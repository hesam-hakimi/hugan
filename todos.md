# Phase 1B.3G — One-Shot Local Real-Host Structured-Result Characterization

Continue in the current desktop VS Code GitHub Copilot Local Agent session.

This phase is HOST-ONLY and ONE-SHOT.

Do not edit any file.
Do not compile.
Do not run any npm script.
Do not press F5.
Do not use Cloud, ETL Orchestrator, a worktree, harness workspace,
batch wrapper, sidecar bridge, Code CLI, or retry.
Do not install, copy, update, disable, or download any extension.

## Fixed repository state

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:

fix/workspace-write-completion-0.3.148

Expected HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected Git status, exactly and in order:

 M .github/templates/request.md
 M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Protected request.md SHA-256:

2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84

Focused-test SHA-256:

8713EC3B3F2F75B06541F9B68AC4D9026CA0A17D052E07898EA12C5E12FAABCE

Required compiled artifact hashes from the successful Phase 1B.3F build:

out/test/runTest.js
9DD31EAB51B18ABA4409FC829ADC3E8A56A72AE6C0673DA8887455D1C03A5A43

out/test/suite/sttmRealHostStructuredResult.test.js
C9CAE36C9BA461FF4B81C73B2DD805C319D86EE6C47EF168734B9612AA6CCAE6

out/test/suite/index.js
D6151E50E5996F048E3E60129B10AB75205A7300988847748A75D0D3BF9222CC

out/tools/index.js
89445385DCD85DF603543BEE4FE3364CA38D690B176DAD3909264F73169A88E6

out/extension.js
F6620C3BEE15619C584A67A86E1C60F13144EF38DB123ED9C4155F6DABE2E007

Installed VS Code:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe

Expected FileVersionInfo version:

1.135.0

QA root:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

Workbook:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982\sttm\synthetic_workbook.xlsx

Workbook size:

13201 bytes

Workbook SHA-256:

3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA

Focused suite title:

Phase 1B real host structured result characterization

Tool name:

etl_interpret_sttm

## Step 1 — Read-only launch gate

Before consuming the single launch:

1. Verify repository path, branch, HEAD and exact Git status.
2. Verify request.md and focused-test hashes.
3. Verify all five compiled artifact hashes exactly.
4. Capture the current src/test/runTest.ts SHA-256 as the source
   pre-run baseline.
5. Verify every compiled artifact was regenerated after:

   2026-09-02T13:46:25Z

6. Verify Code.exe version only through PowerShell FileVersionInfo.
   Do not execute Code.exe --version.

7. Read the current source and compiled runner/test and confirm:

   - exactly one reachable runTests invocation;
   - the redundant bare extensionDevelopmentPath positional is absent;
   - the top-level extensionDevelopmentPath option remains;
   - isolated execution deletes and restores ELECTRON_RUN_AS_NODE,
     VSCODE_CLI and ELECTRON_NO_ATTACH_CONSOLE through finally;
   - no retry path exists;
   - --disable-extensions is absent;
   - ETL_TEST_VSCODE_EXECUTABLE_PATH is supported;
   - isolated user-data and extensions directories are supported;
   - MOCHA_GREP and MOCHA_RESULT_FILE are honored;
   - the focused test directly inspects LanguageModelToolResult.content;
   - the test uses existing environment contracts for the QA root,
     workbook and evidence paths.

8. Verify the installed VS Code build contains the compatible built-in
   GitHub Copilot/Copilot Chat dependency. Derive this from the installed
   build without copying or installing anything.

9. Inventory the QA root by relative path, size and SHA-256.
   Require exactly 23 files and the exact workbook identity above.

10. Require these variables to be absent in the Local parent terminal:

    - ELECTRON_RUN_AS_NODE
    - VSCODE_CLI
    - ELECTRON_NO_ATTACH_CONSOLE
    - NODE_OPTIONS

Do not clear or repair them in the parent terminal.

If any gate fails, do not launch and return:

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_BLOCKED

## Step 2 — Prepare the isolated run

Create exactly one unique empty isolation/evidence directory under the
current user's Temp directory.

It must be outside:

- the repository;
- the QA root;
- any prior retained evidence directory.

Retain it after every outcome.

