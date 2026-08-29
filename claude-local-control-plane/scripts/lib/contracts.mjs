import { access } from "node:fs/promises";
import path from "node:path";
import { matchesAny, patternWithin } from "./glob.mjs";
import { normalizeRepoPath, readJson } from "./util.mjs";

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertObject(value, label) {
  assert(value && typeof value === "object" && !Array.isArray(value), `${label} must be an object`);
}

function assertKeys(value, required, allowed, label) {
  assertObject(value, label);
  for (const key of required) assert(Object.hasOwn(value, key), `${label} is missing ${key}`);
  for (const key of Object.keys(value)) assert(allowed.includes(key), `${label} has unsupported property ${key}`);
}

function assertString(value, label) {
  assert(typeof value === "string" && value.trim() !== "", `${label} must be a non-empty string`);
  assert(!value.includes("REPLACE_WITH"), `${label} still contains a template placeholder`);
}

function assertStringArray(value, label, { nonEmpty = false } = {}) {
  assert(Array.isArray(value), `${label} must be an array`);
  if (nonEmpty) assert(value.length > 0, `${label} must not be empty`);
  value.forEach((item, index) => assertString(item, `${label}[${index}]`));
  assert(new Set(value).size === value.length, `${label} must not contain duplicates`);
}

function assertPathPatterns(value, label, { nonEmpty = false } = {}) {
  assertStringArray(value, label, { nonEmpty });
  for (const pattern of value) {
    normalizeRepoPath(pattern);
    assert(!pattern.includes("\0"), `${label} contains a NUL byte`);
  }
}

function subset(child, parent, label) {
  for (const item of child) assert(parent.includes(item), `${label} is outside the milestone envelope: ${item}`);
}

function collectIds(value, output = new Set()) {
  if (Array.isArray(value)) {
    value.forEach((item) => collectIds(item, output));
  } else if (value && typeof value === "object") {
    for (const [key, item] of Object.entries(value)) {
      if ((key === "id" || key === "currentMilestone") && typeof item === "string") output.add(item);
      collectIds(item, output);
    }
  }
  return output;
}

export function validateWorkspaceConfig(config) {
  const allowed = ["schemaVersion", "runner", "productSources", "checks", "promptLimits"];
  assertKeys(config, ["schemaVersion", "runner", "productSources", "checks"], allowed, "workspace config");
  assert(config.schemaVersion === "1.0", "workspace config schemaVersion must be 1.0");
  assertKeys(config.runner, ["command", "prefixArgs", "model", "maxTurns", "maxBudgetUsd"], ["command", "prefixArgs", "model", "maxTurns", "maxBudgetUsd"], "runner");
  assertString(config.runner.command, "runner.command");
  assertStringArray(config.runner.prefixArgs, "runner.prefixArgs");
  assertString(config.runner.model, "runner.model");
  assert(Number.isInteger(config.runner.maxTurns) && config.runner.maxTurns > 0 && config.runner.maxTurns <= 100, "runner.maxTurns must be 1..100");
  assert(typeof config.runner.maxBudgetUsd === "number" && config.runner.maxBudgetUsd > 0, "runner.maxBudgetUsd must be positive");
  assertKeys(config.productSources, ["roadmap", "architecture"], ["roadmap", "architecture"], "productSources");
  normalizeRepoPath(config.productSources.roadmap);
  normalizeRepoPath(config.productSources.architecture);
  assertObject(config.checks, "checks");
  assert(Object.keys(config.checks).length > 0, "checks must not be empty");
  for (const [id, check] of Object.entries(config.checks)) {
    assertString(id, "check ID");
    assertKeys(check, ["argv", "cwd", "timeoutMs"], ["argv", "cwd", "timeoutMs"], `check ${id}`);
    assertStringArray(check.argv, `check ${id}.argv`, { nonEmpty: true });
    if (check.cwd !== ".") normalizeRepoPath(check.cwd);
    assert(Number.isInteger(check.timeoutMs) && check.timeoutMs >= 1000 && check.timeoutMs <= 3_600_000, `check ${id}.timeoutMs is invalid`);
  }
  if (config.promptLimits !== undefined) {
    assertKeys(config.promptLimits, [], ["maxSourceBytes", "maxDiffBytes"], "promptLimits");
  }
  return config;
}

