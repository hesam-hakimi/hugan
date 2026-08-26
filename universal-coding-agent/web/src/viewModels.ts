import type {
  CancellationReport,
  ProgramExecutionBinding,
  ProgramExecutionSnapshot,
  ProgramSnapshot,
  RemoteOperationDisposition,
  RemoteOperationSnapshot,
  RequirementContract,
  TaskSnapshot,
} from "./types";

const activeExecutionStatuses = new Set(["starting", "awaiting_scope_approval", "running"]);

export type CancellationEvidencePresentation = {
  label: string;
  summary: string;
  tone: "good" | "warn" | "bad" | "neutral";
};

export type RemoteOperationPresentation = {
  label: string;
  summary: string;
  tone: "good" | "warn" | "bad" | "neutral";
};

export type RemoteOperationDispositionPresentation = {
  label: string;
  summary: string;
  tone: "good" | "warn" | "bad" | "neutral";
};

export function remoteOperationPresentation(
  operation: RemoteOperationSnapshot,
): RemoteOperationPresentation {
  if (operation.state === "unavailable") {
    return {
      label: "Remote state unavailable",
      summary:
        "Endpoint-scoped reconciliation could not establish a valid remote lifecycle state. Do not infer completion or termination.",
      tone: "bad",
    };
  }
  if (operation.state === "terminal") {
    if (operation.last_status === "cancelled") {
      return {
        label: "Provider confirmed cancellation",
        summary:
          "The provider reported terminal status cancelled. This confirms remote termination only; UCA did not recover output or resume the graph.",
        tone: "good",
      };
    }
    return {
      label: "Provider reported terminal state",
      summary: `The provider reported terminal status ${operation.last_status}. UCA did not consume output or resume the graph.`,
      tone: "neutral",
    };
  }
  if (operation.cancellation_requested) {
    return {
      label: "Remote cancellation pending",
      summary:
        "Cancellation intent is durable, but provider termination has not been confirmed. Explicit reconciliation is still required.",
      tone: "bad",
    };
  }
  if (operation.recovered_pending) {
    return {
      label: "Recovered remote operation",
      summary:
        "A redacted durable lease was recovered. Loading this view made no provider request; observe or cancel requires an explicit action.",
      tone: "warn",
    };
  }
  return {
    label: "Remote operation active",
    summary:
      "Provider state was last observed as active. No terminal outcome has been confirmed.",
    tone: "warn",
  };
}

export function canReconcileRemoteOperation(
  operation?: RemoteOperationSnapshot,
  blocked = false,
): boolean {
  return Boolean(
    operation &&
      operation.state === "active" &&
      operation.requires_explicit_action &&
      !blocked,
  );
}

export function canDisposeRemoteOperation(
  operation?: RemoteOperationSnapshot,
  disposition?: RemoteOperationDisposition,
  blocked = false,
): boolean {
  return Boolean(
    operation &&
      operation.state !== "active" &&
      operation.requires_explicit_disposition &&
      !disposition &&
      !blocked,
  );
}

export function remoteOperationDispositionPresentation(
  disposition: RemoteOperationDisposition,
): RemoteOperationDispositionPresentation {
  const outcome = disposition.outcome === "cancelled" ? "cancelled" : "failed";
  if (disposition.provider_confirmed_cancelled) {
    return {
      label: `Task closed as ${outcome}`,
      summary:
        "The provider had reported terminal cancellation. The operator disposition closed only UCA task state; it did not consume output, resume the graph, or advance a Program phase.",
      tone: disposition.outcome === "cancelled" ? "good" : "bad",
    };
  }
  if (disposition.remote_state === "unavailable") {
    return {
      label: `Task closed as ${outcome}`,
      summary:
        "Remote lifecycle state was unavailable. This audited operator disposition does not confirm provider completion or termination.",
      tone: "bad",
    };
  }
  return {
    label: `Task closed as ${outcome}`,
    summary: `The provider reported terminal status ${disposition.remote_status}. UCA did not consume remote output, resume the graph, or advance a Program phase.`,
    tone: disposition.outcome === "cancelled" ? "warn" : "bad",
  };
}

