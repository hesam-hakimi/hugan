TASK: HF1_V2_REPAIR_13_GENUINELY_INDEPENDENT_REVIEW_READ_ONLY

Perform a genuinely independent, strictly read-only review of Repair 13:

HF1_V2_REPAIR_13_AUTHORITATIVE_ACTIVE_MAPPING_PARITY

Work only against:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Execution context:

* VS Code option 4: Claude harness;
* fresh Chat and separate session;
* selected Agent: etl-independent-reviewer;
* Claude Opus 5 with Max reasoning;
* Current Folder, not Worktree;
* exactly one effective repository target;
* Local execution only.

The selected reviewer did not implement Repair 13, and Repair 13 did not modify
the reviewer’s Agent definition, Skill, manifest authority, governance schema, or
governance validators.

This task is independent review only.

Make zero repository changes.

Do not accept the implementer’s report, checkpoint, tests, descriptions, or
OWNER_DECISION_REQUIRED result as trusted proof. Re-derive every material claim
from current source and independent dynamic execution.

==================================================

1. EXPECTED IDENTITY
    ==================================================

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

* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrent Agent mutation;
* existing VSIX artifacts unchanged;
* Repair 13 implementation present;
* no version bump, package, installation, Runtime QA, commit, or push.

Prove real executable identity, stdout, stderr, and exit codes for cmd.exe,
git.exe, node.exe, and npm.cmd or its underlying Node command.

Use task-owned OS-temporary helpers if the known inline-capture/PATH defect is
present.

Do not modify the repository to repair execution.

==================================================
2. STRICT NON-MUTATION

Make zero changes to the live repository.

Do not create, edit, delete, rename, restore, clean, stage, stash, compile, or
regenerate anything in the live tree.

In particular, do not:

* edit Repair 13 source or tests;
* edit src/test/testPatterns.ts;
* regenerate Phase H or golden eval baselines;
* run npm run eval:golden against the live repository;
* generate live out/** or dist/**;
* modify governance assets;
* fix Git durability findings;
* install dependencies;
* build or install a VSIX;
* start Preview, Write, or Runtime QA;
* commit or push.

Capture an independent OS-hash and Git snapshot before review.

Run all compilation, dynamic tests, mutation fixtures, and generated-output
commands only in a byte-faithful task-owned temporary mirror containing both
tracked and untracked working-tree content.

Repeat the live snapshot afterward. Any live mutation is a review failure even
if subsequently restored.

==================================================
3. EXACT REPAIR 13 CHANGE SET

Verify that Repair 13 changed only these four paths:

1. src/core/sttm/SttmResolvedEvidence.ts
2. src/core/sttm/SttmUnderstandingReportRenderer.ts
3. src/tools/EtlReadOnlyToolService.ts
4. src/test/suite/sttmRepair13.test.ts

Expected classification:

* modified existing files: 3;
* added files: 1;
* deleted files: 0;
* unauthorized paths: 0.

For each path report:

* current Git status;
* byte size;
* SHA-256;
* exact changed symbols;
* responsibility;
* callers and consumers;
* whether the change is necessary for Repair 13;
* whether unrelated behavior changed.

Verify independently that these remained unchanged:

* src/test/testPatterns.ts;
* package.json and version;
* package-lock.json absence;
* tsconfig.json and tsconfig.test.json;
* .gitignore;
* .claude/**;
* CLAUDE.md;
* governance manifest and workflow;
* Repair 12 paths;
* canonical QA STTM;
* all eleven src/**/AGENT.md files;
* every existing VSIX.

==================================================
4. ROOT-CAUSE VERIFICATION

Independently reproduce the pre-fix defect from the prior content or a
byte-faithful reconstructed fixture without changing the live repository.

The implementation report claims:

* Markdown used the negative predicate:
    activeState !== "inactive";
* this admitted conflicting, historical, or unknown rows;
* structured output withheld those rows;
* four of thirteen scenarios diverged:
    * 06_one_conflicting;
    * 08_duplicate_target_identity;
    * 10_mixed_all_states;
    * 13_shipped_bundle.

