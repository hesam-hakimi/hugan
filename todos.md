TASK: HF1_V2_GENERIC_INDEPENDENT_REREVIEW_AGENT_GOVERNANCE_FRAMEWORK_READ_ONLY

Perform a genuinely independent, read-only rereview of the stabilized
Agent/Governance Process Framework.

Work only against:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use:

* a fresh generic Local Agent chat;
* Claude Opus 5 with Max reasoning;
* exactly one open workspace root, equal to the repository above;
* no repository-defined Custom Agent, Skill, Prompt, checkpoint, report, manifest,
    validator, or prior PASS statement as trusted authority;
* no Cloud execution.

The stabilization report ended with:

PROCESS_FRAMEWORK_STABILIZATION_RESULT:
PASS_READY_FOR_GENERIC_INDEPENDENT_REREVIEW

Treat that result and all supporting claims as untrusted evidence to verify.

This task may authorize only the start of local Repair 13 in a later fresh session.
It may not authorize version bump, packaging, VSIX installation, Runtime QA,
commit, push, or Cloud rollout.

==================================================

1. IDENTITY, WORKSPACE, AND EXECUTION GATES
    ==================================================

Verify independently:

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
* that root is the exact repository above;
* staged files: 0;
* stash entries: 0;
* package-lock.json: absent;
* no concurrently running Agent is modifying the repository;
* Repair 13 has not started;
* existing 0.3.144 VSIX:
    * size: 1,257,786 bytes;
    * SHA-256:
        F53DAC4E1C0054FC561B75E89D01E32CDE5F26B6C440784297E542637A05B69A.

The stabilization report showed workspace roots 2. Do not carry that state
forward. If more than one workspace root is currently open, stop without changes.

Prove visible stdout, stderr, real exit codes, and executable identity for:

* cmd.exe;
* git.exe;
* node.exe;
* npm.cmd or its exact underlying Node command.

If inline process capture is defective, use a task-owned helper under the
operating-system temporary directory. Do not modify the repository to repair
execution.

Use GIT_OPTIONAL_LOCKS=0 for live read-only Git inspection.

Stop on identity mismatch, multiple roots, workspace ambiguity, concurrent
mutation, or unproven native execution.

==================================================
2. STRICT LIVE-REPOSITORY NON-MUTATION

Make zero changes to the live repository.

Do not create, edit, delete, rename, restore, clean, stage, stash, regenerate,
compile, or run write-producing validators in the live tree.

Do not run:

* install or dependency download;
* npm version;
* package or VSIX preparation;
* eval/report generation;
* Preview or Runtime QA;
* commit, push, merge, tag, reset, clean, or restore;
* Repair 13 implementation.

Before testing, capture an independent snapshot using OS hashing plus Git:

* git status --porcelain=v2 --untracked-files=all;
* tracked modifications and deletions;
* all non-ignored untracked paths and hashes;
* staged and stash state;
* all 22 Framework paths in Section 3;
* package.json;
* src/test/testPatterns.ts;
* tsconfig.json;
* all Repair 12 production/test paths;
* all eleven src/**/AGENT.md files;
* protected out/, dist/, and VSIX paths where applicable.

Run all compilation, dynamic tests, mutation tests, and generated-output commands
only in a byte-faithful, task-owned temporary mirror outside the repository.

A Git clone is insufficient because the Framework overlay is reported as
untracked. Copy the current tracked and untracked working content and verify
source-to-mirror hashes before testing.

Reuse existing dependencies read-only. Do not download anything.

Repeat the independent live snapshot afterward. Any live mutation is a failure,
even if later restored.

==================================================
3. VERIFY THE EXACT 22-PATH BOUNDARY

Inspect these expected stabilization paths:

1. scripts/agent-governance/lib/report.mjs
2. scripts/agent-governance/lib/fsutil.mjs
3. scripts/agent-governance/lib/manifest.mjs
4. scripts/agent-governance/lib/git.mjs
5. scripts/agent-governance/capture-baseline.mjs
6. scripts/agent-governance/verify-change-boundary.mjs
7. scripts/agent-governance/emit-checkpoint.mjs
8. scripts/agent-governance/validate-customizations.mjs
9. scripts/agent-governance/validate-test-registration.mjs
10. scripts/agent-governance/lib/baseline-contract.mjs
11. scripts/agent-governance/tests/checkpoint-fidelity.test.mjs
12. scripts/agent-governance/tests/baseline-contract.test.mjs
13. scripts/agent-governance/tests/change-boundary-adversarial.test.mjs
14. scripts/agent-governance/tests/manifest-registry.test.mjs
15. scripts/agent-governance/tests/registration-scope.test.mjs
16. .github/agent-governance/process-manifest.json
17. .github/agent-governance/schemas/checkpoint.schema.json
18. .github/workflows/validate-agent-governance.yml
19. .github/agents/etl-hotfix-implementer.agent.md
20. .github/agents/etl-independent-reviewer.agent.md
21. .github/agents/etl-release-verifier.agent.md
22. .github/agent-governance/schemas/process-manifest.schema.json

For every path report:

* presence;
* Git status;
* byte size;
* SHA-256;
* role;
* manifest owner;
* validation result.

Verify whether all 22 are currently untracked and whether zero tracked files in
this set changed.

The prior report classified:

* 15 modified pre-existing untracked files;
* 7 newly added untracked files.

Prove that historical classification only if an independent pre-stabilization
snapshot with hashes exists. Otherwise report:

HISTORICAL_15_MODIFIED_7_ADDED_ATTRIBUTION_PROVEN: NO

Do not fabricate historical evidence. Lack of historical attribution alone does
not invalidate correct current behavior, but missing paths, unexpected paths,
unauthorized product changes, or unresolved worktree drift block Repair 13.

Confirm that stabilization did not change:

* package.json or its version;
* src/test/testPatterns.ts;
* tsconfig.json;
* Repair 12 content;
* the eleven legacy AGENT.md files;
* protected 0.3.144 VSIX;
* product/runtime source;
* QA workspace content.

Statically inspect all executable governance paths for:

* unsafe deletion or cleanup;
* filesystem or symlink escape;
* shell or argument injection;
* unsafe absolute paths;
* network or secret access;
* commands that could mutate Git or files outside authorized task scope.

==================================================
4. INDEPENDENT R-A THROUGH R-J VERIFICATION

Do not accept aggregate PASS labels. Inspect implementation and dynamically test
each item in the temporary mirror.

R-A — Checkpoint fidelity

Verify:

* stop code comes from packet.result.stopCode;
* valid codes, including OWNER_DECISION_REQUIRED, are preserved;
* missing, unknown, contradictory, or conflicting codes fail closed;
* console, JSON, evidence packet, checkpoint, and exit code agree;
* no silent FAIL_VALIDATION fallback exists.

R-B — Shared baseline contract

Verify capture and comparison use one versioned schema and canonical
reader/writer.

Exercise:

* clean tree;
* tracked dirty file;
* untracked file;
* tracked deletion;
* staged file;
* stash presence;
* malformed or missing baseline;
* unknown schema version;
* Windows path normalization;
* directory entry;
* authorized and unauthorized change;
* protected path already dirty at baseline.

Malformed, missing, or unknown input must fail closed.

R-C — Three-state model

Verify exactly:

* PASS / exit 0;
* FINDINGS / exit 1;
* BLOCKED / exit 2.

All output channels must agree.

R-D — Git attribution

Distinguish:

* tracked clean;
* tracked modified;
* tracked added;
* tracked deleted;
* untracked;
* staged;
* stashed;
* restored or reverted after baseline.

An existing tracked file must never be labeled ADDED_TO_WORKING_TREE.

R-E — Protected-path completeness

