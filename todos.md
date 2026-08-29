TASK: HF1_V2_PRODUCT_RECOVERY_AND_FAST_VERIFICATION

ROLE
Act as the ETL Extension Product Recovery Implementer.

PRIMARY OBJECTIVE
Escape the governance-validation loop and reconstruct a clean, product-focused
development lane containing only the real ETL Extension implementation, relevant
tests, package assets and one small deterministic verification command.

This is not a governance-framework repair task.

OWNER AUTHORIZATION
You are authorized to:

1. Inspect the current repository and dirty working tree.
2. Create a new clean Git worktree and branch:
   recovery/extension-product-0.3.147
3. Selectively transfer verified product changes into that worktree.
4. Add one minimal deterministic product/package verification mechanism.
5. Run compile, lint, focused tests and one canonical full-unit run.
6. If and only if the recovered product passes validation, change only the package
   version from 0.3.146 to 0.3.147 and build a temporary VSIX for inspection.

You are not authorized to commit, push, merge, tag, release, install the extension,
start Runtime QA, reset, clean, delete, stash or overwrite the current working tree.

NON-DESTRUCTIVE RULE
The current repository contains valuable uncommitted work.

Do not run:

- git reset
- git clean
- git checkout -- <path>
- git restore <path>
- destructive remove/delete commands
- broad copy operations over the existing repository

The current working tree must remain byte-identical throughout this task.

PHASE 1 — PRESERVE AND UNDERSTAND CURRENT STATE

Before any write:

1. Record:
   - repository root;
   - origin;
   - branch;
   - HEAD;
   - package version;
   - tracked modifications;
   - untracked files;
   - ignored files;
   - staged files;
   - stash entries;
   - existing VSIX inventory.

2. Create an independent path/size/SHA-256 snapshot of the complete current
   working tree in OS temporary storage.