export function validateMilestone(milestone) {
  const keys = ["schemaVersion", "milestoneId", "objective", "approvedBy", "approvedAt", "approvedCapabilities", "authorizedPathEnvelope", "prohibitedPaths", "allowedChecks", "roadmapRefs", "architectureRefs"];
  assertKeys(milestone, keys, keys, "milestone contract");
  assert(milestone.schemaVersion === "1.0", "milestone schemaVersion must be 1.0");
  for (const key of ["milestoneId", "objective", "approvedBy", "approvedAt"]) assertString(milestone[key], `milestone.${key}`);
  assert(!Number.isNaN(Date.parse(milestone.approvedAt)), "milestone.approvedAt must be an ISO date-time");
  assertStringArray(milestone.approvedCapabilities, "milestone.approvedCapabilities", { nonEmpty: true });
  assertPathPatterns(milestone.authorizedPathEnvelope, "milestone.authorizedPathEnvelope", { nonEmpty: true });
  assertPathPatterns(milestone.prohibitedPaths, "milestone.prohibitedPaths");
  assertStringArray(milestone.allowedChecks, "milestone.allowedChecks", { nonEmpty: true });
  assertStringArray(milestone.roadmapRefs, "milestone.roadmapRefs", { nonEmpty: true });
  assertStringArray(milestone.architectureRefs, "milestone.architectureRefs", { nonEmpty: true });
  assert(!milestone.authorizedPathEnvelope.some((item) => item === ".git/**" || item.startsWith(".git/")), "milestone cannot authorize .git");
  return milestone;
}

export function validateTask(task) {
  const keys = ["schemaVersion", "taskId", "milestoneId", "capabilityId", "objective", "acceptanceCriteria", "expectedBaseSha", "roadmapRefs", "architectureRefs", "authorizedPaths", "prohibitedPaths", "requiredChecks", "requiresDocumentation", "documentationPaths", "approvalClass"];
  assertKeys(task, keys, keys, "task contract");
  assert(task.schemaVersion === "1.0", "task schemaVersion must be 1.0");
  for (const key of ["taskId", "milestoneId", "capabilityId", "objective"]) assertString(task[key], `task.${key}`);
  assertStringArray(task.acceptanceCriteria, "task.acceptanceCriteria", { nonEmpty: true });
  assert(/^[0-9a-f]{40}$/.test(task.expectedBaseSha) && !/^0+$/.test(task.expectedBaseSha), "task.expectedBaseSha must be a non-zero lowercase 40-character SHA");
  assertStringArray(task.roadmapRefs, "task.roadmapRefs", { nonEmpty: true });
  assertStringArray(task.architectureRefs, "task.architectureRefs", { nonEmpty: true });
  assertPathPatterns(task.authorizedPaths, "task.authorizedPaths", { nonEmpty: true });
  assertPathPatterns(task.prohibitedPaths, "task.prohibitedPaths");
  assertStringArray(task.requiredChecks, "task.requiredChecks", { nonEmpty: true });
  assert(typeof task.requiresDocumentation === "boolean", "task.requiresDocumentation must be boolean");
  assertPathPatterns(task.documentationPaths, "task.documentationPaths", { nonEmpty: task.requiresDocumentation });
  assert(["milestone-preapproved", "task-specific"].includes(task.approvalClass), "task.approvalClass is invalid");
  assert(!task.authorizedPaths.some((item) => item === ".git/**" || item.startsWith(".git/")), "task cannot authorize .git");
  for (const documentationPath of task.documentationPaths) {
    assert(task.authorizedPaths.some((pattern) => matchesAny(documentationPath, [pattern]) || patternWithin(documentationPath, pattern)), `documentation path is not authorized: ${documentationPath}`);
    assert(!matchesAny(documentationPath, task.prohibitedPaths), `documentation path is prohibited: ${documentationPath}`);
  }
  return task;
}

