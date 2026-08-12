Continue from:

LOCAL_VSIX_PACKAGE_READY_WITH_DOCUMENTED_WAIVERS

You are authorized to install the exact locally built VSIX into the local VS Code installation.

ARTIFACT

* Extension ID:
    td-etl.databricks-etl-copilot
* Version:
    3.139
* VSIX:
    C:\repos\etl-extension\etl_fw2\local-release-artifacts\databricks-etl-copilot-0.3.139.vsix
* Expected SHA-256:
    e6ce31f2d1d2a9217e9a4e295bbf2816642eff5613858c39c86872d69d208e98

SAFETY RULES

* Do not modify the repository or artifact.
* Do not stage, commit, push, edit PR #7, or interact with CI.
* Do not read .env, GH, or GH_TOKEN.
* Do not click Keep or Undo.
* Do not uninstall the existing extension.
* Do not reload, restart, or close VS Code automatically.

PREFLIGHT

1. Confirm the VSIX exists.
2. Recompute SHA-256 and require an exact match.
3. Record:
    * code --version
    * currently installed version of td-etl.databricks-etl-copilot, if any.
4. Reconfirm the main repository HEAD, index, unstaged files, PR, and CI remain untouched.

INSTALLATION

If the extension is not currently installed, run:

code --install-extension "C:\repos\etl-extension\etl_fw2\local-release-artifacts\databricks-etl-copilot-0.3.139.vsix"

If a different version is installed, first attempt the same normal installation command.

If version 0.3.139 is already installed and VS Code refuses to replace it because the version is unchanged, one force installation is explicitly authorized only for this exact verified VSIX:

code --install-extension "C:\repos\etl-extension\etl_fw2\local-release-artifacts\databricks-etl-copilot-0.3.139.vsix" --force

Do not use --force for any other extension or artifact.

POST-INSTALL VERIFICATION

1. Require installation exit code 0.
2. Run code --list-extensions --show-versions.
3. Require:
    td-etl.databricks-etl-copilot@0.3.139
4. Confirm the VSIX hash and source artifact remained unchanged.
5. Confirm no repository, PR, CI, token, worktree, or review-card state changed.
6. Do not launch the extension or perform a smoke test in this step.
7. Tell the user to run Developer: Reload Window manually.

Finish with exactly:

LOCAL_VSIX_INSTALLED_RELOAD_REQUIRED

or

LOCAL_VSIX_INSTALL_BLOCKED_<EXACT_REASON>
