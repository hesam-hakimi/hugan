Continue from DRAFT_PR_7_CI_PENDING.

Do not perform another blind 20-minute polling loop. Perform a one-shot, strict read-only queue diagnosis.

AUTHORITATIVE STATE

* Repository: TD-Universe/agentic_etl
* PR: #7
* Branch: feature/v3-agentic-redesign
* Head SHA: b2e44c3a1a051aa7fa6008931d225bc06d22e847
* Workflow run ID: 31634828341
* Job ID: 94242373290
* Check: workflow-contract
* Last observation: queued, no conclusion, no completed steps

No test failure has been demonstrated.

SAFETY RULES

* Use GET/read-only operations only.
* Do not rerun, cancel, approve, edit, dispatch, push, comment, or change Actions settings.
* Do not modify runners, runner groups, labels, permissions, billing, workflow files, or repository files.
* Do not create Commit 10.
* Do not click Keep or Undo.
* Leave all excluded unstaged files and worktrees untouched.
* Never display .env, GH, GH_TOKEN, headers, or credential-bearing URLs.
* Clear process-scoped GH_TOKEN in finally.

PHASE 1 — RECHECK CURRENT STATUS ONCE

Retrieve the current PR, workflow run, check-run, and job state.

If workflow-contract is now:

* completed/success: report the evidence and finish with:
    DRAFT_PR_7_CI_PASS_OBSERVED_CHECKS
* in_progress: report runner identity and start time, then finish with:
    DRAFT_PR_7_CI_NOW_RUNNING
* completed with failure, cancellation, timeout, or action-required: retrieve available logs using GET only, summarize the first actionable failure, and finish with:
    DRAFT_PR_7_CI_BLOCKED_<CONCLUSION>
* still queued: continue below.

PHASE 2 — RESOLVE JOB ROUTING

Using the workflow run and exact approved SHA:

1. Resolve the workflow file path and exact job definition for workflow-contract.
2. Read the workflow from the committed SHA, not from mutable worktree content.
3. Report only the relevant routing fields:
    * runs-on
    * resolved labels and runner group
    * matrix values affecting runs-on
    * workflow-level and job-level concurrency
    * needs
    * if
    * environment
4. Report these job API fields:
    * status and conclusion
    * labels
    * runner ID/name
    * runner-group ID/name
    * step statuses and timestamps

Do not treat started_at alone as proof of execution when the job is still queued, no runner is assigned, and no step has started.

PHASE 3 — FIND THE QUEUE CAUSE

1. Inspect up to the latest 20 runs of the same workflow.
2. Identify:
    * the last successful run;
    * its runner labels/name/group;
    * other queued or running jobs;
    * any run holding the same concurrency group.
3. If runs-on uses self-hosted/custom labels:
    * attempt read-only repository and organization runner inventory;
    * compare every required label as one complete set;
    * report runner status, busy state, and runner-group repository access.
4. If runner inventory returns 403, do not change the token or permissions. Record the sanitized response and classify visibility as insufficient.
5. If it uses a standard GitHub-hosted label:
    * inspect available evidence for concurrency saturation or an explicit Actions policy/billing restriction;
    * do not claim capacity, billing, or policy failure without direct evidence.
6. Inspect check-run output/annotations for an explicit scheduling, policy, billing, or approval message.

PHASE 4 — REPORT

Provide:

* exact workflow and job routing;
* runner labels/group required;
* historical comparison;
* direct evidence for the queue;
* root-cause classification and confidence;
* the smallest next human/admin action, without performing it.

Use one of these causes only when directly supported:

* NO_MATCHING_SELF_HOSTED_RUNNER
* MATCHING_RUNNER_OFFLINE
* MATCHING_RUNNERS_BUSY
* RUNNER_GROUP_ACCESS_MISMATCH
* CONCURRENCY_GATE
* EXPLICIT_ACTIONS_POLICY_OR_BILLING_GATE

Otherwise state that the cause remains unconfirmed.

Finally confirm that local HEAD, index, worktrees, excluded files, PR state, and review card remained unchanged.

Finish with exactly one:

* DRAFT_PR_7_QUEUE_DIAGNOSED_<EXACT_CAUSE>
* DRAFT_PR_7_QUEUE_DIAGNOSIS_INSUFFICIENT_VISIBILITY
* DRAFT_PR_7_QUEUE_STILL_INDETERMINATE
* one of the Phase 1 terminal classifications