Continue F5 Runtime QA — Phase 1A: Deterministic STTM Interpretation Only

Phase 0 completed with:

F5_CAPABILITY_PREFLIGHT_PASS

Remain inside the same registered ETL Orchestrator session and the same
Extension Development Host workspace.

This phase is strictly read-only.

Allowed extension tool:

- `etl_interpret_sttm`, invoked exactly once.

Input:

- workspaceRoot:
  C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982
- sttmPath:
  sttm/synthetic_workbook.xlsx
- includeAudit: true

Do not manually open, parse, convert, copy, or inspect the XLSX binary.
Do not use a general-purpose parser or fallback implementation.

Known expected fixture baseline:

- Files discovered: 1
- Files read: 1
- Files blocked: 0
- Active mappings: 8
- Audit findings: 6
- Expected valid mapping candidate:
  FM_F01417B0_00002
- Expected mapping evidence:
  customers.cust_name -> target_db.customer_name
- Both structured and consumer-visible Markdown results should be available.

The six audit findings are known fixture evidence. If their identities and
signatures match the returned deterministic result, record them without
reinvestigating or attempting to repair them.

Required report:

1. Exact tool invocation count.
2. Containment result and resolved workbook path.
3. Files discovered/read/blocked.
4. Active mapping count and ordered mapping IDs.
5. Exact audit finding codes, row identities, and ordering.
6. Structured-result availability.
7. Markdown-result availability.
8. Details of mapping `FM_F01417B0_00002`.
9. Comparison of every expected baseline value against the actual value.
10. Mutation attestation.

Stop and report BLOCKED if:

- containment fails;
- the parser invocation fails;
- any file is blocked;
- any expected count or identity differs;
- the expected mapping is missing or inactive;
- structured or Markdown output is unavailable;
- a second invocation, fallback parser, terminal command, external service,
  manual XLSX inspection, or filesystem mutation would be required.

Do not call framework discovery, module discovery, example search, render,
validation, preview, approval, write, publish, pipeline, Databricks, Jira,
or Confluence tools.

Do not create or modify any job config, environment config, fixture,
workflow asset, or source file.

End with exactly one marker:

F5_STTM_INTERPRETATION_PASS

or

F5_STTM_INTERPRETATION_BLOCKED
