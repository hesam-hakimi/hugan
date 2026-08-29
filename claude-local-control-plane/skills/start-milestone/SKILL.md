---
name: start-milestone
description: Prepare a milestone contract and bounded task contracts for the local agent control plane without starting implementation.
disable-model-invocation: true
argument-hint: "<milestone objective or milestone file>"
---

Prepare milestone governance for `$ARGUMENTS`.

1. Read the product roadmap and architecture contract.
2. Produce or review one milestone contract using the bundled schema.
3. Break the milestone into small task contracts whose path/check scopes are subsets of the milestone envelope.
4. Put explicit acceptance criteria, roadmap references, architecture references, documentation expectations, and exact base SHA in every task.
5. Do not implement, edit product source, run a task, or approve on the owner's behalf.
6. Show the owner the milestone and task boundaries for one approval decision.

After owner approval, run the deterministic CLI outside this skill:

```text
node <plugin-root>/scripts/lcac.mjs run --project <repo> --config <config> --milestone <milestone.json> --task <task.json>
```