3. Identify changes belonging to these categories:

   A. Product runtime:
      - src/core/**
      - src/tools/**
      - src/customization/**
      - other actual Extension runtime paths

   B. Product tests:
      - focused tests directly exercising changed runtime behavior
      - Repair 11, 12 and 13 tests
      - Runtime QA support fixtures

   C. Packaged consumer resources:
      - resources/copilot/**
      - package/runtime assets required inside VSIX

   D. Governance-only:
      - .github/agent-governance/**
      - scripts/agent-governance/**
      - governance schemas, checkpoints and evidence machinery

   E. Generated/evidence/temp:
      - out/**
      - *.tsbuildinfo
      - generated reports
      - temporary mirrors
      - evidence packets
      - existing VSIX artifacts

4. Produce an exact candidate transfer list before copying.

Do not transfer an entire directory merely because some files within it are useful.

PHASE 2 — CREATE CLEAN PRODUCT WORKTREE

Create a separate clean Git worktree based on the current verified HEAD using the
new branch:

recovery/extension-product-0.3.147

Requirements:

- Do not modify the original working tree.
- Do not use the original dirty tree as the worktree destination.
- Verify the new worktree is clean before transferring anything.
- Use an explicit, unique sibling or temporary directory.
- Record its absolute path.

If the branch already exists, do not overwrite or delete it. Stop and report the
existing branch/worktree state.

PHASE 3 — TRANSFER PRODUCT CHANGES ONLY

Transfer only product-relevant modifications whose behavior can be justified by
source evidence and focused tests.

Expected candidates may include, but are not automatically limited to:

- src/core/sttm/SttmResolvedEvidence.ts
- src/core/sttm/SttmMarkdownBundleParser.ts
- src/tools/EtlReadOnlyToolService.ts
- src/test/suite/sttmRepair13.test.ts
- directly required synthetic Repair 13 fixture files
- other product files proven necessary by exact dependency and test evidence

Do not transfer:

- agent-governance framework files;
- governance reports or checkpoint machinery;
- temporary evidence;
- generated out/** content;
- existing VSIX files;
- unrelated documentation reports;
- unrelated pre-existing modifications.

For each transferred file report:

- source path;
- destination path;
- reason;
- runtime/test/package classification;
- source SHA-256;
- destination SHA-256.

Hashes must match immediately after transfer.

PHASE 4 — MINIMAL PRODUCT VERIFICATION

Create only the smallest deterministic verification mechanism required.

Preferred interface:

npm run product:verify

It should orchestrate existing canonical commands where possible instead of
duplicating their logic.

The verification must check:

1. Compile succeeds.
2. Lint succeeds.
3. Focused tests for transferred behavior succeed.
4. Required package resources are present.
5. Forbidden files are absent from the packaged file list.
6. Package identity and version are internally consistent.
7. No secrets, source tests, governance files, evidence packets, temporary files,
   existing VSIX files or repository metadata enter the VSIX.
8. The package is generated into OS temporary storage for inspection.
9. The source working tree is not polluted by verification output.

Use a small package contract containing:

- required paths/patterns;
- forbidden paths/patterns;
- allowed packaged roots.

Do not introduce baselines containing hashes of hundreds of ordinary source files.
Do not create checkpoint schemas, agent authority manifests or evidence packets.

PHASE 5 — VALIDATION STRATEGY

Run validations in this order:

1. Compile once.
2. Lint once.
3. Focused product tests.
4. Repair 11, 12 and 13 suites.
5. Runtime QA support fixture suite.
6. product:verify.
7. Canonical full-unit suite exactly once.

Known failures F1 and F3 may be accepted only if reconciled by exact test identity
and proven byte-identical to the source at HEAD.

Do not repeatedly run the full suite merely to change aggregate counts.

Required expected behavior:

- new functional regressions: 0;
- new security regressions: 0;
- F1 unchanged;
- F3 unchanged;
- package contract violations: 0.

PHASE 6 — VERSION 0.3.147

Only if all product recovery checks pass:

1. Change only the package version field from 0.3.146 to 0.3.147.
2. Do not alter dependencies or devDependencies.
3. Do not create package-lock.json.
4. Compile again only if the version is embedded in generated code.
5. Build one VSIX into OS temporary storage.
6. Inspect the VSIX as an archive.
7. Confirm:
   - expected Extension ID;
   - version 0.3.147;
   - required resources present;
   - forbidden entries absent;
   - consumer Agent resources match the canonical source;
   - no absolute paths, temporary files, secrets or governance evidence;
   - archive entry count and SHA-256 recorded.

Do not copy the VSIX into the repository yet.
Do not install it.

PHASE 7 — ORIGINAL TREE INTEGRITY

At completion, recompute the full snapshot of the original dirty working tree.

Prove:

- original path set unchanged;
- original contents unchanged;
- original HEAD unchanged;
- original staged/stash state unchanged;
- no file was added, removed or rewritten there.

FINAL REPORT

Return a concise product-oriented report containing:

ORIGINAL_WORKTREE_PRESERVED
RECOVERY_BRANCH
RECOVERY_WORKTREE_PATH
RECOVERY_BASE_HEAD
TRANSFERRED_PRODUCT_FILES
EXCLUDED_GOVERNANCE_FILES
EXCLUDED_UNRELATED_FILES
COMPILE_PASS
LINT_PASS
FOCUSED_TESTS_PASS
REPAIR_11_PASS
REPAIR_12_PASS
REPAIR_13_PASS
RUNTIME_QA_SUPPORT_FIXTURE_PASS
PRODUCT_VERIFY_PASS
FULL_UNIT_PASSING
FULL_UNIT_PENDING
FULL_UNIT_FAILING
F1_UNCHANGED
F3_UNCHANGED
NEW_FUNCTIONAL_REGRESSIONS
NEW_SECURITY_REGRESSIONS
PACKAGE_VERSION
TEMP_VSIX_PATH
TEMP_VSIX_SHA256
TEMP_VSIX_ENTRY_COUNT
REQUIRED_PACKAGE_ENTRIES_PRESENT
FORBIDDEN_PACKAGE_ENTRIES_PRESENT
READY_FOR_OWNER_PRODUCT_REVIEW
READY_TO_COMMIT
READY_TO_INSTALL
READY_FOR_RUNTIME_QA

Allowed terminal verdicts:

- PASS_READY_FOR_OWNER_PRODUCT_REVIEW
- BLOCKED_PRODUCT_CHANGE_ATTRIBUTION
- BLOCKED_PRODUCT_TEST_FAILURE
- BLOCKED_PACKAGE_CONTRACT_FAILURE
- BLOCKED_ORIGINAL_WORKTREE_INTEGRITY
- OWNER_DECISION_REQUIRED

Do not continue into governance review, commit, installation or Runtime QA.
