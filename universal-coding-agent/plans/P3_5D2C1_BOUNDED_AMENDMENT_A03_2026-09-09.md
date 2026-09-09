# P3.5d-2c-1 bounded amendment A03 — H10 loaded-runner deadline

Task: `UCA-20260908-P35D2C1-LOCAL-PRODUCT-COMMANDS`.
This test-only correction is recorded before editing the permitted focused H10
test. It adds no runtime authority, endpoint, phase, workflow or pilot task.

## Exact observed gap

PR30 amended candidate `e1a2146630306cf48b24c4d88993160787b6407c`,
tree `21e26be1166762f3e79cc1ea090a79981aa85486`, was checked out through preview
`6d48dedad3f4fac0b6366c1ee1420770695d398c` by CI449. Python 3.11 passed.
Python 3.13 completed 1,875 tests successfully and failed only the
`decide_first_source` parameter of the H10 transaction-contention test after
1,782.69 seconds of full-suite load. One of four already-issued public legacy
control/recovery HTTP futures exceeded the harness's per-future 15-second wait.
The failure log does not identify an incorrect response or runtime exception;
the test's `finally` block then released the deliberately held transaction.

This run remains failed. It is not retried unchanged, manually requalified,
waived or combined with the separate Python 3.11 success. The exact retained
Python 3.13 log has 58,191 bytes and SHA-256
`aaae9013372e4702fc3b452746ce268b833fec63c65f599d3e496ac3452c04d3`.

The same three H10 parameters previously passed locally in 75.13 seconds and
in the separate published-candidate independent 16-test run. Those results are
evidence of their own trees and environments, not a replacement for CI449.

## Permitted change

Change only `tests/test_local_product_command_durability.py`, already an allowed
focused test in the canonical task. Replace sequential per-future 15-second
waits with one finite aggregate deadline for all four concurrently issued
requests. Require every future to complete before inspecting any response, and
retain the exact response-status, pending-replay, lock-exclusion, no-extra-call,
completion and replay assertions. The held effect must still remain blocked
until explicit release. No sleep, retry loop, skip, xfail, platform condition,
response relaxation or runtime change is permitted.

An aggregate 60-second deadline bounds the whole set rather than granting up to
60 seconds independently to each future. The test must fail with a concrete
count if any request remains unfinished. This increases runner scheduling
tolerance while preserving the concurrency proof and a finite failure bound.

## Gates

Run all three H10 parameters repeatedly on the exact staged tree and execute
the focused Product suite plus Ruff as appropriate. Preserve all failures. The
new exact candidate requires its own independent bounded correction review and
automatic current-head CI, Live and Web results; prior results stay attached to
their original heads. No blind paid retry or manual workflow dispatch is part
of this amendment.

Ready and expected-head-locked integration remain blocked until all current
candidate gates pass. This document does not certify future execution,
publication or integration. The local Product milestone remains planned;
`ready_for_supervised_pilot=false` and `real_project_pilot_validated=false`.
