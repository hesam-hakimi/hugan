We are continuing the existing AskTD / askAlpha / KMAI project.

Program Phase 2C is formally closed:

PHASE_2C_POST_MERGE_CLOSURE_PASS

The read-only Phase 2C.5 discovery concluded:

PHASE_2C5_FOUNDATION_READY_FOR_BOUNDED_IMPLEMENTATION

This task is a BOUNDED IMPLEMENTATION of the minimum provider-abstraction foundation required before Phase 2D.

Do NOT start Phase 2D recipe implementation.

⸻

1. Critical repository rule

The existing primary checkout asktd_v2 is stale and does not contain the integrated Phase 2A/2B/2C implementation.

Do NOT implement this work on asktd_v2.

First verify current:

origin/main

contains the formally accepted Phase 2C implementation.

Then create a new dedicated branch/worktree from the exact current origin/main.

Suggested branch name:

phase2/provider-abstraction-foundation

Use the repository’s normal safe worktree/branch workflow.

Before mutation record:

* repository identity;
* origin/main SHA;
* new branch;
* worktree path;
* clean working-tree status.

If Phase 2C is not present in origin/main, STOP.

⸻

2. Discovery findings to preserve

The prior repository audit found:

Execution seam — already exists

Existing abstraction:

contracts/tool_base.py::DatabaseTool

with existing concrete implementations and configuration-based selection in the application.

Do not create a competing ExecutionProvider hierarchy merely to rename an existing abstraction.

Treat the existing DatabaseTool boundary as satisfying the execution-provider architectural seam unless implementation evidence encountered during this task proves otherwise.

Governance seam — already exists

Existing abstraction/substance:

MetadataRegistryService

operating on canonical:

RegistrySnapshot

Do not introduce a duplicate metadata-provider layer merely for naming symmetry.

Preserve canonical Phase 2C metadata:

ProductGroup
  -> Schema
    -> Dataset
      -> Field
Relationship
RegistryVersion
...

Future Unity Catalog / Collibra providers must eventually map into this canonical model, but they are NOT implemented now.

Authorization seam — already exists

Existing scope model:

EffectivePermissions

with current entity-level allowlists and fail-closed behavior.

Extend/reuse this model.

Do not create a parallel AuthorizationScope model.

Do not implement dataset-, column-, or row-level authorization in this task.

Data-source seam — actual missing foundation

Existing:

SqlDataStore

already exposes an adapter-shaped API but has no declared provider-neutral contract.

The prior audit found direct SqlDataStore construction/coupling in Orchestrator at approximately three construction points and two direct type hints.

This is the main implementation target.

⸻

3. Objective

Introduce the smallest provider-neutral data-source contract so that core orchestration depends on an abstraction rather than directly depending on SqlDataStore.

Current behavior must remain unchanged.

Target conceptual dependency:

Orchestrator
    |
    v
DataSourceAdapter
    |
    v
SqlDataStore   # current concrete implementation

Do NOT rename SqlDataStore merely for aesthetic consistency.

Do NOT rewrite its working SQL implementation.

⸻

4. DataSourceAdapter contract

Inspect the actual public API currently required from SqlDataStore by its consumers.

Define the smallest typed interface/protocol/ABC representing only the behavior actually required by the orchestration/core layer.

Prefer a lightweight Python Protocol if compatible with the repository’s typing/version conventions.

Do not expose SQL Server-specific concepts in the contract unless they are genuinely required by current callers.

The contract should represent capabilities, not a future Databricks design.

Examples of candidate capabilities may include current operations such as:

* executing an approved read query;
* retrieving result rows;
* connection/query lifecycle behavior;
* timeout/cancellation if already exposed;

but derive the exact interface from existing code.

Do not invent unused methods.

⸻

5. Preserve SqlDataStore behavior

Make existing SqlDataStore satisfy the new contract with the minimum possible change.

Prefer structural typing where possible so implementation changes are minimal.

Do not:

* rewrite SQL connection handling;
* change SQL generation;
* change SQL safety;
* change retry semantics;
* change authorization;
* change result shape;
* change environment/config behavior.

