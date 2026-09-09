# P3.5b-3 owned source materialization contract

Implemented on actual PR22 merge `cd08bf64832dd4cc8c66bd267cb6abf245a325e9`.
PR23 integrated this contract at `2da3d9f8a9376233c968ec539fc7fee260a1d8b2`,
tree `325f8160cf85b7ceafcc23dc8a17d47a57202986`, on 2026-09-07T17:32:18Z.
CI428 / Live179 attempt1 and the separate independent correctness/security PASS
qualified that exact tree. See ../reviews/PR23_INDEPENDENT_REVIEW_2026-09-07.md.

## Authority and API

`ProgramSourceMaterializationService` is a trusted host adapter around the existing
`ProgramSourceAcceptanceService`. Its only admission inputs are Program identity,
an actual stored acceptance receipt SHA-256 and the existing private lifecycle
worker token. It loads the accepted snapshot from the immutable Program database
and checks current source generation/predecessor, repository/requirement/plan,
host policy, exact Program/control record and current worker ownership. A caller
cannot supply a snapshot, PASS report or destination path.

- `begin` records an immutable intent and returns durable status. It does not
  allocate a directory. Concurrent identical active requests return the same ID.
- `reconcile` is an explicit owner-bound operation. It allocates or resumes the
  existing operation and returns an exact verified completion receipt.
- `status` reports historical database state. It does not inspect the filesystem,
  claim current usability, recover, invoke a provider or advance a phase.
- `verify_complete` requires a complete operation and repeats current authority,
  lineage, complete bytes, directory ownership and persisted filesystem identity
  verification. A copied receipt is never sufficient admission for future use.
- `abandon` records an explicit reason for an incomplete operation. Exact replay
  is idempotent; a different reason is rejected. It performs **no filesystem
  deletion**, including ambiguous directories. A new `begin` may then allocate
  a different random operation. Completed operations cannot be abandoned.

No new lease, TTL, recovery daemon, HTTP route, dispatcher, Git checkout or
`SandboxInfo` is added. Recovery by a changed worker does not silently inherit the
old operation: exact owner/control binding rejects it. Existing lifecycle
recovery remains separate. Historical rows remain inspectable after invalidation.

## Database and filesystem handoffs

| Durable state | Filesystem possibility | Explicit next operation |
| --- | --- | --- |
| `intent` | Absent name | Exclusive allocation; then commit allocation identity |
| `intent` | Existing name, including a marker after a crash | Reject adoption; explicit abandonment preserves all bytes |
| `allocated` | Marker and source directory with recorded device/inode identities | Verify existing exact files; create only missing files with exclusive opens |
| `allocated` | Incomplete/corrupt existing file, extra entry, link or substituted identity | Reject without overwrite; explicit abandonment preserves all bytes |
| `allocated` | Complete synced tree; completion commit was interrupted | Re-sync and verify; commit the same content-bound completion |
| `complete` | Expected unchanged tree and current owner/lineage | Repeat full verification; return the same receipt |
| `complete` | Missing or changed bytes, metadata/inodes or current authority | Reject current use; preserve historical receipt and files |
| `abandoned` | Any retained staging contents | Report only; never adopt or clean automatically |

Each SQLite transaction writes only the existing Program database. Its attached
control/lifecycle/Safe checkpoint databases are held against competing writers
using the existing `BEGIN IMMEDIATE` boundary. Durable intent is committed before
filesystem allocation. Allocation records commit before source writes. A source
completion receipt commits only after exact file verification, file/directory
fsync, repeated filesystem verification and owner/control/source revalidation.

These are **separate transactions and filesystem operations**, not cross-system
atomicity. In particular, a directory created before allocation identity commits
is deliberately ambiguous after process death. It is never treated as owned just
because a matching marker can be read. An interrupted partial file is never
overwritten during recovery. Exact existing files are re-synced before recovery
completion because visible cached bytes alone do not establish durable writes.

No rename or dispatchable path switch is required: the database completion is the
exposure boundary. There is therefore no rename failure path to qualify. No old
sandbox or accepted snapshot is modified. Failed additional operations leave
previous complete directories and their historical evidence intact; current use
still requires the corresponding accepted lineage and worker/control authority.

## Filesystem boundary and resource limits

