TASK: HF1_V2_QA_PHASE_1_PREVIEW_ONLY

Continue HF1 V2 runtime QA using the installed Databricks ETL Copilot
extension version 0.3.140.

CURRENT QA STATE

- The current VS Code window has one disposable consumer workspace root.
- Expected workspace basename:
  etl-acz9999-hf1v2-qa
- Workflow setup has already completed successfully.
- The generated agents, skills, instructions, and supporting context files are
  already present.
- Databricks ETL Copilot 0.3.140 is activated.
- ETL Chat participant, read-only tools, action tools, and commands are
  registered.
- The synthetic QA STTM is:

  sttm/qa_hf1v2_demo_sttm.md

IMPORTANT

Do NOT run:

@etl /workflow create

again.

That workflow setup has already completed.

This phase tests the normal ETL job planning and preview flow after bootstrap.

Do NOT modify extension source.
Do NOT access or modify etl-framework-adb.
Do NOT access or modify any real consumer repository.
Do NOT commit or push.
Do NOT install or download dependencies.
Do NOT approve or execute a write during this phase.

==================================================
1. VERIFY RUNTIME AND WORKSPACE
==================================================

Confirm from live runtime evidence:

- installed and active extension version is exactly 0.3.140;
- 0.3.139 is not active;
- exactly one workspace folder is open;
- its basename is etl-acz9999-hf1v2-qa;
- this is a disposable QA workspace;
- no framework source or etl-framework-adb is present;
- workflow customization setup is already present;
- ETL Orchestrator and its required skills/tools are available.

If any prerequisite fails, stop with:

QA_PHASE_1_RESULT: BLOCKED

Do not modify anything.

==================================================
2. CAPTURE THE PREVIEW BASELINE
==================================================

Before starting ETL planning, capture a recursive workspace inventory containing:

- relative path;
- file size;
- SHA-256 for every existing file.

Include the currently generated:

- .github/**
- resources/copilot/context/**
- sttm/**
- .gitignore

Record the baseline file count and aggregate hash.

Do not modify any file while creating this baseline.

==================================================
3. INPUT AND CONTEXT DISCOVERY
==================================================

Use:

sttm/qa_hf1v2_demo_sttm.md

as the only STTM/business-mapping input.

Report:

- whether the STTM was discovered;
- whether it was parsed successfully;
- the detected source and target concepts;
- the detected columns/mappings;
- the requested output/write strategy, if present;
- any genuinely missing required information.

Do not invent missing business mappings.

If required information is genuinely absent, stop with:

QA_INPUT_REQUIRED: YES
QA_PHASE_1_RESULT: BLOCKED

List the exact questions required to continue.

Also report the exact context/knowledge files consumed during planning.

Do not add, replace, or upload new context files during this phase.

Record the following deferred observation without repairing it:

DEFERRED_DESIGN_FINDING:
CONTEXT_OWNERSHIP_AND_TRUST_BOUNDARY

==================================================
4. RUN THE NORMAL ETL JOB-PLANNING FLOW
==================================================

Use the installed ETL Orchestrator, skills, and runtime tools.

Do not invoke extension source directly.

Run the normal ETL job-planning flow for the supplied STTM.

The workflow must:

1. inspect the consumer workspace;
2. inspect the synthetic STTM;
3. inspect available packaged framework contracts/resources;
4. determine the workspace target classification;
5. determine the target decision;
6. determine the required ETL artifacts;
7. run validation/readiness checks;
8. produce an immutable preview manifest.

Do not force the target decision to CREATE_NEW_JOB.

Report the actual decision from runtime evidence as one of:

- CREATE_NEW_JOB
- UPDATE_EXISTING_REPO
- BLOCKED

Because workflow setup assets already exist, explain exactly why the runtime
selected its decision.

The key requirement is that the workspace must not be BLOCKED merely because
etl-framework-adb or framework source is absent.

==================================================
5. PREVIEW-ONLY SAFETY
==================================================

Generate the complete Preview.

The Preview report must include for every proposed artifact:

- relative path;
- artifact type;
- disposition:
  CREATE / MODIFY / UNCHANGED / CONFLICT / BLOCKED;
- content SHA-256;
- reason/evidence;
- whether it is writable;
- whether approval is required.

Confirm that all proposed destinations are contained within the current
disposable consumer root.

Do not request automatic approval.

Do not perform any filesystem write.

Stop at the point where explicit approval would normally be requested.

==================================================
6. VERIFY ZERO WRITES
==================================================

After the Preview has been generated, recapture the complete workspace
inventory and hashes.

Compare it with the Phase-1 baseline.

Required result:

- zero new files;
- zero deleted files;
- zero modified file bytes;
- `.github/**` unchanged;
- `resources/copilot/context/**` unchanged;
- STTM unchanged;
- no job_conf/** created;
- no env_conf/** created;
- no generated ETL artifact written.

A preview/log record held only in extension memory is acceptable.

A workspace file write is not acceptable.

==================================================
7. FRAMEWORK INDEPENDENCE
==================================================

Confirm that planning and Preview succeeded using packaged extension resources.

Required:

- no etl-framework-adb workspace;
- no framework-source checkout;
- no sibling framework repository;
- no manual frameworkRepositoryPath required;
- no source-root fallback used.

Report which packaged framework contract or provider-neutral contract was used.

Do not describe the ETL architecture as Oracle-only.

==================================================
8. STOP BEFORE APPROVAL
==================================================

Do not approve the Preview.

Do not call the write operation.

Do not create, modify, or delete artifacts.

Stop after presenting the immutable Preview ID and manifest.

==================================================
9. REQUIRED FINAL REPORT
==================================================

Return:

ACTIVE_EXTENSION_VERSION: <value>
WORKSPACE_ROOT: <absolute path>
WORKSPACE_ROOT_COUNT: <number>
WORKFLOW_SETUP_ALREADY_PRESENT: YES/NO
STTM_INPUT_FOUND: YES/NO
STTM_PARSED: YES/NO
CONTEXT_FILES_CONSUMED: <exact list>
TARGET_CLASSIFICATION: <value>
TARGET_DECISION: CREATE_NEW_JOB/UPDATE_EXISTING_REPO/BLOCKED
FRAMEWORK_SOURCE_REQUIRED: YES/NO
PACKAGED_CONTRACT_RESOLVED: YES/NO
PREVIEW_ID: <value or NONE>
PREVIEW_ARTIFACT_COUNT: <number>
PREVIEW_ARTIFACT_MANIFEST: <complete list>
PREVIEW_ZERO_NEW_FILES: YES/NO
PREVIEW_ZERO_MODIFIED_FILES: YES/NO
PREVIEW_ZERO_DELETED_FILES: YES/NO
PREVIEW_PATHS_INSIDE_CONSUMER_ROOT: YES/NO
EXPLICIT_APPROVAL_REQUIRED: YES/NO
WRITE_EXECUTED: NO
DEFERRED_CONTEXT_TRUST_FINDING_RECORDED: YES/NO

End exactly with one:

QA_PHASE_1_RESULT: PASS
QA_PHASE_1_RESULT: FAIL
QA_PHASE_1_RESULT: BLOCKED

PASS requires a real runtime Preview from the installed extension with a
Preview ID, complete artifact manifest, zero workspace writes, and explicit
approval still pending.

Do not convert static inspection into a runtime PASS.
Do not repair source code during this QA phase.
