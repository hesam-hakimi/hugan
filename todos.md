# Audit test coverage and repeated setup cost alongside the active repair

STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
TASK\_ID: ETL\-0914\-TEST\-COVERAGE\-AND\-REUSE\-AUDIT01\.
MODE: Independent research from preserved evidence and source snapshots\.
RELATED IMPLEMENTATION: ETL\-0914\-JOB\-JSON\-SQL\-INCLUDE\-QUALIFY01, whose current execution state must be checked, not assumed\.
PRODUCT\_WRITE\_AUTHORIZATION\_BUDGET: 0\.

Execute this research on submission in a separate engineering session\. Use English for all replies and artifacts\. Use text and filesystem evidence; no screenshots, video, OCR or vision\. The owner wants earlier defect detection and less repeated helper generation, testing and packaging\. Produce a concrete, small implementation recommendation from this project’s actual code and records\.

## 1\. Keep this work independent

Read applicable instructions and task records\. Use a separate research output directory under C:\\docs and any documented nonexclusive research registration\. Do not acquire or change another task’s source/runtime ownership\. Do not edit product code, tests, skills, managed consumer assets, canonical guidance, another task’s records or historical evidence\.

Use preserved, authenticated source lanes and closed task outputs as the primary inputs\. A moving worktree is not a stable baseline: if current code must be consulted, distinguish that observation from the pinned historical snapshot and record the relevant identity\. Prefer the archived version when concurrent edits make attribution uncertain\. Do not ask the active task to stop for this audit\.

Do not launch a host, use the active CDP/profile, make model requests, rerun helpers, run suites, compile, package, install, change dependencies, mutate Git or perform cleanup\. This is an inspection task; execution proposals are for the implementation owner to adopt later\. Ordinary read commands are sufficient\. Do not create a new audit harness or a series of numbered helper scripts\.

## 2\. Load only the relevant history

Resolve actual roots under C:\\docs by task ID, starting with:

- ETL\-0914\-JSON\-DISCOVERY\-AND\-INSTALLED\-DEFAULT01: installed \.156 selected a \.json job without an explicit extension, but reusable SQL validation blocked the first writer call before previewId\. Source/package discovery was repaired; final modal was not reached\.
- ETL\-0914\-INSTALLED\-0155\-APPROVED\-WRITE\-EXECUTE01: successful local job \.conf plus reusable \.sql write; actual captured arguments and read\-back evidence are useful regression inputs\. Its one final\-write allowance is spent\.
- ETL\-0914\-JOB\-CONFIG\-JSON\-ALIGNMENT01: default\-extension policy, consumed guidance, actual HOCON\-with\-\.json convention, and tests added for that change\.

Follow their references only as necessary to existing test suites, runners, fixtures, the collector, launch/package commands, env/include authority and approval\-expiry repairs\. The last reported worktree was C:\\repos\\etl\-extension\\etl\_fw2\\recovery\-extension\-product\-0\.3\.147; authenticate its relationship to archived lanes\. Do not scan every historical task, repeat the sample\-repository census or collect credentials\.

The \.156 report attributes its failure tentatively to over\-generalizing the job\-config suffix to a SQL include\. The active repair owns reproduction, root\-cause determination and correction\. This audit evaluates coverage around that observation; it must not issue a competing implementation or assume the tentative attribution is proven\.

## 3\. Map coverage to actual user outcomes

Inspect assertions and production call paths, not just suite names or pass counts\. For each row below, identify existing permanent test files/cases, the production stages actually exercised, important mocks, relevant fixtures and the remaining gap\. If evidence is missing, say “not established from inspected sources” rather than declaring the test absent\.

|Scenario                      |Outcome to examine                                                                                                                                                         |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Job default plus reusable SQL |A request omits filenames; the job uses .json; the separate SQL artifact and reference form are supported; required filter and mappings survive effective validation.      |
|Real artifact discovery       |The actual accepted HOCON body reaches ArtifactDiscovery and yields its supported metadata, including the documented extraction limits.                                    |
|Reused env and includes       |Workspace bytes govern reused inputs; declared writes and read dependencies remain distinct; normalized identities and transitive dependency changes affect binding.       |
|Preview and approval lifecycle|Manifest/content binding, late answers using a controlled clock, dependency drift, cancellation and consumed-record behavior are exercised at the real relevant boundaries.|
|Local write and subsequent use|Written bytes match approved content; reused files stay unchanged; generated artifacts can be read again at the coverage level actually tested.                            |

Separate two kinds of evidence explicitly:

1. Deterministic replay of recorded tool arguments through resolver, validator, manifest and writer boundaries\. It can catch downstream defects cheaply without a live model\.
2. Actual model behavior under the shipped context\. Replay begins after generation and cannot prove that a fresh Orchestrator request chooses the right filename or include form\.

Identify the smallest permanent replay cases obtainable from the \.155 success and \.156 failure\. State their provenance, expected behavior grounded in the contract, and the appropriate existing suite\. Preserve the distinction between an invalid proposal correctly rejected and a supported proposal incorrectly rejected; allow the active repair’s demonstrated contract conclusion to settle that expectation\.

Where historical failure coverage can be established, distinguish tests present before discovery from regressions added after the repair\. A current test is not proof that the old pipeline would have caught the defect\. Do not claim complete end\-to\-end coverage from mocked or partially replayed execution\.

## 4\. Identify reusable execution and actual time costs

Inspect existing runner and helper entry points\. Record their real paths, supported parameters, output destinations, side effects and dependencies\. Classify each as reusable unchanged, needing a small parameterization, or tied to a historical one\-off\. Check whether the normal repository runner can host the missing replay cases before proposing another runner\.

Use already\-recorded timestamps/logs from the selected closed tasks to separate preparation, helper authoring, tests, build/package, installation, model waiting, capture and review where evidence permits\. Distinguish a displayed chat\-turn duration from total task duration\. Do not add overlapping intervals or present estimates as measured values\. Mark missing phase timings unknown; propose minimal timing fields in the existing runner for later use\.

Give actual existing commands for the smallest affected test selection and the required package/install checks, with prerequisites and side effects\. Label commands as discovered but not executed by this audit\. If a command cannot be verified from code or configuration, describe the missing fact instead of inventing it\.

Recommend when an existing result can be reused based on relevant source, tests, assets, tooling and environment identities\. A stable version string or unchanged HEAD alone is insufficient in this dirty worktree\. Preserve applicable required gates\. Explain which changes require a new packaged candidate and which can be verified with focused tests without packaging\.

## 5\. Deliver one actionable handoff

Write one concise report\.md in this research task’s own directory\. Include:

- Inspected source/evidence identities and coverage table with exact source references\.
- Existing reusable entry points and any small parameterization needed\.
- Measured or unknown phase durations; no invented speed\-up percentages\.
- At most three prioritized changes, each with its target files, acceptance behavior and dependency on the active repair\.
- The smallest proposed sequence: targeted replay tests, relevant validation, required package gates, then a bounded installed\-model test for the behavior replay cannot establish\.
- A clear boundary between findings established here and tests/changes merely proposed\.

Return the absolute report path and a short summary for the owner\. Do not automatically send messages to other sessions, rewrite their prompts, implement the recommendation or start another qualification\. The implementation owner can adopt compatible findings at its next safe checkpoint; this report is not a new gate that blocks the current repair\.
