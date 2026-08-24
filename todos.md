TASK: HF1_V2_REPAIR_9_FRESH_CONSUMER_CLASSIFICATION_AND_BUILD_0_3_142

Implement the bounded Repair 9 confirmed by the completed read-only root-cause
investigation.

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

This task fixes the 0.3.141 runtime preflight classifier, adds regression and
security tests, increments the version to 0.3.142, builds the exact VSIX and
verifies it.

Do not access or modify the Development Test Workspace.
Do not access or modify etl-framework-adb.
Do not install or uninstall the extension.
Do not run Runtime QA.
Do not use web search.
Do not download dependencies.
Do not run npm install.
Do not use npm version.
Do not create package-lock.json.
Do not modify protected .github/** assets.
Do not modify resources/copilot/** unless concrete test evidence proves that an
existing packaged asset is incorrect. The root-cause investigation found no
packaged agent/prompt change necessary.
Do not modify historical test baselines to hide failures.
Do not commit, push, merge, tag, stash, reset, clean, restore, or delete existing
files.
Do not overwrite or delete the verified 0.3.141 VSIX.

==================================================

1. AUTHORITATIVE ROOT-CAUSE EVIDENCE
    ==================================================

Treat the completed investigation as authoritative:

ROOT_CAUSE_RESULT:
CONFIRMED_SOURCE_LOGIC_DEFECT

Source version and active failed runtime:

0.3.141

Live failure:

* correctly initialized fresh consumer workspace;
* one non-Git root;
* STTM present;
* initialized managed workflow assets present;
* no job_conf/**;
* no env_conf/**;
* no Framework source;
* no etl-framework-adb;
* etl_capabilities returned targetType=unknown and blocked before STTM discovery.

Exact blocker:

src/tools/EtlReadOnlyToolService.ts
EtlReadOnlyToolService.capabilities()
approximately line 907

Classifier:

src/tools/EtlReadOnlyToolService.ts
classifyWorkspaceTargetType()
via detectEtlAssetRepo()
approximately lines 1007–1025 and 1468–1487

Exact failed logic:

detectEtlAssetRepo(folder, reader).length > 0 === false

Current detection accepts only generated/legacy evidence such as:

* job_conf/**;
* env_conf/**;
* sql/**;
* common_script/**;
* external_modules/**;
* job_onboarding/**;
* legacy ETL-flavoured AGENTS.md.

It ignores the extension-managed initialization signals already used by
RepoWriter and WorkflowTargetResolver.

Safe initialized-consumer evidence:

* .github/copilot-instructions.md containing exact managed provenance:
    etl-copilot:managed; or
* at least one extension-managed asset under:
    .github/agents/**,
    .github/skills/**,
    .github/instructions/**,
    .github/prompts/**
    whose content carries the same managed provenance.

Evidence that must remain insufficient by itself:

* bare sttm/**;
* resources/copilot/context/**;
* folder naming;
* Git metadata;
* arbitrary .github files without the managed provenance stamp.

Existing generated job_conf/env_conf evidence must continue to work.

The new classification evidence establishes workspace intent only. It must never
become Framework contract, schema, validation, module, path or write authority.

==================================================
2. VERIFY REPOSITORY AND PRESERVE BASELINE

Expected identity:

REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION_BEFORE:
0.3.141

Capture before editing:

* absolute repository root;
* origin;
* branch;
* HEAD;
* source version;
* staged paths;
* tracked modifications;
* untracked paths;
* existing 0.3.141 and 0.3.142 VSIX files;
* package-lock.json presence.

Preserve the complete pre-existing working-tree overlay exactly.

If root, origin, branch or HEAD differs, stop:

REPAIR_9_RESULT: BLOCKED_IDENTITY_MISMATCH

If staged files exist, stop:

REPAIR_9_RESULT: BLOCKED_STAGED_CHANGES

If databricks-etl-copilot-0.3.142.vsix already exists, do not overwrite it.
Inspect and report it, then stop:

REPAIR_9_RESULT: BLOCKED_EXISTING_0_3_142_ARTIFACT

==================================================
3. AUTHORIZED CHANGE BOUNDARY

Primary authorized source files:

* src/tools/EtlReadOnlyToolService.ts
* src/customization/WorkflowTargetResolver.ts

Authorized test files:

* src/test/suite/EtlReadOnlyToolService.test.ts
* src/test/suite/hf1OracleFreshConsumer.test.ts
* src/test/suite/workspaceClassificationParity.test.ts
    (new, if the existing test structure supports it)

Conditionally authorized:

* the canonical existing test registration/pattern file, only if required to
    guarantee the new suite runs;
* package.json, version token only:
    3.141 → 0.3.142;
* normal compiled/package output produced by existing scripts.

Do not remove or exclude any existing test pattern.

Prefer exporting/reusing the established managed-marker predicate from
WorkflowTargetResolver rather than creating duplicate detection logic.

If a new shared source file is technically necessary, stop before creating it
and report why the two planned source files cannot safely host the shared
predicate:

REPAIR_9_RESULT: BLOCKED_SCOPE_EXPANSION_REQUIRED

Any other intentional source/resource/configuration change is unauthorized.

==================================================
4. IMPLEMENT SHARED INITIALIZATION-EVIDENCE DETECTION

Create or expose one shared predicate that recognizes extension-managed consumer
workflow initialization.

It must:

1. Recognize .github/copilot-instructions.md only when its content contains the
    exact etl-copilot:managed provenance.
2. Recognize managed assets below:
    * .github/agents/**;
    * .github/skills/**;
    * .github/instructions/**;
    * .github/prompts/**;
        only when the inspected asset contains the same managed provenance.
3. Continue recognizing existing canonical consumer job/env layouts.
4. Not require Git metadata.
5. Not accept folder names as evidence.
6. Not accept sttm/** alone.
7. Not accept resources/copilot/context/** alone.
8. Not interpret the content of consumer context as machine authority.
9. Use bounded reads and normalized workspace-relative paths.
10. Fail closed on read errors, traversal, sibling escapes and ambiguous roots.

Reuse this same predicate in the preflight classifier and the existing workflow
target resolver so their consumer classification cannot drift.

Avoid duplicating marker lists or marker parsing.

==================================================
5. FIX PREFLIGHT CLASSIFICATION

Update EtlReadOnlyToolService workspace classification so that:

Fresh initialized consumer:

* no Git;
* no job_conf;
* no env_conf;
* managed workflow initialization evidence present;
* optional STTM present;
* no Framework source;

returns:

consumer-etl-workspace

For this case, etl_capabilities must report:

* selected root is the fresh consumer root;
* runtimeReady=true;
* available=true;
* targetType=consumer-etl-workspace;
* blockers=[].

The absence of job_conf/env_conf must remain a later target-decision concern and
lead to CREATE_NEW_JOB. It must not block capabilities or STTM interpretation.

Keep evidence categories distinct.

Initialization evidence may classify workspace intent, but must not be passed to
buildExampleSearchRoots or treated as an approved Framework example root.

Approved example search must remain restricted to trusted packaged or canonical
artifact-layout evidence.

==================================================
6. FAIL CLOSED FOR FRAMEWORK/SOURCE ROOTS

The investigation found that a Framework root containing sql/** or
common_script/** can currently be mistaken for a consumer.

Close this false positive within the same classification boundary.

Reuse existing source-root/reference-root evidence already used by RepoWriter,
including established sourceRootNames or equivalent trusted predicates.

Required behavior:

* extension source checkout is never classified as consumer-etl-workspace;
* Framework/reference source root is never classified as a writable consumer;
* ordinary existing consumer remains consumer-etl-workspace;
* arbitrary empty folder remains unknown/blocked;
* multi-root ambiguity remains fail-closed.

Prefer the existing non-consumer/unknown result if it safely distinguishes the
root. Do not expand the public target-type model unless absolutely required.

Do not widen any write authorization.

==================================================
7. CORRECT THE MISLEADING DIAGNOSTIC

Replace the current instruction that tells a normal consumer to open an ETL
Framework workspace.

The diagnostic must accurately state that the folder lacks both:

* existing canonical consumer artifacts; and
* initialized managed ETL Copilot workflow evidence.

It should direct the user to initialize the ETL Copilot workflow in the intended
consumer folder.

It must not direct the user to obtain or open Framework source.

Preserve the stable diagnostic prefix or identifier if tests or callers depend
on it; update only the misleading directive portion where possible.

==================================================
8. REQUIRED REGRESSION AND SECURITY TESTS

Add deterministic tests for all of the following.

Positive cases:

1. Fresh initialized consumer:
    * no Git;
    * no job_conf/env_conf;
    * managed copilot-instructions marker;
    * managed workflow assets;
    * STTM;
    * result consumer-etl-workspace;
    * etl_capabilities runtimeReady/available true;
    * blockers empty.
2. Managed marker without generated artifacts:
    * sufficient for initialized consumer classification.
3. Existing canonical consumer:
    * remains consumer-etl-workspace.
4. HF1 Oracle fresh-consumer suite:
    * capabilities classification passes before the write path;
    * CREATE_NEW_JOB remains the expected decision;
    * no Framework source required.

Negative/security cases:

5. Arbitrary empty folder:
    * unknown/blocked.
6. Bare STTM only:
    * not consumer.
7. resources/copilot/context/** only:
    * not consumer.
8. Arbitrary .github assets without etl-copilot:managed:
    * not consumer.
9. Extension source checkout:
    * not consumer and not writable.
10. Framework/reference root:
    * not consumer and not writable.
11. Multiple roots:
    * fail closed.
12. Marker read failure or malformed marker:
    * fail closed.
13. Traversal and sibling escape:
    * rejected.
14. Preview drift and approval token rules:
    * unchanged and still enforced.
15. Example search-root isolation:
    * initialization evidence does not add consumer directories to trusted
        example search roots.

Cross-classifier parity:

Add a matrix asserting agreement among:

* RepoWriter;
* WorkflowTargetResolver;
* EtlReadOnlyToolService/etl_capabilities;

for fresh consumer, existing consumer, empty folder, Framework/source root and
multi-root cases.

Every new test must be included in an actually executed test command.

Do not alter expectations merely to make the implementation pass.

==================================================
9. VALIDATE BEFORE VERSION BUMP

Run using existing local dependencies:

1. TypeScript compile;
2. lint;
3. focused EtlReadOnlyToolService tests;
4. HF1 Oracle fresh-consumer tests;
5. workspace-classification parity tests;
6. trusted Job Config envelope direct suite;
7. Repair 8 focused suites;
8. Repair 5/6/7 regression suites;
9. full unit suite;
10. canonical repository test command.

Report for every command:

* exact command;
* exit code;
* passing count;
* pending/skipped count;
* failing count;
* complete failure names.

The prior verified 0.3.141 baseline was:

* full unit passing: 2120;
* pending: 1;
* failures: 5;
* all five failures historical;
* new functional regressions: 0;
* new security regressions: 0.

The passing count should increase for the new tests.

The same five historical failures may remain only if their identities and causes
are unchanged and they reproduce against pristine HEAD.

Required:

COMPILE_PASS: YES
LINT_PASS: YES
NEW_REPAIR_9_TESTS_PASS: YES
HF1_FRESH_CONSUMER_SUITE_PASS: YES
CLASSIFICATION_PARITY_SUITE_PASS: YES
TRUSTED_JOB_CONFIG_ENVELOPE_DIRECT_SUITE_PASS: YES
REPAIR_8_FOCUSED_SUITES_PASS: YES
REPAIR_5_6_7_REGRESSION_SUITES_PASS: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

If a required gate fails, do not bump the version or package:

REPAIR_9_RESULT: FAIL_VALIDATION_GATE

==================================================
10. VERSION BUMP

Only after all required repair gates pass, change exactly the package.json
version token:

“version”: “0.3.141”

to:

“version”: “0.3.142”

Do not use npm version.
Do not modify dependencies, scripts, publisher, package name or extension ID.
Do not create or modify package-lock.json.

Expected identity:

PUBLISHER:
td-etl

PACKAGE_NAME:
databricks-etl-copilot

EXTENSION_ID:
td-etl.databricks-etl-copilot

TARGET_VERSION:
0.3.142

Re-run compile and the focused Repair 9 tests after the version change.

==================================================
11. BUILD EXACT 0.3.142 VSIX

Use the existing canonical local packaging workflow.

Create exactly:

databricks-etl-copilot-0.3.142.vsix

Expected path:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.142.vsix

Do not publish, install, commit or tag it.
Do not overwrite the 0.3.141 artifact.

==================================================
12. VERIFY THE EXACT PACKAGE

Run the repository’s exact-package verifier against the explicit 0.3.142 path.

Do not use a newest-file selector.

Independently verify:

* archive opens;
* internal package.json version is 0.3.142;
* extension.vsixmanifest version is 0.3.142;
* publisher is td-etl;
* extension ID is td-etl.databricks-etl-copilot;
* trusted Job Config contract is present and byte-equal to source;
* trusted Oracle contract is present and byte-equal to source;
* installed-layout contract resolution passes;
* no etl-framework-adb dependency exists;
* no source-checkout runtime dependency exists;
* package hygiene and entry limits pass;
* no .tmp/**;
* no nested .git/**;
* no .tsbuildinfo*;
* no source tests or out-test content;
* repaired classifier logic is present in packaged compiled output;
* managed-marker detection is present in packaged compiled output;
* corrected consumer diagnostic is present;
* initialization evidence is not added to trusted example-search roots.

Compare decompressed 0.3.141 and 0.3.142 package entries.

Report all changed entries and classify each difference as:

* expected version metadata;
* expected compiled Repair 9 implementation;
* unexpected.

Ignore ZIP timestamps.

Any unexplained entry or byte difference fails package verification.

==================================================
13. COMPUTE FINAL ARTIFACT IDENTITY

Calculate from the actual newly built file:

FINAL_VSIX_PATH: 
FINAL_VSIX_SIZE_BYTES: 
FINAL_VSIX_SHA256: 

Do not predict or reuse a hash.

==================================================
14. POST-BUILD CHANGE-BOUNDARY CHECK

Compare final state with the captured initial baseline.

Report separately:

* pre-existing tracked modifications;
* pre-existing untracked files;
* intentional Repair 9 source changes;
* intentional Repair 9 test changes;
* package.json version edit;
* generated compile/package output;
* unexpected changes;
* staged files.

Required:

UNAUTHORIZED_SOURCE_CHANGES: NONE
UNEXPECTED_CHANGED_PATHS: NONE
STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
PACKAGE_LOCK_CREATED_OR_MODIFIED: NO
DEVELOPMENT_TEST_WORKSPACE_TOUCHED: NO
EXTENSION_INSTALLED: NO
RUNTIME_QA_STARTED: NO

Do not clean the repository after reporting.

==================================================
15. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION_BEFORE: 
SOURCE_VERSION_AFTER: 
ROOT_CAUSE_REPAIRED: YES/NO
MANAGED_INITIALIZATION_EVIDENCE_SUPPORTED: YES/NO
CONSUMER_CONTEXT_USED_AS_MACHINE_AUTHORITY: NO
FRESH_NON_GIT_CONSUMER_CLASSIFICATION: 
FRESH_CONSUMER_CAPABILITIES_RUNTIME_READY: YES/NO
FRESH_CONSUMER_CAPABILITIES_BLOCKER_COUNT: 
EMPTY_FOLDER_CLASSIFICATION: 
BARE_STTM_CLASSIFICATION: 
CONTEXT_ONLY_CLASSIFICATION: 
EXTENSION_SOURCE_CLASSIFICATION: 
FRAMEWORK_ROOT_CLASSIFICATION: 
MULTI_ROOT_FAIL_CLOSED: YES/NO
EXAMPLE_SEARCH_ROOTS_WIDENED: NO
CROSS_CLASSIFIER_PARITY_PASS: YES/NO
AUTHORIZED_SOURCE_CHANGED_PATHS: 
AUTHORIZED_TEST_CHANGED_PATHS: 
UNAUTHORIZED_SOURCE_CHANGED_PATHS: 
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
NEW_REPAIR_9_TESTS_PASS: YES/NO
HF1_FRESH_CONSUMER_SUITE_PASS: YES/NO
CLASSIFICATION_PARITY_SUITE_PASS: YES/NO
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
JOB_CONFIG_CONTRACT_HASH_MATCH: YES/NO
ORACLE_CONTRACT_HASH_MATCH: YES/NO
PACKAGE_CHANGED_ENTRIES_VS_0_3_141: 
UNEXPLAINED_PACKAGE_DIFFERENCES: 
FINAL_VSIX_PATH: 
FINAL_VSIX_SIZE_BYTES: 
FINAL_VSIX_SHA256: 
STAGED_FILES: 
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
PACKAGE_LOCK_CREATED_OR_MODIFIED: NO
DEVELOPMENT_TEST_WORKSPACE_TOUCHED: NO
READY_TO_INSTALL_0_3_142: YES/NO
READY_FOR_RUNTIME_QA_PHASE_1: NO
SAFE_TO_COMMIT: NO
SAFE_TO_RELEASE: NO

PASS requires:

* confirmed source-logic defect repaired;
* fresh initialized non-Git consumer classified correctly;
* arbitrary/unsafe roots remain fail-closed;
* Framework/source roots are not consumers;
* classifiers agree;
* no machine-authority boundary weakened;
* all required focused/regression gates pass;
* only unchanged historical full-suite failures remain;
* zero new functional/security regressions;
* version is 0.3.142;
* exact final package verification passes;
* actual artifact SHA-256 calculated;
* zero staged files;
* no install, Runtime QA, commit, push or tag.

End exactly with one:

REPAIR_9_RESULT: PASS

REPAIR_9_RESULT: FAIL_VALIDATION_GATE

REPAIR_9_RESULT: FAIL_PACKAGE_VERIFICATION

REPAIR_9_RESULT: FAIL_UNAUTHORIZED_CHANGE

REPAIR_9_RESULT: BLOCKED_IDENTITY_MISMATCH

REPAIR_9_RESULT: BLOCKED_STAGED_CHANGES

REPAIR_9_RESULT: BLOCKED_EXISTING_0_3_142_ARTIFACT

REPAIR_9_RESULT: BLOCKED_SCOPE_EXPANSION_REQUIRED
