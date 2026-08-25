TASK: INSTALL_VERIFIED_HF1_V2_VSIX_0_3_142_FOR_DEFAULT_VSCODE_PROFILE

Work only inside the Software Development Environment:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

This task installs the already-built and verified 0.3.142 VSIX into the same
Visual Studio Code Stable Default profile used by all local workspaces on this
laptop.

The Extension is installed for the VS Code user/profile, not separately for each
workspace.

Do not access the Development Test Workspace.
Do not access etl-framework-adb.
Do not modify source, tests, contracts, resources, or package.json.
Do not rebuild, rename, overwrite, or delete the VSIX.
Do not install or download dependencies.
Do not run Runtime QA.
Do not invoke ETL Preview or Write.
Do not connect to real data.
Do not commit, push, merge, tag, stash, reset, restore, clean, stage, or publish.

==================================================

1. VERIFY REPOSITORY AND ARTIFACT
    ==================================================

Expected repository root:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected working source version:

0.3.142

Expected VSIX:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.142.vsix

Expected size:

1251308 bytes

Expected SHA-256:

B392329A4B45C26D6DC17E91F14604B5731286F74B3AFE03603EE57A5F046E23

Verify:

* repository root;
* branch and HEAD;
* staged file count;
* package.json version;
* VSIX path;
* VSIX size;
* VSIX SHA-256;
* archive readability;
* internal package.json version = 0.3.142;
* internal extension.vsixmanifest version = 0.3.142;
* publisher = td-etl;
* Extension ID = td-etl.databricks-etl-copilot.

Capture the complete Git status before installation.

If the artifact identity differs, stop:

INSTALL_0_3_142_RESULT: BLOCKED_ARTIFACT_MISMATCH

If staged files exist, stop:

INSTALL_0_3_142_RESULT: BLOCKED_STAGED_CHANGES

==================================================
2. VERIFY THE SHARED VS CODE INSTALLATION

Expected VS Code product:

Visual Studio Code Stable

Expected CLI:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd

Expected profile:

Default

Verify that this is the same Stable installation and Default profile used by the
Development Test Workspace.

Confirm that no custom --extensions-dir, alternate user-data directory,
Insiders installation, remote Extension Host, or profile override is active.

Report the currently installed version of:

td-etl.databricks-etl-copilot

If a different VS Code product or profile is detected, do not install:

INSTALL_0_3_142_RESULT: BLOCKED_VSCODE_PROFILE_MISMATCH

==================================================
3. INSTALL ONCE FOR THE DEFAULT PROFILE

If version 0.3.142 is already installed in the Stable Default profile:

* do not reinstall;
* continue to verification.

Otherwise run exactly:

& “C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd” --install-extension
“.\databricks-etl-copilot-0.3.142.vsix” --force
–profile “Default”

Do not use the Marketplace.
Do not use a wildcard.
Do not select an artifact by modification time.
Do not uninstall files manually.
Do not install separately inside any consumer workspace.

Capture:

* exact command;
* exit code;
* stdout;
* stderr.

If installation fails:

INSTALL_0_3_142_RESULT: FAIL_INSTALL

==================================================
4. VERIFY INSTALLED VERSION

Using the same Stable CLI and Default profile, verify the installed version:

& “C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd” --list-extensions
–show-versions `
–profile “Default”

Required result:

td-etl.databricks-etl-copilot@0.3.142

Installed-file metadata is sufficient only for this installation task.
Runtime activation will be verified after the Development Test Workspace window
is reloaded.

Do not attempt to open or inspect the Development Test Workspace during this task.

==================================================
5. POST-INSTALL SAFETY CHECK

Recalculate the VSIX size and SHA-256.

Required:

VSIX_SIZE_AFTER: 1251308
VSIX_SHA256_AFTER:
B392329A4B45C26D6DC17E91F14604B5731286F74B3AFE03603EE57A5F046E23

Compare Git status with the initial baseline.

Required:

SOURCE_FILES_MODIFIED_BY_TASK: 0
TEST_FILES_MODIFIED_BY_TASK: 0
PACKAGE_JSON_MODIFIED_BY_TASK: NO
VSIX_MODIFIED_BY_TASK: NO
STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
RUNTIME_QA_STARTED: NO
DEVELOPMENT_TEST_WORKSPACE_ACCESSED: NO

==================================================
6. FINAL REPORT

Return:

REPOSITORY_ROOT: 
BRANCH: 
HEAD: 
SOURCE_VERSION: 
VSIX_PATH: 
VSIX_SIZE_BYTES: 
VSIX_SHA256: 
ARTIFACT_IDENTITY_MATCH: YES/NO
VS_CODE_PRODUCT: 
VS_CODE_CLI: 
TARGET_PROFILE: 
CUSTOM_EXTENSIONS_DIRECTORY_ACTIVE: YES/NO
INSTALLED_VERSION_BEFORE: 
INSTALL_COMMAND: 
INSTALL_EXIT_CODE: 
INSTALLED_VERSION_AFTER: 
SOURCE_FILES_MODIFIED_BY_TASK: 
TEST_FILES_MODIFIED_BY_TASK: 
PACKAGE_JSON_MODIFIED_BY_TASK: YES/NO
VSIX_MODIFIED_BY_TASK: YES/NO
STAGED_FILES: 
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
RUNTIME_QA_STARTED: NO
DEVELOPMENT_TEST_WORKSPACE_ACCESSED: NO
QA_WINDOW_RELOAD_REQUIRED: YES
READY_TO_RELOAD_QA_WINDOW: YES/NO

PASS requires:

* exact verified 0.3.142 VSIX;
* correct VS Code Stable Default profile;
* installed version td-etl.databricks-etl-copilot@0.3.142;
* zero repository or artifact modifications;
* no Runtime QA and no Development Test Workspace access.

End exactly with one:

INSTALL_0_3_142_RESULT: PASS

INSTALL_0_3_142_RESULT: BLOCKED_ARTIFACT_MISMATCH

INSTALL_0_3_142_RESULT: BLOCKED_STAGED_CHANGES

INSTALL_0_3_142_RESULT: BLOCKED_VSCODE_PROFILE_MISMATCH

INSTALL_0_3_142_RESULT: FAIL_INSTALL
