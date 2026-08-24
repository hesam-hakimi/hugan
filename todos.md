TASK: ASKTD_PHASE_2F_BOUNDED_READ_ONLY_DISCOVERY

You are performing one bounded, read-only discovery task for the existing AskTD / KMAI implementation.

This is not an implementation task.

Do not redesign the system, start Phase 2F coding, or make any repository or GitHub mutation.

1. Objective

Determine the smallest safe and evidence-backed Phase 2F scope for governed Approved Recipe dependency-lifecycle evaluation, building directly on the finalized Phase 2E implementation.

The candidate lifecycle vocabulary to investigate is:

* VALID
* REVIEW_REQUIRED
* BROKEN
* NOT_APPROVED

Do not assume these states, their precedence, persistence model, approval evidence, or transition rules are already approved.

Classify every conclusion as one of:

* CURRENT / IMPLEMENTED
* TECHNICALLY VALIDATED
* WORKING DECISION
* WORKING ASSUMPTION
* RECOMMENDED
* OPEN
* DEFERRED

The output must be a discovery report and recommendation only. Do not create an implementation prompt.

Current PR-workflow clarification

The owner has confirmed that each existing PR requires only one approval from an eligible person other than the PR author.

That approval is being handled separately.

Do not:

* reopen the PR approval-policy investigation;
* treat CODEOWNERS repair as part of Phase 2F;
* request reviewers;
* approve, mark ready, retarget, merge, or modify PRs #15, #16, or #17.

2. Required workspace gate

The required logical repository root is:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The accepted physical equivalent is:

/app1/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

Before reading any project file:

1. run pwd;
2. run pwd -P;
3. resolve the real path of the required logical root;
4. confirm that the current physical directory and required logical root resolve to the same directory.

If they are not aliases of the same permanent Phase 2E worktree, stop immediately.

Do not read or search:

* the stale primary checkout;
* branch asktd_v2;
* any sibling repository;
* ETL or UCA workspaces;
* /tmp worktrees.

Do not perform a recursive search from any parent directory.

3. Required Phase 2E identity

Verify read-only that:

* branch is phase2/governed-field-records;
* local HEAD is exactly:
    0430613e6a9f1680338d8fc099e7960e5d46cac2
* the worktree and index are clean;
* there are no commits beyond this finalized Phase 2E commit;
* remote phase2/governed-field-records resolves to the same SHA through read-only remote inspection;
* PR #17 base remains phase2/approved-recipe-pilot;
* PR #17 head remains phase2/governed-field-records;
* PR #17 head SHA remains the exact Phase 2E SHA;
* the Phase 2E committed 12-file digest remains:
    d24d75ddc9cd38f699aefbda7392292d7b0cb708d06416cbb53b846a293915be
* no Phase 2F branch, commit, push, worktree, or PR exists unexpectedly.

Record current PR states, but do not mutate them.

A Draft/review-state-only change is not candidate drift. A head-SHA, base, ancestry, committed-content, or unexpected Phase 2F implementation change is material drift.

Do not run git fetch, update local refs, switch branches, or authenticate/reconfigure GitHub.

If authenticated read-only GitHub access is unavailable, report exactly what could and could not be verified. Do not repair credentials.

4. Permitted external reports

Read these reports completely from the reports directory outside the repository:

1. ASKTD_PHASE_2E_F01_TARGETED_INDEPENDENT_REREVIEW_RERUN_2026-08-23.md
2. ASKTD_PHASE_2E_FINALIZATION_2026-08-23.md
3. ASKTD_PHASE_2E_PR_STACK_READINESS_2026-08-23.md

Treat the final committed code as authoritative for implementation details and use the reports only as evidence indexes and completion-state records.

Do not read:

* the procedurally failed targeted re-review report;
* unrelated reports;
* ETL or UCA reports;
* Library exports not explicitly listed here.

The PR-stack report’s CODEOWNERS observation remains a separate governance backlog item and is not a Phase 2F discovery blocker.

5. Repository evidence to inspect

Read the relevant files completely, including at minimum:

* docs/adr/0004-phase2d-approved-recipe-pilot.md
* docs/adr/0005-phase2e-governed-field-records.md
* docs/adr/README.md
* src/backend/app/available_data/registry_contract.py
* src/backend/app/available_data/field_evidence.py
* src/backend/app/recipes/approved_recipes.py
* src/backend/app/recipes/dependency_fingerprint.py
* every current production call site for:
    * Approved Recipe validation;
    * Governed Semantic Plan validation;
    * dependency resolution;
    * dependency fingerprinting;
    * authoritative builder resolution and invocation;
* all directly relevant Phase 2D and Phase 2E tests.

Search only within this repository root for existing lifecycle, approval, fingerprint, registry-version, recipe-version, provenance, and recipe-state concepts.

Do not infer behavior from names alone. Trace actual production call paths and test evidence.

6. Exact research questions

Answer every question with file, function, and line evidence.

A. Existing approval and lifecycle contract

