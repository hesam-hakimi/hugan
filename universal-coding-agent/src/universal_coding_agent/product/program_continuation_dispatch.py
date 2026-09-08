"""Explicit v3 admission, live quiescence and one fresh-worker scope continuation.

This is a trusted Python host consumer. It has no Product/API/CLI wiring and
never accepts source, refreshes a proposal, reconstructs a ticket or schedules work.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

from universal_coding_agent.core.safe_models import SafeTaskRequest
from universal_coding_agent.product.models import PhaseResult, ProgramExecutionBinding
from universal_coding_agent.product.program_continuation_execution_store import (
    DISPATCH,
    FLAGS,
    HEADS,
    PREFIX,
    RECEIPTS,
    REQUESTS,
    ContinuationExecutionStore,
    Reader,
    _request,
    bounded_json,
    canonical,
    closed_foundation,
    digest,
    durable,
    identifier,
    integer,
    locked,
    parse_record,
    request_result,
    require,
    sha,
    status,
)
from universal_coding_agent.product.program_source_evidence import (
    _capture_at_owned_destination,
    strict_json,
)
from universal_coding_agent.product.program_source_routing import (
    GUARD_TABLE,
    REGISTRY,
    table,
)
from universal_coding_agent.product.program_source_transitions import (
    _canonical,
    _hash,
    _require,
)
from universal_coding_agent.providers.base import (
    RemoteOperationLeaseAwareProvider,
    RestartReconciliationModelProvider,
)
from universal_coding_agent.safe.testing import SafeTestRunner


def _protocol():
    value = os.environ.get("UCA_SAFE_EDIT_PROTOCOL", "v1").strip().lower()
    if value in {"v2", "v2-line-addressed", "line-addressed"}:
        return "v2-line-addressed"
    require(value == "v1", "unsupported v3 Safe edit protocol")
    return value


class ProgramContinuationDispatchService:
    def __init__(self, preparation, provider, *, lifecycle, transport_id):
        identifier(transport_id)
        self.preparation, self.store, self.provider = preparation, preparation.acceptance, provider
        self.lifecycle, self.transport_id = lifecycle, transport_id
        self.db = ContinuationExecutionStore(self.store, lifecycle)
        self._live = {}
        self._provider = provider
        self._host_bytes = self._host()
        self.host_sha256 = sha(self._host_bytes)

    def _host(self):
        require(
            not isinstance(
                self.provider,
                (RemoteOperationLeaseAwareProvider, RestartReconciliationModelProvider),
            ),
            "v3 requires a synchronous transport without retained remote leases",
        )
        runner = SafeTestRunner.from_environment()
        # The first consumer uses the built-in synchronous subprocess runner.
        # Qualified pausable handles retain their ordinary legacy configuration.
        require(runner.adapter_module_path is None, "v3 test transport must return synchronously")
        return canonical(
            {
                "schema": "uca-program-continuation-host-3",
                "stores": self.db.identities,
                "preparation_host_sha256": self.preparation.host_sha256,
                "transport_id": self.transport_id,
                "provider_type": type(self.provider).__module__
                + "."
                + type(self.provider).__qualname__,
                "policy": self.store.trusted_policy.model_dump(mode="json"),
                "edit_protocol": _protocol(),
                "publication_enabled": False,
            }
        )

    def _host_gate(self):
        require(
            self.provider is self._provider and self._host() == self._host_bytes,
            "v3 host, policy or transport changed",
        )
        self.db.pins()

    def _put_record(self, value):
        raw = canonical(value)
        parse_record(raw, value["schema"])
        return self.store._put(raw)

    def _json(self, value):
        return strict_json(self.store._get(value))

    def _record_json(self, value, schema):
        return Reader(self.store.connection).record(value, schema)

    def status(self, program_id, operation_id, *, after_sequence=0, limit=20):
        return status(
            self.store.programs.database_path,
            program_id,
            operation_id,
            after_sequence=after_sequence,
            limit=limit,
        )

    def request_result(self, program_id, request_id):
        return request_result(self.store.programs.database_path, program_id, request_id)

    def _row(self, operation_id):
        require(
            type(operation_id) is str
            and len(operation_id) == 32
            and all(c in "0123456789abcdef" for c in operation_id),
            "invalid v3 operation",
        )
        fields = (
            "operation_id",
            "program_id",
            "phase_id",
            "task_id",
            "thread_id",
            "admission_sha256",
            "host_sha256",
            "preparation_receipt_sha256",
            "guard_sha256",
        )
        reader = Reader(self.store.connection)
        rows = reader.rows(DISPATCH, fields, "operation_id=?", (operation_id,), limit=1)
        require(
            len(rows) == 1 and rows[0]["host_sha256"] == self.host_sha256,
            "v3 admission is missing or host changed",
        )
        columns = (
            "operation_id",
            "program_id",
            "epoch",
            "state",
            "sequence",
            "receipt_sha256",
            "authority_sha256",
            "filesystem_sha256",
            "retained_sha256",
            "task_sha256",
            "discovery_sha256",
            "decision_sha256",
            "checkpoint_sha256",
            "result_sha256",
            "proposal_sha256",
            "settlement_sha256",
            "invocation_sha256",
            "invocation_state",
            "invocation_action",
            "request_id",
            "revision",
        )
        heads = reader.rows(HEADS, columns, "operation_id=?", (operation_id,), limit=1)
        require(
            len(heads) == 1 and heads[0]["program_id"] == rows[0]["program_id"],
            "v3 continuation head is missing or inconsistent",
        )
        return {**rows[0], **heads[0], "approval_sha256": heads[0]["decision_sha256"]}

    def _admission(self, row):
        saved = self._record_json(row["admission_sha256"], "uca-program-source-dispatch-3")
        intent = saved["intent"]
        require(
            all(
                intent[key] == row[key]
                for key in (
                    "operation_id",
                    "program_id",
                    "phase_id",
                    "task_id",
                    "thread_id",
                    "host_sha256",
                    "preparation_receipt_sha256",
                )
            )
            and saved["guard_sha256"] == row["guard_sha256"],
            "v3 admission rows differ",
        )
        return intent

    def _remote_absence(self, admission):
        db = self.store.connection
        task, thread = admission["task_id"], admission["thread_id"]
        require(
            db.execute(
                "SELECT 1 FROM remote.remote_operation_leases "
                "WHERE task_id=? OR thread_id=? LIMIT 1",
                (task, thread),
            ).fetchone()
            is None
            and db.execute(
                "SELECT 1 FROM remote.remote_operation_lease_retirements WHERE task_id=? LIMIT 1",
                (task,),
            ).fetchone()
            is None,
            "v3 cannot settle a retained or retired remote operation",
        )
        return sha(
            canonical(
                {
                    "store": self.db.identities[3],
                    "task_id": task,
                    "thread_id": thread,
                    "leases": [],
                    "retirements": [],
                }
            )
        )

    def _legacy_collision(self, intent):
        db = self.store.connection
        for alias, name in (
            ("control", "uca_source_dispatch_tasks"),
            ("main", "program_source_dispatches"),
        ):
            if not table(db, name, alias):
                continue
            where = "task_id=?"
            args = [intent["task_id"]]
            if alias == "control":
                where += " OR thread_id=?"
                args.append(intent["thread_id"])
            else:
                where += " OR operation_id=?"
                args.append(intent["operation_id"])
            require(
                db.execute(f"SELECT 1 FROM {alias}.{name} WHERE {where} LIMIT 1", args).fetchone()
                is None,
                "cross-version source admission collision",
            )
        present = [
            table(db, name)
            for name in (
                "program_continuation_heads",
                "program_continuation_receipts",
                "program_continuation_requests",
            )
        ]
        require(not any(present) or all(present), "partial d2a history blocks v3")
        if all(present):
            closed_foundation(db, intent["program_id"])

    def _witness(self, admission, owner_token):
        """Full current semantic witness; owner is checked separately by the accepted CAS API."""
        db, program = self.store.connection, admission["program_id"]
        reader = Reader(db)
        program_rows = reader.rows(
            "programs",
            ("program_id", "status", "requirement_hash", "plan_hash", "plan_ref"),
            "program_id=?",
            (program,),
            limit=1,
        )
        require(len(program_rows) == 1, "v3 Program is missing")
        phases = reader.rows(
            "program_phases",
            ("program_id", "phase_id", "status", "result_ref", "summary_ref"),
            "program_id=?",
            (program,),
            order="phase_id",
        )
        executions = reader.rows(
            "program_executions",
            (
                "program_id",
                "phase_id",
                "unit_key",
                "slice_id",
                "task_id",
                "thread_id",
                "requirement_hash",
                "status",
                "safe_status",
                "result_ref",
                "phase_report_ref",
                "error_ref",
                "accepted_evidence_ref",
                "accepted_evidence_hash",
                "expected_base_sha",
                "remote_disposition_ref",
            ),
            "program_id=?",
            (program,),
            order="task_id",
        )
        tasks = tuple(sorted({admission["task_id"], *(r["task_id"] for r in executions)}))
        clause = ",".join("?" for _ in tasks)
        controls = reader.rows(
            "control.control_state",
            ("entity_type", "entity_id", "state", "reason", "revision"),
            f"(entity_type='program' AND entity_id=?) "
            f"OR (entity_type='task' AND entity_id IN ({clause}))",
            (program, *tasks),
            order="entity_type,entity_id",
            limit=101,
        )
        source = reader.rows(
            "program_source_heads",
            (
                "program_id",
                "generation",
                "source_sha256",
                "host_sha256",
                "initial_receipt_sha256",
                "receipt_sha256",
            ),
            "program_id=?",
            (program,),
            limit=1,
        )
        recovery = reader.rows(
            "lifecycle.lifecycle_recovery_receipts",
            (
                "recovery_ref",
                "target_type",
                "target_kind",
                "scope_id",
                "task_id",
                "program_id",
                "created_at",
                "reason",
                "recovered_at",
                "audit_ref",
                "confirmed_by_operator",
                "rows_recovered",
            ),
            f"program_id=? OR task_id IN ({clause})",
            (program, *tasks),
            order="recovery_ref",
        )
        owner = self.lifecycle.check_program_worker_in_transaction(
            db, program, task_ids=tasks, owner_token=owner_token
        )
        return (
            {
                "program": program_rows[0],
                "phases": phases,
                "executions": executions,
                "controls": controls,
                "source": source,
                "recovery": recovery,
                "lifecycle_exclusions": [],
            },
            sha(canonical(owner)) if owner else None,
            tasks,
        )

    def _authority_record(self, row, admission, owner_token):
        witness, owner, _ = self._witness(admission, owner_token)
        bounded_json(canonical(witness))
        return {
            "schema": PREFIX + "authority-3",
            "admission_sha256": row["admission_sha256"],
            "epoch": row["epoch"],
            "state": row["state"],
            "predecessor_sha256": row["receipt_sha256"],
            "witness_sha256": self.store._put(canonical(witness)),
            "owner_sha256": owner,
            "filesystem_sha256": row["filesystem_sha256"],
            "retained_sha256": row["retained_sha256"],
        }

    def _refresh_authority(self, operation_id, owner_token):
        row = self._row(operation_id)
        authority = self._authority_record(row, self._admission(row), owner_token)
        self.store.connection.execute(
            f"UPDATE {HEADS} SET authority_sha256=? WHERE operation_id=?",
            (self._put_record(authority), operation_id),
        )
        return authority

    def _load(self, operation_id, owner_token, *, after_finalize=False):
        self._host_gate()
        row = self._row(operation_id)
        admission = self._admission(row)
        reader = Reader(self.store.connection)
        receipt = reader.receipt(row["receipt_sha256"], row["program_id"])
        require(
            receipt["operation_id"] == operation_id
            and receipt["sequence"] == row["sequence"]
            and receipt["admission_sha256"] == row["admission_sha256"],
            "v3 head history differs",
        )
        completed = _request(reader, row["program_id"], receipt["request_id"])
        require(
            completed and completed["status"] == "completed", "v3 predecessor request is missing"
        )
        self._legacy_collision(admission)
        self._verify_guard(admission, row["guard_sha256"])
        registry = self.store.connection.execute(
            f"SELECT * FROM control.{REGISTRY} WHERE task_id=?", (admission["task_id"],)
        ).fetchone()
        require(
            registry is not None
            and dict(registry)
            == {
                key: row[key] for key in ("task_id", "thread_id", "admission_sha256", "host_sha256")
            },
            "v3 registry differs",
        )
        before = self.store.source.load_snapshot(
            self.store._get(admission["source_sha256"]), expected_sha256=admission["source_sha256"]
        )
        self.store._plan(before.identity)
        require(
            before.identity.requirement_sha256 == admission["requirement_sha256"]
            and before.identity.plan_sha256 == admission["plan_sha256"],
            "v3 plan identity differs",
        )
        expected = self._record_json(row["authority_sha256"], PREFIX + "authority-3")
        witness, owner, _ = self._witness(admission, owner_token)
        old_witness = bounded_json(self.store._get(expected["witness_sha256"]))
        if after_finalize:
            for control in old_witness["controls"]:
                if control["entity_type"] == "task" and control["entity_id"] == row["task_id"]:
                    require(control["state"] == "running", "unexpected pre-finalizer control")
                    control.update(state="completed", reason="", revision=control["revision"] + 1)
        require(
            witness == old_witness
            and expected
            == {
                **expected,
                "admission_sha256": row["admission_sha256"],
                "epoch": row["epoch"],
                "state": row["state"],
                "predecessor_sha256": row["receipt_sha256"],
                "owner_sha256": owner,
                "filesystem_sha256": row["filesystem_sha256"],
                "retained_sha256": row["retained_sha256"],
            },
            "v3 current authority changed",
        )
        require(
            witness["source"][0]["source_sha256"] == admission["source_sha256"]
            and witness["source"][0]["generation"] == admission["generation"]
            and witness["source"][0]["receipt_sha256"] == admission["acceptance_receipt_sha256"],
            "v3 accepted source changed",
        )
        require(
            self._lineage(admission, before) == self.store._get(admission["dependency_sha256"]),
            "v3 dependency evidence changed",
        )
        if row["discovery_sha256"]:
            for item in self._json(row["discovery_sha256"]):
                self.store.safe.artifacts.read_bytes_bounded_verified(
                    item["ref"], expected_sha256=item["sha256"], max_bytes=2_000_000
                )
        self._remote_absence(admission)
        return row, admission, before

    def _state(self, operation_id, old, new, *, owner_token, **fields):
        allowed = {
            "task_sha256",
            "discovery_sha256",
            "decision_sha256",
            "checkpoint_sha256",
            "result_sha256",
            "proposal_sha256",
            "settlement_sha256",
            "invocation_sha256",
            "invocation_state",
            "invocation_action",
            "request_id",
            "epoch",
        }
        require(set(fields) <= allowed, "invalid v3 state assignment")
        assignments = ",".join(("state=?", "revision=revision+1", *(k + "=?" for k in fields)))
        count = self.store.connection.execute(
            f"UPDATE {HEADS} SET {assignments} WHERE operation_id=? AND state=?",
            (new, *fields.values(), operation_id, old),
        ).rowcount
        require(count == 1, "v3 state CAS differs")
        self._refresh_authority(operation_id, owner_token)

    def _payload(
        self,
        action,
        program_id,
        operation_id,
        request_id,
        *,
        admission_sha256=None,
        expected_state="absent",
        expected_epoch=0,
        expected_receipt_sha256=None,
        proposal_sha256=None,
        scope_sha256=None,
        approval_id=None,
        approved=None,
        preparation_receipt_sha256=None,
    ):
        for value in (program_id, operation_id, request_id):
            identifier(value)
        integer(expected_epoch)
        payload = {
            "schema": PREFIX + "request-3",
            "host_sha256": self.host_sha256,
            "operation_id": operation_id,
            "program_id": program_id,
            "request_id": request_id,
            "action": action,
            "admission_sha256": admission_sha256,
            "expected_state": expected_state,
            "expected_epoch": expected_epoch,
            "expected_receipt_sha256": expected_receipt_sha256,
            "proposal_sha256": proposal_sha256,
            "scope_sha256": scope_sha256,
            "approval_id": approval_id,
            "approved": approved,
            "preparation_receipt_sha256": preparation_receipt_sha256,
        }
        parse_record(canonical(payload), payload["schema"])
        return payload

    def _request(self, payload, *, admit=False):
        reader, db = Reader(self.store.connection), self.store.connection
        prior = _request(reader, payload["program_id"], payload["request_id"])
        payload_sha = sha(canonical(payload))
        if prior:
            require(prior["payload_sha256"] == payload_sha, "v3 request ID content differs")
            if prior["status"] == "completed":
                return prior["response"]
            if not admit:
                return {
                    "program_id": payload["program_id"],
                    "request_id": payload["request_id"],
                    "request_status": "pending",
                    "blockers": ["recovery_required"],
                    **FLAGS,
                }
            return None
        db.execute(
            f"INSERT INTO {REQUESTS} VALUES (?,?,?,?,?,?,'pending',NULL)",
            (
                self.host_sha256,
                payload["program_id"],
                payload["request_id"],
                payload["operation_id"],
                payload["action"],
                self._put_record(payload),
            ),
        )
        return None

    def _preparation_intent(self, program_id, operation_id, receipt_sha, owner_token):
        receipt = self.preparation._finish_locked(
            operation_id, owner_token, self.preparation.filesystem.deadline(), allow_fill=False
        )
        require(
            sha(canonical(receipt)) == receipt_sha and receipt["program_id"] == program_id,
            "v3 exact pending preparation differs",
        )
        before = self.store.current(program_id)
        binding = self.store._binding(before.identity, owner_token)
        require(
            binding["program"]["status"] == binding["program_control"]["state"] == "running",
            "v3 admission requires a running Program",
        )
        context = self._lineage(receipt, before)
        ref = self.store.programs.artifacts.write_text(
            f"programs/{program_id}/source-dispatch/{operation_id}/lineage-v3-{sha(context)}.json",
            context.decode(),
            "application/json",
        )
        intent = {
            "schema": "uca-program-source-dispatch-intent-3",
            "operation_id": operation_id,
            "host_sha256": self.host_sha256,
            "preparation_receipt_sha256": receipt_sha,
            "preparation_row": dict(self.preparation._row(operation_id)),
            "materialization_row": dict(
                self.preparation.materialization._row(receipt["materialization_id"])
            ),
            "owner_binding_sha256": binding["owner_binding_sha256"],
            "edit_protocol": _protocol(),
            "dependency_ref": ref.uri,
            "dependency_sha256": self.store._put(context),
            "requirement_sha256": before.identity.requirement_sha256,
            "plan_sha256": before.identity.plan_sha256,
            "policy_sha256": sha(canonical(self.store.trusted_policy.model_dump(mode="json"))),
            "transport_id": self.transport_id,
            **{
                key: receipt[key]
                for key in (
                    "program_id",
                    "phase_id",
                    "task_id",
                    "thread_id",
                    "generation",
                    "source_sha256",
                    "acceptance_receipt_sha256",
                    "materialization_id",
                    "materialization_receipt_sha256",
                    "origin_repository_url",
                    "origin_repository_sha256",
                    "origin_base_sha",
                    "origin_tree_sha",
                    "derived_git_commit_sha",
                    "derived_git_tree_sha",
                    "object_format",
                )
            },
        }
        self._legacy_collision(intent)
        self._remote_absence(intent)
        self._witness(intent, owner_token)
        parse_record(canonical(intent), intent["schema"])
        return intent, receipt

    def _guard(self, intent):
        return {
            "schema": "uca-program-source-dispatch-guard-3",
            "intent_sha256": sha(canonical(intent)),
            **{
                key: intent[key]
                for key in ("operation_id", "program_id", "task_id", "thread_id", "host_sha256")
            },
        }

    def _persist_guard(self, intent):
        safe = self.store.safe
        with (
            locked(self.store.programs._lock),
            locked(safe.control._lock),
            locked(self.store._lock),
        ):
            self._host_gate()
            durable(safe.connection, ("main",), rollback=False)
            root = {
                "schema": "uca-program-source-dispatch-root-3",
                "host_sha256": self.host_sha256,
                "program_store": self.db.identities[0],
                "control_store": self.db.identities[1],
            }
            guard = self._guard(intent)
            self.db.boundary("before_guard")
            self.db.persist_locator(root)
            self.db.boundary("after_root_locator")
            with self.db.guard_transaction():
                # This separate immutable root write is not an admission. Keep
                # the accepted c2 binding bytes, without calling its committing API.
                safe.connection.execute(
                    "INSERT OR IGNORE INTO uca_source_dispatch_control VALUES (1, ?, ?, ?)",
                    safe._source_dispatch_control_identity(),
                )
                safe.verify_source_dispatch_control(required=True)
                for key, task, thread, record in (
                    ("root", "", "", root),
                    (intent["operation_id"], intent["task_id"], intent["thread_id"], guard),
                ):
                    raw = canonical(record)
                    parse_record(raw, record["schema"])
                    safe.connection.execute(
                        f"INSERT OR IGNORE INTO {GUARD_TABLE} VALUES (?,?,?,?)",
                        (key, task, thread, raw),
                    )
                    saved = safe.connection.execute(
                        f"SELECT content FROM {GUARD_TABLE} WHERE guard_key=?", (key,)
                    ).fetchone()
                    require(saved is not None and saved[0] == raw, "v3 immutable guard differs")
            self.db.boundary("after_guard")
            return sha(canonical(guard))

    def _verify_guard(self, intent, expected):
        from universal_coding_agent.product.program_source_routing import read_root_locator
        require(read_root_locator(self.store.safe) == {
            "schema": "uca-program-source-dispatch-root-3", "host_sha256": self.host_sha256,
            "program_store": self.db.identities[0], "control_store": self.db.identities[1]},
            "v3 immutable root locator differs")
        self.store.safe.verify_source_dispatch_control(required=True)
        for key, record in (
            (
                "root",
                {
                    "schema": "uca-program-source-dispatch-root-3",
                    "host_sha256": self.host_sha256,
                    "program_store": self.db.identities[0],
                    "control_store": self.db.identities[1],
                },
            ),
            (intent["operation_id"], self._guard(intent)),
        ):
            size = self.store.connection.execute(
                f"SELECT length(content) FROM safe.{GUARD_TABLE} WHERE guard_key=?", (key,)
            ).fetchone()
            raw = canonical(record)
            require(size is not None and size[0] == len(raw), "v3 checkpoint guard is missing")
            found = self.store.connection.execute(
                f"SELECT content FROM safe.{GUARD_TABLE} WHERE guard_key=?", (key,)
            ).fetchone()[0]
            require(found == raw, "v3 checkpoint guard differs")
        require(expected == sha(canonical(self._guard(intent))), "v3 guard digest differs")

    def admit(
        self, program_id, operation_id, *, request_id, preparation_receipt_sha256, owner_token
    ):
        digest(preparation_receipt_sha256)
        payload = self._payload(
            "admit",
            program_id,
            operation_id,
            request_id,
            preparation_receipt_sha256=preparation_receipt_sha256,
        )
        self._host_gate()
        self.db.initialize()
        with self.db.transaction():
            replay = self._request(payload, admit=True)
            if replay is not None:
                return replay
            intent, _ = self._preparation_intent(
                program_id, operation_id, preparation_receipt_sha256, owner_token
            )
            require(
                self.store.connection.execute(
                    f"SELECT 1 FROM {HEADS} WHERE program_id=? AND state!='closed'", (program_id,)
                ).fetchone()
                is None,
                "another v3 operation is active",
            )
        guard_sha = self._persist_guard(intent)
        with self.db.transaction():
            replay = self._request(payload, admit=True)
            if replay is not None:
                return replay
            current, receipt = self._preparation_intent(
                program_id, operation_id, preparation_receipt_sha256, owner_token
            )
            require(current == intent, "v3 pending admission changed before consumption")
            self._verify_guard(intent, guard_sha)
            db = self.store.connection
            require(
                db.execute(
                    "SELECT 1 FROM safe.checkpoints WHERE thread_id=? LIMIT 1",
                    (intent["thread_id"],),
                ).fetchone()
                is None,
                "v3 task already has a checkpoint",
            )
            admission_sha = self._put_record(
                {
                    "schema": "uca-program-source-dispatch-3",
                    "intent": intent,
                    "intent_sha256": sha(canonical(intent)),
                    "guard_sha256": guard_sha,
                }
            )
            db.execute(
                f"INSERT INTO {DISPATCH} VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    operation_id,
                    program_id,
                    intent["phase_id"],
                    intent["task_id"],
                    intent["thread_id"],
                    admission_sha,
                    self.host_sha256,
                    preparation_receipt_sha256,
                    guard_sha,
                ),
            )
            db.execute(
                """INSERT INTO program_executions
                (program_id,phase_id,unit_key,task_id,thread_id,requirement_hash,status,expected_base_sha)
                VALUES (?,?,'__phase__',?,?,?,'starting',?)""",
                (
                    program_id,
                    intent["phase_id"],
                    intent["task_id"],
                    intent["thread_id"],
                    intent["requirement_sha256"],
                    intent["derived_git_commit_sha"],
                ),
            )
            require(
                db.execute(
                    "UPDATE program_phases SET status='running' WHERE program_id=? "
                    "AND phase_id=? AND status='pending'",
                    (program_id, intent["phase_id"]),
                ).rowcount
                == 1,
                "v3 pending phase CAS differs",
            )
            db.execute(
                "INSERT INTO control.control_state VALUES ('task',?,'running','',0)",
                (intent["task_id"],),
            )
            db.execute(
                f"INSERT INTO control.{REGISTRY} VALUES (?,?,?,?)",
                (intent["task_id"], intent["thread_id"], admission_sha, self.host_sha256),
            )
            db.execute(
                f"""INSERT INTO {HEADS}
                (operation_id,program_id,epoch,state,sequence,authority_sha256,filesystem_sha256,
                 retained_sha256,revision) VALUES (?,?,0,'admitted',0,?,?,?,0)""",
                (
                    operation_id,
                    program_id,
                    admission_sha,
                    receipt["filesystem_sha256"],
                    intent["source_sha256"],
                ),
            )
            self.db.boundary("after_admission")
            result = self._complete(payload, owner_token, state="admitted")
        return result

    def _expected(self, row, payload):
        require(
            row["program_id"] == payload["program_id"]
            and row["admission_sha256"] == payload["admission_sha256"]
            and row["epoch"] == payload["expected_epoch"]
            and row["receipt_sha256"] == payload["expected_receipt_sha256"]
            and row["state"] == payload["expected_state"],
            "v3 exact state/epoch/receipt changed",
        )

    def dispatch(
        self,
        program_id,
        operation_id,
        *,
        request_id,
        admission_sha256,
        expected_epoch,
        expected_receipt_sha256,
        owner_token,
    ):
        payload = self._payload(
            "dispatch",
            program_id,
            operation_id,
            request_id,
            admission_sha256=admission_sha256,
            expected_state="admitted",
            expected_epoch=expected_epoch,
            expected_receipt_sha256=expected_receipt_sha256,
        )
        from universal_coding_agent.product.program_continuation_execution_adapter import (
            ContinuationSafeExecution,
        )

        adapter = None
        try:
            with self.db.transaction():
                replay = self._request(payload)
                if replay is not None:
                    return replay
                row, admission, _ = self._load(operation_id, owner_token)
                self._expected(row, payload)
                self._verify_files(row, admission)
                adapter = ContinuationSafeExecution(self, operation_id, owner_token, payload)
                self._state(
                    operation_id,
                    "admitted",
                    "discovery_started",
                    owner_token=owner_token,
                    request_id=request_id,
                    invocation_action="dispatch",
                )
                adapter._arm()
        except BaseException:
            if adapter is not None:
                adapter._discard()
            raise
        self._live[operation_id] = adapter
        return adapter._drive()

    def approve_scope(
        self,
        program_id,
        operation_id,
        *,
        request_id,
        admission_sha256,
        expected_epoch,
        expected_receipt_sha256,
        proposal_sha256,
        scope_sha256,
        approval_id,
        approved,
    ):
        require(type(approved) is bool, "v3 requires an explicit strict boolean scope decision")
        identifier(approval_id)
        for value in (admission_sha256, expected_receipt_sha256, proposal_sha256, scope_sha256):
            digest(value)
        payload = self._payload(
            "approve_scope",
            program_id,
            operation_id,
            request_id,
            admission_sha256=admission_sha256,
            expected_state="parked_scope",
            expected_epoch=expected_epoch,
            expected_receipt_sha256=expected_receipt_sha256,
            proposal_sha256=proposal_sha256,
            scope_sha256=scope_sha256,
            approval_id=approval_id,
            approved=approved,
        )
        from universal_coding_agent.product.program_continuation_execution_adapter import (
            ContinuationSafeExecution,
        )

        adapter = None
        try:
            with self.db.transaction():
                replay = self._request(payload)
                if replay is not None:
                    return replay
                row, admission, _ = self._load(operation_id, None)
                self._expected(row, payload)
                require(
                    row["proposal_sha256"] == proposal_sha256
                    and row["invocation_state"] == "revoked",
                    "v3 proposal or revocation differs",
                )
                proposal = self._record_json(proposal_sha256, PREFIX + "proposal-3")
                require(
                    proposal["parked_receipt_sha256"] == expected_receipt_sha256
                    and proposal["parked_epoch"] == expected_epoch
                    and proposal["scope_sha256"] == scope_sha256
                    and proposal["authority_sha256"] == row["authority_sha256"]
                    and proposal["admission_sha256"] == admission_sha256
                    and proposal["settlement_sha256"] == row["settlement_sha256"]
                    and proposal["next_action"] == "scope_decision",
                    "v3 exact proposal changed",
                )
                self._verify_files(row, admission)
                checkpoint, state, boundary = self._checkpoint(row, admission)
                require(
                    boundary == "scope"
                    and sha(checkpoint) == row["checkpoint_sha256"]
                    and proposal["checkpoint_sha256"] == row["checkpoint_sha256"]
                    and state["scope_hash"] == scope_sha256,
                    "v3 parked checkpoint changed",
                )
                witness, _, tasks = self._witness(admission, None)
                require(
                    sha(canonical(witness)) == proposal["witness_sha256"],
                    "v3 proposal semantic witness changed",
                )
                owner = self.lifecycle.reserve_program_worker_in_transaction(
                    self.store.connection, program_id, task_ids=tasks
                )
                self.db.boundary("after_fresh_worker")
                self._state(
                    operation_id,
                    "parked_scope",
                    "resume_started",
                    owner_token=owner,
                    epoch=expected_epoch + 1,
                    request_id=request_id,
                    invocation_action="approve_scope",
                    proposal_sha256=None,
                )
                fresh = self._row(operation_id)
                decision = {
                    "schema": PREFIX + "scope-decision-3",
                    "request_id": request_id,
                    "proposal_sha256": proposal_sha256,
                    "parked_receipt_sha256": expected_receipt_sha256,
                    "parked_epoch": expected_epoch,
                    "scope_sha256": scope_sha256,
                    "approval_id": approval_id,
                    "approved": approved,
                    "epoch": fresh["epoch"],
                    "authority_sha256": fresh["authority_sha256"],
                }
                self.store.connection.execute(
                    f"UPDATE {HEADS} SET decision_sha256=? WHERE operation_id=?",
                    (self._put_record(decision), operation_id),
                )
                adapter = ContinuationSafeExecution(self, operation_id, owner, payload)
                adapter._arm()
        except BaseException:
            if adapter is not None:
                adapter._discard()
            raise
        self._live[operation_id] = adapter
        return adapter._drive()

    def _checkpoint(self, row, admission):
        """Decode the latest exact root checkpoint and its actual interrupt writes."""
        db, thread = self.store.connection, admission["thread_id"]
        for name in ("checkpoints", "writes"):
            require(
                db.execute(
                    f"SELECT 1 FROM safe.{name} WHERE thread_id=? AND checkpoint_ns!='' LIMIT 1",
                    (thread,),
                ).fetchone()
                is None,
                "v3 checkpoint contains an unsupported namespace",
            )
        sizes = db.execute(
            "SELECT length(checkpoint),length(metadata) FROM safe.checkpoints "
            "WHERE thread_id=? AND checkpoint_ns='' ORDER BY checkpoint_id DESC LIMIT 1",
            (thread,),
        ).fetchone()
        require(
            sizes is not None
            and all(type(n) is int and n >= 0 for n in sizes)
            and sum(sizes) <= 16_000_000,
            "missing or oversized v3 checkpoint",
        )
        headers = db.execute(
            "SELECT length(checkpoint_id),length(parent_checkpoint_id),length(type),"
            "typeof(checkpoint),typeof(metadata) FROM safe.checkpoints "
            "WHERE thread_id=? AND checkpoint_ns='' ORDER BY checkpoint_id DESC LIMIT 1",
            (thread,),
        ).fetchone()
        require(
            all(n is None or type(n) is int and 0 <= n <= 128 for n in headers[:3])
            and headers[3] == headers[4] == "blob",
            "invalid v3 checkpoint header bounds",
        )
        checkpoint = db.execute(
            "SELECT * FROM safe.checkpoints WHERE thread_id=? AND checkpoint_ns='' "
            "ORDER BY checkpoint_id DESC LIMIT 1",
            (thread,),
        ).fetchone()
        require(len(checkpoint["checkpoint_id"].encode()) <= 128, "oversized checkpoint identity")
        args = (thread, checkpoint["checkpoint_id"])
        count, size = db.execute(
            "SELECT count(*),coalesce(sum(length(value)),0) FROM safe.writes "
            "WHERE thread_id=? AND checkpoint_ns='' AND checkpoint_id=?",
            args,
        ).fetchone()
        require(count <= 128 and size <= 16_000_000, "v3 pending write bound exceeded")
        headers = db.execute(
            "SELECT length(task_id),length(channel),length(type),typeof(value) "
            "FROM safe.writes WHERE thread_id=? AND checkpoint_ns='' AND checkpoint_id=?",
            args,
        ).fetchall()
        require(
            all(
                all(type(n) is int and 0 <= n <= 128 for n in h[:3]) and h[3] == "blob"
                for h in headers
            ),
            "invalid v3 pending write header bounds",
        )
        writes = db.execute(
            "SELECT * FROM safe.writes WHERE thread_id=? AND checkpoint_ns='' "
            "AND checkpoint_id=? ORDER BY task_id,idx",
            args,
        ).fetchall()

        # Inspect bytes without object construction before the actual graph decoder.
        # This slice's checkpoint values are plain data; its only extension is the
        # observed LangGraph Interrupt constructor in the scope pending write.
        import ormsgpack

        def plain_extension(code, data):
            raise ValueError("unsupported v3 checkpoint extension")

        def interrupt_extension(code, data):
            value = ormsgpack.unpackb(data, ext_hook=plain_extension)
            require(
                code == 2
                and type(value) is list
                and len(value) == 3
                and value[:2] == ["langgraph.types", "Interrupt"]
                and type(value[2]) is dict
                and value[2].keys() == {"value", "id"}
                and type(value[2]["id"]) is str
                and len(value[2]["id"]) <= 128,
                "unsupported v3 interrupt extension",
            )
            return value[2]

        require(
            checkpoint["type"] == "msgpack" and all(w["type"] == "msgpack" for w in writes),
            "unsupported v3 checkpoint serialization",
        )
        ormsgpack.unpackb(checkpoint["checkpoint"], ext_hook=plain_extension)
        for write in writes:
            ormsgpack.unpackb(write["value"], ext_hook=interrupt_extension)

        def encoded(record):
            return {
                key: base64.b64encode(value).decode() if isinstance(value, bytes) else value
                for key, value in dict(record).items()
            }

        raw = canonical({"checkpoint": encoded(checkpoint), "writes": [encoded(w) for w in writes]})
        require(
            len(raw) <= min(44_000_000, self.store.source.policy.max_artifact_bytes),
            "encoded v3 checkpoint bound exceeded",
        )
        point = self.store.safe.graph.get_state(
            {
                "configurable": {
                    "thread_id": thread,
                    "checkpoint_ns": "",
                    "checkpoint_id": checkpoint["checkpoint_id"],
                }
            }
        )
        require(
            point.config["configurable"]["checkpoint_id"] == checkpoint["checkpoint_id"],
            "decoded checkpoint identity differs",
        )
        state = point.values
        require(state.get("task") == self._json(row["task_sha256"]), "v3 checkpoint task differs")
        task = SafeTaskRequest.model_validate(state["task"])
        destination = str(
            self.preparation.filesystem.root / ("execution-" + row["operation_id"]) / "repo"
        )
        require(
            task.task_id == row["task_id"]
            and task.thread_id == thread
            and state.get("sandbox_path") == destination
            and state.get("base_sha") == admission["derived_git_commit_sha"]
            and state.get("sandbox_id") == row["task_id"]
            and state.get("scope_hash") == task.manifest.canonical_hash()
            and not task.require_publish_approval
            and not state.get("publish_approved"),
            "v3 checkpoint scope/source/publication binding differs",
        )
        if tuple(point.next) == ("scope_approval",):
            require(
                state.get("status") == "awaiting_scope_approval"
                and state.get("scope_approved") is None
                and not state.get("patch_applied")
                and len(point.tasks) == 1
                and len(writes) == 1,
                "v3 scope stop contains unexpected pending work",
            )
            pending, write = point.tasks[0], writes[0]
            require(
                pending.name == "scope_approval"
                and pending.path == ("__pregel_pull", "scope_approval")
                and pending.error is None
                and pending.state is None
                and pending.result is None
                and len(pending.interrupts) == 1
                and write["task_id"] == pending.id
                and write["channel"] == "__interrupt__"
                and write["idx"] == -3,
                "v3 scope interrupt task/write shape differs",
            )
            expected = {
                "type": "safe_scope_approval",
                "task_id": task.task_id,
                "base_sha": task.manifest.base_sha,
                "plan_hash": task.manifest.plan_hash,
                "scope_hash": state["scope_hash"],
                "allowed_changes": [
                    c.model_dump(mode="json") for c in task.manifest.allowed_changes
                ],
                "denied_prefixes": list(task.manifest.denied_prefixes),
                "test_profiles": list(task.manifest.test_profiles),
                "acceptance_criteria": list(task.manifest.acceptance_criteria),
            }
            decoded = self.store.safe.graph.checkpointer.serde.loads_typed(
                (write["type"], write["value"])
            )
            require(
                pending.interrupts[0].value == expected
                and tuple(decoded) == tuple(pending.interrupts),
                "v3 interrupt data differs",
            )
            return raw, state, "scope"
        require(
            not point.next
            and not point.tasks
            and not writes
            and state.get("status") in {"completed", "failed", "blocked"},
            "v3 has no supported returned boundary",
        )
        self._terminal_evidence(row, admission, state)
        return raw, state, "terminal"

    def _terminal_evidence(self, row, admission, state):
        decision = self._record_json(row["decision_sha256"], PREFIX + "scope-decision-3")
        require(
            state.get("scope_approved") is decision["approved"], "actual scope decision differs"
        )
        ref = state.get("final_report_ref")
        require(
            ref == f"artifact://tasks/{row['task_id']}/safe-final-report.json",
            "v3 terminal result has no actual final report",
        )
        raw = self.store.safe.artifacts._read_bytes_bounded(ref, max_bytes=2_000_000)
        report = strict_json(raw)
        require(
            report["task_id"] == row["task_id"]
            and report["thread_id"] == row["thread_id"]
            and all(
                report.get(k) == state.get(k)
                for k in (
                    "status",
                    "scope_hash",
                    "scope_approved",
                    "rolled_back",
                    "rollback_ref",
                    "tests_ref",
                    "tests_sha256",
                    "review_ref",
                    "review_sha256",
                    "reviewer_verdict",
                )
            ),
            "v3 actual final report differs",
        )
        if state["status"] == "completed":
            before = self.store.source.load_snapshot(
                self.store._get(admission["source_sha256"]),
                expected_sha256=admission["source_sha256"],
            )
            _capture_at_owned_destination(
                state=state,
                before=before,
                artifacts=self.store.safe.artifacts,
                repository_url=self.store.repository_url,
                policy=self.store.trusted_policy,
                attestor=self.store.attestor,
                sandbox=self.preparation.filesystem.root
                / ("execution-" + row["operation_id"])
                / "repo",
            )
        else:
            require(
                not state.get("patch_applied") or state.get("rolled_back") is True,
                "v3 cannot close an ambiguous retained patch",
            )
            require(
                row["retained_sha256"] == admission["source_sha256"],
                "v3 failed result did not restore the accepted source",
            )

    def _seal(self, adapter):
        require(
            self._live.get(adapter.operation_id) is adapter,
            "v3 reconciliation requires the original live invocation",
        )
        adapter._returned_proof()
        coordinator = self.store.safe.control.cancellation
        with self.db.transaction(barrier=coordinator._settlement_barrier(adapter._context)):
            adapter._returned_proof()
            row, admission, _ = self._load(adapter.operation_id, adapter.owner_token)
            adapter._settling(row)
            self._verify_files(row, admission)
            raw, state, boundary = self._checkpoint(row, admission)
            require(
                (adapter.payload["action"] == "dispatch" and boundary == "scope")
                or (adapter.payload["action"] == "approve_scope" and boundary == "terminal"),
                "returned v3 action has an unsupported boundary",
            )
            require(
                adapter._result_state() == state, "actual returned state differs from checkpoint"
            )
            self.db.boundary("before_settlement")
            checkpoint_sha = self.store._put(raw)
            self._record(
                row,
                admission,
                state,
                "awaiting_scope_approval"
                if boundary == "scope"
                else ("completed" if state["status"] == "completed" else "failed"),
            )
            self.store.connection.execute(
                f"UPDATE {HEADS} SET checkpoint_sha256=? WHERE operation_id=?",
                (checkpoint_sha, row["operation_id"]),
            )
            current = self._row(row["operation_id"])
            settlement = {
                "schema": PREFIX + "settlement-3",
                "admission_sha256": row["admission_sha256"],
                "epoch": row["epoch"],
                "action": adapter.payload["action"],
                "request_id": adapter.payload["request_id"],
                "invocation_sha256": row["invocation_sha256"],
                "boundary": boundary,
                "checkpoint_sha256": checkpoint_sha,
                "task_sha256": row["task_sha256"],
                "scope_sha256": state["scope_hash"],
                "result_sha256": current["result_sha256"],
                "authority_sha256": row["authority_sha256"],
                "filesystem_sha256": row["filesystem_sha256"],
                "retained_sha256": row["retained_sha256"],
                "revoked": True,
                "registrations_absent": True,
                "remote_absence_sha256": self._remote_absence(admission),
            }
            result = self._complete(
                adapter.payload,
                adapter.owner_token,
                state="parked_scope" if boundary == "scope" else "closed",
                settlement=self._put_record(settlement),
                terminal_status=None if boundary == "scope" else state["status"],
            )
        return result

    def reconcile(self, program_id, operation_id, *, request_id):
        """Finish a reversible seal failure only with the original returned live object."""
        recorded = self.request_result(program_id, request_id)
        if recorded["request_status"] == "completed":
            return recorded
        adapter = self._live.get(operation_id)
        require(
            adapter is not None
            and adapter.payload["program_id"] == program_id
            and adapter.payload["request_id"] == request_id,
            "recovery_required: original live return evidence is unavailable",
        )
        return self._seal(adapter)

    def _complete(self, payload, owner_token, *, state, settlement=None, terminal_status=None):
        """One receipt -> proposal -> response DAG; references never form a hash cycle.

        Receipt.proposal identifies the consumed proposal (null at first park).
        The newly issued proposal binds that parked receipt. The immutable response
        then binds both. A GET returns these stored bytes without minting a proposal.
        """
        row = self._row(payload["operation_id"])
        admission = self._admission(row)
        task = self._json(row["task_sha256"]) if row["task_sha256"] else None
        scope = SafeTaskRequest.model_validate(task).manifest.canonical_hash() if task else None
        outcome = {
            "schema": PREFIX + "outcome-3",
            "state": state,
            "epoch": row["epoch"],
            "scope_sha256": scope,
            "result_sha256": row["result_sha256"],
            "terminal_status": terminal_status,
            **FLAGS,
        }
        receipt = {
            "schema": PREFIX + "receipt-3",
            "host_sha256": self.host_sha256,
            "operation_id": row["operation_id"],
            "program_id": row["program_id"],
            "admission_sha256": row["admission_sha256"],
            "sequence": row["sequence"] + 1,
            "old_epoch": payload["expected_epoch"],
            "epoch": row["epoch"],
            "state": state,
            "action": payload["action"],
            "request_id": payload["request_id"],
            "request_sha256": sha(canonical(payload)),
            "predecessor_sha256": row["receipt_sha256"],
            "settlement_sha256": settlement,
            "proposal_sha256": payload["proposal_sha256"],
            "decision_sha256": row["decision_sha256"],
            "result_sha256": row["result_sha256"],
            "outcome": outcome,
        }
        receipt_sha = self._put_record(receipt)
        db = self.store.connection
        db.execute(
            f"INSERT INTO {RECEIPTS} VALUES (?,?,?,?)",
            (receipt_sha, row["operation_id"], row["program_id"], receipt["sequence"]),
        )
        self.db.boundary("after_receipt")
        if state != "admitted":
            _, _, tasks = self._witness(admission, owner_token)
            self.lifecycle.release_program_worker_in_transaction(
                db, row["program_id"], task_ids=tasks, owner_token=owner_token
            )
            self.db.boundary("after_worker_release")
        db.execute(
            f"UPDATE {HEADS} SET state=?,sequence=?,receipt_sha256=?,invocation_state=?,"
            "settlement_sha256=?,revision=revision+1 WHERE operation_id=?",
            (
                state,
                receipt["sequence"],
                receipt_sha,
                "revoked" if settlement else None,
                settlement,
                row["operation_id"],
            ),
        )
        authority = self._refresh_authority(
            row["operation_id"], owner_token if state == "admitted" else None
        )
        proposal_sha = None
        if state == "parked_scope":
            proposal_sha = self._put_record(
                {
                    "schema": PREFIX + "proposal-3",
                    "operation_id": row["operation_id"],
                    "program_id": row["program_id"],
                    "admission_sha256": row["admission_sha256"],
                    "parked_epoch": row["epoch"],
                    "parked_receipt_sha256": receipt_sha,
                    "settlement_sha256": settlement,
                    "checkpoint_sha256": row["checkpoint_sha256"],
                    "task_sha256": row["task_sha256"],
                    "scope_sha256": scope,
                    "dependency_sha256": admission["dependency_sha256"],
                    "source_sha256": admission["source_sha256"],
                    "preparation_receipt_sha256": admission["preparation_receipt_sha256"],
                    "materialization_receipt_sha256": admission["materialization_receipt_sha256"],
                    "witness_sha256": authority["witness_sha256"],
                    "authority_sha256": self._put_record(authority),
                    "next_action": "scope_decision",
                }
            )
        db.execute(
            f"UPDATE {HEADS} SET proposal_sha256=? WHERE operation_id=?",
            (proposal_sha, row["operation_id"]),
        )
        response = {
            "schema": PREFIX + "response-3",
            "operation_id": row["operation_id"],
            "program_id": row["program_id"],
            "request_id": payload["request_id"],
            "request_status": "completed",
            "state": state,
            "epoch": row["epoch"],
            "admission_sha256": row["admission_sha256"],
            "receipt_sha256": receipt_sha,
            "proposal_sha256": proposal_sha,
            "scope_sha256": scope,
            "result_sha256": row["result_sha256"],
            "terminal_status": terminal_status,
            **FLAGS,
        }
        require(
            db.execute(
                f"UPDATE {REQUESTS} SET status='completed',response_sha256=? "
                "WHERE host_sha256=? AND program_id=? AND request_id=? AND status='pending'",
                (
                    self._put_record(response),
                    self.host_sha256,
                    row["program_id"],
                    payload["request_id"],
                ),
            ).rowcount
            == 1,
            "v3 request completion CAS differs",
        )
        self.db.boundary("after_request_completion")
        return response

    def _lineage(self, receipt, before):
        """Versioned dependency context: exact accepted predecessors, never a v1 Base relabel."""
        plan = self.store._plan(before.identity)
        entries, previous = [], None
        for index, phase in enumerate(plan.phases[: before.generation]):
            task, _ = self.store.programs._execution_ids(plan.program_id, phase.phase_id, None)
            row = self.store.connection.execute(
                """SELECT * FROM program_source_acceptances
                WHERE program_id = ? AND task_id = ?""",
                (plan.program_id, task),
            ).fetchone()
            _require(row is not None, "dependency source acceptance is missing")
            accepted = self._json(row["receipt_sha256"])
            _require(
                accepted["generation"] == index + 1
                and (previous is None or accepted["predecessor_sha256"] == previous),
                "dependency acceptance lineage differs",
            )
            candidate = self._json(row["candidate_sha256"])
            frozen = self._json(candidate["evidence_sha256"])
            prefix = f"programs/{plan.program_id}/phases/{phase.phase_id}"
            refs = [
                f"artifact://{prefix}/executions/{task}/safe-result-completed.json",
                f"artifact://{prefix}/phase-execution-report.json",
                f"artifact://{prefix}/phase-result.json",
                f"artifact://{prefix}/phase-summary.md",
            ]
            if frozen["schema"] == "uca-program-safe-source-evidence-2":
                saved_state = strict_json(base64.b64decode(frozen["program_result_base64"]))
                prefix = self._result_prefix(plan.program_id, phase.phase_id, task, saved_state)
                refs = [
                    f"artifact://{prefix}/{name}"
                    for name in (
                        "safe-result.json",
                        "phase-execution-report.json",
                        "phase-result.json",
                        "phase-summary.md",
                    )
                ]
            raw = [
                self.store.programs.artifacts._read_bytes_bounded(ref, max_bytes=2_000_000)
                for ref in refs
            ]
            _require(
                base64.b64decode(frozen["program_result_base64"], validate=True) == raw[0]
                and base64.b64decode(frozen["phase_report_base64"], validate=True) == raw[1],
                "accepted dependency Program artifacts changed",
            )
            result = PhaseResult.model_validate(strict_json(raw[2]))
            safe_result = strict_json(raw[0])
            safe_result = safe_result.get("state", safe_result)
            _require(
                tuple(result.changed_paths) == tuple(safe_result.get("actual_changed_paths", ()))
                and result.tests == (f"{task}: {safe_result.get('tests_ref')}",)
                and self.store.programs._phase_summary(plan.program_id, result).encode() == raw[3],
                "dependency result/summary differs from actual Safe evidence",
            )
            _require(
                result.phase_id == phase.phase_id
                and result.reviewer_verdict == "PASS"
                and bool(result.tests),
                "dependency phase result is not qualified",
            )
            entries.append(
                {
                    "phase_id": phase.phase_id,
                    "task_id": task,
                    "acceptance_receipt_sha256": row["receipt_sha256"],
                    "source_sha256": accepted["source_sha256"],
                    "predecessor_sha256": accepted["predecessor_sha256"],
                    "artifacts": [
                        {"ref": ref, "sha256": _hash(data)}
                        for ref, data in zip(refs, raw, strict=True)
                    ],
                    "summary": result.summary,
                }
            )
            previous = accepted["source_sha256"]
        _require(previous == receipt["source_sha256"], "dependency head is not the current source")
        content = _canonical(
            {
                "schema": "uca-accepted-source-lineage-2",
                "program_id": plan.program_id,
                "requirement_sha256": before.identity.requirement_sha256,
                "plan_sha256": before.identity.plan_sha256,
                "target_phase_id": receipt["phase_id"],
                "execution_base_sha": receipt["derived_git_commit_sha"],
                "source_sha256": previous,
                "phases": entries,
            }
        )
        _require(len(content) <= 48_000, "source-aware dependency context exceeds its bound")
        return content

    def _verify_files(self, row, admission, *, retained=None, mutable=()):
        """Verify immutable material and complete private worktree including .git and inodes."""
        base, store = self.preparation, self.store
        b = base._row(admission["operation_id"])
        m = base.materialization._row(admission["materialization_id"])
        _require(
            dict(b) == admission["preparation_row"] and dict(m) == admission["materialization_row"],
            "consumed preparation changed",
        )
        before = store.source.load_snapshot(
            store._get(admission["source_sha256"]), expected_sha256=admission["source_sha256"]
        )
        material = base.materialization
        intent = self._json(m["intent_sha256"])
        receipt = self._json(m["completion_sha256"])
        fs, deadline = material.filesystem, base.filesystem.deadline()
        with fs.root_handle(intent["root_chain"]) as (root, _):
            proof = fs.inspect(
                root,
                "source-" + m["operation_id"],
                material._marker(m),
                self._json(m["allocation_sha256"]),
                fs.layout(before),
                deadline,
            )
            _require(
                proof == store._get(receipt["filesystem_sha256"]),
                "accepted immutable materialization changed",
            )
            fs.anchor(intent["root_chain"])
        current = retained or store.source.load_snapshot(
            store._get(row["retained_sha256"]), expected_sha256=row["retained_sha256"]
        )
        layout = base.filesystem.execution_layout(before, store.source)
        tree = base.filesystem.layout(current)
        tree[".git"] = layout.tree[".git"]
        intent = self._json(b["intent_sha256"])
        fs = base.filesystem
        with fs.root_handle(intent["root_chain"]) as (root, _):
            proof = fs.inspect(
                root,
                "execution-" + b["operation_id"],
                base._marker(b),
                self._json(b["allocation_sha256"]),
                tree,
                deadline,
            )
            old, new = self._json(row["filesystem_sha256"]), strict_json(proof)
            _require(
                old["owner"] == new["owner"]
                and old["operation"] == new["operation"]
                and set(old["entries"]) == set(new["entries"]),
                "owned execution inventory changed",
            )
            parents = {""}
            for path in mutable:
                parents.update(
                    str(parent) + "/" for parent in Path(path).parents if str(parent) != "."
                )
            for path, stamp in new["entries"].items():
                expected = old["entries"][path]
                if path in mutable:
                    _require(
                        stamp[:1] == expected[:1] and stamp[2:5] == expected[2:5] and stamp[6] == 1,
                        "approved edit ownership/mode changed",
                    )
                elif mutable and path in parents:
                    _require(stamp[:5] == expected[:5], "approved parent was substituted")
                else:
                    _require(stamp == expected, "retained source or Git metadata changed")
            if current.files == before.files:
                base._verify_git(b["operation_id"], before, layout, deadline)
            fs.anchor(intent["root_chain"])
        return proof

    def _record(self, row, admission, state, status):
        """Derive Program output from the actual checkpoint under the attached transaction."""
        store, program, phase, task = (
            self.store,
            admission["program_id"],
            admission["phase_id"],
            admission["task_id"],
        )
        # Each proven checkpoint has immutable result artifacts. A crash after a file write
        # but before the DB commit must leave the prior committed report intact.
        prefix = self._result_prefix(program, phase, task, state)
        result_ref = store.programs.artifacts.write_json(f"{prefix}/safe-result.json", state)
        store.connection.execute(
            """UPDATE program_executions SET status = ?, safe_status = ?,
            result_ref = ? WHERE task_id = ?""",
            (status, state["status"], result_ref.uri, task),
        )
        if status == "completed":
            result = PhaseResult(
                phase_id=phase,
                summary="Completed one admitted v3 Safe unit; source remains unaccepted.",
                changed_paths=tuple(state.get("actual_changed_paths", ())),
                tests=(f"{task}: {state['tests_ref']}",),
                reviewer_verdict="PASS",
                artifact_refs=tuple(
                    v for v in state.values() if isinstance(v, str) and v.startswith("artifact://")
                ),
            )
            result_artifact = store.programs.artifacts.write_json(
                f"{prefix}/phase-result.json", result.model_dump(mode="json")
            )
            summary_ref = store.programs.artifacts.write_text(
                f"{prefix}/phase-summary.md",
                store.programs._phase_summary(program, result),
                "text/markdown",
            )
            store.connection.execute(
                """UPDATE program_phases SET status = 'completed',
                result_ref = ?, summary_ref = ? WHERE program_id = ? AND phase_id = ?""",
                (result_artifact.uri, summary_ref.uri, program, phase),
            )
            remaining = store.connection.execute(
                """SELECT 1 FROM program_phases
                WHERE program_id = ? AND status != 'completed' LIMIT 1""",
                (program,),
            ).fetchone()
            if remaining is None:
                store.connection.execute(
                    "UPDATE programs SET status = 'completed' WHERE program_id = ?", (program,)
                )
                store.connection.execute(
                    """UPDATE control.control_state
                    SET state = 'completed', reason = '', revision = revision + 1
                    WHERE entity_type = 'program' AND entity_id = ?""",
                    (program,),
                )
        elif status == "failed":
            store.connection.execute(
                "UPDATE program_phases SET status = 'failed' WHERE program_id = ? AND phase_id = ?",
                (program, phase),
            )
            store.connection.execute(
                "UPDATE programs SET status = 'blocked' WHERE program_id = ?", (program,)
            )
        execution = dict(
            store.connection.execute(
                "SELECT * FROM program_executions WHERE task_id = ?", (task,)
            ).fetchone()
        )
        execution.pop("unit_key")
        binding = ProgramExecutionBinding.model_validate(
            {**execution, "slice_id": execution["slice_id"] or None}
        )
        phase_status = store.connection.execute(
            "SELECT status FROM program_phases WHERE program_id = ? AND phase_id = ?",
            (program, phase),
        ).fetchone()[0]
        program_status = store.connection.execute(
            "SELECT status FROM programs WHERE program_id = ?", (program,)
        ).fetchone()[0]
        report_ref = store.programs.artifacts.write_json(
            f"{prefix}/phase-execution-report.json",
            {
                "schema": "uca-program-source-execution-report-3",
                "program_id": program,
                "program_status": program_status,
                "requirement_hash": binding.requirement_hash,
                "phase_id": phase,
                "phase_status": phase_status,
                "admission_sha256": row["admission_sha256"],
                "cross_phase_source_handoff": False,
                "source_acceptance_authorized": False,
                "execution_authorized": False,
                "consumer_bound": True,
                "automatic_execution": False,
                "bindings": [binding.model_dump(mode="json")],
            },
        )
        store.connection.execute(
            "UPDATE program_executions SET phase_report_ref = ? WHERE task_id = ?",
            (report_ref.uri, task),
        )
        store.connection.execute(
            "UPDATE program_source_continuation_heads_v3 SET result_sha256 = ? "
            "WHERE operation_id = ?",
            (
                store._put(
                    _canonical(
                        {"result_sha256": result_ref.sha256, "report_sha256": report_ref.sha256}
                    )
                ),
                row["operation_id"],
            ),
        )

    @staticmethod
    def _result_prefix(program, phase, task, state):
        return (
            f"programs/{program}/phases/{phase}/executions/{task}/"
            f"source-results/{_hash(_canonical(state))}"
        )
