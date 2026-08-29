import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnCapture } from "../scripts/lib/util.mjs";

export const CONTROL_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const FAKE_CLAUDE = path.join(CONTROL_ROOT, "tests", "fixtures", "fake-claude.mjs");

export async function writeJson(filePath, value) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

async function git(project, args) {
  const result = await spawnCapture("git", args, { cwd: project, timeoutMs: 30_000 });
  if (result.code !== 0) throw new Error(`git ${args.join(" ")} failed: ${result.stderr}`);
  return result.stdout.trim();
}

export async function createFixture({ failingCheck = false, mutatingCheck = false } = {}) {
  const root = await mkdtemp(path.join(os.tmpdir(), "lcac-test-"));
  const project = path.join(root, "project");
  await mkdir(project, { recursive: true });
  await git(project, ["init", "-b", "test-branch"]);
  await git(project, ["config", "user.name", "LCAC Test"]);
  await git(project, ["config", "user.email", "lcac-test@example.invalid"]);

  const roadmap = {
    schemaVersion: "1.0",
    currentMilestone: "M1",
    milestones: [{ id: "M1", capabilities: [{ id: "CAP-001", status: "approved" }] }],
  };
  const architecture = {
    schemaVersion: "1.0",
    principles: [{ id: "ARCH-001", rule: "Maintain one source of truth." }],
  };
  const config = {
    schemaVersion: "1.0",
    runner: { command: process.execPath, prefixArgs: [FAKE_CLAUDE], model: "test-model", maxTurns: 10, maxBudgetUsd: 1 },
    productSources: { roadmap: "product/roadmap.json", architecture: "architecture/contract.json" },
    checks: {
      unit: {
        argv: [process.execPath, "-e", failingCheck ? "process.exit(7)" : mutatingCheck ? "require('node:fs').writeFileSync('src/example/feature.js', 'mutated by check\\n')" : "process.exit(0)"],
        cwd: ".",
        timeoutMs: 10_000,
      },
    },
    promptLimits: { maxSourceBytes: 20_000, maxDiffBytes: 20_000 },
  };
  const milestone = {
    schemaVersion: "1.0",
    milestoneId: "M1",
    objective: "Deliver one approved capability",
    approvedBy: "owner",
    approvedAt: "2026-08-29T00:00:00.000Z",
    approvedCapabilities: ["CAP-001"],
    authorizedPathEnvelope: ["src/**", "docs/**"],
    prohibitedPaths: [".git/**", "**/*.vsix"],
    allowedChecks: ["unit"],
    roadmapRefs: ["M1", "CAP-001"],
    architectureRefs: ["ARCH-001"],
  };

  const configPath = path.join(project, "governance", "lcac.config.json");
  const milestonePath = path.join(project, "governance", "milestones", "M1.json");
  await writeJson(path.join(project, "product", "roadmap.json"), roadmap);
  await writeJson(path.join(project, "architecture", "contract.json"), architecture);
  await writeJson(configPath, config);
  await writeJson(milestonePath, milestone);
  await mkdir(path.join(project, "src", "example"), { recursive: true });
  await writeFile(path.join(project, "src", "example", "existing.js"), "export const existing = true;\n");
  await writeFile(path.join(project, ".gitignore"), "ignored/\n");
  await git(project, ["add", "."]);
  await git(project, ["commit", "-m", "fixture baseline"]);
  const headSha = await git(project, ["rev-parse", "HEAD"]);

  const task = {
    schemaVersion: "1.0",
    taskId: "CAP-001-T1",
    milestoneId: "M1",
    capabilityId: "CAP-001",
    objective: "Implement the example feature",
    acceptanceCriteria: ["The feature and its documentation are present."],
    expectedBaseSha: headSha,
    roadmapRefs: ["M1", "CAP-001"],
    architectureRefs: ["ARCH-001"],
    authorizedPaths: ["src/example/**", "docs/example.md"],
    prohibitedPaths: [".git/**", "**/*.vsix"],
    requiredChecks: ["unit"],
    requiresDocumentation: true,
    documentationPaths: ["docs/example.md"],
    approvalClass: "milestone-preapproved",
  };
  const taskPath = path.join(root, "CAP-001-T1.json");
  await writeJson(taskPath, task);
  const fakeLog = path.join(root, "fake-claude.log");
  const marker = path.join(root, "planner-failed-once.marker");

  return {
    root,
    project,
    configPath,
    milestonePath,
    taskPath,
    config,
    milestone,
    task,
    headSha,
    fakeLog,
    marker,
    cleanup: async () => rm(root, { recursive: true, force: true }),
    readLog: async () => {
      try { return (await readFile(fakeLog, "utf8")).trim().split("\n").filter(Boolean); }
      catch { return []; }
    },
  };
}
