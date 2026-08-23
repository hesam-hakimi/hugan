We are continuing the AskTD / KMAI roadmap after Phase 2D.

This task is DISCOVERY + READINESS ONLY for Phase 2E.

DO NOT implement Phase 2E yet.
DO NOT modify production code.
DO NOT create commits.
DO NOT push branches.
DO NOT create a PR.
DO NOT merge anything.
DO NOT modify PR #15 or PR #16.
DO NOT use /tmp or create a detached worktree outside the main VS Code workspace.

IMPORTANT WORKSPACE RULE

Work only inside the currently opened repository workspace.

Do not create another Git worktree under /tmp, /var/tmp, home, or any other external path.

The purpose is to avoid repeated Copilot approval prompts for filesystem access.

If branch isolation is needed for later implementation, recommend the exact branch strategy in the report, but do not create it during this discovery task.

==================================================
CURRENT VERIFIED STATE
==================================================

Repository:
TD-Enterprise/kmai-td-genie

Phase 2C.5:
PR #15
Base: main
Head: phase2/provider-abstraction-foundation
Status: open / draft / not merged
Reviewed candidate commit:
d5472ae31081879329c224922244d87962737e8c

Phase 2D:
PR #16
Base: phase2/provider-abstraction-foundation
Head: phase2/approved-recipe-pilot
Status: draft

Phase 2D implementation has passed independent review.

Relevant validation evidence:
- Full backend: 962 passed, 3 skipped
- Coverage: ~86.75%
- Golden baseline passed
- Phase 2D independent review: PASS
- Candidate was verified byte-identical before finalization
- main was not changed
- PR #15 was not changed

Phase 2D introduced the bounded Approved Recipe pilot.

The Phase 2D implementation includes, among other things:
- ApprovedRecipe contract
- deterministic approved-recipe lookup
- recipe lifecycle gate
- parameter validation
- governed dataset references
- governed semantic-plan validation
- builder_key as authoritative builder selector
- governed validation before adapter/schema-probe/builder/SQL activity
- fail-closed behavior
- existing authorization preserved
- feature flag / rollback path
- source_balance_mom_change pilot recipe

Do not assume this summary is sufficient.
Inspect the actual repository and PR branches.

==================================================
FIRST: VERIFY LIVE REPOSITORY STATE
==================================================

Before architecture analysis, verify:

1. current workspace path
2. current checked-out branch
3. git status
4. origin/main SHA
5. PR #15 branch SHA
6. PR #16 branch SHA
7. whether either PR has changed since the recorded evidence
8. exact relationship:

main
  -> phase2/provider-abstraction-foundation
      -> phase2/approved-recipe-pilot

9. changed-file inventory for PR #15
10. changed-file inventory for PR #16
11. whether Phase 2D files are present only on PR #16 or anywhere else
12. workflow/check status for both PRs
13. whether PR #16 still intentionally receives no CI because its base is a stacked feature branch

If the live state differs materially from the recorded state, STOP implementation planning and clearly explain the drift.

Do not mutate anything while verifying.

==================================================
SECOND: READ THE EXISTING ARCHITECTURE
==================================================

Inspect the current implementation and roadmap-related code/docs needed to understand what Phase 2E should be.

At minimum inspect the current implementations of:

- orchestration/runtime flow
- Approved Recipe package
- semantic models
- GovernedSemanticPlan
- RegistrySnapshot
- MetadataRegistryService
- registry/version handling
- authorization / EffectivePermissions
- SQL policy / read-only enforcement
- DataSourceAdapter / provider abstraction
- query recipe builders
- answer renderers
- report generation
- visualization/chart generation
- model/agent workflow
- current cache usage
- Redis support if present
- any graph / relationship / semantic-network implementation
- configuration and feature flags
- audit / tracing
- golden baseline tests
- architecture ADRs
- roadmap/status documentation currently available in the repository

Do not redesign the system from scratch.

==================================================
THIRD: RECONSTRUCT THE PHASE 2E PURPOSE
==================================================

Determine from evidence what the smallest useful Phase 2E should be.

The Phase 2E analysis MUST explicitly examine these roadmap areas:

A. Approved Recipe evolution
B. metadata/semantic governance integration
C. keeping recipes valid when datasets/metadata evolve
D. field-level and relationship-level governed references
E. recipe versioning and lifecycle
F. richer answer-generation workflow
G. reusable report / presentation templates
H. graph / semantic relationship layer
I. caching strategy
J. Redis role
K. provider abstraction continuation
L. Databricks / Genie coexistence boundaries
M. future cross-source capability
N. observability / audit
O. self-service onboarding

Do NOT assume all of these belong in Phase 2E.

Classify each item as:

- Phase 2E
- Phase 2F
- Later
- Existing / already implemented
- Separate infrastructure track
- Separate UX/reporting track
- Needs architecture decision

Explain why.

==================================================
IMPORTANT QUESTION: RECIPE EVOLUTION
==================================================

We specifically need an architecture answer for this:

"What happens when a governed dataset changes after an Approved Recipe has been created?"

Investigate and design the intended lifecycle.

Evaluate scenarios such as:

- dataset gains a column
- dataset loses a column
- column renamed
- datatype changed
- relationship changed
- business definition changed
- source physical object changes but logical governed dataset stays stable
- recipe parameter domain changes
- builder implementation changes
- registry version changes for an unrelated dataset
- dataset is deprecated
- recipe is superseded

Determine whether recipes should be:

- dynamically validated against the latest governed snapshot,
- pinned to logical metadata versions,
- pinned only to specific referenced entities,
- dependency-aware,
- automatically marked stale,
- automatically revalidated,
- manually re-approved,
- or some combination.

