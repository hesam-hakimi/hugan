Continue CLUE development through completion of the local delivery candidate.

Owner decision: park live Dynatrace onboarding, the VMC2 collection-route decision, DEV destination configuration and live ingestion verification. Keep these recorded as external operational dependencies. They must not block the remaining development.

Preserve the existing structured local logging, TD logger integration and valid tests. Use an explicit configuration setting to disable live forwarding while it is parked. Disabled forwarding must be reported accurately and must not prevent application startup or processing.

All development responses, code, tests and documents must remain in English.

1. Reconcile the current implementation and finish the remaining scope

Read the current handoff and inspect the actual checkout, including newer changes and active-session ownership.

The latest reported baseline is 187 passing tests, but use the actual current source and evidence. Reuse completed work and existing tests. Identify the remaining implementation tasks from the handoff and recent instructions, then proceed directly with them.

Resolve routine implementation choices within the existing authority. When an external input is unavailable, record the specific dependency and continue independent work.

2. Close the remaining queue and execution correctness gaps

Use the existing single-host architecture and durable state.

Verify and complete only the behavior that remains unimplemented or unproven:

* A healthy operation continues beyond the configured lease duration without another invocation taking over its work.
* A stopped or crashed owner can be recovered appropriately.
* Overlapping invocations cannot multiply the effective provider limits for one deployment.
* Actual orchestration uses the intended bounded concurrency and can pass committed Symcor results downstream while respecting Tungsten capacity.
* Retry waiting, held outcomes, newly arriving files and backpressure remain correct through interruption and restart.

Prefer the simplest reliable ownership model. One active processing coordinator per deployment state directory, with bounded provider workers inside it, is acceptable if it meets the existing requirements. Reuse an equivalent working mechanism if one already exists.

A second invocation must have a clear outcome, preserve pending work and avoid duplicate processing. Document the supported deployment model.

Use controlled clocks and bounded fake providers for missing behavioral tests. Distinguish concurrency, requests per second and records per request. Treat unconfirmed provider limits as unconfirmed.

3. Complete the remaining adapter and data-processing work

Reconcile the earlier image, fault-policy and acceptance refinements against the current source. Complete actual remaining gaps, including:

* Supported image decoding/conversion, front/back association and explicit handling of unsupported or ambiguous image formats.
* SOAP fault classification and retry decisions based on available contract evidence.
* Preservation of source-row/document associations, partial results and completed page checkpoints.
* One logical output per input delivery, with accurate processing and delivery status.

Finish the getCriterionRules task already assigned in the handoff if it is still pending. Use the available WSDL/XSD and documented operation through the existing Symcor adapter, limiter and fault handling.

Label schema-derived fixtures accurately. Do not invent TransitBankAcct composition, resolve the timeStamp contradiction by assumption, or impose an unsupported debit/credit cardinality rule.

Keep unresolved business output mappings explicit in the runnable candidate.

4. Preserve clear integration boundaries

Missing Dynatrace configuration is now a parked item.

Symcor/Tungsten DEV validation can proceed if the actual required configuration and permitted test inputs are available within the existing authority. Otherwise complete the callable adapters and offline verification, recording the exact missing provider inputs.

Keep these statuses distinct:

* Implemented.
* Verified with offline fixtures.
* Verified against a real DEV provider.
* Accepted by the business.
* Verified on VMC2/AutoSys.

Preserve the effective owner instructions already recorded in the handoff.

5. Produce the final local release candidate

After the implementation changes:

* Run targeted tests during development and one full regression pass on the final source.
* Reuse the existing multi-file acceptance fixtures and the bulk scenario where applicable.
* Verify duplicate delivery, interruption/resume, partial or held outcomes and output correlation through the actual application entry point.
* Build the release from the intended package contents.
* Extract it into an isolated directory and verify the documented execution path.
* Record the runtime, dependencies, source revision, package checksum, commands and acceptance outputs.

Broaden testing only when changes, failures or unresolved concerns justify it.

6. Complete the handoff and delivery report

Update the existing handoff and startup prompt with:

* Completed functionality and supporting evidence.
* Exact release location and instructions for running it.
* Current ownership and source state.
* Remaining external dependencies, with the evidence needed to close each.
* The next integration or deployment action when those inputs arrive.

Keep live Dynatrace explicitly parked. Identify any remaining local development work honestly.

Create the appropriate local commits within the current authority. Preserve unrelated work and active-session boundaries.

Continue through implementation, verification, packaging and handoff. The requested outcome is a reproducibly executable local delivery candidate, not another plan or findings-only report.
