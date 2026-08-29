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
mutation. The next source-control-adapter slice must consume and revalidate this exact approval
binding before it may perform any approved publication side effect.

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
execution, cross-phase patched-source integration, retry/replan policy, and general project-memory
compaction remain future work.

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
