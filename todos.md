TASK_ID: ETL-0910-INSTALLED-CONSUMER-JOBENV-WRITE-SMOKE01
TYPE: Installed-product preview, approval and consumer-write qualification

ENVIRONMENT
Windows; reuse the installed td-etl.databricks-etl-copilot 0.3.147 in:
C:\docs\ETL-TESTENV-INSTALLED-WORKFLOW-SMOKE01
Reuse its dedicated user-data/extensions directories and existing
automation transport. Resolve exact current identities from local records.

LANGUAGE / NO VISION
Use English for all messages, progress updates and deliverables.
No screenshots, video, image inspection, OCR or vision calls.
Disable screenshot hooks in reused automation.
Use text/DOM events, product tool results, logs and filesystem evidence.

ACCEPTED BASELINE
ETL-0910-EXISTING-CONSUMER-UPGRADE-INDEPENDENT-REVIEW01 accepted the
consumer skill upgrade with limitations and zero blocking findings.
Preserve that acceptance. Do not repeat Initialize, Upgrade, catalog
reconstruction, installation review or historical reconciliation.

Check whether this task is already running or completed before acting.
Resume valid existing work; do not create a concurrent or duplicate run.

AUTHORIZED WORK
Prepare one fresh disposable consumer workspace and exercise the installed
product's actual preview → approval → write route for exactly two new
fixture outputs: one job configuration and one environment configuration.

This task authorizes that bounded temporary write after the actual
preview identifies the selected root, both CREATE paths and their content.
Use the normal product approval mechanism bound to that exact preview.
Do not bypass approval, forge approval records, or replace the product
writer with direct filesystem writes.

EXECUTION
1. Check the installed candidate against the accepted identity once.
   Reuse existing helpers; make only the minimum task-specific adaptation.
   Use normal Workspace Trust behavior; do not pass
   --disable-workspace-trust or alter global trust settings.
   If trust interaction is required, use the normal UI for this temporary
   folder only and record the observed behavior.

2. Resolve and reuse the converged synthetic fixture retained under
   ETL-0909-PRODUCT-WRITE-REPRO01:
   measurements/d6-converged-full-route-preview.json
   derivedFixtureDisclosure.{jobConfig,envConfig}
   Verify it against its actual retained records, not screenshot hashes.
   Do not invent another fixture or substitute customer data.

3. Create the temporary consumer through OS temporary-directory APIs,
   outside source, reference and installed-extension trees.
   Use a distinct prefix from helper/scratch files.
   Prepare only required fixture prerequisites, including job_conf/
   and env_conf/ layout markers, and record the baseline.

4. Invoke the supported installed ETL preview/write tools through the
   normal Host workflow. Reuse the recorded valid call shape.
   Do not import repository source or mock the writer/approval services.
   Pass the selected consumer workspaceRoot explicitly where supported.

5. Before approval, retain the actual root, both relative and resolved
   destinations, proposed content, and the product's manifest identity.
   Require exactly two CREATE outputs contained in that consumer root.
   Confirm preview has created neither output.

6. Complete the normal approval and guarded write once, bound to the
   unchanged preview. A changed root, destination, content or artifact set
   requires a new preview and its corresponding approval.

7. Verify actual on-disk content against the approved preview:
   exactly the two intended outputs, no unexpected product-created files,
   no changes to existing fixture files, and no write outside the root.
   Retain the actual product result, including structured blockers or
   partial outcomes. A success message alone is insufficient.

EFFICIENCY AND FAILURE HANDLING
Reuse accepted permanent-test results within their recorded scope.
Do not rebuild test outputs or rerun suites simply because this is a new
task. Do not create another evidence framework or catalog extractor.

If the product route fails, preserve the smallest reproducible failure:
exact input, preview, tool result, observed filesystem delta and the
specific permanent regression-test target. Stop repeated attempts unless
a concrete, authorized correction to the test invocation justifies one.
Do not silently modify the fixture or weaken validation to obtain PASS.

BOUNDARIES
No product source edits, build, packaging, installation, version bump,
Git mutation, real consumer changes, publish, deploy or ETL runtime job.
Leave the previously accepted workflow consumer unchanged.
Close only task-owned Host processes and preserve the reusable environment.

DELIVERY
Produce concise report.md and result.json, with only the supporting
tool/log and before/after evidence needed for this scenario.
Reference earlier accepted records instead of reproducing their reports.

Report separately:
- Installed preview/approval/write outcome.
- Approved versus actual paths and content.
- Preservation and containment outcome.
- Normal trust behavior actually observed.
- Any concrete defect and smallest corrective task.
- Historical original-incident reproduction: only claim if actually tested.
- Multi-root behavior and full release readiness: not established here.

Keep the Upgrade disclosure/Overwrite release issues open.
Finish this scenario without adding another reconciliation stage.
