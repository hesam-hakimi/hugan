TASK: PHASE_2E_PR17_FINAL_VERIFICATION_AND_MERGE_COMMIT

Perform one bounded final verification and, only if every gate passes,
merge PR #17 into main using a genuine merge commit.

Repository:
TD-Enterprise/kmai-td-genie

Required logical repository root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The equivalent physical /app1 path is acceptable only if realpath proves
that it identifies the same permanent Phase 2E worktree.

This task authorizes exactly one GitHub mutation:

    Merge PR #17 into main using merge method: merge

Squash and rebase are prohibited.

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
- current local HEAD;
- git status --porcelain=v1 --untracked-files=all.

Required local identity:

Branch:
phase2/governed-field-records

HEAD:
0430613e6a9f1680338d8fc099e7960e5d46cac2

Required worktree and index:
completely clean

Do not inspect or use:

- the stale primary checkout;
- branch asktd_v2;
- sibling repositories;
- ETL or UCA workspaces;
- temporary worktrees;
- the Windows/ETL Coding Agent session.

Do not fetch, pull, switch branches, reset, stash, clean, merge, rebase,
cherry-pick, push, or modify Git configuration.

If workspace identity or cleanliness differs, stop without mutation and
end with:

PHASE_2E_PR17_MERGE_BLOCKED_WRONG_WORKSPACE

==================================================
2. REQUIRED PRIOR EVIDENCE
==================================================

Read this report completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_READY_FOR_REVIEW_2026-08-25.md

Also read this report completely to verify the accepted base history:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_RETARGET_2026-08-25.md

Use both reports only as evidence indexes. Independently verify every
decisive value against live GitHub state.

Do not read unrelated reports or repositories.

==================================================
3. GITHUB ACCESS
==================================================

Use only the existing authenticated GitHub access available in the
environment.

Do not:

- log in or log out;
- repair authentication;
- alter credential files;
- print or persist credentials;
- modify Git configuration.

Every GitHub request before section 7 must be read-only.

If authenticated GitHub access is unavailable, stop without mutation and
end with:

PHASE_2E_PR17_MERGE_BLOCKED_GITHUB_ACCESS

==================================================
4. VERIFY CURRENT MAIN AND ACCEPTED PARENT CHAIN
==================================================

Independently verify live GitHub state.

Current main SHA must be exactly:

409fed3fb98fc87547a7d05a68292fc28c3c1e7c

PR #16 must remain:

- state: closed;
- merged: true;
- base: main;
- head branch: phase2/approved-recipe-pilot;
- accepted head SHA:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- merge commit:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- changed files: exactly 9;
- additions/deletions: exactly +1431/-6.

Verify the PR #16 merge commit:

- has exactly two parents;
- first parent:
  9db7e6b86c596bdf613f3180c2a1c927625233a1
- second parent:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- is a genuine merge commit;
- is still the current pre-merge main SHA.

PR #15 must remain closed and merged.

If main or the accepted parent chain has changed, stop without merging
PR #17, report the exact drift, and end with:

PHASE_2E_PR17_MERGE_BLOCKED_MAIN_DRIFT

==================================================
5. VERIFY PR #17 CANDIDATE
==================================================

Independently verify live PR #17:

- state: open;
- Draft: false;
- merged: false;
- base branch: main;
- current base SHA:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- head branch:
  phase2/governed-field-records
- exact head SHA:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- exactly one commit;
- head commit parent:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- changed files: exactly 12;
- additions/deletions: exactly +1760/-18;
- mergeable: true / MERGEABLE;
- no merge conflict;
- the authorized retarget from phase2/approved-recipe-pilot to main is
  present;
- the authorized ready-for-review transition is present;
- no force-push or candidate drift occurred;
- no unresolved change request exists.

Verify the exact twelve-file inventory remains identical to the
ready-for-review and retarget reports.

The PR description may still describe the historical stacked-PR
relationship. Treat that as historical text only. Do not edit the title or
description during this task.

If candidate identity, scope, base, head, commit, or conflict state differs,
stop without merging and end with:

PHASE_2E_PR17_MERGE_BLOCKED_CANDIDATE_DRIFT

==================================================
6. VERIFY APPROVAL, CHECKS, AND POLICY
==================================================

Verify that PR #17 has at least one current eligible approving review from
a non-author with the repository access required by branch protection.

Expected visible evidence:

Author:
tag5916_tdbank

Approving reviewer:
tar2859_tdbank

Verify:

- reviewer is not the PR author;
- review state is APPROVED;
- reviewer has write access or otherwise satisfies the repository policy;
- approval applies to the current exact head SHA:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- approval was not dismissed;
- no commit was added after approval;
- no later CHANGES_REQUESTED review overrides it;
- reviewDecision is APPROVED or its live equivalent;
- branch-protection review requirement is satisfied;
- GitHub reports “Changes approved” or the live API equivalent;
- no required check is pending or failing;
- zero check runs is acceptable only if main has zero required status
  contexts and GitHub reports the PR as ready to merge;
- GitHub reports no conflicts with the base branch.

If approval is stale, dismissed, ineligible, insufficient, or does not apply
to the current head, stop without merge and end with:

PHASE_2E_PR17_MERGE_BLOCKED_APPROVAL_INVALID

If a required check or branch-protection gate is pending or failing, stop
without mutation and end with:

PHASE_2E_PR17_MERGE_BLOCKED_POLICY

==================================================
7. RECORD PRE-MERGE PRESERVATION EVIDENCE
==================================================

Before the merge, record normalized live metadata for:

- PR #15;
- PR #16;
- PR #17;
- current main;
- the three Phase branches.

Verify these remote branches exist and do not delete them:

- phase2/provider-abstraction-foundation
- phase2/approved-recipe-pilot
- phase2/governed-field-records

Create a deterministic PR-scoped digest for the relevant PR #17 metadata.
Exclude embedded repository-wide mutable counters and timestamps that may
legitimately change when a PR is merged.

Record:

- exact twelve-file inventory;
- additions/deletions;
- current review identity;
- current checks;
- head and base identity;
- issue-comment and review-comment counts;
- branch existence.

==================================================
8. ONLY AUTHORIZED MUTATION
==================================================

Only after sections 1–7 pass, merge PR #17 through the GitHub API using:

- expected head SHA:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- merge method:
  merge

The operation must create a genuine two-parent merge commit.

Do not use:

- squash;
- rebase;
- local Git merge;
- command-line push;
- force-push.

Do not:

- edit the PR title or description;
- add a comment or label;
- request or submit another review;
- change the base or head;
- close the PR without merge;
- delete any branch;
- modify PR #15 or PR #16;
- trigger or rerun a workflow manually;
- edit any repository file;
- change any local branch, ref, configuration, or runtime flag.

If GitHub rejects the merge, do not retry using another merge method and do
not bypass branch protection. End with:

PHASE_2E_PR17_MERGE_BLOCKED_MERGE_REJECTED

==================================================
9. POST-MERGE VERIFICATION
==================================================

After the merge, independently verify PR #17:

- state: closed;
- merged: true;
- base remains main;
- head remains phase2/governed-field-records;
- accepted head SHA remains:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- changed files remain exactly 12;
- additions/deletions remain exactly +1760/-18;
- the exact full 40-character merge-commit SHA is recorded.

Verify the new merge commit:

- is the current live main SHA;
- has exactly two parents;
- first parent is:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- second parent is:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- is therefore a genuine merge commit, not squash or rebase;
- contains the exact accepted PR #17 candidate;
- makes the Phase 2E candidate an ancestor of main.

Also verify:

- PR #15 remains closed and merged;
- PR #16 remains closed and merged;
- PR #16 merge identity remains unchanged;
- all three remote Phase branches still exist;
- no branch was deleted;
- no unauthorized comment, label, review, or PR edit occurred;
- the permanent local worktree remains clean;
- the local branch remains phase2/governed-field-records;
- local HEAD remains:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- local refs, index, tracked files, and Git configuration remain unchanged;
- git status --porcelain remains empty.

Record whether the merge automatically created a workflow or check run.
Do not trigger, rerun, cancel, or modify it.

If the merge succeeds but any post-merge evidence differs, do not attempt
rollback or compensation. Record the exact live state and end with:

PHASE_2E_PR17_MERGE_BLOCKED_POSTMERGE_VALIDATION

==================================================
10. REPORT
==================================================

Write exactly one report outside the Git repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_MERGE_2026-08-26.md

The report must include:

1. final verdict;
2. workspace identity and clean-state verification;
3. prior reports read;
4. PR #15 and PR #16 accepted-state verification;
5. exact pre-merge main SHA;
6. PR #17 exact pre-merge identity;
7. exact twelve-file inventory and +1760/-18 scope;
8. approval identity, eligibility, and current-head applicability;
9. checks, mergeability, conflict, and branch-protection state;
10. branch-preservation evidence;
11. exact single GitHub mutation performed;
12. PR #17 complete post-merge state;
13. exact merge-commit SHA;
14. exact two-parent verification;
15. proof that the candidate is an ancestor of main;
16. confirmation that PR #15 and PR #16 were untouched;
17. workflow/check state after merge;
18. local and repository no-change attestation;
19. exact next permitted action.

After successful completion, the next permitted action is only:

- independently reverify the completed Phase 2E merge;
- update the authoritative AskTD/askAlpha phase-status and handoff documents;
- determine and authorize the next implementation phase separately.

No next-phase implementation, branch deletion, or repository cleanup is
authorized by this task.

End with exactly one applicable terminal token:

PHASE_2E_PR17_MERGE_COMPLETE

or:

PHASE_2E_PR17_MERGE_BLOCKED_WRONG_WORKSPACE
PHASE_2E_PR17_MERGE_BLOCKED_GITHUB_ACCESS
PHASE_2E_PR17_MERGE_BLOCKED_MAIN_DRIFT
PHASE_2E_PR17_MERGE_BLOCKED_CANDIDATE_DRIFT
PHASE_2E_PR17_MERGE_BLOCKED_APPROVAL_INVALID
PHASE_2E_PR17_MERGE_BLOCKED_POLICY
PHASE_2E_PR17_MERGE_BLOCKED_MERGE_REJECTED
PHASE_2E_PR17_MERGE_BLOCKED_POSTMERGE_VALIDATION
