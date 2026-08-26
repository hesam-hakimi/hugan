TASK: HF1_V2_INDEPENDENT_REVIEW_AGENT_GOVERNANCE_FRAMEWORK_READ_ONLY

Perform a genuinely independent, read-only review of the newly implemented
Agent/Governance Process Framework.

Work only in:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use a fresh generic local Agent session.

Do NOT select or invoke the newly created etl-independent-reviewer or any other
newly created custom agent to certify the framework that created it.

Treat all newly created or modified instructions, agents, skills, prompts,
templates, governance scripts, workflows, CLAUDE.md content, and reports as
objects under review—not as trusted proof.

This task is independent review only. Make zero repository changes.

==================================================

1. EXPECTED IDENTITY
    ==================================================

Required identity:

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

* exactly one open workspace root;
* zero staged files;
* package-lock.json absent;
* existing 0.3.144 VSIX protected;
* no Repair 13 implementation;
* no commit, push, package, install, or Runtime QA.

If identity differs, stop:

PROCESS_FRAMEWORK_INDEPENDENT_REVIEW_RESULT: BLOCKED_IDENTITY

==================================================
2. STRICT NON-MUTATION BOUNDARY

Do not create, edit, delete, rename, restore, clean, stage, stash, or regenerate
any repository file.

Do not run commands that regenerate docs/eval reports in the live repository.
Do not run package preparation or VSIX verification.
Do not modify out/** in the live repository.

Commands requiring generated output must run in a task-owned isolated temporary
mirror or with all outputs redirected under the operating-system temporary
directory.

Existing local dependencies may be reused read-only.
Do not install or download anything.
Do not create package-lock.json.

Capture complete repository status, file hashes, and mtimes before and after the
review. Any repository mutation caused by the review is a failure:

PROCESS_FRAMEWORK_INDEPENDENT_REVIEW_RESULT: FAIL_REVIEW_MUTATED_REPOSITORY

==================================================
3. EXECUTION RECOVERY

The implementation session observed a session-local process-capture defect:

* inline PowerShell capture sometimes returned empty output;
* npm.cmd with shell:false could return EINVAL;
* native processes themselves remained executable;
* redirected Start-Process execution with separate stdout/stderr worked.

Independently verify this behavior.

Do not misclassify empty inline capture as a missing toolchain or repository
failure.

Use task-owned temporary helpers and redirected stdout/stderr when necessary.
Require visible output and a real exit code from Git, Node, npm or its underlying
command, and cmd.exe.

If native execution cannot be proven through the recovery route, make no changes
and stop:

PROCESS_FRAMEWORK_INDEPENDENT_REVIEW_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

==================================================
4. FRAMEWORK INVENTORY

Independently enumerate and inspect all relevant current assets, including:

* .github/copilot-instructions.md;
* .github/instructions/**/*.instructions.md;
* .github/skills/*/SKILL.md;
* .github/agents/*.agent.md;
* .github/prompts/*.prompt.md;
* .github/templates/**;
* .github/agent-governance/**;
* scripts/agent-governance/**;
* .github/workflows/** related to governance;
* root AGENTS.md;
* root CLAUDE.md;
* all tracked src/**/AGENT.md files.

Produce a complete manifest containing:

* repository-relative path;
* tracked/untracked/modified status;
* asset type;
* byte size;
* SHA-256;
* local loading mechanism;
* Cloud static-support classification;
* authority classification;
* referenced files;
* validation result.

Confirm that no policy depends on screenshots, chat history, local absolute
paths, developer-machine state, or uncommitted evidence outside the repository.

Cloud runtime activation is outside this review and must remain:

CLOUD_RUNTIME_ACTIVATION_PROVEN: NO

==================================================
5. REVIEW IMPLEMENTED GOVERNANCE DESIGN

Review the reported framework implementation:

* five skills:
    * etl-hotfix-lifecycle;
    * etl-independent-review;
    * etl-package-delivery;
    * etl-runtime-qa;
    * etl-execution-recovery;
* three custom agents:
    * etl-hotfix-implementer;
    * etl-independent-reviewer;
    * etl-release-verifier;
* governance manifest, README, schemas, and templates;
* governance validation scripts and libraries;
* governance test suites;
* governance CI workflow;
* instruction frontmatter changes;
* CLAUDE.md bridge behavior.

Verify:

* responsibilities are distinct and non-overlapping;
* no agent can self-certify its own implementation;
* implementation and independent review require separate sessions;
* prompts are convenience wrappers, not Cloud authority;
* skills contain reusable procedures rather than duplicated global policy;
* canonical rules have one authority;
* local and Cloud surfaces do not silently diverge;
* mutation, Preview, approval, packaging, installation, and Runtime QA
    boundaries remain explicit;
* no agent grants itself approval;
* no consumer context becomes machine authority;
* Bypass Permissions is not treated as authorization to violate repository
    boundaries.

Report every duplicate, contradiction, unreachable reference, circular
authority, ambiguous owner, or missing stop condition.

==================================================
6. RECONCILE VALIDATOR FINDINGS

The implementation report stated:

* governance tests: 76 passing, 0 failing;
* customization validation: 0 blocker, 0 major, 8 minor findings;
* registration validation:
    * 1 SUITE_NOT_REGISTERED;
    * 11 COMPILED_SUITE_MISSING;
    * 1 COMPUTED_PATTERN_ENTRY;
* compile, test compile, and lint passed;
* full unit baseline before process changes:
    2245 passing, 1 pending, 3 failing;
* full unit after process changes:
    2246 passing, 1 pending, 2 failing;
* F2 was resolved by valid instruction frontmatter;
* F1 and F3 remained.

Independently reproduce and reconcile every diagnostic.

Do not accept aggregate counts alone.

Return:

* all eight customization minor findings;
* all eleven COMPILED_SUITE_MISSING paths and disposition;
* the exact COMPUTED_PATTERN_ENTRY and disposition;
* the exact SUITE_NOT_REGISTERED path and evidence;
* exact failure names, locations, and fingerprints for F1 and F3;
* whether F2 is genuinely resolved without weakening its assertion.

==================================================
7. UNREGISTERED SUITE INVESTIGATION

Inspect:

src/test/unit/SourceValidationStateHandler.test.ts

and:

src/test/testPatterns.ts

Determine:

* whether the source suite is genuine;
* whether its compiled JavaScript exists;
* whether any canonical runner discovers it;
* how many tests it contains;
* whether it is currently executed zero times;
* whether one narrow registration entry would discover it exactly once;
* whether a broad src/test/unit/** pattern would cause duplicate or unintended
    discovery.

Do not edit the registry.

If confirmed, provide the exact one-line proposed registration and its exact
expected match and execution counts.

Also inspect whether the governance CI registration step currently uses
continue-on-error and whether fail-closed enforcement is safe after the detector
is repaired.

==================================================
8. BASELINE TOOLING SCHEMA INVESTIGATION

Inspect and dynamically test:

* capture-baseline.mjs;
* verify-change-boundary.mjs;
* their libraries, schemas, and tests.

The implementation agent reported that the capture tool wrote a flat
path-to-SHA form while the verifier expected a different nested schema.

Reproduce this only with task-owned temporary fixtures.

Test:

1. capture then verify without change;
2. one added file;
3. one modified file;
4. one deleted file;
5. staged-state drift;
6. malformed baseline;
7. missing required field;
8. unknown schema version;
9. Windows separator/case normalization;
10. directory marker versus file entry.

Determine whether the tools:

* share one schema and reader/writer;
* silently reinterpret incompatible data;
* can incorrectly report an empty baseline as clean;
* fabricate Git state that was never captured;
* fail closed on malformed or unknown input.

Return an exact bounded repair design and exact authorized paths. Do not
implement it.

==================================================
9. F1 AGENT/PROMPT FINDING

Inspect the exact F1 test, its referenced paths, current agents, prompts,
manifest, and repository history available locally.

The implementation report says F1 expects three additional Custom Agents and one
maintainer-delivery prompt, including an agent named:

ETL Delivery Orchestrator

Determine:

* the exact three expected agent identities and paths;
* the exact missing prompt path;
* whether those assets express real distinct repository responsibilities;
* whether the test represents a current authoritative contract or stale
    repository expectation;
* whether creating them would improve the framework or merely make the test
    green;
* whether existing agents already own the same responsibilities;
* whether any Cloud-critical rule would exist only in the prompt.

Do not create agents or prompts.
Do not weaken or edit the test.

Return one recommendation:

* CREATE_EXACT_MISSING_ASSETS;
* UPDATE_AUTHORITATIVE_CONTRACT;
* DEFER_AS_EXACT_KNOWN_BASELINE_FAILURE.

Support the recommendation with file-level evidence.

==================================================
10. F3 LEGACY AGENT.md FINDING

Enumerate the exact eleven tracked files matching:

src/**/AGENT.md

For every file report:

* path;
* SHA-256;
* Git provenance;
* references from other files;
* unique versus duplicated instructions;
* current scope;
* closest canonical destination if migration is appropriate;
* risk of deletion.

Do not delete, rename, or migrate any file.
Do not weaken or retire the F3 assertion.

Determine whether the correct future action is:

* content-preserving migration to scoped AGENTS.md/instructions;
* retention with an explicit compatibility decision;
* deletion only after proven semantic migration;
* retirement or correction of a stale assertion.

Blind deletion solely to obtain a passing test must be rejected.

Return a complete migration ledger proposal if migration is recommended.

==================================================
11. VALIDATION

Run all safe read-only validations from an isolated temporary mirror or with
temporary output redirection:

* governance Node tests;
* customization validator;
* registration validator;
* governance manifest/schema validator;
* workflow validator;
* TypeScript compile;
* test compile;
* lint;
* exact F1 test;
* exact F2 test;
* exact F3 test;
* Repair 12 focused suite;
* canonical full unit suite;
* GitHub mutation guard through its documented snapshot lifecycle.

Do not use an ad-hoc Mocha command that bypasses the VS Code bootstrap.
Do not run npm test if it downloads VS Code.
Do not run eval/report generators against the live repository.

