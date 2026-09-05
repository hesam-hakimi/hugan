TASK_ID: ETL-0904-IMPL05A1A2
TYPE: SOURCE-ONLY COUPLED REPAIR — M3 LAST-COMPLETED-STAGE SEMANTICS AND LIMITED B3 BOUNDARY DECOUPLING

Run this in a fresh, normal local VS Code Agent chat on Windows. Do not
use the Agent that implemented IMPL05A2, reviewed REVIEW-A2, implemented
or self-reviewed IMPL04, or the ETL Orchestrator.

Echo TASK_ID: ETL-0904-IMPL05A1A2 as the first line of your report.

========================================================= OWNER SCOPE DECISION — FORMER A1/A2 SEAM

Independent review ETL-0904-REVIEW-A2 returned NOT_ACCEPTABLE for one
blocking reason only:

M3_FINDING_1: seven of eight non-initial stage assignments occur before
their gates execute, so a failure records the attempted gate rather
than the last successfully completed gate.

The same review concluded:

M2_REQUIREMENTS_MET: YES
M3_REQUIREMENTS_MET: PARTIAL
STAGE_TRACKING_VERDICT: VIOLATES
STAGE_FIX_REQUIRES_A3_SCOPE: NO
SCOPE_BOUNDARY_CROSSED: NO
B3_LOGIC_UNCHANGED: YES
FINALIZATION_SCHEMA_UNCHANGED: YES
POST_EXIT_FLOW_UNCHANGED: YES
NEXT_REQUIRED_GATE: OWNER_SCOPE_DECISION

The owner now makes that decision. This task authorizes one deliberately
coupled repair across the former A1/A2 boundary:

1. Correct M3 stage semantics so stage always represents the last
successfully completed gate, not the gate being attempted.
2. Decouple the existing B3 product-boundary decision from the old
assign-before-gate interpretation of stage, preserving the existing
pre-task B3 behavior at that seam.

This is a narrow coupling authorization, not permission to combine all
of A1 and A2, and not permission to repair every B3 finding. Do not claim
that broader B3 is closed by this task.

========================================================= OWNER-LOCKED SEMANTICS

The following decisions are authoritative for this task:

1. stage has exactly one meaning: the last gate that completed
successfully.
2. The initial value startup means no later named gate has yet completed.
3. A gate’s stage label may be assigned only after that gate succeeds.
If the gate throws, rejects, returns an invalid result, or otherwise
fails, its label must not be assigned.
4. B3 must not infer an attempted gate or product-boundary reachability
from stage after this repair.
5. If B3 needs product-boundary state, use the smallest private local
state whose only meaning is whether the exact existing product boundary
has actually been reached. Do not add it to an evidence schema, public
interface, manifest, or result contract.
6. Preserve the existing stage vocabulary and serialized field:
  startup
evidence-bootstrap
qa-workspace-resolution
protected-manifest
protected-pre-run-digests
executable-resolution
host-launch
mocha-result-handling
complete
  Do not add, remove, rename, reorder, or reinterpret any serialized
stage value beyond changing assignment timing to last-completed-gate
semantics.
7. Preserve all accepted IMPL05A2 M2 behavior. In particular, do not
modify the reduced filename derivation, canonical containment checks,
distinct-path checks, wx writer, reduced-record schema, or the
primary/reduced failure-reporting contract.
8. Static reasoning is not runtime qualification. Targeted tests remain
required later and are forbidden in this task.

========================================================= AUTHORIZATION AND EXACT LIMITS

The owner authorizes:

• read-only identity, status, hash, diff, process-inspection, and source-
inspection commands required for preflight and static proof;
• surgical edits only to src/test/runTest.ts;
• moving existing pre-finalization stage assignments to the exact point
after their corresponding gates complete successfully;
• introducing or adjusting the minimum private local state necessary to
decouple the existing B3 product-boundary seam from stage;
• changing the exact B3 expression(s) whose behavior depends on
stage === 'mocha-result-handling', but only to preserve the existing
product-boundary behavior under the corrected stage semantics.

The owner does NOT authorize:

