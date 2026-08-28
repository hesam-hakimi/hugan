TASK: HF1_V2_GENUINELY_INDEPENDENT_REVIEW_RUNTIME_QA_SUPPORT_AND_STRUCTURED_DIAGNOSTICS

Perform a genuinely independent, read-only review of the complete accumulated
Runtime QA support and Repair 13 structured-diagnostics change set.

Work against:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use:

* a fresh Claude harness Chat;
* source-governance Agent etl-independent-reviewer;
* Claude Opus 5 with Max reasoning;
* exactly one effective repository target.

Do not use consumer Agents such as ETL Orchestrator, ETL Implementer, or ETL
Verifier as review authority.

The implementation checkpoint ended with:

RUNTIME_QA_STRUCTURED_DIAGNOSTICS_RESULT:
PASS_READY_FOR_GENUINELY_INDEPENDENT_REVIEW

Treat that statement and every prior report as untrusted evidence to verify.

This task is strictly read-only.

==================================================

1. IDENTITY AND NON-MUTATION
    ==================================================

Required identity:

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION:
0.3.145

Required:

* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrent Agent mutation.

Before reviewing, capture an independent filesystem snapshot containing path,
size, SHA-256, Git status, and mtime.

Do not use git ls-files as the sole authority because protected and untracked
content must also be covered.

Run all compilation and dynamic tests only in a byte-faithful task-owned mirror.

Make zero changes to the live repository.

Do not regenerate the golden baseline in the live tree.

==================================================
2. REVIEW THE COMPLETE ACCUMULATED CHANGE SET

Independently enumerate every Runtime QA support change currently present,
including relevant changes under:

* src/core/sttm/**;
* src/tools/**;
* src/customization/CopilotAssetCatalog.ts;
* src/test/fixtures/sttm/synthetic_repair13_qa_bundle/**;
* src/test/helpers/registerVscodeStub.ts;
* src/test/suite/EtlReadOnlyTools.test.ts;
* src/test/suite/sttmRepair13.test.ts;
* resources/copilot/agents/etl-orchestrator.agent.md;
* resources/copilot/agents/etl-verifier.agent.md;
* docs/eval/phase_h_latest_report.json;
* docs/eval/phase_h_latest_report.md.

Do not restrict the review to the final six changed paths. Review the complete
accumulated Runtime QA support implementation.

Identify:

* modified paths;
* added paths;
* deleted paths;
* unauthorized or unexplained paths;
* pre-existing dirty paths;
* task-attributable paths.

Confirm specifically that package.json and src/test/testPatterns.ts were already
dirty before the reviewed implementation and were not modified by these tasks.

==================================================
3. STRUCTURED DIAGNOSTIC CONTRACT

Verify independently through the full public seam:

EtlReadOnlyToolService.interpretSttm(…) -> { markdown, data }

Prove:

* a dedicated public structured parser-diagnostic channel exists;
* STTM_TABLE_MALFORMED is reused rather than duplicated;
* malformed short rows fail closed;
* malformed oversized rows fail closed;
* malformed rows receive no active authority;
* deterministic row identity is exposed;
* Markdown and structured diagnostic codes agree;
* Markdown and structured affected-row identities agree;
* valid mapping IDs and order remain unchanged;
* a valid document reports its real informational diagnostics rather than
    fabricating an empty list;
* absence of diagnostics is represented honestly;
* no source-attribute value or secret leaks through diagnostic messages;
* no write or machine authority is introduced.

Use negative controls proving the tests fail if:

* the structured diagnostic channel is removed;
* malformed rows regain active authority;
* parser relatedIds are removed;
* Markdown and structured diagnostics diverge.

==================================================
4. REPAIR 13 AND QA FIXTURE COVERAGE

Verify the synthetic Runtime QA fixture covers the currently supported contract:

* active;
* inactive;
* conflicting;
* unresolved BR;
* unresolved TR;
* unresolved JC;
* unresolved ER;
* malformed short row;
* malformed oversized row;
* structured/Markdown dual-channel parity.

Confirm the following are deliberately deferred, not silently claimed as tested:

FT:
DEFERRED_PARSER_UNREACHABLE_NOT_REQUIRED_FOR_REPAIR_13_RUNTIME_QA

Historical state:
DEFERRED_UNSUPPORTED_INPUT_SYNTAX

Unknown state:
DEFERRED_UNSUPPORTED_INPUT_SYNTAX

Confirm the deferrals do not weaken current supported-input behavior.

==================================================
5. CONSUMER AGENT ASSET REVIEW

Verify:

* src/customization/CopilotAssetCatalog.ts is the canonical source;
* the Orchestrator and Verifier packaged resources match it;
* package asset byte-lock passes;
* ETL Orchestrator preserves structured and Markdown channels;
* ETL Verifier independently compares both channels;
* tools are byte-identical to their pre-change definitions;
* delegation lists are unchanged;
* user visibility is unchanged;
* internal worker Agents remain non-user-facing;
* no Agent receives new write, execution, approval, installation, Preview, or
    deployment authority.

Reconcile the two carried-forward CONTROL_PLANE_PATH_CHANGED findings.

Determine whether they are:

* expected generated-product-source changes with proven catalog provenance; or
* a real governance-boundary defect.

Do not modify the manifest or validators.

==================================================
6. PHASE H GOLDEN BASELINE REVIEW

Independently run the canonical Phase H generator in two separate mirrors.

Verify:

* tracked-input drift was caused only by authorized source changes;
* both generated reports are semantically equal;
* tracked-input digest agrees;
* scenario set and outcomes agree;
* acceptance, parity, validation, correction, and coverage results agree;
* only documented timestamp and measured-latency fields may vary;
* committed JSON and Markdown reports agree semantically;
* no scenario, threshold, assertion, or tracked-input pattern was weakened;
* the negative stale-baseline test still detects deliberate drift;
* both formerly failing EvalGating tests now pass.

Fail review if the baseline refresh merely hides behavioral regression.

==================================================
7. VALIDATION

Run in the mirror:

1. compile;
2. compile:test;
3. lint;
4. Repair 11 focused suite;
5. Repair 12 canonical suite;
6. Repair 13 focused suite;
7. Runtime QA support fixture suite;
8. public structured-diagnostic seam tests;
9. package asset byte-lock;
10. Phase H evaluation gate;
11. governance tests;
12. customization validation;
13. test-registration validation;
14. canonical full unit suite.

Expected implementation report:

* compile: pass;
* compile:test: pass;
* lint: pass;
* Repair 11: pass;
* Repair 12: 21/21;
* Repair 13: pass;
* Runtime QA support fixture: pass;
* governance: pass;
* full unit: 2298 passing, 1 pending, 2 failing;
* new functional regressions: 0;
* new security regressions: 0.

Do not accept counts alone.

Reconcile every count difference by exact test identity.

The only allowed full-suite failures are exact unchanged fingerprints for:

F1:
missing .github/prompts/deploy-v3-agent-tool-context-gap.prompt.md

F3:
the eleven existing src/**/AGENT.md files.

