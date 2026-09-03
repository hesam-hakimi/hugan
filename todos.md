TASK: PHASE_1B_3N_V_TEST_ORACLE_AND_EVIDENCE_HARDENING_IMPLEMENTATION_ONLY

ROLE

Use the normal local GitHub Copilot Agent, not the ETL Orchestrator.

This is a bounded test/harness implementation task. It does not authorize compilation, test execution, runner invocation, Extension Host launch, retry, packaging, installation, version change, commit, merge, publication, or product-source modification.

AUTHORITATIVE BASELINE

Repository:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Branch:
fix/workspace-write-completion-0.3.148

HEAD:
45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected Git status:
M .github/templates/request.md
M src/extension.ts
M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Retained Phase 1B.3N-T evidence:
C:\Users\tag5916\AppData\Local\Temp\etl-phase1b3n-t-evidence-bb866c7be991469abd3bf924b0373fc0

Do not modify or delete the retained evidence.

ACCEPTED PHASE 1B.3N-U FINDINGS

1. Canonical structured source is db.entity.field when all components exist.
2. Markdown intentionally renders the shorter entity.field source label.
3. The fixture authors:
    * sourceDb = source_db
    * sourceEntity = customers
    * sourceField = cust_name
4. The public adapter serializes response.data without rewriting mapping fields.
5. Cross-channel parity applies to mapping ID, order, count, exclusions, and diagnostics—not byte-identical source display strings.
6. The observed structured value source_db.customers.cust_name conforms to the current product contract.
7. The focused test incorrectly reused the Markdown expectation customers.cust_name for the structured channel.
8. No product projection change is authorized or required.

PREFLIGHT — READ ONLY

Before editing:

1. Verify repository, branch, HEAD and exact four-line Git status.
2. Confirm no concurrent Agent is modifying the worktree.
3. Read the complete focused test and existing test-owned evidence helpers.
4. Identify a genuine test-only seam for observing parser invocation cardinality.
5. Confirm evidence can be captured without modifying:
    * src/extension.ts
    * src/core/**
    * Markdown renderer
    * public adapter
    * package.json
    * compiled output
    * QA files
6. Reconcile, from existing runner/evidence only:
    * argvDevelopmentPaths must be [etlRepositoryPath, bundledCopilotExtensionPath];
    * activation/log order is a separate non-contractual observation.
7. If parser cardinality cannot be observed without production changes, stop before editing and report:
    BLOCKED_TEST_ONLY_PARSER_INSTRUMENTATION

AUTHORIZED CHANGES

Prefer changing only:

src/test/suite/sttmRealHostStructuredResult.test.ts

If strictly necessary, a minimal existing helper or runner under src/test/** may also be changed solely for test-owned evidence capture. Explain why before changing it.

Do not modify any production path.

IMPLEMENTATION REQUIREMENTS

1. Replace the shared source expectation with separate values:

* structured source:
    source_db.customers.cust_name
* Markdown source display:
    customers.cust_name
* cross-channel parity:
    mapping ID, order, and count

2. Preserve and independently ground the existing target expectation from the fixture and structured projection. Do not invent or weaken it.
3. Prevent first-assertion masking:

* capture all observed values before asserting;
* evaluate source and target comparisons independently;
* collect deterministic mismatches;
* fail once at the end with the complete mismatch set.

4. Prepare machine-readable evidence for the future authorized run containing:

* exact argv development paths in order;
* activation order as a separate field;
* runner, runTests, Host, suite, test and invokeTool counts;
* part order and constructor/type;
* MIME for every applicable part;
* character length and UTF-8 byte length;
* SHA-256 for TextPart and DataPart;
* exact DataPart bytes or an equivalent lossless retained representation;
* decoded JSON;
* observed structured source and target;
* observed Markdown source and target;
* every deterministic comparison result;
* exact parser invocation cardinality;
* exact pre/post values for all eight protected file hashes;
* QA inventory, workbook size/hash and final process integrity.

Evidence must be written only to the future unique test-owned isolation/evidence directory, never to the repository or QA workspace.

5. Parser cardinality must come from a real test-only observation seam. Do not substitute:

* invokeTool count;
* registration count;
* static call-graph inference;
* expected behavior.

6. Preserve:

* preview-only behavior;
* zero consumer writes;
* production extensionDependencies = ["github.copilot-chat"];
* production and normal-development activation behavior;
* all existing QA and repository safety boundaries.

PROHIBITED

Do not:

* change structured output to remove sourceDb;
* change Markdown rendering;
* change the public adapter;
* change product code;
* compile;
* run tests;
* invoke the compiled runner;
* launch an Extension Host;
* retry Phase 1B.3N-T;
* create or install a VSIX;
* bump the version;
* stage, commit, merge, push, publish, or clean the worktree.

FINAL REPORT

Return:

1. Preflight identity result.
2. Exact changed paths.
3. Exact source-oracle change.
4. How target evaluation avoids short-circuiting.
5. Exact parser-cardinality observation seam.
6. Evidence fields prepared for the future run.
7. Resolution of argv order versus activation order.
8. Confirmation of zero product-source changes.
9. New hashes for every changed test/harness file.
10. Remaining evidence gaps.
11. Proposed scope of the future one-shot qualification—but do not execute it.

End with exactly:

PHASE_1B_3N_V_IMPLEMENTATION_RESULT: PASS_READY_FOR_REVIEW
or
PHASE_1B_3N_V_IMPLEMENTATION_RESULT: BLOCKED_<EXACT_REASON>

COMPILE_OR_TEST_EXECUTED: NO
RUNNER_OR_HOST_EXECUTED: NO
FUTURE_RUN_AUTHORIZATION_REQUIRED: YES
