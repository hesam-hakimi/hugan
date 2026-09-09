# P3.5d-2c-1 — Local Product commands and host binding

Status: normative preimplementation definition. No runtime implementation or
qualification is credited. Owner: `UCA-20260908-P35D2C1-LOCAL-PRODUCT-COMMANDS`.
See the [task and evidence matrix](P3_5D2C1_LOCAL_PRODUCT_COMMANDS_TASK_2026-09-08.md).

## 1. Baselines and reconciliation

Accepted runtime is actual PR29 `f27c2693babcdf20145676328012b2d7576c5aa3`, tree
`29b763ff5af8a50348f7e987b341db65fac33bfa`. The documentation starting point is
the local delivery milestone commit `a04dd89ae3dd9f9db50755f8a4e7dda0248c952f`.
Its milestone `UCA-M-LOCAL-PILOT-1` stays approved/planned, not delivered.

A parallel definition was published on `feature/universal-coding-agent-continuation-api`
at `8799f39cbc97af179cebf5310521222879e9c5d1`, tree
`0226bd7e41018a0c8075c30a1593b2c70beca547`, directly from PR29. Its shared-reference
replacement failed with version conflicts. It selected entry only after actual
receipt-1 acceptance. This contract reconciles that valid documentation work with
the subsequently reconstructed delivery milestone and current owner instruction.
The old branch and exact historical task/contract bytes are retained. There is
one d2c-1 task, with the current task ID above; the old task ID is a superseded
definition, not a second implementation slice or an accepted implementation.

Retained decisions: synchronous finite actions; typed local input; durable
request/response linkage; no replayed effects; c1 preparation and v3 dispatch in
one owner episode; PR29 separate fresh preview/decision workers; inert full lineage.
Changed definition choices: include initialization and first-phase commands;
define a bounded first-phase review bridge; supply a real host configuration/
launch seam; expose only the already-supported same-live v3 reconciliation.
No existing acceptance gate is reopened or weakened by this definition.

## 2. Host configuration, lifecycle and local boundary

The implementation adds `product/local_product_binding.py` and an explicit
optional startup binding, separate from `ProductWorkspace.create`. The existing
`serve` command gets only `--local-product-binding <file>` and
`--enable-local-product-commands`. Both are necessary for new effects. No file,
no flag, an invalid binding or an unsupported transport leaves commands disabled.
An invalid supplied binding fails startup before provider probing or source work;
ordinary default serving remains available without this feature. The CLI/provider
selection already owned by the operator is reused; the browser never chooses it.
`--allow-remote-ui` cannot override this feature's loopback restriction.

The operator-owned UTF-8 JSON has exactly these fields, with no defaults that
select authority: `schema="uca-local-product-binding-1"`, `project_id`,
`display_name`, `source_root`, `origin_repository_url`, `origin_commit_sha`,
`origin_tree_sha`, `object_format`, `owned_execution_root`, `safe_state_root`,
`transport_id`, `edit_protocol`, `policy`, `programs`, `local_origin`.
`programs` is a nonempty list of at most 100 exact objects
`{program_id, requirement_sha256, plan_sha256}`. IDs use the bounds below;
`display_name` is at most 200 characters; Git hashes have the exact selected
SHA-1/SHA-256 length. `policy` is the existing strict `SafeModePolicy`, including
its trusted test profiles. Host policy may contain trusted test argv as already
supported; HTTP input may not. No credentials, provider module imports, arbitrary
hooks, tokens or shell snippets are added to this configuration format.

Load at explicit startup, maximum 65,536 bytes, duplicate-key/extra-field denial,
no symlink or multiple-link config file, and stable no-follow file identity.
Resolve roots once against the host, require absolute canonical distinct roots,
and reject a state/owned root inside the original source or an original source
inside a state/owned root. Pin actual store paths/device/inodes, artifact roots,
repository identity, Git/source policy, exact approved requirement/plan and provider
identity/capability in the private binding digest. The source root must match the
actual pinned origin; a mutable branch name is not its Base. Reuse the actual
shared Program/control/lifecycle/remote stores and one canonical Safe root across
first-phase and continuation calls. Do not silently switch between
`product/safe` and `web-runtime/safe`.

