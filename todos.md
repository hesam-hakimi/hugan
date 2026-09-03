IMPLEMENTATION ONLY — COMMENT ACCURACY. No compile, no test execution,
no runner, no commit. Edit only src/test/runTest.ts. Change only comment
text. Do not change a single line of executable code, type, or field.

Two doc comments now overstate the invariant after the scope correction.
Rewrite them to describe what is actually true.

1. The comment above `interface RunnerEvidenceDeclarations` currently
   claims this block is the only place where a hard-coded value carries
   meaning. That is no longer accurate. Rewrite it to say: this block
   holds values asserted by the author rather than observed by the
   runner; it is not the only literal in the evidence, and the remaining
   literals are marked individually at their fields.

2. The comment above `interface RunnerEvidence` currently claims every
   field outside `declarations` is an observation. Rewrite it to say:
   fields marked "must be computed, never literal" are observations and
   must be produced from a runtime value at the moment of writing;
   fields carrying an explicit literal comment are known exceptions;
   the shape is closed, so the compiler rejects a newly invented field,
   but TypeScript cannot distinguish a hard-coded value from a computed
   one of the same type.

Do not add, remove, or reword any other comment. Do not add a comment to
any field. Do not touch `taskId`.

REPORT
1. Unified diff of the two comment blocks only.
2. Confirm in one line that no executable line, type declaration, or
   field changed.
3. Stop. Independent review follows.
