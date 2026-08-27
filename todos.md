TASK: PHASE_2F1_INDEPENDENT_LOCAL_COMMIT_REVIEW

Perform one independent, strictly read-only review of the completed local
Phase 2F.1 commit.

Run this task in a fresh Agent chat. Do not reuse conclusions from the
implementation Agent.

Do not repair, edit, amend, commit, push, or create a PR.

==================================================
1. EXPECTED IDENTITIES
==================================================

Repository:
TD-Enterprise/kmai-td-genie

Target logical worktree:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Target application root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

Expected branch:
phase2/recipe-lifecycle-classification

Expected local commit:
c1639fc779aaed64e4be9fdd17381e0f293c7f9f

Expected commit tree:
a5bd9ed7f7959c02ccb6c00b574599fb32d4fa95

Expected sole parent:
f283f01b6d615f9fa00debcef959d9c5c86a3224

Expected commit subject:
feat(recipes): add phase 2f.1 lifecycle classification

Expected accepted Phase 2E head:
0430613e6a9f1680338d8fc099e7960e5d46cac2

Expected accepted Phase 2E tree:
6448dac5be9dee275598e054f505517a215b484b

==================================================
2. STRICT NO-MUTATION RULE
==================================================

This review is read-only.

Do not:

- edit, create, delete, rename, format, restore, or generate repository files;
- stage, unstage, amend, commit, reset, clean, stash, switch, merge, rebase,
  cherry-pick, fetch, pull, or modify refs or Git configuration;
- push any ref;
- create or modify a PR, issue, comment, label, release, or workflow;
- enable any persistent runtime flag;
- install or upgrade dependencies;
- use the stale primary checkout or another worktree;
- implement or repair any finding.

The only durable write permitted is the review report outside the repository.

For tests:

- use one validated temporary directory outside every repository;
- prevent bytecode and pytest cache writes inside the repository;
- redirect coverage data and TMPDIR to that temporary directory;
- remove only that exact validated temporary directory afterward;
- never delete or modify the pre-existing ignored __pycache__ or .pyc files.

If any repository mutation occurs, stop and report it without hiding or
repairing it.

==================================================
3. REQUIRED EVIDENCE
==================================================

Read these reports completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_MERGE_2026-08-26.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_POSTMERGE_REVERIFICATION_2026-08-26.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_DISCOVERY_2026-08-26.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_TARGET_COLLISION_REVIEW_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_CONTINUATION_2026-08-27.md

Verify their terminal tokens, but treat every report only as an evidence index.
Independently reproduce every approval-critical claim.

==================================================
4. WORKSPACE AND COMMIT GATE
==================================================

Before reading implementation details or running tests, independently verify:

- pwd and pwd -P;
- target logical-root realpath;
- Git top-level and common directory;
- exact origin identity;
- current branch;
- local HEAD SHA;
- HEAD tree SHA;
- parent count and sole parent;
- commit subject;
- complete porcelain status, including all untracked files;
- staged state;
- upstream configuration;
- shared-worktree inventory.

Required result:

- branch, commit, tree, parent, and subject match exactly;
- commit has exactly one parent;
- worktree and index are completely clean;
- no untracked repository file exists;
- no unexpected upstream is configured;
- permanent Phase 2E source worktree remains clean.

If this gate fails, do not run tests.

==================================================
5. EXACT COMMIT SCOPE
==================================================

Use commit-object and diff-tree evidence, not the editor UI.

Prove that the commit contains exactly these 10 paths:

Added:

1. kmai-td-genie/src/backend/app/recipes/lifecycle.py
2. kmai-td-genie/src/backend/app/recipes/approval_evidence.py
3. kmai-td-genie/test/test_recipe_lifecycle.py
4. kmai-td-genie/docs/adr/0006-phase2f1-recipe-lifecycle-classification.md

Modified:

5. kmai-td-genie/src/backend/app/recipes/approved_recipes.py
6. kmai-td-genie/src/backend/app/orchestrator.py
7. kmai-td-genie/test/test_approved_recipe_pilot.py
8. kmai-td-genie/test/test_authz_no_access_guard.py
9. kmai-td-genie/test/test_provider_abstraction_contracts.py
10. kmai-td-genie/docs/adr/README.md

Verify:

- exactly four additions and six modifications;
- no eleventh repository path;
- no rename, copy, binary, submodule, symlink, or executable-mode change;
- no dependency, configuration, migration, generated-artifact, or schema change;
- kmai-td-genie/src/backend/app/recipes/__init__.py is unchanged.

Explicitly reconcile the editor’s “11 Files changed” display.

