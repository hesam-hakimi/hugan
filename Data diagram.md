TASK: HF1_V2_ROOT_CAUSE_12_STTM_PUBLIC_OUTPUT_GAP_0_3_144_READ_ONLY

Perform a deep, read-only root-cause investigation of the live Runtime QA failure
observed after Repair 11.

This task must determine whether the missing STTM evidence is caused by:

* parser data loss;
* normalized-model data loss;
* evidence-provider loss;
* public tool serialization or projection omission;
* packaged or installed artifact drift;
* agent-side summary omission;
* or an unsupported/overconstrained QA expectation.

Produce a bounded Repair 12 plan only.

Do not implement Repair 12.

==================================================

1. SOFTWARE DEVELOPMENT ENVIRONMENT
    ==================================================

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected identity:

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION:
0.3.144

EXPECTED_VSIX:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.144.vsix

A large dirty working-tree overlay from Repairs 5–11 is expected.

Preserve it exactly.

Do not reset, restore, stash, clean, delete, stage, commit, push, merge, tag, or
modify any existing file.

Do not access or inspect etl-framework-adb.

If repository root, origin, branch, HEAD, or source version differs, stop:

ROOT_CAUSE_12_RESULT: BLOCKED_IDENTITY

If staged files exist, stop:

ROOT_CAUSE_12_RESULT: BLOCKED_STAGED_CHANGES

==================================================
2. NATIVE PROCESS PREFLIGHT

Before analysis, prove that this Local execution environment can launch real
native processes.

Run:

* cmd.exe /c echo PROCESS_EXECUTION_OK
* git.exe –version
* node.exe –version
* npm.cmd –version

Every command must produce visible output and exit code 0.

Do not substitute PowerShell-only static inspection if native processes cannot
execute.

If this gate fails, make no changes and stop:

ROOT_CAUSE_12_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

==================================================
3. STRICT READ-ONLY BOUNDARY

Do not modify:

* source;
* tests;
* fixtures;
* resources;
* skills;
* contracts;
* documentation;
* package.json;
* compiled output;
* VSIX files;
* installed extensions;
* VS Code settings;
* QA workspace files;
* the QA STTM.

Do not:

* compile;
* package;
* install or uninstall an extension;
* reload another VS Code window;
* start Runtime QA;
* create a Preview;
* approve or execute a write;
* access real data;
* edit the Phase 1 QA prompt to make it pass.

Network access and dependency downloads are forbidden.

Read-only dynamic probes are authorized.

If temporary scripts or extracted VSIX entries are deterministically required,
write them only under a new task-owned directory such as:

%TEMP%\hf1v2-root-cause-12\

Report every temporary path created. Never write temporary evidence into either
repository or the QA workspace.

Capture a path-and-content-hash working-tree baseline before investigation and
prove the same baseline remains afterward.

==================================================
4. AUTHORITATIVE LIVE QA RESULT

Treat the following as the captured live 0.3.144 Runtime QA evidence:

ACTIVE_EXTENSION_ID:
td-etl.databricks-etl-copilot

ACTIVE_EXTENSION_VERSION:
0.3.144

RUNTIME_TARGET_TYPE:
consumer-etl-workspace

RUNTIME_READY:
YES

RUNTIME_AVAILABLE:
YES

RUNTIME_BLOCKER_COUNT:
0

WORKSPACE_ROOT:
C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa

WORKSPACE_ROOT_COUNT:
1

SOURCE_CHECKOUT_PRESENT:
NO

ETL_FRAMEWORK_ADB_PRESENT:
NO

STTM file:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Expected STTM identity:

SIZE_BYTES:
1437

SHA256:
F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Live Runtime successes:

* exactly one STTM file parsed;
* no sibling file enumerated;
* all five sections recognized:
    Source, Target, Column mapping, Filters, Notes;
* six ordered mappings returned;
* one source-evidence object reported;
* one target-evidence object reported;
* two schema-evidence objects reported;
* two exact filters returned:
    * status_cd IS NOT NULL
    * updated_ts >= ${etl.effective.start.date}
* no raw-content fallback;
* no obsolete filter values fabricated.

Live Runtime stop findings:

1. Notes section was recognized, but exposed Notes count was 0 instead of 2.
2. Source evidence count was 1, but its exact literal identifier was not exposed.
3. Target evidence count was 1, but its exact literal identifier was not exposed.
4. Mapping IDs and their uniqueness were not exposed.
5. The runtime therefore reported material section loss and stopped before
    Framework discovery, rendering, validation, or Preview.

