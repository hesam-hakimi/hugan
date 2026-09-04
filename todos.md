TASK_ID: ETL-0903-TYPECHECK01
TYPE: AUTHORISED TYPE-CHECK — NO EMIT

Echo TASK_ID: ETL-0903-TYPECHECK01 as the first line of your report.

EXACTLY ONE COMMAND IS AUTHORISED IN THIS TASK:

    npx tsc -p ./ --noEmit

Run it once, from the repository root. Nothing else is authorised.

Specifically forbidden, without exception:
  - npm run compile, npm run compile:test, npm test, npm run pretest,
    npm run bundle, npm run bundle:sttm, or any other npm script
  - tsc with -p tsconfig.test.json (that config sets incremental: true
    and tsBuildInfoFile: ".tsbuildinfo.test" and would rewrite a TRACKED
    file — do not use it)
  - tsc without --noEmit
  - npm install, npm ci, or any dependency change
  - eslint, mocha, node, vsce, the runner, the Extension Host
  - any edit, patch, or write tool
  - accepting or discarding any pending editor change — no Keep, no
    Undo, no equivalent command. Several chat-editing sessions hold
    unresolved pending entries for src/test/runTest.ts against much
    older snapshots. Leave every one exactly as it is. Do not inspect,
    resolve, or comment on them.
  - stage, commit, stash, checkout, restore, reset, clean
  - deleting or moving anything, especially anything under out/

WHY THIS IS NARROW
The out/ directory holds 2,016 generated files and is the only working
build in this worktree. It is git-ignored, so no git operation can
restore it. The repository's own compile script deletes out/ before
invoking the compiler. That script is not authorised here. --noEmit
writes nothing at all, which is the entire point of this step.

If npx attempts to download or install anything, stop and report that
instead of proceeding.

BEFORE RUNNING — RECORD THE STARTING STATE
Read-only. Report:
  a. SHA-256, byte size, and line count of src/test/runTest.ts
  b. file count and total byte size under out/
  c. SHA-256, byte size, and mtime of .tsbuildinfo.test (this file is
     TRACKED; it must be unchanged at the end)
  d. git --no-optional-locks status --porcelain=v1 --untracked-files=all

RUN
Execute the single authorised command. Capture its complete stdout and
stderr verbatim, and its exit code. Do not re-run it. Do not run a
variant if it fails. Do not attempt a fix.

REPORT THE RESULT

1. Exit code.

2. Total number of diagnostics. If zero, say so plainly.

3. If there are errors, group them by file, with a count per file. Then
   list every distinct error code with its count and one representative
   message.

4. For src/test/runTest.ts specifically: every diagnostic, with live line
   number, the error code, the full message, and the source line quoted.

5. Classify each error as one of:
     PRE-EXISTING — present in code that was already committed
     NEW — in the uncommitted 1,998 lines of src/test/runTest.ts
     OTHER — anywhere else
   State how you determined the classification. Do not guess.

6. State plainly, in one sentence, whether the current sources compile.

AFTER RUNNING — PROVE NOTHING CHANGED
Re-measure and compare against the starting state:
  a. src/test/runTest.ts SHA-256 — must be identical
  b. out/ file count and total byte size — must be identical
  c. .tsbuildinfo.test SHA-256 and mtime — must be identical
  d. git status --porcelain — must be identical
Report each as SAME or DIFFERENT. If any is DIFFERENT, say so loudly and
explain what you observed. Do not attempt to repair it.

DO NOT FIX ANYTHING
If the type-check fails, that is the finding. Report it and stop.
Proposing a fix is welcome; applying one is not authorised.

REPORT
1. TASK_ID line.
2. Starting state.
3. The command, its exit code, and its complete raw output.
4. Items 1 to 6 above.
5. The after-state comparison.
6. Anything found that this prompt did not ask about — reported, not
   changed.
7. Close with exactly:
     TASK_ID: ETL-0903-TYPECHECK01
     COMMAND_RUN: npx tsc -p ./ --noEmit
     EXIT_CODE: <n>
     TOTAL_DIAGNOSTICS: <n>
     ERRORS_IN_RUNTEST_TS: <n>
     SOURCES_COMPILE: YES / NO
     OUT_DIRECTORY_UNCHANGED: YES / NO
     TSBUILDINFO_TEST_UNCHANGED: YES / NO
     FILES_MODIFIED: NONE
     PENDING_EDITOR_CHANGES_RESOLVED: NONE
     EMIT_OCCURRED: NO
8. Stop.
