Task: LOCAL-PHASE-A0R2-TRIAGE-20260813-01
Mode: read-only isolated regression triage
Target: extension-source
Delivery: report-only
Mutation authorization: NONE
Phase A1: PROHIBITED

Objective

The prior differential validation established:

* clean A1/A2 and overlay B1/B2 all compile;
* shared repository-baseline failures occur in all four snapshots;
* B1 and B2 each introduce the same three assertion failures absent from A1/A2;
* focused B suites pass with 32 passing, 0 failing;
* registered A0 B runs pass with 6 passing, 0 failing;
* the complete 19-item executable coverage matrix was not produced;
* final classification was:

LOCAL_PHASE_A0R_AB_OVERLAY_REGRESSION

This task must identify the exact cause and minimal future repair scope. Do not repair anything yet.

Hard boundaries

1. Do not click Keep or Undo; leave the current nine-file review card pending.
2. Do not start, plan, scaffold, or implement Phase A1.
3. Do not edit any source, test, helper, configuration, documentation, package, or tracked/generated file.
4. Do not stage, commit, push, merge, rebase, switch branches, edit PR #7, or invoke CI.
5. Do not package, rebuild, install, uninstall, or replace a VSIX.
6. Do not install dependencies, compile, or test inside the real repository.
7. Do not modify any Consumer workspace or contact Databricks, ADF, SQL Server, storage, or another external system.
8. Do not modify:
    * .tsbuildinfo.test
    * package.json
    * CopilotAssetCatalog.ts
    * EtlActionToolService.ts
    * SolutionMemoryStore.ts
    * .github/**
    * AGENTS.md
    * workflow/**
    * COPY_ORDER.md
9. Do not restore RepoWriter, process.cwd(), ambient workspace inference, or preview with incomplete evidence.
10. Do not classify a test as stale merely because it fails under the new implementation.
11. Do not propose weakening, deleting, skipping, quarantining, or renaming tests out of discovery.

Temporary diagnostic output may be created only under one unique OS temporary root and must be deleted afterward.

Identity preflight

Verify read-only:

* repository: TD-Universe/agentic_etl
* origin: https://github.com/TD-Universe/agentic_etl.git
* branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* committed package version: 0.3.139
* protected dirty package version: 0.3.128
* staged changes: none
* candidate/installed VSIX: pre-A0 0.3.139
* current review scope: exactly nine A0R files

Capture before-state:

* exact git status --porcelain;
* registered worktrees;
* canonical paths and SHA-256 of all nine A0R files;
* hashes of the four protected dirty files;
* candidate VSIX SHA-256;
* protected control-plane hashes.

If identity or scope differs, stop with:

LOCAL_PHASE_A0R2_TRIAGE_BLOCKED_IDENTITY_OR_SCOPE

Overlay partitions

Resolve the exact nine canonical paths and partition them without changing them.

Production/source overlay

1. TrustedPlanningEvidenceService.ts
2. EtlAgent.ts
3. AgentMessageRouter.ts
4. AgentActionExecutor.ts
5. ResponseComposer.ts
6. index.ts

Test/test-helper overlay

7. trustedPlanningEvidenceService.test.ts
8. testPatterns.ts
9. phase5AgentRouter.test.ts

Prove that no tenth file is part of the overlay and that SolutionMemoryStore.ts is unchanged.

Isolated environment

Create one unique temporary dependency seed from git archive HEAD.

Because HEAD has no committed lockfile:

* install dependencies only in the temporary seed;
* record Node/npm versions;
* record exact installation command and exit code;
* record generated temporary lockfile SHA-256;
* record npm ls --depth=0;
* label the environment:

UNPINNED_TEMP_DEPENDENCY_RESOLUTION

Never copy dependencies, lockfiles, compiled output, or caches back to the repository.

Create these isolated variants using the identical dependency tree:

Variant	Source files	Test files
H	clean HEAD	clean HEAD
S	six-file A0 source overlay	clean HEAD tests
T	clean HEAD source	three-file A0 test overlay
F	six-file source overlay	three-file test overlay

If T cannot compile because its tests legitimately require new A0 types, record the exact compile errors. Do not treat that expected dependency mismatch as a product regression.

Do not reuse compiled/test output between variants.

Capture the exact three failures

Run the exact broader pure-unit command previously used on H, S and F, and on T if it compiles.

The original command must run unchanged first. A diagnostic reporter may then be added in a separate run solely to obtain structured failure output; it must not change test discovery or execution semantics.

For every failure, capture:

* full test file path;
* complete suite and test title;
* error/assertion class;
* exact expected value;
* exact actual value;
* normalized error message;
* first meaningful test stack frame;
* first meaningful production stack frame;
* variant(s) where it occurs;
* whether the same test passed, failed, or was absent in clean HEAD.

Produce the exact three-element F-only or overlay-sensitive failure set. Exit code alone is insufficient.

Individual and order-dependence reproduction

For each of the three failures, using variant F:

1. Run the test alone in a fresh process twice.
2. Run all three together twice.
3. Run the owning test file alone twice.
4. Reproduce it in the broader runner.
5. Identify the immediately preceding suite/test in broader execution order.
6. Run the preceding suite followed by the failing test.
7. Where supported without changing test semantics, run the owning file in reversed test order.

Repeat the corresponding individual test under H and S where it exists.

Record whether the failure is:

* reproducible individually;
* reproducible only in the owning file;
* reproducible only after another suite;
* reproducible only in the broader runner;
* caused by changed production code;
* caused by changed test/helper code.

Inspect read-only for shared mutable state, including:

* singleton or module-level registries;
* cached planning evidence;
* shared SolutionMemoryStore;
* environment-variable mutation;
* VS Code mocks;
* spies/stubs not restored;
* module cache;
* test lifecycle hooks;
* shared workspace/root selections;
* mutable response or plan fixtures.

Do not edit or reset tracked code during this investigation.

Route and hunk tracing

For each failure, trace the complete call path and identify:

* whether it exercises direct /create;
* /workflow create;
* another agent command;
* response composition only;
* preview/writer behavior;
* a fixture/helper rather than production behavior.

Map the observed change to the exact A0 overlay hunk(s).

Use the H/S/T/F comparison to distinguish production changes from test-overlay effects:

* Failure in S and F, absent in H: likely source behavior change.
* Failure only in F, while S passes: likely test/helper interaction or state/order issue.
* Failure only during broad F but not isolated F: likely shared-state/order leakage.
* Failure on /workflow create caused by the A0 gate: likely out-of-scope route interception.
* Old expectation requiring ambient RepoWriter or incomplete-evidence preview: candidate stale legacy expectation, but only after authoritative contract confirmation.

Per-failure adjudication

Classify each failure as exactly one:

TRUE_SOURCE_REGRESSION

A still-valid product invariant is violated by the source overlay.

Examples:

* /workflow create changes;
* unrelated routes are intercepted;
* valid complete evidence is mishandled;
* response compatibility is unintentionally broken;
* evidence mutates;
* behavior becomes nondeterministic.

STALE_LEGACY_EXPECTATION

The old expectation directly conflicts with an explicit A0 safety invariant, such as:

* ambient/default RepoWriter workspace resolution;
* process.cwd() fallback;
* preview with incomplete evidence;
* intent alone being treated as complete discovery/collision evidence.

Do not use this classification unless the original safety purpose is identified and a replacement exact assertion is proposed.

TEST_ORDER_OR_SHARED_STATE_LEAK

The test passes individually but fails after another suite or only within the broader process, with the responsible mutable state or missing cleanup boundary identified.

TEST_OVERLAY_OR_FIXTURE_DEFECT

The changed test/helper introduces an invalid fixture, incompatible expectation, or unintended effect not caused by production behavior.

OUT_OF_SCOPE_ROUTE_INTERCEPTION

The A0 direct /create evidence gate is incorrectly affecting /workflow create or another route that must remain unchanged.

INCONCLUSIVE

Evidence is insufficient or contradictory.

For each failure provide:

Field	Required evidence
Full test identity	File, suite and title
Expected/actual	Exact assertion values
Route	Direct create, workflow create, other, or fixture
H/S/T/F result	Compile and test status
Individual result	Two-run outcome
Broad result	Two-run outcome
Responsible hunk/state	Exact source or shared-state owner
Classification	One permitted classification
Preserved invariant	Original safety/compatibility purpose
Minimal proposed repair	Files and behavior, without editing
Required regression test	Exact future assertion

If any failure remains INCONCLUSIVE, do not recommend a repair.

Existing 19-item coverage audit

Without adding or editing tests, map the currently existing executable tests to these requirements:

1. Explicit selected-workspace provenance.
2. Ambiguous multi-root fail-closed behavior.
3. No process.cwd() or ambient fallback.
4. Empty-repository initialization intent.
5. STTM canonical identity, SHA-256 and containment.
6. Missing/external/stale STTM rejection.
7. Extension-source/installation-root rejection.
8. Windows drive and mixed-separator containment.
9. UNC escape handling.
10. Symlink/junction or equivalent resolved-path handling.
11. Missing job discovery represented explicitly as unresolved.
12. Missing collision/ownership evidence represented explicitly as unresolved.
13. Direct /create collects evidence before executor.
14. Executor receives immutable evidence.
15. Incomplete evidence blocks preview.
16. Exact unresolved codes reach ResponseComposer.
17. Spies prove zero calls to writer, preview and filesystem-write boundaries.
18. /workflow create remains separate and unchanged.
19. applyEligible === false.

For each item report:

* exact test file and full title;
* executable assertion;
* latest observed result;
* COVERED, PARTIAL, or GAP.

Do not claim coverage from source-text search alone.

Required repair proposal

Make no edits. Produce a proposed next repair scope containing:

* exact files that would need modification;
* whether each change is production, test, fixture, or cleanup;
* hunk-level behavioral intent;
* assertions that must be retained;
* new regression tests required;
* commands required for focused and final A/B validation;
* explicit files that must remain untouched.

If production repair would require a file outside the existing six production files, identify it as a scope-expansion request rather than assuming authorization.

Cleanup and immutability

Delete only the exact temporary root.

Then verify:

* git status --porcelain is byte-for-byte unchanged;
* all nine overlay hashes are unchanged;
* all protected dirty hashes are unchanged;
* candidate VSIX hash is unchanged;
* no Consumer, control-plane, Git, PR, CI, package, installation, or external state changed;
* Keep/Undo remains untouched;
* Phase A1 remains unstarted.

Final report

Provide:

1. Identity and isolation evidence.
2. Exact H/S/T/F command matrix.
3. Exact three-failure inventory.
4. Individual/order-dependence results.
5. Route and overlay-hunk trace.
6. Per-failure adjudication table.
7. Existing 19-item coverage matrix.
8. Minimal proposed repair scope.
9. Before/after immutability proof.
10. Explicit confirmation that no edit or external mutation occurred.

End with exactly one token:

LOCAL_PHASE_A0R2_TRIAGE_READY_FOR_BOUNDED_REPAIR
LOCAL_PHASE_A0R2_TRIAGE_INCONCLUSIVE
LOCAL_PHASE_A0R2_TRIAGE_BLOCKED
