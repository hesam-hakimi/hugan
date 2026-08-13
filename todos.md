Task: LOCAL-PHASE-A1A-20260813-01
Mode: bounded A0-completion / A1A implementation with isolated verification
Target: extension-source
Delivery: source-and-tests, local-only
Authorized scope: trusted read-only discovery, collision evidence, deterministic lifecycle decision, and planning eligibility only

Architectural decision

Implement the product-correct contract:

Preserve valid direct /create preview flows by deriving planningEligible: true only when all safety-critical trusted evidence is complete.

Do not change Phase 6 or Golden Corpus contracts to expect permanent blocking. Those tests identified a real source regression.

This task authorizes only a narrow A1A prerequisite slice. It does not authorize full Phase A1 generation, apply, approval, guarded writes, packaging, deployment, or release work.

Current evidence

* Repository: TD-Universe/agentic_etl
* Branch: feature/v3-agentic-redesign
* Expected HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* Committed package version: 0.3.139
* Protected dirty package version: 0.3.128
* Candidate and installed VSIX: pre-A0/A1A 0.3.139
* Current pending review card: nine A0R files, approximately +541/-37
* Keep and Undo remain untouched.
* SolutionMemoryStore.ts remains unchanged.
* H/S/T/F triage proved that the six-file source overlay causes three reproducible TRUE_SOURCE_REGRESSION failures:
    1. phase6WriteDeployRun.test.ts expects trusted_preview_validated, but receives trusted_preview_blocked.
    2. goldenCorpusRunner.test.ts expects acceptance rate 1, but receives 0.2222222222222222.
    3. goldenCorpusRunner.test.ts expects canonical ABFSS aiFirst.acceptance === true, but receives false.
* These failures reproduce individually and together with the source overlay.
* They are not caused by test order, shared state, or the A0 test overlay.
* Root cause: TrustedPlanningEvidenceService currently always emits:

evidenceComplete: false
planningEligible: false
applyEligible: false

* AgentActionExecutor therefore blocks every direct /create preview.
* /workflow create was not intercepted and must remain unchanged.

Non-negotiable boundaries

1. Do not click Keep or Undo. Extend the pending review card and leave it pending.
2. Do not stage, commit, push, merge, rebase, switch branches, edit PR #7, or invoke CI.
3. Do not package, rebuild, install, uninstall, or replace a VSIX.
4. Do not install dependencies, compile, test, or generate output inside the real repository.
5. Do not modify any real Consumer workspace or external Databricks, ADF, SQL Server, storage, or other system.
6. Do not implement:
    * apply;
    * approval tokens;
    * writer behavior;
    * atomic writes or rollback;
    * deployment;
    * production release;
    * Phase A1B generation.
7. Direct /create must not invoke:
    * RepoWriter;
    * NewArtifactWriter;
    * writeArtifacts;
    * resolveWorkspacePath;
    * process.cwd();
    * filesystem write APIs;
    * directory creation;
    * write-capable caches.
8. Do not restore ambient/default workspace selection.
9. Do not trust arbitrary request text as workspace identity.
10. Do not weaken fail-closed behavior for incomplete, ambiguous, stale, external, or unsafe evidence.
11. Do not change Phase 6 or Golden expectations to accept blocking, lower acceptance, or remove the ABFSS scenario.
12. Do not use fuzzy scores, filenames, repository names, paths, or sample data as managed ownership identity.
13. Do not treat failed discovery as “no matching job.”
14. Do not treat missing collision evidence as “no collision.”
15. Do not infer credentials, physical paths, environment values, write modes, merge keys, onboarding IDs, output semantics, or business decisions.
16. Do not introduce or depend on:

* CD Renewal
* cd_renewal
* acz0004
* cz_acz0004_retail
* renewal
* sample_sttm

