"""Recorded mixed receipt-1/receipt-2 lineage; never filesystem or live authority.

Existing files are opened read-only. No legacy status fallback, constructors,
checkpoint decoders, provider imports, graph setup or lifecycle mutations.
"""

from __future__ import annotations

from universal_coding_agent.product.program_continuation_execution_store import (
    canonical,
    digest,
    identifier,
    require,
    sha,
)
from universal_coding_agent.product.program_source_acceptance_v2_store import (
    DECISIONS,
    EXACT_FIELDS,
    PROPOSALS,
    REQUESTS,
    read_session,
)
from universal_coding_agent.product.program_source_terminal_proof import terminal_history


def candidate_links(reader, candidate_sha):
    candidate = reader.record(candidate_sha, "uca-source-candidate-2")
    core = reader.record(candidate["core_sha256"], "uca-source-evidence-core-2")
    require(
        all(
            core[k] == candidate[k]
            for k in (
                "program_id",
                "operation_id",
                "task_id",
                "host_sha256",
                "before_sha256",
                "after_sha256",
                "transition_sha256",
                "generation",
                "predecessor_receipt_sha256",
                "terminal_receipt_sha256",
            )
        ),
        "candidate evidence core linkage differs",
    )
    proposals = reader.rows(
        PROPOSALS,
        ("program_id", "task_id", "operation_id", "candidate_sha256", "request_sha256"),
        "candidate_sha256=?",
        (candidate_sha,),
        limit=1,
    )
    require(
        len(proposals) == 1
        and all(proposals[0][k] == candidate[k] for k in ("program_id", "operation_id", "task_id")),
        "candidate index differs",
    )
    request = reader.record(proposals[0]["request_sha256"], "uca-source-request-2")
    require(
        request["action"] == "preview"
        and all(
            request[k] == candidate[k]
            for k in (
                "program_id",
                "operation_id",
                "host_sha256",
                "before_sha256",
                "generation",
                "terminal_receipt_sha256",
            )
        ),
        "candidate preview request differs",
    )
    return candidate, core, proposals[0]


