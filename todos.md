# ETL\-0904\-IMPL03 — Protected\-Policy Actual\-Path Micro\-Fix

This prompt supersedes `ETL-0904-IMPL02`, whose prescribed replacement path was disproven\. You are the normal local VS Code engineering Agent on Windows\. You are **not** the ETL Orchestrator\.

## Owner authorization

The owner approves one semantic edit in exactly one file:

- `src/test/runTest.ts`

Replace protected\-policy entry 4:

`out/test/mochaResultGuard.js`

with the verified compiler\-output path:

`out/test/harness/mochaResultGuard.js`

Do not alter any other logic, path, comment, formatting, identifier, test oracle, or file\.

## Prohibited actions

Do **not** compile, emit, test, launch a runner or Extension Host, package, install, clean, delete, restore, commit, push, merge, bump a version, or release\. Do not modify `out/**`, `package.json`, product source, QA/evidence/profile/consumer\-workspace locations, the linked primary worktree, or Library files\.

## Mandatory preflight

Re\-derive the live identity and Git status read\-only\. Expected identity:

- Worktree: `C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`
- Branch: `fix/workspace-write-completion-0.3.148`
- HEAD: `45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19`
- Manifest version: `0.3.147`
- Extension identifier: `td-etl.databricks-etl-copilot`
- Dirty inventory:
  - ` M .github/templates/request.md`
  - ` M src/extension.ts`
  - ` M src/test/runTest.ts`
  - ` M src/test/suite/index.ts`
  - `?? src/test/suite/sttmRealHostStructuredResult.test.ts`

Before editing, reconfirm without compilation:

- source: `src/test/harness/mochaResultGuard.ts`;
- TypeScript mapping: `rootDir: src` and `outDir: out`;
- therefore emitted path: `out/test/harness/mochaResultGuard.js`;
- existing compiled `.js`, `.d.ts`, and `.js.map` artifacts corroborate that path;
- neither `out/test/mochaResultGuard.js` nor `out/mochaResultGuard.js` is producible by the current mapping\.

If identity/status differs or any mapping fact is not confirmed, make no edit and stop with:

`ETL_0904_IMPL03_RESULT: BLOCKED_BASELINE_OR_PATH_DRIFT`

## Required edit and invariants

Make only the single path substitution in the canonical `PROTECTED_POLICY_PATHS` definition\.

The final strictly ordinally sorted policy must be exactly:

1. `out/core/solution/FileSystemSttmDocumentReader.js`
2. `out/core/sttm/SttmExcelWorkbookParser.js`
3. `out/extension.js`
4. `out/test/harness/mochaResultGuard.js`
5. `out/test/runTest.js`
6. `out/test/suite/index.js`
7. `out/test/suite/sttmRealHostStructuredResult.test.js`
8. `out/test/testPatterns.js`
9. `out/tools/EtlReadOnlyToolService.js`
10. `out/tools/index.js`
11. `package.json`

Keep the set repo\-defined\. All protected\-set cardinalities must remain derived from `PROTECTED_POLICY_PATHS.length`; do not add a duplicate `11` literal\. Do not alter the separate focused\-suite expectation of 8 authored/evaluated tests\.

## Allowed verification

Use source inspection and read\-only Git/diff/status/hash checks only\. Verify that:

- `out/test/harness/mochaResultGuard.js` occurs exactly once in the policy;
- `out/test/mochaResultGuard.js` occurs zero times in the policy;
- `out/mochaResultGuard.js` occurs zero times in the policy;
- the policy remains strictly ordinally sorted;
- only `src/test/runTest.ts` changed relative to the immediate pre\-task state;
- the only new semantic delta is this one path substitution;
- the other four dirty paths remain byte\-identical to their immediate pre\-task state\.

Language\-service diagnostics may be reported if already available, but they are not a no\-emit TypeScript check\. Do not invoke a compiler or test command\.

## Required handoff

Return:

1. verified identity and pre\-edit status;
2. exact source/configuration/output\-path proof;
3. exact before/after line;
4. final sorted 11\-path policy;
5. immediate pre\-task versus post\-task diff/hash guard;
6. exact final Git status;
7. confirmation that no compile, test, runner, Host, commit, or push occurred\.

End with exactly:

`ETL_0904_IMPL03_RESULT: MICROFIX_APPLIED_AWAITING_INDEPENDENT_REVIEW`

`AUTHORIZED_FILES_CHANGED: src/test/runTest.ts`

`UNAUTHORIZED_FILES_CHANGED: 0`

`COMPILE_OR_TEST_EXECUTED: NO`

`RUNNER_OR_HOST_EXECUTED: NO`

`COMMIT_OR_PUSH_EXECUTED: NO`

Stop\. Do not begin independent review, compilation, qualification, packaging, installation, merge, version bump, or release\.
