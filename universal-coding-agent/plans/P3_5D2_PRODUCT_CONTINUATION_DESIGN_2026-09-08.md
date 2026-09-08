# P3.5d-2 — Product continuation across explicit worker episodes

Status: design selected under the owner's bounded engineering mandate; only the
accompanying d2a foundation now has an implementation candidate. Independent and
platform acceptance remain pending. The later execution/API/UI slices are planned.

## Accepted baseline and outcome

Start from actual PR26 integration `132f1410661e9c3a9034c9d6cd9400eebeda65f9`,
tree `884a94d8722e614d72b48892e77aa59ca015d622`. Ordered parents are accepted
PR25 `5d1bb45c28689131b9b538e798d3b8e7aa25742c`, then reviewed corrected
PR26 `ffc1616be54f9c735a7ba3c35f6dc8e5fd197a55`. Both independent PR26 reports,
including the original BLOCKED findings, remain canonical evidence. PR26 does not
implement a public effectful source-aware execution action.

The product outcome is an explicit local-user journey: approve a Program; run and
approve its original-Base first phase to tested/reviewed 43; separately accept that
source; start the next phase on accepted 43; restart the Product process at an
actual scope stop; explicitly approve the new scope; reach tested/reviewed 44;
separately accept 44. API/UI must show original Git, accepted source and execution
Git distinctly. Each effect requires its own current authority. Refresh is a read.

The existing host execution schema `uca-program-source-dispatch-2` pins the full
worker row throughout an operation. Web requests intentionally reserve and release
workers. The next request receives a different row/token. This mismatch also affects
materialization/Base preparation and source candidates, so a button wired directly
to c2 is not a complete solution. A durable worker row is exclusive execution
ownership, not a long-lived user approval.

## Read-only implementation evidence

All paths below are relative to `universal-coding-agent/` at the accepted baseline.
The preimplementation inspection changed no runtime, test or workflow file.

| Current consumer / producer | Observed behavior | Design consequence |
| --- | --- | --- |
| `product/lifecycle_reservations.py::reserve_program_worker`, `_release_worker` | Random private owner row; exact-owner deletion; restart persistence; no TTL | Use a fresh owner for each finite action and preserve the shared exclusion boundary |
| `web/app.py::start_next_program_execution`, `continue_program_execution` and workers | Reserve per explicit request, recheck route, release after a stop/result | Do not store a browser token or hold a worker while awaiting a person |
| `product/program_source_acceptance.py::_binding`, `prepare`, `accept` | Owner, control, execution and checkpoint are bound; candidate digest includes that binding | A candidate prepared in one owner episode cannot silently be accepted in another |
| `product/program_execution_base.py` and materialization | Complete pending receipt is verified under the original current owner/control | Preparation and consumption must stay in one episode unless a separately reviewed preparation handoff is added |
| `product/program_source_dispatch.py::_authority`, `_load`, `reconcile` | Full owner/control equality; one-use invocation; exact checkpoint-only reconciliation | Preserve c2 semantics and introduce an explicitly distinct continuation authority protocol |
| `product/program_source_execution_adapter.py` | Process-local ticket, durable digest, claim CAS and current authority before/after nodes | A parked descriptor must never reconstruct an old invocation capability |
| `safe_service.py`, `discovered_safe_service.py`, `product/task_control.py` | Exact adapter type and bound control registry reject alternate/legacy entrypoints | New schema needs explicit registry/adapter routing and cross-version rejection |
| `product/program_source_acceptance.py::_dispatch_for` | One c2 resolver selected by the existing registry | New acceptance resolver needs explicit schema routing; no catch-and-fall-back to v1 |
| `product/program_source_status.py` / Program panel | Bounded metadata-only view; F1/F2 coherence and legacy guards | Recognize new schema deliberately; unknown/incomplete history must stay blocked |
| CI/Live workflow triggers | A UCA documentation PR triggers standard CI and paid Live; this new branch's push does not | Publish the definition branch without a PR; open a Draft PR for the first implementation candidate |

## Selected decisions

1. Separate semantic continuation intent from temporary exclusive worker ownership.
   A parked record is bounded historical intent, containing no live worker, raw
   token or executable capability. An explicit claim reserves a new worker and
   binds one next action to a new monotonically increasing epoch.
2. Reserve execution schema `uca-program-source-dispatch-3` for the eventual
   consumer. It is separate from the Safe edit protocol. V2 records retain exact
   v2 validation and are never automatically upgraded or adopted by v3.
3. Reserve `uca-program-continuation-handoff-1` for the provider-free foundation.
   It does not grant dispatch or source acceptance. Only the later v3 consumer,
   after complete current proof, may issue a process-local invocation ticket.
