TASK: PHASE_2F1_PUSH_BRANCH_AND_CREATE_PR

Perform one bounded Phase 2F.1 branch push and Pull Request creation task.

This task is explicitly authorized to:

1. push the exact accepted Phase 2F.1 branch and HEAD;
2. create exactly one Pull Request targeting main;
3. observe and report automatically triggered workflow/check status.

This task is not authorized to merge the PR or modify implementation files.

Repository:
TD-Enterprise/kmai-td-genie

Required logical worktree root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Required application root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

The equivalent physical /app1 paths are acceptable only if realpath proves identity with these permanent logical paths.

==================================================

1. FIXED ACCEPTED IDENTITIES
    ==================================================

Required origin:

https://github.com/TD-Enterprise/kmai-td-genie.git

Required branch:

phase2/recipe-lifecycle-classification

Required base branch:

main

Required accepted live main SHA:

f283f01b6d615f9fa00debcef959d9c5c86a3224

Required implementation commit:

c1639fc779aaed64e4be9fdd17381e0f293c7f9f

Required repair/final HEAD:

6e37281e61a782ffbe8c8675346144567406dabe

Required final tree:

6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab

Required commit chain:

f283f01b6d615f9fa00debcef959d9c5c86a3224
-> c1639fc779aaed64e4be9fdd17381e0f293c7f9f
-> 6e37281e61a782ffbe8c8675346144567406dabe

Do not substitute a newer local commit, amend either accepted commit, or recreate the branch.

==================================================
2. REQUIRED EVIDENCE

Read this report completely before any mutation:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_2026-08-27.md

Verify that it ends exactly with:

PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_APPROVED

Use the report only as an evidence index. Independently verify all approval-critical Git and GitHub identities.

Do not modify any existing report.

==================================================
3. PRE-PUSH WORKSPACE GATE

Before pushing, verify:

* pwd;
* pwd -P;
* logical and physical root identity;
* Git top-level;
* Git common directory;
* worktree Git directory;
* origin fetch/push identity;
* current branch;
* current HEAD;
* current tree;
* both parent relationships;
* commit subjects;
* complete tracked/untracked porcelain;
* staged name-status and staged raw diff;
* git diff --check;
* ignored-artifact baseline.

Required repository state:

* branch is exactly phase2/recipe-lifecycle-classification;
* HEAD is exactly 6e37281e61a782ffbe8c8675346144567406dabe;
* tree is exactly 6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab;
* HEAD parent is exactly c1639fc779aaed64e4be9fdd17381e0f293c7f9f;
* implementation parent is exactly
    f283f01b6d615f9fa00debcef959d9c5c86a3224;
* tracked and untracked porcelain is empty;
* staged state is empty;
* git diff --check passes.

Required ignored baseline:

* kmai-td-genie/.coverage is absent;
* kmai-td-genie/logs/app.log is a regular non-symlink file;
* size is exactly 3,603 bytes;
* SHA-256 is exactly:
    58fe010df71e59c08ab00d9ac5a96ab87991d64f52dd869bab0b2a09694d6128
* ignored-path count is exactly 141.

Do not repair, regenerate, truncate, restore, delete, or modify ignored artifacts.

If any workspace or ignored-baseline requirement fails, stop without mutation and end with:

PHASE_2F1_PUSH_PR_BLOCKED_WORKSPACE

==================================================
4. LIVE BASE AND GITHUB GATE

Using authenticated read-only GitHub requests, independently verify:

* repository identity;
* current live main SHA;
* branch protection or available PR metadata needed for this task;
* whether the target remote branch already exists;
* whether any open, closed, or merged PR already uses this head branch.

The live main SHA must still be:

f283f01b6d615f9fa00debcef959d9c5c86a3224

Do not rely only on a local main ref.

Do not fetch, pull, rebase, merge, or update local refs to perform this check.

If live main differs, stop without pushing and end with:

PHASE_2F1_PUSH_PR_BLOCKED_BASE_DRIFT

Never print, store, expose, or persist credentials or tokens.

