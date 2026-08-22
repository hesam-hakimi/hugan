TASK: LOCAL_HOTFIX_HF1_V2_FINAL_RELEASE_PREPARATION_CLEANUP

This is a narrowly bounded RELEASE-PREPARATION task after the independently
verified Repair 7.

Do NOT reopen or redesign Repair 5, Repair 6, or Repair 7.

The final independent re-audit established:

REPOSITORY_IDENTITY_VERIFIED: YES
ALL_LIVE_CONSUMER_WRITE_ROUTES_ENUMERATED: YES
ALL_RELEASE_RELEVANT_CONSUMER_WRITES_PHYSICALLY_CONTAINED: YES
WRITE_AUTHORIZATION_RUNTIME_SAFE: YES
STANDARD_UNIT_SUITE_INCLUDES_CONTAINMENT_REGRESSIONS: YES
MUTATION_PROBE_DETECTS_DISABLED_CONTAINMENT: YES
COMPILE_PASS: YES
LINT_PASS: YES
FOCUSED_TESTS_PASS: YES
FRESH_POST_REPAIR7_VSIX_BUILT: YES
FRESH_POST_REPAIR7_VSIX_VERIFIED: YES
PACKAGE_PROVENANCE_MATCHES_CURRENT_SOURCE: YES
SAFE_TO_BEGIN_QA_VSIX_TESTING: YES
SAFE_TO_RELEASE_HF1_V2: NO

The Repair-7 security implementation is accepted and must remain byte-identical.

The only remaining release-preparation work is:

1. remove unauthorized working-tree drift under .github/** while preserving
   its current content externally before restoration;
2. remove developer/CI-only files from the distributable VSIX;
3. harden package verification so the same files cannot silently return;
4. rebuild and verify one fresh clean QA VSIX;
5. report the Phase-H baseline refresh as a separate pre-merge chore.

Do not change production TypeScript code.

==================================================
1. AUTHORIZED REPOSITORY PATHS
==================================================

The only repository paths authorized for mutation are:

RESTORE/CLEAN ONLY:

1. .github/copilot-instructions.md
2. .github/instructions/source-conventions.instructions.md

PACKAGE POLICY:

3. .vscodeignore
4. src/test/verifyVsixContents.ts
5. src/test/suite/packageAssets.test.ts

No sixth repository source/config/test path may change.

A newly generated VSIX output is allowed.

An external backup directory under the operating-system temporary directory
is allowed and must remain outside the repository.

If any additional repository file is required, STOP before modifying it and
return:

LOCAL_HOTFIX_HF1_V2_RELEASE_PREP_SCOPE_AMENDMENT_REQUIRED

==================================================
2. PRESERVE REPAIR-7 SECURITY BYTES
==================================================

At task start, capture SHA-256 hashes for all Repair-7 security-relevant files,
including at minimum:

src/core/utils/PhysicalPathContainment.ts
src/core/trusted/WriteAuthorization.ts
src/core/trusted/index.ts
src/writers/RepoWriter.ts
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

Recalculate them at task end.

Any difference is an automatic failure.

No production TypeScript file may be edited in this task.

==================================================
3. SAFE PRESERVATION OF THE TWO .GITHUB CHANGES
==================================================

Before restoring or removing anything, create a unique external backup under:

$env:TEMP\HF1_V2_EXCLUDED_GITHUB_<timestamp>

or the equivalent platform temp path.

Preserve:

- the complete current content of
  .github/copilot-instructions.md;
- its complete Git diff against HEAD;
- the complete current content of
  .github/instructions/source-conventions.instructions.md;
- SHA-256 hashes for both current files;
- a small README describing their original repository paths and Git state.

The backup must be outside the repository.

Do not place it under repository .tmp/.

After independently confirming the external backup exists and its hashes
match the repository copies:

- restore `.github/copilot-instructions.md` exactly to HEAD;
- remove only the untracked
  `.github/instructions/source-conventions.instructions.md`
  from the working tree.

Do not modify any other `.github/**` path.

Then run:

npm run guard:github

Expected:

PASS / exit 0

Also prove:

git diff -- .github
git status --short -- .github

show no remaining `.github/**` drift.

==================================================
4. PACKAGE-HYGIENE ROOT CAUSE
==================================================

The independently verified post-Repair-7 VSIX still included:

ETL_HotFix.code-workspace
scripts/assert-control-plane-clean.mjs
scripts/validate-workflow.mjs
workflow/targets.yml

The audit proved these are developer/maintainer/CI assets and are not required
by extension runtime code under src/** or resources/**.

The workspace file is developer-local and references a sibling repository.

These files must not be distributed to QA/end users.

Do not delete them from the source tree.

Exclude them through package policy.

==================================================
5. .VSCODEIGNORE REPAIR
==================================================

Modify only `.vscodeignore`.

Add robust vsce/minimatch-compatible exclusions for:

**/*.code-workspace
scripts/**
workflow/**

Preserve all existing Repair-6 package-hygiene exclusions, including:

.tmp/**
nested .git/**
all tsbuildinfo variants
src/test/**
out/test/**
docs/eval/**
.vscode-test/**
*.log
*.vsix
node_modules/**

Do not exclude required runtime content.

Required runtime content must still include:

out/extension.js
out/sttm-runtime.js
package.json
resources/copilot/**
resources/prompts/**
resources/framework/**
required media assets

==================================================
6. VERIFIER HARDENING
==================================================

Modify only:

src/test/verifyVsixContents.ts

Extend the forbidden package-entry policy so it fails for:

extension/**/*.code-workspace
extension/scripts/**
extension/workflow/**

Retain all existing forbidden patterns.

The verifier must fail on representative examples such as:

extension/ETL_HotFix.code-workspace
extension/scripts/validate-workflow.mjs
extension/scripts/assert-control-plane-clean.mjs
extension/workflow/targets.yml

Do not weaken size ceilings, required-entry checks, manifest checks, content
markers, machine-path scanning, or previous package-security checks.

==================================================
7. PACKAGE-ASSET REGRESSION TESTS
==================================================

Modify only:

src/test/suite/packageAssets.test.ts

Add regression assertions proving:

- `.vscodeignore` excludes `*.code-workspace`;
- `.vscodeignore` excludes `scripts/**`;
- `.vscodeignore` excludes `workflow/**`;
- `verifyVsixContents` rejects those same representative entries;
- required framework and runtime resources remain included.

Ensure the ignore file and verifier cannot silently drift apart.

==================================================
8. VALIDATION BEFORE PACKAGING
==================================================

Using already-installed dependencies only, run:

npm run compile
npm run lint

Run focused tests for:

packageAssets
verifyVsixContents
physicalWriteContainment
repoContextInit
artifactReuseConversation
WriteAuthorization
RepoWriter workspace selection

Then run:

npm run test:unit

Expected functional result:

- no new failure;
- containment/security tests pass;
- the three protected Copilot customization failures may remain;
- the two EvalGating failures may remain as Phase-H baseline freshness failures;
- no additional failure is permitted.

Do not regenerate the Phase-H baseline in this task.

==================================================
9. BUILD ONE FRESH CLEAN QA VSIX
==================================================

After all code/config tests pass:

- build one fresh post-cleanup QA VSIX from the current source;
- use already-installed packaging tools only;
- do not download dependencies;
- do not install the VSIX;
- do not reuse any Repair-6 or pre-cleanup VSIX.

Use a distinguishable output name if the existing packaging mechanism permits,
for example:

databricks-etl-copilot-0.3.139-hf1-v2-qa-clean.vsix

No manual ZIP surgery.

==================================================
10. VERIFY THE NEW VSIX
==================================================

Run the repository's verifier against the fresh package.

Independently inspect the package contents.

Required:

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
NO developer-machine absolute paths
NO credentials or secrets
NO unrelated repository content

Required runtime content must remain present.

Report:

- VSIX exact path
- SHA-256
- entry count
- compressed size
- uncompressed size
- required-content result
- forbidden-content result
- provenance result

==================================================
11. PHASE-H BASELINE STATUS
==================================================

Do not modify the Phase-H baseline.

Report clearly:

- the two EvalGating failures are baseline freshness failures caused by the
  candidate's legitimate tracked-input changes;
- they are not functional regressions;
- baseline regeneration remains a separate explicitly authorized maintainer
  pre-merge task;
- the three Copilot customization failures remain pre-existing and outside this
  hotfix.

Do not label all five as unrelated historical failures.

Use the honest classification:

2 EXPECTED_BASELINE_REFRESH_REQUIRED
3 PRE_EXISTING_PROTECTED_CUSTOMIZATION_FAILURES
0 NEW_FUNCTIONAL_REGRESSIONS

==================================================
12. FINAL SCOPE PROOF
==================================================

At task end prove:

- Repair-7 security file hashes unchanged;
- only `.vscodeignore`,
  `src/test/verifyVsixContents.ts`, and
  `src/test/suite/packageAssets.test.ts`
  contain new intended package-policy changes;
- `.github/**` is clean and equal to HEAD;
- external backup path exists;
- staged count remains 0;
- Git commits/pushes remain 0;
- dependency installations/downloads remain 0;
- VSIX installations remain 0;
- consumer-repository mutations remain 0.

==================================================
13. FINAL REPORT
==================================================

Return:

1. External backup location and hashes.
2. Exact .github restoration result.
3. guard:github result.
4. Package-policy files changed.
5. `.vscodeignore` before/after behavior.
6. Verifier before/after behavior.
7. PackageAssets regression result.
8. Compile result.
9. Lint result.
10. Focused-test result.
11. Full-unit classification.
12. Fresh clean VSIX metrics.
13. Required entries present.
14. Forbidden entries absent.
15. Package provenance.
16. Repair-7 hash preservation.
17. Remaining pre-merge chores.

Finish with:

GITHUB_PROTECTED_PATHS_CLEAN: YES|NO
EXCLUDED_GITHUB_CHANGES_BACKED_UP_EXTERNALLY: YES|NO
GUARD_GITHUB_PASS: YES|NO
REPAIR7_SECURITY_BYTES_UNCHANGED: YES|NO
PACKAGE_WORKSPACE_FILE_EXCLUDED: YES|NO
PACKAGE_SCRIPTS_EXCLUDED: YES|NO
PACKAGE_WORKFLOW_EXCLUDED: YES|NO
PACKAGE_VERIFIER_COVERS_NEW_EXCLUSIONS: YES|NO
COMPILE_PASS: YES|NO
LINT_PASS: YES|NO
FOCUSED_TESTS_PASS: YES|NO
NEW_FUNCTIONAL_REGRESSIONS: YES|NO
FRESH_CLEAN_QA_VSIX_BUILT: YES|NO
FRESH_CLEAN_QA_VSIX_VERIFIED: YES|NO
PACKAGE_HYGIENE_SAFE: YES|NO
PACKAGE_PROVENANCE_MATCHES_CURRENT_SOURCE: YES|NO
PHASE_H_BASELINE_REFRESH_REQUIRED_BEFORE_MERGE: YES|NO
SAFE_TO_COMMIT_HF1_V2: YES|NO
SAFE_TO_BEGIN_FORMAL_QA_TESTING: YES|NO
SAFE_TO_RELEASE_HF1_V2: NO

End exactly:

LOCAL_HOTFIX_HF1_V2_FINAL_RELEASE_PREPARATION_CLEANUP_COMPLETE
