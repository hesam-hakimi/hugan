Continue the same Phase 1 runtime QA in this Extension Development Host and isolated QA workspace.

The authoritative prior verdict is:

PHASE1_CORRECTION_BLOCKED

No confirmation or approval is currently available, and etl_write_to_workspace was not called.

The three ADLS path corrections and physical workspace containment have passed. Preserve them exactly.

Before rerendering, perform a read-only contract reconciliation using only:

* etl_get_framework_rules
* etl_describe_module
* etl_search_examples

Use complete packaged/local canonical examples rather than isolated keyword matches.

Establish explicit evidence for:

1. The permitted destination extension for a HOCON job configuration.
2. The complete stage-keyed modules structure.
3. The exact location and permitted values of options.module and options.method for data_sourcing_process.
4. The exact location, type, and required contents of sourceList.
5. The exact output-strategy representation recognized for the selected dataframe_writer.
6. Whether a SQL/include artifact is required for this sourced-view transformation.

Report the evidence source and exact relevant field structure for each item.

If the packaged rules, module contract, canonical example, and Validator requirements are missing or contradictory, stop without rerendering or writing and return:

PHASE1_CONTRACT_EVIDENCE_BLOCKED

If the contract is unambiguous, perform exactly one additional correction cycle.

Preserve:

* mapping FM_F01417B0_00002;
* identifier qa_sttm_workspace_write_smoke_20260901_095418_c5e982;
* the three corrected ADLS relationships;
* the synthetic transformation and writer intent;
* all workspace destinations as relative paths.

Correct only what the established contract requires:

* replace the invalid job_config.yaml destination with the evidence-supported .conf or .json destination;
* use the exact valid data_sourcing_process stage structure;
* add the required non-empty sourceList;
* express the output strategy in the recognized form;
* add an include artifact only if the canonical contract proves it is required.

The earlier restriction to exactly two artifacts is lifted only when the framework contract requires an include. Do not add any unrelated artifact, job, environment, or identifier.

Use only the registered ETL render tools. Do not directly edit files.

Call etl_validate_artifacts exactly once on the corrected rendered artifact set.

Do not call etl_write_to_workspace if any of these remain:

* any blocker;
* HOCON extension mismatch;
* missing or incorrect options.module/method;
* missing or empty sourceList;
* undetermined output strategy;
* missing required include;
* duplicate conflict;
* absolute, escaping, or source-repository path;
* any other structural or write-safety warning.

The only acceptable residual warnings are the isolated-QA limitations stating that framework 0.0.0-qa was resolved locally but runtime/DBFS compatibility evidence is unavailable. Report these explicitly.

If validation satisfies those conditions, call etl_write_to_workspace with the exact validated artifacts and pause at the trusted confirmation.

The first confirmation must show:

* every proposed destination under CREATE;
* OVERWRITE empty;
* UNCHANGED empty;
* BLOCKED empty;
* all paths inside the current isolated QA workspace.

Report the complete manifest and wait for my manual decision. Do not approve on my behalf and do not perform the identical rerun yet.

Do not use direct filesystem writes, terminal commands, external services, Databricks, pipeline execution, publication, Git commit, or push.

Return exactly one verdict:

PHASE1_CONTRACT_RECONCILED_CREATE_CONFIRMATION_READY

or:

PHASE1_CONTRACT_RECONCILIATION_BLOCKED