export function cancellationEvidencePresentation(
  report: CancellationReport,
): CancellationEvidencePresentation {
  const stillActive =
    report.processes_still_active + report.cancellable_operations_still_active;
  if (stillActive > 0) {
    return {
      label: "Owned work still active",
      summary: `The bounded cancellation window ended with ${stillActive} registered owned operation${stillActive === 1 ? "" : "s"} still active.`,
      tone: "bad",
    };
  }
  if (report.cooperative_fallback) {
    return {
      label: "Cooperative fallback",
      summary:
        "No actively terminable owned process or handle was registered; cancellation relies on provider and test checkpoints.",
      tone: "warn",
    };
  }
  const observed =
    report.owned_processes_observed +
    report.owned_cancellable_operations_observed;
  if (observed > 0) {
    return {
      label: "No owned work remained active",
      summary:
        "The bounded cancellation window ended with no registered owned process or handle still active.",
      tone: "good",
    };
  }
  return {
    label: "No owned work observed",
    summary:
      "The cancellation request found no registered owned process or handle.",
    tone: "neutral",
  };
}

export function statusTone(status?: string): "good" | "warn" | "bad" | "neutral" {
  if (!status) return "neutral";
  if (["completed", "approved", "running", "ready_for_approval", "ok"].includes(status)) {
    return "good";
  }
  if (
    [
      "paused",
      "pause_requested",
      "starting",
      "awaiting_approval",
      "awaiting_scope_approval",
      "needs_clarification",
    ].includes(status)
  ) {
    return "warn";
  }
  if (["failed", "cancelled", "blocked", "scope_rejected"].includes(status)) {
    return "bad";
  }
  return "neutral";
}

export function phaseProgress(program?: ProgramSnapshot): { completed: number; total: number } {
  if (!program) return { completed: 0, total: 0 };
  return {
    completed: program.phases.filter((phase) => phase.status === "completed").length,
    total: program.phases.length,
  };
}

export function unresolvedClarifications(contract?: RequirementContract) {
  if (!contract) return [];
  return contract.clarifications.filter(
    (item) =>
      (item.severity === "blocking" || item.severity === "material") &&
      !contract.answers[item.decision_key] &&
      !contract.answers[item.question_id],
  );
}

export function canApproveScope(task?: TaskSnapshot): boolean {
  return Boolean(
    task &&
      !task.busy &&
      ["awaiting_scope_approval", "indexed"].includes(task.status ?? ""),
  );
}

export function activeProgramExecutionBinding(
  execution?: ProgramExecutionSnapshot,
): ProgramExecutionBinding | undefined {
  return [...(execution?.bindings ?? [])]
    .reverse()
    .find((binding) => activeExecutionStatuses.has(binding.status));
}

export function canStartProgramExecution(
  program?: ProgramSnapshot,
  execution?: ProgramExecutionSnapshot,
): boolean {
  return Boolean(
    program &&
      execution &&
      program.program_id === execution.program_id &&
      program.status === "running" &&
      !execution.runtime.busy &&
      !execution.runtime.requires_explicit_action &&
      !activeProgramExecutionBinding(execution),
  );
}

export function canContinueProgramExecution(
  program?: ProgramSnapshot,
  execution?: ProgramExecutionSnapshot,
): boolean {
  const binding = activeProgramExecutionBinding(execution);
  return Boolean(
    program &&
      execution &&
      binding &&
      program.program_id === execution.program_id &&
      program.status === "running" &&
      !execution.runtime.busy &&
      execution.runtime.requires_explicit_action &&
      !["pause_requested", "paused", "cancel_requested", "cancelled"].includes(
        binding.control?.state ?? "",
      ),
  );
}
