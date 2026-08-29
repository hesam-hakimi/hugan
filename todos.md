TASK: HF1_V2_REPAIR_PACKAGE_LIFECYCLE_GOVERNANCE_OWNER_DECISIONS_V4

ROLE

Act as a fresh maintainer-side implementation Agent.

You are not:

* a consumer ETL Agent;
* ETL Orchestrator;
* the later independent reviewer;
* authorized to install, activate, run, commit, push, or release the Extension.

Use Claude Opus 5 Max in the local VS Code Agent environment.

Bypass Permissions may be used only to avoid repetitive confirmations for repository-local reads, the nine authorized edits, temporary evidence files, and approved validation commands. It does not broaden the authorized path set or permit Git, installation, packaging, Runtime QA, or external side effects.

Communicate progress and conclusions to the owner in Persian. Keep repository files, code, tests, identifiers, and final technical reports in English.

This is a continuation of the previous V3 investigation. Do not restart broad architecture discovery.

==================================================

1. EXPECTED REPOSITORY IDENTITY
    ==================================================

Verify before any edit. Do not assume these values are still current.

Repository root:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Origin:

https://github.com/TD-Universe/agentic_etl.git

Branch:

hotfix/hf1-oracle-fresh-consumer-v2

Last reported HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected package/source version:

0.3.146

Existing target artifact:

databricks-etl-copilot-0.3.146.vsix

Extension ID:

td-etl.databricks-etl-copilot

Required identity checks:

* repository root;
* origin;
* branch;
* HEAD;
* source version;
* package-lock state;
* staged-file count;
* stash count;
* concurrent Agent mutation;
* existing VSIX inventory.

Stop before editing if identity differs materially or another Agent is modifying the repository.

==================================================
2. ACCEPTED V3 INVESTIGATION RESULT

The previous V3 session correctly stopped before editing.

Its reported outcome was:

IDENTITY_GATE: PASS
PROCESS_EXECUTION_GATE: PASS
CONCURRENT_AGENT_MUTATION: NO
INDEPENDENT_BASELINE_CAPTURED: YES
AUTHORIZED_CHANGED_PATHS: NONE
UNAUTHORIZED_CHANGED_PATHS: NONE
CREATE_ONLY_VSIX_GLOBAL_PROTECTION_INTACT: YES
AGENT_AUTHORITY_BROADENED: NO
PACKAGE_JSON_UNCHANGED: YES
VERSION_REMAINS_0_3_146: YES
PACKAGE_LOCK_ABSENT: YES
ALL_VSIX_ARTIFACTS_IDENTICAL: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_ADDITIONAL_PATH_REQUIRED

The exact additional path identified was:

.claude/agents/etl-release-verifier.md

The investigation found:

1. verify-change-boundary.mjs calculates the change kind but the protected-path exception does not enforce it.
2. The current exception model cannot safely express “exactly one newly CREATED VSIX.”
3. emit-checkpoint.mjs still relies on an incomplete/display-name-based producer-versus-certifier comparison.
4. etl-release-verifier currently owns both VERSION_AND_PACKAGE and EXACT_PACKAGE_VERIFICATION.
5. That co-ownership creates one production/certification authority conflict.
6. Correcting the manifest without updating the Agent declaration would leave inconsistent ownership metadata.
7. No V3 edit or test execution occurred.

Treat these as investigation evidence to re-confirm, not as automatic permission to skip the identity and baseline gates.

==================================================
3. AUTHORIZED CHANGE BOUNDARY — EXACTLY NINE PATHS

Only these nine repository paths may be modified:

1. .github/agent-governance/process-manifest.json
2. .github/agent-governance/schemas/process-manifest.schema.json
3. scripts/agent-governance/verify-change-boundary.mjs
4. scripts/agent-governance/tests/change-boundary-adversarial.test.mjs
5. scripts/agent-governance/tests/manifest-registry.test.mjs
6. scripts/agent-governance/emit-checkpoint.mjs
7. scripts/agent-governance/tests/checkpoint-fidelity.test.mjs
8. scripts/agent-governance/validate-customizations.mjs
9. .claude/agents/etl-release-verifier.md

No other repository path is authorized.

Specifically prohibited:

* package.json;
* package-lock.json;
* any existing or new VSIX;
* src/**;
* resources/copilot/**;
* consumer Agent resources;
* test-pattern registration files;
* prompts or instructions outside the exact list;
* consumer workspaces;
* QA workspaces;
* installed Extension state;
* Git commit, push, tag, stash, reset, or branch changes.

If a correct implementation still requires a tenth path, stop before the first edit or roll back only this task’s uncommitted changes safely, then report the exact additional path and why it is unavoidable.

Do not land a partial Decision A or Decision B.

==================================================
4. PRE-EDIT BASELINE

Before changing any file:

1. Read all applicable repository instructions and governance contracts.
2. Capture the canonical governance baseline.
3. Capture an independent OS-level full-tree snapshot.
4. Include ignored and protected files.
5. Do not rely only on git ls-files.
6. Record every existing VSIX by exact path, size, and SHA-256.
7. Record package.json and package-lock state.
8. Record all nine authorized files by path and SHA-256.
9. Record protected paths outside the boundary.
10. Verify that the V3 investigation introduced no repository mutation.

Baseline evidence must distinguish:

* pre-existing working-tree content;
* current task changes;
* ignored artifacts;
* protected paths;
* temporary evidence stored outside the repository.

==================================================
5. DECISION A — SAFE CREATE-ONLY VSIX EXCEPTION

Implement a narrow machine-enforced exception for VERSION_AND_PACKAGE.

The exception must authorize only the lifecycle that the stage legitimately requires:

* exactly one new VSIX;
* change kind exactly CREATED;
* exact expected artifact identity;
* exact current version;
* no existing VSIX mutation;
* no global weakening of **/*.vsix protection.

Required manifest/schema semantics must include the minimum machine-enforceable equivalent of:

* allowedChangeKinds: [“CREATED”];
* maximum or exact new-artifact count: 1;
* exact artifact identity derivation;
* required separate authorization token;
* stage-specific applicability;
* schema validation with additionalProperties remaining false.

Do not add fields that the verifier ignores.

The verifier must enforce:

1. The protected-path exception exists for the exact stage.
2. The supplied authorization token is correct.
3. The observed change kind is allowed.
4. Exactly one new VSIX is present.
5. The artifact filename is derived from package name/version.
6. The packaged Extension ID matches the expected identity.
7. The packaged version matches package.json.
8. No pre-existing VSIX was content-changed.
9. No pre-existing VSIX was replaced.
10. No pre-existing VSIX was renamed.
11. No pre-existing VSIX was removed.
12. No second VSIX was created.
13. The exception applies only to VERSION_AND_PACKAGE.
14. Generic **/*.vsix protection remains intact for every other stage and change kind.

Do not use newest-mtime selection, an unconstrained glob, or a handwritten filename constant as the sole identity proof.

==================================================
6. DECISION A — REQUIRED ADVERSARIAL MATRIX

Exercise the real compareSnapshots / protected-path verifier route.

Required cases:

* correct single new versioned VSIX + exact token → pass;
* exception absent → block;
* wrong stage → block;
* missing token → block;
* wrong token → block;
* CONTENT_CHANGED existing VSIX → block;
* DELETED existing VSIX → block;
* renamed/replaced existing VSIX → block;
* two newly created VSIX files → block;
* wrong package name → block;
* wrong version in filename → block;
* wrong internal package version → block;
* wrong Extension ID → block;
* artifact outside allowed identity → block;
* non-VSIX protected-path control → remain blocked;
* unrelated stage attempting VSIX creation → block.

Include at least one mutation control proving the test fails if change-kind enforcement is removed.

==================================================
7. DECISION B — DISTINCT PRODUCER AND CERTIFIER

Repair the existing checkpoint/governance system. Do not create a parallel policy engine.

Required outcomes:

* VERSION_AND_PACKAGE production authority and EXACT_PACKAGE_VERIFICATION certification authority are distinct;
* etl-release-verifier must not own both stages;
* .claude/agents/etl-release-verifier.md must agree with the canonical process manifest;
* missing producer identity fails closed;
* malformed or wrong-typed provenance fails closed;
* ambiguous producer identity fails closed;
* producer and certifier identities are resolved canonically;
* aliases or different display names cannot conceal the same actor;
* producer and certifier must be different when independent certification is required;
* required implementation/review session IDs must be distinct;
* the producer cannot certify the artifact it produced;
* static manifest/customization validation detects impossible independence topology;
* no new Agent is created;
* no Agent gains new write, approval, installation, Preview, deployment, or runtime authority.

Do not determine trust solely from a user-facing Agent name.

Do not merely remove a stage name from one file. Keep the process manifest, schema, Agent declaration, checkpoint emitter, and validators mutually consistent.

Derive the correct owner/actor arrangement from the repository’s existing governance model. Do not invent an unregistered reviewer or a new Agent.

==================================================
8. DECISION B — REQUIRED NEGATIVE MATRIX

At minimum, prove:

* missing implementedBy/producer identity → block;
* null producer → block;
* empty producer → block;
* malformed provenance object → block;
* wrong-typed producer → block;
* producer equals certifier → block;
* producer alias equals certifier canonical identity → block;
* same display name but different unproven identity → block or remain untrusted;
* distinct valid producer/certifier identities → pass;
* same session ID where separation is required → block;
* distinct valid session IDs → pass;
* etl-release-verifier production/certification co-ownership → static validation failure;
* corrected ownership topology → static validation pass;
* consumer ETL Agent cannot become a source-governance certifier;
* unknown reviewer remains fail closed;
* no SELF_CERTIFICATION or CERTIFIED_OWN_IMPLEMENTATION bypass remains.

Include mutation controls for:

* removal of missing-producer fail-closed logic;
* replacement of canonical identity comparison with display-name-only comparison;
* restoration of dual stage ownership.

==================================================
9. REQUIRED VALIDATION

Use repository-canonical commands. Record every invoked command/tool and its real exit code.

Run, at minimum:

1. Process-manifest schema validation.
2. Manifest registry tests.
3. Change-boundary adversarial tests.
4. Checkpoint-fidelity tests.
5. Customization validation.
6. Governance unit tests.
7. Agent invariant and authority checks.
8. Package asset byte-lock tests.
9. Compile.
10. Compile-test.
11. Lint.
12. Repair 11 focused suites.
13. Repair 12 focused suites.
14. Repair 13 focused suites.
15. Runtime QA support fixture suite.
16. Canonical full unit suite.
17. Independent post-edit boundary comparison.

Do not run tests against stale compiled output. Perform the repository’s canonical clean compile before the final full-suite run when required.

The previously reported full-unit state was:

2298 passing
1 pending
2 failing

The two known failures were:

F1:
missing .github/prompts/deploy-v3-agent-tool-context-gap.prompt.md

F3:
existing src/**/AGENT.md files versus expected AGENTS.md guidance

Re-derive the live results by exact test identity.

Do not modify F1/F3 paths, remove tests, weaken expectations, or regenerate unrelated baselines in this task.

==================================================
10. POST-EDIT BOUNDARY PROOF

At close, independently compare the full tree against the pre-edit baseline.

Required proof:

* authorized changed paths are a subset of the nine declared paths;
* unauthorized changed paths: none;
* package.json unchanged;
* package-lock state unchanged;
* package version remains 0.3.146;
* all existing VSIX artifacts byte-identical;
* no new VSIX created;
* Repair 13 source unchanged;
* consumer Agent assets unchanged;
* QA workspace untouched;
* Extension not installed or uninstalled;
* Runtime QA not started;
* no commit, push, tag, stash, or branch mutation;
* temporary evidence exists only outside the repository.

==================================================
11. REQUIRED FINAL REPORT

Report:

1. Identity gate.
2. Process-execution gate.
3. Concurrent-Agent state.
4. Baseline methods and coverage.
5. Exact authorized changed paths.
6. Exact unauthorized changed paths.
7. Decision A implementation mapping:
    requirement → source change → test.
8. Decision A complete adversarial matrix.
9. Decision B ownership model before and after.
10. Decision B canonical identity/provenance enforcement.
11. Decision B complete negative matrix.
12. Mutation-control evidence.
13. All test commands and exit codes.
14. Full-suite count and exact failure reconciliation.
15. Final boundary and VSIX byte-identity proof.
16. Remaining findings.
17. Honest readiness state.

Required terminal fields:

