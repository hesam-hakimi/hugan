TASK: PHASE_2D_PR16_FINAL_VERIFICATION_AND_MERGE_COMMIT

Perform one bounded final verification and, only if every gate passes,
merge PR #16 into main using a genuine merge commit.

Repository:
TD-Enterprise/kmai-td-genie

Required logical repository root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The equivalent physical /app1 path is acceptable only if realpath proves
that both paths identify the same permanent Phase 2E worktree.

This task authorizes exactly one GitHub mutation:

    Merge PR #16 into main using merge method: merge

Squash and rebase are prohibited.

No other mutation is authorized.

==================================================
1. WORKSPACE GATE
==================================================

Before reading repository files, verify:

- pwd;
- pwd -P;
- realpath of the required logical root;
- repository remote identity;
- current branch;
- current local HEAD;
- git status --porcelain.

Expected local identity:

Branch:
phase2/governed-field-records

HEAD:
0430613e6a9f1680338d8fc099e7960e5d46cac2

Expected worktree/index:
clean

Do not inspect or use:

- stale primary checkout;
- branch asktd_v2;
- sibling repositories;
- ETL/UCA workspaces;
- temporary worktrees.

Do not fetch, pull, switch branches, reset, stash, clean, merge, rebase,
cherry-pick, push, or change Git configuration.

If the workspace identity or cleanliness differs, stop without mutation
and end with:

PHASE_2D_PR16_MERGE_BLOCKED_WRONG_WORKSPACE

==================================================
2. REQUIRED PRIOR EVIDENCE
==================================================

Read this report completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2D_PR16_READY_FOR_REVIEW_2026-08-24.md

Use it as an evidence index only. Independently verify every decisive
value against live GitHub state.

Do not read unrelated reports or repositories.

==================================================
3. GITHUB ACCESS
==================================================

Use only the existing authenticated GitHub access available in the
environment.

Do not:

- log in or log out;
- repair authentication;
- modify credential files;
- print or persist credentials;
- modify Git configuration.

All GitHub requests before section 7 must be read-only.

If authenticated GitHub access is unavailable, stop without mutation and
end with:

PHASE_2D_PR16_MERGE_BLOCKED_GITHUB_ACCESS

==================================================
4. VERIFY CURRENT MAIN AND PR #15
==================================================

Verify live GitHub state:

PR #15:

- state: closed;
- merged: true;
- base: main;
- head:
  phase2/provider-abstraction-foundation
- accepted head SHA:
  d5472ae31081879329c224922244d87962737e8c
- merge commit:
  9db7e6b86c596bdf613f3180c2a1c927625233a1

Verify current live main SHA is still exactly:

9db7e6b86c596bdf613f3180c2a1c927625233a1

If current main has changed, stop without merging PR #16 and report the
exact drift:

PHASE_2D_PR16_MERGE_BLOCKED_MAIN_DRIFT

==================================================
5. VERIFY PR #16 CANDIDATE
==================================================

Independently verify PR #16:

- state: open;
- Draft: false;
- merged: false;
- base branch: main;
- base SHA:
  9db7e6b86c596bdf613f3180c2a1c927625233a1
- head branch:
  phase2/approved-recipe-pilot
- exact head SHA:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- commits: exactly 1;
- changed files: exactly 9;
- additions/deletions: exactly +1431/-6;
- mergeable: true / MERGEABLE;
- no merge conflict;
- Draft-to-ready transition is present;
- no head force-push or candidate drift occurred;
- no unresolved change request exists.

Verify the exact nine-file inventory remains unchanged.

If any candidate identity, commit, scope, base, head, or conflict value
differs, stop without merge and end with:

PHASE_2D_PR16_MERGE_BLOCKED_CANDIDATE_DRIFT

==================================================
6. VERIFY APPROVAL AND POLICY
==================================================

Verify that PR #16 has at least one current eligible approving review
from a non-author with the required repository access.

Expected evidence currently visible:

Author:
tag5916_tdbank

Approving reviewer:
tar2859_tdbank

Verify:

- reviewer is not the PR author;
- review state is APPROVED;
- approval applies to the current exact head SHA;
- approval was not dismissed;
- no later CHANGES_REQUESTED review overrides it;
- reviewDecision is APPROVED or its live equivalent;
- branch-protection review requirement is satisfied;
- no required check is pending or failing;
- zero check runs is acceptable only if main has zero required status
  contexts and GitHub reports the PR as merge-ready.

If approval or policy evidence is invalid, stale, dismissed, or
insufficient, stop without merge and end with:

PHASE_2D_PR16_MERGE_BLOCKED_APPROVAL_INVALID

==================================================
7. VERIFY PR #17 BEFORE MERGE
==================================================

Record the complete normalized live metadata for PR #17.

Expected state:

- state: open;
- Draft: true;
- merged: false;
- base:
  phase2/approved-recipe-pilot
- head:
  phase2/governed-field-records
- head SHA:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- changed files: exactly 12;
- additions/deletions: exactly +1760/-18;
- reviews/approvals: 0/0.

Create a deterministic digest of the complete relevant PR #17 metadata
so it can be compared after the merge.

Verify these remote branches exist and do not delete them:

- phase2/provider-abstraction-foundation
- phase2/approved-recipe-pilot
- phase2/governed-field-records

==================================================
8. ONLY AUTHORIZED MUTATION
==================================================

Only after sections 1–7 pass, merge PR #16 through the GitHub API using:

- expected head SHA:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
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

- edit the PR title or body;
- add a comment or label;
- request or submit another review;
- change its base or head;
- close it without merge;
- delete its branch;
- modify PR #15 or PR #17;
- retarget PR #17;
- trigger or rerun a workflow manually;
- modify any repository file, branch, runtime flag, or configuration.

If GitHub rejects the merge, do not retry using a different merge method
and do not bypass branch protection. End with:

PHASE_2D_PR16_MERGE_BLOCKED_MERGE_REJECTED

==================================================
9. POST-MERGE VERIFICATION
==================================================

After the merge, independently verify:

PR #16:

- state: closed;
- merged: true;
- base remains main;
- head remains phase2/approved-recipe-pilot;
- accepted head SHA remains:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- changed files remain exactly 9;
- additions/deletions remain exactly +1431/-6;
- the exact full 40-character merge-commit SHA is recorded.

Verify the merge commit:

- is the current live main SHA;
- has exactly two parents;
- first parent is:
  9db7e6b86c596bdf613f3180c2a1c927625233a1
- second parent is:
  5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
- therefore the merge was not squash or rebase;
- the Phase 2D candidate is now an ancestor of main.

Verify additionally:

- PR #15 remains closed and merged;
- PR #17 remains open and Draft;
- PR #17 base remains phase2/approved-recipe-pilot;
- PR #17 head and head SHA remain unchanged;
- PR #17 complete normalized metadata digest is unchanged;
- all three remote branches still exist;
- no branch was deleted;
- the permanent local worktree remains clean;
- local branch and HEAD remain unchanged;
- no repository file, local ref, configuration, or runtime flag changed.

If the merge succeeded but any post-merge evidence differs, do not attempt
automatic rollback or compensation. Record the exact live state and end
with:

PHASE_2D_PR16_MERGE_BLOCKED_POSTMERGE_VALIDATION

==================================================
10. REPORT
==================================================

Write exactly one report outside the Git repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2D_PR16_MERGE_2026-08-25.md

The report must include:

1. final verdict;
2. workspace and clean-state verification;
3. PR #15 and pre-merge main identity;
4. PR #16 exact pre-merge identity and nine-file scope;
5. approval identity, eligibility, and current-head applicability;
6. check and branch-protection state;
7. PR #17 pre-merge identity and metadata digest;
8. the exact single GitHub mutation performed;
9. PR #16 post-merge state;
10. exact merge-commit SHA and its two parents;
11. proof that the candidate is an ancestor of main;
12. PR #17 untouched confirmation;
13. branch-preservation confirmation;
14. local and repository no-change attestation;
15. exact next permitted action.

After a successful merge, the next permitted action is only:

- independently reverify the PR #16 merge;
- then retarget PR #17 from
  phase2/approved-recipe-pilot
  to main;
- confirm PR #17 remains exactly 12 files and +1760/-18.

Retargeting PR #17 is not authorized by this task.

End with exactly one applicable terminal token:

PHASE_2D_PR16_MERGE_COMPLETE

or:

PHASE_2D_PR16_MERGE_BLOCKED_WRONG_WORKSPACE
PHASE_2D_PR16_MERGE_BLOCKED_GITHUB_ACCESS
PHASE_2D_PR16_MERGE_BLOCKED_MAIN_DRIFT
PHASE_2D_PR16_MERGE_BLOCKED_CANDIDATE_DRIFT
PHASE_2D_PR16_MERGE_BLOCKED_APPROVAL_INVALID
PHASE_2D_PR16_MERGE_BLOCKED_MERGE_REJECTED
PHASE_2D_PR16_MERGE_BLOCKED_POSTMERGE_VALIDATION
