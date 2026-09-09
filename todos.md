TASK_ID: ETL-0909-R3R4-COMPOSITION-INDEPENDENT-REVIEW03
TYPE: BOUNDED INDEPENDENT REVIEW — TEST04 DELTA ONLY

LANGUAGE
Use English for all development-environment conversation, reports, status
messages, and engineering artifacts.

OBJECTIVE
Independently review ETL-0909-R3R4-COMPOSITION-TEST04.

Determine whether its narrow two-file delta genuinely closes the material F-1
composed-unit-coverage gap while preserving the previously accepted B-1, C-2,
C-1, C.3, and B-2 source behavior.

Also verify the bounded F-2 comment correction, F-3 evidence addendum, and F-4
historical-preservation claim.

This is not a full re-review of ETL-0909-R3R4-CORRECTION-TEST03 and does not
authorize product, runner, producer, Extension Host, packaging, installation,
release, Git mutation, source repair, or reference-state mutation.

REVIEWER INDEPENDENCE
Act only as an independent reviewer.

Do not edit repository source, TEST04 evidence, earlier evidence packages,
glossaries, reference files, or Git state.

If a defect is found, report it precisely and propose the smallest correction.
Do not implement it in this task.

If this review task is already running on the same worktree, wait for it.
Do not start a duplicate reviewer while another writer or reviewer is active.

SOURCE AND EVIDENCE RESOLUTION
Expected repository:
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Locate the TEST04 evidence root through bounded direct-child discovery:
  C:\docs\ETL-0909-R3R4-COMPOSITION-TEST04-*

Select it by its machine-readable task identity, not by newest timestamp.

Resolve the governing REVIEW02 continuation and its reviewed TEST03 root through
the cross-references recorded in TEST04. Do not recursively scan C:\docs or
unrelated workspaces.

Read completely:

1. TEST04 report.md and result.json.
2. TEST04 post/task.diff.
3. TEST04 pre-edit copies of the two authorized files.
4. TEST04 attempt records for the regression-red and unit-final runs.
5. TEST04 F-2 and F-3 addenda.
6. The relevant REVIEW02 continuation findings defining F-1 through F-4.
7. The current versions of:
   - src/test/b3OutcomePolicy.unit.test.ts
   - src/test/runTest.ts
   - src/test/b3OutcomePolicy.ts
8. Only the relevant actual runner and focused-test regions needed to establish
   the production sequence and F-2 datum relationship.

Use machine records for paths, hashes, byte counts, commands, and results.
Do not transcribe identities from screenshots.

PREFLIGHT
Perform read-only checks establishing:

- No active writer, runner, compiler, or Extension Host is using the worktree.
- Repository path, branch, HEAD, staging, and dirty-path set match the TEST04
  end-state record.
- Both current authorized files match TEST04 post-state identities.
- The other three previously reviewed source files still match the accepted
  REVIEW02 continuation endpoints.
- TEST04 evidence was created outside the repository.
- No unaccounted repository path was modified by TEST04.

If the current live state has drifted, stop and report the exact mismatch.
Do not repair or reinterpret the baseline.

INDEPENDENT F-1 REVIEW
Verify from actual source—not only from TEST04 prose—that
simulateFocusedRun.finalize() now executes the same relevant order as runTest:

1. bindComparisonProvenance
2. record every integrity failure as its own infrastructure cause
3. applyCountSettlementExemptions using the retained oracle
4. attributeComparisonMismatches

Confirm:

- The harness calls actual exported pure policy functions.
- It does not copy production decision logic.
- It does not import or execute the runner or extension.
- Fixture provenance and declared coverage are explicit.
- Deliberately malformed fixture metadata reaches binding unrepaired.
- Raw comparison results and expected values are not rewritten.
- RunResult exposes sufficient intermediate decisions to test composition,
  rather than asserting only the final verdict.

Review every new or changed assertion and independently map it to:

- correct composition;
- actual runTestsOutcome exemption;
- absence of the exempted comparison cause;
- independent preservation of the abnormal-termination cause and BLOCKED result;
- integrity-failure ledger identity;
- reordered/malformed provenance remaining fail-safe;
- unchanged product, infrastructure, mixed, and partial-attribution behavior.

Confirm that accepted case-30 surplus-provenance semantics were not reversed.

REGRESSION AUTHENTICITY
Authenticate the regression-red construction.

Verify that it consists of:

- the exact authenticated pre-edit unit harness;
- the same regression assertion used to test the repaired composition;
- the corresponding policy source identical to the live reviewed policy;
- no syntax error, missing import, protocol alteration, or artificial failure.

Confirm independently:

- both variants compile successfully;
- the old composition fails specifically for the intended behavioral reason;
- the repaired composition passes;
- the final local unit result is genuinely 35 tests, 35 passes, 0 failures,
  0 pending, exit 0;
- all previous 33 obligations remain represented and exactly two meaningful
  tests were added.

F-2 REVIEW
Verify that the runTest.ts executable token stream is identical before and after
TEST04 and that only comments changed.

Check the underlying source expressions for observedMarkdownMapping.mappingId
and "Markdown mapping:Active Mappings first ID".

Determine whether the revised comment accurately states:

- the comparison and observation derive from the same underlying datum and
  expectation;
- the independent classification was deliberately retained under the explicit
  conservative owner disposition;
- a duplicate-cause limitation remains recorded;
- no claim of full B3-5 semantic resolution is made.

Confirm that the old static-trace-and-maps.md was preserved and that the new
addendum identifies and corrects its superseded statement without rewriting
history.

F-3 AND F-4 REVIEW
For F-3, authenticate the retained TEST03 a7-unit-final attempt from its existing
machine records. Confirm that the new addendum records the omission without
overwriting TEST03 result.json or falsely claiming a rerun.

For F-4, confirm the prior REVIEW02 report and result were not changed by
TEST04. Preserve the limitation that original result.json bytes are
unrecoverable and actor attribution is unknown.

Do not require reconstruction of missing historical bytes.

BOUNDED INDEPENDENT EXECUTION
You may independently compile and run only the pure local policy/unit-test closure
needed to verify the TEST04 delta, using already-installed tools.

All emitted or temporary files must be placed in a new exclusive external review
directory.

Do not:

- run the project-wide compiler;
- run package scripts;
- run the focused Host test;
- run the runner, producer, extension, or product;
- install or download dependencies;
- emit files into the repository;
- alter Git state.

One independent final compile and unit-test execution is sufficient if the
retained regression evidence is authenticated. Do not repeat unchanged accepted
TEST03 tests merely to recreate evidence.

REVIEW DECISION
Return one of:

ACCEPTED
  The F-1 delta is independently supported at the pure source/unit boundary,
  F-2 is comment-only and accurately bounded, F-3/F-4 are preserved, and no
  material defect is found.

ACCEPTED_WITH_LIMITATIONS
  The delta is technically acceptable, but a non-material limitation remains.
  Name it and state its exact downstream effect.

CHANGES_REQUIRED
  A material technical, test-validity, preservation, or evidence defect exists.
  Identify the precise requirement, source location, and smallest correction.

BLOCKED
  Required baseline or evidence cannot be authenticated. Identify the exact
  missing or mismatched record.

Do not grant runtime, Host, product-write, packaging, installation, or release
acceptance under any outcome.

DELIVERABLES
Create a new exclusive evidence directory outside the repository containing:

- report.md
- result.json
- independent source/diff identity measurements
- independent test execution record, if executed
- end-state preservation measurement

The report must distinguish:

- independently measured facts;
- facts authenticated from retained evidence;
- inherited earlier acceptance;
- limitations not tested by this review.

End with:

TASK_ID: ETL-0909-R3R4-COMPOSITION-INDEPENDENT-REVIEW03
REVIEWED_TASK: ETL-0909-R3R4-COMPOSITION-TEST04
REVIEW_RESULT:
F1_COMPOSED_COVERAGE_ACCEPTED:
F2_COMMENT_ONLY_AND_LIMITATION_ACCEPTED:
F3_ADDENDUM_ACCEPTED:
F4_HISTORY_PRESERVED:
REGRESSION_EVIDENCE_ACCEPTED:
LOCAL_UNIT_RESULT:
CHANGED_BY_REVIEWER: NONE
HOST_OR_PRODUCT_EXECUTED_BY_REVIEWER: NO
ORIGINAL_PRODUCT_WRITE_FIX_VERIFIED: NO
RUNTIME_OR_RELEASE_ACCEPTANCE: NOT_GRANTED
REVIEW_ROOT:
REPORT_PATH:
RESULT_PATH:
NEXT_CONDITIONAL_GATE:

NEXT CONDITIONAL GATE
If ACCEPTED or ACCEPTED_WITH_LIMITATIONS:
recommend a separately authorized protocol-3 build/provenance and focused
runtime task. Do not launch it automatically.

That later runtime task must still distinguish STTM read-only validation from
the guarded product file-write scenario. The original product-write defect
cannot be declared fixed until its exact error and reproducible consumer input
are available and a separately authorized guarded write test succeeds.

If CHANGES_REQUIRED:
recommend only the smallest bounded correction over the TEST04 delta.

If BLOCKED:
report the exact evidence or baseline blocker without repairing it.

Stop after returning the review report.
