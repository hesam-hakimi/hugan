# P3.5c-2 implementation contract

This is an explicit execution API for approved unsliced linear Programs. The first
phase retains the existing original-Base path. Later phases consume a complete
execution Base by operation ID and exact receipt digest, never by caller path or
copied receipt. Execution schema `uca-program-source-dispatch-2` is independent
of the semantic/line-addressed edit protocol.

## Authority and transactions

The existing Program worker owns admission, discovery, Safe execution and source
acceptance. Its complete ownership binding, approved requirement/plan, control
revision and accepted source predecessor are compared at every effect boundary.
Consumption verifies the unchanged c1 preparation contract before atomically
inserting the v2 admission, Program execution, running phase and task control.
The same transaction registers the task/thread in the shared control database;
Safe's public entry points consult that registry. No provider is invoked while a write transaction is held.

After consumption, a distinct validator checks the stored admission and current
execution authority. It does not relax c1's pending-phase verifier. The original
repository, immutable accepted materialization and private derived execution Git
remain separate. All accepted material bytes, execution inventory and Git metadata
are verified; only approved edit paths may change during actual Safe edits or
rollback. Every host test profile is mandatory.

## Explicit handoffs and recovery

Durable states are admitted, discovery_started, discovered, safe_started,
awaiting_scope_approval, resume_started and terminal. Each effectful call first
claims its state with a database CAS. Duplicate connections cannot start the same
call. Discovery saves its actual result and exact proposed Safe task before Safe
starts. Scope approval binds the actual new manifest hash and an explicit decision.

Status is a database-only historical read. Reconciliation is explicit and does
not invoke a provider. A discovery_started operation without a committed result
is ambiguous and cannot be replayed. After safe_started or resume_started,
reconciliation may record only the actual matching scope-stop or terminal
checkpoint, with matching task, thread, source, authority and retained filesystem
proof. An intermediate checkpoint or a committed scope decision without a proven
terminal checkpoint is fail-closed; it is not permission to repeat provider work.
There is no new worker lease, timeout-based takeover or automatic Program loop.

Safe results and Program phase results derive from the actual checkpoint. Their
database changes and expected authority are committed together. Artifact writes
precede their associated database changes under the same authority transaction
and are hash-bound in the resulting record; a failed
transaction cannot turn orphaned files into accepted evidence. Exact source
transition approval is a separate operation and revalidates the admission.

Capability reports describe only qualified explicit v2 progression. Existing v1
same-Base evidence and capability meanings remain intact. Qualification must
exercise actual discovery, Safe, subprocess tests, independent review provenance,
fresh processes, failures and byte-preserving 42 -> 43 -> 44 source lineage.

## Multi-database durability

Admission and Program-result transactions write only the Program and shared control
databases. Both must retain on-disk rollback journals with synchronous FULL or EXTRA;
v2 fails closed on WAL, MEMORY, OFF or weaker synchronization for those writers.
The attached Safe checkpoint database remains WAL and read-only in these transactions.
Its separate invocation/checkpoint handoff is reconciled as described above. This
keeps every modified database inside SQLite's super-journal commit contract; it does
not claim cross-database atomicity for WAL writes.

References: [SQLite super-journals](https://sqlite.org/tempfiles.html#super_journal_files)
and [ATTACH transaction guarantees](https://sqlite.org/lang_attach.html).

## Explicit host API

Construct `ProgramSourceDispatchService(preparation, provider)` using the existing
acceptance/materialization/Base services and their shared control and lifecycle
stores. Keep the current Program worker token for this bounded operation.

1. Finish c1 preparation and obtain its `completion_sha256` from `preparation.status`.
2. Call `admit(operation_id, preparation_receipt_sha256=..., owner_token=...)`.
3. Call `dispatch(operation_id, owner_token=...)` once. Inspect the returned exact
   `scope` and `scope_sha256` at the actual Safe approval checkpoint.
4. Call `approve_scope(operation_id, owner_token=..., scope_sha256=...,
   approved=True/False, approval_id=...)` for that reviewed scope.
5. For a completed execution, use the existing acceptance service's `prepare` and
   separate exact `accept` calls. Construct the dispatch service again when
   reopening those stores so v2 capture has its explicit trusted resolver.

`status` loads only bounded database records. `reconcile` can recover a proven
scope or terminal checkpoint without a provider call. A `discovered` state may
continue through explicit `dispatch` without repeating discovery. Intermediate
ambiguous work remains stopped. Failed terminal Programs remain blocked; their
historical status remains readable. No UI endpoint or automatic scheduling loop
is introduced by this bounded API.
