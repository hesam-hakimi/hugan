TASK: HF1_V2_REPAIR_12_REGISTER_CANONICAL_TEST_SUITE_AND_REVERIFY

Continue the existing Repair 12 implementation task in the same Software
Development Environment and the same Chat.

This is a narrowly authorized follow-up. Do not repeat Root Cause 12 and do not
redesign or modify the Repair 12 implementation.

The implementation report established:

* Repair 12 focused suite: 21 passing;
* EtlReadOnlyToolService suite: 49 passing;
* canonical full unit suite: 2222 passing, 1 pending, 5 failing;
* src/test/suite/sttmRepair12.test.ts is not included in
    PURE_UNIT_TEST_PATTERNS;
* therefore its 21 tests pass in focused execution but are absent from
    npm run test:unit.

This violates the required canonical-suite coverage gate and must be corrected
before independent review.

==================================================

1. IDENTITY AND BASELINE
    ==================================================

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Required:

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION:
0.3.144

Before editing, verify:

* native git, node, npm, and cmd execution still works;
* staged file count is zero;
* package version remains 0.3.144;
* existing 0.3.144 VSIX size and SHA-256 match the Repair 12 baseline;
* the six Repair 12 implementation paths are unchanged since the completed
    implementation report;
* the QA STTM remains size 1437 with SHA-256:
    F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

If another process or agent changed the repository after the Repair 12 report,
stop without editing:

REPAIR_12_REGISTRATION_RESULT: BLOCKED_CONCURRENT_MUTATION

==================================================
2. ADDITIONAL AUTHORIZED PATH

Authorize exactly one additional changed path:

src/test/testPatterns.ts

The only authorized change in this file is registering:

src/test/suite/sttmRepair12.test.ts

in the existing PURE_UNIT_TEST_PATTERNS allowlist, following the exact existing
format and ordering convention.

Do not:

* change another pattern;
* remove or broaden an existing pattern;
* replace the allowlist with a glob;
* change test-runner logic;
* change sttmRepair12.test.ts;
* modify production source;
* modify EtlReadOnlyToolService.test.ts;
* modify package.json;
* modify the QA STTM;
* modify the 0.3.144 VSIX.

The final Repair 12 change boundary may therefore contain the previous six paths
plus this newly authorized seventh path.

If another path is required, stop:

REPAIR_12_REGISTRATION_RESULT: BLOCKED_CHANGE_BOUNDARY

==================================================
3. VERIFY REGISTRATION DIRECTLY

After the one-line registration:

1. inspect the resolved PURE_UNIT_TEST_PATTERNS;
2. prove sttmRepair12.test.ts matches exactly once;
3. prove no existing test pattern was removed or broadened;
4. prove the canonical unit runner discovers the Repair 12 suite;
5. prove the 21 Repair 12 tests are not executed twice.

Required:

REPAIR_12_PATTERN_MATCH_COUNT: 1
REPAIR_12_DUPLICATE_EXECUTION: NO
EXISTING_PATTERNS_REMOVED: 0
EXISTING_PATTERNS_BROADENED: 0

==================================================
4. VALIDATION

Run and report exact commands and exit codes for:

1. TypeScript compile;
2. lint;
3. Repair 12 focused suite;
4. canonical full unit suite;
5. the repository’s guarded unit command, if it is an existing local command
    that does not download dependencies.

Required focused result:

REPAIR_12_FOCUSED:
21 passing, 0 pending, 0 failing

Previous canonical baseline before registration:

2222 passing
1 pending
5 failing

Expected canonical result after registration:

2243 passing
1 pending
5 failing

The increase must be exactly 21 and must correspond exactly to the newly
registered Repair 12 tests.

The five existing failure identities must remain exactly:

* two EvalGating committed Phase-H baseline failures;
* maintainer delivery prompt references real repo-local agents;
* repository customization assets use valid frontmatter and agent naming;
* source tree uses standard AGENTS.md guidance instead of module AGENT.md files.

Required:

FULL_UNIT_PASSING_COUNT: 2243
FULL_UNIT_PENDING_COUNT: 1
FULL_UNIT_FAILURE_COUNT: 5
FULL_UNIT_PASSING_DELTA: 21
FULL_UNIT_FAILURE_IDENTITIES_UNCHANGED: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

If the total is not exactly 2243/1/5, investigate only test discovery and
duplicate execution. Do not change production code or weaken tests.

==================================================
5. DETERMINISM TEST DECISION

Do not modify the existing determinism test in this follow-up.

The existing test permits only the documented wall-clock Audited at line to
differ and asserts that all other semantic output remains stable.

Leave this behavior unchanged for the independent reviewer to evaluate.

Report:

AUDIT_TIMESTAMP_EXCEPTION_CHANGED: NO
OTHER_NONDETERMINISTIC_FIELDS_FOUND: YES/NO

==================================================
6. SAFETY AND CHANGE BOUNDARY

Recapture the final working-tree baseline.

Required task-attributable change in this follow-up:

src/test/testPatterns.ts

* exactly one Repair 12 registration entry.

Required:

PRODUCTION_FILES_CHANGED_BY_FOLLOWUP: 0
TEST_CONTENT_FILES_CHANGED_BY_FOLLOWUP: 0
PACKAGE_JSON_CHANGED_BY_FOLLOWUP: NO
PACKAGE_VERSION: 0.3.144
PACKAGE_LOCK_CREATED: NO
EXISTING_0_3_144_VSIX_MODIFIED: NO
QA_STTM_MODIFIED: NO
STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
VSIX_BUILT: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO

Do not clean, restore, reset, stash, stage, commit, package, or install.

==================================================
7. STOP POINT

Stop after the canonical suite proves that all 21 Repair 12 tests are registered
and executed exactly once.

Do not perform the independent review in this Chat.

The next step after PASS is a new Chat containing a genuinely independent
reviewer prompt.

==================================================
8. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION: 
PROCESS_EXECUTION_PREFLIGHT: PASS/FAIL
STAGED_FILES_AT_START: 
STAGED_FILES_AT_END: 

REPAIR_12_PATTERN_REGISTERED: YES/NO
REPAIR_12_PATTERN_MATCH_COUNT: 
REPAIR_12_DUPLICATE_EXECUTION: YES/NO
EXISTING_PATTERNS_REMOVED: 
EXISTING_PATTERNS_BROADENED: 
FOLLOWUP_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 

COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_12_FOCUSED_PASS: YES/NO
REPAIR_12_FOCUSED_PASSING_COUNT: 
FULL_UNIT_PASSING_COUNT_BEFORE: 2222
FULL_UNIT_PASSING_COUNT_AFTER: 
FULL_UNIT_PASSING_DELTA: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURES: 
FULL_UNIT_FAILURE_IDENTITIES_UNCHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

AUDIT_TIMESTAMP_EXCEPTION_CHANGED: NO
OTHER_NONDETERMINISTIC_FIELDS_FOUND: YES/NO

PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
EXISTING_0_3_144_VSIX_MODIFIED: NO
QA_STTM_MODIFIED: NO
PRODUCTION_FILES_CHANGED_BY_FOLLOWUP: 0
TEST_CONTENT_FILES_CHANGED_BY_FOLLOWUP: 0
VSIX_BUILT: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO

READY_FOR_GENUINELY_INDEPENDENT_REVIEW: YES/NO
READY_TO_BUMP_VERSION: NO
READY_TO_PACKAGE: NO
READY_TO_INSTALL: NO

PASS requires:

* exactly one new test registration entry;
* all 21 Repair 12 tests executed exactly once by the canonical unit runner;
* final canonical count exactly 2243 passing, 1 pending, 5 failing;
* accepted five failure identities unchanged;
* zero production or test-content changes in this follow-up;
* zero new functional or security regressions;
* source version remains 0.3.144;
* no VSIX, install, Runtime QA, Preview, write, commit, push, or tag.

End exactly with one:

REPAIR_12_REGISTRATION_RESULT: PASS_READY_FOR_INDEPENDENT_REVIEW
REPAIR_12_REGISTRATION_RESULT: BLOCKED_IDENTITY
REPAIR_12_REGISTRATION_RESULT: BLOCKED_STAGED_CHANGES
REPAIR_12_REGISTRATION_RESULT: BLOCKED_EXECUTION_ENVIRONMENT
REPAIR_12_REGISTRATION_RESULT: BLOCKED_CONCURRENT_MUTATION
REPAIR_12_REGISTRATION_RESULT: BLOCKED_CHANGE_BOUNDARY
REPAIR_12_REGISTRATION_RESULT: FAIL_TEST_DISCOVERY
REPAIR_12_REGISTRATION_RESULT: FAIL_REGRESSION
REPAIR_12_REGISTRATION_RESULT: FAIL_CHANGE_BOUNDARY
