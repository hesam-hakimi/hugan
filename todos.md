# ETL\-0904\-REVIEW01 — Independent Phase W Source Review

Run this prompt in a **fresh VS Code Agent chat with a reviewer that did not implement ****`ETL-0904-IMPL01`**** or ****`ETL-0904-IMPL03`**\. Prefer a strong review model such as Claude Opus 5\. This is the normal local engineering environment, not the ETL Orchestrator\.

## Authorization boundary

This task authorizes **read\-only independent source review only**\.

Do not edit, create, delete, restore, format, compile, emit, type\-check, test, launch a runner or Extension Host, package, install, clean, commit, push, merge, bump a version, or release\. Do not click or use Undo to alter the implementation\. Do not use Bypass Permissions to expand scope\.

If the implementation is still presented as an unresolved `Keep`/`Undo` editor checkpoint, or if you are the same Agent/session that implemented it, stop with:

`ETL_0904_REVIEW01_RESULT: BLOCKED_NOT_INDEPENDENT_OR_PENDING_CHECKPOINT`

Do not treat the implementing Agent’s report, language\-service diagnostics, comments, screenshots, or stated invariants as proof\. Re\-derive every conclusion from the live files and complete diff\.

## Expected live identity

- Active worktree: `C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`
- Linked primary worktree: `C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2`
- Branch: `fix/workspace-write-completion-0.3.148`
- HEAD: `45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19`
- Manifest version: `0.3.147`
- Extension identifier: `td-etl.databricks-etl-copilot`
- Expected dirty paths:
  - ` M .github/templates/request.md`
  - ` M src/extension.ts`
  - ` M src/test/runTest.ts`
  - ` M src/test/suite/index.ts`
  - `?? src/test/suite/sttmRealHostStructuredResult.test.ts`

Re\-derive all values read\-only before reviewing\. If identity, HEAD, or dirty\-path inventory differs, stop with:

`ETL_0904_REVIEW01_RESULT: BLOCKED_BASELINE_DRIFT`

The branch name does not prove that `0.3.148` exists\. `0.3.147` remains immutable\.

## Required review scope

Read completely:

- the full diff of every tracked dirty file;
- the full untracked `src/test/suite/sttmRealHostStructuredResult.test.ts`;
- the complete current contents of the three harness files;
- every directly relevant imported helper, type, package script, and TypeScript configuration needed to validate the implementation;
- existing compiled files only as stale identity/layout evidence—never execute them\.

Do not sample only changed snippets\. `src/test/runTest.ts` contains a large change and must be reviewed end\-to\-end, including all success, throw, cleanup, and post\-exit branches\.

Separate:

- pre\-existing control\-plane edit: `.github/templates/request.md`;
- pre\-existing product edit: `src/extension.ts`;
- Phase W harness edits in the three test files\.

Verify that the harness changes neither absorb nor conceal unrelated product/control\-plane changes\.

## Independent review checklist

### A\. Canonical protected\-set contract

Verify that the policy is defined once and contains exactly these ordinally sorted repo\-relative paths:

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

Confirm source/configuration mapping for every compiled path\. Verify exact membership, canonical containment, regular\-file/no\-symlink\-or\-reparse\-point checks, duplicate rejection, ordinal order, and derived cardinality\. Reject any hidden `8`, `11`, `39`, historical hash, or operator\-supplied count used as protected\-set truth\. Keep the separate focused\-suite 8\-test oracle conceptually distinct\.

Verify that manifest generation uses the approved repo\-defined policy and the compiled artifact that will actually be qualified, with no undocumented operator list or stale hash gate\.

### B\. Manifest, digest, and evidence integrity

Trace the complete lifecycle in order:

- isolation\-root resolution and freshness;
- manifest creation and exclusive write;
- manifest self\-digest and canonical `path + sha256` files digest;
- pre\-run file capture;
- Host/child execution boundary;
- post\-run capture;
- evidence persistence;
- parent post\-exit re\-read and independent recomputation\.

Verify all three comparisons exist and are fail\-closed: manifest → pre\-run, pre\-run → post\-run, and post\-run → manifest\. Check that serialization/order rules allow the parent to reproduce every digest exactly\.

Prove that an early failure at QA\-root resolution, manifest generation/validation, freshness, digest capture, Host launch, Mocha handling, or post\-exit verification still produces the strongest possible non\-overwriting evidence\. Identify any path where evidence disappears, overwrites prior evidence, masks the original error, or incorrectly exits zero\.

Check that evidence\-file creation is compatible with the isolation\-root freshness invariant and that no repository, QA workbook, profile, installed extension, consumer workspace, or control\-plane path is mutated\.

### C\. Failure classification and formal verdicts

Verify machine\-readable separation of `product`, `infrastructure`, and `evidence-write` failures, including multiple simultaneous failures and precedence\.

A product `FAIL` is valid only when the Host reached the intended product boundary, the oracle was valid, infrastructure completed, and retained evidence is complete\. Missing/incomplete evidence, manifest disagreement, Host/setup failure, or failed parent verification must remain `BLOCKED`, not `PASS` or product `FAIL`\.

Ensure a stale oracle cannot be reclassified as a product defect and Phase T’s historical run\-level `FAIL` marker is not reused as current truth\.

### D\. Executed parent post\-exit verification

Confirm the parent verifier is actually invoked after every child/Host exit or throw—not merely declared in evidence\. It must independently re\-read retained evidence and live protected files, recompute digests, record completion/result/mismatches, and force nonzero exit on disagreement\.

