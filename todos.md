Continue from the successful live Tungsten result and focus on completing the core input-workbook-to-output-workbook flow.

1. Read back the generated sample workbook programmatically and compare it with the saved live response. Confirm that the image, extracted values, confidence scores, and detected / returned-but-undetected / not-returned statuses are preserved correctly. Reuse the saved capture; do not call Tungsten again just to regenerate or inspect Excel.
2. Integrate the corrected Tungsten response handling into the normal workbook pipeline using the existing components. Select one real input row and its explicitly associated cheque image. Resolve that association from the available sample files and metadata. Do not invent a relationship from filename or row order, and do not apply one sample’s OCR result to unrelated rows.
3. If the row-to-image association is missing, complete the independent integration work and report the exact missing association needed to finish the example. Keep front and back results separate unless their pairing is established.
4. Produce one normal-pipeline Excel output demonstrating that the selected input row retains its original data and receives the corresponding OCR results and field statuses. If this run replays the saved live response, label it clearly as a replay; do not describe it as a new live end-to-end run.
5. Run focused checks for the integration changes and update the handoff with the output path, source revision, evidence, and remaining core gaps. Keep the parked infrastructure items and credential-rotation deferral parked. Do not start another broad architecture review or push changes.

Report what is now complete in the core workflow and the smallest remaining step needed to finish it.
