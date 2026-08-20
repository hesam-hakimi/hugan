We are continuing the existing AskTD / askAlpha / KMAI project.

This task is DISCOVERY / VERIFICATION ONLY.

Do not redesign the architecture and do not implement fixes in this operation.

Objective

Determine the actual current repository state of Program Phase 2C and identify exactly what, if anything, still prevents final independent Phase 2C acceptance.

Phase 2D must NOT begin.

Repository identity

Expected application repository:

TD-Enterprise/kmai-td-genie

The historically referenced development branch is asktd_v2, but do not assume that this is still the active continuation branch.

First report:

* repository identity;
* current branch;
* HEAD SHA;
* upstream/tracking branch if any;
* working-tree status;
* existing staged, unstaged, and untracked changes.

Do not checkout, switch, reset, clean, stash, pull, merge, rebase, commit, push, or otherwise change Git state.

If unrelated local modifications already exist, preserve them untouched and list them in the report.

Authoritative Phase 2C scope

Phase 2C consists of:

* canonical ProductGroup -> Schema -> Dataset -> Field hierarchy;
* governed metadata relationships;
* Governed Semantic Plan;
* deterministic semantic-plan validator;
* binding plans to an authoritative registry_version;
* compatibility with the accepted Phase 2A / Phase 2B contracts.

Audit the actual implementation against the following eight remediation requirements.

R1 — Canonical hierarchy cannot be bypassed

Every canonical governed Dataset must resolve to exactly one Schema.

Every Schema must resolve to exactly one Product Group.

Therefore every canonical Dataset must resolve to exactly one Product Group.

A canonical dataset with missing/null Schema must not silently bypass hierarchy validation.

Do not infer Schema or Product Group from dataset/table names.

R2 — Legacy hierarchy-less input must be adapted before canonical validation

If compatibility with legacy hierarchy-less metadata is still required, verify that it is converted through an explicit deterministic compatibility/adaptation boundary before canonical validation.

A deterministic unassigned hierarchy is acceptable only if that is the implemented compatibility contract.

Legacy compatibility must not weaken the canonical model itself.

R3 — registry_version represents the complete governed semantic snapshot

Verify that registry_version changes when governed semantic content changes, including applicable:

* Product Groups;
* Schemas;
* Datasets;
* Fields;
* Relationships;
* owners / roles / sources;
* intents / questions;
* lifecycle-relevant governed content.

It must be deterministic:

* across processes/checkouts;
* independent of collection ordering;
* based on canonical stable content/IDs;
* independent of paths, timestamps, and environment-only values.

It must not merely hash historical seed/input bytes while ignoring constructed governed content.

R4 — Explicit Product Group / Schema scope cannot contradict selected datasets

If a Governed Semantic Plan explicitly declares Product Group or Schema scope, verify that the deterministic validator derives the actual hierarchy from selected datasets and rejects contradictory explicit scope.

It must not trust a caller-supplied scope merely because the IDs independently exist.

R5 — Fields, grain fields, and time fields belong to selected datasets

Verify that every selected field referenced by the semantic plan belongs to one of the selected datasets.

Apply the same rule to:

* grain fields;
* time fields / time-window fields;
* any other structural field references used by Phase 2C.

Existence elsewhere in the registry is insufficient.

R6 — Cross-ProductGroup relationships are explicitly governed

Cross-Schema and Cross-ProductGroup relationships may be structurally valid only when an explicit governed RelationshipRecord connects the relevant endpoints.

Verify that:

* no relationship is inferred from similar field/table names;
* endpoint datasets and fields exist;
* cross-ProductGroup use requires an explicit governed relationship;
* dedicated positive and negative tests exist for cross-ProductGroup behavior.

Relationship existence must not grant authorization to either side.

R7 — Classification metadata is not authorization

PII, PCI, security/sensitivity classification, data type, key indicators, and similar attributes are governance metadata.

Verify that Phase 2C preserves authoritative classification values where supplied but does not translate them implicitly into user authorization grants.

Do not implement future fine-grained authorization as part of this audit.

R8 — Registry-cache concurrency test/contract

