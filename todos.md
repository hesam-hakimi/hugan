LOCAL_HOTFIX_HF1_V2_REPAIR_4 — CLOSE FINAL QA WRITE/ROOT BLOCKERS

Implement the bounded Repair 4 derived from the completed read-only scope discovery.

Authoritative discovery result:

REPAIR_4_SCOPE_FROZEN: YES
LOCAL_HOTFIX_HF1_V2_REPAIR_4_SCOPE_DISCOVERY_COMPLETE

This task fixes exactly:

1. CRITICAL — sample_repo can be accepted as a writable consumer root.
2. HIGH — UnitTestCoordinator.handleWrite() bypasses the trusted preview/approval/write-authorization boundary and consumerRoot containment.

The discovery separately concluded:

FRAMEWORK_BINDING_REPAIR_NOT_REQUIRED

Do not modify framework-manifest binding in this task.

⸻

1. EXACT AUTHORIZED FILES

Modify only these four production files:

src/writers/RepoWriter.ts
src/chat/UnitTestCoordinator.ts
src/services/unitTesting/UnitTestGenerationTypes.ts
src/chat/ETLChatParticipant.ts

Modify only these two test files:

src/test/suite/repoWriterWorkspaceSelection.test.ts
src/test/suite/unitTestGeneration.test.ts

No new files are authorized.

No other file may be edited.

If another file becomes necessary, STOP before editing and return:

LOCAL_HOTFIX_HF1_V2_REPAIR_4_SCOPE_AMENDMENT_REQUIRED

⸻

2. FINDING A — BLOCK sample_repo

The discovery confirmed the canonical write-root classification is:

RepoWriter.getDefaultExclusionReason(...)

with the existing protected/reference/source-root set.

Implement the smallest repair:

* add sample_repo to the existing protected source/reference-root set;
* route it through the already-correct BLOCKED behavior;
* do not invent a second classifier;
* do not alter the valid single-folder fresh-consumer path.

Required behavior:

only workspace folder = sample_repo
→ BLOCKED
→ workspacePath undefined
→ no consumer write possible

while:

one legitimate empty consumer folder
→ CREATE_NEW_JOB

must remain green.

Do not use fuzzy substring matching for sample_repo.

Use the same normalization/case convention already used by the existing protected-root names.

⸻

3. UNIT TEST COORDINATOR — REMOVE DIRECT WRITE

The discovery confirmed:

UnitTestCoordinator.handleWrite()

currently performs a direct filesystem write without:

* immutable preview;
* explicit approval;
* WriteAuthorization;
* approved manifest;
* consumerRoot containment equivalent to the other write routes.

This route must be brought under the SAME trusted write architecture already used elsewhere.

Do NOT create a new authorization implementation.

Reuse the existing trusted preview/approval/write primitives.

Required lifecycle:

generate
→ user requests write
→ resolve canonical consumerRoot
→ validate artifact/path
→ immutable preview
→ return approval-required response
→ zero filesystem writes
next turn with approved preview
→ verify same consumerRoot
→ verify same artifact path/bytes
→ consume one-time authorization
→ containment-safe write
→ exactly one filesystem write

A consumed/replayed approval must not write again.

⸻

4. PERSIST PREVIEW IDENTITY BETWEEN TURNS

The discovery confirmed the unit-test flow is multi-turn and the persisted:

UnitTestEvidenceSummary

currently cannot carry the preview/approval identity required for the next turn.

Modify:

src/services/unitTesting/UnitTestGenerationTypes.ts

only as minimally required to carry the trusted preview identity between turns.

Requirements:

* add only the minimum optional field needed;
* do not store a fabricated WriteAuthorization object;
* do not persist a privileged runtime capability;
* persist only the identifier/state needed to resume the real approval flow;
* preserve backwards compatibility for summaries created before the field existed.

The actual authorization must still be minted/verified through the trusted approval mechanism.

⸻

5. INJECT THE EXISTING WRITE DEPENDENCIES

Modify:

src/chat/ETLChatParticipant.ts

only as needed to construct UnitTestCoordinator with the same trusted write dependencies already used by the normal write path.

Reuse the existing RepoWriter instance used by the surrounding participant/write flow.

Do not silently construct a second independent workspace resolver.

