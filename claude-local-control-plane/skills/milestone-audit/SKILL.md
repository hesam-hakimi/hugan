---
name: milestone-audit
description: Audit milestone completion from task contracts and verified local run evidence without changing code.
disable-model-invocation: true
argument-hint: "<milestone file and run evidence directory>"
---

Audit `$ARGUMENTS` read-only.

Require every task to have:

- a matching milestone and approved capability;
- an immutable base SHA;
- signed Planner-to-Implementer and Implementer-to-Verifier handoffs;
- distinct role session IDs;
- deterministic boundary PASS;
- all required checks PASS;
- an independent Verifier PASS on the exact diff digest;
- required documentation evidence;
- no unresolved BLOCKED or partially mutated run.

Return `READY_FOR_OWNER_MILESTONE_REVIEW` only when all requirements are proven. Never authorize merge, package, install, runtime QA, deployment, or release.
