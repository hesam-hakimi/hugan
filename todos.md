TASK_ID: ETL-0909-PREVIEW-CONTAINMENT-INDEPENDENT-REVIEW01
TYPE: INDEPENDENT REVIEW OF THE COMPLETED REPAIR DELTA
LANGUAGE: English only for conversation, code and artifacts.

REVIEWED_TASK:
ETL-0909-PREVIEW-CONTAINMENT-REPAIR01

OBJECTIVE
Independently assess whether the completed repair prevents escaping
destinations from becoming approvable preview entries while preserving
the existing write-time guard and valid consumer destinations.

Review the actual implementation and evidence. Do not implement fixes.
Do not reopen unrelated accepted work.

1. INPUTS AND IDENTITY

Active worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:
fix/workspace-write-completion-0.3.148

Resolve the reviewed task's evidence directory through bounded direct-child
task-prefix discovery under C:\docs. Authenticate its task identity using
machine records, not directory recency or screenshot-transcribed hashes.

Read the complete issued repair brief, report.md, result.json, task.diff,
pre-edit records and relevant original compiler/test logs.
Follow the explicit REPRO01 references only where needed to establish F-1.

Verify the exact diff endpoints against authenticated pre-edit bytes
and the live reviewed post-state, including both new files.

Reported mutation set:
- src/core/trusted/WriteAuthorization.ts
- src/writers/RepoWriter.ts
- src/tools/EtlActionToolService.ts
- src/chat/WriteCoordinator.ts
- src/chat/DeployCoordinator.ts
- src/test/suite/workspaceWriteCollision.test.ts
- src/test/testPatterns.ts
- src/core/utils/ArtifactWriteContainment.ts [new]
- src/test/suite/previewDestinationContainment.test.ts [new]

Reported baseline transition:
10 pre-existing dirty paths to 19; original ten unchanged.
HEAD, branch and staging unchanged; repository out/ unchanged.

Confirm these against actual records. Do not restore or repair drift.
Check for concurrent writers before reviewing.

2. REQUIRED REVIEW

Read complete affected implementations and their immediate consumers.

A. Manifest boundary
Verify buildWriteManifestFiles requires the actual selected consumer root
at every caller, without a default-root or empty-root bypass.
Check that invalid write destinations are rejected before preview storage,
approvable rendering or approval eligibility.
Check mixed valid/invalid sets and unchanged valid destination contents.

B. Shared containment
Compare the extracted routine with the original RepoWriter implementation.
Verify lexical and physical containment checks, their ordering, errors,
and protected-path policy remain equivalent.
Confirm the writer still independently checks immediately before each
write; preview approval must not cache away that protection.
Inspect junction/symlink handling and uncertainty/failure behavior.

C. Write versus reference destinations
Verify every destination classified as "reference"/UNCHANGED is genuinely
non-mutating throughout its consumers.
Do not accept the exclusion merely because the report calls it intentional.
Check that a write cannot be misclassified to bypass validation.
Keep unrelated input-read policy outside this repair's scope.

D. Error propagation — explicit acceptance question
The repair reports throwing Error from writeToWorkspace instead of
returning a structured "Write Blocked" response.

Trace actual handling through EtlActionToolService, WriteCoordinator
and DeployCoordinator, and compare it with the issued repair requirement
for the existing structured blocker mechanism.

Determine whether this is contract-compatible failure handling or a
material unmet requirement. Check for false success, lost blockers,
partial authorization, uncaught failures or unintended continuation.

Similarity to a pre-existing conflict error is not, by itself, proof of
acceptance. Do not automatically classify this issue as a limitation.

E. Tests and evidence
Verify the identical final regression was used against authentic
pre-edit and post-edit product code, and both trees compiled successfully.

Reported targeted results:
pre-edit: 1 passing / 5 failing;
post-edit: 6 passing / 0 failing.

Inspect the retained first-attempt assertion correction:
distinguish direct writer behavior, which may handle valid members
individually, from the preview route, which must not authorize the invalid
member. Confirm the correction did not weaken the required preview check.

Verify test adapter instrumentation supports the claimed absence of write
attempts. A no-op filesystem adapter cannot establish successful writing.

Check the reported unchanged adjacent failures and timeout explanation
from original logs. Do not describe the whole test set as passing.

3. PROPORTIONATE VERIFICATION AUTHORITY

Source and existing evidence are read-only.
Create only a fresh exclusive review evidence directory and task-owned
temporary fixtures.

You may use existing installed compiler/test tooling to independently
execute the six-test containment regression against verified source,
with necessary output directed outside the repository.

Use additional targeted checks only to resolve a concrete review risk.
Reuse authenticated adjacent-suite evidence rather than automatically
rerunning all eleven suites or the protocol-3/STTM campaign.

No source edits, repository out/ promotion, Host, actual product writes,
approval tokens, package installation, Git mutation, packaging, cloud
operations, reference updates or pending-editor resolution.

Never use a stale REPRO01 preview ID or treat its temporary workspace
as approved for writing.

4. REVIEW RESULT

Return report.md and result.json containing:
- Authenticated reviewed source/diff identities.
- Acceptance decision and its exact scope.
- Findings with code/evidence locations and practical impact.
- Error-propagation contract decision.
- Shared-containment and write/reference-boundary decisions.
- Actual independent checks and retained limitations.
- Source, output and evidence preservation results.
- The smallest conditional next gate.

Use ACCEPTED, ACCEPTED_WITH_LIMITATIONS, or CHANGES_REQUIRED.
Do not hide unmet requirements in a limitations section.

REAL_VSCODE_FILESYSTEM_WRITE_VERIFIED: NO
ORIGINAL_PRODUCT_WRITE_FIX_VERIFIED: NO
INSTALLED_OR_RELEASE_ACCEPTANCE: NOT_GRANTED

If accepted, identify the remaining prerequisites for a separately bounded
real-filesystem guarded-write smoke. The current test-mode registration
gap and simulated filesystem are not resolved by this source review.
Accepted earlier runtime remains evidence for its original candidate;
it does not automatically qualify these newly changed sources.

If changes are required, return the smallest coherent correction scope.
Do not implement it or launch another task.

Stop after delivering the review.
