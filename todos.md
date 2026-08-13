Task: LOCAL-PHASE-A1A-PATH-ARCHITECTURE-DESIGN-20260813-01

Mode: read-only architecture and extraction design
Target: extension-source
Delivery: report-only
Mutation authorization: NONE

Accepted finding

The latest blocker is substantiated:

* TrustedCreatePreviewService.ts owns environment selection but is not the canonical owner of all artifact paths.
* Artifact-set and path rules are distributed across:
    * ArtifactGenerationPipeline
    * RepoWriter.generatePaths
    * IncludeFileRenderer
    * EnvConfigRenderer
* Some paths become available only after ETLBlueprint generation or mutation.
* The current generation pipeline may use prompt/AI behavior and therefore cannot be assumed pure or deterministic.
* Adding a descriptor only to TrustedCreatePreviewService would either duplicate path rules or invoke downstream generation/writer dependencies before the correct safety gate.

The previous sixth-file authorization was not used and is insufficient for implementation. Do not attempt another workaround.

Hard boundaries

1. Do not click Keep or Undo; preserve the current pending nine-file review card.
2. Do not edit any source, test, configuration, documentation, package, generated output, or workspace file.
3. Do not start Phase A1B or any implementation.
4. Do not stage, commit, push, merge, switch branches, edit PR #7, or invoke CI.
5. Do not build, package, install, uninstall, or replace a VSIX.
6. Do not install dependencies or compile/test inside the real repository.
7. Do not modify any Consumer workspace or contact an external system.
8. Do not copy current path formulas into a second component.
9. Do not weaken containment, collision safety, ownership verification, preview immutability, or incomplete-evidence blocking.
10. Do not change Phase 6 or Golden Corpus expectations to accept permanent preview blocking.
11. Do not treat fixtures, samples, or AI output as product truth.
12. Do not infer credentials, physical paths, environment values, write modes, merge keys, onboarding IDs, or business decisions.

Only local search, source/contracts/tests reading, static tracing, and reporting are authorized.

1. Identity and immutability

Revalidate read-only:

* repository, origin, branch, and exact HEAD;
* staged state and exact git status --porcelain;
* registered worktrees;
* current nine pending A0R paths and hashes;
* four protected dirty-file hashes;
* committed/worktree package versions;
* candidate and observable installed VSIX identity;
* current review-card state.

If state differs materially, stop with:

LOCAL_PHASE_A1A_PATH_DESIGN_BLOCKED_IDENTITY

2. Complete artifact-path ownership inventory

Trace every artifact and path that can appear for:

* UPDATE_EXISTING_JOB
* CREATE_NEW_JOB
* INITIALIZE_NEW_CONSUMER_REPO

Include at minimum:

* primary job configuration;
* split extract/load job configurations;
* sourcing artifacts;
* transformation SQL;
* writer/output artifacts;
* environment configuration;
* common/shared configuration;
* include and nested-include patches;
* additional-job artifacts;
* onboarding/registration;
* CSV or other declared outputs;
* managed ownership metadata.

For every artifact report:

Artifact kind	Actual path owner/symbol	Required inputs	Available before generation?	Deterministic?	AI-dependent?	Blueprint-mutation-dependent?	Filesystem read/write?	Preview/apply usage

Cite exact canonical files, symbols, callers, and line ranges.

Do not call a component the owner merely because it invokes the actual path-producing symbol.

3. Current call graphs and side effects

Produce exact call graphs for:

1. direct /create;
2. trusted preview;
3. preview validation;
4. later write/apply;
5. /workflow create.

Trace at minimum:

* TrustedCreatePreviewService
* TrustedPlanningEvidenceService
* ArtifactGenerationPipeline
* RepoWriter.generatePaths
* IncludeFileRenderer.renderAll
* IncludeFileRenderer.ensureModuleIncludes
* EnvConfigRenderer.buildEnvConfigPath
* lifecycle/reuse classifiers;
* collision and ownership services;
* validators;
* write services.

For every relevant symbol identify:

* pure/stateful;
* synchronous/asynchronous;
* filesystem reads;
* filesystem writes;
* directory creation;
* cache or plan mutation;
* ambient workspace or process.cwd() usage;
* model/AI invocation;
* timestamps/randomness;
* writer dependency.

Explicitly answer:

* Does ArtifactGenerationPipeline perform any write or directory creation?
* Does it call RepoWriter, NewArtifactWriter, writeArtifacts, or an external operation?
* Does AI control artifact content, artifact identity, filenames, paths, or all of them?
* What is the earliest point where the exact complete normalized candidate path set exists?
* Can exact paths be obtained without AI or blueprint mutation?
* Can generation safely execute once, entirely in memory, before collision inspection?
* Does full preview regenerate or recompute any artifact/path?
* Can renderers consume supplied paths instead of independently creating them?

4. Contract truth analysis

For every current path rule classify it as:

* explicitly defined by authoritative ETL Framework contracts/templates;
* deterministically derived from trusted STTM/job identity;
* derived from grounded environment selection;
* embedded only in RepoWriter;
* embedded only in a renderer;
* selected by AI;
* fixture/sample convention only;
* unresolved.

Identify which path decisions require:

* selected Consumer root;
* lifecycle route;
* stable managed job identity;
* deterministic STTM-derived module plan;
* environment selection;
* discovered managed artifact paths;
* logical source/target/output evidence;
* unresolved deployment or business values.

If a path cannot be known without guessing, report it as unresolved.

5. Compare the coherent architecture options

Option A — deterministic structural path plan

trusted evidence
→ discovery
→ lifecycle/environment decision
→ pure StructuralArtifactPlan
→ exact path manifest
→ collision inspection
→ planningEligible
→ in-memory content generation
→ trusted preview

Select this only if every artifact identity and path can be derived without AI, content generation, blueprint mutation, writer access, or guessed values.

Option B — two-gate, render-once architecture

trusted evidence
→ discovery
→ lifecycle/environment decision
→ candidateGenerationEligible
→ one completely write-free in-memory generation
→ frozen exact candidate manifest
→ containment/collision/ownership inspection
→ previewEligible/planningEligible
→ validation and user-visible trusted preview

Select this only if generation can be proven to have:

* zero filesystem writes;
* zero directory creation;
* zero writer calls;
* zero external operational actions;
* no Consumer mutation.

The exact generated paths/content/environment result must be frozen and reused without regeneration.

Option C — pure generation-core extraction

Refactor the current generation pipeline into:

* a pure in-memory candidate-generation core;
* separate validation;
* separate later writer/apply adapter.

Select this if exact paths require generation but the current generation pipeline is not sufficiently side-effect-free.

Option D — hybrid

Use deterministic structural planning for artifact identities and contract-derived paths, followed by one frozen in-memory generation step for genuinely content-dependent information.

Select this only if it still provides one canonical owner per path rule and no duplicated formulas.

Compare:

Criterion	A	B	C	D
One canonical path truth				
No write before approval				
Handles AI nondeterminism				
Exact collision inventory				
UPDATE path preservation				
CREATE/INITIALIZE support				
Environment-selection support				
Windows containment				
Phase 6/Golden compatibility				
Dependency-cycle risk				
Estimated production files				
Estimated test files				
Migration risk				

Recommend exactly one architecture and reject the others using source evidence. Do not choose solely by lowest file count.

6. Required safety state machine

The recommended design must distinguish, where necessary:

* evidenceComplete
* candidateGenerationEligible
* manifestComplete
* previewEligible or planningEligible
* applyEligible

Do not overload one flag across multiple lifecycle stages.

Required rules:

* unknown/unsafe workspace blocks before generation;
* missing or external STTM blocks before generation;
* multiple matching jobs request explicit selection;
* incomplete discovery must not mean “no match”;
* one stable managed match routes to update;
* no match in a confirmed existing repository routes to create;
* an explicitly confirmed empty repository routes to initialize;
* unmanaged collisions block after the exact candidate path set is known;
* preview is always write-free;
* applyEligible remains unconditionally false in this phase;
* /workflow create remains separate and unchanged.

7. Canonical immutable manifest design

Specify the minimum immutable candidate-manifest schema, including:

* workspace/session binding;
* STTM identity and SHA-256;
* discovery snapshot hash;
* lifecycle route;
* environment-selection outcome;
* stable artifact ID;
* artifact kind;
* normalized relative path;
* canonical contained destination;
* path provenance;
* ownership observation;
* content or deferred-content status;
* content SHA-256 when generated;
* path-set hash;
* manifest hash;
* unresolved non-safety decisions;
* blockers.

For each field state:

* which component creates it;
* when it becomes available;
* whether it is safety-critical;
* how immutability is enforced;
* how collision inspection, preview, and future apply consume the identical manifest;
* how drift, replay, regeneration, or stale evidence is rejected.

8. Exact phased migration plan

Design implementation slices but do not implement them.

For each slice provide:

* exact production files;
* exact test files;
* new files, if any;
* symbols changed;
* dependency direction;
* compatibility/delegation approach;
* behavior preserved;
* acceptance tests;
* explicit scope expansion required.

At minimum separate:

1. extracting or defining canonical path/layout ownership with parity tests;
2. changing existing path producers to delegate to or consume it;
3. separating mutating include behavior from in-memory preview behavior;
4. adding discovery/collision and the necessary eligibility gates;
5. restoring valid Phase 6 and Golden direct-create preview flows;
6. complete isolated A/B validation.

Explicitly answer:

* Must RepoWriter.generatePaths be extracted or become a thin delegate?
* Must RepoWriter itself change?
* Must ArtifactGenerationPipeline change?
* Must IncludeFileRenderer change?
* Must EnvConfigRenderer change?
* Can TrustedCreatePreviewService remain environment-selection/orchestration-only?
* Where is collision inspection performed?
* Where does the manifest become authoritative?
* How does future write consume it without recomputing paths?
* What is the smallest coherent scope that does not duplicate logic?

No proposed slice is authorized by this task.

9. Future executable test plan

Design coverage for:

* manifest/preview/write path parity;
* no hidden path recomputation;
* no writes during evidence, generation, collision, or preview;
* AI nondeterminism captured by immutable hashes;
* regenerated-content or path drift rejection;
* update-path preservation;
* create and empty-repository initialization;
* environment reuse, absence, ambiguity, and stale selection;
* managed/unmanaged/unknown ownership;
* duplicate/case-alias paths;
* Windows mixed separators and drive behavior;
* UNC and different-drive escape;
* C:\foo versus C:\foobar;
* .. traversal;
* symlink/junction escape;
* stale workspace/STTM/discovery/manifest;
* all three existing Phase 6/Golden regressions;
* /workflow create separation;
* applyEligible === false.

Provide the future A1 → B1 → B2 → A2 validation matrix and failure-equivalence criteria.

Final report

Return:

1. Identity and immutability evidence.
2. Complete artifact/path ownership table.
3. Current call graphs and side-effect matrix.
4. Earliest exact-manifest point.
5. Contract-derived versus AI/implementation-derived path table.
6. Architecture-option comparison.
7. Exactly one recommended architecture.
8. Exact eligibility state machine.
9. Immutable manifest schema.
10. Phased file/symbol migration plan.
11. Scope expansion required per slice.
12. Dependency-cycle and semantic-cycle assessment.
13. Future executable test/A/B plan.
14. Confirmation that no file changed and no Keep/Undo, Git/PR/CI, package/VSIX/install, Consumer, or external action occurred.

End with exactly one token:

LOCAL_PHASE_A1A_PATH_ARCHITECTURE_DESIGN_READY
LOCAL_PHASE_A1A_PATH_ARCHITECTURE_DESIGN_INCONCLUSIVE
LOCAL_PHASE_A1A_PATH_DESIGN_BLOCKED_IDENTITY
