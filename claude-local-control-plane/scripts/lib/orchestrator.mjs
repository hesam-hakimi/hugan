import { randomUUID } from "node:crypto";
import { mkdir, readdir, realpath } from "node:fs/promises";
import path from "node:path";
import { matchesAny } from "./glob.mjs";
import {
  validateContractSet,
  validateImplementerResult,
  validatePlannerResult,
  validateVerifierResult,
} from "./contracts.mjs";
import { assertCleanWorktree, captureWorkspaceSnapshot, compareWorkspaceSnapshots, diffEvidence, gitMetadataDirectory, repositoryIdentity } from "./git.mjs";
import { createHandoff, ensureSigningKey, verifyHandoff } from "./handoff.mjs";
import { implementerPrompt, plannerPrompt, verifierPrompt } from "./prompts.mjs";
import { runClaudeRole } from "./runner.mjs";
import {
  acquireLock,
  assertResolvedInside,
  digestJson,
  normalizeRepoPath,
  readJson,
  spawnCapture,
  truncateUtf8,
  writeJsonAtomic,
} from "./util.mjs";

class ControlledBlock extends Error {
  constructor(message, { resumeAllowed = false } = {}) {
    super(message);
    this.name = "ControlledBlock";
    this.resumeAllowed = resumeAllowed;
  }
}

function now() {
  return new Date().toISOString();
}

function sortedUnique(values) {
  return [...new Set(values)].sort();
}

function sameSet(left, right) {
  const a = sortedUnique(left);
  const b = sortedUnique(right);
  return a.length === b.length && a.every((item, index) => item === b[index]);
}

async function saveArtifact(runDir, name, value) {
  const filePath = path.join(runDir, "artifacts", `${name}.json`);
  await writeJsonAtomic(filePath, value);
  return { path: filePath, digest: digestJson(value) };
}

async function saveState(runDir, state) {
  state.updatedAt = now();
  await writeJsonAtomic(path.join(runDir, "state.json"), state);
}

async function workspaceChangedSinceBaseline(projectRoot, state) {
  const baselineArtifactValue = await readJson(state.artifacts.baseline.path);
  const currentSnapshot = await captureWorkspaceSnapshot(projectRoot);
  return compareWorkspaceSnapshots(baselineArtifactValue.workspaceSnapshot, currentSnapshot).length > 0;
}

function transition(state, target, manifest) {
  const allowed = manifest.transitions[state.currentState] ?? [];
  if (!allowed.includes(target)) throw new Error(`Illegal state transition ${state.currentState} -> ${target}`);
  state.history.push({ from: state.currentState, to: target, at: now() });
  state.currentState = target;
  state.status = manifest.terminalStates.includes(target) ? target : "RUNNING";
}

async function loadInputs({ pluginRoot, project, configPath, milestonePath, taskPath, requireClean = true }) {
  const projectRoot = await realpath(path.resolve(project));
  const absoluteConfig = path.resolve(configPath);
  const absoluteMilestone = path.resolve(milestonePath);
  const absoluteTask = path.resolve(taskPath);
  const [config, milestone, task, processManifest, identity] = await Promise.all([
    readJson(absoluteConfig),
    readJson(absoluteMilestone),
    readJson(absoluteTask),
    readJson(path.join(pluginRoot, "contracts", "process-manifest.json")),
    repositoryIdentity(projectRoot),
  ]);
  if (requireClean) await assertCleanWorktree(projectRoot);
  const sources = await validateContractSet({ projectRoot, config, milestone, task, headSha: identity.headSha });
  return {
    pluginRoot,
    projectRoot,
    configPath: absoluteConfig,
    milestonePath: absoluteMilestone,
    taskPath: absoluteTask,
    config,
    milestone,
    task,
    processManifest,
    identity,
    ...sources,
  };
}

async function validateBoundary(context, identity, baselineSnapshot) {
  const liveIdentity = await repositoryIdentity(context.projectRoot);
  if (liveIdentity.headSha !== identity.headSha) throw new ControlledBlock("HEAD changed during the run");
  if (liveIdentity.branch !== identity.branch) throw new ControlledBlock("Branch changed during the run");
  const currentSnapshot = await captureWorkspaceSnapshot(context.projectRoot);
  const paths = compareWorkspaceSnapshots(baselineSnapshot, currentSnapshot);
  if (paths.length === 0) throw new ControlledBlock("Implementer reported PASS but the worktree snapshot found no source changes");
  for (const filePath of paths) {
    await assertResolvedInside(context.projectRoot, filePath);
    if (!matchesAny(filePath, context.task.authorizedPaths)) {
      throw new ControlledBlock(`Unauthorized changed path: ${filePath}`);
    }
    if (matchesAny(filePath, context.task.prohibitedPaths) || filePath === ".git" || filePath.startsWith(".git/")) {
      throw new ControlledBlock(`Prohibited changed path: ${filePath}`);
    }
  }
  return { paths, liveIdentity, currentSnapshot };
}

