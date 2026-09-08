# P3.5d-2b-2 — Evidence core and atomic source acceptance contract

Status: documentation-only definition from actual accepted PR28. This is the
binding contract for [the bounded task](P3_5D2B2_SOURCE_TRANSITION_ACCEPTANCE_TASK_2026-09-08.md); no runtime implementation
or evidence family is complete for this new slice. It specializes the parent
Product design's reserved candidate/approval version 2 to a final v3 result.

## 1. Version and authority boundaries

Use `uca-source-candidate-2`, `uca-source-approval-2` and
`uca-source-acceptance-receipt-2`. New bounded metadata uses distinct version-2
schema names for evidence core, preview/decision request, response and capture
witness. Snapshot-1 and transition-1 pure byte semantics remain unchanged.
Execution remains `uca-program-source-dispatch-3`; edit protocol version is
independent. Existing candidate-1, approval-1, receipt-1 and their owner-bound
services remain unchanged. D2a reports `execution_authorized=false` and
`consumer_bound=false`; no metadata record authenticates itself.

The trusted local host binds all existing Program/control/lifecycle/Safe/remote
stores, their real paths/device/inodes, artifact roots, owned-source root,
repository/origin, Git policy, source limits and trusted test/reviewer policy.
Record a new acceptance-host digest separately from the existing source-host
digest. Never rewrite `program_source_heads.host_sha256` to switch adapters.
The command caller supplies only allowlisted IDs, exact hashes/revisions and an
explicit decision. No caller paths, checkpoint objects, PASS payloads, provider
configuration or owner token are authority inputs on the new public host API.

Only a complete settled final v3 unit of the bounded two-phase linear Program
is eligible. A valid terminal receipt with terminal status completed is necessary
but insufficient: its full history, current evidence and current exclusion of
work must also verify. Failed/blocked terminal records remain history. The v3
terminal's old `source_acceptance_authorized=false` and generation-1 witness stay
unchanged after a new acceptance; a receipt-2 records the later source action.

Terminal-proof extraction validates the historical admission/receipt/request/
settlement chain, revoked invocation and post-release semantic witness without
calling the live execution `_load` path with a substituted owner. Compare that
recorded post-terminal semantic witness with the current baseline before preview
claim, then exclude only the newly reserved acceptance worker from the stable
comparison while independently checking its complete row. Root locator, Safe
guard and control registry must all agree; surviving affinity with missing or
unknown records is denial evidence. A status read after source acceptance checks
historical predecessor links, not a false equality between the old execution's
generation-1 witness and the new generation-2 current head.

## 2. Exact reviewed core versus temporary witness

Candidate-2 contains an immutable evidence-core digest and all exact review
identities. The core includes:

- Program/requirement/approved-plan identity, deterministic phase/task/thread,
  origin repository/commit/tree and explicit v3 execution schema;
- predecessor source snapshot, generation and acceptance receipt; exact prepared
  transition, proposed resulting snapshot, allowed paths and changed bytes/modes;
- v3 admission, c1 complete preparation/materialization and derived Git Base/tree,
  dependency lineage, terminal receipt, settlement, terminal request/response,
  decision, checkpoint identity and result/report identities;
- actual complete canonical Safe/Program evidence: scope decision, structured
  edits, Git patch and validation, all trusted test results, independent reviewer
  context/validation/provenance and PASS, final report and retained filesystem/Git
  proof. Hashes bind these bytes but do not substitute for their verification;
- stable semantic authority baseline: exact Program/phase/execution and control
  rows/revisions, source head, relevant administrative recovery history and all
  host/source/test/Git policy bindings at preview.

The temporary *current capture witness* is separate. It binds the complete fresh
worker row, the same semantic baseline, actual pinned store identities, exact
selected checkpoint bytes and full observed filesystem/Git inventory. Compare
that complete witness from claim through capture and commit. Do not delete owner
fields from an old v1 candidate or relabel a c2/v3 execution owner to achieve a
match. Historical execution-owner digests inside immutable v3 records remain
historical provenance; only the new current witness authorizes acceptance work.

Candidate-2 is a strict canonical object binding program/task, candidate revision,
core/transition/before/after hashes, expected generation, terminal receipt and new
host digest. It is persisted before being returned. Its hash excludes its own hash
and does not depend on a future decision, receipt or response. Approval-2 binds
candidate hash/revision, core hash, transition hash, predecessor/generation,
terminal receipt, action, boolean decision, approval ID and request ID. Receipt-2
binds those immutable objects plus the resulting generation and witness digest.
Response binds the receipt last. No hash cycles or self-certified future writes.

## 3. Explicit host operations

Public method spellings may follow local conventions; these distinct semantics
and arguments are required. They are Python host operations, not new endpoints.

