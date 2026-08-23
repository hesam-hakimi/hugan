We are implementing the next bounded AskTD / KMAI architecture slice:

PHASE 2E — GOVERNED FIELD RECORDS AND DEPENDENCY-AWARE RECIPE REFERENCES

This is a CONTINUATION of the accepted Phase 2D work.

This is NOT a redesign.
This is NOT Phase 2F.
This is NOT a Databricks, Genie, Redis, reporting, graph-database, or infrastructure task.

The implementation must remain narrow, reversible, feature-flagged, provider-neutral, and independently reviewable.

==================================================
1. AUTHORITATIVE DISCOVERY INPUT
==================================================

Before changing code, read this discovery document COMPLETELY:

/home/tag5916/projects/kmai-td-genie/kmai-td-genie/docs/plans/ASKTD_PHASE_2E_DISCOVERY_AND_ROADMAP_2026-08-23.md

The document may be untracked in the primary checkout. That is acceptable.

Treat it as the approved scope and planning input, but do NOT stage, move, edit, or commit it during this operation.

The selected option is:

OPTION A — Governed Field Records and Dependency-Aware Recipe References

Its objective is:

Emit strictly evidenced FieldRecord objects into the governed snapshot for datasets that already exist in the governed registry; let the Phase 2D pilot ApprovedRecipe declare the governed fields it actually depends on; and compute a per-recipe, entity-scoped dependency fingerprint.

Do not implement Option B or Option C.

==================================================
2. CURRENT EXPECTED REPOSITORY STATE
==================================================

Repository:

TD-Enterprise/kmai-td-genie

Expected stack:

main
  -> PR #15: phase2/provider-abstraction-foundation
      -> PR #16: phase2/approved-recipe-pilot
          -> proposed Phase 2E: phase2/governed-field-records

Phase 2C.5 branch:

phase2/provider-abstraction-foundation

Phase 2D branch:

phase2/approved-recipe-pilot

Phase 2D PR:

#16

Phase 2D has already passed independent review and must be treated as frozen.

The exact Phase 2D remote HEAD recorded in the discovery report is authoritative.

Before creating Phase 2E, independently verify:

- origin/main HEAD
- origin/phase2/provider-abstraction-foundation HEAD
- origin/phase2/approved-recipe-pilot HEAD
- PR #15 state, base, head, SHA, and changed files
- PR #16 state, base, head, SHA, and changed files
- linear ancestry:
  main -> Phase 2C.5 -> Phase 2D
- no unexpected changes since the discovery report

If PR #16 or its remote branch has changed from the exact SHA recorded in the discovery report:

STOP.

Return:

PHASE_2E_IMPLEMENTATION_BLOCKED_BASE_DRIFT

Do not create the Phase 2E branch.
Do not rebase or repair PR #16.
Do not infer that the changed base is acceptable.

==================================================
3. PERMANENT WORKTREE — DO NOT USE /tmp
==================================================

Do not implement inside the stale `asktd_v2` checkout.

Do not modify, stash, discard, stage, or commit the two pre-existing dirty files in the primary checkout.

Do not create a worktree under `/tmp`.

Use this permanent project-area worktree:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records

Use this branch:

phase2/governed-field-records

Use this exact base:

origin/phase2/approved-recipe-pilot

First verify whether the branch or worktree already exists.

If neither exists, create them safely using the equivalent of:

git fetch origin
git worktree add \
  -b phase2/governed-field-records \
  /home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records \
  origin/phase2/approved-recipe-pilot

If the branch or worktree already exists:

- inspect it;
- verify its base and contents;
- reuse it only if it is clean and exactly at the expected Phase 2D HEAD;
- otherwise STOP without deleting, resetting, rebasing, or overwriting it.

Return:

PHASE_2E_IMPLEMENTATION_BLOCKED_EXISTING_WORKTREE_STATE

if the existing state is not safely reusable.

After creating the permanent worktree, perform all implementation work only inside:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records

If the current Copilot session cannot access that permanent path, STOP and report the exact path that must be opened in VS Code.

Do not fall back to `/tmp`.

==================================================
4. MODE AND MUTATION BOUNDARIES
==================================================

This operation MAY:

- create the Phase 2E branch and permanent worktree;
- create ADR 0005;
- implement the bounded Phase 2E source changes;
- add and update the bounded tests;
- run local validation;
- create one implementation report outside the Git worktree.

This operation MUST NOT:

