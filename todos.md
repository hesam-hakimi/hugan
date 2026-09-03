IMPLEMENTATION ONLY — ONE SENTENCE. No compile, no test execution, no
runner, no commit, no stage. Edit only src/test/runTest.ts. Change only
comment text inside the doc comment above `interface RunnerEvidence`.
Do not touch any executable line, type, field, or the other doc comment.

An independent review found one blocking defect. The doc comment above
`interface RunnerEvidence` states that a field marked "must be computed,
never literal" is filled from a runtime value. One field carries that
marker and is emitted as a hard-coded literal: retriesOrRelaunches,
declared at runTest.ts:134 and emitted at runTest.ts:1980. The file
therefore states a rule it breaks.

REQUIRED CHANGE
Restore an explicit carve-out so the sentence is true of this file. The
comment must state that a marked field whose emission site carries an
explicit literal comment is a known exception, and that exactly one such
exception exists today.

Do not remove the marker from retriesOrRelaunches. Do not change its
value. Do not add or reword any other sentence.

REPORT
1. Unified diff of that one comment block only.
2. Quote the comment in full and, for each sentence, give the file:line
   evidence that makes it true of the file as it now stands.
3. Confirm no executable line, type, or field changed.
4. Stop.
