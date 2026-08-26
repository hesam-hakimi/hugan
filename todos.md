TASK: PHASE_2E_PR17_INDEPENDENT_POSTMERGE_REVERIFICATION

Perform one bounded, independent, read-only reverification of the completed
Phase 2E PR #17 merge and the automatically created workflow run.

This task authorizes no GitHub mutation and no repository mutation.

Repository:
TD-Enterprise/kmai-td-genie

Required logical repository root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The equivalent physical /app1 path is acceptable only if realpath proves it
is the same permanent Phase 2E worktree.

==================================================
1. WORKSPACE GATE
==================================================

Before reading reports or querying GitHub, verify:

- pwd;
- pwd -P;
- realpath;
- Git repository identity and origin;
- current branch;
- local HEAD;
- git status --porcelain=v1 --untracked-files=all.

Required local identity:

Branch:
phase2/governed-field-records

Local HEAD:
0430613e6a9f1680338d8fc099e7960e5d46cac2

Required worktree and index:
completely clean

Do not use:

- the stale primary checkout;
- branch asktd_v2;
- sibling repositories;
- ETL or UCA workspaces;
- temporary worktrees;
- the Windows/ETL Coding Agent session.

Do not fetch, pull, switch, reset, stash, clean, merge, rebase,
cherry-pick, push, or modify Git configuration.

If the workspace is incorrect or dirty, stop and end with:

PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_WORKSPACE

==================================================
2. REQUIRED MERGE REPORT
==================================================

Read this report completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_MERGE_2026-08-26.md

Verify its SHA-256 is:

ad9aa8a902b2390e6a083b964d547c5691cac31f78652df948913dac1e67e875

Use the report only as an evidence index. Independently verify all decisive
values against current live GitHub state.

Do not read unrelated reports or repositories.

==================================================
3. GITHUB ACCESS AND MUTATION PROHIBITION
==================================================

Use only existing authenticated GitHub access.

All GitHub operations must be read-only.

Do not:

- merge, close, reopen, or edit any PR;
- add comments, labels, reviewers, or approvals;
- create, delete, or modify branches;
- push or force-push;
- trigger, rerun, cancel, or approve a workflow;
- modify repository settings or branch protection;
- log in, log out, or repair authentication;
- print or persist credentials.

If authenticated read access is unavailable, stop and end with:

PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_GITHUB_ACCESS

==================================================
4. INDEPENDENTLY VERIFY MAIN AND PR #17
==================================================

Verify current live main SHA is exactly:

f283f01b6d615f9fa00debcef959d9c5c86a3224

Verify PR #17:

- state: closed;
- merged: true;
- Draft: false;
- base branch: main;
- head branch:
  phase2/governed-field-records
- accepted head SHA:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- merge commit:
  f283f01b6d615f9fa00debcef959d9c5c86a3224
- commits: exactly 1;
- changed files: exactly 12;
- additions/deletions: exactly +1760/-18;
- reviews/approvals: exactly 1/1;
- no branch deletion;
- no post-merge force-push;
- no unexpected PR edit.

Independently obtain and compare the exact twelve-file inventory with the
merge report.

If main, PR identity, head, or scope differs, stop and end with:

PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_IDENTITY_DRIFT

==================================================
5. VERIFY THE MERGE COMMIT
==================================================

Independently verify merge commit:

f283f01b6d615f9fa00debcef959d9c5c86a3224

Required properties:

- it is the current live main SHA;
- it has exactly two parents;
- first parent:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- second parent:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- second parent is the exact accepted PR #17 candidate;
- the merge was not squash or rebase;
- the accepted Phase 2E head is an ancestor of current main;
- current main contains no unexpected commit after the merge.

Verify using at least two independent live GitHub surfaces where possible.

If any property differs, stop and end with:

PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_MERGE_INVALID

==================================================
6. VERIFY THE ACCEPTED PARENT CHAIN
==================================================

Verify:

PR #15:

- closed;
- merged;
- merge commit:
  9db7e6b86c596bdf613f3180c2a1c927625233a1

PR #16:

- closed;
- merged;
- accepted head:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- merge commit:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
- exactly 9 files;
- exactly +1431/-6.

Verify PR #15 and PR #16 were not modified by the PR #17 merge.

Verify all three branches still exist at their expected SHAs:

phase2/provider-abstraction-foundation:
d5472ae31081879329c224922244d87962737e8c

phase2/approved-recipe-pilot:
5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

phase2/governed-field-records:
0430613e6a9f1680338d8fc099e7960e5d46cac2

Do not delete or modify them.

==================================================
7. VERIFY AUTOMATIC WORKFLOW RUN
==================================================

Independently inspect the workflow run automatically created by the merge:

Workflow run ID:
32974122120

Expected trigger:

- event: pull_request;
- head branch:
  phase2/governed-field-records
- head SHA:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- run attempt: 1;
- it was automatically created as a consequence of the authorized merge.

The merge report observed three checks:

1. determine-environment
   Previously completed successfully.

2. build-payload (prod)
   Previously completed successfully.

3. build-and-publish (prod, snapshot-cycle)
   Previously in progress.

Obtain the current final workflow and job/check conclusions.

If the workflow is still running, use bounded read-only polling only.
Do not wait indefinitely and do not rerun, cancel, approve, or modify it.

Classify the result as exactly one of:

A. WORKFLOW_SUCCESS
   The workflow and every required job/check completed successfully.

B. WORKFLOW_FAILED
   At least one job/check failed, was cancelled, timed out, or concluded
   unsuccessfully.

C. WORKFLOW_PENDING
   The workflow remains queued or in progress after bounded observation.

If WORKFLOW_FAILED:

- record the exact failing job and conclusion;
- capture its failure summary using read-only access;
- do not implement a fix;
- do not rerun it;
- end with:
  PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_WORKFLOW_FAILED

If WORKFLOW_PENDING, do not treat the merge itself as invalid, but stop
before authorizing documentation finalization and end with:

PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_WORKFLOW_PENDING

==================================================
8. VERIFY LOCAL NO-CHANGE STATE
==================================================

Confirm that:

- local branch remains phase2/governed-field-records;
- local HEAD remains:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- worktree and index remain clean;
- no untracked file exists;
- no local ref changed;
- no tracked repository file changed;
- Git configuration remains unchanged;
- no repository file was created, modified, or deleted.

Do not update local main or fetch remote state.

==================================================
9. REPORT
==================================================

Create exactly one report outside the Git repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_POSTMERGE_REVERIFICATION_2026-08-26.md

Include:

1. final verdict;
2. workspace and clean-state evidence;
3. merge report identity and SHA-256 verification;
4. current live main SHA;
5. PR #17 complete current identity;
6. exact twelve-file and +1760/-18 verification;
7. merge-commit two-parent verification;
8. candidate ancestry proof;
9. PR #15 and PR #16 untouched verification;
10. branch-preservation evidence;
11. workflow run ID, trigger, status, conclusion, and all job conclusions;
12. confirmation that no workflow action was taken;
13. local and repository no-change attestation;
14. exact next permitted action.

If every gate passes and the automatic workflow completes successfully,
the exact next permitted action is:

- update the authoritative AskTD/askAlpha phase-status, roadmap, decision,
  handoff, and continuation documents;
- record Phase 2E as fully merged and verified;
- separately determine and authorize the Phase 2F implementation scope.

Do not update those documents in this task.

End with exactly one terminal token:

PHASE_2E_POSTMERGE_REVERIFICATION_COMPLETE

or:

PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_WORKSPACE
PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_GITHUB_ACCESS
PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_IDENTITY_DRIFT
PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_MERGE_INVALID
PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_WORKFLOW_FAILED
PHASE_2E_POSTMERGE_REVERIFICATION_BLOCKED_WORKFLOW_PENDING
