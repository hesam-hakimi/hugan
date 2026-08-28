TASK: HF1_V2_RESOLVE_RUNTIME_QA_SUPPORT_OWNER_DECISIONS

Continue the current task from the current worktree:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

The previous terminal result was:

RUNTIME_QA_SUPPORT_REPAIR_RESULT:
BLOCKED_CHANGE_BOUNDARY_EXPANSION

This prompt supplies the required owner decisions and narrowly expands the
authorized boundary.

Do not restart the implementation.
Do not revert or discard the valid existing Runtime QA support changes.
Re-verify the current worktree and continue from it.

Use the source-governance role:

etl-hotfix-implementer

Do not use any consumer-workspace Agent such as ETL Orchestrator, ETL
Implementer, or ETL Verifier as authority for modifying the extension source.

Do not run @etl /workflow.
Do not access or modify the Development Test Workspace.
Do not start Runtime QA in this task.

==================================================

1. IDENTITY AND CONCURRENCY GATE
    ==================================================

Required:

REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION:
0.3.145

Verify:

* exactly one effective repository target;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrent Agent is modifying the repository;
* the existing Runtime QA support edits are present;
* package.json and version remain unchanged;
* existing VSIX files remain unchanged.

Stop without edits on identity mismatch or concurrent mutation.

==================================================
2. NEW BASELINE REQUIREMENT

Capture a fresh task baseline before editing.

Use:

scripts/agent-governance/capture-baseline.mjs

plus an independent OS-level path, size, and SHA-256 snapshot.

Do not use git ls-files as the sole baseline authority.

The baseline must include protected and ignored assets when relevant, including:

* .claude/**;
* .github/** governance paths;
* scripts/agent-governance/**;
* root *.vsix files;
* package.json;
* src/test/testPatterns.ts;
* all current Runtime QA support changes.

Treat all valid changes present before this task as pre-existing baseline content.

Do not misclassify paths omitted by git ls-files as task changes.

==================================================
3. OWNER DECISION A — CONSUMER AGENT SOURCE

The canonical source for packaged consumer Agent definitions is:

src/customization/CopilotAssetCatalog.ts

The generated or synchronized consumer Agent resources are:

resources/copilot/agents/etl-orchestrator.agent.md
resources/copilot/agents/etl-verifier.agent.md

The existing byte-lock between the catalog and packaged resources is intentional
and must be preserved.

Authorize narrowly modifying, if required:

* src/customization/CopilotAssetCatalog.ts;
* resources/copilot/agents/etl-orchestrator.agent.md;
* resources/copilot/agents/etl-verifier.agent.md;
* the exact related asset synchronization tests only when necessary.

Do not relax, skip, delete, or weaken the byte-lock test.

Update the canonical catalog first and synchronize the two packaged resources
through the repository’s canonical generation or synchronization mechanism.

Add structured-result guidance so that:

ETL Orchestrator:

* preserves both the structured data part and rendered Markdown returned by
    public ETL read-only tools;
* does not discard the structured channel;
* passes both channels to delegated verification when Repair 13 parity or
    authority behavior is being assessed;
* distinguishes absent structured data from an empty valid structured result;
* reports missing channel coverage instead of fabricating parity.

ETL Verifier:

* independently compares structured and Markdown active-mapping IDs, order, and
    counts;
* validates excluded mappings and deterministic diagnostics in both channels;
* treats missing structured output as uncovered evidence, not PASS;
* reports declared-state or unresolved-reference coverage gaps explicitly.

These are guidance changes only.

Do not:

* add tools;
* remove tools;
* broaden tool access;
* change user-invocable;
* grant write, Preview, approval, installation, execution, or deployment
    authority;
* expose internal worker Agents to the consumer;
* change the rule that the user interacts only with ETL Orchestrator while
    internal Agents work through it.

Required:

ORCHESTRATOR_STRUCTURED_GUIDANCE_PRESENT: YES
VERIFIER_STRUCTURED_GUIDANCE_PRESENT: YES
AGENT_TOOL_SETS_CHANGED: NO
AGENT_AUTHORITY_BROADENED: NO
BYTE_LOCK_PRESERVED: YES

==================================================
4. OWNER DECISION B — MALFORMED/RAGGED ROWS

Malformed Field Mapping rows must fail closed before Runtime QA.

Inspect and identify the exact canonical bundle-parser path. Authorize modifying
only that parser and its directly relevant tests/fixtures.

When a recognized Field Mapping table row has a cell count inconsistent with its
header:

* emit the existing deterministic diagnostic:
    STTM_TABLE_MALFORMED;
* identify the affected row deterministically;
* do not admit that row into active mapping authority;
* do not silently truncate, pad, reinterpret, or accept it;
* preserve the structured diagnostic through the public data part;
* preserve an equivalent deterministic disclosure in Markdown;
* keep all valid neighboring rows unchanged.

Do not create a second malformed-table diagnostic when the existing
STTM_TABLE_MALFORMED contract applies.

Add focused tests proving:

* short row fails closed;
* oversized row fails closed;
* malformed row does not receive active authority;
* valid surrounding rows remain unchanged;
* structured and Markdown diagnostics agree;
* the full public EtlReadOnlyToolService.interpretSttm(...) seam is exercised.

Do not change Repair 11, Repair 12, or valid Repair 13 mapping-selection behavior.

==================================================
5. OWNER DECISION C — FT AND DECLARED STATES

FT-reference parsing is deferred to a separate post-hotfix parser capability.

Do not add:

* a new filters parser branch;
* a new canonical header;
* synthetic FT authority;
* a fabricated FT test path that the current public parser cannot reach.

For this Runtime QA cycle, classify FT as:

DEFERRED_PARSER_UNREACHABLE_NOT_REQUIRED_FOR_REPAIR_13_RUNTIME_QA

Likewise, do not broaden this task merely to introduce historical or unknown
input syntax when the current supported bundle format cannot express them.

The required Runtime QA fixture coverage for this hotfix is:

* active;
* inactive;
* conflicting;
* unresolved BR;
* unresolved TR;
* unresolved JC;
* unresolved ER;
* malformed short row;
* malformed oversized row;
* valid structured/Markdown dual-channel parity.

The following remain explicitly deferred and must be reported, not fabricated:

* FT parser support;
* historical input-state syntax;
* unknown input-state syntax.

==================================================
6. AUTHORIZED BOUNDARY

In addition to the already-present Runtime QA support paths, authorize only the
minimum necessary changes under:

* src/customization/CopilotAssetCatalog.ts;
* resources/copilot/agents/etl-orchestrator.agent.md;
* resources/copilot/agents/etl-verifier.agent.md;
* the exact canonical STTM Markdown bundle parser;
* directly related tests under src/test/**;
* existing synthetic Repair 13 QA fixture paths.

Do not modify:

* package.json;
* package version;
* package-lock.json;
* src/test/testPatterns.ts;
* tsconfig files;
* Repair 11 or Repair 12 behavior;
* Repair 13’s authoritative selector or correct renderer behavior;
* .claude/**;
* governance Agent definitions;
* existing VSIX files;
* QA workspace content.

Do not commit, push, tag, package, install, activate, Preview, approve, or write.

==================================================
7. VALIDATION

Run in a task-owned mirror whenever compilation or generated output could mutate
ignored live paths.

Run:

1. canonical catalog-to-resource byte-lock tests;
2. consumer Agent asset/frontmatter validation;
3. focused ETL Orchestrator guidance tests;
4. focused ETL Verifier guidance tests;
5. malformed short-row test;
6. malformed oversized-row test;
7. structured/Markdown diagnostic-parity tests;
8. public interpretSttm seam tests;
9. Repair 11 focused suite;
10. Repair 12 canonical suite;
11. Repair 13 focused suite;
12. Runtime QA synthetic-fixture suite;
13. governance tests;
14. customization validation;
15. test-registration validation;
16. compile;
17. compile:test;
18. lint;
19. canonical full unit suite.

Required:

* compile, compile:test, and lint: exit 0;
* Repair 11: pass;
* Repair 12: 21/21 pass;
* Repair 13: all tests pass;
* governance: all tests pass;
* package asset byte-lock: pass;
* F1 and F3: exact unchanged known failures only;
* new functional regressions: 0;
* new security regressions: 0.

Compare failures by exact identity, not aggregate counts.

==================================================
8. FINAL CHANGE-BOUNDARY PROOF

Compare final state with the new pre-edit baseline using both:

* repaired governance baseline/change-boundary tools;
* independent OS-level content hashing.

Report every task-attributable path.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
TEST_PATTERNS_CHANGED: NO
REPAIR_11_BEHAVIOR_CHANGED: NO
REPAIR_12_BEHAVIOR_CHANGED: NO
REPAIR_13_CORE_BEHAVIOR_CHANGED: NO
AGENT_TOOL_SETS_CHANGED: NO
AGENT_AUTHORITY_BROADENED: NO
EXISTING_VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

==================================================
9. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
CONCURRENT_AGENT_MUTATION: YES/NO
CANONICAL_BASELINE_CAPTURED: YES/NO
AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 

COPILOT_ASSET_CATALOG_UPDATED: YES/NO
ORCHESTRATOR_RESOURCE_SYNCHRONIZED: YES/NO
VERIFIER_RESOURCE_SYNCHRONIZED: YES/NO
BYTE_LOCK_PRESERVED: YES/NO
ORCHESTRATOR_STRUCTURED_GUIDANCE_PRESENT: YES/NO
VERIFIER_STRUCTURED_GUIDANCE_PRESENT: YES/NO
AGENT_TOOL_SETS_CHANGED: YES/NO
AGENT_AUTHORITY_BROADENED: YES/NO

MALFORMED_SHORT_ROW_FAILS_CLOSED: YES/NO
MALFORMED_OVERSIZED_ROW_FAILS_CLOSED: YES/NO
MALFORMED_ROW_ACTIVE_AUTHORITY: YES/NO
MALFORMED_DIAGNOSTIC_CODE: 
MALFORMED_DIAGNOSTIC_IN_BOTH_CHANNELS: YES/NO

FT_REFERENCE_STATUS:
DEFERRED_PARSER_UNREACHABLE_NOT_REQUIRED_FOR_REPAIR_13_RUNTIME_QA

HISTORICAL_STATE_STATUS: DEFERRED_UNSUPPORTED_INPUT_SYNTAX
UNKNOWN_STATE_STATUS: DEFERRED_UNSUPPORTED_INPUT_SYNTAX

REQUIRED_QA_SCENARIOS_PASSING: /
STRUCTURED_DATA_ROUNDTRIP_PASS: YES/NO
MARKDOWN_STRUCTURED_IDS_EQUAL: YES/NO
MARKDOWN_STRUCTURED_ORDER_EQUAL: YES/NO
MARKDOWN_STRUCTURED_COUNTS_EQUAL: YES/NO

COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_11_PASS: YES/NO
REPAIR_12_PASS: YES/NO
REPAIR_13_PASS: YES/NO
GOVERNANCE_PASS: YES/NO
FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_FAILURES: 
F1_UNCHANGED: YES/NO
F3_UNCHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

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

Do not perform the independent review in this chat.

End exactly with one:

RUNTIME_QA_SUPPORT_OWNER_DISPOSITION_RESULT:
PASS_READY_FOR_GENUINELY_INDEPENDENT_REVIEW

RUNTIME_QA_SUPPORT_OWNER_DISPOSITION_RESULT:
FAIL_VALIDATION

RUNTIME_QA_SUPPORT_OWNER_DISPOSITION_RESULT:
FAIL_UNAUTHORIZED_CHANGE

RUNTIME_QA_SUPPORT_OWNER_DISPOSITION_RESULT:
BLOCKED_IDENTITY_OR_CONCURRENT_MUTATION

RUNTIME_QA_SUPPORT_OWNER_DISPOSITION_RESULT:
BLOCKED_ADDITIONAL_OWNER_DECISION
