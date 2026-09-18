Continue the active CLUE development session and apply the following two owner updates to the current implementation, tests and handoff.

All responses, code comments, reports and documentation in this development environment must remain in English.

Continue from the current checkout and latest handoff. Preserve existing work and reuse the current configuration, adapters, component runners and processing controls. The previously reported 214 passing tests are a historical baseline, not evidence that the new Excel behavior is already implemented.

Our current scope is the core application: read supplied local data, process it, and generate Excel output locally. ADIDO/TIBCO integration, AutoSys, live Dynatrace onboarding and production deployment remain outside this task. The owner’s decision to defer credential replacement remains in effect.

1. Use the supplied files

Repository:
C:\repos\fcrm_clue

Workbook:
C:\repos\fcrm_clue\test_data\Test Data_TDB.xlsx

The owner confirms that this workbook contains one debit sheet and one credit sheet. Read the actual workbook to discover the exact sheet names, headers, cell types and records.

Cheque sample directory:
C:\repos\fcrm_clue\test_data\test_cheques

Files visible in that directory:

* cheque_001.jpg
* cheque_002.jpg
* cheque_003.jpg
* test_cheques_metadata.csv
* test_transactions_3_cheques.csv

Verify these files through the filesystem. Read the workbook and CSVs programmatically. Inspect image format and dimensions programmatically as needed. Use text and filesystem inspection for the engineering work, without screenshots or UI automation.

Do not ask the owner again for information available in these files.

These are Windows source locations. Do not report them as files already deployed or tested on the Linux DEV server.

2. Update workbook ingestion and parameterize paths

Inspect the existing configuration and command interfaces first. Add or reuse configurable paths for:

* The input workbook.
* The cheque sample directory.
* The output directory.

Keep existing conventions and document how relative paths are resolved and which configuration source takes precedence. Paths containing spaces must work. Windows-specific sample paths must not be embedded in application logic or become mandatory Linux paths.

Read both debit and credit sheets through the existing processing pipeline. Preserve:

* Original input values and columns.
* Identifier text and leading zeros where present.
* Source file, sheet and row associations.
* Existing duplicate handling, durable state and restart behavior.

Rows at the same position in different sheets must remain distinct. Do not invent account-number normalization or new business validation rules from a single sample.

For this manually supplied file, use or implement an explicit local-file execution path with the existing processing controls. This test must not depend on an upstream ADIDO completion file. Preserve the established validation behavior of the production arrival path.

3. Produce and verify actual Excel output

The previous release demonstrated CSV output. Inspect the current code and implement any missing .xlsx import/export capability using the existing adapter structure.

Use the supplied workbook and current references to determine the output layout. Prefer preserving debit/credit separation and original fields, then adding the relevant document identifiers, extraction results, confidence values and processing status.

Preserve traceability when one input row produces multiple documents. Missing images, failed extraction and unresolved associations must remain explicit rather than silently disappearing.

If a layout choice is not specified in the available references, use a clearly documented provisional DEV layout that the owner can review.

Reuse the original saved cheque images for workbook display or references. Where image association is confirmed, the provisional DEV output may embed those images. Do not depend on Tungsten returning image bytes.

Verify that the generated file is a real .xlsx workbook that can be reopened and that its sheets, values, associations and any embedded images are present.

4. Exercise Tungsten independently using the supplied images

Use the existing Tungsten adapter and component runner. This component test does not require Symcor to be available.

Read both CSV files and current references to identify the images, page sides and document/transaction associations. Do not infer that cheque_001.jpg and cheque_002.jpg are front/back pairs simply because their names are consecutive.

Do not assume these images belong to rows in Test Data_TDB.xlsx. If that relationship is not evidenced, keep the image-based Tungsten test separate from the workbook integration result.

Treat supplied expected metadata as reference data. Never substitute it for a live OCR response or report fixture values as provider-extracted results.

Inspect the current native request example, adapter and configuration. Reuse the existing configured DEV endpoint and credentials. Earlier reports mentioned unresolved Config/sessionId values; check the current state before treating them as missing. Do not guess provider identifiers or copy the API key into unrelated request fields.

When the required configuration, sample identity and connection are usable, run a bounded real Tungsten DEV test through the existing runner:

* Start with one image whose page side is established.
* Process its matching opposite side only if that association is established.
* Follow the actual request contract for page submission.
* Preserve the response and its association with the image and document.
* Distinguish HTTP success, provider processing success and successfully parsed extraction fields.
* Handle an ambiguous submission outcome through the existing recovery behavior rather than blindly submitting again.

A captured native response can resolve the remaining response-schema uncertainty. Inspect it and update the parser/mapping only where the evidence supports the change.

If a required value or association is genuinely missing, report the exact missing item and continue all independent implementation and offline verification. Do not stop the whole task at a generic “external dependencies pending” statement.

Keep credentials out of logs, reports and command-line arguments.

5. Verify the changes and update the handoff

Reuse existing test utilities. Add focused coverage for the changed behavior, including:

* Configurable paths, including the supplied filename containing a space.
* Reading both workbook sheets and preserving their separate row identities.
* Correct image/transaction associations, including an unresolved association.
* Real .xlsx generation and readback.
* Any response-parser change supported by the Tungsten test.

Run the relevant existing regressions and, after implementation changes are complete, run the appropriate full suite once against the final source revision. Repeat only if subsequent changes or failures justify it.

Update the current handoff, development tasks and relevant interface notes. Record:

* The supplied file locations and discovered structure.
* The actual configuration options and runnable commands.
* What changed in the implementation.
* Generated output paths and verification results.
* Which results used fixtures and which used real Tungsten responses.
* The machine/environment where each execution occurred.
* Only the remaining concrete blockers or output decisions.

Remove stale statements that no workbook or cheque samples have been supplied.

Preserve the owner’s original sample files. Do not automatically publish sample data or provider responses. Rebuild the existing local release package if its application code changed.

Complete the implementation and verification that are possible with the supplied files, then return a concise delivery report. Do not end with only a plan.
