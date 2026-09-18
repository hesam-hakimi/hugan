Continue the current CLUE implementation session. This is an additive update to the workbook and Tungsten sample task already supplied; preserve and finish that work.

All engineering responses and artifacts remain in English.

A separate review session has reported additional failure-path findings. Incorporate the applicable findings into this implementation, without starting another general architecture review.

Keep application edits, tests, packaging and current handoff updates coordinated in this implementation session. Any parallel reviewer should inspect a defined source snapshot rather than modify the same application files.

1. Reconcile the review with current source

Locate and read the relevant CLUE_SOLUTION_REVIEW.md. There may be multiple historical review documents, so identify the report by its content and reviewed revisions.

The new report describes:

* R02: a permanent failure for one item aborts its delivery, leaves remaining items unattempted, and does not persist FAILED for the item.
* R03: backpressure admission/release is not balanced on exception paths.
* R04: exceptions escape without the controlled failure result and exit_outcome.
* R10: shared SQLite access/concurrency is a concern explicitly marked unverified.

The review mentions baseline c4fd22f and review HEAD d985047 while another session was editing. Compare its findings with the current checkout, including relevant uncommitted changes.

Finding numbers differ between reports. Identify findings by title and affected behavior. Do not reopen the previously corrected completion-marker and coordinator-renewal issues simply because an identifier is reused.

For each applicable finding, establish a focused reproducer on the current source before changing behavior. If already fixed, record the evidence and preserve the correction.

2. Repair item-failure handling

A definite, item-scoped permanent provider failure must persist the item’s terminal outcome and allow other independent eligible items to continue according to the existing policy.

Distinguish item-specific failures from delivery-wide or infrastructure failures, such as shared authentication/configuration problems, state-store failure or loss of ownership. Do not convert every exception into an item failure and continue blindly.

Preserve the established COMPLETE/PARTIAL/FAILURE semantics, restart behavior, source associations and Excel reporting. Failed items must remain visible rather than disappearing from the result or appearing successful.

3. Repair backpressure cleanup

Ensure each successful admission has exactly one matching release at the appropriate lifecycle boundary, including exception and early-exit paths.

Reuse the current abstractions. Avoid both leaked capacity and premature/double release.

Add a focused scenario demonstrating that a failure after admission does not prevent a subsequent eligible item from progressing.

4. Repair controlled CLI outcomes

Ensure failures at the appropriate command boundary produce the correct existing exit classification and a sanitized structured exit_outcome.

Preserve distinctions between configuration errors, item-level partial results and fatal run failures. Retain the existing interruption/recovery behavior.

An uncaught Python exception may already produce process exit code 1; verify the actual defect rather than assuming no failure code is returned. The requirement is consistent controlled status, reporting and exit behavior.

5. Handle the unverified concurrency concern proportionately

Inspect connection and lock ownership, including background lease-renewal access, and perform a bounded targeted check where feasible.

Do not report a demonstrated SQLite race or corruption without evidence.

If multi-worker operation cannot be verified within this bounded task, enforce workers=1 for the current DEV milestone and clearly reject unsupported higher values. Do not silently clamp the setting.

A single worker does not by itself prove all shared-connection access safe, because background threads may still use the state store. Address any concrete access defect found without introducing a broad redesign.

6. Finish the workbook/Tungsten task and validate the final revision

Preserve the supplied two-sheet workbook, configurable file/image/output paths, evidence-based image associations and isolated Tungsten test.

Keep expected metadata separate from observed OCR responses. A failure-path repair must not turn missing provider evidence into a claimed successful live integration.

Use focused regressions for:

* A multi-item input where an item-specific permanent failure occurs and the other eligible items still receive the correct processing and outcomes.
* Capacity recovery following an exception.
* Controlled CLI failure and partial-result reporting.
* Any concurrency constraint or small concurrency fix introduced.

After these repairs and the workbook/Tungsten implementation are complete, run the appropriate existing full suite once against the final source, verify the generated .xlsx output, and rebuild the local release package as needed. Repeat checks only when further changes or failures justify them.

Update the current handoff with the final source revision, actual test results, working commands, output locations, live-versus-fixture evidence, concurrency limitations and remaining concrete blockers.

Do not automatically expand into the review’s proposed Stage 2 list. Address an item there only if it directly blocks this scoped core execution. Keep the owner’s parked Dynatrace and deferred credential-replacement decisions unchanged.

Complete applicable corrections and verification, then report which findings were reproduced, already fixed, corrected or still unverified.
