# Phase 1B.1 — Unblock and Run the Real Extension-Host Structured-Result Characterization

## Authorization

This prompt supersedes the previous Phase 1B edit allowlist.

Explicitly authorize one minimal test-runner enhancement that allows the existing
real-host runner to use the already installed VS Code executable instead of
downloading another VS Code build.

Then create and run exactly one focused real Extension Development Host
characterization test.

This remains a test-infrastructure and characterization task:

- no production-code change;
- no product repair;
- no commit or staging;
- no cache copying;
- no VS Code download or installation;
- no Chat/Orchestrator invocation;
- no external service call.

## Authoritative environment

Repository root:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required branch:

fix/workspace-write-completion-0.3.148

Required HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

QA workspace:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

Workbook:

sttm/synthetic_workbook.xlsx

Installed VS Code executable:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe

Required runtime version:

1.135.0

Extension ID:

td-etl.databricks-etl-copilot

Tool:

etl_interpret_sttm

Known pre-existing worktree modification:

.github/templates/request.md

## 1. Mandatory preflight

Before editing:

1. Verify exact repository root, branch, and HEAD.
2. Run and record:

   git status --short --untracked-files=all

3. The only pre-existing changed path must be:

   .github/templates/request.md

4. Record its:
   - SHA-256;
   - exact Git diff;
   - size;
   - UTC mtime.

5. Never edit, format, stage, restore, stash, reset, clean, or commit it.
6. Confirm these intended paths are initially clean or absent as appropriate:
   - `src/test/runTest.ts`
   - `src/test/testPatterns.ts`
   - `src/test/suite/sttmRealHostStructuredResult.test.ts`
7. Confirm all production files on the `etl_interpret_sttm` path are byte-identical to HEAD.
8. Verify the configured `Code.exe` path:
   - is absolute;
   - exists;
   - is a regular file;
   - is `Code.exe`, not `code.cmd` or a directory.
9. Run that exact executable with `--version`.
10. Require and record:
    - version `1.135.0`;
    - commit identifier;
    - architecture;
    - executable SHA-256.

Do not embed quote characters inside the environment-variable path value.

If repository identity, initial status, protected-file identity, intended-path
cleanliness, executable identity, or VS Code version differs, make no edits and end:

F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED

## 2. Exact edit allowlist

Authorize changes only to:

1. `src/test/runTest.ts`
2. one new file:
   `src/test/suite/sttmRealHostStructuredResult.test.ts`
3. `src/test/testPatterns.ts` only if strictly required to classify the new test under `INTEGRATION_TEST_PATTERNS`

No other tracked or untracked repository path may be created or modified.

Generated compiler output may be regenerated only by the existing sanctioned compiler.
Never edit `out/**` manually.

Do not modify:

- production TypeScript;
- `package.json` or lockfiles;
- version fields;
- launch configurations;
- contracts;
- fixtures or the XLSX;
- documentation or Eval reports;
- existing tests;
- the existing stub-based result-envelope suite;
- `.github/templates/request.md`.

Do not weaken, rename, remove, skip, or reclassify any existing test.

## 3. Minimal supported runner enhancement

Modify `src/test/runTest.ts` only enough to support this process-scoped variable:

ETL_TEST_VSCODE_EXECUTABLE_PATH

Required behavior:

1. If the variable is absent, preserve the existing
   `downloadAndUnzipVSCode()` behavior exactly.
2. If the variable is present:
   - trim it;
   - reject an empty value;
   - require an absolute path;
   - require an existing regular file;
   - use it directly as `vscodeExecutablePath` in `runTests(...)`;
   - do not call `downloadAndUnzipVSCode()`;
   - do not fall back to downloading if validation fails.
3. Emit a concise diagnostic:
   - executable source: environment override;
   - resolved executable path.
4. Do not add automatic executable discovery, cache copying, downloads, persisted configuration, or global state.
5. Keep `reuseMachineInstall` false or omitted.
6. Preserve the normal no-variable behavior for existing callers.

This runner change is explicitly authorized even though it was excluded by the
previous Phase 1B prompt.

## 4. Isolated test-host directories

The installed VS Code executable must not use the user’s normal VS Code profile and
must not create `.vscode-test` inside the repository.

Support this additional process-scoped variable:

ETL_TEST_VSCODE_ISOLATION_ROOT

When the executable override is active:

1. Require this variable to contain an absolute directory under `$env:TEMP`.
2. Require it to be outside:
   - the source repository;
   - the QA workspace.
3. Preserve all existing launch arguments.
4. Add:

   --user-data-dir=<isolation-root>\user-data
   --extensions-dir=<isolation-root>\extensions
   --disable-extensions

5. The extension under test must still load through `extensionDevelopmentPath`.
6. Do not use or copy any sibling repository’s `.vscode-test`.
7. Verify no `.vscode-test` directory appears in the current repository.

