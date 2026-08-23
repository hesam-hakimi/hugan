We need to perform an INDEPENDENT, READ-ONLY RE-REVIEW of the remediated AskTD / KMAI Phase 2D approved-recipe pilot.

This is NOT an implementation task.

Do NOT modify repository files.
Do NOT create or amend commits.
Do NOT push.
Do NOT create/update a PR.
Do NOT merge.
Do NOT start any later phase.
Do NOT fix findings during this review.
Do NOT trust the remediation chat summary by itself; independently verify the candidate from source and tests.

==================================================
1. REVIEW TARGET
==================================================

Repository:
TD-Enterprise/kmai-td-genie

Phase 2C.5 parent branch / accepted candidate:
phase2/provider-abstraction-foundation

Phase 2D working branch:
phase2/approved-recipe-pilot

Expected Phase 2D worktree:
/tmp/asktd-phase2d-approved-recipe-pilot

The Phase 2D remediation has completed but is intentionally:
- uncommitted
- unpushed
- without a PR
- not formally accepted

The remediation report states:

PHASE_2D_REMEDIATION_READY_FOR_RE_REVIEW

Do not accept that verdict without independent verification.

==================================================
2. PRIOR REVIEW FINDINGS THAT MUST BE RE-TESTED
==================================================

The previous independent review failed Phase 2D for two HIGH findings.

HIGH-1:
Governed validation occurred too late, after adapter/schema probing or other SQL-related work had already started.

Acceptance requirement:
For every Phase 2D approved-recipe path, governance/lifecycle/parameter validation must complete successfully BEFORE:

- DataSourceFactory / data-source construction
- adapter acquisition
- schema probing
- builder resolution/invocation
- SQL generation
- SQL execution

On every fail-closed path, prove that NONE of those operations occur.

HIGH-2:
ApprovedRecipe.builder_key did not authoritatively control the executed SQL builder; legacy query_kind control flow could construct the SQL before recipe validation.

Acceptance requirement:
After successful Phase 2D validation, the executed deterministic SQL builder must be selected through the approved recipe's builder_key.

There must not be an alternative legacy builder invocation that bypasses the authoritative builder_key decision for the Phase 2D pilot path.

==================================================
3. REMEDIATION CLAIMS TO VERIFY
==================================================

Independently verify each claim below from the actual candidate bytes:

1. Governed validation now precedes ALL:
   - adapter creation/access
   - schema probing
   - builder resolution
   - builder execution
   - SQL execution

2. builder_key is authoritative for selecting the executed deterministic builder.

3. ApprovedRecipe contains only six actively consumed contract fields after remediation.
   Verify the exact field set and prove each retained field has a real runtime or validation consumer.
   Flag any dead/unused contract field.

4. The pilot parameter model validates valid source-code/source-label pairs, including:
   IMSB -> Deposits
   STAX -> Savings

5. Mismatched pairs fail closed.

6. Missing required parameters fail closed.

7. Out-of-domain values fail closed.

8. Unknown recipe IDs fail closed.

9. Non-approved/non-published lifecycle state fails closed.

10. Ungoverned dataset references fail closed.

11. Strict-mode unavailable/off behavior remains fail closed where required by the pilot contract.

12. deny_all and unauthorized-object paths preserve the EXISTING audited blocked behavior.

13. For governed denial/validation failures, prove with executable dependency-injection/call-count tests that there are ZERO calls to:
   - data-source factory
   - adapter/data source
   - schema helper/probe
   - authoritative builder
   - legacy builder
   - SQL execution

Do not accept string scanning as sufficient evidence for this item.

==================================================
4. ARCHITECTURAL BOUNDARIES THAT MUST REMAIN INTACT
==================================================

This remains a bounded Phase 2D pilot.

Confirm that the diff does NOT introduce:

- Databricks implementation
- Unity Catalog implementation
- Genie implementation
- Collibra implementation
- Redis
- Event Hubs
- cross-source execution
- new provider SDKs
- SQL dialect abstraction
- broad orchestrator redesign
- frontend changes
- fine-grained row/column authorization model
- a second authorization engine
- a second read-only enforcement layer
- a second SQL parser/table-reference extractor
- an intermediate execution-spec/compiler architecture
- broad recipe migration
- registry seed migration
- recipe folding into RegistrySnapshot identity

Existing SQL Server-backed execution behind DataSourceAdapter is acceptable for this pilot.

==================================================
5. CANDIDATE IDENTITY / IMMUTABILITY
==================================================

Before reviewing logic:

1. Verify the exact worktree and branch.
2. Capture:
   - current HEAD
   - base/parent SHA
   - git status
   - git diff --stat
   - git diff --name-status
3. Compute a deterministic digest for the current Phase 2D candidate files.
4. Record the start-state hashes.
5. At the end of review, recompute them.
6. Prove the candidate bytes did not change during the review.

If the expected Phase 2D worktree is absent, do not silently inspect another checkout.

If a correct reachable candidate exists elsewhere, identify it explicitly and prove equivalence before continuing.

Otherwise STOP with a clear blocker.

==================================================
6. FILE-SCOPE REVIEW
==================================================

Enumerate the complete Phase 2D diff against its Phase 2C.5 parent.

Pay particular attention to:

- docs/adr/0004-phase2d-approved-recipe-pilot.md
- src/backend/app/recipes/
- src/backend/app/recipes/approved_recipes.py
- src/backend/app/orchestrator.py
- test/test_approved_recipe_pilot.py
- test/test_semantic_plan_contract.py
- test/test_semantic_models.py
- test/test_authz_no_access_guard.py
- test/test_query_recipes.py
- test/test_golden_baseline.py
- test/test_provider_abstraction_contracts.py
- docs/adr/README.md

Do not assume this list is complete.
The live diff is authoritative.

Also separate:
A. Phase 2D-attributable findings
B. pre-existing findings
C. PR #15 / Phase 2C.5 findings

Do not fail Phase 2D for unrelated pre-existing issues unless Phase 2D makes them worse or depends on them unsafely.

==================================================
7. REQUIRED SOURCE-CODE TRACE
==================================================

Trace the real pilot execution path end-to-end:

user request
-> authentication context
-> coarse deny_all handling
-> deterministic recipe selection
-> approved recipe lookup
-> recipe lifecycle validation
-> required parameter validation
-> allowed-domain / pair validation
-> governed dataset plan construction
-> governed semantic validation
-> authoritative builder resolution from builder_key
-> SQL construction
-> existing authorization/read-only enforcement
-> DataSourceAdapter.execute_query(...)
-> result handling

For each stage, identify the exact symbol/file and confirm ordering.

The key question is:

CAN ANY ADAPTER, SCHEMA PROBE, BUILDER, SQL GENERATION, OR SQL EXECUTION OCCUR BEFORE THE APPROVED RECIPE HAS PASSED ITS GOVERNED VALIDATION?

The only acceptable answer for PASS is:
NO, proven by code path plus executable tests.

==================================================
8. REQUIRED TESTING
==================================================

Run the narrowest tests first, then broaden.

At minimum run:

A. Approved-recipe focused tests
B. Semantic-plan compatibility tests
C. Authorization/no-access tests
D. Query recipe tests
E. Provider abstraction tests
F. Golden baseline
G. Relevant Phase 2A / 2B / 2C / 2C.5 regression slice
H. Full backend configured test suite
I. Coverage gate
J. git diff --check

Also run an excluded-technology scan against ADDED Phase 2D code.

The previous remediation reported approximately:

Focused Phase 2D: 124 passed
Full backend: 962 passed, 3 skipped
Coverage: ~86.75%
Golden baseline: 10 passed

These numbers are context only.
Do not force them.
Report the actual independently observed results.

==================================================
9. ADVERSARIAL TEST CASES
==================================================

Independently test or inspect coverage for at least these cases:

- valid Deposits/IMSB recipe request
- valid Savings/STAX recipe request
- mismatched IMSB/Savings
- mismatched STAX/Deposits
- missing required parameter
- unknown recipe id
- draft/non-approved recipe
- ungoverned dataset
- strict-mode unavailable/off
- deny_all user
- resolved-but-unauthorized dataset/table
- malicious/out-of-domain parameter
- flag OFF regression path
- flag ON successful pilot path

For every failed recipe/governance case, assert no adapter/schema/builder/SQL side effects.

==================================================
10. GOLDEN / REGRESSION REQUIREMENT
==================================================

With the Phase 2D pilot flag OFF:

Existing behavior must remain byte-for-byte / semantically unchanged where the current golden harness supports comparison.

Confirm:
- legacy recipe routing still works
- existing response behavior is preserved
- existing authorization behavior is preserved
- no new provider dependency leaks into core
- previous Phase 2C.5 abstraction guarantees remain intact

==================================================
11. REVIEW OF THE TWO REMEDIATION DESIGN CHOICES
==================================================

Explicitly answer:

A. Is governance now truly before all side-effectful data-source work?

B. Is ApprovedRecipe.builder_key now the single authoritative builder selector for the pilot lane?

C. Can legacy query_kind branching still choose or invoke another builder after recipe validation?

D. Can any schema probe occur before validation?

E. Can an unauthorized or invalid recipe cause any DB/data-source interaction?

F. Are all six ApprovedRecipe fields actually consumed?

G. Are the source_code/source_label pair rules sufficiently deterministic and fail-closed?

==================================================
12. SECURITY FINDING FROM PREVIOUS REVIEW
==================================================

The previous review also noted a pre-existing MEDIUM issue:

The resolved-but-unauthorized denial path may disclose the blocked physical object name.

Re-check whether Phase 2D:
- introduces it,
- worsens it,
- fixes it,
- or leaves it unchanged.

Classify it accurately.

Do NOT silently expand Phase 2D scope to fix it unless the Phase 2D implementation created the issue.

==================================================
13. OUTPUT REPORT
==================================================

Write a formal report outside the repository/worktree:

/tmp/ASKTD_PHASE_2D_INDEPENDENT_REREVIEW_2026-08-22.md

Include at minimum:

1. Candidate identity
2. Parent/base identity
3. Candidate byte/hash proof
4. Complete changed-file inventory
5. Source execution trace
6. Previous HIGH-1 disposition
7. Previous HIGH-2 disposition
8. ApprovedRecipe contract audit
9. Parameter/pair validation audit
10. Fail-closed side-effect audit
11. Authorization interaction
12. Provider-abstraction boundary audit
13. Excluded-technology scan
14. Test results
15. Coverage
16. Golden/regression results
17. Security/pre-existing findings
18. Severity-ranked findings
19. Acceptance matrix
20. Final verdict
21. Candidate immutability/end-state proof
22. Recommended next action

==================================================
14. VERDICT RULES
==================================================

Return EXACTLY ONE of these final verdict tokens:

PHASE_2D_INDEPENDENT_REREVIEW_PASS

or

PHASE_2D_INDEPENDENT_REREVIEW_FAIL

PASS requires BOTH former HIGH findings to be conclusively resolved.

Any remaining HIGH issue attributable to Phase 2D => FAIL.

A pre-existing unrelated MEDIUM/LOW finding should be recorded separately and should not automatically fail Phase 2D.

Do not downgrade an unresolved HIGH simply because tests are green.

==================================================
15. COMPLETION STATE
==================================================

At the end explicitly report:

Repository files modified by reviewer: Yes/No
Candidate bytes changed during review: Yes/No
PR #15 changed: Yes/No
main changed: Yes/No
Commit created: Yes/No
Branch pushed: Yes/No
Phase 2D PR created: Yes/No
Phase 2D formally accepted: Yes/No
Later phase started: Yes/No

This review must remain completely read-only.