async function runChecks(context) {
  const results = [];
  for (const checkId of context.task.requiredChecks) {
    const check = context.config.checks[checkId];
    const cwd = path.resolve(context.projectRoot, check.cwd === "." ? "" : normalizeRepoPath(check.cwd));
    await assertResolvedInside(context.projectRoot, cwd);
    const [command, ...args] = check.argv;
    const startedAt = now();
    const result = await spawnCapture(command, args, {
      cwd,
      timeoutMs: check.timeoutMs,
      maxOutputBytes: 2_000_000,
      env: { ...process.env, CI: "true", LCAC_ACTIVE: "0" },
    });
    results.push({
      checkId,
      argv: check.argv,
      cwd: path.relative(context.projectRoot, cwd) || ".",
      startedAt,
      finishedAt: now(),
      exitCode: result.code,
      timedOut: result.timedOut,
      stdout: truncateUtf8(result.stdout, 250_000),
      stderr: truncateUtf8(result.stderr, 250_000),
      pass: result.code === 0 && !result.timedOut,
    });
  }
  return results;
}

async function issueAndVerifyHandoff(parameters) {
  const issued = await createHandoff(parameters);
  if (!verifyHandoff(issued.handoff, parameters.key)) throw new Error(`Generated handoff failed signature verification: ${parameters.fromRole} -> ${parameters.toRole}`);
  return issued;
}

async function blockRun(state, runDir, manifest, message, resumeAllowed) {
  const blockedAt = state.currentState;
  transition(state, "BLOCKED", manifest);
  state.blockedAt = blockedAt;
  state.blockReason = message;
  state.resumeAllowed = Boolean(resumeAllowed);
  await saveState(runDir, state);
}

async function executePipeline(context, state, runDir, stateRoot, { resuming = false } = {}) {
  const key = await ensureSigningKey(stateRoot);
  const baselineArtifactValue = await readJson(state.artifacts.baseline.path);
  const baselineSnapshot = baselineArtifactValue.workspaceSnapshot;
  const limits = {
    maxSourceBytes: context.config.promptLimits?.maxSourceBytes ?? 200_000,
    maxDiffBytes: context.config.promptLimits?.maxDiffBytes ?? 300_000,
  };
  const sessions = {
    planner: randomUUID(),
    implementer: randomUUID(),
    verifier: randomUUID(),
  };
  if (new Set(Object.values(sessions)).size !== 3) throw new Error("Role session IDs are not distinct");
  state.sessions = { ...(state.sessions ?? {}), ...sessions };
  state.resumeAllowed = false;
  await saveState(runDir, state);

  if (state.currentState === "BASELINE_CAPTURED" || (resuming && state.currentState === "PLANNING")) {
    if (state.currentState === "BASELINE_CAPTURED") transition(state, "PLANNING", context.processManifest);
    await saveState(runDir, state);
    const initialHandoff = await issueAndVerifyHandoff({
      runDir,
      runId: state.runId,
      taskId: context.task.taskId,
      fromRole: "orchestrator",
      toRole: "planner",
      fromSessionId: null,
      toSessionId: sessions.planner,
      baseSha: context.identity.headSha,
      taskDigest: state.taskDigest,
      artifactDigests: { baseline: state.artifacts.baseline.digest, milestone: state.milestoneDigest, config: state.configDigest },
      key,
    });
    state.handoffs = { ...(state.handoffs ?? {}), orchestratorToPlanner: initialHandoff.filePath };
    await saveState(runDir, state);

    let plannerExecution;
    try {
      plannerExecution = await runClaudeRole({
        pluginRoot: context.pluginRoot,
        projectRoot: context.projectRoot,
        config: context.config,
        role: "planner",
        prompt: plannerPrompt({ task: context.task, milestone: context.milestone, roadmap: context.roadmap, architecture: context.architecture, maxSourceBytes: limits.maxSourceBytes }),
        task: context.task,
        taskPath: context.taskPath,
        sessionId: sessions.planner,
      });
    } catch (error) {
      throw new ControlledBlock(`Planner process did not produce a valid result: ${error.message}`, { resumeAllowed: true });
    }
    validatePlannerResult(plannerExecution.structured, context.task);
    const plannerArtifact = await saveArtifact(runDir, "planner-result", plannerExecution.structured);
    await saveArtifact(runDir, "planner-raw", plannerExecution.raw);
    state.artifacts.planner = plannerArtifact;
    if (plannerExecution.structured.status !== "PASS") {
      throw new ControlledBlock(`Planner blocked the task: ${plannerExecution.structured.blockers.join("; ")}`);
    }
    if (await workspaceChangedSinceBaseline(context.projectRoot, state)) {
      throw new ControlledBlock("Planner process mutated the worktree despite read-only authority");
    }
    transition(state, "PLAN_READY", context.processManifest);
    await saveState(runDir, state);
  }

  const plannerResult = await readJson(state.artifacts.planner.path);
  const plannerToImplementer = await issueAndVerifyHandoff({
    runDir,
    runId: state.runId,
    taskId: context.task.taskId,
    fromRole: "planner",
    toRole: "implementer",
    fromSessionId: sessions.planner,
    toSessionId: sessions.implementer,
    baseSha: context.identity.headSha,
    taskDigest: state.taskDigest,
    artifactDigests: { planner: state.artifacts.planner.digest },
    key,
  });
  state.handoffs.plannerToImplementer = plannerToImplementer.filePath;
  transition(state, "IMPLEMENTING", context.processManifest);
  state.sourceMutationPossible = true;
  await saveState(runDir, state);

  const implementerExecution = await runClaudeRole({
    pluginRoot: context.pluginRoot,
    projectRoot: context.projectRoot,
    config: context.config,
    role: "implementer",
    prompt: implementerPrompt({ task: context.task, milestone: context.milestone, plan: plannerResult, roadmap: context.roadmap, architecture: context.architecture, maxSourceBytes: limits.maxSourceBytes }),
    task: context.task,
    taskPath: context.taskPath,
    sessionId: sessions.implementer,
  });
  validateImplementerResult(implementerExecution.structured, context.task);
  const implementerArtifact = await saveArtifact(runDir, "implementer-result", implementerExecution.structured);
  await saveArtifact(runDir, "implementer-raw", implementerExecution.raw);
  state.artifacts.implementer = implementerArtifact;
  if (implementerExecution.structured.status !== "PASS") {
    throw new ControlledBlock(`Implementer blocked the task: ${implementerExecution.structured.blockers.join("; ")}`);
  }

  const boundary = await validateBoundary(context, context.identity, baselineSnapshot);
  if (!sameSet(boundary.paths, implementerExecution.structured.declaredChangedPaths)) {
    throw new ControlledBlock(`Implementer declaration disagrees with Git. declared=${implementerExecution.structured.declaredChangedPaths.join(",")} actual=${boundary.paths.join(",")}`);
  }
  const boundaryArtifact = await saveArtifact(runDir, "boundary-result", { pass: true, changedPaths: boundary.paths, headSha: boundary.liveIdentity.headSha, branch: boundary.liveIdentity.branch });
  state.artifacts.boundary = boundaryArtifact;
  transition(state, "BOUNDARY_VERIFIED", context.processManifest);
  transition(state, "CHECKING", context.processManifest);
  await saveState(runDir, state);

  const checks = await runChecks(context);
  const checksArtifact = await saveArtifact(runDir, "check-results", checks);
  state.artifacts.checks = checksArtifact;
  if (checks.some((check) => !check.pass)) {
    throw new ControlledBlock(`Required checks failed: ${checks.filter((check) => !check.pass).map((check) => check.checkId).join(", ")}`);
  }

  const afterChecks = await validateBoundary(context, context.identity, baselineSnapshot);
  if (!sameSet(afterChecks.paths, boundary.paths) || compareWorkspaceSnapshots(boundary.currentSnapshot, afterChecks.currentSnapshot).length > 0) {
    throw new ControlledBlock("Required checks mutated the repository worktree");
  }
  const diff = await diffEvidence(context.projectRoot, limits.maxDiffBytes, afterChecks.paths, baselineSnapshot);
  const diffArtifact = await saveArtifact(runDir, "diff-evidence", diff);
  state.artifacts.diff = diffArtifact;
  transition(state, "IMPLEMENTED", context.processManifest);
  await saveState(runDir, state);

  const implementerToVerifier = await issueAndVerifyHandoff({
    runDir,
    runId: state.runId,
    taskId: context.task.taskId,
    fromRole: "implementer",
    toRole: "verifier",
    fromSessionId: sessions.implementer,
    toSessionId: sessions.verifier,
    baseSha: context.identity.headSha,
    taskDigest: state.taskDigest,
    artifactDigests: {
      implementer: implementerArtifact.digest,
      boundary: boundaryArtifact.digest,
      checks: checksArtifact.digest,
      diff: diffArtifact.digest,
    },
    key,
  });
  state.handoffs.implementerToVerifier = implementerToVerifier.filePath;
  transition(state, "VERIFYING", context.processManifest);
  await saveState(runDir, state);

  const verifierExecution = await runClaudeRole({
    pluginRoot: context.pluginRoot,
    projectRoot: context.projectRoot,
    config: context.config,
    role: "verifier",
    prompt: verifierPrompt({ task: context.task, milestone: context.milestone, plan: plannerResult, implementer: implementerExecution.structured, diff, checks, roadmap: context.roadmap, architecture: context.architecture, maxSourceBytes: limits.maxSourceBytes }),
    task: context.task,
    taskPath: context.taskPath,
    sessionId: sessions.verifier,
  });
  validateVerifierResult(verifierExecution.structured, context.task, diff.digest);
  const verifierArtifact = await saveArtifact(runDir, "verifier-result", verifierExecution.structured);
  await saveArtifact(runDir, "verifier-raw", verifierExecution.raw);
  state.artifacts.verifier = verifierArtifact;
  const afterVerifierSnapshot = await captureWorkspaceSnapshot(context.projectRoot);
  if (compareWorkspaceSnapshots(afterChecks.currentSnapshot, afterVerifierSnapshot).length > 0) {
    throw new ControlledBlock("Verifier process mutated the worktree despite read-only authority");
  }
  if (verifierExecution.structured.verdict !== "PASS") {
    throw new ControlledBlock("Independent Verifier blocked the task");
  }
  transition(state, "VERIFIED", context.processManifest);

  const documentationChanged = !context.task.requiresDocumentation || diff.changedPaths.some((filePath) => matchesAny(filePath, context.task.documentationPaths));
  if (!documentationChanged) throw new ControlledBlock("Required documentation path was not changed");
  if (context.task.requiresDocumentation && verifierExecution.structured.documentationStatus !== "PASS") {
    throw new ControlledBlock("Verifier did not pass required documentation");
  }
  if (!context.task.requiresDocumentation && !["PASS", "NOT_REQUIRED"].includes(verifierExecution.structured.documentationStatus)) {
    throw new ControlledBlock("Verifier blocked documentation status");
  }
  transition(state, "DOCUMENTATION_CHECKED", context.processManifest);
  transition(state, "DONE", context.processManifest);
  state.sourceMutationPossible = true;
  state.resumeAllowed = false;
  state.final = {
    result: "PASS_READY_FOR_OWNER_REVIEW",
    changedPaths: diff.changedPaths,
    diffSha256: diff.digest,
    checks: checks.map(({ checkId, pass, exitCode }) => ({ checkId, pass, exitCode })),
    verifierVerdict: verifierExecution.structured.verdict,
    sessions,
    commitCreated: false,
    pushExecuted: false,
    pullRequestCreated: false,
    packageCreated: false,
    installOrDeploymentStarted: false,
  };
  const finalArtifact = await saveArtifact(runDir, "final-report", state.final);
  state.artifacts.final = finalArtifact;
  await saveState(runDir, state);
  return state;
}

