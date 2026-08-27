TASK: PHASE_2F1_REPAIR_M1_M2_TEST_AND_COMMIT

The owner has explicitly accepted the current ignored-artifact state as the new
Phase 2F.1 review baseline:

- kmai-td-genie/.coverage is absent;
- kmai-td-genie/logs/app.log remains the current 3,603-byte file;
- this acceptance does not erase or conceal the documented review incident.

Perform one bounded repair of only findings M1 and M2, independently test the
repair outside the live worktree, and create exactly one new local repair
commit.

Do not amend the existing implementation commit.
Do not push or create a PR.

==================================================
1. TARGET IDENTITY
==================================================

Repository:
TD-Enterprise/kmai-td-genie

Logical worktree:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Application root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

Required branch:
phase2/recipe-lifecycle-classification

Required current HEAD:
c1639fc779aaed64e4be9fdd17381e0f293c7f9f

Required current tree:
a5bd9ed7f7959c02ccb6c00b574599fb32d4fa95

Required parent:
f283f01b6d615f9fa00debcef959d9c5c86a3224

Required existing subject:
feat(recipes): add phase 2f.1 lifecycle classification

Accepted ignored baseline:

1. kmai-td-genie/.coverage
   - absent

2. kmai-td-genie/logs/app.log
   - regular file
   - mode: 0644
   - size: 3,603 bytes
   - SHA-256:
     58fe010df71e59c08ab00d9ac5a96ab87991d64f52dd869bab0b2a09694d6128

Accepted current manifest evidence:

- 655 descendants below the worktree root;
- 656 entries when the worktree root is included;
- ignored-path count: 141;
- task-local manifest SHA-256:
  34f2415386e61f3a769e0483428fa8f47589d6f551be8936e5d5eb31425e50de

==================================================
2. REQUIRED REPORTS
==================================================

Read completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_CONTINUATION_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_INDEPENDENT_REVIEW_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_REVIEW_WORKSPACE_INCIDENT_DISPOSITION_2026-08-27.md

Verify the terminal tokens:

PHASE_2F1_IMPLEMENTATION_CONTINUATION_COMPLETE

PHASE_2F1_INDEPENDENT_REVIEW_BLOCKED_WORKSPACE

PHASE_2F1_REVIEW_WORKSPACE_INCIDENT_REQUIRES_OWNER_DISPOSITION

Treat the owner decision in this prompt as the authorized disposition required
by the last token.

Do not reopen the ignored-artifact decision.
Do not restore, regenerate, truncate, or modify either ignored artifact.

==================================================
3. PRE-MUTATION GATE
==================================================

Before editing, verify:

- pwd and pwd -P;
- target and application-root realpaths;
- Git top-level and common directory;
- origin;
- branch;
- HEAD, tree, parent, and subject;
- tracked and untracked porcelain;
- staged state;
- shared-worktree inventory;
- accepted ignored baseline and manifest evidence.

Required state:

- exact expected identity;
- tracked, untracked, and staged states empty;
- .coverage absent;
- logs/app.log matches the accepted size and SHA-256;
- no unexplained workspace drift.

Using authenticated read-only GitHub GET requests, verify:

- main remains:
  f283f01b6d615f9fa00debcef959d9c5c86a3224
- the Phase 2F.1 branch is still not remote;
- no PR or workflow exists for the local Phase 2F.1 commit.

Do not fetch or modify local refs.

If any gate fails, stop without mutation.

==================================================
4. EXACT REPAIR SCOPE
==================================================

Only these four repository paths are authorized to change:

1. kmai-td-genie/src/backend/app/orchestrator.py
2. kmai-td-genie/src/backend/app/recipes/lifecycle.py
3. kmai-td-genie/test/test_approved_recipe_pilot.py
4. kmai-td-genie/test/test_recipe_lifecycle.py

No fifth repository path is authorized.

Do not modify:

- approval_evidence.py;
- approved_recipes.py;
- authz tests;
- provider-abstraction tests;
- ADRs or README;
- recipes/__init__.py;
- configuration or dependencies;
- ignored artifacts;
- reports created by earlier tasks.

