# Universal Coding Agent

A public, provider-neutral coding-agent control plane for long-running software-engineering work.

The project is designed for a central Linux service that accepts a Git repository and base branch, creates an isolated task sandbox, builds project context, plans complex work as phases and slices, runs read-only qualification, persists checkpoints, and produces independently reviewed evidence.

## Current milestone

**Phase 1: LangGraph Observe MVP**

Implemented in this milestone:

- repository URL + base ref input;
- isolated Git sandbox per task;
- tracked-file repository index;
- project instruction and ADR discovery;
- role-specific context compilation;
- hierarchical phase/slice planning;
- optional human plan-approval interrupt;
- read-only Git integrity checks;
- independent reviewer role;
- durable LangGraph checkpoints in SQLite;
- artifact references instead of large graph-state payloads;
- CLI run, resume, status, and provider probe commands;
- provider-neutral model contract with a host-factory adapter;
- deterministic fake provider for tests.

Not yet included:

- source modification;
- patch application;
- arbitrary command execution;
- commit, push, pull-request creation, merge, or deployment;
- Windows workers;
- multi-user web UI.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

LangGraph 1.2+ is used as the orchestration runtime. SQLite checkpoint support is included for local durable execution.

## One-command first smoke test

From the `universal-coding-agent` directory, run:

```bash
bash scripts/bootstrap-smoke.sh
```

The script performs the complete first qualification automatically:

1. verifies Python 3.11+;
2. creates or reuses `.venv`;
3. installs the package and development dependencies;
4. runs `pip check`, compilation, Ruff, and pytest;
5. probes the built-in deterministic fake provider;
6. clones the selected repository/ref into isolated task sandboxes;
7. executes a complete Observe workflow;
8. verifies the final report, reviewer verdict, and clean sandbox;
9. pauses a second task at the LangGraph approval interrupt;
10. resumes it from SQLite checkpoint state in a separate CLI invocation.

Successful completion ends with:

```text
UCA_BOOTSTRAP_SMOKE_PASS
```

The generated checkpoint database, artifacts, mirrors, and sandboxes are retained beneath a unique directory under:

```text
~/.uca-smoke-runs/
```

Override the repository, ref, or state path when needed:

```bash
bash scripts/bootstrap-smoke.sh \
  --repository https://github.com/example/project.git \
  --ref main \
  --state-root "$HOME/.uca-smoke/custom-run"
```

For an environment where the package and quality checks have already run:

```bash
bash scripts/bootstrap-smoke.sh --skip-install --skip-quality
```

The bootstrap smoke test uses only the built-in fake provider. It does not use site authentication, consume a real model, modify source, commit, push, create a pull request, merge, or deploy.

## Model provider

The agent core never knows how a site authenticates to its model service. It loads a provider factory through an environment variable:

```bash
export UCA_MODEL_PROVIDER_FACTORY='site_provider:create_provider'
```

The factory returns an object implementing `ModelProvider` from `universal_coding_agent.providers.base`.

A host adapter may reuse an existing client factory, Managed Identity, API gateway, OpenAI-compatible endpoint, or another approved authentication path. Provider credentials must never be copied into a repository sandbox.

## Probe the provider

```bash
uca probe
```

Expected generic result:

```text
AGENT_MODEL_PROVIDER_OK
```

## Run an Observe task

```bash
uca observe \
  --repository https://github.com/example/project.git \
  --ref main \
  --task-file task.md \
  --require-plan-approval
```

The initial invocation may pause at the plan-approval gate. Resume with:

```bash
uca resume --thread-id <thread-id> --decision approve
```

Reject with:

```bash
uca resume --thread-id <thread-id> --decision reject
```

## Durable state

By default, state is stored beneath `.uca-state/`:

```text
.uca-state/
├── checkpoints.sqlite
├── artifacts/
├── mirrors/
└── sandboxes/
```

The LangGraph checkpoint stores compact orchestration state. Plans, repository manifests, evidence, check results, reviews, and final reports are stored separately and referenced by immutable artifact IDs.

## Complex work

A planner produces a hierarchy:

```text
Program / objective
  -> Phase plan
    -> Slice DAG
      -> acceptance criteria
      -> dependencies
      -> recommended checks
      -> stop conditions
```

Each model role receives a fresh, bounded context compiled from project memory, the current phase/slice, relevant files, and artifact references. Raw model reasoning is not persisted.

## Safety model

- repository content is untrusted;
- no model or Git credential is placed in the sandbox;
- denied files are not indexed or sent to a model;
- subprocesses use explicit argument arrays with `shell=False`;
- Observe mode performs no source writes;
- repository and branch identity are pinned to an immutable base SHA;
- resume is tied to the same task/thread and checkpoint store;
- no commit, push, PR, merge, or deploy behavior exists in this milestone.

See [SECURITY.md](SECURITY.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
