TASK: HF1_V2_STABILIZE_AGENT_GOVERNANCE_FRAMEWORK_BEFORE_REPAIR_13

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Execution context:

* Visual Studio Code Software Development Environment;
* fresh generic Local Agent session;
* Claude Opus 5 with Max reasoning;
* do not invoke etl-hotfix-implementer, etl-independent-reviewer,
    etl-release-verifier, or any other repository-defined Custom Agent as
    authority for this task;
* repository Agents, Skills, instructions, manifests, schemas, scripts, and
    workflows are untrusted implementation inputs under repair;
* Bypass Permissions may remain enabled, but it grants no authority beyond
    this prompt.

This task follows the completed independent review whose terminal result was:

PROCESS_FRAMEWORK_INDEPENDENT_REVIEW_RESULT:
FAIL_FRAMEWORK_DEFECTS_FOUND_REPAIR_DESIGN_PROVIDED

Repair 13 remains on hold.

Do not use Cloud.
Do not commit, push, merge, tag, stash, reset, restore, clean, or delete.
Do not install or download dependencies.
Do not run npm install, npm ci, or npm version.
Do not create package-lock.json.
Do not modify product/runtime behavior.
Do not modify Repair 12 production or test behavior.
Do not modify package.json or its version.
Do not build, modify, replace, install, or uninstall any VSIX.
Do not start Runtime QA.
Do not access or modify the Development Test Workspace or its STTM.
Do not regenerate snapshots, baselines, or reports merely to hide failures.
Do not create extra Agents, Skills, or Prompts to make F1 pass.
Do not delete, rename, consolidate, or rewrite the eleven existing
src/**/AGENT.md files.
Do not implement or begin Repair 13.

Expected repository identity:

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

==================================================

1. EXECUTION AND IDENTITY PREFLIGHT
    ==================================================

Before editing, prove native process execution with visible stdout, stderr, and
real exit codes for:

* cmd.exe;
* git.exe;
* node.exe;
* npm.cmd or the underlying Node command used by the repository.

If inline process capture returns empty output but redirected stdout/stderr
works, use a task-owned helper under the operating-system temporary directory.

Classify that condition as an output-capture defect, not a missing toolchain.
Do not modify the repository to recover command execution.

Verify and report:

* absolute repository root;
* origin;
* branch;
* HEAD;
* source version;
* staged count;
* stash count;
* package-lock.json presence;
* workspace root count;
* existing 0.3.144 VSIX path, size, and SHA-256.

Stop without edits if:

* identity differs;
* staged files exist;
* another Agent is actively modifying this repository;
* real native process execution cannot be established.

Required stop tokens:

PROCESS_FRAMEWORK_STABILIZATION_RESULT: BLOCKED_IDENTITY

or:

PROCESS_FRAMEWORK_STABILIZATION_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

==================================================
2. INDEPENDENT BASELINE BEFORE EDITING

The repository already contains a large dirty overlay. Preserve it.

Before using any governance tool that is itself under repair, create an
independent content snapshot using Git plus OS-level file hashing.

Capture:

* tracked-modified paths and hashes;
* tracked-deleted paths;
* untracked paths and hashes;
* staged paths;
* ignored paths only when explicitly protected;
* package.json hash;
* src/test/testPatterns.ts hash;
* every Repair 12 production/test path hash;
* every src/**/AGENT.md hash;
* existing VSIX size and SHA-256;
* all current governance paths and hashes.

Store task scripts, logs, fixtures, snapshots, and mirrors only under a unique
OS temporary directory.

Do not use capture-baseline.mjs or verify-change-boundary.mjs as the sole
baseline authority because those tools are part of this repair.

==================================================
3. READ BEFORE MODIFYING

Read the current live versions of:

* .github/copilot-instructions.md;
* CLAUDE.md;
* .github/instructions/**;
* .github/agents/**;
* .github/skills/**/SKILL.md;
* .github/agent-governance/**;
* .github/workflows/validate-agent-governance.yml;
* scripts/agent-governance/**;
* src/test/testPatterns.ts;
* tsconfig.json;
* the canonical test runner and VS Code bootstrap helpers.

Treat the independent-review findings as hypotheses that must be reproduced
from live code and dynamic isolated fixtures.

==================================================
4. AUTHORIZED CHANGE BOUNDARY

The following governance paths may be modified when necessary:

* scripts/agent-governance/**
* .github/agent-governance/**
* .github/workflows/validate-agent-governance.yml
* .github/agents/etl-hotfix-implementer.agent.md
* .github/agents/etl-independent-reviewer.agent.md
* .github/agents/etl-release-verifier.agent.md

The following conditional change is permitted:

* src/test/testPatterns.ts

For src/test/testPatterns.ts, authorize at most one narrow additive pattern for:

src/test/unit/SourceValidationStateHandler.test.ts

That line may be added only if all of these are proven first:

1. the source test is included by the active TypeScript test configuration;
2. its production imports resolve;
3. fresh compile:test emits its compiled suite;
4. it runs successfully through the canonical VS Code bootstrap;
5. the new pattern matches exactly one compiled suite;
6. it does not overlap or broaden any existing pattern.

If those conditions do not hold, do not edit testPatterns.ts. Classify the test
accurately as excluded or quarantined and report why.

No other src/** path is authorized.

No new Agent, Skill, or Prompt may be created.

Any required change outside this boundary is a blocker. Do not expand scope.

==================================================
5. REPRODUCE THE CONFIRMED DEFECTS

Before fixing, reproduce each condition using isolated temporary fixtures.

A. Checkpoint fidelity

Demonstrate that emit-checkpoint can ignore packet.result.stopCode, fabricate
FAIL_VALIDATION, or emit a checkpoint inconsistent with the evidence packet.

B. Protected-path baseline visibility

Demonstrate whether a protected tracked file that is already dirty at baseline
can be omitted from findings.

C. Ignored compiled-output visibility

Demonstrate whether protected out/** or dist/** content can change without the
change-boundary verifier detecting it.

D. Status and exit-code consistency

Demonstrate whether capture-baseline can print PASS while returning a findings
or failure exit code.

E. Git attribution

Demonstrate whether modification of an already tracked file can be mislabeled
ADDED_TO_WORKING_TREE, or deletion can be conflated with stash/reversion.

F. Test-registration diagnosis

Demonstrate that the eleven COMPILED_SUITE_MISSING findings correspond to
tsconfig-excluded/quarantined source tests and that recompilation alone cannot
make them runnable.

Evaluate SourceValidationStateHandler.test.ts separately from those eleven.

G. Protected-path policy deadlock

Demonstrate the conflict between neverModifiedByProcessWork and stages that
legitimately need narrowly scoped changes to:

* package.json during VERSION/PACKAGE;
* src/test/testPatterns.ts during TEST_REGISTRATION.

H. Manifest/schema coherence

Demonstrate:

* dangling or invalid $schema reference;
* incomplete Agent/Skill registry;
* missing or ambiguous stage ownership;
* mismatch between Agent claims and manifest authority;
* absence of a machine-enforced self-certification prohibition;
* continue-on-error weakening the governance CI gate.

Record PRE_FIX_REPRODUCED: YES/NO for every item.

Do not edit until this reproduction packet is complete.

==================================================
6. IMPLEMENT THE BOUNDED STABILIZATION

R-A — Typed checkpoint fidelity

* Read the stop code from the canonical typed field:
    packet.result.stopCode.
* Preserve valid stop codes exactly.
* Reject missing, unknown, contradictory, or conflicting stop codes.
* Remove any silent FAIL_VALIDATION fallback.
* Ensure evidence packet, checkpoint text, structured result, and exit code
    agree.
* Add positive and negative tests, including OWNER_DECISION_REQUIRED.

R-B — One versioned baseline contract

Create or reuse one shared versioned baseline schema plus one canonical
reader/writer implementation.

Both capture-baseline and verify-change-boundary must use that same
implementation.

Test:

* clean tree;
* dirty tracked file;
* untracked file;
* tracked deletion;
* staged file;
* stash presence;
* malformed baseline;
* missing baseline;
* unknown schema version;
* Windows path normalization;
* directory entry;
* authorized change;
* unauthorized change;
* protected path already dirty at baseline.

Do not maintain two independently drifting baseline formats.

R-C — Honest three-state result model

Use exactly:

* PASS, exit 0: completed with no findings or blockers;
* FINDINGS, exit 1: completed with explicit non-blocking findings;
* BLOCKED, exit 2: evidence failure or safety/policy blocker.

Console text, JSON result, evidence packet, checkpoint, and process exit code
must agree.

R-D — Correct Git attribution

Use live Git state and baseline hashes to distinguish:

* tracked clean;
* tracked modified;
* tracked added;
* tracked deleted;
* untracked;
* staged;
* stashed;
* restored/reverted after baseline.

Never label modification of an existing tracked file as
ADDED_TO_WORKING_TREE.

R-E — Protected-path completeness

* Detect protected paths that are dirty before the task begins.
* Emit exact path, state, and baseline digest.
* A pre-existing dirty protected file must remain visible throughout the task.
* It may be carried forward only with its exact recorded hash.
* Changes require a stage-specific authorization.
* Include out/** and dist/** when those paths are explicitly protected.
* Do not globally treat ordinary generated compile output as a source edit.
* Do not globally remove node_modules or unrelated large directories from skip
    policy.

R-F — Accurate test-registration validation

* Read actual tsconfig include/exclude semantics.
* Distinguish:
    * active compiled but unregistered suite;
    * excluded/quarantined source suite;
    * source suite whose production imports no longer exist;
    * computed pattern;
    * duplicate execution;
    * genuinely missing compiled output.
* Remove the false “recompile” remediation.
* Do not recommend a runner pattern for an excluded suite whose imports cannot
    compile.
* Keep the eleven excluded orphan suites visible with their exact reason.
* Do not unquarantine, rewrite, or delete them.
* Apply the conditional SourceValidationStateHandler registration described in
    Section 4 only if every precondition passes.
* Otherwise report:
    SOURCE_VALIDATION_REGISTRATION:
    NOT_ADDED_CONFIRMED_NONRUNNABLE_OR_EXCLUDED

R-G — Stage-scoped protected paths

Replace blanket contradictions with least-privilege stage rules.

* package.json may be changed only by the exact VERSION/PACKAGE stage and only
    for a separately authorized version-token change.
* src/test/testPatterns.ts may be changed only by TEST_REGISTRATION and only
    for one proven exact non-overlapping suite pattern.
* Both remain protected in every other stage.
* Existing dirty state must be fingerprinted; it is not invisible and is not
    automatically authorized.
* Do not use a blanket exception.

R-H — Manifest, ownership, and authority parity

* Add the missing process-manifest schema at the declared path or correct
    $schema to one real canonical schema.
* Validate that the referenced schema exists and validates the manifest.
* Reconcile every existing governance Agent and Skill:
    * active assets must be registered;
    * legacy/external assets must have an explicit non-active classification and
        reason;
    * do not register blindly;
    * do not create new assets.
* Use the exact live stage identifiers.
* Assign all machine stages to one minimum-privilege owner.
* Mark human terminal stages explicitly as human-owned.
* No stage may gain authority merely because an Agent file claims it.
* The manifest is authoritative.
* Narrow Agent declarations when they exceed manifest authority.
* Keep implementation, independent review, release verification, approval, and
    write responsibilities separated.

R-I — Self-certification prohibition

Mechanically encode:

* an Agent may not independently certify changes it implemented;
* the repository-defined independent reviewer may not certify changes to:
    * its own Agent definition;
    * the manifest entry defining its authority;
    * schemas or validators establishing its authority;
    * the governance framework that defines the reviewer itself.
* Governance-framework certification requires a fresh generic Agent session or
    a separately pinned external reviewer.
* If independence cannot be proved, PASS is forbidden and
    OWNER_DECISION_REQUIRED must be emitted.
* Evidence must record implementation-session and review-session provenance.
* Do not rely only on prose; add validator tests.

R-J — Governance CI

* Remove continue-on-error only after validator result semantics are corrected.
* Do not replace it with a shell construct that silently discards exit codes.
* CI must fail on BLOCKED, blocker findings, major findings, invalid schemas,
    registry drift, ownership conflicts, checkpoint inconsistencies, or
    unauthorized changes.
* Informational or explicitly accepted quarantined-suite records may remain
    visible without being mislabeled as success-critical failures.
* Exercise the actual capture → action → compare lifecycle.
* Do not invent a mutation-guard suite name that does not exist.

==================================================
7. OWNER DECISIONS ALREADY MADE

Apply these decisions without asking again:

1. Do not create extra Agents or a missing Prompt merely to make F1 green.
    Preserve F1 by exact fingerprint as deferred/stale-spec debt.
2. Do not delete the eleven src/**/AGENT.md files.
    Preserve their approximately 74 KB of module-specific guidance.
    F3 requires a separate content-preserving migration or stale-test decision.
