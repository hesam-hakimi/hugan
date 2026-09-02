Phase 1B.3L-PRE — Read-Only Existing Logging Capability Audit

Work locally in the currently open desktop VS Code repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

This phase is strictly read-only.

Do not:

* edit any repository, compiled, installed-product, QA, or evidence file;
* compile or run tests;
* invoke npm, npx, tsc, esbuild, Code.exe, or the compiled runner;
* launch an Extension Host;
* invoke vscode.lm.invokeTool;
* install, copy, seed, or update an extension;
* use Marketplace or network access;
* use F5, Cloud, ETL Orchestrator, or another worktree;
* stage, commit, stash, restore, reset, or clean;
* inspect credentials, tokens, authentication state, or real-profile prompt contents.

Context

Phase 1B.3K has already passed and its changes have been accepted with Keep.

Expected repository identity:

Branch:

fix/workspace-write-completion-0.3.148

HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected Git status:

M .github/templates/request.md
M src/extension.ts
M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Do not treat these existing changes as audit mutations.

The VS Code Output selector currently shows at least:

* ETL Copilot
* ETL Copilot - Prompt Debug Log

The next proposed operation is Phase 1B.3L, a one-shot isolated real-Host run using two explicit development-extension paths.

Before spending that launch, determine whether the existing logging implementation provides enough evidence to diagnose each relevant boundary.

Step 1 — Preserve and verify current state

Read and report:

1. Repository path, branch, HEAD, and Git status.
2. git diff --check.
3. A complete SHA-256 baseline for:
    * src/extension.ts
    * src/test/runTest.ts
    * package.json
    * out/extension.js
    * out/test/runTest.js
    * out/test/suite/sttmRealHostStructuredResult.test.js
4. Confirm that no command used by this audit can mutate the working tree.

Do not stop merely because the four expected existing changes are present.

Stop as BLOCKED only if additional unexpected repository changes make the logging implementation ambiguous.

Step 2 — Map the current logging architecture

Search tracked source, tests, manifests, and compiled output for all logging-related implementations, including:

* createOutputChannel
* LogOutputChannel
* OutputChannel
* ETL Copilot
* ETL Copilot - Prompt Debug Log
* trace
* debug
* info
* warn
* error
* append
* appendLine
* console.log
* console.warn
* console.error
* logger
* logLevel
* outputLevel
* telemetry
* correlationId
* requestId
* invocationId
* redaction or sanitization

For each of the two visible ETL channels report:

1. Exact source file and symbol that creates it.
2. Whether it uses OutputChannel or LogOutputChannel.
3. When it is created and disposed.
4. Which execution modes create it:
    * Production
    * Development
    * Test
    * opted-in Test mode using ETL_TEST_READ_ONLY_TOOL_ONLY=1
5. Whether it supports configurable levels.
6. Exact setting, command, or environment contract controlling its level.
7. Default level.
8. Whether timestamps and severity are generated automatically or manually.
9. Whether logs are persisted to disk or visible only in the Output UI.
10. Whether it performs redaction.
11. Whether Prompt Debug logging is opt-in.
12. Whether prompt contents, STTM data, paths, generated code, credentials, tokens, or authentication information could be exposed.
13. Whether the authoritative source and compiled output agree.

Do not assume behavior from channel names alone.

Step 3 — Inventory all current log call sites

Produce a concise matrix of every relevant logging call site grouped by stage:

* runner preflight and launch configuration;
* Extension Host startup;
* ETL extension activation start;
* github.copilot-chat resolution;
* Copilot activation start/success/failure;
* Copilot readiness;
* Test-mode gate selection;
* etl_interpret_sttm registration start/success/failure;
* invokeTool entry;
* tool input validation;
* workspace and STTM resolution;
* workbook parsing;
* semantic validation;
* manifest/preview creation;
* LanguageModelToolResult construction;
* result part count and types;
* tool completion;
* caught and uncaught errors;
* extension deactivation.

For each stage report:

* exact file/function;
* log channel;
* severity;
* data recorded;
* whether it executes in the opted-in Test-only path;
* whether it runs before and after the relevant operation;
* whether failure includes stack/cause information;
* whether sensitive data is safely excluded.

Explicitly distinguish:

* implemented log evidence;
* test assertion evidence;
* runner console output;
* VS Code Extension Host logs;
* missing evidence.

Step 4 — Evaluate Phase 1B.3L diagnostic coverage

Determine whether a single failed Phase 1B.3L run would allow us to distinguish all of these outcomes without another diagnostic Host launch:

1. The ordered development-path array was accepted.
2. The bundled Copilot extension was discovered from the explicit development path.
3. Built-in shadowing did or did not occur.
4. github.copilot-chat resolution succeeded or failed.
5. Copilot activation started and succeeded or failed.
6. ETL extension activation started and succeeded or failed.
7. The opted-in Test-mode branch was selected.
8. etl_interpret_sttm registration started and succeeded or failed.
9. invokeTool was attempted or never reached.
10. invokeTool returned or rejected.
11. LanguageModelToolResult construction started and completed.
12. The returned part count, part types, MIME type, and byte length.
13. Workbook/parser/validator stage reached.
14. The exact first failing boundary.
15. A usable error name, message, cause, and stack was retained.
16. Logs and evidence would survive beneath the isolated evidence root after Host exit.

For every outcome classify coverage as:

* FULL
* PARTIAL
* NONE

Do not claim FULL coverage unless the exact source/compiled path proves it.

Step 5 — Inspect retained isolated evidence only

If present, inspect read-only evidence beneath:

C:\Users\tag5916\AppData\Local\Temp\etl-phase-1b3i-seeded-20260902-113624-f3a807760bbe

Use it only to determine:

* which ETL, runner, and Extension Host logs were actually retained;
* whether the existing ETL Output channels appeared in retained disk evidence;
* whether prior Copilot resolution/activation failure was observable;
* whether an Output-channel message can be recovered after Host exit.

Do not inspect the real VS Code user profile or unrelated logs.

Do not modify or delete the retained evidence.

Step 6 — Security and operability audit

Evaluate whether the existing implementation:

* avoids credentials, tokens, authentication state, and full environment dumps;
* avoids recording full STTM workbook contents by default;
* avoids recording full prompts and generated source unless explicitly opted in;
* supports a safe production default;
* can enable Debug/Trace without a code change;
* uses correlation identifiers consistently;
* records elapsed time for major stages;
* provides actionable errors without exposing sensitive content;
* prevents unbounded log volume.

Separate mandatory diagnostic gaps from optional product improvements.

Final decisions

Return exactly one logging classification:

A. CURRENT_LOGGING_SUFFICIENT_FOR_1B3L

B. CURRENT_LOGGING_EXISTS_BUT_GAPS_REQUIRE_TARGETED_INSTRUMENTATION

C. CURRENT_LOGGING_NOT_SUITABLE_FOR_HOST_DIAGNOSIS

Also return exactly one operational decision:

1. RUN_1B3L_NOW_WITH_CURRENT_LOGGING
2. PAUSE_1B3L_AND_ADD_INSTRUMENTATION_FIRST

Choose decision 2 only if a failure during the one-shot run would leave the first failing activation/registration/invocation boundary ambiguous.

If instrumentation is required, provide a minimal future patch plan only:

* exact authoritative source files and functions;
* exact missing events;
* recommended channel to reuse;
* required log levels;
* safe fields to record;
* fields that must never be recorded;
* whether a correlation ID is needed;
* smallest static tests;
* whether one compile would be required.

Prefer extending the existing ETL Copilot channel. Do not recommend creating a third channel unless the current architecture proves that reuse is impossible.

Do not implement the plan.

Required counters

Report:

* repository edits: 0
* QA edits: 0
* compiled-file edits: 0
* compiles: 0
* runner invocations: 0
* Host launches: 0
* invokeTool calls: 0
* extension copies/installations: 0

End with exactly:

F5_LOCAL_EXISTING_LOGGING_AUDIT_COMPLETE
