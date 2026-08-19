# One-command project Observe

`observe-project.sh` runs a complete read-only qualification against a Git repository and immutable base ref.

It performs the following sequence:

1. validates the repository and task request;
2. loads the configured model provider;
3. creates a mirror-backed isolated sandbox;
4. indexes tracked files, instructions, architecture documents, ADRs, and tests;
5. compiles a bounded planner context;
6. creates a phase/slice plan;
7. runs fixed read-only Git checks;
8. invokes an independent reviewer;
9. writes the final report, plan, review, manifest, checks, and run summary;
10. verifies that both the sandbox and the original local repository remain unchanged.

The command never modifies source, stages files, commits, pushes, opens a pull request, merges, or deploys.

## Run with a site-owned model client

```bash
bash scripts/observe-project.sh \
  --repository /absolute/path/to/project \
  --ref feature/current-phase \
  --phase-id "Current implementation phase" \
  --focus "contract completeness" \
  --focus "test and compatibility evidence" \
  --host-client /absolute/path/to/site_model_client.py
```

When `--host-python` is omitted, the script searches parent `.venv/bin/python` and `venv/bin/python` locations above the host client.

The host client and its authentication remain outside the repository sandbox.

## Run with a complete task file

```bash
bash scripts/observe-project.sh \
  --repository https://github.com/example/project.git \
  --ref main \
  --task-file /absolute/path/to/task.md \
  --host-client /absolute/path/to/site_model_client.py
```

## Use another provider

```bash
bash scripts/observe-project.sh \
  --provider-factory site_provider:create_provider \
  --repository https://github.com/example/project.git \
  --ref main \
  --phase-id "Read-only qualification"
```

## Plan approval

Add `--require-plan-approval` to pause after planning. The task remains in the SQLite checkpoint store and can be resumed through the CLI with the printed thread ID.

## Successful infrastructure result

A safe completed run prints:

```text
UCA_PROJECT_PROVIDER_PROBE_PASS
UCA_PROJECT_OBSERVE_EXECUTION_PASS
SOURCE_REPOSITORY_PRESERVED
UCA_PROJECT_OBSERVE_PASS
```

The substantive result remains independent of infrastructure success and is printed separately:

```text
FINAL_STATUS=completed|blocked
REVIEWER_VERDICT=PASS|PASS_WITH_CONDITIONS|BLOCKED|FAIL
```

Artifacts are retained under a unique directory beneath:

```text
~/.uca-project-runs/
```

Important output paths include:

```text
run-summary.json
artifacts/tasks/<task-id>/final-report.json
artifacts/tasks/<task-id>/phase-plan.json
artifacts/tasks/<task-id>/review.json
artifacts/tasks/<task-id>/repository-manifest.json
artifacts/tasks/<task-id>/checks.json
sandboxes/<task-id>/repo/
```
