TASK: HF1_V2_FRESH_INDEPENDENT_GOVERNANCE_REVIEW

ROLE
Act as a genuinely independent repository-governance reviewer.

This is a fresh review session. Do not rely on conclusions, summaries, PASS labels,
or self-certification produced by the implementation agent. Re-derive every material
claim directly from repository state, source files, tests, manifests, schemas, and
current Git state.

PRIMARY OBJECTIVE
Independently review the recently implemented package-lifecycle governance repair.

The implementation claims to have resolved:

1. Create-only VSIX authorization for VERSION_AND_PACKAGE.
2. Enforcement of the PACKAGE_ARTIFACT_AUTHORIZED token.
3. Exact artifact identity/version derivation from package.json.
4. Preservation of generic protection for existing VSIX artifacts.
5. Separation of producer and certifier stage ownership.
6. Canonical agent identity resolution.
7. Fail-closed handling of missing or malformed producer identity.
8. Static detection of producer-certifies-own-output topology.
9. Checkpoint and evidence fidelity.

IMPORTANT
This is review only.

Do not:
- edit repository files;
- update tests or snapshots;
- weaken an assertion;
- regenerate evidence to manufacture a pass;
- modify governance manifests or schemas;
- build or install a VSIX;
- run Runtime QA;
- commit, stage, stash, reset, push, tag, merge, or create a release;
- accept the implementation agent’s PASS result without independent proof.

REQUIRED REVIEW PROCEDURE

1. Identity gate
   Independently record and verify:
   - repository root;
   - origin;
   - branch;
   - HEAD;
   - package version;
   - staged files;
   - stash entries;
   - package-lock presence;
   - concurrent mutation status.

2. Baseline and attribution
   Capture a fresh full-filesystem snapshot, including ignored and protected paths.
   Derive the actual changed-path set independently.
   Do not use the implementation report as the attribution authority.

3. Review the exact implementation
   Inspect at minimum:
   - .github/agent-governance/process-manifest.json
   - .github/agent-governance/schemas/process-manifest.schema.json
   - scripts/agent-governance/verify-change-boundary.mjs
   - scripts/agent-governance/emit-checkpoint.mjs
   - scripts/agent-governance/validate-customizations.mjs
   - scripts/agent-governance/tests/change-boundary-adversarial.test.mjs
   - scripts/agent-governance/tests/manifest-registry.test.mjs
   - scripts/agent-governance/tests/checkpoint-fidelity.test.mjs
   - .claude/agents/etl-release-verifier.md

4. Independently prove create-only VSIX semantics
   Verify all of the following:
   - exactly one newly created VSIX may be authorized;
   - authorization is restricted to VERSION_AND_PACKAGE;
   - PACKAGE_ARTIFACT_AUTHORIZED is required;
   - artifact filename, extension id, and version are derived from package.json;
   - wrong version fails closed;
   - wrong filename fails closed;
   - creation in another stage fails closed;
   - two created VSIX files fail closed;
   - modification of an existing VSIX remains blocked;
   - replacement or deletion of an existing VSIX remains blocked;
   - the generic VSIX protection rule remains effective.

5. Independently prove producer/certifier separation
   Verify:
   - VERSION_AND_PACKAGE has a producer owner appropriate for local artifact creation;
   - EXACT_PACKAGE_VERIFICATION has a distinct certifier owner;
   - aliases and display names cannot bypass identity comparison;
   - missing or malformed producer identity fails closed;
   - a stage owner cannot certify its own produced artifact;
   - the static topology validator detects producer-certifies-own-output configurations;
   - no agent gained write, install, execution, approval, preview, deployment, or release authority.

6. Run canonical validations
   Run the repository-defined canonical commands for:
   - manifest schema validation;
   - manifest registry tests;
   - boundary adversarial tests;
   - checkpoint fidelity tests;
   - customization validation;
   - governance unit tests;
   - agent invariant/authority checks;
   - package asset byte-lock tests;
   - compile;
   - compile:test;
   - lint;
   - Repair 11, 12, and 13 suites;
   - Runtime QA support fixture suite;
   - canonical full unit suite.

Do not substitute approximate commands. If a command is unavailable or ambiguous,
report it as unverified.

7. Reconcile known failures
   Determine by exact test identity whether F1 and F3:
   - pre-existed this task;
   - are unchanged;
   - are unrelated to the governance repair.

Do not classify them only by aggregate test counts.

8. Adversarial review
   Attempt to falsify the repair using negative controls, including:
   - remove the required token;
   - change the artifact version;
   - create a second VSIX;
   - use an existing VSIX path;
   - assign producer and certifier to the same canonical identity;
   - use an alias/display-name collision;
   - omit producer identity;
   - provide malformed producer identity.

Use an isolated temporary mirror for destructive negative controls.
Restore and hash-verify the mirror after every control.
Do not perform these mutations in the live repository.

9. Final boundary proof
   Recompute:
   - authorized changed paths;
   - unauthorized changed paths;
   - protected paths;
   - package.json status;
   - package-lock status;
   - VSIX inventory and hashes;
   - staged/stash state;
   - source version;
   - commit/push/tag/install/runtime-QA status.

FINAL REPORT

Report explicit values for:

IDENTITY_GATE
INDEPENDENCE_GATE
REPOSITORY_MUTATED_BY_REVIEW
AUTHORIZED_CHANGED_PATHS
UNAUTHORIZED_CHANGED_PATHS
CREATE_ONLY_VSIX_EXCEPTION_VALID
CREATE_ONLY_VSIX_NEGATIVE_CONTROLS_PASS
EXISTING_VSIX_PROTECTION_INTACT
PACKAGE_ARTIFACT_TOKEN_ENFORCED
ARTIFACT_IDENTITY_DERIVED_CANONICALLY
PRODUCER_CERTIFIER_DISTINCT
CANONICAL_IDENTITY_RESOLUTION_ENFORCED
MISSING_PRODUCER_FAILS_CLOSED
SELF_CERTIFICATION_BLOCKED
STATIC_TOPOLOGY_VALIDATION_PASS
AGENT_AUTHORITY_BROADENED
GOVERNANCE_TESTS_PASS
COMPILE_PASS
COMPILE_TEST_PASS
LINT_PASS
REPAIR_11_PASS
REPAIR_12_PASS
REPAIR_13_PASS
RUNTIME_QA_SUPPORT_FIXTURE_PASS
FULL_UNIT_PASSING
FULL_UNIT_PENDING
FULL_UNIT_FAILING
F1_UNCHANGED
F3_UNCHANGED
NEW_FUNCTIONAL_REGRESSIONS
NEW_SECURITY_REGRESSIONS
READY_FOR_VERSION_AND_PACKAGE
READY_FOR_EXACT_PACKAGE_VERIFICATION
READY_FOR_INSTALL
READY_FOR_RUNTIME_QA

VERDICT RULES

Return PASS only if every required governance and regression claim is independently
proven and the live repository remains unchanged by the review.

Allowed terminal verdicts:

- PASS_READY_TO_RESUME_PACKAGE_LIFECYCLE
- BLOCKED_IMPLEMENTATION_DEFECT
- BLOCKED_GOVERNANCE_DEFECT
- BLOCKED_UNPROVEN_INDEPENDENCE
- BLOCKED_ENVIRONMENT_OR_CAPTURE_FAILURE
- OWNER_DECISION_REQUIRED

Do not repair any issue discovered. Report exact evidence and the minimum recommended
follow-up boundary.