==================================================
5. REMOTE-BRANCH COLLISION GATE

Handle the remote target branch deterministically:

A. If the remote branch does not exist:

* it may be created by pushing the exact accepted local HEAD.

B. If the remote branch already points exactly to:

6e37281e61a782ffbe8c8675346144567406dabe

* treat the push as already satisfied;
* do not force-push;
* continue to the PR gate.

C. If the remote branch exists at any other SHA:

* do not push;
* do not delete, rename, reset, overwrite, or force-update it;
* stop and end with:

PHASE_2F1_PUSH_PR_BLOCKED_REMOTE_COLLISION

The only permitted Git mutation is an ordinary non-force push of the exact accepted branch:

phase2/recipe-lifecycle-classification

Use an explicit source and destination refspec.

Never use:

* --force;
* --force-with-lease;
* wildcard refspecs;
* deletion refspecs;
* tag pushes;
* --mirror;
* --all.

After the push, independently verify through GitHub that the remote branch points exactly to the accepted HEAD and tree.

==================================================
6. EXISTING-PR IDEMPOTENCY GATE

Before creating a PR, inspect all PRs associated with:

head:
TD-Enterprise:phase2/recipe-lifecycle-classification

base:
main

If no PR exists, create one as specified below.

If exactly one open PR already exists with the correct head, base and accepted HEAD:

* do not create a duplicate;
* verify its metadata;
* reuse it as the task result.

If a closed or merged PR, multiple PRs, an incorrect base, an unexpected head owner, or materially conflicting PR metadata exists:

* do not reopen, edit, close, replace, or duplicate anything;
* stop for owner review and end with:

PHASE_2F1_PUSH_PR_BLOCKED_EXISTING_PR_CONFLICT

==================================================
7. CREATE THE PULL REQUEST

Create one non-draft Pull Request.

Title:

Phase 2F.1: recipe lifecycle classification

Base:

main

Head:

phase2/recipe-lifecycle-classification

Use this PR body:

Summary

Implements Phase 2F.1 recipe lifecycle classification as a default-OFF, classification-only capability.

* Adds a pure deterministic lifecycle evaluator.
* Adds immutable lifecycle and approval-evidence contracts.
* Adds an ApprovalEvidenceProvider port and current ApprovedRecipe metadata adapter.
* Returns all applicable deterministic reason codes and affected dependency references.
* Applies final-state precedence:
    BROKEN > NOT_APPROVED > REVIEW_REQUIRED > VALID.
* Resolves evidence before calling the pure evaluator.
* Emits lifecycle results as best-effort trace evidence only.
* Preserves existing Phase 2E execution and authorization behavior when the flag is OFF.
* Adds no persistence, API, schema, cache, queue, provider query, or business-data scan.

Repair verification

The follow-up repair commit independently corrected:

* M1: lifecycle evaluation and trace failures cannot propagate into or change runtime execution.
* M2: non-executable approval status is evaluated for every approval record, including ambiguous and conflicting evidence.

The post-repair independent review approved both corrections with no Critical, High, or Medium findings.

Validation

* Affected tests: 149 passed
* Focused tests: 238 passed, 8 pre-existing/unrelated warnings
* Golden tests: 10 passed
* Full suite: 1076 passed, 3 skipped, 10 pre-existing/unrelated warnings
* Total coverage: 87.01%
* recipes/lifecycle.py: 93%
* orchestrator.py: 71%
* git diff --check: passed
* Independent M1 and M2 probes: passed
* Phase 2E accepted dependency baseline reconstruction: passed
* Live worktree and accepted ignored-artifact baseline: unchanged

Safety and scope

* Feature flag: RECIPE_LIFECYCLE_CLASSIFICATION_ENABLED
* Default: OFF
* No warn or block behavior
* No lifecycle-result persistence
* No Synapse, Databricks, Data Lake, SQL, network, or business-data access
* Work is bounded by declared recipe dependencies and already-loaded governed metadata
* Approximately 5 TB or greater provider-data scale remains outside Phase 2F.1
* Provider query pushdown remains Phase 3
* Benchmarking, concurrency, scan-cost controls, and SLO validation remain Phase 6

