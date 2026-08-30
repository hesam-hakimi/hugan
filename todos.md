Accept the current BLOCKED result. Do not commit, package, install, bump the
version, or change the existing four-file product diff.

Important corrections:

1. The approved historical mapping is:
   - Failure 1, missing maintainer delivery prompt:
     F1 / ETL-TEST-DEBT-001
   - Failure 3, stale module AGENT.md expectation:
     F3 / ETL-TEST-DEBT-002
   - Failure 2, business-context.instructions.md missing valid name:
     unregistered blocker; do not quarantine it.

2. Do not treat:
   code --extensionDevelopmentPath=...
   as equivalent to an attached F5 debugging session.

3. Without modifying the repository, create a temporary external
   .code-workspace under %TEMP% containing a real extensionHost launch
   configuration for:
   - the current source repository as extensionDevelopmentPath;
   - the isolated QA workspace as the Extension Development Host workspace;
   - correct compiled outFiles/source maps;
   - no source repository folder inside the child QA workspace.

4. Compile the current candidate and validate the temporary launch configuration.
   Then stop and give the owner one minimal action: open that workspace and press F5.

5. The real-host acceptance must include both:
   A. Direct vscode.lm.invokeTool validation of TextPart + DataPart, MIME,
      Uint8Array, parsed object, parity, malformed fail-closed, and containment.
   B. Actual @etl /workflow execution using a synthetic Excel STTM workbook
      from the QA workspace. A Markdown fixture alone is insufficient for
      end-to-end acceptance.

6. Until the real host runs, report:
   REAL_HOST_F5_EXECUTED: NO
   PUBLIC_STRUCTURED_OBJECT_VISIBLE: NOT_TESTED_ON_REAL_HOST
   MARKDOWN_STRUCTURED_PARITY: NOT_TESTED_ON_REAL_HOST
   PREVIEW_WORKSPACE_MUTATION: NOT_TESTED_ON_REAL_HOST
   SOURCE_REPOSITORY_ACCESSED: NOT_TESTED_ON_REAL_HOST

Do not add .vscode/launch.json to this product branch.
Stop after preparing and validating the external F5 harness.
