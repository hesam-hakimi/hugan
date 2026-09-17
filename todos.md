Continue the current CLUE implementation in C:\repos\fcrm_clue on feature/clue-durable-core.

The owner’s priority is now delivery of the runnable project. Credential rotation/replacement is deferred. Continue with the existing configuration and previously authorized DEV scope. Do not spend this run repeating credential scans, rotation instructions, or requests for rotation confirmation.

Use the reported checkpoint bea1f4e and 92 passing offline tests as context. Inspect the actual current HEAD and working tree, preserve subsequent changes, and continue from the existing implementation.

All responses, code, tests, documentation, and commands must be in English. Use text and filesystem tools only.

Target deliverable

Deliver an executable CLUE batch application that accepts multiple input files, runs the existing Symcor/Tungsten processing flow, and produces a separately correlated output for each input file. Include a reproducible acceptance run, inspectable outputs, installation/run instructions, and a packaged local release candidate.

Proceed autonomously through the work that the available source, configuration, and environment support. Keep external dependencies specific to the affected integration and continue the remaining delivery work.

1. Finish the supported Symcor adapter path

Read the WSDL and schema in Appendices B and C and any corresponding native files already present. Use the existing extracted specifications and helpers.

Resolve and implement the supported SOAP operations, namespaces/actions, request and response element names, search criteria, hit-list interpretation, document retrieval, page identification, and image decoding.

Apply the findings already established from native sources: operator mappings, AvailableSegments bitmask behavior, hit-list limits, and processing date plus ISN as the documented item identity within its provider context.

Check whether a documented Account-based search profile can work without constructing an unresolved TransitBankAcct value. Implement supported profiles where all required details are known. Keep remaining ambiguities localized to the affected profile.

Use the schema to resolve structural questions such as docsFetchLimit naming where possible. Do not assume that WSDL alone resolves timestamp semantics or routing/account composition.

Reuse the current code and fixtures. Complete the callable adapter and its wiring rather than ending with another findings-only report.

2. Complete one application path from intake to output

Connect the existing intake, durable state, Symcor adapter, Tungsten stage, and output writer through one runnable batch command.

Use that same orchestration path for offline fixtures and configured DEV providers. Record which provider mode supplied each result.

Support multiple timestamped input files, each with its own delivery identity and corresponding output. Preserve source file, source row, case/request association, provider document identity, processing date, and front/back page role.

Repeated account/date values across files or cases must retain their original associations. A credit row may return multiple cheques.

Keep the existing page-level durability and held-unknown-outcome behavior. Preserve the existing SQLite implementation while recording its operational acceptance separately from the local release candidate.

3. Make the output useful for review

Use the existing business samples and field definitions wherever they provide evidence. Preserve the original input fields and append or associate the agreed image and metadata results.

Where the physical business format is unresolved, provide an explicitly named provisional output profile with an inspectable sample. Keep that uncertainty separate from the working processing pipeline.

Produce one logical output per input file, including referenced image assets when needed and a machine-readable processing summary.

Distinguish completed extraction, no matching document, missing/blank extracted fields, failed processing, and unresolved provider outcomes. Preserve useful partial results.

Inspect the current “front values win” merge behavior. Treat page precedence as an explicit mapping decision supported by evidence. Preserve page-specific values and surface conflicts when no agreed precedence exists.

Keep test/provisional extraction status visible in the acceptance artifacts.

4. Finish file lifecycle behavior

Reuse the existing delivery registration, duplicate handling, and archive logic.

Start processing only after the configured completion signal. For the local acceptance run, supply the corresponding marker/manifest or other explicitly supported completion mechanism. Document that the actual ADIDO/TIBCO handoff contract remains an external configuration decision.

Return each output when its batch reaches the applicable terminal state. Preserve the relationship between the input, output, and processing status.

Archive according to processing and delivery state. A date change alone must not remove unfinished or undelivered work from recovery.

Provide configurable retention settings and document their operational requirements. The meeting’s 500 GB figure is a planning input, not evidence of available capacity.

5. Use available DEV integration without restarting the credential work

Continue loading C:\repos\FCRM.env through the explicit –env-file option and the existing aliases.

The owner has deferred credential replacement. Adjust any assistant-added rotation-confirmation prerequisite so it does not block the otherwise authorized DEV component test solely because rotation was deferred. Do not falsely set –confirm-credentials-rotated or report that rotation occurred. Preserve ordinary secret handling.

Resolve Tungsten Config/sessionId settings from available authoritative artifacts. If actual values or semantics remain unavailable, report the exact missing input once and continue the rest of the delivery work.

When the required settings, permitted sample image, identifiers, and DEV endpoint are available, execute one bounded Tungsten component request using the configured credential. Separate transport success, provider/job outcome, and extraction interpretation.

Create the required local capture directory and configure its access as part of setup rather than repeatedly stopping because the directory does not exist.

Keep each live provider within the already authorized environment. Do not infer Symcor connectivity from the earlier PAT TCP result or silently change environments.

6. Run a concrete acceptance demonstration

Reuse existing fixtures and tests. Prepare at least two input files covering a debit case and a credit case with multiple documents, including repeated account/date values across distinct requests.

Demonstrate:

* A separate correlated output for each input file.
* Correct document/page and source-row associations.
* An interrupted run that resumes remaining work using committed results.
* A duplicate-delivery rerun that reuses completed work.
* Clear handling of partial and unresolved results.

Use existing recovery coverage where it already proves the behavior. Add targeted tests only for new integration behavior or defects discovered during this work.

Run the relevant checks and existing regression suite once after the implementation changes. Keep the reported validation tied to the tested code.

7. Package and hand over the runnable project

Use the repository’s existing packaging and dependency conventions.

Produce a local release candidate with the application, dependency manifest, configuration example, synthetic acceptance inputs, and concise instructions for installation, execution, restart, output inspection, and troubleshooting.

Include Windows development instructions and the intended RHEL 9/VMC2 execution requirements. Report Linux execution as verified only if it actually runs in that environment.

Keep the existing local logging operational. Document the remaining Dynatrace destination/package setup as a separate integration item.

Build the package from an explicit set of release files, excluding local credentials, private captures, virtual environments, and unrelated workspace contents.

Validate the packaged entry point from an isolated extraction location where practical. Record the resulting commit and artifact paths, keeping the work within the existing local publication scope.

Final report

Lead with what can now be run and what it produces. Include:

* The exact batch command.
* Actual paths to the package, sample inputs, and generated outputs.
* The demonstrated input-to-output behavior.
* Which providers used fixtures and which were exercised live.
* Validation results and the tested commit.
* A short list of the external inputs still required for deployment or live end-to-end acceptance.

If independent work can run in parallel, divide provider work, output/lifecycle work, and packaging documentation into non-overlapping tasks, then integrate and validate the resulting application.

Continue through implementation, acceptance execution, and packaging. Do not stop after a plan or another list of possible next steps.
