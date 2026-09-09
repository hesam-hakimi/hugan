# P3.5d-2c-1 local Product commands — author implementation evidence

Task: `UCA-20260908-P35D2C1-LOCAL-PRODUCT-COMMANDS`.

This is an authored implementation candidate, not independent acceptance, a human
GitHub APPROVE, or completed Product/pilot qualification. The delivery milestone
`UCA-M-LOCAL-PILOT-1` remains planned. This document records completed observations
before its publication; it does not certify its own future upload, CI or integration.

## Source and bounded changes

The exact definition base is `578079cf344b0c535e5278282c5703f75c716a41`, tree
`9a8c537b96ead7ddf77de05ccbe70216f0ce160d`. Its sole parent is the preserved milestone
`a04dd89ae3dd9f9db50755f8a4e7dda0248c952f`, whose parent is actual PR29
`f27c2693babcdf20145676328012b2d7576c5aa3`, tree
`29b763ff5af8a50348f7e987b341db65fac33bfa`. The accepted target and superseded parallel
continuation-api definition were independently rechecked without rewinding either.

The author reviewed all 23 changed Python files and changed native consumers. The
implementation adds the seven planned local binding, command/journal, recorded
reader, first-driver/source-quote and HTTP modules. Narrow changes are confined to
CLI/web startup, Safe/discovery denial, v1 source participation, v3/v2 transaction
participation and composed recorded readers. Four focused test modules exercise
real TCP HTTP, Program, Safe, stores, Git, deterministic providers and actual trusted
subprocess tests. Existing UI, workflows, c1/c2 proof and adapter code, milestone and
historical definition documents remain unchanged. No outside-scope runtime amendment
was needed. This new author evidence document is within the task's allowed evidence seam.

The new path is disabled unless both explicit startup flags and the immutable
operator binding are present. One canonical Safe root and exact project/Program,
provider/capability, source/Git/test policy, store inode and approved-plan bindings
are retained. Browser values contain only bounded intent and exact identities.

There are nine explicit effect POST commands, one narrowly bounded observation/reconcile
POST, and five recorded GET families. Each Program retains canonical request/head/
response linkage. Completed replay returns exact historical bytes; ambiguous work
cannot be retried or adopted after process death or removal of its worker row.

The first driver executes the real first phase and returns through its original
registration context. The first quote retains candidate-1 under its original owner.
A decision prepares another candidate under a fresh worker, captures the full core
independently twice, compares it with the quote, and accepts the new candidate under
that same worker. v1 owner/capture/same-Base comparisons remain intact. Source CAS,
receipt, HTTP response and exact release participate in the same final transaction.

Continuation keeps one owner through real c1 materialization/Base and v3 admission/
discovery, retaining actual lower-generated IDs. Scope and final source decisions
use their required fresh workers. PR29's full preview/predecessor ancestry, immutable
core and atomic receipt-2 remain required. Only the original live returned v3 adapter
can explicitly reconcile its reversible seal failure. D2a remains inert and receipt-2
authorizes neither materialization nor a third phase.

## Recorded-reader correction and supported runtime

Pure readers use existing files, selected bounded SQL, no effectful runtime factories,
no checkpoint/source decoding, and shared metadata/hash accounting. No old-reader
fallback grants access to partial or unknown-version records.

The supported observer path is 64-bit Linux with SQLite's unix VFS and OFD locks.
Read-only non-inheritable descriptors are retained in a process-bounded cache (maximum
256) because closing an unrelated descriptor could drop SQLite's POSIX locks. Only
observer locks, not descriptors, are released at a read boundary. They are not worker
handles or execution authority. The database shared range prevents final close cleanup;
SHM recovery/read slots 122–127 prevent recovery and read-mark writes, including cached
writable SHM mappings. Writer/checkpoint slots 120/121 remain available so an in-flight
command's prior committed pending response can still be observed. `readonly_shm=1`
prevents a fresh reader from initializing SHM. No immutable/nolock URI, chmod, snapshot
copy, fabricated DMS lock or store repair is used. Unsupported or missing companion
states deny. Explicit normal host startup may open its existing stores; GET cannot
create missing WAL/SHM files.

The lock reasoning was checked against SQLite's primary `src/os_unix.c` and `src/wal.c`
(version-3.40.1) and actual local SQLite 3.53.1 probes. An existing older read mark can
protect the current committed WAL snapshot. Runtime evidence below tests the actual
latest value and byte preservation; source inspection is not a platform-wide certification.

Primary source: https://github.com/sqlite/sqlite/blob/version-3.40.1/src/wal.c
and https://github.com/sqlite/sqlite/blob/version-3.40.1/src/os_unix.c.

## Candidate evidence and acceptance mapping

| Gate | Concrete authored evidence and limits |
| --- | --- |
| H01 | Full nine-effect HTTP 42 -> 43 -> five-process restart/continuation -> 44 -> separate final acceptance, SHA-1/v1 and SHA-256/line-addressed variants. Original 42 and immutable accepted-43 bytes/modes and Git identities are preserved. No preaccepted fixture or transport mock replaces first acceptance. |
| H02 | Strict flags/configuration/local peer/Host/Origin/header/body/projection checks; mapping, source/store/root/provider/policy drift denies. Method and unknown-route errors now use the fixed uncacheable envelope. |
| H03 | Actual scope stop, all five retained registration sets, revoked late invocation context and real outer return. Remaining handles block sealing. |
| H04 | Fresh-owner quote/decision, source/execution bytes, empty directories/modes, control round trip, wrong-task/exact-thread retained remote lease, rejection finality and same-Base preservation. |
| H05 | Actual c1 materialization/Base IDs and one-owner v3 admission/discovery in H01 and all-nine race. Receipt-2 cannot continue. |
| H06 | Explicit v3 scope; failed tests, FAIL and conditional review deny preview; premature final preview is a pure denial. Native full final acceptance remains separate. |
| H07 | All nine commands raced between independent server processes: one effect, historical pending response, exact completed replay, conflicting-body/new-ID denial; lost committed response replays after source drift. Actual call/apply/trusted-test counters are checked. |
| H08 | Nine process-death command boundaries, plus two external SIGKILL cases after actual first-driver return; even removing the dead worker does not clear the pending claim. |
| H09 | Actual reversible v3 seal failure: only original same-live adapter reconciles without another provider call; restart stays blocked. |
| H10 | Independent public pause/resume/cancel/recovery, real fresh-worker method and Safe/remote WAL writers excluded during initialization, first acceptance and final acceptance transactions. Parked control drift invalidates a quote. |
| H11 | Fresh import-guarded reader, no subprocess/Git/provider/checkpoint decoder, complete ancestry deletion and missing companion denial, exact historical response, no missing-store creation. Actual HTTP after unrelated Safe WAL write, last-writer close and another connection's POSIX reservation are checked together with pending replay. |
| H12 | Aggregate 64-KiB/1-MiB metadata and 24,000,000/256,000,000 opaque limits, stricter cached bounds, large counters denied before allocation, SQL-bound adversarial WAL growth, full public view validation and fixed errors. |
| H13 | Raw v1/c1/Safe/discovery and reconstructed/subclass participant denials; unmarked native v1/c1/c2/v3/v2/web behavior receives the explicitly selected compatibility run. |
| H14 | LP01, LP02 and API share of LP05 have implementation candidate evidence only until independent/platform/integration gates pass. LP03/d2c-2, LP04/LP06 and RP01/RP02 remain uninstantiated. |
| H15 | Full author diff/consumer review and focused checks complete; separate exact-candidate independent review and actual CI/Live/Web are still required. Web applies because existing workflow filters include backend web paths. No paid retry/manual freshness qualification is authorized by this report. |

Latest author code/test tree before this documentation addition:
`1318ed484188a5081eb7ed68a76b79d658ae3c52`.

The final full local run on `fa6ea7ef1097628a797b8056ee7c26c5bc03d17c` had **59 passed,
1 failed**: one old test still expected framework HEAD 405 after the required fixed
422 mapping was implemented. The correction changes that expectation only; all runtime
bytes equal that full-run tree. The corrected H02/H12 run on `1318ed48...` has **9 passed,
27 deselected**. These are separate scopes, not a claimed 60-pass full rerun.

The touched-consumer run on `15b54cf8...` executed 80 tests: **79 passed, 1 failed**.
Its failure was the subsequently corrected all-nine pending reader. All 24 selected
native compatibility cases passed: exact v1 acceptance/owner/same-Base, real c1 source/
Base, c2 execution and raw-entry denial, inert d2a/v3 distinction, scoped authorizers,
v3 scope settlement, v2 replay/opaque bounds/pure reads, and legacy web explicit start.
This is candidate compatibility evidence, not a repetition or relabeling of PR26–PR29
accepted gates. Ruff over the complete project passed after the final correction.

## Retained failures and separate reviews

Initial local review: `b279d5c13dba46bb9c25c60eee950720ff7e3b08`, tree
`a4b4a137b6f538d47a5bec45e73b323266475a8a`, BLOCKED with six P1 findings. Its report
remains unchanged. The next frozen correction `de1bd398df92e11ca9a921fd7b2845b14ae98d87`,
tree `d5e73b4fb5facd498811bafb2d122c6724e59f6c`, had 54 local passes, but separate probes
found SHM mutation and a lower-counter bound gap. That reviewer session ended without
a final report; its probes/eight-test log are preserved without inventing acceptance.

A separately observed working-tree correction was preserved as local commit
`006580d6e69a2d094c7b932d72530110091824a3`, tree `2ab699ecc6a2a76ad628e7e334a9273ab5240be2`,
then continued in another isolated checkout. It is recorded as observed work, not
retroactively attributed to the implementation author or independent reviewer.

Independent correction-3 review of `90670da6c26bb8962da9690ec1848d1b94f1bb71`, tree
`15b54cf86e18fd442225267720872bbb6ba96f02`, is also preserved BLOCKED. It independently
ran 26 passing and one failing tests across two commands and verified 191 artifact
removal denials (not 191 separate journeys). P1 was the concurrent pending lock
collision; P2 was method-denial projection/no-store. Both need exact corrected-tree
review evidence and are not waived by this author report.

Earlier shared-workspace H01 failures showed directory timestamp reversion while
all independently checked file bytes remained equal. They are retained as failed
runs. The fixture root moved to `/tmp`; no source proof, owner binding or timestamp
comparison was weakened. Initial transport setup, incorrect derived-witness traversal,
evidence-manifest omissions and test-argument/path/expectation errors also remain in
the exact run ledger below. No failed run is reclassified as a pass.

| Author run ID | Exact staged tree | Literal completed pytest scope |
| --- | --- | --- |
| `h01-initial` | `2630c422598629e6f308c8b4a9ddde6876a2ef8c` | No completed pytest count; exit 1 |
| `h01-correction-1` | `6ca87feadd036f3ba3fe95dbaf8c4fc5f17c3dae` | 1 passed in 8.60s |
| `h01-correction-2` | `3fc673823367b2a6b9fe8567f9734465a8254420` | 1 failed in 2.83s |
| `h01-correction-3` | `62b75beced911623b67c8eb7c8740f58ebaea698` | 1 failed in 5.67s |
| `h01-correction-4` | `92f5d8ab177630e28d5b6927ede96ee24106d304` | 1 failed in 5.73s |
| `h01-correction-5` | `d16be17b0f1d2b34a8d4dd82375cc59108f5c6b3` | 1 failed in 6.53s |
| `h01-correction-6-diagnostic` | `b88c03d52ea4cad1b3678e64078ff5c8c7ec63eb` | 1 passed in 9.87s |
| `h01-correction-7` | `a4b4a137b6f538d47a5bec45e73b323266475a8a` | 2 passed in 21.66s |
| `h02-h04-initial` | `fc0517b8f35a75a361539b40eb780eef391fdc5a` | 12 passed, 2 deselected, 1 warning in 24.95s |
| `h07-h09-initial` | `45400b397e23152ec23bcf9f67dfcb05e6ff02e4` | 12 passed, 14 deselected in 51.17s |
| `h01-h09-correction-8` | `071ae294174a5fb51e4893c6e46d8a79589eead3` | 1 failed, 3 passed, 22 deselected in 34.07s |
| `h04-h13-correction-9` | `c8d9ba7e42c0680c711ed799d8007845e2883bc8` | 1 failed, 7 passed, 26 deselected in 37.73s |
| `h01-serialized-observation-10` | `c8d9ba7e42c0680c711ed799d8007845e2883bc8` | 1 failed, 1 passed, 32 deselected in 23.67s |
| `h01-tmp-11` | `c8d9ba7e42c0680c711ed799d8007845e2883bc8` | 2 passed, 32 deselected in 23.38s |
| `h01-h11-correction-12` | `91d728045be81708a499432c40c3658ae53399f2` | 3 failed, 31 deselected in 16.77s |
| `h01-h11-correction-13` | `91db495ec40f7183a4ebbc5b0aa518e507ca9d7d` | 11 passed, 23 deselected, 1 warning in 51.86s |
| `h07-h10-processes-14` | `b8167b7eb41f348d51c0563e491ab93baa807720` | 1 failed, 3 passed in 63.25s (0:01:03) |
| `h10-h12-correction-15` | `e3b8a510debb3589b731076829dcb2cc4e64429e` | 2 failed, 3 passed, 3 deselected in 17.12s |
| `h01-h12-reader-16` | `afa20a483ffb14cfc32f4ce5a89401e7a5468205` | 7 failed, 1 passed, 30 deselected in 9.37s |
| `h01-h12-reader-17` | `57bb2cb12bc21bcbbf283ed979abb5e8ac5fc1a1` | 8 passed, 30 deselected in 56.32s |
| `h03-h06-h13-lifetimes-18` | `1d5eb738c1efec4c6d226cd7394465854dbc2f4f` | 1 failed, 15 passed, 29 deselected in 52.01s |
| `local-product-full-19` | `d5e73b4fb5facd498811bafb2d122c6724e59f6c` | 54 passed, 1 warning in 246.23s (0:04:06) |
| `correction3-shm-and-bounds-20` | `15b54cf86e18fd442225267720872bbb6ba96f02` | 3 passed, 4 deselected in 4.79s |
| `correction3-local-and-consumers-21` | `15b54cf86e18fd442225267720872bbb6ba96f02` | 1 failed, 79 passed, 1 warning in 222.83s (0:03:42) |
| `correction3-pending-wal-controls-22` | `6cea73a2fe8a1f9b55921cd2d5a700a8e2f08857` | 3 failed, 4 passed, 7 deselected in 59.66s |
| `correction3-h10-writers-23` | `4fc3b527347c0899a2ef6578f67242c527928dfe` | 3 failed, 4 deselected in 15.32s |
| `correction3-h10-writers-24` | `64d34e5d7e0b7c93bab5e4fec16843add6a6498e` | 3 passed, 4 deselected in 75.13s (0:01:15) |
| `correction3-final-local-25` | `fa6ea7ef1097628a797b8056ee7c26c5bc03d17c` | 1 failed, 59 passed, 1 warning in 329.89s (0:05:29) |
| `correction3-h02-final-26` | `1318ed484188a5081eb7ed68a76b79d658ae3c52` | 9 passed, 27 deselected, 1 warning in 16.62s |

Each complete retained run record includes its exact argv, contemporaneous local HEAD,
staged tree, UTC start/end, exit status and log SHA-256. Staged-tree evidence is not
misrepresented as a committed head. Failed/corrected reports and reference preimages
are preserved before any continuity replacement.

`ready_for_supervised_pilot=false` and `real_project_pilot_validated=false`.
No AskTD/customer access, new live-provider Product journey, UI/workflow implementation,
scheduler, migration, refresh, arbitrary shell endpoint, ETL, production deployment,
main/PR6/root todos/history rewrite or generated-source publication is part of this slice.
Standard Live Program is v1 and cannot qualify a complete real-model v3 Product journey.
Future direction remains read-only AskTD onboarding followed by one separately approved
bounded change, with private project mapping and generic public Product behavior.
