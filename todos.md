/build

Start a new bounded task:

LOCAL PHASE A0 — PLANNING-ONLY WORKSPACE AND EVIDENCE COLLECTION BOUNDARY

The previous Phase A task correctly stopped with:

LOCAL_PHASE_A_BLOCKED_BEFORE_UNSAFE_OR_OVERLAPPING_CHANGE

Resume development by implementing only the missing trusted, read-only evidence boundary required before deterministic ETL lifecycle routing.

Do not implement the lifecycle decision matrix yet.

1. Scope

Implement a planning-only evidence collector and typed lifecycle-planning context for the direct ETL /create path.

The direct /create call path was reported as:

ETLChatParticipant
→ AgentMessageRouter
→ AgentActionExecutor
→ planning/preview

The collector must execute before lifecycle planning or preview.

It must not use RepoWriter to resolve the workspace and must not invoke any writer.

Preserve the separate meaning of:

/workflow create

It remains managed Copilot workflow-asset setup and must not be repurposed as ETL job creation.

2. Restrictions

Do not:

* stage, commit, push, merge, rebase, or alter Git state;
* edit Draft PR #7;
* perform any CI/CD action;
* change package version;
* modify or regenerate a VSIX;
* install or change the installed Extension;
* modify a real Consumer workspace;
* invoke RepoWriter, NewArtifactWriter, writeArtifacts, Apply, approval, publish, deploy, register, or run;
* implement lifecycle routing outcomes;
* implement candidate artifact generation;
* implement atomicity, rollback, or idempotent Apply;
* modify maintainer .github/**, AGENTS.md, workflow/**, or COPY_ORDER.md;
* invent missing STTM, job, ownership, infrastructure, environment, or business evidence.

All delegated agents must follow the same restrictions.

3. Mandatory source/version identity gate

Before editing, report read-only evidence for:

* repository root and origin;
* current branch;
* exact HEAD SHA;
* worktrees;
* staged, unstaged, and untracked files;
* current worktree package.json version;
* committed HEAD package.json version using the HEAD blob, not the dirty working copy;
* current worktree and committed blob hashes for:
    * package.json
    * CopilotAssetCatalog.ts
    * EtlActionToolService.ts
* candidate VSIX version/hash, if available;
* installed Extension version, if observable.

Current reported state:

* repository: TD-Universe/agentic_etl
* branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* working package.json: 0.3.128
* candidate/installed Extension: 0.3.139

Apply this gate:

Case A

If committed HEAD package.json is 0.3.139 and the 0.3.128 value exists only in the protected dirty working copy:

* report WORKTREE_PACKAGE_VERSION_DIRTY_MISMATCH;
* preserve the dirty file;
* continue source-only Phase A0 without changing package.json.

Case B

If committed HEAD is not 0.3.139, or the expected repository/branch/HEAD cannot be proven:

* stop before editing;
* report the exact source/package/runtime mismatch;
* finish with the blocked status token specified below.

Do not “fix” the mismatch by editing or restoring package.json.

4. Protected dirty files

The following are user-owned pre-existing changes:

* .tsbuildinfo.test
* package.json
* CopilotAssetCatalog.ts
* EtlActionToolService.ts

Do not edit, reset, restore, reformat, stage, or overwrite them.

Phase A0 must be designed around them.

If the evidence boundary cannot be integrated without modifying one of these files, stop before editing and report the exact required overlap.

5. New planning evidence contract

Introduce an immutable typed contract equivalent in semantics to:

type EtlPlanningEvidenceRequest = {
  requestedWorkspaceRoot?: string;
  workspaceSelectionSource:
    | "explicit_argument"
    | "trusted_workspace_selection"
    | "active_editor"
    | "single_eligible_root"
    | "none";
  initializationIntent?: "none" | "initialize_new_consumer_repo";
  requestedSttmPath?: string;
  explicitJobSelection?: string;
};
type EtlPlanningEvidence = {
  workspace: {
    selectionSource: string;
    requestedRoot?: string;
    canonicalRoot?: string;
    targetType:
      | "consumer_etl_workspace"
      | "empty_consumer_initialization_candidate"
      | "temporary_test_workspace"
      | "extension_source"
      | "extension_installation"
      | "external"
      | "unknown";
    explicitlySelected: boolean;
    containmentValidated: boolean;
    evidence: string[];
    blockers: string[];
  };
  initializationIntent: {
    explicit: boolean;
    requested: boolean;
  };
  sttm: {
    requestedPath?: string;
    canonicalPath?: string;
    workspaceRelativePath?: string;
    exists: boolean;
    containmentValidated: boolean;
    sha256?: string;
    evidence: string[];
    blockers: string[];
  };
  discoveredJobs: Array<{
    candidateId: string;
    canonicalJobConfigPath?: string;
    stableJobId?: string;
    onboardingIdentity?: string;
    managedAssetId?: string;
    ownershipProven: boolean;
    evidence: string[];
  }>;
  explicitJobSelection?: {
    candidateId: string;
    selectionSource: "trusted_user_selection";
  };
  collisions: Array<{
    relativePath: string;
    exists: boolean;
    ownership: "managed" | "unmanaged" | "unknown";
    evidence: string[];
  }>;
  unresolvedDecisions: Array<{
    code: string;
    affectedArtifacts: string[];
    requiredFrom: "user" | "repository" | "sttm" | "external_runtime";
  }>;
  evidenceComplete: boolean;
  planningEligible: boolean;
  applyEligible: false;
};

Exact type and symbol names may follow repository conventions, but all semantics above must be represented.

Do not add fields whose values would need to be guessed.

6. Planning-only workspace resolver

Implement a read-only workspace-resolution component for planning.

It must:

1. accept an explicit trusted workspaceRoot;
2. canonicalize paths using platform-aware path handling;
3. preserve Windows and POSIX behavior;
4. check containment and filesystem identity;
5. distinguish Extension source, installation, Consumer, temporary-test, external, empty, and unknown roots;
6. preserve fail-closed multi-root behavior;
7. never use process.cwd() as an implicit Consumer target;
8. never call RepoWriter.resolveWorkspacePath;
9. never select a root merely because ETL artifacts were discovered there;
10. record the selection source and evidence.

Selection precedence:

1. explicit trusted workspaceRoot;
2. trusted VS Code workspace selection;
3. active editor only when it unambiguously belongs to exactly one eligible root;
4. single eligible root;
5. otherwise return structured ambiguity evidence and planningEligible: false.

An explicitly selected empty root may be classified as:

empty_consumer_initialization_candidate

only when initializationIntent is explicitly supplied and containment succeeds.

An empty directory alone is not authorization.

7. STTM identity collection

The collector must resolve the requested STTM only against the selected planning workspace.

It must:

* canonicalize the exact requested path;
* verify containment;
* verify existence/readability;
* compute a stable SHA-256 when readable;
* retain canonical and workspace-relative identity;
* reject traversal, external, stale-session, Extension-source, installation, and sample fallback paths;
* never substitute sample_sttm or another workbook;
* return structured blockers when the path is absent or invalid.

Do not parse business rules or generate artifacts in this phase. This phase establishes stable STTM identity only.

8. Read-only job and ownership evidence

Use existing read-only discovery services where safe, but do not treat their scores as ownership.

Collect job candidates and distinguish:

* stable managed identity;
* onboarding identity;
* stable job ID;
* canonical job-config path;
* managed-asset identity;
* similarity-only candidate;
* no ownership evidence.

Rules:

* similarity score is candidate evidence only;
* repository-name similarity is not identity;
* STTM/workbook-name similarity is not identity;
* an existing file is not automatically managed;
* missing artifacts are valid evidence and must not cause a write or failure by themselves;
* do not select the final lifecycle route in Phase A0.

9. Collision evidence

Perform a read-only collision inventory for known/planned destinations only when those destinations can be derived without guessing.

Classify existing paths as:

* managed
* unmanaged
* unknown

Do not overwrite, skip, repair, or approve anything.

If destination paths cannot yet be derived safely, record an unresolved decision instead of inventing paths.

10. Integration into the v3 /create planning path

Propagate the typed evidence result through the direct /create planning path before preview.

Requirements:

* planning receives the evidence object, not just free-form plan text;
* missing evidence remains explicit;
* the collector may return planningEligible: false;
* no preview that implies safe routing may be produced when mandatory evidence is missing;
* no writer may be invoked;
* no scoring result may be promoted to managed identity;
* existing /workflow create behavior remains unchanged.

If the existing v3 message/request shape cannot carry the evidence without changing a protected dirty file, stop and report the exact limitation.

Do not parse untrusted free-form user text into trusted workspace, STTM, initialization, job-selection, or ownership evidence.

11. Required Phase A0 tests

Use neutral names and unique OS temporary workspaces.

Do not use CD Renewal, cd_renewal, acz0004, renewal, or sample_sttm.

Add tests proving:

1. explicit workspace selection is retained with provenance;
2. unambiguous active-editor selection is handled;
3. ambiguous multi-root selection fails closed;
4. no workspace is selected through process.cwd();
5. Extension-source and installation roots are rejected;
6. external, traversal, mixed-separator, different-drive, UNC, and symlink/junction escapes are rejected where applicable;
7. an explicitly selected empty root plus explicit initialization intent becomes an initialization candidate;
8. an empty root without initialization intent is not authorized;
9. a contained STTM receives stable canonical identity and SHA-256;
10. missing or external STTM produces structured blockers;
11. no sample workbook fallback occurs;
12. job candidates remain candidates unless stable ownership evidence exists;
13. similarity scoring never becomes managed identity;
14. unmanaged/unknown collision evidence is retained;
15. incomplete evidence results in:
    * evidenceComplete: false
    * planningEligible: false where mandatory
    * applyEligible: false
16. direct /create receives structured evidence before planning/preview;
17. /workflow create remains unchanged;
18. RepoWriter, NewArtifactWriter, and all write methods are never invoked;
19. real Consumer workspaces and protected Extension paths remain byte-identical.

12. Validation

Run only:

* new Phase A0 targeted tests;
* directly affected existing read-only workspace/containment tests;
* safe affected-file lint/type-check where it does not modify protected dirty files.

If normal commands would change .tsbuildinfo.test, compiled output, package files, snapshots, lockfiles, or tracked caches, use an isolated temporary build/test location where supported.

Do not run package, install, VSIX, CI, or live-provider validation.

13. Explicitly deferred

Do not implement yet:

* UPDATE_EXISTING_JOB
* CREATE_NEW_JOB
* INITIALIZE_NEW_CONSUMER_REPO
* REQUEST_JOB_SELECTION
* BLOCK_UNSAFE_OVERWRITE
* lifecycle decision precedence;
* full artifact candidate manifest;
* SQL/job/env/onboarding rendering;
* approval or Apply;
* writer hardening;
* atomicity or rollback;
* idempotency.

Those begin only after Phase A0 supplies trustworthy structured evidence.

14. Required final report

Report:

1. source/version identity gate result;
2. exact cause of the 0.3.128 versus 0.3.139 mismatch;
3. protected dirty files and proof they remained unchanged;
4. selected architecture/integration point;
5. evidence contract;
6. files changed;
7. tests executed and exact results;
8. evidence that /create no longer depends on RepoWriter for planning workspace selection;
9. evidence that no writer was invoked;
10. evidence of zero real Consumer-workspace mutation;
11. remaining work for Phase A1 deterministic lifecycle decisions.

Finish with exactly one:

LOCAL_PHASE_A0_PLANNING_EVIDENCE_BOUNDARY_IMPLEMENTED_AND_VERIFIED

or:

LOCAL_PHASE_A0_BLOCKED_BY_SOURCE_IDENTITY_OR_PROTECTED_FILE_OVERLAP
