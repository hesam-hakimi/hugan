TASK_ID: ETL-0906-F5-REPAIR-TEST02
TYPE: BOUNDED F5 REPAIR WITH PURE LOCAL TESTS — NO RUNNER OR HOST
STATUS: EXECUTION BRIEF; THIS DOCUMENT IS NOT AN EXECUTION RESULT

Run in the same normal LOCAL Windows VS Code Agent chat that performed
ETL-0906-B3-CURRENT-SOURCE-REVIEW01 and retains its original machine-generated
measurements. That Agent now becomes the implementer; a different independent
Agent must review this task’s result. Do not use the ETL Orchestrator or start
a second writer. Echo TASK_ID as the first line of the report.

1. Owner decision and exact supersession

The owner requests a new task to repair the remaining F5 catch-path defect and
verify it with the bounded local-test lane. This brief authorizes that work
when submitted to the local Agent. It does not restart
ETL-0906-B3-REPAIR-TEST01.

For this task, use the current source assessed by
ETL-0906-B3-CURRENT-SOURCE-REVIEW01 as the new immediate before/after baseline,
verified against that assessment’s original machine-generated identities.
The earlier 126,214-byte / 2,903-LF source is NOT this task’s pre-edit baseline.
Do not replace historical pins, restore historical source, or claim that the
new baseline proves preservation relative to that unavailable reviewed source.

The local glossary mismatch is known. The definitions and requirements below
are the self-contained contract for THIS task. No glossary replacement,
formatting, or old glossary-pin gate is required or authorized here. Old
navigation, one-file/source-only restrictions and old baseline requirements
are superseded only for the operations explicitly specified in this brief.
Do not rewrite any previous task or reference document.

F1–F4 only APPEAR_RESOLVED_STATIC in the current-source assessment. Preserve
their behavior; do not repeat their original repairs or claim full acceptance.
Historical M2/M3 preservation and all runtime qualification remain open.

2. Known defect and required behavior

Read the complete current runTest.ts and confirm this reported flow by symbols,
not stale line numbers:

• The outer catch in main classifies from focusedMochaOracle.boundaryReached.
• That position-derived value is assigned after await runTests resolves.
• On a normal counted-test failure, runTests can reject before that assignment.
• Catch then records a run-abort infrastructure cause; finally observes the
valid failed focused result and adds a product cause for the same event.
• The duplicate infrastructure cause changes FAIL into BLOCKED even though
both verdicts have a nonzero exit code.

B3 owns canonical verdict, causal classification, accumulation, deduplication,
primary selection and verdict-to-exit consistency. A single cause observed
twice must become one ledger row; independent causes must remain separate.
Infrastructure outranks product; product outranks none. With no independent
infrastructure failure, trustworthy counted product failure gives FAIL/nonzero.
With an independent infrastructure cause, retain both and give BLOCKED/nonzero.
PASS/zero requires trustworthy authorized evidence and no classified failure.

Repair the catch/observation/cause-identity seam so catch and finally consume
the same retained immutable observation for the same eligible focused run.
Do not use the last-completed-stage variable as proof that a result was or
was not observed. Preserve actual pre-launch aborts as their own causes.

CRITICAL: a valid failed result alone does not prove that every caught error
is the same cause. Establish an explicit causal mapping from the actual
producer, guard, and installed launcher contract, correlated with the same
invocation and trustworthy result. Capture internal origin/provenance at the
relevant await/guard boundary if needed. Stage, message equality, a nonzero
exit, or failures > 0 alone must not erase an independent or unknown error.
Preserve separately observed infrastructure causes even when product evidence
exists. If the available contracts cannot support the required distinction,
report BLOCKED_CAUSE_PROVENANCE with the exact missing fact and minimum scope
needed; do not invent error fields or silently relax the requirement.

Observation eligibility must respect the existing run identity, freshness,
authorization and result-validation gates. File existence alone does not
permit reading stale/pre-launch evidence as this run’s result. Any observation
error must be retained without masking the original caught error. Once taken,
the first observation, including an unusable observation, must not be replaced
by a later file read or mutable object state.

3. Allowed files, tools and preservation boundaries

Only these repository paths may change:

1. src/test/runTest.ts — surgical F5 wiring and the minimum behavior-preserving
extraction needed to exercise the actual production decision.
2. src/test/b3OutcomePolicy.ts — NEW small dependency-free policy/seam helper.
3. src/test/b3OutcomePolicy.unit.test.ts — NEW targeted tests with independent
expected outcomes. Verify both new paths are absent, including ignored files.

The helper must be consumed by the runner. It may contain the F5 decision,
minimal provenance/observation-sharing seam, and the minimum unchanged
cause-ledger/verdict primitives needed to test real deduplication and outcome.
A small injected async seam is allowed if needed to test rejection versus
resolution without real I/O. Do not copy a parallel implementation into tests,
leave the tested helper unused, or extract the entire runner.

Read the complete producer src/test/suite/index.ts, the authoritative
mochaResultGuard and focused-suite constants found by symbol search, relevant
local compiler/test configuration, and the installed launcher source/types
needed to establish rejection provenance. Read dependencies; do not edit them.

