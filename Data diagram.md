TASK: HF1_V2_REPAIR_11_HOTFIX_STABILIZATION_PREPACKAGE_NO_VSIX

Implement the smallest safe Repair 11 required to unblock HF1 V2 Runtime QA.

This task starts from the independently confirmed static findings:

* single-file Markdown requests enumerate sibling Markdown files;
* Mapping IDs are not file- or section-scoped;
* the QA STTM has 5 logical sections but only the mapping section is recognized;
* Source, Target, Filters, and Notes evidence is lost;
* partial recognition returns confidence 0.90 and status read;
* the actual QA filters differ from the earlier Runtime QA prompt.

This task must produce a source-level Hotfix Candidate only.

Do not bump the version.
Do not build a VSIX.
Do not install the extension.
Do not start Runtime QA.

==================================================

1. ENVIRONMENT
    ==================================================

Work only in:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected identity:

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE VERSION:
0.3.143

Existing VSIX, which must remain untouched:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.143.vsix

EXPECTED SIZE:
1255490

EXPECTED SHA-256:
8819E0902BF5FE1F8EFE9BA302EB196D3715AF17DC5F44B76F3C0EACBDB3CFFA

Authorized read-only QA STTM:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Expected QA STTM SHA-256:

F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

==================================================
2. EXECUTION PREFLIGHT — BEFORE ANY EDIT

Before inspecting or editing source, execute and report:

* git.exe –version
* node.exe –version
* npm.cmd –version
* cmd.exe /c echo PROCESS_EXECUTION_OK

Every command must:

* produce visible output;
* return exit code 0;
* execute as a real native process.

If any command cannot execute, returns empty output, or provides no exit code,
stop before editing with:

REPAIR_11_PREPACKAGE_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

Do not substitute static inspection for required dynamic tests.

==================================================
3. SAFETY AND BASELINE

Capture before editing:

* repository root;
* origin;
* branch;
* HEAD;
* package.json version;
* staged paths;
* tracked-modified paths and hashes;
* untracked paths and hashes;
* VSIX path, size, and SHA-256;
* QA STTM path, size, and SHA-256.

A large pre-existing working-tree overlay is expected. Preserve it exactly.

Required:

STAGED_FILES_AT_START: 0
SOURCE_VERSION_BEFORE: 0.3.143

Do not:

