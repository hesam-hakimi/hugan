TASK_ID: ETL-0904-IMPL05A1-B3-REPAIR
TYPE: SOURCE-ONLY REPAIR — FIVE BLOCKING B3 FINDINGS

Run this in a fresh, normal local VS Code Agent chat on Windows. Do not use an
Agent that implemented or reviewed IMPL04, IMPL05A2, IMPL05A1A2,
IMPL05A1-B3-REMAINDER, REVIEW-A2, REVIEW-A1A2-COUPLING, or
REVIEW-B3-REMAINDER. Do not use the ETL Orchestrator.

Echo TASK_ID: ETL-0904-IMPL05A1-B3-REPAIR as the first report line.

========================================================= OWNER AUTHORIZATION AND HARD BOUNDARY

The owner authorizes one bounded source repair for the five blocking findings
from ETL-0904-REVIEW-B3-REMAINDER.

You may run read-only identity/status/hash/diff/search/Local-History/source
inspection commands and edit ONLY src/test/runTest.ts. Make surgical changes.

You may NOT:

• edit any other file;
• alter M2 evidence-path behavior, M3 authorization ordering, or the eight
accepted last-completed-stage assignments;
• alter finalization-stage schema, finalization flow outside the B3
classification seam, post-exit invocation count/order, or reduced-record
non-B3 schema;
• broaden into B4, M1, M4, M5, C1, C2, B1, parser/renderer behavior,
protected-set policy, packaging, or release work;
• type-check, compile, lint, emit, test, run the parser/runner/Extension Host,
package, install, stage, commit, stash, checkout, restore, reset, clean,
merge, push, tag, or release;
• accept, discard, Keep, Undo, or resolve pending editor changes;
• format the whole file or normalize line endings;
• claim runtime verification or qualification.

Do not launch a process whose executable arguments constitute an actual
--extensionTestsPath, --extensionDevelopmentPath, runTest, or
@vscode/test-electron invocation. Exclude the inspection shell and matches
occurring only in inspection text, prompt text, or an ordinary source path.

If another file is required, stop before editing:
BLOCKED_SCOPE_EXPANSION_REQUIRED: <path> <symbol> <reason> <minimum change>.

If a fix requires touching M2, M3 ordering/stages, finalization-stage schema,
non-B3 finalization flow, post-exit ordering, or reduced-record non-B3 schema,
stop before editing:
BLOCKED_ADJACENT_SCOPE_COUPLING: <symbol> <reason> <minimum expansion>.

========================================================= AUTHORITATIVE FINDINGS — ALL FIVE MUST CLOSE

1. B3_FINDING_1: runner comparison is currently gated by global ledger
emptiness (runnerMismatchCount > 0 && classifiedFailures.length === 0), so
a distinct cause can disappear when another row already exists.
2. B3_FINDING_2: the focused-result oracle accepts focusedMode: false,
ignores focusedSuiteFile, and does not prove expected suiteTitles and
loadedFiles content.
3. B3_FINDING_3: class precedence is correct, but the primary datum within the
winning class is selected by insertion order.
4. B3_FINDING_4: counts are individually validated but not checked for
producer-implied cross-field consistency.
5. B3_FINDING_5: some keys name observation sites/broad buckets rather than
underlying causes; repeated reads of one mutable result can classify one
event under two keys.

Do not downgrade or defer any of these. Preserve B3-1, B3-6, B3-7, B3-8;
infrastructure > product > none precedence; verdict-derived exit status;
distinct-cause coexistence; same-cause exactly-once behavior; and the rule that
nonzero exit status alone never creates product classification.

========================================================= MANDATORY PREFLIGHT — RE-DERIVE BEFORE EDITING

Expected:
Active worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
Linked primary:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2
Branch: fix/workspace-write-completion-0.3.148
HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Exact dirty inventory:
M .github/templates/request.md
M src/core/sttm/SttmUnderstandingReportRenderer.ts
M src/extension.ts
M src/test/runTest.ts
M src/test/suite/index.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Verify empty staging, no worktree/common index.lock, and no actual active
test/development Host.

