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

Durable still-active evidence is the cancellation-time snapshot of a currently registered handle.
If the lifecycle itself times out or fails before a later cancellation request, UCA ends its local
wait with unconfirmed termination and unregisters the handle; it does not persist a remote lease or
claim that the response terminated. Persisting and reconciling failed remote-operation leases is
outside this slice.

The opt-in preserves `store=false`, but background execution necessarily has temporary provider
retention of roughly ten minutes for asynchronous execution and polling. Plain `invoke()`, the
default environment configuration, and foreground-only test transports remain synchronous and
cooperative; a foreground-only test transport combined with the background opt-in fails closed.
This slice adds no second transport, active pause, arbitrary shell access, publication path, or
broader hard-cancellation claim.

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