Using only environment-variable contracts verified in the current
runner/test:

- set ETL_TEST_VSCODE_EXECUTABLE_PATH to the installed Code.exe;
- enable the existing isolated-dependency mode;
- set the existing isolation-root contract to the unique Temp directory;
- point the focused test to the fixed QA root and workbook;
- set MOCHA_GREP to the exact focused-suite title;
- set MOCHA_RESULT_FILE inside the unique evidence directory;
- set any existing test-evidence path inside that same directory.

Do not invent an environment-variable name.

Use only process-scoped environment variables in the same Integrated
PowerShell invocation that runs the compiled runner.

Do not use the real VS Code user profile.
Do not pass --disable-extensions.
Leave the isolated external extensions directory empty and rely on the
compatible built-in Copilot dependency in the installed VS Code build.

## Step 3 — Invoke exactly once

From the repository root, directly invoke exactly once:

& 'C:\Program Files\nodejs\node.exe' '.\out\test\runTest.js'

This is:

- the only compiled-runner invocation;
- the only authorized Extension Host launch;
- the only authorized focused-test execution.

Do not use npm test, npm run test, F5, Code.exe directly, Start-Process,
another launcher, or a second invocation.

Wait for this same invocation to finish.

If the existing invocation times out, terminate only that invocation and
classify BLOCKED. Never relaunch it.

If an approval or sign-in UI prevents the tool invocation, do not bypass,
click through, or retry. Record APPROVAL_UI_BLOCKED and classify BLOCKED.

## Required direct evidence

The focused test must prove from the raw return value of exactly one:

vscode.lm.invokeTool('etl_interpret_sttm', ...)

that:

- the real Extension Host launched;
- the extension activated;
- the intended ETL tool registered;
- exactly one focused test was selected and evaluated;
- invokeTool count is exactly 1;
- parser count is exactly 1;
- no other ETL tool was invoked;
- result.content.length is exactly 2;
- part 0 is LanguageModelTextPart with nonempty complete Markdown;
- part 1 is LanguageModelDataPart;
- part 1 mimeType is exactly application/json;
- part 1 data is a nonempty Uint8Array;
- strict UTF-8 decoding succeeds;
- JSON parsing succeeds;
- structured and Markdown channels agree;
- structured evidence was observed directly and was not reconstructed
  from Markdown or Chat output.

The deterministic baseline must include:

- files discovered: 1
- files read: 1
- files blocked: 0
- active mappings: 8
- audit findings: 6
- mapping FM_F01417B0_00002 present and active
- source: customers.cust_name
- resolved source: source_db.customers.cust_name
- target: target_db.customer_name

## Classification

PASS only when:

- the real Host launches;
- the focused test reaches the structured-result boundary;
- every structured and deterministic assertion passes;
- the runner exits 0.

FAIL only when:

- the real Host and actual invokeTool boundary are proven reached; and
- an observed result violates part count, order, type, MIME, byte,
  UTF-8, JSON, parity or deterministic-baseline assertions.

BLOCKED applies to:

- preflight failure;
- Host boot or dependency failure;
- activation or registration failure;
- approval/sign-in UI;
- zero focused tests;
- timeout;
- missing evidence;
- any failure before the observable tool-result boundary.

Do not classify solely from the runner exit code.
Do not classify infrastructure or before-all failures as FAIL.

## Final integrity

After the single run:

1. Restore only process-scoped environment state.
2. Do not delete the isolation/evidence directory.
3. Recheck branch, HEAD and exact three-line Git status.
4. Recheck request.md, focused test, runTest.ts and compiled hashes.
5. Recheck the complete QA inventory and workbook hash.
6. Require zero repository and QA mutations.

Report concisely:

- runner invocation count;
- Host launches attempted and proven;
- focused tests selected and evaluated;
- activation and registration evidence;
- invokeTool and parser counts;
- result part count, order and types;
- MIME, byte length, UTF-8 and JSON result;
- deterministic baseline result;
- runner exit and Mocha result;
- retained evidence path;
- repository/build/QA integrity;
- exact PASS, FAIL or BLOCKED reason.

Do not repair, retry, clean up, or start another phase.

End with exactly one marker:

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_PASS

or

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_FAIL

or

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_BLOCKED
