Phase 1B.3N — One-Shot Multi-Development-Path Real-Host Structured-Result Run

Environment

Run locally in VS Code Agent mode from:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

This is an operational-only, one-shot real Extension Host characterization.

The Windows multi-development-path transport repair has already passed an independent no-Host argv proof. Do not repeat that probe.

Objective

Launch exactly one fresh isolated VS Code Extension Host using the current compiled runner and these two ordered development-extension paths:

1. ETL repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

2. Bundled Copilot extension:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot

Run the existing focused structured-result suite exactly once and determine whether the raw vscode.LanguageModelToolResult.content boundary preserves the expected structured parts.

Absolute prohibitions

* Do not edit any source, test, generated, package, configuration, QA, or extension file.
* Do not compile.
* Do not run npm install, npm update, or package preparation.
* Do not copy, seed, install, update, disable, or modify any extension.
* Do not use the normal VS Code profile.
* Do not use Marketplace or network remediation.
* Do not launch manually with F5.
* Do not invoke Code.exe --version.
* Do not run a second Host, runner, suite, or test attempt.
* Do not retry after any failure.
* Do not repair any newly observed problem.
* Do not stage, commit, stash, restore, reset, clean, switch branches, or modify Git state.
* Do not expose environment-variable values other than the explicitly authorized paths and test-control flags.
* Do not substitute earlier results for evidence from this run.

Step 1 — Read-only preflight

Record:

* repository root;
* branch;
* HEAD;
* exact git status --porcelain;
* resolved node.exe;
* installed @vscode/test-electron version;
* VS Code executable path;
* bundled Copilot canonical path, manifest ID, version, engine, file count, and reparse-point count;
* absence of a matching still-running isolated Host from earlier phases.

Require:

* branch: fix/workspace-write-completion-0.3.148
* HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
* VS Code: 1.135.0
* bundled dependency ID: github.copilot-chat
* bundled dependency version: 0.63.0
* bundled dependency engine: ^1.135.0

Verify these SHA-256 values exactly:

* src/test/runTest.ts
    05A083F77C6231443A2169502AFE4CA6702305E157A02ECF9C4B1744ECD56787
* out/test/runTest.js
    730F294F961AE3CBE7E56DE08BE5AF22E7614435497257E945F6D4EF3A2346C1
* src/extension.ts
    4872337F0F97BBB2A2109F21EE7F362CD4A35F5932B49533936DE8E48FBFC7BC
* out/extension.js
    2A323B09ACB640F65DAF50C494951242B3CAC4779A7B095A3EB92A499B5E5890
* .github/templates/request.md
    2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84
* src/test/suite/sttmRealHostStructuredResult.test.ts
    8713EC3B3F2F75B06541F9B68AC4D9026CA0A17D052E07898EA12C5E12FAABCE
* package.json
    7D0D882FA21594B7B04FA7F282221EA837A5FEB3BAF5D5BB8E0F19BF08B58B40C
* tsconfig.json
    06E2452EBB943F26DF490129ABD39B630BF44C5DA5C936E66ADBA9993EAB856E

Also verify:

* QA inventory: exactly 23 files;
* workbook size: exactly 13,201 bytes;
* workbook SHA-256:
    3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA
* git diff --check exits 0; the already-known line-ending warning alone is not a blocker.

If any required premise differs, stop before launch and classify BLOCKED.

Step 2 — Understand the existing runner contract

Read the current source and compiled runner plus the focused test before launch.

Use their existing authoritative environment-variable names and launch contract. Do not invent a replacement runner or duplicate its logic.

Confirm statically that this run will:

* enable isolated dependencies;
* use the bundled Copilot path;
* enable Test-only/read-only-tool-only activation;
* pass the two ordered development paths through the repaired Windows adapter;
* create fresh isolated user-data and extensions directories;
* select exactly the intended focused suite;
* call the top-level runTests(...) exactly once;
* restore all process-scoped environment variables in finally.

Step 3 — Create evidence root

Create one unique %TEMP% isolation/evidence root outside:

* the repository;
* the QA workspace;
* all earlier retained evidence roots.

Record its exact path before launch.

All observable runtime, Mocha, terminal, activation, registry, and structured-result evidence must be retained there.

Do not place evidence in the repository or QA workspace.

Step 4 — One authorized execution

Set only the existing runner’s required test-control environment variables, using the exact bundled Copilot path above.

Invoke:

node.exe out\test\runTest.js

exactly once from the repository root.

This invocation consumes the complete execution budget.

Do not relaunch regardless of stdout quality, exit code, timeout, activation failure, test failure, or missing evidence.

Wait only within the runner’s existing bounded timeout. After it returns, perform read-only evidence collection.

Step 5 — Required observations

Report only directly observed facts for:

* runner invocations;
* Host launches attempted and proven;
* actual Host VS Code version and PID;
* both development-extension paths as resolved by the Host;
* ETL extension identity and version;
* Copilot dependency discovery, identity, version, and activation state;
* ETL activation state;
* etl_interpret_sttm registration count;
* focused suites selected;
* authored test bodies;
* evaluated test bodies;
* Mocha passes, failures, pending, and duration;
* vscode.lm.invokeTool call count;
* raw LanguageModelToolResult.content availability;
* structured part count, order, runtime types, MIME values, and byte lengths;
* strict UTF-8 decoding;
* JSON decoding;
* deterministic STTM comparison;
* parser invocation cardinality, only if independently observable;
* resolved source value, only if independently observed;
* runner exit code;
* retained evidence files.

Never infer an unobserved value and never replace missing runtime evidence with static source expectations.

Step 6 — Classification

PASS

Classify PASS only if:

* exactly one runner and one Host launch occurred;
* the Host received both complete development-extension paths;
* github.copilot-chat was discovered and usable;
* the ETL extension activated;
* etl_interpret_sttm registered exactly once;
* exactly the intended focused suite executed;
* vscode.lm.invokeTool was called exactly once;
* the raw structured-result boundary was reached;
* every existing focused structured-result assertion passed;
* the runner exited 0.

FAIL

Classify FAIL only if the real raw structured-result boundary was reached but one or more focused assertions failed.

Report the exact expected-versus-observed mismatch without repair or retry.

BLOCKED

Classify BLOCKED if execution stopped before the raw structured-result boundary, including:

* dependency discovery or activation failure;
* ETL activation or registration failure;
* Host/runner infrastructure failure;
* suite-selection failure;
* timeout before the boundary;
* missing authoritative evidence.

Do not misclassify a pre-boundary blocker as FAIL.

Step 7 — Final integrity

After completion, verify:

* branch and HEAD unchanged;
* Git status exactly matches preflight;
* all pinned hashes unchanged;
* QA inventory, workbook size, and workbook hash unchanged;
* bundled Copilot inventory unchanged;
* repository and QA edits made by this phase: 0;
* compiles: 0;
* runner invocations: 1;
* retries/relaunches: 0;
* extension copies/installations: 0;
* no matching isolated Host process remains;
* all process-scoped environment variables were restored.

Retain the isolation/evidence root for every classification and report its exact full path.

End with exactly one marker:

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_REAL_HOST_PASS

or

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_REAL_HOST_FAIL

or

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_REAL_HOST_BLOCKED
