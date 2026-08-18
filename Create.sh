cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

TASK_FILE="$HOME/phase2c-safe-scope-design.md"

cat > "$TASK_FILE" <<'EOF'
# Objective

Design the exact, bounded, file-level Safe Mode scope for the first real
Phase 2C AskTD remediation slice.

This is a read-only scope-design task. Do not implement or modify anything.

# Seven approved architecture and contract decisions

1. Unit, contract, and standard CI tests must use deterministic synthetic
   or mock data.

2. Live governed data may be used only in a separate, optional, read-only,
   environment-gated integration profile. It must not be required by the
   standard CI acceptance gate.

3. Field governance and classification enforcement are explicitly deferred
   in Phase 2C:
   - classification metadata may be absent, null, or unknown;
   - valid metadata must be preserved and serialized;
   - Phase 2C must not grant authorization based on classification metadata;
   - malformed governance or classification values must be rejected.

4. Registry snapshots are immutable and publication must be atomic:
   - readers see either the complete previous snapshot or the complete new
     snapshot;
   - readers must never observe partially published state.

5. Stale registry writers must be rejected using a version conflict:
   - cache identity must include registry version or snapshot identity;
   - publication of a new snapshot must deterministically invalidate stale
     cache entries.

6. Registry identity must be derived from canonical full snapshot content:
   - semantic changes to ProductGroup, Schema, Dataset, Field, or Relationship
     require a new identity;
   - ordering-only differences must not create a new identity;
   - equal canonical content must produce equal identity;
   - stale or conflicting snapshots must be rejected.

7. Cross-ProductGroup relationships must be explicit:
   - both endpoints must exist;
   - the relationship must not expand authorization;
   - authorization for each Dataset remains independently enforced;
   - relationships with unknown endpoints must be rejected.

# Process rule

Production source code must not be placed in the first Safe Mode scope.

Production code may be proposed later only when an approved contract test
demonstrates a real implementation gap.

# Required investigation

1. Inspect repository instructions, ADRs, architecture documents, current
   contracts, tests, fixtures, and test configuration.

2. Identify the smallest coherent documentation-and-test-only slice that
   begins closing these currently missing or partial areas:

   - field-governance and metadata-classification deferral;
   - registry-cache concurrency and stale-cache behavior;
   - full snapshot registry identity;
   - explicit cross-ProductGroup relationship behavior.

3. Reuse existing test and documentation conventions.

4. Identify exact repository-relative paths.

5. For every proposed path, determine one exact operation:

   - MODIFY, only when the file currently exists;
   - CREATE, only when the file currently does not exist and its parent
     directory and naming convention are supported by repository evidence.

6. Do not guess paths.

7. Do not include production source paths.

8. Limit the first slice to at most four changed files.

9. Identify exact focused-test commands using the repository's existing test
   runner and configuration.

10. Identify dependencies and stop conditions.

# Required PhasePlan output

Return exactly one bounded slice.

For the slice:

- `included_scope` must contain entries in one of these exact forms:

  - `MODIFY path/to/file`
  - `CREATE path/to/file`

- `expected_paths` must contain the raw repository-relative paths without
  the MODIFY or CREATE prefix.

- `acceptance_criteria` must be deterministic and testable.

- `recommended_checks` must contain exact commands or exact test targets.

- `excluded_scope` must explicitly exclude production source code, deployment,
  authentication, environment configuration, Git publication, and live-data
  dependencies.

- Any missing exact file location or missing authoritative contract must remain
  visible as a blocker.

# Evidence requirements

Every path and operation must be supported by repository evidence.

For an existing file, include the exact path and relevant symbol or line range.

For a new file, include evidence for:

- the existing parent directory;
- the repository naming convention;
- the closest analogous test or document.

# Constraints

- Observe only.
- Do not modify, create, delete, or rename files.
- Do not stage, commit, push, create or edit a pull request, merge, or deploy.
- Do not invent contracts.
- Do not infer that a proposed file already exists.
- Preserve the original branch, HEAD, Git status, and worktree inventory.
EOF

bash scripts/observe-project.sh \
  --skip-install \
  --repository /app1/tag5916/projects/kmai-td-genie \
  --ref phase2/semantic-plan-contract-validator \
  --task-file "$TASK_FILE" \
  --title "Phase 2C exact Safe Mode scope design" \
  --host-client /app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py
