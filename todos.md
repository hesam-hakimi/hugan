Repair B — Validator consumption parity

Execute this task in the normal writable VS Code source-repository workspace:

Repository:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required branch:
fix/workspace-write-completion-0.3.148

Required starting HEAD — committed Repair A:
46f6930e8474f6ac07d157cc85d21687a08869f3

Required HEAD subject:
fix: expose canonical runtime artifact contract

Speak to the user in Persian, but keep source code, code comments, test names, commit messages, commands, technical reports, and final markers in English.

This is Repair B only: validator consumption parity.

Repair A is complete and committed. Do not repeat, amend, redesign, squash, or revert Repair A.

Do not run this task in:

* the Extension Development Host;
* an F5 QA workspace;
* a consumer ETL workspace;
* an ETL Orchestrator chat;
* a read-only agent session.

The session must provide repository-scoped Read, Write/Edit, and Terminal capabilities. If Write/Edit is unavailable, stop immediately with:

REPAIR_B_WRITE_EDIT_UNAVAILABLE

Do not use a general-purpose or read-only workflow as a substitute.

==================================================
0. POWERSHELL COMMAND PREFIX

This shell may inherit PATHEXT=.CPL.

Every terminal invocation that uses git, node, npm, npx, or cmd must set PATHEXT in that same invocation:

$env:PATHEXT = ‘.COM;.EXE;.BAT;.CMD’;

Do not persist this workaround with setx, registry edits, profile edits, VS Code settings, or repository files.

==================================================

1. STRICT PREFLIGHT
    ==================================================

Before editing anything, verify:

1. Repository root is exactly:
    C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
2. Current branch is exactly:
    fix/workspace-write-completion-0.3.148
3. HEAD is exactly:
    46f6930e8474f6ac07d157cc85d21687a08869f3
4. HEAD subject is exactly:
    fix: expose canonical runtime artifact contract
5. HEAD has exactly one parent:
    a7ec7284906897321b2af5f7bf99de99211f7b70
6. git status --short --untracked-files=all is empty.
7. Index contains no staged paths.
8. No unexpected merge topology exists.
9. Repair A contains exactly nine changed paths relative to its parent.
10. The two Phase H report files remain unchanged from the Repair A parent:

* docs/eval/phase_h_latest_report.json
* docs/eval/phase_h_latest_report.md

If any check differs, do not infer, repair, checkout, reset, clean, stash, fetch, merge, rebase, amend, or continue. Stop and report the exact mismatch with:

REPAIR_B_PREFLIGHT_BLOCKED

Do not use destructive Git commands.

==================================================
2. REPAIR B OBJECTIVE

Align artifact validation with the canonical executable contract established by Repair A.

Repair the two validator-consumption defects:

A. DataSourcingConfigValidator must consume the shared canonical HOCON module grammar instead of relying on colon-only block extraction.

B. The public artifact-validation adapter must populate the real module sequence and provide the correct output-strategy decision for recognized canonical writers, instead of validating an empty Blueprint and producing a false strategy warning.

This task does not redesign artifact rendering, writing, approval, preview, manifest handling, collision handling, drift detection, or runtime QA.

==================================================
3. AUTHORIZED PRODUCTION SCOPE

Production edits are authorized only in:

1. src/core/validation/DataSourcingConfigValidator.ts
2. src/tools/EtlActionToolService.ts

For EtlActionToolService.ts, only validation-related hunks inside or directly supporting validateRenderedArtifacts are authorized.

A small validation-only helper or import immediately supporting that function is permitted.

No other behavior in EtlActionToolService.ts may change.

Before editing EtlActionToolService.ts:

* record the current blob OID;
* record the exact current line range of validateRenderedArtifacts;
* record the names of adjacent write-related methods;
* preserve the pre-edit file for post-edit hunk comparison.

After editing, prove that every changed hunk is either:

* inside validateRenderedArtifacts; or
* a minimal validation-only helper/import used exclusively by that path.

Any hunk touching or changing the behavior of these areas is an immediate blocker:

* writeToWorkspace
* performWrite
* collectManifestFiles
* buildApprovalManifest
* evaluateToolPlanScopedConsent
* preview
* probing
* approval
* authorization
* consent
* manifest generation
* collision handling
* drift handling
* checksum handling
* write-result construction
* trusted write state
* W1 ownership or atomic-apply behavior

If a required fix cannot be made without touching one of those areas, stop with:

REPAIR_B_W1_BOUNDARY_BLOCKED

==================================================
4. AUTHORIZED TEST SCOPE

Prefer extending existing directly related tests.

Authorized test paths are limited to existing or newly created focused tests whose sole purpose is one of these components:

* DataSourcingConfigValidator
* EtlActionToolService.validateRenderedArtifacts
* the registered public etl_validate_artifacts boundary

Before creating a new test file, prove that the behavior cannot be clearly expressed in an existing directly related suite.

Do not modify:

* EvalGating or EvalGovernance tests;
* Phase H reports;
* W1 collision/approval tests;
* workspace classification tests;
* unrelated shared test utilities;
* test expectations merely to hide a genuine regression.

==================================================
5. CHARACTERIZATION BEFORE PRODUCTION EDITS

Do not rerun or reinvestigate the full known baseline before editing.

First run focused characterization tests that prove the current behavior for:

1. Colon-form HOCON stage:
    stage: { … }
2. Equals-form HOCON stage:
    stage = { … }
3. Omitted-separator HOCON stage:
    stage { … }
4. Canonical data-sourcing configuration containing:
    * a modules root;
    * a stage whose options.module is data_sourcing_process;
    * module-local sourceList;
    * named source blocks referenced by sourceList;
    * options.method.
5. Canonical dataframe_writer bytes passed through the real public validation path.
6. A valid canonical job config at a .conf path.
7. The same canonical bytes at a .yaml path.
8. Recognized writer output currently receiving or not receiving:
    OUTPUT_STRATEGY_REVIEW_REQUIRED

Record the focused red/green evidence. A failing characterization test must demonstrate the intended defect, not an unrelated setup problem.

Do not run F5 QA or create a physical fixture.

==================================================
6. PARSER CONSUMPTION REPAIR

In DataSourcingConfigValidator:

* stop maintaining an independent colon-only interpretation of module blocks;
* reuse the repository’s shared canonical module-sequence grammar from:
    src/core/utils/ModuleSequenceExtractor.ts
    wherever safely possible;
* ensure all contract-supported separators are recognized equivalently:
    * stage: { ... }
    * stage = { ... }
    * stage { ... }
* identify the actual stage whose canonical dispatch field resolves to:
    options.module = data_sourcing_process
* validate data-sourcing keys from that stage’s complete content;
* read sourceList as a module-local array and a sibling of options;
* verify that every sourceList entry names a source block inside the same stage;
* preserve all existing validation rules for paths, zones, read formats, interpolation, required source attributes, and issue codes;
* preserve fail-closed behavior;
* preserve the existing “no data_sourcing module” valid early return unless the trusted contract explicitly requires otherwise;
* do not weaken validation to make malformed content pass;
* do not implement another ad-hoc parser if the shared extractor can provide the required structure.

The following outcomes must disappear for valid canonical bytes:

* MISSING_MODULE_OPTIONS
* MISSING_SOURCE_LIST
* MISSING_SOURCE_BLOCK

They must still occur for genuinely invalid configurations.

==================================================
7. PUBLIC VALIDATION ADAPTER REPAIR

In the validation-only path of EtlActionToolService:

* parse the real module sequence from artifacts.jobConfig;
* populate blueprint.modules from the recognized canonical modules;
* do not pass an empty module list when canonical modules are present;
* derive outputDecision only for recognized supported output modules;
* use existing output-strategy discriminators and mappings where available;
* do not duplicate contract parsing rules.

Required recognized mapping:

* dataframe_writer → generic_dataframe_write
* load_enrich_process → curated_load_enrich

Preserve the existing supported behavior and discriminators for:

* database_out
* tibco_out

Unknown, contradictory, malformed, or unsupported output modules must remain fail-closed or review-required according to the existing validator contract.

Do not fabricate an output decision when the module sequence does not justify one.

A valid canonical dataframe-writer configuration must not receive the false warning:

OUTPUT_STRATEGY_REVIEW_REQUIRED

Do not weaken OutputStrategyConfigValidator itself. Repair the adapter input supplied to it.

==================================================
8. EXTENSION-BOUNDARY REQUIREMENTS

Repair A established job-config extensions:

* .conf
* .json

Do not add .yaml or .yml as permitted job-config extensions.

Required behavior:

1. Valid canonical bytes at a .conf path pass validation.
2. Valid canonical bytes at a .json path pass validation when the content is otherwise supported.
3. The same valid canonical job bytes at a .yaml path fail only at the job-config extension boundary.
4. The .yaml result must not cascade into unrelated errors such as:
    * MISSING_MODULE_OPTIONS
    * MISSING_SOURCE_LIST
    * MISSING_SOURCE_BLOCK
    * OUTPUT_STRATEGY_REVIEW_REQUIRED