export async function validateRunInputs(options) {
  const context = await loadInputs({ ...options, requireClean: true });
  return {
    valid: true,
    projectRoot: context.projectRoot,
    branch: context.identity.branch,
    headSha: context.identity.headSha,
    milestoneId: context.milestone.milestoneId,
    taskId: context.task.taskId,
    capabilityId: context.task.capabilityId,
    requiredChecks: context.task.requiredChecks,
    authorizedPaths: context.task.authorizedPaths,
  };
}

export async function startRun(options) {
  const context = await loadInputs({ ...options, requireClean: true });
  const stateRoot = await gitMetadataDirectory(context.projectRoot);
  const runId = `${context.task.taskId}-${Date.now()}-${randomUUID().slice(0, 8)}`;
  const runDir = path.join(stateRoot, "runs", runId);
  await mkdir(runDir, { recursive: true });
  const release = await acquireLock(path.join(stateRoot, "active.lock"), { runId, pid: process.pid, startedAt: now() });
  const state = {
    schemaVersion: "1.0",
    runId,
    status: "RUNNING",
    currentState: "INTAKE",
    lastSafeState: "INTAKE",
    history: [],
    createdAt: now(),
    updatedAt: now(),
    projectRoot: context.projectRoot,
    branch: context.identity.branch,
    baseSha: context.identity.headSha,
    baseTreeSha: context.identity.treeSha,
    inputs: {
      configPath: context.configPath,
      milestonePath: context.milestonePath,
      taskPath: context.taskPath,
    },
    configDigest: digestJson(context.config),
    milestoneDigest: digestJson(context.milestone),
    taskDigest: digestJson(context.task),
    artifacts: {},
    handoffs: {},
    sessions: {},
    sourceMutationPossible: false,
    resumeAllowed: false,
  };
  await saveState(runDir, state);
  try {
    transition(state, "BASELINE_CAPTURED", context.processManifest);
    state.lastSafeState = "BASELINE_CAPTURED";
    const workspaceSnapshot = await captureWorkspaceSnapshot(context.projectRoot);
    const baseline = await saveArtifact(runDir, "baseline", { identity: context.identity, workspaceSnapshot });
    state.artifacts.baseline = baseline;
    await saveState(runDir, state);
    try {
      return await executePipeline(context, state, runDir, stateRoot);
    } catch (error) {
      const resumeAllowed = error instanceof ControlledBlock && error.resumeAllowed && !(await workspaceChangedSinceBaseline(context.projectRoot, state));
      await blockRun(state, runDir, context.processManifest, error.message, resumeAllowed);
      return state;
    }
  } finally {
    await release();
  }
}

