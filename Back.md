
DIAGNOSE AND REPAIR FULL-WORKLOAD REVIEWER ROLE_OUTPUT_INVALID

We are working only on the AskTD / KMAI local development agent.

Repository:

/app1/tag5916/projects/kmai-td-genie

Local agent:

.kmai-dev-agent

Do not work on any ETL repository or ETL-related phase.

A small real Observe smoke test passed after the previous role-output
repair, but the first full Phase 2C qualification task failed again during
the Reviewer stage.

Failed task ID:

task-20260815T024721Z-3e8bc744

Task directory:

/app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/state/tasks/task-20260815T024721Z-3e8bc744

Observed sequence:

running_regression_tests
→ reviewing
→ reviewer_started
→ role_output_invalid
→ failed

Known final state:

- finalStatus: FAIL
- reviewerVerdict: null
- changedPaths: []
- noCommitPushMergeDeploy: true

This is a local-agent infrastructure diagnosis and repair task.

Do not perform Phase 2C application remediation.

────────────────────────────────────
1. Safety boundary
────────────────────────────────────

Allowed modifications:

- `.kmai-dev-agent/**` only.

Do not modify:

- tracked AskTD application source;
- tracked tests;
- tracked documentation;
- Phase 2B or Phase 2C source branches;
- worktrees;
- pull requests;
- Git history;
- deployment configuration;
- authentication;
- credentials;
- environment settings.

Do not:

- commit;
- push;
- merge;
- rebase;
- deploy;
- install packages;
- expose raw model responses;
- expose private reasoning;
- rerun the full Phase 2C qualification before the Reviewer-only replay
  succeeds.

Confirm first that `.kmai-dev-agent` is ignored and untracked.

────────────────────────────────────
2. Determine whether stale code handled the failed task
────────────────────────────────────

Verify whether the failed task was executed using the latest repaired
version of:

.kmai-dev-agent/autonomous_task.py

Compare safely:

- current file hash;
- task execution timestamp;
- UI server/process start timestamp;
- persisted task schema/version;
- any recorded parser or validator version.

Classify:

A. STALE_RUNTIME

The failed task used the old parser because the UI/task process was not
restarted.

B. CURRENT_RUNTIME_FAILURE

The failed task used the repaired parser but exposed a second defect.

Do not assume either result.

If it was stale runtime:

- make no unnecessary parser change;
- prove the restarted UI loads the current code;
- continue to the Reviewer-only replay.

────────────────────────────────────
3. Inspect the failed Reviewer artifacts
────────────────────────────────────

Inspect only the persisted sanitized artifacts for:

task-20260815T024721Z-3e8bc744

Identify:

- failing role;
- validator function;
- first response result;
- repair response result;
- whether schema repair was invoked;
- retry count;
- exact sanitized validation path;
- exact sanitized validation reason;
- finish reason;
- output character count;
- completion-token usage;
- reasoning-token usage when available;
- whether output was truncated;
- whether one or multiple JSON objects were detected;
- whether Markdown fences or explanatory wrapper text were present;
- missing required fields;
- invalid enum values;
- forbidden fields;
- incorrect nested data types.

Do not print the complete raw model response.

Do not print repository-sensitive prompt or evidence content.

Return only safe structural diagnostics.

If field-level diagnostics were not persisted, record that as an
infrastructure defect.

────────────────────────────────────
4. Compare the successful and failed Reviewer workloads
────────────────────────────────────

Compare the failed full task with:

- the successful real Observe smoke task;
- the successful c2-preview task.

Compare only structural metrics:

- Reviewer input size;
- number of evidence items;
- number of findings;
- number of file/symbol references;
- Planner artifact size;
- test artifact size;
- requested output schema;
- prompt/schema version;
- maximum output-token budget;
- actual model;
- repair attempts;
- response size;
- finish reason.

Determine whether the full-task failure was caused by:

- stale runtime;
- output truncation;
- insufficient completion-token budget;
- prompt/schema drift;
- invalid nested enum;
- missing nested field;
- forbidden extra field;
- multiple JSON objects;
- malformed/truncated JSON;
- oversized Reviewer context;
- insufficient repair instructions;
- another evidence-supported reason.

────────────────────────────────────
5. Reproduce the failure locally
────────────────────────────────────

Use the persisted sanitized artifacts from the failed task to create the
smallest deterministic Reviewer-only reproduction.

Do not rerun:

- repository indexing;
- Planner;
- source inspection;
- Phase 2 tests;
- full Phase 2C qualification.

Use the same:

- Reviewer prompt contract;
- output schema;
- parser;
- validator;
- repair path.

The reproduction must produce the same safe failure classification before
the repair.

────────────────────────────────────
6. Implement the smallest safe repair
────────────────────────────────────

Implement only an evidence-supported change.

Possible repairs include:

- correcting prompt/schema mismatch;
- increasing the bounded Reviewer output budget when truncation is proven;
- reducing unnecessary context sent to Reviewer;
- summarizing large evidence artifacts before Reviewer invocation;
- placing detailed evidence in referenced artifacts instead of the
  schema-bound output;
- requiring concise bounded finding arrays;
- improving nested field-level repair instructions;
- fixing an enum mismatch;
- deterministic extraction of exactly one JSON object;
- safe handling of one Markdown JSON fence;
- safe persistence of oversized event data through hash and size metadata;
- displaying the safe field-level failure in UI.

Do not:

- weaken mandatory Reviewer fields;
- convert FAIL into PASS;
- accept partial output;
- remove required findings;
- silently discard invalid fields;
- accept arbitrary extra fields;
- use unbounded retries;
- expose raw malformed output or private reasoning.

Preserve fail-closed behavior.

────────────────────────────────────
7. Add full-workload regression tests
────────────────────────────────────

Add local-agent tests that cover:

1. Reviewer output with at least eight findings.
2. Findings owned by both Phase 2B and Phase 2C.
3. Long but bounded source paths and symbol names.
4. Nested remediation dependencies.
5. Architecture-decision findings.
6. Valid PASS_WITH_CONDITIONS.
7. Valid FAIL with findings.
8. Truncated large JSON.
9. Completion-token exhaustion.
10. Missing required nested field.
11. Invalid nested enum.
12. Forbidden nested field.
13. Multiple JSON objects.
14. Successful single bounded repair.
15. Repair exhaustion and fail-closed result.
16. Safe field-level diagnostic event.
17. No raw model response in UI or task events.
18. No private reasoning exposure.

Run:

- focused Reviewer schema tests;
- all local-agent self-tests;
- UI self-tests;
- fake Observe E2E;
- fake Safe E2E;
- Python compilation;
- Bash syntax validation;
- authentication probe.

Expected authentication output:

KMAI_DEV_AGENT_AUTH_OK

────────────────────────────────────
8. Reviewer-only replay
────────────────────────────────────

After the tests pass, replay only the Reviewer stage using the persisted
Planner, evidence, and test artifacts from:

task-20260815T024721Z-3e8bc744

Do not rerun repository investigation.

Expected:

- Reviewer output is schema-valid;
- reviewerVerdict is populated;
- Review artifact exists;
- Final Report can be constructed;
- no role_output_invalid;
- no tracked source changes.

If the Reviewer-only replay fails, stop.

Do not rerun the full qualification.

────────────────────────────────────
9. One controlled full qualification
────────────────────────────────────

Only if Reviewer-only replay passes, run the full Phase 2C Observe
qualification once.

Use:

Workspace:
/tmp/kmai-phase2c-semantic-plan

Branch:
phase2/semantic-plan-contract-validator

Autonomy:
observe

Expected:

- phase: completed;
- Planner artifact present;
- targeted evidence present;
- tests present;
- Reviewer output schema-valid;
- reviewerVerdict populated;
- Final Report present;
- changedPaths empty;
- no commit/push/merge/deploy;
- no role_output_invalid.

────────────────────────────────────
10. Final response
────────────────────────────────────

Return:

1. Overall PASS or FAIL.
2. STALE_RUNTIME or CURRENT_RUNTIME_FAILURE.
3. Exact failing Reviewer field/path and safe reason.
4. Whether truncation/token budget was involved.
5. Whether schema repair ran and why it failed.
6. Structural difference between smoke and full workloads.
7. Exact `.kmai-dev-agent` files changed.
8. Exact repair implemented.
9. Focused test results.
10. Full self-test and UI-test results.
11. Reviewer-only replay result.
12. Controlled full qualification result.
13. Authentication probe result.
14. Before/after tracked Git status.
15. Confirmation that no AskTD source, branch, worktree, PR, credential,
    environment setting, or deployment changed.
16. Whether the Agent is now qualified for full real Observe tasks.
