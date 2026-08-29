# Local Claude Agent Control Plane

This folder implements automatic, local handoff between independent Claude Code roles without requiring a cloud coding agent or an AI-enabled CI/CD runner.

One deterministic command launches three fresh Claude Code processes in sequence:

```text
Planner (read-only)
  -> signed handoff
Implementer (bounded file edits, no shell)
  -> deterministic Git boundary + approved checks
  -> signed handoff
Verifier (fresh, read-only, independent)
  -> terminal evidence
```

Claude is used for semantic work: product alignment, architecture reasoning, implementation, and independent review. Node scripts and Git provide the security boundary, lifecycle, exact path enforcement, check execution, identity separation, durable state, and evidence integrity.

## Why this design

Previous agent workflows repeatedly failed when:

- the next agent depended on a user copying a long prompt;
- agent names were treated as proof of independence;
- preview, validation, and write recalculated different paths;
- agents widened scope after discovering a missing file;
- tests wrote into protected maintainer paths;
- one role both produced and certified an artifact;
- a failed agent was resumed after partial edits without a new baseline;
- free-form shell commands were trusted as part of the plan;
- documentation and roadmap status drifted away from implementation.

This implementation addresses those failures with one frozen task contract, milestone-preapproved envelopes, separate OS processes and UUIDs, HMAC-signed handoffs, no shell access for model roles, exact named checks executed outside the model, fail-closed hooks, and no automatic repair loop.

## Requirements

- Git
- Node.js 20+
- Claude Code with support for `--agent`, `--plugin-dir`, `--json-schema`, `--session-id`, and `--tools`
- a clean Git worktree for a new run

The automated tests do not require Claude Code or an Anthropic credential. They use a fake runner.

## Verify this control plane

```bash
cd claude-local-control-plane
npm run verify
```

When Claude Code is installed, also validate the plugin with:

```bash
claude plugin validate .
```

## Adopt in a target repository

1. Copy `templates/workspace/lcac.config.json`, the product roadmap, architecture contract, and milestone into owner-approved locations in the target repository. Keep runnable task contracts in a local sidecar directory or separate governance repository, not tracked in the target worktree.
2. Replace every placeholder.
3. Set each external task's `expectedBaseSha` to the exact current `git rev-parse HEAD`.
4. Keep task path patterns and check IDs inside the approved milestone envelope.
5. Run validation before invoking Claude.

```bash
node /path/to/claude-local-control-plane/scripts/lcac.mjs validate \
  --project /path/to/repository \
  --config /path/to/lcac.config.json \
  --milestone /path/to/M1.json \
  --task /path/to/CAP-001-T1.json
```

Run the full automatic handoff:

```bash
node /path/to/claude-local-control-plane/scripts/lcac.mjs run \
  --project /path/to/repository \
  --config /path/to/lcac.config.json \
  --milestone /path/to/M1.json \
  --task /path/to/CAP-001-T1.json
```

PowerShell uses the same arguments:

```powershell
node C:\tools\claude-local-control-plane\scripts\lcac.mjs run `
  --project C:\repos\product `
  --config C:\repos\product\governance\lcac.config.json `
  --milestone C:\repos\product\governance\milestones\M1.json `
  --task C:\lcac-workspaces\product\tasks\CAP-001-T1.json
```

## Commands

| Command | Behavior |
|---|---|
| `validate` | Validates contracts, milestone subsets, source references, Git identity, and clean baseline without invoking Claude. |
| `run` | Executes the complete approved Planner → Implementer → checks → Verifier lifecycle. |
| `status` | Reads durable state and evidence; never invokes an agent. |
| `resume` | Resumes only a safe pre-mutation Planner failure. |
| `verify-installation` | Checks Node, Git, Claude CLI, plugin files, schemas, and target configuration. |

## Automatic does not mean uncontrolled

An approved task automatically hands off from one role to the next. The Orchestrator stops before or during handoff when it detects:

- base SHA or branch drift;
- a dirty starting worktree;
- milestone/task mismatch;
- capability, roadmap, architecture, path, or check scope expansion;
- Planner ambiguity or BLOCKED status;
- an unauthorized or prohibited changed path;
- an Implementer declaration that disagrees with Git;
- a failed required check;
- duplicate session identity;
- a Verifier reviewing a different diff digest;
- missing required documentation;
- any malformed or unsigned artifact.

It does not commit, push, create or merge a PR, package, install, deploy, or run environment QA.

## CI/CD relationship

The local control plane produces reviewable source changes and evidence. CI remains agentless: it should re-run deterministic validators, compile/lint/tests, boundary checks, and documentation checks. Deployment remains under the authority of the team that owns credentials and environments.

See [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), and [OPERATIONS.md](OPERATIONS.md).

The full design, existing-Agent reuse rules, and the honest boundary between task automation and later milestone automation are in [DESIGN.md](DESIGN.md).