- commit;
- push;
- create or update a PR;
- modify PR #15;
- modify PR #16;
- modify main;
- rebase;
- merge;
- force-push;
- stage files;
- modify the primary stale checkout;
- begin Phase 2F;
- modify deployment or infrastructure;
- enable strict mode in an environment.

Stop after the implementation is ready for independent review.

==================================================
5. ADR FIRST
==================================================

Before modifying production source code, create:

kmai-td-genie/docs/adr/0005-phase2e-governed-field-records.md

Also add the corresponding row to:

kmai-td-genie/docs/adr/README.md

ADR 0005 must define at minimum:

1. Phase 2E scope.
2. Why the existing validator is sufficient but governed FieldRecord data is currently absent.
3. Why fields are emitted only from existing evidence.
4. Why evidence must never invent a DatasetRecord, SchemaRecord, relationship, or business name.
5. Why only already-governed datasets may receive emitted fields.
6. Explicit field-ID normalization rules.
7. Fail-closed handling for inconsistent evidence.
8. Separation of descriptive classification metadata from authorization.
9. The entity-scoped dependency-set model.
10. The pure per-entity and per-recipe dependency-fingerprint model.
11. Why recipes are not pinned to the whole `registry_version`.
12. Why unrelated snapshot changes must not invalidate a recipe.
13. Why referenced-entity semantic changes must alter the dependency fingerprint.
14. Feature-flag and rollback behavior.
15. Explicit deferral of the complete stale-state lifecycle:
    - VALID
    - REVIEW_REQUIRED
    - BROKEN
    - NOT_APPROVED
16. Explicit deferral of relationship emission and the metadata relationship graph.
17. Explicit exclusion of Redis, Databricks, Genie, Unity Catalog, Collibra, infrastructure, authorization changes, and report templates.
18. Test and acceptance criteria.

Do not write code before the ADR establishes these boundaries.

==================================================
6. BOUNDED SOURCE CHANGE SURFACE
==================================================

The expected source surface is approximately:

MODIFY:

1. kmai-td-genie/src/backend/app/available_data/registry_contract.py
2. kmai-td-genie/src/backend/app/recipes/approved_recipes.py

CREATE:

3. kmai-td-genie/src/backend/app/available_data/field_evidence.py
4. kmai-td-genie/src/backend/app/recipes/dependency_fingerprint.py

The second new source module may be omitted only if the pure fingerprint and reverse-index functions fit cleanly into an existing Phase 2E-owned module without coupling them to orchestration.

Do not create broad new packages.

Do not modify `orchestrator.py`.

If the implementation appears to require `orchestrator.py`, API DTOs, authorization, SQL policy, or execution-layer changes, STOP and report why the discovery scope is insufficient.

Do not silently widen the implementation.

==================================================
7. FIELD EVIDENCE SOURCE
==================================================

The repository already contains field evidence under the existing metadata JSON area, including:

data/metadata/json/field.json

The discovery report also identified:

data/metadata/json/table.json
data/metadata/json/relationship.json

For Phase 2E:

- `field.json` is field evidence.
- `table.json` and `relationship.json` may be read only to detect contradictions.
- Do NOT emit RelationshipRecord objects.
- Do NOT treat relationship evidence as governed truth yet.
- Do NOT create missing governed datasets.
- Do NOT create a real ProductGroup or Schema taxonomy.
- Keep the existing unassigned hierarchy behavior unchanged.

Inspect the actual files and confirm the live schema before coding.

Do not assume screenshot text is sufficient.

==================================================
8. FIELD EVIDENCE LOADER REQUIREMENTS
==================================================

Implement a narrow, deterministic field-evidence loader.

It must:

1. Read the existing field evidence through repository-safe path resolution.
2. Produce deterministic output independent of source-row ordering.
3. Map evidence only to datasets already present in the canonical RegistrySnapshot.
4. Never invent a DatasetRecord.
5. Never infer a dataset from display-name similarity.
6. Never infer schema or product group from a field name.
7. Never silently coerce conflicting evidence.
8. Preserve existing canonical IDs and logical dataset IDs.
9. Emit only structural FieldRecord information supported by the existing canonical model.
10. Keep PII, PCI, security classification, business-name, and descriptive classification evidence separate from authorization.
11. Reuse existing exception and validation patterns where possible.
12. Fail closed with deterministic, safe errors for evidence inconsistencies that affect an already-governed dataset.
13. Ignore unrelated field-evidence rows for datasets that are not governed; do not add those datasets to the snapshot.
14. Reject duplicate/conflicting canonical field IDs for the same governed snapshot.
15. Avoid timestamps, process IDs, filesystem ordering, or environment-specific values in semantic identity.

