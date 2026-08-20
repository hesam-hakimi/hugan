LOCAL_HOTFIX_HF1_V2 — FINAL INDEPENDENT READ-ONLY AUDIT

Perform a fresh, independent, adversarial, strictly read-only audit of the completed HF1 V2 candidate.

You did not implement this candidate.

Do not trust implementation-chat conclusions, self-reviews, test descriptions, or architectural claims unless independently supported by live source evidence.

This audit must not edit, create, delete, format, stage, commit, package, install, or otherwise mutate repository state.

⸻

1. Repository identity

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

The working tree intentionally contains the uncommitted HF1 V2 candidate.

External validation immediately before this audit reported:

Changed paths before validation: 23
Compile: PASS
Lint: PASS
Focused Repair 3 / HF1 V2 tests:
79 passing
0 failing
Full unit:
1853 passing
5 pending
5 failing
The remaining five failures are the known historical baseline:
1. EvalGating — committed Phase H baseline
2. EvalGating — deterministic v3 baseline without prompt telemetry
3. Copilot workflow customization — repo-local agents
4. Copilot workflow customization — frontmatter/agent naming
5. Copilot workflow customization — AGENTS.md guidance
New HF1 V2 regressions: NONE
Repository state changed by validation: NO
Staged paths: 0
Final marker:
HF1_V2_REPAIR_3_EXTERNAL_VALIDATION_PASS

Treat these as supplied external evidence, not evidence produced by this audit.

⸻

2. One consolidated read-only authorization

Before any command, request one consolidated authorization for the complete read-only audit.

The request may cover only:

* git status
* git diff
* git diff --check
* git rev-parse
* git remote
* git ls-files
* git show
* rg
* Get-Content
* Get-Item
* Get-ChildItem
* Test-Path
* Get-FileHash
* other strictly read-only source inspection required for this audit

No edit permission is required.

After approval, do not repeatedly ask conversational permission for operations inside this read-only set.

Do not run:

* npm install
* npm ci
* npx
* compile commands that emit
* test commands that mutate repository files
* VSIX packaging
* VSIX installation
* Git mutations
* baseline regeneration
* network/download operations

⸻

3. Audit immutability proof

At audit start:

1. Enumerate the complete changed-path set, including untracked candidate files.
2. Record full SHA-256 for every changed candidate file.
3. Record staged count.
4. Record repository identity.

At audit end:

* recompute the same hashes;
* re-enumerate the changed-path set;
* recheck staged count and identity.

Any candidate byte change during this audit is an automatic FAIL.

Do not assume the count 23 is correct; independently verify it.

Report any additional or missing candidate path.

⸻

4. Product requirement — normal QA must need ONE folder only

The intended product topology is:

VS Code
└── consumer workspace folder

Normal QA/end users must NOT need:

etl-framework-adb
framework source
extension source
frameworkRepositoryPath
a second workspace folder
manual job_conf/
manual env_conf/
manual workspace marker

Verify this from executable production paths, not comments.

Normal QA resolution must be:

exactly one workspace folder
→ canonicalize
→ validate
→ consumerRoot

Verify:

* zero folders → blocked;
* exactly one valid consumer folder → consumerRoot;
* multiple folders with no explicit safe consumer selection → ambiguous / fail closed;
* never use workspaceFolders[0] as a fallback;
* never infer “the folder that is not extension/framework must be consumer”;
* normal single-folder flow is independent from framework-source discovery.

Report any code path that violates this model.

⸻

5. Root separation

Audit strict separation between:

consumerRoot

The only filesystem root where consumer artifacts may be written.

extensionResourceRoot

The installed Extension package/resource root.

Contains the packaged trusted framework contract.

Never writable as a consumer root.

maintainerFrameworkRoot

Optional maintainer/development framework source.

Never required by QA.

Never writable as a consumer root.

Verify these concepts cannot be silently substituted for one another.

⸻

6. Packaged framework contract

Locate the packaged Oracle delivery-control contract.

Expected conceptual resource:

resources/framework/contracts/oracle-delivery-controls.v1.json

Audit:

* schemaVersion;
* contract ID/version;
* closed machine-readable semantics;
* supported module/control identifiers;
* Oracle db_data_out / db_ctrl_out semantics;
* deterministic canonical representation;
* SHA-256/fingerprint handling;
* integrity/version enforcement.

Verify the contract contains no:

* framework source code;
* Python/HOCON/SQL bodies;
* credentials;
* connection strings;
* hostnames;
* consumer schema/table values;
* business data;
* environment-specific data;
* developer machine absolute paths;
* unnecessary internal framework source paths.

Documentation alone must not act as trusted executable authority.

⸻

7. QA framework-authority resolution

Verify final authority precedence.

Expected:

1. non-empty explicitly configured maintainer source
   → validate
   → invalid = fail closed
2. explicitly present valid maintainer etl-framework-adb workspace source
   → validate
   → invalid = fail closed
3. packaged trusted framework contract
   → normal QA authority
4. unavailable

Critical requirements:

* QA with no configured source and no etl-framework-adb must use packaged_contract.
* No arbitrary filesystem scan.
* No neighboring-repository inference.
* No machine-wide search.
* No developer-path dependency.
* An explicitly invalid maintainer source must not silently fall back.

Verify authority/source kind is explicit, including an equivalent of:

configured_source
workspace_source
packaged_contract

⸻

8. Installed-extension resource loading

Verify the packaged framework contract is loaded from the installed Extension resource root.

Fail the audit if runtime depends on:

process.cwd()
consumerRoot
neighboring repo
developer checkout path
etl-framework-adb

to find the packaged contract.

Determine whether the same path logic will work after installation from a VSIX.

⸻

9. Oracle delivery-control validation

Trace validation from artifact evidence to readiness decision.

Verify:

* requirement.requiredWhen is honored;
* valid Oracle db_data_out / db_ctrl_out does not incorrectly require generic target path/table semantics;
* verified Oracle authority suppresses the false missing_target_location;
* missing authority emits an equivalent of:

FRAMEWORK_DEFINITION_UNAVAILABLE

* authority present but missing Oracle semantics emits:

ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING

* incomplete control sets fail closed;
* unrelated non-database target behavior is preserved;
* no consumer/database values are invented.

⸻

10. Fresh-consumer classification

Audit the typed decision contract equivalent to:

CREATE_NEW_JOB
UPDATE_EXISTING_REPO
BLOCKED

Verify a valid single fresh consumer folder can become:

CREATE_NEW_JOB

without requiring:

job_conf/
env_conf/
marker file
etl-framework-adb

Verify classification/preview itself creates no consumer files or directories.

External/source/framework/install roots must remain blocked.

⸻

11. Consumer-relative path model

Audit artifact identity.

The manifest should use canonical consumer-relative artifact paths rather than developer-machine absolute path identity.

Verify:

* absolute artifact paths are rejected;
* drive-qualified paths are rejected;
* .. traversal is rejected;
* escaping consumerRoot is rejected;
* sibling-root escape is rejected;
* paths are normalized deterministically;
* consumerRoot + approved relative path is used to produce the final target;
* containment is rechecked immediately before writing;
* write code does not independently recalculate a different path.

No artifact may write outside consumerRoot.

⸻

12. Immutable preview / approval binding

Verify preview and approval bind at least:

* canonical consumerRoot identity;
* target type;
* targetDecision;
* selected artifact types;
* exact relative artifact paths;
* content hashes;
* framework source kind;
* framework/contract identity;
* framework fingerprint.

Verify drift in any of these requires a new preview.

Specifically inspect tests and production behavior for:

* consumerRoot drift;
* relative path drift;
* content drift;
* authority/source-kind drift;
* framework fingerprint drift.

⸻

13. All write bypasses

Trace every production consumer-write entry point, including at least:

EtlActionToolService.writeToWorkspace
WriteCoordinator.writeArtifactsWithSummary
DeployCoordinator local-write path

