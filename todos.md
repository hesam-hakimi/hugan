TASK_ID: ETL-0903-DIAG03
TYPE: READ-ONLY INVESTIGATION — PROTECTED-HASH COUNT DEFECT IN src/test/runTest.ts

Echo TASK_ID: ETL-0903-DIAG03 as the first line of your report.

Do not edit any file. Do not use any patch, edit, or write tool. Do not
accept, discard, or otherwise resolve any pending editor change — no
Keep, no Undo, no equivalent command. Several chat-editing sessions hold
unresolved pending entries for this file against a much older snapshot;
leave every one of them exactly as it is. No compile, no lint, no test
execution, no runner, no Extension Host, no stage, no commit, no stash,
no checkout, no restore, no reset. Read-only commands only.

Report what you find. Fix nothing. Propose, do not apply.

REPOSITORY
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
This is a LINKED GIT WORKTREE. Its index lives under the parent
repository at
etl_framework_extension_hf1_v2\.git\worktrees\recovery-extension-product-0.3.147\
There is no local .git directory. HEAD is not a usable baseline for
src/test/runTest.ts — the committed blob is 79 lines and the working file
is over 2,000.

DERIVE EVERY LINE NUMBER YOURSELF
Project documents cite this defect at three different lines and none is
authoritative. Take no line number from this prompt or from any document.
Locate everything by reading the file.

BACKGROUND
The runner reads a protected-hash manifest, captures hashes before a run
and after it, and compares them. A count of protected entries is believed
to be hard-coded as the literal 8 somewhere in this file, while the real
manifest is believed to contain 39 paths. If so, the assertion cannot
detect a manifest that has grown or shrunk, and may be asserting
something no run could falsify. Establish whether that is true.

WHAT TO ESTABLISH

Q1 — THE MANIFEST, AS IT ACTUALLY IS
Locate the protected-hash manifest that this runner reads at runtime.
Report its resolved path, whether it exists on disk, its SHA-256, its
byte size, and the exact number of path entries it declares. Show how you
counted. If the manifest is generated rather than stored, say so and
report what generates it.

Q2 — EVERY HARD-CODED COUNT IN THIS FILE
Scan the whole of src/test/runTest.ts for numeric literals used as an
expected count, length, or size in a comparison, assertion, throw
condition, or evidence field. For each, report file:line, the full
statement, what it is counting, and what value it would have to be today
for the assertion to be correct. Include the suspected 8. Do not restrict
yourself to the protected-hash area.

Q3 — THE PROTECTED-HASH PATH, END TO END
Trace and report, with file:line for each step:
  a. where the manifest is read;
  b. where the "before" hashes are captured;
  c. where the "after" hashes are captured;
  d. every comparison performed between them, and between either of them
     and the manifest;
  e. every throw or failure condition on that path, quoted;
  f. every evidence field this path emits, and whether each is computed
     at runtime or written as a literal.

Q4 — WHICH ASSERTIONS CANNOT FAIL
For every assertion, comparison, and evidence field identified in Q3,
state whether any possible run could make it false. Classify each as:
  FALSIFIABLE — a real run could produce a failing value;
  BLIND — structurally cannot fail as written; explain why;
  CANNOT_DETERMINE_STATICALLY.
For each BLIND item, state precisely what a reader would wrongly conclude
from seeing it pass.

Q5 — WHAT CORRECT WOULD LOOK LIKE
Describe, without writing or applying any edit, the smallest change that
would make each BLIND item falsifiable. State for each whether it is a
pure test-tooling change or whether it would alter what the extension
does for a user. Flag anything in the second category loudly and
separately — that is an owner decision, not yours.

Q6 — BLAST RADIUS
List every other file in the repository that reads, writes, generates, or
asserts against this manifest, or that hard-codes a count derived from
it. Report path and file:line. Do not open files outside the repository
except VS Code local history if you need a baseline.

REPORT
1. TASK_ID line.
2. Q1 to Q6 in order, with raw command output where relevant.
3. Every command you ran, and confirmation all were read-only.
4. Anything you found that this prompt did not ask about — reported,
   not changed.
5. Close with exactly:
     TASK_ID: ETL-0903-DIAG03
     MANIFEST_ENTRY_COUNT: <number>
     HARD_CODED_COUNTS_FOUND: <number>
     BLIND_ASSERTIONS_FOUND: <number>
     OWNER_DECISIONS_REQUIRED: <number>
     FILES_MODIFIED: NONE
     PENDING_EDITOR_CHANGES_RESOLVED: NONE
     COMPILE_OR_TEST_EXECUTED: NO
6. Stop.
