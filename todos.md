TASK: LOCAL_HOTFIX_HF1_V2_QA_CONTRACT_BLOCKER_REPAIR_8_SCOPE_AMENDMENT_1

This is a READ-ONLY scope-completion task in the SOFTWARE DEVELOPMENT ENVIRONMENT.

Do NOT implement.
Do NOT edit any file.
Do NOT change version.
Do NOT build a VSIX.
Do NOT regenerate baselines.
Do NOT commit or push.
Do NOT modify etl-framework-adb.

The previous Repair-8 discovery is accepted as authoritative.

Do not re-litigate the following proven facts:

CANONICAL_JOB_CONFIG_ENVELOPE_PROVEN: YES
CANONICAL_MODULE_REPRESENTATION_PROVEN: YES
DATAFRAME_WRITER_CONTRACT_PROVEN: YES
UNITY_CATALOG_TABLE_WRITE_SUPPORTED: NO
CRITICAL_CONFIG_KEYS_FALLBACK_DEFECT_CONFIRMED: YES
PACKAGED_EXAMPLE_SEARCH_DEFECT_CONFIRMED: YES
PACKAGE_SELF_CONSISTENCY_DEFECT_CONFIRMED: YES
STTM_PARSER_REPAIR_REQUIRED: NO
PRODUCT_CODE_CHANGE_REQUIRED: YES
PACKAGE_CONTRACT_CHANGE_REQUIRED: YES
NEXT_QA_VERSION_MUST_BE_0_3_141: YES

The canonical executable Job Config form is:

modules {
  <stage_key> {
    ...
    options {
      module = <module_type>
      method = process
    }
  }
}

The purpose of this task is only to close the remaining scope gaps before
Repair-8 implementation.

==================================================
1. VERIFY SOFTWARE DEVELOPMENT ENVIRONMENT
==================================================

Expected root:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected base HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected current version:

0.3.140

Verify repository identity through read-only evidence.

Do not reset, clean, restore, checkout, stash, or mutate the working tree.

==================================================
2. ACCEPTED INITIAL REPAIR-8 FILE INVENTORY
==================================================

The previous discovery proposed these files.

New:

1. resources/framework/contracts/job-config-envelope.v1.json

2. src/core/framework/TrustedJobConfigEnvelopeResolver.ts

Modified:

3. src/tools/EtlReadOnlyToolService.ts

4. resources/copilot/context/etl-module-reference.md

5. resources/copilot/knowledge/examples/dataframe-writer-export.example.json

6. resources/copilot/knowledge/framework-contracts/etl-framework-2.latest.json

7. src/renderers/JobConfigRenderer.ts

8. src/test/verifyVsixContents.ts

Treat this as the initial proposed scope, not automatically complete.

==================================================
3. PROVE THE FRESH-CONSUMER INTEGRATION SEAM
==================================================

Trace the complete shipping-runtime call path used in the development test
workspace:

ETL Orchestrator
→ registered ETL tools
→ framework-rule retrieval
→ job-config drafting/rendering
→ deterministic validation
→ trusted preview creation

Answer conclusively:

A. How will the new TrustedJobConfigEnvelopeResolver be consumed by the actual
fresh-consumer CREATE_NEW_JOB path?

B. Is changing EtlReadOnlyToolService plus packaged guidance sufficient to make
the active agentic path consume the canonical contract?

C. Does EtlActionToolService.renderJobConfig() require a code change?

D. Does ArtifactGenerationPipeline require a code change?

E. Does JobConfigRenderer need to become the actual deterministic rendering
boundary for the agentic path, or is it only required as the canonical example
renderer?

F. Are ModuleSequenceExtractor, FrameworkParseValidator, or
ReadinessProfileCatalog production changes required, or are their current
strict checks correct and only new tests are needed?

For every answer provide:

- exact source path;
- function or class;
- call-path evidence;
- CHANGE_REQUIRED or NO_CHANGE_REQUIRED;
- reason.

Do not add a file to scope merely because it is adjacent.

Do not rely on model compliance alone if a deterministic integration point is
already intended by the architecture.

==================================================
4. EXACT TEST-FILE INVENTORY
==================================================

The previous discovery defined 13 required proofs but did not name the exact
test files.

Locate the smallest existing test homes for every proof:

1. canonical envelope contract loads, validates, and fingerprints;
2. contract fails closed on invalid fields/version/secret scan;
3. resolver precedence and installed-resource ancestor resolution;
4. canonical examples yield at least one module;
5. quoted-JSON and array forms yield zero modules;
6. FrameworkParseValidator accepts canonical fresh-consumer config;
7. artifact evidence extracts a canonical dataframe_writer target;
8. generic_dataframe_write readiness accepts the supported target;
9. fallback surfaces non-empty criticalConfigKeys;
10. packaged examples are searchable without local workspace examples;
11. every shipped example/context conforms to the canonical form;
12. fresh-consumer CREATE_NEW_JOB reaches a real Preview ID with zero writes;
13. verifyVsixContents proves both trusted contracts ship in the VSIX.

