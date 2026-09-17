# Assess ETL Copilot against a real repository and its job patterns

TASK\_ID: ETL\-0916\-REAL\-REPOSITORY\-UNDERSTANDING\-ASSESS01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
MODE: Independent assessment, parallel to the root\-resolution hotfix\. No shared product repair or baseline changes\.
GOAL: Establish what the current extension can actually discover, interpret, diagnose, modify and generate for representative patterns in an existing ETL repository\.

Use English for all development\-agent responses, prompts, code, tests and deliverables\. Use text, filesystem and DOM/accessibility only; no screenshots, video, OCR or vision\.

## 1\. Required input and bounded authority

The owner supplies the absolute Windows path of the real repository alongside this brief\. Treat that as REPO\_UNDER\_TEST\. It is a consumer ETL repository, not the extension’s development checkout\. If its path is missing, ask for that one input; do not infer a clone path from photographs or scan unrelated drives\. The repository may stay on the owner’s machine\.

Use the Framework version/source or documentation referenced by that repository where available\. Record missing Framework dependencies explicitly and continue checks that do not need them\. Do not reconstruct a complete config from screenshots\. The photographed job is illustrative until its actual file and dependencies are available\.

Submission authorizes repository inspection, an isolated assessment copy, task\-owned fixtures/evidence, the bounded product tests below, and independent review\. Leave the original repository and extension source unchanged\. Proposed fixes/new jobs may be captured as unapplied outputs in the assessment area; do not apply them to the original repository\.

Use the existing approved product/model connection for any model\-backed probes\. Do not configure a new provider, change credentials or send repository content through a separate ad hoc model service\. This brief authorizes at most six top\-level product requests as specified below, with their normal internal orchestration recorded separately\. It authorizes a separate test Host/profile using the existing accepted extension artifact where necessary, with at most two launches for this first assessment\. Routine local setup inside this boundary does not need another approval\.

No Databricks, Spark, Synapse, database or data\-pipeline execution; no publication, teammate messaging or product approval/write click\. SQL containing MERGE, DELETE or INSERT is inspected, not executed\. Local assessment fixture/output writes are permitted\. Historical \.154/\.155/\.160 write allowances remain SPENT\.

## 2\. Pin the product and isolate parallel work

Read applicable local instructions and:
`C:\docs\ETL_Team_Test_Prep\references\09_AGILE_REPAIR_AND_VERIFICATION_CONTRACT.md`

Expected contract v1\.2: 23,684 bytes; SHA\-256:
`5387aa5c42940eceb2ffcd4d68d732ad3d57f1c69c2288c66bd0f32455e6f75b`\.

Use the exact accepted 0\.3\.160 internal\-test artifact as the primary product under test\. Resolve its actual VSIX/package identities from the completed internal\-kit and delivery records under `C:\docs`; a displayed version alone is insufficient\. Reuse those bytes in the isolated Host/profile rather than rebuilding from the live hotfix checkout\. Record product digest, settings and actual model identity where exposed\. If that artifact cannot be exercised, report the exact missing capability; do not silently substitute a different build and call it the same result\.

Keep three roles distinct: the real repository as input, the pinned extension as the subject, and the assessment agent/reviewer as evaluators\. The evaluator’s ability to explain files is not evidence that the extension can do so\.

Create one task\-owned root under `C:\docs` and an assessment copy/snapshot preserving paths, file contents and required includes/environment/schema dependencies\. Capture repository commit if present plus actual relevant file identities, including uncommitted input\. Do not use HEAD alone as the snapshot identity or omit dependencies in a way that creates artificial missing\-file failures\. Record unavailable dependencies instead of fabricating them\.

Use separate writable fixtures, logs, temporary consumer, profile and extension directory\. Do not change the live hotfix workspace, its claims, `docs/eval/phase_h_latest_report.*`, corpus fixtures, shared `out` or `.tsbuildinfo.test`\. Do not open the assessment snapshot as an extra root inside the hotfix’s active product Host\.

Prefer existing packaged entrypoints and helpers\. If a focused check truly needs compilation, inspect the effective configuration first and direct every compiler output/buildinfo destination into this task’s lane\. Apply the same restriction explicitly to the reviewer\. The earlier reviewer accidentally overwrote shared output; old preservation counts must not be reused as current facts\. Do not use normal shared\-output compile/eval scripts or install new dependencies for an assessment framework\.

