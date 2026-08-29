# ETL Framework Extension — Workflow, Agents, and Safety Contract

## 1. End-to-end product workflow

```text
Install exact VSIX
→ activate and verify live version
→ open exactly one intended consumer workspace
→ provision managed workflow assets when required
→ select ETL Orchestrator
→ resolve workspace and STTM
→ inspect consumer artifacts and trusted contracts
→ ask only genuinely missing decisions
→ classify create/update/scaffold/block
→ render one canonical artifact set in memory
→ validate deterministically
→ create zero-write Preview
→ independently verify Preview
→ obtain explicit approval for that exact Preview
→ re-prove root, paths, bytes, and containment
→ write the approved artifact set once
→ validate, record ownership, and audit
→ independently verify post-state
→ optionally execute an external runtime action under a separate approval
```

`@etl /workflow` is a provisioning/update action. It is not a passive diagnostic, ordinary Preview command, or Runtime QA shortcut.

## 2. Two Agent systems

Do not confuse maintainer/source-governance Agents with consumer runtime Agents.

| System | Location | Purpose |
|---|---|---|
| Source-governance Agents (`SG:*`) | Extension repository `.claude/agents/**` | Implement, independently review, verify, and package the Extension |
| Consumer Agents (`CA:*`) | Consumer workspace `.github/agents/**` | Plan, implement, verify, diagnose, research, and operate ETL solutions |

Source-governance examples:

- `SG:etl-hotfix-implementer`;
- `SG:etl-independent-reviewer`;
- `SG:etl-release-verifier`.

Consumer Agents:

- `CA:ETL Orchestrator`;
- `CA:ETL Implementer`;
- `CA:ETL Verifier`;
- `CA:ETL Runtime Troubleshooter`;
- `CA:ETL Evidence Researcher`;
- `CA:ETL Operator`.

## 3. Consumer Agent topology

`ETL Orchestrator` is the only directly user-invocable ETL Agent. The other five declare `user-invocable: false` and are internal delegates, not disabled Agents.

| Agent | Responsibility | Important prohibition |
|---|---|---|
| ETL Orchestrator | Coordinate interpretation, planning, delegation, approval state, and reporting | Cannot treat tool possession or delegation as approval |
| ETL Implementer | Apply an accepted plan to authorized workspace artifacts | Cannot approve or independently certify its own work; no external runtime action |
| ETL Verifier | Independently inspect artifacts, validation, Preview/write readiness, and evidence | Read-only; no edit, deploy, run, or self-remediation |
| ETL Runtime Troubleshooter | Diagnose failed runs and remediation options | Cannot run, retry, deploy, edit, or approve |
| ETL Evidence Researcher | Retrieve cited historical Jira/Confluence evidence | Read-only; no ETL or external mutation |
| ETL Operator | Execute an exact separately approved Databricks/ADF/runtime action | Cannot plan, approve, or execute without exact approval |

Invariants:

- exactly one user-facing ETL Agent;
- exactly five internal specialists;
- delegation does not grant authority;
- a declared tool is only a maximum technical envelope;
- Bypass Permissions does not replace product approval;
- no Agent self-approves or self-certifies.

## 4. Canonical candidate manifest

All artifact destinations and bytes must be produced once and frozen:

```text
selected root + task evidence + trusted contract
→ canonical candidate artifact set
→ deterministic validation
→ Preview record
→ approval bound to the same set
→ writer consumes the same paths and bytes
```

No downstream layer may independently recalculate a path, artifact type, disposition, or content. Any change requires a new Preview.

## 5. Preview and approval state machine

```text
rendered → previewed → approved/declined → writing → consumed/failed
```

A trusted Preview record binds:

- random opaque Preview ID;
- bounded TTL;
- selected workspace root;
- target decision;
- session/conversation identity;
- exact artifact types and sorted paths;
- exact bytes or trusted hashes;
- per-file and manifest checksums;
- one-time state.

The first call validates and issues a Preview but writes zero files. Approval must occur through the Extension-owned store. The write call must consume the exact approved candidate once.

Reject missing, forged, expired, replayed, or mismatched IDs; changed roots, paths, bytes, artifact sets, or manifests; concurrent consumption; and post-preview path substitution.

## 6. Root and filesystem safety

Never choose a destination from:

- `process.cwd()`;
- the Extension source or installed Extension directory;
- the Framework source;
- the first folder in a multi-root workspace;
- the active editor;
- a stale session path;
- packaged samples or documentation roots;
- a folder-name heuristic.

Lexical containment is insufficient because a child path can be a symlink, junction, or reparse point. Immediately before mutation, the shared containment primitive must walk to an existing ancestor, use `lstat` and native `realpath`, preserve platform case behavior, reject sibling-prefix confusion, and block link/reparse/hard-link/TOCTOU escape.

No `mkdir` or write occurs before this proof.

## 7. Runtime QA evidence contract

Runtime QA must use the tools actually declared by the installed consumer Agent. Do not silently substitute shell, Git, PowerShell, hashing, or a user-run command when the Agent does not have that capability.

If hash capability is absent:

- use the complete Agent/tool invocation audit;
- prove that no write-capable call occurred;
- compare tool-visible before/after inventory;
- do not claim byte-for-byte equality.

Preview-only QA must not invoke Implementer or Operator unless the scenario explicitly requires them. External Databricks/ADF effects require a separate controlled environment and explicit action approval.

## 8. Repair 13 authority and diagnostic contract

The consumer-visible `etl_interpret_sttm` result has two coordinated channels:

- rendered Markdown;
- structured data, including parser diagnostics and affected row identities.

Required behavior:

- structured and Markdown Active Mapping IDs match in content and order;
- counts match;
- positive active state grants authority;
- inactive state does not block solely because it is inactive;
- conflicts are excluded and disclosed;
- historical, unknown, unsupported, blank, or undeclared states gain no authority;
- undeclared state fails closed;
- malformed short/oversized rows fail closed and carry deterministic row identity;
- unresolved authority-critical references are disclosed and non-authoritative;
- no diagnostic text may leak an authoritative source attribute value;
- no Preview, approval, write, deployment, or runtime authority is broadened.

## 9. Non-negotiable safety invariants

1. Resolve the exact root before reading or writing.
2. One root or explicit trusted selection; never first-folder fallback.
3. Preview writes nothing.
4. Approval is Extension-owned and exact-manifest bound.
5. Write consumes the same paths and bytes once.
6. Physical containment is re-proven immediately before mutation.
7. Normal consumer operation does not require Framework source.
8. Advisory context cannot become machine authority.
9. Unsupported provider behavior fails clearly.
10. Tests write only inside disposable roots and use synthetic data.
11. Agent/tool capability is distinct from authorization.
12. Implementer and producer cannot certify their own output.