Existing behavior must remain byte-for-byte/semantically equivalent where practical.

⸻

6. Remove core Orchestrator coupling

Inspect every direct:

SqlDataStore(...)

construction and direct SqlDataStore type annotation in the orchestration/core path.

Replace those dependencies with the new adapter contract through the smallest safe injection/factory seam.

Important:

Do not introduce a dependency-injection framework.

Reuse existing configuration/factory construction patterns if present.

A simple explicit constructor/factory boundary is preferred.

The runtime default must continue to construct/use the existing SQL implementation.

There must be no behavior change for existing users.

⸻

7. Configuration

Do NOT introduce speculative provider configuration if current code does not need it.

If a source/provider selector already exists, reuse it.

If one minimal selector is genuinely required to remove the direct construction coupling, add only the smallest backward-compatible configuration required.

Default behavior must remain the current SQL path.

Do not add config values for:

* Databricks;
* Unity Catalog;
* Collibra;
* Genie.

No future provider should be selectable until it actually exists.

⸻

8. ExecutionProvider compatibility proof

Do not add a new ExecutionProvider hierarchy unless repository evidence proves the discovery result was incorrect.

Instead add/extend tests that demonstrate:

* the core execution path depends on the existing DatabaseTool abstraction rather than one hard-coded concrete execution provider where applicable;
* current configuration still selects the current implementation;
* behavior remains unchanged.

If an unavoidable gap is found, STOP and report it before broadening scope.

⸻

9. DataGovernanceProvider compatibility proof

Do not wrap MetadataRegistryService in a meaningless forwarding class merely to create a name called DataGovernanceProvider.

Instead verify through tests/types that semantic planning/core code consumes canonical registry/service contracts rather than provider-specific Unity/Collibra structures.

If a lightweight Protocol is useful at an actual dependency boundary, it may be added only if it removes real coupling.

Do not add:

* UnityCatalogProvider;
* CollibraProvider;
* provider stubs.

⸻

10. AuthorizationScope compatibility proof

Reuse EffectivePermissions.

If necessary, make only additive typing/documentation changes proving that it can later support additional optional scope dimensions.

Current behavior remains:

allowed_entities

or its existing equivalent.

Do not implement:

* allowed_datasets;
* allowed_columns;
* row_scope;

unless those fields already exist and only need preservation.

Do not change authorization decisions.

⸻

11. Contract tests

Add focused tests proving the architecture seam rather than testing hypothetical providers.

At minimum verify:

Data-source contract

* current SqlDataStore satisfies/implements DataSourceAdapter;
* orchestrator/core accepts a test/fake adapter without constructing SqlDataStore;
* normal default runtime still selects/uses current SQL behavior;
* no SQL Server-specific concrete type is required by core orchestration after the seam.

Governance boundary

* canonical registry service remains the metadata contract used by Phase 2C planning/validation;
* no external-provider-specific structure enters semantic planning.

Execution boundary

* existing DatabaseTool abstraction remains the execution-provider seam;
* existing concrete selection behavior is unchanged.

Authorization

* existing EffectivePermissions behavior remains fail-closed/entity-scoped;
* introducing the provider seam does not bypass authorization.

Prefer focused contract tests over broad mocking.

⸻

12. Dependency-direction acceptance requirement

After implementation, the intended direction must be demonstrably:

Core / Orchestrator
        |
        +--> DataSourceAdapter
        |       |
        |       +--> SqlDataStore
        |
        +--> MetadataRegistryService / canonical registry boundary
        |
        +--> DatabaseTool execution abstraction
        |
        +--> EffectivePermissions authorization boundary

Core planning/orchestration must not newly import:

* Databricks SDK;
* Unity Catalog models;
* Collibra clients;
* Genie clients.

⸻

13. Explicit out of scope

Do NOT implement:

* Databricks SQL adapter;
* Databricks authentication;
* Unity Catalog provider;
* Collibra provider;
* Genie provider;
* provider stubs with NotImplementedError;
* SQL dialect abstraction for Databricks;
* cross-source joins;
* new query recipes;
* KPI/glossary functionality;
* Phase 2D recipe pilot;
* Redis;
* Event Hubs;
* fine-grained authorization;
* deployment/infrastructure changes;
* frontend changes;
* broad orchestrator redesign.

