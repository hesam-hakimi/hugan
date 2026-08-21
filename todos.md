LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_1 — AUTHORIZE TWO CANONICAL ROOT FILES AND COMPLETE EXISTING REPAIR

The current Repair-5 task correctly stopped with:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

The read-only reconciliation established that the original nine-file ceiling is insufficient.

This is an amendment to the SAME Repair-5 task.

Do not restart Repair 5.
Do not discard, revert, undo, or rewrite already-valid partial Repair-5 work.

==================================================
1. AUTHORIZE EXACTLY TWO ADDITIONAL EXISTING FILES
==================================================

Add exactly these two existing files to the Repair-5 authorized edit universe:

10.
src/writers/RepoWriter.ts

11.
src/test/suite/repoWriterWorkspaceSelection.test.ts

The complete maximum Repair-5 universe is now exactly 11 existing files:

PRODUCTION

1. src/chat/ExplainCoordinator.ts
2. src/chat/ArtifactReuseConversationCoordinator.ts
3. src/chat/ETLChatParticipant.ts
4. src/core/artifacts/ArtifactActionCoordinator.ts
5. src/extension.ts
6. src/customization/RepoContextInitializer.ts
7. src/writers/RepoWriter.ts

TEST

8. src/test/suite/configExplain.test.ts
9. src/test/suite/artifactReuseConversation.test.ts
10. src/test/suite/repoContextInit.test.ts
11. src/test/suite/repoWriterWorkspaceSelection.test.ts

NEW FILES AUTHORIZED: 0

No twelfth file may be modified.

If another file becomes necessary, STOP before editing it and return:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

==================================================
2. CANONICAL ROOT-CLASSIFICATION DEFECT
==================================================

The live source inspection established:

RepoWriter.getDefaultExclusionReason(...)

is the canonical classifier.

It currently recognizes the extension/source root basename:

etl_framework_extension

but does not classify the actual current extension-source checkout:

etl_framework_extension_hf1_v2

as an excluded extension/source root.

As a consequence:

RepoWriter.resolveWorkspacePath()

can accept the extension source checkout itself as a consumerRoot.

Fix this only in the canonical RepoWriter classifier.

Do NOT duplicate root classification inside ExplainCoordinator, Artifact Reuse, RepoContextInitializer, ETLChatParticipant, or another coordinator.

Do NOT introduce another root classifier.

==================================================
3. ROOT-CLASSIFICATION REQUIREMENTS
==================================================

The repair must guarantee that the actual extension/source checkout used by this HF1 V2 candidate cannot become a consumer root.

At minimum prove:

sole open root = current extension-source checkout
→ BLOCKED
→ workspacePath undefined

explicitly selected root = current extension-source checkout
→ BLOCKED
→ workspacePath undefined

while:

legitimate fresh consumer folder
→ CREATE_NEW_JOB

legitimate existing consumer folder
→ UPDATE_EXISTING_REPO

Also preserve:

sample_repo
framework roots
reference roots
extension/install roots
→ BLOCKED

Do not introduce fuzzy substring matching that would block an unrelated legitimate consumer merely because its name contains an extension-like token.

Use the existing canonical normalization/exact-root convention unless live source proves a more semantic existing identity check is available inside RepoWriter.

Do not add a hard-coded developer absolute path.

==================================================
4. REQUIRED ROOT-CLASSIFICATION TESTS
==================================================

In:

src/test/suite/repoWriterWorkspaceSelection.test.ts

add/extend behavioral tests proving:

R1.
The current extension-source checkout basename is BLOCKED when it is the sole workspace folder.

R2.
The same root is BLOCKED when explicitly selected.

R3.
No first-folder fallback can convert it into consumerRoot.

R4.
A legitimate fresh consumer remains CREATE_NEW_JOB.

R5.
A legitimate existing consumer remains UPDATE_EXISTING_REPO.

R6.
A similarly named but genuinely valid consumer is not blocked by fuzzy matching.

