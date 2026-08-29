---
name: resume-run
description: Resume only a pre-mutation local control-plane failure after validating the durable state and unchanged base.
disable-model-invocation: true
argument-hint: "--project <repo> --run-id <id>"
---

Inspect `$ARGUMENTS` with the status command first.

Resume is allowed only when the Orchestrator reports `resumeAllowed: true`. A failure after the Implementer may have modified the worktree and must not be automatically replayed or repaired. In that situation, create a separately approved repair task.

For an allowed pre-mutation resume, run:

```text
node <plugin-root>/scripts/lcac.mjs resume $ARGUMENTS
```
