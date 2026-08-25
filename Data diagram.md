TASK: HF1_V2_ROOT_CAUSE_11_INDEPENDENT_CONFIRMATION_NO_BUILD_NO_WRITE

Perform a genuinely independent, read-only confirmation of the findings reported
against Repair 10 and Databricks ETL Copilot 0.3.143.

This must run in a completely new Chat/session that did not implement Repair 10
and did not produce the 0.3.143 VSIX.

Work only in the Software Development Environment:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected identity:

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE VERSION:
0.3.143

EXISTING VSIX:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.143.vsix

VSIX SIZE:
1255490

VSIX SHA-256:
8819E0902BF5FE1F8EFE9BA302EB196D3715AF17DC5F44B76F3C0EACBDB3CFFA

Authorized read-only QA input:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Expected QA STTM SHA-256:

F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

==================================================
0. INDEPENDENCE AND ZERO-WRITE RULES

Before inspection, report whether this Chat/session previously:

* implemented Repair 10;
* modified its source or tests;
* built version 0.3.143;
* issued the earlier Repair 10 PASS.

If YES to any item, stop with:

ROOT_CAUSE_11_RESULT: BLOCKED_NOT_INDEPENDENT

This task is investigation only.

Do not:

* edit any repository or QA file;
* run npm run compile;
* run npm run package:prepare;
* run vsce package;
* build or rebuild a VSIX;
* modify or regenerate out/**;
* install an extension;
* start Runtime QA;
* create a Preview ID;
* execute an ETL write;
* stage, commit, push, tag, stash, reset, restore, clean, or delete;
* download dependencies;
* create package-lock.json.

Read-only Git commands are permitted.

Runtime probes may use only:

* the existing compiled output;
* the exact existing 0.3.143 VSIX;
* task-owned files under %TEMP%.

Do not write test fixtures into the repository.

Capture repository status and hashes before and after. They must remain identical.

==================================================

1. IDENTITY GATE
    ==================================================

Verify:

* repository root;
* origin;
* branch;
* HEAD;
* source version;
* staged-file count;
* VSIX path, size, SHA-256;
* QA STTM path and SHA-256.

If any value conflicts, stop without further work.

==================================================
2. FINDING A — SIBLING-FILE READ AMPLIFICATION

Independently trace the complete Markdown read path beginning with a request for
one specific .md file.

Inspect at minimum:

* FileSystemSttmDocumentReader;
* parseSttmMarkdownBundle;
* SttmMarkdownBundleParser;
* SttmEvidenceProvider;
* the tool-facing STTM interpretation path.

Determine whether requesting:

\requested.md

causes the runtime to enumerate and parse other sibling .md files in the same
directory.

Create an isolated %TEMP% reproduction:

1. requested.md contains one valid mapping section and one identifiable mapping;
2. unrelated-sibling.md contains a different valid mapping section and a unique
    sentinel mapping;
3. invoke the same public/runtime read path while naming only requested.md;
4. inspect whether the sentinel mapping from unrelated-sibling.md appears.

Repeat the reproduction against:

* existing compiled output;
* the exact extracted 0.3.143 packaged runtime.

Required report:

REQUESTED_FILE_ONLY_READ: YES/NO
SIBLING_FILE_ENUMERATION_OCCURRED: YES/NO
SIBLING_SENTINEL_MAPPING_LEAKED: YES/NO
CROSS_FILE_AMBIGUITY_REJECTED: YES/NO
SOURCE_COMPILED_PACKAGED_BEHAVIOR_MATCH: YES/NO

If the sibling sentinel is returned without explicit authorization, classify it
as a HIGH correctness and trust-boundary defect.

Determine whether the correct boundary should be:

* exact-file parsing for a single-file STTM request; and
* explicit directory enumeration only when the caller explicitly supplies a
    bundle directory.

Do not implement the correction.

==================================================
3. FINDING B — MAPPING-ID UNIQUENESS

Inspect how mapping IDs are generated for:

* canonical bundle rows;
* single-file sectioned Markdown rows;
* mappings originating from different files;
* mappings originating from different logical sections.

Determine whether IDs such as:

FM_

can collide across separate files or sections.

Use a %TEMP% reproduction with two logical inputs having mappings on the same
source line.

Report:

MAPPING_ID_COLLISION_REPRODUCED: YES/NO
CURRENT_ID_FILE_SCOPED: YES/NO
CURRENT_ID_SECTION_SCOPED: YES/NO
TRACEABILITY_JOIN_RISK: HIGH/MEDIUM/LOW/NONE

Propose a deterministic stable identity input, but do not implement it.

It must not expose absolute machine paths and must not use random values.

==================================================
4. FINDING C — PARTIAL-RECOGNITION CONFIDENCE

Run the existing packaged parser against the exact unmodified QA STTM.

Report:

* total logical sections;
* recognized sections;
* unrecognized sections;
* extracted mappings;
* extracted source evidence;
* extracted target evidence;
* extracted filters;
* extracted notes;
* diagnostics;
* confidence;
* status.

Determine whether recognizing only the mapping section while dropping the
Source, Target, Filters, and Notes sections can still produce approximately
0.90 confidence.

Report:

PARTIAL_RECOGNITION_CONFIDENCE_OVERSTATED: YES/NO
ZERO_RECOGNIZED_FAIL_CLOSED: YES/NO
PARTIAL_RECOGNITION_PENALIZED: YES/NO
MISSING_MATERIAL_SECTION_DIAGNOSTIC_PRESENT: YES/NO

Determine which sections are material for the advertised interpretation
contract and whether confidence/status should reflect missing material sections.

Do not invent a new confidence formula and do not implement a change.

==================================================
5. FINDING D — UTF-8 BOM HANDLING

Create two byte-identical logical STTM inputs under %TEMP%:

* UTF-8 without BOM;
* UTF-8 with BOM.

Run the existing compiled and packaged parser against both.

Report:

NO_BOM_MAPPING_COUNT: 
BOM_MAPPING_COUNT: 
BOM_CHANGES_SECTION_SEGMENTATION: YES/NO
BOM_DIAGNOSTIC_ACCURATE: YES/NO
BOM_FINDING_SEVERITY: HIGH/MEDIUM/LOW/INFORMATIONAL

Do not modify the parser.

==================================================
6. FINDING E — RESIDUAL FIRST-TABLE ASSUMPTIONS

Search for remaining firstTable(…) or tables[0] behavior in all Markdown STTM
section parsers.

Distinguish:

* mapping parsing changed by Repair 10;
* revision-history parsing;
* business-rule/schema/filter/source/target parsing;
* unrelated pre-existing behavior.

Report every remaining first-table assumption with exact file and line evidence
and whether it can affect the Phase 1 QA input.

==================================================
7. QA CONTRACT AND PROMPT DISCREPANCY

Read the exact QA STTM content and report its literal filter expressions.

Do not rely on the earlier Runtime QA prompt.

Specifically verify whether the file contains:

* status_cd IS NOT NULL;
* updated_ts >= ${etl.effective.start.date};

and whether it contains or does not contain:

* status_code = ‘ACTIVE’;
* updated_ts IS NOT NULL.

Report:

QA_STTM_LITERAL_FILTERS: 
EARLIER_RUNTIME_PROMPT_FILTERS_MATCH_FILE: YES/NO
QA_STTM_WAS_MODIFIED: NO

Also separate:

* evidence explicitly present in the STTM;
* fixed QA inputs supplied externally by the Runtime QA prompt;
* evidence currently lost because a section is unrecognized.

This discrepancy is a test-specification issue and must not be “fixed” by
editing the STTM or making the parser fabricate missing values.

==================================================
8. ROOT-CAUSE AND BOUNDED REPAIR PLAN

If the findings are confirmed, provide a bounded Repair 11 plan covering only
the confirmed defects.

The plan must preserve:

* exact workspace-root containment;
* no sibling or traversal escape;
* explicit single-file versus bundle-directory semantics;
* deterministic parsing;
* explicit enumerated aliases;
* rejection of ambiguous sections/tables;
* fail-closed behavior;
* consumer context remaining advisory only;
* canonical Markdown bundle compatibility;
* Excel STTM compatibility;
* Repairs 5–10 behavior;
* preview/write approval boundaries.

Identify:

* exact source files;
* exact functions;
* exact tests and fixtures to add;
* negative/security controls;
* package/documentation changes, if contract behavior changes;
* whether the next version should be 0.3.144.

Do not implement, build, install, or run Runtime QA.

==================================================
9. FINAL REPORT

Return:

INDEPENDENT_SESSION_CONFIRMED: YES/NO
REPOSITORY_IDENTITY_PASS: YES/NO
VSIX_IDENTITY_PASS: YES/NO
QA_STTM_IDENTITY_PASS: YES/NO
SIBLING_FILE_ENUMERATION_OCCURRED: YES/NO
SIBLING_SENTINEL_MAPPING_LEAKED: YES/NO
CROSS_FILE_AMBIGUITY_REJECTED: YES/NO
MAPPING_ID_COLLISION_REPRODUCED: YES/NO
PARTIAL_RECOGNITION_CONFIDENCE_OVERSTATED: YES/NO
BOM_CHANGES_SECTION_SEGMENTATION: YES/NO
RESIDUAL_FIRST_TABLE_ASSUMPTIONS: 
QA_STTM_LITERAL_FILTERS: 
EARLIER_RUNTIME_PROMPT_FILTERS_MATCH_FILE: YES/NO
HIGH_FINDING_COUNT: 
MEDIUM_FINDING_COUNT: 
LOW_FINDING_COUNT: 
CONFIRMED_FINDINGS: 
REJECTED_FINDINGS: 
PROPOSED_REPAIR_VERSION: 
PROPOSED_CHANGED_SOURCE_PATHS: 
PROPOSED_CHANGED_TEST_PATHS: 
REPOSITORY_FILES_CHANGED: 0
QA_FILES_CHANGED: 0
OUT_REGENERATED: NO
VSIX_BUILT: NO
EXTENSION_INSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
READY_FOR_BOUNDED_REPAIR: YES/NO

End exactly with one:

ROOT_CAUSE_11_RESULT: CONFIRMED

ROOT_CAUSE_11_RESULT: PARTIALLY_CONFIRMED

ROOT_CAUSE_11_RESULT: REJECTED

ROOT_CAUSE_11_RESULT: BLOCKED_NOT_INDEPENDENT

ROOT_CAUSE_11_RESULT: BLOCKED_IDENTITY_MISMATCH

ROOT_CAUSE_11_RESULT: BLOCKED_EXECUTION_ENVIRONMENT
