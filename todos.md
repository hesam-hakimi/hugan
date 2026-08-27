TASK: PHASE_2F1_ADOPT_REPAIR_COMPLETE_AND_COMMIT

Continue the separately authorized AskAlpha/KMAI Phase 2F.1 implementation by
explicitly adopting the three pre-existing files as untrusted partial candidate
content.

Do not delete, reset, restore, overwrite wholesale, stash, clean, rename, or
discard the existing candidate work.

Preserve it initially, independently correct every reviewed defect, complete
only the authorized ten-file plan, run all required validation gates, and create
exactly one local implementation commit only after every gate passes.

This task authorizes safe edit/test/fix/rerun cycles within the exact Phase 2F.1
scope.

It does not authorize push, PR creation, merge, deployment, workflow execution,
runtime flag enablement, or any deferred Phase 2F feature.

==================================================
1. READ THE AUTHORITATIVE REPORTS
==================================================

Read these reports completely:

1.
/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_DISCOVERY_2026-08-26.md

Required terminal token:

PHASE_2F1_DISCOVERY_COMPLETE

2.
/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_2026-08-27.md

Required terminal token:

PHASE_2F1_IMPLEMENTATION_BLOCKED_TARGET_COLLISION

3.
/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_TARGET_COLLISION_REVIEW_2026-08-27.md

Required terminal token:

PHASE_2F1_TARGET_COLLISION_REVIEW_SAFE_TO_ADOPT

The discovery report defines the required architecture and ten-file scope.

The collision-review report defines:

- the exact adopted three-file candidate;
- candidate hashes and provenance evidence;
- verified five-value baseline;
- every mandatory defect repair;
- the seven untouched required files.

Do not modify any of these reports.

==================================================
2. EXACT TARGET WORKTREE
==================================================

Reuse only this existing target:

Git worktree root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Application root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

Branch:

phase2/recipe-lifecycle-classification

Required HEAD:

f283f01b6d615f9fa00debcef959d9c5c86a3224

Required HEAD tree:

6448dac5be9dee275598e054f505517a215b484b

Do not create another branch or worktree.

Do not use or modify:

- the clean Phase 2E source worktree;
- stale primary checkout;
- `asktd_v2`;
- sibling repositories;
- ETL/UCA workspaces;
- temporary worktrees.

==================================================
3. PRE-MUTATION ADOPTION GATE
==================================================

Before editing, verify:

- logical and physical target identity;
- Git top-level and common directory;
- origin;
- exact branch;
- exact HEAD and tree;
- no upstream;
- no staged changes;
- no commit after the accepted base;
- no remote branch or PR;
- exact complete porcelain state.

The only dirty paths must be:

 M kmai-td-genie/src/backend/app/recipes/approved_recipes.py
?? kmai-td-genie/src/backend/app/recipes/approval_evidence.py
?? kmai-td-genie/src/backend/app/recipes/lifecycle.py

Recompute the SHA-256 of all three paths and compare them with the exact values
recorded in the collision-review report.

If any path, state, size, hash, branch, HEAD, tree, remote ownership, or staging
state differs, stop without mutation.

The existing ignored `__pycache__`/`.pyc` artifacts recorded by the review are
not source changes. Do not delete or clean them.

Independently reverify through authenticated read-only GitHub requests that
`main` remains:

f283f01b6d615f9fa00debcef959d9c5c86a3224

If live `main` has drifted, stop without mutation.

==================================================
4. ADOPTION RULE
==================================================

Explicitly adopt the three existing source paths as untrusted partial candidate
content.

Adoption means:

- retain the useful reviewed implementation;
- treat no existing behavior as correct merely because it exists;
- patch the files in place;
- independently verify every contract;
- correct all identified defects;
- complete all missing work;
- run the entire original validation matrix.

Do not delete and recreate these files merely to remove their provenance.

Do not create a preliminary/WIP commit.

Exactly one final local commit is authorized after all tests pass.

==================================================
5. FIXED ARCHITECTURE
==================================================

Preserve Option A:

- pure deterministic lifecycle evaluator;
- `ApprovalEvidenceProvider` runtime-checkable Protocol;
- current ApprovedRecipe metadata adapter;
- orchestration-side approval and current-dependency evidence resolution;
- immutable result;
- default-OFF;
- classification-only;
- trace-only;
- provider-neutral;
- no persistence;
- no runtime warning/blocking.

Fixed state precedence:

BROKEN
NOT_APPROVED
REVIEW_REQUIRED
VALID

Return every applicable reason even when a higher-precedence state wins.

The evaluator must not access:

- environment variables;
- current time;
- random values;
- mutable globals;
- provider or registry services;
- SQL or databases;
- Synapse or Databricks;
- Data Lake;
- network/HTTP/socket;
- cache, queue or persistence;
- logger or tracer;
- business data.

==================================================
6. MANDATORY REPAIRS TO THE THREE ADOPTED FILES
==================================================

Correct every defect recorded in Collision Review Sections 8–11.

A. `src/backend/app/recipes/lifecycle.py`

1. Malformed auxiliary dependency-resolution fields must fail closed.

The current normalization can silently drop malformed/non-iterable
`missing_dependency_refs`, `conflicting_dependency_refs`, or
`invalid_dependency_refs`.

Replace this behavior with deterministic normalization that also records an
invalid condition.

Malformed auxiliary data must never be ignored in a way that permits `VALID`.

2. Preserve every applicable reason.

Do not use mutually exclusive branches that suppress:

- `RECIPE_NOT_APPROVED` when another approval field is invalid;
- `APPROVAL_EVIDENCE_INVALID` for individual malformed records;
- dependency review reasons when a higher-precedence reason also exists.

Final-state precedence selects the state; it must not remove reason codes.

3. Conflicting approved fingerprint pairs must produce:

APPROVAL_EVIDENCE_CONFLICTING

A repeated identical `(ref, fingerprint)` pair may collapse.

The same ref with different approved fingerprints must fail closed as a
conflicting approval record.

4. Whitespace-only recipe IDs or versions must be invalid.

Strict non-empty validation must reject values such as:

""
" "
"\t"
"\n"

5. Resolve the runtime `LifecycleStatus` type correctly.

Do not leave the authoritative annotation available only under
`TYPE_CHECKING`.

Use the repository’s actual runtime-safe import/annotation convention and keep
the exact authoritative contract.

6. Maintain:

- all four exact StrEnum states;
- all twelve reason codes;
- frozen dataclasses;
- fixed precedence;
- stable sorting/deduplication;
- pure evaluator;
- exact trace payload;
- explicit owning-module `__all__`.

B. `src/backend/app/recipes/approval_evidence.py`

1. Make the accepted baseline container truly immutable.

The current plain dictionary is mutable.

Use an immutable representation consistent with the discovery contract, such
as a private tuple of exact `(dependency_ref, fingerprint)` pairs.

Do not add a database, file, environment lookup or runtime-generated baseline.

2. Require exact baseline completeness.

A usable baseline must match exactly the pilot recipe’s five declared unique
dependency refs:

- no missing ref;
- no extra ref;
- no duplicate ref;
- no conflicting pair;
- every fingerprint well formed.

A non-empty subset is not usable.

Incomplete or malformed baseline evidence must become invalid evidence and fail
closed.

3. Preserve the five exact fingerprint literals independently verified in the
collision-review report.

Do not alter, guess or runtime-recompute them.

4. Preserve:

- runtime-checkable `ApprovalEvidenceProvider`;
- `ApprovedRecipeApprovalEvidenceProvider`;
- normalized lookup behavior;
- unknown recipe → zero evidence;
- known pilot recipe → one evidence record;
- cycle-safe imports;
- no provider/data-source/network/database access;
- explicit owning-module `__all__`.

C. `src/backend/app/recipes/approved_recipes.py`

1. Implement the missing `_current_dependency_evidence(...)` helper.

The current call exists but the function does not, causing a flag-on
`NameError`.

Implement bounded current-dependency evidence resolution using only:

- the existing MetadataRegistryService;
- the already materialized governed RegistrySnapshot;
- the recipe’s unique declared dataset and field refs;
- existing dependency-record resolution;
- existing `entity_ref()` and `entity_fingerprint()` semantics;
- existing unknown/conflicting/invalid metadata errors.

It must return immutable `DependencyEvidenceResolution`.

It must never call a data source, SQL, Synapse, Databricks, Data Lake or
business-data provider.

2. Normalize all current-evidence failures deterministically into:

- current fingerprints;
- missing refs;
- conflicting refs;
- invalid refs.

Metadata unavailable or malformed must fail closed for classification but must
not deny runtime execution.

3. Move provider construction inside the normalization boundary, or otherwise
prove that both provider-construction and provider-method failures are converted
to invalid approval evidence.

No provider exception may change runtime execution.

4. Preserve the first flag-disabled return before:

- recipe lookup;
- provider construction/call;
- registry construction/call;
- fingerprint work.

5. Preserve:

- exact flag name:
  `RECIPE_LIFECYCLE_CLASSIFICATION_ENABLED`;
- strict default-OFF parser;
- existing ApprovedRecipe fields;
- existing Approved Recipe execution-gate behavior;
- classification-only result;
- exact three new public exports.

==================================================
7. COMPLETE THE REMAINING SEVEN FILES
==================================================

Complete exactly these seven untouched authorized paths:

1. Add:
   `test/test_recipe_lifecycle.py`

2. Add:
   `docs/adr/0006-phase2f1-recipe-lifecycle-classification.md`

3. Modify:
   `src/backend/app/orchestrator.py`

4. Modify:
   `test/test_approved_recipe_pilot.py`

5. Modify:
   `test/test_authz_no_access_guard.py`

6. Modify:
   `test/test_provider_abstraction_contracts.py`

7. Modify:
   `docs/adr/README.md`

Together with the three adopted paths, the final change set must contain exactly
10 repository files.

Do not modify `src/backend/app/recipes/__init__.py`.

No eleventh repository path is authorized.

==================================================
8. ORCHESTRATOR INTEGRATION
==================================================

Integrate lifecycle classification immediately before the existing Approved
Recipe gate in the deterministic primary-source path.

Required order:

1. greeting handling;
2. deny-all authorization short-circuit;
3. semantic/source-plan selection;
4. recipe-parameter construction;
5. lifecycle classification helper;
6. optional best-effort `recipe_lifecycle` trace;
7. existing Approved Recipe gate;
8. existing data-source and SQL path.

When the lifecycle helper returns a result, emit only:

self._trace("recipe_lifecycle", result.to_trace_payload())

Ignore lifecycle state for control flow.

`BROKEN`, `NOT_APPROVED`, and `REVIEW_REQUIRED` must not:

- block;
- warn;
- change SQL;
- change response status;
- change routing;
- replace authorization;
- stop execution.

The existing Approved Recipe and SQL-authorization gates remain authoritative.

==================================================
9. REQUIRED TEST COVERAGE
==================================================

Implement the full discovery test matrix, including:

- all four lifecycle states;
- all twelve reason codes;
- fixed precedence;
- all-reasons preservation;
- deterministic permutations;
- stable affected-ref ordering;
- identical duplicate collapse;
- conflicting duplicate failure;
- malformed auxiliary resolution fields;
- whitespace-only identifiers and versions;
- missing, invalid, ambiguous and conflicting approval evidence;
- incomplete baseline rejection;
- exact five-value baseline pin;
- missing/conflicting/invalid current dependencies;
- provider-construction and provider-call failures;
- exact trace serialization;
- evaluator purity and repeated-input equality;
- provider Protocol conformance;
- no forbidden imports;
- bounded fingerprint-call count;
- default-OFF and explicit-false canonical compatibility;
- invalid flag-token behavior;
- deny-all ordering;
- trace ordering;
- all lifecycle states remaining trace-only;
- existing Approved Recipe SQL/status/result unchanged;
- governance-flag interaction;
- no business-data or data-source calls.

Keep the existing
`test_flag_off_leaves_the_deterministic_lane_untouched()`
test unchanged.

The ADR must document:

- Option A;
- classification-only behavior;
- state/reason mapping;
- immutable accepted baseline;
- fail-closed classification;
- default-OFF rollout and rollback;
- expected `BROKEN` trace when existing metadata flags remain disabled;
- no runtime blocking;
- no persistence;
- no business-data scan;
- Phase 3 and Phase 6 deferrals;
- test and acceptance gates;
- deliberate use of the repository’s first StrEnums.

==================================================
10. SCALE AND NO-SCAN BOUNDARY
==================================================

The approximately 5 TB data volume remains outside this classifier.

Phase 2F.1 may inspect only bounded metadata and declared recipe dependencies.

It must issue:

- zero business-data queries;
- zero SQL statements;
- zero Synapse calls;
- zero Databricks calls;
- zero Data Lake calls.

Provider query pushdown remains Phase 3.

Benchmarks, concurrency, scan-cost controls and SLOs remain Phase 6.

==================================================
11. TEST AND FIX CYCLES
==================================================

Use the existing project environment.

Use `python3`, not `python`.

Do not install or upgrade packages.

Run focused tests:

python3 -m pytest --no-cov -q \
  test/test_recipe_lifecycle.py \
  test/test_approved_recipe_pilot.py \
  test/test_authz_no_access_guard.py \
  test/test_provider_abstraction_contracts.py \
  test/test_recipe_dependency_fingerprint.py \
  test/test_governed_field_records.py \
  test/test_semantic_plan_contract.py

