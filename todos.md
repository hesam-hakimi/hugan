TASK: HF1_V2_REPAIR_RUNTIME_QA_DATA_PART_AND_FIXTURE_COVERAGE

Implement the bounded support repair required to complete Repair 13 consumer
Runtime QA.

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Execution context:

* fresh Claude harness session;
* source-governance Agent: etl-hotfix-implementer;
* Claude Opus 5 with Max reasoning;
* exactly one open workspace root;
* do not invoke consumer ETL Orchestrator or consumer ETL Implementer;
* do not access the Development Test Workspace;
* do not run @etl /workflow.

The preceding read-only diagnosis ended with:

RUNTIME_QA_DIAGNOSTIC_RESULT: BLOCKED_QA_INPUT_COVERAGE

It independently established:

* Repair 13 itself is not defective;
* EtlReadOnlyToolService.interpretSttm returns both structured data and
    rendered markdown;
* the public Tool handler receives both;
* createToolResult attaches a text part and a
    vscode.LanguageModelDataPart.json(...) structured part;
* VS Code supports the mixed dual-channel envelope;
* both channels use the same authoritative selectActiveMappings() result;
* no structured payload is lost inside the service or Tool adapter;
* consumer Agents are not instructed to inspect the structured Data Part;
* createToolResult has no direct unit coverage;
* LanguageModelDataPart access is not safely guarded when the class is absent;
* the existing consumer QA fixture cannot exercise the reachable negative
    Repair 13 surfaces;
* Parser-producible states are active, inactive, and conflicting;
* historical and unknown are union members but have no parser producer.

This task must repair only those supporting gaps.

Do not redesign Repair 13.

==================================================

1. IDENTITY AND EXECUTION GATES
    ==================================================

Verify:

REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

EXPECTED_HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

EXPECTED_SOURCE_VERSION:
0.3.145

Required:

* exactly one effective repository root;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* existing 0.3.145 VSIX files protected;
* no concurrently mutating Agent.

The repository contains a substantial pre-existing dirty overlay.

Before editing, create an independent OS-level content snapshot containing:

* all tracked modifications and deletions;
* all non-ignored untracked files;
* byte length and SHA-256 of every repository file;
* staged and stash state;
* package.json;
* Repair 11, Repair 12, and Repair 13 paths;
* governance assets;
* .claude/**;
* existing VSIX files.

Store snapshots and logs only under a task-owned operating-system temporary
directory.

If inline process capture is unreliable, use file-redirection and task-owned
temporary helpers. Do not modify the repository to repair process execution.

Stop before editing on identity mismatch, staged files, concurrent mutation,
multiple effective roots, or unproven command execution.

==================================================
2. AUTHORIZED CHANGE BOUNDARY

Authorized existing paths:

* src/tools/index.ts
* src/test/helpers/registerVscodeStub.ts
* src/test/suite/EtlReadOnlyTools.test.ts
* src/test/suite/sttmRepair13.test.ts
* src/test/suite/copilotWorkflowCustomization.test.ts
* resources/copilot/agents/etl-orchestrator.agent.md
* resources/copilot/agents/etl-verifier.agent.md

One new synthetic fixture directory is authorized only beneath the repository’s
existing canonical STTM test-fixture root.

Use the exact existing fixture naming and directory conventions discovered from
the live repository.

No other path is authorized.

Do not modify:

* Repair 13 production selector or renderer;
* SttmActiveState;
* package.json;
* package version;
* package-lock.json;
* testPatterns.ts;
* tsconfig files;
* Repair 11 or Repair 12 behavior;
* .claude/**;
* .github/** governance assets;
* consumer workspace files;
* existing VSIX files.

If a correct implementation requires another path, stop and report
BLOCKED_CHANGE_BOUNDARY_EXPANSION.

==================================================
3. OWNER DECISION — HISTORICAL AND UNKNOWN

Apply this decision:

* Do not add parser behavior for historical or unknown in this hotfix.
* Do not remove those union members in this hotfix.
* Do not create a fake STTM state column or synthetic parser-only format.
* Preserve the existing fail-closed type-level tests for these values.
* Classify them as parser-unreachable contract members requiring a separate
    post-hotfix architecture decision.

Runtime fixture coverage is required only for states and diagnostics producible
through the real public parser.

==================================================
4. ADAPTER HARDENING

Repair createToolResult in src/tools/index.ts.

Required behavior:

1. When vscode.LanguageModelDataPart exists and exposes a callable json
    factory:
    * return the Markdown text part;
    * attach the structured JSON Data Part;
    * preserve the complete response data;
    * preserve the result title;
    * preserve Active Mapping ID order;
    * preserve excluded mappings and diagnostics.
2. When LanguageModelDataPart or its json factory is unavailable:
    * do not throw;
    * return a valid text-only Tool result;
    * preserve the full Markdown;
    * do not report total Tool failure;
    * do not fabricate structured-channel availability.
3. Do not change Tool permissions, schemas, names, registration, invocation
    authority, or write capability.
4. Do not modify Repair 13 mapping-selection behavior.

==================================================
5. DIRECT DUAL-CHANNEL TESTS

Add direct tests for createToolResult.

At minimum test:

A. Data Part class and JSON factory available:

* result contains exactly the expected text and structured parts;
* structured data round-trips without mutation;
* title is preserved;
* activeMappings IDs and order are preserved;
* activeMappingCount agrees;
* excludedMappings and diagnostics are preserved;
* Markdown and structured IDs originate from the same response.

B. LanguageModelDataPart absent:

* no exception;
* valid text-only result;
* complete Markdown retained.

C. class present but json factory absent or non-callable:

* no exception;
* valid text-only result.

D. structured result containing no excluded mappings:

* valid empty structured collection;
* no fabricated diagnostic.

Update the VS Code stub only as narrowly as necessary.

Do not weaken existing assertions.

==================================================
6. CONSUMER AGENT GUIDANCE

Update only the packaged consumer Agent sources:

* ETL Orchestrator;
* ETL Verifier.

Add concise guidance stating:

* etl_interpret_sttm may return both a Markdown text part and a structured JSON
    Data Part;
* when both exist, inspect both;
* compare Active Mapping IDs, order, and count;
* inspect excluded mappings, active state, active authority, conflict diagnostics,
    and unresolved-reference diagnostics from structured data;
* compare those fields with the rendered Markdown;
* do not report the structured channel as absent without inspecting Tool result
    content parts;
* if the runtime genuinely supplies text only, report
    STRUCTURED_CHANNEL_UNAVAILABLE without fabricating parity;
* Tool possession does not grant write, Preview, approval, or runtime authority.

Do not:

* change user-invocable;
* add tools;
* remove tools;
* broaden delegation;
* grant write or runtime authority;
* make ETL Verifier mutating;
* expose internal specialists directly to the user.

Add or update customization tests proving these instructions exist without
changing the Agent topology.

==================================================
7. REACHABLE REPAIR 13 QA FIXTURE

Create one canonical synthetic Markdown-bundle fixture under the existing STTM
test-fixture root.

Use:

* the real canonical 26-column Field Mapping header;
* existing parser-supported sheets and filenames;
* real parser-supported BR/TR/JC/ER/FT identifier patterns;
* synthetic values only.

Cover every parser-reachable surface established by the diagnosis, including:

1. active mapping with all references resolved;
2. a second distinct active mapping;
3. full-strikethrough row or important cell producing inactive;
4. partial strikethrough remaining active;
5. deterministic conflict using distinct sources;
6. deterministic conflict using distinct transformation-rule IDs;
7. unresolved BR reference;
8. unresolved TR reference when supported by the real resolver path;
9. unresolved JC reference;
10. unresolved ER reference;
11. unresolved FT reference when supported by the real resolver path;
12. reference from an active mapping to an inactive referenced rule;
13. malformed row with a cell-count mismatch;
14. oversized referenced-rule text and its public-summary behavior.

Use fewer rows only if multiple expectations can be proven without ambiguity.

Do not add fake historical, unknown, or state-literal rows.

For every scenario assert through the full public interpretSttm seam:

* structured Active Mapping IDs;
* Markdown Active Mapping IDs;
* exact deterministic order;
* exact count;
* excluded mappings;
* activeState;
* activeAuthority;
* conflict diagnostics;
* unresolved-reference diagnostics;
* blocker or non-blocker result;
* fail-closed behavior;
* no authority broadening.

Required:

* structured and Markdown Active Mapping IDs are exactly equal;
* their order is exactly equal;
* conflicting mappings are excluded from both;
* inactive mappings are excluded without becoming blockers merely because they
    are inactive;
* unresolved authority-critical references are disclosed and non-authoritative;
* malformed content is diagnosed rather than silently discarded;
* Repair 12 behavior remains unchanged.

==================================================
8. VALIDATION

Run generated-output validations only in a task-owned temporary mirror so the
live repository’s out/**, reports, baselines, and VSIX files are not changed.

Reuse existing dependencies read-only.

Do not install or download anything.

Run:

1. focused createToolResult tests;
2. EtlReadOnlyTools suite;
3. Repair 13 focused suite;
4. consumer Agent/customization tests;
5. Repair 11 focused suite;
6. Repair 12 focused suite;
7. STTM parser and reference-resolution suites;
8. governance tests;
9. customization validator;
10. test-registration validator;
11. compile;
12. compile:test;
13. lint;
14. canonical full unit suite.

Require:

* all new tests pass;
* Repair 13 remains at least 23/23 passing before counting new tests;
* Repair 12 remains 21/21;
* Repair 11 remains unchanged and passing;
* governance enforcement remains passing;
* customization blockers, majors, and minors remain zero;
* test-registration enforcing findings remain zero;
* the only full-suite failures remain the exact pre-existing F1 and F3
    fingerprints;
* new functional regressions: 0;
* new security regressions: 0.

Compare failures by exact identity and fingerprint, not aggregate count.

Do not regenerate the Phase H golden baseline.

Do not make F1 or F3 pass by creating unrelated Agents, Prompts, or deleting
legacy AGENT.md files.

==================================================
9. FINAL CHANGE-BOUNDARY PROOF

Compare the final repository against the independent pre-task snapshot.

Report:

* every task-attributable changed path;
* every preserved pre-existing path;
* every unauthorized changed path;
* staged and stash state;
* package.json hash before and after;
* source version before and after;
* Repair 11/12/13 core hashes before and after;
* .claude/** hashes before and after;
* existing VSIX hashes before and after.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
TEST_PATTERNS_CHANGED: NO
REPAIR_13_CORE_BEHAVIOR_CHANGED: NO
REPAIR_12_BEHAVIOR_CHANGED: NO
SOURCE_GOVERNANCE_AGENTS_CHANGED: NO
EXISTING_VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
WORKFLOW_PROVISIONED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
STAGED_FILES: 0
STASH_ENTRIES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

==================================================
10. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
INDEPENDENT_BASELINE_CAPTURED: YES/NO

AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 

ADAPTER_CLASS_ABSENCE_FAILS_GRACEFULLY: YES/NO
ADAPTER_JSON_FACTORY_ABSENCE_FAILS_GRACEFULLY: YES/NO
DUAL_CHANNEL_RESULT_TESTED: YES/NO
STRUCTURED_DATA_ROUNDTRIP_PASS: YES/NO
MARKDOWN_STRUCTURED_IDS_EQUAL: YES/NO
MARKDOWN_STRUCTURED_ORDER_EQUAL: YES/NO
MARKDOWN_STRUCTURED_COUNTS_EQUAL: YES/NO

ORCHESTRATOR_STRUCTURED_GUIDANCE_PRESENT: YES/NO
VERIFIER_STRUCTURED_GUIDANCE_PRESENT: YES/NO
AGENT_TOOL_SETS_CHANGED: YES/NO
AGENT_AUTHORITY_BROADENED: YES/NO

QA_FIXTURE_CREATED: YES/NO
QA_FIXTURE_PATH: 
QA_REACHABLE_SCENARIO_COUNT: 
ACTIVE_STATE_COVERED: YES/NO
INACTIVE_STATE_COVERED: YES/NO
CONFLICTING_STATE_COVERED: YES/NO
UNRESOLVED_REFERENCE_TYPES_COVERED: 
MALFORMED_ROW_COVERED: YES/NO
OVERSIZED_RULE_COVERED: YES/NO
HISTORICAL_OR_UNKNOWN_PARSER_BEHAVIOR_ADDED: NO

COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_11_PASS: YES/NO
REPAIR_12_PASS: YES/NO
REPAIR_13_PASS: YES/NO
GOVERNANCE_PASS: YES/NO
CUSTOMIZATION_VALIDATION_PASS: YES/NO
TEST_REGISTRATION_PASS: YES/NO

FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_FAILURES: 
F1_UNCHANGED: YES/NO
F3_UNCHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
RUNTIME_QA_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

READY_FOR_GENUINELY_INDEPENDENT_REVIEW: YES/NO
READY_TO_BUMP_TO_0_3_146: NO
READY_TO_PACKAGE: NO
READY_TO_INSTALL: NO
READY_FOR_RUNTIME_QA: NO

Do not perform the independent review in this session.

End exactly with one:

RUNTIME_QA_SUPPORT_REPAIR_RESULT:
PASS_READY_FOR_GENUINELY_INDEPENDENT_REVIEW

RUNTIME_QA_SUPPORT_REPAIR_RESULT:
FAIL_VALIDATION

RUNTIME_QA_SUPPORT_REPAIR_RESULT:
FAIL_UNAUTHORIZED_CHANGE

RUNTIME_QA_SUPPORT_REPAIR_RESULT:
BLOCKED_IDENTITY_OR_WORKTREE_DRIFT

RUNTIME_QA_SUPPORT_REPAIR_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT

RUNTIME_QA_SUPPORT_REPAIR_RESULT:
BLOCKED_CHANGE_BOUNDARY_EXPANSION
