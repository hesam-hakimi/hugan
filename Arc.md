TASK: PHASE_2F1_PR18_AND_WORKFLOW_INDEPENDENT_REVIEW

Perform one fresh, strictly read-only, independent review of Phase 2F.1 Pull Request #18 and its automatically triggered workflows.

This task must independently verify the PR, accepted commit identities, complete diff, workflow conclusions, mergeability, and regression evidence.

Do not merge, approve, comment on, edit, close, or otherwise mutate the PR.

Repository:

TD-Enterprise/kmai-td-genie

Pull Request:

#18

Required logical worktree root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Required application root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

Equivalent physical /app1 paths are acceptable only if realpath proves identity.

==================================================

1. REQUIRED IDENTITIES
    ==================================================

Required origin:

https://github.com/TD-Enterprise/kmai-td-genie.git

Required PR base:

main

Required accepted base SHA:

f283f01b6d615f9fa00debcef959d9c5c86a3224

Required PR head branch:

phase2/recipe-lifecycle-classification

Required implementation commit:

c1639fc779aaed64e4be9fdd17381e0f293c7f9f

Required repair and PR head commit:

6e37281e61a782ffbe8c8675346144567406dabe

Required final tree:

6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab

Required commit chain:

f283f01b6d615f9fa00debcef959d9c5c86a3224
-> c1639fc779aaed64e4be9fdd17381e0f293c7f9f
-> 6e37281e61a782ffbe8c8675346144567406dabe

PR #18 must be open and non-draft.

==================================================
2. REQUIRED PRIOR REPORTS

Read these reports completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_PUSH_AND_PR_2026-08-27.md

Verify their terminal tokens:

PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_APPROVED

PHASE_2F1_PUSH_AND_PR_COMPLETE

Use the reports only as evidence indexes. Reproduce all approval-critical GitHub, Git, diff, tree, workflow and mergeability evidence independently.

Do not modify either report.

==================================================
3. LOCAL READ-ONLY GATE

Verify:

* pwd and pwd -P;
* logical and physical path identity;
* Git top-level and common directory;
* origin identity;
* current branch;
* HEAD, tree and parent identities;
* tracked/untracked porcelain;
* staged name-status and staged raw diff;
* git diff --check;
* ignored baseline.

Required local state:

* branch:
    phase2/recipe-lifecycle-classification
* HEAD:
    6e37281e61a782ffbe8c8675346144567406dabe
* tree:
    6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab
* tracked/untracked porcelain: empty
* staged state: empty
* git diff --check: exit 0

Required ignored baseline:

* kmai-td-genie/.coverage is absent;
* kmai-td-genie/logs/app.log is a regular non-symlink file;
* size: exactly 3,603 bytes;
* SHA-256:
    58fe010df71e59c08ab00d9ac5a96ab87991d64f52dd869bab0b2a09694d6128
* ignored-path count: exactly 141.

Do not modify, restore, regenerate, truncate, or delete ignored artifacts.

If this gate fails, stop and end with:

PHASE_2F1_PR18_REVIEW_BLOCKED_WORKSPACE

==================================================
4. AUTHENTICATED GITHUB VERIFICATION

Use authenticated read-only GitHub requests.

Never print or persist credentials.

Independently verify:

* repository identity;
* live main SHA;
* PR #18 state and draft status;
* PR base repository, branch and SHA;
* PR head repository, branch and SHA;
* PR title and body;
* author;
* commit count and commit identities;
* changed-file count;
* additions/deletions;
* mergeable and merge-state values;
* review requirements;
* all check suites, check runs and workflow runs;
* remote branch SHA and tree.

The live main SHA must still be:

f283f01b6d615f9fa00debcef959d9c5c86a3224

If live main, PR base, or merge base has drifted, do not fetch, rebase or update the branch. Stop with:

PHASE_2F1_PR18_REVIEW_BLOCKED_BASE_DRIFT

If PR head differs from the accepted repair commit, stop with:

PHASE_2F1_PR18_REVIEW_BLOCKED_HEAD_DRIFT

==================================================
5. EXACT PR SCOPE

Verify that the PR contains exactly two commits and exactly these ten cumulative changed paths:

Added:

