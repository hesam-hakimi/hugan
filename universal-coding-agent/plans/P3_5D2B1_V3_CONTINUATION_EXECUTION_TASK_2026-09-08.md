# P3.5d-2b-1 — Explicit v3 execution across quiescent worker episodes

Task ID: `UCA-20260908-P35D2B1-V3-CONTINUATION-EXECUTION`

Status: bounded implementation candidate under author verification. The definition
was published at `7f2286f3395658b28ad4d7a3e2921116bbdd51ac`; runtime work begins from
that exact definition. Independent acceptance and current-tree platform qualification
remain separate submission gates. D2a is accepted and complete.

## Initial blocked candidate and correction scope

Initial implementation `de99db9fdff64745d76f07ff6061044534851642`, tree
`c15863e8e05f5f662560da0fe5a3144b59bc93af`, was independently BLOCKED for raw
Safe routing after guard namespace loss, incomplete closed d2a history,
unbounded v3 registration lock waits, and mutating-PRAGMA authorizer gaps.
The correction adds an immutable independent root locator and plain checkpoint
version denial, complete bounded inert predecessor validation, bounded new v3
registry waits with monotonic revocation, and read-only PRAGMA allowlists. CI441
attempt 1 failed both Python legs (1612 passed, one child-import harness failure
per leg); that harness now supplies its fixture import path explicitly. Live192
attempt 1 passed on the initial preview `cc9bee057af186f74c66e5aebfe7a92495118e3a`.
These observations remain initial-tree history. Corrected-tree independent review
and platform outcomes are recorded separately in PR28 and external evidence;
no initial result substitutes for those gates. Standard Live Program remains v1.

## Accepted starting point and authority

Repository: `hesam-hakimi/hugan`. Integration target:
`feature/universal-coding-agent-structured-edits`. Start this slice from actual PR27
integration `fdb97d3d10c8a843eae0ab71c255c3ebd0e6ac4a`, tree
`f1e78ac88cdb58c166e4fd51f672c54f9625f210`. Its ordered parents are
`132f1410661e9c3a9034c9d6cd9400eebeda65f9`, then
`dc60201f618c67e9afbdf263c75360df823ef783`. The preview
`cf33eb76114bfe3154002e665e75f2e741386de3` is not the actual merge identity.

Definition branch: `feature/universal-coding-agent-continuation-dispatch`.
Bounded engineering authority continues without routine owner reconfirmation.
The preceding definition-only phase completed without runtime changes. The current
engineering phase implements this task under the continuing bounded authority.

Read the full current checkpoint/state/master/status and observed sync receipt,
both PR27 reports, the [d2a task](P3_5D2A_PROGRAM_CONTINUATION_HANDOFF_TASK_2026-09-08.md),
[parent design](P3_5D2_PRODUCT_CONTINUATION_DESIGN_2026-09-08.md),
[delivery matrix](P3_5D2_VALIDATION_AND_DELIVERY_MATRIX_2026-09-08.md), both
[c1](P3_5C_EXECUTION_BASE_CONTRACT.md) and
[c2](P3_5C2_ADMISSION_AND_RECOVERY_CONTRACT.md) contracts, and actual consumers.
The binding consumer decisions are in the accompanying
[v3 admission and quiescence contract](P3_5D2B1_V3_ADMISSION_AND_QUIESCENCE_CONTRACT.md).
These plans are repository-owned; do not create separate canonical copies.

PR27's initial BLOCKED review is preserved, SHA-256
`67b6843a1294d80ef1f76e59b58a48b0979c8ef78bc8dc035c7494c481d9dd3d`.
Its separate correction PASS report has SHA-256
`ef165e96ded09a76b7a91fb66c84e84659f1b93920d80443d4a299b668bc00a2`.
The correction established control writer exclusion through commit, including WAL,
with 151 focused tests and independent probes. CI439 and Live190 attempt 1 qualify
that corrected tree; earlier CI438/Live189 and the initial 249-test union do not.
Do not repeat PR26/PR27 submission gates or call technical acceptance human APPROVE.

## Problem and bounded deliverable

C2 binds every action to one complete immutable worker row. Product workers release
ownership at a stop. D2a provides atomic metadata/worker transitions, but its fixed
semantic witness changes as soon as real Program execution changes. Its descriptors,
caller-supplied hashes and successful claim cannot establish Safe quiescence or
grant execution. A production consumer therefore needs its own versioned authority.

Define and subsequently implement an explicit trusted-host v3 admission/adapter
which consumes actual c1 preparation under the same worker; runs actual discovery
and Safe to the scope interrupt; proves the whole invocation has returned; parks
the exact proposal and releases that worker atomically; then accepts one explicit
scope decision under a freshly reserved worker in a new process. The latter runs
the existing Safe apply/test/review/finalize path once and records its actual result.
A successful terminal result remains unaccepted source. No second phase starts itself.

