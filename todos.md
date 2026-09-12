Repair the concrete job-config contract gaps before another live qualification

TASK_ID: ETL-0912-JOBCONFIG-CONTRACT-AND-QUALIFICATION-REPAIR01
STATUS: PREPARED_FOR_OWNER_SUBMISSION; not executed by ChatGPT.
Scope: bounded source/test correction, existing test-driver correction and focused review. PRODUCT_WRITE_AUTHORIZATION_BUDGET: 0.

Use the current Windows engineering session. Resolve the final GATE-PATH-AND-EVIDENCE-REVIEW01 report and reviewer verdict under ETL-0912-INSTALLED-0152-ORCHESTRATOR-PREVIEW01. Authenticate ownership release and current source preimages. Reuse an existing matching repair task if already instantiated; otherwise acquire one bounded task. No broad C:\docs scan, duplicate intake or reconciliation campaign.

Owner submission authorizes the source/test and task-helper changes below. All engineering communication is English. No screenshots, video, image inspection, OCR or vision. No live host/model run, approved consumer write, build/package/install, dependency installation, version bump, Git mutation, DBFS publish, job execution or deployment. Preserve .152, all historical fixtures/evidence, both worktrees’ unrelated changes, shared out and .tsbuildinfo.test. Compilation/tests must use the existing isolated output lane with its authenticated resources.

Correct starting state

The selected consumer Orchestrator reached the genuine etl_write_to_workspace tool owned by td-etl.databricks-etl-copilot .152. There was no generic-edit bypass. Skip declined prepareInvocation consent for the FIRST call. The tool body never executed: no extension-owned preview, previewId, retained candidate bytes or final Approve write modal existed. The earlier PREVIEW_AND_CANCEL_VERIFIED claim was withdrawn. Preserve that correction; do not rerun or rewrite history.

Three different causes need different repairs:

1. Product gap: the model-supplied job path was job_conf/ERUS9/… instead of job_conf/conf/ERUS9/…, with no destination-layout check before preview. The DBFS path mapper’s filename fallback would drop the zone, as established by code tracing, not deployment.
2. Product gap: .conf and .json are both permitted by the shipped job-config contract, but several discovery consumers recognize only .json. A correct conf/ directory alone does NOT restore .conf inventory/discovery.
3. Test/executor gap: the clarification answer omitted registered filter order_status IS NOT NULL; candidate bytes and validator payloads were not captured; tool consent was mislabeled as final approval. Do not attribute the wrong clarification answer to the product.

A. Enforce job-config destination shape at the trusted boundary

Inspect the real contract, valid consumers and guarded preview/write path. Add the smallest shared validation at the appropriate job-artifact boundary BEFORE a preview manifest/record is accepted, and ensure the write phase cannot evade it. Require the applicable job_conf/conf/ layout and a permitted extension from the authoritative contract. Use existing normalization/containment utilities; keep canonical root safety independent from relative layout.

Reject an invalid model-supplied destination with an actionable explanation before preview creation or writing. Do not silently relocate it, create a new candidate under a different path, or mutate a previously approved plan. Do not broaden generic PathValidator rules for unrelated artifact types or invent a new planning/approval subsystem.

Inspect DbfsPublisher’s corresponding job-config mapping. Remove silent zone loss for invalid job-config paths through the smallest explicit validation/error behavior consistent with valid callers. Preserve the zone/subpath for conforming paths and keep different zones’ same-named jobs distinct. No actual publishing is permitted. Do not migrate existing consumer files or change unrelated artifact mapping.

B. Make supported extensions work through discovery

Trace and correct the affected readers identified in the review:

• src/core/artifacts/ArtifactReuseTypes.ts;
• src/tools/EtlReadOnlyToolService.ts;
• src/services/postRunVerification/VerificationIntentResolver.ts;
• src/customization/RepoInventoryService.ts.

Verify the actual paths and call sites before edits. Apply the existing contract’s supported-extension policy consistently, reusing the established seam where available. A glob change is insufficient if downstream classification or parsing still rejects the supported artifact. Preserve legitimate .json behavior and ambiguity/collision handling; do not arbitrarily select one file when both extensions identify the same job. Do not solve this by forbidding .conf, renaming it to .json, changing its contents, or depending on an unused constant.