Run golden tests:

python3 -m pytest --no-cov -q test/test_golden_baseline.py

Run the full configured suite with coverage:

python3 -m pytest

Coverage must remain at or above 75%.

Run:

git diff --check

Safe edit/test/fix/rerun cycles are authorized until every required gate passes.

Do not weaken, delete, skip or rewrite tests merely to obtain a pass.

Do not invent an unconfigured formatter, linter or type-check gate.

If the environment lacks required dependencies, stop without installing them.

==================================================
12. FINAL ACCEPTANCE GATES
==================================================

Before committing, verify:

- exactly 10 authorized repository paths changed;
- all seven collision-review defects are corrected;
- all five pinned fingerprints remain exact;
- static baseline container is immutable;
- exact baseline completeness is enforced;
- `_current_dependency_evidence` exists and is bounded;
- lifecycle module imports correctly at runtime;
- all reasons are preserved;
- malformed values fail closed;
- flag absent/false performs no provider or registry work;
- flag-OFF canonical Phase 2E behavior is unchanged;
- lifecycle never controls execution;
- deny-all still precedes lifecycle;
- SQL authorization remains authoritative;
- no provider/data-source/network/database imports exist in evaluator/adapter;
- no API, persistence, queue, cache, UI or new backend exists;
- focused tests pass;
- golden tests pass;
- full suite passes;
- coverage is at least 75%;
- `git diff --check` passes;
- no optional cleanup or deferred work entered the diff.

==================================================
13. EXACTLY ONE LOCAL COMMIT
==================================================

Only after every gate passes:

1. inspect the complete diff;
2. verify the changed-file inventory is exactly the authorized ten files;
3. verify no secret, generated output or unrelated change exists;
4. stage only those ten files;
5. verify the staged list;
6. create exactly one local commit:

feat(recipes): add phase 2f.1 lifecycle classification

7. record commit SHA and tree SHA;
8. verify the worktree has no staged, unstaged or untracked source changes.

Do not delete the pre-existing ignored bytecode caches.

Do not amend, push, open a PR, merge, deploy, trigger a workflow or enable the
runtime flag.

If any required gate fails, do not commit.

==================================================
14. IMPLEMENTATION CONTINUATION REPORT
==================================================

Do not overwrite the earlier blocked implementation report or collision-review
report.

Write exactly one new report:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_CONTINUATION_2026-08-27.md

Include:

1. final verdict;
2. three-report token verification;
3. target branch/worktree/HEAD/tree evidence;
4. pre-adoption three-path state and hash match;
5. explicit adoption statement;
6. repair made for each collision-review defect;
7. exact final ten-file inventory;
8. five pinned dependency refs/fingerprints;
9. contracts and public symbols;
10. lifecycle/reason behavior;
11. current-dependency resolver behavior;
12. feature-flag and orchestration integration;
13. flag-OFF compatibility evidence;
14. classification-only/control-flow evidence;
15. bounded-metadata/no-scan proof;
16. focused-test command and exact result;
17. golden-test command and exact result;
18. full-suite result and coverage percentage;
19. `git diff --check` result;
20. commit SHA and tree SHA;
21. final clean-status evidence;
22. no push/PR/merge/deployment/workflow/flag-enablement attestation;
23. exact next permitted action.

The next permitted action must be an independent read-only review of the local
implementation commit.

End with exactly one token:

PHASE_2F1_IMPLEMENTATION_CONTINUATION_COMPLETE

or one applicable blocker:

PHASE_2F1_IMPLEMENTATION_CONTINUATION_BLOCKED_CANDIDATE_DRIFT
PHASE_2F1_IMPLEMENTATION_CONTINUATION_BLOCKED_BASE_DRIFT
PHASE_2F1_IMPLEMENTATION_CONTINUATION_BLOCKED_GITHUB_ACCESS
PHASE_2F1_IMPLEMENTATION_CONTINUATION_BLOCKED_SCOPE
PHASE_2F1_IMPLEMENTATION_CONTINUATION_BLOCKED_ENVIRONMENT
PHASE_2F1_IMPLEMENTATION_CONTINUATION_BLOCKED_TESTS
PHASE_2F1_IMPLEMENTATION_CONTINUATION_BLOCKED_COMMIT

At completion, output:

- final token;
- branch;
- commit SHA if created;
- exact changed-file count;
- focused-test result;
- golden-test result;
- full-suite result;
- coverage percentage;
- report path;
- confirmation that nothing was pushed and no PR was created.