Allowed execution: existing local compiler for pre/post no-emit integration
diagnostics; test-only emit and execution of the explicitly selected pure test
closure, with existing installed tooling and outputs only in the external
task root. A test-owned configuration may be created there.

NEVER execute, import, evaluate or launch runTest.ts/runTest.js, the producer,
the launcher, VS Code, Host, parser or product. Inspect transitive runtime
imports before tests: no vscode, @vscode/test-electron, activation, network,
credentials, real consumer input, filesystem-dependent policy tests or child
process launch from helper/test code. Tool-managed workers may run only the
selected pure test closure. Record the entrypoint and arguments.

No dependency installation, npm/npx lifecycle scripts, lint/formatting, watch,
persistent caches/build-info, repository build output, package/install,
Git mutation, editor-change resolution or release. Use git –no-optional-locks
for Git reads. No changes to package/config/lock files or suite registration.

Preserve relative to this task’s captured current baseline:

• F1 accumulation and runner-comparison policy; F2 focused identity validation;
F3 deterministic primary selection; F4 producer-derived count checks.
• M2: evidence paths, containment, exclusive writes, write ordering and
original/dual-error handling.
• M3: freshness/dedication-before-authorization, all eight main-gate stage
assignments and their meanings.
• A3: non-B3 finalization flow, schemas, post-exit invocation count/order.
• Product, observation and protection-policy behavior outside F5.

B3 row contents may change as required to correct F5. Do not broaden serialized
schemas or alter the surrounding evidence-persistence mechanisms. Do not fix
the assessment’s residual observations: real pure-FAIL reachability, ledger
serialization ordering, authorized-cardinality eligibility, key-separator
hardening or Windows path casing. A concrete required coupling is a stop,
not permission to absorb that work.

4. One preflight and one immediate baseline

Active worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
Linked primary:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2
Expected branch: fix/workspace-write-completion-0.3.148
Expected HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
Expected staging: empty.
Expected dirty inventory (leading space means unstaged modification):

```text
 M .github/templates/request.md
 M src/core/sttm/SttmUnderstandingReportRenderer.ts
 M src/extension.ts
 M src/test/runTest.ts
 M src/test/suite/index.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts
```

Use the exact full SHA-256 values from the original machine-generated output
of CURRENT-SOURCE-REVIEW01 retained in this local chat. Match all five assessed
source inputs, including producer, guard, discovery constants and focused
test. The assessed runTest.ts measurements were 136,657 bytes, 3,106 bare LF,
zero CRLF and zero bare CR. Counts are cross-checks, never hash substitutes.
Do not manually transcribe a hash from a screenshot, adopt live hashes as
expected values, or infer a full path from a link’s display label.

If the original text/tool measurements cannot be recovered from this chat,
report BLOCKED_MISSING_ASSESSMENT_ANCHOR before writes, with exactly what is
missing. Do not repeat historical Local History searches or rebuild baselines.
If live inputs differ, report BLOCKED_BASELINE_DRIFT; do not repair the drift.

Verify worktree/common-Git identity, inventory, empty staging, absent index.lock,
and no actual active test/development Host or concurrent writer. Ordinary
editors and prompt/inspection text are not Host evidence. Do not clear locks,
stop another process or resolve pending editor changes.

After these checks, create one fresh unique task root:
C:\docs\ETL-0906-F5-REPAIR-TEST02<UTC-timestamp>-<GUID>\

First verify the existing C:\docs parent and resolved destination are safely
outside both worktrees, consumer/protected roots and historical snapshots.
Create only the named task-owned directories. Stop on unsafe redirection,
destination conflict or permission failure; do not silently choose another root.

