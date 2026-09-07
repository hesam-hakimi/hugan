# P3.5c — Explicit source-aware Program execution

Task ID: UCA-20260907-P35C-EXPLICIT-SOURCE-AWARE-EXECUTION
Status: parent integration task remains open. P3.5c-1 execution Base preparation
and recovery is an implementation candidate, with its actual boundary recorded
in P3_5C_EXECUTION_BASE_CONTRACT.md. Versioned source-aware dispatch and the actual
42 -> 43 -> restart -> 44 acceptance have not been implemented or qualified.
This document grants no Product capability by itself.

## Actual starting source and inherited acceptance

- Repository: hesam-hakimi/hugan.
- Integration target: feature/universal-coding-agent-structured-edits.
- Actual PR23 merge: 2da3d9f8a9376233c968ec539fc7fee260a1d8b2.
- Merge time: 2026-09-07T17:32:18Z.
- Base tree: 325f8160cf85b7ceafcc23dc8a17d47a57202986.
- Ordered merge parents: cd08bf64832dd4cc8c66bd267cb6abf245a325e9, then
  c8e8838a7c0b437a259eb306741636e6ee6452bc.
- Successor branch: feature/universal-coding-agent-source-aware-execution.
- PR23 independent correctness/security PASS:
  ../reviews/PR23_INDEPENDENT_REVIEW_2026-09-07.md;
  author-side recording in PR23 comment 5573972182. This is an independent agent
  report, not a submitted human GitHub APPROVE.
- CI428/run34146958823 and Live179/run34146958346 attempt1 qualified preview
  11eedb7d095a957e0e913dceaa8e4cc1a8dadb4e with this exact tree. The preview is
  neither the actual merge nor PR head. No changed successor code is qualified
  merely because those results passed.

Bounded autonomous engineering, source-continuity priority and normal Ready plus
expected-head-locked integration are already authorized. Preserve independent
technical acceptance and actual platform gates; do not request owner approval
again for this existing scope.

## Concrete product gap

P3.5b-1 attests complete local Git source; P3.5b-2 authenticates actual Safe output
and commits accepted cumulative source; P3.5b-3 creates a verified owned source
directory with explicit recovery. Program still drives v1 executions from a
single immutable Base and compiles prior-phase evidence. It does not execute the
next phase from accepted cumulative source.

Implement the first explicit, versioned, sequential source-aware Program path.
The caller explicitly requests each execution and each required approval. Bound
initial admission to an unambiguous linear dependency and one execution unit per
phase. Reject unsupported branching, merge conflicts and slicing combinations
before side effects. No automatic Program loop, parallel DAG scheduler, automatic
retry, provider call on reload or publication belongs to this task.

## Required implementation mapping

Read complete modules, callers and tests before freezing API or schema names:

- product/program_orchestrator.py, models.py and handoff_compaction.py: existing
  execution binding, phase lifecycle, v1 accepted evidence and approval rules.
- product/program_source_acceptance.py, program_source_evidence.py and
  program_source_attestation.py: actual checkpoint/report/PASS admission,
  attest_execution_base(), current source CAS and complete byte comparison.
- product/program_source_materialization.py and sandbox/owned_source.py:
  verify_complete(), owner/control/receipt/root bindings, persisted inode proof
  and the database/filesystem crash gaps.
- product/controlled_safe_graph.py, core/models.py, sandbox/git.py and the actual
  discovered Safe execution service: discovery, scope approval, implementation,
  test/review, rollback, sandbox allocation and retained evidence consumers.
- lifecycle_reservations.py and task_control.py: existing worker ownership and
  explicit recovery. Do not introduce an unrelated second lease system.

The first executable action is to map these actual consumers and freeze a short
contract showing the new execution-base admission, durable binding, approval and
recovery boundaries. Then implement that bounded contract with actual fixtures.

## Mandatory source and execution boundary

1. Admit only the actual current acceptance and P3.5b-3 completion from trusted
   stores under the current Program, requirement/plan, host and worker authority.
   Re-run verify_complete() and exact lineage checks at use. Historical status
   or a copied completion receipt alone cannot authorize execution.
2. Preserve the completed materialization directory and its filesystem proof.
   Do not initialize Git, insert metadata or run project commands inside that
   directory: its exact entry and inode proof would be invalidated. Allocate a
   separate exclusive owned execution destination and verify the complete raw
   source transferred into it. Revalidate the source proof after transfer.
