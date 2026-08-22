I want to continue development of the existing AskTD / askAlpha / KMAI project from the previous sessions.

This is a CONTINUATION of an existing project.

Do NOT redesign the system from scratch.

Do NOT infer current implementation state from this prompt alone.

Do NOT immediately start coding.

The ChatGPT Library and external documentation were comprehensively refreshed on 2026-08-22 after substantial Phase 2C, Phase 2C.5, Phase 2D discovery, roadmap, reporting, graph, provider, and caching work.

Your first responsibility is to reconstruct the authoritative current state from those documents.

==================================================

1. LOAD THE AUTHORITATIVE LIBRARY CONTEXT FIRST
    ==================================================

Search my ChatGPT Library for AskTD / askAlpha / KMAI documents.

Start with the newest 2026-08-22 documents.

At minimum, locate and read COMPLETELY:

1. AskTD_Library_Index_2026-08-22.md
2. AskTD_Implementation_Phase_Status_2026-08-22.md
3. AskTD_Architecture_and_Roadmap_Update_2026-08-22.md
4. AskTD_Assumption_Decision_Log_2026-08-22.md
5. AskTD_Management_Roadmap_and_Feature_Map_2026-08-22.md
6. AskTD_Session_Continuation_Handoff_2026-08-22.md
7. AskTD_Unity_Catalog_Genie_Architecture_Update_2026-08-22.md

Then read the updated master references:

8. AskTD_Enterprise_Architecture_Master_Reference_2026-08-11_Architect_Aligned.md
9. AskTD_Enterprise_Architecture_Master_Reference_2026-08-10.md
10. askalpha_asktd_updated_master_handoff_2026-08-04.md

The master documents contain a:

AUTHORITATIVE UPDATE — 2026-08-22

That section overrides older conflicting implementation assumptions.

Do not stop after finding snippets.

Read enough of the complete documents to understand:

* current implementation;
* architecture history;
* security/authentication;
* authorization;
* metadata architecture;
* RegistrySnapshot;
* registry_version;
* Phase 2A;
* Phase 2B;
* Phase 2C;
* Phase 2C remediation and final acceptance;
* Phase 2C.5 provider abstraction;
* DataSourceAdapter;
* DatabaseTool;
* MetadataRegistryService;
* EffectivePermissions;
* Phase 2D Approved Recipe discovery;
* recipe lifecycle and dataset-change compatibility;
* Phase 2E business semantics;
* Phase 2F Answer Intelligence & Reporting;
* Phase 2G controlled publish/change lifecycle;
* Governed Semantic Graph;
* caching and Redis;
* SQL Server;
* Databricks;
* Unity Catalog;
* Collibra;
* Genie;
* SpruceX;
* DAC;
* PIA;
* current architecture assumptions;
* development blockers versus integration blockers;
* management roadmap.

If any required document cannot be found, tell me EXACTLY which document is missing before proceeding.

Also search for any AskTD/askAlpha reference document newer than 2026-08-22.

If one exists, read it and explain whether it supersedes any part of the 2026-08-22 baseline.

==================================================
2. EXTERNAL DOCUMENTATION

The external/public planning repository is:

hesam-hakimi/usefull_prompt

Relevant documentation branch:

docs/askalpha-roadmap-self-service-multisource-v1

The documentation pack was refreshed to revision 1.7 on 2026-08-22.

Important updated external documents include:

docs/architecture/
ASKTD_ARCHITECTURE_AND_ROADMAP_UPDATE_2026-08-22.md

docs/architecture/
ASKTD_UNITY_DAC_GENIE_PROVIDER_UPDATE_2026-08-22.md

docs/plans/
ASKTD_IMPLEMENTATION_PHASE_STATUS_2026-08-22.md

docs/plans/
ASKTD_ASSUMPTION_DECISION_LOG_2026-08-22.md

docs/plans/
ASKTD_MANAGEMENT_ROADMAP_FEATURE_MAP_2026-08-22.md

docs/plans/
ASKTD_SESSION_CONTINUATION_HANDOFF_2026-08-22.md

Also inspect:

docs/architecture/README.md
docs/plans/README.md

These README files define the updated source-of-truth reading order.

The external repository is documentation/planning evidence.

It is NOT proof of private runtime implementation.

==================================================
3. STATUS DISCIPLINE

Every important statement must be classified as one of:

CURRENT / IMPLEMENTED

TECHNICALLY VALIDATED