Persist an immutable binding descriptor and Program-to-project mapping in the
Program database during explicit enabled startup, using the new schema below.
Reopen only the identical mapping/configuration; changed roots, provider, policy,
plan or binding cannot overwrite it or adopt existing pending work. A new binding
requires a new project/Program identity and separately approved plan, outside this
task's update flow. There is no HTTP binding create/update/delete, hot reload,
TTL, cleanup or automatic migration. Missing/inconsistent companion stores block.
Shutdown must join or positively settle an already admitted finite call before
closing its stores; uncertain work retains its durable ownership. Startup never
requeues it. The current `close(wait=False)` behavior is insufficient for the new
coordinator and must not be reused as its settlement proof.

Use only synchronous providers allowed by PR28 `_host`, with its actual rejection
of `RemoteOperationLeaseAwareProvider`, `RestartReconciliationModelProvider` and
asynchronous test adapters. Publication is disabled. No configuration change,
probe, source attestation, materialization or provider invocation occurs on GET
or completed replay. Standalone readers use the persisted descriptor, not an
effectful workspace factory. `configured` and `commands_enabled` describe startup
configuration only; neither is pilot readiness or current operation authority.

For every new endpoint, validate the actual loopback peer and exact configured
Host authority including port; ignore forwarded host/address headers. Require
Origin to equal `local_origin` when present; reject null, multiple and cross-origin
values. A local nonbrowser client may omit Origin only with the same peer/Host
checks. POST requires `application/json` and `X-UCA-Command: 1`; no forms, CORS,
JSONP or credential exchange. Apply these checks also to existing effect routes
when serving an enabled bound project, so an old route cannot bypass the boundary.
This is a trusted single-operator local product, not multi-user authentication or
isolation from malicious code running as the same OS user.

## 3. Exact command inventory and types

Prefix `P=/api/local-product/v1/projects/{project_id}/programs/{program_id}`.
Paths have no wildcard filesystem component. Every POST body has exactly the
common fields and the selected row's additional fields. The common fields are:
`schema="uca-local-product-command-1"`, `request_id`, `action`,
`expected_binding_sha256`, `expected_revision`, `requirement_sha256`,
`plan_sha256`, `program_control_revision`, `task_control_revision`.
The task revision is explicitly null for initialization/first start, otherwise
the exact task revision where a task exists. The reconciliation row uses the
target command's task identity and revisions as comparisons, never a new grant.
Project/Program from the route are included in the canonical request digest.

| POST suffix | Literal action | Exact additional fields |
| --- | --- | --- |
| `/source/initialize` | `initialize_source` | `origin_commit_sha`, `origin_tree_sha` |
| `/phases/first/start` | `start_first_phase` | `before_sha256`, `generation` (0) |
| `/phases/first/scope-decisions` | `decide_first_scope` | `task_id`, `scope_proposal_sha256`, `scope_sha256`, `checkpoint_sha256`, `approval_id`, `approved` |
| `/source/first/previews` | `preview_first_source` | `task_id`, `result_sha256`, `before_sha256`, `generation` (0) |
| `/source/first/decisions` | `decide_first_source` | `task_id`, `quote_sha256`, `quote_revision` (1), `core_sha256`, `transition_sha256`, `before_sha256`, `generation` (0), `predecessor_receipt_sha256`, `evidence_view_sha256`, `approval_id`, `approved` |
| `/continuation/start` | `start_continuation` | `before_sha256`, `generation` (1), `acceptance_receipt_sha256` |
| `/continuation/scope-decisions` | `decide_continuation_scope` | `operation_id`, `task_id`, `admission_sha256`, `expected_epoch`, `expected_receipt_sha256`, `proposal_sha256`, `scope_sha256`, `approval_id`, `approved` |
| `/source/final/previews` | `preview_final_source` | `operation_id`, `task_id`, `terminal_receipt_sha256`, `before_sha256`, `generation` (1) |
| `/source/final/decisions` | `decide_final_source` | `operation_id`, `task_id`, `terminal_receipt_sha256`, `before_sha256`, `generation` (1), `candidate_sha256`, `revision` (1), `core_sha256`, `transition_sha256`, `predecessor_receipt_sha256`, `evidence_view_sha256`, `approval_id`, `approved` |
| `/requests/{target_request_id}/reconcile` | `reconcile_outcome` | `target_request_sha256`, `target_revision`, `operation_id` (null only when the target has no operation) |