3. Construct any required derived Git objects locally from exact accepted bytes,
   using fixed bounded commands with no fetch, lazy fetch, helpers, hooks,
   filters, signing or ambient configuration. No shared mutable object database,
   alternates, grafts, replacements or fabricated origin/upstream. Verify actual
   commit/tree inventory, supported modes and full worktree bytes before use.
4. Keep origin repository URL/identity, origin commit/tree, cumulative source
   SHA-256/generation/receipt and derived execution commit/tree separate. A
   synthetic local commit is an execution identity, never a published upstream
   revision. Any parent relationship must name real verified local objects and
   be explicitly justified; never invent history to satisfy an old API.
5. Persist the exact Program/phase/task, accepted predecessor, materialization,
   execution allocation and derived Base before dispatch. Handle allocation,
   Git construction, database completion and dispatch as separate crash points.
   Reject ambiguous existing destinations. Reconciliation is explicit and
   owner-bound; replay cannot allocate duplicate executions or call a provider.
6. Define a separately versioned source-aware execution/evidence admission. Keep
   the v1 _prepare_accepted_evidence() same-Base guard and existing callers intact.
   Replacing its expected Base with an unrelated commit or relabeling old v1
   evidence as cumulative source is forbidden. Define how dependency evidence,
   current source generation and exact derived Base bind together for v2.
7. Discovery and Safe scope approval must inspect the new actual execution Base.
   No edits occur before its exact manifest/scope approval. Existing transition
   approval remains a distinct acceptance boundary. Revalidate worker ownership,
   Program/control revisions and source generation before dispatch, resume and
   source acceptance. Pause/cancel/realign or concurrent source drift fails closed.
8. Integrate actual Safe results with P3.5b-2 capture rather than fabricating a
   checkpoint, PASS artifact or source snapshot. Its execution Base attestation
   must prove complete files equal the current accepted preimage. Preserve tests,
   reviewer provenance, exact approved transition and durable acceptance lineage.
9. A failed later phase preserves the original repository, accepted source and
   completed materialization. Scope rollback may restore only the owned execution
   destination to its verified derived Base. No broad cleanup/reset of owner work.

## Decisive actual Product fixture

Qualify 42 -> 43 -> restart -> 44 through actual Program and Safe services with
deterministic providers for regression tests. Use a real local Git repository,
approved requirement/plan and two explicitly dependent phases:

- Phase A reads the original 42, obtains actual scope approval, edits to 43,
  passes real subprocess tests and review, then receives exact transition
  approval and durable source acceptance. Materialize and verify its full tree.
- Terminate the process and reconstruct the existing services/stores in a new
  process. Initial status reads neither recover nor invoke a provider. Explicitly
  resume under the permitted current ownership and verify accepted 43.
- Phase B must discover and actually read 43 from the new verified execution
  destination, obtain a new exact scope approval, and produce 44. A test must
  fail if it sees 42; a reported plan or prefilled DTO is insufficient proof.
- Capture actual tested/reviewed Safe output and exact transition approval;
  accept the next generation with the complete 42/43/44 lineage and distinct
  origin/derived Git identities. Preserve unchanged binary/executable/empty files,
  CRLF/no-final-LF and original source throughout.
- Negative fixtures cover stale/missing/mismatched receipt, wrong owner/host,
  corrupt or substituted materialization/destination, current source/control CAS,
  forged derived Base, rejected approval, failed test/review, cancellation,
  process death at each handoff and concurrent duplicate admission. Verify no
  provider invocation on reload and no duplicate side effect on explicit replay.

An execution-base helper passing alone is not this Program acceptance. Update
capability diagnostics only when the actual v2 fixture qualifies; preserve v1
diagnostics in their own schema and explicitly distinguish manual source-aware
progression from automatic execution.

## Completion and exclusions

Publish a concrete Draft PR, qualify its exact current tree through normal CI
and Live and obtain a separate independent correctness/security report. The
review task explicitly authorizes a separate read-only engineering-agent review;
it does not authorize author APPROVE or platform-gate bypass. Do not rerun paid
qualification without diagnosing a concrete failure or a normal changed-source
trigger. Preserve all existing gates, assertions and historical failures.

Freshly revalidate head/tree/target/checks/reviews before authorized Ready and
expected-head-locked merge. Verify actual merge parents/tree/ref before any
successor. Keep repository and canonical continuation documents current and
read back persistent updates. No background work or monitoring is promised.

Exclude main, PR6, root todos.md, AskTD/ETL/customer source, credentials, customer
environments/deployments, history rewriting and publication of generated source.