1. src/backend/app/recipes/lifecycle.py
2. src/backend/app/recipes/approval_evidence.py
3. test/test_recipe_lifecycle.py
4. docs/adr/0006-phase2f1-recipe-lifecycle-classification.md

Modified:

5. src/backend/app/orchestrator.py
6. src/backend/app/recipes/approved_recipes.py
7. test/test_approved_recipe_pilot.py
8. test/test_authz_no_access_guard.py
9. test/test_provider_abstraction_contracts.py
10. docs/adr/README.md

Verify specifically that:

* src/backend/app/recipes/__init__.py is unchanged;
* no workflow, deployment, infrastructure, dependency, configuration, database, migration, API or persistence file changed;
* implementation commit changes exactly the authorized ten-file inventory;
* repair commit changes exactly these four files:
    * src/backend/app/orchestrator.py
    * src/backend/app/recipes/lifecycle.py
    * test/test_approved_recipe_pilot.py
    * test/test_recipe_lifecycle.py

Compare GitHub’s PR head tree with the accepted local tree. They must be byte-identical.

Any additional, missing, renamed or differently classified path blocks approval:

PHASE_2F1_PR18_REVIEW_BLOCKED_SCOPE_DRIFT

==================================================
6. INDEPENDENT CODE AND CONTRACT REVIEW

Review the complete cumulative PR diff and relevant final files.

Independently verify:

* evaluator purity and determinism;
* immutable result and evidence objects;
* provider port separation;
* evidence resolution before evaluator invocation;
* stable reason-code and dependency-reference ordering;
* duplicate normalization;
* all-reasons preservation;
* precedence:
    BROKEN > NOT_APPROVED > REVIEW_REQUIRED > VALID
* fail-closed handling of missing, malformed, ambiguous, conflicting or invalid evidence;
* per-record non-executable approval evaluation;
* M1 boundary preventing lifecycle or trace failures from changing runtime execution;
* default-OFF feature flag behavior;
* exact Phase 2E behavior while OFF;
* deny-all authorization preceding lifecycle work;
* trace-only integration;
* lifecycle results never used for allow/deny, SQL generation, routing or response status;
* no persistence;
* no database, API, cache, queue, network or provider call from the pure evaluator;
* no Synapse, Databricks, Data Lake or business-data scan;
* bounded metadata-only operation;
* no timestamp, random value, current time, environment read, global mutable state or I/O inside the evaluator;
* no approval expiry, reapproval, owner, approver, override or runtime-blocking policy invented.

Classify every finding as:

* Critical
* High
* Medium
* Low
* Informational

For each finding provide file/symbol, exact evidence, impact, required correction and whether it blocks approval.

Do not implement findings.

==================================================
7. WORKFLOW COMPLETION GATE

The push report observed the PR workflow while it was still incomplete.

Enumerate every workflow run and check associated with PR #18 and the accepted head SHA.

If checks are still queued or in progress:

* poll using authenticated read-only requests;
* use bounded intervals no longer than 60 seconds;
* wait for a maximum of 30 minutes;
* do not trigger, rerun, cancel or approve anything.

A skipped job is acceptable only when its workflow condition proves that the job is legitimately non-applicable to this PR. Do not treat an unexplained skipped required check as success.

Approval requires:

* all applicable required checks completed successfully;
* no required check failed, timed out, was cancelled, or requires action;
* no workflow evaluated another head SHA;
* no merge conflict;
* branch protection is not bypassed.

A blocked merge state caused only by required human review is not a code or workflow failure. Record it precisely.

If checks remain non-terminal after the bounded wait, end with:

PHASE_2F1_PR18_REVIEW_PENDING_WORKFLOW

If any applicable required workflow fails, end with:

PHASE_2F1_PR18_REVIEW_BLOCKED_WORKFLOW

==================================================
8. REGRESSION EVIDENCE

Independently confirm the accepted test evidence:

* affected: 149 passed;
* focused: 238 passed, 8 warnings;
* golden: 10 passed;
* full suite: 1076 passed, 3 skipped, 10 warnings;
* total coverage: 87.01%;
* recipes/lifecycle.py: 93%;
* orchestrator.py: 71%;
* independent M1 probe: passed;
* independent M2 probe: passed;
* accepted Phase 2E five-reference baseline reconstruction: passed;
* git diff --check: passed.

Verify:

* all three skips are unrelated CLI integration tests;
* no Phase 2F.1 test is skipped or xfailed;
* modified pre-existing test files contain additions only relative to Phase 2E, except the independently justified Phase 2F.1 repair rename;
* warnings are pre-existing third-party or unrelated warnings;
* no assertion was weakened to make the implementation pass.

Do not rerun the full local suite inside the live worktree.

If execution is genuinely required to resolve contradictory evidence, use only a validated external temporary mirror outside every Git repository and preserve the live worktree byte-for-byte.

==================================================
9. INFORMATIONAL OBSERVATIONS

Reassess but do not implement the three prior non-blocking observations:

1. discarded lifecycle failures have no dedicated observability signal;
2. orchestrator-level invalid flag parsing is best-effort;
3. per-reference resolution is O(D×M) and inherits snapshot-wide conflict semantics.

Determine whether any becomes blocking based on PR or workflow evidence.

Do not reopen them merely because they exist. Phase 2F.1 approval is blocked only if concrete evidence shows a violated requirement, security issue or regression.

==================================================
10. STRICT NO-MUTATION BOUNDARY

Do not:

* edit, create, delete, rename, format or restore repository files;
* modify ignored artifacts;
* stage, unstage, commit, amend, reset, clean, stash, switch, merge, rebase or cherry-pick;
* fetch or pull;
* push or force-push;
* create branches, worktrees or tags;
* edit the PR title, body, base or head;
* submit a GitHub review or approval;
* add a comment, label, reviewer, assignee or milestone;
* rerun, cancel, dispatch or approve a workflow;
* change branch protection, settings, secrets or permissions;
* merge or deploy;
* enable any runtime flag.

All GitHub operations must be authenticated read-only requests.

The only authorized write is the single report outside the repository.

==================================================
11. FINAL PRESERVATION GATE

After all inspection and workflow observation, reverify:

* local HEAD and tree unchanged;
* worktree and index clean;
* ignored baseline unchanged;
* remote branch still points to the accepted head;
* PR head and base unchanged;
* no local or GitHub mutation occurred;
* no temporary review directory remains.

==================================================
12. REPORT

Write exactly one report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_PR18_AND_WORKFLOW_INDEPENDENT_REVIEW_2026-08-27.md

Include:

1. final verdict;
2. local identity and clean-state evidence;
3. live main, PR base and PR head identities;
4. PR metadata and URL;
5. exact two-commit chain;
6. exact ten-file scope verification;
7. remote/local tree equality;
8. code and architecture review;
9. M1 and M2 independent verification;
10. feature-flag, deny-all and Phase 2E compatibility proof;
11. trace-only and no-runtime-control proof;
12. no-scan, no-persistence and bounded-metadata proof;
13. workflow/check inventory with conclusions and URLs;
14. skipped-job justification;
15. mergeability and branch-protection state;
16. regression, skip, warning and coverage evidence;
17. findings by severity;
18. reassessment of the three informational observations;
19. pre/post preservation evidence;
20. explicit no-mutation attestation;
21. exact next permitted action.

If approved, the exact next permitted action must be:

A separately authorized Phase 2F.1 merge task. Merge is not authorized by this review.

End the report and final response with exactly one token:

PHASE_2F1_PR18_INDEPENDENT_REVIEW_APPROVED

or one applicable non-approval token:

PHASE_2F1_PR18_REVIEW_PENDING_WORKFLOW
PHASE_2F1_PR18_REVIEW_BLOCKED_WORKSPACE
PHASE_2F1_PR18_REVIEW_BLOCKED_GITHUB_ACCESS
PHASE_2F1_PR18_REVIEW_BLOCKED_BASE_DRIFT
PHASE_2F1_PR18_REVIEW_BLOCKED_HEAD_DRIFT
PHASE_2F1_PR18_REVIEW_BLOCKED_SCOPE_DRIFT
PHASE_2F1_PR18_REVIEW_BLOCKED_WORKFLOW
PHASE_2F1_PR18_REVIEW_BLOCKED_FINDINGS