MERGED / ACCEPTED

WORKING DECISION

WORKING ASSUMPTION

PLANNED

TARGET

OPEN

REJECTED / DO NOT ASSUME

Do not turn plans or architecture diagrams into implementation facts.

Do not turn integration discussions into enterprise architecture decisions.

==================================================
4. CURRENT PROGRAM STATUS TO VERIFY

The 2026-08-22 documents report approximately:

Phase 2A
Governed Registry Contracts

Status:
MERGED / ACCEPTED

Phase 2B
Registry Service + Version Boundary + Bounded Cache

Status:
MERGED / ACCEPTED

Phase 2C
ProductGroup -> Schema -> Dataset -> Field
+
RelationshipRecords
+
Governed Semantic Plan
+
Deterministic Validator

Status:
CLOSED / ACCEPTED

Phase 2C passed:

* final independent acceptance;
* merge;
* post-merge closure verification.

Do NOT reopen Phase 2C without concrete regression evidence.

Phase 2C.5
Provider Abstraction Foundation

Reported status:

TECHNICALLY VALIDATED

The implementation passed:

PHASE_2C5_INDEPENDENT_REVIEW_PASS

after an earlier independent review correctly identified incomplete dependency inversion and a bounded remediation fixed it.

The accepted dependency direction is:

Composition Root
↓
SqlDataStore

Orchestrator
↓
DataSourceAdapter

Existing additional seams:

Execution
-> DatabaseTool

Governance
-> MetadataRegistryService
-> RegistrySnapshot

Authorization
-> EffectivePermissions

Do NOT create duplicate abstractions merely to obtain names such as:

ExecutionProvider
DataGovernanceProvider
AuthorizationScope

when repository evidence shows the existing contracts already provide those seams.

==================================================
5. CRITICAL LIVE STATE: PR #15

Phase 2C.5 was committed and pushed to:

phase2/provider-abstraction-foundation

Draft PR:

#15

Base:

main

Last observed state:

* Draft PR created;
* candidate independently technically accepted;
* branch pushed;
* CI/review/approval/merge workflow was still open.

IMPORTANT:

Do NOT assume PR #15 is still open.

The state may have changed since the documentation update.

Before starting Phase 2D implementation, verify the LIVE repository/GitHub state of PR #15.

Determine:

* Open / Closed / Merged;
* Draft / Ready;
* base;
* head;
* head SHA;
* checks;
* review/approval state;
* merge/conflict state;
* whether Phase 2C.5 is present in current main.

==================================================
6. PHASE 2C.5 ARCHITECTURE BOUNDARY

Phase 2C.5 intentionally did NOT implement:

* Databricks adapter;
* Databricks authentication;
* Unity Catalog provider;
* Collibra provider;
* Genie provider;
* Redis;
* Event Hubs;
* cross-source joins;
* fine-grained authorization;
* Phase 2D recipes.

Current SQL Server/Azure SQL behavior remains supported.

Provider independence means:

Core depends on contracts.

It does NOT mean all future providers must already exist.

==================================================
7. CURRENT CACHE / REDIS POSITION

Caching exists today.

The implemented cache is:

BOUNDed IN-PROCESS RegistrySnapshot / metadata cache.

It supports approximately:

* current snapshot lookup;
* retained version lookup;
* bounded capacity;
* TTL/retention;
* deterministic eviction;
* invalidation;
* metrics;
* immutable/deep-copy retrieval;
* concurrency contract.

It is NOT:

* a query-result cache;
* a distributed cache;
* Redis;
* durable audit storage.

Because it is in-process:

* every process owns its own cache;
* process restart clears it;
* multiple App Service instances do not automatically share it.

Redis / Azure Managed Redis is NOT a current required runtime dependency.

Do not add Redis merely because configuration or historical architecture material mentions it.

A future distributed cache requires a measured use case such as:

* multi-instance query-result caching;
* scope-aware shared cache;
* distributed metadata invalidation;
* approved UI/Agent streaming/session requirements.

Any future result cache must be authorization-scope-aware.

Redis never replaces durable audit/event storage.

==================================================
8. CURRENT DEVELOPMENT CONTINUATION: PHASE 2D

Phase 2D is:

APPROVED RECIPE PILOT

A repository-backed discovery was already completed.

Discovery verdict:

PHASE_2D_DISCOVERY_READY_FOR_BOUNDED_IMPLEMENTATION

Do NOT repeat the entire discovery unless repository changes invalidate it.

