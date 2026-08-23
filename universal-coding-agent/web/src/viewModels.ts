import type {
  CancellationReport,
  ProgramExecutionBinding,
  ProgramExecutionSnapshot,
  ProgramSnapshot,
  RequirementContract,
  TaskSnapshot,
} from "./types";

const activeExecutionStatuses = new Set(["starting", "awaiting_scope_approval", "running"]);

export type CancellationEvidencePresentation = {
  label: string;
  summary: string;
  tone: "good" | "warn" | "bad" | "neutral";
};

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