export async function validateContractSet({ projectRoot, config, milestone, task, headSha }) {
  validateWorkspaceConfig(config);
  validateMilestone(milestone);
  validateTask(task);
  assert(task.milestoneId === milestone.milestoneId, "task milestoneId does not match the milestone contract");
  assert(milestone.approvedCapabilities.includes(task.capabilityId), `capability ${task.capabilityId} is not approved by the milestone`);
  subset(task.roadmapRefs, milestone.roadmapRefs, "task roadmapRefs");
  subset(task.architectureRefs, milestone.architectureRefs, "task architectureRefs");
  subset(task.requiredChecks, milestone.allowedChecks, "task requiredChecks");
  for (const checkId of task.requiredChecks) assert(Object.hasOwn(config.checks, checkId), `check ${checkId} is not configured`);
  for (const pattern of task.authorizedPaths) {
    assert(milestone.authorizedPathEnvelope.some((parent) => patternWithin(pattern, parent)), `task authorized path is outside milestone envelope: ${pattern}`);
  }
  for (const pattern of milestone.prohibitedPaths) {
    assert(task.prohibitedPaths.includes(pattern), `task must preserve milestone prohibited path: ${pattern}`);
  }
  for (const pattern of task.authorizedPaths) {
    assert(!matchesAny(pattern.replace(/[*?].*$/, "sentinel"), task.prohibitedPaths), `task path is both authorized and prohibited: ${pattern}`);
  }
  assert(task.expectedBaseSha === headSha, `base SHA mismatch: task=${task.expectedBaseSha} live=${headSha}`);
  const roadmapPath = path.resolve(projectRoot, normalizeRepoPath(config.productSources.roadmap));
  const architecturePath = path.resolve(projectRoot, normalizeRepoPath(config.productSources.architecture));
  await access(roadmapPath);
  await access(architecturePath);
  const roadmap = await readJson(roadmapPath);
  const architecture = await readJson(architecturePath);
  const roadmapIds = collectIds(roadmap);
  const architectureIds = collectIds(architecture);
  for (const ref of task.roadmapRefs) assert(roadmapIds.has(ref), `roadmap reference does not exist: ${ref}`);
  for (const ref of task.architectureRefs) assert(architectureIds.has(ref), `architecture reference does not exist: ${ref}`);
  assert(task.approvalClass === "milestone-preapproved", "automatic handoff requires milestone-preapproved task authority");
  return { roadmap, architecture, roadmapPath, architecturePath };
}

export function validatePlannerResult(result, task) {
  const keys = ["role", "status", "taskId", "baseSha", "summary", "planSteps", "predictedPaths", "checkIds", "roadmapAlignment", "architectureAlignment", "assumptions", "blockers"];
  assertKeys(result, keys, keys, "planner result");
  assert(result.role === "planner", "planner result role is invalid");
  assert(["PASS", "BLOCKED"].includes(result.status), "planner status is invalid");
  assert(result.taskId === task.taskId, "planner taskId mismatch");
  assert(result.baseSha === task.expectedBaseSha, "planner baseSha mismatch");
  assertString(result.summary, "planner.summary");
  assertStringArray(result.planSteps, "planner.planSteps", { nonEmpty: result.status === "PASS" });
  assertPathPatterns(result.predictedPaths, "planner.predictedPaths", { nonEmpty: result.status === "PASS" });
  assertStringArray(result.checkIds, "planner.checkIds", { nonEmpty: result.status === "PASS" });
  assert(["PASS", "BLOCKED"].includes(result.roadmapAlignment), "planner roadmapAlignment is invalid");
  assert(["PASS", "BLOCKED"].includes(result.architectureAlignment), "planner architectureAlignment is invalid");
  assertStringArray(result.assumptions, "planner.assumptions");
  assertStringArray(result.blockers, "planner.blockers");
  for (const filePath of result.predictedPaths) {
    assert(matchesAny(filePath, task.authorizedPaths), `planner predicted unauthorized path: ${filePath}`);
    assert(!matchesAny(filePath, task.prohibitedPaths), `planner predicted prohibited path: ${filePath}`);
  }
  assert(result.checkIds.length === task.requiredChecks.length && result.checkIds.every((id) => task.requiredChecks.includes(id)), "planner checkIds must exactly match task requiredChecks");
  if (result.status === "PASS") {
    assert(result.roadmapAlignment === "PASS", "planner cannot pass with blocked roadmap alignment");
    assert(result.architectureAlignment === "PASS", "planner cannot pass with blocked architecture alignment");
    assert(result.blockers.length === 0, "planner cannot pass with blockers");
  }
}

export function validateImplementerResult(result, task) {
  const keys = ["role", "status", "taskId", "baseSha", "summary", "declaredChangedPaths", "requestedCheckIds", "blockers"];
  assertKeys(result, keys, keys, "implementer result");
  assert(result.role === "implementer", "implementer result role is invalid");
  assert(["PASS", "BLOCKED"].includes(result.status), "implementer status is invalid");
  assert(result.taskId === task.taskId, "implementer taskId mismatch");
  assert(result.baseSha === task.expectedBaseSha, "implementer baseSha mismatch");
  assertString(result.summary, "implementer.summary");
  assertPathPatterns(result.declaredChangedPaths, "implementer.declaredChangedPaths");
  assertStringArray(result.requestedCheckIds, "implementer.requestedCheckIds");
  assertStringArray(result.blockers, "implementer.blockers");
  for (const filePath of result.declaredChangedPaths) {
    assert(matchesAny(filePath, task.authorizedPaths), `implementer declared unauthorized path: ${filePath}`);
    assert(!matchesAny(filePath, task.prohibitedPaths), `implementer declared prohibited path: ${filePath}`);
  }
  assert(result.requestedCheckIds.length === task.requiredChecks.length && result.requestedCheckIds.every((id) => task.requiredChecks.includes(id)), "implementer requestedCheckIds must exactly match task requiredChecks");
  if (result.status === "PASS") {
    assert(result.declaredChangedPaths.length > 0, "implementer PASS requires declared changed paths");
    assert(result.blockers.length === 0, "implementer cannot pass with blockers");
  }
}

export function validateVerifierResult(result, task, diffSha256) {
  const keys = ["role", "verdict", "taskId", "baseSha", "reviewedDiffSha256", "requirements", "qualityFindings", "securityFindings", "remainingRisks", "documentationStatus", "independent"];
  assertKeys(result, keys, keys, "verifier result");
  assert(result.role === "verifier", "verifier result role is invalid");
  assert(["PASS", "BLOCKED"].includes(result.verdict), "verifier verdict is invalid");
  assert(result.taskId === task.taskId, "verifier taskId mismatch");
  assert(result.baseSha === task.expectedBaseSha, "verifier baseSha mismatch");
  assert(result.reviewedDiffSha256 === diffSha256, "verifier reviewed a different diff digest");
  assert(result.independent === true, "verifier must assert independent=true");
  assert(Array.isArray(result.requirements), "verifier.requirements must be an array");
  assert(result.requirements.length === task.acceptanceCriteria.length, "verifier must not add or omit acceptance criteria");
  for (const [index, requirement] of result.requirements.entries()) {
    assertKeys(requirement, ["criterion", "status", "evidence"], ["criterion", "status", "evidence"], `verifier.requirements[${index}]`);
    assertString(requirement.criterion, `verifier.requirements[${index}].criterion`);
    assert(["PASS", "BLOCKED"].includes(requirement.status), `verifier.requirements[${index}].status is invalid`);
    assertString(requirement.evidence, `verifier.requirements[${index}].evidence`);
    assert(task.acceptanceCriteria.includes(requirement.criterion), `verifier reported unknown criterion: ${requirement.criterion}`);
  }
  for (const criterion of task.acceptanceCriteria) {
    const matches = result.requirements.filter((item) => item?.criterion === criterion);
    assert(matches.length === 1, `verifier must report exactly once on criterion: ${criterion}`);
    if (result.verdict === "PASS") assert(matches[0].status === "PASS" && typeof matches[0].evidence === "string" && matches[0].evidence.trim() !== "", `criterion lacks PASS evidence: ${criterion}`);
  }
  for (const key of ["qualityFindings", "securityFindings", "remainingRisks"]) assertStringArray(result[key], `verifier.${key}`);
  assert(["PASS", "BLOCKED", "NOT_REQUIRED"].includes(result.documentationStatus), "verifier documentationStatus is invalid");
}
