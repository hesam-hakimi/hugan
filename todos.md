/verify-change

LOCAL PHASE A0V — ISOLATED EXECUTABLE VERIFICATION

Phase A0 changes are still pending in the current Agent review card. Do not click Keep or Undo, and do not modify the Phase A0 implementation during this task.

This is a verification-only task. Do not begin Phase A1.

1. Restrictions

Do not:

* edit, reformat, repair, regenerate, or delete any real source/test file;
* stage, commit, push, merge, rebase, switch branches, or alter Git state;
* edit Draft PR #7 or perform any CI/CD action;
* change package version, lockfiles, snapshots, baselines, or tracked out/**;
* build, package, install, uninstall, or replace a VSIX;
* change the installed Extension;
* modify any real Consumer workspace;
* invoke RepoWriter, NewArtifactWriter, writeArtifacts, Apply, approval, deployment, publication, registration, Databricks, ADF, or SQL Server operations;
* use the dirty worktree package.json;
* copy any protected user-owned dirty file into the validation snapshot.

2. Establish the real-worktree baseline

Report:

* repository root and origin;
* branch and exact HEAD;
* staged, unstaged, and untracked state;
* exact eight Phase A0 file paths and SHA-256 hashes;
* hashes of all protected dirty files;
* committed HEAD:package.json version;
* dirty worktree package.json version;
* candidate and installed VSIX identity, read-only.

Expected:

* repository: TD-Universe/agentic_etl
* branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* committed package version: 0.3.139
* dirty user-owned package version: 0.3.128

Protected dirty files:

* .tsbuildinfo.test
* package.json
* CopilotAssetCatalog.ts
* EtlActionToolService.ts

Expected Phase A0 files:

1. TrustedPlanningEvidenceService.ts
2. EtlAgent.ts
3. AgentMessageRouter.ts
4. AgentActionExecutor.ts
5. ResponseComposer.ts
6. index.ts
7. TrustedPlanningEvidenceService.test.ts
8. testPatterns.ts

Resolve and report their exact repository-relative paths.

Stop if:

* repository, branch, or HEAD differs;
* exactly eight Phase A0 files cannot be isolated;
* a Phase A0 file overlaps a protected file;
* the implementation depends on an unapproved dirty file.

3. Create an isolated validation snapshot

Create a unique directory under the OS temporary directory, outside all repository and VS Code workspace roots.

Populate it using the committed tree at HEAD through a read-only method equivalent to:

git archive HEAD

Do not use git clone, git worktree add, or copy the entire dirty worktree.

Overlay exactly the eight Phase A0 files from the current worktree, preserving their repository-relative paths. Overlay no other file.

Verify:

* snapshot package.json is committed version 0.3.139;
* the eight overlay hashes match the pending Phase A0 files;
* protected dirty files came from HEAD and not the worktree;
* no real out/**, node_modules, VSIX, cache, or Consumer file was copied.

If compilation requires a protected dirty file, stop with:

PROTECTED_DIRTY_DEPENDENCY_DETECTED

Do not copy that dependency.

4. Install dependencies only inside the snapshot

Dependency installation is explicitly authorized only inside this temporary snapshot.

If the committed lockfile exists, run the repository-supported equivalent of:

npm ci --include=dev --no-audit --no-fund

Do not install globally or modify dependencies in the real repository.

Use only binaries from the snapshot-local node_modules/.bin. Do not perform interactive or unpinned npx installation.

All compiled output, .tsbuildinfo, caches, and test output must remain inside the snapshot.

5. Execute validation

Inspect the committed test scripts and runner, then run:

1. TypeScript compile/type-check;
2. the focused TrustedPlanningEvidenceService tests;
3. directly affected routing and containment tests;
4. the Phase A0 suite registered through testPatterns.ts.

If focused selection is unavailable, a broader unit suite may run only inside the snapshot.

For every command report:

* working directory;
* exact command;
* exit code;
* passing, failing, pending/skipped, and total counts;
* complete relevant failure diagnostics.

Do not change implementation or tests if anything fails.

6. Executable assertions required

Executable tests—not only source search—must verify:

* explicit workspace selection retains provenance;
* ambiguous multi-root selection fails closed;
* process.cwd() is never an implicit Consumer target;
* Extension-source, installation, external and traversal targets are rejected;
* explicit empty-root initialization is distinguished from inferred emptiness;
* contained STTM identity and SHA-256 are stable;
* missing/external STTM returns structured blockers;
* no sample fallback occurs;
* incomplete mandatory evidence prevents trusted preview;
* applyEligible is always false;
* direct /create receives evidence before AgentActionExecutor;
* /workflow create remains separate workflow-asset setup;
* RepoWriter, NewArtifactWriter, writeArtifacts, Apply and filesystem writers receive zero calls.

Map every Phase A0 requirement to:

* test name;
* executed/not executed;
* pass/fail;
* evidence.

Do not report an assertion as passed if it was only statically inspected.

7. Confirm real-worktree immutability

After testing, prove:

* git status --porcelain is byte-for-byte unchanged from baseline;
* staged state is unchanged;
* all eight Phase A0 file hashes are unchanged;
* all four protected dirty-file hashes are unchanged;
* .github/**, AGENTS.md, workflow/**, and COPY_ORDER.md are unchanged;
* candidate VSIX is unchanged;
* no real Consumer workspace was touched;
* no untracked file was created in the real repository.

Capture results before safely removing only the exact validated temporary directory.

8. Final result

Do not begin Phase A1.

Return:

1. baseline identity;
2. exact eight overlay files;
3. temporary snapshot construction evidence;
4. dependency-installation result;
5. all compile/test commands and results;
6. executable assertions proven;
7. assertions still supported only statically;
8. failures or remaining gaps;
9. before/after worktree and protected-file evidence;
10. confirmation that installed/candidate VSIX 0.3.139 is pre-A0 content and was not changed.

Finish with exactly one:

LOCAL_PHASE_A0_ISOLATED_EXECUTABLE_TESTS_PASS

or:

LOCAL_PHASE_A0_ISOLATED_EXECUTABLE_TESTS_FAIL

or:

LOCAL_PHASE_A0_ISOLATED_EXECUTABLE_TESTS_BLOCKED
