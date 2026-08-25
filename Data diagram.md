TASK: HF1_V2_RUNTIME_QA_PHASE_1_PREVIEW_ONLY_0_3_144_REPAIR_11

Execute Phase 1 Runtime QA against the installed Databricks ETL Copilot extension
after Repair 11 finalization.

Run only in the already-open Development Test Workspace window after:

Developer: Reload Window

Use:

AGENT: ETL Orchestrator

Do not use a source-coding Agent, Claude coding session, Explore mode, or Plan
mode.

Bypass Permissions may remain enabled. It permits unattended tool execution but
is NOT explicit ETL approval and MUST NOT be interpreted as permission to accept
a Preview or perform a filesystem write.

This phase is PREVIEW ONLY.

==================================================

1. AUTHORIZED ENVIRONMENT
    ==================================================

Expected workspace root:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa

Expected workspace classification:

DEVELOPMENT_TEST_WORKSPACE

Expected extension identity:

EXTENSION_ID:
td-etl.databricks-etl-copilot

ACTIVE_RUNTIME_VERSION:
0.3.144

Expected topology:

* exactly one open workspace root;
* no extension-source checkout;
* no etl-framework-adb checkout;
* no existing job_conf/**;
* no existing env_conf/**;
* no existing generated ETL artifacts;
* ETL Copilot workflow assets already initialized;
* exact STTM present at:
    sttm/qa_hf1v2_demo_sttm.md

This workspace may not be a Git repository. Do not require Git metadata as
consumer-workspace evidence.

Do not access the Software Development Environment.
Do not inspect or modify extension source.
Do not access etl-framework-adb.
Do not install, build, or reinstall an extension.
Do not download dependencies.
Do not initialize, stage, commit, or push Git.
Do not execute a Databricks job.
Do not connect to ADLS, Databricks, Unity Catalog, or real data.
Do not modify workflow customization assets.
Do not modify the STTM.
Do not approve, consume, reject, close, or discard a valid Preview.
Do not execute any filesystem write.

==================================================
2. LIVE RUNTIME ACTIVATION GATE

Prove live activation from the reloaded QA Extension Host.

Use:

* etl_capabilities;
* live ETL Copilot Output;
* other installed runtime identity evidence exposed by the extension, if needed.

Required:

ACTIVE_EXTENSION_ID: td-etl.databricks-etl-copilot
ACTIVE_EXTENSION_VERSION: 0.3.144
RUNTIME_TARGET_TYPE: consumer-etl-workspace
RUNTIME_READY: YES
RUNTIME_AVAILABLE: YES
RUNTIME_BLOCKER_COUNT: 0

The live ETL Copilot Output must identify version 0.3.144.

An extension listing, VSIX filename, package.json, manifest, or CLI output alone
is not runtime activation proof.

If the active runtime is not exactly 0.3.144, or the workspace is not classified
as consumer-etl-workspace with zero blockers, stop before STTM interpretation,
discovery, rendering, validation, or Preview creation:

QA_PHASE_1_RESULT: BLOCKED_RUNTIME_IDENTITY

Do not reinstall from this workspace.

==================================================
3. FILESYSTEM BASELINE

Before STTM interpretation or Preview, capture a read-only filesystem baseline.

Record:

* absolute workspace root;
* workspace-root count;
* complete recursive file inventory;
* relative path, type, size, last-write time, and SHA-256 of every file;
* job_conf file count;
* env_conf file count;
* generated ETL artifact count;
* workflow customization paths and hashes;
* .github/** and resources/copilot/context/** hashes;
* STTM size, last-write time, and SHA-256;
* extension-source checkout absence;
* etl-framework-adb absence;
* active/pre-existing Preview ID count.

Expected STTM:

RELATIVE_PATH:
sttm/qa_hf1v2_demo_sttm.md

EXPECTED_SIZE_BYTES:
1437

EXPECTED_SHA256:
F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Expected initial state:

EXISTING_JOB_CONF_COUNT: 0
EXISTING_ENV_CONF_COUNT: 0
EXISTING_GENERATED_ETL_ARTIFACT_COUNT: 0
EXISTING_ACTIVE_PREVIEW_COUNT: 0

Do not create a baseline file inside the workspace. Keep comparison data in
session memory or a task-owned temporary path outside the workspace.

If the STTM identity or workspace baseline conflicts, stop without Preview:

QA_PHASE_1_RESULT: BLOCKED_INPUT_OR_WORKSPACE

==================================================
4. FIXED QA JOB CONTRACT

Use these fixed values without asking the user again.

JOB_NAME:
qa_hf1v2_demo

MALCODE:
acz9999

ENVIRONMENT:
dev

STRATEGY:
generic_dataframe_write

SOURCE_TYPE:
Delta

SOURCE_PHYSICAL_MODE:
ADLS-path-backed

SOURCE_PATH:
abfss://qa@qaetlhf1v2dev.dfs.core.windows.net/raw/qa_hf1v2_customer

TARGET_TYPE:
Delta

TARGET_PHYSICAL_MODE:
ADLS-path-backed

TARGET_PATH:
abfss://qa@qaetlhf1v2dev.dfs.core.windows.net/curated/qa_hf1v2_customer

OUTPUT_FORMAT:
delta

WRITE_MODE:
append

PRIMARY_KEY:
customer_id

The primary key is informational for this append-only QA case.

Explicitly excluded:

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

Logical raw/curated evidence in the STTM must not be converted into direct Unity
Catalog table identifiers. The fixed physical destination remains the ADLS path.

==================================================
5. REPAIR 11 LIVE STTM INTERPRETATION

Invoke the installed 0.3.144 runtime against exactly:

sttm/qa_hf1v2_demo_sttm.md

Use etl_interpret_sttm and installed runtime tools only.

Do not:

* enumerate or read sibling files;
* replace the requested file with its parent-directory Markdown bundle;
* use raw-content guessing;
* use an LLM fallback;
* fabricate source, target, filter, note, schema, or mapping values.

Required structured result:

STTM_FILES_PARSED: 1
STTM_SECTIONS_TOTAL: 5
STTM_SECTIONS_RECOGNIZED: 5

Recognized sections:

* Source;
* Target;
* Column mapping;
* Filters;
* Notes.

Required mappings in document order:

1. customer_id -> customer_id
2. first_name -> first_name
3. last_name -> last_name
4. email -> email_address
5. status_cd -> status_code
6. updated_ts -> updated_ts

Required evidence:

STTM_STRUCTURED_MAPPING_COUNT: 6
STTM_SOURCE_EVIDENCE_COUNT: 1
STTM_TARGET_EVIDENCE_COUNT: 1
STTM_SCHEMA_EVIDENCE_COUNT: 2
STTM_FILTER_COUNT: 2
STTM_NOTES_COUNT: 2

Required literal filters:

* status_cd IS NOT NULL
* updated_ts >= ${etl.effective.start.date}

The following obsolete expectations are forbidden and must not be substituted:

* status_code = ‘ACTIVE’
* updated_ts IS NOT NULL

Report Source and Target sections verbatim, including exact logical identifiers.

Expected logical evidence:

SOURCE_LOGICAL_EVIDENCE:
raw.qa_hf1v2_customer

TARGET_LOGICAL_EVIDENCE:
curated.qa_hf1v2_customer

These are logical STTM values, not direct Unity Catalog write targets.

The exact STTM bytes remain authoritative. If an identifier differs, report the
exact file value and stop rather than guessing or silently normalizing it.

Required Repair 11 behavior:

* sibling files enumerated: NO;
* sibling evidence returned: NO;
* mappings remain in document order;
* mapping IDs, if exposed, are unique;
* mapping IDs contain no absolute machine path;
* obsolete values fabricated: NO;
* material sections silently dropped: NO;
* raw fallback required: NO.

Expected non-blocking information diagnostics may include:

* STTM_MARKDOWN_LOSSY_FORMATTING;
* STTM_XLSX_REQUIRED_FOR_FORMATTING_VERIFICATION.

These may be reported only at information level. There must be no blocking,
warning, or error diagnostic for an unrecognized material section, including:

STTM_MATERIAL_SECTION_UNRECOGNIZED

The following results are failures:

* zero or fewer than six mappings;
* fewer than five recognized sections;
* missing Source, Target, Filters, or Notes;
* a successful/high-confidence result with a material section dropped;
* source or target inferred from unrelated prose;
* direct table-name or Unity Catalog inference;
* raw fallback or guessing.

If any required result differs, stop before discovery, rendering, validation, or
Preview:

QA_PHASE_1_RESULT: FAIL_STTM_RUNTIME

==================================================
6. TRUSTED FRAMEWORK-INDEPENDENT DISCOVERY

Only after the STTM gate passes, use installed runtime tools such as:

* etl_capabilities;
* etl_get_framework_rules;
* etl_search_examples;
* etl_describe_module;
* etl_interpret_sttm.

Verify:

* framework-source checkout is absent;
* framework source is not required;
* packaged framework fallback is active;
* trusted Job Config envelope contract resolves from installed packaged resources;
* criticalConfigKeys are non-empty;
* approved packaged examples are searchable without a local Framework root;
* installed-layout resolution passes;
* consumer resources/copilot/context/** files are advisory only;
* consumer context is never used as machine authority.

Machine authority must come from installed trusted runtime code and packaged
resources, including:

resources/framework/contracts/**

Do not recover syntax from the Software Development Environment.
Do not infer contracts from consumer-authored context.

If packaged contract, critical keys, or examples cannot resolve, stop:

QA_PHASE_1_RESULT: FAIL_PACKAGED_DISCOVERY

==================================================
7. TARGET DECISION AND CANONICAL CONFIG

Because no job_conf or env_conf exists for this job, require:

TARGET_DECISION: CREATE_NEW_JOB
FRAMEWORK_SOURCE_REQUIRED: NO

Generate the proposed Job Config only from:

* exact structured STTM model;
* fixed physical QA inputs;
* trusted packaged contract;
* trusted packaged examples.

Required canonical envelope:

modules {
<stage_key> {
…
options {
module = <module_type>
method = process
}
}
}

Validate:

* modules is an object, not an array;
* stages are keyed by stage name;
* every stage has options.module;
* executable stages have required method/options;
* mappings preserve STTM document order;
* both literal filters are preserved;
* final writer is dataframe_writer;
* destination is the fixed ADLS target path;
* format is delta;
* mode is append;
* no merge, CDC, SCD2, database_out, or direct Unity Catalog target;
* no quoted-JSON modules envelope;
* no noncanonical top-level module blocks;
* no invented source, target, filter, schema, or note value.

If deterministic rendering or validation fails, stop without Preview:

QA_PHASE_1_RESULT: FAIL_DETERMINISTIC_VALIDATION

==================================================
8. COMPLETE PREVIEW ARTIFACT SET

Render and validate the proposed artifact set in memory.

It must contain at least:

* one Job Config;
* one Environment Config.

Likely canonical paths include:

job_conf/conf/acz9999/qa_hf1v2_demo.json
env_conf/dev/env_conf_dev_qa_hf1v2_demo.yaml

Do not force these paths if the installed trusted contract deterministically
produces other canonical consumer-relative paths. Report the actual paths and
contract evidence.

Additional SQL/include artifacts are permitted only when deterministically
required. Do not create convenience artifacts.

Every proposed path must:

* resolve inside the single Development Test Workspace root;
* pass traversal and containment validation;
* be absent from the filesystem before Preview.

For every artifact report:

* relative path;
* normalized absolute destination;
* artifact type;
* disposition;
* SHA-256 of exact proposed content;
* writable decision;
* deterministic validation result;
* reason/evidence.

==================================================
9. REQUEST EXACTLY ONE REAL PREVIEW

Only after all preceding gates pass, invoke the installed guarded-write workflow
exactly once and only far enough to create a Preview record.

Use the canonical guarded-write tool exposed by etl_capabilities.

For the first request:

* do not provide previewId;
* do not provide approval;
* do not set accept, consume, or write to true;
* submit the complete validated manifest and exact proposed contents;
* request Preview only.

Required result:

* a real extension-issued Preview ID;
* complete manifest frozen;
* exact proposed-content hashes frozen;
* deterministic validation passed;
* zero files created;
* zero files modified;
* zero files deleted;
* explicit ETL approval required;
* approval still pending;
* write authorization not consumed.

Bypass Permissions is not ETL approval.

Do not:

* fabricate a Preview ID;
* invoke a second guarded-write turn;
* call beginConsume;
* accept the Preview;
* reject the Preview;
* approve the Preview;
* write an artifact;
* close or discard the Preview state.

If no real Preview ID is issued, report the exact runtime failure and stop:

QA_PHASE_1_RESULT: FAIL_PREVIEW_CREATION

==================================================
10. POST-PREVIEW ZERO-WRITE PROOF

Immediately after Preview creation, compare the workspace with the baseline.

Verify:

* no job_conf/** exists;
* no env_conf/** exists;
* no include or SQL artifact exists;
* no artifact exists merely because it appeared in the Preview manifest;
* no existing file size, hash, or last-write time changed;
* STTM size, hash, and last-write time remain identical;
* workflow customization hashes remain identical;
* .github/** and context hashes remain identical;
* no file was created, modified, renamed, or deleted;
* no protected root was changed;
* no real data was accessed;
* no Preview approval was consumed.

Required:

PREVIEW_ZERO_NEW_FILES: YES
PREVIEW_ZERO_MODIFIED_FILES: YES
PREVIEW_ZERO_DELETED_FILES: YES
STTM_UNCHANGED: YES
WORKFLOW_CUSTOMIZATION_UNCHANGED: YES
WRITE_EXECUTED: NO
DEVELOPMENT_TEST_WORKSPACE_MUTATED: NO

If any delta exists, report it and fail. Do not delete, restore, clean, or repair
the evidence.

==================================================
11. REQUIRED STOP POINT

Stop immediately after obtaining:

1. a real Preview ID;
2. direct zero-write proof.

Preserve this exact Chat/session and active Preview state. Phase 2 must use the
same Preview ID and byte-identical manifest/content.

Do not continue to approval or write testing.

==================================================
12. FINAL REPORT

Return:

ACTIVE_EXTENSION_ID: 
ACTIVE_EXTENSION_VERSION: 
RUNTIME_ACTIVATION_PROVEN: YES/NO
RUNTIME_TARGET_TYPE: 
RUNTIME_READY: YES/NO
RUNTIME_AVAILABLE: YES/NO
RUNTIME_BLOCKER_COUNT: 

WORKSPACE_CLASSIFICATION: 
WORKSPACE_ROOT: 
WORKSPACE_ROOT_COUNT: 
WORKFLOW_SETUP_ALREADY_PRESENT: YES/NO
SOURCE_CHECKOUT_PRESENT: YES/NO
ETL_FRAMEWORK_ADB_PRESENT: YES/NO

STTM_INPUT_FOUND: YES/NO
STTM_SIZE_BYTES: 
STTM_SHA256: 
STTM_FILES_PARSED: 
STTM_SECTIONS_TOTAL: 
STTM_SECTIONS_RECOGNIZED: 
STTM_RECOGNIZED_SECTION_LIST: 
STTM_STRUCTURED_MAPPING_COUNT: 
STTM_MAPPINGS: 
STTM_MAPPING_IDS_UNIQUE: YES/NO/NOT_EXPOSED
STTM_SOURCE_EVIDENCE_COUNT: 
STTM_SOURCE_EVIDENCE: 
STTM_TARGET_EVIDENCE_COUNT: 
STTM_TARGET_EVIDENCE: 
STTM_SCHEMA_EVIDENCE_COUNT: 
STTM_FILTER_COUNT: 
STTM_FILTERS: 
STTM_NOTES_COUNT: 
STTM_RAW_FALLBACK_REQUIRED: YES/NO
STTM_SIBLING_FILES_ENUMERATED: YES/NO
STTM_SIBLING_EVIDENCE_RETURNED: YES/NO
STTM_PARSER_WARNINGS: 
STTM_MATERIAL_SECTION_LOSS: YES/NO

CONTEXT_FILES_CONSUMED: 
CONSUMER_CONTEXT_USED_AS_MACHINE_AUTHORITY: NO
FRAMEWORK_SOURCE_REQUIRED: YES/NO
PACKAGED_CONTRACT_RESOLVED: YES/NO
CRITICAL_CONFIG_KEYS_COUNT: 
PACKAGED_EXAMPLE_SEARCH_PASS: YES/NO

TARGET_DECISION: 
CANONICAL_MODULE_ENVELOPE: YES/NO
MODULE_COUNT: 
DATAFRAME_WRITER_PATH_BASED: YES/NO
SOURCE_PHYSICAL_PATH_BASED: YES/NO
TARGET_PHYSICAL_PATH_BASED: YES/NO
WRITE_MODE_APPEND: YES/NO
UNITY_CATALOG_DIRECT_WRITE_REQUESTED: NO
OBSOLETE_FILTER_VALUE_FABRICATED: NO
DETERMINISTIC_VALIDATION_PASS: YES/NO

PREVIEW_ID: 
PREVIEW_ARTIFACT_COUNT: 
PREVIEW_ARTIFACT_MANIFEST: <complete list with path, type, disposition, SHA-256,
containment, and validation>
PREVIEW_PATHS_INSIDE_WORKSPACE_ROOT: YES/NO
PREVIEW_ZERO_NEW_FILES: YES/NO
PREVIEW_ZERO_MODIFIED_FILES: YES/NO
PREVIEW_ZERO_DELETED_FILES: YES/NO
EXPLICIT_APPROVAL_REQUIRED: YES/NO
APPROVAL_STILL_PENDING: YES/NO
WRITE_AUTHORIZATION_CONSUMED: YES/NO
WRITE_EXECUTED: NO

STTM_UNCHANGED: YES/NO
WORKFLOW_CUSTOMIZATION_UNCHANGED: YES/NO
SOURCE_CODE_MODIFIED: NO
REAL_DATA_ACCESSED: NO
DEVELOPMENT_TEST_WORKSPACE_MUTATED: NO
REPAIR_11_LIVE_RUNTIME_PASS: YES/NO
CHAT_AND_PREVIEW_STATE_PRESERVED: YES/NO

PASS requires:

* active runtime exactly 0.3.144;
* exactly one valid Development Test Workspace root;
* consumer-etl-workspace classification with zero blockers;
* exact STTM identity;
* exactly one requested STTM file and no sibling enumeration;
* all five material sections recognized;
* exactly six ordered mappings;
* exact Source and Target evidence;
* exact two current QA filters;
* no obsolete filter fabrication;
* no raw fallback;
* trusted packaged contract and examples resolved;
* CREATE_NEW_JOB;
* canonical modules-object envelope;
* path-backed Delta dataframe_writer in append mode;
* deterministic validation success;
* a real Preview ID;
* complete frozen artifact manifest;
* zero workspace writes;
* explicit approval still pending.

End exactly with one:

QA_PHASE_1_RESULT: PASS
QA_PHASE_1_RESULT: FAIL_STTM_RUNTIME
QA_PHASE_1_RESULT: FAIL_PACKAGED_DISCOVERY
QA_PHASE_1_RESULT: FAIL_DETERMINISTIC_VALIDATION
QA_PHASE_1_RESULT: FAIL_PREVIEW_CREATION
QA_PHASE_1_RESULT: BLOCKED_RUNTIME_IDENTITY
QA_PHASE_1_RESULT: BLOCKED_INPUT_OR_WORKSPACE
