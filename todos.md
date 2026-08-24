TASK: INSTALL_AND_ACTIVATE_VERIFIED_HF1_V2_VSIX_0_3_142

Work only from the Development Test Workspace:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa

This task installs and verifies the exact already-built 0.3.142 VSIX.

Do not start Runtime QA Phase 1.
Do not interpret the STTM.
Do not invoke ETL Preview or Write.
Do not create a Preview ID.
Do not approve any filesystem operation.
Do not create, modify, rename, or delete workspace files.
Do not inspect or modify Extension source.
Do not inspect or modify etl-framework-adb.
Do not rebuild or modify the VSIX.
Do not install dependencies.
Do not commit or push.
Do not connect to real data.

The only permitted external file access is reading and installing this exact VSIX:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.142.vsix

==================================================

1. WORKSPACE IDENTITY GATE
    ==================================================

Confirm:

EXPECTED_WORKSPACE_ROOT:
C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa

EXPECTED_WORKSPACE_ROOT_COUNT:
1

EXPECTED_WORKSPACE_CLASSIFICATION:
DEVELOPMENT_TEST_WORKSPACE

Expected conditions:

* exactly one open workspace root;
* no Extension-source checkout open;
* no etl-framework-adb open;
* workspace is not a Git source repository;
* workflow customization is already initialized;
* STTM exists at:
    sttm/qa_hf1v2_demo_sttm.md
