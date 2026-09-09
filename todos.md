TASK_ID: ETL-0909-PROTOCOL3-RUNTIME-INDEPENDENT-REVIEW01
TYPE: BOUNDED INDEPENDENT REVIEW OF RETAINED BUILD AND RUNTIME EVIDENCE

ENVIRONMENT AND LANGUAGE
Use a fresh independent LOCAL Windows VS Code Agent reviewer.
Use English for all conversation and artifacts.

OBJECTIVE
Review ETL-0909-PROTOCOL3-FOCUSED-RUNTIME01 and determine whether its
source -> checked build -> promotion -> canonical manifest -> actual run
relationship supports acceptance of the nominal protocol-3 focused scenario.

Reported outcome:
- RUNTIME_EVIDENCE_OBTAINED
- No source changes
- 11 compiler outputs promoted within the four-source boundary
- One runner invocation, one Host launch, no retries
- Eight focused tests passed
- Host exit 0, parent PASS/0, empty cause ledger
- No consumer product writes

These are claims to authenticate, not predetermined review conclusions.

AUTHORITY
This prompt authorizes read-only repository/evidence inspection and new
review-only measurements and reports in an exclusive external directory.

Do not compile, run tests, import/execute project modules, launch the runner,
producer or Host, promote outputs, modify Git, or edit existing evidence.

Read-only analysis helpers may parse files, compare bytes, compute identities,
and assess retained records. Inspect reused helpers before use; never run a
helper that writes to a prior evidence directory.

Do not repeat accepted TEST03/TEST04 source or unit reviews.
Do not implement fixes during this review.

RESOLVE THE ACTUAL EVIDENCE
Expected repository:
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Resolve the reviewed bundle through bounded direct-child discovery:
  C:\docs\ETL-0909-PROTOCOL3-FOCUSED-RUNTIME01-*

Select by result.json task identity and evidence relationships, not timestamp.

Read the complete RUNTIME01 brief, report.md, result.json, and the following
records, resolving their actual paths through the report:

- measurements/p3-preflight.json
- measurements/p3-process-scan.json
- attempts/b1-checked/build-result.json
- attempts/b1-checked/build-diagnostics.json
- Compiler read-set and source/output association records
- promotion-plan.json and promotion-journal.json
- Destination pre-copies and staged/promoted outputs
- measurements/p3-qa-materialization.json
- run-root-creation-receipt.json and execution-plan.json
- pre-launch-recheck.json
- run-status.json, run-stdout.txt, run-stderr.txt, supervisor.log
- Original manifest/result artifacts and their preserved copies
- measurements/p3-run-assessment.json
- measurements/p3-run-assessment-correction.json
- measurements/p3-end-state.json
- measurements/p3-buildinfo-resolution.json
- addendum/l1-superseded-claim-reference.md

Follow exact cross-references to REVIEW03 and the accepted C1 build/run
records only where needed to authenticate baseline, outputs, Host or fixture.

Do not recursively scan C:\docs or unrelated workspaces.
Do not request credentials, profile dumps, or consumer data.

Read expected hashes from machine records. Never transcribe them from images
or use a fresh measurement as its own expected baseline.

RUNTIME01 reported that 01_CURRENT_STATE.json and
08_DECISIONS_AND_CHANGELOG.md were inaccessible after bounded probes.
Assess this against its “where accessible” instruction. Do not claim they
were read or create a new blocker solely from their optional absence when
the governing brief and necessary original evidence are available.

PREFLIGHT
Confirm no conflicting writer/runner/Host is active.
An ordinary editor or language server alone is not a blocker.
Do not remove locks or terminate processes.

Authenticate:
- Repository/common-Git identity, branch, HEAD, staging and dirty-path set.
- All five accepted reviewed source identities.
- Live promoted outputs against RUNTIME01's recorded post-state.
- Required retained evidence and copy/original relationships.

Use git --no-optional-locks for read-only Git checks.

