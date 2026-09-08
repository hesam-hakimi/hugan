# Current checkpoint — P3.5d-2b-2 implementation candidate

The bounded implementation now exists on the source-transition definition
branch, descending from verified definition commit
`62f988ed85c219715a7d74bbfc75f03c54f3d7a0`. It adds immutable candidate-2 evidence
cores, distinct temporary capture witnesses, separate fresh preview/decision
workers, an atomic receipt-2/source-head/request/release transaction, an explicit
one-action host companion, and a standalone recorded mixed-version reader.
The final two-phase result can be explicitly accepted at generation 2 / 44 in
the deterministic real Program/Safe/Git fixture. Original 42 and accepted material
43 remain unchanged. Receipt-2 enables no materialization or third phase.

The canonical task maps A01–A12 to submitted executable evidence and records the
limited shared-read accounting scope decision. Author development runs are not
independent acceptance. Exact candidate-tree author, separate independent,
current-tree CI/Live, normal Ready and expected-head integration gates remain
required; their observations must identify their own source trees. This source
checkpoint claims no completed platform/integration gate or cumulative live-model
v3/Product journey. PR28 remains accepted; its gates are not rerun for credit.
D2a remains inert and d2c-1/d2c-2 remain planned and uninstantiated.

This block supersedes operative status below. Earlier definition and failed
candidate records remain history with their original source identities.

---

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

Canonical new [source-acceptance task](P3_5D2B2_SOURCE_TRANSITION_ACCEPTANCE_TASK_2026-09-08.md) and
[evidence-core/acceptance contract](P3_5D2B2_EVIDENCE_CORE_AND_ACCEPTANCE_CONTRACT.md) select a separate candidate-2
preview and exact decision under fresh workers, ending at accepted generation 2 /
44. First-phase 43 retains existing same-owner acceptance. Receipt-2 does not
enable later materialization or dispatch in this slice. D2c-1/d2c-2 remain planned
and uninstantiated. No new PR, tests, CI/Live/Web or implementation acceptance is
claimed for this definition. Do not repeat PR26/PR27/PR28 gates.

This current block supersedes operative status/next-action wording below; the
exact prior text remains historical, including both PR28 blocked candidates.

---

# P3.5d-2 — Product continuation across explicit worker episodes

Status: d2a is independently accepted, platform-qualified and integrated through
actual PR27 `fdb97d3d10c8a843eae0ab71c255c3ebd0e6ac4a`, tree
`f1e78ac88cdb58c166e4fd51f672c54f9625f210`. Only
[d2b-1](P3_5D2B1_V3_CONTINUATION_EXECUTION_TASK_2026-09-08.md) has a bounded implementation candidate;
its [consumer contract](P3_5D2B1_V3_ADMISSION_AND_QUIESCENCE_CONTRACT.md) is normative
for that bounded slice. Independent acceptance and platform qualification remain
pending for this candidate. D2b-2/d2c-1/
d2c-2 remain planned. The original PR26-based rationale below is retained; its
future-tense d2a obligations are now completed, not open submission gates.

## First correction remains blocked; second correction scope

First correction `55636c067479abdd856bdd349e7d18d224d5e168`, tree
`2c0a8f767f88b701206021dae33d8e2d6bb4d875`, resolves the original four reproductions
but remains independently BLOCKED: an unknown checkpoint execution version can
hide surviving source affinity after all three routing markers are lost, and a
separate WAL writer can grow checkpoint bytes between the raw routing reader's
preflight and retrieval. Its author 165 v3 + 532 compatibility passing cases remain
scoped to that tree. Live193 attempt 1 failed its hard CDC group: the generated fixture documentation
used `operation` instead of the required `op`, so review returned
`PASS_WITH_CONDITIONS`; source was preserved and the patch rolled back. CI442
attempt 1 passed 1636 tests per Python leg on preview
`bbdfd827017b43fae5d792998cfe88aa8246baea`. All first-correction observations
remain separate history, never final qualification.