The current evidence contains known inconsistencies across files and datasets.

Do not introduce a global “best effort” normalizer that hides them.

The pilot dataset evidence is reported as internally consistent, but verify that directly.

==================================================
9. FIELD ID NORMALIZATION
==================================================

Inspect the existing canonical ID conventions in:

- DatasetRecord
- FieldRecord
- RegistrySnapshot
- existing seed adapters
- existing tests

Use an existing stable convention if one already exists.

If no complete field-ID convention exists, ADR 0005 must define a minimal explicit rule with these properties:

- deterministic;
- collision-resistant within the governed snapshot;
- derived from stable logical dataset identity plus evidenced field identity;
- independent of collection order;
- independent of physical row position;
- independent of display-only labels;
- not silently case-insensitive unless the rule explicitly documents that behavior.

Do not normalize business meaning.

Do not silently transform one real field name into a different business field name.

The normalization rule must have positive, negative, casing, duplicate, and collision tests.

==================================================
10. SNAPSHOT FIELD EMISSION
==================================================

Modify the existing registry snapshot construction boundary rather than creating a second registry.

The expected integration point is the existing:

build_registry_snapshot_from_seeds(...)

or its actual live equivalent.

The existing legacy-seed adapter must remain the sole legacy-to-canonical boundary.

When the Phase 2E field-emission flag is OFF:

- snapshot behavior must remain byte-equivalent/semantically equivalent to the Phase 2D baseline;
- `fields` must remain as before;
- the previous `registry_version` must be reproduced exactly;
- no field-evidence file is allowed to alter runtime behavior.

When the flag is ON:

- emit FieldRecord objects only for governed datasets with valid evidence;
- preserve strict canonical validation;
- include the field collection in the existing canonical `registry_version` calculation;
- produce stable output and stable registry identity for equivalent content;
- allow the current semantic-plan validator to validate real `field_refs`;
- do not emit relationships.

Use a default-off flag following the repository’s existing feature-flag/configuration style.

Expected semantic name:

GOVERNED_FIELD_RECORDS_ENABLED

Do not add Terraform, deployment YAML, environment promotion, or infrastructure changes.

Do not claim the flag is enabled in any deployed environment.

==================================================
11. PILOT RECIPE FIELD REFERENCES
==================================================

Extend the existing frozen ApprovedRecipe contract only as necessary to add:

governed_field_refs

Use canonical governed field IDs, not raw physical table references.

Do not pin the recipe to the whole registry version.

Do not add a second recipe.

Do not migrate the existing 25 legacy recipe plans.

Do not modify query builder SQL.

Do not modify `query_recipes.py`.

Do not modify `semantic_models.py`.

Do not modify `orchestrator.py`.

The single Phase 2D pilot recipe is expected to depend on the governed dataset logically associated with:

v_dlv_dep_agmt_clr

The discovery report identified the likely required evidenced fields:

- CUR_BAL_AMT
- RRDW_SRC_CD
- RRDW_AS_OF_DT
- AGMT_CD

Verify each field against the live evidence and the actual SQL builder before declaring it.

Do not copy this list blindly.

The recipe must declare exactly the governed fields its authoritative builder actually needs for the governed contract being tested.

Do not include unrelated output, formatting, trace-only, or cosmetic fields merely to increase coverage.

==================================================
12. GOVERNED SEMANTIC PLAN INTEGRATION
==================================================

When the Phase 2D Approved Recipe pilot flag is ON and Phase 2E field records are enabled:

- construct the existing GovernedSemanticPlan using the recipe’s:
  - governed dataset refs;
  - governed field refs;
- stamp the live registry version using the existing service-level path;
- use the existing semantic-plan validator;
- do not create a second validator;
- do not create a second registry;
- do not create a second planner;
- do not create a second authorization check.

An unknown field reference must continue to fail with the existing deterministic field error.

A removed or renamed referenced field must fail closed before:

- data-source factory access;
- adapter access;
- schema probing;
- builder resolution;
- builder invocation;
- SQL construction;
- SQL execution.

Reuse the Phase 2D dependency-injection/call-count test pattern to prove zero side effects.

==================================================
13. DEPENDENCY FINGERPRINT
==================================================

Implement a pure dependency-fingerprint function.

It must operate on:

- the canonical governed records referenced by a recipe;
- a deterministic set of entity references;
- the semantic content of those referenced entities.

