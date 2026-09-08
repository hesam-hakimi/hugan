# P3.5d-2b-1 — V3 admission, settlement and quiescent continuation contract

Status: selected definition, not implemented or qualified. This contract is owned
by the [d2b-1 task](P3_5D2B1_V3_CONTINUATION_EXECUTION_TASK_2026-09-08.md), from actual
accepted PR27 `fdb97d3d10c8a843eae0ab71c255c3ebd0e6ac4a`, tree
`f1e78ac88cdb58c166e4fd51f672c54f9625f210`. It resolves the parent's d2b-1 schema,
helper-sharing and proposal-drift gates. API routes and source acceptance remain
with d2c-1 and d2b-2 respectively.

## Evidence from actual consumers and selected boundary

| Accepted code | Consequence for v3 |
| --- | --- |
| `program_continuation_handoff._semantic` binds all current Program/control/execution rows and rejects c2; `_change` requires that witness unchanged | Do not drive real execution through d2a receipts or change their false authority flags. Use separate v3 records and the accepted lifecycle transaction primitives |
| `program_source_dispatch.admit` calls c1 `_finish_locked(..., allow_fill=False)` before pending phase changes and freezes preparation/material rows | Consume unchanged c1 proof in the original owner episode; preserve consumed bytes as history, with a separate current v3 witness |
| C2 `_authority` / `_load` compare the exact owner/control and four-column registry | No rebind of v2 receipts, no v2 migration, no additional column in the old registry |
| `AdmittedSafeExecution` arms a durable digest but holds the secret ticket in one live object; its nodes recheck current files/control | V3 needs its own exact adapter and live tickets, equally strict node boundaries and explicit final revocation |
| Discovery's `discovery_completed` / `start_safe` execute inside the outer admitted start call | A discovered record is not an invocation-return proof and is not a parked boundary in this slice |
| Safe graph `get_state` supplies the actual checkpoint; c2 includes bounded raw pending interrupt writes | Bind both actual decoded graph state and exact checkpoint/write bytes; absence of next nodes alone is insufficient |
| `CancellationCoordinator` owns operation/process/cancellable/pausable registries | Add a narrow registration barrier and live settlement proof; a new process's empty registry proves nothing about its predecessor |
| Safe checkpoint root pins its control database; `_execution_gate` currently only checks c2 | Add a durable task-version deny guard before admission and exact version routing, including surviving-marker failures |
| Old acceptance `_dispatch_for` returns None on absent c2 row; Program/status have positive v1 rules | Add early v3 denials, never exception fallback to v1 or terminal v3 source acceptance |
| Web workers release ownership after results/exceptions | No v3 web wiring here; only the host consumer may atomically release after positive settlement |

Paths in this table are under `src/universal_coding_agent/`, principally `product/`.
These are bounded source observations, not a new independent repository audit.

## Identity and immutable records

Eligibility remains an actually approved, unsliced linear Program with one active
unit, a verified accepted predecessor and host-owned repository/provider/test
configuration. Revalidate the real requirement, approved plan and phase ordering;
caller-supplied IDs or a stored descriptor do not establish these facts. The host
pins synchronous transport capability and publication-disabled policy at admission
and every fresh-worker action. No new retry/replan or phase-DAG executor is added.

Dispatch schema is exactly `uca-program-source-dispatch-3`. It is unrelated to the
Safe edit protocol (`v1` or `v2-line-addressed`), which remains independently pinned
in the host/admission. Do not overload schema 2 or d2a's schema 1.

| Record schema | Required bound content |
| --- | --- |
| `uca-program-source-dispatch-3` | Operation/Program/phase/task/thread; host/policy/edit protocol; requirement/plan; accepted generation/source/receipt; immutable c1 preparation/materialization receipt and full frozen rows; origin repository/Base/tree; derived Git commit/tree/object format; dependency evidence; initial owner witness; deny-guard digest |
| `uca-program-continuation-authority-3` | Admission hash; epoch; current full Program/phase/execution/control/source witness; complete actual lifecycle exclusion set and exact owner-row digest; immutable filesystem/retained-source proof references; current state and predecessor receipt |
| `uca-program-continuation-settlement-3` | Admission/epoch/action/request/invocation digest; actual returned boundary; exact checkpoint and writes hash; task/scope/result references; current file/control witness; live invocation revoked and all owned registrations absent; remote-store absence proof |
| `uca-program-continuation-proposal-3` | Admission, parked epoch/receipt, settlement, actual checkpoint/task/scope/dependency/source and immutable c1 references; exact current non-owner witness; only next action `scope_decision` |
| `uca-program-continuation-scope-decision-3` | Request ID, proposal/parked receipt/epoch, exact scope hash, approval ID and strict boolean decision; new epoch and current authority digest |
| `uca-program-continuation-receipt-3` | Immutable predecessor-linked action/request result, admission, old/new epoch, settlement/proposal/decision/result references, stored public outcome; no private row/token/capability |
| `uca-program-continuation-request-3` | Host/Program/request identity, action and canonical payload digest, pending/completed state and immutable completed response receipt |

The implementation must define exact allowlists per record and reject unknown or
missing fields, duplicate JSON keys and alternate encodings before use. Null fields
are explicit and state-specific, not wildcards. Hashes bind canonical bytes; they
are not signatures, evidence by assertion or authorization. Public records may say
`consumer_bound=true` for this v3 consumer but must always say
`execution_authorized=false`, `automatic_execution=false` and
`source_acceptance_authorized=false`. An action's eligibility is advisory; only
the current private live adapter can cross an execution boundary.

Use additive Program tables `program_source_dispatches_v3`,
`program_source_continuation_heads_v3`, `program_source_continuation_receipts_v3`
and `program_source_continuation_requests_v3`. Content-addressed records may use
the existing bounded immutable `program_source_artifacts`; do not rewrite existing
blobs. Key dispatch/admission by operation with unique task/thread, and continuation
heads by operation with at most one nonclosed v3 operation per Program. Receipt
hashes are immutable and predecessor-linked; requests are unique by host/Program/ID.
One consumed preparation can never admit another operation. Closed history remains
available without blocking a later, separately authorized phase forever.

The separate control table is `uca_source_dispatch_tasks_v3` with exactly
`task_id`, `thread_id`, `admission_sha256`, `host_sha256`; both task and thread must
be unique. Keep c2's original four-column table and whole-row checks unchanged.
Registry, admission, head, execution and checkpoint guard must agree on version
and identities. A digest match alone does not replace proof of their contents.

## Durable route exclusion before admission

Before atomic admission, persist an immutable task/thread/version/host/admission-
intent guard in `safe.uca_source_dispatch_tasks_v3_guard`, alongside the existing
checkpoint-root control path/device/inode binding. The guard binds the canonical
admission intent, not an epoch or ticket. Its schema is
`uca-program-source-dispatch-guard-3`; admission references its digest. Intent omits
the guard digest to avoid a circular hash. Admission contains the exact intent and
its digest plus the guard digest. No guard field authorizes execution.

This is a separate Safe-database transaction before the atomic Program/control/
lifecycle admission, like the existing root binding. It must be durable and checked
again by admission; require FULL/EXTRA, and allow rollback or WAL for this single-
database write. An orphan guard after a crash blocks the task from all execution.
The same explicit pending admission under its still-valid original owner may verify
the identical guard and finish admission; no different task/version or reconstructed
invocation can adopt it. Incomplete c1 preparation is not repaired by admission.

Every actual Safe/discovery effect entrypoint checks root binding, both registry
namespaces and any surviving task guard before provider/sandbox/discovery writes.
Raw run, scope resume, publish resume and control resume must all reject a guarded
v3 identity without the exact live v3 adapter/action. C2 adapters cannot enter v3,
v3 adapters cannot enter v2 or unadmitted v1, and structurally similar objects or
subclasses do not qualify. Cross-version task/thread collisions reject before
either admission mutates; serialize both admissions on the same control writer
boundary and recheck the Safe guard while checkpoint writers are excluded.

Old Program execution routes and old acceptance capture/prepare/accept/replay must
reject any v3-bound task/operation before their first effect. Existing public source
status may expose a bounded unsupported-version blocker; adding the complete v3
Product projection is d2c-1. Missing registry, head, admission, preparation or guard
with surviving v3 evidence is corruption, not v1. If all dispatch markers are
removed but a derived-Base execution survives, retain PR26's positive v1 eligibility
rules and combined-metadata rejection. Unknown schemas and impossible state pairs
fail closed. These are narrow denials, not an expanded v1/c2 evidence interpretation.

An active or parked d2a foundation for the Program blocks v3 admission. Its owner
must close it through the accepted inert protocol before preparation/admission.
Closed d2a history stays inert. Conversely d2a create/park/claim/close must reject
a Program with an active v3 execution/continuation, including partial v3 history;
otherwise an inert metadata call could release a live consumer's worker. No d2a
receipt is adopted, relabeled or rewritten, and d2a exact historical replay remains
public and capability-free.

## Transaction composition and current proof

Use the actual `ProgramSourceAcceptanceService` connection already shared by c1
and materialization, under its lock, as the v3 effect transaction connection.
Do not swap an object's connection, call nested public committing methods or use
reserve/release before or after a separate receipt commit. A v3 transaction wrapper
owns BEGIN/commit/rollback, the necessary read-only remote attachment and its scoped
SQL authorizer. Call unchanged c1 `_finish_locked(..., allow_fill=False)` on this
same connection before the phase ceases to be pending; compare exact requested
receipt, source head, frozen rows, immutable bytes, inventory, inode and actual Git.
Short bounded c1 filesystem/Git attestation is retained. No provider, discovery,
apply, test, review or long-running execution subprocess runs inside a DB transaction.

Modified participants are Program, control and lifecycle: all must be distinct
existing on-disk rollback-journal files at FULL or EXTRA on original and attached
connections. V3 writes the control registry/admission and can record existing
terminal Program control transitions, so WAL control is rejected for v3 effects
without changing its PRAGMA. This does not restrict d2a's accepted logically
read-only WAL control support. Initialization is explicit; GET never initializes.

Safe checkpoints and the private remote-operation store are logically read-only
attachments in the multi-database transaction. Open with writer-excludable handles
and BEGIN IMMEDIATE; retain exclusion through commit even in WAL. Deny every
actual write to those attachments with the authorizer. Check their actual pinned
path/device/inode, availability and durability before proof. Do not infer writer
exclusion from a read snapshot. Deny unrelated Program/control/lifecycle writes,
trigger side effects and schema changes during effects. Source-head/candidate/
acceptance tables are never writable by v3 dispatch. Dedicated initialization and
the separate deny-guard write have explicit smaller allowlists.

Define a consistent in-process lock order around the shared store/control and
invocation registry, with bounded acquisition and cleanup on every exception.
For sealing, hold the task's registration barrier from the positive no-work check
through commit; no provider callbacks run under it. The implementation review
must inspect the existing control-to-cancellation call order and probe contention
for deadlocks as well as stale commits. Locks may not authorize replay on timeout.
Database atomicity does not make filesystem changes atomic; retain the existing
tracked rollback and ambiguous-partial-apply exclusions.

Each v3 node entry/exit and each state transition revalidates the exact current
epoch/owner, Program/phase/execution/control revisions, trusted host and policy,
source generation/head, frozen preparation/material rows, dependency evidence,
retained accepted bytes and owned execution-tree/Git/inode proof. Only the exact
expected writes of the current live action may change its current witness: initial
admission, validated Safe graph progression, the approved patch and normal
finalizer task-control completion. Arbitrary recapture followed by replacing the
witness is forbidden. Terminal/rollback evidence uses actual Safe/test/review state.
C2's verifier/adapter code is not weakened or shared through duck typing.

## Actual invocation settlement

A v3 invocation has a random process-local secret, a durable digest, action kind,
epoch and one CAS from armed to claimed. Only the same live object may claim it.
Admission, a receipt, request replay, process restart or the old private worker token
cannot reconstruct it. The current ticket is invalidated before another is armed.
Discovery and the Safe run are one outer action for quiescence purposes; internal
stage tickets may be distinct but cannot escape the same owned action.

Settlement is a private consumer operation after the outer actual discovery/Safe
call returns and the checkpointer has completed its writes. It must prove all of:

1. That live invocation has no executing node/callback or pending stage and has
   irreversibly revoked all its tickets. The live call-return fact is not accepted
   from a caller boolean, supplied checkpoint, elapsed time or a reconstructed object.
2. The actual `CancellationCoordinator` has no registrations for the task in any
   owned operation/process/cancellable/pausable/paused set. Hold a registration
   barrier through commit and reject late registration from revoked v3 contexts.
   Paused or apparently done-but-still-registered handles do not qualify. A freshly
   empty coordinator cannot manufacture a predecessor's settlement.
3. The actual private remote store has no lease or retirement for this task/thread.
   In this first slice only synchronous, fully returned provider/test transports
   without retained remote-operation identity are eligible. Reject unsupported
   remote-lease transports at admission and any unexpected retained row at seal;
   unavailable/unknown/retired remote state never proves quiescence. No provider
   polling, lease retirement or remote recovery is added here.
4. The current exact checkpoint and pending writes are pinned while their writers
   are excluded. Read the latest root namespace row with size checks before BLOB
   retrieval, and decode actual graph state for that exact checkpoint identity.
   Task/thread/sandbox/admission, next nodes, tasks, interrupt data, scope and stored
   immutable discovery artifacts must agree. No semantic-only hash substitution.
5. Full current authority and filesystem proof still match at commit. Concurrent
   pause/cancel/recovery/source changes either serialize afterward or cause rejection.

For a resumable seal require exactly `next == ('scope_approval',)`, actual status
`awaiting_scope_approval`, undecided scope, and only the matching scope-approval
interrupt task/write structure produced by the actual graph. Validate the exact
supported LangGraph task/write shape from a real fixture; reject extra namespace,
extra task, error, decision/resume or unrecognized write. Do not demand zero pending
interrupt writes at a legitimate scope stop. For a terminal seal require no next
nodes, no pending tasks or writes, actual completed/failed/blocked evidence and
exact test/review/rollback/result binding. An exception or missing result is not
automatically terminal. Source-control publishing must remain disabled.

After positive settlement, persist its immutable record in the same transaction
that records the Program stop/result, revokes the durable invocation state, writes
the continuation receipt/request/head and releases the exact lifecycle owner row
using the accepted full-row CAS primitive. There is no independently trusted
caller-operated `park(quiescent=True)`, no release in a generic exception/finally
handler, and no intermediate durable settled-but-owned success state in this slice.
Artifact files written before binding use immutable state-addressed paths; orphans
after failure are not authority and existing reports must not be overwritten.

## Explicit actions and state transitions

The Python host surface is `ProgramContinuationDispatchService` with explicit
`admit`, `dispatch`, `approve_scope`, `reconcile`, `status` and `request_result`.
No browser parameters choose paths, transport or policy. Operation/Program identity,
request ID and expected epoch/receipt are explicit; methods never pick the latest
operation or approve a changed proposal silently.

| State / action | Required authority | Atomic outcome / permitted work |
| --- | --- | --- |
| Absent / `admit` | Current reserved worker; exact complete c1 receipt under that same owner; positive guards and full current proof | Admission/registry/execution/head/request at epoch 0, worker retained, no provider call |
| `admitted` / `dispatch` | Same current owner; exact admission/epoch/receipt and new explicit request | Arm/claim one live action, then actual discovery and Safe outside the transaction |
| Live action returns at scope | Positive settlement above under that live owner | Actual Program awaiting-scope result plus `parked_scope` proposal/receipt; exact worker released atomically |
| `parked_scope` / `approve_scope` | Exact proposal/parked receipt/epoch, scope hash, approval ID and strict boolean; full unchanged non-owner proof; no conflicts | Reserve fresh worker, advance epoch, consume proposal, persist exact decision and arm a new live adapter in one transaction; then call actual Safe resume once |
| Live action returns terminal | Positive terminal settlement under the exact current worker | Actual terminal-unaccepted result/report, `closed` receipt and exact worker release atomically; accepted source unchanged |
| Owned interrupted/unknown | Existing exact ownership and current diagnosis only | Project `recovery_required`; no new ticket, inferred release or provider replay |
| Any completed request replay | Same canonical request identity/content | Exact immutable public result only; no new epoch/worker/token/ticket/provider or source action |

