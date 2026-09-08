# P3.5d-2c-1 — Local continuation API from accepted generation 1

Task ID: `UCA-20260908-P35D2C1-LOCAL-CONTINUATION-API`.
Status: documentation-only definition; runtime implementation, independent
acceptance and platform qualification have not started. Canonical companion:
[HTTP command and recorded-status contract](P3_5D2C1_HTTP_COMMAND_AND_STATUS_CONTRACT.md).

## Accepted starting point

Use actual accepted PR29 integration
`f27c2693babcdf20145676328012b2d7576c5aa3`, tree
`29b763ff5af8a50348f7e987b341db65fac33bfa`, merged 2026-09-08T18:46:55Z.
Its ordered parents are `95096565d85640ea471182fc0b421e124667b73b`, then
`b0e1a9dd590ba33a65d42868553bcada15c432ee`. Separate preview
`9f816b01cae2d60e8241b32c4a7b43d61d6afabe` has the same tree and parents.
The new definition branch is
`feature/universal-coding-agent-continuation-api`; its first documentation commit
must have actual PR29 as its sole parent. Verify the published commit/tree/ref and
exact changed blobs before implementation. No integration-target update is part
of definition publication. Do not create a documentation-only PR: the accepted
workflow triggers would run normal CI and paid Live on that PR.

PR29 is complete, not an open implementation gate. Its initial independent
report remains BLOCKED (F1 completed-preview ancestry and F2 retained receipt-1
artifacts); the separate correction report is PASS for exactly the corrected
source/tree. Author and independent correction each ran 168 submitted cases;
the independent reviewer also reused all five original probes unchanged, now
denying without effects. CI446/Live197 attempt 1 qualify only the corrected
preview; CI passed 1812 cases in each Python leg. These scopes overlap. Technical
PASS is not human GitHub APPROVE or an audit. PR28, PR27 and PR26 remain accepted
history with every failed report and earlier-tree qualification retained.

## Explicit scope selection and the remaining Product gap

This task implements an API journey starting from an **actually accepted v1
receipt-1 at generation 1**, represented by 43 in the deterministic fixture.
It ends with a separate candidate-2 decision accepting tested/reviewed 44 at
generation 2. Generation numbers and hashes are authoritative; 42/43/44 are
fixture values, never service eligibility constants. The Program is approved,
unsliced, linear and exactly two phases; the first is complete and accepted, and
the second is pending with no execution binding at entry.

This narrows the parent's originally grouped API outcome. Inspection at PR29
shows `ProgramSourceTransitionHost._first` retains the first-phase worker across
`start_first_phase`, `decide_first_phase_scope`, `preview_first_phase_source` and
`accept_first_phase_source`. V1 candidates bind that exact worker. The web
runtime normally releases each request's worker. Neither first-phase host method
is therefore safe to expose as a sequence of browser commands that wait for a
person. Candidate-2 currently covers terminal v3 at generation 1 only.

The selected entry precondition preserves those accepted contracts. A host/test
fixture may produce real 42-to-43 acceptance through the accepted Python host,
then close that episode before constructing the API runtime. It must not seed
receipt rows, accept caller-supplied proof, or claim that the setup was HTTP work.
Generation 0 and first-phase preview/accept requests are unsupported by these new
routes. Existing legacy routes do not become a workaround for source acceptance.

The full Product/browser 42-to-44 journey remains open. A separate bounded design
is required for first-phase scope/preview/accept across worker episodes before
that outcome can be implemented or claimed. This task does not instantiate that
prerequisite, generalize candidate-2 to v1, or mark the parent's full journey
complete. D2c-2 remains planned and uninstantiated; its future definition must
state whether it consumes this restricted API and must retain the first-phase gap.

## Deliverable

Add an opt-in, host-configured local HTTP surface for four explicit finite
commands: prepare/admit/start continuation, exact scope decision, source preview,
and exact source decision. Provide standalone bounded recorded status and request
lookup. Compose actual c1 materialization/Base preparation, PR28 v3 execution and
PR29 acceptance, with no synthetic result, checkpoint, settlement or PASS evidence.

Preparation, admission and initial dispatch are one worker episode and one start
command. They may end only at the actual v3 settled boundary; there is no browser
pause between preparation and consumption. Later scope, preview and acceptance
each use the fresh-worker rules of their owning service. Execution, scope approval
and source acceptance remain separate authorities and separate command types.

Implement durable HTTP command identity and exact completed replay as specified
in the companion. The command journal is a transport binding, never a new worker,
invocation capability, acceptance ledger or replacement for underlying lineage.
Command completion must join the underlying outcome/response/exact-release
transaction. A second, best-effort response-cache commit is not sufficient.

The host supplies immutable repository, origin, requirement/plan, state paths,
policy, test profiles and synchronous transport bindings. Browser input supplies
only explicit intent and exact expected public identities. No path, provider,
destination, command, raw owner token, invocation ticket or source bytes are
accepted. Default configuration has no effectful continuation binding.

## Permitted implementation area

All paths are under `universal-coding-agent/`. Expected primary changes are a
small `product/` API coordinator/command store/recorded reader, typed models and
new routes under `src/universal_coding_agent/web/`, and explicit workspace/host
construction. Narrow connection-scoped completion integration may be needed in
`program_continuation_dispatch.py`, its store, and acceptance-v2/store. Preserve
their original public signatures/behavior for non-HTTP callers where possible.
Any added optional hook must be a private exact typed journal participant with
allowlisted SQL, not a general callback capable of authorizing effects.

