#!/usr/bin/env node

import path from "node:path";
import { matchesAny } from "./lib/glob.mjs";
import { assertResolvedInside, toRepoRelative } from "./lib/util.mjs";

function deny(message) {
  process.stderr.write(`LCAC_HOOK_BLOCKED: ${message}\n`);
  process.exit(2);
}

async function main() {
  if (process.env.LCAC_ACTIVE !== "1") return;
  if (!process.env.LCAC_HOOK_NONCE) deny("missing orchestrator hook nonce");
  process.stdin.setEncoding("utf8");
  let inputText = "";
  for await (const chunk of process.stdin) inputText += chunk;
  let event;
  try {
    event = JSON.parse(inputText);
  } catch (error) {
    deny(`invalid hook JSON: ${error.message}`);
  }
  const tool = event.tool_name ?? event.toolName;
  const toolInput = event.tool_input ?? event.toolInput ?? {};
  if (["Bash", "Agent", "WebFetch", "WebSearch"].includes(tool)) {
    deny(`${tool} is never authorized inside a governed role process`);
  }
  const projectRoot = process.env.LCAC_PROJECT_ROOT;
  if (!projectRoot) deny("missing project root");
  const rawPath = toolInput.file_path ?? toolInput.path ?? toolInput.notebook_path;
  const pattern = toolInput.pattern;
  if (["Glob", "Grep"].includes(tool)) {
    if (rawPath) {
      try {
        const relativeSearchRoot = toRepoRelative(projectRoot, rawPath);
        await assertResolvedInside(projectRoot, rawPath);
        if (relativeSearchRoot === ".git" || relativeSearchRoot.startsWith(".git/")) deny(`${tool} cannot inspect Git metadata`);
      } catch (error) {
        deny(error.message);
      }
    }
    if (tool === "Glob" && typeof pattern === "string") {
      const slashPattern = pattern.replaceAll("\\", "/");
      if (slashPattern.startsWith("/") || /^[A-Za-z]:\//.test(slashPattern) || slashPattern.split("/").includes("..")) deny("Glob pattern must remain inside the project");
      if (slashPattern.split("/").includes(".git")) deny("Glob cannot inspect Git metadata");
    }
    return;
  }
  if (!rawPath) return;
  let relative;
  try {
    relative = toRepoRelative(projectRoot, rawPath);
    await assertResolvedInside(projectRoot, rawPath);
  } catch (error) {
    deny(error.message);
  }
  if (relative === ".git" || relative.startsWith(".git/")) deny("Git metadata is protected");
  if (tool === "Read") return;
  if (!["Edit", "Write", "NotebookEdit"].includes(tool)) return;
  if (process.env.LCAC_ROLE !== "implementer" || process.env.LCAC_STAGE !== "IMPLEMENTING") {
    deny(`writes require implementer role in IMPLEMENTING stage; role=${process.env.LCAC_ROLE} stage=${process.env.LCAC_STAGE}`);
  }
  let authorized;
  let prohibited;
  try {
    authorized = JSON.parse(process.env.LCAC_AUTHORIZED_PATHS ?? "[]");
    prohibited = JSON.parse(process.env.LCAC_PROHIBITED_PATHS ?? "[]");
  } catch (error) {
    deny(`invalid path policy environment: ${error.message}`);
  }
  if (!Array.isArray(authorized) || !Array.isArray(prohibited)) deny("path policies must be arrays");
  if (!matchesAny(relative, authorized)) deny(`path is outside task authorization: ${relative}`);
  if (matchesAny(relative, prohibited)) deny(`path is prohibited: ${relative}`);
}

main().catch((error) => deny(error.message));
