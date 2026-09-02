# Phase 1B.3C — Code Identity Closure and File-Sidecar Bridge Acceptance

Mode: verify-only.

Continue in this same normal Claude Agent session.
Do not use ETL Orchestrator.
Keep F5 stopped and all breakpoints disabled.

Goal:
Close the sole Phase 1B.3B assertion using Windows file metadata.
Do not rerun the wrapper or invoke any native executable.

Fixed identities:
- Repository:
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
- QA root:
  C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982
- Code executable:
  C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\Code.exe
- Expected Code version:
  1.135.0
- Retained evidence directory:
  C:\Users\tag5916\AppData\Local\Temp\etl-native-sidecar-be7ebbc589c041e5b43bbab8de16ae9d
- Expected branch:
  fix/workspace-write-completion-0.3.148
- Expected HEAD:
  45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
- Protected file:
  .github/templates/request.md
- Protected SHA-256:
  2EA692C2178863551D7E40CF1C85DBE48286C370F0D1A392678EBF47751ECB84

Expected retained Git status, exactly and in this order:
' M .github/templates/request.md'
' M src/test/runTest.ts'
'?? src/test/suite/sttmRealHostStructuredResult.test.ts'

Hard prohibitions:
- Do not invoke Code.exe, code.cmd, cmd.exe, git.exe, node.exe, npm, npx, Start-Process, or bridge.cmd.
- Do not retry Phase 1B.3B.
- Do not edit any repository or QA-workspace file.
- Do not compile or run tests.
- Do not press F5 or launch an Extension Host.
- Do not call vscode.lm.invokeTool, etl_interpret_sttm, or any ETL tool.
- Do not stage, commit, stash, restore, reset, clean, or switch branches.
- Never modify, restore, format, stage, or delete .github/templates/request.md.
- Use only PowerShell cmdlets and .NET property reads.

Procedure:

1. Validate the evidence-directory target before reading or deleting anything:
   - Canonicalize it using [System.IO.Path]::GetFullPath().
   - Its parent must be exactly $env:TEMP.
   - Its leaf must be exactly:
     etl-native-sidecar-be7ebbc589c041e5b43bbab8de16ae9d
   - Do not use wildcards.

2. Read the existing sidecar files using only Get-Content and Get-ChildItem. Require:
   - done.txt trims exactly to COMPLETE.
   - git.exit.txt, node.exit.txt, code.exit.txt, head.exit.txt,
     branch.exit.txt, and status.exit.txt each trim exactly to 0.
   - The corresponding six stderr files are exactly zero bytes.
   - git.stdout.txt trims exactly to:
     git version 2.45.0.windows.1
   - node.stdout.txt trims exactly to:
     v20.19.5
   - code.stdout.txt may contain only CRLF; do not treat it as the
     Code version and do not rerun Code.exe.
   - head.stdout.txt matches the expected HEAD.
   - branch.stdout.txt matches the expected branch.
   - status.stdout.txt contains exactly the three expected lines,
     including prefixes and order.
   - eran.before.txt is PRESENT.
   - eran.after.txt is ABSENT.
   - vscode-cli.after.txt is ABSENT.
   - no-attach.after.txt is ABSENT.
   - comspec.after.txt is PRESENT.

3. Confirm Code.exe exists using Test-Path.

4. Read these properties without executing Code.exe:
   (Get-Item -LiteralPath $codeExe).VersionInfo.ProductVersion
   (Get-Item -LiteralPath $codeExe).VersionInfo.FileVersion

   Normalize every available version to its first three numeric
   components. Both 1.135.0 and 1.135.0.0 must normalize to 1.135.0.

   Require at least one normalized metadata value to equal exactly:
   1.135.0

5. Recompute the protected file SHA-256 using Get-FileHash and require
   the exact expected hash.

6. If any check fails:
   - Do not delete the evidence directory.
   - Report the exact failed assertion.
   - End with exactly:
     F5_FILE_SIDECAR_NATIVE_BRIDGE_BLOCKED

7. If every check passes:
   - State that the earlier BLOCKED marker was caused only by the
     incompatible direct Code.exe --version stdout probe.
   - State that Code identity is now verified through Windows file
     metadata.
   - State that the sidecar bridge is accepted for later CLI
     compile/test result capture.
   - State that no Extension Host or parser budget was consumed.
   - Remove only the exact validated evidence directory with:
     Remove-Item -LiteralPath $runDir -Recurse -Force
   - Verify that exact path is absent.
   - End with exactly:
     F5_FILE_SIDECAR_NATIVE_BRIDGE_PASS

Final counters must be:
- Repository edits: 0
- QA-workspace edits: 0
- Native invocations: 0
- Wrapper invocations: 0
- Compiles/tests/F5: 0
- Extension Host launches: 0
- invokeTool calls: 0
- Parser calls: 0