Verify Snapshot01 manifest: SHA-256
78324A99A5D700053214B15F680E2DCBE3A2099A0801C43B6D02E512D43004DF,
valid JSON, TASK_ID=ETL-0904-SNAPSHOT01, snapshotStatus=COMPLETE, and
SOURCE_HISTORY_STATE_UNCHANGED=YES.

Verify each out-of-scope dirty path:
.github/templates/request.md
2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84 / 555
src/core/sttm/SttmUnderstandingReportRenderer.ts
49A4012D1E5216C7E7C9DCF6D55D4517885ECFBCE096F9A96FDD34807D4B32DF / 23461
src/extension.ts
4872337F0F97BBB2A2109F21EE7F362CD4A35F5932B49533936DE8E48FBFC7BC / 18797
src/test/suite/index.ts
488E7344F71D22CE8E439452115DF0EE66B30358BD04F274E400ACD55C61CEC0 / 8397
src/test/suite/sttmRealHostStructuredResult.test.ts
561749C33A09B73D880917EE242A1CB550E26EACF8ABEEF34BA192406C8F6DB3 / 41106

Immediate pre-repair src/test/runTest.ts must be:
SHA-256 9F865D703AB8C0FEAB453D62C2E26491DC6639F95423F2470473722808740089
bytes 126214; bare LF 2903; CRLF 0; bare CR 0.
Snapshot01-to-pre-repair numstat must be +280/-103.

Before editing, find and hash an immutable Local History copy exactly matching
that pre-repair SHA and size. Record its full path; do not create a repository,
Snapshot01, or evidence copy to manufacture a baseline. If absent, stop:
BLOCKED_PRE_REPAIR_BASELINE_NOT_PRESERVABLE.

Capture pre-edit SHA-256, bytes, CRLF/LF/CR for all six dirty paths. Any identity,
HEAD, dirty-set, staging, lock/process, manifest, hash, size, line-ending, or
baseline mismatch requires immediate stop before editing:
BLOCKED_BASELINE_DRIFT: <exact mismatch>.

========================================================= REPAIR A — ACCUMULATE DISTINCT RUNNER CAUSES

• Classify a runner-comparison mismatch by its own cause identity even when the
ledger already contains product or infrastructure rows.
• Never use global ledger emptiness as a cause-eligibility condition.
• Deduplicate only the same runner-comparison cause.
• For product failure + independent runner mismatch, retain both in
failure.all, select infrastructure primary, return BLOCKED, exit nonzero.
• Keep deterministicComparisons, failure.all, primary, verdict, and exit
mutually consistent.

========================================================= REPAIR B — PROVE THE AUTHORIZED FOCUSED EXECUTION

Re-derive the contract from the actual producer in src/test/suite/index.ts,
the consumer/guard, and expected focused-suite constants. Read those sources;
do not infer from the failed evaluator.

The product boundary requires all of the following:

• focusedMode === true;
• focusedSuiteFile identifies the authorized focused suite using the
producer’s real normalization semantics;
• suiteTitles contains exactly the expected suite identity and no foreign
suite;
• loadedFiles identifies exactly the authorized focused file set;
• every count is a nonnegative integer;
• producer-implied cross-field equalities hold, including the tests/passes/
failures/pending relation and every exposed array/count relation;
• product failure derives only from the authoritative failure count after
shape, identity, and consistency all succeed.

If producer and consumer disagree, or identity cannot be proven from
runTest.ts without changing another file, stop with a precise coupling blocker.

Hostile static cases that must not establish product:

1. focusedMode=false;
2. wrong/null focusedSuiteFile;
3. foreign/multiple suiteTitles;
4. foreign/multiple/missing loadedFiles;
5. tests=8, passes=8, pending=0, failures=3;
6. any exposed array/count disagreement.

