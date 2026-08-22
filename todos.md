TASK: LOCAL_HOTFIX_HF1_V2_FINAL_RELEASE_REAUDIT

Perform a final, independent, adversarial, READ-ONLY release re-audit of the current HF1 V2 candidate after Repair 6.

This is NOT an implementation task.
DO NOT edit, create, delete, rename, stage, commit, revert, Keep, package-install, dependency-install, or otherwise mutate source/repository state.

Treat all prior implementation reports as UNTRUSTED INPUT.
Re-derive conclusions from the current source tree, Git state, generated output, test results, and QA VSIX contents.

Primary objective:
Determine whether the current candidate is genuinely safe to commit and release, or whether any release-blocking defect still exists.

==================================================
1. REPOSITORY / SCOPE INTEGRITY
==================================================

Verify independently:

- current repository root
- current branch
- current HEAD
- origin
- staged file count
- complete modified/untracked path inventory
- no unexpected files were modified by Repair 6
- no protected/no-touch areas were modified
- Repair 6 changed only the authorized paths plus the explicitly authorized new test file
- no consumer repository was modified
- no etl-framework-adb source/runtime dependency was introduced
- no Git mutation occurred during this audit

Capture hashes/state at audit start and end and prove this audit itself changed nothing.

==================================================
2. COMPLETE CONSUMER WRITE-ROUTE ENUMERATION
==================================================

Do NOT assume the previously listed write routes are complete.

Enumerate all reachable production code paths that can perform any real consumer-workspace filesystem mutation, including:

- writeFile
- createDirectory
- rename
- delete
- copy
- backup
- patch
- create
- overwrite
- any helper wrapping these operations

Classify every route as one of:

A. TRUSTED_CONSUMER_WRITE
B. INTERNAL_NON_CONSUMER_WRITE
C. TEST_ONLY
D. DEAD_OR_UNREACHABLE
E. LEGACY / DEFERRED

For every TRUSTED_CONSUMER_WRITE route prove all three:

1. trusted authorization or approved lifecycle exists where applicable
2. canonical logical consumer root is used
3. PHYSICAL containment is verified immediately before filesystem mutation

Do not accept lexical path checking alone.

==================================================
3. PHYSICAL CONTAINMENT ADVERSARIAL RECHECK
==================================================

Re-audit the Repair 6 containment model from source.

Specifically verify protection against:

- ../ traversal
- absolute path escape
- drive-qualified path escape
- sibling-root escape
- symlink escape
- junction/reparse-point escape
- dangling final-link escape
- dangling ancestor-link escape
- path replacement between preview and write
- TOCTOU after approval
- hard-link based escape where relevant
- POSIX case-sensitive sibling paths
- Windows case-insensitive equivalent paths

Confirm the hardened physical resolver is applied BEFORE any directory creation or file mutation.

Pay special attention to:

- RepoWriter.writeArtifacts
- UnitTestCoordinator
- ExplainCoordinator
- NewArtifactWriter
- ArtifactPatchApplier
- RepoContextInitializer
- any route newly discovered during this audit

If any consumer write path reaches the filesystem with only lexical containment, classify it as RELEASE BLOCKING.

==================================================
4. AUTHORIZATION / PREVIEW / WRITE INVARIANCE
==================================================

Verify the following independently:

preview
→ immutable/frozen artifact identity
→ explicit approval
→ re-validation
→ one-time authorization
→ physical containment immediately before mutation
→ write
→ consumed/failed terminal state

Check:

- no approval reuse
- no forged approval
- no stale approval
- no wrong consumerRoot
- no wrong target/decision
- no changed relPath
- no changed artifact type
- no changed bytes/content hash
- no second write from the same authorization
- no route can bypass the trusted approval model using a plain boolean or conversation state alone within the release-relevant fresh-consumer path

Also verify that the manifest truthfully describes files actually rewritten versus unchanged.

==================================================
5. SINGLE-FOLDER / MULTI-ROOT QA MODEL
==================================================

Re-prove:

- zero folders => BLOCKED
- one valid fresh consumer => CREATE_NEW_JOB
- one valid existing consumer => UPDATE_EXISTING_REPO
- prohibited/reference/source/extension roots => BLOCKED
- sample_repo => BLOCKED
- multiple roots without explicit safe selection => AMBIGUOUS/BLOCKED
- no workspaceFolders[0] fallback survives in a release-relevant consumer write path
- QA does NOT require etl-framework-adb to be opened
- QA does NOT require a framework source checkout beside the consumer repo

Check both runtime behavior and tests.

==================================================
6. FRAMEWORK CONTRACT / ORACLE REGRESSION CHECK
==================================================