Use the real RepoWriter.resolveWorkspacePath() behavior.

No source-text-only assertion is sufficient.

==================================================
5. CONTINUE THE EXISTING PARTIAL REPAIR 5
==================================================

After the root classifier is corrected, continue the existing Repair-5 implementation.

The read-only reconciliation identified three incomplete areas.

Do not declare Repair 5 complete until all three are closed.

==================================================
6. EXPLAIN — COMPLETE DRIFT / REVOCATION SAFETY
==================================================

Current partial state:

Explain authorization exists, but final root/path/content drift verification and preview revocation are incomplete.

Complete the existing Explain flow.

Required final lifecycle:

FIRST TURN
→ canonical consumerRoot
→ immutable explain artifact identity
→ trusted preview
→ persist opaque pendingWriteApprovalId
→ zero writes

SECOND TURN
→ same canonical consumerRoot
→ same relative path
→ same bytes/content
→ approved preview
→ immediate containment re-check
→ exactly one write
→ mark consumed
→ clear pending identity

Reject before write if any of these changed:

consumerRoot
relative path
artifact content/bytes
artifact identity
preview state

CANCEL / DECLINE / SUPERSEDED PREVIEW
→ revoke/clear the pending preview identity
→ zero writes

REPLAY
→ rejected
→ zero additional writes

Do not auto-approve.
Do not fabricate preview IDs.
Do not persist WriteAuthorization capabilities.

==================================================
7. ARTIFACT REUSE — FIX PREVIEW_ONLY DEAD END
==================================================

Current partial state:

Artifact Reuse creates a preview_only preview, but ArtifactActionCoordinator.apply() rejects it instead of reaching an approved create/patch operation.

This is incomplete.

Repair the real state transition rather than weakening ArtifactActionCoordinator.

Required lifecycle:

PREVIEW TURN
→ canonical consumerRoot
→ create/patch operation manifest
→ real trusted preview record
→ pendingWriteApprovalId persisted
→ preview rendered
→ zero mutations

USER APPROVES

Use the existing trusted approval state machine to transition the SAME preview identity to an approved authorization state.

Do not mint an unrelated replacement operation.

APPLY_CREATE / APPLY_PATCH

→ re-resolve/reverify canonical consumerRoot
→ verify same operation
→ verify same relative path
→ verify same content/patch identity
→ verify approved, unconsumed preview
→ immediate containment re-check
→ exactly intended mutation
→ mark consumed
→ clear pending preview identity

REPLAY
→ rejected
→ zero additional mutation

CANCEL / REJECT
→ zero mutation
→ pending preview revoked/cleared

Do NOT make apply accept preview_only as if it were approved.

The repair must create the correct approved state.

==================================================
8. REPO CONTEXT — MANIFEST MUST HASH ACTUAL BYTES WRITTEN
==================================================

Current partial state:

RepoContext uses trusted inline authorization, but the `.gitignore` manifest hash does not represent the actual bytes ultimately written.

This is an approval-binding defect.

Fix it inside the currently authorized RepoContext route.

The authorization manifest must be constructed from the exact:

relative paths
+
exact final bytes

that ScaffoldedAssetWriter will actually write.

No manifest entry may hash:

a template precursor
a placeholder
a pre-normalized string
a different newline representation
or any content different from the actual final filesystem bytes.

Required invariant for every RepoContext file:

SHA256(manifest bytes)
===
SHA256(actual bytes passed to the final writer)

especially `.gitignore`.

Do not weaken the manifest check.

Do not special-case `.gitignore` out of authorization.

==================================================
9. REPO CONTEXT ROOT / AUTHORIZATION SAFETY REMAINS REQUIRED
==================================================

Preserve the Repair-5 requirements already in progress:

- canonical RepoWriter root classification;
- no workspaceFolders[0] fallback;
- no raw `{ approved: true }` write capability;
- trusted inline authorization;
- immediate containment re-check;
- sample_repo/reference/framework/extension source roots blocked;
- no cross-root write.

