# PR26 independent technical review — P3.5d-1

**Verdict: BLOCKED for the bounded recorded-source visibility and legacy-routing contract. Two P2 metadata-integrity defects remain.**

The submitted source passes the existing regressions and its recorded platform qualification. Those successes do not cover the two independently observed incomplete/inconsistent metadata cases below. Neither finding claims unauthorized provider execution, compromised-host resistance, a regression of PR25's accepted c2 authority engine, or a whole-repository security audit.

## Exact independent source and scope

| Identity | Observed value |
| --- | --- |
| Repository / PR | `hesam-hakimi/hugan` / PR26 |
| Independent agent | `/root/pr26_independent_review` |
| Own detached checkout | `/workspace/scratch/2f614e332d31/pr26-independent` |
| Reviewed HEAD | `cc391fb3da9bd914a7425e028877e53d57db30ec` |
| Reviewed tree | `af7a2db6b0a4e09e807b90ef8e57c05f4e6ba82e` |
| Sole HEAD parent / definition commit | `ca91d963a3aa2138fbf1db989a49b442f86bce4e` |
| Definition tree | `06788ea5e603907eca7dc490122dd66ba1e749f5` |
| Sole definition parent / accepted base | `5d1bb45c28689131b9b538e798d3b8e7aa25742c` |
| Accepted base tree | `2433238df764274bcf5ba6cc1639913b496fd3e6` |
| Target | `feature/universal-coding-agent-structured-edits` |
| Recorded qualification preview | `87d705d1f4df210e8e7a54b835a4c46e8c8c0264` |
| Preview tree | Same reviewed tree |
| Preview ordered parents | Accepted base, then reviewed HEAD |

Local Git verified the base/definition/HEAD chain and trees. The preview object is absent from this local repository: the initial local `git show` including it failed with `bad object`. Preview identity was instead checked against the retained GitHub Git-data response `pr26-evidence/platform-3.json`, and each of the four actual job checkout logs. The preview is not the submitted HEAD or an actual integration. No branch/ref was advanced; a detached worktree was created as requested.

The entire base-to-HEAD comparison contains 12 files, 1,523 insertions and four deletions. All changed hunks were read, including the seven implementation/test files and five documentation/report files:

- `src/universal_coding_agent/product/program_source_status.py`
- `src/universal_coding_agent/web/app.py`
- `tests/test_program_source_status.py`
- `web/src/App.tsx`, `web/src/programSource.test.tsx`, `web/src/types.ts`, `web/src/viewModels.ts`
- `PROGRAM_SOURCE_VISIBILITY.md`, `ROADMAP.md`, the P3.5d-1 task and both retained PR25 reports.

Paths in this report are relative to `universal-coding-agent/` unless stated otherwise. Actual relevant consumers inspected include Program table definitions, v1 execution/continuation and same-Base evidence handling; source initialization, candidate/approval/acceptance producers; execution-Base and v2 admission schemas, dispatch reconciliation/result persistence; workspace execution-service construction; web reservation/release and HTTP handlers; lifecycle ownership CAS; and frontend loading, busy polling, rendering and start/continue selection. The actual deterministic cumulative fixture and status assertions were inspected. This is not a fresh line-by-line audit of every unchanged c2 implementation module.

The complete current d1 checkpoint, state JSON, master/status, continuation, review task and observed receipt were read from the supplied current copies. Exact duplicate paragraphs in master/status were deduplicated for reading without dropping distinct history. The complete accepted c2 checkpoint was byte-verified as an embedded span of the read master. All 13 receipt-described local artifacts match the receipt's lengths/hashes. All 12 submitted-file identities match this checkout. Both PR25 reports match their original copies byte-for-byte:

| Historical report | SHA-256 |
| --- | --- |
| Initial BLOCKED | `0864ea1112b42c280e2d7dc3fadeb6cd86adfc52421312496c88ae1684f86945` |
| Final bounded correction PASS | `ee5f278bc6e8a44e9fbad5c08782c49da825cae02c54e01532370a8aeb1ee737` |

Both P3.5c contracts and parent/c2 task definitions were read. Their frozen submission-time gate wording is historical. PR25 acceptance is preserved within its own documented limits and does not qualify these changed bytes.

## Findings

### F1 — P2: A contradictory terminal dispatch is presented as recorded execution history

**Locations:** `product/program_source_status.py:160–164,320–327`; consumer `web/src/App.tsx:1660–1665`. Relevant producer: `product/program_source_dispatch.py:701–770,774–800`.

The reader omits `program_executions.status` and `safe_status`. It checks that the dispatch state's string belongs to `DISPATCH_STATES` and that accepted tasks are terminal, but never checks the converse relationship between the dispatch state and its persisted execution status. Consequently, an inconsistent but recognized state passes the purported coherent-record projection.

A bounded check copied the database left by the independently executed actual HTTP fixture after its v2 task reached scope approval. Only the copy was changed:

```sql
UPDATE program_source_dispatches SET state='terminal';
```

The existing execution row remained `status='awaiting_scope_approval'`, `safe_status='awaiting_scope_approval'`. `program_source_status()` nevertheless returned `status='recorded'` and a dispatch with `state='terminal'`. `ProgramSourcePanel` renders that value as **Execution terminal**. The copied DB bytes remained unchanged by the subsequent reads. No metadata hash was altered or recomputed and no provider/service was invoked by this check.

This is an internally contradictory recorded state, not merely a stale filesystem observation. The actual producer's `reconcile()` computes a terminal target only for an actual terminal checkpoint; `_record()` writes completed/failed execution state and the dispatch update commits in the same Program transaction. A recorded terminal dispatch paired with a still-pending scope execution cannot be explained by that legitimate transaction gap. Reading those Program scalar fields is possible inside the existing read-only snapshot and does not require current filesystem, checkpoint-file or ownership requalification.

**Required correction:** validate the durable dispatch/execution state relationship, including terminal states and any legitimate explicit lifecycle dispositions, before returning apparently coherent history. Add a regression for a recognized but impossible state combination; preserve normal admitted, scope-stop, in-flight, failed terminal and separately accepted states. Do not solve this by loading effectful services or weakening c2 recovery.

### F2 — P2: Missing preparation plus admission silently removes a known derived execution from history and permits legacy routing

**Locations:** `product/program_source_status.py:165–191,335–345`; frontend `web/src/viewModels.ts:403–414`; runtime `web/app.py:1208–1209,1386–1387`. Relevant persisted schema/producer: `product/program_orchestrator.py:157–178`, `product/program_source_dispatch.py:388–446`.

The projection discovers dispatches only by matching execution task IDs, and detects a missing dispatch only if a preparation row still exists. It never classifies or rejects the executions left unmatched after both lookups. The surviving execution's derived `expected_base_sha` is ignored unless a dispatch was found.

A second disposable copy of the same actual scope-stopped fixture was changed with:

```sql
DELETE FROM program_source_dispatches;
DELETE FROM program_execution_bases;
```

The initialized Program, accepted generation-one lineage, phase-two execution and its derived Git Base remained. The reader returned `status='recorded'`, `dispatches=[]`. Calling `require_legacy_program_route(copy, program_id, phase_two_task_id)` **returned without rejection**. Its advanced-generation condition applies only to start (`task_id is None`); continuation relies solely on the now-empty projected dispatch list. The frontend makes the same decision. The read preserved copied DB bytes.

This is a two-record-loss case, not a claim that normal c2 admission partially commits these records. Missing/corrupt persisted required metadata is explicitly in the d1 contract and existing negative-test scope. Existing tests cover deleting either row individually; they miss their combined absence. In this concrete fixture the surviving derived execution Base differs from the verified recorded origin, so there is still metadata contradicting classification as ordinary original-Base v1 continuation. The new guard must not turn absence of its lookup records into an affirmative legacy classification.

**Required correction:** account for every relevant execution in initialized source history. Establish a bounded, explicit legacy classification using the existing original-Base contract and available persisted evidence; reject unresolved/derived bindings whose required admission/preparation records are missing. Add a regression for this combined loss and preserve generation-zero/ordinary v1 cases. No control-store migration, service construction, source-byte loading or new execution authority is required merely to reject inconsistent history.

**Impact limit:** this check called the pure metadata reader and legacy guard, not the effectful HTTP continuation. The original fixture also retains its legitimate worker reservation, and c2's shared-control/Safe authority defenses remain unchanged. This report does not claim that deleting these two records bypasses those later defenses or results in a provider call. The independently demonstrated failure is incomplete product history and incorrect early route classification.

## Independently executed validation

