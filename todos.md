LOCAL_HOTFIX_HF1_V2_REPAIR_5 — CLOSE ALL REMAINING CONSUMER WRITE ROUTES

Implement the bounded Repair 5 using the authoritative completed scope discovery:

ALL_LIVE_CONSUMER_WRITE_ROUTES_ENUMERATED: YES
ADDITIONAL_UNGATED_WRITE_ROUTE_BEYOND_AUDIT_TWO: YES
EXPLAIN_WRITE_REPAIR_REQUIRED: YES
ARTIFACT_REUSE_WRITE_REPAIR_REQUIRED: YES
FRAMEWORK_BINDING_CHANGE_NEEDED_FOR_REPAIR_5: NO
REPAIR_5_SCOPE_FROZEN: YES
LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_DISCOVERY_COMPLETE

This Repair closes exactly three remaining consumer-workspace write findings:

A. ExplainCoordinator.handleSaveExplain()
B. Artifact Reuse preview/apply-create/apply-patch flow
C. RepoContextInitializer / initializeRepoContext consumer write

Do not redesign the already-secure HF1 V2 routes.

Do not change framework-binding behavior.

==================================================
0. ONE CONSOLIDATED AUTHORIZATION REQUEST
==================================================

Before the first edit or mutating validation command, request one consolidated authorization covering:

- edits only to the nine authorized files listed below;
- local compile/lint/tests using already-installed dependencies;
- read-only inspection needed to verify the implementation;
- no Git mutation;
- no install/download;
- no VSIX packaging/install;
- no consumer repository mutation outside test-managed temporary fixtures.

Ask for exactly:

APPLY_LOCAL_HOTFIX_HF1_V2_REPAIR_5

After receiving it, do not repeatedly request conversational authorization for operations already inside this bounded batch.

Host-enforced permission dialogs must not be bypassed.

==================================================
1. EXACT AUTHORIZED PRODUCTION FILES
==================================================

Repair 5 may modify only these six production files:

1.
src/chat/ExplainCoordinator.ts

2.
src/chat/ArtifactReuseConversationCoordinator.ts

3.
src/chat/ETLChatParticipant.ts

4.
src/core/artifacts/ArtifactActionCoordinator.ts

5.
src/extension.ts

6.
src/customization/RepoContextInitializer.ts

No other production file may be modified.

IMPORTANT:
ArtifactActionCoordinator.ts was included by discovery because approval identity may need to be threaded through dispatch.

Before editing it, confirm from live source that the edit is actually required.

If it is not required, leave it byte-identical.

Do not edit a file merely because it appears in the allowed set.

==================================================
2. EXACT AUTHORIZED TEST FILES
==================================================

Modify only these three test files:

1.
src/test/suite/configExplain.test.ts

2.
src/test/suite/artifactReuseConversation.test.ts

3.
src/test/suite/repoContextInit.test.ts

Do not create a new test file.

==================================================
3. NO NEW FILES
==================================================

NEW FILES AUTHORIZED:

0

If implementation genuinely requires another production or test file, STOP before editing it and report:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

==================================================
4. REUSE EXISTING TRUSTED INFRASTRUCTURE
==================================================

Do not create:

- another root classifier;
- another approval store;
- another WriteAuthorization implementation;
- another security state machine.

Reuse the existing trusted HF1 V2 infrastructure:

RepoWriter
RepoWriter.resolveWorkspacePath()
PathValidator
TrustedWriteApprovalStore
requestWriteAuthorization(...)
requestInlineWriteAuthorization(...)
WriteAuthorization
existing manifest/checksum primitives
existing markConsumed/fail state transitions

The design principle for every consumer write remains:

resolve canonical consumerRoot
→ reject prohibited/reference/source roots
→ validate contained relative artifact path
→ immutable preview
→ explicit approval
→ trusted one-time authorization
→ immediate containment re-check
→ exactly one filesystem mutation

==================================================
5. NORMAL QA ROOT CONTRACT
==================================================

For all three repaired flows:

exactly one legitimate consumer folder
→ canonical consumerRoot

zero workspace folders
→ BLOCKED

one prohibited/reference/source/install root
→ BLOCKED

sample_repo as sole root
→ BLOCKED

multiple folders without explicit safe selection
→ ambiguous / BLOCKED

Never use:

workspaceFolders[0]
workspaceFolders?.[0]

as a consumer-write root.

Never infer:

"the folder that is not extension/framework must be consumer"

All root decisions must reuse RepoWriter.resolveWorkspacePath() or an exact trusted delegation to it.

==================================================
6. FINDING A — EXPLAIN SAVE
==================================================

Repair:

ExplainCoordinator.handleSaveExplain()

Current problem:

- naive first-folder root selection;
- no protected-root classification;
- direct write;
- no trusted preview/approval/WriteAuthorization lifecycle.

Required final behavior:

FIRST SAVE REQUEST

resolve canonical consumerRoot
→ validate destination/path
→ construct immutable manifest
→ requestWriteAuthorization(...)
→ preview record created
→ persist opaque preview ID
→ return approval-required state
→ zero filesystem writes

SECOND TURN WITH APPROVED PREVIEW

same canonical consumerRoot
+ same relative path
+ same bytes/content
+ valid approved preview
→ authorization accepted
→ immediately re-check containment
→ exactly one write
→ mark approval consumed
→ clear persisted pending preview identity

REPLAY

same consumed preview
→ rejected
→ zero additional writes

CANCEL / DECLINE

→ zero writes

==================================================
7. EXPLAIN STATE
==================================================

Inside:

src/chat/ExplainCoordinator.ts

the discovery authorized adding exactly the minimum optional state to ExplainOutput:

pendingWriteApprovalId?: string

or the exact equivalent naming already established by the implementation.

Requirements:

- opaque string only;
- optional;
- backwards-compatible;
- no WriteAuthorization object;
- no approval-store record;
- no privileged runtime capability;
- no writer instance.

Do not persist anything more powerful than the preview/approval identity required to resume the trusted lifecycle.

==================================================
8. EXPLAIN PATH SAFETY
==================================================

Explain save must reject:

- absolute paths;
- drive-qualified paths;
- `..` traversal;
- normalized consumerRoot escape;
- sibling-root escape;
- extension root;
- framework/reference root;
- sample_repo.

Immediately before the real write:

final target must still be a descendant of the same canonical consumerRoot approved in Preview.

The approved relative path must be the path written.

Do not independently reconstruct a different destination after approval.

==================================================
9. FINDING B — ARTIFACT REUSE
==================================================

Repair the flow:

ArtifactReuseConversationCoordinator
→ ArtifactActionCoordinator
→ NewArtifactWriter / ArtifactPatchApplier

The low-level writers and PathValidator are already trusted/contained.

Do NOT modify:

NewArtifactWriter.ts
ArtifactPatchApplier.ts
PathValidator.ts
RepoWriter.ts
TrustedWriteApprovalStore.ts
WriteAuthorization.ts

The defect is above them:

- root selected naively before session creation;
- root persisted without canonical consumer classification;
- conversational confirmation is weaker than trusted authorization;
- no immutable one-time approval binding;
- no root/path/content drift protection equivalent to HF1 V2.

==================================================
10. ARTIFACT REUSE ROOT RESOLUTION
==================================================

At:

ETLChatParticipant.startArtifactReuseSession(...)

replace naive workspaceFolders[0]-style root selection with the canonical RepoWriter resolution.

Before ArtifactReuseSessionState is created:

resolve canonical root.

If resolution is:

BLOCKED
ambiguous
no_workspace
prohibited/reference/source root

then do not create a writable Artifact Reuse session.

No consumer mutation may later occur from an unresolved or prohibited root.

==================================================
11. ARTIFACT REUSE STATE
==================================================

Inside:

ArtifactReuseConversationCoordinator.ts

add only the minimum optional opaque identity:

pendingWriteApprovalId?: string

to ArtifactReuseSessionState.

