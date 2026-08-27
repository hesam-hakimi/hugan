TASK: PHASE_2F1_IMPLEMENTATION_DISCOVERY

Perform one bounded, strictly read-only implementation discovery for Phase 2F.1.

Do not implement Phase 2F.1 in this task.

Repository:
TD-Enterprise/kmai-td-genie

Required logical repository root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2e-governed-field-records/kmai-td-genie

The equivalent physical /app1 path is acceptable only if realpath proves both
paths identify the same permanent Phase 2E worktree.

==================================================
1. WORKSPACE GATE
==================================================

Before reading repository files, verify:

- pwd;
- pwd -P;
- realpath of the required logical root;
- Git top-level and common directory;
- origin identity;
- current branch;
- current local HEAD;
- git status --porcelain=v1 --untracked-files=all.

Required local identity:

Branch:
phase2/governed-field-records

HEAD:
0430613e6a9f1680338d8fc099e7960e5d46cac2

Required worktree/index:
completely clean, including zero untracked files.

Do not use or inspect:

- the stale primary checkout;
- branch asktd_v2;
- sibling repositories;
- ETL/UCA workspaces;
- Windows/ETL Coding Agent sessions;
- temporary worktrees.

Do not fetch, pull, switch branches, reset, stash, clean, merge, rebase,
cherry-pick, commit, push, or modify Git configuration.

If the workspace gate fails, stop without mutation and end with:

PHASE_2F1_DISCOVERY_BLOCKED_WORKSPACE

==================================================
2. REQUIRED PRIOR EVIDENCE
==================================================

Read these reports completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_MERGE_2026-08-26.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKTD_PHASE_2E_PR17_POSTMERGE_REVERIFICATION_2026-08-26.md

Use them only as evidence indexes.

Independently verify through authenticated, read-only GitHub requests:

- current main SHA:
  f283f01b6d615f9fa00debcef959d9c5c86a3224
- PR #17 is closed and merged;
- PR #17 accepted head:
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- merge commit has exactly two parents:
  409fed3fb98fc87547a7d05a68292fc28c3c1e7c
  0430613e6a9f1680338d8fc099e7960e5d46cac2
- merge-commit tree is byte-identical to the local Phase 2E candidate tree;
- Phase 2E workflow completed successfully.

If current main or the accepted Phase 2E identity differs, stop and end with:

PHASE_2F1_DISCOVERY_BLOCKED_BASE_DRIFT

==================================================
3. FIXED PHASE 2F.1 PRODUCT DECISIONS
==================================================

Treat all decisions in this section as fixed. Do not reopen them.

Phase 2F.1 is classification-only.

It must not:

- warn or block runtime execution;
- persist lifecycle evaluation results;
- add a database, API, cache, queue, or new persistence backend;
- query or scan business data in Synapse or Databricks;
- implement Phase 2F.2 policy decisions;
- implement Phase 3 provider integrations;
- implement Phase 6 performance work.

The evaluator must:

- be pure, deterministic, provider-neutral, and side-effect-free;
- receive already-resolved approval evidence as input;
- never call a provider, proxy, database, network client, Synapse, Databricks,
  Dedicated SQL Pool, or Data Lake directly;
- return an immutable LifecycleEvaluationResult;
- return all applicable deterministic reason codes;
- return all affected dependency references;
- use stable ordering independent of input ordering;
- return one final lifecycle state using this precedence:

  BROKEN
  NOT_APPROVED
  REVIEW_REQUIRED
  VALID

Add an abstract ApprovalEvidenceProvider port and one initial adapter over the
existing ApprovedRecipe/approval metadata.

The orchestration layer resolves approval evidence through the port before
calling the pure evaluator.

Missing, ambiguous, conflicting, or invalid evidence must fail closed.

With the Phase 2F feature flag disabled, exact Phase 2E behavior must remain
unchanged.

Do not invent approval expiry, reapproval windows, owners, approvers, manual
overrides, or runtime enforcement. Those are later product decisions.

Scale context, recorded for future phases only:

- anticipated data volume is approximately 5 TB or more;
- Synapse data resides in Dedicated SQL Pools;
- Databricks data resides in the Data Lake;
- Phase 2F.1 must operate on bounded metadata/evidence only;
- no lifecycle decision may require a full or partial business-data scan;
- provider-side query pushdown belongs to Phase 3;
- benchmarks, concurrency, scan-cost controls, and SLO validation belong to
  Phase 6.

==================================================
4. INSPECT THE CURRENT IMPLEMENTATION
==================================================

Read only the minimum relevant repository files.

Start from the exact Phase 2E inventory and follow imports only where required:

- docs/adr/0005-phase2e-governed-field-records.md
- docs/adr/README.md
- src/backend/app/available_data/field_evidence.py
- src/backend/app/available_data/registry_contract.py
- src/backend/app/recipes/approved_recipes.py
- src/backend/app/recipes/dependency_fingerprint.py
- test/test_approved_recipe_pilot.py
- test/test_authz_no_access_guard.py
- test/test_governed_field_records.py
- test/test_provider_abstraction_contracts.py
- test/test_recipe_dependency_fingerprint.py
- test/test_semantic_plan_contract.py

Account for the repository’s actual nested path prefix if present.

Inspect additional files only when directly required to identify:

- ApprovedRecipe model and approval metadata;
- recipe registry and lookup path;
- Phase 2E FieldRecord and dependency-reference contracts;
- fingerprint computation and comparison;
- semantic-plan or orchestration entry point;
- existing feature-flag mechanism;
- existing Protocol/ABC/provider conventions;
- immutable-model conventions;
- exception and fail-closed conventions;
- serialization conventions;
- Python/runtime version;
- test framework, fixtures, parametrization, and coverage commands;
- ADR numbering and formatting conventions;
- module export conventions.

For every additional file read, record why it was necessary.

Do not read unrelated product areas or implementation phases.

==================================================
5. ANSWER THE IMPLEMENTATION QUESTIONS
==================================================

Determine from actual code, without guessing:

1. Exact existing approval fields and their types.
2. Whether approval is represented by status, boolean, enum, provenance,
   timestamp, or another structure.
3. Exact dependency-reference and fingerprint types already available.
4. Which evidence can be classified as:
   - VALID;
   - REVIEW_REQUIRED;
   - BROKEN;
   - NOT_APPROVED;
   without inventing new product policy.
5. Which conditions cannot be classified using current metadata.
6. Exact orchestration boundary where approval evidence should be resolved.
7. Exact boundary where the pure evaluator should be called.
8. Whether the repository prefers Protocol, ABC, callable adapter, or another
   port pattern.
9. Whether immutable results should use frozen dataclasses, NamedTuple,
   Pydantic configuration, or an existing project-specific pattern.
10. Exact existing feature-flag mechanism and safe default-OFF behavior.
11. Exact serialization representation required for enums, tuples, reason
    codes, and dependency references.
12. Exact stable sorting key for affected dependency references.
13. How duplicate dependency references should be normalized.
14. How missing, ambiguous, conflicting, malformed, or stale evidence is
    currently represented.
15. Whether current metadata supports approval expiry. If it does not, state
    explicitly that expiry must not be implemented in Phase 2F.1.
16. Whether any proposed operation could accidentally scan Synapse Dedicated
    SQL Pools or Databricks Data Lake data.
17. How to structurally prove that Phase 2F.1 is bounded by recipe dependency
    count and metadata size rather than total data volume.
18. Exact compatibility tests proving flag-OFF behavior is byte-for-byte or
    structurally identical to Phase 2E behavior.
19. Exact tests required for precedence, ordering, duplicates, missing
    evidence, ambiguity, conflict, invalid evidence, and all-reasons output.
20. Existing commands required for focused tests, full backend tests, golden
    tests, lint/type checks if configured, and coverage.

==================================================
6. COMPARE IMPLEMENTATION OPTIONS
==================================================

Compare these options against actual repository conventions:

A. Pure evaluator + ApprovalEvidenceProvider port + current-metadata adapter.

B. Evaluator directly calls an approval provider.

C. Evaluator directly reads ApprovedRecipe metadata with no port.

D. Persist lifecycle results and read them later.

Evaluate each for:

- determinism;
- testability;
- coupling;
- provider neutrality;
- compatibility with existing code;
- fail-closed behavior;
- Phase 3 extensibility;
- 5 TB+ safety;
- risk of accidental data scans;
- implementation complexity;
- migration risk.

