TASK: HF1_V2_REPAIR_12_PUBLIC_STTM_PROJECTION_IMPLEMENTATION_PRE_REVIEW_NO_VSIX

Implement only the confirmed Repair 12 defect at the public
etl_interpret_sttm projection boundary.

The 0.3.144 parser and canonical internal model are correct. The defect is that
contract-required evidence is lost or incompletely rendered while producing the
public structured result and Markdown result.

This task must:

1. dynamically reproduce the existing public-output loss before editing;
2. implement one shared canonical public projection for both output channels;
3. add full-seam tests against the actual public etl_interpret_sttm response;
4. run compile, lint, focused, security, regression, and full-unit gates;
5. stop with a source-level candidate ready for a genuinely independent review.

Do not bump the version.
Do not build, modify, install, or uninstall a VSIX.
Do not run Runtime QA.
Do not create or approve a Preview.
Do not execute an ETL write.
Do not commit, push, merge, tag, stage, stash, reset, restore, clean, or delete.

==================================================

1. EXACT SOFTWARE DEVELOPMENT ENVIRONMENT
    ==================================================

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Required identity:

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION:
0.3.144

Expected protected artifact:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.144.vsix

A large uncommitted overlay from Repairs 5–11 is expected. Preserve it exactly.

Capture:

* repository root;
* origin;
* branch;
* HEAD;
* package.json version;
* staged paths;
* tracked-modified paths;
* untracked paths;
* package-lock.json presence;
* existing 0.3.144 VSIX path, size, and SHA-256;
* path, type, size, and content hash of every working-tree entry.

Do not assume that a remembered porcelain count remains exact.

If root, origin, branch, HEAD, or source version differs, stop unchanged:

REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_IDENTITY

If staged files exist, stop unchanged:

REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_STAGED_CHANGES

If repository content changes after the baseline from another process or agent,
before this task makes its first authorized edit, stop:

REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_CONCURRENT_MUTATION

Never normalize or clean the dirty working tree.

==================================================
2. NATIVE EXECUTION PREFLIGHT

Before editing, execute as real native processes:

* cmd.exe /c echo PROCESS_EXECUTION_OK
* git.exe –version
* node.exe –version
* npm.cmd –version

Every command must produce visible output and exit code 0.

Do not replace required dynamic execution with static source inspection.

If this gate fails, make no changes and stop:

REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

==================================================
3. AUTHORIZED READ-ONLY QA INPUT

The only authorized QA input is:

C:\Users\tag5916\etl-qa\hf1v2\consumer-fresh\etl-acz9999-hf1v2-qa\sttm\qa_hf1v2_demo_sttm.md

Expected:

SIZE_BYTES:
1437

SHA256:
F172E5EBDDEFFFFBFD4C148E9A2F4FD279DBDA068728705CC5891C9AD3C56BAF

Read exactly this file.

Do not enumerate or inspect sibling QA files.
Do not modify this file or any QA workspace path.
Record size and SHA-256 before and after the task.

Expected authored evidence:

SOURCE_LITERAL:
raw.qa_hf1v2_customer

TARGET_LITERAL:
curated.qa_hf1v2_customer

These are consumer-authored logical dotted object references. They are not
physical paths and must not be reinterpreted as:

* ABFSS paths;
* Unity Catalog authority;
* database/schema/table triples;
* physical writer destinations.

Expected content:

* five recognized sections;
* six ordered mappings;
* two Notes bullets;
* two filters:
    * status_cd IS NOT NULL
    * updated_ts >= ${etl.effective.start.date}

==================================================
4. CONFIRMED ROOT CAUSE

Root Cause 12 proved dynamically:

INTERNAL MODEL:

* Notes count = 2, including deterministic IDs and verbatim line-scoped text;
* Source literal is present in Source-section attributes;
* Target literal is present in Target-section attributes;
* mapping count = 6;
* mapping-ID count = 6;
* mapping IDs are deterministic, unique, and file/section scoped;
* filter count = 2;
* all five sections are present.

