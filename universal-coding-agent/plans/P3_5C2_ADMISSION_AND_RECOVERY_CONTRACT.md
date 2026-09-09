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
Safe's public entry points consult that registry. Before any admission, a separate
durable binding pins the Safe checkpoint root to the trusted control database's
path/device/inode. Default or unrelated control stores cannot resume the same
checkpoints. Legacy discovery checks that boundary before sandbox, provider or
artifact work; pause/cancel also verify the root's actual control binding.
No provider is invoked while a write transaction is held.

After consumption, a distinct validator checks the stored admission and current
execution authority. It does not relax c1's pending-phase verifier. The original
repository, immutable accepted materialization and private derived execution Git
remain separate. All accepted material bytes, execution inventory and Git metadata
are verified; only approved edit paths may change during actual Safe edits or
rollback. Every host test profile is mandatory.

## Explicit handoffs and recovery

Durable states are admitted, discovery_started, discovered, safe_started,
awaiting_scope_approval, resume_started and terminal. Each effectful call first
claims its state with a database CAS. The explicit transaction issues a process-local
random invocation capability, persists only its digest, and consumes that digest
with another CAS before provider/graph entry. A newly constructed adapter cannot
recover or repeat a started invocation, including a crash before the claim. Active
node callbacks require the same live consumed capability. Duplicate connections
cannot start the same call. Discovery saves its actual result and exact proposed Safe task before Safe
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
and are hash-bound in the resulting record. Each proven checkpoint uses a separate
immutable result/report path; writing a terminal report cannot overwrite the prior
committed scope report if the database transaction rolls back. Orphaned files do
not become accepted evidence. V2 evidence consumers derive these exact paths from
the proven checkpoint, while v1 retains its existing path and Base checks. Exact source
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

## Known local edit failure

The bounded Git adapter preserves `check=False` return codes so the existing Safe
edit engine can detect rejected edits and enter its rollback path. A live known
partial apply may restore only that attempt's approved existing files. Before any
restore write, it verifies current owner/control, the entire immutable material,
all unrelated source and Git bytes, complete inventory, and no-follow file and
directory identities. Only bounded partial bytes of that live attempt may differ.
Restoration writes the exact accepted Base bytes and records a verified retained
proof. Changed authority, extra files, links or replaced identities stay fail-closed;
they do not grant repair permission. Process-interrupted edits remain ambiguous.

## Submission review history

The first PR25 head `fb033d6e57b580bd609a6796fef7984b880cbbcb` passed 1,294
tests in both CI432 Python jobs and standard Live183 attempt 1, but independent
review blocked it on five reproduced entrypoint/replay/artifact/rollback defects.
The 2026-09-08 correction addresses those findings with new regressions. Its own
exact-source independent review and platform gates remain required. The initial
report and successful old-source checks remain historical evidence.

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