==================================================
10. ARTIFACTACTIONCOORDINATOR SCOPE RULE
==================================================

src/core/artifacts/ArtifactActionCoordinator.ts remains authorized only if needed for the existing preview → approved → apply state transition.

Do not alter it merely because it is allowed.

If the correct repair can be completed entirely through ArtifactReuseConversationCoordinator and existing APIs, leave ArtifactActionCoordinator byte-identical and report that.

==================================================
11. DO NOT MODIFY SHARED SECURITY PRIMITIVES
==================================================

Do NOT modify:

TrustedWriteApprovalStore.ts
WriteAuthorization.ts
TrustedFrameworkDefinitionResolver.ts
PathValidator.ts
NewArtifactWriter.ts
ArtifactPatchApplier.ts
ScaffoldedAssetWriter.ts

Reuse them as-is.

If live compilation proves an API adaptation is impossible without modifying one of them, STOP and request scope amendment.

Do not silently edit it.

==================================================
12. EXPLICIT NO-TOUCH
==================================================

Do not modify:

etl-framework-adb
original etl_framework_extension repository
consumer repositories
resources/prompts/**
.github/**
Phase-H baseline reports
AGENT.md / AGENTS.md
package-lock.json
S-A / S-B files
Copilot workflow customization historical-failure assets

Do not repair the five historical full-suite failures.

==================================================
13. VALIDATION
==================================================

After implementation, run using existing local dependencies only:

npm run compile
npm run lint

Run focused behavioral tests covering:

RepoWriter workspace selection
Explain save
Artifact Reuse
RepoContextInitializer
HF1
UnitTestCoordinator
WriteAuthorization
fresh consumer
single-folder
trusted framework

Then run full unit tests.

Expected:

compile: PASS
lint: PASS
focused Repair-5/HF1 tests: PASS
full unit: exactly 5 historical failures
new HF1 V2 regressions: NONE

No baseline regeneration.

==================================================
14. FINAL EXHAUSTIVE WRITE-ROUTE SWEEP
==================================================

Repeat the read-only repo-wide consumer-write inventory after the implementation.

Every live consumer-workspace mutation route must classify as:

TRUSTED_CONSUMER_WRITE

or legitimately:

INTERNAL_NON_CONSUMER_WRITE
TEST_ONLY
DEAD_OR_UNREACHABLE

There must be zero remaining:

REPAIR_5_REQUIRED

routes.

No reachable consumer write may use an unvalidated:

workspaceFolders[0]
workspaceFolders?.[0]

root.

If another live ungated consumer write appears, STOP:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

==================================================
15. EXACT END-STATE SCOPE
==================================================

Report exactly which of the 11 authorized files were actually modified during Repair 5.

No twelfth file.

No new file.

Staged count must remain zero.

No Git mutation.
No install/download.
No VSIX package/install.
No real consumer repository mutation.

==================================================
16. REQUIRED FINAL REPORT
==================================================

Return:

1. Full actual Repair-5 changed-file inventory.
2. Canonical extension/source-root classifier before/after.
3. RepoWriter regression-test results.
4. Explain lifecycle final state.
5. Explain drift/revocation proof.
6. Artifact Reuse preview→approve→apply proof.
7. Artifact Reuse replay/cancel proof.
8. RepoContext exact-byte manifest proof, especially `.gitignore`.
9. Root/containment proof for all three flows.
10. Compile result.
11. Lint result.
12. Focused test result.
13. Full unit result.
14. Final exhaustive write-route inventory.
15. Confirmation no REPAIR_5_REQUIRED route remains.
16. Historical-five separation.
17. Exact scope/no-touch proof.

Finish exactly one:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_VALIDATED

or

LOCAL_HOTFIX_HF1_V2_REPAIR_5_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

or

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

or

LOCAL_HOTFIX_HF1_V2_REPAIR_5_BLOCKED

Do not Keep.
Do not commit.
Do not push.
Do not package.
Do not install a VSIX.
