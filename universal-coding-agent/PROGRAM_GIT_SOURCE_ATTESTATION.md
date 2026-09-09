# Program Git-source attestation — P3.5b-1

This slice starts from actual PR20 merge `204d3e39543aab442c05ce9605b407af7f29ea07`
on `feature/universal-coding-agent-structured-edits`. Its tree is
`8712fab44f2f114bbdeccb2a7b1fe6da623057f0`; ordered parents are the previous target
`d6b346716f1db7d5241145b584899de68ab28c52` and reviewed head
`f46ceb4b7084fe463f4395be3eb07f15aec71ba9`. This is an actual merge, distinct from
the previously qualified preview `1d39386d3a6cc42c6e906c880fec1d858dec275f`.

## Implemented boundary

`ProgramGitSourceAttestationService` is a provider-free, read-only host adapter.
It attests the complete supported tracked-file set at an immutable Git commit
and returns a generation-zero P3.5a snapshot, full inventory, and canonical
receipt. It has no Program dispatcher, Safe execution, artifact admission,
database, approval, filesystem materialization, or publication caller.

The host constructs the service with an exact repository root and its trusted
logical repository SHA-256 identity. Each request must match that binding. The
host binding digest also includes the canonical absolute root, so moving a
repository changes this host-local identity even if its source is identical.
Caller-provided names, remotes, documents, or hashes do not bootstrap trust.
The host is responsible for binding the intended repository and trusted Git
executable. This adapter does not authenticate a GitHub account or protect
against an adversary who controls the trusted host process or Git executable.

The adapter supports POSIX ordinary repositories, linked worktrees and bare
repositories with SHA-1 or SHA-256 object storage. It rejects an ancestor
repository discovered from a supplied subdirectory. Root/directory identity,
repository layout and storage format are checked before and after the read.
Platforms without its bounded pipe/process-group implementation fail closed.

## Complete object proof

Fixed argument-vector `git cat-file --batch-check` operations establish object
types and sizes before content reads. `--batch` returns raw objects with
size-delimited framing. The adapter recomputes each commit, tree and blob object
ID from its type, decimal byte count, NUL separator and exact payload. It checks
the commit's tree header against the expected origin tree and traverses every
raw tree entry, including unchanged files, binary blobs and executable modes.
Missing objects, altered payloads, incomplete framing, unexpected trailing
output, duplicate names, noncanonical order and unsupported modes reject the
whole operation; no partial attestation is returned.

Tree directories, including empty entries, are traversed and validated. The
P3.5a file snapshot contains files; an empty directory does not invent a file.
Its original Git tree remains a separate immutable identity. Snapshot hashes
must not be substituted for Git trees or commits when later materializing a
sandbox or creating a derived Git revision.

All file and directory names pass the existing conservative P3.5a portable
path contract. Symlinks, gitlinks/submodules, case collisions, file/directory
conflicts and unsupported spellings reject the complete source. The original
path limits are not weakened to accommodate a repository.

The adapter never reads checkout file contents or applies clean/smudge,
textconv, line-ending conversion, replacement objects or LFS expansion. Its
isolated environment removes inherited Git repository/config overrides and
disables replacement objects, lazy fetching, optional locks, prompting, hooks,
credentials, external protocols, fsmonitor and external diff behavior for its
fixed operations. It does not invoke repository text as shell code.

Every command requires the global `--no-lazy-fetch` capability; an unsupported
Git fails on its first command before source traversal. The environment variable
alone is insufficient on older Git versions. `GIT_ALLOW_PROTOCOL=''` rejects
all transports even when repository `protocol.<name>.allow` overrides the
default `protocol.allow=never`. Both boundaries are required for partial clones
with missing promisor objects.

Git LFS pointers are unsupported. Current and legacy pointer candidates, plus
conservative malformed/BOM/whitespace variants, are rejected from a bounded
4,096-byte prefix. A `version` candidate naming git-lfs, hawser or git-media,
or carrying `oid sha256:`, and a leading `oid sha256:` candidate cannot stand in
for expanded bytes. This conservative rule can reject an ordinary text blob
that resembles a pointer. It is not an LFS payload resolver. Valid LFS v1
pointers are smaller than 1,024 bytes; no network payload fetch is attempted.

