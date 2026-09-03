INDEPENDENT REVIEW — READ ONLY. Do not compile, run tests, launch a
runner or Extension Host, install anything, or edit any file. Read-only
git and file-read commands are acceptable.

You did not write this change. Be strict.

Repository: C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
File: src/test/runTest.ts (uncommitted working-tree change)

A previous review of this file returned NOT_ACCEPTABLE with exactly one
blocking finding: the doc comment above `interface RunnerEvidence`
asserted that every field marked "must be computed, never literal" is
filled from a runtime value, while one such field is emitted as a
hard-coded literal. The author was authorised to restore a carve-out in
that one sentence, and nothing else.

CHECKS — each with file:line evidence and a verdict

A. Read the doc comment above `interface RunnerEvidence` in full. Take
   each sentence in turn and state whether it is true of the file as it
   now stands. A sentence true only under a charitable reading counts as
   false.

B. The comment now claims exactly one exception exists. Enumerate every
   field carrying the "must be computed, never literal" marker, and for
   each, state whether its emission site is a runtime value or a
   literal. Confirm or refute the count of one.

C. Does the file still declare any rule that it then violates anywhere?

D. Confirm no executable line, type declaration, field, marker, or
   emitted value changed in this edit.

E. Report any change outside the single authorised sentence, including
   whitespace or line-wrapping changes to neighbouring lines.

F. Independently of this edit, list every value in the emitted evidence
   object that no possible run could falsify. For each, state whether it
   sits under a container the file explicitly declares as authored
   rather than observed.

G. VS Code local history for this file is at
     %APPDATA%\Code\User\History\7179216d
   Use it to establish the pre-edit state. Diff against the most recent
   snapshot that predates this edit and report anything the author did
   not declare.

REPORT
1. Verdicts A through G.
2. Overall verdict: ACCEPTABLE, or NOT_ACCEPTABLE with blocking findings.
3. What you could not determine without compiling or running.
4. Do not propose fixes. Do not edit. Stop
