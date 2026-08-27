TASK: HF1_V2_REPAIR_13_OWNER_DISPOSITION_GOLDEN_REFRESH_AND_PURE_UNIT_REGISTRATION

Perform the two exact repository-owner actions required after the successful
independent review of Repair 13.

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Execution context:

* VS Code option 4: Claude harness;
* fresh Chat;
* built-in generic claude Agent;
* do not select etl-hotfix-implementer;
* do not select etl-independent-reviewer;
* Claude Opus 5 with Max reasoning;
* Current Folder, not Worktree;
* exactly one effective repository target;
* Local execution only.

The independent review concluded:

REPAIR_13_INDEPENDENT_REVIEW_RESULT:
PASS_WITH_REQUIRED_SEPARATE_OWNER_ACTIONS

Repair 13 itself is independently certified as correct, complete, minimal, and
non-regressing.

This prompt records an explicit repository-owner decision authorizing exactly two
mechanical follow-up actions:

OWNER_ACTION_1:
Refresh the Phase H golden eval baseline for the two independently verified
legitimate Repair 13 behavior-input changes.

OWNER_ACTION_2:
Register the Repair 13 focused suite exactly once in the canonical Pure Unit test
registry.

No other action is authorized.

==================================================

1. VERIFIED REPAIR 13 STATE
    ==================================================

The independently reviewed Repair 13 change set is:

Modified:

1. src/core/sttm/SttmResolvedEvidence.ts
2. src/core/sttm/SttmUnderstandingReportRenderer.ts
3. src/tools/EtlReadOnlyToolService.ts

Added:

4. src/test/suite/sttmRepair13.test.ts

The independent review proved:

* one positive-grant authoritative selector;
* no negative authority predicate;
* compile-time exhaustive state coverage;
* runtime fail-closed handling;
* structured/Markdown parity in 19/19 scenarios;
* Repair 13 focused suite: 23/23;
* Repair 12: 21/21;
* Repair 11: 22/22;
* QA STTM unchanged;
* no Repair 13 functional or security regression;
* no unauthorized Repair 13 path;
* unresolved schema references are display-only, read-only, and
    non-authoritative;
* no Preview, Write, approval, generation, packaging, installation, or Runtime QA
    authority was introduced.

Do not reopen or redesign Repair 13.

Do not modify the four Repair 13 paths in this task.

==================================================
2. REQUIRED IDENTITY

Verify:

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

Required:

* exactly one effective Current Folder repository target;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrently running Agent mutation;
* Repair 13 four-path change set still present;
* no version bump, package, install, Runtime QA, commit, or push;
* protected VSIX files unchanged.

Prove visible stdout, stderr, executable identity, and real exit codes for:

* cmd.exe;
* git.exe;
* node.exe;
* npm.cmd or the exact underlying Node command.

Use task-owned file-redirection helpers under the OS temporary directory when the
known inline-capture/PATH defect occurs.

Do not modify the repository to recover process execution.

Stop without mutation on identity mismatch, staged files, concurrent mutation, or
unproven execution.

==================================================
3. INDEPENDENT PRE-ACTION SNAPSHOT

Before any mutation, capture an independent Git plus OS-hash baseline containing:

* all tracked modifications and deletions;
* all non-ignored untracked files;
* all Repair 13 paths;
* all Phase H eval baseline paths;
* src/test/testPatterns.ts;
* package.json;
* package-lock.json state;
* tsconfig.json and tsconfig.test.json;
* Repair 11 and Repair 12 paths;
* canonical QA STTM;
* .gitignore;
* .claude/**;
* CLAUDE.md;
* governance manifest, scripts, tests, and workflow;
* all eleven src/**/AGENT.md files;
* all VSIX files.

Store all logs, generated candidates, snapshots, and mirrors under a unique OS
temporary directory.

Do not use Git alone because the repository has a large untracked overlay.

==================================================
4. EXACT AUTHORIZED CHANGE BOUNDARY

This task may change only:

A. the exact existing Phase H golden baseline file or files proven to be written
by the repository’s canonical eval:golden command;

B. src/test/testPatterns.ts, with exactly one narrow additive Pure Unit pattern
for the freshly compiled Repair 13 suite.

Before editing, return:

PROPOSED_GOLDEN_BASELINE_PATHS: 
PROPOSED_TEST_REGISTRATION_PATH:
src/test/testPatterns.ts

PROPOSED_EXACT_REGISTRATION_LINE: 
PROPOSED_PATTERN_MATCH_COUNT: 

Do not edit until:

* every proposed golden baseline path is proven to be canonical output of the
    existing generator;
