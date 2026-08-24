AskTD / KMAI — Phase 2E F-01 Targeted Independent Re-review

You are performing the targeted independent re-review of the Phase 2E F-01 remediation.

This is a read-only review task. It is not an implementation, remediation, commit, push, PR, merge, runtime-activation, or Phase 2F task.

Perform this review in a separate independent-review session, not in the session that implemented the remediation.

1. Mandatory workspace

Use only:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records

Repository implementation root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

Expected branch:

phase2/governed-field-records

Do not access or modify the stale primary checkout on branch asktd_v2.

2. Strict mutation boundary

You MUST NOT:

* edit repository files;
* apply fixes or formatting;
* stage files;
* create or amend commits;
* push;
* create or modify PRs;
* switch, rebase, merge, cherry-pick, reset, stash, clean, or delete branches;
* modify Git configuration;
* modify existing implementation, review, or remediation reports;
* modify deployment or runtime configuration;
* enable feature flags outside process-local test execution;
* start Phase 2F.

The only permitted persistent write is this new report outside the Git candidate:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_TARGETED_INDEPENDENT_REREVIEW_2026-08-23.md

If a review command unexpectedly changes candidate bytes or Git state, stop immediately. Do not restore or clean anything. Report the exact change.

3. Required reports

Read these three reports completely before reviewing code:

1. Phase 2E implementation report:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_IMPLEMENTATION_2026-08-23.md
2. Original independent review:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_INDEPENDENT_REVIEW_2026-08-23.md
3. F-01 remediation report:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_REMEDIATION_2026-08-23.md

Treat the reports as evidence indexes only. Independently verify the remediation and its results.

Do not reopen unrelated Phase 2E behavior that already passed unless the current remediation changed or invalidated it.

4. Candidate identity gate

Before substantive review, verify:

* branch is phase2/governed-field-records;
* local HEAD remains exactly:
    5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
* HEAD is the accepted Phase 2D parent;
* zero commits exist beyond the parent;
* Git index is clean;
* all candidate changes remain unstaged and uncommitted;
* the candidate contains exactly the same 12 expected paths;
* there are exactly 7 tracked modifications and 5 untracked candidate files;
* no unrelated candidate file exists;
* no remote Phase 2E branch exists;
* no Phase 2E PR exists.

Expected post-remediation combined candidate SHA-256:

d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be

Expected pre-remediation digest:

1c72d47be76b7e8d2f768005cca0254dd43761212a15637950fcfb0ed6d7cc35

Independently recompute the current combined digest:

1. use the exact 12 workspace-relative candidate paths;
2. sort paths bytewise;
3. hash each complete file with SHA-256;
4. create each manifest line as:
    <lowercase-sha256><two spaces><workspace-relative-path>\n
5. hash the complete 12-line manifest, including the final newline.

If the current digest differs from the expected post-remediation digest, stop and return:

PHASE_2E_F01_TARGETED_REREVIEW_BLOCKED_CANDIDATE_DRIFT

If authenticated remote access is available, verify read-only that these refs remain unchanged:

* origin/main:
    9ca6567571772a9f4e1ab555d8a678e678c45d49
* origin/phase2/provider-abstraction-foundation:
    d5472ae31081879329c224922244d87962737e8c
* origin/phase2/approved-recipe-pilot:
    5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

If remote access is unavailable, state that explicitly without guessing.

5. Exact targeted code-review scope

The remediation was permitted to change only:

1. kmai-td-genie/src/backend/app/recipes/dependency_fingerprint.py
2. kmai-td-genie/test/test_recipe_dependency_fingerprint.py

Review every changed line in both files.

Independently verify that no third repository file changed relative to the pre-remediation candidate.

The remediation report states that runtime code added a semantic-equivalence helper and changed both duplicate-detection paths to use canonical semantic payload comparison.

Confirm this from source, not from the report.

6. Required F-01 source review

Verify that the implementation now uses one consistent definition of semantic equivalence.

Specifically verify:

* semantic duplicate equivalence is derived from the same canonical semantic payload used by entity_fingerprint();
* raw Pydantic model equality is no longer used for duplicate conflict decisions;
* both duplicate-detection paths use the corrected comparison:
    1. direct dependency_fingerprint(records) processing;
    2. snapshot-based resolve_dependency_records(snapshot, refs) processing;
