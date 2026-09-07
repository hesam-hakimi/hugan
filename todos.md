TASK_ID: ETL-0907-F5-CONTRACT-REPAIR01
TYPE: PROPOSED BOUNDED HARNESS-CONTRACT REPAIR WITH PURE LOCAL TESTS
STATUS: PROPOSAL; NOT AN EXECUTION RESULT OR PRIOR AUTHORIZATION

Owner submission of this complete brief to a LOCAL Windows VS Code Agent
authorizes the prospective work below, including the explicitly named producer
change. Merely receiving or reviewing this draft authorizes no repository
operation. This is a new task, not a continuation of the old repair permissions.

Use one implementation Agent and one writer. A later independent reviewer
must be a different Agent. Do not use the ETL Orchestrator. Keep code, tests,
comments, evidence and the engineering report in English.

1. Decision and scope of the correction

The latest independent report returned NOT_ACCEPTABLE for the delivered F5
repair. Its important technical findings are useful, but two proposed shortcuts
are not this task’s contract:

• Checking signal alone leaves abnormal numeric exits unresolved.
• A producer marker written before termination does not prove that a later
abnormal termination was caused only by the recorded test failure.

Adopt a focused-run protocol that separates completed test-result delivery
from failure of the Host/launcher process:

1. A focused producer that finishes and successfully writes its run-bound
result completes its entrypoint normally, including when Mocha counted
failed tests. Completing delivery must not label those tests PASS.
2. The parent runner derives PASS/FAIL/BLOCKED and its own exit status from the
validated retained result plus the complete cause ledger.
3. Any actual launcher rejection or abnormal Host termination retains an
infrastructure/unknown-equivalence cause. A completion marker, matching
invocation, positive test counts, signal absence or an apparently familiar
exit code must not erase that cause.
4. When valid product evidence independently survives alongside such an abort,
retain the product cause as well. If that evidence is unusable or compromised,
do not manufacture a product cause.

Thus the normal focused counted-failure path becomes: completed producer
delivery -> normal Host/launcher completion -> parent FAIL/nonzero. An abnormal
Host exit remains BLOCKED/nonzero, including when valid failed-test evidence
also exists. This avoids guessing why a nonzero Host exit occurred.

This proposed task deliberately expands the previous three-file scope to the
focused producer and the four directly related F5 behaviors: abnormal exits,
the guard’s second read, pre-launch result eligibility, and deterministic
representatives of deduplicated causes. It does not accept those as residual
risks or authorize unrelated cleanup.

Only these repository files may change:

• src/test/runTest.ts
• src/test/b3OutcomePolicy.ts
• src/test/b3OutcomePolicy.unit.test.ts
• src/test/suite/index.ts

Preserve ordinary non-focused producer/runner behavior. Do not change product
code, test discovery, focused suite contents, package/configuration/dependencies,
or src/test/harness/mochaResultGuard.ts. For focused execution, replace the
path-reading guard call with a decision over the retained validated observation;
the existing guard remains available unchanged for ordinary execution.

Before editing, inspect the actual producer and installed launcher/entrypoint
contracts to establish that normal focused delivery can use this protocol.
If it cannot be implemented within the four paths, report the exact coupling
and minimum additional boundary. Do not silently substitute a marker-only
scheme or classify every ordinary counted failure BLOCKED.

2. Current evidence and terminology

Read this entire brief, then the complete
docs/glossary/ETL_QUALIFICATION_GLOSSARY.md, ETL_LATEST.md and the current
overlay in ETL_STATE_REV3.md. Follow their navigation to the governing B3
independent-review definitions and then read the original files below. Read
the complete earlier implementation/review briefs where supplied with their
evidence; a report’s recollection is not proof of its former authorization.
Use bounded read-only discovery for these named documents and relevant source
symbols inside the active worktree and the explicitly identified evidence
roots. Do not substitute model memory for a missing definition or requirement.

This new brief explicitly proposes changing the focused producer contract and
using a new immediate baseline; it does not assert that prior gates accepted
those changes. If a governing current-state requirement conflicts beyond
these explicit prospective changes, stop and report the exact conflict. If
required terminology/state material is missing, name the missing input.
Screenshots are navigation aids, not executable pins or source substitutes.

Independent review root, read only:
C:\docs\ETL-0906-F5-INDEPENDENT-REVIEW02\20260907T101629Z-0318A671-32C9-41EC-AA32-B4EF0BF16505

Required review files:
report.md, review-identities.md, review-identities-pass2.json,
review-anchor-provenance.md, review-runTest.diff,
review-red-vs-green-policy.diff.

Previous implementation root, read only:
C:\docs\ETL-0906-F5-REPAIR-TEST02-20260906T193742Z-11E99B37-E240-4D33-931A-3793C1E97409

Read its report.md and task.diff plus relevant retained source/log artifacts
needed to distinguish prior behavior from this task. The old pre\runTest.ts
is historical to this new task; it is NOT the immediate pre-edit baseline.

The independent report’s F-1 through F-6 labels are local finding numbers.
They are not replacements for the earlier F1-F5/B3 definitions:

|Review-local finding|Meaning                                                                      |Disposition in this task                                              |
|--------------------|-----------------------------------------------------------------------------|----------------------------------------------------------------------|
|F-1                 |Abnormal Host termination incorrectly collapsed into product/unusable result |Repair through the focused delivery/exit contract                     |
|F-2                 |Guard’s second read can introduce a hidden independent error                 |Remove the focused second read                                        |
|F-3                 |Finalization can read foreign pre-launch evidence; test 6b misses it         |Gate all result acquisition and attribution                           |
|F-4                 |First observation fixes a cause’s message/stage; order test masks it         |Make canonical primary evidence order-independent                     |
|F-5                 |Throwing-reader test does not exercise the normal reader-error representation|Correct coverage and state its boundary                               |
|F-6                 |Existing repository JavaScript predates the repair                           |Expected under earlier no-emit rules; no repository build in this task|

B3 still requires one canonical verdict; trustworthy focused identity and
producer-defined count coherence; accumulation of distinct causes; same-cause
deduplication; order-independent primary classification/stage/message; and
exit status derived from the final verdict.

Preserve infrastructure priority over product and product over no failure;
evidence-write failures also block. Preserve the existing exact mapping
PASS -> 0, FAIL -> 1, BLOCKED -> 1 at every parent exit decision.

The report’s observation that catch precedes finally in production does not
satisfy the separate requirement that the same cause observations produce the
same primary triple under permutation. This task does not weaken that contract.
It does not require sorting the entire serialized ledger array.

The review also proceeded despite identifying strictly malformed legacy
post-state.json, although its review brief specified a stop for that condition.
Record that limitation, rather than retroactively declaring the old review
procedure compliant. Its concrete source findings remain inspection inputs.

The owner disclosed temporary presentation edits to legacy evidence JSON.
Do not edit, normalize, reconstruct or repin those files. This new task uses
the independent review’s current source measurements for its baseline gate;
it does not depend on parsing the malformed legacy JSON. This permission is
prospective and does not ratify previous departures. Historical evidence-file
immutability and preservation against the unavailable 126214-byte source
remain NOT_VERIFIED.

3. Preflight and a new immediate baseline

Active worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
Linked primary, identity only:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2
Expected branch: fix/workspace-write-completion-0.3.148
Expected HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
Expected staging: empty.

Expected complete dirty inventory:

```text
 M .github/templates/request.md
 M src/core/sttm/SttmUnderstandingReportRenderer.ts
 M src/extension.ts
 M src/test/runTest.ts
 M src/test/suite/index.ts
?? src/test/b3OutcomePolicy.ts
?? src/test/b3OutcomePolicy.unit.test.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts
```

Use git –no-optional-locks for reads. Verify worktree/common-Git identity,
branch, HEAD, the full path/status set, empty staging, absent applicable
index.lock files, and no active test/development Host or concurrent writer.
Use actual executable arguments, not text matches on inspection commands.
An ordinary editor is not a prohibited Host. Never stop another process,
remove a lock, or use Keep/Undo/save/revert to change pending editor state.

Read the full source SHA-256 values from review-identities-pass2.json and
cross-check review-identities.md. If the JSON is absent, the complete explicit
64-character source measurements in the saved Markdown are an allowed
alternative anchor for this new task. Both are local original review artifacts;
do not transcribe hashes from pictures. If available anchors disagree, are
incomplete or cannot be unambiguously read, stop before writes.

