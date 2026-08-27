Do not require the user to execute PowerShell or paste manually generated JSON.

You are the only user-facing ETL Agent. The installed runtime contract requires
you to delegate specialized work to the internal non-user-invocable Agents.

Delegate the read-only pre-QA workspace snapshot and hash verification to the
appropriate installed internal Agent:

- prefer `etl-verifier` for the independent pre/post workspace snapshot,
  SHA-256 comparison and Git-state verification;
- use `etl-evidence-researcher` for read-only evidence discovery if additional
  workspace evidence is required.

Use the installed Agent-delegation mechanism and the installed read-only MCP/tool
surface. Do not invoke `@etl /workflow`, because the Consumer Workspace is already
provisioned and this QA must not reinstall or modify its Agent assets.

This delegation is itself part of Runtime QA.

Continue the existing task:

HF1_V2_RUNTIME_QA_REPAIR_13_PREVIEW_ONLY_VERSION_0_3_145

only if the delegated snapshot succeeds.

Do not:

- ask the user to run a command;
- weaken or skip the snapshot gate;
- write any workspace file;
- approve Preview;
- execute Write;
- recreate or update `.github/agents`, instructions, prompts, skills or MCP
  configuration.

If internal delegation or the required read-only hashing capability is unavailable,
stop and report the exact missing Agent, tool, permission or MCP capability.

In that case end exactly with:

RUNTIME_QA_RESULT:
FAIL_INTERNAL_AGENT_DELEGATION_OR_TOOL_ACCESS

Otherwise continue the previously supplied Preview-only Runtime QA through the
ETL Orchestrator and its internal Agents.