Required safety evidence:

PREVIEW_ID:
NONE

WRITE_EXECUTED:
NO

QA_WORKSPACE_MUTATED:
NO

Do not reinterpret this failure as a general parser failure: five sections,
six mappings, and both filters already passed.

==================================================
5. EXACT INPUT INSPECTION

Read only the exact authorized QA STTM file above.

Do not enumerate or inspect sibling files in its directory.

Verify its size and SHA-256 before and after the investigation.

Capture with exact line references:

* both Notes rows and their exact contents;
* Source section structure and literal physical identifier;
* Target section structure and literal physical identifier;
* the six mapping rows;
* any mapping IDs explicitly present in the file;
* headings, table headers, list structure, casing, whitespace, and delimiters
    relevant to the failed fields.

Do not normalize or rewrite the file.

Do not assume two visually separate lines automatically represent two structured
Notes rows. Determine the intended Notes contract from authoritative source and
tests.

==================================================
6. END-TO-END DATA-BOUNDARY TRACE

Locate the actual production symbols rather than relying only on these likely
file names.

Trace the exact STTM through every relevant boundary:

1. filesystem reader and single-file routing;
2. Markdown section segmentation;
3. sheet classification;
4. individual section parsers;
5. canonical internal STTM document model;
6. evidence normalization;
7. reference/evidence provider;
8. etl_interpret_sttm handler;
9. language-model-tool response builder;
10. structuredContent/content/text projection;
11. registered tool schema and description;
12. final information visible to the ETL Orchestrator.

Inspect, where applicable:

* src/core/solution/FileSystemSttmDocumentReader.ts
* src/core/sttm/SttmMarkdownBundleParser.ts
* src/core/sttm/SttmTypes.ts
* src/core/sttm/SttmReferenceResolver.ts
* src/core/solution/SttmEvidenceProvider.ts
* src/tools/EtlReadOnlyToolService.ts
* tool registration and package.json languageModelTools declarations;
* relevant renderer, wrapper, serializer, and result types;
* Repair 10 and Repair 11 tests;
* Golden Path pre-package tests;
* compiled out/** equivalents;
* extracted 0.3.144 VSIX entries;
* installed-layout 0.3.144 entries.

Search for the actual call chain and report it. Do not assume the candidate list
is complete.

For each stage capture:

* Notes collection and exact values;
* Source evidence count and literal value;
* Target evidence count and literal value;
* Mapping count;
* mapping IDs;
* mapping-ID uniqueness;
* diagnostics;
* confidence/status;
* property names and nesting;
* whether a field exists but is excluded from public output.

The report must identify the first boundary where every missing datum:

* ceases to exist; or
* still exists but ceases to be externally observable.

==================================================
7. READ-ONLY DYNAMIC PROBES

Use existing production code and existing local dependencies only.

Do not implement a parallel parser or hard-code expected output in the probe.

Using the exact QA STTM, compare:

A. current compiled repository runtime;
B. the exact 0.3.144 VSIX packaged runtime;
C. the installed-layout 0.3.144 runtime;
D. the public etl_interpret_sttm adapter/response surface.

Where an existing repository test harness can invoke the real public tool
adapter without mutation, use it.

Otherwise, create the smallest possible temporary probe under the authorized
%TEMP% directory that imports and invokes the existing production entry points.

Run each deterministic probe twice and compare results.

Do not compile or rebuild source during this investigation.

For every probe report:

* exact command;
* exact production entry point invoked;
* input path and input SHA-256;
* exit code;
* output object shape;
* Notes count and values;
* Source/Target fields and values;
* mapping IDs and uniqueness;
* diagnostics;
* whether the result is internal or public;
* whether repeated results are byte-stable.

If invoking the public adapter requires an unavailable VS Code Extension Host,
do not simulate a successful public response. Inspect the adapter and existing
tests, report the limitation, and classify any unsupported conclusion as
UNRESOLVED.

==================================================
8. SOURCE / COMPILED / VSIX / INSTALLED PARITY

Verify:

* source package version is 0.3.144;
* VSIX internal package.json version is 0.3.144;
* VSIX internal manifest version is 0.3.144;
* publisher and extension ID are correct;
* the inspected compiled files are the files packaged in the explicit VSIX;
* packaged relevant entries match installed-layout 0.3.144 entries;
* Repair 11 logic is present in compiled, packaged, and installed artifacts;
* no 0.3.142 file is accidentally loaded or compared as 0.3.144.

Stream or extract archive entries only under the authorized temporary directory.

Do not use modification time or a “newest VSIX” selector to choose the artifact.

Report ARTIFACT_DRIFT: YES only when content evidence proves a semantic
source/compiled/package/installed mismatch.

The mere presence of an old 0.3.142 installation directory is not artifact drift.

==================================================
9. PUBLIC CONTRACT AUTHORITY

For each failed expectation, identify whether it is promised by an authoritative
public contract.

Inspect:

* registered language-model-tool schema and description;
* installed packaged skill instructions;
* trusted packaged contracts;
* package model descriptions;
* public result types;
* runtime consumer code;
* production downstream render/discovery consumers;
* focused and Golden Path tests.

Consumer-editable context is advisory and cannot establish machine authority.

An internal TypeScript property alone is not automatically a public promise.
A failing QA assertion alone is not contract authority.

Determine separately:

A. NOTES

* Were both Notes parsed internally?
* Were they normalized into the canonical model?
* Were they intentionally advisory?
* Did a serializer or projection convert them to an empty collection?
* Does the public contract promise Notes content or count?

B. SOURCE AND TARGET

* Are the exact path-backed Delta identifiers preserved internally?
* Are they exposed under another documented property?
* Does the public contract require literal values or only evidence counts?
* Can deterministic downstream rendering obtain the physical paths without
    raw-content guessing or consumer-context authority?

C. MAPPING IDS

* Do six deterministic internal IDs exist?
* Are all six unique?
* Are IDs file/section scoped as Repair 11 intended?
* Does the public contract promise the IDs themselves?
* Does it promise an explicit uniqueness field, or is uniqueness only an
    internal invariant?

D. GOLDEN PATH COVERAGE

Determine whether the existing Repair 11 Golden Path test:

* invokes the real public etl_interpret_sttm result surface; or
* stops at an internal parser/evidence model and therefore misses the runtime
    projection seam.

This determination must be explicit.

==================================================
10. ROOT-CAUSE CLASSIFICATION

Classify each symptom independently using the earliest proven divergence:

* PARSER_DATA_LOSS
* MODEL_NORMALIZATION_LOSS
* EVIDENCE_PROVIDER_LOSS
* PUBLIC_TOOL_SERIALIZATION_OMISSION
* PUBLIC_TOOL_SCHEMA_OMISSION
* AGENT_SUMMARY_OMISSION
* TEST_OVERCONSTRAINT
* ARTIFACT_DRIFT
* COMPOSITE
* UNRESOLVED

Do not weaken the QA contract merely because the current tool does not expose a
field.

Do not modify production code merely because the QA prompt requested an
unsupported presentation field.

For Source and Target, explicitly decide whether the missing literals prevent a
real consumer from rendering the requested path-based dataframe_writer.

For Notes, explicitly decide whether zero exposed Notes constitutes material
section loss or an intentionally documented advisory projection.

For mapping IDs, explicitly separate:

* IDs being internally correct;
* IDs being externally visible;
* uniqueness being externally asserted.

==================================================
11. TEST-COVERAGE GAP ANALYSIS

Report which existing test should have detected this exact live discrepancy and
why it did not.

Determine whether a future test must cross this full seam:

exact single-file Markdown
→ production reader
→ production parser
→ canonical model
→ evidence provider
→ actual public etl_interpret_sttm response
→ packaged installed-layout runtime.

Do not add or edit tests in this task.

List the exact future positive and negative assertions needed, including:

* two Notes retained or intentionally excluded according to contract;
* exact Source and Target path evidence;
* six deterministic unique mapping IDs;
* no sibling enumeration;
* no raw-content fallback;
* no loss of existing five-section/six-mapping/two-filter behavior;
* public response and internal model parity for contract-required fields.

==================================================
12. BOUNDED REPAIR 12 PLAN — DO NOT IMPLEMENT

Produce one evidence-based Repair 12 plan.

Maximum:

* eight ordered implementation actions;
* eight production/test/contract files.

Choose only the proven repair branch:

A. parser/model repair;
B. evidence-provider repair;
C. public serializer/schema repair;
D. QA-contract correction;
E. artifact-chain repair;
F. a proven minimal composite.

For every proposed file report:

* exact symbol;
* evidence proving it must change;
* intended behavior;
* focused tests;
* security/trust boundary preserved.

Do not propose:

* a general parser redesign;
* fuzzy inference;
* raw-content or LLM fallback;
* fabricated identifiers;
* consumer context as machine authority;
* unrelated cleanup;
* dependency upgrades;
* changes to Repairs 9–11 that are not proven necessary.

If the root cause is not proven strongly enough, set:

REPAIR_12_PLAN: BLOCKED

Do not speculate.

A future implementation, independent review, version bump to 0.3.145, package,
installation, and Runtime QA will require separate authorization. Do none of
them now.

==================================================
13. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION: 
PROCESS_EXECUTION_PREFLIGHT: PASS/FAIL
STAGED_FILES: 
WORKTREE_BASELINE_PRESERVED: YES/NO

QA_STTM_PATH: 
QA_STTM_SIZE_BYTES: 
QA_STTM_SHA256_BEFORE: 
QA_STTM_SHA256_AFTER: 
QA_STTM_UNCHANGED: YES/NO
QA_NOTES_RAW_COUNT: 
QA_SOURCE_LITERAL: 
QA_TARGET_LITERAL: 
QA_MAPPING_ROWS: 
QA_MAPPING_IDS_IN_INPUT: 

SOURCE_INTERNAL_NOTES_COUNT: <number/NOT_PRESENT/UNRESOLVED>
COMPILED_INTERNAL_NOTES_COUNT: <number/NOT_PRESENT/UNRESOLVED>
PACKAGED_INTERNAL_NOTES_COUNT: <number/NOT_PRESENT/UNRESOLVED>
PUBLIC_TOOL_NOTES_COUNT: <number/NOT_EXPOSED/UNRESOLVED>

SOURCE_LITERAL_INTERNAL_STATUS: PRESENT/ABSENT/UNRESOLVED
TARGET_LITERAL_INTERNAL_STATUS: PRESENT/ABSENT/UNRESOLVED
PUBLIC_SOURCE_LITERAL_STATUS: PRESENT/ABSENT/NOT_PROMISED/UNRESOLVED
PUBLIC_TARGET_LITERAL_STATUS: PRESENT/ABSENT/NOT_PROMISED/UNRESOLVED

INTERNAL_MAPPING_ID_COUNT: <number/UNRESOLVED>
INTERNAL_MAPPING_IDS_UNIQUE: YES/NO/UNRESOLVED
PUBLIC_MAPPING_IDS_EXPOSED: YES/NO/UNRESOLVED
PUBLIC_MAPPING_ID_UNIQUENESS_PROMISED: YES/NO/UNRESOLVED

GOLDEN_PATH_CROSSES_PUBLIC_TOOL_BOUNDARY: YES/NO
SOURCE_COMPILED_PARITY: PASS/FAIL/UNRESOLVED
COMPILED_VSIX_PARITY: PASS/FAIL/UNRESOLVED
VSIX_INSTALLED_LAYOUT_PARITY: PASS/FAIL/UNRESOLVED
ARTIFACT_DRIFT: YES/NO/UNRESOLVED

NOTES_ROOT_CAUSE: 
SOURCE_TARGET_ROOT_CAUSE: 
MAPPING_IDS_ROOT_CAUSE: 
PRIMARY_ROOT_CAUSE: 
SECONDARY_ROOT_CAUSES: 
QA_EXPECTATION_CORRECTION_REQUIRED: YES/NO/UNRESOLVED
PRODUCTION_REPAIR_REQUIRED: YES/NO/UNRESOLVED
REPAIR_12_PLAN: READY/BLOCKED
REPAIR_12_PROPOSED_PATHS: 

SOURCE_FILES_MODIFIED: 0
TEST_FILES_MODIFIED: 0
PACKAGE_JSON_MODIFIED: NO
VSIX_MODIFIED: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
QA_WORKSPACE_MUTATED: NO
TEMP_ARTIFACTS: 

End exactly with one:

ROOT_CAUSE_12_RESULT: CONFIRMED_PUBLIC_OUTPUT_GAP
ROOT_CAUSE_12_RESULT: CONFIRMED_PARSER_OR_MODEL_LOSS
ROOT_CAUSE_12_RESULT: CONFIRMED_QA_OVERCONSTRAINT
ROOT_CAUSE_12_RESULT: CONFIRMED_ARTIFACT_DRIFT
ROOT_CAUSE_12_RESULT: CONFIRMED_COMPOSITE
ROOT_CAUSE_12_RESULT: INCONCLUSIVE
ROOT_CAUSE_12_RESULT: BLOCKED_IDENTITY
ROOT_CAUSE_12_RESULT: BLOCKED_STAGED_CHANGES
ROOT_CAUSE_12_RESULT: BLOCKED_EXECUTION_ENVIRONMENT
