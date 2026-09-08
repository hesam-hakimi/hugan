Architecture Update Notice — Review Required Before Continuing Beyond Phase 2F

You are currently implementing Phase 2F of the AskAlpha / KMAI program.

Do NOT restart the implementation and do NOT redesign completed phases unless a
real compatibility issue is found.

Before continuing Phase 2F or planning later phases, incorporate the following
architecture updates as authoritative working decisions unless explicitly marked
Open / Planned / Future.

Your task is to:

1. Compare these architecture deltas with the current implementation.
2. Identify any Phase 2F code, contracts, tests, documentation, or future-phase
   plans that need adjustment.
3. Do not change already accepted earlier phases unless required for compatibility.
4. Clearly distinguish:
   - implemented compatibility changes;
   - documentation-only changes;
   - future-phase changes;
   - open architecture decisions.
5. Produce an impact report before making broad cross-phase changes.

==================================================
1. CACHE ORDERING HAS CHANGED
==================================================

The previous architecture placed cache lookup after Semantic Planning.

That is no longer the preferred design because Azure OpenAI may already have
been called before the cache can produce a hit.

The architecture now supports two cache levels:

A. Early Request / Template Cache

Location:

Authentication / Authorization
→ Intent Normalization
→ Template Match
→ EARLY CACHE
→ Semantic Planning only on cache miss

Purpose:

- avoid repeated semantic-planning / LLM calls;
- avoid repeated data queries where a valid authorized result already exists;
- accelerate predefined and repeatable questions.

The Early Cache key MUST NOT depend on semantic_plan_hash because the semantic
plan does not exist yet.

Candidate key dimensions include:

- authorization scope hash;
- normalized question / intent;
- predefined template ID where applicable;
- registry version;
- authorization-policy version;
- data-freshness version or bucket;
- requested output type.

B. Semantic / Result Cache

A second cache may remain after Semantic Planning for precise reuse of:

- semantic plans;
- validated bounded results;
- derived response payloads.

It may additionally use:

- semantic_plan_hash;
- recipe version;
- model-policy version;
- other post-plan versions.

IMPORTANT:

Never cache unrestricted data and filter it only after retrieval.

Cache implementation/platform remains:

PLANNED / PLATFORM TBD

Do not hard-code Redis or another cache technology unless separately approved.

==================================================
2. SEMANTIC REGISTRY IS THE BUSINESS-SEMANTIC SOURCE OF TRUTH
==================================================

The AskAlpha Semantic Registry is authoritative for governed business semantics,
including:

- Business Terms;
- KPI / Metric definitions;
- approved Relationships;
- Recipes;
- semantic definitions;
- canonical statuses;
- registry versions.

The Template Library MUST NOT duplicate independent business definitions.

Templates should reference governed semantic objects using stable identifiers
and versions, for example:

Template
→ KPI ID
→ Recipe ID
→ Registry Version

If Phase 2F currently embeds business definitions directly inside output
templates, dynamic suggestions, or template JSON, review and refactor that design
so the authoritative definition remains in the Semantic Registry.

==================================================
3. AUTHORIZATION MODEL — DO NOT BUILD ACL SYNCHRONIZATION
==================================================

For the current MVP:

AskAlpha is the source of truth for end-user authorization at the entity level.

Flow:

User signs in through Microsoft Entra ID
→ AskAlpha validates identity
→ AskAlpha resolves allowed entity scope
→ unauthorized requests are denied before metadata retrieval or query execution
→ authorized execution uses AskAlpha Managed Identity / MSI
→ the source platform verifies whether the AskAlpha service identity may access
   the approved source objects.

Do NOT implement continuous synchronization or reconciliation between AskAlpha
user permissions and SQL Server / Unity Catalog user ACLs.

That would add unacceptable complexity and maintenance overhead for the current
model.

If:

- the user is authorized in AskAlpha;
- but the AskAlpha MSI cannot access the required source object;

then:

- fail closed;
- return a safe service/source-access error;
- include a correlation ID;
- log the detailed provider/configuration error internally;
- do not expose raw provider errors, SQL, credentials, or paths to the user.

Future user-identity passthrough or provider-native user authorization would be
a separate architecture decision.

==================================================
4. RESPONSE FORMATTING IS NOW AN EXPLICIT ARCHITECTURE STAGE
==================================================

The response flow should explicitly include:

Validated Result
→ Response Formatting / Template Selection
→ Final Business Output

There are two possible formatting routes.

A. Deterministic Template Formatter

Preferred when:

- an approved output template exists;
- the question is repeated/common;
- output structure should be predictable;
- the use case is high-risk or highly governed.

This path should not require an LLM call.

B. Azure OpenAI Response Formatting

Status:

CONDITIONAL / PIA-DEPENDENT

Use only when:

- deterministic formatting is insufficient;
- the use case is explicitly approved;
- minimum necessary result context can safely be sent to the model.

If Azure OpenAI receives query-result data, treat that as a different privacy
boundary from semantic metadata.

Only send:

- authorized data;
- minimum necessary rows or aggregates;
- masked / redacted values;
- approved fields.

This route must be visible in architecture, audit, and privacy controls.

==================================================
5. FORMATTING ROUTING MUST BE DETERMINISTIC
==================================================

The LLM must not freely decide whether to use deterministic formatting or
AI-assisted formatting.

Use explicit routing rules such as:

approved template exists
→ deterministic formatter

no suitable template + AI formatting explicitly approved
→ AI-assisted formatter

The same validated analytical result must not silently produce materially
different business meaning depending on the formatting path.

==================================================
6. PHASE 2F MUST INCLUDE CONSISTENCY / REGRESSION TESTING
==================================================

Because Phase 2F covers output templates and dynamic suggestions, add or plan
tests that protect business-result consistency.

Where both deterministic and AI-assisted formatting are supported, use
golden-response / regression tests.

Verify that AI formatting does NOT alter:

- numeric values;
- KPI values;
- business meaning;
- authorization scope;
- warnings;
- as-of date;
- source attribution;
- material qualifiers.

AI formatting may change wording or presentation only within approved bounds.

==================================================
7. PREDEFINED QUESTIONS / TEMPLATE LIBRARY
==================================================

The architecture now includes a versioned predefined question/template library.

Purpose:

- common question patterns;
- approved template references;
- approved output structures;
- routing hints.

Usage analytics may identify the most common query patterns.

However:

- do NOT build autonomous daily self-rewriting templates;
- do NOT let runtime analytics directly modify production definitions.

The preferred governance model is:

Usage Analytics
→ Offline Analysis
→ Curated Selection
→ Review / Approval
→ Monthly or Approved Standard Release
→ Versioned Template Library

The exact cadence remains configurable, but monthly is the current working
direction.

==================================================
8. LARGE-DATA POSITION
==================================================

The current planning data volume is approximately 5 TB.

This does NOT mean 5 TB should be cached.

Caching should remain bounded and limited to items such as:

- small authorized result sets;
- aggregates;
- KPI outputs;
- semantic plans;
- metadata candidates;
- predefined-template matches;
- formatted response payloads where approved.

Large analytical queries continue to run on the underlying approved compute
platform.

Design cache size, TTL, invalidation, and eligibility independently from the raw
source-data size.

==================================================
9. PROVIDER-AGNOSTIC ARCHITECTURE REMAINS REQUIRED
==================================================

Do not hard-wire Core AskAlpha logic to:

- SQL Server;
- Databricks;
- Unity Catalog;
- Collibra;
- Genie.

Maintain or prepare these architectural seams:

DataSourceAdapter
  ├── SqlServerAdapter
  ├── DatabricksSqlAdapter
  └── Future Adapter

DataGovernanceProvider
  ├── AskAlphaRegistryProvider
  ├── UnityCatalogProvider
  ├── CollibraProvider
  └── Future Provider

