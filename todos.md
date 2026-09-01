# Phase 1B — Real Extension-Host Structured-Result Characterization

## Mode

Implement and run exactly one focused, test-only characterization at the real VS Code `vscode.lm.invokeTool` boundary.

This is not a product repair.
Do not change production code.
Do not commit or stage anything.

## Authoritative environment

Repository root:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required branch:
fix/workspace-write-completion-0.3.148

Required HEAD:
45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

QA workspace root:
C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

Workbook relative path:
sttm/synthetic_workbook.xlsx

Extension ID:
td-etl.databricks-etl-copilot

Tool:
etl_interpret_sttm

Known pre-existing worktree modification:
.github/templates/request.md

## Objective

Determine whether the current committed implementation’s
`LanguageModelDataPart` survives a fresh, real Extension Development Host invocation through:

vscode.lm.invokeTool(...)

Inspect the result directly from:

LanguageModelToolResult.content

Do not use the ETL Orchestrator transcript or its offloaded Markdown resource as evidence for the structured channel.

Evidence boundary:

- This test can prove the extension-to-real-`vscode.lm` programmatic boundary.
- It cannot prove what the model-facing Chat/Orchestrator offload layer receives.
- A passing result must not be reported as proving or disproving
  `VS_CODE_CHAT_HOST_OFFLOAD_LIMITATION`.

## 1. Mandatory preflight

Before editing:

1. Verify the exact repository root, branch, and HEAD.
2. Run and record:

   git status --short --untracked-files=all

3. The only pre-existing changed path must be:

   .github/templates/request.md

4. Record the SHA-256 and exact Git diff of that file.
5. Do not edit, format, stage, restore, stash, reset, clean, commit, or otherwise alter it.
6. Confirm every implementation file on the audited tool path is byte-identical to HEAD.
7. Confirm every intended test/harness file is initially clean.
8. Record:
   - `package.json` version;
   - `package.json.main`;
   - installed `code --version`;
   - SHA-256 and UTC mtime of `out/tools/index.js`.

Do not change the package version. Version `0.3.147` on the `0.3.148` branch is known and is not sufficient build identity.

If repository identity differs, an intended test file is already dirty, or any additional pre-existing changed path exists, stop with:

F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED

## 2. Real-host infrastructure gate

Inspect the existing integration-test conventions read-only.

Proceed only if one focused test can run in a fresh, real Extension Development Host using the already installed VS Code.

Do not:

- download or install VS Code;
- run `npm install`;
- use a VS Code stub;
- use `registerVscodeStub`;
- intercept `Module._load`;
- call `EtlReadOnlyToolService.interpretSttm` directly;
- call the parser implementation directly;
- reuse the currently running or previous manual F5 host.

If no existing focused real-host runner exists, or implementing this requires production/configuration/dependency changes, stop and report the exact blocker. Do not invent a broad new harness.

## 3. Edit allowlist

Authorize at most:

1. one new characterization test inside the existing real Extension Development Host integration-test tree; and
2. `src/test/testPatterns.ts` only if strictly required to place the new test in `INTEGRATION_TEST_PATTERNS`.

Do not modify:

- production TypeScript;
- `package.json` or lockfiles;
- launch configurations;
- contracts;
- fixtures or the XLSX;
- documentation or Eval reports;
- the existing stub-based result-envelope suite;
- `.github/templates/request.md`;
- generated `out/**` manually.

Do not weaken, rename, remove, or reclassify any existing test.

If more than the two authorized test paths are required, stop before making additional edits.

## 4. Fresh-build and fresh-host identity

Use only the repository’s established focused test-compilation command and real-host integration runner.

Before launching the new Extension Development Host:

1. Compile the current worktree using the narrow sanctioned command.
2. Record:
   - exact compile command;
   - UTC compile completion time;
   - SHA-256 and UTC mtime of `out/tools/index.js`;
   - confirmation that compiled output contains explicit
     `application/json` structured-result construction.

Launch a new Extension Development Host only after that compilation.

Inside the real-host test, record:

- `vscode.version`;
- process PID;
- approximate process-start UTC using `Date.now() - process.uptime()`;
- extension ID;
- resolved extension path;
- extension package version;
- `extension.isActive`;
- resolved compiled main path.

The extension path must resolve to the authoritative source repository, and the host process must start after the recorded build.

Do not rely on package version alone.

If compilation dirties a tracked incremental cache that was clean at preflight, restore it byte-for-byte from its committed HEAD blob only after proving compilation was the sole cause. Do not use checkout, reset, restore, clean, or stash.

## 5. Characterization test

Use real `require('vscode')`.

The test must derive the QA workspace root from this process-scoped environment variable:

ETL_F5_QA_WORKSPACE_ROOT

Set that variable only for the focused runner process to:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

Do not hardcode that absolute path in tracked test source.

Activate the extension and verify that `etl_interpret_sttm` appears in `vscode.lm.tools`.

