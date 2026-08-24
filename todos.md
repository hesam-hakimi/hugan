AskTD / KMAI — Phase 2E F-01 Targeted Independent Re-review Rerun

You are rerunning the complete targeted independent re-review of the Phase 2E F-01 remediation.

The previous re-review found no technical defect, but it could not issue a PASS because that session read an unrelated instruction file from the prohibited stale primary checkout.

This rerun must be procedurally clean and technically independent.

1. Immediate workspace gate

Before reading any project file, run a read-only current-directory check.

The exact required repository root is:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

If the current working directory is not exactly that physical repository root:

* do not search for the repository;
* do not inspect parent or sibling directories;
* do not continue the review;
* return:

PHASE_2E_F01_TARGETED_REREVIEW_RERUN_BLOCKED_WRONG_WORKSPACE

The currently opened VS Code folder must be this exact Phase 2E implementation root, not:

* a multi-root workspace;
* the worktrees parent directory;
* the stale primary checkout;
* branch asktd_v2;
* any other AskTD, ETL, or UCA project.

2. Mandatory read boundary

During this entire rerun, project-related reads are permitted only from:

1. the exact Phase 2E repository root:
    /home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie
2. these exact three reports:
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_IMPLEMENTATION_2026-08-23.md
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_INDEPENDENT_REVIEW_2026-08-23.md
    /home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_REMEDIATION_2026-08-23.md

Do not read or search:

* the stale primary checkout;
* /home/tag5916/projects/kmai-td-genie;
* any parent or sibling repository;
* any unrelated AGENTS.md, instruction file, handoff, task file, report, branch, or workspace;
* the previous failed targeted re-review report, if it exists;
* ETL or UCA files.

Do not use commands such as find .., rg .., or recursive searches beginning outside the exact Phase 2E repository root.

Normal Git commands executed from the required repository root are permitted. Read-only remote verification is permitted.

If any prohibited project file is read, stop and return:

PHASE_2E_F01_TARGETED_REREVIEW_RERUN_FAIL_WORKSPACE_BOUNDARY

Do not reuse technical conclusions from the previous procedurally failed re-review. Reproduce the required evidence independently.

3. Mutation boundary

This is a read-only review.

Do not:

* edit repository files;
* apply formatting or fixes;
* stage files;
* create or amend commits;
* push;
* create or modify PRs;
* switch branches;
* rebase, merge, cherry-pick, reset, stash, clean, or delete;
* modify Git configuration;
* modify runtime or deployment configuration;
* enable feature flags outside process-local tests;
* start Phase 2F;
* modify any existing report.

The only permitted persistent write is this new rerun report:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_TARGETED_INDEPENDENT_REREVIEW_RERUN_2026-08-23.md

Do not overwrite:

* the implementation report;
* the original independent-review report;
* the F-01 remediation report;
* the prior failed targeted re-review report.

If a command unexpectedly changes candidate bytes or Git state, stop. Do not restore or clean anything.

4. Read prerequisites

After the workspace gate passes, read the three permitted reports completely in this order:

1. Phase 2E implementation report;
2. original independent-review report;
3. F-01 remediation report.

Use them as evidence indexes only. Independently verify the current candidate.

5. Candidate identity gate

Verify:

* branch: phase2/governed-field-records;
* local HEAD:
    5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5
* HEAD remains the accepted Phase 2D parent;
* zero commits exist beyond that parent;
* Git index is clean;
* all candidate changes are unstaged and uncommitted;
* candidate inventory contains exactly 12 expected paths;
* exactly 7 tracked modifications and 5 untracked candidate files exist;
* no unrelated candidate path exists;
* no remote Phase 2E branch exists;
* no Phase 2E PR exists.

Expected current combined candidate SHA-256:

d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be

Independently recompute the digest using the established algorithm:

1. use the exact 12 workspace-relative candidate paths;
2. sort paths bytewise;
3. SHA-256 each complete file;
4. create each manifest line as:
    <lowercase-sha256><two spaces><workspace-relative-path>\n
5. SHA-256 the complete 12-line manifest including the final newline.

If the digest or candidate inventory differs, return:

PHASE_2E_F01_TARGETED_REREVIEW_RERUN_BLOCKED_CANDIDATE_DRIFT

If authenticated remote access is available, verify read-only:

* origin/main:
    9ca6567571772a9f4e1ab555d8a678e678c45d49
* origin/phase2/provider-abstraction-foundation:
    d5472ae31081879329c224922244d87962737e8c
* origin/phase2/approved-recipe-pilot:
    5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

Do not fetch or alter local refs. If remote verification is unavailable, state that explicitly.

6. Exact targeted source scope

Review every line changed by F-01 in:

1. src/backend/app/recipes/dependency_fingerprint.py
2. test/test_recipe_dependency_fingerprint.py

Verify no third repository file changed relative to the pre-remediation candidate.

Confirm independently that:

* canonical semantic payload defines duplicate equivalence;
* raw Pydantic model equality is no longer used for duplicate conflict decisions;
* direct dependency_fingerprint(records) processing uses the corrected comparison;
* snapshot-based resolve_dependency_records(snapshot, refs) uses the corrected comparison;
* reordered DatasetRecord.required_columns values are semantically equivalent;
* materially different required-column sets remain conflicting;
* semantic payload dictionaries are compared directly;
* comparison does not rely only on fingerprint/hash equality;
* record type participates in semantic identity;
* DatasetRecord and FieldRecord attributes remain correctly separated;
* unknown references remain fail-closed;
* deterministic error and reference ordering remain unchanged;
* ef- and df- retain full SHA-256 formats;
* reverse-index behavior is unchanged;
* no unrelated refactor or scope expansion exists.

7. Independent production-code probes

Do not rely only on candidate tests.

Run non-persistent, process-local probes against production code.

Probe A — direct equivalent duplicates

Create two DatasetRecords with:

* the same entity reference;
* identical semantic attributes;
* required columns ("A", "B") and ("B", "A").

Verify:

* canonical semantic payloads are equal;
* entity fingerprints are equal;
* dependency fingerprinting succeeds;
* equivalent duplicates produce the same dependency fingerprint as one record;
* reversed record order produces the same result.

Probe B — snapshot equivalent duplicates

Place the same reordered duplicates in a RegistrySnapshot used by resolve_dependency_records().

Verify:

* they resolve as one dependency;
* no conflict exception is raised;
* reversed snapshot order produces the same result.

Probe C — genuine dataset conflict

Use the same dataset reference with a materially different required-column set.

Verify direct and snapshot paths both raise deterministic ConflictingDependencyRecordError.

Probe D — FieldRecord regression

Verify:

* identical FieldRecord duplicates remain equivalent;
* materially different FieldRecords with the same reference remain conflicting;
* unknown field references remain rejected.

8. Test-quality review

Review the three F-01 tests.

Confirm that they exercise production behavior and prove:

* direct reordered duplicates;
* snapshot reordered duplicates;
* input-order invariance;
* single-record versus equivalent-duplicate fingerprint equality;
* genuine-conflict preservation;
* both duplicate-detection paths.

Confirm no existing test was removed, weakened, skipped, or converted into a non-asserting check.

9. Invariant verification

Verify that remediation did not change:

* normal entity fingerprints;
* dependency-reference sorting;
* deterministic failure behavior;
* unknown-reference failure;
* referenced-entity change sensitivity;
* unrelated-metadata insensitivity;
* reverse index;
* field emission;
* semantic-plan validation order;
* authorization;
* provider neutrality;
* relationship count;
* flag-off Phase 2D behavior;
* Phase 2E scope boundaries.

Important transcription rule:

Do not rely on a manually copied pilot fingerprint from the previous prompt. That prompt may have contained an extra character.

Instead:

1. derive the pilot fingerprint directly from the current production code and governed snapshot;
2. compare it byte-for-byte with the authoritative value recorded in the F-01 remediation report;
3. verify it remains unchanged across the remediation.

With feature flags absent or false, verify:

* fields: 0;
* relationships: 0;
* no governed field refs;
* no dependency fingerprint;
* exact Phase 2D registry version:
    sv-a9dd6c5ac25e1b42

