# P3.5c-2 — Versioned source-aware Program dispatch

Task ID: `UCA-20260907-P35C2-VERSIONED-SOURCE-AWARE-DISPATCH`

Status at implementation submission: bounded v2 code and deterministic actual
42 -> 43 -> fresh-process restart -> 44 qualification are implemented. Independent
review and this candidate's own CI/Live/platform gates remain required. No integration
or automatic Program loop is claimed here. See `P3_5C2_ADMISSION_AND_RECOVERY_CONTRACT.md`.

## Starting point

- Repository: `hesam-hakimi/hugan`.
- Integration target: `feature/universal-coding-agent-structured-edits`.
- Actual PR24 integration: `b0daccdb16bd09898b06ed56bff787008a31a145`.
- Integrated tree: `a21c01b85e766a6d0f427e4b46dbb1b5f2de1bfd`.
- Ordered parents: `2da3d9f8a9376233c968ec539fc7fee260a1d8b2`, then `9d88070d2c3d5d34f42e593fddc5fcfc3643ee0f`.
- Independent report: `../reviews/PR24_INDEPENDENT_REVIEW_2026-09-07.md`.
- Inherited bounded contract: `P3_5C_EXECUTION_BASE_CONTRACT.md`.
- Parent acceptance task: `P3_5C_EXPLICIT_SOURCE_AWARE_EXECUTION_TASK_2026-09-07.md`.

Existing bounded engineering authorization persists. A separate independent
review has now been explicitly requested for PR24; never treat that technical
verdict as human GitHub APPROVE or permission to bypass platform gates.

## Concrete integration gap

P3.5c-1 prepares an exact private Git Base containing the current accepted source,
but binds its receipt to a pending target phase with no execution. The legacy
Program method starts that phase before inserting the execution binding. Calling
the preparation verifier after this state change will correctly reject it.
Define an explicit consumed admission; do not loosen the preparation verifier.

The actual `DiscoveredSafeAgentService.start` currently allocates a discovery
clone and then calls Safe to allocate another clone. `SafeModeGraph.prepare_sandbox`
uses the legacy Git manager. `capture_safe_source_evidence` requires the canonical
host task directory and the original repository URL. Passing a local derived Git
path as a substitute repository URL would lose origin identity; allowing arbitrary
sandbox paths would weaken evidence admission. Implement a versioned trusted
execution adapter and stored admission instead of either shortcut.

## Required boundaries

1. Map the complete actual Program/Safe/discovery/evidence/capture/control callers
   and tests. Admit only an approved unsliced linear plan with the exact current
   accepted predecessor. Keep the first phase on its actual original Base.
2. Atomically consume a current complete P3.5c-1 receipt under the existing worker,
   requirement/plan, Program/control revision and source-generation authority.
   Bind Program/phase/task/thread, preparation and acceptance receipts, destination
   identity, origin Git and derived Git in a distinct immutable v2 admission.
   Insert the execution and change phase state in the same applicable transaction.
   Do not invoke providers inside a database write transaction.
3. Model the gap between committed dispatch intent and the actual Safe checkpoint.
   Status/reload remains read-only and makes no provider call. Explicit replay may
   reconcile only proven matching task/thread/checkpoint state. An ambiguous
   started provider/discovery operation is not automatically repeated or adopted.
   Reuse existing worker/lifecycle ownership, not a new unrelated lease or TTL.
4. Wire actual discovery to the proven owned Base containing 43. Validate its full
   source and Git identity before provider work and the read-only result after
   discovery. Freeze a new exact manifest and reach actual Safe scope approval
   before any edit. Preserve the immutable accepted materialization throughout.
5. The Safe sandbox adapter must derive the destination only from the stored
   admitted execution. It must keep the original repository identity separate
   from the derived commit/tree and validate every task/thread/host association.
   Resume must use this same explicit versioned binding. Caller-supplied paths,
   copied receipt DTOs or arbitrary `SandboxInfo` values are not authority.
6. Add a separately versioned dependency-evidence path. Leave legacy
   `_prepare_accepted_evidence()` and its same-Base guard intact. Prior-phase
   artifacts can supply context only after their exact requirement, dependency,
   acceptance lineage and current source are validated for the new execution.
   Never relabel v1 evidence as proof that source changed between phases.
   Source-aware admission v2 is distinct from the existing v2-line-addressed edit
   protocol; its environment setting is not execution or source authority.
7. Capture real Safe checkpoint, exact patch, all host test profiles, review inputs
   and provenance, scope decision and retained source using the stored v2
   admission. Preserve original repository URL and source generation. Test/review
   failure, rejected approval and rollback must preserve the prior accepted head.
   Exact transition approval remains distinct from scope and execution admission.
8. Revalidate owner/control/source CAS at dispatch, resume, result capture and
   next-generation acceptance. Cancellation, pause/resume revision drift,
   realignment, source drift, simultaneous duplicate calls or wrong host must not
   advance a phase or accepted source through stale admission.
9. Update capability reporting only after the actual v2 path qualifies. Distinguish
   explicit source-aware progression from automatic Program execution. V1 reports
   keep their existing meanings and values. No automatic Program loop is in scope.

## Actual decisive fixture

Use real local Git, the actual Program/acceptance/materialization/execution Base
and discovered Safe services with deterministic test providers and real subprocess
tests. Do not fabricate a final checkpoint, PASS bundle, source snapshot or phase
result to replace the boundary being tested.

- Phase A reads original 42, obtains actual scope approval, edits to 43, passes
  the required tests/review, receives exact transition approval and commits the
  actual next accepted generation. Prepare the independently verified Base.
- Terminate the process and reopen the stores in a genuinely fresh process.
  Status alone performs no recovery or provider work. Explicit continuation under
  current ownership loads and verifies the accepted 43 and its execution admission.
- Phase B discovery and execution must actually read 43; the fixture must fail if
  it sees 42. Obtain its new exact scope approval and produce tested/reviewed 44.
  Capture real evidence, approve the exact transition and accept the next source
  generation with complete 42/43/44 lineage and distinct origin/derived identities.
- Preserve binary/executable/empty files, CRLF/no-final-newline bytes and the
  original source. A failed later phase rolls back only its owned execution to
  the verified derived Base and leaves accepted source/materialization intact.
- Cover missing/stale/forged receipts and Base identities; wrong host/owner;
  corrupt, extra or substituted files/metadata; approval rejection; failed tests
  or review; cancellation and CAS drift; independent-connection duplicate calls;
  and real process death at each database/discovery/approval/Safe/capture handoff.
  Prove no duplicate side effects or automatic provider invocation on reload.

## Qualification and completion

Publish a bounded Draft PR and qualify its own exact source through normal CI
and Live. Historical PR24 checks do not qualify changed successor bytes. Keep
existing gates/assertions and historical failures. Diagnose a concrete failure
before any paid retry; do not turn ordinary pending checks into retry requests.
Obtain a separate independent correctness/security report, then freshly verify
identities and platform gates for already-authorized normal Ready and
expected-head-locked integration. Verify the actual merge before any successor.

Keep continuation references and the observed byte-readback receipt current.
Exclude main, PR6, root todos.md, AskTD/ETL/customer code or environments,
credentials, deployment, history rewriting and generated-source publication.
No background monitor or asynchronous continuation is promised.
