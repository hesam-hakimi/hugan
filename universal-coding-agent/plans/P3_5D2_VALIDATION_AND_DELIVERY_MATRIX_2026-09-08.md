# Current delivery decision — local Product for a supervised pilot

The owner approved delivery milestone `UCA-M-LOCAL-PILOT-1` on 2026-09-08:
a locally runnable UCA Product for supervised real-project testing at the end of
P3.5d-2. The [canonical delivery milestone](P3_5D2_LOCAL_PRODUCT_PILOT_DELIVERY_MILESTONE_2026-09-08.md) defines LP01-LP06 for local
readiness and separate RP01/RP02 for read-only onboarding followed by one bounded
change. Status is **approved and planned; not delivered or pilot-validated**.

Accepted runtime remains actual PR29 merge
`f27c2693babcdf20145676328012b2d7576c5aa3`, tree
`29b763ff5af8a50348f7e987b341db65fac33bfa`. Ordered parents are accepted PR28
`95096565d85640ea471182fc0b421e124667b73b`, then corrected candidate
`b0e1a9dd590ba33a65d42868553bcada15c432ee`. Separate preview
`9f816b01cae2d60e8241b32c4a7b43d61d6afabe` is not the actual merge.
PR29's initial F1/F2 BLOCKED and separate correction PASS reports remain unchanged;
CI446/Live197 attempt 1 qualify the correction, while CI445/Live196 retain initial
scope. Standard Live Program remains v1; no cumulative live-model v3 Product
journey or customer-project pilot has been qualified. Do not repeat accepted gates.

D2a, d2b-1 and d2b-2 are accepted and complete. D2c-1/API and d2c-2/UI remain
planned and uninstantiated. The next engineering action is **d2c-1 definition**:
typed local commands, host-owned project bindings, durable request outcomes and
inert status. The later UI and actual real-model Product journey each require
their own evidence before delivery readiness. This documentation update starts
no implementation, model execution, customer access, qualification run or PR gate.
Existing bounded authority and runtime approvals remain distinct; no routine owner
reconfirmation is needed to prepare the next definition.

This block supersedes earlier operative status and next-action wording below.
Earlier exact text and source-specific observations remain history. Canonical
plans stay in Git; project-specific pilot mapping stays in the private handoff.

---

# Current checkpoint — P3.5d-2b-2 implementation candidate

The bounded implementation now exists on the source-transition definition
branch, descending from verified definition commit
`62f988ed85c219715a7d74bbfc75f03c54f3d7a0`. It adds immutable candidate-2 evidence
cores, distinct temporary capture witnesses, separate fresh preview/decision
workers, an atomic receipt-2/source-head/request/release transaction, an explicit
one-action host companion, and a standalone recorded mixed-version reader.
The final two-phase result can be explicitly accepted at generation 2 / 44 in
the deterministic real Program/Safe/Git fixture. Original 42 and accepted material
43 remain unchanged. Receipt-2 enables no materialization or third phase.

The canonical task maps A01–A12 to submitted executable evidence and records the
limited shared-read accounting scope decision. Author development runs are not
independent acceptance. Exact candidate-tree author, separate independent,
current-tree CI/Live, normal Ready and expected-head integration gates remain
required; their observations must identify their own source trees. This source
checkpoint claims no completed platform/integration gate or cumulative live-model
v3/Product journey. PR28 remains accepted; its gates are not rerun for credit.
D2a remains inert and d2c-1/d2c-2 remain planned and uninstantiated.

This block supersedes operative status below. Earlier definition and failed
candidate records remain history with their original source identities.

---

# Current checkpoint — P3.5d-2b-2 defined from accepted PR28

P3.5d-2b-1 is accepted and complete. Only P3.5d-2b-2 is newly instantiated as a
documentation-only task and branch; runtime implementation has not started.
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

Canonical new [source-acceptance task](P3_5D2B2_SOURCE_TRANSITION_ACCEPTANCE_TASK_2026-09-08.md) and
[evidence-core/acceptance contract](P3_5D2B2_EVIDENCE_CORE_AND_ACCEPTANCE_CONTRACT.md) select a separate candidate-2
preview and exact decision under fresh workers, ending at accepted generation 2 /
44. First-phase 43 retains existing same-owner acceptance. Receipt-2 does not
enable later materialization or dispatch in this slice. D2c-1/d2c-2 remain planned
and uninstantiated. No new PR, tests, CI/Live/Web or implementation acceptance is
claimed for this definition. Do not repeat PR26/PR27/PR28 gates.

