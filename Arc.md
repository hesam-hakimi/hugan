TASK: HF1_V2_LOCAL_INSTALL_0_3_145_AND_ACTIVATION_GATE

The verified package result was:

VERSION_AND_PACKAGE_RESULT:
PASS_READY_FOR_LOCAL_INSTALL_AND_RUNTIME_QA

The repository owner now authorizes installation of the verified local package:

databricks-etl-copilot-0.3.145.vsix

Perform only the LOCAL_INSTALL_AND_ACTIVATION stage.

Before installation:

- verify the VSIX still exists;
- recompute its SHA-256 and compare it with the previously verified package;
- inspect the manifest and confirm:
  - extension ID: td-etl.databricks-etl-copilot
  - version: 0.3.145;
- record the currently installed version of this extension;
- verify no concurrent Agent mutation.

Install the VSIX into the normal local VS Code installation so it is available to
all workspaces, including the Development Test Workspace.

Use the canonical local command equivalent to:

code --install-extension "<absolute-path-to-databricks-etl-copilot-0.3.145.vsix>" --force

Do not perform a workspace-specific installation.

After installation, independently verify through the VS Code CLI that:

td-etl.databricks-etl-copilot@0.3.145

is the installed version.

Do not:

- modify any repository file;
- modify or delete any VSIX;
- start Runtime QA yet;
- invoke @etl before Reload;
- access or modify the Development Test Workspace;
- create Preview or execute Write;
- commit, push, stage, stash or tag;
- install any other extension or dependency.

Return:

VSIX_SHA256_MATCHES_VERIFIED_PACKAGE: YES/NO
INSTALLED_VERSION_BEFORE: <value or NONE>
INSTALL_COMMAND_EXIT_CODE: <number>
INSTALLED_EXTENSION_ID: <value>
INSTALLED_VERSION_AFTER: <value>
INSTALL_SCOPE: LOCAL_VSCODE_ALL_WORKSPACES
REPOSITORY_CHANGED_BY_INSTALL: YES/NO
RUNTIME_QA_STARTED: NO
READY_FOR_VSCODE_RELOAD: YES/NO

End exactly with one:

LOCAL_INSTALL_RESULT:
PASS_READY_FOR_RELOAD_AND_RUNTIME_QA

LOCAL_INSTALL_RESULT:
FAIL_PACKAGE_IDENTITY

LOCAL_INSTALL_RESULT:
FAIL_INSTALLATION

LOCAL_INSTALL_RESULT:
FAIL_UNAUTHORIZED_CHANGE
