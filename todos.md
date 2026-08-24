TASK: LOCAL_HOTFIX_HF1_V2_QA_CONTRACT_BLOCKER_REPAIR_8_INDEPENDENT_READ_ONLY_REAUDIT

Perform an independent, adversarial, READ-ONLY re-audit of the current
Repair-8 working tree.

IMPORTANT:

Do NOT trust the prior implementation report as evidence.
Reconstruct conclusions independently from the live working tree, tests,
existing build artifacts, and executable code.

DO NOT modify any file.
DO NOT repair anything.
DO NOT build a VSIX.
DO NOT install or download dependencies.
DO NOT stage, commit, push, reset, restore, checkout, stash, clean, rename,
delete, or regenerate anything.
DO NOT regenerate Phase-H baselines.
DO NOT modify any development test workspace or consumer repository.

This is an independent release-gate investigation only.

==================================================
1. VERIFY REPOSITORY IDENTITY
==================================================

Expected software-development repository:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected base HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected source version:

0.3.140

Expected publisher:

td-etl

Verify independently.

Capture:

- current changed paths;
- untracked paths;
- staged count;
- .github/** status;
- package.json version;
- package-lock.json status;
- existing VSIX artifacts and their mtimes;
- source mtimes for Repair-8 files.

Do not mutate anything while collecting evidence.

==================================================
2. RECONSTRUCT REPAIR-8 CHANGE SURFACE
==================================================

Independently determine whether Repair 8 changed exactly the authorized
21-path set:

NEW:
1. src/core/framework/TrustedJobConfigEnvelopeResolver.ts
2. resources/framework/contracts/job-config-envelope.v1.json
3. src/test/suite/trustedJobConfigEnvelope.test.ts

AUTHORIZED EXISTING PATHS:
4. src/core/trusted/FirstRenderInvariantGuard.ts
5. src/core/trusted/index.ts
6. src/core/utils/ModuleSequenceExtractor.ts
7. src/core/framework/FrameworkDiscoveryService.ts
8. src/tools/EtlReadOnlyToolService.ts
9. src/core/readiness/ReadinessProfileCatalog.ts
10. src/core/readiness/JobDevelopmentReadinessEvaluator.ts
11. resources/copilot/context/etl-module-reference.md
12. resources/copilot/knowledge/examples/dataframe-writer-export.example.json
13. resources/copilot/knowledge/examples/curated-load-enrich.example.json
14. src/test/verifyVsixContents.ts
15. src/test/suite/configExplain.test.ts
16. src/test/suite/firstRenderInvariantGuard.test.ts
17. src/test/suite/EtlReadOnlyToolService.test.ts
18. src/test/suite/jobDevelopmentReadiness.test.ts
19. src/test/suite/packageAssets.test.ts
20. src/test/suite/etlActionTools.test.ts
21. src/test/suite/hf1OracleFreshConsumer.test.ts

Distinguish:

- Repair-8 changes;
- accepted Repair-5/6/7 pre-existing changes;
- unrelated pre-existing working-tree changes;
- any unauthorized Repair-8 mutation.

Do not infer scope only from git status.

==================================================
3. AUDIT THE TRUSTED CONTRACT
==================================================

Inspect independently:

resources/framework/contracts/job-config-envelope.v1.json

and:

src/core/framework/TrustedJobConfigEnvelopeResolver.ts

Verify:

- canonical modules-object envelope;
- stage-keyed modules;
- options.module;
- options.method;
- supported module types;
- required/optional fields;
- dataframe_writer destination semantics;
- critical config keys;
- strict whitelist;
- version validation;
- integrity validation;
- deterministic fingerprint;
- secret/content scanning;
- installed-resource resolution;
- no normal process.cwd() dependency;
- mutation isolation;
- fail-closed behavior;
- consumer-editable context cannot override authority.

Confirm the contract is machine-authoritative and:

resources/copilot/context/**

remains advisory only.

==================================================
4. AUDIT CANONICAL JOB-CONFIG ENFORCEMENT
==================================================

Trace the real runtime call path.

Verify that fresh-consumer agent-authored job config reaches deterministic
enforcement before preview/write.

Specifically determine whether:

NON_CANONICAL_JOB_CONFIG_ENVELOPE

is enforced for all relevant paths.

Test/reason about:

- canonical colon HOCON;
- canonical equals HOCON;
- legal omitted-separator-before-{ HOCON;
- quoted JSON;
- modules array;
- missing modules envelope;
- missing options.module;
- malformed module structure.

Confirm no alternate production route bypasses the invariant.

==================================================
5. AUDIT DATAFRAME_WRITER / UNITY CATALOG BEHAVIOR
==================================================

Independently inspect executable framework evidence and extension behavior.

Confirm whether the current dataframe_writer supports direct Unity Catalog
three-part table-name writes.

Do NOT assume the implementation report is correct.

If unsupported, verify:

- canonical module detection still succeeds;
- explicit UNSUPPORTED_UNITY_CATALOG_TARGET is produced;
- readiness returns unsupported_unity_catalog_target;
- it does not degrade to "No modules detected in job config";
- it does not degrade only to "Confirm output path or table";
- no Preview ID is issued;
- no write occurs.

Also confirm supported path-based dataframe_writer behavior still succeeds.

==================================================
6. AUDIT FRESH-CONSUMER FALLBACK
==================================================

With no framework checkout available, verify from tests/code that:

- trusted packaged contract resolves;
- criticalConfigKeys are non-empty;
- packaged examples are searchable;
- zero local search roots does not incorrectly produce
  no_search_roots_available when packaged examples exist;
- local/package precedence is deterministic;
- no framework source is required;
- no consumer-editable context becomes authoritative.

==================================================
7. AUDIT PREVIEW / WRITE SECURITY
==================================================

Verify independently that the Repair-8 positive fresh-consumer path:

- classifies CREATE_NEW_JOB;
- produces canonical job config;
- issues a real Preview ID;
- performs zero filesystem writes during preview;
- requires explicit approval before write;
- remains protected by Repair-5/6/7 authorization and physical-containment
  controls.

Trace production code rather than relying only on test names.

Confirm Repair 8 did not weaken:

- TrustedWriteApprovalStore;
- WriteAuthorization;
- physical containment;
- root selection;
- replay protection;
- stale-preview protection;
- manifest binding.

==================================================
8. RUN READ-ONLY VALIDATION
==================================================

Using already-installed dependencies only, run:

- compile;
- lint;
- all 8 Repair-8 focused suites;
- relevant Repair-5/6/7 regression suites;
- full unit suite.

Do not alter source or fixtures to make tests pass.

List every full-suite failure by exact test name.

Classify each as exactly one:

A. HISTORICAL_PROTECTED_FAILURE
B. REPAIR_8_FUNCTIONAL_REGRESSION
C. REPAIR_8_SECURITY_REGRESSION
D. STALE_BUILD_ARTIFACT_FAILURE
E. TEST_INFRASTRUCTURE_DEFECT
F. UNRELATED_PRE_EXISTING_FAILURE
G. UNKNOWN

Provide evidence for every classification.

==================================================
9. INVESTIGATE THE SIXTH FAILURE ADVERSARIALLY
==================================================

The implementation report claimed one additional full-suite failure:

"VSIX machine-specific path scan > built VSIX (when present) contains no
machine-specific absolute path"

with missing entry:

extension/resources/framework/contracts/job-config-envelope.v1.json

Do NOT accept that explanation automatically.

Investigate independently.

Determine:

1. Which exact VSIX file the test selected.
2. Its absolute path.
3. Its filename.
4. Its internal extension version.
5. Its creation/modification timestamp.
6. Whether it predates Repair 8.
7. Whether it contains the new job-config-envelope contract.
8. Why the test selected that VSIX.
9. Whether the source tree/package policy would include the new contract in a
   freshly built VSIX.
10. Whether the failure is caused by stale artifact selection, source/package
    omission, verifier logic, or another defect.

Inspect the VSIX read-only.

Do NOT rebuild, rename, delete, or modify it.

Also inspect every existing .vsix candidate and determine whether the test's
selection algorithm can accidentally bind the unit suite to stale build
artifacts.

Answer explicitly:

SIXTH_FAILURE_CAUSED_BY_REPAIR8_SOURCE_DEFECT: YES/NO/UNKNOWN

SIXTH_FAILURE_CAUSED_BY_STALE_VSIX: YES/NO/UNKNOWN

VSIX_SELECTION_LOGIC_ROBUST: YES/NO

FRESH_VSIX_BUILD_REQUIRED_TO_CLOSE_GATE: YES/NO

If the selection logic itself is defective, identify the exact code path and
smallest future repair, but DO NOT implement it.

==================================================
10. FALSE-GREEN CHECK
==================================================

Determine whether the Repair-8 focused suite could pass while the actual
runtime feature is broken.

Use mutation/adversarial reasoning where possible without modifying source.

Verify specifically that tests genuinely fail conceptually if:

- trusted contract resolution is disabled;
- canonical envelope guard is disabled;
- packaged fallback criticalConfigKeys become empty;
- packaged example search is disabled;
- Unity Catalog rejection is removed;
- preview writes to disk;
- framework checkout becomes required.

Do not claim mutation evidence unless actually executed safely without source
mutation.

==================================================
11. NO-TOUCH / VERSION PROOF
==================================================

Confirm:

VERSION: 0.3.140

and verify:

- package.json was not version-bumped by Repair 8;
- no VSIX was built during this audit;
- no dependencies installed/downloaded;
- no consumer/development-test workspace mutated;
- etl-framework-adb not mutated;
- no Git mutation;
- no .github/** mutation;
- no Phase-H baseline regeneration.

==================================================
12. DECISION
==================================================

Return these markers:

REPOSITORY_IDENTITY_MATCH: YES/NO
REPAIR_8_SCOPE_MATCH: YES/NO
UNAUTHORIZED_REPAIR_8_PATHS: <count>
TRUSTED_CONTRACT_VALID: YES/NO
TRUSTED_RESOLVER_VALID: YES/NO
CANONICAL_ENVELOPE_RUNTIME_ENFORCED: YES/NO
MODULE_EXTRACTION_CORRECT: YES/NO
UNITY_CATALOG_DIRECT_WRITE_SUPPORTED: YES/NO
UNITY_CATALOG_NEGATIVE_DIAGNOSTIC_CORRECT: YES/NO
PACKAGED_FALLBACK_CORRECT: YES/NO
PACKAGED_EXAMPLE_SEARCH_CORRECT: YES/NO
FRESH_CONSUMER_PREVIEW_PATH_CORRECT: YES/NO
PREVIEW_ZERO_WRITE_PROVEN: YES/NO
REPAIR_5_6_7_SECURITY_PRESERVED: YES/NO
COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
FOCUSED_REPAIR_8_TESTS_PASS: YES/NO
FULL_UNIT_FAILURE_COUNT: <number>
HISTORICAL_PROTECTED_FAILURE_COUNT: <number>
REPAIR_8_FUNCTIONAL_REGRESSION_COUNT: <number>
REPAIR_8_SECURITY_REGRESSION_COUNT: <number>
STALE_BUILD_ARTIFACT_FAILURE_COUNT: <number>
SIXTH_FAILURE_CAUSED_BY_REPAIR8_SOURCE_DEFECT: YES/NO/UNKNOWN
SIXTH_FAILURE_CAUSED_BY_STALE_VSIX: YES/NO/UNKNOWN
VSIX_SELECTION_LOGIC_ROBUST: YES/NO
FRESH_VSIX_BUILD_REQUIRED_TO_CLOSE_GATE: YES/NO
VERSION_REMAINS_0_3_140: YES/NO
WORKING_TREE_MUTATED_BY_AUDIT: NO

Then make exactly one recommendation:

A. REPAIR_8_SOURCE_FIX_REQUIRED
B. REPAIR_8_SOURCE_VALID_BUILD_GATE_REQUIRED
C. REPAIR_8_READY_FOR_VERSION_BUMP
D. REPAIR_8_SCOPE_AMENDMENT_REQUIRED

Do not equate a stale VSIX failure with a source defect without proving it.

Do not authorize version 0.3.141 yet unless all source/runtime findings are
clean and the only unresolved condition is the intentionally deferred fresh
package build.

End exactly with one:

LOCAL_HOTFIX_HF1_V2_REPAIR_8_INDEPENDENT_REAUDIT_PASS

LOCAL_HOTFIX_HF1_V2_REPAIR_8_INDEPENDENT_REAUDIT_FAIL

LOCAL_HOTFIX_HF1_V2_REPAIR_8_INDEPENDENT_REAUDIT_BLOCKED