Deferred informational observations

The independent review recorded three non-blocking Low/Informational items:

1. discarded lifecycle failures provide no dedicated observability signal;
2. orchestrator-level invalid flag parsing is intentionally best-effort;
3. per-reference resolution is currently O(D×M) and inherits snapshot-wide conflict semantics.

These are not Phase 2F.1 approval blockers and are not changed in this PR.

Commits

* c1639fc779aaed64e4be9fdd17381e0f293c7f9f
    — Phase 2F.1 implementation
* 6e37281e61a782ffbe8c8675346144567406dabe
    — lifecycle classification hardening repair

Do not add labels, reviewers, assignees, milestone, comments, or approvals unless an existing repository automation does so automatically.

==================================================
8. AUTOMATION BOUNDARY

Automatic workflows triggered naturally by the branch push or PR creation are permitted.

Do not manually:

* dispatch a workflow;
* rerun, cancel, approve, or edit a workflow;
* change repository settings;
* change branch protection;
* create or update secrets;
* bypass required checks.

After PR creation, use authenticated read-only requests to record:

* PR number and URL;
* PR state and draft status;
* base SHA;
* head SHA;
* mergeability state if available;
* automatically triggered checks/workflows;
* current status and conclusion of each check.

Do not claim workflow success while a check is queued or in progress.

Waiting indefinitely is not required. Record the observed status accurately for the next independent review.

==================================================
9. STRICT NO-CODE-MUTATION BOUNDARY

Do not:

* edit, create, delete, rename, format, or restore repository files;
* change ignored artifacts;
* amend or create commits;
* stage or unstage files;
* reset, clean, stash, switch, merge, rebase, or cherry-pick;
* fetch or pull;
* create another branch or worktree;
* create tags or releases;
* merge the PR;
* enable a runtime flag;
* deploy anything;
* implement the three informational findings.

No implementation test rerun is required in this task because the accepted commit is immutable and independently reviewed.

==================================================
10. POST-ACTION VERIFICATION

After push and PR creation or idempotent reuse, verify:

* local branch remains unchanged;
* local HEAD remains
    6e37281e61a782ffbe8c8675346144567406dabe;
* local tree remains
    6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab;
* worktree and index remain clean;
* ignored baseline remains exact;
* remote branch points exactly to the accepted HEAD;
* PR base is main;
* PR head is phase2/recipe-lifecycle-classification;
* PR head SHA is the accepted repair commit;
* no merge occurred;
* no manual workflow action occurred.

==================================================
11. REPORT

Write exactly one report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_PUSH_AND_PR_2026-08-27.md

Include:

1. final verdict;
2. workspace and identity evidence;
3. accepted commit chain and tree;
4. live main verification;
5. remote-branch pre-state;
6. exact push command and result, with no credentials;
7. remote-branch post-state;
8. existing-PR collision check;
9. PR number, URL, title, base, head and SHAs;
10. PR body verification;
11. automatic workflow/check status;
12. final clean-state and ignored-baseline evidence;
13. explicit confirmation that no code, commit, merge, deployment, runtime flag or manual workflow action occurred;
14. exact next permitted action.

The exact next permitted action must be:

A separate independent Pull Request and workflow review. Merge is not yet authorized.

End the report and final response with exactly one token:

PHASE_2F1_PUSH_AND_PR_COMPLETE

or one applicable blocker:

PHASE_2F1_PUSH_PR_BLOCKED_WORKSPACE
PHASE_2F1_PUSH_PR_BLOCKED_BASE_DRIFT
PHASE_2F1_PUSH_PR_BLOCKED_GITHUB_ACCESS
PHASE_2F1_PUSH_PR_BLOCKED_REMOTE_COLLISION
PHASE_2F1_PUSH_PR_BLOCKED_EXISTING_PR_CONFLICT
PHASE_2F1_PUSH_PR_BLOCKED_PUSH
PHASE_2F1_PUSH_PR_BLOCKED_PR_CREATION
