We are performing the FINAL INDEPENDENT READ-ONLY REVIEW of the AskTD /
KMAI Phase 2D Approved Recipe Pilot stacked candidate.

The implementation was produced in a separate implementation session.

Implementation verdict:

PHASE_2D_STACKED_CANDIDATE_READY_FOR_INDEPENDENT_REVIEW

This review is strictly READ-ONLY.

Do not modify files.
Do not fix findings.
Do not commit.
Do not push.
Do not create or edit a PR.
Do not merge.
Do not deploy.
Do not change PR #15.
Do not start any additional roadmap phase.

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

Expected accepted PR #15 base SHA:

d5472ae31081879329c224922244d87962737e8c

Do not trust the SHA blindly.

Verify the current local and remote evidence.

PR #15 must remain byte-for-byte unchanged.

==================================================
2. READ IMPLEMENTATION REPORT
==================================================

Read completely:

/tmp/ASKTD_PHASE_2D_STACKED_IMPLEMENTATION_2026-08-22.md

Also read the Phase 2D discovery report:

/tmp/ASKTD_PHASE_2D_DISCOVERY_2026-08-22.md

Use the discovery only as expected design evidence.

Verify the actual implementation independently.

==================================================
3. REPOSITORY AND CANDIDATE IDENTITY
==================================================

Report:

- repository identity;
- Phase 2D worktree path;
- branch;
- current HEAD;
- staged changes;
- unstaged changes;
- untracked files;
- PR #15 local/remote HEAD;
- merge-base with PR #15;
- ahead/behind state.

Confirm:

- Phase 2D was created from the exact accepted PR #15 HEAD;
- PR #15 was not modified;
- main was not modified;
- no commit was created;
- no Phase 2D branch was pushed;
- no Phase 2D PR exists.

If the candidate is not based on the exact accepted PR #15 HEAD, return:

PHASE_2D_INDEPENDENT_REVIEW_INSUFFICIENT_EVIDENCE

and STOP.

==================================================
4. EXACT DIFF INVENTORY
==================================================

Inspect the complete Phase 2D diff relative to the exact PR #15 HEAD.

The implementation agent reported approximately:

- 9 changed files;
- +1521 / -4;
- new ADR 0004;
- new app/recipes package;
- new approved_recipes.py;
- new test_approved_recipe_pilot.py;
- limited Orchestrator modifications;
- extensions to three existing test files;
- ADR index update.

Produce the exact changed-file inventory.

Classify every file:

- REQUIRED
- JUSTIFIED_TEST
- JUSTIFIED_ADR
- UNNECESSARY
- OUT_OF_SCOPE
- SUSPICIOUS

No unexplained file may remain for PASS.

==================================================
5. ADR REVIEW
==================================================

Review:

docs/adr/0004-phase2d-approved-recipe-pilot.md

Verify it accurately records:

- one-recipe pilot;
- source_balance_mom_change;
- Q25/Q26-style route;
- dataset-scoped governed plan;
- feature flag default OFF;
- strict metadata requirement when ON;
- fail-closed behavior;
- dependency-aware compatibility;
- live registry_version used for evidence, not blind pinning;
- recipe lifecycle independent from registry lifecycle;
- rollback through feature-flag disablement;
- no Databricks, Unity Catalog, Collibra, Genie, Redis, Event Hubs,
  Graph, reporting, or fine-grained authorization implementation.

Verify the ADR does not silently make an enterprise architecture decision.

==================================================
6. APPROVED RECIPE CONTRACT
==================================================

Inspect the actual ApprovedRecipe and RecipeParameter models.

Verify:

- immutable/frozen behavior;
- unknown extra fields rejected;
- only repository-backed fields exist;
- every field has a current consumer;
- no speculative recipe DSL was introduced;
- no provider-specific fields exist;
- recipe lifecycle is explicit;
- recipe version is independent from registry version;
- governed dataset dependencies are explicit.

The implementation reported an eight-field ApprovedRecipe contract.

Independently determine whether all eight fields are necessary and sufficient.

==================================================
7. RECIPE REGISTRY AND SELECTION
==================================================

Verify:

- only the intended pilot recipe is registered;
- recipe ID is deterministic;
- lookup is exact and fail-closed;
- no fuzzy matching;
- no LLM recipe invention;
- no dynamic imports/plugin framework;
- no database/config-generated recipe registry;
- existing deterministic selector is reused.

Unknown recipe IDs must never fall into an ungoverned execution path.

==================================================
8. PARAMETER VALIDATION
==================================================

Inspect the parameter model and actual call path.

Verify:

- required values are enforced;
- type checking is enforced;
- allowed_values/domain is enforced;
- undeclared values are rejected;
- injection-like values fail before SQL building/execution;
- valid values preserve the existing SQL output;
- source code/source label mapping is deterministic;
- quote escaping is not the only trust control.

