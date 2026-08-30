TASK: HF1_V2_REQUIREMENT_TRACEABILITY_RECONCILIATION_BEFORE_F5

Accept the current BLOCKED result.

A newly proven architectural fact invalidates part of the previous acceptance:

- @etl /workflow does not invoke etl_interpret_sttm;
- it routes through openCopilotWorkflowManager and WorkflowCommandExecutor to
  vscode.commands.executeCommand;
- etl_interpret_sttm is a separately contributed Language Model tool;
- a Copilot/VS Code host may invoke that registered tool without any first-party
  product code calling vscode.lm.invokeTool.

Do not run F5 yet. This task is read-only requirement and call-path
reconciliation.

HARD CONSTRAINTS

- Preserve exactly these four existing product changes:
  - src/tools/index.ts
  - src/test/suite/sttmPublicToolResultEnvelope.test.ts
  - src/test/helpers/registerVscodeStub.ts
  - src/test/testPatterns.ts
- Keep version 0.3.147.
- Do not edit source, tests, package metadata, governance, documentation,
  prompts, or the external harness.
- Do not compile, run tests, run F5, invoke UI actions, or use debugger mutation.
- Do not commit, push, package, install, build VSIX, bump version, run jobs,
  approve writes, or deploy.
- F1 / ETL-TEST-DEBT-001 and F3 / ETL-TEST-DEBT-002 are the only approved
  quarantines.
- Failure 2, business-context.instructions.md missing a valid name, remains an
  unregistered blocker.

1. IMMUTABLE PRE-STATE

Record:

- full git HEAD;
- git status --short;
- exact changed paths;
- hash of the tracked dirty diff;
- package version.

Stop with STOP_UNEXPECTED_REPOSITORY_STATE if the state is not exactly the four
approved files at version 0.3.147.

2. REQUIREMENT–EVIDENCE LEDGER

Review the exact requirements available in this session, relevant repository
documentation, tests, package contributions, source comments, and git history.

Create a ledger for:

- Markdown plus structured STTM output;
- TextPart plus DataPart;
- application/json containing an object;
- mapping, order, affected-row, and diagnostic parity;
- missing/null/primitive/malformed fail-closed behavior;
- direct vscode.lm.invokeTool acceptance;
- Copilot/host-initiated tool invocation;
- @etl /workflow integration;
- synthetic Excel through @etl /workflow.

For every claim record:

- exact wording and source;
- provenance:
  USER_APPROVED_REQUIREMENT |
  REPOSITORY_CONTRACT |
  TEST_ONLY_EXPECTATION |
  AGENT_ADDED_ACCEPTANCE |
  INFERENCE;
- required consumer boundary;
- implementation evidence;
- verification level:
  STATIC_TRACE | UNIT_TEST | EXTENSION_HOST | INSTALLED_VSIX | NONE;
- status:
  PROVEN | PARTIAL | NOT_PROVEN | CONTRADICTED | DECISION_REQUIRED.

Do not promote an Agent-added acceptance step into a product requirement.

3. STATIC CALL-PATH MAPS

Provide exact file, symbol, and line references for:

A. @etl /workflow

Trace ETLChatParticipant through openCopilotWorkflowManager,
WorkflowCommandExecutor, vscode.commands.executeCommand, and its final
observable behavior.

B. etl_interpret_sttm

Trace:

- package contribution;
- activation and registration;
- handler invocation;
- Markdown construction;
- structured-result construction;
- LanguageModelToolResult return;
- every first-party repository caller, if any;
- every prompt/agent configuration exposing the tool;
- every production vscode.lm.invokeTool call site and the tool it invokes.

Explicitly distinguish:

- product code producing LanguageModelToolResult;
- a first-party consumer calling vscode.lm.invokeTool;
- Copilot/VS Code dynamically invoking a registered tool;
- @etl /workflow.

4. NEGATIVE-CASE RECONCILIATION

For missing, null, primitive, and malformed cases, identify existing natural
deterministic regression evidence.

Do not treat:

- a successfully parsed document with zero mappings as malformed output;
- conditional-breakpoint response mutation as release acceptance evidence.

Classify debugger mutation only as DIAGNOSTIC_FAULT_INJECTION.

5. CONTRACT CLASSIFICATION

Select exactly one classification based only on authoritative evidence:

A. STANDALONE_PUBLIC_LM_TOOL_CONTRACT
   etl_interpret_sttm must return Markdown plus structured data when invoked.
   @etl /workflow is a separate command and is not its consumer.

B. WORKFLOW_INTEGRATION_REQUIREMENT
   An authoritative requirement explicitly requires @etl /workflow to invoke
   or consume etl_interpret_sttm. The current four-file repair cannot satisfy it.

C. AMBIGUOUS_REQUIRES_OWNER_DECISION
   The authoritative evidence cannot resolve A versus B.

Do not select A because it is easier to test.
Do not select B solely because the previous F5 runbook assumed that path.

If A is supported, describe—but do not execute—the next F5 acceptance,
separating these fields:

- DIRECT_LM_TOOL_PUBLIC_CONTRACT
- COPILOT_AGENT_TOOL_INVOCATION
- COPILOT_CONSUMER_HANDLING
- WORKFLOW_COMMAND_PATH

@etl /workflow must not be used as structured-output evidence.

Also require the future harness to:

- use per-invocation correlation rather than a global harnessDriven boolean;
- record full SHA and exact diff hash;
- isolate/reset activation observations;
- label debugger mutation as fault injection;
- report repository-sample provenance as NOT_PROVEN unless the actual parser
  input path or complete I/O path is observed.

If B applies, report a separate implementation scope and stop.
If C applies, state the single exact owner decision required and stop.

6. POST-STATE

Re-record HEAD, status, changed paths, version, and diff hash.
Do not repair or revert anything automatically if it changed.

REQUIRED FINAL REPORT

REPOSITORY_DIFF_EXACTLY_FOUR_FILES: YES|NO
REPOSITORY_DIFF_UNCHANGED: YES|NO
PACKAGE_VERSION: <value>
AUTHORITATIVE_REQUIREMENT_FOUND: YES|PARTIAL|NO
CONTRACT_CLASSIFICATION:
  STANDALONE_PUBLIC_LM_TOOL_CONTRACT |
  WORKFLOW_INTEGRATION_REQUIREMENT |
  AMBIGUOUS_REQUIRES_OWNER_DECISION
WORKFLOW_CALLS_ETL_INTERPRET_STTM: YES|NO
WORKFLOW_CALLS_VSCODE_LM_INVOKETOOL: YES|NO
FIRST_PARTY_STTM_CONSUMER: <path/symbol>|NONE
HOST_MEDIATED_TOOL_SELECTION: POSSIBLE_NOT_RUNTIME_PROVEN|PROVEN|NOT_APPLICABLE
NEGATIVE_CASE_EVIDENCE: <per-class status>
CONTRADICTIONS_OR_UNTESTED_CLAIMS: <list>
OWNER_DECISION_REQUIRED: <exact question>|NONE
F5_AUTHORIZED: NO
REAL_HOST_F5_EXECUTED: NO
STRUCTURED_OUTPUT_RUNTIME_GATE: BLOCKED_NOT_EXECUTED
UNREGISTERED_FAILURE_2: OPEN
OVERALL_TASK_PR_GATE: BLOCKED_FAILURE_2
