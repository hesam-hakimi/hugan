IMPLEMENT LOCAL PHASE A1B — SLICE 1 CANONICAL ETL ARTIFACT PATH/LAYOUT OWNERSHIP

You are implementing ONLY Slice 1 from the completed read-only architecture task:

LOCAL-PHASE-A1A-PATH-ARCHITECTURE-DESIGN-20260813-01

The A1A investigation is the authoritative design input for this task.

==================================================
PRIMARY OBJECTIVE
==================================================

Establish ONE canonical, deterministic owner for ETL artifact path/layout rules.

This slice is PARITY-ONLY.

Do NOT migrate existing producers yet.
Do NOT change runtime behavior yet.
Do NOT implement Slice 2 or later slices.

The purpose is to introduce and prove the canonical path/layout contract that later slices will delegate to.

Target architecture from A1A:

trusted evidence
→ lifecycle route
→ environment selection
→ structural artifact planning
→ canonical path manifest
→ collision/ownership inspection
→ preview
→ future apply

This task implements ONLY the canonical path/layout foundation required by that architecture.

==================================================
MANDATORY PRE-FLIGHT
==================================================

Before modifying anything:

1. Re-read the complete A1A design evidence available in the current session.

2. Verify repository identity:
   - repository root
   - origin
   - current branch
   - HEAD SHA
   - git status
   - staged files
   - worktrees

3. Reconcile the current pending review-card state.

The A1A report identified:
- nine pending AOR review-card files
- four protected dirty files
- previously authorized TrustedCreatePreviewService state

Do NOT modify, Keep, Undo, stage, revert, restore, clean, overwrite, or otherwise disturb those existing changes.

Record hashes before implementation.

If the repository state materially differs from the A1A starting state:
STOP and report the drift.

==================================================
SLICE 1 AUTHORIZED SCOPE
==================================================

Implement the canonical ETL artifact layout owner.

Expected new production files:

src/core/artifacts/layout/EtlArtifactLayout.ts

src/core/artifacts/layout/ArtifactPathNormalizer.ts

Expected new test file:

src/test/suite/etlArtifactLayoutParity.test.ts

You may adjust exact filenames only if repository conventions make these paths technically invalid.

If so:
STOP before implementation and explain why.

No other production files are authorized in this slice.

==================================================
DESIGN REQUIREMENTS
==================================================

EtlArtifactLayout must become the future single owner of deterministic ETL artifact path formulas.

It must provide pure path-planning functions for the artifact families identified in A1A, including as applicable:

- primary job config
- split EXTRACT config
- split LOAD config
- transformation SQL include files
- environment config CREATE path
- onboarding / registration artifact
- any deterministic artifact path already proven by repository evidence

IMPORTANT:

Do NOT invent paths for artifact families where A1A found no authoritative producer or contract.

Specifically unresolved items must remain unresolved and explicit, including where applicable:

- common/shared config path
- CSV / other declared outputs
- managed-ownership marker for ETL artifacts

Do not guess them.

==================================================
PARITY REQUIREMENT
==================================================

This slice MUST preserve existing path behavior byte-for-byte/string-for-string for every path formula that is already authoritative enough to reproduce.

The new layout owner must encode existing behavior.

Existing producers must NOT delegate to it yet.

Therefore:

CURRENT PRODUCERS
        │
        │ existing behavior unchanged
        ▼
existing paths

AND IN PARALLEL:

same grounded inputs
        │
        ▼
EtlArtifactLayout
        │
        ▼
canonical candidate paths

Tests must prove parity between these wherever authoritative existing behavior exists.

If two existing producers disagree on a formula:

DO NOT silently choose one.

Instead:

1. identify the conflicting producers,
2. preserve both observed formulas in evidence,
3. classify the conflict,
4. make the canonical function require an explicit contract decision OR represent the unresolved state safely,
5. add a test proving that the conflict cannot silently resolve through guessing.

A1A specifically found disagreement around job-config and env-config formulas. Treat these as contract conflicts, not refactoring trivia.

==================================================
PATH NORMALIZATION
==================================================

ArtifactPathNormalizer must define deterministic normalization/containment primitives required by the future manifest.

Design for both Linux and Windows path semantics where applicable.

Cover at minimum:

- workspace-relative paths
- separator normalization
- "." segments
- ".." traversal rejection
- absolute path rejection where a relative artifact path is required
- Windows drive-letter behavior
- UNC paths
- mixed separators
- case-folded comparison key where needed for collision detection
- canonical destination resolution beneath a selected workspace root
- containment verification
- symlink/realpath boundary considerations where filesystem evidence is required

IMPORTANT:

Do not perform writes.

Pure normalization functions should remain filesystem-independent.

If realpath/symlink verification requires filesystem access, separate that concern cleanly from pure normalization rather than hiding I/O inside path formula functions.

==================================================
ARCHITECTURAL BOUNDARIES
==================================================

The new layout module must be a LEAF dependency.

It may depend on stable types/utilities.

It must NOT depend on:

- chat/v3
- TrustedCreatePreviewService
- AgentMessageRouter
- AgentActionExecutor
- RenderingChain
- ArtifactGenerationPipeline orchestration
- RepoWriter
- ArtifactPatchPlanner
- UI
- Copilot runtime orchestration

Higher-level components will eventually depend on the layout owner, not vice versa.

Check for dependency cycles.

==================================================
NO AI / NO NONDETERMINISM
==================================================

Canonical path calculation must be deterministic.

It must NOT depend on:

- LLM output
- model ranking
- current time
- Date.now()
- random values
- ambient active editor
- ambient workspace selection
- Databricks calls
- network calls

All required inputs must be explicit function parameters.

==================================================
NO WRITES / NO SIDE EFFECTS
==================================================

Slice 1 is path-contract foundation only.

The new production code must not:

- create directories
- write files
- modify files
- call RepoWriter.writeArtifacts
- call NewArtifactWriter.writeFiles
- stage Git changes
- commit
- push
- package
- install
- modify a consumer workspace
- contact external systems

==================================================
TEST REQUIREMENTS
==================================================

Create focused tests for the new canonical layout and normalizer.

At minimum cover:

1. deterministic output for identical inputs
2. primary job-config path parity
3. split EXTRACT path parity
4. split LOAD path parity
5. transformation include path parity
6. environment CREATE path parity where contract is authoritative
7. onboarding path parity
8. unresolved/conflicting formulas fail explicitly rather than guessing
9. POSIX separator normalization
10. Windows separator normalization
11. mixed separators
12. "." normalization
13. ".." traversal rejection
14. absolute-path rejection
15. Windows drive-letter escape rejection
16. UNC escape rejection
17. prefix-confusion containment:
    C:\foo must not contain C:\foobar
18. case-folded collision-key behavior
19. duplicate normalized destination detection primitives
20. no filesystem writes
21. no AI/model dependency
22. no ambient workspace dependency
23. stable output across repeated executions

Where practical, compare the new canonical functions against the existing producer formulas using identical grounded inputs.

Do NOT modify existing producers merely to make tests easier.

==================================================
REGRESSION SAFETY
==================================================

Run the smallest relevant existing test suites first.

Then run the broader appropriate extension tests permitted by the environment.

Pay special attention to the three regressions identified in A1A:

- phase6WriteDeployRun.test.ts expected trusted_preview_validated
- goldenCorpusRunner.test.ts acceptance behavior
- goldenCorpusRunner.test.ts ABESS aiFirst.acceptance === true

Use the A/B methodology defined in A1A where practical to distinguish:

PRE-EXISTING failures
from
NEW REGRESSIONS.

Do not “fix” unrelated failures in this slice.

==================================================
SCOPE ESCALATION RULE
==================================================

If implementation requires modifying ANY existing production file:

STOP.

Do not expand scope automatically.

Report:

SCOPE_EXPANSION_REQUIRED

and include:

- exact file
- exact symbol
- why Slice 1 cannot be completed without it
- minimal proposed change
- whether it belongs to Slice 1 or should wait for Slice 2

Do not make that modification without explicit authorization.

==================================================
GIT / REVIEW-CARD SAFETY
==================================================

Do not touch the existing pending AOR review-card files.

Do not press Keep or Undo.

Do not stage anything.

Do not commit.

Do not push.

Do not create or modify PRs.

Do not switch branches.

Do not rebase or merge.

Do not build/package/install a VSIX.

Do not modify consumer repositories.

At the end, prove the original pending files are byte-identical to their starting hashes.

==================================================
FINAL REPORT
==================================================

Return a concise but evidence-rich report containing:

1. PASS / FAIL / BLOCKED / SCOPE_EXPANSION_REQUIRED

2. Repository identity:
   - root
   - branch
   - starting HEAD
   - ending HEAD

3. Existing pending-file integrity:
   - before/after hashes
   - confirmation untouched

4. Exact new files created

5. Canonical path functions implemented

6. Path formulas represented

7. Any formula conflicts intentionally left unresolved

8. Normalization and containment rules implemented

9. Dependency-cycle result

10. Determinism / no-AI / no-I/O evidence

11. Tests executed with exact pass/fail counts

12. Classification of any failures:
    - pre-existing
    - introduced
    - environment
    - unresolved

13. Confirmation:
    - no existing production files modified
    - no consumer files modified
    - no package/VSIX operation
    - no commit/push/PR action
    - no external action

14. Recommendation:
    READY_FOR_SLICE_1_AUDIT
    or
    NOT_READY_FOR_SLICE_1_AUDIT

Do NOT start Slice 2.

Do NOT propose implementation of Slice 2 beyond identifying evidence needed for the next decision.
