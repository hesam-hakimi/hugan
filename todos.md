INDEPENDENT REVIEW — READ ONLY. Do not compile, run tests, launch a
runner or Extension Host, install anything, or edit any file. Read-only
git and file-read commands are acceptable. Writing, staging, or
committing is not.

You did not write this change. The author may be a model of the same
family as you. That is a reason to be stricter, not softer.

Repository: C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
File under review: src/test/runTest.ts (uncommitted working-tree change)

BACKGROUND
A previous version of this change was reviewed and rejected. The
rejection found that two fields added as replacements were tautological:
they could never be false, so they carried no information. The author
has now deleted them and added nothing in their place.

AUTHORISED INTENT — the whole of it
The evidence file must not present a literal value as an observation.
Exactly two things were authorised:
  1. Remove runnerAliveWhileWritingEvidence from finalProcessIntegrity
     and put nothing in its place.
  2. Move parentPostExitCheckRequired out of finalProcessIntegrity into
     a new top-level `declarations` object, as a flat boolean, keeping
     its original name.
Plus: correct the two doc comments so every sentence in them is true.
Nothing else was authorised.

CHECKS — each with file:line evidence and a verdict of CONFIRMED,
VIOLATED, or CANNOT_DETERMINE_STATICALLY

A. List every key in finalProcessIntegrity and in declarations as
   emitted. Confirm finalProcessIntegrity gained nothing, lost exactly
   two keys, and that declarations holds exactly one flat boolean named
   parentPostExitCheckRequired.

B. Is any field anywhere in the emitted object an assertion that no
   possible run could falsify? Name each one. This is the failure the
   previous review found; verify it is gone and has not reappeared in
   another form.

C. Take each sentence of both doc comments in turn. For each, state
   whether it is true of the file as it now stands, with the file:line
   that makes it true or false. A sentence that is true only under a
   charitable reading counts as false.

D. Does the file still declare a rule that it then violates? Compare
   every "must be computed, never literal" marker against the value
   actually emitted for that field.

E. Does this change alter runner behaviour — control flow, exit codes,
   write ordering, file path, encoding, or what is written in a failing
   run? Answer for a passing run and a failing run separately.

F. Report any change that serves no part of the authorised intent above.
   Scope creep is a finding, not a favour.

G. A baseline copy of the pre-change file may exist at:
     %TEMP%\runTest.baseline-2026-09-03.ts
   If it exists, diff against it and report anything the author did not
   declare. If it does not exist, say so plainly and state which of your
   verdicts are weakened by its absence.

REPORT
1. Verdicts A through G.
2. Overall verdict: ACCEPTABLE, or NOT_ACCEPTABLE with blocking findings.
3. What you could not determine without compiling or running.
4. Do not propose fixes. Do not edit. Do not compile. Stop.
