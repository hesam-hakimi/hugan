# Architecture

## Thesis

The orchestration runtime and the security/runtime adapters are intentionally separated:

```text
LangGraph
  = workflow, routing, checkpoints, interrupts, and resumability

Project-owned code
  = model provider, Git sandbox, repository tools, context compiler,
    artifact storage, policy enforcement, workers, and user interface
```

The graph never receives credentials. Nodes invoke narrow services with explicit contracts.

## Control-plane view

```text
Client / future web UI
        |
        v
Task Service
        |
        v
LangGraph Observe Graph
  | validate request
  | prepare isolated sandbox
  | index repository
  | compile planner context
  | planner role
  | optional plan-approval interrupt
  | read-only checks
  | independent reviewer role
  | final report
        |
        +--> SQLite checkpoints
        +--> Artifact store
        +--> Git mirror/sandbox store
        +--> Host model-provider adapter
```

## Graph state versus artifacts

Graph state contains only compact identifiers, status, counters, and artifact references. Large content is kept outside checkpoints.

```text
Graph state
- task ID / thread ID
- repository and immutable base SHA
- sandbox ID
- phase/status
- artifact references
- approval status
- safe errors

Artifact store
- repository manifest
- compiled contexts
- plan
- evidence
- read-only check results
- review
- final report
```

This keeps checkpoints small and makes context compaction independent from workflow persistence.

## Complex-task hierarchy

The planner returns a typed `PhasePlan` with slices and dependencies. Slices are not executed in the Observe MVP; they become the durable execution units in the Safe Development milestone.

```text
Phase
  +-- Slice A (no dependencies)
  +-- Slice B (depends on A)
  +-- Slice C (depends on A)
  +-- Slice D (depends on B and C)
```

Every slice defines:

- objective;
- included and excluded scope;
- expected paths;
- acceptance criteria;
- recommended check profiles;
- rollback note;
- stop conditions.

## Role isolation

### Planner

Receives the task, project manifest, instructions, relevant snippets, and constraints. Produces a typed phase plan and identifies missing decisions.

### Reviewer

Receives the original task, the typed plan, read-only check evidence, and independently compiled repository context. It does not receive private reasoning or a hidden implementer transcript.

### Future roles

Implementer, test/repair, security reviewer, and publish coordinator will be added as separate subgraphs with typed inputs and outputs.

## Persistence and resume

The compiled graph uses a SQLite checkpointer. Every invocation uses:

```python
{"configurable": {"thread_id": task.thread_id}}
```

A human approval gate uses `interrupt()`. Resume uses `Command(resume=...)` with the same thread ID. The approval node performs no side effect before the interrupt.

Before future write-mode resume, the service will revalidate repository identity, base SHA, branch, sandbox, diff hash, plan hash, and approval scope.

## Task cancellation

Safe execution has a task-scoped typed cancellation signal in addition to the persistent control
record. Every provider invocation and trusted test profile receives a cooperative checkpoint. UCA
registers only child processes that it starts itself: the host-provider bridge and fixed-argv test
profiles. A cancellation request sends termination to those active process groups, escalates to a
kill after a bounded grace period, prevents later task work from starting, and stores a durable
SQLite cancellation report with the observed operation kind and termination outcome. The isolated
sandbox is retained for evidence and deterministic finalization; the source repository remains
untouched.

P1.2b adds one opt-in in-process/remote adapter to `HostChatCompletionsProvider`. A trusted host
module may configure `UCA_HOST_CANCELLABLE_COMPLETION_FACTORY` and return a non-blocking handle with
`result()`, `cancel()`, and `done()` methods. UCA creates and registers that handle before waiting
for the remote completion, invokes `cancel()` from the task-control path, waits only for the bounded
coordinator grace period, and records the owned handle, cancel request, and still-active outcome in
the durable report. Existing P1.2a databases receive additive default-zero report columns.

The host factory is optional and trusted: it must return promptly, its cancellation hook must be
thread-safe and non-blocking, and `done()` must be non-blocking and accurately report transport
termination. Missing hooks retain cooperative before/after checks. Invalid configured handles fail
closed. A handle that does not terminate is explicitly reported as still active, so hard
cancellation is claimed only for registered child processes and host handles that actually
terminate. Other in-process and remote provider transports remain cooperative. No arbitrary shell
or model-controlled process execution is introduced.

P1.2c types and displays the same durable report in the local Product Control Center for standalone
tasks and persisted Program execution bindings. The UI shows operation kinds, owned process and
handle observations, terminate/cancel/kill requests, work still active after the bounded window,
and cooperative fallback. It does not add cancellation authority: pause remains a safe-boundary
control, and cancel requests active termination only for registered UCA-owned processes and
explicitly owned handles. The displayed counts are evidence of the observed outcome, not a blanket
claim that every provider or network transport was forcibly stopped.

P1.2d adds exactly one more opt-in owned-handle adapter to the already-supported pre-transfer
OpenAI Responses transport. `UCA_OPENAI_BACKGROUND_CANCELLATION=1` makes cancellable invocations
create a background response, poll its response identifier, and dispatch the documented remote
cancel request from a UCA-owned worker. The handle is registered before UCA waits; `cancel()` only
latches a non-blocking worker signal, and `done()` is a non-blocking read that becomes true only
after a terminal response status is observed. A cancel requested before the response identifier is
available is retained and dispatched as soon as creation returns an active response. The configured
request timeout also bounds the complete create/poll/cancel lifecycle, with only the remaining
budget passed to each HTTP call. During cancellation, network ambiguity, an unknown status, or a
cancel/retrieve call that outlives the existing bounded coordinator grace remains reported as still
active rather than forcibly terminated.

At the P1.2d baseline, durable still-active evidence was only the cancellation-time snapshot of a
currently registered handle. If the lifecycle timed out or failed, UCA ended its local wait with
unconfirmed termination and unregistered the handle; that slice did not persist or reconcile a
remote lease. P1.2f below deliberately closes only that restart-reconciliation gap.

The opt-in preserves `store=false`, but background execution necessarily has temporary provider
retention of roughly ten minutes for asynchronous execution and polling. Plain `invoke()`, the
default environment configuration, and foreground-only test transports remain synchronous and
cooperative; a foreground-only test transport combined with the background opt-in fails closed.
This slice adds no second transport, active pause, arbitrary shell access, publication path, or
broader hard-cancellation claim.

P1.2e adds a dedicated, fail-closed live qualification of that exact opt-in lifecycle. The probe
registers the real owned handle, latches cancellation immediately after handle registration, and
requires an active initial provider state, a returned cancel request, an observed terminal
`cancelled` state, one durable cancellation report, and an unchanged source checkout. A response
that completes before the remote cancel is dispatched does not qualify. The cancellation-time
report may accurately record the handle as still active when the provider needs longer than the
existing grace period; the probe then separately requires terminal cancellation within the
provider lifecycle timeout. The recorded lifecycle evidence deliberately omits the provider
response identifier. Existing foreground live qualifications remain unchanged and the final live
aggregator fails closed on the additional cancellation outcome.

The P1.2e baseline added qualification evidence only. It did not persist a remote-operation lease,
add another provider adapter, change active pause, widen cancellation authority, or introduce
publication.

P1.2f adds restart-safe reconciliation to that same opt-in OpenAI background-response transport.
Immediately after an asynchronous response is created, the provider writes one typed lease before
polling. The lease binds task identity, optional thread identity, immutable Base SHA when present in
the model request, transport type, a hash-addressed endpoint scope, creation/update times, lifecycle
status, cancel intent, action counters, and revision. The opaque provider response identifier is
stored only in `private-remote-operations.sqlite`, a database separate from task control, product
databases, artifacts, and workflow uploads. Public snapshots expose only a SHA-256 reference. They
never expose the identifier through API/UI state, safe diagnostics, logs, reports, or artifacts, and
no provider credential is persisted. UCA requests owner-only file permissions where supported but
does not claim that file mode alone supplies host isolation or encryption at rest.

