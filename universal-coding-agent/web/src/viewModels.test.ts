import { describe, expect, it } from "vitest";

import type {
  CancellationReport,
  ProgramExecutionSnapshot,
  ProgramSnapshot,
  RemoteOperationDisposition,
  RemoteOperationLeaseRetirement,
  RemoteOperationLeaseRetirementEligibilityCode,
  RemoteOperationSnapshot,
  RetainedRemoteOperationLeaseInventoryItem,
  RequirementContract,
  TaskSnapshot,
} from "./types";
import {
  activeProgramExecutionBinding,
  canApproveScope,
  canContinueProgramExecution,
  canDisposeRemoteOperation,
  canReconcileRemoteOperation,
  canRetireRemoteOperationLease,
  canStartProgramExecution,
  cancellationEvidencePresentation,
  hasRemoteOperationEvidence,
  phaseProgress,
  remoteOperationDispositionPresentation,
  remoteOperationLeaseRetirementPresentation,
  remoteOperationPresentation,
  retainedRemoteOperationLeaseEligibilityPresentation,
  statusTone,
  unresolvedClarifications,
} from "./viewModels";

function executionSnapshot(
  overrides: Partial<ProgramExecutionSnapshot["runtime"]> = {},
): ProgramExecutionSnapshot {
  return {
    program_id: "program-1",
    program_status: "running",
    runtime: {
      busy: false,
      action: "",
      task_id: "",
      status: "idle",
      recovered_pending: false,
      requires_explicit_action: false,
      error_type: "",
      error: "",
      ...overrides,
    },
    bindings: [],
  };
}

const runningProgram = {
  program_id: "program-1",
  status: "running",
} as ProgramSnapshot;

function cancellationReport(
  overrides: Partial<CancellationReport> = {},
): CancellationReport {
  return {
    task_id: "task-1",
    reason: "operator cancelled",
    active_operation_kinds: ["provider"],
    owned_processes_observed: 0,
    owned_cancellable_operations_observed: 0,
    terminate_requests: 0,
    kill_requests: 0,
    cancellable_operation_cancel_requests: 0,
    processes_still_active: 0,
    cancellable_operations_still_active: 0,
    cooperative_fallback: false,
    ...overrides,
  };
}

function remoteOperation(
  overrides: Partial<RemoteOperationSnapshot> = {},
): RemoteOperationSnapshot {
  return {
    task_id: "task-1",
    thread_id: "thread-1",
    transport: "openai_responses",
    transport_scope: `sha256:${"a".repeat(64)}`,
    operation_ref: `sha256:${"b".repeat(64)}`,
    base_sha: "c".repeat(40),
    created_at: "2026-08-26T12:00:00Z",
    updated_at: "2026-08-26T12:01:00Z",
    last_status: "in_progress",
    state: "active",
    cancellation_requested: false,
    revision: 1,
    reconciliation_attempts: 0,
    cancel_requests: 0,
    last_action: null,
    recovered_pending: true,
    requires_explicit_action: true,
    requires_explicit_disposition: false,
    ...overrides,
  };
}

function remoteDisposition(
  overrides: Partial<RemoteOperationDisposition> = {},
): RemoteOperationDisposition {
  return {
    schema_version: "1",
    audit_ref: `sha256:${"d".repeat(64)}`,
    task_id: "task-1",
    outcome: "cancelled",
    reason: "Operator confirmed terminal closure.",
    recorded_at: "2026-08-26T12:02:00Z",
    program_id: "",
    phase_id: "",
    slice_id: "",
    transport: "openai_responses",
    transport_scope: `sha256:${"a".repeat(64)}`,
    operation_ref: `sha256:${"b".repeat(64)}`,
    base_sha: "c".repeat(40),
    remote_state: "terminal",
    remote_status: "cancelled",
    remote_revision: 2,
    remote_updated_at: "2026-08-26T12:01:00Z",
    provider_confirmed_cancelled: true,
    confirmed_by_operator: true,
    provider_calls_made: 0,
    output_consumed: false,
    graph_resumed: false,
    program_phase_advanced: false,
    ...overrides,
  };
}

