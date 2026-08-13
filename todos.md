TASK: LOCAL-PHASE-A1B-PATH-POLICY-ADR-INDEPENDENT-REAUDIT-20260813-01

The complete prior ADR-proposal response, if supplied above this task, is a CHAT-ONLY, UNTRUSTED CANDIDATE. No ADR file exists. Do not inherit its conclusions, labels, counts, citations, readiness claims, or recommendations. Independently re-derive everything from the live repositories, HEAD, worktree, call graphs, validators, deployment code, consumer evidence, and current review-card state.

EXPECTED REPOSITORY IDENTITY — VERIFY, DO NOT ASSUME

* Selected repository: etl_framework_extension
* Expected origin: https://github.com/TD-Universe/agentic_etl.git
* Expected branch: feature/v3-agentic-redesign
* Expected HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* Existing combined review card: 11 modified + 4 untracked entries, including an unaccepted nine-file AOR overlay.
* Slice-1/protected hash counts have previously been reported as both 15 and 16. Reconcile the exact protected-file inventory and count from first principles.
* Phase-H baseline staleness is a separate pre-existing governance blocker.
* Installed extension was previously reported as td-etl.databricks-etl-copilot-0.3.139. Verify without modifying it.

If any expected identity differs, report the exact difference and use the live state as authority. Do not silently continue across a repository, branch, HEAD, worktree, or manifest mismatch.

MODE: STRICTLY READ-ONLY, INDEPENDENT, ADVERSARIAL, REPORT-ONLY

Allowed:

* Read-only filesystem inspection.
* Git metadata/status/diff/log reads.
* Source, documentation, test and call-graph inspection.
* Hashing and deterministic read-only analysis.

Forbidden:

* No file creation, editing, deletion, rename, formatting, save or temporary artifact.
* Do not click Keep or Undo.
* No Git stage, commit, push, merge, rebase, reset, checkout, branch switch, stash or worktree mutation.
* No build, test execution that writes artifacts, package, install, uninstall or VSIX replacement.
* No baseline or snapshot regeneration.
* No Slice-2 design in code, scaffolding or implementation.
* No PR, CI, consumer-workspace, Databricks, ADF, DBFS, MSSQL, Confluence or Jira mutation.
* Do not write an ADR file or modify the decisions directory.

The objective is to try to falsify the candidate ADR and reduce it to the smallest defensible policy, residual-decision packet and implementation-independent sub-scopes.

AUTHORITY HIERARCHY

Use, highest first:

1. NORMATIVE_CONTRACT: behavior actually enforced by the Framework, deployment platform or deterministic validator.
2. CURRENT_RUNTIME_BEHAVIOR: production source behavior that does not establish a universal convention.
3. LEGACY_COMPATIBILITY: explicitly superseded/deprecated behavior.
4. CORROBORATING_CONSUMER_EVIDENCE: structural corroboration only.
5. DOCUMENTATION_ONLY.
6. EXAMPLE_OR_FIXTURE.

Separately label accepted maintainer directions as MAINTAINER_DIRECTION_ACCEPTED. They are not EVIDENCE_PROVEN.

Never select a convention by producer count, file count, test count, prevalence, recency, path proximity or majority voting. Producer uniqueness is not normative authority. Absence of a producer is not, by itself, proof of a permanent product prohibition.

CANDIDATE POLICY SNAPSHOT TO AUDIT

The untrusted proposal claims:

D1. Canonical development deployment mirrors the complete repositoryRelativePath beneath an externally supplied deploymentRoot; registrationPath derives from the actual deployed location. Legacy fixed-template publishing must be explicit, versioned and fail-closed.

D2. Job Config CREATE uses evidence-first layout resolution; ambiguity or no ratified fallback blocks. UPDATE/REUSE preserves discovered paths verbatim.

D3. Environment Config CREATE uses evidence-first layout resolution; ambiguity, incomplete evidence or no ratified fallback blocks. UPDATE/REUSE preserves directory, filename, environment segment and extension verbatim.

D4. Existing standalone .sql transformations may be discovered and path-preserved but new standalone .sql artifacts are never created; new transformation artifacts use the HOCON/YAML include family.

