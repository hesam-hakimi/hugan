# Phase 1B.3J — Read-Only Dependency Contract and Supported Host Strategy Audit

Work locally in the currently open desktop VS Code repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

This phase is strictly read-only.

Do not:

- edit any repository, compiled, installed-product or QA file;
- compile or run tests;
- invoke npm;
- create another isolation root;
- copy or install any extension;
- invoke the runner;
- launch Code.exe or an Extension Host;
- call vscode.lm.invokeTool;
- use Marketplace or network access;
- use F5, Cloud, ETL Orchestrator or another worktree;
- stage, commit, stash, restore, reset or clean;
- inspect credentials, tokens or account contents.

## Authoritative preceding result

Phase 1B.3I performed exactly one seeded-dependency Host run.

Observed:

- one seeded github.copilot-chat@0.63.0 was discovered;
- VS Code explicitly skipped it “in favour of the builtin extension”;
- the effective Extension Host still reported github.copilot-chat as unknown;
- Databricks ETL Copilot failed activation in its before-all hook;
- test bodies executed: 0 of 8;
- passes: 0;
- failures: 1 before-all failure;
- vscode.lm.invokeTool calls: 0;
- Host launches: 1;
- retries/relaunches: 0;
- repository edits caused by the phase: 0;
- QA edits: 0.

Primary classification:

F. DEPENDENCY_DISABLED_OR_REMOVED_IN_ISOLATED_PROFILE

Refinement:

SEEDED_COPY_DISCOVERED_BUT_SHADOWED_BY_BUILTIN

Retained evidence root:

C:\Users\tag5916\AppData\Local\Temp\etl-phase-1b3i-seeded-20260902-113624-f3a807760bbe

Repository state:

Branch:
fix/workspace-write-completion-0.3.148

HEAD:
45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Expected Git status, exactly:

 M .github/templates/request.md
 M src/test/runTest.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

The QA root correctly contains 23 files. Do not repeat the prior invalid
assumption that the QA root should contain only the workbook.

## Goal

Determine whether:

extensionDependencies: ["github.copilot-chat"]

is a genuine runtime requirement of the ETL extension or only a manifest-level
activation gate that is unnecessary for registering and directly invoking the
ETL Language Model Tool.

Then identify exactly one evidence-supported next implementation/test path.

Do not implement or execute that path in this phase.

## Step 1 — Integrity verification

Read the retained Phase 1B.3I evidence and verify:

1. repository path, branch, HEAD and exact Git status;
2. protected-file identity;
3. current runner and focused-test identities;
4. all five compiled artifact identities;
5. QA inventory remains exactly 23 files;
6. workbook remains 13201 bytes with SHA-256:

   3F9743877E50B46C50AD398FEF1CD649281C1E74188D8E942A8875465798F3AA

7. the seeded source/destination comparison remained 98 of 98 files with
   zero mismatches;
8. no matching isolated Host process remains.

Use hashes read directly from disk and retained evidence. Do not transcribe
hashes from screenshots or OCR.

If integrity differs, report the exact difference and stop without mutation.

## Step 2 — Map the authoritative manifest chain

Locate every manifest involved in building and packaging:

td-etl.databricks-etl-copilot

Map, without editing:

authoritative source manifest
→ build/package transformation
→ packaged manifest
→ currently compiled/installed development manifest

For every occurrence of either:

github.copilot-chat
GitHub.copilot-chat
github.copilot

report:

- exact file and JSON/property path;
- whether it is tracked source, generated output or installed-product data;
- whether it affects activation, packaging, recommendations or UI only;
- whether changing the authoritative occurrence automatically updates the
  packaged occurrence.

Identify exactly which authoritative file owns:

extensionDependencies: ["github.copilot-chat"]

Do not assume that the repository-root package.json is the packaged extension
manifest unless the build chain proves it.

## Step 3 — Prove or disprove a functional Copilot dependency

Search tracked source, compiled output and focused tests for direct use of:

- vscode.extensions.getExtension('github.copilot-chat');
- activation of github.copilot-chat;
- Copilot extension exports;
- Copilot-specific commands;
- Copilot-specific context keys;
- imports or requires from Copilot packages;
- authentication or session APIs supplied by Copilot;
- any code path that cannot execute without Copilot Chat activation.

Separately map the ETL tool implementation:

- contributes.languageModelTools declaration;
- activation event responsible for ETL tool registration;
- vscode.lm.registerTool call;
- tool ID etl_interpret_sttm;
- vscode.lm.invokeTool usage in the focused test;
- LanguageModelToolResult creation;
- LanguageModelTextPart creation;
- LanguageModelDataPart creation;
- application/json DataPart construction.

For every relevant result distinguish:

- VS Code core API dependency;
- Copilot-extension API dependency;
- Node/npm dependency;
- manifest-only dependency;
- no dependency.

Do not infer a functional dependency merely because the string appears in
extensionDependencies, recommendations or documentation.

## Step 4 — Verify the VS Code 1.135.0 API contract

Using the installed VS Code 1.135.0 API declarations, the repository’s
@types/vscode version and locally installed documentation/source, determine:

1. whether vscode.lm.registerTool is a core API in this supported version;
2. whether vscode.lm.invokeTool is a core API;
3. whether either call requires Copilot Chat to be activated;
4. whether the languageModelTools contribution point requires
   github.copilot-chat;
5. whether enabledApiProposals or a Copilot-provided proposed API is used;
6. whether direct programmatic invokeTool requires a language-model provider,
   sign-in or chat UI;
7. whether the existing focused test exercises only direct tool registration
   and invocation.

Explicitly separate:

- tool registration/invocation;
- presenting the tool to an AI model or Agent UI;
- selecting or calling a language model.

These are not automatically the same dependency contract.

## Step 5 — Evaluate the manifest-only hypothesis

Evaluate this exact hypothesis:

“The ETL extension uses only VS Code core Language Model Tool APIs.
It consumes no API, export, command, authentication state or runtime service
from github.copilot-chat. Therefore extensionDependencies creates an
unnecessary hard activation gate and may be removed without changing the
tool’s registration or direct-invocation behavior.”

Classify it as:

PROVED
DISPROVED
UNRESOLVED

A PROVED result requires all of the following:

- no functional Copilot API/export/command/context dependency;
- registerTool and invokeTool are supported core APIs;
- languageModelTools is declared by the ETL extension itself;
- direct focused invocation does not select or call a language model;
- no relevant proposed API is supplied by Copilot Chat;
- the authoritative manifest path is known;
- packaged-manifest propagation is understood.

## Step 6 — Conditional supported test strategy

If the manifest-only hypothesis is PROVED:

Recommend a narrowly scoped future patch plan only.

The plan must specify:

- exact authoritative manifest file/property to change;
- whether any generated/package manifest must also be updated or regenerated;
- the smallest static/manifest regression test needed;
- one compile;
- one later isolated Host run;
- no dependency seed;
- no real user profile;
- no Marketplace/network access.

Do not apply the patch now.

If the hypothesis is DISPROVED because a real Copilot API dependency exists:

Inspect, read-only, whether the installed @vscode/test-electron contract
supports extensionDevelopmentPath as string[].

Determine whether a future test could load both:

1. the ETL repository extension; and
2. the audited application-bundled Copilot extension

as explicit development extensions in one temporary isolated profile.

Also determine whether development-extension precedence is proven to bypass
the observed built-in shadowing.

Do not recommend this path unless both array support and precedence behavior
are proven from installed code.

If neither path is fully proved, report NO_SAFE_PATH_YET and identify the
single smallest missing observation or instrumentation needed next.

Do not recommend normal-profile execution unless all isolated supported paths
are disproved. The real profile must remain the last resort because it can
hide packaging defects and introduce user-state/authentication effects.

## Final decision

Return exactly one primary decision:

A. MANIFEST_ONLY_DEPENDENCY_REMOVAL_SUPPORTED

B. FUNCTIONAL_DEPENDENCY_REQUIRES_MULTI_DEVELOPMENT_PATH_TEST

C. NO_SAFE_PATH_YET

For the chosen decision report:

- direct evidence;
- exact authoritative files involved;
- proposed future delta;
- why the delta should cross the activation boundary;
- remaining risks;
- exact preflight required before another one-shot Host launch.

Also report these counters:

- repository edits: 0
- QA edits: 0
- compiled-file edits: 0
- extension copies/installations: 0
- compiles: 0
- runner invocations: 0
- Host launches: 0
- invokeTool calls: 0

End with exactly:

F5_LOCAL_DEPENDENCY_CONTRACT_AUDIT_COMPLETE
