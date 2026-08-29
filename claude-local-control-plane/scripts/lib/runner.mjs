import { randomBytes, randomUUID } from "node:crypto";
import path from "node:path";
import { readJson, spawnCapture } from "./util.mjs";

const ROLE_TOOLS = {
  planner: "Read,Glob,Grep",
  implementer: "Read,Glob,Grep,Edit,Write",
  verifier: "Read,Glob,Grep",
};

const ROLE_SCHEMA = {
  planner: "planner-result.schema.json",
  implementer: "implementer-result.schema.json",
  verifier: "verifier-result.schema.json",
};

function extractStructuredOutput(payload) {
  if (payload && typeof payload === "object" && payload.structured_output && typeof payload.structured_output === "object") {
    return payload.structured_output;
  }
  if (payload && typeof payload === "object" && payload.result && typeof payload.result === "object") {
    return payload.result;
  }
  return payload;
}

export async function runClaudeRole({ pluginRoot, projectRoot, config, role, prompt, task, taskPath, sessionId = randomUUID() }) {
  if (!Object.hasOwn(ROLE_TOOLS, role)) throw new Error(`Unsupported role: ${role}`);
  const schema = await readJson(path.join(pluginRoot, "contracts", ROLE_SCHEMA[role]));
  const scopedAgent = `local-agent-control-plane:${role}`;
  const permissionMode = role === "implementer" ? "acceptEdits" : "default";
  const args = [
    ...config.runner.prefixArgs,
    "--print",
    "--plugin-dir",
    pluginRoot,
    "--agent",
    scopedAgent,
    "--output-format",
    "json",
    "--json-schema",
    JSON.stringify(schema),
    "--session-id",
    sessionId,
    "--no-session-persistence",
    "--setting-sources",
    "project",
    "--model",
    config.runner.model,
    "--max-turns",
    String(config.runner.maxTurns),
    "--max-budget-usd",
    String(config.runner.maxBudgetUsd),
    "--tools",
    ROLE_TOOLS[role],
    "--disallowedTools",
    "Bash,Agent,WebFetch,WebSearch,mcp__*",
    "--permission-mode",
    permissionMode,
    prompt,
  ];
  const env = {
    ...process.env,
    LCAC_ACTIVE: "1",
    LCAC_ROLE: role,
    LCAC_STAGE: role === "implementer" ? "IMPLEMENTING" : role === "planner" ? "PLANNING" : "VERIFYING",
    LCAC_PROJECT_ROOT: projectRoot,
    LCAC_TASK_CONTRACT: taskPath,
    LCAC_AUTHORIZED_PATHS: JSON.stringify(task.authorizedPaths),
    LCAC_PROHIBITED_PATHS: JSON.stringify(task.prohibitedPaths),
    LCAC_HOOK_NONCE: randomBytes(24).toString("hex"),
  };
  const execution = await spawnCapture(config.runner.command, args, {
    cwd: projectRoot,
    env,
    timeoutMs: 3_600_000,
    maxOutputBytes: 8_000_000,
  });
  if (execution.timedOut) throw new Error(`${role} process timed out`);
  if (execution.code !== 0) throw new Error(`${role} process failed (${execution.code}): ${execution.stderr.trim()}`);
  let payload;
  try {
    payload = JSON.parse(execution.stdout);
  } catch (error) {
    throw new Error(`${role} returned invalid JSON: ${error.message}`);
  }
  return {
    sessionId,
    structured: extractStructuredOutput(payload),
    raw: payload,
    stderr: execution.stderr,
  };
}
