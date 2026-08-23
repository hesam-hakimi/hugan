AskTD / KMAI — Phase 2E F-01 Bounded Remediation Prompt

You are performing a narrowly bounded remediation of the single defect identified by the Phase 2E independent review.

This is not a redesign, general cleanup, commit, push, PR, runtime-activation, or Phase 2F task.

1. Required workspace

Use only the permanent Phase 2E worktree:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records

Repository implementation root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

Expected branch:

phase2/governed-field-records

Do not use or modify the stale primary checkout on asktd_v2.

2. Read the evidence first

Before editing anything, read these two reports completely:

1. Implementation report:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_IMPLEMENTATION_2026-08-23.md
2. Independent-review report:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_INDEPENDENT_REVIEW_2026-08-23.md

Treat the independent-review finding F-01 as the complete remediation scope.

Do not modify either existing report.

3. Pre-remediation identity gate

Before editing, verify:

* local branch is phase2/governed-field-records;
* local HEAD is exactly the accepted Phase 2D SHA:
    5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
* the Git index is clean;
* no commit exists beyond the Phase 2D parent;
* the candidate remains unstaged and uncommitted;
* the candidate still consists of exactly the expected 12 files;
* no unrelated file has entered the candidate;
* the pre-remediation combined candidate SHA-256 is exactly:
    1c72d47be76b7e8d2f768005cca0254dd43761212a15637950fcfb0ed6d7cc35

If any identity check differs, make no edits and return:

PHASE_2E_F01_REMEDIATION_BLOCKED_CANDIDATE_DRIFT

Remote verification is read-only. If remote access is available, confirm that no Phase 2E remote branch or PR exists and that the Phase 2D parent ref remains unchanged. If unavailable, report that explicitly without guessing.

4. Exact defect to remediate

The independent review identified one Medium-severity correctness defect:

F-01 — semantic duplicate datasets can be falsely classified as conflicting

Relevant implementation locations are currently in:

src/backend/app/recipes/dependency_fingerprint.py

The review identified duplicate-record comparisons around the current lines 87 and 113.

The code currently canonicalizes DatasetRecord.required_columns by sorting it when producing the semantic entity payload and fingerprint. However, duplicate detection uses raw Pydantic model equality.

Consequently, two records with:

* the same entity reference;
* the same semantic attributes;
* required_columns=("A", "B") in one record;
* required_columns=("B", "A") in the other;

produce the same entity fingerprint but are incorrectly rejected as conflicting duplicates.

This violates the accepted requirement that semantically equivalent duplicates be insensitive to ordering while genuinely different records still fail closed.

5. Permitted repository edits

Modify only:

1. kmai-td-genie/src/backend/app/recipes/dependency_fingerprint.py
2. kmai-td-genie/test/test_recipe_dependency_fingerprint.py

Do not modify any other source, test, ADR, configuration, deployment, frontend, orchestration, authorization, provider, recipe, or metadata file.

If correct remediation genuinely requires another repository file, stop without expanding scope and return:

PHASE_2E_F01_REMEDIATION_BLOCKED_SCOPE_EXPANSION

6. Required implementation behavior

Implement one consistent semantic-equivalence definition for governed dependency records.

Use the same canonical semantic payload that defines entity identity and entity fingerprints.

Correct both duplicate-detection paths:

1. direct dependency-fingerprint input processing;
2. snapshot-based dependency resolution through resolve_dependency_records().

Requirements:

* Do not use raw Pydantic model equality to decide semantic duplicate equivalence.
* Prefer comparing canonical semantic payloads directly.
* Do not make required_columns order semantically significant.
* Do not remove the existing canonical sorting of required_columns.
* Do not compare only truncated or collision-prone values.
* Preserve rejection of genuinely conflicting duplicate records.
* Preserve deterministic unknown-reference failure.
* Preserve entity-reference ordering and input-order independence.
* Preserve the existing ef- and df- full SHA-256 fingerprint formats.
* Preserve the current pilot fingerprint when its governed entities have not changed.
* Preserve all current Phase 2E behavior outside F-01.
* Do not add lifecycle, persistence, caching, graph, authorization, provider, runtime-activation, or Phase 2F behavior.

Avoid unrelated refactoring, renaming, formatting, abstraction, or cleanup.

7. Required focused regression tests

Add narrowly focused tests to:

test/test_recipe_dependency_fingerprint.py

At minimum, prove all three cases:

Case 1 — direct iterable semantic duplicate

Create two DatasetRecord values with:

* the same dataset/entity reference;
* otherwise identical semantic attributes;
* reversed required_columns ordering.

Verify:

* their canonical entity fingerprints are identical;
* dependency fingerprint computation does not raise a conflict;
* the result is equivalent to supplying only one canonical record;
* input ordering does not alter the result.

Case 2 — snapshot resolution semantic duplicate

Construct the equivalent duplicate condition inside a snapshot or snapshot-like input used by resolve_dependency_records().

Verify:

* both equivalent records resolve as one semantic dependency;
* no ConflictingDependencyRecordError is raised;
* the dependency fingerprint remains deterministic and stable.

