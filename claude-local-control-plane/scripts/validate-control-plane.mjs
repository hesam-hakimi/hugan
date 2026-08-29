#!/usr/bin/env node

import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readJson } from "./lib/util.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function validateFrontmatter(filePath) {
  const text = await readFile(filePath, "utf8");
  assert(text.startsWith("---\n"), `${filePath} is missing YAML frontmatter`);
  const end = text.indexOf("\n---\n", 4);
  assert(end > 4, `${filePath} has unterminated YAML frontmatter`);
  const frontmatter = text.slice(4, end);
  assert(/^name:\s*\S+/m.test(frontmatter), `${filePath} frontmatter is missing name`);
  assert(/^description:\s*.+/m.test(frontmatter), `${filePath} frontmatter is missing description`);
  return { text, frontmatter };
}

async function listFiles(directory, suffix) {
  const entries = await readdir(directory, { withFileTypes: true });
  const output = [];
  for (const entry of entries) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) output.push(...(await listFiles(absolute, suffix)));
    else if (entry.isFile() && entry.name.endsWith(suffix)) output.push(absolute);
  }
  return output;
}

export async function validateControlPlane() {
  const plugin = await readJson(path.join(ROOT, ".claude-plugin", "plugin.json"));
  assert(plugin.name === "local-agent-control-plane", "plugin name must remain local-agent-control-plane");
  assert(/^\d+\.\d+\.\d+$/.test(plugin.version), "plugin version must be semver");

  const jsonFiles = await listFiles(ROOT, ".json");
  for (const filePath of jsonFiles) await readJson(filePath);

  for (const schemaName of [
    "workspace-config.schema.json",
    "milestone-contract.schema.json",
    "task-contract.schema.json",
    "planner-result.schema.json",
    "implementer-result.schema.json",
    "verifier-result.schema.json",
    "handoff.schema.json",
  ]) {
    const schema = await readJson(path.join(ROOT, "contracts", schemaName));
    assert(schema.type === "object", `${schemaName} must describe an object`);
    assert(schema.additionalProperties === false, `${schemaName} must fail closed on additional properties`);
    assert(Array.isArray(schema.required) && schema.required.length > 0, `${schemaName} must declare required fields`);
    for (const key of schema.required) assert(Object.hasOwn(schema.properties, key), `${schemaName} requires undefined property ${key}`);
  }

  const agents = await listFiles(path.join(ROOT, "agents"), ".md");
  assert(agents.length === 3, `expected exactly three maintainer agents, found ${agents.length}`);
  const agentDocuments = {};
  for (const filePath of agents) agentDocuments[path.basename(filePath, ".md")] = await validateFrontmatter(filePath);
  assert(agentDocuments.planner.frontmatter.includes("tools: Read, Glob, Grep"), "Planner tool set must remain read-only");
  assert(agentDocuments.verifier.frontmatter.includes("tools: Read, Glob, Grep"), "Verifier tool set must remain read-only");
  assert(agentDocuments.implementer.frontmatter.includes("tools: Read, Glob, Grep, Edit, Write"), "Implementer tool set is invalid");
  for (const [role, document] of Object.entries(agentDocuments)) {
    assert(/disallowedTools:.*Bash/.test(document.frontmatter), `${role} must explicitly disallow Bash`);
    assert(/disallowedTools:.*Agent/.test(document.frontmatter), `${role} must explicitly disallow nested Agent use`);
  }

  const skills = await listFiles(path.join(ROOT, "skills"), "SKILL.md");
  assert(skills.length >= 5, "expected at least five operational skills");
  for (const filePath of skills) await validateFrontmatter(filePath);

  const manifest = await readJson(path.join(ROOT, "contracts", "process-manifest.json"));
  assert(manifest.initialState === "INTAKE", "process must start at INTAKE");
  assert(manifest.roles.planner.mayWriteSource === false, "Planner must remain read-only");
  assert(manifest.roles.verifier.mayWriteSource === false, "Verifier must remain read-only");
  assert(manifest.roles.implementer.mayCertify === false, "Implementer cannot certify");
  assert(manifest.roles.verifier.mayCertify === true, "Verifier must own certification");
  assert(manifest.automaticHandoff.autoRepairLoops === 0, "automatic repair loops must remain disabled");
  for (const [state, targets] of Object.entries(manifest.transitions)) {
    assert(Array.isArray(targets), `transition list for ${state} must be an array`);
    for (const target of targets) assert(Object.hasOwn(manifest.transitions, target), `transition ${state} -> ${target} targets an unknown state`);
  }

  const hooks = await readJson(path.join(ROOT, "hooks", "hooks.json"));
  const hookCommand = hooks.hooks?.PreToolUse?.[0]?.hooks?.[0]?.command ?? "";
  assert(hookCommand.includes("${CLAUDE_PLUGIN_ROOT}"), "hook command must resolve through CLAUDE_PLUGIN_ROOT");
  assert(hooks.hooks.PreToolUse[0].matcher.includes("Bash"), "hook must cover Bash");
  assert(hooks.hooks.PreToolUse[0].matcher.includes("Edit"), "hook must cover Edit");

  return {
    result: "LCAC_CONTROL_PLANE_VALID",
    pluginVersion: plugin.version,
    jsonFiles: jsonFiles.length,
    agents: agents.length,
    skills: skills.length,
  };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  validateControlPlane()
    .then((result) => process.stdout.write(`${JSON.stringify(result, null, 2)}\n`))
    .catch((error) => {
      process.stderr.write(`LCAC_CONTROL_PLANE_INVALID: ${error.message}\n`);
      process.exitCode = 1;
    });
}
