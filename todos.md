TASK: LOCAL_HOTFIX_HF1_V2_QA_CONTRACT_BLOCKER_REPAIR_8_IMPLEMENTATION

Implement the frozen Repair-8 scope in the SOFTWARE DEVELOPMENT ENVIRONMENT.

This is a bounded source-code implementation and local-validation task.

Do NOT perform further architecture discovery unless a direct contradiction is
found in one of the authorized files.

Do NOT change the extension version.
Do NOT build or install a VSIX.
Do NOT regenerate Phase-H baselines.
Do NOT commit or push.
Do NOT modify etl-framework-adb.
Do NOT modify a development test workspace or any consumer repository.
Do NOT install or download dependencies.
Use only the already-installed dependencies.

==================================================
1. ACCEPTED AUTHORITATIVE DISCOVERY
==================================================

The previous discovery and scope amendment are accepted.

Do not re-litigate these facts:

CANONICAL_JOB_CONFIG_ENVELOPE_PROVEN: YES
CANONICAL_MODULE_REPRESENTATION_PROVEN: YES
DATAFRAME_WRITER_CONTRACT_PROVEN: YES
UNITY_CATALOG_TABLE_WRITE_SUPPORTED: NO
CRITICAL_CONFIG_KEYS_FALLBACK_DEFECT_CONFIRMED: YES
PACKAGED_EXAMPLE_SEARCH_DEFECT_CONFIRMED: YES
PACKAGE_SELF_CONSISTENCY_DEFECT_CONFIRMED: YES
STTM_PARSER_REPAIR_REQUIRED: NO
FRESH_CONSUMER_INTEGRATION_PATH_PROVEN: YES
ETL_ACTION_TOOL_SERVICE_CHANGE_REQUIRED: NO
ARTIFACT_GENERATION_PIPELINE_CHANGE_REQUIRED: NO
JOB_CONFIG_RENDERER_RUNTIME_INTEGRATION_REQUIRED: NO
VALIDATOR_PRODUCTION_CHANGE_REQUIRED: YES
READINESS_PROFILE_PRODUCTION_CHANGE_REQUIRED: YES
EXACT_TEST_FILE_INVENTORY_PROVEN: YES
POSITIVE_PATH_BASED_QA_FIXTURE_PROVEN: YES
UNITY_CATALOG_NEGATIVE_TEST_DEFINED: YES
CONTEXT_TRUST_BOUNDARY_REMAINS_DEFERRED: YES
NEXT_QA_VERSION_REMAINS_0_3_141: YES
REPAIR_8_SCOPE_AMENDMENT_FROZEN: YES

Canonical executable HOCON shape:

modules {
  <stage_key> {
    ...
    options {
      module = <module_type>
      method = process
    }
  }
}

The `modules` value is an object keyed by stage name.

The following representations are non-canonical:

- top-level module blocks without `modules { ... }`;
- modules represented as a JSON array;
- quoted-JSON `"modules"` syntax;
- module entries without `options.module`;
- packaged planning DTOs used directly as final HOCON.

The current `dataframe_writer` does NOT support a Unity Catalog table by
three-part table name.

Its supported output contract is path-based, with JDBC/Synapse variants where
explicitly documented by executable framework evidence.

Do not add Unity Catalog support in Repair 8.

==================================================
2. SOFTWARE DEVELOPMENT ENVIRONMENT PREFLIGHT
==================================================

Expected root:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected base HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected current version:

0.3.140

Expected publisher:

td-etl

Verify all values before editing.

The working tree already contains accepted Repair-5, Repair-6, and Repair-7
changes.

Do not reset, clean, restore, checkout, stash, rebase, or otherwise alter those
accepted bytes.

Capture before-edit hashes for all 21 authorized files that already exist.

Capture the initial changed-path inventory and staged-file count.

If repository identity does not match, stop without editing.

==================================================
3. EXACT FROZEN AUTHORIZED FILE SET
==================================================

Only the following 21 paths are authorized.

------------------------------
NEW PRODUCTION/CONTRACT FILES
------------------------------

