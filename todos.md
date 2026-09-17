Continue implementation in TD-Universe/fcrm_clue with the scope below. This answers your three pending questions together.

My instruction to implement the solution changes the earlier advisory-only scope for this bounded development checkpoint. Record that change in the working checkpoint, preserving the historical baseline. Proceed autonomously with routine source inspection, checkout, branch creation, implementation, local commits and synthetic verification. Do not repeatedly ask for those decisions.

1. Workspace and source

Locate an existing checkout of TD-Universe/fcrm_clue first. If the current workspace contains only the documentation pack and no suitable checkout exists, clone the repository into a separate sibling directory using the existing authorized GitHub access. Preserve the copied references and all user changes.

Report the actual repository path, remote, branch and inspected commit SHA. Use a suitable feature branch.

Trace the CLI entrypoints, imports, configuration, tests and any scheduler wrappers to identify the executable pipeline. Explain the selected implementation path with source evidence. Preserve the other copies during this checkpoint; do not delete or quarantine them merely because they appear duplicated. Avoid introducing another competing pipeline.

2. Implementation scope and deliverable

Implement Waves 0–5, plus the packaging and synthetic integration needed to demonstrate the result. Continue beyond Waves 0–2 without another routine approval checkpoint.

Deliver one runnable local flow:

complete synthetic input → validation and admission → simulated Symcor retrieval → simulated Tungsten extraction → explicit source/document associations → reconciled output → simulated delivery acknowledgement.

Use clearly named synthetic contracts and fixtures. Keep them separate from live provider and business contracts. Unsupported live configurations must fail clearly without guessing fields, identifiers, authentication, matching rules or output formats.

Implement durable progress, duplicate-delivery handling, atomic work ownership, restart/resume, bounded retries, ambiguous-outcome handling, bounded staging/backpressure and structured redacted logs.

Keep persistence behind an interface. Provide a durable local implementation suitable for the demonstrated concurrency, document its guarantees and limits, and avoid making an external database a prerequisite. Local verification does not establish that the persistence choice is approved for VMC2.

3. Evidence and corrections

Verify the reported defects against complete source files at the recorded commit before fixing them.

Do not treat five output columns as proof that eight metadata/confidence pairs cannot be represented: inspect the JSON contents and the consumer contract.

Moving zfill(14) into configuration does not resolve an incorrect mapping from a bare account to TransitBankAcct. Keep unresolved identifier construction explicit.

Remove secret-bearing command arguments and unnecessary sensitive diagnostic payloads. Preserve protected intermediate artifacts required for recovery. Distinguish application-readable files from evidence about storage encryption.

Treat the reported successful Tungsten DEV request as attributed evidence until its exact request, environment and result are available. Do not equate a synthetic pass with a live integration pass.

4. File-transfer boundary

Carry forward Amber’s statement: “Tibco cannot pull from Adido they will have to be pushed from that server.”

The supported ADIDO-to-VMC2 initiator, route, identity, protocol and acknowledgement remain unresolved. Model and test the application’s delivery boundary locally. Do not assume a working TIBCO pull, implement an unconfirmed ADIDO downloader, or change infrastructure.

This checkpoint uses synthetic data and simulated providers/transfers. Live provider calls, real file transfers, deployment and merging are outside this checkpoint.

5. Verification and parallel work

Use subagents for independent source analysis, test development/review and documentation where helpful. Assign clear file ownership and integrate through one implementation owner.

Demonstrate:

* repeated delivery without duplicate business output;
* interruption and restart partway through a file;
* Symcor success followed by Tungsten failure, resuming from persisted images;
* an unknown submission outcome without blind resubmission;
* competing workers and stale ownership recovery;
* multiple cheques and repeated account/date values without accidental Cartesian joins or lost case associations;
* incomplete file arrival and lost output acknowledgement.

Keep tests independent of live endpoints. Reuse stable fixtures and run targeted tests after changes, followed by one appropriate integration check.

6. Completion report

Provide the final commit and working-tree status, implemented behavior, exact commands and observed test results, and a requirement-to-code-to-test matrix. Mark each item implemented and verified, partially implemented, awaiting a contract, or awaiting environment integration.

List only the remaining concrete dependencies. Do not report an unsupported completion percentage or claim full business end-to-end acceptance.

All engineering responses, code, comments, tests and documents must be in English. Use text and filesystem tools; do not use screenshots, OCR or vision.

Start now and continue until this checkpoint is complete or a specific blocker prevents further independent work.
