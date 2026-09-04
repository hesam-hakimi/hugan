TASK_ID: ETL-0903-DIAG06
TYPE: READ-ONLY INVESTIGATION — UNCOMMITTED CHANGE IN src/extension.ts

Echo TASK_ID: ETL-0903-DIAG06 as the first line of your report.

Do not edit any file. Do not use any patch, edit, or write tool. Do not
accept, discard, or otherwise resolve any pending editor change — no
Keep, no Undo, no equivalent command. Several chat-editing sessions hold
unresolved pending entries for files in this worktree against much older
snapshots; leave every one exactly as it is. No compile, no build, no
emit, no lint, no test execution, no runner, no Extension Host, no npm
install, no stage, no commit, no stash, no checkout, no restore, no
reset. Read-only commands only. Prefer git --no-optional-locks.

Report what you find. Fix nothing. Judge nothing as acceptable or not —
that is the owner's call, not yours.

REPOSITORY
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
LINKED GIT WORKTREE — index lives under the parent repository at
etl_framework_extension_hf1_v2\.git\worktrees\recovery-extension-product-0.3.147\
There is no local .git directory.

DERIVE EVERYTHING YOURSELF
Take no line number, count, or path from this prompt or from any
document. Locate everything by reading.

BACKGROUND
src/extension.ts carries uncommitted changes. It is product code — the
extension entry point — and unlike the test harness it ships to users.
A compile of the test runner necessarily compiles this file too, so its
contents cannot be deferred. Establish exactly what changed and what it
would do differently for a user.

WHAT TO ESTABLISH

Q1 — THE FILE AND THE DELTA
Report the file's SHA-256, byte size, and line count. Report the diff
against HEAD: numstat, hunk count, and every hunk header. Confirm whether
HEAD is a usable baseline for this file — state the committed blob's size
and line count, and say plainly whether the uncommitted change is a small
delta on a mostly-committed file or something larger.

Q2 — THE FULL DIFF
Print the complete diff against HEAD, every hunk, in full. Do not
summarise or abbreviate. If it is too large to print whole, say so, give
the total changed-line count, and print it in labelled parts across your
answer rather than omitting any of it.

Q3 — WHAT EACH HUNK DOES
For each hunk, in file order, report:
  a. live line numbers;
  b. what the code did before and what it does now, in plain terms;
  c. classification — one of:
       BEHAVIOUR — changes what the extension does at runtime
       INTERFACE — changes a command, setting, contribution, or API shape
       DIAGNOSTIC — logging, telemetry, error text
       COMMENT — comment or doc text only
       REFACTOR — same behaviour, different structure
       DEAD — unreachable or unused as written
  d. whether it is reachable when a user runs the extension normally.

Q4 — USER-VISIBLE EFFECT
State plainly, for a user of the packaged extension, what would be
different. If nothing user-visible changes, say so and show why. If
something does, describe it concretely: what they would see, when, and
under what conditions.

Q5 — COMPLETENESS
Assess whether the change looks finished. Report specifically:
  - references to identifiers, functions, files, or settings that do not
    exist;
  - added code that nothing calls;
  - removed code that something still calls;
  - error paths that are started but not completed;
  - TODO, FIXME, HACK, or debug markers;
  - anything commented out rather than removed.
For each, give file:line. If you find none, say so plainly.

Q6 — DOES IT COMPILE ON ITS OWN TERMS
Without compiling anything, report whether every identifier the new code
references is declared and imported, and whether the file's imports and
exports are consistent with what it now uses. A successful project-wide
type-check has already been observed, so treat any apparent gap as your
own reading error first and re-check before reporting it.

Q7 — COUPLING TO THE OTHER UNCOMMITTED FILES
The worktree carries other uncommitted changes. Report whether this
change depends on any of them, or they on it — shared identifiers, shared
settings, call relationships. State whether src/extension.ts could be
committed alone, coherently, or whether it is part of a set.

Q8 — WHAT SHIPS
Read the packaging ignore rules and confirm whether this file's compiled
output is included in a package. State which built artefact carries it
and whether that artefact is currently present in the build output.

REPORT
1. TASK_ID line.
2. Q1 to Q8 in order, with raw command output where relevant.
3. Every command you ran, and confirmation all were read-only.
4. Anything found that this prompt did not ask about — reported, not
   changed.
5. Close with exactly:
     TASK_ID: ETL-0903-DIAG06
     LINES_ADDED: <n>
     LINES_DELETED: <n>
     HUNKS: <n>
     BEHAVIOUR_HUNKS: <n>
     INTERFACE_HUNKS: <n>
     USER_VISIBLE_CHANGE: YES / NO
     CHANGE_APPEARS_COMPLETE: YES / NO / CANNOT_DETERMINE
     COMMITTABLE_ALONE: YES / NO / CANNOT_DETERMINE
     OWNER_DECISIONS_REQUIRED: <n>
     FILES_MODIFIED: NONE
     PENDING_EDITOR_CHANGES_RESOLVED: NONE
     COMPILE_OR_BUILD_EXECUTED: NO
6. Stop.