17. Do not change resources/copilot/**, .github/**, AGENTS.md, workflow assets, or existing VSIX files.
18. applyEligible must remain unconditionally false throughout A1A.
19. /workflow create must remain separate and behaviorally unchanged.
20. Preview must remain completely write-free.

Protected files

Do not modify:

* .tsbuildinfo.test
* package.json
* CopilotAssetCatalog.ts
* EtlActionToolService.ts
* SolutionMemoryStore.ts
* RepoWriter.ts
* NewArtifactWriter.ts
* ArtifactReuseAdvisor.ts
* SttmAuditor.ts
* .github/**
* AGENTS.md
* workflow/**
* COPY_ORDER.md
* resources/copilot/**
* real out/**
* existing VSIX files
* real Consumer workspaces

Phase 0 — identity and preflight

Before editing, verify read-only:

* repository origin and canonical root;
* branch and exact HEAD;
* registered worktrees;
* staged state;
* full git status --porcelain;
* committed and dirty package versions;
* candidate VSIX SHA-256;
* installed Extension version;
* canonical paths and SHA-256 hashes of the current nine A0R files;
* hashes of all four protected dirty files;
* protected control-plane hashes.

Expected candidate VSIX SHA-256:

e6ce31f2d1d2a9217e9a4e295bbf2816642eff5613858c39c86872d69d208e98

If identity, pending overlay, or protected state differs materially, stop with:

LOCAL_PHASE_A1A_BLOCKED_IDENTITY_OR_SCOPE

Phase 1 — source and contract discovery

Trace the actual direct /create lifecycle:

* request parsing;
* trusted VS Code workspace/session state;
* explicit workspace selection;
* STTM resolution and hashing;
* TrustedPlanningEvidenceService;
* AgentMessageRouter;
* AgentActionExecutor;
* artifact discovery;
* pure candidate/preview planning;
* preview validation;
* response composition;
* existing ownership/provenance metadata;
* Consumer ETL Framework job, environment, SQL and onboarding contracts.

Determine where exact candidate artifact paths become available.

If candidate paths currently appear only during preview, extract only the minimum pure in-memory descriptor needed before collision inspection:

trusted workspace and STTM
→ read-only repository/job discovery
→ pure candidate path descriptor
→ read-only collision inventory
→ deterministic lifecycle decision
→ planning eligibility
→ in-memory preview and validation

The descriptor must be deterministic, write-free, contained, and must not invent missing values.

Phase 2 — bounded change-manifest gate

Before the first edit, print the exact proposed file list with:

* canonical path;
* existing or new;
* production or test;
* reason;
* requirements covered.

The existing nine A0R files may be revised:

1. TrustedPlanningEvidenceService.ts
2. EtlAgent.ts
3. AgentMessageRouter.ts
4. AgentActionExecutor.ts
5. ResponseComposer.ts
6. index.ts
7. trustedPlanningEvidenceService.test.ts
8. testPatterns.ts
9. phase5AgentRouter.test.ts

Authorize at most five additional files under src/**, solely for:

* trusted selected-workspace/session evidence;
* read-only managed-job discovery;
* read-only collision inventory;
* deterministic lifecycle decisions;
* canonical containment support.

Authorize at most six additional test files, including when necessary:

* phase6WriteDeployRun.test.ts
* goldenCorpusRunner.test.ts
* workspaceInputContainment.test.ts
* focused discovery/collision/decision tests.

Phase 6 and Golden tests may only replace artificial untrusted workspace fixtures with injected trusted workspace/session/STTM/discovery evidence. Preserve their original:

* successful-preview behavior;
* validation assertions;
* acceptance rate 1;
* canonical ABFSS acceptance;
* later isolated write-flow assertions.

Do not lower expected values, remove scenarios, skip tests, or change them to expect trusted_preview_blocked.

If more than five additional production files, six additional test files, a protected file, writer change, or apply/approval change is required, stop before editing with:

LOCAL_PHASE_A1A_BLOCKED_SCOPE_EXPANSION_REQUIRED

If the manifest fits the limits, proceed without waiting for further confirmation.

Phase 3 — trusted immutable evidence

Implement typed immutable evidence containing equivalent concepts:

TrustedPlanningEvidence
├── request/session identity
├── trusted target evidence
├── STTM identity and hash
├── repository discovery snapshot
├── managed-job candidates
├── pure candidate path-set identity
├── collision inventory
├── lifecycle decision
├── unresolved non-safety decisions
├── evidenceComplete
├── planningEligible
├── applyEligible = false
└── deterministic evidence hash

Workspace trust

Workspace selection must originate from a trusted VS Code workspace/session provider.

A request-supplied workspaceRoot is only a selector key. It becomes trusted only if it resolves exactly to an eligible, currently open or explicitly selected workspace in the trusted current workspace set.

Bind evidence to:

* canonical workspace root;
* target classification;
* explicit-selection provenance;
* current workspace-set hash/generation;
* request/session;
* extension source/install roots;
* containment result.

Never select through process.cwd(), repository name, arbitrary prompt text, active editor alone, first-workspace fallback, or RepoWriter.

Multiple eligible roots require a verified explicit selection.

STTM trust

Bind STTM evidence to:

* canonical contained path;
* raw-content SHA-256;
* selected workspace;
* parser result;
* request/session.

Reject missing, external, extension-source, stale, changed, symlink-escaping, or junction-escaping STTM inputs.

Samples and fixtures must never become runtime defaults.

Hashing and immutability

* Canonically sort paths and observations before hashing.
* Exclude timestamps, randomness, credentials, secrets, and temporary-machine prefixes from semantic hashes.
* Bind evidence to workspace state, STTM hash, discovery hash, candidate set, selected candidate, candidate-path set and collision inventory.
* Deep-freeze or otherwise enforce immutability.
* The same immutable evidence identity/content must reach AgentActionExecutor.
* Reject stale evidence instead of recollecting from ambient state.

Phase 4 — read-only repository/job discovery

Discovery must be deterministic, read-only, contained and generic.

Inspect only Consumer ETL Framework contract locations and safely resolved includes.

Existing job, environment, SQL and onboarding files are evidence inputs—not prerequisites for creating a job.

Distinguish:

* confirmed empty selected repository;
* non-empty repository;
* one exact verified managed job match;
* complete no-match;
* multiple candidate matches;
* unmanaged or unknown ownership;
* unreadable path;
* parse failure;
* unresolved include;
* containment failure;
* incomplete discovery.

A repository containing user files but no matching job is non-empty and routes to CREATE_NEW_JOB.

An explicitly selected existing root with a complete empty inventory may route to initialization.

Read, parse or containment failure must never become zero candidates.

Stable managed identity

UPDATE_EXISTING_JOB requires both verified managed ownership and stable exact identity.

Stable identity may derive only from authoritative evidence such as:

* managed asset metadata;
* stable managed job ID;
* managed onboarding identity;
* explicit managed source/target identity;
* explicit current selection referencing a candidate in the current hashed candidate set.

Similarity scoring, names and paths are insufficient.

An explicit selection cannot turn an unmanaged asset into a managed asset.

Duplicate or conflicting identities remain unresolved.

Phase 5 — candidate paths and collisions

Build a pure in-memory candidate path descriptor containing:

* exact workspace-relative paths;
* artifact kinds;
* associated lifecycle candidate;
* deterministic path-set hash.

Do not generate files or guess content/deployment values.

For every candidate path, inventory read-only:

* normalized relative path;
* canonical destination;
* existence;
* ownership state and provenance;
* same managed asset, different managed asset, unmanaged, unknown, or absent;
* safe current content hash where applicable;
* containment;
* collision result.

Rules:

* same verified managed asset may participate in update;
* another managed asset blocks;
* unmanaged or unknown ownership blocks overwrite;
* duplicate normalized candidate paths block;
* missing observer does not mean collision-free;
* read/stat/realpath errors make evidence incomplete;
* Windows comparison is case-insensitive;
* use canonical/real-path containment, not string-prefix checks;
* C:\foo must not contain C:\foobar;
* handle different drives, UNC roots, mixed separators, dot segments, case variations and symlink/junction escape;
* for nonexistent destinations, resolve the nearest existing ancestor before appending remaining normalized segments.

Do not create directories or files.

Phase 6 — deterministic lifecycle decision

Implement a pure typed decision contract:

Evidence	Outcome
One exact verified managed match	UPDATE_EXISTING_JOB
Valid explicit selection of one verified managed current candidate	UPDATE_EXISTING_JOB
Complete discovery, no match, confirmed non-empty Consumer repo	CREATE_NEW_JOB
Complete discovery, confirmed empty selected repo, explicit initialization intent	INITIALIZE_NEW_CONSUMER_REPO
Multiple matches without valid selection	REQUEST_JOB_SELECTION
Stale/invalid selection or incomplete safety evidence	BLOCK_INCOMPLETE_EVIDENCE
Unmanaged/unknown conflicting destination	BLOCK_UNSAFE_OVERWRITE
Extension source/install, external, missing, unknown or unselected target	BLOCK_UNSAFE_TARGET

Job-specific files are not prerequisites for create or initialization.

Missing credentials, physical storage values, environment values, write modes, merge keys, onboarding IDs or business decisions must not be invented.

Distinguish:

* safety-critical unknowns that block planning;
* non-safety deployment/business unknowns that may appear unresolved in a write-free preview while apply remains blocked.

Phase 7 — derive eligibility

Do not hardcode eligibility.

evidenceComplete === true only when all safety evidence needed for planning is complete.

planningEligible === true only when:

* workspace and session evidence is trusted/current;
* STTM is contained/current/hash-verified;
* discovery completed;
* lifecycle outcome is one of:
    * UPDATE_EXISTING_JOB
    * CREATE_NEW_JOB
    * INITIALIZE_NEW_CONSUMER_REPO;
* exact candidate-path set is known and hashed;
* collision evidence is complete;
* no unsafe collision or unresolved safety decision exists.

planningEligible === false for selection requests, incomplete evidence, unsafe target, unsafe overwrite or stale evidence.

applyEligible remains false for every A1A outcome.

Valid complete direct /create must reach in-memory preview and validation.

Incomplete evidence must block before preview and expose deterministic lifecycle/unresolved codes through ResponseComposer.

Phase 8 — close the three regressions

Restore:

1. Phase 6 direct create → trusted_preview_validated.
2. Golden Corpus acceptance rate → 1.
3. Canonical ABFSS aiFirst.acceptance → true.

Do not accomplish this by trusting arbitrary C:\workspace, weakening safety, restoring fallback, or changing expected assertions.

Replace synthetic fixtures with an injected trusted test provider or real isolated temporary selected workspace that supplies:

* trusted open/selected workspace evidence;
* contained STTM identity;
* complete repository discovery;
* exact candidate-path set;
* complete collision inventory.

Phase 9 — executable coverage

All 19 requirements must be executable and COVERED:

1. Explicit workspace provenance.
2. Ambiguous-root fail-closed.
3. No process.cwd() or ambient fallback.
4. Empty-repository initialization intent.
5. STTM identity, SHA-256 and containment.
6. Missing/external/stale/changed STTM rejection.
7. Extension-source/install-root rejection.
8. Windows drive and mixed-separator handling.
9. UNC escape handling.
10. Symlink/junction escape handling.
11. Incomplete job discovery explicitly unresolved.
12. Incomplete collision/ownership explicitly unresolved.
13. Router collects before executor.
14. Same immutable evidence reaches executor.
15. Incomplete evidence blocks preview.
16. Exact lifecycle/unresolved codes reach response.
17. Spies prove zero calls to all writer, preview-when-ineligible and filesystem-write boundaries.
18. /workflow create remains separate.
19. applyEligible === false.

Also test the lifecycle matrix using neutral fixtures:

* one managed match;
* no match in non-empty repository;
* empty repository with explicit initialization intent;
* multiple matches;
* valid and stale explicit selection;
* unmanaged match;
* same/different managed-asset collisions;
* unmanaged/unknown collision;
* unreadable or unparseable discovery;
* unsafe target;
* missing STTM;
* non-safety unresolved value visible in successful preview.

No PARTIAL or GAP is acceptable.

Phase 10 — isolated validation

Do not test in the real worktree.

Create a unique temporary dependency seed from git archive HEAD.

Because HEAD has no lockfile:

* install dependencies only inside the temporary seed;
* record Node/npm versions, install command, exit code, generated lock SHA-256 and npm ls --depth=0;
* label the run UNPINNED_TEMP_DEPENDENCY_RESOLUTION.

Create:

1. A1: clean HEAD
2. B1: clean HEAD plus exact final pending overlay
3. B2: second clean HEAD plus identical overlay
4. A2: second clean HEAD

Use byte-identical dependencies and run in order:

A1 → B1 → B2 → A2

For all four run:

* test TypeScript compilation;
* the exact broader pure-unit command used during triage.

For B1/B2 also run:

* trusted-evidence tests;
* containment tests;
* discovery/collision/lifecycle tests;
* direct /create router/executor tests;
* Phase 6 regression;
* Golden Corpus;
* /workflow create separation;
* registered A0/A1A runner;
* zero-writer/zero-filesystem-write tests;
* git diff --check.

A1A passes only if:

* B1/B2 compile;
* all focused tests pass;
* all 19 requirements are covered;
* all lifecycle cases pass;
* the three regressions disappear;
* Phase 6 returns trusted_preview_validated;
* Golden acceptance is 1;
* canonical ABFSS acceptance is true;
* incomplete evidence still blocks;
* /workflow create is unchanged;
* all zero-write assertions pass;
* B introduces no new or changed broader failure compared with A;
* any pre-existing baseline failures have matching identities and signatures in all four snapshots.

Independent verification and cleanup

Use an independent verifier after implementation.

It must check:

* scope and protected paths;
* workspace provenance;
* stable identity;
* discovery/collision completeness;
* lifecycle and eligibility truth tables;
* evidence immutability;
* all 19 coverage mappings;
* three-regression restoration;
* A/B equivalence;
* absence of weakened assertions.

Delete only the exact temporary roots.

Prove afterward:

* real status contains only the four protected baseline files plus authorized pending A1A files;
* staged state remains empty;
* protected dirty hashes and candidate VSIX hash are unchanged;
* installed/candidate VSIX remains pre-A1A;
* no Consumer, control-plane or external state changed;
* no Git, PR, CI, package, VSIX or installation action occurred;
* Keep/Undo remains untouched;
* Phase A1B did not start.

Required report

Provide:

1. Identity and pre-edit change manifest.
2. Exact final changed-file list and hashes.
3. Trusted evidence schema and provenance.
4. Discovery, ownership and collision rules.
5. Lifecycle and eligibility truth tables with results.
6. Restoration evidence for all three regressions.
7. Complete 19-item coverage matrix with full test titles.
8. Commands, exit codes and counts.
9. A1/B1/B2/A2 failure-equivalence table.
10. Dependency reproducibility disclosure.
11. Independent verifier result.
12. Before/after immutability evidence.
13. Confirmation that applyEligible is always false and direct /create invoked no writer.

End with exactly one token:

LOCAL_PHASE_A1A_IMPLEMENTED_AND_AB_VERIFIED
LOCAL_PHASE_A1A_OVERLAY_REGRESSION
LOCAL_PHASE_A1A_COVERAGE_GAP
LOCAL_PHASE_A1A_INCONCLUSIVE
LOCAL_PHASE_A1A_BLOCKED
