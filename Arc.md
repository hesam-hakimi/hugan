TASK: HF1_V2_REPAIR_PACKAGE_LIFECYCLE_GOVERNANCE_OWNER_DECISIONS_V2

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use a fresh generic Local Agent session.

Do not invoke any repository-defined lifecycle Agent or consumer ETL Agent as the
authority for this task.

This is a bounded governance implementation authorized by the repository owner.
It repairs two confirmed governance defects:

1. VERSION_AND_PACKAGE is required to create one new versioned VSIX, but the
    protected-path system currently has no create-only, stage-scoped exception.
2. etl-release-verifier currently participates in both artifact production and
    certification, allowing producer/certifier identity ambiguity.

The preceding attempt ended correctly with:

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_REQUIRED_CHANGE_OUTSIDE_BOUNDARY

It made zero repository changes and proved that two additional implementation
paths are required.

Do not install the extension.
Do not start Runtime QA.
Do not rebuild or modify the 0.3.146 VSIX.
Do not change package.json or its version.
Do not create another VSIX.
Do not modify product source or tests.
Do not commit, push, stage, stash, reset, restore, clean, merge, or tag.
Do not perform independent certification in this session.

==================================================

1. EXPECTED IDENTITY
    ==================================================

Required:

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

Required state:

* exactly one effective repository target;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrent Agent mutation;
* existing VSIX files preserved byte-for-byte;
* databricks-etl-copilot-0.3.146.vsix present and unchanged.

Prove native execution with visible output and real exit codes.

If inline capture is empty, use task-owned file-redirection under the operating
system temporary directory. Do not modify the repository to repair execution.

Stop without edits on identity mismatch, concurrent mutation, staged content, or
unproven execution.

==================================================
2. INDEPENDENT PRE-EDIT BASELINE

Before editing, capture both:

1. the canonical governance baseline;
2. an independent OS-level path, size, SHA-256, and mtime snapshot.

The independent snapshot must include tracked, untracked, ignored protected, and
VSIX paths.

Record exact pre-edit hashes for all authorized files and all existing VSIX
artifacts.

Do not rely solely on git ls-files, because *.vsix and other governance assets
may be ignored or untracked.

==================================================
3. AUTHORIZED CHANGE BOUNDARY

Only these five files may be modified:

1. .github/agent-governance/process-manifest.json
2. .github/agent-governance/schemas/process-manifest.schema.json
3. scripts/agent-governance/verify-change-boundary.mjs
4. scripts/agent-governance/tests/change-boundary-adversarial.test.mjs
5. scripts/agent-governance/tests/manifest-registry.test.mjs

No other path is authorized.

If a correct implementation requires any sixth path, stop without partial edits:

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_REQUIRED_CHANGE_OUTSIDE_BOUNDARY

==================================================
4. OWNER DECISION A — CREATE-ONLY VSIX EXCEPTION

Implement a machine-enforced protected-path exception that allows the
VERSION_AND_PACKAGE stage to create exactly one new canonical VSIX for the exact
package version being produced.

The manifest and schema must be capable of expressing all of these constraints:

* applicable stage: VERSION_AND_PACKAGE only;
* applicable protected path: the canonical root VSIX artifact only;
* allowed change kind: CREATED only;
* required explicit authorization token;
* maximum newly created artifacts: exactly 1;
* exact filename derived from the canonical extension/package identity and the
    authorized target version;
* artifact version must equal the authorized package version;
* artifact identity must equal the canonical extension identity;
* an existing artifact may not be modified, replaced, deleted, or renamed;
* an artifact for another version may not be created;
* a second new VSIX must be rejected;
* the exception grants no install, activation, Runtime QA, approval, commit, push,
    or publication authority.

Do not implement this by excluding VSIX files from protection.

