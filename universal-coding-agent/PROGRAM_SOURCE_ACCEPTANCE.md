# Program source acceptance — P3.5b-2

Implementation starts from actual PR21 merge
`b8df8b10030d528855e72dae9c2533bd77a922f6`, tree
`5964944de12eba3ef255f5dea95d54ebff8dfd14`, on
`feature/universal-coding-agent-structured-edits`. Its ordered parents are
`204d3e39543aab442c05ce9605b407af7f29ea07` and
`0fdfa4f8b38cb6bb434499382940433eb38ffacb`.

This document records the implemented bounded adapter contract. Current
qualification, exact candidate identities and independent acceptance are recorded
in the publishing PR and maintained continuation references. Code presence alone
is not qualification. The adapter is an explicit host API; no dispatcher invokes it.

## Scope and trust

The slice connects complete Git-source attestation, an actual persisted Safe
execution, and durable acceptance of one immutable P3.5a source transition.
It does not create a sandbox, execute another phase, publish source, remove
the evidence-only v1 same-Base guard, or implement an automatic Program loop.

Only the trusted host constructs the service with its existing Program,
control, lifecycle, Safe-checkpoint and artifact stores, repository binding,
and trusted test policy. A model or uploaded document cannot supply those
authorities. Public methods accept identities and exact approvals, not a
caller-authored Safe result, review, source DTO or collection of evidence hashes.
The trusted host and executable remain outside the adversarial boundary;
there is no signing claim against an actor that controls the host databases.

The completed Safe checkpoint anchors its exact frozen request, test-result
hash and separately invoked reviewer evidence. Task-owned artifact bytes are
loaded with bounded reads and cross-checked against that checkpoint and each
other. Tests must identify the actual canonical patch before and after their
execution. Reviewer provenance must bind the same patch, tests, context and
review. Legacy results lacking these bindings are rejected for source promotion;
their historical evidence-only v1 behavior remains available.

## Evidence admission

Admission requires all of the following:

- An approved, unchanged Program plan/requirement and exact completed execution
  binding for the requested Program, phase, optional slice, task and thread.
- A completed Safe checkpoint with no pending node/writes, errors, rollback or
  failed task control, whose source/manifest/request identities agree.
- Exact task-owned scope and approval bytes; an approved create/modify path
  set; valid patch evidence; every profile in the bound host test policy
  passing; a separate reviewer-context PASS with no required corrective action;
  and a complete, consistent final report retaining the sandbox patch.
- A complete attestation of the Safe execution's immutable Base, whose entire
  file set, bytes and modes equal the current cumulative snapshot. The execution
  Base and origin commit/tree remain separate identities.
- Deterministic application of the bounded canonical text patch to that snapshot,
  with exact preimages, hunk counts, paths, modes and full Git blob identities.
  Unsupported binary changes, deletes, renames, mode transitions or malformed
  representations reject the operation; unchanged binary files are retained.
- Complete retained worktree bytes and Git executable classifications agree with
  the expected after-snapshot, including unchanged tracked files. Bounded descriptor
  traversal refuses symlinks in every parent and file. Index assume-unchanged or
  skip-worktree flags, disabled filemode tracking and checkout normalization cannot
  hide drift. This reads the existing Safe sandbox and creates nothing.

Promotion-critical final-report fields include task/thread/repository/Base/scope,
the approved edit and patch refs, tests/review/provenance refs and hashes, retained
patch/rollback/error status and publication decision. The actual Program result
and exact phase execution report are also checked and retained. Ancillary index,
implementer-context and diagnostic references do not independently confer source
authority. Their presence is not a claim that every diagnostic was requalified.

Retained Git checks use the same bounded no-lazy-fetch, deny-all-transport runner
as origin attestation. Configured clean/process filters are rejected before status
or diff. Canonical patch sections follow approved manifest order, even if model
edit order differs. Git hunk bytes retain CRLF and no-final-LF semantics.

Hashes authenticate content only relative to these trusted producer/store
bindings. A self-consistent uploaded PASS bundle cannot bootstrap provenance.
Task scope approval, source-transition approval and publication approval remain
distinct. A publication rejection does not become source-transition approval.

