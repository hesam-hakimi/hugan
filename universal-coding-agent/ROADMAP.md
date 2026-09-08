# Current checkpoint — P3.5d-2b-2 defined from accepted PR28

P3.5d-2b-1 is accepted and complete. Only P3.5d-2b-2 is newly instantiated as a
documentation-only task and branch; runtime implementation has not started.
Actual accepted PR28 integration is `95096565d85640ea471182fc0b421e124667b73b`,
tree `26611a055acd80a254cd40c519726e4cad0a85d1`, merged 2026-09-08T15:57:46Z.
Ordered parents: `fdb97d3d10c8a843eae0ab71c255c3ebd0e6ac4a`, then
`1675c2ad1ffa2d324982e4604043bd14e0f27a27`. Preview
`7b86cd520a44c59e8b611f7f29eddb2bf75189d6` is a separate commit with the same tree.
The second correction received separate bounded technical PASS; CI443 and Live194
attempt 1 qualify that exact corrected tree. CI passed 1644 tests per Python leg.
Author 173 v3 + 532 compatibility cases and independent 173 + 291 cases have
different scopes and overlap; do not add them as unique tests. Standard Live
Program remains v1; no cumulative live-model v3 or Product journey is qualified.
Technical PASS is not human GitHub APPROVE or a repository audit.

Canonical new [source-acceptance task](plans/P3_5D2B2_SOURCE_TRANSITION_ACCEPTANCE_TASK_2026-09-08.md) and
[evidence-core/acceptance contract](plans/P3_5D2B2_EVIDENCE_CORE_AND_ACCEPTANCE_CONTRACT.md) select a separate candidate-2
preview and exact decision under fresh workers, ending at accepted generation 2 /
44. First-phase 43 retains existing same-owner acceptance. Receipt-2 does not
enable later materialization or dispatch in this slice. D2c-1/d2c-2 remain planned
and uninstantiated. No new PR, tests, CI/Live/Web or implementation acceptance is
claimed for this definition. Do not repeat PR26/PR27/PR28 gates.

This current block supersedes operative status/next-action wording below; the
exact prior text remains historical, including both PR28 blocked candidates.

---

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
- [x] P3.2 deterministic phase/slice handoff compaction beyond the bounded accepted phase bundle, with an immutable source-bundle hash, adaptive semantic excerpts, exact list/phase digests, bounded verified artifact reads, and fail-closed byte limits;
- [x] P3.3a accepted project decision and ADR records: immutable project-scoped versions, explicit hash-bound human acceptance, deterministic latest-accepted supersession and indexing, bounded verified artifact reads, SQLite restart recovery, and fail-closed provenance, drift, oversize, and scope handling;
- [x] P3.4a incremental repository index foundation: immutable bounded Base-SHA and policy-bound
  snapshots, explicit predecessor compare-and-swap, unchanged-file reuse, deterministic deltas,
  atomic SQLite search/state advancement, restart recovery, and fail-closed integrity handling;
- [x] P3.4b deterministic Python module dependency and test-impact foundation: exact snapshot and
  graph binding, bounded immutable graphs and reports, safe incremental reuse, typed unresolved
  imports, predecessor-aware delete and rename impact, atomic active state, and restart recovery;
- [x] P3.4c-1 deterministic Python symbol and static call-graph foundation: exact snapshot and
  dependency-graph reference/digest binding, canonical function/class/method identities, only
  statically unambiguous in-repository call edges, typed unresolved evidence, bounded immutable
  artifacts, atomic active state, safe reuse, and restart recovery;
- [x] P3.4c-2a conservative Python dynamic-dispatch evidence: exact static-call-graph binding,
  bounded class hierarchy evidence, explicit receiver-type candidates, typed unresolved outcomes,
  immutable artifacts, atomic active state, exact replay, and restart recovery;
- [x] P3.4c-2b1 host-attested trusted coverage evidence foundation: exact Base, Git tree, trusted
  profile, run, repository snapshot, dependency graph, call graph, and dispatch-evidence binding;
  exact whole-snapshot Base-blob verification and whole-tracked-set eligibility; bounded canonical
  per-test line evidence;
  conservative symbol-span projection; immutable run identity, hash-bound input, and
  content-addressed derived artifacts; atomic active state; exact replay; and restart recovery;
- [x] P3.4c-2b2a identity-bound coverage-selection eligibility: additive host-attested
  per-profile execution-environment and coverage-collector/configuration identities; exact
  digest compatibility; bounded historical coverage-chain verification; advisory eligible or
  complete-requested-profile fallback outcomes; and preserved P3.4c-2b1 v1 evidence;