Environment-config YAML behavior is out of scope and must remain unchanged.

==================================================
9. REQUIRED ACCEPTANCE TESTS

The focused tests must prove at least:

1. DataSourcingConfigValidator accepts equivalent valid sourcing stages using all three separators:
    * colon;
    * equals;
    * omitted separator.
2. Canonical sourceList and its named source blocks are resolved from the correct sourcing stage.
3. Valid canonical sourcing bytes produce none of:
    * MISSING_MODULE_OPTIONS
    * MISSING_SOURCE_LIST
    * MISSING_SOURCE_BLOCK
4. Truly missing or empty sourceList still produces the correct existing issue.
5. A referenced but absent named source block still produces the correct existing issue.
6. The real public etl_validate_artifacts handler accepts repository-owned canonical dataframe-writer bytes at a .conf path.
7. The same canonical bytes at a .yaml path produce exactly the extension mismatch and no parser or strategy cascade.
8. A recognized canonical dataframe writer produces no false:
    OUTPUT_STRATEGY_REVIEW_REQUIRED
9. Unknown or unsupported output strategy remains fail-closed/review-required.
10. Existing database and TIBCO strategy behavior remains unchanged.

Tests must exercise both applicable layers:

* direct service/validator behavior;
* the registered public tool boundary through the real handler, including its structured application/json result.

Do not prove only a private helper while leaving the public payload incorrect.

==================================================
10. EXPECTED FAILURE MANIFEST

This manifest is authoritative for this task and exists to avoid repeated investigation.

The full unit suite may be run once after focused tests pass.

An expected failure is acceptable only when its exact test identity and essential signature match this manifest.

Do not accept a failure merely because the total failure count matches.

⸻

A. KNOWN_BASELINE_FAILURE

1. Test identity:

Copilot workflow customization > maintainer delivery prompt references real repo-local agents

Essential signature:

ENOENT opening:
.github/prompts/deploy-v3-agent-tool-context-gap.prompt.md

Action:

Record as KNOWN_BASELINE_FAILURE and continue.
Do not investigate or rerun it individually.

2. Test identity:

Copilot workflow customization > repo customization assets use valid frontmatter and agent file naming

Essential signature:

business-context.instructions.md frontmatter declares applyTo but no name

Action:

Record as KNOWN_BASELINE_FAILURE and continue.
Do not investigate or rerun it individually.

3. Test identity:

Copilot workflow customization > source tree uses standard AGENTS.md guidance instead of module AGENT.md files

Essential signature:

11 tracked src/*/AGENT.md files versus expected empty inventory

Action:

Record as KNOWN_BASELINE_FAILURE and continue.
Do not investigate or rerun it individually.

⸻

B. KNOWN_EVAL_FRESHNESS_FAILURE

4. Test identity:

EvalGating > passes against the committed Phase H baseline report

5. Test identity:

EvalGating > allows deterministic v3 baseline reports without prompt telemetry

Required essential signature for both:

Tracked prompt or behavior inputs changed since the last baseline report

The changed-path list may contain only a nonempty subset of these authorized tracked inputs:

* src/core/framework/TrustedJobConfigEnvelopeResolver.ts
* src/core/validation/DataSourcingConfigValidator.ts
* src/tools/EtlActionToolService.ts

The Repair A resolver path is already an expected tracked difference.

Repair B may add only its authorized production paths to the same freshness signature.

If the two exact EvalGating tests fail with that exact failure class and their changed paths are confined to the list above:

* classify them as KNOWN_EVAL_FRESHNESS_FAILURE;
* record the actual changed-path list verbatim;
* do not investigate them again;
* do not rerun them individually;
* do not modify or weaken EvalGating;
* do not run npm run eval:golden;
* continue toward the Repair B commit.

If the failure names, failure class, or changed paths differ, stop.

If an expected failure disappears, continue and report that the manifest entry may be removed later.

Any additional failure, changed signature, unexpected changed path, timeout, crash, or infrastructure error blocks the commit.

==================================================
11. VALIDATION ORDER

Run validation in this order:

1. git diff --check
2. Compile.
3. Focused DataSourcingConfigValidator tests.
4. Focused EtlActionToolService validation tests.
5. Registered public etl_validate_artifacts boundary tests.
6. Relevant existing strategy-validation tests.
7. Relevant W1 protection/collision/approval tests, without changing their bytes.
8. Full unit suite exactly once after all focused tests pass.

For the full suite:

* reconcile failures by exact identity and signature against Section 10;
* do not reinvestigate exact manifest matches;
* do not rerun exact manifest matches individually;
* stop on any unexpected failure.

Do not run:

* npm run eval:golden
* F5 QA
* VSIX build/package/install
* external service calls
* publication or release commands

==================================================
12. PROTECTED FILES AND NON-GOALS

Do not modify:

* Repair A contract/discovery files;
* resources/framework/contracts/job-config-envelope.v1.json
* src/core/framework/TrustedJobConfigEnvelopeResolver.ts
* src/tools/EtlReadOnlyToolService.ts
* resources/copilot/context/etl-module-reference.md
* docs/reference/ETL_MODULE_REFERENCE.md
* package.json
* Repair A focused test files unless one is also an existing directly related Repair B test and an edit is strictly necessary;
* src/core/utils/ModuleSequenceExtractor.ts
* src/test/testPatterns.ts
* src/tools/TrustedWriteApprovalStore.ts
* src/tools/index.ts
* .vscodeignore
* docs/eval/phase_h_latest_report.json
* docs/eval/phase_h_latest_report.md
* any STTM workbook;
* any job config;
* any environment config;
* any QA fixture;
* any generated build artifact;
* any version, dependency, devDependency, engine, or lockfile;
* release notes;
* W1 implementation or W1 tests.

Do not:

* run npm run eval:golden;
* create a deterministic physical fixture;
* run end-to-end F5 QA;
* redesign renderer ownership;
* make renderers synthesize caller bytes;
* alter etl_search_examples;
* change write, preview, approval, consent, manifest, collision, checksum, drift, or atomic-apply behavior;
* fetch, pull, merge, rebase, reset, checkout, stash, clean, amend, cherry-pick, squash, push, publish, or create a branch.

The missing deterministic physical source/target/environment fixture remains a separate later task.

Repair B must not claim that end-to-end F5 QA is now confirmation-ready.

==================================================
13. PRE-COMMIT GATE

Before committing, report:

1. Current branch.
2. HEAD before commit.
3. Exact changed-path inventory.
4. Exact diff summary.
5. git diff --check result.
6. Compile result.
7. Focused test commands and totals.
8. Full-suite totals.
9. Expected Failure Manifest reconciliation with:
    * exact test identity;
    * exact observed signature;
    * classification;
    * action taken.
10. Proof that all EtlActionToolService.ts hunks are validation-only.
11. Proof that W1-owned paths and behavior are unchanged.
12. Proof that Repair A production files are unchanged.
13. Proof that Eval report files are byte-identical to Repair A HEAD.
14. Proof that package version, dependencies, engines, and lockfile state are unchanged.
15. Proof that no fixture, VSIX, generated artifact, or unexpected file exists.

Commit only if:

* all focused tests pass;
* compile passes;
* no unexpected full-suite failure exists;
* the only full-suite failures are exact manifest matches;
* every changed path is authorized;
* every EtlActionToolService.ts hunk is validation-only;
* all protected boundaries remain intact.

Stage each authorized path explicitly.

Do not use:

git add -A

Do not use:

git add .

If the gate passes, create exactly one commit with subject:

fix: align artifact validation with canonical contract

Do not amend Repair A.

Do not push.

==================================================
14. POST-COMMIT VERIFICATION

After committing, verify:

1. The new commit has exactly one parent.
2. Its sole parent is:
    46f6930e8474f6ac07d157cc85d21687a08869f3
3. Its subject is exactly:
    fix: align artifact validation with canonical contract
4. It contains only authorized Repair B paths.
5. Worktree, index, and untracked inventory are empty.
6. Repair A remains the immediate parent.
7. Phase H reports remain unchanged.
8. No W1, fixture, version, dependency, lockfile, generated artifact, or unrelated file was changed.

==================================================
15. FINAL RESPONSE

Return a concise evidence report containing:

* Repair B commit SHA;
* sole parent SHA;
* commit subject;
* exact changed paths;
* focused test results;
* full-suite result;
* Expected Failure Manifest reconciliation;
* EtlActionToolService validation-only hunk proof;
* protected-file verification;
* final worktree state;
* explicit statement that npm run eval:golden was not run;
* explicit statement that no push occurred;
* explicit statement that deterministic F5 fixture work remains separate.

End with exactly one marker:

REPAIR_B_VALIDATOR_CONSUMPTION_COMMITTED

or, if blocked:

REPAIR_B_VALIDATOR_CONSUMPTION_BLOCKED
