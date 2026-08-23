import { describe, expect, it } from "vitest";

import type {
  ProgramExecutionSnapshot,
  ProgramSnapshot,
  RequirementContract,
  TaskSnapshot,
} from "./types";
import {
  activeProgramExecutionBinding,
  canApproveScope,
  canContinueProgramExecution,
  canStartProgramExecution,
  phaseProgress,
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
});
