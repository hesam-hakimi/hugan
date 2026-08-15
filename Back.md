
DIAGNOSE AND REPAIR GPT-5.5 PLANNER REASONING-TOKEN BUDGET EXHAUSTION

Work only on the AskTD / KMAI local development agent.

Repository:

/app1/tag5916/projects/kmai-td-genie

Local tool:

.kmai-dev-agent

The previous Reviewer schema defect has been successfully repaired and
qualified:

- Reviewer-only real-model replay: PASS
- Reviewer verdict: PASS_WITH_CONDITIONS
- Reviewer output: schema-valid
- local-agent self-tests: 86/86 passed
- UI self-tests: 63/63 passed

A separate defect was discovered during the one controlled full
qualification run.

Observed failure:

- stage: Planner
- model profile: gpt55-quality
- actual deployment/model: gpt-5.5-2026-04-24
- maximumModelOutputTokens: 1200
- completion_tokens: 1200
- visible response content: empty
- accepted_prediction_tokens: 0
- surfaced error: json_parse_failed

Evidence indicates the entire output-token budget was consumed by model
reasoning, leaving no visible JSON Planner output.

This task is only for repairing that local-agent infrastructure defect.

Do not implement or remediate Phase 2C application findings.

────────────────────────────────────
1. Safety boundary
────────────────────────────────────

Allowed changes:

- `.kmai-dev-agent/**` only.

Do not modify:

- tracked AskTD source;
- tracked AskTD tests;
- tracked documentation;
- branches;
- worktrees;
- PRs;
- Git history;
- deployment configuration;
- application configuration;
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
- print raw model responses;
- expose private model reasoning;
- rerun the complete Phase 2C qualification before Planner-only replay
  passes.

Confirm first that `.kmai-dev-agent` remains ignored and untracked.

────────────────────────────────────
2. Locate the exact failed controlled run
────────────────────────────────────

Locate the most recent controlled full-qualification task that has:

- model profile `gpt55-quality`;
- Planner-stage failure;
- `json_parse_failed`;
- zero visible content;
- completion-token usage equal to the 1200-token budget.

Inspect only sanitized task artifacts and model-event metadata.

Record:

- task ID;
- model profile;
- requested deployment/alias;
- actual model;
- role;
- configured token budget;
- completion tokens;
- reasoning tokens when available;
- visible-content length;
- finish reason;
- repair-attempt count;
- final classification.

Do not print private reasoning or the raw response.

────────────────────────────────────
3. Confirm the root cause
────────────────────────────────────

Determine whether the failure was caused by:

A. reasoning-token budget exhaustion;

B. unsupported or incorrectly mapped request parameters;

C. response parsing before visible output was available;

D. Planner prompt/schema drift;

E. another evidenced cause.

Do not assume that increasing tokens is the only possible fix.

Inspect:

- `.kmai-dev-agent/policy.json`;
- model-profile role mappings;
- Planner invocation code;
- KMAI client request construction;
- output-token parameter mapping;
- reasoning-effort support;
- Planner parser and validator;
- retry and failure-classification logic.

Do not read or print credentials.

────────────────────────────────────
4. Replace the global fixed budget with bounded role/model policy
────────────────────────────────────

If confirmed by evidence, introduce a server-controlled, profile-aware,
role-aware output-budget policy.

The browser must not supply arbitrary token values.

The policy must support distinct bounded budgets for:

- search;
- planner;
- implementer;
- reviewer;
- repair;
- escalation.

Preserve the existing profile behavior.

For `gpt55-quality`, determine the smallest safe Planner budget through
bounded calibration rather than guessing.

Use a sanitized Planner fixture representative of the full workload.

Calibrate in bounded steps, for example:

- current budget;
- next bounded budget;
- one final higher bounded budget.

Stop at the first budget that returns:

- non-empty visible content;
- exactly one JSON object;
- schema-valid Planner output.

Do not exceed a documented local-agent maximum.

Do not run the full repository qualification during calibration.

────────────────────────────────────
5. Model-aware failure classification
────────────────────────────────────

When all available completion tokens are consumed and visible content is
empty, do not report only:

json_parse_failed

Classify it safely as something equivalent to:

model_output_budget_exhausted

Persist sanitized fields such as:

- role;
- profile;
- actual model;
- configured budget;
- completion-token count;
- reasoning-token count when available;
- visible-content length;
- finish reason.

Do not expose raw content or private reasoning.

The UI should show a useful safe message such as:

Planner produced no visible structured output because the configured
model-output budget was exhausted.

────────────────────────────────────
6. Bounded retry behavior
────────────────────────────────────

If budget exhaustion is conclusively detected:

- allow at most one bounded retry;
- use the next approved server-side budget for that profile and role;
- do not repeat the same request with the same exhausted budget;
- do not retry unrelated schema failures as budget failures;
- record the retry reason safely.

If the second attempt still has no visible output, fail closed.

No unbounded retries.

────────────────────────────────────
7. Planner output compactness
────────────────────────────────────

Review whether the Planner prompt requests unnecessary verbosity.

The schema-bound Planner output should remain concise and deterministic.

Detailed evidence should stay in persisted evidence artifacts and be
referenced by safe identifiers rather than duplicated extensively inside
the Planner JSON.

Do not remove required planning fields.

Do not weaken planning quality or safety gates.

────────────────────────────────────
8. Tests
────────────────────────────────────

Add focused tests for:

1. Existing Default profile and current budgets remain unchanged.
2. GPT-5.5 Planner receives the configured role-specific budget.
3. Browser cannot submit an arbitrary token budget.
4. Empty visible content with budget fully consumed is classified as
   model_output_budget_exhausted.
5. Empty output without proven exhaustion is not misclassified.
6. One bounded budget retry succeeds.
7. Second exhaustion fails closed.
8. Schema failures do not trigger a budget retry.
9. Valid Planner JSON is accepted.
10. Truncated Planner JSON remains rejected.
11. Planner output remains bounded and concise.
12. Historical tasks remain readable.
13. Task state records sanitized budget diagnostics.
14. UI displays safe diagnostics.
15. No raw model response or private reasoning is persisted.
16. Reviewer schema repair remains passing.
17. Existing fake Observe and Safe E2E remain passing.

Run:

- focused Planner/model-policy tests;
- Reviewer hardening tests;
- all local-agent self-tests;
- all UI self-tests;
- fake Observe E2E;
- fake Safe E2E;
- Python compilation;
- Bash syntax validation;
- authentication probe.

Expected authentication result:

KMAI_DEV_AGENT_AUTH_OK

────────────────────────────────────
9. Planner-only real-model replay
────────────────────────────────────

After all local tests pass, replay only the Planner stage using:

- the persisted full-qualification task input;
- the same `gpt55-quality` profile;
- the repaired role/model budget policy.

Do not rerun repository indexing or application tests.

Expected:

- visible content is non-empty;
- Planner JSON is schema-valid;
- Planner artifact is created;
- no json_parse_failed;
- no model_output_budget_exhausted after the bounded retry policy;
- no tracked AskTD changes.

If Planner-only replay fails, stop.

Do not run the full qualification.

────────────────────────────────────
10. Reviewer regression replay
────────────────────────────────────

After Planner-only replay passes, confirm the previously repaired
Reviewer-only replay still passes:

- schema-valid;
- verdict populated;
- no role_output_invalid.

────────────────────────────────────
11. One controlled full qualification
────────────────────────────────────

Only after both Planner-only and Reviewer-only replays pass, run one
complete Phase 2C Observe qualification.

Use:

Workspace:
/tmp/kmai-phase2c-semantic-plan

Branch:
phase2/semantic-plan-contract-validator

Autonomy:
observe

Model profile:
gpt55-quality

Expected:

- phase completed;
- Planner artifact present;
- evidence present;
- tests present;
- Reviewer artifact schema-valid;
- Reviewer verdict populated;
- Final Report present;
- changed paths empty;
- no commit/push/merge/deploy;
- no json_parse_failed;
- no role_output_invalid.

Do not perform application remediation.

────────────────────────────────────
12. Final response
────────────────────────────────────

Return:

1. Overall PASS or FAIL.
2. Exact root-cause classification.
3. Failed controlled-run task ID.
4. Original budget and sanitized token-usage evidence.
5. Whether request-parameter mapping was correct.
6. Exact local-agent files changed.
7. Role/model budget policy implemented.
8. Calibrated GPT-5.5 Planner budget and evidence for choosing it.
9. Failure-classification behavior.
10. Bounded retry behavior.
11. Focused test results.
12. Full self-test and UI-test results.
13. Planner-only replay result.
14. Reviewer regression replay result.
15. Controlled full-qualification result.
16. Authentication probe result.
17. Before/after tracked Git status.
18. Confirmation that no AskTD source, branch, worktree, PR, credential,
    environment setting, or deployment was changed.
19. Whether the Agent is now qualified for full real Observe tasks with
    the `gpt55-quality` profile.
