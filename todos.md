TASK: HF1_V2_VERIFY_AND_ADOPT_PREEXISTING_VSIX_0_3_141

Work only inside the Software Development Environment:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Current confirmed situation:

* package.json already reports version 0.3.141;
* databricks-etl-copilot-0.3.141.vsix already exists;
* the previous build task stopped safely with:
    BUILD_0_3_141_RESULT: BLOCKED_UNEXPECTED_EXISTING_ARTIFACT
* the user reports that this may be an earlier experimental 0.3.141 package that
    was manually installed;
* installation history is not proof that this VSIX is the final verified package;
* the previous task left many validation fields as NOT_RUN or NOT_VERIFIED.

The goal of this task is to validate the exact existing 0.3.141 artifact and,
only if every required gate passes, adopt that same artifact as the final
Development Test VSIX without rebuilding it.

Do not use web search.
Do not access or modify the Development Test Workspace.
Do not access or modify etl-framework-adb.
Do not install or download dependencies.
Do not install or uninstall any VS Code extension.
Do not start Runtime QA.
Do not modify package.json.
Do not use npm version.
Do not create package-lock.json.
Do not delete, rename, move, overwrite, or rebuild the existing VSIX.
Do not create another VSIX.
Do not edit source, resources, tests, baselines, snapshots, contracts, or prompts.
Do not commit, push, merge, tag, stash, reset, clean, or restore files.
Do not modify protected .github/** assets.

==================================================

1. VERIFY REPOSITORY IDENTITY
    ==================================================

Verify:

EXPECTED_REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

EXPECTED_ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

EXPECTED_BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

EXPECTED_HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

EXPECTED_SOURCE_VERSION:
0.3.141

EXPECTED_ARTIFACT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix

Capture before running validations:

* absolute repository root;
* origin URL;
* current branch;
* current HEAD;
* staged paths;
* tracked-modified paths;
* untracked paths;
* package.json version;
* package-lock.json presence;
* exact artifact path;
* artifact size;
* artifact modification timestamp;
* artifact SHA-256.

A large pre-existing working-tree overlay may exist. Preserve it exactly.

If repository root, origin, branch, HEAD, or source version conflicts with the
expected identity, stop without modifying anything:

EXISTING_0_3_141_VERIFICATION_RESULT: BLOCKED_IDENTITY_MISMATCH

If staged files exist, report them and stop:

EXISTING_0_3_141_VERIFICATION_RESULT: BLOCKED_STAGED_CHANGES

If the exact VSIX is absent, stop. Do not build it:

EXISTING_0_3_141_VERIFICATION_RESULT: BLOCKED_ARTIFACT_ABSENT

==================================================
2. INSPECT THE EXISTING ARTIFACT READ-ONLY

Inspect the exact existing file:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix

Do not select an artifact by newest modification time.

Verify independently:

* the VSIX/ZIP archive opens successfully;
* internal package.json exists;
* internal package.json version is exactly 0.3.141;
* internal extension.vsixmanifest exists;
* manifest version is exactly 0.3.141;
* publisher is td-etl;
* package name is databricks-etl-copilot;
* extension ID resolves to td-etl.databricks-etl-copilot;
* resources/framework/contracts/job-config-envelope.v1.json is present;
* the packaged Job Config contract is byte-equal to the current source contract;
* the trusted Oracle delivery-control contract is present;
* the packaged Oracle contract is byte-equal to the current source contract;
* trusted contracts resolve using the installed-layout structure;
* no etl-framework-adb checkout is required at runtime;
* no absolute Software Development Environment path is embedded as a runtime
    dependency;
* no consumer-editable context is used as machine authority;
* no forbidden package-hygiene entries are present;
* no .tmp/** content is present;
* no nested .git/** content is present;
* no .tsbuildinfo* content is present;
* no test source or out-test content is present;
* package entry-count and size limits pass.

Do not infer validity merely from the filename, version number, installation
history, or the fact that the archive opens.

==================================================
3. RUN THE EXISTING EXACT-PACKAGE VERIFIER

Inspect package.json and the repository scripts to identify the project’s
canonical exact-package verification command.

Run the existing exact-package verifier against this explicit path:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.141.vsix

Do not allow a newest-VSIX selector or wildcard to choose another artifact.

Report:

* exact command;
* exact artifact supplied to the verifier;
* exit code;
* every passed gate;
* every warning;
* every failed gate.

Required:

EXACT_PACKAGE_VERIFIER_PASS: YES

If the repository has no usable exact-package verifier, do not fabricate a pass.
Return:

EXISTING_0_3_141_VERIFICATION_RESULT: FAIL_VERIFIER_UNAVAILABLE

==================================================
4. RUN CURRENT VALIDATION GATES

Use only existing local dependencies and repository scripts.

Do not run npm install or any dependency-changing command.

Run and report:

1. TypeScript compile;
2. lint;
3. trusted Job Config envelope direct suite;
4. Repair 8 focused suites;
5. Repair 5/6/7 regression suites;
6. full unit suite.

For each gate report:

* exact command;
* exit code;
* passing count;
* pending/skipped count;
* failing count;
* complete failure names;
* whether each failure is historical/known or new;
* whether a new functional regression exists;
* whether a new security regression exists.

Required:

COMPILE_PASS: YES
LINT_PASS: YES
TRUSTED_JOB_CONFIG_ENVELOPE_DIRECT_SUITE_PASS: YES
REPAIR_8_FOCUSED_SUITES_PASS: YES
REPAIR_5_6_7_REGRESSION_SUITES_PASS: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

Do not edit any implementation or test file if a gate fails.

==================================================
5. COMPARE WITH THE TRUSTED 0.3.140 BASELINE

If an exact previously verified 0.3.140 VSIX can be identified deterministically,
compare it with the existing 0.3.141 artifact.

Compare:

* decompressed entry names;
* decompressed entry bytes;
* internal version metadata;
* trusted contract bytes;
* package-hygiene results.

Ignore ZIP container timestamps.

Expected:

* identical entry set;
* all non-version functional content consistent with the intended HF1 V2 source;
* differences limited to expected version metadata and already-authorized HF1 V2
    package content.

Do not select a 0.3.140 baseline only because it is the newest file.

If no exact trusted baseline can be proven, report:

BASELINE_0_3_140_COMPARISON:
NOT_PERFORMED_NO_TRUSTED_BASELINE

This alone does not fail adoption if all direct source/package verification gates
pass.

==================================================
6. DETERMINE WHETHER THE EXISTING ARTIFACT IS ADOPTABLE

Adopt the existing artifact without rebuilding only if:

* repository identity passes;
* source version is 0.3.141;
* internal package and manifest versions are 0.3.141;
* publisher, package name, and extension ID are correct;
* exact-package verifier passes;
* independent package inspection passes;
* trusted packaged contracts exist and are byte-equal to source;
* required compile/lint/focused/regression gates pass;
* there are zero new functional regressions;
* there are zero new security regressions;
* package hygiene passes;
* no task-attributable source changes occurred;
* no files are staged;
* the SHA-256 is computed from the exact existing artifact.

If all conditions pass:

EXISTING_ARTIFACT_ADOPTED_AS_FINAL: YES
REBUILD_REQUIRED: NO
READY_TO_INSTALL_0_3_141: YES
READY_FOR_RUNTIME_QA_PHASE_1: NO

READY_FOR_RUNTIME_QA_PHASE_1 must remain NO because installation and active
Extension Host verification have not been performed by this task.

If any condition fails:

EXISTING_ARTIFACT_ADOPTED_AS_FINAL: NO
REBUILD_REQUIRED: YES
READY_TO_INSTALL_0_3_141: NO
READY_FOR_RUNTIME_QA_PHASE_1: NO

Do not rename, delete, overwrite, or rebuild the artifact after a failure. Preserve
the evidence for the next repair/rebuild prompt.

==================================================
7. POST-VALIDATION SAFETY CHECK

Capture final Git status and compare it with the initial baseline.

Separate:

* pre-existing tracked modifications;
* pre-existing untracked files;
* validation-generated output;
* unexpected changes;
* staged files.

Required:

TASK_ATTRIBUTABLE_SOURCE_CHANGES: NONE
ARTIFACT_OVERWRITTEN: NO
NEW_VSIX_CREATED: NO
STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
PACKAGE_LOCK_CREATED: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
DEVELOPMENT_TEST_WORKSPACE_TOUCHED: NO
RUNTIME_QA_STARTED: NO

==================================================
8. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION: 
EXISTING_VSIX_PATH: 
EXISTING_VSIX_SIZE_BYTES: 
EXISTING_VSIX_MODIFIED_AT: 
EXISTING_VSIX_SHA256: 
INTERNAL_PACKAGE_VERSION: 
INTERNAL_MANIFEST_VERSION: 
PUBLISHER: 
PACKAGE_NAME: 
RESOLVED_EXTENSION_ID: 
ARCHIVE_READABLE: YES/NO
EXACT_PACKAGE_VERIFIER_COMMAND: 
EXACT_PACKAGE_VERIFIER_PASS: YES/NO
INDEPENDENT_PACKAGE_INSPECTION_CLEAN: YES/NO
JOB_CONFIG_CONTRACT_PRESENT: YES/NO
JOB_CONFIG_CONTRACT_SOURCE_PACKAGE_HASH_MATCH: YES/NO
ORACLE_CONTRACT_PRESENT: YES/NO
ORACLE_CONTRACT_SOURCE_PACKAGE_HASH_MATCH: YES/NO
INSTALLED_LAYOUT_CONTRACT_RESOLUTION_PASS: YES/NO
SOURCE_CHECKOUT_RUNTIME_DEPENDENCY_FOUND: YES/NO
CONSUMER_CONTEXT_USED_AS_MACHINE_AUTHORITY: YES/NO
PACKAGE_HYGIENE_PASS: YES/NO
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
BASELINE_0_3_140_COMPARISON: PASS/FAIL/NOT_PERFORMED_NO_TRUSTED_BASELINE
TASK_ATTRIBUTABLE_SOURCE_CHANGES: 
UNEXPECTED_CHANGED_PATHS: 
STAGED_FILES: 
EXISTING_ARTIFACT_ADOPTED_AS_FINAL: YES/NO
REBUILD_REQUIRED: YES/NO
READY_TO_INSTALL_0_3_141: YES/NO
READY_FOR_RUNTIME_QA_PHASE_1: NO
SAFE_TO_COMMIT: NO
SAFE_TO_RELEASE: NO

PASS means the exact pre-existing artifact has been independently proven safe for
installation; it does not mean Runtime QA has passed.

End exactly with one:

EXISTING_0_3_141_VERIFICATION_RESULT: PASS

EXISTING_0_3_141_VERIFICATION_RESULT: FAIL_PACKAGE_VERIFICATION

EXISTING_0_3_141_VERIFICATION_RESULT: FAIL_VALIDATION_GATE

EXISTING_0_3_141_VERIFICATION_RESULT: FAIL_UNAUTHORIZED_CHANGE

EXISTING_0_3_141_VERIFICATION_RESULT: FAIL_VERIFIER_UNAVAILABLE

EXISTING_0_3_141_VERIFICATION_RESULT: BLOCKED_IDENTITY_MISMATCH

EXISTING_0_3_141_VERIFICATION_RESULT: BLOCKED_STAGED_CHANGES

EXISTING_0_3_141_VERIFICATION_RESULT: BLOCKED_ARTIFACT_ABSENT
