# P3.5c-1 — Owned execution Base admission and recovery

Implementation candidate on `feature/universal-coding-agent-source-aware-execution`,
starting at documentation commit `a09dae4ea45deb6e93e67ffe203af4f3965c8576`, whose
parent is the actual PR23 integration `2da3d9f8a9376233c968ec539fc7fee260a1d8b2`.

The parent P3.5c task remains the product acceptance target. Repository inspection
identified a separate filesystem/Git/database preparation boundary that must be
reviewed before wiring a dispatcher. This candidate completes that preparation
boundary only. It does not implement or qualify `42 -> 43 -> restart -> 44`.

## Trusted API and authority

`ProgramExecutionBaseService` composes the actual P3.5b materialization and
acceptance services. `begin(materialization_id, owner_token=...)` admits an actual
current completed materialization, repeats its exact source and inode proof, and
records intent for the next phase. It accepts no destination, source payload,
PASS bundle, Base hash or arbitrary phase/task ID from a caller.

Admission requires an approved unsliced linear plan: the first phase has no
dependency and each later phase depends only on its immediate predecessor in
plan order. The source generation selects the next pending phase. The actual
acceptance must belong to the deterministic task ID of the immediately preceding
completed phase, every preceding phase must be completed, and the target must
have no execution binding. Branching, slicing, missing completion, stale source,
wrong owner/host, pause/resume revision changes, cancellation and realignment
reject admission. No Program or task control state is advanced by this service.

The existing Program-worker ownership row is reused. There is no new lease or
TTL. Attached `BEGIN IMMEDIATE` transactions exclude competing Program, control,
lifecycle and checkpoint writers at allocation/completion; only the Program
database receives the new intent, artifacts and completion records.

## Source, destination and Git identity

The accepted source directory remains immutable and is verified before and
after transfer. An independently allocated `execution-<random operation>/repo`
receives the same complete bytes and modes, without hardlinks. Its parent has an
exclusive ownership marker. Every directory component uses no-follow descriptors;
new files use exclusive creation; no existing file is overwritten.

Git construction uses deterministic in-memory encodings of canonical loose
objects and a Git index v2, followed by the same bounded descriptor writes as
source transfer. This deliberately avoids Git write commands altogether: no
`init`, clone, fetch, checkout, hook, filter, signing helper, template, alternate,
shared object store, graft, replacement or external configuration is consumed.
The index includes exact paths, modes, blob identities, a canonical checksum and
zero cache timestamps; it is not derived from working-tree normalization.

Both SHA-1 and SHA-256 storage formats are supported. The derived detached root
commit has no parents: it is a snapshot of accepted source, and the original
repository objects are not copied or invented as ancestors. Fixed identity and
timestamp fields plus the cumulative source SHA-256 make construction replayable.
There is no remote or fabricated upstream.

Real Git independently reads the constructed commit/tree/blob inventory and
checks exact `HEAD` and a clean index/worktree. All commands use the existing
bounded no-lazy-fetch, deny-all-transport runner, isolated configuration and one
aggregate output/deadline budget. Full source/Git byte and inode proofs are
repeated after Git inspection, which cannot refresh the index under this policy.

The immutable receipt preserves origin repository URL/hash, origin commit/tree,
source SHA-256/generation, acceptance/materialization receipts, target phase/task/
thread and derived Git commit/tree separately. A hash is a byte binding, not a
signature or an independently supplied authority.

## Durable states and recovery

| Boundary | Durable state and permitted explicit action |
|---|---|
| Before destination allocation | `intent`; database record exists, no directory required |
| Allocation identity committed | `allocated`; create only missing exact source/Git files |
| All bytes/fsync/Git/source/authority revalidated | `complete`; return the immutable completion receipt |
| Explicit abandonment of incomplete operation | `abandoned`; retain every filesystem byte and exact reason |

`status()` reads historical database state only. `reconcile()` explicitly
allocates/resumes and verifies. `verify_complete()` repeats all current authority,
source, execution filesystem and Git checks without allocation. Exact duplicate
admission/completion returns one operation/receipt across independent connections.

A directory created before its allocation record commits is ambiguous and is
never adopted, even with a copied matching marker. A corrupt or partial existing
object is never overwritten. An incomplete operation can be abandoned explicitly
and replaced with a new private allocation; a completed operation cannot. Changed
owner/control/source authority is not recovered by inferring a new approval.

Filesystem durability and database commits are separate boundaries. A crash after
fsync but before completion can be reconciled only after full verification. A
completion record alone never makes a corrupted directory eligible for use.
The trusted local filesystem must honor fsync; deadlines are cooperative around
filesystem calls and do not interrupt stalled kernel I/O. The same-UID host and
trusted Git executable remain outside adversarial isolation claims.

## Explicit remaining P3.5c integration

This receipt is not `SandboxInfo`, v2 dependency evidence, Safe scope approval,
transition approval or dispatch authority. It explicitly reports
`dispatch_authorized=false`, `cross_phase_source_handoff=false` and
`automatic_execution=false`. Existing v1 evidence/dispatch APIs are unchanged.

The next implementation must atomically consume the pending-phase Base binding
under current ownership before changing phase state. The current preparation
receipt cannot be revalidated after silently changing its bound control/phase
state. Define a distinct consumed/dispatch receipt and explicit recovery for the
database-to-Safe-checkpoint gap; never relax preparation checks to disguise it.
It must preserve the immutable materialization while using the separate execution
destination, discover the actual 43, obtain a new exact scope approval, and run
the actual Safe services to tested/reviewed 44 after a process restart.

Actual Safe evidence capture must validate the new destination against the stored
v2 execution admission rather than replace the legacy canonical task-path rule
with an arbitrary path. Keep v1 `_prepare_accepted_evidence()` and its same-Base
guard intact. Bind v2 dependency receipts/source generation/derived Base explicitly,
retain transition approval as a separate boundary, and qualify current owner/CAS,
replay, rejected approval, test/review failure and rollback on the new path.

The current tests prove an actual approved Safe 42-to-43 acceptance followed by
owned Git Base construction and fresh-process recovery, for both storage formats.
They are not actual second-phase execution or complete P3.5c acceptance. Normal
current-source CI/Live and separate independent correctness/security acceptance
remain integration gates. No main/PR6/customer environment, deployment, generated
source publication or automatic Program loop is in scope.
