We are continuing the existing AskTD / askAlpha / KMAI implementation after the successful formal closure of Program Phase 2C.

Phase 2C status:

PHASE_2C_POST_MERGE_CLOSURE_PASS

Do NOT reopen Phase 2C.

Do NOT start Phase 2D recipe implementation yet.

This task is:

READ-ONLY DISCOVERY / ARCHITECTURE-TO-CODE MAPPING ONLY

Do not modify any repository file.

⸻

Objective

Determine the smallest safe implementation required to introduce the previously approved provider-abstraction foundation before Phase 2D.

The intended internal seams are:

DataSourceAdapter
    ├── SqlServerAdapter
    ├── DatabricksSqlAdapter       # contract/future implementation
    └── future adapters
DataGovernanceProvider
    ├── AskTDRegistryProvider
    ├── UnityCatalogProvider       # future
    ├── CollibraProvider           # future
    └── future providers
ExecutionProvider
    ├── DirectSqlExecutionProvider
    ├── DatabricksSqlExecutionProvider   # future
    └── GenieExecutionProvider           # future evaluation only
AuthorizationScope
    allowed_entities       # MVP
    allowed_datasets       # future
    allowed_columns        # future
    row_scope              # future

These are architecture concepts, not permission to create all of these implementations now.

The goal is to find the minimum seam needed so the current SQL Server/Azure SQL implementation can sit behind stable contracts without changing current behavior.

⸻

Architecture rules

Preserve these decisions:

1. AskTD must remain provider-agnostic.
2. The semantic planner must not depend directly on:
    * SQL Server;
    * Databricks;
    * Unity Catalog;
    * Collibra;
    * Genie.
3. Azure SQL / SQL Server remains the current concrete analytical path.
4. Databricks is NOT being integrated in this task.
5. Genie is NOT being implemented.
6. Unity Catalog and Collibra are NOT being integrated.
7. MVP authorization remains application-controlled entity-level authorization.
8. Fine-grained dataset/column/row authorization is future work.
9. Do not add Redis.
10. Do not add Event Hubs.
11. Do not redesign hosting, React/FastAPI topology, agents, or deployment.
12. Preserve all Phase 2A/2B/2C contracts and behavior.

⸻

1. Verify repository state

Report:

* repository;
* current branch;
* HEAD SHA;
* origin/main SHA;
* working-tree status.

Confirm Phase 2C is present in main.

Do not create or switch branches.

⸻

2. Find existing data-source boundaries

Inspect the current code and identify all important components involved in:

* Azure SQL / SQL Server connection;
* SqlDataStore or equivalent;
* query execution;
* SQL generation/compiler behavior;
* query timeout/cancellation;
* result retrieval;
* source configuration;
* any existing source registry or source abstraction.

For each relevant component report:

* file path;
* class/function;
* responsibility;
* callers;
* dependencies;
* whether it is provider-specific;
* whether it already behaves like part of a DataSourceAdapter.

Answer:

What is the smallest change that can put the current SQL implementation behind a DataSourceAdapter contract without rewriting working SQL behavior?

⸻

3. Find existing metadata/governance boundaries

Inspect:

* MetadataRegistryService;
* RegistrySnapshot;
* registry loaders;
* semantic planner metadata access;
* metadata lookup/search paths;
* Azure AI Search metadata use where relevant;
* any direct metadata-source assumptions.

Determine whether an existing object/service can naturally become:

AskTDRegistryProvider

behind:

DataGovernanceProvider

without changing Phase 2C canonical metadata contracts.

The canonical model must remain:

ProductGroup
  -> Schema
    -> Dataset
      -> Field
Relationship
BusinessTerm
KPI
Classification
Owner
Source
RegistryVersion

External providers must eventually map into this model.

Do not design Unity Catalog or Collibra mappings in detail yet.

⸻

4. Find existing execution boundary

Trace the current path from:

validated semantic/query intent
    ->
SQL candidate
    ->
SQL safety validation
    ->
execution
    ->
result

Identify:

* where execution is currently initiated;
* which class actually executes SQL;
* where SQL Server-specific behavior enters;
* whether source selection and execution are currently coupled;
* the smallest place to introduce ExecutionProvider.

Determine whether:

DirectSqlExecutionProvider

should wrap an existing component rather than replacing it.

Do not implement it.

⸻

5. AuthorizationScope discovery

