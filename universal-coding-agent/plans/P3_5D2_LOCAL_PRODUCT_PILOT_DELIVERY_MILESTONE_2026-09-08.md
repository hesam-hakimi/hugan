# P3.5d-2 local Product delivery for a supervised existing-project pilot

Milestone ID: `UCA-M-LOCAL-PILOT-1`

Status: **owner-approved delivery goal; planned; not delivered**.
Decision date: 2026-09-08. This document records delivery criteria only. It
instantiates no d2c implementation task, qualification run or customer pilot.
The owner-specific pilot target is recorded in the private delivery references;
the public product and engineering contract remain project/provider neutral.

## Accepted engineering baseline

PR29 is accepted and integrated at
`f27c2693babcdf20145676328012b2d7576c5aa3`, tree
`29b763ff5af8a50348f7e987b341db65fac33bfa`, merged 2026-09-08T18:46:55Z.
Its ordered parents are `95096565d85640ea471182fc0b421e124667b73b` then
`b0e1a9dd590ba33a65d42868553bcada15c432ee`. Preview
`9f816b01cae2d60e8241b32c4a7b43d61d6afabe` remains a distinct commit.

The explicit Python host has bounded real Git/Program/Safe evidence for original
42, first accepted 43, continued tested/reviewed 44 and separately accepted 44 at
generation 2. PR29's initial F1/F2 BLOCKED report remains separate from its
correction PASS. CI446 and Live197 attempt 1 qualify the corrected tree only;
CI445/Live196 retain their initial-tree scope. Standard Live Program remains v1.
No cumulative live-model v3 Product journey or target-project pilot is qualified.
Do not rerun accepted PR26/PR27/PR28/PR29 gates as new delivery evidence.

## Deliverable and acceptance states

The intended end-of-P3.5d-2 deliverable is a locally runnable UCA Product that an
operator can use to bind an existing project, submit a bounded objective, inspect
the proposal and diff, explicitly approve scope, follow execution, inspect actual
test/review results, resume the supported stopped operation after process restart,
and separately accept the exact resulting source. The local launch and operating
instructions must be usable by the pilot operator in the qualified environment.

Track three facts separately:

| State | Meaning | Current value |
| --- | --- | --- |
| `delivery_goal_approved` | The milestone and criteria are included in project delivery | true |
| `ready_for_supervised_pilot` | Every LP01-LP06 delivery criterion has exact evidence | false |
| `real_project_pilot_validated` | Both RP01 and RP02 have passed under separately bounded pilot tasks | false |

The first deliverable makes real-project testing possible. The later pilot verdict
records whether it actually worked on the selected project. API completion, a UI
snapshot, standard Live v1, a host-only fixture, or a successful documentation sync
cannot individually set either readiness or pilot validation to true.

## Delivery acceptance matrix

| ID | Criterion | Owning work | Required evidence |
| --- | --- | --- | --- |
| LP01 | Reproducible local launch and project binding | d2c-1, completed by delivery handoff | Version/commit-pinned launch recipe; recorded supported OS/runtime; existing provider/test-profile configuration resolved by the host; operator can reopen the same project and inspect state |
| LP02 | Explicit Product API operations | d2c-1 | Actual HTTP consumer tests for the supported first-phase, preview/acceptance, next-phase, scope-decision and outcome-inspection actions; typed allowlists; wrong-project rejection; durable same-request replay and content-conflict denial; GET/refresh performs no work |
| LP03 | Usable controls and evidence views | d2c-2 | Actual API-backed browser journey with Review scope, Continue, Review source changes and Accept source; current diff/test/review evidence; actionable blocked/stale/ambiguous states; source acceptance visibly distinct from execution completion |
| LP04 | Qualified complete local Product journey | End-to-end delivery qualification, bounded task to be defined | Actual Git/Safe/Program/test/review/HTTP/UI journey plus a bounded real-model run on the candidate: first acceptance, next phase on accepted source, real scope stop, Product restart, explicit continuation and separate final acceptance; original source preserved; exact model/run/source/result provenance |
| LP05 | Safe failure and recovery behavior | d2c-1/d2c-2 and delivery qualification | Rejection, failed or conditional test/review, source/policy drift, stale actions, duplicate requests, lost response and process crash do not advance source or repeat effects; retained or ambiguous ownership is shown as blocked; current lineage checks retain PR29 F1/F2 coverage |
| LP06 | Reviewed handoff of the exact local candidate | Delivery closure | Separate independent technical PASS, applicable current-tree CI/Live/Web gates, normal Ready and expected-head-locked integration; concise launch/use/restart/rollback guide; bounded test scenario and expected observations; known limits and evidence links; explicit readiness verdict |