• editing any file other than src/test/runTest.ts;
• changing any B3 classification field name, enum value, failure
precedence, PASS/FAIL/BLOCKED promotion rule, or unrelated assignment;
• implementing the broader REVIEW02A B3 repair in this task;
• changing reduced-record or full-record schemas;
• changing finalization-stage schema, finalization flow, post-exit
ordering, or post-exit invocation behavior;
• modifying M2 code or behavior;
• touching B4, M1, M4, M5, C1, C2, B1, A3, package.json, tsconfig*.json,
out/**, src/test/suite/index.ts, src/extension.ts, or
src/core/sttm/SttmUnderstandingReportRenderer.ts;
• whole-file formatting or line-ending normalization;
• type-check, compile, lint, emit, tests, runner, Extension Host, package,
install, activation, or consumer writes;
• launching a process bearing --extensionTestsPath,
--extensionDevelopmentPath, runTest, or @vscode/test-electron as
an actual test/development Host invocation;
• any Git command that mutates the index, worktree, refs, stash, branch,
tags, or history;
• commit, push, merge, tag, stash, checkout, restore, reset, or clean;
• accepting, discarding, Keeping, Undoing, or otherwise resolving any
pending VS Code chat edit;
• creating helper scripts, temporary files, generated output, or
intermediate reports.

Use git --no-optional-locks for every Git read. Treat an already-running
ordinary VS Code editor as non-blocking. When inspecting processes, exclude
the inspection shell itself and matches caused only by the inspection
command text, prompt text, or an ordinary source-file path.

If a required correction needs another file, stop before editing and
report:

BLOCKED_SCOPE_EXPANSION_REQUIRED: <path> <symbol> <reason>

If it requires a reduced/full evidence schema change, finalization-stage
schema change, finalization-flow change, or post-exit change, stop before
editing and report:

BLOCKED_A3_COUPLING_DETECTED: <symbol> <reason> <minimum expansion>

If preserving or correcting the product-boundary behavior requires broader
B3 classification, precedence, enum, or promotion changes, stop before
editing and report:

BLOCKED_B3_BEHAVIOR_DECISION_REQUIRED: <symbol> <reason> <minimum expansion>

If the exact product-boundary event cannot be proved from the live source,
stop before editing and report:

BLOCKED_PRODUCT_BOUNDARY_SEMANTICS_UNPROVEN: <specific ambiguity>

========================================================= MANDATORY PREFLIGHT — RE-DERIVE BEFORE EDITING

Verify every value live. Do not infer identity from this prompt, prior
screenshots, or a prior report.

Expected repository identity:

Active worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
Linked primary worktree:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2
Branch:
fix/workspace-write-completion-0.3.148
HEAD:
45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected dirty inventory — exactly these six paths and status codes:

M .github/templates/request.md
M src/core/sttm/SttmUnderstandingReportRenderer.ts
M src/extension.ts
M src/test/runTest.ts
M src/test/suite/index.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Also prove:

• staging area is empty;
• no index.lock exists in the linked-worktree Git metadata;
• no actual test/development Host process is active under the process-
inspection rule above;
• the Snapshot01 root and manifest still exist;
• manifest.json SHA-256 is exactly:
  78324A99A5D700053214B15F680E2DCBE3A2099A0801C43B6D02E512D43004DF
• the manifest parses as JSON and contains these actual fields:
  $.taskId = ETL-0904-SNAPSHOT01
$.snapshotStatus = COMPLETE
$.s6SourceStateVerification.sourceHistoryStateUnchanged = YES

Snapshot01 root:

C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z

The authoritative immediate pre-task state of src/test/runTest.ts is the
post-IMPL05A2 file independently reviewed by REVIEW-A2:

SHA-256:
CB30EF5D9AEF3CB6D7AE8590A25A85CDCEE898ED296A2783C35E40AEEFF6BF64
Bytes: 120549
CRLF: 0
bare LF: 2783
bare CR: 0

The five pre-existing dirty out-of-scope files must still equal their
Snapshot01 values exactly:

1. .github/templates/request.md
SHA-256: 2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84
Bytes: 555
2. src/core/sttm/SttmUnderstandingReportRenderer.ts
SHA-256: 49A4012D1E5216C7E7C9DCF6D55D4517885ECFBCE096F9A96FDD34807D4B32DF
Bytes: 23461
3. src/extension.ts
SHA-256: 4872337F0F97BBB2A2109F21EE7F362CD4A35F5932B49533936DE8E48FBFC7BC
Bytes: 18797
4. src/test/suite/index.ts
SHA-256: 488E7344F71D22CE8E439452115DF0EE66BD30358BD04F274E400ACD55C61CEC0
Bytes: 8397
5. src/test/suite/sttmRealHostStructuredResult.test.ts
SHA-256: 561749C33A09B73D880917EE242A1CB550E26EACF8ABEEF34BA192406C8F6DB3
Bytes: 41106

Reproduce the pre-task Snapshot01-to-live diffstat with this comparison:

git –no-optional-locks diff –no-index –numstat – “C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z\payload\worktree\src\test\runTest.ts” “src\test\runTest.ts”

Expected: 94 37 with exit code 1, where exit code 1 means differences
were found and is not a failure.

Capture immediate pre-edit SHA-256, byte size, and line-ending counts for
all six dirty paths. Retain the pre-edit src/test/runTest.ts text in
memory only if needed for comparison; do not write a baseline or helper
file anywhere.

If branch, HEAD, worktree identity, dirty-path identity/count, staging
state, Snapshot01 identity, any expected hash/size, runTest line endings,
or the 94 37 diffstat differs, stop immediately without editing and
report:

BLOCKED_BASELINE_DRIFT: <specific mismatch>

========================================================= REQUIRED SOURCE ANALYSIS BEFORE EDITING

Using live line numbers, re-derive and report before editing:

1. Every declaration and assignment of stage in src/test/runTest.ts.
2. The beginning and successful completion point of each corresponding
gate.
3. Every read of stage, separating:
  • evidence/reporting use;
  • failure-localization use;
  • classification or product-boundary use;
  • finalization or post-exit use.
4. The exact B3 expression reported near the REVIEW-A2 live line 2244
that depends on stage === 'mocha-result-handling', plus every value
derived from that expression.
5. The exact event the current source treats as crossing the product
boundary. Prove it from control flow; do not choose a new boundary.
6. The M2 implementation surfaces and reduced-record literal so they can
be proved untouched after editing.
7. The finalization schema/flow and post-exit surfaces so they can be
proved untouched after editing.

Before editing, state one of:

COUPLING_REPAIR_FEASIBLE_WITHIN_AUTHORIZED_SCOPE: YES

or the applicable blocker token. Do not edit after a blocker is found.

========================================================= REQUIRED REPAIR R1 — LAST-COMPLETED STAGE SEMANTICS

Surgically change assignment timing so that every stage label denotes the
last gate that completed successfully.

For each gate:

• leave the prior successful stage value in place while the next gate is
executing;
• assign the next stage value only after all operations that constitute
that gate have succeeded;
• do not assign the next stage in a finally block or before a potentially
failing operation;
• do not introduce a stage assignment on a failure path;
• do not change the stage vocabulary or serialized schema.

At minimum, statically establish these failure semantics:

• failure while resolving or proving the isolation root occurs before
authorization and leaves stage at startup;
• QA-root resolution failure after successful evidence bootstrap records
evidence-bootstrap;
• protected-manifest gate failure records qa-workspace-resolution;
• protected pre-run digest failure records protected-manifest;
• executable resolution failure records protected-pre-run-digests;
• Host-launch gate failure records executable-resolution;
• Mocha-result-handling gate failure records host-launch;
• complete is assigned only after all preceding gates complete.

If the live source proves that a named gate has a more precise boundary
than the shorthand above, use the live control-flow boundary and explain
the difference. Never weaken the owner-locked last-completed semantics.

========================================================= REQUIRED REPAIR R2 — LIMITED B3 BOUNDARY DECOUPLING

The old B3 path uses the pre-gate value
stage === 'mocha-result-handling' as a proxy for product-boundary
reachability. R1 invalidates that proxy by design.

Repair only this coupling seam:

1. Derive the product-boundary state from the exact existing control-flow
event that establishes the boundary, not from stage.
2. Prefer the smallest private local boolean or equivalent local state.
3. Set it only when the product boundary has actually been reached.
4. Ensure failures before the boundary retain the existing infrastructure
treatment and failures after the boundary retain the existing product-
path treatment.
5. Preserve the current classification field name, enum values,
precedence expressions, promotion rules, and result schema.
6. Do not use attempted-stage state to populate evidence stage.
7. Do not add a second serialized stage/currentGate field.

Produce a static before/after behavior matrix for every B3 branch affected
by the coupling seam. The matrix must identify:

• the triggering control-flow condition;
• whether the product boundary has actually been reached;
• the pre-task B3 result;
• the post-task B3 result;
• whether behavior is preserved.

If any row cannot be proven behavior-preserving without changing broader
B3 logic, stop and report BLOCKED_B3_BEHAVIOR_DECISION_REQUIRED. Do not
guess and do not broaden the repair.

========================================================= REQUIRED INVARIANTS

After the edit, prove all of the following statically:

1. M2 remains intact:
  • primary and reduced evidence paths remain distinct;
  • canonical/lexical containment checks are unchanged;
  • both writes retain wx fail-if-exists semantics;
  • successful reduced evidence preserves the primary failure;
  • dual write failure still reports both failures and exits nonzero;
  • reduced-record schema is unchanged.
2. M3 authorization ordering remains intact:
  • freshness and dedication still precede evidence-write authorization;
  • post-authorization recoverable failures still reach full/reduced
evidence persistence as before.
3. Finalization-stage schema is unchanged.
4. Finalization flow is unchanged.
5. Post-exit ordering and invocation are unchanged.
6. No broader B3 field, enum, precedence, or promotion logic changed.
7. No out-of-scope file changed and no new dirty/staged/generated path
appeared.
8. src/test/runTest.ts remains pure LF with no normalization.

The REVIEW-A2 non-blocking manifest/reduced-path collision observation,
duplicate QA-root validation, root re-canonicalization, Windows drive-
relative-name hardening, redundant pre-existence loop, and
retriesOrRelaunches: 0 observation remain backlog only. Do not fix them.

========================================================= STATIC VERIFICATION — NO EXECUTION

Without running TypeScript, tests, runner, or Host:

1. Re-read every changed hunk and enclosing control flow.
2. List every post-edit stage assignment with live line number, its gate,
and the last potentially failing operation that precedes it.
3. Trace at least these concrete failure paths and report the recorded
stage:
  • isolation-root freshness/dedication failure;
  • QA-root resolution failure after authorization;
  • protected-manifest failure;
  • executable-resolution failure;
  • Host-launch failure;
  • Mocha-result-handling failure.
4. Prove no failure path advances to the failing gate’s label.
5. Prove B3 no longer depends on stage as the product-boundary proxy.
6. Provide the required B3 before/after behavior matrix.
7. Search for any remaining stage comparison that relies on attempted-
gate semantics. Report every match; do not silently dismiss one.
8. Compare pre/post hashes for all six dirty paths and prove only
src/test/runTest.ts changed.
9. Confirm staging remains empty and dirty-path identity/count remains six.
10. Report:
  • task-only line additions/deletions from the Agent-authored hunks;
  • final Snapshot01-to-live --numstat for runTest.ts;
  • exact final Git status.
11. Run no formatter and create no generated output.

========================================================= RUNTIME LIMIT — MANDATORY DISCLOSURE

If implementation succeeds, include a section titled exactly:

UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST

It must list at least these items, each with STATIC_SOURCE_SUPPORT and
RUNTIME_STATUS: UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST:

1. Every injected/reproduced gate failure records the last successfully
completed stage.
2. B3 classification behavior is unchanged on both sides of the product
boundary after decoupling it from stage.
3. A QA-root failure after authorization persists evidence with stage
evidence-bootstrap.
4. Primary evidence-write failure still permits the distinct reduced
write to succeed.
5. Primary and reduced write failures still report both identities and
produce a nonzero exit.
6. A pre-existing primary or reduced evidence file is never overwritten.

Static source support must not be presented as runtime verification.
No item may be omitted. No test may be run in this task.

For a blocked result, replace that section with the single line:

UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST: NOT_REACHED

========================================================= REQUIRED REPORT

Return a complete report containing:

1. Re-derived repository/Snapshot01 identity and exact pre-edit status,
hashes, sizes, and line endings.
2. REVIEW-A2 finding accepted as the repair input.
3. Pre-edit stage assignment/read inventory and product-boundary proof.
4. Feasibility decision before edit.
5. Every changed hunk with live before/after source lines.
6. R1 closure table covering every stage assignment and failure trace.
7. R2 closure table plus the B3 before/after behavior matrix.
8. Proof that M2 implementation and reduced-record schema are unchanged.
9. Proof that broader B3 logic, finalization schema/flow, and post-exit
behavior are unchanged.
10. Pre/post hashes proving all five dirty out-of-scope files are byte-
identical and no additional dirty/staged/generated path appeared.
11. Task-only additions/deletions, final Snapshot01-to-live diffstat, and
exact final Git status.
12. Mandatory runtime-limit disclosure if implemented.
13. Deferred backlog candidates observed but not changed.
14. Every command executed in order, identifying all writes. Confirm the
sole write target was src/test/runTest.ts.

Do not claim qualification, runtime verification, or completion beyond
implementation awaiting independent review.

========================================================= RESULT TOKEN AND FOOTER

End with exactly one result token and the corresponding footer.

If implemented without blocking:

ETL_0904_IMPL05A1A2_RESULT: IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW
AUTHORIZED_FILES_CHANGED: src/test/runTest.ts
UNAUTHORIZED_FILES_CHANGED_BY_THIS_TASK: 0
M2_IMPLEMENTATION_TOUCHED: NO
M3_LAST_COMPLETED_STAGE_SEMANTICS_IMPLEMENTED: YES
B3_STAGE_COUPLING_SEAM_TOUCHED: YES
BROADER_B3_LOGIC_TOUCHED: NO
REDUCED_RECORD_SCHEMA_TOUCHED: NO
FINALIZATION_STAGE_SCHEMA_TOUCHED: NO
FINALIZATION_FLOW_TOUCHED: NO
POST_EXIT_FLOW_TOUCHED: NO
TYPECHECK_OR_COMPILE_EXECUTED: NO
TEST_RUNNER_OR_HOST_EXECUTED: NO
COMMIT_PUSH_MERGE_OR_RELEASE_EXECUTED: NO
PENDING_EDITOR_CHANGES_RESOLVED: NONE
TARGETED_TEST_VERIFICATION_REQUIRED: YES
NEXT_REQUIRED_GATE: INDEPENDENT_SOURCE_REVIEW_A1A2_COUPLING

If blocked before any edit:

ETL_0904_IMPL05A1A2_RESULT: BLOCKED_<REASON>
AUTHORIZED_FILES_CHANGED: NONE
UNAUTHORIZED_FILES_CHANGED_BY_THIS_TASK: 0
M2_IMPLEMENTATION_TOUCHED: NO
M3_LAST_COMPLETED_STAGE_SEMANTICS_IMPLEMENTED: NO
B3_STAGE_COUPLING_SEAM_TOUCHED: NO
BROADER_B3_LOGIC_TOUCHED: NO
REDUCED_RECORD_SCHEMA_TOUCHED: NO
FINALIZATION_STAGE_SCHEMA_TOUCHED: NO
FINALIZATION_FLOW_TOUCHED: NO
POST_EXIT_FLOW_TOUCHED: NO
TYPECHECK_OR_COMPILE_EXECUTED: NO
TEST_RUNNER_OR_HOST_EXECUTED: NO
COMMIT_PUSH_MERGE_OR_RELEASE_EXECUTED: NO
PENDING_EDITOR_CHANGES_RESOLVED: NONE
TARGETED_TEST_VERIFICATION_REQUIRED: NOT_REACHED
NEXT_REQUIRED_GATE: OWNER_SCOPE_DECISION

If blocked after an authorized edit was already made, report actual values
rather than forcing a clean footer:

ETL_0904_IMPL05A1A2_RESULT: BLOCKED_<REASON>
AUTHORIZED_FILES_CHANGED: <actual>
UNAUTHORIZED_FILES_CHANGED_BY_THIS_TASK: <actual count>
M2_IMPLEMENTATION_TOUCHED: <YES | NO>
M3_LAST_COMPLETED_STAGE_SEMANTICS_IMPLEMENTED: <YES | NO | PARTIAL>
B3_STAGE_COUPLING_SEAM_TOUCHED: <YES | NO>
BROADER_B3_LOGIC_TOUCHED: <YES | NO>
REDUCED_RECORD_SCHEMA_TOUCHED: <YES | NO>
FINALIZATION_STAGE_SCHEMA_TOUCHED: <YES | NO>
FINALIZATION_FLOW_TOUCHED: <YES | NO>
POST_EXIT_FLOW_TOUCHED: <YES | NO>
TYPECHECK_OR_COMPILE_EXECUTED: NO
TEST_RUNNER_OR_HOST_EXECUTED: NO
COMMIT_PUSH_MERGE_OR_RELEASE_EXECUTED: NO
PENDING_EDITOR_CHANGES_RESOLVED: NONE
TARGETED_TEST_VERIFICATION_REQUIRED: NOT_REACHED
NEXT_REQUIRED_GATE: OWNER_SCOPE_DECISION

========================================================= OWNER DECISION RULES AFTER EXECUTION

These rules are for the owner, not for this Agent:

• If M2_IMPLEMENTATION_TOUCHED, BROADER_B3_LOGIC_TOUCHED,
REDUCED_RECORD_SCHEMA_TOUCHED, FINALIZATION_STAGE_SCHEMA_TOUCHED,
FINALIZATION_FLOW_TOUCHED, or POST_EXIT_FLOW_TOUCHED is YES, or an
unauthorized file count is greater than zero, the scope boundary was
breached. The next gate is OWNER_SCOPE_DECISION, not review acceptance.
• If the success result omits any mandatory runtime-unverified item or
reports targeted verification as unnecessary, reject the report as
overconfident.
• The only successful source-only outcome is
IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW.
• Do not execute or propose the independent review, targeted tests,
compile, package, install, commit, merge, or release inside this task.

Stop.