Use `extensionTestsEnv` or the runner’s established equivalent to pass these
process-scoped values to the real-host test:

- `ETL_F5_QA_WORKSPACE_ROOT`
- `MOCHA_GREP`
- `MOCHA_RESULT_FILE`

Do not persist any environment variable.

## 5. Characterization test

Create exactly:

src/test/suite/sttmRealHostStructuredResult.test.ts

Use this unique grep-safe test title:

Phase 1B real host structured result characterization

Classify it as a real-host integration test, never as a pure unit test.

The test must use the real:

require('vscode')

It must not use:

- `registerVscodeStub`;
- any VS Code stub;
- `Module._load` interception;
- `EtlReadOnlyToolService.interpretSttm` directly;
- the parser implementation directly;
- a private registration object;
- the Chat or Orchestrator transcript.

Read the QA root only from:

ETL_F5_QA_WORKSPACE_ROOT

Fail if it is absent, empty, nonexistent, or not absolute.
Do not hardcode the absolute QA path in tracked test source.

### Real-host identity

Inside the test:

1. Record `vscode.version` and require exactly `1.135.0`.
2. Record process PID.
3. Record approximate process-start UTC using:

   Date.now() - process.uptime() * 1000

4. Resolve:

   vscode.extensions.getExtension(
     'td-etl.databricks-etl-copilot'
   )

5. Require the extension to exist.
6. Record its resolved extension path and package version.
7. Require its canonical resolved path to equal the authoritative repository.
8. Activate it.
9. Require `extension.isActive === true`.
10. Require `etl_interpret_sttm` to appear in the real `vscode.lm.tools`.

### QA mutation guard

Before invoking the tool, inventory every QA-workspace file using:

- workspace-relative POSIX-normalized path;
- size;
- SHA-256.

Hashing the XLSX for mutation detection is allowed.
Do not manually parse, convert, copy, or modify it.

Repeat the identical inventory after invocation and require an exact match.

Do not write logs, snapshots, results, or temporary files into the QA workspace.

### Exactly one public invocation

Create one `vscode.CancellationTokenSource`.

Invoke exactly once:

await vscode.lm.invokeTool(
  'etl_interpret_sttm',
  {
    input: {
      workspaceRoot: qaWorkspaceRoot,
      sttmPath: 'sttm/synthetic_workbook.xlsx',
      includeAudit: true
    },
    toolInvocationToken: undefined
  },
  cancellationTokenSource.token
);

Dispose the token source afterward.

Do not invoke `etl_capabilities` or any other ETL tool.
Do not invoke `etl_interpret_sttm` a second time.

Capture the raw returned `LanguageModelToolResult` before passing it to any repository extractor.

### Raw result assertions

Record:

1. `result.content.length`;
2. ordered constructor name of every part;
3. stable API classification using the real VS Code classes;
4. TextPart value length;
5. DataPart MIME type;
6. whether DataPart data is a `Uint8Array`;
7. DataPart byte length;
8. strict UTF-8 decoding result;
9. JSON parsing result;
10. parsed top-level keys.

Require exactly two ordered parts:

1. index 0: `vscode.LanguageModelTextPart`
2. index 1: `vscode.LanguageModelDataPart`

Require:

- exact MIME `application/json`;
- non-empty `Uint8Array`;
- strict UTF-8 decoding using `TextDecoder` with fatal error handling;
- valid JSON.

Do not rely only on `constructor.name`.
Use real API `instanceof` assertions and record constructor names only as supporting evidence.

Reuse the exact payload field paths and deterministic assertions from:

src/test/suite/sttmPublicToolResultEnvelope.test.ts

Do not invent alternative payload interpretations.

Require:

- files discovered/read/blocked = 1/1/0;
- active mappings = 8;
- audit findings = 6;
- `FM_F01417B0_00002` is present, active, and first;
- source `customers.cust_name`;
- target `target_db.customer_name`;
- rendered Markdown contains the same mapping evidence.

## 6. Fresh build and focused execution

Use only the repository’s existing narrow TypeScript test-compilation command and
existing `src/test/runTest.ts` runner.

Do not create a replacement launcher.

Before compilation, record:

- SHA-256 and UTC mtime of `out/tools/index.js`;
- package version;
- `package.json.main`.

After compilation, record:

- exact compile command;
- compile completion UTC;
- SHA-256 and UTC mtime of `out/tools/index.js`;
- confirmation that compiled production output constructs the explicit
  `application/json` DataPart.

If an unexplained production-output difference appears, do not launch the host.
Report BLOCKED.

For the single focused runner process, set:

ETL_TEST_VSCODE_EXECUTABLE_PATH=
C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe

ETL_F5_QA_WORKSPACE_ROOT=
C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

ETL_TEST_VSCODE_ISOLATION_ROOT=
<one unique directory created under $env:TEMP for this run>

MOCHA_GREP=
Phase 1B real host structured result characterization

