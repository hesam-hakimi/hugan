TASK: PHASE_1B_3N_U_SOURCE_CONTRACT_RECONCILIATION_READ_ONLY

ROLE

Act as a fresh independent evidence and contract reviewer. Communicate conclusions to the owner in Persian. Keep technical identifiers and report markers in English.

This is a read-only diagnosis and decision-support task. You are not authorized to implement, edit, compile, run tests, launch an Extension Host, retry Phase 1B.3N-T, package, install, commit, merge, or publish.

FROZEN INPUTS

Repository:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Branch:
fix/workspace-write-completion-0.3.148

HEAD:
45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Retained Phase 1B.3N-T evidence:
C:\Users\tag5916\AppData\Local\Temp\etl-phase1b3n-t-evidence-bb866c7be991469abd3bf924b0373fc0

Frozen observed result:

* Raw LanguageModelToolResult.content boundary reached.
* One runner, one runTests call, one Host launch, zero retries.
* Eight tests evaluated: seven passed and one failed.
* Mapping: FM_F01417B0_00002
* Expected source: customers.cust_name
* Observed source: source_db.customers.cust_name
* Runner exit code: 1
* Repository and QA integrity remained unchanged.

PURPOSE

Determine the authoritative public contract for the structured mapping source field and identify whether the observed mismatch represents:

1. a product projection defect;
2. a stale or over-qualified test expectation;
3. an intentional channel-specific representation with an incorrect parity assertion; or
4. an unresolved owner-level contract decision.

REQUIRED READ-ONLY WORK

1. Read completely every existing machine-readable file under the retained evidence root, including:

* phase-result.json
* mocha-result.evidence.json
* any raw structured-result, integrity, process, Host, or pre/post-state manifests already present

Do not create or modify evidence files.

2. Confirm the recorded values for:

* repository, branch, HEAD and four-line Git status;
* eight protected hashes and QA identity;
* runner/runTests/Host/retry counts;
* Host PID and VS Code version;
* ordered development paths;
* Copilot and ETL activation;
* tool registration;
* suite/test/invokeTool counts;
* raw part order, types, MIME values and byte lengths;
* UTF-8/JSON decoding;
* observed source and target fields;
* parser invocation cardinality, only if already recorded;
* final integrity.

3. Trace the source contract through the existing source, tests, fixtures, accepted documentation and relevant Git history. Include at minimum:

* the resolved STTM mapping projection;
* Markdown report rendering;
* the public LanguageModelToolResult adapter;
* sttmRealHostStructuredResult.test.ts;
* synthetic workbook fixture generation;
* existing consumer-visible contract tests;
* accepted packaged skill/documentation wording.

4. Answer these questions with direct evidence:

* Is the canonical structured source format db.entity.field or entity.field?
* Does parity require identical source strings or only identical mapping identity/order?
* Is source_db intentionally authoritative or display-only?
* Is the focused test expectation supported by an accepted contract?
* Can the unevaluated target assertion be checked from retained raw data without rerunning?
* Is parser cardinality already observable from retained evidence?

RULES

* Do not choose a contract merely to make the test pass.
* Do not treat an untracked test assertion as authoritative unless accepted source, documentation, fixtures, or history support it.
* Do not alter the frozen FAIL evidence.
* Do not execute the runner or launch a Host.
* Do not edit source, tests, compiled files, QA files, or documentation.
* If evidence conflicts, identify the exact owner decision required.
* Keep product remediation separate from test remediation.

FINAL REPORT

Provide:

1. authoritative contract findings;
2. exact evidence supporting each finding;
3. classification as PRODUCT_PROJECTION_DEFECT, STALE_TEST_ORACLE, CHANNEL_CONTRACT_MISMATCH, or BLOCKED_OWNER_DECISION;
4. the smallest proposed changed-path boundary for each viable resolution;
5. evidence gaps that can be answered without rerunning;
6. whether an owner contract decision is required;
7. whether implementation can be authorized next.

End with:

SOURCE_CONTRACT_RECONCILIATION: 
NEW_RUN_REQUIRED_NOW: NO
READY_FOR_OWNER_IMPLEMENTATION_AUTHORIZATION: YES|NO