Same restrictions as Explain:

- opaque identifier only;
- optional;
- no privileged capability;
- no raw authorization object;
- no approval-store record;
- backwards compatible.

==================================================
12. ARTIFACT REUSE PREVIEW/APPLY LIFECYCLE
==================================================

The conversational flow already has natural preview/apply turns.

Integrate those turns with the trusted approval store.

PREVIEW TURN

- canonical consumerRoot already resolved;
- patch/create plan computed;
- artifact path/content/operation captured;
- construct trusted immutable manifest;
- call requestWriteAuthorization(...)
- create preview record;
- persist pendingWriteApprovalId;
- render preview;
- zero filesystem mutations.

APPLY_PATCH / APPLY_CREATE TURN

- use stored opaque preview identity;
- re-resolve/re-verify consumerRoot;
- verify operation;
- verify relative path;
- verify content/patch identity;
- verify approval;
- immediately re-check containment;
- perform exactly intended mutation;
- mark consumed;
- clear pending preview identity.

REPLAY

→ rejected
→ zero additional mutations.

CANCEL

→ zero mutations.

==================================================
13. ARTIFACTACTIONCOORDINATOR
==================================================

If required by the real call graph, thread the opaque preview ID / resolved authorization information through:

src/core/artifacts/ArtifactActionCoordinator.ts

only as necessary to reach the existing apply dispatch.

Do not put approval logic into NewArtifactWriter or ArtifactPatchApplier.

Do not invent a second authorization state machine.

If live source proves no ArtifactActionCoordinator change is needed, leave this file untouched and explain why in the final report.

==================================================
14. ARTIFACT REUSE DRIFT CHECKS
==================================================

Between Preview and Apply, reject:

consumerRoot drift
relative path drift
operation drift
artifact content drift
patch drift
target drift
consumed/replayed preview
expired/stale approval

No stale preview may apply a different create or patch operation.

==================================================
15. FINDING C — REPO CONTEXT INITIALIZER
==================================================

Repair the consumer-write route:

RepoContextInitializer.initialize(...)

reached through both identified call sites:

- extension command path
- ETLChatParticipant command path

This is a distinct consumer-write feature and is in scope even though it shares ScaffoldedAssetWriter with separately excluded Copilot workflow customization code.

Do NOT modify the excluded Copilot workflow customization family.

Do NOT touch the three historical Copilot customization failures.

==================================================
16. REPO CONTEXT ROOT SELECTION
==================================================

Both callers must resolve the target through the same canonical RepoWriter consumer-root contract.

Remove any naive:

workspaceFolders[0]

or QuickPick result that is accepted without canonical root classification.

If the selected candidate is:

sample_repo
framework/reference/source/install root
ambiguous
invalid/external

→ BLOCKED
→ zero writes.

For multi-root selection:

a UI-selected folder still must pass canonical RepoWriter classification before it can become consumerRoot.

Selection does not itself make a root trusted.

==================================================
17. REPO CONTEXT AUTHORIZATION MODEL
==================================================

The discovery concluded this flow is synchronous:

preview
→ modal confirmation
→ initialize/write

within one invocation.

Therefore use the existing:

requestInlineWriteAuthorization(...)

or the exact existing single-shot trusted helper designed for this shape.

Replace the current:

{ approved: boolean }

or equivalent plain-boolean security gate.

RepoContextInitializer.initialize() must consume a resolved trusted authorization shape rather than trusting a caller-provided boolean.

Do not allow:

initialize(..., { approved: true })

to become a writable capability.

==================================================
18. REPO CONTEXT WRITE SAFETY
==================================================

Before ScaffoldedAssetWriter writes:

- consumerRoot must be canonical and approved;
- generated relative path must be validated;
- final target containment must be rechecked;
- protected/reference/source roots must remain blocked;
- approval must bind the exact write;
- one user approval must authorize only the intended operation.

No raw boolean approval.

No first-folder fallback.

No cross-root write.

==================================================
19. EXTENSION COMMAND
==================================================

Modify:

src/extension.ts

only for the identified initializeRepoContext command route.

Responsibilities:

- canonical root resolution;
- fail-closed behavior;
- trusted inline preview/approval flow;
- pass trusted resolved authorization to RepoContextInitializer.

Do not modify unrelated extension activation or command behavior.

==================================================
20. ETLCHATPARTICIPANT
==================================================

Modify:

src/chat/ETLChatParticipant.ts

only for:

A. Artifact Reuse session root selection.

B. RepoContext initialization command root selection / trusted authorization integration.

Do not modify unrelated routing/planning behavior.

Do not repair the existing non-blocking multi-root observability debt in this task.

==================================================
21. DO NOT FOLD THESE INTO RENDEREDARTIFACTS
==================================================

Discovery confirmed there is no literal "12 artifact" constant.

The governed /create artifact shape is represented by RenderedArtifacts.

Explain output, Artifact Reuse generated/modified artifacts, and RepoContext output are separately generated consumer-workspace artifacts.

Do NOT fold them into:

RenderedArtifacts
buildWriteManifestFiles
/create artifact ordering

Do not make them an artificial "13th artifact".

Each receives the smallest independent trusted authorization adapter while reusing the same underlying security infrastructure.

==================================================
22. CONFIGEXPLAIN TESTS
==================================================

In:

src/test/suite/configExplain.test.ts

extend the existing Explain command suite.

Required behavioral tests:

E1 — first save request:
preview/approval required
zero writes

E2 — approved second request:
exactly one write
inside canonical consumerRoot

E3 — replay:
zero additional writes

E4 — decline/cancel:
zero writes

E5 — sole sample_repo/reference root:
BLOCKED
zero writes

E6 — multi-root with no explicit safe selection:
BLOCKED
zero writes

E7 — no first-folder fallback:
put an attractive folder at index 0
still BLOCKED if selection is ambiguous

E8 — absolute path rejected

E9 — traversal rejected

E10 — sibling-root escape rejected

E11 — re-verify containment immediately before write

Use real production behavior.

Use existing mintTestWriteAuthorization test infrastructure only as intended.

Do not fabricate a production WriteAuthorization object.

==================================================
23. ARTIFACT REUSE TESTS
==================================================

In:

src/test/suite/artifactReuseConversation.test.ts

required behavioral tests:

A1 — preview produces zero writes

A2 — approved create performs exactly one contained write

A3 — approved patch performs exactly intended contained mutation

A4 — replay cannot apply again

A5 — cancel performs zero mutations

A6 — sample_repo/reference root BLOCKED

A7 — framework/source/install root BLOCKED

A8 — multi-root ambiguity BLOCKED

A9 — no first-folder fallback

A10 — consumerRoot drift after preview rejected

A11 — relative path drift rejected

A12 — content/create drift rejected

A13 — patch drift rejected

A14 — absolute path escape rejected

A15 — traversal rejected

A16 — sibling-root escape rejected

A17 — every actual mutation remains inside canonical consumerRoot

Exercise the real conversational coordinator and existing low-level writers.

==================================================
24. REPO CONTEXT TESTS
==================================================

In:

src/test/suite/repoContextInit.test.ts

update existing initialize() call sites for the trusted authorization contract.

Required behavioral coverage:

R1 — preview/confirmation + valid trusted inline authorization permits exactly intended initialization write

R2 — no approval → zero writes

R3 — plain `{ approved: true }`-style capability no longer authorizes a write

R4 — sample_repo sole root BLOCKED

R5 — framework/reference/source root BLOCKED

R6 — multi-root selected candidate still must pass root classification

R7 — no first-folder fallback

R8 — traversal/escape rejected

R9 — final write contained in canonical consumerRoot

R10 — existing status/non-writing behavior remains green

If command-registration behavior in extension.ts requires additional testing, add the assertion inside this existing file or an already-existing relevant routing suite only if necessary.

Do NOT create a new test file.

==================================================
25. COPILOT WORKFLOW CUSTOMIZATION — EXPLICIT NO TOUCH
==================================================

