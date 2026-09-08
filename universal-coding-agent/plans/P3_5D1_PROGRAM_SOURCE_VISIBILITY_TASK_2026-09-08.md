# P3.5d-1 — Recorded Program source visibility

Task ID: `UCA-20260908-P35D1-PROGRAM-SOURCE-VISIBILITY`

Status: bounded successor defined before implementation. Source qualification and
independent acceptance must be recorded separately when they actually occur.

## Accepted starting point

Repository: `hesam-hakimi/hugan`. Integration target:
`feature/universal-coding-agent-structured-edits` at actual PR25 merge
`5d1bb45c28689131b9b538e798d3b8e7aa25742c`, tree
`2433238df764274bcf5ba6cc1639913b496fd3e6`. Ordered parents are
`b0daccdb16bd09898b06ed56bff787008a31a145` and
`aabc8d2c06d54978363d43f69d6e00d0b481e7c2`.

PR25's bounded correction review passed. The exact final report is
`../reviews/PR25_INDEPENDENT_CORRECTION_REVIEW_2026-09-08.md`, SHA-256
`ee5f278bc6e8a44e9fbad5c08782c49da825cae02c54e01532370a8aeb1ee737`.
The original BLOCKED report is preserved separately. CI433 and Live184 attempt 1
qualify PR25's tree; they cannot qualify changed successor source. C2's submitted
pending-gate wording is completed history, not a reason to reopen its acceptance.

## Concrete product gap and selection

The accepted c2 Python service implements explicit cumulative execution and real
42 -> 43 -> fresh-process restart -> 44. ProductWorkspace and ProductWebRuntime
still expose v1 start/continue; the React Program panel has no accepted-source or
v2-dispatch representation. A completed phase can therefore be mistaken for an
accepted source generation, and the existing continuation controls do not explain
why an admitted v2 task cannot use their v1 request.

The web worker reserves and releases a Program worker for each explicit request.
C2 admission/materialization receipts bind the exact existing ownership row.
Changing tokens between requests invalidates that authority. This task must not
bridge the mismatch by accepting a new token, copying private ownership into the
browser, relaxing c2 validation, retaining a worker indefinitely, or inferring
crash recovery. Effectful Product continuation needs a later explicit contract.

The next bounded deliverable is read-only product visibility, plus rejection of
misrouted legacy execution requests. It advances the existing Milestone 3
resumability and Milestone 5 task/evidence visibility work without an automatic
execution loop or a new lease scheme.

## Implementation boundary

1. Add a bounded, provider-free projection of the existing Program source records.
   Use only the already-existing programs database and a consistent read-only
   transaction. Do not construct acceptance, preparation, dispatch, Safe, Git or
   provider services while reading. No schema migration, source snapshot loading,
   source-file inspection, artifact-file write or recovery belongs to this read.
2. Show separately the recorded origin Git commit/tree, accepted source generation
   and SHA-256 lineage, and each stored v2 execution's derived Git commit/tree and
   durable dispatch state. Hash-verify the bounded metadata receipts and their
   stored relational bindings before presenting them. Do not claim live filesystem,
   current ownership, provider outcome or full source-byte requalification.
3. Project an explicit allowlist. Exclude tokens, invocation capabilities/digests,
   filesystem locations, repository URLs, raw source, complete task payloads and
   private binding records. Bound row count, field lengths, JSON bytes, aggregate
   bytes and database work before materializing untrusted persisted content.
   Reject incomplete/corrupt metadata with a stable error; never silently label it
   a legacy Program or return an apparently complete partial lineage.
4. Expose the projection in the existing execution-status API and React Program
   view. Loading and refreshing remain explicit reads. Label recorded state as
   historical evidence; current authority is checked only by an effectful service.
   A later phase's completed execution and its separate source acceptance remain
   distinct. Preserve all v1 API fields and their meaning.
5. Hide/disable v1 continuation for a registered v2 execution and v1 start-next
   after accepted cumulative source has advanced. Reject the corresponding legacy
   runtime requests before provider work, and recheck at the worker boundary under
   its existing ownership. Do not release or replace another worker's ownership.
   Keep v1 first-phase execution and v1-only Programs working.
6. Do not modify the accepted c2 engine, preparation verifier, same-Base v1 evidence,
   stored approvals, lifecycle recovery semantics, workflow gates or test profiles.

Allowed implementation paths: one new product source-status module; the existing
web runtime, React App/types/viewModels and their focused tests; one new Python
status/API integration test module; bounded documentation and retained PR25 reports.
No new dependencies, automatic polling, CLI execution command, effectful v2 HTTP
action, provider transport, language expansion, publication or deployment.

## Decisive validation

Use the existing actual cumulative fixture with deterministic providers and real
Git/Program/Safe/test/review/acceptance. Inspect generation 0, accepted 43, admitted
and scope-stopped 44 work, terminal-but-not-accepted 44, then accepted generation 2.
Verify receipt lineage and distinct origin/derived identities at every stage.
Reopen a fresh process and read without constructing effectful source services;
provider logs, source bytes, artifacts and database logical state must not change.

Cover v1-only databases with no source tables, unrelated Programs, absent/corrupt/
oversized metadata, wrong Program/task/receipt/source linkage, noncontiguous
generations, unexpected dispatch states, and read bounds. Exercise actual HTTP
and runtime guards, including revalidation after worker ownership is acquired.
Confirm browser rendering/control selection and preserve existing v1 tests.

Run focused deterministic checks and required CI/Live on the changed exact tree.
Do not manually rerun paid Live or repeat accepted suites merely for freshness.
Keep failures and source-specific evidence. Independent technical review and
normal platform gates remain required before Ready and expected-head-locked
integration. A self-review is not independent acceptance. Verify actual merge
tree/parents/ref before a later successor.

## Continuity and exclusions

Existing bounded autonomous engineering authorization persists. This definition
does not broaden platform or reviewer permissions. Preserve the canonical current
references and observed synchronization receipt. Retain PR25's initial failures,
bounded final-review limitations, v1 standard Live capability values and all open
nonblocking follow-ups, including the separate legacy Git helper audit.

Exclude main, PR6, root todos.md, AskTD/ETL/customer work, credentials, deployment,
history rewriting and generated-source publication. No background work is claimed.

## Bounded correction after initial independent BLOCKED review

The owner authorized correction and independent follow-up. Preserve the exact
initial report `../reviews/PR26_INDEPENDENT_INITIAL_REVIEW_2026-09-08.md` and its
separately retained reproduction/evidence archive. Correct only F1 (recorded
execution/dispatch-state coherence) and F2 (missing combined preparation/admission
must not classify a surviving derived execution as v1), plus focused regressions
and the nonblocking existing-polling wording clarification. Do not reopen c2.

Independent follow-up must use its own exact corrected checkout and inspect the
complete parent-to-correction delta with relevant consumers. Recheck both original
observations within the same bounded metadata-reader scope and run relevant existing
regressions. Preserve original failures even if corrected. A separate report must
state the exact inspected head/tree, commands/results, findings and limits; no
whole-repository audit or unperformed test is implied. Source and external state
remain read-only for the reviewer; any tool rejection must be honored.

Normal current-tree CI/Web/Live, independent acceptance, normal Ready and expected-
head-locked integration remain gates. Verify actual integration tree, ordered
parents and target ref before closing this phase. No manual paid Live retry.
