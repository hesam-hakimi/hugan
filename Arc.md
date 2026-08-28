TASK: HF1_V2_REPAIR_PACKAGE_LIFECYCLE_GOVERNANCE_OWNER_DECISIONS

Perform a narrowly bounded owner-authorized repair of the package lifecycle
governance framework.

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use:

* a fresh generic Local Agent session;
* Claude Opus 5 with Max reasoning;
* no repository-defined Custom Agent as authority;
* no consumer Agent such as ETL Orchestrator or ETL Verifier;
* no Cloud execution.

This task implements two explicit repository-owner decisions arising from the
separate exact verification of version 0.3.146.

The exact package verification ended with:

EXACT_PACKAGE_VERIFICATION_0_3_146_RESULT:
PASS_ARTIFACT_VALID_BLOCKED_GOVERNANCE_EXCEPTION

Verified package facts:

* artifact:
    databricks-etl-copilot-0.3.146.vsix
* artifact integrity: PASS;
* declared identity: correct;
* expected entries: 66/66;
* duplicate/traversal/unreadable entries: 0;
* consumer Agent resources: 6/6 correct;
* source-to-package provenance: 66/66;
* unexpected entries/differences: 0/0;
* repository and artifact remained unchanged;
* the artifact itself is sound.

The two confirmed governance findings are:

1. VSIX_PROTECTED_PATH_NO_EXCEPTION
    **/*.vsix is protected by neverModifiedByProcessWork, but
    VERSION_AND_PACKAGE has no narrowly scoped protected-path exception permitting
    creation of its required new version-distinguishable VSIX.
2. CERTIFYING_ROLE_AMBIGUITY
    etl-release-verifier currently owns or performs both VERSION_AND_PACKAGE and
    EXACT_PACKAGE_VERIFICATION. When the same actor produced and certified the
    artifact, implementedBy == emittedBy and machine independence checks correctly
    report SELF_CERTIFICATION.

This task repairs only those two governance defects.

Do not install or uninstall the extension.
Do not rebuild, replace, rename, or modify any VSIX.
Do not change package.json or version 0.3.146.
Do not access the Development Test Workspace.
Do not start Runtime QA.
Do not run Preview or Write.
Do not commit, push, stage, stash, tag, reset, restore, or clean.
Do not create package-lock.json.
Do not download or install dependencies.
Do not modify product/runtime source.
Do not modify consumer Agent resources.
Do not implement unrelated governance improvements.
Do not certify this governance repair in this session.

==================================================

1. IDENTITY AND EXECUTION GATES
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
0.3.146

Required:

* exactly one effective repository target;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrent Agent mutation;
* target 0.3.146 VSIX present;
* all eleven current VSIX artifacts unchanged at entry.

If inline process capture returns empty output, use file-redirected execution
through a task-owned helper under the OS temporary directory.

Require real executable identity, stdout, stderr, and exit codes.

Do not modify the repository to recover process execution.

Stop without edits on identity mismatch, concurrent mutation, staged content,
workspace ambiguity, or unproven command execution.

==================================================
2. INDEPENDENT PRE-EDIT BASELINE

Before editing, capture:

* complete working-tree path inventory;
* tracked and non-ignored untracked content;
* protected and ignored governance/VSIX paths;
* per-file size and SHA-256;
* staged and stash state;
* package.json hash;
* all VSIX paths, sizes, and SHA-256 values;
* all governance manifest/schema/validator/test hashes;
* all product/runtime and consumer-Agent resource hashes.

Use both:

1. the repository governance baseline mechanism; and
2. an independent OS-level filesystem hash snapshot.

Store temporary scripts, reports, snapshots, and outputs only under a unique OS
temporary directory.

==================================================
3. AUTHORIZED CHANGE BOUNDARY

Only these paths are authorized for modification:

1. .github/agent-governance/process-manifest.json
2. scripts/agent-governance/tests/change-boundary-adversarial.test.mjs
3. scripts/agent-governance/tests/manifest-registry.test.mjs

No other path is authorized.

Before editing, confirm that the existing manifest schema already supports the
required rules.

Do not modify the schema merely for convenience.

If the two repairs cannot be implemented correctly within these three paths,
stop without expanding the boundary and return:

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_REQUIRED_CHANGE_OUTSIDE_BOUNDARY

==================================================
4. OWNER DECISION A — NARROW VSIX CREATION EXCEPTION

Modify the process manifest so VERSION_AND_PACKAGE can create exactly one new,
version-distinguishable VSIX required by that stage.

The rule must:

* apply only during VERSION_AND_PACKAGE;
* require a separately authorized version bump;
* derive the permitted filename from the current package identity and exact
    package version;
* permit only the CREATED state;
* permit exactly one new artifact;
* require the expected filename shape:
    databricks-etl-copilot-.vsix;
* require the artifact version to equal package.json version;
* keep all pre-existing VSIX files protected by their baseline digests;
* reject modification of a pre-existing VSIX;
* reject replacement of a pre-existing VSIX;
* reject deletion or renaming of any VSIX;
* reject creation of additional VSIX files;
* reject an unversioned, incorrectly versioned, or ambiguous artifact;
* remain forbidden during all other stages.

Do not introduce a blanket writable **/*.vsix exception.

