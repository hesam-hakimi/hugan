# LOCAL_HOTFIX_HF1_V2_FINAL_POST_REPAIR5_REAUDIT
# FRESH INDEPENDENT READ-ONLY RELEASE-GATE AUDIT

Perform a fresh, independent, adversarial, strictly read-only audit of the CURRENT HF1 V2 candidate after the completed Repair 5 and Amendment 2.

You did NOT implement this candidate.

Do not trust the implementation chat's conclusions, its internal verifier, test summaries, or architectural claims unless independently supported by current live source evidence.

The current implementation workflow reported:

- production compile: PASS
- lint: PASS
- RepoWriter suite: 23 passing
- Explain suite: 28 passing
- focused Repair-5/HF1 matrix: 304 passing, 0 failing
- full unit: 1896 passing, 5 pending, exactly 5 failing
- five failures = the protected historical set
- REPAIR_5_REQUIRED routes remaining: 0
- staged files: 0
- new files from Amendment 2: 0
- internal verifier: VERIFIED
- final implementation marker:
  LOCAL_HOTFIX_HF1_V2_REPAIR_5_VALIDATED

Treat all of the above as supplied evidence only.

Do not edit or mutate anything.

==================================================
1. ONE CONSOLIDATED READ-ONLY AUTHORIZATION
==================================================

Before inspection, request one consolidated authorization for all required read-only commands, including equivalents of:

git status
git diff
git diff --check
git rev-parse
git remote
git ls-files
git show
rg
Get-Content
Get-Item
Get-ChildItem
Get-FileHash
Test-Path

Do NOT run:

- Git mutations
- npm install / npm ci
- downloads
- VSIX packaging/install
- baseline regeneration
- any command that intentionally changes candidate bytes

==================================================
2. REPOSITORY IDENTITY
==================================================

Audit only:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected base HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected origin:

https://github.com/TD-Universe/agentic_etl.git

Expected staged count:

0

Independently verify all values.

==================================================
3. AUDIT IMMUTABILITY
==================================================

At audit start:

- enumerate the complete current candidate changed-path set;
- capture full SHA-256 for every candidate file;
- capture repository identity;
- capture staged count.

Repeat all four at audit end.

Any candidate-byte drift during this audit is an automatic FAIL.

Do not assume the implementation's changed-file count.

==================================================
4. COMPLETE CONSUMER-WRITE ROUTE SWEEP
==================================================

Perform a fresh repo-wide search for every reachable production filesystem mutation capable of writing to a consumer workspace.

Trace equivalents of:

workspace.fs.writeFile
workspace.fs.createDirectory
fs.writeFile
fs.writeFileSync
fs.mkdir
fs.mkdirSync
rename/copy/write abstractions
writers eventually reaching these APIs

Do not assume the previously known list is complete.

For every route classify it as exactly one of:

TRUSTED_CONSUMER_WRITE
INTERNAL_NON_CONSUMER_WRITE
TEST_ONLY
DEAD_OR_UNREACHABLE
UNSAFE_CONSUMER_WRITE
AMBIGUOUS

For every TRUSTED_CONSUMER_WRITE prove:

canonical consumerRoot
→ prohibited-root rejection
→ contained artifact identity
→ immutable preview
→ explicit approval
→ trusted authorization
→ immediate pre-write re-verification
→ exactly intended mutation
→ one-time consumption/replay protection

PASS requires:

UNSAFE_CONSUMER_WRITE count = 0
AMBIGUOUS consumer-write route count = 0

==================================================
5. NORMAL QA SINGLE-FOLDER CONTRACT
==================================================

Independently prove:

one legitimate fresh consumer folder
→ CREATE_NEW_JOB

one legitimate existing consumer folder
→ UPDATE_EXISTING_REPO

zero folders
→ BLOCKED

multiple folders with no explicit safe selection
→ ambiguous/BLOCKED

sample_repo
→ BLOCKED

current HF1 V2 extension checkout
→ BLOCKED

etl-framework-adb / framework/source/reference/install root
→ BLOCKED

Normal QA must NOT require:

etl-framework-adb
framework source
frameworkRepositoryPath
extension source
a second workspace folder
manual job_conf/
manual env_conf/
manual marker files

Search specifically for any remaining consumer-write use of:

workspaceFolders[0]
workspaceFolders?.[0]

Any reachable unvalidated first-folder write root is a release blocker.

==================================================
6. PHYSICAL CONTAINMENT — REPAIR 5 AMENDMENT 2
==================================================

Independently inspect the final RepoWriter physical-containment implementation.

Verify all of these:

1. normal in-root destination accepted;
2. `..` traversal rejected;
3. absolute destination rejected;
4. sibling-root destination rejected;
5. link/junction to existing outside destination rejected;
6. dangling final-file link to outside missing target rejected;
7. dangling/escaping linked ancestor rejected;
8. POSIX case-distinct sibling rejected;
9. Windows equivalent-case path remains valid where appropriate;
10. valid in-root linked/non-linked destination remains safe;
11. hard-link/symlink compositions cannot physically mutate an outside file.

Specifically verify:

- ancestor discovery is lstat-aware;
- dangling links cannot be skipped as "nonexistent";
- failed realpath is fail-closed;
- physical target is checked, not merely lexical relative path;
- POSIX comparisons preserve case;
- Windows path identity remains case-insensitive as intended.

A physical write escape is automatic FAIL.

==================================================
7. EXPLAIN WRITE FLOW
==================================================

Trace Explain save end-to-end.

Prove:

first save
→ preview only
→ zero writes

approved second turn
→ same root/path/content
→ exactly one contained write

root drift
→ rejected

path drift
→ rejected

content drift
→ rejected

decline/cancel
→ zero writes

replay
→ zero additional writes

pending preview identity is opaque only.

Also verify unique temporary Explain fixtures are test-only isolation and do not alter production semantics.

==================================================
8. ARTIFACT REUSE
==================================================

Trace:

ArtifactReuseConversationCoordinator
→ ArtifactActionCoordinator
→ create/patch writers

Prove:

preview
→ zero mutations

real approval transition
→ SAME preview/operation becomes authorized

approved create
→ exactly intended contained write

approved patch
→ exactly intended contained mutation

consumerRoot drift
→ rejected

path drift
→ rejected

content/patch drift
→ rejected

cancel
→ zero mutations

replay
→ zero additional mutation

No preview_only state may be treated directly as approved.

No independent weaker approval mechanism may bypass the trusted state machine.

==================================================
9. REPO CONTEXT INITIALIZATION
==================================================

Trace both production entry points.

Verify:

- canonical RepoWriter consumerRoot classification;
- selected root is revalidated even after UI selection;
- no workspaceFolders[0] trust;
- raw `{ approved: true }` cannot authorize writes;
- trusted inline authorization is required;
- exact final bytes are what the authorization manifest hashes;
- especially verify `.gitignore`;
- containment is rechecked before writing;
- prohibited/reference/source roots cannot be initialized.

==================================================
10. UNIT TEST COORDINATOR
==================================================

Reconfirm the previously fixed route:

- no direct-write bypass;
- shared RepoWriter root semantics;
- preview first;
- zero first-turn writes;
- approval second turn;
- exactly one write;
- replay rejected;
- path containment safe.

==================================================
11. FRAMEWORK AUTHORITY / ORACLE
==================================================

Reconfirm normal QA needs no live etl-framework-adb source.

Verify packaged Oracle authority:

configured source
→ validated or fail closed

explicit valid framework workspace source
→ validated or fail closed

otherwise packaged trusted contract
→ normal QA authority

Verify:

FRAMEWORK_DEFINITION_UNAVAILABLE

is distinct from:

ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING

and valid db_data_out / db_ctrl_out does not incorrectly produce generic missing_target_location.

==================================================
12. INSTALLED VSIX RESOURCE RESOLUTION
==================================================

Verify the trusted packaged framework contract can be resolved from the installed extension resource topology.

It must not require:

process.cwd()
developer checkout
neighbor repo
consumer root
etl-framework-adb

for normal QA operation.

A non-winning dev fallback may remain only if installed-resource resolution clearly wins.

==================================================
13. WRITE AUTHORIZATION ADVERSARIAL CHECK
==================================================

Verify trusted routes reject:

forged authorization
expired approval
stale approval
consumed approval
wrong consumerRoot
wrong target
wrong targetDecision
changed artifact type
changed relative path
changed bytes
replay/concurrent second consumption

No authorization may produce two writes.

==================================================
14. COMPETING-ROUTE DEBT
==================================================

The implementation discovery classified conversational competing-route precedence as NON_BLOCKING_DEBT.

Independently verify that:

- only one route mutates per request;
- one route cannot consume another route's approval;
- stale conversation state cannot bypass authorization;
- remaining issue is only UX/conversational precedence.

If true, leave it non-blocking.

If an actual write bypass exists, elevate and FAIL.

==================================================
15. PACKAGE HYGIENE
==================================================

Verify the repository packaging configuration is sufficient for a clean QA VSIX.

Required runtime resources must include the packaged framework contract.

Development/test artifacts must remain excluded, including applicable forms of:

src/test/**
out/test/**
docs/eval/**
.vscode-test/**
*.tsbuildinfo*
tsconfig.test.json
*.log
*.vsix

No manual ZIP surgery may be required.

==================================================
16. CONSUMER ARTIFACT CONTRACT
==================================================

Verify Repair 5 did not unintentionally alter governed /create consumer artifact output.

Explain, Artifact Reuse, and RepoContext remain separately generated consumer-workspace operations and must not silently become additional /create artifacts.

Verify equivalent /create inputs retain stable intended artifact paths/bytes/order.

==================================================
17. HISTORICAL FIVE
==================================================

Confirm the remaining five full-suite failures are still only:

- two protected EvalGating failures;
- three protected Copilot workflow customization failures.

Confirm current HF1 V2 candidate does not introduce those failures.

Do not repair them.

==================================================
18. NO-TOUCH BOUNDARY
==================================================

Verify current HF1 V2 candidate has not modified prohibited external surfaces such as:

etl-framework-adb
real consumer repositories
S-A/S-B work
Phase-H baselines
resources/prompts/**
.github/**
AGENT.md / AGENTS.md
package-lock.json

except exact candidate-owned files explicitly expected by the hotfix.

==================================================
19. SEVERITY / RELEASE RULE
==================================================

Classify findings:

CRITICAL
HIGH
MEDIUM
LOW
INFO

A release-gate PASS requires:

CRITICAL = 0
HIGH = 0

No reachable unsafe consumer write route may remain.

No root/path physical escape may remain.

No normal QA dependency on framework source may remain.

==================================================
20. REQUIRED FINAL REPORT
==================================================

Return:

1. Repository identity.
2. Exact candidate changed-path inventory.
3. Start/end SHA-256 proof.
4. Severity-ranked findings.
5. Complete consumer-write-route inventory.
6. Single-folder QA verdict.
7. Physical containment verdict.
8. Explain verdict.
9. Artifact Reuse verdict.
10. RepoContext verdict.
11. UnitTestCoordinator verdict.
12. WriteAuthorization verdict.
13. Packaged framework/Oracle verdict.
14. VSIX resource-resolution verdict.
15. Package-hygiene verdict.
16. Historical-five separation.
17. Remaining non-blocking debts.
18. End-state no-touch proof.

Finish exactly:

REPOSITORY_IDENTITY_MATCH: YES|NO
CANDIDATE_BYTES_STABLE_DURING_AUDIT: YES|NO
UNAUTHORIZED_PATH_DRIFT: YES|NO
ALL_LIVE_CONSUMER_WRITE_ROUTES_ENUMERATED: YES|NO
ALL_CONSUMER_WRITE_ROUTES_GATED: YES|NO
NORMAL_QA_SINGLE_FOLDER_MODEL_SAFE: YES|NO
QA_REQUIRES_FRAMEWORK_SOURCE: YES|NO
PHYSICAL_CONTAINMENT_SAFE: YES|NO
DANGLING_LINK_ESCAPE_CLOSED: YES|NO
POSIX_CASE_CONTAINMENT_SAFE: YES|NO
EXPLAIN_TRUSTED_WRITE_SAFE: YES|NO
ARTIFACT_REUSE_TRUSTED_WRITE_SAFE: YES|NO
REPO_CONTEXT_TRUSTED_WRITE_SAFE: YES|NO
UNIT_TEST_COORDINATOR_TRUSTED_WRITE_SAFE: YES|NO
WRITE_AUTHORIZATION_RUNTIME_SAFE: YES|NO
PACKAGED_CONTRACT_TRUST_BOUNDARY_SAFE: YES|NO
ORACLE_VALIDATION_SAFE: YES|NO
INSTALLED_EXTENSION_RESOURCE_LOADING_SAFE: YES|NO
CONSUMER_ARTIFACT_CONTRACT_PRESERVED: YES|NO
PACKAGE_HYGIENE_READY_FOR_QA_VSIX: YES|NO
FIVE_HISTORICAL_FAILURES_UNRELATED: YES|NO
REAL_CONSUMER_E2E: NOT EXECUTED — SAMPLE UNAVAILABLE
SAFE_TO_KEEP_REPAIR_5: YES|NO
SAFE_TO_BUILD_QA_VSIX: YES|NO
SAFE_TO_COMMIT_HF1_V2: NO

Then exactly one final marker:

LOCAL_HOTFIX_HF1_V2_FINAL_POST_REPAIR5_REAUDIT_PASS

or:

LOCAL_HOTFIX_HF1_V2_FINAL_POST_REPAIR5_REAUDIT_FAIL

No text after the marker.