This current block supersedes operative status/next-action wording below; the
exact prior text remains historical, including both PR28 blocked candidates.

---

# P3.5d-2 — Validation, delivery and product decisions

Status: d2a accepted and integrated through actual corrected PR27
`fdb97d3d10c8a843eae0ab71c255c3ebd0e6ac4a`, tree
`f1e78ac88cdb58c166e4fd51f672c54f9625f210`. D2b-1 has a bounded implementation
candidate under author verification; independent and current-tree platform gates
remain pending. Later slices remain
planned. The initial d2a BLOCKED tree and corrected PASS/CI439/Live190 tree retain
separate evidence. Do not repeat already completed PR26/PR27 gates.

References: [parent design](P3_5D2_PRODUCT_CONTINUATION_DESIGN_2026-09-08.md) and
[first task](P3_5D2A_PROGRAM_CONTINUATION_HANDOFF_TASK_2026-09-08.md).

## First correction remains blocked; second correction scope

First correction `55636c067479abdd856bdd349e7d18d224d5e168`, tree
`2c0a8f767f88b701206021dae33d8e2d6bb4d875`, resolves the original four reproductions
but remains independently BLOCKED: an unknown checkpoint execution version can
hide surviving source affinity after all three routing markers are lost, and a
separate WAL writer can grow checkpoint bytes between the raw routing reader's
preflight and retrieval. Its author 165 v3 + 532 compatibility passing cases remain
scoped to that tree. Live193 attempt 1 failed its hard CDC group: the generated fixture documentation
used `operation` instead of the required `op`, so review returned
`PASS_WITH_CONDITIONS`; source was preserved and the patch rolled back. CI442
attempt 1 passed 1636 tests per Python leg on preview
`bbdfd827017b43fae5d792998cfe88aa8246baea`. All first-correction observations
remain separate history, never final qualification.

The second correction treats reserved execution/admission metadata and retained
accepted-source lineage as denial evidence regardless of version value, including
missing/unknown/rewritten versions. It denies unsupported checkpoint extensions
and shapes, passes copied source evidence to the raw discovery gate before provider
work, and preserves the existing exact c2 adapter/registry route. Raw checkpoint
retrieval binds the selected id, encoding and byte length in SQL, caps the actual
returned bytes, and validates them before decode. None of these metadata markers
grants execution. A separate second-correction review and normal current-tree
platform results are required before Ready or integration; reports retain both
prior BLOCKED verdicts.

## Initial blocked candidate and correction scope

Initial implementation `de99db9fdff64745d76f07ff6061044534851642`, tree
`c15863e8e05f5f662560da0fe5a3144b59bc93af`, was independently BLOCKED for raw
Safe routing after guard namespace loss, incomplete closed d2a history,
unbounded v3 registration lock waits, and mutating-PRAGMA authorizer gaps.
The correction adds an immutable independent root locator and plain checkpoint
version denial, complete bounded inert predecessor validation, bounded new v3
registry waits with monotonic revocation, and read-only PRAGMA allowlists. CI441
attempt 1 failed both Python legs (1612 passed, one child-import harness failure
per leg); that harness now supplies its fixture import path explicitly. Live192
attempt 1 passed on the initial preview `cc9bee057af186f74c66e5aebfe7a92495118e3a`.
These observations remain initial-tree history. Corrected-tree independent review
and platform outcomes are recorded separately in PR28 and external evidence;
no initial result substitutes for those gates. Standard Live Program remains v1.

## Accepted d2a test mapping

`tests/test_program_continuation_handoff.py` uses actual on-disk Program/control/
lifecycle stores, actual Program execution bindings and a real SQLite checkpoint
store for preservation checks. Deterministic fixture planning precedes handoff;
handoff never calls a provider. Source-head fixture hashes are metadata references,
not a claim of source-byte or real acceptance qualification.

