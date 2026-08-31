TASK: HF1_V2_FINAL_EXTERNAL_GATE_HARDENING_AFTER_P0_ZERO

Accept the current corrected contract and external F5 harness state.

New owner-observed P0 evidence:

- VS Code parent workspace root:
  recovery-extension-product-0.3.147
- Problems filter visibly empty;
- VS Code reports exactly:
  "No problems have been detected in the workspace"

Therefore:

PROBLEMS_PANEL_COUNT: 0
PROBLEMS_PANEL_CLASSIFICATION: ZERO_DETECTED
P0_RESULT: PASS

The prior value 15 was a transient observation, not an acceptance
requirement. Do not fabricate or wait for 15 Problems.

Do not run F5 in this task.

HARD CONSTRAINTS

- Change only the external %TEMP% F5 harness, runbook, manifest, and self-test.
- Do not modify the repository.
- Preserve exactly the existing four-file product diff.
- Keep package version 0.3.147.
- Do not compile, package, install, build a VSIX, commit, push, run a job,
  approve a write, or deploy.
- F1 and F3 remain the only approved quarantines.
- Failure 2 remains an independent open PR blocker.
- @etl /workflow remains out of scope for Repair 13.
- The two accepted runtime seams remain:
  A. DIRECT_LM_TOOL_PUBLIC_CONTRACT
  B. COPILOT_AGENT_TOOL_INVOCATION

1. MAKE P0 DYNAMIC, NOT HARD-CODED

Remove every acceptance assumption that exactly 15 Problems must exist.

The gate must record:

- PROBLEMS_SCAN_COMPLETE
- PROBLEMS_TOTAL
- PROBLEMS_CLASSIFIED
- PROBLEMS_BLOCKING
- PROBLEMS_PANEL_CLASSIFICATION

Rules:

- zero Problems is valid;
- when total is zero:
  - classified = 0
  - blocking = 0
  - classification = ZERO_DETECTED
- when total is greater than zero:
  every entry must be classified;
- PASS requires:
  - PROBLEMS_SCAN_COMPLETE = YES
  - PROBLEMS_CLASSIFIED = PROBLEMS_TOTAL
  - PROBLEMS_BLOCKING = 0

Record the current owner-observed P0 result as manual owner-attested
preflight evidence. Do not claim it was obtained programmatically.

2. REQUIRE BOTH APPROVED RUNTIME SEAMS

STRUCTURED_OUTPUT_RUNTIME_GATE must never PASS unless:

- DIRECT_LM_TOOL_PUBLIC_CONTRACT = PASS_ON_REAL_HOST
- COPILOT_AGENT_TOOL_INVOCATION = OBSERVED_ON_REAL_HOST

Seam B proves host invocation/reachability only. It must not claim that
Copilot decoded or consumed the returned DataPart.

Add a self-test proving that:

COPILOT_AGENT_TOOL_INVOCATION = NOT_TESTED_ON_REAL_HOST

can never produce a PASS runtime gate.

3. FIX FINAL-EVIDENCE ORDERING

The current runbook calls __etlQA.save() before:

- post-run external-asset verification;
- post-run workspace inventory/diff;
- final repository identity verification.

That permits a premature authoritative PASS.

Correct the design so that:

- scheduled/running artifacts are explicitly PRELIMINARY;
- no preliminary artifact is authoritative;
- A2 post-run hashes complete first;
- post-run inventory and diff complete first;
- final repository HEAD, dirty diff, per-file hashes, version, and compiled
  output pins are reverified first;
- all postflight records use the same RUN_ID;
- only then may one finalizer calculate the gates and atomically write the
  authoritative terminal evidence artifact;
- missing, stale, mismatched, or incomplete postflight input blocks finalization;
- no PASS artifact can exist before postflight completes.

Add false-PASS self-tests for every missing postflight input and for an
attempt to finalize early.

4. FIX CHILD-HOST APPROVAL-CONTROL ORDER

The child Extension Development Host does not exist before F5.

Move the manual control check to this exact position:

- owner presses F5;
- child host opens but the extension remains lazily inactive;
- before @etl hello, schedule(), or any tool invocation:
  verify in the child host that Auto Approve, Bypass, YOLO, and Always Allow
  are all OFF;
- only then trigger benign activation.

Absence of this confirmed child-host check must block the run.

5. REVIEW EVERY EXECUTABLE EXTERNAL ASSET

The safety review and manifest must explicitly cover every executable asset,
including at minimum:

- qa-harness.js
- repair13-harness-selftest.js
- qa-inventory.ps1
- any helper script or launch task that can execute

For each executable asset:

- inspect its exact content;
- verify no network, deletion, package/install, version mutation,
  unrestricted shell, repository write, job, deployment, or approval action;
- pin its SHA-256;
- refuse execution if its hash does not match;
- do not treat ExecutionPolicy Bypass as trusted unless the exact script
  content has passed this review and hash verification.

Add a self-test showing that one executable asset omitted from the review or
manifest blocks the run.

6. REMOVE DEBUG-CONSOLE POLLING DEPENDENCY

Do not require repeated __etlQA.status() evaluation while the Extension Host
is running.

Use the RUN_ID-scoped atomic status file from an external read-only
PowerShell terminal for polling.

Debug Console output is non-authoritative. Only the final postflight-complete
atomic evidence artifact is authoritative.

7. REVALIDATE THE EXTERNAL PACKAGE

Run only the external harness self-tests.

The self-test must demonstrate:

- zero Problems is a valid P0 PASS;
- unclassified or blocking Problems cannot PASS;
- missing Seam B cannot PASS;
- early finalization cannot PASS;
- missing postflight hashes/inventory cannot PASS;
- missing child-host approval check cannot PASS;
- an unreviewed executable asset cannot PASS;
- Failure 2 always keeps OVERALL_TASK_PR_GATE at BLOCKED_FAILURE_2.

Regenerate the external manifest after all changes and provide its new
out-of-band SHA-256 and byte count.

Do not reuse the previous manifest hash because the external assets changed.

REQUIRED FINAL REPORT

REPOSITORY_DIFF_UNCHANGED: YES|NO
PACKAGE_VERSION: <value>
P0_GATE_MODE: DYNAMIC
P0_CURRENT_RESULT: ZERO_DETECTED
P0_CURRENT_COUNT: 0
SEAM_B_REQUIRED_BY_RUNTIME_GATE: YES|NO
POSTFLIGHT_PRECEDES_FINAL_ARTIFACT: YES|NO
PREMATURE_PASS_ARTIFACT_POSSIBLE: YES|NO
CHILD_HOST_APPROVAL_CHECK_ORDER_FIXED: YES|NO
ALL_EXECUTABLE_EXTERNAL_ASSETS_REVIEWED: YES|NO
STATUS_POLLING_USES_ATOMIC_FILE: YES|NO
HARNESS_SELFTEST: PASS|FAIL (<passed>/<total>)
NEW_MANIFEST_SHA256: <full hash>
NEW_MANIFEST_BYTES: <count>
REAL_HOST_F5_EXECUTED: NO
STRUCTURED_OUTPUT_RUNTIME_GATE: BLOCKED_NOT_EXECUTED
OVERALL_TASK_PR_GATE: BLOCKED_FAILURE_2
NEXT_OWNER_ACTION: VERIFY_NEW_MANIFEST_HASH_BEFORE_F5

Stop after this report. Do not execute F5.