It must NOT operate on:

- the whole snapshot hash as the recipe identity;
- collection positions;
- runtime timestamps;
- process IDs;
- cache state;
- filesystem paths;
- unrelated records.

Recommended conceptual layers:

A. Per-entity fingerprint:

entity_fingerprint(record) -> stable string

B. Per-recipe dependency fingerprint:

dependency_fingerprint(
    referenced canonical records
) -> stable string

The exact semantic attribute set must be documented in ADR 0005 and must reuse the canonical record model.

Exclude only explicitly documented non-semantic/runtime provenance values.

Required properties:

1. Same referenced semantic content in different collection order -> same fingerprint.
2. Unrelated dataset or field changes -> same recipe dependency fingerprint.
3. Referenced field removal -> resolution failure / fail closed.
4. Referenced field rename -> fail closed or changed identity, according to the canonical ID rule.
5. Referenced field datatype/semantic-record change -> different fingerprint.
6. Equivalent serialization across processes -> same fingerprint.
7. Duplicate reference inputs -> canonicalized, deterministic result.
8. Unknown reference -> deterministic failure, not silent omission.

Do not add the complete stale-state classification engine in Phase 2E.

Do not add a human approval workflow.

Do not automatically mutate recipe lifecycle state.

==================================================
14. DEPENDENCY REVERSE INDEX
==================================================

Implement a small pure in-memory reverse-index helper only within the Phase 2E dependency module:

entity_ref -> approved recipe IDs that depend on it

This is the first recipe-impact index.

It must:

- be computed from immutable recipe records;
- be deterministic;
- not be persisted;
- not require a database;
- not require a graph database;
- not introduce an API endpoint;
- not introduce Redis;
- not become a second metadata store.

It may remain test-only or internal if there is no existing safe runtime consumer.

Do not widen the API surface merely to expose it.

==================================================
15. TRACE / DECISION EVIDENCE
==================================================

Where the existing Approved Recipe evaluation result or trace structure already supports adding safe metadata, record:

- governed field refs used;
- the computed dependency fingerprint.

Do this entirely within the existing Approved Recipe module and existing trace/decision structures.

Do not modify `orchestrator.py`, API DTOs, frontend DTOs, or response schemas merely to expose the fingerprint.

If no safe existing trace slot exists without widening scope:

- keep the fingerprint available in the internal evaluation result;
- document the limitation;
- do not expand the source surface.

==================================================
16. AUTHORIZATION AND CLASSIFICATION SEPARATION
==================================================

Do not change authorization.

Do not add authorization fields to:

- ProductGroupRecord
- SchemaRecord
- DatasetRecord
- FieldRecord
- RelationshipRecord
- GovernedSemanticPlan
- ApprovedRecipe

Do not interpret PII, PCI, key indicators, business classifications, or security classifications as grants.

Metadata describes governed content.

Authorization continues to decide access through the existing EffectivePermissions and SQL authorization path.

All Phase 2C and Phase 2D tests proving this separation must remain green.

==================================================
17. RELATIONSHIP AND GRAPH BOUNDARY
==================================================

Do NOT emit RelationshipRecord objects in Phase 2E.

The discovery report proved that the current relationship evidence cannot yet pass strict canonical validation because:

- several relationship endpoint datasets are not yet governed;
- at least one bridge dataset lacks field evidence;
- naming inconsistencies remain;
- relationship key fields cannot yet be validated completely.

Do not “repair” those metadata gaps in code.

Do not hard-code relationship records.

Do not add a graph database.

Do not add a persisted graph.

The only graph-like structure allowed in Phase 2E is the pure recipe dependency reverse index.

==================================================
18. STRICT MODE BOUNDARY
==================================================

`METADATA_REGISTRY_STRICT_ENABLED` currently defaults to false and is not enabled in the deployed development configuration.

Do not change that configuration here.

Do not modify infrastructure.

Do not claim deployed runtime value.

Phase 2E code must be locally testable with strict mode enabled through test-controlled configuration.

Record this as an integration/runtime activation dependency, not a Core implementation blocker.

==================================================
19. REQUIRED TEST FILES
==================================================

Expected new tests:

1. kmai-td-genie/test/test_governed_field_records.py
2. kmai-td-genie/test/test_recipe_dependency_fingerprint.py

Expected existing tests to extend as needed:

- test/test_semantic_plan_contract.py
- test/test_approved_recipe_pilot.py
- test/test_registry_contract.py
- test/test_registry_hierarchy_contract.py
- test/test_provider_abstraction_contracts.py