| Cases | Concrete candidate coverage |
| --- | --- |
| C01/C02 | Fresh-process park/claim/close, concurrent process claims, 46 real process-death cases at receipt/worker/request/head and both sides of commit with DELETE/WAL unmodified control |
| C03 | Exact create/park/claim/close replay after lost responses, no token restoration, conflicting IDs, unknown/in-progress diagnosis |
| C04 | Exact owner/epoch/proposal, actual pause/cancel/realign/control revisions, source/head changes, lifecycle remote/control/task conflicts, host and file replacement, explicit administrative recovery |
| C05 | Read-only byte/logical preservation, effectful-module import probe, strict JSON/schema/field/row/aggregate budgets, keyset pages, current and older receipt tampering |
| C02/C04 | Both writer journal/sync settings rejected without alteration; SQL triggers cannot modify unrelated Program rows |
| C02/C04 correction | Preconstructed separate TaskControlService processes attempt real pause commits at create/park/claim/close commit boundaries under both DELETE and WAL; control stays unmodified and subsequent explicit pause succeeds |
| C14 compatibility | Existing `test_program_source_status.py`, `test_program_source_dispatch.py`, `test_program_execution.py` and all lifecycle reservation/recovery/index/pagination tests retained |

The published review/qualification evidence records exact head/tree, commands,
counts, failures and platform attempts. The tests above do not qualify C06-C13's
later provider, checkpoint, acceptance or Product API/UI consumers. Standard Live
Program remains v1 even if the ordinary workflow passes on this candidate.

## D2b-1 candidate evidence and outstanding acceptance gates

The [d2b-1 task](P3_5D2B1_V3_CONTINUATION_EXECUTION_TASK_2026-09-08.md) and
[consumer contract](P3_5D2B1_V3_ADMISSION_AND_QUIESCENCE_CONTRACT.md) own V01-V12.
They make C06-C09 and the v3 portions of C03-C05/C14 concrete. Definition delivery
completed at `7f2286f3395658b28ad4d7a3e2921116bbdd51ac` with unchanged runtime.
The subsequent implementation adds actual deterministic host evidence in
`test_program_continuation_dispatch.py` and `test_program_continuation_boundaries.py`.
Exact final run counts and candidate identities are recorded with submission;
author tests do not substitute for independent probes or current-tree CI/Live.

| Parent requirements | D2b-1 decisive cases | Boundary |
| --- | --- | --- |
| C06 / C14 | V08 / V12 | Exact v3 adapter/registries and durable deny guards; all legacy effect paths blocked, including missing metadata; c1/c2/d2a preserved |
| C07 / C09 | V01 / V07 | Real accepted 43 -> actual discovery/scope stop -> fresh-process exact decision -> tested/reviewed terminal-unaccepted 44 |
| C01 / C02 / C04 / C08 | V02-V05 / V11 | Live outer invocation settlement, all owned work absent, registration barrier, actual SQLite writers excluded through atomic release/claim |
| C03 / C08 | V05 / V06 | Ambiguous invocation cannot replay; completed response carries no capability; crash before settlement may remain blocked |
| C05 / C14 | V10 / V12 | Bounded standalone v3 host reads and fail-closed legacy route denial; no public Product v3 projection yet |
| Source preservation / failure | V07 / V09 / V12 | Immutable accepted source/preparation, exact rollback and failed/rejected outcomes; no source advancement |

Only the real scope interrupt is resumable in d2b-1. The broader fault/journey rows
below retain later-slice ownership: discovery-only parking, post-drift refresh,
remote-lease recovery, source previews/acceptance and Product actions are not
implicitly included. A checkpoint by itself cannot authorize reconciliation after
process loss: d2b-1 requires the still-live invocation's actual return/revocation
proof, or an already committed park/close. Exact administrative row removal grants
no continuation capability. Successful 44 stays terminal-unaccepted at generation
1/accepted 43; C10/C11's accepted generation 2 remains d2b-2.

## Requirements and evidence ownership

