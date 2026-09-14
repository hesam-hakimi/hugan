# Preserve validation codes and reconcile failure identities

TASK\_ID: ETL\-0914\-VALIDATION\-CODE\-AND\-FAILURE\-IDENTITY01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
PREDECESSOR: ETL\-0914\-COVERAGE\-REPLAY\-AND\-TIMING01\.
SCOPE: One narrow source/test/helper repair with focused independent review\.
DELIVERY\_BOUNDARY: Source changes only; no VSIX/package/install or installed\-runtime claim in this task\.
PRODUCT\_WRITE\_AUTHORIZATION\_BUDGET: 0\.
DIAGNOSTIC\_OR\_CONSUMER\_MODEL\_REQUESTS\_AND\_HOST\_LAUNCHES: 0\.

Execute on submission, preferably in the same engineering session\. All communication, code, tests and documents must be English\. Use text, DOM/accessibility and filesystem evidence only\. No screenshots, video, OCR or vision\. Complete the authorized inspection, minimal edits, focused checks and review without repeated routine approval requests\.

## 1\. Reuse the current state

Resolve the predecessor’s actual report, result, diff, relevant raw logs, helper and reviewer return under the established C:\\docs task location\. Resolve the worktree from those records; its last reported path was C:\\repos\\etl\-extension\\etl\_fw2\\recovery\-extension\-product\-0\.3\.147\. Read applicable repository instructions and the effective repair contract\. Use already\-read unchanged references; do not restart the project, maintainer integration, authentication diagnostics or the coverage audit\.

The owner’s latest report states:

- P1: all five suites were registered exactly once, normal headless discovery selected 153 files, and the compiled runUnitTests runner executed all five\. writeFlow remains unregistered\.
- P2: permanent recorded R1/R2 coverage uses the product’s real validators\. R1 reaches preview with the SQL include in CREATE and WHERE order\_status IS NOT NULL preserved through readIncludeSql\. R2 rejects without preview\. Its error code is asserted at the real validator, because the pipeline currently drops it\.
- A valid differing column alias with SQL reading the registered view was added as a positive control, taking the reported real\-validator tests from 28 to 29\.
- P3: the task\-owned t1\-run\-suites helper records monotonic duration, unknown values as null, raw exit/signal and separate allGreen/regressionsIntroduced fields\. No new framework or MOCHA\_RESULT\_FILE support was needed\.
- The focused seven\-suite comparison had zero failures on either side\. Full headless results were baseline 2438 passing / 26 failing and post 2577 passing / 24 failing\. Three post failure identity strings remained mispaired\. One apparent NEW result was a duration\-suffix pairing artifact; five failures were reported as lane\-input ENOENT errors for docs/\*\*\.
- The older \.159 report’s 16 failures are a different population; writeFlow did not execute in the new headless run\. Preserve both populations separately\.
- Independent review was reported VERIFIED after one low finding was corrected\. Ownership was released\. Worktree package\.json stayed 0\.3\.147, protected shared out and \.tsbuildinfo\.test were unchanged, the five applied maintainer files were intact, and dirty count changed from 76 to 77\.

Authenticate the actual current identities and ownership release before editing; the reported counts/version are not byte proofs\. If a successor already fixed either item, verify and reuse its result\. Do not overlap a conflicting writer\. Create one new task evidence directory and retain pre\-edit bytes; do not modify the closed predecessor’s evidence or helper in place\.

Library/sandbox paths are not Windows paths\. Use authentic local records\. If a required exact input is missing, use the established documentation staging transfer outside the worktree; block only its dependent action\. Do not reconstruct recorded inputs from photographed text\.

## 2\. Repair the loss of the existing structured error code

Inspect the complete relevant PreWriteValidationPipeline implementation and its actual issue types, transformation\-validator producer, writer consumer and result formatting\. The report locates the loss near the transformation\-issue fold around line 1071; this is a locator, not a guaranteed current line number\.