CreateNew byte copies of the original six dirty files and other inspected
source dependencies under pre, with exact paths and hashes in baseline.json.
Verify the source/copy hashes match. Record hashes/inventory of package,
configuration and lock files and existing configured output roots, including
out/**, for post-task preservation checks. Recheck inspected inputs immediately
before editing. Snapshot01 is historical context, not this task’s baseline;
its unavailable successor source does not require reconstruction here.

5. Implementation and meaningful local feedback

Print one short non-blocking plan: edit paths, helper boundary, causal rule,
exact compiler/test commands, input closure and output locations. Proceed
within the specified scope without another routine approval round.

Before source edits, capture no-emit diagnostics with the existing compiler
and persistent writes disabled. Use identical options after changes. Preserve
pre-existing failures separately; new unexplained diagnostics block success.
Neither a failed nor unavailable compiler check may be called a pass.

When practical, perform a behavior-preserving extraction and demonstrate the
existing rejection-path failure before fixing it. Do not recreate a historical
source or undo user changes to manufacture red evidence. Report whether a
genuine pre-fix red was observed; a passing negative fixture is not pre-fix red.

Test the production-consumed helper/seam and actual cause/outcome logic.
Expectations must come independently from the contracts above and the actual
producer/launcher, not from the function under test. Use deterministic injected
observations/errors only. Include these cases:

1. Same-invocation launcher rejection proven to restate counted test failure,
with valid authorized positive failures: catch plus finally retain exactly
one product cause; FAIL/nonzero, with no independent infrastructure fixture.
2. Resolved invocation followed by the existing counted-failure guard throwing:
the same product cause and FAIL; no duplicate abort row.
3. Valid product failure plus an independent infrastructure error: both causes
survive; BLOCKED/nonzero. Include similar stage/message text.
4. Valid product failure plus an error whose equivalence is unknown: do not
silently discard or convert that error to product.
5. Rejected invocation with valid zero-failure evidence: retain the abort as
infrastructure; do not manufacture PASS or a product failure.
6. An eligible unusable-result event observed in catch and finally: one cause
for that same event. A separate abort remains separate. Genuine pre-launch
abort is not collapsed into the unusable-result bucket, and stale result
availability cannot create product attribution.
7. Missing, malformed, foreign or count-incoherent result inputs cannot create
product PASS/FAIL. Preserve the existing validator; exercise the real F5
decision consuming its outcome and document validation wiring statically.
8. The actual injected async rejection path acquires the shared observation
at the permitted boundary; catch and finally share it. Assert observation
acquisition count and identity. The reader’s failure cannot mask the
original exception. Mutation or a simulated second read cannot replace it.
9. Product failure plus an independent runner mismatch remains BLOCKED with
both causes. Reversing observation order does not change the primary triple;
repeated same-event observations do not increase cause count.
10. Valid successful observation with no errors remains PASS/zero. Unknown or
invalid evidence must not pass through an accidentally open default.

If a fixture assumes an internal provenance tag, also prove and test how the
production-consumed seam sets that tag on resolved/rejected control flow.
Merely hand-setting a favorable tag in tests does not close the original bug.
Do not execute the real runner to test the wiring; retain static call-site
proof for the integration boundary that remains unexecuted.

Compile only the approved pure closure into external attempt directories.
Explicitly select its test entrypoint; no broad discovery. Keep per-attempt
commands, executed case names, stdout/stderr and exit codes. Never weaken
assertions, hide failed attempts or install missing tooling. Iterate within
scope; a needed scope expansion stops the task.

6. Preservation, report and stopping

Review every changed hunk and enclosing flow against pre\runTest.ts. Demonstrate
the causal mapping at catch, observation acquisition, finally and ledger
insertion. Preserve stage meaning even if obsolete boundaryReached bookkeeping
is narrowly removed after all references are checked. Do not move accepted
stage assignments to make the defect disappear.

Trace M2/M3/A3 behavior through changed B3 inputs, not just unchanged function
text. Re-hash all out-of-scope dirty files, inspected dependencies, configuration
and output roots. Prove only the three allowed repository paths changed;
staging stays empty and no generated/ignored repository files were created.

Keep the exact task-only diff against the captured current baseline, normal
and whitespace/EOL-ignored numstats, and complete additions for the new files.
Do not compare with HEAD or Snapshot01 as if either were the immediate baseline.

Save baseline.json, post-state.json, task.diff, per-attempt logs and report.md
only under the external task root, using fresh files. Include the source of
every expected identity, exact commands, test results, causal-equivalence rule,
preservation matrix and remaining risks. Keep failed attempts and authorized
partial work; do not reset/revert/clean on a blocker.

End report.md with factual values:

```text
TASK_ID: ETL-0906-F5-REPAIR-TEST02
RESULT: IMPLEMENTED_WITH_LOCAL_TESTS_AWAITING_INDEPENDENT_REVIEW | BLOCKED_<REASON>
FILES_CHANGED_BY_TASK: <paths or NONE>
UNAUTHORIZED_FILES_CHANGED_BY_TASK: <actual count>
LOCAL_UNIT_TESTS: <passed/failed/not reached; case counts>
PRE_FIX_RED_EVIDENCE: <observed/partial/not obtained; reason>
NO_EMIT_INTEGRATION_CHECK: <passed/pre-existing failures/new failures/not reached>
SAME_CAUSE_DEDUP_AND_INDEPENDENT_ERROR_RETENTION: <evidence/status>
CURRENT_BASELINE_PRESERVATION: <each boundary YES/NO/NOT_VERIFIED>
HISTORICAL_REVIEWED_BASELINE_PRESERVATION: NOT_VERIFIED
RUNNER_OR_HOST_EXECUTED: <actual; NO required>
PACKAGE_INSTALL_GIT_MUTATION_OR_RELEASE_EXECUTED: <actual; NO required>
PENDING_EDITOR_CHANGES_RESOLVED: <actual; NONE required>
HOST_AND_CONSUMER_QUALIFIED: NO
NEXT_GATE: <ETL-0906-F5-INDEPENDENT-REVIEW02 if successful; OWNER_SCOPE_DECISION if blocked>
EVIDENCE_ROOT: <exact path, or NOT_CREATED if blocked before creation>
```

Choose one result. Success requires F5 closure including independent-error
retention, passing required local cases, no unexplained new diagnostics and
scope preservation. It does not close the historical provenance gap, residual
observations, full B3 acceptance or runtime/product qualification.

Give a short chat summary with the exact report path, result, test counts and
remaining blocker(s). Stop. Independent review is the next separately bounded
gate; do not perform it yourself or continue to Host/build/release.