An unrelated active hotfix is not a blocker once these inputs and writable surfaces are isolated\. This task neither waits for its repair result nor claims to assess that future repaired version\.

## 3\. Inventory patterns before selecting examples

First inventory the supplied repository locally without sending every file to a model\. Discover actual formats and relationships rather than classifying solely by file extension\. In particular, a `.json` suffix can contain HOCON\-style configuration with unquoted keys, substitutions and multiline SQL\.

Build a small pattern inventory from real files\. Include these dimensions where present:

- JSON/HOCON/other actual formats, comments, multiline strings, substitutions, concatenation, includes, overrides and environment precedence\.
- Sourcing definitions and `sourceList`; effective relation/view names, including any `table.name` override or key fallback that the actual Framework implements\.
- Views/results produced by job modules and consumed later, inline SQL and included SQL, versus external physical tables and Delta paths\. A view need not be declared in an included `CREATE VIEW` statement\.
- Module execution order, parameter dependencies, intermediate transformations and name reuse\. Do not assume object text order is execution order without checking the Framework contract\.
- Reads, filters, joins/CTEs where present, MERGE/DELETE/INSERT, writers and pre/post actions\. Explain their effects and dependencies without executing them\.
- Repository\-specific environment keys such as `adls.srz.psa.root`, alongside any other legitimate names\. Do not impose generic `adls.source.root` aliases on every job\.

The supplied example includes a report\-date module, a `cpat_w` sourcing definition, a downstream transformation reading `cpat_w`, and later merge/insert operations\. Use actual file bytes and the Framework contract to establish its full behavior; do not infer unseen dependencies from the photographs\.

Select up to twelve representative existing jobs for the first assessment, covering distinct discovered families, common patterns and unusual/high\-impact patterns\. If more families exist, report the uncovered ones rather than expanding without bounds or claiming full coverage\. Preserve the complete relevant dependency closure for selected cases\. Selection must not be limited to files the current tool already parses successfully\.

## 4\. Establish independent expected results

Before probing the extension, record an expected interpretation for each selected case: inputs, actual format, modules/order, produced and consumed relations, environment/include dependencies, target writes and unresolved external requirements\. Cite exact repository/Framework locations\. Separate facts, justified inference and unknowns\.

Use the actual Framework contracts/implementation and supported parser behavior as the reference\. Existing working jobs and owner explanations are useful corroboration; neither a familiar\-looking file nor the extension’s validator establishes correctness by itself\. A validator being assessed must not also be the sole oracle used to approve its own answer\.

Record a compact semantic checklist before reading the product’s output\. Where a necessary expectation cannot be established, mark that part UNVERIFIED and name the missing fact\. Continue independently evaluable cases rather than requesting a general acceptance decision for the whole repository\.

Keep the expected answers, injected\-fault manifest and scoring notes outside the repository visible to the product\. Hold back the jobs used for the final modification/generation probes from evaluator\-authored explanations\. The product may inspect the repository normally, but it must not receive the evaluator’s answer key or a prompt tailored after seeing its first failure\.

## 5\. Exercise the actual extension at distinct levels

Resolve real tool names and callable public routes from the pinned extension’s registration\. Use their actual outputs; do not invent API names or replace unavailable product behavior with manual evaluator work\.

### A\. Deterministic discovery, parsing and validation

Run the relevant product discovery/analysis/validation tools over the selected jobs and dependencies\. Record which files were actually opened and which were skipped, truncated, unsupported or unresolved\. A command exiting zero is not enough if it returned an empty structure, ignored inline SQL or omitted a module\.

Compare actual extracted structure and diagnostics against the expected interpretation\. Distinguish syntactic parse success from semantic coverage, relation resolution and correct validation\. Check both false positives on established\-valid patterns and missed problems in the adverse variants below\.

If a component is callable only through an isolated source\-level check, label that evidence component\-only and authenticate the source relationship\. Do not present it as successful execution through the installed product\.

### B\. Six bounded product requests

