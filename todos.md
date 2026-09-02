# Phase 1B.3I — Seeded Copilot Dependency One-Shot Real-Host Run

Work locally in the currently open desktop VS Code repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

This is an operational characterization run, not an implementation task.

The preceding Phase 1B.3H read-only audit completed with:

- primary classification:
  F. DEPENDENCY_DISABLED_OR_REMOVED_IN_ISOLATED_PROFILE
- declared dependency: github.copilot-chat
- compatible application-bundled package found
- package version: 0.63.0
- engines.vscode: ^1.135.0
- extensionDependencies: absent/empty
- isolated extension packages: 0
- repository edits caused by the audit: 0
- QA edits: 0
- extension copies/installations: 0
- compiles: 0
- new Host launches: 0
- invokeTool calls: 0

This phase authorizes one fresh isolated run with the audited
github.copilot-chat package seeded into its isolated extensions directory.

## Absolute prohibitions

Do not edit any repository source, test, compiled, configuration or QA file.

Do not compile or invoke npm.

Do not stage, commit, stash, restore, reset, clean or switch worktrees.

Do not use:

- Cloud agents
- F5
- ETL Orchestrator
- Marketplace
- network downloads
- --install-extension
- VSIX installation
- the Code CLI for installation
- Start-Process
- an external wrapper or sidecar
- the real VS Code user profile
- retries or relaunches

Do not inspect credentials, tokens, authentication state or account contents.

The only permitted writes are inside one newly created Temp
isolation/evidence directory.

## Fixed audited state

Expected repository branch:

fix/workspace-write-completion-0.3.148

Expected HEAD:

45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected Git status, exactly and in this order:

 M .github/templates/request.md
 M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Audited dependency source:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\08d4889f9e\resources\app\extensions\copilot

Required manifest identity:

- canonical extension ID: github.copilot-chat
- version: 0.63.0
- engines.vscode: ^1.135.0
- extensionDependencies: absent or empty

Do not fabricate or seed github.copilot. It is not part of the declared
dependency closure.

QA root:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

Workbook:

C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982\sttm\synthetic_workbook.xlsx

Expected workbook size:

13201 bytes

Expected workbook SHA-256:

3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA

Focused suite title:

Phase 1B real host structured result characterization

Prior retained Host evidence directory — read-only and never reuse:

C:\Users\tag5916\AppData\Local\Temp\etl-phase-1b3g-c2-ea9575f1ed28431d9edd7b56d50830d7

## Step 1 — Read-only preflight gate