If repository evidence proves one of the four test files unnecessary, it may
remain unchanged. Do not replace it with another path.

==================================================
5. REPAIR M1
==================================================

Finding M1:

An unexpected lifecycle-classification or trace-payload exception can propagate
from the orchestrator and alter existing runtime execution.

Required behavior:

- Phase 2F.1 remains observational, classification-only, and best-effort.
- An unexpected failure anywhere inside the lifecycle-only block must never
  alter existing execution.
- The lifecycle-only exception boundary must include:
  - evaluate_recipe_lifecycle_gate(...);
  - lifecycle-result handling;
  - to_trace_payload();
  - the lifecycle trace attempt.
- On any lifecycle-only exception:
  - emit no lifecycle trace for the failed classification;
  - serialize no exception text;
  - expose no fingerprint or raw evidence;
  - continue immediately to the existing Approved Recipe gate and unchanged
    runtime path.
- Do not catch or suppress exceptions from:
  - the existing Approved Recipe execution gate;
  - authorization;
  - SQL generation or validation;
  - data-source execution;
  - unrelated orchestration behavior.
- The lifecycle result must never influence allow/deny, SQL, routing, response
  status, warning, fallback, or authorization.
- At most one successful lifecycle trace may be emitted.

Add focused integration regression tests proving at least:

1. lifecycle-gate RuntimeError does not propagate and existing execution
   continues unchanged;
2. to_trace_payload RuntimeError does not propagate and existing execution
   continues unchanged;
3. no exception text or failed lifecycle trace is emitted;
4. existing authoritative gate failures are not swallowed by the new boundary;
5. flag-OFF and deny-all behavior remain unchanged.

==================================================
6. REPAIR M2
==================================================

Finding M2:

Multi-record non-executable approval evidence suppresses the simultaneously
applicable RECIPE_NOT_APPROVED reason.

Required behavior:

- Evaluate executable/non-executable lifecycle status for every approval record,
  independently of record count, ambiguity, or conflict.
- Multiple records remain ambiguous even when identical.
- Structural validation still applies to every record.
- Preserve every simultaneously applicable reason.
- Higher-precedence BROKEN must not suppress lower-priority applicable reasons.
- Final precedence remains exactly:

  BROKEN
  NOT_APPROVED
  REVIEW_REQUIRED
  VALID

- Reason ordering and deduplication remain deterministic.
- Do not change approval product policy or invent new statuses.
- Do not change fingerprints, baseline semantics, or persistence behavior.

Add focused regression tests proving at least:

1. two identical draft records produce:
   - final state BROKEN;
   - APPROVAL_EVIDENCE_AMBIGUOUS;
   - RECIPE_NOT_APPROVED;
2. mixed approved/non-approved multi-record evidence preserves every applicable
   reason;
3. malformed or conflicting multi-record evidence preserves invalid/conflict,
   ambiguity, and non-approved reasons together when applicable;
4. input permutations produce identical ordered results;
5. existing single-record behavior remains unchanged.

==================================================
7. LIVE-WORKTREE PROTECTION DURING TESTS
==================================================

Do not execute Python, pytest, coverage, or runtime probes inside the live
worktree after editing.

This restriction prevents another ignored-artifact incident.

After completing the candidate repair:

1. Create one validated temporary directory outside every Git repository.
2. Create a byte-faithful test mirror of the application root inside it,
   including the current uncommitted candidate source and tests.
3. Do not include Git metadata.
4. Verify the four authorized candidate files in the mirror have the same
   SHA-256 as their live candidate versions.
5. Run every test only from the temporary mirror.
6. Set:
   - PYTHONDONTWRITEBYTECODE=1;
   - PYTHONPYCACHEPREFIX inside the temporary directory;
   - COVERAGE_FILE inside the temporary directory;
   - TMPDIR inside the temporary directory;
   - pytest cache inside the temporary directory.
7. Any log, coverage, cache, XML, bytecode, or runtime output must remain inside
   that temporary directory.
8. Remove only that exact validated temporary directory after recording results.

Do not delete or modify any pre-existing live ignored file.

==================================================
8. TEST GATES
==================================================

