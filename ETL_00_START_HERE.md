# ETL Framework Extension — Session Handoff — Start Here

**Snapshot date:** 2026-08-29  
**Audience:** a fresh implementation/review Agent or a maintainer joining without prior chat history  
**Product language:** English  
**Conversation language with the owner:** Persian is preferred unless the owner asks otherwise

## 1. One-minute summary

This project has two cooperating products:

1. **Consumer ETL Framework** — a configuration-driven Databricks ETL execution framework. It consumes STTM and configuration artifacts and executes source, transformation, load/enrichment, and writer stages.
2. **Databricks ETL Copilot Extension** — a VS Code VSIX that exposes `@etl`, `/workflow`, ETL tools, and a managed six-Agent consumer workflow. It resolves the selected consumer workspace, interprets STTM, decides create/update/scaffold, renders and validates artifacts, creates a zero-write Preview, obtains exact approval, performs guarded writes, and supports audit/repair/upgrade workflows.

The current implementation line is `hotfix/hf1-oracle-fresh-consumer-v2`. Repairs 3–8 hardened workspace selection, trusted Preview/Approval, physical write containment, package hygiene, and canonical job-config generation. Later Repairs 11–13 added and validated STTM authority behavior, a dual Markdown/structured diagnostic channel, malformed-row fail-closed behavior, and consumer-Agent guidance.

The latest reported package is `0.3.146`. Its archive content passed exact package verification and independent inspection. **The package must not yet be installed or used for Runtime QA** because package-lifecycle governance still blocks creation of a new `*.vsix` artifact and the source-governance certification model still has a producer/reviewer ambiguity.

The last governance-repair attempt made **zero repository changes** and ended:

```text
PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_REQUIRED_CHANGE_OUTSIDE_BOUNDARY
```

The next implementation task should authorize the complete eight-file governance boundary described in `ETL_04_CURRENT_STATE_OPEN_WORK_AND_NEXT_GATE.md` and use the exact prompt in `ETL_06_NEW_SESSION_MASTER_PROMPT.md`.

## 2. Read order

1. `ETL_00_START_HERE.md` — current orientation and source precedence.
2. `ETL_01_PRODUCT_PROJECT_AND_ARCHITECTURE.md` — what the Framework and Extension are.
3. `ETL_02_WORKFLOW_AGENTS_AND_SAFETY_CONTRACT.md` — how the product works and its safety invariants.
4. `ETL_03_IMPLEMENTED_CAPABILITIES_AND_EVIDENCE.md` — repairs, tests, packages, and proven behavior.
5. `ETL_04_CURRENT_STATE_OPEN_WORK_AND_NEXT_GATE.md` — exact current blocker and backlog.
6. `ETL_05_CHRONOLOGY_DECISIONS_RISKS_AND_GLOSSARY.md` — history, accepted decisions, risks, and terminology.
7. `ETL_06_NEW_SESSION_MASTER_PROMPT.md` — copy/paste prompt for the next fresh Agent session.

## 3. Evidence precedence

When values conflict, use this order:

1. Current explicit owner instruction.
2. Live repository, live installed Extension Host, exact artifact, and reproducible runtime output.
3. Machine-authoritative contracts and executable validators.
4. This 2026-08-29 handoff package.
5. The 2026-08-24/27 Library handoff set.
6. Older Library documents.
7. Screenshots, OCR, remembered chat values, examples, or assumptions.

Never silently merge conflicting version, path, branch, hash, test-count, or status values. Re-derive them before mutation.

## 4. Current identity to re-verify before any edit

```text
Repository root:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Origin:
https://github.com/TD-Universe/agentic_etl.git

Branch:
hotfix/hf1-oracle-fresh-consumer-v2

Last repeatedly reported HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

Extension ID:
td-etl.databricks-etl-copilot

Latest reported source/package version:
0.3.146

Latest reported artifact:
databricks-etl-copilot-0.3.146.vsix
```

These values are evidence, not permission and not a substitute for the identity gate.

## 5. Hard stop conditions

Stop and report instead of guessing if:

- repository identity, branch, or HEAD differs;
- another Agent is concurrently mutating the tree;
- the authorized path set is incomplete;
- a proposed fix requires weakening `**/*.vsix` protection globally;
- a fix relies on a display name as trust identity;
- missing or malformed producer provenance would still pass;
- an edit would touch package version, VSIX, product source, test registration, prompts, consumer workspace, install state, or Runtime QA outside the declared task;
- a claimed PASS lacks executable evidence.

## 6. Current top-level status

| Area | Status |
|---|---|
| Core Extension architecture | Implemented and extensively source/package validated |
| Consumer six-Agent topology | Implemented; static and byte-lock evidence passed |
| Repair 13 structured diagnostic channel | Implemented and independently reviewed |
| Phase-H baseline refresh | Completed canonically for the accepted Repair 13 input drift |
| `0.3.146` package | Built and exact-package verified |
| Package artifact integrity | PASS |
| Package-lifecycle governance | BLOCKED — exception model cannot express safe create-only VSIX creation |
| Certification provenance | BLOCKED — producer/reviewer identity can be missing or ambiguous |
| Local install/activation of `0.3.146` | Not authorized/currently not ready |
| Live Runtime QA for `0.3.146` | Not started |
| Commit/push/PR/SIT/release | Not authorized |