| Operation | Inputs and allowed effect |
|---|---|
| `preview_source_transition` | Program/operation, request ID, expected terminal receipt and source hash/generation; reserve a fresh worker, fully capture, persist candidate + response and release atomically |
| `decide_source_transition` | Exact returned candidate/revision/core/transition/predecessor identities, request/approval IDs and approved boolean; fresh worker, verify, accept or reject once |
| `source_transition_status` | Bounded recorded metadata only; no preview creation or current authority claim |
| `source_transition_request_result` | Exact completed stored response after validating immutable request/response linkage; never restores worker/token/ticket |

After preview returns, no worker, callback, owned child or remote lease is held
for the later human decision. Accepted PR28 terminal settlement must be proven
before preview admission. Preview itself runs no discovery, Safe graph, provider,
tests or model review. Bounded read-only Git verification may create a tracked
subprocess; it must return and settle before release. Merely writing a candidate
or observing no handles in another process is not proof of that return.

One candidate per task/semantic baseline is prepared; exact duplicate preview
requests return the same response. A different concurrent preview request for
that same task does not create another revision. Rejecting the exact candidate
records an immutable rejected decision and response, releases the fresh worker
and leaves source untouched. Rejection is final for that candidate; no later
acceptance or replacement candidate is inferred. Source/control/plan/policy or
administrative recovery drift blocks the old proposal; this slice has no
post-drift refresh or rejection-reproposal workflow.

The host orchestration companion exposes these one-action boundaries and returns
after each. For the fixture, first-phase 43 uses accepted v1 execution/acceptance
within its existing owner episode. A later explicit c1 materialize/prepare/admit
episode keeps the same owner through consumption. Scope decision after restart
uses accepted PR28. The final new preview and acceptance use distinct fresh
episodes. No helper automatically accepts, starts a phase, or chains a returned
proposal into the next action.

## 4. Reservation, capture and commit

Use the accepted connection-scoped lifecycle reservation/release primitives.
Do not call public methods that commit another connection inside a transaction.
A bounded request claim and fresh Program-worker reservation commit together.
The raw token remains private to the live call and is never recoverable from
records or returned values. Existing workers/reservations or nonempty remote
leases for the Program/tasks block a new claim. No TTL takeover or owner-row
substitution is permitted.

Use a distinct acceptance transaction policy. Do not expand the v3 execution
store's authorizer into a generic write surface. Program and lifecycle are the
only mutated databases for new acceptance requests; both must be existing on-disk
rollback-journal databases with synchronous FULL or EXTRA. Control, Safe and
remote stores are logically read-only and writer-excluded through final commit,
including their permitted WAL mode. Pin all paths/inodes and repeat schema,
durability and host checks. Mutating PRAGMAs, trigger/view substitution and extra
write tables are denied. SQLite super-journal limits remain the accepted local
durability contract; no atomic WAL multi-writer claim.

Capture may run outside the short claim transaction with the durable worker
retained. At the final transaction repeat the exact full semantic/current-owner
witness, terminal history, actual selected checkpoint and immutable artifacts,
and retained source/Git checks. Hold exclusion through commit, not only through
the first read or last comparison. Any competing writer that wins before the
final lock is acquired must make the comparison fail. In-process registration
locks/revocation and settlement must prevent late owned work until release.

No filesystem source edits, materialization, cleanup or artifact-path overwrites
are part of acceptance. Retain canonical captured bytes in the bounded immutable
database artifact store; recapture actual existing files, not just stored copies.
Use no-follow descriptors, exact inventory, byte/mode and inode checks for origin,
accepted material and derived execution, preserving only the already approved
retained patch. Verify before and after read-only Git inspection. Trusted same-UID
host/filesystem assumptions remain explicit: SQLite locks do not lock arbitrary
filesystem writers, and no hostile same-UID isolation is claimed. Any observed
replacement, link, extra path, metadata or byte drift blocks acceptance.

## 5. Shared source head and versioned ledgers

Keep `program_source_heads` as the sole accepted source head and
`program_source_artifacts` as bounded immutable bytes. New candidate/decision/
request tables and their schema/index attestations are separate from candidate-1.
Insert the accepted receipt-2 into the shared `program_source_acceptances` ledger
as well as its versioned decision ledger in the same commit. The existing
`UNIQUE(program_id, task_id)` remains the cross-version one-acceptance barrier.
Do not insert a fabricated candidate-1 index row or receipt-1 envelope.

The final successful transaction atomically persists approval-2, after snapshot,
receipt-2, shared/versioned ledger entries, the exact completed request response,
source-head CAS from expected generation/source/receipt to generation + 1 and
the new receipt, and exact worker release. Any failure rolls all those writes
back. The receipt preserves existing source-host digest plus the new
acceptance-host digest; it sets `materialization_ready=false`,
`execution_authorized=false`, `automatic_execution=false`. It certifies source
acceptance only. Program/phase completion, task control, v3 admission/terminal
history, original repository and accepted generation-1 material are not rewritten.