The Git subprocess protocol follows the official
[git-cat-file documentation](https://git-scm.com/docs/git-cat-file).
Pointer limits follow the upstream
[Git LFS specification](https://github.com/git-lfs/git-lfs/blob/main/docs/spec.md).

## Resource and preservation contract

The existing source policy enforces file count, per-file and aggregate content
bytes, and final canonical snapshot size. Shared blob objects count once for
transport and once per path for the source-content budget. All tree entries,
including directories and repeated subtree appearances, count against the
tree-entry budget. Tree metadata bytes count per traversed appearance.

| Additional Git policy | Default | Meaning |
|---|---:|---|
| `max_tree_entries` | 40,000 | Complete traversal entries, including directories |
| `max_tree_bytes` | 8,000,000 | Aggregate traversed raw tree payload bytes |
| `max_commit_bytes` | 1,000,000 | Origin commit payload before content retrieval |
| `max_git_output_bytes` | 32,000,000 | Cumulative stdout plus stderr for the whole operation |
| `git_timeout_seconds` | 10 | Deadline per child process |
| `operation_timeout_seconds` | 60 | Shared deadline across reads and result construction |

Limits are positive integers, excluding booleans; byte limits are at most
64,000,000, entry counts at most 200,000 and time limits at most 300 seconds.
Metadata-derived sizes and aggregate blob bytes are checked before payload
reads. Nonblocking stdin/stdout/stderr avoid pipe deadlocks. Overflow or timeout
terminates the adapter-owned process group and returns no attestation. These
are input/output/work budgets, not a process-wide peak-memory quota or sandbox.

No command checks out, stages, resets, cleans, commits or updates a ref. Branch,
HEAD, staged/unstaged bytes and unrelated untracked files remain untouched by
the adapter. This is a read-only preservation claim, not isolation from another
host actor concurrently editing the repository. Immutable object verification
prevents silent source substitution during the read.

## Receipt and authority

The canonical policy digest binds the adapter schema/version, Git limits and
existing P3.5a source-policy digest. The complete inventory digest binds every
sorted path, mode, Git blob ID, byte length and content SHA-256. The receipt
separately binds the original Program/repository/requirement/plan identities,
origin commit, origin Git tree, canonical snapshot SHA-256, host binding,
policy, inventory, file count and total source bytes.

Only the result of a trusted live adapter call is attestation evidence at that
boundary. Constructing a DTO, serializing a receipt, or supplying its hash is
not a signature, provenance authentication, PASS evidence or approval. No
receipt loader accepts caller-provided bytes as trusted evidence. Repeating
the call in a fresh process against the same unchanged host binding reproduces
its bytes and hashes; it does not advance durable state.

P3.5b-2 must bind accepted task-owned Safe evidence, trusted tests, independent
PASS review and exact approval to durable ownership/CAS acceptance. P3.5b-3
must add newly owned sandbox materialization and recoverable receipts across
the database/filesystem crash boundary. Source-aware Program dispatch and the
decisive `42 -> 43 -> restart -> 44` fixture remain later integration work.
Evidence-only v1 same-Base handoff is unchanged.

## Qualification record

The dedicated suite uses actual local Git repositories and child processes,
including both object formats, source-preservation comparisons, fresh-process
replay, ordinary/bare/linked layouts, empty/nested trees, modes and raw binary
bytes, identity drift, unsafe trees, missing/corrupt/replaced objects, LFS
candidates and configured resource limits. Fault-injecting Git wrappers are
owned fixtures; they do not execute customer source or call a provider.

Code presence and local tests do not establish hosted qualification or final
independent acceptance. Exact Base/head/tree, changed-file evidence, current
CI/Live outcomes and review dispositions are recorded in the publishing PR
and maintained continuation references. Overlapping suite counts are not
added together as unique coverage.

Initial CI423 exposed a race in the new descendant-termination fixture: Python
3.11 observed `/proc` state `R` immediately after the adapter sent SIGKILL.
Signal generation is not synchronous process reaping. The fixture now requires
actual termination within a fixed observation interval through the EOF of an
exclusively child-held liveness pipe, and includes a mutation control suppressing
group signaling, which must observe the still-live child. This also avoids
false success when the host's `/proc` mount uses a different PID namespace.
It also cleans up that deliberately surviving owned fixture. No production
deadline, termination action, workflow or acceptance assertion was weakened.
The failed initial head remains historical evidence; a source repair requires
normal qualification of its new head rather than retrying until green.

The independent reviewer also identified a blocking initial lazy-fetch gap:
older Git versions ignore the environment-only lazy-fetch switch, and per-
protocol repository configuration can override a default protocol policy. The
explicit capability and deny-all transport environment above repair that gap.
The qualification suite must prove missing-promisor rejection without source
or transport side effects and unsupported-capability rejection before reads.
