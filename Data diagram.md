TASK: PHASE_2D_PR16_MARK_READY_FOR_REVIEW

Perform one bounded verification and, only if every identity gate passes,
mark PR #16 ready for review.

Repository:
TD-Enterprise/kmai-td-genie

Required workspace:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

Equivalent /app1 physical path is acceptable only when realpath proves it is
the same permanent worktree.

This task authorizes exactly one GitHub mutation:

    Convert PR #16 from Draft to Ready for review.

No other mutation is authorized.

==================================================
1. WORKSPACE AND EVIDENCE GATE
==================================================

Verify:

- pwd, pwd -P, and realpath;
- repository remote identity;
- current branch:
  phase2/governed-field-records
- local HEAD:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- git status --porcelain is clean.

Read completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2D_PR16_RETARGET_2026-08-24.md

Do not use the stale primary checkout, asktd_v2, sibling repositories,
ETL/UCA workspaces, or temporary worktrees.

Do not fetch, pull, switch branches, reset, stash, clean, merge, rebase,
cherry-pick, or change Git configuration.

If identity or cleanliness differs, stop without mutation and report:

PHASE_2D_PR16_READY_BLOCKED_WRONG_WORKSPACE

==================================================
2. LIVE PRE-MUTATION VERIFICATION
==================================================

Using existing authenticated GitHub access, independently verify:

PR #15:

- state: closed;
- merged: true;
- base: main;
- merge-commit SHA:
  9db7e6b86c596bdf613f3180c2a1c927625233a1

Current main SHA must still equal that merge commit.

PR #16:

- state: open;
- Draft: true;
- merged: false;
- base: main;
- head branch:
  phase2/approved-recipe-pilot
- exact head SHA:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- changed files: exactly 9;
- additions/deletions: exactly +1431/-6;
- mergeable: true;
- no merge conflict;
- zero approvals;
- review requirement is the only policy blocker.

PR #17:

- state: open;
- Draft: true;
- base:
  phase2/approved-recipe-pilot
- head:
  phase2/governed-field-records
- exact head SHA:
  0430613e6a9f1680338d8fc099e7960e5d46cac2

Also verify both remote branches still exist:

- phase2/provider-abstraction-foundation
- phase2/approved-recipe-pilot

If any expected identity or PR #16 scope differs, stop without mutation and
report:

PHASE_2D_PR16_READY_BLOCKED_CANDIDATE_DRIFT

==================================================
3. ONLY AUTHORIZED MUTATION
==================================================

Mark PR #16 ready for review.

Do not:

- change its base or head;
- push or force-push;
- edit title or description;
- request or add a reviewer;
- submit a review or approval;
- comment, label, assign, close, or merge the PR;
- change PR #15 or PR #17;
- delete any branch;
- modify any repository file or local Git ref;
- enable any runtime flag.

==================================================
4. POST-MUTATION VERIFICATION
==================================================

Re-read the live PR state and verify:

- PR #16 remains open;
- Draft is now false;
- base remains main;
- head branch remains phase2/approved-recipe-pilot;
- head SHA remains:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- changed files remain exactly 9;
- additions/deletions remain exactly +1431/-6;
- mergeable remains true;
- no conflict exists;
- no approval was submitted;
- review remains required until an eligible non-author approves;
- PR #15 remains merged;
- PR #17 remains byte-identical in GitHub metadata;
- both parent branches still exist;
- local HEAD and clean status remain unchanged.

Record any automatically triggered workflow/check runs. Do not trigger,
rerun, cancel, or modify a workflow manually.

==================================================
5. REPORT
==================================================

Create exactly one report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2D_PR16_READY_FOR_REVIEW_2026-08-24.md

Include:

1. workspace and clean-state verification;
2. PR #15 and current main identity;
3. PR #16 state before mutation;
4. exact single mutation performed;
5. PR #16 state after mutation;
6. unchanged head SHA and 9-file / +1431/-6 scope;
7. mergeability, review, and workflow/check state;
8. PR #17 untouched confirmation;
9. branch-preservation confirmation;
10. repository no-change attestation;
11. exact next action:
    obtain one eligible non-author approval for PR #16, then reverify the
    candidate before merge.

Do not approve or merge PR #16 during this task.

End with exactly one applicable token:

PHASE_2D_PR16_READY_FOR_REVIEW_COMPLETE

or:

PHASE_2D_PR16_READY_BLOCKED_WRONG_WORKSPACE
PHASE_2D_PR16_READY_BLOCKED_GITHUB_ACCESS
PHASE_2D_PR16_READY_BLOCKED_CANDIDATE_DRIFT
PHASE_2D_PR16_READY_BLOCKED_POSTCHANGE_VALIDATION
