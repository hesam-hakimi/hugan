We are finalizing the independently accepted AskTD / KMAI Phase 2D Approved Recipe Pilot.

The implementation and bounded remediation are complete.

The latest independent read-only re-review returned:

PHASE_2D_INDEPENDENT_REREVIEW_PASS

The reviewer independently confirmed:

- Former HIGH-1 (governed validation ordering): RESOLVED
- Former HIGH-2 (`builder_key` not authoritative): RESOLVED
- No HIGH findings attributable to Phase 2D
- Full backend suite: 962 passed, 3 skipped
- Coverage: 86.75% (required gate 75%)
- Golden baseline: passed
- `git diff --check`: clean
- Independent mutation probes confirmed that the new controls are load-bearing
- Candidate bytes remained unchanged during independent review
- PR #15 was not changed
- `main` was not changed
- No commit was created by the reviewer
- No branch was pushed by the reviewer
- No Phase 2D PR was created by the reviewer
- No later phase was started

The independent reviewer also recorded:

1. A pre-existing MEDIUM issue where a denial message can disclose the blocked physical object name. This is NOT attributable to Phase 2D and MUST NOT be repaired in this operation.
2. A future-risk LOW/INFO item: `governed_dataset_refs` is not currently cross-checked against the tables actually emitted by the builder. This MUST NOT be expanded into new Phase 2D work now. Record it as follow-up/deferred work only.

==================================================
OBJECTIVE
==================================================

Finalize the EXACT independently reviewed Phase 2D candidate:

1. Verify candidate identity and byte stability.
2. Commit the already-reviewed Phase 2D implementation.
3. Push the Phase 2D branch.
4. Create a DRAFT pull request.
5. Report the exact resulting repository state.

DO NOT implement anything new.

==================================================
CRITICAL IMMUTABILITY RULE
==================================================

The independently reviewed candidate MUST NOT change before commit.

Before doing anything mutating:

1. Identify the exact Phase 2D worktree and branch used for the successful independent re-review.

Expected branch:

    phase2/approved-recipe-pilot

Expected parent:

    d5472ae31081879329c224922244d87962737e8c

The parent corresponds to the independently accepted Phase 2C.5 candidate.

2. Capture:

    git status --short
    git branch --show-current
    git rev-parse HEAD
    git diff --stat
    git diff --check
    git diff --name-status
    git diff
    git ls-files --others --exclude-standard

3. Compute a deterministic digest of ALL candidate changes, including:
   - modified tracked files
   - newly added/untracked files that belong to Phase 2D

4. Compare the candidate against the state that received:

    PHASE_2D_INDEPENDENT_REREVIEW_PASS

If there is ANY unexplained candidate drift:

STOP.

Output:

    PHASE_2D_FINALIZATION_BLOCKED_CANDIDATE_DRIFT

Do not commit.
Do not push.
Do not create a PR.

==================================================
SCOPE LOCK
==================================================

Do NOT:

- modify implementation
- modify tests
- modify ADR content
- fix formatting unless required to preserve the exact reviewed bytes
- repair the pre-existing MEDIUM security issue
- implement the governed_dataset_refs/table cross-check
- modify PR #15
- modify `main`
- merge anything
- rebase the reviewed candidate
- squash or rewrite Phase 2C.5
- start Phase 2E
- add Databricks/Genie/Unity Catalog work
- add Redis/Event Hubs work
- perform unrelated cleanup

This operation is repository finalization only.

==================================================
EXPECTED PHASE 2D CONTENT
==================================================

Verify the candidate contains the already-reviewed Phase 2D work, including the relevant Phase 2D files such as:

- docs/adr/0004-phase2d-approved-recipe-pilot.md
- src/backend/app/recipes/__init__.py
- src/backend/app/recipes/approved_recipes.py
- src/backend/app/orchestrator.py
- test/test_approved_recipe_pilot.py
- previously reviewed Phase 2D test extensions
- ADR index update if it was part of the reviewed candidate

Do NOT reconstruct this list from this prompt alone.

The actual independently reviewed Git diff is authoritative.

==================================================
PRE-COMMIT VALIDATION
==================================================

