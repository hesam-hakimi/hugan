We are finalizing the already independently accepted AskTD Phase 2C.5
Provider Abstraction Foundation candidate.

Independent review verdict:

PHASE_2C5_INDEPENDENT_REVIEW_PASS

This operation is ONLY for:

1. proving the reviewed candidate has not changed;
2. committing exactly that candidate;
3. pushing the existing Phase 2C.5 branch;
4. creating a Draft PR to main;
5. reporting CI/PR state.

Do NOT modify implementation behavior.
Do NOT perform remediation.
Do NOT merge the PR.
Do NOT deploy.
Do NOT start Phase 2D.

==================================================
1. TARGET
==================================================

Repository:
TD-Enterprise/kmai-td-genie

Branch:
phase2/provider-abstraction-foundation

Expected worktree:
/tmp/asktd-phase2c5-provider-abstraction

PR base:
main

First verify that this exact worktree/branch is being used.

Do not use the stale asktd_v2 checkout.

==================================================
2. PROVE THE REVIEWED CANDIDATE IS UNCHANGED
==================================================

Before staging anything, capture:

- git status --short
- current HEAD SHA
- origin/main SHA
- complete changed-file inventory
- git diff --check
- git diff --stat
- a deterministic SHA-256 digest of the complete candidate diff,
  including tracked modifications and the contents/paths of intended
  untracked files.

Compare the current candidate with the state described by the successful
independent re-review.

Expected Phase 2C.5 files include the provider-abstraction implementation,
tests, composition-root change, and ADR.

If ANY unexplained code/test/documentation change occurred after the
independent review:

STOP.

Return:

PHASE_2C5_REVIEWED_CANDIDATE_CHANGED

Do not commit or push.

==================================================
3. SCOPE CHECK
==================================================

Confirm the candidate still contains only Phase 2C.5 work.

It must NOT contain implementation of:

- Databricks SQL
- Databricks authentication
- Unity Catalog
- Collibra
- Genie
- Redis
- Event Hubs
- cross-source joins
- fine-grained authorization
- Phase 2D recipes
- KPI/glossary features
- frontend changes
- deployment/infrastructure changes
- unrelated refactoring

Confirm Orchestrator still has:

- direct SqlDataStore import: No
- direct SqlDataStore construction: No
- concrete SqlDataStore annotation: No
- concrete SqlDataStore isinstance dependency: No

And default concrete construction remains outside Orchestrator through the
accepted composition root / build_default_data_source path.

==================================================
4. FINAL PRE-COMMIT TEST
==================================================

Do not rerun unnecessary large investigation.

Run at minimum:

- provider abstraction contract tests
- git diff --check

If the worktree has changed since the independent review for any reason,
rerun the affected focused tests before proceeding.

The previously independently accepted state had green:

- Phase 2A/2B/2C regressions
- MetadataRegistryService tests
- authorization tests
- SQL/Orchestrator tests
- golden baseline
- full backend
- coverage gate

Do not regenerate baselines.

==================================================
5. COMMIT
==================================================

Stage ONLY the reviewed Phase 2C.5 files.

Before committing, print:

git status --short
git diff --cached --stat
git diff --cached --name-status

Verify there are no unrelated staged files.

Create ONE focused commit.

Suggested commit message:

feat(phase2c5): add provider-neutral data source boundary

Do not amend unrelated commits.

After commit report:

- commit SHA
- parent SHA
- committed file list

==================================================
6. VERIFY COMMITTED BYTES
==================================================

Immediately after commit:

- verify working tree is clean;
- compare the committed tree/diff with the pre-commit reviewed candidate;
- confirm no file was added, removed, or altered by staging/commit hooks;
- rerun git diff --check as appropriate.

If commit hooks or tooling altered the candidate unexpectedly:

STOP.

Do not push.

Return:

PHASE_2C5_COMMIT_DIFFERS_FROM_REVIEWED_CANDIDATE

==================================================
7. PUSH
==================================================

Push:

phase2/provider-abstraction-foundation

to origin.

Use a normal push.

Do not force-push unless repository evidence proves it is required.
If a force push would be required, STOP and ask before doing it.

Confirm local and remote branch HEADs are identical after push.

==================================================
8. CREATE DRAFT PR
==================================================

Create a DRAFT pull request:

Head:
phase2/provider-abstraction-foundation

Base:
main

Suggested title:

Phase 2C.5 — Provider abstraction foundation

PR body should summarize:

- Phase 2C is already formally closed;
- this PR introduces the minimal provider-neutral DataSourceAdapter seam;
- concrete SqlDataStore construction moved outside Orchestrator to the
  composition root;
- existing DatabaseTool remains the execution seam;
- MetadataRegistryService / RegistrySnapshot remain the governance boundary;
- EffectivePermissions remains the authorization-scope foundation;
- no Databricks, Unity Catalog, Collibra, Genie, Redis, Event Hubs, or
  Phase 2D implementation is included;
- independent technical review result:
  PHASE_2C5_INDEPENDENT_REVIEW_PASS;
- important regression/coverage/golden evidence.

Explicitly state:

DO NOT MERGE until required PR CI and independent repository review are green.

Do not mark Ready for Review in this operation unless repository policy
automatically requires it.

==================================================
9. PR / CI OBSERVATION
==================================================

After creating the Draft PR, report:

- PR number
- PR URL
- base
- head
- head SHA
- Draft status
- changed-file count
- checks currently visible
- approval requirement
- merge/conflict state if observable

Do not wait indefinitely for CI.

If checks are queued/running, simply report that.

==================================================
10. FINAL VERDICT
==================================================

Return exactly one:

PHASE_2C5_DRAFT_PR_CREATED

or

PHASE_2C5_COMMIT_PUSH_PR_BLOCKED

or

PHASE_2C5_REVIEWED_CANDIDATE_CHANGED

Include:

- reviewed candidate diff digest
- commit SHA
- pushed remote SHA
- PR number
- PR base/head
- Draft status
- CI state
- files committed
- working tree clean: Yes/No
- Phase 2D started: No

Do NOT merge.
Do NOT deploy.
Do NOT start Phase 2D.

Then STOP.
