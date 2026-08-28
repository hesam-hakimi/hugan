TASK: HF1_V2_SEPARATE_EXACT_PACKAGE_VERIFICATION_0_3_146_READ_ONLY

Perform a separate, exact, read-only verification of the newly built version
0.3.146 VSIX.

Use a fresh Claude harness chat in the source repository and select the
repository lifecycle Agent:

etl-release-verifier

Do not use the consumer-workspace Agent named “ETL Verifier”.

Work only against:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Treat the previous packaging report, its checkpoint, stated hashes, counts, and
PASS result as untrusted claims to re-derive independently.

This task is exact package verification only.

Do not edit any repository file.
Do not rebuild or replace the VSIX.
Do not change the version.
Do not install or uninstall the extension.
Do not reload VS Code for activation.
Do not access the Development Test Workspace.
Do not start Runtime QA.
Do not run Preview or Write.
Do not commit, push, tag, stage, stash, reset, restore, or clean.
Do not create package-lock.json.
Do not download or install dependencies.
Do not repair the governance manifest in this session.

==================================================

1. IDENTITY AND NON-MUTATION GATE
    ==================================================

Verify independently:

REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION:
0.3.146

Required:

* exactly one effective repository target;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrent Agent mutation;
* exactly one newly attributable 0.3.146 VSIX;
* all earlier VSIX artifacts present and unchanged.

Target artifact:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.146.vsix

Capture a complete OS-level hash snapshot before inspection, including ignored
and untracked protected files. Repeat it afterward.

If inline command capture is empty, use file-redirected process execution under
the OS temporary directory. Require real stdout, stderr, executable identity, and
exit codes. Do not modify the repository to repair execution.

==================================================
2. EXACT ARTIFACT IDENTITY

Derive directly from the VSIX bytes:

* absolute path;
* filename;
* byte size;
* SHA-256;
* ZIP entry count;
* duplicate ZIP entry count;
* extension ID;
* publisher;
* extension name;
* archive manifest version;
* embedded package.json version.

Expected identity:

* filename: databricks-etl-copilot-0.3.146.vsix
* extension ID: td-etl.databricks-etl-copilot
* version: 0.3.146
* reported packaging size to verify independently: 1,262,112 bytes
* reported entry count to verify independently: 66

Do not copy the previously reported SHA-256. Compute it independently twice from
the artifact bytes and require equality.

Reject:

* malformed ZIP structure;
* unreadable entries;
* duplicate or traversal entries;
* absolute archive paths;
* paths escaping the extension root;
* inconsistent versions;
* incorrect extension identity;
* secrets, credentials, temporary logs, machine-specific paths, or unexpected
    repository files.

==================================================
3. SOURCE-TO-PACKAGE PROVENANCE

Independently compare every packaged non-build entry with its intended live source.

Report:

* exact matching source entries;
* generated build entries;
* synchronized consumer-Agent resource entries;
* version-only metadata entries;
* missing expected entries;
* unexpected entries;
* byte mismatches;
* entries with no provenance.

Verify specifically that the packaged consumer-facing Agent assets are generated
from the canonical catalog and remain semantically and byte consistent where the
contract requires it.

Verify presence and correctness of:

* ETL Orchestrator;
* ETL Implementer;
* ETL Verifier;
* ETL Runtime Troubleshooter;
* ETL Evidence Researcher;
* ETL Operator;
* their instructions, skills, prompts, and required context resources;
* the Runtime QA support fixture and structured-diagnostic support introduced
    before packaging.

Confirm that user-facing behavior remains:

* only ETL Orchestrator is user-facing;
* the other consumer Agents are internal delegates;
* internal delegates did not become user-invocable;
* tool sets and delegated authority were not broadened.

==================================================
4. DIFFERENTIAL VERIFICATION

Compare 0.3.146 with the immediately preceding 0.3.145 VSIX.

Enumerate every archive difference by exact path and classify it as:

* authorized version metadata;
* deterministic rebuilt bundle;
* synchronized consumer-Agent resource;
* Runtime QA/structured-diagnostic implementation;
* unexpected.

The packaging report claimed:

* six changed archive entries;
* zero unexpected archive differences;
* two version metadata entries;
* two rebuilt bundles;
* two synchronized consumer-Agent resource entries.

Re-derive these counts. Do not accept them from the report.

Confirm that no previously existing VSIX was modified.

==================================================
5. PACKAGE VALIDATION

==================================================

Run only read-only validations that do not rewrite the package or repository:

* archive integrity;
* extension manifest validation;
* package identity validation;
* explicit-path VSIX content verification;
* source-to-package byte comparison;
* consumer-Agent catalog/resource byte-lock verification;
* detection of secrets and machine-local paths;
* forbidden-file and unexpected-entry checks.

Do not run a verifier using mtime or a multi-match glob to select the artifact.
Use the exact absolute 0.3.146 VSIX path.

If any validation utility would mutate the repository or package, reproduce its
read-only checks using a task-owned temporary extraction directory.

==================================================
6. GOVERNANCE-GAP ASSESSMENT

Read, but do not modify:

.github/agent-governance/process-manifest.json

and the relevant schema and boundary validator.

Independently determine whether the following reported gap is real:

* VERSION_AND_PACKAGE authorizes the package.json version change;
* the stage is expected to create a new version-distinguishable VSIX;
* **/*.vsix is protected;
* no protectedPathExceptions entry currently permits creation of a new VSIX
    during VERSION_AND_PACKAGE;
* therefore verify-change-boundary blocks the newly created artifact even though
    no pre-existing VSIX was modified.

Distinguish clearly between:

1. artifact integrity;
2. task authorization from the owner prompt;
3. machine-enforced manifest authorization.

If the gap is confirmed, provide the exact minimal proposed manifest change and
exact required governance tests, but do not apply it.

The proposed rule must permit only creation of the exact new, version-distinguishable
VSIX during VERSION_AND_PACKAGE. It must not permit replacement, deletion, or
modification of any pre-existing VSIX and must not create a blanket **/*.vsix
write exception across other stages.

==================================================
7. FINAL NON-MUTATION PROOF

Compare the final OS-level snapshot with the initial snapshot.

Required:

* repository paths changed by this review: 0;
* target VSIX changed: NO;
* package.json changed: NO;
* package version changed: NO;
* governance files changed: NO;
* package-lock.json created: NO;
* staged files: 0;
* stash entries: 0;
* extension installed or uninstalled: NO;
* Runtime QA started: NO;
* QA workspace touched: NO;
* Preview created: NO;
* Write executed: NO;
* commit/push/tag: NO.

==================================================
8. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
REPOSITORY_MUTATED_BY_VERIFICATION: YES/NO

VSIX_PATH:
VSIX_FILENAME:
VSIX_SIZE:
VSIX_SHA256_FIRST:
VSIX_SHA256_SECOND:
VSIX_HASHES_EQUAL: YES/NO
VSIX_ENTRY_COUNT:
VSIX_DUPLICATE_ENTRY_COUNT:
VSIX_ARCHIVE_INTEGRITY: PASS/FAIL
EXTENSION_ID:
ARCHIVE_MANIFEST_VERSION:
EMBEDDED_PACKAGE_VERSION:
VERSION_IDENTITIES_EQUAL: YES/NO

EXPECTED_ENTRIES_PRESENT: YES/NO
SOURCE_TO_PACKAGE_MISMATCH_COUNT:
UNEXPECTED_ARCHIVE_ENTRY_COUNT:
SECRET_OR_MACHINE_PATH_FINDINGS:
CONSUMER_AGENT_COUNT:
USER_FACING_CONSUMER_AGENTS:
INTERNAL_DELEGATE_AGENTS:
INTERNAL_AGENTS_USER_INVOKABLE: YES/NO
CONSUMER_AGENT_TOOL_SETS_CHANGED_BY_PACKAGING: YES/NO
CONSUMER_AGENT_AUTHORITY_BROADENED: YES/NO

DIFF_VS_0_3_145_COUNT:
VERSION_METADATA_DIFF_COUNT:
REBUILT_BUNDLE_DIFF_COUNT:
SYNCHRONIZED_AGENT_RESOURCE_DIFF_COUNT:
RUNTIME_QA_SUPPORT_DIFF_COUNT:
UNEXPECTED_DIFF_COUNT:
PREEXISTING_VSIX_MODIFIED_COUNT:

GOVERNANCE_VSIX_EXCEPTION_GAP_CONFIRMED: YES/NO
ARTIFACT_INTEGRITY_VALID_DESPITE_GAP: YES/NO
MINIMAL_MANIFEST_REPAIR_PATHS:
MINIMAL_MANIFEST_REPAIR_DESIGN:
REQUIRED_GOVERNANCE_TESTS:

PACKAGE_JSON_CHANGED_BY_REVIEW: NO
PACKAGE_VERSION_CHANGED_BY_REVIEW: NO
VSIX_CHANGED_BY_REVIEW: NO
GOVERNANCE_CHANGED_BY_REVIEW: NO
PACKAGE_LOCK_CREATED: NO
QA_WORKSPACE_TOUCHED: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

READY_FOR_LOCAL_INSTALL_AND_ACTIVATION: YES/NO
REQUIRES_GOVERNANCE_OWNER_ACTION_BEFORE_INSTALL: YES/NO

Only return READY_FOR_LOCAL_INSTALL_AND_ACTIVATION: YES when:

* artifact identity and integrity pass;
* all expected entries and consumer Agent resources are correct;
* zero unexpected entries or content differences exist;
* source-to-package provenance is complete;
* the repository and artifact remain unchanged;
* no unresolved enforcing governance blocker remains.

End exactly with one:

EXACT_PACKAGE_VERIFICATION_0_3_146_RESULT:
PASS_READY_FOR_LOCAL_INSTALL_AND_ACTIVATION

EXACT_PACKAGE_VERIFICATION_0_3_146_RESULT:
PASS_ARTIFACT_VALID_BLOCKED_GOVERNANCE_EXCEPTION

EXACT_PACKAGE_VERIFICATION_0_3_146_RESULT:
FAIL_PACKAGE_INTEGRITY

EXACT_PACKAGE_VERIFICATION_0_3_146_RESULT:
FAIL_UNAUTHORIZED_OR_UNEXPECTED_CONTENT

EXACT_PACKAGE_VERIFICATION_0_3_146_RESULT:
FAIL_VERIFICATION_MUTATED_REPOSITORY

EXACT_PACKAGE_VERIFICATION_0_3_146_RESULT:
BLOCKED_IDENTITY_OR_EXECUTION
