ETL-0904-IMPL02 — Protected-Policy Path Micro-Fix

You are the normal local VS Code engineering Agent on Windows. You are not the ETL Orchestrator.

Authorization boundary

This task authorizes exactly one semantic edit in exactly one file:

• src/test/runTest.ts

Correct protected-policy entry 4 from:

out/test/mochaResultGuard.js

to the actual compiler-output path:

out/mochaResultGuard.js

Do not change any other logic, path, formatting, comment, identifier, test oracle, or file.

Do not compile, emit, test, launch a runner or Extension Host, package, install, clean, delete, restore, commit, push, merge, bump a version, or release. Do not modify out/**, package.json, product source, QA/evidence/profile/consumer-workspace locations, the linked primary worktree, or Library files.

Mandatory preflight

Re-derive the live worktree, branch, HEAD, manifest version, extension identifier, and exact Git status read-only.

Expected identity:

• Worktree: C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
• Branch: fix/workspace-write-completion-0.3.148
• HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
• Manifest version: 0.3.147
• Extension identifier: td-etl.databricks-etl-copilot
• Dirty inventory remains exactly:
  •  M .github/templates/request.md
  •  M src/extension.ts
  •  M src/test/runTest.ts
  •  M src/test/suite/index.ts
  • ?? src/test/suite/sttmRealHostStructuredResult.test.ts

Confirm from source layout and TypeScript configuration—without compiling—that mochaResultGuard.ts emits to out/mochaResultGuard.js, and that out/test/mochaResultGuard.js cannot be produced by the repository’s configured mapping.

If identity/status differs or the output-path mapping is not proven exactly, make no edit and stop with:

ETL_0904_IMPL02_RESULT: BLOCKED_OUTPUT_PATH_UNCONFIRMED

Required edit

In the single canonical PROTECTED_POLICY_PATHS definition introduced by ETL-0904-IMPL01, replace only the incorrect entry.

After the edit, the canonical ordinally sorted 11-path policy must be exactly:

1. out/core/solution/FileSystemSttmDocumentReader.js
2. out/core/sttm/SttmExcelWorkbookParser.js
3. out/extension.js
4. out/mochaResultGuard.js
5. out/test/runTest.js
6. out/test/suite/index.js
7. out/test/suite/sttmRealHostStructuredResult.test.js
8. out/test/testPatterns.js
9. out/tools/EtlReadOnlyToolService.js
10. out/tools/index.js
11. package.json

The set remains repo-defined. All cardinality checks must remain derived from PROTECTED_POLICY_PATHS.length; do not add a duplicated 11 literal. Do not alter the separate focused-suite expectation of 8 authored/evaluated tests.

Verification allowed in this task

Use source inspection and read-only Git/diff/status checks only. Verify:

• out/test/mochaResultGuard.js has zero remaining occurrences in the protected policy;
• out/mochaResultGuard.js occurs exactly once in that policy;
• the policy remains strictly ordinally sorted;
• only src/test/runTest.ts changed relative to the immediate pre-task state;
• the only new semantic delta is the one path substitution;
• the other four dirty paths are byte-identical to their pre-task state.

Language-service diagnostics may be reported if already available, but they are not a TypeScript check. Do not invoke a compiler or test command.

Required handoff

Return:

1. verified identity and pre-edit status;
2. source/configuration proof of the actual output path;
3. exact before/after line;
4. the final sorted 11-path policy;
5. immediate pre-task versus post-task diff guard;
6. exact final Git status;
7. confirmation that no compile/test/runner/Host/commit/push occurred.

End with exactly:

ETL_0904_IMPL02_RESULT: MICROFIX_APPLIED_AWAITING_INDEPENDENT_REVIEW

AUTHORIZED_FILES_CHANGED: src/test/runTest.ts

UNAUTHORIZED_FILES_CHANGED: 0

COMPILE_OR_TEST_EXECUTED: NO

RUNNER_OR_HOST_EXECUTED: NO

COMMIT_OR_PUSH_EXECUTED: NO

Stop. Do not begin independent review, compilation, qualification, packaging, installation, merge, version bump, or release.
