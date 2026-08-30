TASK: HF1_V2_REMOVE_UNRELATED_GOVERNANCE_TRANSFERS

WORKTREE
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

EXPECTED_BRANCH
recovery/extension-product-0.3.147

OBJECTIVE
Remove exactly the 11 unrelated governance-transfer changes identified by the
owner product review, then run the minimal product verification once.

This is a mechanical correction, not a redesign or governance task.

AUTHORIZED PATHS

.github/instructions/business-context.instructions.md
.github/instructions/change-safety.instructions.md
.github/instructions/execution-recovery.instructions.md
.github/instructions/workflow-asset-boundaries.instructions.md
.github/instructions/workflow-coherence.instructions.md
.github/prompts/01-implement-tool-aware-agent.prompt.md
.github/prompts/build.prompt.md
.github/prompts/investigate.prompt.md
.github/prompts/plan-change.prompt.md
.github/prompts/verify-change.prompt.md
.github/prompts/verify-live-flow.prompt.md

No other path is authorized.

PROCEDURE

1. Verify repository root and branch.
2. Record git status and diff for the 11 paths.
3. For each path:
   - if absent at the recovery base HEAD, remove it from this recovery worktree;
   - if present at the recovery base HEAD, restore exactly its base-HEAD content.
4. Do not modify the original dirty worktree.
5. Do not modify any runtime, test, fixture, resource, package.json, Phase H or
   product-verify file.
6. Verify the 11 paths no longer differ from the base HEAD.
7. Confirm the recovery diff now contains:
   - 41 runtime files;
   - 8 packaged resource files;
   - 43 test/fixture files;
   - 2 Phase H files;
   - 2 package metadata files;
   - 1 product-verification file;
   - 0 governance files;
   - 0 unexpected files.
8. Run exactly once:

   npm run product:verify

9. Do not rerun the full-unit suite.
10. Do not commit, stage, push, package into the repository, install or start
    Runtime QA.

FINAL REPORT

IDENTITY_GATE
REMOVED_OR_RESTORED_PATHS
UNAUTHORIZED_CHANGED_PATHS
TOTAL_CHANGED_PATHS
GOVERNANCE_FILES_PRESENT
UNEXPECTED_FILES_PRESENT
PACKAGE_JSON_UNCHANGED_BY_THIS_TASK
PRODUCT_FILES_UNCHANGED_BY_THIS_TASK
PRODUCT_VERIFY_PASS
PACKAGE_VERSION
TEMP_VSIX_SHA256
REQUIRED_PACKAGE_ENTRIES_PRESENT
FORBIDDEN_PACKAGE_ENTRIES_PRESENT
READY_TO_COMMIT_RECOVERY_BRANCH

Expected terminal verdict:

PASS_READY_TO_COMMIT_RECOVERY_BRANCH

Stop immediately if any correction requires touching a path outside the exact
11-path authorization.