Return the exact test path for every proof.

Prefer extending existing suites.

A new test file is allowed only when no existing suite can exercise the real
integration path without becoming misleading.

For every test file return:

- exact path;
- existing or new;
- proofs covered;
- whether it already contains HF1 candidate changes;
- whether real production code or only source text is exercised.

Do not use source-text-only assertions for behavioral proofs.

==================================================
5. POSITIVE AND NEGATIVE DESTINATION FIXTURES
==================================================

The current development-test STTM used:

curated.qa_hf1v2_customer

as a Unity Catalog table-by-name target.

The framework implementation proves this is unsupported by dataframe_writer.

Define two separate QA cases:

A. Positive supported case

Specify the exact synthetic path-based destination shape that can produce a
valid preview without requiring real credentials or real storage access.

Return:

- target path format;
- target format;
- write mode;
- required dataframe_writer fields;
- whether only planning/preview is possible without storage connectivity;
- exact sanitized STTM/fixture update required.

B. Negative unsupported case

Retain a Unity Catalog table-name target as a deterministic negative test.

Expected outcome must be a clear unsupported-destination error, not:

"No modules detected in job config"

and not an ambiguous:

"Confirm output path or table"

Do not add Unity Catalog support in Repair 8.

Determine whether the positive/negative fixture belongs in:

- an existing test file;
- a new test fixture;
- the disposable DEVELOPMENT_TEST_WORKSPACE only;
- or a packaged approved example.

Name the exact file if repository mutation is required.

==================================================
6. CONTEXT TRUST BOUNDARY
==================================================

Keep this deferred and out of Repair 8:

CONTEXT_OWNERSHIP_AND_TRUST_BOUNDARY

Confirm Repair 8 will not make:

resources/copilot/context/**

the machine-authoritative executable contract.

The authority must remain an extension-owned, integrity-validated contract
under:

resources/framework/contracts/**

The prose context may reference the trusted contract but must not override it.

==================================================
7. VERSIONING AND PACKAGING SEPARATION
==================================================

Confirm the recommended sequence:

1. implement Repair 8 while source version remains 0.3.140;
2. run compile/lint/focused/full tests;
3. independently re-audit Repair 8;
4. perform a separate version bump to 0.3.141;
5. build and verify one clean 0.3.141 VSIX;
6. return to the DEVELOPMENT_TEST_WORKSPACE for runtime QA.

Do not change version or package during this scope task.

==================================================
8. FINAL FROZEN FILE INVENTORY
==================================================

Return one exact deduplicated inventory grouped as:

NEW_PRODUCTION_OR_CONTRACT_FILES
MODIFIED_PRODUCTION_FILES
MODIFIED_PACKAGED_GUIDANCE_FILES
MODIFIED_TEST_FILES
NEW_TEST_FILES
PACKAGE_POLICY_OR_VERIFIER_FILES
VERSION_FILES_DEFERRED_TO_LATER
EXPLICITLY_NO_CHANGE_FILES

For every file include:

- exact path;
- reason;
- specific function/section;
- proof/test mapped to it.

The list must include every file needed to implement and test Repair 8.

No implementation authorization will include unnamed files.

==================================================
9. FINAL MARKERS
==================================================

Finish with:

INITIAL_8_FILE_SCOPE_COMPLETE: YES|NO
FRESH_CONSUMER_INTEGRATION_PATH_PROVEN: YES|NO
ETL_ACTION_TOOL_SERVICE_CHANGE_REQUIRED: YES|NO
ARTIFACT_GENERATION_PIPELINE_CHANGE_REQUIRED: YES|NO
JOB_CONFIG_RENDERER_RUNTIME_INTEGRATION_REQUIRED: YES|NO
VALIDATOR_PRODUCTION_CHANGE_REQUIRED: YES|NO
READINESS_PROFILE_PRODUCTION_CHANGE_REQUIRED: YES|NO
EXACT_TEST_FILE_INVENTORY_PROVEN: YES|NO
POSITIVE_PATH_BASED_QA_FIXTURE_PROVEN: YES|NO
UNITY_CATALOG_NEGATIVE_TEST_DEFINED: YES|NO
CONTEXT_TRUST_BOUNDARY_REMAINS_DEFERRED: YES|NO
REPAIR_8_IMPLEMENTATION_FILE_COUNT: <number>
REPAIR_8_TEST_FILE_COUNT: <number>
REPAIR_8_NEW_FILE_COUNT: <number>
NEXT_QA_VERSION_REMAINS_0_3_141: YES|NO
REPAIR_8_SCOPE_AMENDMENT_FROZEN: YES|NO

End exactly:

LOCAL_HOTFIX_HF1_V2_QA_CONTRACT_BLOCKER_REPAIR_8_SCOPE_AMENDMENT_1_COMPLETE
