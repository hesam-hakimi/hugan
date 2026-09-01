Structured Result Boundary Audit — Read-Only Diagnosis Only

Environment:

- Run in the normal source-repository VS Code window, not inside the
  Extension Development Host.
- Repository:
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
- Expected branch:
  fix/workspace-write-completion-0.3.148
- Expected HEAD:
  45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Objective:

Determine exactly why the F5 ETL Orchestrator received the complete rendered
Markdown STTM report but could not observe a structured-data result channel.

This is diagnosis only. Do not implement a fix.

Validated runtime evidence:

- `etl_interpret_sttm` was invoked exactly once.
- Workbook containment passed.
- Files discovered/read/blocked: 1/1/0.
- Active mappings: 8.
- Audit findings: 6.
- Mapping `FM_F01417B0_00002` was present, active, and first.
- Markdown output was complete.
- The chat host offloaded the large result into a session-resource content file.
- That file exposed only rendered Markdown.
- No structured data part was observable by the Orchestrator.
- Runtime marker:
  `F5_STTM_INTERPRETATION_BLOCKED`

Do not rerun `etl_interpret_sttm`. Do not repeat the F5 workflow.

Phase 0 — Repository identity and protection

1. Verify repository root, branch, and HEAD.
2. Record `git status --short --untracked-files=all`.
3. Preserve every pre-existing modification exactly.
4. Use committed HEAD content as the audit baseline.
5. If an implementation file involved in this audit differs from HEAD, stop and
   report the exact path and diff. Do not restore or modify it.

If bare `git`, `node`, or `npm` fails because PATHEXT is corrupted, set this only
inside each required PowerShell invocation:

$env:PATHEXT = '.COM;.EXE;.BAT;.CMD'

Do not persist that environment change.

Audit the complete committed runtime path:

1. Trace registration of `etl_interpret_sttm`.
2. Trace its `execute()` result type and actual returned object.
3. Trace `BaseReadOnlyTool.invoke()` in `src/tools/index.ts`.
4. Trace `createToolResult(...)`.
5. Trace construction of `vscode.LanguageModelToolResult`.
6. Inspect the compiled `out/**` implementation actually loaded by F5 and
   reconcile it against the TypeScript source.
7. Determine:
   - whether the raw service response contains distinct structured and Markdown
     representations;
   - the exact number and types of content parts emitted by `createToolResult`;
   - whether the extension emits a structured part at all;
   - whether the installed VS Code API supports the intended structured part;
   - whether the Chat host’s large-result offload drops, hides, or converts
     non-text parts;
   - whether the current automated tests verify only the service response or the
     real registered public-tool boundary.

Inspect existing relevant tests, but do not add or modify tests and do not run the
full test suite, Eval Golden, compilation, packaging, VSIX, F5, or external calls.

Classify the root cause as exactly one of:

A. EXTENSION_RESULT_CONSTRUCTION_DEFECT
B. PUBLIC_TOOL_BOUNDARY_TEST_GAP
C. VS_CODE_CHAT_HOST_OFFLOAD_LIMITATION
D. QA_HARNESS_OBSERVABILITY_GAP
E. MULTIPLE_CAUSES
F. EVIDENCE_INSUFFICIENT

Required report:

- Repository identity and protected worktree inventory.
- Source-to-compiled call path with exact files and symbols.
- Raw service response shape.
- Public `LanguageModelToolResult` content-part shape.
- Supported VS Code API content-part types.
- Existing test coverage and exact missing boundary.
- Root-cause classification.
- Whether product code requires repair.
- Whether only the QA harness/evidence method requires repair.
- Smallest safe next implementation or characterization-test task.
- Explicit confirmation that nothing was modified.

Do not weaken the dual-channel success criterion and do not infer structured
output from Markdown.

End with exactly one marker:

STRUCTURED_RESULT_BOUNDARY_AUDIT_COMPLETE

or

STRUCTURED_RESULT_BOUNDARY_AUDIT_BLOCKED