function remoteLeaseRetirement(
  overrides: Partial<RemoteOperationLeaseRetirement> = {},
): RemoteOperationLeaseRetirement {
  return {
    schema_version: "1",
    retirement_ref: `sha256:${"e".repeat(64)}`,
    task_id: "task-1",
    disposition_audit_ref: `sha256:${"d".repeat(64)}`,
    disposition_outcome: "cancelled",
    program_id: "",
    phase_id: "",
    slice_id: "",
    reason: "Operator approved local private lease retirement.",
    retired_at: "2026-08-26T12:03:00Z",
    transport: "openai_responses",
    transport_scope: `sha256:${"a".repeat(64)}`,
    operation_ref: `sha256:${"b".repeat(64)}`,
    base_sha: "c".repeat(40),
    remote_state: "terminal",
    remote_status: "cancelled",
    remote_revision: 2,
    remote_updated_at: "2026-08-26T12:01:00Z",
    confirmed_by_operator: true,
    private_lease_rows_retired: 1,
    private_identifier_retained_in_active_store: false,
    provider_calls_made: 0,
    output_consumed: false,
    graph_resumed: false,
    task_outcome_changes_made: 0,
    program_outcome_changes_made: 0,
    program_phase_advanced: false,
    ...overrides,
  };
}

function retainedLeaseInventoryItem(
  overrides: Partial<RetainedRemoteOperationLeaseInventoryItem> = {},
): RetainedRemoteOperationLeaseInventoryItem {
  return {
    schema_version: "1",
    task_id: "task-1",
    program_id: "",
    phase_id: "",
    slice_id: "",
    transport: "openai_responses",
    remote_state: "terminal",
    remote_status: "cancelled",
    remote_revision: 2,
    remote_updated_at: "2026-08-26T12:01:00Z",
    disposition_audit_ref: `sha256:${"d".repeat(64)}`,
    disposition_outcome: "cancelled",
    disposition_recorded_at: "2026-08-26T12:02:00Z",
    retained_private_lease: true,
    eligible_for_retirement: true,
    eligibility_reasons: [],
    preview_is_advisory: true,
    action_revalidation_required: true,
    ...overrides,
  };
}

