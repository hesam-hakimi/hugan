TASK: PHASE_2F1_REVIEW_WORKSPACE_INCIDENT_DISPOSITION

Perform one bounded owner-authorized investigation and, only when byte-exact
recovery is independently proven, restore the two ignored artifacts changed
during the Phase 2F.1 independent review.

Do not repair M1 or M2 in this task.
Do not run tests.
Do not modify any source file, commit, branch, index, remote, PR, or workflow.

==================================================
1. TARGET IDENTITY
==================================================

Repository:
TD-Enterprise/kmai-td-genie

Logical worktree:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification

Application root:
/home/tag5916/projects/kmai-td-genie-worktrees/phase2f1-recipe-lifecycle-classification/kmai-td-genie

Required branch:
phase2/recipe-lifecycle-classification

Required HEAD:
c1639fc779aaed64e4be9fdd17381e0f293c7f9f

Required tree:
a5bd9ed7f7959c02ccb6c00b574599fb32d4fa95

Required parent:
f283f01b6d615f9fa00debcef959d9c5c86a3224

==================================================
2. REQUIRED REPORTS
==================================================

Read completely:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_IMPLEMENTATION_CONTINUATION_2026-08-27.md

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_INDEPENDENT_REVIEW_2026-08-27.md

Verify that the independent-review report ends with:

PHASE_2F1_INDEPENDENT_REVIEW_BLOCKED_WORKSPACE

Extract the authoritative pre-test and post-focused size and SHA-256 evidence
for the two affected ignored paths directly from that report. Do not rely on
screenshots or manually transcribed hashes.

==================================================
3. PRE-MUTATION IDENTITY GATE
==================================================

Before inspecting recovery options, verify:

- pwd and pwd -P;
- target realpath;
- Git top-level and common directory;
- origin identity;
- branch, HEAD, tree, parent, and commit subject;
- tracked and untracked porcelain;
- staged state;
- shared-worktree identity.

Required Git state:

- exact expected identity;
- tracked, untracked, and staged states empty;
- no source change since the blocked review.

Also record the current existence, type, mode, size, and SHA-256 of:

1. kmai-td-genie/.coverage
2. kmai-td-genie/logs/app.log

Expected incident state from the review:

- .coverage was deleted;
- logs/app.log remains present but changed.

If identity or incident state differs, stop without mutation.

==================================================
4. STRICT SCOPE
==================================================

The only paths that may potentially be restored are:

- kmai-td-genie/.coverage
- kmai-td-genie/logs/app.log

Do not modify:

- any tracked file;
- any other ignored file;
- any __pycache__ or .pyc file;
- Git index, refs, configuration, branches, or worktrees;
- source, tests, documentation, reports from earlier tasks;
- remote GitHub state.

Do not use:

- git clean;
- git reset;
- git checkout;
- git restore;
- stash;
- broad recursive deletion;
- test execution;
- coverage regeneration;
- guessed or synthesized file content.

Do not conceal the incident.

==================================================
5. BYTE-EXACT RECOVERY INVESTIGATION
==================================================

First operate read-only.

For logs/app.log:

1. Obtain its exact pre-review byte length and SHA-256 from the independent
   review report.
2. Check whether the current file’s prefix of exactly that recorded byte length
   has the recorded pre-review SHA-256.
3. If and only if it matches exactly, the appended portion is independently
   proven to be the review-generated mutation.
4. Record the appended byte count and its SHA-256, but do not include raw log
   content, credentials, tokens, business data, or exception payloads in the
   report.

For .coverage:

1. Obtain the exact pre-review size and SHA-256 from the independent-review
   report.
2. Search read-only and only within permanent KMAI worktrees and task-owned
   review locations for an already-existing regular file with:
   - the exact recorded size;
   - the exact recorded SHA-256;
   - a valid coverage-data file identity.
3. Do not accept a matching filename without matching bytes.
4. Do not regenerate the file by running tests.
5. Do not copy a different coverage database even if it appears semantically
   equivalent.

Candidate search must not inspect unrelated repositories or user directories.

==================================================
6. RESTORATION AUTHORIZATION BOUNDARY
==================================================

Restoration is authorized only if both artifacts are byte-exactly recoverable.

Required conditions:

- logs/app.log’s pre-review prefix matches the recorded pre-review hash;
- an exact existing copy of .coverage matches the recorded pre-review size and
  hash;
- the target paths resolve inside the exact application root;
- no other workspace drift exists.

If all conditions pass:

1. Restore .coverage from the independently verified byte-identical source.
2. Restore logs/app.log to its independently verified pre-review prefix.
3. Do not change timestamps intentionally beyond unavoidable filesystem write
   effects.
4. Do not touch any other path.

If either artifact cannot be recovered byte-exactly:

- do not restore either artifact;
- do not truncate logs/app.log;
- do not create .coverage;
- do not invent a replacement;
- stop and request explicit owner disposition of the current ignored state.

This task must never produce a partially restored workspace.

==================================================
7. POST-RESTORATION VERIFICATION
==================================================

If restoration occurred, independently prove:

- .coverage exists with the exact pre-review type, mode, size, and SHA-256;
- logs/app.log has the exact pre-review type, mode, size, and SHA-256;
- tracked, untracked, and staged Git states remain empty;
- branch, HEAD, tree, parent, and index remain unchanged;
- no source, test, ADR, or configuration file changed;
- exactly the two authorized ignored paths changed relative to task start;
- the final worktree manifest matches the pre-review manifest evidence wherever
  that evidence is available.

Do not run Phase 2F.1 tests in this task.

==================================================
8. REPORT
==================================================

Write exactly one report outside the repository:

/home/tag5916/projects/kmai-td-genie-worktrees/reports/ASKALPHA_PHASE_2F1_REVIEW_WORKSPACE_INCIDENT_DISPOSITION_2026-08-27.md

Include:

1. final disposition;
2. workspace and commit identity;
3. incident evidence from the independent-review report;
4. initial state of both affected paths;
5. bounded recovery-source search;
6. log-prefix verification;
7. coverage-file recovery proof;
8. whether restoration was permitted;
9. exact actions performed;
10. pre/post hashes and sizes;
11. proof that no other path changed;
12. clean Git-state attestation;
13. incident-preservation attestation;
14. exact next permitted action.

If both files were restored byte-exactly, the next permitted action is a
separately authorized repair of M1 and M2.

If exact restoration was impossible, the next permitted action is an explicit
owner decision to accept the current ignored-artifact state as a new review
baseline or provide an authoritative recovery source.

End with exactly one token:

PHASE_2F1_REVIEW_WORKSPACE_INCIDENT_RESTORED

or:

PHASE_2F1_REVIEW_WORKSPACE_INCIDENT_REQUIRES_OWNER_DISPOSITION

or:

PHASE_2F1_REVIEW_WORKSPACE_INCIDENT_BLOCKED_IDENTITY

or:

PHASE_2F1_REVIEW_WORKSPACE_INCIDENT_BLOCKED_UNEXPECTED_DRIFT