The first resumable boundary is only the actual `awaiting_scope_approval` stop.
Completed discovery inside a still-running outer call, control pause, publish
approval, unfinished preparation and ambiguous remote work are not additional
handoff points. Host configuration must disable source-control publication and its
post-test approval journey for this slice. Existing v1/v2 capabilities remain intact.

## Allowed implementation scope

All source paths below are under `src/universal_coding_agent/`.

| Area | Allowed change and limit |
| --- | --- |
| `product/program_continuation_dispatch.py` | New `ProgramContinuationDispatchService`: explicit admission, action requests, versioned current authority, actual result recording and atomic park/close |
| `product/program_continuation_execution_adapter.py` | New exact `ContinuationSafeExecution` adapter: one-use live capabilities, source/files/control gates and settlement; no subclass/duck-type adoption of c2 |
| `product/program_continuation_execution_store.py` | New bounded v3 schemas, immutable records, requests, standalone read-only readers and transaction composition; may contain the quiescence proof helper |
| `product/program_source_routing.py` | Small version/marker resolver and deny-only legacy guards; no provider/service construction on read |
| `safe_service.py`, `discovered_safe_service.py` | Exact version-specific adapter selection, durable checkpoint-root task guard and all effectful entrypoint denials; retain existing graph behavior |
| `core/cancellation.py` | Narrow task-scoped registration barrier/snapshot for v3 settlement, covering owned operations/processes/handles; preserve cancellation, pause and resume behavior |
| `product/program_source_dispatch.py` | Only cross-version collision/route rejection before mutation; do not relax c2 authority, checkpoint, lineage or replay checks |
| `product/program_source_acceptance.py` | Only early v3 rejection in old acceptance/capture paths, including replay; no v3 source candidate/approval/acceptance implementation |
| `product/program_continuation_handoff.py` | Only prevent inert foundation operations from acquiring/releasing ownership of a v3-bound Program; retain d2a schema, public false flags, receipts and transaction behavior |
| `product/program_source_status.py`, `product/program_orchestrator.py` | Narrow fail-closed v3 legacy-route exclusion, including missing/partial metadata; no public v3 Product projection or v1 evidence changes |
| Focused new tests and relevant existing suites | Real consumer, routing, quiescence, crash, bounds and compatibility evidence described below |
| This task, its consumer contract, parent, matrix and ROADMAP | Bounded engineering continuity |

Reuse the accepted connection-scoped lifecycle primitives unchanged. C1 and
materialization verifiers, c2 execution adapter, Safe graph algorithms and source
evidence/transition semantics stay unchanged. Do not extract shared c2 authority
helpers in this slice: use the existing pure filesystem/Git/evidence primitives,
and implement the separate v3 proof with explicit parity tests. If implementation
requires a broader path or a weakened invariant, revise the concrete scope first.

No web/API/UI/CLI/ProductWorkspace wiring, workflow change, new dependency,
scheduler, v2 migration, automatic proposal refresh after control drift, remote
lease recovery, source-generation advance, candidate-2/approval-2, deployment,
credentials, main, PR6, root todos.md, AskTD/ETL/customer work, history rewriting
or generated-source publication. D2b-2, d2c-1 and d2c-2 remain planned and uninstantiated.

## Implementation order and decisive evidence

1. Add bounded v3 records, collision guards and read-only routing. Prove old
   entrypoints cannot fall through to v1 when any required v3 marker is missing.
2. Add explicit admission on the existing c1 connection, unchanged pending-state
   verification and immutable consumption. Pin trusted host/store/source/policy
   identities and keep each database's actual write role explicit.
3. Add the separate adapter and live invocation lifecycle. Preserve c2-strength
   discovery, execution-base, inventory, inode, control and rollback checks.
4. Add actual outer-call settlement, checkpoint/remote writer exclusion and the
   registration barrier before any worker release. Prove the scope checkpoint
   alone cannot produce a parked record while an invocation is still alive.
5. Add fresh-worker exact-proposal scope decisions and terminal recording, using
   actual graph/subprocess tests and review. Add durable replay without rearming.
6. Run the bounded fault/routing matrix and compatibility tests, then submit the
   first implementation candidate through the normal gates below.

The mandatory host journey uses actual temporary Git and on-disk stores. Start
with original source 42; run/test/review a real v1 first phase to 43 and accept it
using existing exact v1 acceptance in its own valid owner episode. Under one new
worker, materialize accepted 43, prepare c1 and admit v3. Discovery must read 43.
At the real Safe scope stop, prove settlement and atomically park/release. Terminate
that host process and reopen the same stores; read-only inspection does no work.
An explicit exact scope approval reserves a different worker/token and epoch,
revalidates the unchanged proposal, and reaches actual tested/reviewed 44 without
repeating discovery. Record terminal-unaccepted 44 and atomically release the new
worker. Source generation remains 1 at accepted 43; no candidate/acceptance for 44
is created. D2b-2 owns accepting 44 and the complete accepted cumulative lineage.