Verify:

* the exact old predicate;
* the exact structured-channel selection behavior;
* all four claimed divergent scenarios;
* exact structured IDs;
* exact Markdown IDs;
* exact ordering;
* exact diagnostics;
* that the focused suite genuinely fails against pre-fix behavior.

Do not accept source inspection alone. Require dynamic public-seam reproduction.

==================================================
5. AUTHORITATIVE SELECTOR REVIEW

Inspect the implementation of:

selectActiveMappings()

and its exact type declarations and callers.

Verify:

* there is one shared selector;
* both structured and Markdown channels consume its exact selected collection;
* activeMappingsCount uses the same selected collection;
* neither channel performs a second filter;
* neither channel reorders independently;
* ordering is deterministic and preserves the canonical authored order;
* selection does not mutate the input;
* there is no hidden global state;
* all declared states are exhaustively covered;
* no negative-state predicate grants authority.

Independently enumerate the actual declared state model.

The report claims an authority table equivalent to:

* active → selected;
* inactive → excluded;
* historical → excluded;
* unknown → excluded;
* conflicting → excluded.

Verify this from the source type and runtime behavior.

If additional states exist, include and test all of them.

==================================================
6. CRITICAL UNRESOLVED-MAPPING CONTRADICTION

Resolve this apparent contradiction in the implementation report.

The report claims both:

A. “Unresolved excluded, fails closed.”

and:

B. “An unresolved reference on an active mapping keeps the mapping active and
discloses the ID rather than silently dropping it.”

These claims may describe different concepts, or they may represent a
machine-authority defect.

Determine precisely:

* what constitutes an unresolved mapping;
* what constitutes an unresolved reference;
* whether either condition leaves a mapping in Active Mappings;
* whether an unresolved essential source/target/reference can retain machine
    authority;
* whether the public structured result marks it active;
* whether Markdown marks it active;
* whether activeMappingsCount includes it;
* whether Preview or downstream generation may consume it;
* which diagnostic is emitted;
* whether status and stop code fail closed.

Required security rule:

A mapping with an unresolved authority-critical source, target, identity, or
reference must not retain active machine authority.

Disclosure alone is insufficient if the mapping remains executable or
authoritative.

Test at minimum:

1. active mapping with all references resolved;
2. active mapping with unresolved non-authoritative display metadata;
3. active mapping with unresolved source reference;
4. active mapping with unresolved target reference;
5. active mapping with unresolved identity;
6. unknown state;
7. missing state;
8. malformed state;
9. conflicting state;
10. mixed valid and unresolved mappings.

Return one exact determination:

* UNRESOLVED_CONTRACT_CORRECT_AND_FAILS_CLOSED;
* UNRESOLVED_DISPLAY_ONLY_REFERENCE_NON_AUTHORITATIVE;
* FAIL_UNRESOLVED_MAPPING_RETAINS_MACHINE_AUTHORITY;
* BLOCKED_UNRESOLVED_CONTRACT_AMBIGUOUS.

If authority-critical unresolved content remains active, Repair 13 must fail
regardless of channel parity.

==================================================
7. CONFLICT AND AUTHORITY REVIEW

Verify:

* conflicting mappings are absent from both Active Mappings channels;
* conflicts are disclosed deterministically under the intended exclusion
    section;
* the exact diagnostic code is STTM_CONFLICTING_ACTIVE_ROWS, or report the
    actual canonical code;
* conflicting mappings cannot be used by downstream machine behavior;
* inactive mappings do not create blockers merely because they are inactive;
* unknown or undeclared state fails closed;
* no mapping disappears silently;
* excludedMappings is disclosure-only;
* activeAuthority: false is present wherever required;
* no new public operation or authority surface was introduced.

Inspect the public seam in:

src/tools/EtlReadOnlyToolService.ts

Verify that the change narrows or preserves authority and does not:

* add a write path;
* add Preview approval;
* add a public mutation;
* grant authority from display context;
* expose an internal bypass;
* broaden tool registration.

==================================================
8. STRUCTURED/MARKDOWN PARITY

Through the full public seam, independently execute all thirteen scenarios from
the Repair 13 suite.

For every scenario report:

* declared mapping states;
* structured IDs and order;
* Markdown IDs and order;
* excluded IDs;
* diagnostic codes;
* status;
* stop code;
* active mapping count;
* expected versus actual result.

Required:

* divergent scenarios after fix: 0;
* IDs equal in both channels;
* ordered IDs equal;
* same selected collection identity or exact immutable projection;
* deterministic repeated execution;
* full public seam tested;
* shipped bundle tested;
* no private-helper-only proof.

Confirm or disprove the reported focused result:

23 passing / 0 failing.

==================================================
9. QA STTM AND REPAIR 12 PRESERVATION

Verify the canonical repository-side QA STTM remains byte-identical.

Report:

* mapping count;
* source literals;
* target literals;
* filters;
* notes;
* byte size;
* SHA-256.

Do not access or modify the external Development Test Workspace.

Verify:

* QA STTM unchanged;
* Repair 12 source unchanged;
* Repair 12 test behavior unchanged;
* Repair 12 canonical suite: 21/21;
* Repair 11 focused suite: 22/22 if still canonical;
* no historical baseline was regenerated;
* no assertion was weakened or deleted.

==================================================
10. PHASE H EVAL BASELINE FINDING

Investigate the two new full-suite failures independently:

1. EvalGating > passes against the committed Phase H baseline report
2. EvalGating > allows deterministic v3 baseline reports without prompt telemetry

The report attributes both to changed tracked behavior inputs:

* src/core/sttm/SttmResolvedEvidence.ts;
* src/core/sttm/SttmUnderstandingReportRenderer.ts.

Determine:

* the exact baseline file or files;
* exact baseline schema;
* exact hashes recorded before Repair 13;
* which Repair 13 paths are covered;
* why EtlReadOnlyToolService.ts is or is not covered;
* whether the gate is intentionally detecting legitimate behavior change;
* whether any behavioral metric regressed;
* whether acceptanceRate remains 1;
* whether parityRate remains 1;
* whether validationSuccessRate remains 1;
* whether missingRequiredScenarios remains empty;
* whether the existing baseline is stale or Repair 13 introduced a real eval
    regression;
* the exact diff a separately authorized golden refresh would produce.

Do not regenerate or approve the baseline.

Return one disposition:

* LEGITIMATE_REPAIR_REQUIRES_SEPARATE_GOLDEN_BASELINE_REFRESH;
* REPAIR_13_BEHAVIOR_REGRESSION;
* EVAL_GATE_COVERAGE_DEFECT;
* BLOCKED_EVAL_BASELINE_AMBIGUITY.

A later golden-baseline refresh may be recommended only if:

* all Repair 13 behavior is correct;
* no acceptance, parity, validation, containment, or security metric regressed;
* the exact generated diff is independently reviewed;
* regeneration occurs in a separately authorized stage.

==================================================
11. COMPILED_SUITE_MISSING FINDING

Investigate:

COMPILED_SUITE_MISSING

The implementation report states:

* live out/** contains 139 suites;
* fresh temporary mirror contains 140 suites;
* the mirror registration validator passes;
* the live build is stale;
* live compilation was forbidden to preserve the repository.

Determine whether this represents:

* a source/test registration defect;
* expected stale generated output;
* missing source compilation coverage;
* an incorrect validator diagnostic;
* an actual release blocker requiring a later canonical build.

Do not compile into the live tree.

Freshly compile in the temporary mirror and prove:

* sttmRepair13.test.ts compiles;
* the compiled output exists;
* source and compiled output correspond;
* the focused runner discovers it exactly once;
* no duplicate execution occurs.

Return one disposition:

* EXPECTED_STALE_LIVE_OUTPUT_FRESH_MIRROR_PASS;
* REPAIR_13_COMPILE_OR_DISCOVERY_DEFECT;
* VALIDATOR_DIAGNOSTIC_DEFECT;
* BLOCKED_COMPILED_SUITE_AMBIGUITY.

==================================================
12. TEST REGISTRATION AND OWNERSHIP CONFLICT

Inspect:

* src/test/testPatterns.ts;
* the canonical unit runner;
* the exact single-suite runner;
* process-manifest ownership for TEST_REGISTRATION;
* Agent authority for etl-hotfix-implementer;
* any PURE_UNIT_TEST_PATTERNS registry.

The implementation report states:

* the task authorized a testPatterns.ts change;
* the governance manifest reserves TEST_REGISTRATION for repository-owner;
* the implementer correctly left testPatterns.ts unchanged;
* the suite runs through an existing integration/single-suite pattern;
* it does not run under the canonical npm run test:unit discovery;
* SUITES_DISCOVERED_COUNT is 1;
* unregistered count is 0 under the integration validator;
* duplicate count is 0.

Determine:

* whether Repair 13 is registered in any canonical registry;
* which canonical commands execute it;
* whether it executes exactly once;
* whether it is omitted from the full unit suite;
* whether integration-only coverage is sufficient for this defect;
* whether PURE_UNIT_TEST_PATTERNS is the correct destination;
* exact one-line proposed registration if required;
* exact owner/stage authorized to make that change;
* exact match count after the proposed change;
* duplicate-execution risk.

Do not edit the registry.

Return one disposition:

* CURRENT_INTEGRATION_REGISTRATION_IS_CANONICAL_AND_SUFFICIENT;
* SEPARATE_OWNER_AUTHORIZED_PURE_UNIT_REGISTRATION_REQUIRED;
* REGISTRATION_VALIDATOR_OR_MANIFEST_CONFLICT;
* BLOCKED_REGISTRATION_CONTRACT_AMBIGUOUS.

==================================================
13. GOVERNANCE TEST ENVIRONMENT FINDING

Investigate the reported split governance result:

* governance live: 224 tests with 223 passing and 1 failing;
* governance mirror: 224 tests with 223 passing and 1 failing;
* failure identities reportedly differ;
* every test allegedly passes in the environment supporting its assumptions;
* temporary mirror may lack .git.

Re-run governance validation in correctly constructed temporary environments.

Distinguish:

* genuine governance regression;
* mirror missing Git metadata;
* live stale generated output;
* process-capture defect;
* test environment assumption defect;
* validator defect.

Report exact failing test identity and fingerprint in every environment.

Do not dismiss disjoint failures solely because their counts match.

Return:

GOVERNANCE_ALL_TESTS_PASS_IN_ONE_VALID_ENVIRONMENT: YES/NO
GOVERNANCE_ENVIRONMENT_ASSUMPTION_DEFECT: YES/NO
GOVERNANCE_NEW_REGRESSION: YES/NO
GOVERNANCE_EXACT_FAILURES: 

==================================================
14. VALIDATION

Run read-only or temporary-mirror validation for:

1. Repair 13 focused suite;
2. all thirteen mapping scenarios;
3. structured/Markdown ordered parity;
4. unresolved authority-negative cases;
5. conflict disclosure;
6. public EtlReadOnlyToolService seam;
7. compile;
8. compile:test;
9. lint;
10. Repair 12 canonical suite;
11. Repair 11 focused suite if canonical;
12. STTM regression suites;
13. EtlReadOnlyToolService regression suite;
14. golden-path suite;
15. containment/security suites;
16. trusted-envelope suites;
17. governance tests;
18. customization validator;
19. test-registration validator;
20. canonical full unit suite;
21. independent snapshot → action → compare lifecycle.

Report exact commands, execution routes, exit codes, duration, and failure
fingerprints.

Expected prior baseline:

* full unit: 2246 passing, 1 pending, 2 failing.

Reported Repair 13 result:

* 2244 passing, 1 pending, 4 failing.

Determine whether the two additional failures are exclusively stale-baseline
gates or real regressions.

Known pre-existing failures:

F1:

* missing .github/prompts/deploy-v3-agent-tool-context-gap.prompt.md.

F3:

* assertion concerning eleven existing src/**/AGENT.md files.

