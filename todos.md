/build

Implement only the first bounded local-only phase of the generic ETL job lifecycle:

DETERMINISTIC ETL LIFECYCLE ROUTING AND ZERO-WRITE PLANNING PREVIEW

This is an Extension-source implementation task. It is not a Consumer ETL job-generation task, packaging task, Git task, PR task, CI task, or deployment task.

Use the four ETL reference documents and the two recent read-only audit results as context. Current source, contracts, tests, and the explicit requirements below remain authoritative.

1. Hard restrictions

Do not:

* stage, commit, amend, push, pull, merge, rebase, switch branches, or alter Git state;
* edit Draft PR #7;
* trigger, rerun, cancel, or change CI/CD;
* change package version;
* build, package, install, uninstall, or replace a VSIX;
* change the installed Extension;
* invoke Databricks, ADF, DBFS, SQL Server, Jira, or Confluence operations;
* write to a real Consumer ETL workspace;
* invoke any production writer or Apply operation;
* implement atomic apply or rollback in this phase;
* mass-replace CD Renewal or other sample-related literals;
* modify maintainer .github/**, root AGENTS.md, workflow/**, or COPY_ORDER.md;
* invent credentials, storage values, environment values, writer modes, merge keys, onboarding identities, or business decisions.

Any delegated sub-agent must receive the same restrictions.

2. Mandatory read-only preflight

Before modifying anything, report:

* Git top-level repository path;
* repository identity/origin;
* current branch;
* exact HEAD SHA;
* registered worktrees;
* staged, unstaged, and untracked state;
* all VS Code workspace roots;
* which root is the Extension source;
* package version;
* candidate VSIX identity, if present;
* installed Extension version, if observable;
* whether source, out/**, candidate VSIX, and installed VSIX represent the same build.

Expected—but not automatically trusted—state:

* repository: TD-Universe/agentic_etl
* branch: feature/v3-agentic-redesign
* reported HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847

Preserve all pre-existing dirty files.

The following were previously reported as user-owned dirty files:

* .tsbuildinfo.test
* package.json
* CopilotAssetCatalog.ts
* EtlActionToolService.ts

Inspect their current diffs read-only. Do not reset, restore, overwrite, stage, reformat, or incorporate them into this task.

If the correct implementation necessarily overlaps one of these dirty files and the existing intent cannot be preserved with certainty, stop before editing and return a precise overlap report.

If repository or branch identity is wrong or ambiguous, stop before editing.

A source/VSIX/installed-version mismatch should be reported. It does not authorize packaging or installation during this phase.

3. Reconciled starting findings

Treat these as the current working interpretation, but verify the relevant integration points before editing:

1. No behavior-affecting CD Renewal, acz0004, or sample_sttm hard-code was established in the inspected shipped runtime.
2. cd_renewal may exist as a structural STTM template label; do not rename it unless current evidence proves externally visible behavioral coupling.
3. TARGET_WORKSPACE_IDENTITY_REQUIRES_USER_CONFIRMATION was not found as a production result identifier in the inspected source/package.
4. The observed blocked behavior can be explained by the generic multi-root guard:
    multiple eligible roots + no explicit workspaceRoot + no active-editor selection → fail closed.
5. @etl /workflow create currently initializes managed Copilot workflow assets. Preserve that meaning. Do not repurpose it as the ETL job lifecycle.
6. Discovery, scoring, scaffold, preview, and writer components exist, but isolated component existence is not proof of a complete ETL lifecycle.
7. Similarity scoring may identify candidates, but it is not sufficient evidence for automatic update.
8. Generic scaffold fragments are not equivalent to an end-to-end empty-repository initializer.
9. Unmanaged job-artifact collision lacks sufficient ownership enforcement for the required product contract.

4. Goal

Add one trusted, typed, deterministic ETL lifecycle decision layer, integrated into the existing read-only ETL job planning path.

Do not create a duplicate planning pipeline. First trace the current planning call graph and choose the smallest existing integration point.

Preserve /workflow create as Copilot workflow-asset initialization.

The new decision layer must accept explicit, structured evidence including:

* explicitly selected and containment-validated workspaceRoot;
* explicit initialization intent where an empty repository is involved;
* validated STTM identity/evidence;
* discovered job artifacts;
* managed-ownership or stable job-identity evidence;
* explicit user job selection, if provided;
* detected destination collisions;
* unresolved operational or business decisions.

Do not use:

* repository name similarity as ownership proof;
* workbook name similarity as ownership proof;
* sample identities;
* process.cwd() as an implicit Consumer target;
* prompt text as a substitute for trusted runtime enforcement.

5. Typed decision contract

Design the contract so that lifecycle routing and preview readiness are not collapsed into one ambiguous string.

The lifecycle route must be exactly one of:

* UPDATE_EXISTING_JOB
* CREATE_NEW_JOB
* INITIALIZE_NEW_CONSUMER_REPO
* REQUEST_JOB_SELECTION
* BLOCK_UNSAFE_TARGET
* BLOCK_UNSAFE_OVERWRITE

For routable create/update/initialize results, separately report preview readiness:

* READY_FOR_PLANNING_PREVIEW
* PREVIEW_WITH_UNRESOLVED_DECISIONS

The result must include, as applicable:

* selected workspace identity;
* STTM identity/hash or other stable reference;
* route;
* readiness;
* evidence used;
* matching job candidates;
* selected stable managed identity;
* unresolved decisions;
* detected collisions;
* blocked artifacts;
* reason codes;
* applyEligible: false.

This phase must always return applyEligible: false.

This is a planning preview, not an approval-bound write manifest.

6. Deterministic decision rules

Implement these rules:

A. Exactly one matching managed job

Return UPDATE_EXISTING_JOB only when stable identity is supported by trusted evidence such as:

* managed-asset identity;
* stable job ID;
* authoritative onboarding identity;
* canonical managed path plus ownership evidence;
* or an explicit trusted user selection among presented candidates.

A heuristic or similarity score alone must never auto-select update.

B. Valid non-empty Consumer repository with no matching job

Return:

CREATE_NEW_JOB

The absence of an existing job, environment file, onboarding file, or SQL file is not itself a blocker.

C. Explicitly selected empty Consumer repository

Return:

INITIALIZE_NEW_CONSUMER_REPO

only when:

* the workspace was explicitly selected;
* initialization intent is explicit;
* the root passes containment and safety checks;
* it is not Extension source, installation, external, stale, or ambiguous.

Do not reject the target merely because job_conf, env_conf, onboarding, or managed context does not yet exist.

Emptiness by itself is not authorization.

D. Multiple plausible matches

Return:

REQUEST_JOB_SELECTION

Include deterministic candidate identities and evidence. Do not auto-select using score alone.

E. Unmanaged or user-owned collision

Return:

BLOCK_UNSAFE_OVERWRITE

An overwrite: true flag alone is not authorization.

Do not invoke a writer.

F. Unsafe target

Return:

BLOCK_UNSAFE_TARGET

for:

* Extension source;
* Extension installation;
* external/unselected root;
* unknown root;
* stale session path;
* ambiguous multi-root selection;
* path traversal or containment failure.

Preserve the current correct fail-closed multi-root behavior.

G. Missing operational or business decision

Preserve the underlying lifecycle route, but set:

readiness: PREVIEW_WITH_UNRESOLVED_DECISIONS

and:

applyEligible: false

Examples include missing:

* physical source or destination path;
* compatible environment value;
* write mode;
* merge key;
* credential;
* onboarding identity;
* generation-affecting business decision.

Do not invent a value.

7. Zero-write requirement

The entire phase must remain planning/preview-only.

The new route must not:

* create directories;
* create or modify Consumer artifacts;
* invoke RepoWriter, NewArtifactWriter, writeArtifacts, or equivalent write methods;
* create approval state;
* call Apply;
* write managed-ownership metadata;
* publish, deploy, register, or run anything.

Add an explicit production guard or architecture boundary preventing the new planning route from reaching a writer.

8. Required neutral contract tests

Use entirely neutral names. Do not use:

* CD Renewal
* cd_renewal
* acz0004
* cz_acz0004_retail
* renewal
* sample_sttm
* historical repository or workbook names

Every filesystem-capable test must use a unique OS temporary workspace with reliable teardown.

Add tests for:

1. stable managed match → UPDATE_EXISTING_JOB;
2. similarity-only match → must not auto-update;
3. valid non-empty Consumer repository with no match → CREATE_NEW_JOB;
4. explicitly selected empty repository with initialization intent → INITIALIZE_NEW_CONSUMER_REPO;
5. empty repository without explicit initialization intent → safe block/request, never initialization by inference;
6. multiple matches → REQUEST_JOB_SELECTION;
7. unmanaged collision → BLOCK_UNSAFE_OVERWRITE;
8. Extension-source target → BLOCK_UNSAFE_TARGET;
9. external, stale, traversal, or ambiguous multi-root target → BLOCK_UNSAFE_TARGET;
10. missing deployment/business values → original lifecycle route plus PREVIEW_WITH_UNRESOLVED_DECISIONS;
11. neutral renamed repository, workbook, job, and target → identical routing semantics;
12. /workflow create remains workflow-asset setup and is not repurposed;
13. no writer is invoked for any planning result;
14. directory snapshot before and after every scenario proves zero Consumer-workspace mutation;
15. real Extension .github/** and other protected paths remain byte-identical.

Do not weaken or rewrite unrelated tests merely to obtain green results.

9. Validation allowed in this phase

Run only:

* the new targeted contract tests;
* directly affected existing routing/containment tests;
* a safe TypeScript type-check or lint limited to affected files, if it can run without changing protected or pre-existing dirty files.

If a repository script would modify .tsbuildinfo.test, package files, compiled output, snapshots, lockfiles, caches inside tracked locations, or another dirty/protected file, do not run it directly. Use an isolated temporary output location where supported, or report the limitation.

Do not:

* perform full packaging;
* build a VSIX;
* install or activate a new version;
* change evaluation baselines;
* run CI.

10. Likely areas to inspect—not automatic edit authorization

Inspect the current roles and call graph around:

* WorkflowTargetResolver
* ArtifactDiscovery
* ArtifactReuseScorer
* ArtifactReuseAdvisor
* ArtifactReuseConversationCoordinator
* ArtifactPatchPlanner
* ArtifactPreviewService
* RepoWriter
* NewArtifactWriter
* EtlActionToolService
* relevant packaged create/validate assets under resources/copilot/**

Edit only the smallest necessary files.

Do not modify EtlActionToolService.ts while it remains an unresolved user-owned dirty file. If integration requires it, stop and report the exact required changes without applying them.

11. Explicitly deferred

Do not implement in this phase:

* full job/env/shared/SQL/onboarding candidate generation;
* approval-bound exact-byte manifest;
* managed-ownership registry writes;
* filesystem Apply;
* transactional write;
* compensating rollback;
* replay or concurrent approval consumption;
* post-create idempotent Apply;
* package/version/VSIX work;
* installed-extension smoke testing;
* Git, PR, CI, Production, Databricks, ADF, or SQL Server work.

These belong to later phases:

1. complete in-memory candidate generation;
2. trusted approval and atomic guarded Apply;
3. failure injection and idempotency;
4. clean local VSIX rebuild/install/smoke;
5. formal Git/PR/CI closure.

12. Required final report

Return:

1. identity/preflight evidence;
2. source/out/VSIX/installed-version parity status;
3. reconciled current behavior;
4. selected integration point and why;
5. exact files changed;
6. final typed decision contract;
7. scenario A–G decision matrix;
8. targeted tests and exact results;
9. zero-write evidence;
10. protected/dirty-file preservation evidence;
11. known limitations and next implementation phase;
12. explicit confirmation that no Git, PR, CI, package, VSIX, installation, deployment, or real Consumer-workspace action occurred.

End with exactly one:

LOCAL_PHASE_A_DETERMINISTIC_ROUTING_IMPLEMENTED_AND_VERIFIED

or:

LOCAL_PHASE_A_BLOCKED_BEFORE_UNSAFE_OR_OVERLAPPING_CHANGE