Run from the external test mirror.

First run the directly affected tests:

python3 -m pytest --no-cov -q \
  test/test_recipe_lifecycle.py \
  test/test_approved_recipe_pilot.py

Then run the complete focused gate:

python3 -m pytest --no-cov -q \
  test/test_recipe_lifecycle.py \
  test/test_approved_recipe_pilot.py \
  test/test_authz_no_access_guard.py \
  test/test_provider_abstraction_contracts.py \
  test/test_recipe_dependency_fingerprint.py \
  test/test_governed_field_records.py \
  test/test_semantic_plan_contract.py

Previous baseline:
229 passed

Required result:

- all previous tests pass;
- all new M1/M2 tests are collected and pass;
- focused pass count increases only by the newly added tests;
- zero failure, error, xfail, or unexpected skip.

Golden gate:

python3 -m pytest --no-cov -q test/test_golden_baseline.py

Required result:
10 passed

Full gate:

python3 -m pytest

Previous baseline:
1067 passed, 3 skipped, coverage 87%

Required result:

- all previous tests and all new tests pass;
- exactly the same three justified unrelated skips unless independently
  explained;
- total coverage remains at least 87%;
- new M1/M2 branches are covered;
- no Phase 2F.1 test is skipped.

Record exact commands, exit codes, counts, skips, warnings, total coverage, and
coverage for lifecycle.py and orchestrator.py.

After mirror testing, run only non-executing Git checks in the live worktree:

git diff --check

Verify the live ignored baseline is unchanged:

- .coverage remains absent;
- logs/app.log remains exactly 3,603 bytes with SHA-256:
  58fe010df71e59c08ab00d9ac5a96ab87991d64f52dd869bab0b2a09694d6128

==================================================
9. COMMIT GATE
==================================================

Commit only if:

- M1 and M2 are corrected;
- every required test passes;
- coverage requirement passes;
- git diff --check passes;
- only the authorized paths changed;
- live ignored baseline is unchanged;
- no Critical, High, or Medium finding remains.

Create exactly one new local commit.

Do not amend or squash the original implementation commit.

Required subject:

fix(recipes): harden lifecycle classification

After committing, verify:

- the new commit has exactly one parent:
  c1639fc779aaed64e4be9fdd17381e0f293c7f9f
- the repair commit contains only the authorized changed paths;
- worktree/index/tracked/untracked states are clean;
- accepted ignored baseline remains unchanged;
- the original implementation commit remains in history.

Do not push.
Do not create a PR.
Do not trigger a workflow.
Do not merge or deploy.

==================================================
10. REPORT
==================================================

Write exactly one report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_M1_M2_REPAIR_2026-08-27.md

Include:

1. final repair verdict;
2. owner-accepted ignored-artifact disposition;
3. workspace and initial commit identity;
4. current-main and no-remote-state proof;
5. exact changed-file inventory;
6. M1 root cause and correction;
7. M1 regression-test evidence;
8. M2 root cause and correction;
9. M2 regression-test evidence;
10. external test-mirror construction and identity proof;
11. affected/focused/golden/full test results;
12. skips, warnings, and coverage;
13. live-worktree pre/post manifest comparison;
14. proof that ignored baseline remained unchanged;
15. repair commit SHA, tree, parent, and subject;
16. final clean status;
17. no-push/no-PR/no-workflow attestation;
18. exact next permitted action.

If complete, the next permitted action is a fresh independent read-only review
of the new two-commit Phase 2F.1 branch.

End with exactly one token:

PHASE_2F1_M1_M2_REPAIR_COMPLETE

or:

PHASE_2F1_M1_M2_REPAIR_BLOCKED_IDENTITY
PHASE_2F1_M1_M2_REPAIR_BLOCKED_BASE_DRIFT
PHASE_2F1_M1_M2_REPAIR_BLOCKED_SCOPE
PHASE_2F1_M1_M2_REPAIR_BLOCKED_TESTS
PHASE_2F1_M1_M2_REPAIR_BLOCKED_COVERAGE
PHASE_2F1_M1_M2_REPAIR_BLOCKED_WORKSPACE