`approved=false` is an explicit consumed scope decision, not permission to edit.
The graph's actual rejection result must be recorded after settlement; it cannot
be represented as successful test/review or source acceptance. Failed execution
and blocked rollback retain their actual outcome, never a fabricated PASS.

`admit` and `dispatch` keep preparation/consumption in one original owner episode;
there is no prepared-base park. `approve_scope` reserves its new worker internally
using the attached transaction, after checking all actual Program task conflicts.
Public input cannot supply a replacement owner binding. Raw worker tokens and live
tickets remain private to the host process and must not enter public receipts,
status, reports, logs, exceptions or request digests. An owner-row digest is allowed.

Canonical request content includes action, operation/admission, expected state/
epoch/receipt/proposal and exact decision fields. Exclude the private token from
replay identity; its original value is never restored. Record pending before any
effect and complete only with the immutable outcome commit. Same request ID with
different content rejects. Unknown/pending/lost-ticket states cannot retry work.
Historical request lookup returns the result as recorded, without claiming current
eligibility. A duplicate arriving during execution returns a bounded in-progress
diagnosis, never a second invocation. No automatic paid retry or effect scheduler.

`reconcile` is explicit and provider-free. It may only finish sealing with the
still-live original invocation's already-observed return/revocation evidence and
its exact current owner after a reversible recording failure. It cannot infer
settlement from checkpoint presence in a new process, reconstruct a lost live
capability, re-enter a graph or synthesize PASS. Since settlement and park/close are
one commit, a process crash before that commit may remain blocked even if a valid
checkpoint exists. Exact administrative worker removal is only recovery history;
it does not enable rebind in d2b-1. The guaranteed restart path is after successful
parking, when no owner or invocation remains.

Control/policy/source/plan/host drift, pause then resume, disposition or administrative
recovery invalidates the old proposal. This slice does not refresh/rebase proposals
after those changes. Reject with a bounded diagnosis; any future refresh protocol
needs its own concrete definition and fresh explicit approval. Ordinary fresh-worker
claim verifies the unchanged parked proposal using the new current witness; it does
not rewrite immutable evidence with a new token or waive changed control revisions.

## Bounds, preservation and evidence ownership

Use strict 128-byte identifiers, 64 KiB per public metadata record, 1 MiB metadata
aggregate per read, depth 8, at most 64 fields per object, 4 KiB scalar strings,
100 records per keyset page and bounded SQL work. Keep large actual checkpoint,
file and dependency evidence in separately bounded content-addressed storage;
references do not let status deserialize those blobs. Check checkpoint plus metadata
at 16,000,000 bytes before retrieval, and pending writes at 128 rows/16,000,000 value
bytes before retrieval, also bounding encoded output. Preserve stricter existing
source/filesystem policy bounds and the 48,000-byte dependency-context bound.
Reject oversized/corrupt historical records needed for an effect; never silently
truncate the proof or scan unbounded receipt chains to grant authority.

Read-only `status` / `request_result` use dedicated existing-file URI `mode=ro`
connections with query-only and bounded parsing; no effectful service constructor,
checkpoint setup, schema initialization, recovery, reconciliation or new proposal.
No raw worker/control/remote identifiers or tokens appear in public records. Show
historical state, stored hashes, terminal-unaccepted status and typed blockers only.
Metadata cannot certify current quiescence or authorize an action on GET.

Acceptance requires V01-V12 in the task with actual processes/stores and a separate
independent reviewer. In particular reproduce PR27's control race at v3 transitions,
hold actual provider/owned work alive past checkpoint creation, inspect both sides
of every crash commit, and probe all legacy effect entrypoints. Preserve original
and retained source bytes, c1 pending verifier semantics, c2 exact owner behavior,
d2a false flags and PR26 F1/F2. No result here qualifies later candidate-2/approval-2,
accepted generation 2, Product HTTP/UI, live-model cumulative v3 or a scheduler.