Keep the change confined to job-config layout, recognition and affected consumers. If a broader parser redesign is required, document the concrete boundary and do not expand silently.

C. Repair the existing qualification driver and input contract

Reuse the final transport and fixture utilities; no new harness. Preserve the frozen fixture and failed transcript. Prepare corrected clarification data outside the consumer, including the exact registered filter. Answers must distinguish registered literals, derived paths and unresolved technical choices. A question asserting ‘no additional filtering’ must not receive agreement when the registered filter is nonempty.

Resolve READFORMAT-VIEW-VS-ANSWER-001 against the actual packaged Framework semantics: whether plain path-backed Delta can legitimately use read-format: view without type: srz_zone. A Delta source declaration alone is not proof of an SRZ classification. Record the supported encoding and its authority, or retain the semantic blocker. Do not label validator-driven changes equivalent without evidence or invent a new business answer.

Correct the observer’s state distinctions:

1. Host consent for a preview-producing call;
2. Actual tool result with extension-owned previewId/manifest;
3. Host consent for the identical-content call carrying that previewId;
4. The genuine Approve write modal.

The driver must never classify Allow Once/Skip by label alone as final approval. Before any future qualification claim, it must durably capture the actual final rendered candidate bytes, the corresponding validator payload with verbatim warnings, the preview manifest/ID and the pending final approval. A model summary, tool progress row or output-path string is insufficient. Missing evidence produces a specific incomplete result, never a fabricated success. Do not reconstruct the lost old candidate or inject stale preview state.

Offline helper checks may use clearly labeled synthetic observations to test these distinctions; they are not live product evidence. No UI consent or write click is authorized in this task.

D. Focused verification and independent review

Use permanent behavioral regressions for the product changes: invalid/missing conf/ layout and prefix lookalikes; conforming .conf and .json paths; unchanged canonical containment; invalid paths producing no accepted preview/write; supported config discovery and reuse through the affected real consumers; ambiguous dual-extension cases according to existing policy; zone-preserving DBFS path mapping without external calls. Verify unrelated artifact behavior where the changed seam is shared. Use independent literal expected outcomes rather than deriving both sides from the policy under test.

Reproduce concrete pre-fix behavior using retained source/preimages or existing pre-fix APIs without resetting the dirty tree. Run the smallest affected suites and required adjacent checks, not the entire historical inventory. Include the corrected isolated resources so a missing test-lane resource is not confused with a product regression. Preserve known unrelated failures and report new ones separately.

Use one focused independent reviewer for the final source diff, affected tests and helper changes. If the named Verifier is unavailable, a disclosed equivalent read-only reviewer is acceptable; it must not mutate product/source/consumer files or control runtime. Preserve its actual verdict in its own task-owned directory, or capture a returned message honestly when file output is unavailable. Address concrete in-scope findings and obtain the actual final disposition; do not self-promote CHANGES_REQUIRED.

E. Finish with a concrete next qualification brief

Report changed files, behavior corrected, actual tests and reviewer verdict, source identities and preservation. Claim source repair only to the extent proven. No new installed qualification is established here.

Prepare, but do not execute, the smallest next candidate/package-and-Orchestrator-preview brief using the existing .152 build/install and driver interfaces. A distinguishable candidate is required because source changed; .152 remains historical. The future run needs a fresh legitimate preview, captured bytes/validation/manifest, correct layout, intact filter, established read semantics, and decline at the genuine final Approve write modal. Keep approved writing as a later explicitly scoped gate. Do not reuse the previous report’s proposed .152 write brief as if its prerequisites were met.

Close ownership with result pins. Retain open INCLUDE-SQL-KEY-EXTRACTION-001 unless separately reproduced/fixed under an applicable authority, Route B’s separate gap, broader STTM and four-header limitations, OUTCOME-DISCLOSURE-001, catalog-asset limitations, Windows case-folding gaps and all historical Base/Upgrade/B1/C1, QA, R3/R4, F-1, CASE2, model/trust/toolchain/source-preservation boundaries. Quarantine ends 2026-09-13 inclusive UTC without automatic extension. No RELEASE_ACCEPTANCE or FULL_PRODUCT_OR_ASKTD_READINESS. Demo remains deferred.