Check exception precedence: the original product/infrastructure failure must remain observable even if parent verification or evidence writing also fails\.

### E\. Exclusive focused\-suite loading

Trace the focused\-suite variable from parent setup through child environment to the Mocha loader\. Confirm that focused mode resolves one exact regular file inside the compiled test root and calls `mocha.addFile` exactly once\.

No other integration suite may be globbed, imported, registered, or execute top\-level side effects in focused mode\. `mocha.grep` alone is insufficient\. Missing, duplicate, ambiguous, outside\-root, symlink, and reparse\-point selections must fail closed\. Ordinary non\-focused discovery must remain unchanged\.

Confirm `loadedFiles`, `loadedFileCount`, `authoredSuiteTitles`, and `authoredTests` are independently derived and cannot merely echo expected constants\.

### F\. Parser observer installation/restoration

Verify that the wrapper patches the exact unbundled module instance used by the real product path\. Installation must occur immediately before the single real `vscode.lm.invokeTool` call; restoration must be the first unconditional action in `finally` and must verify restored identity\.

Review all failure paths: unresolved module, wrong export, already wrapped export, installation not taking effect, invocation rejection, assertion failure, observation failure, and restoration failure\. None may leave the parser wrapped or hide the primary failure\.

Confirm that `vscode.lm.invokeTool` count and parser invocation cardinality are separate directly recorded observations\. Explain the Test\-mode unbundled assumption and why this does not qualify a later bundled/installed artifact\.

### G\. Oracle correctness and assertion independence

Verify from executable contract/source—not prior prose—that:

- the structured source uses the canonical structured source identity;
- Markdown uses its intended display form;
- structured and Markdown channels express the same semantic mapping;
- the structured target includes `target_db.tgt_customers.customer_name`;
- the Markdown short target is `tgt_customers.customer_name`;
- source and target comparisons are recorded under distinct identities before aggregate failure;
- a source mismatch cannot mask the target result;
- the owner\-required target assertion is actually evaluated\.

Reconcile the 8 authored/evaluated tests with the reported comparison cardinality &#40;currently 47&#41; without equating those two quantities\. Detect duplicate, missing, expected\-only, or dynamically unexecuted comparisons\.

### H\. Containment and environment boundaries

Verify Windows canonical\-path, case\-folding, junction, symlink, and reparse\-point behavior for repository root, isolation root, QA root, suite path, manifest, and evidence paths\.

Confirm repository ↔ isolation, QA ↔ isolation, and repository ↔ QA disjointness where required\. If repository ↔ QA disjointness remains unproved, classify its actual risk and whether it blocks the next no\-emit type\-check or only the future Host run\.

Confirm no consumer writes, no `.github/**` test writes, and no reliance on Bypass Permissions\.

### I\. Maintainability and compile risk

Review the large `runTest.ts` delta for duplicated state, unreachable branches, inconsistent types, partial initialization, unsafe casts, incorrect async/finally behavior, non\-deterministic ordering, JSON/schema incompatibility, path normalization defects, accidental line\-ending churn, and error swallowing\.

Check every renamed/removed field against all in\-repository readers and writers\. Identify anything likely to fail TypeScript no\-emit checking, compilation, or runtime, but do not execute those checks\.

State explicitly that source review does not prove type correctness, compiled output freshness, Test\-mode behavior, package contents, installed activation, or release readiness\. Note that a future compile will incorporate the current uncommitted product and harness source, so its exact scope must be authorized separately\.

## Finding and verdict rules

Report findings first, ordered `BLOCKER`, `MAJOR`, then `MINOR`\. Every finding must include:

- exact file and re\-derived line/symbol;
- violated invariant;
- concrete failure scenario;
- smallest safe repair direction;
- whether it blocks no\-emit type\-check, compile, Host qualification, packaging, or installed Runtime QA\.

Use exactly one formal verdict:

- `ACCEPTABLE`: every checklist item was independently verified and no `BLOCKER` or `MAJOR` remains;
- `CHANGES_REQUIRED`: source defects or missing invariants require implementation changes;
- `BLOCKED`: independence, baseline, complete\-file access, or evidence needed for review was unavailable\.

Silence or missing evidence is never `ACCEPTABLE`\.

## Required output

Return in this order:

1. reviewer independence and verified live identity/status;
2. complete review scope and diff inventory;
3. findings by severity;
4. checklist A–I with `VERIFIED`, `REPORTED`, `STALE`, or `UNKNOWN` for each material claim;
5. exact 11\-path policy verdict;
6. Phase W objection\-to\-repair verdict;
7. oracle/channel/target verdict;
8. containment and future compile\-risk verdict;
9. formal overall verdict and justification;
10. if `CHANGES_REQUIRED`, a minimal bounded repair list only—do not edit;
11. if `ACCEPTABLE`, state that the next gate is a separately authorized no\-emit TypeScript check, not compilation\.

End with exactly one of:

`ETL_0904_REVIEW01_RESULT: ACCEPTABLE`

`ETL_0904_REVIEW01_RESULT: CHANGES_REQUIRED`

`ETL_0904_REVIEW01_RESULT: BLOCKED`

Then end with all of:

`INDEPENDENT_REVIEWER: YES`

`FILES_CHANGED: 0`

`TYPECHECK_COMPILE_OR_TEST_EXECUTED: NO`

`RUNNER_OR_HOST_EXECUTED: NO`

`COMMIT_OR_PUSH_EXECUTED: NO`

Stop\. Do not repair, type\-check, compile, qualify, package, install, merge, version\-bump, or release\.