* no existing job_conf/**;
* no existing env_conf/**;
* no existing generated ETL artifacts.

If the root or topology differs, stop without installing:

INSTALL_0_3_142_RESULT: BLOCKED_WRONG_WORKSPACE

==================================================
2. CAPTURE ZERO-WRITE BASELINE

Before installation, capture:

* complete workspace file inventory;
* file size and SHA-256 for every existing workspace file;
* STTM size and SHA-256;
* workflow customization asset list and hashes;
* job_conf file count;
* env_conf file count;
* generated ETL artifact count.

Expected:

EXISTING_JOB_CONF_COUNT: 0
EXISTING_ENV_CONF_COUNT: 0
EXISTING_GENERATED_ETL_ARTIFACT_COUNT: 0

Do not modify the workspace while collecting the baseline.

==================================================
3. VERIFY THE EXACT VSIX

Verify the exact external artifact:

EXPECTED_VSIX_PATH:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.142.vsix

EXPECTED_VSIX_SIZE_BYTES:
1251308

EXPECTED_VSIX_SHA256:
B392329A4B45C26D6DC17E91F14604B5731286F74B3AFE03603EE57A5F046E23

Independently inspect the archive metadata and confirm:

* archive is readable;
* internal package.json version is 0.3.142;
* internal extension.vsixmanifest version is 0.3.142;
* publisher is td-etl;
* package name is databricks-etl-copilot;
* resolved Extension ID is td-etl.databricks-etl-copilot.

Do not inspect any sibling source files.

If path, size, SHA-256, identity, or internal versions differ, stop without
installation:

INSTALL_0_3_142_RESULT: BLOCKED_ARTIFACT_MISMATCH

==================================================
4. IDENTIFY THE CORRECT VS CODE INSTANCE

Confirm the current QA window uses Visual Studio Code Stable and determine:

* VS Code product/version;
* CLI path belonging to that same Stable installation;
* current user-data profile;
* current Extension installation state;
* installed td-etl.databricks-etl-copilot version;
* active Extension Host runtime version.

Expected Stable CLI from the previous verified QA environment:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd

Expected profile:

Default Stable standard user-data profile with no profile override.

Do not target Insiders, ETL HotFix, another profile, or another VS Code window.

Installed-directory metadata alone is not runtime activation proof.

Accepted starting runtime versions:

* 0.3.141;
* 0.3.142.

Any unrelated active version is a conflict:

INSTALL_0_3_142_RESULT: BLOCKED_RUNTIME_IDENTITY

==================================================
5. INSTALL ONLY IF REQUIRED

If the exact 0.3.142 artifact is already installed:

* do not reinstall it;
* continue to runtime activation verification.

If 0.3.142 is not installed, use the verified Stable CLI and exact VSIX path:

& “C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd” --install-extension
“C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.142.vsix” `
–force

Capture:

* exact command;
* exit code;
* stdout/stderr;
* installed version after the command.

Do not use marketplace installation.
Do not use a wildcard or newest-file selector.
Do not uninstall another version separately.
Do not delete Extension directories manually.

If installation fails:

INSTALL_0_3_142_RESULT: FAIL_INSTALL

==================================================
6. EXTENSION HOST ACTIVATION

Installation metadata is insufficient.

Prove that the Extension Host serving this exact QA window has activated:

ACTIVE_EXTENSION_ID:
td-etl.databricks-etl-copilot

ACTIVE_EXTENSION_VERSION:
0.3.142

Use fresh runtime evidence from this QA window, such as:

* current ETL Copilot Output channel;
* newly timestamped Extension Host activation log;
* installed runtime capability output after activation.

Required runtime evidence must include the equivalent of:

ETL Copilot version: 0.3.142

Do not use stale 0.3.141 log entries or package metadata as activation proof.

If installation succeeds but the current Extension Host still reports 0.3.141:

* do not start Runtime QA;
* do not create a Preview;
* do not mutate the workspace;
* preserve this Chat;
* return:

HOST_RELOAD_REQUIRED: YES
INSTALL_0_3_142_RESULT: RELOAD_REQUIRED

If a supported non-destructive VS Code Reload Window action is available, it may
be requested. Do not kill VS Code processes or restart the computer.

After Reload Window, continue in this same Chat with:

CONTINUE_INSTALL_0_3_142_POST_RELOAD_VERIFICATION

Then repeat only Sections 6–8. Do not reinstall when the exact version is already
installed.

==================================================
7. POST-INSTALL ZERO-MUTATION VERIFICATION

Compare the workspace directly against the Section 2 baseline.

Required:

NEW_JOB_CONF_FILES: 0
NEW_ENV_CONF_FILES: 0
NEW_GENERATED_ETL_ARTIFACTS: 0
STTM_MODIFIED: NO
WORKFLOW_CUSTOMIZATION_MODIFIED: NO
WORKSPACE_FILES_CREATED: 0
WORKSPACE_FILES_MODIFIED: 0
WORKSPACE_FILES_DELETED: 0
PREVIEW_ID_CREATED: NO
ETL_WRITE_EXECUTED: NO
REAL_DATA_ACCESSED: NO
SOURCE_REPOSITORY_MODIFIED: NO
VSIX_MODIFIED: NO

Recalculate the external VSIX size and SHA-256 and confirm they remain:

SIZE_BYTES:
1251308

SHA256:
B392329A4B45C26D6DC17E91F14604B5731286F74B3AFE03603EE57A5F046E23

==================================================
8. FINAL REPORT

Return:

WORKSPACE_CLASSIFICATION: 
WORKSPACE_ROOT: 
WORKSPACE_ROOT_COUNT: 
STTM_INPUT_FOUND: YES/NO
WORKFLOW_SETUP_ALREADY_PRESENT: YES/NO
EXISTING_JOB_CONF_COUNT: 
EXISTING_ENV_CONF_COUNT: 
VS_CODE_PRODUCT: 
VS_CODE_CLI: 
ACTIVE_PROFILE: 
VERIFIED_VSIX_PATH: 
VERIFIED_VSIX_SIZE_BYTES: 
VERIFIED_VSIX_SHA256: 
ARTIFACT_IDENTITY_MATCH: YES/NO
INSTALLED_VERSION_BEFORE: 
RUNTIME_VERSION_BEFORE: 
INSTALL_COMMAND: 
INSTALL_EXIT_CODE: 
INSTALLED_VERSION_AFTER: 
HOST_RELOAD_REQUIRED: YES/NO
ACTIVE_EXTENSION_ID: 
ACTIVE_EXTENSION_VERSION: 
RUNTIME_ACTIVATION_PROVEN: YES/NO
NEW_JOB_CONF_FILES: 
NEW_ENV_CONF_FILES: 
NEW_GENERATED_ETL_ARTIFACTS: 
STTM_MODIFIED: YES/NO
WORKFLOW_CUSTOMIZATION_MODIFIED: YES/NO
WORKSPACE_FILES_CREATED: 
WORKSPACE_FILES_MODIFIED: 
WORKSPACE_FILES_DELETED: 
PREVIEW_ID_CREATED: YES/NO
ETL_WRITE_EXECUTED: YES/NO
REAL_DATA_ACCESSED: YES/NO
SOURCE_REPOSITORY_MODIFIED: YES/NO
VSIX_MODIFIED: YES/NO
RUNTIME_QA_STARTED: NO
READY_FOR_RUNTIME_QA_PHASE_1: YES/NO

PASS requires:

* correct single Development Test Workspace;
* exact verified 0.3.142 artifact identity;
* correct Stable VS Code instance/profile;
* installed version 0.3.142;
* active runtime version 0.3.142 proven from fresh runtime evidence;
* zero workspace mutations;
* no Preview, Write, real-data access, source modification, or Runtime QA.

End exactly with one:

INSTALL_0_3_142_RESULT: PASS

INSTALL_0_3_142_RESULT: RELOAD_REQUIRED

INSTALL_0_3_142_RESULT: BLOCKED_WRONG_WORKSPACE

INSTALL_0_3_142_RESULT: BLOCKED_ARTIFACT_MISMATCH

INSTALL_0_3_142_RESULT: BLOCKED_RUNTIME_IDENTITY

INSTALL_0_3_142_RESULT: FAIL_INSTALL