MOCHA_RESULT_FILE=
<one unique JSON result path under $env:TEMP>

The two `<...>` values must be generated dynamically under `$env:TEMP`; never
hardcode them in tracked source.

Before host launch, require the runner diagnostic to confirm the executable override.

If any VS Code download begins, stop immediately and classify BLOCKED.

All variables must remain process-scoped and be restored or removed after the run,
including on failure.

If the known Windows command-resolution issue affects bare `git`, `node`, or `npm`,
set:

$env:PATHEXT = '.COM;.EXE;.BAT;.CMD'

only inside the affected process and restore the prior value afterward.

## 7. Execution limits

The Extension Development Host may launch exactly once.

`etl_interpret_sttm` may be invoked exactly once.

Do not rerun after the real-host launch, regardless of PASS, FAIL, or error.

If compilation fails before host launch, correct only an error within the authorized
test-runner/test files. If another path is required, stop.

If host launch fails before tool invocation, report BLOCKED.
Do not improvise a direct service call or second launcher.

If approval UI blocks invocation, do not bypass it with private APIs.
Report `APPROVAL_UI_BLOCKED` and classify BLOCKED.

Do not run:

- the full unit suite;
- Eval Golden;
- packaging or VSIX operations;
- install or download commands;
- the stub-only result-envelope test;
- render, validation, preview, approval, write, publish, or pipeline flows;
- Databricks, Jira, or Confluence calls;
- another Orchestrator interaction.

The five pending tests and these three known unrelated failures remain out of scope:

1. missing `.github/prompts/deploy-v3-agent-tool-context-gap.prompt.md`;
2. missing `name` in `.github/instructions/business-context.instructions.md`;
3. eleven tracked `src/**/AGENT.md` files versus an expected empty inventory.

Do not investigate them.

## 8. Incremental-cache handling

If compilation changes a tracked incremental cache that was clean at preflight:

1. prove compilation alone caused it;
2. restore only that cache byte-for-byte from its committed HEAD blob;
3. verify its final SHA-256 equals its preflight/HEAD hash.

Do not use `git checkout`, `git restore`, reset, clean, or stash.

## 9. Classification

Use exactly one classification.

### F5_REAL_HOST_STRUCTURED_RESULT_PASS

Use only if:

- the installed `Code.exe` override was used;
- the fresh host reports VS Code `1.135.0`;
- extension path and build identity are proven;
- exactly one public invocation occurred;
- the raw result contains the expected ordered TextPart and
  `application/json` DataPart;
- JSON and deterministic fixture evidence pass;
- QA inventory is byte-identical before and after.

Supported conclusion:

The structured part survives the real `vscode.lm.invokeTool` programmatic boundary.
The earlier Orchestrator result was an evidence-observability failure, not evidence
of a parser or current result-construction defect.

Do not claim this proves or disproves what the model-facing Chat offload layer receives.

### F5_REAL_HOST_STRUCTURED_RESULT_FAIL

Use only if executable, fresh host, extension path, and build identity are proven,
but the raw public result has a missing, malformed, reordered, invalid, or wrong-MIME
DataPart.

Capture all raw content-part metadata and stop.
Do not repair production code.

### F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED

Use if identity, runner override, build, host launch, registration, approval, fixture
access, invocation count, or mutation safety cannot be proven.

Report the exact blocker and stop without fallback.

## 10. Final report and integrity

Report:

1. repository root, branch, HEAD, and initial status;
2. protected `request.md` hash/diff before and after;
3. exact authorized changed paths;
4. runner override diff and fallback-preservation evidence;
5. executable path, SHA-256, version, commit, and architecture;
6. temporary isolation paths;
7. compile command and compiled build identity;
8. host PID/start time, `vscode.version`, extension path/version/activity;
9. real-tool registration evidence;
10. exact invocation count;
11. raw ordered part metadata;
12. decoded JSON and Markdown parity;
13. QA inventory comparison;
14. selected classification;
15. final:

   git status --short --untracked-files=all

The only permissible final repository changes are:

- pre-existing `.github/templates/request.md`;
- `src/test/runTest.ts`;
- new `src/test/suite/sttmRealHostStructuredResult.test.ts`;
- optionally `src/test/testPatterns.ts`.

Confirm explicitly:

- `.github/templates/request.md` is byte-for-byte unchanged;
- no product code or fixture changed;
- package version and lockfiles are unchanged;
- no existing test was altered or weakened;
- no `.vscode-test` cache was copied or created in the repository;
- no download or installation occurred;
- no full suite or Eval Golden ran;
- no external service or write flow ran;
- nothing was staged or committed;
- only one real-host launch and one `etl_interpret_sttm` invocation occurred.

End with exactly one marker:

F5_REAL_HOST_STRUCTURED_RESULT_PASS

or

F5_REAL_HOST_STRUCTURED_RESULT_FAIL

or

F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED
