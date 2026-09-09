# P3.5d-2c-1 bounded amendment A01 — H15 documentation vocabulary

Task: `UCA-20260908-P35D2C1-LOCAL-PRODUCT-COMMANDS`.
This amendment is recorded before either implementation edit below. It uses the
canonical task's explicit provision for a recorded bounded amendment before an
additional-file change. It adds no Product phase, delivery criterion or pilot task.

## Exact observed gap

PR30 initial published candidate is `a67d4ee4046aa484568c85ef31afbfd9e3e08060`,
tree `bd605e8f28f3492d9ce389b11775f6aad05ecde0`. Its automatic required Live199
run `34298513573`, job `102300235608`, checked out preview
`3c4420ca85aeee2edd2aea92663d9ad2aa944fc8` with that same tree. The aggregate
gate failed with literal `HARD_OUTCOME=failure`; the other five child outcomes
were success. The UI's step conclusion is insufficient because the hard step
uses `continue-on-error`.

The hard fixture reached the checker script's final documentation assertion:
`assert "stale" in doc or "less than or equal" in doc`. Its generated contract
states that a winning candidate mutates stored state only when strictly newer,
and that an equal or older delete does nothing. The semantic requirement is
present; that equivalent vocabulary is absent from the lexical allowlist. All
preceding functional assertions executed before this final assertion failed.
The run remains failed: source was preserved, the sandbox patch was rolled back,
and no reviewer verdict or completed hard qualification is inferred.

The exact retained UTF-8 job log has 201,075 bytes and SHA-256
`92e4fba00b5548f9815351ea9c725f8e430d7a1ce8f3275a90de697b08824f91`.
There is no request to retry the same candidate, waive this gate, or reclassify it.

## Added file scope and exact limit

The primary author read the complete existing producer and its sole focused test
consumer, plus all `hard_test_script`/reference/initial/suite call sites, before
recording this amendment. The two files are unchanged from the accepted base:

| Added path, relative to `universal-coding-agent/` | Initial Git blob | Permitted edit |
| --- | --- | --- |
| `src/universal_coding_agent/testlab/hard_reasoning.py` | `71ccc07ced2262dc30d98b39d4650a50ce3d23bb` | Recognize the equivalent documentation phrase `equal or older` in the final lexical check only |
| `tests/test_hard_reasoning_lab.py` | `d965f1bb35895ef8bd3273eeb55eea953943e5eb` | Deterministic subprocess regressions for equivalent wording, missing documentation, and rejection of equal/older state mutations |

Every functional checker statement, fixture/reference implementation, model
objective, approval criterion, provider, policy, source-preservation check,
reviewer requirement and aggregate success threshold remains required. This is
a bounded correction to an existing qualification vocabulary check, not a
general documentation evaluator or a change to a CDC/ETL project. No generated
model source or patch is added to the repository. No UI or workflow file changes.

## Verification and separate candidate gates

Retain the failed Live199 result and initial candidate's independent review and
CI/Web scopes. Reproduce the wording failure without model calls, then execute
the amended checker against the known valid solution with both wording families,
missing required documentation, and functional equal/older-update mutants. The
known incorrect initial fixture must still fail.

Review the complete correction diff and obtain a separate independent correction
review of the exact new candidate. A normal PR synchronization may run the
required automatic current-candidate CI/Live/Web gates. There is no manual
dispatch, paid retry of unchanged bytes, freshness-only requalification, or gate
waiver. Ready and expected-head integration remain blocked until every required
gate passes for the corrected candidate.

This document records scope and required checks; it does not certify their future
results, its own publication, or integration. The earlier author evidence report
remains an exact historical observation before this amendment. LP01/LP02/API LP05
remain subject to H15. `UCA-M-LOCAL-PILOT-1` remains planned, with
`ready_for_supervised_pilot=false` and `real_project_pilot_validated=false`.
