TASK: LOCAL-PHASE-A1C-CORRECTED-PATH-POLICY-RATIFICATION-PACKET-20260813-01

MODE: STRICTLY READ-ONLY ANALYSIS AND DECISION-PACKET PREPARATION.

This is NOT an implementation task, NOT an ADR-write task, and NOT authorization to modify any repository, consumer workspace, review overlay, baseline, package, VSIX, CI system, or external system.

The immediately preceding independent re-audit completed with:

LOCAL_PHASE_A1B_PATH_POLICY_ADR_REAUDIT_PASS_WITH_CORRECTIONS_AND_RESIDUALS

The earlier candidate ADR was never written. Its authority labels, path model, residual decisions, and S1/S2/S3 readiness claims were materially corrected. Your task is to independently verify the corrected findings against live evidence and produce one precise, owner-routed ratification packet before any ADR file or implementation is authorized.

1. Absolute preservation rules

You MUST NOT:

* create, edit, delete, rename, format, save, generate, or overwrite any file;
* click or invoke Keep, Undo, Revert, Discard, Clean, Accept, Apply, or equivalent actions;
* alter any pending, untracked, modified, protected, or review-overlay file;
* stage, commit, push, pull, merge, rebase, reset, checkout, switch, stash, tag, or mutate any worktree;
* build, test, package, install, uninstall, replace, or regenerate the VSIX;
* regenerate Phase-H/evaluation baselines or snapshots;
* write an ADR under decisions or anywhere else;
* write to any consumer workspace, Databricks, ADF, DBFS, MSSQL, Confluence, Jira, PR, or CI surface;
* treat untracked/unaccepted Slice-1 files as established authority;
* ask an ordinary Extension consumer to choose a Framework structural convention.

Terminal commands may be used only when read-only and terminal-output-only. Do not redirect output to disk or create temporary files.

Preserve all user-owned work and sessions, especially:

* Implement bounded local-only ETL phase
* Independent audit for Slice 1
* Independent re-audit of Slice-1 repair

Do not interact with their Keep/Undo state.

2. Start/end immutability proof

Capture before analysis and again at completion:

* selected root, origin, branch and HEAD;
* complete worktree list;
* staged state;
* default porcelain inventory;
* porcelain with --untracked-files=all;
* the reconciled inventory:
    * 15 default porcelain entities;
    * 16 expanded pending files;
    * 17 hashed paths when the additional clean protected file is included;
* SHA256 of all 17 reconciled paths;
* candidate VSIX SHA256;
* installed Extension identifier/version;
* eval, decisions, protected-governance and review-overlay states.

Expected identity, to be verified rather than assumed:

* root: etl_framework_extension
* origin: https://github.com/TD-Universe/agentic_etl.git
* branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* staged: empty
* installed Extension: td-etl.databricks-etl-copilot-0.3.139
* eval: clean
* decisions: clean, with no ADR file
* Slice 2: not started

If identity, inventory, or hashes differ, stop substantive work and report the exact discrepancy. Do not repair it.

3. Evidence method

The prior reports and this prompt are routing aids, not authority. Re-inspect the live sources and selected consumer/CD evidence.

Use this precedence:

1. NORMATIVE_CONTRACT
2. CURRENT_RUNTIME_BEHAVIOR
3. LEGACY_COMPATIBILITY
4. CORROBORATING_CONSUMER_EVIDENCE
5. DOCUMENTATION_ONLY
6. EXAMPLE_OR_FIXTURE
7. MAINTAINER_DIRECTION_PROPOSED

Never decide by producer count, test count, prevalence, recency, proximity, or majority vote.

Evidence scope must be restricted to the explicitly selected workspace root. Exclude sibling workspace roots, fixtures, examples, Framework Best-Practices trees, generated previews and unaccepted review artifacts.

Git status is not an evidence-qualification predicate. A valid non-Git, untracked or modified consumer artifact may qualify when it is inside the selected consumer scope and parses correctly.