Opening the Product workspace or reading task/Program execution state after a process restart only
reopens and displays the redacted lease; it starts no provider request. An active recovered lease is
marked as requiring an explicit action. The
`POST /api/tasks/{task_id}/remote-operation/reconcile` endpoint accepts exactly `observe` or
`cancel`. Each action performs one endpoint-scoped request with a ten-second-or-shorter request
bound, validates that the
returned identifier and lifecycle status match the lease, and durably records the outcome. Cancel
intent is committed before the remote cancel request. A confirmed terminal lease is idempotent and
causes no further network call. A missing/expired response (HTTP 404/410), endpoint-scope drift, an
unknown lifecycle state, or invalid persistence fails closed; unavailable remote state is recorded
durably where it can be established. Failure to persist a newly created response triggers a bounded
best-effort remote cancel and never enters the normal polling wait.

Recovery does not resume the interrupted graph, consume a completed response as model output,
retry a request, or advance a Program phase. The operator may only observe or request cancellation
of the orphaned remote operation. Deterministic tests reopen the private store and prove zero
network work before the explicit action. The live qualification creates an actual background
response in a child process, terminates only that local qualification process, reopens the lease,
explicitly observes and cancels the response, requires a provider-observed terminal `cancelled`
state and a durable redacted reload, and preserves the source checkout. The existing live
cancellation outcome remains the fail-closed aggregator boundary; the private lease database is
deliberately excluded from diagnostics uploads.

P1.2f still uses the provider's temporary background retention (roughly ten minutes even with
`store=false`). It adds no webhook, automatic restart work, output recovery, retry/replan policy,
second transport, active pause, arbitrary shell access, publication path, or broader hard-
cancellation claim. Remote termination is claimed only after a terminal `cancelled` status is
observed.

P1.2g exposes that bounded P1.2f recovery surface in the local Product Control Center without
adding backend authority. Standalone task snapshots and persisted Program execution bindings use
one typed remote-operation presentation containing only the redacted public lease: task and
transport identity, hash-addressed endpoint scope and operation reference, optional immutable Base
SHA, provider lifecycle status, durable cancel intent, revision, action counters, and timestamps.
The opaque provider response identifier remains absent. Recovered active operations, cancellation
intent without confirmed termination, terminal states, and unavailable state have distinct copy;
the UI claims remote cancellation only when the provider-reported state is terminal `cancelled`.
A terminal completion is not represented as recovered model output.

Loading an existing standalone task, loading or refreshing a Program, refreshing a task, and all
busy polling remain GET-only and start no provider work. An active lease becomes actionable only
when the API marks it as requiring explicit action and no local UI or Program worker is busy.
`Observe remote operation` performs the existing bounded observe action. `Request remote
cancellation` requires browser confirmation before calling the existing cancel action. After a
Program action the UI rereads Program and execution state; after a standalone action it applies the
returned public snapshot. Neither path resumes the interrupted graph, consumes output, advances a
Program phase, retries a request, or changes source.

P1.2g changes no provider transport, persistence schema, safety gate, cancellation coordinator,
active-pause behavior, workflow threshold, live aggregator, or publication boundary. The UI remains
local and single-user. The P1.2f temporary-retention and private-store limitations continue to
apply.

P1.2h adds one explicit terminal disposition for an orphaned remote operation after reconciliation
can no longer proceed: the durable lease must already be `terminal` or `unavailable`, and no local
standalone or Program worker may be active. The operator chooses exactly `cancelled` or `failed`,
supplies a reason, and sends `confirmed=true` to
`POST /api/tasks/{task_id}/remote-operation/dispose`. Active leases fail closed and retain the
P1.2f observe/cancel path. The disposition implementation does not reference the provider and makes
zero provider calls.

Task control stores one immutable redacted disposition with a SHA-256 audit reference, operator
confirmation, outcome and reason, the public operation/transport hashes, optional immutable Base
SHA, and the exact remote state, status, revision, and timestamp on which the decision was based.
It also records that no provider call was made, no output was consumed, the graph was not resumed,
and no Program phase was advanced. An exact repeat is idempotent; a conflicting replacement is
rejected. The task control record becomes terminal `cancelled` or `failed`, and a disposed task ID
cannot be reused or continued.

For a persisted Program binding, the same disposition is written as an artifact and its reference
is added to the binding. The binding and phase become `cancelled` or `failed`, and the Program
becomes `blocked`; it does not select or start another unit. UI controls require browser
confirmation and show the durable audit evidence for standalone and Program tasks. A lease marked
`unavailable` is explicitly described as unknown remote lifecycle state, never as confirmed
completion or termination. Provider-confirmed cancellation is claimed only when the captured
terminal status is exactly `cancelled`.

The restart live qualification now records and reloads this disposition after the existing real
provider cancellation proof and requires zero additional provider calls, redacted durable
evidence, and unchanged source. P1.2h adds no output recovery, graph resume, retry/replan, Program
phase advancement, automatic restart action, another provider transport, active pause,
publication, or broader cancellation claim.

P1.2i adds explicit local retirement of the private opaque lease only after that complete P1.2h
disposition exists. Retention remains the default. The operator must supply the exact durable
disposition audit reference, a non-empty retirement reason, and `confirmed=true` to
`POST /api/tasks/{task_id}/remote-operation/retire`. An active lease, missing or drifted
disposition, active local worker or lifecycle action, or mismatch in task, transport, endpoint
scope, operation reference, immutable Base SHA, remote state/status/revision/timestamp fails
closed before deletion. The action has no provider dependency and makes zero provider calls.
The destructive method is deliberately absent from the provider-facing
`RemoteOperationLeaseStore` protocol. Providers receive a restricted store view with only lease
registration, lifecycle update, and reconciliation reads. UCA-owned Product control and the
dedicated qualification retain access to the concrete private store's retirement capability.

The private SQLite store runs one `BEGIN IMMEDIATE` transaction that writes a typed redacted
retirement receipt and conditionally deletes exactly one matching opaque lease row. Either both
changes commit or both roll back. The receipt retains the disposition identity and outcome,
Program/phase/slice identity where applicable, public transport and operation hashes, immutable
Base SHA, exact remote lifecycle evidence, reason and timestamp, and explicit zero-work facts; it
never retains the opaque provider identifier in the active private store. The receipt hash is
recomputed and validated whenever it is loaded. An exact repeat returns the same receipt after a
lost response or restart, a conflicting repeat is rejected, and the durable tombstone prevents
reuse of the retired task identity. SQLite `secure_delete` is enabled for this private store to
overwrite deleted content in the active database where SQLite supports it, but P1.2i claims only
logical local row retirement—not remote provider deletion, encrypted erasure, backup cleanup, or
forensic destruction across storage layers.

Standalone retirement first proves that task control already has the matching terminal outcome.
For a Program task it additionally proves the persisted binding identity and terminal status, the
exact disposition artifact, terminal phase report, blocked Program status, and phase outcome.
The retirement action invokes no Task or Program mutation method, and its receipt records zero
Task/Program outcome changes made. Deterministic tests compare those records before and after the
action. One runtime reservation atomically excludes local workers and competing lifecycle actions;
the same reservation prevents a worker from starting concurrently. Reuse of a retained or retired
remote-operation task identity is rejected before discovery or provider work. An exact repeat of a
partially propagated P1.2h Program disposition first repairs and verifies its binding, artifact,
phase, Program, and report before retirement can proceed. The local Product Control Center
requires a separate browser confirmation, explains destructive local scope, keeps disposition and
redacted receipt visible after the private lease disappears, and never describes unavailable
remote state as termination.

Deterministic coverage proves default retention, explicit confirmation, atomic rollback after an
injected delete failure, exact-repeat concurrency, additive reopening of a P1.2h private database,
redaction, restart durability, identity drift rejection, Program evidence requirements, zero
provider work, and unchanged Task/Program outcomes. The existing restart live qualification now
retires the real disposed qualification lease, reloads its receipt and preserved disposition,
requires zero additional provider calls and absence of the opaque identifier from the active
private database, and preserves source. Workflow thresholds and the fail-closed live aggregator
are unchanged. P1.2i adds no output recovery, graph resume, retry/replan, automatic retention
policy, another provider transport, active pause, publication, remote deletion, or broader
cancellation claim.

P1.2j adds one read-only operator inventory for the private leases that remain after a durable
P1.2h disposition. `GET /api/remote-operations/retained-leases` returns an allow-listed,
identifier-free projection with task and persisted Program binding identity, last persisted remote
state/status/revision/timestamp, disposition audit identity and outcome, and a typed advisory
retirement-eligibility result. It never returns the opaque provider identifier, thread ID,
operation or endpoint-scope hashes, Base SHA, operator reasons, output, credentials, URLs, or a
retirement receipt. The strict response model also records that the page is read-only, made zero
provider calls, made no mutation, and exposed no opaque provider identifier.

