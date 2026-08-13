TASK: LOCAL-PHASE-A1B-PATH-POLICY-ADR-PROPOSAL-20260813-01

Mode: strictly read-only maintainer-decision formalization.
Output: report-only proposed ADR in Chat.
Implementation authorization: NONE.
Slice 2 implementation: PROHIBITED.

Current checkpoint

The authoritative contract-extraction audit completed with:

LOCAL_PHASE_A1B_CONTRACT_EXTRACTION_MAINTAINER_DECISION_REQUIRED

It proved that:

* the ETL Framework is repository-layout agnostic;
* the current Extension has divergent CREATE-path producers;
* UPDATE/reuse preserves discovered Job and Environment paths verbatim;
* ten preservation, include, ownership and path-safety rules are supported by evidence;
* full Slice 2 is blocked by product-contract decisions;
* the combined review card still contains the unaccepted nine-file A0R overlay;
* Phase-H staleness remains a separate pre-existing governance blocker.

Non-negotiable controls

Do not:

* create, edit, delete, rename, format or save any file, including an ADR file;
* click Keep or Undo;
* stage, commit, push, merge, rebase, switch branches, stash or modify any worktree;
* modify Git, PR, CI, evaluation or Phase-H state;
* build, package, install, uninstall or replace a VSIX;
* write to a Consumer workspace or external system;
* deploy or publish any artifact;
* start, scaffold, design in code or implement Slice 2;
* reinterpret examples, fixtures, customer repositories or producer prevalence as authority.

At the start and end, revalidate repository identity, branch, HEAD, staged state, pending-path manifest, protected hashes, worktrees, VSIX identity and all existing safety boundaries. Prove the real workspace remained byte-identical.

Accepted maintainer direction

These are approved product directions, not evidence-proven Framework contracts.

Direction 1 — Deployment fidelity: Decision 4A

The canonical development publisher must mirror the artifact’s repositoryRelativePath beneath its explicitly configured deployment root, matching the Enterprise CD filePath semantics.

Requirements:

* do not hard-code or infer a physical DBFS root;
* deployment root remains an externally supplied deployment value;
* legacy fixed-template publishing is not silently treated as canonical;
* any legacy compatibility strategy must be explicit, versioned and fail-closed;
* repository, deployment and registration paths must not be collapsed into one ambiguous field.

Direction 2 — Primary Job Config CREATE

Use evidence-first layout resolution.

* UPDATE and reuse preserve the selected existing path verbatim.
* For CREATE in an established repository, an unambiguous supported local convention may be selected.
* Producer count, file count and majority voting must not select a convention.
* Conflicting or incomplete evidence must block.
* No zero-evidence fallback grammar has yet been ratified.

Do not interpret this direction as approval of:

* job_conf/conf/<name>.json;
* job_conf/<name>.json;
* conf/jobs/<name>_config.json;
* any sanitizer;
* any split EXTRACT/LOAD filename;
* or any implicit default.

Direction 3 — Environment Config CREATE: Decision 2B

Use evidence-first layout resolution.

* UPDATE and reuse preserve the selected existing directory, filename, environment segment and extension verbatim.
* CREATE may derive a convention only from unambiguous trusted repository evidence.
* Conflicting or incomplete evidence must block.
* No zero-evidence fallback has yet been ratified.

Do not interpret this as approval of:

* .yaml, .yml or .conf;
* prod, prd or stg;
* processName, catalog, common or another identifier;
* any directory or filename grammar;
* silent environment alias conversion;
* or any hard-coded dev behavior.

Direction 4 — Standalone transformation SQL: Decision 3C

A standalone executable .sql artifact may be discovered and preserved when it already exists, but the Extension must never create a new standalone .sql transformation artifact.

For new transformation artifacts, use the proven HOCON/YAML transformation-include contract.

Do not collapse standalone SQL and HOCON/YAML includes into one artifact family.

The ADR must determine whether “preserved” means:

* path-preserved only;
* content may be updated in place;
* or completely read-only and never content-modified.

If the evidence and accepted direction do not establish this detail, return it as a residual maintainer decision.

Required authority labels

Every ADR rule must use exactly one status:

* EVIDENCE_PROVEN
* MAINTAINER_DIRECTION_ACCEPTED
* DETAIL_PENDING_RATIFICATION
* LEGACY_OBSERVED_ONLY
* REJECTED

Do not present a maintainer decision as historical Framework evidence.

Do not present current runtime behavior as a normative rule unless a validator, deployment contract or deterministic product boundary enforces it.

Formal path-domain model

Define separate fields and invariants for at least:

1. repositoryRelativePath
    * workspace-relative artifact destination;
    * governed by destination containment and collision rules.
2. includeReferencePath
    * a reference stored inside a configuration document;
    * may contain controlled relative segments such as ../conf/...;
    * must be resolved against a defined base and proven contained;
    * must not be validated as though it were an artifact destination.
3. deploymentRoot
    * externally configured;
    * never guessed from a repository path, customer name or example.
4. deployedPath
    * produced by a versioned deployment projection;
    * under Direction 4A, preserves the complete repository-relative suffix beneath deploymentRoot.
5. registrationPath
    * derived from the actual deployedPath;
    * never independently supplied by onboarding, a renderer or the user.
6. layoutProfileId, deploymentProfileId and formula/provenance identity.

State the mandatory invariant:

registrationPath === actual deployedPath

after the applicable platform-aware normalization.

Onboarding may consume these values from the finalized manifest but must not calculate, override or independently request them.

Lifecycle matrix

For each relevant artifact family, provide an exact matrix covering:

* DISCOVER
* CREATE
* UPDATE
* REUSE
* DEPLOY
* REGISTER

Include at least:

* primary Job Config;
* split EXTRACT Job Config;
* split LOAD Job Config;
* Environment Config;
* transformation HOCON/YAML include;
* standalone transformation SQL;
* shared/common configuration;
* onboarding/registration record;
* declared tabular output;
* ETL managed-ownership marker.

For every cell state whether the operation is:

* supported;
* preserved;
* derived;
* externally owned;
* blocked;
* unsupported;
* or pending ratification.

Evidence-first resolver contract

Propose a deterministic, pure and fail-closed evidence-resolution policy.

It must define:

1. the exact workspace scope from which local evidence may be collected;
2. which real artifacts qualify as trusted evidence;
3. which examples, fixtures, generated samples, docs and unrelated workspaces are excluded;
4. how evidence maps to a recognized layout profile;
5. the definition of “unambiguous”;
6. behavior when multiple profiles are observed;
7. behavior when discovery is incomplete;
8. behavior when no evidence exists;
9. behavior when a discovered path is safe but unsupported;
10. stable error/result codes;
11. deterministic provenance and explanation output.

Requirements:

* no prevalence or majority voting;
* no “nearest convenient producer” selection;
* no structural question may be delegated to an ordinary Extension consumer;
* genuinely workload-specific values such as an explicitly selected target environment may be requested only after the structural policy is established;
* ambiguous evidence must remain a conflict, not a prompt to guess.

At minimum, evaluate codes equivalent to:

* AMBIGUOUS_LAYOUT_EVIDENCE
* INCOMPLETE_LAYOUT_DISCOVERY
* NO_LAYOUT_EVIDENCE
* FALLBACK_PROFILE_NOT_RATIFIED
* UNSUPPORTED_LAYOUT_PROFILE
* DEPLOYMENT_REGISTRATION_MISMATCH
* ARTIFACT_CREATE_NOT_SUPPORTED

Recommend final names but do not implement them.

Preserve the proven boundaries

The proposed ADR must retain these evidence-supported rules:

* Job Config UPDATE/reuse preserves the selected existing path verbatim.
* Environment Config UPDATE/reuse preserves the selected existing path verbatim.
* split EXTRACT/LOAD is currently coupled to _config.json; this is a legacy implementation coupling, not a future contract.
* transformation SQL and transformation HOCON/YAML include are distinct artifact kinds.
* the proven transformation include reference is ../sql/<module>.yaml, subject to the existing resolver contract.
* shared/common configurations are externally owned and referenced, never created by the Extension.
* ETL artifacts receive no Copilot managed-ownership marker.
* declared_tabular_output has no authoritative representation or path and remains excluded.
* artifact-destination traversal safety and include-reference resolution are separate validation domains.
* no existing artifact path is migrated during UPDATE without a separately approved migration feature.

Treat B7 and applicable parts of C2 as preservation/current-runtime compatibility contracts unless stronger authority is proven. Do not overstate them as universal Framework truth.

Residual ratification packet

Return the smallest exact packet of remaining decisions required before CREATE integration can be implemented.

At minimum evaluate:

1. zero-evidence Job Config fallback grammar;
2. canonical Job filename sanitizer;
3. split EXTRACT/LOAD directory and filename grammar;
4. whether split naming is role-based rather than suffix replacement;
5. scope of Job layout evidence within a repository;
6. zero-evidence Environment Config fallback grammar;
7. scope and precedence of Environment evidence;
8. fallback extension: .yaml, .yml or another allowed value;
9. environment vocabulary and alias handling, including prod, prd and stg;
10. Environment identifier semantics: processName, job ID, catalog or another explicit field;
11. treatment of an existing standalone .sql file’s content;
12. exact versioned 4A deployment projection;
13. disposition of the legacy fixed-template publisher;
14. migration and compatibility behavior for repositories containing mixed conventions.