Invoke the registered tool exactly once:

await vscode.lm.invokeTool(
  'etl_interpret_sttm',
  {
    input: {
      workspaceRoot: qaWorkspaceRoot,
      sttmPath: 'sttm/synthetic_workbook.xlsx',
      includeAudit: true
    },
    toolInvocationToken: undefined
  }
);

Do not invoke `etl_capabilities` or any other ETL tool.
Do not perform a second parser invocation.
Do not manually open, parse, convert, copy, or modify the XLSX.

Before passing the result to any repository extractor, capture the raw returned result.

Record and assert:

1. `result.content.length`;
2. ordered constructor/type name of every content part;
3. TextPart value length;
4. DataPart `mimeType`;
5. whether DataPart data is a `Uint8Array`;
6. DataPart byte length;
7. UTF-8 decode success;
8. `JSON.parse` success;
9. parsed top-level keys;
10. exact deterministic fixture evidence:
    - files discovered/read/blocked = 1/1/0;
    - active mapping count = 8;
    - audit finding count = 6;
    - `FM_F01417B0_00002` is present, active, and first;
    - `customers.cust_name -> target_db.customer_name`;
11. Markdown contains the same deterministic mapping evidence.

Reuse the exact field paths and assertions from the existing stub-based envelope test rather than inventing a second interpretation of the payload.

The expected successful result is exactly:

- index 0: `LanguageModelTextPart`;
- index 1: `LanguageModelDataPart`;
- DataPart MIME: `application/json`;
- non-empty, valid UTF-8 JSON bytes.

If confirmation or approval UI prevents the focused test from completing, do not bypass it using private APIs or direct implementation calls. Report:

APPROVAL_UI_BLOCKED

## 6. Workspace mutation guard

Before and after the single invocation, compare the QA workspace inventory and hashes.

The parser invocation must not create, modify, rename, or delete any file in:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

Do not write test logs or snapshots into the QA workspace.

## 7. Execution limits

Run only the focused real-host characterization test.

Do not run:

- the full unit suite;
- Eval Golden;
- packaging or VSIX operations;
- publish, pipeline, Databricks, Jira, or Confluence calls;
- render, preview, approval, or workspace-write flows;
- another Orchestrator STTM invocation.

Do not rerun after an actual `etl_interpret_sttm` invocation. If the runner fails before invoking the tool, report the blocker rather than improvising another route.

The five pending tests and these three known unrelated failures are out of scope and must not be investigated:

1. missing `.github/prompts/deploy-v3-agent-tool-context-gap.prompt.md`;
2. missing `name` in `.github/instructions/business-context.instructions.md` frontmatter;
3. eleven tracked `src/**/AGENT.md` files versus an expected empty inventory.

## 8. Result classification

Use exactly one classification.

### F5_REAL_HOST_STRUCTURED_RESULT_PASS

Use only if:

- fresh build and host identity are proven;
- the tool was invoked exactly once;
- the raw result contains the expected ordered TextPart and
  `application/json` DataPart;
- the structured bytes parse and match the deterministic baseline;
- the QA workspace is unchanged.

Allowed conclusion:

The structured part survives the real `vscode.lm.invokeTool` boundary. The earlier `F5_STTM_INTERPRETATION_BLOCKED` was an observability failure of the Chat/offloaded evidence method, not evidence of a parser or current result-construction defect.

Do not claim that the Chat-host offload mechanism itself has been proven.

### F5_REAL_HOST_STRUCTURED_RESULT_FAIL

Use only if fresh-build identity is proven and the direct public invocation returns a missing, malformed, reordered, or wrong-MIME structured part.

Capture complete raw part metadata and stop. Do not repair product code.

### F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED

Use if repository/build identity, focused real-host launch, fixture access, tool registration, confirmation handling, or mutation safety cannot be proven.

Report the exact blocker and stop without fallback.

## 9. Final report

Report:

1. repository identity and initial status;
2. protected `request.md` hash/diff before and after;
3. exact authorized changed paths;
4. compile command and build identity;
5. real-host identity;
6. tool-registration evidence;
7. exact invocation count;
8. raw ordered content-part metadata;
9. decoded structured-data checks;
10. Markdown/structured parity;
11. QA workspace before/after comparison;
12. classification and narrowly supported conclusion;
13. final `git status --short --untracked-files=all`.

Confirm explicitly:

- no product code changed;
- no fixture changed;
- no package/version/lockfile changed;
- no existing test was weakened or reclassified;
- no full suite or Eval Golden ran;
- no external service or write flow ran;
- nothing was staged or committed;
- `.github/templates/request.md` is byte-for-byte unchanged from preflight.

End with exactly one marker:

F5_REAL_HOST_STRUCTURED_RESULT_PASS

or

F5_REAL_HOST_STRUCTURED_RESULT_FAIL

or

F5_REAL_HOST_STRUCTURED_RESULT_BLOCKED
