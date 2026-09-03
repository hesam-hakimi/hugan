IMPLEMENTATION ONLY — COMMENT ACCURACY, PRE-EXISTING DEFECT. No compile,
no test execution, no runner, no Extension Host, no commit, no stage.
Edit only src/test/runTest.ts. Change only comment text. Do not change
any executable line, type, field, or behaviour.

An independent review found a comment that asserts something untrue of
the code it documents. It predates the current task; the owner has now
authorised fixing it.

THE DEFECT
runTest.ts:1362 states the function resolves the disposable profile root
"without mutating it", and runTest.ts:1364 states "The caller must create
this directory first." Both are unqualified and both are false: the
function creates the directory tree at runTest.ts:1409 whenever its
allowRootCreation parameter is true, and the non-focused call site passes
true at runTest.ts:1633.

REQUIRED CHANGE
Rewrite those comments so they describe what the function actually does.
State the conditional plainly: the function does not mutate the
filesystem unless allowRootCreation is true, in which case it creates the
directory tree itself; the caller is responsible for creating it only
when allowRootCreation is false. Use whatever wording is accurate — do
not copy that sentence verbatim if the code does something subtler than
this description.

Read runTest.ts:1350-1420 and runTest.ts:1625-1640 before writing, and
base the wording on what the code does, not on what I have described.
If my description of the defect is itself wrong, say so and change
nothing.

CONSTRAINTS
- Change only these comments. Do not touch the function, its parameters,
  its call sites, or any other comment in the file.
- Do not add a comment anywhere else.
- Do not fix, note, or reword any other inaccurate comment you notice.
  Report it instead.
- Write the edit in a single save. Do not reflow neighbouring lines.

REPORT
1. Unified diff of the comment blocks only.
2. Quote the rewritten comments in full and, for each sentence, give the
   file:line evidence in the function body that makes it true.
3. Confirm no executable line, type, field, or call site changed.
4. List any other comment in this file you found to be inaccurate,
   without changing it.
5. Stop. Independent review follows.
