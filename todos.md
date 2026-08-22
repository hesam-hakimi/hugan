LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6 — IMPLEMENT FROZEN RELEASE-GATE SCOPE

The read-only Repair-6 discovery completed with:

CURRENT_HF1_V2_BYTES_PRESERVED: YES
H1_PRIMARY_WRITE_PHYSICAL_CONTAINMENT_REPAIR_REQUIRED: YES
H2_TMP_PACKAGE_EXCLUSION_REPAIR_REQUIRED: YES
M1_ADDITIONAL_PHYSICAL_CONTAINMENT_REPAIR_REQUIRED: YES
M2_TSBUILDINFO_PACKAGE_REPAIR_REQUIRED: YES
M3_DISPOSITION_REPAIR_REQUIRED_FOR_QA: YES
M4_LEGACY_CUSTOMIZATION_REPAIR_REQUIRED_FOR_QA: NO
ADDITIONAL_RELEASE_BLOCKER_DISCOVERED: YES
ALL_RELEASE_RELEVANT_WRITE_ROUTES_PHYSICALLY_AUDITED: YES
REPAIR_6_SCOPE_FROZEN: YES

LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6_SCOPE_DISCOVERY_COMPLETE

Implement exactly this frozen Repair-6 scope.

Do not reopen Repair 5.

==================================================
0. SINGLE BOUNDED AUTHORIZATION
==================================================

Before edits, request one consolidated authorization covering:

- edits only to the 11 exact paths listed below;
- creation of exactly one new test file;
- compile/lint/unit/focused tests using existing dependencies;
- package creation and verifyVsix only at the final validation stage;
- no Git mutation;
- no dependency install/download;
- no VSIX installation;
- no real consumer repository mutation.

Ask for:

APPLY_LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6

==================================================
1. EXACT AUTHORIZED SCOPE
==================================================

PRODUCTION FILES

1. src/writers/RepoWriter.ts
2. src/chat/UnitTestCoordinator.ts
3. src/chat/ExplainCoordinator.ts
4. src/core/artifacts/NewArtifactWriter.ts
5. src/core/artifacts/ArtifactPatchApplier.ts
6. src/tools/EtlActionToolService.ts

TEST / VERIFICATION FILES

7. src/test/verifyVsixContents.ts
8. src/test/suite/packageAssets.test.ts
9. src/test/suite/onboardingWriteApproval.test.ts

PACKAGE CONFIG

10. .vscodeignore

NEW FILE — EXACTLY ONE

11. src/test/suite/physicalWriteContainment.test.ts

No twelfth file may change.

If another file is genuinely required, STOP before editing it and return:

LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6_SCOPE_AMENDMENT_REQUIRED

==================================================
2. H1 — REPOWRITER PRIMARY PHYSICAL CONTAINMENT
==================================================

RepoWriter.writeArtifacts() is the central write choke point shared by:

/write
WriteCoordinator
DeployCoordinator
etl_write_to_workspace

Today it performs lexical PathValidator checks and then constructs physical paths with path.join before writing.

That is insufficient.

Integrate the already-hardened:

resolveContainedWorkspacePath(...)

inside RepoWriter.writeArtifacts() for EVERY actual artifact destination:

- job config
- every additional job config
- env config
- every include file

The physical containment decision must occur before ANY filesystem mutation for that target.

Do not duplicate the hardened algorithm.

Reuse the existing helper.

==================================================
3. ORDERING REQUIREMENT
==================================================

Current private writeFile() creates parent directories before writing.

Therefore containment MUST be resolved BEFORE calling writeFile().

Required order:

approved canonical consumerRoot
→ relative artifact path
→ lexical validation
→ resolveContainedWorkspacePath()
→ fail closed if unsafe
→ only then createDirectory
→ only then writeFile

An unsafe destination must create:

- zero outside files
- zero outside directories
- zero target directories through an escaping link

==================================================
4. REPOWRITER ALL FOUR DESTINATION BRANCHES
==================================================

Apply the same physical containment contract independently to:

1. artifacts.jobConfigPath / artifacts.jobConfig

2. every additionalJobConfigs entry

