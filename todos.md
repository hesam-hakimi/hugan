Step 1 — Read-only deterministic F5 fixture readiness audit

Run this task in the normal VS Code source-repository workspace:

Repository:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required branch:
fix/workspace-write-completion-0.3.148

Required starting HEAD:
edeaaa74f8d4df715fedb7b2d9f50f2418018770

Required HEAD subject:
test: refresh Phase H evaluation baseline

Speak with the user in Persian, but keep technical evidence, paths, identifiers, commands, and final markers in English.

This is a strictly read-only audit.

Do not create the fixture yet. Do not edit, stage, commit, push, render, validate, preview, approve, write, package, install, or run F5.

==================================================

1. POWERSHELL PREFIX
    ==================================================

Every terminal invocation using git, node, npm, npx, or cmd must begin with:

$env:PATHEXT = ‘.COM;.EXE;.BAT;.CMD’;

Do not persist this workaround.

==================================================
2. PREFLIGHT

Verify:

* repository root is exact;
* branch is exact;
* HEAD is exactly:
    edeaaa74f8d4df715fedb7b2d9f50f2418018770
* HEAD subject is exact;
* HEAD has exactly one parent:
    6107aa0b0e0d5bb26a998db62ee26712a728139a
* worktree, index, and untracked inventory are empty;
* topology is linear:
    Repair A → Repair B → Phase H Eval refresh.

If anything differs, stop with:

DETERMINISTIC_F5_FIXTURE_AUDIT_BLOCKED

==================================================
3. AUDIT OBJECTIVE

Determine the smallest authoritative deterministic fixture required for the intended ETL Orchestrator F5 QA flow to proceed from STTM interpretation through:

* canonical artifact construction;
* render;
* validation;
* write preview;
* trusted confirmation readiness.

Do not perform those runtime actions in this step.

The previous runtime QA selected:

* mapping: FM_F01417B0_00002
* strategy: generic_dataframe_write
* chain:
    data_sourcing_process → data_transformation → dataframe_writer
* writer mode: overwrite
* environment choice: new synthetic environment config

Previous evidence reported missing:

* authoritative physical source path;
* authoritative target path;
* deterministic environment roots;
* source/schema details required by JC_001;
* executable column and predicate details required by FT_001;
* complete canonical artifact bytes.

Treat those statements as audit leads, not permission to invent values.

==================================================
4. AUTHORITATIVE SOURCES TO INSPECT

Inspect read-only:

1. The trusted job-config envelope contract.
2. TrustedJobConfigEnvelopeResolver.
3. The repaired public discovery projection.
4. The packaged canonical dataframe-writer example.
5. The packaged and source module-reference documentation.
6. Environment-config generation and validation contracts.
7. Data-sourcing, transformation, and dataframe-writer validators.
8. First-render invariant and path/interpolation guards.
9. Existing repository-owned synthetic examples, fixtures, or QA configurations.
10. Existing tests demonstrating valid source, target, environment-root, schema, column, predicate, inline-SQL, and writer representations.
11. The STTM native parser/tool contract and any available structured evidence for:
    FM_F01417B0_00002, JC_001, and FT_001.

If an STTM workbook is not inside the current repository, do not search unrelated external directories and do not request broad filesystem access. Record that the workbook must be inspected later in the isolated QA workspace.

Do not parse an Excel STTM with an improvised parser when the registered native STTM interpreter is required.

==================================================
5. QUESTIONS THE AUDIT MUST ANSWER

Report with file-and-symbol evidence:

1. Does a complete repository-owned deterministic fixture already exist?
2. If yes:
    * exact path;
    * exact purpose;
    * whether it is safe for isolated F5 QA;
    * whether it supplies all required physical and executable values.
3. If no, identify the exact missing fields without guessing their values.
4. What is the canonical environment-config extension and structure?
5. Which environment-root keys are required for:
    * physical source;
    * transformation/intermediate output, if applicable;
    * dataframe-writer destination?
6. What path form is accepted by the first-render guard?
7. Which values must be interpolated instead of hard-coded?
8. What exact sourcing-stage structure is required, including:
    * options.module;
    * options.method;
    * sourceList;
    * named source blocks;
    * read format;
    * path;
    * zone;
    * schema or dataset details.
9. What exact executable transformation representation is required for FT_001?
10. Does FT_001 require:
    * inline SQL;
    * column expressions;
    * predicates;
    * aliases;
    * include artifacts;
    * or another contract field?
11. What exact dataframe-writer options are required for:
    * generic_dataframe_write;
    * overwrite mode;
    * format;
    * destination path;
    * inline SQL or input view.
12. Which values are authoritative from STTM evidence, and which must come from a QA-owned fixture decision?
13. Where should the fixture live:
    * source repository;
    * isolated QA workspace;
    * or both?
14. What exact files would need to be created in the next step?
15. Which files must remain protected and untouched?

==================================================
6. SAFETY REQUIREMENTS

The proposed fixture must be:

* synthetic;
* deterministic;
* isolated to a QA workspace;
* free of real customer or production data;
* free of external service dependency;
* free of Databricks, DBFS, ABFSS, network, or credential requirements unless the existing F5 contract explicitly requires them;
* incapable of writing outside its isolated QA roots;
* reusable across repeated F5 runs;
* explicit enough that the Orchestrator does not need to guess any executable value.

Do not propose relaxing validation or invariant guards merely to make the fixture pass.

Do not modify Repair A, Repair B, Eval reports, W1 code, version, dependencies, contracts, examples, or documentation.

==================================================
7. NO TEST OR GENERATION WORK

Do not run:

* npm run eval:golden;
* full unit suite;
* F5;
* VSIX build/package/install;
* ETL Orchestrator;
* renderer;
* validator;
* preview;
* write;
* external services.

Small read-only inspection commands are permitted.

==================================================
8. REQUIRED OUTPUT

Return a concise readiness report with:

1. Preflight result.
2. Existing-fixture finding.
3. Authoritative contract findings.
4. Exact missing-field inventory.
5. STTM-derived versus QA-owned decision table.
6. Proposed minimal fixture file inventory.
7. Recommended fixture location.
8. Exact protected boundaries.
9. Any unresolved evidence that must be obtained from the isolated QA workspace.
10. A clear verdict:

* READY_TO_AUTHOR_FIXTURE
* EXISTING_FIXTURE_REUSABLE
* FIXTURE_EVIDENCE_INCOMPLETE

11. Confirmation that nothing was modified and git status remains empty.

Do not create a fixture-authoring prompt yet; return the evidence first.

End with exactly one marker:

DETERMINISTIC_F5_FIXTURE_AUDIT_COMPLETE

or:

DETERMINISTIC_F5_FIXTURE_AUDIT_BLOCKED

answer in english only
