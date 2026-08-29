import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { spawnCapture } from "../scripts/lib/util.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const HOOK = path.join(ROOT, "scripts", "hook-guard.mjs");

async function invoke(project, event, overrides = {}) {
  return await spawnCapture(process.execPath, [HOOK], {
    cwd: project,
    input: JSON.stringify(event),
    timeoutMs: 10_000,
    env: {
      ...process.env,
      LCAC_ACTIVE: "1",
      LCAC_HOOK_NONCE: "test-nonce",
      LCAC_PROJECT_ROOT: project,
      LCAC_ROLE: "implementer",
      LCAC_STAGE: "IMPLEMENTING",
      LCAC_AUTHORIZED_PATHS: JSON.stringify(["src/**"]),
      LCAC_PROHIBITED_PATHS: JSON.stringify(["src/private/**", ".git/**"]),
      ...overrides,
    },
  });
}

test("hook permits only implementer writes inside exact boundary", async (t) => {
  const project = await mkdtemp(path.join(os.tmpdir(), "lcac-hook-"));
  t.after(() => rm(project, { recursive: true, force: true }));
  await mkdir(path.join(project, "src"), { recursive: true });
  const allowed = await invoke(project, { tool_name: "Write", tool_input: { file_path: "src/allowed.js" } });
  assert.equal(allowed.code, 0);

  const outside = await invoke(project, { tool_name: "Write", tool_input: { file_path: "escape.txt" } });
  assert.equal(outside.code, 2);
  assert.match(outside.stderr, /outside task authorization/);

  const prohibited = await invoke(project, { tool_name: "Edit", tool_input: { file_path: "src/private/secret.js" } });
  assert.equal(prohibited.code, 2);
  assert.match(prohibited.stderr, /path is prohibited/);
});

test("hook blocks write-capable wrong roles, commands, nesting, and Git metadata", async (t) => {
  const project = await mkdtemp(path.join(os.tmpdir(), "lcac-hook-"));
  t.after(() => rm(project, { recursive: true, force: true }));
  await mkdir(path.join(project, ".git"), { recursive: true });

  const plannerWrite = await invoke(project, { tool_name: "Write", tool_input: { file_path: "src/a.js" } }, { LCAC_ROLE: "planner", LCAC_STAGE: "PLANNING" });
  assert.equal(plannerWrite.code, 2);
  assert.match(plannerWrite.stderr, /writes require implementer/);

  for (const tool of ["Bash", "Agent", "WebFetch", "WebSearch"]) {
    const result = await invoke(project, { tool_name: tool, tool_input: {} });
    assert.equal(result.code, 2, `${tool} should be blocked`);
  }

  const gitRead = await invoke(project, { tool_name: "Read", tool_input: { file_path: ".git/config" } });
  assert.equal(gitRead.code, 2);
  assert.match(gitRead.stderr, /Git metadata is protected/);

  for (const tool of ["Glob", "Grep"]) {
    const outsideSearch = await invoke(project, { tool_name: tool, tool_input: { path: os.tmpdir(), pattern: tool === "Glob" ? "**/*" : "needle" } });
    assert.equal(outsideSearch.code, 2, `${tool} outside the project should be blocked`);
    assert.match(outsideSearch.stderr, /outside the project/);
  }

  const escapingGlob = await invoke(project, { tool_name: "Glob", tool_input: { pattern: "../**/*" } });
  assert.equal(escapingGlob.code, 2);
  assert.match(escapingGlob.stderr, /must remain inside the project/);
});

test("hook is inert for ordinary non-control-plane Claude use", async (t) => {
  const project = await mkdtemp(path.join(os.tmpdir(), "lcac-hook-"));
  t.after(() => rm(project, { recursive: true, force: true }));
  const result = await spawnCapture(process.execPath, [HOOK], {
    cwd: project,
    input: JSON.stringify({ tool_name: "Bash", tool_input: { command: "echo ordinary" } }),
    env: { ...process.env, LCAC_ACTIVE: "0" },
  });
  assert.equal(result.code, 0);
});
