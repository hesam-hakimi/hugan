TASK: LOCAL-PHASE-A1D-OWNER-DECISION-CAPTURE-20260813-01

MODE: INTERACTIVE OWNER-DECISION CAPTURE — STRICTLY READ-ONLY.

Continue from the completed LOCAL PHASE A1C RATIFICATION PACKET.

The current status is:

LOCAL_PHASE_A1C_CORRECTED_RATIFICATION_PACKET_READY_AWAITING_OWNER_DECISIONS

This means only that the corrected decision packet is coherent. It does NOT mean:

* any principle or ADR has been ratified;
* any Job/Environment grammar has been selected;
* standalone SQL creation has been prohibited;
* Slice 2 or any implementation has been authorized;
* S1/S2/S3 may be implemented;
* any unresolved maintainer or CD/platform decision may be inferred.

Immutable preservation boundary

Preserve every existing Keep session and all pre-existing workspace changes, including:

* Implement bounded local-only ETL phase
* Independent audit for Slice 1
* Independent re-audit of Slice-1 repair

Do not invoke Keep, Undo, Revert, Discard, Delete, Clean, Reset, Checkout, Stash, Restore, or any equivalent action.

Do not:

* create, edit, delete, rename, format, save, stage or commit any file;
* write an ADR;
* modify source code, tests, fixtures, baselines, snapshots or generated context;
* run build, test, package, install, uninstall or VSIX replacement;
* start or scaffold Slice 2;
* mutate Git, PR, CI or worktrees;
* write to a consumer workspace, Databricks, ADF, DBFS, MSSQL, Confluence or Jira;
* treat unaccepted/untracked Slice‑1 material as production authority;
* ask an ordinary Extension consumer to choose a Framework structural convention.

This phase is decision capture only. Prefer no terminal commands; any command genuinely needed for clarification must be strictly read-only and must not redirect output to disk.

Authority rule

Do not answer any owner question yourself.

Do not convert:

* producer count,
* prevalence,
* current implementation,
* documentation,
* absence of a producer,
* a model recommendation,
* silence,
* or an unanswered checkbox

into approval.

Every unanswered item is DEFER and keeps its affected lifecycle stage fail-closed.

Step 1 — Identify the respondent

Ask exactly one question first:

“Which authority are you answering as?

A. Maintainer/Product Owner
B. CD/Platform Owner
C. Both authorities
D. Neither — prepare forwarding packets only”

Wait for the answer before proceeding.

Step 2 — Principle ratification

If the respondent has Maintainer/Product authority, present these principles individually and wait for one answer before moving to the next.

Allowed answers for each principle:

RATIFY | REJECT | REVISE: <exact replacement wording> | DEFER

D1 — Repository mirroring

Repository-relative ETL layout is projected to deployment by preserving the complete relative path beneath a typed, externally supplied deployment root. Ratifying D1 does not decide deployment-root ownership, component casing, environment axes, version semantics, URI spelling, receipt shape or legacy-adapter behavior.

D2/D3 — Evidence-first, fail-closed registry

CREATE layout selection may choose only an already-ratified profile from a versioned recognized-profile registry. Evidence must be restricted to the explicitly selected workspace root and scoped by (artifactFamily, evidenceScope). It must never synthesize a sanitizer, extension, alias table, identifier rule or path grammar. Incomplete discovery, no ratified match, ambiguity or cross-family include-topology failure blocks CREATE with a typed cause.

D4 — Standalone SQL narrowing classification

A rule that stops creation of standalone .sql artifacts is an intentional breaking product narrowing because standalone SQL is created by shipped behavior today. Ratifying D4 only ratifies this classification and the requirement for characterization tests plus a separate explicit product decision. It does not itself prohibit standalone SQL.

For every principle, show briefly:

1. the exact wording;
2. authority and strongest evidence;
3. compatibility/breaking consequence;
4. what it unlocks;
5. what remains unresolved.

Do not preselect an answer.

Step 3 — Maintainer/Product decisions

After the principles, ask the applicable D‑1 decisions one at a time. For each item:

* reproduce the mutually exclusive choices from the corrected packet;
* distinguish evidence from recommendation;
* state topology, collision, compatibility and lifecycle effects;
* state dependencies and what the answer unlocks;
* include DEFER;
* wait for the human answer.

Capture decisions for:

1. R1 — canonical Job Config formula;
2. R2 — canonical Job-name sanitizer;
3. R3 — canonical Environment Config formula, extension and environment segment;
4. R10 — shared/common configuration: creatable or reference-only;
5. R11 — standalone SQL: keep both, narrow to HOCON/YAML, narrow to SQL, or defer; any narrowing requires explicit breaking-change confirmation and characterization coverage;
6. R12 — UPDATE/REUSE preservation scope: selected discovered artifact only versus whole patch plan;
7. R14 — managed-ownership marker policy;
8. R15 — recognized-profile registry owner, versioning mechanism and initial profile-set authority;
9. R18 — mandatory fail-closed legacy include-closure preflight;
10. R20 — onboarding as a separate artifact family and its target grammar;
11. A‑20 — whether declared_tabular_output remains merely without an authoritative producer or becomes creation-prohibited through a separate product decision;
12. confirmation or objection that R4, R5, R6, R7, R8, R13 and R19 may be designed—but not implemented—as policy-determinable items after principle ratification.

Remember:

* absence of a producer is not a prohibition;
* Job and Environment choices are jointly constrained by include topology;
* the profile registry does not yet exist;
* onboarding is currently misrouted as an include;
* the current include resolvers are base-blind and family-blind;
* standalone SQL prohibition is a breaking removal, not a validation clarification.

Step 4 — CD/Platform-owner decisions

Only collect these answers from a respondent explicitly acting as CD/Platform Owner.

Otherwise mark every item EXTERNAL_OWNER_REQUIRED and produce a standalone forwarding packet without answering it.

Capture:

1. R16 — typed deployment-root components, source and owner of each component, including malcode, edpEnvironment, projectName, repositorySlug, conditional version, and any filePath prefix;
2. authoritative casing and whether lowercasing occurs;
3. R17 — <version> and version_artifact semantics;
4. R9 — complete environment vocabulary and the relationship between envName, enviro, edpEnvironment, dev, sit, pat, prod, prod_c2, prd and stg;
5. canonical provider URI representation and typed comparison rules for dbfs:/, dbfs:/// and /dbfs/;
6. authoritative publisher receipt and partial-failure semantics, including whether registration is allowed after partial publication;
7. confirmation that <filePath> preserves the complete nested repository-relative include closure without flattening;
8. deployProjectName, projectName, applicationName and path-segment disambiguation.

Do not infer these answers from current code, examples, observed casing or majority usage.

Step 5 — Decision ledger

After each answered item, append an in-chat ledger row containing:

* decision ID;
* authority/owner;
* exact human answer;
* status: RATIFIED, REJECTED, REVISED or DEFERRED;
* evidence versus human direction;
* dependencies satisfied;
* remaining blockers;
* affected lifecycle stages;
* breaking/backward-compatibility note.

Do not write the ledger to a file.

Completion output

When the interview is paused or completed, return:

1. ratified/rejected/revised/deferred principles;
2. completed Maintainer/Product decisions;
3. outstanding Maintainer/Product decisions;
4. completed CD/Platform decisions;
5. outstanding EXTERNAL_OWNER_REQUIRED decisions;
6. corrected hard-prerequisite graph;
7. atomic readiness classification, explicitly separating:
    * ready after principle ratification,
    * ready only with reduced scope,
    * revision required,
    * blocked;
8. the smallest possible future implementation slice—but label it DESCRIBED_ONLY_NOT_AUTHORIZED;
9. confirmation that all Keep sessions and workspace state remain untouched.

Use one of these final statuses:

* LOCAL_PHASE_A1D_OWNER_DECISIONS_PARTIAL
* LOCAL_PHASE_A1D_AWAITING_CDP_OWNER_DECISIONS
* LOCAL_PHASE_A1D_OWNER_DECISIONS_CAPTURED_READY_FOR_ADR_DRAFT

Even the last status does not authorize an ADR write or implementation. Stop and wait for a separate explicit request.
