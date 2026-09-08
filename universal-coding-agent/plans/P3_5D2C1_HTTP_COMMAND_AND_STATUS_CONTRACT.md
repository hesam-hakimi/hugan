# P3.5d-2c-1 — HTTP commands and recorded status

Status: normative documentation-only definition for the
[local continuation API task](P3_5D2C1_LOCAL_CONTINUATION_API_TASK_2026-09-08.md).
No API implementation or qualification is claimed. Baseline is actual PR29
`f27c2693babcdf20145676328012b2d7576c5aa3`, tree
`29b763ff5af8a50348f7e987b341db65fac33bfa`.

## Authority and entry

The new route starts only from actual receipt-1 / source generation 1 of an
approved, unsliced, exactly two-phase linear Program. Phase 1 is completed and
accepted; phase 2 is pending and has no execution binding. Revalidate actual
requirement/plan, receipt-1 lineage, source, host/policy and all existing lifecycle
exclusions. IDs and hashes supplied by the client are comparisons, not proof.
Original-Base first-phase execution/acceptance is outside this route. A source
head seeded by a fixture, uploaded receipt or caller PASS bundle is ineligible.

The trusted host explicitly binds the Program/project to existing stores and
approved repository/origin, policy, requirement, plan, test profiles and one
supported synchronous transport with publication disabled. Binding construction
is programmatic in this slice; no new CLI configuration or UI is included.
An absent binding rejects effects. Keep immutable public binding digests separate
from private paths/provider objects. Do not use a browser's repository, ref,
filesystem destination or provider fields to construct the host.

New routes enforce a configured loopback peer and exact configured Host authority
(including port); do not trust forwarded headers. Browser Origin, if present,
must equal the configured local origin; reject null, multiple and cross-origin
values. POST requires `application/json` and `X-UCA-Command: 1`. Nonbrowser local
clients may omit Origin only with the same Host/peer/header checks. Do not enable
CORS or accept form bodies. These are local invocation checks, not multi-user
authentication or hostile same-UID isolation. Default-unbound routes cannot
initialize effectful services. Do not broaden unrelated old routes in this task.

## Exact typed surface

All paths are below `/api/programs/{program_id}/continuation`. Program and request
IDs are strict bounded identifiers, not paths. Each POST body has exactly
`schema="uca-product-continuation-command-1"`, `request_id`, `action`, and that
action's fields below. `program_id` comes from the route and is included in the
canonical stored payload. Host digest comes from the trusted binding. Forbid
unknown fields and duplicate JSON keys before model parsing. Require actual JSON
booleans and nonnegative integers: strings, floats and booleans-as-integers do
not coerce. Hashes are lowercase 64-character SHA-256 encodings.

| Method/path | Action and exact additional fields | Owning effect |
| --- | --- | --- |
| POST `/start` | `start`; `expected_requirement_sha256`, `expected_plan_sha256`, `before_sha256`, `generation` (exactly 1), `acceptance_receipt_sha256` | Reserve one fresh worker; actual materialization/Base preparation; consume c1 through v3 admission and dispatch within that episode |
| POST `/scope-decisions` | `scope_decision`; `operation_id`, `admission_sha256`, `expected_epoch`, `expected_receipt_sha256`, `proposal_sha256`, `scope_sha256`, `approval_id`, `approved` | PR28 exact parked-proposal decision with its separately reserved fresh worker |
| POST `/source-previews` | `source_preview`; `operation_id`, `terminal_receipt_sha256`, `before_sha256`, `generation` (exactly 1) | PR29 fresh-worker terminal capture and completed preview |
| POST `/source-decisions` | `source_decision`; `operation_id`, `terminal_receipt_sha256`, `before_sha256`, `generation` (exactly 1), `candidate_sha256`, `revision`, `core_sha256`, `transition_sha256`, `predecessor_receipt_sha256`, `approval_id`, `approved` | PR29 separate fresh-worker exact decision and receipt-2/source-head CAS |
| GET `/` (also normalized without trailing slash) | No effect body; optional bounded `after_sequence` and `limit` | Recorded Program/source/command summary with typed blockers |
| GET `/operations/{operation_id}` | Optional bounded `after_sequence` and `limit` | Exact recorded v3 operation; no inferred latest operation for an effect |
| GET `/requests/{request_id}` | No body | Exact recorded command identity/outcome; no retry or reconciliation |

The coordinator maps scope fields unchanged to
`ProgramContinuationDispatchService.approve_scope`, and source fields unchanged
to `ProgramSourceAcceptanceV2Service`'s existing preview/decision methods. Do not
add a parallel authority service. No effect route accepts a replacement owner, live
ticket, decoded checkpoint, evidence core, approval object or source bytes.