Phase 2D implementation has NOT formally started.

==================================================
9. PHASE 2D PURPOSE

The objective is NOT to build a complete enterprise recipe platform.

The objective is to prove ONE controlled governed business route.

Conceptual flow:

User Question
↓
current entity authorization
↓
deterministic recipe selection
↓
ApprovedRecipe
↓
GovernedSemanticPlan
↓
validation against current RegistrySnapshot
↓
existing safe SQL/query builder
↓
DataSourceAdapter
↓
current execution path
↓
validated answer
↓
recipe/registry/audit evidence

The LLM must NOT invent an ungoverned business recipe.

==================================================
10. PHASE 2D PILOT CANDIDATE

The repository-backed discovery recommended:

source_balance_mom_change

covering the existing Q25/Q26-style source-balance month-over-month route.

Why it was selected:

* real existing deterministic business logic;
* one governed dataset;
* known parameters such as IMSB/STAX-style source input;
* existing runtime route;
* testable;
* does not require Databricks;
* does not require cross-source joins;
* does not require new authorization architecture.

Verify this candidate is still present before implementation.

==================================================
11. MINIMUM APPROVED RECIPE CONTRACT

Do not force fields from this prompt if repository evidence suggests a smaller contract.

The discovery indicated a pilot recipe likely needs only concepts such as:

recipe_id

recipe_version

intent / route identifier

governed_dataset_refs

required field/dependency refs where supported

allowed relationship refs where required

parameter schema

builder_key / deterministic execution builder reference

lifecycle status

enabled / approved state

Do NOT build a huge generic recipe DSL.

==================================================
12. RECIPE FRESHNESS WHEN DATASETS CHANGE

This is an important design decision.

Do NOT blindly pin recipe validity to an exact entire:

registry_version

because an unrelated metadata-description change should not invalidate every recipe.

Instead:

Recipe declares governed dependencies
↓
current RegistrySnapshot
↓
deterministic compatibility validation

If relevant dependencies remain compatible:

recipe remains usable.

If a required dependency changes incompatibly, for example:

* dataset removed;
* required field removed;
* field type incompatible;
* relationship removed;
* relationship key changed;
* required grain changed;

the recipe must:

FAIL CLOSED

and require a reviewed/new recipe version.

For audit/reproducibility record:

recipe_id
recipe_version
registry_version used
source/data freshness
validation result

Future lifecycle automation may classify recipes as:

VALID
STALE
REVIEW_REQUIRED
RETIRED

But do not build the complete lifecycle engine inside the first Phase 2D pilot.

==================================================
13. TWO METADATA WORLDS

Phase 2D discovery found that legacy runtime semantic/recipe logic and the newer governed:

RegistrySnapshot
+
GovernedSemanticPlan

world still coexist.

Do NOT solve the entire historical migration in Phase 2D.

The pilot should bridge ONE existing runtime route into the governed path.

Do not migrate every existing recipe.

Do not redesign the planner globally.

==================================================
14. PHASE 2D EXPECTED BOUNDED IMPLEMENTATION

The discovery suggested a small implementation surface approximately like:

NEW:
app/recipes/init.py

NEW:
app/recipes/approved_recipes.py

MODIFY:
app/orchestrator.py

PLUS:

* focused recipe tests;
* authorization negative tests;
* parameter validation tests;
* feature-flag OFF regression;
* feature-flag ON pilot tests;
* ADR 0004 or repository-equivalent architecture note.

Do not assume these exact paths if repository evidence changed.

The coding agent must inspect the current main before editing.

==================================================
15. PHASE 2D FEATURE FLAG

The pilot should be reversible.

Prefer:

feature flag default OFF

so:

OFF
-> existing behavior remains unchanged

ON
-> one approved recipe pilot path is enabled

Do not change unrelated routes.

==================================================
16. PHASE 2D NON-GOALS

Do NOT implement as part of Phase 2D:

* Databricks SQL;
* Databricks authentication;
* Unity Catalog integration;
* Collibra integration;
* Genie;
* Redis;
* Event Hubs;
* cross-source joins;
* complete recipe-management UI;
* complete recipe lifecycle automation;
* fine-grained dataset/column/row authorization;
* complete KPI/glossary platform;
* Governed Semantic Graph;
* GraphRAG;
* broad reporting redesign;
* Phase 2F answer/report templates;
* deployment architecture changes.

==================================================
17. NEXT ROADMAP AFTER PHASE 2D