With governed fields enabled, verify the Phase 2E registry version remains the value recorded in the remediation report and relationships remain zero.

10. Complete validation rerun

Run validations from the exact required repository root.

Use:

* PYTHONDONTWRITEBYTECODE=1;
* pytest cache provider disabled;
* coverage and JUnit outputs outside the repository;
* no formatter or rewriting command.

Run:

1. focused fingerprint suite;
2. all four independent probes;
3. field-evidence and fingerprint suites;
4. registry, hierarchy, cache, and version regressions;
5. semantic-plan regressions;
6. Approved Recipe pilot regressions;
7. authorization/no-access regressions;
8. provider-abstraction contract tests;
9. query-recipe and SQL-policy regressions;
10. golden baseline;
11. complete configured backend suite;
12. configured coverage gate;
13. git diff --check;
14. index diff check;
15. all untracked-file checks;
16. diagnostics for candidate Python files;
17. provider-neutrality scan;
18. excluded-technology and Phase 2F scans.

Expected evidence to reproduce:

* focused fingerprint suite: 12 passed;
* field and fingerprint suites: 31 passed;
* registry/hierarchy/cache/version: 149 passed;
* semantic plan: 51 passed;
* Approved Recipe pilot: 75 passed;
* authorization/no-access: 29 passed;
* provider abstraction: 7 passed;
* query recipe and SQL policy: 59 passed;
* golden baseline: 10 passed;
* full backend: 999 passed, 3 skipped, 8 warnings;
* coverage approximately 86.90%;
* required coverage: 75%.

Explain any difference. Do not declare PASS based only on counts.

11. Scope exclusions

Confirm no implementation was added for:

* lifecycle or reapproval;
* relationship emission;
* metadata, join, or lineage graphs;
* graph database;
* Redis or distributed/query-result caching;
* Databricks, Genie, Unity Catalog, or Collibra;
* cross-source execution;
* SQL dialect compilation;
* new provider SDK;
* new authorization engine or row/column authorization;
* frontend, deployment, Terraform, migrations, or Orchestrator changes;
* extra Approved Recipes;
* Phase 2F.

12. Final integrity check

After review:

* verify branch and HEAD again;
* verify clean index;
* verify zero commits;
* verify exact 12 candidate paths;
* recompute all hashes;
* verify combined digest remains:
    d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be
* verify no Phase 2E remote branch or PR;
* verify candidate bytes did not change;
* verify no prohibited checkout or project file was read;
* verify only the new rerun report was written.

13. Report and verdict

Write only:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_F01_TARGETED_INDEPENDENT_REREVIEW_RERUN_2026-08-23.md

Include:

1. final verdict;
2. workspace-boundary attestation;
3. exact list of permitted external reports read;
4. reviewer-independence statement;
5. parent, branch, worktree, remote, and PR identity;
6. candidate inventory and digest;
7. two-file source review;
8. test-quality review;
9. direct duplicate probe;
10. snapshot duplicate probe;
11. genuine-conflict probe;
12. FieldRecord probe;
13. fingerprint and flag-off invariants;
14. complete validation commands and results;
15. authorization and scope-boundary proof;
16. pre-review versus post-review candidate identity;
17. findings;
18. attestation that nothing was edited, staged, committed, pushed, or opened as a PR.

End with exactly one token:

* PHASE_2E_F01_TARGETED_REREVIEW_RERUN_PASS
* PHASE_2E_F01_TARGETED_REREVIEW_RERUN_FAIL
* PHASE_2E_F01_TARGETED_REREVIEW_RERUN_FAIL_WORKSPACE_BOUNDARY
* PHASE_2E_F01_TARGETED_REREVIEW_RERUN_BLOCKED_WRONG_WORKSPACE
* PHASE_2E_F01_TARGETED_REREVIEW_RERUN_BLOCKED_CANDIDATE_DRIFT
* PHASE_2E_F01_TARGETED_REREVIEW_RERUN_BLOCKED_ENVIRONMENT

A PASS means only that the uncommitted Phase 2E candidate passed the procedurally clean targeted independent re-review. It does not authorize commit, push, PR creation, merge, runtime activation, or Phase 2F.