* modify the QA workspace or STTM;
* modify the existing VSIX;
* modify package.json;
* run npm version;
* run npm run package:prepare;
* run vsce package;
* create a VSIX;
* install an extension;
* modify .github/**;
* access etl-framework-adb;
* download dependencies;
* create package-lock.json;
* commit, push, tag, stage, stash, reset, restore, clean, or delete files;
* execute a Databricks job;
* access real data;
* create a Preview in the real QA workspace;
* execute any QA-workspace write.

npm run compile is permitted and required for validation.

==================================================
4. PRE-CHANGE DYNAMIC REPRODUCTION

Use task-owned files under %TEMP%.

4.1 Sibling-file leak

Create:

* requested.md containing one unique REQUESTED mapping;
* unrelated-sibling.md containing one unique SIBLING mapping.

Invoke the real public/runtime read path while explicitly requesting only
requested.md.

Required pre-fix reproduction:

* requested mapping returned;
* sibling file enumerated;
* sibling sentinel mapping returned or demonstrably admitted by the executed
    runtime path;
* no cross-file ambiguity diagnostic.

4.2 Mapping-ID collision

Create two logical Markdown mapping inputs with mapping rows at the same source
line.

Execute the parser and confirm whether their generated Mapping IDs collide.

4.3 QA partial recognition

Execute the current source/compiled interpretation path against the exact
read-only QA STTM.

Record:

* total sections;
* recognized sections;
* mappings;
* Source evidence;
* Target evidence;
* Filters;
* Notes/write evidence;
* diagnostics;
* confidence;
* status.

Expected pre-fix observation:

SECTIONS_TOTAL: 5
SECTIONS_RECOGNIZED: 1
MAPPINGS: 6
SOURCE_EVIDENCE: 0
TARGET_EVIDENCE: 0
FILTERS: 0
NOTES: 0
CONFIDENCE: approximately 0.90
STATUS: read

If these defects cannot be dynamically reproduced, stop before editing and
report the conflict.

==================================================
5. BOUNDED IMPLEMENTATION

5.1 Exact-file isolation

Implement an explicit single-file Markdown entry point.

When a caller supplies a specific .md path:

* parse exactly that file;
* never replace it with its parent-directory bundle;
* never enumerate sibling Markdown files;
* never merge sibling evidence.

Directory enumeration remains available only when the caller explicitly
supplies an authorized bundle directory.

Preserve:

* workspace-root containment;
* traversal rejection;
* sibling-root rejection;
* UNC rejection;
* different-drive rejection;
* realpath/symlink containment;
* explicit bundle behavior;
* Excel routing.

For an explicit bundle directory, reject document-level ambiguity when multiple
files contribute conflicting field-mapping sections.

5.2 Mapping identity

Preserve explicitly supplied canonical IDs.

For human-readable mappings without canonical IDs, derive a stable identity from
a deterministic logical tuple containing sufficient scope such as:

* normalized bundle-relative file identity;
* normalized logical section identity;
* table index;
* source line or deterministic row index.

Requirements:

* distinct files cannot produce the same mapping ID merely because line numbers
    match;
* distinct sections cannot collide;
* repeated parsing produces identical IDs;
* no absolute machine path;
* no drive letter;
* no random value;
* no timestamp;
* source, compiled, and later packaged layouts must agree.

Update directly affected traceability joins and tests together.

Do not redesign the public mapping model beyond what is necessary.

5.3 Deterministic QA section evidence

Recognize the QA single-file sections using a small explicit alias set.

Required logical sections:

* Source;
* Target;
* Column mapping / Field mapping;
* Filters;
* Notes or explicit write evidence.

Requirements:

* exact normalized aliases only;
* no fuzzy matching;
* no substring guessing;
* no LLM extraction;
* no raw-content fallback;
* no arbitrary prose interpretation;
* reject duplicate or ambiguous material sections;
* select mapping tables by deterministic headers, not table position.

The QA Filters section uses a Markdown bullet list, not the canonical filter
table. Support this exact documented single-file shape deterministically.

The literal filters in the authorized QA STTM are:

* status_cd IS NOT NULL
* updated_ts >= ${etl.effective.start.date}

These older prompt expectations are wrong and must not be used:

* status_code = ‘ACTIVE’
* updated_ts IS NOT NULL

Do not edit the STTM and do not fabricate old values.

Do not infer:

* Unity Catalog table targets;
* ADLS physical paths that are not literally in the STTM;
* missing filters;
* missing primary keys;
* missing write modes.

Raw/curated identifiers remain logical evidence.

5.4 Partial-recognition safety

Add a distinct diagnostic when a material section is present but cannot be
recognized or deterministically parsed.

A document must not be treated as complete merely because one of several
material sections was recognized.

Implement the smallest fail-closed completeness rule needed by the existing
contract.

Do not invent a new numerical confidence formula.

If changing the numeric confidence model requires a contract-owner decision:

* retain the existing formula;
* emit the new material-section diagnostic;
* make completeness/validation fail closed;
* record the numeric-confidence redesign as deferred.

==================================================
6. DEFERRED FINDINGS

Do not expand Repair 11 for these items unless an in-scope edit directly
regresses them:

* UTF-8 BOM support;
* residual first-table assumptions outside the Phase 1 path;
* general parser redesign;
* unrelated historical failures.

The current QA STTM has no BOM.

Record these under DEFERRED_FINDINGS.

==================================================
7. REQUIRED TESTS

Add focused tests for:

A. Exact-file isolation

* requested file returns only its own evidence;
* sibling sentinel mapping is absent;
* sibling file is not opened;
* a sibling containing another mapping section does not create cross-file merge;
* explicit directory bundle still parses its files;
* ambiguous bundle mappings fail closed;
* containment and traversal protections remain unchanged.

B. Mapping identity

* identical line numbers in different files produce different IDs;
* different sections do not collide;
* two runs produce identical IDs;
* canonical supplied IDs remain unchanged;
* no absolute path appears in generated IDs.

C. Section evidence

Using a synthetic fixture with the same shape as the QA STTM:

* five logical sections recognized;
* six mappings;
* Source evidence retained;
* Target evidence retained;
* both literal filters retained;
* explicit Notes/write evidence retained only when present;
* no Unity Catalog inference;
* no physical path fabrication;
* no raw fallback.

D. Partial recognition

* missing/unparseable material sections produce explicit diagnostics;
* incomplete material evidence cannot pass as complete;
* zero mappings remain fail-closed;
* unrelated prose containing “mapping” remains unrecognized;
* duplicate/ambiguous sections remain rejected.

E. Regression

* canonical Markdown bundles unchanged;
* Excel STTM unchanged;
* Repairs 5–10 unchanged;
* workspace containment unchanged;
* trusted contract resolution unchanged.

==================================================
8. PRE-PACKAGE GOLDEN PATH

Create or extend one automated source-level Golden Path test using a temporary
fresh-consumer workspace.

Do not use or modify the real QA workspace.

Use:

JOB:
qa_hf1v2_demo

MALCODE:
acz9999

ENVIRONMENT:
dev

STRATEGY:
generic_dataframe_write

SOURCE:
Delta path
abfss://qa@qaetlhf1v2dev.dfs.core.windows.net/raw/qa_hf1v2_customer

TARGET:
Delta path
abfss://qa@qaetlhf1v2dev.dfs.core.windows.net/curated/qa_hf1v2_customer

FORMAT:
delta

WRITE MODE:
append

PRIMARY KEY:
customer_id, informational only

Expected STTM semantics:

* six mappings;
* status_cd IS NOT NULL;
* updated_ts >= ${etl.effective.start.date};
* single-file sectioned Markdown.

Validate without consumer writes:

1. fresh-consumer classification;
2. exact-file STTM isolation;
3. six mappings;
4. Source, Target, Filters, and explicit write evidence;
5. CREATE_NEW_JOB;
6. canonical modules-object envelope;
7. path-based dataframe_writer;
8. Delta append output;
9. proposed job configuration;
10. proposed environment configuration;
11. complete Preview manifest;
12. all paths contained inside the temporary workspace;
13. explicit approval required;
14. approval remains pending;
15. zero files created, modified, or deleted.

Reuse existing production services and test helpers.

Do not create parallel planning, rendering, validation, or Preview logic only for
the test.

==================================================
9. VALIDATION

Run with existing local dependencies:

1. npm run compile;
2. npm run lint;
3. Repair 11 focused tests;
4. the pre-package Golden Path test;
5. STTM Markdown parser suites;
6. resolver/evidence-provider suites;
7. workspace-containment security suites;
8. Repair 10 regression;
9. Repair 9 regression;
10. Repair 8 regression;
11. Repair 5/6/7 regression;
12. trusted Job Config envelope direct suite;
13. canonical full unit suite.

Report exact command, exit code, pass, pending, and failure counts.

Pre-Repair-11 historical full-unit baseline:

PASSING: 2180
PENDING: 1
FAILING: 5

The passing count should increase by the new tests.

The same five failures may remain only when their exact identities are shown to
be unchanged and unrelated.

Required:

NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

Do not edit baselines or unrelated tests to hide failures.

==================================================
10. FINAL CHANGE BOUNDARY

Compare the final state with the captured baseline.

Permitted changes:

* the smallest production files necessary for exact-file isolation, mapping
    identity, section evidence, and completeness diagnostics;
* directly related STTM tests;
* a synthetic fixture;
* one Golden Path regression test;
* the minimum test-only helper required by that test;
* the STTM skill/contract documentation only if necessary to describe the
    already-selected single-file/bundle distinction.

Forbidden changes:

* package.json;
* source version;
* .github/**;
* unrelated consumer context;
* real QA workspace;
* existing VSIX;
* generated VSIX;
* unrelated source or tests.

Any newly discovered non-blocking issue must be recorded, not automatically
fixed.

==================================================
11. FINAL REPORT

Return:

PROCESS_EXECUTION_PREFLIGHT_PASS: YES/NO
REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION_BEFORE: 0.3.143
SOURCE_VERSION_AFTER: 0.3.143
VERSION_CHANGED: NO
PRE_FIX_SIBLING_LEAK_REPRODUCED: YES/NO
POST_FIX_EXACT_FILE_ISOLATION_PASS: YES/NO
POST_FIX_SIBLING_SENTINEL_ABSENT: YES/NO
MAPPING_ID_COLLISION_PRE_FIX: YES/NO
MAPPING_ID_COLLISION_POST_FIX: YES/NO
MAPPING_IDS_STABLE_AND_PATH_SAFE: YES/NO
QA_STTM_SHA256_MATCH: YES/NO
QA_STTM_MODIFIED: NO
QA_LITERAL_FILTERS: 
STRUCTURED_MAPPING_COUNT: 
SOURCE_EVIDENCE_PARSED: YES/NO
TARGET_EVIDENCE_PARSED: YES/NO
FILTER_EVIDENCE_PARSED: YES/NO
WRITE_EVIDENCE_PARSED_WITHOUT_GUESSING: YES/NO
MATERIAL_SECTION_DIAGNOSTIC_PASS: YES/NO
PARTIAL_RECOGNITION_FAIL_CLOSED: YES/NO
UNITY_CATALOG_INFERENCE_USED: NO
RAW_CONTENT_FALLBACK_USED: NO
GOLDEN_PATH_TEST_PASS: YES/NO
GOLDEN_PATH_ARTIFACT_COUNT: 
GOLDEN_PATH_ZERO_WRITES: YES/NO
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_11_FOCUSED_PASS: YES/NO
STTM_REGRESSION_PASS: YES/NO
WORKSPACE_CONTAINMENT_PASS: YES/NO
REPAIR_10_REGRESSION_PASS: YES/NO
REPAIR_9_REGRESSION_PASS: YES/NO
REPAIR_8_REGRESSION_PASS: YES/NO
REPAIR_5_6_7_REGRESSION_PASS: YES/NO
TRUSTED_ENVELOPE_PASS: YES/NO
FULL_UNIT_PASSING_COUNT: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
HISTORICAL_FAILURE_IDENTITY_CONFIRMED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 
AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
DEFERRED_FINDINGS: 
STAGED_FILES: 
PACKAGE_JSON_MODIFIED: NO
PACKAGE_PREPARE_EXECUTED: NO
VSIX_BUILT: NO
EXISTING_0_3_143_VSIX_MODIFIED: NO
EXTENSION_INSTALLED: NO
RUNTIME_QA_STARTED: NO
QA_WORKSPACE_MUTATED: NO
READY_FOR_ONE_FINAL_INDEPENDENT_REVIEW: YES/NO
READY_TO_PACKAGE: NO
READY_TO_INSTALL: NO

PASS requires:

* working native-process execution;
* dynamic pre-fix reproduction;
* exact-file isolation;
* no sibling evidence leakage;
* stable non-colliding mapping IDs;
* deterministic required QA evidence;
* fail-closed material completeness;
* Golden Path PASS;
* zero new regressions;
* zero unauthorized changes;
* version remains 0.3.143;
* no package or VSIX build.

End exactly with one:

REPAIR_11_PREPACKAGE_RESULT: PASS

REPAIR_11_PREPACKAGE_RESULT: FAIL_VALIDATION

REPAIR_11_PREPACKAGE_RESULT: FAIL_SECURITY_BOUNDARY

REPAIR_11_PREPACKAGE_RESULT: FAIL_GOLDEN_PATH

REPAIR_11_PREPACKAGE_RESULT: FAIL_UNAUTHORIZED_CHANGE

REPAIR_11_PREPACKAGE_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

REPAIR_11_PREPACKAGE_RESULT: BLOCKED_IDENTITY_MISMATCH

REPAIR_11_PREPACKAGE_RESULT: BLOCKED_STAGED_CHANGES
