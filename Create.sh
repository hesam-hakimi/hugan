cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

TASK_FILE="$HOME/phase2c-evidence-closure.md"

cat > "$TASK_FILE" <<'EOF'
# Objective

Perform a read-only Phase 2C evidence and acceptance-contract closure.

The purpose of this task is not to implement code. It is to replace generic
blockers with exact repository evidence, exact missing contracts, and exact
acceptance criteria.

# Fixed architecture decision

Cross-ProductGroup unit, contract, and CI tests must use deterministic
synthetic or mock data.

Live governed data may be used only by a separate, optional, read-only,
environment-gated integration qualification profile. Live data must not be a
prerequisite for unit tests or the standard CI acceptance gate.

# Required investigation

1. Locate authoritative repository evidence for the canonical hierarchy:

   ProductGroup → Schema → Dataset → Field

2. Locate the authoritative contract for mandatory schema membership:

   - whether every Dataset must have a schema_id;
   - whether every Schema must belong to a ProductGroup;
   - how missing, unknown, duplicate, or cross-ProductGroup references behave.

3. Locate the authoritative registry-version contract:

   - what constitutes registry identity;
   - whether identity includes the full snapshot content;
   - which changes require a new version identity;
   - how stale or conflicting snapshots are rejected.

4. Locate the contract and existing tests for:

   - field governance;
   - field classification;
   - metadata-classification deferral;
   - unsupported or deferred governance values.

5. Locate the contract and existing tests for:

   - cross-ProductGroup relationships;
   - allowed versus rejected relationship behavior;
   - same-ProductGroup and cross-ProductGroup cases;
   - security and authorization implications.

6. Locate the contract and existing tests for:

   - registry-cache concurrency;
   - snapshot publication;
   - stale cache behavior;
   - simultaneous readers and writers;
   - deterministic cache invalidation.

7. Locate the public API security and compatibility evidence relevant to
   Phase 2C.

8. Inspect these files when present and identify the exact symbols and tests:

   - test_registry_hierarchy_contract.py
   - test_registry_contract.py

9. For every requirement, classify it as exactly one of:

   - CONFIRMED
   - PARTIALLY_CONFIRMED
   - MISSING
   - CONTRADICTED
   - EXPLICITLY_DEFERRED

10. Every confirmed or partially confirmed claim must include an exact
    repository-relative file path and, where possible, a line range or symbol.

11. Verify that every expected implementation or test path actually exists.
    Do not output a guessed path as an existing path.

12. Clearly distinguish:

    - existing paths;
    - proposed future paths;
    - missing authoritative documents;
    - unresolved architecture decisions.

13. Map every requested Phase 2C focus area to one of:

    - an implementation slice;
    - a test-only slice;
    - a documentation/contract slice;
    - an explicit blocker;
    - an explicit deferral.

# Required output

Return an evidence-backed Phase 2C plan containing:

- exact confirmed contracts;
- exact missing contracts;
- repository-relative evidence paths;
- internal slice dependencies;
- external prerequisites;
- test-only remediation slices;
- production-code remediation slices, only where evidence proves they are needed;
- explicit stop conditions;
- final acceptance criteria;
- independent reviewer findings;
- explicit confirmation that no repository change occurred.

# Constraints

- Observe only.
- Do not modify, create, delete, or rename files.
- Do not stage, commit, push, create or edit a pull request, merge, or deploy.
- Do not invent contracts.
- Do not treat a proposed path as an existing path.
- Missing evidence must remain visible as a blocker.
- Preserve the original repository branch, HEAD, Git status, and worktree inventory.
EOF

bash scripts/observe-project.sh \
  --skip-install \
  --repository /app1/tag5916/projects/kmai-td-genie \
  --ref phase2/semantic-plan-contract-validator \
  --task-file "$TASK_FILE" \
  --title "Phase 2C authoritative evidence closure" \
  --host-client /app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py
