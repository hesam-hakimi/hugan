TASK: HF1_V2_COMMIT_RECOVERY_AND_BUILD_EXACT_VSIX_0_3_147

WORKTREE
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

EXPECTED_BRANCH
recovery/extension-product-0.3.147

EXPECTED_PRECOMMIT_HEAD
b2e44c3a1a051aa7fa6008831d225bc06d22e847

OWNER AUTHORIZATION
I authorize:

1. Staging exactly the already-reviewed 97 product paths.
2. Creating one local commit on the recovery branch.
3. Running product:verify once from the committed tree.
4. Exporting the verified VSIX outside the Git repository.

I do not authorize push, merge, tag, release, installation, Runtime QA, reset,
clean, stash, branch deletion or modification of the original dirty worktree.

PRECOMMIT GATE

Verify before staging:

- current branch exactly matches the expected branch;
- HEAD matches EXPECTED_PRECOMMIT_HEAD;
- changed-path count is exactly 97;
- runtime files: 41;
- packaged resources: 8;
- tests/fixtures: 43;
- Phase H files: 2;
- package metadata: 2;
- product verification files: 1;
- governance files: 0;
- unexpected files: 0;
- package version: 0.3.147;
- staged files: 0.

Stop if any value differs.

STAGING

1. Generate the complete explicit list of the 97 reviewed paths.
2. Reject the list if it contains:
   - .github/**
   - .claude/**
   - scripts/agent-governance/**
   - temporary evidence;
   - build output;
   - *.vsix;
   - local environment files;
   - portfolio or unrelated documentation.
3. Stage paths using the explicit list.
4. Do not use broad `git add -A`, `git add .` or wildcard staging.
5. Verify:
   - staged count is 97;
   - unstaged product changes are 0;
   - staged diff exactly equals the reviewed precommit diff.
6. Run:

   git diff --cached --check

Do not rewrite or format files during staging.

COMMIT

If Git author identity is unavailable, stop and report it. Do not change global or
repository Git identity settings.

Create exactly one local commit with this message:

feat: recover ETL extension product baseline 0.3.147

Record:

- commit SHA;
- commit tree SHA;
- parent SHA;
- author;
- committed path count.

After commit, verify the recovery worktree is clean.

Do not amend an existing commit.

POST-COMMIT PRODUCT VERIFICATION

From the clean committed tree, run exactly once:

npm run product:verify

Do not rerun the canonical full-unit suite.

Require:

- exit code 0;
- package version 0.3.147;
- 66 archive entries;
- 54/54 required entries;
- 0 forbidden entries;
- all entries within the 8 allowed roots;
- no repository pollution.

EXACT ARTIFACT EXPORT

Use the VSIX produced by the successful post-commit product verification.

Copy it outside the Git repository to:

C:\repos\etl-extension\release-artifacts\0.3.147\

Use this filename:

databricks-etl-copilot-0.3.147-<short-commit-sha>.vsix

Do not place a VSIX inside either Git worktree.

Record:

- absolute artifact path;
- file size;
- SHA-256;
- archive entry count;
- package identity;
- package version.

Reopen and inspect the exported artifact to confirm it is byte-identical to the
verified temporary artifact.

FINAL INTEGRITY CHECK

Verify:

- recovery branch HEAD equals the new commit;
- recovery worktree is clean;
- original dirty worktree is unchanged;
- no staged or stash changes were created;
- no out/**, *.tsbuildinfo or *.vsix artifact leaked into the recovery worktree;
- no push, merge, tag, install or Runtime QA occurred.

FINAL REPORT

IDENTITY_GATE
PRECOMMIT_CHANGED_PATH_COUNT
STAGED_PATH_COUNT
UNEXPECTED_STAGED_PATHS
CACHED_DIFF_CHECK
COMMIT_CREATED
COMMIT_SHA
COMMIT_TREE_SHA
COMMIT_PARENT_SHA
COMMITTED_PATH_COUNT
WORKTREE_CLEAN_AFTER_COMMIT
PRODUCT_VERIFY_PASS
PACKAGE_VERSION
EXPORTED_VSIX_PATH
EXPORTED_VSIX_SIZE
EXPORTED_VSIX_SHA256
VSIX_ENTRY_COUNT
REQUIRED_PACKAGE_ENTRIES_PRESENT
FORBIDDEN_PACKAGE_ENTRIES_PRESENT
ORIGINAL_WORKTREE_UNCHANGED
PUSH_EXECUTED
INSTALL_EXECUTED
RUNTIME_QA_STARTED
READY_TO_INSTALL_LOCALLY

Expected terminal verdict:

PASS_READY_TO_INSTALL_LOCALLY

Stop without committing if the precommit gate differs from the reviewed 97-path
product change set.
