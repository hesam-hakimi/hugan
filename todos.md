# Repair environment\-root resolution on the measured trusted\-preview path

TASK\_ID: ETL\-0916\-PHASE\-H\-ROOT\-RESOLUTION\-REPAIR01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
PREDECESSOR: ETL\-0916\-PHASE\-H\-REAL\-VALIDATION\-CONNECTION01\.
SCOPE: Trace and repair the demonstrated root\-resolution failure for `canonical-abfss-path-fidelity`, preserving real validation and authoritative environment selection\.
CLASSIFICATION: BOUNDARY; environment authority, artifact configuration and pre\-write validation\. Delivery is source\-only\.

Owner submission authorizes bounded inspection, implementation, permanent regression coverage, isolated execution, independent review, application and directly necessary baseline changes\. Resolve routine in\-scope choices without another approval request\. Use English for all execution, responses, code, tests and reports\. Use text, filesystem and DOM/accessibility only; no screenshots, video, OCR or vision\.

## 1\. Owner clarification: do not infer the cause from the diagnostic

The owner supplied a job\-config example with `sourceList: [cpat_w]`, a corresponding `cpat_w` sourcing definition, inline SQL and a reference to `${adls.srz.psa.root}`\. A downstream transformation reads a sourced relation\. This is an illustration, not a complete executable fixture or proof about the separate `source1` case\.

A sourced view can be registered by the Framework while executing job modules\. Its absence from included SQL alone does not establish that the job lacks a valid producer\. For `source1`, inspect the actual job’s sourcing declarations, effective view names, inline SQL, producer/consumer execution order and Framework view\-registration contract before classifying the diagnostic\. A SQL include containing `CREATE VIEW` must not become a new universal requirement\.

Keep that inspection read\-only in this task\. Record whether the `source1` finding is independent, cascading, a suspected false positive or still unresolved\. Do not suppress it, append SQL to satisfy a name search, rename a source, or repair the source\-view validator as part of this root task\. Do not promise that fixing roots alone makes the complete scenario pass\.

Likewise, `adls.source.root` and `adls.destination.root` are names appearing in the failing scenario, not automatically mandatory names for every job\. Resolve the keys actually referenced under the accepted Framework/configuration contract\. Do not rename valid keys such as `adls.srz.psa.root` or impose a new root namespace\.

## 2\. Recover current evidence once

Checkout:
`C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`

Read applicable local instructions and the delivered repair contract:
`C:\docs\ETL_Team_Test_Prep\references\09_AGILE_REPAIR_AND_VERIFICATION_CONTRACT.md`

Expected contract v1\.2: 23,684 bytes; SHA\-256:
`5387aa5c42940eceb2ffcd4d68d732ad3d57f1c69c2288c66bd0f32455e6f75b`\.

Resolve the predecessor’s report, result, final review, actual artifacts, environment\-control experiment and prepared root follow\-up through published task metadata under `C:\docs`\. Reuse its working harness and recorded reproduction\. Recover applicable environment\-selection, dependency\-binding and Framework substitution contracts from their referenced sources; do not re\-audit unrelated history\.

Last reported state, to authenticate locally:

- The selected scenario now reaches the real `PreWriteValidationPipeline` through trusted preview\. Two genuine validation observations are recorded through authoritative session state; both are failures\.
- Result: `ok: false`, five errors, twelve warnings, `writeBlocked: true`\. Diagnostics include missing/unresolved root references and the `source1` finding\. Preserve exact per\-run diagnostic identities rather than treating five messages as five independent defects\.
- Supplying a workspace environment config containing both reported roots cleared zero of the five errors; preview still generated a new environment config\. This is a reproduction to explain, not proof of which binding or precedence rule is wrong\.
- A sibling scenario’s `FirstRenderInvariantGuard` also rejected the relevant condition\. Resolve the exact retained evidence rather than assuming that guard needs changing\.
- Focused regression suite: 21 passing/0 failing\. Four final controls discriminate; earlier synthesized\-success/fabricated\-observation controls initially failed to detect their mutations and were corrected\. Review ended VERIFIED\_WITH\_LIMITATIONS, zero blocking/material findings\.
- Canonical validation ratio is a measured 0/2, not unmeasured\. The aggregate gate fails\. Freshness was current; nine corpus scenario IDs were stable\. Preserve D2 null/count/rate coherence and T1 telemetry independence\.