Preserve the updated product roadmap.

⸻

PHASE 2E
BUSINESS SEMANTICS

Planned capabilities:

* KPI catalog;
* certified formulas;
* glossary;
* business terms;
* product taxonomy;
* canonical statuses;
* grain;
* inclusions/exclusions;
* caveats;
* ownership;
* lifecycle/versioning.

Purpose:

Make the organization agree on what the number means,
not only where the data lives.

⸻

PHASE 2F
ANSWER INTELLIGENCE & REPORTING EXPERIENCE

This phase has been explicitly expanded.

Planned capabilities include:

* better question clarification;
* better question-to-answer workflow;
* better agent/model routing;
* audience-aware answers;
* concise answers;
* analyst explanations;
* executive summaries;
* reusable report templates;
* management-ready layouts;
* KPI cards;
* formatted tables;
* charts;
* trends;
* period comparisons;
* variance;
* explanatory narratives;
* drill-down;
* follow-up suggestions;
* output selection based on question type;
* answer consistency;
* baseline reconciliation;
* quality regression tracking;
* evidence/source/freshness/caveat presentation.

Important product principle:

Phase 2D makes answers GOVERNED.

Phase 2F makes answers USEFUL, INTELLIGENT, CONSISTENT,
AND PRESENTATION-READY.

⸻

PHASE 2G
CONTROLLED PUBLISH & CHANGE LIFECYCLE

Planned:

Draft
→ Validate
→ Test
→ Approve
→ Publish

Plus:

* dry-run;
* rollback;
* retirement;
* emergency disable;
* dependency impact analysis;
* automatic stale/review-required detection;
* owner notification;
* version history;
* schema/metadata drift handling.

==================================================
18. GOVERNED SEMANTIC GRAPH ROADMAP

The roadmap now explicitly includes:

GOVERNED SEMANTIC GRAPH & MULTI-DATASET REASONING

Formal phase numbering remains open.

The graph builds on the existing Phase 2C foundation:

ProductGroup
→ Schema
→ Dataset
→ Field
+
RelationshipRecord

Future capabilities:

* governed dataset relationships;
* governed field relationships;
* approved traversal;
* approved join paths;
* grain/cardinality evidence;
* multi-dataset reasoning;
* semantic discovery;
* recipe discovery;
* lineage;
* explainability;
* controlled cross-domain reasoning.

Important:

Relationships must come from explicit governed records.

Do NOT infer enterprise relationships merely from similar names.

Graph existence does not grant authorization.

Authorization remains enforced independently.

GraphRAG is different.

GraphRAG for unstructured documents remains an OPTIONAL FUTURE enhancement and is NOT MVP Core.

==================================================
19. MULTI-PLATFORM ROADMAP

AskTD remains provider-agnostic.

Current:

SQL Server / Azure SQL

Future provider possibilities:

DataSourceAdapter
├── current SQL implementation
├── Databricks SQL adapter
└── future providers

Governance sources may eventually include:

AskTD Registry
Unity Catalog
Collibra
future systems

but all must map to canonical AskTD metadata.

Execution may eventually include:

Direct SQL
Databricks SQL
future Genie provider

Genie is:

FUTURE EVALUATION ONLY

It is NOT:

* a current dependency;
* a confirmed replacement;
* a reason to stop AskTD;
* assumed production-ready inside TD.

==================================================
20. SPRUCEX / DAC / DATABRICKS / PIA

These remain active parallel workstreams.

Open questions include:

* approved SpruceX data path;
* DAC copy/refresh vs AZ/Consumption views vs direct access/hybrid;
* freshness SLA;
* serving endpoint;
* cold/warm latency;
* concurrency;
* cost;
* workload identity;
* network/firewall;
* metadata source of truth;
* production promotion;
* PIA/model data boundary.

Do NOT silently choose these enterprise architecture decisions.

They are generally integration/production blockers,
not blockers for source-neutral Core development.

==================================================
21. FIRST ACTION IN THIS NEW SESSION

After reading the Library and external documents:

1. Verify the live state of PR #15.
2. Confirm whether Phase 2C.5 has been merged into main.
3. If PR #15 is NOT merged:
    Do NOT modify PR #15 casually.
    Tell me the safest options for continuing development without losing
    the independently reviewed Phase 2C.5 candidate.
    Consider whether a stacked Phase 2D branch from the exact PR #15 HEAD
    is appropriate.
    Do NOT perform it
