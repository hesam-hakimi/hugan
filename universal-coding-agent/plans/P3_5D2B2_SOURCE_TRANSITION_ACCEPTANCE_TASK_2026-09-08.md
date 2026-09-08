# P3.5d-2b-2 — Separate source transition preview and acceptance

## Current implementation candidate

Runtime implementation is present from verified definition commit
`62f988ed85c219715a7d74bbfc75f03c54f3d7a0`. Candidate-2 and receipt-2 have separate
immutable metadata and an acceptance-only transaction policy. The private fresh
worker is committed with its pending request; the final source-head CAS, receipt,
shared/versioned ledger, response and exact release commit together. Interrupted
requests remain ambiguous. No existing live v3 owner is substituted or resumed.

Author qualification and separate independent/platform/integration observations
must bind the exact candidate tree. This candidate's source documentation does
not itself claim those later gates passed. The definition status below records
the prior phase and is superseded by this implementation-candidate block.

Submitted evidence is in `tests/test_program_source_acceptance_v2.py`,
`tests/test_program_source_acceptance_v2_boundaries.py` and
`tests/test_program_source_acceptance_v2_lineage.py` (paths relative to this
project). The executable map is:

| Family | Submitted cases |
|---|---|
| A01 | Real complete journey in both Git formats; separate OS invocations at park/terminal/preview/accept; explicit host composition |
| A02 | Different current-owner witness hashes; no public token; full worker exclusion and private claim binding |
| A03 | Every exact decision argument; request collisions, completed replay and final rejection |
| A04 | Missing v3 requests/receipts/settlement/authority/registry/guards/root/c1 history; complete closed d2a chain |
| A05 | Recaptured actual tests/review/provenance/scope/patch/validation/Program artifacts and retained/origin bytes |
| A06 | Source/control/checkpoint/plan/policy/recovery/owner/inode drift; WAL writers blocked through release and commit; late filesystem drift rolls back |
| A07 | Two OS processes competing for preview, accept/accept, accept/reject and accept/legacy; shared one-task barrier |
| A08 | External SIGKILL across claim, capture, source-head, response, release and commit; new-process exact replay or retained ambiguous owner |
| A09 | Actual rejected scope, failed tests, FAIL/conditional review and rollback; pending writes, workers, handles and remote retention |
| A10 | Independent read-only process, no effectful imports or new stores, unchanged database bytes, historical response after filesystem drift |
| A11 | Actual selected checkpoint bounds before graph decode; metadata depth/duplicates/canonicality/aggregate/history; schema and index attestations; no-follow inventory; lock, Git and cumulative capture limits; authorizer negatives |
| A12 | Old-route denial of candidate-2/receipt-2, inert d2a and preserved existing v1/v2/c1/c2/v3 regression suites |

The shared-read budget exceptions are recorded at the end of this task. They do
not change v3 execution/settlement schemas or expand its write authorizer.

### Initial independent findings and separate correction

Initial candidate `8d72ad67bfa9dc9ebabb656cc298b1b09fa16894` is blocked by
independent observations: a missing completed preview request or response did
not block a fresh decision, and missing receipt-1 transition/checkpoint/original
snapshot artifacts did not block new preview or acceptance. Passing submitted
tests and initial-tree platform runs cannot override these findings.

The correction requires the exact completed preview request, response and
witness before decision claim and at each recapture. Historical decision replay
and recorded status require the same complete preparation; status also requires
every referenced decision request, including rejection. All original receipt-1
artifact links and candidate-2 evidence-core artifacts receive bounded stored-byte
hash checks. Live capture reconstructs the original approved 42-to-43 transition
under the pinned source policy. No historical owner or current capability is
restored. Forty additional submitted cases cover deleted or corrupted links,
pending/owner mismatch, post-capture deletion, accepted/rejected replay and
separate metadata/opaque-artifact read budgets. The initial BLOCKED report remains
separate; correction acceptance and platform gates must name their exact tree.

---

Task ID: `UCA-20260908-P35D2B2-SOURCE-TRANSITION-ACCEPTANCE`