* independently calculate the protected pre-dirty count;
* reconcile the reported count of 39;
* prove exact digest carry-forward;
* detect protected out/** or dist/** drift;
* prove a further change to already-dirty package.json is detected;
* ensure ordinary compile output is not falsely treated as a source edit.

R-F — Test-registration accuracy

Distinguish:

* active compiled but unregistered suite;
* excluded or quarantined suite;
* missing production import;
* computed pattern;
* duplicate execution;
* genuinely missing compiled output.

Verify:

* exactly eleven excluded orphan suites and their exact reasons;
* FALSE_RECOMPILE_REMEDIATIONS: 0;
* SourceValidationStateHandler.test.ts classification;
* whether it is excluded by tsconfig;
* whether its production imports are excluded;
* whether it emits compiled output;
* current pattern match and execution count;
* src/test/testPatterns.ts remained unchanged.

Do not register, unquarantine, rewrite, or delete anything.

R-G — Stage-scoped protection

Prove:

* package.json may change only in separately authorized VERSION/PACKAGE work;
* testPatterns.ts may change only through a proven exact TEST_REGISTRATION action;
* no blanket exception exists;
* no negative-state authority predicate exists;
* pre-existing dirty state remains visible.

R-H — Manifest and authority parity

Verify:

* manifest schema exists and validates;
* active Agents: exactly 3;
* active Skills: exactly 5;
* unclassified assets: 0;
* unowned machine stages: 0;
* authority conflicts: 0;
* Agent declarations do not exceed manifest authority;
* human terminal stages are explicitly human-owned;
* inactive assets and reasons are enumerated.

R-I — Self-certification prohibition

Using fixtures in the temporary mirror, attempt certification of the exact
22-path Framework change as the repository-defined independent reviewer.

Expected:

* BLOCKED;
* exit 2;
* SELF_CERTIFICATION;
* CERTIFIED_IN_IMPLEMENTATION_SESSION;
* REVIEWER_CERTIFIES_OWN_AUTHORITY;
* INDEPENDENCE_UNPROVEN_STOP_CODE;
* final stop code OWNER_DECISION_REQUIRED.

Prove this is machine-enforced across all 22 paths and is not only prose.

R-J — Governance CI

Verify:

* no executable continue-on-error, || true, or unconditional success exit;
* comments or documentation are not misclassified as executable weakening;
* BLOCKED, blocker, major, schema, registry, ownership, checkpoint, and
    unauthorized-change failures stop CI;
* capture → action → compare lifecycle works;
* unauthorized src/extension.ts mutation blocks;
* protected pre-dirty package.json mutation blocks.

All mutation exercises must occur only in the temporary mirror.

==================================================
5. VALIDATION AND KNOWN-FAILURE RECONCILIATION

Run through canonical repository execution routes:

* all governance tests;
* customization validator;
* registration validator;
* evidence and checkpoint validation;
* manifest/schema and authority validation;
* governance workflow validation;
* compile;
* compile:test;
* lint;
* Repair 12 canonical suite;
* canonical full unit suite with VS Code bootstrap;
* positive and negative snapshot lifecycle tests.

Report exact commands, execution routes, exit codes, and failure fingerprints.

Verify or disprove:

* governance tests: 207 passing, 0 failing;
* customization: blocker 0, major 0, minor 0, informational 8;
* all eight informational findings are ASSET_CLASSIFIED_INACTIVE;
* registration: enforcing findings 0, informational records 12;
* Repair 12: 21/21 passing;
* compile, compile:test, and lint: exit 0;
* full unit: 2242 passing, 5 pending, 2 failing;
* new functional regressions: 0;
* new security regressions: 0.

Counts alone are insufficient.

Reconcile these historical results:

* 2245 passing / 1 pending / 3 failing;
* 2246 passing / 1 pending / 2 failing;
* 2242 passing / 5 pending / 2 failing.

List all five current pending tests and explain why four moved from passing to
pending. Determine whether the difference comes from discovery, exclusion,
environment, bootstrap, stale compilation, or behavior change.

Any unexplained count or pending-state difference blocks Repair 13.

Known F1–F3:

F1:

* locate the exact test, failure name, path, assertion, and fingerprint;
* verify whether it is the unchanged missing .github/prompts/*.prompt.md
    contract;
* do not create an Agent or Prompt;
* do not weaken the test.

F2:

* prove it passes through valid instruction frontmatter;
* prove its assertion was not weakened, skipped, or reclassified.

F3:

* locate the exact test and fingerprint;
* enumerate the eleven tracked src/**/AGENT.md files;
* verify their combined current byte count, reported as 73,909;
* do not delete, migrate, or rewrite them.

