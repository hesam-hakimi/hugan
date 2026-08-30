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
- [x] byte-bounded Program disposition and phase-report reads for retained-lease inventory eligibility, with a typed oversized-evidence blocker and unchanged retirement authority;
- [x] byte-bounded Program disposition and phase-report revalidation for explicit private-lease retirement, failing closed before mutation with unchanged authority and outcomes;
- [x] durable fail-closed lifecycle reservations shared across Product runtimes for remote-operation actions and Program controls, with restart persistence, ownership-checked release, and zero provider work;
- [x] durable fail-closed ownership for Product Control Center standalone and Program execution workers, transactionally serialized with lifecycle actions across runtime processes;
- [x] explicit audited administrative recovery for crash-left lifecycle reservations and worker ownership, with exact-row confirmation, immutable redacted receipts, and no TTL or automatic cleanup;
- [x] independently bounded keyset pagination for lifecycle recovery candidates and receipts, with opaque cursors, fail-closed persisted-field limits, GET-only React continuation, and unchanged recovery authority;
- [x] index-backed immutable-receipt keyset pagination with additive legacy-database initialization, exact fail-closed index attestation, and unchanged API, UI, recovery authority, provider behavior, and outcomes;
- [x] index-backed lifecycle-recovery candidate pagination with additive reservation and worker indexes, exact fail-closed index attestation, shared bounded reads, and unchanged API, UI, recovery authority, provider behavior, and outcomes;
- [x] index-backed global lifecycle-recovery field validation with additive partial violation indexes, exact fail-closed definition and query-plan attestation, preserved whole-table corruption detection, and unchanged API, UI, recovery authority, provider behavior, and outcomes;
- [x] P2.2a provider-neutral fail-closed pausable-operation contract foundation with exact owned-handle registration, bounded pause/resume acknowledgement, durable redacted evidence, safe-boundary fallback, cancellation precedence, and no production transport claim;
- [x] P2.2b opt-in Host Chat pausable-handle adapter with fail-closed configuration, deterministic and HTTP coverage, cancellation precedence, durable redacted evidence, source preservation, and dedicated `llama-cpp-python` live host qualification;
- [x] P2.2c opt-in trusted-test cooperative pausable-handle adapter with fail-closed configuration, deterministic, Safe graph, HTTP, cancellation, durable-evidence, and source-preservation coverage, plus dedicated adapter-level live host qualification;
- [x] P2.2d opt-in HostSubprocess cooperative pausable-handle adapter with a strict bounded child-control bridge, underlying-handle acknowledgements, cancellation precedence, redacted evidence, unchanged legacy behavior, and dedicated Azure live qualification;
- [x] P2.2 current-transport inventory closure: every currently eligible provider/test transport has an opt-in pausable adapter; OpenAI Responses has no remote pause primitive and no additional production transport is presently eligible;
- [x] P2.3a opt-in exact-patch publish approval with post-test/review interrupt, Base/plan/scope/patch binding, restart durability, explicit rejection, fail-closed mismatch rollback, and zero source-control side effects;
- [x] P2.3b explicit post-approval source-control transaction with integrity-verified approval, patch, test, and review evidence; stable adapter/Draft-PR identity binding; immutable completed replay; retryable exact reconciliation with per-attempt evidence; temporary-index crash safety; isolated Git history/config verification; exact local commit; lease-guarded feature-ref creation/exact replay; an optional trusted Draft-PR creator contract; and deterministic local bare-remote qualification;
- [x] P2.3c-a default-disabled GitHub hosted Draft-PR adapter with repository/account pinning, host-owned API credentials, exact Base/Head SHA revalidation, same-repository Draft-only creation, exact idempotent replay and create-race reconciliation, bounded redacted API failures, redirect rejection, and deterministic contract coverage;
- [x] P2.3c-b dedicated live GitHub feature-ref push and Draft-PR qualification in an isolated approved branch, including provider-level exact replay, service-restart replay, durable receipts, source preservation, credential-redaction evidence, and proof that only the approved feature ref was added; qualified on Azure on 2026-08-30 with Draft PR #6 retained as durable evidence.

## Milestone 3 — Project memory and large-program execution

- [x] P3.1 accepted project knowledge packs: immutable versioned manifests, explicit human acceptance, document/content-hash and scope binding, provenance-preserving retrieval, deterministic indexing, and fail-closed replacement or drift handling;
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
