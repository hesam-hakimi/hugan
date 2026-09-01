Prepare and launch the real VS Code Extension Development Host for manual W1 runtime QA. Do not perform the runtime QA itself in this turn.

Current source repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Requirements:

1. Verify the repository path, current branch, current HEAD, and git status --short.
2. The expected branch is:

fix/workspace-write-completion-0.3.148

3. The working tree and index must be clean. Stop if they are not clean.
4. Do not create or modify .vscode/launch.json.
5. Do not edit, stage, commit, reset, clean, stash, or push anything.
6. Locate the existing synthetic_workbook.xlsx fixture from the repository. Do not modify it.
7. Create a new uniquely named isolated QA workspace under the Windows temporary directory, outside the source repository.
8. Inside that temporary workspace, create:

sttm\synthetic_workbook.xlsx

by copying the existing synthetic workbook fixture.
9. Confirm that the QA workspace is not nested inside the extension source repository and contains no consumer or production files.
10. Verify that the compiled extension entry point exists. Run npm run compile only if the compiled development output is missing. If compilation is required, verify afterward that git status --short remains empty.
11. Discover the available VS Code CLI command (code or code.cmd) and use it only to launch a new real Extension Development Host window with:

* the current repository as --extensionDevelopmentPath;
* the newly created temporary QA directory as the opened workspace;
* a new VS Code window.

12. Do not invoke any ETL tool, do not write ETL artifacts, and do not run the QA prompt yet.
13. Do not use a normal VS Code window as a substitute. Confirm that the launched window is running the current extension development source.

Report:

* repository path;
* branch;
* full HEAD SHA and subject;
* source worktree status;
* temporary QA workspace path;
* source path of the copied workbook;
* destination path of the copied workbook;
* exact VS Code launch command;
* whether the Extension Development Host opened successfully;
* final source git status --short.

Return exactly one verdict:

EXTENSION_DEVELOPMENT_HOST_READY

or:

EXTENSION_DEVELOPMENT_HOST_BLOCKED
