TASK_ID: ETL-0910-INSTALLED-WORKFLOW-SMOKE01
TYPE: BOUNDED PRIVATE VSIX INSTALLATION AND WORKFLOW VERIFICATION

Use English for all communication, UI guidance, reports, and artifacts.

GOAL
Install the exact private 0.3.148 VSIX produced by
ETL-0910-VSIX-CANDIDATE-PREP01 and verify the Base-profile empty-project
workflow through the installed extension.

Do not rebuild or repackage.

INPUT AND IDENTITY
Resolve PREP01 through its machine-recorded task identity under C:\docs.
Read its complete report.md and result.json, package inventory, and
relevant verification records.

Obtain the actual VSIX path, SHA-256, size, and packaged file identities
from those records. Recompute the VSIX hash before installation.
Never transcribe hashes from screenshots.

Expected:
- Extension ID: td-etl.databricks-etl-copilot
- Candidate version: 0.3.148
- PREP01 status: CANDIDATE_BUILT_AND_CONTENT_VERIFIED

The source repository remaining at version 0.3.147 is expected:
PREP01 changed version metadata only in packaging staging.
Do not "repair" the repository version.

Carry forward the recorded vsce 3.7.1 versus pinned 3.9.2 deviation.
Do not treat packaging as release qualification. If an applicable
governing rule makes that exact tool pin mandatory for this private
installation, identify the rule and stop rather than waive it.

INSTALLATION BOUNDARY
Use the existing local VS Code executable.

Install the candidate once into one isolated test environment with
dedicated user-data and extensions directories, reusable across test
folders. Do not install separately per workspace or replace the owner's
normal extension installation.

Check for an already-running execution of this task before starting.
If the exact candidate is already installed in this test environment,
authenticate it and reuse it instead of reinstalling.

Use normal VS Code installation and reload behavior.
Do not use --extensionDevelopmentPath or load the staged source.
Do not bypass platform trust or signature checks.

Use existing required extensions where available. If the declared
GitHub Copilot Chat dependency is disabled, use normal Enable/Reload
within this test environment and record it.
Do not request credentials or install additional dependencies.
Report a concrete dependency blocker if necessary.

PROVE WHAT IS RUNNING
After installation and reload, record:
- actual VS Code version and test-environment paths;
- installed extension ID, version, and installation path;
- activation evidence tied to the workflow command;
- installed entrypoint, runtime bundles, and resources matching the
  VSIX inventory, allowing only identified installation metadata.

Version text alone is insufficient.
The extension must run without a link to repository node_modules,
staged sources, or repository out/.

ONE FOCUSED SCENARIO
Create one fresh, genuinely empty temporary consumer folder outside
the source and reference trees. Open it as the only workspace folder.

Use the real Command Palette command:
ETL: Initialize Copilot Workflow

Registered command:
databricks-etl-copilot.initializeCopilotWorkflow

1. Choose Base through the real profile picker.
2. Confirm the exact temporary root through the real folder modal.
3. Capture the Initialize approval dialog.
   Verify it displays:
   - the selected destination;
   - all eight Base catalog asset paths;
   - the managed .gitignore creation/update disclosure.

The product dialog itself must disclose .gitignore.
An external disclosure record cannot substitute for this check.

4. Cancel at the Initialize approval.
   Verify the consumer folder remains empty, including no .gitignore.

5. Invoke the same command again and approve through the real dialogs.
   This task authorizes only the displayed Base assets, their necessary
   parent directories, and managed .gitignore in this temporary root.

6. Verify:
   - exactly eight catalog assets plus .gitignore were created;
   - asset content and managed metadata match the installed catalog;
   - no unexpected files or artificial ETL marker directories exist;
   - recorded writes remain within the selected consumer root;
   - output and notifications accurately report the result.

Use existing UI automation if available. Do not stub dialogs, invoke
the initializer directly, or create another automation framework.
If manual interaction is required, prepare the environment first and
give the owner one concise English instruction with the exact window,
root, command, profile, and buttons. Never claim unobserved clicks.

PRESERVATION AND EVIDENCE
Leave the repository, candidate VSIX, and earlier evidence unchanged.
Record relevant before/after checks without a broad machine scan.

Retain a compact report.md, result.json, installation/activation logs,
dialog evidence, and consumer before/after inventory with content checks.

Only close processes started by this task after preserving evidence.
Keep the installed test environment identifiable for later use.

No source changes, compiler, packaging, broad suites, Git mutation,
reference updates, real consumer writes, ETL jobs, deployment, or release.

ASSESSMENT
A PASS verifies only the installed 0.3.148 Base-profile initialization
scenario in one empty, single-root temporary workspace.

Do not claim:
- all profiles or multi-root behavior qualified;
- Repair/Upgrade disclosure fixed;
- the original job/env write defect verified;
- full product or release acceptance.

Keep F-2 through F-5 and U-1/U-2 recorded.

FINAL FIELDS
TASK_ID:
STATUS: PASS / FAIL / BLOCKED / WAITING_FOR_OWNER_UI
VSIX_IDENTITY:
INSTALLED_EXTENSION_IDENTITY:
ACTIVATION_VERIFIED:
TEMPORARY_CONSUMER_ROOT:
REAL_GITIGNORE_DISCLOSURE_VISIBLE:
CANCELLATION_ZERO_WRITES:
CREATED_FILES:
CONTENT_VERIFICATION:
UNEXPECTED_OR_OUTSIDE_ROOT_WRITES:
REPOSITORY_CHANGED: NO
EMPTY_PROJECT_WORKFLOW_INSTALLED_VERIFIED:
VERIFICATION_SCOPE: BASE_PROFILE_EMPTY_SINGLE_ROOT
FULL_PRODUCT_OR_RELEASE_ACCEPTANCE: NOT_GRANTED
RETAINED_LIMITATIONS:
EVIDENCE_ROOT:
REPORT_PATH:
RESULT_PATH:
NEXT_CONDITIONAL_GATE:

If failing, preserve the exact symptom and stop without implementing
a fix. If passing, report the remaining qualification gaps without
starting another task.
