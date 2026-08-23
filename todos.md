TASK: LOCAL_HOTFIX_HF1_V2_QA_CONTRACT_BLOCKER_REPAIR_8_SCOPE_DISCOVERY

This is a READ-ONLY source-of-truth discovery task.

Do NOT implement.
Do NOT edit files.
Do NOT regenerate contracts.
Do NOT change the extension version.
Do NOT package a VSIX.
Do NOT commit or push.

The goal is to determine the exact minimum repair required to unblock the
fresh-consumer CREATE_NEW_JOB preview flow discovered during runtime QA of
Databricks ETL Copilot 0.3.140.

==================================================
1. QA EVIDENCE TO RECONCILE
==================================================

Runtime QA independently established:

- Databricks ETL Copilot 0.3.140 was active.
- The workspace was a single disposable consumer workspace.
- Workflow customization was installed.
- No extension source or etl-framework-adb was available to the QA user.
- The synthetic STTM was discovered.
- The workspace was correctly classified as a fresh consumer.
- The runtime selected:

  TARGET_DECISION: CREATE_NEW_JOB

- Packaged framework fallback was successfully selected.
- No filesystem write occurred.
- No Preview ID was issued because deterministic validation failed first.

The two blocking validation findings were:

1. "No modules detected in job config"
2. "Confirm output path or table"

Read-only packaged-contract discovery then established:

TOP_LEVEL_MODULE_ENVELOPE_PROVEN: NO
TOP_LEVEL_MODULE_ENVELOPE_KEY: UNKNOWN
UNITY_CATALOG_TABLE_WRITE_SUPPORTED: UNKNOWN
UNITY_CATALOG_TARGET_FIELD: UNKNOWN
PATH_REQUIRED_FOR_DATAFRAME_WRITER: UNKNOWN
PRODUCT_DEFECT_FOUND: YES
PACKAGE_CONTRACT_GAP_FOUND: YES
QA_CAN_RESUME_WITHOUT_CODE_CHANGE: NO

Do not challenge these runtime facts without contrary live-source evidence.

==================================================
2. SOURCE REPOSITORY PREFLIGHT
==================================================

Work only in the current HF1 V2 extension source checkout.

Expected repository family:

TD-Universe/agentic_etl

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Independently verify:

- repository root
- branch
- HEAD
- origin
- staged count
- complete changed-path inventory
- current package version
- `.github/**` cleanliness
- Repair-5/6/7 candidate files remain present

The working tree contains extensive uncommitted HF1 work.

Do not reset, clean, stash, checkout, restore, or mutate anything.

If repository identity is not the expected HF1 V2 candidate, stop.

==================================================
3. FIND THE AUTHORITATIVE JOB-CONFIG ENVELOPE
==================================================

Trace the production runtime responsible for the error:

"No modules detected in job config"

Locate the exact:

- validator
- parser
- renderer
- module extractor
- job-config model/type
- HOCON handling
- validation error definition

Determine from executable production code:

1. the exact top-level Job Config module-envelope key;
2. the exact expected nesting shape;
3. whether modules are represented as:
   - a list,
   - an object,
   - a map,
   - named HOCON blocks,
   - or another structure;
4. the exact minimum valid Job Config HOCON document;
5. how the validator detects module types;
6. the required module ordering;
7. whether the current renderer produces that same shape.

Do not infer this from prose documentation when production code is available.

Return exact source paths, functions, and line ranges.

Classify the result:

- PROVEN_FROM_RUNTIME_CODE
- CONTRADICTORY_RUNTIME_CODE
- NOT_IMPLEMENTED

==================================================
4. RECONCILE ALL MODULE REPRESENTATIONS
==================================================

Inspect and compare all sources that currently describe modules:

- `etl_describe_module`
- `etl_get_framework_rules`
- packaged module reference assets
- packaged framework contracts
- packaged examples
- renderer inputs
- renderer output
- validators
- tests
- runtime types/interfaces
- repo-convention rules

The QA evidence found at least two conflicting representations:

A. named module HOCON block with a top-level `type`;
B. ordered JSON array entries using `options.module`,
   `target-path`, `target-format`, and `mode-of-write`.

Determine:

- which representation production runtime actually consumes;
- whether either representation is only a planning DTO rather than final HOCON;
- where conversion is supposed to occur;
- why the conversion did not occur during QA;
- whether Package examples are stale, wrong, or incomplete;
- whether `etl_describe_module` output is stale, wrong, or incomplete.

There must be one authoritative representation or one explicit transformation
pipeline. Do not propose parallel undocumented forms.

==================================================
5. DETERMINE THE REAL DATAFRAME_WRITER CONTRACT
==================================================

Trace the actual production/framework implementation of `dataframe_writer`.

Determine conclusively whether it supports:

A. ADLS/filesystem path output;
B. Delta path output;
C. Parquet/CSV/text path output;
D. JDBC/Synapse output;
E. Unity Catalog table by three-part name;
F. another registered-table abstraction.

For each supported destination mode return:

- exact config field names;
- exact required fields;
- exact optional fields;
- accepted HOCON shape;
- overwrite/append semantics;
- merge/upsert/CDC/SCD limitations;
- production implementation path;
- validator path;
- corresponding tests.

Specifically answer:

UNITY_CATALOG_TABLE_WRITE_SUPPORTED: YES/NO
UNITY_CATALOG_TARGET_FIELD: <exact field or NONE>
PATH_REQUIRED_FOR_DATAFRAME_WRITER: YES/NO

Do not add Unity Catalog support merely because the QA STTM used a table name.

If direct Unity Catalog table output is not supported, identify the correct
existing writer/module for that destination, or conclude that the QA fixture
must use a supported path-based synthetic destination.

==================================================
6. READ-ONLY FRAMEWORK SOURCE RECONCILIATION
==================================================

If an existing local `etl-framework-adb` checkout is available to the maintainer,
it may be inspected READ ONLY as authoritative implementation evidence.

It must NOT be:

- modified;
- added to the QA workspace;
- packaged;
- required by the end user;
- used as a runtime fallback in the final fix.

Compare the live framework implementation with the packaged extension contract.

Report every contract field that must be copied/generated into the VSIX so the
installed extension is self-contained.

If no framework checkout is available, do not fabricate the missing contract.

==================================================
7. TRACE PACKAGED FALLBACK DEFECTS
==================================================

Investigate the confirmed defects:

A. `criticalConfigKeys` missing from `etl_get_framework_rules`

QA observed:

- the packaged machine-readable framework contract contains populated
  `criticalConfigKeys`;
- `etl_get_framework_rules` returns
  "Critical config keys: not available".

Locate the exact data-loss point.

B. `etl_search_examples` ignores packaged examples

QA observed:

- indexed approved examples exist inside packaged knowledge assets;
- `etl_search_examples` returns `no_search_roots_available`;
- the packaged examples are never consulted.

Locate the exact discovery/search-root defect.

C. packaged self-inconsistency

Locate why:

- module reference output;
- packaged examples;
- renderer;
- validator;

do not use one consistent model.

D. deployed context divergence

Determine why the installed workspace context file is a small prose stub while
other packaged assets contain richer and conflicting contracts.

Do not solve this by copying arbitrary user-editable context into a trusted
contract path.

Record the existing deferred finding:

CONTEXT_OWNERSHIP_AND_TRUST_BOUNDARY

==================================================
8. STTM FIXTURE/PARSER CLASSIFICATION
==================================================

QA also observed:

- the markdown STTM was found;
- native structured parsing recognized zero mappings;
- it returned `STTM_SHEET_UNRECOGNIZED` / `missing_sheet: fieldMapping`;
- the Orchestrator then read the raw markdown content manually.

Determine whether:

A. Markdown STTM is an officially supported input format;
B. the QA fixture is simply the wrong format/template;
C. the parser is expected to support this template but has a defect.

Do not automatically include STTM parser changes in Repair 8.

If the fixture is invalid, specify the exact supported synthetic format to use
for the next QA run, such as a sanitized XLSX workbook with required sheets and
columns.

Classify:

STTM_QA_FIXTURE_VALID: YES/NO/UNKNOWN
STTM_PARSER_REPAIR_REQUIRED: YES/NO/UNKNOWN

==================================================
9. DEFINE THE SINGLE SOURCE OF TRUTH
==================================================

Based on production implementation, recommend the smallest design that ensures:

- one machine-readable canonical Job Config contract;
- exact module-envelope key and shape;
- exact module fields;
- exact writer destination modes;
- exact critical config keys;
- examples validated against the same contract;
- renderer output validated against the same contract;
- installed extension fallback remains self-contained;
- no framework source is required by QA/end users;
- no user-editable context file becomes the authority for executable config.

Do not redesign the entire ETL product.

Prefer extracting/packaging existing authoritative implementation facts over
inventing a new schema.

==================================================
10. MINIMUM REPAIR INVENTORY
==================================================

Produce the exact minimum file inventory for a bounded Repair 8.

For each required file state:

- exact path;
- production/test/package/config;
- exact function/type/section;
- reason the change is necessary;
- whether it already has HF1 candidate changes;
- whether a new file is required.

Expected repair areas may include, but must be proven rather than assumed:

- canonical Job Config contract/schema;
- packaged framework-contract generation;
- `etl_get_framework_rules` fallback;
- `etl_describe_module`;
- `etl_search_examples`;
- renderer contract consumption;
- validator/renderer alignment;
- package-content tests;
- fresh-consumer preview regression tests.

Do not include files merely because they are adjacent.

Do not include `etl-framework-adb` as a modified file.

==================================================
11. REQUIRED TEST PLAN
==================================================

Define tests proving:

1. a fresh consumer with no local job/env examples can produce a valid preview;
2. the renderer emits the exact production module envelope;
3. the validator recognizes every rendered module;
4. the packaged fallback surfaces `criticalConfigKeys`;
5. packaged examples are searchable without local search roots;
6. examples, module descriptions, renderer, and validator agree;
7. supported writer destination modes are explicit and validated;
8. unsupported Unity Catalog table-by-name output is rejected clearly, if it is
   not supported;
9. a supported destination produces a Preview ID;
10. preview remains zero-write;
11. framework source is not required;
12. the existing Repair-5/6/7 security behavior is unchanged;
13. package verification remains clean.

Include mutation/negative tests where useful to prevent false-green results.

==================================================
12. VERSIONING DECISION
==================================================

Do not change the version during this discovery.

Because runtime behavior and/or packaged contract content must change, state
whether the next QA package must become:

0.3.141

The expected answer is YES unless discovery proves no product/package byte
change is necessary.

Do not build that package in this task.

==================================================
13. FINAL REPORT
==================================================

Return:

1. Repository identity.
2. Exact validator source for "No modules detected in job config".
3. Exact validator source for "Confirm output path or table".
4. Canonical Job Config envelope key and shape.
5. Minimal valid Job Config HOCON example.
6. Canonical module representation.
7. Actual `dataframe_writer` destination contract.
8. Unity Catalog table-name support verdict.
9. `criticalConfigKeys` fallback root cause.
10. Packaged-example search root cause.
11. Package self-inconsistency root cause.
12. STTM fixture/parser classification.
13. Minimum Repair-8 file inventory.
14. Required tests.
15. No-touch proof.
16. Versioning recommendation.

Finish exactly with:

CANONICAL_JOB_CONFIG_ENVELOPE_PROVEN: YES/NO
CANONICAL_MODULE_REPRESENTATION_PROVEN: YES/NO
DATAFRAME_WRITER_CONTRACT_PROVEN: YES/NO
UNITY_CATALOG_TABLE_WRITE_SUPPORTED: YES/NO/UNKNOWN
CRITICAL_CONFIG_KEYS_FALLBACK_DEFECT_CONFIRMED: YES/NO
PACKAGED_EXAMPLE_SEARCH_DEFECT_CONFIRMED: YES/NO
PACKAGE_SELF_CONSISTENCY_DEFECT_CONFIRMED: YES/NO
STTM_QA_FIXTURE_VALID: YES/NO/UNKNOWN
STTM_PARSER_REPAIR_REQUIRED: YES/NO/UNKNOWN
PRODUCT_CODE_CHANGE_REQUIRED: YES/NO
PACKAGE_CONTRACT_CHANGE_REQUIRED: YES/NO
NEXT_QA_VERSION_MUST_BE_0_3_141: YES/NO
REPAIR_8_SCOPE_FROZEN: YES/NO

End exactly:

LOCAL_HOTFIX_HF1_V2_QA_CONTRACT_BLOCKER_REPAIR_8_SCOPE_DISCOVERY_COMPLETE
