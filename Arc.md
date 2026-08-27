TASK: HF1_V2_VERSION_AND_PACKAGE_0_3_145_EXACT_VERIFICATION

Work only in:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use the repository-defined etl-release-verifier Agent.

The independent Owner Action review completed with:

OWNER_ACTION_INDEPENDENT_REVIEW_RESULT:
PASS_READY_FOR_VERSION_AND_PACKAGE

This task is authorized to:

1. change the extension version from 0.3.144 to 0.3.145;
2. build exactly one new 0.3.145 VSIX;
3. perform exact static package verification.

This task is NOT authorized to:

- install or uninstall the extension;
- start VS Code Extension Host or Runtime QA;
- access or modify the Development Test Workspace;
- execute Preview, approval, or Write;
- commit, push, merge, tag, stage, stash, reset, restore, or clean;
- download or install dependencies;
- run npm install, npm ci, or any command that creates package-lock.json;
- modify Repair 13, Repair 12, QA STTM, test registration, golden baselines,
  governance assets, Claude Agents or Skills;
- overwrite, rename, or delete any existing VSIX.

==================================================
1. IDENTITY AND EXECUTION PREFLIGHT
==================================================

Verify:

REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION_AT_ENTRY:
0.3.144

Required:

- exactly one effective repository target;
- staged files: 0;
- stash entries: 0;
- package-lock.json absent;
- no concurrent Agent mutation;
- all existing VSIX files captured by path, size and SHA-256.

Prove real stdout, stderr and exit codes for Git, Node, npm and packaging tools.
If inline capture is defective, use file-redirection through a task-owned helper
under the OS temporary directory.

Do not modify the repository to repair process execution.

Stop without changes on identity mismatch, concurrent mutation, staged content or
unproven execution.

==================================================
2. PRE-PACKAGE BASELINE
==================================================

Before editing, capture an independent OS-hash snapshot of the live repository.

Explicitly fingerprint:

- package.json;
- package-lock.json presence;
- all four Repair 13 implementation paths;
- the three reviewed Owner Action paths;
- Repair 11 and Repair 12 paths;
- QA STTM fixture;
- src/test/testPatterns.ts;
- tsconfig files;
- .claude/**;
- governance assets;
- all existing VSIX artifacts.

The reviewed Repair 13 paths are:

- src/core/sttm/SttmResolvedEvidence.ts
- src/core/sttm/SttmUnderstandingReportRenderer.ts
- src/tools/EtlReadOnlyToolService.ts
- src/test/suite/sttmRepair13.test.ts

The reviewed Owner Action paths are:

- docs/eval/phase_h_latest_report.json
- docs/eval/phase_h_latest_report.md
- src/test/testPatterns.ts

These seven paths must remain byte-identical throughout this task.

==================================================
3. EXACT VERSION CHANGE
==================================================

Inspect the repository’s canonical version source and packaging procedure.

Required intended change:

package.json:
version: 0.3.144 -> 0.3.145

Permit only the exact JSON version field required by the canonical extension
manifest.

Do not change:

- extension ID;
- publisher;
- display name;
- engines;
- activation events;
- commands;
- dependencies;
- devDependencies;
- scripts;
- package inclusion/exclusion rules;
- any unrelated package.json field.

Do not use npm version if it creates a lockfile, Git commit, or tag.

After editing, prove:

PACKAGE_JSON_CHANGED_FIELDS:
["version"]

PACKAGE_VERSION:
0.3.145

DEPENDENCIES_CHANGED:
NO

PACKAGE_LOCK_CREATED:
NO

If another source-controlled version declaration must change for package
correctness, stop and report BLOCKED_VERSION_CONTRACT rather than silently
expanding the boundary.

==================================================
4. BUILD IN AN ISOLATED MIRROR
==================================================

Create a byte-faithful task-owned temporary mirror outside the repository after
the exact version change.

Reuse existing dependencies read-only. Do not download anything.

Perform compilation and packaging in the temporary mirror so live out/** and
other generated directories are not modified.

Before packaging, run:

- compile;
- compile:test;
- lint;
- Repair 11 focused suite;
- Repair 12 focused suite;
- Repair 13 focused suite;
- Phase H EvalGating suite;
- governance validators;
- canonical full unit suite.

Expected:

- compile: exit 0;
- compile:test: exit 0;
- lint: exit 0;
- Repair 13: 23 passing, 0 failing;
- Phase H: passing;
- full unit:
  2269 passing, 1 pending, 2 failing.

The two failures must be the exact unchanged F1 and F3 fingerprints:

1. missing deploy-v3-agent-tool-context-gap.prompt.md contract;
2. eleven preserved src/**/AGENT.md files.

Any additional failure, changed failure identity, or new functional/security
regression blocks packaging.

==================================================
5. BUILD EXACTLY ONE 0.3.145 VSIX
==================================================

Use the repository’s canonical offline packaging command.

Build exactly one new VSIX for version 0.3.145.

