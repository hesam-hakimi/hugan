# Run Phase H in parallel against an isolated, fixed snapshot

TASK\_ID: ETL\-0915\-PHASE\-H\-PARALLEL\-GOLDEN\-RUN01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
PREDECESSOR: ETL\-0915\-PHASE\-H\-AND\-FIRST\-RELEASE\-SCOPE01\.
PARALLEL\_WITH: ETL\-0915\-TRUSTED\-WRITE\-APPROVAL\-TEST\-REPAIR01\.
SCOPE: Execute the existing Phase H golden corpus against a coherent snapshot of current source, retain the historical baseline, and explain measured differences\.

The owner authorizes this separate parallel evaluation\. The approval\-test repair continues under its own authority\. Its instruction not to launch Phase H automatically remains applicable to that session; this brief authorizes Phase H in this session only\. Do not run or modify the sibling’s repair\.

Use English for all execution, responses, code, and deliverables\. Use text, filesystem, and DOM/accessibility interfaces only; no screenshots, video, OCR, or vision\. Complete authorized local setup, evaluation, and in\-scope corrections without repeated approval requests\.

## 1\. Recover the actual evaluation and its inputs

Source checkout:
`C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`

Read applicable local instructions and the accepted contract:
`C:\docs\ETL_Team_Test_Prep\references\09_AGILE_REPAIR_AND_VERIFICATION_CONTRACT.md`

Expected v1\.2: 23,684 bytes; SHA\-256:
`5387aa5c42940eceb2ffcd4d68d732ad3d57f1c69c2288c66bd0f32455e6f75b`\.

Resolve the completed predecessor through its published task metadata under `C:\docs`\. Read its actual Phase H findings, source references, baseline provenance, execution recommendation, and final disposition\. Locate the real corpus, evaluator, compiler configuration, comparison rules, and freshness gate from those references\. Do not invent their paths or rescan all project history\.

The predecessor established that Phase H is the golden\-corpus evaluation phase\. G1/G2/G3 are another population\. It reported 28 changed tracked inputs, all explained by accepted repair work, and a stale baseline\. Recover the exact list and check present applicability; 28 inputs does not mean 28 test failures, nor does accepted source work automatically accept new outputs\.

Inspect the real command chain before invoking anything\. In particular, `npm run eval:golden` reportedly begins by deleting shared `out`\. Do not invoke that command in the recovery checkout\. Determine whether the existing evaluation is deterministic, recorded\-input replay, or requires live services, and report that distinction accurately\.

## 2\. Establish parallel independence and capture a coherent snapshot

Create one task\-owned root under `C:\docs`, with separate snapshot, build output, evaluation results, and reviewer output locations\. Claim only these new surfaces\. Read the sibling’s published claim and declared editable paths to identify overlap; do not modify its claim, evidence, fixtures, or workspace files\. Check for an already active instance of this same evaluation to avoid duplicate execution\.

Map actual Phase H dependencies against the sibling’s affected tests and fixtures\. Include indirect compile/configuration dependencies, not just runtime imports\. Record whether any overlap affects compilation, evaluated behavior, or only unrelated files\. Do not assume independence from filenames alone\.

Capture the necessary current inputs, including relevant uncommitted changes\. A clean checkout of HEAD would omit accepted work and is not an adequate snapshot\. Use the existing staging helper where suitable\. Capture source/configuration/fixture/corpus/baseline identities and toolchain details sufficient to reproduce this run\.

Check source identities around capture and compare copied bytes\. If relevant inputs change during copying, resolve the affected capture before running; do not label a mixture of revisions a coherent snapshot\. A complete authenticated pre\-edit or post\-edit version of an overlapping file may be used if its provenance and compatibility are established\. Label which version was evaluated\. If coherence cannot be established, finish independent setup and report the exact blocked dependency\.

Once captured, execute from the snapshot only\. Product inputs and the retained baseline stay fixed for the run\. Redirect every writable build/output/cache/buildinfo/result path into this task\. Do not link writable output paths back to the recovery checkout or sibling\. Existing dependencies may be reused read\-only; no dependency installation is part of this task\.

Do not freeze the sibling’s work or require its completion merely because it is active\. At close, compare relevant current inputs with the snapshot\. If the repair is still active, report current applicability as pending where appropriate; do not poll indefinitely\. Results remain valid for the recorded snapshot\. They do not automatically qualify a later combined state\.

## 3\. Execute the real corpus without accepting a new baseline

Reuse matching compiled output only where its source, configuration, fixtures, dependencies, and toolchain identities apply\. Otherwise perform the necessary local compile in the isolated tree\. Do not use shared `out` as evidence of current\-source behavior merely because it exists\.

Use the existing Phase H evaluator and normal case definitions\. Inspect and safely redirect the actual build/evaluation chain inside the snapshot, or use its supported entrypoints\. Preserve evaluation semantics, case selection, and comparison rules\. Do not substitute an ad hoc imitation of the evaluator or silently replace live\-generation cases with replay\.

Retain the original baseline bytes and metadata\. Do not run update/accept modes, rewrite snapshots, refresh input pins, suppress differences, or change freshness criteria to produce green results\.