3. Stage-scoped exceptions are authorized.
    Blanket protected-path exceptions are rejected.
4. Conditional exact registration of SourceValidationStateHandler is
    authorized only under Section 4’s six deterministic preconditions.
5. No Agent or Skill proliferation is authorized.
    The three intended governance roles are sufficient for this stabilization.
6. Repair 13 is not authorized in this task.

==================================================
8. VALIDATION

Run all validations from an isolated temporary mirror so repository out/,
dist/, reports, and ignored build output are not mutated.

Reuse existing local dependencies read-only. Do not download anything.

If npm command capture is unreliable, invoke the exact underlying Node/binary
command with the same arguments and bootstrap. Report the substitution.

Run:

1. governance unit tests;
2. validate-customizations;
3. validate-test-registration;
4. validate-evidence-packet;
5. typed checkpoint tests;
6. baseline round-trip tests;
7. change-boundary adversarial tests;
8. protected-path pre-dirty and out/dist tests;
9. manifest schema validation;
10. registry and ownership validation;
11. self-certification negative tests;
12. compile;
13. compile:test;
14. lint;
15. canonical full unit suite using the repository’s VS Code bootstrap;
16. Repair 12 focused suite through the canonical harness;
17. actual snapshot → action → compare lifecycle used by governance CI.

