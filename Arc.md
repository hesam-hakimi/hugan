TASK: HF1_V2_REPAIR_PACKAGE_LIFECYCLE_GOVERNANCE_OWNER_DECISIONS_V3

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use a fresh generic Local Agent session with Claude Opus 5 Max.

Do not select:

* etl-hotfix-implementer;
* etl-independent-reviewer;
* etl-release-verifier;
* any source-governance Custom Agent;
* ETL Orchestrator or any consumer Agent.

This is one atomic repository-owner-authorized governance repair.

The preceding attempt ended truthfully with:

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_REQUIRED_CHANGE_OUTSIDE_BOUNDARY

That attempt made zero repository changes and proved that the complete repair
requires exactly eight authorized paths rather than five.

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

Required initial state:

* exactly one effective repository target;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrent Agent mutation;
* databricks-etl-copilot-0.3.146.vsix present and unchanged;
* expected VSIX size: 1,262,112 bytes.

Prove visible stdout, stderr, executable identity, and real exit codes for:

* cmd.exe;
* git.exe;
* node.exe;
* npm.cmd or the exact underlying Node executable.

If inline capture returns empty output, use a task-owned file-redirection helper
under the operating-system temporary directory. Do not modify repository content
to repair process execution.

Stop without edits on identity mismatch, concurrent mutation, staged content,
workspace ambiguity, or unproven process execution.

==================================================
2. PRE-EDIT BASELINE

Before editing, capture two independent baselines:

1. the canonical governance baseline tool;
2. an OS-level full-content snapshot independent of Git tracking and ignore state.

Include:

* tracked, untracked, ignored-but-protected, and protected paths;
* all governance assets;
* all *.vsix files;
* package.json;
* package-lock.json presence;
* all Repair 11, 12, and 13 source/test paths;
* all consumer Agent catalog and generated-resource paths;
* HEAD, staged count, stash count;
* per-path size and SHA-256.

Store temporary scripts, logs, snapshots, mirrors, and fixtures only under a
unique OS temporary directory.

Do not rely only on git ls-files; the governance and VSIX assets include
untracked or ignored content.

==================================================
3. ATOMIC AUTHORIZED CHANGE BOUNDARY

Exactly these eight files may be modified:

1. .github/agent-governance/process-manifest.json
2. .github/agent-governance/schemas/process-manifest.schema.json
3. scripts/agent-governance/verify-change-boundary.mjs
4. scripts/agent-governance/tests/change-boundary-adversarial.test.mjs
5. scripts/agent-governance/tests/manifest-registry.test.mjs
6. scripts/agent-governance/emit-checkpoint.mjs
7. scripts/agent-governance/tests/checkpoint-fidelity.test.mjs
8. scripts/agent-governance/validate-customizations.mjs

No ninth path is authorized.

If a correct implementation genuinely requires another path:

* make no partial repair;
* do not weaken a validator;
* do not silently reinterpret the requirement;
* stop with:

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_ADDITIONAL_PATH_REQUIRED

Do not modify:

* package.json;
* package-lock.json;
* any existing or new VSIX;
* product source;
* Repair 11, 12, or 13 source/tests;
* consumer Agent catalog or rendered Agent resources;
* .claude/**;
* QA workspace content;
* testPatterns.ts;
* evaluation baselines;
* Git state.

==================================================
4. DECISION A — CREATE-ONLY VERSIONED VSIX EXCEPTION

Implement a narrow, machine-enforced exception for the VERSION_AND_PACKAGE
stage.

The exception must permit only:

* change kind: CREATED;
* artifact type: VSIX;
* exactly one new artifact;
* canonical filename derived from the declared extension identity and requested
    version;
* archive-declared extension ID equal to the manifest/package identity;
* archive-declared version equal to the requested version;
* an explicitly supplied authorization token;
* no pre-existing VSIX content change.

The exception must never permit:

* CONTENT_CHANGED;
* DELETED;
* replacement;
* overwrite;
* wrong version;
* wrong filename;
* wrong extension ID;
* two or more new VSIX files;
* reuse of an existing filename;
* arbitrary *.vsix creation;
* creation at another lifecycle stage;
* missing, malformed, mismatched, or replayed authorization;
* path traversal;
* case or separator ambiguity;
* an artifact outside the exact package destination.

The live comparator already derives a change kind such as:

* CREATED;
* CONTENT_CHANGED;
* DELETED.

Change-boundary authorization must consult that exact change kind.

Do not merely check whether a token exists.

Do not weaken the global **/*.vsix protected-path rule.

Add explicit versioned manifest/schema properties equivalent to:

* allowedChangeKinds: ["CREATED"];
* maxNewArtifacts: 1;
* exact artifact identity/filename derivation;
* the required authorization token or token class.

Use the repository’s existing schema conventions. Do not introduce an
unvalidated free-form property.

The protected-path walker must continue detecting VSIX files independently of Git
tracking and ignore state.

==================================================
5. DECISION A — REQUIRED TEST MATRIX

Add dynamic positive and negative tests proving:

1. exactly one correctly named new versioned VSIX with valid authorization:
    PASS;