Status: instantiated documentation-only definition; runtime implementation has
not started. This task and its companion contract define the next bounded
engineering phase. D2b-1 is accepted and complete. D2c-1/d2c-2 remain planned,
not instantiated. Definition review is author review of prose, links, scope and
source identity; it is not independent implementation acceptance.

## Starting point and authority

Actual accepted PR28 integration is `95096565d85640ea471182fc0b421e124667b73b`,
tree `26611a055acd80a254cd40c519726e4cad0a85d1`, merged 2026-09-08T15:57:46Z.
Ordered parents: `fdb97d3d10c8a843eae0ab71c255c3ebd0e6ac4a`, then
`1675c2ad1ffa2d324982e4604043bd14e0f27a27`. Preview
`7b86cd520a44c59e8b611f7f29eddb2bf75189d6` is a separate commit with the same tree.
The second correction received separate bounded technical PASS; CI443 and Live194
attempt 1 qualify that exact corrected tree. CI passed 1644 tests per Python leg.
Author 173 v3 + 532 compatibility cases and independent 173 + 291 cases have
different scopes and overlap; do not add them as unique tests. Standard Live
Program remains v1; no cumulative live-model v3 or Product journey is qualified.
Technical PASS is not human GitHub APPROVE or a repository audit.

Repository: `hesam-hakimi/hugan`. Definition branch:
`feature/universal-coding-agent-source-transition-approval`. Integration target
remains `feature/universal-coding-agent-structured-edits`. Start from the actual
PR28 merge, not its preview or a prior candidate. Existing bounded engineering
authority persists without routine owner reconfirmation. Do not repeat completed
PR26/PR27/PR28 gates. This definition phase changes documentation only and opens
no PR, invokes no provider, and runs no runtime/platform qualification.

Read the full current checkpoint/state/master/status, observed receipt and its
external observation, all three PR28 reports, both PR27 reports, the
[d2a task](P3_5D2A_PROGRAM_CONTINUATION_HANDOFF_TASK_2026-09-08.md),
[parent design](P3_5D2_PRODUCT_CONTINUATION_DESIGN_2026-09-08.md),
[delivery matrix](P3_5D2_VALIDATION_AND_DELIVERY_MATRIX_2026-09-08.md),
[c1 contract](P3_5C_EXECUTION_BASE_CONTRACT.md),
[c2 contract](P3_5C2_ADMISSION_AND_RECOVERY_CONTRACT.md),
[d2b-1 task](P3_5D2B1_V3_CONTINUATION_EXECUTION_TASK_2026-09-08.md),
[v3 contract](P3_5D2B1_V3_ADMISSION_AND_QUIESCENCE_CONTRACT.md), and the
[new acceptance contract](P3_5D2B2_EVIDENCE_CORE_AND_ACCEPTANCE_CONTRACT.md). All remain canonical in Git.

PR28's initial BLOCKED and first-correction BLOCKED reports remain unchanged.
Their SHA-256 values are respectively
`17a80dad50553c3e8305bfad119642ce3f20f4637b99b0bcd486e6f0b5cc66df` and
`ac3e3a34d503c0a74a5e343940a4d5214034dba69a56463f47c2b16cf3190204`.
The separate second-correction PASS report has SHA-256
`2e5db5497f515e134a790841d7d2e50867c63a6d5412cec0c5a32189cae1cdbd`.
CI441 failed its child-import harness; Live192 passed only the initial tree.
CI442 passed; Live193 failed the hard CDC fixture (`operation` instead of `op`,
review PASS_WITH_CONDITIONS, rollback). These are not final qualification.
The second-correction review records an automatic content-risk flag followed by
a narrowed read-only/existing-test review; expanded route cases were submitted
tests independently executed, not newly independently designed probes.
PR27's original BLOCKED/correction PASS and WAL-control stale-commit failure,
both PR26 reports, PR25/PR24 failures and legacy Git-helper follow-ups remain history.

## Problem and selected first consumer

