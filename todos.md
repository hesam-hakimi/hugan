IMPLEMENTATION ONLY — REVERT AND SIMPLIFY. No compile, no test
execution, no runner, no Extension Host, no commit, no stage, no version
bump, no packaging. Edit only src/test/runTest.ts. Do not self-certify.

CONTEXT
An independent review returned NOT_ACCEPTABLE. The replacement fields
added earlier are tautological: they cannot ever be false, so they carry
no information. The owner's decision is to delete them and add nothing
in their place. Do not propose a better replacement. Do not argue.

REQUIRED CHANGES

1. In the finalProcessIntegrity emission block, delete these two fields
   entirely:
     evidenceWriterPid
     evidenceWriterSampledAtUtc
   Add nothing in their place. finalProcessIntegrity must end with the
   three fields that were there originally: observedAfterRunTests,
   hostPidStates, runnerPid.

2. In the declarations block, change parentPostExitCheck from an object
   to the flat boolean the owner authorised:
     declarations: { parentPostExitCheckRequired: true }
   Delete the `implemented` sub-field. It was never authorised.

3. Update both interfaces to match exactly:
   - Remove evidenceWriterPid and evidenceWriterSampledAtUtc from the
     RunnerEvidence finalProcessIntegrity shape.
   - Change RunnerEvidenceDeclarations to a single flat boolean field
     parentPostExitCheckRequired.

4. Rewrite the two doc comments so that every sentence in them is true
   of the file as it stands after this revert. Specifically:
   - Do not claim that all remaining literals are marked. They are not.
   - Do not claim that every marked field is produced at the moment of
     writing. Several are captured earlier in the run.
   - Do not assert an exhaustive taxonomy of fields.
   Say only what you can verify by reading the file. If you cannot make
   a sentence true, delete the sentence rather than soften it.

CONSTRAINTS
- Do not touch retriesOrRelaunches. It stays the literal 0 with its
  existing comment. It is a known open item, not this task.
- Do not touch taskId, activationOrderObservation, the manifest
  cardinality check, evidence write ordering, exit-code handling, or any
  other known defect.
- Do not change the evidence file path, name, write flag, or encoding.
- Add no new field, type, comment, or refactor beyond the above.

REPORT
1. Unified diff of this revert only.
2. The complete list of keys in finalProcessIntegrity and in
   declarations after this change.
3. State the resulting JSON shape delta from the original, in one line.
4. Quote both rewritten doc comments in full and, for each sentence,
   state the file:line evidence that makes it true.
5. Anything you could not verify without compiling.
6. Stop. Independent review follows.