Use fresh conversation state per case, with the normal repository context available to the extension\. Freeze the requests before execution and retain the first complete response, relevant tool calls and proposed artifacts\. The first assessment contains:

1. Two explanations of different real job patterns: ask for sources, intermediate views, environment/include dependencies, module order, destinations and write effects, with file references\.
2. Two debugging cases: in separate private copies of established\-valid inputs, introduce one small contract\-grounded fault per case, such as a broken required reference or producer/consumer name mismatch\. The product must locate and explain the defect and propose a bounded fix while preserving valid surrounding structure\.
3. One bounded change to another existing job: select a meaningful local change supported by its pattern, and ask for a proposed diff/preview\. Check all affected references and preservation of unrelated behavior; a prose promise is not a completed artifact\.
4. One new\-job request following a different discovered pattern: provide a concrete requirement and access to repository examples, then inspect the proposed artifacts/preview for semantic consistency, legitimate configuration keys, correct dependencies and adherence to the repository’s conventions\.

Choose the cases from the inventory, not convenience\. Do not introduce an intentionally ambiguous fault or score a pre\-existing unresolved job as known valid\. Keep the debugging mutations out of the original repository and canonical Phase H corpus\.

Do not correct the product’s response manually, feed it the hidden answer, weaken the request or retry until it succeeds\. An infrastructure failure may justify one of the remaining requests after its cause is recorded; do not exceed six top\-level requests or confuse repeated responses with independent cases\. Record actual internal model/tool calls, timing and available usage rather than assuming one request equals one inference\.

Capture proposed diffs/artifacts exactly in task\-owned output\. Preview is sufficient for this assessment; no Approve write operation is required\. Validation passing is necessary evidence where applicable, but assess semantic correctness and conformity independently\. No live pipeline is run, so runtime correctness remains unqualified\.

If a product route, model connection or necessary context is unavailable, mark that layer NOT\_EXECUTED with the precise reason and complete the deterministic work\. Static parsing must not be reported as proof of diagnosis, modification or generation ability\.

## 6\. Report capability by pattern, with concrete failures

For each case, record pattern, input identity, product route/version, expected facts, observed facts, diagnostic/artifact differences, evidence level and disposition\. Use explicit outcomes such as observed support, partial interpretation, false positive, missed defect, incorrect proposed change, explicit unsupported behavior and unverified/not executed\.

Summarize actual denominators: inventory size, selected jobs, represented families, parsing/semantic cases completed, known\-valid cases falsely rejected, injected defects caught, and modification/generation outputs satisfying their defined checks\. Do not produce one overall “repository understanding percentage” that hides skipped families, different evidence levels or a small sample\.

Locate failures where evidence permits: discovery/context selection, parsing, configuration resolution, view/module semantics, validation, orchestration/retrieval, or generation\. Keep uncertainty explicit when the public output cannot isolate the layer\. Unknown/unsupported reported honestly is different from a confident wrong answer\.

Prioritize a small repair backlog by concrete user impact and pattern frequency: existing\-job misdiagnosis, unsafe/wrong proposed edits, lost configuration semantics and invalid generated artifacts\. Retain minimal reproducible examples and meaningful future acceptance checks\. Do not start those repairs or build a new parser, template library or helper framework during this assessment\.

Obtain focused independent BOUNDARY review of the reference interpretations, scoring, reported capability limits and highest\-priority findings\. The reviewer may reuse raw results and existing tools, but must evaluate expectations independently\. Reviewer checks use private outputs; frozen records stay unchanged\. Review is not another full six\-request model campaign\.

Deliver one `report.md` and `result.json` containing the pattern/capability matrix, supported conclusions, precise gaps and prioritized next action, plus necessary original tool outputs, requests/responses and proposed diffs\. Keep the final review verdict separate from the reviewed files\. State what additional patterns or Framework evidence are needed for a broader assessment\.

Finish with a practical recommendation: which sampled job families can currently be inspected or drafted with useful assistance, where a maintainer must verify specific semantics, and where the product demonstrably lacks support\. Do not claim universal repository understanding, installed hotfix qualification or release readiness\.

Preserve the original repository, pinned product and hotfix work\. Persist the assessment, release to only this task’s ownership and stop without applying repairs, refreshing canonical baselines or starting a follow\-on task\.