Authenticate task ownership and relevant inputs once\. Create one task\-owned evidence root, retain editable\-file preimages, and use the predecessor’s established runner/collector\. Resume only your own authenticated task\. Do not duplicate an active writer, acquire foreign claims or interpret missing reports as idle ownership\.

## 3\. Contain compilation, including the reviewer’s work

The predecessor disclosed that a reviewer compiled into shared output: `out` changed from 2,041 to 2,085 files and `.tsbuildinfo.test` from 158,611 to 160,132 bytes\. No retained byte\-copy was available for restoration\. Those are reported intake facts, not permission to restore by guessing or to treat the earlier output identities as current\.

Capture the actual current protected\-output identities once and preserve them throughout this task\. Do not use shared `out` as evidence for this candidate\. Reuse a matching isolated build or compile the required source into an isolated task snapshot, including the relevant dirty changes\. Do not reset/clean/rebuild the shared tree to recover old counts\.

Before every distinct compile command, establish its effective working directory, project configuration, output paths and incremental buildinfo destination\. All writable compiler destinations, including `outDir`, applicable declaration output and `tsBuildInfoFile`, must resolve inside the task\-owned lane\. Use explicit supported overrides or an isolated task configuration; changing cwd alone is insufficient\. Reuse a verified command instead of rebuilding this setup for every check\.

Pass this exact restriction in the reviewer brief with the concrete isolated paths and inspected commands\. A generic permission to compile is insufficient\. The reviewer may reuse applicable compiled evidence or compile in its own isolated lane\. No compiler or helper may fall back to live checkout output\. No hand\-edited generated JavaScript\.

Do not run the normal `npm run compile`, `npm run eval:golden`, or other commands with shared\-output side effects\. Keep intermediate evaluation reports outside canonical `docs/eval`; final reviewed baseline application is handled below\. If protected output changes unexpectedly, stop the responsible command, retain the incident and identify its scope before relying on affected evidence\.

## 4\. Trace authority and implement the smallest root repair

For each failing root diagnostic, trace:

1. The exact reference in the generated job, inline SQL, include or environment artifact\.
2. Its accepted source: selected on\-disk environment, explicitly supplied configuration, or authorized new\-environment inputs\.
3. The environment identity actually chosen and read, dependency binding, and the payload passed into trusted preview\.
4. Generated versus reused environment handling, include/merge precedence and substitution resolution\.
5. The final configuration seen by the real validator and the resulting diagnostic\.

Use real bytes, parsed values and call attribution\. A file existing in the workspace does not prove it was selected or read\. A log saying an environment was supplied does not prove its values reached validation\. Inspect both real execution paths of the selected scenario\.

Determine whether values are lost by selection, routing, generation, merge/resolution or validation, or whether the scenario requests roots for which no accepted values were supplied\. Record the demonstrated cause and affected files before editing\. Do not infer that creating a new env is wrong in every context; apply the accepted create\-versus\-reuse decision for this case\.

Repair only the proven defect and directly coupled consumers\. The resulting behavior must preserve:

- Authoritative selected environment values reaching preview and validation through the existing supported configuration mechanism, including accepted include/substitution semantics\.
- Existing precedence and dependency authority\. Reused on\-disk config must not be silently replaced by caller text or an incomplete generated env when the contract makes that file authoritative\.
- Valid configured root names and path composition\. Use the actual parser/resolver; do not apply a global text replacement or insert guessed ABFSS paths/default storage roots\.
- Rejection of genuinely missing, unresolved or invalid required configuration with specific diagnostics\. Absence of necessary values must not become a passing preview\.
- Existing approval, containment, dependency\-change and no\-write behavior\. Keep the real validator and its result in the composed path\.

Editable scope is the directly responsible root/environment selection, propagation, generation or resolution code, strictly necessary types/callers, focused tests/fixtures, and current Phase H baseline files\. Any necessary validation\-code correction must preserve the accepted required\-input rules\. Do not weaken `FirstRenderInvariantGuard`, rename config keys, change view\-resolution semantics or redesign the harness\.

A test fixture may be corrected only when a demonstrated mismatch with an accepted input contract warrants it; state that separately from a product repair\. Never add missing values to the canonical scenario solely to produce green results\. If the trace establishes a valid rejection of unspecified owner input rather than a code defect, complete the diagnosis and concrete input proposal, preserving the rejection; do not manufacture a source fix\.

## 5\. Verify root behavior independently of the remaining view finding