* DatasetRecord.required_columns remains canonicalized as an order-insensitive sorted representation;
* reordered equivalent values are treated as one semantic record;
* materially different values remain conflicting;
* canonical payload comparison is direct and does not rely only on hash equality;
* record type remains part of semantic identity;
* dataset and field semantic attributes remain correctly separated;
* unknown references remain fail-closed;
* deterministic reference and error ordering remain unchanged;
* fingerprint formats remain full SHA-256 with ef- and df- prefixes;
* reverse-index behavior remains unchanged;
* no unrelated refactor or scope expansion was introduced.

Inspect callers and type behavior sufficiently to ensure the new helper cannot accidentally classify different record types or materially different entity records as equivalent.

7. Independent reproduction requirements

Do not rely only on the newly added tests.

Create process-local, non-persistent reproduction probes that exercise production code directly.

Probe A — direct semantic duplicate

Construct two DatasetRecord values with:

* the same entity reference;
* identical semantic attributes;
* required_columns=("A", "B");
* required_columns=("B", "A").

Verify independently:

* raw object equality may differ;
* canonical semantic payloads are equal;
* entity fingerprints are equal;
* direct dependency fingerprinting does not raise;
* the equivalent duplicate produces the same dependency fingerprint as one record;
* reversing input record order produces the same result.

Probe B — snapshot semantic duplicate

Place equivalent reordered duplicates in the snapshot path consumed by resolve_dependency_records().

Verify:

* they resolve as one semantic dependency;
* no ConflictingDependencyRecordError is raised;
* reversed snapshot ordering produces the same result;
* the resulting dependency fingerprint is stable.

Probe C — genuine conflict

Use the same entity reference with a materially different required-column set.

Verify:

* direct processing raises ConflictingDependencyRecordError;
* snapshot resolution raises the same deterministic error;
* the exact conflicting entity reference is preserved safely;
* conflict detection was not weakened.

Probe D — field-record regression

Verify that:

* identical FieldRecord duplicates remain equivalent;
* materially different field records with the same reference remain conflicting;
* unknown field references remain deterministically rejected.

8. Test-quality review

Review the three new focused tests and determine whether they genuinely exercise production behavior.

Confirm coverage for:

1. direct reordered semantic duplicates;
2. snapshot-resolved reordered semantic duplicates;
3. genuine material conflicts;
4. input-order invariance;
5. single-record versus equivalent-duplicate fingerprint equality;
6. both duplicate-detection locations.

Reject tests that merely reproduce helper output without exercising the public behavior.

Confirm that no existing test was removed, weakened, skipped, or converted into a non-asserting check.

9. Required invariant checks

Verify that the remediation did not change:

* normal entity fingerprint construction;
* dependency-reference sorting;
* deterministic error behavior;
* unknown-reference failure;
* referenced-entity change sensitivity;
* unrelated-metadata insensitivity;
* reverse-index behavior;
* field-evidence emission;
* semantic-plan validation ordering;
* authorization behavior;
* provider neutrality;
* relationship count;
* feature-flag-OFF Phase 2D behavior;
* accepted Phase 2E scope boundaries.

The current pilot dependency fingerprint must remain exactly:

df-5018e97c00917aaa455c71b0c7ca7d42eeac2ea01c0cab2b7449bd490559b425a

With GOVERNED_FIELD_RECORDS_ENABLED absent or false, verify:

* fields: 0;
* relationships: 0;
* no recipe field references or dependency fingerprint are consulted;
* exact Phase 2D registry version:
    sv-a9dd6c5ac25e1b42

With governed fields enabled, the Phase 2E registry version should remain:

sv-4d6de9b05c3abe43

No runtime or deployment flag should be changed.

10. Validation requirements

Run all validations from the permanent Phase 2E repository root.

Prevent avoidable worktree artifacts:

* set PYTHONDONTWRITEBYTECODE=1;
* disable the pytest cache provider;
* direct coverage and JUnit output outside the worktree;
* do not run formatters or rewriting tools.

Run at minimum:

1. test/test_recipe_dependency_fingerprint.py;
2. the independent F-01 reproduction probes;
3. new field-evidence and fingerprint tests together;
4. registry, hierarchy, cache, and version regressions;
5. semantic-plan regressions;
6. Approved Recipe pilot regressions;
7. authorization/no-access regressions;
8. provider-abstraction contract tests;
9. query-recipe and SQL-policy regressions;
10. golden baseline;
11. the complete configured backend suite;
12. configured coverage gate;
13. git diff --check;
14. index diff check;
15. untracked-file content checks;
16. diagnostics on all candidate Python files;
17. provider-neutrality scan;
18. excluded-technology and Phase 2F scope scans.

The remediation reported:

* focused fingerprint suite: 12 passed;
* field-evidence and fingerprint suites: 31 passed;
* registry/hierarchy/cache/version: 149 passed;
* semantic-plan regressions: 51 passed;
* authorization/no-access: 29 passed;
* provider abstraction: 7 passed;
* query-recipe and SQL-policy: 59 passed;
* golden baseline: 10 passed;
* full backend: 999 passed, 3 skipped, 8 warnings;
* coverage: 86.90%;
* required coverage: 75%.

Reproduce these independently. Explain any difference.

11. Scope-exclusion verification

Confirm that the remediation introduced no:

* lifecycle or reapproval implementation;
* relationship emission;
* metadata, join, or lineage graph;
* graph database;
* Redis or distributed/query-result cache;
* Databricks, Genie, Unity Catalog, or Collibra integration;
* cross-source execution;
* SQL dialect compiler;
* provider SDK;
* authorization-engine or row/column authorization change;
* frontend, deployment, Terraform, migration, or Orchestrator change;
* extra Approved Recipe;
* Phase 2F implementation.

Documentation and negative-test references are acceptable. Runtime implementation is not.

12. Post-validation integrity gate

After all review and validation:

* recheck branch and HEAD;
* confirm the index remains clean;
* confirm no commit was created;
* confirm the exact same 12 candidate paths remain;
* recompute every file hash;
* recompute the combined digest;
* confirm it remains:
    d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be
* confirm no remote Phase 2E branch or PR appeared;
* confirm no report or repository file except the permitted new re-review report was written.

If candidate bytes changed during review, do not clean or repair them. Return a blocked verdict with exact evidence.

13. Finding and verdict policy

Do not fix any finding.

For every finding, report:

* severity;
* confidence;
* exact file and line;
* violated requirement;
* concrete reproduction;
* behavioral/security impact;
* narrowly bounded recommendation;
* required re-review scope.

A PASS requires:

* exact candidate identity;
* correct remediation in both paths;
* successful independent reproduction;
* preservation of genuine conflict failure;
* all targeted and complete validations passing;
* unchanged pilot and flag-off identities;
* no unrelated regression or scope expansion;
* byte-for-byte unchanged candidate after review.

14. Targeted re-review report

Write only:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_TARGETED_INDEPENDENT_REREVIEW_2026-08-23.md

Include:

1. final verdict;
2. reviewer-independence statement;
3. parent, branch, worktree, and remote identity;
4. exact 12-file inventory and combined digest;
5. exact two-file targeted review scope;
6. source-review findings;
7. test-quality findings;
8. direct-path independent reproduction;
9. snapshot-path independent reproduction;
10. genuine-conflict preservation proof;
11. FieldRecord regression proof;
12. fingerprint and flag-off invariants;
13. complete validation commands and results;
14. coverage and golden-baseline results;
15. authorization and scope-boundary proof;
16. pre-review versus post-review candidate identity;
17. findings and required actions;
18. completion-state attestation confirming no mutation, staging, commit, push, or PR.

End with exactly one token:

* PHASE_2E_F01_TARGETED_REREVIEW_PASS
* PHASE_2E_F01_TARGETED_REREVIEW_FAIL
* PHASE_2E_F01_TARGETED_REREVIEW_BLOCKED_CANDIDATE_DRIFT
* PHASE_2E_F01_TARGETED_REREVIEW_BLOCKED_ENVIRONMENT

A PASS means the remediated uncommitted Phase 2E candidate has passed the required targeted independent re-review. It does not authorize commit, push, PR creation, merge, runtime activation, or Phase 2F.
