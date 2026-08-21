We are performing an INDEPENDENT READ-ONLY REVIEW of the AskTD / askAlpha / KMAI Phase 2C.5 Provider Abstraction Foundation implementation.

This review must be performed independently from the agent/session that implemented the change.

Do NOT modify anything.

Do NOT fix findings during this review.

Do NOT commit, push, merge, rebase, create a PR, change branches, or start Phase 2D.

⸻

1. Known project state

Program Phase 2C is formally closed:

PHASE_2C_POST_MERGE_CLOSURE_PASS

A bounded Phase 2C.5 implementation was then created from integrated origin/main.

Implementation verdict from the implementation agent:

PHASE_2C5_IMPLEMENTATION_READY_FOR_INDEPENDENT_REVIEW

Expected implementation branch:

phase2/provider-abstraction-foundation

Expected dedicated worktree:

asktd-phase2c5-provider-abstraction

The implementation has NOT been pushed.

The implementation is expected to still exist as local worktree changes.

Do not assume commit state. Verify it.

⸻

2. Previously reported implementation scope

The implementation agent reported changes around:

* src/backend/app/contracts/data_source.py
* orchestrator.py
* test_contracts_and_helpers.py
* test/test_provider_abstraction_contracts.py
* docs/adr/0003-phase2c5-provider-abstraction-foundation.md

The UI reported approximately:

6 files changed, +505 / -13

Reconcile the exact file list from Git rather than trusting this summary.

Previously reported validation:

* provider contract tests: PASS
* Phase 2A/2B/2C focused regressions: 142 passed
* MetadataRegistryService tests: 11 passed
* authorization regressions: 61 passed
* SQL datastore/orchestrator-adjacent regressions: 118 passed
* golden baseline: 10 passed
* full backend: 886 passed, 3 skipped
* coverage: 86.64%
* required threshold: 75%
* git diff --check: PASS

Independently verify the implementation and the important assertions.

⸻

3. Review objective

Determine whether the Phase 2C.5 change is:

1. genuinely minimal;
2. provider-neutral;
3. behavior-preserving;
4. compatible with Phase 2A/2B/2C;
5. free of duplicate abstraction layers;
6. safe to commit and push for PR review.

The review is not asking:

Can the tests pass?

It is asking:

Is this the correct smallest architectural seam, implemented safely?

⸻

4. Verify repository/worktree state first

Report:

* repository identity;
* worktree path;
* branch;
* branch base SHA;
* current HEAD SHA;
* origin/main SHA;
* staged changes;
* unstaged changes;
* untracked files;
* ahead/behind status if applicable.

Confirm the worktree originates from the integrated main containing accepted Phase 2C.

Do not mutate Git state.

⸻

5. Inspect the complete diff

Review the entire diff against the exact origin/main base from which this Phase 2C.5 branch was created.

Produce the exact changed-file list.

For every changed file classify:

* REQUIRED
* JUSTIFIED_TEST
* JUSTIFIED_ADR
* UNNECESSARY
* OUT_OF_SCOPE
* SUSPICIOUS

Reconcile any discrepancy between the previously reported “6 files changed” and the actual Git diff.

No unexplained changed file may remain for PASS.

⸻

6. DataSourceAdapter contract review

Inspect the new provider-neutral contract in:

src/backend/app/contracts/data_source.py

or the actual equivalent path.

Determine:

A. Contract minimality

Does the contract contain only capabilities currently required by core/orchestration?

FAIL the review if it contains speculative methods added only for hypothetical:

* Databricks;
* Unity Catalog;
* Collibra;
* Genie;
* cross-source execution.

B. Provider neutrality

The contract must not unnecessarily expose:

* SQL Server connection objects;
* T-SQL-specific types;
* Azure SQL implementation details;
* Databricks-specific constructs;
* vendor SDK objects.

Current SQL-shaped operations are acceptable only where they represent genuine current application behavior.

C. Structural compatibility

Verify the existing SqlDataStore satisfies the contract without rewriting its business/runtime behavior.

Prefer structural typing if that is what the implementation uses.

D. No fake future-proofing

There must be no empty implementations, fake adapters, NotImplementedError providers, or placeholder provider classes merely to make the hierarchy look complete.

⸻

7. Orchestrator decoupling review

This is the highest-risk part of the change.

Search the complete relevant orchestration path for direct:

SqlDataStore

imports, constructions, annotations, and assumptions.

