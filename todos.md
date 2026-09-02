# Phase 1B.3D — Gated Compile and One-Shot Real-Host Structured-Result Characterization

Mode: verify, compile, and run the existing focused characterization only.

Continue in this same normal Claude Agent chat.
Do not use ETL Orchestrator.
Keep F5 stopped and all breakpoints disabled; do not delete them.

Authoritative completed prerequisite:

F5_FILE_SIDECAR_NATIVE_BRIDGE_PASS

## Objective

Using the accepted file-sidecar transport:

1. statically validate the existing runner and characterization test;
2. compile exactly once in an isolated compile wrapper;
3. validate the compiled artifacts without launching VS Code;
4. only if every gate passes, invoke the compiled test runner exactly once
   in a second sanitized wrapper.

The one permitted run must establish whether the real VS Code Extension Host
preserves the `application/json` LanguageModelDataPart returned by
`etl_interpret_sttm`.

## Fixed identities

Repository:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Branch:
fix/workspace-write-completion-0.3.148

HEAD:
45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

QA root:
C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

Workbook:
C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982\sttm\synthetic_workbook.xlsx

Workbook size:
13201 bytes

Workbook SHA-256:
3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA

Installed Code:
C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe

Expected normalized Code version:
1.135.0

Extension ID:
td-etl.databricks-etl-copilot

Extension version:
0.3.147

Package main:
./out/extension.js

Protected file:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147\.github\templates\request.md

Protected SHA-256:
2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84

Runner:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147\src\test\runTest.ts

Required runner SHA-256:
A7483429C0569CB62221E7FCD3650DD1BA29D64D67B366DD7E7F46ABA6D54BEC

Characterization test:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147\src\test\suite\sttmRealHostStructuredResult.test.ts

Required test SHA-256:
8713EC3B3F2F75B06541F9B68AC4D9026CA0A17D052E07898EA12C5E12FAABCE

Expected Git status, exactly and in this order:
' M .github/templates/request.md'
' M src/test/runTest.ts'
'?? src/test/suite/sttmRealHostStructuredResult.test.ts'

Focused suite title:
Phase 1B real host structured result characterization

Executables:
- cmd: C:\Windows\System32\cmd.exe
- git: C:\Program Files\TD Git\cmd\git.exe
- node: C:\Program Files\nodejs\node.exe
- npm: C:\Program Files\nodejs\npm.cmd

## Authorization and budgets

Authorized:

- authored source edits: 0;
- generated compiler output under existing out/** paths;
- exactly one compile command;
- exactly one compile-wrapper invocation;
- at most one run-wrapper invocation;
- at most one compiled test-runner invocation;
- at most one real Extension Host launch;
- at most one vscode.lm.invokeTool call;
- at most one etl_interpret_sttm parser call;
- no retries.

## Absolute prohibitions

- Do not edit any source, test, configuration, fixture, package, lockfile,
  documentation, or launch configuration.
- Do not add runner sanitation or change launchArgs in this phase.
- Do not remove or reorder the existing positional launch argument.
- Never modify, restore, format, stage, delete, or otherwise touch request.md.
- Do not stage, commit, stash, restore, reset, clean, switch, merge, or rebase.
- Do not write into the QA root.
- Hashing the XLSX is allowed, but do not manually open, parse, convert, or copy it.
- Do not create a replacement test, runner, launcher, or harness.
- Do not invoke Code.exe --version.
- Do not use Start-Process.
- Do not use npm test.
- Do not press F5.
- Do not use ETL Orchestrator.
- Do not download or install VS Code or extensions.
- Do not access Marketplace.
- Do not use --disable-extensions.
- Do not invoke any ETL tool except the single etl_interpret_sttm call
  already implemented by the focused test.
- Do not retry any wrapper, compile, test runner, host, invokeTool, or parser.
- Do not weaken any assertion.
- Do not delete the resulting evidence directory.

## Step 1 — Cmdlet-only static gate

Use only PowerShell cmdlets and .NET reads.

1. Canonicalize and validate all fixed paths.

2. Recompute and require the exact hashes for:
   - request.md;
   - src/test/runTest.ts;
   - src/test/suite/sttmRealHostStructuredResult.test.ts;
   - synthetic_workbook.xlsx.

3. Require workbook size 13201 bytes.

4. Capture a sorted QA inventory containing relative path, size, and SHA-256.
   Require exactly 23 files.

5. Read Code.exe ProductVersion and FileVersion through VersionInfo without
   executing it. Normalize to three numeric components and require 1.135.0.

6. Read completely, without editing:
   - package.json;
   - tsconfig.json and any referenced build config;
   - src/test/runTest.ts;
   - src/test/suite/index.ts;
   - src/test/suite/sttmRealHostStructuredResult.test.ts;
   - src/test/testPatterns.ts;
   - node_modules/@vscode/test-electron/package.json;
   - the installed @vscode/test-electron 2.5.2 runTest implementation.

7. Require all of the following:
   - package version is 0.3.147;
   - package main is ./out/extension.js;
   - @vscode/test-electron version is 2.5.2;
   - package.json has an existing compile script;
   - the compile script and any precompile script are compile-only and do not
     execute tests, Code.exe, downloads, or Marketplace operations;
   - runTest.ts honors ETL_TEST_VSCODE_EXECUTABLE_PATH;
   - isolated mode uses the installed Code executable and does not download;
   - isolated mode creates unique Temp user-data and extensions directories;
   - isolated mode omits --disable-extensions;
   - runTests(...) has exactly one reachable call and no retry path;
   - neither runTest.ts nor extensionTestsEnv reintroduces
     ELECTRON_RUN_AS_NODE, VSCODE_CLI, or ELECTRON_NO_ATTACH_CONSOLE;
   - the focused suite title matches exactly;
   - MOCHA_GREP and MOCHA_RESULT_FILE are honored;
   - no unrelated test shares the focused suite phrase;
   - the test explicitly activates extension
     td-etl.databricks-etl-copilot;
   - exactly one reachable vscode.lm.invokeTool call exists;
   - its tool name is exactly etl_interpret_sttm;
   - it is outside every loop/retry path;
   - its input explicitly resolves the fixed QA root and workbook;
   - includeAudit is enabled;
   - no other ETL tool can be invoked;
   - the existing test observes the actual public result content parts and
     does not reconstruct structured data from Markdown;
   - all configurable result/evidence paths can be directed to Temp.

8. Record the exact number of tests inside the focused suite and the exact
   evidence environment-variable names already used by the test.
   Do not invent new contracts.

If any static requirement fails, do not compile or launch anything.
Report the exact problem and end with:

F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED

## Step 2 — Create one evidence directory

After the static gate passes, create exactly one unique directory:

$env:TEMP\etl-realhost-structured-<32-lowercase-hex-guid>

Require:

- canonical parent exactly equals $env:TEMP;
- it is outside the repository and QA root;
- no wildcard is used.

Store all manifests, wrappers, stdout, stderr, exit codes, counters,
Mocha output, and characterization evidence only inside this directory.

Write:

- the pre-run QA inventory;
- all preflight hashes;
- an ASCII expected-status.txt containing the exact three status lines,
  with CRLF line endings and a final CRLF.

Retain this directory for every result.

## Step 3 — Compile wrapper, exactly once

Create compile.cmd under the evidence directory.

Requirements:

- use `setlocal DisableDelayedExpansion`;
- clear any environment variable named ERRORLEVEL;
- do not use `&&`;
- do not place command execution and error capture in one parenthesized block;
- capture `%ERRORLEVEL%` on the immediately following line;
- use explicit executable paths.

Inside compile.cmd:

1. Set:
   ComSpec=C:\Windows\System32\cmd.exe

2. Require NODE_OPTIONS to be absent. If present, write ENV_BLOCKED and stop.

3. Remove, rather than set to 0 or false:
   - ELECTRON_RUN_AS_NODE
   - VSCODE_CLI
   - ELECTRON_NO_ATTACH_CONSOLE

4. Capture pre-compile Git HEAD, branch, and porcelain status using the
   explicit Git executable.

5. Require:
   - Git commands exit 0;
   - HEAD and branch match;
   - status matches expected-status.txt exactly.

6. If identity fails, atomically write compile.done containing
   IDENTITY_BLOCKED and exit without compiling.

7. Change directory to the fixed repository.

8. Execute exactly once:

   call "C:\Program Files\nodejs\npm.cmd" run compile

9. Redirect and capture:
   - compile.stdout.txt;
   - compile.stderr.txt;
   - compile.exit.txt.

10. Capture post-compile HEAD, branch, and porcelain status.

11. Atomically publish compile.done.

Invoke compile.cmd exactly once through:

C:\Windows\System32\cmd.exe /d /q /c <exact-compile.cmd-path>

The Agent shell’s stdout or $LASTEXITCODE is not evidence.
Do not retry.

Poll compile.done using PowerShell cmdlets for at most 180 seconds.
If it is absent at the deadline, retain evidence and return BLOCKED.

## Step 4 — Post-compile gate before any host launch

Using only PowerShell cmdlets and .NET reads, require:

- compile.exit.txt trims exactly to 0;
- post-compile HEAD, branch, and status remain exact;
- all fixed source/protected hashes remain exact;
- QA inventory and workbook remain unchanged;
- compiled runner exists at the build-config-derived path;
- compiled focused test exists at the build-config-derived path;
- compiled suite loader includes the focused test;
- compiled runner contains one reachable runTests call and no retry;
- compiled test contains one reachable invokeTool call and no retry;
- compiled tool name and suite title remain exact;
- generated compiled paths correspond to the current source files;
- no compile or precompile test/host execution occurred.

Record SHA-256 values for the compiled runner, compiled test, loader,
and out/tools/index.js.

If any post-compile requirement fails:

- do not create or invoke the run wrapper;
- Extension Host launches remain 0;
- retain all evidence;
- end with:
  F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED

## Step 5 — Real-host run wrapper, exactly once

Only after Step 4 passes, create run.cmd inside the same evidence directory.

Use the same safe batch construction rules.

Before launching Node:

1. Reconfirm Git HEAD, branch, and exact status inside the wrapper.
   If they differ, atomically write run.done as IDENTITY_BLOCKED and stop.

2. Record presence-only tokens for:
   - ELECTRON_RUN_AS_NODE;
   - VSCODE_CLI;
   - ELECTRON_NO_ATTACH_CONSOLE;
   - NODE_OPTIONS;
   - ComSpec.

3. Require NODE_OPTIONS to be absent.

4. Delete:
   - ELECTRON_RUN_AS_NODE;
   - VSCODE_CLI;
   - ELECTRON_NO_ATTACH_CONSOLE.

5. Set:
   ComSpec=C:\Windows\System32\cmd.exe

6. Record after-sanitation tokens and self-gate on:
   - ELECTRON_RUN_AS_NODE=ABSENT;
   - VSCODE_CLI=ABSENT;
   - ELECTRON_NO_ATTACH_CONSOLE=ABSENT;
   - NODE_OPTIONS=ABSENT;
   - ComSpec=PRESENT.

7. Set only the existing contracts confirmed in Step 1:
   - ETL_TEST_VSCODE_EXECUTABLE_PATH to the fixed Code.exe;
   - ETL_TEST_ENABLE_ISOLATED_DEPENDENCIES=1;
   - MOCHA_GREP exactly to the focused suite title;
   - MOCHA_RESULT_FILE to a unique file inside the evidence directory;
   - the existing QA-root/workbook/evidence variables to their fixed paths.

Do not invent an environment variable.

8. Require every result/evidence output path to be outside repo and QA.

9. Write:
   - runner.invocations.txt = 1;
   - host.launch.attempts.txt = 1.

10. Invoke the compiled runner directly exactly once:

"C:\Program Files\nodejs\node.exe" "<derived-compiled-runTest.js-path>"

Do not use npm for this step.

Capture:

- test.stdout.txt;
- test.stderr.txt;
- test.exit.txt.

Capture `%ERRORLEVEL%` immediately.
Never invoke the runner again.

11. Capture post-run Git HEAD, branch, and porcelain status.

12. Atomically publish run.done.

Invoke run.cmd exactly once through:

C:\Windows\System32\cmd.exe /d /q /c <exact-run.cmd-path>

Ignore blank Agent-shell stdout and null $LASTEXITCODE.
Do not retry.

Poll run.done through PowerShell cmdlets for at most 300 seconds.
If absent at the deadline, preserve evidence and return BLOCKED.
Do not launch or kill another process.

## Step 6 — Result validation

Read only the retained evidence.

PASS requires affirmative evidence for every item:

- compile command count exactly 1 and exit 0;
- test-runner invocation exactly 1;
- real Extension Host proven started exactly once;
- installed Code.exe was used;
- no download or Marketplace activity;
- unique isolated user-data/extensions paths were used;
- --disable-extensions was absent;
- extension ID and version were exact;
- extension activation completed;
- ETL tools registered;
- only the focused suite executed;
- all tests within that focused suite passed;
- no unrelated test executed;
- invokeTool was reached exactly once;
- tool name was etl_interpret_sttm;
- parser execution was reached exactly once;
- no other ETL tool was called;
- workbook resolved inside the fixed QA root;
- public LanguageModelToolResult.content contained exactly two ordered parts:
  1. LanguageModelTextPart
  2. LanguageModelDataPart
- text part was nonempty;
- DataPart MIME was exactly application/json;
- DataPart byte array was nonempty;
- UTF-8 decoding and JSON parsing succeeded;
- structured and Markdown channels represented the same STTM result;
- structured data was observed directly, not rebuilt from Markdown;
- deterministic baseline matched:
  - files discovered: 1
  - files read: 1
  - files blocked: 0
  - active mappings: 8
  - audit findings: 6
  - FM_F01417B0_00002 present and active
  - source: customers.cust_name
  - target: target_db.customer_name
- test exit was 0;
- protected/source hashes remain exact;
- QA inventory remains the same 23 files;
- workbook remains byte-identical;
- HEAD, branch, and Git status remain exact;
- nothing was staged or committed.

## Step 7 — Classification

PASS:
Use only if every required compile, runtime, structured-channel,
baseline, count, and integrity assertion is positively verified.

End with:
F5_REAL_HOST_STRUCTURED_RESULT_PASS

FAIL:
Use only if the real host reached the single invokeTool/parser boundary
and directly observed a structured-result assertion mismatch, including:

- missing DataPart;
- wrong part order or count;
- wrong MIME;
- empty/invalid bytes;
- JSON decode failure;
- Markdown/structured disagreement;
- deterministic STTM mismatch.

End with:
F5_REAL_HOST_STRUCTURED_RESULT_FAIL

BLOCKED:
Use for any failure before or outside the observable structured boundary,
including:

- static or identity mismatch;
- compile failure;
- missing compiled artifact;
- environment-sanitation failure;
- pre-activation or registration failure;
- installed-host configuration failure;
- unexpected approval UI;
- timeout;
- missing/ambiguous evidence;
- unverified counts;
- more than one attempted host, invokeTool, or parser call.

End with:
F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED

## Final report

Report:

- final classification and marker;
- retained evidence-directory path;
- compile command and exit;
- source and compiled hashes;
- installed Code identity;
- isolated host path;
- attempted versus proven host counts;
- activation and registration evidence;
- invokeTool and parser counts;
- result part count/order/types/MIME/byte length/JSON decode;
- deterministic STTM comparison;
- pre/post Git and QA integrity;
- exact stopping boundary if not PASS.

Never report an unverified count as 0 or 1.

Do not perform repair, retry, cleanup, or a next phase after the marker.