Check that no parameter value can select an undeclared table, builder, recipe,
or execution provider.

==================================================
9. GOVERNED SNAPSHOT COMPATIBILITY
==================================================

Verify the pilot:

1. resolves the current RegistrySnapshot through MetadataRegistryService;
2. captures the live registry_version for trace/evidence;
3. builds a dataset-scoped GovernedSemanticPlan;
4. reuses the existing service-level deterministic validator;
5. fails closed for unknown/ungoverned datasets;
6. does not use field_refs or relationship_refs that the current snapshot
   cannot validate;
7. does not treat an exact historical registry_version as a permanent
   recipe-validity lock.

Confirm a relevant incompatible dataset dependency fails closed.

Confirm an unrelated metadata-version change does not automatically invalidate
the recipe merely because the overall registry hash changed.

==================================================
10. FEATURE FLAG AND STRICT MODE
==================================================

Verify:

### Flag OFF

- current runtime behavior is unchanged;
- current routing and answers remain compatible;
- governed recipe evaluation does not alter unrelated routes;
- no strict-mode requirement is imposed on normal existing traffic.

### Flag ON

- only the pilot recipe enters the governed path;
- strict metadata validation is required or implied;
- unavailable strict metadata fails closed;
- no silent fallback executes the pilot as an ungoverned legacy route;
- rollback is possible by disabling the flag.

The feature flag must default to OFF.

==================================================
11. ORCHESTRATOR REVIEW
==================================================

Review every Orchestrator change.

The implementation agent reported approximately 21 changed lines across four
small hunks.

Verify:

- insertion is at the expected pre-execution seams;
- no broad Orchestrator redesign occurred;
- no duplicate route was created;
- no existing authorization ordering was weakened;
- recipe validation happens before SQL execution;
- failure uses an existing safe response family;
- unrelated recipes and LLM routes remain unchanged;
- DataSourceAdapter remains the execution dependency;
- no SqlDataStore concrete dependency was reintroduced.

==================================================
12. AUTHORIZATION PRESERVATION
==================================================

Verify reuse of:

- EffectivePermissions;
- deny_all short-circuit;
- SqlPolicy;
- SqlAuthorizationGuard;
- auth-bound DataSourceAdapter.

Recipe selection must not grant authorization.

Check:

- deny_all blocks before data access;
- unauthorized tables/entities execute no SQL;
- the existing audited blocked response remains intact;
- governed metadata does not carry permission grants;
- no column/row authorization model was added.

==================================================
13. EXECUTION BOUNDARY
==================================================

Verify the valid pilot route is:

ApprovedRecipe.builder_key
    ->
existing tested query builder
    ->
existing SQL string
    ->
existing SQL safety / authorization
    ->
DataSourceAdapter.execute_query
    ->
existing result/rendering path

Confirm:

- no execution-spec compiler was introduced;
- no new SQL dialect abstraction;
- no alternate database execution path;
- no direct SqlDataStore use in Orchestrator;
- no provider-specific implementation entered the diff.

==================================================
14. TEST QUALITY
==================================================

Do not judge tests only by pass counts.

Read important assertions in:

test/test_approved_recipe_pilot.py

and every extended test file.

Verify tests prove:

- contract immutability and extra-field rejection;
- known/unknown recipe behavior;
- lifecycle gate;
- parameter presence/type/domain validation;
- injection-like value rejection;
- dataset-scoped governed-plan validation;
- strict-mode failure;
- feature flag OFF regression;
- feature flag ON positive route;
- no SQL on validation failure;
- deny_all and unauthorized-table behavior;
- DataSourceAdapter execution;
- existing SQL policy/read-only enforcement;
- unrelated recipes remain unchanged.

Flag tests that overmock the path they claim to prove.

==================================================
15. SECURITY FINDING: OBJECT NAME DISCLOSURE
==================================================

The implementation report identified a pre-existing behavior:

an unauthorized denial response may include the blocked physical object name,
for example a dbo-qualified view.

Review this independently.

Determine:

- exact production path;
- whether the value is exposed to the user, debug-only, or audit-only;
- whether unauthorized users can learn metadata they are not entitled to know;
- whether it is introduced or expanded by Phase 2D;
- severity: BLOCKER / HIGH / MEDIUM / LOW / OBSERVATION;
- whether it blocks Phase 2D technical acceptance;
- the minimum separate remediation if required.

Do not fix it in this review.

Do not dismiss it merely because it is pre-existing.

==================================================
16. ADR INDEX FINDING
==================================================

The implementation report states that ADR 0003 has no row in the ADR index,
and that the Phase 2D agent deliberately did not modify PR #15 to fix it.

Verify the exact state.

Determine:

- whether ADR 0004 is indexed;
- whether ADR 0003 is missing;
- whether this is inherited from PR #15;
- whether it blocks the stacked candidate;
- what must be done before the final integrated Phase 2D merge.

Do not modify PR #15 or the Phase 2D candidate.

==================================================
17. SCOPE AUDIT
==================================================

Search the complete diff.

Confirm no implementation was added for:

- Databricks SQL;
- Databricks authentication;
- Unity Catalog;
- Collibra;
- Genie;
- Redis;
- Event Hubs;
- cross-source joins;
- Graph or GraphRAG;
- Answer Intelligence/report templates;
- KPI/glossary;
- fine-grained authorization;
- recipe-management UI;
- full lifecycle automation;
- frontend;
- infrastructure/deployment;
- broad planner migration;
- migration of all historical recipes.

==================================================
18. VALIDATION GATES
==================================================

Run independently:

1. focused Approved Recipe tests;
2. Phase 2A/2B/2C regression;
3. Phase 2C.5 provider-abstraction regression;
4. MetadataRegistryService tests;
5. authorization tests;
6. SQL policy/store tests;
7. semantic-model/query-recipe tests;
8. golden baseline;
9. full backend regression with configured coverage;
10. git diff --check;
11. excluded-technology scan.

Historical implementation results were:

- focused: 107 passed;
- selected 18-file regression: 405 passed;
- full backend: 945 passed, 3 skipped;
- coverage: 86.72%;
- required gate: 75%;
- excluded-technology scan: 0.

Different counts are acceptable only if explained.

Do not regenerate baselines.

Do not install or upgrade dependencies.

==================================================
19. FINDINGS
==================================================

Report findings by severity:

- BLOCKER
- HIGH
- MEDIUM
- LOW
- OBSERVATION

For each finding include:

- file/symbol/path;
- evidence;
- why it matters;
- whether introduced by Phase 2D;
- whether it blocks technical acceptance;
- minimum remediation.

PASS requires zero BLOCKER and zero HIGH findings attributable to or
necessarily blocking the Phase 2D pilot.

==================================================
20. FINAL ACCEPTANCE MATRIX
==================================================

Answer Yes/No with evidence:

1. Is the candidate based on the exact accepted PR #15 HEAD?
2. Did PR #15 remain unchanged?
3. Is the ApprovedRecipe contract minimal and immutable?
4. Is recipe selection deterministic and LLM-independent?
5. Are parameters allow-listed and fail-closed?
6. Is the recipe validated against the current governed snapshot?
7. Is registry_version recorded without blind compatibility pinning?
8. Does flag OFF preserve existing behavior?
9. Does flag ON fail closed when governance is unavailable?
10. Is authorization unchanged and independently enforced?
11. Does valid execution use DataSourceAdapter and existing SQL policy?
12. Is the implementation limited to one pilot recipe?
13. Are all regression/coverage/golden gates acceptable?
14. Is the complete diff bounded to Phase 2D?
15. Did Phase 2D avoid every excluded technology?
16. Is the candidate technically safe for commit/push as a stacked Draft PR?

==================================================
21. FINAL VERDICT
==================================================

Return exactly one:

PHASE_2D_INDEPENDENT_REVIEW_PASS

or

PHASE_2D_INDEPENDENT_REVIEW_FAIL

or

PHASE_2D_INDEPENDENT_REVIEW_INSUFFICIENT_EVIDENCE

If PASS, state:

The Phase 2D Approved Recipe Pilot stacked candidate is technically ready to be
committed and pushed for a Draft stacked PR based on
phase2/provider-abstraction-foundation. It is not ready to merge until PR #15
is merged, the branch is rebased onto main, and final integrated acceptance is
re-run.

If FAIL, provide only the smallest bounded remediation.

Do not implement fixes.

==================================================
22. REPORT
==================================================

Save outside the worktree:

/tmp/ASKTD_PHASE_2D_INDEPENDENT_REVIEW_2026-08-22.md

Required sections:

1. Repository / Stack Evidence
2. Executive Verdict
3. Exact Diff Inventory
4. ADR Review
5. ApprovedRecipe Contract
6. Registry and Selection
7. Parameter Validation
8. Governed Snapshot Compatibility
9. Feature Flag / Strict Mode
10. Orchestrator Review
11. Authorization Preservation
12. Execution Boundary
13. Test Quality
14. Security Finding Review
15. ADR Index Review
16. Scope Audit
17. Validation Results
18. Findings by Severity
19. Final Acceptance Matrix
20. Remaining Remediation
21. Final Recommendation

At completion explicitly state:

- Repository files modified by review: No
- PR #15 changed: No
- main changed: No
- Commit created: No
- Branch pushed: No
- Phase 2D PR created: No
- Phase 2D formally accepted: No

Then STOP.