The concrete private store performs an explicit-column, binary task-ID keyset read without
selecting `operation_id` or `thread_id`. Public requests default to 25 rows and reject limits above
100; the store reads one sentinel row to determine continuation. Rows without a durable disposition
are not returned, so a bounded page may underfill or be empty while a continuation remains. The
cursor advances over the scanned local task-ID keyspace, not provider identity. Refresh starts from
the beginning; the UI never polls or automatically traverses pages. The paging method remains
absent from the provider-facing `RemoteOperationLeaseStore` protocol.

Eligibility recomputes the canonical disposition hash, verifies the exact lease/disposition
binding and terminal task-control outcome, detects an active lease, local worker or lifecycle
action, and fails closed on conflicting or invalid retirement evidence. Program candidates also
require the persisted binding identity, terminal binding and phase, exact disposition artifact,
matching phase report, and blocked Program. Program identity is derived from the persisted binding,
not from untrusted disposition fields. Private-store locks are released before task-control,
runtime, Program, or artifact reads, and receipt presence is captured in the same private-store
query as the lease so an ordinary concurrent retirement is not mislabeled as corruption.

The inventory is an advisory, non-atomic view across separate SQLite stores, artifacts, and
in-memory worker state. The existing one-task retirement POST still requires a reason and browser
confirmation and revalidates under its lifecycle reservation; an eligible preview never claims
that retirement occurred. The same in-process reservation now excludes overlapping Program
approve/pause/resume/cancel controls in both directions, closing the Program-control race between
evidence validation and the private-store transaction. This remains a loopback, single-process reservation,
not a distributed or multi-process transaction. The React view offers only explicit Refresh,
bounded next-page navigation, and a GET-only jump to the existing task controls. It adds no direct
or batch retirement, TTL, automatic deletion, output recovery, resume/retry, Program advancement,
provider transport, active pause, publication, remote deletion, encrypted-erasure, backup-cleanup,
or forensic-destruction claim.

P1.2k bounds the two Program artifact reads used only by advisory retained-lease inventory
eligibility. The disposition artifact and phase report each have an explicit 256 KiB limit. The
artifact store reads at most one byte beyond that limit before UTF-8 decoding or JSON parsing, so
an oversized file is never loaded in full by this GET path. Either oversized artifact produces the
typed `program_evidence_oversized` blocker and leaves the item ineligible; malformed or missing
bounded evidence continues to use `program_evidence_incomplete`.

This limit does not apply to unrelated artifact consumers or alter the existing one-task
retirement POST, which remains the authoritative revalidation and mutation path. P1.2k adds no provider call,
mutation, lifecycle reservation, polling, automatic traversal, output recovery, resume/retry,
Program advancement, new transport, active pause, publication, or deletion authority.

P1.2l applies the same 256 KiB per-artifact bound to the Program disposition and phase-report
reads performed by the explicit retirement POST under its existing lifecycle reservation. Either
oversized artifact now fails closed before the private-store retirement transaction, so no lease
row or receipt is changed. Standalone retirement performs no Program artifact read. With valid
bounded Program evidence, confirmation, revalidation, receipt creation, and one-row retirement
retain their prior behavior and still make zero provider calls and zero Task/Program outcome
changes. P1.2l changes no API schema, retirement authority, provider facade, inventory semantics,
automatic action, output recovery, resume/retry, Program advancement, transport, active pause,
publication, or deletion/erasure claim.

P1.2m replaces the lifecycle-action and Program-control serialization boundary with a durable,
fail-closed SQLite reservation shared by Product runtimes that use the same workspace. A remote
operation action reserves its Task identity and persisted Program identity when present. A Program
approve, pause, resume, or cancel reserves the Program identity and checks every persisted binding
Task. `BEGIN IMMEDIATE` makes those conflict checks and insertion one transaction, so two runtime
processes cannot both win an overlapping Task/Program action. Release requires the exact internal
owner token and deletes exactly one matching row; missing, conflicting, malformed, corrupt, or
unavailable reservation state blocks the action.

The reservation database contains only local Task/Program identity, an unexposed random owner
token, action kind, and creation timestamp. It contains no provider identifier, operation hash,
endpoint scope, output, reason, credential, or URL. A reservation left by an interrupted process
survives restart and continues to block; P1.2m deliberately adds no TTL, startup cleanup, or
automatic recovery that could silently discard an active safety boundary. Read-only retained-lease
inventory includes durable reservations when computing its advisory lifecycle blocker. Existing
same-runtime worker exclusion remains unchanged. Explicit administrative recovery of an
interrupted reservation or worker-ownership row belongs to later production hardening.

Deterministic and live coverage proves cross-runtime Task/Program mutual exclusion, one winner
under concurrency, ownership-checked release, additive database creation, malformed-state
fail-closed behavior, restart durability, zero provider calls, redaction, and source preservation.
P1.2m changes no provider behavior, retirement authority, eligibility semantics, Task/Program
outcome, output recovery, resume/retry, phase advancement, transport, active pause, publication,
or deletion/erasure claim. This closes the bounded P1.2 sequence; any P2 production-hardening work
requires separate authorization.

P2.1a extends the same `0600` SQLite serialization boundary with durable ownership for standalone
Safe workers and Program execution workers launched by the Product Control Center. Worker
acquisition and lifecycle-action conflict checks share `BEGIN IMMEDIATE` transactions. A
standalone worker conflicts on Task identity; a Program worker conflicts on Program identity, so
remote-operation actions and Program approve/pause/resume/cancel controls cannot overlap across
Product runtime processes. Completion releases exactly one row with the unexposed random owner
token before the runtime publishes a non-busy, operator-actionable state.

Worker ownership contains only local Task or Program identity, worker kind, creation timestamp,
and owner token. It contains no provider identifier, operation hash, endpoint, output, credential,
repository URL, or source content. A crash-left ownership row survives restart and blocks; P2.1a
adds no TTL, heartbeat inference, startup cleanup, or administrative recovery. Retained-lease
inventory treats recovered worker ownership as an advisory `local_worker_active` blocker. The
slice makes zero provider calls and changes no provider behavior, API schema, React source,
Task/Program outcome, recovery authority, retry/replan policy, autonomous execution, active pause,
publication, safety threshold, or live aggregator.

P2.1b adds an explicit loopback administrative recovery path for a lifecycle reservation or worker
ownership row left behind after a process crash. A GET-only preview returns local Task/Program
identity, kind, timestamp, and a redacted hash bound to the exact persisted row. It does not infer
that the owner crashed: the operator must verify outside UCA that the process has stopped, supply a
reason, confirm the destructive local action, and select exactly one current recovery reference.
The current runtime rejects recovery when its own matching action or worker remains active.

The confirmed POST revalidates the exact row under `BEGIN IMMEDIATE`, inserts an immutable redacted
receipt, and deletes exactly one owner-token-matching serialization row in the same transaction.
The internal owner token is never returned or retained in the receipt. Exact retries are
idempotent; changed references, target mismatches, partial deletes, malformed state, corrupt audit
evidence, and concurrent replacement fail closed. Recovery makes zero provider calls and adds no
TTL, heartbeat inference, startup cleanup, batch cleanup, automatic recovery, remote-termination
claim, output consumption, graph resume, retry/replan, Task/Program outcome change, phase
advancement, transport, active pause, publication, threshold, or aggregator change.

P2.1c bounds the read side of that administrative surface without expanding its write authority.
Candidates use a stable `(target_type, target_kind, scope_id)` keyset; immutable receipts use an
independent `(recovered_at, recovery_ref)` keyset. The loopback API exposes only opaque, stream-bound
continuation cursors and accepts independent limits from zero through 100, allowing React to load
one stream without rereading or widening the other. Each page materializes at most `limit + 1` rows and
returns explicit count, `has_more`, and next-cursor metadata. GET remains cache-disabled and makes
no provider call or persistent mutation.

Before any page or explicit recovery, SQLite performs global type and length checks using bounded
metadata predicates. Oversized identity, timestamp, reason, hash, kind, ownership-token, or audit
flag state fails closed even when the bad row falls outside the requested page. Selected rows still
receive the existing semantic, timestamp, ownership, and audit-hash validation. The compatibility
snapshot is capped at 100 rows per stream and rejects larger state rather than restoring an
unbounded read. P2.1c changes no recovery confirmation, exact-row transaction, same-runtime block,
provider behavior, Task/Program outcome, TTL policy, automatic cleanup, retry/replan, phase
advancement, transport, active pause, publication, threshold, or live aggregator.

