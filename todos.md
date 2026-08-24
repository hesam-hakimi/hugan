TASK: HF1_V2_BUILD_AND_VERIFY_FINAL_DEVELOPMENT_TEST_VSIX_0_3_141

Work only inside the Software Development Environment:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

This task corrects the current live state:

* the last confirmed built and active Extension version is 0.3.140;
* version 0.3.141 has not yet been built;
* Runtime QA Phase 1 for 0.3.141 must not start until this build/package gate passes;
* any earlier handoff claim that a verified 0.3.141 VSIX or its SHA already
    exists is not live evidence and must not be trusted.

Do not use web search.
Do not access or modify any Development Test Workspace.
Do not access or modify etl-framework-adb.
Do not install or download dependencies.
Do not use npm version.
Do not create package-lock.json.
Do not commit, push, merge, tag, stash, reset, clean, or delete files.
Do not modify protected .github/** assets.
Do not modify tests or baselines to make failures disappear.
Do not reopen or redesign Repairs 3–8.
Do not install the resulting VSIX.
Do not start Runtime QA.

==================================================

1. VERIFY SOFTWARE DEVELOPMENT ENVIRONMENT IDENTITY
    ==================================================

Before making any change, verify and report:

EXPECTED_REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

EXPECTED_ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

EXPECTED_BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

EXPECTED_BASE_HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

Capture:

* absolute repository root;
* origin URL;
* current branch;
* current HEAD;
* staged file count;
* tracked-modified paths;
* untracked paths;
* current package.json version;
* package-lock.json presence;
* existing VSIX files matching 0.3.140 and 0.3.141.

A large existing local working-tree overlay is expected. Preserve it exactly.

Do not assume the working tree is clean.
Do not reset, restore, stash, clean, or remove any existing user changes.

If repository root, origin, branch, or HEAD conflicts with the expected identity,
stop without changing anything and return:

BUILD_0_3_141_RESULT: BLOCKED_IDENTITY_MISMATCH

If staged changes exist, report them and stop without changing anything:

BUILD_0_3_141_RESULT: BLOCKED_STAGED_CHANGES

If an unexpected 0.3.141 VSIX already exists, do not overwrite or delete it.
Inspect and report its path, version metadata, size, and SHA-256, then stop with:

BUILD_0_3_141_RESULT: BLOCKED_UNEXPECTED_EXISTING_ARTIFACT

==================================================
2. VERIFY CURRENT VERSION STATE

Read the authoritative live version from package.json.

Accepted starting states:

A. package.json version is 0.3.140:

* authorize exactly one intentional source edit;
* change only the package.json version token:
    “version”: “0.3.140”
    to
    “version”: “0.3.141”

B. package.json version is already 0.3.141, but no 0.3.141 VSIX exists:

* do not edit package.json again;
* continue to validation and packaging.

Any other source version is a conflict. Stop without changing it:

BUILD_0_3_141_RESULT: BLOCKED_VERSION_MISMATCH

Do not use npm version.
Do not generate or modify a lockfile.
Do not modify publisher, extension ID, scripts, dependencies, source,
resources, tests, contracts, or package policy.

Expected extension identity:

PUBLISHER: td-etl
PACKAGE_NAME: databricks-etl-copilot
EXTENSION_ID: td-etl.databricks-etl-copilot
TARGET_VERSION: 0.3.141

==================================================
3. PRE-BUILD CHANGE BOUNDARY

After the conditional version edit, compare the working tree with the captured
baseline.

The only task-attributable intentional source change permitted is:

package.json

* version 0.3.140 → 0.3.141

Existing changes that predate this task must remain untouched.

Generated output produced by existing compile/package commands must be reported
separately and must not be described as an intentional source edit.

If any other task-attributable source/resource/test/configuration path changes,
stop and report:

BUILD_0_3_141_RESULT: FAIL_UNAUTHORIZED_CHANGE

==================================================
4. RUN EXISTING VALIDATION GATES

Inspect package.json and the existing repository validation scripts to identify
the canonical local commands already used by this project.

Use only existing local dependencies and existing repository scripts.
Do not download packages or change validation configuration.

Run and report:

1. TypeScript compile;
2. lint;
3. trusted Job Config envelope direct suite;
4. Repair 8 focused suites;
5. Repair 5/6/7 regression suites;
6. the full unit suite.

Do not modify tests, baselines, snapshots, prompts, contracts, or source to
change the result.

For every gate report:

* exact command;
* exit code;
* passing count;
* pending/skipped count;
* failing count;
* failure names;
* whether each failure is historical/known or new;
* whether any new functional regression exists;
* whether any new security regression exists.

Known historical failures may remain visible, but they must not be hidden.
Any new functional or security regression blocks packaging acceptance.

Required:

COMPILE_PASS: YES
LINT_PASS: YES
TRUSTED_JOB_CONFIG_ENVELOPE_DIRECT_SUITE_PASS: YES
REPAIR_8_FOCUSED_SUITES_PASS: YES
REPAIR_5_6_7_REGRESSION_SUITES_PASS: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

If any required gate fails, do not repair source during this task.
Stop, preserve all evidence, and return:

BUILD_0_3_141_RESULT: FAIL_VALIDATION_GATE

==================================================
5. BUILD THE FINAL 0.3.141 VSIX

Use the existing canonical local packaging workflow.

Build exactly one final Development-Test artifact named:

databricks-etl-copilot-0.3.141.vsix

Expected final path:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix

Do not publish it.
Do not install it.
Do not overwrite an unexpected pre-existing 0.3.141 artifact.
Do not create a Git tag or commit.

==================================================
6. VERIFY THE EXACT FINAL PACKAGE

Run the repository’s existing exact-package verifier against the explicit final
0.3.141 VSIX path. Do not allow a “newest VSIX” selector to choose another file.

Independently inspect the produced archive and verify:

* the archive opens successfully;
* internal package.json version is exactly 0.3.141;
* internal extension.vsixmanifest version is exactly 0.3.141;
* publisher is td-etl;
* extension ID resolves to td-etl.databricks-etl-copilot;
* resources/framework/contracts/job-config-envelope.v1.json is present;
* the packaged Job Config envelope contract is byte-equal to source;
* the trusted Oracle contract is present;
* the packaged Oracle contract is byte-equal to source;
* packaged trusted contracts resolve from installed-layout structure;
* no etl-framework-adb checkout is required;
* no source-checkout path is embedded as a runtime dependency;
* no forbidden package-hygiene entries are present;
* no .tmp/** content is present;
* no nested .git/** content is present;
* no .tsbuildinfo* content is present;
* no source tests or out-test content is present;
* package entry and size limits pass.

If the exact verified 0.3.140 package is available locally, compare the
decompressed entry sets and entry bytes.

Expected comparison:

* the same package entry set;
* all non-version content bytes unchanged;
* only package/manifest version metadata differs.

Ignore ZIP container timestamps when comparing; compare entry names and
decompressed bytes.

If the exact trusted 0.3.140 comparison artifact cannot be identified
deterministically, report:

GATE_TO_FINAL_COMPARISON: NOT_PERFORMED_NO_TRUSTED_BASELINE

Do not guess or select an artifact only by newest modification time.

==================================================
7. COMPUTE THE REAL ARTIFACT IDENTITY

After all verification passes, calculate from the actual newly built file:

* absolute VSIX path;
* file size in bytes;
* SHA-256.

Do not reuse or expect any SHA recorded in the earlier handoff.
The SHA must be computed from the actual new artifact.

Report:

FINAL_VSIX_PATH: 
FINAL_VSIX_SIZE_BYTES: 
FINAL_VSIX_SHA256: 

==================================================
8. POST-BUILD SAFETY CHECK

Capture final Git status and compare it with the initial baseline.

Report separately:

* pre-existing tracked modifications;
* pre-existing untracked files;
* task-attributable package.json version edit;
* generated build/package artifacts;
* unexpected changes;
* staged files.

Required:

TASK_ATTRIBUTABLE_INTENTIONAL_SOURCE_CHANGES:

* package.json version token only, or NONE if it was already 0.3.141

STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
PACKAGE_LOCK_CREATED: NO
DEVELOPMENT_TEST_WORKSPACE_TOUCHED: NO
RUNTIME_QA_STARTED: NO

Do not commit or clean the repository.

==================================================
9. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION_BEFORE: 
SOURCE_VERSION_AFTER: 
VERSION_EDIT_REQUIRED: YES/NO
AUTHORIZED_SOURCE_CHANGED_PATHS: 
UNAUTHORIZED_SOURCE_CHANGED_PATHS: 
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
TRUSTED_JOB_CONFIG_ENVELOPE_DIRECT_SUITE_PASS: YES/NO
REPAIR_8_FOCUSED_SUITES_PASS: YES/NO
REPAIR_5_6_7_REGRESSION_SUITES_PASS: YES/NO
FULL_UNIT_PASSING_COUNT: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURES: 
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 
FINAL_EXACT_VSIX_VERIFIER_PASS: YES/NO
FINAL_INDEPENDENT_PACKAGE_INSPECTION_CLEAN: YES/NO
INTERNAL_PACKAGE_VERSION: 
INTERNAL_MANIFEST_VERSION: 
JOB_CONFIG_CONTRACT_PRESENT: YES/NO
JOB_CONFIG_CONTRACT_SOURCE_PACKAGE_HASH_MATCH: YES/NO
ORACLE_CONTRACT_PRESENT: YES/NO
ORACLE_CONTRACT_SOURCE_PACKAGE_HASH_MATCH: YES/NO
GATE_TO_FINAL_COMPARISON: PASS/FAIL/NOT_PERFORMED_NO_TRUSTED_BASELINE
FINAL_VSIX_PATH: 
FINAL_VSIX_SIZE_BYTES: 
FINAL_VSIX_SHA256: 
STAGED_FILES: 
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
PACKAGE_LOCK_CREATED: NO
READY_TO_INSTALL_0_3_141: YES/NO
READY_FOR_RUNTIME_QA_PHASE_1: YES/NO
SAFE_TO_COMMIT: NO
SAFE_TO_RELEASE: NO

PASS requires:

* correct repository identity;
* source version 0.3.141;
* only the authorized version-token source edit;
* all required compile/lint/focused/regression gates pass;
* zero new functional regressions;
* zero new security regressions;
* exact final VSIX verification passes;
* internal package and manifest versions are 0.3.141;
* trusted contracts are present and match source;
* actual SHA-256 is calculated;
* zero staged files;
* no commit, push, tag, install, or Runtime QA.

End exactly with one:

BUILD_0_3_141_RESULT: PASS

BUILD_0_3_141_RESULT: FAIL_VALIDATION_GATE

BUILD_0_3_141_RESULT: FAIL_PACKAGE_VERIFICATION

BUILD_0_3_141_RESULT: FAIL_UNAUTHORIZED_CHANGE

BUILD_0_3_141_RESULT: BLOCKED_IDENTITY_MISMATCH

BUILD_0_3_141_RESULT: BLOCKED_STAGED_CHANGES

BUILD_0_3_141_RESULT: BLOCKED_VERSION_MISMATCH

BUILD_0_3_141_RESULT: BLOCKED_UNEXPECTED_EXISTING_ARTIFACT