## Durable state and ownership

Use the existing Program SQLite database for immutable source artifacts,
prepared candidates, acceptance receipts and one compare-and-swap source head.
Reuse the existing lifecycle Program-worker token. There is no second lease
framework, automatic token recovery, implicit TTL or synthetic Program owner.

The acceptance connection attaches the existing control, lifecycle and Safe
checkpoint databases. A bounded `BEGIN IMMEDIATE` transaction holds their writer
boundaries while checking the owner token, current Program/requirement/plan,
control revisions, execution binding, checkpoint identity, expected generation
and predecessor. Only the Program database receives acceptance writes. Checkpoint
deserialization and Git/artifact reads occur outside this transaction. Exact
serialized checkpoint bytes and database bindings are revalidated at the commit
boundary. Verified artifact bytes are retained in SQLite; the transaction does
not lock their former filesystem paths or claim filesystem atomicity.

The immutable snapshot/transition/evidence bytes, exact approval record and
receipt are committed together with the conditional source-head update. Hash
collisions, conflicting existing artifact bytes, stale candidates, changed
approvals, competing owners and source drift reject the whole promotion.
An explicit replay of the identical accepted operation under current permitted
Program ownership/control returns the same receipt, including concurrent identical
accepts. Another operation or approval cannot inherit it. Paused/cancelled Programs
cannot perform acceptance replay, while `receipt()` remains a historical read.
Read/reload methods never promote state, advance a phase or invoke providers.

The private lifecycle token is checked against the existing row; public candidates
retain only a hash of its binding. A restarted worker must use the established
lifecycle recovery/ownership APIs. Changed ownership or a pause/resume revision
invalidates an unaccepted candidate and requires a fresh prepare/exact approval.

Host API order is `initialize(identity, owner_token=...)`, `prepare(program_id,
task_id, owner_token=..., expected_source_sha256=..., expected_generation=...)`,
then `accept(candidate_sha256, approved_transition_sha256=..., approval_id=...,
owner_token=...)`. Prepare only persists an immutable candidate; its internal pure
snapshot calculation grants no execution or approval authority. `current()` and
`receipt()` read committed state. There is no automatic provider call or filesystem
recovery side effect on service reload.

SQLite acceptance is not a database/filesystem transaction. In this slice all
new accepted payload bytes live in that one database, so no external candidate
directory is execution-ready. Safe artifacts read during admission are retained
as immutable evidence bytes. P3.5b-3 must separately create an owned sandbox and
provide a complete recoverable materialization receipt before any future source-
aware dispatcher can use it.

The concurrency design follows SQLite's documented
[transaction semantics](https://www.sqlite.org/lang_transaction.html) and
[attached-database boundary](https://www.sqlite.org/lang_attach.html).
The attached Safe checkpoint database may use WAL. This slice writes acceptance
to one database and does not claim cross-database WAL atomic commit.

## Required qualification

Use real local Git repositories, the actual Safe graph and fixed local test
processes, existing Program/control/lifecycle services and separate SQLite
connections/processes. Model providers may be deterministic test fixtures;
their use does not turn a manually fabricated Safe result into qualification.

Verify valid admission and exact source bytes; every missing/mismatched artifact;
cross-task/project/request substitution; untrusted or failed profiles; non-PASS
or non-independent review; incomplete reports; stale generation/approval;
cancelled/realigned/paused control; competing tokens and checkpoint drift;
immutable artifact conflicts; exact replay; fresh-process reload; transaction
faults and process death before commit. Preserve original source and existing
v1 handoff/ownership regressions. Counts from overlapping suites are not added.

The later decisive Program fixture remains `42 -> 43 -> restart -> 44`, with
phase B consuming the actual accepted 43 preimage through a qualified owned
materialization and dispatcher. This slice alone cannot establish that fixture
or automatic cumulative-source Program execution.

## Existing follow-ups

PR21's separate audit of `coverage_evidence._run_git` remains tracked. This
slice uses the qualified complete Git-source adapter and does not invoke that
older helper. PR21's optional aggregate-budget request-order instrumentation
and PR20's documented LOW follow-ups remain separate work.