2. same case without authorization:
    BLOCKED;
3. wrong filename:
    BLOCKED;
4. wrong version in filename:
    BLOCKED;
5. wrong archive manifest version:
    BLOCKED;
6. wrong extension ID:
    BLOCKED;
7. two new VSIX artifacts:
    BLOCKED;
8. modification of a pre-existing VSIX:
    BLOCKED;
9. replacement of a pre-existing VSIX:
    BLOCKED;
10. deletion of a pre-existing VSIX:
    BLOCKED;
11. creation outside VERSION_AND_PACKAGE:
    BLOCKED;
12. malformed or unknown change kind:
    BLOCKED;
13. malformed, missing, or unknown exception fields:
    schema rejection or BLOCKED;
14. case/separator/path traversal variants:
    BLOCKED;
15. other protected paths remain unchanged and fail closed.

The positive test must validate the exception without weakening any negative test.

==================================================
6. DECISION B — PRODUCER/CERTIFIER SEPARATION

Repair package-certification independence at its existing canonical enforcement
seam:

scripts/agent-governance/emit-checkpoint.mjs

Do not create a parallel policy system in verify-change-boundary.mjs.

Certification must resolve canonical actor identity, role, lifecycle ownership,
and session provenance rather than comparing only untrusted display-name strings.

A package-certification PASS requires independently proven:

* producer canonical identity;
* certifier canonical identity;
* producer role;
* certifier role;
* implementation/production session ID;
* certification/review session ID;
* distinct canonical actors;
* distinct sessions;
* certifier authorized for the exact stage;
* producer not certifying its own artifact;
* no actor alias resolving producer and certifier to the same principal;
* no consumer Agent acting as release certifier;
* complete and correctly typed provenance.

Fail closed if any required producer or certifier identity is:

* missing;
* null;
* empty;
* unknown;
* malformed;
* wrong-typed;
* unresolved;
* supplied only as an untrusted display name;
* inconsistent with the declared session;
* inconsistent with manifest role ownership.

Do not coerce malformed producer identity to null and continue.

Do not allow changing spelling, casing, display name, alias, or session label to
bypass self-certification.

==================================================
7. DECISION B — ROLE MODEL

Keep responsibilities distinct:

* VERSION_AND_PACKAGE:
    produces the versioned package;
* EXACT_PACKAGE_VERIFICATION:
    independently verifies that package;
* consumer ETL Agents:
    are not source-release certifiers;
* repository owner:
    grants explicit lifecycle authorization but does not automatically become the
    certifier;
* a role may not certify an artifact it produced.

If the same source-governance Agent currently owns both production and
certification stages, correct the manifest ownership or stage actor requirements
without creating a new Agent.

Do not broaden any Agent’s authority.

Do not make the release verifier both producer and certifier merely because its
name contains “verifier.”

Update validate-customizations.mjs so static validation identifies and blocks:

* the same canonical Agent owning package production and exact certification;
* incomplete self-review prohibition;
* unresolved certifier ownership;
* consumer Agent certification authority;
* role declarations exceeding manifest authority.

==================================================
8. DECISION B — REQUIRED TEST MATRIX

In checkpoint-fidelity.test.mjs, directly test the real independence guard.

Required cases:

1. distinct authorized producer and certifier, distinct sessions, complete
    provenance:
    PASS;
2. same canonical actor and same display name:
    BLOCKED SELF_CERTIFICATION;
3. same canonical actor under different display names:
    BLOCKED;
4. same canonical actor under an alias:
    BLOCKED;
5. different actor but same session:
    BLOCKED;
6. missing producer identity:
    BLOCKED;
7. null producer identity:
    BLOCKED;
8. empty producer identity:
    BLOCKED;
9. wrong-typed producer identity:
    BLOCKED;
10. unknown producer identity:
    BLOCKED;
11. malformed producer provenance:
    BLOCKED;
12. missing certifier identity:
    BLOCKED;
13. unauthorized certifier:
    BLOCKED;
14. consumer ETL Orchestrator attempts certification:
    BLOCKED;
15. another consumer Agent attempts certification:
    BLOCKED;
16. producer tries to certify through a renamed session:
    BLOCKED;
17. manifest ownership conflict:
    BLOCKED;
18. incomplete provenance must never produce a PASS checkpoint.

For all blocked cases require:

* exit code 2;
* deterministic diagnostic;
* OWNER_DECISION_REQUIRED or the canonical fail-closed stop code;
* agreement between console, structured output, evidence packet, checkpoint, and
    process exit code.

==================================================
9. MANIFEST AND SCHEMA INVARIANTS

The repaired manifest and schema must prove:

* every new property is schema-declared;
* unknown properties remain rejected;
* allowed change kinds are exhaustive and typed;
* artifact-count limits are typed and bounded;
* exact filename/identity derivation is deterministic;
* stage ownership remains unambiguous;
* no machine stage is unowned;
* no Agent declaration exceeds manifest authority;
* production and certification ownership are distinct;
* self-certification prohibition is complete;
* human terminal stages remain explicitly human-owned;
* no consumer Agent gains source-release authority;
* no negative-state predicate grants authority.

