TASK: HF1_V2_ROOT_CAUSE_10_MARKDOWN_FIELD_MAPPING_ZERO_MAPPINGS

Perform a read-only root-cause investigation of the installed 0.3.142 Runtime QA
failure where the Markdown STTM Field Mapping section produced zero structured
mappings.

Work primarily inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

This is an investigation-only task.

Do not implement the repair.
Do not change the package version.
Do not modify source, tests, resources, contracts, prompts, baselines, or package
policy.
Do not rebuild or overwrite the 0.3.142 VSIX.
Do not install another Extension version.
Do not start Runtime QA.
Do not create a Preview.
Do not execute a filesystem write in the QA workspace.
Do not access real data.
Do not install or download dependencies.
Do not use web search.
Do not commit, push, merge, tag, stage, stash, reset, restore, clean, or delete
files.

A dirty source working tree is expected. Preserve it exactly.

==================================================

1. SOURCE REPOSITORY IDENTITY
    ==================================================

Expected repository root:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected origin:

https://github.com/TD-Universe/agentic_etl.git

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected working source version:

0.3.142

Expected verified VSIX:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.142.vsix

Expected VSIX size:

1251308 bytes

Expected VSIX SHA-256:

B392329A4B45C26D6DC17E91F14604B5731286F74B3AFE03603EE57A5F046E23

Capture before investigation:

* repository root;
* origin;
* branch;
* HEAD;
* package.json version;
* staged file count;
* complete tracked-modified and untracked path lists;
* VSIX path, size, and SHA-256.

If repository identity differs or staged files exist, stop without changing
anything:

ROOT_CAUSE_10_RESULT: BLOCKED_IDENTITY_MISMATCH

==================================================
2. AUTHORITATIVE RUNTIME FAILURE EVIDENCE

Treat the following as the authoritative observed 0.3.142 Runtime QA result:

ACTIVE_EXTENSION_ID:
td-etl.databricks-etl-copilot

ACTIVE_EXTENSION_VERSION:
0.3.142

RUNTIME_ACTIVATION_PROVEN:
YES

WORKSPACE_CLASSIFICATION:
DEVELOPMENT_TEST_WORKSPACE

RUNTIME_TARGET_TYPE:
consumer-etl-workspace

RUNTIME_READY:
YES

RUNTIME_AVAILABLE:
YES

RUNTIME_BLOCKER_COUNT:
0

REPAIR_9_FRESH_CONSUMER_RUNTIME_PASS:
YES

STTM_INPUT_FOUND:
YES

STTM_STRUCTURED_MAPPING_COUNT:
0

STTM_MAPPINGS:
none parsed by installed runtime parser

STTM_SOURCE_EVIDENCE:
none parsed

STTM_TARGET_EVIDENCE:
none parsed

STTM_FILTERS:
none parsed

STTM_WRITE_STRATEGY:
unresolved by parser

STTM_RAW_FALLBACK_REQUIRED:
YES

Observed parser warnings include:

* template variant unknown;
* fieldMapping missing;
* revisionHistory missing;
* businessRules missing;
* transformationRules missing;
* joinClauses missing;
* tableSchema missing;
* Markdown lossy-format warning.

The Runtime QA also performed a targeted retry for sheet/section:

Field Mapping

The targeted retry still returned zero mappings.

Because deterministic extraction failed:

* rendering was not attempted;
* validation was not attempted;
* Preview was not requested;
* Preview ID was not created;
* no workspace files were created, modified, or deleted;
* no write occurred.

This is not a Repair 9 classification regression.

==================================================
3. LIMITED QA INPUT ACCESS

The only Development Test Workspace file authorized for read-only inspection is:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Do not inspect any other QA workspace file or directory.

Before reading it, record:

* absolute path;
* size;
* SHA-256;
* encoding/BOM;
* newline style.

Read the file byte-for-byte and as decoded text.

After the investigation, recalculate its size and SHA-256 and prove it remains
unchanged.

Do not copy it into the source repository.

If a diagnostic script or capture is required, place it only in a unique
task-owned directory under %TEMP%, never inside either repository or QA
workspace. Report every temporary path created.

==================================================
4. DOCUMENT THE EXACT MARKDOWN SHAPE

Without changing the STTM, report:

* exact heading hierarchy;
* exact heading text and Markdown level for Field Mapping;
* whitespace before and after the heading text;
* whether the heading contains singular/plural wording;
* mapping-table column names in exact order;
* table delimiter/alignment row;
* exact number of mapping rows;
* whether cells contain code formatting, quotes, pipes, escaped characters,
    blank values, or multiline content;
* whether a code fence or HTML block surrounds the table;
* source section and physical path evidence;
* target section and physical path evidence;
* filter representation;
* writer strategy representation;
* encoding, BOM, and newline details.

Report the expected six mappings exactly as present in the STTM.

Do not infer or rewrite missing information.

==================================================
5. TRACE THE COMPLETE PARSER PATH

Trace the actual source path used by:

etl_interpret_sttm

for a .md input.

Identify, with exact files/functions:

1. tool request validation;
2. workspace/path resolution;
3. file type detection;
4. Markdown decoding;
5. template-variant detection;
6. section/sheet-name normalization;
7. Field Mapping alias resolution;
8. Markdown-table recognition;
9. table header mapping;
10. mapping-row extraction;
11. source/target/filter/write-strategy extraction;
12. raw-content fallback;
13. warning construction;
14. structured response serialization.

For every stage report:

* source file;
* function/class;
* relevant line or symbol;
* input shape;
* output shape;
* whether the exact QA STTM reaches the stage;
* whether information is discarded or renamed;
* exact reason the stage succeeds or fails.

Do not assume the failure is only a heading alias.

Prove the first point where the six mappings are lost.

==================================================
6. INSPECT ALL FORMAT AND ALIAS CONTRACTS

Search the source, tests, trusted packaged contracts, approved packaged examples,
compiled output, and exact VSIX for:

* Field Mapping;
* Field Mappings;
* fieldMapping;
* fieldMappings;
* mapping;
* Markdown STTM support;
* Markdown table parsing;
* sheet-name selection;
* template-variant detection;
* raw fallback;
* lossy-format warnings.

Determine:

* whether singular Field Mapping is supported;
* whether only an Excel sheet/object key is supported;
* whether Markdown headings are normalized into sheet names;
* whether heading case, spacing, punctuation, or Markdown level matters;
* whether parser code expects fieldMapping before Markdown conversion;
* whether table headers must match a fixed schema;
* whether Markdown input is intentionally supported by the public/runtime contract;
* whether the packaged examples contain a structurally equivalent Markdown STTM;
* whether current tests cover the exact QA format.

Do not treat consumer-editable examples or context as machine authority.

==================================================
7. REPRODUCE THE FAILURE DETERMINISTICALLY

Using only existing local dependencies and task-owned %TEMP% scratch files,
reproduce the parser behavior against the exact read-only STTM bytes.

Run the closest existing source and compiled parser entry points.

Where possible compare:

* source implementation;
* compiled out/** implementation;
* exact packaged VSIX implementation;
* installed Runtime QA result.

Required reproduction evidence:

* exact command or invocation;
* exit code;
* structured mapping count;
* extracted mapping payload;
* warnings;
* detected template variant;
* requested section/sheet name;
* raw fallback behavior.

Do not edit the STTM to make the parser pass.

You may construct temporary diagnostic variants under %TEMP% only to isolate
the predicate. If used, change exactly one characteristic per variant, such as:

* Field Mapping → Field Mappings;
* heading level;
* table column alias;
* removal of code formatting;
* newline style;
* BOM;
* section order.

For each variant report the one changed characteristic and result.

Diagnostic variants are evidence only and must not become the proposed solution
without contract analysis.

==================================================
8. DETERMINE THE ROOT-CAUSE CATEGORY

Classify the proven root cause using one or more exact categories:

* MARKDOWN_INPUT_NOT_ROUTED_TO_STRUCTURED_PARSER;
* FIELD_MAPPING_HEADING_ALIAS_MISSING;
* HEADING_NORMALIZATION_DEFECT;
* MARKDOWN_TABLE_HEADER_ALIAS_MISMATCH;
* MARKDOWN_TABLE_EXTRACTION_DEFECT;
* TEMPLATE_VARIANT_DETECTION_DEFECT;
* RAW_FALLBACK_DOES_NOT_EXTRACT_STRUCTURED_MAPPINGS;
* SOURCE_COMPILED_PACKAGE_DRIFT;
* QA_STTM_CONTRACT_MISMATCH;
* MULTIPLE_CONTRIBUTING_DEFECTS;
* OTHER_PROVEN_CAUSE.

Do not classify based only on symptom correlation.

Required:

FIRST_FAILED_FUNCTION: 
EXACT_FAILED_PREDICATE_OR_TRANSFORMATION: 
WHY_TARGETED_FIELD_MAPPING_RETRY_FAILED: 
WHY_RAW_FALLBACK_RETURNED_ZERO_MAPPINGS: 

==================================================
9. SECURITY AND TRUST BOUNDARY

The proposed repair must not turn arbitrary Markdown or raw consumer content into
machine authority.

Confirm that a safe repair would:

* extract mappings only from an explicitly recognized mapping section;
* require deterministic table headers;
* validate every row structure;
* reject duplicate or ambiguous mapping sections;
* reject malformed or incomplete rows;
* preserve path containment;
* preserve consumer-context advisory-only rules;
* preserve trusted packaged contracts as machine authority;
* preserve zero-write interpretation;
* preserve unsupported target diagnostics;
* fail closed when exact deterministic extraction is impossible.

Determine whether broad fuzzy heading matching would create a security or
correctness risk.

==================================================
10. EXISTING TEST COVERAGE AND MISSING TESTS

Report all existing relevant tests and what they actually cover.

Specifically determine whether tests cover:

* a real Markdown .md file;
* exact heading Field Mapping;
* exact QA mapping-table headers;
* six direct mappings;
* source and target ADLS paths;
* both QA filters;
* append-only dataframe writer evidence;
* singular/plural heading aliases;
* heading-level and whitespace normalization;
* duplicate mapping sections;
* malformed table rows;
* ambiguous headings;
* context/prompt injection near a mapping section;
* source/compiled/VSIX parity.

Identify the precise missing test that allowed version 0.3.142 to pass while the
installed runtime returned zero mappings.

==================================================
11. BOUNDED REPAIR PLAN — DO NOT IMPLEMENT

If the root cause is proven, propose the smallest safe Repair 10.

The plan must include:

* exact source paths to modify;
* exact functions/symbols to modify;
* whether a shared normalizer/parser must be reused or extracted;
* exact test paths to add or modify;
* positive tests;
* negative/security tests;
* regression suites;
* source/compiled/VSIX parity checks;
* installed-runtime QA repetition;
* expected version after repair: 0.3.143.

Prefer extending one canonical Markdown section/table parser.

Do not add independent parsing logic inside the ETL tool handler.
Do not use an LLM or guessing fallback to derive mappings.
Do not hard-code this specific job, path, field names, or STTM filename.
Do not weaken deterministic validation.
Do not redesign unrelated STTM formats or Repairs 3–9.

If the source contract explicitly does not support Markdown STTM, report that
honestly and propose the smallest contract-aligned resolution. Do not silently
change the QA input.

==================================================
12. CHANGE-BOUNDARY VERIFICATION

At the end, compare the repository and QA STTM against their initial baselines.

Required:

SOURCE_FILES_MODIFIED: 0
TEST_FILES_MODIFIED: 0
PACKAGE_JSON_MODIFIED: NO
VSIX_MODIFIED: NO
QA_STTM_MODIFIED: NO
QA_WORKSPACE_FILES_CREATED: 0
QA_WORKSPACE_FILES_MODIFIED: 0
QA_WORKSPACE_FILES_DELETED: 0
STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO

==================================================
13. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION: 
VSIX_PATH: 
VSIX_SIZE_BYTES: 
VSIX_SHA256: 
QA_STTM_PATH: 
QA_STTM_SIZE_BYTES_BEFORE: 
QA_STTM_SIZE_BYTES_AFTER: 
QA_STTM_SHA256_BEFORE: 
QA_STTM_SHA256_AFTER: 
QA_STTM_ENCODING: 
QA_STTM_NEWLINE_STYLE: 
FIELD_MAPPING_HEADING_EXACT: 
FIELD_MAPPING_HEADING_LEVEL: 
FIELD_MAPPING_TABLE_HEADERS: 
FIELD_MAPPING_ROW_COUNT: 
EXPECTED_MAPPING_COUNT_FROM_FILE: 
EXPECTED_MAPPINGS_FROM_FILE: 
SOURCE_EVIDENCE_IN_FILE: 
TARGET_EVIDENCE_IN_FILE: 
FILTER_EVIDENCE_IN_FILE: 
WRITE_STRATEGY_EVIDENCE_IN_FILE: 
MARKDOWN_RUNTIME_SUPPORT_CONTRACT: YES/NO/AMBIGUOUS
SOURCE_PARSER_REPRODUCED_ZERO: YES/NO
COMPILED_PARSER_REPRODUCED_ZERO: YES/NO
PACKAGED_PARSER_REPRODUCED_ZERO: YES/NO
SOURCE_COMPILED_VSIX_PARITY: PASS/FAIL/NOT_PROVEN
FIRST_FAILED_SOURCE_FILE: 
FIRST_FAILED_FUNCTION: 
EXACT_FAILED_PREDICATE_OR_TRANSFORMATION: 
WHY_TARGETED_FIELD_MAPPING_RETRY_FAILED: 
WHY_RAW_FALLBACK_RETURNED_ZERO_MAPPINGS: 
ROOT_CAUSE_CATEGORY: 
ROOT_CAUSE_PROVEN: YES/NO
EXISTING_RELEVANT_TESTS: 
MISSING_TEST_SCENARIOS: 
SECURITY_BOUNDARY_PRESERVED_BY_PLAN: YES/NO
PROPOSED_SOURCE_PATHS: 
PROPOSED_TEST_PATHS: 
PROPOSED_VERSION_AFTER_REPAIR: 0.3.143
SOURCE_FILES_MODIFIED: 0
TEST_FILES_MODIFIED: 0
PACKAGE_JSON_MODIFIED: NO
VSIX_MODIFIED: NO
QA_STTM_MODIFIED: NO
QA_WORKSPACE_FILES_CREATED: 0
QA_WORKSPACE_FILES_MODIFIED: 0
QA_WORKSPACE_FILES_DELETED: 0
STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
READY_FOR_BOUNDED_REPAIR_10: YES/NO

End exactly with one:

ROOT_CAUSE_10_RESULT: CONFIRMED_MARKDOWN_PARSER_DEFECT

ROOT_CAUSE_10_RESULT: CONFIRMED_QA_STTM_CONTRACT_MISMATCH

ROOT_CAUSE_10_RESULT: CONFIRMED_MULTIPLE_CAUSES

ROOT_CAUSE_10_RESULT: BLOCKED_INSUFFICIENT_EVIDENCE

ROOT_CAUSE_10_RESULT: BLOCKED_IDENTITY_MISMATCH
