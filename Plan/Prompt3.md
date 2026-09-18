Continue the active CLUE implementation and complete the remaining core workflow:

Input workbook → Symcor → every returned cheque → Tungsten → enriched Excel output.

All responses, code, tests, documentation, and handoff updates must remain in English.

This is a continuation of the existing implementation. Preserve the current checkout, user changes, completed fixes, working adapters, durable state, logging, replay support, and output generation.

Finish any active mutation safely before applying this update. Keep one owner for code changes. Independent contract or artifact inspections may run in parallel, but do not let multiple sessions edit the same files.

Working context

* Application repository: C:\repos\fcrm_clue
* Expected working branch: feature/clue-durable-core. Verify the current branch and revision; preserve active work rather than resetting it.
* Reference material: C:\repos\FCRM
* Supplied workbook: C:\repos\fcrm_clue\test_data\Test Data_TDB.xlsx
* Supplied cheque samples: C:\repos\fcrm_clue\test_data\test_cheques
* Current handoff: C:\repos\fcrm_clue\docs\handoff\clue
* Resolve configuration through the existing precedence rules and available .env files, including the supplied reference configuration where applicable. Do not print credential values.

Read the current handoff, relevant native interface artifacts, and implementation before making affected changes. Use actual files rather than screenshots or UI automation.

Reconcile the recent work

First consume any completed results from:

* The correction restricting the OCR-name-based image association to an explicitly labelled demonstration fixture.
* The requirement to process and display every returned cheque.
* The focused inspection of retry, resume, FAILED-item recovery, and UNKNOWN_OUTCOME handling.

Verify their current implementation status rather than repeating completed work. This prompt authorizes targeted implementation fixes needed to finish the core workflow.

The previously reported 292 passing tests are historical evidence. Tie final validation to the revision actually delivered.

Confirmed owner requirement

For each input record, process every cheque record returned by its Symcor request.

If one input record returns three cheques:

* All three enter the Tungsten processing flow.
* The output contains three cheque rows.
* Every row preserves the original input columns unchanged.
* Each row receives its own images, OCR values, confidence scores, and processing statuses.

Front and back are sides of the same cheque and belong in the same output row when their relationship is established by the native data.

Preserve failed and incomplete cheque rows. Preserve the same cheque under different input requests when both requests return it. Scope retry and replay duplicate prevention to the existing parent-and-child work identity.

The decision about which returned cheques to include is closed: include all of them. Do not use OCR names, amounts, confidence thresholds, or an assumed single-result Debit rule to discard results.

1. Complete the native Symcor integration and provenance

Inspect the supplied Java code, XML samples, WSDL/interface definitions, captures, and current adapter.

Establish the actual supported request parameters for Debit and Credit. Use documented account/date/indicator/identifier behavior; do not invent a mandatory ISN or unsupported filtering rule.

Process the complete response, including continuation or pagination if the native contract requires it.

Maintain traceability from:

* Source delivery, sheet, and input row
* To its Symcor request
* To every returned cheque/document
* To each available image side

Use the originating request and native response metadata to establish this relationship. An OCR-name match must not establish a real image-to-account association.

Preserve original account values and formatting-sensitive identifiers. Apply service-specific transformations only when supported by the native contract. Identify unresolved validation rules precisely instead of introducing silent normalization or rejection rules.

2. Complete front/back Tungsten processing

Reuse the corrected request builder and parser established by the successful live front-image call.

Process each available side of every returned cheque using the established Tungsten contract and current worker limits.

Use native document/page information or an explicit trusted declaration to pair images and establish page side. Preserve unresolved sides as visible outcomes.

Retain results separately by cheque and side until they are merged into the output. Apply any documented field-merging rules. If a rule is missing, preserve the side-specific results and surface the conflict rather than silently overwriting a value.

Keep these meanings distinct:

* Field returned and detected
* Field returned but not detected
* Field not returned by the provider
* Processing failed or remains unresolved

Do not assume the three bank-stamp fields will appear in a back-image response. Verify the response actually received.

Reuse saved captures for development and report generation. Use the smallest necessary authorized DEV calls to verify an untested native path, then retain the responses for replay. Do not make repeated provider calls solely to rebuild Excel.

3. Execute the supplied workbook and complete the output

