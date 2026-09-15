# Refresh Phase H baseline provenance and verify both EvalGating tests

TASK\_ID: ETL\-0915\-PHASE\-H\-BASELINE\-REFRESH01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
PREDECESSOR: ETL\-0915\-PHASE\-H\-WRITE\-RECONCILE01\.
SCOPE: Inspect and apply the prepared bookkeeping\-only baseline refresh, preserve accepted behavior and historical evidence, and verify the two existing EvalGating tests\.

The owner approves this bounded baseline refresh and its necessary local verification\. Complete inspection, preparation, focused checks, review, and application without requesting routine authorization again\. This approval does not accept new expected behavior, resolve the corpus coverage limitations, or authorize a release\.

All execution, responses, code, and artifacts must be in English\. Use text, filesystem, and DOM/accessibility interfaces only; no screenshots, video, OCR, or vision\.

## 1\. Recover the exact proposal and current state

Use the existing checkout:
`C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`

Read applicable local instructions and the accepted contract:
`C:\docs\ETL_Team_Test_Prep\references\09_AGILE_REPAIR_AND_VERIFICATION_CONTRACT.md`

Expected v1\.2: 23,684 bytes; SHA\-256:
`5387aa5c42940eceb2ffcd4d68d732ad3d57f1c69c2288c66bd0f32455e6f75b`\.

Resolve the predecessor through its published metadata under `C:\docs`\. Read its actual report, structured result, final review, and the proposal/candidate diff under its recorded `proposals` location\. Follow those records to the real canonical baseline, generator, input inventory, freshness checker, and both EvalGating test identities\. Do not invent paths from the screenshot\.

Reuse the relevant completed evidence:

- The approval\-test repair is applied\. Its retained suite observations were 39 passing/2 failing before repair, 41/0 after repair, 37/4 under the negative control, and 41/0 restored\. The control was sensitive but not exclusive to the two repaired tests\. Do not reopen that repair\.
- Phase H executed 9/9 scenarios with zero behavioral differences within corpus scope\. The reconciliation established applicability to the post\-repair snapshot with no relevant drift\.
- Both EvalGating failures encountered stale baseline provenance after 28 tracked inputs changed\. The telemetry\-free test stopped at that prerequisite, so its intended check remains unverified\.
- The baseline refresh is prepared but unapplied\. The reconciliation’s final disposition was VERIFIED\_WITH\_LIMITATIONS\.

Authenticate current relevant inputs once\. Same HEAD, dirty count, or version alone is insufficient\. Use actual machine records for identities; retain the previously disclosed byte\-count discrepancy as a report limitation rather than rewriting the closed repair report\.

Check ownership of the baseline surface and whether this refresh has already been applied\. Reuse your own existing claim where applicable; do not start a duplicate repair or take a live foreign owner’s files\. Establish one new task\-owned evidence root and preserve the original canonical baseline bytes before editing\.

## 2\. Prove that the proposed change is bookkeeping only

Inspect the complete candidate diff and relevant consumers of its changed fields\. Classify every field change before application\.

Allowed changes are the verified source/input identities and associated provenance metadata needed to bind the existing baseline to the evaluated current inputs\. Every new value must come from actual source bytes, matching retained evaluation evidence, or the repository’s real generation mechanism\. Distinguish the retained evaluation time from the time this refresh is performed\.

Preserve:

- Scenario identities, inventory, selection, and expected outputs\.
- Assertions, thresholds, comparison/normalization rules, metrics definitions, and failure meanings\.
- The tracked\-input set and freshness algorithm; do not omit inputs or ignore changed files to make the gate pass\.
- Existing coverage gaps and the distinction between structural parity and stronger semantic or runtime evidence\.

A metadata\-looking field that changes a behavioral expectation, threshold, case selection, or validation rule is not bookkeeping\. The intended change from stale to fresh through accurate input rebinding is authorized\. If the prepared patch includes a wider change, isolate the permitted refresh where possible and prepare a concrete decision for the remaining change\.

Confirm that the recorded 9\-scenario result still applies to the candidate’s effective evaluation inputs\. Reuse it when dependencies match\. If a relevant input differs, determine the impact and repeat only the affected evaluation or the necessary corpus run; do not stamp unevaluated inputs as qualified\. A new task ID or a new report timestamp does not require another full run\.

Use the prepared candidate and existing tools\. Do not regenerate a baseline by blindly accepting current output\. Keep the original baseline immutable as historical evidence and record the candidate’s exact identity separately\.

## 3\. Verify the two real EvalGating tests

Use the existing isolated lane and the repository’s actual test entrypoint, selecting both named tests or their smallest necessary containing suite\. Record selected and executed identities; an empty selection cannot pass unnoticed\.

Inspect command effects first\. Do not run `npm run eval:golden` in the recovery checkout: it deletes shared `out` and writes into `eval`\. Normal compile/test commands can also overwrite shared output and buildinfo\. Put required compilation, fixtures, generated evaluation output, and buildinfo under this task\. Reuse compiled output only when its relevant inputs match\.

Test the exact candidate baseline against a repository\-equivalent isolated tree containing the authenticated current inputs\. Record which baseline and source root the real checker actually opened\. Do not satisfy freshness against a fabricated or reduced inventory\.

Establish these outcomes:

|Check                   |Required observation                                                                                                                                                              |
|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Original stale condition|Reuse the authenticated failure if still comparable, or run the old baseline in isolation. The original provenance mismatch must remain distinguishable from a behavioral failure.|
|Baseline freshness test |The existing test reaches its actual freshness checks and passes against the verified candidate and current input set.                                                            |
|Telemetry-free test     |The existing telemetry-free setup is actually used; execution passes the freshness prerequisite and reaches the intended assertions. Report their real outcome.                   |

Do not infer telemetry independence from the test’s name or from fixing the first failure\. Inspect the existing setup/assertions and report precisely what they establish\. If the telemetry test reveals another defect, preserve the failure and identify its cause; do not weaken, skip, or rewrite the assertion to declare success\.

The existing stale\-baseline evidence may serve as the adverse control when its inputs and checker match\. Add a small isolated control only if necessary to establish that the real freshness gate remains effective\. Do not create a broad mutation campaign or modify product source for this refresh\.

Correct in\-scope metadata, staging, or invocation errors and recheck the affected result\. If a genuine product/test\-contract defect or a Git\-history requirement prevents a gate from passing, prepare the smallest separate repair/decision with evidence\. Do not mutate Git history, product code, or acceptance rules to satisfy it\.

## 4\. Review and apply the verified candidate

Apply the contract’s BOUNDARY review to the baseline’s acceptance implications\. Obtain a focused independent read\-only review of the full candidate diff, reused corpus applicability, real freshness and telemetry\-test evidence, and preserved limitations\. Reuse established collectors and source records; do not repeat the whole historical audit\.

Run reviewer checks only on isolated copies with fresh output destinations\. Never execute a helper whose fixed path overwrites frozen author results or closed predecessor evidence\. Disclose reviewer provenance and retain the final disposition outside the frozen reviewed files\.

Correct in\-scope findings, recheck affected evidence, and apply only the final reviewed bookkeeping candidate\. Immediately before application, verify that the canonical baseline still equals the saved preimage and that the evaluated inputs remain applicable\. Read back the applied bytes and confirm they equal the tested/reviewed candidate\. Record application separately from patch applicability\.

If a remaining failure does not invalidate the bookkeeping refresh, report the refresh and that failure separately\. If it invalidates the refresh’s basis, keep the candidate unapplied and provide the exact blocker\. Do not collapse a partial outcome into PASS\.

## 5\. Preserve scope and finish

Only the authenticated canonical baseline file&#40;s&#41; needed for this refresh and this task’s evidence may change\. Preserve product source, tests, runner registration, maintainer files, closed reports, sibling results, shared `out`, shared `.tsbuildinfo.test`, installed 0\.3\.160, and consumers\. No Git reset/clean/index/commit/branch changes, dependency installation, package/install, host launch, model request, live consumer write, approval click, external runtime call, or publication\.

Local isolated fixture/output writes are permitted\. Historical \.154/\.155/\.160 write allowances remain SPENT; expired quarantine is not renewed\.

Keep the corpus limitations open: structural parity, the empty validation denominator, no second\-turn create flow, zero prompt samples, and only one artifact\-producing scenario\. Refreshing provenance does not resolve them\. Do not confuse their reused decision labels with earlier unrelated D1\-D6 decisions\.

Preserve prior scoped 0\.3\.160 installed/write qualification as historical evidence\. This task adds no fresh natural\-language, installed\-consumer, or Databricks/ADF/DBFS qualification; do not describe the absence of new qualification as erasing earlier observed success\.

Deliver one concise `report.md`, one `result.json`, the final `task.diff`, the retained baseline preimage, and necessary raw check/review evidence\. Include:

- Exactly which fields changed and why they are bookkeeping only\.
- Applied baseline identity and its actual freshness outcome\.
- Each EvalGating test’s outcome, including whether telemetry assertions were reached\.
- The reused 9/9 corpus result and the identities supporting reuse; any new execution and its reason\.
- Preservation, review disposition, unresolved limitations, and one concrete next action\.

Record baseline application, corpus comparison, freshness, telemetry verification, and release status separately\. Do not claim RELEASE\_READY or wider owner acceptance\. Complete all available work, persist the result, release only this task’s ownership, and stop without launching another task\.
