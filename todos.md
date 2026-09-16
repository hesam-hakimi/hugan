# Make the Phase H telemetry test discriminating

TASK\_ID: ETL\-0916\-PHASE\-H\-TELEMETRY\-TEST\-REPAIR01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
PREDECESSOR: ETL\-0915\-PHASE\-H\-BASELINE\-REFRESH01\.
SCOPE: Strengthen the existing telemetry\-independence regression and perform any directly necessary baseline\-provenance upkeep in the same task\.

Owner submission of this brief authorizes the bounded test repair, focused verification, independent review, application, and conditional bookkeeping refresh described below\. Complete routine implementation and in\-scope corrections without another approval request\. Use English for all execution, responses, code, tests, and reports\. Use text, filesystem, and DOM/accessibility interfaces only; no screenshots, video, OCR, or vision\.

## 1\. Reuse the completed work

Checkout:
`C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`

Read applicable local instructions and:
`C:\docs\ETL_Team_Test_Prep\references\09_AGILE_REPAIR_AND_VERIFICATION_CONTRACT.md`

Expected contract v1\.2: 23,684 bytes; SHA\-256:
`5387aa5c42940eceb2ffcd4d68d732ad3d57f1c69c2288c66bd0f32455e6f75b`\.

Resolve the predecessor’s actual report, result, final review, and prepared telemetry follow\-up through published task metadata under `C:\docs`\. Reuse its named source/test locations and prepared proposal; do not repeat the Phase H investigation or reconstruct paths from photographs\.

The reported state is:

- Baseline refresh APPLIED to two files; current checkout freshness PASS\.
- The 9/9 corpus result with zero behavioral differences was reused with matching relevant inputs\.
- EvalGating: historical baseline 5 passing/2 failing; refreshed baseline 7/0\.
- The telemetry test reaches its assertions but is vacuous on its named subject\. Both baselines already contain zero prompt samples and estimated cost, making the override ineffective\. Its issue\-absence assertions do not discriminate the intended behavior\.
- Review: VERIFIED\_WITH\_LIMITATIONS; no blocking or material findings\. Product source was unchanged\.

Check current relevant identities and ownership once\. Preserve the completed approval\-test repair and closed evidence\. Resume only your own authenticated task; do not duplicate an active repair or take a foreign owner’s surface\. Create one task\-owned evidence root and preserve preimages of every file this task will edit\.

## 2\. Repair the existing test against the real contract

Read the actual telemetry test, gate, report schema, and accepted intent\. Recover the exact decision boundary the test is supposed to protect\. Do not introduce a requirement that all product behavior must ignore telemetry, or add telemetry behavior to production merely to make a test meaningful\.

Use valid deterministic fixtures with genuinely different values for `totalPromptSamples` and `estimatedCostUnits`\. Include nonzero values and zero values; use absent values only if the accepted schema permits absence\. Derive valid domains from the real schema\. Keep behavior/quality inputs, source provenance, and freshness prerequisites equivalent across the comparison\.

Invoke the actual gate through the existing test mechanism\. Assert equality of its complete decision\-relevant outcome, including the applicable reasons/issues, across telemetry variations\. Permit observational fields to differ only where the contract explicitly allows it\. Do not arbitrarily normalize away differences or limit the assertion to the absence of words such as “telemetry” or “cost”\.

Exercise the meaningful combinations needed to show that each field cannot accidentally influence the intended decision; avoid a large combinatorial test matrix\. Retain other existing assertions that protect valid behavior\. Preserve the original regression’s identity where practical, explaining any necessary renaming or parameter expansion\.

Change only the relevant test and strictly necessary test fixtures/helpers\. Use typed existing interfaces; do not hide mismatches with loose casts or ignored type errors\. Do not change product source, thresholds, gate rules, corpus membership, or runner registration\.

If the accepted contract is ambiguous, complete the concrete test proposal and identify the exact competing expectations\. If the strengthened assertion exposes a genuine product defect, retain that failure and prepare a bounded product follow\-up; do not weaken the test to accept it\.

## 3\. Show that the test can catch the intended regression

Use the established isolated lane and real focused test entrypoint\. Record selected and executed test identities, assertion outcomes, and raw exits\. Compile changed TypeScript into task\-owned output as necessary\. Keep shared `out` and `.tsbuildinfo.test` unchanged\.