Do not weaken the global **/*.vsix protected-path rule.

Do not authorize CONTENT_CHANGED, DELETED, RENAMED, or replacement.

Do not rely on ordinary working-tree enumeration because ignored VSIX files may
not appear there.

Update verify-change-boundary.mjs so the protected-path comparison branch:

* evaluates the actual change kind;
* enforces the exception’s allowed change kinds;
* walks protected VSIX paths independently of Git tracking/ignore state;
* derives pre/post artifact counts;
* identifies the exact newly created artifact;
* validates filename, package version, extension identity, and authorization;
* fails closed when required identity evidence is missing or ambiguous;
* emits deterministic structured findings and an appropriate exit code.

The verifier must not treat the mere existence of an exception as blanket
permission.

==================================================
5. REQUIRED DECISION-A TEST MATRIX

Add adversarial tests proving:

1. no exception → new VSIX creation is BLOCKED;
2. wrong stage → BLOCKED;
3. missing authorization token → BLOCKED;
4. wrong authorization token → BLOCKED;
5. exactly one correctly named new VSIX for the authorized version → PASS;
6. correct artifact created under another stage → BLOCKED;
7. wrong version in filename → BLOCKED;
8. wrong extension/artifact identity → BLOCKED;
9. two new VSIX artifacts → BLOCKED;
10. modification of a pre-existing VSIX → BLOCKED;
11. replacement of a pre-existing VSIX → BLOCKED;
12. deletion of a pre-existing VSIX → BLOCKED;
13. rename of a pre-existing VSIX → BLOCKED;
14. creation plus modification of an existing VSIX → BLOCKED;
15. creation of a noncanonical VSIX path → BLOCKED;
16. absent or malformed artifact identity evidence → BLOCKED;
17. the existing VERSION_BUMP_AUTHORIZED package.json behavior remains unchanged;
18. all unrelated protected paths remain fail-closed.

Include at least one negative control that removes the new allowed-change-kind
check and proves the tests fail. Restore the implementation afterward and verify
its hash/content.

Tests must exercise real verifier behavior, not merely inspect manifest text.

==================================================
6. OWNER DECISION B — PRODUCER/CERTIFIER SEPARATION

Mechanically enforce that an Agent or actor that produced a package artifact
cannot independently certify that same artifact.

The following must be true:

* a different session ID alone is insufficient;
* the same Agent identity in another session remains the same actor for
    certification purposes;
* etl-release-verifier may not certify an artifact it produced;
* an Agent may not certify definitions, policies, manifests, schemas, validators,
    or artifact paths that define or govern its own certification authority;
* a fresh generic session or separately pinned external reviewer may certify only
    when complete producer and reviewer provenance proves distinct actor identity;
* missing or ambiguous producer provenance fails closed;
* no repository-defined Agent gains new authority;
* no new Agent is created;
* no existing role gains install, write, approval, deployment, or Runtime QA
    authority.

Use the existing self-certification model, governanceAuthorityPaths,
mayNotCertify.paths, provenance fields, and runtime enforcement architecture.
Extend those mechanisms narrowly rather than creating a parallel policy system.

The exact package-verification stage must remain independently executable, but a
producer must be rejected as its certifier.

Required negative findings must remain deterministic, including as applicable:

* SELF_CERTIFICATION;
* CERTIFIED_IN_IMPLEMENTATION_SESSION;
* REVIEWER_CERTIFIES_OWN_AUTHORITY;
* SELF_REVIEW_PROHIBITION_INCOMPLETE;
* INDEPENDENCE_UNPROVEN_STOP_CODE;
* OWNER_DECISION_REQUIRED.

==================================================
7. REQUIRED DECISION-B TEST MATRIX

Add tests proving:

1. same Agent and same session produces and certifies → BLOCKED;
2. same Agent with different session IDs → BLOCKED;
3. same repository-defined release-verifier in separate chats → BLOCKED;
4. missing producer identity → BLOCKED;
5. missing producer session provenance → BLOCKED;
6. malformed provenance → BLOCKED;
7. reviewer certifies a path governing its own authority → BLOCKED;
8. fresh generic reviewer with complete distinct provenance → eligible;
9. pinned external reviewer with complete distinct provenance → eligible;
10. different display name but same canonical actor identity → BLOCKED;
11. consumer ETL Agent cannot certify source-package governance;
12. certification eligibility grants no mutation or installation authority;
13. all existing governance self-certification tests continue to pass.

Do not encode trust solely from a user-facing actor name.

==================================================
8. VALIDATION

Run write-producing validation only in a task-owned byte-faithful temporary
mirror.

Run at minimum:

* governance unit tests;
* change-boundary adversarial tests;
* manifest registry tests;
* manifest/schema validation;
* customization validation;
* test-registration validation;
* workflow validation;
* evidence-packet and checkpoint validation;
* compile;
* compile:test;
* lint;
* canonical full unit suite;
* Repair 11 focused suite;
* Repair 12 focused suite;
* Repair 13 focused suite;
* Runtime-QA-support fixture suite;
* package asset byte-lock tests.

Expected known full-suite state:

* 2298 passing;
* 1 pending;
* 2 failing;
* F1: missing
    .github/prompts/deploy-v3-agent-tool-context-gap.prompt.md;
* F3: eleven existing src/**/AGENT.md files.