Do not add a separate write store or authorization subsystem.

The UnitTestCoordinator must use the same canonical consumer-root semantics as the rest of HF1 V2.

Existing unrelated construction sites must remain unchanged unless TypeScript requires a compatible optional/default parameter.

⸻

6. REMOVE FIRST-FOLDER FALLBACK

The existing UnitTestCoordinator path must no longer end with or semantically perform:

workspaceFolders[0]

as a write-root fallback.

Required behavior:

Zero workspace folders

BLOCKED
zero writes

One valid consumer folder

canonical consumerRoot

One prohibited root, including sample_repo

BLOCKED
zero writes

Multiple folders without explicit safe selection

ambiguous / BLOCKED
zero writes

Never infer:

first folder = consumer

and never infer:

the non-extension/non-framework folder = consumer

⸻

7. REUSE CONSUMER PATH CONTAINMENT

Do not retain the current narrow filename-regex check as the security boundary.

UnitTestCoordinator writes must reuse the existing production consumer path-safety contract.

At minimum reject:

* absolute paths;
* drive-qualified paths;
* .. traversal;
* normalized paths escaping consumerRoot;
* sibling-root escape;
* extension-resource root;
* framework/reference/source roots.

Immediately before the filesystem write, prove:

final target is inside canonical consumerRoot

The exact artifact path approved in Preview must be the path written after Approval.

Do not recompute a different write path later.

⸻

8. FIRST TURN MUST WRITE NOTHING

Rewrite the unit-test write behavior so the first write request returns a Preview/Approval-required result.

Assert and implement:

first write request:
preview generated
preview identity persisted
filesystem write count = 0
result != written

No directory or test file may be created on the first turn.

No approval prompt must be bypassed.

⸻

9. APPROVED SECOND TURN

With the same generated test evidence and valid approved preview:

second write request:
authorization verifies
consumerRoot unchanged
artifact relative path unchanged
artifact bytes unchanged
exactly one write
result = written/success according to existing contract

Use the exact existing approved-write mechanism.

Do not:

* auto-approve;
* forge preview IDs;
* forge WriteAuthorization;
* call fs.writeFile directly before authorization;
* bypass the approval store.

⸻

10. REPLAY MUST FAIL

A third attempt using the consumed approval must:

perform zero new writes
not return a successful written result

Do not mint a replacement approval automatically.

⸻

11. FRAMEWORK BINDING — NO CHANGE

The discovery concluded:

FRAMEWORK_BINDING_REPAIR_NOT_REQUIRED

Reason:

* gated EtlActionToolService write re-runs prewrite readiness/authority validation before authorization;
* a degraded framework authority blocks before stale approval can be consumed;
* inline WriteCoordinator/DeployCoordinator authorizations are single-shot and have no meaningful drift window.

Therefore do NOT modify:

TrustedWriteApprovalStore.ts
WriteAuthorization.ts
TrustedFrameworkDefinitionResolver.ts
framework contract JSON

in Repair 4.

Record the theoretical long-lived framework-authority manifest binding issue as existing LOW follow-up debt only.

⸻

12. REQUIRED TEST — sample_repo

In:

src/test/suite/repoWriterWorkspaceSelection.test.ts

add a behavioral regression test beside the existing extension/reference-root exclusion coverage.

Prove:

workspaceFolders = [sample_repo]

returns:

workspacePath === undefined
reason === single_workspace_folder_excluded
targetDecision === BLOCKED

or the exact equivalent live contract values.

Also preserve the existing test proving a legitimate fresh single-folder consumer still reaches:

CREATE_NEW_JOB

No source-text-only assertion is sufficient.

⸻

13. REQUIRED UNITTESTCOORDINATOR TEST MATRIX

In:

src/test/suite/unitTestGeneration.test.ts

update/add behavioral coverage for the actual production UnitTestCoordinator route.

Required:

T1 — first call preview only

* generated unit-test evidence exists;
* request write;
* preview returned/persisted;
* write count = 0.

T2 — approved second call

* identical artifact;
* approved preview;
* exactly one workspace.fs.writeFile;
* exact destination URI is under canonical consumerRoot.

T3 — approval replay

* reuse consumed approval;
* write count remains 1;
* result is rejected/not-written.

