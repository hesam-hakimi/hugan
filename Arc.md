TASK: PHASE_2F1_RECIPE_LIFECYCLE_CLASSIFICATION_IMPLEMENTATION

Implement the separately authorized AskAlpha/KMAI Phase 2F.1 scope.

This task authorizes:

* creation of one dedicated Phase 2F.1 branch and permanent worktree;
* implementation of exactly the ten-file required plan;
* repeated safe test/fix cycles until all required gates pass;
* exactly one local implementation commit;
* exactly one implementation report outside the repository.

This task does not authorize push, PR creation, merge, deployment, runtime flag enablement, workflow execution, or any deferred Phase 2F work.

==================================================

1. AUTHORITATIVE DISCOVERY REPORT
    ==================================================

Before implementation, read this report completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_DISCOVERY_2026-08-26.md

It must:

* exist;
* end with PHASE_2F1_DISCOVERY_COMPLETE;
* recommend Option A;
* state NO_ADDITIONAL_PRODUCT_DECISION_REQUIRED;
* specify exactly 10 required files: 4 added and 6 modified.

Treat its Sections 7–16 as the authoritative implementation contract.

Also read completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_MERGE_2026-08-26.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_POSTMERGE_REVERIFICATION_2026-08-26.md

Do not modify any of these reports.

==================================================
2. PRE-MUTATION WORKSPACE AND LIVE-BASE GATE

Start from the permanent Phase 2E worktree:

Logical application root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The equivalent /app1 physical path is acceptable only when realpath proves identity.

Before any mutation, verify:

* pwd;
* pwd -P;
* logical-root realpath;
* Git top-level;
* Git common directory;
* origin identity;
* current branch;
* local HEAD;
* local tree;
* complete porcelain status, including untracked files;
* existing worktree inventory;
* absence of target branch/path collisions.

Required source identity:

* Repository: TD-Enterprise/kmai-td-genie
* Phase 2E branch: phase2/governed-field-records
* accepted Phase 2E head:
    0430613e6a9f1680338d8fc099e7960e5d46cac2
* accepted tree:
    6448dac5be9dee275598e054f505517a215b484b
* current accepted main:
    f283f01b6d615f9fa00debcef959d9c5c86a3224
* first merge parent:
    409fed3fb98fc87547a7d05a68292fc28c3c1e7c
* second merge parent:
    0430613e6a9f1680338d8fc099e7960e5d46cac2
* Phase 2E workflow run:
    32974122120
* workflow conclusion: success

The source Phase 2E worktree must be completely clean.

Independently reverify through authenticated read-only GitHub requests:

* current main SHA;
* PR #17 remains closed and merged;
* accepted head and merge commit;
* two-parent merge identity;
* successful workflow conclusion;
* merge tree remains identical to the accepted Phase 2E tree.

If live main differs from the required SHA, do not rebase or reinterpret the scope. Stop before mutation.

If authenticated GitHub access is unavailable, stop before mutation.

Do not inspect or use:

* stale primary checkout;
* asktd_v2;
* sibling repositories;
* ETL/UCA workspaces;
* Windows/ETL Coding Agent sessions;
* temporary or unrelated worktrees.

==================================================
3. CREATE THE AUTHORIZED WORKTREE

Create exactly one dedicated permanent worktree and branch from the accepted main merge commit—not from an unmerged feature head.

Branch:

phase2/recipe-lifecycle-classification

Worktree Git root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Application root inside that worktree:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

Base commit:

f283f01b6d615f9fa00debcef959d9c5c86a3224

If the base object is unavailable locally, one bounded non-destructive fetch of origin/main is authorized only after the live-base gate proves that main still equals the required SHA.

After worktree creation, verify:

* exact target branch;
* HEAD equals the accepted main SHA;
* HEAD tree equals the accepted Phase 2E tree;
* correct origin;
* correct Git common directory;
* clean index/worktree with zero untracked files.

If the target path or branch already exists, do not delete, reset, rename, overwrite, or silently reuse it. Inspect read-only and stop with the target-collision result.

Do not modify the Phase 2E worktree.

==================================================
4. FIXED PHASE 2F.1 ARCHITECTURE

Implement only Option A:

Pure lifecycle evaluator

* ApprovalEvidenceProvider Protocol port
* current ApprovedRecipe-metadata adapter
* orchestration-side evidence resolution.

The evaluator must be:

* pure;
* deterministic;
* immutable-input/immutable-output;
* provider-neutral;
* side-effect-free;
* independent of environment variables;
* independent of current time, timestamps, random values, global mutation and I/O;
* total over malformed resolution values;
* bounded by recipe dependency metadata, not business-data volume.

The evaluator must never call or import:

* an approval provider;
* MetadataRegistryService;
* DataSourceAdapter;
* SQL or database tools;
* Synapse;
* Databricks;
* Data Lake clients;
* network/HTTP/socket libraries;
* provider SDKs;
* cache, queue or persistence APIs;
* logger or tracer.

The orchestration helper must resolve immutable evidence before calling the evaluator.

==================================================
5. EXACT TEN-FILE PLAN

Add exactly these four files:

1. src/backend/app/recipes/lifecycle.py
2. src/backend/app/recipes/approval_evidence.py
3. test/test_recipe_lifecycle.py
4. docs/adr/0006-phase2f1-recipe-lifecycle-classification.md

Modify exactly these six files:

5. src/backend/app/recipes/approved_recipes.py
6. src/backend/app/orchestrator.py
7. test/test_approved_recipe_pilot.py
8. test/test_authz_no_access_guard.py
9. test/test_provider_abstraction_contracts.py
10. docs/adr/README.md

No eleventh repository file is permitted.

Specifically:

* do not modify app/recipes/__init__.py;
* do not change any existing ApprovedRecipe field;
* do not modify configuration or dependency files;
* do not create API, database, cache, queue, UI or seed schemas;
* do not modify unrelated tests, documentation or product areas.

If implementation genuinely requires an eleventh file, stop for owner review instead of expanding scope.

==================================================
6. REQUIRED CONTRACTS

Implement the repository-native contracts and signatures from the discovery report, including:

* LifecycleState(StrEnum)
* LifecycleReasonCode(StrEnum)
* frozen ApprovalEvidence
* frozen ApprovalEvidenceResolution
* frozen DependencyEvidenceResolution
* frozen LifecycleEvaluationResult
* ApprovalEvidenceProvider as @runtime_checkable Protocol
* ApprovedRecipeApprovalEvidenceProvider
* pure evaluate_recipe_lifecycle(...)
* RECIPE_LIFECYCLE_CLASSIFICATION_FLAG
* recipe_lifecycle_classification_enabled()
* evaluate_recipe_lifecycle_gate(...)

The lifecycle states and precedence are fixed:

1. BROKEN
2. NOT_APPROVED
3. REVIEW_REQUIRED
4. VALID

Return all applicable reasons even when a higher-precedence final state is selected.

Use exactly the reason codes defined in the discovery report:

* APPROVAL_EVIDENCE_MISSING
* APPROVAL_EVIDENCE_AMBIGUOUS
* APPROVAL_EVIDENCE_CONFLICTING
* APPROVAL_EVIDENCE_INVALID
* RECIPE_NOT_APPROVED
* DEPENDENCY_REFERENCE_MISSING
* DEPENDENCY_EVIDENCE_CONFLICTING
* DEPENDENCY_EVIDENCE_INVALID
* DEPENDENCY_NOT_IN_APPROVAL
* APPROVED_DEPENDENCY_NOT_DECLARED
* DEPENDENCY_FINGERPRINT_CHANGED
* APPROVAL_AND_DEPENDENCIES_VALID

Stable normalization rules:

* dependency refs use exact case-sensitive strings;
* sort with normal Python lexicographic ordering;
* normalize ref collections using tuple(sorted(set(refs)));
* sort fingerprint pairs by dependency ref;
* collapse only identical (ref, fingerprint) pairs;
* the same ref with different fingerprints is conflicting;
* never silently deduplicate multiple approval records;
* multiple identical approval records are ambiguous and BROKEN;
* differing approval records are ambiguous plus conflicting and BROKEN;
* deduplicate and sort reason codes by reason.value.

to_trace_payload() must serialize only:

* recipe ID;
* uppercase lifecycle-state string;
* ordered uppercase reason-code strings;
* ordered affected governed dependency refs.

It must not expose fingerprints, SQL, raw evidence, exception text, timestamps, paths, provider names or internal objects.

==================================================
7. ACCEPTED APPROVAL BASELINE

The current code lacks historical approved per-entity fingerprints. Phase 2F.1 must add a private immutable baseline for exactly the five dependencies of the current pilot recipe:

* one governed dataset;
* four governed fields.

Mechanically derive their exact ef-... values from the accepted Phase 2E tree:

6448dac5be9dee275598e054f505517a215b484b

Requirements:

* derive the exact refs from the existing pilot ApprovedRecipe;
* use the existing accepted RegistrySnapshot and entity_fingerprint() behavior;
* do not guess or manually invent a fingerprint;
* do not use an aggregate df-... value as the per-reference baseline;
* record the five accepted values as immutable static adapter metadata;
* never recompute the approved baseline at runtime;
* add a test proving every static value matches the accepted Phase 2E snapshot;
* malformed or incomplete static baseline must produce invalid evidence and fail closed;
* current fingerprints must be resolved independently from the current bounded snapshot.

If the exact accepted five-value baseline cannot be mechanically generated and independently verified, stop without committing.

Do not implement approval expiry. Missing expiry metadata must never mean expired.

==================================================
8. FEATURE FLAG AND ORCHESTRATION

Feature flag:

RECIPE_LIFECYCLE_CLASSIFICATION_ENABLED

Parse it with the repository’s existing strict boolean helper and default it to False.

When the flag is absent or false:

* return None before recipe lookup;
* do not construct or call the approval provider;
* do not construct or call the registry service;
* do not evaluate lifecycle;
* emit no lifecycle trace;
* preserve exact Phase 2E response, trace, SQL and routing behavior.

Preserve the current invalid-token RuntimeError behavior of the strict parser.

Required execution ordering:

1. greeting handling;
2. deny_all authorization short-circuit;
3. deterministic source-plan/query-kind selection;
4. recipe-parameter construction;
5. new lifecycle classification helper;
6. optional recipe_lifecycle trace;
7. existing Approved Recipe execution gate;
8. existing data-source/SQL path.

The lifecycle call must occur immediately before the current Approved Recipe gate.

The resulting state must be ignored for runtime control flow.

BROKEN, NOT_APPROVED, and REVIEW_REQUIRED must not:

* warn or deny;
* stop execution;
* alter SQL;
* alter status or response selection;
* replace current authorization;
* change the existing Approved Recipe gate.

Observability is limited to the existing best-effort in-memory trace mechanism.

==================================================
9. NO-SCAN AND SCALE BOUNDARY

Phase 2F.1 must inspect exactly zero business-data rows and issue exactly zero SQL statements.

The anticipated scale context is:

* 5 TB or more;
* Synapse data in Dedicated SQL Pools;
* Databricks data in the Data Lake.

This phase operates only on bounded repository metadata, the already materialized RegistrySnapshot and recipe dependency refs.

Add structural and spy tests proving:

* no forbidden provider/data-access imports in either new module;
* no data-source factory or adapter call for lifecycle classification;
* provider call count is exactly one only when the flag is enabled and the route is in scope;
* fingerprint work is bounded by unique dependency count;
* input permutations and duplicates do not increase unique resolution work;
* no evaluator input accepts table rows, SQL, query callables or a data-source adapter.

Provider query pushdown remains Phase 3. Performance benchmarks, concurrency, scan-cost controls and SLOs remain Phase 6.

==================================================
10. REQUIRED TEST MATRIX

Implement every test required in Discovery Section 14, including:

* every lifecycle state;
* all reason mappings;
* every precedence pair and a combined multi-state case;
* preservation of all reasons;
* stable ordering across all relevant permutations;
* duplicate normalization;
* conflicting duplicate fingerprints;
* missing approval evidence;
* missing approved per-ref baseline;
* missing current dependency;
* identical and differing multiple approval records;
* invalid recipe ID/version/status/fingerprint shape;
* exact trace serialization;
* purity and repeated-input equality;
* provider exception normalization;
* adapter Protocol conformance;
* exact static baseline pin;
* default-OFF and explicit-false compatibility;
* no provider/registry call when disabled;
* deny_all ordering;
* SQL-authorization behavior;
* trace position;
* all four injected lifecycle states remaining trace-only;
* governance-flag interaction;
* provider-neutrality AST scan;
* dependency-count/no-I/O proof.

Preserve the existing
test_flag_off_leaves_the_deterministic_lane_untouched()
test unchanged.

For flag-OFF compatibility, compare canonical response bytes between:

* new flag absent;
* new flag explicitly false.

Also prove equality of:

* trace names and order;
* SQL strings;
* response status;
* answer;
* followups;
* citations;
* result;
* chart;
* report fields;
* cards.

==================================================
11. TEST AND QUALITY GATES

Use the existing project environment. Use python3, not python.

Do not install or upgrade packages.

First run the focused suite:

python3 -m pytest --no-cov -q \
  test/test_recipe_lifecycle.py \
  test/test_approved_recipe_pilot.py \
  test/test_authz_no_access_guard.py \
  test/test_provider_abstraction_contracts.py \
  test/test_recipe_dependency_fingerprint.py \
  test/test_governed_field_records.py \
  test/test_semantic_plan_contract.py

Then run the golden suite:

python3 -m pytest --no-cov -q test/test_golden_baseline.py

Then run the complete configured backend suite with coverage:

python3 -m pytest

Coverage must remain at or above 75%.

Run:

git diff --check

Do not invent lint, formatting or type-check gates. The repository currently has no authoritative configured command for them.

Safe test/fix/rerun cycles are authorized until all required gates pass. Do not weaken, delete or skip tests to obtain a pass.

If the existing environment cannot resolve required dependencies, stop without installing packages.

==================================================
12. ACCEPTANCE GATES

Implementation is acceptable only if:

* exactly the authorized ten files changed;
* new flag absent/false reproduces canonical Phase 2E behavior;
* ApprovedRecipe.model_fields is unchanged;
* current Approved Recipe execution gate remains authoritative and unchanged in business behavior;
* lifecycle result never controls execution;
* deny_all precedes classification;
* SQL authorization remains independently authoritative;
* provider-abstraction tests pass;
* all focused, golden and full tests pass;
* coverage is at least 75%;
* no provider/network/database/data-source import enters the evaluator or adapter;
* no persistence, API, UI, queue, cache or new backend is introduced;
* no business-data scan is possible through these contracts;
* git diff --check passes;
* no optional cleanup or deferred work is included.

Do not implement:

* warning or runtime blocking;
* approval persistence;
* expiry or reapproval;
* owner/approver/override policy;
* additional recipe migration;
* provider integrations;
* Synapse or Databricks access;
* UI/admin workflows;
* benchmarks or SLO work;
* Phase 2F.2 policy.

==================================================
13. LOCAL COMMIT

After every gate passes:

1. verify the changed-file list is exactly the authorized ten files;
2. inspect the complete diff;
3. verify no secret, credential, generated artifact or unrelated change exists;
4. stage only the exact ten files;
5. verify the staged file list again;
6. create exactly one local commit with message:

feat(recipes): add phase 2f.1 lifecycle classification

7. verify the target worktree is completely clean after the commit;
8. record the commit SHA and tree SHA.

Do not amend, squash, push, open a PR or trigger a workflow.

If any required gate fails, do not commit.

==================================================
14. IMPLEMENTATION REPORT

Write exactly one report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_2026-08-27.md

Include:

1. final verdict;
2. source workspace and live-base evidence;
3. target branch/worktree identity;
4. accepted main/head/tree identity;
5. exact ten-file changed inventory;
6. exact five accepted dependency refs and their pinned ef-... values;
7. contracts and public symbols implemented;
8. lifecycle and reason mapping implemented;
9. feature-flag and orchestration behavior;
10. proof that flag-OFF matches Phase 2E;
11. proof that classification never affects control flow;
12. no-scan and bounded-metadata evidence;
13. focused-test command and exact result;
14. golden-test command and exact result;
15. full-suite result and coverage percentage;
16. git diff --check result;
17. compatibility/regression gate results;
18. risks encountered and resolutions;
19. commit SHA and tree SHA;
20. final clean-status evidence;
21. no push/PR/merge/deployment/workflow/flag-enablement attestation;
22. exact next permitted action.

The exact next permitted action must be an independent read-only review of the local Phase 2F.1 implementation and commit.

End the report with exactly one token:

PHASE_2F1_IMPLEMENTATION_COMPLETE

or one applicable blocker:

* PHASE_2F1_IMPLEMENTATION_BLOCKED_WORKSPACE
* PHASE_2F1_IMPLEMENTATION_BLOCKED_BASE_DRIFT
* PHASE_2F1_IMPLEMENTATION_BLOCKED_GITHUB_ACCESS
* PHASE_2F1_IMPLEMENTATION_BLOCKED_TARGET_COLLISION
* PHASE_2F1_IMPLEMENTATION_BLOCKED_BASELINE
* PHASE_2F1_IMPLEMENTATION_BLOCKED_ENVIRONMENT
* PHASE_2F1_IMPLEMENTATION_BLOCKED_SCOPE
* PHASE_2F1_IMPLEMENTATION_BLOCKED_TESTS

At task completion, output:

* final token;
* branch;
* commit SHA if created;
* changed-file count;
* focused/golden/full test summaries;
* coverage percentage;
* report path;
* confirmation that nothing was pushed and no PR was created.