LP04 adds required delivery evidence; it does not claim an existing live-v3 recipe
or authorize an immediate paid run. The owning qualification task must first pin
its candidate, actual operator journey, environment, provider/profile, budget,
stop conditions and evidence. Deterministic consumer coverage and real-model
observations remain distinct. Retain failures, conditions and corrective runs with
their own identities. Do not sum overlapping author/independent/platform counts.

## Supervised real-project validation after local delivery

| ID | Pilot step | Entry condition | Passing outcome |
| --- | --- | --- | --- |
| RP01 | Read-only onboarding | LP01-LP06 passed; actual project Base SHA, access boundary, approved roadmap/ADRs and business context pinned in a bounded pilot task | Evidence-backed implementation-versus-roadmap mapping, uncertainties, impact/dependencies and one proposed low-risk change; source remains unchanged |
| RP02 | One bounded change | RP01 accepted; exact proposed objective, files/scope and trusted checks approved before effects | Isolated change with diff, actual tests, separate independent review, rollback/source-preservation evidence and explicit source decision; no implicit next task |

The owner has approved this staged pilot direction. Existing engineering authority
continues without routine reconfirmation. Project access qualification and exact
runtime scope/source decisions remain required evidence, not repeat permission
requests for the already-approved direction. A concrete blocked access or material
scope expansion must be identified rather than bypassed. This planning update
does not access the customer project, obtain credentials, run models or edit it.

## Sequence and task boundary

1. Define the bounded **P3.5d-2c-1** task and API/host-binding contract from the
   actually accepted PR29 baseline while carrying this published milestone forward.
2. Implement and qualify d2c-1 under its own gates.
3. Define, implement and qualify d2c-2 for the actual Product controls.
4. Complete LP04-LP06 through explicitly defined delivery qualification/handoff
   work and record `ready_for_supervised_pilot` only from completed evidence.
5. Execute separately bounded RP01, then RP02, and record the pilot verdict.

D2c-1/d2c-2 and later qualification/pilot tasks remain uninstantiated by this
document. Two main API/UI slices remain; this is not a promise of exactly two PRs,
a completion date, or an already accepted product. The next prompt is for d2c-1
definition, not implementation. A later execution session must use its completed
canonical task rather than infer runtime authority from this milestone text.

## Preserved contracts and exclusions

Execution, scope decisions and source acceptance remain distinct. Keep first-phase
v1 same-owner acceptance, c1 preparation, c2 exact-owner routing and PR28 settlement
guards. Retain candidate-2 immutable cores, separate fresh preview/decision workers,
complete mixed receipt lineage and the atomic final acceptance transaction. D2a
metadata is inert; historical replay grants no token/ticket. Browser intent cannot
supply host paths, providers, credentials or capabilities. Respect pinned bounds,
local-only serving and same-origin rules. No automatic retries or recovery on GET.

Receipt-2 still enables no later materialization or third phase. No v1/v2 migration,
post-drift refresh, automatic next phase, arbitrary shell, generated-source
publication, production deployment, ETL work or customer-specific public-core
configuration is added. `main`, PR6, root `todos.md`, credentials and history
rewriting remain outside scope. The broader worker/service Milestones 4/5 remain
separate; only their controls concretely needed for this bounded local pilot are
prerequisites. No complete production service or autonomous project-roadmap
execution is implied.

## Canonical references

- [Product continuation design](P3_5D2_PRODUCT_CONTINUATION_DESIGN_2026-09-08.md)
- [Validation and delivery matrix](P3_5D2_VALIDATION_AND_DELIVERY_MATRIX_2026-09-08.md)
- [Accepted source-transition task](P3_5D2B2_SOURCE_TRANSITION_ACCEPTANCE_TASK_2026-09-08.md)
- [Evidence-core and acceptance contract](P3_5D2B2_EVIDENCE_CORE_AND_ACCEPTANCE_CONTRACT.md)
- [Roadmap](../ROADMAP.md)

Canonical engineering plans remain in Git. Private handoff references link the
exact published document identity and map the chosen pilot project; they do not
create another canonical plan. This milestone publication requires an author
documentation review only and claims no new runtime, independent implementation,
CI/Live/Web, Ready or merge result.
