INDEPENDENT REVIEW — READ ONLY. Do not compile, run tests, launch a
runner or Extension Host, install anything, or edit any file. Read-only
git commands are acceptable. Writing, staging, or committing is not.

You did not write this change. The author may be a model of the same
family as you. That is a reason to be stricter, not softer. Do not
assume the change is correct. Do not fix anything.

Repository: C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
Branch:     fix/workspace-write-completion-0.3.148
File under review: src/test/runTest.ts (uncommitted working-tree change)

INTENT AS AUTHORISED BY THE OWNER
The runner's evidence file must not present a literal value as an
observation. Two fields were in scope:
  - runnerAliveWhileWritingEvidence, a hard-coded true presented as an
    observation, to be removed and replaced only by something genuinely
    observable.
  - parentPostExitCheckRequired, to move into a new top-level
    `declarations` block meaning "asserted by the author, not observed".
Everything else was to be reported, not changed. Two doc comments were
then corrected for accuracy. taskId was deliberately left alone.

The permitted JSON shape delta is exactly:
  two keys removed from finalProcessIntegrity,
  two keys added to finalProcessIntegrity,
  one new top-level key `declarations` containing parentPostExitCheck
  only.

WHAT TO CHECK — answer each with file:line evidence and a verdict of
CONFIRMED, VIOLATED, or CANNOT_DETERMINE_STATICALLY

A. Derive the emitted JSON shape from source. List every top-level key,
   and every key inside finalProcessIntegrity, activationOrderObservation,
   and declarations. State whether the shape delta matches the permitted
   delta exactly — no more, no less.

B. Is every field now inside finalProcessIntegrity produced from a
   runtime value at the moment of writing? Quote each one and its right
   hand side. Name any that is still a literal.

C. evidenceWriterPid and evidenceWriterSampledAtUtc were added as the
   replacement. Do they actually observe anything meaningful about the
   writing process, or are they a differently-shaped restatement of the
   same unverifiable claim? Say plainly which.

D. observedAfterRunTests is now derived from runTestsOutcome. Is that
   derivation sound — can runTestsOutcome hold a value that makes this
   field assert something false?

E. Scan the whole file for any remaining value presented under an
   observation-shaped key but hard-coded. List every one with file:line,
   including ones the author declared as accepted exceptions.

F. Do the two doc comments accurately describe the file as it now
   stands? Quote them and name any claim that is still false.

G. Does this change alter runner behaviour — control flow, exit codes,
   write ordering, file path, encoding, or what is written in a failing
   run? Answer for a passing run and a failing run separately.

H. Search the repository for any consumer of the evidence file or of any
   key in it. Report each by file:line. State plainly that you can only
   see consumers inside this repository.

I. Report any change that serves no stated part of the intent above.
   Scope creep is a finding, not a favour.

REPORT
1. Verdicts, in order A through I.
2. A single overall verdict: ACCEPTABLE, or NOT_ACCEPTABLE with the
   blocking findings listed.
3. What you could not determine without compiling or running.
4. Do not propose fixes. Do not edit. Do not compile. Stop.