`approved` is a required actual JSON boolean; no implicit true. IDs are ASCII
`[A-Za-z0-9][A-Za-z0-9._-]{2,127}`; operation IDs additionally use the lower
consumer's exact 32 lowercase hex characters. Digests are lowercase SHA-256;
Git object IDs use the pinned format. Revisions/epochs/generations are strict
nonnegative integers, at most 2^53-1; booleans/floats/strings do not coerce.
Unknown/missing fields, duplicate keys, NaN, unsupported schemas, null in a
nonnullable field and unknown enum values reject before effects. Limit streamed
body bytes to 65,536 even without Content-Length; reject an oversized declared
length before buffering. Depth <=8, <=64 keys/object, strings <=4 KiB, and all
stricter field limits apply before canonicalization. No request accepts paths,
repository URLs, policies, profiles, providers, evidence bytes, PASS objects,
checkpoint objects, owner tokens, invocation tickets or authority flags.

| GET route | Query allowlist | Meaning |
| --- | --- | --- |
| `/api/local-product/v1/projects/{project_id}` | none | Persisted redacted binding summary; configuration state, all readiness/authority flags false |
| `P` | `after_sequence`, `limit` | Recorded Program/source/command history; keyset page, default 20/max 100 |
| `P/operations/{operation_id}` | `after_sequence`, `limit` | Exact recorded continuation operation |
| `P/requests/{request_id}` | none | Exact recorded request or pending diagnosis |
| `P/evidence/{evidence_view_sha256}` | `after_chunk`, `limit` (default 1/max 16) | Previously committed bounded public review view; no generic artifact/path reader |

Reject GET bodies and unknown query fields. GET/HEAD/refresh never invokes a
command, repairs history, reserves/releases a worker, reconciles, materializes,
decodes a checkpoint, runs Git or constructs an effectful source service.

## 4. First-phase composition without transferring a v1 owner

Entry is an actually approved unsliced linear two-phase Program pinned by the
binding. Initialization uses `ProgramSourceAcceptanceService.initialize` with a
host-built `ProgramSourceIdentity` and a newly reserved worker. No browser-created
receipt or source snapshot is admissible. First start requires generation 0, no
first execution, no other work, and the exact initial source/plan/control binding.
Compose `ProductWorkspace.discovered_safe` and `ProgramOrchestrator.start_next_execution`
directly with the host repository/policy; the existing web request model containing
repository/ref/policy is not a transport adapter for this new command.

Do not use `ProgramSourceTransitionHost._first`, reuse its worker, retain a worker
while waiting for a person, or generalize candidate-2 to generation 0. Add a narrow
`LocalFirstPhaseDriver` for these marked Product requests. Its actual synchronous
start/resume invocation owns a process-local one-shot context and positive outer
return fact. At a scope stop verify exact task/thread/checkpoint/interrupt/write
shape, undecided scope, actual returned result and full current binding. Revoke
the context and prove no callbacks or operation/process/cancellable/pausable/paused
registrations and no remote lease/retirement, holding a bounded registration
barrier through the command completion/exact worker release. Empty maps in a new
process, an exception, a stored checkpoint or elapsed time cannot prove return.

Record a strict `uca-local-first-scope-proposal-1` containing Program/task/thread,
binding/plan/requirement, exact checkpoint and scope digests, Program/phase/execution
and Program/task control row digests, initial source/receipt, recovery-history
digest and the start command receipt. Only its explicit decision can call real
`ProgramOrchestrator.continue_execution` with `approved` unchanged. A fresh worker
must independently match this unchanged baseline. The first decision ends at a
proven terminal result or remains blocked; no partial execution retry or scope
proposal refresh. Original Safe v1 and line-addressed edit protocols stay separate
from Product/execution schemas. Failed, rejected or conditional work is never
eligible for source acceptance.

