TASK_ID: ETL-0909-R3R4-COMPOSITION-TEST04
TYPE: BOUNDED LOCAL TEST REPAIR AND EVIDENCE ADDENDUM

LANGUAGE
Use English for all development-environment conversation, code comments,
reports, status messages, and artifacts.

OBJECTIVE
Close the material F-1 coverage gap identified by the continuation of
ETL-0909-R3R4-INDEPENDENT-REVIEW02 reviewing
ETL-0909-R3R4-CORRECTION-TEST03.

Preserve the five accepted technical corrections:
B-1, C-2, C-1, C.3, and B-2.

Also correct the F-2 rationale and add the missing F-3 evidence reference.
Do not reopen unchanged accepted work or claim that this task fixes or
runtime-qualifies the original product file-write defect.

OWNER DISPOSITION PROPOSED BY THIS PROMPT
Submission of this prompt authorizes this bounded task.

For F-2, retain the existing conservative independent classification of
"observedMarkdownMapping ID". Correct the inaccurate explanation of its
independence. Record the possible duplicate-cause limitation explicitly.

This is a prospective choice to preserve existing behavior, not permission
to rewrite historical evidence, waive other cause-identity requirements,
or grant runtime/product acceptance.

AUTHORITATIVE INPUTS
Use the existing local references and machine evidence.

Reference folder:
  /ETL Copilot Reference v2
Local mirror, only if accessible:
  C:\docs\ETL_Copilot_Reference_v2

Existing TEST03 input location, if present:
  C:\docs\ETL_0909_R3R4_TEST03_INPUTS

Expected working repository, subject to evidence verification:
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Read:
1. Current state, changelog, and the adopted agile repair contract.
2. The complete governing TEST03 brief and its incorporated TEST02
   requirements.
3. The complete REVIEW02 continuation report and its machine result.
4. The relevant referenced machine records and actual source.

Apply current owner decisions over older documentary state. Do not treat
the reference state as live source verification.

Resolve REVIEW02 by bounded direct-child discovery under:
  C:\docs\ETL-0909-R3R4-INDEPENDENT-REVIEW02-*

Identify the continuation through its task identity and reviewed TEST03
evidence references. Do not select an arbitrary newest folder.

Follow exact recorded paths to TEST03 and other necessary evidence.
Do not recursively scan C:\docs, unrelated repositories, user profiles,
chat history, or consumer workspaces.

The original blocked REVIEW02 result is historical. Its preserved BLOCKED
status does not override the continuation result.

Use machine records for hashes, byte counts, paths, and source identities.
Never transcribe a hash from a screenshot or reconstruct missing bytes.

PREFLIGHT
Before source mutation:

- Confirm no writer, runner, or Extension Host is using this worktree.
  If one is active, stop and report WAITING; do not terminate it.
- Authenticate the reviewed TEST03 post-state against all five live
  reviewed source files using the continuation's machine evidence.
- Confirm repository, branch, HEAD, staging, and dirty-path set against
  the accepted end-state records.
- Resolve any required glossary identity through the governing machine
  manifest. Do not replace, normalize, or re-pin the glossary.
- Create a new exclusive external evidence directory for this task.
- Preserve exact pre-edit copies of the two authorized files.

If a required baseline or authority record is missing or mismatched,
report the precise blocker before mutation. Do not repair the baseline.

ALLOWED REPOSITORY CHANGES
Only:
1. src/test/b3OutcomePolicy.unit.test.ts
   Harness composition, necessary fixture metadata, and meaningful tests.

2. src/test/runTest.ts
   Comment-only correction for F-2. No executable-token changes.

Do not modify b3OutcomePolicy.ts, suite/index.ts, the focused Host test,
product implementation, configuration, dependencies, or generated out/.

If closing F-1 actually requires production behavior changes, stop with
the exact reason and proposed scope. Do not expand this task automatically.

F-1: REPAIR THE COMPOSED UNIT HARNESS
Inspect the actual runner sequence and the current
simulateFocusedRun -> finalize() implementation.

The harness currently attributes fixture comparisons directly, omitting
the real binding, integrity-failure recording, and exemption stages.

Make the harness exercise the same sequence as the actual runner:

1. bindComparisonProvenance
2. Record each returned integrity failure as the corresponding independent
   infrastructure cause, using the actual runner's identity/stage mapping.
3. applyCountSettlementExemptions with the actual retained run observation
   and the same relevant arguments used by the runner.
4. attributeComparisonMismatches

Call the actual exported pure policy functions.
Do not copy their decision logic, hardcode their expected decisions,
or import/execute the runner or extension to obtain them.

Provide explicit fixture provenance and declared coverage where required.
Preserve deliberately malformed metadata in negative cases; do not
silently replace it with a valid default.

Keep comparison measurements and expectations intact. Test handling of
their provenance and attribution rather than rewriting raw outcomes.

REQUIRED EXECUTED COVERAGE
Add or strengthen focused cases proving:

- Correctly bound comparisons pass through the complete sequence.
- The case-31 abnormal-termination scenario genuinely receives the
  intended runTestsOutcome exemption.
- That exempted comparison does not itself produce the comparison cause
  that would accidentally make the test pass.
- The abnormal-termination infrastructure cause remains independently
  recorded and preserves the required BLOCKED result.
- Binding integrity failures actually enter the ledger with the expected
  identity; checking only the final verdict is insufficient.
- Shifted/reordered or malformed provenance cannot suppress an unrelated
  failing comparison.
- Relevant product, infrastructure, and partial-attribution outcomes
  remain consistent when passed through this composed path.

Preserve the existing 33 test obligations. Do not target an invented final
test count. Explain any changed fixture expectations individually.

Do not reverse the already accepted case-30 surplus-provenance finding:
a surplus entry outside declared coverage is not read as a binding for
another row; valid existing bindings may remain usable while the length
integrity failure remains an independent infrastructure cause.

Show at least one meaningful regression failing with the prior harness
composition and passing with the repaired composition. Use an authenticated
pre-edit copy in the external evidence directory, preserving the same
regression assertion. Do not manufacture a red result with a syntax error,
missing import, or unrelated protocol change.

If a genuine before/after regression cannot be demonstrated within this
scope, report the limitation explicitly; never label another failure as
the required regression.

F-2: COMMENT CORRECTION ONLY
Inspect the actual focused comparison and observer assignment underlying:
  observedMarkdownMapping ID
  Markdown mapping:Active Mappings first ID

Correct the runTest.ts comment so it does not falsely describe these as
independent data when the source shows the same rendered identifier and
expectation.

State that the independent classification is intentionally retained under
the governing conservative contract choice. Record its possible duplicate
cause as a limitation.

Keep classification, protocol, linking behavior, comparison values, and
expectations unchanged. Demonstrate that the runTest.ts diff is comment-only.

Do not edit the old static-trace-and-maps.md. Correct its explanation in
a new evidence addendum with an exact reference to the superseded claim.

F-3 AND F-4: PRESERVE HISTORY
F-3:
Authenticate the retained TEST03 a7-unit-final attempt using its existing
command, output, source provenance, and inventory records.

Add a new evidence addendum explaining that TEST03 result.json omitted
this attempt even though the report and retained evidence include it.
Record actual machine values. Do not rerun TEST03 merely to recreate an
index entry, and do not overwrite its result.json.

F-4:
Preserve the known original REVIEW02 result.json formatting discrepancy
and the continuation's stated evidentiary limitation.
Do not reconstruct original bytes, assign an unproven actor, or claim
complete semantic equivalence. Do not reopen this historical issue unless
new evidence materially affects the present baseline.

VALIDATION AUTHORITY
Allowed:
- Read-only inspection and bounded machine measurements.
- Existing installed compiler/test tooling used directly.
- Compilation of only the pure policy/unit-test closure.
- Execution of only those local unit tests.
- Temporary regression variants and emitted JavaScript inside this task's
  external evidence directory.

Use the existing targeted procedure, with all emission outside the
repository. Disable incremental/build-info, declarations, and source maps
unless strictly necessary and already authorized by the governing brief.

Do not run package scripts that expand into other suites or runtime work.
Do not install dependencies or use a command that may download tooling.

No project-wide rebuild is needed for a unit-harness change and a
comment-only runner change. Reuse unchanged accepted evidence and label
it as inherited rather than newly measured.

Within this scope, resolve ordinary compile/test failures in the same
task, preserving meaningful failed attempts. Do not create a new task
for every iteration. Stop when the stated coverage is sufficiently verified.

PROHIBITED
No project runner, producer, Extension Host, product execution, A3,
consumer workspace writes, package installation, packaging, release,
Git mutation, pending-editor-change resolution, glossary replacement,
or reference-state/changelog update.

Do not launch another writer or delegate work on the same worktree.
Do not broaden this into investigation of the original product-write
failure.

The original error/reproduction evidence remains a separate prerequisite
for its later product scenario; its absence does not block this F-1 repair.

DELIVERABLES
Return a concise English report and machine-readable result containing:

- Task status and exact evidence directory.
- Baseline identities and their machine-record provenance.
- Exact task-only diff and pre/post identities for changed files.
- Proof that runTest.ts changes are comment-only.
- Commands, exit codes, final test counts, and genuine regression evidence.
- A requirement-to-executed-test mapping for F-1.
- Separate dispositions for F-2, F-3, and retained F-4 limitations.
- Newly measured versus inherited checks.
- Any remaining blocker or coverage gap.

Preserve all previous reports and evidence packages.

End with these fields using actual results:
TASK_ID:
STATUS:
F1_COMPOSED_COVERAGE:
F2_RATIONALE_AND_RETAINED_LIMITATION:
F3_A7_EVIDENCE_ADDENDUM:
F4_HISTORICAL_LIMITATION:
CHANGED_REPOSITORY_PATHS:
LOCAL_TEST_RESULT:
EVIDENCE_ROOT:
REPORT_PATH:
RESULT_PATH:
HOST_OR_PRODUCT_EXECUTED: NO
ORIGINAL_PRODUCT_WRITE_FIX_VERIFIED: NO
INDEPENDENT_ACCEPTANCE_OF_THIS_DELTA: NOT_GRANTED

NEXT GATE
Return this small delta and its evidence for bounded independent review.
Do not repeat the complete review of unchanged accepted corrections.

After that acceptance, follow the dependency roadmap for separately
authorized protocol-3 build/provenance and focused runtime work.
Neither this task nor its unit-test result grants Host or release authority.

Stop after returning the report.