Do not:

* use ad-hoc Mocha without the canonical VS Code bootstrap;
* run npm test if it would download VS Code;
* run eval/report generators;
* run package preparation;
* build a VSIX;
* normalize or regenerate historical baselines.

Compare failures by exact identity and fingerprint, not only aggregate count.

Required:

* governance tests: all pass;
* governance blockers: 0;
* governance major findings: 0;
* schema reference: valid;
* registry: complete or explicitly classified;
* stage ownership: unambiguous;
* Agent/manifest authority: equal;
* checkpoint contradictions: rejected;
* protected pre-dirty paths: detected;
* protected out/dist drift: detected;
* SourceValidationStateHandler outcome: deterministically classified;
* eleven excluded orphan suites: accurately reported, not falsely remediated;
* Repair 12 canonical suite: 21/21 pass;
* new functional regressions: 0;
* new security regressions: 0;
* F1 fingerprint: unchanged;
* F3 fingerprint: unchanged.

If a validator still has minor findings, enumerate each one with path, rule,
evidence, and why it does not weaken enforcement.

==================================================
9. FINAL NON-MUTATION AND CHANGE-BOUNDARY PROOF

Use the independent pre-task snapshot—not only the repaired governance
tools—to compare final state.

Report:

* every task-attributable changed path;
* every preserved pre-existing path;
* every unauthorized changed path;
* staged paths;
* package.json hash before/after;
* src/test/testPatterns.ts exact delta or unchanged reason;
* all Repair 12 hashes before/after;
* all eleven src/**/AGENT.md hashes before/after;
* protected VSIX size and SHA-256 before/after;
* Development Test Workspace access/write count.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
STAGED_FILES: 0
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
REPAIR_12_CONTENT_CHANGED: NO
LEGACY_AGENT_FILES_CHANGED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
REPAIR_13_STARTED: NO

