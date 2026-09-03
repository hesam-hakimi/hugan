READ-ONLY DIAGNOSTIC — WORKING TREE RECONCILIATION FOR src/test/runTest.ts

Do not edit any file. Do not use any patch, edit, or write tool. Do not
accept or discard any pending editor change — do not press Keep or Undo,
and do not invoke any equivalent command. No compile, no lint, no test
execution, no runner, no Extension Host, no stage, no commit, no stash,
no checkout, no restore. Read-only commands only.

If you believe something is wrong, report it. Do not fix it.

REPOSITORY
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
This is a LINKED GIT WORKTREE. Its index lives under the parent repository
at etl_framework_extension_hf1_v2\.git\worktrees\recovery-extension-product-0.3.147\
Do not assume a local .git directory.

BACKGROUND
An earlier session reported a comment-only edit to src/test/runTest.ts:
one hunk, doc-comment text only, no executable line changed. The editor
change counter displayed "1 file changed +1702 -49" for the same file,
and the same session disclosed a second hunk near line 119 that it says
predates the task. These have not been reconciled. Establish the facts.

Q1 — ON-DISK STATE
a. Report SHA-256, byte size, and total line count of src/test/runTest.ts.
b. The previously recorded pre-task values were
   9fc4041b2cbd0394329fdd8ee16631ef969edda13c4c858d7369a025d4b55447
   and 82517 bytes. State only SAME or DIFFERENT for each. Do not infer
   what the difference means.
c. Locate the function that resolves the disposable profile root. Quote
   its complete preceding doc comment verbatim, with live line numbers.
   State whether the on-disk text is the original wording or the
   rewritten wording.

Q2 — DIFF VOLUME AGAINST HEAD
Run and report the raw output of each:
  git --no-pager diff --numstat -- src/test/runTest.ts
  git --no-pager diff -w --numstat -- src/test/runTest.ts
  git --no-pager diff -U0 -- src/test/runTest.ts
For the last one, report the total number of hunks and list every hunk
header line (the @@ lines) in file order. Do not paste the full diff body
here.

Q3 — EVERY HUNK THAT IS NOT THE COMMENT HUNK
For each hunk identified in Q2 other than the doc-comment hunk, print the
hunk header and the complete hunk body. State for each whether it touches
an executable line, a type, a field, a parameter, or a call site.

Q4 — RECONCILE THE COUNTER
State whether the displayed "+1702 -49" can be reproduced from any
read-only comparison available to you, and if so which two states it
compares. If it cannot be reproduced, answer exactly:
COUNTER_ORIGIN: CANNOT_DETERMINE_STATICALLY

Q5 — BASELINE COMPARISON
VS Code local history for this file is at
  %APPDATA%\Code\User\History\7179216d
Read its entries.json. Confirm the resource it maps to. List every entry
with its timestamp in chronological order. Identify the latest entry
whose timestamp precedes the comment edit. Then run:
  git --no-pager diff --no-index --numstat -- "<that entry>" "src\test\runTest.ts"
  git --no-pager diff --no-index -U0 -- "<that entry>" "src\test\runTest.ts"
Report the numstat line, the hunk count, and every hunk header.

Q6 — RE-DERIVE LINE NUMBERS LIVE
Do not use any line number from this prompt or from any document. Report
the current live line number of each of the following, quoting the line:
  1. the signature of the function that resolves the disposable profile root
  2. the guard that tests whether the isolation root does not already exist
  3. the throw taken when allowRootCreation is false
  4. the call that creates the directory tree
  5. the call site that passes allowRootCreation false
  6. the call site that passes allowRootCreation true
If any of these does not exist as described, say so plainly.

REPORT
1. Q1–Q6, in order, with raw command output where requested.
2. A list of every command you ran, and confirmation that all were
   read-only.
3. Confirmation that no file was written, no editor change was accepted
   or discarded, and no compile, test, runner, Host, stage, or commit
   occurred.
4. Anything you found that this prompt did not ask about — reported,
   not changed.
5. Stop.
