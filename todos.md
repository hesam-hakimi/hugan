TASK_ID: ETL-0903-DIAG04
TYPE: READ-ONLY INVESTIGATION — STALE COMPILED RUNNER (runTest.js)

Echo TASK_ID: ETL-0903-DIAG04 as the first line of your report.

Do not edit any file. Do not use any patch, edit, or write tool. Do not
accept, discard, or otherwise resolve any pending editor change — no
Keep, no Undo, no equivalent command. Several chat-editing sessions hold
unresolved pending entries for src/test/runTest.ts against a much older
snapshot; leave every one exactly as it is. No compile, no build, no
lint, no test execution, no runner, no Extension Host, no npm install,
no stage, no commit, no stash, no checkout, no restore, no reset.
Read-only commands only.

Report what you find. Fix nothing. Build nothing. Propose, do not apply.

REPOSITORY
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
LINKED GIT WORKTREE — index lives under the parent repository at
etl_framework_extension_hf1_v2\.git\worktrees\recovery-extension-product-0.3.147\
There is no local .git directory.

DERIVE EVERYTHING YOURSELF
Take no line number, path, size, or timestamp from this prompt or from
any document. Locate everything by reading.

BACKGROUND
package.json defines the test script as "node runTest.js". A file of
that name exists and is far smaller and older than the TypeScript source
src/test/runTest.ts, and searching it for the source's protected-hash
identifiers returns nothing. If that is right, the current test entry
point does not contain the logic under qualification, and nothing on
that path has ever executed in this worktree. Establish the facts.

WHAT TO ESTABLISH

Q1 — IDENTIFY BOTH ARTEFACTS
For runTest.js and src/test/runTest.ts report: resolved absolute path,
byte size, line count, SHA-256, and last-write time. State where exactly
runTest.js sits relative to the repository root.

Q2 — HOW THE TEST IS INVOKED
Quote every script in package.json that runs tests, with file:line.
Trace what each one actually executes. State plainly which file is the
entry point today, and whether any script compiles TypeScript before
running it.

Q3 — WHAT PRODUCES runTest.js
Determine whether runTest.js is a build output, a hand-written file, or
something else. Report the TypeScript configuration that governs
src/test/**: its path, its outDir, its include and exclude, and where a
compiled runTest.js would be written. State whether that location is the
same file the test script runs. If they differ, say so explicitly and
give both paths.

Q4 — VERSION SKEW, MEASURED
Do not compile. Compare the two files textually and report:
  a. identifiers present in the .ts source but absent from the .js;
  b. identifiers present in the .js but absent from the .ts;
  c. whether the .js contains any protected-hash, isolation-root, or
     evidence-emission logic at all;
  d. your best evidence for roughly which state of the source the .js was
     produced from — cite what you matched on.

Q5 — TRACKED OR NOT
For runTest.js and for any compiled output directory, report whether git
tracks them, whether they are ignored, and by which ignore rule with
file:line. Report whether runTest.js differs from its committed version
if one exists. Use read-only git commands and prefer --no-optional-locks.

Q6 — WHAT A BUILD WOULD TOUCH
Without running anything, determine what a compile of this project would
write: every output path or directory, and whether any of them already
contains files. State whether a compile could overwrite or delete
anything currently uncommitted anywhere in the worktree. Name every such
path. This is the question that matters most — answer it carefully.

Q7 — PRECONDITIONS FOR A BUILD
Report whether the toolchain a compile needs is present: node_modules,
the TypeScript compiler, and any build script the project defines. Do
not install anything. Report absence as absence.

Q8 — THE SMALLEST SAFE PATH FORWARD
Describe, without applying it, the smallest sequence that would make the
test entry point run the current source. For each step state whether it
writes to the worktree, what it would overwrite, and whether it is
reversible. Flag separately anything that would alter what the extension
does for a user — that is an owner decision, not yours.

REPORT
1. TASK_ID line.
2. Q1 to Q8 in order, with raw command output where relevant.
3. Every command you ran, and confirmation all were read-only.
4. Anything found that this prompt did not ask about — reported, not
   changed.
5. Close with exactly:
     TASK_ID: ETL-0903-DIAG04
     TEST_ENTRY_POINT: <path>
     ENTRY_POINT_IS_CURRENT: YES / NO
     RUNTEST_JS_TRACKED: YES / NO
     BUILD_WOULD_OVERWRITE_UNCOMMITTED: YES / NO / CANNOT_DETERMINE
     PATHS_AT_RISK: <count>
     OWNER_DECISIONS_REQUIRED: <count>
     FILES_MODIFIED: NONE
     PENDING_EDITOR_CHANGES_RESOLVED: NONE
     COMPILE_OR_BUILD_EXECUTED: NO
6. Stop.