Add focused permanent coverage through the existing trusted\-preview/validation entrypoints\. Use typed deterministic fixtures and the real validator\. Cover the relevant cases with a small set of assertions:

|Case                                            |Required evidence                                                                                                                      |
|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
|Selected env contains the required roots        |The intended env is actually read, values reach the final config, resolved paths are correct, and the target root diagnostics disappear|
|Root values are genuinely missing/unresolved    |Specific rejection remains; no invented default or successful validation record                                                        |
|Selected env versus conflicting/generated values|The accepted precedence and reuse rule holds; the test detects replacement or loss of authoritative values                             |
|Valid non-generic key used by the job           |Existing supported root-key semantics remain valid; no requirement for unreferenced generic aliases                                    |

Reuse accepted dependency\-binding/adverse tests where their inputs still match\. If this change affects that boundary, run its focused checks, including changed dependency handling where applicable\. Avoid repeating the entire historical campaign\.

Use the retained pre\-fix reproduction and a behavioral negative control suited to the demonstrated cause: reverting the bounded repair or deliberately losing the authoritative root binding in an isolated copy must fail at the intended root/authority assertion, not at compilation, import or baseline freshness\. Restore the candidate and verify the passing regressions\. Record collateral failures honestly\.

Keep the raw `source1` result visible during the original scenario replay\. A root\-focused regression may pass while the complete preview remains rejected by a separate diagnostic\. Verify root correctness with actual resolved configuration and diagnostic identities, not merely fewer errors, absence of a substring, or aggregate gate PASS\.

Run the affected containing suites, including the real\-collection assertions and applicable D2/T1 checks\. Execute the existing nine\-scenario corpus in the isolated lane for the final candidate; reuse unrelated controls only where dependencies still match\. Do not count an adverse fixture as new canonical corpus coverage or settle the unresolved expected\-invalid population policy through this task\.

## 6\. Baseline, review and application

Preserve the prior baseline\. Classify all candidate differences by scenario: directly explained root/configuration/validation changes, retained view findings, other scenario behavior, and provenance/timing\. Update only expectations and current baseline fields justified by this authorized root repair\. Leave unexplained differences open instead of accepting them wholesale\.

Generate JSON/Markdown with the actual product mechanisms, current tracked\-input identities and real execution time\. Preserve the observation population and 100% measured validation threshold\. Do not convert an observed failure into unmeasured data or declare success because the baseline is fresh\. Source/evaluator changes invalidate affected old\-run evidence; report what was rerun and what was reused\.

Obtain focused independent BOUNDARY review of the root cause, authority/precedence, required\-input rejection, composed regressions, baseline delta and compile isolation\. Reviewer outputs use fresh destinations; closed records and frozen author outputs stay unchanged\. Preserve actual reviewer authorship and record the final verdict separately from reviewed material\. Correct in\-scope findings and recheck only affected evidence\.

Confirm relevant inputs and preimages still match before applying the final reviewed source and baseline bytes\. Verify readback, actual checkout freshness and preservation of protected output at the new intake identities\. Keep unrelated dirty work, maintainer files, installed 0\.3\.160, real consumers and closed evidence unchanged\.

No Git reset/clean/index/commit/branch changes, dependency installation, packaging, installation, Host launch, model request, external runtime call, live consumer write, approval click or publication\. Local fixture writes are permitted\. Historical allowances remain SPENT and expired quarantine is not renewed\. Reuse helpers rather than creating a helper repository or another reporting framework\.

Deliver `report.md`, `result.json`, `task.diff`, recoverable preimages and necessary raw execution/review evidence\. Lead with the proven root cause, exact changed behavior, whether the targeted root failures are gone, and the remaining full\-scenario validation result\. Record test passes, validation numerator/denominator, gate, freshness, application and review separately\.

For `source1`, report only the demonstrated producer/consumer facts and whether a separate investigation is still needed\. Preserve D1/D3/D4/D5 and other inherited limitations to their actual scope\. This task adds no fresh natural\-language, installed, Databricks/ADF/DBFS or release qualification\.

If useful, prepare a separate read\-only follow\-up for the `source1` view\-origin question, including views created from the job itself\. Such work may use an immutable snapshot and private lane; it must not edit this task’s surfaces, share writable outputs or publish a competing baseline\. Do not start it automatically\.

Claim APPLIED only after readback\. Persist the result, release only this task’s ownership and stop\.