P2.1d makes immutable-receipt keyset selection index-backed through a named additive SQLite index
on `(recovered_at, recovery_ref)`. Store initialization creates that index for existing compatible
databases, attests its exact non-unique, non-partial two-column shape, and fails closed when a
same-named incompatible index or an unavailable schema prevents the invariant. Receipt pages use
the attested index explicitly, avoiding the previous full receipt-table scan and temporary sort in
the receipt-selection query while preserving the P2.1c cursor, limit, response, redaction, and
validation contracts. This slice does not claim to optimize the independent candidate UNION or
global validation predicates. It changes no recovery authority, provider call, Task/Program
outcome, automatic cleanup, TTL, retry/replan, active pause, publication, threshold, or live
model-dependent behavior.

P2.1e makes lifecycle recovery candidate selection index-backed through two named additive SQLite
indexes on `(reservation_kind, scope_id)` and `(worker_kind, scope_id)`. Store initialization
creates both indexes for existing compatible databases, attests each exact non-unique, non-partial
two-column shape, and fails closed when either invariant is unavailable. Candidate pages replace
the previous scan-and-sort UNION with two explicit keyset scans that share one remaining
`limit + 1` row budget. Reading the reservation stream before the worker-ownership stream preserves
the existing `(target_type, target_kind, scope_id)` ordering, cursor, limit, API, redaction, and
selected-row validation contracts. This slice does not optimize the independent global validation
predicates and changes no UI behavior, recovery authority, provider call, Task/Program outcome,
automatic cleanup, TTL, retry/replan, active pause, publication, threshold, or live
model-dependent behavior.

P2.1f makes the remaining global lifecycle-recovery field-bound checks index-backed through three
named additive partial SQLite indexes. Each index contains only reservation, worker-ownership, or
receipt rows that violate the exact existing type and length predicate for that table. Compatible
legacy databases pay one index-construction scan when first opened; subsequent recovery reads and
explicit recoveries force the corresponding violation index and retain detection of malformed
state anywhere in the table, including rows outside the requested page. Initialization attests
each exact non-unique partial shape, normalized SQL definition, and production query plan, and
fails closed when an index cannot be created or a same-named incompatible index is present. This
preserves all P2.1c global and selected-row validation semantics while removing valid-row table
scans from the steady-state field-bound checks. It changes no cursor, limit, API, UI, recovery
authority, provider call, Task/Program outcome, automatic cleanup, TTL, retry/replan, active pause,
publication, threshold, or live model-dependent behavior.

P2.2a adds the provider-neutral contract required before UCA may claim that an already-running
operation was actively paused. A trusted UCA-owned handle must expose non-blocking `pause()`,
`resume()`, `paused()`, `cancel()`, and `done()` hooks. The task-scoped coordinator latches pause
before any later pausable handle may be created. Registration requires the same signal's matching
active-operation scope, so an unbound or kind-mismatched handle is rejected before its factory can
run. The coordinator snapshots only registered owned work, invokes pause hooks outside its lock,
and accepts active pause only after every exact operation registration is still present, owned by
at least one observed pausable handle, and acknowledged within a bounded window with no unsupported
active work. Once acknowledged, later owned-operation starts fail closed until resume or cancel.
Otherwise the existing durable `pause_requested` state remains in force until the next Safe graph
boundary.

Each attempt stores a redacted SQLite report with operation kinds, observed handle counts,
unsupported-work counts, pause/resume requests and acknowledgements, safe-boundary fallback, and
missing-handle evidence. Active resume targets only the exact handles that acknowledged pause in
the same runtime. A restart has no such live ownership and therefore fails closed rather than
claiming that remote or in-process work resumed. In-runtime pause and resume transitions are
serialized per task; a concurrent duplicate control attempt fails closed while cancellation
remains available. Cancellation remains terminal and clears the in-runtime pause latch before
invoking the existing bounded cancellation path.

P2.2a itself registers no production provider or test transport and changes no HTTP or React
surface. At that foundation boundary, Host Chat, OpenAI Responses, host subprocesses, and trusted
test commands retained their existing cancellation and safe-boundary pause behavior. P2.2b was
therefore gated on a trusted, non-blocking, accurately acknowledged Host Chat pause primitive and
dedicated live host qualification. No OS process suspension, provider output consumption,
retry/resume automation, Task or Program outcome change, publication, or broader hard-control
claim was introduced by the foundation.

P2.2b adds an opt-in Host Chat adapter for that exact contract. A site enables it only by naming
`UCA_HOST_PAUSABLE_COMPLETION_FACTORY`; the factory must return one handle implementing the
existing result/cancel/done lifecycle plus non-blocking pause/resume/paused hooks. Configuration
of both the older cancellable factory and the pausable factory is rejected, and missing or
incomplete pausable contracts fail closed. The provider registers the handle only inside its
matching task-scoped provider operation, so HTTP pause/resume controls can report active
acknowledgement without widening ownership or transport authority. Unconfigured Host Chat calls
retain their previous synchronous or cooperative behavior, and the cancellable-only adapter
retains its previous behavior.

Dedicated live qualification is intentionally separate from deterministic tests. It observes the
site-owned handle without exposing model text, requires a stable acknowledged pause window,
requires acknowledged resume and completed inference, reloads the durable redacted pause report,
and verifies that the exact Git HEAD, tree, and clean status were preserved. The tracked runner is
manual and provider-local; it opens no application port and grants no workflow or remote execution
authority.

The adapter-level qualification passed on 2026-08-29 against the local
Qwen2.5-Coder-0.5B-Instruct Q4_K_M `llama-cpp-python` host. The exact qualified source was HEAD
`85b0fe6c7f81f75771b3091175f8a6c67f83f909` with tree
`ed557ef73ced91268e6c168c0ff02d1b4f8aba0d`. One owned provider handle acknowledged pause within
the existing bounded control call (`920.183 ms`), remained paused for the full `1500 ms` stability
window, acknowledged resume (`27.845 ms` control call), completed inference, reloaded the exact
durable redacted report, and preserved the clean source HEAD and tree. No unsupported active work,
cooperative fallback, invocation error, or source mutation was observed. This completes P2.2b for
the opt-in Host Chat transport only. The broader roadmap item for active pause across additional
provider and trusted-test transports remains open.

P2.2c introduces a separate opt-in trusted-test adapter without changing the default subprocess
runner. A site must configure both `UCA_TRUSTED_TEST_ADAPTER_PATH` and
`UCA_TRUSTED_TEST_PAUSABLE_FACTORY`; incomplete configuration, a missing module or factory, an
invalid handle, or an invalid result fails closed. The site-owned factory receives only the fixed
operator-approved argv, resolved sandbox cwd, restricted test environment, and bounded profile
timeout. Its handle must expose a bounded `result(timeout_seconds=...)` returning explicit
returncode/stdout/stderr fields plus the same non-blocking pause/resume/paused/cancel/done contract.
UCA registers that handle only inside the matching task-scoped test operation. Unconfigured tests
continue through the existing shell-disabled owned subprocess path with active cancellation and
safe-boundary-only pause; UCA does not suspend an arbitrary process or infer pause from stopped
output.

Deterministic coverage exercises stable progress while paused, acknowledged resume, cancellation
precedence, invalid configuration and handle rejection, full Safe graph source preservation, and
HTTP evidence with operation kind `test`. A tracked manual live qualifier observes the actual
site-owned handle, requires a stable acknowledged pause with the operation still unfinished,
requires successful resume and profile completion, reloads the durable redacted report, and checks
the exact Git HEAD, tree, and clean status.

P2.2c completed its dedicated adapter-level qualification on the trusted Azure host against HEAD
`5e36cf0d919a88a8c3e48c4a46f07b3cf31a8b1f` with tree
`25bebc1458597d60062b15be9d2e1cc7774ec7c7`. The site-owned trusted-test handle acknowledged pause
within the existing bounded control call (`53.659 ms`), remained paused and unfinished for the full
`1500 ms` stability window, acknowledged resume (`27.835 ms` control call), and completed the fixed
trusted profile successfully. The exact durable redacted report reloaded after reopening the control
store, with one owned pausable `test` operation, zero unsupported active operations, no cooperative
fallback, no test errors, and preserved clean source HEAD and tree. This completes P2.2c for the
explicitly configured trusted-test adapter only; unconfigured trusted tests retain the existing
shell-disabled subprocess behavior and safe-boundary-only pause semantics.