Confirm where an existing validator issue’s code is lost\. Preserve that code alongside the existing message when folding the issue into the pipeline’s structured result\. Use the existing optional field and result contract\. Preserve message text, severity, path/context, issue order and current blocking behavior\. Do not manufacture codes for uncoded issues, infer codes by parsing messages, change SQL/include acceptance or weaken validation\.

Carry the supported field to the existing composed structured\-result seam consumed by writeToWorkspace\. Trace what the public tool actually returns and report that scope precisely\. If this requires a new public protocol rather than preservation of an existing supported field, identify the concrete boundary and retain a failing reproduction instead of inventing a protocol in this task\. Complete the independent helper work while that decision is unresolved\.

Use the predecessor’s permanent byte\-pinned fixtures and real pipeline:

1. Extend R2 so SQL\_FIELD\_HOLDS\_ARTIFACT\_PATH is asserted on the real composed pipeline result, with rejection and no preview still asserted\. A validator\-only assertion or a mocked code at the writer is insufficient to close this remaining gap\. If the tool’s current structured contract exposes that result, assert it there as well\.
2. Keep R1’s actual preview, include CREATE classification and effective SQL filter assertions passing\.
3. Cover coded and uncoded issues through the affected fold, preserving uncoded behavior and existing message/severity/context\. Reuse existing cases where they establish this behavior\.
4. Retain the valid differing\-alias control and the existing Framework identity rules: table\.name when present, otherwise the sourceList key; alias renames a column and is not a view name\.

Do not stub the transformation validator or replace the prewrite pipeline with a lightweight implementation\. Existing VS Code surface stubs, a bounded DBFS probe substitute and disposable filesystem fixtures are suitable\. No live DBFS or consumer writes are needed\. An in\-memory/disposable test preview is not a reusable product approval\.

Use the existing unsupported\-path rejection as the behavioral starting point\. When practical, capture the new composed\-code assertion failing against matching pre\-edit source and passing after the fix; a compile/import failure is not behavioral red\. Do not rebuild historical \.155/\.156 versions or regenerate their proposals to get that evidence\.

## 3\. Repair the three failure\-identity pairings

Inspect the predecessor’s final extractor/comparator and the original full\-headless records\. Preserve its two rejected parser attempts as history\. Work in the established maintained helper source or a new task\-owned copy with a stable reusable location, retaining the inherited copy separately\. Do not build another runner/evidence framework\.

Prefer existing structured test events/results when available\. Otherwise make the smallest correction to the existing parser using the actual captured output\. Anchor identities in the available test file, full suite/test title and case discriminator; document any missing component\. Strip only demonstrated reporter decoration such as ANSI sequences and appended duration text\. Do not discard meaningful numbers, paths or parameter values in test names, collapse genuine duplicate cases, or pair failures by a global ordinal alone\.

Use the retained outputs to verify:

- All 24 post failures and all 26 baseline failures remain represented exactly once, with correct raw\-log references and counts matching the runner\.
- The three identified mispairings are corrected, including the apparent NEW duration\-suffix case\.
- Pass/failure/pending counts and native process exit/signal are preserved; allGreen remains false for these full runs\.
- Comparison accounts for actual selection changes\. Newly selected or unmatched cases are not automatically new product regressions\. Unknown correspondence remains explicit instead of becoming an empty regressionsIntroduced array\.

Use small meaningful regression checks derived from the observed bad pairings and a genuine distinct\-failure counterexample\. Confirm the parser cannot normalize two genuinely different failures into one\. Reuse the captured logs; do not repeat the full headless campaign just to parse it again\. If one identity cannot be established from retained records, rerun only the necessary affected case with existing result support, or state the exact remaining limitation\.

