TASK: HF1_V2_DIAGNOSE_REPAIR_13_PUBLIC_RESULT_AND_QA_FIXTURE_READ_ONLY

Perform a strictly read-only diagnosis of the remaining Repair 13 Runtime QA
blockers.

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Execution context:

* fresh Claude harness session;
* built-in generic claude Agent;
* Claude Opus 5 with Max reasoning;
* exactly one open workspace root;
* do not invoke repository Custom Agents;
* do not invoke ETL Orchestrator or any consumer Agent;
* do not run @etl /workflow.

The preceding consumer Runtime QA established:

* installed extension ID: td-etl.databricks-etl-copilot;
* installed and activated version: 0.3.145;
* 16/16 ETL tools available;
* user-facing Agent: ETL Orchestrator;
* delegation to ETL Verifier succeeded;
* etl_interpret_sttm returned six deterministic Mapping IDs in rendered
    Markdown;
* a separate structured payload was not exposed through the public consumer
    result;
* qa_hf1v2_demo_sttm.md did not contain the state-bearing negative scenarios
    required to exercise Repair 13;
* no Preview, approval, write, provisioning, or runtime side effect occurred;
* terminal result: BLOCKED_QA_INPUT_COVERAGE.

Treat these claims as evidence to verify against the current source.

This task is diagnosis and repair design only.

Make zero repository changes.

Do not compile, build, package, install, activate, run Runtime QA, create or edit
fixtures, regenerate baselines, modify test registration, change package.json,
change the version, create a VSIX, stage, stash, commit, push, reset, restore,
clean, or run @etl /workflow.

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

* exactly one workspace root;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* existing 0.3.145 VSIX protected;
* no concurrently mutating Agent.

Capture Git status and an OS-level hash inventory of all source, test, fixture,
governance, package, and VSIX paths relevant to this diagnosis.

Repeat the inventory at the end and require zero changes.

If inline command capture is unreliable, use task-owned helpers and redirected
output under the operating-system temporary directory. Do not modify the
repository to recover command execution.

Stop on identity mismatch, multiple workspace roots, staged files, concurrent
mutation, or unproven native command execution.

==================================================
2. TRACE THE COMPLETE etl_interpret_sttm RESULT PATH

Locate and inspect every stage involved in etl_interpret_sttm, including:

1. Tool declaration and input/output schema;
2. Tool registration;
3. public Tool invocation handler;
4. STTM parser;
5. EtlReadOnlyToolService.interpretSttm;
6. Repair 13 authoritative selector;
7. structured-result construction;
8. Markdown renderer;
9. conversion to the VS Code Language Model Tool result;
10. content-part serialization or response adapters;
11. consumer Agent instructions interpreting the Tool result;
12. Repair 13 source and public-seam tests;
13. applicable local VS Code API type declarations.

Determine whether the internal service returns an object equivalent to:

{
data: ,
markdown: 
}

For every boundary report:

* exact file;
* function or class;
* input type;
* output type;
* whether structured data exists;
* whether markdown exists;
* whether each value is retained, transformed, serialized, hidden, or dropped.

Identify the first exact boundary where structured data becomes unavailable to
the consumer Agent.

Distinguish among:

A. the service never creates structured data;
B. the service creates it but the Tool handler discards it;
C. the handler serializes only Markdown into a text content part;
D. VS Code’s public Tool API does not support a separate structured channel;
E. structured data is present but consumer Agent instructions fail to expose it;
F. the QA fixture lacks the state fields required to populate the evidence;
G. a combination of these causes.

Do not infer an API limitation from screenshots. Verify it against the installed
TypeScript declarations and current implementation.