Use the actual repository structure as authoritative.

Do not create duplicate fixture frameworks.

Reuse existing strict-snapshot, semantic-plan, authorization, dependency-injection, and golden-baseline helpers.

==================================================
20. REQUIRED TEST MATRIX
==================================================

At minimum, independently prove all of the following:

1. Field emission is deterministic and independent of source-row ordering.
2. Equivalent field evidence produces the same registry version across processes.
3. Field-ID normalization is explicit, deterministic, total, and tested.
4. Duplicate/colliding field IDs fail closed.
5. A non-governed evidence dataset is not invented in RegistrySnapshot.
6. Extra evidence for non-governed datasets does not silently create governed content.
7. Inconsistent evidence for an already-governed dataset fails closed.
8. With the Phase 2E flag ON, the snapshot passes `validate_registry_snapshot` with zero errors.
9. With the Phase 2E flag OFF, the Phase 2D snapshot and registry version are reproduced.
10. A real field-scoped GovernedSemanticPlan for the pilot validates cleanly.
11. An unknown field ref still returns the existing deterministic unknown-field error.
12. The Phase 2D pilot recipe declares only live, evidenced governed field refs.
13. The pilot recipe validates and executes successfully with the valid Phase 2D parameter pairs.
14. Removing a referenced field fails closed.
15. Renaming a referenced field fails closed according to the canonical ID rule.
16. Missing referenced fields cause zero:
    - data-source factory calls;
    - adapter calls;
    - schema-probe calls;
    - authoritative-builder calls;
    - legacy-builder calls;
    - SQL execution calls.
17. Unrelated snapshot edits may change registry_version but do not change the recipe dependency fingerprint.
18. A referenced field semantic-attribute edit changes the dependency fingerprint.
19. Dependency fingerprint is stable under reference ordering and duplicate input.
20. Dependency reverse index returns the correct recipe IDs and is ordering-independent.
21. Phase 2C hierarchy and semantic-plan regression suites remain green.
22. Phase 2D Approved Recipe and authorization negative suites remain green.
23. Provider-abstraction import guards include all new Phase 2E modules.
24. No future-provider SDK/model imports are introduced.
25. Golden baseline behavior remains unchanged with flags OFF.
26. Full backend suite passes.
27. Coverage gate passes.
28. `git diff --check` passes.

==================================================
21. VALIDATION ORDER
==================================================

Run tests incrementally:

A. New field-evidence tests.
B. New fingerprint/index tests.
C. Registry hierarchy and registry-version tests.
D. Semantic-plan tests.
E. Approved Recipe pilot tests.
F. Authorization/no-access tests.
G. Provider-abstraction contract tests.
H. Query recipe and SQL policy regressions.
I. Golden baseline.
J. Phase 2A/2B/2C/2C.5/2D focused regression slice.
K. Full backend configured suite.
L. Coverage gate.
M. `git diff --check`.
N. added-code scan for excluded technologies.

The previous accepted full-suite baseline was approximately:

962 passed
3 skipped
86.75% coverage
75% required gate

Do not force those exact counts after adding tests.

Report the actual results.

Any failing test, unexplained skip increase, material coverage regression, or golden-baseline drift blocks readiness.

==================================================
22. EXCLUDED TECHNOLOGY SCAN
==================================================

Scan added Phase 2E implementation code and confirm no new runtime dependency or implementation for:

- Databricks
- Genie
- Unity Catalog
- Collibra
- Redis
- Event Hubs
- Kafka/message bus
- graph database
- cross-source execution
- cross-source joins
- SQL dialect abstraction
- SQL compiler
- intermediate execution specification
- new provider SDK
- new authorization engine
- fine-grained row/column authorization
- frontend framework changes
- deployment/Terraform changes

Mentions inside ADR non-goals and negative test constants are acceptable.

Runtime imports or stubs are not acceptable.

==================================================
23. EXPLICITLY OUT OF SCOPE
==================================================

Do not implement:

- full VALID / REVIEW_REQUIRED / BROKEN lifecycle classification;
- recipe reapproval workflow;
- recipe admin UI;
- recipe registry API;
- migration of more recipes;
- KPI catalogue;
- business glossary;
- business-rule registry;
- report-template registry;
- relationship emission;
- join graph;
- metadata graph service;
- lineage graph;
- graph database;
- Databricks adapter;
- Genie integration;
- Collibra integration;
- Unity Catalog integration;
- Redis;
- result caching;
- cross-source support;
- emitted-table versus governed-dataset cross-check;
- pre-existing denial-message physical-object disclosure repair;
- orchestrator decomposition;
- frontend work;
- infrastructure;
- registry seed migration;
- folding ApprovedRecipe objects into RegistrySnapshot identity.

