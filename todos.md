TASK_ID: ETL-0910-INSTALLED-CONSUMER-JOBENV-MULTIROOT-AND-OVERWRITE-SMOKE01
TYPE: Focused installed-product qualification using the existing harness

ENVIRONMENT
Windows; reuse the dedicated ETL test environment:
C:\docs\ETL-TESTENV-INSTALLED-WORKFLOW-SMOKE01
Installed product: td-etl.databricks-etl-copilot 0.3.147.
Resolve actual paths and identities from the completed predecessor:
ETL-0910-INSTALLED-CONSUMER-JOBENV-WRITE-SMOKE01.

LANGUAGE / NO VISION
Use English for ALL communication and deliverables.
No screenshots, video, image inspection, OCR or vision calls.
Use existing text/DOM automation, tool results, logs and filesystem checks.

MANDATORY REUSE
The predecessor completed the installed single-root CREATE scenario:
two correct files, no pre-approval writes, 12 verification groups passed.

Reuse its FINAL working repeatable caller, flow driver, fixture,
verification helpers and retained temporary job/env consumer.
Do not select the obsolete one-shot caller.
The caller must handle BOTH observed gates:
- VS Code tool confirmation from prepareInvocation.
- The product's trusted write-approval dialog.

Read the existing interfaces once and parameterize them for these cases.
Allow only minimal changes needed for the new scenarios.
Do not build another harness, catalog extractor or evidence framework.
Do not repeat the accepted CREATE scenario or rebuild test outputs.
Check for an existing/in-progress instance of this task before execution.

AUTHORITY AND PRESERVATION
This task authorizes disposable fixture setup and one approved content
update to the existing temporary consumer's job configuration.
Preserve its environment configuration and unrelated files.
Preserve all prior evidence and the separate accepted workflow consumer.

Use normal product approval bound to the exact preview.
No forged approval records, mocked services or direct filesystem writes
to substitute for the product operation.

SCENARIOS
Establish expected behavior from the existing contract and focused prior
tests before execution. Inspect only relevant source if a concrete
contract detail remains unresolved.

1. Root selection and reference exclusion
Reuse the temporary job/env consumer. Add a disposable reference stand-in
using the established reference-classification fixture.
Open the reference folder first and the consumer second.

Preview with the explicit consumer workspaceRoot. Verify that every
destination resolves inside that consumer. Reverse folder order and
verify destination selection remains consistent.

Exercise explicit reference-root rejection through a non-mutating preview.
Require no output files in the reference stand-in.
Never use the actual source repository as a negative-test write target.

2. Genuine ambiguity
Use two eligible disposable consumer roots with no explicit or otherwise
unambiguous selected target. Omit workspaceRoot and verify the documented
ambiguity blocker and zero output writes.

Do not assume that one reference folder plus one eligible consumer is
ambiguous. If the resolver legitimately identifies a unique target,
that is a different scenario.

3. Existing identical files
Preview the unchanged retained fixture against the existing consumer.
Record the actual disposition and compare it with the contract.
Do not describe an identical-payload run as proof of content replacement.
Exercise a no-op only as supported by the normal product protocol.
Verify the promised preservation behavior.

4. Actual content replacement and cancellation
Prepare one minimal, schema-valid change to an existing non-routing job
field, keeping both destination paths and the environment input unchanged.
Retain the exact before/after content delta.

Obtain the real preview. Require that only the intended job content
changes and that the environment file is preserved.
Cancel the product write-approval dialog once and verify zero changes.

Obtain a fresh valid preview and approve that exact change once through
the normal product controls.
Verify the resulting job bytes match the approved content, the environment
and unrelated files remain unchanged, and no output escapes the selected
consumer root.

EXECUTION DISCIPLINE
Use the installed registered etl_write_to_workspace route through the
existing caller. Preserve the distinction from model-driven Chat behavior.
Use the same explicit root throughout each preview/approval/write sequence.
Compare Windows path identity correctly while retaining authored casing.

Keep normal launch settings; do not disable Workspace Trust.
Carry forward the existing trust limitation without another trust
investigation or session-storage inspection.

If a check fails, preserve the exact input, product result and filesystem
delta. Identify the smallest product or harness correction.
Do not weaken expectations, reset evidence or repeat uncertain writes.

A report-generation failure must never trigger another product write.
Resume from retained outputs and fix only reporting when appropriate.

BOUNDARIES
No product source edits, build, packaging, installation, version change,
Git mutation, real consumer writes, deployment, publishing or ETL job run.
No repeated historical audits or standalone reconciliation stage.

DELIVERY
Produce concise report.md and result.json with minimal supporting evidence.
Report each scenario as PASS, FAIL or NOT EXERCISED, with its actual scope.
Separate product defects from caller/reporting failures.

Record the final reusable invocation, parameter locations and helper paths
in the existing report so the next task can run them without reconstruction.

Keep Upgrade disclosure/Overwrite UI issues open.
Do not claim historical-incident reproduction, model-driven Chat
qualification or full release readiness.

Finish with the remaining concrete release blockers. Retain evidence for
one consolidated independent review of the related write scenarios.
