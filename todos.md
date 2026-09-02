# Phase 1B.3F — Local Runner Sanitization Patch and Compile Verification

Continue in the current desktop VS Code GitHub Copilot Local Agent session.

This phase authorizes one narrow runner patch and one compile only.

Do not launch the Extension Development Host.
Do not press F5.
Do not run tests.
Do not invoke vscode.lm.invokeTool or etl_interpret_sttm.
Do not use Cloud, ETL Orchestrator, a worktree, wrapper, sidecar, or batch bridge.

## Fixed state

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Branch:

fix/workspace-write-completion-0.3.148

HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected initial Git status, exactly:

 M .github/templates/request.md
 M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Protected request.md SHA-256:

2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84

Expected initial runTest.ts SHA-256:

A7483429C0569CB62221E7FCD3650DD1BA29D64D67B366DD7E7F46ABA6D54BEC

Focused-test SHA-256:

8713EC3B3F2F75B06541F9B68AC4D9026CA0A17D052E07898EA12C5E12FAABCE

Phase 1B.3E already proved:

- Git, Node and npm return observable output and exit code 0;
- Node is v20.19.5;
- npm is 10.8.2;
- VS Code is 1.135.0;
- ELECTRON_RUN_AS_NODE, VSCODE_CLI,
  ELECTRON_NO_ATTACH_CONSOLE and NODE_OPTIONS are absent;
- npm run compile succeeds locally.

## Authorization

The only source file authorized for editing is:

src/test/runTest.ts

Generated output under out/** is authorized through exactly one compile.

Do not modify:

- .github/templates/request.md
- src/test/suite/sttmRealHostStructuredResult.test.ts
- src/test/suite/index.ts
- src/test/testPatterns.ts
- package.json
- package-lock.json
- tsconfig.json
- fixtures, contracts, documentation or QA files.

Do not stage, commit, stash, restore, reset, clean, switch, merge or rebase.

## Step 1 — Verify the two unresolved runner conditions

Before editing:

1. Verify the fixed branch, HEAD, status and hashes.
2. Read src/test/runTest.ts completely.
3. Inspect the installed @vscode/test-electron implementation used by this
   repository.
4. Confirm from code that @vscode/test-electron already derives/appends the
   Extension Development Path from the `extensionDevelopmentPath` option.
5. Confirm the current runner also places a redundant bare
   `extensionDevelopmentPath` positional value in `launchArgs`.
6. Confirm the isolated-run path currently has no invocation-scoped sanitation
   for:

   - ELECTRON_RUN_AS_NODE
   - VSCODE_CLI
   - ELECTRON_NO_ATTACH_CONSOLE

If these premises are not supported by the current files, make no edit and end:

F5_LOCAL_RUNNER_SANITIZATION_BLOCKED

Do not guess or broaden the change.

## Step 2 — Apply the narrow runner patch

Edit only src/test/runTest.ts.

Make only these behavioral changes:

1. Remove the redundant bare `extensionDevelopmentPath` positional value from
   `launchArgs`.

2. Preserve the existing top-level `extensionDevelopmentPath` option passed to
   `runTests`. It must continue identifying this repository as the extension
   development path exactly once.

3. In the existing opt-in isolated-dependency execution path only, immediately
   around the single `runTests(...)` invocation:

   - save whether each of these variables exists and its original value;
   - delete them from `process.env` before calling `runTests`:

     ELECTRON_RUN_AS_NODE
     VSCODE_CLI
     ELECTRON_NO_ATTACH_CONSOLE

   - restore their exact prior presence/value in a `finally` block after
     `runTests` completes or throws.

4. Do not log environment-variable values.

5. Do not persistently modify the user or machine environment.

6. Preserve all existing behavior when
   ETL_TEST_ENABLE_ISOLATED_DEPENDENCIES is not enabled.

7. Preserve:

   - exactly one reachable `runTests` invocation;
   - ETL_TEST_VSCODE_EXECUTABLE_PATH support;
   - the existing isolated user-data and extensions-directory behavior;
   - omission of `--disable-extensions`;
   - existing MOCHA_GREP and MOCHA_RESULT_FILE behavior;
   - the existing no-retry behavior.

Do not refactor unrelated code.

## Step 3 — Review before compiling

Before invoking npm:

1. Show the incremental change made in this phase.
2. Confirm only src/test/runTest.ts changed during this phase.
3. Confirm the patch contains:

   - removal of the redundant positional path;
   - scoped delete/restore logic;
   - a `finally` restoration path;
   - no additional `runTests` call;
   - no retry loop;
   - no `--disable-extensions`.

If this static review fails, do not compile and return BLOCKED.

## Step 4 — Compile exactly once

Record the UTC compile-start time.

Run exactly once from the repository root:

npm run compile

Require observable output and `$LASTEXITCODE` exactly 0.

Do not retry and do not invoke `tsc` separately.

## Step 5 — Post-compile verification

Require these artifacts to have been regenerated after the compile start:

- out/test/runTest.js
- out/test/suite/sttmRealHostStructuredResult.test.js
- out/test/suite/index.js
- out/tools/index.js
- out/extension.js

Verify in the compiled runner that:

- the redundant bare extension-development positional is absent;
- the existing extensionDevelopmentPath option remains;
- isolated execution deletes the three variables before runTests;
- restoration occurs through finally;
- exactly one runTests invocation remains;
- no retry was introduced;
- --disable-extensions remains absent.

Calculate and report:

- new src/test/runTest.ts SHA-256;
- new out/test/runTest.js SHA-256;
- hashes of the other four regenerated artifacts.

Finally revalidate:

- branch and HEAD unchanged;
- Git status remains exactly the original three lines;
- request.md hash unchanged;
- focused-test hash unchanged;
- no additional tracked or untracked file appeared.

Report the exact incremental runner change, compile exit code, artifact
freshness/hashes and integrity results.

Do not launch the Host or begin another phase.

End with exactly one marker:

F5_LOCAL_RUNNER_SANITIZATION_PASS

or

F5_LOCAL_RUNNER_SANITIZATION_BLOCKED
