# Operations

## Owner workflow

The owner approves a milestone once, including capabilities, maximum paths, prohibited paths, architecture references, roadmap references, and named checks. Tasks inside that envelope can run without per-agent copying or handholding.

Runnable task contracts must remain outside the target Git worktree because their exact `expectedBaseSha` cannot self-reference the commit containing the contract. The Orchestrator records and verifies their digest.

Owner involvement remains required when:

- a task needs scope outside the milestone envelope;
- product priority or architecture must change;
- a protected governance path must change;
- a run becomes BLOCKED after implementation begins;
- a risk is deferred or accepted;
- merge, package, installation, runtime QA, deployment, or release is requested.

## Safe recovery

Use `status` after interruption. The state reports `resumeAllowed`.

- `true`: no source mutation occurred; `resume` creates a new Planner session and continues from the frozen baseline.
- `false`: source may have changed. Do not replay the Implementer. Inspect the diff and create a new repair task or explicitly discard/recover changes outside this tool.

The CLI never runs `git reset`, `git checkout`, `git clean`, or an automatic rollback.

## Agentless CI adoption

Use the template under `templates/github-workflows/agentless-pr-quality-gates.yml` as a starting point. CI should:

1. check out the PR head;
2. validate the control-plane/plugin files;
3. run deterministic project compile/lint/tests;
4. re-run architecture/path/documentation validators appropriate to the target project;
5. upload evidence without invoking Claude;
6. require human/environment approval for downstream delivery.

Repository administrators may need to enable Actions and register these jobs as required status checks. No Claude Agent, API key, deployment secret, or environment permission is needed for PR qualification itself.
