TASK: LOCAL_HOTFIX_HF1_V2_FINAL_RELEASE_REAUDIT_AFTER_REPAIR_7

This is an INDEPENDENT FINAL RELEASE RE-AUDIT.

Do NOT modify source files.
Do NOT fix findings.
Do NOT commit.
Do NOT push.
Do NOT install the VSIX.
Do NOT touch any consumer repository.
Do NOT touch etl-framework-adb.
Do NOT modify .github/**, resources/prompts/**, AGENT.md, AGENTS.md,
package-lock.json, historical Phase-H baselines, or framework/Oracle contracts.

Treat all prior Repair-5, Repair-6, and Repair-7 reports as UNTRUSTED CLAIMS.
Verify the current working tree independently from live source and executed evidence.

Primary objective:

Determine whether the current HF1 V2 candidate is actually safe to:

1. build a fresh QA VSIX,
2. verify that fresh VSIX,
3. commit the hotfix candidate,
4. proceed toward release testing.

==================================================
A. REPOSITORY / SCOPE INTEGRITY
==================================================

Independently capture:

- repository root
- branch
- HEAD
- origin
- git status
- staged files
- tracked modified files
- untracked files
- complete changed-path inventory

Confirm no unauthorized change exists in:

- consumer repositories
- etl-framework-adb
- .github/**
- resources/prompts/**
- AGENT.md / AGENTS.md
- package-lock.json
- historical Phase-H baseline files
- framework/Oracle contracts

Do not assume the reported 12-file Repair-7 scope is correct.
Derive it from the working tree.

==================================================
B. ENUMERATE ALL LIVE CONSUMER-WORKSPACE WRITE ROUTES
==================================================

Do not start from a fixed list.

Search production source for every reachable filesystem mutation that can
write/create/delete/move/rename consumer-workspace content.

Include at minimum:

- workspace.fs.writeFile
- workspace.fs.delete
- workspace.fs.createDirectory
- fs.writeFile / writeFileSync
- fs.mkdir / mkdirSync
- fs.rename
- fs.copyFile
- fs.rm / unlink
- wrapper/helper methods that ultimately perform these operations

For each reachable route classify:

- TRUSTED_CONSUMER_WRITE
- INTERNAL_NON_CONSUMER_WRITE
- READ_ONLY
- TEST_ONLY
- DEAD_OR_UNREACHABLE
- LEGACY/DEFERRED

For every TRUSTED_CONSUMER_WRITE prove all three:

1. trusted authorization / approval semantics where applicable
2. canonical logical consumer root
3. physical containment immediately before filesystem mutation

The physical containment proof must cover:

- ../ traversal
- absolute path
- drive-qualified path
- sibling-root escape
- symlink/junction/reparse-point escape
- dangling final symlink
- linked ancestor escape
- hard-link escape where relevant
- POSIX case-sensitive behavior
- Windows case-insensitive behavior
- TOCTOU path replacement between preview/approval and write

If ANY live consumer write route reaches mutation with lexical-only
containment, classify it RELEASE BLOCKING.

==================================================
C. REPAIR-7 SHARED PRIMITIVE AUDIT
==================================================

Inspect the new shared physical-containment primitive independently.

Confirm:

- no policy-specific rules are embedded in it
- no .github-specific policy is embedded in it
- nearest-existing-ancestor discovery is lstat-aware
- dangling links cannot be silently skipped
- realpath/native canonicalization is used appropriately
- POSIX case is preserved
- Windows comparison is case-insensitive
- sibling-prefix tricks are rejected
- hard-link handling matches the intended contract
- mutations happen only after containment succeeds

Then independently verify every Repair-7 consumer of this primitive.

Do not rely on source-text presence alone.
Trace the actual runtime write path.

==================================================
D. AUTHORIZATION / PREVIEW / WRITE INVARIANCE
==================================================

Verify that routes using WriteAuthorization still reject:

- forged authorization
- stale authorization
- expired authorization
- consumed authorization
- wrong consumerRoot
- wrong target
- wrong targetDecision
- changed artifact types
- changed relative path
- changed bytes/content hash
- replay / concurrent reuse

Confirm a failed physical-containment check cannot mark an approval consumed
as successful.

For legacy/deferred customization routes that do not use WriteAuthorization,
classify them explicitly and determine whether any remains a release blocker
for the current fresh-consumer QA path.

==================================================
E. STANDARD TEST-SUITE INCLUSION / FALSE-GREEN DEFENSE
==================================================

Verify that the new containment suites actually run under the normal unit
command.

Specifically verify inclusion of:

- physicalWriteContainment.test
- artifactReuseConversation.test
- repoContextInit.test

Inspect PURE_UNIT_TEST_PATTERNS / equivalent runner configuration.

Run a controlled mutation probe only against generated build output or another
fully reversible non-source artifact:

Temporarily neutralize the shared physical-containment decision.

Expected result:
relevant containment tests MUST fail.

Restore the generated artifact afterward and prove source bytes did not change.

If tests remain green with the guard neutralized, classify TEST_FALSE_GREEN
and fail the release audit.

==================================================
F. VALIDATION
==================================================

Using already-installed dependencies only, run:

- compile
- lint
- focused physical-containment tests
- Repair-5 regression suites
- Repair-6 regression suites
- Repair-7 customization-route suites
- WriteAuthorization suites
- onboarding approval suites
- repo-writer workspace-selection suites
- RepoContext suites
- full unit suite

The five previously identified historical failures may remain only if they are
independently proven unchanged and unrelated.

Any additional failure is a release blocker.

==================================================
G. BUILD A FRESH QA VSIX
==================================================

This step MUST use the current post-Repair-7 source.

Do not reuse:
etl-hf1-v2-repair6-qa.vsix
or any other pre-Repair-7 package.

Build exactly one fresh QA VSIX using the repository's normal packaging
mechanism and already-installed dependencies.

Do not install it.

Record:

- exact filename
- SHA-256
- file count
- compressed size
- uncompressed size

==================================================
H. VERIFY THE FRESH VSIX
==================================================

Run the repository's VSIX verification against the newly-created package.

Independently inspect package contents.

Confirm required runtime content exists and forbidden content is absent.

At minimum verify absence of:

- .tmp/**
- nested .git/**
- *.tsbuildinfo and *.tsbuildinfo.*
- node_modules/**
- source test trees
- out/test/**
- docs/eval/**
- .vscode-test/**
- *.log
- nested .vsix
- unrelated repositories
- developer-machine absolute paths
- credentials/secrets
- local scratch repositories

Also check for unexpected:

- *.code-workspace
- scripts/**
- workflow/**

If such maintainer-only files are shipped, determine whether they are required
runtime assets. Do not silently accept them.

Confirm package provenance:
the packaged JS/runtime files must correspond to the current source/build, not
the pre-Repair-7 build.

==================================================
I. CLEAN BUILD REPRODUCIBILITY
==================================================

If possible without downloads:

- remove/regenerate only authorized generated build output
- rebuild
- rebuild the QA VSIX
- compare the resulting package deterministically

Report whether package bytes or content manifests are reproducible.

Do not modify source to force reproducibility.

==================================================
J. FINAL DECISION
==================================================

Return a severity-ranked finding table:

CRITICAL
HIGH
MEDIUM
LOW
INFO

For every finding state:

- exact file
- exact function / route
- reachability
- normal QA impact
- security/correctness impact
- release blocking YES/NO
- smallest repair scope if needed

Then return EXACTLY these markers:

REPOSITORY_IDENTITY_VERIFIED: YES/NO
UNAUTHORIZED_SCOPE_DRIFT: YES/NO
ALL_LIVE_CONSUMER_WRITE_ROUTES_ENUMERATED: YES/NO
ALL_RELEASE_RELEVANT_CONSUMER_WRITES_PHYSICALLY_CONTAINED: YES/NO
WRITE_AUTHORIZATION_RUNTIME_SAFE: YES/NO
STANDARD_UNIT_SUITE_INCLUDES_CONTAINMENT_REGRESSIONS: YES/NO
MUTATION_PROBE_DETECTS_DISABLED_CONTAINMENT: YES/NO
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
FOCUSED_TESTS_PASS: YES/NO
FULL_UNIT_ONLY_HISTORICAL_FAILURES: YES/NO
FRESH_POST_REPAIR7_VSIX_BUILT: YES/NO
FRESH_POST_REPAIR7_VSIX_VERIFIED: YES/NO
PACKAGE_HYGIENE_SAFE: YES/NO
PACKAGE_PROVENANCE_MATCHES_CURRENT_SOURCE: YES/NO
SAFE_TO_COMMIT_HF1_V2: YES/NO
SAFE_TO_BEGIN_QA_VSIX_TESTING: YES/NO
SAFE_TO_RELEASE_HF1_V2: YES/NO

PASS BAR:

SAFE_TO_COMMIT_HF1_V2 may be YES only if there are ZERO unresolved
CRITICAL/HIGH release-blocking findings.

SAFE_TO_BEGIN_QA_VSIX_TESTING may be YES only if a fresh post-Repair-7 VSIX
was built and independently verified.

SAFE_TO_RELEASE_HF1_V2 must remain NO until QA installation/end-user workflow
testing is completed separately.

Do not repair anything during this audit.

End with:

LOCAL_HOTFIX_HF1_V2_FINAL_RELEASE_REAUDIT_AFTER_REPAIR_7_COMPLETE
