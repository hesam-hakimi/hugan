# Objective

Analyze the current Phase 2C acceptance-audit failures and produce a precise, evidence-backed remediation plan.

This is an OBSERVE-ONLY task.

Do not modify source files.
Do not commit, push, merge, rebase, deploy, or modify PR metadata.
Do not start Phase 2D.

# Required investigation

1. Verify the current Phase 2C branch/worktree state and HEAD.

2. Locate and read the authoritative Phase 2C ADR, implementation files, validation logic, and related tests.

3. Reproduce or verify the known acceptance findings, including:

   - canonical ProductGroup -> Schema -> Dataset hierarchy can be bypassed;
   - canonical DatasetRecord may still allow schema_id=None;
   - registry_version may not identify the complete governed RegistrySnapshot;
   - explicit ProductGroup or Schema refs may contradict dataset-derived hierarchy;
   - field_refs, grain_field_refs, and time_field_refs may not be fully constrained to selected dataset scope;
   - cross-ProductGroup relationship behavior may lack explicit dedicated coverage;
   - PII/PCI/security classification handling must remain governance metadata, not authorization;
   - registry-cache concurrency behavior/test contract requires classification.

4. Determine which findings belong to the Phase 2B parent branch and which belong strictly to Phase 2C.

5. For every confirmed finding, identify:

   - requirement/contract being violated;
   - exact source file(s);
   - exact symbol(s);
   - related test file(s);
   - whether the issue is implementation, contract, test, or ambiguity;
   - minimum safe remediation.

6. Identify dependency ordering between fixes.

7. Identify all focused tests and regression tests that must pass before Phase 2C can receive final acceptance.

8. Check whether any issue requires a product/architecture decision rather than a code change.

# Constraints

- Read and search broadly enough to establish evidence.
- Prefer repository-authored ADRs, plans, contracts, source, and tests over assumptions.
- Do not invent metadata rules.
- Do not infer authorization from metadata.
- Public API behavior must remain unchanged unless an authoritative requirement says otherwise.
- Treat unknown or conflicting evidence as a blocker/decision, not as permission to guess.
- Preserve parent branches and existing PR state.
- No source writes of any kind.

# Required final output

Return:

1. Overall assessment:
   - READY_FOR_REMEDIATION
   - BLOCKED_BY_AMBIGUITY
   - or INCOMPLETE_EVIDENCE

2. Current worktree / branch / HEAD evidence.

3. Finding-by-finding table with:
   - finding
   - reproduced/confirmed?
   - owning phase (2B or 2C)
   - source file/symbol
   - tests
   - remediation summary

4. Exact recommended implementation order.

5. Exact files expected to change in Phase 2B, if any.

6. Exact files expected to change in Phase 2C.

7. Focused test plan.

8. Full regression test plan.

9. Product/architecture decisions still required.

10. Explicit confirmation that no source file, branch, PR, worktree, or deployment was changed.