ExecutionProvider
  ├── DirectSqlExecutionProvider
  ├── DatabricksSqlExecutionProvider
  └── Future GenieExecutionProvider

Provider-specific behavior must remain outside the canonical semantic-planning
contracts where possible.

==================================================
10. DATABRICKS GENIE STATUS
==================================================

Databricks Genie remains:

FUTURE / EVALUATION

It is NOT:

- a current dependency;
- a confirmed AskAlpha replacement;
- a reason to stop AskAlpha development;
- assumed production-ready for the program.

If it later proves suitable, it may be integrated as an ExecutionProvider behind
AskAlpha.

Do not implement Genie integration as part of Phase 2F unless a separate approved
scope explicitly requests it.

==================================================
11. CURRENT / PLANNED STATUS MUST REMAIN EXPLICIT
==================================================

Do not present planned capabilities as already deployed.

Current / Core examples:

- existing AskAlpha application;
- Entra authentication;
- entity-level application authorization direction;
- Semantic Registry work;
- semantic planning;
- SQL safety / read-only execution principles.

Planned / Open examples:

- scope-aware distributed cache;
- finalized Databricks runtime path;
- provider-specific metadata integrations not yet approved.

Conditional:

- Azure OpenAI response formatting.

Future / Evaluation:

- Genie integration;
- future providers.

==================================================
12. PHASE 2F-SPECIFIC IMPACT REVIEW
==================================================

Because development is currently in Phase 2F, specifically inspect:

- output-template contracts;
- dynamic suggestion contracts;
- template storage;
- template versioning;
- registry references;
- KPI / Recipe references;
- response-format routing;
- deterministic formatter behavior;
- AI formatter behavior if already planned;
- response regression tests;
- suggestion provenance;
- audit evidence;
- any cache assumptions embedded in 2F;
- documentation describing the response pipeline.

Verify that:

1. Templates reference Registry objects instead of redefining business semantics.
2. Template and suggestion outputs can be tied to registry_version.
3. Formatting-path selection is deterministic.
4. AI-assisted formatting is optional and isolated behind an explicit contract.
5. The future Early Cache can use template ID / normalized intent without needing
   semantic_plan_hash.
6. Phase 2F does not hard-code a specific data provider or cache technology.

==================================================
13. FUTURE PHASE IMPACT
==================================================

Review Phase 2G and later planned work for compatibility.

In particular, future publish/validation/rollback workflow should version and
validate:

- template definitions;
- registry references;
- recipe references;
- formatting policies;
- cache compatibility/invalidation metadata where applicable.

Publishing a changed template must not silently redefine a KPI or business term.

Semantic changes belong in the Semantic Registry lifecycle.

Template changes belong in the template/output lifecycle.

==================================================
14. DO NOT DO THESE THINGS
==================================================

Do NOT:

- restart completed phases;
- build permission synchronization;
- hard-code Redis;
- hard-code Unity Catalog;
- hard-code SQL Warehouse;
- implement Genie now;
- duplicate business semantics in templates;
- make templates self-modify in production;
- allow AI formatting to change analytical meaning;
- send unrestricted query results to Azure OpenAI;
- treat planned capabilities as current.

==================================================
15. REQUIRED OUTPUT BEFORE BROAD CHANGES
==================================================

First produce:

ARCHITECTURE_DELTA_IMPACT_REPORT.md

Include:

1. Summary of each architecture delta above.
2. Whether the current implementation already complies.
3. Exact Phase 2F files/contracts/tests affected.
4. Any earlier-phase compatibility issue discovered.
5. Phase 2G+ plan changes required.
6. Documentation changes required.
7. Tests to add/update.
8. Items that are documentation-only.
9. Items that are future-only.
10. Open questions requiring architecture confirmation.

Then provide a recommended implementation sequence.

Do not make broad cross-phase code changes until the impact report clearly
demonstrates they are necessary.

If a small, local, low-risk Phase 2F correction is obviously required and can be
safely implemented without changing accepted phase behavior, you may propose it
separately after the impact report.
