We are continuing the AskTD / KMAI project using the verified live repository
state.

DECISION:

Proceed with Option A — preserve PR #15 unchanged and create a stacked
Phase 2D development branch from the exact independently accepted PR #15 HEAD.

Do NOT create the optional tag at this time.

This operation may begin bounded Phase 2D development, but Phase 2D must remain
a stacked, non-mergeable candidate until PR #15 is merged and the candidate is
rebased and re-reviewed against the updated main.

==================================================
1. AUTHORITATIVE TARGET
==================================================

Repository:

TD-Enterprise/kmai-td-genie

Phase 2C.5 PR:

#15

Phase 2C.5 branch:

phase2/provider-abstraction-foundation

Expected last verified Phase 2C.5 HEAD:

d5472ae31081879329c224922244d87962737e8c

Do not trust the SHA from this prompt blindly.

First use read-only remote Git evidence to confirm the exact current remote HEAD
of:

origin/phase2/provider-abstraction-foundation

If the remote HEAD differs from the independently accepted SHA above, STOP and
report:

PHASE_2D_STACK_BASE_CHANGED

Do not create a branch or modify anything.

==================================================
2. PRESERVE PR #15
==================================================

Do NOT:

- modify phase2/provider-abstraction-foundation;
- commit to PR #15;
- force-push PR #15;
- rebase PR #15;
- squash PR #15;
- amend its accepted commit;
- change PR #15 title/body/base/draft state;
- merge PR #15;
- modify main;
- use the stale asktd_v2 checkout.

The independently reviewed Phase 2C.5 candidate must remain byte-for-byte
unchanged.

==================================================
3. READ THE EXISTING PHASE 2D DISCOVERY
==================================================

Read completely:

/tmp/ASKTD_PHASE_2D_DISCOVERY_2026-08-22.md

Treat it as the repository-backed implementation discovery for this bounded
pilot.

Do not repeat broad discovery unless current code contradicts that report.

Reconfirm only the essential facts:

- recommended pilot still exists:
  source_balance_mom_change;
- corresponding Q25/Q26 route still exists;
- query builder still exists;
- governed dataset reference still validates;
- Phase 2C.5 DataSourceAdapter seam is present;
- app/recipes does not already contain a Phase 2D implementation.

If any essential fact changed, STOP before coding and report the mismatch.

==================================================
4. CREATE A DEDICATED STACKED WORKTREE
==================================================

Create a new branch from the exact confirmed PR #15 HEAD:

phase2/approved-recipe-pilot

Create a separate worktree, preferably:

/tmp/asktd-phase2d-approved-recipe-pilot

Do not reuse:

- the primary asktd_v2 checkout;
- the Phase 2C.5 worktree;
- any dirty checkout.

Before implementation report:

- PR #15 base SHA used;
- new branch;
- worktree path;
- git status;
- merge-base;
- whether the branch is exactly zero commits ahead of PR #15 at creation.

==================================================
5. PHASE 2D SCOPE
==================================================

Implement only the bounded Approved Recipe Pilot identified by discovery.

Target pilot:

source_balance_mom_change

The pilot should cover the existing Q25/Q26-style source-balance
month-over-month route.

Conceptual flow:

User Question
    ->
existing entity authorization
    ->
existing deterministic recipe selection
    ->
ApprovedRecipe lookup
    ->
recipe lifecycle and parameter validation
    ->
dataset-scoped GovernedSemanticPlan
    ->
validation against current RegistrySnapshot
    ->
existing tested SQL builder
    ->
existing SQL safety and authorization
    ->
DataSourceAdapter
    ->
existing result handling

The LLM must not invent, name, alter, or approve a recipe.

==================================================
6. ADR FIRST
==================================================

Before production code, create the Phase 2D ADR using the repository's existing
ADR conventions.

Suggested file:

docs/adr/0004-phase2d-approved-recipe-pilot.md

The ADR must record:

- one-recipe pilot scope;
- source_balance_mom_change candidate;
- dataset-scoped governed plan;
- no field/relationship refs until governed snapshot supports them;
- recipes deliberately excluded from RegistrySnapshot identity for the pilot;
- recipe lifecycle independent from registry lifecycle;
- dependency-aware validation against the current snapshot;
- registry_version recorded for audit but not used as a blind exact-version
  validity lock;
- feature flag default OFF;
- strict metadata mode requirement when the pilot is ON;
- fail-closed behavior;
- rollback by disabling the feature flag;
- no Databricks, Genie, Unity Catalog, Collibra, Redis, Event Hubs, graph,
  reporting, or fine-grained authorization implementation.

Update the ADR index only as required by repository convention.

