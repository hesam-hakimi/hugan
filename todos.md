TASK: PHASE_2F_OWNER_DECISION_PACKET_PREPARATION

Mode: bounded decision-document preparation only.
No Phase 2F implementation is authorized.

==================================================
1. WORKSPACE GATE
==================================================

Operate only from:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The corresponding physical path may be:

/app1/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

Accept the workspace only if realpath confirms that these identify the
same permanent Phase 2E worktree.

Expected identity:

Branch:
phase2/governed-field-records

HEAD:
0430613e6a9f1680338d8fc099e7960e5d46cac2

Expected state:
- clean worktree and index;
- zero commits beyond the finalized Phase 2E candidate;
- no unexpected Phase 2F branch, worktree, commit, or PR.

If the workspace, HEAD, or cleanliness does not match, stop without
reading unrelated files and report:

PHASE_2F_OWNER_PACKET_BLOCKED_IDENTITY_DRIFT

Do not inspect or use the stale primary checkout or branch asktd_v2.

==================================================
2. AUTHORITATIVE INPUT
==================================================

Read this report COMPLETELY:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2F_DISCOVERY_2026-08-24.md

Use it as the authoritative Phase 2F discovery baseline.

You may read the exact repository files cited by that report solely to
confirm names, fields, and current contracts. Do not perform a new broad
architecture discovery.

Do not read unrelated reports, sibling repositories, ETL/UCA workspaces,
Library exports, or the stale primary checkout.

==================================================
3. PURPOSE
==================================================

Create one concise owner-decision packet that allows the designated:

- Product owner;
- Data Governance owner;
- Architecture owner;
- recipe-governance authority;
- Platform/Security owner where applicable;

to explicitly approve, amend, reject, or defer the decisions required
before bounded Phase 2F implementation.

Do not make these decisions on their behalf.

The packet must clearly distinguish:

1. GitHub PR approval:
   one eligible non-author approval required for each PR;

2. recipe business/governance approval:
   the immutable approval evidence consumed by the proposed Phase 2F
   runtime comparison.

A GitHub PR approval must never be represented as recipe approval
provenance.

==================================================
4. BASELINE TO RECORD
==================================================

Record these as technically validated evidence, not approved business
baselines:

Phase 2E SHA:
0430613e6a9f1680338d8fc099e7960e5d46cac2

Phase 2E committed-content digest:
d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be

Pilot key:
("source_balance_mom_change", "1.0.0")

Current technically validated dependency fingerprint:
df-5018e97c00917aaa455c71b0c7ca7d42eac2ea01c0cab2b7449bd490559b425a

Label the fingerprint:

CANDIDATE TECHNICAL EVIDENCE — NOT AN APPROVED BASELINE

Never silently convert it into approved evidence.

==================================================
5. REQUIRED DECISION FORMS
==================================================

Create explicit decision forms for the following.

D-01 — Approval authority and provenance

Require owners to specify:

- recipe approval authority;
- approved_by or approval_authority representation;
- approval_reference format;
- approved_at requirements;
- whether any additional provenance is mandatory.

D-02 — Four-state semantics and precedence

Present the discovery recommendation for explicit approval or amendment:

1. Phase 2F flag OFF:
   emit no Phase 2F state and preserve exact Phase 2E behavior.

2. Missing or invalid exact approval evidence:
   NOT_APPROVED.

3. Valid approval exists but current governed truth cannot be resolved,
   including missing/renamed references or canonical conflicts:
   BROKEN.

4. Current recipe definition or dependency fingerprint differs while
   current governed truth remains resolvable:
   REVIEW_REQUIRED.

5. Exact approved recipe-definition fingerprint and exact approved
   dependency fingerprint:
   VALID.

Require an explicit owner decision for ambiguous multi-condition cases.

D-03 — Canonical recipe-definition fingerprint

Present the minimum recommended payload:

- recipe_id;
- recipe_version;
- normalized governed dataset references;
- normalized governed field references;
- normalized parameter definitions, domains, and allowed pairs;
- builder_key.

Require explicit decisions on:

- inclusion of lower-case lifecycle_status;
- inclusion of builder implementation identity or code digest;
- inclusion of output semantics;
- canonical ordering and normalization;
- version-bump requirements for execution-semantic changes.

Do not invent the final payload or fingerprint.

D-04 — Builder-change discipline

Require owners to decide whether a builder implementation or output
change:

- changes recipe_version;
- changes the approved recipe-definition fingerprint;
- requires both;
- or follows another explicitly documented rule.

D-05 — Initial pilot approval record

Create a decision template for the exact key:

("source_balance_mom_change", "1.0.0")

Required fields:

- recipe_id;
- recipe_version;
- approved_recipe_fingerprint:
  PENDING_OWNER_PAYLOAD_DECISION;
- approved_dependency_fingerprint:
  CANDIDATE_VALUE_REQUIRES_EXPLICIT_OWNER_ACCEPTANCE;
- approval_authority:
  PENDING;
- approval_reference:
  PENDING;
- approved_at:
  PENDING;
- decision:
  APPROVE / REJECT / DEFER / REQUEST_CHANGES;
- decision rationale;
- approver/sign-off.

Do not populate an approval timestamp, authority, recipe fingerprint, or
approval decision automatically.

D-06 — Architecture option

Request explicit acceptance, amendment, or rejection of:

2F-B — a separate frozen, source-controlled, in-process approval-record
registry keyed by exact (recipe_id, recipe_version).

Record that:

- runtime is a read-only consumer;
- no setter, writer, upsert, bootstrap, refresh, or auto-registration
  path is permitted;
- 2F-A is not recommended because of approval/definition co-location and
  self-blessing risk;
- 2F-C persistent control plane is deferred.

D-07 — Feature-flag interaction

Request explicit confirmation of behavior when:

APPROVED_RECIPE_DEPENDENCY_LIFECYCLE_ENABLED=true

but strict registry or governed field records are unavailable or false.

Present the recommendation:

fail closed as BROKEN; never downgrade to dataset-only approval.

D-08 — Trace and disclosure policy

Request confirmation that enabled traces may contain only:

- lifecycle state;
- safe internal reason code.

They must not expose:

- approval authority or approver identity;
- approved/current fingerprints;
- physical object names;
- governed dependency IDs;
- raw evidence;
- validation internals in the user-facing response.

D-09 — Separate GitHub control

Record as a working decision:

GitHub PR approval is separate from recipe approval evidence.

D-10 — Phase-name reconciliation

Ask Architecture to reconcile ADR 0004’s earlier Phase 2G wording with
the current bounded Phase 2F lifecycle slice.

D-11 — Implementation base

Record that Phase 2F implementation must not start until PR #15, #16,
and #17 are merged bottom-up and the resulting main SHA, ancestry, file
inventories, and Phase 2E digest are reverified.

==================================================
6. REQUIRED PACKET STRUCTURE
==================================================

The document must contain:

1. Purpose and authority boundary.
2. Technically validated evidence.
3. Recommended 2F-B summary.
4. Decisions requiring owner confirmation.
5. Initial pilot approval-record decision form.
6. State-precedence approval table.
7. Recipe-definition payload decision table.
8. Feature-flag and trace decisions.
9. Owner/sign-off matrix.
10. Explicit non-goals and deferred items.
11. Implementation blockers.
12. Exact effect of no decision:
    the safe pilot result remains NOT_APPROVED and implementation remains
    blocked.
13. One recommended next action:
    circulate the packet to the named owners and obtain explicit recorded
    decisions.

For every open item include:

- decision;
- why it matters;
- current evidence;
- recommended answer;
- owner;
- confirmation required;
- blocks Core implementation, runtime activation, integration,
  production, or only a later phase.

==================================================
7. PROHIBITED ACTIONS
==================================================

Do not:

- implement Phase 2F;
- create a Phase 2F branch or worktree;
- edit repository files;
- stage or commit;
- push;
- create, edit, approve, retarget, mark ready, or merge a PR;
- alter PR #15, #16, or #17;
- enable runtime flags;
- create approval evidence automatically;
- treat the current dependency fingerprint as approved;
- repair CODEOWNERS or workflows;
- start Phase 2G;
- introduce persistence, migrations, API, UI, Redis, graph, Databricks,
  Genie, Unity Catalog, Collibra, deployment, or Terraform work.

==================================================
8. OUTPUT
==================================================

Create exactly one new report outside the Git repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2F_OWNER_DECISION_PACKET_2026-08-24.md

Do not modify any existing report.

Before completion, reverify that the repository worktree remains clean
and that HEAD remains unchanged.

End with exactly one terminal marker:

PHASE_2F_OWNER_DECISION_PACKET_READY_FOR_OWNER_REVIEW

or:

PHASE_2F_OWNER_DECISION_PACKET_BLOCKED
