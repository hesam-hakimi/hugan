TASK: LOCAL_HOTFIX_HF1_V2_REPAIR_8_FRESH_0_3_140_BUILD_GATE

Perform the Repair-8 fresh-package build gate in the SOFTWARE DEVELOPMENT
ENVIRONMENT.

This task is authorized to:

- compile the current accepted Repair-8 working tree;
- build exactly one fresh QA VSIX at source version 0.3.140;
- verify that exact VSIX;
- execute focused and full unit validation;
- inspect generated package content read-only.

This task is NOT authorized to change source code.

Do NOT change the version.
Do NOT edit package.json.
Do NOT edit package-lock.json.
Do NOT repair any source or test.
Do NOT regenerate Phase-H baselines.
Do NOT install the VSIX.
Do NOT install or download dependencies.
Do NOT modify a development test workspace.
Do NOT modify etl-framework-adb.
Do NOT stage, commit, push, reset, restore, checkout, stash, or clean.
Do NOT delete, rename, or modify existing stale VSIX artifacts.
Do NOT modify .github/**, resources/prompts/**, AGENT.md, or AGENTS.md.

Use only already-installed dependencies and the already-installed VSCE
executable.

==================================================
1. ACCEPTED INDEPENDENT RE-AUDIT
==================================================

The following findings are accepted:

REPAIR_8_SCOPE_MATCH: YES
UNAUTHORIZED_REPAIR_8_PATHS: 0
TRUSTED_CONTRACT_VALID: YES
TRUSTED_RESOLVER_VALID: YES
CANONICAL_ENVELOPE_RUNTIME_ENFORCED: YES
MODULE_EXTRACTION_CORRECT: YES
UNITY_CATALOG_DIRECT_WRITE_SUPPORTED: NO
UNITY_CATALOG_NEGATIVE_DIAGNOSTIC_CORRECT: YES
PACKAGED_FALLBACK_CORRECT: YES
PACKAGED_EXAMPLE_SEARCH_CORRECT: YES
FRESH_CONSUMER_PREVIEW_PATH_CORRECT: YES
PREVIEW_ZERO_WRITE_PROVEN: YES
REPAIR_5_6_7_SECURITY_PRESERVED: YES
COMPILE_PASS: YES
LINT_PASS: YES
FOCUSED_REPAIR_8_TESTS_PASS: YES
REPAIR_8_FUNCTIONAL_REGRESSION_COUNT: 0
REPAIR_8_SECURITY_REGRESSION_COUNT: 0
SIXTH_FAILURE_CAUSED_BY_REPAIR8_SOURCE_DEFECT: NO
SIXTH_FAILURE_CAUSED_BY_STALE_VSIX: YES
VSIX_SELECTION_LOGIC_ROBUST: NO
FRESH_VSIX_BUILD_REQUIRED_TO_CLOSE_GATE: YES
VERSION_REMAINS_0_3_140: YES

Do not repeat the Repair-8 architecture discovery.

The purpose of this task is only to close the fresh-package build gate.

==================================================
2. VERIFY SOFTWARE DEVELOPMENT ENVIRONMENT
==================================================

Expected repository root:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected base HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected package version:

0.3.140

Expected publisher:

td-etl

Verify all values before running any build command.

Capture:

- current tracked-modified paths;
- current untracked paths;
- staged count;
- package.json SHA-256;
- all Repair-8 source/resource SHA-256 values;
- existing root-level VSIX filenames, sizes, and mtimes.

Do not mutate the source tree during preflight.

If repository identity or version differs, stop with:

REPAIR_8_BUILD_GATE_ENVIRONMENT_MISMATCH

==================================================
3. SOURCE BYTE-FREEZE
==================================================

The source and resource bytes accepted by the independent re-audit must remain
unchanged.

Before the build, hash at minimum:

- all 21 Repair-8 authorized files;
- package.json;
- .vscodeignore;
- src/test/testPatterns.ts;
- resources/framework/contracts/oracle-delivery-controls.v1.json;
- resources/framework/contracts/job-config-envelope.v1.json.

At task end, re-hash the same files.

Required:

SOURCE_OR_RESOURCE_DRIFT_DURING_BUILD: 0

Build-generated ignored files under out/** and TypeScript build metadata are
not source drift.

==================================================
4. COMPILE AND LINT
==================================================

Using already-installed dependencies only, run:

- production compile;
- lint.

Required:

COMPILE_PASS: YES
LINT_PASS: YES

If either fails, stop.

Do not modify code to repair a failure in this task.

==================================================
5. RUN THE TRUSTED CONTRACT SUITE DIRECTLY
==================================================

The independent re-audit found that:

src/test/suite/trustedJobConfigEnvelope.test.ts

is not currently included in PURE_UNIT_TEST_PATTERNS.

Do NOT edit src/test/testPatterns.ts in this task.

Compile the test tree and execute the compiled trusted contract suite directly.

Required:

TRUSTED_JOB_CONFIG_ENVELOPE_DIRECT_SUITE_PASS: YES

Report the exact passing/failing count.

This direct run is required in addition to npm run test:unit.

==================================================
6. BUILD EXACTLY ONE FRESH 0.3.140 GATE VSIX
==================================================

Build exactly one new VSIX from the current Repair-8 source.

Do not reuse an existing VSIX.
Do not rename an existing VSIX.
Do not delete existing VSIX artifacts.
Do not install the result.

Use an explicit output filename that cannot be confused with the final
0.3.141 QA candidate:

databricks-etl-copilot-0.3.140-repair8-build-gate.vsix

The exact expected location is:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.140-repair8-build-gate.vsix

Use the repository's normal package preparation and the already-installed VSCE
binary.

No npm install, npx download, or dependency update is permitted.

Record:

- command used;
- exit code;
- build timestamp;
- absolute path;
- SHA-256;
- archive entry count;
- compressed size;
- uncompressed size;
- largest entry;
- internal package.json version;
- internal extension.vsixmanifest version.

Required internal version:

0.3.140

==================================================
7. VERIFY THE EXACT NEW VSIX BY EXPLICIT PATH
==================================================

Do not rely only on newest-file selection.

Run the repository verifier against the exact absolute path of:

databricks-etl-copilot-0.3.140-repair8-build-gate.vsix

Verify all existing package-security controls remain active:

- required entries;
- forbidden entries;
- size ceilings;
- archive entry ceilings;
- content markers;
- manifest checks;
- machine-path scanning;
- unrelated-repository scanning;
- source/test/build-artifact exclusion;
- credentials and secret scans;
- nested .git exclusion;
- nested VSIX exclusion;
- .tmp exclusion;
- .tsbuildinfo exclusion.

Specifically verify these two entries exist:

extension/resources/framework/contracts/oracle-delivery-controls.v1.json

extension/resources/framework/contracts/job-config-envelope.v1.json

Also verify the packaged job-config contract bytes match the current source
contract bytes exactly.

Required:

EXACT_NEW_VSIX_VERIFIER_PASS: YES
JOB_CONFIG_ENVELOPE_PRESENT_IN_VSIX: YES
JOB_CONFIG_ENVELOPE_SOURCE_PACKAGE_HASH_MATCH: YES
ORACLE_CONTRACT_PRESENT_IN_VSIX: YES

==================================================
8. INDEPENDENT PACKAGE INSPECTION
==================================================

In addition to the repository verifier, inspect the new VSIX archive using an
independent ZIP central-directory reader.

Confirm:

- the new Job Config contract exists;
- the Oracle contract exists;
- internal version is 0.3.140;
- no developer-machine absolute paths exist;
- no unrelated repositories exist;
- no .tmp/** exists;
- no nested .git/** exists;
- no source test tree exists;
- no out/test/** exists;
- no node_modules/** exists;
- no .tsbuildinfo exists;
- no nested VSIX exists;
- no credentials or secrets are evident;
- required Copilot agents, skills, instructions, context, knowledge, prompts,
  framework contracts, runtime bundles, and media are present.

Do not extract files into the repository.

Use an OS temporary directory only if extraction is necessary and remove only
that task-created temporary directory afterward.

==================================================
9. RUN REPAIR-8 AND REPAIR-5/6/7 REGRESSIONS
==================================================

Run all eight Repair-8 focused suites:

- trustedJobConfigEnvelope.test
- configExplain.test
- firstRenderInvariantGuard.test
- EtlReadOnlyToolService.test
- jobDevelopmentReadiness.test
- packageAssets.test
- etlActionTools.test
- hf1OracleFreshConsumer.test

Also run relevant Repair-5/6/7 regression suites, including:

- physicalWriteContainment;
- workspaceInputContainment;
- onboardingWriteApproval;
- repoWriterWorkspaceSelection;
- createPreviewFlow;
- artifactReuseConversation;
- repoContextInit;
- trusted framework definition resolver;
- trusted write authorization.

All must pass.

No source change is authorized if a test fails.

==================================================
10. RUN THE FULL UNIT SUITE
==================================================

Run the full unit suite after the fresh build-gate VSIX exists.

First report which exact VSIX the suite selects.

It must select:

databricks-etl-copilot-0.3.140-repair8-build-gate.vsix

or otherwise explicitly bind the VSIX-dependent check to that exact artifact.

Do not silently accept selection of an older VSIX.

Expected failure set after the stale-artifact issue is removed:

A. Two Phase-H/EvalGating baseline-freshness failures.

B. Three pre-existing protected Copilot workflow-customization failures.

Expected total:

5 failures

The previous sixth failure must disappear:

VSIX machine-specific path scan
>
built VSIX (when present) contains no machine-specific absolute path

must no longer fail because the new contract must be present.

Classify every failure by exact test name.

Required:

FULL_UNIT_FAILURE_COUNT: 5
STALE_VSIX_FAILURE_REMAINING: NO
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

If an additional failure exists, stop with:

REPAIR_8_FRESH_BUILD_GATE_FAILED

Do not repair it during this task.

==================================================
11. CHECK THE FAIL-OPEN PACKAGING DEPENDENCY
==================================================

The independent audit documented that the two Repair-8 invariants become inert
if the trusted contract is unavailable.

Do not redesign that behavior in this task.

Instead prove that the newly built artifact contains and resolves the trusted
contract through the installed-resource path.

Report:

PACKAGED_CONTRACT_PRESENT: YES/NO
PACKAGED_CONTRACT_RESOLVABLE_FROM_INSTALLED_LAYOUT: YES/NO
REPAIR_8_INVARIANTS_ACTIVE_IN_NEW_PACKAGE: YES/NO

This proof is required because package presence is currently a load-bearing
release condition.

==================================================
12. KNOWN DEFERRED ITEMS
==================================================

Record but do not repair:

1. FirstRenderInvariantGuard contract-unavailable fail-open behavior.
2. trustedJobConfigEnvelope.test.ts absence from PURE_UNIT_TEST_PATTERNS.
3. VSIX newest-mtime selection logic is not source/version-aware.
4. The low-severity degenerate modules/options shape precision gap.
5. The known Phase-H baseline refresh chore.
6. The three protected customization failures.

Do not promote any of these into a Repair-8 source failure unless live evidence
contradicts the independent re-audit.

==================================================
13. END-STATE SCOPE PROOF
==================================================

At task end report:

- exact newly created VSIX path;
- exact generated temporary/build artifacts;
- source/resource hash mismatch count;
- staged count;
- package.json version;
- package.json hash match;
- unauthorized source path count;
- dependency installs/downloads;
- consumer workspace mutations;
- etl-framework-adb mutations;
- Git mutations;
- VSIX installations.

Required:

VERSION_AFTER_BUILD_GATE: 0.3.140
SOURCE_OR_RESOURCE_DRIFT_DURING_BUILD: 0
UNAUTHORIZED_SOURCE_CHANGED_PATHS: 0
STAGED_COUNT: 0
DEPENDENCY_INSTALLS_OR_DOWNLOADS: 0
CONSUMER_WORKSPACE_MUTATIONS: 0
ETL_FRAMEWORK_ADB_MUTATIONS: 0
GIT_MUTATIONS: 0
VSIX_INSTALLATIONS: 0
FRESH_VSIX_CREATED_COUNT: 1

Do not delete the fresh build-gate VSIX at task end.

==================================================
14. FINAL MARKERS
==================================================

Return:

REPOSITORY_IDENTITY_MATCH: YES/NO
VERSION_BEFORE_BUILD_GATE: 0.3.140
VERSION_AFTER_BUILD_GATE: 0.3.140
SOURCE_BYTES_PRESERVED: YES/NO
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
TRUSTED_JOB_CONFIG_ENVELOPE_DIRECT_SUITE_PASS: YES/NO
FOCUSED_REPAIR_8_TESTS_PASS: YES/NO
REPAIR_5_6_7_REGRESSIONS_PASS: YES/NO
FRESH_BUILD_GATE_VSIX_CREATED: YES/NO
FRESH_BUILD_GATE_VSIX_PATH: <absolute path>
FRESH_BUILD_GATE_VSIX_SHA256: <sha256>
FRESH_BUILD_GATE_VSIX_INTERNAL_VERSION: <version>
EXACT_NEW_VSIX_VERIFIER_PASS: YES/NO
JOB_CONFIG_ENVELOPE_PRESENT_IN_VSIX: YES/NO
JOB_CONFIG_ENVELOPE_SOURCE_PACKAGE_HASH_MATCH: YES/NO
ORACLE_CONTRACT_PRESENT_IN_VSIX: YES/NO
PACKAGED_CONTRACT_RESOLVABLE_FROM_INSTALLED_LAYOUT: YES/NO
REPAIR_8_INVARIANTS_ACTIVE_IN_NEW_PACKAGE: YES/NO
FULL_UNIT_FAILURE_COUNT: <number>
FULL_UNIT_HISTORICAL_AND_PREEXISTING_FAILURES_ONLY: YES/NO
STALE_VSIX_FAILURE_REMAINING: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: <number>
NEW_SECURITY_REGRESSIONS: <number>
SOURCE_OR_RESOURCE_DRIFT_DURING_BUILD: <number>
UNAUTHORIZED_SOURCE_CHANGED_PATHS: <number>
VSIX_INSTALLED: NO
VERSION_BUMP_PERFORMED: NO
GIT_MUTATION_PERFORMED: NO
READY_FOR_0_3_141_VERSION_BUMP: YES/NO

End exactly with one:

LOCAL_HOTFIX_HF1_V2_REPAIR_8_FRESH_0_3_140_BUILD_GATE_PASS

LOCAL_HOTFIX_HF1_V2_REPAIR_8_FRESH_0_3_140_BUILD_GATE_FAIL

LOCAL_HOTFIX_HF1_V2_REPAIR_8_FRESH_0_3_140_BUILD_GATE_BLOCKED
