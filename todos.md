Phase 1B.3M — Windows Multi-Development-Path Transport Repair and Compile

Work locally in the currently open desktop VS Code repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

This phase is a narrowly scoped source repair, compile, and no-Host argument-transport verification.

Do not ask for another implementation confirmation. The user authorizes the bounded edit and single compile described below.

Preceding authoritative result

Phase 1B.3L ended with:

F5_LOCAL_MULTI_DEVELOPMENT_PATH_REAL_HOST_BLOCKED

It was BLOCKED before the raw LanguageModelToolResult boundary.

Observed facts:

* Runner invocations: 1
* Extension Host launches attempted/proven: 1/1
* VS Code: 1.135.0
* Host PID: 25948
* Focused suites selected: 1
* Authored/evaluated test bodies: 8/0
* Mocha passes/failures/pending: 0/1/0
* etl_interpret_sttm registrations: 0
* vscode.lm.invokeTool calls: 0
* Real LanguageModelToolResult returned: no
* Runner exit code: 1
* Retries/relaunches: 0
* Repository and QA integrity: fully preserved

The intended second development path was:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot

The effective path observed by the Host was truncated at the first space to:

C:\Users\tag5916\AppData\Local\Programs\Microsoft

Therefore github.copilot-chat never entered the extension registry and ETL activation failed with:

Cannot activate the ‘Databricks ETL Copilot’ extension because it depends on unknown extension ‘github.copilot-chat’

No built-in shadowing occurred. The explicit second development path was malformed before registry discovery.

Retained 1B.3L evidence root:

C:\Users\tag5916\AppData\Local\Temp\etl-phase-1b3l-multipath-20260902-155503-6c19c9c08c74

Treat that directory as read-only and retain it unchanged.

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

Expected pre-repair SHA-256 for src/test/runTest.ts:

7BD59B54E5D2C7018CB65E77A248E2D8E95771D3BCA6FED79A6C5CA2AB610E3A

Expected pre-repair SHA-256 for out/test/runTest.js:

DA55A159540D1A5F3D50C369C66304BF278B07DC0AF647A609BFEABD82E68EC3

Expected unchanged src/extension.ts SHA-256:

4872337F0F97BBB2A2109F21EE7F362CD4A35F5932B49533936DE8E48FBFC7BC

Expected unchanged out/extension.js SHA-256:

2A323B09ACB640F5DAF50C494951242B3CAC4779A7B095A3EB92A499B5E5890

Scope

The only authored source file permitted to change is:

src/test/runTest.ts

