TASK: HF1_V2_VERSION_AND_PACKAGE_0_3_146

Perform only the VERSION_AND_PACKAGE stage for ETL Extension version 0.3.146.

Work in:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use:

* a fresh Claude harness Chat;
* Agent etl-release-verifier;
* Claude Opus 5 with Max reasoning.

The independent review ended with:

RUNTIME_QA_SUPPORT_INDEPENDENT_REVIEW_RESULT:
PASS_READY_FOR_VERSION_0_3_146_AND_PACKAGE

This authorizes version bump and package creation only.

Do not perform independent package certification in this same session.
Do not install or activate the extension.
Do not start Runtime QA.

==================================================

1. IDENTITY GATE
    ==================================================

Required:

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION_BEFORE:
0.3.145

Verify:

* one effective repository target;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrent Agent mutation;
* current independent-reviewed source changes are present;
* existing VSIX files are captured by path, size, and SHA-256.

Stop on identity mismatch or concurrent mutation.

==================================================
2. BASELINE

Before editing, capture:

* complete filesystem path/size/SHA-256 snapshot;
* Git status;
* package.json hash and exact current fields;
* every existing root VSIX hash;
* current source and packaged consumer Agent hashes.

Use both governance baseline tooling and independent OS hashing.

Do not rely solely on git ls-files.

==================================================
3. AUTHORIZED CHANGES

Authorize exactly:

1. Change only:

package.json -> version

from:

0.3.145

to:

0.3.146

2. Create exactly one new artifact:

databricks-etl-copilot-0.3.146.vsix

Use the repository’s canonical package filename if it deterministically differs;
report the exact filename.

Do not change any other package.json field.

Required:

DEPENDENCIES_CHANGED: NO
DEVDEPENDENCIES_CHANGED: NO
PACKAGE_LOCK_CREATED: NO

Do not modify or replace any existing VSIX.

==================================================
4. PACKAGING TOOL

Use the exact pinned packaging tool declared by the repository.

Prefer an existing local or cached installation.

If unavailable, a one-time acquisition of the exact pinned
@vscode/vsce version is authorized only inside a task-owned OS temporary
directory.

Do not:

* install it into live repository node_modules;
* modify package.json to acquire it;
* create package-lock.json;
* use an unpinned version;
* persist downloaded tooling in the repository.

Record the exact tool version and execution path.

==================================================
5. PRE-PACKAGE VALIDATION

Run in a task-owned mirror where generated output could affect the live baseline:

* compile;
* compile:test;
* lint;
* Repair 11;
* Repair 12;
* Repair 13;
* Runtime QA support fixture suite;
* Phase H eval gate;
* governance tests;
* customization validation;
* test-registration validation;
* package asset byte-lock;
* canonical full unit suite.

Expected full-unit state:

* passing: 2298;
* pending: 1;
* failing: 2;
* failures: exact unchanged F1 and F3 only;
* new functional regressions: 0;
* new security regressions: 0.

If identities differ, do not package.

==================================================
6. BUILD THE VSIX

Build exactly one 0.3.146 VSIX from the independently reviewed current working
content.

Verify mechanically:

* extension ID;
* archive manifest version: 0.3.146;
* package.json version inside archive: 0.3.146;
* archive opens successfully;
* every archive entry is readable;
* no absolute machine path;
* no temporary files;
* no secrets or credentials;
* no source-governance .claude/** content unless explicitly required by the
    established package contract;
* packaged consumer Agent resources match the canonical catalog;
* structured diagnostic implementation and required Runtime QA fixture/support
    assets are included according to the existing packaging contract.

Compare the new VSIX with version 0.3.145 and enumerate every content difference.

Every difference must be attributable to:

* version metadata;
* independently reviewed Repair 13 changes;
* Runtime QA support changes;
* structured diagnostic changes;
* synchronized consumer Agent guidance;
* canonical Phase H/report content only if those files are part of the established
    package contract.

Unexpected archive differences are a failure.

==================================================
7. PROHIBITIONS

Do not:

* install or uninstall any extension;
* reload VS Code for activation;
* access the Development Test Workspace;
* run @etl /workflow;
* start Runtime QA;
* create Preview;
* approve or execute Write;
* commit, push, tag, stage, stash, reset, restore, or clean;
* modify governance files;
* perform independent certification of the package in this session.

==================================================
8. FINAL BOUNDARY PROOF

Required task-attributable changes:

* package.json version only;
* one new 0.3.146 VSIX only.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
PACKAGE_VERSION_AFTER: 0.3.146
PACKAGE_LOCK_CREATED: NO
DEPENDENCIES_CHANGED: NO
EXISTING_VSIX_CHANGED: NO
REPAIR_SOURCE_CHANGED_DURING_PACKAGE_STAGE: NO
QA_WORKSPACE_TOUCHED: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

==================================================
9. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
CONCURRENT_AGENT_MUTATION: YES/NO

SOURCE_VERSION_BEFORE: 0.3.145
SOURCE_VERSION_AFTER: 
PACKAGE_JSON_CHANGED_FIELDS: 
DEPENDENCIES_CHANGED: YES/NO
DEVDEPENDENCIES_CHANGED: YES/NO
PACKAGE_LOCK_CREATED: YES/NO

PRE_PACKAGE_VALIDATION_PASS: YES/NO
FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_FAILURES: 
F1_UNCHANGED: YES/NO
F3_UNCHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

VSIX_BUILT: YES/NO
VSIX_PATH: 
VSIX_FILENAME: 
VSIX_SIZE_BYTES: 
VSIX_SHA256: 
VSIX_FILE_COUNT: 
VSIX_EXTENSION_ID: 
VSIX_VERSION: 
VSIX_ARCHIVE_INTEGRITY: PASS/FAIL
VSIX_UNEXPECTED_CONTENT_DIFFERENCES: 

AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
EXISTING_VSIX_CHANGED: YES/NO
REPAIR_SOURCE_CHANGED_DURING_PACKAGE_STAGE: YES/NO

EXTENSION_INSTALLED_OR_UNINSTALLED: NO
QA_WORKSPACE_TOUCHED: NO
RUNTIME_QA_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

READY_FOR_SEPARATE_EXACT_PACKAGE_VERIFICATION: YES/NO
READY_TO_INSTALL: NO
READY_FOR_RUNTIME_QA: NO

Do not independently certify the package in this session.

End exactly with one:

VERSION_AND_PACKAGE_0_3_146_RESULT:
PASS_READY_FOR_SEPARATE_EXACT_PACKAGE_VERIFICATION

VERSION_AND_PACKAGE_0_3_146_RESULT:
FAIL_VALIDATION

VERSION_AND_PACKAGE_0_3_146_RESULT:
FAIL_PACKAGE_INTEGRITY

VERSION_AND_PACKAGE_0_3_146_RESULT:
FAIL_UNAUTHORIZED_CHANGE

VERSION_AND_PACKAGE_0_3_146_RESULT:
BLOCKED_IDENTITY_OR_CONCURRENT_MUTATION

VERSION_AND_PACKAGE_0_3_146_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT
