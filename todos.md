TASK: HF1_V2_REPAIR_12_GENUINELY_INDEPENDENT_REVIEW_SOURCE_ONLY_0_3_144

Perform a genuinely independent, read-only review of Repair 12 and its canonical
test registration.

This is an ETL-extension task only.

Do not inspect, run, reference, or modify:

* AskTD or KMAI repositories;
* Phase 2E worktrees;
* PR 15, PR 16, or PR 17;
* governed-field-record tasks;
* any unrelated repository or workspace.

If the active task or prompt starts with PHASE_2E, ASKTD, KMAI, or refers
to PR 15/16/17, stop immediately with:

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_WRONG_PROMPT

This review must be performed in a completely new Chat that did not implement
Repair 12 and did not register its test suite.

Do not rely on previous agent conclusions as machine authority. Re-derive every
material conclusion from live source, diffs, tests, and independently created
read-only probes.

Do not use web search.
Do not download or install dependencies.
Do not modify source, tests, fixtures, package.json, contracts, skills, prompts,
workflow assets, baselines, or the QA workspace.
Do not build or package a new VSIX.
Do not modify the existing 0.3.144 VSIX.
Do not bump the version.
Do not install or uninstall any extension.
Do not start Runtime QA.
Do not request or create a Preview ID.
Do not authorize or execute a filesystem write workflow.
Do not commit, push, tag, stage, stash, reset, restore, clean, or delete files.

Temporary review scripts and outputs may be created only under:

%TEMP%\hf1v2-repair12-independent-review\

==================================================

1. IDENTITY AND PROCESS-EXECUTION GATE
    ==================================================

Required repository identity:

REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION:
0.3.144

Prove that real native processes work before beginning the review.

Run real commands that produce visible output and exit codes:

* cmd.exe /c echo PROCESS_EXECUTION_OK
* git.exe –version
* node.exe –version
* npm.cmd –version

Then capture:

* absolute repository root;
* origin URL;
* branch;
* HEAD;
* package.json version;
* staged-file count;
* stash count;
* package-lock.json presence;
* working-tree porcelain;
* existing 0.3.144 VSIX path, size, mtime, and SHA-256.

Required:

PROCESS_EXECUTION_PREFLIGHT: PASS
STAGED_FILES_AT_START: 0
SOURCE_VERSION: 0.3.144
PACKAGE_LOCK_PRESENT: NO

If identity differs, stop with:

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_IDENTITY_MISMATCH

If native processes cannot execute, stop with:

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

If staged files exist, stop with:

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_STAGED_CHANGES

==================================================
2. PROTECTED ARTIFACTS AND QA INPUT

The existing VSIX:

databricks-etl-copilot-0.3.144.vsix

predates Repair 12 and is intentionally protected.

It does not contain the final Repair 12 source changes. Do not use the old VSIX
to decide whether the repaired source behavior is correct, and do not flag the
expected source/VSIX difference as artifact drift.

Only verify that the existing 0.3.144 VSIX remains byte-identical and unmodified
during this review.

Authorized read-only QA input:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Expected:

QA_STTM_SIZE_BYTES: 1437

QA_STTM_SHA256:
F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Expected literal content includes:

SOURCE_LITERAL:
raw.qa_hf1v2_customer

TARGET_LITERAL:
curated.qa_hf1v2_customer

FILTER_1:
status_cd IS NOT NULL

FILTER_2:
updated_ts >= ${etl.effective.start.date}

The source and target literals are authored logical dotted object references.
They are not ABFSS paths and must not automatically become Unity Catalog,
database, schema, or physical-path authority.

The STTM must remain unchanged.

==================================================
3. REPAIR 12 CHANGE BOUNDARY

The complete expected Repair 12 boundary is exactly these seven paths:

1. src/core/sttm/SttmResolvedEvidence.ts
2. src/core/sttm/SttmUnderstandingReportRenderer.ts
3. src/tools/EtlReadOnlyToolService.ts
4. package.json
5. src/test/suite/sttmRepair12.test.ts
6. src/test/suite/EtlReadOnlyToolService.test.ts
7. src/test/testPatterns.ts

Verify independently:

* no Repair 12 change exists outside these seven paths;
* src/test/testPatterns.ts contains exactly one added registration:
    **/sttmRepair12.test.js;
* no existing test pattern was removed, broadened, reordered, or duplicated;
* sttmRepair12.test.js is discovered exactly once by the canonical unit runner;
* package.json remains version 0.3.144;
* the Repair 12 package.json change is confined to the
    etl_interpret_sttm public description/model contract;
