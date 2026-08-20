LOCAL_HOTFIX_HF1_V2 — CLEAN IMPLEMENTATION FROM AGENTIC-REDESIGN BASE

Objective

Implement a clean V2 hotfix for the Oracle delivery-control / fresh-consumer write blocker directly from the committed feature/v3-agentic-redesign baseline.

This V2 implementation must incorporate all architectural lessons learned from the earlier abandoned HF1 attempt.

The final QA experience must be:

Install VSIX
→ Open consumer ETL workspace
→ Read STTM
→ Preview
→ Validate
→ Explicit approval
→ Write

QA and normal end users must NOT need:

etl-framework-adb source access
framework source code
frameworkRepositoryPath configuration
a framework repository in their VS Code workspace
manual job_conf/
manual env_conf/
manual workspace markers

The etl-framework-adb repository available in this maintainer workspace is READ-ONLY evidence only.

⸻

1. EXPECTED REPOSITORY IDENTITY

Editable repository:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected base HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected origin:

https://github.com/TD-Universe/agentic_etl.git

The repository must initially be clean.

The original repository:

C:\repos\etl-extension\etl_fw2\etl_framework_extension

is protected and must never be modified by this task.

The original repository must retain its existing three-worktree inventory.

⸻

2. CONSOLIDATED ONE-TIME AUTHORIZATION

Before the first tool call, command, file read, or file edit, display exactly:

CONSOLIDATED_APPROVAL_REQUEST — LOCAL_HOTFIX_HF1_V2
Authorize one bounded local implementation batch covering:
1. Read-only inspection of:
   - etl_framework_extension_hf1_v2
   - etl-framework-adb as framework truth evidence only
2. Modification only inside the bounded HF1-V2 edit universe defined by this prompt.
3. Creation of exactly one packaged machine-readable framework contract resource.
4. Creation of the minimum necessary HF1-V2 source and test files within the authorized universe.
5. Local compile, lint, and test execution using only already-installed local dependencies.
6. If node_modules is absent in the V2 clone, use of an already-existing local dependency tree is allowed only through a local no-network dependency preparation explicitly confined to the ignored node_modules directory. Do not alter package.json or package-lock.json for dependency preparation.
7. Read-only Git/status/diff/hash verification.
EXPLICITLY NOT AUTHORIZED:
- network access
- npm install
- npm ci
- npx downloads
- dependency version changes
- Git add/commit/push/pull/reset/checkout/clean/stash/merge/rebase
- package publishing
- VSIX installation
- deployment
- modification of etl-framework-adb
- modification of any consumer repository
- modification of the original etl_framework_extension repository
- S-A/S-B work
- Keep/Undo
- CI/PR actions
Reply exactly:
APPLY_LOCAL_HOTFIX_HF1_V2_BATCH

Stop and wait.

After receiving exactly:

APPLY_LOCAL_HOTFIX_HF1_V2_BATCH

execute the complete task autonomously.

Do not repeatedly ask for conversational authorization for an operation already inside this batch.

Host-enforced VS Code/Copilot permission dialogs must not be bypassed.

⸻

3. PREFLIGHT — BEFORE ANY EDIT

Verify:

* canonical root;
* origin;
* branch;
* HEAD;
* staged count = 0;
* working tree clean;
* original repository remains untouched;
* etl-framework-adb is outside the editable repository;
* no consumer repository is an editable target.

Capture start hashes for every file that will later be modified.

If repository identity differs, stop with:

LOCAL_HOTFIX_HF1_V2_PREFLIGHT_BLOCKED

⸻

4. READ-ONLY DISCOVERY BEFORE FIRST EDIT

Before editing, inspect the live source and derive:

1. Current framework discovery implementation.
2. Current packaged-resource loading convention.
3. Current extension-installation-root/resource resolution convention.
4. Oracle db_data_out / db_ctrl_out validation path.
5. requirement.requiredWhen behavior.
6. Workspace/consumer classification.
7. All production write entry points.
8. Preview-manifest generation.
9. Approval-manifest implementation.
10. One-time approval consumption.
11. Artifact hash/path binding.
12. Existing test registration.
13. Existing .vscodeignore.
14. Existing package-asset checks.
15. Existing runtime bundling/output structure.

Before the first edit, print:

FROZEN_HF1_V2_EDIT_INVENTORY

followed by the exact files that will be changed/created.

Touch only files proven necessary.

If implementation later requires a file outside the authorized universe below, STOP before editing it and return:

LOCAL_HOTFIX_HF1_V2_SCOPE_AMENDMENT_REQUIRED

⸻