The second correction treats reserved execution/admission metadata and retained
accepted-source lineage as denial evidence regardless of version value, including
missing/unknown/rewritten versions. It denies unsupported checkpoint extensions
and shapes, passes copied source evidence to the raw discovery gate before provider
work, and preserves the existing exact c2 adapter/registry route. Raw checkpoint
retrieval binds the selected id, encoding and byte length in SQL, caps the actual
returned bytes, and validates them before decode. None of these metadata markers
grants execution. A separate second-correction review and normal current-tree
platform results are required before Ready or integration; reports retain both
prior BLOCKED verdicts.

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

## Accepted baseline and outcome

The original d2a design started from actual PR26 integration `132f1410661e9c3a9034c9d6cd9400eebeda65f9`,
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

The accepted foundation uses additive, versioned records in the existing Program
database. Its names and false authority flags remain frozen. The table below is
d2a historical metadata only. Its fixed semantic witness cannot follow real
execution changes. D2b-1 uses disjoint v3 records, real settlement proof and the
accepted connection-scoped lifecycle primitives, as specified in its contract;
it does not use this metadata chain to grant execution or quiescence.

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

[D2a](P3_5D2A_PROGRAM_CONTINUATION_HANDOFF_TASK_2026-09-08.md) is accepted and
complete through corrected PR27. The initial WAL-control BLOCKED report and the
separate correction PASS remain distinct. Actual merge ordered parents are
`132f1410661e9c3a9034c9d6cd9400eebeda65f9`, then
`dc60201f618c67e9afbdf263c75360df823ef783`; preview `cf33eb7` is separate.
CI439/Live190 attempt 1 qualify that corrected tree only; standard Live Program
remains v1. Do not repeat completed PR26/PR27 gates.

Only d2b-1 has a new definition from accepted PR27. Its scope is host-only v3
admission, actual scope quiescence, fresh-worker continuation and terminal-unaccepted
result recording. It excludes discovery-only/pause/publish handoffs, remote leases,
post-drift proposal refresh and source acceptance. The broader parent states and
journey below remain eventual outcomes with separate owning-slice gates.

| Slice | Deliverable | Required evidence before integration |
| --- | --- | --- |
| d2a — accepted PR27 | Provider-free handoff records and exact atomic worker transition primitives | Real Program/control/lifecycle databases, crash/CAS/bounds/legacy regressions; independent technical review and applicable normal platform gates |
| d2b-1 — defined only | Explicit v3 admission, adapter and scope-quiescent continuation consumer; terminal source remains unaccepted | Actual Git/Safe/discovery across fresh workers and process restart; no duplicate provider/apply invocation; preserved c1/c2 guards |
| d2b-2 | Versioned transition preview/approval/acceptance and host orchestration | Separate exact source acceptance across owner changes; actual 42/43/44 lineage; failed/rejected paths preserved |
| d2c-1 | Typed local Product commands, durable request replay and status | Actual HTTP routing, host-owned project bindings, duplicate/conflict/restart, zero authority on GET |
| d2c-2 | Program controls and evidence review in UI | Actual API-backed first-phase/source-acceptance/next-phase/restart/44 journey; source identities and approval stages distinguished |

The validation and rollout details are in
[P3.5d-2 validation matrix](P3_5D2_VALIDATION_AND_DELIVERY_MATRIX_2026-09-08.md).
D2b-1's consumer contract selects exact v3 record/registry/deny-guard namespaces,
retains separate c2 authority code without shared-helper extraction, and rejects
post-drift proposal reuse without adding refresh/recovery. It requires full current
proof for an unchanged parked proposal and a positive live-invocation settlement
before atomic release. These resolve the d2b-1 design gates. Source acceptance
schemas/consumer details remain d2b-2. Route names, response codes and host
project-binding configuration remain d2c-1; UI choices remain d2c-2. No external
credential or routine owner reconfirmation is needed for this definition.
