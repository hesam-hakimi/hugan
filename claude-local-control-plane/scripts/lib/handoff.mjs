import { createHmac, randomBytes } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { stableStringify, writeJsonAtomic } from "./util.mjs";

export async function ensureSigningKey(stateRoot) {
  const keyPath = path.join(stateRoot, "handoff.key");
  await mkdir(stateRoot, { recursive: true });
  try {
    const existing = await readFile(keyPath);
    if (existing.length < 32) throw new Error("Existing handoff key is too short");
    return existing;
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }
  const key = randomBytes(48);
  try {
    await writeFile(keyPath, key, { flag: "wx", mode: 0o600 });
    return key;
  } catch (error) {
    if (error.code !== "EEXIST") throw error;
    return await readFile(keyPath);
  }
}

function payloadForSignature(handoff) {
  const { signature: _signature, ...payload } = handoff;
  return payload;
}

export function signHandoff(handoff, key) {
  const payload = payloadForSignature(handoff);
  return {
    ...payload,
    signature: createHmac("sha256", key).update(stableStringify(payload)).digest("hex"),
  };
}

export function verifyHandoff(handoff, key) {
  if (!handoff || typeof handoff.signature !== "string") return false;
  const expected = createHmac("sha256", key)
    .update(stableStringify(payloadForSignature(handoff)))
    .digest("hex");
  const actual = handoff.signature;
  if (expected.length !== actual.length) return false;
  let difference = 0;
  for (let index = 0; index < expected.length; index += 1) difference |= expected.charCodeAt(index) ^ actual.charCodeAt(index);
  return difference === 0;
}

export async function createHandoff({ runDir, runId, taskId, fromRole, toRole, fromSessionId, toSessionId, baseSha, taskDigest, artifactDigests, key }) {
  if (fromRole === toRole) throw new Error("Handoff source and destination roles must be distinct");
  if (typeof toSessionId !== "string" || toSessionId.length === 0) throw new Error("Handoff destination session ID is required");
  if (fromSessionId !== null && fromSessionId === toSessionId) throw new Error("Handoff source and destination session IDs must be distinct");
  const unsigned = {
    schemaVersion: "1.0",
    runId,
    taskId,
    fromRole,
    toRole,
    fromSessionId,
    toSessionId,
    baseSha,
    taskDigest,
    artifactDigests,
    issuedAt: new Date().toISOString(),
    nonce: randomBytes(24).toString("hex"),
  };
  const handoff = signHandoff(unsigned, key);
  const filePath = path.join(runDir, "handoffs", `${fromRole}-to-${toRole}.json`);
  await writeJsonAtomic(filePath, handoff);
  return { handoff, filePath };
}
