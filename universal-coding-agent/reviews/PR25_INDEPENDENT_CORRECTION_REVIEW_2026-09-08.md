# PR25 independent correction review — 2026-09-08

**Verdict: PASS for the bounded correction review. All five findings in the
previous independent report are resolved at the exact source reviewed below.
No unresolved correctness blocker was identified within this review's scope.**

This is the separately authorized, read-only follow-up review of
`hesam-hakimi/hugan` PR25. The latest review instruction restricted the work to
the nine-file correction, relevant consumers, the prior five findings, and
existing deterministic pytest cases. That instruction superseded the earlier
request to adapt and rerun the independent probes. No new adversarial experiment,
network request, live provider call, implementation edit, or external mutation
was performed during this follow-up.

| Source identity | Independently verified value |
| --- | --- |
| Detached review checkout | `/workspace/scratch/9c5f9e1807b4/uca-pr25-review-fixed` |
| Reviewed HEAD | `aabc8d2c06d54978363d43f69d6e00d0b481e7c2` |
| Reviewed tree | `2433238df764274bcf5ba6cc1639913b496fd3e6` |
| Sole parent / previously reviewed HEAD | `fb033d6e57b580bd609a6796fef7984b880cbbcb` |
| Actual PR24 merge / PR base | `b0daccdb16bd09898b06ed56bff787008a31a145` |
| Base tree | `a21c01b85e766a6d0f427e4b46dbb1b5f2de1bfd` |
| Base-to-HEAD merge base | `b0daccdb16bd09898b06ed56bff787008a31a145` |
| Correction compared | Parent to reviewed HEAD: nine files, 504 insertions, 20 deletions |
| Tracked working-tree state | Clean before and after testing |

The complete correction diff and prior independent report were read, including
the amended P3.5c-2 task and admission/recovery contract. The relevant corrected
Safe, discovery, dispatch, execution-adapter, attestation and acceptance consumers
were inspected alongside the new regression assertions. The earlier review's
full base-to-parent examination remains historical evidence for unchanged code;
this follow-up does not represent a fresh unrestricted security review of the
entire repository.

All source and test locations below are relative to `universal-coding-agent/`
at the reviewed HEAD. Priorities retain their meaning from the original report.

| Original finding | Disposition | Corrected implementation and observed regression coverage |
| --- | --- | --- |
| F1, P1: wrong/default-control Safe resume bypass | Resolved | `safe_service.py:146–196` verifies a checkpoint-database binding to the control database's canonical path, device and inode before the task registry check. `product/program_source_dispatch.py:43–76` establishes the binding before admission and requires it during durability validation. The existing regression at `tests/test_program_source_dispatch.py:449` passes for both omitted and unrelated control stores. |
| F2, P1: reconstructed adapter replays ambiguous discovery | Resolved | `product/program_source_execution_adapter.py:30–78` introduces a process-local random capability, persists only its digest, and consumes an armed invocation through a database CAS. Explicit dispatch and approval transactions issue the capability at `product/program_source_dispatch.py:566,623`. Five process-death/reconstruction regressions at `tests/test_program_source_dispatch.py:815` pass. |
| F3, P2: legacy discovery mutates evidence before rejection | Resolved | `discovered_safe_service.py:94–104` gates legacy task/thread entry before sandbox allocation, provider invocation and task artifact writes. The regression at `tests/test_program_source_dispatch.py:484` passes with the shared control store and the default control store. |
| F4, P2: result-recording crash destroys a committed report binding | Resolved | `product/program_source_dispatch.py:83–87,785` places result and report artifacts beneath a digest of the exact Safe state. Lineage verification at line 287 and capture at `product/program_source_acceptance.py:326` derive the matching v2 references. The `report-update` case of `tests/test_program_source_dispatch.py:848` passes at the previously missing crash interval. |
| F5, P2: rejected edit application leaves modified bytes | Resolved | `product/program_source_attestation.py:467` returns bounded subprocess results; the adapter at `product/program_source_execution_adapter.py:262–274` preserves ordinary nonzero results when `check=False`. Its live-apply rollback at lines 278–415 restores approved Base bytes while retaining ownership, inventory and filesystem checks. Whitespace, partial-write and changed-boundary regressions pass. |

For F1, the authority check reads the binding from the Safe checkpoint database
independently of the caller's selected control database. The binding is written
in a separate transaction before admission. Program and control remain the only
databases written by admission/result transactions. The regression exercises
legacy run, resume, control resume, pause and cancel against mismatched control
stores, checks that provider calls and source generation do not advance, and
then demonstrates successful approval through the correct v2 service.

For F2, a durable `*_started` state is no longer sufficient for a newly
constructed adapter. Discovery and Safe/resume entry claim the matching
capability before invocation; active execution checks the consumed claim. The
five existing regressions kill real child processes at discovery,
discovery-result, Safe-intent, scope-intent and implementer boundaries. A fresh
process's reconstructed adapter fails with an invocation-capability error;
provider call logs, dispatch status and accepted generation remain unchanged.
The normal safe continuation from a proven recorded discovery remains covered
by the selected tests.

