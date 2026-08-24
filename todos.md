TASK: PHASE_2D_PR16_POST_PR15_MERGE_VERIFICATION_AND_RETARGET

Perform one bounded post-merge verification and, only if every gate passes,
retarget PR #16 from its current stacked base to main.

Repository:
TD-Enterprise/kmai-td-genie

Required logical repository root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The equivalent physical path under /app1 is acceptable only if realpath proves
that it is the same permanent Phase 2E worktree.

This task authorizes exactly one GitHub mutation:

    Change PR #16 base branch from:
        phase2/provider-abstraction-foundation
    to:
        main

No other mutation is authorized.

==================================================
1. MANDATORY WORKSPACE GATE
==================================================

Before reading any repository file, verify:

- pwd;
- pwd -P;
- realpath of the required logical root;
- current repository identity;
- current branch and HEAD;
- git status --porcelain.

The active workspace must resolve to the permanent Phase 2E repository root.

Do not read, search, inspect, or modify:

- the stale primary checkout;
- branch asktd_v2;
- sibling repositories;
- ETL/UCA workspaces;
- /tmp worktrees.

If the workspace does not match, stop without mutation and end with:

PHASE_2D_PR16_RETARGET_BLOCKED_WRONG_WORKSPACE

Do not change branches, fetch, pull, reset, stash, clean, rebase, merge,
cherry-pick, or modify Git configuration.

==================================================
2. PERMITTED PRIOR EVIDENCE
==================================================

Read these reports completely, from outside the Git repository:

1.
/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR_STACK_READINESS_2026-08-23.md

2.
/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_FINALIZATION_2026-08-23.md

Treat them as evidence indexes only. Independently verify all decisive live
values.

Do not read unrelated reports, the stale checkout, Library exports, or Phase 2F
decision documents.

==================================================
3. AUTHENTICATION AND SAFETY
==================================================

Use authenticated GitHub read access already available in the environment.

If the stored gh account token is invalid, do not repair it, log in, log out,
rewrite hosts.yml, print credentials, or persist a token.

You may use the same existing credential-helper-based method that previously
authorized GitHub reads and the PR #17 push/creation.

Never print, copy, save, or expose any credential.

All GitHub requests before section 6 must be read-only.

If authenticated access is unavailable, stop without mutation and end with:

PHASE_2D_PR16_RETARGET_BLOCKED_GITHUB_ACCESS

==================================================
4. VERIFY PR #15 POST-MERGE STATE
==================================================

Independently query the live GitHub state and verify:

PR #15:

- state: closed;
- merged: true;
- base branch: main;
- head branch: phase2/provider-abstraction-foundation;
- original candidate head SHA exactly:

  d5472ae31081879329c224922244d87962737e8c

- changed files: exactly 7;
- additions/deletions: exactly +430/-28;
- at least one eligible non-author approval exists;
- the five previously reported checks succeeded;
- exact full merge-commit SHA is obtained from GitHub.

Verify the merge commit:

- is the current live main SHA;
- has exactly two parents;
- first parent is the previous main:

  9ca6567571772a9f4e1ab555d8a678e678c45d49

- second parent is the accepted Phase 2C.5 candidate:

  d5472ae31081879329c224922244d87962737e8c

- therefore Phase 2C.5 was merged using a merge commit, not squash or rebase;
- d5472ae31081879329c224922244d87962737e8c is now an ancestor of main.

Do not silently trust the short SHA shown in the browser. Record the exact
40-character merge SHA.

If any value differs, stop without changing PR #16 and end with:

PHASE_2D_PR16_RETARGET_BLOCKED_POSTMERGE_IDENTITY

==================================================
5. VERIFY PR #16 BEFORE RETARGETING
==================================================

Verify live PR #16 before making any mutation:

- state: open;
- Draft: true;
- merged: false;
- base branch:

  phase2/provider-abstraction-foundation

- head branch:

  phase2/approved-recipe-pilot

- exact head SHA:

  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

- the head commit has the accepted Phase 2C.5 candidate as its single parent:

  d5472ae31081879329c224922244d87962737e8c

