# PR25 independent correctness and security review

**Verdict: BLOCKED — two P1 findings and three P2 findings require correction.**

This is a separately authorized, independent read-only engineering review of
`hesam-hakimi/hugan` PR25. Review completed on 2026-09-08 UTC; the report filename
retains the task's requested 2026-09-07 identifier. The implementation was not
modified. No GitHub comment, approval, Ready action, merge, paid provider call,
deployment, or platform-gate bypass was performed by this reviewer.

## Exact reviewed identity

| Identity | Independently observed value |
| --- | --- |
| Review checkout | `/workspace/scratch/9c5f9e1807b4/uca-pr25-review` |
| Reviewed HEAD | `fb033d6e57b580bd609a6796fef7984b880cbbcb` |
| Reviewed tree | `56ae33656d3f77da32c34f492db861ed3071c3c2` |
| HEAD parent | `f403d12036f23eaed0e9eaf13a4682faba0973e2` |
| Actual PR24 merge / PR base | `b0daccdb16bd09898b06ed56bff787008a31a145` |
| Base tree | `a21c01b85e766a6d0f427e4b46dbb1b5f2de1bfd` |
| Base-to-HEAD merge base | `b0daccdb16bd09898b06ed56bff787008a31a145` |
| Tracked working-tree state | Clean before and after review/testing |

The reviewed comparison is the complete base-to-HEAD change: 18 files, 2,837
insertions and 71 deletions. The predecessor commit changes four documentation
files only. Historical PR24 acceptance is treated as inherited history, not as
qualification of PR25 or as an additional blocker.

## Scope and method

The full P3.5c parent execution task, P3.5c-1 execution Base contract, P3.5c-2
versioned dispatch task, and P3.5c-2 admission/recovery contract were read. No
repository `AGENTS.md` was found. Independent review authorization comes from the
parent execution task's completion section, including lines 153–156.

Review covered the complete new dispatch and execution-adapter modules, all
changed implementation hunks, the entire new 53-case test module, and the actual
Program, discovery, Safe graph, control, lifecycle ownership, acceptance,
materialization, attestation, patch, artifact, context and Git consumers. The
legacy CLI construction path was checked in addition to the injected shared-control
path used by the new tests. The existing v1 `_prepare_accepted_evidence()` same-Base
guard remains unchanged. The `_finish_locked()` extraction retains the c1
pending-phase verification; it does not silently revalidate a consumed preparation
as a pending phase.

An isolated `.venv` was created in the detached review checkout using cached
dependencies. Both the interpreter and imported package path were checked:

- Interpreter: `/workspace/scratch/9c5f9e1807b4/uca-pr25-review/universal-coding-agent/.venv/bin/python`
- Source import: `/workspace/scratch/9c5f9e1807b4/uca-pr25-review/universal-coding-agent/src/universal_coding_agent/__init__.py`
- Python 3.12.13; SQLite 3.53.1.

The tests' subprocesses use this interpreter, whose editable install is pinned
to the review checkout. The author checkout and its virtual environment did not
qualify these results.

## Findings

All paths below are relative to `universal-coding-agent/` in the exact reviewed
commit. P1 denotes a high-priority execution/approval boundary failure; P2 denotes
a material correctness or recovery defect that blocks this contract's acceptance.

### F1 — P1: Default-control Safe resume bypasses v2 admission and scope authority

**Location:** `src/universal_coding_agent/safe_service.py:145–154`; control selection
at lines 77–78. The actual legacy CLI caller is `src/universal_coding_agent/cli.py:238–242`.

`_execution_gate()` consults only the control database selected by the current
caller. A v2 task is registered in the Program's shared control database, but
`SafeAgentService.create(same_safe_root, provider)` defaults to a different
`safe/task-control.sqlite`. Both services open the same Safe checkpoint database.
The default control store has no v2 registry entry, so the legacy graph resumes
the stored v2 task with no execution adapter.

Reproduction through real services and deterministic providers:

1. Run the actual first phase and accept 43; admit the second phase and dispatch
   it to its actual scope approval checkpoint.
2. Create a new `SafeAgentService` on the same Safe root, omitting `control` and
   `execution_adapter`, exactly as the CLI construction does.
3. Call `resume(stored_thread_id, True)` without an owner token, scope digest or
   v2 approval operation.

Observed: legacy resume returns `completed`; real implementer and reviewer calls
run; the owned derived `app.py` changes from 43 to 44. The dispatch remains
`awaiting_scope_approval`, its `approval_sha256` is still null, and accepted source
generation stays 1. This is unauthorized v2 execution even though subsequent
source acceptance remains protected.

Correction must bind a Safe checkpoint root to its trusted control authority and
reject mismatched/default-control effectful entry before graph invocation. A
registry in an optional caller-selected control store is insufficient.

### F2 — P1: Reconstructing an admitted adapter replays ambiguous discovery

**Location:** `src/universal_coding_agent/product/program_source_execution_adapter.py:49–59`
and `src/universal_coding_agent/discovered_safe_service.py:75–79`. The same admission
pattern appears in adapter `entry()` at lines 173–182.

`discovery_request()` accepts any newly constructed exact-type
`AdmittedSafeExecution` while the durable state is `discovery_started`. That state
is a record that provider work may already have begun; it is not a one-time
invocation claim. Recreating the adapter with the current owner token is enough
to call the public `start_admitted()` path again.

Reproduction: after an actual child process logs entry to `solution_discovery`
and exits via `os._exit(73)`, reopen all stores in a fresh process. Normal
`dispatch()` correctly rejects the ambiguous state. However:

```python
service.start_admitted(AdmittedSafeExecution(dispatch, operation_id, current_owner))
```

repeats discovery and reaches the actual Safe scope stop. The independent call log
shows a new `solution_discovery` invocation reading 43; durable state advances to
`safe_started`. No database contents or implementation code are changed to enable
this restart. The crash uses the existing real-process fixture.

Each effectful adapter entry must consume an invocation capability issued by the
explicit transaction. A stored `*_started` state alone must never authorize a
new adapter or simultaneous connection to repeat an ambiguous invocation.

### F3 — P2: Legacy discovery mutates v2 evidence before its later Safe rejection

**Location:** `src/universal_coding_agent/discovered_safe_service.py:70–73` and
131–144, followed by artifact writes before `safe.run()` at lines 239–249.

The legacy `start()` entry has no v2 registry gate before cloning, discovery or
artifact writes. Even with the correct shared control store, the eventual Safe
gate runs too late.

Reproduction: after a v2 phase reaches scope approval, call legacy `start()` with
its task/thread identifiers and the original repository. A deterministic provider
reading original 42 runs discovery and overwrites `tasks/<task>/solution-*`
artifacts. `safe.run()` then rejects the v2 task, as intended, but the provider
side effect and evidence overwrite have already occurred.

Observed: one new discovery call on 42; discovery provenance hash changes;
legacy start raises `ValueError: source-aware task requires explicit v2 execution API`.
The legitimate subsequent v2 `approve_scope()` fails with
`ArtifactIntegrityError: artifact SHA-256 does not match trusted evidence`.

Gate the legacy discovery task/thread against the authoritative registry before
sandbox allocation, provider work, or writes to task-owned artifacts.

### F4 — P2: A result-recording crash destroys the prior committed report binding

**Location:** `src/universal_coding_agent/product/program_source_dispatch.py:835–852`;
the resulting recovery rejection occurs in `_load()` at lines 237–244.

`_record()` overwrites `phase-execution-report.json`, whose prior scope-stop bytes
are already hash-bound in the committed dispatch row, before the result transaction
commits. Filesystem replacement is not rolled back when SQLite rolls back. The
next `_load()` therefore rejects the previous committed digest and reconciliation
cannot consume an otherwise proven terminal checkpoint.

Reproduction uses a real child-process death after the report write:

```sql
CREATE TEMP TRIGGER report_crash
AFTER UPDATE OF phase_report_ref ON program_executions
WHEN NEW.safe_status='completed'
BEGIN SELECT die(); END;
```

Here `die()` invokes `os._exit(73)`. Reopen the stores in a fresh process.

Observed: actual Safe checkpoint is `completed` with no pending nodes; dispatch
is `resume_started`; Program execution correctly rolls back to
`awaiting_scope_approval`; generation remains 1. Yet `reconcile()` fails with
`ArtifactIntegrityError` because the report file contains terminal bytes while
the database still binds the old scope-stop report. The existing `record-update`
test crashes earlier and misses this interval.

Preserve committed artifact bytes during a new result transaction, for example
with immutable versioned artifact references. Do not recover by omitting hash
verification or adopting an unbound replacement file.

### F5 — P2: Ordinary rejected edit application leaves changed bytes without rollback

**Location:** `src/universal_coding_agent/product/program_source_execution_adapter.py:208–215`
and 228–234; actual caller `src/universal_coding_agent/safe/patching.py:186–194`.

The adapter's replacement `_git()` ignores `check=False` and always calls the
attestor runner with only return code 0 allowed. `SafeEditEngine.apply()` relies
on receiving a nonzero `git diff --check` result so it can run its rollback branch.
Instead, the adapter raises before that branch, after the local edit was written.

Reproduction: through the actual approved phase, return a valid existing-file
replacement changing `return 43` to `return 44 `, with a trailing space. Git rejects
the resulting whitespace. No crash or filesystem sabotage is required.

Observed: `approve_scope()` raises a source filesystem-proof error; derived
`app.py` remains `b'def answer():\n    return 44 \n'`; dispatch is `resume_started`;
the last Safe checkpoint is `planning` with `apply_edits` pending; accepted source
generation stays 1. There is no terminal rollback result.

Static inspection identifies a second part of the same rollback defect:
`_restore()` calls `_path()`, which insists that the worktree still equals the old
retained proof. During an ordinary partially completed apply, the new retained
proof has not yet been stored, so restoring `check=False` behavior alone will
still reject restoration. Preserve caller return-code semantics and implement a
bounded owned-file rollback for known local apply failures, maintaining current
owner/control checks and no-follow filesystem identity checks.

## Independent validation results

| Check | Result |
| --- | --- |
| `python -m pytest -q tests/test_program_source_dispatch.py` | 53 passed in 112.21 seconds |
| `python -m pytest -q` | 1,294 passed in 295.13 seconds |
| Full-suite warning | One Starlette/AnyIO deprecated `BlockingPortal` alias warning |
| Ruff on new dispatch, adapter and dispatch test modules | Passed |
| Five independent probes, rerun from preserved probe script | All five findings reproduced |
| Final HEAD/tree/status recheck | Exact reviewed identity; tracked checkout clean |

The passing suite includes the actual original 42 to accepted 43 to fresh-process
execution and accepted 44 flow, separate exact scope/transition approvals,
SHA-256 Git with the line-addressed edit protocol, owned rollback on ordinary
test/review failures, authority/evidence drift, independent-connection admission
and duplicate-dispatch checks, and real process deaths at its specified handoffs.
These successes do not cover the five independently reproduced gaps above.

`git diff --check` reports a trailing blank line at the end of the historical
PR24 review document. This is not an engineering blocker and was not changed.

The written Program/control rollback-journal policy is consistent with the
reviewed SQL mutation set. The attached Safe checkpoint database is not written
by those transactions. SQLite's primary documentation distinguishes modified
rollback-journal databases from WAL writes in multi-database atomic commit;
this review does not claim power-loss fault injection or database/filesystem
atomicity. References checked: [SQLite super-journals](https://sqlite.org/tempfiles.html#super_journal_files)
and [ATTACH transactions](https://sqlite.org/lang_attach.html).

## Reproduction artifacts

The independent probe source and captured observations are outside the repository:

- `/workspace/scratch/9c5f9e1807b4/review-output/pr25_independent_probes.py`
  — SHA-256 `9af24717fbede9887399ab80880c77a3998b15821c2882f060fc6253f2124201`.
- `/workspace/scratch/9c5f9e1807b4/review-output/pr25_independent_probe_observations.jsonl`
  — SHA-256 `19eb16c2c55c7e3f7f313417973aaeee72f0f386f9075d915ce58033e3b8ec47`.

Reproduce with:

```bash
/workspace/scratch/9c5f9e1807b4/uca-pr25-review/universal-coding-agent/.venv/bin/python \
  /workspace/scratch/9c5f9e1807b4/review-output/pr25_independent_probes.py \
  --checkout /workspace/scratch/9c5f9e1807b4/uca-pr25-review/universal-coding-agent
```

Each probe creates isolated local fixture repositories and stores. The recorded
observations include their paths and the exact imported source identity. The
script does not modify implementation files or call a paid provider.

## Acceptance and limitations

Technical acceptance is withheld for the exact reviewed HEAD. The parent author
has been informed of all five findings; proposed author corrections have not
been reviewed or accepted by this report. Any corrected source requires a new
explicit fixed-head review, including rerunning the relevant independent probes
and checking that authority, recovery and rollback protections remain intact.

This report does not qualify CI/Live results, platform policy, human GitHub
APPROVE, Ready status, or permission to merge. Those are separate gates for the
corrected exact source. No automatic Program execution loop is accepted.

The bounded POSIX/same-UID trusted-host model and trusted Git executable remain
the inherited limitations. Arbitrary host compromise and physical power-loss
behavior were not tested. The review uses real local Git, actual services and
checkpoints, deterministic providers, subprocess tests and real process death;
it makes no claim about a live paid provider run.
