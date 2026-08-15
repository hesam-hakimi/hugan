# Objective

Perform a complete read-only qualification of the current Phase 2C
acceptance-audit findings and produce an evidence-backed remediation plan.

This is an OBSERVE-ONLY task.

Do not modify source files.
Do not commit, push, merge, rebase, deploy, or modify PR metadata.
Do not start Phase 2D.

# Required investigation

1. Verify and report:

   - repository root;
   - current worktree;
   - branch;
   - HEAD;
   - clean/dirty status;
   - Phase 2B parent branch;
   - Phase 2C branch ancestry.

2. Locate and read the authoritative artifacts for Phase 2B and Phase 2C,
   including:

   - Phase 2B ADR;
   - Phase 2C ADR;
   - registry contracts;
   - registry cache/service implementation;
   - hierarchy validation;
   - governed semantic-plan contract and validator;
   - focused tests;
   - relevant acceptance and regression tests.

3. Verify every known finding independently:

   A. Canonical hierarchy:
      ProductGroup -> Schema -> Dataset -> Field.

   B. Whether a canonical DatasetRecord can still use schema_id=None.

   C. Whether registry_version identifies the complete governed
      RegistrySnapshot, including ProductGroups, Schemas, Fields,
      Relationships, and adaptation outcomes.

   D. Whether explicit product_group_refs or schema_refs can contradict
      the hierarchy derived from selected datasets.

   E. Whether field_refs, grain_field_refs, and time_field_refs are
      constrained to the selected dataset scope.

   F. Whether explicit cross-ProductGroup relationships have dedicated
      validation and tests.

   G. Whether PII, PCI, security classification, business name,
      business description, data type, and key metadata are retained or
      explicitly deferred as governance metadata rather than treated as
      authorization.

   H. Whether the registry-cache concurrency issue is:
      - an implementation defect;
      - a test defect;
      - a pre-existing flake;
      - or an unresolved contract ambiguity.

4. For each finding determine the owning phase:

   - Phase 2B / parent PR;
   - Phase 2C / child PR;
   - product or architecture decision;
   - test-only correction;
   - or not reproducible.

5. For every confirmed finding provide:

   - violated requirement;
   - authoritative evidence;
   - exact source file;
   - exact symbol;
   - exact related test file;
   - current behavior;
   - expected behavior;
   - minimum safe correction;
   - dependency on another correction.

6. Produce a remediation order that respects the stacked branch chain.

7. Identify exact focused tests and full regression gates required before
   Phase 2C can receive final acceptance.

# Evidence requirements

Do not rely only on keyword matches.

For every finding, read the relevant contiguous ADR, contract, source, and
test sections.

Classify every statement as:

- evidenced fact;
- inference;
- unresolved ambiguity.

Do not invent missing contracts.

Metadata existence must never be treated as authorization.

Public API behavior must remain unchanged unless an authoritative
requirement explicitly says otherwise.

# Required final output

Return:

1. Overall classification:

   - READY_FOR_REMEDIATION
   - BLOCKED_BY_AMBIGUITY
   - or INCOMPLETE_EVIDENCE

2. Repository/worktree/branch/HEAD evidence.

3. Complete finding matrix containing:

   - finding ID;
   - reproduced or not;
   - owning phase;
   - requirement;
   - source file and symbol;
   - test file;
   - correction;
   - dependency;
   - confidence.

4. Exact Phase 2B files expected to change.

5. Exact Phase 2C files expected to change.

6. Exact implementation sequence across the stacked branches.

7. Focused test plan.

8. Full regression and acceptance plan.

9. Product or architecture decisions still required.

10. Explicit confirmation that no source file, branch, worktree, PR,
    deployment, or environment setting was changed.
