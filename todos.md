# Correct environment\-context binding in the /create workload plan

TASK\_ID: ETL\-0911\-CREATE\-ENV\-ROLE\-BINDING\-REPAIR01
PARENT\_TASK: ETL\-0911\-INSTALLED\-0151\-CHAT\-AND\-ETL\-WRITE\-PREVIEW01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not launched by ChatGPT
TYPE: Bounded source correction, permanent affected tests and focused review

Continue in the current Windows session\. English only for coordinator/subagent replies and deliverables\. No screenshots, video, image inspection, OCR or vision\.

## Confirmed observation and unresolved cause

The latest parent result traced the installed \.151 /create plan and write\-mode question:

- env\_conf\_erus9\_dev\.yaml became the workload table/source, with load\_enrich and target curated/env\_conf\_erus9\_dev\.yaml, status ready\.
- The requested IMSB\_MASTER\_AREA\_V3\_PASSED\_EXTRACT job did not appear as a workload\.
- The question generator used the populated adlsTarget\. The upstream extractor/classifier that populated table/adlsTarget was NOT established\.
- The operator cancelled the actual clarification using Escape after preserving the open input\. No mode was guessed\. The product reported no workspace writes; the one\-file fixture remained unchanged\.

Treat the incorrect environment\-as\-workload binding as observed\. Do not assume a specific regex, LLM, classifier or UI function caused it until traced\. The fixture may lack sufficient workload/STTM inputs; if so, the correct behavior is a precise missing\-input clarification, not inventing a workload from the environment configuration or the requested job name\.

Route A separately produced a safe preview on \.151: proposed job\_conf/conf/ERUS9/IMSB\_MASTER\_AREA\_V3\_PASSED\_EXTRACT\.conf as CREATE, with env reuse unchanged\. The \.conf versus expected \.json difference is recorded as permitted\-format variance, not an established defect\. Do not change extensions or rewrite the fixture’s expectations merely to force \.json\.

Neither route reached the final product write\-approval gate in this Chat task\. Cancellation of the requirement InputBox is NOT cancellation of a write approval\. Preserve the earlier installed\-helper/workflow evidence under its own scope; do not claim that no prior product gate was ever observed elsewhere\.

## Authority and ownership

Owner submission authorizes targeted cause tracing, the smallest in\-scope source correction, permanent affected regression tests in isolated temporary test workspaces and one focused independent review\. Complete that bounded work without another design\-only handoff if a product defect is established\. If primary evidence instead establishes solely a fixture/driver defect, correct only the task\-owned input/reporting problem and do not force a product change\.

No runtime Chat request, model request, product command, consumer write, job, build/package/install, version change, dependency installation, Git mutation or publication is authorized\. Typecheck and isolated test compilation/execution with existing tooling are authorized\. No live reproduction: use retained request/tool/plan records and offline tests\. Preserve the signed\-in env151 profile and candidate, all \.147/\.149/\.150 evidence, both worktrees, shared out/ and tracked build state\. Demo remains deferred\.

Read the parent’s final intervention result, exact original submitted /create text, current plan/transcript, frozen fixture and relevant \.151/source identity records\. Resolve paths through real locators\. Check actual ownership and any existing task disposition before edits\. Do not duplicate the task or infer not\-started from absent output\. Use one source owner and a bounded task directory outside protected worktrees/evidence\. Do not rescan C:\\docs or reconstruct session storage\.

Source worktree: C:\\repos\\etl\-extension\\etl\_fw2\\recovery\-extension\-product\-0\.3\.147
Protected linked primary: C:\\repos\\etl\-extension\\etl\_fw2\\etl\_framework\_extension\_hf1\_v2

## Trace and implement the narrow correction

1. Follow the actual /create entrypoint through request classification, workload extraction, consumer context assembly, target inference and requirement generation\. Pin the source preimages and prove relevant correspondence to the installed \.151 implementation\. Preserve newer source changes and other owners rather than rolling them back\.
2. Identify the earliest evidence\-supported point where a reference explicitly supplied as existing environment configuration becomes a workload/source/target\. Determine whether that value comes from request parsing, context scanning, model output, fallback inference or another actual component\. Quote only directly relevant non\-sensitive records/code in the report\.
3. Preserve the distinction between environment/configuration context and requested workload data\. A configuration reference supplied for reuse must not silently become a ready data workload or curated target\. It must not trigger a workload write\-mode question about the environment file\.
4. If the controlled request lacks the information required to generate the job, return a clear, non\-writing clarification naming the genuine missing workload input\. A job identifier alone need not establish a table, source, target or write mode\. Do not hallucinate these or substitute a default append/overwrite answer\.
5. Where model output participates, enforce the trusted input\-role/validation boundary as needed; a stronger prompt alone is not a sufficient guarantee\. Do not treat recorded model output as authority to reinterpret an explicit environment\-reuse instruction\.
6. Do not blanket\-ban YAML/JSON filenames, all file inputs, all names containing env or legitimate data workloads\. Use the actual role/context contract\. Keep valid workload extraction and explicit existing\-env reuse working through the same entrypoint\.
7. Make no unrelated architecture rewrite, second planner, new global schema/platform, writer strategy expansion or approval redesign\. Keep final write gates unchanged\. No changes to C\-LIVE\-1 migration, F\-Q1, OUTCOME\-DISCLOSURE\-001, diagnostic F\-1 or optional format policy\.

