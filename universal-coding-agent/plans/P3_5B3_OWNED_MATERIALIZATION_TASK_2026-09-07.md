# P3.5b-3 — Owned source materialization and explicit recovery

Task ID: UCA-20260907-P35B3-OWNED-MATERIALIZATION
Status: instantiated bounded implementation task; no P3.5b-3 implementation or qualification is claimed.

## Verified starting source

- Repository: hesam-hakimi/hugan.
- Integration target: feature/universal-coding-agent-structured-edits.
- Actual PR22 merge: cd08bf64832dd4cc8c66bd267cb6abf245a325e9.
- Base tree: e1689ca818bca3439e53118dab36df8fad68066e.
- Ordered merge parents: b8df8b10030d528855e72dae9c2533bd77a922f6, then
  3bf783792f7684348a1c738fd50de6462c160e70.
- Successor branch: feature/universal-coding-agent-source-materialization.
- PR22 was merged normally at 2026-09-07T15:27:10Z after independent technical
  PASS and current-source CI426/Live177 attempt1 qualification. All three jobs
  literally checked out ad095975833d4647f3cb161bae15d4c7bc204e7e, with the exact
  same tree; that preview is neither the PR head nor the actual merge.
- The PR22 independent report is preserved at
  ../reviews/PR22_INDEPENDENT_REVIEW_2026-09-07.md and in PR22 comment 5572777881.
  Report SHA-256: 6d30fc4d4660dffeb6e3277f83c6122fb3011a82759ad6614aec96a92a3d3440.

Owner authorization for bounded autonomous engineering, the source-continuity
priority and normal Ready/head-locked integration already exists. Do not ask for
it again. Preserve independent review and actual platform gates.

## Concrete problem and product boundary

P3.5b-2 commits an authenticated accepted snapshot and its exact evidence,
transition, approval and receipt into the existing Program database. It does not
create an execution-ready directory. P3.5b-3 must produce a complete private
UCA-owned sandbox from that accepted state with a reloadable completion receipt.

This task implements only materialization and explicit recovery. Do not add an
automatic Program loop, provider calls on reload, phase advancement, source-aware
dispatch, publication, or a bypass of the v1 same-Base evidence handoff.

## Existing APIs to inspect and reuse

Read these complete modules and their relevant callers/tests before freezing
implementation names or public signatures:

- product/program_source_acceptance.py: existing one-database immutable artifacts,
  source head, exact acceptance receipt, lifecycle owner binding and transaction.
- product/program_source_attestation.py and program_source_transitions.py: complete
  bounded bytes, modes, portable paths, distinct origin/execution/source identities.
- product/lifecycle_reservations.py and Program/control integration: current owner
  token, conflicts, revisions and explicit recovery; do not create a second lease.
- sandbox/git.py and core/models.py: the established UCA state-root layout and
  SandboxInfo boundary. Existing prepare() clones/fetches the original repository;
  it cannot substitute for accepted-snapshot materialization.
- Existing Safe checkpoint, artifact and Program execution consumers: this slice
  must not accidentally expose a prepared or partial directory as usable.

The existing sandbox path helper uses resolve/containment checks. A one-time
containment check does not provide the race-safe allocation/write boundary this
task requires. Inspect the platform primitives and fail closed if they cannot
enforce ownership and no-follow traversal.

## Required contract

1. Accept only a verified P3.5b-2 acceptance and matching immutable snapshot from
   the trusted existing stores. Bind repository, Program, requirement/plan,
   accepted generation/source/receipt, host policy and current private worker
   ownership. Reject caller-supplied snapshots, PASS bundles and arbitrary paths.
2. Allocate a new private directory under the established UCA-owned sandbox root.
   The caller does not choose a filesystem destination. Refuse reused names,
   unowned/preexisting destinations, links and substituted roots/parents. Use
   descriptor-based no-follow operations and exclusive creation across allocation,
   staging, verification and final exposure; do not rely on normalize-then-write.
3. Write every accepted file as exact raw bytes with its supported Git mode.
   Include unchanged binary and executable files. Preserve CRLF/no-final-LF and
   portable-path limits. Bound file count, bytes, metadata and operation time.
   Do not fetch origin, apply checkout filters, run repository hooks or execute
   customer/project code while materializing.