==================================================
7. MINIMAL APPROVED RECIPE CONTRACT
==================================================

Create the smallest repository-backed recipe package.

Expected shape from discovery:

app/recipes/__init__.py

app/recipes/approved_recipes.py

Revalidate paths against the actual repository layout.

The pilot contract should contain only fields with a current consumer.

Expected mandatory concepts include approximately:

- recipe_id;
- recipe_version;
- lifecycle_status;
- intent_id;
- governed_dataset_refs;
- parameters;
- builder_key;
- renderer or existing output-routing key.

Do not build a generic recipe DSL.

Do not add speculative fields for:

- Databricks;
- multi-provider SQL;
- cross-source joins;
- graph traversal;
- complete output-template definitions;
- future row/column security.

Use immutable/frozen typed records if consistent with repository conventions.

Reject unknown extra fields.

==================================================
8. RECIPE REGISTRY
==================================================

Add one deterministic registry entry only:

source_balance_mom_change

Add a deterministic lookup such as:

get_approved_recipe(recipe_id)

Unknown IDs must return no executable recipe and must fail closed.

Do not use:

- fuzzy matching;
- LLM selection;
- dynamic imports;
- a plugin framework;
- database-backed recipe storage;
- configuration-generated recipes.

Reuse the existing deterministic route selector to obtain the recipe ID.

==================================================
9. PARAMETERS
==================================================

Declare the existing governed parameter domain for the pilot.

At minimum preserve the current source-code/source-label behavior identified in
discovery.

Replace the current quote-escaping-only trust boundary with a declared
allow-list/domain check.

Validate:

- required parameter present;
- correct type;
- value is in allowed_values;
- no undeclared parameters;
- injection-like or out-of-domain values fail before SQL execution.

Do not change the existing SQL builder's intended output for valid values.

==================================================
10. GOVERNED PLAN AND SNAPSHOT COMPATIBILITY
==================================================

For an approved pilot recipe:

1. resolve the current live RegistrySnapshot through the existing
   MetadataRegistryService path;

2. stamp/capture the live registry_version for evidence;

3. build a dataset-scoped GovernedSemanticPlan using the recipe's governed
   dataset refs;

4. reuse:

   validate_governed_semantic_plan_for_service

   or the exact current service-level validator;

5. fail closed on:
   - unknown recipe;
   - recipe not approved/published;
   - unknown dataset;
   - invalid current registry version;
   - strict metadata mode unavailable;
   - missing/out-of-domain parameter.

Do not pin recipe compatibility to a historical exact registry_version.

The recipe declares its dependencies and is validated against the current
governed snapshot.

Do not add field_refs or relationship_refs when the current snapshot cannot
validate them.

==================================================
11. FEATURE FLAG AND STRICT MODE
==================================================

The pilot feature flag must default to OFF.

When OFF:

- existing runtime behavior must be byte-for-byte/trace-compatible where
  practical;
- existing recipes and answers must remain unchanged;
- no governed recipe lookup or validation may alter routing.

When ON:

- the Approved Recipe pilot path is active only for the one pilot recipe;
- strict metadata validation must be required or implied by the pilot;
- if strict metadata is unavailable, fail closed instead of silently falling
  back to an ungoverned execution for the pilot route.

Do not modify infrastructure or environment deployment configuration in this
operation.

Only add application-level configuration support required for testability and
safe default-OFF behavior.

==================================================
12. ORCHESTRATOR INSERTION
==================================================

Use the exact minimal insertion seams identified in the discovery report.

The report identified approximately:

orchestrator.py:2770-2775

and the structural twin around:

orchestrator.py:2907-2911

Reconfirm current line/symbol locations.

Insert a single bounded evaluation/gate before the existing execution call.

Do not broadly redesign Orchestrator.

Do not duplicate the entire route.

On pilot validation failure, use the existing safe no-data/search-elsewhere
response family identified by discovery.

Preserve the current audited authorization-denial response for unauthorized
tables/entities.

Do not replace an authorization failure with a generic recipe error.

==================================================
13. AUTHORIZATION
==================================================

Reuse existing:

EffectivePermissions

SqlPolicy

SqlAuthorizationGuard

DataSourceAdapter-bound auth context

Do not introduce a second authorization model.

Recipe selection is not authorization.

Authorization remains enforced at execution and must preserve the current
audited blocked response.

Do not add column- or row-level authorization in this pilot.

==================================================
14. EXECUTION
==================================================

The approved recipe should call the existing tested SQL builder through its
builder_key.

The builder may continue to return the current SQL Server/T-SQL string for the
pilot.

Then reuse:

DataSourceAdapter.execute_query(...)

and the existing:

