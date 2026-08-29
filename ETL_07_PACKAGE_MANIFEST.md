# ETL Framework Extension — Handoff Package Manifest

**Package date:** 2026-08-29  
**Purpose:** durable transfer of project understanding and the exact next gate to a fresh session

## Included documents

| File | Primary question answered |
|---|---|
| `ETL_00_START_HERE.md` | What is the current one-minute state and what should be read first? |
| `ETL_01_PRODUCT_PROJECT_AND_ARCHITECTURE.md` | What are ETL FW and the Extension, and what does each own? |
| `ETL_02_WORKFLOW_AGENTS_AND_SAFETY_CONTRACT.md` | How does the product work and what safety rules are non-negotiable? |
| `ETL_03_IMPLEMENTED_CAPABILITIES_AND_EVIDENCE.md` | What has been implemented and what evidence supports it? |
| `ETL_04_CURRENT_STATE_OPEN_WORK_AND_NEXT_GATE.md` | What remains open and what is the immediate next task? |
| `ETL_05_CHRONOLOGY_DECISIONS_RISKS_AND_GLOSSARY.md` | How did the project reach this point and what decisions/risks must persist? |
| `ETL_06_NEW_SESSION_MASTER_PROMPT.md` | What exact prompt should be run in the next implementation session? |
| `ETL_07_PACKAGE_MANIFEST.md` | Is the handoff set complete and how should it be transferred? |
| `ETL_08_CURRENT_STATE_MACHINE_READABLE.json` | What is the same current state in a deterministic machine-readable form? |

## Coverage checklist

| Required handoff topic | Covered in |
|---|---|
| ETL Framework definition | `ETL_01` |
| Extension/product definition | `ETL_01` |
| Framework vs Extension ownership | `ETL_01`, `ETL_02` |
| Environment model | `ETL_01` |
| Consumer artifacts and configuration | `ETL_01` |
| End-to-end workflow | `ETL_02` |
| Source-governance vs consumer Agents | `ETL_02` |
| Agent responsibilities and authority | `ETL_02` |
| Preview/approval/write contract | `ETL_02` |
| Workspace and physical containment | `ETL_02` |
| Repairs 3–8 | `ETL_03` |
| Repairs 11–13 | `ETL_03` |
| Phase-H refresh | `ETL_03` |
| `0.3.146` package evidence | `ETL_03` |
| Current governance blockers | `ETL_04` |
| Exact eight-file next boundary | `ETL_04`, `ETL_06` |
| Runtime QA still outstanding | `ETL_04` |
| Pre-merge/release backlog | `ETL_04`, `ETL_05` |
| Accepted owner decisions | `ETL_05` |
| Risk register and glossary | `ETL_05` |
| Copy/paste new-session prompt | `ETL_06` |
| Machine-readable identity, blockers, boundary, and stop conditions | `ETL_08` |

## Evidence basis and limits

This package reconciles:

- the durable Library handoff set dated 2026-08-24 and its 2026-08-27 consumer-Agent addendum;
- later source/package/independent-review reports for Repairs 11–13 and versions `0.3.145`–`0.3.146`;
- the final exact-package verification report;
- the latest package-lifecycle governance investigation, which ended with zero edits because the original boundary was incomplete.

It is a handoff snapshot, not live repository evidence. The next Agent must re-run identity, status, baseline, and test gates before mutation. Screenshot-derived values are intentionally described as reported evidence and not promoted above live executable state.

## Transfer procedure

For a fresh session:

1. Attach or reference this complete folder.
2. Ask the Agent to read `ETL_00_START_HERE.md` first and then follow its read order.
3. Open the Extension source repository, not a consumer workspace.
4. Start a generic maintainer implementation Agent, not `ETL Orchestrator`.
5. Paste `ETL_06_NEW_SESSION_MASTER_PROMPT.md` only after the documents are available.
6. Require the identity/baseline report before the first edit.
7. If implementation passes, open a second fresh session for independent review.