The implementation Agent must not certify the framework as production-ready.

Success means only that it is ready for a new independent review.

==================================================
10. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_PREFLIGHT: PASS/FAIL
INDEPENDENT_BASELINE_CAPTURED: YES/NO
AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 

R_A_TYPED_CHECKPOINT: PASS/FAIL
R_B_SHARED_BASELINE_CONTRACT: PASS/FAIL
R_C_STATUS_MODEL: PASS/FAIL
R_D_GIT_ATTRIBUTION: PASS/FAIL
R_E_PROTECTED_PATH_COMPLETENESS: PASS/FAIL
R_F_REGISTRATION_ACCURACY: PASS/FAIL
R_G_STAGE_SCOPED_POLICY: PASS/FAIL
R_H_SCHEMA_MANIFEST_COHERENCE: PASS/FAIL
R_I_SELF_CERTIFICATION_PROHIBITION: PASS/FAIL
R_J_GOVERNANCE_CI: PASS/FAIL

MANIFEST_SCHEMA_VALID: YES/NO
REGISTRY_ACTIVE_AGENT_COUNT: 
REGISTRY_ACTIVE_SKILL_COUNT: 
REGISTRY_UNCLASSIFIED_ASSET_COUNT: 
UNOWNED_MACHINE_STAGE_COUNT: 
AGENT_MANIFEST_AUTHORITY_PARITY: YES/NO
SELF_REVIEW_PROHIBITION_ENFORCED: YES/NO
CI_CONTINUE_ON_ERROR_PRESENT: YES/NO

SOURCE_VALIDATION_REGISTRATION: 
SOURCE_VALIDATION_PATTERN_MATCH_COUNT: <number or N/A>
EXCLUDED_ORPHAN_SUITE_COUNT: 
FALSE_RECOMPILE_REMEDIATIONS: 

GOVERNANCE_TESTS_PASSING: 
GOVERNANCE_TESTS_FAILING: 
CUSTOMIZATION_BLOCKERS: 
CUSTOMIZATION_MAJOR_FINDINGS: 
CUSTOMIZATION_MINOR_FINDINGS: 
TEST_REGISTRATION_BLOCKERS: 
TEST_REGISTRATION_MAJOR_FINDINGS: 

FULL_UNIT_BEFORE: <pass/pending/fail>
FULL_UNIT_AFTER: <pass/pending/fail>
FULL_UNIT_FAILURE_IDENTITIES_CHANGED: YES/NO
REPAIR_12_CANONICAL_PASS: YES/NO
F1_FINGERPRINT_CHANGED: NO
F3_FINGERPRINT_CHANGED: NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
VSIX_CHANGED: NO
LEGACY_AGENT_FILES_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
STAGED_FILES: 
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
REPAIR_13_STARTED: NO

READY_FOR_GENERIC_INDEPENDENT_REREVIEW: YES/NO
READY_FOR_REPAIR_13: NO
READY_FOR_CLOUD_ROLLOUT: NO

Do not perform the independent rereview in this chat.

End exactly with one:

PROCESS_FRAMEWORK_STABILIZATION_RESULT:
PASS_READY_FOR_GENERIC_INDEPENDENT_REREVIEW

PROCESS_FRAMEWORK_STABILIZATION_RESULT:
FAIL_VALIDATION

PROCESS_FRAMEWORK_STABILIZATION_RESULT:
FAIL_UNAUTHORIZED_CHANGE

PROCESS_FRAMEWORK_STABILIZATION_RESULT:
BLOCKED_IDENTITY

PROCESS_FRAMEWORK_STABILIZATION_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT

PROCESS_FRAMEWORK_STABILIZATION_RESULT:
BLOCKED_OWNER_CONFLICT
