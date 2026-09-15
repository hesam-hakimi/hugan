# Restore the two trusted\-write approval regressions

TASK\_ID: ETL\-0915\-TRUSTED\-WRITE\-APPROVAL\-TEST\-REPAIR01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
PREDECESSOR: ETL\-0915\-PHASE\-H\-AND\-FIRST\-RELEASE\-SCOPE01\.
SCOPE: Apply the prepared repair to the two affected approval\-manifest tests, prove their assertions execute and detect the intended defect, and complete the bounded review\.

The owner authorizes this test repair through application, focused verification, and correction of in\-scope review findings\. Continue routine work without asking for approval again\. All execution, responses, code, and deliverables must be in English\. Use text, filesystem, and DOM/accessibility interfaces only; no screenshots, video, OCR, or vision\.

## 1\. Recover the prepared repair

Work in the existing checkout:
`C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`

Read applicable local instructions and the accepted contract:
`C:\docs\ETL_Team_Test_Prep\references\09_AGILE_REPAIR_AND_VERIFICATION_CONTRACT.md`

Expected contract v1\.2: 23,684 bytes, SHA\-256:
`5387aa5c42940eceb2ffcd4d68d732ad3d57f1c69c2288c66bd0f32455e6f75b`\.

Locate the predecessor’s actual `report.md`, `result.json`, final review disposition, prepared patch, and next implementation brief through its published task metadata under `C:\docs`\. Use those records to resolve exact filenames, test titles, patch identities, and expected results\. Do not invent a patch path or repeat the Phase H investigation\. Preserve the closed predecessor\.

Authenticate ownership of the affected test surface before editing\. Reuse an existing implementation claim for this repair if it is yours; do not dispatch a duplicate task under another name\. A live foreign owner must retain its surface\. If the repair is already applied, establish its actual source and verification state and complete only the remaining work\.

Establish one task\-owned evidence directory\. The last reported baseline was HEAD `45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19`, source version 0\.3\.147, dirty count 81, shared `out` 2,041 files, and `.tsbuildinfo.test` 158,611 bytes\. These are context: authenticate current relevant bytes, preserve unrelated changes, and do not reset the checkout to match old counts\.

## 2\. Confirm the test contract and apply the smallest repair

The predecessor reported that two `onboardingWriteApproval` regressions invoke private `collectManifestFiles` through a cast declaring a one\-parameter signature\. The accepted product method takes `(artifacts, workspacePath)`\. The omitted root becomes `undefined`, causing rejection before the intended assertions execute; the cast concealed the mismatch from TypeScript\.

The invariant to preserve is:
**A job configuration that the writer would write must be included in the approval manifest\.**

Read the actual method, its relevant caller/writer contract, and both tests\. Reuse the predecessor’s measured replacement expectations and defect evidence where their inputs match\. Confirm the meaning of each assertion rather than inferring it from its title\.

Inspect the prepared patch and its applicability to current bytes\. The predecessor’s VERIFIED analysis and successful `git apply --check` do not establish that repaired tests have passed\. If preimages match and the patch meets this brief, apply it once\. If relevant bytes have changed, reconcile only the affected delta and validate the adapted repair; preserve the original patch as provenance\.

Supply a valid task\-owned workspace root and fixtures satisfying the actual accepted containment and artifact prerequisites\. Do not stop at adding a second argument if the fixture or expectation still embodies the old contract\. Keep private test access narrowly aligned with the real signature; do not introduce loose casts, ignored type errors, or public product exports merely to silence the mismatch\.

Preserve both regression identities and their substantive assertions\. Do not skip them, replace them with expected setup failures, weaken inclusion checks, or change shipped behavior\. In\-scope test/fixture corrections may be completed autonomously\. If a genuine product defect prevents the accepted expectation from passing, retain the failing evidence and prepare the smallest concrete product follow\-up instead of changing the expectation to accept it\.

## 3\. Prove effective coverage

Reuse the existing isolated lane, runner, fixture utilities, and evidence collectors\. Check their relevant source/test/configuration identities once\. Use `b1-lane.corrected.js` only where its declared inputs apply; create minimal glue only for a demonstrated gap\. There is no shared helper repository to build as a prerequisite\.