Current drift must be reported separately from the historical run's evidence.
Do not repair drift or silently replace the reviewed baseline.

Create a new exclusive external review directory:
  C:\docs\ETL-0909-PROTOCOL3-RUNTIME-INDEPENDENT-REVIEW01-<UTC>-<GUID>

BUILD AND PROMOTION REVIEW
Verify from retained compiler records and inspected build-helper source:

- A checked Program using the actual configuration and installed compiler.
- Configuration, options, global, syntactic, semantic, declaration and emit
  diagnostics were captured.
- noEmitOnError=true, successful emit, zero reported errors/warnings.
- Physical writes were redirected to external staging.
- Incremental/build-info persistence was prevented.
- Source identities came from actual compiler reads.
- Source/output associations are supported by compiler and source-map data,
  rather than guessed filenames.

Reconcile the reported 2028 emissions against 2020 existing outputs:
2009 identical, 11 different, eight staged-only unit companions.

Authenticate that:
- The promotion plan preceded destination writes.
- All 11 changes belong to compiler companions of:
    src/test/runTest.ts
    src/test/b3OutcomePolicy.ts
    src/test/suite/index.ts
    src/test/suite/sttmRealHostStructuredResult.test.ts
- Five identical companions were skipped.
- Eight staged-only unit companions were not promoted.
- Every replacement has a valid preimage, journal entry and read-back identity.
- No required runtime dependency mismatch was omitted.
- No output outside the frozen plan changed.

Do not rebuild merely to reproduce already-retained evidence.
If provenance is insufficient, identify the exact unsupported relationship.

THREE MEASUREMENT CORRECTIONS
Independently assess these corrections without overwriting their originals:

1. Output-path keys:
   The original C1 inventory was out/-relative while the promotion journal
   was repository-relative. Confirm the normalization maps both to the same
   files without collisions, omissions, or hidden content mismatches.

2. Declared coverage:
   The initial assessment confused the focused suite's 49 comparisons with
   the runner's derived Host-evidence prefix.
   Recompute from actual source and retained runtime data:
     49 focused-suite comparison records
     124 derived Host-evidence rows
     40 runner-owned measurements
     164 total runner comparisons
   Verify the correction supersedes only the affected fields and preserves
   the original record. Do not infer declaredCoverage from a count alone.

3. BUILD_INFO_CHANGED:
   Check the claimed null-versus-omitted-field representation difference
   against file existence and byte identities at the recorded stages.
   Determine whether it is a helper-record discrepancy or actual drift.
   A successful final verdict alone cannot settle this question.

MANIFEST, HOST, FIXTURE AND RUN REVIEW
Verify:
- Prepared VS Code 1.135.0 and dependency identities from prior records and
  RUNTIME01 measurements.
- The quarantine was valid at the recorded execution time; do not renew it.
- The authenticated 23-file QA seed/copy relationship and unchanged workbook.
- RUN_ROOT was exclusively created, empty at launch, disjoint from QA and
  TASK_ROOT, and compatible with the real runner's containment contract.
- Supported child settings and ordered development/dependency paths.
- No pre-seeded nonce, delivery or acceptance fields.
- The protected set was derived from current policy, with all four promoted
  runtime JavaScript modules covered.
- Fresh manifest generation and canonical acceptance occurred in the same
  authorized runner invocation.
- Manifest entries match the promoted bytes; digest differences from C1 are
  explained by authorized promotion.
- Exactly one runner and one Host executed, with no retries or hidden probes.
- Host/parent exits, timing, process ownership, cleanup and post-exit checks
  are supported by original logs and records.

Do not equate a matching post-run digest with proof of prelaunch acceptance.
Identify the evidence supporting each phase separately.

NOMINAL RUNTIME RESULT
Independently verify:
- Protocol version 3 was produced and accepted in the focused result path.
- Nonce, suite identity, loaded-file identity, delivery completion and QA
  correlation agree across the original artifacts.
