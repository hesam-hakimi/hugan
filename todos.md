TASK_ID: ETL-0904-IMPL05A2
TYPE: SOURCE-ONLY REPAIR — EVIDENCE PERSISTENCE AND AUTHORIZATION ORDERING

Run this in a fresh, normal local VS Code Agent chat on Windows. Do not
use the Agent that implemented or self-reviewed IMPL04, and do not use
the ETL Orchestrator.

Echo TASK_ID: ETL-0904-IMPL05A2 as the first line of your report.

=========================================================
OWNER AUTHORIZATION AND TASK BOUNDARY
=========================================================

The owner authorizes one bounded repair task: close the M2 and M3
findings from independent review ETL-0904-REVIEW02A, as scoped below.

You may:
  - run read-only identity, status, hash, diff, file-search, and
    source-inspection commands needed for preflight and proof;
  - edit ONLY src/test/runTest.ts;
  - make surgical edits only — no whole-file formatting, no line-ending
    normalization, no changes outside the scope defined here.

You may NOT:
  - edit any file other than src/test/runTest.ts. If a required fix
    genuinely needs another source file, stop before editing anything
    and return:
      BLOCKED_SCOPE_EXPANSION_REQUIRED: <exact path> <symbol> <reason>
      <minimum proposed change>
  - touch B3 (verdict classification and precedence logic). If M2 or M3
    cannot be fixed without touching the B3 classification path, stop and
    report BLOCKED_B3_COUPLING_DETECTED with the specific coupling point.
  - run type-check, compile, lint, emit, tests, the runner, or package;
  - launch any process bearing --extensionTestsPath,
    --extensionDevelopmentPath, runTest, or @vscode/test-electron flags.
    A normal VS Code editor process that is already running is not a
    blocker. Only test/development Host processes are blocked.
    Treat a process as active only when its executable arguments show an
    actual test/development Host invocation. Exclude the current
    inspection shell and any match where these strings occur only in the
    inspection command itself, in prompt text, or in an ordinary
    source-file path.
  - run any git command that mutates the index, worktree, refs, stash,
    branch, or history;
  - commit, push, merge, tag, stash, checkout, restore, reset, or clean;
  - accept, discard, Keep, Undo, or otherwise resolve any pending VS Code
    chat edit;
  - normalize line endings or format whole files;
  - treat this implementation as qualification or certify your own work.

=========================================================
REQUIRED PREFLIGHT — RE-DERIVE BEFORE EDITING
=========================================================

Verify all values live. Do not infer them from this prompt or any prior
report.

Expected identity:
  Active worktree:
    C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
  Linked primary worktree:
    C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2
  Branch: fix/workspace-write-completion-0.3.148
  HEAD:   45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected pre-task dirty inventory (six paths):
   M .github/templates/request.md
   M src/extension.ts
   M src/test/runTest.ts
   M src/test/suite/index.ts
   M src/core/sttm/SttmUnderstandingReportRenderer.ts
  ?? src/test/suite/sttmRealHostStructuredResult.test.ts

Also verify:
  - staging area is empty;
  - no index.lock exists in the linked-worktree Git metadata;
  - no process bearing --extensionTestsPath, --extensionDevelopmentPath,
    runTest, or @vscode/test-electron is active (see exclusion rule
    above);
  - capture immediate pre-edit SHA-256, byte size, and line-ending counts
    for every dirty path.

Baseline for file comparison:
  The authoritative baseline for src/test/runTest.ts is:
    C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z\
      payload\worktree\src\test\runTest.ts

  Before editing, verify that the SNAPSHOT01 manifest
  (SHA-256: 78324A99A5D700053214B15F680E2DCBE3A2099A0801C43B6D02E512D43004DF)
  is present and valid. Compare the SHA-256 and byte size of every dirty
  path against the corresponding values recorded in the SNAPSHOT01
  manifest.

  For the A2 diffstat, run this single command:
    git --no-optional-locks diff --no-index --numstat -- "C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z\payload\worktree\src\test\runTest.ts" "src\test\runTest.ts"
  Exit code 1 from git diff --no-index means that differences were found;
  it is not a task failure. Do not use HEAD as the baseline.