PR28 completes a real second phase at tested/reviewed 44 but leaves source at
generation 1 / accepted 43. Its terminal receipt releases the execution worker
and grants no source acceptance. The v1 acceptance candidate includes the entire
temporary owner binding; accepting it with a substituted owner would violate
the accepted contract. D2a metadata does not solve this authority problem.

Add an explicit trusted-host acceptance service for a successfully settled v3
terminal result. It prepares a versioned immutable evidence core, returns a
reviewable candidate, and requires a later exact source-transition decision.
Preview and acceptance reserve separate fresh workers. Approval compares the
recaptured core under current ownership and atomically commits one source
generation, receipt, request response and worker release. Execution approval,
scope approval and source acceptance remain three distinct decisions.

The first consumer is deliberately a two-phase unsliced linear Program:
original 42 -> existing first-phase Safe result 43 -> existing same-owner v1
source acceptance at generation 1 -> accepted c1 preparation and explicit v3
admission in one worker episode -> real scope stop -> clean process restart
and explicit scope decision -> terminal-unaccepted 44 -> new preview -> another
clean process restart -> explicit acceptance at generation 2 / accepted 44.
Keep the original Git source at 42 and accepted generation-1 material at 43.
First-phase candidate-1 creation/acceptance stays within its original worker
episode; cross-owner v1/v2 candidate migration is excluded. New acceptance is
limited to the final v3 unit; no subsequent c1 materialization or third phase is
instantiated from receipt-2 in this slice.

## Allowed implementation surfaces

Paths below are under `src/universal_coding_agent/product/` unless stated.

| Surface | Bounded change |
|---|---|
| New `program_source_acceptance_v2.py` and bounded store/reader companion | Candidate-2 core, preview, decision, receipt-2 and request ledger; exact fresh-owner capture |
| New host orchestration companion | Explicit one-action composition of existing first-phase/c1/v3 calls and new acceptance; no loop or automatic next action |
| `program_continuation_dispatch.py` / `program_continuation_execution_store.py` | At most a strict read-only terminal-proof extraction surface; retain existing execution/settlement authorization and schemas |
| New source-acceptance status reader | Bounded mixed receipt-1/receipt-2 lineage and v3 metadata; explicit entry point, no existing UI/API wiring |
| `program_source_acceptance.py` and routing denial helpers | Only necessary early denial of candidate-2 misuse; do not make old routes accept v3 |
| Existing lifecycle transaction primitives | Reuse reservation/release on the same connection; no owner substitution, TTL or primitive relaxation |
| Focused tests and fixture | Actual 42/43/44 lineage, fresh processes, races, crash boundaries and negative families below |
| Task, contract, parent/matrix/ROADMAP | Bounded status and evidence links |

Reuse pure snapshot/transition and complete Safe evidence verification where
their preconditions are proved. Do not modify c1 pending preparation semantics,
c2 exact-owner semantics, old candidate/approval/receipt schemas, Safe graph
effect boundaries, or d2a flags. A shared ledger insertion of a receipt-2 is
explicitly versioned, not a fake receipt-1; old materialization rejects it.
If implementation discovers a necessary change outside these surfaces, document
the concrete contract conflict before widening the task; no silent scope growth.

## Required evidence families

Every family is required for the future implementation; none is executed by this
definition. Map cases and independent observations to exact source identities.