P2.2d introduces an opt-in cooperative pause contract for the HostSubprocess provider. A site
enables this path only by naming `UCA_HOST_SUBPROCESS_PAUSABLE_COMPLETION_FACTORY`; when the
variable is absent, the existing one-shot HostSubprocess bridge, owned-process cancellation, and
safe-boundary-only pause behavior remain unchanged. The configured factory runs in the trusted
host Python process and must return the same site-owned result/cancel/done/pause/resume/paused
handle contract already required by P2.2b. UCA does not infer pause from process state or from a
quiet output stream, and it never uses `SIGSTOP`/`SIGCONT` or another OS process-suspension
mechanism. The configured host-interpreter path is made absolute without dereferencing its final
symlink, because Python virtual environments rely on that invoked path to discover their adjacent
`pyvenv.cfg` and site-owned packages.

The opt-in path uses the dedicated `host_subprocess_pause_bridge.py` child-control bridge rather
than changing the legacy one-shot bridge protocol. UCA launches the child through fixed argv with
the shell disabled, then parent and child exchange bounded, versioned, strictly validated frames
over a dedicated inherited duplex control channel that isolates control traffic from site stdout.
Pause and resume count as acknowledged only after a child-originated acknowledgement reports the
underlying site handle's corresponding live state; merely delivering a control frame is
insufficient. Cancellation takes precedence over a pending or acknowledged pause, clears the
local pause latch, and retains the existing bounded termination fallback for cancellation only.
Protocol errors, missing hooks, unexpected EOF, oversized or out-of-sequence frames, and
acknowledgement timeouts fail closed. Durable pause reports and control-protocol failure
diagnostics retain only bounded control metadata and never model prompts, output, credentials, or
site configuration; the existing safe response diagnostics may still identify the requested
deployment.

OpenAI Responses is not eligible for P2.2d active-pause registration because its supported
background handle exposes observation and cancellation but no provider pause primitive. Stopping
local response polling would not pause remote inference and therefore cannot produce an active
pause acknowledgement. Deterministic coverage exercises the opt-in bridge contract, exact owned
provider registration, acknowledgement state, cancellation precedence, and the unchanged legacy
path.

P2.2d completed its dedicated adapter-level qualification on the trusted Azure host against HEAD
`5c8cd4f5e93a534c0fca19610991cc45b87c3b75` with tree
`9b9e9bbe594b0f606984319f8e43a9c9cfd2697c`. The site-owned HostSubprocess handle acknowledged
pause within the bounded control call (`638.766 ms`), remained paused and unfinished for the full
`1500 ms` stability window, acknowledged resume (`39.336 ms` control call), and resumed to
successful completion with no invocation errors. The exact durable redacted report reloaded after
reopening the control store, with one owned pausable `provider` operation, zero unsupported active
operations, no cooperative fallback, and preserved clean source HEAD and tree. This completes
P2.2d for the explicitly configured HostSubprocess adapter only; unconfigured HostSubprocess
providers retain the legacy one-shot bridge, owned-process cancellation, and safe-boundary-only
pause semantics.

P2.2 closes against the currently supported transport inventory. Host Chat, trusted tests, and
HostSubprocess now have explicit opt-in pausable-handle adapters and dedicated live host evidence.
The background OpenAI Responses transport remains intentionally ineligible because its provider
contract exposes observe and cancel but no remote pause primitive; pausing local polling would not
pause inference. The remaining provider modules are deterministic/test wrappers rather than an
additional production transport. A future transport must supply a real trusted non-blocking pause
primitive and receive separate authorization and qualification before UCA can extend this claim.

P2.3a adds an opt-in publish-approval gate without adding publication authority. A Safe task sets
`require_publish_approval=true`; after the canonical Git patch passes fixed tests and independent
review, execution interrupts with the exact Base SHA, plan hash, scope hash, canonical patch
reference and SHA-256, changed paths, test evidence, and review evidence. Resume requires an
explicit approve/reject decision plus the exact patch SHA-256. Before recording the decision, UCA
revalidates the materialized sandbox against the approved manifest and canonical patch. A missing,
malformed, stale, or mismatched hash fails closed and rolls back agent-owned sandbox changes.

The approval and rejection records are durable artifacts and survive service restart. Rejection of
an otherwise valid patch records that publication was not authorized while retaining the reviewed
sandbox patch for inspection. Approval authorizes only that exact patch; it still performs no Git
stage, commit, push, pull-request creation, merge, deployment, credential access, or source-repository
mutation. P2.3b's source-control-adapter transaction must consume and revalidate this exact
approval binding before it may perform any approved publication side effect.

P2.3b adds source-control publication as an explicit transaction after, and separate from, the
P2.3a approval resume. Recording approval never publishes automatically. The operator invokes
`safe-source-publish` with the task ID, the exact approval-artifact SHA-256, the exact patch
SHA-256, one bounded action (`commit`, `push`, or `draft_pr`), and a validated feature branch that
must differ from the base branch. This command dispatches without loading a model provider. Before
the adapter is called, the publication service performs bounded integrity-verified reads of the
approval and patch artifacts, revalidates the approval schema and task/thread identity, Base SHA,
plan hash, scope hash, ordered changed paths, successful tests and PASS review, completed Safe
task/control state, retained materialized worktree patch, and clean Git index. Test and review
artifacts are bounded and independently verified against the SHA-256 values sealed into the
approval. Missing, oversized, tampered, stale, rejected, cancelled, mismatched, or already-consumed
evidence fails closed before an adapter side effect.

The complete immutable intent binds the approval and patch hashes to the repository URL, base ref
and Base SHA, changed paths, feature branch, selected action, fixed commit/Draft-PR metadata, stable
adapter identity, and—for Draft PRs—the provider/account-scoped creator identity. Its canonical
SHA-256 and the approval SHA-256 derive a publication ID. A separate SQLite store and per-task file
lock reserve one intent per task and approval before adapter work. Conflicting reuse is rejected. A
completed transaction replays its immutable receipt without another adapter call, even if the
mutable sandbox or approval file has subsequently been cleaned up. A failed or crash-left `planned`
transaction may re-enter only the same exact adapter request so the adapter can reconcile its fixed
local and remote targets. Reported failures preserve bounded attempted-versus-verified local-ref,
push, and Draft-PR effect evidence. On the next exact retry, a crash-left attempt with no result
first receives a synthesized interrupted
receipt that explicitly marks effect attribution unknown. Only a completed receipt becomes
terminal.

The built-in Git adapter stages the canonical patch in an isolated temporary Git index with fixed
Git arguments and isolated global/system configuration, leaving the sandbox index untouched even if
the process is interrupted. It rejects unsafe repository configuration, symbolic publication refs,
replacement refs, grafts, shallow history metadata, and symlinked object/ref/reflog storage. It
disables replacement-object lookup and runs each local Git operation through a private Git-directory
proxy whose fixed common directory is the validated sandbox Git directory, making a sandbox
`commondir` override inert. It verifies the staged bytes and SHA-256, constructs a single-parent
commit whose parent is the exact Base SHA, and then
reads the raw commit-object headers to verify its parent, tree, paths, patch, and fixed message before
creating the explicit local feature ref. The publication service independently performs the same
raw-object and local-ref checks. Remote reads and pushes run from a fresh neutral Git client that
does not load mutable sandbox-local configuration; the service likewise verifies the exact remote
feature ref from a neutral directory before it records success. `push` uses
an explicit feature-only refspec with an exact zero-object lease: it either creates an absent remote
feature ref or recognizes the exact commit as an idempotent no-op. A pre-existing, divergent,
symbolic, or racing remote ref is never overwritten, and the base ref is never a push destination.
`draft_pr` additionally requires a
trusted Draft-PR creator and accepts only a result that remains Draft and binds the approved base,
feature branch, and exact commit. Deterministic qualification uses a temporary local bare remote and
explicitly authorizes local repositories only for that test; it covers exact commit and replay,
temporary-index interruption, lease-guarded creation, divergence, drift, retry reconciliation, capability,
and Draft-PR boundaries without hosted credentials.