Use actual Safe graph, artifact/checkpoint stores, isolated derived Git, trusted
subprocess tests and deterministic provider responses. A mocked dispatch result,
inserted checkpoint or metadata-only 42/43/44 fixture is insufficient. Include
SHA-1 and SHA-256 derived-Git qualification and original/retained source byte
preservation, including binary, executable, CRLF, empty and no-final-newline files.
This host fixture is not live-model cumulative v3 or a Product HTTP/UI journey.

| ID | Required evidence before implementation acceptance |
| --- | --- |
| V01 | Complete real 42/43/44 terminal-unaccepted journey across a clean process restart and two actual worker identities; zero repeated discovery and one consumed scope decision |
| V02 | Live outer invocation or any owned operation/process/cancellable/pausable/paused handle blocks seal even with an apparently valid checkpoint; new registrations and late callbacks cannot race release |
| V03 | Exact checkpoint/task/thread/namespace/interrupt and pending-write validation; wrong scope, hidden work, error/resume writes, terminal pending tasks and unsupported boundaries reject |
| V04 | Separate real processes race pause/cancel/control updates, fresh claims and worker recovery at all commits; no stale release or action grant, no double provider invocation; include WAL read-only Safe/remote attachments |
| V05 | Crash before/after durable task guard, admission, ticket arm/claim, discovery, apply, test, review, finalize, invocation settlement, park, new claim and terminal commit; inspect every involved store and exact filesystem bytes |
| V06 | Completed lost-response replay returns exact immutable public outcome and no token/ticket; conflicts and pending/unknown requests block; crashes before settlement never infer quiescence from an empty fresh-process coordinator |
| V07 | Full current source/head/control/plan/host/policy and immutable c1 material/preparation/Git/inode proof; stale approval, recovery, source drift, wrong worker and changed-then-restored control revision reject |
| V08 | Raw Safe run/resume/publish/control-resume, discovery, Program continue/start, old acceptance and d2a ownership paths cannot bypass v3; cross-version duplicates, mismatched adapters and missing registries/guards reject |
| V09 | Rejected scope, failed tests/review, known partial apply rollback, ambiguous partial apply and source-preservation negatives; no false success or accepted-source change |
| V10 | Standalone existing-file read-only status/request lookup: no effectful imports, constructors, setup, proposals, reconciliation, ownership or provider calls; strict schema/type/field/SQL/blob/page bounds |
| V11 | Journal/sync/path/inode/authorizer failures and trigger attacks before writes; atomic Program/control/lifecycle changes, logically read-only Safe/remote protection through commit, no hidden PRAGMA repair |
| V12 | Existing c1/c2, Program v1 evidence, PR26 F1/F2, d2a corrected WAL control and lifecycle/recovery/pagination regressions; frozen old schemas and adapter behavior |

## Definition delivery and later submission gates

The candidate implements the four new modules and narrow legacy entry guards in
the scope table. `tests/test_program_continuation_dispatch.py` and
`tests/test_program_continuation_boundaries.py` contain the real consumer evidence,
including process exits, competing processes, live registration barriers, faulted
checkpoints, immutable history bounds, source preservation and copied-proof parity.
Their deterministic provider fixture uses real Git, discovery, Safe checkpoints,
subprocess tests and reviewer outcomes. These tests do not qualify a live-model v3
or Product HTTP/UI journey. Final exact candidate identities, commands/counts and
independent/platform outcomes belong to the submission evidence; an author run
alone cannot complete this task's acceptance gates.

For this definition: check every referenced path, review the complete documentation
diff, verify runtime/tests/workflows are identical to accepted PR27, publish only
the definition branch and verify its actual Git commit/tree/sole parent. Record
that identity in current references. Do not create a documentation-only PR: the
existing UCA PR trigger would start standard paid Live. No runtime test result is
claimed for prose validation, and no new CI/Live/Web run is required or claimed.

For subsequent implementation: open the first candidate as Draft against the
accepted feature target, preserve all initial failures and exact source identities,
and obtain a separate independent technical review on the actual submitted tree.
The review must independently rerun the real journey plus concurrency, crash,
read-only, route and authorizer probes; author-written tests alone are insufficient.
Corrections require their own acceptance and current-tree platform evidence.
Run applicable focused tests, Ruff and diff checks; use normal CI/Live triggers
and record literal job checkout heads/trees, attempts, results and limits. Do not
manually repeat paid runs or call standard Live Program (v1) a v3 journey.
Only then use normal Ready and expected-head-locked merge; verify the actual
target ref/tree/ordered parents after integration. PR27 acceptance is the baseline,
not approval or qualification of this new consumer. Later slices keep their own gates.