If the cause belongs to a different dependency or cannot be established from available primary input, state that exact limitation and the smallest next evidence needed\. Do not implement speculative broad fixes\.

## Permanent tests and proportional verification

Reuse the existing route/parser/planner suites and test setup\. Replay the retained synthetic request and minimal context offline; if model output must be replayed, label it as a controlled test input, never a fresh live model observation\.

Add a behavioral regression at the relevant existing entrypoint for the observed request: the reused env file must not appear as a workload/data target\. A missing\-input outcome is acceptable only if it identifies the real missing workload information and remains non\-writing\. Do not assert that the product must generate a complete job from an insufficient fixture\.

Cover the distinct affected risks with the smallest meaningful set:

- The exact observed environment\-only/reference request, reproducing the pre\-fix incorrect binding before the fix when possible\.
- A valid explicit workload plus the existing\-env reference: workload and environment remain correctly separated; the legitimate target remains usable\.
- Missing/ambiguous workload input fails closed or clarifies without inventing table/target/write mode\.
- Any actual fallback/model\-output boundary responsible for the defect cannot reintroduce the environment as data after the initial parser check\.

Use literal expected roles/paths from controlled inputs, not output from the extractor being tested\. Assert no writer dispatch on clarification/invalid\-plan paths\. Preserve relevant existing negative approval/containment checks; do not mirror the implementation or chase arbitrary test counts\.

Use the retained isolated compiler/Mocha/stub commands and existing dependencies\. Put compiled output and incremental state in this task’s directory, not protected out/ or \.tsbuildinfo\.test\. Confirm the tests execute the intended fresh compiled files\. Do not run npm run compile against the protected worktree or reset/revert source repeatedly to manufacture red results\.

Run affected regressions only\. Reuse other results only when relevant source, tests, inputs, dependencies, settings and outputs still match\. The three known adjacent failures remain identified by actual failure identity; do not waive new failures or opportunistically repair unrelated ones\.

## Focused independent review

You are the sole source/test editor\. At most one read\-only subagent may trace the role\-binding boundary while you work, then review the final diff and actual regression results in its own evidence directory\. It must not edit shared files, invoke Chat, launch a host or mutate consumers\.

Have it assess the confirmed cause, legitimate missing\-input behavior, preservation of valid workload extraction and no\-write boundary\. Fix concrete in\-scope findings and re\-check that delta\. Save the actual reviewer response with honest provenance at receipt so another round is not needed merely to record it\. Keep the author result distinct from its actual verdict; no self\-promotion of CHANGES\_REQUIRED\.

## Completion

Return a short report/result with confirmed cause or exact unresolved dependency, changed files/preimage identities, regression evidence, reviewer verdict and FINAL reusable test commands/parameter locations\. Keep helper/request\-state fixes separate from product changes\.

Use SOURCE\_CREATE\_ENV\_ROLE\_BINDING\_REPAIR\_VERIFIED\_WITH\_LIMITATIONS only if a product correction is substantiated by the affected tests; otherwise report the actual narrower outcome\. Do not claim an installed repair or a successful final Chat write gate from source tests\.

Prepare the smallest follow\-up to resume the unfinished Route B preview case using the existing signed\-in profile/transport and frozen fixture data, after qualification of a distinguishable candidate if product bytes changed\. Do not execute packaging or that live follow\-up here\. Do not rerun successful Route A unless the eventual source delta demonstrably affects its dependencies; explain any invalidated evidence rather than assuming either universal reuse or universal rerun\. Do not seed private participant state or bypass /create by injecting a fake candidate\.

Close with result pins and explicit source\-ownership release\. Preserve all previous observations: Route A preview, Route B’s deterministic missing\-artifact response, cancellation of the mis\-bound requirement and zero consumer writes\. Retain spent historical budgets, B1/C1/Base/Upgrade boundaries, QA exception, R3/R4 uncertainty, document 10 requests, OUTCOME\-DISCLOSURE\-001, diagnostic F\-1, historical CASE2 dispute, Windows case\-folding gap and toolchain/no\-lockfile/adjacent\-suite/source/preservation limits\. Quarantine ends 2026\-09\-13 inclusive UTC with no automatic extension from September 14\. No RELEASE\_ACCEPTANCE or FULL\_PRODUCT\_OR\_ASKTD\_READINESS\. Demo remains deferred\.
