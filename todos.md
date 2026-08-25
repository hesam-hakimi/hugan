TASK: HF1_V2_RUNTIME_QA_PHASE_1_PREVIEW_ONLY_VERSION_0_3_142

Execute Phase 1 of HF1 V2 Runtime QA using the installed Databricks ETL
Copilot Extension version 0.3.142.

This run validates Repair 9 in the real installed Extension runtime and continues
only as far as creating a real Preview record.

This is a DEVELOPMENT_TEST_WORKSPACE containing synthetic QA inputs.

It is not:

* the Extension source repository;
* a Framework source repository;
* SIT;
* production;
* a real consumer deployment repository.

Do not inspect or modify the Extension source repository.
Do not inspect or modify etl-framework-adb.
Do not install or download dependencies.
Do not commit or push.
Do not execute a Databricks job.
Do not connect to real data.
Do not approve or execute a filesystem write.
Do not repair source code.
Do not create or modify workflow customization assets.

==================================================

1. EXPECTED RUNTIME IDENTITY
    ==================================================

Expected Extension ID:

td-etl.databricks-etl-copilot

Expected active runtime version:

0.3.142

Verified installed artifact:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.142.vsix

Verified artifact size:

1251308 bytes

Verified artifact SHA-256:

B392329A4B45C26D6DC17E91F14604B5731286F74B3AFE03603EE57A5F046E23

Expected VS Code product/profile:

* Visual Studio Code Stable;
* Default profile;
* no custom extensions directory.

Use live runtime evidence from this reloaded QA window.

Acceptable runtime activation evidence includes:

* current ETL Copilot Output containing ETL Copilot version: 0.3.142;
* live installed Extension capabilities identifying version 0.3.142;
* newly timestamped Extension Host activation evidence for this window.

Do not treat installed-directory metadata, package.json, VSIX metadata, or stale
logs as runtime activation proof.

If the active Extension Host is not version 0.3.142, stop immediately without
interpreting the STTM or requesting Preview:

QA_PHASE_1_RESULT: BLOCKED

==================================================
2. EXPECTED WORKSPACE

Expected workspace root:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa

Expected topology:

* exactly one open workspace root;
* no Extension-source checkout;
* no etl-framework-adb;
* non-Git fresh consumer workspace is permitted;
* workflow customization already initialized;
* managed initialization evidence is present;
* STTM file is present at:
    sttm/qa_hf1v2_demo_sttm.md
