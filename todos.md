# Deliver the existing qualified private VSIX for Hesam’s demo

TASK\_ID: ETL\-0911\-PRIVATE\-DEMO\-VSIX\-HANDOFF01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not launched by ChatGPT
TYPE: Exact\-artifact demo handoff; may run in a new session alongside C review

## Goal and bounded authority

Give Hesam an installable copy of the ALREADY BUILT private 0\.3\.149 VSIX, its full SHA\-256, and short usable installation/demo instructions\. Do not build the current worktree: C migration and the F\-Q1 source fix are under a separate review and are not in this qualified \.149 binary\.

Owner submission authorizes read\-only authentication of the retained \.149 package and its qualification records, creation of a unique demo\-delivery directory, byte\-identical copying of that VSIX, and writing the short handoff files below\. This is private owner handoff, not publication or release acceptance\.

No source/test changes, build, repackaging, version bump, signing change, dependency setup, Git mutation, extension installation, Host launch, product command, consumer write, ETL job or publication is authorized by THIS delivery task\. Supply installation commands for Hesam to use later; do not execute them\. Do not rerun earlier qualification tests or write sequences to prepare the handoff\.

ALL replies, progress, questions and deliverables must be English\. No screenshots, video, image inspection, OCR or vision\. Use text, structured records, filesystem checks and hashes\. Do not create another JavaScript helper, harness, catalog extractor or review/reporting framework for a file\-copy handoff; existing tools and a short report are sufficient\. No subagent is needed\.

## Parallel execution boundary

The other session is continuing:
`ETL-0911-CONSUMER-CONTEXT-DESTINATION-MIGRATION01 / REVIEW-FINDINGS-CONTINUATION01`\.

It may edit source and run isolated tests\. This handoff reads only the completed \.149 qualification bundle and VSIX and writes only its own delivery directory\. It neither needs nor releases C’s source ownership\. Do not wait for C’s review, acquire a source/runtime lock, inspect changing source as the package baseline, or modify that session’s claim/report\. Do not use either retained installed environment or Hesam’s default profile\.

Check this exact handoff task’s disposition using its claim/result before setup\. If already delivered, reuse its authenticated result; if active, do not duplicate it\. Use the established task ownership mechanism or one atomic CreateNew claim:
`C:\docs\ETL-0911-PRIVATE-DEMO-VSIX-HANDOFF01.claim.json`

No whole\-C:\\docs scan, session\-storage query or broad historical reconstruction\.

## Resolve and authenticate the original package

Read this completed qualification claim and follow its exact result/artifact pointers:
`C:\docs\ETL-0911-WORKFLOW-UPGRADE-PLAN-BINDING-INSTALL-QUALIFY01.claim.json`

Read the current original result and only the report sections needed for package identity, qualification scope, constraints and final locators\. If a pointer differs, use one direct task\-prefix listing, not a broad content scan\. A Windows path supplied by ChatGPT is a locator, not proof that ChatGPT accessed it\.

Reported package context, to verify against originals:

- Extension ID: `td-etl.databricks-etl-copilot`\.
- Private package version: `0.3.149`\.
- VSIX size: 1,269,223 bytes; 66 entries; full SHA\-256 is in the retained records\. Never use size, entry count or a hash prefix as identity proof\.
- Qualification status: `INSTALLED_WORKFLOW_UPGRADE_PLAN_BINDING_VERIFIED_WITH_LIMITATIONS`, 77/77 checks passed\.
- Staging included the authenticated B source repair and earlier dirty/untracked content, with only the package version line changed from \.147 to \.149\. Its installed bundle matched the staged bundle\.
- Both approved qualification operations were consumed; the claim was closed with explicit runtime/source\-freeze release\.

Verify the actual VSIX’s full SHA\-256 against its retained package record and inspect its embedded manifest read\-only to confirm ID/version\. Use the existing archive/package reader; do not extract into or alter a protected installed environment\. Follow the retained source\-to\-package identity record, not today’s changed worktree\.

If the exact VSIX is missing, corrupt or mismatched, report the exact blocker\. Do not reconstruct it from an installed directory, rebuild a replacement, download another version, fall back to \.147/\.148 or silently substitute an unqualified candidate\. If a verified immutable copy is already named in the same qualification records, that identical copy may be used\.

## Deliver a small usable packet

Create one unique folder, for example:
`C:\docs\ETL-DEMO-0.3.149-<UTC>-<unique>`

Deliver exactly these essentials:

1. The original\-named `.vsix`, copied byte\-identically\. Verify the destination SHA\-256 equals both the source and retained record\.
2. `DEMO_README.md`, concise and in English\.
3. `demo-result.json`, with actual disposition, source and delivered absolute paths, extension ID/version, full SHA\-256, size, qualification\-record pointers, delivery timestamp and limitations\.

Do not copy source repositories, node\_modules, agent session histories, credentials, unsanitized logs or real consumer data into the demo folder\. Do not zip/repackage the VSIX\. Keep predecessor bundles untouched\.

The README must include:

- The exact ready\-to\-install VSIX path and expected SHA\-256\.
- Prerequisites grounded in the retained package/environment records\. Distinguish tested versions from manifest minimum requirements; do not invent account or connector requirements\. A consumer must not need either ETL source repository or an etl\-framework\-adb checkout just to install this extension\.
- Copyable PowerShell commands using the actual local VS Code executable and quoted absolute paths to check the hash, install once into a NEW dedicated demo environment with its own user\-data and extensions directories, and open a fresh demo workspace\. Keep those commands explicitly NOT EXECUTED by this task\. Installation is once per demo environment, not per workspace; subsequent consumer folders use that installed extension\. Do not point the commands at B/D’s retained profiles or change Hesam’s default profile\.
- How to confirm the installed extension ID/version and use normal reload if necessary\. Do not use F5/Extension Development Host as the installation method\.
- A short suggested demo centered on the qualified workflow root/profile/item disclosure and cancellation behavior\. State that this task has not launched or rehearsed that demo\. Prior B/D write budgets cannot be replayed; any future live demonstration writes require a fresh disposable target, a separately bounded write scope and the product’s normal approvals\. Do not instruct automatic approval or bypass any gate\.
- Honest scope: \.149 contains B’s workflow approval/disclosure repair; it does NOT contain C’s `.github/etl-context/` migration or the later F\-Q1 fix\. F\-Q1 is the minor final\-output overlap between Replaced and Skipped; it does not imply a second physical write\. Job/env diagnostic F\-1 is separate\. The model\-driven Chat/@etl\-write route and full ETL end\-to\-end readiness were not established by the \.149 workflow qualification\.
- The package is private and qualified only within the retained bounded evidence\. No RELEASE\_ACCEPTANCE or FULL\_PRODUCT\_OR\_ASKTD\_READINESS\. Preserve QA exception, R3/R4, historical CASE2, trust/toolchain/no\-lockfile/adjacent\-suite/source/preservation limitations by reference, without dumping engineering history into the demo steps\. Quarantine ends 2026\-09\-13 inclusive UTC; this handoff does not extend it or authorize reliance on that exception from September 14\.

## Finish

Return `EXACT_PRIVATE_0149_DEMO_VSIX_DELIVERED_WITH_LIMITATIONS` only after the exact package has been copied and its identity verified\. Otherwise report the precise blocked or already\-running disposition\. Close this task’s claim with result pointer and package hash\.

The final response must lead with the VSIX’s full absolute Windows path and demo folder, then give the exact version/hash and the README path\. State that no rebuild, install, Host launch or product write occurred and that the parallel C review was untouched\. Do not claim a demo rehearsal or qualification beyond the retained evidence\.