The previous discovery found several direct construction/type-hint sites.

For each previous/direct site determine:

* before behavior;
* after behavior;
* whether construction now goes through a provider-neutral seam;
* whether default runtime behavior remains identical.

Verify:

A. Core dependency direction

Desired:

Orchestrator / Core
        |
        v
DataSourceAdapter
        |
        v
SqlDataStore

Not:

Orchestrator
   -> SqlDataStore concrete implementation

B. Test injection

Core/orchestration should be able to receive a fake/test implementation satisfying the contract without constructing real SqlDataStore.

C. No DI overengineering

Reject unnecessary:

* dependency-injection framework;
* service locator;
* plugin manager;
* dynamic import system;
* global provider registry;

unless one already existed and is simply reused.

D. Default behavior

Verify existing runtime still chooses the same SQL implementation by default.

No current user behavior should require new configuration.

⸻

8. ExecutionProvider review

The discovery concluded that the existing:

DatabaseTool

boundary already satisfies the architectural ExecutionProvider seam.

Verify this conclusion remains true after implementation.

Check:

* core consumers depend on the abstraction where appropriate;
* existing concrete selection remains configuration-driven;
* no duplicate ExecutionProvider hierarchy was created.

If the implementation introduced a new execution-provider abstraction solely for naming symmetry, classify that as a defect unless there is concrete need.

⸻

9. DataGovernanceProvider review

The discovery concluded that:

MetadataRegistryService

plus canonical:

RegistrySnapshot

already form the current governance-provider boundary.

Verify:

* Phase 2C canonical registry contracts are reused;
* no parallel canonical metadata model was introduced;
* no unnecessary forwarding/wrapper class exists merely to be named DataGovernanceProvider;
* semantic-plan validation still consumes canonical AskTD metadata;
* no Unity Catalog / Collibra structures leak into planning.

Future providers must eventually map INTO the canonical model.

They must not redefine it.

⸻

10. AuthorizationScope review

The discovery concluded that:

EffectivePermissions

is the existing authorization-scope foundation.

Verify:

* implementation reuses it;
* entity-level behavior remains unchanged;
* fail-closed behavior remains unchanged;
* no second AuthorizationScope model was created;
* no metadata record grants authorization;
* no dataset/column/row authorization was accidentally implemented.

Phase 2C.5 must not broaden user access.

⸻

11. Configuration review

Inspect every configuration change, if any.

Verify:

* existing default SQL behavior remains default;
* no user must configure a provider merely to preserve existing behavior;
* no speculative config keys were added for unsupported providers.

Specifically flag any unnecessary configuration for:

* Databricks;
* Genie;
* Unity Catalog;
* Collibra.

If no new config is needed, that is acceptable and potentially preferable.

⸻

12. Contract-test quality review

Do NOT judge tests only by pass/fail.

Read the important assertions in:

test/test_provider_abstraction_contracts.py

and other modified tests.

Verify that tests actually prove:

DataSourceAdapter

* existing SqlDataStore conforms to the contract;
* orchestration accepts a fake/test adapter;
* orchestration does not construct the concrete SQL store when an adapter is supplied;
* default path remains unchanged.

Existing execution seam

* DatabaseTool abstraction is still honored;
* no concrete execution implementation became hard-coded.

Governance seam

* canonical MetadataRegistryService/RegistrySnapshot remains the governed metadata boundary.

Authorization seam

* EffectivePermissions remains fail-closed and entity scoped;
* provider abstraction cannot bypass authorization.

Flag tests that:

* assert implementation internals instead of observable contract;
* merely test isinstance without proving decoupling;
* overmock away the behavior they are supposed to prove;
* duplicate production logic inside the test.

⸻

13. Behavioral regression review

Independently inspect whether any changed production code alters:

* SQL text;
* SQL validation;
* query parameters;
* connection handling;
* timeout behavior;
* retry behavior;
* authorization;
* metadata selection;
* result shape;
* exception handling;
* logging;
* public API responses.

Provider abstraction must be behavior-preserving.

Any behavioral change must be explicitly justified and within Phase 2C.5 scope.

⸻

14. ADR review

Review:

docs/adr/0003-phase2c5-provider-abstraction-foundation.md

or equivalent.

Verify it accurately states:

