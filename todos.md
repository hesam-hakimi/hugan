OWNER DECISION — ACCEPTANCE SCOPE RESOLVED

The intended architecture is now confirmed:

1. @etl /workflow is the provisioning path.
   It creates or updates the required agents and assets in the consumer
   environment.

2. etl_interpret_sttm is a separate read-only runtime LM tool.
   Copilot Agent invokes it to read STTM mappings and transformation logic and
   receive Markdown plus structured JSON.

Therefore:

CONTRACT_CLASSIFICATION: STANDALONE_PUBLIC_LM_TOOL_CONTRACT
WORKFLOW_STTM_INTEGRATION: NOT_REQUIRED_BY_DESIGN
PRODUCT_GAP: NO
PREVIOUS_ACCEPTANCE_ASSUMPTION: INCORRECT

Do not run the previous requirement-reconciliation task.
Do not change product routing or make @etl /workflow invoke etl_interpret_sttm.

Keep:

- exactly the existing four-file product diff;
- package version 0.3.147;
- no commit, push, package, install, VSIX, version bump, job, write, or deploy;
- F1 and F3 as the only approved quarantines;
- Failure 2 as an open unregistered blocker.

Update only the external %TEMP% F5 harness/runbook:

1. Remove @etl /workflow from Repair 13 structured-output acceptance.

2. Record it only as:

   WORKFLOW_PROVISIONING_PATH: OUT_OF_SCOPE_FOR_REPAIR_13
   WORKFLOW_CALLS_ETL_INTERPRET_STTM: NO_BY_DESIGN

3. Repair 13 F5 acceptance must test:

   A. DIRECT_LM_TOOL_PUBLIC_CONTRACT
      Invoke etl_interpret_sttm through the real VS Code public LM-tool API and
      inspect the resolved LanguageModelToolResult.

   B. COPILOT_AGENT_TOOL_INVOCATION
      From the isolated consumer QA workspace, invoke/reference
      etl_interpret_sttm through Copilot Agent mode using the synthetic Excel
      workbook.

4. Validate:

   - TextPart plus DataPart;
   - MIME application/json;
   - decoded non-null structured object;
   - exact mapping identity, order, affected-row, and diagnostic parity;
   - missing/null/primitive/malformed fail-closed behavior;
   - zero Preview mutation;
   - QA-workbook provenance;
   - unchanged repository diff.

5. Replace the global harnessDriven boolean with per-invocation correlation so a
   concurrent host invocation cannot be misclassified.

6. Label conditional-breakpoint response mutation only as:

   DIAGNOSTIC_FAULT_INJECTION

   Do not present it as natural end-to-end runtime evidence.

7. Record the full commit SHA and exact dirty-diff hash.

8. Give the owner one final numbered Desktop VS Code F5 runbook.
   Do not execute UI actions and do not claim Runtime PASS.

Required status before the owner executes F5:

CONTRACT_CLASSIFICATION: STANDALONE_PUBLIC_LM_TOOL_CONTRACT
WORKFLOW_PROVISIONING_PATH: OUT_OF_SCOPE_FOR_REPAIR_13
DIRECT_LM_TOOL_PUBLIC_CONTRACT: NOT_TESTED_ON_REAL_HOST
COPILOT_AGENT_TOOL_INVOCATION: NOT_TESTED_ON_REAL_HOST
REAL_HOST_F5_EXECUTED: NO
STRUCTURED_OUTPUT_RUNTIME_GATE: BLOCKED_NOT_EXECUTED
OVERALL_TASK_PR_GATE: BLOCKED_FAILURE_2