async function locateRun(projectRoot, runId) {
  const stateRoot = await gitMetadataDirectory(projectRoot);
  const runsRoot = path.join(stateRoot, "runs");
  let selected = runId;
  if (!selected) {
    const entries = await readdir(runsRoot, { withFileTypes: true });
    const directories = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort().reverse();
    if (directories.length === 0) throw new Error("No local control-plane runs exist");
    selected = directories[0];
  }
  const runDir = path.join(runsRoot, selected);
  const state = await readJson(path.join(runDir, "state.json"));
  return { stateRoot, runDir, state };
}

export async function readRunStatus({ project, runId }) {
  const projectRoot = await realpath(path.resolve(project));
  const { state } = await locateRun(projectRoot, runId);
  return state;
}

export async function resumeRun({ pluginRoot, project, runId }) {
  const projectRoot = await realpath(path.resolve(project));
  const located = await locateRun(projectRoot, runId);
  const state = located.state;
  if (state.currentState !== "BLOCKED" || state.resumeAllowed !== true || state.blockedAt !== "PLANNING") {
    throw new Error("This run is not safely resumable; post-mutation or policy blocks require a new approved task");
  }
  const context = await loadInputs({
    pluginRoot,
    project: projectRoot,
    configPath: state.inputs.configPath,
    milestonePath: state.inputs.milestonePath,
    taskPath: state.inputs.taskPath,
    requireClean: true,
  });
  if (digestJson(context.config) !== state.configDigest || digestJson(context.milestone) !== state.milestoneDigest || digestJson(context.task) !== state.taskDigest) {
    throw new Error("Contracts changed since the blocked run; create a new run instead of resuming");
  }
  if (context.identity.headSha !== state.baseSha || context.identity.branch !== state.branch) {
    throw new Error("Repository identity changed since the blocked run");
  }
  const release = await acquireLock(path.join(located.stateRoot, "active.lock"), { runId: state.runId, pid: process.pid, resumedAt: now() });
  try {
    state.history.push({ from: "BLOCKED", to: "PLANNING", at: now(), resume: true });
    state.currentState = "PLANNING";
    state.status = "RUNNING";
    state.blockReason = null;
    state.blockedAt = null;
    state.resumeAllowed = false;
    await saveState(located.runDir, state);
    try {
      return await executePipeline(context, state, located.runDir, located.stateRoot, { resuming: true });
    } catch (error) {
      const resumeAllowed = error instanceof ControlledBlock && error.resumeAllowed && !(await workspaceChangedSinceBaseline(context.projectRoot, state));
      await blockRun(state, located.runDir, context.processManifest, error.message, resumeAllowed);
      return state;
    }
  } finally {
    await release();
  }
}
