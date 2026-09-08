"""Deny-only version routing. No execution service is imported or constructed here."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

V3_TABLES = (
    "program_source_dispatches_v3",
    "program_source_continuation_heads_v3",
    "program_source_continuation_receipts_v3",
    "program_source_continuation_requests_v3",
)
GUARD_TABLE = "uca_source_dispatch_tasks_v3_guard"
REGISTRY = "uca_source_dispatch_tasks_v3"


def table(connection, name, alias="main"):
    row = connection.execute(
        f"SELECT type FROM {alias}.sqlite_master WHERE name=?", (name,)
    ).fetchone()
    if row is not None and row[0] != "table":
        raise ValueError("invalid source dispatch table")
    return row is not None


def program_has_v3(
    connection,
    *,
    program_id=None,
    task_id=None,
    thread_id=None,
    operation_id=None,
    active_only=False,
):
    """Surviving partial history is a denial, never evidence of legacy eligibility."""
    present = [table(connection, name) for name in V3_TABLES]
    if any(present) and not all(present):
        raise ValueError("incomplete v3 history; explicit diagnosis required")
    if not any(present):
        return False
    for name in V3_TABLES[1:]:
        if connection.execute(
            f"SELECT 1 FROM {name} h WHERE NOT EXISTS (SELECT 1 FROM {V3_TABLES[0]} d "
            "WHERE d.operation_id=h.operation_id) LIMIT 1"
        ).fetchone():
            raise ValueError("partial v3 history; explicit diagnosis required")
    clauses, args = [], []
    for key, value in (
        ("program_id", program_id),
        ("task_id", task_id),
        ("thread_id", thread_id),
        ("operation_id", operation_id),
    ):
        if value is not None:
            clauses.append(key + "=?")
            args.append(value)
    if not clauses:
        raise ValueError("source route requires an exact identity")
    where = " OR ".join(clauses)
    rows = connection.execute(
        f"SELECT operation_id FROM {V3_TABLES[0]} WHERE {where} LIMIT 101", args
    ).fetchall()
    if len(rows) > 100:
        raise ValueError("source route exceeds its bound")
    # Heads, receipts and requests independently retain Program/operation identity.
    history_clauses, history_args = [], []
    for key, value in (("program_id", program_id), ("operation_id", operation_id)):
        if value is not None:
            history_clauses.append(key + "=?")
            history_args.append(value)
    if history_clauses:
        history_where = " OR ".join(history_clauses)
        for name in V3_TABLES[1:]:
            found = connection.execute(
                f"SELECT operation_id FROM {name} WHERE {history_where} LIMIT 101",
                history_args,
            ).fetchall()
            if len(found) > 100:
                raise ValueError("source route exceeds its bound")
            if any(row[0] not in {r[0] for r in rows} for row in found):
                raise ValueError("partial v3 history; explicit diagnosis required")
    if not active_only:
        return bool(rows)
    for row in rows:
        head = connection.execute(
            f"SELECT state,receipt_sha256,invocation_state,epoch FROM {V3_TABLES[1]} "
            "WHERE operation_id=?",
            (row[0],),
        ).fetchone()
        if head is None or head[0] != "closed":
            return True
        receipt = connection.execute(
            f"SELECT 1 FROM {V3_TABLES[2]} WHERE operation_id=? AND receipt_sha256=?",
            (row[0], head[1]),
        ).fetchone()
        if receipt is None:
            raise ValueError("partial closed v3 history")
        from universal_coding_agent.product.program_continuation_execution_store import Reader

        reader = Reader(connection)
        current = reader.record(head[1], "uca-program-continuation-receipt-3")
        reader.receipt(head[1], current["program_id"])
        if current["state"] != "closed" or head[2] != "revoked" or head[3] != current["epoch"]:
            raise ValueError("v3 closure is not a consistent recorded result")
    return False


def require_no_v3(connection, **identity):
    if program_has_v3(connection, **identity):
        raise ValueError("v3 source execution requires its explicit continuation consumer")


def registry_has_task(connection, thread_id, task_id=None, *, alias="main"):
    if not table(connection, REGISTRY, alias):
        return False
    return (
        connection.execute(
            f"SELECT 1 FROM {alias}.{REGISTRY} WHERE thread_id=? OR task_id=? LIMIT 1",
            (thread_id, task_id or ""),
        ).fetchone()
        is not None
    )


def safe_v3_route(safe, thread_id, task_id=None):
    """Check the permanent root marker as well as the per-task guard and registries.

    The root marker allows a raw Safe instance to find surviving Program evidence
    even if the task's guard and control registry were independently damaged.
    Missing root marker in an initialized namespace fails closed for the root.
    """
    guarded = registry_has_task(safe.control.connection, thread_id, task_id)
    if not table(safe.connection, GUARD_TABLE):
        if guarded or table(safe.control.connection, REGISTRY):
            raise ValueError("v3 checkpoint guard is missing")
        return False
    row = safe.connection.execute(
        f"SELECT length(content),typeof(content) FROM {GUARD_TABLE} WHERE guard_key='root'"
    ).fetchone()
    if row is None or row[1] != "blob" or not 0 < row[0] <= 65536:
        raise ValueError("v3 checkpoint root binding is missing or invalid")
    raw = safe.connection.execute(
        f"SELECT content FROM {GUARD_TABLE} WHERE guard_key='root'"
    ).fetchone()[0]
    # Import only the standard-library record reader, never the execution consumer.
    from universal_coding_agent.product.program_continuation_execution_store import parse_record

    root = parse_record(raw, "uca-program-source-dispatch-root-3")
    safe.verify_source_dispatch_control(required=True)
    path, device, inode = root["program_store"]
    path = Path(path)
    info = path.stat()
    if (info.st_dev, info.st_ino) != (device, inode):
        raise ValueError("v3 Program store identity changed")
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0.5)) as db:
        db.execute("PRAGMA query_only=ON")
        db.set_progress_handler(lambda: 1, 2_000_000)
        guarded |= program_has_v3(db, task_id=task_id, thread_id=thread_id)
    guarded |= (
        safe.connection.execute(
            f"SELECT 1 FROM {GUARD_TABLE} WHERE guard_key!='root' "
            "AND (task_id=? OR thread_id=?) LIMIT 1",
            (task_id or "", thread_id),
        ).fetchone()
        is not None
    )
    return guarded
