TASK: PHASE_2E_PR17_POST_PR16_MERGE_VERIFICATION_AND_RETARGET

Perform one bounded post-merge verification and, only if every gate passes,
retarget PR #17 from its stacked Phase 2D base to main.

Repository:
TD-Enterprise/kmai-td-genie

Required logical repository root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The equivalent physical /app1 path is acceptable only if realpath proves it
is the same permanent Phase 2E worktree.

This task authorizes exactly one GitHub mutation:

    Change PR #17 base branch from:
        phase2/approved-recipe-pilot
    to:
        main

No other mutation is authorized.

==================================================
1. WORKSPACE GATE
==================================================

Before reading repository files, verify:

- pwd;
- pwd -P;
- realpath of the required logical root;
- Git repository identity and origin;
- current branch;
- current HEAD;
- git status --porcelain.

Required local identity:

Branch:
phase2/governed-field-records

HEAD:
0430613e6a9f1680338d8fc099e7960e5d46cac2

The worktree and index must be completely clean.

Do not inspect or use:

- the stale primary checkout;
- branch asktd_v2;
- sibling repositories;
- ETL/UCA workspaces;
- temporary worktrees.

Do not fetch, pull, switch branches, reset, stash, clean, merge, rebase,
cherry-pick, push, or alter Git configuration.

If identity or cleanliness differs, stop without mutation and end with:

PHASE_2E_PR17_RETARGET_BLOCKED_WORKSPACE

==================================================
2. REQUIRED PRIOR EVIDENCE
==================================================

Read this report completely before any live GitHub query:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2D_PR16_MERGE_2026-08-25.md

Use it only as an evidence index. Independently reverify every decisive live
value.

Do not read unrelated reports or repository files.

==================================================
3. VERIFY PR #16 POST-MERGE STATE
==================================================

Independently verify live PR #16:

- state: closed;
- merged: true;
- base: main;
- head branch: phase2/approved-recipe-pilot;
- head SHA:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- changed files: exactly 9;
- additions/deletions: exactly +1431/-6;
- merge-commit SHA:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c

Verify that the merge commit:

- is the current live main SHA;
- has exactly two parents;
- first parent is:
  9db7e6b86c596bdf613f3180c2a1c927625233a1
- second parent is:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- is a genuine merge commit, not squash or rebase;
- contains the exact accepted PR #16 candidate.

If any value differs, stop without changing PR #17 and end with:

PHASE_2E_PR17_RETARGET_BLOCKED_POSTMERGE_IDENTITY

==================================================
4. VERIFY PR #17 BEFORE RETARGETING
==================================================

Independently verify live PR #17:

- state: open;
- Draft: true;
- merged: false;
- base branch:
  phase2/approved-recipe-pilot
- head branch:
  phase2/governed-field-records
- exact head SHA:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- the Phase 2E commit is based on the accepted PR #16 candidate;
- changed files: exactly 12;
- additions/deletions: exactly +1760/-18;
- reviews/approvals: 0/0;
- issue comments and review comments: 0/0;
- no force-push;
- no candidate drift;
- no ready-for-review transition;
- no unexpected base change;
- no merge conflict.

The previous report established that closing PR #16 changed embedded repository
metadata such as repository counters and pushed_at. These are not PR #17 field
changes.

Compare PR #17 using a PR-scoped canonical digest that excludes embedded
repository-wide mutable metadata. Do not treat the already documented
repository-counter side effect as PR #17 drift.

Verify that these remote branches still exist:

- phase2/provider-abstraction-foundation
- phase2/approved-recipe-pilot
- phase2/governed-field-records

Do not delete any branch.

If PR #17 identity or scope differs, stop without mutation and end with:

PHASE_2E_PR17_RETARGET_BLOCKED_CANDIDATE_DRIFT

==================================================
5. ONLY AUTHORIZED MUTATION
==================================================

Only after sections 1–4 pass, change PR #17’s base branch from:

    phase2/approved-recipe-pilot

to:

    main

Use an authenticated GitHub API operation that changes only the base branch.

Do not:

- modify or push the head branch;
- rebase or merge locally;
- edit title or description;
- mark the PR ready for review;
- request a reviewer;
- submit a review or approval;
- create a comment;
- add labels, assignees, or milestones;
- close, reopen, or merge the PR;
- trigger or rerun a workflow;
- modify PR #15 or PR #16;
- delete any branch.

==================================================
6. POST-RETARGET VERIFICATION
==================================================

After the base change, independently verify:

- PR #17 remains open;
- Draft remains true;
- merged remains false;
- base is now main;
- base SHA is the verified PR #16 merge commit:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- head branch remains phase2/governed-field-records;
- head SHA remains:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- changed files remain exactly 12;
- additions/deletions remain exactly +1760/-18;
- reviews and approvals remain zero;
- no ready-for-review transition occurred;
- no head commit changed;
- no conflict exists;
- mergeability resolves successfully.

GitHub may temporarily report mergeability as unknown/null. Use bounded,
read-only polling. Do not perform a second mutation.

Also verify:

- main remains at:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- PR #16 remains closed and merged;
- PR #15 remains closed and merged;
- all three remote phase branches still exist;
- the local branch, HEAD, refs, index, tracked files, and Git configuration are
  unchanged;
- git status --porcelain remains empty.

Record whether the base change created a check or workflow run. Do not trigger
one manually.

If the post-retarget scope is not exactly 12 files and +1760/-18, or another
candidate property changed, stop and end with:

PHASE_2E_PR17_RETARGET_BLOCKED_POSTCHANGE_VALIDATION

Do not automatically undo or compensate for the base change. Report the exact
live state.

==================================================
7. REPORT
==================================================

Create exactly one report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_RETARGET_2026-08-25.md

Include:

1. workspace identity and clean-state evidence;
2. PR #16 post-merge verification;
3. exact current main SHA;
4. merge-commit parent verification;
5. PR #17 complete pre-retarget state;
6. PR-scoped metadata digest and repository-counter exclusion;
7. exact single GitHub mutation;
8. PR #17 complete post-retarget state;
9. twelve-file inventory and +1760/-18 totals;
10. mergeability and conflict state;
11. workflow/check state before and after;
12. confirmation that PR #15 and PR #16 were untouched;
13. branch-preservation evidence;
14. local and repository no-change attestation;
15. exact next permitted action.

After successful retargeting, the next permitted action is only:

- mark PR #17 ready for review;
- obtain one eligible non-author approval;
- reverify its exact head SHA and 12-file / +1760/-18 scope;
- merge it using a merge commit.

Those actions are not authorized by this task.

End with exactly one terminal token:

PHASE_2E_PR17_RETARGET_COMPLETE

or one applicable BLOCKED token defined above.