For F3, the early check executes before discovery processing. Both regression
variants preserve every existing Safe artifact byte, create no legacy discovery
sandbox and add no provider call. The subsequent legitimate v2 approval succeeds,
covering the original evidence-corruption consequence as well as the rejection.

For F4, the prior scope-stop report and the terminal report have different state
digests and therefore different references. Exact artifact verification remains
in place, including v2 acceptance and lineage consumers; the v1 reference path
is retained. The added `report-update` death occurs after the terminal report
write and during the corresponding Program execution update. The test verifies
that the previously committed report bytes survive, reopens in a fresh process,
reconciles the proven terminal checkpoint without repeating provider work, and
prepares and accepts generation 2. This directly covers the old report-write /
database-rollback interval.

For F5, preserving `check=False` allows the edit engine to reach its ordinary
rollback branch. The adapter also handles a known partial local apply while its
live invocation capability remains valid, instead of requiring the partially
modified files to match the old content proof. It bounds reads, retains file
identity and no-follow checks, validates all unaffected inventory and Git metadata,
and checks current authority before restoring exact Base bytes. The passing
tests at lines 513 and 548 cover rejected trailing whitespace through both
`v1` and `v2-line-addressed`, and a real partial file write followed by an error.
They end blocked with exact Base bytes restored and source generation unchanged.
The three cases at line 572 change control authority, add an unexpected file,
or substitute a symlink during failure handling; rollback rejects these changes
without repairing the changed authority or inventory. This remains a bounded
live-failure mechanism, not permission to replay an ambiguous crashed apply.

The separate local environment was created with cached dependencies using
`uv venv .venv` and
`uv pip install --offline --python .venv/bin/python -e '.[dev]'` inside the
corrected review checkout. Independent checks confirmed:

- Interpreter: `/workspace/scratch/9c5f9e1807b4/uca-pr25-review-fixed/universal-coding-agent/.venv/bin/python`.
- Imported package: `/workspace/scratch/9c5f9e1807b4/uca-pr25-review-fixed/universal-coding-agent/src/universal_coding_agent/__init__.py`.
- Python 3.12.13; SQLite 3.53.1.

Existing test subprocesses use that interpreter, so their editable package
source is pinned to the corrected review checkout. The author's environment
was not used to qualify these results.

| Independently executed check | Result |
| --- | --- |
| Selected deterministic pytest run below | **431 passed in 274.85 seconds**, exit status 0 |
| Ruff on all six corrected source modules and `tests/test_program_source_dispatch.py` | Passed |
| `git diff --check fb033d6e57b580bd609a6796fef7984b880cbbcb HEAD` | Passed |
| Final source identity and tracked status | Exact HEAD/tree/parent; clean |
| Previous report and reproduction artifact hashes | Unchanged |

The pytest command, run from the corrected checkout's
`universal-coding-agent/` directory, was:

```bash
.venv/bin/python -m pytest -q \
  tests/test_program_source_dispatch.py \
  tests/test_program_source_acceptance.py \
  tests/test_program_source_attestation.py \
  tests/test_program_execution_base.py \
  tests/test_program_source_materialization.py \
  tests/test_safe_graph.py \
  tests/test_safe_control.py \
  tests/test_discovered_safe_service.py \
  tests/test_program_execution.py \
  tests/test_line_edit_protocol.py \
  tests/test_sharded_line_edit_protocol.py
```

This includes all 69 corrected dispatch cases and relevant shared consumers.
The selected tests cover actual local service/checkpoint flows, deterministic
providers, separate source approval, both edit protocols, process deaths and
fresh-process recovery. A complete corrected-head repository suite was not run
by this reviewer. Author-reported tests and platform CI/Live runs are not counted
as independent evidence in this report.

The historical artifacts below were preserved byte-for-byte under
`/workspace/scratch/9c5f9e1807b4/review-output/`:

| Preserved file | SHA-256 |
| --- | --- |
| `UCA_PR25_Independent_Review_Report_2026-09-07.md` | `0864ea1112b42c280e2d7dc3fadeb6cd86adfc52421312496c88ae1684f86945` |
| `pr25_independent_probes.py` | `9af24717fbede9887399ab80880c77a3998b15821c2882f060fc6253f2124201` |
| `pr25_independent_probe_observations.jsonl` | `19eb16c2c55c7e3f7f313417973aaeee72f0f386f9075d915ce58033e3b8ec47` |

The old BLOCKED verdict continues to apply to the old exact HEAD. This separate
report accepts closure of those five findings only for the corrected identity
above, using the source inspection and existing regressions stated here. No
prior finding remains unresolved within that restricted review.

The inherited bounded POSIX/same-UID trusted-host and trusted Git-executable
assumptions remain. This follow-up did not test arbitrary host compromise,
physical power loss or live provider behavior. Technical finding closure is
separate from final platform qualification, human GitHub APPROVE, Ready and merge
gates. This report performs none of those actions and authorizes no automatic
Program execution loop.
