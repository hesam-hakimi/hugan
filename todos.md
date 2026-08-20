LOCAL_HOTFIX_HF1_V2 — READ-ONLY ROOT-CAUSE ANALYSIS OF THE TWO NEW FULL-SUITE FAILURES

Perform a fresh, independent, strictly read-only root-cause analysis of the two newly observed full-unit failures after HF1 V2.

Do not implement, repair, edit, format, create, delete, rename, stage, commit, package, or modify any file.

Do not modify Git state.

Do not change tests merely to make the suite green.

Your job is only to determine whether each failure is:

* a genuine production regression;
* an intentionally obsolete test expectation caused by the newly authorized architecture;
* a test-harness/setup defect;
* an unrelated pre-existing issue;
* or still ambiguous.

⸻

1. Current validated state

Repository:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Current validation evidence:

Compile: PASS
Lint: PASS
Focused HF1 V2 tests: PASS
Repair-2 focused validation: PASS

Full unit result:

1850 passing
5 pending
7 failing

Before HF1 V2, this same base was known to have 6 unrelated failures.

One historical failure:

Package asset manifest —
excludes dev logs, eval outputs, generated packages, and test artifacts from VSIX candidate

is no longer present, consistent with the authorized package-hygiene repair.

Therefore the current 7 failures appear to consist of:

5 remaining historical failures
+
2 newly surfaced failures

Verify this independently from live test/source evidence rather than simply accepting the statement.

⸻

2. Five historical failures — DO NOT REPAIR

These five failures are expected to remain outside HF1 V2:

EvalGating —
passes against the committed Phase H baseline report
EvalGating —
allows deterministic v3 baseline reports without prompt telemetry
Copilot workflow customization —
maintainer delivery prompt references real repo-local agents
Copilot workflow customization —
repo customization assets use valid frontmatter and agent file naming
Copilot workflow customization —
source tree uses standard AGENTS.md guidance instead of module AGENT.md files

Do not recommend repairing, regenerating, suppressing, rebaselining, or changing these as part of HF1 V2.

Confirm whether all five are still materially the same failures observed before HF1 V2.

⸻

3. New Failure A — Phase 6 Agent Router / workspace selection

Observed failure:

Phase 6 Agent Router And Create Flow
default v3 workspace context selects ETL asset repo instead of extension repo

Observed assertion:

assert.ok(
    capturedInputs.every(
        input => input.workspaceRoot === assetRoot.uri.fsPath
    )
);

The assertion is currently false.

Required investigation

Trace the complete runtime path leading to capturedInputs[].workspaceRoot.

Inspect at minimum:

* the failing test setup;
* number and identity of workspace folders in that fixture;
* whether the test supplies an explicit consumer/resource selection;
* Agent/router/context code that resolves workspaceRoot;
* RepoWriter workspace-selection changes introduced by HF1 V2;
* any pass-through layer between Agent routing and RepoWriter;
* the Single-Folder QA/User Architecture Amendment.

The approved architecture now says:

Normal QA/user mode

exactly one workspace folder
→ canonicalize
→ consumerRoot

Multi-root mode

Without explicit consumer selection:

multiple workspace folders
→ ambiguous / fail closed

The system must never silently use:

workspaceFolders[0]

and must never infer:

"the folder that is not the extension/framework must be the consumer"

Maintainer multi-root mode may work only through an existing explicit safe consumer-selection mechanism.

Determine exactly

A. Does this failing Phase-6 test construct a multi-root workspace?

B. Does it provide an explicit consumer selection?

C. Was its old expectation based on implicit ETL-asset-repository inference?

D. Is the new failure therefore an intentionally stale expectation under the approved Single-Folder model?

OR

E. Does the router already possess an explicit selected consumer root which HF1 V2 accidentally discards or replaces, making this a real production regression?

F. Does the failure affect normal QA single-folder operation?

G. Does it affect only internal/maintainer multi-root behavior?

H. What exact behavior should the test assert under the approved architecture?

Do not decide merely from the test title. Trace actual runtime data.

⸻

4. New Failure B — non-onboarding write lifecycle

Observed failure:

EtlActionToolService.writeToWorkspace trusted onboarding lifecycle
non-onboarding writes follow the existing path without preview/approval

The actual response now contains:

Write Preview Recorded — Approval Required
A trusted preview was recorded by the extension.
Nothing was written.