| ID | Required evidence |
|---|---|
| A01 | Real complete 42 -> 43 -> scope park -> clean restart -> tested/reviewed 44 -> preview -> clean restart -> accepted generation 2; both supported Git object formats |
| A02 | Different preview/acceptance owners; current exact full owner during capture; no token/ticket in public metadata; restart alone gives no authority |
| A03 | Exact candidate/revision/transition/core/predecessor/decision/request binding; duplicate exact response; request-ID/action/payload collisions and changed approval rejected |
| A04 | Actual v3 terminal receipt/settlement/request/registry/root locator/c1 materialization and preparation lineage; missing, corrupt, unknown-schema or partial combined history blocks without v1 fallback |
| A05 | Actual checkpoint, Program result/report, scope, patch, every trusted test profile, separate reviewer provenance and retained source recapture; copied hashes/PASS bundles cannot qualify |
| A06 | Source/control/plan/host/policy/recovery drift before reserve, during capture and through commit; separate WAL control/checkpoint/remote writers excluded until commit |
| A07 | Independent-connection competing preview/accept/reject/old-route requests; one source generation and one task acceptance across shared and versioned ledgers |
| A08 | External process death before/after claim, during capture, before/after acceptance and release/request writes, immediately before/after commit; no partial durable advance; completed exact replay in fresh process |
| A09 | Rejected source decision, rejected scope, failed tests, failed/conditional review, rollback, pending writes, incomplete preparation, remote lease, active handles and ambiguous execution stay unaccepted |
| A10 | Read-only status/request replay produces no stores, schema setup, worker, preview, recovery, providers or capability; historical/current distinction after later drift |
| A11 | Bound real selected SQL bytes/types/IDs, aggregate reads, recursion, row/history counts, locks, Git subprocess output/deadline and no-follow filesystem inventory; oversize/TOCTOU/authorizer/PRAGMA negatives |
| A12 | v1/v2 acceptance and exact-owner behavior, c1 pending proof, d2a inertness, PR26 F1/F2, PR28 root/unknown-source-affinity denial and revocation remain intact; no generated-source publication |

Tests must exercise actual Program/discovery/Safe/Git/subprocess test and reviewer
provenance services with deterministic providers. Hand-built terminal checkpoints
or direct file edits may serve negatives, not the positive journey. Preserve
failed/rejected evidence and exact 42/43/44 bytes and modes. Do not infer cumulative
live-model qualification from standard Live Program v1.

## Future delivery gates and completion

Implementation starts from the verified published definition branch. Review the
complete diff and exact changed bytes, publish the bounded candidate, and use a
normal Draft PR against the unchanged feature integration target. Preserve a
separate independent correctness/security review for the exact candidate tree;
any BLOCKED report remains unchanged and corrections get separate reports.
Normal current-tree CI/Live must qualify the exact preview checkout and map to the
candidate tree; earlier PR28 results do not qualify new code. No manual paid retry
or new Web qualification is implied. Only after all required current-tree gates
pass use normal Ready and expected-head-locked integration, then verify actual
ordered parents/tree/ref. Independent technical PASS does not mean human APPROVE.

Definition completion means reviewed canonical task/contract, documentation-only
branch from actual PR28, exact source/readback identities and synchronized current
references. Implementation completion later requires all A01-A12 families and
the gates above. API/HTTP/UI/CLI wiring, scheduler/workflow changes, automatic
phase progression, remote-lease retention, post-drift proposal refresh, old
candidate migration, new recovery policy, credentials, main, PR6, root todos.md,
AskTD/ETL/customer work, deployment, history rewriting and generated-source
publication are excluded. Root September1 remains unverified and ignored.
# Implementation scope decision — cumulative capture accounting

The definition's 256,000,000-byte cumulative capture limit requires accounting
at the existing shared read boundaries. The author records this concrete scope
exception before changing those boundaries: an opt-in, context-local read budget
in a new acceptance companion may be charged by `storage/artifacts.py`,
`sandbox/owned_source.py`, `product/program_source_attestation.py`, the immutable
artifact getter in `product/program_source_acceptance.py`, and bounded v3 readers.
The counter is inactive outside an explicit new acceptance capture. It grants
no owner, changes no execution/settlement schema, performs no write, and expands
no legacy acceptance or v3 transaction authorizer. Existing per-read bounds remain.
Budget exhaustion is a denial, including repeated reads. This is an implementation
scope decision, not implementation acceptance or completion of A01–A12.

The existing local Git clone fixture leaves shared immutable loose Git objects
in the origin's `.git/objects` directory. Origin inspection records their complete
bytes and exact link counts; it does not require an initial count of one for
those existing Git objects. All later link-count/identity changes deny capture.
Artifact and source files still require one link, and symlinks are never followed.