Source-control loading is disabled by default and requires an explicit trusted `module:function`
factory. That adapter and its optional Draft-PR creator are the credential boundary: ambient Git or
provider credentials remain host-owned and are not sent to a model or stored in approval and
publication evidence. Repository and receipt URLs may not embed credentials; relative local paths
and local repositories are denied by default. Git prompts are disabled, commands use fixed argument
vectors with `shell=False`, and hooks, signing, unsafe config, external diff helpers, and replacement
objects are disabled. The public contract grants no arbitrary shell, non-fast-forward history rewrite, ref
deletion, tag, merge, deployment, or base-branch update authority. P2.3b therefore qualifies the
provider-neutral transaction and deterministic Git path; it does not claim a live hosted-provider
or hosted Draft-PR qualification.

P2.3c-a adds a built-in, default-disabled GitHub Draft-PR creator behind the same trusted
`module:function` factory boundary. The factory requires a host-owned API token, an exact
`owner/repository` allowlist, and a stable non-secret account or installation identity. Those fixed
values derive the adapter and Draft-PR creator identities sealed into the publication intent; the
token is retained only by the API transport and is not added to model input, subprocess arguments,
repository URLs, artifacts, receipts, or error text. Git publication still uses the P2.3b fixed
feature-only refspec and ambient host SSH agent. The GitHub token is used only for bounded ref reads,
same-head/base PR lookup, and Draft-PR creation.

Before looking up or creating a pull request, the GitHub creator proves that the request repository
matches the configured GitHub host and repository, and that the hosted base and feature refs equal
the exact approved Base and commit SHAs. It accepts only an open Draft PR in the same repository
whose base branch/SHA, head branch/SHA, title, and body exactly match the sealed request. One exact
match is an idempotent replay; a conflicting or ambiguous match fails closed. A create response is
accepted only after both refs are checked again, and an HTTP conflict is reconciled only by finding
that same exact Draft PR. API response reads are byte-bounded, redirects are rejected so the bearer
credential cannot cross hosts, returned URLs must be credential-free GitHub HTTPS URLs, and failure
evidence records only typed stages and codes. These deterministic contracts do not yet constitute
P2.3c-b live hosted qualification or authority to merge, deploy, update the base branch, rewrite or
delete refs, or create a non-Draft pull request.

P2.3c-b adds a dedicated, fail-closed live-qualification harness without widening publication
authority. The operator must start from a clean checkout whose HEAD is the exact approved Base SHA,
use a credential-free `git@github.com:owner/repository.git` URL pinned to the configured GitHub
repository identity, provide the API token only through the host environment, and provide Git push
authorization only through a host-owned SSH agent. The target head must be absent and use the
isolated `uca/github-live-qualification-...` namespace. State is written outside the source
checkout.

The harness obtains a normal Safe Mode scope approval and exact publish approval for one harmless,
dedicated qualification fixture. It then runs the production publication service and adapter to
create one exact single-parent commit, add only the isolated remote head, and create one same-
repository Draft PR. A fresh adapter must reconcile that exact ref and Draft PR without another
commit, push, or PR creation. A reopened publication service must return the immutable completed
receipt without calling the adapter. Before and after snapshots must prove that the base ref and all
tags are unchanged, no ref was removed or rewritten, and only the expected head was added. The
source HEAD, tree, and clean status must remain identical. Every generated state file, including
the final summary, is scanned for the configured bearer token, and failure summaries expose only
bounded exception type/code/stage metadata.

The qualification ref and Draft PR remain in place as durable evidence; the harness has no cleanup
authority because ref deletion is outside the approved boundary. It never merges, deploys, updates
the base branch, rewrites history, deletes refs, creates tags, or creates a non-Draft PR. The
deterministic local simulation validates this lifecycle without credentials, but P2.3c-b remains
incomplete until the same harness reports `GITHUB_PUBLICATION_LIVE_PASS` against the approved
hosted repository and isolated base branch.


## Accepted project knowledge packs

P3.1 adds immutable, versioned project knowledge-pack manifests above the existing text-document
store. A draft pack binds an ordered set of document identifiers to their exact SHA-256 digests,
roles, scopes, and project scope identifier. Version 1 must introduce a new pack; each later version
must supersede the immediately prior accepted version. Existing accepted versions are never
modified or deleted.

Acceptance is an explicit human action bound to the exact canonical manifest hash. Before recording
acceptance, UCA re-reads every bounded artifact and verifies its trusted content digest and stored
provenance. Missing content, content drift, role/scope drift, a cross-project document, an unaccepted
predecessor, or a mismatched approval hash fails closed. The acceptance receipt contains only pack,
project, version, manifest-hash, document-hash, and confirmation evidence.

Accepted packs can be indexed into a deterministic version-specific namespace. Replay first clears
only that namespace and then rebuilds it from the verified accepted manifest, making retries
idempotent without changing the accepted evidence. SQLite records and immutable artifact references
survive Product workspace restart. This foundation adds no model/provider call, automatic
acceptance, cross-project authority, source-control publication, merge, or deployment behavior.

## Accepted project decision and ADR records

P3.3a adds structured decision memory without treating repository ADR files or model output as
automatically trusted. Each draft is bound to a project ID, decision ID, version, optional immediate
predecessor, and bounded title, context, decision, rationale, alternatives, and consequences. Its
canonical JSON is written as an immutable artifact whose SHA-256 is also the human-approval key.
Version 1 introduces one project-scoped decision identity; each later draft must supersede the
immediately prior accepted version. The same decision ID may exist independently in another project.

Acceptance is an explicit confirmed action against the exact manifest SHA-256. Before recording it,
the service performs a bounded verified artifact read and revalidates the canonical manifest against
durable SQLite metadata. The immutable acceptance receipt binds project, decision, version, and
manifest hash and is itself hash-addressed and verified on every accepted read. Exact repeated
acceptance is idempotent. A stale approval hash, invalid version chain, missing acceptance evidence,
database provenance mismatch, artifact drift, malformed UTF-8/JSON, or oversize fails closed.

Indexing is also explicit. It first verifies the selected latest accepted version and every latest
accepted decision for the project, then deterministically rebuilds only that project's decision
`explicit:project-decisions:<project_id>` namespace as `SearchSourceType.DECISION`. Superseded
accepted versions remain immutable evidence but are removed from the active project index. An
unscoped search excludes every `explicit:` namespace; callers must name the project namespace;
P3.3a does not automatically inject decisions into model context or permit cross-project retrieval.
SQLite records, manifest and acceptance references, and index state survive Product workspace
restart.

This slice adds no automatic ADR-file discovery/import, UI or HTTP endpoint, model/provider call,
automatic acceptance, autonomous conflict resolution, arbitrary shell authority, source-control
publication, merge, or deployment behavior.

## Incremental repository index snapshots

P3.4a adds an explicit project-scoped repository index without changing the legacy manifest entry
point or automatically adding repository content to model context. Each immutable canonical
snapshot binds the project and repository identity, exact clean Git Base SHA, base ref, indexing
policy digest, file-size ceiling, search chunk policy, optional predecessor reference and digest,
and every eligible tracked file's Git mode, blob object ID, content digest, and extracted metadata.
The snapshot artifact has an independent byte ceiling and is read back through bounded digest and
canonical-hash verification.

An initial build requires an explicitly absent predecessor. Every later build uses
compare-and-swap against the exact active snapshot digest and requires the predecessor Base SHA to
be an ancestor of the requested Base SHA. Fixed-argument Git metadata identifies unchanged paths,
so their immutable metadata is reused without reopening their content. Changed eligible paths are
reprocessed; deterministic content-and-mode matching reports renames; denied and oversize paths are
excluded before content reads. A clean HEAD/Base check runs before construction and again before
state advancement. Source, artifact, policy, predecessor, ancestry, or working-tree drift fails
closed.

The search service stores the active snapshot provenance alongside project-isolated
`explicit:repository-index:<project_id>` code chunks. Deletions and replacements, changed-file
chunk insertion, and active-state advancement occur in one `BEGIN IMMEDIATE` SQLite transaction.
Failure rolls back both search and active state to the verified predecessor; an already-written
hash-addressed snapshot may remain as unreferenced immutable evidence. Exact retry and exact-Base
replay are idempotent, and SQLite plus artifact state survives Product workspace restart. Binary
files remain in eligible snapshot metadata when within the size limit but contribute no text
chunks; a text-to-binary transition atomically removes stale searchable content.

