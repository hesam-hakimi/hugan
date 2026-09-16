Make Phase H validation evidence meaningful when no observations exist

TASK_ID: ETL-0916-PHASE-H-VALIDATION-OBSERVATIONS-REPAIR01
STATUS: PREPARED_FOR_OWNER_SUBMISSION; not executed by ChatGPT.
PREDECESSOR: ETL-0916-PHASE-H-TELEMETRY-TEST-REPAIR01.
SCOPE: Repair D2, the empty validation denominator, across the actual metric, its gate and report consumers, with permanent regression coverage and directly necessary baseline upkeep.
CLASSIFICATION: BOUNDARY; this changes evaluation and acceptance semantics. Delivery is source-only.

The owner has accepted the following policy for this task:

• With zero eligible validation observations, validation success is NOT_EVALUATED, not 100% and not a measured 0% failure rate. It cannot satisfy a required validation-success criterion.
• With eligible observations, compute the real success ratio. All successful observations yield 100%; mixed outcomes yield their actual ratio. Preserve the existing 100% acceptance threshold for measured results.
• Missing evidence must remain visible. Do not invent observations or weaken another gate to obtain a passing report.

Submission authorizes inspection, the bounded source/test repair, focused execution, independent review, application, and the corresponding baseline changes described here. Resolve routine in-scope choices without another permission request. Use English for all execution, responses, code, tests and reports. Use text, filesystem and DOM/accessibility only; no screenshots, video, OCR or vision.

1. Recover current state and reuse the prepared work

Checkout:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Read applicable local instructions and the already delivered contract:
C:\docs\ETL_Team_Test_Prep\references\09_AGILE_REPAIR_AND_VERIFICATION_CONTRACT.md

Expected contract v1.2: 23,684 bytes; SHA-256:
5387aa5c42940eceb2ffcd4d68d732ad3d57f1c69c2288c66bd0f32455e6f75b.

Resolve the predecessor’s actual report, structured result, final review and prepared D2 proposal through published task metadata under C:\docs. Read the relevant accepted metric definitions and current-state pointers; do not reconstruct hashes from photographs or repeat the historical investigation.

The last reported state is:

• T1’s telemetry regression repaired in evalGating.test.ts; focused suite 7 passing/0 failing. Two independent type-correct mutations were caught at the intended decision-comparison assertion, with no collateral failures.
• Baseline freshness PASS, 274 tracked inputs and zero changed inputs. The telemetry test edit required no baseline change.
• The earlier corpus result was reused: 9/9 scenarios, zero behavioral differences within its scope. It is not evidence for newly changed evaluator behavior.
• D2 remains open: the required validationSuccessRate criterion has been evaluated over zero observations. The corpus has one artifact-producing scenario.
• Other corpus gaps remain distinct: D1 structural parity, D3 missing second-turn create flow, D4 zero real prompt samples, and D5 only one artifact-producing scenario. BYTE-COUNT-001 remains a disclosed historical evidence discrepancy.

Authenticate current relevant inputs and ownership once. Reuse suitable existing lane, runner, collector and fixtures. Resume only your own authenticated attempt; do not duplicate a live task or acquire another session’s files. Preserve interrupted attempts if continuation is needed. Establish one task-owned evidence root and recoverable preimages for edited files.

2. Establish what is actually being measured

Trace the real producer-to-consumer path: validation invocation and result, observation collection, numerator/denominator, aggregation, report schema/renderer, and gate decision. Identify why the current artifact-producing scenario contributes no validation observations: a missing invocation, unrecorded result, excluded population, or another measured cause. State which cause is demonstrated.

Define one eligible observation and the counting unit from the accepted evaluator/validator contract. Preserve that unit and avoid duplicate counting. Artifact creation, a test assertion passing, missing events and unrelated checks are not substitutes for a validator outcome.

Determine how deliberately invalid scenarios are classified today. Distinguish an invalid artifact being correctly rejected from an artifact validating successfully; do not silently change the metric’s population or count rejection as success merely to improve its score. If that part of the contract is unresolved, document the exact ambiguity and complete the authorized zero-observation repair without inventing a new rule for it.

Before editing, record the affected files and consumers in one short scope statement. Prefer the predecessor’s prepared proposal when it implements the accepted policy. Do not build another evaluation harness or redesign generation.

3. Implement the smallest coherent repair

Represent the unmeasured state consistently with the repository’s actual types and consumers. NOT_EVALUATED is the required meaning, not a mandated new enum name. Choose the smallest appropriate existing status/nullable representation, with observation counts exposed where consumers need them. Avoid NaN, Infinity, fabricated percentages, loose casts and truthy/falsy shortcuts that conflate a measured zero with absence.

Ensure the actual gate distinguishes insufficient validation evidence from observed validation failure. An unmeasured required criterion must not pass, and the aggregate decision must not hide it. Preserve other thresholds and independent reasons. JSON and Markdown must agree; a renderer must not turn null/absence back into 100% or present an unmeasured result as all green.

Handle retained reports explicitly if their schema lacks the evidence needed for the new decision. Do not infer an observation count from a percentage. Report that evidence as unknown/insufficient or use the existing versioned compatibility mechanism; preserve historical files as historical evidence rather than silently rewriting them.

If the existing artifact scenario can exercise the real validator through a bounded connection already supported by the evaluator, add that connection and collect the real outcome. Existing accepted real-validator replay fixtures may be reused where applicable. Do not substitute a no-op validator, manually increment counts, or feed a guessed success result into the report.

If obtaining real observations requires a new generation flow, a broad harness redesign, a live model/Host, or a separate unresolved acceptance decision, do not make that expansion a prerequisite. Complete the honest zero-evidence behavior and its tests, explain the measured collection gap, and prepare the smallest concrete follow-up. A corpus correctly reported as insufficient is an acceptable outcome of this repair.