4. Reserve `uca-source-candidate-2` / `uca-source-approval-2` for product transition
   approval. Split immutable reviewed evidence from the current worker witness.
   A fresh worker must independently recapture/verify the exact evidence core at
   acceptance. Old v1 candidate/approval rules are not relaxed or rewritten.
5. Use exact request IDs, action kind, proposal hash, Program revision/epoch and
   immutable result receipts. An exact completed duplicate returns its stored
   response; an in-progress/ambiguous duplicate cannot invoke a provider again.
   Reusing a request ID with different content rejects. HTTP retry is not recovery.
6. Scope the first product route to the existing trusted local host, approved
   unsliced linear Programs, one active unit and existing trusted policies/profiles.
   A host-owned project binding supplies repository, paths, provider and test policy.
   Browser input does not choose a filesystem destination, transport or policy.
7. Finish one bounded action or park only at a proven quiescent boundary. A process
   crash leaves ownership intact. Existing exact administrative recovery may remove
   a crash-left row, but that receipt alone cannot resume work or restore a ticket.
8. No new scheduler, automatic phase loop, TTL takeover, paid retry loop, multi-user
   RBAC, deployment, customer pilot or generated-source publication in this parent.

Rejected approaches: keeping a worker indefinitely through user approval; copying
its token to the browser or restoring it from a parked record; replacing the old
owner hash in a v2 receipt; ignoring control revisions; treating an empty registry
lookup as v1; replaying a provider after timeout; merging transition approval into
scope approval; automatically approving the next generation after a terminal result.

## Durable authority model

The foundation uses additive, versioned records in the existing Program database.
Names are reserved by d2a and may only be changed with an explicit contract update.

| Record | Required bound content |
| --- | --- |
| `program_continuation_heads` | Program ID; schema/host binding; monotonic epoch; state; current immutable receipt hash; no raw owner token |
| `program_continuation_receipts` | Immutable hash; predecessor hash; action/request digest; phase/task/thread; source generation/source and accepted-receipt hashes; admission/checkpoint/result/approval-core references; control/Program/phase/execution witness digest; current owner-row digest when applicable; outcome |
| `program_continuation_requests` | Unique host/Program/request ID; canonical request digest; action; epoch; status and exact immutable response receipt |

Receipt hashes are integrity bindings, not signatures or capabilities. Authority
comes from the trusted local service, validated host binding, actual current rows,
explicit operator intent and the one-use process-local ticket. Do not serialize
complete private owner/control rows into public responses. Bounds must precede
retrieval, parsing and recursive canonicalization; proposed d2a limits are 100
records per page, 128-byte IDs, 64 KiB per metadata record, 1 MiB aggregate, bounded
SQL work and keyset pagination. Existing source/checkpoint policies remain in force.

| Durable state | Permitted transition | Authority effect |
| --- | --- | --- |
| Absent | Explicit create under the currently reserved worker | Records a new foundation operation; no execution grant |
| `owned` | Seal a proven quiescent handoff, or close a completed action | Atomically records the receipt and releases that exact worker |
| `parked` | Explicit exact-proposal claim with a fresh worker | Atomically advances epoch and records the new owner witness; still no provider permission |
| `owned` after claim | Later consumer validates current source/checkpoint/policy and arms one invocation | Consumer-specific ticket, unavailable in d2a |
| `owned` after interrupted work | Explicit diagnosis/reconciliation only | No new owner, release or repeat inferred from age, missing response or process restart |
| `closed` | Exact recorded duplicate / historical read | No execution and no phase advancement |

`recovery_required` is a projected blocker, not an automatic mutation on GET.
Invalid or missing required metadata always rejects before legacy classification.
No worker row may be adopted because a digest or timestamp looks familiar.

## Transactions and crash boundaries

A handoff commit changes Program receipt/request/head records and the exact lifecycle
worker row in one attached transaction. Claim likewise reserves a fresh worker and
consumes the parked epoch in one transaction. Require on-disk rollback journals and
synchronous FULL or EXTRA for every modified database; reject incompatible settings,
never silently change them. Read-only control/checkpoint attachments do not become
write participants. No provider or long-lived subprocess runs inside a transaction.

The existing lifecycle methods commit their own connection. Calling reserve/release
around a separate Program commit is not atomic. D2a therefore needs a small explicit
connection-scoped primitive retaining the existing exclusion queries and exact-owner
CAS; its caller owns the attached transaction. Existing public lifecycle APIs retain
their transaction behavior and regression coverage. Do not generalize unrelated
lifecycle recovery or pagination while adding this primitive.

A crash before park commit retains the old owner and old epoch. After commit there
is one parked receipt and no owner, even if the HTTP response was lost. A crash before
claim commit leaves the parked record untouched. After claim commit there is a fresh
owner and an owned epoch; a lost response must not cause another claim or work replay.
Existing explicit recovery records the exact row removal only. A later consumer must
reconcile actual checkpoints and obtain a new explicit proposal/approval where allowed.
Ambiguous provider, scope-decision, test, review or apply work remains blocked.