The proposal also claims that S1, S2 and S3 form a decision-free implementation sub-scope after principle ratification. Treat this readiness claim as a primary falsification target.

The proposal lists residual decisions:

* R1: zero-evidence Job Config fallback.
* R2: canonical Job filename sanitizer.
* R3: split EXTRACT/LOAD directory and filename grammar.
* R4: first-class EXTRACT/LOAD role versus suffix replacement.
* R5: Job evidence scope.
* R6: zero-evidence Environment Config fallback.
* R7: Environment evidence scope and precedence.
* R8: fallback extension or blocking on incomplete extension evidence.
* R9: environment vocabulary and aliases such as prod/prd/stg.
* R10: Environment identifier semantics.
* R11: content mutability of an existing standalone .sql file.
* R12: exact versioned deployment projection and deploymentRoot supply.
* R13: disposition of the legacy fixed-template publisher.
* R14: mixed-convention repositories.

AUDIT A — IDENTITY AND IMMUTABILITY

Capture at start and end:

* root, origin, branch, HEAD and worktree list;
* staged state;
* exact dirty/untracked manifest;
* exact protected/Slice-1 file inventory and SHA256 values;
* review-card state;
* candidate VSIX hash and installed extension version;
* eval baseline state;
* decisions-directory state.

Explicitly reconcile why earlier reports used both 15 and 16 protected hashes. Do not merely repeat either number. End state must be byte-identical to start state.

AUDIT B — AUTHORITY LEDGER

Independently audit every candidate category:

* P1–P10 EVIDENCE_PROVEN
* M1–M11 MAINTAINER_DIRECTION_ACCEPTED
* L1–L7 LEGACY_OBSERVED_ONLY
* X1–X13 REJECTED

For every rule return:

* exact source citation and call path;
* actual authority tier;
* lifecycle and artifact-family applicability;
* whether it establishes a universal Framework rule, Extension-local runtime behavior, preservation compatibility, documentation, example evidence or no rule;
* corrected label if the candidate label is too strong.

Explicitly test these possible overclaims:

* Unaccepted Slice-1/review-card code must not be promoted to an established product contract.
* Single-producer onboarding behavior does not automatically become normative.
* Lack of a shared-config, declared-output, standalone-SQL or marker producer does not alone prove a permanent product prohibition.
* B7/C2 include behavior may be Extension-local preservation/current-runtime compatibility rather than universal ETL Framework truth.
* A job-onboarding path may be current behavior without being an authoritative repository grammar.

AUDIT C — FORMAL PATH DOMAINS

Determine whether the model must distinguish at least:

* repositoryRelativePath
* includeReferencePath
* resolvedIncludeTargetRepositoryPath
* deploymentRoot
* projectedDeployedPath
* actualDeployedPath or a typed successful publisher receipt
* registrationPath
* layoutProfileId, potentially scoped by artifact family and evidence scope
* deploymentProfileId and projectionVersion
* formulaId/provenance

Do not assume a planned projected path equals the actual published path.

Specify:

* which field exists at plan, preview, validation, write, successful publish and registration time;
* the authority that creates each value;
* failure and atomicity behavior;
* whether registration derives only from a successful publisher receipt;
* whether equality is raw-string equality or typed canonical-location equality;
* the exact path/URI semantic domain of each field.

Keep these semantic domains separate:

* repository filesystem paths and workspace containment;
* include-reference grammar and post-resolution containment;
* DBFS/deployment URI semantics;
* registration serialization;
* host win32/posix collision semantics.

Do not apply host filesystem normalization to DBFS or URI paths without evidence. Audit scheme handling, encoding, separator rules, trailing slash, containment and root joining. Determine whether deploymentRoot can safely be opaque or needs a typed provider-specific contract.

Replace any cross-process requirement for “the same object instance” with an evidence-backed manifest identity, version or digest contract if object identity is not operationally valid.

AUDIT D — INCLUDE TOPOLOGY

Trace and model the relative-reference graph for at least:

* ../sql/.yaml
* ../conf/{common_config|spark_config|etl_config|cluster_config}.yaml
* conf/**
* sql/**
* all candidate Job Config layouts
* all candidate Environment Config layouts
* the four current fixed DBFS publisher templates
* the proposed repository-mirroring projection

For each case determine:

* path of the including artifact;
* repository target after resolution;
* projected deployed source and target;
* whether the reference resolves to the same target after deployment;
* whether CREATE is supported, preservation-only, ambiguous or unsafe.

Do not declare HOCON/YAML include CREATE independent of Job/Environment layout unless the complete relative topology is proven.

An explicit legacy profile is not sufficient by itself. Determine whether any legacy adapter must preflight the entire include closure and registration fidelity and fail closed if flattening or re-rooting changes topology.

AUDIT E — EVIDENCE-FIRST RESOLVER

Audit whether a usable resolver requires a versioned registry defining, per recognized profile:

* artifact family;
* evidence scope;
* directory grammar;
* filename grammar;
* sanitizer/canonicalizer ID and version;
* environment-token parameterization;
* identifier-source rule;
* extension set;
* include topology;
* compatibility/version metadata.

Evidence may select an already ratified profile. It must not synthesize a sanitizer, alias table or future naming transformation from a few observed filenames.

Challenge the candidate phrase “real, committed artifacts.” Independently define how to handle:

* valid tracked and committed files;
* valid tracked but modified files;
* valid untracked consumer files;
* non-Git consumer workspaces;
* generated previews;
* unaccepted review-card files;
* fixtures/examples/docs;
* unreadable or malformed files;
* ignored files;
* symlinks and containment;
* permission failures;
* multi-root workspaces.

Do not permit an unreadable or unsearched region to become false NO_LAYOUT_EVIDENCE. Determine whether discovery completeness must be an explicit attested input to a pure classifier.

Audit whether one global layoutProfileId is sufficient or profiles must be artifact-family and scope specific.

Audit result-code structure. In particular, determine whether NO_LAYOUT_EVIDENCE followed by FALLBACK_PROFILE_NOT_RATIFIED should be two sequential results or one primary result with an evidence-state/cause chain.

AUDIT F — R1–R14 DEPENDENCY AND OWNERSHIP

For every residual decision provide:

* exact question;
* options still genuinely open;
* existing evidence and accepted-direction constraints;
* dependencies on other residuals;
* affected lifecycles and components;
* safe interim behavior;
* required decision owner;
* whether the candidate recommendation is justified.

Use one of:

* POLICY_DETERMINABLE_NOW
* REQUIRES_MAINTAINER_PRODUCT_CHOICE
* REQUIRES_DEPLOYMENT_OR_CD_OWNER_EVIDENCE
* DEFER_AS_SEPARATE_FEATURE
* MISSING_DECISION

Verify or correct these dependency groups:

* Job CREATE: R1–R5.
* Environment CREATE: R6–R10.
* Standalone SQL update/content policy: R11.
* Deployment and registration: R12–R13, plus R9 if environment vocabulary affects projection.
* Mixed-convention CREATE behavior: R14, scoped per artifact family/evidence scope.

Explicitly assess these candidate safe constraints without assuming their acceptance:

* zero-evidence Job/Environment CREATE blocks until a ratified fallback exists;
* EXTRACT/LOAD role is a first-class typed input, not suffix substitution;
* incomplete extension evidence blocks rather than choosing .yaml or .yml;
* no implicit common identifier fallback;
* mixed recognized profiles block CREATE while UPDATE/REUSE preserves existing paths;
* legacy publisher is never an automatic fallback;
* existing standalone SQL content is read-only unless separately approved.

Correct the final hard-prerequisite list. Do not omit R4/R5/R7/R8/R13 merely because another summary omitted them.

AUDIT G — ATOMIC S1/S2/S3 READINESS

Do not issue one verdict for a broad slice. Audit separately:

S1a. Pure field/type separation with no concrete path behavior.
S1b. Provider-specific repository/include/deployment path algebra.
S1c. Versioned deployment-projection interface.
S1d. Successful publisher receipt, actual deployed location and registration derivation.

S2a. Pure result/error/provenance algebra.
S2b. Generic deterministic classifier accepting an injected profile registry, explicit evidence scope and explicit discovery-completeness state.
S2c. Production recognized-profile registry and real Job/Environment classification.

S3a. Job and Environment UPDATE/REUSE path preservation only.
S3b. Duplicate include-resolver centralization and domain separation.
S3c. Creation-prohibition enforcement for unsupported families.
S3d. Onboarding record shape.
S3e. Populated deployed/registration fields and publisher-receipt derivation.
S3f. Frozen-manifest identity/digest and collision parity.

For each atomic scope return exactly one:

* READY
* READY_WITH_REDUCED_SCOPE
* REVISION_REQUIRED
* BLOCKED

Also give:

* remaining decision dependencies;
* exact behavior permitted;
* behavior explicitly prohibited;
* candidate production files;
* candidate tests;
* whether independent audit would be required.

A generic type or result algebra may be ready while a concrete projection or recognized profile is blocked. Do not call S2 ready if it hard-codes unratified profiles. Do not call onboarding registration ready if it depends on R12.

AUDIT H — DEPLOYMENT/REGISTRATION GAP

Independently locate every current configuration source contributing to DBFS/deployment paths.

Determine:

* whether any deploymentRoot configuration surface exists;
* whether current malcode, repositoryName, project segment, environment or version components are configured or inferred;
* who owns their authoritative values;
* the exact questions that must be answered by the CD/platform owner;
* whether deploymentRoot should be one resolved external value or multiple externally supplied typed components;
* how projectionVersion and deploymentProfileId are selected;
* what constitutes the actual deployed-location receipt;
* how onboarding/ADF registration consumes it;
* what happens when publishing partially fails.

The accepted direction forbids guessing deploymentRoot from repository path, customer name, malcode inference, examples or prevalence. A missing value must fail closed.

AUDIT I — TEST AND COMPATIBILITY MODEL

Review T1–T19 and the compatibility matrix.

Correct or add tests for:

* recognized-profile registry versioning;
* explicit discovery-completeness input;
* non-Git and uncommitted consumer evidence;
* malformed/unreadable evidence;
* multi-root and scope isolation;
* family-scoped mixed conventions;
* repository filesystem versus DBFS/URI normalization;
* planned versus actual deployment paths;
* successful receipt and failed/partial publish;
* typed registration equivalence;
* deployed include-graph preservation;
* unsafe legacy topology blocking;
* manifest digest/version parity across processes;
* hash-inventory reconciliation.

No test is to be executed or written in this task.

REQUIRED REPORT

Return, in order:

1. Repository identity and start-state proof.
2. Independent authority ledger with corrected labels.
3. Candidate-ADR issues ranked CRITICAL/HIGH/MEDIUM/LOW.
4. Corrected formal path-domain model and lifecycle timing.
5. Include-topology audit.
6. Evidence-resolver contract and completeness model.
7. Corrected R1–R14 dependency/ownership table, including any missing R15+ decisions.
8. Atomic S1/S2/S3 readiness matrix.
9. Corrected compatibility and test-invariant deltas.
10. Minimal maintainer decision packet.
11. Minimal external CD/platform-owner decision packet.
12. Principle-ratification verdict.
13. Full Slice-2 readiness verdict.
14. End-state immutability proof and exact start/end comparison.

Do not manufacture a recommendation when evidence and accepted direction do not resolve a choice. Clearly distinguish:

* principle ratification;
* detail ratification;
* implementation authorization;
* independent implementation audit.

No ordinary Extension consumer may be asked to select a Framework structural convention.

FINAL VERDICT

End with exactly one token and nothing after it:

LOCAL_PHASE_A1B_PATH_POLICY_ADR_REAUDIT_PASS_READY_FOR_PRINCIPLE_RATIFICATION

LOCAL_PHASE_A1B_PATH_POLICY_ADR_REAUDIT_PASS_WITH_CORRECTIONS_AND_RESIDUALS

LOCAL_PHASE_A1B_PATH_POLICY_ADR_REAUDIT_FAIL

LOCAL_PHASE_A1B_PATH_POLICY_ADR_REAUDIT_INCONCLUSIVE

LOCAL_PHASE_A1B_PATH_POLICY_ADR_REAUDIT_BLOCKED
