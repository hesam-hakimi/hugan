import assert from "node:assert/strict";
import test from "node:test";
import { validateContractSet, validateImplementerResult, validatePlannerResult, validateTask, validateVerifierResult } from "../scripts/lib/contracts.mjs";
import { matchesPattern, patternWithin } from "../scripts/lib/glob.mjs";
import { createFixture } from "./helpers.mjs";

test("glob matching handles root files, nested files, and path escape", () => {
  assert.equal(matchesPattern("artifact.vsix", "**/*.vsix"), true);
  assert.equal(matchesPattern("nested/artifact.vsix", "**/*.vsix"), true);
  assert.equal(matchesPattern("src/a/b.js", "src/**"), true);
  assert.equal(matchesPattern("other/a.js", "src/**"), false);
  assert.equal(patternWithin("src/example/**", "src/**"), true);
  assert.equal(patternWithin("escape/**", "src/**"), false);
  assert.throws(() => matchesPattern("../escape", "**"), /escapes the project/);
});

test("contract set accepts a valid frozen milestone task", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const result = await validateContractSet({
    projectRoot: fixture.project,
    config: fixture.config,
    milestone: fixture.milestone,
    task: fixture.task,
    headSha: fixture.headSha,
  });
  assert.equal(result.roadmap.currentMilestone, "M1");
});

test("contract set blocks base drift, scope widening, and unapproved capability", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  await assert.rejects(validateContractSet({ projectRoot: fixture.project, config: fixture.config, milestone: fixture.milestone, task: { ...fixture.task, expectedBaseSha: "1".repeat(40) }, headSha: fixture.headSha }), /base SHA mismatch/);
  await assert.rejects(validateContractSet({ projectRoot: fixture.project, config: fixture.config, milestone: fixture.milestone, task: { ...fixture.task, authorizedPaths: ["escape/**", "docs/example.md"] }, headSha: fixture.headSha }), /outside milestone envelope/);
  await assert.rejects(validateContractSet({ projectRoot: fixture.project, config: fixture.config, milestone: fixture.milestone, task: { ...fixture.task, capabilityId: "CAP-999" }, headSha: fixture.headSha }), /not approved/);
});

test("task blocks unauthorized or prohibited documentation paths", () => {
  const base = {
    schemaVersion: "1.0", taskId: "T", milestoneId: "M", capabilityId: "C", objective: "O",
    acceptanceCriteria: ["A"], expectedBaseSha: "a".repeat(40), roadmapRefs: ["M"], architectureRefs: ["A"],
    authorizedPaths: ["src/**"], prohibitedPaths: ["private/**"], requiredChecks: ["unit"],
    requiresDocumentation: true, documentationPaths: ["docs/readme.md"], approvalClass: "milestone-preapproved",
  };
  assert.throws(() => validateTask(base), /documentation path is not authorized/);
  assert.throws(() => validateTask({ ...base, authorizedPaths: ["private/**"], documentationPaths: ["private/readme.md"] }), /documentation path is prohibited/);
});

test("role result validators reject widened, malformed, and self-inconsistent evidence", async (t) => {
  const fixture = await createFixture();
  t.after(fixture.cleanup);
  const planner = {
    role: "planner", status: "PASS", taskId: fixture.task.taskId, baseSha: fixture.headSha, summary: "Plan",
    planSteps: ["Step"], predictedPaths: ["src/example/feature.js"], checkIds: ["unit"],
    roadmapAlignment: "PASS", architectureAlignment: "PASS", assumptions: [], blockers: [],
  };
  validatePlannerResult(planner, fixture.task);
  assert.throws(() => validatePlannerResult({ ...planner, extra: true }, fixture.task), /unsupported property extra/);
  assert.throws(() => validatePlannerResult({ ...planner, predictedPaths: ["escape.txt"] }, fixture.task), /unauthorized path/);

  const implementer = {
    role: "implementer", status: "PASS", taskId: fixture.task.taskId, baseSha: fixture.headSha,
    summary: "Done", declaredChangedPaths: ["src/example/feature.js"], requestedCheckIds: ["unit"], blockers: [],
  };
  validateImplementerResult(implementer, fixture.task);
  assert.throws(() => validateImplementerResult({ ...implementer, requestedCheckIds: [] }, fixture.task), /exactly match/);
  assert.throws(() => validateImplementerResult({ ...implementer, declaredChangedPaths: ["escape.txt"] }, fixture.task), /unauthorized path/);

  const digest = "b".repeat(64);
  const verifier = {
    role: "verifier", verdict: "PASS", taskId: fixture.task.taskId, baseSha: fixture.headSha,
    reviewedDiffSha256: digest,
    requirements: [{ criterion: fixture.task.acceptanceCriteria[0], status: "PASS", evidence: "Diff evidence" }],
    qualityFindings: [], securityFindings: [], remainingRisks: [], documentationStatus: "PASS", independent: true,
  };
  validateVerifierResult(verifier, fixture.task, digest);
  assert.throws(() => validateVerifierResult({ ...verifier, independent: false }, fixture.task, digest), /independent=true/);
  assert.throws(() => validateVerifierResult({ ...verifier, reviewedDiffSha256: "c".repeat(64) }, fixture.task, digest), /different diff digest/);
  assert.throws(() => validateVerifierResult({ ...verifier, requirements: [...verifier.requirements, { criterion: "invented", status: "PASS", evidence: "none" }] }, fixture.task, digest), /must not add or omit/);
});
