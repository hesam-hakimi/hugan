import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { readRunStatus, resumeRun, startRun, validateRunInputs } from "../scripts/lib/orchestrator.mjs";
import { verifyHandoff } from "../scripts/lib/handoff.mjs";
import { CONTROL_ROOT, createFixture } from "./helpers.mjs";

function options(fixture) {
  return {
    pluginRoot: CONTROL_ROOT,
    project: fixture.project,
    configPath: fixture.configPath,
    milestonePath: fixture.milestonePath,
    taskPath: fixture.taskPath,
  };
}

async function withFakeEnvironment(fixture, mode, callback) {
  const previous = {
    mode: process.env.FAKE_CLAUDE_MODE,
    log: process.env.FAKE_CLAUDE_LOG,
    marker: process.env.FAKE_CLAUDE_MARKER,
  };
  process.env.FAKE_CLAUDE_MODE = mode;
  process.env.FAKE_CLAUDE_LOG = fixture.fakeLog;
  process.env.FAKE_CLAUDE_MARKER = fixture.marker;
  try {
    return await callback();
  } finally {
    if (previous.mode === undefined) delete process.env.FAKE_CLAUDE_MODE; else process.env.FAKE_CLAUDE_MODE = previous.mode;
    if (previous.log === undefined) delete process.env.FAKE_CLAUDE_LOG; else process.env.FAKE_CLAUDE_LOG = previous.log;
    if (previous.marker === undefined) delete process.env.FAKE_CLAUDE_MARKER; else process.env.FAKE_CLAUDE_MARKER = previous.marker;
  }
}

test("validation is read-only and binds task to exact Git identity", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const result = await validateRunInputs(options(fixture));
  assert.equal(result.valid, true);
  assert.equal(result.headSha, fixture.headSha);
  assert.equal(result.branch, "test-branch");
});

test("automatic Planner to Implementer to Verifier handoff reaches owner review", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const state = await withFakeEnvironment(fixture, "pass", () => startRun(options(fixture)));
  assert.equal(state.currentState, "DONE");
  assert.equal(state.final.result, "PASS_READY_FOR_OWNER_REVIEW");
  assert.deepEqual(state.final.changedPaths, ["docs/example.md", "src/example/feature.js"]);
  assert.equal(new Set(Object.values(state.sessions)).size, 3);
  assert.deepEqual(await fixture.readLog(), ["planner", "implementer", "verifier"]);
  assert.equal(state.final.commitCreated, false);
  assert.equal(state.final.pushExecuted, false);

  const key = await readFile(path.join(fixture.project, ".git", "lcac", "handoff.key"));
  for (const handoffPath of Object.values(state.handoffs)) {
    const handoff = JSON.parse(await readFile(handoffPath, "utf8"));
    assert.equal(verifyHandoff(handoff, key), true);
  }
  const status = await readRunStatus({ project: fixture.project, runId: state.runId });
  assert.equal(status.currentState, "DONE");
});

test("post-edit Git boundary blocks a lying implementer before checks or verification", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const state = await withFakeEnvironment(fixture, "escape", () => startRun(options(fixture)));
  assert.equal(state.currentState, "BLOCKED");
  assert.match(state.blockReason, /Unauthorized changed path: escape.txt/);
  assert.equal(state.resumeAllowed, false);
  assert.deepEqual(await fixture.readLog(), ["planner", "implementer"]);
});

test("read-only Planner mutation blocks before Implementer launch", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const state = await withFakeEnvironment(fixture, "planner-mutation", () => startRun(options(fixture)));
  assert.equal(state.currentState, "BLOCKED");
  assert.match(state.blockReason, /Planner process mutated the worktree/);
  assert.equal(state.resumeAllowed, false);
  assert.deepEqual(await fixture.readLog(), ["planner"]);
});

test("full worktree snapshot detects unauthorized ignored-file mutation", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const state = await withFakeEnvironment(fixture, "ignored-escape", () => startRun(options(fixture)));
  assert.equal(state.currentState, "BLOCKED");
  assert.match(state.blockReason, /Unauthorized changed path: ignored\/secret.txt/);
  assert.equal(state.resumeAllowed, false);
  assert.deepEqual(await fixture.readLog(), ["planner", "implementer"]);
});

test("declaration mismatch blocks before certification", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const state = await withFakeEnvironment(fixture, "mismatch", () => startRun(options(fixture)));
  assert.equal(state.currentState, "BLOCKED");
  assert.match(state.blockReason, /declaration disagrees with Git/);
  assert.deepEqual(await fixture.readLog(), ["planner", "implementer"]);
});

test("failed deterministic check blocks independent Verifier launch", async (t) => {
  const fixture = await createFixture({ failingCheck: true });
  t.after(fixture.cleanup);
  const state = await withFakeEnvironment(fixture, "pass", () => startRun(options(fixture)));
  assert.equal(state.currentState, "BLOCKED");
  assert.match(state.blockReason, /Required checks failed: unit/);
  assert.deepEqual(await fixture.readLog(), ["planner", "implementer"]);
});

test("a passing check that mutates an already-changed file is blocked", async (t) => {
  const fixture = await createFixture({ mutatingCheck: true });
  t.after(fixture.cleanup);
  const state = await withFakeEnvironment(fixture, "pass", () => startRun(options(fixture)));
  assert.equal(state.currentState, "BLOCKED");
  assert.match(state.blockReason, /Required checks mutated the repository worktree/);
  assert.deepEqual(await fixture.readLog(), ["planner", "implementer"]);
});

test("read-only Verifier mutation blocks final certification", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const state = await withFakeEnvironment(fixture, "verifier-mutation", () => startRun(options(fixture)));
  assert.equal(state.currentState, "BLOCKED");
  assert.match(state.blockReason, /Verifier process mutated the worktree/);
  assert.deepEqual(await fixture.readLog(), ["planner", "implementer", "verifier"]);
});

test("only a pre-mutation Planner transport failure can resume", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const first = await withFakeEnvironment(fixture, "transient-planner", () => startRun(options(fixture)));
  assert.equal(first.currentState, "BLOCKED");
  assert.equal(first.blockedAt, "PLANNING");
  assert.equal(first.resumeAllowed, true);
  const resumed = await withFakeEnvironment(fixture, "transient-planner", () => resumeRun({ pluginRoot: CONTROL_ROOT, project: fixture.project, runId: first.runId }));
  assert.equal(resumed.currentState, "DONE");
  assert.deepEqual(await fixture.readLog(), ["planner", "planner", "implementer", "verifier"]);
});
