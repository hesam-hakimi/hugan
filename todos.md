TASK: PHASE_2F1_TARGET_COLLISION_READ_ONLY_REVIEW

Perform one independent, strictly read-only owner review of the pre-existing
Phase 2F.1 target branch, worktree, and its three uncommitted paths.

Do not implement, complete, repair, format, test, stage, commit, move, delete,
reset, stash, clean, restore, rename, push, or open a PR.

The purpose is to determine whether the three pre-existing changes are a safe,
scope-aligned partial Phase 2F.1 implementation that can be explicitly adopted,
or whether they are unrelated, ambiguous, or unsafe.

==================================================
1. REQUIRED REPORTS
==================================================

Read these reports completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_DISCOVERY_2026-08-26.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_2026-08-27.md

The discovery report must end with:

PHASE_2F1_DISCOVERY_COMPLETE

The blocked implementation report must end with:

PHASE_2F1_IMPLEMENTATION_BLOCKED_TARGET_COLLISION

Use the discovery report as the authoritative Phase 2F.1 contract.

Do not modify either report.

==================================================
2. EXPECTED SOURCE AND TARGET IDENTITIES
==================================================

Clean Phase 2E source application root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

Target worktree Git root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Target application root:

/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

Target branch:

phase2/recipe-lifecycle-classification

Expected target HEAD:

f283f01b6d615f9fa00debcef959d9c5c86a3224

Expected target tree:

6448dac5be9dee275598e054f505517a215b484b

Expected pre-existing porcelain paths:

 M kmai-td-genie/src/backend/app/recipes/approved_recipes.py
?? kmai-td-genie/src/backend/app/recipes/approval_evidence.py
?? kmai-td-genie/src/backend/app/recipes/lifecycle.py

The equivalent `/app1` paths are acceptable only when `realpath` proves
identity.

==================================================
3. IDENTITY AND STATE VERIFICATION
==================================================

Read-only verify:

- `pwd` and `pwd -P`;
- logical and physical target paths;
- Git top-level and common directory;
- origin;
- branch;
- HEAD and tree;
- upstream configuration, if any;
- `git worktree list --porcelain`;
- `git status --porcelain=v2 --untracked-files=all`;
- unstaged changed paths;
- staged changed paths;
- untracked paths;
- whether any additional ignored or unexpected implementation artifact exists.

Confirm independently that the permanent Phase 2E source remains completely
clean and unchanged.

Do not fetch, pull, switch branches, update refs, or modify Git configuration.

==================================================
4. FREEZE READ-ONLY COLLISION EVIDENCE
==================================================

For each of the three pre-existing paths, record without modification:

- exact path;
- tracked/untracked state;
- file type;
- size;
- line count;
- modification timestamp;
- SHA-256;
- whether it is a regular file or symlink;
- staged versus unstaged state.

Record the complete diff for `approved_recipes.py`.

Read both untracked modules completely.

Do not open, inspect, or read unrelated dirty content because none is expected.

Do not inspect shell history, credentials, unrelated user files, or unrelated
VS Code state.

==================================================
5. BOUNDED PROVENANCE REVIEW
==================================================

Use only scoped read-only evidence:

- branch reflog for `phase2/recipe-lifecycle-classification`;
- worktree administrative identity;
- HEAD reflog for the target worktree, if available;
- branch creation/reflog timestamps;
- file metadata timestamps;
- local and authenticated read-only GitHub checks for whether this branch,
  commit, PR, or remote ref already exists.

Determine:

1. When the local branch/worktree appears to have been created.
2. Whether the target has ever moved away from the accepted base.
3. Whether any implementation commit exists locally or remotely.
4. Whether any PR exists for this branch.
5. Whether evidence suggests an interrupted earlier Phase 2F.1 attempt.
6. Whether another active or remote owner appears to control these changes.

Do not claim provenance that cannot be proven. Clearly distinguish verified
facts from inference.

==================================================
6. CONTENT REVIEW AGAINST THE DISCOVERY CONTRACT
==================================================

Treat the three files as untrusted candidate content.

Review them completely against the authoritative discovery report.

For `lifecycle.py`, determine whether it correctly and exclusively implements:

- `LifecycleState`;
- `LifecycleReasonCode`;
- frozen evidence/resolution/result dataclasses;
- fixed precedence;
- all required reason codes;
- pure `evaluate_recipe_lifecycle`;
- deterministic sorting and deduplication;
- all-reasons behavior;
- fail-closed handling;
- exact trace serialization;
- no environment, time, random, I/O, provider, registry, database, network,
  SQL, logger, tracer, cache, queue, or persistence dependency.

For `approval_evidence.py`, determine whether it correctly and exclusively
implements:

- `ApprovalEvidenceProvider` as `@runtime_checkable Protocol`;
- `ApprovedRecipeApprovalEvidenceProvider`;
- current ApprovedRecipe lookup behavior;
- immutable accepted per-reference fingerprints;
- zero/one initial evidence behavior;
- missing/invalid baseline behavior;
- no runtime recomputation of the approved baseline;
- no provider, database, network, SQL, Synapse, Databricks, Data Lake, proxy,
  or data-source access.

