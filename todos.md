TASK: HF1_V2_COMPLETE_RUNTIME_QA_STRUCTURED_DIAGNOSTICS_AND_REFRESH_PHASE_H_BASELINE

Continue from the current worktree in:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

The previous result was:

RUNTIME_QA_SUPPORT_OWNER_DISPOSITION_RESULT:
BLOCKED_ADDITIONAL_OWNER_DECISION

This prompt supplies the two remaining owner decisions.

Do not restart, revert, or discard the valid existing Runtime QA support work.

Use:

etl-hotfix-implementer

This remains extension-source implementation work. Do not use consumer Agents as
authority for modifying the extension.

==================================================

1. REQUIRED IDENTITY
    ==================================================

Verify:

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

Required:

* one effective repository target;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* no concurrent Agent mutation;
* current Runtime QA support changes preserved.

Capture a new pre-edit baseline using:

* scripts/agent-governance/capture-baseline.mjs;
* an independent OS-level path, byte-size, and SHA-256 snapshot.

Do not rely on git ls-files alone.

==================================================
2. OWNER DECISION OD-STRUCT-1

The malformed-row diagnostic must be exposed through the public structured data
part as well as Markdown.

Authorize narrowly modifying:

* src/core/sttm/SttmResolvedEvidence.ts;
* src/tools/EtlReadOnlyToolService.ts;
* src/core/sttm/SttmMarkdownBundleParser.ts only if necessary to propagate the
    existing diagnostic;
* directly relevant focused tests and synthetic Repair 13 QA fixture files.

Inspect the current types before editing.

Implement one minimal, backward-compatible structured parser-diagnostic channel.

Prefer a dedicated optional parser-diagnostics collection rather than treating a
parser error as an unrelated projection diagnostic.

Requirements:

* reuse the existing canonical diagnostic code:
    STTM_TABLE_MALFORMED;
* do not create a duplicate diagnostic vocabulary;
* preserve the deterministic malformed row identity;
* include sufficient structured evidence to identify the affected table and row;
* malformed short and oversized rows must receive no active authority;
* valid neighboring rows remain unchanged;
* Markdown and structured output must disclose the same malformed-row event;
* existing consumers that do not inspect the new optional field must continue to
    work;
* do not broaden machine authority;
* do not add write, approval, Preview, installation, execution, or deployment
    behavior.

Do not change the correct Repair 13 positive authority selector.

Add focused tests through the full public seam:

EtlReadOnlyToolService.interpretSttm(…) -> { markdown, data }

Prove:

* structured malformed diagnostic present;
* Markdown malformed diagnostic present;
* diagnostic codes and affected row identities agree;
* malformed row absent from active mappings;
* valid active mappings and order remain equal across both channels;
* absence of parser diagnostics is represented honestly for a valid document.

==================================================
3. OWNER DECISION OD-EVAL-1

A legitimate tracked parser change necessarily invalidates the committed Phase H
golden baseline. A controlled golden refresh is authorized.

Authorize modifying only the canonical Phase H baseline artifacts produced by the
repository’s existing generator, expected to include:

* docs/eval/phase_h_latest_report.json;
* docs/eval/phase_h_latest_report.md.

Before refreshing the live baseline:

1. Run the canonical generator in two independent task-owned temporary mirrors.
2. Prove the only tracked-input changes are the authorized Runtime QA support
    source changes.
3. Compare both generated results semantically.
4. Ignore only explicitly documented volatile fields such as generation timestamp
    and measured latency.
5. Require identical:
    * tracked-input digest;
    * scenario set;
    * scenario outcomes;
    * acceptance/parity/validation rates;
    * failure identities;
    * coverage semantics.
6. Confirm the negative drift test still fails against a deliberately stale
    baseline.
7. Confirm no assertion, threshold, scenario, or tracked-input pattern was
    weakened.

Only after these gates pass, run the canonical generator once against the live
repository to refresh the two authorized baseline files.

Do not hand-edit either report.

After refresh, require both previously failing EvalGating tests to pass:

* passes against the committed Phase H baseline report;
* allows deterministic v3 baseline reports without prompt telemetry.

If the two isolated generations differ semantically, do not update the live
baseline and stop with BLOCKED_NONDETERMINISTIC_BASELINE_GENERATION.

==================================================
4. GENERATED CONSUMER AGENT RESOURCES

Preserve the already synchronized consumer resources:

* resources/copilot/agents/etl-orchestrator.agent.md;
* resources/copilot/agents/etl-verifier.agent.md.

Do not modify their tools, delegation lists, user visibility, or authority.

The package asset byte-lock must continue to pass.

The two previously reported CONTROL_PLANE_PATH_CHANGED findings must be
reported honestly.

Do not modify the governance manifest or validators in this task merely to hide
those findings.

The later independent reviewer must determine whether regeneration provenance is
sufficient or whether a separate governance repair is required.

==================================================
5. DEFERRED CAPABILITIES

Keep these decisions unchanged:

FT_REFERENCE_STATUS:
DEFERRED_PARSER_UNREACHABLE_NOT_REQUIRED_FOR_REPAIR_13_RUNTIME_QA

HISTORICAL_STATE_STATUS:
DEFERRED_UNSUPPORTED_INPUT_SYNTAX

UNKNOWN_STATE_STATUS:
DEFERRED_UNSUPPORTED_INPUT_SYNTAX

Do not add a filters branch, new header, fabricated FT authority, historical
syntax, or unknown-state syntax.

==================================================
6. PROTECTED BOUNDARIES

Do not modify:

* package.json;
* package version;
* package-lock.json;
* src/test/testPatterns.ts;
* tsconfig files;
* Repair 11 behavior;
* Repair 12 behavior;
* Repair 13 positive authority-selection behavior;
* .claude/**;
* governance Agent definitions;
* existing VSIX files;
* Development Test Workspace.

Do not:

* build or install a VSIX;
* start Runtime QA;
* invoke @etl /workflow;
* create Preview;
* approve or execute Write;
* commit, push, tag, stage, stash, reset, restore, or clean.

==================================================
7. VALIDATION

Run all write-producing validation in a task-owned mirror except for the one
explicitly authorized live golden-baseline refresh.

Run:

1. structured parser-diagnostic tests;
2. Markdown/structured diagnostic parity tests;
3. malformed short-row tests;
4. malformed oversized-row tests;
5. full public interpretSttm seam tests;
6. consumer Agent package byte-lock tests;
7. Phase H golden generator twice in separate mirrors;
8. Phase H negative stale-baseline test;
9. both EvalGating tests;
10. Repair 11 focused suite;
11. Repair 12 canonical suite;
12. Repair 13 focused suite;
13. Runtime QA support fixture suite;
14. governance tests;
15. customization validation;
16. test-registration validation;
17. compile;
18. compile:test;
19. lint;
20. canonical full unit suite.

Required:

* compile, compile:test, and lint: exit 0;
* Repair 11: pass;
* Repair 12: 21/21 pass;
* Repair 13: all pass;
* Phase H eval gate: pass;
* package asset byte-lock: pass;
* F1 and F3 remain the only known full-suite failures;
* both former EvalGating failures are resolved;
* every new passing-count change is reconciled to added tests or resolved
    EvalGating tests;
* new functional regressions: 0;
* new security regressions: 0.

Compare failures by exact identity, not only aggregate counts.

==================================================
8. FINAL CHANGE-BOUNDARY PROOF

Compare final state against the new pre-edit baseline using both governance tools
and independent OS hashing.

Report every changed path and distinguish:

* pre-existing Runtime QA support changes;
* changes attributable to this task;
* generated Phase H artifacts;
* unexpected or unauthorized changes.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
TEST_PATTERNS_CHANGED: NO
REPAIR_11_BEHAVIOR_CHANGED: NO
REPAIR_12_BEHAVIOR_CHANGED: NO
REPAIR_13_AUTHORITY_SELECTION_CHANGED: NO
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

PUBLIC_STRUCTURED_PARSER_DIAGNOSTIC_CHANNEL_PRESENT: YES/NO
STRUCTURED_MALFORMED_DIAGNOSTIC_PRESENT: YES/NO
MARKDOWN_MALFORMED_DIAGNOSTIC_PRESENT: YES/NO
DIAGNOSTIC_CODES_EQUAL: YES/NO
DIAGNOSTIC_ROW_IDENTITIES_EQUAL: YES/NO
MALFORMED_ROW_ACTIVE_AUTHORITY: YES/NO
VALID_MAPPING_IDS_AND_ORDER_PRESERVED: YES/NO
PUBLIC_INTERPRET_STTM_SEAM_TESTED: YES/NO

PHASE_H_TRACKED_INPUT_DRIFT_PROVEN: YES/NO
ISOLATED_GOLDEN_GENERATION_COUNT: 
ISOLATED_GENERATIONS_SEMANTICALLY_EQUAL: YES/NO
GOLDEN_BASELINE_REFRESHED_CANONICALLY: YES/NO
GOLDEN_BASELINE_HAND_EDITED: NO
NEGATIVE_STALE_BASELINE_TEST_PASS: YES/NO
PHASE_H_EVAL_PASS: YES/NO
EVAL_ASSERTIONS_OR_THRESHOLDS_WEAKENED: YES/NO

PACKAGE_ASSET_BYTE_LOCK_PASS: YES/NO
ORCHESTRATOR_STRUCTURED_GUIDANCE_PRESERVED: YES/NO
VERIFIER_STRUCTURED_GUIDANCE_PRESERVED: YES/NO
CONTROL_PLANE_PATH_CHANGED_FINDINGS: 

FT_REFERENCE_STATUS:
DEFERRED_PARSER_UNREACHABLE_NOT_REQUIRED_FOR_REPAIR_13_RUNTIME_QA

HISTORICAL_STATE_STATUS:
DEFERRED_UNSUPPORTED_INPUT_SYNTAX

UNKNOWN_STATE_STATUS:
DEFERRED_UNSUPPORTED_INPUT_SYNTAX

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
FULL_UNIT_COUNT_DELTA_RECONCILED: YES/NO
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

Do not perform independent review in this chat.

End exactly with one:

RUNTIME_QA_STRUCTURED_DIAGNOSTICS_RESULT:
PASS_READY_FOR_GENUINELY_INDEPENDENT_REVIEW

RUNTIME_QA_STRUCTURED_DIAGNOSTICS_RESULT:
FAIL_VALIDATION

RUNTIME_QA_STRUCTURED_DIAGNOSTICS_RESULT:
FAIL_UNAUTHORIZED_CHANGE

RUNTIME_QA_STRUCTURED_DIAGNOSTICS_RESULT:
BLOCKED_IDENTITY_OR_CONCURRENT_MUTATION

RUNTIME_QA_STRUCTURED_DIAGNOSTICS_RESULT:
BLOCKED_NONDETERMINISTIC_BASELINE_GENERATION

RUNTIME_QA_STRUCTURED_DIAGNOSTICS_RESULT:
BLOCKED_ADDITIONAL_OWNER_DECISION
