We are continuing the AskTD Phase 2C acceptance workflow.

PR #11 (Phase 2A) and PR #12 (Phase 2B) have now been processed through their review/merge sequence.

The Phase 2C implementation has already been independently inspected and all eight remediation requirements R1-R8 were found:

FIXED_AND_COVERED

with the focused Phase 2A/2B/2C test suite:

141 passed

Do NOT redesign or remediate Phase 2C logic unless integration evidence proves an actual regression.

Current observed state

Phase 2C PR:

#14

Head branch:

phase2/semantic-plan-contract-validator

GitHub currently still shows its base as:

phase2/service-version-boundary

and reports a merge conflict involving:

kmai-td-genie/docs/adr/README.md

The PR remains Draft.

Objective

Safely bring the Phase 2C branch onto the now-integrated current main, resolve only integration conflicts, and verify that the accepted Phase 2C behavior remains unchanged.

This operation must NOT:

* start Phase 2D;
* add provider abstractions;
* implement Databricks;
* implement Genie;
* implement Collibra;
* add Redis or Event Hubs;
* change authorization scope;
* redesign Phase 2C;
* merge PR #14.

Step 1 — Verify upstream state before mutation

Fetch remote refs.

Verify and report:

* origin/main HEAD SHA;
* whether PR #11 content is present in origin/main;
* whether PR #12 content is present in origin/main;
* current Phase 2C branch HEAD;
* current working-tree status in the dedicated Phase 2C worktree;
* whether the Phase 2C branch is pushed and synchronized with origin.

If PR #12 is NOT actually present in origin/main, STOP WITHOUT CHANGING ANYTHING and report:

PHASE_2C_INTEGRATION_BLOCKED_PHASE_2B_NOT_IN_MAIN

Do not guess from GitHub UI labels alone.

Step 2 — Preserve safety

Work only in the existing dedicated Phase 2C worktree/branch:

phase2/semantic-plan-contract-validator

Do not touch the primary asktd_v2 checkout.

The Phase 2C worktree must be clean before beginning.

If it is not clean, STOP and report the existing changes.

Before changing history, record:

* current Phase 2C HEAD SHA;
* current origin/main SHA;
* git status;
* merge-base.

Do not delete backup refs or historical branches.

Step 3 — Rebase Phase 2C onto current main

Once Phase 2A and 2B are confirmed present in origin/main, rebase the Phase 2C branch onto current:

origin/main

The goal is for PR #14 to contain only the Phase 2C delta relative to integrated main.

Do not manually copy Phase 2A/2B commits.

Do not squash or rewrite Phase 2C semantics unnecessarily.

Step 4 — Resolve conflicts minimally

If conflicts occur, inspect both sides and resolve them according to the now-integrated repository state.

The currently known conflict is:

kmai-td-genie/docs/adr/README.md

For this file:

* preserve all already-integrated Phase 2A and Phase 2B ADR entries from main;
* preserve/add the Phase 2C ADR entry;
* do not remove unrelated ADR entries;
* do not rewrite historical ADR content;
* make the smallest deterministic reconciliation necessary.

If ANY source-code or test conflict appears, do not blindly choose ours/theirs.

Inspect the conflict and preserve:

1. accepted Phase 2A contracts;
2. accepted Phase 2B service/version/cache behavior;
3. Phase 2C R1-R8 behavior already independently verified.

If resolving a source/test conflict requires a semantic design decision rather than a mechanical integration, STOP and report it instead of inventing a decision.

Step 5 — Run focused Phase 2C regression

After successful rebase/conflict resolution, run the exact focused suite used by the previous audit:

PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  test/test_registry_cache.py \
  test/test_registry_contract.py \
  test/test_registry_hierarchy_contract.py \
  test/test_semantic_plan_contract.py \
  -p no:cacheprovider -q -c /dev/null

Expected baseline:

141 passed

If the count changes, explain exactly why.

R1-R8 must remain behaviorally satisfied.

Step 6 — Verify MetadataRegistryService integration

Locate the existing tests covering MetadataRegistryService interaction with:

* registry_contract.py;
* registry_cache.py;
* semantic-plan validation / validate_governed_semantic_plan_for_service.

Run the smallest existing applicable service/integration test set.

Do not create new tests unless an actual uncovered regression is demonstrated.

Step 7 — Run required acceptance regression gates

Using the repository’s existing environment and instructions only:

* full backend test suite;
* configured coverage gate;
* golden baseline tests if they are part of ADR 0002 validation evidence;
* git diff --check;
* existing tracked-file secret/security scan if a repository-supported command already exists.

Do not install or upgrade dependencies.

Do not rewrite baselines simply to make tests pass.

If a test fails, determine whether it is:

* Phase 2C regression;
* pre-existing unrelated failure;
* environment/tooling failure.

Do not broaden scope automatically.

Step 8 — Verify resulting PR delta

Compare the rebased Phase 2C branch to origin/main.

Verify:

* Phase 2A/2B commits are no longer presented as Phase 2C-specific changes;
* only intended Phase 2C changes remain;
* no unrelated files entered the diff;
* docs/adr/README.md contains the complete integrated ADR index;
* R1-R8 implementation remains intact.

Step 9 — Push safely

If and only if:

* rebase completed successfully;
* conflicts were mechanically resolved;
* focused tests pass;
* required regression gates have acceptable results;
* no unintended changes exist;

push the updated Phase 2C branch to:

origin/phase2/semantic-plan-contract-validator

Because rebase changes commit history, use the repository-approved safe history-update method, preferably:

git push --force-with-lease

Never use plain --force.

Do NOT merge PR #14.

Do NOT mark it Ready for Review.

Step 10 — PR base

After the branch is successfully rebased onto integrated main, determine whether PR #14’s base automatically updates to main.

If GitHub still lists the obsolete Phase 2B branch as its base, retarget PR #14 only to:

main

only after confirming that main contains the accepted Phase 2A and Phase 2B content.

Do not change any other PR.

Final report

Save outside the repository as:

/tmp/ASKTD_PHASE_2C_INTEGRATION_2026-08-20.md

Include:

1. Pre-Integration Evidence
2. Confirmation Phase 2A/2B Are in Main
3. Rebase Result
4. Conflict Resolution
5. Focused R1-R8 Regression
6. MetadataRegistryService Integration Tests
7. Full Regression / Coverage / Golden / Safety Gates
8. Final Diff Against Main
9. PR #14 Current Base / Head / Draft / Checks
10. Independent Acceptance Readiness
11. Recommended Single Next Action

Use exactly one final verdict:

* PHASE_2C_INTEGRATION_READY_FOR_FINAL_ACCEPTANCE
* PHASE_2C_INTEGRATION_HAS_REGRESSION
* PHASE_2C_INTEGRATION_BLOCKED
* PHASE_2C_INTEGRATION_INSUFFICIENT_EVIDENCE

At the end report:

* old Phase 2C SHA;
* new Phase 2C SHA;
* origin/main SHA used as base;
* files changed specifically during conflict resolution;
* focused test result;
* full regression result;
* whether PR #14 was retargeted;
* whether branch was pushed.

Do not mark PR #14 Ready for Review.
Do not merge PR #14.
Do not start Phase 2D.

Then STOP.