4. Verify the entire written tree and ownership before exposing completion.
   Keep origin commit/tree, cumulative source SHA-256 and any derived sandbox Git
   tree/commit distinct. If a derived Git revision is necessary, construct and
   verify it only inside the owned directory with the hardened no-fetch/no-helper
   runner. It confers no upstream relationship or publication approval.
5. Persist a recoverable state machine in the existing Program store. Proposed
   states are allocated/staging/verified/complete/abandoned; freeze exact names
   only after mapping existing APIs. A recorded accepted transition is not a
   complete materialization. A prepared/partial/stale directory must never be
   returned as dispatchable.
6. Treat database acceptance and filesystem writes as separate crash boundaries.
   Record an owner-bound operation identity before writes. Sync/verify durable
   bytes and ownership markers before the final database completion. If the
   filesystem becomes complete before its receipt commits, explicit recovery
   must verify and reconcile it idempotently. If a completion receipt exists,
   subsequent use must reject changed/missing bytes, root identity or lineage.
   Do not describe a database transaction plus rename as cross-system atomicity.
7. Revalidate exact lifecycle ownership, Program/control revisions and current
   accepted predecessor/generation at every irreversible completion boundary.
   Pause/cancel/realign, ownership change, competing recovery or CAS drift must
   block completion without destroying the last usable state.
8. Read/startup/reload operations only report state. Reconciliation is explicit,
   bounded and owner-bound; identical permitted replay returns the same receipt.
   Cleanup touches only demonstrably owned staging contents, with the same
   descriptor/identity checks. Do not broad-reset, clean or delete owner work.

Trust remains anchored in the trusted host and executable. Hashes are content
bindings, not signatures against a compromised host. Scope approval, transition
approval, materialization completion and publication authorization are distinct.

## Decisive qualification for this slice

Use actual Git/Program/Safe/acceptance services and real filesystem/process
fixtures, with deterministic providers where needed. Do not fabricate accepted
DTOs as a replacement for actual P3.5b-2 admission.

- Exact complete materialization after an actual accepted 42-to-43 transition;
  unchanged binary/modes/line endings and original repository state preserved.
- Wrong owner/receipt/host/Program, stale generation/control and arbitrary or
  preexisting destination rejection; symlink/root/parent substitution races.
- Partial write, ENOSPC or injected write/fsync/rename/database failure; process
  death at each database/filesystem handoff and fresh-process read-only reload.
- Explicit reconciliation from each incomplete state, concurrent exact replay,
  competing owners and cleanup boundaries. The last completed sandbox stays usable.
- Complete-tree drift after staging and after receipt, missing files, extra
  files, altered modes and equal-length hidden-byte corruption reject use.
- No provider calls, implicit approval or phase advancement on any read/reload.
  Preserve current v1 and lifecycle regressions and unchanged qualification gates.

The later source-aware dispatcher must separately pass 42 -> 43 -> restart -> 44:
dependent phase B must consume the actual accepted/materialized 43 preimage in a
new process and produce 44 with exact lineage, approvals and tested/reviewed output.
A P3.5b-3 materializer test alone must not be relabeled that Program qualification.

## Review, publication and stopping conditions

Keep source changes within UCA and add a bounded contract plus actual negative,
concurrency and crash tests. Publish a Draft PR from this successor branch only
when its candidate is concrete. Qualify its exact current source through normal
CI/Live, obtain a separate independent correctness/security report, and preserve
normal platform gates. An agent PASS is not human GitHub APPROVE.

On failure, diagnose the concrete source or environment issue before another
paid run. Never replace old failing evidence, lower assertions or claim that
successful PR22 checks qualify a changed successor tree. Revalidate live
head/tree/target/check/review state before authorized Ready/head-locked merge;
verify actual merge parents/tree/ref before any subsequent slice.

Exclude main, PR6, root todos.md, AskTD/ETL/customer source, credentials, customer
environments/deployments, history rewriting and fabricated upstreams.
Keep repository documentation and current continuation references accurate and
read back persistent updates. No asynchronous work or future monitoring is
promised by this task record.
