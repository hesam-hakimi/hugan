import type { ProgramSnapshot, RequirementContract, TaskSnapshot } from "./types";

export function statusTone(status?: string): "good" | "warn" | "bad" | "neutral" {
  if (!status) return "neutral";
  if (["completed", "approved", "running", "ready_for_approval", "ok"].includes(status)) {
    return "good";
  }
  if (["paused", "awaiting_approval", "awaiting_scope_approval", "needs_clarification"].includes(status)) {
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