Do not overwrite or delete any existing VSIX.

Copy only the final verified 0.3.145 VSIX from the temporary mirror to the
canonical live repository artifact location.

Do not copy mirror out/**, reports, logs, caches, temporary helpers or other
generated files into the repository.

==================================================
6. EXACT PACKAGE VERIFICATION
==================================================

Inspect the new VSIX as an archive without installing it.

Verify:

- archive integrity;
- canonical extension ID;
- publisher;
- version exactly 0.3.145;
- expected extension entry point exists;
- compiled Repair 13 product changes are present;
- stale 0.3.144 compiled product code is not substituted;
- test suites and test-only output are not packaged;
- package-lock.json is absent;
- no secrets, credentials, temporary files, snapshots or machine-specific paths;
- no Development Test Workspace content;
- no unintended .git content;
- no duplicate VSIX nested inside the package;
- no unexpected `.claude/**` or governance-development assets are introduced into
  the product package;
- package file list is consistent with the previous 0.3.144 VSIX except for
  expected version metadata and compiled hotfix deltas.

Report:

- exact VSIX path;
- filename;
- byte size;
- SHA-256;
- archive file count;
- manifest extension ID;
- manifest version;
- expected differences from 0.3.144;
- unexpected differences, if any.

Any unexpected content difference blocks progression.

==================================================
7. FINAL CHANGE-BOUNDARY PROOF
==================================================

Compare the final live repository with the pre-task OS snapshot.

The only authorized live changes are:

1. package.json — version field only;
2. one newly created 0.3.145 VSIX artifact.

Required:

- Repair 13 paths unchanged;
- Owner Action paths unchanged;
- Repair 11 and Repair 12 unchanged;
- QA STTM unchanged;
- src/test/testPatterns.ts unchanged;
- governance assets unchanged;
- `.claude/**` unchanged;
- all pre-existing VSIX files unchanged;
- package-lock.json absent;
- staged files: 0;
- stash entries: 0;
- no install;
- no Runtime QA;
- no Preview or Write;
- no commit, push or tag.

==================================================
8. FINAL REPORT
==================================================

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
CONCURRENT_AGENT_MUTATION: YES/NO

SOURCE_VERSION_BEFORE: 0.3.144
SOURCE_VERSION_AFTER: <value>
PACKAGE_JSON_CHANGED_FIELDS: <complete list>
DEPENDENCIES_CHANGED: YES/NO
PACKAGE_LOCK_CREATED: YES/NO

COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_11_PASS: YES/NO
REPAIR_12_PASS: YES/NO
REPAIR_13_PASS: YES/NO
PHASE_H_EVAL_PASS: YES/NO
GOVERNANCE_PASS: YES/NO

FULL_UNIT_PASSING: <number>
FULL_UNIT_PENDING: <number>
FULL_UNIT_FAILING: <number>
FULL_UNIT_FAILURES: <exact identities>
NEW_FUNCTIONAL_REGRESSIONS: <number>
NEW_SECURITY_REGRESSIONS: <number>

VSIX_BUILT: YES/NO
VSIX_PATH: <absolute path>
VSIX_FILENAME: <value>
VSIX_SIZE_BYTES: <number>
VSIX_SHA256: <value>
VSIX_ARCHIVE_FILE_COUNT: <number>
VSIX_EXTENSION_ID: <value>
VSIX_VERSION: <value>
VSIX_ARCHIVE_INTEGRITY: PASS/FAIL
VSIX_UNEXPECTED_CONTENT_DIFFERENCES: <complete list or NONE>

AUTHORIZED_CHANGED_PATHS: <complete list>
UNAUTHORIZED_CHANGED_PATHS: <complete list or NONE>
PREEXISTING_VSIX_FILES_CHANGED: YES/NO
REPAIR_13_CONTENT_CHANGED: YES/NO
OWNER_ACTION_CONTENT_CHANGED: YES/NO
QA_WORKSPACE_TOUCHED: YES/NO

EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
STAGED_FILES: <number>
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO

READY_FOR_LOCAL_INSTALL_AND_RUNTIME_QA: YES/NO
READY_FOR_COMMIT_OR_PUSH: NO
READY_FOR_CLOUD_ROLLOUT: NO

End exactly with one:

VERSION_AND_PACKAGE_RESULT:
PASS_READY_FOR_LOCAL_INSTALL_AND_RUNTIME_QA

VERSION_AND_PACKAGE_RESULT:
FAIL_VALIDATION

VERSION_AND_PACKAGE_RESULT:
FAIL_PACKAGE_VERIFICATION

VERSION_AND_PACKAGE_RESULT:
FAIL_UNAUTHORIZED_CHANGE

VERSION_AND_PACKAGE_RESULT:
BLOCKED_IDENTITY_OR_CONCURRENT_MUTATION

VERSION_AND_PACKAGE_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT

VERSION_AND_PACKAGE_RESULT:
BLOCKED_VERSION_CONTRACT
