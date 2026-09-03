IMPLEMENTATION ONLY — SCOPE CORRECTION. No compile, no test execution,
no runner, no Extension Host, no commit, no stage, no version bump, no
packaging. Edit only src/test/runTest.ts. Do not self-certify.

CONTEXT
Your previous edit exceeded the authorised scope. The owner accepts part
of it and is reverting the rest. This is not a rejection of quality; it
is a scope decision. Do not re-argue it, do not re-apply anything you
are told to revert, and do not introduce new improvements.

KEEP EXACTLY AS YOU LEFT THEM
1. finalProcessIntegrity.runnerAliveWhileWritingEvidence — removed,
   replaced by evidenceWriterPid and evidenceWriterSampledAtUtc.
2. finalProcessIntegrity.parentPostExitCheckRequired — moved into
   declarations.parentPostExitCheck { required, implemented }.
3. finalProcessIntegrity.observedAfterRunTests — now computed from
   runTestsOutcome.
4. The RunnerEvidenceDeclarations interface and the declarations block.
5. The "must be computed, never literal" comments.

REVERT TO THE PRE-EDIT VALUE
6. runner.retriesOrRelaunches — restore the literal 0. Your derived
   expression encodes a definition of "retry" that no specification in
   this repository states. Restore the literal and add exactly this
   comment on the line:
     // literal: retry semantics undefined; see open item
7. activationOrderObservation.contractual — restore it in place as the
   literal false. Remove declarations.activationOrderContractual.
8. activationOrderObservation.source — restore it in place as the
   original literal string. Remove declarations.activationOrderSource.

Items 7 and 8 are reverted because the emitted JSON shape must not
change beyond what item 2 already requires. declarations must therefore
contain parentPostExitCheck only.

DECIDED BY THE OWNER — DO NOT CHANGE
9. taskId stays exactly where and as it is. An identifier is not an
   observation. Do not move it, do not comment on it further.

TYPE SHAPE
10. Keep the RunnerEvidence interface, but update it so it matches the
    reverted JSON shape exactly: activationOrderObservation regains
    contractual and source; declarations narrows to parentPostExitCheck
    only.
11. If `satisfies` cannot be used without a TypeScript version you
    cannot confirm, replace it with a plain type annotation and say so.
    Do not leave a construct whose support you have not verified.

CONSTRAINTS
- Do not touch the manifest cardinality check, evidence write ordering,
  exit-code handling, or any other known defect.
- Do not change the evidence file path, name, write flag, or encoding.
- Do not add any field, comment, type, or refactor not named above.
- Do not "improve" anything you notice along the way. Report it instead.

REPORT, in this order
1. Unified diff of this correction only, against the state you left the
   file in.
2. The complete list of top-level keys in the emitted JSON, before your
   first edit and after this correction, side by side, so the shape
   delta is exactly visible.
3. Confirm in one line that the only JSON shape change from the original
   is: two keys removed from finalProcessIntegrity, two keys added to
   finalProcessIntegrity, one new top-level key `declarations`.
4. Anything you could not verify without compiling.
5. Stop. Independent review follows.
