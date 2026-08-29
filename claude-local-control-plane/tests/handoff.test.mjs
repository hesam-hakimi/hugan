import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { createHandoff, ensureSigningKey, verifyHandoff } from "../scripts/lib/handoff.mjs";

test("handoff is signed, durable, and tamper-evident", async (t) => {
  const root = await mkdtemp(path.join(os.tmpdir(), "lcac-handoff-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  const key = await ensureSigningKey(path.join(root, "state"));
  const issued = await createHandoff({
    runDir: path.join(root, "run"), runId: "run-1", taskId: "task-1",
    fromRole: "planner", toRole: "implementer", fromSessionId: "session-planner", toSessionId: "session-implementer",
    baseSha: "a".repeat(40), taskDigest: "b".repeat(64), artifactDigests: { planner: "c".repeat(64) }, key,
  });
  assert.equal(verifyHandoff(issued.handoff, key), true);
  const disk = JSON.parse(await readFile(issued.filePath, "utf8"));
  assert.equal(verifyHandoff(disk, key), true);
  assert.equal(verifyHandoff({ ...disk, toRole: "verifier" }, key), false);
});

test("handoff rejects same role or session identity", async (t) => {
  const root = await mkdtemp(path.join(os.tmpdir(), "lcac-handoff-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  const key = await ensureSigningKey(path.join(root, "state"));
  const base = { runDir: path.join(root, "run"), runId: "r", taskId: "t", baseSha: "a".repeat(40), taskDigest: "b".repeat(64), artifactDigests: {}, key };
  await assert.rejects(createHandoff({ ...base, fromRole: "planner", toRole: "planner", fromSessionId: "a", toSessionId: "b" }), /roles must be distinct/);
  await assert.rejects(createHandoff({ ...base, fromRole: "planner", toRole: "implementer", fromSessionId: "same", toSessionId: "same" }), /session IDs must be distinct/);
});