For the `approved_recipes.py` diff, determine whether it correctly and
exclusively adds:

- `RECIPE_LIFECYCLE_CLASSIFICATION_ENABLED`;
- strict default-OFF parsing;
- `recipe_lifecycle_classification_enabled()`;
- `evaluate_recipe_lifecycle_gate(...)`;
- return-before-lookup behavior when disabled;
- orchestration-side evidence resolution;
- classification-only behavior;
- no modification to existing `ApprovedRecipe` fields;
- no change to the existing Approved Recipe execution gate.

Check:

- imports and module boundaries;
- public `__all__` symbols;
- fingerprint syntax and structural validity;
- duplicate/conflict behavior;
- missing or unfinished code;
- TODOs, placeholders, stubs, ellipses, debug code, generated prose, secrets,
  credentials, absolute paths, SQL, raw evidence, or suspicious content;
- consistency among the three files;
- compatibility with the existing Phase 2E APIs.

Do not execute or import the candidate code.

==================================================
7. REQUIRED GAP ANALYSIS
==================================================

Compare the existing three-path candidate with the exact ten-file authorized
plan.

Identify:

- which required work is already present;
- which parts are partially present;
- which parts are incorrect;
- which parts require repair;
- which seven expected files remain untouched;
- whether any existing candidate code exceeds Phase 2F.1 scope;
- whether adopting it would be safer than discarding it;
- whether every byte can be reviewed and corrected without trusting its
  unknown provenance.

Do not treat unknown authorship alone as unsafe if the content is fully
inspectable, contains no secrets, is confined to Phase 2F.1, and can be treated
as an untrusted candidate during the later implementation.

==================================================
8. DISPOSITION RULES
==================================================

Select exactly one verdict.

A. SAFE_TO_ADOPT

Use only if all are true:

- target branch/worktree identity is exact;
- target HEAD never left the accepted base;
- there are exactly the three expected dirty paths;
- nothing is staged;
- no remote commit or PR owns the changes;
- all three files are exclusively Phase 2F.1-related;
- no secret, destructive behavior, unrelated change, data access, persistence,
  runtime enforcement, or scope expansion exists;
- the content is sufficiently reviewable to preserve as an untrusted partial
  candidate;
- any defects can be corrected within the existing authorized ten-file scope.

B. OWNER_DECISION_REQUIRED

Use if the content appears Phase 2F.1-related but ownership, external activity,
or safe disposition remains materially ambiguous.

C. UNRELATED_OR_UNSAFE

Use if any change is unrelated, destructive, secret-bearing, outside scope,
externally owned, or unsafe to adopt.

D. BLOCKED

Use only if the required files or evidence cannot be read.

Do not mutate the target regardless of verdict.

==================================================
9. NO MUTATION
==================================================

Do not:

- edit any repository file;
- create, delete, move, copy, rename, restore, or overwrite a repository file;
- stage, unstage, commit, amend, reset, stash, clean, checkout, switch, merge,
  rebase, cherry-pick, or update a ref;
- create/remove/move a branch or worktree;
- run tests, coverage, application imports, formatter, linter or type checker;
- install a package;
- create a backup inside or outside the repository;
- push or create/edit a PR, issue, comment, label, review, workflow or release;
- enable a runtime flag;
- query any business data.

The only authorized write is the single review report outside the repository.

==================================================
10. REPORT
==================================================

Write exactly one report:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_TARGET_COLLISION_REVIEW_2026-08-27.md

Include:

1. final disposition;
2. source and target identity;
3. exact porcelain/staged/untracked evidence;
4. branch/worktree/reflog provenance evidence;
5. local and remote branch/commit/PR evidence;
6. file metadata and SHA-256 table;
7. complete findings for each of the three files;
8. discovery-contract compliance matrix;
9. security and no-scan assessment;
10. detected defects, placeholders and gaps;
11. exact comparison with the ten-file plan;
12. verified facts versus provenance inferences;
13. adoption safety analysis;
14. whether the candidate may be preserved and corrected;
15. exact next permitted action;
16. repository/GitHub no-mutation attestation.

If the verdict is SAFE_TO_ADOPT, the next action must be a separately
authorized continuation that:

- explicitly adopts the three files as untrusted partial candidate content;
- preserves them initially;
- independently reviews and corrects them;
- completes only the remaining authorized ten-file plan;
- runs all Phase 2F.1 validation gates;
- creates one local commit only after all gates pass.

End with exactly one token:

PHASE_2F1_TARGET_COLLISION_REVIEW_SAFE_TO_ADOPT

or:

PHASE_2F1_TARGET_COLLISION_REVIEW_OWNER_DECISION_REQUIRED

PHASE_2F1_TARGET_COLLISION_REVIEW_UNRELATED_OR_UNSAFE

PHASE_2F1_TARGET_COLLISION_REVIEW_BLOCKED

At completion, output:

- final token;
- exact three dirty paths;
- whether anything is staged;
- provenance conclusion;
- content-scope conclusion;
- recommended disposition;
- report path;
- confirmation that nothing was modified.