The existing Safe sandbox root supplies the host path. Every absolute component
is opened with `O_DIRECTORY | O_NOFOLLOW`; device/inode/owner/mode identities for
the complete root chain are bound in the durable intent and rechecked on recovery
and completion. The root must be owned by the executing user and not writable by
group/other users. Unsupported descriptor/no-follow platforms fail closed.

A new `source-<random operation UUID>` directory is created exclusively with mode
0700. Its separate `.uca-owner.json` marker is exclusive, exact and mode 0600.
Accepted source lives under `source/`, so user paths cannot collide with the
marker. All descendant traversal and writes are relative to open directory
descriptors; existing files are never opened for writing. Parent substitution
cannot redirect traversal through a link. Directory identity is rechecked after
use and the root chain is re-opened before completion. Files must be regular,
single-link, owned, on the same filesystem and exactly mode 0644 or 0755.

Complete traversal rejects extra files, unexpected empty directories, symlinks,
hard links, special files, missing bytes and executable/mode drift. It preserves
all original bytes, including unchanged binary, empty files, CRLF and no final
newline. The completion proof also binds file/directory device/inode, mode, owner,
size, link count and modification/change timestamps. Access time is excluded;
ordinary reads do not invalidate a receipt. Even an equal-byte replacement inode
invalidates an already completed receipt.

Existing source policy bounds still apply. Additional host policy defaults are
40,000 total source entries, 8,000,000 bytes of verification/path metadata and a
60-second cooperative deadline (maximum configurable 300 seconds). Directory
layout is bounded before allocation. Directory scans stop at the first unexpected
entry, file reads/writes use at most 65,536-byte chunks, and deadlines are checked
around I/O and before completion. The deadline prevents late acceptance; it is
**not a watchdog for a stalled kernel/filesystem syscall**. This adapter requires
a trusted local filesystem honoring fsync. It does not claim power-loss durability
against a lying storage stack or isolation from a compromised same-UID host.

The host/executable and its owned state root remain the trust anchor. Hashes are
content bindings, not signatures. No filesystem cleanup is provided in this slice;
abandoned storage remains visible for separate bounded operator handling. There
is no broad reset, clean, deletion, origin fetch, filter, hook or project execution.

## Distinct source and execution identities

The completion receipt binds its intent, allocation, actual acceptance receipt,
cumulative source SHA-256/generation/predecessor and verified filesystem proof.
Origin Git commit and tree remain distinct recorded values. Derived Git commit
and tree are explicitly null: this slice needs no Git object construction. This
is a complete owned **source directory**, not a fabricated checkout or upstream.

Materialization completion grants no new scope approval, transition approval,
publication authority or execution approval. The existing v1 same-Base evidence
handoff is unchanged. There is no provider call on reload, phase advance or
automatic execution. The later source-aware dispatch contract must define its
own admission and Git/execution identity and separately qualify
`42 -> 43 -> restart -> 44` through actual dependent Program executions.

## Qualification intent

Tests use the actual Git/Program/Safe/acceptance fixture, including a real approved
42-to-43 Safe transition, rather than fabricated accepted snapshot DTOs. Real
subprocess death covers intent commit, mkdir, allocation update before commit,
allocation commit, partial file write, file fsync, complete tree verification,
completion update before commit and completion commit. Fresh processes read only
before explicit owner-bound reconciliation. Negative fixtures cover authority,
root/parent/link substitutions, byte/mode/inode drift, missing/extra entries,
write/ENOSPC/fsync/database failures, concurrent SQLite connections and resource
bounds. Current-source CI428 passed 1147 tests on each Python 3.11/3.13 and all
five Py3.11 smoke groups; five duplicate Py3.13 groups were intentionally skipped.
Live179 passed 201 deterministic tests and all six actual outcomes plus final
enforcement. These counts overlap. All jobs checked out preview
`11eedb7d095a957e0e913dceaa8e4cc1a8dadb4e`, with the exact integrated tree and
ordered parents target then head. The preview is not the actual merge or head.
The separate agent report completed PASS at 2026-09-07T17:26:09Z; it is not a
human GitHub APPROVE. The six Live179 artifact ZIPs were not independently
downloaded or rehashed. Source-aware Program dispatch remains unimplemented.
