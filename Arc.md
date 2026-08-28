TASK: PHASE_2F1_PR18_AUTHORIZED_MERGE

Perform one strictly bounded and explicitly authorized merge of Phase 2F.1 Pull Request #18.

The only authorized repository mutation is merging PR #18 into main using a genuine merge commit.

Do not use squash merge or rebase merge.

Do not delete the source branch.

Repository:

TD-Enterprise/kmai-td-genie

Pull Request:

https://github.com/TD-Enterprise/kmai-td-genie/pull/18

Required logical worktree root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Required application root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

Equivalent physical /app1 paths are acceptable only if realpath proves identity.

==================================================

1. FIXED ACCEPTED IDENTITIES
    ==================================================

Required origin:

https://github.com/TD-Enterprise/kmai-td-genie.git

Required base branch:

main

Required pre-merge main SHA:

f283f01b6d615f9fa00debcef959d9c5c86a3224

Required PR head branch:

phase2/recipe-lifecycle-classification

Required implementation commit:

c1639fc779aaed64e4be9fdd17381e0f293c7f9f

Required repair and accepted PR head:

6e37281e61a782ffbe8c8675346144567406dabe

Required accepted PR-head tree:

6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab

Required commit chain:

f283f01b6d615f9fa00debcef959d9c5c86a3224
-> c1639fc779aaed64e4be9fdd17381e0f293c7f9f
-> 6e37281e61a782ffbe8c8675346144567406dabe

==================================================
2. REQUIRED PRIOR EVIDENCE

Read these reports completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_PUSH_AND_PR_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_PR18_AND_WORKFLOW_INDEPENDENT_REVIEW_2026-08-27.md

Verify that their required terminal tokens are respectively:

PHASE_2F1_POST_REPAIR_INDEPENDENT_REVIEW_APPROVED

PHASE_2F1_PUSH_AND_PR_COMPLETE

PHASE_2F1_PR18_INDEPENDENT_REVIEW_APPROVED

Use the reports only as evidence indexes. Independently verify every merge-critical condition immediately before merging.

Do not modify any prior report.

==================================================
3. LOCAL PRE-MERGE PRESERVATION GATE

Before any GitHub mutation, verify:

* pwd;
* pwd -P;
* logical and physical path identity;
* Git top-level and common directory;
* origin fetch and push identity;
* current branch;
* local HEAD;
* local tree;
* HEAD parent;
* complete tracked/untracked porcelain;
* staged name-status and staged raw diff;
* git diff --check;
* ignored-artifact baseline.

Required local state:

* branch:
    phase2/recipe-lifecycle-classification
* HEAD:
    6e37281e61a782ffbe8c8675346144567406dabe
* tree:
    6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab
* HEAD parent:
    c1639fc779aaed64e4be9fdd17381e0f293c7f9f
* tracked/untracked porcelain: empty
* staged state: empty
* git diff --check: exit 0

Required ignored baseline:

* kmai-td-genie/.coverage is absent;
* kmai-td-genie/logs/app.log is a regular non-symlink file;
* size is exactly 3,603 bytes;
* SHA-256 is exactly:
    58fe010df71e59c08ab00d9ac5a96ab87991d64f52dd869bab0b2a09694d6128
* ignored-path count is exactly 141.

Do not modify, restore, regenerate, truncate or delete ignored artifacts.

If this gate fails, stop without merging and end with:

PHASE_2F1_PR18_MERGE_BLOCKED_WORKSPACE

==================================================
4. FINAL LIVE GITHUB GATE

Using authenticated read-only GitHub requests, immediately verify:

* repository identity;
* live main SHA;
* PR #18 is open and non-draft;
* PR base is main;
* PR head branch is
    phase2/recipe-lifecycle-classification;
* PR head SHA is
    6e37281e61a782ffbe8c8675346144567406dabe;
