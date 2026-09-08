# P3.5d-2c-1 — Typed local Product commands

Task ID: `UCA-20260908-P35D2C1-LOCAL-PRODUCT-COMMANDS`.
Status: **defined for bounded implementation; implementation not started**.
Canonical [API and host-binding contract](P3_5D2C1_API_AND_HOST_BINDING_CONTRACT.md).
Delivery milestone: [UCA-M-LOCAL-PILOT-1](P3_5D2_LOCAL_PRODUCT_PILOT_DELIVERY_MILESTONE_2026-09-08.md),
approved/planned, not delivered. All implementation acceptance families below are pending.

## Starting identities and preserved work

Repository: `hesam-hakimi/hugan`. Accepted target
`feature/universal-coding-agent-structured-edits` is actual PR29
`f27c2693babcdf20145676328012b2d7576c5aa3`, tree
`29b763ff5af8a50348f7e987b341db65fac33bfa`, merged 2026-09-08T18:46:55Z.
Ordered parents are `95096565d85640ea471182fc0b421e124667b73b`, then
`b0e1a9dd590ba33a65d42868553bcada15c432ee`. Preview
`9f816b01cae2d60e8241b32c4a7b43d61d6afabe` is distinct.

Definition branch: `feature/universal-coding-agent-local-product-commands`.
Its documentation parent is milestone commit
`a04dd89ae3dd9f9db50755f8a4e7dda0248c952f`, tree
`5bd990cd0f2ff9f097f0f39a5dea2c7afb5f0b50`, sole parent PR29. Preserve all four
milestone document changes. Exact published definition commit/tree belong to the
external publication checkpoint; this file cannot identify its own future commit.
Verify that identity and all document blobs before implementation; do not select
a moving branch or local author bookmark without readback.

The parallel `feature/universal-coding-agent-continuation-api` definition at
`8799f39cbc97af179cebf5310521222879e9c5d1` is preserved, not overwritten or rewound.
It omitted first-phase HTTP actions and its shared synchronization was blocked.
Its old task/contract are carried here with exact historical suffixes and explicit
supersession links. This current task resolves that earlier API entry restriction
under the now-authorized local milestone. It does not instantiate d2c-2, a pilot,
or a live qualification task. Neither documentation branch is accepted runtime.

PR29 initial F1/F2 BLOCKED and correction PASS stay separate; CI446/Live197 apply
to the correction, CI445/Live196 only the initial tree. PR28's two BLOCKED reports
and final PASS, both PR27 and both PR26 reports remain retained. Standard Live
Program remains v1. Do not repeat accepted PR26–PR29 gates for credit. Author,
independent and platform counts overlap and must not be added as unique coverage.

## Outcome and entry conditions

Implement explicit finite local HTTP commands from host-bound source initialization
through first-phase scope stop/decision, exact first source review/acceptance,
accepted-source continuation/discovery, restart at a settled scope stop, explicit
scope decision, final source preview and separate final acceptance. The scope is
an actually approved unsliced linear two-phase Program, one unit at a time,
synchronous supported transport, trusted test policy and publication disabled.
42 (original), 43 (first accepted) and 44 (continued/last accepted) are fixture
values only; actual source hashes, generations and evidence control eligibility.

The first-phase ownership solution is a new explicit review quote and finite
driver, not direct HTTP exposure of `ProgramSourceTransitionHost._first`.
Preview preserves its complete candidate-1; decision independently prepares a
new candidate under a fresh current owner, compares every immutable semantic
core field, and accepts that new candidate under that same owner. V1's existing
owner-change denial remains an explicit regression. No old worker is restored.
V1 source finalization and the Product outcome/exact release are atomic through
a narrow typed transaction seam. The companion specifies the proof and DAG.

Complete transport durability is part of this task. A best-effort response cache,
in-memory run map, fabricated Program/Safe result, or preaccepted host setup as a
substitute for first-phase HTTP coverage cannot satisfy it. Pending/ambiguous work
blocks new effects; only original-live v3 seal reconciliation is supported.

## Actual consumer map and required composition

All paths below are relative to `universal-coding-agent/` at accepted PR29.
Rows identify inspected consumers and exact implementation obligations. They do
not claim those new adapters already exist.

| Surface | Actual producer/consumer | Required composition / constraint |
| --- | --- | --- |
| Host startup | `src/universal_coding_agent/cli.py::_run_server`, `product/workspace.py::ProductWorkspace.create/discovered_safe`, `web/app.py::ProductWebRuntime` | Add the two explicit CLI flags and strict host binding; reuse existing provider/control/remote stores and one Safe root; default disabled. Do not use `close(wait=False)` as proof that new work settled |
| Source initialize | `product/program_source_acceptance.py::ProgramSourceAcceptanceService.initialize`, `program_source_attestation.py`, `program_source_transitions.py::ProgramSourceIdentity` | Host derives origin identity; actual attestation and exact worker; initialization receipt, HTTP completion and release join final transaction |
| First start/scope | `ProductWorkspace.discovered_safe`, `program_orchestrator.py::start_next_execution/continue_execution`, `discovered_safe_service.py::start/resume`, actual Safe graph | New finite `LocalFirstPhaseDriver` owns live return/settlement and exact scope proposal; no repository/policy from HTTP; no retained `_first` worker |
| First preview/acceptance | `program_source_acceptance.py::prepare/accept/_binding/_capture/_checkpoint`, `program_source_evidence.py::capture_safe_source_evidence` | Exact quote/core, fresh candidate same-owner prepare/accept, complete producer evidence and current checks; narrow final transaction participant only |
| Current host companion | `product/program_source_transition_host.py::start_first_phase/decide_first_phase_scope/preview_first_phase_source/accept_first_phase_source` | Its private `_first` map spans human actions and is intentionally not the new HTTP authority; existing host semantics remain unchanged |
| Next phase | `program_source_materialization.py::begin/reconcile`, `program_execution_base.py::begin/reconcile/_finish_locked`, `program_continuation_dispatch.py::admit/dispatch` | One current owner through c1 pending preparation and v3 consumption; persist actual lower-generated IDs, no prepared-base park or crash adoption |
| Continued scope/reconcile | `program_continuation_dispatch.py::approve_scope/reconcile/_seal/_complete`, `program_continuation_execution_adapter.py::_drive/_returned_proof` | Exact v3 adapter/epoch/receipt/proposal, new owner only for scope decision; reconcile only original live returned adapter; journal joins existing seal/release |
| Final source | `program_source_acceptance_v2.py::preview_source_transition/decide_source_transition`, `program_source_acceptance_v2_store.py::AcceptanceStore` | Exact candidate-2/core, complete PR29 ancestry, distinct fresh capture workers, atomic receipt-2 and wrapper completion |
| Lifetimes and stop controls | `lifecycle_reservations.py` public and connection-scoped worker methods, `task_control.py`, `core/cancellation.py`, `product/remote_operations.py` | Full-row exact ownership, bounded registry barrier, no retained leases/retirements, no fresh-process inference; control/recovery drift invalidates proposal |
| Version denials | `program_source_routing.py::safe_v3_route/task_has_source_marker`, `program_source_status.py::require_legacy_program_route`, `safe_service.py` and discovery entry gates | Preserve c2 exact type/four-column registry; PR28 surviving-affinity/root/guard denials; add managed-command denial without marking metadata as authority |
| Recorded status | `program_source_status.py::program_source_status`, `program_continuation_execution_store.py::Reader/status/request_result`, `program_source_acceptance_v2_status.py::source_transition_status/completed_request/completed_preview`, `program_source_terminal_proof.py::terminal_history` | Explicit generation-0 reader plus selected mixed v1/v3/v2 readers with one shared budget; no exception fallback or effectful constructor |
| Existing browser boundary | `web/src/api.ts::request/startProgramExecution/continueProgramExecution/programExecutions`, `web/src/types.ts`, `web/src/App.tsx` | Existing start accepts browser repository/ref/policy and legacy status is not complete v3 Product status. New generic typed API is supplied now; actual UI consumer changes are d2c-2 |

Follow these imports/call sites in full current source before editing. Read all
canonical parent/milestone, c1/c2, d2a, d2b-1 and d2b-2 task/contracts, applicable
AGENTS instructions and retained reports. No filenames alone establish a consumer.

## Bounded implementation files and authority

Primary new modules: `src/universal_coding_agent/product/local_product_binding.py`,
`local_product_commands.py`, `local_product_command_store.py`,
`local_product_status.py`, `local_product_first_phase.py`,
`local_product_first_source.py`, and `src/universal_coding_agent/web/local_product_api.py`.
These names are the planned module boundary, not existing implementation evidence.

Narrow wiring/transaction/denial changes may touch `cli.py`, `web/app.py`,
`product/workspace.py`, `product/program_orchestrator.py`,
`product/program_source_acceptance.py`, `product/program_continuation_dispatch.py`,
`product/program_continuation_execution_store.py`,
`product/program_source_acceptance_v2.py`, `product/program_source_acceptance_v2_store.py`,
`product/program_source_acceptance_v2_status.py`, `product/program_source_status.py`,
`product/program_source_routing.py`, `safe_service.py`, `discovered_safe_service.py`,
`product/task_control.py` and `core/cancellation.py` only where required for exact
typed command ownership, completion, bounded composed reads and denial/settlement.
Preserve legacy nonparticipant behavior and accepted comparisons/schemas. Do not
change c1/c2 proof or adapter code, d2a authority, Safe edit algorithms, source
policy limits or general recovery. Any extra file or broader semantic change
needs a recorded bounded task amendment before that edit, not an invented bypass.

