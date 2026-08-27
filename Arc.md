TASK: HF1_V2_RUNTIME_QA_REPAIR_13_USING_CONSUMER_AGENT_CONTRACT

Continue Runtime QA for the already installed and provisioned ETL Extension.

Installed extension expected:

* ID: td-etl.databricks-etl-copilot
* version: 0.3.145

Consumer workspace:

* use the currently open Development Test Workspace only;
* use the existing synthetic STTM:
    sttm/qa_hf1v2_demo_sttm.md;
* the workspace is already provisioned;
* do not invoke @etl /workflow;
* do not recreate or update Agents, Skills, Prompts, instructions, MCP
    configuration, or managed assets.

Architecture contract:

* ETL Orchestrator is the only user-facing Agent;
* internal Agents are intentionally user-invocable: false;
* use the agent delegation tool when specialist work is required;
* delegate independent interpretation verification to ETL Verifier;
* use ETL Runtime Troubleshooter only if interpretation or activation fails;
* do not invoke ETL Implementer or ETL Operator;
* ETL Evidence Researcher is unnecessary unless historical Confluence/Jira
    evidence is genuinely required.

Do not request PowerShell, shell commands, Git output, file hashes, or manually
generated JSON from the user. Those capabilities are not part of the installed
Consumer Agent contract.

Do not claim byte-for-byte workspace equality when no hashing tool exists.
For this Runtime QA, non-mutation evidence must be based on the complete tool
invocation record and the fact that no write, deployment, execution, approval,
or provisioning tool was invoked.

Perform these steps:

1. Call the installed ETL capabilities tool and verify that the active extension
    reports the expected ETL capability surface.
2. Read the existing synthetic STTM without modifying it.
3. Invoke the public read-only etl_interpret_sttm seam against exactly:
    sttm/qa_hf1v2_demo_sttm.md
4. Capture the complete consumer-visible result, including both:
    * structured data;
    * rendered Markdown.
5. Use the agent tool to delegate an independent read-only verification to
    ETL Verifier.
6. Require ETL Verifier to independently inspect the same STTM through its
    permitted read-only ETL tools and verify:
    * structured Active Mapping IDs equal Markdown Active Mapping IDs;
    * ID order is identical;
    * active-mapping counts agree;
    * authority is granted only by the declared positive active state;
    * conflicting mappings are excluded from active authority;
    * conflicting mappings are disclosed deterministically;
    * inactive mappings do not become blockers merely for being inactive;
    * historical, inactive, conflicting, unknown, or undeclared states never
        gain machine authority;
    * undeclared states fail closed;
    * unresolved authority-critical references remain non-authoritative and are
        disclosed;
    * no public write, approval, Preview, deployment, registration, or runtime
        authority was broadened.
7. Verify the complete list of tools invoked during this QA.

The following tools or operation classes are forbidden:

* etl_write_to_workspace;
* workflow installation or reprovisioning;
* ETL artifact implementation;
* Preview approval;
* DBFS publication;
* Databricks test execution;
* ADF pipeline execution;
* cluster start;
* job creation or update;
* file creation or modification;
* any Operator delegation;
* any external runtime side effect.

This is Preview-only read verification. Do not create a Preview if doing so
requires a write or managed asset creation.

If the QA STTM does not contain enough states to prove one of the required
Repair 13 behaviors, do not modify it and do not fabricate coverage. Report the
missing states exactly.

Return:

INSTALLED_EXTENSION_ID: 
INSTALLED_EXTENSION_VERSION: 
USER_FACING_AGENT: ETL Orchestrator
DELEGATED_AGENT: 
DELEGATION_SUCCEEDED: YES/NO

SELECTED_STTM_PATH: 
STRUCTURED_ACTIVE_MAPPING_IDS: 
MARKDOWN_ACTIVE_MAPPING_IDS: 
ACTIVE_MAPPING_IDS_EQUAL: YES/NO
ACTIVE_MAPPING_ORDER_EQUAL: YES/NO
ACTIVE_MAPPING_COUNTS_EQUAL: YES/NO

CONFLICTING_MAPPINGS_EXCLUDED: YES/NO
CONFLICT_DIAGNOSTICS_PRESENT: YES/NO
INACTIVE_MAPPING_CAUSES_BLOCKER: YES/NO
UNDECLARED_STATE_FAILS_CLOSED: YES/NO
UNRESOLVED_MAPPING_NON_AUTHORITATIVE: YES/NO
PUBLIC_MACHINE_AUTHORITY_BROADENED: YES/NO

TOOLS_INVOKED: 
WRITE_CAPABLE_TOOLS_INVOKED: 
RUNTIME_SIDE_EFFECT_TOOLS_INVOKED: 
WORKFLOW_REPROVISIONED: YES/NO
USER_COMMAND_EXECUTION_REQUESTED: YES/NO
QA_EVIDENCE_SCOPE: CONSUMER_TOOL_INVOCATION_AND_PUBLIC_RESULT

End exactly with one:

RUNTIME_QA_RESULT:
PASS_PREVIEW_ONLY_READY_FOR_EXPLICIT_WRITE_QA

RUNTIME_QA_RESULT:
FAIL_EXTENSION_ACTIVATION

RUNTIME_QA_RESULT:
FAIL_REPAIR_13_RUNTIME_BEHAVIOR

RUNTIME_QA_RESULT:
FAIL_INTERNAL_AGENT_DELEGATION

RUNTIME_QA_RESULT:
FAIL_FORBIDDEN_SIDE_EFFECT_TOOL

RUNTIME_QA_RESULT:
BLOCKED_QA_INPUT_COVERAGE
