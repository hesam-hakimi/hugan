# ETL\-0904\-REVIEW\-A2 — Independent Source Review Prompt

```text
TASK_ID: ETL-0904-REVIEW-A2
TYPE: INDEPENDENT SOURCE REVIEW — IMPL05A2 M2 AND M3

Run this in a fresh, normal local VS Code Agent chat on Windows. Do not
use the Agent that implemented IMPL05A2 or the Agent that implemented or
self-reviewed IMPL04. Do not use the ETL Orchestrator.

Echo TASK_ID: ETL-0904-REVIEW-A2 as the first line of your report.

You are reviewing, not implementing. Do not edit any file. Do not accept,
discard, Keep, Undo, or otherwise resolve any pending VS Code chat edit.
Do not run type-check, compile, lint, emit, tests, the runner, Extension
Host, npm install, package, stage, commit, stash, checkout, restore, reset,
clean, merge, rebase, cherry-pick, or any other mutating operation.
Read-only commands only. Use git --no-optional-locks for every Git read.

Report what you find. Fix nothing. Do not propose a repair design or edit.

=========================================================
REPOSITORY
=========================================================

Active linked worktree:
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Linked primary worktree:
  C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use these paths for navigation and expected-scope comparison only.
Independently re-derive repository identity, branch, HEAD, Git directories,
dirty inventory, hashes, sizes, diffstats, and live line numbers.

Do not enter or modify the linked primary worktree. Read-only inspection of
its recorded Git identity is permitted only when needed to prove linked-
worktree identity.

=========================================================
BASELINE — VERIFY BEFORE REVIEWING SOURCE
=========================================================

Snapshot01 root:
  C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z

Snapshot01 manifest:
  C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z\manifest.json

Expected manifest SHA-256:
  78324A99A5D700053214B15F680E2DCBE3A2099A0801C43B6D02E512D43004DF

Pre-IMPL05A2 runTest.ts baseline:
  C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z\payload\worktree\src\test\runTest.ts

Before examining the implementation:

1. Confirm the Snapshot01 root, manifest.json, and baseline runTest.ts exist.
2. Compute manifest.json SHA-256 and compare it to the expected value.
3. Parse manifest.json as JSON.
4. Confirm these actual JSON paths and exact values:
     $.taskId == "ETL-0904-SNAPSHOT01"
     $.snapshotStatus == "COMPLETE"
     $.s6SourceStateVerification.sourceHistoryStateUnchanged == "YES"
5. Locate the manifest record for repository-relative path
   src/test/runTest.ts. Report its recorded SHA-256 and byte size.
6. Compute the SHA-256 and byte size of the copied baseline runTest.ts and
   prove they match that manifest record.

Do not substitute guessed top-level fields such as TASK_ID or
SOURCE_HISTORY_STATE_UNCHANGED for the actual JSON paths above.

If any baseline identity check fails, stop without source conclusions and
report:
  BLOCKED_BASELINE_NOT_VERIFIED: <specific reason>
  REVIEW_A2_RESULT: BLOCKED
  NEXT_REQUIRED_GATE: OWNER_BASELINE_DECISION

src/test/runTest.ts on disk IS expected to differ from Snapshot01 because
IMPL05A2 modified it. That difference is not baseline drift.

=========================================================
PREFLIGHT — READ-ONLY
=========================================================

Re-derive and report:

  - git --git-dir, --git-common-dir, and --show-toplevel;
  - active branch;
  - active-worktree HEAD;
  - linked-primary recorded HEAD;
  - git status --porcelain=v1 --untracked-files=all verbatim;
  - staged inventory;
  - SHA-256, byte size, and line-ending counts for every dirty path;
  - SHA-256 and byte size of the Snapshot01 runTest.ts baseline.

Expected branch:
  fix/workspace-write-completion-0.3.148

Expected active-worktree HEAD:
  45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected dirty-path set, regardless of porcelain output order:
   M .github/templates/request.md
   M src/core/sttm/SttmUnderstandingReportRenderer.ts
   M src/extension.ts
   M src/test/runTest.ts
   M src/test/suite/index.ts
  ?? src/test/suite/sttmRealHostStructuredResult.test.ts

Expected staging area: empty.

Using the Snapshot01 manifest records, prove that the five dirty paths other
than src/test/runTest.ts remain byte-identical to Snapshot01. The live
src/test/runTest.ts is deliberately excluded from that equality test.

If repository identity, branch, HEAD, staged inventory, dirty-path identity,
or any of the five out-of-scope dirty-file hashes or byte sizes differs from
the expected state, stop and report:
  BLOCKED_BASELINE_DRIFT: <specific mismatch>
  REVIEW_A2_RESULT: BLOCKED
  NEXT_REQUIRED_GATE: OWNER_BASELINE_DECISION

Do not attempt to repair, restore, accept, discard, or reconcile drift.

=========================================================
DIFFSTAT RECONCILIATION — MANDATORY IF PREFLIGHT PASSES
=========================================================

Run these three commands as three separate single-line Windows commands from
the active worktree. Do not use a backslash as a PowerShell line-continuation
character:

git --no-optional-locks diff --no-index --numstat -- "C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z\payload\worktree\src\test\runTest.ts" "C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147\src\test\runTest.ts"

git --no-optional-locks diff --no-index --numstat -w -- "C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z\payload\worktree\src\test\runTest.ts" "C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147\src\test\runTest.ts"

git --no-optional-locks diff --no-index --numstat --ignore-cr-at-eol -- "C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z\payload\worktree\src\test\runTest.ts" "C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147\src\test\runTest.ts"

Exit code 1 from git diff --no-index means that differences were found. It is
not a command failure and must not stop the review.

Report every numstat and its net line delta. The implementing Agent reported
+94/-37 against Snapshot01, while the VS Code panel displayed +237/-20.

Determine:

  - which measurement reproduces +94/-37;
  - whether any required measurement reproduces +237/-20;
  - whether the two figures use the same comparison pair;
  - whether whitespace or CR-at-EOL treatment explains any difference.

Do not infer the VS Code panel comparison baseline. If its exact comparison
pair cannot be established from surviving read-only evidence, report:
  PANEL_COMPARISON_BASELINE: UNKNOWN
  PANEL_FIGURE_REPRODUCED: NO
  DIFFSTAT_RECONCILED: PARTIAL

That outcome does not invalidate a successfully verified Snapshot01-to-live
diffstat. Explain exactly what was proved and what remains unknowable.

=========================================================
REVIEW SCOPE
=========================================================

Review only the IMPL05A2 changes between the Snapshot01 runTest.ts baseline
and the current live src/test/runTest.ts, plus the minimum enclosing control
flow required to assess M2 and M3.

Do not assess unrelated defects in:

  - B3 classification, verdict, or precedence logic;
  - B4, M1, M4, M5, C1, C2, or B1;
  - product Markdown rendering;
  - post-exit ordering or finalization behavior reserved for A3;
  - any other implementation outside the M2/M3 seams.

However, a change made by IMPL05A2 to any out-of-scope surface is a scope
boundary violation and MUST be assessed and may block acceptance. Distinguish
an implementation scope violation from an unrelated pre-existing defect.

Read-only hash and status checks of the five other dirty files are authorized
solely for boundary proof. Do not review their source behavior.

Report unrelated observations under OUT_OF_SCOPE_FINDINGS. Do not fix them and
do not make them blocking unless they demonstrate that IMPL05A2 crossed its
authorized boundary.

=========================================================
Q1 — DIFF CONFINEMENT
=========================================================

Produce and inspect the complete Snapshot01-to-live diff for runTest.ts.

For every changed hunk:

  - quote its live line range;
  - classify it as M2, M3, shared M2/M3 support, or out of scope;
  - explain its control-flow effect;
  - state whether it changes B3 logic, reduced-record schema,
    finalization-stage schema, finalization flow, or post-exit ordering.

Confirm that no hunk is omitted. Any implementation change outside M2/M3 is a
scope violation even if the changed code appears beneficial.

=========================================================
Q2 — M2: REDUCED-EVIDENCE PATH CORRECTNESS
=========================================================

For every answer, quote the relevant current source with live line numbers and
compare it to the Snapshot01 baseline where necessary.

Q2a. Report the exact primary and reduced evidence filenames and the complete
derivation of the reduced filename. Determine whether failure-controlled input
can contribute separators, absolute paths, dot components, or traversal.

Q2b. Review the containment proof:

  - how the existing evidence root is canonicalized;
  - how candidate paths are lexically resolved and normalized;
  - whether both resolved parents equal the canonical evidence root under the
    repository's Windows path-comparison semantics;
  - whether primary and reduced resolved paths are guaranteed distinct;
  - whether the implementation correctly avoids requiring realpath resolution
    for output files that do not yet exist.

Q2c. Identify every primary and reduced write call. Determine whether both use
fail-if-exists/CreateNew semantics and whether any overwrite, delete-first,
rename-over-existing, or retry-with-overwrite path remains.

Q2d. When the primary write fails and the reduced write succeeds, determine
whether the reduced record preserves the original primary failure without
relabeling, replacement, or masking. Confirm whether the reduced-record schema
itself changed.

Q2e. When the reduced write also fails, determine whether stderr identifies
both the original primary failure and the secondary reduced-write failure.
Trace every later write to process.exitCode in the minimum enclosing main flow
and determine whether nonzero exit can be cleared or masked. This trace is
authorized only to assess the M2 nonzero-exit requirement; do not assess or
redesign the broader A3 post-exit flow.

Q2f. Search for any surviving same-path collision, existsSync guard, or
primary-filename dependency that could prevent the reduced-write attempt when
the primary fails. Root-wide failures such as permission denial, disk full, or
an inaccessible evidence root are excluded from path independence; for those,
assess only the stderr-plus-nonzero contract.

Q2g. Determine whether the derived reduced path can collide with another
authorized focused output path, including the manifest, result, or host-
evidence path, and thereby prevent fallback evidence. If such a collision is
possible, decide whether it violates the stated M2 contract or is a distinct
non-blocking configuration-hardening observation. Give the evidence; do not
propose a repair.

For Q2a through Q2g, conclude separately:
  MET / PARTIAL / NOT_MET

=========================================================
Q3 — M3: AUTHORIZATION ORDERING AND FAILURE COVERAGE
=========================================================

For every answer, quote current source with live line numbers.

Q3a. Identify the exact assignment that enables focused evidence-write
authorization.

Q3b. Identify every isolation-root dedication, canonical containment,
non-overlap, and freshness check that must succeed before authorization.

Q3c. Prove from straight-line and exceptional control flow whether all those
checks complete successfully before authorization is enabled. Identify any
catch, finally, callback, or alternate branch that changes this conclusion.

Q3d. Enumerate every recoverable failure path beginning immediately after
authorization and ending at completion of full evidence assembly. For each:

  - name the operation that can fail;
  - identify the catch/finally path it takes;
  - identify whether full or reduced evidence is attempted;
  - identify the exact reduced destination;
  - identify the result if the reduced write succeeds;
  - identify stderr and exit behavior if the reduced write fails.

Do not summarize several distinct throws as one path unless they enter the
same catch with identical evidence and exit behavior; if grouped, list every
throwing operation in the group.

Q3e. Trace QA-root resolution failure in both conditions:

  - a safe authorized evidence destination already exists;
  - no safe authorized evidence destination exists.

Determine whether the first condition attempts reduced evidence and whether
the second avoids inventing a destination while still producing stderr and a
nonzero exit.

For Q3a through Q3e, conclude separately:
  MET / PARTIAL / NOT_MET

=========================================================
Q4 — STAGE TRACKING: PRIMARY OPEN QUESTION
=========================================================

The M3 requirement is:

  "Stage tracking must correctly reflect the last successfully completed gate
  before a failure. The stage must not advance when a gate fails."

The implementing Agent disclosed that the current convention may assign the
stage before a gate executes. If true, a failure could record the attempted
gate instead of the last successfully completed gate.

Determine independently from source:

Q4a. Enumerate every stage assignment in the relevant M2/M3 control-flow
interval. Quote each assignment and its live line number. For each, state
whether assignment occurs before the gate begins, during the gate, or only
after the gate succeeds.

Q4b. Trace at minimum these concrete failures, plus any additional path needed
for a sound conclusion:

  - protected-manifest-path resolution failure;
  - freshness/dedication assertion failure;
  - QA-root resolution failure after authorization;
  - primary evidence-write failure followed by reduced-write success;
  - primary and reduced evidence writes both failing.

For each path, report:

  - the last gate that completed successfully;
  - the stage value actually recorded;
  - whether those two values accurately correspond under the stated M3
    requirement.

Q4c. Return exactly one stage verdict:

  STAGE_TRACKING_VERDICT: SATISFIES
  STAGE_TRACKING_VERDICT: PARTIAL
  STAGE_TRACKING_VERDICT: VIOLATES

SATISFIES requires every reviewed failure path to record the last successfully
completed gate. PARTIAL means at least one but not all paths are inaccurate.
VIOLATES means the governing convention does not meet the requirement.

Q4d. If the verdict is PARTIAL or VIOLATES, determine whether correction can
remain entirely within the existing stage schema and M2/M3 pre-finalization
control flow, or whether it necessarily requires any A3-reserved surface:

  - finalization-stage schema;
  - finalization-stage tracking;
  - finalization flow;
  - post-exit ordering;
  - reduced-record schema.

Do not design or implement the correction. Report exactly:

  STAGE_FIX_REQUIRES_A3_SCOPE: YES
  STAGE_FIX_REQUIRES_A3_SCOPE: NO
  STAGE_FIX_REQUIRES_A3_SCOPE: CANNOT_DETERMINE

If SATISFIES, report STAGE_FIX_REQUIRES_A3_SCOPE: NO and state that no stage fix
is required.

=========================================================
Q5 — AUTHORIZATION BOUNDARY CHECKS
=========================================================

Compare the Snapshot01 baseline to the current worktree and prove each:

Q5a. No B3 classification field name, enum value, classification assignment,
promotion rule, or precedence expression changed.

Q5b. No reduced-record schema changed.

Q5c. No finalization-stage schema, finalization-stage tracking, finalization
flow logic, or post-exit ordering changed.

Q5d. All five pre-existing dirty out-of-scope files remain byte-identical to
their Snapshot01 records.

Q5e. No additional dirty or staged path appeared.

If a boundary was crossed, quote the exact hunk or name the exact path and
classify it as:
  SCOPE_VIOLATION_<n>: <description>

At the end of the review, re-run raw porcelain status and hashes for all six
dirty paths. Compare them to review-start values and prove that this review
modified nothing.

=========================================================
Q6 — SOURCE-REVIEW / RUNTIME-QUALIFICATION BOUNDARY
=========================================================

This task is a source review only. ACCEPTABLE must never mean runtime-qualified.

For each behavior below, report a concise STATIC_REVIEW_ASSESSMENT and retain
the exact runtime status shown:

1. Primary write fails and the reduced write succeeds at its distinct path.
   RUNTIME_STATUS: UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST

2. Both writes fail; stderr identifies both failures and exit is nonzero.
   RUNTIME_STATUS: UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST

3. A pre-existing primary or reduced evidence file is never overwritten.
   RUNTIME_STATUS: UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST

4. QA-root resolution failure with a safe authorized destination produces a
   reduced record.
   RUNTIME_STATUS: UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST

5. Freshness/dedication failure occurs before authorization and prevents it.
   RUNTIME_STATUS: UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST

No source reasoning, however strong, may change any RUNTIME_STATUS to VERIFIED.
Do not run those tests in this task.

=========================================================
VERDICT RULES
=========================================================

End with exactly one of:

  REVIEW_A2_RESULT: ACCEPTABLE
  REVIEW_A2_RESULT: NOT_ACCEPTABLE
  REVIEW_A2_RESULT: BLOCKED

ACCEPTABLE requires all of the following:

  - baseline and preflight verified;
  - every Q2 M2 item is MET;
  - every Q3 M3 item is MET;
  - STAGE_TRACKING_VERDICT is SATISFIES;
  - no scope boundary was crossed;
  - the review itself modified nothing.

Partial reconciliation of the VS Code panel figure does not by itself prevent
ACCEPTABLE when the Snapshot01-to-live comparison is independently verified
and the unknown panel baseline is reported without inference.

NOT_ACCEPTABLE means at least one M2 or M3 requirement is PARTIAL/NOT_MET, the
stage verdict is PARTIAL/VIOLATES, or an implementation scope boundary was
crossed. List every applicable finding:

  M2_FINDING_<n>: <description>
  M3_FINDING_<n>: <description>
  SCOPE_VIOLATION_<n>: <description>

Do not stop after the first finding. Complete the bounded review and report all
findings unless continuing would require a prohibited action.

BLOCKED is reserved for an unverified baseline, preflight drift, inaccessible
required evidence, or another condition that prevents a trustworthy review.
Do not return M2/M3 conclusions for portions not reached.

Place non-blocking observations under NON_BLOCKING_OBSERVATIONS and unrelated
observations under OUT_OF_SCOPE_FINDINGS.

=========================================================
NEXT-GATE DECISION
=========================================================

Set NEXT_REQUIRED_GATE deterministically:

  - ACCEPTABLE:
      NEXT_REQUIRED_GATE: IMPL05A1

  - NOT_ACCEPTABLE, with no scope violation and every required correction
    confined to src/test/runTest.ts, the existing schemas, and M2/M3
    pre-finalization control flow:
      NEXT_REQUIRED_GATE: IMPL05A2_REPAIR

  - NOT_ACCEPTABLE with a scope violation, B3 coupling, A3 coupling, another
    required file, or an unresolved scope expansion:
      NEXT_REQUIRED_GATE: OWNER_SCOPE_DECISION

  - BLOCKED because baseline or preflight cannot be trusted:
      NEXT_REQUIRED_GATE: OWNER_BASELINE_DECISION

Do not authorize or execute the next gate in this task.

=========================================================
REQUIRED REPORT ORDER
=========================================================

1. TASK_ID line.
2. Snapshot01 manifest and baseline verification.
3. Re-derived repository identity and exact preflight state.
4. Diffstat reconciliation, including all three command results.
5. Q1 through Q6 in order, with live source references.
6. Every blocking and non-blocking finding.
7. Exact final status and pre/post proof that the review changed nothing.
8. Every command executed, in order, confirming each was read-only.
9. One result token.
10. The exact footer below.
11. Stop.

=========================================================
EXACT FOOTER
=========================================================

TASK_ID: ETL-0904-REVIEW-A2
BASELINE_VERIFIED: <YES | NO>
DIFFSTAT_FROM_SNAPSHOT01: <+n/-n | NOT_REACHED>
PANEL_COMPARISON_BASELINE: <identified baseline | UNKNOWN | NOT_REACHED>
PANEL_FIGURE_REPRODUCED: <YES | NO | NOT_REACHED>
DIFFSTAT_RECONCILED: <YES | NO | PARTIAL | NOT_REACHED>
M2_REQUIREMENTS_MET: <YES | NO | PARTIAL | NOT_REACHED>
M3_REQUIREMENTS_MET: <YES | NO | PARTIAL | NOT_REACHED>
STAGE_TRACKING_VERDICT: <SATISFIES | PARTIAL | VIOLATES | NOT_REACHED>
STAGE_FIX_REQUIRES_A3_SCOPE: <YES | NO | CANNOT_DETERMINE | NOT_REACHED>
SCOPE_BOUNDARY_CROSSED: <YES | NO | NOT_REACHED>
B3_LOGIC_UNCHANGED: <YES | NO | NOT_REACHED>
REDUCED_RECORD_SCHEMA_UNCHANGED: <YES | NO | NOT_REACHED>
FINALIZATION_SCHEMA_UNCHANGED: <YES | NO | NOT_REACHED>
FINALIZATION_STAGE_TRACKING_UNCHANGED: <YES | NO | NOT_REACHED>
POST_EXIT_FLOW_UNCHANGED: <YES | NO | NOT_REACHED>
FILES_MODIFIED_BY_THIS_REVIEW: NONE
PENDING_EDITOR_CHANGES_RESOLVED: NONE
GIT_MUTATION_EXECUTED: NO
COMPILE_OR_TEST_EXECUTED: NO
RUNTIME_BEHAVIOR_VERIFIED: NO
TARGETED_TESTS_STILL_REQUIRED: YES
NEXT_REQUIRED_GATE: <IMPL05A1 | IMPL05A2_REPAIR | OWNER_SCOPE_DECISION | OWNER_BASELINE_DECISION>
```
