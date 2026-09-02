# Phase 1B.3 — Sanitized Installed-Code Real-Host Structured-Result Characterization (One Shot)

Continue from the current uncommitted Phase 1B state. Do not restart, revert, clean, stash, or broaden the task.

Run this task as a normal coding Agent in the SOURCE repository. Do not use the ETL Orchestrator Chat participant for this harness repair.

## 1. Objective

Perform exactly one additional real Extension Host characterization run after eliminating inherited Electron Node-mode contamination.

Phase 1B.2 never reached:

- VS Code main-process startup,
- Extension Host activation,
- ETL tool registration,
- `vscode.lm.invokeTool`,
- or `etl_interpret_sttm`.

Therefore this prompt authorizes:

- exactly ONE additional Extension Host launch;
- exactly ONE `vscode.lm.invokeTool` call, only if activation succeeds;
- exactly ONE parser invocation, only through that tool call;
- zero retries or reruns under every outcome.

The purpose is characterization only. Do not repair product behavior.

## 2. Authoritative identity

Source repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Branch:

fix/workspace-write-completion-0.3.148

HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Installed GUI VS Code executable:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe

Expected VS Code version:

1.135.0

QA workspace:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

Workbook:

sttm\synthetic_workbook.xlsx

Protected pre-existing modification:

.github/templates/request.md

Expected protected-file SHA-256:

2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84

## 3. Required initial Git state

Before editing, run read-only identity checks.

The exact expected status is:

 M .github/templates/request.md
 M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Requirements:

- `src/test/testPatterns.ts` must be clean.
- No other tracked or untracked path may exist.
- Verify the protected request.md SHA-256.
- Record SHA-256 hashes of the current `src/test/runTest.ts` and characterization test.
- Record a path/size/SHA-256 inventory of the 23 QA-workspace files.
- Stop BLOCKED before editing if any identity differs.

Never modify, format, stage, restore, stash, reset, clean, or commit `.github/templates/request.md`.

## 4. Evidence-correct diagnosis

Treat the Phase 1B.2 stack:

electron/js2c/node_init
→ out/extension.js
→ require("vscode")
→ Cannot find module "vscode"

as evidence that `Code.exe` ran in Electron Node mode instead of becoming the VS Code Extension Host.

The primary hypothesis is inherited `ELECTRON_RUN_AS_NODE`.

Do not claim that omitting `--disable-extensions` caused Node mode.

Do not treat the existing first positional path as the established root cause:

- `@vscode/test-electron` officially permits a file/folder/workspace as the first launch argument;
- it separately appends `--extensionDevelopmentPath`;
- Phase 1B.1 previously booted with the same positional path.

For this run, keep the current positional-path behavior unchanged so environment sanitation is the only causal launch change. Do not remove or replace it merely because the Phase 1B.2 report suggested doing so.

## 5. Edit allowlist

The only file authorized for further editing is:

src/test/runTest.ts

Do not edit:

- `src/test/suite/sttmRealHostStructuredResult.test.ts`;
- `src/test/testPatterns.ts`;
- production TypeScript;
- package.json or lockfiles;
- contracts, fixtures, workbook, QA assets;
- generated reports;
- node_modules;
- any protected file.

If the existing characterization test itself fails to compile, stop and report BLOCKED. Do not improvise a test change.

## 6. Required runner sanitation

Limit the new behavior strictly to the existing installed-executable / isolated-dependency opt-in path. Default runner behavior must remain byte-for-byte semantically unchanged when that opt-in is absent.

Immediately around the awaited `runTests(...)` call:

1. Enumerate environment keys case-insensitively.
2. Record presence only—not values—for:

   - `ELECTRON_RUN_AS_NODE`
   - `VSCODE_CLI`
   - `ELECTRON_NO_ATTACH_CONSOLE`
   - `NODE_OPTIONS`
   - `ComSpec`

3. Snapshot all actual case variants of:

   - `ELECTRON_RUN_AS_NODE`
   - `VSCODE_CLI`
   - `ELECTRON_NO_ATTACH_CONSOLE`

4. Delete every case-insensitive occurrence of those three keys from `process.env`.

5. Assert immediately before `runTests(...)` that no case-insensitive `ELECTRON_RUN_AS_NODE` key remains.

6. Await `runTests(...)`.

7. Restore the exact original keys and values in a `finally` block.

Important:

- Delete `ELECTRON_RUN_AS_NODE`; do not set it to `"0"`, `""`, `"false"`, or `"undefined"`.
- Do not log the complete environment.
- Do not place secrets or environment values in output.
- Do not modify `node_modules/@vscode/test-electron`.

Log these safe diagnostics:

- `process.execPath`;
- installed VS Code executable path;
- owned `launchArgs` in exact order;
- extension development path;
- extension tests path;
- isolated user-data path;
- isolated extensions path;
- presence/absence results for the listed environment names.