If identity, HEAD, dirty path set, staging state, or any file's SHA-256
or byte size differs from SNAPSHOT01 manifest values, stop immediately
and report:
  BLOCKED_BASELINE_DRIFT
Do not attempt to repair the baseline. Do not produce the
UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST section for any blocked result.

=========================================================
SCOPE DEFINITION — WHAT IS IN AND OUT
=========================================================

IN SCOPE — repair these two finding groups from REVIEW02A:

M2 — Evidence persistence: the reduced-evidence fallback path cannot
write when the primary write fails with a filesystem error, because it
uses the same destination path with the same wx flag, and existsSync
blocks a second attempt at the same path.

M3 — Authorization and containment ordering: the evidence destination
is authorized before freshness and dedication of the isolation root are
proved; the first recoverable failure after authorization but before
the primary write path is ready leaves no evidence record.

OUT OF SCOPE — do not touch these:
  - B3: verdict classification, PASS/FAIL/BLOCKED promotion logic,
    failure precedence ordering, or failureClassification field.
    Reserved for IMPL05A1.
  - B4: ETL_TEST_READ_ONLY_TOOL_ONLY environment variable handling.
  - M1: Host PID regex and liveness evidence.
  - M4: compiled-artifact provenance.
  - M5: registration evidence from the API.
  - C1: parser wrapper restoration.
  - C2: channel assertions.
  - B1: Markdown renderer output.
  - post-exit invocation ordering. Reserved for IMPL05A3.
  - finalization stage tracking, finalization flow logic, and
    reduced-record schema completeness. Reserved for IMPL05A3.
  - any change to src/test/suite/index.ts, src/extension.ts,
    src/core/sttm/SttmUnderstandingReportRenderer.ts, package.json,
    tsconfig*.json, or out/**.

If a defect is found outside this scope, report it under
DEFERRED_BACKLOG_CANDIDATES. Do not fix it.

=========================================================
REQUIRED REPAIRS
=========================================================

If either M2 or M3 requires changing the reduced-record schema,
finalization-stage tracking, post-exit ordering, or finalization flow,
stop before editing and report:
  BLOCKED_A3_COUPLING_DETECTED: <symbol> <reason> <minimum expansion>

If either repair requires a new classification value to be expressed,
stop and report:
  BLOCKED_B3_COUPLING_DETECTED: <symbol> <reason>

Repair M2 — Reduced-evidence write path must be independently writable

Requirements:
  - the reduced record must use a distinct filename within the same
    evidence root, derived deterministically from the primary name and
    distinguishable by suffix or prefix so both records can coexist;
  - derive the reduced filename without accepting path separators or
    traversal components from failure-controlled input;
  - canonicalize the existing evidence root. Resolve and normalize the
    primary and reduced candidate paths lexically against that root,
    then prove that each resolved parent equals the canonical evidence
    root and that the two resolved file paths are distinct. Do not
    require filesystem realpath resolution of a candidate output file
    that does not yet exist;
  - the reduced record must use fail-if-exists / CreateNew semantics;
  - if the reduced write succeeds, its record must preserve the original
    primary failure without relabelling or replacement;
  - if the reduced write also fails, do not claim that a record exists.
    stderr must identify both the original primary failure and the
    secondary reduced-write failure, and the process must exit nonzero;
  - if the entire evidence root is unwritable, both writes will fail;
    follow the stderr-plus-nonzero contract above;
  - never overwrite a prior evidence file at either path.

Repair M3 — Freshness and dedication must be proved before authorization

Requirements:
  - prove isolation-root freshness and dedication before setting the
    evidence-write authorization flag;
  - after authorization is set, every recoverable failure between
    authorization and the completion of full evidence assembly must
    leave at minimum a reduced evidence record;
  - if QA-root resolution fails after a safe evidence destination has
    already been established and authorized, write a reduced record;
    if no safe authorized evidence destination exists at that point,
    do not invent or authorize one — emit the failure to stderr and
    ensure a nonzero exit instead;
  - stage tracking must correctly reflect the last successfully
    completed gate before a failure within the full-evidence assembly
    path. Do not advance the stage counter on failure. Do not modify
    finalization-stage tracking, finalization flow logic, or the stage
    schema — those are A3 scope;
  - preserve the existing classification field name, enum values, and
    assignment logic exactly as they stand. Do not add new enum values,
    change precedence, or alter any assignment.

=========================================================
STATIC VERIFICATION BEFORE STOPPING
=========================================================

Without running TypeScript, tests, runner, or Host:

1. Re-read every changed hunk and its enclosing control flow.
2. For M2: prove the reduced-record filename is distinct, lexically
   contained in the authorized evidence root, and uses CreateNew
   semantics. Prove that successful reduced writes preserve the primary
   failure without relabelling. Prove that failed reduced writes report
   both failure identities to stderr with nonzero exit.
3. For M3: prove freshness/dedication gates precede the authorization
   flag, and that every failure after authorization and before full
   evidence assembly leaves a reduced record, conditional on an
   authorized destination existing.
4. Search for any remaining same-path collision, existsSync guard, or
   primary-filename dependency that could prevent the reduced-write
   attempt. Root-wide storage failures are excluded from this search
   and must follow the stderr-plus-nonzero contract.
5. Confirm src/test/suite/index.ts was not modified.
6. Confirm no B3 classification logic was touched: no assignment,
   no enum value, no precedence expression.
7. Confirm that finalization-stage tracking, finalization flow logic,
   and reduced-record schema are all unchanged from the pre-edit state.
8. Compare immediate pre/post SHA-256 for every dirty path and prove
   only src/test/runTest.ts changed.
9. Report the A2 diffstat using the SNAPSHOT01 baseline command above.
10. Run no formatter or command that writes generated output.

If and only if the result is IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW,
include a mandatory section titled
"UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST" containing all five items
below. For each item provide:
  STATIC_SOURCE_SUPPORT: <source-based reasoning>
  RUNTIME_STATUS: UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST

Static source support must never be presented as runtime verification.
All five items must remain listed. If you believe any item is fully
statically verifiable, state that in STATIC_SOURCE_SUPPORT and a
reviewer will assess it — RUNTIME_STATUS stays
UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST regardless.

  Item 1: primary evidence write fails; reduced record succeeds at its
    distinct path.
  Item 2: both primary and reduced writes fail; stderr identifies both
    failure identities without either masking the other, and the
    process exits nonzero.
  Item 3: pre-existing primary or reduced evidence file is never
    overwritten.
  Item 4: QA-root resolution failure, when a safe authorized evidence
    destination exists, produces the required reduced evidence record.
  Item 5: freshness/dedication failure occurs before evidence-write
    authorization is set and correctly prevents it.

For any blocked result, do not produce this section. Instead report:
  UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST: NOT_REACHED

=========================================================
REQUIRED REPORT
=========================================================

Return a complete report containing:

1. Re-derived identity and exact pre-edit status with hashes.
2. SNAPSHOT01 manifest verification result.
3. The precise lines changed, with before/after for each hunk.
4. An M2 and M3 closure table with source references.
5. Proof of the distinct reduced-record filename, its lexical
   containment in the authorized evidence root, and its CreateNew
   semantics.
6. Proof that freshness/dedication gates precede authorization.
7. Proof that post-authorization failures leave a reduced record,
   conditional on an authorized destination existing.
8. Proof that all five pre-existing dirty out-of-scope paths remained
   byte-identical, that no additional dirty or staged path appeared,
   and that no generated output was created by this task.
9. Proof that finalization-stage tracking, finalization flow logic,
   and reduced-record schema are unchanged.
10. A2 diffstat computed against the SNAPSHOT01 baseline.
11. Exact final git status.
12. If and only if the result is IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW:
    the mandatory UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST section with
    all five items, each with STATIC_SOURCE_SUPPORT and RUNTIME_STATUS.
    For any blocked result, this section is replaced by the single line:
      UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST: NOT_REACHED
13. Deferred backlog candidates found but not fixed.

=========================================================
RESULT TOKEN AND FOOTER
=========================================================

End with exactly one result token, then the conditional fields below.

If implemented without blocking:
  ETL_0904_IMPL05A2_RESULT: IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW
  AUTHORIZED_FILES_CHANGED: src/test/runTest.ts
  UNAUTHORIZED_FILES_CHANGED_BY_THIS_TASK: 0
  B3_CLASSIFICATION_LOGIC_TOUCHED: NO
  FINALIZATION_STAGE_SCHEMA_TOUCHED: NO
  POST_EXIT_FINALIZATION_FLOW_TOUCHED: NO
  TYPECHECK_OR_COMPILE_EXECUTED: NO
  TEST_RUNNER_OR_HOST_EXECUTED: NO
  COMMIT_PUSH_MERGE_OR_RELEASE_EXECUTED: NO
  PENDING_EDITOR_CHANGES_RESOLVED: NONE
  TARGETED_TEST_VERIFICATION_REQUIRED: YES
  NEXT_REQUIRED_GATE: INDEPENDENT_SOURCE_REVIEW_A2

If blocked before any edit:
  ETL_0904_IMPL05A2_RESULT: BLOCKED_<REASON>
  AUTHORIZED_FILES_CHANGED: NONE
  UNAUTHORIZED_FILES_CHANGED_BY_THIS_TASK: 0
  B3_CLASSIFICATION_LOGIC_TOUCHED: NO
  FINALIZATION_STAGE_SCHEMA_TOUCHED: NO
  POST_EXIT_FINALIZATION_FLOW_TOUCHED: NO
  TYPECHECK_OR_COMPILE_EXECUTED: NO
  TEST_RUNNER_OR_HOST_EXECUTED: NO
  COMMIT_PUSH_MERGE_OR_RELEASE_EXECUTED: NO
  PENDING_EDITOR_CHANGES_RESOLVED: NONE
  TARGETED_TEST_VERIFICATION_REQUIRED: NOT_REACHED
  NEXT_REQUIRED_GATE: OWNER_SCOPE_DECISION

If blocked after an authorized edit was already made:
  ETL_0904_IMPL05A2_RESULT: BLOCKED_<REASON>
  AUTHORIZED_FILES_CHANGED: src/test/runTest.ts
  UNAUTHORIZED_FILES_CHANGED_BY_THIS_TASK: <n>
  B3_CLASSIFICATION_LOGIC_TOUCHED: <YES | NO>
  FINALIZATION_STAGE_SCHEMA_TOUCHED: <YES | NO>
  POST_EXIT_FINALIZATION_FLOW_TOUCHED: <YES | NO>
  TYPECHECK_OR_COMPILE_EXECUTED: NO
  TEST_RUNNER_OR_HOST_EXECUTED: NO
  COMMIT_PUSH_MERGE_OR_RELEASE_EXECUTED: NO
  PENDING_EDITOR_CHANGES_RESOLVED: NONE
  TARGETED_TEST_VERIFICATION_REQUIRED: NOT_REACHED
  NEXT_REQUIRED_GATE: OWNER_SCOPE_DECISION

=========================================================
DECISION RULES FOR THE OWNER AFTER EXECUTION
=========================================================

These rules are for the owner, not for this Agent:

  - If any of B3_CLASSIFICATION_LOGIC_TOUCHED,
    FINALIZATION_STAGE_SCHEMA_TOUCHED, or
    POST_EXIT_FINALIZATION_FLOW_TOUCHED is YES, or
    UNAUTHORIZED_FILES_CHANGED_BY_THIS_TASK is greater than zero:
    the A2 scope boundary was breached. The independent reviewer must
    be informed and must treat the report as out-of-scope before
    assessing it. NEXT_REQUIRED_GATE remains OWNER_SCOPE_DECISION.

  - If the result is IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW and
    TARGETED_TEST_VERIFICATION_REQUIRED is not YES, or if the
    UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST section is absent or
    missing any of the five items: the report is overconfident.
    The independent reviewer must reject it on that basis alone.

  - The only acceptable successful outcome of A2 is
    IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW. A precise blocker is also
    a valid outcome and must not be concealed to obtain the success
    token.

Do not propose or execute the review, type-check, compile, Host run,
package, install, commit, merge, or release inside this task.