def completed_request(reader, host, program, request_id, expected=None):
    rows = reader.rows(
        REQUESTS,
        (
            "host_sha256",
            "program_id",
            "request_id",
            "operation_id",
            "action",
            "payload_sha256",
            "baseline_sha256",
            "owner_sha256",
            "status",
            "response_sha256",
        ),
        "host_sha256=? AND program_id=? AND request_id=?",
        (host, program, request_id),
        limit=1,
    )
    if not rows:
        return None
    row = rows[0]
    payload = reader.record(row["payload_sha256"], "uca-source-request-2")
    require(
        all(
            payload[k] == row[k]
            for k in ("host_sha256", "program_id", "request_id", "operation_id", "action")
        ),
        "stored request differs",
    )
    require(
        expected is None or payload == expected, "request ID conflicts with another exact payload"
    )
    require(
        row["status"] == "completed" and row["response_sha256"] is not None,
        "pending source request requires explicit administrative recovery; it cannot resume",
    )
    response = reader.record(row["response_sha256"], "uca-source-response-2")
    require(
        all(
            response[k] == payload[k]
            for k in ("host_sha256", "program_id", "operation_id", "request_id", "action")
        )
        and response["request_sha256"] == row["payload_sha256"],
        "recorded response differs",
    )
    candidate, core, proposal = candidate_links(reader, response["candidate_sha256"])
    require(
        response["candidate"] == candidate
        and all(
            candidate[k] == payload[k]
            for k in (
                "program_id",
                "operation_id",
                "host_sha256",
                "before_sha256",
                "generation",
                "terminal_receipt_sha256",
            )
        ),
        "response reviewed candidate differs",
    )
    witness = reader.record(response["witness_sha256"], "uca-source-capture-witness-2")
    require(
        witness["baseline_sha256"] == core["baseline_sha256"] == row["baseline_sha256"]
        and witness["owner_sha256"] == row["owner_sha256"]
        and witness["core_sha256"] == candidate["core_sha256"]
        and all(
            witness[k] == core[k]
            for k in (
                "program_id",
                "operation_id",
                "host_sha256",
                "checkpoint_sha256",
                "filesystem_sha256",
                "inventory_sha256",
            )
        ),
        "historical capture witness differs",
    )
    reader.metadata(witness["baseline_sha256"])
    terminal, admission, baseline, completed = terminal_history(
        reader, program, candidate["operation_id"]
    )
    require(
        core["terminal_receipt_sha256"] == terminal["receipt_sha256"]
        and core["baseline_sha256"] == sha(canonical(baseline))
        and core["terminal_response_sha256"] == completed["response_sha256"]
        and all(
            core[k] == terminal[k]
            for k in (
                "admission_sha256",
                "settlement_sha256",
                "decision_sha256",
                "checkpoint_sha256",
                "result_sha256",
            )
        )
        and all(
            core[k] == admission[k]
            for k in (
                "preparation_receipt_sha256",
                "materialization_receipt_sha256",
                "dependency_sha256",
            )
        ),
        "recorded core terminal history differs",
    )
    if payload["action"] == "preview":
        require(
            response["status"] == "prepared"
            and proposal["request_sha256"] == row["payload_sha256"],
            "preview response differs",
        )
    else:
        require(
            response["status"] == ("accepted" if payload["approved"] else "rejected")
            and response["candidate_sha256"] == payload["candidate_sha256"]
            and all(
                payload[k] == candidate[k] for k in EXACT_FIELDS.split() if k != "candidate_sha256"
            ),
            "decision response differs",
        )
        approval = reader.record(response["approval_sha256"], "uca-source-approval-2")
        require(
            approval == {**payload, "schema": "uca-source-approval-2"}, "exact approval differs"
        )
        decisions = reader.rows(
            DECISIONS,
            ("candidate_sha256", "approval_sha256", "receipt_sha256", "request_sha256", "approved"),
            "candidate_sha256=?",
            (response["candidate_sha256"],),
            limit=1,
        )
        require(
            decisions
            == [
                {
                    "candidate_sha256": response["candidate_sha256"],
                    "approval_sha256": response["approval_sha256"],
                    "receipt_sha256": response["receipt_sha256"],
                    "request_sha256": row["payload_sha256"],
                    "approved": int(payload["approved"]),
                }
            ],
            "versioned decision ledger differs",
        )
        shared = reader.rows(
            "program_source_acceptances",
            ("candidate_sha256", "approval_sha256", "receipt_sha256", "program_id", "task_id"),
            "program_id=? AND task_id=?",
            (program, candidate["task_id"]),
            limit=1,
        )
        if not payload["approved"]:
            require(not shared, "rejected candidate unexpectedly accepted source")
        else:
            receipt = reader.record(response["receipt_sha256"], "uca-source-acceptance-receipt-2")
            require(
                shared
                == [
                    {
                        k: receipt[k]
                        for k in (
                            "candidate_sha256",
                            "approval_sha256",
                            "receipt_sha256",
                            "program_id",
                            "task_id",
                        )
                        if k != "receipt_sha256"
                    }
                    | {"receipt_sha256": response["receipt_sha256"]}
                ],
                "shared acceptance ledger differs",
            )
            require(
                receipt["candidate_sha256"] == response["candidate_sha256"]
                and receipt["approval_sha256"] == response["approval_sha256"]
                and receipt["witness_sha256"] == response["witness_sha256"]
                and receipt["source_sha256"] == candidate["after_sha256"]
                and receipt["predecessor_sha256"] == candidate["before_sha256"]
                and receipt["host_sha256"] == core["source_host_sha256"]
                and receipt["acceptance_host_sha256"] == host
                and receipt["generation"] == 2
                and all(
                    receipt[k] == candidate[k]
                    for k in (
                        "program_id",
                        "task_id",
                        "operation_id",
                        "core_sha256",
                        "transition_sha256",
                        "predecessor_receipt_sha256",
                        "terminal_receipt_sha256",
                    )
                ),
                "accepted receipt differs",
            )
    return response


def request_result(database_path, host_sha256, program_id, request_id):
    digest(host_sha256)
    identifier(program_id)
    identifier(request_id)
    with read_session(database_path) as reader:
        result = completed_request(reader, host_sha256, program_id, request_id)
        require(result is not None, "source request was not recorded")
        return result