Assert that the arguments contain neither:

- `--ms-enable-electron-run-as-node`;
- nor a `resources/app/out/cli.js` path.

## 7. Dependency and isolation requirements

Continue using the exact GUI executable:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe

Never use:

- `code.cmd`;
- a downloaded test build;
- a sibling repository’s `.vscode-test`;
- Marketplace access;
- copied extensions;
- a replacement launcher.

Keep `--disable-extensions` OMITTED only under the existing isolated-dependency opt-in so the compatible built-in `github.copilot-chat` dependency can load.

Keep the isolated extensions directory empty.

Use fresh unique temporary directories outside both the source repository and QA workspace for:

- user data;
- extensions;
- result/evidence files;
- the temporary batch wrapper.

Do not open or reuse the normal VS Code profile.

## 8. Windows wrapper

Create one temporary `.cmd` wrapper outside the repository and QA workspace.

It must use `setlocal`, report whether the contaminated variables were inherited, and then remove them before starting Node/npm:

@echo off
setlocal
if defined ELECTRON_RUN_AS_NODE (
  echo [etl-preflight] inherited ELECTRON_RUN_AS_NODE: present
) else (
  echo [etl-preflight] inherited ELECTRON_RUN_AS_NODE: absent
)
set "ELECTRON_RUN_AS_NODE="
set "VSCODE_CLI="
set "ELECTRON_NO_ATTACH_CONSOLE="

Then set only the existing Phase 1B process-scoped variables, including:

- installed Code.exe override;
- isolated-dependency opt-in;
- QA workspace root;
- unique isolation root;
- unique result file;
- the exact existing Mocha grep/title.

Do not invent a new test title. Read it from the existing characterization test.

Launch the wrapper through:

C:\Windows\System32\cmd.exe

Do not use:

- `Start-Process`;
- `$env:ComSpec`;
- `code.cmd`;
- a second PowerShell process that relies on inherited `$env:` mutations.

The wrapper must call the existing focused Phase 1B test command directly and return its exit code.

## 9. Static gate before the one launch

Before consuming the launch budget:

- inspect the final `runTest.ts` diff;
- verify only the opt-in path changed;
- verify environment restoration is in `finally`;
- verify the protected file hash remains exact;
- verify the characterization test hash is unchanged;
- verify the QA inventory is unchanged;
- run `Code.exe --version` only after the wrapper environment is sanitized;
- run the existing narrow compile command exactly once;
- verify the compiled runner contains the sanitation;
- verify no host process was started during these checks.

If any static check fails, report BLOCKED and do not launch.

## 10. The single authorized run

After every gate passes, perform exactly one focused real-host run.

The existing characterization test remains authoritative and must not be weakened.

If the Extension Host starts:

- verify activation;
- verify the intended ETL extension identity;
- verify `etl_interpret_sttm` registration;
- call `vscode.lm.invokeTool` exactly once;
- accept whatever PASS/FAIL evidence the existing assertions produce;
- never retry after the invocation.

No Chat/Orchestrator invocation is allowed in this phase.

Do not run:

- F5 manually;
- a second host window;
- a full test suite;
- Eval Golden;
- package or install;
- VSIX;
- Databricks, Jira, Confluence, publish, pipeline, approval, or write tools.

## 11. Classification

PASS:

- the real Extension Host boots;
- the intended extension activates;
- the focused test invokes the tool exactly once;
- all existing structured-result assertions pass.

FAIL:

- activation and tool invocation occur;
- the test receives a real result;
- a product-facing structured-result assertion fails.

BLOCKED:

- infrastructure fails before tool invocation;
- the intended extension cannot activate/register;
- environment contamination remains;
- any preflight identity or protection check fails.

If BLOCKED before invocation, explicitly state that the parser budget remains unused.

Never convert infrastructure BLOCKED into product FAIL.

## 12. Root-cause wording

If the wrapper observes inherited `ELECTRON_RUN_AS_NODE` and the sanitized launch boots normally, report Electron Node-mode contamination as confirmed causal evidence.

If the variable was not observed but sanitation results in a successful boot, report that the sanitized launch succeeded but do not overclaim which inherited variable was causal.

If the run is still blocked, do not speculate and do not attempt the positional-path change in the same phase.

## 13. Final integrity report

Report:

- pre/post request.md SHA-256;
- pre/post characterization-test SHA-256;
- pre/post QA inventory comparison;
- executable and VS Code version;
- environment-key presence before and after sanitation;
- exact owned launch arguments;
- launch count;
- invocation count;
- activation/registration evidence;
- result classification;
- final `git status --porcelain=v1 --untracked-files=all`;
- confirmation that nothing was staged or committed.

End with exactly one marker:

F5_REAL_HOST_STRUCTURED_RESULT_PASS

or

F5_REAL_HOST_STRUCTURED_RESULT_FAIL

or

F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED
