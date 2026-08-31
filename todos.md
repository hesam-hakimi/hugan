Perform the final read-only W1 acceptance gate.

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required branch:

fix/workspace-write-completion-0.3.148

Required HEAD:

64706129e0d1054ea615e150b28dd623fb3c629e

Do not repair or edit anything in this task.

Preflight

Confirm:

* Branch and HEAD match.
* Nothing is staged.
* git status --short contains exactly these 12 paths:

Modified:

* src/chat/DeployCoordinator.ts
* src/chat/WriteCoordinator.ts
* src/core/trusted/WriteAuthorization.ts
* src/test/helpers/mintTestWriteAuthorization.ts
* src/test/suite/onboardingWriteApproval.test.ts
* src/test/testPatterns.ts
* src/tools/EtlActionToolService.ts
* src/tools/TrustedWriteApprovalStore.ts
* src/writers/RepoWriter.ts

Untracked:

* src/core/artifacts/ArtifactDestinationInventory.ts
* src/core/artifacts/WorkspaceDestinationProbe.ts
* src/test/suite/workspaceWriteCollision.test.ts

Run git diff --check and record a content hash for all 12 files.

If preflight differs, stop.

Phase A — Static review

Inspect the complete diff and provide file-and-line evidence for every conclusion.

1. W1-only scope

Verify that:

* Every production change is required for destination inventory, collision classification, approval display/checksum, or final pre-write revalidation.
* No package-version, Repair 13, atomic multi-file apply, managed ownership, CI, or unrelated behavior was changed.

2. Fail-closed no-workspace behavior

Verify that:

* An undefined workspace root, missing workspace, containment failure, or probe error cannot be interpreted as “destination absent” or CREATE for a real write.
* Every real write entry point fails before approval or writing when the workspace cannot be safely resolved.
* No direct writer path bypasses the new guard.

The new probe returning “nothing exists” when no workspace is available is acceptable only if a separate mandatory guard proves that every real write stops before approval and before filesystem mutation.

3. Canonical inventory completeness

Verify that:

* The same production inventory drives collision checking and actual writes.
* Independently enumerate every category written by RepoWriter.writeArtifacts and map it to the inventory, including:
    * primary job config
    * environment configs
    * includes
    * every additionalJobConfigs entry
* Search for any writable category or side-write outside the inventory.
* Tests do not prove completeness by deriving both expected and actual values from the same helper.

4. Classification and duplicate behavior

Verify that:

* Missing destination → CREATE
* Existing destination with identical intended bytes → UNCHANGED
* Existing destination with different intended bytes → OVERWRITE
* Conflicting duplicate destinations fail before approval and before writing.
* Identical duplicates collapse deterministically.
* Probe ambiguity, permission errors, or unsupported destination types fail closed.

5. Path identity and containment

Verify that:

* Inventory, checksum, probe, revalidation, and writer use the same destination identity.
* Windows case-only aliases, slash variants, dot segments, and drive-letter variants cannot be treated as different destinations.
* Existing physical containment still blocks absolute paths, traversal, cross-root access, junction or symlink escapes, and dangling links.
* A path normalization or probe error never becomes CREATE.

6. Explicit trusted approval

Verify that:

* CREATE, OVERWRITE, and UNCHANGED are rendered separately.
* Every path appears in the correct section.
* Disposition, canonical path, intended bytes or hash, and relevant metadata are bound into the existing trusted approval checksum.
* No second approval mechanism was introduced.
* UNCHANGED files are not rewritten.

7. Drift and TOCTOU boundary

Verify that:

* The complete approved inventory is re-probed after approval and immediately before the first filesystem mutation.
* Identity, existence/disposition, destination type or link state, and relevant existing-content evidence are compared.
* Any mismatch aborts before any file is written.
* The approval cannot be replayed after rejection or drift.
* Report every await or side effect between final revalidation and the first write.
* Do not claim that W1 solves the residual operating-system race or multi-file rollback.

8. Test integrity

Verify that:

* No assertion was removed or weakened merely to make tests pass.
* No skip, only, swallowed error, or broader expectation was introduced.
* Changed CREATE-to-OVERWRITE expectations are backed by fixtures that truly pre-create those destinations.
* testPatterns.ts only adds the new headless suite.
* GUI-dependent writeFlow.test.ts remains excluded.

Hard blockers

Return W1_ACCEPTANCE_BLOCKED and do not run tests if any of these is found:

* Fail-open no-workspace or probe-error behavior
* Missing inventory category or direct-write bypass
* Incorrect CREATE/OVERWRITE/UNCHANGED classification
* Windows path aliases treated as different destinations
* Approval does not display and checksum-bind overwrite state
* Revalidation happens after a write or checks insufficient state
* Weakened or tautological tests
* W1 scope expansion

Phase B — Final execution

Only if Phase A has no blocker, run exactly once each:

npm run compile

npm run test:unit

Do not rerun focused tests. Existing post-fix evidence already records 346 passing workspace-write tests.

Expected unit result:

* 2326 passing
* 5 pending
* 5 failing
* Exit code 1

The only permitted failures are:

1. The same three known failures in copilotWorkflowCustomization.test.js:
    * missing deploy-v3 tool-context prompt
    * missing frontmatter name
    * module AGENT.md files
2. Exactly two EvalGating freshness failures that only report stale committed evaluation evidence caused by the intentional W1 source changes.

Acceptance requires:

* Compile exits 0.
* All 17 workspaceWriteCollision tests execute and pass.
* No workspace-write test fails.
* Totals and the five allowed failures match exactly.
* No additional failure appears.
* Starting and ending HEAD match.
* All 12 before/after content hashes match.
* Final Git status exactly matches preflight.

Return exactly one verdict:

W1_ACCEPTANCE_PASS_EVAL_BASELINE_REFRESH_REQUIRED

or:

W1_ACCEPTANCE_BLOCKED

Report:

* Static-review findings with file and line references
* Commands, exit codes, and elapsed times
* Passing, pending, and failing totals
* Full names of every failure
* Result of all 17 new tests
* Before/after source-state comparison
* Final Git status
* Final verdict

Restrictions:

* Do not edit, format, repair, stage, commit, or push.
* Do not refresh evaluation baselines.
* Do not rerun any command.
* Do not change the package version.
* Do not run F5, packaging, installed QA, or the external harness.
* Stop after reporting.