* remote source branch points to the same SHA;
* PR contains exactly two commits;
* PR contains exactly ten changed files;
* PR is mergeable with no conflicts;
* no requested-changes review exists;
* at least one currently valid approving review from a reviewer with write access exists;
* all applicable required checks are terminal and successful;
* the two skipped checks are still proven non-applicable by the empty Terraform matrix;
* SonarQube reports success;
* the observed new-code coverage is 91%, satisfying the 80% threshold;
* branch protection is satisfied without bypass.

The accepted approval currently shown is from:

Vuggina, Sravya
GitHub identity: tar2859_tdbank

Do not rely only on screenshots or prior reports. Verify the current live review state.

The live main SHA must still be:

f283f01b6d615f9fa00debcef959d9c5c86a3224

If main has advanced, stop without merging. Do not fetch, rebase, merge locally or update the PR branch. End with:

PHASE_2F1_PR18_MERGE_BLOCKED_BASE_DRIFT

If the PR head, commit count, file count, approval, checks or mergeability differs, stop without mutation and use the applicable blocker:

PHASE_2F1_PR18_MERGE_BLOCKED_HEAD_DRIFT
PHASE_2F1_PR18_MERGE_BLOCKED_SCOPE_DRIFT
PHASE_2F1_PR18_MERGE_BLOCKED_APPROVAL
PHASE_2F1_PR18_MERGE_BLOCKED_CHECKS
PHASE_2F1_PR18_MERGE_BLOCKED_CONFLICT

Never print or persist credentials or tokens.

==================================================
5. AUTHORIZED MERGE METHOD

Merge PR #18 through the authenticated GitHub API using:

* expected head SHA:
    6e37281e61a782ffbe8c8675346144567406dabe
* merge method:
    merge

Use an expected-head guard so the merge fails if the PR head changes between the final gate and merge request.

Expected merge commit title:

Merge pull request #18 from TD-Enterprise/phase2/recipe-lifecycle-classification

Expected merge commit message:

Phase 2F.1: recipe lifecycle classification

Do not use:

* squash merge;
* rebase merge;
* admin bypass;
* branch-protection bypass;
* local merge;
* force push;
* direct push to main.

Submit exactly one merge request.

If GitHub returns an ambiguous response, do not submit a second merge request until read-only requests establish whether the first request succeeded.

==================================================
6. IMMEDIATE POST-MERGE VERIFICATION

After the merge request, independently verify:

* PR #18 is closed and merged=true;
* GitHub reports the exact merge commit SHA;
* live main points exactly to that merge commit;
* the merge commit has exactly two parents;
* first parent is exactly:
    f283f01b6d615f9fa00debcef959d9c5c86a3224
* second parent is exactly:
    6e37281e61a782ffbe8c8675346144567406dabe
* the merge commit tree is exactly:
    6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab
* the merge-commit tree is byte-identical to the accepted PR-head tree;
* no unexpected additional commit exists between the accepted base and merge commit;
* the source branch still exists and still points to the accepted head;
* no tag or release was created;
* no deployment or runtime flag was enabled.

If the merge response reports failure and GitHub confirms the PR remains open, end with:

PHASE_2F1_PR18_MERGE_BLOCKED_GITHUB

If GitHub confirms the merge occurred but any post-merge identity is unexpected, do not attempt repair or another merge. End with:

PHASE_2F1_PR18_MERGE_COMPLETED_IDENTITY_MISMATCH

==================================================
7. POST-MERGE WORKFLOW OBSERVATION

Discover all workflows and check runs automatically triggered by the merge commit or updated main.

Do not manually trigger, rerun, cancel or approve any workflow.

For each run, record:

* workflow name;
* run ID and URL;
* event;
* attempt;
* head branch;
* head SHA;
* status;
* conclusion;
* every job/check name and conclusion.

If workflows remain queued or in progress:

* poll with authenticated read-only requests;
* use intervals no longer than 60 seconds;
* wait for a maximum of 30 minutes.