A separate editable environment was built with cached dependencies:

```bash
uv venv .venv
uv pip install --offline --python .venv/bin/python -e '.[dev]'
```

Interpreter: `/workspace/scratch/2f614e332d31/pr26-independent/universal-coding-agent/.venv/bin/python`. Imported package: `/workspace/scratch/2f614e332d31/pr26-independent/universal-coding-agent/src/universal_coding_agent/__init__.py`. Python is 3.12.13 and SQLite 3.53.1. Test subprocesses use that interpreter and editable checkout.

The exact existing-test command, from the independent checkout's `universal-coding-agent/`, was:

```bash
.venv/bin/python -m pytest -q \
  tests/test_program_source_status.py \
  tests/test_web_api.py \
  tests/test_program_source_dispatch.py \
  tests/test_program_execution.py \
  tests/test_lifecycle_reservations.py
```

**Observed: 166 passed, one warning, in 158.38 seconds; exit 0.** The warning is the existing Starlette/AnyIO deprecated `BlockingPortal` alias. This includes all 31 new status cases, 16 existing web API cases, 69 c2 dispatch cases and relevant v1/lifecycle regressions. The original PR25 independent probes were not rerun.

The real cumulative status fixture exercised initialization, 42-to-43 acceptance, fresh-process reads, restart, actual discovery/scope stop, terminal-but-unaccepted 44, and separate generation-two acceptance. Fresh-process reads retained source/artifact/provider-log/DB bytes and did not load the dispatch or Safe service modules. Actual HTTP negatives rejected intact v2 continuation and advanced-source start without claiming another owner's reservation; queued workers rechecked metadata before workspace service construction and released only their own ownership. These are meaningful passing results, but not tests of F1/F2.

| Additional independent check | Observed result |
| --- | --- |
| `.venv/bin/ruff check .` | All checks passed, exit 0 |
| `git diff --check 5d1bb45c28689131b9b538e798d3b8e7aa25742c HEAD` | Passed, exit 0 |
| Tracked source status | Clean before/after verification |
| Two copied-DB metadata checks | Both findings reproduced; original fixture and copied DB read bytes preserved |
| Local frontend tests/build | Not run; recorded hosted Web61 evidence inspected |
| Whole local repository Python suite | Not run; selected relevant suite above only |

The two extra checks use only copies of an existing test database and the new read-only reader/guard. They do not replay discovery, resume Safe, modify submitted source, access live customer state, or constitute an unrestricted adversarial campaign.

## Recorded platform evidence independently inspected

The source/checkouts, actual test/smoke output, Web test/build output, all 15 complete Live JSON documents, actual final outcome lines and executed enforcement were inspected. Installer and runner boilerplate were not exhaustively audited. Retained run metadata confirms all three workflows are pull-request attempt 1 for submitted HEAD; no workflow was retriggered.

| Recorded gate | Actual evidence |
| --- | --- |
| CI435, run34180348752, Python 3.11 job101917994938 | 1,341 passed, one warning, 457.75s; five actual smoke groups passed |
| Same run, Python 3.13 job101917995100 | 1,341 passed, one warning, 474.03s; five duplicate smoke steps intentionally skipped |
| Web61, run34180348743, job101917995008 | Three test files / 45 tests passed, including five new source-render/control tests; `tsc --noEmit && vite build` completed |
| Live186, run34180348766, job101917995118 | 201 deterministic tests passed in 12.33s; seven qualified summaries in 15 complete JSON documents |
| Executed Live final enforcement | Six actual outcomes success, then `PRETRANSFER_ALL_LIVE_QUALIFICATIONS_PASS` at `2026-09-08T02:37:05.2348359Z` |

The six actual outputs at Live log lines 2438–2443 are CANCELLATION, LIVE, PRODUCT, PROGRAM, HARD and PRODUCTION_LARGE success; line 2444 is executed enforcement, distinguished from echoed script text. Hard and Large test documents have return code zero and PASS reviews with no required actions. The standard Program document explicitly reports `program_automatic_execution=false` and `cross_phase_source_handoff=false`; its live qualification remains v1. No live-model cumulative-v2 qualification is inferred.

All four logs literally check out preview `87d705d1f4df210e8e7a54b835a4c46e8c8c0264`; matching tree establishes source equivalence, not commit identity or an actual integration. Independently rehashed decoded logs:

| Log | SHA-256 |
| --- | --- |
| CI435-Python311.log | `f0bca0a727cf7ec1114f45ee8c6f04f1004697c75a2f13e6fce9b09ae2239a36` |
| CI435-Python313.log | `739a5daea05fffebb9842916c44f705510d373fcba1c3e70c02e87cc8818afe8` |
| web-ui.log | `4da680644aa66943038f032a8de974a85a0fc15b1851972d6cf09e1bfd6ec1bf` |
| Live186.log | `cbb10b4dd9843705797e47f6ca7d0bbd0ff6a7df63e5d0aed05e4dc57fce3290` |

Counts overlap. Downloaded diagnostic ZIPs were not independently rehashed by this reviewer; their API digests are not promoted to that claim. Platform success remains valid historical qualification of this source, but does not resolve F1/F2.

## Other conclusions, follow-ups and limits

The new reader uses SQLite `mode=ro`, `query_only`, normal locking, one explicit read transaction, bounded scalar/document/aggregate retrieval and cooperative SQLite work limits. It constructs no effectful service and projects an explicit field allowlist. Token/capability/URL/path/source payloads are excluded; current filesystem, source-byte and ownership verification flags remain false. This historical/trusted-host boundary is sound in the inspected ordinary paths. The defects above concern completeness and internal consistency within that boundary.

Origin Git, accepted source and derived execution Git are distinct in API/UI. Terminal and separate source acceptance labels are distinct on valid metadata. Refresh does not grant v2 authority. Existing c2/preparation/acceptance implementations, v1 same-Base checks, lifecycle recovery and platform-gate files are unchanged by the complete diff. The selected regressions support preservation; this report does not reopen PR25 or give a blanket security attestation.

Nonblocking follow-ups remain separate: the inherited legacy `coverage_evidence.py::_run_git` audit, PR21 aggregate blob-request instrumentation and PR20 objective/parser/preflight wording items. No closure is claimed. A minor documentation clarification would also help: `PROGRAM_SOURCE_VISIBILITY.md` says there is no polling, while the unchanged busy-Program polling effect in `App.tsx:135–152` now receives the added source field. No new polling loop was introduced; wording should distinguish that from explicit idle refresh.

The required corrections are narrowly the new projection's F1/F2 and their regressions. Preserve the read-only boundary, valid in-flight recovery states, private authority exclusions, legacy/generation-zero support and c2 effectful defenses. A corrected exact HEAD/tree requires independent follow-up and its normal platform gates. This report provides no human GitHub APPROVE, Ready, merge, gate bypass, paid retry, automatic execution, deployment or generated-source publication. No external state or canonical handoff was changed by this reviewer. The parent session is responsible for persisting this report and recording the resulting blocked checkpoint.

## Review evidence staged outside the repository

- `pr26-review-output/metadata_read_checks.py`: exact bounded reproduction code.
- `pr26-review-output/metadata_read_observations.jsonl`: exact observed outputs.
- `pr26-independent-tests.log`: independent existing-test output.

The scratch SQLite copies are reproducible diagnostic intermediates, not user deliverables or execution-authority stores. The report and small textual evidence should be retained; no fixture source publication is requested.

Run the preserved two-case reader check from the independent checkout's `universal-coding-agent/` directory:

```bash
.venv/bin/python /workspace/scratch/2f614e332d31/pr26-review-output/metadata_read_checks.py
```

Its input is the existing regression fixture at `/tmp/pytest-of-root/pytest-52/test_actual_http_reads_and_rej0/product/programs.sqlite`. Both output copies remain under `pr26-review-output/`: `terminal_with_pending_execution.sqlite` and `missing_dispatch_and_base.sqlite`. The script makes a new backup from that pristine input before each mutation. Recreating the input after scratch loss requires running the existing named fixture; it is not a new live qualification.

| Retained textual evidence | SHA-256 |
| --- | --- |
| `metadata_read_checks.py` | `ea7ef915f7b51cb36060fd3f47fb3e4ab6efca82b1b585615793f104e340b0b5` |
| `metadata_read_observations.jsonl` | `068df87ec4336d110031caa2baaf1230a15262b0ed687d1cd48be7c72f49d717` |
| `pr26-independent-tests.log` | `909420ebf6e92e5633f7793065cd339ac98b0c928f27848ced96ae623ad7ae3d` |
