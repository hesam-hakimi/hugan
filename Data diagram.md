TASK: HF1_V2_INDEPENDENT_REVIEW_AND_FINALIZE_REPAIR_11_0_3_144

Work in a NEW chat independently from the session that implemented Repair 11.

ENVIRONMENT:
Software Development Environment

REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

AGENT:

* Agent -> claude
* Claude Opus 5
* High reasoning
* Do not use Explore or Plan mode.
* Bypass Permissions may remain enabled. It removes repetitive approval prompts
    but does not expand the authorization boundary defined below.

This task has one strict conditional sequence:

1. independently review and dynamically verify the existing Repair 11 candidate;
2. reconcile all change-boundary evidence, including the reported 15 paths versus
    the VS Code UI display of 14 changed files;
3. only if every independent blocking gate passes:
    * change the version exactly once from 0.3.143 to 0.3.144;
    * build exactly one final 0.3.144 VSIX;
    * verify the exact artifact;
    * install that artifact into Visual Studio Code Stable, Default profile;
4. stop before Runtime QA.

A blocking review finding must stop the task before version bump, package, or
installation. Do not repair findings during this review/finalization task.

Do not ask the user to copy the VSIX into another workspace. Installation from
this source environment into VS Code Stable’s Default profile is shared by the
local Development Test Workspace window after that window is reloaded.

