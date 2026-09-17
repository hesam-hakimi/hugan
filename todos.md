Continue from the current CLUE local release candidate and preserve the reported 128-test baseline, packaging, and acceptance workflow.

Complete these three focused delivery refinements using the existing implementation and dependencies:

1. Finish the image conversion path

JPEG conversion is already within the delivery scope. Implement the required TIFF-to-JPEG path instead of stopping at IMAGE_FORMAT_REQUIRES_CONVERSION.

Use valid, decodable test images. Verify JPEG pass-through and TIFF conversion by decoding the result, checking dimensions, and preserving document/page identity. Treat signature-only or “JPEG-framed” test bytes as insufficient evidence of a usable image.

Handle supported multi-page inputs explicitly without silently selecting or dropping pages. Report only genuine target-environment dependency constraints.

2. Correct the Symcor retry classification

Inspect the current awsSystemException → TRANSIENT mapping. Use documented subcodes/conditions or an explicit operation-specific retry policy. Do not present the entire category as proven transient.

Keep attempts bounded and preserve fault details in the existing safe error model. Retain the established handling of uncertain Tungsten outcomes.

3. Align the acceptance fixture with debit/credit behavior

Inspect the –docs-per-item 2 seed, generated associations, and reported debit counts before changing code.

Demonstrate one cheque per successful debit row and multiple cheques for the credit scenario, while preserving repeated-case associations and ineligible rows. If a debit query unexpectedly returns multiple documents, expose that outcome explicitly rather than silently selecting one.

Reuse existing tests and add only the coverage needed for these changes. Run the relevant regression suite once after implementation, rebuild the local release candidate, and validate its entry point and acceptance outputs from an isolated extraction.

Keep the native multipart profile marked as awaiting provider evidence until actual response fields and attachment mapping are confirmed. Missing Java helpers should not stop these independent refinements.

Keep credential replacement deferred as instructed. Finish with the rebuilt package path, actual output paths, demonstrated image conversion, corrected debit/credit counts, retry policy, and the precise external inputs still needed for the first connected tests.