Do not treat a skipped job as successful without verifying its job condition and non-applicability.

If every applicable post-merge workflow completes successfully, record that result.

If workflows remain pending after the bounded wait, the merge itself remains valid. End with:

PHASE_2F1_PR18_MERGE_COMPLETE_WORKFLOW_PENDING

If a post-merge workflow fails, is cancelled, times out or requires action, do not rerun it. End with:

PHASE_2F1_PR18_MERGE_COMPLETE_WORKFLOW_FAILED

==================================================
8. STRICT MUTATION BOUNDARY

The only authorized mutation is the single GitHub merge operation for PR #18.

Do not:

* edit repository files;
* modify ignored artifacts;
* stage, unstage, commit or amend;
* reset, clean, stash, switch, merge locally, rebase or cherry-pick;
* fetch or pull;
* update local refs;
* push any ref;
* delete the local or remote phase branch;
* create a branch, worktree or tag;
* create a release;
* edit the PR;
* add comments, labels, reviewers, assignees or milestones;
* dismiss or submit reviews;
* trigger or rerun workflows;
* modify branch protection;
* deploy;
* enable RECIPE_LIFECYCLE_CLASSIFICATION_ENABLED;
* implement any Low or Informational finding.

Preserve the completed Phase 2F.1 branch for audit and later verification.

==================================================
9. FINAL LOCAL PRESERVATION GATE

After all GitHub operations, reverify:

* local branch remains
    phase2/recipe-lifecycle-classification;
* local HEAD remains
    6e37281e61a782ffbe8c8675346144567406dabe;
* local tree remains
    6112ddcc08fcb005d6e50daa51d8d5d1cce3e4ab;
* tracked/untracked porcelain remains empty;
* staged state remains empty;
* ignored baseline remains exact;
* no local refs, index, configuration or repository files changed.

==================================================
10. REPORT

Write exactly one report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_PR18_MERGE_2026-08-28.md

Include:

1. final merge verdict;
2. local pre-merge identity and clean-state evidence;
3. ignored-baseline evidence;
4. live pre-merge main, PR base and PR head identities;
5. final approval and review evidence;
6. required-check and SonarQube evidence;
7. exact merge request method and expected-head guard;
8. GitHub merge response;
9. merge commit SHA;
10. exact two-parent verification;
11. merge tree and PR-head tree equality;
12. final live main identity;
13. PR closed/merged state;
14. preserved source-branch identity;
15. post-merge workflow/check inventory;
16. final local preservation evidence;
17. no deployment/runtime/configuration mutation attestation;
18. exact next permitted action.

The exact next permitted action must be:

A separate independent Phase 2F.1 post-merge reverification. Phase 2F.2 implementation is not yet authorized.

If the merge and applicable post-merge workflows complete successfully, end the report and final response with exactly:

PHASE_2F1_PR18_MERGE_COMPLETE

Otherwise end with exactly one applicable token:

PHASE_2F1_PR18_MERGE_BLOCKED_WORKSPACE
PHASE_2F1_PR18_MERGE_BLOCKED_GITHUB_ACCESS
PHASE_2F1_PR18_MERGE_BLOCKED_BASE_DRIFT
PHASE_2F1_PR18_MERGE_BLOCKED_HEAD_DRIFT
PHASE_2F1_PR18_MERGE_BLOCKED_SCOPE_DRIFT
PHASE_2F1_PR18_MERGE_BLOCKED_APPROVAL
PHASE_2F1_PR18_MERGE_BLOCKED_CHECKS
PHASE_2F1_PR18_MERGE_BLOCKED_CONFLICT
PHASE_2F1_PR18_MERGE_BLOCKED_GITHUB
PHASE_2F1_PR18_MERGE_COMPLETED_IDENTITY_MISMATCH
PHASE_2F1_PR18_MERGE_COMPLETE_WORKFLOW_PENDING
PHASE_2F1_PR18_MERGE_COMPLETE_WORKFLOW_FAILED
