# Phase 1B.3K — Multi-Development-Path Harness Patch and Compile

Work locally in the currently open desktop VS Code repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

This is a narrowly authorized implementation-and-compile phase.

Do not request another implementation confirmation. Platform permission prompts
may still be shown.

Do not launch an Extension Host in this phase.

## Authoritative preceding decision

Phase 1B.3J completed with:

B. FUNCTIONAL_DEPENDENCY_REQUIRES_MULTI_DEVELOPMENT_PATH_TEST

The manifest-only dependency-removal hypothesis was DISPROVED.

Established facts:

1. Root package.json is the authoritative extension manifest.
2. package.json declares github.copilot-chat in extensionDependencies.
3. src/extension.ts explicitly resolves and activates github.copilot-chat before
   ETL read-only tool registration.
4. The STTM tool uses stable VS Code core APIs, but the current production
   activation flow still treats Copilot Chat activation as a prerequisite.
5. Installed @vscode/test-electron 2.5.2 supports:

   extensionDevelopmentPath: string | string[]

6. It emits one --extensionDevelopmentPath argument for every array entry.
7. VS Code merges development extensions after built-in extensions, allowing an
   explicit Copilot development path to replace the same built-in identifier.
8. The supported future launch shape is:

   extensionDevelopmentPath: [
     etlRepositoryPath,
     bundledCopilotExtensionPath
   ]

9. The existing ExtensionMode.Test early return currently occurs before Copilot
   readiness and ETL read-only tool registration.
10. Production behavior must remain unchanged.

Audited bundled Copilot directory:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot

Audited package identity:

- canonical ID: github.copilot-chat
- version: 0.63.0
- engines.vscode: ^1.135.0
- extensionDependencies: absent or empty
- file inventory: 98 files
- reparse points: none

## Fixed repository state

Expected branch:

fix/workspace-write-completion-0.3.148

Expected HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected pre-edit Git status, exactly:

 M .github/templates/request.md
 M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Protected-file SHA-256:

.github/templates/request.md
2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84

Current runner-source SHA-256:

src/test/runTest.ts
56CF4FAB4CA798178C503806BDE94D8ABAB59F1E861B9D44B14A27442DE0E771

Focused-test SHA-256:

src/test/suite/sttmRealHostStructuredResult.test.ts
8713EC3B3F2F75B06541F9B68AC4D9026CA0A17D052E07898EA12C5E12FAABCE

Read hashes directly from disk. Do not use screenshots or OCR as hash evidence.

## Authorized scope

Authored source edits are allowed only in:

1. src/test/runTest.ts
2. src/extension.ts

One compile may regenerate files under:

out/**

Do not modify:

- package.json;
- package-lock.json;
- tsconfig.json;
- .github/templates/request.md;
- src/test/suite/sttmRealHostStructuredResult.test.ts;
- tool implementation files;
- QA files;
- installed VS Code files;
- bundled Copilot files;
- previous isolation/evidence directories.

Do not:

- remove or alter extensionDependencies;
- hard-code the local Copilot path in source;
- install, copy or seed an extension;
- use Marketplace or network access;
- run npm install;
- run tests;
- run F5;
- invoke Code.exe;
- invoke out/test/runTest.js;
- launch an Extension Host;
- invoke vscode.lm.invokeTool;
- use Cloud, ETL Orchestrator or another worktree;
- stage, commit, stash, restore, reset or clean;
- retry a failed compile.

This phase authorizes exactly one compile command:

npm run compile

No other npm, npx, tsc or esbuild invocation is authorized.

## Step 1 — Pre-edit gate

Before editing, verify:

1. Repository path, branch, HEAD and exact three-line Git status.
2. All fixed hashes above.
3. package.json still declares exactly the github.copilot-chat dependency.
4. Capture pre-edit hashes for package.json and src/extension.ts.
5. The bundled Copilot directory and manifest still prove the audited identity.
6. The Copilot path is inside the selected VS Code application installation,
   contains no reparse points and has the expected 98-file inventory.
7. @vscode/test-electron still supports string | string[] and emits one
   development-path argument per array entry.
8. src/test/runTest.ts still contains:
   - exactly one runTests(...) call;
   - top-level extensionDevelopmentPath;
   - no bare positional extensionDevelopmentPath in launchArgs;
   - scoped sanitation/restoration for ELECTRON_RUN_AS_NODE, VSCODE_CLI and
     ELECTRON_NO_ATTACH_CONSOLE;
   - restoration in finally;
   - no retry;
   - no --disable-extensions in isolated-dependency mode.
9. src/extension.ts still contains:
   - the ordinary ExtensionMode.Test early return;
   - the existing Copilot resolve/activate/readiness path;
   - a separable ETL read-only tool-registration point;
   - participant/sidebar/action-tool/UI initialization after that point.
10. Capture pre-compile hashes of the five pinned compiled artifacts.
11. QA inventory remains exactly 23 files.
12. The workbook remains 13201 bytes with SHA-256:

    3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA

If a fixed identity or required premise differs, make no edits, do not compile
and classify BLOCKED.

## Step 2 — Add the narrow runner contract

Modify only src/test/runTest.ts.

Reuse an equivalent existing contract if one already exists. Otherwise add this
test-only environment contract:

ETL_TEST_COPILOT_EXTENSION_PATH

Required behavior:

1. Consult it only when ETL_TEST_ENABLE_ISOLATED_DEPENDENCIES is enabled.
2. In isolated-dependency mode:
   - require a nonempty value;
   - require an absolute existing directory;
   - resolve and normalize its real path;
   - require it to remain inside the selected VS Code installation root;
   - read its package.json;
   - require canonical ID github.copilot-chat;
   - require a nonempty version and VS Code engine;
   - fail before runTests if validation fails;
   - do not hard-code the machine path or version into source;
   - pass exactly:

     extensionDevelopmentPath: [
       etlRepositoryPath,
       bundledCopilotExtensionPath
     ]

3. Outside isolated-dependency mode:
   - do not require or resolve the Copilot path;
   - preserve the existing single ETL development path;
   - preserve default runner behavior.
4. Pass development paths only through the top-level runTests option.
5. Do not put either path in launchArgs.
6. Do not manually construct --extensionDevelopmentPath arguments.
7. Preserve:
   - exactly one runTests(...) invocation;
   - executable-path override;
   - isolation-root/user-data/extensions-directory contracts;
   - the existing --disable-extensions gate;
   - process-variable sanitation and finally restoration;
   - no retries or fallback launches.
8. Do not log environment-variable values.

Do not copy or mutate the bundled Copilot extension.

## Step 3 — Add an explicitly gated Test-mode activation path

Modify only src/extension.ts.

Use this exact additional opt-in contract:

ETL_TEST_READ_ONLY_TOOL_ONLY=1

The special activation path must require both:

context.extensionMode === vscode.ExtensionMode.Test

and:

process.env.ETL_TEST_READ_ONLY_TOOL_ONLY === '1'

Required behavior:

### Ordinary Test mode without the opt-in

Preserve the current early-return behavior exactly.

It must not activate Copilot or register tools merely because the extension is
running in Test mode.

### Opted-in Test mode

When both conditions are true:

1. Execute the existing production Copilot resolution, activation and readiness
   checks without bypassing, weakening or mocking them.
2. Register exactly the existing ETL read-only Language Model Tool:

   etl_interpret_sttm

3. Use the same production implementation and registration logic.
4. Add the registration disposable to context.subscriptions.
5. Return immediately after read-only tool registration.
6. Do not initialize or register:
   - chat participant UI;
   - sidebar or view UI;
   - action/write tools;
   - unrelated commands;
   - walkthrough/onboarding behavior;
   - model selection;
   - model sendRequest calls;
   - authentication or sign-in behavior.

### Production and Development modes

Preserve their existing behavior and registration order.

The presence of ETL_TEST_READ_ONLY_TOOL_ONLY in Production or Development mode
must have no effect.

Additional requirements:

- Do not register etl_interpret_sttm twice.
- Do not duplicate its implementation.
- Do not create a fake Copilot dependency or fake vscode.lm API.
- Do not change the tool ID, input or result contract.
- Do not refactor unrelated activation code.
- Prefer a narrow relocation/gating of the existing Test-mode early return.
- Keep package.json and extensionDependencies unchanged.

If these requirements cannot be satisfied through a narrow change, stop before
compile and classify FAIL.

## Step 4 — Pre-compile static verification

Before compiling, verify:

### Runner

- exactly one runTests(...) call;
- isolated mode produces exactly two development paths;
- order is ETL repository first and bundled Copilot second;
- normal mode retains one ETL development path;
- ETL_TEST_COPILOT_EXTENSION_PATH is consulted only in isolated mode;
- no hard-coded user or VS Code installation path;
- no positional development path;
- no manually constructed --extensionDevelopmentPath flag;
- no retry;
- existing sanitation/restoration remains in finally;
- existing --disable-extensions behavior remains unchanged.

### Activation

Verify all four cases:

1. Production mode, regardless of test opt-in:
   existing production activation remains unchanged.

2. Development mode, regardless of test opt-in:
   existing development activation remains unchanged.

3. Test mode without ETL_TEST_READ_ONLY_TOOL_ONLY=1:
   existing early return remains unchanged.

4. Test mode with ETL_TEST_READ_ONLY_TOOL_ONLY=1:
   Copilot readiness executes, etl_interpret_sttm registers exactly once, and
   all participant/sidebar/action/write/UI initialization is unreachable.

Also verify:

- failed or missing Copilot activation registers no ETL tool;
- package.json dependency remains unchanged;
- no environment values are logged;
- neither new environment contract is mutated by the source.

If static verification fails, do not compile. Report FAIL.

## Step 5 — Compile exactly once

Record a UTC compile-start timestamp.

From the repository root invoke exactly once:

npm run compile

Capture stdout, stderr and exit code.

Do not retry.

Do not run any test, compiled runner, Code.exe or Extension Host afterward.

## Step 6 — Post-compile verification

PASS requires:

1. The single compile exits 0.
2. All five pinned compiled artifacts exist and are newer than compile start.
3. out/test/runTest.js proves:
   - exactly one runTests call;
   - conditional single-path versus ordered two-path behavior;
   - the new Copilot-path contract;
   - no hard-coded local path;
   - no manual/positional development-path argument;
   - no retry;
   - retained sanitation and finally restoration.
4. out/extension.js proves all four activation cases above.
5. package.json is byte-for-byte unchanged.
6. extensionDependencies remains unchanged.
7. package-lock.json and tsconfig.json remain unchanged.
8. request.md and the focused test retain their fixed hashes.
9. Only src/test/runTest.ts and src/extension.ts have authored changes.
10. Generated changes are confined to out/**.
11. Branch and HEAD remain unchanged.
12. Final Git status is exactly:

    M .github/templates/request.md
    M src/extension.ts
    M src/test/runTest.ts
    ?? src/test/suite/sttmRealHostStructuredResult.test.ts

13. QA inventory and workbook remain unchanged.
14. Bundled Copilot remains unchanged.
15. Operational counters remain:
    - test executions: 0;
    - runner invocations: 0;
    - Host launches: 0;
    - invokeTool calls: 0;
    - extension copies/installations: 0;
    - retries: 0.

This phase proves only patch integrity, compilation and static launch-shape
readiness. It does not prove production Copilot/Agent integration.

## Final report

Report:

- classification;
- exact authored files changed;
- new/reused environment contracts and semantics;
- Test-mode activation behavior before and after;
- confirmation that production behavior and package dependency are preserved;
- static verification;
- compile count and exit code;
- relevant source and compiled pre/post hashes;
- final branch, HEAD and Git status;
- QA/workbook integrity;
- bundled Copilot integrity;
- all operational counters.

Classification:

- PASS: both narrow edits, static verification, one compile and all integrity
  checks succeed.
- FAIL: an authorized edit occurred but static verification or compilation
  failed. Preserve the working tree and do not retry.
- BLOCKED: a pre-edit identity or prerequisite failed. Make no edits.

End with exactly one marker:

F5_LOCAL_MULTI_DEVELOPMENT_PATH_HARNESS_PASS

or

F5_LOCAL_MULTI_DEVELOPMENT_PATH_HARNESS_FAIL

or

F5_LOCAL_MULTI_DEVELOPMENT_PATH_HARNESS_BLOCKED
