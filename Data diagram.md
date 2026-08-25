TASK: HF1_V2_INDEPENDENT_REVIEW_RETRY_REPAIR_10_AND_VSIX_0_3_143

Perform a fresh, independent, read-only review of Repair 10 and the exact
Databricks ETL Copilot 0.3.143 VSIX.

This review supersedes the previous blocked review only with respect to:

1. the corrected expected SHA-256;
2. the requirement to verify external-process execution before starting.

Do not rely on the implementation agent’s PASS conclusion.
Verify all material claims independently.

Work in the Software Development Environment:

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

EXACT VSIX:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.143.vsix

EXPECTED VSIX SIZE:
1255490 bytes

CORRECTED EXPECTED VSIX SHA-256:
8819E0902BF5FE1F8EFE9BA302EB196D3715AF17DC5F44B76F3C0EACBDB3CFFA

The earlier expected hash ending with:

…DC5F44876E3C0EACBD03CFFA

was mistranscribed and is explicitly superseded. Do not use it.

Authorized read-only QA input:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Expected QA STTM SHA-256:

F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Do not modify the QA workspace or STTM.

Do not edit source, tests, fixtures, contracts, documentation, package.json,
compiled output, the VSIX, or any workflow asset.

Do not install the extension.
Do not start Runtime QA.
Do not create a Preview ID.
Do not execute any ETL write.
Do not commit, push, tag, stage, stash, reset, restore, clean, or delete files.
Do not download dependencies.
Do not create package-lock.json.

==================================================
0. EXTERNAL-PROCESS EXECUTION PREFLIGHT

Before the repository identity gate, prove this Chat can execute local processes.

Resolve and execute:

* git.exe –version
* node.exe –version
* npm.cmd –version
* cmd.exe /c echo PROCESS_EXECUTION_OK

Report:

GIT_PROCESS_EXIT_CODE
GIT_PROCESS_OUTPUT
NODE_PROCESS_EXIT_CODE
NODE_PROCESS_OUTPUT
NPM_PROCESS_EXIT_CODE
NPM_PROCESS_OUTPUT
CMD_PROCESS_EXIT_CODE
CMD_PROCESS_OUTPUT

Required:

* every process produces visible output;
* every exit code is zero;
* cmd output contains PROCESS_EXECUTION_OK.

If any command returns empty output, has no exit code, cannot launch, or is
intercepted by the execution environment, stop without inspecting or changing
the repository and return:

INDEPENDENT_REVIEW_0_3_143_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

Do not substitute PowerShell-only inspection for the required node/npm/git
validation.

==================================================

1. IDENTITY AND ARTIFACT GATE
    ==================================================

Verify independently:

* absolute repository root;
* origin;
* current branch;
* HEAD;
* package.json version;
* staged-file count;
* exact VSIX path;
* VSIX size;
* internal package.json version;
* internal extension.vsixmanifest version;
* publisher;
* extension ID;
* archive entry count.

Compute the VSIX SHA-256 twice using independent implementations:

1. PowerShell Get-FileHash;
2. raw System.Security.Cryptography.SHA256 over the file bytes.

Both results must equal exactly:

8819E0902BF5FE1F8EFE9BA302EB196D3715AF17DC5F44B76F3C0EACBDB3CFFA

Do not use a “latest VSIX” selector.

If the two independently computed hashes disagree, or the file differs from the
corrected expected hash, stop with:

INDEPENDENT_REVIEW_0_3_143_RESULT: BLOCKED_IDENTITY_MISMATCH

If staged changes exist, stop with:

INDEPENDENT_REVIEW_0_3_143_RESULT: BLOCKED_STAGED_CHANGES

==================================================
2. CAPTURE AND PRESERVE THE WORKING-TREE BASELINE

The repository is expected to contain a large pre-existing uncommitted overlay.

Capture before review:

* tracked-modified paths and hashes;
* untracked paths and hashes;
* staged paths;
* repository porcelain status.

Preserve this baseline exactly.

The review must make zero repository changes.

==================================================
3. REVIEW THE REPAIR 10 CHANGE BOUNDARY

Review the actual diff and implementation in these Repair 10 areas:

Source:

* src/core/sttm/SttmMarkdownBundleParser.ts
* src/core/sttm/SttmReferenceResolver.ts
* src/core/solution/SttmEvidenceProvider.ts

Tests and fixture:

* src/test/suite/sttmMarkdownParser.test.ts
* src/test/fixtures/sttm/synthetic_single_file_sectioned_markdown/**

Contract and documentation:

* package.json
* resources/copilot/skills/etl-sttm-document-understanding/SKILL.md

Confirm that package.json changes are limited to:

* version 0.3.142 → 0.3.143;
* the supported STTM modelDescription contract.

Identify any Repair 10 change outside this boundary.

==================================================
4. INDEPENDENT CORRECTNESS REVIEW

Verify from code rather than from the implementation report that:

* a single self-contained sectioned Markdown STTM is supported;
* section segmentation occurs only on explicit recognized headings;
* the mapping-section alias set is small, explicit, and enumerable;
* fuzzy or substring-based heading guessing is not used;
* the mapping table is selected by deterministic header matching;
* human-readable Source column and Target column headers are supported;
* rows without canonical Excel IDs can be accepted deterministically;
* fake schema, business-rule, transformation-rule, or join IDs are not created;
* duplicate mapping sections are rejected;
* ambiguous mapping tables are rejected;
* zero recognized sheets or zero mappings fail closed;
* zero extraction cannot return a successful high-confidence read;
* canonical multi-file Markdown bundles retain their previous behavior;
* the Excel STTM path is unchanged;
* targeted retrieval and path-containment protections are not weakened;
* consumer context is not treated as machine authority.

Explicitly look for:

* accidental broadening of trusted input;
* arbitrary prose being interpreted as structured mappings;
* nondeterministic table selection;
* first-table assumptions;
* silent ambiguity resolution;
* fail-open behavior;
* path traversal or sibling-root access;
* regressions to Repairs 5–9;
* duplicated contract logic that can drift.

Report findings by severity with exact file and line references.

==================================================
5. QA STTM INDEPENDENT PARSER PROBE

Read only the authorized QA STTM file.

First verify:

QA_STTM_SHA256:
F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Run independent source, compiled, and packaged parser probes against the exact
unmodified file.

Required deterministic result:

* structured mapping count: 6;
* identical source, compiled, and packaged payloads;
* source and target field names preserved;
* status_code = ‘ACTIVE’ preserved;
* updated_ts IS NOT NULL preserved;
* Delta source and target evidence preserved;
* path-backed target preserved;
* append writer evidence preserved;
* no Unity Catalog table-name inference;
* no raw-content guessing fallback;
* no modification of the QA STTM.

Report the complete six-mapping payload, not only the count.

==================================================
6. VALIDATION GATES

Use existing local dependencies and repository scripts only.

Run and report exact command, exit code, passing, pending, and failing counts for:

1. TypeScript compile;
2. lint;
3. Repair 10 focused tests;
4. STTM Markdown parser regression tests;
5. STTM reference resolver and evidence-provider tests;
6. Repair 9 regression tests;
7. Repair 8 regression tests;
8. Repair 5/6/7 regression tests;
9. trusted Job Config envelope direct suite;
10. workspace-root and path-containment security tests;
11. the canonical full unit suite.

Expected full-unit baseline after Repair 10:

FULL_UNIT_PASSING_COUNT: 2180
FULL_UNIT_PENDING_COUNT: 1
FULL_UNIT_FAILURE_COUNT: 5

The five failures must be independently matched to the previously historical:

* two EvalGating baseline-report failures;
* three Copilot workflow-customization failures.

Do not merely label them historical. Reproduce or compare their exact identities
against the appropriate unchanged baseline evidence.

Required:

NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

==================================================
7. EXACT PACKAGE REVIEW

Run the existing exact-package verifier against the explicit 0.3.143 path.

Independently inspect the archive and verify:

* valid ZIP archive;
* exactly 66 entries;
* internal package version 0.3.143;
* internal manifest version 0.3.143;
* publisher td-etl;
* extension ID td-etl.databricks-etl-copilot;
* trusted contracts are present and byte-equal to source;
* installed-layout contract resolution works;
* no source-checkout runtime dependency exists;
* no machine-specific paths are embedded;
* no forbidden package-hygiene entries exist;
* no tests, temporary files, nested Git data, or tsbuildinfo files are packaged;
* repaired parser logic is present in the packaged runtime.

Compare source, compiled, and packaged behavior on both:

* the Repair 10 synthetic fixture;
* the exact QA STTM.

==================================================
8. INDEPENDENT VERDICT

A PASS requires:

* process-execution preflight passes;
* corrected artifact identity matches;
* zero staged files;
* no high- or medium-severity finding;
* six exact QA mappings from source, compiled, and packaged runtimes;
* deterministic and fail-closed parsing;
* canonical bundle compatibility;
* no security-boundary weakening;
* all required validation gates pass;
* only the five independently confirmed historical unit failures remain;
* exact-package verification passes;
* zero files changed by the review.

Return:

PROCESS_EXECUTION_PREFLIGHT_PASS: YES/NO
REPOSITORY_IDENTITY_PASS: YES/NO
CORRECTED_VSIX_SHA256_MATCH: YES/NO
VSIX_SHA256_METHOD_1: 
VSIX_SHA256_METHOD_2: 
ARTIFACT_IDENTITY_PASS: YES/NO
REPAIR_10_CHANGE_BOUNDARY_PASS: YES/NO
QA_STTM_SHA256_MATCH: YES/NO
SOURCE_STRUCTURED_MAPPING_COUNT: 
COMPILED_STRUCTURED_MAPPING_COUNT: 
PACKAGED_STRUCTURED_MAPPING_COUNT: 
SOURCE_COMPILED_PACKAGED_PAYLOAD_MATCH: YES/NO
QA_STTM_MODIFIED: NO
DETERMINISTIC_PARSER_PASS: YES/NO
ZERO_EXTRACTION_FAIL_CLOSED: YES/NO
CANONICAL_BUNDLE_REGRESSION_PASS: YES/NO
PATH_CONTAINMENT_PASS: YES/NO
TRUST_BOUNDARY_PASS: YES/NO
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_10_FOCUSED_PASS: YES/NO
STTM_REGRESSION_PASS: YES/NO
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
EXACT_PACKAGE_VERIFIER_PASS: YES/NO
INDEPENDENT_PACKAGE_INSPECTION_CLEAN: YES/NO
HIGH_FINDING_COUNT: 
MEDIUM_FINDING_COUNT: 
LOW_FINDINGS: 
FILES_CHANGED_BY_REVIEW: 
STAGED_FILES: 
EXTENSION_INSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
READY_TO_INSTALL_0_3_143: YES/NO
READY_FOR_RUNTIME_QA_PHASE_1: YES/NO

End exactly with one:

INDEPENDENT_REVIEW_0_3_143_RESULT: PASS

INDEPENDENT_REVIEW_0_3_143_RESULT: FAIL_FINDINGS

INDEPENDENT_REVIEW_0_3_143_RESULT: FAIL_VALIDATION

INDEPENDENT_REVIEW_0_3_143_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

INDEPENDENT_REVIEW_0_3_143_RESULT: BLOCKED_IDENTITY_MISMATCH

INDEPENDENT_REVIEW_0_3_143_RESULT: BLOCKED_STAGED_CHANGES
