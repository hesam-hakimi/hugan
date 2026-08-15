DIAGNOSE AND REPAIR THE SECOND REVIEWER ROLE_OUTPUT_INVALID FOUND BY THE
FULL PHASE 2C QUALIFICATION TASK

The previous local-agent infrastructure repair passed all focused,
self-test, fake-E2E, UI, authentication, and small real Observe smoke
tests.

However, the first full real qualification task exposed a second failure.

Exact failed task:

task-20260815T024721Z-3e8bc744

Task directory:

/app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/state/tasks/task-20260815T024721Z-3e8bc744

Observed task sequence:

running_regression_tests
→ reviewing
→ reviewer_started
→ role_output_invalid
→ failed

The failure occurred approximately eight seconds after reviewer_started.

The task produced:

- finalStatus: FAIL
- reviewerVerdict: null
- changedPaths: []
- noCommitPushMergeDeploy: true

This is an infrastructure/role-contract diagnosis task.

Do not perform Phase 2C remediation.

────────────────────────────────────
1. Safety boundaries
────────────────────────────────────

Allowed modifications:

- locally ignored `.kmai-dev-agent/**` only.

Do not modify:

- tracked application source;
- application tests;
- tracked documentation;
- Phase 2B or Phase 2C worktrees;
- branches;
- PRs;
- Git history;
- credentials;
- environment configuration;
- deployments.

Do not:

- commit;
- push;
- merge;
- rebase;
- deploy;
- install packages;
- run the full Phase 2C qualification again until the exact Reviewer
  failure has been reproduced and repaired.

Confirm `.kmai-dev-agent` remains ignored and untracked before editing.

────────────────────────────────────
2. Confirm the repaired runtime is active
────────────────────────────────────

Verify that the failed full task used the latest repaired
`.kmai-dev-agent/autonomous_task.py`.

Compare:

- file hash at task execution;
- current file hash;
- task event schema/version if available;
- UI server start time;
- task process start time.

Determine whether the task ran through:

A. the repaired role-output parser; or
B. a stale UI/task process using the older implementation.

Do not assume either result.

If the task used stale code, report that clearly, run no additional code
repair, and prove that a restarted UI/task process loads the new code.

────────────────────────────────────
3. Inspect the exact failed task artifacts
────────────────────────────────────

Inspect the persisted sanitized artifacts for:

task-20260815T024721Z-3e8bc744

Identify:

- exact failing role;
- validator used;
- field-level validation path;
- sanitized failure reason;
- whether the first Reviewer response or repair response failed;
- whether repair was invoked;
- retry count;
- finish reason;
- output-token usage;
- reasoning-token usage when available;
- response-content length;
- whether the response was truncated;
- whether multiple JSON objects were detected;
- whether Markdown fences or wrapper text were present;
- whether an enum, required field, forbidden field, array item, or data
  type failed validation.

Do not print:

- raw model output;
- private reasoning;
- sensitive repository content;
- prompts containing application data;
- credentials or headers.

If field-level diagnostics were not persisted, classify that itself as a
remaining diagnostic defect.

────────────────────────────────────
4. Compare successful and failed Reviewer workloads
────────────────────────────────────

Compare the failed full task against the successful small real smoke task
and the successful `c2-preview` task.

Compare only safe structural properties:

- Reviewer input character count;
- number of findings;
- number of evidence items;
- number and length of file paths;
- requested output fields;
- output-token budget;
- prompt/schema version;
- number of repair attempts;
- actual model;
- finish reason;
- response length.

Determine whether the failure is caused by:

- scale/output truncation;
- schema mismatch;
- prompt/schema drift;
- enum mismatch;
- unsupported extra fields;
- malformed JSON;
- ambiguous multiple objects;
- repair prompt insufficiency;
- another evidenced reason.

────────────────────────────────────
5. Reproduce without rerunning repository investigation
────────────────────────────────────

Create the smallest sanitized deterministic reproduction from the failed
Reviewer artifact.