A coherent, correctly identified result with zero failures must yield PASS
absent another cause; the same with positive failures must yield product FAIL
absent an infrastructure cause.

========================================================= REPAIR C — ORDER-INDEPENDENT PRIMARY EVIDENCE

• Preserve infrastructure > product > none.
• Within the winning class, select primary by a documented stable total order
over immutable row data, never insertion order.
• Every permutation of the same cause multiset must yield identical primary
classification, stage, and message.
• Do not make failure.all lossy or add a serialized field merely for sorting.
• State and prove the exact tie-break tuple for every reachable row.

========================================================= REPAIR D — TRUE CAUSE-IDENTITY DEDUPLICATION

• Keys must identify underlying events, not observation sites, current stage,
or broad buckets.
• Distinct causes at one stage coexist; one cause observed twice appears once.
• Do not classify one mutable Mocha result artifact twice from separate reads
under different identities. Prefer one immutable observation, or prove shared
identity and non-divergence under a between-read change.
• Do not collapse unrelated pre-result aborts into one generic
focused-mocha-result-unusable cause.
• Enumerate every classifyFailure call and prove key equivalence.

Required cause traces:

• product row + surviving Host PID;
• product row + runner mismatch;
• parent-post-exit + host-evidence failure;
• one result artifact observed twice;
• result artifact changed between potential reads;
• two distinct failures during the same last-completed stage.

========================================================= PRESERVATION RULES

Preserve:

• M2 reduced-path/containment/exclusive-write/dual-failure behavior;
• M3 freshness/dedication-before-authorization ordering;
• all eight accepted stage assignment values/order/gate positions;
• finalization-stage interfaces/schema;
• post-exit invocation count/order;
• non-B3 reduced-record fields;
• verdict values and verdict-to-exit mapping;
• all five out-of-scope dirty files.

Do not fix pre-existing R14 (reduced-record completeness/type guard) or R16
(unguarded finalization reads). List them as deferred only. They cannot excuse
any of the five blocking findings.

========================================================= STATIC VERIFICATION — NO EXECUTION

1. Re-read every changed hunk and its enclosing branches.
2. Map all five findings to exact hunks and live lines.
3. Enumerate every classifyFailure site: event, class, stage source, cause key,
duplicate sites, and possible coexistence.
4. Produce a producer/guard/evaluator equivalence matrix for every oracle field
and invariant.
5. Trace all six hostile cases plus coherent zero/positive-failure cases.
6. Prove count equations from producer source, not assumption.
7. Show at least three permutations of one same-class cause multiset and prove
identical primary class/stage/message.
8. Trace product+runner mismatch and product+surviving PID through ledger,
primary, verdict, persisted outcome, and exit.
9. Trace same-cause-twice and distinct-same-stage cases.
10. Search for any surviving global-empty-ledger gate, insertion-order primary,
broad observation key, second mutable-result read, identity gap, or count
coherence gap.
11. Compare B3-1/B3-6 and all M2/M3/stage/finalization/post-exit protected
regions to the exact pre-repair baseline.
12. Re-hash all six paths; prove only src/test/runTest.ts changed, staging is
empty, and no new dirty or generated path appeared.
13. Run and report exit codes for task-only numstats against the exact Local
History baseline: normal, -w, and --ignore-cr-at-eol.
14. Report cumulative Snapshot01-to-live numstat. Never use HEAD as the task
baseline.

If a blocking case remains, do not report success. Repair it within scope and
repeat static verification, or return the exact blocker.

========================================================= UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST

For an implemented result, list each item with STATIC_SOURCE_SUPPORT: and
RUNTIME_STATUS: UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST:

