Phase 1B.2 — One-Shot Isolated Dependency-Provisioned Real-Host Rerun

Environment: the same local Windows VS Code session.
Agent: Claude Opus 5.
Repository:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
Branch:
fix/workspace-write-completion-0.3.148
Expected HEAD:
45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Objective:
Unblock the Phase 1B real-host characterization by provisioning only the declared
github.copilot-chat dependency into a fresh isolated extension directory, then perform
exactly ONE additional real VS Code Extension Host launch.

Authorization:
- Read-only preflight and temporary staging outside the repository and QA workspace.
- One narrowly scoped test-harness change in src/test/runTest.ts only if required to omit
  --disable-extensions under an explicit opt-in environment variable.
- Exactly one additional real Extension Host launch.
- No product-code changes.

Hard boundaries:
1. Preserve .github/templates/request.md byte-for-byte:
   SHA-256:
   2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84
2. Preserve all current dirty and untracked work.
3. Never checkout, restore, reset, clean, stash, stage, commit, or push.
4. Do not modify package.json, lockfiles, production code, fixtures, contracts,
   src/test/testPatterns.ts, or existing tests.
5. Do not use the real user extensions directory directly during the test.
6. Do not download or install anything from Marketplace.
7. Do not write to the QA workspace.
8. No model, Chat, Orchestrator, render, approval, write, publish, or pipeline invocation.
9. No full suite, Eval Golden, packaging, or VSIX build.
10. Never retry the Extension Host launch.

Preflight:
- Reverify repository root, branch, HEAD, package version 0.3.147, Code.exe identity/version,
  repository status, production-output hashes, and complete QA inventory/hashes.
- Expected current repository changes are:
  M  .github/templates/request.md
  M  src/test/runTest.ts
  ?? src/test/suite/sttmRealHostStructuredResult.test.ts
- Stop before staging or launching if any authoritative value differs.

Dependency staging:
- Locate the already-installed local github.copilot-chat extension.
- Validate its publisher/name ID, version, VS Code engine compatibility, package.json, and hashes.
- Recursively identify all required non-built-in extensionDependencies.
- Copy only that validated dependency closure into a newly created temporary:
  <isolation-root>\extensions
- Create a fresh:
  <isolation-root>\user-data
- Do not point --extensions-dir at the real user extensions directory.
- If a complete compatible dependency closure is unavailable, do not launch and report:
  F5_REAL_HOST_DEPENDENCY_PREREQUISITE_BLOCKED

Launch configuration:
- Continue using the authoritative Code.exe through ETL_TEST_VSCODE_EXECUTABLE_PATH.
- Use the fresh isolated --user-data-dir and preseeded isolated --extensions-dir.
- Omit global --disable-extensions for this one launch because the isolated extensions
  directory is the allowlist.
- If src/test/runTest.ts cannot currently support that configuration, add only a narrow
  explicit opt-in such as ETL_TEST_ENABLE_ISOLATED_DEPENDENCIES=1.
- Default runner behaviour must remain unchanged when the opt-in is absent.
- Compile before launch and preserve generated incremental-cache bytes exactly.

Execution:
- Run only the Phase 1B real-host structured-result characterization suite.
- Launch the Extension Host exactly once.
- Prove:
  - real host identity;
  - authoritative development-extension path;
  - github.copilot-chat dependency resolution;
  - target extension activation;
  - etl_interpret_sttm registration;
  - exactly one vscode.lm.invokeTool invocation.

Assertions:
- Capture the raw LanguageModelToolResult.
- Verify part count and order, constructor/API types, TextPart content, DataPart MIME,
  Uint8Array status and byte length, UTF-8 decoding, JSON parsing, deterministic payload
  fields, and Markdown/JSON parity.
- Reverify QA inventory/hashes and repository state afterward.

Classification:
- PASS only if invocation occurs and every assertion and guard passes.
- FAIL only if invocation returns a result and an assertion mismatches.
- BLOCKED if activation, registration, or invocation is not reached.
- Never perform a second launch.

End with exactly one marker:
F5_REAL_HOST_STRUCTURED_RESULT_PASS
F5_REAL_HOST_STRUCTURED_RESULT_FAIL
F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED
