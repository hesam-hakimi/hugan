TASK: PHASE_1B_3N_W_INDEPENDENT_DIFF_AND_BASELINE_REVIEW_READ_ONLY

ROLE

Act as a fresh independent reviewer. Do not use the Agent that implemented Phase 1B.3N-V to certify its own changes.

Use the normal local GitHub Copilot Agent, not the ETL Orchestrator.

This task is strictly read-only. You may inspect the repository, Git state, source files, and retained evidence. You may not edit, format, restore, stage, compile, test, invoke the runner, launch an Extension Host, install, package, commit, merge, publish, or delete anything.

REPOSITORY

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:
fix/workspace-write-completion-0.3.148

Expected HEAD:
45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

PRE-V PROTECTED STATUS

M .github/templates/request.md
M src/extension.ts
M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

PHASE V REPORTED CHANGES

* src/test/runTest.ts
* src/test/suite/index.ts
* src/test/suite/sttmRealHostStructuredResult.test.ts

Phase V reported approximately 2,902 additions and 652 deletions. Do not assume this volume is intentional until the complete diff is reviewed.

REVIEW REQUIREMENTS

1. Verify the exact repository, branch, HEAD, staged state, final git status --short, and absence of concurrent mutation or Git lock.
2. Reconstruct the exact post-V status. Do not continue using the old four-line baseline if src/test/suite/index.ts adds another status entry.
3. Review the complete diff of all three Phase V files.

The focused test is untracked, so inspect its complete contents explicitly. Do not rely on ordinary git diff or git diff --check to cover an untracked file.

4. Explain the large line count:

* distinguish semantic changes from whitespace or line-ending conversion;
* identify any full-file rewrite;
* report semantic additions/deletions separately;
* reject unrelated refactoring or formatting churn.

5. Confirm scope containment:

* no Phase V change under src/core/**;
* no Phase V change to src/extension.ts;
* no Phase V change to .github/templates/request.md;
* no change to package.json, production dependencies, resources, QA, compiled files, or documentation;
* extensionDependencies remains exactly ["github.copilot-chat"].

6. Review the focused test and verify:

* Structured source expectation is source_db.customers.cust_name;
* Markdown source expectation is customers.cust_name;
* Structured and Markdown target expectation is grounded as target_db.customer_name;
* cross-channel parity covers mapping ID, order, and count;
* source, target, IDs, counts, and projections are captured before assertions;
* all mismatches are collected before the test fails;
* evidence is persisted before any assertion can abort execution.

7. Review parser cardinality instrumentation:

* the wrapped CommonJS export is the exact mutable export consumed by the ETL activation path;
* no production module captures or destructures the original parser before the wrapper is installed;
* ETL activation cannot race ahead of wrapper installation;
* original this, arguments, result, rejection, and error behavior are preserved;
* every invocation path/outcome is recorded;
* exactly one call is asserted;
* restoration always occurs in finally, including setup, activation, parser, assertion, and evidence-write failure;
* the hook cannot leak into another suite or ordinary test run.

If this seam is not reliable, report BLOCKED_PARSER_OBSERVATION_SEAM. Do not fix it.

8. Review src/test/suite/index.ts and prove that:

* the focused suite is loaded only under the explicit isolated qualification control;
* ordinary suites do not import or execute it;
* the loader does not import all suites and merely filter their reported results;
* authored/evaluated suite and test counts cannot be falsified by hidden imports or side effects.

9. Review src/test/runTest.ts and the evidence design:

* exactly one canonical evidence root is shared by controller, runner, and Host;
* evidence writes are restricted to etl-phase1b3n-v-evidence-<32 hex> under a test-owned temporary location;
* raw argv order is recorded as [etlRepositoryPath, bundledCopilotExtensionPath];
* activation/log order is stored separately and is not compared with argv order;
* complete TextPart and DataPart metadata, UTF-8 lengths, SHA-256, lossless DataPart base64, decoded JSON, projections, and all comparison results are retained;
* runner, runTests, Host, suite, test, invokeTool, registration, and parser counts are distinguishable;
* the parent independently records runner exit and verifies no runner or Host process remains;
* evidence is available for BLOCKED, FAIL, and PASS paths;
* a failed evidence write cannot be reported as product FAIL.

10. Review the reported 45 comparisons:

* enumerate their categories and counts;
* confirm they are independent and contract-relevant;
* identify duplicate, tautological, or implementation-only comparisons;
* confirm a first mismatch cannot suppress later observations.

11. Reconstruct an authoritative protected-path manifest proposal.

The previous eight-entry manifest is not automatically sufficient because Phase V introduced src/test/suite/index.ts and its future compiled artifact.

List every source, harness, contract, configuration, and compiled path that must be pinned for the compile and one-shot qualification gates. For each currently existing file, report its exact SHA-256.

Mark compiled files expected to change during the future compile as STALE_UNTIL_COMPILE; do not treat their current hashes as qualification hashes.

Do not write the manifest to disk during this review.

12. Confirm retained Phase 1B.3N-T evidence was not modified.

CLASSIFICATION

PASS_READY_FOR_COMPILE_GATE requires:

* complete diff review;
* no product or unauthorized change;
* no accidental rewrite or line-ending churn;
* reliable parser observation;
* exclusive focused-suite loading;
* complete evidence lifecycle;
* exact post-V Git baseline;
* complete protected-manifest proposal.

If any condition is not established, return BLOCKED_<EXACT_REASON>.

FINAL REPORT

Report:

1. exact repository, branch, HEAD and post-V Git status;
2. exact changed paths;
3. semantic diff summary per file;
4. explanation of the large line count;
5. unauthorized or unrelated changes, if any;
6. oracle and target correctness;
7. parser-hook verdict;
8. focused-loader verdict;
9. evidence-lifecycle verdict;
10. 45-comparison audit;
11. protected manifest table with path and SHA-256;
12. remaining blockers;
13. whether Phase V changes should be kept or revised;
14. exact proposed scope for the later compile-only gate.

End with:

PHASE_1B_3N_W_REVIEW_RESULT: PASS_READY_FOR_COMPILE_GATE|BLOCKED_<EXACT_REASON>
DIFF_ACCEPTABLE: YES|NO
EXACT_POST_V_STATUS_CAPTURED: YES|NO
PROTECTED_MANIFEST_COMPLETE: YES|NO
COMPILE_OR_TEST_EXECUTED: NO
RUNNER_OR_HOST_EXECUTED: NO
FUTURE_RUN_AUTHORIZATION_REQUIRED: YES