* no existing job_conf/**;
* no existing env_conf/**;
* no existing generated ETL artifacts.

Expected runtime classification after Repair 9:

WORKSPACE_CLASSIFICATION: DEVELOPMENT_TEST_WORKSPACE
RUNTIME_TARGET_TYPE: consumer-etl-workspace
RUNTIME_READY: YES
RUNTIME_AVAILABLE: YES
RUNTIME_BLOCKER_COUNT: 0

A fresh initialized consumer must not require:

* Git metadata;
* existing job_conf/**;
* existing env_conf/**;
* an Extension source checkout;
* a Framework source checkout.

The absence of job_conf and env_conf means CREATE_NEW_JOB downstream. It must not
become a capabilities or STTM preflight blocker.

If the correct single QA workspace is open but the 0.3.142 runtime still
classifies it as unknown, or directs the user to open an ETL Framework
workspace, record this as a Repair 9 runtime regression and stop:

REPAIR_9_FRESH_CONSUMER_RUNTIME_PASS: NO
QA_PHASE_1_RESULT: FAIL

If the actual workspace root or root count differs from the expected topology,
stop:

QA_PHASE_1_RESULT: BLOCKED

==================================================
3. FIXED QA INPUTS

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

Any raw or curated labels in the STTM are logical zone names, not Unity Catalog
table identifiers.

==================================================
4. CAPTURE THE PRE-PREVIEW BASELINE

Before invoking ETL discovery or Preview, capture:

* workspace root count;
* absolute workspace root;
* runtime target type;
* runtime readiness and blockers;
* active Extension ID and runtime version;
* existing job_conf file count;
* existing env_conf file count;
* existing include and SQL artifact count;
* existing generated ETL artifact count;
* complete workspace file inventory;
* size and SHA-256 of every workspace file;
* STTM path, size, and SHA-256;
* workflow customization asset paths, sizes, and SHA-256 values;
* source and Framework checkout absence.

Expected:

EXISTING_JOB_CONF_COUNT: 0
EXISTING_ENV_CONF_COUNT: 0
EXISTING_GENERATED_ETL_ARTIFACT_COUNT: 0

Do not modify the workspace while collecting the baseline.

==================================================
5. REPAIR 9 RUNTIME CLASSIFICATION CHECK

Invoke installed-runtime capabilities before STTM interpretation.

Verify that managed initialization evidence establishes consumer-workspace intent
without becoming machine authority.

Required:

* targetType = consumer-etl-workspace;
* runtime ready and available;
* zero blockers;
* Git metadata not required;
* existing job_conf/env_conf not required;
* folder name not accepted as classification evidence;
* STTM alone not accepted as classification evidence;
* resources/copilot/context/** alone not accepted as classification evidence;
* consumer context content not treated as machine authority;
* Extension source and Framework source remain rejected;
* ambiguous multi-root remains fail-closed;
* initialization evidence is not passed to packaged example-root discovery;
* initialization evidence does not authorize a write.

Record the exact runtime evidence used.

Required:

REPAIR_9_FRESH_CONSUMER_RUNTIME_PASS: YES

==================================================
6. FRAMEWORK-INDEPENDENT DISCOVERY

Use only installed-Extension runtime tools.

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
* no source-checkout path is required;
* no consumer-editable context becomes machine authority.

Machine authority must come from trusted installed resources such as:

resources/framework/contracts/**

and trusted installed runtime code.

Consumer files under:

resources/copilot/context/**

are advisory only.

Do not access the Software Development Environment to recover syntax.

If the packaged contract cannot be resolved, stop without Preview or Write:

QA_PHASE_1_RESULT: FAIL

==================================================
7. STTM INTERPRETATION

Read:

sttm/qa_hf1v2_demo_sttm.md

The mapping section heading is:

Field Mapping

Report:

* structured mapping count;
* exact six source-to-target mappings;
* source evidence;
* target evidence;
* filters;
* write strategy;
* raw-content fallback requirement;
* parser warnings.

Expected logical content:

* six direct field mappings;
* filter status_code = 'ACTIVE';
* filter updated_ts IS NOT NULL;
* path-backed Delta source;
* path-backed Delta target;
* append-only dataframe writer.

Do not silently reinterpret the target as a Unity Catalog table.

If the structured parser reports zero mappings, record that honestly.

Continue only if the installed 0.3.142 runtime can derive the exact same six
mappings deterministically from the supplied STTM without guessing.

If exact deterministic interpretation is impossible, stop without Preview:

QA_PHASE_1_RESULT: FAIL

==================================================
8. TARGET DECISION

Because this fresh consumer workspace contains no job_conf or env_conf for the
job, the required decision is:

TARGET_DECISION: CREATE_NEW_JOB
FRAMEWORK_SOURCE_REQUIRED: NO

This decision must be based on consumer workspace contents.

It must not be based merely on the absence of etl-framework-adb.

==================================================
9. CANONICAL JOB CONFIG

Generate the proposed Job Config using the trusted packaged contract and approved
packaged examples.

Use the canonical HOCON envelope:

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
* every stage has options.module;
* every executable stage contains required method and option fields;
* final writer is dataframe_writer;
* writer destination is the target ADLS path;
* output format is delta;
* write mode is append;
* no direct Unity Catalog table target exists;
* no quoted-JSON modules envelope exists;
* no non-canonical top-level module block exists;
* no merge/upsert/CDC/SCD2 logic exists.

Do not invent an envelope or syntax not supported by the packaged contract.

==================================================
10. RENDER AND VALIDATE THE COMPLETE PROPOSAL

Render and validate the complete proposed artifact set.

It must contain at least:

* one Job Config;
* one Environment Config.

Likely canonical paths include:

job_conf/conf/acz9999/qa_hf1v2_demo.json

env_conf/dev/env_conf_dev_qa_hf1v2_demo.yaml

Do not force those paths if the trusted runtime deterministically produces
different canonical consumer-relative paths.

Report the actual path and its authoritative evidence.

Additional include or SQL artifacts are allowed only if deterministically
required by the selected strategy and STTM.

Every artifact path must remain physically inside the single Development Test
Workspace root.

For every proposed artifact report:

* relative path;
* absolute normalized path;
* artifact type;
* disposition;
* content SHA-256/checksum;
* writable decision;
* validation result;
* authoritative destination evidence.

Required validation:

* canonical envelope valid;
* required modules and methods present;
* one Job Config only;
* no duplicate destination paths;
* path containment passes;
* deterministic validation passes;
* no unsupported Unity Catalog diagnostic;
* no consumer context used as machine authority.

==================================================
11. REQUEST A REAL PREVIEW ONLY

Invoke the installed trusted guarded-write workflow only far enough to create a
real Preview record.

This must be the first Preview request.

Do not provide a previewId on the first request.

Expected first-call behavior:

* deterministic validation passes;
* a real runtime-issued Preview ID is returned;
* complete artifact manifest is frozen;
* proposed paths and content hashes are frozen;
* zero proposed consumer files are created;
* zero existing consumer files are modified;
* zero consumer files are deleted;
* explicit approval remains pending;
* no write authorization is consumed;
* no approval is inferred or fabricated.

Do not approve the Preview.

Do not invoke the second write turn.

Do not simulate or fabricate a Preview ID.

If deterministic validation passes but no real Preview ID is issued, report the
exact diagnostic and stop:

QA_PHASE_1_RESULT: FAIL

==================================================
12. ZERO-WRITE VERIFICATION

After Preview creation, directly compare the workspace with the Section 4
baseline.

Verify:

* job_conf/** is still absent;
* env_conf/** is still absent;
* no include or SQL file was created;
* no generated artifact in the Preview manifest physically exists;
* workflow customization assets are byte-unchanged;
* STTM is byte-unchanged;
* no protected root changed;
* no workspace file was created;
* no workspace file was modified;
* no workspace file was deleted.

Required:

PREVIEW_ZERO_NEW_FILES: YES
PREVIEW_ZERO_MODIFIED_FILES: YES
PREVIEW_ZERO_DELETED_FILES: YES
PREVIEW_PATHS_INSIDE_WORKSPACE_ROOT: YES
WRITE_EXECUTED: NO
REAL_DATA_ACCESSED: NO
SOURCE_CODE_MODIFIED: NO
DEVELOPMENT_TEST_WORKSPACE_MUTATED: NO

==================================================
13. STOP POINT

Stop immediately after both conditions are satisfied:

1. a valid real Preview ID exists;
2. direct zero-write proof is complete.

Do not accept the Preview.
Do not reject the Preview unless deterministic validation itself fails.
Do not execute the write turn.
Do not close, discard, supersede, or recreate the active Preview.
Do not start Phase 2.

Preserve this exact Chat/session because Phase 2 must use:

* the exact Preview ID;
* the exact frozen artifact manifest;
* identical artifact content and hashes;
* the same workspace root;
* the same active Extension runtime.

==================================================
14. FINAL REPORT

Return:

ACTIVE_EXTENSION_ID: 
ACTIVE_EXTENSION_VERSION: 
RUNTIME_ACTIVATION_PROVEN: YES/NO
WORKSPACE_CLASSIFICATION: DEVELOPMENT_TEST_WORKSPACE/UNKNOWN
RUNTIME_TARGET_TYPE: 
RUNTIME_READY: YES/NO
RUNTIME_AVAILABLE: YES/NO
RUNTIME_BLOCKER_COUNT: 
RUNTIME_BLOCKERS: 
REPAIR_9_FRESH_CONSUMER_RUNTIME_PASS: YES/NO
WORKSPACE_ROOT: 
WORKSPACE_ROOT_COUNT: 
WORKFLOW_SETUP_ALREADY_PRESENT: YES/NO
STTM_INPUT_FOUND: YES/NO
EXISTING_JOB_CONF_COUNT: 
EXISTING_ENV_CONF_COUNT: 
EXISTING_GENERATED_ETL_ARTIFACT_COUNT: 
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

* active installed runtime version 0.3.142;
* exactly one correct Development Test Workspace root;
* Repair 9 fresh-consumer classification passes;
* runtime target type is consumer-etl-workspace;
* zero runtime blockers;
* CREATE_NEW_JOB;
* no Framework source requirement;
* trusted packaged contract resolves;
* at least one canonical module;
* final writer is path-based dataframe_writer;
* deterministic validation succeeds;
* a real Preview ID is issued;
* complete frozen artifact manifest is reported;
* every Preview path is inside the workspace root;
* zero workspace files are created, modified, or deleted;
* explicit approval remains pending;
* no write or real-data access occurs.

End exactly with one:

QA_PHASE_1_RESULT: PASS

QA_PHASE_1_RESULT: FAIL

QA_PHASE_1_RESULT: BLOCKED
