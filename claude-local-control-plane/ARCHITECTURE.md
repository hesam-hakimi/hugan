# Architecture

## Trust model

The Orchestrator is the authority. Model output is a proposal or review result, never an enforcement decision by itself.

| Component | Trusted for |
|---|---|
| Milestone contract | Owner-approved product and path envelope |
| Task contract | Frozen task scope and acceptance criteria |
| Orchestrator | State transitions, identity, process creation, evidence, checks |
| Git | Canonical base, diff, and changed paths |
| Command hook | Pre-tool defense in depth |
| Planner | Semantic plan recommendation only |
| Implementer | Bounded file edits only |
| Verifier | Independent semantic verdict only |
| CI | Re-derived deterministic qualification |

## Lifecycle

```text
INTAKE
  -> BASELINE_CAPTURED
  -> PLANNING
  -> PLAN_READY
  -> IMPLEMENTING
  -> BOUNDARY_VERIFIED
  -> CHECKING
  -> IMPLEMENTED
  -> VERIFYING
  -> VERIFIED
  -> DOCUMENTATION_CHECKED
  -> DONE
```

Every state may fail closed to `BLOCKED`. Only a pre-mutation Planner failure is automatically resumable. A failure after the Implementer starts may have changed source and requires a new, explicitly approved repair task or manual owner disposition.

## Automatic handoff

The handoff is not a chat message. It is an HMAC-signed artifact containing:

- run and task IDs;
- immutable base SHA and task digest;
- source and destination roles;
- distinct source and destination session UUIDs;
- hashes of the artifacts being transferred;
- issuance time and nonce.

The Orchestrator validates the signature and identities before starting the next process. The signing key is generated under the repository Git metadata path and is never included in prompts.

## Product and architecture governance

Roadmap and architecture remain owner-authored sources. A milestone contract selects approved capabilities and defines the maximum path/check envelope. A task contract can only narrow that envelope. Planner and Verifier receive the same frozen sources and contracts.

CI can deterministically enforce identifiers, references, paths, checks, and documentation presence. Claude supplies semantic assessment, but cannot change the sources or broaden the approved envelope.

## Check execution

Agents have no Bash tool. Task contracts reference check IDs, and workspace configuration maps those IDs to exact argument arrays. The Orchestrator executes arrays with `shell: false`, fixed working directories, timeouts, bounded logs, and recorded exit codes.

This prevents a Planner or Implementer from inventing a shell command and disguising it as a required test.

## Portability

The folder is both:

- a Claude Code plugin loaded with `--plugin-dir`; and
- a standalone Node CLI with no runtime package dependencies.

It can be stored independently and used against another local Git repository. Nothing requires GitHub Agent access, an Anthropic key in CI, or deployment permissions.
