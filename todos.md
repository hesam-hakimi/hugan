# Phase 1B.3G-C2 — Corrected One-Suite Real-Host Characterization

Continue in the current desktop VS Code GitHub Copilot Local normal-Agent
session and current repository folder.

The preceding Phase 1B.3G attempts stopped during read-only preflight:

- runner invocations: 0
- Extension Host launches: 0
- focused suites evaluated: 0
- invokeTool calls: 0

Therefore, the single authorized Host budget remains completely unused.

This prompt supersedes conflicting acceptance conditions from the previous
Phase 1B.3G prompts.

Do not edit or compile.
Do not use npm, F5, Cloud, ETL Orchestrator, a worktree, harness workspace,
wrapper, sidecar, Start-Process, Code.exe directly, or retry.

## Corrected authoritative semantics

The focused artifact intentionally defines:

- exactly one focused Mocha suite;
- exactly eight Mocha test cases inside that suite;
- exactly one shared vscode.lm.invokeTool('etl_interpret_sttm', ...) call
  in the suite setup/before path;
- eight tests asserting different properties of that same shared result.

Therefore:

- selecting one suite and evaluating eight tests is expected;
- eight Mocha tests do not mean eight tool invocations;
- replace every previous “exactly one focused test” requirement with
  “exactly one focused suite containing eight tests.”

The current test has no independent internal parser-call counter.

This is nonblocking for the real-host DataPart transport question. Report:

parser cardinality: NOT_INDEPENDENTLY_OBSERVABLE

Do not claim that parser count 1 was directly observed.

The current test does not independently assert or persist:

source_db.customers.cust_name

That semantic field was covered by the deterministic Phase 1A analysis and
is not required to establish whether LanguageModelDataPart survives the real
Extension Host boundary.

Report it only if directly present in retained runtime evidence; otherwise:

resolved source: NOT_OBSERVED_BY_CURRENT_TEST

Do not reconstruct it from Markdown. This status does not prevent a boundary
PASS.

## Step 1 — Minimal corrected gate

Reconfirm without editing:

1. Repository path, branch, HEAD and exact three-line Git status remain
   unchanged.
2. Protected request.md and focused-test hashes still match.
3. The current runTest.ts hash matches the immediately preceding successful
   sanitization report. Read it directly from disk; do not use OCR or introduce
   another manually transcribed expected value.
4. All five compiled artifact hashes still match the successful Phase 1B.3F
   report.

The authoritative corrected hash for:

out/test/suite/index.js

is:

D6151E50E5996F048E3E60129B10AB75205A7300988847748A75DDD3BF9222CC

5. QA inventory remains exactly 23 files and the workbook remains:

   size: 13201 bytes

   SHA-256:
   3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA

6. Confirm from the current source and compiled test:

   - MOCHA_GREP selects exactly one suite;
   - the selected suite contains exactly eight tests;
   - one shared invokeTool call supplies their raw result;
   - all tests inspect that shared result;
   - structured data comes directly from LanguageModelToolResult.content;
   - it is not reconstructed from rendered Markdown.

7. Reconfirm the compiled runner has:

   - exactly one runTests invocation;
   - no redundant positional development path;
   - scoped Electron-variable sanitation and finally restoration;
   - no retry;
   - no --disable-extensions.

8. Reconfirm these variables are absent from the parent Local terminal:

   - ELECTRON_RUN_AS_NODE
   - VSCODE_CLI
   - ELECTRON_NO_ATTACH_CONSOLE
   - NODE_OPTIONS

If any corrected gate fails, stop before launch and report BLOCKED.
Do not add another evidence requirement or modify anything.

## Step 2 — Prepare exactly one isolated run

Create exactly one unique empty isolation/evidence directory under the
current user’s Temp directory, outside the repository and QA root.

Retain it after every result.

Using only environment-variable names already implemented and verified in
the runner/test:

- select the installed VS Code 1.135.0 executable;
- enable isolated-dependency mode;
- point the isolation and evidence paths to the unique Temp directory;
- point the focused test to the fixed QA root and workbook;
- set MOCHA_GREP to the exact focused-suite title;
- set MOCHA_RESULT_FILE inside the evidence directory.

Set the variables only for the same Integrated PowerShell process that will
invoke the runner.

Do not invent an environment-variable name.
Do not use the real VS Code profile.
Do not install, copy, update or download extensions.
Do not pass --disable-extensions.

## Step 3 — Invoke exactly once

From the repository root invoke exactly once:

& 'C:\Program Files\nodejs\node.exe' '.\out\test\runTest.js'

This is the only authorized runner invocation and Extension Host launch.

Wait for this same invocation to finish.
Do not retry.

If it times out, terminate only that invocation and classify BLOCKED.

If approval or sign-in UI prevents invocation, do not bypass it or relaunch.
Classify BLOCKED.

## Boundary PASS requirements

PASS requires:

- the real Extension Host launches;
- the extension activates and registers etl_interpret_sttm;
- exactly one focused suite is selected;
- exactly eight tests are evaluated;
- all eight pass with none skipped;
- one shared invokeTool call is executed;
- direct raw result evidence confirms content.length === 2;
- part 0 is a nonempty LanguageModelTextPart;
- part 1 is LanguageModelDataPart;
- MIME is exactly application/json;
- data is a nonempty Uint8Array;
- strict UTF-8 decoding succeeds;
- JSON parsing succeeds;
- the existing authored cross-channel and deterministic assertions pass;
- runner exit code is 0.

Report parser cardinality as:

NOT_INDEPENDENTLY_OBSERVABLE

Report resolved source as its directly observed value or:

NOT_OBSERVED_BY_CURRENT_TEST

Neither non-observable item prevents a real-host DataPart boundary PASS.

## Classification

FAIL only if invokeTool reaches the real raw result boundary and an existing
structured-result assertion fails.

BLOCKED applies to Host boot, dependency, activation, registration,
approval/sign-in, timeout, zero selected suite, missing raw-result evidence,
or another failure before the boundary.

Do not classify only from process exit code.

## Final integrity

After the single invocation:

- restore only process-scoped environment state;
- retain the isolation/evidence directory;
- verify repository, compiled artifacts, protected file and QA workspace
  remain unchanged;
- report runner, Host, suite, test and invokeTool counts;
- report raw part types/order, MIME, byte length, UTF-8 and JSON results;
- report 8/8 Mocha result and runner exit;
- report the non-observable fields honestly;
- report retained evidence path and integrity result.

Do not edit, compile, repair, retry, clean up or begin another phase.

End with exactly one marker:

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_PASS

or

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_FAIL

or

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_BLOCKED