Case 3 — genuine semantic conflict

Use the same entity reference with a materially different required_columns set, not merely reordered values.

Verify:

* ConflictingDependencyRecordError is still raised;
* both the direct path and snapshot-resolution path remain fail-closed where applicable.

Do not weaken or delete any existing tests.

8. Mandatory invariants

After remediation, independently prove that:

* existing normal entity fingerprints are unchanged;
* the current pilot dependency fingerprint remains unchanged:
    df-5018e97c00917aaa455c71b0c7ca7d42eeac2ea01c0cab2b7449bd490559b425a
* unrelated metadata remains fingerprint-insensitive;
* material changes to referenced entities still change fingerprints;
* removed, renamed, or unknown references still fail deterministically;
* reverse-index behavior is unchanged;
* authorization behavior is unchanged;
* feature-flag-OFF behavior remains exact Phase 2D behavior;
* Phase 2D registry version remains:
    sv-a9dd6c5ac25e1b42
* no relationship is emitted;
* no out-of-scope technology or behavior is introduced.

9. Validation requirements

Run all commands from the permanent Phase 2E repository root.

Avoid test artifacts inside the candidate:

* set PYTHONDONTWRITEBYTECODE=1;
* disable the pytest cache provider;
* direct coverage and JUnit outputs outside the worktree;
* do not run formatters or rewriting tools.

Run, at minimum:

1. the focused dependency-fingerprint test file;
2. the independent-review F-01 reproduction probe;
3. new field-evidence and fingerprint tests together;
4. registry, hierarchy, cache, and version regressions;
5. semantic-plan regressions;
6. Approved Recipe pilot regressions;
7. authorization/no-access regressions;
8. provider-abstraction contract tests;
9. query-recipe and SQL-policy regressions;
10. golden baseline;
11. the complete configured backend suite;
12. the configured coverage gate;
13. git diff --check;
14. checks for every untracked candidate file;
15. provider-neutrality and excluded-technology scans;
16. diagnostics for all changed Python files.

The pre-remediation full-suite baseline was:

* 996 passed;
* 3 skipped;
* 8 warnings;
* coverage 86.87%;
* required coverage 75%;
* golden baseline 10 passed.

The pass count should increase according to the newly added tests. Do not hardcode success based only on an expected count. Report and explain any difference.

10. Candidate-integrity verification

After remediation and validation:

1. confirm only the two permitted repository files changed relative to the pre-remediation candidate;
2. confirm the complete candidate still contains the same 12 paths;
3. confirm the index remains clean;
4. confirm no commit was created;
5. recompute every candidate file SHA-256;
6. recompute the combined candidate digest using the established manifest algorithm;
7. record both the old and new combined digests;
8. prove the post-validation digest matches the post-edit digest;
9. confirm no test or validation command changed candidate bytes.

The new digest must differ from:

1c72d47be76b7e8d2f768005cca0254dd43761212a15637950fcfb0ed6d7cc35

because the source and test corrections are intentional.

11. Prohibited actions

Do not:

* modify the independent-review report;
* modify the original implementation report;
* modify ADR 0005 unless a new contradiction is discovered—in that case stop and report it instead;
* stage files;
* commit or amend;
* push;
* create or modify a PR;
* alter PR #15 or PR #16;
* rebase, merge, cherry-pick, reset, stash, clean, or switch branches;
* modify Git configuration;
* enable runtime configuration;
* start Phase 2F;
* implement any deferred lifecycle;
* introduce Redis, graphs, relationships, Databricks, Genie, Unity Catalog, Collibra, frontend, deployment, Terraform, or authorization changes.

12. Remediation report

Write the remediation report outside the Git candidate:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_REMEDIATION_2026-08-23.md

The report must include:

1. final verdict;
2. pre-remediation identity and digest;
3. exact F-01 root cause;
4. exact source correction;
5. why canonical semantic-payload comparison is correct;
6. complete changed-line and changed-file inventory;
7. focused tests added;
8. direct-path reproduction before and after;
9. snapshot-resolution reproduction before and after;
10. genuine-conflict preservation proof;
11. all focused and full validation commands and results;
12. coverage and golden-baseline results;
13. pilot fingerprint and flag-off compatibility proof;
14. authorization and scope-boundary proof;
15. new per-file hashes and combined digest;
16. pre-validation versus post-validation candidate identity;
17. attestation that nothing was staged, committed, pushed, or opened as a PR;
18. exact targeted re-review scope.

End with exactly one token:

* PHASE_2E_F01_REMEDIATION_READY_FOR_TARGETED_REREVIEW
* PHASE_2E_F01_REMEDIATION_FAILED
* PHASE_2E_F01_REMEDIATION_BLOCKED_CANDIDATE_DRIFT
* PHASE_2E_F01_REMEDIATION_BLOCKED_SCOPE_EXPANSION
* PHASE_2E_F01_REMEDIATION_BLOCKED_ENVIRONMENT

A successful remediation does not authorize commit, push, PR creation, runtime activation, merge, or Phase 2F. The next permitted action is a targeted independent re-review of F-01 plus full validation.