Keep the five reported ENOENT lane\-input failures visible with their actual evidence and classification\. They still count as failed executions\. Do not repair unrelated product tests, change assertions, add ignore rules or renew quarantine\. Keep the \.159 historical 16 failures, including nine writeFlow cases, separately attributed; do not merge them with the newer 24 or claim they ran here\. Quarantine expired after September 13 UTC and was not renewed\.

## 4\. Bound the edits and execution

Authorized edits are the identified pipeline fold, narrowly necessary existing type/consumer handling for that same optional field, the existing composed tests/test support, the established failure extractor/comparator and this task’s documentation\. Preserve the completed suite registrations, maintainer customization, SQL/include parsing and Framework view\-identity repair\.

Take the actual current dirty source as the baseline\. Use the existing b1\-lane/t1\-run\-suites mechanisms and focused runner interfaces\. Reuse matching baseline evidence only when source, tests, configuration, toolchain and compiled identities correspond\. Compile changed TypeScript into an isolated lane; do not hand\-edit generated JavaScript\.

Do not run naive compile/test:unit/pretest in the recovery worktree: they can delete shared out\. Do not run compile:test there because it writes shared out/build info\. Preserve shared out, \.tsbuildinfo\.test, package version, dependencies, Git state and all unrelated dirty files\. Do not reset, clean, commit, switch branches, upgrade tools or install dependencies\.

Run the affected pipeline/writer tests, the relevant identity controls and helper verification required by the actual delta\. Broaden only for a concrete dependency or required gate\. Fix task\-caused failures and repeat their affected checks in this same task, preserving each attempt\. No maintainer or consumer host launches, account/PAT/\.env changes, model requests, product writes, package/install, Databricks job execution, deployment or release\.

This task changes shipped source behavior, so the test\-only no\-package conclusion from the predecessor must not be transferred to eventual delivery\. This task intentionally ends at reviewed source: \.159 remains the last reported installed candidate and does not qualify the new code\. Record the changed shipped input and the minimum future candidate/installed check needed when the repair is delivered; do not launch that campaign here or label the source fix installed\.

## 5\. Review and handoff

Treat the structured\-result and failure\-classification changes as BOUNDARY changes\. Use one independent read\-only review of the combined delta, reusing prior validated contracts and evidence\. Require inspection of real code propagation, unchanged rejection behavior, composed assertions, distinct failure identity preservation, raw counts/exits and all remaining uncertainty\. Resolve in\-scope findings and obtain focused re\-review\. Preserve the full reviewer return; parent\-persisted output must use artifactAuthoredByReviewer: false\.

Deliver report\.md, result\.json and task\.diff with the necessary original logs and recoverable preimages\. Include:

- Exact baseline/post and changed\-file identities; retained protected state and unrelated dirty changes\.
- Where the error code now survives, what the public writer actually exposes, and the real composed R2 result\. Distinguish any narrower verified seam from public exposure\.
- Corrected baseline/post failure mapping, all raw totals, selection differences, unresolved cases and separate historical findings\.
- Focused test commands/outcomes, measured versus reused evidence, timing limits and the independent review’s final scoped disposition\.
- Zero product writes, diagnostic/consumer model requests, host launches, packages and installs in this task\.
- A concise next\-step assessment: whether the original \.json write path has a demonstrated remaining blocker, which concrete failed tests affect delivery, and the smallest later candidate/installed qualification needed\. Do not promote logging/classification defects into a claimed write blocker without tracing the consumer\.

Preserve historical item E, F\-ROOT\-1, ledger byte\-identity limits, the check\-to\-write race, runtime/DBFS limits and relevant unexercised branches\. Do not rewrite \.155 artifacts or spent ledgers\. Historical \.154/\.155 write allowances remain spent, and the \.159 preview is consumed/expired\. A future actual \.json write needs fresh bounded owner authorization and a fresh matching preview\.

Release ownership\. Report reviewed source completion separately from installed delivery, actual write success and release readiness\. Stop when this bounded task is sufficiently verified; do not start another audit or an unrelated baseline\-repair campaign\.
