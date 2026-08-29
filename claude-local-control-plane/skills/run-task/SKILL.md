---
name: run-task
description: Explain and initiate one already approved local control-plane task through the deterministic Orchestrator.
disable-model-invocation: true
argument-hint: "--project <repo> --config <config> --milestone <milestone> --task <task>"
---

Use the deterministic Orchestrator for `$ARGUMENTS`.

Do not manually invoke Planner, Implementer, or Verifier. Do not copy their output between chats. The CLI must create fresh session IDs, validate signed handoffs, enforce path boundaries, run approved checks, and stop on failure.

Run:

```text
node <plugin-root>/scripts/lcac.mjs run $ARGUMENTS
```

Report the run ID, terminal state, changed paths, check results, verifier verdict, and any human action required.
