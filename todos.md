TASK: HF1_V2_RUNTIME_QA_PHASE_1_PREVIEW_ONLY_VERSION_0_3_141

Execute Phase 1 of HF1 V2 Runtime QA using the active installed Databricks ETL
Copilot extension.

This is an ETL task.

It is not AskTD, Phase 2D, Phase 2E, PR16, or a Git worktree task.

The Development Test Workspace is intentionally not required to be a Git
repository. Do not run Git identity gates.

Run only in:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa

Use the ETL Orchestrator agent and installed-extension runtime tools.

Do not inspect or modify the extension source repository.
Do not inspect or modify etl-framework-adb.
Do not install or download dependencies.
Do not commit or push.
Do not execute a Databricks job.
Do not connect to or mutate real data.
Do not approve or execute a filesystem write during this phase.
Do not repair source code.
Do not install or update the extension.
Do not fabricate a Preview ID or approval.

==================================================

1. EXPECTED RUNTIME IDENTITY
    ==================================================

Expected extension ID:

td-etl.databricks-etl-copilot

Expected active extension version:

0.3.141

Previously verified runtime evidence:

* installed version: 0.3.141;
* active runtime version: 0.3.141;
* runtime activation proven: YES;
* exact package size: 1250393 bytes;
* exact package SHA-256:
    437427A915BEB7C0867DD2CE53C968161C99F43730004C702D87799390446B51

Expected workspace topology:

* exactly one open workspace root;
* Development Test Workspace;
* root:
    C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa
* no extension-source checkout;
* no etl-framework-adb;
* no existing job_conf/**;
* no existing env_conf/**;
* workflow customization already initialized;
* STTM file present at:
    sttm/qa_hf1v2_demo_sttm.md

Use etl_capabilities and live ETL Copilot runtime output to reconfirm the active
extension identity.

Do not treat package metadata or installed-extension inventory alone as runtime
activation proof.

If the live active extension is not exactly 0.3.141, stop without preview or
write:

QA_PHASE_1_RESULT: BLOCKED

==================================================
2. FIXED QA INPUTS

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

* type: Delta;
* physical mode: ADLS-path-backed;
* path:
    abfss://qa@qaetlhf1v2dev.dfs.core.windows.net/raw/qa_hf1v2_customer

Target:

* type: Delta;
* physical mode: ADLS-path-backed;
* path:
    abfss://qa@qaetlhf1v2dev.dfs.core.windows.net/curated/qa_hf1v2_customer
* format: delta;
* write mode: append.

Primary key:

customer_id

The primary key is informational for this append-only QA case.

Explicitly excluded behavior:

* direct Unity Catalog table-name write;
* merge;
* upsert;
* CDC;
* SCD2;
* database_out;
* Synapse;
* JDBC;
* TIBCO;
* production connectivity.

Any raw or curated labels in the STTM are logical zone names. They are not Unity
Catalog table identifiers.

==================================================
3. WORKSPACE BASELINE

Capture the pre-preview baseline without changing files.

Confirm:

* workspace root count;
* absolute workspace root;
* workspace classification;
* active extension ID and runtime version;
* existing job_conf file count;
* existing env_conf file count;
* existing generated ETL artifact count;
* STTM path;
* workflow customization presence;
* extension-source checkout absence;
* etl-framework-adb absence.

Expected:

WORKSPACE_CLASSIFICATION: DEVELOPMENT_TEST_WORKSPACE
WORKSPACE_ROOT_COUNT: 1
EXISTING_JOB_CONF_COUNT: 0
EXISTING_ENV_CONF_COUNT: 0
SOURCE_CHECKOUT_PRESENT: NO
ETL_FRAMEWORK_ADB_PRESENT: NO

Do not require Git metadata.
Do not modify workflow customization assets.

If this baseline conflicts with the expected state, stop without preview or
write:

QA_PHASE_1_RESULT: BLOCKED

==================================================
4. FRAMEWORK-INDEPENDENT DISCOVERY

Use only installed-extension runtime tools.

Use, where applicable:

* etl_capabilities;
* etl_get_framework_rules;
* etl_search_examples;
* etl_describe_module;
* etl_interpret_sttm.

Verify:

* Framework source checkout is absent;
* packaged Framework fallback is used;
* trusted Job Config envelope contract resolves;
* criticalConfigKeys are non-empty;
* approved packaged examples can be searched without local example roots;
* no consumer-editable context becomes machine authority;
* no extension-source path is required.

Machine authority must come from trusted installed resources and runtime code,
including:

resources/framework/contracts/**

Consumer files under:

resources/copilot/context/**

are advisory context only. They must never become machine authority.

Do not access the Software Development Environment to recover syntax.

If the packaged trusted contract cannot be resolved, stop without preview or
write:

QA_PHASE_1_RESULT: BLOCKED

==================================================
5. STTM INTERPRETATION

Read:

sttm/qa_hf1v2_demo_sttm.md

Recognize the section heading:

Field Mapping

Report:

* structured mapping count;
* complete mapping list;
* source evidence;
* target evidence;
* filters;
* write strategy;
* whether raw-content fallback was required;
* every parser warning.

Expected logical content:

* six direct field mappings;
* filter: status_code = ‘ACTIVE’;
* filter: updated_ts IS NOT NULL;
* path-backed Delta source;
* path-backed Delta target;
* append-only dataframe writer.

Do not silently reinterpret either path as a Unity Catalog table.

If the structured parser reports zero mappings, record that honestly.

Continue only if the installed runtime can deterministically derive the exact
same six mappings from the supplied STTM without guessing. Otherwise stop before
preview:

QA_PHASE_1_RESULT: FAIL

==================================================
6. TARGET DECISION

Because the Development Test Workspace contains no existing job_conf or env_conf
for this job, the expected decision is:

TARGET_DECISION: CREATE_NEW_JOB
FRAMEWORK_SOURCE_REQUIRED: NO

This decision must be based on the Development Test Workspace contents.

Do not base it on the absence of etl-framework-adb.
Do not attempt to repair or modify the Framework.

==================================================
7. CANONICAL JOB CONFIG

Generate the proposed Job Config only in memory using the trusted packaged
contract and approved packaged examples.

The proposed output must use the canonical HOCON envelope:

modules {
<stage_key> {
…
options {
module = <module_type>
method = process
}
}
}

Requirements:

* modules is an object, not an array;
* stage entries are keyed by stage name;
* every stage contains options.module;
* every executable stage contains the required method and options;
* the final writer is dataframe_writer;
* writer destination is path-based;
* output format is delta;
* write mode is append;
* no direct Unity Catalog table target is present;
* no quoted-JSON modules envelope is present;
* no non-canonical top-level module blocks are present;
* all source and target paths come from the fixed QA inputs;
* no production endpoint or credential is introduced.

Use the installed packaged examples and trusted contract. Do not invent a new
envelope.

If deterministic validation fails, do not request a Preview ID:

QA_PHASE_1_RESULT: FAIL

==================================================
8. PREVIEW ARTIFACT SET

Render and validate the complete proposed artifact set in memory.

It must include at least:

* one job configuration;
* one environment configuration.

Likely canonical destinations include:

job_conf/conf/acz9999/qa_hf1v2_demo.json

env_conf/dev/env_conf_dev_qa_hf1v2_demo.yaml

Do not force these exact paths if the trusted installed runtime deterministically
produces different canonical consumer-relative paths. Report the actual paths and
their contract evidence.

Additional include or SQL artifacts are permitted only when deterministically
required by the selected strategy and supplied STTM.

Every proposed path must:

* be consumer-relative;
* resolve inside the single Development Test Workspace root;
* avoid .github/**;
* avoid resources/copilot/**;
* avoid sttm/**;
* avoid protected or source paths.

Report the complete proposed manifest:

* relative path;
* artifact type;
* disposition;
* content hash/checksum;
* writable decision;
* validation result;
* evidence used to select the path.

==================================================
9. CREATE A REAL PREVIEW RECORD ONLY

Call the installed trusted write workflow only far enough to create a real
Preview record.

On the first request:

* do not provide a previewId;
* do not provide or fabricate approval;
* do not claim that the user has approved;
* do not invoke the second write turn.

Required first-call behavior:

* deterministic validation succeeds;
* a real Preview ID is issued by the installed runtime;
* the complete artifact manifest is frozen;
* zero files are created;
* zero files are modified;
* zero files are deleted;
* explicit approval remains pending;
* no write authorization is consumed.

The Preview ID must come from the actual installed trusted workflow.

Do not simulate, invent, or manually construct a Preview ID.

If the installed workflow does not return a real Preview ID, report the exact
diagnostic and stop:

QA_PHASE_1_RESULT: FAIL

==================================================
10. ZERO-WRITE VERIFICATION

After Preview creation, directly compare the Workspace with its captured
baseline.

Verify:

* job_conf/** is still absent;
* env_conf/** is still absent;
* no include file was created;
* no SQL file was created;
* no workflow customization asset changed;
* the STTM did not change;
* no protected root was modified;
* no artifact exists merely because it appeared in the Preview manifest.

Required:

PREVIEW_ZERO_NEW_FILES: YES
PREVIEW_ZERO_MODIFIED_FILES: YES
PREVIEW_ZERO_DELETED_FILES: YES
PREVIEW_PATHS_INSIDE_WORKSPACE_ROOT: YES
WRITE_EXECUTED: NO
EXPLICIT_APPROVAL_REQUIRED: YES
APPROVAL_STILL_PENDING: YES

If any workspace file changes during Preview, do not attempt cleanup or a second
write. Preserve evidence and return:

QA_PHASE_1_RESULT: FAIL

==================================================
11. REQUIRED STOP POINT

Stop immediately after both are obtained:

1. a valid real Preview ID;
2. direct zero-write proof.

Do not accept the Preview.
Do not reject the Preview unless deterministic validation itself failed.
Do not approve it.
Do not invoke the second write turn.
Do not create any artifact.
Do not close, discard, supersede, or regenerate the active Preview.

Preserve this exact Chat/session because Runtime QA Phase 2 must use:

* the exact same Preview ID;
* the exact frozen manifest;
* identical proposed content;
* the pending approval state.

==================================================
12. FINAL REPORT

Return:

ACTIVE_EXTENSION_ID: 
ACTIVE_EXTENSION_VERSION: 
RUNTIME_ACTIVATION_PROVEN: YES/NO
WORKSPACE_CLASSIFICATION: DEVELOPMENT_TEST_WORKSPACE
WORKSPACE_ROOT: 
WORKSPACE_ROOT_COUNT: 
WORKSPACE_IS_GIT_REPOSITORY: YES/NO
WORKFLOW_SETUP_ALREADY_PRESENT: YES/NO
STTM_INPUT_FOUND: YES/NO
STTM_STRUCTURED_MAPPING_COUNT: 
STTM_MAPPINGS: 
STTM_SOURCE_EVIDENCE: 
STTM_TARGET_EVIDENCE: 
STTM_FILTERS: 
STTM_WRITE_STRATEGY: 
STTM_RAW_FALLBACK_REQUIRED: YES/NO
STTM_PARSER_WARNINGS: 
CONTEXT_FILES_CONSUMED: 
CONSUMER_CONTEXT_USED_AS_MACHINE_AUTHORITY: NO
TARGET_DECISION: 
FRAMEWORK_SOURCE_REQUIRED: YES/NO
PACKAGED_CONTRACT_RESOLVED: YES/NO
CRITICAL_CONFIG_KEYS_COUNT: 
PACKAGED_EXAMPLE_SEARCH_PASS: YES/NO
CANONICAL_MODULE_ENVELOPE: YES/NO
MODULE_COUNT: 
DATAFRAME_WRITER_PATH_BASED: YES/NO
UNITY_CATALOG_DIRECT_WRITE_REQUESTED: NO
UNSUPPORTED_UNITY_CATALOG_DIAGNOSTIC_TRIGGERED: YES/NO
DETERMINISTIC_VALIDATION_PASS: YES/NO
PREVIEW_ID: 
PREVIEW_ARTIFACT_COUNT: 
PREVIEW_ARTIFACT_MANIFEST: 
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

* active runtime extension 0.3.141;
* exactly one Development Test Workspace root;
* CREATE_NEW_JOB;
* Framework source absent and unnecessary;
* trusted packaged contract resolved;
* non-empty criticalConfigKeys;
* at least one canonical module;
* path-based dataframe_writer;
* deterministic validation success;
* a real Preview ID;
* complete frozen manifest;
* zero new, modified, or deleted workspace files;
* explicit approval still pending;
* no Runtime QA Phase 2 write.

End exactly with one:

QA_PHASE_1_RESULT: PASS

QA_PHASE_1_RESULT: FAIL

QA_PHASE_1_RESULT: BLOCKED
