#!/usr/bin/env node

import { appendFile, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

function argument(name) {
  const index = process.argv.indexOf(name);
  return index === -1 ? null : process.argv[index + 1];
}

async function emit(value) {
  process.stdout.write(`${JSON.stringify({ structured_output: value })}\n`);
}

const role = process.env.LCAC_ROLE;
const mode = process.env.FAKE_CLAUDE_MODE ?? "pass";
const task = JSON.parse(await readFile(process.env.LCAC_TASK_CONTRACT, "utf8"));
const projectRoot = process.env.LCAC_PROJECT_ROOT;
const prompt = process.argv.at(-1) ?? "";

if (process.env.FAKE_CLAUDE_LOG) await appendFile(process.env.FAKE_CLAUDE_LOG, `${role}\n`);

if (role === "planner") {
  if (mode === "transient-planner") {
    const marker = process.env.FAKE_CLAUDE_MARKER;
    try {
      await readFile(marker);
    } catch {
      await writeFile(marker, "failed-once\n");
      process.stderr.write("simulated planner transport failure\n");
      process.exit(9);
    }
  }
  if (mode === "planner-mutation") await writeFile(path.join(projectRoot, "planner-mutation.txt"), "read-only role mutated source\n");
  await emit({
    role: "planner",
    status: "PASS",
    taskId: task.taskId,
    baseSha: task.expectedBaseSha,
    summary: "Bounded plan",
    planSteps: ["Implement the approved source and documentation changes."],
    predictedPaths: ["src/example/feature.js", "docs/example.md"],
    checkIds: task.requiredChecks,
    roadmapAlignment: "PASS",
    architectureAlignment: "PASS",
    assumptions: [],
    blockers: [],
  });
} else if (role === "implementer") {
  await mkdir(path.join(projectRoot, "src", "example"), { recursive: true });
  await mkdir(path.join(projectRoot, "docs"), { recursive: true });
  await writeFile(path.join(projectRoot, "src", "example", "feature.js"), "export const feature = true;\n");
  await writeFile(path.join(projectRoot, "docs", "example.md"), "# Example feature\n");
  if (mode === "escape") await writeFile(path.join(projectRoot, "escape.txt"), "unauthorized\n");
  if (mode === "ignored-escape") {
    await mkdir(path.join(projectRoot, "ignored"), { recursive: true });
    await writeFile(path.join(projectRoot, "ignored", "secret.txt"), "ignored but observable\n");
  }
  await emit({
    role: "implementer",
    status: "PASS",
    taskId: task.taskId,
    baseSha: task.expectedBaseSha,
    summary: "Implemented bounded change",
    declaredChangedPaths: mode === "mismatch" ? ["src/example/feature.js"] : ["src/example/feature.js", "docs/example.md"],
    requestedCheckIds: task.requiredChecks,
    blockers: [],
  });
} else if (role === "verifier") {
  const digest = prompt.match(/===== CANONICAL DIFF DIGEST =====\n([0-9a-f]{64})/)?.[1];
  if (mode === "verifier-mutation") await writeFile(path.join(projectRoot, "docs", "example.md"), "# Mutated by verifier\n");
  await emit({
    role: "verifier",
    verdict: "PASS",
    taskId: task.taskId,
    baseSha: task.expectedBaseSha,
    reviewedDiffSha256: digest,
    requirements: task.acceptanceCriteria.map((criterion) => ({ criterion, status: "PASS", evidence: "Canonical diff and deterministic check evidence satisfy the criterion." })),
    qualityFindings: [],
    securityFindings: [],
    remainingRisks: [],
    documentationStatus: task.requiresDocumentation ? "PASS" : "NOT_REQUIRED",
    independent: true,
  });
} else {
  process.stderr.write(`unexpected role ${role}; agent=${argument("--agent")}\n`);
  process.exit(10);
}
