TASK: HF1_V2_RECOVERY_BRANCH_OWNER_PRODUCT_REVIEW

ROLE
Act as a read-only product reviewer.

This is a short owner-level product-diff review, not a governance certification
and not another full validation cycle.

REPOSITORY
Recovery worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:
recovery/extension-product-0.3.147

Expected base HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

IMPLEMENTATION RESULT
The recovery task reported:

- 107 transferred product files;
- 39 governance files excluded;
- 17 unrelated files excluded;
- one new scripts/product-verify.mjs;
- package version 0.3.147;
- compile and lint passing;
- Repair 11/12/13 passing;
- Product Verify passing;
- full unit: 2294 passing, 5 pending, 2 failing;
- F1 and F3 unchanged;
- no functional or security regression;
- temporary VSIX: 66 entries;
- required package entries: 54/54;
- forbidden entries: 0;
- no commit, installation or Runtime QA performed.

REVIEW OBJECTIVE
Determine whether the recovery branch contains only intentional ETL Extension
product changes and is safe to commit.

Do not edit, delete, restore, stage, commit, push, package, install or start
Runtime QA.

1. IDENTITY CHECK

Verify:

- repository root;
- branch;
- HEAD/base;
- staged and stash state;
- package version;
- worktree status.

Stop if the worktree or branch does not match the expected recovery state.

2. REVIEW THE COMPLETE DIFF

Inspect every changed path relative to the base HEAD.

Group the changed files into:

- runtime implementation;
- packaged consumer resources;
- product tests and fixtures;
- canonical generated evaluation baseline;
- product verification mechanism;
- package metadata;
- documentation;
- unexpected or unrelated.

For each group report:

- file count;
- purpose;
- whether it is required;
- whether it should be committed.

Do not accept a file merely because it was present in the previous dirty tree.

3. REVIEW THE 107 TRANSFERRED FILES

Prove that each transferred file is required for at least one of:

- actual Extension runtime behavior;
- packaged consumer Agent/resource behavior;
- focused regression coverage;
- canonical product evaluation;
- VSIX packaging.

Flag any file that belongs to:

- governance framework;
- temporary evidence;
- checkpoint machinery;
- unrelated documentation;
- generated build output;
- old VSIX artifacts;
- local environment configuration;
- portfolio/poster work;
- unrelated pre-existing modifications.

4. PACKAGE.JSON REVIEW

Inspect the complete package.json diff against the base HEAD.

Explicitly report:

- version change;
- dependency changes;
- devDependency changes;
- script changes;
- contribution/activation changes;
- packaged resource changes.

Investigate @vscode/vsce 3.9.2 specifically.

Determine whether it is:

- intentionally required by product:verify and repeatable local packaging;
- already required by the existing canonical package workflow;
- or an unrelated pre-existing modification that should not enter this branch.

Do not accept it only because it existed in the dirty source tree.

PACKAGE_JSON_INTENTIONAL must be NO if any unexplained field other than the
authorized version and product-verification changes is present.

5. PHASE H REPORT REVIEW

Inspect:

- docs/eval/phase_h_latest_report.json
- docs/eval/phase_h_latest_report.md

Verify:

- they were canonically regenerated;
- JSON and Markdown agree semantically;
- thresholds, scenarios, gates and assertions were not weakened;
- changes are limited to legitimate tracked-input refreshes;
- volatile latency fields are not being treated as product behavior;
- the reports are actually required by EvalGating.

Flag them if they were manually edited or transferred only to make a test pass.

6. PRODUCT VERIFY REVIEW

Inspect scripts/product-verify.mjs and its package.json command.

Confirm it is small and deterministic and only checks:

- compile/lint/focused validation orchestration where appropriate;
- required packaged entries;
- forbidden packaged entries;
- identity/version consistency;
- temporary VSIX creation;
- absence of repository pollution.

Confirm it does not:

- rewrite baselines;
- suppress failures;
- alter the working tree;
- add governance/checkpoint behavior;
- rely on machine-specific absolute paths;
- silently exclude unexpected package files.

Run npm run product:verify once.

Do not rerun the canonical full-unit suite; it was already completed once during
recovery. This review is about the diff and package contract.

7. PACKAGE RESOURCE REVIEW

Verify the six packaged consumer Agent resources are derived from the canonical
product sources and are not stale or hand-edited copies.

Confirm:

- Agent tool sets were not broadened;
- user-invocable behavior was not broadened unexpectedly;
- no write/install/execute/deploy authority was added;
- runtime resources required for the structured diagnostic fix are present.

8. FINAL REPORT

Return:

IDENTITY_GATE
TOTAL_CHANGED_PATHS
RUNTIME_FILE_COUNT
PACKAGED_RESOURCE_FILE_COUNT
TEST_AND_FIXTURE_FILE_COUNT
EVAL_BASELINE_FILE_COUNT
DOCUMENTATION_FILE_COUNT
UNEXPECTED_FILE_COUNT
ALL_107_TRANSFERS_INTENTIONAL
UNRELATED_TRANSFERRED_PATHS
GOVERNANCE_FILES_PRESENT
PACKAGE_VERSION
PACKAGE_JSON_INTENTIONAL
VSCE_3_9_2_DISPOSITION
PHASE_H_REFRESH_LEGITIMATE
EVAL_ASSERTIONS_WEAKENED
PRODUCT_VERIFY_DESIGN_ACCEPTABLE
PRODUCT_VERIFY_PASS
PACKAGE_REQUIRED_ENTRIES
PACKAGE_FORBIDDEN_ENTRIES
NEW_AGENT_AUTHORITY
NEW_FUNCTIONAL_REGRESSIONS
NEW_SECURITY_REGRESSIONS
READY_TO_COMMIT_RECOVERY_BRANCH
READY_TO_INSTALL
READY_FOR_RUNTIME_QA

Allowed verdicts:

- PASS_READY_TO_COMMIT_RECOVERY_BRANCH
- BLOCKED_UNRELATED_TRANSFER
- BLOCKED_PACKAGE_METADATA_DEFECT
- BLOCKED_EVAL_BASELINE_DEFECT
- BLOCKED_PRODUCT_VERIFY_DEFECT
- OWNER_DECISION_REQUIRED

Do not make corrections. Report the minimum exact paths requiring correction.
