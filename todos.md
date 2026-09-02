Phase 1B.3L — One-Shot Multi-Development-Path Real-Host Structured-Result Run

Work locally in the currently open desktop VS Code repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

This is an operational-only, one-shot real Extension Host characterization.

Do not request another implementation confirmation. Normal platform permission prompts may still be shown.

Mandatory precondition

The Phase 1B.3K changes must already have been accepted with Keep.

Phase 1B.3K completed with:

F5_LOCAL_MULTI_DEVELOPMENT_PATH_HARNESS_PASS

Established state:

* Authored changes are confined to:
    * src/test/runTest.ts
    * src/extension.ts
* npm run compile ran exactly once and exited 0.
* Generated changes were confined to out/**.
* No test, compiled runner, Extension Host, or invokeTool call ran.
* package.json and extensionDependencies remained unchanged.
* Production and Development activation behavior remained unchanged.
* Ordinary Test mode retained its previous early return.
* Opted-in Test mode can perform production Copilot readiness, register only etl_interpret_sttm, and return before participant/sidebar/action/UI behavior.
* The runner now supports an ordered two-development-path launch.

New contracts:

* ETL_TEST_COPILOT_EXTENSION_PATH
* ETL_TEST_READ_ONLY_TOOL_ONLY=1

Existing isolated-run contract:

* ETL_TEST_ENABLE_ISOLATED_DEPENDENCIES=1

Fixed repository identity

Expected branch:

fix/workspace-write-completion-0.3.148

Expected HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected Git status, exactly:

M .github/templates/request.md
M src/extension.ts
M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Protected request SHA-256:

2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84

Focused-test SHA-256:

8713EC3B3F2F75B06541F9B68AC4D9026CA0A17D052E07898EA12C5E12FAABCE

The post-Phase-1B.3K source and compiled hashes shown in the prior UI were abbreviated. Do not transcribe or compare abbreviated hashes. Read complete hashes directly from disk, establish a fresh pre-run baseline, and compare that same baseline after the run.

Fixed product and QA identity

Installed VS Code executable:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe

Required VS Code version:

1.135.0

Audited bundled Copilot development-extension path:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot

Required Copilot identity:

* Canonical extension ID: github.copilot-chat
* Version: 0.63.0
* engines.vscode: ^1.135.0
* extensionDependencies: absent or empty
* File inventory: 98 files
* Reparse points: 0

QA root:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

Workbook:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982\sttm\synthetic_workbook.xlsx

Expected QA inventory:

23 files

Expected workbook size:

13201 bytes

Expected workbook SHA-256:

3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA

Focused suite title:

Phase 1B real host structured result characterization

Absolute prohibitions

Do not edit any repository, source, compiled, installed-product, bundled-Copilot, QA, or prior-evidence file.

Do not:

* Compile.
* Invoke npm, npx, tsc, or esbuild.
* Run any test command other than the single authorized compiled runner.
* Copy, seed, or install any extension.
* Use Marketplace, VSIX, or –install-extension.
* Deliberately initiate a download.
* Change package.json or extensionDependencies.
* Use the real VS Code user profile.
* Use F5, Cloud, ETL Orchestrator, or another worktree.
* Invoke Code.exe manually or outside the compiled runner.
* Use Start-Process or create an additional launch wrapper/bridge.
* Stage, commit, stash, restore, reset, or clean.
* Inspect credentials, tokens, authentication state, or account contents.
* Retry, relaunch, repair, or perform a diagnostic Host run.

Existing Mocha-result and focused-test evidence sidecar files are allowed, but they must be written only beneath the new isolation/evidence root.

The only permitted writes are normal runtime and evidence files underneath exactly one new unique Temp isolation root.

Launch budget

If every preflight gate passes, this phase authorizes exactly:

* Compiled-runner invocations: 1
* Extension Host launches: 1
* Focused suites: 1
* Shared vscode.lm.invokeTool calls: at most 1
* Retries/relaunches: 0

A preflight BLOCKED result consumes none of this budget.

Step 1 — Read-only preflight

Before creating the new isolation root, verify:

1. Repository path, branch, HEAD, and exact four-line Git status.
2. The protected request and focused-test hashes above.
3. package.json is unchanged and still declares exactly:
    extensionDependencies: [“github.copilot-chat”]
4. Git diff is confined to the expected existing authored files and git diff –check passes.
5. Capture complete pre-run SHA-256 values for:
    * src/extension.ts
    * src/test/runTest.ts
    * package.json
    * tsconfig.json
    * out/extension.js
    * out/test/runTest.js
    * out/test/suite/sttmRealHostStructuredResult.test.js
    * both relevant compiled index.js files
6. All five pinned compiled artifacts exist and still correspond to the successful Phase 1B.3K compile.
7. src/test/runTest.ts and out/test/runTest.js prove:
    * Exactly one runTests(…) invocation exists.
    * Normal mode uses one ETL development path.
    * Isolated-dependency mode uses exactly two ordered paths:
        [etlRepositoryPath, bundledCopilotExtensionPath]
    * The paths are passed only through the top-level extensionDevelopmentPath option.
    * ETL_TEST_COPILOT_EXTENSION_PATH is consulted only in isolated mode.
    * The Copilot directory and manifest are validated before runTests.
    * No machine-specific Copilot path is hard-coded in source.
    * No positional or manually constructed –extensionDevelopmentPath exists.
    * No retry exists.
    * Scoped environment sanitation/restoration remains inside finally.
    * –disable-extensions is absent in isolated-dependency mode.
8. src/extension.ts and out/extension.js prove:
    * Production behavior is unchanged.
    * Development behavior is unchanged.
    * Ordinary Test mode still returns early.
    * Test mode with ETL_TEST_READ_ONLY_TOOL_ONLY=1 executes the existing Copilot-readiness path, registers exactly one etl_interpret_sttm using its production implementation, and returns before participant/sidebar/action/command/UI, model-selection, model-request, and authentication behavior.
    * Failed Copilot activation registers no ETL tool.
9. The focused source and compiled suite prove:
    * Exactly one suite has the fixed title.
    * Exactly eight Mocha test cases exist.
    * Exactly one shared vscode.lm.invokeTool call exists.
    * The tool ID is etl_interpret_sttm.
    * There is no selectChatModels call.
    * There is no language-model sendRequest call.
    * There is no authentication call.
10. Code.exe exists and FileVersionInfo reports 1.135.0. Do not invoke Code.exe –version.
11. The bundled Copilot path:

* Exists under the selected VS Code installation.
* Resolves to a canonical path inside that installation.
* Has the fixed package identity above.
* Contains exactly 98 files.
* Contains no reparse points.
* Is unchanged from the preceding audit fingerprint.

12. QA contains exactly 23 files and the workbook matches the fixed size and SHA-256.
13. No matching prior isolated Extension Host process remains.
14. Previous evidence roots remain unchanged.
15. Read the current runner and focused test to identify all existing environment contracts required for:

* VS Code executable
* Isolation root
* QA root and workbook
* Mocha result
* Structured-result evidence files

Do not invent or rename environment contracts.

Record only presence or absence—not values—of:

* ELECTRON_RUN_AS_NODE
* VSCODE_CLI
* ELECTRON_NO_ATTACH_CONSOLE
* NODE_OPTIONS
* ComSpec

Their parent-process presence is not itself a failure because the runner has scoped sanitation and restoration.

If any substantive identity, integrity, or launch-shape gate fails:

* Do not create an isolation root.
* Do not invoke the runner.
* Classify BLOCKED.

Step 2 — Create exactly one isolation/evidence root

Create exactly one unique directory beneath the current user’s Temp directory, named with the prefix:

etl-phase-1b3l-multipath-

It must be outside:

* The repository
* The QA root
* The bundled Copilot directory
* Every prior evidence directory

The root must begin empty and may contain only files and directories created by this single runtime run.

Create fresh isolated user-data and extensions directories underneath it.

Before launch, the isolated extensions directory must be empty and contain no copied, seeded, or installed extension package.

Do not place github.copilot-chat in the isolated extensions directory. It must be loaded directly from the audited bundled path as the second explicit development extension.

Place the Mocha result and all existing focused-test evidence outputs underneath this new root.

Retain the root for PASS, FAIL, or BLOCKED after its creation.

Step 3 — Configure the same PowerShell process

In the same local PowerShell process that will invoke the runner:

1. Save the prior process-local presence and value of every environment variable that will be changed, without logging any existing value.
2. Use only environment contracts already present in the current runner or focused test.
3. Set:
    ETL_TEST_ENABLE_ISOLATED_DEPENDENCIES=1
    ETL_TEST_COPILOT_EXTENSION_PATH=C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot
    ETL_TEST_READ_ONLY_TOOL_ONLY=1
4. Set the existing executable-path contract to:
    C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe
5. Set the existing isolation-root contract to the new Temp root.
6. Set the existing QA/workbook contracts to the fixed QA artifacts above.
7. Set MOCHA_GREP exactly to:
    Phase 1B real host structured result characterization
8. Set MOCHA_RESULT_FILE and every existing evidence-output contract to unique paths underneath the new isolation root.
9. Do not create a new environment contract.
10. Do not dump the environment or log pre-existing environment-variable values.

Immediately before invocation, verify:

* The effective top-level extensionDevelopmentPath array will contain exactly, in order:
    1. C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
    2. C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot
* Both paths exist and have the validated identities.
* Copilot will be supplied as a development extension, not as a seed.
* The isolated user-data and extensions directories are fresh.
* The isolated extensions directory is empty.
* –disable-extensions is absent.
* Both isolated-dependency opt-ins equal 1.
* Exactly one runner invocation remains available.
* No matching Host process is running.

If this gate fails, retain the new root, restore process state, and classify BLOCKED without launch.

Step 4 — Invoke the compiled runner exactly once

From the repository root, in that same PowerShell process, invoke exactly once:

& ‘C:\Program Files\nodejs\node.exe’ ‘.\out\test\runTest.js’

This is the only authorized runner/test invocation and must cause at most one Extension Host launch.

Wait for this same invocation to complete. Do not retry, relaunch, repair, or invoke a diagnostic runner.

If it does not complete within the existing bounded deadline, terminate only the matching isolated child process, retain all evidence, and classify BLOCKED.

If the terminal displays ambiguous rendering or an interruption such as ^C but result/evidence files exist, do not rerun. Determine the outcome from the authoritative Mocha result, structured evidence, and isolated Host logs.

If approval, trust, sign-in, or other UI prevents reaching the raw tool-result boundary, do not bypass it. Classify BLOCKED.

Step 5 — Required runtime observations

Report:

* Runner invocation count
* Extension Host launches attempted and proven
* Host VS Code version and PID
* Exact development-extension paths received by VS Code and their order
* Effective ETL extension identity, path, and version
* Effective github.copilot-chat identity, path, and version
* Whether Copilot was treated as an explicit development extension
* Whether built-in shadowing occurred
* Copilot activation outcome
* ETL extension activation outcome
* etl_interpret_sttm registration outcome
* Focused suites selected
* Test bodies evaluated
* Mocha pass/fail/pending counts
* vscode.lm.invokeTool call count
* Whether invokeTool returned a real LanguageModelToolResult
* Runner exit code
* Result/evidence file paths
* Retained isolation/evidence root

Do not claim that development-path precedence worked solely because the Host launched. Require direct registry/log evidence or successful dependency activation followed by tool registration/invocation.

Raw-result boundary

The structured-result boundary is reached only when the single real:

vscode.lm.invokeTool(‘etl_interpret_sttm’, …)

call returns its LanguageModelToolResult to the focused suite.

A missing tool, rejected invocation, activation exception, registration failure, or before-all failure before a returned LanguageModelToolResult has not reached this boundary.

Classification

PASS

PASS requires direct retained evidence that:

* Runner invocations: 1
* Host launches attempted/proven: 1/1
* github.copilot-chat resolves from the explicit bundled development path
* Copilot activation succeeds
* Databricks ETL Copilot activation succeeds
* etl_interpret_sttm registers exactly once
* Focused suites selected: 1
* Test bodies evaluated: 8 of 8
* vscode.lm.invokeTool calls: exactly 1
* The real invokeTool call returns a LanguageModelToolResult
* All 8 tests pass
* Failures: 0
* Pending/skipped: 0
* result.content.length is exactly 2
* result.content[0] is a nonempty LanguageModelTextPart
* result.content[1] is a LanguageModelDataPart
* result.content[1].mimeType is exactly application/json
* result.content[1].data is a nonempty Uint8Array
* Strict UTF-8 decoding succeeds
* JSON parsing succeeds
* All existing cross-channel parity assertions pass
* All existing deterministic STTM assertions pass
* Runner exit code is 0

Label PASS narrowly as a Test-mode direct-tool structured-result characterization. Do not describe it as full Production, Copilot Chat UI, model-provider, or Agent integration validation.

FAIL

FAIL applies only if the real invokeTool call returned its raw LanguageModelToolResult and at least one authored structured-result assertion then failed.

Report the first failing assertion and the observed:

* Part count
* Part order
* Runtime types
* MIME type
* Byte length
* UTF-8/JSON outcome
* Cross-channel comparison
* Deterministic STTM comparison

Do not convert a genuine post-boundary assertion failure into BLOCKED because the runner exited nonzero.

BLOCKED

BLOCKED applies to any failure before a real LanguageModelToolResult returns, including:

* Preflight or environment gate failure
* Invalid development-path shape
* Built-in shadowing of the explicit Copilot development extension
* Dependency still unknown
* Copilot activation failure
* ETL activation failure
* Tool-registration failure
* Missing-tool or rejected invokeTool call
* Host boot failure
* Zero focused suites
* before-all failure before the raw result returns
* Approval, sign-in, or trust interruption
* Timeout
* Missing or ambiguous result evidence

A process exit code alone does not determine classification.

Unless this exact run directly proves otherwise, report these nonblocking observations exactly as:

parser cardinality: NOT_INDEPENDENTLY_OBSERVABLE

resolved source: NOT_OBSERVED_BY_CURRENT_TEST

Neither observation is required for a structured transport-boundary PASS.

Step 6 — Post-run containment and integrity

After the single invocation:

1. Restore all changed process-local environment variables to their prior presence/value inside a finally path, without logging values.
2. Do not delete the new isolation/evidence root.
3. Confirm no matching isolated Host process remains.
4. Recompute every complete pre-run source and compiled SHA-256 and require exact equality.
5. Reverify repository branch, HEAD, and exact four-line Git status.
6. Require package.json, tsconfig.json, and extensionDependencies to remain unchanged.
7. Require no repository or out/** hash/timestamp change caused by this phase.
8. Reverify the protected request and focused-test fixed hashes.
9. Reverify the 23-file QA inventory and fixed workbook size/hash.
10. Identify any QA file whose write timestamp changed during the Host window. Expected count: 0.
11. Reverify the bundled Copilot inventory, identity, and pre-run fingerprint.
12. Require no bundled Copilot mutation.
13. Confirm no extension was copied, seeded, or installed.
14. Inventory and retain all new evidence files under the single new root.
15. Do not clean up, retry, repair, compile, or begin another phase.

Final report

Report:

* PASS, FAIL, or BLOCKED
* Exact stopping boundary
* Full runtime observations
* Raw-result evidence if reached
* Complete repository, compiled-output, Copilot, and QA integrity results
* Retained isolation/evidence path
* Operational counters

Expected counters for a completed launch:

* Repository edits: 0
* QA edits: 0
* Compiled-file edits: 0
* Extension copies/seeds/installations: 0
* Compiles: 0
* Runner invocations: 1
* Host launches: 1
* Retries/relaunches: 0
* invokeTool calls: 1 only if the registration boundary is reached

End with exactly one marker:

F5_LOCAL_MULTI_DEVELOPMENT_PATH_REAL_HOST_PASS

or

F5_LOCAL_MULTI_DEVELOPMENT_PATH_REAL_HOST_FAIL

or

F5_LOCAL_MULTI_DEVELOPMENT_PATH_REAL_HOST_BLOCKED