Any other failure blocks approval.

==================================================
8. FINAL LIVE NON-MUTATION PROOF

Repeat the independent live filesystem snapshot.

Required:

* live paths changed by review: 0;
* staged files: 0;
* stash entries: 0;
* package.json unchanged;
* package version remains 0.3.145;
* src/test/testPatterns.ts unchanged;
* existing VSIX files unchanged;
* QA workspace untouched;
* Runtime QA not started;
* no Preview or Write;
* no commit, push, or tag.

==================================================
9. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
INDEPENDENCE_GATE: PASS/FAIL
REPOSITORY_MUTATED_BY_REVIEW: YES/NO

COMPLETE_CHANGE_SET_REVIEWED: YES/NO
AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
PRE_EXISTING_DIRTY_PATHS_RECONCILED: YES/NO

PUBLIC_STRUCTURED_DIAGNOSTIC_CHANNEL: PASS/FAIL
MALFORMED_ROWS_FAIL_CLOSED: YES/NO
MALFORMED_ROWS_ACTIVE_AUTHORITY: YES/NO
MARKDOWN_STRUCTURED_DIAGNOSTIC_PARITY: YES/NO
VALID_MAPPING_IDS_AND_ORDER_PRESERVED: YES/NO
PUBLIC_SEAM_TESTED: YES/NO

QA_SUPPORTED_SCENARIOS_PASS: YES/NO
FT_STATUS: 
HISTORICAL_STATUS: 
UNKNOWN_STATUS: 

AGENT_CATALOG_RESOURCE_PARITY: YES/NO
PACKAGE_ASSET_BYTE_LOCK_PASS: YES/NO
AGENT_TOOL_SETS_CHANGED: YES/NO
AGENT_AUTHORITY_BROADENED: YES/NO
CONTROL_PLANE_FINDINGS_DISPOSITION: 

PHASE_H_REFRESH_LEGITIMATE: YES/NO
GOLDEN_GENERATIONS_SEMANTICALLY_EQUAL: YES/NO
GOLDEN_ASSERTIONS_WEAKENED: YES/NO
NEGATIVE_DRIFT_TEST_PASS: YES/NO

COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_11_PASS: YES/NO
REPAIR_12_PASS: YES/NO
REPAIR_13_PASS: YES/NO
RUNTIME_QA_SUPPORT_FIXTURE_PASS: YES/NO
GOVERNANCE_PASS: YES/NO

FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_FAILURES: 
FULL_UNIT_COUNTS_RECONCILED: YES/NO
F1_UNCHANGED: YES/NO
F3_UNCHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 
UNRESOLVED_HIGH_OR_SECURITY_FINDINGS: 

PACKAGE_VERSION_CHANGED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
RUNTIME_QA_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

READY_FOR_VERSION_0_3_146_AND_PACKAGE: YES/NO
READY_TO_INSTALL: NO
READY_FOR_RUNTIME_QA: NO

End exactly with one:

RUNTIME_QA_SUPPORT_INDEPENDENT_REVIEW_RESULT:
PASS_READY_FOR_VERSION_0_3_146_AND_PACKAGE

RUNTIME_QA_SUPPORT_INDEPENDENT_REVIEW_RESULT:
FAIL_IMPLEMENTATION_OR_VALIDATION

RUNTIME_QA_SUPPORT_INDEPENDENT_REVIEW_RESULT:
FAIL_NEW_FUNCTIONAL_OR_SECURITY_REGRESSION

RUNTIME_QA_SUPPORT_INDEPENDENT_REVIEW_RESULT:
FAIL_REVIEW_MUTATED_REPOSITORY

RUNTIME_QA_SUPPORT_INDEPENDENT_REVIEW_RESULT:
BLOCKED_IDENTITY_OR_INDEPENDENCE
