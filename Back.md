DIAGNOSE AND REPAIR LOCAL KMAI DEVELOPMENT AGENT ROLE_OUTPUT_INVALID

A real Observe-mode qualification task failed inside the local
`.kmai-dev-agent`.

Task:

Phase 2C Acceptance Audit Remediation Planning

Verified runtime facts:

- Workspace:
  /tmp/kmai-phase2c-semantic-plan

- Branch:
  phase2/semantic-plan-contract-validator

- Autonomy:
  observe

- Model profile:
  Existing Default

- Requested model alias:
  complex-reasoning-configured

- Actual model:
  gpt-4o-2024-08-06

- Worktree was clean and verified during the task.

- The task reached:
  running_regression_tests
  → reviewing
  → failed

- Final error:
  role_output_invalid

- Activity evidence:
  reviewer_started
  followed by
  role_output_invalid

- git-diff-check exited 0.

- No project source change was introduced.

The purpose of this task is to diagnose and repair the local agent
infrastructure failure. Do not perform Phase 2C remediation.

────────────────────────────────────
1. Safety boundaries
────────────────────────────────────

Allowed modifications:

- locally ignored `.kmai-dev-agent/**` only.

Do not modify:

- tracked application source;
- application tests;
- tracked documentation;
- branches;
- worktrees;
- pull requests;
- Git history;
- environment configuration;
- authentication configuration.

Do not:

- commit;
- push;
- merge;
- rebase;
- deploy;
- install packages;
- expose credentials;
- rerun the full real Phase 2C task until the infrastructure defect has
  been reproduced and repaired.

Confirm `.kmai-dev-agent` is ignored and contains no tracked file before
editing.

────────────────────────────────────
2. Inspect the failed task evidence
────────────────────────────────────

Locate the persisted state, events and sanitized role artifacts for the
failed task.

Identify exactly:

1. which role produced the invalid output:
   - planner;
   - reviewer;
   - another role;

2. which schema validator rejected it;

3. the precise safe validation failure:
   - invalid JSON;
   - missing required property;
   - extra forbidden property;
   - invalid enum;
   - wrong data type;
   - nullability mismatch;
   - code-fence wrapping;
   - explanatory text surrounding JSON;
   - truncated output;
   - token exhaustion;
   - incorrect role schema;
   - parser defect;
   - another identified reason.

Do not print private reasoning, credentials, prompts containing sensitive
repository content, or the complete raw model response.

Return only a sanitized structural summary and validation path.

────────────────────────────────────
3. Reproduce minimally
────────────────────────────────────

Build the smallest deterministic reproduction using:

- the same role schema;
- the same parser/validator;
- a sanitized fixture shaped like the failed output;
- no real repository modification;
- no external action.

Prove the reproduction fails with the same `role_output_invalid`
classification.

Check whether the existing bounded schema-repair retry was:

- invoked;
- skipped;
- exhausted;
- incompatible with the failure;
- incorrectly configured.

────────────────────────────────────
4. Inspect the role-output contract
────────────────────────────────────

Review:

- Planner output schema;
- Reviewer output schema;
- role prompts;
- structured-output request parameters;
- output parsing;
- code-fence removal;
- JSON extraction;
- schema-repair retry;
- maximum output-token settings;
- failure classification;
- UI event/state propagation.

Check for contract drift between:

- prompt instructions;
- expected JSON schema;
- Pydantic/dataclass/manual validator;
- persisted role artifact;
- UI parser.

Do not weaken required safety fields merely to make the model pass.

────────────────────────────────────
5. Implement the smallest safe repair
────────────────────────────────────

The repair may include, only when supported by evidence:

- deterministic stripping of Markdown code fences;
- extraction of exactly one JSON object;
- rejection of ambiguous multiple JSON objects;
- bounded repair of syntactic JSON defects;
- one bounded schema-repair model retry;
- explicit missing-field repair instructions;
- enum normalization only when the mapping is unambiguous;
- sufficient role output-token budget;
- correct structured-output request configuration;
- corrected prompt/schema alignment;
- improved sanitized validation diagnostics.

Requirements:

- preserve fail-closed behavior;
- never accept incomplete evidence as PASS;
- never invent required findings;
- never expose private chain-of-thought;
- never return raw malformed model text to the browser;
- never silently discard required fields;
- cap all retries;
- record the exact repair reason in sanitized task events.

────────────────────────────────────
6. Tests
────────────────────────────────────

Add focused local-agent tests for:

1. valid Planner output;
2. valid Reviewer output;
3. JSON wrapped in one Markdown code fence;
4. leading/trailing explanatory text;
5. missing required field;
6. forbidden extra field;
7. invalid enum;
8. truncated JSON;
9. multiple JSON objects;
10. schema-repair success;
11. schema-repair exhaustion;
12. output remains invalid and fails closed;
13. no private reasoning appears in events;
14. UI receives a useful sanitized validation error;
15. final Reviewer PASS is accepted only from a schema-valid output.

Run:

- focused role-schema tests;
- local-agent self-tests;
- fake-repository Observe E2E;
- fake-repository Safe E2E;
- UI self-tests;
- Python compilation;
- Bash syntax validation;
- authentication probe.

Expected authentication result:

KMAI_DEV_AGENT_AUTH_OK

────────────────────────────────────
7. Controlled real smoke test
────────────────────────────────────

After all local and fake-repository tests pass, run a small real
Observe-only smoke task against the clean Phase 2C worktree.

The smoke task should only ask the Agent to return:

- repository branch;
- HEAD;
- applicable Phase 2 ADR paths;
- confirmation that no tracked source file changed.

It must exercise:

- Planner;
- repository evidence;
- Reviewer;
- schema validation;
- final report.

Do not yet rerun the complete Phase 2C remediation-planning task.

Expected:

- Planner output valid;
- Reviewer output valid;
- Reviewer verdict present;
- Final Report present;
- no tracked change;
- no `role_output_invalid`.

────────────────────────────────────
8. Final response
────────────────────────────────────

Return:

1. Overall PASS or FAIL
2. Exact failing role
3. Exact sanitized schema-validation failure
4. Why the existing repair mechanism did not recover
5. Exact local-agent files changed
6. Repair implemented
7. Focused-test results
8. Full self-test results
9. Fake E2E results
10. Real Observe smoke-test result
11. Probe result
12. Before/after tracked Git status
13. Confirmation that no application source, branch, worktree, PR,
    credential, environment setting or deployment was modified
14. Whether the original Phase 2C Observe task is now safe to rerun

Do not perform Phase 2C remediation in this task.
