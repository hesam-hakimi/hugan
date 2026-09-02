# Phase 1B.3B — File-Sidecar Native Execution Bridge Preflight

This task only verifies a file-sidecar workaround for the broken native stdout
and exit-code return path.

Do not continue Phase 1B.3, edit repository files, compile, run tests, launch an
Extension Host, invoke an ETL tool, or consume the parser budget.

The Agent is expected to have `ELECTRON_RUN_AS_NODE` in its environment and may
receive blank native stdout and a null `$LASTEXITCODE`. Do not retry native
commands because of that outer symptom.

## Authoritative paths

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:

fix/workspace-write-completion-0.3.148

Expected HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected exact Git status:

 M .github/templates/request.md
 M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Git:

C:\Program Files\TD Git\cmd\git.exe

Node:

C:\Program Files\nodejs\node.exe

VS Code:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe

Expected VS Code version first line:

1.135.0

Protected file:

.github/templates/request.md

Expected SHA-256:

2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84

## Prohibitions

Do not:

- edit any repository or QA-workspace file;
- run npm, compile, Mocha, tests, `runTests`, or F5;
- invoke Code.exe except once with `--version`;
- launch an Extension Development Host;
- invoke `vscode.lm.invokeTool` or any ETL tool;
- use `Start-Process`;
- use `$env:ComSpec` to select the shell;
- stage, commit, stash, restore, reset, or clean;
- retry the wrapper invocation.

`Code.exe --version` is not an Extension Host launch.

## 1. Create a unique Temp evidence directory

Using PowerShell cmdlets only, create exactly one directory:

C:\Users\tag5916\AppData\Local\Temp\etl-native-sidecar-<new-guid-without-hyphens>

Verify that it is outside both the repository and QA workspace.

Set:

- `$runDir` to that absolute directory;
- `$wrapperPath` to `bridge.cmd` inside it.

Create the wrapper with `Set-Content -Encoding Ascii`.

## 2. Wrapper content

Substitute the absolute `$runDir` value for `@@RUN_DIR@@` and write exactly this
logical wrapper:

@echo off
setlocal DisableDelayedExpansion
set "RUN_DIR=@@RUN_DIR@@"
set "REPO=C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147"
set "GIT_EXE=C:\Program Files\TD Git\cmd\git.exe"
set "NODE_EXE=C:\Program Files\nodejs\node.exe"
set "CODE_EXE=C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe"

set "ERAN_BEFORE=ABSENT"
if defined ELECTRON_RUN_AS_NODE set "ERAN_BEFORE=PRESENT"
>"%RUN_DIR%\eran.before.txt" echo %ERAN_BEFORE%

set "VSCODE_CLI_BEFORE=ABSENT"
if defined VSCODE_CLI set "VSCODE_CLI_BEFORE=PRESENT"
>"%RUN_DIR%\vscode-cli.before.txt" echo %VSCODE_CLI_BEFORE%

set "NO_ATTACH_BEFORE=ABSENT"
if defined ELECTRON_NO_ATTACH_CONSOLE set "NO_ATTACH_BEFORE=PRESENT"
>"%RUN_DIR%\no-attach.before.txt" echo %NO_ATTACH_BEFORE%

set "COMSPEC_BEFORE=ABSENT"
if defined ComSpec set "COMSPEC_BEFORE=PRESENT"
>"%RUN_DIR%\comspec.before.txt" echo %COMSPEC_BEFORE%

set "ELECTRON_RUN_AS_NODE="
set "VSCODE_CLI="
set "ELECTRON_NO_ATTACH_CONSOLE="
set "ComSpec=C:\Windows\System32\cmd.exe"

set "ERAN_AFTER=ABSENT"
if defined ELECTRON_RUN_AS_NODE set "ERAN_AFTER=PRESENT"
>"%RUN_DIR%\eran.after.txt" echo %ERAN_AFTER%

set "VSCODE_CLI_AFTER=ABSENT"
if defined VSCODE_CLI set "VSCODE_CLI_AFTER=PRESENT"
>"%RUN_DIR%\vscode-cli.after.txt" echo %VSCODE_CLI_AFTER%

set "NO_ATTACH_AFTER=ABSENT"
if defined ELECTRON_NO_ATTACH_CONSOLE set "NO_ATTACH_AFTER=PRESENT"
>"%RUN_DIR%\no-attach.after.txt" echo %NO_ATTACH_AFTER%

set "COMSPEC_AFTER=ABSENT"
if defined ComSpec set "COMSPEC_AFTER=PRESENT"
>"%RUN_DIR%\comspec.after.txt" echo %COMSPEC_AFTER%

