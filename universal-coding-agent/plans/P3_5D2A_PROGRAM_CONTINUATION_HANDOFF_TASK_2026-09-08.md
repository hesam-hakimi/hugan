# P3.5d-2a — Bounded Program continuation handoff foundation

Task ID: `UCA-20260908-P35D2A-CONTINUATION-HANDOFF`
Status: bounded implementation candidate; independent and platform acceptance pending.

## Baseline and authority

Repository `hesam-hakimi/hugan`; target
`feature/universal-coding-agent-structured-edits` at accepted PR26 integration
`132f1410661e9c3a9034c9d6cd9400eebeda65f9`, tree
`884a94d8722e614d72b48892e77aa59ca015d622`.

The owner authorized all necessary preimplementation planning and preparation.
Existing bounded engineering authority persists and now covers this instantiated
foundation implementation. The published definition was documentation only at
`2052562787923a098c9567d02baa515836c854cd`. This candidate does not claim independent
acceptance, platform qualification, Ready, integration or product execution.

Read the complete current canonical checkpoint/state/master/status/receipt, both
PR26 reports, this task and the parent design/matrix, both P3.5c contracts, and the
actual lifecycle/Program/source/Safe consumers relevant to any proposed change.
PR26 and earlier pending submission instructions are historical, not open gates
for their already accepted trees. Preserve initial failures and nonblocking audits.

## Concrete problem and first deliverable

The web runtime releases the worker at every explicit stop. The accepted c2 host
service requires its original exact worker for subsequent actions. Preparation
and source candidates also capture ownership, so a web-only wrapper is insufficient.

Build only the durable handoff foundation and the narrow atomic worker primitives
specified by the parent design. A parked record carries historical next-action
intent; a new owner claim is serialized and epoch-bound. Neither operation grants
Safe execution, verifies a checkpoint/source tree, accepts source or changes a phase.
The eventual v3 consumer must add those proofs independently in d2b.

## Allowed implementation scope

- New `src/universal_coding_agent/product/program_continuation_handoff.py` for
  bounded canonical schemas, receipts, request replay, snapshot/status and transactions.
- A narrow addition to `product/lifecycle_reservations.py` for connection-scoped
  reserve/release checks under the caller's existing attached transaction. Preserve
  existing API behavior, exact-owner CAS, conflicts, recovery and pagination.
- Focused `tests/test_program_continuation_handoff.py` and small additions to existing
  lifecycle tests only where needed to establish unchanged public behavior.
- This task, parent design/matrix and bounded continuity documentation.

Do not edit c2 admission/adapter, c1 verifier, source acceptance, Safe/discovery
entrypoints, v1 evidence, ProductWorkspace, web/UI/CLI or workflow files in d2a.
No new dependencies. If real integration requires those paths, that belongs in the
separately defined d2b/d2c task, or requires a concrete scope revision before editing.

## Required API/record behavior

Proposed Python foundation names: `ProgramContinuationHandoffStore`, `create`,
`park`, `claim`, `close`, `status` and `request_result`. Final signatures may use
existing project conventions while preserving every bound field and behavior.

1. Construct from trusted existing Program/control/lifecycle stores with pinned
   distinct resolved paths and configured host identity. Do not accept a browser path.
2. Create a foundation record only for an existing approved Program under its actual
   current worker; validate current requirement/plan/control and conflict exclusion.
   The descriptor is data, not a claim that a real v3 execution has been admitted.
   D2a must expose `execution_authorized=false` and `consumer_bound=false`.
3. Persist a canonical, bounded descriptor and immutable predecessor-linked receipts.
   IDs/hash/schema/status types are strict; reject duplicate JSON keys, wrong types,
   unknown fields and over-budget reads before Python materialization.
4. `park` compares exact epoch/receipt/request and actual current owner/control rows;
   its transaction writes the parked receipt and deletes only that owner row. A
   caller cannot attach a successful effect/acceptance outcome to this inert record.
5. `claim` requires explicit exact descriptor/proposal confirmation, no current owner
   or conflicting lifecycle action, and unchanged semantic/control inputs. In one
   transaction reserve a fresh owner, consume one parked epoch and record its digest.
   Return the private token only to the trusted local caller, never in public status,
   receipt serialization, exception text or logs. It is not a provider capability.
6. `close` records foundation closure and releases only its owned row atomically;
   it does not complete/fail/cancel Program execution or advance accepted source.
7. Exact completed request replay returns the same immutable public outcome without
   reserving again or returning/reconstructing an old private token. Same request ID
   with a different canonical payload rejects. An owned or unknown post-claim request
   requires explicit diagnosis; a missing client response is not permission to retry.
8. `status` and replay reads use an existing database only, a bounded snapshot and
   allowlisted output; no setup/migration, control mutation, recovery or service load.
9. Existing administrative recovery may remove the exact crash-left worker. Its
   receipt does not close, rebind or advance a handoff. Expose a recovery-required
   blocker when current rows contradict the recorded owned witness; no automatic
   recovery or age-based deletion, including after restart.
10. All modified attached databases must meet the rollback-journal/FULL-or-EXTRA
    contract. Do not claim atomicity for independently committed connections or WAL
    writers. Fault injection must demonstrate the actual transaction boundaries.

No production caller may use the d2a descriptor as a replacement for v2 admission
or as evidence that a Safe checkpoint is quiescent. D2a grants only its documented
foundation state transitions; d2b must refuse records without its own typed consumer
binding, complete current proof and new one-use invocation capability.