This foundation does not provide dependency/call graphs, test-impact analysis, semantic embeddings,
watcher or background indexing, dirty-worktree indexing, automatic model-context injection,
cross-project retrieval, UI or HTTP endpoints, arbitrary model shell access, publication, merge,
deployment, or production-readiness claims.

## Python dependency and test-impact evidence

P3.4b builds a deterministic, project-scoped Python module dependency graph only from a verified
active P3.4a snapshot. The graph is bound to the exact repository snapshot reference and digest,
project and repository identity, clean Base SHA, resolver policy, index policy, every configured
node, edge, unresolved-import, traversal, depth, and artifact byte limit, and its optional exact
predecessor graph. Index policy version 2 preserves leading dots in Python `ImportFrom` metadata so
relative imports remain distinguishable from absolute imports.

The static resolver maps Python paths to modules, including the conventional repository `src/`
layout, and resolves only exact absolute or package-relative module identities. A `from` import
prefers an exact in-repository child module and otherwise binds to the exact base module. Missing or
external modules, ambiguous module paths, invalid imports, and relative imports outside the package
boundary are retained as typed unresolved evidence; the resolver never guesses between candidates.
The graph records source-to-dependency edges and test classification but adds no symbol or dynamic
call inference.

Graph construction uses compare-and-swap against the exact active graph digest. An unchanged Python
node reuses its prior resolution only when its content metadata and the complete module map are both
unchanged; any module-map change safely recomputes all current Python nodes. The canonical graph is
written as a bounded hash-addressed artifact, then its active pointer advances only if the repository
snapshot is still exact. Repository snapshot provenance, graph predecessor, and active graph state
are checked in one `BEGIN IMMEDIATE` SQLite transaction. Failure leaves the active graph on the
verified predecessor; an already-written graph artifact may remain as unreferenced immutable
evidence. Exact replay and Product workspace restart are deterministic.

Test-impact analysis is explicit and delta-bound. Added and modified paths seed reverse-dependency
traversal in the current graph; deleted and old rename paths seed the verified immediate predecessor
graph. Cycles terminate deterministically, the shortest stable path is retained for each result,
depth zero and one are high confidence, and deeper transitive paths are medium confidence. Reports
include impacted source evidence but recommend only tests still tracked by the current snapshot.
Traversal count, depth, result count, and canonical report bytes are bounded, and every graph,
snapshot, predecessor, policy, and artifact mismatch fails closed.

P3.4b does not execute or skip tests automatically, claim coverage-minimal selection, infer symbols,
calls, dynamic imports, reflection, or runtime dispatch, analyze non-Python dependencies, watch the
worktree, inject model context, expose UI or HTTP endpoints, grant arbitrary model shell access, or
authorize publication, merge, deployment, or production-readiness claims. Those graph extensions
require a separately approved P3.4c slice.

## Deterministic Python symbol and static call-graph evidence

P3.4c-1 derives a project-scoped Python symbol and static call graph from one exact active P3.4a
repository snapshot and one exact active P3.4b dependency graph. The caller supplies both the
artifact reference and SHA-256 for each input. The service verifies the complete active provenance
chain before reading source, and the resulting graph binds project and repository identity, Base
ref and SHA, both input reference/digest pairs, the resolver-policy digest, configured limits, and
an optional exact predecessor call-graph reference/digest pair.

Source analysis is read-only and bounded. The checkout must have the exact clean snapshot Base SHA
before analysis and again before active-state advancement. Every regular tracked Python file is
read beneath the resolved source root, total source bytes are capped, and its size and SHA-256 must
match the verified snapshot and dependency node. Invalid UTF-8, invalid Python syntax, and
non-regular Git modes remain typed per-file parse evidence rather than silently disappearing.
Source text is not copied into the call-graph artifact.

Named functions, async functions, classes, and methods receive deterministic identities of the
form `python:<module>:<lexical-qualname>:<kind>:<line>:<column>`. Lexical qualified names retain
class nesting and Python-style `<locals>` segments for named definitions nested in functions.
Definition spans, async identity, parent identity, path, and module are evidence fields; duplicate
qualified definitions remain separate candidates instead of being collapsed.

The resolver emits an edge only when a call target is unique under its conservative static binding
rules. Supported evidence includes an exact lexical symbol, an exact symbol imported from an
unambiguous P3.4b module edge, an exact attribute on an imported module, and an exact method reached
through an explicit class identity. Parameters, assignments, `global`/`nonlocal`, unresolved
imports, wildcard imports, conditional bindings, duplicate or reassigned exports, dynamic
receivers such as `self` and `cls`, lambdas, decorators/default expressions, and unsupported callee
shapes never produce guessed edges. Each such call is retained with a typed reason, stable source
location and expression identity, and sorted candidate symbol IDs when candidates exist. Decorator
semantics are not inferred beyond preserving the underlying definition identity.

Independent limits cap total source bytes, symbols, edges, unresolved calls, calls per file, callee
expression bytes, and canonical artifact bytes. The full symbol-resolution index is hashed. Calls
for an unchanged file may be reused only when that file evidence and the complete resolution index
are unchanged; any symbol-identity, ambiguity, parse-state, module-map, or export-safety change
forces deterministic recomputation. A clean derivation produces the same files, symbols, edges,
and unresolved evidence as an incremental derivation.

The immutable canonical graph is written under its content hash and read back with a bounded digest
and canonical-hash check. Its explicit `repository_call_graph_state` pointer advances through one
`BEGIN IMMEDIATE` compare-and-swap transaction only while both the active repository snapshot and
active dependency graph still match every bound reference and digest. A failed transaction leaves
the prior active graph unchanged; an already-written artifact may remain as unreferenced evidence,
and exact retry is safe. Exact replay and Product workspace restart reload and reverify the same
bounded artifact. Clearing a project repository index removes only that project's dependent graph
pointers, preserving cross-project isolation.

P3.4c-1 does not infer runtime or dynamic dispatch, reflection, monkey-patching, dynamic imports,
decorator replacement behavior, inherited method resolution, or calls through values and
callbacks. It does not analyze non-Python languages, execute or select tests, claim coverage or
minimality, create semantic embeddings, inject model context, add UI/HTTP behavior, grant model
shell access, publish source control, merge, deploy, or establish production readiness. Those
capabilities remain separate, explicitly authorized slices.

## Conservative Python dynamic-dispatch evidence

P3.4c-2a adds a separate, project-scoped evidence layer over one exact active P3.4c-1 call graph.
The caller supplies the call-graph artifact reference and SHA-256, and the service verifies the
complete snapshot, dependency-graph, and call-graph chain before reading source. The canonical
artifact binds all three upstream reference/digest pairs, repository identity, Base ref and SHA,
policy digest, configured limits, and an optional exact predecessor evidence reference/digest.

The resolver records canonical class identities, direct base expressions, resolved in-repository
base candidates, and whether each hierarchy is safe for this bounded analysis. Only a unique
top-level class name, a unique imported class, or a unique imported-module class attribute is an
eligible type binding. Multiple inheritance, cycles, unresolved or unsupported bases, unsafe
symbol bindings, conditional assignments, decorated-method receiver conventions, and ambiguous
annotations remain typed unresolved evidence. They never produce candidate method targets.

Candidate sites are restricted to calls already recorded by P3.4c-1 as dynamic receivers. A
receiver type may come from an explicit simple parameter annotation, the undecorated instance
method receiver, or a direct local assignment from an exact class constructor. For an eligible
declared type, the evidence includes its known in-repository descendants and each unique method
implementation selected along a safe single-inheritance chain. These are conservative static
candidate targets, not proof of runtime dispatch, completeness over external subclasses, or
permission to replace the unresolved P3.4c-1 call with an executable edge.

Independent limits cap source bytes, classes, base expressions, dispatch sites, total receiver and
method candidates, expression bytes, and canonical artifact bytes. Exact replay reuses the active
artifact only while the complete active call graph and policy remain unchanged; a changed upstream
graph performs a deterministic full derivation. Source must match the exact clean Base before
analysis and before state advancement. The immutable artifact is bounded and hash-verified, and an
explicit SQLite pointer advances through one compare-and-swap transaction only while the active
call graph still matches every bound field. Transaction failure leaves the predecessor active;
exact retry and Product workspace restart are safe, and repository-index cleanup cascades without
cross-project deletion.

