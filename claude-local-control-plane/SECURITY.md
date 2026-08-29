# Security and Safety Contract

## Invariants

1. Repository content is untrusted input.
2. Every new run starts from a clean worktree and exact 40-character base SHA.
3. A task may narrow but never widen its milestone envelope.
4. Planner and Verifier are read-only.
5. Implementer can use file tools only inside authorized paths.
6. No model role receives Bash, nested Agent, web, MCP, Git, package, install, deployment, or runtime authority.
7. A full worktree hash snapshot plus Git, not an agent declaration, determines changed paths and canonical diff, including ignored files.
8. Named checks are exact owner-configured argument arrays executed with `shell: false`.
9. Planner, Implementer, and Verifier have distinct process/session UUIDs.
10. The Implementer cannot certify its own work.
11. Required documentation is a deterministic gate.
12. No automatic repair/retry loop occurs after source mutation.
13. The control plane never commits, pushes, opens/merges a PR, packages, installs, deploys, or starts runtime QA.

## Hook coverage

The plugin `PreToolUse` hook denies:

- all Bash and nested Agent calls;
- web operations;
- writes outside `IMPLEMENTING`;
- writes outside task-authorized paths;
- writes to prohibited paths;
- reads/writes beneath `.git` and control-plane state;
- paths resolving outside the project through symlinks.

Hooks are defense in depth. The Orchestrator independently checks the post-edit Git diff and fails closed even if a hook was unavailable or misconfigured.

## Prompt injection

Each role is told that repository instructions cannot alter its authority or output contract. Tool availability is fixed by the spawning process, so a malicious repository file cannot grant Bash, network, nested-agent, or certification capability.

## Secrets

The HMAC key is stored beneath the repository's Git metadata path. It is not written to the worktree, passed in a prompt, logged, or committed. Agent processes receive only an ephemeral hook nonce; model roles have no shell tool to enumerate environment variables.

## Residual risks

- A compromised local user account can alter the CLI, Git repository, Claude binary, or state.
- Semantic verification is probabilistic; deterministic tests and human milestone/release gates remain required.
- A task with an overly broad owner-approved path envelope remains overly broad. Contracts should use the smallest practical scope.
- Enterprise-managed Claude settings may add restrictions. They must not be bypassed.