Avoid a design where every unrelated registry change invalidates every recipe.

Propose a practical dependency-aware model.

==================================================
IMPORTANT QUESTION: GRAPH
==================================================

Investigate what "graph" should mean in AskTD.

Distinguish between:

1. metadata relationship graph
2. dataset relationship graph
3. business semantic graph
4. execution/query plan graph
5. lineage graph

Identify which one is useful first.

Explain whether the graph should initially be:

- persisted,
- computed from registry metadata,
- represented in relational tables,
- represented in JSON,
- stored in a graph database,
- or deferred.

Do not introduce a graph database unless evidence justifies it.

==================================================
IMPORTANT QUESTION: BETTER ANSWERS + REPORT TEMPLATES
==================================================

Determine where roadmap work belongs for:

- better multi-step reasoning
- improved question clarification
- stronger agent workflow
- executive summaries
- richer tables
- formatted analytical answers
- reusable report templates
- beautiful visual layouts
- chart/report composition
- downloadable reports

Separate:

1. reasoning/orchestration improvement
2. semantic correctness
3. visualization
4. report-template system
5. frontend presentation

Propose likely phases for each.

==================================================
IMPORTANT QUESTION: CACHE / REDIS
==================================================

Audit current caching.

Answer:

1. Is Redis currently implemented, optional, planned, or unused?
2. What is currently cached?
3. What should be cached?
4. What must never be cached without authorization scope?
5. Should cache keys include:
   - user/effective scope
   - registry version
   - recipe version
   - dataset refs
   - query parameters
6. Which cache belongs in-process vs Redis?
7. Should Redis be introduced now or later?
8. What invalidates cached entries?

Do not propose Redis merely because it exists in the architecture roadmap.

==================================================
FOURTH: DEFINE PHASE 2E OPTIONS
==================================================

Produce at least three realistic Phase 2E options:

Option A — smallest bounded next slice

Option B — medium governance expansion

Option C — larger semantic foundation

For each include:

- objective
- user/business value
- architecture value
- exact dependencies
- approximate file-change surface
- migration risk
- test scope
- rollback strategy
- whether PR #15 must merge first
- whether PR #16 must merge first
- whether it can safely be stacked
- expected follow-on phase

Then recommend ONE option.

Prefer the smallest slice that creates a durable architectural improvement.

==================================================
FIFTH: BRANCH / PR STRATEGY
==================================================

We currently have stacked PRs.

Recommend the safest continuation strategy.

Consider:

main
 -> PR #15 / Phase 2C.5
    -> PR #16 / Phase 2D
       -> possible Phase 2E branch

Answer:

- Can Phase 2E safely stack on PR #16?
- What risks arise if #15 later changes?
- What risks arise if #16 later changes?
- When should rebase happen?
- Should Phase 2E implementation wait for both merges?
- If implementation must continue before approvals, what exact branch structure should be used?

For future implementation, prefer creating the branch directly inside the normal repository workspace rather than using /tmp worktrees.

Do not create the branch during this discovery.

==================================================
SIXTH: ROADMAP RECONSTRUCTION
==================================================

Build a management-friendly roadmap from current state through the enterprise target.

Use simple language.

Include approximately:

Current foundation
Phase 2D
Phase 2E
Phase 2F
Phase 3
Phase 4
Phase 5 / enterprise maturity

Do not force these names if repository evidence supports different sequencing.

For each phase show:

- What capability the user gets
- What technical foundation is added
- Why it matters
- Major dependencies

Make sure the roadmap explicitly places:

- Approved Recipes
- recipe maintenance/versioning
- metadata governance
- field/relationship semantics
- better agent reasoning
- report templates
- charts/visualization
- graph capabilities
- caching / Redis
- Databricks provider
- Genie integration/coexistence
- cross-source support
- observability
- self-service onboarding

==================================================
SEVENTH: PRODUCE THE DISCOVERY REPORT
==================================================

Create ONE markdown report inside the current workspace, preferably under an existing docs/plans or docs/architecture location.

Do not use /tmp.

Suggested name:

ASKTD_PHASE_2E_DISCOVERY_AND_ROADMAP_2026-08-23.md

The report must contain:

1. Executive summary
2. Live repository / PR state
3. Current architecture baseline
4. What Phase 2D established
5. Remaining architecture gaps
6. Recipe evolution / stale-detection design
7. Metadata + relationship graph analysis
8. Better-answer / reporting / visualization roadmap
9. Cache / Redis analysis
10. Provider / Databricks / Genie boundary
11. Phase 2E option A
12. Phase 2E option B
13. Phase 2E option C
14. Recommended Phase 2E
15. Exact bounded implementation surface
16. Tests required
17. Branch / stacked PR strategy
18. Rollback strategy
19. Dependencies / blockers
20. Management roadmap
21. Explicit out-of-scope items
22. Recommended next action

==================================================
FINAL RESPONSE
==================================================

At the end, report:

PHASE_2E_DISCOVERY_COMPLETE

Then provide:

- recommended Phase 2E name
- one-sentence objective
- approximate number of source files to modify
- approximate number of new source files
- approximate test files
- PR dependency recommendation
- whether Phase 2E can safely start before PR #15/#16 merge
- report path

And explicitly state:

Repository files modified:
Git state changed:
Commit created:
Branch created:
Branch pushed:
PR created:
Phase 2E implementation started:

For this discovery task, all should be NO except the single discovery/report document if documentation creation is permitted.

Do not begin implementation.