Inspect the current authorization implementation.

Identify:

* existing authenticated-user representation;
* group/entity entitlement representation;
* current allowed_entities or equivalent;
* where metadata is filtered by authorization;
* where semantic planning receives authorized scope;
* any existing canonical authorization/scope object.

Determine whether an existing contract should be extended or wrapped instead of creating a parallel authorization model.

For MVP preserve only current entity-level behavior.

Do not implement dataset/column/row enforcement.

⸻

6. Configuration discovery

Inspect existing configuration patterns for:

* data source;
* SQL provider;
* metadata source;
* environment;
* execution behavior.

Determine the smallest configuration model required eventually to support explicit provider selection such as:

data_source_provider
governance_provider
execution_provider

Do not change configuration in this audit.

Do not expose provider-specific configuration to the semantic planner.

⸻

7. Dependency direction audit

Produce the current dependency direction for:

Semantic Planner
Metadata Registry
Authorization
SQL generation
SQL validation
SQL execution
Data source

Identify any current direct dependency that would prevent future replacement of SQL Server or metadata providers.

Classify every finding:

* ALREADY_ABSTRACTED
* MINOR_SEAM_REQUIRED
* COUPLED_REQUIRES_REFACTOR
* OUT_OF_SCOPE
* INSUFFICIENT_EVIDENCE

Do not label ordinary current SQL implementation as a defect merely because SQL Server is currently concrete.

⸻

8. Existing tests

Find existing tests that can protect behavior while provider seams are introduced.

Report tests covering:

* SQL execution;
* SQL safety;
* metadata registry;
* semantic planner;
* authorization;
* source/config behavior;
* Phase 2A/2B/2C compatibility.

Identify the minimum new contract tests that would be required for the abstraction foundation.

Do not write them in this task.

⸻

9. Proposed minimum Phase 2C.5 implementation

Based on actual code evidence, provide the smallest implementation sequence.

Prefer something approximately like:

1. define DataSourceAdapter protocol/interface;
2. wrap current SQL implementation as SqlServerAdapter;
3. define DataGovernanceProvider;
4. wrap current registry service as AskTDRegistryProvider;
5. define ExecutionProvider;
6. wrap current direct SQL execution;
7. introduce/normalize extensible AuthorizationScope;
8. add provider-selection configuration;
9. add contract tests;
10. prove existing behavior unchanged.

But do NOT force this exact structure if repository evidence shows existing abstractions should be reused.

For every proposed change give:

* exact file to modify;
* exact new file if needed;
* symbol/class to add or change;
* reason;
* compatibility impact;
* tests required.

⸻

10. Explicitly identify what must NOT be implemented

The report must explicitly confirm that this foundation does NOT require:

* Databricks SQL connection code;
* Unity Catalog API code;
* Collibra API code;
* Genie API code;
* cross-source joins;
* fine-grained row/column authorization;
* Redis;
* Event Hubs;
* Phase 2D recipes;
* KPI/glossary work;
* deployment changes.

Stubs should not be added merely for visual completeness unless they are required to prove the contract.

⸻

11. Final decision

Return exactly one:

PHASE_2C5_FOUNDATION_READY_FOR_BOUNDED_IMPLEMENTATION

or

PHASE_2C5_FOUNDATION_REQUIRES_ARCHITECTURE_DECISION

or

PHASE_2C5_FOUNDATION_INSUFFICIENT_EVIDENCE

Use READY only if the contracts can be introduced without making an unresolved enterprise architecture decision.

⸻

Output

Save the report outside the Git worktree:

/tmp/ASKTD_PHASE_2C5_PROVIDER_ABSTRACTION_DISCOVERY_2026-08-21.md

Sections:

1. Repository State
2. Current Data Source Architecture
3. Current Governance / Metadata Architecture
4. Current Execution Architecture
5. Current Authorization Architecture
6. Current Configuration Architecture
7. Dependency / Coupling Matrix
8. Existing Test Protection
9. Minimum Proposed Phase 2C.5 Changes
10. Files That Would Change
11. Explicitly Out of Scope
12. Open Decisions / Assumptions
13. Final Verdict
14. Recommended Single Next Action

This task is strictly read-only.

At completion state:

* Repository files changed: No
* Git state changed: No
* PR state changed: No
* Databricks implemented: No
* Genie implemented: No
* Phase 2D started: No

Then STOP.
