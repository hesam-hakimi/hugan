TASK: HF1_V2_ROOT_CAUSE_FRESH_CONSUMER_WORKSPACE_CLASSIFICATION_BLOCKER_0_3_141

Perform a read-only root-cause investigation inside the Software Development
Environment:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Do not implement a fix during this task.

The purpose is to explain why the active verified 0.3.141 runtime rejects the
intended fresh consumer Development Test Workspace before STTM interpretation.

Do not access or modify the Development Test Workspace.
Do not access or modify etl-framework-adb.
Do not modify source, tests, resources, generated output, or package metadata.
Do not build another VSIX.
Do not install or uninstall extensions.
Do not run npm install.
Do not create package-lock.json.
Do not commit, push, merge, tag, stash, reset, clean, restore, or delete files.
Do not modify protected .github/** assets.
Temporary diagnostic fixtures may be created only outside the repository and
must not contain real data.

==================================================

1. LIVE RUNTIME FAILURE EVIDENCE
    ==================================================

Treat the following as authoritative live evidence from Runtime QA:

ACTIVE_EXTENSION_ID:
td-etl.databricks-etl-copilot

ACTIVE_EXTENSION_VERSION:
0.3.141

RUNTIME_ACTIVATION_PROVEN:
YES

QA workspace:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa

QA workspace facts:

* exactly one workspace root;
* intentionally consumer-shaped Development Test Workspace;
* intentionally not a Git repository;
* workflow setup already present;
* sttm/qa_hf1v2_demo_sttm.md present;
* resources/copilot/context/** present;
* no job_conf/**;
* no env_conf/**;
* no generated ETL artifacts;
* no extension-source checkout;
* no etl-framework-adb;
* synthetic QA data only.

The installed runtime returned this blocker:

Workspace folder “etl-acz9999-hf1v2-qa” could not be confirmed as a consumer ETL
workspace; open an ETL Framework workspace before STTM interpretation or guarded
writes.

Runtime result:

WORKSPACE_CLASSIFICATION:
UNKNOWN

TARGET_DECISION:
CREATE_NEW_JOB (filesystem evidence only; runtime workflow blocked)

The Runtime stopped before:

* STTM interpretation;
* packaged Framework discovery;
* contract resolution;
* example search;
* rendering;
* deterministic validation;
* Preview creation.

No Preview ID was created and zero workspace files changed.

==================================================
2. EXPECTED PRODUCT BEHAVIOR

The intended supported scenario is a fresh consumer workspace.

Required behavior:

* a consumer does not require the extension source repository;
* a consumer does not require etl-framework-adb;
* a fresh consumer may initially have no job_conf/** and no env_conf/**;
* absence of those generated files must lead to CREATE_NEW_JOB;
* absence of generated files must not classify the workspace as UNKNOWN;
* Git repository metadata must not be required for this disposable Runtime QA
    workspace;
* workflow setup and the STTM are already present;
* packaged trusted Framework contracts provide machine authority;
* resources/copilot/context/** remains advisory and must not become machine
    authority;
* an arbitrary empty folder must still fail closed;
* multi-root ambiguity must still fail closed;
* guarded Preview/write validation and explicit approval must not be weakened.

Do not recommend adding placeholder job_conf/env_conf files, initializing Git,
copying Framework source, or opening etl-framework-adb as a workaround.

==================================================
3. VERIFY SOURCE ENVIRONMENT IDENTITY

Before analysis, report:

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

Capture:

* repository root;
* origin;
* branch;
* HEAD;
* source version;
* staged paths;
* tracked-modified paths;
* untracked paths.

A large pre-existing working-tree overlay may exist. Preserve it exactly.

If root, origin, branch, HEAD, or version differs, stop:

ROOT_CAUSE_RESULT: BLOCKED_IDENTITY_MISMATCH

If staged files exist, report them and stop:

ROOT_CAUSE_RESULT: BLOCKED_STAGED_CHANGES

==================================================
4. TRACE THE EXACT CLASSIFICATION BLOCKER

Search the source and compiled runtime for the exact or closest diagnostic text:

could not be confirmed as a consumer ETL workspace

and:

open an ETL Framework workspace before STTM interpretation or guarded writes

Identify and report:

* exact source file and function producing the blocker;
* compiled/runtime file containing it;
* calling tool and call path;
* classification function or resolver used;
* input evidence the classifier reads;
* evidence it ignores;
* exact condition that returns UNKNOWN;
* whether Git metadata is required directly or indirectly;
* whether job_conf/** or env_conf/** presence is required;
* whether Framework markers are incorrectly required;
* whether STTM or initialized workflow markers are considered;
* whether the error message incorrectly directs normal consumers to open a
    Framework workspace.

Trace the path beginning with etl_capabilities through the classifier and into
the gate that prevents:

* etl_interpret_sttm;
* etl_get_framework_rules;
* etl_search_examples;
* guarded Preview creation.

Do not infer from names alone. Cite exact files, functions, predicates, and
returned values.

==================================================
5. DETERMINE THE INTENDED INITIALIZATION SIGNAL

Inspect the existing workflow initialization and customization implementation.

Identify every durable signal created for a correctly initialized consumer
workspace, including, where applicable:

* .github/agents/**;
* .github/skills/**;
* .github/instructions/**;
* .github/prompts/**;
* resources/copilot/context/**;
* managed-asset or initialization manifests;
* workspace configuration or extension-owned markers.

For each signal report:

* whether it exists in the QA topology;
* whether current classification reads it;
* whether it is extension-managed or consumer-editable;
* whether it may safely establish workspace intent;
* whether it may provide machine authority.

Maintain this distinction:

* a safe initialization marker may establish that the folder is an initialized
    consumer workspace;
* consumer-editable context must never define trusted Framework contracts,
    validation rules, module schemas, or write authority.

Determine which existing signal should classify a fresh initialized consumer
without treating advisory content as machine authority.

If no trustworthy existing initialization signal exists, state that clearly.
Do not invent one during this task.

==================================================
6. REPRODUCE THE FAILURE

Use existing tests and test helpers where possible.

Do not edit tests.

Create any additional diagnostic fixture only in a temporary location outside
the repository.

Reproduce at least these matrices:

A. Fresh initialized consumer:

* one root;
* no Git metadata;
* workflow customization present;
* STTM present;
* resources/copilot/context present;
* no job_conf;
* no env_conf;
* no Framework source.

Expected:
consumer-etl-workspace and CREATE_NEW_JOB.

B. Arbitrary empty folder:

* no initialization evidence;
* no STTM;
* no job/env;
* no Framework.

Expected:
UNKNOWN/BLOCKED.

C. Existing consumer:

* canonical existing consumer artifacts present.

Expected:
consumer-etl-workspace.

D. Framework source workspace:

Expected:
Framework/development classification, not consumer.

E. Multi-root workspace:

Expected:
ambiguous/BLOCKED.

For each case report:

* actual classification;
* expected classification;
* decisive evidence;
* exact predicate responsible for a mismatch.

Do not use the real QA workspace for reproduction.

==================================================
7. TEST-COVERAGE GAP ANALYSIS

Locate all existing tests covering:

* workspace classification;
* etl_capabilities;
* fresh consumers;
* no existing job_conf/env_conf;
* non-Git workspaces;
* packaged Framework fallback;
* CREATE_NEW_JOB routing;
* pre-STTM capability gates;
* Preview/write authorization.

Explain why compile, focused suites and the full unit suite passed while this
runtime defect remained.

Report:

* existing relevant test files;
* scenarios currently covered;
* missing scenario;
* tests that give a false sense of coverage;
* whether fixtures accidentally contain job/env/Framework/Git evidence;
* exact regression tests required for a repair.

==================================================
8. SOURCE/VISX/PACKAGING PARITY CHECK

Determine whether this is:

* a source logic defect;
* a compiled-output defect;
* a package-content defect;
* stale installed runtime;
* missing initialization evidence;
* incorrect tool invocation;
* or a combination.

Compare the relevant classifier and blocker logic across:

1. source;
2. current compiled output;
3. exact verified VSIX:
    databricks-etl-copilot-0.3.141.vsix

The exact verified artifact identity is:

SIZE:
1250393 bytes

SHA-256:
437427A915BEB7C0867DD2CE53C968161C99F43730004C702D87799390446B51

Do not rebuild or modify the artifact.

Report whether the source, compiled output and packaged runtime contain equivalent
classification behavior.

==================================================
9. TRUST AND SAFETY ANALYSIS

Explain how the repair can recognize a fresh initialized consumer while
preserving fail-closed behavior.

The future repair must not:

* classify every folder containing an STTM as trusted;
* use consumer context as Framework contract authority;
* bypass packaged-contract resolution;
* bypass artifact path validation;
* bypass Preview freezing;
* bypass explicit approval;
* permit writes outside the workspace root;
* weaken multi-root handling;
* require Framework source.

Identify the minimum safe classification evidence and the separate downstream
guards that continue to protect Preview and write operations.

==================================================
10. PROPOSE THE BOUNDED REPAIR — DO NOT IMPLEMENT

Provide a concrete repair plan containing:

* exact source files requiring modification;
* exact functions/predicates requiring modification;
* exact diagnostic message correction;
* exact new or updated test files;
* required positive cases;
* required negative/security cases;
* compiled/generated artifacts expected from normal build commands;
* whether packaged agent/prompt assets require synchronization;
* whether a package version increment from 0.3.141 to 0.3.142 is required;
* exact validation commands;
* exact packaging verification commands;
* Runtime QA steps that must be repeated afterward.

Do not edit any file during this task.

==================================================
11. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION: 
LIVE_RUNTIME_VERSION: 0.3.141
LIVE_QA_WORKSPACE_EXPECTED_CLASSIFICATION: DEVELOPMENT_TEST_WORKSPACE
LIVE_RUNTIME_CLASSIFICATION: UNKNOWN
BLOCKER_SOURCE_FILE: 
BLOCKER_SOURCE_FUNCTION: 
CLASSIFIER_SOURCE_FILE: 
CLASSIFIER_FUNCTION: 
EXACT_FAILED_PREDICATE: 
GIT_METADATA_REQUIRED_BY_CURRENT_LOGIC: YES/NO
JOB_OR_ENV_REQUIRED_BY_CURRENT_LOGIC: YES/NO
FRAMEWORK_MARKER_REQUIRED_BY_CURRENT_LOGIC: YES/NO
INITIALIZED_CONSUMER_SIGNALS_FOUND: 
CURRENT_CLASSIFIER_READS_INITIALIZATION_SIGNAL: YES/NO
SAFE_MINIMUM_CLASSIFICATION_EVIDENCE: 
FRESH_CONSUMER_REPRODUCED: YES/NO
FRESH_CONSUMER_ACTUAL_RESULT: 
EMPTY_FOLDER_NEGATIVE_CONTROL_PASS: YES/NO
EXISTING_CONSUMER_CONTROL_PASS: YES/NO
FRAMEWORK_WORKSPACE_CONTROL_PASS: YES/NO
MULTI_ROOT_CONTROL_PASS: YES/NO
MISSING_TEST_SCENARIO: 
SOURCE_COMPILED_VSIX_PARITY: PASS/FAIL
ROOT_CAUSE_CATEGORY: 
SECURITY_BOUNDARY_PRESERVED_BY_PROPOSED_REPAIR: YES/NO
PROPOSED_CHANGED_SOURCE_PATHS: 
PROPOSED_CHANGED_TEST_PATHS: 
PROPOSED_VERSION_AFTER_REPAIR: 
TASK_ATTRIBUTABLE_CHANGES: NONE
STAGED_FILES: 
QA_WORKSPACE_TOUCHED: NO
SOURCE_MODIFIED: NO
VSIX_BUILT: NO
READY_FOR_BOUNDED_REPAIR: YES/NO

End exactly with one:

ROOT_CAUSE_RESULT: CONFIRMED_SOURCE_LOGIC_DEFECT

ROOT_CAUSE_RESULT: CONFIRMED_PACKAGING_DEFECT

ROOT_CAUSE_RESULT: CONFIRMED_MISSING_INITIALIZATION_SIGNAL

ROOT_CAUSE_RESULT: CONFIRMED_TOOL_INVOCATION_DEFECT

ROOT_CAUSE_RESULT: CONFIRMED_COMBINED_DEFECT

ROOT_CAUSE_RESULT: INCONCLUSIVE

ROOT_CAUSE_RESULT: BLOCKED_IDENTITY_MISMATCH

ROOT_CAUSE_RESULT: BLOCKED_STAGED_CHANGES