Do not change the manifest solely to make tests green. Tests must exercise the
actual runtime and manifest behavior.

==================================================
10. VALIDATION

Run write-producing validation only in a byte-faithful task-owned temporary mirror.

Reuse existing dependencies read-only. Do not install or download anything.

Run:

1. governance unit tests;
2. checkpoint-fidelity tests;
3. change-boundary adversarial tests;
4. manifest-registry tests;
5. manifest/schema validation;
6. customization validation;
7. test-registration validation;
8. workflow validation;
9. capture → create artifact → compare positive lifecycle;
10. all negative VSIX lifecycle cases;
11. all producer/certifier independence cases;
12. compile;
13. compile:test;
14. lint;
15. Repair 11 focused suite;
16. Repair 12 focused suite;
17. Repair 13 focused suite;
18. Runtime-QA-support fixture suite;
19. canonical full unit suite.

Require fresh compilation; do not trust stale out/**.

Expected known full-suite baseline:

* 2298 passing;
* 1 pending;
* 2 failing.

The only acceptable failures are the exact unchanged F1 and F3 identities:

* F1: missing
    .github/prompts/deploy-v3-agent-tool-context-gap.prompt.md;
* F3: eleven existing src/**/AGENT.md files.

Compare exact test identities and fingerprints, not only counts.

Required:

* new functional regressions: 0;
* new security regressions: 0;
* governance tests: all pass;
* schema findings: 0;
* manifest ownership conflicts: 0;
* self-certification bypasses: 0;
* VSIX create-only negative-case escapes: 0.

==================================================
11. FINAL CHANGE-BOUNDARY PROOF

Compare the final live repository against both pre-edit baselines.

Required:

* every task-attributable change is one of the eight authorized files;
* unauthorized changed paths: NONE;
* package.json unchanged;
* package version remains 0.3.146;
* package-lock.json remains absent;
* all existing VSIX artifacts remain byte-identical;
* databricks-etl-copilot-0.3.146.vsix remains byte-identical;
* product source unchanged;
* Repairs 11, 12, and 13 unchanged;
* consumer Agent files and tool sets unchanged;
* QA workspace untouched;
* staged files: 0;
* stash entries: 0;
* commit/push/tag: none;
* installation: not performed;
* Runtime QA: not started;
* Preview/Write: not performed.

Do not certify this repair in the implementation session.

Success authorizes only a fresh generic independent review.

It does not authorize installation or Runtime QA.

==================================================
12. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
CONCURRENT_AGENT_MUTATION: YES/NO
INDEPENDENT_BASELINE_CAPTURED: YES/NO

AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 

CREATE_ONLY_VSIX_EXCEPTION_IMPLEMENTED: YES/NO
CHANGE_KIND_ENFORCED: YES/NO
MAX_NEW_ARTIFACTS_ENFORCED: YES/NO
CANONICAL_VSIX_FILENAME_ENFORCED: YES/NO
ARCHIVE_ID_AND_VERSION_ENFORCED: YES/NO
PREEXISTING_VSIX_MODIFICATION_BLOCKED: YES/NO
VSIX_NEGATIVE_MATRIX_PASS: YES/NO

PRODUCER_IDENTITY_REQUIRED: YES/NO
CERTIFIER_IDENTITY_REQUIRED: YES/NO
CANONICAL_ACTOR_RESOLUTION_PRESENT: YES/NO
DISTINCT_ACTOR_REQUIRED: YES/NO
DISTINCT_SESSION_REQUIRED: YES/NO
MISSING_PROVENANCE_FAILS_CLOSED: YES/NO
MALFORMED_PROVENANCE_FAILS_CLOSED: YES/NO
ALIAS_SELF_CERTIFICATION_BLOCKED: YES/NO
CONSUMER_AGENT_CERTIFICATION_BLOCKED: YES/NO
PRODUCER_CERTIFIER_STAGE_OWNERSHIP_DISTINCT: YES/NO
SELF_REVIEW_PROHIBITION_COMPLETE: YES/NO

MANIFEST_SCHEMA_VALID: YES/NO
UNOWNED_MACHINE_STAGE_COUNT: 
AUTHORITY_CONFLICT_COUNT: 
AGENT_AUTHORITY_BROADENED: YES/NO

GOVERNANCE_TESTS_PASSING: 
GOVERNANCE_TESTS_FAILING: 
COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_11_PASS: YES/NO
REPAIR_12_PASS: YES/NO
REPAIR_13_PASS: YES/NO
RUNTIME_QA_SUPPORT_FIXTURE_PASS: YES/NO

FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_FAILURES: 
F1_UNCHANGED: YES/NO
F3_UNCHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
EXISTING_VSIX_CHANGED: NO
REPAIR_SOURCE_CHANGED: NO
CONSUMER_AGENT_FILES_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
INSTALL_PERFORMED: NO
RUNTIME_QA_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

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
BLOCKED_ADDITIONAL_PATH_REQUIRED

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_IDENTITY_OR_CONCURRENT_MUTATION

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT
