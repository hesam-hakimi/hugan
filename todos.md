# Phase 1B.3H — Read-Only Copilot Dependency Visibility Audit

Continue in the current desktop VS Code GitHub Copilot Local normal-Agent
session and current repository folder.

The preceding Phase 1B.3G-C2 result is authoritative:

- runner invocations: 1
- real Extension Host launches attempted/proven: 1/1
- Host VS Code version: 1.135.0
- focused suite selected: 1
- test bodies evaluated: 0/8
- before-all failures: 1
- invokeTool calls: 0
- runner exit: 1
- classification: BLOCKED before the raw tool-result boundary

Activation failed with:

Cannot activate the 'Databricks ETL Copilot' extension because it depends
on unknown extension 'github.copilot-chat'.

Retained evidence directory:

C:\Users\tag5916\AppData\Local\Temp\etl-phase-1b3g-c2-ea9575f1ed28431d9edd7b56d50830d7

This phase is READ-ONLY DIAGNOSIS ONLY.

Do not edit or compile.
Do not launch another Extension Host.
Do not invoke the runner, Code.exe, F5, npm, invokeTool or any ETL tool.
Do not install, copy, move, rename, update, enable or disable an extension.
Do not access Marketplace or the network.
Do not modify the repository, QA root, installed VS Code, user profile,
retained evidence, or environment variables.
Do not read authentication tokens, credential stores, secrets or Copilot
account data.

## Step 1 — Preserve and verify state

Verify:

- repository path, branch, HEAD and exact three-line Git status;
- protected request.md hash;
- current runTest.ts and focused-test hashes;
- all five compiled hashes;
- QA 23-file inventory and workbook identity;
- retained evidence directory and its existing files.

Require zero changes since Phase 1B.3G-C2.

## Step 2 — Verify the declared dependency

Read the repository package.json and report:

- extension publisher;
- extension name and canonical ID;
- version;
- complete extensionDependencies array;
- exact spelling and casing of the Copilot dependency.

Determine whether the declared canonical dependency is:

github.copilot-chat

Do not change the manifest.

## Step 3 — Inventory installed Copilot extension packages

Using PowerShell filesystem and JSON reads only, inspect the following
candidate locations when they exist:

1. Installed VS Code application extensions:

   C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\resources\app\extensions

2. User-installed extensions:

   C:\Users\tag5916\.vscode\extensions

3. Any extension directory explicitly recorded in the retained Host launch
   evidence.

4. The exact isolated extensions directory created by Phase 1B.3G-C2.

For every candidate package related to GitHub Copilot or Copilot Chat,
read only its package.json and record:

- absolute directory;
- publisher;
- name;
- canonical lowercase `${publisher}.${name}` ID;
- displayName;
- version;
- engines.vscode;
- extensionKind;
- extensionDependencies;
- package.json SHA-256;
- whether it is application-bundled, user-installed, or isolated-run content.

Do not identify an extension from its folder name alone. Derive its ID from
publisher and name in package.json.

Explicitly determine whether these IDs exist and where:

- github.copilot
- github.copilot-chat

## Step 4 — Inspect installed VS Code product metadata

Read only:

C:\Users\tag5916\AppData\Local\Programs\Microsoft VS Code\resources\app\product.json

Report relevant entries from:

- defaultChatAgent;
- builtInExtensions;
- builtInExtensionsEnabledWithAutoUpdates;
- any other product entry referencing GitHub.copilot or
  GitHub.copilot-chat.

Do not invoke Code.exe and do not update anything.

Determine whether product metadata references an extension whose physical
package is absent, present under another ID, or present only outside the
isolated scan path.

## Step 5 — Inspect the failed Host’s actual scan evidence

Read the retained evidence directory and isolated user-data logs.

Search only for relevant lines containing:

- github.copilot
- github.copilot-chat
- unknown extension
- extensionDependencies
- extension scan
- extensionDevelopmentPath
- extensions-dir
- user-data-dir
- disable-extensions
- activation

Report:

- exact executable used;
- exact Host launch arguments;
- exact user-data directory;
- exact extensions directory;
- whether --disable-extensions was absent;
- which Copilot IDs the failed Host actually discovered;
- which Copilot IDs were absent;
- whether an extension was found but rejected as incompatible, disabled,
  removed, or duplicate;
- the precise log evidence for the activation failure.

Do not modify or clean the retained directory.

## Step 6 — Determine dependency closure

If github.copilot-chat exists anywhere locally:

1. Read its manifest.
2. Recursively identify only its declared extensionDependencies.
3. For each dependency, locate its exact installed directory, version,
   engine compatibility and package manifest hash.
4. Produce the minimum complete dependency closure required by the isolated
   Host.

Do not copy the closure in this phase.

## Root-cause classification

Choose exactly one primary classification supported by direct evidence:

A. DEPENDENCY_NOT_INSTALLED_LOCALLY

B. DEPENDENCY_PRESENT_IN_USER_EXTENSION_DIR_BUT_EXCLUDED_BY_ISOLATION

C. DEPENDENCY_PRESENT_IN_VSCODE_APPLICATION_BUT_NOT_SCANNED_BY_HOST

D. DEPENDENCY_ID_MISMATCH

E. DEPENDENCY_ENGINE_INCOMPATIBLE

F. DEPENDENCY_DISABLED_OR_REMOVED_IN_ISOLATED_PROFILE

G. MULTIPLE_CAUSES

H. NOT_DETERMINED

Do not infer the cause only from the activation error.

## Recommendation

Recommend exactly one smallest safe next action, but do not implement it.

Prefer a deterministic isolated solution. Compare only when supported:

1. Seed the next unique isolated extensions directory with the exact existing
   compatible dependency closure.

2. Reference an existing extension directory read-only if the runner already
   supports it safely.

3. Use the application-bundled extension if direct evidence proves why it was
   omitted and how the runner can expose it.

Do not recommend Marketplace download, changing package.json dependencies,
using the real VS Code profile broadly, or removing the dependency unless
direct evidence proves that is the correct product design.

For the recommended action provide:

- exact source extension directories;
- exact destination concept;
- complete dependency closure;
- versions and engine compatibility;
- required runner/configuration change, if any;
- whether another compile is necessary;
- risks and integrity guards for one newly authorized Host run.

## Final response

Report:

- repository and QA integrity;
- declared dependency ID;
- every located Copilot package and canonical ID;
- product.json findings;
- failed Host launch/scan findings;
- minimum dependency closure;
- exact root-cause classification;
- one smallest safe recommended next action.

Confirm:

- repository edits: 0
- QA edits: 0
- extension copies/installations: 0
- compiles: 0
- new Host launches: 0
- invokeTool calls: 0

End with exactly one marker:

F5_LOCAL_COPILOT_DEPENDENCY_AUDIT_COMPLETE

or

F5_LOCAL_COPILOT_DEPENDENCY_AUDIT_BLOCKED
