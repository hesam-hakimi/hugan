# P3.5d-2 — Validation, delivery and product decisions

Status: d2a accepted and integrated through actual corrected PR27
`fdb97d3d10c8a843eae0ab71c255c3ebd0e6ac4a`, tree
`f1e78ac88cdb58c166e4fd51f672c54f9625f210`. D2b-1 is defined only; no successor
implementation, PR, test result or platform run is claimed. Later slices remain
planned. The initial d2a BLOCKED tree and corrected PASS/CI439/Live190 tree retain
separate evidence. Do not repeat already completed PR26/PR27 gates.

References: [parent design](P3_5D2_PRODUCT_CONTINUATION_DESIGN_2026-09-08.md) and
[first task](P3_5D2A_PROGRAM_CONTINUATION_HANDOFF_TASK_2026-09-08.md).

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

## Defined d2b-1 evidence plan — not yet run

The [d2b-1 task](P3_5D2B1_V3_CONTINUATION_EXECUTION_TASK_2026-09-08.md) and
[consumer contract](P3_5D2B1_V3_ADMISSION_AND_QUIESCENCE_CONTRACT.md) own V01-V12.
They make C06-C09 and the v3 portions of C03-C05/C14 concrete. Definition delivery
checks only documentation, source identity and unchanged runtime/test/workflow bytes.
There is no documentation-only PR or new paid Live run.

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
