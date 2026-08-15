# Roadmap

## Milestone 1 — LangGraph Observe MVP

- [x] Provider-neutral model contract
- [x] Host provider-factory loading
- [x] Isolated Git mirror/sandbox
- [x] Repository manifest and Python symbol index
- [x] Role-specific bounded context compiler
- [x] Hierarchical phase/slice planner contract
- [x] Optional human plan-approval interrupt
- [x] Fixed read-only Git checks
- [x] Independent reviewer contract
- [x] SQLite LangGraph checkpointing
- [x] Filesystem artifact store and final report
- [ ] Live host-provider qualification
- [ ] Public project license decision

## Milestone 2 — Safe Development

- approved-path scope gate;
- implementer subgraph;
- unified patch parser and path validator;
- atomic patch application;
- fixed test-profile registry;
- bounded diagnose/repair loop;
- regression and security reviewers;
- checkpoint-safe rollback of agent-owned patches;
- publish approval;
- commit, push, and optional Draft PR through a source-control adapter.

## Milestone 3 — Project memory and large-program execution

- accepted project knowledge packs;
- phase/slice handoff compaction;
- project decision and ADR memory;
- incremental repository index;
- dependency/call graph and test-impact analysis;
- phase DAG execution with per-slice gates;
- resumable long-running programs;
- context deduplication and model-budget policies.

## Milestone 4 — Worker backends

- Linux process sandbox hardening;
- container sandbox backend;
- remote Windows worker protocol;
- platform-specific check profiles;
- GitHub Actions and self-hosted runner adapters;
- cross-platform evidence reconciliation.

## Milestone 5 — Service and UI

- multi-project web UI;
- task history, live progress, interrupts, and resume;
- artifact/diff/test/review viewers;
- user/RBAC boundaries;
- quotas and sandbox retention;
- PostgreSQL checkpoint and object-store backends;
- usage/cost evidence;
- operational health, audit, and deployment guidance.
