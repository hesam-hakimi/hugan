TASK_ID: ETL-0910-SCAFFOLDED-SKILL-ROOT-GUIDANCE-PARITY-REVIEW01

Communicate entirely in English.

Perform an independent, read-only review of:
ETL-0910-SCAFFOLDED-SKILL-ROOT-GUIDANCE-PARITY01

Review the source correction and retained test evidence. Do not repeat
the skill-resolution investigation or earlier initialization qualification.

Environment
Existing development worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Confirm its current identity and preserve all existing changes.
Resolve the implementation evidence directory through bounded discovery
and its machine-readable task identity.

Read the implementation's complete report.md, result.json, task-diff.patch,
retained pre/post files, and test logs. The owner's latest screenshots
contain the implementation summary followed by the older shadow-resolution
report; do not confuse those two tasks.

Scope
Review these reported changes against their retained pre-task state:
- src/customization/CopilotAssetCatalog.ts
- src/test/suite/copilotWorkflowCustomization.test.ts
- src/test/suite/workflowEmptyProjectBootstrap.test.ts

Inspect directly relevant production dependencies and existing tests only
where needed to assess a concrete claim.

Review criteria
1. Confirm the live files match the implementation's recorded post-state.
   Separate this task's delta from pre-existing uncommitted work.
   Do not use the editor's changed-file panel as the authoritative diff.

2. Verify the actual generated etl-validate-write body now includes:
   explicit consumer-root selection, workspaceRoot usage consistent with
   tool schemas, exclusion of extension/source/reference roots, no reliance
   on workspace-folder order, and consistent preview/approval/write targets.

   Ensure job/env evidence requirements do not block workflow initialization
   in an explicitly selected empty project.

3. Confirm the change preserves qualified tool names, approval requirements,
   side-effect restrictions, asset identity/path/profile membership, and
   unrelated asset content. Verify the managed version change is limited
   to the intended asset: 1.1.4 to 1.1.5.

4. Assess the permanent tests against real production APIs:
   - previous generated fixture authenticity;
   - corrected content generation;
   - Audit detecting the stale asset;
   - approval required before Upgrade;
   - only the intended asset upgraded;
   - updated version/hash and post-upgrade audit;
   - preservation of user-owned content and existing conflict safeguards;
   - empty-project initialization remains supported.

   Distinguish properties actually tested from source-only conclusions.
   Check existing coverage before declaring a missing test.

5. Verify retained red/green evidence:
   - new tests fail behaviorally with the previous producer;
   - the corrected producer was restored;
   - typecheck succeeds;
   - customization changes from 51 passing/3 failing to 53 passing/3 failing;
   - bootstrap changes from 13 passing/0 failing to 14 passing/0 failing;
   - packageAssets records 34 passing/0 failing.

   Compare the identities and causes of the three retained failures.
   Equal failure counts alone do not establish no regression.

6. Account for the disclosed test-compilation changes to out/ and
   .tsbuildinfo.test using retained records. Compilation was authorized;
   do not create a new blocker merely because build artifacts changed.
   Distinguish test compilation from VSIX packaging. Do not restore or
   clean those artifacts during this review.

Execution boundaries
No source edits, compiler/test execution, Host launch, Copilot request,
packaging, installation, Git mutation, consumer upgrade, or reference-state
updates. Use retained evidence and ordinary read-only inspection.
Do not create another helper framework or inspect chat/session stores.

Delivery
Create only a concise report.md and result.json in a new review directory.

Return:
- ACCEPTED, ACCEPTED_WITH_LIMITATIONS, or CHANGES_REQUIRED;
- concrete findings with supporting file/evidence references;
- verified test scope and retained limitations;
- readiness of the exact source state for candidate preparation.

If accepted, identify the next bounded delivery step: package the accepted
source and verify the existing consumer asset's supported upgrade in the
reusable isolated environment. Do not execute that step in this review.

Keep installed delivery, original job/env write verification, and release
acceptance explicitly unclaimed.