3. artifacts.envConfigPath / artifacts.envConfig

4. every includeFiles entry

Do not assume one safe job-config destination proves the others safe.

==================================================
5. REPOWRITER PUBLIC MUTATORS L5
==================================================

Discovery found:

backupExisting(...)
ensureDirectoryStructure(...)

have no production callers but remain public mutation APIs.

Do not delete them.

Route any destination they mutate through the same physical containment primitive using the smallest change possible.

This is latent hardening only.

Do not redesign their APIs unless necessary.

==================================================
6. UNITTESTCOORDINATOR PHYSICAL CHECK
==================================================

Replace the current lexical-only final containment check immediately before the real filesystem mutation.

Do NOT rely on:

isInsideRoot(...)

as the sole security boundary.

Use the same hardened physical containment semantics as RepoWriter.

The approved path identity must remain unchanged.

Required order:

approved preview
→ canonical consumerRoot
→ physical destination re-resolution
→ fail closed
→ createDirectory/writeFile
→ mark consumed

Also correct any comment that currently claims lexical isInsideRoot is a complete containment proof.

==================================================
7. EXPLAINCOORDINATOR ORDERING FIX
==================================================

Explain already performs physical containment, but discovery found:

createDirectory(...)

occurs before the final physical containment check.

Move the physical containment resolution/check BEFORE createDirectory.

Required:

preview/approval
→ root/path/content drift checks
→ physical containment
→ createDirectory
→ writeFile
→ mark consumed

Unsafe path:

→ zero directory creation
→ zero file creation
→ fail/revoke approval correctly

Do not otherwise redesign Explain.

==================================================
8. ARTIFACT REUSE — REAL APPLY MUTATION CHECKS
==================================================

Repair the real physical mutation points:

src/core/artifacts/NewArtifactWriter.ts

and

src/core/artifacts/ArtifactPatchApplier.ts

The preview/plan-freeze containment check is NOT sufficient because filesystem topology may change between preview and apply.

Immediately before:

createDirectory
writeFile
patch write

perform the same hardened physical containment check against the canonical approved consumerRoot.

This closes the TOCTOU window:

preview
→ approval
→ attacker/environment creates junction/symlink
→ apply

must result in:

REJECTED
zero outside mutation

Do not weaken ArtifactActionCoordinator's approval model.

Do not change preview_only handling.

==================================================
9. M3 — MANIFEST DISPOSITION TRUTHFULNESS
==================================================

Discovery confirmed:

EtlActionToolService.collectManifestFiles(...)

can describe job config as:

disposition: unchanged

while RepoWriter.writeArtifacts() will rewrite the non-empty job config anyway.

The approval preview must truthfully describe the actual mutation.

Change only the smallest relevant logic in:

src/tools/EtlActionToolService.ts

so disposition reflects what RepoWriter will really do.

Do not change the artifact bytes.

Do not change output paths.

Do not add a new write.

Only make preview/manifest semantics truthful.

Add/update the behavioral regression in:

src/test/suite/onboardingWriteApproval.test.ts

==================================================
10. H2/M2 — .VSCODEIGNORE
==================================================

Repair package hygiene in:

.vscodeignore

At minimum ensure recursive exclusion of:

.tmp/**

nested Git metadata at any depth:

**/.git/**

and robust tsbuildinfo variants, including:

.tsbuildinfo
.tsbuildinfo.test
foo.tsbuildinfo
foo.tsbuildinfo.test
nested equivalents

Use patterns compatible with the actual vsce/minimatch semantics.

Do not remove required runtime content.

Required runtime resources must remain packageable:

out/extension.js
out/sttm-runtime.js
resources/copilot/**
resources/framework/contracts/**
media/runtime assets required by package.json

==================================================
11. VERIFYVSIXCONTENTS MUST MATCH PACKAGE POLICY
==================================================

Update:

src/test/verifyVsixContents.ts

The verifier must not use suffix-only logic that misses nested temporary trees.

It must reject at least:

extension/.tmp/**
any nested /.git/**
all tsbuildinfo variants
src/test/**
out/test/**
docs/eval/**
.vscode-test/**
*.log
*.vsix
other existing forbidden package entries

Also add package-size/content ceilings sufficient to catch a future bulk leak even if a novel file extension appears.

Do not hard-code today's exact .tmp byte count.

Use reasonable deterministic ceilings based on the legitimate package profile.

The verifier and .vscodeignore must express equivalent policy so they cannot silently drift apart.

==================================================
12. PACKAGEASSETS REGRESSION LOCK
==================================================

Update:

src/test/suite/packageAssets.test.ts

Assert the new .vscodeignore rules exist and match representative paths:

.tmp/agentic_etl/package.json
.tmp/repo/.git/objects/pack/example.pack
.tsbuildinfo.test
nested/foo.tsbuildinfo.test

Also assert required framework runtime contracts remain INCLUDED.

==================================================
13. NEW PHYSICAL WRITE TEST SUITE
==================================================

Create exactly:

src/test/suite/physicalWriteContainment.test.ts

This is the only new file authorized.

Use real filesystem behavior where possible.

Cover the central RepoWriter real mutation path and reduced multiplicity for the other Repair-6 routes.

Minimum RepoWriter cases:

1. job_conf directory junction → outside root: rejected.

2. env_conf junction → outside root: rejected.

3. include/sql directory junction → outside root: rejected.

4. additionalJobConfig destination junction → outside root: rejected independently.

5. final-file symlink → outside existing file: rejected.

6. dangling final symlink → outside missing target: rejected.

7. hard-linked unsafe destination / multiply-linked target: rejected according to existing containment contract.

8. refusal creates no directory outside root.

9. TOCTOU:
   build preview/approval while topology is safe,
   create escaping link after approval,
   attempt write,
   rejected and approval failed/not consumed.

10. positive control:
    normal deep fresh-consumer artifact path still writes successfully.

==================================================
14. M1 ROUTE REGRESSIONS
==================================================

The new suite must also include reduced physical escape tests for:

UnitTestCoordinator

NewArtifactWriter

ArtifactPatchApplier

ExplainCoordinator ordering

At minimum for each real mutation class:

- one escaping junction/symlink case
- assertion of zero outside mutation

For Explain additionally prove:

unsafe path creates no directory before rejection.

For Artifact Reuse additionally prove:

topology changed after preview/approval but before apply
→ rejected.

==================================================
15. DO NOT REPAIR M4
==================================================

Legacy Copilot workflow customization remains OUT OF SCOPE.

Do not modify:

CopilotWorkflowInitializer
WorkflowTargetResolver
CopilotWorkflowDeleter
Repairer
Upgrader
or protected customization assets

The discovery explicitly classified these as:

OUT_OF_SCOPE_LEGACY_BEHAVIOR

They are not part of the fresh-consumer QA release path.

Record them as deferred security-hardening debt only.

==================================================
16. DO NOT REPAIR NON-BLOCKING LOW DEBT
==================================================

Do not redesign:

folder-name exclusion heuristic
PathValidator.normalizePath
env-config read-root fallback
competing conversational route UX

unless compilation proves an unavoidable direct dependency.

Repair 6 should stay bounded to the frozen release blockers.

==================================================
17. NO-TOUCH BOUNDARY
==================================================

Do not modify:

etl-framework-adb
real consumer repositories
S-A / S-B files
Phase-H baselines
resources/prompts/**
.github/**
AGENT.md / AGENTS.md
package-lock.json
historical customization assets

Do not delete .tmp.

The package must exclude it; the source tree remains untouched.

==================================================
18. VALIDATION — CODE FIRST
==================================================

Using existing dependencies only:

npm run compile
npm run lint

Run focused suites for:

physicalWriteContainment
RepoWriter
UnitTestCoordinator
Explain
Artifact Reuse
RepoContext
WriteAuthorization
onboardingWriteApproval
packageAssets
HF1 V2 / Repair 5 regressions

Then run:

npm run test:unit

Expected:

compile PASS
lint PASS
all Repair-6 focused tests PASS
all Repair-5/HF1 focused tests PASS
full unit exactly 5 historical failures
no new regression

==================================================
19. PACKAGE VALIDATION — NOW AUTHORIZED
==================================================

Only AFTER code/test validation passes:

build the QA candidate VSIX using the repository's existing local packaging flow and already-installed tools.

No download.
No install.
No npx dependency fetch.

Then run the existing:

npm run verify:vsix

or exact repo-local equivalent discovered.

Also inspect the generated VSIX contents using the existing local vsce/archive tooling.

Prove REQUIRED runtime entries are present.

Prove forbidden entries are absent.

Specifically prove:

NO extension/.tmp/**
NO nested /.git/**
NO *.tsbuildinfo*
NO src/test/**
NO out/test/**
NO docs/eval/**
NO .vscode-test/**
NO *.log
NO nested *.vsix

The VSIX must not contain any of the eight .tmp scratch repositories.

==================================================
20. PACKAGE SIZE / CONTENT SANITY
==================================================

Report:

VSIX path
SHA-256
file count
compressed size
uncompressed size

Compare against expected legitimate extension content.

If package size is unexpectedly large, FAIL rather than manually deleting archive entries.

No manual ZIP surgery is allowed.

==================================================
21. SOURCE IMMUTABILITY AROUND PACKAGING
==================================================

Capture repository changed-path inventory before package validation.

Repeat afterward.

Packaging may create its expected output artifact outside or in the repository according to existing packaging convention, but source candidate bytes must not change unexpectedly.

No package-driven source mutation is acceptable.

==================================================
22. FINAL WRITE-ROUTE PHYSICAL SWEEP
==================================================

Re-audit all release-relevant write routes.

For each report:

Trusted authorization
Canonical logical root
Physical containment immediately before mutation

PASS requires every release-relevant consumer mutation to have all three.

No lexical-only physical mutation route may remain in the fresh-consumer QA path.

==================================================
23. FINAL SCOPE PROOF
==================================================

Return exact:

- files modified
- one new file created
- files authorized but unchanged
- staged count
- Git mutation count
- dependency install/download count
- consumer repository mutation count

No unlisted source/config/test file may change.

==================================================
24. REQUIRED FINAL REPORT
==================================================

Return:

1. Exact Repair-6 changed-file inventory.
2. H1 RepoWriter before/after.
3. UnitTestCoordinator physical containment result.
4. Explain ordering result.
5. Artifact create/patch TOCTOU result.
6. M3 disposition correction.
7. .vscodeignore before/after.
8. verifyVsixContents hardening.
9. physical containment adversarial matrix.
10. Compile result.
11. Lint result.
12. Focused tests.
13. Full unit result.
14. Historical-five separation.
15. VSIX build result.
16. VSIX SHA-256/file-count/size.
17. Required package entries.
18. Forbidden package entries.
19. Final write-route physical sweep.
20. Exact no-touch/scope proof.
21. Deferred M4/non-blocking debt list.

Finish exactly:

H1_PRIMARY_WRITE_PHYSICAL_CONTAINMENT_CLOSED: YES|NO
M1_ADDITIONAL_PHYSICAL_CONTAINMENT_CLOSED: YES|NO
H2_PACKAGE_HYGIENE_CLOSED: YES|NO
M2_TSBUILDINFO_HYGIENE_CLOSED: YES|NO
M3_MANIFEST_DISPOSITION_CLOSED: YES|NO
ALL_RELEASE_RELEVANT_WRITES_PHYSICALLY_CONTAINED: YES|NO
COMPILE_PASS: YES|NO
LINT_PASS: YES|NO
FOCUSED_TESTS_PASS: YES|NO
FULL_UNIT_ONLY_HISTORICAL_FIVE: YES|NO
QA_VSIX_BUILT: YES|NO
QA_VSIX_CONTENT_VERIFIED: YES|NO
UNEXPECTED_SCOPE_DRIFT: YES|NO
SAFE_FOR_FINAL_RELEASE_REAUDIT: YES|NO

Then exactly one:

LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6_VALIDATED

or:

LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

or:

LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6_SCOPE_AMENDMENT_REQUIRED

or:

LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6_BLOCKED

Do not commit.
Do not push.
Do not install the VSIX.
Stop after the report.