Prove whether the eleventh item is only:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_CONTINUATION_2026-08-27.md

outside the Git repository.

If an eleventh repository path exists, fail the review.

==================================================
6. LIVE BASE AND REMOTE STATE
==================================================

Using authenticated read-only GitHub GET requests only, independently verify:

- current main remains:
  f283f01b6d615f9fa00debcef959d9c5c86a3224
- PR #17 remains merged with accepted Phase 2E identity;
- phase2/recipe-lifecycle-classification does not exist remotely;
- no PR exists for that Phase 2F.1 head branch;
- the local commit is not reachable from any remote ref;
- no workflow run exists for the local commit.

Use at least two appropriate GitHub read-only endpoints when verifying current
main identity.

Do not fetch or modify local refs.

If main has drifted, stop with the base-drift token.
If a push, PR, or workflow exists contrary to the completion report, stop with
the remote-state token.

==================================================
7. COMPLETE INDEPENDENT CODE REVIEW
==================================================

Read the complete parent-to-commit diff and all 10 changed files.

Read additional unchanged files only when directly required to verify a
referenced Phase 2E contract. Record why each additional file was needed.

Verify every defect found in the collision review was corrected:

1. Malformed auxiliary dependency evidence always contributes invalid evidence
   and can never permit VALID.
2. All simultaneously applicable reasons are preserved; no elif-based
   suppression remains.
3. Conflicting approved fingerprints produce approval-evidence conflict.
4. Whitespace-only recipe versions are rejected.
5. LifecycleStatus annotations are valid at runtime.
6. The accepted baseline is deeply immutable.
7. The accepted baseline requires exactly the five pilot dependency refs.
8. An independent baseline-pin test exists.
9. _current_dependency_evidence exists and flag-ON cannot raise NameError.
10. Current dependency resolution is complete, deterministic, and bounded.
11. Provider construction and provider calls are inside the fail-closed
    exception boundary.
12. Orchestrator integration and best-effort trace are present.
13. Tests, ADR, and ADR index are complete.

Verify all fixed architecture and product invariants:

- the evaluator is pure, deterministic, provider-neutral, and side-effect-free;
- it receives already-resolved immutable evidence;
- it never constructs or calls a provider;
- ApprovalEvidenceProvider follows the repository’s Protocol convention;
- LifecycleEvaluationResult and nested collections are immutable;
- precedence is exactly:
  BROKEN > NOT_APPROVED > REVIEW_REQUIRED > VALID;
- precedence never removes lower-priority applicable reasons;
- all affected dependency refs are retained;
- ordering and deduplication are stable and input-order independent;
- missing, malformed, ambiguous, conflicting, stale, or invalid evidence
  fails closed;
- identical duplicate approval records are still ambiguous;
- every approval record is individually validated;
- conflicting same-ref fingerprints are detected;
- whitespace-only identifiers and versions cannot become valid;
- malformed non-iterable or malformed auxiliary inputs cannot fail open;
- no expiry, reapproval window, owner, approver, override, or lifecycle mutation
  policy was invented;
- feature flag parsing uses the existing strict parser;
- the feature flag defaults to OFF;
- flag-OFF returns before recipe lookup, provider construction/call, registry
  access, lifecycle evaluation, and trace emission;
- flag-OFF Phase 2E models, serialization, outputs, SQL, and control flow remain
  unchanged;
- the deny-all authorization guard runs before lifecycle evaluation;
- denied users cause no lifecycle provider/evaluator call;
- lifecycle state is never used for allow/deny, warning, SQL, routing,
  response status, authorization, or fallback behavior;
- unexpected lifecycle/provider/registry/trace failures cannot change runtime
  execution;
- at most one best-effort recipe_lifecycle trace is emitted;
- trace data contains only permitted recipe ID, state, reason codes, and
  dependency refs;
- trace contains no fingerprint, raw evidence, SQL, exception text, timestamp,
  credential, or business data;
- no lifecycle result or baseline is persisted;
- no database, network, HTTP, provider SDK, data-source adapter, SQL tool,
  pandas, Synapse, Databricks, or Data Lake access was introduced;
- complexity is bounded by declared dependency count and already-loaded
  metadata, not total business-data volume;
- no new dependency, API, migration, cache, queue, or schema exists.

A passing test suite must not override a code-review defect.

==================================================
8. INDEPENDENT ACCEPTED-BASELINE PROOF
==================================================

Do not trust the new constants, tests, ADR, or continuation report.

Mechanically reconstruct the five accepted dependency refs and fingerprints
from the accepted Phase 2E tree:

6448dac5be9dee275598e054f505517a215b484b

Compare that independently derived result with the new pinned baseline.

Verify:

- exact five-ref set equality;
- exact fingerprint equality;
- no missing or extra ref;
- no duplicate ref;
- no conflicting pair;
- every fingerprint is well formed;
- the baseline container cannot be mutated;
- an incomplete subset is rejected;
- the baseline-pin test does not derive its expected values from the
  implementation constant it is supposed to validate.

Any discrepancy is approval-blocking.

==================================================
9. ISOLATED TEST REVERIFICATION
==================================================

Before tests:

- capture HEAD, tree, branch, status, staged state, and a content manifest of
  the complete worktree excluding .git but including existing ignored files;
- create one validated temporary directory outside every repository;
- set PYTHONDONTWRITEBYTECODE=1;
- redirect PYTHONPYCACHEPREFIX, COVERAGE_FILE, TMPDIR, and pytest cache into that
  temporary directory;
- disable the in-repository pytest cache provider;
- ensure RECIPE_LIFECYCLE_CLASSIFICATION_ENABLED is not persistently set.

From the target application root run:

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
229 passed

Golden:

python3 -m pytest --no-cov -q test/test_golden_baseline.py

Expected:
10 passed

Full:

python3 -m pytest

Expected:
1067 passed, 3 skipped, coverage 87%

Also run commit-scoped whitespace validation:

git diff --check f283f01b6d615f9fa00debcef959d9c5c86a3224..c1639fc779aaed64e4be9fdd17381e0f293c7f9f

Record:

- exact command and exit code for every gate;
- exact pass, failure, error, xfail, and skip counts;
- exact identities and reasons for all three skips;
- whether any skip masks Phase 2F.1 behavior;
- total coverage;
- coverage for lifecycle.py and approval_evidence.py;
- every warning.

Additional non-mutating diagnostics are allowed only when needed to identify a
skip, warning, or uncovered branch. Do not weaken or deselect tests.

After tests:

- compare the complete worktree manifest with the pre-test manifest;
- verify tracked, untracked, staged, and ignored content is unchanged;
- verify branch, HEAD, and tree remain unchanged;
- remove only the exact validated external temporary directory.

==================================================
10. VERDICT RULES
==================================================

Approval requires all of the following:

- exact workspace, branch, commit, tree, parent, and subject;
- exact 10-file scope;
- no unresolved requirement violation;
- all collision-review defects corrected;
- architecture, fail-closed, trace-only, compatibility, and no-scan invariants;
- independently verified five-ref baseline;
- all three test gates pass with expected results;
- all skips are unrelated and justified;
- clean, byte-identical worktree state before and after review;
- authenticated proof of no push, PR, or workflow;
- no Critical, High, or Medium finding.

Do not implement fixes.

For every finding report:

- severity;
- exact file and symbol;
- observed evidence;
- violated requirement;
- required correction;
- whether it blocks approval.

Keep optional cosmetic suggestions separate. Do not silently expand Phase 2F.1.

==================================================
11. REPORT
==================================================

Write exactly one report:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_INDEPENDENT_REVIEW_2026-08-27.md

Include:

1. final verdict;
2. workspace and identity proof;
3. commit/tree/parent/subject proof;
4. current-main and remote no-push proof;
5. exact 10-file inventory;
6. reconciliation of the editor’s 11-file display;
7. disposition of every collision-review defect;
8. architecture-invariant review;
9. independent five-ref baseline proof;
10. flag-OFF and deny-all compatibility proof;
11. trace-only, security, and no-scan proof;
12. focused, golden, and full-suite results;
13. skips, warnings, and coverage details;
14. pre/post worktree-manifest comparison;
15. findings by severity;
16. clean/no-mutation attestation;
17. exact next permitted action.

If approved, the next permitted action is only a separately authorized push and
PR-creation task. Do not push, merge, or deploy in this review.

End with exactly one token:

PHASE_2F1_INDEPENDENT_REVIEW_APPROVED

or:

PHASE_2F1_INDEPENDENT_REVIEW_BLOCKED_WORKSPACE
PHASE_2F1_INDEPENDENT_REVIEW_BLOCKED_IDENTITY
PHASE_2F1_INDEPENDENT_REVIEW_BLOCKED_BASE_DRIFT
PHASE_2F1_INDEPENDENT_REVIEW_BLOCKED_GITHUB_ACCESS
PHASE_2F1_INDEPENDENT_REVIEW_BLOCKED_REMOTE_STATE
PHASE_2F1_INDEPENDENT_REVIEW_CHANGES_REQUIRED