Select exactly one recommended option.

Expected recommendation is A unless decisive repository evidence proves it
incompatible. If a different option is recommended, provide exact evidence
and stop for owner review. Do not silently change the fixed architecture.

==================================================
7. PROPOSE THE EXACT PHASE 2F.1 CONTRACT
==================================================

Propose, using repository-native names and types:

- lifecycle state enum;
- deterministic reason-code enum;
- approval-evidence value object;
- ApprovalEvidenceProvider port;
- initial current-metadata adapter;
- immutable LifecycleEvaluationResult;
- evaluator function or service signature;
- stable ordering and deduplication rules;
- fail-closed mapping table;
- final-state precedence algorithm;
- orchestration integration point;
- feature-flag boundary;
- observability limited to existing side-effect-free mechanisms;
- public exports;
- ADR addition;
- tests.

Important:

- Do not add timestamps inside the pure evaluator.
- Do not use current time, random values, global mutable state, I/O, network,
  database access, or environment reads inside the evaluator.
- Do not persist the result.
- Do not query raw or business data.
- Do not treat missing expiry metadata as “expired.”
- Preserve all applicable reason codes even when the final state is selected
  by precedence.

==================================================
8. FILE-BY-FILE IMPLEMENTATION PLAN
==================================================

Produce an exact minimal file plan containing:

- files to add;
- files to modify;
- purpose of each change;
- public symbols added or changed;
- expected test coverage;
- whether each file affects runtime behavior when the flag is OFF.

Separate:

- required Phase 2F.1 work;
- optional cleanup;
- explicitly deferred work.

Optional cleanup must not be included in the eventual implementation unless
separately authorized.

Estimate expected file count and explain any uncertainty.

==================================================
9. PRODUCT-DECISION GATE
==================================================

Identify whether any genuinely product-level decision is still required
before implementation.

Do not classify naming, module layout, typing, sorting, test design, adapter
shape, or internal error handling as product decisions when they can be
derived safely from repository conventions.

Only stop for a product decision if it would change externally observable
business behavior.

If one is required, provide:

- exactly one question;
- 2–3 mutually exclusive choices;
- recommended choice first;
- concrete behavioral impact of each choice.

If none is required, state exactly:

NO_ADDITIONAL_PRODUCT_DECISION_REQUIRED

==================================================
10. NO MUTATION
==================================================

This task is read-only.

Do not:

- edit or create repository files;
- create a branch or worktree;
- create, edit, close, reopen, review, or merge a PR;
- create a comment, label, issue, release, or workflow;
- trigger, rerun, cancel, or approve automation;
- modify local refs, index, configuration, or runtime flags;
- delete anything.

The only authorized write is the single report outside the repository.

==================================================
11. REPORT
==================================================

Write exactly one report:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_DISCOVERY_2026-08-26.md

Include:

1. final discovery verdict;
2. workspace and clean-state evidence;
3. current main and accepted Phase 2E identity;
4. files inspected and justification;
5. current model and contract inventory;
6. approval-evidence capabilities and limitations;
7. lifecycle state and reason mapping;
8. architecture-option comparison;
9. selected architecture;
10. exact proposed contracts and signatures;
11. orchestration and feature-flag integration points;
12. 5 TB+ bounded-metadata and no-scan proof;
13. exact file-by-file implementation plan;
14. exact test matrix and commands;
15. compatibility and regression gates;
16. risks and mitigations;
17. product-decision gate result;
18. whether implementation can begin without another question;
19. exact next permitted action;
20. local/repository/GitHub no-mutation attestation.

End with exactly one token:

PHASE_2F1_DISCOVERY_COMPLETE

or:

PHASE_2F1_DISCOVERY_BLOCKED_WORKSPACE
PHASE_2F1_DISCOVERY_BLOCKED_BASE_DRIFT
PHASE_2F1_DISCOVERY_BLOCKED_GITHUB_ACCESS
PHASE_2F1_DISCOVERY_BLOCKED_INSUFFICIENT_EVIDENCE
PHASE_2F1_DISCOVERY_BLOCKED_PRODUCT_DECISION