For each residual decision include:

* exact question;
* 2–3 viable options;
* evidence for and against each option;
* safety impact;
* backward-compatibility impact;
* CREATE/UPDATE/REUSE/DEPLOY/REGISTER impact;
* recommendation only where the accepted direction or evidence supports one;
* what remains blocked.

Do not manufacture a recommendation from prevalence.

Negative requirements

The proposed ADR must explicitly prohibit:

* path migration during ordinary UPDATE;
* free-form onboarding path overrides;
* independent registration-path computation;
* creation of shared/common configurations;
* an ETL managed-ownership marker;
* invention of a declared-output path;
* creation of standalone transformation .sql;
* collapsing SQL and YAML/HOCON artifacts;
* applying destination-path rejection rules directly to include references;
* guessing environment aliases, identifiers, extensions or directories;
* silently retaining legacy publisher divergence under Direction 4A;
* asking ordinary consumers to choose Framework structure.

Compatibility and migration analysis

Report the impact of the accepted directions on:

* RepoWriter.generatePaths;
* ArtifactPatchPlanner;
* ArtifactGenerationPipeline;
* EnvConfigRenderer;
* BlueprintBuilder;
* IncludeFileRenderer;
* DbfsPublisher;
* onboarding generation;
* discovery and reuse services;
* validation and collision detection;
* Preview and Write parity.

Do not edit those producers.

Identify separately:

* behavior that can be delegated without additional product decisions;
* behavior blocked by residual ratification;
* behavior requiring an explicit legacy adapter;
* behavior requiring a future migration decision.

Testable acceptance invariants

Define exact future acceptance tests without writing them.

Include:

* deterministic evidence resolution under reordered inputs;
* conflict on mixed layout profiles;
* zero-evidence fail-closed behavior;
* UPDATE path preservation;
* separate destination and include-reference validation;
* platform-aware collision behavior;
* repository/deployment/registration projection fidelity;
* onboarding derivation from the finalized manifest;
* no standalone SQL creation;
* no shared-config creation;
* no ETL ownership marker;
* no duplicate destination;
* Preview/Validation/Write consuming the same frozen manifest.

Dependency-ordered implementation plan

Produce a future plan only; do not implement it.

Use approximately this dependency order:

1. formal path tuple and versioned projection contract;
2. pure evidence classifier and ambiguity handling;
3. UPDATE preservation and proven include/shared/no-marker/path-safety delegation;
4. canonical publisher/registration fidelity for Direction 4A;
5. Job CREATE integration only after fallback and split grammar ratification;
6. Environment CREATE integration only after fallback, vocabulary and identifier ratification;
7. standalone SQL 3C integration;
8. frozen Preview/Validation/Write manifest and collision integration;
9. independent audit;
10. only afterward package/VSIX and Consumer-workspace verification.

For every proposed slice provide:

* goal;
* prerequisites;
* exact candidate production files;
* candidate tests;
* prohibited scope;
* exit criteria;
* independent-audit requirement.

Do not authorize any slice merely by listing it.

Required output

Return:

1. repository identity and immutability proof;
2. proposed ADR title, status and scope;
3. evidence-to-direction traceability table;
4. authority-status ledger;
5. formal path-domain model;
6. lifecycle matrix;
7. evidence-first resolver decision table;
8. proven preservation rules;
9. residual ratification packet;
10. compatibility and migration matrix;
11. testable invariants;
12. dependency-ordered implementation plan;
13. explicit Full Slice-2 readiness verdict;
14. proof that no file, review card, Git/PR/CI, VSIX, Phase-H baseline, Consumer workspace or external system changed.

The ADR status must remain PROPOSED_PENDING_RATIFICATION. Do not claim it is accepted or implemented.

Do not write an ADR file and do not implement any slice after reporting.

End with exactly one:

* LOCAL_PHASE_A1B_PATH_POLICY_ADR_READY_FOR_RATIFICATION
* LOCAL_PHASE_A1B_PATH_POLICY_ADR_RESIDUAL_DETAILS_REQUIRED
* LOCAL_PHASE_A1B_PATH_POLICY_ADR_CONTRADICTION_FOUND
* LOCAL_PHASE_A1B_PATH_POLICY_ADR_BLOCKED