| ID | Requirement | First owning slice | Decisive evidence |
| --- | --- | --- | --- |
| C01 | Fresh worker per explicit action; no worker held for a person | d2a | Actual owner-row identities across park/restart/claim, one exclusive worker |
| C02 | Atomic receipt/epoch/worker change | d2a | Process death on both sides of each commit with both on-disk stores inspected |
| C03 | Durable request idempotency without effect replay | d2a then d2b | Exact response replay; lost private claim token cannot be reconstructed; no duplicate invocation |
| C04 | Old owner, proposal, epoch and changed control reject | d2a | Concurrent/stale-state negatives and preserved existing lifecycle exclusion |
| C05 | GET never creates stores, recovers or performs provider work | d2a then d2c | Fresh-process module checks and database/provider/source fingerprints |
| C06 | No mixed v1/v2/v3 authority routing | d2b-1 | All public Safe/discovery/acceptance entrypoints and duplicate registry cases |
| C07 | Actual scope stop permits a new worker and exact approval | d2b-1 | Real Safe checkpoint, different private owner and no repeated discovery |
| C08 | Ambiguous provider/apply/test/review work cannot replay | d2b-1 | Live process-local capability loss plus existing interruption cases |
| C09 | Preparation verification and immutable materialization preserved | d2b-1 | Actual c1 complete proof, consumed immutable bytes, derived Git/source/inode checks |
| C10 | Source acceptance stays distinct from execution/scope | d2b-2 | New candidate evidence-core approval; full recapture under current owner; stale approval rejects |
| C11 | Actual cumulative 42/43/44 accepted lineage | d2b-2 then d2c | Real Program/Safe/Git/discovery/subprocess tests/review/acceptance, fresh process |
| C12 | Browser sends explicit intent, never host authority/configuration | d2c-1 | Host project binding, typed request allowlists, wrong project/Program/task rejection |
| C13 | UI acts on current server proposal and distinguishes outcomes | d2c-2 | Actual HTTP-backed controls, refresh/stale conflict, rejection and terminal-unaccepted views |
| C14 | PR26 F1/F2 cannot reappear | Every changed consumer | Impossible state and missing combined preparation/admission never yield complete history or v1 fallback |

## Fault and replay matrix

| Boundary | Required post-crash observation | Forbidden inference |
| --- | --- | --- |
| Before create/park commit | Previous receipt/epoch and exact old owner remain | Partial receipt grants a new action |
| After park commit, before response | One parked receipt, no old owner; completed request can replay | Recreate the old worker token |
| Two simultaneous claims | One committed fresh owner/epoch; loser gets conflict | Both claims return execution permission |
| After claim commit, before response | Owned epoch remains; exact request has a recorded outcome | Repeat claim or recover the private token from DB |
| Before provider claim | New consumer ticket may be lost; effect has not been proven complete | Reconstruct an armed invocation merely because it was not claimed |
| After provider claim, before result | Owned/ambiguous operation remains stopped | Timeout, retry or browser reconnect authorizes another invocation |
| After real scope checkpoint, before Program result | Explicit same-operation reconciliation may establish the actual stop | Discovery/apply replay or guessed scope acceptance |
| After approval decision, before terminal checkpoint | Ambiguous in-progress result | Reuse approval as proof of completion |
| After terminal checkpoint, before result receipt | Explicit exact checkpoint reconciliation | Overwrite the prior committed report |
| After source-candidate preview, before later approval | Immutable evidence core and source predecessor remain inspectable | Prior worker witness authorizes acceptance under a new worker |
| After acceptance commit, before response | One accepted generation/receipt and exact response replay | Advance the source again or start the next phase automatically |
| After exact administrative owner recovery | Recovery receipt and explicit blocker | Administrative row removal proves Safe quiescence |

Use real temporary database files/processes for d2a transactions, not mocked commit
return values. Use deterministic providers plus actual Git/Safe/Program/subprocess
execution for d2b/d2c. Mock transport-only HTTP tests and rendered UI snapshots may
supplement, not replace, the real consumer journey. Full-suite success does not
prove an untested crash boundary. Keep each failure and its exact source identity.

## Planned local Product journey

1. Bind a local project using host-owned repository, source, provider and trusted
   profile configuration. Explicitly initialize source metadata after attestation.
2. Run the existing original-Base first phase through explicit Product actions.
   Preserve its v1 evidence rules. The first fixture result is tested/reviewed 43.
3. Show the actual source transition preview. The user explicitly accepts that
   exact evidence core; the current worker revalidates it and records generation 1.
4. Show accepted 43 and offer one explicit next-phase action. Preparation and v3
   admission occur under the current worker; actual discovery must read 43.