Unreadable, permission-denied, malformed, truncated or incompletely searched evidence must produce INCOMPLETE_LAYOUT_DISCOVERY, never “no evidence”.

4. Corrections requiring verification

Verify, correct or explicitly disprove each item with exact source citations and authority labels:

1. pyhocon==3.5.7 resolves nested includes relative to the including file. Repository layout is constrained by include topology; prior P10 was inverted.
2. Job CREATE and Environment CREATE are jointly constrained by cross-family include topology. No shipped combination has yet been proven topology-safe for every relevant edge.
3. Existing resolveIncludePath implementations are base-blind and family-blind. They must not be centralized as a “proven contract” without an explicit (base, family, reference) contract and reconciliation of all resolution surfaces.
4. The path model requires at least these ten distinct fields:
    * repositoryRelativePath
    * includeReferencePath
    * resolvedIncludeTargetRepositoryPath
    * deploymentRoot
    * projectedDeployedPath
    * actualDeployedPath
    * registrationPath
    * layoutProfileId, scoped by (artifactFamily, evidenceScope)
    * deploymentProfileId plus projectionVersion
    * formulaId / provenance
5. Planned projection and actual publisher receipt must remain distinct. Registration is derived only from a successful actual receipt. Partial publication produces no registration.
6. Registration fidelity uses typed provider-specific canonical-location equality, not raw-string equality.
7. Repository mirroring is supported by normative include topology, CD semantics, consumer evidence and an existing compile-check/test-run projection. The open issues are root ownership, typed components, casing, environment axes, version semantics, profile selection, receipt and canonical URI form.
8. The current DBFS publisher is hybrid marker-anchored/flattening, not simply “four fixed templates”, and can break include closure.
9. Evidence-first CREATE requires a versioned recognized-profile registry. Evidence may select only an already-ratified profile; it must not synthesize a sanitizer, extension, alias table, identifier rule or grammar.
10. Profiles are scoped by (artifactFamily, evidenceScope) and require a subsequent cross-family topology-consistency check.
11. Discovery completeness is an explicit injected attestation. Multi-root evidence isolation is mandatory.
12. Job UPDATE/REUSE preservation applies only to the selected discovered artifact. It must not be generalized to the complete patch plan, which may generate missing includes.
13. Shared/common configuration is currently planned and rejected downstream. Absence of successful output is not a permanent prohibition.
14. Standalone .sql creation exists today and Framework-owned evidence contains .sql includes. “Never create standalone SQL” is an explicit breaking product narrowing requiring characterization and human ratification.
15. Onboarding is incorrectly routed/classified as an include in current paths and is contested by consumer evidence. It requires a separate artifact-family decision.
16. Environment discovery has active defects, including prod reachability/vocabulary mismatch and unrooted multi-root globs.
17. Existing registration-preflight and production mirroring machinery must be cited rather than reported as nonexistent.
18. Manifest parity is defined through identity/version/content digest across process boundaries, not object-instance identity.
19. Include topology must be preserved before and after projection. A legacy adapter must preflight the complete closure and fail closed.
20. Resolve the candidate report’s internal S3c contradiction: P6/X6 correctly state that absence of a declared-output producer does not establish prohibition. Do not include declared tabular output in ARTIFACT_CREATE_NOT_SUPPORTED without an independent product decision.

5. Required in-chat output

Do not write any result to a file.

A. Corrected authority ledger

For every retained P/M/L/X claim provide:

* original claim;
* live finding;
* corrected authority/status;
* exact evidence;
* eligibility for a future ADR;
* classification as contract, runtime behavior, compatibility, latent defect, proposal, or unsupported absence inference.

Explicitly cover P1, P4, P6, P8, P10, shared config, standalone SQL, onboarding and the unaccepted Slice-1 normalizer.

B. Principle-ratification wording for D1–D4

Draft exact concise text labelled:

PROPOSED_PENDING_HUMAN_RATIFICATION

Requirements:

* D1: mirroring is supported by normative parser topology, CD contract, observed paths and an existing production projection.
* D2/D3: evidence-first and fail-closed through a versioned recognized-profile registry plus mandatory cross-family topology validation.
* D4: explicitly record that this is a breaking product narrowing, because the Extension creates standalone SQL today and the Framework itself contains SQL-include counterexamples.

State that principle ratification:

* does not select a concrete Job or Env grammar;
* does not authorize implementation;
* does not approve a legacy adapter;
* does not waive independent implementation audit.

Give each principle a RATIFY / REJECT / REVISE response slot.

C. Canonical R1–R20 decision ledger

For R1–R20 provide:

* exact question;
* owner:
    * POLICY_DETERMINABLE_NOW
    * MAINTAINER_PRODUCT_CHOICE
    * CD_OR_PLATFORM_OWNER
    * SEPARATE_FEATURE
    * MISSING_DECISION
* dependencies;
* mutually exclusive options;
* authoritative evidence for and against;
* topology, collision and safety impact;
* backward-compatibility impact;
* lifecycle impact;
* recommendation only where supported, otherwise NONE;
* interim fail-closed behavior;
* exactly what remains blocked.

Include and verify:

* R15: versioned recognized-profile registry, owner and versioning;
* R16: typed deployment-root components and ownership/case;
* R17: <version> and version_artifact semantics;
* R18: mandatory legacy-adapter include-closure preflight;
* R19: selected-root-only multi-root evidence isolation;
* R20: onboarding artifact-family separation.

Treat R4, R8, R18, R19 and R20 as policy-determinable proposals only if their derivation remains valid. Determinable does not mean ratified.

D. Separate owner decision forms

Produce two short forms:

1. Maintainer/product-owner form covering all applicable R1–R15, R18 and R20 decisions.
2. CD/platform-owner form covering:
    * R16 deployment-root component model and ownership;
    * uppercase/lowercase authority;
    * R17 version-segment semantics;
    * R9 environment vocabulary and envName versus enviro;
    * canonical dbfs:/, /dbfs/ or dbfs:/// representation;
    * publisher receipt and partial-failure contract;
    * complete include-closure preservation;
    * deployProjectName disambiguation.

Do not route either form to an ordinary consumer.

E. Corrected model and invariants

Restate the ten-field model and corrected INV-1 through INV-9, including:

* typed provider canonical equality;
* planned versus actual deployment;
* include versus destination validation domains;
* host versus provider collision domains;
* manifest digest/version parity;
* include-topology preservation;
* no registration after partial publication.

Use one primary layout-resolution outcome with evidence state and typed cause chain. Deployment errors remain separate from layout-resolution errors.

F. Atomic readiness matrix

Independently classify:

* S1a field/type separation
* S1b provider-specific path algebra
* S1c projection interface
* S1d receipt/actual/registration
* S2a result/error/provenance algebra
* S2b generic injected-registry classifier
* S2c production profile registry
* S3a artifact-only UPDATE preservation
* S3b corrected include resolver
* S3c creation-prohibition enforcement
* S3d onboarding-family separation
* S3e deployment/registration population
* S3f manifest digest/collision parity

For each, mark:

* ready after principle ratification;
* ready only with reduced scope;
* revision required;
* blocked by maintainer decisions;
* blocked by CD/platform decisions.

Do not repeat the falsified claim that S1, S2 and S3 are wholly decision-free.

G. Next authorization boundary

State exactly:

* what can be designed after principle ratification alone;
* what needs R1–R20 detail decisions;
* what needs external CD/platform evidence;
* what remains deferred;
* the smallest later independently auditable implementation slice.

Do not implement or scaffold it.

6. Final status

End with exactly one status:

LOCAL_PHASE_A1C_CORRECTED_RATIFICATION_PACKET_READY_AWAITING_OWNER_DECISIONS

or:

LOCAL_PHASE_A1C_RATIFICATION_PACKET_BLOCKED_BY_EVIDENCE_CONFLICT

Then provide the complete end-state immutability proof.

A READY result means only that the decision packet is coherent. It does not approve an ADR and does not authorize Slice 2.