* no unrelated file would be generated or modified;
* the registration pattern matches exactly one compiled suite;
* the registration pattern overlaps no existing Pure Unit pattern;
* duplicate execution remains impossible.

If the generator requires changes outside the exact baseline outputs, stop:

OWNER_DISPOSITION_RESULT: BLOCKED_GOLDEN_OUTPUT_SCOPE

If exact one-suite registration cannot be proven, stop:

OWNER_DISPOSITION_RESULT: BLOCKED_REGISTRATION_SCOPE

Everything else is protected.

==================================================
5. OWNER ACTION 1 — CONTROLLED GOLDEN REFRESH

Do not run the golden generator directly against the live repository first.

Create a byte-faithful temporary mirror containing tracked and untracked working
content.

In the mirror:

1. freshly compile required source;
2. run the canonical Phase H eval validation before regeneration;
3. record the two expected EvalGating failures;
4. run the repository’s canonical golden-generation command;
5. capture every generated path and exact diff;
6. run the generator a second time from the same normalized inputs;
7. identify deterministic fields and permitted timestamp/latency fields;
8. validate the regenerated baseline;
9. confirm all Phase H scenarios pass.

Expected legitimate drift inputs:

* src/core/sttm/SttmResolvedEvidence.ts;
* src/core/sttm/SttmUnderstandingReportRenderer.ts.

The independent review established that these are the only tracked Phase H input
hashes expected to change.

src/tools/EtlReadOnlyToolService.ts and
src/test/suite/sttmRepair13.test.ts were not tracked Phase H baseline inputs.

Required regenerated semantic results:

* acceptanceRate: 1;
* parityRate: 1;
* validationSuccessRate: 1;
* coverage complete;
* required scenarios: 9/9 passing;
* missing required scenarios: none;
* no behavioral regression;
* no containment regression;
* no security regression.

The diff may contain only:

* the baseline digest derived from the legitimate inputs;
* hashes for the two legitimate drifted inputs;
* canonical generation timestamp fields;
* expected latency measurement fields.

It must not:

* remove scenarios;
* weaken thresholds;
* reduce coverage;
* change acceptance semantics;
* hide failures;
* exclude Repair 13 inputs improperly;
* regenerate unrelated historical baselines.

After the candidate passes, apply only the exact canonical baseline output files
to the live repository.