Old acceptance methods must deny candidate-2/v3 before effects; they do not gain
a resolver that permits owner substitution. Old materialization/c1/c2 dependency
consumers continue to reject receipt-2. This is intentional bounded scope:
generation-2 44 is the final accepted source, with no third-phase preparation.
A future consumer needs a separately defined exact receipt-2 resolver.

Provide a separate bounded recorded-status reader that understands the original
receipt-1 at generation 1 and receipt-2 at generation 2, verifies all metadata
links, exact complete lineage and c1/v3 combined history, and reports both.
It must not call the old v1 status reader as fallback when v3 markers exist.
Old Product/API status wiring remains unchanged. A standalone new read must use
existing read-only stores and never construct effectful services/setup tables.
It reports `source_bytes_verified=false`, `filesystem_verified=false`,
`current_authority_verified=false` and no live execution capability.

## 6. Completed replay, crashes and invalidation

Key requests by new host, Program and request ID. Canonical request digest binds
the action and all explicit arguments. Same key/different action or payload is
a conflict. An exact completed request returns the identical stored response
after bounded full linkage validation, without reserving a worker or recapturing
current files. That response is historical evidence of its committed action;
later drift does not turn it into current execution/acceptance authority.

Pending requests cannot be replayed as work after a process dies. A request
claim and worker reservation survive as ambiguous; a reconstructed service,
empty local handle registry, checkpoint or old token digest cannot release them
or finish the operation. Existing explicit audited administrative recovery may
clear the exact stale row, but its changed recovery history invalidates the old
proposal and grants no approval. Recovery-and-refresh is outside this slice.

Before claim commit, a crash leaves no claimed request/worker. After claim but
before final commit, no source acceptance may be visible. A crash inside the
final transaction must leave either the entire old state with its pending owner,
or the entire committed acceptance + response + released owner. Immediately
after commit, loss of response is solved only by exact completed replay. Prove
these with external process termination, not only exception rollback hooks.

Control pause/resume revision changes, cancellation, realignment, disposition,
host/source/plan/policy drift, source advance and administrative recovery block
the pending proposal. No automatic reapproval, next phase, provider retry or
cleanup follows. Unknown schemas, missing guards, ambiguous checkpoint shapes,
incomplete c1/v3 or closed d2a history and failed/conditional evidence block.

## 7. Bounded readers and verification limits

Small canonical metadata records: maximum 65,536 bytes, aggregate 1 MiB per
logical read, depth 8, at most 100 history rows, bounded 128-byte identifiers.
Large source/evidence blobs use the existing explicit source-policy bounds:
24,000,000 bytes per artifact, 16,000,000 aggregate source/evidence raw bytes,
1,000,000 per file, 20,000 files and 1,000 changed/allowed paths; stricter configured
limits win. Enforce a 256,000,000-byte cumulative read budget for each complete
preview/accept capture, including repeated checks, before allocating payloads;
exhaustion blocks the operation rather than skipping verification. Avoid silently
applying the small metadata budget to large complete evidence or dropping it.

Checkpoint retrieval retains the PR28 maximum 16,000,000 selected raw bytes and
exact type/encoding/ID/length checks in the actual SQL projection before decoding.
Do not reintroduce a size-preflight/retrieval gap. Bounded parser depth, duplicate
key and noncanonical checks apply before trusting records. SQL progress, lock
timeouts, complete bounded history queries and read-only PRAGMA allowlists apply
to new services and registration paths. Git subprocess checks reuse trusted
deny-all-transport configuration, aggregate output and monotonic deadlines;
no provider runs in a write transaction. Filesystem syscall deadlines remain
cooperative, not hard interruption of stalled kernel I/O.

## 8. Acceptance evidence and exclusions

All A01-A12 in the task are required for implementation. A01 must demonstrate
the separate reviewed preview at terminal-unaccepted 44, close that process,
accept exactly once in another process, and expose the complete accepted
42/43/44 lineage. A12 must preserve PR26 F1/F2 and the corrected PR28 root
locator/source-affinity denial, bounded raw reads, full d2a history, bounded
registration/revocation and mutating-PRAGMA protections. Keep negative evidence.

No source publication, v1/v2 migration, remote lease handoff, discovery/publish/
control-pause continuation, post-drift proposal refresh, HTTP/API/UI/CLI wiring,
scheduler, workflow or third-phase consumption is authorized here. Future
implementation needs its own independent exact-tree review and normal platform,
Ready and expected-head integration gates. This definition inherits no runtime
qualification from PR28 for new acceptance behavior.
