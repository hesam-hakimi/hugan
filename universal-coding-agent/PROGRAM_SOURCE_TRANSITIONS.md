# Program source transitions — P3.5a

## Accepted direction and bounded scope

On September 7, 2026, the owner approved prioritizing cumulative source continuity and
Program resumability before additional-language analysis. PR #19 was integrated into
`feature/universal-coding-agent-structured-edits` as
`d6b346716f1db7d5241145b584899de68ab28c52`, retaining source tree
`721b6d62cbd896fd60789843d6532f190d508812`.

P3.5a supplies a pure, provider-neutral contract for content-bearing source transitions.
It is the first bounded slice toward that direction, not completion of cross-phase
execution. `ProgramSourceTransitionService` is available through the Product lazy exports.
It does not modify `ProgramOrchestrator`, `ProductWorkspace` dispatch, existing evidence
bundles, trusted test profiles, Python/ECMAScript analysis, or HTTP/UI behavior.

## Why a separate contract

Existing accepted phase handoff carries validated evidence, not earlier sandbox patches.
`ProgramOrchestrator._prepare_accepted_evidence` requires those records to share one immutable
Base SHA. That guardrail remains unchanged. A content-bearing source handoff must not be
implemented by dropping the Base check or treating a phase summary as patched source.

The new service computes an immutable in-memory file table from another exact file table.
A trusted future adapter must separately attest the initial Git source and accepted Safe
outcomes, persist accepted transitions, and connect them to an isolated checkout. None of
those side effects or attestations is invented by this foundation.

## Identity and data contracts

`ProgramSourceIdentity` binds the program ID, an opaque repository identity SHA-256,
requirement and Program-plan SHA-256 values, and the original immutable Git Base and tree.
The trusted host supplies and verifies these identities. This service does not contact Git
or prove that supplied initial bytes match a live repository. Original Git anchors remain
unchanged when the cumulative file table advances.

`ProgramSourceSnapshot` contains a frozen tuple of ordered `ProgramSourceFile` entries,
a generation number, and the immediate predecessor snapshot digest. Every entry contains
actual immutable bytes and a regular-file Git mode (`100644` or `100755`). Binary bytes and
line endings are preserved exactly. The snapshot SHA-256 is a canonical artifact digest;
it is **not** a Git tree SHA, commit SHA, signature, or independent attestation.

`ProgramSourceEdit` expresses an exact path, expected preimage fingerprint, and replacement
file or deletion. A fingerprint includes file mode and raw bytes. Creation requires absence;
modification/deletion requires the exact present fingerprint. Rename is an explicit deletion
and creation, not a fuzzy rename detector. Duplicate edits, no-op edits, and mismatched
replacement paths are rejected.

`ProgramSourceTransition` binds before/after snapshot hashes, the complete policy hash,
phase/task/optional-slice identities, an exact path allowlist, ordered qualification-evidence
hashes, and the full edits. Evidence hashes are opaque bindings: a supplied hash does not
prove a PASS review, trusted test execution, acceptance, or permission. The future trusted
adapter must verify the actual referenced evidence before obtaining a materialization
approval. A caller-controlled digest is not a cryptographic signature.

## Prepare, approve, materialize

1. The trusted host obtains and attests a complete, bounded initial source file table.
2. `prepare` verifies the explicitly expected source digest, exact edit scope and preimages,
   computes the candidate cumulative table, and binds its digest into the transition.
3. The host presents the exact transition for a separate approval decision. The approved
   transition SHA-256 must come from the trusted caller, never repository text or model output.
4. `materialize` rechecks approval, policy, predecessor, preimages, and resulting digest. It
   returns an immutable snapshot with actual bytes. It does **not** create a filesystem tree.
5. A later transition uses that returned snapshot and its exact digest. Applying an old
   transition to the newer snapshot is rejected; repeating it against the original snapshot
   reproduces the same result without side effects.