def source_transition_status(database_path, program_id):
    identifier(program_id)
    with read_session(database_path) as reader:
        heads = reader.rows(
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
            (program_id,),
            limit=1,
        )
        require(
            len(heads) == 1 and heads[0]["generation"] in {1, 2}, "unsupported accepted source head"
        )
        head = heads[0]
        initial = reader.metadata(head["initial_receipt_sha256"])
        require(
            initial["schema"] == "uca-source-initialization-1"
            and initial["host_sha256"] == head["host_sha256"]
            and initial["attestation"]["snapshot_sha256"] == initial["source_sha256"]
            and initial["attestation"]["identity"]["program_id"] == program_id,
            "source origin lineage differs",
        )
        rows = reader.rows(
            "program_source_acceptances",
            ("candidate_sha256", "approval_sha256", "receipt_sha256", "task_id"),
            "program_id=?",
            (program_id,),
            limit=2,
        )
        require(len(rows) == head["generation"], "source acceptance history is incomplete")
        history = []
        for row in rows:
            receipt = reader.metadata(row["receipt_sha256"])
            require(
                receipt["program_id"] == program_id
                and receipt["host_sha256"] == head["host_sha256"]
                and all(
                    receipt[k] == row[k] for k in ("candidate_sha256", "approval_sha256", "task_id")
                ),
                "shared receipt index differs",
            )
            if receipt["schema"] == "uca-source-acceptance-receipt-1":
                require(
                    receipt["generation"] == 1 and receipt["materialization_ready"] is False,
                    "first source acceptance must remain receipt-1",
                )
                candidate = reader.metadata(row["candidate_sha256"])
                approval = reader.metadata(row["approval_sha256"])
                indexed = reader.rows(
                    "program_source_candidates",
                    ("program_id",),
                    "candidate_sha256=?",
                    (row["candidate_sha256"],),
                    limit=1,
                )
                require(
                    indexed == [{"program_id": program_id}]
                    and candidate["schema"] == "uca-source-candidate-1"
                    and candidate["program_id"] == program_id
                    and candidate["task_id"] == row["task_id"]
                    and candidate["host_sha256"] == head["host_sha256"]
                    and candidate["generation"] == 0
                    and candidate["before_sha256"]
                    == receipt["predecessor_sha256"]
                    == initial["source_sha256"]
                    and candidate["after_sha256"] == receipt["source_sha256"]
                    and candidate["transition_sha256"] == receipt["transition_sha256"]
                    and approval["schema"] == "uca-source-approval-1"
                    and approval["candidate_sha256"] == row["candidate_sha256"]
                    and approval["approved_transition_sha256"] == receipt["transition_sha256"],
                    "first-phase same-owner acceptance lineage differs",
                )
            else:
                require(
                    receipt["schema"] == "uca-source-acceptance-receipt-2"
                    and receipt["generation"] == 2,
                    "unknown source receipt version",
                )
                approval = reader.record(row["approval_sha256"], "uca-source-approval-2")
                completed_request(
                    reader, approval["host_sha256"], program_id, approval["request_id"]
                )
            history.append({**receipt, "receipt_sha256": row["receipt_sha256"]})
        history.sort(key=lambda r: r["generation"])
        require(
            [r["generation"] for r in history] == list(range(1, head["generation"] + 1))
            and history[-1]["source_sha256"] == head["source_sha256"]
            and history[-1]["receipt_sha256"] == head["receipt_sha256"],
            "accepted head skips lineage",
        )
        if len(history) == 2:
            require(
                history[1]["predecessor_sha256"] == history[0]["source_sha256"]
                and history[1]["predecessor_receipt_sha256"] == history[0]["receipt_sha256"],
                "mixed receipt predecessor differs",
            )
        dispatches = reader.rows(
            "program_source_dispatches_v3",
            ("operation_id",),
            "program_id=?",
            (program_id,),
            limit=1,
        )
        require(len(dispatches) == 1, "final v3 metadata is missing")
        terminal, admission, _, _ = terminal_history(
            reader, program_id, dispatches[0]["operation_id"]
        )
        require(
            admission["source_sha256"] == history[0]["source_sha256"]
            and admission["acceptance_receipt_sha256"] == history[0]["receipt_sha256"],
            "historical v3 predecessor differs",
        )
        if len(history) == 2:
            require(
                history[1]["terminal_receipt_sha256"] == terminal["receipt_sha256"]
                and history[1]["task_id"] == terminal["task_id"],
                "accepted terminal lineage differs",
            )
        proposals = reader.rows(
            PROPOSALS,
            ("candidate_sha256", "request_sha256"),
            "program_id=?",
            (program_id,),
            limit=1,
        )
        candidates = []
        for proposal in proposals:
            candidate, core, _ = candidate_links(reader, proposal["candidate_sha256"])
            request = reader.record(proposal["request_sha256"], "uca-source-request-2")
            completed_request(reader, request["host_sha256"], program_id, request["request_id"])
            require(
                core["admission_sha256"] == terminal["admission_sha256"]
                and core["terminal_receipt_sha256"] == terminal["receipt_sha256"],
                "candidate terminal lineage differs",
            )
            candidates.append({"candidate_sha256": proposal["candidate_sha256"], **candidate})
        requests = reader.rows(
            REQUESTS,
            (
                "host_sha256",
                "request_id",
                "status",
                "payload_sha256",
                "baseline_sha256",
                "owner_sha256",
                "response_sha256",
            ),
            "program_id=?",
            (program_id,),
            limit=2,
        )
        request_status = []
        for request in requests:
            payload = reader.record(request["payload_sha256"], "uca-source-request-2")
            require(
                payload["host_sha256"] == request["host_sha256"]
                and payload["program_id"] == program_id
                and payload["request_id"] == request["request_id"],
                "request history identity differs",
            )
            reader.metadata(request["baseline_sha256"])
            digest(request["owner_sha256"])
            if request["status"] == "completed":
                completed_request(reader, request["host_sha256"], program_id, request["request_id"])
            else:
                require(
                    request["status"] == "pending" and request["response_sha256"] is None,
                    "unknown request recovery state",
                )
            request_status.append(
                {"request_id": request["request_id"], "status": request["status"]}
            )
        return {
            "schema": "uca-source-transition-status-2",
            "program_id": program_id,
            "generation": head["generation"],
            "source_sha256": head["source_sha256"],
            "lineage": history,
            "candidates": candidates,
            "requests": request_status,
            "terminal_receipt_sha256": terminal["receipt_sha256"],
            "source_bytes_verified": False,
            "filesystem_verified": False,
            "current_authority_verified": False,
            "execution_authorized": False,
            "automatic_execution": False,
            "materialization_ready": False,
        }
