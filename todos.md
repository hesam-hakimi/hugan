TASK: HF1_V2_INSTALL_EXACT_VERIFIED_0_3_141_AND_VERIFY_RUNTIME_ACTIVATION

Execute this task only from the single-root Development Test Workspace.

Expected workspace:

* classification: DEVELOPMENT_TEST_WORKSPACE;
* expected root folder name: etl-acz9999-hf1v2-qa;
* exactly one open workspace root;
* no extension-source checkout;
* no etl-framework-adb;
* synthetic QA inputs only;
* workflow customization already initialized;
* STTM present at:
    sttm/qa_hf1v2_demo_sttm.md

This task installs the exact independently verified 0.3.141 VSIX and determines
whether the current Extension Host is actually running it.

Do not run Runtime QA Phase 1.
Do not create a Preview ID.
Do not approve or execute ETL writes.
Do not create job_conf/** or env_conf/**.
Do not modify the STTM or workflow customization.
Do not access Databricks or real data.
Do not commit, push, install dependencies, or modify source code.

The only permitted access outside the Development Test Workspace is read-only
access to this exact verified artifact:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix

Do not inspect the containing source repository or any other file within it.

==================================================

1. VERIFY DEVELOPMENT TEST WORKSPACE
    ==================================================

Capture and report:

* absolute workspace root;
* workspace root count;
* root folder name;
* STTM presence;
* workflow customization presence;
* existing job_conf file count;
* existing env_conf file count;
* existing generated ETL artifact count;
* extension-source checkout absence;
* etl-framework-adb absence.

Required:

WORKSPACE_CLASSIFICATION: DEVELOPMENT_TEST_WORKSPACE
WORKSPACE_ROOT_COUNT: 1
STTM_INPUT_FOUND: YES
WORKFLOW_SETUP_ALREADY_PRESENT: YES
EXISTING_JOB_CONF_COUNT: 0
EXISTING_ENV_CONF_COUNT: 0
SOURCE_CHECKOUT_PRESENT: NO
ETL_FRAMEWORK_ADB_PRESENT: NO

If the workspace fails these requirements, do not install anything. Stop with:

INSTALL_0_3_141_RESULT: BLOCKED_WORKSPACE_MISMATCH

==================================================
2. VERIFY THE EXACT ARTIFACT BEFORE INSTALLATION

Verify the exact file:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix

Expected identity:

EXPECTED_SIZE_BYTES:
1250393

EXPECTED_SHA256:
437427A915BEB7C0867DD2CE53C968161C99F43730004C702D87799390446B51

EXPECTED_EXTENSION_ID:
td-etl.databricks-etl-copilot

EXPECTED_VERSION:
0.3.141

Calculate the size and SHA-256 directly from the file immediately before
installation.

Read the internal package and manifest metadata and confirm:

* package version is 0.3.141;
* manifest version is 0.3.141;
* publisher is td-etl;
* extension ID is td-etl.databricks-etl-copilot.

If any identity value differs, do not install. Stop with:

INSTALL_0_3_141_RESULT: BLOCKED_ARTIFACT_IDENTITY_MISMATCH

==================================================
3. CAPTURE PRE-INSTALL STATE

Determine the VS Code product and profile used by this current Development Test
Workspace.

Use the CLI associated with this exact VS Code product.

Do not switch between VS Code Stable and Insiders.
Do not guess an active profile name.
Do not install into an unrelated profile.

Capture:

* VS Code product;
* VS Code CLI executable;
* active profile, when deterministically available;
* installed version of td-etl.databricks-etl-copilot;
* runtime-active version, when obtainable from etl_capabilities or live ETL
    Copilot output.

An extension listing is installation inventory only. It is not runtime activation
proof.

Expected prior runtime evidence is 0.3.140, but report the actual current value.

If the active VS Code product/profile cannot be resolved safely, stop with:

INSTALL_0_3_141_RESULT: BLOCKED_PROFILE_UNRESOLVED

==================================================
4. INSTALL THE EXACT VERIFIED VSIX

Install the exact verified artifact into the VS Code product/profile used by this
Development Test Workspace.

Use the equivalent of this canonical command, with the resolved current VS Code
CLI and active profile when required:

code –install-extension “C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix” –force

Do not install from Marketplace.
Do not use another VSIX.
Do not copy the VSIX into the Development Test Workspace.
Do not uninstall the extension first.
Do not modify the VSIX.
Do not install dependencies.

Capture:

* exact installation command;
* exit code;
* complete installation output;
* installed extension inventory after the command.

Required installed inventory:

td-etl.databricks-etl-copilot@0.3.141

If installation fails, stop with:

INSTALL_0_3_141_RESULT: FAIL_INSTALLATION

==================================================
5. HANDLE EXTENSION HOST RELOAD SAFELY

Do not claim that 0.3.141 is runtime-active merely because installation succeeded
or the installed-extension inventory reports 0.3.141.

Check the live Extension Host through:

* etl_capabilities, when available;
* live Databricks ETL Copilot output;
* explicit extension activation output.

If the current Extension Host still reports 0.3.140, a reload is required.

If a supported VS Code action is available to request:

Developer: Reload Window

invoke that action.

Do not terminate VS Code forcibly.
Do not kill processes.
Do not use a different VS Code window.
Do not continue Runtime QA in the old Extension Host.

If reloading interrupts this agent turn, preserve the Development Test Workspace
unchanged. After VS Code reloads, this same task may be rerun; it must recognize
the already-installed 0.3.141 and skip unnecessary reinstallation when the exact
artifact identity and installed version already match.

If the Agent cannot invoke the supported reload action, stop cleanly with:

HOST_RELOAD_REQUIRED: YES
INSTALL_0_3_141_RESULT: PASS_RELOAD_REQUIRED

==================================================
6. POST-RELOAD RUNTIME ACTIVATION PROOF

This section may run only in a freshly reloaded Extension Host.

Use installed-extension runtime evidence such as etl_capabilities and live ETL
Copilot activation output.

Required:

ACTIVE_EXTENSION_ID:
td-etl.databricks-etl-copilot

ACTIVE_EXTENSION_VERSION:
0.3.141

INSTALLED_VERSION:
0.3.141

Do not treat package metadata, the VSIX filename, CLI installation output, or an
installed-directory listing alone as runtime activation proof.

If the installed inventory is 0.3.141 but the freshly reloaded runtime still
reports 0.3.140, stop with:

INSTALL_0_3_141_RESULT: FAIL_STALE_RUNTIME_ACTIVATION

If runtime identity cannot be obtained, stop with:

INSTALL_0_3_141_RESULT: BLOCKED_RUNTIME_IDENTITY_UNPROVEN

If runtime identity is exactly 0.3.141:

RUNTIME_ACTIVATION_PROVEN: YES
READY_FOR_RUNTIME_QA_PHASE_1: YES

Stop without starting Runtime QA Phase 1.

==================================================
7. ZERO-WORKSPACE-MUTATION CHECK

Compare the Development Test Workspace before and after installation/activation.

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
RUNTIME_QA_STARTED: NO

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
HOST_RELOAD_REQUESTED: YES/NO
HOST_RELOAD_REQUIRED: YES/NO
POST_RELOAD_RUNTIME_CHECK_EXECUTED: YES/NO
ACTIVE_EXTENSION_ID: 
ACTIVE_EXTENSION_VERSION: 
RUNTIME_ACTIVATION_PROVEN: YES/NO
WORKSPACE_FILES_CREATED: 
WORKSPACE_FILES_MODIFIED: 
WORKSPACE_FILES_DELETED: 
PREVIEW_ID_CREATED: NO
ETL_WRITE_EXECUTED: NO
SOURCE_REPOSITORY_MODIFIED: NO
RUNTIME_QA_STARTED: NO
READY_FOR_RUNTIME_QA_PHASE_1: YES/NO

End exactly with one:

INSTALL_0_3_141_RESULT: PASS

INSTALL_0_3_141_RESULT: PASS_RELOAD_REQUIRED

INSTALL_0_3_141_RESULT: FAIL_INSTALLATION

INSTALL_0_3_141_RESULT: FAIL_STALE_RUNTIME_ACTIVATION

INSTALL_0_3_141_RESULT: BLOCKED_WORKSPACE_MISMATCH

INSTALL_0_3_141_RESULT: BLOCKED_ARTIFACT_IDENTITY_MISMATCH

INSTALL_0_3_141_RESULT: BLOCKED_PROFILE_UNRESOLVED

INSTALL_0_3_141_RESULT: BLOCKED_RUNTIME_IDENTITY_UNPROVEN
