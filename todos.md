Accept the prepared external F5 harness, but do not call it PASS yet.

Keep the repository at the same four approved changes and version 0.3.147.
Do not edit source or governance, commit, push, package, install, build a VSIX,
bump the version, run jobs, approve writes, or deploy.

Only these quarantines are approved:
- F1 / ETL-TEST-DEBT-001
- F3 / ETL-TEST-DEBT-002

Failure 2, business-context.instructions.md missing a valid name, remains an
unregistered blocker.

Before I run F5, update only the external %TEMP% harness and operator runbook:

1. Replace the concurrent forEach invocations with deterministic sequential
   valid and negative invocations.

2. Capture and inspect the resolved result returned by:
   vscode.lm.invokeTool('etl_interpret_sttm', ...)
   Do not rely only on the producer-local variable `parts`.

3. For a valid result, assert on returned result.content:
   - exactly TextPart plus DataPart;
   - MIME application/json;
   - data is Uint8Array;
   - decoded JSON is a non-null object with the expected schema;
   - exact ordered mapping identities and affected rows;
   - exact bidirectional diagnostic parity between Markdown and JSON.

4. Exercise missing, null, primitive, and malformed structured-result cases
   independently. Each executed invalid case must fail closed with TextPart
   only and no DataPart. Mark every unexecuted class individually as
   NOT_TESTED_ON_REAL_HOST.

5. Locate the actual @etl /workflow participant/tool-call path. Give me a
   breakpoint at or after its vscode.lm.invokeTool call, or an equivalent host
   tool-call trace. Hitting src/tools/index.ts:191 alone proves only producer
   execution. Without consumer-return evidence report:
   WORKFLOW_PUBLIC_SEAM: NOT_PROVEN

6. Provide one numbered Desktop VS Code runbook in this exact order:
   - open %TEMP%\etl-f5-harness.code-workspace;
   - select its extensionHost configuration;
   - set and confirm bound breakpoints;
   - press F5;
   - verify the child [Extension Development Host] contains only
     %TEMP%\etl-consumer-qa;
   - verify td-etl.databricks-etl-copilot@0.3.147 is running from the current
     source checkout;
   - run direct cases sequentially;
   - run the synthetic Excel @etl /workflow case.

   If a read-only tool confirmation appears, choose Continue once.
   Never choose Always Allow. Any write/job/deploy approval request is failure.

7. Save all evidence only under %TEMP%. Capture:
   - HEAD and dirty-diff hash;
   - selected launch configuration;
   - extension ID, version, and development path;
   - resolved public results;
   - workflow tool name, caller evidence, and resolved QA workbook path;
   - chat transcript;
   - forced file, directory, and settings pre/post inventory;
   - final git status.

8. Define an observable proof for repository-local sample access using path/I/O
   tracing or unique workbook provenance. Path separation alone is insufficient.
   Report:
   REPO_LOCAL_SAMPLE_STTM_READ: NO|YES|NOT_PROVEN

Stop after producing the corrected copy/paste-safe runbook.
Do not execute UI actions and do not claim PASS.

Required post-run fields:

REAL_HOST_F5_EXECUTED: YES|NO
DIRECT_PUBLIC_TOOL_SEAM: PASS|FAIL|NOT_TESTED
WORKFLOW_TOOL_INVOKED: YES|NO|NOT_PROVEN
WORKFLOW_PUBLIC_SEAM: PASS|FAIL|NOT_PROVEN
NEGATIVE_CLASSES: <per-class status>
MARKDOWN_STRUCTURED_PARITY: PASS|FAIL|NOT_TESTED
PREVIEW_WORKSPACE_MUTATION: NO|YES|NOT_PROVEN
REPO_LOCAL_SAMPLE_STTM_READ: NO|YES|NOT_PROVEN
REPOSITORY_DIFF_UNCHANGED: YES|NO
STRUCTURED_OUTPUT_RUNTIME_GATE: PASS|FAIL|BLOCKED
OVERALL_TASK_PR_GATE: BLOCKED_FAILURE_2