P3.4c-2a performs no runtime execution or tracing and does not infer reflection, monkey patching,
dynamic imports, decorator replacement, descriptor behavior, arbitrary MRO, callback targets, or
non-Python dispatch. It does not execute or select tests, claim coverage or runtime completeness,
inject model context, expose UI/HTTP behavior, grant arbitrary model shell access, publish source
control, merge, deploy, or establish production readiness.

## Host-attested trusted coverage evidence

P3.4c-2b1 adds a provider-neutral ingestion boundary for normalized per-test line evidence. The
service accepts only a canonical `uca-trusted-test-coverage-v1` receipt through an exact bounded
artifact reference and SHA-256. It does not accept raw Coverage.py JSON, `.coverage` databases,
arbitrary filesystem paths, aggregate Safe test-result artifacts, or producer-supplied symbol IDs.
The trusted host/test adapter must create the normalized receipt separately; this slice does not
execute tests or add arguments to an existing test command.

Each receipt binds the project and repository identity, Base ref and SHA, exact Git tree object ID
observed both before and after execution, and exact reference/digest pairs for the active repository
snapshot, dependency graph, static call graph, and dynamic-dispatch evidence. It also binds the
canonical whole `SafeModePolicy` digest and every selected `TestProfile` digest. Recording fails
closed unless every referenced profile is present in that operator-owned policy, reports a zero
return code and PASS, and explicitly attests complete collection and execution. An old receipt is
therefore invalid after a Base, source tree, policy, profile, or upstream evidence change, including
when two commits happen to share the same Git tree.

The receipt declares a sorted, hash-bound coverage scope and exact source digest for every scoped
file. Each completed test has a bounded opaque identity beginning with its separately normalized
tracked test path, the test file's exact snapshot digest, and canonical non-overlapping,
non-adjacent line ranges per covered file. A completed test may explicitly cover no scoped file, but
at least one completed test in the run must carry attributed line evidence. Unattributed line ranges
remain explicit evidence rather than being silently assigned to a test. Covered paths must be in
the declared scope and active snapshot, line ranges must fit verified UTF-8 regular-file content,
and source reads are deduplicated per verification pass across every regular file in the active
indexed snapshot under an aggregate byte ceiling. Every indexed file is matched to its exact Base
tree mode and Git blob object ID from live bytes, including Python files outside the declared
coverage scope. A tracked path excluded from the active snapshot is never opened and makes the
repository ineligible for coverage recording; so does any symlink, gitlink, unsupported index mode,
or index visibility hint such as `assume-unchanged` or `skip-worktree` anywhere in the tracked set.
Visibility and staged identity come from one bounded index read. Repository-configured fsmonitor is
forcibly disabled and its cached state ignored rather than executed or trusted; all eligible tracked
source is independently read and matched byte-for-byte. The trusted host must also preserve the
existing isolated-sandbox ownership boundary against direct concurrent filesystem or index mutation
while a receipt is being recorded.
This conservative byte identity deliberately rejects a checkout representation whose bytes differ
from the committed blob rather than invoking repository-configured content filters.

UCA derives, rather than accepts, symbol mappings. For each test/file pair it conservatively records
every exact P3.4c-1 Python symbol whose definition span intersects an observed line range. Nested
spans may therefore produce multiple symbol IDs, while non-Python files and Python lines outside a
known symbol remain useful file-level evidence. Explicitly unattributed ranges receive the same
symbol-span projection but remain unassigned to any test. This projection is not proof that a
function was invoked, that a dispatch candidate ran, or that a call edge is complete.

Independent limits cap input-receipt bytes, derived-artifact bytes, verified source bytes, trusted
policy and individual profile bytes, profiles, scope files, tests, files per test, total file
observations, ranges per file, total ranges, covered-line cardinality, derived symbol bindings,
symbol-intersection evaluations, emitted symbol-identity bytes, test-identity bytes, JSON structural
items and depth, an aggregate record-operation deadline shared by every Git verification, and each
Git process's aggregate captured output. Git verification suppresses repository-local fsmonitor,
hook, credential, protocol, lazy-fetch, external-diff, replacement-object, and ambient configuration
execution surfaces. A schema-aware streaming structural preflight rejects excess nested
cardinality, unknown or duplicate fields, missing required nested fields, and incompatible member
shapes before Pydantic model allocation; fail-fast iterable validation is a second boundary.
Incremental UTF-8 line counting avoids newline-density amplification. Derived canonical JSON
encoding stops before it exceeds its byte ceiling. The complete canonical input receipt remains a
separate hash-bound artifact, and the content-addressed derived artifact redundantly binds its exact
reference and digest. Bounded digest verification and a canonical-hash check protect every reload.

The active `repository_coverage_evidence_state` pointer advances only through an exact predecessor
reference/digest compare-and-swap in one `BEGIN IMMEDIATE` transaction. The transaction rechecks the
active repository snapshot, dependency graph, call graph, and dispatch evidence rather than trusting
a stale downstream pointer. A failed transition leaves the predecessor active; an already-written
hash-addressed artifact may remain as unreferenced evidence, and exact retry is safe. Exact replay
revalidates the input run, mappings, current policies, upstream chain, Base, and source tree.
Workspace restart reloads the same bounded artifacts, and repository-index cleanup removes only the
same project's dependent coverage pointer. A project-scoped immutable run ledger prevents one
`run_id` from later being rebound to a different receipt reference or digest, including after the
active coverage pointer advances or is cleared.

"Trusted" here means that the operator-owned policy, test runner/adapter, and state-root control path
are trusted inputs to the control plane. SHA-256 detects drift but does not authenticate a coherent
control-plane compromise. Repository code can still distort in-process instrumentation, and test
contexts do not prove causality for background threads, subprocesses, import-time work, native code,
or unsupported runtimes. P3.4c-2b1 does not claim complete runtime or branch/path coverage, select or
skip tests, claim a minimal safe test set, analyze additional-language dependencies, inject model
context, add UI/HTTP behavior, grant arbitrary model shell access, publish source control, merge,
deploy, or establish production readiness. Conservative selection and stronger privilege-separated
collection remain separately approved future work. Before P3.4c-2b2 may use this history for a
selection or skip decision, its separately approved contract must add and validate compatible
execution-environment and coverage-collector/configuration identities; this foundation does not
infer those identities from a Base or test-profile digest.

## Context management

The context compiler uses progressive disclosure:

1. project manifest;
2. discovered instructions and ADRs;
3. term-ranked relevant tracked files;
4. bounded snippets;
5. current task and phase plan;
6. latest check evidence.

It enforces per-role character budgets and stores the compiled context as an artifact. For a
dependency-ready Program phase, the orchestrator now compiles completed prerequisite phases into
one typed, hash-addressed, read-only evidence bundle. The bundle preserves the approved
requirement hash, immutable source Base SHA, phase result/report references, trusted test
references, independent PASS reviews, decisions, risks, and Safe execution references. Discovery,
Implementer, and Reviewer contexts receive the bounded bundle as evidence, not instructions or
edit authority. Missing provenance, a non-PASS review, missing test evidence, mixed Base SHAs, or
a current checkout that no longer matches the evidence Base SHA stops before new model work.

This handoff deliberately transfers no prior sandbox source or patch. Automatic full-program
execution, cross-phase patched-source integration, and retry/replan policy remain future work.

P3.2 extends that contract when the complete accepted evidence bundle is too large for one Safe
context. The control plane first writes the canonical source bundle under its SHA-256, verifies it
with a separate source-bundle byte ceiling, and then creates a deterministic compact handoff. The
handoff retains Program/phase identity, requirement and Base bindings, the immutable source-bundle
reference and hash, one exact digest per source phase, PASS verdicts, execution counts, and exact
count/hash metadata for changed paths, decisions, tests, and risks. Human-readable excerpts are
reduced through fixed profiles until the result fits the existing 48,000-byte Safe-context limit;
the complete accepted source remains addressable but is not copied into model context. If even the
provenance-only form or the source bundle exceeds its independent bound, execution fails closed
before model work. Small bundles preserve the existing accepted-phase-evidence representation.

## Portability

The public core has no customer or environment name. Integrations are plugins:

- model provider factory;
- source-control provider;
- sandbox backend;
- Linux/Windows worker;
- check-profile registry;
- persistence backend;
- artifact backend.

The first implementation uses ambient Git credentials, local Linux Git sandboxes, SQLite checkpoints, and a filesystem artifact store.