Focused tests: `tests/test_local_product_api.py`, `test_local_product_binding.py`,
`test_local_product_first_phase.py`, `test_local_product_first_source.py`,
`test_local_product_command_durability.py`, `test_local_product_status.py`;
minimal regressions in touched existing consumer tests. Canonical task/contract,
author evidence, ROADMAP and parent/milestone/matrix may be updated with actual
candidate evidence. No workflow or UI file changes in this slice; CLI changes
are limited to the two local binding flags and startup validation above.

This document defines later runtime scope. The current definition phase edits
documents only and runs no execution test, model, CI/Live/Web, UI or pilot.

## Endpoint-to-consumer acceptance matrix

Every family is **pending implementation**. Use actual HTTP requests through the
new router, real Program/Safe/Git and stores, deterministic recording providers,
actual subprocess test profiles and reviewer provenance. Transport mocks can
supplement malformed-body checks but cannot establish the accepted journey.

| ID / endpoints | Required evidence and existing source anchors |
| --- | --- |
| H01 / all nine effect commands | Real HTTP initialization 42, first scope stop/explicit decision to tested/reviewed 43, first preview, process restart, separate receipt-1 acceptance, next-phase c1/v3 discovery, actual scope stop, Product process restart, exact scope decision to 44, final preview, restart and separate receipt-2 acceptance. Assert original and immutable accepted 43 bytes/modes unchanged. Extend construction patterns in `test_program_source_acceptance.py`, `test_program_continuation_dispatch.py::test_v01_real_process_exit_after_scope_and_restart_once`, `test_program_source_acceptance_v2.py::test_a01_a02_real_os_restart_at_every_handoff`; the HTTP path itself must do first acceptance |
| H02 / startup and all routes | No flag/file, wrong project/Program, wrong root/inode/Safe host, wrong provider/test policy, unsupported remote transport, remote host even with allow-remote-ui, bad peer/Host/Origin/header/content type, duplicate fields/coercions/oversized stream deny before effects. Reopen identical host config successfully. CLI exact arguments tested without provider calls. Existing `test_web_api.py::test_ui_binding_is_loopback_by_default` is legacy evidence only |
| H03 / first start/scope | Real scope stop, all owned registration sets/late callback barriers, actual return required, strict scope checkpoint/interrupt/writes; fresh worker decision after clean stop/restart. Wrong task, stale control, hidden writes, retained lease or process-dead live context cannot resume. Existing web `RecordingProgramExecutor` tests are supplementary only; use actual graph evidence as in PR28 V02/V03 |
| H04 / first preview/decision | Different preview and decision owner digests; intact original candidate; its direct acceptance under a new owner still fails `test_real_control_revision_and_owner_changes_reject_prepared_approval`. New prepare+accept under one current owner succeeds only when every core field agrees. Change each semantic/evidence/inventory/control/recovery/host field, delete preview request/response/quote/core/first artifacts, reject exact quote, attempt accept after rejection and race two decisions; no unauthorized source advance |
| H05 / continuation start | One owner across actual lower-generated materialization/Base IDs, complete c1 pending verifier, v3 admission/guard/dispatch; no prepared-base pause. Crash around each allocation/ID-record boundary remains pending with source preserved. Frozen materialization/Base/c2 tests retain their original semantics |
| H06 / continued scope + final preview/decision | Real v3 parked proposal/epoch/source checks and separate PR29 fresh workers. Rejected scope, failed tests, FAIL/conditional review, actual rollback, pending writes/handles and retained leases do not accept. Terminal/preview/source acceptance remain distinct; receipt-2 cannot materialize or start phase 3 |
| H07 / every POST + request GET | Same ID/same body race across two OS processes causes at most one actual provider/apply/test/review action; changed content/action/project binding rejects. Response loss/restart and later source drift return byte-identical completed historical response. New ID cannot bypass pending head or administrative worker removal. Missing lower/upper links deny rather than fabricate completion |
| H08 / claim/seal/source commits | External process termination before/after claim, first scope/terminal seal, first preview, v1 final acceptance, c1/admit, v3 scope/final seal, final preview and receipt-2 commit. Inspect real SQLite logical state and original/accepted/execution bytes separately. Source CAS/receipts/response/release atomic where required; first execution gap explicitly remains pending and owned. No recovery from a merely terminal checkpoint |
| H09 / reconcile endpoint | Actual reversible v3 seal failure in same process; explicit reconcile succeeds with original returned adapter and zero repeated provider calls. New process, missing/changed original adapter, wrong target/payload/child, c1/first/source target, drift and retained lease give typed blocked result. Duplicate reconciliation never reexecutes; original target stays blocked on denial. Anchor `test_v06_pending_duplicate_and_reversible_seal_failure_do_not_repeat_work` |
| H10 / effects with concurrent controls | Real independent public pause/cancel/recovery/fresh-worker processes and Safe/remote WAL writers at final boundaries; exact source/policy/plan/control revision drift (including pause-resume round trip), bounded locks and current proof through commit. Retain PR27 WAL exclusion, PR28 registration/revocation and protected PRAGMA denial. Unsupported writer modes reject without repair |
| H11 / status, replay, evidence | Fresh standalone existing-file read-only reader with effectful imports/factories, checkpoint decode, Git and provider entry made fatal. No file/database/WAL byte changes or missing-store creation. Complete mixed lineage and PR29 F1/F2 deletion scenarios through HTTP both before and after accepted/rejected decision. Unknown/missing registries/locator/checkpoint versions never fall back to old status |
| H12 / reads and body parser | One aggregate 64-KiB/1-MiB metadata and 24,000,000/256,000,000 opaque budgets, selected-row SQL bounds, adversarial WAL growth between header/fetch, history/keyset/depth/type bounds, no implicit proof truncation or resets per child. Public review-view exact digest, redaction/incomplete denial, tokens/credentials/paths/raw exceptions absent. No current-authority flag becomes true |
| H13 / old and raw entrypoints | Preserve actual v1/c2/d2a behavior for unmarked records. Managed pending/settled tasks reject arbitrary old browser config, raw Safe/discovery copies, wrong/subclass/reconstructed contexts and command-namespace loss with surviving affinity. C2 four-column exact-owner registry and accepted PR28 root/guard/unknown-version cases remain intact |
| H14 / definition-to-delivery map | LP01 host startup/reopen, LP02 complete commands, d2c-1 share of LP05 receive exact candidate evidence only. LP03 stays d2c-2; LP04/LP06 and complete pilot readiness remain false. No host-only setup or old Live v1 result is relabeled full Product qualification |
| H15 / integration gates | Complete author diff/consumer/acceptance review, focused author checks and meaningful touched-seam compatibility; separate independent bounded implementation review; actual current-tree CI/Live and Web when applicable, child outcomes and literal checkout/tree inspection; normal Ready and expected-head-locked integration. Preserve every failed tree/report, correction and exact readback |

