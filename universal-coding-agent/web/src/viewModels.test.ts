import { describe, expect, it } from "vitest";

import type { ProgramSnapshot, RequirementContract, TaskSnapshot } from "./types";
import { canApproveScope, phaseProgress, statusTone, unresolvedClarifications } from "./viewModels";

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
});