Before committing, rerun the relevant non-mutating validation gates against the unchanged candidate.

At minimum:

1. Phase 2D focused tests
2. Approved Recipe contract tests
3. semantic-plan/governance tests
4. authorization negative tests
5. provider-abstraction regression tests
6. golden baseline
7. full backend test suite with configured coverage
8. git diff --check
9. excluded/future-provider technology scan

Expected previously reviewed baseline includes:

    962 passed
    3 skipped
    coverage 86.75%

Small test-count differences are acceptable ONLY if you can prove they are caused by test-discovery/environment differences and NOT candidate changes.

Any real regression:

STOP.

Output:

    PHASE_2D_FINALIZATION_BLOCKED_VALIDATION_FAILURE

==================================================
COMMIT
==================================================

Only after identity and validation pass:

Stage ONLY the exact independently reviewed Phase 2D files.

Before commit, show:

    git status --short
    git diff --cached --name-status
    git diff --cached --stat

Confirm that no unrelated files are staged.

Create ONE commit.

Suggested commit message:

    feat(asktd): add governed approved recipe pilot

Do not amend any existing commit.

After commit capture:

    git rev-parse HEAD
    git show --stat --oneline HEAD
    git status --short

==================================================
PUSH
==================================================

Push:

    phase2/approved-recipe-pilot

Do NOT force push.

Verify local HEAD equals remote branch HEAD after push.

If they differ:

STOP and report the mismatch.

==================================================
DRAFT PR
==================================================

Create a DRAFT PR.

Base:

    phase2/provider-abstraction-foundation

Head:

    phase2/approved-recipe-pilot

IMPORTANT:

PR #15 is the Phase 2C.5 PR into `main`.

Phase 2D is intentionally stacked on the accepted Phase 2C.5 candidate.

Do NOT target `main` while PR #15 remains unmerged.

The PR body should clearly state:

Title:

    Phase 2D — Governed Approved Recipe Pilot

Summary should explain in simple terms:

- introduces the first governed Approved Recipe pilot
- uses deterministic recipe selection
- validates recipe lifecycle and parameters before any data-source/SQL activity
- makes `builder_key` authoritative for the executed SQL builder
- validates governed dataset scope using the existing semantic-plan governance layer
- preserves existing authorization and read-only enforcement
- remains behind the Phase 2D pilot flag
- preserves legacy behavior when the flag is disabled
- does not introduce Databricks, Genie, Unity Catalog, Redis, Event Hubs, or cross-source execution

Include validation evidence:

- Independent re-review: PASS
- Full backend: 962 passed, 3 skipped
- Coverage: 86.75%
- Golden baseline: passed
- diff checks: clean
- independent mutation probes: passed

Also explicitly state:

Dependency:
This PR is stacked on PR #15 / `phase2/provider-abstraction-foundation`.
It must not be merged before its base dependency is resolved.

Deferred/non-blocking findings:
- pre-existing physical-object disclosure in one denial path
- future governed_dataset_refs vs emitted-table cross-check

Do NOT claim those were fixed.

==================================================
POST-PUSH / PR VERIFICATION
==================================================

After creating the Draft PR, verify:

- branch name
- local commit SHA
- remote commit SHA
- PR number
- PR URL
- PR base
- PR head
- Draft = yes
- changed-file count
- CI/check status if available
- mergeability if available
- PR #15 unchanged
- `main` unchanged
- working tree clean

==================================================
FINAL RESPONSE
==================================================

Return exactly one final status token:

PHASE_2D_DRAFT_PR_CREATED

or, if blocked:

PHASE_2D_FINALIZATION_BLOCKED_<REASON>

Then provide a concise evidence table containing:

- Parent SHA
- Phase 2D commit SHA
- Remote SHA
- Branch
- PR number
- PR base/head
- Draft status
- Changed files
- Test results
- Coverage
- CI status
- Working-tree status
- PR #15 changed? Yes/No
- main changed? Yes/No
- Phase 2E started? Yes/No

IMPORTANT:

Do not start Phase 2E.

Stop after Phase 2D Draft PR creation and verification.
