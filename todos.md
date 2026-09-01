Continue the same F5 runtime QA Phase 1 in the current Extension Development Host and the same isolated QA workspace.

The previous result was safely blocked by etl_validate_artifacts. No preview, approval, or write occurred. Treat that as a valid fail-closed result, not as permission to bypass validation.

Do not restart the test, do not create a new identifier, and do not reinterpret the workbook unless the prior structured result is genuinely unavailable.

Reuse exactly:

* selected mapping: FM_F01417B0_00002
* identifier: qa_sttm_workspace_write_smoke_20260901_095418_c5e982
* the same two-artifact inventory only:
    * one job configuration
    * one generated environment configuration
* no include files
* no additional job configuration
* the same synthetic transformation and writer intent

Correct only the three path semantics reported by the validator:

1. The environment source root incorrectly included /qa. Derive and use the host root required by the framework contract.
2. The job source path must preserve and append the complete relative source path qa/customers.
3. The environment destination/output root must preserve the complete output root qa/customer_name.

Derive the exact corrected field values from the validator diagnostics, framework rules, and module contracts already retrieved. Do not guess, weaken, suppress, or bypass a validation rule.

Use the registered render tools to rebuild the two artifacts in memory. Do not edit files directly.

Then call etl_validate_artifacts again on the exact corrected rendered bytes.

Report:

* the three corrected field names and before/after values;
* both proposed workspace destinations;
* artifact count;
* blocker count;
* warning count;
* physical workspace-containment result.

If any blocker remains, stop without calling etl_write_to_workspace and return:

PHASE1_CORRECTION_BLOCKED

If validation has zero blockers and both destinations are physically contained in the current isolated QA workspace, call etl_write_to_workspace with those exact two validated artifacts.

Pause at the trusted VS Code confirmation. Do not approve on my behalf.

Before pausing, report the complete confirmation manifest:

* workspace root;
* CREATE paths;
* OVERWRITE paths;
* UNCHANGED paths;
* blocked paths;
* exact total count.

For this first write, both artifacts must be under CREATE. OVERWRITE and UNCHANGED must be empty. If that is not true, instruct me to reject and stop.

Do not perform the identical rerun yet. Do not use direct filesystem writes, terminal commands, external services, Databricks, pipeline execution, publication, Git commit, or push.

If the correct trusted confirmation is displayed and awaiting my decision, return:

PHASE1_CORRECTION_READY_FOR_USER_APPROVAL