describe("control-center view models", () => {
  it("classifies delivery states without changing backend semantics", () => {
    expect(statusTone("completed")).toBe("good");
    expect(statusTone("awaiting_scope_approval")).toBe("warn");
    expect(statusTone("failed")).toBe("bad");
    expect(statusTone("discovering")).toBe("neutral");
  });

  it("counts completed phases", () => {
    const program = {
      phases: [
        { phase_id: "p1", title: "One", status: "completed", dependencies: [] },
        { phase_id: "p2", title: "Two", status: "pending", dependencies: ["p1"] },
      ],
    } as unknown as ProgramSnapshot;
    expect(phaseProgress(program)).toEqual({ completed: 1, total: 2 });
  });

  it("uses stable decision keys when deciding whether clarification remains", () => {
    const contract = {
      clarifications: [
        {
          question_id: "Q-001",
          decision_key: "authorization_role",
          question: "Which role?",
          severity: "blocking",
          rationale: "security",
          options: [],
          recommended_answer: "",
        },
      ],
      answers: { authorization_role: "manager" },
    } as unknown as RequirementContract;
    expect(unresolvedClarifications(contract)).toEqual([]);
  });

  it("only enables scope approval at the explicit safe gate", () => {
    expect(
      canApproveScope({ task_id: "t", status: "awaiting_scope_approval", busy: false }),
    ).toBe(true);
    expect(canApproveScope({ task_id: "t", status: "implementing", busy: false })).toBe(false);
    expect(
      canApproveScope({
        task_id: "t",
        status: "awaiting_scope_approval",
        busy: true,
      } as TaskSnapshot),
    ).toBe(false);
  });

  it("selects the latest active persisted Program execution binding", () => {
    const execution = executionSnapshot({ requires_explicit_action: true });
    execution.bindings = [
      {
        program_id: "program-1",
        phase_id: "phase-1",
        slice_id: null,
        task_id: "task-completed",
        thread_id: "thread-completed",
        requirement_hash: "a".repeat(64),
        status: "completed",
        safe_status: "completed",
        result_ref: "artifact://completed.json",
        phase_report_ref: "artifact://phase-1.json",
        error_ref: "",
        accepted_evidence_ref: "",
        accepted_evidence_hash: "",
        expected_base_sha: "",
        remote_disposition_ref: "",
      },
      {
        program_id: "program-1",
        phase_id: "phase-2",
        slice_id: "slice-1",
        task_id: "task-active",
        thread_id: "thread-active",
        requirement_hash: "a".repeat(64),
        status: "awaiting_scope_approval",
        safe_status: "awaiting_scope_approval",
        result_ref: "artifact://awaiting.json",
        phase_report_ref: "artifact://phase-2.json",
        error_ref: "",
        accepted_evidence_ref: "artifact://accepted-phase-1.json",
        accepted_evidence_hash: "b".repeat(64),
        expected_base_sha: "c".repeat(40),
        remote_disposition_ref: "",
      },
    ];

    expect(activeProgramExecutionBinding(execution)?.task_id).toBe("task-active");
  });

  it("starts only from a loaded running Program with no active work", () => {
    expect(canStartProgramExecution(runningProgram, executionSnapshot())).toBe(true);
    expect(
      canStartProgramExecution(
        runningProgram,
        executionSnapshot({ busy: true }),
      ),
    ).toBe(false);
    expect(
      canStartProgramExecution(
        { ...runningProgram, status: "paused" },
        executionSnapshot(),
      ),
    ).toBe(false);
  });

  it("continues only after an explicit action is required for an active binding", () => {
    const execution = executionSnapshot({ requires_explicit_action: true });
    execution.bindings = [
      {
        program_id: "program-1",
        phase_id: "phase-1",
        slice_id: null,
        task_id: "task-active",
        thread_id: "thread-active",
        requirement_hash: "a".repeat(64),
        status: "awaiting_scope_approval",
        safe_status: "awaiting_scope_approval",
        result_ref: "artifact://awaiting.json",
        phase_report_ref: "artifact://phase-1.json",
        error_ref: "",
        accepted_evidence_ref: "",
        accepted_evidence_hash: "",
        expected_base_sha: "",
        remote_disposition_ref: "",
        control: {
          state: "running",
          reason: "",
          revision: 0,
        },
      },
    ];

    expect(canContinueProgramExecution(runningProgram, execution)).toBe(true);
    execution.runtime.requires_explicit_action = false;
    expect(canContinueProgramExecution(runningProgram, execution)).toBe(false);
    execution.runtime.requires_explicit_action = true;
    execution.bindings[0].control = {
      state: "cancel_requested",
      reason: "operator cancelled",
      revision: 1,
    };
    expect(canContinueProgramExecution(runningProgram, execution)).toBe(false);
  });

  it("reports the bounded outcome after an owned process is no longer active", () => {
    const evidence = cancellationEvidencePresentation(
      cancellationReport({
        active_operation_kinds: ["test"],
        owned_processes_observed: 1,
        terminate_requests: 1,
      }),
    );

    expect(evidence).toEqual({
      label: "No owned work remained active",
      summary:
        "The bounded cancellation window ended with no registered owned process or handle still active.",
      tone: "good",
    });
  });

  it("labels cancellation without an owned termination contract as cooperative", () => {
    const evidence = cancellationEvidencePresentation(
      cancellationReport({ cooperative_fallback: true }),
    );

    expect(evidence.label).toBe("Cooperative fallback");
    expect(evidence.tone).toBe("warn");
    expect(evidence.summary).toContain("provider and test checkpoints");
  });

  it("surfaces an unresponsive owned handle without claiming termination", () => {
    const evidence = cancellationEvidencePresentation(
      cancellationReport({
        owned_cancellable_operations_observed: 1,
        cancellable_operation_cancel_requests: 1,
        cancellable_operations_still_active: 1,
      }),
    );

    expect(evidence.label).toBe("Owned work still active");
    expect(evidence.tone).toBe("bad");
    expect(evidence.summary).toContain("1 registered owned operation still active");
  });

  it("presents a recovered active lease without implying provider work", () => {
    const presentation = remoteOperationPresentation(remoteOperation());

    expect(presentation).toEqual({
      label: "Recovered remote operation",
      summary:
        "A redacted durable lease was recovered. Loading this view made no provider request; observe or cancel requires an explicit action.",
      tone: "warn",
    });
    expect(canReconcileRemoteOperation(remoteOperation())).toBe(true);
    expect(canReconcileRemoteOperation(remoteOperation(), true)).toBe(false);
  });

  it("does not claim termination while remote cancellation remains pending", () => {
    const operation = remoteOperation({
      cancellation_requested: true,
      cancel_requests: 1,
      last_action: "cancel",
    });
    const presentation = remoteOperationPresentation(operation);

    expect(presentation.label).toBe("Remote cancellation pending");
    expect(presentation.tone).toBe("bad");
    expect(presentation.summary).toContain("termination has not been confirmed");
    expect(canReconcileRemoteOperation(operation)).toBe(true);
  });

  it("claims remote cancellation only for a provider-confirmed terminal state", () => {
    const operation = remoteOperation({
      state: "terminal",
      last_status: "cancelled",
      cancellation_requested: true,
      requires_explicit_action: false,
      requires_explicit_disposition: true,
    });
    const presentation = remoteOperationPresentation(operation);

    expect(presentation.label).toBe("Provider confirmed cancellation");
    expect(presentation.tone).toBe("good");
    expect(presentation.summary).toContain("did not recover output or resume the graph");
    expect(canReconcileRemoteOperation(operation)).toBe(false);
  });

  it("keeps non-cancelled terminal output outside recovery", () => {
    const presentation = remoteOperationPresentation(
      remoteOperation({
        state: "terminal",
        last_status: "completed",
        requires_explicit_action: false,
        requires_explicit_disposition: true,
      }),
    );

    expect(presentation.label).toBe("Provider reported terminal state");
    expect(presentation.tone).toBe("neutral");
    expect(presentation.summary).toContain("did not consume output");
  });

  it("fails closed when the remote lifecycle is unavailable", () => {
    const operation = remoteOperation({
      state: "unavailable",
      last_status: "remote_state_unavailable",
      requires_explicit_action: false,
      requires_explicit_disposition: true,
    });
    const presentation = remoteOperationPresentation(operation);

    expect(presentation.label).toBe("Remote state unavailable");
    expect(presentation.tone).toBe("bad");
    expect(presentation.summary).toContain("Do not infer completion or termination");
    expect(canReconcileRemoteOperation(operation)).toBe(false);
  });

  it("enables disposition only for an undisposed terminal or unavailable lease", () => {
    const terminal = remoteOperation({
      state: "terminal",
      last_status: "cancelled",
      requires_explicit_action: false,
      requires_explicit_disposition: true,
    });

    expect(canDisposeRemoteOperation(terminal)).toBe(true);
    expect(canDisposeRemoteOperation(terminal, undefined, true)).toBe(false);
    expect(canDisposeRemoteOperation(terminal, remoteDisposition())).toBe(false);
    expect(canDisposeRemoteOperation(remoteOperation())).toBe(false);
  });

  it("keeps unavailable disposition distinct from confirmed termination", () => {
    const presentation = remoteOperationDispositionPresentation(
      remoteDisposition({
        outcome: "failed",
        remote_state: "unavailable",
        remote_status: "remote_state_unavailable",
        provider_confirmed_cancelled: false,
      }),
    );

    expect(presentation.label).toBe("Task closed as failed");
    expect(presentation.tone).toBe("bad");
    expect(presentation.summary).toContain(
      "does not confirm provider completion or termination",
    );
  });

  it("describes provider-confirmed cancellation without broadening recovery", () => {
    const presentation = remoteOperationDispositionPresentation(remoteDisposition());

    expect(presentation.label).toBe("Task closed as cancelled");
    expect(presentation.tone).toBe("good");
    expect(presentation.summary).toContain(
      "did not consume output, resume the graph, or advance a Program phase",
    );
  });

  it("enables retirement only for an exact disposed non-active lease", () => {
    const terminal = remoteOperation({
      state: "terminal",
      last_status: "cancelled",
      revision: 2,
      requires_explicit_action: false,
      requires_explicit_disposition: false,
    });
    const disposition = remoteDisposition();

    expect(canRetireRemoteOperationLease(terminal, disposition)).toBe(true);
    expect(
      canRetireRemoteOperationLease(terminal, disposition, undefined, true),
    ).toBe(false);
    expect(
      canRetireRemoteOperationLease(
        terminal,
        disposition,
        remoteLeaseRetirement(),
      ),
    ).toBe(false);
    expect(
      canRetireRemoteOperationLease(
        terminal,
        remoteDisposition({ remote_revision: 3 }),
      ),
    ).toBe(false);
    expect(canRetireRemoteOperationLease(remoteOperation(), disposition)).toBe(false);
  });

  it("presents logical local retirement without remote or forensic claims", () => {
    const terminal = remoteOperationLeaseRetirementPresentation(
      remoteLeaseRetirement(),
    );
    const unavailable = remoteOperationLeaseRetirementPresentation(
      remoteLeaseRetirement({
        remote_state: "unavailable",
        remote_status: "remote_state_unavailable",
      }),
    );

    expect(terminal.label).toBe("Local private lease retired");
    expect(terminal.summary).toContain(
      "retirement action made no provider call or Task/Program outcome change",
    );
    expect(terminal.summary).toContain("not a claim of forensic storage erasure or remote deletion");
    expect(unavailable.summary).toContain("does not confirm provider completion, termination");
  });

  it("keeps durable evidence visible after the private lease row is gone", () => {
    expect(
      hasRemoteOperationEvidence(
        undefined,
        remoteDisposition(),
        remoteLeaseRetirement(),
      ),
    ).toBe(true);
    expect(hasRemoteOperationEvidence()).toBe(false);
  });

  it("presents eligible inventory evidence as advisory without claiming retirement", () => {
    const presentation = retainedRemoteOperationLeaseEligibilityPresentation(
      retainedLeaseInventoryItem(),
    );

    expect(presentation.label).toBe("Eligible at this snapshot");
    expect(presentation.tone).toBe("good");
    expect(presentation.summary).toContain("Nothing was retired");
    expect(presentation.summary).toContain("revalidate all evidence");
    expect(presentation.reasons).toEqual([]);
  });

  it("maps every inventory blocker to fixed operator-safe copy", () => {
    const codes: RemoteOperationLeaseRetirementEligibilityCode[] = [
      "lifecycle_action_active",
      "local_worker_active",
      "active_private_lease",
      "disposition_audit_invalid",
      "lease_disposition_mismatch",
      "task_control_missing",
      "task_control_state_mismatch",
      "retirement_receipt_conflict",
      "retirement_receipt_invalid",
      "program_binding_missing",
      "program_binding_mismatch",
      "program_evidence_oversized",
      "program_evidence_incomplete",
    ];

    for (const code of codes) {
      const presentation = retainedRemoteOperationLeaseEligibilityPresentation(
        retainedLeaseInventoryItem({
          eligible_for_retirement: false,
          eligibility_reasons: [{ code, message: "untrusted server copy" }],
        }),
      );
      expect(presentation.label).toBe("Not eligible at this snapshot");
      expect(presentation.summary).toContain("No retirement was attempted");
      expect(presentation.reasons).toHaveLength(1);
      expect(presentation.reasons[0]).not.toBe("untrusted server copy");
    }
  });

  it("fails closed when inventory eligibility fields contradict each other", () => {
    const eligibleWithBlocker = retainedRemoteOperationLeaseEligibilityPresentation(
      retainedLeaseInventoryItem({
        eligibility_reasons: [
          { code: "local_worker_active", message: "A worker is active." },
        ],
      }),
    );
    const ineligibleWithoutBlocker = retainedRemoteOperationLeaseEligibilityPresentation(
      retainedLeaseInventoryItem({ eligible_for_retirement: false }),
    );

    expect(eligibleWithBlocker.label).toBe("Not eligible at this snapshot");
    expect(eligibleWithBlocker.summary).toContain("fails closed");
    expect(ineligibleWithoutBlocker.label).toBe("Not eligible at this snapshot");
    expect(ineligibleWithoutBlocker.reasons[0]).toContain("inconsistent");
  });

  it("fails closed on an unknown future inventory blocker", () => {
    const presentation = retainedRemoteOperationLeaseEligibilityPresentation(
      retainedLeaseInventoryItem({
        eligible_for_retirement: false,
        eligibility_reasons: [
          {
            code: "future_fail_closed_blocker" as RemoteOperationLeaseRetirementEligibilityCode,
            message: "untrusted future server copy",
          },
        ],
      }),
    );

    expect(presentation.label).toBe("Not eligible at this snapshot");
    expect(presentation.reasons).toEqual([
      "Unknown eligibility evidence was returned.",
    ]);
    expect(presentation.reasons).not.toContain("untrusted future server copy");
  });

  it("keeps unavailable inventory state free of termination or deletion claims", () => {
    const presentation = retainedRemoteOperationLeaseEligibilityPresentation(
      retainedLeaseInventoryItem({
        remote_state: "unavailable",
        remote_status: "remote_state_unavailable",
      }),
    );

    expect(presentation.stateWarning).toContain("does not confirm provider completion");
    expect(presentation.stateWarning).toContain("termination");
    expect(presentation.stateWarning).toContain("remote deletion");
  });
});
