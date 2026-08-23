AskTD / KMAI — Phase 2E Independent Review Prompt

You are performing an independent review of the already-implemented Phase 2E candidate.

This is a review task, not an implementation or remediation task.

1. Mandatory safety boundary

Work only in this permanent Phase 2E worktree:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records

Repository implementation root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

Do not use or modify the stale primary checkout on branch asktd_v2.

You MUST NOT:

* edit repository files;
* apply fixes or formatting;
* stage files;
* create commits;
* amend commits;
* push branches;
* create or modify PRs;
* rebase, merge, cherry-pick, reset, stash, clean, switch, or delete branches;
* modify Git configuration;
* modify deployment or environment configuration;
* enable runtime feature flags outside process-local test execution;
* start Phase 2F;
* alter PR #15, PR #16, or main.

The only permitted persistent write is the independent-review report outside the Git candidate:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_INDEPENDENT_REVIEW_2026-08-23.md

If any review command unexpectedly modifies the worktree, stop immediately. Do not clean, restore, or overwrite anything. Report the exact modification.

2. Review independence

Do not assume the implementation report is correct.

You may read it as an evidence index, but independently verify every material claim:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_IMPLEMENTATION_2026-08-23.md

Do not redesign accepted Phase 2C, Phase 2C.5, or Phase 2D behavior.

Do not expand the Phase 2E scope.

3. Expected immutable parent and candidate identity

The expected Phase 2D parent SHA is:

5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

The expected local branch is:

phase2/governed-field-records

The expected branch state is:

* local HEAD remains exactly at the Phase 2D parent SHA;
* all Phase 2E candidate changes are unstaged and uncommitted;
* no remote phase2/governed-field-records ref exists;
* no Phase 2E commit or PR exists;
* the candidate contains exactly 12 repository files: 5 new and 7 modified.

Expected combined candidate SHA-256:

1c72d47be76b7e8d2f768005cca0254dd43761212a15637950fcfb0ed6d7cc35

Before reviewing code, verify:

1. current working directory and repository root;
2. current branch and exact HEAD;
3. clean index;
4. unstaged and untracked inventory;
5. absence of unexpected commits;
6. absence of unrelated files;
7. exact parent relationship;
8. whether the expected remote Phase 2E branch is still absent;
9. whether main, Phase 2C.5, and Phase 2D remote refs remain at their expected SHAs, if authenticated remote access is available.

Expected remote SHAs:

* origin/main:
    9ca6567571772a9f4e1ab555d8a678e678c45d49
* origin/phase2/provider-abstraction-foundation:
    d5472ae31081879329c224922244d87962737e8c
* origin/phase2/approved-recipe-pilot:
    5d267fdac75c5e76ab13f93ae0eb2bbb999b08a5

If remote access is unavailable, state that explicitly. Do not infer remote state.

If the parent SHA, candidate inventory, or candidate digest differs, stop the behavioral review and return:

PHASE_2E_INDEPENDENT_REVIEW_BLOCKED_CANDIDATE_DRIFT

4. Expected candidate files

New files

1. kmai-td-genie/docs/adr/0005-phase2e-governed-field-records.md
2. kmai-td-genie/src/backend/app/available_data/field_evidence.py
3. kmai-td-genie/src/backend/app/recipes/dependency_fingerprint.py
4. kmai-td-genie/test/test_governed_field_records.py
5. kmai-td-genie/test/test_recipe_dependency_fingerprint.py

Modified files

1. kmai-td-genie/docs/adr/README.md
2. kmai-td-genie/src/backend/app/available_data/registry_contract.py
3. kmai-td-genie/src/backend/app/recipes/approved_recipes.py
4. kmai-td-genie/test/test_approved_recipe_pilot.py
5. kmai-td-genie/test/test_authz_no_access_guard.py
6. kmai-td-genie/test/test_provider_abstraction_contracts.py
7. kmai-td-genie/test/test_semantic_plan_contract.py

Verify all 12 files, including untracked files. Do not rely only on ordinary git diff, because it omits untracked files.

Recompute the combined digest independently:

1. sort the 12 workspace-relative paths bytewise;
2. SHA-256 each complete file;
3. create one line per file in this exact form:
    <lowercase-sha256><two spaces><workspace-relative-path>\n
4. hash the complete 12-line manifest, including the final newline;
5. compare it to the expected combined digest.

5. Phase 2E bounded objective

Independently determine whether the candidate correctly:

* emits real, strictly evidenced FieldRecord objects;
* emits fields only for datasets already governed;
* never invents datasets, schemas, Product Groups, relationships, fields, or business meaning;
* adds canonical governed field references only to the single Phase 2D pilot ApprovedRecipe;
* computes deterministic, entity-scoped dependency fingerprints;
* prevents unrelated metadata changes from invalidating the recipe;
* changes the dependency fingerprint when a referenced entity materially changes;
* fails closed when a referenced field is missing, renamed, unknown, ambiguous, or invalid;
* preserves exact Phase 2D behavior when the Phase 2E feature flag is OFF.

6. Minimum source review

Review every line of all 12 candidate files.

At minimum, perform a detailed behavioral review of:

1. src/backend/app/available_data/field_evidence.py
2. src/backend/app/available_data/registry_contract.py
3. src/backend/app/recipes/dependency_fingerprint.py
4. src/backend/app/recipes/approved_recipes.py

Review ADR 0005 and its index entry for consistency with the code and bounded scope.

Review all six changed test files. Determine whether the assertions genuinely prove the required behavior rather than merely exercising code paths.

7. Field-evidence review requirements

Verify independently that:

* data/metadata/json/field.json is the authoritative field-evidence input;
* the live file contains 328 rows;
* exactly 199 evidenced rows map to the already-governed pilot dataset;
* rows for non-governed datasets do not cause new datasets or fields to be invented;
* field identity is exact and case-sensitive;
* canonical IDs use:
    field:<logical_dataset_id>.<exact_COLUMN_NAME>
* whitespace, punctuation, prefixes, empty components, duplicate canonical IDs, ambiguous mappings, invalid required values, malformed JSON, unsupported IS_KEY values, and inconsistent governed source context fail deterministically where required;
* display names do not substitute inferred business meaning;
* descriptive classifications do not grant authorization;
* evidence ordering cannot change canonical output or registry identity;
* safe error output does not disclose complete evidence rows, business descriptions, classifications, or filesystem paths.

Confirm that relationship evidence is not emitted and no RelationshipRecord is introduced.

8. Pilot recipe reference review

Inspect the authoritative Phase 2D pilot builder directly.

Verify that its actual SQL/data access requires exactly these four evidenced fields:

1. field:v_dlv_dep_agmt_clr.CUR_BAL_AMT
2. field:v_dlv_dep_agmt_clr.RRDW_SRC_CD
3. field:v_dlv_dep_agmt_clr.RRDN_AS_OF_DT
4. field:v_dlv_dep_agmt_clr.AGMT_CD

Confirm that:

* all four exist verbatim in current evidence;
* no required source field is omitted;
* no derived alias, output-format field, parameter label, trace field, or unrelated field was added;
* no second recipe was created;
* no legacy recipe was migrated.

9. Semantic-plan and fail-closed review

Verify the complete enabled execution order:

1. recipe lifecycle and parameter validation;
2. live registry/version resolution;
3. semantic-plan construction using governed dataset and field references;
4. service-level governed semantic-plan validation;
5. dependency-fingerprint computation only after successful validation;
6. authoritative builder resolution and invocation only after all governance checks pass.

For missing, removed, renamed, or unknown referenced fields, verify:

* deterministic failure;
* expected error code such as plan_unknown_field, where applicable;
* zero data-source factory activity;
* zero adapter or schema-probe activity;
* zero builder resolution;
* zero authoritative or legacy builder invocation;
* zero SQL execution.

10. Dependency-fingerprint review

Verify that fingerprinting is:

* deterministic;
* canonical;
* entity-scoped;
* independent of input ordering;
* insensitive to equivalent duplicates;
* sensitive to conflicting duplicates;
* sensitive to materially changed referenced dataset or field attributes;
* insensitive to unrelated datasets and unreferenced fields;
* independent of whole-registry version changes when referenced entities are unchanged;
* fail-closed for unknown references.

Review which DatasetRecord and FieldRecord attributes are included and determine whether they represent the intended dependency semantics without accidentally incorporating unrelated global state.

Confirm that no historical approved fingerprint is persisted or compared and that no future lifecycle status is assigned.

11. Reverse-index review

Verify that the reverse index:

* maps each governed entity reference to a deterministically sorted tuple of approved recipe IDs;
* de-duplicates equivalent references and recipe IDs;
* is pure and in-memory;
* has no persistence;
* has no external API;
* is not a metadata graph, join graph, lineage graph, or graph database;
* has no Redis or cache dependency.

12. Compatibility and separation review

Verify that with GOVERNED_FIELD_RECORDS_ENABLED absent or false:

* field.json is not read;
* emitted fields remain empty;
* relationships remain empty;
* the exact Phase 2D registry version is restored:
    sv-a9dd6c5ac25e1b42