- read-only check;
- table authorization;
- row/time limits;
- result handling;
- renderer/output path.

Do not introduce an intermediate execution specification.

Do not build a SQL compiler or dialect abstraction.

Do not change DataSourceAdapter.

==================================================
15. TESTS
==================================================

Add one new focused test file for the pilot and extend existing tests only where
the discovery report recommends.

At minimum cover:

A. Recipe contract
- immutable/frozen behavior;
- unknown extra fields rejected;
- known recipe lookup;
- unknown recipe fail closed;
- lifecycle approved/published requirement.

B. Parameter validation
- required parameter missing;
- wrong type;
- value outside allow-list;
- injection-like value rejected;
- valid declared values produce expected existing SQL.

C. Governed compatibility
- pilot governed dataset validates against current snapshot;
- unknown/ungoverned dataset fails;
- strict metadata mode unavailable fails closed;
- live registry_version is captured for evidence.

D. Routing
- Q25/Q26-style questions select the same recipe with different governed
  parameter values;
- unknown question does not enter the pilot recipe path.

E. Authorization
- deny_all blocks before data access;
- unauthorized table preserves existing audited blocked response;
- no SQL is executed on authorization or validation failure.

F. Execution boundary
- valid pilot goes through DataSourceAdapter;
- existing SQL policy/read-only controls still run.

G. Regression
- feature flag OFF preserves current golden behavior and traces;
- unrelated recipes remain unchanged.

Do not create a parallel fixture or golden-baseline framework.

==================================================
16. VALIDATION SEQUENCE
==================================================

Run focused tests first.

Then run:

1. Phase 2A/2B/2C focused regression;
2. Phase 2C.5 provider-abstraction tests;
3. MetadataRegistryService tests;
4. authorization tests;
5. SQL policy/store tests;
6. semantic-model and query-recipe tests;
7. golden baseline;
8. full backend regression with coverage gate;
9. git diff --check.

Do not regenerate baselines.

Do not install or upgrade dependencies.

Classify failures before broadening scope.

==================================================
17. SCOPE EXCLUSIONS
==================================================

Do NOT implement:

- any change to PR #15;
- Databricks SQL;
- Databricks authentication;
- Unity Catalog;
- Collibra;
- Genie;
- Redis;
- Event Hubs;
- cross-source joins;
- Graph or GraphRAG;
- Answer Intelligence/Reporting templates;
- KPI/glossary;
- fine-grained authorization;
- recipe-management UI;
- complete recipe lifecycle engine;
- automated stale-notification workflow;
- deployment/infrastructure changes;
- frontend changes;
- broad planner migration;
- migration of all historical recipes.

==================================================
18. GIT BEHAVIOR
==================================================

Do not commit, push, or create a PR automatically.

The implementation must first receive an independent read-only review.

Do not touch:

main

phase2/provider-abstraction-foundation

PR #15

Only modify the new Phase 2D worktree/branch.

==================================================
19. FINAL VERDICT
==================================================

Return exactly one:

PHASE_2D_STACKED_CANDIDATE_READY_FOR_INDEPENDENT_REVIEW

or

PHASE_2D_STACKED_CANDIDATE_HAS_BLOCKERS

or

PHASE_2D_STACKED_CANDIDATE_INSUFFICIENT_EVIDENCE

READY requires:

- branch created from exact accepted PR #15 HEAD;
- PR #15 remained unchanged;
- one bounded recipe pilot implemented;
- flag OFF behavior preserved;
- flag ON pilot works and fails closed;
- existing auth and SQL controls reused;
- tests/regressions/coverage/golden gates pass;
- no excluded feature entered the diff;
- no commit/push/PR created.

==================================================
20. REPORT
==================================================

Save outside the worktree:

/tmp/ASKTD_PHASE_2D_STACKED_IMPLEMENTATION_2026-08-22.md

Include:

1. PR #15 Base Evidence
2. New Worktree / Branch Evidence
3. ADR
4. ApprovedRecipe Contract
5. Recipe Registry
6. Parameter Validation
7. Governed Snapshot Compatibility
8. Feature Flag and Strict Mode
9. Orchestrator Insertion
10. Authorization Preservation
11. Execution Boundary
12. Tests
13. Regression / Coverage / Golden Results
14. Diff Inventory
15. Explicit Scope Exclusions
16. Stack Risk and Post-PR-15 Rebase Plan
17. Final Verdict
18. Recommended Next Action

At completion report:

- PR #15 changed: No
- main changed: No
- Phase 2D branch created: Yes/No
- commit created: No
- branch pushed: No
- Phase 2D PR created: No
- Phase 2D formally accepted: No

Then STOP.