Record these as deferred work only.

==================================================
24. ROLLBACK REQUIREMENTS
==================================================

Rollback must remain simple:

- Phase 2E field emission flag OFF:
  - zero emitted FieldRecords;
  - previous Phase 2D snapshot behavior;
  - previous registry version restored for equivalent seed content.
- Phase 2D pilot flag OFF:
  - recipe field refs are not consulted;
  - legacy behavior remains unchanged.
- No schema migration.
- No data migration.
- No infrastructure rollback.
- No persisted graph/cache cleanup.

Test the rollback behavior explicitly.

==================================================
25. DIFF DISCIPLINE
==================================================

Before finishing:

1. Show the complete changed-file inventory.
2. Verify every changed file belongs to the approved Phase 2E scope.
3. Verify no primary-checkout dirty file was copied into the Phase 2E branch.
4. Verify no report file is inside the Git candidate.
5. Run:
   - git status --short
   - git diff --name-status
   - git diff --stat
   - git diff --check
6. Compute deterministic per-file SHA-256 hashes for the candidate files.
7. Compute one combined candidate digest.
8. Record the Phase 2D parent SHA.
9. Leave the candidate uncommitted for independent review.

Do not stage any file.

==================================================
26. IMPLEMENTATION REPORT
==================================================

Save the implementation report OUTSIDE the Git worktree, but inside the permanent project area:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_IMPLEMENTATION_2026-08-23.md

Create the `reports` directory if needed.

Do not use `/tmp`.

The report must include:

1. Live repository and PR state.
2. Verified Phase 2D parent SHA.
3. Worktree and branch identity.
4. ADR 0005 summary.
5. Complete changed-file inventory.
6. Field evidence source and schema.
7. Field-ID normalization contract.
8. Fail-closed evidence rules.
9. FieldRecord emission behavior.
10. Flag-off compatibility proof.
11. Pilot governed-field refs.
12. GovernedSemanticPlan validation path.
13. Dependency-fingerprint algorithm.
14. Dependency reverse-index behavior.
15. Authorization separation proof.
16. Relationship/graph deferral proof.
17. Strict-mode runtime dependency.
18. Test results by layer.
19. Full suite and coverage.
20. Golden baseline.
21. Excluded-technology scan.
22. Rollback proof.
23. Candidate hashes/digest.
24. Remaining risks and deferred items.
25. Exact minimum re-review scope.
26. Final verdict.
27. Completion-state attestation.

==================================================
27. FINAL VERDICT
==================================================

Return exactly one of these final tokens:

PHASE_2E_IMPLEMENTATION_READY_FOR_INDEPENDENT_REVIEW

or:

PHASE_2E_IMPLEMENTATION_BLOCKED_<REASON>

READY requires:

- ADR first;
- bounded source scope;
- real evidenced FieldRecords;
- no invented datasets;
- field-scoped pilot plan validates;
- missing referenced field fails closed with zero side effects;
- dependency fingerprint ignores unrelated changes;
- dependency fingerprint changes for relevant semantic changes;
- flag-off behavior reproduces Phase 2D;
- full tests and coverage pass;
- golden baseline unchanged;
- no excluded technology;
- no unrelated diff.

==================================================
28. COMPLETION STATE
==================================================

At the end explicitly report:

Primary checkout files modified: Yes/No
Primary checkout dirty files touched: Yes/No
Permanent Phase 2E worktree created: Yes/No
Phase 2E branch created: Yes/No
Repository source files modified: Yes/No
ADR 0005 created: Yes/No
Tests added/updated: Yes/No
Files staged: Yes/No
Commit created: Yes/No
Branch pushed: Yes/No
PR created: Yes/No
PR #15 changed: Yes/No
PR #16 changed: Yes/No
main changed: Yes/No
Deployment configuration changed: Yes/No
Strict mode enabled in an environment: Yes/No
Phase 2F started: Yes/No
Implementation report path: <exact path>

Expected at this stage:

- source files modified: Yes;
- branch/worktree created: Yes;
- commit/push/PR: No;
- PR #15/#16/main changed: No;
- deployment and strict-mode environment changes: No;
- Phase 2F started: No.

STOP after the candidate is ready for independent review.