- [x] P3.4c-2b2b conservative coverage-backed test selection: exact direct-predecessor binding;
  reverse Python dependency impact; identity-qualified per-test coverage; fail-closed static-call
  and dynamic-dispatch uncertainty; hash-addressed selected-test or complete-profile-fallback
  artifacts; no execution authorization or minimality claim;
- [x] P3.4c-2c approval-gated coverage-selected test execution: immutable exact-Base plans;
  explicit hash-bound human approval; operator-opted-in positional test IDs or complete requested
  profile fallback; isolated one-shot execution; bounded canonical receipts; exact source
  verification, drift detection, and verified tracked rollback; durable replay and restart safety;
- [x] P3.4c-3a bounded TypeScript/JavaScript static module-reference evidence: repository-index
  policy v3; deterministic literal ESM import, export-from, and TypeScript import-equals evidence;
  `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, and `.cjs` classification; canonical
  kind-prefixed references; explicit lexical, token, count, and specifier bounds; fail-closed
  malformed supported declarations; and unchanged Python dependency and execution behavior;
- [x] P3.4c-3b deterministic TypeScript/JavaScript module resolution, dependency graph, and impact
  analysis: unique bounded repository-relative candidates, typed unresolved and ambiguous evidence,
  exact snapshot and policy binding, safe incremental reuse, predecessor-aware delete and rename
  impact, immutable bounded artifacts, atomic active state, source preservation, and restart replay;
- [x] P3.5a cumulative source-transition foundation: immutable content-bearing source snapshots,
  exact preimages and path scope, separate hash-bound materialization approval, canonical bounded
  serialization, and pure in-memory replay across process restart. See
  [Program source transitions](PROGRAM_SOURCE_TRANSITIONS.md). This is code present in this branch,
  not a claim that Program dispatch transfers patched source or that hosted qualification passed;
- [x] P3.5b-1 complete read-only Git-source attestation: trusted host repository binding,
  exact raw commit/tree/blob verification, full bounded file inventory and canonical snapshot,
  source preservation and fresh-process replay. See
  [Program Git-source attestation](PROGRAM_GIT_SOURCE_ATTESTATION.md). Code presence does not
  establish hosted qualification, durable acceptance or source-aware Program dispatch;
- P3.5b-2 verified Safe/test/review evidence and durable transition acceptance using lifecycle
  ownership, compare-and-swap, exact approval and idempotent replay;
- P3.5b-3 newly owned sandbox materialization and explicit recovery receipts across the
  database/filesystem crash boundary; separately gated source-aware dispatch must preserve
  evidence-only v1 same-Base behavior;
- P3.5c phase DAG per-slice gates, explicit retry/replan, and resumable long-running programs;
- P3.5d-1 [recorded Program source visibility](PROGRAM_SOURCE_VISIBILITY.md): bounded
  read-only origin/accepted lineage/v2 dispatch display and legacy-route guards;
  independently accepted and integrated through PR26 on 2026-09-08;
- P3.5d-2 [Product continuation design](plans/P3_5D2_PRODUCT_CONTINUATION_DESIGN_2026-09-08.md):
  explicit worker episodes, versioned continuation/acceptance and later API/UI delivery;
  d2a inert handoff accepted and integrated through corrected PR27 on 2026-09-08,
  with no execution capability or production caller;
  [d2b-1](plans/P3_5D2B1_V3_CONTINUATION_EXECUTION_TASK_2026-09-08.md) has a second correction candidate after two independent BLOCKED reviews
  from actual accepted PR27 for explicit v3 admission, actual scope quiescence and
  fresh-worker continuation to terminal-unaccepted results; independent/current-tree gates pending;
  d2b-2 source acceptance and d2c-1/API, d2c-2/UI remain planned;
- P3.4c-3c additional-language dependency analysis beyond Python and TypeScript/JavaScript
  (deferred behind source continuity and resumability by the September 7 owner decision);
- context deduplication and model-budget policies.

### Accepted September 7 priority

After PR #19 integration, prioritize source continuity and gated Program resumability before
additional-language expansion. Start with the bounded P3.5a contract, then trusted integration,
then a read-only AskTD onboarding pilot and one separately bounded change. The owner approved
advancing this route autonomously within existing quality gates. This does not waive independent
review, exact evidence/approval binding, source preservation, or environment-specific acceptance.
The pure source-transition service does not itself establish a completed autonomous Program loop.

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
