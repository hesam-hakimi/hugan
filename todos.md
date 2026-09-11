# Session B — Upgrade disclosure and workflow overwrite design

TASK\_ID: ETL\-0911\-UPGRADE\-DISCLOSURE\-OVERWRITE\-DESIGN01
TYPE: BOUNDARY DESIGN ONLY — read\-only inspection, no implementation or runtime
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not launched by ChatGPT

## Goal and environment

Prepare the smallest implementation\-ready design for the remaining Upgrade disclosure and Overwrite Existing Assets workflow UI gaps\. This task may run concurrently with Session A’s consolidated write review and Session C’s asset/layout design\. Do not wait for their results to inspect this separate boundary\.

Windows development environment:

- Source worktree, read only: `C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`\.
- Linked primary, protected: `C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2`\.
- Installed evidence environment, read only: `C:\docs\ETL-TESTENV-INSTALLED-WORKFLOW-SMOKE01`\.
- Reported installed product: `td-etl.databricks-etl-copilot 0.3.147`, private candidate\. Authenticate relevant identities from original records; these paths and the version are locators, not proof of access or matching bytes\.

Use English for ALL agent/subagent progress, questions, final answers and artifacts\. No screenshots, video, image inspection, OCR or vision\. Use source text, existing DOM/accessibility traces, structured outcomes, logs and filesystem measurements\.

## Authority, isolation and efficient reading

Owner submission authorizes this inspection/design and only new task\-owned documentation outside both worktrees\. No source/resource/test edits, generated code, fixture changes, tests, product tool calls, Host launches, build, install, package, dependency changes, Git mutation, consumer writes, jobs or publication\. Read\-only Git observations may use disabled optional locks\. Do not mutate the running editor’s settings or profile\.

Check THIS task’s disposition before starting: running means do not duplicate; completed means inspect its existing result; a missing report alone does not mean not started\. Sessions A and C are permitted concurrent readers, not blockers\. Do not stop or control their processes\.

For a new task, create one exclusive output directory:
`C:\docs\ETL-0911-UPGRADE-DISCLOSURE-OVERWRITE-DESIGN01-<UTC>-<unique>`\.
Write only your own `design.md`, `result.json` and indispensable supporting notes there\. Do not modify shared reference/state files, existing reports or other sessions’ outputs\. If returning to an interrupted task, preserve earlier outputs and record the continuation\.

Use `rg` to locate the relevant command handlers, dialog construction, asset plan/catalog, approval and write consumers, plus existing test entrypoints\. Read complete relevant functions/contracts and follow only real dependencies\. Record identities of inspected files once and verify them before finalizing; if they drift, mark the affected analysis stale and identify the changed dependency\. Do not rebuild, reset or scan all history to fix drift\.

Reference v2 contract 09 v1\.1 and safety document 05 govern proportionality\. Use available matching copies; never invent a Windows mirror or make delivery of the entire pack a prerequisite\. The task\-specific operative requirements are included below\. Resolve only a missing original requirement that materially affects your design\.

## Evidence and known boundary

Resolve original `C:\docs` task roots by task ID, report contents and metadata, not newest\-name selection:

- `ETL-0910-INSTALLED-WORKFLOW-EXISTING-CONSUMER-UPGRADE-SMOKE01`\.
- `ETL-0910-EXISTING-CONSUMER-UPGRADE-INDEPENDENT-REVIEW01`\.
- Relevant disclosure findings from `ETL-0910-WORKFLOW-GITIGNORE-DISCLOSURE-REVIEW01`, only as needed\.

Reported accepted scope: one AG consumer’s scaffolded validate\-write skill upgraded from 1\.1\.4 to 1\.1\.5; other managed assets and managed `.gitignore` were preserved\. This bounded acceptance does not close the decision UI gaps\.

Reported open concerns: Upgrade presents counts at the decision point, while root, paths, versions and managed `.gitignore` details are elsewhere in the output channel\. Overwrite Existing Assets lacks sufficient itemization and has not been qualified end to end\. Treat exact claims as reported until authenticated\. Existing nonempty user content outside managed sections was not exercised by the accepted Upgrade\.

The completed job/env multi\-root/overwrite smoke is a DIFFERENT operation; Session A reviews it\. Do not rerun it or use its result to accept workflow\-asset overwrite\. Its diagnostic logging F\-1 is also outside this implementation design\.

## Produce the design

1. Trace actual Upgrade and Overwrite Existing Assets entrypoints through planning, decision UI, approval and writing\. Identify shared consumers with Initialize/Repair, preserving their distinct acceptance boundaries\. Where source identity cannot be tied to installed evidence, separate source\-design findings from installed observations\.
2. Define the decision\-time information users need: actual selected consumer root, action/profile, exact destination paths, per\-item disposition, applicable current/target asset versions, managed `.gitignore` effects, and treatment of customized/unmanaged files\. Include only relevant product information\. Design explicit Cancel and accurately scoped confirmation\.
3. Reuse one authoritative operation plan so displayed items and approved writes agree on root, paths, content and scope\. Determine how existing controls bind that plan and handle drift\. Do not invent a second catalog, planning engine or approval mechanism when the existing seam suffices\.
4. Keep routine Upgrade distinct from explicit workflow overwrite\. Define preservation of user content and managed sections; collisions or missing ownership must not silently expand overwrite authority\. Identify the smallest affected files/functions and propose exact behavior changes, not patches\.
5. Propose meaningful permanent regressions using EXISTING test entrypoints: correct root/path/version/disposition disclosure; pending/Cancel with no writes; stale/current and customized assets; managed `.gitignore` plus nonempty user sections; approved plan versus actual writes; applicable stale\-plan rejection; and affected Initialize/Repair behavior\. Specify independent expected fixtures and which checks may be reused when identities match\. Do not execute tests or create a new harness\.
6. Identify shared files/interfaces with Session C, especially catalog destinations and their presentation\. Design against CURRENT destinations; do not implement or assume C’s future migration\. Propose one later integration owner and order for shared changes\.

## Delegation and handoff

This session is already one parallel work lane\. Default to no additional subagents\. If useful capacity exists, delegate at most ONE bounded read\-only subtask &#40;for example existing regression coverage&#41;, while the parent completes the UI/control\-flow design\. Do not delegate Session A’s review or Session C’s inventory work\. All agents obey this prompt; only the parent writes the consolidated outputs\. No independent acceptance claim from an author check\.

Finish with `DESIGN_READY_FOR_IMPLEMENTATION_SCOPING`, `BLOCKED_DEPENDENCY` or `OWNER_DECISION_REQUIRED`, stating the precise dependency/decision when applicable\. Make routine design choices yourself and explain them\. Include observed versus proposed behavior, exact source/evidence identities, editable surfaces for a FUTURE task, test matrix, shared\-file dependencies, remaining risks and the smallest next implementation brief\. Do not execute that brief\.

Do not wait indefinitely for A or C\. Mark their unpublished results pending and return this independently useful design\. A only needs your task ID, result location and dependency summary; do not edit A’s report\. Keep release/toolchain/adjacent\-suite and source\-acceptance limits visible without re\-auditing them\. Preserve B1/C1 acceptance and the existing QA exception\. Do not rely on an unrenewed quarantine from 2026\-09\-14; its recorded expiry is 2026\-09\-13 inclusive UTC\. No release or full\-readiness acceptance is granted by this design\.
