import { truncateUtf8 } from "./util.mjs";

function block(label, value) {
  return `\n===== ${label} =====\n${typeof value === "string" ? value : JSON.stringify(value, null, 2)}\n`;
}

export function plannerPrompt({ task, milestone, roadmap, architecture, maxSourceBytes }) {
  return [
    "Plan the supplied task under the frozen contracts. Do not edit or run commands. Return the required structured planner result.",
    block("TASK CONTRACT", task),
    block("MILESTONE CONTRACT", milestone),
    block("PRODUCT ROADMAP", truncateUtf8(JSON.stringify(roadmap, null, 2), maxSourceBytes)),
    block("ARCHITECTURE CONTRACT", truncateUtf8(JSON.stringify(architecture, null, 2), maxSourceBytes)),
    "A PASS is allowed only when predicted paths are within task.authorizedPaths, checkIds exactly equal task.requiredChecks, roadmapAlignment is PASS, architectureAlignment is PASS, and blockers is empty.",
  ].join("\n");
}

export function implementerPrompt({ task, milestone, plan, roadmap, architecture, maxSourceBytes }) {
  return [
    "Implement exactly one approved task. Use file tools only. Do not run tests or Git. Return the required structured implementer result.",
    block("TASK CONTRACT", task),
    block("MILESTONE CONTRACT", milestone),
    block("APPROVED PLANNER RESULT", plan),
    block("PRODUCT ROADMAP", truncateUtf8(JSON.stringify(roadmap, null, 2), maxSourceBytes)),
    block("ARCHITECTURE CONTRACT", truncateUtf8(JSON.stringify(architecture, null, 2), maxSourceBytes)),
    "If the correct change requires anything outside the contract, return BLOCKED before making that out-of-scope change.",
  ].join("\n");
}

export function verifierPrompt({ task, milestone, plan, implementer, diff, checks, roadmap, architecture, maxSourceBytes }) {
  return [
    "Independently review the exact canonical evidence. Do not edit or run commands. Return the required structured verifier result.",
    block("TASK CONTRACT", task),
    block("MILESTONE CONTRACT", milestone),
    block("PLANNER RESULT", plan),
    block("IMPLEMENTER DECLARATION", implementer),
    block("CANONICAL DIFF DIGEST", diff.digest),
    block("CANONICAL CHANGED PATHS", diff.changedPaths),
    block("CANONICAL PATCH", diff.patch),
    block("DETERMINISTIC CHECK RESULTS", checks),
    block("PRODUCT ROADMAP", truncateUtf8(JSON.stringify(roadmap, null, 2), maxSourceBytes)),
    block("ARCHITECTURE CONTRACT", truncateUtf8(JSON.stringify(architecture, null, 2), maxSourceBytes)),
    "Set reviewedDiffSha256 exactly to the supplied canonical digest. Report every acceptance criterion exactly once with concrete evidence.",
  ].join("\n");
}