PASS is allowed only if:

* F1 and F3 are the only full-suite failures;
* they are exact unchanged deferred contract failures;
* F2 genuinely passes;
* the five pending tests are completely reconciled;
* no new functional, security, High, or unreported governance defect exists.

==================================================
6. FINAL LIVE NON-MUTATION PROOF

Compare final live snapshot with the pre-review snapshot.

Required:

* repository content changed by review: 0 paths;
* staged files: 0;
* stash entries: 0;
* package.json unchanged;
* package version unchanged;
* package-lock.json absent;
* src/test/testPatterns.ts unchanged;
* tsconfig.json unchanged;
* Repair 12 paths unchanged;
* all eleven AGENT.md files unchanged;
* existing VSIX size and SHA-256 unchanged;
* QA workspace not accessed or modified;
* Repair 13 not started;
* no commit, push, tag, package, install, Preview, or Runtime QA.

Do not claim non-mutation solely from Git because the Framework is untracked.
Use independent OS hash comparison.

==================================================
7. DECISION RULE

Repair 13 may start only if:

* identity, execution, workspace, and independence gates pass;
* exactly one workspace root is open;
* live repository remains byte-for-byte unchanged;
* all 22 expected paths are present, bounded, inspected, and validated;
* no unauthorized or unexplained stabilization path exists;
* R-A through R-J independently pass;
* schema, registry, ownership, authority, self-review, and CI enforcement pass;
* SourceValidationStateHandler and all eleven orphan suites are accurately
    classified without mutation;
* Repair 12 remains 21/21;
* compile, compile:test, and lint pass;
* all full-suite count differences are reconciled;
* F1 and F3 alone remain exact known failures;
* F2 passes;
* zero new functional, security, High, or unreported governance regressions exist.

A PASS authorizes only local Repair 13 in a later fresh Generic Agent session.

It does not authorize:

* version 0.3.145;
* packaging;
* VSIX build or installation;
* Runtime QA;
* commit or push;
* Cloud rollout.

==================================================
8. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
INDEPENDENCE_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
WORKSPACE_ROOT_COUNT: 
WORKSPACE_ROOTS: 
WORKSPACE_TARGET_UNAMBIGUOUS: YES/NO
REPOSITORY_MUTATED_BY_REREVIEW: YES/NO

EXPECTED_22_PRESENT_COUNT: 
EXPECTED_22_MISSING_PATHS: 
EXPECTED_22_TRACKED_COUNT: 
EXPECTED_22_UNTRACKED_COUNT: 
EXPECTED_22_MANIFEST: <path, bytes, SHA-256, role, owner, result>
UNEXPECTED_STABILIZATION_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
HISTORICAL_15_MODIFIED_7_ADDED_ATTRIBUTION_PROVEN: YES/NO
HISTORICAL_ATTRIBUTION_EVIDENCE: 

R_A_CHECKPOINT_FIDELITY: PASS/FAIL
R_B_SHARED_BASELINE_CONTRACT: PASS/FAIL
R_C_THREE_STATE_MODEL: PASS/FAIL
R_D_GIT_ATTRIBUTION: PASS/FAIL
R_E_PROTECTED_PATH_COMPLETENESS: PASS/FAIL
R_F_REGISTRATION_ACCURACY: PASS/FAIL
R_G_STAGE_SCOPED_PROTECTION: PASS/FAIL
R_H_MANIFEST_AUTHORITY_PARITY: PASS/FAIL
R_I_SELF_CERTIFICATION_PROHIBITION: PASS/FAIL
R_J_GOVERNANCE_CI: PASS/FAIL