Inputs are not modified on success or failure. A complete candidate is validated before it
is returned. This is pure all-or-nothing computation, not an atomic persistent-state update.
The host must retain the transition, approval, and source artifacts together; identical
content results can legitimately be bound to different approved execution identities.

## Serialization, bounds, and restart

Snapshot and transition encodings use distinct v1 schema tags, canonical sorted compact
ASCII JSON, and canonical base64 for source bytes. Loads verify the expected SHA-256 and
artifact byte limit before JSON interpretation, reject duplicate or unknown fields, enforce
sequence and file bounds, and require byte-for-byte canonical re-encoding. Invalid UTF-8,
JSON, base64, schema, identities, generations, or changed policy fail closed.

Default limits are 20,000 files, 1,000 edits/allowed paths, 1 MB per file, 16 MB total source
bytes, and 24 MB per serialized artifact. All policy limits are positive bounded integers,
not booleans, and participate in the policy digest. Generations are capped at 10,000, evidence
bindings at 32, path length at 1,024 characters, component length at 255, and path depth at 64.
Exhaustion fails rather than returning a partial snapshot. The complete supplied file table,
including unchanged content and modes, is retained unless an explicit edit changes it.

Supported paths are a conservative ASCII portable subset. Absolute paths, traversal,
backslashes, empty/dot segments, control characters, spaces, trailing dots, `.git` components,
Windows device names, case-insensitive collisions, inconsistent directory spelling, and
file/directory conflicts are rejected. Symlinks and Git submodules are unsupported. A future
adapter must reject an unsupported repository rather than silently omit such files. These
constraints are not a claim of complete filesystem or Git filename equivalence.

Reinstantiating the service has no startup side effects. A newly started Python process can
load the exact snapshot/transition bytes and the trusted approval digest and reproduce the
same next snapshot. This proves serialization replay, **not** a durable Program checkpoint,
automatic retry, a filesystem recovery transaction, or resumable provider work.

## Deterministic qualification

Run from a normal complete UCA checkout with the existing development dependencies:

```bash
set -Eeuo pipefail
python -m compileall -q src tests
python -m pytest -q tests/test_program_source_transitions.py
python -m pytest -q
ruff check .
git diff --check
echo "PROGRAM_SOURCE_TRANSITION_FOUNDATION_PASS"
```

The focused tests cover cumulative byte changes, creation/modification/deletion/explicit
rename and modes, immutable original input, exact scope and preimages, identity/approval/
policy/result drift, portable-path conflicts, all configured bound types, malformed and
noncanonical serialized evidence, process-restart replay, duplicate application, and lazy
Product export. Tests use deterministic fixtures and do not call a model or publish source.

An isolated-module local run is not qualification of the complete repository. Exact-head
hosted CI, existing live integration checks where triggered, and independent review must be
recorded separately. No gate or aggregator may be weakened to obtain a green result.

## Next bounded integration and remaining gaps

P3.5b must attest the full Git tree/file/mode set, accepted task-owned patch, trusted tests,
independent PASS review, actual current snapshot, and source scope before accepting a source
transition. It must store the evidence and approval immutably, use compare-and-swap durable
state and existing lifecycle ownership, and materialize only into a verified owned sandbox.
Keep original Base, cumulative content digest, and any derived sandbox Git revision distinct.
Provide crash/replay and stale-approval tests; do not overwrite unrelated owner work.

Only after that contract is qualified should Program dispatch consume cumulative source.
Preserve the evidence-only v1 chain; use an explicitly versioned source-aware handoff rather
than weakening its same-Base invariant. DAG gates, bounded retry/replan, long-running Program
recovery, and the actual independent execution loop remain subsequent work.

The AskTD pilot remains read-only until its actual Base, architecture/ADRs, accepted business
context, and environment access are reconciled. The existing UCA source-transition foundation
alone does not discover business truth, execute AskTD tests, change Azure/Databricks resources,
or authorize customer deployment. PR #6 and unrelated root `todos.md`/ETL work remain protected.