## Decisive deterministic validation

Use temporary on-disk databases with actual Program, control and lifecycle stores;
no provider or customer source is needed. Assert unchanged Program phase/execution,
accepted-source and checkpoint rows before/after every foundation operation.

- Create -> park -> fresh-process claim -> close with actual worker row identities.
- Different worker tokens across episodes; no raw token in public outputs/artifacts.
- Competing processes claim the same epoch: exactly one wins, one worker exists.
- Existing remote/program-control/standalone-worker conflicts remain excluded.
- Crash before and after each Program/worker transaction commit. Inspect both stores
  after restart, including lost-response replay and missing process-local token.
- Old owner, old epoch, stale proposal, source/requirement/plan/control change,
  cancelled/paused/realigned Program, tampered/missing receipts and mismatched host.
- Exact duplicates, conflicting request reuse, excessive rows/fields/JSON/aggregate,
  malformed canonical data and unsupported journal/synchronization settings.
- Explicit existing administrative recovery leaves a visible blocker and cannot
  become a fresh claim automatically. Reads must preserve byte/logical state as
  appropriate to the existing SQLite mode and load no effectful service modules.
- Existing lifecycle reservation/recovery/index/pagination tests and relevant v1,
  c2 and PR26 F1/F2 regressions remain required compatibility evidence.

Only broaden tests for a concrete risk or a required gate. Do not run a full suite
or paid Live while this branch contains only the definition documents. For the
implementation candidate, run focused tests, Ruff and diff checks, publish a Draft
PR to the accepted target and inspect actual current-tree CI/Live logs/outcomes.
If web paths are unchanged, do not claim a new Web workflow run. Counts overlap.

## Completion gates and successor control

D2a acceptance requires exact head/tree identity, relevant deterministic and normal
platform qualification plus a separate independent technical review using its own
checkout. The review must inspect the full implementation delta and the actual
transaction consumers, verify the crash/CAS/security boundaries, state what it ran,
and preserve failures. It is not human GitHub APPROVE or blanket security approval.
Normal Ready/expected-head-locked merge and actual tree/ordered-parent/target-ref
verification follow only when every applicable gate is satisfied.

D2a success proves an inert foundation only. It does not establish v3 dispatch,
checkpoint recovery, source acceptance across requests, API/UI continuation or the
actual cumulative Product journey. Define d2b-1 from the then-accepted target before
its implementation; no other successor branch/task is instantiated now.

Exclude main, PR6, root todos.md, AskTD/ETL/customer work, credentials, deployment,
history rewriting and generated-source publication. Preserve the legacy Git helper
and other nonblocking follow-ups. No autonomous scheduling or background monitoring.

## Implemented foundation contract (candidate)

`ProgramContinuationHandoffStore(programs, lifecycle, host_id=...)` uses the actual
Program's control store. It pins all three existing paths and device/inode identities;
the host binding includes those identities. It opens an operation-scoped connection,
attaches lifecycle and read-only control, and writes only the three additive handoff
tables and the exact lifecycle worker row. It never constructs a Product workspace.
Mutations require durable rollback journals/FULL-or-EXTRA on both original writer
connections and both attached writers. Existing public lifecycle methods are unchanged.

`create` accepts canonical descriptor bytes and the private current worker token.
The descriptor requires the foundation schema, Program/phase and optional existing
Task/thread, approved requirement/plan hashes, current source generation/head receipt
(or explicit absent-source values), and admission/checkpoint/result/approval-core
hash references. References are data only. `next_action` is exactly `foundation_only`;
both authorization flags are false. Existing registered/recorded c2 executions are
not adopted. The complete database Program/phase/execution/control/source witness is
hashed; private control and owner rows are never included in public records.

`park` and `close` require exact expected epoch/receipt and the current private owner.
`claim` additionally requires the exact descriptor/proposal digests and `confirmed=True`.
All operations use immutable predecessor receipts and host/Program/request digest
binding. Park/close release inside the receipt transaction. Claim reserves a new
worker and advances the epoch inside that transaction. A first claim returns its
private token through a local `HandoffResult` envelope; serialize only `result.public`.
Completed replay returns that same public outcome and no token. Unknown/in-progress
requests require diagnosis, and administrative owner removal leaves a visible blocker.

The descriptor and semantic witness remain fixed throughout this inert lifecycle.
Changed Program/control/source rows reject; there is no proposal refresh or consumer
reconciliation in d2a. Database hashes are compared to the caller's exact approved
hashes; this foundation does not read/attest plan artifacts, source bytes or checkpoints.
Those proofs and any consumer-specific witness transition belong to d2b.

Metadata parsing is bounded before materialization: 128-byte ASCII identifiers,
64 KiB JSON records, eight nesting levels, 64 object fields, 4 KiB database scalar
fields, 1 MiB aggregate reads and bounded SQLite work/time. Program phase/execution
sets are capped at 100. Status uses receipt-sequence keyset pages of at most 100 and
validates each returned receipt plus its immediate predecessor. Mutations validate
the complete predecessor chain within the same aggregate/work budget and reject
oversized history. No automatic pruning, migration, recovery or effect retry exists.

`status` and `request_result` use existing read-only connections and bounded snapshots.
Status is recorded metadata, not provider authority or a full historical audit. No
production caller, v3 adapter, source acceptance resolver, HTTP route or UI is added.