* Phase 2D recipe behavior remains dataset-only;
* recipe field references and dependency fingerprints are not consulted or traced.

Verify that authorization remains independent:

* no authorization source or contract changed;
* metadata classifications do not grant or deny access;
* existing EffectivePermissions, SQL policy, SQL authorization, auditing, and denial behavior remain authoritative.

13. Explicit scope exclusions

Confirm through diff inspection and case-insensitive source scanning that the candidate contains no implementation, stub, adapter, or import for:

* lifecycle states VALID, REVIEW_REQUIRED, BROKEN, or NOT_APPROVED;
* approval or reapproval workflows;
* relationship emission;
* metadata, join, or lineage graphs;
* graph databases;
* Redis or distributed caching;
* query-result caching;
* Databricks;
* Genie;
* Unity Catalog;
* Collibra;
* Event Hubs, Kafka, or message buses;
* cross-source execution or joins;
* SQL dialect compilers;
* new provider SDKs;
* new authorization engines;
* row/column authorization;
* frontend work;
* deployment or Terraform changes;
* Orchestrator decomposition;
* schema or data migrations;
* extra Approved Recipes;
* Phase 2F work.

Documentation-only non-goal references and negative test constants are acceptable. Runtime implementation is not.

14. Validation execution

Run validation from the permanent Phase 2E repository root.

Prevent avoidable review artifacts:

* set PYTHONDONTWRITEBYTECODE=1;
* disable the pytest cache provider;
* direct coverage data outside the Git candidate if needed;
* do not run auto-formatters or commands that rewrite files.

Run at least:

1. new field-evidence/emission tests;
2. new dependency-fingerprint and reverse-index tests;
3. registry, hierarchy, and version regressions;
4. semantic-plan regressions;
5. Approved Recipe pilot regressions;
6. authorization/no-access regressions;
7. provider-abstraction contract tests;
8. query-recipe and SQL-policy regressions;
9. golden baseline;
10. the complete configured backend test suite;
11. the configured coverage gate;
12. git diff --check;
13. checks covering untracked candidate files;
14. provider-neutrality and excluded-technology scans.

The previous implementation evidence reported:

* full backend: 996 passed, 3 skipped;
* coverage: 86.87%, required 75%;
* golden baseline: 10 passed;
* warnings: 8 existing warnings;
* no increase in skips;
* no changed-Python-file diagnostics;
* all diff and excluded-technology scans passed.

Do not treat those values as authoritative. Reproduce them independently and explain any difference.

After all validation, compare the final Git status, candidate inventory, per-file hashes, and combined digest with the pre-review capture.

The candidate must remain byte-for-byte unchanged.

15. Defect handling

Do not fix defects.

For every finding, record:

* severity: Blocking / High / Medium / Low;
* exact file and line;
* violated requirement;
* concrete evidence;
* reproduction command or test;
* security or behavioral impact;
* narrowly bounded remediation recommendation;
* whether a full re-review is required.

Any unresolved blocking correctness, security, fail-closed, parent-identity, candidate-drift, authorization-separation, or scope-boundary defect requires a FAIL or BLOCKED verdict.

16. Independent-review report

Write the final report only to:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_INDEPENDENT_REVIEW_2026-08-23.md

The report must include:

1. final verdict;
2. reviewer independence statement;
3. parent, branch, worktree, and remote identity;
4. complete 12-file inventory;
5. per-file hashes and independently recomputed combined digest;
6. detailed source-review findings;
7. acceptance-criterion matrix;
8. field-evidence and canonical-ID findings;
9. recipe-reference findings;
10. semantic-plan and fail-closed findings;
11. dependency-fingerprint findings;
12. reverse-index findings;
13. flag-off compatibility proof;
14. authorization-separation proof;
15. relationship/graph and excluded-scope proof;
16. exact commands and test results;
17. pre-review versus post-review candidate identity;
18. risks and deferred items;
19. required remediation, if any;
20. completion-state attestation confirming no repository mutation.

End with exactly one verdict token:

* PHASE_2E_INDEPENDENT_REVIEW_PASS
* PHASE_2E_INDEPENDENT_REVIEW_FAIL
* PHASE_2E_INDEPENDENT_REVIEW_BLOCKED_CANDIDATE_DRIFT
* PHASE_2E_INDEPENDENT_REVIEW_BLOCKED_ENVIRONMENT

A PASS means only that the current uncommitted Phase 2E candidate passed independent technical review. It does not authorize commit, push, PR creation, runtime activation, merge, or Phase 2F.