5. AUTHORIZED EDIT UNIVERSE

The implementation may use only the minimum necessary subset of these existing files:

.vscodeignore
package.json
src/core/framework/FrameworkDiscoveryService.ts
src/core/readiness/JobKnowledgeContract.ts
src/core/readiness/ReadinessProfileCatalog.ts
src/core/readiness/JobDevelopmentReadinessEvaluator.ts
src/validation/PreWriteValidationPipeline.ts
src/tools/TrustedWriteApprovalStore.ts
src/tools/EtlActionToolService.ts
src/writers/RepoWriter.ts
src/core/trusted/index.ts
src/chat/WriteCoordinator.ts
src/chat/DeployCoordinator.ts
src/test/testPatterns.ts
src/test/suite/repoWriterWorkspaceSelection.test.ts
src/test/suite/jobDevelopmentReadiness.test.ts
src/test/suite/onboardingWriteApproval.test.ts
src/test/suite/createPreviewFlow.test.ts
src/test/suite/writeFlow.test.ts
src/test/suite/extension.test.ts
src/test/suite/phase6WriteDeployRun.test.ts
src/test/suite/runtimeCreateFlow.test.ts
src/test/suite/etlActionTools.test.ts
src/test/suite/packageAssets.test.ts

New files may be created only if required:

src/core/framework/TrustedFrameworkDefinitionResolver.ts
src/core/trusted/WriteAuthorization.ts
src/test/helpers/mintTestWriteAuthorization.ts
src/test/suite/trustedFrameworkDefinitionResolver.test.ts
src/test/suite/hf1OracleFreshConsumer.test.ts
resources/framework/contracts/oracle-delivery-controls.v1.json

One additional existing resource-binding/activation file may be added to the frozen inventory ONLY if read-only discovery proves it is strictly required to resolve a packaged resource from the installed Extension root.

It must be identified before the first edit with exact path and reason.

No other file is authorized.

⸻

6. ROOT CAUSE TO FIX

The original reported blocker was:

Confirm destination schema/table or database delivery controls

It affected both:

etl_validate_artifacts
etl_write_to_workspace

The root causes are:

Defect A — Oracle validation

Generic target-path validation does not correctly honor externally defined database-delivery controls.

db_data_out and db_ctrl_out can therefore be incorrectly rejected as:

missing_target_location

even when Oracle delivery controls are valid.

Defect B — framework authority

The Extension previously depended on a live etl-framework-adb workspace source to prove Oracle delivery semantics.

That is unacceptable for QA/end users.

Defect C — fresh consumer classification

An explicitly selected, valid, empty consumer repository can be rejected merely because:

job_conf/
env_conf/

do not exist yet.

Defect D — write bypasses

Some production write paths can currently reach direct write behavior without the same immutable preview + approval contract.

Structural requirement — framework drift binding

The trusted framework authority and fingerprint must be bound to preview/approval so the authority cannot change between preview and write.

⸻

7. REQUIRED TARGET ARCHITECTURE

Implement two framework-authority modes.

Normal QA / end-user mode

Use a packaged trusted framework contract shipped inside the Extension.

QA requires no framework source.

Maintainer/development override mode

Maintainers may optionally validate against:

1. explicitly configured framework source;
2. explicitly opened multi-root etl-framework-adb.

Resolver precedence must be:

1. non-empty explicitly configured framework root
   → validate
   → invalid = fail closed
2. explicitly opened etl-framework-adb workspace root
   → validate
   → invalid = fail closed
3. packaged trusted framework contract
   → normal QA/end-user authority
4. unavailable

Important:

A non-empty but invalid configured source MUST NOT silently fall back.

An explicitly present but invalid framework workspace MUST NOT silently fall back.

No arbitrary filesystem scanning.

No neighboring-repository inference.

No machine-wide search.

⸻

8. PACKAGED TRUSTED FRAMEWORK CONTRACT

Create exactly one resource:

resources/framework/contracts/oracle-delivery-controls.v1.json

unless read-only repository conventions conclusively require a closely equivalent resource path.

It must be a deliberately curated machine contract—not documentation.

Contract characteristics

It must contain only the minimum safe metadata required for deterministic validation.

At minimum derive:

* schemaVersion;
* contractId;
* contractVersion;
* supported framework module type;
* Oracle delivery-control identities required by the actual Framework;
* safe option/control semantics needed by Extension validation;
* executable/process semantic requirement where relevant;
* deterministic compatibility fingerprint information.

Derive every semantic field from executable or structured etl-framework-adb evidence.

Documentation may corroborate semantics but may not be the sole authority.

Do not include:

* source code;
* Python;
* SQL;
* HOCON bodies;
* source comments;
* documentation prose;
* usernames;
* absolute paths;
* repository paths;
* Git URLs;
* credentials;
* connection strings;
* hostnames;
* environments;
* business data;
* real schema/table names;
* consumer values.

Prefer semantic contract identifiers over source filenames.

⸻

9. PACKAGED CONTRACT INTEGRITY

Runtime must not trust arbitrary JSON.

Validate:

* exact schemaVersion;
* exact contractId;
* supported contractVersion;
* exact closed field set;
* field types;
* allowed delivery-control identifiers;
* allowed module semantics;
* no unknown executable payload;
* no paths/environment payload;
* deterministic canonical representation.

Calculate deterministic SHA-256 over canonical contract content.

The runtime source must deliberately pin or otherwise explicitly validate the expected packaged contract identity/integrity so an accidental contract change cannot silently alter compatibility semantics.

Changing the contract must require an intentional source/test update.

Malformed or integrity-invalid packaged contracts fail closed.

⸻

10. LOAD FROM THE INSTALLED EXTENSION

The packaged contract must be resolved from the installed Extension package.

Do NOT load it relative to:

process.cwd()
consumer workspace
framework repository
neighboring repository
developer machine path

Use the repository’s established Extension-resource-resolution mechanism.

If this requires an activation/resource-binding file outside the normal allow-list, it must have been frozen during Discovery before editing.

The same implementation must work from a packaged VSIX.

⸻

11. FRAMEWORK SOURCE KIND

Represent framework authority explicitly.

Use existing naming conventions where possible, but distinguish at least:

configured_source
workspace_source
packaged_contract

For normal QA:

sourceKind = packaged_contract

Bind to approval:

* source kind;
* framework/contract identity;
* deterministic fingerprint.

Changing source kind between preview and write invalidates approval.

⸻

12. OPTIONAL FRAMEWORK PATH SETTING

If this setting is added or retained:

databricks-etl-copilot.frameworkRepositoryPath

it is an OPTIONAL maintainer/development override.

Normal QA users leave it empty.

Update its description accordingly.

Semantics:

empty:
    explicit framework workspace if valid
    else packaged contract
non-empty valid:
    configured source
non-empty invalid:
    fail closed
    do NOT fall back

Use selected consumer workspace/resource scope.

Canonicalize real paths.

Never write to the framework path.

⸻

13. ORACLE VALIDATION

Fix the actual validation contract.

Verify:

* requirement.requiredWhen is honored.
* Oracle destination validation uses actual db_data_out / db_ctrl_out delivery controls.
* A verified Oracle authority prevents the incorrect generic missing_target_location.
* Missing framework authority produces:

FRAMEWORK_DEFINITION_UNAVAILABLE

* Existing authority without required Oracle semantics produces:

ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING

* Incomplete delivery-control pairs fail closed.
* Non-database targets retain existing behavior.
* Missing framework provenance never invents a verdict.
* Blocking validation prevents render/write.

⸻

14. FRESH CONSUMER CLASSIFICATION

Implement a typed decision such as:

type WorkspaceTargetDecision =
  | 'CREATE_NEW_JOB'
  | 'UPDATE_EXISTING_REPO'
  | 'BLOCKED';

Do not use a free-form reason string as the security decision.

CREATE_NEW_JOB requires:

* explicit workspace selection;
* directory exists;
* canonical containment succeeds;
* valid consumer target;
* target is not Extension source;
* not Extension installation;
* not framework source;
* not external root;
* not ambiguous;
* no existing job_conf/;
* no existing env_conf/.

A fresh consumer must NOT require a marker file.

Do not auto-create:

job_conf/
env_conf/
etl-workspace.json
AGENTS.md

before approved write.

⸻

15. CLOSE ALL WRITE BYPASSES

All three production write entry points must use one guarded flow:

validation
→ immutable preview/path manifest
→ explicit approval
→ one-time WriteAuthorization
→ runtime re-verification
→ exactly one write

Audit and close:

EtlActionToolService.writeToWorkspace
WriteCoordinator.writeArtifactsWithSummary
DeployCoordinator local-write step

Do not implement a “route 1 only” partial fix.

Missing preview:

return preview
zero writes

Approval required before write.

Deploy-level approval alone is not sufficient for consumer artifact write.

Declining approval:

zero writes
zero publish
zero downstream side effect

⸻

16. WRITE AUTHORIZATION

Implement a narrow trusted write authorization.

Prefer a module-private brand / unique symbol.

Production callers must not be able to construct a valid authorization object arbitrarily.

Authorization must bind:

* approval ID;
* workspace identity;
* target type;
* targetDecision;
* selected artifact types;
* exact artifact paths;
* exact artifact content SHA-256 hashes;
* framework authority source kind;
* framework/contract identity;
* framework fingerprint.

At runtime immediately before write, re-verify all claims.

Reject:

* missing preview;
* stale preview;
* expired preview;
* already consumed approval;
* forged authorization;
* cast-like plain object;
* wrong workspace;
* changed target type;
* changed targetDecision;
* changed selected artifact types;
* changed path;
* changed artifact bytes;
* changed framework source kind;
* changed framework identity;
* changed framework fingerprint.

Exactly one write may occur after valid approval.

⸻

17. IMMUTABLE MANIFEST BINDING

Validation, Preview, Approval, and Write must consume the same authoritative artifact manifest.

Do NOT independently recalculate artifact paths at write time.

Bind:

* workspace identity;
* target decision;
* selected artifacts;
* paths;
* bytes/hashes;
* framework authority;
* fingerprint.

Any drift requires a new Preview.

⸻

18. CONSUMER ARTIFACT INVARIANCE

The existing consumer artifact contract must remain unchanged.

The previous behavior produced 12 preview artifacts.

V2 must preserve:

* same artifact set;
* same paths;
* same ordering;
* same generated bytes.

The packaged framework contract is an Extension resource.

It must NOT:

* become artifact 13;
* enter consumer workspace;
* change a renderer;
* change a template;
* change a path builder;
* change consumer output bytes.

Framework provenance belongs only to internal validation/approval state.

⸻

19. PACKAGE HYGIENE — FIX IT PERMANENTLY

The earlier test package revealed that package-selection hygiene is insufficient.

Inspect .vscodeignore and permanently ensure the VSIX excludes test/build-only artifacts including applicable forms of:

.tsbuildinfo.test
*.tsbuildinfo
*.tsbuildinfo.*
tsconfig.test.json
src/test/**
out/test/**
docs/eval/**
*.log
*.vsix
.vscode-test/**

Do not exclude required runtime bundles.

Ensure runtime packaging continues to include:

package.json
out/extension.js
out/sttm-runtime.js
resources/copilot/**
resources/framework/contracts/oracle-delivery-controls.v1.json
required media/runtime resources

Do not package during this implementation task.

Add or update package-related unit assertions only within the authorized test universe.

⸻

20. TEST REQUIREMENTS

Tests must be behavioral where security or correctness is material.

Source-text checks may supplement but cannot replace execution.

Implement tests for at least:

Framework contract

1. Valid packaged contract loads without framework source.
2. QA topology performs no etl-framework-adb access.
3. Configured valid source overrides packaged contract.
4. Invalid configured source fails closed without fallback.
5. Valid explicit workspace framework source overrides packaged contract.
6. Invalid explicit workspace framework fails closed.
7. Missing packaged contract + no source → FRAMEWORK_DEFINITION_UNAVAILABLE.
8. Malformed packaged contract fails closed.
9. Wrong schema version fails closed.
10. Unknown contract field fails closed.
11. Contract integrity/fingerprint mismatch fails closed.
12. Contract missing Oracle semantics → ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING.
13. Packaged contract validates db_data_out.
14. Packaged contract validates db_ctrl_out.

QA topology

15. No configured source.
16. No framework workspace.
17. Fresh consumer present.
18. Packaged contract present.
19. Oracle validation succeeds.
20. sourceKind === packaged_contract.

Fresh consumer

21. Explicit empty consumer → CREATE_NEW_JOB.
22. No marker created.
23. No job_conf/ before approval.
24. No env_conf/ before approval.
25. Unselected/external/source/install/framework roots → BLOCKED.

Approval/write

26. Missing preview → preview only, zero writes.
27. Valid explicit approval → exactly one write.
28. Forged authorization fails.
29. Stale approval fails.
30. Consumed approval fails.
31. Changed workspace fails.
32. Changed path fails.
33. Changed bytes fails.
34. Changed target type fails.
35. Changed targetDecision fails.
36. Changed framework identity fails.
37. Changed framework fingerprint fails.
38. Changed framework source kind fails.

Former bypass routes

39. hasOnboarding === false cannot bypass.
40. WriteCoordinator cannot bypass.
41. DeployCoordinator local-write cannot bypass.

Artifact invariance

42. Artifact count remains 12.
43. Paths unchanged.
44. Ordering unchanged.
45. Bytes unchanged.
46. Framework contract does not become consumer artifact.

Packaging hygiene

47. .tsbuildinfo.test excluded.
48. tsconfig.test.json excluded.
49. src/test/** excluded.
50. out/test/** excluded.
51. packaged framework contract explicitly included.
52. runtime bundles remain included.

Do not weaken or delete existing tests merely to obtain green output.

⸻

21. TEST REGISTRATION

Use existing test discovery conventions.

Modify src/test/testPatterns.ts only if new test files genuinely require explicit registration.

Do not broadly change test discovery.

⸻

22. TOOLCHAIN

Use only already-installed local tooling.

Before validation check:

node_modules
typescript
eslint
mocha
required local types/plugins

Do not run:

npm install
npm ci
npx download
network-dependent tooling

If node_modules is absent in the V2 clone but the original local development repository has an existing compatible node_modules, a local no-network copy into the ignored V2 node_modules directory is allowed by the consolidated authorization.

Do not alter package manifests as part of dependency preparation.

If local execution is unavailable from the Copilot environment, do not fabricate validation results.

⸻

23. VALIDATION

Run when locally available:

npm run compile
npm run lint

Run focused HF1-V2 tests using Windows-compatible PowerShell environment assignment.

Then run full unit tests.

Historical clean-base evidence from the same base commit showed six pre-existing failures:

1. Phase-H committed baseline
2. deterministic v3 baseline without telemetry
3. package-asset manifest
4. maintainer delivery prompt repo-local agents
5. customization asset frontmatter/naming
6. standard AGENTS.md guidance

V2 intentionally repairs package hygiene, so failure #3 MAY legitimately disappear.

Do not attempt to repair unrelated failures #1, #2, #4, #5, or #6.

Success criteria:

* compile: PASS
* lint: PASS
* all focused HF1-V2 tests: PASS
* no new full-unit failure
* unrelated baseline failures unchanged
* package-asset baseline failure may disappear only if directly attributable to the authorized .vscodeignore repair.

If native validation cannot be executed, return exact PowerShell commands for external validation.

⸻

24. NO REAL-CONSUMER CLAIM

No affected consumer repository/sample was supplied.

Always report:

REAL_CONSUMER_E2E:
NOT EXECUTED — SAMPLE UNAVAILABLE

Synthetic tests are not production validation.

⸻

25. NO-TOUCH BOUNDARY

Never modify:

C:\repos\etl-extension\etl_fw2\etl_framework_extension

Never modify:

etl-framework-adb

Never modify a consumer repository.

Do not modify:

.github/**
resources/prompts/**
docs/eval/**
S-A files
S-B files
Phase-H baseline reports
package-lock.json
AGENT.md / AGENTS.md

unless an exact file was explicitly included in the frozen inventory by this prompt’s permitted universe.

Do not:

* commit;
* stage;
* push;
* package;
* install VSIX;
* publish;
* deploy;
* create PR;
* run CI.

⸻

26. END-STATE INTEGRITY

At completion re-check:

* repository root;
* branch;
* HEAD;
* staged count;
* exact changed-path inventory;
* no unexpected file;
* original repository unchanged;
* framework repo unchanged;
* no consumer writes;
* no network/install action.

Run:

git diff --check

Report complete diff statistics.

⸻

27. FINAL REPORT

Return:

1. Repository identity.
2. Frozen edit inventory.
3. Exact created files.
4. Exact modified files.
5. Root-cause-to-change mapping.
6. Packaged contract schema.
7. Evidence-to-contract mapping.
8. Proof no framework source/sensitive content entered the contract.
9. Final resolver precedence.
10. QA flow without framework source.
11. Maintainer override flow.
12. Oracle blocker matrix.
13. Fresh-consumer decision behavior.
14. Write-authorization design.
15. All former bypass closures.
16. Approval/drift behavior.
17. Consumer artifact invariance.
18. Package-hygiene changes.
19. Test changes.
20. Exact validation commands and results.
21. Remaining baseline failures, separated.
22. Real-consumer limitation.
23. No-touch verification.
24. Final changed-file count and diff stats.

This implementation session cannot authorize Keep, Git, packaging, or release.

Finish with exactly one marker:

LOCAL_HOTFIX_HF1_V2_COMPLETE

if implementation and actual local validation complete successfully;

or:

LOCAL_HOTFIX_HF1_V2_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

if implementation is complete but native validation must be run externally;

or:

LOCAL_HOTFIX_HF1_V2_SCOPE_AMENDMENT_REQUIRED

if an additional repository file is required;

or:

LOCAL_HOTFIX_HF1_V2_BLOCKED

if implementation cannot safely complete.

Do not Keep.
Do not commit.
Do not push.
Do not package.
Do not install a VSIX.
Stop after the final report.