Inspect the previously reported Phase 2B/2C registry-cache concurrency test or contract issue.

Determine:

* whether it is already resolved;
* whether implementation and tests currently agree;
* what the intended contract actually is based on repository evidence;
* whether any remaining failure represents a production defect, a test defect, or an unresolved contract decision.

Do not choose a new concurrency semantic if repository evidence is contradictory. Report the contradiction instead.

Verification discipline

For each R1-R8, assign exactly one verdict:

* FIXED_AND_COVERED
* IMPLEMENTED_BUT_TEST_GAP
* PARTIALLY_FIXED
* OPEN
* NOT_APPLICABLE_WITH_EVIDENCE
* INSUFFICIENT_EVIDENCE

Do not mark an item fixed merely because a test has a matching name.

Inspect the actual implementation and the important assertions.

For every item provide:

1. exact implementation file path(s);
2. relevant class/function/symbol names;
3. exact test file path(s);
4. important test names;
5. short explanation of the code behavior;
6. current verdict;
7. minimum change required if the verdict is not FIXED_AND_COVERED.

Tests

Run only existing, relevant Phase 2A / 2B / 2C tests needed to verify these contracts.

Prefer focused tests first.

Where possible, prevent discovery from dirtying the repository with caches or bytecode, for example by using the repository’s supported equivalents of:

PYTHONDONTWRITEBYTECODE=1

and disabling pytest cache generation if pytest is used.

Do not:

* install or upgrade dependencies;
* rewrite snapshots/baselines;
* auto-format files;
* generate code;
* change configuration;
* update lock files.

If a required test cannot safely be run in the existing environment, report exactly why instead of changing the environment.

Also identify the appropriate parent/compatibility tests that must pass before final Phase 2C acceptance.

Documentation-versus-code reconciliation

Inspect relevant repository Phase 2C documentation/audit evidence if present.

Explicitly report any case where:

* documentation says an item is open but code has already fixed it;
* documentation says an item is complete but code/tests do not prove it;
* test expectations contradict documented contracts;
* current code introduces behavior outside Phase 2C scope.

Actual current code and executable tests are the primary evidence for implementation state.

Do not silently rewrite documentation.

Out of scope

Do NOT implement or design:

* Phase 2D recipes;
* Phase 2C.5/provider abstractions;
* DataSourceAdapter;
* DataGovernanceProvider;
* ExecutionProvider;
* Databricks integration;
* Unity Catalog integration;
* Collibra integration;
* Genie integration;
* fine-grained dataset/column/row authorization;
* Redis;
* Event Hubs;
* new runtime infrastructure;
* deployment changes;
* unrelated refactoring.

Do not modify production/application source or tests.

Required final report

Produce a Markdown report with these sections:

1. Repository Evidence
2. Executive Verdict
3. Phase 2C Remediation Matrix
4. Detailed Evidence R1-R8
5. Test Execution Results
6. Documentation vs Code Mismatches
7. Remaining Minimum Remediation
8. Independent Acceptance Readiness
9. Recommended Next Step

The Executive Verdict must contain exactly one of:

* PHASE_2C_READY_FOR_INDEPENDENT_ACCEPTANCE
* PHASE_2C_NOT_READY_FOR_INDEPENDENT_ACCEPTANCE
* PHASE_2C_STATUS_INSUFFICIENT_EVIDENCE

If Phase 2C is not ready, give the smallest bounded set of changes necessary for final acceptance. Do not implement them.

If it is ready, identify the exact independent acceptance tests/audit that should be run next. Do not start Phase 2D.

Output file

Save the report as:

ASKTD_PHASE_2C_DISCOVERY_VERIFICATION_2026-08-20.md

Prefer saving it outside the Git worktree (for example under /tmp) so the repository remains unchanged.

If the environment cannot save outside the repository, do not create a repository file merely to satisfy this instruction; instead return the complete Markdown in the agent response and clearly state that no repository file was written.

At completion, report:

* saved report path, if created;
* repository branch and HEAD SHA;
* whether the Git working tree changed during this audit.

Then STOP.

Do not remediate anything in this operation.