Use the repository’s normal test mechanism with focused selection of the affected tests or their smallest necessary containing suite\. Record the selected and executed test identities so an empty selection cannot pass unnoticed\. Compile changed TypeScript and dependencies into task\-owned output when required; reused compiled code must correspond to the actual tested inputs\.

Provide these three observations, reusing valid retained evidence for the first where possible:

|Observation                    |Required meaning                                                                                                                                                 |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Original failure               |The old call cannot reach the intended checks because the required root is absent. Report this accurately as a test invocation/setup defect.                     |
|Repaired execution             |Both tests execute their intended assertions against the actual implementation and pass with valid fixtures. Compilation alone is insufficient.                  |
|Discriminating negative control|The repaired assertions detect omission of a writer-eligible job configuration from the manifest, with valid workspace and fixture prerequisites still satisfied.|

Use an existing meaningful negative case if it already proves the last row\. Otherwise use a narrowly scoped, reversible mutation in an isolated copy of the actual code exercised by the tests\. The negative control must fail at the relevant assertion, not during import, compilation, root validation, or fixture setup\. Do not obtain it with an unconditional failing assertion or by omitting `workspacePath` again\. Keep such mutations out of the checkout and restore the isolated candidate afterward\.

Distinguish repairing broken tests from fixing a product regression\. The old invocation failure is not evidence that the product violates manifest completeness\. Report actual counts, exits, and failed assertions; do not claim repository\-wide green results from this focused run\. Broaden testing only for an affected dependency, concrete remaining risk, or required gate\.

## 4\. Keep the execution boundary

Only the affected permanent test file&#40;s&#41;, necessary test fixtures, and this task’s evidence may change\. Preserve product source, runner registration, the applied writeFlow repair, maintainer files, canonical references, installed 0\.3\.160, existing consumers, and closed reports\. Do not reset, clean, stage, commit, change branches, or install dependencies\.

Inspect command side effects before invoking them\. Normal compile/test commands can delete or rewrite shared `out` and buildinfo; use the existing isolated lane\. Do not run `npm run eval:golden`, the Phase H corpus, or baseline regeneration in this task\. D1\-D6 and first\-release acceptance remain separate decisions\.

No packaging, installation, host launch, sign\-in, model request, live consumer write, approval click, external runtime call, publication, or teammate messaging is authorized here\. Test fixture writes in task\-owned temporary roots are permitted and must not be represented as a new installed product\-write qualification\. Historical \.154/\.155/\.160 allowances remain SPENT; expired quarantine is not renewed\.

## 5\. Review, preserve evidence, and finish

Use the accepted contract’s BOUNDARY review for approval\-manifest coverage and changed expected results\. After author verification, obtain an independent read\-only review of the actual test delta, real consumer contract, positive/negative evidence, and relevant source identities\. The review is limited to this repair\. Correct in\-scope findings and recheck the affected delta without reopening unrelated historical reviews\.

Prevent the predecessor’s evidence overwrite incident: inspect helper output paths before execution, use fresh task/reviewer output destinations, and never rerun a helper against a frozen or predecessor\-owned result path\. If a helper has a fixed destination, copy and minimally adapt it within this task before use\. The reviewer may run checks on isolated copies; reviewed inputs and author evidence remain unchanged\. Preserve review authorship and disclose any fallback reviewer\. Keep the final verdict outside the frozen reviewed material\.

Deliver one concise `report.md`, one `result.json`, the final `task.diff`, recoverable preimages, and only necessary raw logs/review records\. Record:

- Exact changed files and patch origin; what was applied or adapted\.
- Both test identities, expected behavior, actual assertion outcomes, and the negative control’s failure location\.
- What was measured now versus reused, with matching input identities\.
- Relevant preservation checks, actual review disposition, and any remaining limitation\.
- A concise handoff for the next isolated Phase H corpus run, preserving its old baseline for comparison and leaving regeneration undecided\.

Report APPLIED only after readback confirms the intended source changes\. State independent review separately and precisely\. If blocked, name the exact unresolved dependency and preserve completed work\. Do not claim a product release, installed qualification, or resolution of the remaining historical failures\.

Persist the result, release only this task’s ownership, and stop\. Do not start the Phase H run automatically\.