Do not use web search.
Do not download or install dependencies.
Do not create package-lock.json.
Do not access or modify etl-framework-adb.
Do not commit, push, merge, tag, stage, stash, reset, restore, clean, or delete.
Do not publish.
Do not modify protected .github/** assets.
Do not change tests, fixtures, source, contracts, baselines, or prompts to make a
gate pass.
Do not execute a Databricks job or access real data.
Do not start Runtime QA.
Do not create, approve, or consume a real consumer-workspace write.
Do not modify the QA STTM.
Do not modify the existing 0.3.143 VSIX.

The only source edit conditionally authorized after an independent PASS is:

package.json

* version token 0.3.143 -> 0.3.144

Existing Repair 11 files are review subjects, not new editing authorization.

==================================================
0. NATIVE PROCESS EXECUTION PREFLIGHT

Before any edit, prove that this session can execute real native processes.

Run commands showing visible output and exit code 0 for:

* cmd.exe;
* git.exe;
* node.exe;
* npm.cmd.

Report their resolved executable paths and versions.

Do not substitute static inspection for required dynamic execution.

If native execution is unavailable, stop without modifying anything:

REPAIR_11_FINALIZATION_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

==================================================

1. IDENTITY AND IMMUTABLE BASELINE
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
0.3.143

EXPECTED_STAGED_FILE_COUNT:
0

EXPECTED_EXISTING_BASELINE_ARTIFACT:
databricks-etl-copilot-0.3.143.vsix

EXPECTED_NEW_ARTIFACT_BEFORE_FINALIZATION:
databricks-etl-copilot-0.3.144.vsix must not exist

Capture before any edit:

* absolute repository root;
* origin;
* branch;
* HEAD;
* source version;
* staged paths and count;
* git status --porcelain=v2 -z --untracked-files=all;
* flattened tracked-modified and untracked file lists;
* SHA-256 of every current overlay file;
* protected .github/** hashes;
* package-lock.json presence;
* every existing VSIX path.

The working tree is intentionally dirty. Preserve the complete existing overlay.
Do not assume it should be cleaned.

Independently compute the size and SHA-256 of the existing 0.3.143 VSIX. Do not
use a manually transcribed SHA as machine authority. Confirm that its archive
opens and its internal package and manifest versions are 0.3.143. Preserve it
byte-for-byte as the pre-Repair-11 packaged baseline.

Authorized read-only QA input:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Expected size:
1437 bytes

Expected SHA-256:
F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Verify its bytes and hash independently. For dynamic tests, copy those exact bytes
to a task-owned directory under %TEMP%. Never edit or write beside the original.

Report this accurately as:

QA_STTM_READ_ONLY_ACCESS: YES
QA_WORKSPACE_MUTATED: NO

Stop without changes if root, origin, branch, HEAD, version, staged state, or QA
STTM identity conflicts, or if an unexpected 0.3.144 VSIX exists:

REPAIR_11_FINALIZATION_RESULT: BLOCKED_IDENTITY_OR_EXISTING_ARTIFACT

==================================================
2. INDEPENDENCE AND CHANGE-BOUNDARY REVIEW

State explicitly that this session did not implement Repair 11 and does not accept
the implementation agent’s PASS as authority.

Re-derive findings from files, Git state, dynamic execution, compiled output, and
artifacts.

Independently enumerate every Repair 11-attributable production, test,
registration, and fixture file.

The previous report described:

* 4 production files;
* 10 test/registration files;
* 1 fixture file;
* 15 total path-level files.

The VS Code response UI displayed:

14 files changed

Reconcile 14 versus 15 using:

* flattened git status --porcelain=v2 -z --untracked-files=all;
* tracked and untracked file lists;
* directory-versus-file presentation;
* filesystem hashes;
* actual test registration and fixture references;
* any uniquely matching pre-Repair-11 baseline record, if available.

Do not select an earlier baseline merely by newest modification time. A baseline
record may be used only if repository root, HEAD, version, QA STTM hash, and the
reported 75-row starting state uniquely match.

A UI count difference is not automatically a failure if the complete unique path
set reconciles exactly. A missing file, unauthorized file, or unexplained content
change is blocking.

Report:

REPAIR_11_DECLARED_PATH_COUNT
REPAIR_11_ACTUAL_UNIQUE_PATH_COUNT
REPAIR_11_PATHS
PATH_COUNT_RECONCILIATION
UNAUTHORIZED_CHANGED_PATHS

Do not edit anything during this review.

==================================================
3. INDEPENDENT CODE AND CONTRACT REVIEW

Prove the following properties from implementation and dynamic behavior.

A. Exact-file isolation

* A request for one .md file reads only that exact file.
* The requested filename is not replaced with its parent directory.
* Sibling files are not enumerated, opened, parsed, or merged.
* A sibling sentinel mapping cannot enter the result.
* Directory/bundle requests retain canonical bundle behavior.
* Multi-file ambiguity remains fail-closed.
* Workspace-root containment, traversal, symlink, UNC, and different-drive
    protections remain intact.

B. Mapping identity

* Mapping IDs are deterministic across repeated runs.
* Different files and sections with identical line numbers cannot collide.
* IDs are sufficiently file- and section-scoped.
* IDs contain no absolute machine path.
* Equivalent fixtures under different absolute temporary roots produce
    machine-independent identity.
* Path separators and case are normalized deterministically.
* Traceability joins consistently use the same IDs.
* No randomness, timestamp, or LLM-derived value contributes to identity.

C. Exact QA STTM interpretation

Using the exact authorized QA STTM bytes copied to %TEMP%, verify:

* sections total: 5;
* sections recognized: 5;
* Source recognized;
* Target recognized;
* Column mapping recognized;
* Filters recognized;
* Notes recognized;
* structured mappings: exactly 6 in document order;
* source evidence count: 1;
* target evidence count: 1;
* both schema items present;
* notes count: 2;
* filters exactly as present in the file:
    status_cd IS NOT NULL
    updated_ts >= ${etl.effective.start.date}

Do not fabricate or substitute the obsolete expectations:

status_code = ‘ACTIVE’
updated_ts IS NOT NULL

Verify:

* no Unity Catalog table-name inference;
* no raw-content guessing fallback;
* no sibling-derived evidence;
* no fabricated source, target, filters, or values.

D. Completeness and fail-closed behavior

* Zero recognized material sections fails closed.
* Partial material-section recognition emits the explicit
    STTM_MATERIAL_SECTION_UNRECOGNIZED diagnostic and cannot silently appear
    complete.
* The numeric confidence formula remains unchanged.
* No fuzzy heading matching exists.
* Duplicate or ambiguous mapping sections/tables are rejected.
* Consumer context remains advisory and never becomes machine authority.

E. Model compatibility

Review the new notes model field and every mechanical notes: [] test update.

Confirm:

* all production constructors, serializers, and consumers are handled;
* no assertion was weakened;
* no parallel test-only model or production implementation exists;
* no exported/public compatibility boundary was silently broken by a new required
    field;
* source, compiled output, and runtime serialization agree.

A real public/API compatibility break is blocking. Do not repair it here.

F. Golden Path authenticity

Confirm that the Golden Path uses actual production components and proves:

* fresh consumer classification -> CREATE_NEW_JOB;
* exact single-file isolation;
* six mappings in order with unique stable IDs;
* both literal QA filters;
* path-based dataframe_writer;
* format delta;
* write mode append;
* no merge, CDC, SCD2, or direct Unity Catalog write;
* canonical modules-object envelope;
* complete env/job preview manifest with per-file SHA-256;
* every preview path contained under the temporary root;
* explicit approval required;
* consume/write remains not approved;
* zero consumer files created, modified, or deleted.

==================================================
4. DYNAMIC REVIEW GATES BEFORE VERSION EDIT

Use only existing local scripts and dependencies. Record every exact command,
exit code, passing, pending, and failing count.

Run:

1. compile;
2. lint;
3. Repair 11 focused suite;
4. Golden Path suite;
5. Markdown STTM parser suite;
6. STTM evidence-provider suite;
7. STTM reference-retrieval suite;
8. workspace-containment/security suite;
9. Repair 10 regression;
10. Repair 9 regression;
11. Repair 8 regression;
12. Repair 5 regression;
13. Repair 6 regression;
14. Repair 7 regression;
15. the registered trusted-envelope regression;
16. the direct trusted Job Config envelope suite at:
    out/test/suite/trustedJobConfigEnvelope.test.js
17. canonical full unit suite.

The direct trusted-envelope suite must be executed directly rather than inferred
from a broad grep. The previously established direct-suite expectation is 28
passing, 0 pending, 0 failing. If the repository’s canonical file or count has
legitimately changed, explain it using current source/test registration evidence.

Expected full-unit fingerprint before version edit:

* 2217 passing;
* 1 pending;
* 5 failing;
* passing delta from the pre-Repair-11 baseline: +37;
* pending delta: 0;
* failure delta: 0.

Do not call failures historical merely because their count is unchanged.
Independently report:

* full test names;
* assertion/file locations;
* failure causes;
* whether each failure also exists independently of Repair 11;
* whether any Repair 11 path is exercised by it.

Confirm zero new functional and zero new security regressions.

Expected deferred findings may remain only if independently proven non-causal for
this QA path:

* UTF-8 BOM handling, because the authorized QA STTM has no BOM;
* residual first-table assumptions outside the repaired Phase 1 path;
* general parser redesign;
* numeric confidence-model redesign requiring a contract-owner decision;
* the five unchanged repository-baseline/customization failures.

Do not fix deferred findings.

Blocking findings include:

* sibling enumeration or cross-file evidence;
* ID collision, instability, or machine-path leakage;
* incomplete material evidence accepted without a blocking status;
* fabricated STTM values;
* weakened containment, trust, or approval boundaries;
* test-only replacement of production behavior;
* public/API compatibility break;
* unauthorized changed path;
* source/compiled behavior mismatch;
* any new functional or security regression.

If any blocking finding exists, stop without editing, building, or installing:

REPAIR_11_FINALIZATION_RESULT: FAIL_INDEPENDENT_REVIEW

Only after all independent gates pass, report:

INDEPENDENT_REVIEW_VERDICT: PASS

and continue.

==================================================
5. FREEZE REVIEWED SOURCE

After independent PASS, capture SHA-256 for every reviewed Repair 11 source, test,
fixture, and registration file.

Treat those bytes as frozen. From this point:

* do not change any Repair 11 file;
* do not add or modify tests;
* do not update baselines;
* do not edit contracts, skills, prompts, or .github/**.

The sole source edit now authorized is the package.json version token.

==================================================
6. SINGLE VERSION EDIT

Change only:

“version”: “0.3.143”

to:

“version”: “0.3.144”

Do not use npm version.
Do not alter another package.json field.
Do not create a lockfile.

Verify every frozen Repair 11 path remains byte-identical.

If another task-attributable source change appears, stop:

REPAIR_11_FINALIZATION_RESULT: FAIL_UNAUTHORIZED_CHANGE

==================================================
7. POST-VERSION VALIDATION

Re-run:

* compile;
* lint;
* Repair 11 focused suite;
* Golden Path suite;
* direct trusted Job Config envelope suite;
* canonical full unit suite.

Required full-suite fingerprint:

* 2217 passing;
* 1 pending;
* the exact same 5 failures;
* zero new functional regressions;
* zero new security regressions.

If a required result changes, do not repair or package:

REPAIR_11_FINALIZATION_RESULT: FAIL_VALIDATION

==================================================
8. BUILD EXACTLY ONE FINAL 0.3.144 VSIX

Use the existing canonical local packaging workflow and installed toolchain.

Create exactly one artifact:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.144.vsix

Do not create a gate/intermediate VSIX.
Do not use a newest-file or modification-time selector.
Do not rebuild repeatedly after failure.
Do not overwrite an unexpected existing 0.3.144 artifact.
Do not alter the 0.3.143 VSIX.

==================================================
9. VERIFY THE EXACT FINAL PACKAGE

Run the repository exact-package verifier using the explicit final 0.3.144 path.

Independently inspect the archive and verify:

* ZIP archive readable;
* internal package.json version exactly 0.3.144;
* extension.vsixmanifest version exactly 0.3.144;
* publisher td-etl;
* package name databricks-etl-copilot;
* extension ID td-etl.databricks-etl-copilot;
* trusted Job Config contract present and byte-equal to source;
* trusted Oracle contract present and byte-equal to source;
* installed-layout contract resolution passes;
* no etl-framework-adb checkout dependency;
* no absolute machine-specific runtime dependency;
* no forbidden package-hygiene entry;
* no package-lock, source tests, out-test, nested .git, .tmp, .tsbuildinfo,
    source maps, or unexpected source content;
* package entry and size policy pass.

Run behavioral probes against the extracted packaged runtime. Do not rely only on
minified identifier searches. Prove:

* exact-file isolation;
* no sibling enumeration;
* six QA mappings;
* both literal QA filters;
* unique stable mapping IDs;
* material-section fail-closed behavior;
* canonical envelope;
* zero-write approval boundary.

Compare decompressed 0.3.143 and 0.3.144 archives while ignoring ZIP timestamps.

Require:

* no unexplained added or removed entries;
* every changed byte/entry is explained by version metadata or the reviewed
    Repair 11 production/runtime change;
* no tests or fixtures are packaged;
* the 0.3.143 artifact remains byte-identical to its initial baseline.

Do not predeclare or guess the new SHA-256. Compute the real 0.3.144 size and
SHA-256 from the newly built file using two independent local implementations.

If verification fails, do not install:

REPAIR_11_FINALIZATION_RESULT: FAIL_PACKAGE_VERIFICATION

==================================================
10. INSTALL INTO VS CODE STABLE DEFAULT PROFILE

Only after package verification PASS, verify the CLI:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd

Verify:

* Visual Studio Code Stable;
* same Windows user account;
* profile Default;
* no custom --extensions-dir;
* no alternate --user-data-dir;
* no Insiders, WSL, SSH, container, or Extension Development Host target.

Install the exact verified file once:

“C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd” ^
–profile “Default” ^
–install-extension “C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.144.vsix” ^
–force

Then query the same Stable Default profile and verify:

td-etl.databricks-etl-copilot@0.3.144

Do not uninstall first.
Do not copy the VSIX into the QA workspace.
Do not close or reload the QA window automatically.
Do not claim runtime activation from CLI/package metadata alone.

Installation here is user-level for VS Code Stable’s shared Default profile—not
workspace-local. The Development Test Workspace window on this laptop should use
the new version after that window is reloaded.

==================================================
11. FINAL SAFETY RE-CAPTURE

Compare final state with the initial baseline.

Required:

* Repair 11 source/test/fixture bytes unchanged after review freeze;
* package.json changed only at the version token;
* only expected new artifact is the 0.3.144 VSIX;
* 0.3.143 VSIX unchanged;
* QA STTM size and SHA unchanged;
* QA workspace files created/modified/deleted: 0;
* .github/** byte-identical;
* staged files: 0;
* package-lock.json absent;
* dependencies downloaded: NO;
* commit/push/tag/publish: NO;
* Databricks job/real-data access: NO;
* Runtime QA started: NO.

==================================================
12. FINAL REPORT

Return:

INDEPENDENT_SESSION_CONFIRMED: YES/NO
PROCESS_EXECUTION_PREFLIGHT_PASS: YES/NO
REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION_BEFORE: 
SOURCE_VERSION_AFTER: 
STAGED_FILES_AT_START: 
STAGED_FILES_AT_END: 

REPAIR_11_DECLARED_PATH_COUNT: 
REPAIR_11_ACTUAL_UNIQUE_PATH_COUNT: 
REPAIR_11_PATHS: 
PATH_COUNT_RECONCILIATION: 
UNAUTHORIZED_CHANGED_PATHS: 

EXACT_FILE_ISOLATION_PASS: YES/NO
SIBLING_FILE_ENUMERATION: YES/NO
CROSS_FILE_EVIDENCE_LEAK: YES/NO
MAPPING_IDS_UNIQUE: YES/NO
MAPPING_IDS_REPEAT_STABLE: YES/NO
MAPPING_IDS_MACHINE_PATH_FREE: YES/NO
MATERIAL_SECTION_FAIL_CLOSED: YES/NO
PUBLIC_MODEL_COMPATIBILITY_PASS: YES/NO
GOLDEN_PATH_AUTHENTICITY_PASS: YES/NO
GOLDEN_PATH_PASSING_COUNT: 

QA_STRUCTURED_MAPPING_COUNT: 
QA_SOURCE_EVIDENCE_COUNT: 
QA_TARGET_EVIDENCE_COUNT: 
QA_FILTERS: 
QA_NOTES_COUNT: 
QA_STTM_READ_ONLY_ACCESS: YES/NO
QA_STTM_MODIFIED: NO

COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_11_FOCUSED_PASS: YES/NO
STTM_REGRESSION_PASS: YES/NO
CONTAINMENT_SECURITY_PASS: YES/NO
REPAIRS_5_TO_10_REGRESSION_PASS: YES/NO
TRUSTED_ENVELOPE_DIRECT_SUITE_PASS: YES/NO
FULL_UNIT_PASSING_COUNT: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURES: 
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 
DEFERRED_FINDINGS: 

INDEPENDENT_REVIEW_VERDICT: PASS/FAIL
VERSION_EDIT_PERFORMED: YES/NO
AUTHORIZED_SOURCE_EDIT: package.json version token only/NONE

FINAL_EXACT_VSIX_VERIFIER_PASS: YES/NO
FINAL_INDEPENDENT_PACKAGE_INSPECTION_CLEAN: YES/NO
INTERNAL_PACKAGE_VERSION: 
INTERNAL_MANIFEST_VERSION: 
PACKAGED_BEHAVIOR_PROBES_PASS: YES/NO
PACKAGE_DELTA_EXPLAINED: YES/NO
FINAL_VSIX_PATH: 
FINAL_VSIX_SIZE_BYTES: 
FINAL_VSIX_SHA256: 
BASELINE_0_3_143_VSIX_UNCHANGED: YES/NO

VS_CODE_PRODUCT: 
TARGET_PROFILE: 
INSTALL_COMMAND: 
INSTALL_EXIT_CODE: 
INSTALLED_EXTENSION: <ID@version or NONE>
QA_WINDOW_RELOAD_REQUIRED: YES/NO
RUNTIME_ACTIVATION_PROVEN: NO
RUNTIME_QA_STARTED: NO

PACKAGE_LOCK_CREATED: NO
STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
PUBLISHED: NO
QA_WORKSPACE_MUTATED: NO
REAL_DATA_ACCESSED: NO

READY_TO_RELOAD_QA_WINDOW: YES/NO
READY_FOR_RUNTIME_QA_AFTER_RELOAD: YES/NO

End exactly with one:

REPAIR_11_FINALIZATION_RESULT: PASS
REPAIR_11_FINALIZATION_RESULT: FAIL_INDEPENDENT_REVIEW
REPAIR_11_FINALIZATION_RESULT: FAIL_UNAUTHORIZED_CHANGE
REPAIR_11_FINALIZATION_RESULT: FAIL_VALIDATION
REPAIR_11_FINALIZATION_RESULT: FAIL_PACKAGE_VERIFICATION
REPAIR_11_FINALIZATION_RESULT: BLOCKED_EXECUTION_ENVIRONMENT
REPAIR_11_FINALIZATION_RESULT: BLOCKED_IDENTITY_OR_EXISTING_ARTIFACT
