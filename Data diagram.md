TASK: INDEPENDENT_REVIEW_HF1_V2_REPAIR_10_AND_VSIX_0_3_143

Perform an independent, adversarial, read-only review of Repair 10 and the
already-built VSIX version 0.3.143.

Work inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

This review must be performed in a fresh Chat that did not implement Repair 10.

Do not trust the implementation report as proof.
Independently inspect the actual source, tests, working-tree diff, compiled output,
package contents, and exact QA-input behavior.

Do not modify or repair any file.
Do not change tests or baselines.
Do not change package.json.
Do not rebuild or overwrite the VSIX.
Do not install the Extension.
Do not start Runtime QA.
Do not create a Preview or execute a write.
Do not access real data.
Do not install or download dependencies.
Do not use web search.
Do not commit, push, merge, tag, stage, stash, reset, restore, clean, or delete
files.

If a defect is found, report it with evidence. Do not fix it during this review.

==================================================

1. IDENTITY AND ARTIFACT GATE
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

0.3.143

Expected staged file count:

0

Expected VSIX:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.143.vsix

Expected VSIX size:

1255490 bytes

Expected VSIX SHA-256:

8819E0902BF5FE1F8EFE9BA302EB196D3715AF17DC5F44876E3C0EACBD03CFFA

Expected internal package version:

0.3.143

Expected internal manifest version:

0.3.143

Capture:

* repository identity;
* complete Git status;
* staged paths;
* package version;
* VSIX path, size, SHA-256;
* archive identity;
* internal Extension ID and publisher.

If identity differs, stop:

INDEPENDENT_REVIEW_0_3_143_RESULT: BLOCKED_IDENTITY_MISMATCH

==================================================
2. REVIEW THE ACTUAL CHANGE SET

Inspect the complete actual implementation, not only the summarized file list.

Reported Repair 10 paths include:

Source:

* src/core/sttm/SttmMarkdownBundleParser.ts
* src/core/sttm/SttmReferenceResolver.ts
* src/core/solution/SttmEvidenceProvider.ts

Tests and fixture:

* src/test/suite/sttmMarkdownParser.test.ts
* src/test/fixtures/sttm/synthetic_single_file_sectioned_markdown/**

Contract/documentation:

* package.json
* resources/copilot/skills/etl-sttm-document-understanding/SKILL.md

Determine independently:

* the complete changed-path list attributable to Repair 10;
* whether any implementation change exists outside the authorized scope;
* whether unrelated Repairs 3–9 behavior changed;
* whether pre-existing working-tree changes were overwritten or reformatted;
* whether package.json changed only in version and
    etl_interpret_sttm.modelDescription;
* whether protected .github/** remained unchanged.

Report every unauthorized or unexplained change.

==================================================
3. CONTRACT REVIEW

Verify that the implementation explicitly supports three distinct shapes:

1. Excel .xlsx/.xlsm;
2. canonical multi-file Markdown bundle;
3. single-file sectioned Markdown.

Confirm that the updated package.json model description and packaged STTM skill
describe these shapes consistently and unambiguously.

Check that:

* the contract does not claim arbitrary Markdown support;
* consumers can understand the difference between a bundle and a sectioned file;
* single-file support is implemented as a first-class contract;
* the behavior is not hard-coded to the QA filename, job, malcode, paths, IDs, or
    field names;
* the documentation and runtime behavior agree.

==================================================
4. SECTION SEGMENTATION REVIEW

Review the actual section-segmentation algorithm.

Confirm:

* the document title is metadata and not reused as every sheet name;
* multiple recognized sections become scoped logical sheets;
* section bodies and tables do not leak into adjacent sections;
* existing canonical one-file-per-sheet bundle behavior remains unchanged;
* files without recognized sectioned-document structure preserve valid legacy
    behavior;
* duplicate and ambiguous sections are rejected;
* unrecognized headings do not become trusted sections.

Inspect the exact alias implementation.

Required declared mapping aliases should include normalized forms of:

* column mapping;
* column mappings;
* field mapping;
* field mappings.

Reject the review if production logic uses:

* substring matching;
* regex that broadly accepts anything containing mapping;
* fuzzy matching;
* LLM classification;
* consumer-context-controlled aliases;
* first-heading or first-section guessing.

Test boundary cases independently using %TEMP% only:

* alias with different case;
* leading/trailing whitespace;
* repeated whitespace;
* unrelated prose heading containing “mapping”;
* Mapping notes;
* duplicate Column mapping sections;
* mapping heading inside a code fence;
* mapping-like text inside a table cell;
* H1 document title plus H2 sections;
* multiple non-mapping sections before and after the mapping section.

Do not write these probes into the repository.

==================================================
5. MAPPING TABLE SELECTION REVIEW

Confirm the parser:

* scopes tables to the recognized mapping section;
* does not use tables[0];
* selects by deterministic declared headers;
* requires exactly one matching table;
* rejects zero or multiple matching mapping tables.

Review both canonical and human-readable header aliases.

Required human-readable fields:

* Source column;
* Target column.

Supported optional fields:

* Source type;
* Target type;
* Transformation;
* Nullable;
* ordinal #.

Verify normalization is bounded to explicit deterministic behavior.

Reject if arbitrary similar headers are accepted.

Independently test:

* a non-mapping table before the mapping table;
* two mapping-compatible tables;
* missing Source column;
* missing Target column;
* duplicated header names;
* extra unknown columns;
* reordered supported columns;
* malformed delimiter rows;
* uneven row widths.

==================================================
6. ROW VALIDATION AND IDENTITY REVIEW

Confirm:

* canonical S_SCHM/T_SCHM/BR/TR/JC rows still work unchanged;
* human-readable rows require non-empty deterministic source and target fields;
* no fake canonical IDs are created;
* row ordinal is diagnostic provenance only;
* blank or malformed rows are rejected;
* physical source/target paths are not invented from field mappings;
* no consumer prose becomes trusted physical authority.

Inspect the exact six mappings produced from the QA STTM and ensure they match the
actual six table rows without substitution, omission, reordering, or guessed
content.

==================================================
7. FAIL-CLOSED REVIEW

Independently inspect:

* SttmReferenceResolver confidence calculation;
* SttmEvidenceProvider status selection;
* diagnostics returned for unrecognized documents.

Confirm that the previous defect is closed:

Previous invalid behavior:

* recognizedSheets = 0;
* mappings = 0;
* confidence = 0.90;
* status = read.

Required behavior:

* zero recognized sheets produces an actionable diagnostic;
* confidence is capped/floored to a safe non-success value;
* zero recognized sheets plus zero mappings cannot return successful read;
* downstream planning cannot continue with an empty structured model.

Also prove the fix does not incorrectly block:

* recognized business-rule-only input;
* recognized filter-only input;
* valid canonical bundles;
* valid Excel workbooks;
* targeted read operations that legitimately return no mappings.

Reject overly broad fail-closed logic that treats every zero-mapping partial
document as invalid.

==================================================
8. SECURITY AND TRUST REVIEW

Attempt to falsify the implementation’s security claims.

Verify:

* no LLM extraction;
* no raw-prose guessing fallback;
* no fuzzy heading/header inference;
* no consumer-controlled alias registration;
* no consumer context used as machine authority;
* duplicate/ambiguity rejection;
* deterministic output;
* path containment unchanged;
* traversal rejection unchanged;
* UNC and different-drive rejection unchanged;
* interpretation remains zero-write;
* Preview/approval/write behavior is untouched.

Search for any newly introduced direct filesystem mutation.

A Markdown parser must not write, rename, create, or delete consumer files.

==================================================
9. TEST QUALITY REVIEW

Inspect every Repair 10 test and fixture.

Confirm tests assert actual structured values, not only counts.

Verify coverage includes:

* exact single-file sectioned Markdown shape;
* exactly six mappings;
* mapping section not first;
* mapping table not first;
* declared aliases;
* human-readable headers;
* rows without canonical IDs;
* canonical bundle regression;
* Excel regression;
* duplicate sections;
* ambiguous tables;
* unrelated mapping prose;
* malformed rows;
* zero-extraction fail-closed;
* containment/security regressions.

Check for false-positive testing patterns:

* assertions against implementation constants only;
* snapshots created from current defective output;
* tautological source/expected construction;
* mocked code path different from production;
* skipped or quarantined failures;
* overly broad assertions;
* tests that never invoke the actual production parser;
* fixture content that is easier than the real QA shape.

Identify every missing negative or boundary test.

==================================================
10. INDEPENDENT VALIDATION

Use only existing local dependencies.

Run independently:

1. compile;
2. lint;
3. Repair 10 focused tests;
4. complete Markdown and Excel parser suites;
5. SttmReferenceResolver tests;
6. SttmEvidenceProvider tests;
7. STTM auditor and agent-integration tests;
8. workspace containment/security tests;
9. Repair 9 classification parity;
10. Repairs 5–8 regression suites;
11. trusted Job Config envelope suite;
12. full unit suite;
13. GitHub protected-path guard.

Expected implementation report baseline:

* full-unit passing: 2180;
* pending: 1;
* historical failures: 5;
* new functional regressions: 0;
* new security regressions: 0.

Do not accept historical failures by count alone.

Verify the exact identities and fingerprints of all five failures.

Do not edit anything if a test fails.

==================================================
11. EXACT QA INPUT REVIEW

The only QA workspace file authorized for read-only inspection is:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Expected size:

1437 bytes

Expected SHA-256:

F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Do not inspect any other QA workspace path.

Using task-owned %TEMP% probes only, independently run:

* source parser;
* compiled parser;
* parser extracted from the exact VSIX.

Required:

SOURCE_MAPPING_COUNT: 6
COMPILED_MAPPING_COUNT: 6
PACKAGED_MAPPING_COUNT: 6
SOURCE_COMPILED_PACKAGED_PAYLOAD_MATCH: YES
QA_STTM_MODIFIED: NO
RAW_OR_LLM_FALLBACK_USED: NO

Report all six mappings completely.

==================================================
12. PACKAGE REVIEW

Run the exact package verifier against this explicit path:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.143.vsix

Do not select by newest modification time.

Verify independently:

* internal package version 0.3.143;
* internal manifest version 0.3.143;
* publisher td-etl;
* Extension ID td-etl.databricks-etl-copilot;
* trusted contracts present and byte-equal to source;
* updated STTM skill present;
* updated model description present;
* repaired compiled parser present;
* package hygiene clean;
* no source-checkout dependency;
* no etl-framework-adb dependency;
* no absolute development-machine path;
* no test fixture accidentally shipped.

Compare decompressed 0.3.142 and 0.3.143 packages.

Expected report:

* 66 entries in each;
* 61 identical;
* 0 added;
* 0 removed;
* 5 changed.

Report the exact five changed entries and justify each one.

Any unrelated package delta is a blocking finding.

Recalculate:

VSIX_SIZE_BYTES:
1255490

VSIX_SHA256:
8819E0902BF5FE1F8EFE9BA302EB196D3715AF17DC5F44876E3C0EACBD03CFFA

==================================================
13. FINDINGS FORMAT

Classify every finding:

* BLOCKER;
* HIGH;
* MEDIUM;
* LOW;
* INFORMATIONAL.

For every non-informational finding provide:

* severity;
* exact file and symbol;
* evidence;
* reproducible scenario;
* impact;
* violated contract or security boundary;
* smallest recommended correction;
* missing test that should detect it.

Do not mark the review PASS if any BLOCKER or HIGH finding exists.

A MEDIUM finding must be explicitly evaluated for whether it blocks Runtime QA.

Do not repair findings in this task.

==================================================
14. CHANGE-BOUNDARY VERIFICATION

Compare repository, VSIX, and QA STTM with their initial review baselines.

Required:

SOURCE_FILES_MODIFIED_BY_REVIEW: 0
TEST_FILES_MODIFIED_BY_REVIEW: 0
PACKAGE_JSON_MODIFIED_BY_REVIEW: NO
VSIX_MODIFIED_BY_REVIEW: NO
QA_STTM_MODIFIED_BY_REVIEW: NO
STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
EXTENSION_INSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO

Temporary diagnostic files may exist only under a task-owned %TEMP% directory
and must be reported.

==================================================
15. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION: 
VSIX_PATH: 
VSIX_SIZE_BYTES: 
VSIX_SHA256: 
ARTIFACT_IDENTITY_MATCH: YES/NO
ACTUAL_REPAIR_10_CHANGED_PATHS: 
UNAUTHORIZED_OR_UNEXPLAINED_PATHS: 
CONTRACT_IMPLEMENTATION_MATCH: YES/NO
DOCUMENTATION_RUNTIME_CONSISTENT: YES/NO
CANONICAL_BUNDLE_REGRESSION_PASS: YES/NO
EXCEL_REGRESSION_PASS: YES/NO
SECTION_SCOPING_CORRECT: YES/NO
EXPLICIT_ALIAS_MATCHING_ONLY: YES/NO
FUZZY_OR_SUBSTRING_MATCHING_FOUND: YES/NO
MAPPING_TABLE_SELECTED_DETERMINISTICALLY: YES/NO
DUPLICATE_SECTION_REJECTION_PASS: YES/NO
AMBIGUOUS_TABLE_REJECTION_PASS: YES/NO
ROWS_WITHOUT_CANONICAL_IDS_SAFE: YES/NO
FAKE_IDS_FOUND: YES/NO
ZERO_EXTRACTION_FAIL_CLOSED: YES/NO
VALID_PARTIAL_DOCUMENTS_PRESERVED: YES/NO
DIRECT_FILESYSTEM_MUTATION_INTRODUCED: YES/NO
CONSUMER_CONTEXT_USED_AS_AUTHORITY: YES/NO
SOURCE_MAPPING_COUNT: 
COMPILED_MAPPING_COUNT: 
PACKAGED_MAPPING_COUNT: 
SOURCE_COMPILED_PACKAGED_PAYLOAD_MATCH: YES/NO
EXACT_SIX_MAPPINGS: 
QA_STTM_MODIFIED: YES/NO
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
FOCUSED_TESTS_PASS: YES/NO
STTM_REGRESSION_TESTS_PASS: YES/NO
REPAIRS_5_TO_9_REGRESSION_PASS: YES/NO
FULL_UNIT_PASSING_COUNT: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURE_IDENTITIES_MATCH: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 
EXACT_PACKAGE_VERIFIER_PASS: YES/NO
PACKAGE_DELTA_EXPECTED_ONLY: YES/NO
BLOCKER_FINDING_COUNT: 
HIGH_FINDING_COUNT: 
MEDIUM_FINDING_COUNT: 
LOW_FINDING_COUNT: 
FINDINGS: 
SOURCE_FILES_MODIFIED_BY_REVIEW: 0
TEST_FILES_MODIFIED_BY_REVIEW: 0
PACKAGE_JSON_MODIFIED_BY_REVIEW: NO
VSIX_MODIFIED_BY_REVIEW: NO
QA_STTM_MODIFIED_BY_REVIEW: NO
STAGED_FILES: 0
EXTENSION_INSTALLED: NO
RUNTIME_QA_STARTED: NO
READY_TO_INSTALL_0_3_143: YES/NO
READY_FOR_RUNTIME_QA_PHASE_1: YES/NO

PASS requires:

* zero BLOCKER and HIGH findings;
* no Runtime-QA-blocking MEDIUM finding;
* contract and runtime behavior match;
* deterministic security boundaries pass;
* all six exact mappings match across source, compiled, and packaged parser;
* zero-extraction is fail-closed;
* canonical Markdown bundle and Excel behavior remain valid;
* all required tests pass with unchanged historical failure identities;
* exact VSIX and package delta pass;
* review performs zero repository, artifact, and QA mutations.

End exactly with one:

INDEPENDENT_REVIEW_0_3_143_RESULT: PASS

INDEPENDENT_REVIEW_0_3_143_RESULT: FAIL_BLOCKING_FINDINGS

INDEPENDENT_REVIEW_0_3_143_RESULT: FAIL_PACKAGE_VERIFICATION

INDEPENDENT_REVIEW_0_3_143_RESULT: BLOCKED_IDENTITY_MISMATCH
