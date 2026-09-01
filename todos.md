Repair B — Validator consumption parity

Run this task only in the normal VS Code source-repository window/Claude Code session opened at:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Do not run it in:

* the Extension Development Host;
* the isolated F5 QA workspace;
* a consumer workspace;
* the ETL Orchestrator chat.

This is a bounded source implementation task.

Required Repair A identity

Expected Repair A full commit SHA:

<REPAIR_A_FULL_SHA>

Before executing this prompt, replace that placeholder with the exact full SHA reported by Repair A.

Do not infer, approximate, or search for a “similar” commit.

Required Repair A marker:

REPAIR_A_CONTRACT_DISCOVERY_COMMITTED

Expected branch:

fix/workspace-write-completion-0.3.148

Expected Repair A commit subject:

fix: expose canonical runtime artifact contract

This task addresses independently source-audit-proven defects.

The runtime Orchestrator QA did not reach validation. Do not claim these defects were executed by that QA run.

Reproduce the defects using focused characterization tests before changing production code.

Do not ask for another approval if every gate passes.

Do not push.

Phase 0 — Mandatory preflight

Before editing, report:

* repository root;
* current branch;
* full HEAD SHA and subject;
* HEAD parent topology;
* git status --short;
* staged paths;
* confirmation that HEAD exactly equals <REPAIR_A_FULL_SHA>;
* exact baseline failure names and signatures reported by Repair A.

Stop immediately if:

* the branch differs;
* HEAD differs from the exact Repair A SHA;
* HEAD subject differs;
* worktree or index is not clean;
* baseline failure identities are unavailable;
* unexpected merge/topology changes exist.

A matching failure count alone is not a baseline.

Do not fetch, pull, merge, rebase, reset, checkout, stash, clean, amend, or repair repository state.

Allowed scope

Allowed production files:

1. src/core/validation/DataSourcingConfigValidator.ts
2. src/tools/EtlActionToolService.ts — validation-only hunks defined below

Allowed additional changes:

* directly related focused tests under src/test/**;
* only imports necessary to call an existing shared parser or validation helper.

Do not modify:

* src/core/utils/ModuleSequenceExtractor.ts, unless a focused characterization test proves the shared parser itself violates the trusted contract. If that happens, stop and report; do not expand scope.
* Repair A contract, discovery, fingerprint, reference, documentation, or package-description files;
* resources/framework/contracts/job-config-envelope.v1.json;
* package version, dependencies, or lockfiles;
* evaluation reports or baselines;
* any F5/QA fixture;
* renderer/scaffolding architecture;
* W1 write behavior;
* atomic multi-file apply/rollback;
* durable managed-file ownership;
* sibling repositories or etl-framework-gen-utils.

W1 hunk protection

src/tools/EtlActionToolService.ts overlaps completed W1 work.

Before editing it:

1. Record the exact current line range and deterministic content hash of validateRenderedArtifacts.
2. Record the current bodies and deterministic hashes of all protected W1 methods/regions, including:
    * writeToWorkspace;
    * performWrite;
    * collectManifestFiles;
    * buildApprovalManifest;
    * evaluateToolPlanScopedConsent;
    * preview construction;
    * probing;
    * authorization;
    * approval handling;
    * write-result and per-file result construction.
3. Record the W1 file inventory from commit cb972b7.
4. Record hashes for every W1 file other than the permitted validation-only area.
5. Record the Eval-refresh file inventory from commit a7ec7284906697321b2af5f7bf99de99211f7b70 and their current hashes.

Permitted hunks in EtlActionToolService.ts are limited to:

* validateRenderedArtifacts;
* one narrowly scoped validation-only helper, if genuinely required;
* its necessary import.

No broad formatting, import reordering, method movement, or unrelated cleanup is allowed.

Any hunk touching write, preview, probing, authorization, confirmation, approval, manifest creation, consent evaluation, collision handling, drift handling, filesystem mutation, or write-result construction is an immediate blocker.

If this boundary cannot be maintained, do not commit and report:

REPAIR_B_W1_BOUNDARY_BLOCKED

Phase 1 — Characterization before production edits

Add focused tests before changing either production file.

Run them and record exact pre-fix failures.

If an audited defect cannot be reproduced at the specified real boundary, stop without speculative production changes and report the discrepancy.

1. Data-sourcing grammar characterization

Use repository-owned canonical job-config bytes—not isolated regex fragments.

Parameterize all three trusted HOCON object-opening forms:

* key: {
* key = {
* key {

Cover both:

* the data_sourcing_process stage opener;
* every named sibling source-block opener referenced by sourceList.

For every valid variant, characterize whether validation resolves:

* the correct data_sourcing_process stage rather than a nested source block such as primary;
* options.module;
* options.method;
* a non-empty sourceList;
* every source block named by sourceList.

After repair, valid variants must not produce:

* MISSING_MODULE_OPTIONS
* MISSING_SOURCE_LIST
* MISSING_SOURCE_BLOCK

Preserve negative tests proving that genuinely absent module options, sourceList, or named source blocks remain fail-closed with existing issue codes and messages.

2. Public validation-adapter characterization

Exercise repository-owned canonical dataframe-writer bytes through the real registered etl_validate_artifacts public boundary.

Do not test only a private helper or OutputStrategyConfigValidator in isolation.

Add direct service-level coverage where useful.

Characterize and later prove:

1. blueprint.modules is populated from actual parsed job-config modules in their real order.
2. outputDecision is derived only from recognized modules.
3. dataframe_writer maps to generic_dataframe_write.
4. Existing load_enrich_process, database-output, and TIBCO discriminators retain supported behavior.
5. Unknown or ambiguous module sequences remain fail-closed and still produce OUTPUT_STRATEGY_REVIEW_REQUIRED.
6. The warning is not globally suppressed.
7. OutputStrategyConfigValidator itself is not weakened.

Use the repository-owned canonical dataframe-writer example rather than an approximate replacement.

3. Anti-cascade extension boundary

Feed byte-identical canonical content through the public validator at:

* valid path: job_conf/conf/QA/qa_job.conf
* invalid job-config path: job_conf/conf/QA/qa_job.yaml

For .conf:

* canonical content must produce zero artifact-content errors;
* recognized dataframe-writer content must not receive a false OUTPUT_STRATEGY_REVIEW_REQUIRED.

For .yaml:

* it must fail at the job-config extension boundary;
* it must not additionally report:
    * MISSING_MODULE_OPTIONS;
    * MISSING_SOURCE_LIST;
    * MISSING_SOURCE_BLOCK;
    * OUTPUT_STRATEGY_REVIEW_REQUIRED.

Unrelated environment/readiness warnings may remain only when they exactly match the grounded baseline and are not content defects.

Do not relax the job-config extension validator to accept YAML.

Phase 2 — Production repair

A. DataSourcingConfigValidator

Make DataSourcingConfigValidator consume the trusted module-envelope grammar already used by ModuleSequenceExtractor.

Preferred implementation:

* reuse the existing shared parser;
* select the stage whose module type is data_sourcing_process;
* validate that stage’s content;
* resolve sourceList and its named sibling source blocks using the same accepted object-opening grammar.

Do not retain or introduce three competing colon-only regex implementations.

If named source-block extraction cannot directly reuse the shared parser, use one narrowly scoped validation-local helper whose accepted separators exactly match the trusted contract.

Do not create another independent envelope grammar.

Preserve:

* all existing issue codes;
* all existing issue messages;
* path, zone, read-format, and interpolation rules;
* the existing no-data_sourcing_process early return;
* fail-closed behavior for genuinely missing fields.

B. EtlActionToolService validation adapter

Inside validateRenderedArtifacts only:

* extract the real module sequence from artifacts.jobConfig using the existing shared parser;
* populate blueprint.modules from that real sequence;
* derive outputDecision only when parsed modules provide authoritative recognized evidence.

Required recognized mapping:

* dataframe_writer → generic_dataframe_write

Preserve existing supported handling for:

* load_enrich_process → curated_load_enrich;
* database output;
* TIBCO output.

Use existing discriminators and decision types.

Do not invent a new strategy schema.

If module sequence is absent, conflicting, or unknown:

* do not choose a default;
* remain fail-closed;
* preserve OUTPUT_STRATEGY_REVIEW_REQUIRED.

Do not change any write-path input, output, preview, manifest, approval, consent, or result structure.

Validation order

Run:

1. git diff --check;
2. repository compile/typecheck;
3. focused DataSourcingConfigValidator separator-parity tests;
4. focused validation-adapter tests;
5. real registered etl_validate_artifacts boundary tests;
6. canonical .conf/.yaml anti-cascade tests;
7. unknown-strategy fail-closed test;
8. focused W1 collision, approval, unchanged, and drift regression tests;
9. full unit suite exactly once after focused tests pass.

For the full suite:

* compare each failure by exact test identity and signature with the Repair A baseline;
* matching failure count is insufficient;
* each permitted failure must be demonstrably unaffected by this diff;
* any new, missing, renamed, or behaviorally changed failure blocks the commit.

Do not refresh evaluation artifacts.

Final hunk and byte-identity gate

Before committing:

1. Show git diff --name-status <REPAIR_A_FULL_SHA>.
2. Show git diff --check.
3. Show git diff --unified=0 <REPAIR_A_FULL_SHA> -- src/tools/EtlActionToolService.ts.
4. Prove every EtlActionToolService.ts hunk is limited to:
    * validateRenderedArtifacts;
    * an explicitly validation-only helper;
    * its required import.
5. Recompute protected W1 method/region hashes and prove they are byte-identical.
6. Prove all other W1 files are byte-identical.
7. Prove Eval-report files are unchanged.
8. Prove Repair A contract/discovery files are unchanged by Repair B.
9. Prove package version and dependencies are unchanged.
10. Prove no deterministic fixture was added.
11. List every changed file and justify it against the allowlist.

Any failed proof blocks the commit.

Commit

Only if every gate passes, create exactly one commit:

fix: align artifact validation with canonical contract

Requirements:

* do not amend or squash Repair A;
* the commit’s sole parent must be <REPAIR_A_FULL_SHA>;
* do not create another branch;
* do not push;
* leave worktree and index clean.

Final report

Report:

* branch;
* Repair A starting SHA;
* Repair B full commit SHA and parent SHA;
* exact changed-file inventory;
* pre-fix characterization failures;
* post-fix focused-test results;
* .conf and .yaml anti-cascade results;
* unknown-strategy fail-closed result;
* W1 protected-region before/after hashes;
* focused W1 regression results;
* full-suite totals;
* exact reconciled baseline failure identities;
* confirmation that no fixture, version, Eval report, W1 write behavior, external service, F5 run, or push occurred;
* final git status --short.

Do not claim end-to-end F5 QA is fixed.

The deterministic physical QA fixture remains a separate task.

End with exactly one marker:

REPAIR_B_VALIDATOR_CONSUMPTION_COMMITTED

or:

REPAIR_B_VALIDATOR_CONSUMPTION_BLOCKED
