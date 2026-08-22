We are performing the FINAL INDEPENDENT RE-REVIEW of the AskTD Phase 2C.5 Provider Abstraction Foundation after remediation of the first independent-review findings.

This is strictly:

READ-ONLY INDEPENDENT REVIEW

Do not modify any repository file.

Do not fix findings.

Do not commit, push, create a PR, merge, deploy, rebase, switch branches, or start Phase 2D.

Use a fresh review session independent from the implementation/remediation session.

⸻

1. Context

Program Phase 2C is formally closed.

The initial Phase 2C.5 implementation received:

PHASE_2C5_INDEPENDENT_REVIEW_FAIL

The first independent review identified:

1. HIGH — orchestrator.py still directly imported/constructed SqlDataStore.
2. DataSourceAdapter contract was broader than required by real orchestration.
3. Fake-adapter tests did not sufficiently prove the actual production injection/composition path.

A bounded remediation was then completed.

Remediation verdict:

PHASE_2C5_REMEDIATION_READY_FOR_RE_REVIEW

⸻

2. Expected current implementation state

Expected branch:

phase2/provider-abstraction-foundation

The branch has NOT been committed or pushed yet.

Expected remediation architecture:

Composition root / app.main
        |
        +--> build_default_data_source()
                  |
                  +--> SqlDataStore
        |
        v
Orchestrator
        |
        v
DataSourceAdapter

The core Orchestrator should no longer know the concrete SqlDataStore.

⸻

3. Previously reported remediation evidence

The remediation agent reported this core dependency audit:

* Direct SqlDataStore import in Orchestrator: No
* Direct SqlDataStore(...) construction: No
* Concrete SqlDataStore annotation: No
* Concrete isinstance(..., SqlDataStore) dependency: No
* Default construction moved to:
    app.main.build_default_data_source()

Reported validation:

* Phase 2A/2B/2C focused regressions: 144 passed
* MetadataRegistryService: 11 passed
* Authorization: 61 passed
* SQL/Orchestrator adjacent: 120 passed
* Golden baseline: 10 passed
* Full backend: 887 passed, 3 skipped
* Coverage: 86.63%
* git diff --check: PASS

Independently verify these claims.

Do not trust them merely because the remediation agent reported them.

⸻

4. Verify repository state

Report:

* repository;
* worktree;
* branch;
* original Phase 2C.5 base SHA;
* current HEAD;
* origin/main SHA;
* staged files;
* unstaged files;
* untracked files.

Confirm:

* no commit was created;
* branch was not pushed;
* Phase 2D has not started.

Do not change Git state.

⸻

5. Exact diff inventory

Inspect the complete current Phase 2C.5 diff against its original origin/main base.

Produce the exact changed-file list.

The remediation report indicates changes involving approximately:

* main.py
* orchestrator.py
* src/backend/app/contracts/data_source.py
* test_authz_no_access_guard.py
* test_contracts_and_helpers.py
* test/test_provider_abstraction_contracts.py
* docs/adr/0003-phase2c5-provider-abstraction-foundation.md

Do not assume this list is complete.

For each actual changed file classify:

* REQUIRED
* JUSTIFIED_TEST
* JUSTIFIED_ADR
* UNNECESSARY
* OUT_OF_SCOPE
* SUSPICIOUS

No unexplained file may remain for PASS.

⸻

6. Re-review the original HIGH finding

Search orchestrator.py and relevant core modules for all occurrences of:

SqlDataStore

Verify specifically:

* direct import: absent;
* direct construction: absent;
* direct concrete type annotation: absent;
* concrete isinstance/type checks: absent.

Also search for aliases or indirect imports that would merely hide the same concrete dependency.

PASS requires that core Orchestrator depends only on the provider-neutral contract at this seam.

⸻

7. Composition-root review

Inspect:

app.main.build_default_data_source()

or the actual final construction location.

Verify:

* this is genuinely outside core Orchestrator;
* it is a sensible existing composition/runtime wiring boundary;
* it constructs current SqlDataStore;
* existing authentication context is passed exactly as required;
* existing default runtime behavior remains unchanged;
* no new DI framework/service locator/plugin system was introduced.

The concrete default being SqlDataStore is correct for current behavior.

The requirement is separation of dependency direction, not elimination of SQL Server.

⸻

8. DataSourceAdapter minimality

Re-derive the contract independently from real production Orchestrator/core usage.

For every Protocol member identify at least one real production consumer.

Check that the remediation removed members/arguments that were present only because SqlDataStore exposed them.

The contract must not contain speculative capabilities for:

* Databricks;
* Unity Catalog;
* Collibra;
* Genie;
* cross-source queries.

Also verify it does not leak:

* SQL Server connection objects;
* vendor SDKs;
* T-SQL-specific implementation objects.

A SQL/query-shaped method can remain if current core genuinely requires it.

Return PASS only if the contract is the smallest practical production abstraction.

⸻

9. Substitution-test review

Inspect the updated fake/test adapter tests.

They must prove the actual supported production seam.

Verify there is a test proving:

1. fake DataSourceAdapter is injected using the supported factory/dependency path;
2. representative Orchestrator behavior uses the fake;
3. concrete SqlDataStore construction does not occur;
4. no real database connection is attempted;
5. fake receives expected calls;
6. result/behavior is correct.

Ensure the test does not simply instantiate isolated helper functions while bypassing the path it claims to prove.

Do not accept an isinstance()-only conformance test as sufficient substitution evidence.

⸻

10. Dependency-direction regression protection

Inspect the new test designed to prevent future direct concrete coupling.

Verify it meaningfully protects:

Orchestrator -> DataSourceAdapter

rather than:

Orchestrator -> SqlDataStore

Prefer AST/import/structural or meaningful behavioral protection.

Flag overly fragile text/formatting assertions.

⸻

11. Existing provider seams

Verify remediation did NOT create duplicate abstractions.

Execution

Existing:

DatabaseTool

should remain the execution-provider seam.

No redundant ExecutionProvider hierarchy should exist.

Governance

Existing:

MetadataRegistryService
+
RegistrySnapshot

should remain the governance-provider/canonical metadata boundary.

No pointless DataGovernanceProvider forwarding wrapper should exist.

Authorization

Existing:

EffectivePermissions

should remain the authorization-scope foundation.

No parallel AuthorizationScope model should exist.

Authorization must remain fail-closed and entity scoped.

⸻

12. Behavioral equivalence

Inspect changed production code for any unintended behavior change to:

* SQL text;
* SQL validation;
* query recipes;
* authentication;
* authorization;
* result shapes;
* connection behavior;
* retries;
* timeouts;
* exceptions;
* logging;
* metadata selection;
* API responses.

The only intended behavioral/architectural change is dependency composition.

Existing users should continue to use the current SQL path without new configuration.

⸻

13. Configuration audit

Verify:

* no new provider selector is required for current users;
* current SQL behavior remains the default;
* no config was added for nonexistent providers.

There must be no selectable:

* Databricks provider;
* Genie provider;
* Unity Catalog provider;
* Collibra provider.

⸻

14. Scope audit

Search the complete diff.

Confirm NO implementation was added for:

* Databricks SQL;
* Databricks authentication;
* Unity Catalog;
* Collibra;
* Genie;
* Redis;
* Event Hubs;
* cross-source joins;
* SQL dialect abstraction for Databricks;
* Phase 2D recipes;
* KPI/glossary work;
* fine-grained authorization;
* frontend;
* infrastructure/deployment.

Do not fail the review because pre-existing SQL Server-specific implementation still exists behind SqlDataStore.

⸻

15. ADR review

Review:

docs/adr/0003-phase2c5-provider-abstraction-foundation.md

Verify it accurately represents the final dependency direction:

Composition Root
      -> SqlDataStore
Orchestrator
      -> DataSourceAdapter

It should also correctly state:

* DatabaseTool = existing execution seam;
* MetadataRegistryService / RegistrySnapshot = current governance seam;
* EffectivePermissions = authorization foundation;
* no Databricks/Genie/Unity/Collibra implementation;
* Phase 2D not started.

No future enterprise decision should be described as already implemented or approved.

⸻

16. Validation

Re-run independently:

1. provider-abstraction contract tests;
2. Phase 2A/2B/2C focused regression;
3. MetadataRegistryService tests;
4. authorization regression;
5. SQL datastore/orchestrator-adjacent regression;
6. golden baseline;
7. full backend regression with configured coverage;
8. git diff --check.

Historical post-remediation results:

* 144 focused
* 11 MetadataRegistryService
* 61 authorization
* 120 SQL/Orchestrator
* 10 golden
* 887 backend / 3 skipped
* 86.63% coverage

Different totals are acceptable if explained by current repository state.

Do not regenerate baselines.

Do not install/upgrade dependencies.

⸻

17. Findings

Report findings in severity order:

* BLOCKER
* HIGH
* MEDIUM
* LOW
* OBSERVATION

For each include:

* file;
* symbol/area;
* finding;
* reason;
* minimum remediation.

PASS requires:

* zero BLOCKER;
* zero HIGH.

MEDIUM/LOW findings must be evaluated for whether they truly block this bounded foundation.

⸻

18. Final architecture acceptance questions

Answer Yes/No with evidence:

1. Does Orchestrator still directly know SqlDataStore?
2. Can a fake DataSourceAdapter replace the concrete implementation through the real supported seam?
3. Does the current runtime still default to SqlDataStore?
4. Is DataSourceAdapter minimal?
5. Is DataSourceAdapter provider-neutral?
6. Were existing Execution/Governance/Authorization abstractions reused?
7. Was any future provider implementation added?
8. Did Phase 2D start?
9. Are Phase 2A/2B/2C regressions still clean?
10. Is the complete diff bounded to Phase 2C.5?

For PASS, expected answers are:

1. No
2. Yes
3. Yes
4. Yes
5. Yes
6. Yes
7. No
8. No
9. Yes
10. Yes

⸻

19. Final verdict

Return exactly ONE:

PHASE_2C5_INDEPENDENT_REVIEW_PASS

or

PHASE_2C5_INDEPENDENT_REVIEW_FAIL

or

PHASE_2C5_INDEPENDENT_REVIEW_INSUFFICIENT_EVIDENCE

Use PASS only if the previous HIGH issue is fully resolved and no new HIGH/BLOCKER exists.

If PASS state:

The remediated Phase 2C.5 provider-abstraction foundation is technically ready to be committed and pushed for normal PR/CI review. Phase 2D has not started.

If FAIL, give only the minimum additional remediation required.

Do not implement it.

⸻

Required report

Save outside the worktree:

/tmp/ASKTD_PHASE_2C5_INDEPENDENT_REREVIEW_2026-08-22.md

Include:

1. Repository / Worktree Evidence
2. Executive Verdict
3. Exact Diff Inventory
4. Original HIGH Finding Revalidation
5. Composition Root Review
6. DataSourceAdapter Review
7. Substitution Test Review
8. Dependency-Direction Regression Test
9. Existing Provider Seam Review
10. Behavioral Equivalence
11. Configuration Review
12. ADR Review
13. Scope Audit
14. Validation Results
15. Findings by Severity
16. Final Architecture Acceptance Matrix
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
