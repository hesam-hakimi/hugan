Perform one comprehensive review of the current CLUE solution and its local delivery candidate.

The purpose is to assess the implemented solution, identify concrete defects and material risks, and recommend prioritized corrections and improvements.

This is a review and reporting task. Inspect the implementation and use appropriate verification, but do not automatically implement fixes or refactor the application during the review.

All responses, reports and technical content must be in English.

1. Establish the exact review baseline

Locate the current application repository and handoff. Previously recorded paths are:

* C:\repos\fcrm_clue
* C:\repos\FCRM
* C:\repos\fcrm_clue\docs\handoff\clue

Read CLUE_HANDOFF.md, START_NEW_SESSION.txt, the relevant reference documents, operator instructions and the actual source.

Record:

* Repository, branch, HEAD and review timestamp.
* Relevant uncommitted changes.
* Release artifact path and SHA-256.
* Runtime and dependency versions.
* The source state covered by existing test and acceptance evidence.

The latest report described 204 passing tests and successful execution from an isolated release extraction. Reconcile that report with the current files; do not assume it proves behavior that was not exercised.

Respect active-session ownership. If source changes during the review, keep findings attributable to the reviewed version and identify any affected conclusions.

2. Trace the real application path

Follow the executable entry point through:

* Configuration loading and validation.
* Incoming-file discovery and completeness checks.
* Delivery registration and ownership.
* Input parsing and record validation.
* Symcor request construction and response handling.
* Image extraction, decoding/conversion and storage.
* Tungsten submission and result handling.
* Durable checkpoints, retry waiting and held outcomes.
* Output construction, publication, acknowledgement and archiving.
* Logging, shutdown and exit outcomes.

Verify that important components are actually called from the application path. A helper existing in the repository or passing an isolated unit test is not sufficient evidence of integration.

Explain the implemented flow clearly and identify any meaningful difference between the documentation, intended design and actual behavior.

3. Review correctness, recovery and concurrency

Assess:

* Atomic state transitions and consistency between stored state and filesystem artifacts.
* Lease renewal, ownership fencing and recovery after a crash.
* Competing invocations and the scope of the single-coordinator guarantee.
* Duplicate delivery handling while preserving legitimate repeated investigations.
* Stable delivery, source-row, document and page identities.
* Persisted retry timing and behavior after restart.
* Ambiguous provider outcomes, including acceptance followed by a lost response.
* Front/back partial completion and reuse of committed results.
* Arrival of new files while processing is active.
* Graceful interruption and bounded shutdown.
* Crashes between output creation, publication, acknowledgement and archive movement.

Use realistic failure scenarios. Check what would actually happen, what evidence supports the conclusion and whether the behavior matches the stated contract.

4. Review provider and data contracts

Assess the Symcor SOAP/XML/MTOM/XOP path, request parameters, attachment association, fault handling, getCriterionRules discovery and caching.

Assess image validity, format handling, page association and resource usage.

Assess the Tungsten request/response boundary, configuration requirements, metadata mapping, confidence handling and partial or unknown outcomes.

Review:

* Input validation and communication of rejected records.
* Debit/credit multiplicity and source-row attribution.
* Preservation of all returned document associations.
* One logical output per input delivery.
* Output schema, image representation and reconciliation.
* Schema-derived fixtures versus captured native provider evidence.

Keep unresolved business rules and unavailable provider evidence explicit. Do not invent account normalization, TransitBankAcct composition, timeStamp semantics, debit/credit cardinality or approved output mappings.

Classify an unresolved contract as an external dependency or risk unless there is evidence of a specific implementation defect.

5. Review performance and resource control

Assess:

* Actual provider concurrency in the orchestration path.
* Independent Symcor and Tungsten limits.
* The distinction between in-flight requests, requests per second and records per request.
* Downstream backpressure and pending-work behavior.
* Memory usage for XML, Base64 data, images and output construction.
* Disk growth, staging limits, temporary files and cleanup.
* Retry amplification, fairness and the possibility of work remaining indefinitely pending.

Use the available workload assumptions and mark uncertain quantities. Do not invent a provider limit or processing SLA.

Distinguish configured concurrency from observed parallel execution. Offline timings do not establish real provider latency or production capacity.

Recommend the smallest practical improvements that address demonstrated bottlenecks or material risks.

6. Review operational readiness and maintainability

Assess:

* Configuration precedence and initialization timing.
* Windows-specific assumptions and compatibility risks for RHEL/VMC2.
* Local state storage, paths, permissions and deployment assumptions.
* AutoSys exit semantics and scheduling integration boundaries.
* Structured logging, correlation, redaction and failure isolation.
* Package contents, dependencies, reproducibility and documented execution.
* Whether the extracted release is complete and consistent with the reviewed source.
* Module responsibilities, duplicated logic, excessive coupling and difficult-to-test boundaries.

Review concrete configuration, parser, file-handling and logging behavior that could affect reliability or expose sensitive information. Keep sensitive values out of the report.

Preserve the owner’s decisions:

* Live Dynatrace onboarding and validation are parked.
* Credential replacement remains deferred.
* Local implementation and offline validation are distinct from live integration, business acceptance and production readiness.

Do not reopen those decisions as new approval campaigns.

7. Evaluate the quality of the evidence

Review existing tests and acceptance artifacts for meaningful coverage.

Look for tests that:

* Exercise only helpers while bypassing the real entry point.
* Mirror the implementation without verifying the intended behavior.
* Use unrealistic fixtures that hide integration problems.
* Omit consequential failure boundaries.
* Make stronger claims than their assertions support.

Reuse valid results from the reviewed source. Run focused checks or a small isolated reproduction when necessary to resolve a material concern. Do not repeat the full suite solely to reproduce an unchanged passing count.

Temporary reproduction artifacts may be created outside the application source. Record the commands and relevant sanitized results. Keep application code unchanged during this review.

A failed assertion or a suspected issue must be investigated enough to distinguish a real defect from an incorrect test assumption.

8. Produce actionable findings

For each finding, include:

* A unique ID.
* Classification: confirmed defect, material risk, evidence gap, external dependency or optional improvement.
* Severity and recommended priority.
* Source location, including file and function, with line references where useful.
* Triggering scenario and actual or expected impact.
* Supporting evidence and confidence level.
* Proposed correction or improvement.
* A focused way to verify the correction.
* The recommended delivery stage for addressing it.

Use precise wording:

* “Confirmed” requires supporting evidence.
* “Potential” must explain the assumptions.
* “Not verified” must not be presented as “not implemented.”
* “External dependency” must identify the missing input and what it prevents.

Include strengths worth preserving. Avoid cosmetic recommendations unless they materially affect correctness, maintainability or delivery.

9. Deliver one comprehensive report

Create:

docs/handoff/clue/CLUE_SOLUTION_REVIEW.md

The report must contain:

* An executive assessment of the current candidate.
* The reviewed architecture and executable flow.
* Strengths and verified capabilities.
* Prioritized findings with evidence.
* Test and acceptance coverage gaps.
* A practical correction/improvement plan.
* Remaining external integration and deployment dependencies.
* An evidence appendix with the reviewed revision, commands and artifact locations.

The correction plan must separate:

* Necessary local fixes before accepting the candidate.
* Work required before real integration or deployment.
* Improvements that can reasonably follow the initial delivery.

Use roles rather than assigning people by name. Identify dependencies between recommended actions.

Conclude whether the current candidate is suitable for a local demonstration and the next integration stage, and explain any conditions. Do not equate that conclusion with production approval.

10. Finish the review

Return:

* The actual report path.
* The overall assessment.
* The most important findings.
* The recommended order of corrections.
* Whether any local development remains necessary before proceeding.

Complete this review once all areas above have been assessed and material findings have adequate evidence. Provide the corrections as recommendations; do not start an unrequested remediation cycle.