- Eight unchanged authored tests ran and passed, with zero pending/failures.
- Host comparisons and runner comparisons passed under their actual schemas.
- Parser cardinality was one, outcome fulfilled, wrapper restoration succeeded,
  and the recorded tool invocation count was one.
- Structured and Markdown mapping identities and projections match their
  existing authenticated expectations.
- The parent result is PASS/0 with an empty ledger.
- Both evidence artifacts reached their primary destinations.
- Protected post-exit checks passed and no task-owned processes remained.

For the bind -> integrity handling -> exemption -> attribution sequence,
distinguish directly recorded runtime facts from conclusions inferred through
the authenticated executed source path.

Zero integrity failures means the failure-handling loop body was not exercised.
With all comparisons passing, no actual waiver or failing attribution
disposition was demonstrated. Do not describe those branches as runtime-proven.

LIMITATIONS AND PRESERVATION
Verify the L-1 addendum identifies the missing TEST02 section 5.2 reference
without changing the original brief, classification, or prior evidence.

Carry forward:
- The retained F-2 duplicate-cause limitation.
- The known F-4 historical artifact limitation.
- The eleven explicitly unexercised runtime categories.
- The distinction between STTM read-only validation and guarded product writes.

Review R5 disclosures against actual stderr/logs. Report the observed inherited
MCP identity and unauthenticated GitHub probes accurately. Do not claim absolute
offline isolation, initiate network probes, or expand this into a new investigation.

Verify source, output, QA, consumed evidence and relevant Host preservation.
Report unexpected changes precisely; do not normalize them away.

DECISION AND DELIVERABLES
Return ACCEPTED, ACCEPTED_WITH_LIMITATIONS, CHANGES_REQUIRED, or BLOCKED.

Acceptance applies only to the authenticated build/promotion/manifest relationship
and the nominal protocol-3 focused runtime scenario. It grants no acceptance of
unexecuted failure branches, full B3, consumer writes, installed .148, or release.

For each finding state:
- Concrete requirement and evidence location.
- Whether it affects acceptance.
- Smallest necessary correction or missing record.
Do not create new requirements solely to remove a disclosed non-material limit.

Write report.md, result.json, and only necessary review measurements.
Separate independently measured facts, authenticated retained evidence,
inherited acceptance, and remaining uncertainty.

End with:
TASK_ID: ETL-0909-PROTOCOL3-RUNTIME-INDEPENDENT-REVIEW01
REVIEWED_TASK: ETL-0909-PROTOCOL3-FOCUSED-RUNTIME01
REVIEW_RESULT:
BUILD_AND_PROMOTION_ACCEPTED:
CANONICAL_MANIFEST_AND_RUN_CORRELATION_ACCEPTED:
NOMINAL_PROTOCOL3_RUNTIME_ACCEPTED:
MEASUREMENT_CORRECTIONS_ACCEPTED:
PRESERVATION_ACCEPTED:
MATERIAL_FINDINGS:
RETAINED_LIMITATIONS:
REPOSITORY_CHANGED_BY_REVIEWER: NONE
PROJECT_COMPILER_TEST_RUNNER_OR_HOST_EXECUTED_BY_REVIEWER: NO
ORIGINAL_PRODUCT_WRITE_FIX_VERIFIED: NO
FULL_B3_INSTALLED_OR_RELEASE_ACCEPTANCE: NOT_GRANTED
REVIEW_ROOT:
REPORT_PATH:
RESULT_PATH:
NEXT_CONDITIONAL_GATE:

NEXT GATE
If accepted, identify the smallest next required gate from the dependency
roadmap and the minimum error/reproduction evidence needed for the original
product-write scenario. Distinguish actual blockers from deferred follow-ups;
do not automatically turn all eleven unexercised categories into separate tasks.

If changes are required or evidence is blocked, propose only the specific
correction or missing evidence needed. No automatic rebuild, rerun, repair,
state update, installation or release follows this review.

Stop after delivering the report.