F1 and F3 must remain exact unchanged known failures.

Required:

* new functional regressions: 0;
* new security regressions: 0;
* new blocker/major/minor governance findings caused by this repair: 0;
* all new adversarial tests pass;
* existing VSIX artifacts remain byte-identical;
* package version remains 0.3.146.

==================================================
9. FINAL CHANGE-BOUNDARY PROOF

Compare final state against the independent pre-edit snapshot.

Required:

AUTHORIZED_CHANGED_PATHS:
exactly the subset of the five authorized files actually changed

UNAUTHORIZED_CHANGED_PATHS:
NONE

Also require:

* package.json unchanged;
* package version unchanged at 0.3.146;
* package-lock.json absent;
* product/runtime source unchanged;
* Repair 11/12/13 product behavior unchanged;
* consumer Agent tool sets unchanged;
* existing VSIX files unchanged;
* no new VSIX created;
* no extension installed or uninstalled;
* Runtime QA not started;
* QA workspace untouched;
* no Preview or Write;
* staged files: 0;
* stash entries: 0;
* no commit, push, or tag.

==================================================
10. HANDOFF — DO NOT SELF-CERTIFY

This implementation session must not independently certify its own governance
repair.

Success means only:

READY_FOR_FRESH_GENERIC_COMBINED_INDEPENDENT_REVIEW: YES

The next session must be a fresh Generic Agent and must combine:

1. independent read-only review of this five-file governance repair;
2. exact read-only re-verification of the existing 0.3.146 VSIX.

Do not perform that review in this chat.

==================================================
11. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
INDEPENDENT_BASELINE_CAPTURED: YES/NO
AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 

CREATE_ONLY_EXCEPTION_SCHEMA_PRESENT: YES/NO
PROTECTED_BRANCH_CHECKS_CHANGE_KIND: YES/NO
PROTECTED_BRANCH_DERIVES_ARTIFACT_COUNT: YES/NO
PROTECTED_BRANCH_DERIVES_EXACT_IDENTITY: YES/NO
IGNORED_VSIX_VISIBILITY_PROVEN: YES/NO

CORRECT_SINGLE_NEW_VSIX_ALLOWED: YES/NO
NO_TOKEN_BLOCKED: YES/NO
WRONG_STAGE_BLOCKED: YES/NO
WRONG_TOKEN_BLOCKED: YES/NO
WRONG_VERSION_BLOCKED: YES/NO
WRONG_IDENTITY_BLOCKED: YES/NO
TWO_NEW_ARTIFACTS_BLOCKED: YES/NO
PREEXISTING_VSIX_MODIFICATION_BLOCKED: YES/NO
PREEXISTING_VSIX_REPLACEMENT_BLOCKED: YES/NO
PREEXISTING_VSIX_DELETION_BLOCKED: YES/NO
PREEXISTING_VSIX_RENAME_BLOCKED: YES/NO

SAME_AGENT_SAME_SESSION_CERTIFICATION_BLOCKED: YES/NO
SAME_AGENT_DIFFERENT_SESSION_CERTIFICATION_BLOCKED: YES/NO
MISSING_PROVENANCE_FAILS_CLOSED: YES/NO
OWN_AUTHORITY_CERTIFICATION_BLOCKED: YES/NO
FRESH_GENERIC_REVIEWER_ELIGIBILITY_TEST: PASS/FAIL
PINNED_EXTERNAL_REVIEWER_ELIGIBILITY_TEST: PASS/FAIL
NEW_AGENT_CREATED: NO
AGENT_AUTHORITY_BROADENED: NO

GOVERNANCE_TESTS: <passing/failing>
COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_11_PASS: YES/NO
REPAIR_12_PASS: YES/NO
REPAIR_13_PASS: YES/NO
RUNTIME_QA_SUPPORT_FIXTURE_PASS: YES/NO
PACKAGE_ASSET_BYTE_LOCK_PASS: YES/NO

FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_FAILURES: 
F1_UNCHANGED: YES/NO
F3_UNCHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

PACKAGE_VERSION_CHANGED: NO
EXISTING_VSIX_CHANGED: NO
NEW_VSIX_CREATED: NO
QA_WORKSPACE_TOUCHED: NO
RUNTIME_QA_STARTED: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

READY_FOR_FRESH_GENERIC_COMBINED_INDEPENDENT_REVIEW: YES/NO
READY_FOR_LOCAL_INSTALL: NO
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