Confirm Repair 6 did NOT weaken:

- trusted framework-definition resolution
- configured_source > workspace_source > packaged_contract precedence
- fail-closed behavior
- Oracle delivery-control validation
- distinction between:
  FRAMEWORK_DEFINITION_UNAVAILABLE
  and
  ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING
- packaged-contract identity/version/integrity validation
- installed VSIX resource resolution

Do not redesign framework binding in this task.
Only report a finding if Repair 6 introduced a regression.

==================================================
7. PACKAGE HYGIENE / QA VSIX
==================================================

Perform an independent package-content audit.

Verify that the final QA VSIX excludes at any depth:

- .tmp/**
- nested .git/**
- *.tsbuildinfo
- *.tsbuildinfo.*
- logs
- test output
- test fixtures
- source-only QA artifacts
- unrelated repositories
- previous VSIX files
- pack files
- large scratch outputs
- credentials/secrets
- developer-machine paths

Verify required runtime content is present, especially:

- compiled extension runtime
- STTM runtime
- package.json
- resources/copilot/**
- resources/prompts/**
- resources/framework/**
- required media/scripts/workflow assets

Check package file count and compressed/uncompressed size for plausibility.

Do NOT manually edit the ZIP/VSIX.
The package must be correct from source/package rules alone.

==================================================
8. TEST QUALITY / FALSE-GREEN CHECK
==================================================

Do not only inspect pass counts.

Review whether Repair 6 tests genuinely discriminate regressions.

Confirm tests would fail if we reintroduced:

- lexical-only containment
- workspaceFolders[0] fallback
- write-before-containment
- write-before-approval
- approval replay
- manifest drift
- sample_repo accepted as consumer
- symlink/junction escape
- dangling-link escape
- POSIX case-folding defect
- package inclusion of .tmp
- package inclusion of nested .git
- package inclusion of .tsbuildinfo

Identify any test that is vacuous, mock-only where a real filesystem test is required, or proves source text instead of runtime behavior.

==================================================
9. HISTORICAL FIVE FAILURES
==================================================

Independently confirm the remaining full-suite failures are exactly the pre-existing historical five:

- 2 EvalGating baseline failures
- 3 Copilot workflow customization failures

Confirm none is caused by HF1 V2 / Repair 5 / Repair 6.

Do NOT repair them in this task.

==================================================
10. DEFERRED DEBT
==================================================

Re-check but DO NOT modify deferred/non-blocking areas, including:

- legacy Copilot workflow customization authorization model
- repo-learning / knowledge raw filesystem writers
- remaining low-level path-normalization/folder-name heuristics
- conversational route precedence UX debt
- framework-binding long-lived-session debt

For each, classify:

- release blocker
- bounded non-blocking debt
- out of scope
- needs separate follow-up

Do not silently promote or suppress severity.

==================================================
11. EXECUTION
==================================================

Use already-installed dependencies only.

Run, where available:

- compile
- lint
- focused Repair 5 / Repair 6 tests
- physical containment tests
- relevant write-authorization tests
- full unit suite
- QA VSIX package build
- VSIX content verification

Do NOT install/download dependencies.

If a command cannot run, state that clearly.
Do not infer PASS from source inspection alone.

==================================================
12. FINAL DECISION
==================================================

Return a concise final report with:

A. Repository identity
B. Changed-path inventory
C. Write-route inventory
D. Physical-containment verdict
E. Authorization/TOCTOU verdict
F. Single-folder QA verdict
G. Framework/Oracle regression verdict
H. Package-hygiene verdict
I. Test-quality verdict
J. Historical-five confirmation
K. Remaining debts
L. Exact blockers, if any

Then print EXACTLY one of these final decisions:

SAFE_TO_COMMIT_HF1_V2: YES
SAFE_TO_BUILD_RELEASE_VSIX: YES
SAFE_TO_RELEASE_HF1_V2: YES

OR, if anything release-blocking remains:

SAFE_TO_COMMIT_HF1_V2: NO
SAFE_TO_BUILD_RELEASE_VSIX: NO
SAFE_TO_RELEASE_HF1_V2: NO

If NO, list the minimum exact file/function/test scope needed for the next repair.

Important:
Do not modify anything during this audit.
Do not fix findings.
Do not regenerate baselines.
Do not touch .github/**, resources/prompts/**, AGENT.md/AGENTS.md, package-lock.json, consumer repositories, or etl-framework-adb.
Do not commit, push, Keep, revert, or install the VSIX.

Final marker:
LOCAL_HOTFIX_HF1_V2_FINAL_RELEASE_REAUDIT_COMPLETE
