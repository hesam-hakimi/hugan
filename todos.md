TASK_ID: ETL-0909-PRODUCT-WRITE-EVIDENCE01
TYPE: BOUNDED EVIDENCE INTAKE AND RECORD CORRECTION

ENVIRONMENT AND LANGUAGE
Use one ordinary LOCAL Windows VS Code Agent.
Use English for all conversation and artifacts.

Expected development repository:
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

OBJECTIVE
Prepare a concrete, evidence-backed next task for the original consumer
file-write defect.

The latest independent review:
  ETL-0909-PROTOCOL3-RUNTIME-INDEPENDENT-REVIEW01
accepted the build/promotion/manifest relationship and nominal protocol-3
focused runtime with limitations.

Do not reopen that accepted scenario or rerun its build, tests or Host.
Unexecuted fault branches remain unqualified; they are not prerequisites
for collecting the original write-defect evidence.

Also address the review's four record findings in this same task.
Do not create a separate engineering cycle for these corrections.

AUTHORITY
Allowed:
- Bounded read-only inspection of existing evidence and relevant source.
- Read-only analysis helpers.
- Copying specifically identified evidence into a new external task directory.
- Corrected report/result derivatives and a concise defect-intake record.

Not allowed:
- Repository source, configuration or generated-output changes.
- Compiler, tests, runner, producer, Host or product execution.
- Reproducing a write by executing it.
- Consumer-workspace mutation.
- Dependency installation, Git mutation, packaging or release.
- Editing prior evidence, reference state, changelog or frozen briefs.

This prompt does not authorize a future guarded-write operation.
That approval must identify the actual temporary workspace and exact write set.

READ AND RESOLVE
Read this entire prompt and the complete latest runtime independent review.

Resolve its bundle through bounded direct-child discovery:
  C:\docs\ETL-0909-PROTOCOL3-RUNTIME-INDEPENDENT-REVIEW01-*

Select by machine task identity and reviewed-task relationships, not recency.
Follow its recorded path to:
  ETL-0909-PROTOCOL3-FOCUSED-RUNTIME01

Read the relevant original report, result, correction records, run status,
inventory, preserved runner evidence and the four findings R-1 through R-4.

Use current reference pointers where accessible. Their previously reported
absence does not require recreating the reference pack for this task.

Do not recursively search C:\docs, user profiles, chat storage, Local History,
or unrelated workspaces. Never derive expected hashes from photographs.

Create one exclusive external directory:
  C:\docs\ETL-0909-PRODUCT-WRITE-EVIDENCE01-<UTC>-<GUID>

Keep all new artifacts there. Preserve original records byte-for-byte.

PART A — CORRECT THE RECORD WITHOUT REWRITING HISTORY

R-1: Host-log retention
The reviewed report claimed three logs were copied into logs/host/, but the
directory was empty. The reviewer authenticated 25 logs still in RUN_ROOT
against the retained runner evidence.

Resolve only those explicitly recorded log paths.
If they still exist and match their recorded hashes, copy the recorded logs
into this new task directory and verify each copy.

Do not copy a whole profile or arbitrary RUN_ROOT contents.
Do not modify or delete originals.

Clearly distinguish:
- Logs that were absent from the original evidence bundle.
- Logs newly preserved by this task.
- Any logs now unavailable or mismatched.

If unavailable, correct the retention claim and report the durability gap.
Do not regenerate logs or rerun the Host.

R-2: Residual declaredCoverage and explanation
Create a corrected derivative of RUNTIME01 result.json and a correction map.
Cover every affected field identified by the reviewer, including:

  runtimeAssessment.compositionEvidence
    .bindComparisonProvenance.declaredCoverage

Authenticate the correct values from retained evidence:
- 49 focused-suite comparison records.
- 124 derived Host-evidence rows forming the runner's declared prefix.
- 40 runner-owned measurements.
- 164 total runner comparisons.

Correct the explanation that incorrectly describes the 49 suite records as
the rows directly bound by runner provenance. They are inputs consumed by
buildHostEvidenceComparisons; the derived prefix is 124 rows.

Identify the affected notes and superseded fields precisely.
Do not perform a global replacement of 49; that value remains correct for
the focused suite's own records.

Leave the original assessment and result files unchanged.

R-3: Narrative timestamps
Use exact timestamps from run-status.json and the original machine result
in the corrected report derivative. Do not manually copy them from images.

R-4: Inventory omission
Account for the omitted result-emit-stdout.txt and the original inventory's
documented self-exclusion.