Also do not address unrelated existing items such as:

* hard-coded dbo.* semantic models;
* literal T-SQL in existing recipe code;
* broader planner migration to the governed registry;

unless required to make this very small abstraction compile/test.

Those belong to later bounded work and must not expand this change.

⸻

14. Test gates

Run focused tests for every changed component first.

Then run:

1. Phase 2A/2B/2C focused regression;
2. MetadataRegistryService integration tests;
3. relevant authorization tests;
4. relevant SQL datastore/orchestrator tests;
5. full backend regression;
6. configured coverage gate;
7. golden baseline;
8. git diff --check.

Do not regenerate golden baselines.

Do not install or upgrade dependencies.

Classify any failure before changing additional code.

⸻

15. Diff discipline

Before finishing, inspect the complete diff against the origin/main SHA from which the branch was created.

The diff must contain only the bounded Phase 2C.5 foundation.

Specifically confirm:

* no Phase 2D implementation;
* no Databricks/UC/Collibra/Genie code;
* no unrelated refactor;
* no infrastructure changes;
* no frontend changes;
* no hidden behavior changes to existing SQL execution.

⸻

16. Documentation

Add one small architecture/ADR note only if consistent with the repository’s existing ADR conventions.

It should record that:

* the current SQL data path is now behind DataSourceAdapter;
* DatabaseTool satisfies the execution-provider seam;
* MetadataRegistryService satisfies the current governance-provider seam;
* EffectivePermissions is the extensible authorization-scope foundation;
* future providers must map into canonical AskTD contracts;
* no Databricks/Genie/Collibra/Unity implementation was added.

Do not rewrite the enterprise architecture documents.

⸻

17. Stop conditions

STOP instead of making an architecture decision if implementation reveals that:

* removing SqlDataStore coupling requires redesigning SQL semantics;
* an existing abstraction contradicts the approved provider-agnostic architecture;
* a new provider-specific choice is required;
* Phase 2C behavior must change;
* fine-grained authorization becomes necessary.

Report the exact blocker.

⸻

18. Final verdict

Return exactly one:

PHASE_2C5_IMPLEMENTATION_READY_FOR_INDEPENDENT_REVIEW

or

PHASE_2C5_IMPLEMENTATION_HAS_BLOCKERS

or

PHASE_2C5_IMPLEMENTATION_INSUFFICIENT_EVIDENCE

READY requires:

* bounded implementation complete;
* existing behavior preserved;
* contract tests pass;
* Phase 2A/2B/2C regressions pass;
* full regression/coverage/golden gates acceptable;
* diff is scoped;
* no future provider implementation entered the change.

⸻

19. Git behavior

Implementation may modify files in the new dedicated Phase 2C.5 worktree.

Do NOT:

* merge;
* deploy;
* modify main;
* modify asktd_v2;
* start Phase 2D.

Do not push automatically unless the normal project workflow explicitly requires a pushed branch for review.

If a push is needed, ask before pushing.

⸻

Required report

Save outside the Git worktree:

/tmp/ASKTD_PHASE_2C5_PROVIDER_ABSTRACTION_IMPLEMENTATION_2026-08-21.md

Include:

1. Repository / Branch Evidence
2. Discovery Findings Revalidated
3. DataSourceAdapter Implementation
4. Orchestrator Decoupling
5. Existing ExecutionProvider Mapping
6. Existing GovernanceProvider Mapping
7. AuthorizationScope Mapping
8. Configuration Impact
9. Contract Tests
10. Regression / Coverage / Golden Results
11. Diff Against Main
12. Files Changed
13. Explicit Out-of-Scope Confirmation
14. Remaining Risks / Decisions
15. Final Verdict
16. Recommended Next Action

At completion report:

* branch;
* base SHA;
* current HEAD;
* files changed;
* tests;
* coverage;
* golden baseline;
* repository pushed: Yes/No;
* Phase 2D started: No.

Then STOP.
