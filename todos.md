AskTD / KMAI — Read-only PR Stack Review and Merge-Readiness Verification

Perform one bounded, read-only verification of the complete stacked PR chain for Phase 2C.5, Phase 2D, and Phase 2E.

Repository:

TD-Enterprise/kmai-td-genie

This task must not modify any repository, branch, commit, PR, review, label, Git setting, credential, workflow, or working tree.

Do not mark any PR ready.

Do not approve or merge any PR.

Do not start Phase 2F.

1. Workspace boundary

Required logical repository root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

Accepted physical equivalent:

/app1/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The workspace is valid when:

* pwd matches the logical path;
* pwd -P matches the physical path;
* both resolve through realpath to the same directory.

Do not use or read the stale primary checkout or branch asktd_v2.

Do not inspect ETL, UCA, parent, or sibling repositories.

If the workspace is wrong, stop with:

PHASE_2E_PR_STACK_READINESS_BLOCKED_WRONG_WORKSPACE

2. Permitted evidence reports

Read completely:

1. Final successful Phase 2E independent re-review:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_TARGETED_INDEPENDENT_REREVIEW_RERUN_2026-08-23.md
2. Phase 2E finalization report:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_FINALIZATION_2026-08-23.md

Do not modify these reports.

Do not read the procedurally failed re-review report.

Equivalent resolved /app1/... paths are permitted.

3. Strict read-only rules

Do not:

* edit repository files;
* stage files;
* create or amend commits;
* fetch into or update local refs;
* push;
* force-push;
* create, edit, close, reopen, approve, comment on, mark ready, or merge a PR;
* change any PR base or head;
* add reviewers, labels, milestones, or assignees;
* modify Git or GitHub authentication;
* run gh auth login;
* print, copy, persist, or expose credentials;
* rebase, merge, cherry-pick, reset, stash, clean, switch, or delete branches;
* modify workflows or branch-protection settings;
* enable runtime flags;
* start Phase 2F.

Use git ls-remote and an already-authenticated GitHub read interface where available.

If GitHub API access is unavailable, record that precisely and continue with all Git-level evidence that can be verified safely. Do not guess missing PR metadata.

4. Expected live branch chain

Verify the current live SHAs rather than assuming them.

Last accepted evidence:

Main

Branch:

main

Expected SHA:

9ca6567571772a9f4e1ab555d8a678e678c45d49

Phase 2C.5

Branch:

phase2/provider-abstraction-foundation

Expected SHA:

d5472ae31081879329c224922244d87962737e8c

PR:

#15

Expected base:

main

Phase 2D

Branch:

phase2/approved-recipe-pilot

Expected SHA:

5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

PR:

#16

Expected base:

phase2/provider-abstraction-foundation

Phase 2E

Branch:

phase2/governed-field-records

PR:

#17

Expected base:

phase2/approved-recipe-pilot

Derive the exact Phase 2E SHA independently from:

* local HEAD;
* the remote Phase 2E branch;
* PR #17 head SHA.

All three must match.

Expected Phase 2E candidate digest:

d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be

5. Verify exact linear ancestry

Using read-only Git object and remote evidence, verify:

main
  -> phase2/provider-abstraction-foundation
      -> phase2/approved-recipe-pilot
          -> phase2/governed-field-records

Confirm:

* each phase adds exactly one commit;
* each child commit’s parent is the immediately preceding phase SHA;
* there are no merge commits;
* merge bases are exact;
* no branch has diverged;
* no force-push or candidate drift is evident;
* no unexpected commit appears in any phase branch.

Show the exact four-SHA ancestry.

If any expected accepted branch SHA has changed, return:

PHASE_2E_PR_STACK_READINESS_DRIFT_DETECTED

Do not recommend merge until the drift is independently reviewed.

6. PR #15 live verification

Verify:

* URL;
* state;
* Draft status;
* base branch;
* head branch;
* exact base SHA;
* exact head SHA;
* commit count;
* exact changed-file inventory;
* additions and deletions;
* reviews;
* review decisions;
* requested reviewers;
* comments and review comments;
* checks/workflows and conclusions;
* required checks;
* required approvals;
* branch-protection requirements;
* mergeability;
* merge state;
* conflicts;
* unresolved review threads;
* whether its independently reviewed candidate SHA remains unchanged.

Expected accepted changed-file count:

7

Do not assume an independent PASS means the PR was merged or approved.

7. PR #16 live verification

Verify the same complete metadata for PR #16:

* URL;
* state;
* Draft status;
* base and head;
* base and head SHAs;
* commit count;
* exact changed files;
* additions/deletions;
* reviews and requested reviewers;
* comments/review comments;
* checks;
* required approvals and checks;
* branch protection;
* mergeability and merge state;
* conflicts and unresolved threads;
* candidate drift.

Expected base/head relationship:

phase2/provider-abstraction-foundation <- phase2/approved-recipe-pilot

Expected accepted changed-file count:

9

8. PR #17 live verification

Verify the same complete metadata for PR #17:

* URL;
* state;
* Draft status;
* base:
    phase2/approved-recipe-pilot
* head:
    phase2/governed-field-records
* exact base and head SHAs;
* one commit relative to its base;
* exactly 12 changed files;
* exact changed-file inventory;
* additions/deletions;
* reviews and requested reviewers;
* comments/review comments;
* checks/workflows;
* required approvals and checks;
* branch protection;
* mergeability and merge state;
* conflicts and unresolved threads;
* candidate drift.

Confirm that PR #17’s committed file content reproduces:

d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be

Confirm no report file is included.