Require a fresh compiled result, not stale out/**.

Report exact commands, execution route, exit codes, passing/pending/failing
counts, and exact failure fingerprints.

==================================================
12. REVIEW VERDICT AND CONSOLIDATED PLAN

Produce one consolidated, minimal stabilization plan.

The plan must distinguish:

A. fixes required before local Repair 13;
B. findings safely deferred until after the hotfix;
C. changes required only before commit/push or Cloud rollout;
D. findings that are stale tests rather than implementation defects.

Explicitly evaluate this proposed disposition:

* register SourceValidationStateHandler exactly once with one narrow pattern;
* repair baseline capture/verification through one shared versioned schema;
* make registration CI fail closed only after the detector is trustworthy;
* do not create extra agents merely to satisfy F1 unless distinct authoritative
    roles are proven;
* preserve all eleven AGENT.md files until a content-preserving migration is
    independently justified;
* do not change Repair 13, product source, package version, or VSIX.

For every recommended change provide:

* exact paths;
* exact intended change;
* exact tests;
* protected invariants;
* stop conditions.

==================================================
13. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_RECOVERY_PASS: YES/NO
REPOSITORY_MUTATED_BY_REVIEW: YES/NO
FRAMEWORK_ASSET_COUNT: 
FRAMEWORK_ASSET_MANIFEST: 

GOVERNANCE_TEST_PASSING_COUNT: 
GOVERNANCE_TEST_FAILURE_COUNT: 
CUSTOMIZATION_BLOCKER_COUNT: 
CUSTOMIZATION_MAJOR_COUNT: 
CUSTOMIZATION_MINOR_FINDINGS: 

REGISTRATION_SUITE_NOT_REGISTERED_COUNT: 
REGISTRATION_SUITE_NOT_REGISTERED_PATHS: 
REGISTRATION_COMPILED_SUITE_MISSING_COUNT: 
REGISTRATION_COMPILED_SUITE_MISSING_PATHS: 
REGISTRATION_COMPUTED_PATTERN_ENTRY_COUNT: 
REGISTRATION_COMPUTED_PATTERN_ENTRIES: 

SOURCE_VALIDATION_SUITE_GENUINE: YES/NO
SOURCE_VALIDATION_CURRENT_EXECUTION_COUNT: 
SOURCE_VALIDATION_PROPOSED_PATTERN: 
SOURCE_VALIDATION_EXPECTED_EXECUTION_COUNT_AFTER_FIX: 

BASELINE_SCHEMA_MISMATCH_REPRODUCED: YES/NO
BASELINE_UNCHANGED_ROUNDTRIP_PASS: YES/NO
BASELINE_MALFORMED_INPUT_FAILS_CLOSED: YES/NO
BASELINE_TOOLING_MINIMAL_REPAIR_PATHS: 

F1_EXACT_FAILURE: 
F1_RECOMMENDATION: 
F1_REQUIRED_ASSETS_IF_CONFIRMED: 

F3_EXACT_FAILURE: 
LEGACY_AGENT_MD_COUNT: 
LEGACY_AGENT_MD_MIGRATION_RECOMMENDATION: 
LEGACY_AGENT_MD_LEDGER: 

FULL_UNIT_PASSING_COUNT: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURES: 
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

LOCAL_AGENT_STATIC_READINESS: YES/NO
CLOUD_STATIC_COMPATIBILITY: YES/NO
CLOUD_RUNTIME_ACTIVATION_PROVEN: NO
READY_FOR_LOCAL_REPAIR_13: YES/NO
READY_TO_PUBLISH_PROCESS_FRAMEWORK: NO
READY_FOR_BOUNDED_STABILIZATION: YES/NO
CONSOLIDATED_STABILIZATION_PLAN: 

SOURCE_FILES_MODIFIED_BY_REVIEW: 0
TEST_FILES_MODIFIED_BY_REVIEW: 0
GOVERNANCE_FILES_MODIFIED_BY_REVIEW: 0
PACKAGE_JSON_MODIFIED: NO
PACKAGE_VERSION_CHANGED: NO
VSIX_MODIFIED: NO
QA_WORKSPACE_MUTATED: NO
REPAIR_13_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

A successful review requires:

* zero repository mutations;
* every validator diagnostic reconciled;
* baseline-schema mismatch dynamically characterized;
* unregistered-suite diagnosis proven;
* F1 and F3 grounded in actual repository evidence;
* complete manifest and hashes;
* zero unreported High or Security findings;
* one bounded stabilization plan.

End exactly with one:

PROCESS_FRAMEWORK_INDEPENDENT_REVIEW_RESULT: FINDINGS_CONFIRMED_READY_FOR_BOUNDED_FIX

PROCESS_FRAMEWORK_INDEPENDENT_REVIEW_RESULT: FAIL_ADDITIONAL_HIGH_OR_SECURITY_FINDINGS

PROCESS_FRAMEWORK_INDEPENDENT_REVIEW_RESULT: BLOCKED_IDENTITY

PROCESS_FRAMEWORK_INDEPENDENT_REVIEW_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

PROCESS_FRAMEWORK_INDEPENDENT_REVIEW_RESULT: FAIL_REVIEW_MUTATED_REPOSITORY
