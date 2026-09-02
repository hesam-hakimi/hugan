Phase 1B.3M-R — Independent No-Host argv Transport Proof

Environment

Run locally in VS Code Agent mode from:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

This is an operational-only, read-only validation of the Windows multi-development-path repair retained from Phase 1B.3M.

Objective

Independently prove whether the current retained repair transports both --extensionDevelopmentPath arguments through the exact installed @vscode/test-electron Windows spawn layer without splitting the Copilot path at spaces.

This phase must not launch VS Code or the Extension Host.

Absolute prohibitions

* Do not edit any repository file.
* Do not edit anything under node_modules.
* Do not run npm run compile.
* Do not invoke the repository test runner.
* Do not invoke Code.exe.
* Do not launch an Extension Host.
* Do not run any focused test.
* Do not copy, install, seed, move, or modify an extension.
* Do not use inline node -e or an inline PowerShell-generated JavaScript expression.
* Do not retry the transport probe.
* Do not stage, commit, stash, reset, restore, clean, or change branches.
* Do not click or use F5.

Step 1 — Read-only premise verification

Record:

* repository root
* branch
* HEAD
* exact git status --porcelain
* SHA-256 of:
    * src/test/runTest.ts
    * out/test/runTest.js
    * src/extension.ts
    * out/extension.js
    * .github/templates/request.md
    * src/test/suite/sttmRealHostStructuredResult.test.ts
    * package.json
    * tsconfig.json

Verify that the retained Phase 1B.3M change is confined to the Windows final adapter boundary in src/test/runTest.ts and its compiler-generated out/test/runTest.js.

Statically confirm that:

1. the raw Copilot path is validated and canonicalized before encoding;
2. unsafe Windows shell metacharacters and trailing backslashes are rejected;
3. exactly one quoting layer is added only for the Windows isolated-run call;
4. the ordered pair remains:
    [etlRepositoryPath, bundledCopilotExtensionPath];
5. normal runs and non-Windows behavior are unchanged;
6. exactly one production runTests(...) call remains.

If any premise fails, stop without running the probe and report BLOCKED.

Step 2 — Create a unique temporary probe directory

Create exactly one unique directory beneath %TEMP%, outside the repository and QA workspace.

Using PowerShell file cmdlets, write these separate files into it:

* argv-recorder.js
* fake-code.cmd
* transport-probe.js
* expected-argv.json

Do not use an inline Node program.

argv-recorder.js must write process.argv.slice(2) as strict UTF-8 JSON to a result file whose path is supplied through a dedicated temporary environment variable.

fake-code.cmd must invoke the resolved node.exe and the absolute argv-recorder.js path, forwarding all received arguments exactly once. It must not invoke Code.exe.

transport-probe.js must:

1. require the repository’s exact installed @vscode/test-electron;
2. use the current retained repair’s exact Windows argument representation;
3. call the installed runTests(...) transport exactly once;
4. set vscodeExecutablePath to the temporary fake-code.cmd;
5. supply the repaired ordered development-path pair;
6. use harmless temporary placeholder values for any required test/workspace arguments;
7. perform no repository write.

Step 3 — Expected arguments

The child recorder must receive these two complete argument entries, in this order:

--extensionDevelopmentPath=C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

--extensionDevelopmentPath=C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot

After Windows command parsing, neither recorded value may retain transport-only quote characters.

The recorded argv must not contain any standalone or truncated fragments including:

* C:\Users\tag5916\AppData\Local\Programs\Microsoft
* VS
* Code\08d4889f9e\resources\app\extensions\copilot
* any partial --extensionDevelopmentPath value

There must be exactly two --extensionDevelopmentPath= entries.

Step 4 — Classification

PASS only if all of the following are proven:

* the temporary recorder was reached;
* the installed @vscode/test-electron transport was called exactly once;
* both expected arguments were recorded byte-for-byte after command parsing;
* their order is correct;
* no truncated fragments exist;
* Code.exe invocations: 0;
* Extension Host launches: 0;
* repository edits: 0;
* compiles: 0;
* retries: 0.

Otherwise classify BLOCKED. Do not repair or retry in this phase.

Step 5 — Final integrity

Recheck and report:

* branch and HEAD unchanged;
* exact Git status unchanged;
* every Step 1 hash unchanged;
* git diff --check;
* repository edits made by this phase: 0;
* compiles: 0;
* transport probes attempted/successful: 1/1 or 1/0;
* Code.exe invocations: 0;
* Extension Host launches: 0;
* test bodies evaluated: 0;
* vscode.lm.invokeTool calls: 0;
* extension copies/installations: 0.

On PASS, remove only the exact unique temporary probe directory using PowerShell cmdlets after retaining all evidence in the response.

On BLOCKED, retain the exact temporary directory and report its full path.

End with exactly one marker:

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_ARGV_PROOF_PASS

or

F5_LOCAL_WINDOWS_MULTI_DEVELOPMENT_PATH_ARGV_PROOF_BLOCKED
