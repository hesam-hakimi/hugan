"""Deny-only version routing. No execution service is imported or constructed here."""

from __future__ import annotations

import json
import os
import sqlite3
import stat
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
LOCATOR = "source-dispatch-v3-root.json"


def read_root_locator(safe):
    """Read one bounded immutable routing hint, never construct an execution object."""
    path = safe.artifacts.root.parent / LOCATOR
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    try:
        before = os.fstat(fd)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or not 0 < before.st_size <= 65536
        ):
            raise ValueError("invalid v3 root locator")
        raw = os.read(fd, 65537)
        after = os.fstat(fd)
        current = path.stat(follow_symlinks=False)

        def stamp(s):
            return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns

        if (
            len(raw) != before.st_size
            or stamp(before) != stamp(after)
            or stamp(after) != stamp(current)
        ):
            raise ValueError("v3 root locator changed during read")
    finally:
        os.close(fd)
    from universal_coding_agent.product.program_continuation_execution_store import parse_record

    return parse_record(raw, "uca-program-source-dispatch-root-3")


def task_has_source_marker(task, *, local_only=False):
    """Recognize source affinity without interpreting a version as authority."""
    if task is None:
        return False
    if type(task) is not dict:
        raise ValueError("invalid checkpoint routing task")
    metadata, evidence = task.get("metadata", {}), task.get("context_evidence", [])
    if type(metadata) is not dict or type(evidence) is not list:
        raise ValueError("invalid checkpoint routing metadata")
    # These are reserved admission markers. Unknown, absent-value or rewritten
    # versions remain denial evidence; equality with the known version is not
    # required. C2's actual adapter/registry checks still decide its own entry.
    local = any(key.startswith("local_product_") for key in metadata)
    if local_only:
        return local
    marked = local or bool({"execution_schema", "admission_sha256"} & metadata.keys())
    for item in evidence:
        if type(item) is not dict or type(item.get("context_type")) is not str:
            raise ValueError("invalid checkpoint routing evidence")
        marked |= item["context_type"].startswith("accepted_source_lineage_")
    return marked


def checkpoint_has_source_marker(safe, thread_id, *, local_only=False):
    """Bounded plain-data denial evidence, including corrupt version metadata."""
    if not table(safe.connection, "checkpoints"):
        return False
    args = (thread_id,)
    where = " WHERE thread_id=? AND checkpoint_ns='' ORDER BY checkpoint_id DESC LIMIT 1"
    header = safe.connection.execute(
        "SELECT substr(checkpoint_id,1,129),length(checkpoint),typeof(checkpoint),"
        "substr(type,1,129),length(type),length(checkpoint_id) "
        "FROM checkpoints" + where,
        args,
    ).fetchone()
    if header is None:
        return False
    checkpoint_id, size, kind, encoding, type_size, id_size = header
    if (
        kind != "blob"
        or not 0 < size <= 16_000_000
        or type(encoding) is not str
        or not 0 < type_size <= 128
        or type(checkpoint_id) is not str
        or not 0 < id_size <= 128
    ):
        raise ValueError("checkpoint routing byte bound exceeded")
    row = safe.connection.execute(
        "SELECT substr(checkpoint,1,16000001) FROM checkpoints WHERE thread_id=? "
        "AND checkpoint_ns='' AND checkpoint_id=? AND type=? "
        "AND typeof(checkpoint)='blob' AND length(checkpoint)=?",
        (thread_id, checkpoint_id, encoding, size),
    ).fetchone()
    if row is None or type(row[0]) is not bytes or len(row[0]) != size:
        raise ValueError("checkpoint routing changed or exceeded its byte bound")
    raw = row[0]
    if encoding == "msgpack":
        import ormsgpack

        def unsupported_extension(_code, _data):
            raise ValueError("unsupported checkpoint routing extension")

        value = ormsgpack.unpackb(raw, ext_hook=unsupported_extension)
    elif encoding == "json":
        value = json.loads(raw)
    else:
        raise ValueError("unsupported checkpoint routing encoding")
    if type(value) is not dict or type(value.get("channel_values")) is not dict:
        raise ValueError("invalid checkpoint routing channels")
    return task_has_source_marker(value["channel_values"].get("task"), local_only=local_only)


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
    locator = read_root_locator(safe)
    if not table(safe.connection, GUARD_TABLE):
        if guarded or locator is not None or table(safe.control.connection, REGISTRY):
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
    if root != locator:
        raise ValueError("v3 root locator is missing or differs")
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