Report the following separately:

- **Corpus execution:** which cases actually ran, their outputs, and errors\.
- **Behavior comparison:** observed differences against the historical expected results\.
- **Baseline validity:** the unchanged freshness gate’s actual result and applicability\.

If stale provenance prevents the normal gate from completing, preserve that outcome\. An existing output\-only mode or the real underlying evaluator may be used to collect advisory candidate measurements, provided its case semantics and prerequisites remain intact and the invocation is disclosed\. Such measurements do not turn a stale gate into PASS\. If there is no faithful way to evaluate independently, report the exact blocker instead of altering the gate\.

This task authorizes local compilation and offline evaluation using existing inputs\. If authentic corpus cases require live credentials, model calls, host interaction, or external runtime access, identify those cases and complete the offline portion and concrete follow\-up definition\. Do not silently omit them from the denominator or claim the full corpus passed\.

Run one complete applicable corpus evaluation after setup is sound\. Retry a failed setup or rerun an affected case only to resolve a concrete error or invalidated input; retain the earlier attempt\. No repeated full campaign solely to improve presentation, no general unit\-suite campaign, and no execution of the sibling’s approval\-test repair\.

## 4\. Explain differences without changing expected behavior

Derive the case inventory from the actual corpus\. Record selected, executed, skipped, errored, and compared cases, with stable identities\. Distinguish a precondition/freshness stop from a behavioral failure\. An empty selection or partial execution cannot produce a full\-pass claim\.

For each difference, report old expectation, observed output, relevant source/input change, accepted requirement or decision, recommended disposition, and supporting evidence\. Use clear categories:

- Unchanged behavior\.
- Difference explained by an applicable accepted requirement; baseline update proposed\.
- Behavior contradicting an applicable accepted requirement; product repair proposed\.
- Environment/input limitation\.
- Acceptance decision required or insufficient evidence\.

Use only the evaluator’s already accepted normalization\. Do not merge identities, discard fields, rewrite paths, or strip differences just to improve a match\. Preserve raw outputs alongside any official normalized comparison\.

Treat correlations cautiously: a changed input does not alone establish the cause of a changed output\. Consult the relevant producer/consumer contract and accepted changes; use a small discriminating check only where needed to settle an important difference\.

No baseline regeneration, product/test repair, or D1\-D6 policy decision is authorized by this evaluation\. Prepare recommendations with evidence\. Any proposal to refresh the baseline must enumerate the changes that would be accepted and identify unresolved rows explicitly\.

## 5\. Preserve state and reuse existing tools

The recovery checkout, original baseline, shared `out`, shared `.tsbuildinfo.test`, installed 0\.3\.160, consumers, canonical references, and closed task records remain unchanged by this task\. Sibling\-authorized edits are expected; attribute them separately rather than treating every concurrent dirty\-count change as damage or reverting it\.

No reset, clean, index/commit/branch mutation, dependency installation, packaging, extension installation, host launch, model request, approval click, live consumer write, external runtime call, publication, or teammate messaging\. Local fixture/output writes belong only to this task\. Historical \.154/\.155/\.160 allowances remain SPENT; expired quarantine is not renewed\.

Reuse existing lane, timing, capture, and comparison helpers where their interfaces fit\. The authenticated `b1-lane.corrected.js` is a candidate only if its declared inputs meet this evaluation’s needs\. Do not build a shared helper repository or add a new harness as a prerequisite\. Small path\-redirection glue is permitted when necessary and must be recorded\.

Inspect helper output destinations before executing them\. Never run a helper that overwrites frozen author outputs, predecessor evidence, or sibling results\. A minimal task\-owned copy may redirect output; keep its behavior change explicit\.

## 6\. Review and deliver

Apply the accepted contract proportionally\. Obtain one focused independent read\-only review of input binding, corpus coverage, baseline\-status interpretation, and proposed dispositions of material differences\. Reuse the evaluator and raw evidence; review independence does not require a second implementation or repetition of the entire historical audit\.

Reviewer execution must use isolated copies and new output destinations\. Correct actual in\-scope findings and recheck only affected evidence\. Keep reviewed inputs and author results fixed; preserve the final review verdict separately, with accurate reviewer provenance\.

Deliver one concise `report.md` and `result.json`, with only the necessary input manifest, original baseline reference, raw outputs, and review evidence\. Include:

1. What ran, what was blocked/unexecuted, actual case counts, exits, and timing\.
2. Snapshot identity, included uncommitted changes, and overlap with the sibling repair\.
3. The behavior\-difference table and unchanged baseline\-gate outcome\.
4. The smallest recommended repair or concrete baseline acceptance decision\.
5. Conditions for reusing this result after the sibling finishes, naming affected inputs rather than requiring an automatic full rerun\.

Record execution, baseline validity, applicability to the current checkout, and review disposition separately\. Do not collapse them into a single green label\. Do not claim APPLIED, first\-release acceptance, installed natural\-language generation, or Databricks/DBFS qualification from this task\.

Persist the result, release only this task’s ownership, and stop\. Do not apply recommendations or start another task automatically\.
