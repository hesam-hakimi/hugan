---
name: run-status
description: Read the durable status and evidence summary for a local control-plane run.
disable-model-invocation: true
argument-hint: "--project <repo> [--run-id <id>]"
---

Run the read-only status command for `$ARGUMENTS`:

```text
node <plugin-root>/scripts/lcac.mjs status $ARGUMENTS
```

Summarize the current state, last safe state, role session IDs, changed paths, check outcomes, verifier verdict, and recovery rule. Never infer PASS from an incomplete or missing artifact.
