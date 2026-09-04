ETL-0904-IMPL01 — Phase W Harness Repair

You are the normal local VS Code engineering Agent on Windows. You are not the ETL Orchestrator.

Owner authorization

The owner has approved a repo-defined minimal protected set of 11 paths for the focused 0.3.148 qualification harness.

This task authorizes source edits only to:

• src/test/runTest.ts
• src/test/suite/index.ts
• src/test/suite/sttmRealHostStructuredResult.test.ts

Do not edit any other file. If another file is required, stop with OWNER_SCOPE_EXPANSION_REQUIRED and explain why.

Do not compile, emit, test, launch a runner or Extension Host, package, install, clean, delete, restore, format unrelated files, commit, merge, push, bump a version, or release. Do not modify out/**, package.json, src/extension.ts, .github/templates/request.md, QA workbooks, evidence, profiles, consumer workspaces, the linked primary worktree, or Library files.

Mandatory preflight

Re-derive the live identity and exact Git status read-only. Expected baseline:

• Active worktree: C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
• Linked primary: C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2
• Branch: fix/workspace-write-completion-0.3.148
• HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
• Manifest version: 0.3.147
• Extension identifier: td-etl.databricks-etl-copilot
• Dirty paths before this task:
  •  M .github/templates/request.md
  •  M src/extension.ts
  •  M src/test/runTest.ts
  •  M src/test/suite/index.ts
  • ?? src/test/suite/sttmRealHostStructuredResult.test.ts

If identity, HEAD, or the pre-existing dirty inventory differs, stop without editing:

ETL_0904_IMPL01_RESULT: BLOCKED_BASELINE_DRIFT

Preserve all pre-existing work. 0.3.147 is immutable; the branch name does not establish that 0.3.148 exists.

Approved protected-set contract

Define the following canonical repository-relative POSIX paths exactly once, sorted ordinally:

1. out/core/solution/FileSystemSttmDocumentReader.js
2. out/core/sttm/SttmExcelWorkbookParser.js
3. out/extension.js
4. out/test/mochaResultGuard.js
5. out/test/runTest.js
6. out/test/suite/index.js
7. out/test/suite/sttmRealHostStructuredResult.test.js
8. out/test/testPatterns.js
9. out/tools/EtlReadOnlyToolService.js
10. out/tools/index.js
11. package.json

The authoritative policy is repo-defined. A future runner invocation must generate the manifest from this policy; it must not depend on an undocumented operator-supplied list.

Remove the magic protected-manifest cardinality 8 and derive all protected-set counts/comparisons from the canonical list or validated manifest length. Do not confuse this with the separate focused-suite Mocha oracle of 8 authored/evaluated tests; retain that independent expectation unless the executable test declarations prove otherwise.

Required repairs

1. Total parser-wrapper installation and restoration

• Patch the exact parser module instance consumed by the real product path.
• Scope installation as narrowly as possible around the real vscode.lm.invokeTool operation.
• Restore the original export in an unconditional finally, including assertion, invocation, and observation failures.
• Fail closed if the expected module/export identity is absent, already wrapped, replaced, or cannot be restored.
• Persist sufficient observations to prove installation, restoration, repository-output identity, and parser invocation cardinality.
• Do not treat vscode.lm.invokeTool count as proof of parser call count.

2. Exclusive focused-suite loading

• In focused qualification mode, add only the exact focused compiled suite file to Mocha.
• Do not glob/import all integration suites and then rely on mocha.grep; unselected files must have no import-time or top-level effects.
• Preserve ordinary non-focused test discovery outside focused mode.
• Reject missing, duplicate, ambiguous, or outside-root focused suite resolution.
• Keep suite identity and authored/evaluated counts machine-readable.

3. Evidence persistence on every exit path

• Establish evidence state before any preflight/gate that may throw.
• Use one outer error/finalization boundary covering manifest creation/validation, digest capture, Host launch, Mocha result handling, and post-exit verification.
• Attempt an atomic exclusive evidence write for success, product-candidate failure, infrastructure failure, and early setup failure.
• Never overwrite prior evidence. If evidence writing fails, preserve the original failure and add an explicit evidence-write failure classification.
• Do not allow a pre-run digest mismatch to produce no evidence.

4. Machine-readable classification and parent post-exit verification

• Separate at least product, infrastructure, and evidence-write failure classes.
• Do not convert incomplete evidence or infrastructure failure into product FAIL.
• After the Host/child exits, the parent runner must independently re-read the evidence and live protected files, recompute the manifest self-digest, canonical protected-files digest, and post-run hashes, and exit nonzero on any disagreement.
• Replace a declaration such as parentPostExitCheckRequired: true with an actually executed and evidenced parent check.
• Record whether the parent check completed, its result, and any mismatches.

5. Protected-set and digest integrity

• Generate the manifest from the approved 11-path policy after compilation in a future separately authorized task, never from historical hashes.
• Validate regular-file, canonical-inside-repository, no-symlink/reparse-point, no-duplicate, exact-order, and exact-policy membership invariants.
• Emit and compare all three states: manifest → pre-run, pre-run → post-run, and post-run → manifest.
• Preserve a reproducible manifest self-digest and a canonical digest over sorted path + sha256 records.
• Derive counts; do not introduce 8, 11, or any other duplicated cardinality literal outside the single canonical policy definition.

6. Correct and unmask the focused oracle

• Replace the stale Phase T structured-source assertion with the canonical structured-source contract.
• Preserve channel parity while respecting the deliberate structured-vs-Markdown display distinction.
• Keep the owner-required target entity in the target oracle: target_db.tgt_customers.customer_name (Markdown short target: tgt_customers.customer_name).
• Ensure the source assertion cannot mask the separate target assertion; report each comparison independently before aggregate verdict calculation.
• Do not repair product target-generation logic in this task; src/extension.ts is outside scope.

Engineering constraints

• Make the smallest coherent change within the three authorized files.
• Preserve LF/CRLF style and avoid formatting churn.
• Do not use destructive cleanup or touch tracked build-info.
• Do not accept historical hashes, screenshots, Phase T’s run-level marker, 8, or 39 as current qualification truth.
• The implementing Agent’s self-review is not final independent certification.

Required handoff

Without compiling or testing, provide:

1. verified pre-edit identity/status;
2. exact files and symbols changed;
3. mapping from each Phase W objection to its repair;
4. the canonical 11-path policy as implemented;
5. failure-classification and evidence schema changes;
6. proof from source inspection that focused loading is exclusive;
7. proof from source inspection that parser restoration is unconditional;
8. proof that target and source assertions are independently surfaced;
9. remaining risks and anything requiring owner scope expansion;
10. final diff/stat and exact post-edit status.

End with exactly:

ETL_0904_IMPL01_RESULT: IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW

AUTHORIZED_FILES_CHANGED: <exact list>

UNAUTHORIZED_FILES_CHANGED: 0

COMPILE_OR_TEST_EXECUTED: NO

RUNNER_OR_HOST_EXECUTED: NO

COMMIT_OR_PUSH_EXECUTED: NO

Stop. Do not propose or begin compile, test, Host qualification, packaging, installation, merge, version bump, or release. The next gate is a separately authorized independent source review.