Avoid a circular receipt: the immutable first-result receipt binds the request,
actual result/checkpoint, semantic witness and exact released-owner digest but
does not include the proposal/quote or HTTP response. Construct that receipt,
then the proposal, then the response; the request row finally links the response.
All three records and the exact release commit in the same seal transaction.
The proposal's exact keys are `schema,project_id,program_id,task_id,thread_id,
phase_id,binding_sha256,plan_sha256,requirement_sha256,checkpoint_sha256,
scope_sha256,program_row_sha256,phase_row_sha256,execution_row_sha256,
program_control_row_sha256,task_control_row_sha256,before_sha256,
initialization_receipt_sha256,recovery_history_sha256,first_result_receipt_sha256`.
Its schema is `uca-local-first-scope-proposal-1`; every digest is nonnull.

First source preview runs after the completed, settled first execution. Under its
own fresh worker call actual v1 `prepare`, retaining the complete candidate-1
including its owner binding as immutable historical proof. Also create an explicit
`uca-local-first-source-core-1` by allowlisted assembly from the verified producer:
Program/task/thread/phase and source-host/binding identities; before/after/generation;
initial receipt; transition/evidence/checkpoint/result/phase-report hashes; the
complete Program, phase, execution, Program-control and task-control row digests;
plan/requirement; recovery-history digest; pinned source/Git/test policy digests;
actual origin/execution inventories, bytes/modes and filesystem identity digests;
and the settled first-result receipt. The core has no current-owner field.
Its exact keys are `schema,project_id,program_id,task_id,thread_id,phase_id,
host_sha256,binding_sha256,before_sha256,after_sha256,generation,
initialization_receipt_sha256,transition_sha256,evidence_sha256,
checkpoint_sha256,result_sha256,phase_report_sha256,program_row_sha256,
phase_row_sha256,execution_row_sha256,program_control_row_sha256,
task_control_row_sha256,plan_sha256,requirement_sha256,recovery_history_sha256,
source_policy_sha256,git_policy_sha256,test_policy_sha256,
origin_inventory_sha256,execution_inventory_sha256,filesystem_identity_sha256,
first_result_receipt_sha256`. Schema is `uca-local-first-source-core-1`;
generation is 0 and all listed digests are nonnull lowercase SHA-256.
The candidate supplies source/transition/evidence/checkpoint identities and its
already validated Program/phase/execution/control rows; hash each complete row
individually using the existing canonical encoder. Result/report hashes come
from the exact bounded bytes validated by `_capture`. The additional bounded
producer captures the full ordered recovery history and current attestor/policy/
inventory witnesses under the current capture gates. Inventory records bind
relative paths, types, full byte hashes and modes; filesystem identity additionally
binds pinned devices/inodes/link counts. No selected field or private path is
projected publicly. Every core input is independently reproduced at decision;
no nullable omission or last-known-value substitution is permitted.
Do not remove fields from, rewrite, reinterpret or accept the old candidate.

A `uca-local-first-source-quote-1` has exactly `schema,project_id,program_id,task_id,
quote_revision,core_sha256,preview_candidate_sha256,preview_request_sha256,
evidence_view_sha256`. It is revision 1; its digest excludes itself. The completed
preview response and witness bind that quote, all producer artifacts and the exact
released preview worker. Permit one quote per task/baseline, no post-drift refresh.
Persist the immutable public diff/test/review view at preview, then release only
after positive capture/child settlement. Preview does not accept source.

For a true first-source decision reserve a *different* current worker. Require
the exact completed preview request/response, intact quote/core/artifact ancestry,
shown evidence-view digest and unchanged full semantic/recovery baseline. Call
v1 `prepare` again under this new owner, obtaining a new candidate-1. Assemble
and compare the entire independently captured core with the reviewed core. Call
v1 `accept` on this **new** candidate with the same current worker and exact
reviewed transition. The new candidate's own full binding comparison remains
mandatory. The old preview candidate is never passed to `accept`; it must still
fail the existing owner-change regression if someone does so. Record both candidate
identities and the quote-to-current-candidate relation in the Product decision
receipt. No copied prior worker row or rewritten candidate establishes authority.

Add narrow exact typed command participation to v1's final initialization and
acceptance transaction: lower receipt/source CAS, immutable Product decision/
response and exact current-owner release commit together. Preserve all original
v1 validation and legacy behavior when no participant is supplied; no nested
committing public call, connection swapping or generic callable hooks. The
implementation may extract a private connection-scoped finalization body solely
to provide this composition. It may not replace `_binding`/`_capture`, edit v1
schemas or skip the second current recapture. Use Program/lifecycle rollback
FULL/EXTRA writer policy and logically read-only writer-excluded control/Safe/
remote attachments, including WAL protection and mutating-PRAGMA denial.

A false decision records a final rejected Product quote decision, without calling
v1 accept or inserting a fake source receipt. After either decision this quote
cannot be decided again under another request ID. Source rejection cannot be
turned into acceptance. A drifted recapture leaves pending/blocked ownership as
appropriate; it cannot create a replacement quote. First acceptance is an actual
receipt-1 at generation 1, compatible with c1 and PR29 predecessor verification.

This bridge is new bounded implementation work, not a claim that accepted PR29
already exposes it. Its proof obligations include original owner-change denial,
every semantic-field drift, preview/predecessor deletion, actual HTTP process
restart, live-return ambiguity and atomic receipt/response/release. If those
obligations require changing an existing authority comparison, stop that seam and
revise this contract; passing a narrower API must not be labeled LP02 complete.

## 5. Continuation, version routing and explicit reconciliation

After actual receipt-1 generation 1, one `start_continuation` command reserves one
fresh owner and composes actual materialization `begin/reconcile`, Base
`begin/reconcile`, v3 `admit` and `dispatch`. The c1 pending phase and exact original
owner remain unchanged until consumption; no HTTP pause after preparation. Bind
actual random materialization/Base operation IDs to this pending command before
their next effect. Do not pretend those lower `begin` APIs accept a caller-selected
operation ID. A crash in their independent allocation/recording gap remains blocked.
The host's `_prepared` dictionary is not restart authority. V3 owns its actual
scope settlement/release. Later exact scope decisions use v3 `approve_scope` and
its own fresh owner, proposal/epoch/receipt and current semantic checks.

Final preview and decision map unchanged to `ProgramSourceAcceptanceV2Service`.
Do not pre-reserve another worker around those methods. Preserve complete PR29
preview/request/response/witness ancestry, immutable evidence core, separate fresh
workers and atomic shared/versioned acceptance ledger/source head/response/release.
Receipt-2 at generation 2 enables neither materialization nor a third phase.

Version dispatch is deliberate: original unmarked v1 keeps existing behavior;
managed generation-0 first actions use the new finite driver plus unchanged v1
acceptance semantics; completed receipt-1 permits the exact c1/v3 composition;
existing c2 remains its exact-owner route and is unsupported for adoption here;
v3 scope and final acceptance use only their exact consumers. D2a is inert and
its complete closed history is checked where required. Unknown/partial/mixed
markers deny, including the independent locator, Safe guard, control registries,
checkpoint source metadata and copied accepted-source evidence. No catch-and-fall-
back to legacy and no inference that absent one table means legacy.

Persist a deny-only managed Program/task/root locator before the first marked
effect and bind it to the immutable project/Program mapping. Existing raw Program,
Safe/discovery and source effect routes for managed identities must consult that
mapping/locator, including copied-ID source-affinity cases, before work. Only the
exact live typed command context with its current claim may enter the selected
consumer. Use a distinct namespace; no c2 four-column registry change or v3 schema
reinterpretation. The locator is not authority. Missing companion marker data
blocks rather than restoring legacy eligibility. Narrow deny checks also prevent
new request IDs or old execution routes from bypassing a pending command after
administrative worker removal. Existing stop/control/recovery actions retain their
own concrete guards; they invalidate proposals and never restore command authority.

`reconcile_outcome` has a new exact request ID and names one exact target request,
payload and revision. It is not retry. Completed target: verify and reference its
historical response. Pending v3 start/scope target: only the same process's actual
original returned adapter may call existing `ProgramContinuationDispatchService.reconcile`
with its stored child request ID. It can finish a reversible seal failure without
provider/graph entry or fresh ownership. It must pass the existing returned-proof
and current-owner/barrier checks. Complete original and reconciliation responses
in that same seal transaction. Restart without that live object, interrupted c1,
first-phase invocation or source capture, drift and missing proof return a stable
blocked outcome; no general first-phase or acceptance recovery is added. Recording
that diagnosis does not release the original command head/worker or change source.
GET does not call even this limited reconciliation. No administrative recovery,
lease retirement, abandonment, proposal refresh or polling is bundled into it.

## 6. Durable requests, outcomes and crash semantics

Add exact versioned tables in the existing Program DB:
`local_product_bindings_v1`, `local_product_programs_v1`,
`local_product_requests_v1`, `local_product_heads_v1`,
`local_product_first_quotes_v1`, `local_product_decisions_v1`.
Use bounded immutable `program_source_artifacts` for records. Attest DDL/indexes
and deny unknown triggers/views/extensions. Binding and Program mapping are
immutable; heads have exactly `program_id,revision,last_receipt_sha256,
pending_request_id,next_sequence`. At initial binding revision and next_sequence
are 0; the receipt and pending request are null. Each admitted request, including
an observation, gets one unique immutable per-Program `sequence` from the next
sequence counter in its claim transaction. This counter is for history pagination,
not effect authority. Request key is `(program_id,request_id)`
across projects/hosts/actions: host partitioning cannot allow the same Program
request to run twice. Request columns are exactly `program_id,request_id,
project_id,binding_sha256,sequence,action,payload_sha256,state,child_map_sha256,
response_sha256,claim_sha256`. State is `pending` or `completed`; response is null
iff pending. `claim_sha256` is nonnull: for an effect it names its exact durable
worker claim; for reconciliation it names a typed observation-only target claim,
which contains no owner and cannot invoke an effect. `child_map_sha256` is also
nonnull from admission, initially naming an exact empty domain-tagged map when
the lower operation has not yet allocated its random ID. Child map and claim
are immutable digests once bound; extensions are
append-only domain-tagged linked records, not replacement of a claimed mapping.
One pending effect per Program; reconciliation records do not obtain an effect
head and may name only that exact target. Serialize reconciliation per target.

Canonical request = schema, route identities and every typed body field; no
tokens or live secrets. Child request IDs are `lp-` plus a 64-character digest
of domain/action/Program/request/binding, recorded explicitly. Before lower
effects commit the request claim and its exact fresh worker together, or join
the owning v3/acceptance fresh-worker claim transaction. Pin the exact child
request mapping; never choose latest operation/admission. A generic callback,
boolean or structurally similar journal participant cannot authorize SQL.

At command admission compare `expected_revision` to the head, exact Program/task
control revisions, binding/plan/requirement and action-specific expected source/
proposal. Keep the head revision unchanged while pending and advance by one with
its completed outcome, including actual rejection/failure. Reconciliation has
its own immutable observation revision and cannot make a target eligible. Other
control changes need not update this head: their actual revisions and proposal
baseline must still match at effect admission and final commit.

V3 and final source command completion must join the lower outcome and exact
release commit via a private exact typed transaction participant with allowlisted
SQL. First execution's existing Program/Safe writes can precede its final command
seal; only a still-live returned driver plus exact durable checkpoint/Program
proof may seal response/revision/release. If the process dies in that gap, prior
lower writes remain evidence and the command/worker remain blocked. Never call a
partial lower result a completed HTTP command. V1 source-head advancement uses
the atomic participation in section 4, not a best-effort response cache. Preserve
the different owning transaction policies; no provider/long test process in a
write transaction, no expanded general authorizer, no PRAGMA repair.

Replay order: validate local transport and typed payload; resolve persisted exact
project/Program mapping; use a bounded standalone request reader before any
effectful factory. Same ID/different canonical content, action or binding is 409.
Same ID/completed returns exact canonical stored response bytes after complete
linked validation, even after later filesystem drift; no fresh token, worker,
ticket, eligibility calculation or recapture. Same ID/pending returns a bounded
202 diagnosis, never work. A new effect ID while pending is 409. Missing or
corrupt required history denies; do not fill it from a lower success or current
capture. Normal operator decisions always use new explicit command identities.

Commands are finite synchronous HTTP actions. They do not enqueue a scheduler.
Client disconnect does not authorize cancellation/re-execution; a still-live
action may finish its already admitted work and commit only after its proof.
Before claim commit a crash leaves no claim; after claim and before outcome the
pending ownership remains. After outcome commit lost response is handled only
by historical replay. Pending/ambiguous state remains blocked after restart or
operator removal of a worker. No time-based adoption or inferred successful
return. Test actual process termination at lower-write and journal boundaries.

## 7. Response allowlists, status and bounds

Completed envelope has exactly `schema="uca-local-product-response-1",project_id,
program_id,binding_sha256,request_id,action,request_sha256,request_status,
command_revision,receipt_sha256,outcome,result,authority`. `request_status` is
`completed`. Outcome enum is `initialized,scope_required,terminal_unaccepted,
source_preview_recorded,source_accepted,rejected,failed,blocked,reconciled`.
These are historical outcomes, not current action grants. `receipt_sha256` names
the Product receipt, with exact child response/receipt links; it is not a source
receipt. `result` uses only the action's fields below, with explicit null for
unavailable fields (never a missing field or invented PASS):

| Action group | Exact result keys |
| --- | --- |
| initialize | `generation,source_sha256,initialization_receipt_sha256` |
| first start/scope | `phase_id,task_id,thread_id,execution_status,scope_proposal_sha256,scope_sha256,checkpoint_sha256,result_sha256,tests_summary,reviewer_verdict,evidence_view_sha256` |
| first preview | `task_id,quote_sha256,quote_revision,core_sha256,transition_sha256,before_sha256,after_sha256,generation,predecessor_receipt_sha256,evidence_view_sha256` |
| first decision | `task_id,quote_sha256,approved,source_receipt_sha256,generation,source_sha256` |
| continuation start/scope | `operation_id,phase_id,task_id,thread_id,admission_sha256,epoch,v3_receipt_sha256,proposal_sha256,scope_sha256,execution_status,result_sha256,evidence_view_sha256` |
| final preview | `operation_id,task_id,candidate_sha256,revision,core_sha256,transition_sha256,before_sha256,after_sha256,generation,predecessor_receipt_sha256,terminal_receipt_sha256,evidence_view_sha256` |
| final decision | `operation_id,task_id,candidate_sha256,approved,source_receipt_sha256,generation,source_sha256` |
| reconciliation | `target_request_id,target_request_sha256,target_status,target_response_sha256,disposition` |

`execution_status` is null or exactly `starting,awaiting_scope_approval,running,
completed,failed,cancelled`, matching actual `ProgramExecutionStatus`. A completed
command may expose a scope stop or proven terminal state only; starting/running
are recorded status values and cannot prove settlement. Actual Safe `blocked`
maps to Program `failed`; preserve its failure evidence, never a successful
terminal result. Unrecognized values block. `tests_summary` is null or
`{profiles:[{profile_id,passed,exit_code}],
all_required_passed}`; no command/argv/stdout. Reviewer verdict is null or
`PASS,FAIL,PASS_WITH_CONDITIONS`, never coerced. Reconciliation disposition is
`historical_completed,original_live_seal_completed,original_live_evidence_missing,
unsupported_target,proof_invalid`. False source decisions return original
generation/source with null source receipt. A failed/blocked outcome never
advertises an accepted source action.

`authority` has exactly these false fields on every response/read:
`source_bytes_verified,filesystem_verified,current_authority_verified,
execution_authorized,source_acceptance_authorized,materialization_authorized,
automatic_execution,ready_for_supervised_pilot,real_project_pilot_validated`.
An effect receipt records the completed event; these flags prohibit treating
its public representation as present authority. D2a's separate `consumer_bound`
and `execution_authorized` remain false.

Pending envelope has exactly `schema="uca-local-product-pending-1",project_id,
program_id,request_id,request_sha256,request_status="pending",code,
command_revision,authority`. Code is `pending_or_recovery_required`; do not infer
live versus crashed from memory. Error envelope has exactly
`schema="uca-local-product-error-1",code,message,project_id,program_id,request_id,
retry_effect=false`; unresolved IDs are null, messages are fixed public text.

| HTTP status | Stable code families / meaning |
| --- | --- |
| 200 | Completed historical command, actual rejection/failure included; valid recorded GET |
| 202 | `pending_or_recovery_required`; acknowledged record only, no second invocation |
| 400 / 422 | `invalid_json` / `invalid_command`; byte/shape/schema/type denial before claim |
| 413 | `request_too_large` |
| 403 | `local_boundary_denied` |
| 404 | `project_not_found,program_not_bound,request_not_found,operation_not_found,evidence_not_found` |
| 409 | `request_conflict,revision_conflict,program_busy,binding_changed,source_changed,policy_changed,proposal_changed,unsupported_version,recorded_evidence_invalid,recovery_required,evidence_view_unavailable,unsupported_program,source_decision_final` |
| 503 | `local_commands_disabled,unsupported_transport,store_unavailable` |

Preclaim errors create no success receipt. Once claim commits, an unexpected
exception cannot erase the pending request or release a worker in `finally`.
No raw exception, provider output, SQL, private path, raw control/owner row,
remote identity, token or ticket reaches public errors/logs. `Cache-Control:
no-store` applies to all new responses, including errors and evidence.

Recorded status schema `uca-local-product-status-1` has exactly `schema,project_id,
program_id,binding_sha256,command_revision,program_status,program_control_revision,
task_control_revision,requirement_sha256,plan_sha256,original,accepted,execution,
scope_decision,source_decision,requests,next_cursor,blockers,authority`.
`original={commit_sha,tree_sha,object_format}`;
`accepted=null|{generation,source_sha256,receipt_sha256}`;
`execution=null|{schema,operation_id,phase_id,task_id,thread_id,status,
derived_commit_sha,derived_tree_sha,result_sha256}`. Decision projections are
null or `{request_id,approved,proposal_sha256,receipt_sha256}`. Request page items
are `{sequence,request_id,action,request_status,outcome,response_sha256}`.
Blockers are a list of the stable codes above. No next-action hint is authority.
Binding summary has exactly `schema="uca-local-product-project-1",project_id,
display_name,configured,commands_enabled,program_ids,binding_sha256,authority`;
Program IDs are sorted and bounded by the pinned configuration. Operation GET uses the
same status shape filtered to the exact operation and still validates full ancestry.

Compose deliberate generation-0/v1 recorded validation, v3 stored records and
PR29 `source_transition_status`/completed-request/terminal-history checks. PR29's
reader currently requires generation 1 or 2: do not invoke it for generation 0
and catch its error as legacy success. Add the bounded generation-0/first-quote
reader explicitly. Preserve every mixed receipt, complete preview and predecessor
artifact link. Invalid/unknown-version or missing companion data blocks all
dependent results, including replay after acceptance/rejection. No old-reader
fallback. Existing Program execution GET for managed Programs uses this projection
or a clear unsupported-route denial, never the old reader's incomplete v3 view.

Public review views are committed during the effect's capture, not built on GET.
Use exact keys `schema,view_kind,program_id,task_id,core_sha256,source_evidence_sha256,
chunks,redacted,complete` where chunks are `{index,relative_path,kind,text}` and
kind is `scope,diff,tests,review`. No arbitrary artifact reference or absolute path.
Schema is `uca-local-product-evidence-view-1`; `view_kind` is `scope` or `source`.
`core_sha256` is explicitly null for a scope view and is the exact core for a
source view. `relative_path` is null for nonfile review material. `redacted` and
`complete` are actual booleans; chunk indices are contiguous nonnegative integers.
Evidence GET returns exactly `schema="uca-local-product-evidence-page-1",
evidence_view_sha256,total_chunks,next_chunk,view,authority`. `view` uses the
view schema above with the selected chunks; the digest always refers to the
complete stored view, never a hash of the page. Validate the full bounded stored
view before projection. `next_chunk` is null at the end, otherwise the first
unreturned index. An absent `after_chunk` starts at 0; a supplied index selects
strictly later chunks. This paging cannot turn an incomplete proof into complete
evidence or synthesize a new approval identity.
Public view hash binds sanitized bytes separately from original evidence hashes.
Never hide truncation: an incomplete/oversized/unreviewable view blocks creation
of a decision-ready quote or final preview response. If redaction removes material
needed to review an exact change, return `evidence_view_unavailable`; do not enable
approval of hidden content. No raw credentials or private provider diagnostics in
source/test/review presentation. This slice defines the API view, not UI controls.

One logical composed read shares 1 MiB metadata, 65,536 bytes/small record, depth 8,
100 maximum history rows and keyset limits. Public response <=1 MiB, individual
view chunks <=65,536 UTF-8 bytes, complete view <=1 MiB. Opaque retained artifacts
are hash-checked without decoding source/checkpoints, in <=65,536-byte chunks,
<=24,000,000 bytes each and <=256,000,000 cumulative per logical read. Shared
budgets span child readers, repeated references and aliases; a stricter cached
bound still applies. Required proof is complete within budget or denied, never
silently paged away. SQL retrieval pins exact selected ID/type/encoding/length
and caps bytes in SQL; preflight alone is insufficient. Preserve PR28 checkpoint/
pending-write and PR29 cumulative live capture, source/Git/filesystem bounds.

## 8. Delivery meaning

D2c-1 owns LP01's configuration/launch/API reopening seam, LP02's complete bounded
command inventory and LP05's API durability/denial/projection evidence. LP01's
operator-ready packaging and LP05's final UI/complete journey remain delivery
closure work. LP03 belongs to d2c-2; LP04 and LP06 require later separately defined
complete Product qualification/handoff, including the actual candidate real-model
journey. No successful host fixture or standard Live v1 run substitutes for that.
RP01 read-only onboarding then RP02 one separately approved bounded change remain
approved future direction, private project mapping, and uninstantiated tasks.
Broader Milestones 4/5 are not blanket pilot prerequisites. Required here are only
local binding, strict explicit commands, real settlement, durable outcomes,
source preservation and the separate evidence/integration gates.

No UI implementation, new runtime/test execution, paid CI/Live/Web/model work,
customer access, credentials or source changes occur during this definition.
No migration, post-drift refresh, scheduler, arbitrary shell, third phase, ETL,
production deployment, main/PR6/root todos change, history rewrite or generated
source publication is included. Implementation acceptance remains entirely future.