set "ERRORLEVEL="

"%GIT_EXE%" --version 1>"%RUN_DIR%\git.stdout.txt" 2>"%RUN_DIR%\git.stderr.txt"
set "GIT_RC=%ERRORLEVEL%"
>"%RUN_DIR%\git.exit.txt" echo %GIT_RC%

"%NODE_EXE%" --version 1>"%RUN_DIR%\node.stdout.txt" 2>"%RUN_DIR%\node.stderr.txt"
set "NODE_RC=%ERRORLEVEL%"
>"%RUN_DIR%\node.exit.txt" echo %NODE_RC%

"%CODE_EXE%" --version 1>"%RUN_DIR%\code.stdout.txt" 2>"%RUN_DIR%\code.stderr.txt"
set "CODE_RC=%ERRORLEVEL%"
>"%RUN_DIR%\code.exit.txt" echo %CODE_RC%

"%GIT_EXE%" -C "%REPO%" rev-parse HEAD 1>"%RUN_DIR%\head.stdout.txt" 2>"%RUN_DIR%\head.stderr.txt"
set "HEAD_RC=%ERRORLEVEL%"
>"%RUN_DIR%\head.exit.txt" echo %HEAD_RC%

"%GIT_EXE%" -C "%REPO%" rev-parse --abbrev-ref HEAD 1>"%RUN_DIR%\branch.stdout.txt" 2>"%RUN_DIR%\branch.stderr.txt"
set "BRANCH_RC=%ERRORLEVEL%"
>"%RUN_DIR%\branch.exit.txt" echo %BRANCH_RC%

"%GIT_EXE%" -C "%REPO%" status --porcelain=v1 --untracked-files=all 1>"%RUN_DIR%\status.stdout.txt" 2>"%RUN_DIR%\status.stderr.txt"
set "STATUS_RC=%ERRORLEVEL%"
>"%RUN_DIR%\status.exit.txt" echo %STATUS_RC%

>"%RUN_DIR%\done.tmp" echo COMPLETE
move /y "%RUN_DIR%\done.tmp" "%RUN_DIR%\done.txt" >nul 2>nul
exit /b 0

Important wrapper rules:

- Do not place a native command and its `%ERRORLEVEL%` capture inside a
  parenthesized block.
- Do not place another command between a native command and its errorlevel
  capture.
- Do not use `&&`.
- Do not invoke npm or another `.cmd` file.

## 3. Invoke the wrapper exactly once

Invoke exactly once:

& 'C:\Windows\System32\cmd.exe' /d /q /c $wrapperPath

Blank returned output and null `$LASTEXITCODE` from the Agent shell are expected.
Do not retry.

## 4. Wait using PowerShell cmdlets only

Using PowerShell cmdlets only, poll for:

$runDir\done.txt

Poll approximately every 200 milliseconds for no more than 30 seconds.

Require its trimmed content to be exactly:

COMPLETE

If it does not appear, stop BLOCKED without retrying.

## 5. Validate sidecar evidence

Using PowerShell cmdlets only, read and require:

- `eran.before.txt`: `PRESENT` or `ABSENT`;
- `eran.after.txt`: exactly `ABSENT`;
- `vscode-cli.after.txt`: exactly `ABSENT`;
- `no-attach.after.txt`: exactly `ABSENT`;
- `comspec.after.txt`: exactly `PRESENT`;
- all six `*.exit.txt` files: exactly integer `0`;
- Git, Node, and Code stdout files: nonempty;
- all six stderr files: empty;
- Code stdout first nonempty line: exactly `1.135.0`;
- HEAD: exact expected SHA;
- branch: exact expected branch;
- Git status: exactly the three expected lines, including leading spaces, with
  no additional line.

Calculate the protected request.md SHA-256 using `Get-FileHash` and require the
expected hash.

Do not use previously observed Terminal results as a substitute for a missing
sidecar.

## 6. Cleanup and report

Confirm:

- repository edits: 0;
- compiles/tests/F5: 0;
- Extension Host launches: 0;
- `invokeTool` calls: 0;
- parser calls: 0.

After retaining all validated evidence in the response:

- on PASS, remove only the exact unique `$runDir` using PowerShell cmdlets;
- on BLOCKED, retain it and report its exact path.

End with exactly one marker:

F5_FILE_SIDECAR_NATIVE_BRIDGE_PASS

or

F5_FILE_SIDECAR_NATIVE_BRIDGE_BLOCKED