PROTECTED_PRE_DIRTY_COUNT: 
PROTECTED_PRE_DIRTY_39_RECONCILED: YES/NO
MANIFEST_SCHEMA_VALID: YES/NO
ACTIVE_AGENT_COUNT: 
ACTIVE_SKILL_COUNT: 
UNCLASSIFIED_ASSET_COUNT: 
UNOWNED_MACHINE_STAGE_COUNT: 
AUTHORITY_CONFLICT_COUNT: 
SELF_CERTIFICATION_NEGATIVE_TEST: 
CI_EXECUTABLE_CONTINUE_ON_ERROR_PRESENT: YES/NO

SOURCE_VALIDATION_REGISTRATION: 
SOURCE_VALIDATION_PATTERN_MATCH_COUNT: 
EXCLUDED_ORPHAN_SUITE_COUNT: 
FALSE_RECOMPILE_REMEDIATIONS: 

GOVERNANCE_TESTS: <pass/fail>
CUSTOMIZATION_FINDINGS:
<blocker/major/minor/informational plus complete list>
REGISTRATION_FINDINGS:
<enforcing/informational plus complete list>

COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_12_CANONICAL_PASS: YES/NO

FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_PENDING_TESTS: 
FULL_UNIT_FAILURES: 
HISTORICAL_FULL_UNIT_COUNTS_RECONCILED: YES/NO
HISTORICAL_COUNT_RECONCILIATION: 
F1_UNCHANGED_KNOWN_FAILURE: YES/NO
F2_GENUINELY_PASSING: YES/NO
F3_UNCHANGED_KNOWN_FAILURE: YES/NO
LEGACY_AGENT_MD_COUNT: 
LEGACY_AGENT_MD_TOTAL_BYTES: 
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 
UNRESOLVED_HIGH_OR_SECURITY_FINDINGS: 

PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_PRESENT: NO
TEST_PATTERNS_CHANGED: NO
TSCONFIG_CHANGED: NO
REPAIR_12_CONTENT_CHANGED: NO
LEGACY_AGENT_FILES_CHANGED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
REPAIR_13_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

REPAIR_13_MAY_START: YES/NO
READY_TO_BUMP_TO_0_3_145: NO
READY_TO_PACKAGE_OR_INSTALL: NO
READY_FOR_RUNTIME_QA: NO
READY_FOR_CLOUD_ROLLOUT: NO

End exactly with one:

PROCESS_FRAMEWORK_INDEPENDENT_REREVIEW_RESULT:
PASS_REPAIR_13_MAY_START_IN_FRESH_LOCAL_SESSION

PROCESS_FRAMEWORK_INDEPENDENT_REREVIEW_RESULT:
FAIL_FRAMEWORK_STABILIZATION

PROCESS_FRAMEWORK_INDEPENDENT_REREVIEW_RESULT:
FAIL_NEW_FUNCTIONAL_OR_SECURITY_REGRESSION

PROCESS_FRAMEWORK_INDEPENDENT_REREVIEW_RESULT:
FAIL_REREVIEW_MUTATED_LIVE_REPOSITORY

PROCESS_FRAMEWORK_INDEPENDENT_REREVIEW_RESULT:
BLOCKED_IDENTITY_OR_WORKTREE_DRIFT

PROCESS_FRAMEWORK_INDEPENDENT_REREVIEW_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT

PROCESS_FRAMEWORK_INDEPENDENT_REREVIEW_RESULT:
BLOCKED_INDEPENDENCE_OR_WORKSPACE_AMBIGUITY

Only the first terminal result permits Repair 13 to start. Every other result keeps
Repair 13 on hold.
