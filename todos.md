AskTD / KMAI — Phase 2E Controlled Finalization, Push, and Draft PR

You are finalizing the independently reviewed Phase 2E candidate.

This task is explicitly authorized to:

1. verify the accepted candidate one final time;
2. stage exactly the approved 12 files;
3. create exactly one Phase 2E commit;
4. push phase2/governed-field-records without force;
5. create a Draft PR whose base is exactly phase2/approved-recipe-pilot;
6. verify the resulting remote branch and Draft PR.

This task does not authorize merge, runtime activation, PR readiness, changes to PR #15 or PR #16, or Phase 2F.

1. Exact workspace

Required logical repository root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

Accepted resolved physical root:

/app1/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The workspace gate passes when:

* ordinary pwd equals the logical path;
* pwd -P equals the physical path;
* realpath . equals realpath of the logical path.

Do not search for another repository if the gate fails.

Do not read or modify:

* the stale primary checkout;
* branch asktd_v2;
* parent or sibling repositories;
* ETL or UCA projects;
* unrelated instruction or task files.

If the gate fails, stop with:

PHASE_2E_FINALIZATION_BLOCKED_WRONG_WORKSPACE

2. Permitted reports

Read these reports completely:

1. Implementation report:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_IMPLEMENTATION_2026-08-23.md
2. F-01 remediation report:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_REMEDIATION_2026-08-23.md
3. Final successful targeted independent re-review:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_TARGETED_INDEPENDENT_REREVIEW_RERUN_2026-08-23.md

Do not read the procedurally failed targeted review.

Do not modify any existing report.

The /home/... reports may resolve to equivalent /app1/... physical paths.

3. Required accepted evidence

The final successful review verdict is:

PHASE_2E_F01_TARGETED_REREVIEW_RERUN_PASS

Expected Phase 2D parent:

5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

Expected branch:

phase2/governed-field-records

Expected candidate digest:

d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be

Expected validation:

* full backend: 999 passed, 3 skipped, 8 warnings;
* coverage approximately 86.90%;
* required coverage: 75%;
* golden baseline: 10 passed;
* no Blocking, High, or Medium finding;
* exact 12-file candidate;
* clean index;
* zero commits beyond the Phase 2D parent;
* no Phase 2E remote branch;
* no Phase 2E PR.

4. Pre-mutation identity gate

Before staging, committing, or pushing, verify:

* branch is exactly phase2/governed-field-records;
* HEAD is exactly the Phase 2D parent SHA;
* merge base with origin/phase2/approved-recipe-pilot is exactly that parent;
* zero commits exist in parent..HEAD;
* Git index is clean;
* all candidate changes are unstaged;
* exactly 7 tracked modifications and 5 untracked candidate files exist;
* candidate contains exactly the approved 12 paths;
* no unrelated file exists;
* current combined digest matches the expected digest;
* git diff --check passes;
* no remote phase2/governed-field-records branch exists;
* no Phase 2E PR can already exist without a remote head branch.

Use read-only git ls-remote for remote identity. Do not fetch or mutate refs merely to verify them.

Confirm these live remote SHAs if accessible:

* origin/main:
    9ca6567571772a9f4e1ab555d8a678e678c45d49
* origin/phase2/provider-abstraction-foundation:
    d5472ae31081879329c224922244d87962737e8c
* origin/phase2/approved-recipe-pilot:
    5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

If the Phase 2D remote parent changed, stop. Do not rebase or rebuild the candidate.

If any candidate identity check fails, perform no mutation and return:

PHASE_2E_FINALIZATION_BLOCKED_PRECOMMIT_DRIFT

5. Exact approved file inventory

Only these repository-relative paths may be staged and committed:

1. docs/adr/0005-phase2e-governed-field-records.md
2. docs/adr/README.md
3. src/backend/app/available_data/field_evidence.py
4. src/backend/app/available_data/registry_contract.py
5. src/backend/app/recipes/approved_recipes.py
6. src/backend/app/recipes/dependency_fingerprint.py
7. test/test_approved_recipe_pilot.py
8. test/test_authz_no_access_guard.py
9. test/test_governed_field_records.py
10. test/test_provider_abstraction_contracts.py
11. test/test_recipe_dependency_fingerprint.py
12. test/test_semantic_plan_contract.py

Do not stage:

* reports;
* coverage/JUnit files;
* caches;
* editor files;
* environment files;
* deployment files;
* any other untracked or modified path.

6. Final pre-commit validation

Before staging, rerun from the exact repository root:

* focused fingerprint tests;
* golden baseline;
* complete configured backend suite and coverage gate;
* git diff --check;
* checks for all five untracked candidate files;
* diagnostics for all candidate Python files;
* provider-neutrality scan;
* excluded-technology and Phase 2F scope scans.

Use:

* PYTHONDONTWRITEBYTECODE=1;
* pytest cache provider disabled;
* coverage and JUnit outputs outside the repository;
* no formatting or rewriting command.

Expected full-suite result:

999 passed, 3 skipped, 8 warnings

Expected coverage:

approximately 86.90%, with the required 75% gate passing.

Expected golden baseline:

10 passed

After validation, verify candidate bytes and combined digest again.

If validation fails or candidate bytes change, do not stage or commit. Return:

PHASE_2E_FINALIZATION_BLOCKED_VALIDATION

7. Staging gate

Stage the 12 approved paths explicitly by name.

Do not use broad staging commands such as:

* git add .
* git add -A
* git add --all
* wildcard staging.

After staging, verify:

* exactly 12 staged paths;
* no unstaged candidate difference remains;
* no unrelated path is staged;
* index content is byte-for-byte identical to the accepted candidate;
* the digest recomputed from staged blobs is:
    d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be

If staged content differs, stop before commit. Do not reset automatically. Report the exact staged discrepancy with:

PHASE_2E_FINALIZATION_BLOCKED_STAGING_MISMATCH

8. Create exactly one commit

Verify Git author identity is already configured.

Do not modify local or global Git configuration.

If identity is unavailable, stop before committing with:

PHASE_2E_FINALIZATION_BLOCKED_GIT_IDENTITY

Create exactly one commit with this exact message:

feat(metadata): add governed field records and recipe dependencies

Do not amend, squash, rebase, or create multiple commits.

After committing, verify:

* commit parent is exactly:
    5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
* commit contains exactly the 12 approved paths;
* no report is in the commit;
* commit tree reproduces the accepted combined digest;
* worktree and index are clean;
* branch is exactly one commit ahead of Phase 2D.

Record the exact new commit SHA.

9. Push safely

Push only:

phase2/governed-field-records

Set its upstream to:

origin/phase2/governed-field-records

Requirements:

* no force push;
* no force-with-lease;
* no tag;
* no push to main;
* no push to the Phase 2C.5 or Phase 2D branches;
* no mutation of PR #15 or PR #16.

After pushing, verify with read-only remote inspection:

* the remote Phase 2E branch exists;
* its exact SHA equals the new local commit SHA;
* ancestry remains linear:
    main -> Phase 2C.5 -> Phase 2D -> Phase 2E
* Phase 2D remote SHA remains unchanged.

If the commit succeeds but push fails, do not reset, amend, or retry destructively. Return:

PHASE_2E_FINALIZATION_COMMITTED_PUSH_BLOCKED

10. Create the Draft PR

Create a new Draft PR with:

Base branch:

phase2/approved-recipe-pilot

Head branch:

phase2/governed-field-records

Title:

Phase 2E: governed field records and dependency-aware recipe references

The PR must remain Draft.

Do not use main as the base.

Do not mark it ready for review.

Do not merge it.

Use the authenticated GitHub mechanism already available in the environment. Do not extract, print, copy, or reconfigure credentials.

Required PR description

Use the following content:

## Summary
Phase 2E adds governed FieldRecord emission and dependency-aware references for the single Phase 2D Approved Recipe pilot.
- Emits 199 strictly evidenced fields only for the already-governed pilot dataset.
- Adds the pilot recipe’s four exact governed field dependencies.
- Adds entity-scoped dataset/field and recipe dependency fingerprints.
- Adds a deterministic, pure in-memory dependency reverse index.
- Fails closed for missing, renamed, unknown, ambiguous, or materially changed referenced fields.
- Preserves exact Phase 2D behavior when governed field records are disabled.
## Stacked PR
This PR is intentionally based on `phase2/approved-recipe-pilot`, not `main`.
Dependency chain:
1. PR #15 — provider-abstraction foundation
2. PR #16 — Approved Recipe pilot
3. This PR — governed field records and dependency-aware recipe references
Do not merge this PR independently of its accepted parent chain.
## Independent review
- Initial independent review identified F-01: reordered `DatasetRecord.required_columns` values could be falsely treated as conflicting duplicates.
- F-01 was remediated in both direct and snapshot duplicate-detection paths.
- Procedurally clean targeted independent re-review: PASS.
- No Blocking, High, or Medium findings remain.
Candidate SHA-256:
`d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be`
## Validation
- Full backend: 999 passed, 3 skipped, 8 existing warnings
- Coverage: 86.90% (required: 75%)
- Golden baseline: 10 passed
- Focused fingerprint suite: 12 passed
- Field-evidence and fingerprint suites: 31 passed
- Registry/hierarchy/cache/version regressions: 149 passed
- Semantic-plan regressions: 51 passed
- Approved Recipe pilot regressions: 75 passed
- Authorization/no-access regressions: 29 passed
- Provider-abstraction contracts: 7 passed
- Query-recipe and SQL-policy regressions: 59 passed
- `git diff --check`: passed
- Provider-neutrality and excluded-technology scans: passed
## Compatibility and boundaries
- Feature flags remain default OFF.
- Runtime strict-mode activation is a separate work item.
- Authorization sources and policies are unchanged.
- Relationships remain empty.
- No Redis, Databricks, Genie, Unity Catalog, Collibra, graph database, frontend, deployment, Terraform, cross-source execution, or Phase 2F work is included.
- Reports and review artifacts are intentionally outside the Git candidate.

If the GitHub PR API is unauthenticated or unavailable:

* do not change the PR base;
* do not create a non-Draft substitute;
* do not expose credentials;
* do not undo the valid commit or push;
* record the exact error and the pushed branch SHA;
* provide this manual comparison URL:

https://github.com/TD-Enterprise/kmai-td-genie/compare/phase2/approved-recipe-pilot...phase2/governed-field-records?expand=1

Return:

PHASE_2E_FINALIZATION_PUSHED_PR_CREATION_BLOCKED

11. Verify the created PR

After creation, verify:

* PR number and URL;
* state: open;
* Draft: true;
* base: phase2/approved-recipe-pilot;
* head: phase2/governed-field-records;
* exact head SHA equals the new Phase 2E commit;
* changed-file inventory contains exactly the 12 approved paths;
* no report or unrelated file is present;
* commit count is one relative to the PR base;
* checks/workflows, if any;
* mergeability and merge state, if available;
* reviews and required approvals, if available.

Do not interpret missing CI on a stacked base as an authorization to alter workflows during this task. Record it as a separate open item.

12. Finalization report

Write only this report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_FINALIZATION_2026-08-23.md

The report must include:

1. final verdict;
2. workspace identity;
3. reports read;
4. pre-mutation branch, parent, inventory, and digest;
5. final validation commands and results;
6. exact staged inventory;
7. staged digest proof;
8. commit message, parent SHA, and new commit SHA;
9. committed inventory and digest proof;
10. push result and remote SHA;
11. ancestry verification;
12. Draft PR number, URL, base, head, SHA, state, and Draft status;
13. PR changed files;
14. checks, reviews, mergeability, and merge state;
15. confirmation that PR #15, PR #16, and main were not changed;
16. confirmation that runtime configuration and feature flags were not changed;
17. confirmation that Phase 2F was not started;
18. completion-state attestation.

End with exactly one token:

* PHASE_2E_FINALIZATION_COMPLETE
* PHASE_2E_FINALIZATION_BLOCKED_WRONG_WORKSPACE
* PHASE_2E_FINALIZATION_BLOCKED_PRECOMMIT_DRIFT
* PHASE_2E_FINALIZATION_BLOCKED_VALIDATION
* PHASE_2E_FINALIZATION_BLOCKED_STAGING_MISMATCH
* PHASE_2E_FINALIZATION_BLOCKED_GIT_IDENTITY
* PHASE_2E_FINALIZATION_COMMITTED_PUSH_BLOCKED
* PHASE_2E_FINALIZATION_PUSHED_PR_CREATION_BLOCKED
* PHASE_2E_FINALIZATION_BLOCKED_ENVIRONMENT

PHASE_2E_FINALIZATION_COMPLETE means the exact reviewed candidate was committed once, pushed safely, and opened as a Draft stacked PR. It does not authorize merge, marking ready, runtime activation, changes to PR #15 or #16, or Phase 2F.
