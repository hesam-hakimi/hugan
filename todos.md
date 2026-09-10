TASK_ID: ETL-0910-WORKFLOW-GITIGNORE-DISCLOSURE-FIX01
TYPE: SMALL PRODUCT DISCLOSURE FIX WITH PERMANENT REGRESSION TEST

Use English for all communication, code, tests, and reports.

ENVIRONMENT
Local Windows Agent.
Expected worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Resolve actual baseline identities from the retained machine records.
Do not copy hashes from screenshots.

OBJECTIVE
Fix finding F-1: workflow initialization creates or updates the managed
.gitignore, but the real approval dialog lists only the catalog assets.

Before the user clicks Initialize, the dialog must explicitly disclose
that .gitignore may also be created or updated in the selected root.

AUTHORIZED EDITS
Only:
1. src/customization/CopilotWorkflowCommands.ts
2. src/test/suite/workflowEmptyProjectBootstrap.test.ts

Keep the change small. Do not redesign the workflow, approval-plan
schema, writer, test infrastructure, or root classification.

CONTEXT AND PREFLIGHT
Read the complete report and result for:
- ETL-0909-WORKFLOW-EMPTY-PROJECT-INDEPENDENT-REVIEW01
- ETL-0909-WORKFLOW-EMPTY-PROJECT-HOST-SMOKE01

Locate them through bounded direct-child discovery under C:\docs and
machine-recorded task identities. Follow relevant linked records.

The independent review accepted the bootstrap with limitations.
HOST-SMOKE01 reported PASS for the Base profile in a real development
Host: cancellation wrote nothing; approval created eight catalog assets
plus .gitignore. Installed-extension qualification remains unverified.

Verify the two edit targets against their recorded post-state, and
confirm the expected repository baseline and no concurrent writer.
Preserve all existing dirty changes. If a material mismatch exists,
report it without repairing the baseline.

IMPLEMENTATION
- Locate the actual Initialize approval dialog used by the registered
  workflow command.
- Preserve the selected root and complete catalog asset list.
- Add a clear English disclosure before approval, for example:
  "This also creates or updates the managed .gitignore in this folder
  for generated workflow files."
- Put this in the real modal message or detail, visible before the
  decision. Logging it afterward is insufficient.
- Match the wording to actual behavior. Do not claim byte-preservation
  of an existing .gitignore: the separate EOL finding F-2 remains open.
- Preserve Initialize/Cancel behavior and all write guards.
- Do not change generated content, asset counts, or writer behavior.
- Do not close F-2 through F-5 or U-1/U-2 through this fix.

PERMANENT TEST
Extend the existing bootstrap test suite using its current command
registration and VS Code dialog fixture.

Test the arguments passed to the actual approval dialog:
- selected root remains visible;
- catalog asset paths remain visible;
- .gitignore creation/update is disclosed before approval resolves.

Retain the existing cancellation check proving zero files, including
no .gitignore. Reuse that case rather than duplicating its setup.

The test must exercise the production command, not a copied formatting
function or a search for text in source files.

VALIDATION
Use existing local dependencies and the existing focused test method.
Run the focused regression and bootstrap suite, plus the relevant
TypeScript check.

Where practical, run the new assertion before the product edit to
confirm the intended failure, then verify it passes after the edit.
Do not create full pre/post source-tree copies for this small change.

Keep permanent test logic in the repository test file.
Reuse the existing runner/adapter; do not create a new JavaScript
testing framework or new helper scripts under C:\docs.
Place necessary compiler output in a fresh disposable build directory,
leaving repository out/ and historical evidence untouched.

No broad suite reruns or real Host rerun are required in this task.
If the existing focused method cannot run within this boundary,
report the exact blocker instead of inventing another harness.

BOUNDARIES
No dependency installation, Git mutation, version bump, packaging,
VSIX installation, release, real consumer writes, or reference updates.
Local test writes are permitted only in fresh temporary fixtures.
Do not resolve pending editor changes.

DELIVERY
Perform a focused author review of the two-file delta.
Retain a compact report.md, result.json, exact task diff, and actual
test/compiler output in one fresh evidence directory.

Record commands, exit codes, test counts, and changed-file identities.
Do not claim that the old Host run executed this new source.

End with:
TASK_ID:
STATUS: LOCAL_CHECKED_AWAITING_DELTA_REVIEW / BLOCKED
CHANGED_FILES:
F1_DISCLOSURE_IMPLEMENTED:
PERMANENT_REGRESSION_TEST:
FOCUSED_TEST_RESULT:
TYPECHECK_RESULT:
AUTHOR_REVIEW:
RETAINED_FINDINGS:
REPOSITORY_OUT_CHANGED: NO
REAL_HOST_EXECUTED_THIS_TASK: NO
INSTALLED_OR_RELEASE_ACCEPTANCE: NOT_GRANTED
EVIDENCE_ROOT:
NEXT_CONDITIONAL_GATE: REVIEW_THIS_SMALL_DELTA_BEFORE_VSIX_PREPARATION

Stop after delivering the result. Do not start packaging or another task.