Do not copy any compiled out/**, logs, reports, caches, or temporary files.

Required:

GOLDEN_REFRESH_SEMANTIC_REGRESSION: NO
GOLDEN_REFRESH_MISSING_SCENARIOS: NONE
GOLDEN_REFRESH_UNRELATED_PATHS: NONE

==================================================
6. OWNER ACTION 2 — PURE UNIT REGISTRATION

Inspect the live canonical test registry and compiled suite layout.

The independent review established:

* source suite:
    src/test/suite/sttmRepair13.test.ts;
* compiled suite:
    out/test/suite/sttmRepair13.test.js;
* the suite currently runs through:
    INTEGRATION_TEST_PATTERNS;
* it is not executed by the headless canonical Pure Unit channel;
* it compiles and is discovered exactly once in a fresh mirror;
* TEST_REGISTRATION is owned by repository-owner;
* the implementer correctly did not edit src/test/testPatterns.ts.

Add exactly one narrow pattern to the existing Pure Unit registry.

The independently proposed pattern was equivalent to an exact
sttmRepair13.test.js match. Re-derive the precise syntax from the live registry
instead of copying punctuation blindly.

The final pattern must:

* match out/test/suite/sttmRepair13.test.js;
* match exactly one compiled file;
* execute the suite exactly once in the Pure Unit runner;
* introduce 23 focused passing tests;
* not match Repair 11 or Repair 12 suites;
* not match sibling suites;
* not overlap another Pure Unit pattern;
* not broaden to suite/**;
* not change Integration Test patterns;
* not reorder or rewrite unrelated registry entries.

Make no other change to src/test/testPatterns.ts.

Required:

PURE_UNIT_PATTERN_MATCH_COUNT: 1
PURE_UNIT_DUPLICATE_EXECUTION: NO
REPAIR_13_PURE_UNIT_EXECUTION_COUNT: 1
REPAIR_13_PURE_UNIT_PASSING: 23
REPAIR_13_PURE_UNIT_FAILING: 0

==================================================
7. STALE LIVE OUT POLICY

The live out/** tree is a pre-Repair-13 stale build.

Do not update live out/** in this task.

Do not copy compiled output from the mirror to the live repository.

All fresh compilation and test validation must occur in a temporary mirror.

The prior COMPILED_SUITE_MISSING governance finding is expected against stale
live out/** and must disappear in the freshly compiled mirror.

Required:

LIVE_OUT_MODIFIED: NO
FRESH_MIRROR_COMPILED_SUITE_PRESENT: YES
FRESH_MIRROR_COMPILED_SUITE_DISCOVERY_COUNT: 1
FRESH_MIRROR_GOVERNANCE_TESTS_PASS: YES

Fresh compiled output will be created later by the authorized VERSION_AND_PACKAGE
lifecycle stage.

==================================================
8. VALIDATION

After applying the two exact live changes, create a fresh byte-faithful mirror of
the resulting working tree.

Run:

1. compile;
2. compile:test;
3. lint;
4. Repair 13 focused suite;
5. Repair 13 Pure Unit discovery and execution;
6. Repair 12 canonical suite;
7. Repair 11 focused suite;
8. STTM regression suites;
9. EtlReadOnlyToolService suites;
10. public-seam parity scenarios;
11. containment/security suites;
12. trusted-envelope suites;
13. Phase H EvalGating tests;
14. Phase H golden validation without regeneration;
15. customization validator;
16. test-registration validator;
17. governance tests;
18. canonical full unit suite;
19. independent snapshot → action → compare lifecycle.

Required:

COMPILE_PASS: YES
COMPILE_TEST_PASS: YES
LINT_PASS: YES
REPAIR_13_FOCUSED_PASS: YES
REPAIR_13_PURE_UNIT_PASS: YES
REPAIR_12_CANONICAL_PASS: YES
REPAIR_11_FOCUSED_PASS: YES
STTM_REGRESSION_PASS: YES
PUBLIC_TOOL_REGRESSION_PASS: YES
CONTAINMENT_SECURITY_PASS: YES
TRUSTED_ENVELOPE_PASS: YES
EVAL_GATING_PASS: YES
GOLDEN_VALIDATION_PASS: YES
CUSTOMIZATION_BLOCKERS: 0
CUSTOMIZATION_MAJOR_FINDINGS: 0
CUSTOMIZATION_MINOR_FINDINGS: 0
REGISTRATION_ENFORCING_FINDINGS: 0
GOVERNANCE_TESTS_PASSING: 224
GOVERNANCE_TESTS_FAILING: 0

Previous canonical full unit state after Repair 13 but before owner actions:

* 2244 passing;
* 1 pending;
* 4 failing.

Expected changes:

* the two legitimate EvalGating failures become passing;
* the 23 Repair 13 tests become newly included in Pure Unit;
* the two known pre-existing customization failures remain unchanged.

Expected canonical full unit result, if all counts compose exactly:

* 2269 passing;
* 1 pending;
* 2 failing.

Do not force the numeric expectation. Derive the exact result and explain any
difference by test identity.

Known pre-existing failures:

F1:

* missing .github/prompts/deploy-v3-agent-tool-context-gap.prompt.md.

F3:

* assertion concerning eleven existing src/**/AGENT.md files.

The pending test remains:

KnowledgeAdvisor Integration Tests

Required:

EVAL_GATING_FAILURES_REMAINING: 0
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0
PRE_EXISTING_FAILURE_FINGERPRINTS_CHANGED: NO

==================================================
9. FINAL CHANGE-BOUNDARY PROOF

Compare the final live repository with the independent pre-action snapshot.

Expected task-attributable changes:

* exact Phase H golden baseline output file or files;
* one additive line in src/test/testPatterns.ts.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
REPAIR_13_SOURCE_CHANGED: NO
REPAIR_13_FOCUSED_TEST_CHANGED: NO
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
DEPENDENCIES_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
TSCONFIG_CHANGED: NO
REPAIR_11_CONTENT_CHANGED: NO
REPAIR_12_CONTENT_CHANGED: NO
QA_STTM_CHANGED: NO
GOVERNANCE_FILES_CHANGED: NO
CLAUDE_NATIVE_FILES_CHANGED: NO
GITIGNORE_CHANGED: NO
LEGACY_AGENT_FILES_CHANGED: NO
LIVE_OUT_MODIFIED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
RUNTIME_QA_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
STAGED_FILES: 0
STASH_ENTRIES: 0

==================================================
10. INDEPENDENCE AND NEXT STAGE

This owner-action session may implement and validate only the two authorized
owner actions.

It may not independently review or certify them.

After successful completion, a fresh etl-independent-reviewer session must
review:

* exact golden baseline diff;
* exact Pure Unit registration line;
* match and execution counts;
* full validation results;
* non-mutation boundary.

