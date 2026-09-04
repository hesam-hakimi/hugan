TASK_ID: ETL-0903-DIAG07
TYPE: READ-ONLY INVESTIGATION — WHAT CHANGED BETWEEN 0.3.145 AND 0.3.147

Echo TASK_ID: ETL-0903-DIAG07 as the first line of your report.

Do not edit any file. Do not use any patch, edit, or write tool. Do not
accept, discard, or otherwise resolve any pending editor change — no
Keep, no Undo, no equivalent command. Several chat-editing sessions hold
unresolved pending entries in this worktree; leave every one exactly as
it is. No compile, no build, no emit, no lint, no test, no runner, no
Extension Host, no npm install, no stage, no commit, no stash, no merge,
no rebase, no cherry-pick, no tag.

**Absolutely no checkout, switch, restore, reset, clean, or worktree
add/remove.** You may read any commit's content with `git show`,
`git cat-file`, and `git diff <ref> <ref>` without moving HEAD. Moving
HEAD would discard 2,000 uncommitted lines that exist in no git object.
Use --no-optional-locks throughout.

Report what you find. Fix nothing. Do not propose a repair.

REPOSITORY
Original source repository:
  C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2
Active qualification worktree (run from here):
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
The second is a LINKED WORKTREE of the first. Both share one object
store, so history for either is readable from either.

DERIVE EVERYTHING YOURSELF
Take no commit id, tag, version, path, or line number from this prompt or
from any document. Locate everything by reading git and the filesystem.

BACKGROUND
Version 0.3.147 was committed, packaged, installed and exercised. It is
retained as an immutable known-bad candidate: the installed extension
exposed a Markdown channel to the consumer but did not expose the
required structured channel.

An earlier version, 0.3.145, was intended to deliver both channels. It is
not established whether that version's acceptance tested the wrong seam,
or whether a later change dropped the structured payload. That comparison
has never been performed. Perform it.

Separately, feature work was in progress when a release became urgent,
and the release was cut from the line carrying that feature work rather
than from a clean product line. Whether feature code reached the released
artefact is unknown. Establish it.

WHAT TO ESTABLISH

Q1 — LOCATE THE TWO VERSIONS IN HISTORY
Find the commit at which package.json declared each version. Report for
each: commit id, author date, subject, branch or branches containing it,
and any tag pointing at it. If a version was never committed, or was
committed more than once, say so plainly. List every version between
them in order.

Q2 — THE STRUCTURED CHANNEL, AS OF EACH VERSION
Identify the public adapter — the seam where a tool result is returned to
the host — and the code path that produces the consumer-visible result.
For each of the two versions, read that code as it stood in that commit
and report:
  a. which result channels the adapter constructs, with file:line as of
     that commit;
  b. whether a structured channel is populated unconditionally, populated
     conditionally, or absent;
  c. if conditional, quote the condition and state what must be true.
Show the code. Do not describe it only.

Q3 — WHERE IT WAS LOST
Diff the two versions restricted to the files identified in Q2. Report
numstat, and the full diff of any hunk touching result construction.

Then find the single commit that changed the behaviour. Use `git log -S`
or `git log -L` on the relevant identifiers or line ranges to bisect by
content rather than by guess. Report that commit's id, date, subject, and
full diff for the relevant file. If the behaviour was never present in
0.3.145 either, say so — that is an equally valid finding and it means
the acceptance tested the wrong seam.

Q4 — WAS IT TESTED, AND AT WHICH SEAM
Find the tests that were supposed to cover this contract as of 0.3.145.
For each, report path, what it asserts, and — decisively — whether it
exercises the public adapter or only an internal parser or service.
State plainly whether a test existed that could have caught the loss.

Q5 — FEATURE WORK IN THE RELEASED LINE
Determine what the released commit's line contains beyond product fixes.
Report:
  a. the merge-base of the two worktrees' branches, and each branch's
     current commit;
  b. commits reachable from the released version that belong to feature
     work rather than to the fix line — identify them by what they touch,
     and say how you decided;
  c. whether these four paths exist in the released commit, in the
     working tree, or nowhere:
       src/core/settings/EtlSettingsInventory.ts
       src/core/settings/EtlSettingsProvenance.ts
       src/core/settings/EtlSettingsVsCodeBindings.ts
       src/test/suite/settingsInventoryProvenance.test.ts
  d. for any that exist in the released commit, whether their compiled
     output would have been included in the package.

Q6 — WHAT THE PACKAGE ACTUALLY CONTAINED
Read the packaging ignore rules as of the released commit and list which
source trees were included. Search the repository and its parent for any
built .vsix artefact. If one exists, report path, size, SHA-256 and
mtime — do not open or extract it. If none exists, say so.

Q7 — THE TWO WORKTREES
Report `git worktree list` verbatim. For each worktree: path, branch,
commit, and whether its working tree is clean. Do not enter or modify the
other worktree; read-only inspection of its recorded state only.

REPORT
1. TASK_ID line.
2. Q1 to Q7 in order, with raw command output where relevant.
3. Every command you ran, and confirmation all were read-only and that
   HEAD was never moved in either worktree.
4. Anything found that this prompt did not ask about — reported, not
   changed.
5. Close with exactly:
     TASK_ID: ETL-0903-DIAG07
     VERSION_0_3_145_COMMIT: <id or NOT_FOUND>
     VERSION_0_3_147_COMMIT: <id or NOT_FOUND>
     STRUCTURED_CHANNEL_PRESENT_IN_0_3_145: YES / NO / CONDITIONAL / CANNOT_DETERMINE
     REGRESSION_COMMIT: <id or NONE or CANNOT_DETERMINE>
     TEST_COVERED_PUBLIC_ADAPTER: YES / NO / CANNOT_DETERMINE
     FEATURE_CODE_IN_RELEASED_COMMIT: YES / NO / CANNOT_DETERMINE
     SA_FILES_IN_RELEASED_COMMIT: <count 0-4>
     VSIX_FOUND: YES / NO
     HEAD_MOVED: NO
     FILES_MODIFIED: NONE
     PENDING_EDITOR_CHANGES_RESOLVED: NONE
     COMPILE_OR_BUILD_EXECUTED: NO
6. Stop.
