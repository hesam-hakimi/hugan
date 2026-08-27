TASK: PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW

Perform one fresh, independent, strictly read-only review of the complete
two-commit Phase 2F.1 branch after the M1/M2 repair.

Do not reuse conclusions from either implementation Agent.
Do not edit, repair, amend, commit, push, or create a PR.

==================================================
1. EXPECTED IDENTITIES
==================================================

Repository:
TD-Enterprise/kmai-td-genie

Logical worktree:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Application root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

Branch:
phase2/recipe-lifecycle-classification

Current HEAD / repair commit:
6e37281e61a782ffbe8c8675346144567406dabe

Current repair tree:
6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab

Repair subject:
fix(recipes): harden lifecycle classification

Repair sole parent / implementation commit:
c1639fc779aaed64e4be9fdd17381e0f293c7f9f

Implementation tree:
a5bd9ed7f7959c02ccb6c00b574599fb32d4fa95

Implementation subject:
feat(recipes): add phase 2f.1 lifecycle classification

Implementation sole parent / main base:
f283f01b6d615f9fa00debcef959d9c5c86a3224

Accepted Phase 2E head:
0430613e6a9f1680338d8fc099e7960e5d46cac2

Accepted Phase 2E tree:
6448dac5be9dee275598e054f505517a215b484b

Accepted ignored baseline:

- kmai-td-genie/.coverage is absent;
- kmai-td-genie/logs/app.log:
  - regular file;
  - mode 0644;
  - size 3,603 bytes;
  - SHA-256:
    58fe010df71e59c08ab00d9ac5a96ab87991d64f52dd869bab0b2a09694d6128
- ignored-path count: 141.

==================================================
2. STRICT NO-MUTATION BOUNDARY
==================================================

Do not:

- edit, create, delete, rename, format, or restore repository files;
- modify ignored artifacts;
- stage, unstage, commit, amend, reset, clean, stash, switch, merge, rebase,
  cherry-pick, fetch, pull, or modify Git refs/configuration;
- install or upgrade dependencies;
- push or create/modify a PR, issue, comment, label, workflow, or release;
- enable a persistent runtime flag;
- implement any finding.

The only durable write permitted is the review report outside the repository.

All Python, pytest, coverage, and runtime execution must occur in a validated
external byte-faithful mirror whose application-directory basename is exactly:

kmai-td-genie

Never run Python or tests inside the live worktree.

==================================================
3. REQUIRED REPORT CHAIN
==================================================

Read completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_DISCOVERY_2026-08-26.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_TARGET_COLLISION_REVIEW_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_CONTINUATION_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_INDEPENDENT_REVIEW_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_REVIEW_WORKSPACE_INCIDENT_DISPOSITION_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_M1_M2_REPAIR_2026-08-27.md

Verify every terminal token, but treat all reports only as evidence indexes.
Independently reproduce every approval-critical claim.

==================================================
4. LIVE WORKSPACE GATE
==================================================

Before code review or mirror creation, verify:

- pwd and pwd -P;
- worktree/application realpaths;
- Git top-level and common directory;
- origin;
- branch;
- HEAD and tree;
- complete commit parent chain;
- both commit subjects;
- tracked/untracked porcelain;
- staged name-status and raw state;
- shared-worktree inventory;
- ignored baseline;
- complete live-worktree manifest.

Required result:

- exact expected identities;
- exactly two Phase 2F.1 commits after the main base;
- neither commit was amended, squashed, or replaced;
- index, tracked, untracked, and staged states empty;
- ignored baseline exact;
- no unexpected workspace drift.

If this gate fails, do not run tests.

==================================================
5. LIVE GITHUB GATE
==================================================

Using authenticated read-only GitHub GET requests only, verify:

- main remains:
  f283f01b6d615f9fa00debcef959d9c5c86a3224
- PR #17 remains merged with the accepted Phase 2E identity;
- no remote phase2/recipe-lifecycle-classification ref exists;
- no PR exists for that head branch;
- neither local Phase 2F.1 commit exists in the live repository;
- no workflow exists for either local commit.

Do not fetch or modify local refs.

==================================================
6. COMMIT AND FILE-SCOPE REVIEW
==================================================

Independently prove:

Implementation commit:

- exactly the authorized 10 Phase 2F.1 repository paths;
- four additions and six modifications;
- no eleventh repository path.

Repair commit:

- exactly these four modified paths:

  1. kmai-td-genie/src/backend/app/orchestrator.py
  2. kmai-td-genie/src/backend/app/recipes/lifecycle.py
  3. kmai-td-genie/test/test_approved_recipe_pilot.py
  4. kmai-td-genie/test/test_recipe_lifecycle.py

- no fifth path;
- no added, deleted, renamed, copied, binary, symlink, submodule, executable-mode,
  dependency, configuration, migration, schema, or generated-artifact change.

Cumulative base-to-HEAD diff must remain limited to the original 10-file
Phase 2F.1 scope.

Verify app/recipes/__init__.py remains unchanged.

==================================================
7. COMPLETE ARCHITECTURE REVIEW
==================================================

Independently review the complete cumulative implementation.

Verify:

- pure, deterministic, provider-neutral evaluator;
- already-resolved immutable evidence input;
- immutable result and nested collections;
- ApprovalEvidenceProvider Protocol boundary;
- exact state precedence:
  BROKEN > NOT_APPROVED > REVIEW_REQUIRED > VALID;
- every simultaneously applicable reason survives precedence;
- deterministic reason/ref ordering and deduplication;
- malformed, missing, ambiguous, conflicting, invalid, or stale evidence
  cannot become VALID;
- identical duplicate records remain ambiguous;
- every record is structurally and status validated;
- exact immutable five-ref accepted baseline;
- no invented expiry, owner, approver, override, or reapproval policy;
- feature flag strictly defaults OFF;
- flag-OFF returns before recipe lookup, provider call, registry access,
  evaluator, and trace;
- flag-OFF Phase 2E behavior and serialization remain unchanged;
- deny-all authorization precedes lifecycle;
- lifecycle state is never used for allow/deny, warning, SQL, routing, response
  status, fallback, or authorization;
- at most one successful best-effort trace;
- trace contains no fingerprints, SQL, raw evidence, exception text, timestamp,
  credential, or business data;
- no persistence, API, schema, cache, queue, provider SDK, SQL/data-source
  adapter, Synapse, Databricks, or Data Lake access;
- work remains bounded by declared dependency count and loaded metadata.

==================================================
8. INDEPENDENT M1 REPAIR PROOF
==================================================

Do not trust the repair report or its tests alone.

Verify through source review and independent external-mirror probes:

- the lifecycle-only exception boundary covers:
  - evaluate_recipe_lifecycle_gate();
  - lifecycle-result handling;
  - to_trace_payload();
  - lifecycle trace attempt;
- unexpected failures in each operation are discarded without propagation;
- no failed lifecycle trace or exception text is emitted;
- existing Approved Recipe execution continues byte/behavior-equivalently;
- the existing Approved Recipe gate remains outside the exception boundary;
- authorization, SQL, data-source, and unrelated failures are not swallowed;
- successful lifecycle evaluation emits at most one trace;
- flag-OFF and deny-all remain unchanged.

Any fail-open or runtime-changing lifecycle exception is approval-blocking.

==================================================
9. INDEPENDENT M2 REPAIR PROOF
==================================================

Verify through source review and independent external-mirror probes:

- executable/non-executable status is evaluated for every approval record;
- two identical draft records produce:
  - BROKEN;
  - APPROVAL_EVIDENCE_AMBIGUOUS;
  - RECIPE_NOT_APPROVED;
- mixed approved/non-approved records retain every applicable reason;
- malformed/conflicting multi-record evidence preserves invalid, conflicting,
  ambiguous, and non-approved reasons together when applicable;
- all permutations produce identical ordered results;
- existing single-record draft, validated, and retired behavior is unchanged;
- final-state precedence remains unchanged.

Any suppression of an applicable reason is approval-blocking.

==================================================
10. INDEPENDENT ACCEPTED-BASELINE PROOF
==================================================

Without trusting Phase 2F.1 constants or tests:

- reconstruct the accepted five dependency refs/fingerprints from accepted
  Phase 2E tree:
  6448dac5be9dee275598e054f505517a215b484b
- compare with the implementation baseline;
- verify exact set/value equality;
- verify no missing, extra, duplicate, malformed, or conflicting pair;
- verify deep immutability;
- verify the baseline-pin test does not derive expectations from the constant
  under test.

==================================================
11. EXTERNAL TEST MIRROR
==================================================

Create one validated temporary directory outside every Git repository.

Inside it create the application mirror with basename exactly:

kmai-td-genie

Requirements:

- byte-faithful copy of the current committed application root;
- no Git metadata;
- candidate runtime/test file hashes equal live HEAD blobs;
- PYTHONDONTWRITEBYTECODE=1;
- PYTHONPYCACHEPREFIX inside the temporary root;
- COVERAGE_FILE inside the temporary root;
- TMPDIR inside the temporary root;
- pytest cache and XML output inside the temporary root;
- RECIPE_LIFECYCLE_CLASSIFICATION_ENABLED absent from the process environment.

All test/runtime output must remain in the temporary root.

==================================================
12. TEST REVERIFICATION
==================================================

Run only from the external mirror.

Affected:

python3 -m pytest --no-cov -q \
  test/test_recipe_lifecycle.py \
  test/test_approved_recipe_pilot.py

Expected:
149 passed

Focused:

python3 -m pytest --no-cov -q \
  test/test_recipe_lifecycle.py \
  test/test_approved_recipe_pilot.py \
  test/test_authz_no_access_guard.py \
  test/test_provider_abstraction_contracts.py \
  test/test_recipe_dependency_fingerprint.py \
  test/test_governed_field_records.py \
  test/test_semantic_plan_contract.py

Expected:
238 passed, 8 warnings

Golden:

python3 -m pytest --no-cov -q test/test_golden_baseline.py

Expected:
10 passed

Full:

python3 -m pytest

Expected:

- 1076 passed;
- 3 skipped;
- 10 warnings;
- total coverage 87.01%, reported as 87%;
- lifecycle.py coverage 93%;
- orchestrator.py coverage 71%.

Verify:

- all three skips are the same unrelated CLI integration skips;
- no Phase 2F.1 test is skipped;
- no test is weakened, deselected, xfailed, or conditionally bypassed;
- M1 and M2 branches are exercised;
- warnings are pre-existing or independently justified.

Also run commit-scoped whitespace validation without modifying the live
worktree.

==================================================
13. PRE/POST LIVE-WORKTREE PROOF
==================================================

After all mirror tests:

- remove only the exact validated external temporary directory;
- compare live pre/post manifests;
- verify zero live-worktree path changed;
- verify .coverage remains absent;
- verify logs/app.log remains exactly 3,603 bytes with SHA-256:
  58fe010df71e59c08ab00d9ac5a96ab87991d64f52dd869bab0b2a09694d6128
- verify ignored-path count remains 141;
- verify branch, HEAD, tree, index, tracked, untracked, and staged states remain
  unchanged.

If any live path changes, stop and disclose it. Do not repair it.

==================================================
14. VERDICT RULES
==================================================

Approval requires:

- exact workspace, commit chain, trees, parents, and subjects;
- exact cumulative and repair file scopes;
- no unresolved collision-review defect;
- independent M1 and M2 proof;
- all architecture, compatibility, trace-only, fail-closed, and no-scan
  invariants;
- independently correct five-ref baseline;
- all affected/focused/golden/full tests passing exactly;
- accepted ignored baseline unchanged;
- byte-identical live worktree before and after review;
- no Push, PR, or workflow;
- no Critical, High, or Medium finding.

Do not implement fixes.

For each finding provide severity, exact file/symbol, evidence, violated
requirement, correction required, and whether it blocks approval.

==================================================
15. REPORT
==================================================

Write exactly one report:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_2026-08-27.md

Include:

1. final verdict;
2. workspace and complete commit-chain proof;
3. live-main and no-remote-state proof;
4. implementation and repair scope inventories;
5. cumulative architecture review;
6. disposition of all original collision findings;
7. independent M1 proof;
8. independent M2 proof;
9. independent accepted-baseline reconstruction;
10. flag-OFF and deny-all compatibility;
11. trace-only, security, and no-scan proof;
12. external-mirror identity;
13. affected/focused/golden/full test results;
14. skip, warning, and coverage evidence;
15. live pre/post manifest comparison;
16. ignored-baseline proof;
17. findings by severity;
18. clean/no-mutation attestation;
19. exact next permitted action.

If approved, the next permitted action is only a separately authorized push and
PR-creation task. Do not push, merge, or deploy.

End with exactly one token:

PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_APPROVED

or:

PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_BLOCKED_WORKSPACE
PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_BLOCKED_IDENTITY
PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_BLOCKED_BASE_DRIFT
PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_BLOCKED_GITHUB_ACCESS
PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_BLOCKED_REMOTE_STATE
PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_CHANGES_REQUIRED
