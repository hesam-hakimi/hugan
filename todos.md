We are continuing the AskTD / askAlpha / KMAI project.

Current state:

- Program Phase 2C is formally closed.
- Phase 2C.5 Provider Abstraction Foundation has passed independent technical review.
- PR #15 exists for:
  branch: phase2/provider-abstraction-foundation
  base: main
- PR #15 is not yet approved/merged.
- Therefore Phase 2D must NOT formally start yet.

This task is:

PHASE 2D DISCOVERY / READINESS ONLY

Do not modify repository files.
Do not commit.
Do not push.
Do not create or edit a PR.
Do not merge.
Do not deploy.
Do not start Phase 2D implementation.

==================================================
1. TARGET REPOSITORY
==================================================

Repository:
TD-Enterprise/kmai-td-genie

Use current `origin/main` as the repository baseline.

Also inspect the Phase 2C.5 branch if needed only to understand the provider-abstraction seam:

phase2/provider-abstraction-foundation

Do not modify either branch.

==================================================
2. OBJECTIVE
==================================================

Determine the exact smallest, safest implementation scope for:

PROGRAM PHASE 2D
Approved Recipe Pilot

The goal is NOT to design a new architecture.

The goal is to discover how Phase 2D should attach to the architecture already implemented through:

- Phase 2A
- Phase 2B
- Phase 2C
- Phase 2C.5

We need repository-backed evidence before any implementation prompt is written.

==================================================
3. ARCHITECTURE CONSTRAINTS
==================================================

Preserve these decisions:

1. AskTD remains provider-agnostic.

2. Do not implement:
   - Databricks
   - Unity Catalog
   - Collibra
   - Genie
   - Redis
   - Event Hubs
   - cross-source execution
   - fine-grained authorization

3. Existing seams must be reused, not duplicated:

Execution:
- existing DatabaseTool abstraction

Data source:
- Phase 2C.5 DataSourceAdapter seam

Governance / semantic metadata:
- MetadataRegistryService
- RegistrySnapshot
- Governed Semantic Plan
- deterministic validation

Authorization:
- EffectivePermissions
- current fail-closed entity-level authorization

4. Do not redesign Orchestrator broadly.

5. Phase 2D must be a bounded Approved Recipe Pilot, not a complete enterprise recipe platform.

==================================================
4. FIRST DISCOVERY: CURRENT RECIPE IMPLEMENTATION
==================================================

Find every current recipe-related implementation.

Search for terms including:

- recipe
- recipes
- query_recipe
- approved_recipe
- semantic recipe
- SQL recipe
- report recipe
- intent recipe
- query template
- query plan
- semantic plan

For each relevant file/symbol report:

- file path;
- symbol;
- current purpose;
- whether it is production code, test code, legacy code, or unused;
- whether it contains hard-coded SQL;
- whether it is coupled to SQL Server / T-SQL;
- whether it is currently used by Orchestrator/planner/query generation;
- whether it already behaves like an approved recipe.

Do not infer usage from names alone.
Trace actual call paths.

==================================================
5. TRACE THE CURRENT QUERY PATH
==================================================

Trace the actual current runtime flow from user question to SQL/data execution.

At minimum identify:

User Question
→ intent/routing
→ authorization
→ metadata discovery
→ semantic planning
→ SQL/query generation
→ execution
→ result handling

For every stage identify:

- file;
- class/function;
- inputs;
- outputs;
- current boundary.

Answer specifically:

1. Where is `GovernedSemanticPlan` created today?
2. Where is it validated?
3. Is it actually consumed by the current SQL/query-generation path?
4. If not, where does the current runtime bypass it?
5. What is the smallest seam where an Approved Recipe decision can safely be inserted?

==================================================
6. TWO METADATA WORLDS CHECK
==================================================

Earlier discovery reported a possible issue:

the planner/runtime may still use legacy semantic metadata while the governed registry / semantic-plan model exists separately.

Verify this against current `origin/main`.

Report exactly:

- whether two metadata worlds still exist;
- files/symbols for each;
- whether this is an actual blocker for a bounded Phase 2D pilot;
- whether Phase 2D should bridge them;
- or whether bridging belongs to a later phase.

Do NOT solve it in this task.

==================================================
7. DEFINE “APPROVED RECIPE” FROM CURRENT CODE
==================================================

Based on existing repository architecture, determine the minimum viable contract for one Approved Recipe.

Do not invent a large platform.

Evaluate whether the pilot contract needs only fields such as:

- recipe_id
- version
- intent / use_case
- governed dataset refs
- required field refs
- allowed relationship refs
- required filters/parameters
- parameter schema
- deterministic SQL/query template or builder reference
- output shape
- lifecycle / enabled status

Only recommend fields that are justified by current runtime needs.

For each recommended field provide:

- why required;
- which current component consumes it;
- whether it is mandatory for the pilot or future-only.

==================================================
8. RECIPE STORAGE / REGISTRY LOCATION
==================================================

Determine where the pilot recipe should logically live.

Evaluate current repository options only.

Examples to inspect:

- canonical registry snapshot;
- separate recipe registry;
- existing query_recipes module;
- configuration/static files;
- existing metadata service.

Do not choose based on preference.

For each viable option report:

- benefits;
- coupling;
- versioning implications;
- compatibility with `registry_version`;
- whether recipe content should participate in governed snapshot identity;
- minimum change surface.

Recommend ONE smallest option for the pilot.

==================================================
9. RECIPE SELECTION
==================================================

Determine how one approved recipe should be selected.

Evaluate repository-backed options such as:

- intent match;
- deterministic recipe ID;
- planner-selected recipe;
- registry lookup from semantic plan;
- explicit pilot routing.

The LLM must not be allowed to invent an ungoverned recipe.

For the pilot, identify the smallest deterministic selection mechanism.

Report:

- selector input;
- selector output;
- failure behavior;
- authorization interaction;
- semantic-plan interaction.

Fail-closed behavior is required.

==================================================
10. VALIDATION CONTRACT
==================================================

Determine which deterministic checks must occur before recipe execution.

At minimum evaluate:

- recipe exists;
- recipe enabled/approved;
- registry version compatibility;
- dataset refs exist;
- field refs exist;
- relationships exist;
- selected datasets are authorized;
- recipe scope does not exceed GovernedSemanticPlan;
- required parameters exist;
- parameter types are valid;
- no undeclared dataset/field appears;
- resulting execution remains read-only/bounded.

Identify which checks already exist in Phase 2C validators and should be reused.

Do not duplicate validators unnecessarily.

==================================================
11. SQL / EXECUTION BOUNDARY
==================================================

Determine how the pilot recipe should reach execution without breaking provider abstraction.

Specifically inspect:

- DatabaseTool
- DataSourceAdapter
- current query generation
- SqlDataStore
- existing SQL policy/guardrails

Answer:

1. Should the recipe produce SQL directly in the pilot?
2. Or should it produce an intermediate execution specification?
3. What is the minimum option that preserves current behavior and does not prematurely implement multi-provider SQL dialect support?

Do not implement a Databricks dialect abstraction.

If current pilot can safely remain SQL-server-backed behind existing abstractions, say so explicitly.

==================================================
12. AUTHORIZATION
==================================================

Verify Phase 2D pilot can remain within current authorization model.

Current working model:

Entra user
→ EffectivePermissions
→ allowed entities
→ restricted metadata
→ semantic plan
→ execution

Report:

- where recipe selection must be constrained by authorization;
- whether any new authorization model is required;
- whether dataset-level/entity-level scope is sufficient for the pilot.

Fine-grained column/row authorization must not be added unless current code proves it is already required.

==================================================
13. PILOT USE CASE
==================================================

Find the smallest realistic existing query/use case in the repository that could be converted into the first Approved Recipe pilot.

Prefer a use case that:

- already has deterministic SQL/query logic;
- uses a small number of datasets;
- has known parameters;
- does not require cross-source joins;
- does not require Databricks;
- does not require new authorization;
- has existing tests or golden outputs.

Give up to 3 candidates.

For each report:

- current implementation location;
- complexity;
- dependencies;
- testability;
- risk.

Recommend ONE.

==================================================
14. TEST STRATEGY
==================================================

Identify the minimum test layers Phase 2D implementation will require.

At minimum consider:

- recipe contract tests;
- recipe registry/version tests;
- deterministic recipe selection tests;
- authorization negative tests;
- semantic-plan compatibility tests;
- invalid parameter tests;
- execution boundary tests;
- existing regression/golden tests.

Identify exact existing test files that can be extended.

Avoid creating redundant parallel test frameworks.

==================================================
15. EXACT MINIMUM IMPLEMENTATION SURFACE
==================================================

Produce a proposed Phase 2D pilot change inventory.

For each file classify:

- EXISTING_FILE_TO_MODIFY
- NEW_FILE_REQUIRED
- TEST_ONLY
- ADR/DOC

For each proposed file explain the exact change in one sentence.

Do not write code.

Do not include future enterprise features.

==================================================
16. BLOCKERS VS NON-BLOCKERS
==================================================

Separate:

CORE DEVELOPMENT BLOCKERS
INTEGRATION BLOCKERS
PRODUCTION BLOCKERS
NON-BLOCKING OPEN DECISIONS

For every unresolved item state:

- assumption;
- why it matters;
- evidence;
- who should confirm;
- whether it blocks Phase 2D pilot implementation.

Do not turn Databricks/SpruceX/DAC/Genie decisions into Core blockers unless code evidence genuinely requires them.

==================================================
17. READINESS VERDICT
==================================================

Return exactly one:

PHASE_2D_DISCOVERY_READY_FOR_BOUNDED_IMPLEMENTATION

or

PHASE_2D_DISCOVERY_BLOCKED

or

PHASE_2D_DISCOVERY_INSUFFICIENT_EVIDENCE

PASS/ready requires that you can identify:

- exact insertion seam;
- minimal Approved Recipe contract;
- deterministic selection mechanism;
- validation path;
- execution path;
- first pilot use case;
- bounded file list;
- test strategy.

Do not implement anything.

==================================================
18. REPORT
==================================================

Save the report outside the worktree:

/tmp/ASKTD_PHASE_2D_DISCOVERY_2026-08-22.md

Required sections:

1. Repository Evidence
2. Current Runtime Query Path
3. Existing Recipe Inventory
4. Governed Semantic Plan Integration Status
5. Metadata World Gap Analysis
6. Proposed Minimal Approved Recipe Contract
7. Recipe Storage / Versioning Recommendation
8. Deterministic Recipe Selection
9. Validation Reuse
10. Execution Boundary
11. Authorization Interaction
12. Pilot Candidate Comparison
13. Recommended Pilot
14. Test Strategy
15. Minimum File Change Surface
16. Blockers / Open Decisions
17. Phase 2D Readiness Verdict
18. Recommended Implementation Sequence

At completion explicitly state:

Repository files modified: No
Git state changed: No
Commit created: No
Branch pushed: No
PR created: No
Phase 2D implementation started: No

Then STOP.