Every route must enforce:

validation
→ immutable preview
→ explicit approval
→ one-time WriteAuthorization
→ runtime re-verification
→ exactly one write

Verify:

* hasOnboarding === false cannot bypass;
* missing preview returns preview and performs zero writes;
* declining approval performs zero writes;
* deploy-level approval alone cannot substitute for artifact approval;
* no automatic approval;
* no feature-flag bypass;
* no test-only production bypass.

⸻

14. WriteAuthorization runtime security

Audit the authorization boundary.

Verify arbitrary production callers cannot successfully fabricate authorization.

Runtime must reject:

* forged/plain-object authorization;
* stale approval;
* expired approval;
* consumed approval;
* wrong consumer root;
* changed target;
* changed targetDecision;
* changed artifact types;
* changed path;
* changed bytes;
* changed framework authority;
* changed fingerprint.

Verify exactly one approved write is possible.

⸻

15. Repair 1 / test-stub review

Review the current test-only casts/overrides introduced during external compile repairs.

Determine whether they:

* affect production: they must not;
* weaken a security test;
* make tests vacuous;
* fail to restore shared state;
* leak across suites.

A repo-conventional test-only type assertion is not automatically a blocker, but any test whose assertion no longer discriminates production behavior is a finding.

⸻

16. Repair 3 stale-test alignment

Verify the two previously new failures were corrected only by aligning tests to ratified architecture.

Inspect:

src/test/suite/phase5AgentRouter.test.ts
src/test/suite/onboardingWriteApproval.test.ts

Confirm:

Phase-5 router

* single-folder consumer positive case is asserted;
* multi-root without explicit selection is positively asserted ambiguous/BLOCKED;
* no first-folder/non-extension inference is restored.

Non-onboarding write

* first invocation produces preview and zero writes;
* real approval transition is used;
* second invocation writes exactly once;
* consumed approval cannot be reused.

Fail if tests merely suppress the old failures.

⸻

17. Consumer artifact invariance

Verify HF1 V2 does not alter the intended consumer artifact contract.

Expected:

12 consumer artifacts

Verify:

* same artifact set;
* same paths;
* same ordering;
* same bytes for equivalent input;
* packaged framework contract is not artifact 13;
* no framework provenance leaks into consumer bytes;
* no marker is silently added.

⸻

18. Package hygiene

Audit .vscodeignore, package assets, and resource inclusion.

A future QA VSIX must include:

