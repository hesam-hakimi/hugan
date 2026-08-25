TASK: INSTALL_VERIFIED_HF1_V2_VSIX_0_3_143_FOR_DEFAULT_VSCODE_PROFILE

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Install the exact verified 0.3.143 VSIX into the Visual Studio Code Stable Default
profile used by all local workspaces on this laptop.

Do not access the Development Test Workspace.
Do not access etl-framework-adb.
Do not modify source, tests, fixtures, contracts, resources, or package.json.
Do not rebuild, rename, overwrite, or delete any VSIX.
Do not install or download dependencies.
Do not run Runtime QA.
Do not invoke Preview or Write.
Do not commit, push, merge, tag, stage, stash, reset, restore, or clean.

==================================================

1. VERIFY THE EXACT ARTIFACT
    ==================================================

Expected repository root:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected source version:

0.3.143

Expected VSIX:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.143.vsix

Expected size:

1255490 bytes

Expected SHA-256:

8819E0902BF5FE1F8EFE9BA302EB196D3715AF17DC5F44876E3C0EACBD03CFFA

Verify:

* repository identity;
* branch and HEAD;
* staged file count;
* package.json version;
* VSIX path, size, and SHA-256;
* archive readability;
* internal package.json version = 0.3.143;
* internal extension.vsixmanifest version = 0.3.143;
* publisher = td-etl;
* Extension ID = td-etl.databricks-etl-copilot.

If artifact identity differs, stop:

INSTALL_0_3_143_RESULT: BLOCKED_ARTIFACT_MISMATCH

If staged files exist, stop:

INSTALL_0_3_143_RESULT: BLOCKED_STAGED_CHANGES

==================================================
2. VERIFY THE VS CODE TARGET

Expected product:

Visual Studio Code Stable

Expected CLI:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd

Expected profile:

Default

Verify:

* no Insiders product;
* no alternate user-data directory;
* no custom extensions directory;
* no remote Extension Host;
* no profile override.

Report the currently installed version of:

td-etl.databricks-etl-copilot

Accepted starting versions:

* 0.3.142;
* 0.3.143.

Any other starting version is a conflict:

INSTALL_0_3_143_RESULT: BLOCKED_VSCODE_PROFILE_MISMATCH

==================================================
3. INSTALL ONCE FOR THE DEFAULT PROFILE

If 0.3.143 is already installed:

* do not reinstall;
* continue to verification.

Otherwise run exactly:

& “C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd” --install-extension
“.\databricks-etl-copilot-0.3.143.vsix” --force
–profile “Default”

Do not use the Marketplace.
Do not use a wildcard or newest-file selector.
Do not uninstall or delete Extension directories manually.
Do not install separately inside the QA workspace.

If installation fails:

INSTALL_0_3_143_RESULT: FAIL_INSTALL

==================================================
4. VERIFY THE INSTALLED VERSION

Run:

& “C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd” --list-extensions
–show-versions `
–profile “Default”

Required:

td-etl.databricks-etl-copilot@0.3.143

Runtime activation will be verified only after reloading the Development Test
Workspace window.

==================================================
5. POST-INSTALL SAFETY CHECK

Recalculate the VSIX identity.

Required:

VSIX_SIZE_AFTER: 1255490

VSIX_SHA256_AFTER:
8819E0902BF5FE1F8EFE9BA302EB196D3715AF17DC5F44876E3C0EACBD03CFFA

Compare repository status with the initial baseline.

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

End exactly with one:

INSTALL_0_3_143_RESULT: PASS

INSTALL_0_3_143_RESULT: BLOCKED_ARTIFACT_MISMATCH

INSTALL_0_3_143_RESULT: BLOCKED_STAGED_CHANGES

INSTALL_0_3_143_RESULT: BLOCKED_VSCODE_PROFILE_MISMATCH

INSTALL_0_3_143_RESULT: FAIL_INSTALL