Editable scope is the directly relevant Phase H observation/metric implementation, schema and gate/report consumers, their focused tests/fixtures, any bounded existing validation connection above, and necessary current baseline files. Update directly affected evaluator documentation if needed. Preserve writer/approval behavior, unrelated validators, runner registration, maintainer workflows and unrelated historical records.

4. Verify the decision, not merely the code shape

Use the existing isolated lane and actual evaluator/gate entrypoints. Inspect command side effects first. Do not run npm run eval:golden or another command that deletes shared out or writes into shared eval; direct compilation, evaluation and intermediate results to task-owned locations using the established mechanism. Do not hand-edit generated JavaScript.

Add permanent regression coverage for these distinct cases, reusing existing tests where appropriate:

|Case                                 |Required observation                                                                                                |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------|
|Zero observations                    |Explicit unmeasured state, no success percentage, required criterion not passed; consistent gate and rendered report|
|One or more successful observations  |Actual count and ratio; 100% satisfies this criterion while other gates remain independent                          |
|Mixed success/failure, and all failed|Correct numerator/denominator and measured ratio, including a genuine 0%; required 100% criterion fails             |
|Missing legacy evidence              |No inference of successful validation or invented counts                                                            |
|Actual collection path, if connected |Real validator outcome reaches aggregation and gate with correct scenario attribution and no double counting        |

Exercise boundary cases through the real functions, not a second implementation of the formula in a helper. Keep freshness and unrelated gate prerequisites valid so the zero-observation failure proves the intended policy. Run relevant type checks and the containing EvalGating suite, including the accepted telemetry regression; broaden only for an affected dependency or concrete remaining risk.

Obtain a meaningful behavioral negative control: the original behavior or a small type-correct mutation in an isolated copy treats absent validation evidence as sufficient, and the new regression fails at its intended decision assertion. Record the mutation and any collateral failures; restore the unmutated bytes and passing regression results. Compilation, import, fixture or freshness failures are not this control. Recheck T1’s discriminating control if changed gate inputs/outcome structure invalidate its accepted evidence.

Record executed case identities, commands, exits and relevant source/output correspondence. A passing regression suite may correctly assert that the corpus gate is insufficient; report those two outcomes separately.

5. Keep the corpus and baseline truthful in this same task

Preserve the pre-task canonical baseline for comparison. Source/evaluator changes can invalidate prior golden evidence. Reuse unaffected evidence only after checking the relevant dependencies; execute the changed aggregation, gate and report path on genuine scenario evidence. If the established harness cannot separate those effects reliably, run the nine-scenario corpus once in the isolated lane.

Reusing captured validator results is valid only when their inputs and validator still match. If the historical run never performed validation, a new validation execution is required to supply that evidence. Distinguish newly executed checks, recomputed results from retained evidence, and unchanged reused results.

This is not a bookkeeping-only refresh. The owner authorizes the narrow baseline delta that truthfully records the approved zero-observation policy, measured results from any authorized validation connection, necessary schema/report changes, and current provenance. Do not require zero total differences when the intended metric/gate result has changed. Do not accept unrelated behavioral drift.

Classify the actual delta: observation counts, metric/status and gate reasons; unchanged scenario outputs; provenance and timing. Preserve unrelated acceptance expectations, scenario identities and thresholds. Do not add a scenario merely to manufacture a nonzero denominator. Use the real inventory/digest and product renderer. Retain actual execution times, distinguishing a new run from reuse. Do not bind the baseline to a mutant or omit changed tracked inputs to pass freshness.

Apply only the reviewed current baseline changes needed for this repair. A baseline may be fresh while its validation criterion is insufficient or failing. If an unrelated unexplained difference remains, preserve it and withhold only the dependent baseline acceptance; finish the useful bounded repair work and identify the exact blocker.

6. Review, apply and finish

Obtain focused independent BOUNDARY review of the population/counting rule, zero-evidence decision, consumer compatibility, real collection evidence where added, regressions/control, and baseline delta. Correct in-scope findings and recheck only affected evidence. Reuse existing helpers; do not create a shared helper repository, broad audit or one script per assertion.

Reviewer checks must write to fresh destinations or isolated copies, never overwrite frozen author/predecessor outputs. Preserve actual reviewer authorship and record the final disposition separately from reviewed material. Confirm preimages and relevant inputs still match before application. Apply the final reviewed bytes, verify readback and actual checkout freshness, and report review limitations honestly.

Preserve unrelated dirty work, shared out, .tsbuildinfo.test, closed task evidence, installed 0.3.160 and consumers. No Git reset/clean/index/commit/branch changes, dependency installation, packaging, installation, Host launch, model request, live consumer write, approval click, external runtime call or publication. Local test fixture writes are permitted. Historical write allowances remain SPENT; quarantine is not renewed. Preserve prior scoped 0.3.160 qualification as historical evidence without claiming it covers this new source.

Deliver one concise report.md, result.json, task.diff, recoverable preimages and necessary raw check/review evidence. Lead with the concrete outcome:

• What zero observations now mean, and whether D2 semantics and the actual collection gap are each closed.
• Actual corpus validation numerator/denominator, criterion and aggregate gate outcome; do not conflate these with test pass counts.
• Changed files, relevant test/control outcomes, corpus execution/reuse, baseline freshness/delta and independent review, recorded separately.
• Remaining D1/D3/D4/D5 limits and one prepared next action, without starting it.

Claim APPLIED only after readback. This task adds source/evaluator evidence, not fresh natural-language generation, installed/runtime qualification or release readiness. Persist the result, release only this task’s ownership, and stop.
