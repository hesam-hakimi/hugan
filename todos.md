
We are remediating the existing AskTD Phase 2C.5 provider-abstraction implementation after an independent review.

The independent verdict was:

PHASE_2C5_INDEPENDENT_REVIEW_FAIL

The regression suite is green, but the reviewer identified one HIGH architectural issue plus two related contract/test-quality issues.

This is a BOUNDED REMEDIATION.

Do NOT redesign the application.

Do NOT commit, push, create a PR, merge, deploy, or start Phase 2D.

Work only in the existing Phase 2C.5 worktree/branch:

phase2/provider-abstraction-foundation

Preserve all existing uncommitted implementation changes.

⸻

1. Independent review findings to remediate

The independent reviewer reported:

HIGH — Core dependency inversion is incomplete

orchestrator.py still imports and constructs SqlDataStore.

Therefore:

Orchestrator
   -> SqlDataStore

still exists in production code even though DataSourceAdapter was introduced.

The required architecture is:

Composition Root / Runtime Wiring
        |
        +--> SqlDataStore
        |
        v
Orchestrator
        |
        v
DataSourceAdapter

Orchestrator must not know the concrete SqlDataStore type.

Contract surface is broader than necessary

The new DataSourceAdapter Protocol contains API details/parameters that are not actually required by the core orchestration dependency.

The contract must be derived strictly from real Orchestrator/core usage.

Do not design it for hypothetical Databricks or future providers.

Fake-adapter substitution test is insufficient

The existing fake-adapter test does not actually exercise the injected factory/composition path strongly enough to prove that Orchestrator can operate without constructing SqlDataStore.

⸻

2. First verify the findings

Before editing:

1. inspect the complete Phase 2C.5 diff;
2. locate every SqlDataStore import, type annotation, constructor call, and concrete-type check in orchestrator.py;
3. identify which are actually part of the orchestration/core dependency;
4. identify the current runtime composition entry point(s), factory/helper modules, or application bootstrap that already construct dependencies.

Report the exact evidence before modifying.

Do not assume the best composition root from this prompt alone.

⸻

3. Remove concrete SqlDataStore dependency from Orchestrator

The final production orchestrator.py must not import SqlDataStore solely to construct or type-check its data source.

Move concrete SQL-store creation to the smallest existing composition/runtime wiring boundary supported by repository evidence.

Preferred order:

1. reuse an existing application composition/factory/bootstrap module if one already exists;
2. otherwise introduce one small dedicated factory/composition helper outside orchestrator.py.

Do NOT add a DI framework, plugin system, service locator, or global registry.

The concrete default may still be:

SqlDataStore

but only the outer composition layer should know that.

Example conceptual shape:

def build_default_data_source(auth_context) -> DataSourceAdapter:
    return SqlDataStore(auth_context=auth_context)

and:

Orchestrator(..., data_source_factory=...)

or another equivalent minimal pattern supported by the existing code.

Do not force this exact signature if repository evidence supports a simpler existing pattern.

⸻

4. Eliminate concrete type checks from core

Search for logic such as:

isinstance(x, SqlDataStore)

or equivalent concrete checks in core orchestration.

Replace them only where required with capability/contract-based behavior.

Do not add fake marker methods merely to avoid a type check.

If some behavior genuinely cannot be expressed through the current adapter contract without changing semantics, STOP and report it rather than inventing a new architecture.

⸻

5. Minimize DataSourceAdapter

Re-derive the Protocol from actual production consumers.

For every Protocol member answer:

Which current core production call requires this member?

Remove any method/property/argument that exists only:

* for hypothetical future providers;
* because SqlDataStore happens to expose it;
* for tests only;
* for SQL Server implementation convenience that core does not consume.

The Protocol should represent the minimum orchestration-required capability.

Do not expose:

* SQL Server connection objects;
* implementation-specific clients;
* vendor SDK types;
* speculative Databricks concepts.

If a SQL-shaped parameter is genuinely part of the existing application abstraction, it may remain, but document why the core actually requires it.

⸻

6. Preserve existing SQL behavior

Do not change:

* SQL text;
* query recipes;
* SQL safety;
* authorization;
* connection handling;
* retry behavior;
* timeouts;
* result shapes;
* current source-selection behavior;
* default Azure SQL/SQL Server runtime behavior.

This remediation is dependency-direction work only.

⸻

7. Strengthen the substitution test

Add or correct a test that exercises the actual production injection/factory path.

The test must prove all of the following:

1. a fake DataSourceAdapter can be supplied through the supported production seam;
2. representative Orchestrator behavior uses that fake;
3. the real SqlDataStore constructor is NOT invoked;
4. no database connection is attempted;
5. the fake receives the expected calls;
6. observable Orchestrator behavior remains correct.

A strong pattern is acceptable where the test temporarily makes the concrete SqlDataStore construction fail loudly and proves the injected path still succeeds.

Do not overmock the Orchestrator method being tested.

⸻

8. Add a dependency-direction regression test

Add a lightweight test/static assertion ensuring core orchestrator.py does not regress back to a direct concrete SqlDataStore dependency.

Prefer checking behavior/import structure using repository-supported techniques.

Do not create a fragile test based only on formatting or exact line text if an AST/import-level or structural test is straightforward.

The intent to protect is:

Orchestrator depends on DataSourceAdapter, not SqlDataStore.

⸻

9. Re-review the other three seams

Do NOT alter them unless this remediation proves necessary.

Preserve:

* DatabaseTool as the existing execution-provider seam;
* MetadataRegistryService / RegistrySnapshot as the governance boundary;
* EffectivePermissions as the authorization-scope foundation.

Do not introduce duplicate wrappers or renamed abstractions.

⸻

10. Explicitly remain out of scope

Do NOT add:

* Databricks adapter;
* Databricks authentication;
* Unity Catalog provider;
* Collibra provider;
* Genie provider;
* future-provider stubs;
* SQL dialect abstraction;
* provider selector config for nonexistent providers;
* cross-source joins;
* Phase 2D recipes;
* KPI/glossary functionality;
* Redis;
* Event Hubs;
* fine-grained authorization;
* deployment changes;
* frontend changes;
* broad Orchestrator redesign.

⸻

11. ADR consistency

Update the Phase 2C.5 ADR only if needed to accurately describe the corrected dependency direction.

It must not claim that Orchestrator is decoupled if it still imports/constructs the concrete store.

The ADR should describe the actual final structure.

⸻

12. Run focused remediation tests first

Run:

* provider-abstraction contract tests;
* Orchestrator-adjacent tests;
* SQL datastore tests;
* new substitution/dependency-direction tests.

Inspect assertions, not just pass counts.

⸻

13. Run all existing acceptance gates again

After the remediation:

1. Phase 2A/2B/2C focused regression;
2. MetadataRegistryService integration tests;
3. authorization regressions;
4. SQL datastore/orchestrator-adjacent regressions;
5. golden baseline;
6. full backend regression;
7. configured coverage gate;
8. git diff --check.

Historical pre-remediation results were:

* Phase 2A/2B/2C: 142 passed
* MetadataRegistryService: 11 passed
* authorization: 61 passed
* SQL/orchestrator adjacent: 118 passed
* golden: 10 passed
* full backend: 886 passed, 3 skipped
* coverage: 86.64%

Investigate legitimate count changes instead of forcing these exact totals.

Do not regenerate baselines.

Do not install/upgrade dependencies.

⸻

14. Final dependency audit

Before finishing, explicitly search production code and report:

Orchestrator

* direct SqlDataStore import: Yes/No
* direct SqlDataStore(...) construction: Yes/No
* SqlDataStore concrete type annotation: Yes/No
* concrete isinstance(..., SqlDataStore) dependency: Yes/No

For a successful remediation, all core dependency answers above should be No, unless a clearly justified non-core compatibility case is identified and explained.

Outer composition layer

Report exactly where the default concrete SqlDataStore is now constructed.

That location must be outside the core Orchestrator dependency.

⸻

15. Diff audit

Inspect the complete diff against the original Phase 2C.5 base SHA.

Classify every changed file.

Confirm:

* changes remain Phase 2C.5 only;
* no unrelated cleanup entered;
* no future-provider implementation entered;
* the remediation did not broaden scope.

⸻

16. Final verdict

Return exactly one:

PHASE_2C5_REMEDIATION_READY_FOR_RE_REVIEW

or

PHASE_2C5_REMEDIATION_HAS_BLOCKERS

or

PHASE_2C5_REMEDIATION_INSUFFICIENT_EVIDENCE

READY requires:

* Orchestrator no longer constructs/imports the concrete SQL store at the core seam;
* Protocol is minimal and justified by actual consumers;
* substitution test proves the production injection path;
* dependency-direction regression protection exists;
* behavior remains unchanged;
* all relevant regression gates pass;
* no scope expansion occurred.

⸻

17. Do not finalize Git workflow

Do NOT:

* commit;
* push;
* create PR;
* merge;
* deploy.

The corrected implementation must undergo another independent read-only review first.

⸻

Required report

Save outside the worktree:

/tmp/ASKTD_PHASE_2C5_REMEDIATION_2026-08-21.md

Include:

1. Independent Review Findings Reproduced
2. Root Cause
3. Concrete Dependency Removal
4. Composition Root / Factory Result
5. DataSourceAdapter Contract Reduction
6. Substitution Test Improvement
7. Dependency-Direction Regression Test
8. Other Existing Provider Seams
9. ADR Changes
10. Validation Results
11. Full Diff Inventory
12. Scope Audit
13. Remaining Findings
14. Final Verdict
15. Recommended Next Action

At completion report:

* Repository files changed by remediation: list
* Git commit created: No
* Branch pushed: No
* PR created: No
* Phase 2D started: No

Then STOP.