Use the same:

- Reviewer schema;
- parser;
- validator;
- repair path;
- safe structural shape.

Do not rerun Planner, repository indexing, tests, or the full Phase 2C
qualification merely to reproduce the Reviewer failure.

The reproduction must fail with the same field-level classification.

────────────────────────────────────
6. Implement the smallest safe repair
────────────────────────────────────

Implement only an evidence-supported repair.

Possible repairs include:

- correcting prompt/schema drift;
- increasing the bounded Reviewer output budget when truncation is proven;
- reducing unnecessary Reviewer prompt material;
- requiring concise findings;
- splitting oversized internal evidence from the schema-bound Reviewer
  output;
- adding a bounded maximum and stable shape for finding arrays;
- supplying exact field-level repair instructions;
- fixing enum/value alignment;
- deterministic single-object extraction;
- preserving large event payloads through hash/size references;
- surfacing sanitized field-level failure details in the UI.

Do not:

- weaken required Reviewer fields;
- accept incomplete Reviewer output;
- change FAIL into PASS;
- silently discard findings;
- permit arbitrary extra fields;
- make retries unbounded;
- expose raw invalid output to the browser.

Preserve fail-closed behavior.

────────────────────────────────────
7. Add full-workload regression coverage
────────────────────────────────────

Add tests for Reviewer outputs representative of the full Phase 2C task:

1. eight or more findings;
2. findings split across Phase 2B and Phase 2C;
3. long but bounded source paths and symbols;
4. remediation dependencies;
5. product/architecture decision findings;
6. PASS_WITH_CONDITIONS;
7. FAIL with valid findings;
8. truncated large JSON;
9. token-budget exhaustion;
10. missing required nested field;
11. invalid nested enum;
12. forbidden nested field;
13. one successful bounded repair;
14. repair exhaustion;
15. UI-safe field-level error display;
16. no private reasoning or raw model output exposure.

Run:

- focused Reviewer schema tests;
- all local-agent self-tests;
- UI self-tests;
- fake Observe E2E;
- fake Safe E2E;
- Python compilation;
- Bash validation;
- authentication probe.

Expected probe:

KMAI_DEV_AGENT_AUTH_OK

────────────────────────────────────
8. Reviewer-only replay
────────────────────────────────────

After local tests pass, replay only the Reviewer stage using the persisted
sanitized Planner/evidence/test artifacts from:

task-20260815T024721Z-3e8bc744

Do not rerun repository scanning or application tests.

Expected result:

- Reviewer response schema-valid;
- Reviewer verdict populated;
- Review artifact present;
- no `role_output_invalid`;
- no tracked source changes.

If Reviewer-only replay fails, do not rerun the full qualification.

────────────────────────────────────
9. Controlled full rerun
────────────────────────────────────

Only after Reviewer-only replay passes, rerun the full Phase 2C Observe
qualification once.

Expected:

- Phase completed;
- Planner artifact present;
- targeted evidence present;
- tests present;
- Reviewer artifact schema-valid;
- Reviewer verdict populated;
- Final Report present;
- changed paths empty;
- no commit/push/merge/deploy;
- no `role_output_invalid`.

────────────────────────────────────
10. Final response
────────────────────────────────────

Return:

1. Overall PASS or FAIL
2. Whether stale code or current repaired code handled the failed task
3. Exact failing Reviewer field/path and sanitized reason
4. Whether truncation or token budget was involved
5. Whether schema repair was invoked and why it failed
6. Difference between successful smoke and failed full task
7. Exact local-agent files changed
8. Exact repair implemented
9. Focused test results
10. Full local-agent and UI test results
11. Reviewer-only replay result
12. Controlled full-rerun result, only if authorized by the gates above
13. Authentication probe result
14. Before/after tracked Git status
15. Confirmation that no Phase 2 source, branch, worktree, PR,
    credential, environment setting, or deployment changed
16. Whether the local agent is now qualified for full real Observe tasks
