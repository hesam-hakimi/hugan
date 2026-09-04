TASK_ID: ETL-0903-DIAG05
TYPE: READ-ONLY INVESTIGATION — HARD-CODED PRODUCT PATHS AND CONFIGURATION SURFACE

Echo TASK_ID: ETL-0903-DIAG05 as the first line of your report.

Do not edit any file. Do not use any patch, edit, or write tool. Do not
accept, discard, or otherwise resolve any pending editor change — no
Keep, no Undo, no equivalent command. No compile, no build, no lint, no
test execution, no runner, no Extension Host, no npm install, no stage,
no commit, no stash, no checkout, no restore, no reset. Read-only
commands only.

Report what you find. Fix nothing. Propose, do not apply.

REPOSITORY
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
LINKED GIT WORKTREE — index lives under the parent repository at
etl_framework_extension_hf1_v2\.git\worktrees\recovery-extension-product-0.3.147\
There is no local .git directory.

DERIVE EVERYTHING YOURSELF
Take no path, line number, or setting name from this prompt or from any
document. Locate everything by reading.

SCOPE — PRODUCT PATHS ONLY
This investigation is about paths the extension uses at runtime for a
user: where it reads input from, where it writes output to, where it
looks for workspaces, dependencies, or executables.

It is NOT about the test harness. Paths that exist only inside test,
qualification, or evidence code are out of scope — list them separately
under "test-only, out of scope" and do not analyse them further. If you
cannot tell which side a path falls on, say so rather than guessing.

BACKGROUND
The intended design was that user-facing paths are supplied through
VS Code settings and through the tool's own settings panel, never
compiled into the source. Whether the code actually does this has not
been verified. Establish it.

WHAT TO ESTABLISH

Q1 — THE DECLARED CONFIGURATION SURFACE
From package.json, list every configuration setting the extension
contributes: full setting id, type, default value, scope, description,
and file:line. Mark which of them are paths or contain a path.

Q2 — THE PANEL'S OWN SETTINGS
Locate any settings surface the extension renders itself — a webview,
panel, form, or command that collects configuration from the user. For
each, report file:line, every field it collects, where the value is
persisted, and whether it is a path.

Q3 — HOW EACH SETTING IS READ
For every setting from Q1 and Q2, trace where the code reads it, with
file:line. Report what happens when it is unset or empty: a default, a
fallback, an error, or silent continuation. Quote the fallback.

Q4 — EVERY ABSOLUTE OR MACHINE-SPECIFIC PATH IN PRODUCT CODE
Scan the extension's runtime source for string literals that are, or
build, a filesystem path. Report file:line, the literal, and what it
resolves to. Flag especially: drive letters, user profile paths, machine
or user names, installation directories, and anything naming a specific
person's environment. For each, state whether it is reachable at runtime
for a user, or dead.

Q5 — PATHS THAT SHOULD BE SETTINGS BUT ARE NOT
For each finding in Q4 that is reachable, state whether a user could
override it through any mechanism that exists today. If not, that is a
hard-coded product path. List these separately and plainly — this is the
answer the owner is waiting for.

Q6 — THE OPPOSITE ERROR
Report any setting that is declared but never read, or read but never
declared. Both are defects: the first misleads the user, the second is
invisible configuration.

Q7 — WHAT SHIPS
Read the packaging ignore rules and state which of the files you examined
would actually be included in a package. A hard-coded path in a file that
never ships is a different severity from one that does. Report both
categories separately.

REPORT
1. TASK_ID line.
2. Q1 to Q7 in order, with raw command output where relevant.
3. Every command you ran, and confirmation all were read-only.
4. Anything found that this prompt did not ask about — reported, not
   changed.
5. Close with exactly:
     TASK_ID: ETL-0903-DIAG05
     DECLARED_SETTINGS: <count>
     PATH_SETTINGS: <count>
     HARD_CODED_PRODUCT_PATHS_REACHABLE: <count>
     HARD_CODED_PATHS_THAT_SHIP: <count>
     DECLARED_BUT_NEVER_READ: <count>
     READ_BUT_NEVER_DECLARED: <count>
     OWNER_DECISIONS_REQUIRED: <count>
     FILES_MODIFIED: NONE
     PENDING_EDITOR_CHANGES_RESOLVED: NONE
     COMPILE_OR_BUILD_EXECUTED: NO
6. Stop.
