Phase 1B.3N-R — Corrected Preflight and First Real-Host Execution

Run locally from:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Phase 1B.3N stopped during preflight. Runner invocations and Host launches were both zero, so the authorized one-shot real-Host execution budget remains unused.

The previous BLOCKED result was caused by:

1. an incorrect 65-character pinned package.json hash;
2. PowerShell converting known native stderr output from git diff --check into a terminating NativeCommandError.

These are preflight-harness defects, not product failures.

Prohibitions

* Do not edit any repository, generated, package, test, QA, or extension file.
* Do not compile.
* Do not install, copy, seed, update, or disable extensions.
* Do not modify node_modules.
* Do not use F5.
* Do not use the normal VS Code profile.
* Do not retry or relaunch.
* Do not stage, commit, stash, restore, reset, clean, or switch branches.
* Do not treat this as a second Host attempt: no Host was launched previously.

1. Corrected preflight

Require:

* Branch: fix/workspace-write-completion-0.3.148
* HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Exact Git status:

 M .github/templates/request.md
 M src/extension.ts
 M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Verify these SHA-256 values:

src/test/runTest.ts
05A083F77C6231443A2169502AFE4CA6702305E157A02ECF9C4B1744ECD56787
out/test/runTest.js
730F294F961AE3CBE7E56DE08BE5AF22E7614435497257E945F6D4EF3A2346C1
src/extension.ts
4872337F0F97BBB2A2109F21EE7F362CD4A35F5932B49533936DE8E48FBFC7BC
out/extension.js
2A323B09ACB640F65DAF50C494951242B3CAC4779A7B095A3EB92A499B5E5890
.github/templates/request.md
2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84
src/test/suite/sttmRealHostStructuredResult.test.ts
8713EC3B3F2F75B06541F9B68AC4D9026CA0A17D052E07898EA12C5E12FAABCE
package.json
7D0D882FA21594B7B04FA7F28221EA837A5FEB3BAF5D5BB8E0F19BF08B58B40C
tsconfig.json
06E2452EBB943F26DF490129ABD39B630BF44C5DA5C936E66ADBA9993EAB856E

The corrected package.json hash is exactly 64 hexadecimal characters. Do not reuse the earlier 65-character literal.

Verify:

* VS Code executable resolves beneath the versioned application directory;
* VS Code manifest version is 1.135.0;
* installed @vscode/test-electron is 2.5.2;
* bundled Copilot canonical path is:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot

* Copilot ID is github.copilot-chat;
* Copilot version is 0.63.0;
* engine is ^1.135.0;
* inventory is 98 files with zero reparse points;
* QA inventory is 23 files;
* workbook size is 13,201 bytes;
* workbook SHA-256 is:

3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA

Reliable git diff --check

Run git diff --check through a read-only .NET ProcessStartInfo invocation with:

* UseShellExecute = false;
* stdout redirected;
* stderr redirected;
* the process exit code captured directly.

A known LF-to-CRLF warning on stderr is informational when the actual process exit code is 0. Do not classify stderr presence alone as failure.

If the actual exit code is nonzero or any other premise differs, stop before Host launch and report BLOCKED.

2. One fresh evidence root

Create one new unique evidence/isolation root under %TEMP%, outside the repository, QA workspace, and all prior evidence roots.

Retain it after completion regardless of PASS, FAIL, or BLOCKED.

3. One authorized real execution

Read the existing source and compiled runner to use their authoritative environment-variable names.

Configure the existing isolated test controls so that the runner uses:

1. ETL development path:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

2. Bundled Copilot development path:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot

Enable the existing isolated-dependency and Test-only/read-only-tool-only controls.

Then invoke exactly once from the repository root:

C:\Program Files\nodejs\node.exe out\test\runTest.js

Do not invoke it again under any circumstance.

4. Required runtime evidence

Report directly observed values for:

* runner invocations;
* Host launches attempted/proven;
* Host PID and VS Code version;
* both development paths received by the Host;
* discovery and activation of github.copilot-chat;
* activation of the ETL extension;
* etl_interpret_sttm registration count;
* selected suite count;
* authored and evaluated test counts;
* Mocha passes/failures/pending;
* vscode.lm.invokeTool calls;
* whether raw LanguageModelToolResult.content was reached;
* structured-part count, order, runtime types, MIME types, and byte lengths;
* UTF-8 and JSON decoding;
* deterministic STTM comparison;
* parser cardinality and resolved source only when independently observable;
* runner exit code.

5. Classification

PASS only if one runner and one Host launch occur, both development paths arrive intact, both extensions activate, the tool registers exactly once, invokeTool runs exactly once, the raw structured boundary is reached, every focused assertion passes, and the runner exits 0.

FAIL only if the raw structured-result boundary is reached and an assertion fails.

BLOCKED if execution stops before that boundary.

Never classify a dependency, activation, registration, Host, or suite-selection problem as FAIL.

6. Final integrity

Verify:

* branch, HEAD, Git status, and all pinned hashes unchanged;
* QA and Copilot inventories unchanged;
* repository and QA edits: 0;
* compiles: 0;
* runner invocations: 1 if preflight passed, otherwise 0;
* Host launches: at most 1;
* retries/relaunches: 0;
* extension copies/installations: 0;
* no matching isolated Host remains;
* process-scoped environment restored.

Report the full retained evidence-root path.

End with exactly one marker:

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_REAL_HOST_PASS

or

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_REAL_HOST_FAIL

or

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_REAL_HOST_BLOCKED