Both must remain unchanged.

The pending suite should remain:

KnowledgeAdvisor Integration Tests

==================================================
15. FINAL NON-MUTATION PROOF

Compare the live repository after review with the independent pre-review
snapshot.

Required:

REPOSITORY_MUTATED_BY_REVIEW: NO
UNAUTHORIZED_CHANGED_PATHS: NONE
STAGED_FILES: 0
STASH_ENTRIES: 0
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
TEST_PATTERNS_CHANGED_BY_REVIEW: NO
TSCONFIG_CHANGED: NO
REPAIR_12_CONTENT_CHANGED: NO
QA_STTM_CHANGED: NO
LEGACY_AGENT_FILES_CHANGED: NO
GOVERNANCE_FILES_CHANGED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

==================================================
16. REVIEW DECISION

A successful review does not require the Phase H baseline or test registry to be
modified in this session.

It requires exact disposition of every finding.

Repair 13 may proceed to bounded owner disposition only if:

* the functional repair is correct;
* one authoritative selector is proven;
* structured and Markdown outputs have exact ordered parity;
* every declared state is handled safely;
* conflicts are excluded and disclosed;
* authority-critical unresolved mappings cannot remain active;
* no public machine authority was broadened;
* QA STTM and Repair 12 remain unchanged;
* the two new EvalGating failures are proven to be stale-baseline gates rather
    than regressions;
* fresh mirror compilation and discovery pass;
* the exact registration ownership decision is identified;
* governance failures are reconciled;
* no new functional or security regression exists;
* live repository remains unchanged by review.

==================================================
17. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
INDEPENDENCE_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
REPOSITORY_MUTATED_BY_REVIEW: YES/NO

REPAIR_13_CHANGED_PATHS: 
UNAUTHORIZED_REPAIR_13_PATHS: 
ROOT_CAUSE_CONFIRMED: YES/NO
PRE_FIX_DIVERGENT_SCENARIOS: 
POST_FIX_DIVERGENT_SCENARIOS: 

DECLARED_STATE_MODEL: 
SHARED_SELECTOR_PATH_AND_SYMBOL: 
STRUCTURED_CHANNEL_USES_SHARED_SELECTION: YES/NO
MARKDOWN_CHANNEL_USES_SHARED_SELECTION: YES/NO
ACTIVE_COUNT_USES_SHARED_SELECTION: YES/NO
ORDERED_IDS_EQUAL_ALL_SCENARIOS: YES/NO
NEGATIVE_AUTHORITY_PREDICATE_PRESENT: YES/NO

UNRESOLVED_CONTRACT_DETERMINATION: 
UNRESOLVED_SOURCE_RETAINS_AUTHORITY: YES/NO
UNRESOLVED_TARGET_RETAINS_AUTHORITY: YES/NO
UNRESOLVED_IDENTITY_RETAINS_AUTHORITY: YES/NO
UNRESOLVED_PUBLIC_STATUS: 
UNRESOLVED_STOP_CODE: 

CONFLICT_DIAGNOSTIC_CODE: 
CONFLICTS_EXCLUDED_FROM_BOTH_CHANNELS: YES/NO
CONFLICTS_DETERMINISTICALLY_DISCLOSED: YES/NO
INACTIVE_MAPPING_CAUSES_BLOCKER: YES/NO
UNKNOWN_OR_UNDECLARED_STATE_FAILS_CLOSED: YES/NO
PUBLIC_MACHINE_AUTHORITY_BROADENED: YES/NO