The old test appears to expect a completed direct write.

Required investigation

Trace the exact production route for this test.

Determine:

A. Is hasOnboarding === false the reason the previous implementation bypassed Preview/Approval?

B. Did HF1 V2 intentionally remove that bypass?

C. Does the approved HF1 V2 security contract explicitly require:

EVERY write
→ validation
→ immutable preview
→ explicit approval
→ one-time WriteAuthorization
→ write

including non-onboarding writes?

D. Is zero-write + preview-required therefore the correct new behavior?

E. Does the test exercise any separate legacy contract that is supposed to retain direct writes?

F. Would restoring the old behavior recreate the security bypass HF1 V2 was specifically designed to close?

G. What is the smallest correct test update if the expectation is obsolete?

Do not recommend weakening the approval gate merely to satisfy the test.

⸻

5. Compare against HF1 V2 contracts

For both failures, compare behavior against these ratified requirements.

Single-folder QA path model

Normal QA/user:

ONE consumer workspace folder
NO etl-framework-adb
NO framework source
NO first-folder fallback
NO implicit multi-root consumer guessing

Write security

All production write routes:

validation
→ immutable preview/path manifest
→ explicit approval
→ one-time authorization
→ runtime re-verification
→ write

No special direct-write bypass for:

hasOnboarding === false

is permitted.

Do not classify behavior as a regression merely because a historical test expects behavior that the approved architecture deliberately removed.

⸻

6. Scope implications

For each failure, identify the smallest repair surface if a subsequent repair is authorized.

Important:

src/test/suite/onboardingWriteApproval.test.ts

was already inside the HF1 V2 authorized edit universe.

However:

src/test/suite/phase6AgentRouter.test.ts

may NOT be in the current authorized HF1 V2 edit universe.

Verify this.

If Failure A is merely an obsolete test expectation and correcting it requires modifying phase6AgentRouter.test.ts, explicitly state:

SCOPE_AMENDMENT_REQUIRED

Do not edit it.

If Failure A is a production regression, identify the exact already-authorized or new production file that would require repair.

Do not request a broad scope.

⸻

7. Check for hidden regressions

Also inspect whether either new failure exposes a broader issue such as:

* explicit consumer selection being lost between layers;
* selected consumerRoot being recomputed independently;
* router and writer using different workspace-selection rules;
* preview using one root and execution another;
* normal single-folder QA path accidentally depending on multi-root logic;
* approval gate failing to preserve an existing semantic that should remain supported.

Report such a finding separately even if the immediate test expectation is stale.

⸻

8. Do not mutate or execute broad validation

This task is read-only investigation.

Permitted:

* source/test reads;
* Git diff/status/show;
* text search;
* inspecting previously compiled test output;
* inspecting current implementation and test setup.

Do not:

* edit files;
* rerun full unit suite;
* regenerate baselines;
* package VSIX;
* install anything;
* modify node_modules;
* modify package files;
* perform Git mutation.

If one narrowly targeted command is genuinely required to distinguish two hypotheses, explain it first and keep it read-only/non-mutating.

⸻

9. Required report

Return a two-row root-cause matrix.

For each failure report:

* exact failing test file and lines;
* exact relevant production files and lines;
* old expectation;
* current behavior;
* approved architectural contract;
* root cause;
* classification;
* QA/user impact;
* maintainer/internal impact;
* smallest correct repair;
* whether production code must change;
* whether test code must change;
* whether scope amendment is required.

Classification must be exactly one of:

STALE_TEST_EXPECTATION
PRODUCTION_REGRESSION
TEST_HARNESS_DEFECT
PRE_EXISTING_UNRELATED
AMBIGUOUS

Then provide a recommended next repair sequence.

Do not make any repair in this task.

Finish with exactly:

NEW_FAILURE_A_CLASSIFICATION: <classification>
NEW_FAILURE_B_CLASSIFICATION: <classification>
PRODUCTION_CODE_CHANGE_REQUIRED: YES|NO
TEST_CODE_CHANGE_REQUIRED: YES|NO
SCOPE_AMENDMENT_REQUIRED: YES|NO
FIVE_HISTORICAL_FAILURES_PRESERVED: YES|NO
SAFE_TO_PREPARE_BOUNDED_REPAIR: YES|NO
LOCAL_HOTFIX_HF1_V2_NEW_FAILURE_ROOT_CAUSE_COMPLETE
