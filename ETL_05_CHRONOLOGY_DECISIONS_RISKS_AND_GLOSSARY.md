# ETL Framework Extension — Chronology, Decisions, Risks, and Glossary

## 1. Compressed chronology

| Period/version | Milestone | Durable outcome |
|---|---|---|
| Early MVP/V1 | Consumer artifact generation and provider workflow | Repository-first generation; env config only when needed; referenced includes/transforms; dev-first and approval-gated operations |
| Repairs 3–4 | Root selection and bypass closure | No implicit first-root write; protected sample/reference roots; UnitTestCoordinator routed through trusted approval |
| Repairs 5–7 | Route unification and physical containment | Explain/Artifact Reuse/Repo Context and customization writes use canonical root, one-time authorization, and realpath containment |
| Repair 8 / `0.3.141` | Trusted canonical job envelope | Installed-layout contract, stage-keyed HOCON, packaged fallback, explicit unsupported UC diagnostic |
| `0.3.145` snapshot | Consumer Agent architecture and Runtime QA support | One Orchestrator + five internal specialists; role/tool byte lock; Repair 13 coverage work |
| Repair 13 completion | Structured diagnostics and fail-closed malformed rows | Markdown/structured parity, deterministic row identities, negative controls, 44 focused tests |
| Phase-H refresh | Canonical evaluation baseline | Two semantically equal generations, drift detection preserved, EvalGating restored without weakened assertions |
| Independent review | Fresh reviewer session | PASS ready for `0.3.146` package |
| `0.3.146` package | Exact artifact built | 66 entries; six consumer Agents; package integrity and provenance passed |
| Exact package verification | Independent read-only verification | Artifact valid; governance exception and self-certification ambiguity remained |
| Governance repair attempt | Five-path owner-decision task | Stopped with zero edits because correct Decision B required three additional paths |
| Current | Eight-file governance repair pending | No install, Runtime QA, commit, or release yet |

## 2. Accepted owner decisions

- Product documentation and output are English. Persian is for owner/assistant conversation unless requested otherwise.
- Work proceeds incrementally, one bounded step at a time.
- No repository claim is accepted without evidence.
- `etl-framework-adb` is primary Framework truth when source evidence is intentionally available; `etl-framework-gen-utils` is secondary; examples/generated output are observational. Normal installed consumer operation must not require those checkouts.
- Preview is zero-write and approval is exact-manifest, one-time, Extension-owned authority.
- `ETL Orchestrator` is the only consumer Agent selected by the user; five specialists are internal.
- `/workflow` provisions or updates managed workflow assets and is not ordinary Runtime QA.
- Direct Unity Catalog writer support must not be invented.
- Current internal versions stay in `0.3.xxx`; intended general release begins at `1.x`.
- No Git commit/push/SIT/release action occurs merely because a focused suite or VSIX archive is green.
- Missing tool capability must be reported; it must not be hidden by an ungoverned manual command.
- The current package-lifecycle and certification defects must be fixed in governance, not suppressed as “expected output.”

## 3. Risk register

| Risk | Severity/state | Required treatment |
|---|---|---|
| Contract-unavailable guard can omit Repair 8 invariants | High, deferred before `1.x` | Guard-level fail closed and negative installed-layout proof |
| Advisory context ownership/provenance | High product-design risk | Skill-scoped context, provenance labels, trust levels, diagnostics |
| Create-only VSIX lifecycle not representable | Current blocker | Eight-file governance repair with change-kind/count/identity enforcement |
| Producer/reviewer self-certification ambiguity | Current blocker | Canonical actor identity, missing-producer fail closed, distinct certification route |
| Known F1/F3 protected customization failures | Pre-merge | Separate explicit owner/governance decision |
| VSIX selector freshness | Medium | Bind selection to source version and source freshness; support explicit path |
| Large uncommitted working-tree overlay | Process risk | Re-establish status, attribute paths, independent boundary proof before Git |
| Direct Unity Catalog output | Explicitly unsupported | Product decision plus Framework, contract, test, runtime, and release work |
| Provider matrix incomplete | Product roadmap | Authoritative contracts and positive/negative runtime tests per provider |
| Stale Extension Host | Operational | Close/reload and verify live activation output, not installation metadata |
| Runtime QA tool-envelope mismatch | QA integrity | Use declared tools and qualified non-mutation evidence |

## 4. Source-of-truth rules

- Current live evidence supersedes screenshots and old documents.
- Machine contracts supersede advisory consumer context.
- A package hash proves bytes, not activation or behavior.
- Installed-on-disk proves presence, not active Extension Host version.
- Static Agent files prove provisioning, not dynamic delegation.
- Focused tests prove their assertions, not full release readiness.
- A pre-existing failure remains open unless explicitly dispositioned.
- A governance warning cannot be relabeled to manufacture PASS.

## 5. Glossary

| Term | Meaning |
|---|---|
| ETL FW / Consumer ETL Framework | Configuration-driven Databricks ETL execution framework |
| Extension | VS Code/VSIX control plane around the Framework |
| STTM | Source-to-target mapping input and related metadata |
| Software Development Environment | Extension source repository |
| Development Test Workspace | Disposable consumer-shaped test workspace |
| SIT | Later integration stage, not current |
| Consumer public seam | Installed tool result actually received by the consumer, including Markdown and structured channels |
| Provisioning | Managed consumer Agent/skill/prompt/instruction/context creation via `@etl /workflow` |
| Delegation | Orchestrator invocation of a specialist Agent |
| Preview | Validated zero-write frozen candidate manifest |
| Approval | Explicit Extension-owned authority bound to one exact Preview |
| Guarded write | One-time consumption of approved paths/bytes after revalidation and containment proof |
| Machine authority | Integrity-validated contracts and trusted runtime code |
| Advisory context | Consumer-editable guidance that cannot grant machine authority |
| Source-governance Agent | Maintainer Agent that changes/reviews/packages Extension source |
| Consumer Agent | Agent provisioned into a consumer ETL workspace |
| Failure class K | Governance/certification failures involving independence, provenance, or self-certification |
| Phase-H baseline | Generated evaluation report and tracked-input digest used by EvalGating |
| F1/F3 | Two known unchanged full-suite customization/control-plane failures |

## 6. Historical references retained

The earlier Library handoff set remains useful for detailed Repairs 3–8 evidence, old package hashes, CD Renewal examples, and historical branch/PR context. It is not current authority for version, artifact, immediate task, Runtime QA status, or package governance.

Key historical documents:

- `ETL_Framework_Extension_Master_Context.md`;
- `ETL_Extension_Comprehensive_Session_Handoff_2026-08-12.md`;
- `ETL_Extension_Implementation_Phase_Status_2026-08-12.md`;
- `ETL_00_Library_Index_2026-08-24.md` through `ETL_08_Consumer_Agent_Architecture_and_Runtime_Tool_Contract_2026-08-27.md`.