Do not start VERSION_AND_PACKAGE in this session.

Do not bump to 0.3.145.

Do not build or install a VSIX.

Do not start Runtime QA.

==================================================
11. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
INDEPENDENT_BASELINE_CAPTURED: YES/NO

GOLDEN_BASELINE_PATHS_CHANGED: 
GOLDEN_BASELINE_DIFF: 
GOLDEN_BASELINE_INPUTS_CHANGED: 
GOLDEN_BASELINE_UNRELATED_INPUTS_CHANGED: 
EVAL_ACCEPTANCE_RATE: 
EVAL_PARITY_RATE: 
EVAL_VALIDATION_SUCCESS_RATE: 
EVAL_REQUIRED_SCENARIOS_PASSING: <number/number>
EVAL_MISSING_REQUIRED_SCENARIOS: 
GOLDEN_REFRESH_SEMANTIC_REGRESSION: YES/NO

TEST_REGISTRATION_PATH_CHANGED: 
PURE_UNIT_PATTERN_ADDED: 
PURE_UNIT_PATTERN_MATCH_COUNT: 
PURE_UNIT_DUPLICATE_EXECUTION: YES/NO
REPAIR_13_PURE_UNIT_EXECUTION_COUNT: 
REPAIR_13_PURE_UNIT_PASSING: 
REPAIR_13_PURE_UNIT_FAILING: 

LIVE_OUT_MODIFIED: YES/NO
FRESH_MIRROR_COMPILED_SUITE_PRESENT: YES/NO
FRESH_MIRROR_COMPILED_SUITE_DISCOVERY_COUNT: 

COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_13_FOCUSED_PASS: YES/NO
REPAIR_13_PURE_UNIT_PASS: YES/NO
REPAIR_12_CANONICAL_PASS: YES/NO
REPAIR_11_FOCUSED_PASS: YES/NO
STTM_REGRESSION_PASS: YES/NO
PUBLIC_TOOL_REGRESSION_PASS: YES/NO
CONTAINMENT_SECURITY_PASS: YES/NO
TRUSTED_ENVELOPE_PASS: YES/NO
EVAL_GATING_PASS: YES/NO
GOLDEN_VALIDATION_PASS: YES/NO

GOVERNANCE_TESTS_PASSING: 
GOVERNANCE_TESTS_FAILING: 
CUSTOMIZATION_BLOCKERS: 
CUSTOMIZATION_MAJOR_FINDINGS: 
CUSTOMIZATION_MINOR_FINDINGS: 
REGISTRATION_ENFORCING_FINDINGS: 

FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_FAILURES: 
EVAL_GATING_FAILURES_REMAINING: 
PRE_EXISTING_FAILURE_FINGERPRINTS_CHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
REPAIR_13_SOURCE_CHANGED: NO
REPAIR_13_FOCUSED_TEST_CHANGED: NO
REPAIR_12_CONTENT_CHANGED: NO
QA_STTM_CHANGED: NO
GOVERNANCE_FILES_CHANGED: NO
LIVE_OUT_MODIFIED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
STAGED_FILES: 

READY_FOR_INDEPENDENT_OWNER_ACTION_REVIEW: YES/NO
READY_FOR_VERSION_AND_PACKAGE: NO
READY_TO_BUMP_TO_0_3_145: NO
READY_FOR_INSTALL_OR_RUNTIME_QA: NO
READY_FOR_COMMIT_OR_PUSH: NO
READY_FOR_CLOUD_ROLLOUT: NO

End exactly with one:

OWNER_DISPOSITION_RESULT:
PASS_READY_FOR_INDEPENDENT_OWNER_ACTION_REVIEW

OWNER_DISPOSITION_RESULT:
FAIL_GOLDEN_BASELINE_VALIDATION

OWNER_DISPOSITION_RESULT:
FAIL_TEST_REGISTRATION_VALIDATION

OWNER_DISPOSITION_RESULT:
FAIL_FUNCTIONAL_OR_SECURITY_REGRESSION

OWNER_DISPOSITION_RESULT:
FAIL_UNAUTHORIZED_CHANGE

OWNER_DISPOSITION_RESULT:
BLOCKED_IDENTITY_OR_WORKTREE_DRIFT

OWNER_DISPOSITION_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT

OWNER_DISPOSITION_RESULT:
BLOCKED_GOLDEN_OUTPUT_SCOPE

OWNER_DISPOSITION_RESULT:
BLOCKED_REGISTRATION_SCOPE

OWNER_DISPOSITION_RESULT:
BLOCKED_OWNER_DELEGATION
