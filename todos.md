TASK_ID: ETL-0909-PRODUCT-WRITE-REPRO01
TYPE: BOUNDED CONSUMER ROOT AND PREVIEW DIAGNOSIS
LANGUAGE: English only, including conversation, reports and artifacts.

OWNER DECISION
The owner confirms that the target is the historical consumer write
scenario identified by ETL-0909-PRODUCT-WRITE-EVIDENCE01:
generated files must be written into the selected consumer project,
at the correct relative paths, never into the extension/reference project.

Scenario confirmation is now resolved. Do not ask it again.
Whether this failure still reproduces on current code remains unknown.

OBJECTIVE
Exercise the current root-selection and preview decisions for that
scenario, without committing product output files.
Determine whether current code selects the correct consumer destination
or reproduces a concrete routing defect.

This is not another STTM qualification task.
A preview result does not verify successful file writing.

1. INPUTS AND BASELINE

Use the active recovery worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:
fix/workspace-write-completion-0.3.148

Resolve the original machine report/result for:
ETL-0909-PRODUCT-WRITE-EVIDENCE01

Use bounded direct-child task-prefix discovery under C:\docs and follow
its explicit evidence references. Authenticate task identity and source
correspondence; do not select a bundle merely because it is newest.

Read that report completely, including its intake record and references to:
docs/product/multiroot-write-publish-hotfix/bug-report.md
and the associated hotfix-handoff.md.

Read available current reference pointers and the agile repair contract.
Later authenticated reports supersede stale task-status pointers.
Do not restart accepted work or reconstruct missing reference documents.

Verify current worktree, branch, HEAD, staging and dirty paths against
the latest applicable machine baseline. Obtain expected hashes from
machine records, never photographs. Do not repair unexplained drift.

Check task disposition and concurrent activity before starting.
Do not duplicate a running task or use a worktree held by another writer.

2. PRESERVED ACCEPTANCE

Reuse the accepted protocol-3 build/promotion/manifest relationship and
nominal runtime where their actual dependencies still match.

The evidence intake reports R1–R4 record corrections completed.
Do not repeat those corrections or reopen unrelated accepted tests.

This task grants no full B3, installed-candidate or release acceptance.

3. EXECUTION AUTHORITY

Submitting this prompt authorizes:
- Read-only inspection of relevant source and named evidence.
- A new exclusive evidence directory under C:\docs for this task.
- Fresh isolated temporary fixtures: a consumer root and a stand-in
  reference root, clearly distinguished from real repositories.
- Bounded local diagnostic calls using existing installed tools.
- At most ONE isolated Extension Host invocation, only if required to
  exercise the real root-selection/preview route.

Prefer an existing suitable diagnostic entrypoint. A small external
diagnostic driver is permitted if necessary; do not build a new framework.

If a Host is needed, use the previously authenticated prepared executable,
matching compiled extension artifacts, and fresh isolated user data.
Inspect the launch and activation path first. Do not inherit credentials,
user extensions, MCP configuration or unrelated workspace settings.
No installation, download, cloud operation or publishing is authorized.

No product source edits, product build, output promotion, Git mutation,
packaging, reference updates or resolution of pending editor edits.
Do not hand-edit compiled product JavaScript.

Do not execute the write/commit operation or create an approval token.
Do not bypass root validation, path validation or trusted approval.
Fixture preparation is allowed; generated product outputs are not.

If the actual route cannot safely stop before mutation, do not invoke it.
Return the precise missing capability or authority after completing the
remaining useful read-only analysis.

4. REPRODUCTION

Trace the actual consumer path starting from:
etl_write_to_workspace
src/tools/EtlActionToolService.ts
src/writers/RepoWriter.ts

Read the relevant validation and approval consumers, including:
src/validation/PreWriteValidationPipeline.ts
src/tools/TrustedWriteApprovalStore.ts
src/core/utils/PathValidator.ts

Discover the real preview/selection interface from source.
Do not invent a dryRun flag or substitute mock decisions for product logic.
If workspace adapters are simulated, label that evidence explicitly.

Use the historical request and recorded deterministic inputs where available.
Clearly identify any derived fixture; do not claim it is the original input.
A workbook/STTM is not required for this historical route.

Resolve the recorded relative paths from the original bug report:
job_conf/conf/ERUS9/IMSB_MASTER_AREA_V3_PASSED_EXTRACT.json
env_conf/dev/env_conf_erus9_dev.yaml

These were observed historical writes, not an approved preview manifest.
Capture a fresh preview before proposing any future write.

Batch these targeted cases in the permitted diagnostic session:
A. Ambiguous consumer/reference multi-root selection without an explicit
   consumer root must block instead of silently choosing a folder.
B. An explicit valid temporary consumer root must resolve both preview
   destinations inside that root, preserving their exact relative paths.
C. Reversing workspace folder order must not redirect explicit selection.
D. An extension/reference destination must be rejected.
E. A destination escaping the selected consumer root must be rejected.

Record the actual selected root, candidate roots, targetDecision,
resolved destinations and structured blockers.

Do not call Publish or substitute its historical
"Absolute path outside workspace" error for a write-step exception.
The historical write reported success at the wrong root; no write-step
exception or stack was recorded.

5. RESULT AND NEXT GATE

If current routing behaves correctly:
- Report PREWRITE_ROUTING_CONFIRMED at the measured evidence level.
- Do not invent a repair.
- Return a concrete proposed guarded-write smoke using the actual
  temporary consumer root and exact preview/write set.

If a routing defect reproduces:
- Report ROUTING_DEFECT_REPRODUCED with the decisive input/output.
- Identify the smallest affected implementation boundary and the
  targeted regression needed. Do not implement it in this task.

If execution is blocked:
- Report the exact baseline, input, interface or permission blocker.
- Distinguish completed static analysis from unexecuted runtime checks.

A later write requires explicit approval tied to the actual temporary
consumer root and exact write set. Preserve that proposal for approval.
Successful writing will subsequently require file read-back at those
destinations and verification that no output escaped the approved root.

6. MINIMAL HANDOFF

Create report.md and result.json, plus only the relevant raw diagnostic
output and driver/input records needed to substantiate the result.
Reuse prior evidence by authenticated reference rather than copying bundles.

Include:
TASK_ID
STATUS
OWNER_TARGET_CONFIRMED
BASELINE_MATCH
EXECUTION_LEVEL
HOST_INVOCATIONS
CASE_RESULTS
SELECTED_CONSUMER_ROOT
PREVIEW_RELATIVE_PATHS
RESOLVED_DESTINATIONS
STRUCTURED_BLOCKERS
REPOSITORY_CHANGED
PRODUCT_OUTPUT_FILES_WRITTEN
ORIGINAL_PRODUCT_WRITE_FIX_VERIFIED
PROPOSED_GUARDED_WRITE_ROOT_AND_SET
EVIDENCE_ROOT
NEXT_GATE

ORIGINAL_PRODUCT_WRITE_FIX_VERIFIED must remain NO:
this task stops before actual product writes.

Keep temporary fixtures isolated and identify those retained for the
proposed next gate. Never remove or alter pre-existing evidence or roots.

Stop after delivering the result.