Publish an explicit supplemental entry or corrected derivative index.
Finalize this task's own inventory after its artifacts are written, with
self-exclusions clearly stated.

Produce corrected report/result derivatives linked to the original identities
and this review. Label them as later corrections, not original run artifacts.
Do not present the original inconsistent fields as current facts.

Verify these corrections directly. No compiler, test run, full historical
audit or new independent code-review gate is needed solely for them.

PART B — COLLECT THE ORIGINAL WRITE-DEFECT EVIDENCE

Use already-visible owner context and exact evidence locators explicitly
identified in the current references or supplied reports.

Do not substitute the synthetic STTM read-only fixture for the original
write-failure scenario.

Collect the following, recording each source and any missing item:

1. Actual failure
   - Verbatim observed error and stack, where available.
   - Exact user action/tool/command that failed.
   - Expected behavior versus actual behavior.
   - Whether files were absent, partially written, written to the wrong root,
     blocked, or reported successful without the expected outputs.
   - Extension version and runtime environment, if recorded.

   If no exception or stack was produced, record that honestly and preserve
   the observed symptom. Do not manufacture an error from a source-code string.

2. Reproducible input and workspace
   - The exact owner-selected consumer workspace.
   - The workbook/STTM/configuration actually consumed by the failing route.
   - Original paths and machine identities when available.
   - Relevant settings and existing files needed to reproduce the behavior.

   Do not choose a consumer root by guessing.
   Do not demand a workbook if the observed failure occurred before that
   route consumed one. Mark applicability from evidence.

3. Intended preview and write set
   - Exact relative output paths and intended operations.
   - Recorded preview statuses and existing-file/conflict conditions.
   - Any recorded discrepancy between Preview, Validation and Write roots.
   - What approval was actually given for the failed operation.

   Distinguish a captured preview from a proposed expected set.
   Do not invent filenames or treat a proposed manifest as an observed one.

4. Future guarded-write boundary
   Prepare a proposed isolated temporary-consumer test boundary if the inputs
   are sufficient, including exact intended writes and preservation checks.

   Do not create or populate that consumer workspace, invoke a preview tool,
   approve a manifest, or execute a write in this task.
   Record existing specific approval if present; do not infer it from approval
   of the STTM read-only run.

If evidence identifies the relevant product entrypoint, inspect only its
necessary source path to distinguish the actual consumer write route from
M2 evidence persistence and STTM read-only validation.

Label source-based hypotheses as hypotheses. Do not claim a root cause or
implemented fix from this intake alone.

Do not broaden searches to compensate for missing locators. Complete Part A
and all supported intake work, then identify the smallest missing information.

DELIVERABLES
Return:
- A short English report.md.
- result.json with evidence locators and intake readiness.
- Corrected RUNTIME01 report/result derivatives and correction map.
- Authenticated log copies that could be preserved.
- A compact write-defect intake table:
    required item | observed value | evidence | missing/uncertain
- One bounded proposed next task if the evidence supports it.

Reuse prior records by reference instead of copying whole build bundles.
Do not build a general evidence-management framework.

STATUS RULES
Use:
  READY_FOR_BOUNDED_WRITE_DIAGNOSIS
when the failure and necessary inputs are sufficiently identified, or:
  BLOCKED_MISSING_WRITE_REPRO_INPUTS
with the exact missing items.

Missing write inputs do not undo accepted nominal protocol-3 runtime.
Record completed evidence corrections even if intake is blocked.

If owner information is necessary, ask one consolidated, specific question.
Screenshots or pasted text are acceptable. Do not request the same runtime
reports again, raw repository exports, credentials, or unrestricted data.

End with:
TASK_ID: ETL-0909-PRODUCT-WRITE-EVIDENCE01
STATUS:
R1_LOG_RETENTION:
R2_RECORD_CONSISTENCY:
R3_TIMESTAMPS:
R4_INVENTORY:
ORIGINAL_WRITE_FAILURE_EVIDENCE:
REPRODUCIBLE_INPUT_AND_ROOT:
PREVIEW_AND_WRITE_SET:
GUARDED_WRITE_APPROVAL_STATUS:
MISSING_ITEMS:
REPOSITORY_CHANGED: NO
COMPILER_TEST_RUNNER_HOST_OR_PRODUCT_EXECUTED: NO
CONSUMER_WORKSPACE_WRITTEN: NO
ORIGINAL_PRODUCT_WRITE_FIX_VERIFIED: NO
EVIDENCE_ROOT:
REPORT_PATH:
RESULT_PATH:
NEXT_BOUNDED_TASK_OR_OWNER_QUESTION:

Stop after delivering the result.
