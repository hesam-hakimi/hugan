IMPLEMENTATION ONLY. No compile, no test execution, no runner, no
Extension Host, no commit, no stage, no version bump, no packaging.
Edit only the file named below. Do not touch any other file.
Do not self-certify: report what you changed and stop. An independent
review follows.

Repository: C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
Branch:     fix/workspace-write-completion-0.3.148  (do not switch)
File:       src/test/runTest.ts  (already modified, uncommitted)

GOAL
The runner's evidence file must never present a literal value as an
observation. Every field in the emitted evidence must be either
  (a) computed from a runtime value at the moment of writing, or
  (b) placed under an explicit top-level `declarations` block whose
      meaning is "asserted by the author, not observed by the runner".

REQUIRED CHANGES
1. In the finalProcessIntegrity block (reported near runTest.ts:1943-1949):
   a. Remove `runnerAliveWhileWritingEvidence: true`. Do not replace it
      with another literal. If a genuinely observable substitute exists
      (for example the runner's own process.pid plus a timestamp
      captured immediately before the write call), add that instead,
      named so it cannot be misread as a liveness claim.
   b. Move `parentPostExitCheckRequired: true` out of
      finalProcessIntegrity into a new top-level `declarations` object:
        declarations: {
          parentPostExitCheck: { required: true, implemented: false }
        }
   c. Leave observedAfterRunTests, hostPidStates, runnerPid unchanged
      unless any of them is also a literal. If so, report it and apply
      the same rule.

2. Audit the rest of the evidence object assembled in the same function
   for any other literal true/false/string presented under an
   observation-shaped key. Apply the same rule to each and list it in
   the report. Do not audit other files.

3. Update the TypeScript type for the evidence object so that, where
   expressible, the compiler would reject a future literal in an
   observation field. Where not expressible, add a one-line comment at
   the field: "must be computed, never literal".

CONSTRAINTS
- Do not change the manifest cardinality check, evidence write ordering,
  exit-code handling, or any other known defect in this file. Those are
  separate tasks.
- Do not change the evidence file path, name, write flag, or encoding.
- Do not add, remove, or rename any evidence field other than those
  named above or found in step 2.
- Preserve existing behaviour for every field you did not touch.

REPORT, in this order
1. Complete unified diff of src/test/runTest.ts.
2. Table: field | before | after | rule applied (a or b).
3. Every consumer inside this repository that reads a field you moved or
   removed, by file:line, found by search only. Do not modify consumers.
4. What you could not verify without compiling, stated plainly.
5. Stop. Do not run tsc, do not run tests, do not commit.
