TASK: HF1_V2_REPAIR_10_SINGLE_FILE_MARKDOWN_STTM_AND_BUILD_0_3_143

Implement the bounded contract-first Repair 10 for deterministic support of a
single self-contained, sectioned Markdown STTM, then build and verify version
0.3.143.

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

This task implements Resolution A from the completed Root Cause 10 investigation:

Extend the trusted Markdown STTM contract so one self-contained .md document
containing explicitly recognized sections can be parsed as multiple logical STTM
sheets.

Do not implement a QA-specific workaround.
Do not modify the QA STTM.
Do not use LLM extraction, fuzzy inference, or guessing.
Do not redesign Excel parsing, existing Markdown bundles, targeted retrieval, or
Repairs 3–9.
Do not access etl-framework-adb.
Do not install or download dependencies.
Do not use npm version.
Do not create package-lock.json.
Do not use web search.
Do not modify protected .github/**.
Do not modify tests or baselines to hide failures.
Do not commit, push, merge, tag, stage, stash, reset, restore, clean, publish, or
install the resulting VSIX.
Do not start Runtime QA.
Do not create a Preview or execute a write.

==================================================

1. REPOSITORY IDENTITY AND BASELINE
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

Expected existing verified artifact:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.142.vsix

Expected 0.3.142 size:

1251308 bytes

Expected 0.3.142 SHA-256:

B392329A4B45C26D6DC17E91F14604B5731286F74B3AFE03603EE57A5F046E23

Expected QA STTM:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Expected QA STTM size:

1437 bytes

Expected QA STTM SHA-256:

F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Before editing, capture:

* repository identity;
* package version;
* complete Git status;
* staged file count;
* hashes of every tracked-modified and untracked file;
* exact 0.3.142 VSIX identity;
* exact QA STTM identity;
* whether a 0.3.143 VSIX already exists.

A dirty working-tree overlay is expected:

* 50 tracked-modified files;
* 28 untracked files;
* zero staged files.

Preserve all pre-existing changes exactly.

If identity differs or staged changes exist, stop:

REPAIR_10_RESULT: BLOCKED_IDENTITY_MISMATCH

If an unexpected 0.3.143 VSIX already exists, do not overwrite or delete it:

REPAIR_10_RESULT: BLOCKED_EXISTING_0_3_143_ARTIFACT

==================================================
2. AUTHORIZED CHANGE BOUNDARY

Primary authorized source paths:

* src/core/sttm/SttmMarkdownBundleParser.ts
* src/core/sttm/SttmReferenceResolver.ts
* src/core/solution/SttmEvidenceProvider.ts

Authorized contract/documentation paths:

* package.json
* resources/copilot/skills/etl-sttm-document-understanding/SKILL.md

Authorized test paths:

* src/test/suite/sttmMarkdownParser.test.ts
* a new synthetic fixture directory under:
    src/test/fixtures/sttm/synthetic_single_file_sectioned_markdown/**

Only if compilation proves an existing shared STTM type must change, stop before
editing that additional path and report:

REPAIR_10_RESULT: BLOCKED_SCOPE_EXPANSION_REQUIRED

Do not silently expand the source boundary.

The authorized package.json changes are:

1. version 0.3.142 → 0.3.143;
2. the existing etl_interpret_sttm.modelDescription text necessary to state the
    supported Markdown shapes accurately.

No other package.json field may change.

==================================================
3. CONTRACT DECISION

Implement this explicit supported-input contract:

1. .xlsx and .xlsm workbook input remains supported and unchanged.
2. Existing canonical Markdown bundle remains supported:
    * one .md file per logical Excel worksheet;
    * canonical sheet headings;
    * canonical Excel-style headers and IDs.
3. A new first-class single-file sectioned Markdown shape is supported:
    * one .md document;
    * one document title;
    * multiple explicitly recognized Markdown sections;
    * deterministic pipe tables within those sections;
    * mapping rows may use human-standard field names without canonical
        S_SCHM/T_SCHM/BR/TR/JC IDs.

Update both:

* package.json tool description;
* resources/copilot/skills/etl-sttm-document-understanding/SKILL.md.

The descriptions must distinguish:

* Markdown directory bundle;
* single-file sectioned Markdown;
* deterministic extraction requirements.

Do not imply that arbitrary prose Markdown can be interpreted structurally.

==================================================
4. CANONICAL SECTION SEGMENTATION

Implement segmentation only in the canonical Markdown parser:

src/core/sttm/SttmMarkdownBundleParser.ts

Do not add parsing logic to the ETL tool handler or Evidence Provider.

For each Markdown file:

* preserve the existing whole-file bundle behavior when it matches the canonical
    one-file-per-sheet contract;
* when one file contains multiple recognized section headings, segment it into
    logical sheets before classification;
* preserve the document title as document metadata, not as every logical sheet
    name;
* retain each section heading, scoped body, scoped tables, and source location.

Use a small explicit, reviewable, versioned heading alias map.

Required mapping-section normalized aliases include:

* column mapping
* field mapping
* field mappings

Normalization may include:

* case folding;
* trimming;
* collapsing repeated whitespace;
* deterministic removal of Markdown heading syntax.

Do not use substring matching such as “contains mapping”.
Do not use fuzzy matching.
Do not classify unrelated prose headings as mapping sections.

Recognized section headings must come from declared aliases for known STTM
logical sheets.

If duplicate or ambiguous mapping sections exist, reject them with an actionable
diagnostic. Do not silently select the first one.

==================================================
5. DETERMINISTIC MAPPING TABLE SELECTION

Within the recognized mapping logical sheet:

* do not assume tables[0];
* examine only tables scoped to that mapping section;
* select a table by an explicit deterministic header signature;
* require exactly one matching mapping table;
* reject zero or multiple matching tables with diagnostics.

Support the existing canonical header contract unchanged.

Add a declared secondary header-alias contract for the QA/human-readable shape:

* # — optional ordinal column and not machine authority;
* Source column — required;
* Source type — optional structured metadata;
* Target column — required;
* Target type — optional structured metadata;
* Transformation — optional structured mapping expression;
* Nullable — optional structured metadata.

Header normalization may perform only:

* case folding;
* trimming;
* deterministic whitespace normalization;
* declared exact alias lookup.

Do not accept arbitrary similar headers.

==================================================
6. DETERMINISTIC ROW VALIDATION

Preserve support for canonical S_SCHM/T_SCHM/BR/TR/JC row identifiers.

For the new single-file sectioned Markdown contract, accept a mapping row without
canonical IDs only when:

* normalized source field name is non-empty;
* normalized target field name is non-empty;
* the row belongs to the uniquely recognized mapping table;
* the table passed the declared header contract;
* the row structure is complete and unambiguous.

Do not invent fake schema IDs, business-rule IDs, transformation IDs, join IDs,
or trusted source/target authorities.

A row ordinal may be retained only as diagnostic provenance.

Do not derive physical source or target paths from the field mapping table.

Physical source/target paths remain separate explicit runtime evidence.

Reject:

* blank source fields;
* blank target fields;
* malformed rows;
* inconsistent column counts;
* duplicate ambiguous rows when the existing contract treats them as ambiguous;
* prose or code blocks masquerading as mapping rows.

For the exact unchanged QA STTM, the parser must return exactly six mappings.

==================================================
7. FAIL-CLOSED ZERO-EXTRACTION BEHAVIOR

Fix the contributing fail-open behavior.

Current defective behavior:

* recognizedSheets = 0;
* fieldMappings = 0;
* confidence reported as 0.90;
* tool status reported as read.

Required behavior:

* zero recognized sheets must produce an actionable
    STTM_SHEET_UNRECOGNIZED warning or stronger diagnostic;
* confidence must not remain high when no structured evidence was recognized;
* when the whole document yields both zero recognized sheets and zero mappings,
    SttmEvidenceProvider must return the existing appropriate blocking/non-success
    status;
* downstream planning must not proceed on an empty structured model.

Use existing status and diagnostic types.

Do not introduce a broad new public status model unless compilation proves it is
required; if required, stop with:

REPAIR_10_RESULT: BLOCKED_SCOPE_EXPANSION_REQUIRED

Valid recognized non-mapping sheets must not be incorrectly rejected merely
because they contain zero mappings.

==================================================
8. TRUST AND SECURITY BOUNDARIES

The implementation must preserve:

* deterministic parsing only;
* no LLM extraction;
* no fuzzy inference;
* no raw-prose guessing fallback;
* explicit section aliases;
* explicit header aliases;
* duplicate/ambiguity rejection;
* workspace-root containment;
* traversal rejection;
* UNC and different-drive rejection;
* advisory-only consumer context;
* trusted packaged contracts as machine authority;
* interpretation as zero-write;
* approval and guarded-write behavior unchanged.

A heading containing the word mapping in unrelated prose must not become a
trusted mapping section.

Do not use the QA filename, job name, malcode, ADLS paths, or six field names as
production-code conditions.

==================================================
9. REQUIRED TEST FIXTURE

Create a synthetic test fixture structurally equivalent to the QA input under:

src/test/fixtures/sttm/synthetic_single_file_sectioned_markdown/

The fixture must remain fully synthetic.

It must include:

* one document title;
* multiple H2 sections;
* a ## Column mapping section;
* at least one non-mapping table before the mapping table;
* mapping headers:
    | Source column | Source type | Target column | Target type |
    Transformation | Nullable
* exactly six mapping rows;
* no S_SCHM/T_SCHM/BR/TR/JC canonical IDs;
* synthetic source and target field names only;
* no real data or credentials.

Do not modify or copy the QA workspace file into the repository byte-for-byte if
a minimized structurally equivalent fixture is sufficient.

==================================================
10. REQUIRED TESTS

Add focused tests covering:

Positive:

1. exact single-file sectioned Markdown shape produces six mappings;
2. Column mapping exact normalized alias is recognized;
3. Field Mapping and Field Mappings declared aliases are recognized;
4. mapping table is selected by headers when it is not the first table;
5. rows without canonical IDs parse when deterministic source and target field
    names exist;
6. source type, target type, transformation, and nullable metadata are preserved;
7. CRLF UTF-8 without BOM parses correctly;
8. the existing canonical multi-file Markdown bundle produces byte/semantic
    equivalent output;
9. Excel STTM behavior remains unchanged.

Negative/security:

10. unrelated prose heading containing “mapping” is not recognized;
11. duplicate recognized mapping sections are rejected;
12. two header-matching mapping tables are rejected;
13. missing Source column is rejected;
14. missing Target column is rejected;
15. blank source/target rows are rejected;
16. malformed/inconsistent table rows are rejected;
17. zero recognized sheets does not return confidence 0.90;
18. zero recognized sheets plus zero mappings does not return status read;
19. workspace traversal/UNC/different-drive tests remain unchanged;
20. consumer context cannot influence heading or header recognition.

Tests must assert structured values, not only counts.

Do not weaken, delete, skip, quarantine, or rewrite existing tests to obtain a
pass.

==================================================
11. PRE-BUILD VALIDATION

Use only existing local dependencies and repository scripts.

Run and report:

1. TypeScript compile;
2. lint;
3. Repair 10 focused Markdown parser tests;
4. complete existing Markdown/Excel STTM parser suites;
5. SttmReferenceResolver tests;
6. SttmEvidenceProvider tests;
7. STTM auditor and agent-integration tests;
8. workspace containment/security tests;
9. Repair 9 fresh-consumer and classification parity tests;
10. trusted Job Config envelope direct suite;
11. Repair 8 focused suites;
12. Repair 5/6/7 regression suites;
13. full unit suite;
14. GitHub protected-path guard.

For every gate report:

* exact command;
* exit code;
* passing count;
* pending count;
* failure count;
* complete failure identities.

Known 0.3.142 full-unit baseline:

* passing: 2154;
* pending: 1;
* failing: 5.

The same five historical failures may remain only if their exact identities and
fingerprints are unchanged.

Required:

COMPILE_PASS: YES
LINT_PASS: YES
REPAIR_10_FOCUSED_PASS: YES
STTM_REGRESSION_SUITES_PASS: YES
REPAIR_9_REGRESSION_PASS: YES
REPAIR_8_REGRESSION_PASS: YES
REPAIR_5_6_7_REGRESSION_PASS: YES
TRUSTED_ENVELOPE_SUITE_PASS: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

If a required gate fails, do not modify tests or unrelated source to suppress it.
Stop:

REPAIR_10_RESULT: FAIL_VALIDATION_GATE

==================================================
12. EXACT QA INPUT OFFLINE PROOF

Read only this QA file:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Do not access any other QA workspace path.

Verify before and after:

SIZE:
1437 bytes

SHA-256:
F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Run the repaired source parser and compiled parser against the exact unchanged
bytes.

Required:

SOURCE_STRUCTURED_MAPPING_COUNT: 6
COMPILED_STRUCTURED_MAPPING_COUNT: 6
SOURCE_COMPILED_MAPPING_PAYLOAD_MATCH: YES
RECOGNIZED_MAPPING_SECTION: Column mapping
MAPPING_TABLE_SELECTED_BY_HEADERS: YES
RAW_CONTENT_GUESSING_USED: NO
ZERO_RECOGNIZED_SHEETS: NO
FAIL_OPEN_STATUS_RETURNED: NO
QA_STTM_MODIFIED: NO

Report the exact six extracted mappings.

Do not render artifacts or create a Preview.

==================================================
13. VERSION BUMP

Only after all pre-build validation passes, change package.json:

* version 0.3.142 → 0.3.143;
* update only the necessary etl_interpret_sttm.modelDescription wording for the
    expanded Markdown contract.

Do not use npm version.
Do not create or modify package-lock.json.

Run compile and Repair 10 focused tests again after the version edit.

==================================================
14. BUILD 0.3.143

Build exactly one final artifact:

databricks-etl-copilot-0.3.143.vsix

Expected path:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.143.vsix

Use the existing canonical packaging workflow and existing local dependencies.

Do not install, publish, tag, commit, or run Runtime QA.

==================================================
15. EXACT PACKAGE VERIFICATION

Run the existing exact-package verifier against the explicit 0.3.143 path.

Do not use newest-file selection.

Independently verify:

* archive readability;
* internal package.json version = 0.3.143;
* internal extension.vsixmanifest version = 0.3.143;
* publisher = td-etl;
* Extension ID = td-etl.databricks-etl-copilot;
* trusted contracts present and byte-equal to source;
* updated STTM skill documentation present;
* updated tool model description present;
* compiled repaired parser present;
* installed-layout contract resolution passes;
* no source checkout dependency;
* no etl-framework-adb dependency;
* no absolute machine path;
* package hygiene passes;
* no tests or test fixtures shipped unless package policy explicitly requires
    them;
* no .tmp/**, nested .git/**, .tsbuildinfo*, source tests, or out-test.

Run a packaged-parser proof against the exact unchanged QA STTM bytes without
installing the Extension.

Required:

PACKAGED_STRUCTURED_MAPPING_COUNT: 6
SOURCE_COMPILED_PACKAGED_PAYLOAD_MATCH: YES

==================================================
16. PACKAGE DELTA 0.3.142 TO 0.3.143

Compare normalized archive entry names and decompressed bytes.

Ignore ZIP timestamps.

Report:

* identical entries;
* changed entries;
* added entries;
* removed entries;
* exact reason for every changed entry.

Expected legitimate changes may include:

* package/manifest version metadata;
* compiled runtime bundle containing Repair 10;
* packaged STTM skill documentation;
* package.json model description.

No unrelated runtime or resource delta is permitted.

==================================================
17. REAL ARTIFACT IDENTITY

Compute from the actual final file:

FINAL_VSIX_PATH: 
FINAL_VSIX_SIZE_BYTES: 
FINAL_VSIX_SHA256: 

Do not predict or reuse a hash.

==================================================
18. POST-BUILD CHANGE BOUNDARY

Compare final repository status with the initial baseline.

Report separately:

* pre-existing changed paths;
* task-attributable source changes;
* task-attributable test/fixture changes;
* task-attributable contract/documentation changes;
* package.json version/model-description changes;
* generated compile/package output;
* unexpected changes;
* staged files.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
STAGED_FILES: 0
PACKAGE_LOCK_CREATED: NO
QA_STTM_MODIFIED: NO
QA_WORKSPACE_MUTATED: NO
EXISTING_0_3_142_VSIX_MODIFIED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
EXTENSION_INSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO

==================================================
19. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION_BEFORE: 0.3.142
SOURCE_VERSION_AFTER: 
CONTRACT_DECISION: SUPPORT_SINGLE_FILE_SECTIONED_MARKDOWN
AUTHORIZED_SOURCE_CHANGED_PATHS: 
AUTHORIZED_TEST_CHANGED_PATHS: 
AUTHORIZED_CONTRACT_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
SECTION_SEGMENTATION_IMPLEMENTED: YES/NO
EXPLICIT_MAPPING_ALIAS_SET: 
FUZZY_HEADING_MATCHING_USED: NO
MAPPING_TABLE_SELECTED_BY_HEADERS: YES/NO
HUMAN_HEADER_ALIAS_SET_IMPLEMENTED: YES/NO
ROWS_WITHOUT_CANONICAL_IDS_SUPPORTED_DETERMINISTICALLY: YES/NO
FAKE_IDS_SYNTHESIZED: NO
DUPLICATE_MAPPING_SECTION_REJECTED: YES/NO
AMBIGUOUS_MAPPING_TABLE_REJECTED: YES/NO
ZERO_EXTRACTION_FAIL_CLOSED: YES/NO
SOURCE_STRUCTURED_MAPPING_COUNT: 
COMPILED_STRUCTURED_MAPPING_COUNT: 
PACKAGED_STRUCTURED_MAPPING_COUNT: 
SOURCE_COMPILED_PACKAGED_PAYLOAD_MATCH: YES/NO
EXACT_QA_MAPPING_PAYLOAD: 
QA_STTM_SHA256_BEFORE: 
QA_STTM_SHA256_AFTER: 
QA_STTM_MODIFIED: NO
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_10_FOCUSED_PASS: YES/NO
STTM_REGRESSION_SUITES_PASS: YES/NO
REPAIR_9_REGRESSION_PASS: YES/NO
REPAIR_8_REGRESSION_PASS: YES/NO
REPAIR_5_6_7_REGRESSION_PASS: YES/NO
TRUSTED_ENVELOPE_SUITE_PASS: YES/NO
FULL_UNIT_PASSING_COUNT: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURES: 
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 
FINAL_EXACT_VSIX_VERIFIER_PASS: YES/NO
FINAL_INDEPENDENT_PACKAGE_INSPECTION_CLEAN: YES/NO
INTERNAL_PACKAGE_VERSION: 
INTERNAL_MANIFEST_VERSION: 
TRUSTED_CONTRACTS_SOURCE_PACKAGE_MATCH: YES/NO
PACKAGE_DELTA_EXPECTED_ONLY: YES/NO
FINAL_VSIX_PATH: 
FINAL_VSIX_SIZE_BYTES: 
FINAL_VSIX_SHA256: 
STAGED_FILES: 
PACKAGE_LOCK_CREATED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
EXTENSION_INSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
READY_TO_INSTALL_0_3_143: YES/NO
READY_FOR_RUNTIME_QA_PHASE_1: YES/NO
SAFE_TO_COMMIT: NO
SAFE_TO_RELEASE: NO

PASS requires:

* bounded contract extension implemented;
* single canonical parser;
* explicit aliases with no fuzzy matching;
* deterministic mapping-table selection;
* exact six mappings extracted from the unchanged QA STTM;
* zero-extraction fail-closed;
* all required focused/regression/security gates pass;
* zero new functional/security regressions;
* exact packaged parser returns the same six mappings;
* exact 0.3.143 package verification passes;
* actual size and SHA-256 calculated;
* zero unauthorized or staged changes;
* no install, Runtime QA, Preview, Write, commit, push, or tag.

End exactly with one:

REPAIR_10_RESULT: PASS

REPAIR_10_RESULT: FAIL_VALIDATION_GATE

REPAIR_10_RESULT: FAIL_PACKAGE_VERIFICATION

REPAIR_10_RESULT: FAIL_UNAUTHORIZED_CHANGE

REPAIR_10_RESULT: BLOCKED_IDENTITY_MISMATCH

REPAIR_10_RESULT: BLOCKED_EXISTING_0_3_143_ARTIFACT

REPAIR_10_RESULT: BLOCKED_SCOPE_EXPANSION_REQUIRED
