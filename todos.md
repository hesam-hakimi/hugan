LOCAL_HOTFIX_HF1_V2_REPAIR_3 — BOUNDED STALE-TEST ALIGNMENT

The independent read-only root-cause analysis completed with:

NEW_FAILURE_A_CLASSIFICATION: STALE_TEST_EXPECTATION
NEW_FAILURE_B_CLASSIFICATION: STALE_TEST_EXPECTATION
PRODUCTION_CODE_CHANGE_REQUIRED: NO
TEST_CODE_CHANGE_REQUIRED: YES
SCOPE_AMENDMENT_REQUIRED: YES
FIVE_HISTORICAL_FAILURES_PRESERVED: YES
SAFE_TO_PREPARE_BOUNDED_REPAIR: YES
LOCAL_HOTFIX_HF1_V2_NEW_FAILURE_ROOT_CAUSE_COMPLETE

This repair authorizes test-only changes.

Do NOT modify production code.

AUTHORIZED FILES

Exactly these two files may be modified:

1. src/test/suite/phase5AgentRouter.test.ts
2. src/test/suite/onboardingWriteApproval.test.ts

The first path is a narrowly approved scope amendment.

No other file is authorized.

If any other file appears necessary, stop before editing it and return:

LOCAL_HOTFIX_HF1_V2_SCOPE_AMENDMENT_REQUIRED

==================================================
1. FAILURE A — PHASE 5 AGENT ROUTER TEST
==================================================

Current stale test:

"default v3 workspace context selects ETL asset repo instead of extension repo"

The old fixture opens a multi-root workspace containing:

- extensionRoot
- assetRoot

and supplies no explicit consumer selection.

The old expectation implicitly inferred:

"the folder that is not the extension repo must be the consumer"

That inference has intentionally been removed.

The approved HF1 V2 architecture is:

Normal QA/User:
exactly one consumer workspace folder
→ canonicalize
→ consumerRoot

Multi-root without explicit consumer selection:
→ ambiguous
→ fail closed

Never:
workspaceFolders[0] fallback

Never:
infer that the non-extension/non-framework folder is the consumer

REPAIR REQUIREMENTS

Replace the stale test behavior with discriminating coverage for the approved contract.

At minimum:

A. Single-folder positive case

Workspace contains only:

assetRoot

Expected:

- workspaceRoot/baseDir resolves to assetRoot.uri.fsPath
- normal V3 planning receives the consumerRoot
- no extensionRoot inference is involved

B. Multi-root fail-closed case

Workspace contains:

extensionRoot
assetRoot

with no explicit consumer selection.

Expected:

- resolver reports ambiguous/BLOCKED semantics
- no workspaceRoot is fabricated
- no first-folder fallback occurs
- no "non-extension folder" inference occurs

Do not make this test expect assetRoot in the ambiguous multi-root case.

C. If the existing production route already supports an explicit consumer-selection seam that can be exercised without production changes, add a multi-root explicit-selection positive case.

If no such production seam is currently wired, do not invent one and do not modify production code.

Preserve all unrelated Phase-5 router assertions.

Do not weaken the test merely to accept undefined values. The test must positively assert the intended fail-closed behavior.

==================================================
2. FAILURE B — NON-ONBOARDING WRITE TEST
==================================================

Current stale test:

"non-onboarding writes follow the existing path without preview/approval"

That behavior was the write bypass intentionally removed by HF1 V2.

The approved security contract is:

EVERY write
→ validation
→ immutable preview
→ explicit approval
→ one-time WriteAuthorization
→ runtime re-verification
→ exactly one write

There is no hasOnboarding === false direct-write exception.

REPAIR REQUIREMENTS

Rewrite only this stale test as a real two-step behavioral test.

Use the same non-onboarding input.

Step 1:
- invoke writeToWorkspace without previewId
- assert success === false
- assert Preview/Approval Required result
- capture the returned Preview ID using the existing supported contract
- assert zero filesystem writes
- assert zero approval-prompt bypass

Step 2:
- perform the real approval transition through the existing trusted test mechanism
- invoke writeToWorkspace again with the same content and approved previewId
- assert the approved operation succeeds
- assert the expected conf/sql/report artifact is written
- assert exactly one write lifecycle occurs
- assert approval becomes consumed and cannot be reused

Preserve or strengthen existing assertions concerning:

- prompt count
- written file
- success result
- preview identity
- one-time consumption
- identical manifest/content requirements

Do not:

- auto-approve
- fabricate preview IDs
- forge a production authorization object
- restore a hasOnboarding bypass
- use a direct RepoWriter call to evade the public workflow
- weaken runtime approval checks

Rename the test so its name reflects the new contract, for example:

"non-onboarding writes require the same preview and approval lifecycle"

Use the repository's existing naming style if different.

==================================================
3. DO NOT TOUCH THE FIVE HISTORICAL FAILURES
==================================================

Do not modify or repair:

1. EvalGating — committed Phase H baseline
2. EvalGating — deterministic v3 baseline without prompt telemetry
3. Copilot workflow customization — repo-local agents
4. Copilot workflow customization — frontmatter/naming
5. Copilot workflow customization — AGENTS.md guidance

Do not regenerate any baseline.

==================================================
4. SEPARATE OBSERVABILITY FINDING
==================================================

The read-only analysis identified a separate maintainer multi-root UX/observability issue:

AgentMessageRouter may report ambiguity but continue planning with workspaceRoot undefined when no explicit consumer selection is available.

This is NOT part of Repair 3.

Do not modify:

- AgentMessageRouter
- ETLChatParticipant
- workspaceResolver plumbing
- production planning behavior

Record it only as follow-up debt.

==================================================
5. VALIDATION
==================================================

Run if native tooling is available:

npm run compile
npm run lint

Run targeted tests covering:

- phase5AgentRouter
- onboardingWriteApproval

Then run the existing focused HF1 V2 suite.

Expected:

- compile: PASS
- lint: PASS
- targeted repaired tests: PASS
- focused HF1 V2 suite: PASS

Do not run the full unit suite from this implementation task if it significantly increases scope/time; external full regression will be run separately immediately afterward.

If native execution is unavailable, do not fabricate results.

==================================================
6. END-STATE REQUIREMENTS
==================================================

Confirm:

- exactly the two authorized test files changed during Repair 3
- zero production files changed
- zero unexpected paths created
- staged count remains zero
- no Git mutation
- no package/install/download
- no VSIX packaging
- no consumer write
- no baseline regeneration

Report:

1. Exact changes in phase5AgentRouter.test.ts
2. Exact changes in onboardingWriteApproval.test.ts
3. Why each old assertion was stale
4. Why the new assertions are stronger/discriminating
5. Compile result
6. Lint result
7. Targeted test result
8. Focused HF1 V2 result
9. Separate observability finding retained but not repaired

Finish with exactly one marker:

LOCAL_HOTFIX_HF1_V2_REPAIR_3_VALIDATED

or:

LOCAL_HOTFIX_HF1_V2_REPAIR_3_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

or:

LOCAL_HOTFIX_HF1_V2_REPAIR_3_BLOCKED

Do not Keep.
Do not commit.
Do not push.
Do not package.