Body limit is 65,536 bytes including streamed/chunked input, enforced before full
buffering/JSON decode; oversized declared length rejects early and missing length
does not bypass the stream bound. Depth 8, at most 64 fields per object, scalar
strings at most 4 KiB and identifiers at most 128 UTF-8 bytes retain stricter
lower-service validation. IDs generated by the host must fit the same limits.
Do not encode paths in a nominally opaque ID. Responses are `no-store` and use
stable typed error codes with fixed public messages, not raw exception text.

## Durable command records and exact replay

Add versioned, bounded records in the existing Program database. The logical
schemas are `uca-product-continuation-command-1` and
`uca-product-continuation-response-1`. Tables are
`program_product_continuation_commands_v1` and
`program_product_continuation_command_heads_v1`. Initialization is explicit host
setup, never GET, completed replay or an incidental constructor in those paths.
Attest exact schema/index definitions and deny unrecognized triggers/extensions.

Each command row binds host digest, Program/request ID, action, canonical payload
hash, state, server operation ID, exact child request identities, immutable
response hash and predecessor command reference. Pending response hash is null.
State is `pending` or `completed`; recovery-required is a read-only diagnosis,
not a GET transition. Exact JSON allowlists and state-specific null fields must
be frozen in the implementation and tested. Retain immutable request/response
artifacts; hashes are integrity bindings, not signatures or capabilities.

Enforce unique `(program_id, request_id)` including action/body/host binding, and
at most one pending command for a Program. Two hosts cannot claim the same ID by
partitioning uniqueness on host digest. The head is only a command exclusion and
history link, not source authority. Existing lifecycle/control/source guards still
decide whether a new command is admissible. A pending command blocks a new ID from
restarting that work; absence of a process-local run object never makes it safe.
An active command marker also denies nonparticipating raw/legacy effect entrypoints
for that Program. Missing companion command records with surviving markers fail
closed. Add only the required additive deny guard; records without HTTP markers
retain their accepted behavior. Administrative worker removal cannot bypass this
command guard or adopt the interrupted command under a fresh request ID.

For start, allocate an operation ID and persist its exact child IDs atomically
with command reservation and fresh lifecycle worker reservation, before any
materialization/graph effect. Derive bounded child request IDs from a domain-tagged
hash of Program, host, command ID and child action; do not collide with public IDs
or copy owner tokens into their digests. Store/check the mapping, not a guess at
the newest admission. Start owns preparation, admission and dispatch; later HTTP
commands use the corresponding actual v3/acceptance request as their one child.

For scope/preview/decision, attach the pending command write to the existing
lower-service fresh-worker claim transaction. Never pre-reserve a second worker.
Use narrow private connection-scoped journal operations, with exact allowlisted
SQL and no nested public commit. For start, complete the command at actual v3
park/terminal sealing. For later commands, complete at their underlying outcome
commit. In each case, the immutable public command response, exact lower response
hash/link, command head, lower receipt and exact worker release commit together.
The journal introduces no separate release or source-head update. No provider or
long-running process runs inside these transactions.

The response envelope has exactly schema, host digest, Program/request ID, action,
payload hash, operation ID, `request_status="completed"`, lower response hash,
the bounded redacted lower public response and the false flags below. Freeze
canonical UTF-8 bytes when completing. Return those stored bytes for completed
POST replay and request lookup; do not add replay timestamps or live eligibility.
Validate the complete parent command and underlying required lineage before
returning a result. A completed lower receipt without its required HTTP command
link is corruption for this route, never permission to fabricate that link.

Exact completed duplicate handling occurs through a standalone recorded reader
before any effectful factory, initialization, worker reservation or filesystem
recapture. It returns historical results even after later source filesystem drift;
it never claims current authority. A changed body/action/host under an existing ID
is a conflict. A pending duplicate reports `pending_or_recovery_required`; it
does not call preparation, reconciliation or a provider. Do not infer currently
running versus crashed from an advisory memory map. Missing requests report
`request_not_found` without initialization. Corrupt required lineage reports
`recorded_evidence_invalid` without old-status fallback.

Completed commands return HTTP 200 with the exact stored envelope, including
actual rejected/failed outcomes. A recognized pending duplicate returns 202 with
a bounded non-authorizing diagnosis. Malformed input is 400/422, oversized body
413, local-boundary failure 403, missing binding/identity 404, and current conflict
409. Error responses are not success receipts. A same-ID body collision is 409
even if the original is completed. Errors before admission do not create success
records. An exception after claim may leave a pending command and retained worker;
it is never cleaned up in a generic `finally` handler.