## Quiescent states and consumer proof obligations

D2a records foundation metadata only. D2b must enforce all these obligations before
production use; a supplied boolean, hash or test verifier cannot stand in for proof.

- `awaiting_scope_approval`: actual bound Safe checkpoint is at the precise scope
  interrupt, no decision has been consumed, dispatch and Program rows agree, and
  the current live invocation has settled with no outstanding owned handles.
- Completed discovery without Safe work: exact discovered request/result is durable,
  complete and current, with no outstanding discovery invocation. Do not rerun it.
- Terminal execution: no pending graph nodes/tasks/writes; actual test/review/rollback
  evidence is bound to the result; terminal remains distinct from source acceptance.
- Prepared acceptance preview: immutable evidence core is stable. Later acceptance
  rechecks full current source/control/execution/checkpoint/file evidence under the
  new owner. Old owner-bound candidates do not acquire cross-request validity.
- Incomplete materialization/Base preparation cannot be parked as a complete prepared
  dispatch. Initially perform preparation and consumption within the same episode;
  a crash uses existing explicit preparation diagnostics and may remain blocked.

Pause, cancellation, realignment, disposition, policy drift, source advancement or
an administrative recovery invalidates an old action proposal. Restart alone changes
no rows or authority. A new proposal must be explicitly reconstructed from proven
current state and separately approved where action semantics require it; the old
approval is never relabeled with a new epoch. Cancellation and failed dispositions
never authorize editing or source acceptance.

## Schema routing and compatibility gates for d2b

- Keep the four-column `uca_source_dispatch_tasks` registry and exact c2 comparisons
  unchanged. Add a distinct v3 registry rather than an extra column that would break
  the current full-row equality check. Reject duplicate task/thread registration
  across versions in the same transaction.
- Safe/discovery entrypoints must consult both registries and allow only the exact
  appropriate host adapter. V1, unbound control stores, reconstructed adapters and
  a v2 adapter presented to a v3 task must reject before provider work.
- V3 uses its own admission/authority resolver and process-local tickets. It must
  revalidate immutable materialization, derived Git inventory/inodes, retained source,
  exact control and source CAS with all c2-strength content checks.
- C1 preparation verification stays unchanged before consumption. Its consumed bytes
  remain immutable history; the v3 current authority proof is a separate object.
- V1 acceptance must explicitly reject v3-registered tasks; the new candidate/acceptance
  resolver must never be selected through an exception fallback or duck-typed object.
- Existing v2 admissions, candidates, approvals, receipts and completed replay remain
  unchanged. Migration of a stopped existing v2 task is excluded and needs its own task.
- Unknown version, missing registry/admission/preparation, impossible state pairs and
  incomplete lineage must retain PR26's fail-closed behavior, including F1/F2.

## Delivery and design readiness

Only [d2a](P3_5D2A_PROGRAM_CONTINUATION_HANDOFF_TASK_2026-09-08.md) is ready to enter
bounded qualification. It targets the authority-record/worker transaction boundary,
not actual source-aware execution. D2b and d2c below are planned dependencies and
must receive their own concrete task definitions from the then-accepted source.

| Slice | Deliverable | Required evidence before integration |
| --- | --- | --- |
| d2a | Provider-free handoff records and exact atomic worker transition primitives | Real Program/control/lifecycle databases, crash/CAS/bounds/legacy regressions; independent technical review and applicable normal platform gates |
| d2b-1 | Explicit v3 admission, adapter and quiescent continuation consumer | Actual Git/Safe/discovery across fresh workers and process restart; no duplicate provider/apply invocation; preserved c1/c2 guards |
| d2b-2 | Versioned transition preview/approval/acceptance and host orchestration | Separate exact source acceptance across owner changes; actual 42/43/44 lineage; failed/rejected paths preserved |
| d2c-1 | Typed local Product commands, durable request replay and status | Actual HTTP routing, host-owned project bindings, duplicate/conflict/restart, zero authority on GET |
| d2c-2 | Program controls and evidence review in UI | Actual API-backed first-phase/source-acceptance/next-phase/restart/44 journey; source identities and approval stages distinguished |

The validation and rollout details are in
[P3.5d-2 validation matrix](P3_5D2_VALIDATION_AND_DELIVERY_MATRIX_2026-09-08.md).
No interface/deployment choice or external credential is needed to start d2a.
Open before d2b: precise new consumer schemas, shared verified helper extraction,
and full current-state proposal refresh after lifecycle changes. Open before d2c:
route names, response status codes and host project-binding configuration format.
These are explicitly later slice gates, not implementation-ready claims for them.
