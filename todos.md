Stop all CI/CD investigation. The current product goal is local-only development and packaging.

Do not wait for, rerun, cancel, diagnose, or modify GitHub Actions. Leave Draft PR #7 and its queued check unchanged.

LOCAL BUILD SOURCE

* Repository:
    C:\repos\etl-extension\etl_fw2\etl_framework_extension
* Branch:
    feature/v3-agentic-redesign
* Exact source commit:
    b2e44c3a1a051aa7fa6008931d225bc06d22e847

Build only from this committed SHA in a new isolated temporary directory.

Do not build from the dirty main worktree. The following unstaged files must remain untouched and must not enter the package:

* .tsbuildinfo.test
* package.json
* src/customization/CopilotAssetCatalog.ts
* src/tools/EtlActionToolService.ts

HARD RULES

* Do not read or use .env, GH, or GH_TOKEN.
* Do not modify the main repository.
* Do not stage, commit, amend, push, pull, merge, rebase, reset, restore, clean, or create Commit 10.
* Do not edit or disable CI workflows.
* Do not click Keep or Undo.
* Do not bump the extension version.
* Do not install global npm packages.
* Do not overwrite an existing VSIX artifact.

PHASE 1 — DISCOVER LOCAL BUILD PROCEDURE

From the committed SHA, inspect:

* package.json
* package scripts
* declared Node/npm requirements
* VS Code extension manifest fields
* documented compile, test, prepublish, and VSIX packaging commands

Use repository-declared commands instead of inventing commands.

PHASE 2 — CREATE ISOLATED SOURCE SNAPSHOT

Export the exact committed SHA into a uniquely named temporary directory outside the repository.

Confirm that:

* snapshot commit source is the approved SHA;
* none of the four unstaged files came from the main worktree;
* .env and credentials are absent.

PHASE 3 — DEPENDENCIES

Prefer a compatible lockfile and npm ci.

The existing ignored package-lock.json, if considered for the temporary snapshot, must first match this hash:

79645d6a4df11aabc30f16b608f3249018eb46c5

Copy it only into the temporary build directory and never modify the original.

If it is incompatible with the committed package.json, use npm install --package-lock=false only inside the temporary directory and clearly report that dependency installation was not lockfile-reproducible.

PHASE 4 — LOCAL VALIDATION

Run the repository-declared:

1. compile/build command;
2. fast unit-test command, if available;
3. VS Code prepublish command, if defined.

Do not run tests requiring external enterprise services unless the repository explicitly requires them for packaging.

Any compile or test failure is a hard stop. Do not bypass it.

PHASE 5 — BUILD VSIX

Use the repository-declared local VSCE dependency or packaging script.

Create one VSIX without publishing it.

Copy the completed artifact to a new uniquely named directory under:

C:\repos\etl-extension\etl_fw2\local-release-artifacts

Verify the VSIX contains:

* the extension manifest;
* compiled runtime JavaScript;
* required resources/copilot/** packaged assets;
* no .env;
* no credentials;
* no temporary evidence files;
* no unintended source worktree artifacts.

Compute its SHA-256 hash.

Do not install or replace an existing extension yet. Instead, provide the exact non-force VS Code installation command for the generated VSIX.

FINAL REPORT

Report:

* extension name, ID, and version;
* absolute VSIX path;
* SHA-256;
* dependency installation method;
* compile/build command and result;
* tests executed and result;
* package command and result;
* VSIX content verification;
* exact manual installation command;
* confirmation that the repository, PR, CI, token, unstaged files, and review card remained untouched.

Finish with exactly one:

LOCAL_VSIX_PACKAGE_READY

or

LOCAL_VSIX_BUILD_BLOCKED_<EXACT_REASON>
