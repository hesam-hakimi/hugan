Implement the audited runtime artifact-contract parity fixes in the ETL extension source repository. This is a narrow source repair. Do not launch F5 or modify the QA workspace in this turn.

Repository and audited starting state

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:

fix/workspace-write-completion-0.3.148

Expected audited HEAD:

* short SHA begins with a7ec728;
* subject is test: refresh Phase H evaluation baseline;
* its parent is the W1 commit fix: enforce trusted workspace write collision checks;
* the parent of W1 is Repair 13 commit 64706129e0d1054ea615e150b28dd623fb3c629e.

Audit classification:

MULTIPLE_DEFECTS

Preflight — hard gate

Before editing, report:

* repository root;
* branch;
* full HEAD SHA and subject;
* the last three commits with parents;
* git status --short;
* staged paths.

Requirements:

* branch and topology must match the audited state;
* index and working tree must be clean;
* nothing may already be staged.

Stop if any requirement differs. Do not reset, clean, stash, restore, amend, rebase, fetch, merge, or discard anything.

Capture before-state hashes for the protected W1 files listed below.

Defect 1 — parser parity

src/core/validation/DataSourcingConfigValidator.ts uses colon-only HOCON block parsing in or around:

* hasSourceBlock;
* extractSourceBlocks;
* extractDataSourcingModule.

This contradicts:

* resources/framework/contracts/job-config-envelope.v1.json;
* src/core/framework/TrustedJobConfigEnvelopeResolver.ts;
* src/core/utils/ModuleSequenceExtractor.ts.

The contract permits:

* stage: {
* stage = {
* stage {

Required behavior:

* reuse the shared module parser to locate the data_sourcing_process stage and its exact content;
* eliminate the colon-only assumption;
* recognize stage-local options.module, options.method, sourceList, and named source blocks for every permitted separator;
* preserve all existing validation codes, messages, path/interpolation rules, and fail-closed behavior;
* do not introduce another independent HOCON grammar.

Defect 2 — incomplete public discovery and F5 drift

Primary file:

src/tools/EtlReadOnlyToolService.ts

Relevant symbols include:

* getFrameworkRules;
* describeModule;
* MODULE_REFERENCE_SOURCES;
* module-reference parsing used to derive commonKeys.

Required behavior:

1. Reuse TrustedJobConfigEnvelopeResolver; do not duplicate the contract.
2. Add a compact structured executable-envelope description to:
    * etl_get_framework_rules;
    * etl_describe_module.
3. Expose:
    * root key modules;
    * stage-keyed entries;
    * options.module;
    * options.method;
    * default method process;
    * supported separators;
    * per-module required module and option keys;
    * sourceList requirements and its relationship to named source blocks;
    * permitted job-config extensions.
4. Rank the packaged canonical reference first:
    * resources/copilot/context/etl-module-reference.md
5. Correct the conflicting development reference:
    * docs/reference/ETL_MODULE_REFERENCE.md
6. Ensure equals-form and omitted-separator fields remain visible to reference parsing.
7. Preserve etl_search_examples local-workspace precedence and isolation behavior.
8. Do not change .vscodeignore; F5 and packaged VSIX discovery must converge without shipping docs/**.

Defect 3 — undiscoverable job-config extension rule

Job configurations must use:

* .conf
* .json

They must not use:

* .yaml
* .yml

Environment configuration behavior remains unchanged.

Required behavior:

* add permitted job-config extensions to:
    * resources/framework/contracts/job-config-envelope.v1.json;
* expose them through the public discovery repair;
* update only the jobConfigPath description in package.json if necessary;
* do not change the Validator to accept YAML job configurations;
* update the contract type/canonicalization in TrustedJobConfigEnvelopeResolver.ts only as required;
* recompute the trusted contract fingerprint using the repository’s deterministic supported mechanism;
* report old and new fingerprints.

Stop if a supported deterministic fingerprint-update mechanism cannot be established.

Defect 4 — empty Blueprint in public Validation

Primary file:

src/tools/EtlActionToolService.ts

Limit changes to validateRenderedArtifacts and directly necessary imports or validation-only helpers.

Required behavior:

* populate blueprint.modules from extractModuleSequence(artifacts.jobConfig);
* derive outputDecision from recognized modules:
    * load_enrich_process → curated_load_enrich;
    * dataframe_writer → generic_dataframe_write;
    * retain existing database-out and TIBCO-out discrimination;
* allow existing transformation and strategy validators to inspect the real module sequence;
* do not place search metadata such as strategy into executable Job content;
* do not globally suppress OUTPUT_STRATEGY_REVIEW_REQUIRED;
* recognized canonical writers must not receive the false warning;
* genuinely unknown strategies must retain manual-review/fail-closed behavior;
* keep OutputStrategyConfigValidator unchanged unless a focused test disproves the Audit. If so, stop before expanding Scope.

Contract behavior to preserve

The executable Job configuration must have:

* root object modules;
* modules keyed by stage name;
* stage-local fields plus options;
* options.module set to a supported module type;
* options.method = process;
* sourceList as a non-empty string array, sibling to options;
* every sourceList entry naming a sibling source block;
* inline SQL allowed for this transformation/writer path;
* no Include artifact added merely to silence a warning;
* generic_dataframe_write represented by a dataframe_writer stage.

W1 protection boundary

Do not modify:

* src/chat/DeployCoordinator.ts
* src/chat/WriteCoordinator.ts
* src/core/trusted/WriteAuthorization.ts
* src/test/helpers/mintTestWriteAuthorization.ts
* src/test/suite/onboardingWriteApproval.test.ts
* src/tools/TrustedWriteApprovalStore.ts
* src/writers/RepoWriter.ts
* src/core/artifacts/ArtifactDestinationInventory.ts
* src/core/artifacts/WorkspaceDestinationProbe.ts
* src/test/suite/workspaceWriteCollision.test.ts

Do not change:

* destination inventory;
* CREATE / OVERWRITE / UNCHANGED classification;
* collision or duplicate handling;
* trusted Preview and checksum;
* explicit approval;
* post-approval state validation;
* physical containment;
* per-file results;
* partial-apply reporting.

src/tools/EtlActionToolService.ts overlaps W1. Its diff must be limited to the read-only Validation adapter. Do not touch Preview, Approval, probing, classification, drift checking, writeToWorkspace, or write execution.

Do not implement:

* atomic multi-file apply or rollback;
* durable managed ownership;
* automatic Git rollback.

src/test/testPatterns.ts may receive only minimum additive test registration. Do not remove, reorder, or weaken existing entries.

Allowed implementation paths

Production changes must stay within:

* src/core/validation/DataSourcingConfigValidator.ts
* src/tools/EtlReadOnlyToolService.ts
* src/tools/EtlActionToolService.ts
* src/core/framework/TrustedJobConfigEnvelopeResolver.ts
* resources/framework/contracts/job-config-envelope.v1.json
* resources/copilot/context/etl-module-reference.md
* docs/reference/ETL_MODULE_REFERENCE.md
* package.json — only jobConfigPath description
* directly related unit-test files
* one narrowly named new contract-parity test file if required
* src/test/testPatterns.ts only if required to execute that suite

Do not modify sibling etl-framework-gen-utils.

Stop before changing any additional Production path.

Required automated tests

1. Parser parity

Extend the existing DataSourcingConfigValidator suite with the same canonical configuration parameterized over:

* stage: {
* stage = {
* stage {

For all three, assert recognition of:

* valid sourcing stage;
* options.module;
* options.method;
* non-empty sourceList;
* referenced source block.

Assert absence of:

* MISSING_MODULE_OPTIONS
* MISSING_SOURCE_LIST
* MISSING_SOURCE_BLOCK

Retain negative coverage for genuinely missing fields.

2. Public Discovery

Call the real handlers for:

* etl_get_framework_rules;
* etl_describe_module("data_sourcing_process").

Assert structured results expose:

* modules root;
* stage-keyed envelope;
* options.module;
* options.method;
* default method;
* supported separators;
* required sourceList;
* .conf and .json;
* a canonical executable example.

Prove F5 source selection no longer prefers the conflicting development-only reference.

3. Canonical bytes through the public Validator

Feed canonical Job content from:

resources/copilot/knowledge/examples/dataframe-writer-export.example.json

through the real EtlActionToolService.validateArtifacts path using:

job_conf/conf/QA/qa_job.conf

Assert:

* zero validation errors;
* sourcing and sourceList recognized;
* generic_dataframe_write recognized;
* no OUTPUT_STRATEGY_REVIEW_REQUIRED;
* no filesystem write.

4. Invalid extension boundary

Use identical valid bytes at:

job_conf/conf/QA/qa_job.yaml

Assert:

* exactly the extension mismatch;
* no sourcing/module/sourceList error;
* no false output-strategy warning;
* path is not accepted or rewritten.

Do not globally short-circuit the Validation pipeline.

5. W1 regression

Run established headless suites covering:

* workspace classification parity;
* workspace collision;
* onboarding approval;
* physical containment;
* workspace input containment;
* RepoWriter workspace selection;
* action-tool workspace-write lifecycle.

All must pass unchanged.

Test integrity

Do not add skipped, exclusive, pending, tautological, snapshot-only, or bypassing tests. Do not add Production exports solely for testing.

Command budget

After editing:

1. git diff --check
2. npm run compile
3. one focused contract/parser/discovery/validator test invocation
4. one focused W1 suite invocation
5. npm run test:unit exactly once

If compile or focused contract tests reveal an implementation error, allow only one correction cycle:

* one additional compile;
* one additional focused contract-test invocation.

Do not rerun the full suite.

Do not run:

* npm install
* packaging/VSIX
* F5
* npm run eval:golden
* external QA
* Databricks, DBFS, pipeline, publication, or network-dependent commands.

Full-unit interpretation

Permitted failures are only:

* two EvalGating freshness failures naming exactly the intended changed files;
* the three pre-existing copilotWorkflowCustomization failures:
    * missing delivery Prompt;
    * missing frontmatter name;
    * residual module-level AGENT.md files.

No workspace-write, parser, discovery, contract, renderer, Validator, or new test may fail.

Do not modify:

* docs/eval/phase_h_latest_report.json
* docs/eval/phase_h_latest_report.md

Eval refresh must be a separate follow-up and separate Commit.

Stop without committing for any unexpected failure.

Deterministic F5 fixture limitation

Do not hard-code synthetic ADLS values, credentials, schemas, or QA-only defaults into Production.

This Commit repairs Discovery and Validation parity only.

Report whether an existing repository-owned fixture or generator already provides:

* one complete executable active Mapping;
* authoritative synthetic source and target paths;
* deterministic Env configuration or generated-new-env inputs;
* required schema, column, and predicate values;
* no credentials or real consumer values.

If none exists, report:

DETERMINISTIC_F5_QA_FIXTURE_REQUIRED

Do not create the Fixture in this Commit.

Commit policy

Commit only if:

* Compile and focused tests pass;
* W1 focused suites pass;
* full-unit failures are limited to the permitted set;
* git diff --check passes;
* all changed paths remain in Scope;
* protected W1 files remain byte-identical;
* EtlActionToolService.ts changes Validation only;
* Evaluation reports, version, dependencies, scripts, Workflow, CI and unrelated files are unchanged.

Before committing, report:

* git status --short;
* git diff --stat;
* git diff --check;
* every Production hunk by symbol;
* protected W1 hashes;
* staged path list and staged diffstat.

Create exactly one Commit:

fix: align runtime artifact discovery and validation

Do not amend, push, create a PR/tag, change version, merge, or rebase.

After committing, verify:

* full HEAD and subject;
* parent is the previous a7ec728... Commit;
* exactly one new Commit exists;
* index and worktree are clean;
* nothing was pushed.

F5 handoff — do not execute

Do not reuse the existing Extension Development Host; it contains the old build and an initialized QA Workspace.

Report the later manual Gate:

1. close the stale Host;
2. create a new temporary Workspace outside the Source;
3. prepare the deterministic QA Fixture separately;
4. copy sttm/synthetic_workbook.xlsx;
5. launch a new Extension Development Host;
6. invoke @etl /workflow;
7. verify public Discovery exposes the canonical envelope and .conf/.json;
8. render and validate canonical Job bytes;
9. require zero errors and no false strategy warning;
10. reach trusted confirmation with CREATE-only destinations;
11. wait for explicit user approval;
12. verify per-file results;
13. rerun identical bytes and verify all destinations are UNCHANGED.

Final report

Return:

* Preflight;
* root-cause-to-change table;
* changed files and symbols;
* contract fingerprint before/after;
* test commands and exact results;
* full-unit failure names;
* protected W1 hash comparison;
* implementation Commit SHA and parent;
* final git status --short;
* confirmation that nothing was pushed;
* Eval status:
    * DEFERRED_TO_SEPARATE_COMMIT
* deterministic F5 Fixture status;
* manual F5 handoff.

End with exactly:

RUNTIME_ARTIFACT_CONTRACT_FIX_COMMITTED_NOT_PUSHED

or:

RUNTIME_ARTIFACT_CONTRACT_FIX_BLOCKED