5. At the actual Safe scope stop, park the continuation and release the worker.
   Close/reopen the Product process. Loading status invokes no provider.
6. Show the current scope proposal. Explicit approval claims a fresh worker,
   revalidates the checkpoint/source/control and starts one permitted invocation.
7. Show completed, tested/reviewed 44 as terminal but not yet source-accepted.
8. Separately preview/accept the exact transition and show complete generation
   0/1/2 lineage. The original source remains 42 and accepted material stays immutable.

The UI should use user-facing actions such as Review scope, Continue, Review source
changes and Accept source. It should display the source generation, relevant diff,
test/review outcome and reason an action is unavailable. It should not expose worker
epochs, private tokens, receipt internals or infrastructure choices as decisions a
product user must make. Diagnostic hashes can remain in an optional evidence view.

A refresh does not generate a new candidate, reconcile a checkpoint or approve an
operation. A stale action should give a clear refresh-and-review instruction. The
client must not retry an effect automatically after a conflict or unknown response.

## API/configuration decisions before d2c

These are planned requirements, not newly existing endpoints:

- Distinct typed commands for source initialization, transition preview/acceptance,
  next-phase admission/discovery, scope decision and explicit reconciliation.
- Host-owned project binding IDs resolve repository/policy/provider/test profiles;
  requests carry Program/task IDs, current expected revision, exact proposal digest,
  action/request ID and explicit approval/decision only as appropriate.
- Bounded JSON schemas with unknown-field rejection and stable typed errors. Public
  response allowlists exclude paths, repository credentials, owner/capability digests,
  raw private receipts and provider identifiers. Enforce the existing local-only
  serving boundary and explicit same-origin request rules for new effectful routes.
- Durable request outcome lookup for lost responses; pending/ambiguous means inspect,
  not repeat. IDs/hashes alone are not bearer authorization.
- Default-disabled source-aware product execution until all d2a/b/c gates pass.
  Local operator opt-in is explicit. Multi-user authentication/RBAC and remote
  deployment are outside scope, not implicitly supplied by this local contract.

The exact route names, status codes, project-binding storage/configuration and new
consumer schema validation must be resolved in their owning task before code there.
No new owner question is necessary for d2a: local-only, existing policies/profiles,
no deployment and no customer source are already the bounded defaults.

## Implementation sequence and review gates

1. Publish these definition documents on a new branch from actual PR26, with no
   runtime/test/workflow changes and no PR yet. Record its exact commit/tree/parent.
2. Implement d2a only after reading its task and current consumers. Run meaningful
   focused tests, Ruff and diff checks; open its Draft PR for normal current-tree
   platform qualification. No selective gate suppression or workflow changes.
3. Obtain separate independent technical acceptance on the exact implementation
   head/tree. Preserve findings, corrections and source-specific qualification.
4. Use normal Ready and expected-head-locked merge only after all required gates;
   verify actual merge tree, ordered parents and target ref.
5. Define the next concrete slice from that accepted integration. Do not expand d2a
   in place into provider execution, source acceptance or web/UI work.

D2a's review must test the transaction consumers and unchanged lifecycle boundaries.
D2b adds current-proof/adapter/acceptance security review. D2c adds actual HTTP/UI
execution/approval/restart review. No review is a new unrestricted repository audit
unless separately authorized, and no technical report is human GitHub APPROVE.

Current standard Live Program qualification is v1. A successful unchanged Live run
on future code does not establish live-model v3 or cumulative-product qualification.
If dedicated live coverage is later needed, define its smallest approved fixture
and cost/run boundary separately before changing the workflow. Never blindly rerun
paid Live or repeat successful suites for freshness. Diagnostic ZIP API digests do
not become independent rehashes.

## Preimplementation exit checklist

- Accepted PR26 identity verified and history preserved.
- Actual ownership, candidate, preparation, adapter and Product consumers inspected.
- Selected versioning/ownership model and rejected alternatives written.
- First implementation slice, allowed paths and non-goals bounded.
- Transaction, replay, crash and proof obligations traceable to tests.
- API/UI and source-acceptance work separated into later explicitly gated tasks.
- Definition artifacts published and current canonical handoff synchronized.

This checklist records preparation completion only. No runtime capability, new
independent verdict, successful new suite or merged successor may be inferred.
