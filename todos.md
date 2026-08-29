TASK: HF1_V2_REPAIR_INDEPENDENT_GOVERNANCE_REVIEW_DEFECTS

ROLE
Act as the bounded governance-framework implementer.

This is a continuation after a genuinely independent review returned:

OWNER_DECISION_REQUIRED

The independent reviewer identified five findings:

D1 BLOCKER — GOVERNANCE_GATE_KEYED_TO_SELF_DECLARED_FIELD
D2 BLOCKER — GOVERNANCE_FRAMEWORK_NOT_VERSION_CONTROLLED
D3 MAJOR — TASK_ATTRIBUTION_IMPOSSIBLE
D4 MAJOR — PACKAGE_LIFECYCLE_BLOCKED_AT_CURRENT_VERSION
D5 MINOR — BOUNDARY_TOOL_DOES_NOT_INHERIT_PROTECT_SET

OWNER DECISION

I authorize a narrowly bounded implementation to repair D1 and D5, and to prepare
an exact version-control inclusion plan for D2.

D3 must be resolved procedurally by capturing a fresh authoritative baseline before
the first edit.

D4 is deferred to a later VERSION_AND_PACKAGE task. Do not change package.json,
do not create version 0.3.147, and do not build or modify any VSIX in this task.

Do not package, install, activate, run Runtime QA, commit, push, merge, tag, release,
reset, stash, or modify unrelated files.

PHASE 1 — IDENTITY AND BASELINE

Before the first edit:

1. Record repository root, origin, branch, HEAD, package version, staged files,
   stash entries, tracked/untracked/ignored state, and VSIX inventory.
2. Capture a full filesystem baseline using both:
   - the canonical governance baseline mechanism;
   - an independent OS-level path/size/SHA-256 snapshot.
3. Explicitly enumerate the pre-existing 86 modified entries.
4. Establish the exact authorized path set before editing.
5. If attribution cannot be made reliable, stop with
   BLOCKED_BASELINE_OR_ATTRIBUTION_FAILURE.

PHASE 2 — REPAIR D1

Repair the self-certification control so it is derived from objective repository
facts and not from reviewer-provided provenance.certifiedPaths.

Requirements:

- Determine governance-authority paths from the actual changed-path set,
  stage ownership and manifest authority definitions.
- A reviewer must not bypass the gate by:
  - omitting certifiedPaths;
  - supplying [];
  - supplying unrelated paths;
  - supplying incomplete paths;
  - changing display name or alias.
- The gate must detect when a reviewer is certifying changes within its own
  governance authority.
- Missing, malformed, inconsistent or incomplete provenance must fail closed.
- Do not broaden any reviewer or agent authority.
- Preserve legitimate fresh-generic-session and external-pinned-reviewer behavior.

Add focused positive and adversarial tests proving all of the above.

PHASE 3 — REPAIR D5

Repair verify-change-boundary.mjs so the protected-path set is derived correctly
when --protect is omitted.

Requirements:

- Use the canonical manifest/schema protection definitions.
- Explicit --protect input must remain supported.
- Omission must not classify generated out/** files as control-plane changes.
- Malformed or unavailable protection configuration must fail closed.
- Add regression tests for:
  - omitted --protect;
  - explicit --protect;
  - malformed protected-path configuration;
  - ignored/generated output;
  - actual protected-path changes.

PHASE 4 — D2 VERSION-CONTROL PLAN

Do not blindly stage or commit the current dirty working tree.

Produce an exact inclusion inventory for:

- .github/agent-governance/**
- scripts/agent-governance/**
- the enforcing workflow(s);
- required agent definitions;
- required .gitignore changes, if any.

For every candidate file report:

- tracked/untracked/ignored status;
- whether it is required at runtime;
- whether it is required for validation;
- whether it existed before this task;
- whether its content changed during this task;
- recommended inclusion or exclusion;
- reason.

Prove that unrelated source files, VSIX files, build outputs, temporary evidence,
and the 86 pre-existing changes are excluded.

Do not create the commit. Produce a proposed commit manifest for owner approval.

PHASE 5 — VALIDATION

Run all canonical applicable validations, including:

- manifest schema validation;
- manifest registry tests;
- change-boundary adversarial tests;
- checkpoint fidelity tests;
- customization validation;
- governance unit tests;
- agent invariant/authority checks;
- package asset byte-lock tests;
- compile;
- compile:test;
- lint;
- Repair 11, 12 and 13 suites;
- Runtime QA support fixture suite;
- canonical full unit suite.

Reconcile F1 and F3 by exact identity and prove they remain unchanged.

Use isolated temporary mirrors for destructive negative controls.
Do not mutate the live repository for a negative test.

PHASE 6 — FINAL BOUNDARY PROOF

Compare the post-task tree against both pre-task baselines.

Report:

IDENTITY_GATE
INDEPENDENT_BASELINE_CAPTURED
AUTHORIZED_CHANGED_PATHS
UNAUTHORIZED_CHANGED_PATHS
D1_OBJECTIVE_CHANGE_DERIVATION_IMPLEMENTED
D1_OMISSION_BYPASS_BLOCKED
D1_EMPTY_LIST_BYPASS_BLOCKED
D1_INCOMPLETE_LIST_BYPASS_BLOCKED
D1_ALIAS_BYPASS_BLOCKED
D1_FAIL_CLOSED
D5_CANONICAL_PROTECT_SET_INHERITED
D5_EXPLICIT_PROTECT_SUPPORTED
D5_GENERATED_OUTPUT_FALSE_POSITIVES
D2_PROPOSED_COMMIT_MANIFEST
D2_UNRELATED_CHANGES_EXCLUDED
AGENT_AUTHORITY_BROADENED
PACKAGE_JSON_CHANGED
VSIX_CHANGED_OR_CREATED
COMPILE_PASS
COMPILE_TEST_PASS
LINT_PASS
GOVERNANCE_TESTS_PASS
REPAIR_11_PASS
REPAIR_12_PASS
REPAIR_13_PASS
FULL_UNIT_PASSING
FULL_UNIT_PENDING
FULL_UNIT_FAILING
F1_UNCHANGED
F3_UNCHANGED
NEW_FUNCTIONAL_REGRESSIONS
NEW_SECURITY_REGRESSIONS
READY_FOR_OWNER_APPROVAL_OF_GOVERNANCE_COMMIT

Allowed terminal verdicts:

- PASS_READY_FOR_OWNER_APPROVAL_OF_GOVERNANCE_COMMIT
- BLOCKED_BASELINE_OR_ATTRIBUTION_FAILURE
- BLOCKED_IMPLEMENTATION_DEFECT
- BLOCKED_UNAUTHORIZED_CHANGE
- OWNER_DECISION_REQUIRED
