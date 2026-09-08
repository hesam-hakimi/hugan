"""Bounded historical proof of a completed v3 unit, with no live owner substitution."""

from __future__ import annotations

from universal_coding_agent.product.program_continuation_execution_store import (
    DISPATCH,
    HEADS,
    PREFIX,
    RECEIPTS,
    REQUESTS,
    _request,
    closed_foundation,
    require,
)


def terminal_history(reader, program, operation):
    dispatches = reader.rows(
        DISPATCH,
        (
            "operation_id",
            "program_id",
            "phase_id",
            "task_id",
            "thread_id",
            "admission_sha256",
            "host_sha256",
            "preparation_receipt_sha256",
            "guard_sha256",
        ),
        "program_id=?",
        (program,),
        limit=1,
    )
    require(
        len(dispatches) == 1 and dispatches[0]["operation_id"] == operation,
        "final Program must have exactly one v3 admission",
    )
    heads = reader.rows(
        HEADS,
        (
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
        ),
        "program_id=?",
        (program,),
        limit=1,
    )
    require(len(heads) == 1 and heads[0]["operation_id"] == operation, "final v3 head is missing")
    row = {**dispatches[0], **heads[0], "approval_sha256": heads[0]["decision_sha256"]}
    require(
        row["state"] == "closed"
        and row["epoch"] == 1
        and row["sequence"] == 3
        and row["invocation_state"] == "revoked"
        and row["invocation_action"] == "approve_scope"
        and row["proposal_sha256"] is None,
        "v3 execution has not settled terminally",
    )
    envelope = reader.record(row["admission_sha256"], "uca-program-source-dispatch-3")
    admission = envelope["intent"]
    require(
        all(
            admission[k] == row[k]
            for k in (
                "program_id",
                "operation_id",
                "phase_id",
                "task_id",
                "thread_id",
                "host_sha256",
                "preparation_receipt_sha256",
            )
        )
        and envelope["guard_sha256"] == row["guard_sha256"],
        "v3 admission binding differs",
    )
    terminal = reader.receipt(row["receipt_sha256"], program)
    require(
        terminal["outcome"]["terminal_status"] == "completed"
        and all(
            terminal[k] == row[k]
            for k in (
                "program_id",
                "operation_id",
                "epoch",
                "state",
                "sequence",
                "host_sha256",
                "admission_sha256",
                "settlement_sha256",
                "decision_sha256",
                "result_sha256",
                "request_id",
            )
        ),
        "v3 terminal is not a completed exact result",
    )
    indexed = reader.rows(
        RECEIPTS,
        ("receipt_sha256", "sequence"),
        "program_id=?",
        (program,),
        order="sequence",
        limit=3,
    )
    requests = reader.rows(REQUESTS, ("request_id", "status"), "program_id=?", (program,), limit=3)
    require(
        len(indexed) == len(requests) == 3 and all(r["status"] == "completed" for r in requests),
        "v3 complete request/receipt history differs",
    )
    previous = None
    completed = None
    for index, item in enumerate(indexed, 1):
        receipt = reader.record(item["receipt_sha256"], PREFIX + "receipt-3")
        require(
            receipt["sequence"] == item["sequence"] == index
            and receipt["predecessor_sha256"] == previous
            and receipt["admission_sha256"] == row["admission_sha256"],
            "v3 full history is discontinuous",
        )
        completed = _request(reader, program, receipt["request_id"])
        require(completed is not None and completed["status"] == "completed", "missing v3 response")
        if index > 1:
            settlement = reader.record(receipt["settlement_sha256"], PREFIX + "settlement-3")
            require(
                all(
                    settlement[k] == receipt[k]
                    for k in ("admission_sha256", "epoch", "action", "request_id", "result_sha256")
                )
                and settlement["revoked"] is True
                and settlement["registrations_absent"] is True
                and settlement["boundary"] == ("terminal" if index == 3 else "scope"),
                "v3 settlement provenance differs",
            )
            authority = reader.record(settlement["authority_sha256"], PREFIX + "authority-3")
            require(
                authority["admission_sha256"] == row["admission_sha256"]
                and authority["owner_sha256"] is not None
                and authority["epoch"] == settlement["epoch"]
                and authority["filesystem_sha256"] == settlement["filesystem_sha256"]
                and authority["retained_sha256"] == settlement["retained_sha256"],
                "v3 settlement authority differs",
            )
            reader.metadata(authority["witness_sha256"])
            if index == 3:
                require(
                    all(
                        settlement[k] == row[k]
                        for k in (
                            "invocation_sha256",
                            "checkpoint_sha256",
                            "task_sha256",
                            "result_sha256",
                            "filesystem_sha256",
                            "retained_sha256",
                        )
                    ),
                    "v3 terminal proof changed",
                )
                decision = reader.record(receipt["decision_sha256"], PREFIX + "scope-decision-3")
                proposal = reader.record(receipt["proposal_sha256"], PREFIX + "proposal-3")
                require(
                    decision["approved"] is True
                    and decision["proposal_sha256"] == receipt["proposal_sha256"]
                    and decision["request_id"] == receipt["request_id"]
                    and decision["scope_sha256"] == settlement["scope_sha256"]
                    and decision["parked_receipt_sha256"] == previous
                    and proposal["parked_receipt_sha256"] == previous,
                    "v3 exact approved scope history differs",
                )
        previous = item["receipt_sha256"]
    require(previous == row["receipt_sha256"], "v3 head omits receipt history")
    authority = reader.record(row["authority_sha256"], PREFIX + "authority-3")
    require(
        authority
        == {
            **authority,
            "admission_sha256": row["admission_sha256"],
            "epoch": 1,
            "state": "closed",
            "predecessor_sha256": row["receipt_sha256"],
            "owner_sha256": None,
            "filesystem_sha256": row["filesystem_sha256"],
            "retained_sha256": row["retained_sha256"],
        },
        "v3 post-release historical authority differs",
    )
    baseline = reader.metadata(authority["witness_sha256"])
    require(
        baseline["program"]["program_id"] == program
        and baseline["program"]["status"] == "completed"
        and len(baseline["phases"]) == len(baseline["executions"]) == 2
        and all(p["status"] == "completed" for p in baseline["phases"])
        and all(
            e["status"] == e["safe_status"] == "completed"
            and not e["error_ref"]
            and not e["remote_disposition_ref"]
            for e in baseline["executions"]
        )
        and len(baseline["controls"]) == 3
        and all(c["state"] == "completed" for c in baseline["controls"])
        and baseline["source"][0]["generation"] == admission["generation"] == 1
        and baseline["source"][0]["source_sha256"] == admission["source_sha256"]
        and baseline["source"][0]["receipt_sha256"] == admission["acceptance_receipt_sha256"],
        "v3 post-terminal semantic baseline is incomplete",
    )
    for table, key, frozen in (
        ("program_execution_bases", "operation_id", admission["preparation_row"]),
        ("program_source_materializations", "operation_id", admission["materialization_row"]),
    ):
        actual = reader.rows(table, tuple(frozen), f"{key}=?", (frozen[key],), limit=1)
        require(actual == [frozen] and frozen["state"] == "complete", "consumed c1 row changed")
        intent = reader.metadata(frozen["intent_sha256"])
        reader.metadata(frozen["allocation_sha256"])
        completion = reader.metadata(frozen["completion_sha256"])
        require(
            completion["intent_sha256"] == frozen["intent_sha256"]
            and completion["allocation_sha256"] == frozen["allocation_sha256"]
            and completion["operation_id"] == frozen[key]
            and completion["source_sha256"] == admission["source_sha256"]
            and completion["acceptance_receipt_sha256"] == admission["acceptance_receipt_sha256"],
            "consumed c1 immutable history differs",
        )
        if table == "program_execution_bases":
            require(
                completion["program_id"] == intent["binding"]["program_id"] == program,
                "execution Base Program differs",
            )
        else:
            require(
                intent["program_id"] == intent["binding"]["program"]["program_id"] == program
                and completion["schema"] == "uca-source-materialization-receipt-1"
                and completion["materialization_complete"] is True
                and completion["automatic_execution"] is False,
                "materialization history differs",
            )
    preparation = reader.metadata(admission["preparation_receipt_sha256"])
    require(
        preparation["schema"] == "uca-program-execution-base-receipt-1"
        and preparation["execution_base_complete"] is True
        and preparation["dispatch_authorized"] is False
        and all(
            preparation[k] == admission[k]
            for k in (
                "program_id",
                "operation_id",
                "phase_id",
                "task_id",
                "thread_id",
                "generation",
                "source_sha256",
                "acceptance_receipt_sha256",
                "materialization_id",
                "materialization_receipt_sha256",
                "derived_git_commit_sha",
                "derived_git_tree_sha",
                "origin_repository_sha256",
                "origin_base_sha",
                "origin_tree_sha",
                "object_format",
            )
        ),
        "c1 completion/admission lineage differs",
    )
    lineage = reader.metadata(admission["dependency_sha256"])
    require(
        lineage["schema"] == "uca-accepted-source-lineage-2"
        and lineage["program_id"] == program
        and len(lineage["phases"]) == 1
        and lineage["source_sha256"] == admission["source_sha256"]
        and lineage["phases"][0]["acceptance_receipt_sha256"]
        == admission["acceptance_receipt_sha256"],
        "v3 dependency lineage differs",
    )
    first = reader.metadata(admission["acceptance_receipt_sha256"])
    candidate = reader.metadata(first["candidate_sha256"])
    approval = reader.metadata(first["approval_sha256"])
    indexed = reader.rows(
        "program_source_acceptances",
        ("candidate_sha256", "approval_sha256", "receipt_sha256", "task_id"),
        "program_id=? AND task_id=?",
        (program, first["task_id"]),
        limit=1,
    )
    require(
        indexed
        == [
            {
                "candidate_sha256": first["candidate_sha256"],
                "approval_sha256": first["approval_sha256"],
                "receipt_sha256": admission["acceptance_receipt_sha256"],
                "task_id": first["task_id"],
            }
        ]
        and first["schema"] == "uca-source-acceptance-receipt-1"
        and first["generation"] == 1
        and first["source_sha256"] == admission["source_sha256"]
        and first["materialization_ready"] is False
        and first["program_id"] == program
        and candidate["schema"] == "uca-source-candidate-1"
        and candidate["generation"] == 0
        and candidate["task_id"] == first["task_id"]
        and candidate["program_id"] == program
        and candidate["host_sha256"] == first["host_sha256"] == baseline["source"][0]["host_sha256"]
        and candidate["before_sha256"] == first["predecessor_sha256"]
        and candidate["after_sha256"] == first["source_sha256"]
        and candidate["transition_sha256"] == first["transition_sha256"]
        and approval["schema"] == "uca-source-approval-1"
        and approval["candidate_sha256"] == first["candidate_sha256"]
        and approval["approved_transition_sha256"] == first["transition_sha256"],
        "original receipt-1 acceptance history differs",
    )
    require(
        reader.rows(
            "program_source_candidates",
            ("program_id",),
            "candidate_sha256=?",
            (first["candidate_sha256"],),
            limit=1,
        )
        == [{"program_id": program}],
        "first candidate missing",
    )
    initial = reader.metadata(baseline["source"][0]["initial_receipt_sha256"])
    require(
        initial["schema"] == "uca-source-initialization-1"
        and initial["source_sha256"] == first["predecessor_sha256"]
        and initial["host_sha256"] == first["host_sha256"]
        and initial["attestation"]["snapshot_sha256"] == initial["source_sha256"],
        "original source initialization lineage differs",
    )
    # Receipt-1 remains historical same-owner acceptance. Every immutable
    # predecessor link must still exist with its exact bytes; no old owner is
    # reconstructed and no checkpoint decoder is used by recorded readers.
    for key in (
        "before_sha256",
        "after_sha256",
        "transition_sha256",
        "evidence_sha256",
        "checkpoint_sha256",
    ):
        reader.artifact(candidate[key])
    present = [
        reader.connection.execute("SELECT type FROM sqlite_master WHERE name=?", (name,)).fetchone()
        for name in (
            "program_continuation_heads",
            "program_continuation_receipts",
            "program_continuation_requests",
        )
    ]
    require(not any(present) or all(present), "incomplete inert foundation history")
    if any(present):
        require(all(row[0] == "table" for row in present), "inert foundation table substituted")
        closed_foundation(reader.connection, program)
    return row, admission, baseline, completed
