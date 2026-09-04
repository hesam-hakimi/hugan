# ETL\-0904\-DIAG01 — Protected\-Set Decision Packet

You are the normal local VS Code engineering Agent on Windows\. You are **not** the ETL Orchestrator\.

## Authorization boundary

This task authorizes **read\-only inspection only**\. Do not edit, generate, delete, restore, format, compile, emit, test, launch a runner or Extension Host, package, install, commit, merge, bump a version, release, or write to QA/evidence/profile/consumer\-workspace locations\. Do not run cleanup commands\. Do not use Bypass Permissions to expand this scope\.

## Goal

Prepare an evidence\-backed owner decision packet defining the exact protected\-file set for the next focused real\-Host qualification of release `0.3.148`\. Do not choose policy on the owner’s behalf and do not implement any Phase W repair\.

## Reported baseline to verify read\-only

- Active worktree: `C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`
- Linked primary worktree: `C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2`
- Branch: `fix/workspace-write-completion-0.3.148`
- HEAD: `45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19`
- Manifest version: `0.3.147`
- Extension identifier: `td-etl.databricks-etl-copilot`
- Expected dirty paths:
  - ` M .github/templates/request.md`
  - ` M src/extension.ts`
  - ` M src/test/runTest.ts`
  - ` M src/test/suite/index.ts`
  - `?? src/test/suite/sttmRealHostStructuredResult.test.ts`

Treat these values only as a comparison baseline\. Re\-derive them from the live worktree\. If worktree, branch, HEAD, manifest version, extension identifier, or dirty\-path inventory differs, stop without further investigation and report:

`ETL_0904_DIAG01_RESULT: BLOCKED_BASELINE_DRIFT`

Do not modify or normalize the five dirty paths\. The branch name does not prove that `0.3.148` exists, and `0.3.147` remains immutable\.

## Read\-only investigation

1. Trace the protected\-manifest declaration, population, reading, and comparison logic in `src/test/runTest.ts`, including every downstream consumer\.
2. Inspect the existing control\-plane cleanliness policy &#40;including `assert-control-plane-clean.mjs`, if present&#41; and explain why its protected entries are not automatically the qualification protected set\.
3. Classify relevant paths into:
  - product source and public adapter;
  - test harness and focused suite;
  - compiled outputs/build metadata;
  - package/configuration inputs;
  - QA workbook and inventory inputs;
  - evidence/control\-plane artifacts\.
4. Produce:
  - one **minimal recommended repo\-defined protected set**; and
  - one **extended alternative set**, only if materially justified\.
5. For every included and excluded path, give a concrete invariant and rationale\. Use repository\-relative paths, deterministic sorting, and a count derived from the selected list\. Do not reuse `8`, `39`, historical hashes, or operator\-supplied counts as truth\.
6. Recommend a contract in which the canonical path policy, operator\-generated manifest, pre\-run digests, post\-run digests, manifest self\-digest, and external post\-exit verification cannot silently disagree\.
7. Explain how the owner’s choice affects the five unresolved Phase W objections:
  - total parser\-wrapper installation/restoration;
  - exclusive focused\-suite loading;
  - evidence persistence on early failure;
  - machine\-readable infrastructure/product/evidence\-write classification plus parent post\-exit verification;
  - removal of hard\-coded protected\-set cardinality\.

Use read\-only commands only\. Quote exact paths, symbols, and re\-derived line numbers\. Distinguish observed facts, recommendations, and unknowns\.

## Required output

Return, in this order:

1. verified live identity and exact status;
2. code\-flow trace for the current manifest/protection mechanism;
3. minimal protected set in a sorted table with category and invariant;
4. optional extended set and its incremental cost/benefit;
5. explicitly excluded paths and reasons;
6. conflicts or unknowns;
7. two owner\-decision options, with one recommendation;
8. this exact proposed decision sentence, completed without ambiguity:
  `OWNER_DECISION_PROPOSED: For ETL 0.3.148 focused qualification, the authoritative protected set SHALL be <repo-defined/operator-supplied> and SHALL contain exactly: <sorted repo-relative paths>.`

End with exactly:

`ETL_0904_DIAG01_RESULT: DECISION_PACKET_READY`

`FILES_CHANGED: 0`

`COMPILE_OR_TEST_EXECUTED: NO`

`RUNNER_OR_HOST_EXECUTED: NO`

`OWNER_DECISION_REQUIRED: YES`

Stop after the decision packet\. Do not propose or begin implementation, compile, qualification, packaging, installation, merge, version bump, or release\.