Existing compiled out/** may be inspected as secondary evidence, but do not
regenerate it. Report any source/compiled parity uncertainty.

==================================================
3. VERIFY THE REPAIR 13 PUBLIC CONTRACT

Determine the intended consumer-visible contract for:

* structured Active Mapping IDs;
* Markdown Active Mapping IDs;
* deterministic ordering;
* active mapping count;
* excluded mappings;
* activeState;
* activeAuthority;
* conflict diagnostics;
* unresolved-reference diagnostics;
* undeclared-state fail-closed behavior.

Answer explicitly:

* Does the real public contract require a separate structured output channel?
* Could one Tool result envelope safely contain both structured JSON and Markdown?
* Does the current VS Code Tool API support that envelope?
* Should the consumer Agent compare two fields returned by one invocation?
* Is Runtime QA asking for a channel the public API cannot expose?
* Is the defect in the product service, Tool adapter, Agent instructions,
    Runtime QA contract, fixture coverage, or multiple layers?

Do not propose any write-capable or machine-authority expansion.

==================================================
4. DESIGN THE STATE-BEARING QA FIXTURE

Inspect:

* qa_hf1v2_demo_sttm.md;
* the STTM parser contract;
* Repair 11, Repair 12, and Repair 13 tests;
* all declared SttmActiveState values;
* conflict detection;
* BR/TR/JC/ER/FT reference parsing and resolution.

Design—but do not create—one deterministic synthetic QA fixture covering:

1. valid explicitly active mapping;
2. valid explicitly inactive mapping;
3. historical mapping;
4. two mappings forming one deterministic conflict;
5. unknown or unsupported state literal;
6. blank or undeclared value in a recognized state column;
7. unresolved authority-critical BR reference;
8. unresolved authority-critical TR reference;
9. unresolved authority-critical JC reference;
10. unresolved authority-critical ER reference;
11. unresolved authority-critical FT reference;
12. ordinary state-less mapping, if supported, to distinguish legacy state-less
    semantics from a blank recognized state value.

Derive every column, literal, reference pattern, and identifier from the current
parser. Do not invent an STTM format.

For every scenario return:

* scenario ID;
* proposed Mapping ID;
* exact relevant STTM fields and values;
* parser-recognized state;
* expected structured Active Mapping inclusion;
* expected Markdown Active Mapping inclusion;
* expected excluded-mapping record;
* expected diagnostic code;
* blocker or non-blocker behavior;
* expected activeAuthority;
* expected fail-closed behavior.

The proposed fixture must:

* contain only synthetic data;
* avoid real jobs, credentials, systems, and data;
* be safe for the Development Test Workspace;
* use the read-only etl_interpret_sttm public surface;
* require no Preview or write;
* preserve Repair 12 behavior;
* enable exact structured/Markdown ID, count, and order comparison;
* avoid duplicate Mapping IDs and accidental scenario overlap.

Recommend its exact future consumer-workspace path, but do not create it.

==================================================
5. MINIMAL FUTURE REPAIR DESIGN

If a source change is required, return the smallest bounded repair design.

Separate findings into:

A. public-result adapter repair;
B. consumer Agent instruction repair;
C. QA fixture addition;
D. Runtime QA prompt correction;
E. findings requiring no code change.

For each proposed changed path provide:

* exact repository-relative path;
* exact defect;
* intended change;
* required tests;
* protected invariants;
* whether a future version 0.3.146 would be required;
* stop conditions.

Do not implement anything in this session.

Do not authorize version bump, packaging, installation, or Runtime QA.

==================================================
6. FINAL NON-MUTATION PROOF

Compare the final repository inventory with the initial inventory.

Required:

REPOSITORY_PATHS_CHANGED_BY_DIAGNOSIS: 0
STAGED_FILES: 0
STASH_ENTRIES: 0
PACKAGE_JSON_CHANGED: NO
SOURCE_VERSION_CHANGED: NO
REPAIR_13_CONTENT_CHANGED: NO
CONSUMER_TEMPLATES_CHANGED: NO
GOVERNANCE_ASSETS_CHANGED: NO
VSIX_CHANGED: NO
CONSUMER_WORKSPACE_TOUCHED: NO
RUNTIME_QA_STARTED: NO
WORKFLOW_PROVISIONED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

==================================================
7. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
WORKSPACE_ROOT_COUNT: 
REPOSITORY_MUTATED_BY_DIAGNOSIS: YES/NO

INTERNAL_SERVICE_RETURNS_DATA: YES/NO
INTERNAL_SERVICE_RETURNS_MARKDOWN: YES/NO
TOOL_HANDLER_RECEIVES_BOTH: YES/NO
PUBLIC_TOOL_EXPOSES_STRUCTURED_DATA: YES/NO
PUBLIC_TOOL_EXPOSES_MARKDOWN: YES/NO

STRUCTURED_PAYLOAD_FIRST_LOSS_BOUNDARY:
<exact path, function, conversion, and evidence>

VS_CODE_API_SUPPORTS_SEPARATE_STRUCTURED_CHANNEL: YES/NO
SERIALIZED_DUAL_CHANNEL_ENVELOPE_SUPPORTED: YES/NO
CURRENT_PUBLIC_CONTRACT_REQUIRES_SEPARATE_STRUCTURED_CHANNEL: YES/NO

ROOT_CAUSE_CLASSIFICATION:
<INTERNAL_SERVICE_DEFECT /
TOOL_ADAPTER_DEFECT /
PLATFORM_API_LIMITATION /
AGENT_INSTRUCTION_DEFECT /
QA_CONTRACT_DEFECT /
FIXTURE_COVERAGE_DEFECT /
COMBINATION>

CURRENT_RUNTIME_QA_RESULT_IS_PRODUCT_BEHAVIOR_FAILURE: YES/NO
CURRENT_RUNTIME_QA_RESULT_IS_EVIDENCE_COVERAGE_FAILURE: YES/NO

DECLARED_STATE_VALUES: 
PROPOSED_QA_FIXTURE_PATH: 
PROPOSED_QA_SCENARIO_COUNT: 
PROPOSED_QA_SCENARIO_MATRIX: 
ALL_REQUIRED_NEGATIVE_STATES_COVERED: YES/NO
ALL_AUTHORITY_CRITICAL_REFERENCE_TYPES_COVERED: YES/NO

SOURCE_REPAIR_REQUIRED: YES/NO
CONSUMER_AGENT_INSTRUCTION_REPAIR_REQUIRED: YES/NO
QA_FIXTURE_REQUIRED: YES/NO
RUNTIME_QA_PROMPT_CORRECTION_REQUIRED: YES/NO
MINIMAL_FUTURE_AUTHORIZED_PATHS: 
NEXT_VERSION_IF_SOURCE_REPAIR_IS_APPROVED: <0.3.146 or N/A>

End exactly with one:

RUNTIME_QA_DIAGNOSTIC_RESULT:
READY_FOR_BOUNDED_PUBLIC_SEAM_AND_FIXTURE_REPAIR

RUNTIME_QA_DIAGNOSTIC_RESULT:
READY_FOR_QA_FIXTURE_ONLY

RUNTIME_QA_DIAGNOSTIC_RESULT:
READY_FOR_RUNTIME_QA_CONTRACT_CORRECTION_ONLY

RUNTIME_QA_DIAGNOSTIC_RESULT:
NO_DEFECT_FOUND_CURRENT_CONTRACT_ALREADY_TESTABLE

RUNTIME_QA_DIAGNOSTIC_RESULT:
BLOCKED_IDENTITY_OR_WORKTREE_DRIFT

RUNTIME_QA_DIAGNOSTIC_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT

RUNTIME_QA_DIAGNOSTIC_RESULT:
FAIL_SOURCE_TRACE_INCONCLUSIVE
