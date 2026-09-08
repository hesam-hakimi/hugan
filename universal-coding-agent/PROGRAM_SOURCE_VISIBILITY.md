# Recorded Program source visibility — P3.5d-1

The existing `GET /api/programs/{program_id}/executions` response adds `source`,
schema `uca-program-source-status-1`, and a `Cache-Control: no-store` header.
The Program view reads it on explicit load/refresh. There is no polling, dispatch,
approval, reconciliation, provider invocation or new effectful HTTP/CLI entrypoint.

`status: uninitialized` means this Program has no recorded source initialization.
It does not inherit another Program's history. `status: recorded` distinguishes:

| Field | Meaning |
| --- | --- |
| `origin` | Recorded repository identity hash and original Git commit/tree |
| `accepted` | Latest separately accepted source generation and receipt hash |
| `lineage` | Complete bounded generation sequence, source/predecessor hashes and acceptance tasks |
| `dispatches` | Recorded v2 task/phase, input generation, admission hash, derived Git commit/tree and dispatch state |
| `dispatches[].source_accepted` | Whether that task also has a validated recorded acceptance in the lineage |
| `matches_current_plan` | Whether recorded origin requirement/plan hashes match the current Program row |

A `terminal` dispatch is not source acceptance and does not itself assert a
successful provider/test/review outcome. The view displays source acceptance
separately. Origin Git, accepted cumulative source and derived execution Git are
different identities. Execution schema `uca-program-source-dispatch-2` remains
separate from the Safe edit-protocol choice.

## Read boundary

`product/program_source_status.py` opens only the existing programs database using
SQLite `mode=ro`, ordinary locking, `query_only`, and one read transaction. It
constructs no acceptance/materialization/preparation/dispatch/Safe/Git service and
does not open source snapshots, source files, checkpoint files or artifact files.
It performs no schema initialization or recovery.

The reader verifies canonical metadata hashes and recorded relational bindings
among initialization, acceptance, candidate/approval, preparation, dispatch and
execution records. An inconsistent, missing or excessive required record produces
the stable error `recorded Program source metadata is unavailable`; it never
returns an apparently complete partial lineage or silently selects v1.

Bounds are 100 rows per queried record set, 128 bytes per selected scalar field,
64 KiB per metadata document, and 1 MiB aggregate metadata retrieval. SQL length
preflights precede Python payload retrieval in the same snapshot. A SQLite
progress handler imposes a one-million-instruction limit and a two-second
cooperative deadline; lock waits have a 0.5-second timeout. These are bounded
historical reads on the existing trusted host database, not an arbitrary hostile
SQLite-file parser or an absolute wall-clock service-level guarantee.

The public allowlist excludes worker tokens, invocation capabilities and digests,
repository URLs, paths, raw source and complete private bindings. It explicitly
reports `automatic_execution`, `filesystem_verified`, `source_bytes_verified`
and `current_authority_verified` as false. Reading historical metadata neither
requalifies the filesystem/source bytes nor grants present execution authority.

## Legacy route guard

The existing web start-next path rejects an advanced accepted source generation.
Web continuation rejects a registered v2 task. Both reject mismatched plan history
or invalid source metadata, before reserving work, and recheck at the queued worker
boundary. Only the runtime's existing worker ownership is released on failure.
Generation-zero first-phase execution and v1-only Programs retain their behavior.

Web requests acquire/release a Program worker per explicit request; c2 receipts
bind stable existing ownership. This change does not bridge that mismatch.
Effectful Product continuation requires a later bounded ownership/admission
contract. No token is copied into the browser and no c2 verifier is relaxed.

## Validation and gates

The new deterministic tests use the existing actual Git/Program/Safe/discovery,
subprocess-test/review/acceptance fixture for 42 -> 43 -> restart -> 44. They inspect
generation zero, prepared/admitted/pending execution, terminal-but-unaccepted work
and accepted generation two. Fresh-process reads load no effectful services;
provider logs, source/artifact files and database bytes remain unchanged.

Negative cases cover missing/misbound rows and tables, metadata hashes and size
bounds, incomplete lineage, wrong identities, unknown state, HTTP rejection and
queued-worker revalidation. Frontend tests check rendered identities, separate
terminal/acceptance labels, old-plan notices and legacy control selection.

Local Python validation: 47 tests passed (31 new status tests and 16 existing web
API tests); Ruff and diff checks passed. Local frontend dependency installation
was rejected by the tool before completion. Existing UCA Web UI CI must execute
its frontend test and typecheck/build steps on the submitted tree.

This document records implementation evidence, not independent acceptance.
Required CI/Live and independent review remain separate gates. PR25's accepted
tree and bounded correction-review limits are retained by the successor task and
the two exact historical reports in `reviews/`.
