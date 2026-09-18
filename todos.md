Continue the current CLUE session from the latest corrected source and handoff.

The reported revision 24c17b6 passed 240 tests and closed the three failure-path findings. Accept that as the reported local baseline. Preserve the single-worker boundary and existing recovery behavior.

The next task is one isolated, real Tungsten DEV sample execution using the supplied configuration and cheque images.

All responses, code comments and documentation remain in English.

1. Reconcile the existing configuration

Inspect the current Tungsten runner, configuration resolver, native request example and relevant handoff notes.

The owner previously supplied configuration at:
C:\repos\FCRM.env

Repository:
C:\repos\fcrm_clue

Determine which configuration file the previous check-config invocation actually loaded. Check the established resolution order and existing variable-name mappings before declaring anything missing.

Reconcile:

* The Tungsten DEV base URL.
* Primary/secondary key selection and the supplied credential variable names.
* Config/process configuration.
* sessionId and its required lifecycle.
* Any other mandatory request values evidenced by the current native contract.

Use existing inspection helpers where available. Report configuration names, presence, source and validation status without printing secret values.

The owner’s decision to defer credential replacement remains in effect. Do not reopen a rotation campaign or claim rotation occurred. Distinguish an old local preflight restriction from an actual provider authentication rejection.

Do not describe a key as rejected by Tungsten unless an actual provider response supports that conclusion.

2. Resolve one usable image sample

Inspect:
C:\repos\fcrm_clue\test_data\test_cheques

Use the actual current files and the accompanying metadata/transaction CSVs. The last inventory included front.jpg, front (2).jpg, back.jpg, back2.jpg and cheque_003.jpg.

Choose one image for which the required page type and request values can be established. Record the source of those associations.

This isolated OCR test does not require a confirmed connection to a row in Test Data_TDB.xlsx, and it does not require Symcor to run first.

Determine from the native contract whether document/ISN fields require existing provider-recognized identifiers or are caller-supplied correlation values. Do not assume either interpretation or invent provider resource identifiers.

Do not guess front/back pairings. A supported single-image request is sufficient for this first execution.

3. Prepare and execute one bounded DEV request

Use the existing Tungsten adapter and component runner. Correct only the configuration binding or request preparation that is demonstrably necessary.

Once the required values and sample are usable, execute one bounded real request with the existing authorized DEV configuration.

Preserve TLS verification and the existing handling of authentication errors and ambiguous outcomes. Do not blindly repeat a submission after a timeout or switch keys automatically following an authentication rejection.

Record separately:

* The execution environment.
* Whether a request was actually sent.
* HTTP/transport outcome.
* Provider processing outcome.
* Whether actual OCR fields and confidence values were successfully parsed.

Preserve the native response locally through the existing handling path without dumping credentials, image payloads or sensitive document content into general logs or chat.

If the real response reveals a parser mismatch, use that response to make a focused correction and regression test. Do not substitute expected values from the sample CSV.

4. Produce a small, clearly identified Tungsten test result

If actual extraction succeeds, generate a small standalone .xlsx test output containing the original sample image and the actual extracted fields, confidence values and sample association.

Keep this output clearly identified as the isolated Tungsten test. Do not mix it with simulated workbook results or claim that the full workbook/Symcor integration has passed.

Verify that the generated workbook can be reopened and that its content corresponds to the recorded provider response.

5. Complete independent work if a genuine blocker remains

If a required value cannot be found or a connection cannot be established, finish configuration discovery and request preparation first.

Then report only:

* The exact missing or invalid field, or observed connection/authentication failure.
* The configuration and reference sources already checked.
* What evidence is needed to resolve it.
* Which command is ready to run afterward.

Do not ask the owner again for supplied files or information already available in the source.

6. Keep validation proportional and update the handoff

A configuration-only change or component execution does not require another complete architecture audit or full regression cycle.

For any code change, run focused relevant tests and repository-required checks, clearly identifying which revision they validate. Rebuild the package only if application code changes require it.

Update the current handoff with the actual configuration resolution, runnable command, output paths, live result or precise blocker, and execution environment.

Keep this task focused on obtaining and correctly interpreting the first real Tungsten response.
