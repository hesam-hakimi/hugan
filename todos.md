TASK: HF1_V2_RUNTIME_QA_PHASE_1_PREVIEW_ONLY_VERSION_0_3_147

ROLE
Act as the installed ETL Extension runtime QA orchestrator.

This is a product runtime test of the locally installed VSIX.

EXPECTED EXTENSION

Extension ID: td-etl.databricks-etl-copilot
Expected version: 0.3.147

ENVIRONMENT

- Local VS Code Extension Host
- Development Test Workspace
- Not the ETL Extension source repository
- Not the recovery worktree
- Not SIT or Production
- Synthetic/test inputs only

BOUNDARIES

This phase is preview-only and read-only.

Do not:

- modify workspace files;
- create or update ETL assets;
- execute an approved write;
- create a Databricks job;
- access real business data;
- commit, stage, stash, push or merge;
- modify VS Code settings;
- install another extension;
- access or repair the ETL Extension source repository;
- regenerate test fixtures;
- claim Runtime QA passed if the installed version cannot be verified.

PHASE 1 — INSTALLED PRODUCT IDENTITY

Verify and report:

- active Extension ID;
- active Extension version;
- Extension activation status;
- local versus remote Extension Host;
- currently opened workspace root;
- whether the workspace is a permitted Development Test Workspace;
- whether any ETL source-repository path is present.

Expected:

- ID = td-etl.databricks-etl-copilot
- version = 0.3.147
- local Extension Host
- source repository absent

If version 0.3.147 is not active, stop with:

BLOCKED_WRONG_INSTALLED_VERSION

PHASE 2 — PACKAGED RESOURCE DISCOVERY

Using only the installed Extension and current test workspace, verify:

- ETL Orchestrator is available;
- required packaged Agent resources are readable;
- required tools are registered;
- STTM document-understanding guidance is available;
- runtime does not depend on access to the maintainer source repository;
- no missing packaged resource or absolute developer-machine path is observed.

Do not inspect the source repository as a fallback.

PHASE 3 — TEST INPUT DISCOVERY

Locate an existing authorized synthetic STTM/runtime-QA input in the Development
Test Workspace.

Do not copy a fixture from the source repository.

The input should support as many of these cases as already available:

- active mapping;
- inactive mapping;
- conflicting state;
- unresolved reference;
- malformed short row;
- malformed oversized row;
- structured and Markdown diagnostic output.

If no authorized test input exists, stop with:

BLOCKED_AUTHORIZED_TEST_INPUT_NOT_AVAILABLE

PHASE 4 — PREVIEW-ONLY WORKFLOW

Invoke the installed ETL workflow in analysis/preview mode.

The workflow must:

1. Resolve the current workspace.
2. Resolve the selected synthetic STTM input.
3. Analyze existing workspace/environment evidence.
4. Produce a preview manifest.
5. Stop before approval or write.
6. Perform no workspace mutation.

Verify the preview distinguishes:

- CREATE;
- MODIFY;
- UNCHANGED;
- CONFLICT;
- BLOCKED;

where applicable to the selected synthetic scenario.

PHASE 5 — STRUCTURED DIAGNOSTIC QA

Verify through the public consumer-visible output:

- structured parser diagnostics are present;
- Markdown diagnostics are present;
- malformed rows fail closed;
- malformed rows receive no active authority;
- diagnostic codes agree between structured and Markdown channels;
- affected-row identities agree;
- valid mapping IDs and order remain preserved;
- no internal-only model assertion is used as a substitute for public output;
- no source attribute value is leaked through diagnostic messages.

Do not claim a scenario was tested if it was unreachable from the selected
authorized input.

PHASE 6 — WRITE-CONTAINMENT PROOF

After preview completes, prove:

- no file was created;
- no file was modified;
- no workspace setting was changed;
- no managed asset was recorded;
- no job was submitted;
- no explicit approval was requested or assumed;
- no source-repository path was accessed;
- Git status of the test workspace is unchanged, if it is a Git workspace.

FINAL REPORT

Keep the report concise and product-focused.

Report:

INSTALLED_EXTENSION_ID
INSTALLED_EXTENSION_VERSION
EXTENSION_HOST
EXTENSION_ACTIVATED
TEST_WORKSPACE
SOURCE_REPOSITORY_ACCESSED
PACKAGED_AGENT_RESOURCES_AVAILABLE
REQUIRED_TOOLS_AVAILABLE
AUTHORIZED_TEST_INPUT
WORKFLOW_PREVIEW_STARTED
WORKFLOW_PREVIEW_COMPLETED
PREVIEW_MANIFEST_PRESENT
STRUCTURED_DIAGNOSTIC_CHANNEL_PRESENT
MARKDOWN_DIAGNOSTIC_CHANNEL_PRESENT
DIAGNOSTIC_CODES_EQUAL
DIAGNOSTIC_ROW_IDENTITIES_EQUAL
MALFORMED_ROWS_FAIL_CLOSED
MALFORMED_ROWS_ACTIVE_AUTHORITY
VALID_MAPPING_IDS_AND_ORDER_PRESERVED
WORKSPACE_FILES_CREATED
WORKSPACE_FILES_MODIFIED
JOB_SUBMITTED
EXPLICIT_APPROVAL_EXECUTED
NEW_RUNTIME_REGRESSIONS
READY_FOR_BOUNDED_WRITE_RUNTIME_QA

Allowed verdicts:

- PASS_READY_FOR_BOUNDED_WRITE_RUNTIME_QA
- BLOCKED_WRONG_INSTALLED_VERSION
- BLOCKED_EXTENSION_ACTIVATION
- BLOCKED_PACKAGED_RESOURCE_MISSING
- BLOCKED_AUTHORIZED_TEST_INPUT_NOT_AVAILABLE
- BLOCKED_PREVIEW_RUNTIME_FAILURE
- BLOCKED_UNEXPECTED_WORKSPACE_MUTATION

Do not start the bounded-write phase in this session.
