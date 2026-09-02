# Phase 1B.3A — Fresh Agent Native-Execution Preflight

This is a preflight-only task in a brand-new Claude Agent session.

Do not continue Phase 1B.3 yet. Do not edit any repository file, compile, run tests, launch VS Code, start F5, invoke `runTests`, invoke an ETL tool, or consume any Extension Host/parser budget.

## Repository

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:

fix/workspace-write-completion-0.3.148

Expected HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected exact Git status:

 M .github/templates/request.md
 M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

## Native-process proof

Using this new Agent's own shell/tool—not a user-operated Terminal—perform these read-only probes exactly once:

1. Invoke:

   C:\Windows\System32\cmd.exe /d /c

   Use it to create one uniquely named probe file under `%TEMP%` containing exactly:

   AGENT_NATIVE_OK

2. Verify with PowerShell cmdlets that:

   - the probe file exists;
   - its content is exactly `AGENT_NATIVE_OK`;
   - cmd.exe returned exit code 0.

3. Remove only that temporary probe file.

4. Resolve and invoke `git.exe --version`.

   Require:

   - nonempty version output;
   - exit code 0.

5. Resolve and invoke `node.exe --version`.

   Require:

   - nonempty version output;
   - exit code 0.

6. Using the resolved git.exe, run:

   git -C "C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147" status --porcelain=v1 --untracked-files=all

7. Require exactly the three expected status lines above and no additional path.

8. Report presence or absence only—never values—for:

   - ELECTRON_RUN_AS_NODE
   - VSCODE_CLI
   - ELECTRON_NO_ATTACH_CONSOLE
   - NODE_OPTIONS
   - Com reminders

   Correction: use the exact environment-variable name `ComSpec`, not “Com reminders”.

Do not require `ELECTRON_RUN_AS_NODE` to be absent for this preflight. Only record whether it is present in this Agent's own process.

## Stop rules

If any native command:

- produces no usable output;
- produces no exit code;
- does not create the expected side effect;
- or returns nonzero;

stop immediately with BLOCKED.

Do not troubleshoot, edit files, retry, or launch anything else.

## Final report

Report:

- cmd.exe result and exit code;
- git executable, version, and exit code;
- Node executable, version, and exit code;
- exact Git status;
- environment-variable presence only;
- repository edits: 0;
- Extension Host launches: 0;
- `invokeTool` calls: 0;
- parser calls: 0.

End with exactly one marker:

F5_AGENT_NATIVE_PREFLIGHT_PASS

or

F5_AGENT_NATIVE_PREFLIGHT_BLOCKED