REPAIR_13_FOCUSED_PASSING: 
REPAIR_13_FOCUSED_FAILING: 
REPAIR_13_SCENARIOS_EXECUTED: 
FULL_PUBLIC_SEAM_TESTED: YES/NO

QA_STTM_UNCHANGED: YES/NO
REPAIR_12_CANONICAL_PASS: YES/NO
REPAIR_11_FOCUSED_PASS: YES/NO

EVAL_BASELINE_DISPOSITION: 
EVAL_BASELINE_FILES: 
EVAL_BASELINE_PROPOSED_DIFF: 
EVAL_ACCEPTANCE_RATE: 
EVAL_PARITY_RATE: 
EVAL_VALIDATION_SUCCESS_RATE: 
EVAL_MISSING_REQUIRED_SCENARIOS: 
GOLDEN_BASELINE_REFRESH_AUTHORIZED_IN_THIS_REVIEW: NO

COMPILED_SUITE_DISPOSITION: 
FRESH_MIRROR_SUITE_COMPILED: YES/NO
FRESH_MIRROR_SUITE_DISCOVERY_COUNT: 
LIVE_OUT_STALE: YES/NO

REGISTRATION_DISPOSITION: 
CURRENT_CANONICAL_EXECUTION_ROUTES: 
CANONICAL_FULL_UNIT_EXECUTES_REPAIR_13: YES/NO
PROPOSED_REGISTRATION_PATH: 
PROPOSED_EXACT_REGISTRATION_LINE: 
PROPOSED_PATTERN_MATCH_COUNT: <number or N/A>
REGISTRATION_OWNER_STAGE: 

GOVERNANCE_ALL_TESTS_PASS_IN_ONE_VALID_ENVIRONMENT: YES/NO
GOVERNANCE_ENVIRONMENT_ASSUMPTION_DEFECT: YES/NO
GOVERNANCE_NEW_REGRESSION: YES/NO
GOVERNANCE_EXACT_FAILURES: 

COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
STTM_REGRESSION_PASS: YES/NO
PUBLIC_TOOL_REGRESSION_PASS: YES/NO
CONTAINMENT_SECURITY_PASS: YES/NO
TRUSTED_ENVELOPE_PASS: YES/NO

FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_FAILURES: 
TWO_ADDITIONAL_FAILURES_STALE_BASELINE_ONLY: YES/NO
PRE_EXISTING_FAILURES_UNCHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

OWNER_DECISIONS_REQUIRED: 
MINIMAL_FOLLOW_UP_PATHS: 
MINIMAL_FOLLOW_UP_TESTS: 
READY_FOR_BOUNDED_OWNER_DISPOSITION: YES/NO
READY_FOR_VERSION_BUMP: NO
READY_FOR_PACKAGE_OR_INSTALL: NO
READY_FOR_RUNTIME_QA: NO
READY_FOR_COMMIT_OR_PUSH: NO
READY_FOR_CLOUD_ROLLOUT: NO

End exactly with one:

REPAIR_13_INDEPENDENT_REVIEW_RESULT:
PASS_READY_FOR_BOUNDED_OWNER_DISPOSITION

REPAIR_13_INDEPENDENT_REVIEW_RESULT:
FAIL_UNRESOLVED_MAPPING_RETAINS_MACHINE_AUTHORITY

REPAIR_13_INDEPENDENT_REVIEW_RESULT:
FAIL_FUNCTIONAL_OR_SECURITY_REGRESSION

REPAIR_13_INDEPENDENT_REVIEW_RESULT:
FAIL_CHANGE_BOUNDARY

REPAIR_13_INDEPENDENT_REVIEW_RESULT:
FAIL_REVIEW_MUTATED_REPOSITORY

REPAIR_13_INDEPENDENT_REVIEW_RESULT:
BLOCKED_IDENTITY_OR_WORKTREE_DRIFT

REPAIR_13_INDEPENDENT_REVIEW_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT

REPAIR_13_INDEPENDENT_REVIEW_RESULT:
BLOCKED_CONTRACT_AMBIGUITY
