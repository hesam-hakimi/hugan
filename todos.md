TASK: HF1_V2_RUNTIME_QA_PHASE_1_PREVIEW_ONLY_VERSION_0_3_141

Execute Phase 1 of HF1 V2 runtime QA using the installed Databricks ETL
Copilot extension.

This is a DEVELOPMENT_TEST_WORKSPACE.

It is not:

- the software development source repository;
- SIT;
- production;
- a real consumer deployment repository.

This workspace is disposable and contains synthetic QA inputs only.

Do not inspect or modify the extension source repository.
Do not inspect or modify etl-framework-adb.
Do not install or download dependencies.
Do not commit or push.
Do not execute a Databricks job.
Do not connect to or mutate real data.
Do not approve or execute a filesystem write during this phase.
Do not repair source code.

==================================================
1. EXPECTED RUNTIME IDENTITY
==================================================

Expected extension ID:

td-etl.databricks-etl-copilot

Expected active extension version:

0.3.141

Expected workspace topology:

- exactly one open workspace root;
- Development Test Workspace;
- no extension-source checkout;
- no etl-framework-adb;
- no existing job_conf/**;
- no existing env_conf/**;
- workflow customization already initialized;
- STTM file present at:

  sttm/qa_hf1v2_demo_sttm.md

Use runtime tools such as etl_capabilities and the live ETL Copilot output to
verify the installed extension identity.

Do not treat package metadata alone as runtime activation proof.

If the active extension is not 0.3.141, stop with:

QA_PHASE_1_RESULT: BLOCKED

==================================================
2. FIXED QA INPUTS
==================================================

Do not ask the user to provide these values again.

Job name:

qa_hf1v2_demo

Malcode:

acz9999

Environment:

dev

Strategy:

generic_dataframe_write

Source:

- type: Delta;
- physical mode: ADLS-path-backed;
- path:
  abfss://qa@qaetlhf1v2dev.dfs.core.windows.net/raw/qa_hf1v2_customer

Target:

- type: Delta;
- physical mode: ADLS-path-backed;
- path:
  abfss://qa@qaetlhf1v2dev.dfs.core.windows.net/curated/qa_hf1v2_customer
- format: delta;
- write mode: append.

Primary key:

customer_id

The primary key is informational for this append-only QA case.

Explicitly excluded behavior:

- direct Unity Catalog table-name write;
- merge;
- upsert;
- CDC;
- SCD2;
- database_out;
- Synapse;
- JDBC;
- TIBCO;
- production connectivity.

Any raw/curated labels in the STTM are logical zone names, not Unity Catalog
table identifiers.

==================================================
3. WORKSPACE BASELINE
==================================================

After workflow setup is complete, capture the runtime-QA baseline.

Confirm:

- workspace root count;
- workspace root path;
- active extension version;
- existing job_conf file count;
- existing env_conf file count;
- existing generated ETL artifact count;
- STTM path;
- workflow customization presence.

The expected pre-preview state is:

EXISTING_JOB_CONF_COUNT: 0
EXISTING_ENV_CONF_COUNT: 0

Do not modify workflow customization assets during this QA phase.

==================================================
4. FRAMEWORK-INDEPENDENT DISCOVERY
==================================================

Use only installed-extension runtime tools.

Verify:

- framework source checkout is absent;
- packaged framework fallback is used;
- the trusted Job Config envelope contract resolves;
- criticalConfigKeys are non-empty;
- approved packaged examples can be searched without local example roots;
- no consumer-editable context is treated as machine authority.

Use, where applicable:

- etl_get_framework_rules;
- etl_search_examples;
- etl_describe_module;
- etl_interpret_sttm.

Do not access the software source repository to obtain missing syntax.

If the packaged contract cannot be resolved, stop without preview or write.

==================================================
5. STTM INTERPRETATION
==================================================

Read:

sttm/qa_hf1v2_demo_sttm.md

The `Field Mapping` section must be recognized as a mapping section.

Report:

- mapping count;
- source evidence;
- target evidence;
- filters;
- write strategy;
- whether STTM parsing required a raw-content fallback.

Do not silently reinterpret the target as a Unity Catalog table.

If the structured parser still reports zero mappings, record that fact
honestly, but continue only if the installed runtime can derive the exact same
six mappings deterministically from the supplied STTM without guessing.

==================================================
6. TARGET DECISION
==================================================

Because the workspace contains no existing job_conf or env_conf for this job,
the expected decision is:

CREATE_NEW_JOB

This decision must be based on the Development Test Workspace contents, not on
the absence of etl-framework-adb.

Required:

TARGET_DECISION: CREATE_NEW_JOB
FRAMEWORK_SOURCE_REQUIRED: NO

==================================================
7. CANONICAL JOB CONFIG
==================================================

Generate the proposed Job Config using the trusted packaged contract.

The output must use the canonical HOCON envelope:

modules {
  <stage_key> {
    ...
    options {
      module = <module_type>
      method = process
    }
  }
}

Requirements:

- `modules` is an object, not an array;
- stage entries are keyed by stage name;
- every stage has `options.module`;
- every executable stage has the required method and option fields;
- the final writer is dataframe_writer;
- the writer destination is path-based;
- output format is delta;
- write mode is append;
- no direct Unity Catalog table target is present;
- no quoted-JSON modules envelope is present;
- no non-canonical top-level module blocks are present.

Use the installed packaged examples and trusted contract rather than inventing
a new envelope.

==================================================
8. PREVIEW ARTIFACTS
==================================================

Render and validate the complete proposed artifact set.

It must contain at least:

- one job configuration;
- one environment configuration.

Likely canonical destinations include:

job_conf/conf/acz9999/qa_hf1v2_demo.json

env_conf/dev/env_conf_dev_qa_hf1v2_demo.yaml

Additional include or SQL artifacts are permitted only when deterministically
required by the selected strategy and STTM.

Every artifact path must be inside the single Development Test Workspace root.

Report the complete preview manifest, including:

- relative path;
- artifact type;
- disposition;
- content hash/checksum;
- writable decision;
- validation result.

==================================================
9. REQUEST PREVIEW ONLY
==================================================

Call the installed trusted write workflow only far enough to create a real
preview record.

Do not provide a previewId on the first request.

The expected first-call behavior is:

- deterministic validation passes;
- a real Preview ID is issued;
- the complete artifact manifest is frozen;
- zero files are created;
- zero files are modified;
- zero files are deleted;
- explicit approval remains pending;
- no write authorization is consumed;
- no user approval is fabricated.

Do not approve the preview in this phase.

Do not invoke the second write turn.

Do not simulate or fabricate a Preview ID.

==================================================
10. ZERO-WRITE VERIFICATION
==================================================

After preview creation, verify directly that:

- job_conf/** is still absent;
- env_conf/** is still absent;
- no include or SQL file was created;
- no workflow customization asset changed;
- the STTM did not change;
- no protected root was modified;
- no artifact exists merely because it appeared in the preview manifest.

Required:

PREVIEW_ZERO_NEW_FILES: YES
PREVIEW_ZERO_MODIFIED_FILES: YES
PREVIEW_ZERO_DELETED_FILES: YES
WRITE_EXECUTED: NO

==================================================
11. STOP POINT
==================================================

Stop immediately after a valid Preview ID and zero-write proof are obtained.

Do not accept the preview.
Do not reject the preview unless deterministic validation itself fails.
Do not continue to approval/write testing.
Do not close or discard the active preview state.

Preserve the Chat/session because Phase 2 will use the exact Preview ID and
identical content.

==================================================
12. FINAL REPORT
==================================================

Return:

ACTIVE_EXTENSION_ID: <value>
ACTIVE_EXTENSION_VERSION: <value>
WORKSPACE_CLASSIFICATION: DEVELOPMENT_TEST_WORKSPACE
WORKSPACE_ROOT: <absolute path>
WORKSPACE_ROOT_COUNT: <number>
WORKFLOW_SETUP_ALREADY_PRESENT: YES/NO
STTM_INPUT_FOUND: YES/NO
STTM_STRUCTURED_MAPPING_COUNT: <number>
STTM_RAW_FALLBACK_REQUIRED: YES/NO
CONTEXT_FILES_CONSUMED: <exact list>
TARGET_DECISION: <value>
FRAMEWORK_SOURCE_REQUIRED: YES/NO
PACKAGED_CONTRACT_RESOLVED: YES/NO
CRITICAL_CONFIG_KEYS_COUNT: <number>
PACKAGED_EXAMPLE_SEARCH_PASS: YES/NO
CANONICAL_MODULE_ENVELOPE: YES/NO
MODULE_COUNT: <number>
DATAFRAME_WRITER_PATH_BASED: YES/NO
UNITY_CATALOG_DIRECT_WRITE_REQUESTED: NO
UNSUPPORTED_UNITY_CATALOG_DIAGNOSTIC_TRIGGERED: YES/NO
PREVIEW_ID: <real value or NONE>
PREVIEW_ARTIFACT_COUNT: <number>
PREVIEW_ARTIFACT_MANIFEST: <complete list>
PREVIEW_ZERO_NEW_FILES: YES/NO
PREVIEW_ZERO_MODIFIED_FILES: YES/NO
PREVIEW_ZERO_DELETED_FILES: YES/NO
PREVIEW_PATHS_INSIDE_WORKSPACE_ROOT: YES/NO
EXPLICIT_APPROVAL_REQUIRED: YES/NO
APPROVAL_STILL_PENDING: YES/NO
WRITE_EXECUTED: NO
SOURCE_CODE_MODIFIED: NO
REAL_DATA_ACCESSED: NO
DEVELOPMENT_TEST_WORKSPACE_MUTATED: NO
DEFERRED_CONTEXT_TRUST_FINDING_RECORDED: YES/NO

PASS requires:

- active extension 0.3.141;
- exactly one Development Test Workspace root;
- CREATE_NEW_JOB;
- no framework source;
- trusted packaged contract resolved;
- at least one canonical module;
- path-based dataframe_writer;
- deterministic validation success;
- a real Preview ID;
- a complete manifest;
- zero workspace writes;
- explicit approval still pending.

End exactly with one:

QA_PHASE_1_RESULT: PASS

QA_PHASE_1_RESULT: FAIL

QA_PHASE_1_RESULT: BLOCKED
