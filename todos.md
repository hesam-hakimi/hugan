TASK: HF1 V2 RUNTIME QA — CORRECT FRESH-CONSUMER ENTRY POINT

Continue QA in the current sole disposable workspace:

C:\Users\tag5916\AppData\Local\Temp\hf1-v2-qa-consumer-03140

The installed and activated extension is Databricks ETL Copilot 0.3.140.

IMPORTANT CORRECTION

The previous command:

@etl /workflow create

was routed to:

Copilot workflow manager — action=setup

That command manages consumer workflow customization and is NOT the
fresh ETL job-generation entry point.

It correctly blocked because this completely empty directory has none of the
workflow-target markers:

- job_conf/
- env_conf/
- sttm/
- EDP.yml
- CD.yml
- managed ETL Copilot instructions

Do not classify that result as an HF1 product failure.

Do not rerun `/workflow create` as the fresh-consumer test.

==================================================
1. VERIFY THE CURRENT ENVIRONMENT
==================================================

Confirm from live runtime evidence:

- this directory is the only workspace root;
- Databricks ETL Copilot 0.3.140 is active;
- 0.3.139 is not active;
- this workspace is disposable and contains no real project data;
- no framework source or etl-framework-adb is present.

If any prerequisite fails, return QA_RESULT: BLOCKED.

==================================================
2. IDENTIFY THE REAL ETL JOB-CREATION ENTRY POINT
==================================================

Inspect only the installed extension’s registered commands, chat participant
commands, help output, and packaged runtime metadata.

Identify the normal end-user entry point for creating a new ETL job from an
STTM or equivalent input.

Do not guess the command.

Do not use extension source checkout code.

Explicitly report the distinction between:

A. fresh ETL job creation;
B. `/workflow create` customization setup.

If no job-generation entry point is exposed by the installed extension,
return:

FRESH_JOB_ENTRYPOINT_AVAILABLE: NO
QA_RESULT: FAIL

with the exact command-registration evidence.

==================================================
3. PREPARE MINIMUM SYNTHETIC INPUT
==================================================

Preserve evidence that the consumer workspace began empty.

Then prepare only the minimum non-production test input required by the
documented fresh-job flow.

Preferred form:

sttm/<synthetic-test-STTM>

Use only:

- a documented packaged sample; or
- a user-supplied synthetic/sanitized STTM; or
- a minimal fixture whose structure is explicitly defined by the installed
  extension contract.

Do not copy real production data.

Do not invent undocumented business mappings merely to force the workflow to
continue.

If a valid synthetic STTM is not available, stop with:

TEST_INPUT_REQUIRED: YES
QA_RESULT: BLOCKED

and describe the exact supported file type and minimum fields required.

Do not create job_conf/, env_conf/, EDP.yml, CD.yml, or .github/** merely to
trick workspace classification.

==================================================
4. EXECUTE THE FRESH-CONSUMER JOB FLOW
==================================================

Using the actual installed-extension job-generation command:

1. select/read the synthetic STTM;
2. classify the sole workspace as a fresh consumer;
3. produce the intended ETL artifact preview;
4. confirm preview writes zero files;
5. record every previewed path and content hash;
6. reject/cancel once and prove zero files are written;
7. generate a fresh preview;
8. explicitly approve it;
9. confirm the write succeeds;
10. confirm the actual paths and bytes match the approved preview;
11. confirm the target decision is CREATE_NEW_JOB;
12. confirm no write occurs outside the disposable workspace;
13. confirm no framework-source checkout or etl-framework-adb is required.

Do not assume Oracle, TIBCO, Data Lake, Synapse, or another destination unless
the synthetic fixture explicitly exercises it.

==================================================
5. APPROVAL AND SECURITY CHECKS
==================================================

Verify at runtime:

- the first request is preview-only;
- approval is explicit;
- rejected approval writes zero files;
- approved authorization is one-time;
- replay is rejected;
- changing content or path requires a new preview;
- traversal and absolute escapes are rejected;
- sibling-root escape is rejected;
- junction/symlink/reparse escape is rejected where supported;
- physical containment is checked immediately before mutation.

Do not weaken validation to produce a PASS.

==================================================
6. SEPARATE WORKFLOW-SETUP SCENARIO
==================================================

Only after the fresh ETL job flow has completed or the workspace has become a
verified ETL consumer workspace, test:

@etl /workflow create

Treat this as a separate customization scenario.

Expected behavior:

- target resolves as an end-user ETL workspace;
- proposed `.github/agents/**` assets are shown in a preview;
- no workflow asset is created before approval;
- rejection produces zero workflow files;
- approval creates only the previewed workflow assets;
- all output remains inside this disposable consumer workspace.

In this disposable workspace, `.github/agents/**` is an allowed consumer
workflow output after explicit approval.

Do not modify `.github/**` in the extension source repository or any real
consumer repository.

==================================================
7. FINAL REPORT
==================================================

Return:

FRESH_JOB_ENTRYPOINT_IDENTIFIED: PASS/FAIL/BLOCKED
SYNTHETIC_STTM_AVAILABLE: PASS/FAIL/BLOCKED
EMPTY_WORKSPACE_START_CONFIRMED: PASS/FAIL/BLOCKED
FRESH_CONSUMER_CLASSIFIED: PASS/FAIL/BLOCKED
TARGET_DECISION_CREATE_NEW_JOB: PASS/FAIL/BLOCKED
PREVIEW_ZERO_WRITES: PASS/FAIL/BLOCKED
EXPLICIT_APPROVAL_REQUIRED: PASS/FAIL/BLOCKED
REJECTED_APPROVAL_ZERO_WRITES: PASS/FAIL/BLOCKED
APPROVED_WRITE_SUCCESS: PASS/FAIL/BLOCKED
WRITE_PATH_EQUALS_PREVIEW: PASS/FAIL/BLOCKED
WRITE_CONTENT_EQUALS_APPROVED_MANIFEST: PASS/FAIL/BLOCKED
APPROVAL_REPLAY_BLOCKED: PASS/FAIL/BLOCKED
PHYSICAL_CONTAINMENT_RUNTIME_SAFE: PASS/FAIL/BLOCKED
NO_WRITE_OUTSIDE_CONSUMER_ROOT: PASS/FAIL/BLOCKED
FRAMEWORK_SOURCE_NOT_REQUIRED: PASS/FAIL/BLOCKED
WORKFLOW_SETUP_TARGET_VERIFIED: PASS/FAIL/BLOCKED
WORKFLOW_SETUP_PREVIEW_ONLY_BEFORE_APPROVAL: PASS/FAIL/BLOCKED
WORKFLOW_SETUP_APPROVED_WRITE_SUCCESS: PASS/FAIL/BLOCKED
NEW_FUNCTIONAL_REGRESSIONS: YES/NO/BLOCKED
HF1_SECURITY_REGRESSIONS: YES/NO/BLOCKED

Conclude exactly one:

QA_RESULT: PASS
QA_RESULT: FAIL
QA_RESULT: BLOCKED

PASS requires the fresh-job flow and the separately identified workflow-setup
flow to have actually executed.

Do not convert static inspection into a runtime PASS.
Do not repair product source during this QA task.
