We are performing a BOUNDED REMEDIATION of the existing AskTD / KMAI
Phase 2D Approved Recipe Pilot stacked candidate.

The first independent review verdict was:

PHASE_2D_INDEPENDENT_REVIEW_FAIL

All validation and regression gates were green, but the reviewer identified
two Phase-2D-attributable HIGH findings that block acceptance.

This task must remediate only those findings and directly related
contract/test issues.

Do NOT redesign the application.

Do NOT commit.
Do NOT push.
Do NOT create or edit a PR.
Do NOT merge.
Do NOT deploy.
Do NOT modify PR #15.
Do NOT modify main.
Do NOT start another roadmap phase.

==================================================
1. TARGET
==================================================

Repository:

TD-Enterprise/kmai-td-genie

Phase 2D branch:

phase2/approved-recipe-pilot

Expected worktree:

/tmp/asktd-phase2d-approved-recipe-pilot

Stack base:

phase2/provider-abstraction-foundation

Expected accepted PR #15 SHA:

d5472ae31081879329c224922244d87962737e8c

First verify:

- the Phase 2D worktree is the same candidate that was independently reviewed;
- it is based directly on the accepted PR #15 HEAD;
- PR #15 is unchanged;
- main is unchanged;
- no Phase 2D commit or remote branch has appeared.

If the base or candidate changed unexpectedly, STOP and report:

PHASE_2D_REMEDIATION_CANDIDATE_CHANGED

==================================================
2. READ THE REVIEW EVIDENCE COMPLETELY
==================================================

Read completely:

/tmp/ASKTD_PHASE_2D_INDEPENDENT_REVIEW_2026-08-22.md

Also read:

/tmp/ASKTD_PHASE_2D_STACKED_IMPLEMENTATION_2026-08-22.md

Use the independent-review report as the authoritative source for the
remediation findings.

Before editing, reproduce and report the exact code path for both HIGH
findings.

==================================================
3. FINDINGS TO REMEDIATE
==================================================

The independent reviewer found:

HIGH 1:

The governed Approved Recipe gate runs after an adapter/schema operation.
Therefore a validation failure does not guarantee zero data-source activity.

HIGH 2:

ApprovedRecipe.builder_key does not authoritatively determine the SQL builder.
The legacy path builds SQL before governed recipe validation.

Related issues:

- some ApprovedRecipe fields may exist without a real production consumer;
- independently allowed source_code and source_label values may permit an
  invalid combination;
- tests do not fully prove zero adapter/schema/builder calls on every governed
  denial;
- tests do not prove that builder_key controls the SQL actually executed.

==================================================
4. REQUIRED FINAL ORDERING
==================================================

The final pilot ordering must be:

1. existing coarse deny_all authorization gate;
2. deterministic legacy selector produces a candidate recipe_id;
3. exact ApprovedRecipe lookup;
4. recipe lifecycle validation;
5. parameter presence/type/domain validation;
6. cross-parameter pair validation;
7. current governed RegistrySnapshot resolution;
8. dataset-scoped GovernedSemanticPlan construction;
9. deterministic governed-plan validation;
10. builder resolution from ApprovedRecipe.builder_key;
11. SQL construction using only the resolved builder and validated parameters;
12. data-source adapter construction/access;
13. existing SQL read-only and object-authorization controls;
14. execution and current result handling.

The following must NOT occur before Steps 3–9 pass:

- DataSourceAdapter construction;
- DataSourceAdapter method call;
- database/schema probe;
- has_dataset/schema lookup through the data source;
- SQL builder call;
- SQL string construction;
- SQL authorization/execution.

MetadataRegistryService and its in-process governed RegistrySnapshot service
are not considered a data-source adapter and may be used for governance
validation before SQL construction.

==================================================
5. MOVE GOVERNED EVALUATION EARLIER
==================================================

Inspect the current Orchestrator route from deterministic selection through:

- parameter/source resolution;
- data-source creation;
- schema resolution;
- SQL construction;
- approved-recipe evaluation;
- execution.

Move the Approved Recipe evaluation to the earliest safe point after:

- recipe_id is known;
- raw recipe parameters are available;

but before:

- self._data_source(...);
- any data-source factory;
- schema probes;
- SQL construction.

Do not move existing object-level authorization into the recipe selector.

Selection remains distinct from authorization.

The existing execution-level authorization controls must still run after the
authoritative SQL is built.

Do not broadly restructure Orchestrator.

Use the smallest helper extraction necessary to make ordering explicit and
testable.

==================================================
6. MAKE builder_key AUTHORITATIVE
==================================================

ApprovedRecipe.builder_key must control the SQL builder that is actually used.

Implement a small static allow-listed builder registry/resolver.

Conceptual example only:

APPROVED_RECIPE_BUILDERS = {
    "source_balance_mom_change_sql":
        query_recipes.source_balance_mom_change_sql,
}

Do not use:

- dynamic imports;
- getattr over arbitrary user-controlled strings;
- plugin discovery;
- configuration-provided callables;
- LLM-selected builders;
- reflection-based execution.

After lifecycle, parameter, and governed-plan validation pass:

1. resolve the builder exclusively from recipe.builder_key;
2. fail closed if the builder key is unknown;
3. call that resolved builder with only validated parameters;
4. pass its result into the existing SQL policy/authorization/execution path.

Remove any duplicate direct legacy builder invocation for the pilot path.

There must be one authoritative builder invocation.

==================================================
7. CONTRACT FIELD AUDIT
==================================================

Audit every field in:

ApprovedRecipe

and:

RecipeParameter

For every field identify its real production consumer.

Each field must be one of:

- actively consumed by production behavior;
- actively written into required trace/audit evidence;
- removed from the bounded pilot contract.

Do not preserve unused fields merely because discovery proposed them.

In particular inspect whether fields such as:

- intent_id;
- renderer;
- any descriptive/output field;

are genuinely consumed.

Do not add speculative consumers simply to justify a field.

Prefer removing a field that has no bounded pilot purpose.

Update ADR 0004 and tests to match the actual minimal final contract.

==================================================
8. VALIDATE SOURCE CODE/LABEL AS A PAIR
==================================================

The pilot must not validate source_code and source_label independently when
only specific pairs are governed.

Define one explicit deterministic declared domain for valid combinations.

Based on current repository evidence, preserve only the intended pairs, such
as:

IMSB -> Deposits
STAX -> Savings

Use the exact current business values found in repository code/tests.

Do not trust this prompt if actual values differ.

Validation must reject:

- unknown source_code;
- unknown source_label;
- valid code with the wrong label;
- valid label with the wrong code;
- missing code;
- missing label;
- undeclared additional parameters;
- injection-like values.

Pair validation must happen before builder resolution and before any adapter
activity.

==================================================
9. ZERO-SIDE-EFFECT DENIAL CONTRACT
==================================================

For every Approved Recipe governance failure, guarantee:

- data-source factory calls: 0;
- adapter constructions: 0;
- adapter method calls: 0;
- schema probes: 0;
- builder calls: 0;
- SQL executions: 0.

At minimum cover:

- unknown recipe ID;
- recipe lifecycle not approved/published;
- missing parameter;
- wrong parameter type;
- out-of-domain value;
- invalid source_code/source_label pair;
- unknown builder_key;
- unknown governed dataset;
- strict metadata unavailable;
- governed-plan validation failure.

The existing coarse deny_all behavior must also remain before data access.

==================================================
10. AUTHORITATIVE BUILDER TESTS
==================================================

Add strong tests proving builder_key is not decorative metadata.

Tests must prove:

1. the resolved allow-listed builder is called;
2. an unrelated/legacy direct builder is not called;
3. the exact SQL passed to the execution boundary comes from the resolved
   builder;
4. an unknown builder_key fails closed;
5. validation failure occurs before any builder invocation;
6. a recipe cannot select an arbitrary callable or module.

A useful test may install a sentinel allowed builder and make the former direct
legacy builder raise if invoked.

Do not overmock the Orchestrator behavior under test.

==================================================
11. ADAPTER / SCHEMA-PROBE TESTS
==================================================

Add tests using the real supported dependency-injection seam.

For denial cases, configure the data-source factory to:

- record every invocation; or
- raise immediately if called.

Prove the governed validation failure completes through the expected safe
response without invoking that factory.

If schema resolution is currently hidden inside a helper, instrument the
actual helper or fake adapter method so the test proves:

schema probes == 0

Do not claim zero adapter activity merely because execute_query was not called.

==================================================
12. PRESERVE AUTHORIZATION
==================================================

Do not add a new authorization system.

Preserve:

- EffectivePermissions;
- deny_all;
- SqlPolicy;
- SqlAuthorizationGuard;
- current auth-bound DataSourceAdapter;
- current object-level authorization order for valid governed recipes.

For an approved and governance-valid recipe that references an unauthorized
physical object:

- existing object authorization must still block;
- no rows are returned;
- current audited blocked-path behavior remains reachable.

Do not convert an authorization failure into “recipe not found” or generic
governance failure.

==================================================
13. PRE-EXISTING OBJECT-NAME DISCLOSURE
==================================================

The independent reviewer classified the unauthorized physical-object-name
disclosure as:

MEDIUM
PRE-EXISTING
SEPARATE REMEDIATION

Do not fix it inside this bounded Phase 2D remediation unless the current
Phase 2D diff introduced or expanded the disclosure.

Record it in the remediation report as a separate security follow-up.

Do not weaken or hide tests merely to avoid observing it.

==================================================
14. ADR AND DOCUMENTATION
==================================================

Update ADR 0004 only as needed to describe the corrected architecture:

- governed validation occurs before adapter construction/schema probing/SQL
  construction;
- builder_key is authoritative through a static allow-listed resolver;
- invalid recipe/governance/parameter states have zero adapter and zero builder
  activity;
- pair-level parameter validation;
- final minimal contract fields;
- existing authorization remains a later independent execution control.

Do not modify ADR 0003 or PR #15.

The missing ADR 0003 index row remains an inherited PR #15/documentation issue
to reconcile after integration unless repository policy proves it blocks the
Phase 2D candidate.

==================================================
15. SCOPE LIMIT
==================================================

Do NOT implement:

- Databricks;
- Unity Catalog;
- Collibra;
- Genie;
- Redis;
- Event Hubs;
- graph or GraphRAG;
- reporting templates;
- KPI/glossary;
- cross-source execution;
- fine-grained authorization;
- recipe-management UI;
- generalized recipe lifecycle platform;
- dynamic builder plugins;
- SQL dialect abstraction;
- frontend;
- deployment/infrastructure;
- broad Orchestrator redesign;
- migration of other recipes;
- changes to PR #15 or main.

==================================================
16. FOCUSED TESTS FIRST
==================================================

Run focused tests for:

- ApprovedRecipe/RecipeParameter contract;
- pair validation;
- builder resolver;
- builder authority;
- zero adapter calls;
- zero schema probes;
- zero builder calls on denial;
- flag OFF behavior;
- flag ON successful pilot;
- existing authorization denial.

Inspect the assertions, not only the test count.

==================================================
17. FULL VALIDATION
==================================================

After focused tests pass, run:

1. all Approved Recipe tests;
2. Phase 2A/2B/2C regressions;
3. Phase 2C.5 provider-abstraction regressions;
4. MetadataRegistryService tests;
5. authorization tests;
6. SQL policy/store tests;
7. semantic-model/query-recipe tests;
8. golden baseline;
9. full backend suite with configured coverage;
10. git diff --check;
11. excluded-technology scan.

Historical pre-remediation results:

- focused: 107 passed;
- selected regression: 405 passed;
- full backend: 945 passed, 3 skipped;
- coverage: 86.72%.

Counts may legitimately increase because new tests are required.

Do not force exact historical counts.

Do not regenerate baselines.

Do not install or upgrade dependencies.

==================================================
18. FINAL CODE-PATH AUDIT
==================================================

Before finishing, explicitly report the exact final order for the pilot route.

Answer:

- Is data-source factory called before governed validation? Yes/No
- Is any adapter method called before governed validation? Yes/No
- Is any schema probe performed before governed validation? Yes/No
- Is any SQL builder called before governed validation? Yes/No
- Is SQL constructed before governed validation? Yes/No
- Does recipe.builder_key select the actual executed builder? Yes/No
- Can an unknown builder_key execute anything? Yes/No
- Can an invalid source_code/source_label pair execute anything? Yes/No
- Do existing authorization controls still run for a valid recipe? Yes/No

Required successful answers:

No
No
No
No
No
Yes
No
No
Yes

==================================================
19. DIFF AUDIT
==================================================

Inspect the complete diff against the accepted PR #15 HEAD.

Classify every changed file.

Confirm:

- only bounded Phase 2D remediation entered the candidate;
- no PR #15 files were modified outside inherited base content;
- no unrelated security cleanup entered;
- no excluded technology entered;
- no broad refactor entered.

==================================================
20. FINAL VERDICT
==================================================

Return exactly one:

PHASE_2D_REMEDIATION_READY_FOR_RE_REVIEW

or

PHASE_2D_REMEDIATION_HAS_BLOCKERS

or

PHASE_2D_REMEDIATION_INSUFFICIENT_EVIDENCE

READY requires:

- governed validation before all adapter/schema/SQL-building activity;
- builder_key authoritatively selects executed SQL builder;
- unused contract fields removed or genuinely consumed;
- source code/label pairs validated together;
- zero-side-effect denial tests pass;
- existing authorization preserved;
- regressions, coverage, golden, diff, and scope gates pass;
- PR #15 and main remain unchanged;
- no commit/push/PR created.

==================================================
21. REPORT
==================================================

Save outside the worktree:

/tmp/ASKTD_PHASE_2D_REMEDIATION_2026-08-22.md

Required sections:

1. Candidate / Stack Evidence
2. Independent Review Findings Reproduced
3. Root Cause
4. Corrected Execution Ordering
5. Authoritative Builder Resolution
6. Contract Field Audit
7. Pair-Level Parameter Validation
8. Zero-Side-Effect Denial Evidence
9. Authorization Preservation
10. ADR Update
11. Focused Test Results
12. Full Regression / Coverage / Golden Results
13. Exact Diff Inventory
14. Scope Audit
15. Deferred Security Finding
16. Final Code-Path Audit
17. Remaining Findings
18. Final Verdict
19. Recommended Next Action

At completion explicitly state:

- Repository files modified by remediation: list
- PR #15 changed: No
- main changed: No
- Commit created: No
- Branch pushed: No
- Phase 2D PR created: No
- Phase 2D formally accepted: No

Then STOP.