Examples of concrete compatibility anchors additionally include
`test_program_source_acceptance_v2_lineage.py`, `test_program_source_acceptance_v2_boundaries.py`,
`test_program_continuation_boundaries.py`, `test_program_source_dispatch.py`,
`test_program_execution_base.py`, `test_program_source_materialization.py`,
`test_program_continuation_handoff.py`, `test_lifecycle_reservations.py`,
`test_product_workspace_control.py`, `test_remote_operation_reconciliation.py`,
`test_strong_cancellation.py`, `test_program_source_status.py` and `test_web_api.py`.
Choose execution scope from actual changed seams; do not blindly rerun every
accepted suite or call old successful counts fresh qualification.

## Handoff and limits

Routine bounded choices above are resolved. The definition does not depend on a
missing credential, customer environment or new Milestone 4/5 service. The new
first-phase driver/quote/atomic seam remains the highest implementation risk;
H03/H04/H08 must establish it before LP02 can pass. This is an explicit additive
implementation obligation, not an already proven authority bridge. If its required
invariants cannot be maintained within the allowed seams, record the exact gap and
amend the task before broader work; never silently drop first-phase coverage.

Next bounded action after exact publication and continuity reconciliation:
implement only this task from the verified definition commit, establish focused
author evidence, then submit an implementation candidate through the normal Draft
PR and separately scoped review/platform gates. Paid qualification requires its
normal authorized candidate gate; this definition launches no paid run or PR.
Independent implementation review uses a separate reviewer at that later stage;
the current author definition review is not independent acceptance.

LP03/UI, full Product real-model journey and local handoff are later work. RP01
read-only onboarding then RP02 one exact separately approved change stay planned
and uninstantiated. Private handoff alone maps the chosen real project; public
Product code/configuration stays generic. No complete autonomous roadmap delivery,
production service, third-phase execution or real-project validation is claimed.

Keep main, PR6, root `todos.md`, ETL/customer source, credentials, migrations,
post-drift refresh, scheduler, arbitrary shell, deployment, history rewriting and
generated-source publication out of scope. Speak Persian with the owner; code,
comments, tests, commits, engineering prompts and documents remain English.