Establish:

1. The repaired tests pass against the unmodified product, with genuinely different telemetry fixtures\.
2. A small reversible mutation in an isolated copy of the actual gate introduces a dependency on one of those telemetry values; the repaired regression fails at the intended decision\-comparison assertion\.
3. Removing the mutation restores the passing result\.

Use a type\-correct mutation, not an unconditional assertion failure, import error, omitted root, or fabricated replacement gate\. A failure at compilation or freshness does not count as the telemetry negative control\. Record collateral test failures accurately; do not claim the control isolates this test unless the evidence establishes that\.

If the mutation changes freshness\-tracked bytes, keep the isolated control’s prerequisites honest using the existing fixture/provenance mechanism, or an already supported gate seam\. Record the mutated inputs separately\. Do not disable the freshness rule, misstate source identities, or publish a baseline bound to the mutant\. Mutation evidence is an experiment, not acceptance of changed product behavior\.

Reuse the predecessor’s explanation of the original test weakness; do not rerun historical suites solely to reproduce it\. Run the containing EvalGating suite once for the final candidate and broaden only for an affected dependency or concrete remaining risk\.

## 4\. Close any directly caused freshness drift here

Check whether edited test/fixture files belong to the canonical baseline’s tracked inputs\. Do not assume a test\-only edit is invisible to freshness\.

If they are tracked, prepare the smallest provenance refresh against the final unmutated candidate inputs\. Reuse the predecessor’s established inventory, digest, and renderer mechanisms\. Use real source hashes; preserve the tracked\-input set, expected outputs, scenario identities, comparisons, coverage, thresholds, metrics definitions, and gate semantics\. Retain the actual evaluation time rather than describing reused evidence as a new run\.

Reuse the 9/9 corpus result only after checking its relevant behavior\-producing inputs and configuration\. A test\-harness change does not by itself require the whole corpus again, but an affected evaluation dependency must be resolved\. Repeat only the genuinely invalidated check, or the corpus if it cannot be meaningfully separated\.

The final positive suite must see the final test and baseline combination, with valid freshness prerequisites\. Review and apply that same combination\. After application, read back exact bytes and verify actual checkout freshness\. If there is no directly caused baseline drift, leave the baseline untouched\.

Do not run `npm run eval:golden` or other commands that delete shared output or write into shared `eval`\. Do not omit a tracked file, relax freshness, or accept new behavioral expectations to keep the task green\.

## 5\. Review, apply, and report

Obtain the contract’s focused independent BOUNDARY review of the strengthened assertion, fixture validity, discriminating control, and any baseline delta\. Reuse the existing runner and collectors\. Correct in\-scope findings and recheck affected evidence; do not reopen unrelated reviews or build a helper framework\.

Reviewer checks must use isolated copies and fresh output destinations\. Frozen author results and predecessor records stay unchanged\. Preserve reviewer authorship and keep the final disposition separate from reviewed material\. Before application, confirm preimages and relevant inputs still match; apply the final reviewed bytes and verify readback\.

Preserve product source, maintainer files, installed 0\.3\.160, consumers, sibling work, and unrelated dirty files\. No Git reset/clean/index/commit/branch changes, dependency installation, packaging, installation, host launch, model request, live consumer write, approval click, external runtime call, or publication\. Local test fixture writes are permitted\. Historical write allowances remain SPENT and expired quarantine is not renewed\.

Deliver `report.md`, `result.json`, `task.diff`, recoverable preimages, and necessary raw check/review evidence\. Lead with:

- Whether the telemetry regression now distinguishes the intended defect, and the exact failing assertion in the negative control\.
- Which test and optional baseline fields changed\.
- Final focused\-suite, freshness, corpus\-reuse, and independent\-review outcomes, recorded separately\.
- Remaining corpus limitations and one concrete next recommendation\.

Keep structural parity, empty validation denominator, missing second\-turn creation, zero prompt samples, and the single artifact\-producing corpus scenario open unless separately demonstrated otherwise\. Synthetic test fixtures do not add real prompt samples or runtime qualification\. Preserve previous scoped installed/write evidence; this task adds no new installed, natural\-language, or Databricks/ADF/DBFS qualification\.

Claim APPLIED only after actual readback and close the telemetry finding only to the demonstrated scope\. Persist the result, release only this task’s ownership, and stop without launching another task\.