If the existing exception format cannot express every semantic restriction
directly, use the narrowest existing manifest rule and ensure the validator tests
prove all remaining constraints fail closed.

Add adversarial tests for:

* one exact new VSIX during VERSION_AND_PACKAGE: allowed;
* same action without an authorized version bump: blocked;
* wrong version in filename: blocked;
* two new VSIX artifacts: blocked;
* modification of a pre-existing VSIX: blocked;
* replacement of a pre-existing VSIX: blocked;
* deletion of a pre-existing VSIX: blocked;
* VSIX creation in another stage: blocked;
* broad **/*.vsix authorization: rejected.

==================================================
5. OWNER DECISION B — PRODUCER/CERTIFIER SEPARATION

Mechanically enforce separation between:

* VERSION_AND_PACKAGE; and
* EXACT_PACKAGE_VERIFICATION.

Required policy:

* an artifact producer may not certify the same artifact;
* implementedBy == emittedBy must fail closed;
* different session IDs alone are not sufficient when the certifying actor is the
    same producing identity;
* EXACT_PACKAGE_VERIFICATION must use an actor independent of the producer;
* a fresh generic review session or separately pinned external reviewer may
    perform exact verification when independence is proven;
* no Agent gains broader write, package, install, approval, Preview, or Runtime QA
    authority;
* do not create a new Agent;
* do not weaken the existing self-certification guard;
* do not accept prose-only separation;
* independence must be machine-enforced through the manifest and its validator
    tests.

Preserve the existing three source-governance Agents and five Skills.

A role may participate in either production or verification according to the
manifest, but the same actor must never perform both for the same artifact.

Add positive and negative tests covering:

* same actor and same session: blocked;
* same actor and different session: blocked;
* different actor but unproven provenance: blocked;
* producer plus fresh generic independent verifier with complete provenance:
    allowed;
* producer plus pinned external independent verifier with complete provenance:
    allowed;
* reviewer attempting to certify changes to its own authority: blocked;
* missing implementation session identity: blocked;
* missing review session identity: blocked;
* mismatched artifact digest: blocked;
* exact artifact digest and proven independent actor: allowed.

Do not retroactively certify the current 0.3.146 artifact in this implementation
session.

==================================================
6. VALIDATION

Run all write-producing validation only in a task-owned temporary mirror.

Run:

* governance unit tests;
* change-boundary adversarial tests;
* manifest registry and ownership tests;
* manifest schema validation;
* self-certification negative tests;
* checkpoint fidelity tests;
* baseline contract tests;
* workflow validation;
* customization validation;
* test-registration validation;
* compile;
* compile:test;
* lint.

Also run fixture-based lifecycle tests for:

1. authorized version bump plus exact new VSIX creation;
2. exact package verification by the producer — must block;
3. exact package verification by the same role in a new session — must block;
4. exact package verification by a proven fresh generic reviewer — must pass;
5. modification of any pre-existing VSIX — must block;
6. creation of a second VSIX — must block;
7. artifact digest mismatch — must block.

Do not run installation or Runtime QA.

Required:

* all governance tests pass;
* schema valid;
* unowned machine stages: 0;
* authority conflicts: 0;
* duplicate active authority: 0;
* VSIX creation exception is stage-scoped and create-only;
* producer/certifier separation is machine-enforced;
* no new blocker, major, functional, or security regression.

==================================================
7. FINAL CHANGE-BOUNDARY PROOF

Compare the final live repository with the independent pre-edit snapshot.

Required:

* only the three authorized governance paths changed;
* package.json unchanged;
* version remains 0.3.146;
* target 0.3.146 VSIX byte-identical;
* all pre-existing VSIX files byte-identical;
* product/runtime source unchanged;
* consumer Agent resources unchanged;
* QA workspace untouched;
* staged files: 0;
* stash entries: 0;
* no install/uninstall;
* no Runtime QA;
* no commit/push/tag;
* no package-lock.json.

The implementation session must not certify its own governance changes.

Success authorizes only a fresh independent read-only review combining:

* verification of this governance repair; and
* exact re-verification of the already-built 0.3.146 VSIX.

It does not authorize installation or Runtime QA.

==================================================
8. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
INDEPENDENT_BASELINE_CAPTURED: YES/NO

AUTHORIZED_CHANGED_PATHS:
UNAUTHORIZED_CHANGED_PATHS:

VSIX_CREATE_EXCEPTION_PRESENT: YES/NO
VSIX_EXCEPTION_STAGE:
VSIX_EXCEPTION_ALLOWED_STATE:
VSIX_EXCEPTION_EXACT_VERSION_REQUIRED: YES/NO
VSIX_EXCEPTION_EXACTLY_ONE_REQUIRED: YES/NO
PREEXISTING_VSIX_MODIFICATION_BLOCKED: YES/NO
PREEXISTING_VSIX_DELETION_BLOCKED: YES/NO
SECOND_NEW_VSIX_BLOCKED: YES/NO
OTHER_STAGE_VSIX_CREATION_BLOCKED: YES/NO
BLANKET_VSIX_WRITE_EXCEPTION_PRESENT: YES/NO

PRODUCER_CERTIFIER_SEPARATION_ENFORCED: YES/NO
SAME_ACTOR_SAME_SESSION_BLOCKED: YES/NO
SAME_ACTOR_DIFFERENT_SESSION_BLOCKED: YES/NO
UNPROVEN_PROVENANCE_BLOCKED: YES/NO
FRESH_GENERIC_VERIFIER_ALLOWED_WHEN_PROVEN: YES/NO
PINNED_EXTERNAL_VERIFIER_ALLOWED_WHEN_PROVEN: YES/NO
OWN_AUTHORITY_CERTIFICATION_BLOCKED: YES/NO
ARTIFACT_DIGEST_MISMATCH_BLOCKED: YES/NO

MANIFEST_SCHEMA_VALID: YES/NO
ACTIVE_AGENT_COUNT:
ACTIVE_SKILL_COUNT:
UNOWNED_MACHINE_STAGE_COUNT:
AUTHORITY_CONFLICT_COUNT:
DUPLICATE_ACTIVE_AUTHORITY_COUNT:

GOVERNANCE_TESTS_PASSING:
GOVERNANCE_TESTS_FAILING:
CHANGE_BOUNDARY_TESTS: PASS/FAIL
MANIFEST_REGISTRY_TESTS: PASS/FAIL
SELF_CERTIFICATION_TESTS: PASS/FAIL
CHECKPOINT_TESTS: PASS/FAIL
BASELINE_CONTRACT_TESTS: PASS/FAIL
WORKFLOW_VALIDATION: PASS/FAIL
CUSTOMIZATION_VALIDATION: PASS/FAIL
TEST_REGISTRATION_VALIDATION: PASS/FAIL
COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
NEW_FUNCTIONAL_REGRESSIONS:
NEW_SECURITY_REGRESSIONS:

PACKAGE_VERSION_AFTER: 0.3.146
PACKAGE_JSON_CHANGED: NO
TARGET_0_3_146_VSIX_CHANGED: NO
PREEXISTING_VSIX_CHANGED_COUNT:
PRODUCT_SOURCE_CHANGED: NO
CONSUMER_AGENT_RESOURCES_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
STAGED_FILES:
STASH_ENTRIES:
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

SELF_CERTIFICATION_PERFORMED: NO
READY_FOR_FRESH_GENERIC_COMBINED_INDEPENDENT_REVIEW: YES/NO
READY_FOR_LOCAL_INSTALL_AND_ACTIVATION: NO
READY_FOR_RUNTIME_QA: NO

End exactly with one:

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
PASS_READY_FOR_FRESH_GENERIC_COMBINED_INDEPENDENT_REVIEW

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
FAIL_VALIDATION

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
FAIL_UNAUTHORIZED_CHANGE

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_REQUIRED_CHANGE_OUTSIDE_BOUNDARY

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_IDENTITY_OR_EXECUTION

Do not perform the independent review in this session.
