TASK: PHASE_2E_PR17_MARK_READY_FOR_REVIEW

Perform one bounded verification and, only if every gate passes, convert PR #17
from Draft to Ready for Review.

Repository:
TD-Enterprise/kmai-td-genie

Required logical repository root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The equivalent physical /app1 path is acceptable only if realpath proves it is
the same permanent Phase 2E worktree.

This task authorizes exactly one GitHub mutation:

    Mark PR #17 ready for review.

No other mutation is authorized.

==================================================
1. WORKSPACE GATE
==================================================

Before reading repository files or reports, verify:

- pwd;
- pwd -P;
- realpath of the required logical root;
- Git repository identity and origin;
- current branch;
- current HEAD;
- git status --porcelain.

Required identity:

Branch:
phase2/governed-field-records

HEAD:
0430613e6a9f1680338d8fc099e7960e5d46cac2

The worktree and index must be completely clean.

Do not use or inspect:

- the stale primary checkout;
- branch asktd_v2;
- sibling repositories;
- ETL/UCA workspaces;
- temporary worktrees.

Do not fetch, pull, switch branches, reset, stash, clean, merge, rebase,
cherry-pick, push, or modify Git configuration.

If identity or cleanliness differs, stop without mutation and end with:

PHASE_2E_PR17_READY_FOR_REVIEW_BLOCKED_WORKSPACE

==================================================
2. REQUIRED PRIOR EVIDENCE
==================================================

Read this report completely before the first live GitHub query:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_RETARGET_2026-08-25.md

Use it only as an evidence index. Independently verify every decisive live value.

Do not read unrelated reports or repository files.

==================================================
3. VERIFY MAIN AND PR #16
==================================================

Independently verify:

Current main SHA:
409fed3fb98fc87547a7d05a68292fc28c3c1e7c

PR #16:

- state: closed;
- merged: true;
- base: main;
- head: phase2/approved-recipe-pilot;
- head SHA:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- merge commit:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- changed files: 9;
- additions/deletions: +1431/-6.

If main or PR #16 differs, stop without changing PR #17 and end with:

PHASE_2E_PR17_READY_FOR_REVIEW_BLOCKED_BASE_DRIFT

==================================================
4. VERIFY PR #17 BEFORE MUTATION
==================================================

Independently verify live PR #17:

- state: open;
- Draft: true;
- merged: false;
- base branch: main;
- base SHA:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- head branch:
  phase2/governed-field-records
- exact head SHA:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- exactly one commit;
- the head commit’s parent is:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- changed files: exactly 12;
- additions/deletions: exactly +1760/-18;
- reviews/approvals: 0/0;
- issue comments/review comments: 0/0;
- requested reviewers/teams: 0/0;
- no force-push;
- no unexpected base change after the authorized retarget;
- no ready-for-review event yet;
- mergeable: true / MERGEABLE;
- no merge conflict.

`mergeStateStatus: BLOCKED` or `REVIEW_REQUIRED` is expected before this mutation
because PR #17 is still Draft and has no approval. Do not treat that policy state
as a merge conflict.

Verify the exact twelve-file inventory remains identical to the retarget report.

Also verify all three branches still exist:

- phase2/provider-abstraction-foundation
- phase2/approved-recipe-pilot
- phase2/governed-field-records

If any candidate or scope value differs, stop without mutation and end with:

PHASE_2E_PR17_READY_FOR_REVIEW_BLOCKED_CANDIDATE_DRIFT

==================================================
5. ONLY AUTHORIZED MUTATION
==================================================

Only after sections 1–4 pass, mark PR #17 ready for review using GitHub’s dedicated
GraphQL ready-for-review mutation or an equivalent operation that changes only
Draft status.

Do not:

- edit the PR title or description;
- change base or head;
- push or force-push;
- request a reviewer or team;
- submit a review or approval;
- create a comment;
- add a label, assignee, project, or milestone;
- trigger or rerun a workflow;
- close, reopen, or merge the PR;
- modify PR #15 or PR #16;
- delete any branch;
- modify a repository file or local Git state.

==================================================
6. POST-MUTATION VERIFICATION
==================================================

After the mutation, independently verify:

- PR #17 remains open;
- Draft is now false;
- merged remains false;
- base remains main;
- base SHA remains:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- head branch remains phase2/governed-field-records;
- head SHA remains:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- changed files remain exactly 12;
- additions/deletions remain exactly +1760/-18;
- reviews/approvals remain 0/0;
- no reviewer or team was requested;
- no comment was added;
- exactly one new ready-for-review timeline event exists;
- no force-push or head change occurred;
- mergeable remains true with no conflict.

Record whether the transition created a workflow or check run. Do not trigger,
rerun, cancel, or modify one manually.

Also verify:

- main remains unchanged;
- PR #15 and PR #16 remain closed and merged;
- all three phase branches still exist;
- the local branch, HEAD, refs, index, tracked files, and Git configuration remain
  unchanged;
- git status --porcelain remains empty.

If any unauthorized property changed, stop and report the exact live state. Do not
attempt an automatic rollback.

End the blocked case with:

PHASE_2E_PR17_READY_FOR_REVIEW_BLOCKED_POSTCHANGE_VALIDATION

==================================================
7. REPORT
==================================================

Create exactly one report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_READY_FOR_REVIEW_2026-08-25.md

Include:

1. workspace identity and clean-state evidence;
2. prior report read;
3. main and PR #16 identity;
4. PR #17 complete pre-mutation state;
5. exact twelve-file inventory and +1760/-18 totals;
6. mergeability and conflict evidence;
7. exact single GitHub mutation;
8. PR #17 complete post-mutation state;
9. ready-for-review timeline evidence;
10. workflow/check state before and after;
11. confirmation that no reviewer or approval was added;
12. confirmation that PR #15 and PR #16 were untouched;
13. branch-preservation evidence;
14. local and repository no-change attestation;
15. exact next permitted action.

After successful completion, the next permitted action is only:

- obtain one eligible non-author approval for PR #17;
- reverify the exact head SHA and 12-file / +1760/-18 scope;
- merge PR #17 using a genuine merge commit.

Approval and merge are not authorized by this task.

End with exactly one terminal token:

PHASE_2E_PR17_READY_FOR_REVIEW_COMPLETE

or one applicable BLOCKED token defined above.