1. product failure + runner mismatch retains both and yields BLOCKED/nonzero;
2. product failure + surviving PID retains both and yields BLOCKED/nonzero;
3. every hostile focused-identity case fails closed as infrastructure;
4. inconsistent counts fail closed as infrastructure;
5. coherent valid focused zero failures yields PASS/zero absent another cause;
6. coherent valid focused positive failures yields FAIL/nonzero absent infra;
7. arrival-order permutations leave primary class/stage/message unchanged;
8. same cause twice yields one row; distinct same-stage causes both persist;
9. artifact mutation between potential reads cannot create two identities for
one underlying event;
10. M2 primary/reduced write behaviors remain unchanged;
11. M3 ordering and accepted stage semantics survive gate fault injection;
12. verdict, persisted outcome, stderr, and exit agree for PASS/FAIL/BLOCKED.

Static support is not runtime verification. Run none of these here. For any
blocked result write only:
UNVERIFIED_UNTIL_AUTHORIZED_TARGETED_TEST: NOT_REACHED.

========================================================= REQUIRED REPORT

Include: preflight and exact hashes; retained baseline path; before/after hunks;
five-finding closure table; oracle equivalence and hostile-case matrix; complete
cause-key matrix; deterministic-primary permutation proof; preservation proof;
pre/post six-path proof; task and cumulative diffstats; exact final status;
runtime-unverified section if implemented; and deferred backlog candidates.

========================================================= RESULT TOKEN AND FOOTER

If implemented, end with exactly:

ETL_0904_IMPL05A1_B3_REPAIR_RESULT: IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW
AUTHORIZED_FILES_CHANGED: src/test/runTest.ts
UNAUTHORIZED_FILES_CHANGED_BY_THIS_TASK: 0
B3_FINDINGS_CLOSED_STATICALLY: B3_FINDING_1,B3_FINDING_2,B3_FINDING_3,B3_FINDING_4,B3_FINDING_5
B3_1_CANONICAL_MODEL_PRESERVED: YES
B3_6_VERDICT_EXIT_MAPPING_PRESERVED: YES
M2_LOGIC_TOUCHED: NO
M3_AUTHORIZATION_ORDERING_TOUCHED: NO
M3_STAGE_ASSIGNMENTS_TOUCHED: NO
FINALIZATION_STAGE_SCHEMA_TOUCHED: NO
NON_B3_FINALIZATION_FLOW_TOUCHED: NO
POST_EXIT_INVOCATION_ORDER_TOUCHED: NO
REDUCED_RECORD_NON_B3_SCHEMA_TOUCHED: NO
TYPECHECK_OR_COMPILE_EXECUTED: NO
TEST_RUNNER_OR_HOST_EXECUTED: NO
GIT_MUTATION_EXECUTED: NO
COMMIT_PUSH_MERGE_OR_RELEASE_EXECUTED: NO
PENDING_EDITOR_CHANGES_RESOLVED: NONE
RUNTIME_BEHAVIOR_VERIFIED: NO
TARGETED_TEST_VERIFICATION_REQUIRED: YES
NEXT_REQUIRED_GATE: INDEPENDENT_SOURCE_REVIEW_B3_REPAIR

If blocked before editing, end with:

ETL_0904_IMPL05A1_B3_REPAIR_RESULT: BLOCKED_<REASON>
AUTHORIZED_FILES_CHANGED: NONE
UNAUTHORIZED_FILES_CHANGED_BY_THIS_TASK: 0
TYPECHECK_OR_COMPILE_EXECUTED: NO
TEST_RUNNER_OR_HOST_EXECUTED: NO
GIT_MUTATION_EXECUTED: NO
COMMIT_PUSH_MERGE_OR_RELEASE_EXECUTED: NO
PENDING_EDITOR_CHANGES_RESOLVED: NONE
TARGETED_TEST_VERIFICATION_REQUIRED: NOT_REACHED
NEXT_REQUIRED_GATE: OWNER_SCOPE_DECISION

If blocked after an authorized edit, use the same blocked token, report
AUTHORIZED_FILES_CHANGED: src/test/runTest.ts, the actual unauthorized count,
and YES/NO for every preservation boundary named in the implemented footer.

The only successful outcome is IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW.
Do not propose or execute review, compile, tests, Host, package, install,
commit, merge, or release in this task.
