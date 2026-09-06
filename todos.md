TASK_ID: ETL-0906-PIN-DIAG01
TYPE: READ-ONLY FILE IDENTITY REPORT — NO REPAIR

Run in the existing local Windows VS Code Agent.

The owner authorizes only read-only measurements of these two files:

1. C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147\src\test\runTest.ts
2. C:\docs\ETL_QUALIFICATION_GLOSSARY.md

Purpose: obtain the complete actual hashes omitted from the screenshots of the blocked ETL-0906-B3-REPAIR-TEST01 attempt.

Use existing PowerShell with -NoProfile and .NET read-only byte inspection. Do not create scripts, temporary files, evidence directories, or reports on disk. Return the report in chat only.

Do not edit, replace, normalize, restore, or move either file. Do not execute/import the runner, compile, test, launch Host, install anything, perform Git operations, or resolve editor changes. Do not resume the B3 repair.

Expected identities copied from Reference v2:

runTest.ts:
SHA256:
9F865D703AB8C0FEAB453D62C2E26491DC6639F95423F2470473722808740089
Bytes: 126214
CRLF: 0
Bare LF: 2903
Bare CR: 0

ETL_QUALIFICATION_GLOSSARY.md:
SHA256:
537F32326590454D1070CE6AB32315240ABCCE4CE8C604F0C8AEC65AD4AB749E
Bytes: 25565
CRLF: 0
Bare LF: 587
Bare CR: 0

For each exact path:

* If inaccessible or missing, report that path and the exact error. Do not search for or substitute another file.
* Read the raw bytes without text conversion.
* Calculate SHA-256, byte length, CRLF, bare-LF and bare-CR counts from the same byte buffer.
* Re-read once and compare hashes to detect changes during measurement. If different, report UNSTABLE_DURING_READ; do not retry or select a preferred version.
* Report MATCH or MISMATCH against the expected values. A mismatch is the diagnostic result, not permission to change the baseline.

Print a compact vertical report, without tables. Put each complete 64-character hash on its own line; never truncate it or use ellipses.

Start with TASK_ID. For each file show:
PATH
EXPECTED_SHA256
ACTUAL_SHA256
EXPECTED / ACTUAL bytes and EOL counts
STABLE_DURING_READ
IDENTITY_MATCH

End with:
FILES_CHANGED_BY_TASK: NONE
COMPILER_TEST_RUNNER_OR_HOST_EXECUTED: NO
B3_REPAIR_RESUMED: NO

Stop after reporting. Do not infer who changed a file or when from these measurements.