IDENTITY_GATE: PASS|BLOCKED
PROCESS_EXECUTION_GATE: PASS|BLOCKED
CONCURRENT_AGENT_MUTATION: NO|YES
INDEPENDENT_BASELINE_CAPTURED: YES|NO

AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: NONE|

CREATE_ONLY_VSIX_EXCEPTION_ADDED: YES|NO
CREATE_ONLY_VSIX_CHANGE_KIND_ENFORCED: YES|NO
CREATE_ONLY_VSIX_EXACT_COUNT_ENFORCED: YES|NO
CREATE_ONLY_VSIX_EXACT_IDENTITY_ENFORCED: YES|NO
CREATE_ONLY_VSIX_NEGATIVE_MATRIX_PASS: YES|NO
CREATE_ONLY_VSIX_GLOBAL_PROTECTION_INTACT: YES|NO

PRODUCER_IDENTITY_RESOLUTION_ADDED: YES|NO
CERTIFIER_IDENTITY_RESOLUTION_ADDED: YES|NO
PRODUCER_CERTIFIER_INDEPENDENCE_ENFORCED: YES|NO
MISSING_PRODUCER_FAILS_CLOSED: YES|NO
CANONICAL_ALIAS_SELF_CERTIFICATION_BLOCKED: YES|NO
PRODUCER_CERTIFIER_STAGE_OWNERSHIP_DISTINCT: YES|NO
STATIC_CERTIFICATION_TOPOLOGY_VALIDATED: YES|NO
SELF_CERTIFICATION_BYPASSES: 0|

AGENT_AUTHORITY_BROADENED: NO|YES
NEW_AGENT_CREATED: NO|YES

GOVERNANCE_UNIT_TESTS: PASS|FAIL
CHECKPOINT_FIDELITY_TESTS: PASS|FAIL
CHANGE_BOUNDARY_ADVERSARIAL_TESTS: PASS|FAIL
MANIFEST_REGISTRY_TESTS: PASS|FAIL
CUSTOMIZATION_VALIDATION: PASS|FAIL
COMPILE_PASS: YES|NO
COMPILE_TEST_PASS: YES|NO
LINT_PASS: YES|NO
REPAIR_11_PASS: YES|NO
REPAIR_12_PASS: YES|NO
REPAIR_13_PASS: YES|NO
RUNTIME_QA_SUPPORT_FIXTURE_PASS: YES|NO
PACKAGE_ASSET_BYTE_LOCK_PASS: YES|NO

FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
F1_UNCHANGED: YES|NO
F3_UNCHANGED: YES|NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

PACKAGE_JSON_UNCHANGED: YES|NO
VERSION_REMAINS_0_3_146: YES|NO
PACKAGE_LOCK_STATE_UNCHANGED: YES|NO
EXISTING_VSIX_BYTE_IDENTICAL: YES|NO
NEW_VSIX_CREATED: NO|YES
REPAIR_13_SOURCE_UNCHANGED: YES|NO
CONSUMER_AGENT_ASSETS_UNCHANGED: YES|NO
QA_WORKSPACE_TOUCHED: NO|YES
EXTENSION_INSTALLED_OR_UNINSTALLED: NO|YES
RUNTIME_QA_STARTED: NO|YES
COMMIT_CREATED: NO|YES
PUSH_EXECUTED: NO|YES

READY_FOR_FRESH_GENERIC_GOVERNANCE_REVIEW: YES|NO
READY_FOR_PACKAGE_LIFECYCLE_REVERIFICATION: NO
READY_FOR_LOCAL_INSTALL: NO
READY_FOR_RUNTIME_QA: NO

Success terminal result:

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
PASS_READY_FOR_FRESH_GENERIC_GOVERNANCE_REVIEW

Blocked terminal result:

PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_<EXACT_REASON>

==================================================
12. STOP RULES

* Stop before editing if identity or authority is wrong.
* Stop before partial edits if a tenth path is required.
* Do not weaken generic VSIX protection.
* Do not accept display-name-only independence.
* Do not manufacture missing producer provenance.
* Do not create a new Agent to escape the ownership conflict.
* Do not change package version or create/rebuild a VSIX.
* Do not install or activate the Extension.
* Do not start consumer Runtime QA.
* Do not commit or push.
* Do not self-review.

If implementation passes, the next task must run in a genuinely fresh generic review session and independently re-derive all evidence.
