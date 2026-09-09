TASK_ID: ETL-0909-WORKFLOW-EMPTY-PROJECT-HOST-SMOKE01
TYPE: BOUNDED REAL VSCODE WORKFLOW VERIFICATION

Use English for all communication, UI guidance, reports, and artifacts.

OBJECTIVE
Verify the accepted empty-project workflow bootstrap through a real
VS Code Extension Development Host, real selection/confirmation dialogs,
and real filesystem writes in one fresh temporary consumer folder.

This is verification, not implementation or release.

AUTHORITATIVE INPUTS
Resolve and read the complete report and result for:
ETL-0909-WORKFLOW-EMPTY-PROJECT-INDEPENDENT-REVIEW01

Follow its machine-recorded links to:
ETL-0909-WORKFLOW-EMPTY-PROJECT-BOOTSTRAP01

Use bounded direct-child discovery under C:\docs. Authenticate task
identity and source/build relationships from machine records.
Never derive hashes from screenshots or choose evidence by timestamp alone.

Carry forward:
- Review result: ACCEPTED_WITH_LIMITATIONS.
- The new 13-test suite and regression red/green evidence were authenticated.
- Adjacent-suite totals lacked retained output; do not claim them verified.
- F-1 through F-5 and U-1/U-2 remain recorded limitations.
- No installed-extension or release acceptance exists.

PRECONDITIONS
Verify the reviewed source identities, worktree, branch, HEAD, staged
state, and dirty set against the review records.

Check for an active writer or conflicting Host. Do not launch a duplicate,
terminate unrelated processes, resolve pending editor changes, or repair
a mismatching baseline.

AUTHORITY
You may:
- Create a fresh evidence directory and a fresh temporary consumer folder.
- Prepare an isolated development-host launch surface outside the repository.
- Launch the existing local VS Code executable with isolated user-data
  and extension directories.
- Exercise the actual workflow initialization command and real dialogs.
- Create only the selected packaged workflow assets and their managed
  .gitignore within the explicitly confirmed temporary consumer root.
- Preserve the resulting evidence and temporary test output.

Do not:
- Change product source, tests, references, repository output, or Git.
- Install dependencies, package a VSIX, install the candidate into the
  user's normal VS Code profile, publish, or release.
- Write to any real consumer repository or reference checkout.
- Execute unrelated ETL jobs, publishing, deployment, or broad test suites.
- Substitute mocks, direct initializer calls, or filesystem adapters for
  the real Host path.

RUNTIME PREPARATION
Reuse the authenticated BOOTSTRAP01 external compiled output when its
identity and completeness support a real development-host launch.

Resolve required runtime resources, package metadata, and existing
dependencies from actual files. Keep any necessary staging outside the
repository and record its source-to-staging identities.

Do not launch the stale repository out/ as though it contained bootstrap.
Do not rebuild merely for convenience. If the retained build cannot
support an authentic launch without additional changes, report the exact
blocker and smallest required preparation; do not expand scope.

Record the actual loaded extension path, version, and compiled-code
identity. Version text alone is not sufficient proof.

ONE BOUNDED SCENARIO
1. Create a genuinely empty temporary folder outside protected roots.
   Open it as the only workspace folder in the isolated Host.
   Record its exact absolute path and initial empty inventory.

2. Invoke the registered command:
   databricks-etl-copilot.initializeCopilotWorkflow

   Use the base profile for the smallest packaged asset set.

3. Exercise one cancellation at the real confirmation flow.
   Verify zero consumer-file writes, including no .gitignore creation.

4. Invoke the same command again and complete the real profile selection,
   root confirmation, and Initialize approval.

   Before approval, record the actual root and exact planned asset paths.
   Explicitly disclose that the existing implementation also creates a
   managed .gitignore. This task authorizes that additional file only in
   this temporary root; it does not resolve product disclosure finding F-1.

   Do not bypass the product's confirmation flow.

5. Verify actual created files against the packaged catalog and expected
   written content, including managed metadata where applicable.
   Record the .gitignore content separately.

   Verify no unexpected files or artificial ETL marker directories were
   created, and no writes escaped the temporary consumer root.

6. Capture real Target Resolution and Setup Outcome messages, dialog
   selections, created/blocked/conflicted counts, and relevant Host logs.

Use real UI interaction if available. If your environment cannot operate
the dialogs, prepare everything first, then give the owner one concise
English instruction containing the exact window, command, profile,
temporary root, and buttons to use. Do not simulate their answers or
claim completion while waiting.

EVIDENCE AND PRESERVATION
Keep a small evidence bundle:
- launch/source identity record;
- before/after consumer inventory;
- actual preview and confirmed write set;
- relevant Host/output logs and UI evidence;
- content verification;
- repository preservation check;
- report.md and result.json.

Retain existing evidence unchanged. Do not delete retained directories
to make the earlier incorrect cleanup claim appear true.
Do not rerun adjacent suites to recreate missing historical evidence.

ASSESSMENT
A successful run establishes only the exercised real development-host
empty-project workflow scenario.

It does not establish installed VSIX qualification, release readiness,
all profiles, all multi-root cases, or the original job/env write fix.

If blocked or failing, preserve the concrete symptom and stop without
implementing a fix.

FINAL FIELDS
TASK_ID:
STATUS: PASS / FAIL / BLOCKED / WAITING_FOR_OWNER_UI
LOADED_EXTENSION_IDENTITY:
TEMPORARY_CONSUMER_ROOT:
REAL_VSCODE_HOST_USED:
REAL_DIALOGS_EXERCISED:
CANCELLATION_ZERO_WRITES:
APPROVED_ASSET_SET:
MANAGED_GITIGNORE_DISCLOSED_FOR_THIS_RUN:
ACTUAL_CREATED_FILES:
CONTENT_VERIFICATION:
UNEXPECTED_OR_OUTSIDE_ROOT_WRITES:
REPOSITORY_CHANGED: NO
RETAINED_LIMITATIONS:
EMPTY_PROJECT_WORKFLOW_HOST_VERIFIED:
EMPTY_PROJECT_WORKFLOW_INSTALLED_VERIFIED: NO
INSTALLED_OR_RELEASE_ACCEPTANCE: NOT_GRANTED
EVIDENCE_ROOT:
REPORT_PATH:
RESULT_PATH:
NEXT_CONDITIONAL_GATE:

Stop after delivering the result.
