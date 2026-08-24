TASK: LOCAL_HOTFIX_HF1_V2_QA_VERSION_BUMP_0_3_141_AND_FINAL_DEVELOPMENT_TEST_PACKAGE

Perform the bounded version bump and final Development-Test package build for
the accepted HF1 V2 Repair-8 candidate.

This task runs in the SOFTWARE DEVELOPMENT ENVIRONMENT.

The accepted Repair-8 source and security implementation must remain
byte-identical.

Authorized actions:

1. change only the package.json version:
   0.3.140 -> 0.3.141

2. compile and lint;

3. run the trusted Job Config contract suite directly;

4. run Repair-8 and Repair-5/6/7 regression suites;

5. build exactly one new standard-named VSIX:

   databricks-etl-copilot-0.3.141.vsix

6. verify that exact VSIX by explicit absolute path;

7. run the full unit suite after the final VSIX exists;

8. inspect the package read-only and compare it with the accepted
   0.3.140 Repair-8 build-gate artifact.

This task is NOT authorized to install the VSIX or execute runtime QA.

Do NOT modify any production TypeScript file.
Do NOT modify any test file.
Do NOT modify any resource, contract, context, knowledge, prompt, skill, agent,
instruction, packaging-policy, workflow, or framework file.
Do NOT modify package-lock.json.
Do NOT run npm version because it may create Git state or tags.
Do NOT install or download dependencies.
Do NOT regenerate Phase-H baselines.
Do NOT modify .github/**.
Do NOT modify resources/prompts/**.
Do NOT modify AGENT.md or AGENTS.md.
Do NOT modify etl-framework-adb.
Do NOT modify a Development Test Workspace or consumer repository.
Do NOT install the resulting VSIX.
Do NOT stage, commit, push, reset, restore, checkout, stash, clean, tag, or
otherwise mutate Git state.
Do NOT delete, rename, overwrite, or modify older VSIX artifacts.

Use only already-installed dependencies and the already-installed VSCE binary.

==================================================
1. ACCEPTED BUILD-GATE EVIDENCE
==================================================

Accept these completed findings:

REPAIR_8_FRESH_BUILD_GATE_PASS: YES
REPOSITORY_IDENTITY_MATCH: YES
SOURCE_OR_RESOURCE_DRIFT_DURING_BUILD: 0
COMPILE_PASS: YES
LINT_PASS: YES
TRUSTED_JOB_CONFIG_ENVELOPE_DIRECT_SUITE_PASS: YES
FOCUSED_REPAIR_8_TESTS_PASS: YES
REPAIR_5_6_7_REGRESSIONS_PASS: YES
FULL_UNIT_FAILURE_COUNT: 5
STALE_VSIX_FAILURE_REMAINING: NO
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0
PACKAGED_CONTRACT_PRESENT: YES
PACKAGED_CONTRACT_RESOLVABLE_FROM_INSTALLED_LAYOUT: YES
REPAIR_8_INVARIANTS_ACTIVE_IN_NEW_PACKAGE: YES

Accepted build-gate artifact:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.140-repair8-build-gate.vsix

Do not use that artifact as the final Development-Test package.

Do not repeat Repair-8 architecture discovery.

==================================================
2. SOFTWARE DEVELOPMENT ENVIRONMENT PREFLIGHT
==================================================

Expected repository root:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected base HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected package name:

databricks-etl-copilot

Expected current version:

0.3.140

Expected publisher:

td-etl

Expected package-lock.json:

absent

Verify all values before mutation.

Also verify that the accepted build-gate VSIX exists and record its:

- absolute path;
- SHA-256;
- archive entry count;
- internal package.json version;
- internal extension.vsixmanifest version.

Capture before-task:

- tracked-modified path inventory;
- untracked path inventory;
- staged count;
- package.json SHA-256;
- all existing root-level VSIX paths, sizes, SHA-256 values, and mtimes;
- SHA-256 for all Repair-5/6/7/8 source, test, resource, policy, and contract
  files.

If repository identity, branch, HEAD, or current version differs, stop without
editing and return:

HF1_V2_0_3_141_VERSION_BUMP_ENVIRONMENT_MISMATCH

==================================================
3. EXACT AUTHORIZED SOURCE EDIT
==================================================

The only authorized source-file modification is:

package.json

Change exactly:

"version": "0.3.140"

to:

"version": "0.3.141"

Do not use `npm version`.

Perform a direct single-field edit.

Do not reformat, reorder, normalize, or rewrite package.json.

Immediately verify:

- exactly one tracked source path was modified by this task;
- that path is package.json;
- the task-attributable package.json diff is exactly one removed version line
  and one added version line;
- all other package.json fields remain byte-equivalent;
- package-lock.json remains absent;
- no other source/resource/test/config path changed.

If any additional path changes, stop before building and return:

HF1_V2_0_3_141_VERSION_BUMP_SCOPE_DRIFT

==================================================
4. SOURCE AND REPAIR BYTE FREEZE
==================================================

All accepted Repair-5/6/7/8 implementation bytes must remain unchanged.

Re-hash the previously captured source, test, resource, contract, and package
policy files after the version edit.

Required:

REPAIR_5_6_7_8_NON_VERSION_FILE_DRIFT: 0

The only permitted source hash change is:

package.json

and only because of the version token.

Do not include ignored out/** output or the newly generated VSIX as source
drift.

==================================================
5. COMPILE AND LINT
==================================================

Using existing dependencies only, run:

npm run compile
npm run lint

Required:

COMPILE_PASS: YES
LINT_PASS: YES

Confirm the npm banner reports version:

0.3.141

If compile or lint fails, do not repair code in this task.

Return:

HF1_V2_0_3_141_FINAL_PACKAGE_VALIDATION_FAILED

==================================================
6. RUN TRUSTED CONTRACT SUITE DIRECTLY
==================================================

The following suite is not yet registered in PURE_UNIT_TEST_PATTERNS:

src/test/suite/trustedJobConfigEnvelope.test.ts

Do not modify src/test/testPatterns.ts in this task.

Compile the test output and execute the compiled suite directly using the same
working VS Code stub/register harness previously proven.

Required:

TRUSTED_JOB_CONFIG_ENVELOPE_DIRECT_SUITE_PASS: YES

Expected current result:

28 passing
0 failing

Report actual values honestly.

==================================================
7. PRE-PACKAGE FOCUSED VALIDATION
==================================================

Run all eight Repair-8 focused suites:

1. trustedJobConfigEnvelope
2. configExplain
3. firstRenderInvariantGuard
4. EtlReadOnlyToolService
5. jobDevelopmentReadiness
6. packageAssets
7. etlActionTools
8. hf1OracleFreshConsumer

Run all relevant Repair-5/6/7 regression suites, including:

- physicalWriteContainment;
- workspaceInputContainment;
- onboardingWriteApproval;
- repoWriterWorkspaceSelection;
- createPreviewFlow;
- artifactReuseConversation;
- repoContextInit;
- TrustedFrameworkDefinitionResolver;
- WriteAuthorization / TrustedWriteApprovalStore.

Required:

FOCUSED_REPAIR_8_TESTS_PASS: YES
REPAIR_5_6_7_REGRESSIONS_PASS: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

Do not change source if a suite fails.

==================================================
8. FINAL ARTIFACT NAME AND COLLISION CHECK
==================================================

The final Development-Test package must use the standard filename:

databricks-etl-copilot-0.3.141.vsix

Expected absolute path:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix

Before building, verify that this exact file does not already exist.

If it exists, do not overwrite, delete, rename, or reuse it.

Stop and return:

HF1_V2_0_3_141_FINAL_ARTIFACT_COLLISION

Do not use a descriptive suffix for the final 0.3.141 artifact.

The standard name is intentional because the Packaged Runtime tests resolve:

databricks-etl-copilot-${version}.vsix

by exact filename.

==================================================
9. BUILD EXACTLY ONE FINAL 0.3.141 VSIX
==================================================

Build exactly one new VSIX from the current source:

databricks-etl-copilot-0.3.141.vsix

Use an explicit `--out` path.

Use the already-installed VSCE binary.

Do not invoke an npx path that downloads anything.

Do not build a second package.
Do not manually edit the archive.
Do not rename another VSIX.
Do not reuse the 0.3.140 build-gate VSIX.

Record:

- command;
- exit code;
- absolute output path;
- build timestamp;
- SHA-256;
- file size;
- archive entry count;
- total compressed-entry bytes;
- total uncompressed-entry bytes;
- largest archive entry;
- internal package.json version;
- internal extension.vsixmanifest version.

Required:

FINAL_0_3_141_VSIX_CREATED_COUNT: 1
FINAL_0_3_141_INTERNAL_PACKAGE_VERSION: 0.3.141
FINAL_0_3_141_INTERNAL_MANIFEST_VERSION: 0.3.141

==================================================
10. VERIFY THE EXACT FINAL VSIX
==================================================

Run the project package verifier against the exact absolute path:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix

Do not rely only on newest-mtime discovery.

Required package checks include:

- required entries;
- required content markers;
- manifest checks;
- entry count ceiling;
- compressed-size ceiling;
- uncompressed-size ceiling;
- single-entry ceiling;
- machine-specific absolute path scan;
- credential/secret scan;
- unrelated-repository scan;
- source TypeScript exclusion;
- test-tree exclusion;
- out/test exclusion;
- node_modules exclusion;
- docs/eval exclusion;
- .vscode-test exclusion;
- .tmp exclusion;
- nested .git exclusion;
- nested VSIX exclusion;
- .tsbuildinfo exclusion;
- source-map exclusion;
- maintainer/developer-only file exclusion.

Explicitly verify these entries:

extension/resources/framework/contracts/oracle-delivery-controls.v1.json

extension/resources/framework/contracts/job-config-envelope.v1.json

Verify that both packaged contract byte sequences match the current source
contract files exactly.

Required:

FINAL_EXACT_VSIX_VERIFIER_PASS: YES
JOB_CONFIG_ENVELOPE_PRESENT_IN_FINAL_VSIX: YES
JOB_CONFIG_ENVELOPE_SOURCE_PACKAGE_HASH_MATCH: YES
ORACLE_CONTRACT_PRESENT_IN_FINAL_VSIX: YES
ORACLE_CONTRACT_SOURCE_PACKAGE_HASH_MATCH: YES
PACKAGE_MACHINE_PATH_HITS: 0
PACKAGE_SECRET_HITS: 0
PACKAGE_UNRELATED_REPOSITORY_ENTRIES: 0

==================================================
11. INDEPENDENT ARCHIVE INSPECTION
==================================================

Independently inspect the final VSIX using an OS ZIP central-directory reader,
not only the repository verifier.

Confirm:

- internal package version is 0.3.141;
- internal manifest version is 0.3.141;
- both trusted contracts exist;
- required agents, skills, instructions, context, knowledge, prompts,
  framework contracts, runtime bundles, and media exist;
- every mandatory forbidden class is absent;
- no developer-machine absolute path exists;
- no credential or secret is evident;
- no unrelated repository tree exists.

Do not extract into the repository.

Any temporary extraction must be under an OS temporary folder created only for
this task.

==================================================
12. COMPARE 0.3.140 GATE VSIX TO 0.3.141 FINAL VSIX
==================================================

Compare these two artifacts read-only:

A. Accepted Repair-8 build-gate:

databricks-etl-copilot-0.3.140-repair8-build-gate.vsix

B. Final Development-Test artifact:

databricks-etl-copilot-0.3.141.vsix

Verify:

- entry-name sets are identical;
- no runtime, contract, agent, skill, context, knowledge, prompt, instruction,
  or media entry was added or removed;
- all non-version-bearing entry bytes are identical;
- only version-bearing metadata differs.

Expected differing archive entries:

1. extension/package.json
2. extension.vsixmanifest

If another archive entry differs, report its exact path and byte/hash
difference.

Do not silently accept additional differences.

Required:

GATE_TO_FINAL_ENTRY_SET_IDENTICAL: YES
GATE_TO_FINAL_NON_VERSION_BYTES_IDENTICAL: YES
GATE_TO_FINAL_ONLY_VERSION_METADATA_DIFFERS: YES

==================================================
13. VERIFY BOTH VSIX SELECTION STRATEGIES
==================================================

The previous gate recorded two inconsistent selectors:

- newest-mtime selector;
- exact-version-filename selector.

Do not repair selector code in this task.

After building the standard-named 0.3.141 artifact, prove that both selectors
resolve to:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix

Required:

NEWEST_MTIME_VSIX_SELECTOR_TARGET: databricks-etl-copilot-0.3.141.vsix
EXACT_VERSION_VSIX_SELECTOR_TARGET: databricks-etl-copilot-0.3.141.vsix
VSIX_SELECTORS_CONVERGE_FOR_FINAL_ARTIFACT: YES

Do not rely on the selection result as a substitute for explicit-path package
verification.

==================================================
14. RUN FULL UNIT SUITE AFTER FINAL PACKAGE EXISTS
==================================================

Run:

npm run test:unit

after the final standard-named 0.3.141 VSIX has been built and verified.

Before reporting the result, state:

- which VSIX the newest-mtime test selected;
- which VSIX the exact-version helper selected.

The three STTM packaged-runtime tests that previously remained pending because
the exact default filename did not exist must now execute against:

databricks-etl-copilot-0.3.141.vsix

Required:

STTM_PACKAGED_RUNTIME_TESTS_EXECUTED: YES
STTM_PACKAGED_RUNTIME_PENDING_COUNT: 0

The only permitted pending test is the known Confluence-offline fallback,
provided its exact test name is reported.

Expected pending result:

FULL_UNIT_PENDING_COUNT: 1

Expected full-suite failures remain exactly five:

A. Two Phase-H/EvalGating baseline-freshness failures.

B. Three protected Copilot workflow-customization failures.

List all five by exact test name.

Required:

FULL_UNIT_FAILURE_COUNT: 5
PHASE_H_BASELINE_FRESHNESS_FAILURE_COUNT: 2
PROTECTED_CUSTOMIZATION_FAILURE_COUNT: 3
STALE_VSIX_FAILURE_REMAINING: NO
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

If a sixth or otherwise new failure occurs, do not repair it in this task.

Return:

HF1_V2_0_3_141_FINAL_PACKAGE_VALIDATION_FAILED

==================================================
15. PACKAGED CONTRACT RESOLUTION FROM FINAL LAYOUT
==================================================

Extract the final 0.3.141 package read-only into an OS temporary installed-layout
simulation.

Set process.cwd() to a separate neutral empty directory.

Prove that TrustedJobConfigEnvelopeResolver resolves:

resources/framework/contracts/job-config-envelope.v1.json

from the packaged installed layout, not from the source checkout or cwd
fallback.

Required:

FINAL_PACKAGED_CONTRACT_PRESENT: YES
FINAL_PACKAGED_CONTRACT_RESOLVABLE_FROM_INSTALLED_LAYOUT: YES
CWD_FALLBACK_COULD_LEAK_SOURCE_CONTRACT: NO
REPAIR_8_INVARIANTS_ACTIVE_IN_FINAL_PACKAGE: YES

Also execute the negative control with an empty layout and verify the contract
is not fabricated from cwd.

Do not redesign the deferred guard-level fail-open behavior in this task.

==================================================
16. SOURCE AND END-STATE BYTE PROOF
==================================================

After all builds and tests:

- re-hash every frozen Repair-5/6/7/8 non-version file;
- re-hash package.json;
- compare tracked and untracked inventories;
- compare staged count;
- inspect .github/**;
- inspect resources/prompts/**;
- inspect AGENT.md and AGENTS.md;
- inspect etl-framework-adb;
- inspect Development Test Workspaces;
- inspect dependency directories and cache mtimes where relevant.

Required:

NON_VERSION_SOURCE_OR_RESOURCE_DRIFT: 0
TASK_ATTRIBUTABLE_TRACKED_SOURCE_FILES: 1
TASK_ATTRIBUTABLE_TRACKED_SOURCE_PATH: package.json
PACKAGE_JSON_DIFF_IS_VERSION_ONLY: YES
VERSION_AFTER_TASK: 0.3.141
STAGED_COUNT: 0
GIT_COMMITS_CREATED: 0
GIT_PUSHES_PERFORMED: 0
GIT_TAGS_CREATED: 0
DEPENDENCY_INSTALLS_OR_DOWNLOADS: 0
VSIX_INSTALLATIONS: 0
CONSUMER_OR_DEVELOPMENT_TEST_WORKSPACE_MUTATIONS: 0
ETL_FRAMEWORK_ADB_MUTATIONS: 0
UNAUTHORIZED_SOURCE_CHANGED_PATHS: 0
FINAL_0_3_141_VSIX_RETAINED: YES

Do not delete the accepted 0.3.140 build-gate VSIX or older ignored artifacts.

==================================================
17. DEFERRED ITEMS
==================================================

Record but do not repair:

1. FirstRenderInvariantGuard contract-unavailable fail-open behavior.
2. trustedJobConfigEnvelope.test.ts absence from PURE_UNIT_TEST_PATTERNS.
3. VSIX selection logic is not source/version-freshness aware.
4. Low-severity degenerate modules/options shape precision gap.
5. Phase-H baseline refresh chore.
6. Three protected Copilot workflow-customization failures.
7. Context ownership and trust-boundary redesign.
8. Direct Unity Catalog table-name write support.

Do not add any of these to this one-file version-bump scope.

==================================================
18. FINAL REPORT
==================================================

Return:

REPOSITORY_IDENTITY_MATCH: YES/NO
SOURCE_VERSION_BEFORE: 0.3.140
SOURCE_VERSION_AFTER: 0.3.141
ONLY_PACKAGE_JSON_SOURCE_CHANGED_BY_TASK: YES/NO
PACKAGE_JSON_DIFF_IS_VERSION_ONLY: YES/NO
NON_VERSION_REPAIR_BYTES_PRESERVED: YES/NO
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
TRUSTED_JOB_CONFIG_ENVELOPE_DIRECT_SUITE_PASS: YES/NO
FOCUSED_REPAIR_8_TESTS_PASS: YES/NO
REPAIR_5_6_7_REGRESSIONS_PASS: YES/NO
FINAL_0_3_141_VSIX_CREATED_COUNT: <number>
FINAL_0_3_141_VSIX_PATH: <absolute path>
FINAL_0_3_141_VSIX_SHA256: <sha256>
FINAL_0_3_141_INTERNAL_PACKAGE_VERSION: <version>
FINAL_0_3_141_INTERNAL_MANIFEST_VERSION: <version>
FINAL_EXACT_VSIX_VERIFIER_PASS: YES/NO
FINAL_INDEPENDENT_PACKAGE_INSPECTION_CLEAN: YES/NO
JOB_CONFIG_ENVELOPE_PRESENT_IN_FINAL_VSIX: YES/NO
JOB_CONFIG_ENVELOPE_SOURCE_PACKAGE_HASH_MATCH: YES/NO
ORACLE_CONTRACT_PRESENT_IN_FINAL_VSIX: YES/NO
ORACLE_CONTRACT_SOURCE_PACKAGE_HASH_MATCH: YES/NO
GATE_TO_FINAL_ENTRY_SET_IDENTICAL: YES/NO
GATE_TO_FINAL_NON_VERSION_BYTES_IDENTICAL: YES/NO
GATE_TO_FINAL_ONLY_VERSION_METADATA_DIFFERS: YES/NO
VSIX_SELECTORS_CONVERGE_FOR_FINAL_ARTIFACT: YES/NO
STTM_PACKAGED_RUNTIME_TESTS_EXECUTED: YES/NO
STTM_PACKAGED_RUNTIME_PENDING_COUNT: <number>
FULL_UNIT_PENDING_COUNT: <number>
FULL_UNIT_FAILURE_COUNT: <number>
FULL_UNIT_EXPECTED_FAILURES_ONLY: YES/NO
STALE_VSIX_FAILURE_REMAINING: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: <number>
NEW_SECURITY_REGRESSIONS: <number>
FINAL_PACKAGED_CONTRACT_RESOLVABLE_FROM_INSTALLED_LAYOUT: YES/NO
REPAIR_8_INVARIANTS_ACTIVE_IN_FINAL_PACKAGE: YES/NO
NON_VERSION_SOURCE_OR_RESOURCE_DRIFT: <number>
UNAUTHORIZED_SOURCE_CHANGED_PATHS: <number>
VERSION_BUMP_PERFORMED: YES/NO
VSIX_INSTALLED: NO
GIT_MUTATION_PERFORMED: NO
READY_FOR_DEVELOPMENT_TEST_RUNTIME_QA: YES/NO
SAFE_TO_COMMIT_BEFORE_RUNTIME_QA: NO
SAFE_TO_RELEASE: NO

End exactly with one:

LOCAL_HOTFIX_HF1_V2_QA_VERSION_BUMP_0_3_141_FINAL_PACKAGE_PASS

LOCAL_HOTFIX_HF1_V2_QA_VERSION_BUMP_0_3_141_FINAL_PACKAGE_FAIL

LOCAL_HOTFIX_HF1_V2_QA_VERSION_BUMP_0_3_141_FINAL_PACKAGE_BLOCKED