T4 — multi-root ambiguity

Place an apparently eligible folder at index 0 deliberately.

With multiple folders and no explicit safe consumer selection:

* BLOCKED;
* zero writes.

This must fail a naive workspaceFolders[0] implementation.

T5 — prohibited sole root

Use sample_repo or another exact protected reference root as the only folder:

* BLOCKED;
* zero writes.

T6 — absolute path escape

* rejected;
* zero writes.

T7 — traversal escape

Example:

../outside.py

* rejected;
* zero writes.

T8 — sibling-root escape

* rejected;
* zero writes.

T9 — every attempted write inside consumerRoot

Capture every actual write URI and assert canonical containment beneath the resolved consumerRoot.

T10 — normal run/cancel regression

Existing run/cancel behavior in this test file must remain green.

Use real production coordinator behavior, not source-text scans.

⸻

14. TEST QUALITY

Tests must be discriminating.

They should fail if any of these regressions are reintroduced:

sample_repo becomes writable
workspaceFolders[0] fallback
direct UnitTestCoordinator fs.writeFile
write before approval
approval replay
path traversal
sibling-root escape
write outside consumerRoot

Mocks must not bypass the production authorization path.

Do not make private test-only backdoors.

⸻

15. DO NOT CHANGE THE FIVE HISTORICAL FAILURES

Do not touch:

* EvalGating baseline failures;
* Copilot workflow customization failures;
* their source assets;
* Phase-H baselines.

Expected full-unit baseline after Repair 4 remains:

exactly 5 historical failures
no HF1 V2 regression

⸻

16. VALIDATION

Run, when native tooling is available:

npm run compile
npm run lint

Then run targeted tests covering:

RepoWriter workspace selection
UnitTestCoordinator / unit test generation
HF1
Trusted framework
fresh consumer
single-folder
WriteAuthorization

Then run full unit suite.

Success criteria:

compile: PASS
lint: PASS
targeted Repair-4 tests: PASS
HF1 V2 focused tests: PASS
full unit: exactly 5 historical failures
new HF1 V2 regressions: NONE

Do not regenerate baselines.

If native execution is unavailable, report exact commands for external validation and do not fabricate results.

⸻

17. END-STATE SCOPE PROOF

At completion confirm:

Production files changed during Repair 4:

src/writers/RepoWriter.ts
src/chat/UnitTestCoordinator.ts
src/services/unitTesting/UnitTestGenerationTypes.ts
src/chat/ETLChatParticipant.ts

Test files changed:

src/test/suite/repoWriterWorkspaceSelection.test.ts
src/test/suite/unitTestGeneration.test.ts

New files:

0

No seventh file may change.

If any other file changes, Repair 4 is incomplete.

Confirm:

* staged count = 0;
* no Git mutation;
* no package/install/download;
* no VSIX build;
* no consumer repository write;
* no original repository modification;
* no framework repository modification.

⸻

18. FINAL REPORT

Return:

1. Exact six-file Repair-4 diff inventory.
2. sample_repo classification before/after.
3. UnitTestCoordinator write route before/after.
4. How preview identity is persisted.
5. How existing trusted authorization is reused.
6. How consumerRoot is resolved.
7. How path containment is enforced.
8. Evidence first call writes zero.
9. Evidence approved call writes exactly once.
10. Evidence replay fails.
11. Evidence multi-root cannot use first-folder fallback.
12. Evidence sample_repo cannot become consumerRoot.
13. Evidence path escape fails.
14. Framework-binding non-change confirmation.
15. Compile/lint/test results.
16. Historical-five separation.
17. Remaining LOW framework-binding debt.
18. Exact scope proof.

Finish with exactly one:

LOCAL_HOTFIX_HF1_V2_REPAIR_4_VALIDATED

or:

LOCAL_HOTFIX_HF1_V2_REPAIR_4_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

or:

LOCAL_HOTFIX_HF1_V2_REPAIR_4_SCOPE_AMENDMENT_REQUIRED

or:

LOCAL_HOTFIX_HF1_V2_REPAIR_4_BLOCKED

Do not Keep.
Do not commit.
Do not push.
Do not package.
Do not install a VSIX.
Stop after the Repair-4 report.