package.json
out/extension.js
out/sttm-runtime.js
resources/copilot/**
resources/framework/contracts/oracle-delivery-controls.v1.json
required runtime/media files

It must exclude development/test artifacts including applicable forms of:

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

Determine whether the current checked-in packaging configuration actually guarantees this, rather than requiring post-build manual sanitization.

A package requiring manual ZIP surgery is NOT acceptable for final QA handoff.

⸻

19. Test quality

Inspect HF1 V2 test coverage and identify any critical behavior proven only by:

* source-text search;
* implementation-mirroring constants;
* mocks bypassing the real production boundary;
* vacuous assertions;
* private test backdoors;
* assertions that would still pass if the real security behavior were broken.

Pay particular attention to:

* packaged contract without framework source;
* single-folder QA path;
* path containment;
* write authorization;
* all former bypass routes;
* artifact invariance.

⸻

20. Known historical full-suite failures

The final external regression run established:

1853 passing
5 pending
5 failing

The five failures were independently matched by the external script to:

1. committed Phase-H baseline
2. deterministic v3 baseline without prompt telemetry
3. repo-local agent customization
4. frontmatter / agent naming
5. AGENTS.md guidance

No HF1 V2 regression remained.

Review source dependency relationships and confirm whether these five remain unrelated to HF1 V2.

Do not repair them.

⸻

21. Separate maintainer multi-root observability debt

Prior read-only analysis identified a potential non-safety UX/observability issue:

multi-root maintainer planning may surface ambiguity but continue producing a degraded V3 plan with workspaceRoot: undefined.

Audit whether this observation is accurate.

Do not treat it as an HF1 V2 release blocker unless it creates:

* an unauthorized write;
* root substitution;
* path escape;
* security bypass;
* normal single-folder QA failure.

Otherwise record it as separate follow-up debt.

⸻

22. No-touch boundaries

Verify HF1 V2 has not modified:

original etl_framework_extension repository
etl-framework-adb
consumer repositories
S-A/S-B work
Phase-H baseline reports
resources/prompts/**
.github/**
AGENT.md / AGENTS.md
package-lock.json

except any exact file explicitly and legitimately part of the current HF1 V2 candidate.

⸻

23. Severity rules

Classify findings as:

CRITICAL
HIGH
MEDIUM
LOW
INFO

A PASS is forbidden if any unresolved CRITICAL or HIGH finding exists.

Examples of automatic HIGH/CRITICAL findings:

* QA still requires framework source;
* write can escape consumerRoot;
* first-folder fallback remains reachable;
* write bypass remains;
* approval can be forged/replayed;
* framework/manifest drift does not invalidate approval;
* packaged contract cannot load from installed extension;
* final VSIX cannot contain the packaged contract;
* consumer output silently changes.

⸻

24. Required report

Return:

1. Repository identity and start-state hashes.
2. Exact candidate changed-path inventory.
3. Severity-ranked findings.
4. Single-folder QA path-model verdict.
5. Root-separation verdict.
6. Packaged-contract verdict.
7. Installed-resource-resolution verdict.
8. Oracle-validation verdict.
9. Fresh-consumer verdict.
10. Consumer-relative-path / containment verdict.
11. Preview/approval binding verdict.
12. All-write-routes verdict.
13. WriteAuthorization verdict.
14. Consumer artifact-invariance verdict.
15. Package-hygiene verdict.
16. Test-quality verdict.
17. Historical-five separation.
18. Maintainer multi-root observability finding.
19. End-state hashes and proof the audit changed nothing.
20. If repair is required, smallest exact file scope — but do not repair.

Finish with exactly:

REPOSITORY_IDENTITY_MATCH: YES|NO
CANDIDATE_BYTES_STABLE_DURING_AUDIT: YES|NO
UNAUTHORIZED_PATH_DRIFT: YES|NO
NORMAL_QA_SINGLE_FOLDER_MODEL_SAFE: YES|NO
QA_REQUIRES_FRAMEWORK_SOURCE: YES|NO
PACKAGED_CONTRACT_TRUST_BOUNDARY_SAFE: YES|NO
INSTALLED_EXTENSION_RESOURCE_LOADING_SAFE: YES|NO
ORACLE_VALIDATION_SAFE: YES|NO
FRESH_CONSUMER_CLASSIFICATION_SAFE: YES|NO
CONSUMER_PATH_CONTAINMENT_SAFE: YES|NO
ALL_WRITE_BYPASSES_CLOSED: YES|NO
WRITE_AUTHORIZATION_RUNTIME_SAFE: YES|NO
APPROVAL_DRIFT_BINDING_SAFE: YES|NO
CONSUMER_ARTIFACT_CONTRACT_PRESERVED: YES|NO
PACKAGE_HYGIENE_READY_FOR_QA_VSIX: YES|NO
HF1_V2_TEST_QUALITY_ACCEPTABLE: YES|NO
FIVE_HISTORICAL_FAILURES_UNRELATED: YES|NO
REAL_CONSUMER_E2E: NOT EXECUTED — SAMPLE UNAVAILABLE
SAFE_TO_BUILD_QA_VSIX: YES|NO
SAFE_TO_COMMIT_HF1_V2: NO
LOCAL_HOTFIX_HF1_V2_FINAL_INDEPENDENT_AUDIT_PASS

or, if the audit fails:

SAFE_TO_BUILD_QA_VSIX: NO
SAFE_TO_COMMIT_HF1_V2: NO
LOCAL_HOTFIX_HF1_V2_FINAL_INDEPENDENT_AUDIT_FAIL

No text after the final marker.
