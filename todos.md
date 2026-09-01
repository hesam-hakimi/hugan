@etl

F5 Runtime QA — Phase 0: Read-Only Capability and Identity Preflight

Perform only a strictly read-only runtime preflight in the currently opened
Extension Development Host.

Do not interpret the workbook yet. Do not render, validate, preview, approve,
confirm, or write any artifact.

Expected runtime identity:

- Chat participant: the registered ETL Orchestrator, not a general-purpose Agent.
- Extension ID: td-etl.databricks-etl-copilot
- Extension version: 0.3.147
- Workspace root:
  C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982
- Input workbook:
  sttm/synthetic_workbook.xlsx
- Expected workspace type: consumer ETL workspace with managed workflow assets.
- Expected registered ETL tool count: 16.

Required actions, in this exact order:

1. Invoke the registered `etl_capabilities` tool exactly once.
2. Report:
   - active participant/orchestrator identity;
   - extension ID and version;
   - resolved physical workspace root;
   - workspace classification;
   - registered ETL tool count and exact tool names;
   - runtime implementation source reported by the capability probe.
3. Verify, read-only, that these workspace-relative assets exist:
   - .github/
   - resources/
   - sttm/synthetic_workbook.xlsx
4. Confirm that the workbook remains workspace-contained.
   Do not manually parse, convert, copy, or modify the XLSX file.
5. Confirm that no filesystem write, terminal command, external service call,
   workflow initialization, render, validation, preview, approval, or write
   operation occurred.

Stop immediately and report BLOCKED if:

- the participant is not the registered ETL Orchestrator;
- the extension ID or version differs;
- the physical workspace root differs;
- any required asset is missing;
- the workbook resolves outside the workspace;
- the registered tool count is not exactly 16;
- any capability required for the later deterministic flow is unavailable;
- any mutation or external dependency is required.

Do not attempt to repair or work around a mismatch.

Return a concise evidence table with Expected, Actual, and Result columns.

End with exactly one marker:

F5_CAPABILITY_PREFLIGHT_PASS

or

F5_CAPABILITY_PREFLIGHT_BLOCKED
