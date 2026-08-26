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