* no parser skill, packaged contract, .github/**, QA file, or workflow asset
    was modified by Repair 12;
* no test-only alternative implementation or copied production algorithm exists.

A large pre-existing Repairs 5–11 working-tree overlay is expected. Preserve it.
Do not classify pre-existing unrelated changes as Repair 12 changes. Use captured
hashes, mtime evidence, source history, and focused diffs to isolate the Repair 12
boundary.

If concurrent mutation prevents deterministic isolation, stop with:

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_CONCURRENT_MUTATION

If Repair 12 modified unauthorized paths, return:

INDEPENDENT_REVIEW_0_3_144_RESULT: FAIL_CHANGE_BOUNDARY

==================================================
4. ARCHITECTURE AND CONTRACT REVIEW

Review the actual implementation, not only the tests.

Verify that one canonical public projection path is shared by:

* the structured etl_interpret_sttm data result;
* the human-readable Markdown report.

Verify all of the following:

A. Notes

* exactly two QA Notes are preserved;
* Notes remain advisory and untrusted;
* Notes cannot become configuration authority;
* Notes cannot affect paths, module selection, write authorization, approval,
    critical configuration, or Preview state;
* Markdown characters and embedded content are escaped safely;
* no raw-content or LLM fallback is introduced.

B. Source and Target evidence

* the exact authored literals are publicly exposed;
* the structured and Markdown channels agree;
* source and target are read from their recognized sections;
* duplicate or conflicting evidence is handled deterministically and fail-closed;
* no fallback uses mapping.targetEntity, table names, prose, filenames, or
    workspace context;
* no Unity Catalog, database, schema, table, ABFSS path, or physical destination
    is fabricated.

C. Mapping IDs

* the existing six scoped Mapping IDs are reused unchanged;
* IDs are treated as opaque identifiers;
* mappings remain an ordered array;
* no mapping is keyed by ID in a way that could overwrite duplicates;
* no ID is regenerated, truncated, normalized, or inferred;
* Markdown adds Mapping ID as the final mapping-table column;
* Markdown order matches structured mapping order;
* there is no public mappingIdsUnique Boolean unless it existed before Repair 12;
* uniqueness is derivable from the six exposed IDs.

D. Compatibility

* changes are additive where possible;
* existing public fields and meanings remain stable;
* existing diagnostics and parser behavior remain intact;
* Repairs 5–11 security and write-approval boundaries remain unchanged;
* the public DTO and renderer cannot silently diverge.

==================================================
5. TEST-INTEGRITY REVIEW

Inspect src/test/suite/sttmRepair12.test.ts and related tests.

Prove that the Repair 12 test crosses the real public seam:

exact single-file Markdown
→ production filesystem reader
→ production parser
→ canonical document model
→ evidence provider
→ shared public projector
→ actual EtlReadOnlyToolService
→ structured result and Markdown result

The test must not stop at the internal parser/model layer.

The test must not:

* use a copied fake serializer;
* reproduce production logic inside the test;
* weaken existing assertions;
* normalize away material output;
* edit the QA STTM;
* enumerate sibling Markdown files for a single-file request;
* infer values from raw Markdown after the production parser returns.

Confirm coverage for:

* two Notes in structured output;
* two Notes in Markdown;
* exact Source literal in both channels;
* exact Target literal in both channels;
* six Mapping IDs in both channels;
* Mapping ID as the final Markdown column;
* structured/Markdown ordering parity;
* advisory/untrusted Notes;
* missing Source/Target;
* duplicate or conflicting Source/Target;
* absent Notes;
* Markdown-special-character escaping;
* duplicate or missing mapping IDs without silent overwriting;
* single-file isolation;
* no raw fallback;
* no physical-path or Unity Catalog inference.

==================================================
6. INDEPENDENT DYNAMIC PROBES

Create a new task-owned probe under:

%TEMP%\hf1v2-repair12-independent-review\

Do not reuse the implementation agent’s probe.

Invoke the real compiled production entry points against the exact unchanged QA
STTM at least twice.

Prove:

STTM_FILES_PARSED: 1
STTM_SIBLING_FILES_ENUMERATED: 0
STTM_SECTIONS_TOTAL: 5
STTM_SECTIONS_RECOGNIZED: 5
STTM_STRUCTURED_MAPPING_COUNT: 6
STTM_MAPPING_IDS_EXPOSED: 6
STTM_MAPPING_IDS_UNIQUE: YES
STTM_NOTES_COUNT: 2
STTM_SOURCE_EVIDENCE_COUNT: 1
STTM_TARGET_EVIDENCE_COUNT: 1
STTM_FILTER_COUNT: 2

The public structured result must expose:

* both Notes;
* raw.qa_hf1v2_customer;
* curated.qa_hf1v2_customer;
* all six Mapping IDs;
* both exact filters.

The public Markdown result must expose the same evidence and place Mapping ID in
the final mapping-table column.

Also prove:

* no mappingIdsUnique field was added;
* no raw-content fallback was used;
* no LLM fallback was used;
* no identifier was fabricated;
* no Unity Catalog interpretation was introduced;
* no physical path was fabricated;
* no sibling file was opened or merged;
* no workspace file was created, modified, or deleted.

Run the public tool twice across a real wall-clock boundary.

Do not hide or normalize differences. Report every differing field or line.

Expected deterministic result:

* structured semantic payloads are byte-equivalent;
* Markdown semantic content is equivalent;
* the only permitted difference is the existing audit wall-clock timestamp.

If any additional value changes, report it as a finding.

==================================================
7. NEGATIVE AND SECURITY CONTROLS

Using isolated temporary fixtures only, verify:

* missing Source does not fabricate Source evidence;
* missing Target does not fabricate Target evidence;
* conflicting Source sections are rejected or surfaced explicitly;
* conflicting Target sections are rejected or surfaced explicitly;
* duplicate mapping IDs cannot overwrite mappings;
* missing mapping IDs do not reorder mappings;
* malicious Notes remain inert advisory text;
* Notes cannot alter job config, paths, modules, Preview state, approval state,
    write authorization, or critical configuration;
* Markdown escaping prevents table/heading injection from changing structure;
* traversal, sibling reads, UNC escape, different-drive escape, and symlink escape
    remain rejected;
* Excel STTM behavior remains unchanged;
* canonical multi-file Markdown bundle behavior remains unchanged;
* Repairs 9–11 single-file and classification behavior remains unchanged.

==================================================
8. VALIDATION GATES

Use only existing local dependencies and canonical repository commands.

Run and report exact commands, exit codes, passing, pending, and failing counts
for:

1. TypeScript compile;
2. lint;
3. Repair 12 focused suite;
4. EtlReadOnlyToolService suite;
5. Repair 11 focused suite;
6. Repair 11 Golden Path suite;
7. Repair 10 sectioned-Markdown suite;
8. STTM parser/evidence/reference/auditor/pipeline suites;
9. workspace classification and containment suites;
10. physical-write containment suites;
11. Repair 9 regression;
12. Repair 8 regression;
13. Repairs 5/6/7 regressions;
14. trusted Job Config envelope suite;
15. canonical full unit suite.

Expected canonical full-unit result:

FULL_UNIT_PASSING_COUNT: 2243
FULL_UNIT_PENDING_COUNT: 1
FULL_UNIT_FAILURE_COUNT: 5

Expected unchanged failures:

1. EvalGating — passes against the committed Phase H baseline report
2. EvalGating — allows deterministic v3 baseline reports without prompt telemetry
3. Copilot workflow customization — maintainer delivery prompt references real repo-local agents
4. Copilot workflow customization — repo customization assets use valid frontmatter and agent file naming
5. Copilot workflow customization — source tree uses standard AGENTS.md guidance instead of module AGENT.md files

Confirm the five failure identities independently. Do not merely label them
historical.

npm run test:unit:guarded is expected to short-circuit before its GitHub guard
because the canonical unit command exits 1 with the five accepted failures.

Report that behavior honestly, then execute the existing GitHub guard separately
and report its independent result.

Required:

COMPILE_PASS: YES
LINT_PASS: YES
REPAIR_12_FOCUSED_PASS: YES
REPAIR_12_CANONICAL_EXECUTION_COUNT: 1
FULL_UNIT_PASSING_COUNT: 2243
FULL_UNIT_PENDING_COUNT: 1
FULL_UNIT_FAILURE_COUNT: 5
FULL_UNIT_FAILURE_IDENTITIES_UNCHANGED: YES
GITHUB_GUARD_SEPARATE_PASS: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

Do not change tests or baselines to obtain these results.

==================================================
9. FINDING CLASSIFICATION

Report findings in severity order:

* CRITICAL
* HIGH
* MEDIUM
* LOW
* INFORMATIONAL

For every finding include:

* exact file;
* symbol or line area;
* reproducible evidence;
* affected contract;
* whether it blocks packaging;
* smallest safe remediation.

Do not fix findings during this review.

A correctness or security finding at CRITICAL, HIGH, or MEDIUM blocks acceptance.

Do not count these expected facts as defects by themselves:

* the protected 0.3.144 VSIX predates Repair 12;
* the five known full-unit failures remain unchanged;
* the audit timestamp is the sole demonstrated nondeterministic field;
* the QA Source/Target values are logical dotted literals rather than physical
    ADLS paths.

==================================================
10. FINAL NON-MUTATION CHECK

Re-capture and compare:

* HEAD;
* branch;
* staged files;
* stash count;
* working-tree hashes;
* QA STTM size, hash, and mtime;
* existing 0.3.144 VSIX size, hash, and mtime;
* package.json version;
* all seven Repair 12 paths.

Required:

REVIEW_SOURCE_FILES_MODIFIED: 0
REVIEW_TEST_FILES_MODIFIED: 0
PACKAGE_JSON_MODIFIED_BY_REVIEW: NO
QA_STTM_MODIFIED: NO
EXISTING_0_3_144_VSIX_MODIFIED: NO
PACKAGE_LOCK_CREATED: NO
VSIX_BUILT: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
STAGED_FILES_AT_END: 0

==================================================
11. FINAL REPORT

Return:

INDEPENDENT_SESSION_CONFIRMED: YES/NO
REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION: 
PROCESS_EXECUTION_PREFLIGHT: PASS/FAIL
STAGED_FILES_AT_START: 
STAGED_FILES_AT_END: 

REPAIR_12_CHANGED_PATH_COUNT: 
REPAIR_12_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
REPAIR_12_PATTERN_REGISTERED: YES/NO
REPAIR_12_PATTERN_MATCH_COUNT: 
REPAIR_12_CANONICAL_EXECUTION_COUNT: 
EXISTING_PATTERNS_REMOVED: 
EXISTING_PATTERNS_BROADENED: 

SHARED_PUBLIC_PROJECTOR_CONFIRMED: YES/NO
STRUCTURED_MARKDOWN_PARITY: YES/NO
NOTES_EXPOSED_STRUCTURED: YES/NO
NOTES_EXPOSED_MARKDOWN: YES/NO
NOTES_ADVISORY_UNTRUSTED: YES/NO
SOURCE_LITERAL_EXPOSED_STRUCTURED: YES/NO
SOURCE_LITERAL_EXPOSED_MARKDOWN: YES/NO
TARGET_LITERAL_EXPOSED_STRUCTURED: YES/NO
TARGET_LITERAL_EXPOSED_MARKDOWN: YES/NO
MAPPING_ID_COUNT_STRUCTURED: 
MAPPING_ID_COUNT_MARKDOWN: 
MAPPING_IDS_UNIQUE_DERIVABLE: YES/NO
MAPPING_IDS_UNIQUE_FIELD_ADDED: YES/NO
MAPPING_ORDER_PRESERVED: YES/NO
RAW_FALLBACK_USED: YES/NO
LLM_FALLBACK_USED: YES/NO
PHYSICAL_PATH_FABRICATED: YES/NO
UNITY_CATALOG_INFERENCE_USED: YES/NO
SIBLING_FILES_ENUMERATED: 
PUBLIC_SEAM_TEST_CONFIRMED: YES/NO
DETERMINISM_PASS: YES/NO
DETERMINISM_DIFFERENCES: 

COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_12_FOCUSED_PASS: YES/NO
FULL_UNIT_PASSING_COUNT: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURES: 
FULL_UNIT_FAILURE_IDENTITIES_UNCHANGED: YES/NO
GITHUB_GUARD_SEPARATE_PASS: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

CRITICAL_FINDING_COUNT: 
HIGH_FINDING_COUNT: 
MEDIUM_FINDING_COUNT: 
LOW_FINDING_COUNT: 
INFORMATIONAL_FINDING_COUNT: 
FINDINGS: 

EXISTING_0_3_144_VSIX_UNCHANGED: YES/NO
QA_STTM_UNCHANGED: YES/NO
REPOSITORY_STATE_PRESERVED: YES/NO
READY_FOR_VERSION_BUMP_AND_PACKAGE: YES/NO
READY_TO_INSTALL: NO
READY_FOR_RUNTIME_QA: NO

PASS requires:

* genuinely independent session;
* exact repository identity;
* exact seven-path Repair 12 boundary;
* canonical test registration exactly once;
* real public structured and Markdown seams verified;
* exact Notes, Source, Target, mappings, IDs, and filters exposed;
* no fabricated or authority-escalating evidence;
* no sibling enumeration;
* deterministic behavior except the documented audit timestamp;
* all required focused and regression gates pass;
* canonical unit count is 2243/1/5 with identical five failures;
* zero new functional regressions;
* zero new security regressions;
* no CRITICAL, HIGH, or MEDIUM correctness/security findings;
* zero repository, QA, package, installation, Runtime QA, Preview, or write mutation.

End exactly with one:

INDEPENDENT_REVIEW_0_3_144_RESULT: PASS_READY_FOR_VERSION_BUMP_AND_PACKAGE

INDEPENDENT_REVIEW_0_3_144_RESULT: FAIL_FINDINGS

INDEPENDENT_REVIEW_0_3_144_RESULT: FAIL_CHANGE_BOUNDARY

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_IDENTITY_MISMATCH

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_STAGED_CHANGES

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_CONCURRENT_MUTATION

INDEPENDENT_REVIEW_0_3_144_RESULT: BLOCKED_WRONG_PROMPT