## Execution and crash policy

Commands are finite synchronous host actions. The HTTP wrapper does not enqueue
a scheduler, automatic next phase or paid retry. A disconnected client or request
timeout does not authorize another call. If the same still-live invocation returns
and satisfies its existing settlement proof, it may commit its outcome; a new
process cannot reconstruct that invocation or infer the return from checkpoint
bytes. Duplicate lookup observes only committed history.

The start command keeps c1 preparation and consumption under the exact original
owner and pending phase. It may not use the host's `_prepared` dictionary as
durable authority, expose a prepared-base pause, or dispatch after owner change.
An interrupted preparation/admission remains blocked. This slice adds no HTTP
administrative recovery, abandonment, resume-preparation, reconciliation or
proposal-refresh command. Existing exact administrative recovery is history only;
it cannot release the command exclusion into a fresh execution grant.

At v3 scope stop, preserve the actual returned invocation, revoked tickets,
registration barrier, private remote-store absence and exact checkpoint/write
settlement proof. Only its atomic park makes the documented restart path valid.
After restart, the client must submit the exact parked proposal and explicit
scope decision. After terminal execution, source is still generation 1. Preview
and source decision each perform PR29's full capture under distinct fresh workers.
Only the accepted receipt-2 commit advances to generation 2. It enables no later
materialization, third phase, token or generated-source publication.

Transaction participants retain the owning service's durability policy. Start
reservation modifies Program/lifecycle under rollback journals FULL/EXTRA. V3
effects modify Program/control/lifecycle under their accepted rollback policy.
Acceptance modifies Program/lifecycle and keeps control/Safe/remote logically
read-only but writer-excluded, including supported WAL attachments. New journal
tables live in Program and do not justify adding another modified database or
changing PRAGMAs. Preserve scoped authorizers, lock order, bounded lock waits,
exact full-row release and live capture budgets through commit.

## Recorded projection

Use dedicated existing-file URI read-only connections and bounded query-only
readers. Do not construct the workspace's effectful acceptance/continuation
services, decode checkpoints, invoke Git, recapture source directories, initialize
schemas, refresh proposals, reconcile work or create missing databases on GET.
Compose existing PR29 standalone mixed-history validation with deliberate v3
version routing and a similarly inert command reader. Missing companions and
surviving v3 markers cannot fall back to legacy status.

Show original repository Git commit/tree, accepted source generation/hash/receipt
and separate derived execution Git identity in distinct typed fields. Execution
outcome, scope decision and source decision are distinct recorded fields.
`terminal_unaccepted`, `source_preview_recorded`, `source_accepted` and blockers
describe recorded state, never a grant. Any next-action hint is advisory and is
revalidated only on a new explicit POST. No source payload, raw private worker or
control row, remote identity, token, ticket or host filesystem path is public.

All public recorded projections/envelopes keep `source_bytes_verified=false`,
`filesystem_verified=false`, `current_authority_verified=false`,
`execution_authorized=false`, `source_acceptance_authorized=false`,
`materialization_authorized=false` and `automatic_execution=false`.
Historical receipt hashes may establish stored-byte integrity only.

One logical HTTP read shares a metadata budget of 1 MiB, 64 KiB per small record,
and keyset pages of at most 100 records (default 20). Opaque stored artifacts are
hashed in chunks of at most 65,536 bytes, at most 24,000,000 bytes each and
256,000,000 bytes cumulatively across the composed read. Do not reset budgets
per child reader, alias or repeated reference. Bounds precede BLOB retrieval,
parsing and canonicalization; hashing never decodes checkpoints. Keep stricter
live-capture and pinned-source policy limits separately. Unsupported/oversized
required history blocks rather than truncating proof or omitting a predecessor.

## Preserved boundaries

No changes to v1 acceptance's exact-owner rule, c1 pending proof, c2 schema/owner,
d2a's inert authority flags, PR28 route/settlement guards or PR29 complete preview
and first-receipt artifact linkage are authorized. Narrow journal integration is
not permission to bypass old consumers or replace either acceptance ledger.
No first-phase browser approval bridge, multi-user service, frontend, CLI,
workflow, v1/v2 migration, post-drift refresh, scheduler, deployment or generated
source publication is included. Full Product 42-to-44 and cumulative live-model
v3 remain unqualified. H01–H12 in the task own implementation acceptance.