Compilation may regenerate out/**, but only out/test/runTest.js is expected to change semantically.

Do not edit:

* src/extension.ts
* src/test/suite/sttmRealHostStructuredResult.test.ts
* package.json
* tsconfig.json
* package-lock.json
* node_modules/**
* .github/templates/request.md
* QA files
* bundled Copilot files
* retained evidence
* any other source or configuration file

Do not upgrade, downgrade, patch, or reinstall @vscode/test-electron.

Absolute prohibitions

Do not:

* Launch Code.exe.
* Launch an Extension Host.
* Invoke out/test/runTest.js.
* Run the focused integration suite.
* Use F5.
* Use Cloud or ETL Orchestrator.
* Copy, seed, install, or download an extension.
* Use Marketplace or VSIX.
* Change extensionDependencies.
* Hard-code this machine’s Copilot path in source.
* Use an 8.3 short path.
* Modify node_modules.
* Stage, commit, stash, restore, reset, or clean.
* Retry compilation.
* Perform a real Host rerun in this phase.

Exactly one npm run compile is authorized after the repair is statically reviewed.

A small no-Host argv transport probe using cmd.exe/node.exe and temporary files is authorized. It must not invoke Code.exe or the compiled test runner.

Step 1 — Read-only preflight

Before editing:

1. Verify repository path, branch, HEAD, and exact four-line Git status.
2. Verify all fixed hashes above.
3. Verify git diff –check passes.
4. Verify package-lock.json remains absent.
5. Verify the retained 1B.3L evidence root exists and is unchanged.
6. Read the decisive retained logs and confirm:
    * The ETL repository path arrived intact.
    * The Copilot development path was truncated at its first space.
    * github.copilot-chat was absent from the effective registry.
    * The raw result boundary was not reached.
7. Inspect the exact installed implementation used by this repository:
    node_modules@vscode\test-electron\out\runTest.js
8. Verify the installed package version from its local package.json.
9. Determine and report the exact argument-construction and process-launch behavior, including:
    * How string[] extensionDevelopmentPath is converted into repeated –extensionDevelopmentPath arguments.
    * Whether each value is quoted or escaped.
    * Whether child_process.spawn uses shell: true on Windows.
    * The exact executable supplied by the current runner.
    * Whether the failure is produced at the project adapter, installed library, Windows shell, or VS Code parser boundary.

Do not treat the previous report’s phrase “Windows shell splitting in @vscode/test-electron” as a substitute for inspecting the exact installed implementation.

If the retained evidence and installed implementation do not support one coherent transport diagnosis, stop without editing and classify BLOCKED.

Step 2 — Design the smallest repair

Repair only the Windows transport boundary in src/test/runTest.ts.

Required invariants:

1. Continue using exactly one runTests(…) call.
2. Continue using the supported top-level extensionDevelopmentPath option.
3. Normal runs must continue passing exactly one ETL development path.
4. Isolated-dependency runs must continue representing exactly two ordered development extensions:
    [etlRepositoryPath, bundledCopilotExtensionPath]
5. Validate the original raw Copilot path and manifest before applying any transport encoding.
6. The original raw path remains the authoritative identity.
7. Do not change the existing Copilot identity, version, engine, installation-containment, canonical-path, file-count, or reparse-point validations.
8. Apply any Windows-specific transport representation only at the final adapter boundary immediately before runTests.
9. Non-Windows behavior must remain unchanged.
10. Ordinary non-isolated behavior must remain unchanged.
11. Do not introduce shell-string concatenation for the whole command.
12. Do not add a second runTests call.
13. Do not add a retry.
14. Do not add a manual Code.exe launch.
15. Do not place –extensionDevelopmentPath into launchArgs.
16. Preserve existing environment sanitation/restoration and finally behavior.
17. Preserve absence of –disable-extensions in isolated-dependency mode.
18. Do not mutate the environment variable’s original path value.

Preferred repair

If the installed 2.5.2 behavior matches the retained evidence, implement a narrowly scoped Windows-safe argument representation for each development-path value passed to runTests.

The representation must cause the Windows shell layer to deliver each complete:

–extensionDevelopmentPath=

as one argument even when the path contains spaces.

Requirements:

* Apply quoting or encoding exactly once.
* Never double-quote an already encoded value.
* Keep validation and canonical comparison on the unencoded raw path.
* Reject NUL, CR, LF, embedded quote, or any character that cannot safely pass through the installed Windows shell behavior.
* Fail closed before Host launch if safe representation cannot be guaranteed.
* Include a comment explaining that this adapter compensates for the verified Windows shell behavior of the repository’s installed @vscode/test-electron version.
* Do not apply unnecessary quoting on non-Windows systems.

Do not add literal quotes merely because they look plausible. The exact produced argv must be proven by the no-Host probe.

Permitted fallback

Use this only if the no-Host probe proves that a safely quoted raw path cannot survive the installed library’s Windows shell boundary.

The only permitted fallback is a temporary, no-space directory junction beneath the already-authorized future isolation root that resolves canonically to the validated bundled Copilot directory.

Fallback requirements:

* No extension copy, seed, installation, or content duplication.
* The junction must not be created inside the isolated extensions directory.
* The canonical real path must equal the audited bundled Copilot path.
* The source and target manifests must resolve to the same file identity/content.
* The alias path must contain no whitespace or shell metacharacters.
* Creation must occur only for an opted-in isolated-dependency run.
* Normal runs and non-Windows runs must not create it.
* Failure to create or validate it must fail closed before runTests.
* Do not select this fallback without reporting why direct argument preservation was disproved.

Do not implement both strategies simultaneously.

Step 3 — Static review before compile

Before compiling, inspect the diff and prove:

* Only src/test/runTest.ts has a new authored change.
* No machine-specific Copilot installation path was added.
* No dependency or package change occurred.
* Exactly one runTests call remains.
* The ordered two-path contract remains.
* Raw-path validation occurs before transport encoding.
* Normal mode remains unchanged.
* Non-Windows behavior remains unchanged.
* No Host invocation or retry was added.
* git diff –check passes.

If the static review fails, stop before compile and classify BLOCKED.

Step 4 — Compile exactly once

From the repository root, invoke exactly once:

npm run compile

Record:

* Start time
* End time
* Observable stdout/stderr
* Exit code
* Compile count

Do not retry the compile.

If exit code is nonzero, stop, report the error, and classify BLOCKED. Do not repair and compile again in this phase.

Step 5 — No-Host argv transport proof

Do not invoke Code.exe or out/test/runTest.js.

Create one unique temporary evidence directory outside the repository, QA root, bundled Copilot directory, and all prior evidence roots.

Using a harmless temporary Node argv-recorder and the exact verified Windows command-shell semantics, prove that the post-repair transport representation produces exactly two complete development-path arguments in order:

1. –extensionDevelopmentPath=C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
2. –extensionDevelopmentPath=C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot

The recorded argv must contain neither:

* C:\Users\tag5916\AppData\Local\Programs\Microsoft

as a truncated standalone development path, nor separate fragments beginning with:

* VS
* Code\

Also prove:

* Exactly two development-path arguments exist.
* Their order is preserved.
* The second value is byte-for-byte equal to the original unencoded path after shell parsing.
* No literal transport quotes remain in the child argv.
* The repository path is unchanged.
* No Code.exe process or Extension Host was started.
* The probe executed exactly once.
* The probe directory contains only its recorder, result, and verification evidence.

If the argv proof fails, do not attempt another encoding, compile, or probe in this phase. Classify BLOCKED and retain the evidence.

Step 6 — Post-compile integrity

Verify:

* Branch and HEAD remain unchanged.
* Git status remains exactly the same four paths.
* src/test/runTest.ts has a new expected repair hash.
* out/test/runTest.js has a new expected compiled hash.
* src/extension.ts remains exactly:
    4872337F0F97BBB2A2109F21EE7F362CD4A35F5932B49533936DE8E48FBFC7BC
* out/extension.js remains exactly:
    2A323B09ACB640F5DAF50C494951242B3CAC4779A7B095A3EB92A499B5E5890
* Protected request and focused-test hashes remain exact.
* package.json and tsconfig.json remain byte-for-byte unchanged.
* package-lock.json remains absent.
* extensionDependencies remains exactly [“github.copilot-chat”].
* QA remains 23 files.
* Workbook remains 13,201 bytes with SHA-256:
    3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA
* Bundled Copilot remains 98 files with zero source reparse points and unchanged fingerprint.
* Retained 1B.3L evidence remains unchanged.
* No matching Extension Host process exists.
* No test or Host result was claimed.

Compilation may refresh generated-file timestamps. Evaluate compiled integrity by content/hash and expected semantic change, not timestamp alone.

PASS requirements

PASS requires:

* Exact preflight identity.
* Coherent installed-library transport diagnosis.
* Only src/test/runTest.ts authored.
* One successful compile with exit code 0.
* No Host or integration test launch.
* Exactly one successful no-Host argv probe.
* Two complete development paths preserved in exact order.
* Full spaced Copilot path preserved as one child argv entry.
* No truncated path or residual fragments.
* All protected source, repository, QA, Copilot, and evidence identities preserved.
* No package or dependency change.

PASS proves only Windows-safe multi-development-path argument transport and compile readiness. It does not prove Copilot discovery, activation, tool registration, invokeTool, or the structured result.

Final report

Report:

* Diagnosis and exact splitting layer
* Repair strategy selected
* Exact authored diff scope
* Compile result and count
* No-Host argv probe result
* Exact recorded two development-path arguments
* Pre/post hashes
* Repository and QA integrity
* Retained probe-evidence path
* Operational counters

Expected counters:

* Authored source files changed in this phase: 1
* Compiles: 1
* No-Host argv probes: 1
* Runner invocations: 0
* Code.exe invocations: 0
* Extension Host launches: 0
* Focused tests evaluated: 0
* invokeTool calls: 0
* Extension copies/seeds/installations: 0
* Retries: 0

End with exactly one marker:

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_REPAIR_PASS

or

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_REPAIR_BLOCKED