Do not modify the separately identified Copilot workflow customization family, including behavior responsible for the historical three customization failures.

Do not modify their customization assets.

Do not fix their failures.

Finding C is RepoContext initialization, not authorization to redesign the broader customization system.

==================================================
26. FRAMEWORK BINDING — NO CHANGE
==================================================

Discovery returned:

FRAMEWORK_BINDING_CHANGE_NEEDED_FOR_REPAIR_5: NO

Do not modify:

TrustedFrameworkDefinitionResolver.ts
TrustedWriteApprovalStore.ts
WriteAuthorization.ts
framework contract JSON
resources/framework/**

unless this task later proves a compile-level signature adaptation is impossible without scope amendment.

If so, STOP and request scope amendment rather than editing.

==================================================
27. EXACT REPAIR-5 SCOPE
==================================================

Maximum authorized production files:

src/chat/ExplainCoordinator.ts
src/chat/ArtifactReuseConversationCoordinator.ts
src/chat/ETLChatParticipant.ts
src/core/artifacts/ArtifactActionCoordinator.ts
src/extension.ts
src/customization/RepoContextInitializer.ts

Maximum authorized test files:

src/test/suite/configExplain.test.ts
src/test/suite/artifactReuseConversation.test.ts
src/test/suite/repoContextInit.test.ts

New files:

0

State/type edits are contained inside already-listed production files.

No tenth file may change.

==================================================
28. VALIDATION
==================================================

Run using existing local dependencies only:

npm run compile
npm run lint

Then run targeted tests covering:

Explain
Artifact Reuse
RepoContextInitializer
HF1
RepoWriter workspace selection
UnitTestCoordinator
WriteAuthorization
Trusted framework
fresh consumer
single-folder

Then run the full unit suite.

Expected result:

compile: PASS
lint: PASS
Repair-5 targeted tests: PASS
HF1 V2 focused tests: PASS
full unit: exactly 5 historical failures
new HF1 V2 regressions: NONE

Do not regenerate baselines.

Do not repair the historical five.

If native commands are unavailable, provide exact external validation commands and do not fabricate results.

==================================================
29. FINAL WRITE-ROUTE SWEEP
==================================================

After implementation, perform a read-only repo-wide sweep again for production filesystem mutations.

Confirm each live consumer write route is now either:

TRUSTED_CONSUMER_WRITE

or legitimately:

INTERNAL_NON_CONSUMER_WRITE

No:

REPAIR_5_REQUIRED

route may remain.

Specifically prove no reachable consumer-write route still uses:

workspaceFolders[0]
workspaceFolders?.[0]

as an unvalidated write root.

Do not modify additional files discovered during this final sweep.

If another live ungated consumer write is found, STOP and return:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

==================================================
30. END-STATE PROOF
==================================================

Report:

- exact Repair-5 files actually changed;
- files allowed but left untouched;
- no new files;
- staged count;
- no Git mutation;
- no dependency install/download;
- no VSIX build/install;
- no consumer repository write outside test-managed temp fixtures;
- no original repository modification;
- no etl-framework-adb modification;
- no historical baseline modification.

==================================================
31. REQUIRED FINAL REPORT
==================================================

Return:

1. Exact Repair-5 file inventory.
2. Explain write before/after.
3. Artifact Reuse write before/after.
4. RepoContext initialize before/after.
5. Root-resolution behavior for all three.
6. Preview/approval state design.
7. One-time authorization/replay behavior.
8. Path/root/content drift protection.
9. Containment proof.
10. Test matrix and results.
11. Full unit result.
12. Final exhaustive write-route inventory.
13. Confirmation no additional ungated consumer write remains.
14. Historical-five separation.
15. Framework-binding no-change confirmation.
16. Exact scope/no-touch proof.

Finish with exactly one:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_VALIDATED

or:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

or:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

or:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_BLOCKED

Do not Keep.
Do not commit.
Do not push.
Do not package.
Do not install a VSIX.
Stop after the final Repair-5 report.
