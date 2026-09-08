import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { ProgramSourcePanel } from "./App";
import type { ProgramExecutionSnapshot, ProgramSnapshot, ProgramSourceStatus } from "./types";
import { canContinueProgramExecution, canStartProgramExecution } from "./viewModels";

function source(): Extract<ProgramSourceStatus, { status: "recorded" }> {
  const origin = {
    generation: 0, source_sha256: "0".repeat(64), predecessor_sha256: null,
    task_id: null, receipt_sha256: "1".repeat(64),
  };
  const accepted = {
    generation: 1, source_sha256: "2".repeat(64), predecessor_sha256: origin.source_sha256,
    task_id: "task-43", receipt_sha256: "3".repeat(64),
  };
  return {
    schema: "uca-program-source-status-1", program_id: "program-1", status: "recorded",
    automatic_execution: false, filesystem_verified: false, source_bytes_verified: false,
    current_authority_verified: false, matches_current_plan: true,
    origin: { repository_sha256: "4".repeat(64), git_commit_sha: "5".repeat(40),
      git_tree_sha: "6".repeat(40) },
    accepted, lineage: [origin, accepted],
    dispatches: [{
      operation_id: "7".repeat(32), task_id: "task-44", phase_id: "phase-2", generation: 1,
      source_sha256: accepted.source_sha256, state: "awaiting_scope_approval",
      execution_schema: "uca-program-source-dispatch-2", admission_sha256: "8".repeat(64),
      derived_git_commit_sha: "9".repeat(40), derived_git_tree_sha: "a".repeat(40),
      source_accepted: false,
    }],
  };
}

function execution(recorded?: ProgramSourceStatus): ProgramExecutionSnapshot {
  return {
    program_id: "program-1", program_status: "running", source: recorded,
    runtime: { busy: false, action: "", task_id: "", status: "idle", recovered_pending: false,
      requires_explicit_action: false, error_type: "", error: "" },
    bindings: [],
  };
}

const program = { program_id: "program-1", status: "running" } as ProgramSnapshot;

describe("recorded Program source", () => {
  it("separates origin Git, accepted lineage and derived execution Git", () => {
    const recorded = source();
    const html = renderToStaticMarkup(<ProgramSourcePanel source={recorded} />);
    expect(html).toContain("Recorded source history");
    expect(html).toContain(`Origin Git commit: ${recorded.origin.git_commit_sha}`);
    expect(html).toContain(`Accepted source SHA-256: ${recorded.accepted.source_sha256}`);
    expect(html).toContain(`Derived execution Git commit: ${recorded.dispatches[0].derived_git_commit_sha}`);
    expect(html).toContain("Generation 0");
    expect(html).toContain("Generation 1");
    expect(html).toContain("Source not accepted");
    expect(html).toContain("does not verify current source files or run work");
    expect(html).not.toContain("<button");
  });

  it("does not present terminal execution as source acceptance", () => {
    const recorded = source();
    recorded.dispatches[0].state = "terminal";
    let html = renderToStaticMarkup(<ProgramSourcePanel source={recorded} />);
    expect(html).toContain("Execution terminal · Source not accepted");
    recorded.dispatches[0].source_accepted = true;
    html = renderToStaticMarkup(<ProgramSourcePanel source={recorded} />);
    expect(html).toContain("Execution terminal · Source accepted");
  });

  it("explains absent history and old plans without implying recovery", () => {
    expect(renderToStaticMarkup(<ProgramSourcePanel />)).toContain("not supplied");
    const recorded = source();
    recorded.matches_current_plan = false;
    expect(renderToStaticMarkup(<ProgramSourcePanel source={recorded} />))
      .toContain("earlier requirement or plan");
    const empty: ProgramSourceStatus = { ...recorded, status: "uninitialized", origin: null,
      accepted: null, lineage: [], dispatches: [], matches_current_plan: null };
    expect(renderToStaticMarkup(<ProgramSourcePanel source={empty} />))
      .toContain("No cumulative source history");
  });

  it("allows legacy and generation-zero starts but blocks advanced or mismatched source", () => {
    expect(canStartProgramExecution(program, execution())).toBe(true);
    const recorded = source();
    expect(canStartProgramExecution(program, execution(recorded))).toBe(false);
    recorded.accepted = recorded.lineage[0];
    recorded.lineage = [recorded.accepted];
    recorded.dispatches = [];
    expect(canStartProgramExecution(program, execution(recorded))).toBe(true);
    recorded.matches_current_plan = false;
    expect(canStartProgramExecution(program, execution(recorded))).toBe(false);
  });

  it("disables v1 continuation for a recorded v2 task after reload", () => {
    const snapshot = execution(source());
    snapshot.runtime.requires_explicit_action = true;
    snapshot.runtime.recovered_pending = true;
    snapshot.bindings = [{
      program_id: "program-1", phase_id: "phase-2", slice_id: null, task_id: "task-44",
      thread_id: "thread-44", requirement_hash: "b".repeat(64), status: "awaiting_scope_approval",
      safe_status: "awaiting_scope_approval", result_ref: "", phase_report_ref: "",
      error_ref: "", accepted_evidence_ref: "", accepted_evidence_hash: "", expected_base_sha: "",
      remote_disposition_ref: "", control: { state: "running", reason: "", revision: 0 },
    }];
    expect(canContinueProgramExecution(program, snapshot)).toBe(false);
    snapshot.source = undefined;
    expect(canContinueProgramExecution(program, snapshot)).toBe(true);
  });
});