Tests belong in focused HTTP/command/recorded-reader modules plus minimal
regressions for touched lower-layer seams. Update this task, contract, parent
design/matrix and ROADMAP with actual candidate evidence later. No workflow,
frontend, CLI, scheduler, old-v1/v2 migration or broad Git-helper refactor belongs
in this implementation. If atomic composition requires a wider authority change,
revise the concrete task before coding that change; do not weaken accepted gates.

## Acceptance families

These are future gates, not tests run by this definition. Bind every observation
to the exact candidate commit/tree and distinguish submitted tests independently
executed from new independent probes. Record counts without adding overlapping
author, reviewer, CI and Live scopes.

| Family | Required executable evidence |
| --- | --- |
| H01 — actual HTTP continuation | Real host setup produces accepted 43; HTTP start prepares/consumes real c1 proof, runs actual discovery/Safe to an actual scope stop and atomically releases. Restart the Product process, GET recorded evidence, submit exact scope decision to actual tested/reviewed 44, preview under a fresh worker, restart again, then separately accept 44 at generation 2. Assert original 42 and immutable accepted material 43 unchanged. Label host setup separately from HTTP actions. |
| H02 — strict local boundary | Default-disabled/unbound host, wrong Program/project/Host/Origin, nonloopback peer, proxy headers, content type, duplicate/unknown fields, coercible booleans/integers, oversized streamed bodies and caller paths/tokens reject before service construction, reservation or provider work. A correctly bound loopback client succeeds. |
| H03 — durable request identity | Independent processes race identical and differing bodies under one request ID. One intent wins; changed action/body/Program binding rejects. Completed duplicate POST and GET return exact stored response bytes with no initialization, recapture, provider, owner or source effects. Verify after restart and later filesystem drift. |
| H04 — start preparation episode | Reservation and pending command commit atomically. c1 begin/reconcile, Base begin/reconcile, admit and dispatch use that same private owner. Crash after each filesystem/admission boundary remains pending/blocked without adoption or replay. No prepared-base park or client resume endpoint exists. |
| H05 — command/outcome atomicity | SIGKILL before and after claim, scope park, terminal seal, preview completion and source decision commit. Before completion, pending/ambiguous ownership and source state are retained; after completion, command response, underlying receipt and exact release agree. Lost HTTP response cannot produce an outcome/cache split or re-execution. |
| H06 — current authority and exclusion | Exercise source/control/plan/host/policy drift, pause-resume, administrative recovery, concurrent workers/control actions, registration barriers and retained remote leases. Old proposals and changed binding deny; empty process-local maps are not proof. Preserve WAL writer exclusion and existing journal/synchronization policies for each service. |
| H07 — separate decisions | False scope decision produces actual rejection; failed test, FAIL/conditional review and rollback never advance source. Source rejection remains final for that candidate. Terminal execution alone stays generation 1; preview alone does not accept; receipt-2 enables no third phase or materialization. |
| H08 — complete lineage | Reuse PR29's missing-preview and missing-first-receipt artifact probes through the HTTP surface, plus deleted/corrupt HTTP parent request/response/child links. Preserve exact completed v3 requests and c1/v1 artifacts. Missing proof cannot be repaired by GET or by replaying an effect. |
| H09 — standalone reads | Fresh process reads existing stores with effectful imports/constructors, checkpoint decoding, filesystem source capture and provider entry made fatal. Missing stores are not created. Database/file bytes remain unchanged for successful, corrupt, oversized and missing-history reads; all authority/materialization flags remain false. |
| H10 — bounds and redaction | One cumulative metadata/artifact budget per logical composed read; bounded keyset pages and selected-row retrieval; no whole-table scans or hidden unbounded response. Test 64-KiB/1-MiB metadata, 24,000,000-byte artifact and 256,000,000-byte aggregate limits and stricter existing live-capture limits. Raw tokens, tickets, control rows, credentials and arbitrary exception text never reach responses or logs. |
| H11 — frozen routes and scope | Legacy start/continue/Safe/acceptance still deny v3 and surviving-marker corruption. C1 pending and c2 exact-owner behavior, d2a inert flags and accepted PR28 routing remain. New routes reject generation 0, receipt-2 start/materialization, third phase, slicing and caller configuration. No frontend/CLI/workflow change or full browser-journey claim. |
| H12 — delivery evidence | Focused author qualification and compatibility for changed seams; separate bounded independent correctness/security review; corrected-source normal CI/Live and Web when triggered; inspect literal checkout/tree, required child outcomes and aggregate enforcement. Normal Ready plus expected-head-locked integration only after the implementation candidate passes. Definition publication alone claims none of these gates. |

Use actual HTTP requests and separate processes/stores for the positive path and
crash/race claims. Mocks may exercise malformed inputs and denial seams, but may
not substitute for accepted source, the graph's stop, real subprocess tests,
review provenance, settlement or final receipt-2. Do not rerun accepted PR26–PR29
gates merely to accumulate credit. Standard Live remains v1; no cumulative
live-model v3 or Product journey is qualified by those standard results.

## Completion and next action

Definition completion means exact documentation bytes, sole-parent history,
published branch and preserved reference preimages/readbacks are observed. It
does not mean implementation acceptance. After that verified definition, implement
only this bounded API slice from its exact head, then submit its first candidate
through a normal Draft PR with separately scoped review/platform evidence.

Speak Persian with Hesam; engineering content remains English. Existing bounded
authority persists without routine owner reconfirmation. Exclude main, PR6, root
todos.md, AskTD/ETL/customer work, credentials, deployment, history rewriting and
generated-source publication. Root September1 remains unverified and ignored.
No background monitoring or future asynchronous work is claimed by this record.
