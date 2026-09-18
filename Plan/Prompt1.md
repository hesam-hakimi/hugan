Owner clarification — process and display every cheque returned by Symcor.

Treat this as a confirmed requirement and update the implementation, tests, and handoff accordingly.

For each input record, process every cheque record returned by its Symcor request. If one input record returns three cheques, all three must enter the Tungsten processing flow and produce three output rows.

Implementation requirements:

1. Preserve every original input column, unchanged, on each resulting output row. Append the corresponding cheque images, OCR values, confidence scores, and processing statuses. Keep source input values separate from extracted values.
2. Preserve the parent request association throughout processing. Each returned cheque must remain traceable to the input record and Symcor response that produced it. Do not select or discard returned cheques using OCR names, amounts, confidence thresholds, or an assumption that Debit can return only one cheque.
3. Under the existing output layout, front and back belong to the same cheque’s output row. Process available sides according to the established Tungsten contract. Three cheques with two sides each still produce three output rows.
4. Preserve output rows when individual cheque processing fails. Record the appropriate status and retain any successfully obtained image or OCR results. An item failure must not silently remove that cheque from the output. Retain existing delivery-wide error handling where applicable.
5. Preserve the same cheque under separate input requests when both requests return it. Scope retry/replay duplicate prevention to the existing parent-and-child work identity.
6. Use the existing queue, worker limits, state store, and output writer. Keep existing zero-result handling explicit. Standalone sample images must retain their declared demo or verified association status.

Verify this with focused behavioral cases, reusing existing tests where possible:

* One input returning three cheques produces three enriched rows.
* One failed cheque still leaves three output rows with accurate statuses.
* The same cheque returned under two input requests remains represented under both.
* Replaying the same completed work does not add duplicate output rows.
* Front and back enrich the same cheque row.

Update the open-items tracker: the decision to return all cheque results is closed by the owner; implementation and verification status must be reported separately.

Continue the current core work, preserve parked infrastructure items, and report the output artifact and any remaining concrete implementation gap.