Match every measured live source input before editing, including the producer,
guard, discovery constants, focused suite and out-of-scope dirty files. Counts
below are only cross-checks:

|File                                 |Bytes |CRLF|Bare LF|Bare CR|
|-------------------------------------|-----:|---:|------:|------:|
|src/test/runTest.ts                  |131713|0   |3000   |0      |
|src/test/b3OutcomePolicy.ts          |17652 |435 |0      |0      |
|src/test/b3OutcomePolicy.unit.test.ts|18990 |429 |0      |0      |
|src/test/suite/index.ts              |8397  |208 |0      |0      |

Stop on drift; do not adopt newly observed hashes as the expected identities.
No Local History, chat-log or historical-baseline hunt is needed or authorized.

After preflight, create one fresh root using exclusive creation:
C:\docs\ETL-0907-F5-CONTRACT-REPAIR01<UTC-timestamp>-<GUID>\

Verify C:\docs and the resolved parent/destination are outside both checkouts,
old evidence/snapshots, profiles and protected consumer paths, without unsafe
redirection. Create only task-owned directories; no alternate root on failure.

Capture exact byte copies of the four edit targets and all preservation inputs
under pre; verify source/copy hashes. Record complete raw-byte identities,
line-ending profiles, configuration/lock-file state, and a per-file hash
inventory of configured repository output roots, including out/** and existing
build-info. Counts/size/newest mtime alone are not byte-preservation evidence.
Capture and retain the current review-anchor artifacts’ hashes too. These
records establish the new immediate baseline, not historical immutability.
Recheck target stability before the first source edit.

4. Implementation requirements

A. Focused completion and independent Host errors

Define the focused protocol explicitly in source and the report. Correlate
the retained result to the current authorized invocation, using an existing
adequate run identifier where one exists, or one narrowly introduced identifier
passed from this runner to this producer. Verify its actual origin and matching;
a stored but unused field is not correlation.

A minimal versioned completion/correlation addition to the focused Mocha-result
record and its validation is allowed. Do not add keys to the closed
RunnerEvidence/full/reduced evidence schemas or broaden unrelated environment
policies. In particular, preserve ETL_TEST_READ_ONLY_TOOL_ONLY handling.

For the focused producer only, completing result delivery must resolve the
entrypoint even when there are counted test failures. Producer execution or
write errors must remain errors. The parent must reject missing, foreign,
wrong-invocation, unsupported/absent-protocol or incoherent results as unusable;
do not silently trust an older focused result format or an old compiled producer.

The parent remains the sole verdict/exit authority. All launcher rejections
remain independent infrastructure/unknown-equivalence causes under this new
protocol, including signal, undefined-code termination, code 1 and other numeric
codes. Do not special-case a familiar nonzero code as proof of product failure.
Retain trustworthy counted product evidence separately when present.

Marker presence describes the result/completion boundary; it must never excuse
a later crash or override the observed launcher outcome. Do not modify the
installed launcher, suppress its rejection, swallow a write failure, or turn a
failed focused suite into parent PASS to obtain a clean Host outcome.

B. One eligible observation and one focused gate

The focused result gate must consume the retained observation used by catch
and finalization. Do not call the path-reading Mocha guard a second time for
focused execution. Preserve the non-focused guard path unchanged.

If the focused gate raises a counted-failure error, its attribution must come
from that exact validated current-run observation. An arbitrary error raised
at the same call site must not inherit product attribution. Keep the original
exception and any independent observation error available to the ledger and
retained evidence, not only to local test variables.

Preserve the first observation, including unusable evidence. Trace every raw
and oracle consumer; either enforce the needed immutability or establish that
relevant retained values cannot be replaced/mutated by a later consumer.

C. Pre-launch and unsafe result paths

Result acquisition needs its own explicit eligibility proof: focused invocation,
safe validated result destination, completed applicable freshness/absence
checks, and actual invocation entry. Evidence-write authorization by itself
does not authorize reading a result path or assigning that file to this run.

Apply eligibility to every acquisition/classification site, including finally.
Before launch, no stale/foreign result read may create a product row, even if
evidence-write authorization is already true. In particular, handle the window
where MOCHA_RESULT_FILE is outside the isolation root and containment rejects
it after authorization. Never read that foreign path during finalization.

Preserve the original abort’s cause and write available diagnostics only to an
already safe evidence destination. Do not move the accepted M3 authorization
or eight stage assignments merely to avoid this case; add the narrowly scoped
B3 result-eligibility state and consumption gate instead. If preserving those
boundaries makes the correction impossible, name the exact coupling and stop.

D. Canonical representatives after deduplication

Make repeated observations of one cause produce a deterministic representative
for primary classification, stage and message. Different causes must still
produce distinct rows even with similar text/stage. Do not let first arrival
choose the representative implicitly.

Use a documented order-independent canonicalization/merge rule or canonical
cause payloads. Retain relevant independent exceptions and preserve the
original caught error where the existing evidence contract requires it.
Do not weaken the requirement to ‘catch always happens first’. Do not change
global last-completed-stage semantics or sort the entire serialized ledger
as a substitute for solving representative selection.

5. Preservation and allowed execution

Before editing, read all four target files completely, the unchanged Mocha
guard, focused suite/discovery constants, authoritative producer consumers,
and all relevant classification/observation/persistence/exit call sites.

Preserve:

• F1 independent cause accumulation and runner-comparison policy, except the
exact causal corrections above; no global ledger-emptiness gate.
• F2 runner-owned focused identity checks and F4 producer-defined count/array
coherence. Protocol correlation is additional validation, not a replacement.
• M2 evidence destinations, containment, deterministic reduced filename,
exclusive writes, original-error retention and dual-write-failure handling.
• M3 freshness/dedication before authorization and all eight stage assignments
with their accepted last-successfully-completed meaning.
• A3 non-B3 finalization behavior, closed schemas and post-exit verification
invocation/order. B3 row values may change as required and must be documented.
• Non-focused execution and all product/renderer/Host-observation/configuration
behavior outside this focused contract.

Permitted execution uses existing installed tooling only:

1. Identical pre/post no-emit TypeScript integration checks, with persistent
incremental/cache/build-info writes disabled.
2. Compile and run only the explicitly selected pure unit-test closure, with
outputs/configuration under this task’s external attempt directories.

The helper and unit tests must not import/execute runTest.ts, suite/index.ts,
the launcher, vscode, extension activation, product/parser code, filesystem or
network behavior, or real consumer inputs. Pure functions used by the producer
may live in b3OutcomePolicy.ts and be tested directly. A minimal pure extraction
of validation needed to exercise actual protocol/error data is allowed; avoid
a parallel test-only implementation or unrelated refactoring.

Inspect the transitive runtime import closure before tests. Never run the
actual runner, producer, Host, integration suite, package scripts, broad test
discovery, watcher, formatter/linter, install, package or release. No dependency
installation, repository emit, Git mutation or new repository files. Preserve
each file’s line endings; no whole-file normalization.

6. Required meaningful tests and execution evidence

Exercise the real production-consumed pure policy, validator/protocol gate and
injected asynchronous boundary. Document separately the actual runner/producer
wiring that remains statically inspected. Do not claim Host qualification.

Required cases:

1. Completed focused result with zero failures, normal launcher completion:
parent PASS/0, no failure rows.
2. Completed focused result with positive failures, normal launcher completion:
parent FAIL/nonzero, exactly one product cause. Test the producer’s actual
pure completion decision as well as the parent’s result decision.
3. Valid failed result plus each of signal termination, a distinct numeric
abnormal exit, and code 1: retain product plus infrastructure, BLOCKED.
A completion marker must not erase any of these terminations.
4. Launcher rejection plus unusable result: retain the abort, never product;
deduplicate only an independently demonstrated same cause.
5. A result-write/delivery failure or invalid completion/correlation cannot
become parent PASS/FAIL. Wrong invocation, missing protocol and a stale
otherwise valid focused result must fail the trust boundary.
6. A focused counted-failure gate consumes the first retained observation;
assert the underlying reader is called once and no second guard read occurs.
An unrelated gate/observer error remains independent rather than product.
7. Pre-launch abort both before authorization and after authorization but
before result-path validation/launch: reader call count zero and no product
row anywhere. Include a foreign MOCHA_RESULT_FILE and stale positive counts.
Assert the complete row set, not a product row with one chosen error message.
8. Use the normal production reader-error representation (such as raw.readError)
through the actual pure validator. If retaining a throwing-reader case,
identify its helper-only boundary; do not present it as the normal I/O path.
9. Catch/finalization observations of the same product cause in both orders,
with no dominating infrastructure row: one cause and identical primary
classification, stage and message. Repeat for one unusable-result cause.
10. Independent causes with similar stage/message survive, including a runner
mismatch plus product. Verify order independence without relying solely on
an identical higher-priority row to hide differing representatives.
11. Existing focused identity and count-coherence hostile cases still cannot
become product evidence. The added protocol must not weaken those checks.
12. Non-focused completion policy retains its existing counted-failure behavior;
prove unchanged wiring statically and test any changed shared pure decision.

Update earlier tests whose expectations intentionally change under the new
focused protocol, recording why each expectation changes. Do not weaken
assertions or silently remove adverse cases to recover a green run. A compiler
failure from a missing new API is not pre-fix behavioral red evidence.

Capture each attempt’s exact source copies and hashes, test bytes, closure
configuration, emitted JavaScript hashes, executed entrypoint/arguments,
stdout, stderr, start/end time and the process exit code actually returned by
the execution tool. Preserve failed/intermediate attempts. Do not replace
machine exit evidence with a prose assertion or infer success from an empty
diagnostic file. If genuine pre-fix red cannot be obtained, report the precise
reason rather than reconstructing missing historical source.

Iterate only within this scope. A required coupling is a blocker with a
concrete proposed expansion, not permission to perform it.

7. Finish and hand off

Re-derive the task-only diff against this task’s new pre\ copies, including
normal and whitespace/EOL-ignored numstats. Record all changed paths and every
intentional protocol, classification, representative/message and exit delta.
Do not compare against HEAD or the earlier 136657-byte source as this baseline.

Re-hash preservation inputs, old evidence files read by this task, configuration,
lock files and the full output inventory. Recheck staging/dirty inventory and
prove that only the four allowed repository files changed. Existing compiled
repository JavaScript remains unchanged and is not qualified to run this repair.

Save baseline.json, post-state.json, task.diff, complete attempt evidence and
report.md only under the fresh task root. Serialize new JSON correctly; validate
the new artifacts without rewriting any previous evidence. Use display wrapping
for screenshots rather than inserting raw newlines into JSON string values.

The report must contain the focused protocol and its scope, counterexample
outcomes, trust/causal reasoning, actual local test results, precise preservation
proof, unresolved couplings and the unexecuted integration boundary.

End with:

```text
TASK_ID: ETL-0907-F5-CONTRACT-REPAIR01
RESULT: IMPLEMENTED_WITH_LOCAL_TESTS_AWAITING_INDEPENDENT_REVIEW | BLOCKED_<REASON>
FILES_CHANGED_BY_TASK: <exact paths>
FOCUSED_PRODUCER_DELIVERY_CONTRACT: <implemented/static evidence or blocker>
NORMAL_COUNTED_FAILURE_PARENT_VERDICT: <FAIL/nonzero evidence or blocker>
ABNORMAL_HOST_EXIT_RETENTION: <signal/numeric/unknown cases>
SINGLE_OBSERVATION_AND_PRELAUNCH_ELIGIBILITY: <evidence>
PRIMARY_TRIPLE_ORDER_INDEPENDENCE: <evidence>
LOCAL_UNIT_TESTS: <actual counts and measured exit status>
NO_EMIT_INTEGRATION_CHECK: <actual pre/post results>
CURRENT_BASELINE_PRESERVATION: <each boundary and evidence>
HISTORICAL_REVIEWED_BASELINE_PRESERVATION: NOT_VERIFIED
RUNNER_PRODUCER_OR_HOST_EXECUTED: NO
REPOSITORY_COMPILED_OUTPUT_CHANGED: NO
GIT_MUTATION_INSTALL_PACKAGE_OR_RELEASE_EXECUTED: NO
HOST_AND_CONSUMER_QUALIFIED: NO
NEXT_GATE: <fresh independent review if implemented; exact scope decision if blocked>
EVIDENCE_ROOT: <exact path or NOT_CREATED>
```

Do not claim F5 acceptance from self-review or full B3/runtime qualification
from pure unit tests. Leave the work and evidence intact, provide a concise
summary with the exact report path and remaining blockers, then stop.