The finalization evidence reported zero check runs for PR #17. Verify this live and distinguish among:

* genuinely zero check runs;
* checks not triggered because of stacked-base workflow configuration;
* API permissions preventing visibility;
* checks pending or queued;
* checks present under a different SHA.

Do not infer which explanation is correct without evidence.

9. Approval and branch-protection analysis

For each PR, determine where possible:

* whether approvals are formally required;
* how many approvals;
* whether Code Owner review is required;
* whether stale approvals are dismissed after new commits;
* whether required status checks exist;
* whether conversation resolution is required;
* whether linear history is required;
* whether signed commits are required;
* whether merge queue applies;
* whether draft PRs can be merged;
* who can merge;
* whether base-branch changes dismiss approvals or restart checks.

If API permissions do not expose these settings, mark them:

OPEN — REQUIRES REPOSITORY ADMIN OR GITHUB UI CONFIRMATION

Do not guess.

10. Determine merge-readiness classification

Classify each PR using only verified evidence:

* NOT_READY — CANDIDATE DRIFT
* NOT_READY — TECHNICAL DEFECT
* NOT_READY — DRAFT
* NOT_READY — APPROVAL REQUIRED
* NOT_READY — REQUIRED CHECKS MISSING
* NOT_READY — CONFLICT
* READY TO REQUEST REVIEW
* READY TO MERGE
* OPEN — INSUFFICIENT PERMISSION TO DETERMINE

A clean mergeability result alone is not sufficient for READY TO MERGE.

A prior independent technical PASS alone is not sufficient for READY TO MERGE.

11. Produce the safe stacked merge sequence

Without performing any mutation, determine the exact safe sequence.

The expected bottom-up strategy to evaluate is:

1. request review for PR #15;
2. satisfy approvals and required checks for PR #15;
3. merge PR #15 into main;
4. verify main contains exactly the accepted Phase 2C.5 commit;
5. retarget or recreate the correct base relationship for PR #16 only after explicit authorization;
6. verify PR #16 still shows only the accepted Phase 2D delta;
7. rerun any checks/review invalidated by its base change;
8. merge PR #16;
9. retarget or recreate the correct base relationship for PR #17 only after explicit authorization;
10. verify PR #17 still shows only the accepted 12-file Phase 2E delta;
11. rerun invalidated checks/reviews;
12. merge PR #17.

Determine whether GitHub’s current repository and branch policies support this exact sequence or require a different safe sequence.

Do not perform any retargeting or merge.

Explain:

* why PR #16 must not be merged ahead of PR #15;
* why PR #17 must not be merged ahead of PR #16;
* which checks and approvals may be invalidated after each base change;
* whether branch deletion would affect child PRs;
* whether parent branches must temporarily remain until child PRs are safely retargeted.

12. CI/check-run open item

Investigate read-only why PR #16 and/or PR #17 show zero checks.

Inspect only existing workflow configuration inside the current repository and GitHub’s reported check metadata.

Do not modify workflows.

Determine whether:

* workflows only trigger for PRs targeting main;
* stacked base branches are excluded;
* path filters exclude the changed files;
* workflows require manual dispatch;
* checks have not yet started;
* the API cannot expose them;
* another evidenced cause exists.

Classify this as one of:

* MERGE BLOCKER
* REVIEW-READINESS BLOCKER
* AUTOMATION GAP — MANUAL VALIDATION CURRENTLY AVAILABLE
* VISIBILITY/PERMISSION GAP
* NOT A BLOCKER UNDER VERIFIED POLICY
* OPEN — REQUIRES OWNER CONFIRMATION

Record evidence. Do not make an enterprise or repository-policy decision on behalf of the owner.

13. Required decision register

For every unresolved item, record:

* decision or assumption;
* why it matters;
* current evidence;
* owner;
* confirmation required;
* whether it blocks:
    * review request;
    * merge;
    * runtime activation;
    * production;
    * later phase only.

At minimum cover:

* required approvals;
* Code Owner requirement;
* zero check runs;
* base-retargeting policy;
* branch deletion policy;
* who is authorized to mark PRs ready;
* who is authorized to merge;
* whether PR #15 and #16 should remain Draft until all stacked candidates are reviewed;
* runtime strict-mode activation as a separate work item.

14. Report

Write only this report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR_STACK_READINESS_2026-08-23.md

The report must contain:

1. final verdict;
2. workspace and read-only attestation;
3. live remote branch table;
4. exact ancestry graph;
5. PR #15 complete state;
6. PR #16 complete state;
7. PR #17 complete state;
8. changed-file inventories;
9. reviews and approval requirements;
10. checks/workflows;
11. mergeability and merge states;
12. drift comparison against accepted SHAs;
13. branch-protection findings;
14. readiness classification for each PR;
15. zero-check-run root-cause analysis;
16. safe bottom-up review/merge sequence;
17. decision register;
18. one recommended next action;
19. confirmation that no repository, branch, commit, PR, workflow, credential, or Git setting was changed.

End with exactly one token:

* PHASE_2E_PR_STACK_READINESS_VERIFIED
* PHASE_2E_PR_STACK_READINESS_DRIFT_DETECTED
* PHASE_2E_PR_STACK_READINESS_BLOCKED_API
* PHASE_2E_PR_STACK_READINESS_BLOCKED_WRONG_WORKSPACE
* PHASE_2E_PR_STACK_READINESS_BLOCKED_ENVIRONMENT

A verified report does not authorize marking a PR ready, changing a base, approving, merging, deleting branches, activating runtime flags, or starting Phase 2F.
