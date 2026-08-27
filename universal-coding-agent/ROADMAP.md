# Roadmap

## Milestone 1 — LangGraph Observe MVP

- [x] Provider-neutral model contract
- [x] Host provider-factory loading
- [x] Isolated Git mirror/sandbox
- [x] Repository manifest and Python symbol index
- [x] Role-specific bounded context compiler
- [x] Hierarchical phase/slice planner contract
- [x] Optional human plan-approval interrupt
- [x] Fixed read-only Git checks
- [x] Independent reviewer contract
- [x] SQLite LangGraph checkpointing
- [x] Filesystem artifact store and final report
- [ ] Live host-provider qualification
- [ ] Public project license decision

## Milestone 2 — Safe Development

- [x] approved-path scope gate;
- [x] implementer subgraph;
- [x] deterministic structured edit and patch validation;
- [x] isolated patch application;
- [x] fixed test-profile registry;
- [x] bounded structured-output and edit repair;
- [x] independent Safe reviewer;
- [x] deterministic rollback of agent-owned sandbox changes;
- [x] task-scoped cancellation signal and active termination for registered UCA-owned host-provider and trusted-test child processes;
- [x] durable cancellation report and cooperative fallback for providers without an active termination contract;
- [x] opt-in cancellable handle adapter for the trusted in-process host-chat transport;
- [x] typed durable cancellation evidence in the local Product Control Center;
- [x] opt-in cancellable background-response adapter for the pre-transfer OpenAI Responses transport;
- [x] dedicated live qualification of the opt-in OpenAI background cancellation lifecycle and durable report;
- [x] private restart-safe OpenAI response lease with explicit observe/cancel reconciliation and deterministic/live restart qualification;
- [x] typed redacted remote-operation evidence plus explicit observe and confirmed-cancel controls in the local Product Control Center;
- [x] explicit durable orphan disposition after terminal/unavailable remote state, with audited standalone and Program closure and no provider call;
- [x] explicit disposition-bound local retirement of one private opaque remote-operation lease, with an atomic redacted receipt, default retention, zero provider calls, and zero Task/Program outcome changes;
- [x] bounded GET-only inventory and advisory eligibility preview for retained private leases already bound to durable dispositions, with redacted React review and no provider call or mutation;
- [ ] cancellable adapters for any further supported in-process/remote provider transport;
- [ ] active pause of an already-running provider/test operation;
- publish approval;
- commit, push, and optional Draft PR through a source-control adapter.

## Milestone 3 — Project memory and large-program execution

- accepted project knowledge packs;
- [x] typed, provenance-preserving accepted prior-phase evidence for dependent Safe contexts;
- phase/slice handoff compaction beyond the bounded accepted phase bundle;
- project decision and ADR memory;
- incremental repository index;
- dependency/call graph and test-impact analysis;
- phase DAG execution with per-slice gates;
- resumable long-running programs;
- context deduplication and model-budget policies.

## Milestone 4 — Worker backends

- Linux process sandbox hardening;
- container sandbox backend;
- remote Windows worker protocol;
- platform-specific check profiles;
- GitHub Actions and self-hosted runner adapters;
- cross-platform evidence reconciliation.

## Milestone 5 — Service and UI

- multi-project web UI;
- task history, live progress, interrupts, and resume;
- artifact/diff/test/review viewers;
- user/RBAC boundaries;
- quotas and sandbox retention;
- PostgreSQL checkpoint and object-store backends;
- usage/cost evidence;
- operational health, audit, and deployment guidance.