PUBLIC STRUCTURED/MARKDOWN OUTPUT:

* Notes are absent;
* Source and Target authored literals are absent;
* mapping IDs already exist at:
    resolvedEvidence.activeMappings[].mappingId;
* mapping IDs are absent from rendered Markdown;
* no public contract promises a separate mappingIdsUnique field.

PARITY:

SOURCE_COMPILED_PARITY: PASS
COMPILED_VSIX_PARITY: PASS
VSIX_INSTALLED_LAYOUT_PARITY: PASS
ARTIFACT_DRIFT: NO

PRIMARY ROOT CAUSE:

PUBLIC_TOOL_SCHEMA_OMISSION plus PUBLIC_TOOL_SERIALIZATION_OMISSION at the
etl_interpret_sttm public projection seam.

SECONDARY ROOT CAUSE:

Repair 11 tests stop at the internal model and do not cross the actual public
tool-response boundary.

Do not change the parser merely to work around a projection defect.

==================================================
5. STRICT CHANGE BOUNDARY

Authorize changes only in:

1. src/core/sttm/SttmResolvedEvidence.ts
2. src/core/sttm/SttmUnderstandingReportRenderer.ts
3. src/tools/EtlReadOnlyToolService.ts
4. package.json
5. src/test/suite/sttmRepair12.test.ts
6. src/test/suite/EtlReadOnlyToolService.test.ts

src/test/suite/sttmRepair12.test.ts may be created.

For package.json, authorize only the description/modelDescription belonging to
the existing etl_interpret_sttm language-model tool.

Do not change:

* package.json version;
* publisher or extension ID;
* scripts, dependencies, engines, or activation events;
* another language-model tool;
* package-lock.json;
* parser recognition or normalization logic;
* resources/copilot/skills/**;
* trusted contracts;
* .github/**;
* QA workspace files;
* existing VSIX files;
* unrelated Repairs 5–11 behavior.

If an authorized file does not require modification, leave it unchanged and
report why.

Do not add another path. If another source or test path is truly required, stop:

REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_CHANGE_BOUNDARY

Ignored generated out/** files from compilation must be reported separately
and must not be presented as intentional source changes.

==================================================
6. PRE-CHANGE DYNAMIC PUBLIC-SEAM REPRODUCTION

Before editing, dynamically reproduce the defect using the exact QA STTM and
existing production code.

Temporary probes may be created only under:

%TEMP%\hf1v2-repair12\

A probe must not copy or reimplement a parser, projector, serializer, renderer,
or expected result.

Invoke the real production chain:

exact single Markdown file
→ FileSystemSttmDocumentReader
→ production Markdown parser
→ canonical model
→ SttmEvidenceProvider
→ resolved evidence
→ actual EtlReadOnlyToolService etl_interpret_sttm result construction
→ structured public data
→ rendered public Markdown.

If a VS Code boundary must be stubbed, use the smallest existing repository seam
required to invoke the real handler. Never simulate the returned payload.

Run the probe twice.

Required pre-change evidence:

PRE_INTERNAL_NOTES_COUNT: 2
PRE_INTERNAL_SOURCE_LITERAL: raw.qa_hf1v2_customer
PRE_INTERNAL_TARGET_LITERAL: curated.qa_hf1v2_customer
PRE_INTERNAL_MAPPING_ID_COUNT: 6
PRE_INTERNAL_MAPPING_IDS_UNIQUE: YES

PRE_PUBLIC_STRUCTURED_NOTES_EXPOSED: NO
PRE_PUBLIC_MARKDOWN_NOTES_EXPOSED: NO
PRE_PUBLIC_SOURCE_LITERAL_EXPOSED: NO
PRE_PUBLIC_TARGET_LITERAL_EXPOSED: NO
PRE_PUBLIC_STRUCTURED_MAPPING_ID_COUNT: 6
PRE_PUBLIC_MARKDOWN_MAPPING_ID_COUNT: 0

No sibling QA file may be opened or enumerated.

Semantic results must match across both runs. A documented audit timestamp may
differ and must be reported separately.

If the defect is not reproduced, make no edit and stop:

REPAIR_12_IMPLEMENTATION_RESULT: FAIL_PRECHANGE_REPRODUCTION

Recapture the repository baseline after reproduction. If it drifted from the
initial baseline for reasons outside task-owned temporary or ignored compiled
output, stop as:

REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_CONCURRENT_MUTATION

==================================================
7. ONE SHARED CANONICAL PUBLIC PROJECTOR

The structured result and Markdown renderer must not independently rediscover or
reinterpret STTM evidence.

Create one typed, additive canonical public projection and one deterministic
production projector inside an already authorized production file.

Recommended ownership:

src/core/sttm/SttmResolvedEvidence.ts

Follow existing naming conventions, but both of these consumers must use the
same projector:

* InterpretSttmToolData construction;
* SttmUnderstandingReportRenderer.

Do not create duplicate Source/Target/Notes/Mapping-ID extraction paths.

The projector must consume normalized or resolved production evidence, never raw
Markdown.

The projection must add only the public evidence required for this repair:

* typed Source-section evidence;
* typed Target-section evidence;
* advisory Notes;
* active mappings retaining their existing mapping IDs;
* existing filters and already-public evidence;
* diagnostics for absent, duplicate, ambiguous, conflicting, or malformed
    projection evidence.

The contract must be additive. Preserve all existing public fields and meanings.

Keep mappings as an array. Never key mappings by mappingId, because missing or
duplicate IDs must not overwrite mappings.

Do not expose a generic dump of arbitrary section attributes. Publish only the
narrow, declared typed evidence required by the public contract.

==================================================
8. SOURCE AND TARGET EVIDENCE RULES

Represent Source and Target as dedicated typed section evidence.

Resolve each value only from its corresponding recognized section:

* Source only from the recognized Source section;
* Target only from the recognized Target section.

Prefer already-normalized typed section evidence.

If a fallback to section attributes is necessary:

* use only the parser’s declared exact attribute contract;
* require exactly one matching Source value;
* require exactly one matching Target value;
* copy the authored value verbatim;
* use property-presence checks, not truthiness;
* never scan arbitrary attributes heuristically.

Conflict behavior:

* zero matching values: omit the value and return an actionable diagnostic;
* exactly one value: expose it verbatim;
* explicit empty value: preserve its presence; never reveal a lower-priority
    fallback value;
* multiple identical values: follow the existing duplicate-section policy and
    emit the appropriate diagnostic;
* multiple distinct values: fail closed with an ambiguity/conflict diagnostic;
* never silently select first, last, shortest, newest, or lexically smallest.

Do not:

* split dotted values;
* infer database/schema/table components;
* infer Unity Catalog;
* infer ABFSS;
* infer a physical destination;
* copy Source evidence into Target or Target into Source;
* use mapping.targetEntity as a substitute for authored Target-section
    evidence;
* scrape raw Markdown at the public projection boundary;
* fabricate a value.

==================================================
9. ADVISORY NOTES TRUST BOUNDARY

Notes are untrusted, advisory consumer-authored data.

Expose only normalized Notes already present in the canonical internal model.

Each projected Note must preserve:

* existing deterministic opaque ID;
* section identity;
* semantic text;
* existing active/advisory state.

Notes must never become:

* machine authority;
* executable instructions;
* configuration;
* module-selection evidence;
* path or writer authority;
* approval or write authorization;
* trusted prompt instructions.

Structured output must preserve its contract structure even when Note text
contains control-like or prompt-like content.

Markdown output must use deterministic sink-specific escaping so Notes cannot:

* inject a table column;
* inject an authoritative heading or tool directive;
* break a table/code boundary;
* escape the data section;
* create uncontrolled response expansion.

Cover at least:

* pipes;
* backticks;
* Markdown headings;
* brackets;
* quotes and backslashes;
* HTML-like content;
* CR/LF;
* Unicode and bidi/control-like input;
* instruction-like text.

Reuse existing repository escaping and response-size limits wherever available.
Do not introduce a second parser or an LLM/raw-content sanitization step.

Do not emit arbitrary Source/Target attributes, secret-like attributes, or raw
section metadata through this repair.

==================================================
10. MAPPING-ID CONTRACT

Use each existing internal mappingId as an opaque string.

Do not:

* regenerate it;
* normalize its case;
* coerce numeric-looking values;
* truncate it into another apparently valid ID;
* use it for authorization;
* synthesize a replacement for a missing ID.

Structured output must continue exposing mapping IDs through:

resolvedEvidence.activeMappings[].mappingId

Rendered Markdown must append a Mapping ID column to the existing Active
Mappings table.

The new column must be the final column so existing column ordering remains
stable.

Do not add:

* mappingIdsUnique;
* another uniqueness Boolean;
* a parallel mapping-ID collection.

Tests must derive uniqueness from the six existing IDs.

==================================================
11. STRUCTURED AND MARKDOWN OUTPUT REPAIR

STRUCTURED OUTPUT must:

* expose exactly two advisory Notes for the QA input;
* expose exact typed Source evidence;
* expose exact typed Target evidence;
* retain six active mappings and their IDs;
* preserve the two filters;
* use optional/additive fields so older inputs remain compatible.

MARKDOWN OUTPUT must:

* render Source literal verbatim;
* render Target literal verbatim;
* render a Notes section with IDs, safely rendered text, and an advisory label;
* append Mapping ID as the final Active Mappings column;
* preserve all existing headings and table semantics otherwise.

Both public channels must consume the same canonical projector.

The renderer must not reach back into raw Markdown or independently repeat the
projection rules.

Unknown or malformed new evidence must produce a diagnostic and be omitted
without triggering raw fallback or failing unrelated valid mappings.

==================================================
12. TOOL DESCRIPTION ALIGNMENT

Modify only the existing etl_interpret_sttm description/modelDescription in
package.json.

State accurately that the public result may contain:

* Source;
* Target;
* mappings;
* filters;
* advisory Notes;
* deterministic mapping IDs.

State that:

* Source and Target are copied from recognized authored section evidence;
* Notes are advisory and untrusted;
* no physical path or Unity Catalog target is inferred;
* mapping-ID uniqueness is derived from the returned IDs.

Do not promise:

* raw-content fallback;
* LLM inference;
* path inference;
* Unity Catalog inference;
* a separate uniqueness field;
* behavior absent from the actual public response.

Do not change version 0.3.144.

==================================================
13. FULL-SEAM TESTS

Use only:

* src/test/suite/sttmRepair12.test.ts
* src/test/suite/EtlReadOnlyToolService.test.ts

At least one Repair 12 test must cross the full actual production seam:

single Markdown file
→ production reader
→ production parser
→ canonical model
→ evidence provider
→ shared public projector
→ actual EtlReadOnlyToolService result
→ structured data
→ rendered Markdown.

It must not stop at the internal model, evidence provider, or renderer alone.

Use an existing deterministic sectioned-Markdown fixture or a test-owned input.
Do not edit the live QA STTM.

Positive assertions:

* exactly one requested file read;
* no sibling enumerated or opened;
* five sections recognized;
* six mappings in document order;
* six structured mapping IDs;
* ID uniqueness derived as 6/6;
* the same six IDs rendered in the final Mapping ID column;
* exactly two structured Notes;
* both Notes rendered with their original IDs and order;
* Notes labelled advisory;
* Source exactly raw.qa_hf1v2_customer;
* Target exactly curated.qa_hf1v2_customer;
* both literals present in structured and Markdown output;
* two exact filters unchanged;
* no obsolete filter fabricated;
* no raw/LLM fallback;
* no Unity Catalog, ABFSS, database, schema, table, or physical path fabricated;
* both public channels use the canonical projector;
* semantic output deterministic across repeated runs.

Required negative and edge coverage:

1. Missing Source:
    * Source absent;
    * actionable diagnostic;
    * no mapping-row fallback.
2. Missing Target:
    * Target absent;
    * actionable diagnostic;
    * no mapping.targetEntity fallback.
3. Conflicting Source values:
    * fail closed or explicit blocking ambiguity;
    * no value silently selected.
4. Conflicting Target values:
    * fail closed or explicit blocking ambiguity;
    * no value silently selected.
5. Duplicate identical Source or Target evidence:
    * existing duplicate-section policy retained;
    * diagnostic emitted where required.
6. Empty Notes:
    * no crash;
    * empty advisory collection;
    * no fabricated Note.
7. Notes absent:
    * new optional fields remain backward compatible;
    * no authored placeholder fabricated.
8. Special-character Notes:
    * structured response structure remains valid;
    * Markdown escaping is deterministic;
    * advisory data cannot become tool instructions or authority.
9. Missing, duplicate, non-ASCII, or long mapping IDs:
    * mappings remain an array;
    * no overwrite;
    * no synthetic replacement;
    * no invalid ID truncation.
10. Mapping ID column:
    * IDs preserved;
    * final column position verified;
    * no public mappingIdsUnique field.
11. Existing duplicate/ambiguous mapping-section behavior remains fail closed.
12. Workspace-root, traversal, symlink, and sibling isolation remain unchanged.
13. Malicious Note or section text cannot alter:
    * critical configuration;
    * source or target physical path;
    * Preview state;
    * approval state;
    * write authorization;
    * filesystem state.
14. Existing Excel and canonical Markdown-bundle behavior remains compatible.
15. package.json declaration matches the repaired public response.

Do not weaken, delete, skip, or rewrite an existing assertion to create a pass.

==================================================
14. POST-CHANGE DYNAMIC PROOF

After implementation and compilation, rerun the same real production seam probe
twice.

Required:

POST_INTERNAL_NOTES_COUNT: 2
POST_INTERNAL_SOURCE_LITERAL: raw.qa_hf1v2_customer
POST_INTERNAL_TARGET_LITERAL: curated.qa_hf1v2_customer
POST_INTERNAL_MAPPING_ID_COUNT: 6
POST_INTERNAL_MAPPING_IDS_UNIQUE: YES

POST_PUBLIC_STRUCTURED_NOTES_COUNT: 2
POST_PUBLIC_MARKDOWN_NOTES_COUNT: 2
POST_PUBLIC_SOURCE_LITERAL: raw.qa_hf1v2_customer
POST_PUBLIC_TARGET_LITERAL: curated.qa_hf1v2_customer
POST_PUBLIC_STRUCTURED_MAPPING_ID_COUNT: 6
POST_PUBLIC_MARKDOWN_MAPPING_ID_COUNT: 6
POST_MAPPING_ID_COLUMN_POSITION: LAST
POST_MAPPING_IDS_PRESERVED: YES
POST_MAPPING_IDS_UNIQUE_DERIVED: YES
POST_MAPPING_IDS_UNIQUE_FIELD_PRESENT: NO
POST_SIBLING_FILES_ENUMERATED: NO
POST_RAW_FALLBACK_USED: NO
POST_FABRICATED_VALUES: 0
POST_NOTES_MACHINE_AUTHORITY: NO
POST_PUBLIC_CHANNELS_SHARE_PROJECTOR: YES

Semantic output must be stable across both runs, except an explicitly documented
audit timestamp.

If contract-required evidence remains missing, stop:

REPAIR_12_IMPLEMENTATION_RESULT: FAIL_POSTCHANGE_PUBLIC_SEAM

==================================================
15. VALIDATION GATES

Use only installed local dependencies and existing repository infrastructure.

Do not download dependencies.
Do not create package-lock.json.
Do not change test registration or validation configuration to conceal failures.

Inspect existing canonical test patterns before selecting commands. A grep that
matches zero tests is not a pass.

Run and report exact command, exit code, pass/pending/fail counts, and complete
failure identities for:

1. TypeScript compile;
2. lint;
3. Repair 12 focused suite;
4. EtlReadOnlyToolService public-response suite;
5. Repair 11 focused suite;
6. Repair 11 Golden Path;
7. Repair 10 single-file Markdown regression;
8. STTM Markdown parser regression;
9. STTM resolved-evidence/reference/evidence-provider regressions;
10. workspace containment, traversal, symlink, and sibling-isolation security;
11. Repair 9;
12. Repair 8;
13. Repairs 5/6/7;
14. trusted Job Config envelope;
15. canonical full unit suite.

Required:

COMPILE_PASS: YES
LINT_PASS: YES
REPAIR_12_FOCUSED_PASS: YES
PUBLIC_ETL_INTERPRET_STTM_SEAM_PASS: YES
REPAIR_11_REGRESSION_PASS: YES
GOLDEN_PATH_PASS: YES
REPAIR_10_REGRESSION_PASS: YES
STTM_REGRESSION_PASS: YES
WORKSPACE_CONTAINMENT_PASS: YES
REPAIR_9_REGRESSION_PASS: YES
REPAIR_8_REGRESSION_PASS: YES
REPAIR_5_6_7_REGRESSION_PASS: YES
TRUSTED_ENVELOPE_PASS: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

Accepted pre-Repair-12 full-suite baseline:

2217 passing
1 pending
5 failing

Accepted failure identities:

* two EvalGating committed Phase-H baseline failures;
* maintainer delivery prompt references real repo-local agents;
* repository customization assets use valid frontmatter and agent naming;
* source tree uses standard AGENTS.md guidance instead of module AGENT.md files.

The final passing count must increase by exactly the number of newly registered
passing tests.

Pending count must not increase.
Failure count and exact identities must remain unchanged.

Do not call a failure historical merely because this prompt says so. Match each
identity against the actual accepted baseline evidence.

If a new functional/security failure appears or an accepted failure changes
identity, do not repair unrelated code:

REPAIR_12_IMPLEMENTATION_RESULT: FAIL_REGRESSION

==================================================
16. CHANGE-BOUNDARY VERIFICATION

Compare final state with the captured baseline using path, type, size, and
content hash.

Report separately:

* pre-existing tracked changes;
* pre-existing untracked files;
* Repair 12 production changes;
* Repair 12 tests;
* permitted package.json description-only edit;
* ignored compiled output;
* task-owned temporary artifacts;
* unexpected paths;
* staged paths.

Required:

AUTHORIZED_CHANGED_PATHS:
subset of the six declared paths

UNAUTHORIZED_CHANGED_PATHS:
NONE

PACKAGE_VERSION_BEFORE:
0.3.144

PACKAGE_VERSION_AFTER:
0.3.144

PACKAGE_VERSION_CHANGED:
NO

PACKAGE_LOCK_CREATED:
NO

EXISTING_0_3_144_VSIX_MODIFIED:
NO

STAGED_FILES:
0

Do not clean pre-existing or generated files.

If an unauthorized path changed:

REPAIR_12_IMPLEMENTATION_RESULT: FAIL_CHANGE_BOUNDARY

==================================================
17. STOP POINT

Stop after implementation, pre/post dynamic proof, validation gates, and
change-boundary verification.

Do not:

* perform the independent review in this session;
* bump to 0.3.145;
* build or modify a VSIX;
* install or uninstall an extension;
* reload the QA window;
* start Runtime QA;
* create a Preview;
* execute a write;
* commit, push, or tag.

The next step after PASS is a separate genuinely independent review.

==================================================
18. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
PROCESS_EXECUTION_PREFLIGHT: PASS/FAIL
SOURCE_VERSION_BEFORE: 
SOURCE_VERSION_AFTER: 
VERSION_CHANGED: YES/NO
STAGED_FILES_AT_START: 
STAGED_FILES_AT_END: 

QA_STTM_PATH: 
QA_STTM_SIZE_BYTES_BEFORE: 
QA_STTM_SIZE_BYTES_AFTER: 
QA_STTM_SHA256_BEFORE: 
QA_STTM_SHA256_AFTER: 
QA_STTM_UNCHANGED: YES/NO

PRECHANGE_PUBLIC_SEAM_REPRODUCED: YES/NO
PRE_INTERNAL_NOTES_COUNT: 
PRE_PUBLIC_STRUCTURED_NOTES_EXPOSED: YES/NO
PRE_PUBLIC_MARKDOWN_NOTES_EXPOSED: YES/NO
PRE_PUBLIC_SOURCE_LITERAL_EXPOSED: YES/NO
PRE_PUBLIC_TARGET_LITERAL_EXPOSED: YES/NO
PRE_PUBLIC_STRUCTURED_MAPPING_ID_COUNT: 
PRE_PUBLIC_MARKDOWN_MAPPING_ID_COUNT: 

SHARED_PUBLIC_PROJECTOR_SYMBOL: 
STRUCTURED_OUTPUT_USES_SHARED_PROJECTOR: YES/NO
MARKDOWN_OUTPUT_USES_SHARED_PROJECTOR: YES/NO
DUPLICATE_PROJECTION_LOGIC_PRESENT: YES/NO

AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 

TYPED_SOURCE_SECTION_EVIDENCE: YES/NO
TYPED_TARGET_SECTION_EVIDENCE: YES/NO
SOURCE_TARGET_EXACT_ONE_POLICY: YES/NO
SOURCE_TARGET_CONFLICT_FAIL_CLOSED: YES/NO

PUBLIC_STRUCTURED_NOTES_ADDED: YES/NO
PUBLIC_STRUCTURED_SECTION_EVIDENCE_ADDED: YES/NO
MARKDOWN_NOTES_RENDERED: YES/NO
MARKDOWN_SOURCE_TARGET_RENDERED: YES/NO
MARKDOWN_MAPPING_ID_COLUMN_ADDED: YES/NO
MARKDOWN_MAPPING_ID_COLUMN_POSITION: 
PACKAGE_MODEL_DESCRIPTION_ALIGNED: YES/NO

NOTES_REMAIN_ADVISORY: YES/NO
NOTES_TREATED_AS_MACHINE_AUTHORITY: YES/NO
NOTES_MARKDOWN_ESCAPING_DETERMINISTIC: YES/NO
NOTES_OUTPUT_BOUNDED: YES/NO
SPECIAL_CHARACTER_TESTS_PASS: YES/NO
EMPTY_NOTES_TEST_PASS: YES/NO

MISSING_SOURCE_TEST_PASS: YES/NO
MISSING_TARGET_TEST_PASS: YES/NO
CONFLICTING_SOURCE_TEST_PASS: YES/NO
CONFLICTING_TARGET_TEST_PASS: YES/NO
DUPLICATE_SECTION_POLICY_TEST_PASS: YES/NO

EXPLICIT_MAPPING_IDS_UNIQUE_FIELD_ADDED: NO
MAPPING_IDS_REGENERATED: NO
RAW_CONTENT_FALLBACK_ADDED: NO
FUZZY_INFERENCE_ADDED: NO
FABRICATED_IDENTIFIER_LOGIC_ADDED: NO
CONSUMER_CONTEXT_AUTHORITY_ADDED: NO

POSTCHANGE_PUBLIC_SEAM_PASS: YES/NO
POST_PUBLIC_STRUCTURED_NOTES_COUNT: 
POST_PUBLIC_MARKDOWN_NOTES_COUNT: 
POST_PUBLIC_SOURCE_LITERAL: 
POST_PUBLIC_TARGET_LITERAL: 
POST_PUBLIC_STRUCTURED_MAPPING_ID_COUNT: 
POST_PUBLIC_MARKDOWN_MAPPING_ID_COUNT: 
POST_MAPPING_ID_COLUMN_POSITION: 
POST_MAPPING_IDS_PRESERVED: YES/NO
POST_MAPPING_IDS_UNIQUE_DERIVED: YES/NO
POST_MAPPING_IDS_UNIQUE_FIELD_PRESENT: YES/NO
POST_SIBLING_FILES_ENUMERATED: YES/NO
POST_RAW_FALLBACK_USED: YES/NO
POST_FABRICATED_VALUES: 
POST_NOTES_MACHINE_AUTHORITY: YES/NO
POST_PUBLIC_CHANNELS_SHARE_PROJECTOR: YES/NO
POST_SEMANTIC_OUTPUT_DETERMINISTIC: YES/NO

COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_12_FOCUSED_PASS: YES/NO
REPAIR_12_FOCUSED_PASSING_COUNT: 
PUBLIC_ETL_INTERPRET_STTM_SEAM_PASS: YES/NO
GOLDEN_PATH_PASS: YES/NO
STTM_REGRESSION_PASS: YES/NO
WORKSPACE_CONTAINMENT_PASS: YES/NO
REPAIR_10_REGRESSION_PASS: YES/NO
REPAIR_11_REGRESSION_PASS: YES/NO
REPAIR_9_REGRESSION_PASS: YES/NO
REPAIR_8_REGRESSION_PASS: YES/NO
REPAIR_5_6_7_REGRESSION_PASS: YES/NO
TRUSTED_ENVELOPE_PASS: YES/NO
FULL_UNIT_PASSING_COUNT: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURES: 
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

PREEXISTING_OVERLAY_PRESERVED: YES/NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
EXISTING_0_3_144_VSIX_MODIFIED: NO
VSIX_BUILT: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
QA_WORKSPACE_MUTATED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
TEMP_ARTIFACTS: 

READY_FOR_INDEPENDENT_REVIEW: YES/NO
READY_TO_BUMP_VERSION: NO
READY_TO_PACKAGE: NO
READY_TO_INSTALL: NO
SAFE_TO_COMMIT: NO
SAFE_TO_RELEASE: NO

PASS requires:

* correct identity and working native process execution;
* dynamic pre-change public-seam reproduction;
* one shared typed public projector used by both output channels;
* exact-one, conflict-aware Source/Target evidence;
* advisory and safely rendered Notes;
* six existing mapping IDs preserved;
* Mapping ID appended as the last Markdown column;
* no new public uniqueness field;
* actual public etl_interpret_sttm seam covered;
* missing, duplicate, conflicting, empty, malicious, and special-character
    scenarios covered;
* all focused/security/regression gates pass;
* exactly the accepted five full-suite failures remain;
* zero new functional or security regressions;
* only authorized paths changed;
* source version remains 0.3.144;
* no package, install, Runtime QA, Preview, write, commit, push, or tag.

End exactly with one:

REPAIR_12_IMPLEMENTATION_RESULT: PASS_READY_FOR_INDEPENDENT_REVIEW
REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_IDENTITY
REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_STAGED_CHANGES
REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_EXECUTION_ENVIRONMENT
REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_CONCURRENT_MUTATION
REPAIR_12_IMPLEMENTATION_RESULT: BLOCKED_CHANGE_BOUNDARY
REPAIR_12_IMPLEMENTATION_RESULT: FAIL_PRECHANGE_REPRODUCTION
REPAIR_12_IMPLEMENTATION_RESULT: FAIL_POSTCHANGE_PUBLIC_SEAM
REPAIR_12_IMPLEMENTATION_RESULT: FAIL_FOCUSED_VALIDATION
REPAIR_12_IMPLEMENTATION_RESULT: FAIL_REGRESSION
REPAIR_12_IMPLEMENTATION_RESULT: FAIL_CHANGE_BOUNDARY
