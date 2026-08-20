LOCAL_HOTFIX_HF1_V2_FINAL_REAUDIT — INDEPENDENT READ-ONLY POST-REPAIR-4 AUDIT

Perform a fresh independent adversarial read-only re-audit of the complete current HF1 V2 candidate after Repair 4.

The previous independent audit is historical evidence only. It audited older bytes and returned FAIL.

Repair 4 subsequently changed the candidate, so you must independently inspect the current bytes and issue a new verdict.

Do not trust the Repair-4 implementation report as audit evidence.

Do not edit, create, delete, format, stage, commit, package, install, download, or mutate anything.

⸻

1. Audit target

Canonical repository:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected base HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected origin:

https://github.com/TD-Universe/agentic_etl.git

Expected staged count:

0

Do not assume the current changed-path count. Enumerate it independently.

⸻

2. Supplied external validation evidence

Treat the following only as external evidence to reconcile with live source:

Repair 4 reported:

LOCAL_HOTFIX_HF1_V2_REPAIR_4_VALIDATED

and:

Compile: PASS
Lint: PASS
Repair-4 required tests: PASS
Full unit:
1867 passing
5 pending
5 failing

The five remaining failures were reported as exactly the historical unrelated set:

1. EvalGating — committed Phase-H baseline
2. EvalGating — deterministic v3 baseline without prompt telemetry
3. Copilot workflow customization — repo-local agents
4. Copilot workflow customization — frontmatter / naming
5. Copilot workflow customization — AGENTS.md guidance

No HF1 V2 regression was reported.

Do not claim you independently executed those commands.

⸻

3. One consolidated read-only authorization

Before inspection, ask once for permission to perform the complete bounded read-only audit using commands equivalent to:

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
Test-Path
Get-FileHash

No edits.

No compile/test/package/install commands.

No Git mutation.

No network.

⸻

4. Audit-byte immutability

At the audit start:

* record repository identity;
* enumerate every modified/untracked candidate path;
* record full SHA-256 for every candidate file;
* record staged count.

At audit end repeat all four.

Any candidate-byte difference during the audit is an automatic FAIL.

Report the exact current candidate changed-path count rather than relying on any historical count.

⸻

5. Re-audit the two previous blocking findings

A. Previous CRITICAL — sample_repo

Independently prove:

sole workspace folder = sample_repo
→ BLOCKED
→ workspacePath undefined
→ cannot become consumerRoot
→ zero write capability

Inspect the actual root-classification implementation.

Confirm:

* exact-match/canonical root-name handling;
* no fuzzy substring behavior;
* legitimate similarly named consumer roots are not accidentally blocked;
* a legitimate fresh single consumer folder still reaches CREATE_NEW_JOB.

A source-text check alone is insufficient; inspect behavioral tests and runtime call path.

B. Previous HIGH — UnitTestCoordinator direct write

Trace the entire current production route:

UnitTestCoordinator.handleWrite()
→ consumerRoot resolution
→ artifact/path validation
→ immutable preview
→ approval
→ trusted authorization
→ containment re-check
→ filesystem write

Prove there is no remaining direct-write route around this sequence.

Verify:

* first write request performs zero filesystem writes;
* preview identity survives the multi-turn flow;
* approval is real, not auto-minted;
* approved second turn performs exactly one write;
* approval is marked consumed;
* replay performs zero additional writes;
* multi-root ambiguity fails closed;
* no workspaceFolders[0] fallback survives;
* prohibited single roots remain blocked.

⸻

6. UnitTestCoordinator path containment

This was part of the previous HIGH finding.

Independently verify that the route now rejects:

absolute paths
drive-qualified paths
.. traversal
normalized consumerRoot escape
sibling-root escape
extension-resource root
framework/reference/source root

Immediately before workspace.fs.writeFile, the final target must still be proven inside the canonical approved consumerRoot.

The path written after approval must be the same artifact identity previewed before approval.

Fail if UnitTestCoordinator retains only a filename regex as its effective security boundary.

⸻

7. Preview identity persistence

Inspect the added optional persisted field in the unit-test evidence/summary contract.

Verify:

* it stores only an opaque preview/approval identifier;
* no WriteAuthorization capability is persisted;
* no privileged runtime object is serialized;
* old summaries without the field remain compatible;
* a consumed preview cannot silently become usable again;
* successful write clears or consumes the persisted identity as intended.

⸻

8. Dependency injection

Inspect the ETLChatParticipant → UnitTestCoordinator construction.

Confirm:

* the existing shared RepoWriter / trusted approval infrastructure is reused;
* there is no second independent write-authority store;
* there is no separately constructed root resolver that could disagree with the rest of the extension;
* unrelated coordinator construction sites retain compatible behavior.

⸻

9. Re-audit normal QA topology

The required normal user topology remains:

VS Code
└── exactly one consumer folder

QA must require:

NO etl-framework-adb
NO framework source
NO frameworkRepositoryPath
NO extension source
NO second workspace folder

Verify:

one legitimate empty consumer
→ CREATE_NEW_JOB
one legitimate existing consumer
→ UPDATE_EXISTING_REPO
sample_repo/reference/source/install root
→ BLOCKED
zero workspace folders
→ BLOCKED
multiple folders without explicit safe selection
→ ambiguous / BLOCKED

Never permit first-folder fallback.

⸻

10. Packaged framework contract

Reconfirm that normal QA Oracle validation resolves the trusted packaged contract from the installed Extension resources without framework source.

Verify:

* packaged contract is authoritative machine metadata, not documentation;
* closed schema;
* expected contract identity/version;
* fingerprint/integrity behavior;
* no source code/credentials/business data/developer paths;
* db_data_out / db_ctrl_out semantics available;
* missing authority and missing Oracle semantics remain distinct failures.

⸻

11. Installed-extension resource resolution

Reconfirm the packaged contract can be resolved from an installed VSIX.

Any process.cwd() fallback or development-checkout candidate must not become necessary for normal installed operation.

If a cwd fallback remains only as a non-winning development fallback, classify it appropriately and demonstrate why installed-extension resource resolution wins.

⸻

12. Oracle validation

The previous independent audit could not finish a dedicated second adversarial pass.

Complete it now from live source.

Verify:

* requirement.requiredWhen semantics;
* Oracle delivery-control recognition;
* valid Oracle control does not produce generic missing_target_location;
* missing authority → FRAMEWORK_DEFINITION_UNAVAILABLE;
* authority missing Oracle semantics → ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING;
* incomplete controls fail closed;
* no invented database/consumer value;
* blocking readiness prevents write.

⸻

13. All production write routes

Perform a repo-wide search for actual filesystem consumer writes.

Do not assume there are only four.

Enumerate all production routes capable of:

workspace.fs.writeFile
workspace.fs.createDirectory
or equivalent consumer-workspace mutation

For every real consumer artifact write route, determine whether it is:

* protected by trusted preview/approval/authorization; or
* non-consumer/internal and legitimately outside this contract.

The known relevant routes include:

EtlActionToolService.writeToWorkspace
WriteCoordinator.writeArtifactsWithSummary
DeployCoordinator local-write
UnitTestCoordinator.handleWrite

PASS requires no reachable unapproved consumer write route.

⸻

14. WriteAuthorization

Reconfirm runtime rejection of:

forged authorization
stale approval
expired approval
consumed approval
wrong consumerRoot
wrong target
wrong targetDecision
changed artifact types
changed relative path
changed bytes
wrong framework state where applicable

Verify concurrent/replayed consumption cannot produce two writes.

⸻

15. Framework-binding LOW debt

Repair 4 deliberately did not modify framework-manifest binding.

Re-evaluate the actual current risk.

The current design reportedly revalidates framework authority immediately before gated write, preventing stale authority from reaching the write.

Determine whether this remains:

LOW / INFO follow-up debt

or whether there is a reachable security/reliability sequence that elevates it.

Do not fail the audit merely because framework identity is not directly embedded in the manifest if equivalent fail-closed revalidation removes any exploitable write path.

But report the exact limitation.

⸻

16. Consumer artifact invariance

Independently verify or refute:

12 consumer artifacts
same set
same relative paths
same ordering
same bytes for equivalent input

The packaged framework contract must not become artifact 13.

Framework provenance must not leak into generated consumer bytes.

Do not accept an implementation report as proof.

Use current executable tests/data flow as evidence.

⸻

17. Package hygiene

Verify checked-in packaging config is sufficient for a normal clean VSIX build.

Required runtime content:

package.json
out/extension.js
out/sttm-runtime.js
resources/copilot/**
resources/framework/contracts/oracle-delivery-controls.v1.json
required runtime/media

Forbidden test/dev content includes applicable forms of:

.tsbuildinfo.test
*.tsbuildinfo
*.tsbuildinfo.*
tsconfig.test.json
src/test/**
out/test/**
docs/eval/**
.vscode-test/**
*.log
*.vsix

Manual ZIP surgery must NOT be required for the QA build.

⸻

18. Test quality

Independently inspect whether Repair 4 tests are actually discriminating.

Specifically prove tests would fail if each regression were reintroduced:

sample_repo writable
workspaceFolders[0] fallback
UnitTestCoordinator direct write
write before approval
approval replay
absolute path escape
.. traversal
sibling-root escape
write outside consumerRoot

Review any test-only mocks or hooks for vacuity or state leakage.

⸻

19. Historical five

Confirm the five remaining full-suite failures remain independent from current HF1 V2 candidate changes.

Do not repair them.

⸻

20. Maintainer multi-root observability debt

Recheck the previously identified UX/observability issue:

ambiguity may be surfaced while a degraded V3 planning flow continues with workspaceRoot: undefined.

It is not a release blocker unless it creates:

* unauthorized write;
* root substitution;
* path escape;
* normal QA failure;
* approval bypass.

Otherwise preserve it as separate follow-up debt.

⸻

21. No-touch proof

Verify no HF1 V2 work touched:

original etl_framework_extension repository
etl-framework-adb
consumer repositories
S-A/S-B work
Phase-H baseline reports
resources/prompts/**
.github/**
AGENT.md / AGENTS.md
package-lock.json

except exact files legitimately part of the candidate where applicable.

⸻

22. PASS criteria

A PASS requires:

* zero unresolved CRITICAL;
* zero unresolved HIGH;
* repository/candidate bytes stable;
* no unauthorized path drift;
* normal QA single-folder flow safe;
* no runtime framework-source requirement;
* all consumer write routes gated;
* UnitTestCoordinator containment safe;
* sample_repo blocked;
* trusted authorization safe;
* QA packaging configuration usable without manual sanitization.

MEDIUM/LOW/INFO findings may remain only if they are explicitly non-blocking and do not invalidate QA use.

⸻

23. Required final report

Return:

1. identity + exact candidate inventory;
2. start/end hash proof;
3. severity-ranked findings;
4. sample_repo verdict;
5. UnitTestCoordinator trusted-write verdict;
6. UnitTestCoordinator containment verdict;
7. all-production-write-route inventory;
8. single-folder QA verdict;
9. packaged-contract/Oracle verdict;
10. consumer artifact invariance verdict;
11. package-hygiene verdict;
12. test-quality verdict;
13. framework-binding residual debt;
14. maintainer observability debt;
15. historical-five separation;
16. any smallest remaining repair scope, without editing.

Finish exactly:

REPOSITORY_IDENTITY_MATCH: YES|NO
CANDIDATE_BYTES_STABLE_DURING_AUDIT: YES|NO
UNAUTHORIZED_PATH_DRIFT: YES|NO
SAMPLE_REPO_BLOCKED_AS_CONSUMER_ROOT: YES|NO
UNIT_TEST_COORDINATOR_TRUSTED_WRITE_SAFE: YES|NO
UNIT_TEST_COORDINATOR_CONTAINMENT_SAFE: YES|NO
ALL_CONSUMER_WRITE_ROUTES_GATED: YES|NO
NORMAL_QA_SINGLE_FOLDER_MODEL_SAFE: YES|NO
QA_REQUIRES_FRAMEWORK_SOURCE: YES|NO
PACKAGED_CONTRACT_TRUST_BOUNDARY_SAFE: YES|NO
INSTALLED_EXTENSION_RESOURCE_LOADING_SAFE: YES|NO
ORACLE_VALIDATION_SAFE: YES|NO
FRESH_CONSUMER_CLASSIFICATION_SAFE: YES|NO
WRITE_AUTHORIZATION_RUNTIME_SAFE: YES|NO
APPROVAL_DRIFT_BINDING_SAFE: YES|NO
CONSUMER_ARTIFACT_CONTRACT_PRESERVED: YES|NO
PACKAGE_HYGIENE_READY_FOR_QA_VSIX: YES|NO
HF1_V2_TEST_QUALITY_ACCEPTABLE: YES|NO
FIVE_HISTORICAL_FAILURES_UNRELATED: YES|NO
REAL_CONSUMER_E2E: NOT EXECUTED — SAMPLE UNAVAILABLE
SAFE_TO_BUILD_QA_VSIX: YES|NO
SAFE_TO_COMMIT_HF1_V2: NO

Then exactly one final marker:

LOCAL_HOTFIX_HF1_V2_FINAL_REAUDIT_PASS

or:

LOCAL_HOTFIX_HF1_V2_FINAL_REAUDIT_FAIL

No text after the marker.