* current SQL path is now behind a provider-neutral source seam;
* DatabaseTool satisfies current execution-provider abstraction;
* MetadataRegistryService is the existing current governance seam;
* EffectivePermissions is the current extensible authorization foundation;
* future providers map into canonical AskTD contracts;
* Databricks/Genie/Unity/Collibra were NOT implemented;
* Phase 2D was NOT started.

The ADR must not claim future enterprise architecture decisions as approved implementation facts.

⸻

15. Explicit scope audit

Search the complete diff for signs of scope expansion.

There must be no implementation of:

* Databricks SQL;
* Databricks authentication;
* Unity Catalog;
* Collibra;
* Genie;
* Redis;
* Event Hubs;
* cross-source joins;
* new SQL dialect compiler;
* Phase 2D recipes;
* KPI/glossary semantics;
* fine-grained dataset/column/row authorization;
* frontend changes;
* deployment/infrastructure changes.

There must also be no broad cleanup/refactor unrelated to the provider seam.

⸻

16. Known deferred items

The prior discovery identified existing concerns such as:

* hard-coded dbo.* semantics;
* literal T-SQL in existing recipe-related code;
* planner not yet consuming the governed registry everywhere;
* coexistence of older and governed metadata paths.

Do NOT fail Phase 2C.5 merely because these pre-existing items exist.

However verify Phase 2C.5 did not make them worse.

Record them as deferred/future items only where appropriate.

⸻

17. Re-run validation

Run the existing relevant validation gates from the Phase 2C.5 worktree.

At minimum:

1. provider abstraction contract tests;
2. Phase 2A/2B/2C focused regression;
3. MetadataRegistryService tests;
4. authorization regressions;
5. SQL datastore/orchestrator-adjacent regressions;
6. golden baseline;
7. full backend regression with repository-configured coverage;
8. git diff --check.

Do not regenerate baselines.

Do not install/upgrade dependencies.

Report exact results.

If counts differ from:

* 142 focused
* 11 registry service
* 61 authorization
* 118 SQL/orchestrator
* 10 golden
* 886 backend / 3 skipped
* ~86.64% coverage

investigate the difference rather than automatically failing.

⸻

18. Review findings format

Report findings ordered by severity:

* BLOCKER
* HIGH
* MEDIUM
* LOW
* OBSERVATION

For every finding provide:

* file;
* symbol/line area;
* problem;
* why it matters;
* minimum fix.

Do NOT perform the fix.

⸻

19. Acceptance criteria

Return PASS only if all of the following are true:

* DataSourceAdapter is minimal;
* contract is provider-neutral;
* SqlDataStore behavior is preserved;
* Orchestrator no longer requires the concrete SQL store at the intended seam;
* fake/test adapter substitution is proven;
* execution/governance/authorization existing seams are reused instead of duplicated;
* no future provider implementation entered scope;
* tests meaningfully prove the contracts;
* parent Phase 2A/2B/2C behavior remains green;
* full regression and coverage are acceptable;
* diff is bounded;
* ADR is accurate;
* no BLOCKER/HIGH issue remains.

⸻

20. Final verdict

Return exactly ONE:

PHASE_2C5_INDEPENDENT_REVIEW_PASS

or

PHASE_2C5_INDEPENDENT_REVIEW_FAIL

or

PHASE_2C5_INDEPENDENT_REVIEW_INSUFFICIENT_EVIDENCE

If FAIL, provide the smallest bounded remediation required.

Do not fix it.

If PASS, explicitly state:

The Phase 2C.5 provider-abstraction foundation is technically ready to be committed and pushed for normal PR/CI review. Phase 2D has not started.

⸻

21. Required report

Save outside the worktree as:

/tmp/ASKTD_PHASE_2C5_INDEPENDENT_REVIEW_2026-08-21.md

Sections:

1. Repository / Worktree Evidence
2. Executive Review Verdict
3. Exact Diff Inventory
4. DataSourceAdapter Review
5. Orchestrator Decoupling Review
6. ExecutionProvider Mapping Review
7. DataGovernanceProvider Mapping Review
8. AuthorizationScope Review
9. Configuration Review
10. Contract Test Quality Review
11. Behavioral Regression Review
12. ADR Review
13. Scope Audit
14. Deferred Existing Issues
15. Validation Results
16. Findings by Severity
17. Remaining Remediation
18. Final Recommendation

At completion explicitly state:

* Repository files modified by review: No
* Git state changed by review: No
* Commit created: No
* Branch pushed: No
* PR created: No
* Phase 2D started: No

Then STOP.
