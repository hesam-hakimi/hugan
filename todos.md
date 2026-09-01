Perform runtime QA Phase 1 for the current ETL extension development source.

This test must run through the actual VS Code Extension Development Host and registered ETL tools. Do not simulate tool results and do not replace ETL tool calls with direct filesystem edits or terminal commands.

Scope

Validate this runtime flow:

Synthetic Excel STTM interpretation
→ framework-aware artifact rendering
→ validation
→ trusted preview and explicit approval
→ actual write into the isolated QA workspace
→ identical rerun classified as UNCHANGED

Required workspace

Use only the currently opened isolated QA workspace.

Required STTM input:

sttm/synthetic_workbook.xlsx

Before doing anything, call:

etl_capabilities

Report:

* active extension version;
* current workspace root;
* registered ETL tools;
* whether the workspace is an isolated QA workspace.

The package version may still report 0.3.147; this is expected because this run tests current development source before the release-version change.

Stop if:

* no workspace is open;
* the workbook is outside the current workspace;
* the workspace resolves to the extension source repository;
* the workspace is a real consumer repository;
* any required ETL tool is unavailable.

Permitted ETL tools

Use only the necessary tools from this list:

etl_capabilities
etl_interpret_sttm
etl_get_framework_rules
etl_describe_module
etl_search_examples
etl_render_job_config
etl_render_env_config
etl_render_includes
etl_validate_artifacts
etl_write_to_workspace

Do not call:

etl_publish_to_dbfs
etl_run_pipeline
etl_test_run_on_databricks

Do not access Databricks, ADF, DBFS, GitHub, or any external service.

Phase A — Interpret the Excel STTM

Call etl_interpret_sttm using:

{
  "workspaceRoot": "<the current isolated QA workspace root>",
  "sttmPath": "sttm/synthetic_workbook.xlsx",
  "includeAudit": true
}

Confirm and report:

* the tool was actually invoked;
* the resolved workbook remains inside the QA workspace;
* file count;
* read count;
* blocked count;
* audit finding count;
* mapping count;
* structured JSON result availability;
* Markdown result availability.

Do not manually parse the workbook.

If interpretation fails or returns blocked input, stop without writing.

Phase B — Build the smallest valid smoke-test artifact set

Use the framework rules and packaged local examples to create the smallest valid artifact set representing one valid active mapping from the interpreted workbook.

Use a fresh synthetic identifier beginning with:

qa_sttm_workspace_write_smoke_

The identifier must not collide with an existing QA artifact.

Requirements:

* Use etl_get_framework_rules.
* Use etl_search_examples only against packaged or local reference examples.
* Use the appropriate render tools.
* Do not invent unsupported configuration fields.
* Do not generate a second job configuration for the same job.
* Reuse an existing environment only when the framework evidence requires it.
* Keep the artifact set minimal.
* Use synthetic values only.
* Do not modify the workbook.
* Keep every proposed destination inside the isolated QA workspace.

If a valid minimal artifact set cannot be rendered deterministically, stop before write and report the blocker.

Phase C — Validate before writing

Call:

etl_validate_artifacts

Validation must complete before any write request.

Report:

* every proposed destination;
* artifact type;
* validation result;
* blocked and warning counts;
* whether all destinations are physically contained inside the current QA workspace.

Stop without writing if:

* any validation blocker exists;
* a destination is absolute;
* a destination escapes the workspace;
* duplicate destinations conflict;
* the proposed set contains an unexpected file;
* any source-repository path appears.

Phase D — Trusted CREATE preview and approval

Call:

etl_write_to_workspace

Use only the exact artifacts that passed validation.

Do not use a direct file-write API, editor write, shell command, or terminal command.

The extension must display its trusted confirmation generated from the approved manifest.

Before I approve, summarize in chat:

* workspace root;
* CREATE paths;
* OVERWRITE paths;
* UNCHANGED paths;
* blocked paths;
* exact total file count.

For this first run:

* every writable destination must be CREATE;
* OVERWRITE must be empty;
* every CREATE path must be inside the isolated QA workspace.

If any OVERWRITE appears, instruct me to reject the confirmation and stop. Do not select approval on my behalf.

Pause while the confirmation is displayed. Continue only after I explicitly approve it through the VS Code confirmation interface.

Phase E — Verify the actual write result

After approval and tool completion, report from the real tool result:

* created count and paths;
* overwritten count and paths;
* unchanged count and paths;
* failed count and paths;
* blocked count and paths;
* skipped count and paths;
* success status;
* structured result availability.

Acceptance for the first write requires:

created > 0
overwritten = 0
failed = 0
blocked = 0

Confirm that no destination outside the isolated QA workspace was written.

Do not run a pipeline, publish, commit, or push.

Phase F — Identical rerun

Without changing the artifact bytes, call etl_write_to_workspace again with the exact same artifact set.

Expected result:

* the same destinations are classified as UNCHANGED;
* CREATE is empty;
* OVERWRITE is empty;
* no file is rewritten;
* no new approval is fabricated;
* exact per-file results are reported.

If the host displays a confirmation, report its sections and wait for my action. Do not approve on my behalf.

Acceptance requires:

created = 0
overwritten = 0
failed = 0
blocked = 0
unchanged = the complete artifact set

Final report

Return:

* extension version and workspace root;
* exact ETL tool calls made, in order;
* STTM interpretation totals;
* rendered artifact inventory;
* validation totals;
* first preview classification;
* whether explicit user approval occurred;
* first write per-file results;
* identical-rerun per-file results;
* confirmation that no direct filesystem editing fallback was used;
* confirmation that no external service was called;
* confirmation that no pipeline, publication, Git commit, or push occurred.

Return exactly one verdict:

F5_STTM_AND_WORKSPACE_WRITE_PHASE1_PASS

or:

F5_STTM_AND_WORKSPACE_WRITE_PHASE1_BLOCKED

Stop after reporting.
