#!/usr/bin/env node

import path from "node:path";
import { fileURLToPath } from "node:url";
import { readRunStatus, resumeRun, startRun, validateRunInputs } from "./lib/orchestrator.mjs";
import { parseCliArgs, requiredFlag, spawnCapture } from "./lib/util.mjs";
import { validateControlPlane } from "./validate-control-plane.mjs";

const PLUGIN_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function usage() {
  return `Local Claude Agent Control Plane

Usage:
  lcac validate --project <repo> --config <file> --milestone <file> --task <file>
  lcac run --project <repo> --config <file> --milestone <file> --task <file>
  lcac status --project <repo> [--run-id <id>]
  lcac resume --project <repo> --run-id <id>
  lcac verify-installation [--project <repo> --config <file> --milestone <file> --task <file>]

The run command performs automatic Planner -> Implementer -> checks -> Verifier handoff.
It never commits, pushes, opens a PR, packages, installs, deploys, or starts runtime QA.
`;
}

function commonInput(flags) {
  return {
    pluginRoot: PLUGIN_ROOT,
    project: requiredFlag(flags, "project"),
    configPath: requiredFlag(flags, "config"),
    milestonePath: requiredFlag(flags, "milestone"),
    taskPath: requiredFlag(flags, "task"),
  };
}

async function verifyInstallation(flags) {
  const controlPlane = await validateControlPlane();
  const commands = {};
  for (const [name, command, args] of [
    ["node", process.execPath, ["--version"]],
    ["git", "git", ["--version"]],
    ["claude", "claude", ["--version"]],
  ]) {
    try {
      const result = await spawnCapture(command, args, { timeoutMs: 30_000, maxOutputBytes: 50_000 });
      commands[name] = { available: result.code === 0, output: (result.stdout || result.stderr).trim(), exitCode: result.code };
    } catch (error) {
      commands[name] = { available: false, error: error.message };
    }
  }
  let target = null;
  if (flags.project || flags.config || flags.milestone || flags.task) target = await validateRunInputs(commonInput(flags));
  return { result: commands.claude.available ? "LCAC_INSTALLATION_READY" : "LCAC_INSTALLATION_BLOCKED_CLAUDE_MISSING", controlPlane, commands, target };
}

async function main() {
  const { positional, flags } = parseCliArgs(process.argv.slice(2));
  const command = positional[0];
  if (!command || flags.help) {
    process.stdout.write(usage());
    return;
  }
  let result;
  if (command === "validate") {
    await validateControlPlane();
    result = await validateRunInputs(commonInput(flags));
  } else if (command === "run") {
    await validateControlPlane();
    result = await startRun(commonInput(flags));
  } else if (command === "status") {
    result = await readRunStatus({ project: requiredFlag(flags, "project"), runId: typeof flags["run-id"] === "string" ? flags["run-id"] : undefined });
  } else if (command === "resume") {
    result = await resumeRun({ pluginRoot: PLUGIN_ROOT, project: requiredFlag(flags, "project"), runId: requiredFlag(flags, "run-id") });
  } else if (command === "verify-installation") {
    result = await verifyInstallation(flags);
  } else {
    throw new Error(`Unknown command: ${command}\n${usage()}`);
  }
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (result?.currentState === "BLOCKED" || String(result?.result ?? "").includes("BLOCKED")) process.exitCode = 2;
}

main().catch((error) => {
  process.stderr.write(`LCAC_ERROR: ${error.message}\n`);
  process.exitCode = 1;
});