1. src/core/framework/TrustedJobConfigEnvelopeResolver.ts

2. resources/framework/contracts/job-config-envelope.v1.json

------------------------------
MODIFIED PRODUCTION FILES
------------------------------

3. src/core/trusted/FirstRenderInvariantGuard.ts

4. src/core/trusted/index.ts

5. src/core/utils/ModuleSequenceExtractor.ts

6. src/core/framework/FrameworkDiscoveryService.ts

7. src/tools/EtlReadOnlyToolService.ts

8. src/core/readiness/ReadinessProfileCatalog.ts

9. src/core/readiness/JobDevelopmentReadinessEvaluator.ts

------------------------------
MODIFIED PACKAGED GUIDANCE
------------------------------

10. resources/copilot/context/etl-module-reference.md

11. resources/copilot/knowledge/examples/dataframe-writer-export.example.json

12. resources/copilot/knowledge/examples/curated-load-enrich.example.json

------------------------------
PACKAGE VERIFIER
------------------------------

13. src/test/verifyVsixContents.ts

------------------------------
MODIFIED TEST FILES
------------------------------

14. src/test/suite/configExplain.test.ts

15. src/test/suite/firstRenderInvariantGuard.test.ts

16. src/test/suite/EtlReadOnlyToolService.test.ts

17. src/test/suite/jobDevelopmentReadiness.test.ts

18. src/test/suite/packageAssets.test.ts

19. src/test/suite/etlActionTools.test.ts

20. src/test/suite/hf1OracleFreshConsumer.test.ts

------------------------------
NEW TEST FILE
------------------------------

21. src/test/suite/trustedJobConfigEnvelope.test.ts

No other file may be created, modified, deleted, renamed, reformatted, or
regenerated.

If another file is genuinely required, stop before editing it and return:

REPAIR_8_SCOPE_AMENDMENT_REQUIRED

Name the exact additional path and explain why none of the 21 authorized files
can satisfy the requirement.

==================================================
4. EXPLICITLY NO-CHANGE FILES
==================================================

Do not modify:

- src/tools/EtlActionToolService.ts
- src/core/session/ArtifactGenerationPipeline.ts
- src/renderers/JobConfigRenderer.ts
- src/core/validate/FrameworkParseValidator.ts
- src/core/sttm/SttmMarkdownBundleParser.ts
- .vscodeignore
- resources/copilot/skills/etl-create-job/SKILL.md
- package.json
- package-lock.json
- resources/prompts/**
- .github/**
- AGENT.md
- AGENTS.md

Reasons already proven:

- EtlActionToolService already invokes FirstRenderInvariantGuard.
- ArtifactGenerationPipeline already uses JobConfigRenderer.
- JobConfigRenderer is already the canonical deterministic renderer.
- FrameworkParseValidator's strict zero-module check is correct.
- The STTM parser did not cause the two runtime blockers.
- `.vscodeignore` already re-includes `resources/framework/**`.
- The create-job skill does not define the module envelope and must not become
  another authority.
- Version bump is a later independent task.

==================================================
5. TRUSTED JOB-CONFIG CONTRACT
==================================================

Create:

resources/framework/contracts/job-config-envelope.v1.json

The contract must be:

- extension-owned;
- machine-readable;
- strictly allow-listed;
- versioned;
- integrity-validated;
- deterministic to fingerprint;
- free of credentials, secrets, hostnames, developer paths, URLs, or consumer
  business values;
- derived from executable framework evidence, not invented prose.

It must encode at minimum:

- canonical `modules` object envelope;
- stage-keyed module entries;
- `options.module`;
- `options.method`;
- supported module types;
- required and optional fields by module type;
- required module ordering where applicable;
- supported dataframe_writer destination modes;
- path-based dataframe_writer requirements;
- unsupported Unity Catalog table-by-name semantics;
- critical config keys needed by fresh-consumer planning.

Use the same integrity and fail-closed principles already used by the trusted
Oracle delivery-control contract.

Do not merge the Oracle contract and the Job Config envelope contract into one
unrelated schema.

==================================================
6. TRUSTED RESOLVER
==================================================

Create:

src/core/framework/TrustedJobConfigEnvelopeResolver.ts

Implement it according to the frozen design:

- reuse the proven validation, whitelist, integrity, fingerprint, and installed
  resource-resolution pattern from TrustedFrameworkDefinitionResolver;
- resolve the installed packaged contract without depending on a framework
  checkout;
- use `__dirname`/installed-resource ancestor resolution before any development
  fallback;
- do not depend on `process.cwd()` for normal installed operation;
- fail closed on malformed JSON;
- fail closed on unknown fields;
- fail closed on unsupported schema/contract version;
- fail closed when secret/content scanning has not passed;
- return immutable/cloned resolution objects so caller mutation cannot corrupt
  cached authority;
- provide deterministic fingerprints;
- never treat `resources/copilot/context/**` as the authoritative contract;
- never allow consumer-editable context to override the trusted contract.

Export it through:

src/core/trusted/index.ts

Do not create a second authorization or approval subsystem.

==================================================
7. FIRST-RENDER DETERMINISTIC ENFORCEMENT
==================================================

Modify:

src/core/trusted/FirstRenderInvariantGuard.ts

Use TrustedJobConfigEnvelopeResolver inside the existing deterministic guard
path already called by EtlActionToolService.

Do not modify EtlActionToolService itself.

Add deterministic invariant handling for:

NON_CANONICAL_JOB_CONFIG_ENVELOPE

and:

UNSUPPORTED_UNITY_CATALOG_TARGET

Required behavior:

A. Non-canonical envelope

- reject missing `modules { ... }`;
- reject JSON-array modules;
- reject quoted-JSON job config;
- reject missing `options.module`;
- reject a module shape inconsistent with the trusted contract;
- provide a clear, actionable diagnostic;
- perform no write;
- do not mint a trusted Preview ID.

B. Unsupported Unity Catalog target

For a dataframe_writer module whose destination is a catalog-qualified table
name with no supported path/JDBC/Synapse destination:

- retain successful module detection;
- return `UNSUPPORTED_UNITY_CATALOG_TARGET`;
- do not return `No modules detected in job config`;
- do not return only the ambiguous `Confirm output path or table`;
- perform no write;
- do not mint a trusted Preview ID.

Do not duplicate rendering or parsing logic inside the guard.

==================================================
8. MODULE SEQUENCE EXTRACTION
==================================================

Modify:

src/core/utils/ModuleSequenceExtractor.ts

Support the HOCON forms proven by real framework configs:

- colon separator;
- equals separator;
- separator omitted before an opening `{` where legal HOCON permits it.

Examples of accepted concepts:

modules {
  stage_name {
    options {
      module = dataframe_writer
      method = process
    }
  }
}

and equivalent colon/equals HOCON variants.

Preserve strict rejection of:

- JSON array module forms;
- quoted-JSON `"modules"` forms;
- malformed strings;
- missing module types.

Do not weaken FrameworkParseValidator.

Its existing:

"No modules detected in job config"

check must remain strict and unchanged.

==================================================
9. PACKAGED FALLBACK AND EXAMPLE SEARCH
==================================================

Modify:

src/core/framework/FrameworkDiscoveryService.ts

Replace the hard-coded empty fresh-consumer `criticalConfigKeys` fallback with
the trusted packaged Job Config contract.

Modify:

src/tools/EtlReadOnlyToolService.ts

Required results:

- `etl_get_framework_rules` returns non-empty, contract-backed
  `criticalConfigKeys` when no framework workspace is present;
- packaged-contract fallback is identified clearly;
- `etl_search_examples` searches approved packaged examples even when there are
  no local workspace example roots;
- fresh consumers must not receive `no_search_roots_available` while approved
  packaged examples exist;
- local examples and packaged examples have explicit, deterministic precedence;
- no framework checkout is required;
- no arbitrary consumer context becomes trusted authority.

Do not make the LLM guidance path the sole enforcement mechanism.

==================================================
10. READINESS DIAGNOSTICS
==================================================

Modify:

src/core/readiness/ReadinessProfileCatalog.ts

Add the distinct generic_dataframe_write blocker code and message for an
unsupported Unity Catalog table-by-name target.

Use the established readiness-code naming convention, including:

unsupported_unity_catalog_target

Modify:

src/core/readiness/JobDevelopmentReadinessEvaluator.ts

Ensure that a catalog-qualified table target without a supported writer
destination does not silently satisfy `path_or_table`.

Required outcome:

- canonical module is still detected;
- unsupported Unity Catalog destination is rejected explicitly;
- no generic missing-target diagnostic replaces the specific result;
- supported path-based dataframe_writer destinations continue to pass;
- no Unity Catalog writer capability is added.

==================================================
11. PACKAGED GUIDANCE CONSISTENCY
==================================================

Modify:

resources/copilot/context/etl-module-reference.md

Replace non-canonical top-level `type` examples with canonical:

modules {
  <stage_key> {
    ...
    options {
      module = <module_type>
      method = process
    }
  }
}

The prose file remains advisory only.

It must explicitly state that executable authority comes from:

resources/framework/contracts/job-config-envelope.v1.json

Modify:

resources/copilot/knowledge/examples/dataframe-writer-export.example.json

Replace the array/flattened planning representation with a canonical envelope
representation compatible with the actual renderer and validator.

Use only a supported path-based destination.

Modify:

resources/copilot/knowledge/examples/curated-load-enrich.example.json

Apply the same canonical representation.

Do not claim direct Unity Catalog table-name write support.

All shipped examples must agree with:

- the trusted contract;
- ModuleSequenceExtractor;
- FirstRenderInvariantGuard;
- FrameworkParseValidator;
- readiness evaluation;
- JobConfigRenderer output.

==================================================
12. POSITIVE DEVELOPMENT QA FIXTURE
==================================================

In:

src/test/suite/hf1OracleFreshConsumer.test.ts

Use an inline, sanitized path-based QA mapping.

Do not create a repository fixture file.

Use the proven supported shape:

- target path based on the existing synthetic `adl.destination.root`;
- sanitized relative target such as `curated/qa_hf1v2_customer`;
- target format: delta;
- write mode: append;
- dataframe_writer module;
- method: process;
- required path/format/mode fields;
- canonical modules envelope.

No real storage credentials or real data access may be required.

The test is planning/validation/preview-only and must prove:

- CREATE_NEW_JOB;
- a real Preview ID is issued;
- preview produces zero filesystem writes;
- no framework checkout is required;
- no consumer repository outside the test fixture is touched.

==================================================
13. NEGATIVE UNITY CATALOG TEST
==================================================

Use a canonical dataframe_writer module whose destination is a table name such
as:

curated.qa_hf1v2_customer

with no supported path destination.

Required result:

- module detection succeeds;
- FirstRenderInvariantGuard returns
  `UNSUPPORTED_UNITY_CATALOG_TARGET`;
- readiness returns `unsupported_unity_catalog_target`;
- no Preview ID is issued;
- no write occurs;
- no Unity Catalog support is added;
- the error is not reduced to `No modules detected in job config`;
- the error is not only `Confirm output path or table`.

Place the tests only in the already-authorized existing suites.

==================================================
14. PACKAGE VERIFIER
==================================================

Modify:

src/test/verifyVsixContents.ts

Require the packaged VSIX to contain both trusted framework contracts:

- resources/framework/contracts/oracle-delivery-controls.v1.json
- resources/framework/contracts/job-config-envelope.v1.json

Do not weaken any existing:

- required-entry checks;
- forbidden-content checks;
- size ceilings;
- manifest checks;
- content-marker checks;
- machine-path scans;
- package provenance checks.

This task does not build a VSIX, but verifier source and tests must compile.

==================================================
15. REQUIRED TEST IMPLEMENTATION
==================================================

Create:

src/test/suite/trustedJobConfigEnvelope.test.ts

Cover:

- valid contract loading;
- deterministic fingerprint;
- strict field whitelist;
- bad schema/contract version;
- invalid contract identity;
- secret-scan status failure;
- malformed JSON;
- installed-resource ancestor resolution;
- cache stability;
- returned-object mutation isolation.

Modify:

src/test/suite/configExplain.test.ts

Cover ModuleSequenceExtractor for:

- canonical colon HOCON;
- canonical equals HOCON;
- legal omitted-before-`{` HOCON;
- quoted JSON rejected;
- array representation rejected;
- malformed/missing module rejected.

Modify:

src/test/suite/firstRenderInvariantGuard.test.ts

Cover:

- canonical Job Config accepted;
- non-canonical envelope rejected;
- dataframe_writer contract fields;
- unsupported Unity Catalog target rejected;
- supported path-based target accepted;
- Repair-5/6/7 guard behavior unchanged.

Modify:

src/test/suite/EtlReadOnlyToolService.test.ts

Cover:

- non-empty criticalConfigKeys from packaged fallback;
- packaged examples searchable with zero local roots;
- deterministic precedence;
- no `no_search_roots_available` when packaged examples exist;
- current STTM behavior remains regression-only and unchanged.

Modify:

src/test/suite/jobDevelopmentReadiness.test.ts

Cover:

- supported path destination passes;
- Unity Catalog table-by-name yields
  `unsupported_unity_catalog_target`;
- no silent `path_or_table` success;
- no ambiguous generic message replaces the explicit blocker.

Modify:

src/test/suite/packageAssets.test.ts

Cover:

- both trusted contract files exist;
- both packaged examples conform to the canonical envelope;
- advisory context agrees with the trusted contract;
- package self-consistency;
- no version expectation is changed yet;
- source/package authority cannot silently drift.

Modify:

src/test/suite/etlActionTools.test.ts

Without modifying EtlActionToolService production code, prove its existing guard
path:

- blocks NON_CANONICAL_JOB_CONFIG_ENVELOPE;
- blocks UNSUPPORTED_UNITY_CATALOG_TARGET;
- produces no Preview ID;
- produces zero writes;
- allows a canonical supported path-based config to proceed to preview.

Modify:

src/test/suite/hf1OracleFreshConsumer.test.ts

Cover:

- end-to-end fresh-consumer CREATE_NEW_JOB positive path;
- canonical path-based dataframe_writer config;
- real Preview ID;
- zero-write preview;
- no framework source;
- explicit negative Unity Catalog case;
- all Repair-5/6/7 security invariants remain green.

Modify:

src/test/verifyVsixContents.ts

as specified in Section 14.

No source-text-only assertions may substitute for behavior tests, except direct
validation of the packaged JSON/Markdown assets themselves.

==================================================
16. CONTEXT TRUST BOUNDARY
==================================================

Record but do not redesign:

CONTEXT_OWNERSHIP_AND_TRUST_BOUNDARY

Repair 8 must not make:

resources/copilot/context/**

the machine-authoritative contract.

Authority must remain:

resources/framework/contracts/job-config-envelope.v1.json

The context file may explain or reference the authority but cannot override it.

No broader agent/skill/context redesign is authorized in this task.

==================================================
17. VALIDATION
==================================================

Use only existing dependencies.

Run:

1. production compile;
2. lint;
3. all focused Repair-8 test files;
4. affected Repair-5/6/7 regression suites;
5. the full unit suite.

At minimum, directly exercise all eight test files:

- trustedJobConfigEnvelope.test.ts
- configExplain.test.ts
- firstRenderInvariantGuard.test.ts
- EtlReadOnlyToolService.test.ts
- jobDevelopmentReadiness.test.ts
- packageAssets.test.ts
- etlActionTools.test.ts
- hf1OracleFreshConsumer.test.ts

Acceptance rules:

- compile must pass;
- lint must pass;
- all Repair-8 focused tests must pass;
- positive fresh-consumer path must issue a Preview ID;
- preview must remain zero-write;
- Unity Catalog negative test must return the explicit unsupported diagnostic;
- no new functional or security failure is accepted;
- Repair-5/6/7 focused regressions must remain green.

The full unit suite may still contain the known historical failures.

Classify historical failures by exact test name, not only by count.

Expected historical families are:

- two EvalGating/Phase-H baseline freshness failures;
- three protected Copilot workflow-customization failures.

Do not repair, suppress, regenerate, or relabel those protected failures.

Any additional failure is a Repair-8 regression and must be resolved within the
authorized scope or reported as:

REPAIR_8_VALIDATION_FAILED

Do not regenerate Phase-H baselines.

==================================================
18. SCOPE AND BYTE-PRESERVATION PROOF
==================================================

At task end report:

- exact actual changed paths;
- exact new files;
- staged count;
- whether any unauthorized path changed;
- whether package.json remains at 0.3.140;
- whether Repair-5/6/7 protected file hashes changed only where explicitly
  authorized;
- whether etl-framework-adb remained untouched;
- whether any development test workspace was touched;
- whether any dependency was installed/downloaded;
- whether any VSIX was built or installed;
- whether any commit or push occurred.

Required:

AUTHORIZED_FILE_COUNT: 21
NEW_FILE_COUNT: 3
UNAUTHORIZED_CHANGED_PATH_COUNT: 0
VERSION_AFTER_IMPLEMENTATION: 0.3.140

Do not stage, commit, push, package, install, or press Keep as part of this task.

==================================================
19. FINAL REPORT
==================================================

Report:

REPOSITORY_IDENTITY_MATCH: YES/NO
AUTHORIZED_SCOPE_MATCH: YES/NO
ACTUAL_CHANGED_PATHS: <exact list>
NEW_FILES_CREATED: <exact list>
TRUSTED_JOB_CONFIG_CONTRACT_IMPLEMENTED: YES/NO
TRUSTED_JOB_CONFIG_RESOLVER_IMPLEMENTED: YES/NO
CANONICAL_ENVELOPE_GUARD_ENFORCED: YES/NO
MODULE_EXTRACTOR_CANONICAL_FORMS_PASS: YES/NO
UNITY_CATALOG_SUPPORT_ADDED: NO
UNITY_CATALOG_UNSUPPORTED_DIAGNOSTIC_PASS: YES/NO
CRITICAL_CONFIG_KEYS_FALLBACK_PASS: YES/NO
PACKAGED_EXAMPLE_SEARCH_PASS: YES/NO
PACKAGE_SELF_CONSISTENCY_PASS: YES/NO
FRESH_CONSUMER_PATH_BASED_PREVIEW_ID_ISSUED: YES/NO
FRESH_CONSUMER_PREVIEW_ZERO_WRITES: YES/NO
FRAMEWORK_SOURCE_REQUIRED: NO
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
FOCUSED_REPAIR_8_TESTS_PASS: YES/NO
REPAIR_5_6_7_REGRESSIONS_PASS: YES/NO
FULL_UNIT_HISTORICAL_FAILURES_ONLY: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: YES/NO
NEW_SECURITY_REGRESSIONS: YES/NO
VERSION_REMAINS_0_3_140: YES/NO
VSIX_BUILT: NO
GIT_MUTATION_PERFORMED: NO
UNAUTHORIZED_SCOPE_DRIFT: YES/NO
READY_FOR_INDEPENDENT_READ_ONLY_REAUDIT: YES/NO

Do not declare Repair 8 release-ready.

End exactly with one:

LOCAL_HOTFIX_HF1_V2_QA_CONTRACT_BLOCKER_REPAIR_8_IMPLEMENTED_AWAITING_INDEPENDENT_REAUDIT

or:

LOCAL_HOTFIX_HF1_V2_QA_CONTRACT_BLOCKER_REPAIR_8_IMPLEMENTATION_BLOCKED

or:

LOCAL_HOTFIX_HF1_V2_QA_CONTRACT_BLOCKER_REPAIR_8_VALIDATION_FAILED
