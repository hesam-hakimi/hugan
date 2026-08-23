TASK: LOCAL_HOTFIX_HF1_V2_QA_VERSION_BUMP_0_3_140

Perform a narrowly bounded version-bump and QA-package generation task for the
already validated HF1 V2 candidate.

This is NOT another repair.

Do NOT reopen, redesign, or modify Repair 5, Repair 6, Repair 7, workspace
selection, physical containment, write authorization, framework resolution,
Oracle validation, artifact generation, or package-hygiene architecture.

The current accepted QA package is:

databricks-etl-copilot-0.3.139-hf1-v2-qa-clean.vsix

Its internal extension version is still:

0.3.139

The required new QA version is:

0.3.140

The required new output package is:

databricks-etl-copilot-0.3.140-hf1-v2-qa-clean.vsix

Do NOT rename the existing 0.3.139 VSIX.

The new version must be represented inside the VSIX metadata.

==================================================
1. EXPECTED REPOSITORY IDENTITY
==================================================

Work only in:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch:

hotfix/hf1-oracle-fresh-consumer-v2

Expected base HEAD:

b2e44c3a1a051aa7fa6008831d225bc06d22e847

Expected origin:

https://github.com/TD-Universe/agentic_etl.git

Expected current package version:

0.3.139

Before mutation, independently verify:

- repository root;
- branch;
- HEAD;
- origin;
- staged count;
- `.github/**` is clean;
- `package-lock.json` is absent or unchanged;
- the current `package.json` version is exactly `0.3.139`;
- the existing HF1 candidate changes are still present.

If repository identity does not match, STOP.

==================================================
2. ONE CONSOLIDATED AUTHORIZATION
==================================================

Request one consolidated authorization covering:

- modification of exactly one tracked repository file:
  `package.json`;
- changing only the version value from `0.3.139` to `0.3.140`;
- compile, lint, focused tests, full unit tests;
- creation of exactly one fresh `0.3.140` QA VSIX;
- verification and read-only inspection of that exact VSIX;
- no dependency installation or download;
- no Git mutation;
- no commit or push;
- no VSIX installation;
- no consumer-repository mutation.

Authorization token:

APPLY_HF1_V2_QA_VERSION_BUMP_0_3_140

Do not edit before authorization.

==================================================
3. EXACT SOURCE SCOPE
==================================================

The only tracked repository file authorized for modification is:

package.json

No second source/config/test file may be modified.

The only intended source change is:

"version": "0.3.139"

to:

"version": "0.3.140"

Preserve all other existing HF1 V2 changes already present in `package.json`.

Do not reset, reformat, reorder, normalize, or rewrite unrelated JSON content.

Do not modify:

- package-lock.json;
- `.vscodeignore`;
- any TypeScript file;
- any test file;
- `.github/**`;
- resources/prompts/**;
- framework/Oracle contracts;
- AGENT.md or AGENTS.md;
- Phase-H baselines;
- consumer repositories;
- etl-framework-adb.

If another tracked repository file appears necessary, STOP before modifying it
and return:

LOCAL_HOTFIX_HF1_V2_VERSION_BUMP_SCOPE_AMENDMENT_REQUIRED

==================================================
4. PRESERVE ACCEPTED SECURITY AND PACKAGE-POLICY BYTES
==================================================

Before editing, capture SHA-256 hashes for all accepted Repair-7 and
release-preparation security files, including at minimum:

src/core/utils/PhysicalPathContainment.ts
src/core/trusted/WriteAuthorization.ts
src/core/trusted/index.ts
src/writers/RepoWriter.ts
src/core/artifacts/NewArtifactWriter.ts
src/core/artifacts/ArtifactPatchApplier.ts
src/customization/ScaffoldedAssetWriter.ts
src/customization/WorkflowTargetResolver.ts
src/customization/CopilotWorkflowInitializer.ts
src/customization/CopilotWorkflowUpgrader.ts
src/customization/CopilotWorkflowRepairer.ts
src/customization/GeneratedAssetGitignoreManager.ts
src/customization/CopilotWorkflowDeleter.ts
src/customization/RepoContextInitializer.ts
src/test/suite/physicalWriteContainment.test.ts
src/test/testPatterns.ts
.vscodeignore
src/test/verifyVsixContents.ts
src/test/suite/packageAssets.test.ts

Recalculate every hash at task end.

All must remain byte-identical.

==================================================
5. VERSION UPDATE
==================================================

Modify only the `version` field in `package.json`:

0.3.139 → 0.3.140

Verify these fields remain unchanged:

- name;
- displayName;
- publisher;
- engines;
- main;
- activationEvents;
- contributes;
- scripts;
- dependencies;
- devDependencies;
- configuration;
- extension metadata.

Return a minimal diff proving only the version value changed in this task.

==================================================
6. VALIDATION BEFORE PACKAGING
==================================================

Using already-installed dependencies only, run:

npm run compile
npm run lint

Run focused tests covering:

- packageAssets;
- verifyVsixContents;
- physicalWriteContainment;
- repoContextInit;
- artifactReuseConversation;
- WriteAuthorization;
- RepoWriter workspace selection;
- HF1 V2 Repair-5/6/7 regression suites.

Then run:

npm run test:unit

Expected classification:

2 EXPECTED_BASELINE_REFRESH_REQUIRED
3 PRE_EXISTING_PROTECTED_CUSTOMIZATION_FAILURES
0 NEW_FUNCTIONAL_REGRESSIONS

No additional test failure is permitted.

Do not regenerate the Phase-H baseline.

Do not repair the three protected customization failures.

==================================================
7. BUILD EXACTLY ONE FRESH 0.3.140 QA VSIX
==================================================

Only after compile, lint, and focused tests pass, build a new package from the
current source using already-installed local/global packaging tools.

Do not use npx in a way that downloads anything.

Do not install dependencies.

Do not reuse or rename:

databricks-etl-copilot-0.3.139-hf1-v2-qa-clean.vsix

Do not reuse any Repair-6 package.

The exact required output filename is:

databricks-etl-copilot-0.3.140-hf1-v2-qa-clean.vsix

Pass the output filename explicitly to the packaging tool so no ambiguous
default package is selected.

Do not delete older VSIX files in this task.

Do not manually edit the VSIX archive.

==================================================
8. VERIFY INTERNAL VERSION METADATA
==================================================

Open and independently inspect the new VSIX.

Verify:

1. the output filename contains `0.3.140`;

2. inside:

   extension/package.json

   the value is:

   "version": "0.3.140"

3. inside:

   extension.vsixmanifest

   the extension identity version is exactly:

   0.3.140

4. the extension name and publisher are unchanged;

5. no package metadata still declares `0.3.139`.

A renamed file with internal version `0.3.139` is an automatic FAIL.

==================================================
9. RUN PACKAGE VERIFICATION AGAINST THE EXACT NEW FILE
==================================================

Run the repository VSIX verifier by passing the exact new `0.3.140` path.

Do not allow the verifier to select a VSIX by newest modification time.

Verify the exact package:

databricks-etl-copilot-0.3.140-hf1-v2-qa-clean.vsix

Required forbidden-content result:

NO *.code-workspace
NO extension/scripts/**
NO extension/workflow/**
NO extension/.tmp/**
NO nested .git/**
NO *.tsbuildinfo*
NO node_modules/**
NO src/test/**
NO out/test/**
NO docs/eval/**
NO .vscode-test/**
NO *.log
NO nested *.vsix
NO unrelated repositories
NO developer-machine absolute paths
NO credentials or secrets

Required runtime content must remain present:

- extension/out/extension.js;
- extension/out/sttm-runtime.js;
- extension/package.json;
- resources/copilot/**;
- resources/prompts/**;
- resources/framework/**;
- required media/runtime assets.

==================================================
10. COMPARE 0.3.139 AND 0.3.140 PACKAGES
==================================================

If the validated clean `0.3.139` package is present, use it only as a
read-only comparison baseline.

Compare archive entry names and uncompressed content hashes.

Expected:

- the runtime entry set remains equivalent;
- package hygiene remains equivalent;
- Repair-7 runtime/security content remains unchanged;
- version-bearing metadata changes from `0.3.139` to `0.3.140`.

Identify the exact archive entries whose bytes differ.

Expected version-related differences should be limited to metadata such as:

- extension/package.json;
- extension.vsixmanifest;

and any package metadata directly derived from those values.

If compiled runtime JavaScript or framework/resource bytes differ unexpectedly,
STOP and report the exact entries.

Do not dismiss unexpected runtime drift.

==================================================
11. PACKAGE METRICS
==================================================

Report for the new VSIX:

- exact absolute path;
- filename;
- internal version;
- publisher;
- SHA-256;
- archive entry count;
- compressed file size;
- total compressed-entry size if available;
- total uncompressed size;
- largest entry;
- build timestamp;
- verification result.

The package must remain within the existing configured size ceilings.

==================================================
12. EXACT SOURCE-SCOPE PROOF
==================================================

At task end prove:

- `package.json` is the only tracked repository file changed by this task;
- only its version field changed;
- all Repair-7 security hashes match task-start hashes;
- all package-policy hashes match task-start hashes;
- `.github/**` remains clean;
- staged count remains 0;
- Git commits remain 0;
- Git pushes remain 0;
- dependency installs/downloads remain 0;
- VSIX installations remain 0;
- consumer-repository mutations remain 0;
- etl-framework-adb remains untouched;
- Phase-H baseline remains untouched.

The new `.vsix` output is allowed and must remain uninstalled.

==================================================
13. QA HANDOFF DECISION
==================================================

The exact QA handoff artifact must be:

databricks-etl-copilot-0.3.140-hf1-v2-qa-clean.vsix

Explicitly state that QA must not use:

- databricks-etl-copilot-0.3.139.vsix;
- databricks-etl-copilot-0.3.139-hf1-v2-qa-clean.vsix;
- etl-hf1-v2-repair6-qa.vsix;
- any other older VSIX.

Do not install the new VSIX during this task.

==================================================
14. REQUIRED FINAL REPORT
==================================================

Return:

1. Repository identity.
2. Authorization used.
3. Exact source diff.
4. `package.json` before/after version.
5. Compile result.
6. Lint result.
7. Focused-test result.
8. Full-unit classification.
9. New VSIX path.
10. Internal `extension/package.json` version.
11. Internal `extension.vsixmanifest` version.
12. New VSIX SHA-256 and metrics.
13. Package-verification result.
14. Required-content proof.
15. Forbidden-content proof.
16. 0.3.139 versus 0.3.140 archive comparison.
17. Repair-7 hash-preservation result.
18. Exact scope/no-touch proof.
19. Exact artifact approved for QA handoff.
20. Remaining pre-merge chores.

Finish exactly:

SOURCE_VERSION_BEFORE: 0.3.139
SOURCE_VERSION_AFTER: 0.3.140
VSIX_PACKAGE_JSON_VERSION: 0.3.140|OTHER
VSIX_MANIFEST_VERSION: 0.3.140|OTHER
PACKAGE_FILENAME_VERSION_CORRECT: YES|NO
ONLY_PACKAGE_JSON_SOURCE_CHANGED_BY_TASK: YES|NO
REPAIR7_SECURITY_BYTES_UNCHANGED: YES|NO
PACKAGE_POLICY_BYTES_UNCHANGED: YES|NO
GITHUB_PROTECTED_PATHS_CLEAN: YES|NO
COMPILE_PASS: YES|NO
LINT_PASS: YES|NO
FOCUSED_TESTS_PASS: YES|NO
NEW_FUNCTIONAL_REGRESSIONS: YES|NO
FRESH_0_3_140_QA_VSIX_BUILT: YES|NO
FRESH_0_3_140_QA_VSIX_VERIFIED: YES|NO
PACKAGE_HYGIENE_SAFE: YES|NO
PACKAGE_PROVENANCE_MATCHES_CURRENT_SOURCE: YES|NO
SAFE_TO_HANDOFF_0_3_140_TO_QA: YES|NO
SAFE_TO_RELEASE_HF1_V2: NO

Then exactly one final marker:

LOCAL_HOTFIX_HF1_V2_QA_VERSION_BUMP_0_3_140_COMPLETE

or:

LOCAL_HOTFIX_HF1_V2_QA_VERSION_BUMP_0_3_140_BLOCKED

or:

LOCAL_HOTFIX_HF1_V2_VERSION_BUMP_SCOPE_AMENDMENT_REQUIRED

Do not commit.
Do not push.
Do not install the VSIX.
Stop after the final report.