Use the actual Test Data_TDB.xlsx and inspect both Debit Items and Credit Items. Verify current row counts; earlier reports of 5 Debit and 12 Credit rows are not hardcoded acceptance values.

Start with:

* One representative Debit record
* One representative Credit record returning multiple cheques
* A verified front/back pair where available

Then run the complete supplied workbook through the normal pipeline using the verified integration paths.

For every returned cheque, preserve a separate output row and its parent input association. Retain existing explicit zero-result handling. If Symcor itself fails before returning documents, record the input-level outcome without inventing cheque records.

Read the generated Excel file back programmatically and verify:

* Original input columns and identifiers are preserved.
* Output rows reconcile with returned cheques and explicit zero-result/error records.
* Images and OCR results belong to the corresponding cheque.
* Field values, confidence scores, and statuses match the recorded responses.
* Missing, failed, and unresolved records remain visible.

Do not assume the output must contain 17 or 41 rows. Derive its count from the actual results.

Report live, captured-response replay, and synthetic-association evidence separately. A demonstration fixture must not be described as verified processing of the original business records.

4. Verify and complete retry and recovery behavior

Use the focused retry inspection as the starting point.

Document the actual behavior for each Symcor and Tungsten operation:

* Retryable errors
* Maximum total attempts and additional retries
* Delay/backoff and timeout settings
* Behavior after retry exhaustion
* Checkpoints reused during resume
* Recovery procedure for a persisted FAILED item

Preserve item-level failure isolation and continuation. Keep delivery-wide faults classified appropriately.

Preserve the hold on UNKNOWN_OUTCOME. Do not blindly resubmit an ambiguous Tungsten request. Use a supported status or idempotency mechanism only where the native contract establishes one; otherwise document the concrete recovery procedure or remaining gap.

Using existing fixtures/captures and controlled fault injection, demonstrate:

* A committed successful stage survives interruption.
* Resume continues unfinished work without unnecessarily repeating committed work.
* One failed cheque does not silently remove it or unrelated cheques from the output.
* Repeating the same completed work does not create duplicate output.
* Separate input requests remain separately represented.

Reuse existing tests and add only meaningful coverage for uncovered behavior. Run focused checks while iterating, then the required release checks once the affected code is stable.

5. Produce and exercise the Linux DEV package

Keep workbook, image, output, state, and configuration paths parameterized through the existing configuration model.

Prepare the current release with:

* Dependency and runtime requirements
* Configuration examples
* Exact Linux setup and execution commands
* Writable output/state path requirements
* A reproducible sample/replay setup

Account explicitly for required files under gitignored test_data. Do not assume they will appear on another machine merely because the code was copied.

If the current environment provides access to the confirmed CLUE VMC2 DEV target, execute the packaged workflow there and verify that Excel is created in the expected location.

Use the existing server certificate configuration for the DEV run. Preserve the separately authorized laptop TLS setting, and report the verification mode actually used.

If DEV access or a specific external dependency is unavailable, complete the package, replay validation, commands, and other independent work. Report the exact missing prerequisite and the step it blocks. Do not claim a Windows or replay run as successful VMC2 execution.

6. Finish with reviewable delivery evidence

Update the current handoff, start-new-session instructions, interface notes, and open-items tracker.

Deliver:

* Source revision and package path/checksum
* Exact setup and run commands
* Generated Excel and supporting run-summary paths
* Counts of input records, returned cheques, processed sides, successful items, failed/unresolved items, and output rows
* Actual exit code and its explanation
* Validation performed against the delivered revision
* Which stages ran live and which used saved or synthetic data
* Remaining concrete blockers, their impact, and the smallest action needed to close each

Retain PARTIAL when the recorded outcomes warrant it. Distinguish implemented functionality, verified replay behavior, and verified live DEV behavior.

Scope

Keep ADIDO/TIBCO, AutoSys setup, operational Dynatrace onboarding, a new database platform, high-volume tuning, production rollout, and the existing credential-rotation deferral parked.

Continue using the existing architecture and worker limits. Preserve the other review session’s artifacts. Keep changes local under the established workflow; do not push or publish.

Proceed through the available work to produce the runnable package and inspectable outputs. Do not stop at another general plan or broad review.