- changed files: exactly 9;
- additions/deletions: exactly +1431/-6;
- no merge conflict;
- no unexpected review, comment, head-force-push, base change, or candidate
  drift has occurred.

Also verify that the remote branch
phase2/provider-abstraction-foundation still exists.

Do not delete that branch. It must remain until PR #16 has been successfully
retargeted and verified.

If PR #16 does not match every expected identity and scope value, stop without
mutation and end with:

PHASE_2D_PR16_RETARGET_BLOCKED_CANDIDATE_DRIFT

==================================================
6. THE ONLY AUTHORIZED MUTATION
==================================================

Only after sections 1–5 pass, change PR #16’s base branch from:

    phase2/provider-abstraction-foundation

to:

    main

Use the GitHub API or another authenticated GitHub mechanism that performs only
this base change.

Do not:

- modify PR #16’s head;
- push or force-push;
- rebase or merge locally;
- edit its title or description;
- mark it ready for review;
- request a reviewer;
- submit an approval;
- add a comment, label, milestone, or assignee;
- close, reopen, or merge it;
- trigger a workflow deliberately;
- delete either parent branch;
- modify PR #15 or PR #17.

==================================================
7. POST-RETARGET VERIFICATION
==================================================

After the base change, independently re-read PR #16 and verify:

- state remains open;
- Draft remains true;
- base is now main;
- head remains phase2/approved-recipe-pilot;
- head SHA remains exactly:

  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

- changed files remain exactly 9;
- additions/deletions remain exactly +1431/-6;
- mergeable is true;
- merge state is clean, or its equivalent indicates no conflict;
- no head commit changed;
- no approval was submitted;
- no ready-for-review transition occurred.

GitHub may temporarily return mergeability as unknown/null while recalculating.
Use bounded read-only polling. If it remains unresolved, report it as a blocker;
do not make another mutation.

Verify additionally:

- current main SHA is still the exact PR #15 merge commit obtained in section 4;
- PR #15 remains merged;
- PR #17 remains untouched with:
  - state open;
  - Draft true;
  - base phase2/approved-recipe-pilot;
  - head phase2/governed-field-records;
  - exact head SHA:

    0430613e6a9f1680338d8fc099e7960e5d46cac2

- phase2/provider-abstraction-foundation still exists;
- phase2/approved-recipe-pilot still exists;
- the permanent worktree/index remains clean;
- no repository file or local Git ref changed.

Record whether retargeting created any check or workflow run, but do not trigger
one manually. Zero new checks is not, by itself, candidate drift because the
current pull_request workflow does not listen for the base-change edited event.

If the post-retarget scope is not exactly 9 files and +1431/-6, or any other
identity changed, stop and end with:

PHASE_2D_PR16_RETARGET_BLOCKED_POSTCHANGE_VALIDATION

Do not attempt to undo or compensate automatically. Report the exact live state.

==================================================
8. REPORT
==================================================

Write one report outside the Git repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2D_PR16_RETARGET_2026-08-24.md

The report must include:

1. exact workspace and no-change attestation;
2. exact PR #15 merge commit and both parents;
3. verified current main SHA;
4. PR #15 final approval/check/merge evidence;
5. PR #16 complete before-retarget state;
6. the exact single mutation performed;
7. PR #16 complete after-retarget state;
8. changed-file inventory/count and additions/deletions;
9. mergeability and conflict state;
10. check/workflow state before and after;
11. confirmation that PR #17 was untouched;
12. confirmation that no parent branch was deleted;
13. confirmation that no repository file, commit, branch head, runtime flag, or
    Git configuration was changed;
14. exact next permitted action.

The next permitted action after a successful report is only:

- mark PR #16 ready for review;
- obtain its one eligible non-author approval;
- reverify its exact head and 9-file scope;
- then merge it using a merge commit.

Those actions are not authorized by this prompt.

End with exactly one terminal token:

PHASE_2D_PR16_RETARGET_COMPLETE

or one applicable BLOCKED token defined above.