1. What approval, lifecycle, enabled/disabled, version, and provenance attributes already exist on ApprovedRecipe or adjacent contracts?
2. Does the current single pilot recipe contain durable evidence of:
    * who or what approved it;
    * when it was approved;
    * which recipe version was approved;
    * which governed dependencies were approved?
3. Is any historical approved dependency fingerprint currently stored or compared?
4. Which current checks are deterministic contracts and which are only names, constants, or hard-coded assumptions?
5. Does any existing state already overlap with:
    * VALID;
    * REVIEW_REQUIRED;
    * BROKEN;
    * NOT_APPROVED?
6. Does the current APPROVED recipe state represent approval evidence, runtime validity, or both?

B. Current Phase 2E dependency behavior

1. Where is the current dependency fingerprint computed?
2. Which exact dataset and field attributes participate?
3. Which unrelated metadata edits are intentionally fingerprint-invariant?
4. Which referenced material changes alter the fingerprint?
5. Which missing, renamed, unknown, duplicated, or conflicting references fail closed?
6. At what exact point does validation occur relative to:
    * recipe resolution;
    * parameter validation;
    * registry/version resolution;
    * semantic-plan validation;
    * dependency resolution;
    * fingerprint computation;
    * builder resolution;
    * data-source creation;
    * schema probing;
    * SQL generation;
    * SQL execution?
7. Can a failed lifecycle or dependency decision be guaranteed to occur before all builder, I/O, and execution activity?

C. Approved baseline and self-blessing risk

Investigate how an immutable approved dependency fingerprint could be represented without allowing the runtime to calculate the current fingerprint and immediately treat that same value as approved.

This self-blessing scenario must explicitly fail:

current fingerprint → store as approved automatically → compare with itself → VALID

For every option, answer:

* What is the source of approval authority?
* When is the approved fingerprint captured?
* Is it immutable after approval?
* How is recipe-version identity represented?
* How is approval provenance represented?
* What happens when no approved baseline exists?
* What prevents silent automatic approval?
* What requires explicit reapproval?
* Can application startup or registry construction silently replace the approved baseline?
* Does the option require persistence, migration, API, UI, or workflow changes?

Do not decide that the approved baseline belongs inside ApprovedRecipe, a separate registry, or a persistent store before comparing the evidence-backed options.

D. Lifecycle semantics and precedence

Produce a proposed deterministic decision matrix covering at least:

* recipe has no valid approval evidence;
* recipe approval exists and all referenced entities resolve unchanged;
* approval exists but a referenced entity materially changes;
* approval exists but a referenced field is missing or renamed;
* approval exists but dependency records conflict;
* recipe definition changes without reapproval;
* recipe version changes without matching approval evidence;
* unrelated metadata changes;
* semantically equivalent reference reordering;
* feature flag OFF;
* malformed or unavailable registry evidence.

For each case, state:

* proposed lifecycle result;
* whether execution is allowed;
* whether builder resolution is allowed;
* whether reapproval is required;
* whether the result is a technical conclusion or an open policy decision.

Explicitly investigate precedence when multiple conditions apply, especially:

* NOT_APPROVED versus BROKEN;
* REVIEW_REQUIRED versus BROKEN;
* recipe-definition change versus dependency change;
* malformed evidence versus missing approval;
* unknown reference versus material fingerprint change.

Do not silently decide product or governance policy. Mark unresolved rules OPEN with an owner and confirmation requirement.

E. Separation of concerns

Confirm that lifecycle state:

* is not authorization;
* cannot grant dataset, field, row, or column access;
* is determined by deterministic code rather than an LLM;
* cannot bypass existing authorization or SQL policy;
* fails closed before builder, data-source, schema-probe, or SQL activity;
* does not expose physical-object details through new denial messages;
* does not treat descriptive metadata as permission evidence;
* does not change the existing denial-message backlog item;
* does not introduce relationship or graph semantics.

F. Feature-flag and rollback boundary

Determine the smallest safe feature-flag boundary for Phase 2F.

The recommendation must preserve exact Phase 2E behavior when the Phase 2F flag is absent or false.

Identify:

* proposed flag ownership and default;
* exact flag-off behavior;
* whether flag-off avoids reading approval-baseline evidence;
* whether existing Phase 2E traces remain byte-for-byte or semantically identical;
* rollback proof;
* tests required to prove no Phase 2E registry, fingerprint, recipe, authorization, or SQL behavior changes.

Do not enable any flag in an environment.

G. Options analysis

Compare at least these bounded alternatives without implementing them:

2F-A

Immutable approved dependency snapshot or fingerprint attached to the single pilot recipe.

2F-B

Separate deterministic in-process approval-record registry keyed by recipe ID and recipe version.

2F-C

Persistent approval/control-plane store and approval/reapproval workflow.

For each option provide:

* benefits;
* risks;
* source of approval authority;
* self-blessing protections;
* affected contracts;
* migration or persistence requirements;
* testability;
* rollback behavior;
* scalability;
* security implications;
* operational ownership;
* whether it is appropriate for Phase 2F or should be deferred.

Recommend one option only when repository evidence supports it.

Explain why the recommendation is the smallest safe continuation of Phase 2E and not a replacement architecture.

H. Proposed bounded implementation surface

Without editing anything, identify the exact likely file inventory for the recommended option:

* existing files likely requiring modification;
* files that might need creation;
* coupled test files;
* ADR additions or updates;
* files explicitly not requiring changes.

Explain why each proposed file belongs in scope.

Do not include speculative refactors or unrelated cleanup.

Do not create the files or prepare an implementation branch.

I. Acceptance criteria

Produce a precise acceptance matrix for a later implementation, including:

* exact approved-baseline match → VALID;
* missing approval evidence → deterministic fail-closed result;
* current fingerprint must never automatically become its own approved baseline;
* material referenced change → fingerprint change and non-executable state;
* missing or renamed reference → BROKEN or an explicitly identified open-policy result;
* unrelated metadata change → remains valid;
* reordered semantically equivalent dependencies → no false invalidation;
* genuine duplicate conflict → fail closed;
* recipe-definition or recipe-version change → explicit non-valid state until reapproval;
* feature flag OFF → exact Phase 2E compatibility;
* authorization-negative regressions;
* provider-neutrality regressions;
* golden baseline;
* no builder, data-source, schema-probe, or SQL activity for non-executable states;
* deterministic traces without sensitive metadata disclosure.

7. Scope exclusions

Do not implement, design in detail, or pull into Phase 2F:

* relationship emission;
* metadata, join, or lineage graphs;
* graph databases;
* additional Approved Recipe migration;
* Redis or distributed/query-result caching;
* Databricks, Genie, Unity Catalog, or Collibra integration;
* cross-source execution or joins;
* SQL-dialect compilation;
* new authorization engines;
* row/column authorization changes;
* frontend changes;
* deployment, Terraform, or runtime activation;
* Orchestrator decomposition;
* KPI, glossary, reporting, visualization, or output-template work;
* repair of the existing denial-message disclosure backlog;
* governed-dataset-reference versus emitted-table cross-check;
* CI/workflow changes;
* CODEOWNERS repair;
* PR #15/#16/#17 review, readiness, retarget, approval, or merge actions;
* Phase 2F branch/worktree creation;
* Phase 2F implementation.

Do not start Phase 2G or any later phase.

8. Validation conduct

This is read-only discovery.

You may run existing focused tests or process-local probes only when necessary to resolve an ambiguity, with:

* PYTHONDONTWRITEBYTECODE=1;
* pytest cache disabled;
* all coverage, JUnit, and temporary output directed outside the repository.

Do not:

* change tests;
* regenerate baselines;
* format files;
* run tools that rewrite files;
* create repository artifacts;
* stage files;
* commit;
* push;
* create or modify PRs;
* change Git configuration.

Record git status --porcelain and candidate identity before and after discovery.

9. Decision register

For every unresolved decision or assumption, record:

* decision or assumption;
* why it matters;
* current evidence;
* recommended owner;
* confirmation required;
* whether it blocks:
    * Core implementation;
    * runtime activation;
    * integration;
    * production;
    * or only a later phase.

Do not make enterprise architecture, product-policy, or approval-governance decisions on behalf of architects or owners.

10. Required report

Write exactly one persistent output outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2F_DISCOVERY_2026-08-24.md

The report must include:

1. final discovery verdict;
2. workspace, branch, SHA, remote, digest, and PR identity;
3. evidence read;
4. current implemented facts;
5. Phase 2E-to-2F gap analysis;
6. current production execution order;
7. lifecycle decision matrix;
8. approved-baseline and self-blessing analysis;
9. option comparison;
10. recommended bounded option;
11. exact proposed file inventory;
12. acceptance matrix;
13. security and authorization-separation proof;
14. feature-flag and rollback boundary;
15. scope exclusions;
16. decision register;
17. implementation preconditions;
18. exact recommended next action;
19. no-change attestation.

Do not place the report inside the Git repository.

Do not generate a Phase 2F implementation prompt during this task.

11. Terminal verdict

End the report and final response with exactly one applicable terminal token:

* PHASE_2F_DISCOVERY_COMPLETE
* PHASE_2F_DISCOVERY_BLOCKED_WRONG_WORKSPACE
* PHASE_2F_DISCOVERY_BLOCKED_PHASE2E_DRIFT
* PHASE_2F_DISCOVERY_BLOCKED_EVIDENCE
* PHASE_2F_DISCOVERY_BLOCKED_ENVIRONMENT

A COMPLETE verdict means only that discovery and recommendation are complete.

It does not authorize:

* Phase 2F implementation;
* branch or worktree creation;
* commit or push;
* PR changes;
* runtime activation;
* merging PRs;
* CODEOWNERS or workflow repair;
* Phase 2G.
