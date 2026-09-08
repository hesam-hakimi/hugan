ETL-0908-FOCUSED-HOST-INDEPENDENT-REVIEW01

Assignment and authorization

Act as an independent reviewer in the LOCAL Windows VS Code Agent, on the existing ETL worktree. Review the completed ETL-0908-FOCUSED-HOST-RUN01 and recommend the next bounded task. Do not execute this through the ETL Orchestrator. If you authored or executed RUN01, disclose that limitation; do not represent your review as independent.

This task authorizes read-only inspection of the identified repository, pinned distribution, fixture and evidence roots, plus creation of a new external review directory containing review artifacts and byte-exact copies of necessary evidence. Complete the review autonomously within this scope. It does not authorize another test run, a repair, a rebuild, installation, download, packaging, release or Git mutation.

The preceding run brief is reproduced verbatim in Appendix A. It is historical evidence of that run’s authorized scope. Its execution permissions DO NOT carry into this review. Evaluate any additional contemporaneous authorization found in the actual task conversation; cite the exact instruction and distinguish it from retrospective explanations.

Objective

Determine whether this is trustworthy evidence of a completed but failing focused run, establish the strength of canonical manifest acceptance evidence, and separate:

1. B1: the observed target identity discrepancy.
2. C1: the parser invocation observation discrepancy.
3. The mechanical and causal justification for canonical verdict BLOCKED.
4. Any material evidence, provenance or execution-scope limitations.

Do not turn this into full B3 acceptance or a release certification. A valid failing run can be useful evidence without passing its gate.

Locators — authenticate rather than assume

ACTIVE_WORKTREE:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

EXPECTED_BRANCH: fix/workspace-write-completion-0.3.148
EXPECTED_HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

RUN_TASK_ROOT:
C:\docs\ETL-0908-FOCUSED-HOST-RUN01-20260908T023707634Z-717e5562-a8f9-479d-85c1-95dcffdb92b7

RUN_ROOT:
C:\Users\tag5916\AppData\Local\Temp\etl-phase1b3n-v-evidence-87d05133ce608363fdd52c1d5945b728

ORIGINAL_QA_ROOT:
C:\Users\tag5916\AppData\Local\Temp\etl-w1-qa-20260901-054832-c5e982

RUN_QA_COPY: RUN_TASK_ROOT\qa-workspace

PREP_ROOT:
C:\docs\ETL-0907-PINNED-HOST-MANIFEST-PREP01-20260908T020044626Z-57663a80-64c5-4b80-8e4a-02509b2fe2c2

BUILD_ROOT:
C:\docs\ETL-0907-BUILD-PROVENANCE-PIN01-20260907T212019853Z-541114a2-1843-45ff-a24f-b575eb4694d6

Pinned executable locator: PREP_ROOT\host-1.135.0-win32-x64-tar\Code.exe.
Read exact paths, version, commit and expected hashes from authenticated original records. Do not use screenshot-transcribed hashes as authoritative pins. Account for the distribution’s commit-prefixed application directory; do not assume a conventional resources path.

The reported repository inventory is eight dirty paths and empty staging:
M .github/templates/request.md
M src/core/sttm/SttmUnderstandingReportRenderer.ts
M src/extension.ts
M src/test/runTest.ts
M src/test/suite/index.ts
?? src/test/b3OutcomePolicy.ts
?? src/test/b3OutcomePolicy.unit.test.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts

Read actual current identity. Differences from the recorded run state are evidence to assess, never permission to restore, clean or overwrite anything. If a critical root is missing, document the gap and complete other useful review work; do not search the entire machine or silently substitute another run.

Operating boundaries

• Create exactly one fresh, exclusively created review root under C:\docs, named from this TASK_ID, UTC timestamp and random identifier. Verify it is outside the repository, original run roots, preparation/build roots and original QA root. Check containment and reparse points before writes; fail on an existing destination. Do not create or change an isolation root for another run.
• All review writes, temporary helper outputs and copied evidence belong inside the review root. Preserve original bytes, names and timestamps as evidence where available; never normalize or repair original JSON/logs.
• No source/configuration/output edits, npm/npx/package scripts, compiler invocation, test discovery, Mocha, runner, launcher, Code.exe, Extension Host, producer, product parser or product workflow execution. Do not import runTest.ts, runTest.js, the suite entrypoint or project modules to obtain helper functions; their initialization may execute code.
• No Git changes, staging, reset, restore, checkout, commit, merge, editor Keep/Undo operations, dependency installation or network operations. Read-only Git commands use –no-optional-locks.
• Read only task-relevant files in named roots and exact upstream evidence files referenced by their manifests. No broad user-profile, credential, unrelated workspace or whole-machine search. Inspect saved Host logs only for this run. Do not expose secrets in the review report.
• Existing system tooling or already available general-purpose libraries may read JSON, raw bytes, ZIP entries and source syntax. Do not execute repository application code to validate evidence. If unavailable, report the specific unverified check; do not install tooling.
• Do not kill processes. If evidence is still being written, report instability and avoid claiming a stable snapshot. Do not launch a replacement attempt.

1. Preserve and inventory the evidence

Record reviewer independence, actual worktree/HEAD/branch/staging/status, relevant process observations, and evidence root identities. Read the complete original report and the governing Appendix A before evaluating claims.

Inventory the actual artifacts; expected names include:

RUN_TASK_ROOT: report.md, creation-receipt.json, run-root-creation-receipt.json, baseline.json, post-state.json, fixture-resolution.json, fixture-candidate-inventory.*.json, qa-workspace-materialization.json, execution-plan.json, manifest-strategy.json, canonical-prelaunch-gate.json, run-status.json, run-stdout.txt, run-stderr.txt, supervisor.log, result-assessment.json, task-artifact-hashes.json and the helpers that actually produced them.

RUN_ROOT: protected-hash-manifest.json, mocha-result.json, mocha-result.evidence.json, runner-result.evidence.json and this run’s retained Host logs.

Preserve byte-exact copies of the four raw RUN_ROOT JSON files and necessary original task records/stdout/stderr/supervisor/Host logs under review-root\preserved-evidence. Record original absolute path, original relative path, size, SHA-256, copy hash, and original hash before and after copying. Keep a machine-readable copy inventory. Do not copy unrelated profile storage, credentials, entire installations or archives merely for convenience. Hash the retained archive in place.

State whether each claim rests on direct runtime observation, authenticated control-flow inference, post-hoc data validation, an executor assertion, or an untested hypothesis. A screenshot and a report repeating another report are not independent runtime evidence. New review-time checks strengthen current corroboration but cannot manufacture missing time-of-run measurements.

2. Reconstruct the one run

From raw records, establish the run timeline, supervisor/runner/Host process relationship, invocation count, deadline handling, actual executable selection and arguments, parent environment and runner-generated child environment. Correlate identity across every result artifact.

Reported facts to verify, not assume:

• One focused invocation using VS Code 1.135.0 x64, authoritative extension worktree, no download branch.
• 8 tests, 6 passes, 2 failures, 0 pending; 8 expected/authored tests; exactly the focused suite loaded.
• A normal Host/launcher exit of 0 with a parent runner exit of 1.
• Actual canonical verdict BLOCKED; primary infrastructure / runner-comparisons.
• Correct protocol version, run nonce, completion marker, suite identity and fixture identity; no stale/foreign result accepted.
• Bounded execution completed without timeout or forced termination and no surviving owned process.

Verify counts from raw results and test identities, not summary arithmetic alone. Establish which process exit each value describes. Normal producer completion over counted failures is not equivalent to product PASS. Distinguish the descriptive executor result FOCUSED_RUN_COMPLETED_WITH_PRODUCT_FAILURES from the canonical verdict; assess whether the report clearly preserves both meanings.

3. Canonical manifest acceptance

Inspect authenticated source and emitted code for the actual runtime path, including the unconditional entrypoint. Do not load the entrypoint.

Verify fresh run-root creation, manifest path resolution, actual freshness-check call, canonical reader execution path, pre-run protected hashes, executable selection and launcher ordering. A function definition line is not a call-site proof. In particular, check whether a cited freshness-check line identifies its definition rather than the executed call.

Validate membership, source/output relationships, files digest, generated timestamp and protected hashes against actual policy and recorded build provenance. Confirm the runtime manifest was generated/read on the run path, and that the BUILD_CANDIDATE remained a separate immutable cross-check.

Audit evidence labels D1–D4, C1 and N1 if present:

• Separate reader-derived returned fields and runtime diagnostics from an independent post-hoc reconstruction.
• Explain exactly which control-flow facts make a downstream diagnostic evidence of reader success and whether an intervening catch/fallback could invalidate that inference.
• N1 described as “if the reader rejected, no Host would launch” is a static counterfactual unless a negative case was actually executed. Do not report it as an executed negative control.
• Do not demand a new negative run or instrumentation in this task.

Return a precise acceptance assessment with strength and limitations, not merely ACCEPTED because the executor used that word.

4. Cause ledger and BLOCKED semantics

Reconstruct all deterministic comparisons from raw values and the exact policy used by this run. The report claims 164 comparisons, 12 failures, two count-related restatements excluded, ten remaining mismatches and two ledger rows. Verify exact membership and provenance.

Produce a table for every failed comparison: exact key, expected value, observed value, originating measurement, associated B1/C1 observation or another cause, policy classification, and causal relationship (independent, duplicate/restatement, aggregate/derived, or unresolved). Preserve original strings; abbreviate large values only with a linked raw record.

The reported two rows are a product/focused-suite row for two failing tests and an infrastructure/runner-comparisons row for ten mismatches. Verify selection precedence and resulting exit 1 mechanically. Separately assess whether those ten comparisons establish independent infrastructure causes or reflect product output discrepancies, parser observation failures and their aggregates. Not being a count comparison does not prove causal independence.

Do not equate ten mismatches with ten independent causes. Do not erase genuine infrastructure evidence merely because a product failure exists. Do not silently relabel BLOCKED as FAIL. If the policy appears semantically overbroad, describe an evidenced policy finding and a separately scoped follow-up; preserve the actual historical verdict.

5. B1 — target identity observation

Verify the failed assertions and fixture contract. Reported values:

• Structured actual: target_db.customer_name
• Structured expected: target_db.tgt_customers.customer_name
• Markdown actual: customer_name
• Markdown expected: tgt_customers.customer_name
• Source identities reportedly retain source_db.customers.cust_name and customers.cust_name.

Check the authenticated synthetic workbook and relevant saved intermediate evidence. Read workbook ZIP/XML with a data-only method if required; do not invoke the product parser. Confirm that the expected table/entity is actually grounded in the fixture and authored contract rather than inferred from the assertion alone.

Trace the relevant source statically from workbook/header mapping through reference resolution, resolved evidence and rendering. The executor suggested missing targetEntity upstream because SttmResolvedEvidence composes [db, entity, field].filter(Boolean).join(’.’). Treat that as a hypothesis until the evidence identifies the failing boundary. Source composition alone does not establish which earlier operation lost the entity.

Separate confirmed symptom, grounded expected behavior, likely owner/smallest code slice, alternative explanations and missing evidence. Recommend a bounded B1 repair/diagnosis task without applying it or weakening expectations.

6. C1 — parser observation

Verify wrapper installation, timing, restoration, module path and observed product call sites from original evidence and actual source/output. Reported values: parserInvocationCardinality=0 and parserInvocations=[], while the wrapper was installed/restored and one invokeTool call produced eight mapping identities.

A zero observation counter does not by itself prove the parser was never called. Examine whether the harness and product necessarily share the same module instance/export, including Host module registries and the actual execution path. A compiled namespace-property call sees a wrapper only if it accesses that same object.

Identify what existing evidence proves, what it rules out, and what remains unresolved between module-instance mismatch, hook timing and an execution path bypassing that export. Do not infer an exact real invocation count from mapping output alone. Do not “fix” the assertion by accepting zero.

If a discriminating probe requires execution or instrumentation, specify the minimum separate C1 diagnostic task and the observation it would distinguish. Do not run it here.

7. Provenance and preservation

Verify source/output identities against original before/after inventories, the build’s compiler/source-map provenance and promoted-file read-back records. Reported output count is 2020; fourteen outputs were created/replaced during the earlier build. Verify the full inventory rather than accepting its total count.

If a preparation outInventorySha256 cannot be reproduced because the original serialization was not retained, distinguish an unreproducible aggregate encoding from a per-file content mismatch. Assess the reported stronger chain of build inventory plus promotion hashes without silently replacing the original digest.

For the pinned distribution, size equality of archive entries and extracted files is not byte-level identity. Read the authenticated retained ZIP without executing/extracting the application, stream relevant entries and compare their SHA-256 with disk counterparts, including Code.exe, application metadata, actual entrypoint and relevant dependency files used in this run. Prefer complete entry-to-file comparison if feasible with existing data-only tooling. Record coverage explicitly if bounded to a subset. Account for commit-prefixed paths and archive containment.

Link any new archive comparison to recorded time-of-run before/after hashes. A review-time match without that linkage proves current correspondence only. Keep signature, version metadata, archive hash, extracted-byte correspondence and runtime executable identity as distinct claims.

Assess repository/config/dependency/output/host/original QA/prior-evidence preservation against actual inventory coverage. Verify original QA and the isolated copy identities, exclusive evidence-write results and parent post-exit verification. A fallback not exercised is not a tested fallback. Unmonitored filesystem areas are not proven unchanged by a scoped inventory.

Keep HISTORICAL_REVIEWED_BASELINE_PRESERVATION separate. Do not reconstruct or claim verification of the unavailable historical baseline from a different snapshot. Do not require unrelated historical reconstruction to decide whether this run’s current-source evidence is useful.

8. Execution scope conformance

Compare original instructions and any authentic contemporaneous amendments to actual behavior. Address concrete reported divergences fairly:

• RUN_ROOT was a separate system-Temp directory, not a child/sibling under the new task parent described in the original plan. The executor cites os.tmpdir containment and allowRootCreation=false. Verify the actual contract and distinguish technical necessity from authorization.
• TEMP/TMP were not redirected. Verify explicit user-data/extensions paths, and state the limits of claims that every runtime write stayed inside controlled roots. Do not infer exhaustive containment from selected before/after hashes.
• Fixture discovery included recursive searches in linked worktree/C:\docs/snapshot locations and a bounded Temp search. Read the actual search commands and their authorization, rather than repeating a “bounded search” summary. Do not conduct those searches again.
• Isolated dependency activation included built-in Copilot and ordered extension development paths. Verify these against the prepared plan and the actual focused contract. Inspect this run’s saved logs for relevant observed activation/network errors; no network probe or profile search.
• Distinguish existing launcher defaults such as –disable-workspace-trust and sandbox-related flags from newly introduced operator changes. Do not claim OS sandboxing or offline operation from launch flags. No network monitor means absence of network activity is not independently established.

For each divergence give the governing instruction, actual action, any contemporaneous authorization, evidence, and concrete impact on scope conformance and trust in the result. Do not invent a retrospective waiver. Do not turn hypothetical risks into findings when no relevant requirement or observation exists.

9. Deliverables and stopping rule

Write under the new review root:

1. report.md — decision first, material findings with exact evidence references, B1/C1 separation and the smallest justified next task.
2. review-result.json — separate axes for evidence acceptability, actual canonical verdict/exit, execution completion, manifest acceptance strength, B1 symptom/root-cause confidence, C1 observation/root-cause confidence, provenance coverage, scope conformance and historical-baseline status.
3. comparison-cause-map.json (and a readable table in the report).
4. evidence-inventory.json plus preserved-evidence copy inventory.
5. commands.log — exact read-only checks, review helper executions, measured statuses and limitations.
6. post-review-preservation.json — verify that original inputs read during this review remain unchanged, and record any instability rather than claiming universal preservation.

Choose and justify a review decision such as ACCEPTABLE_AS_FAILING_RUN_EVIDENCE, ACCEPTABLE_WITH_MATERIAL_LIMITATIONS, NOT_ACCEPTABLE_AS_RUN_EVIDENCE, or BLOCKED_MISSING_CRITICAL_EVIDENCE. Do not manufacture a PASS to close a gate. Grade findings by their concrete effect on the next decision, not by how many checks were performed.

End with a concise recommendation: which independently scoped B1 repair, C1 diagnostic or evidence correction should happen first, why, and its minimum acceptance evidence. If useful, list the other follow-up separately. Do not draft an omnibus repair that silently expands B3 scope. No repair or rerun occurs in this review.

Stop when the existing evidence supports a defensible decision and the remaining uncertainty is explicitly bounded. Report full paths of the review artifacts and any material access limitation. Full B3 runtime acceptance and release authorization remain outside this task.

────────

Appendix A — Original RUN01 brief (verbatim historical scope)

The text below describes the already completed run only. It must not be executed again as part of this review.

TASK_ID: ETL-0908-FOCUSED-HOST-RUN01
TYPE: ONE CONTROLLED FOCUSED EXTENSION-HOST RUN WITH CANONICAL VALIDATION FIRST

Run this complete prompt in a fresh ordinary LOCAL Windows VS Code Agent chat
on recovery-extension-product-0.3.147. Use one Agent and one writer, not the
ETL Orchestrator. Keep engineering artifacts in English. Echo TASK_ID as the
first line of the report.

1. Owner authorization

The owner approves the next controlled focused Host run after
ETL-0907-PINNED-HOST-MANIFEST-PREP01. This task authorizes one invocation of
the existing compiled runner, its canonical manifest validation, the verified
VS Code 1.135.0 Windows x64 Host, the existing producer and exactly the
established focused suite. Product parsing/activation is authorized only as
required by that suite against its authenticated synthetic fixture in an
isolated test workspace.

The preparation task’s no-run restriction is superseded for this invocation.
Do not request that same approval again after preflight succeeds. Continue
autonomously through fixture resolution, preparation, the single run and
evidence analysis. A concrete failed prerequisite stops launch, not the
independent preparation/reporting work.

Authorized writes are task evidence, verified copies of existing synthetic
inputs, and the runtime state/output of this one isolated run, all within the
fresh external TASK_ROOT / RUN_ROOT arrangement described below. The existing
runner’s intended writes and rewrites inside its new run directories are
allowed under its established evidence/freshness rules.

No source/configuration/dependency edits, rebuilding, output promotion, Git
mutation, pin change, download, installation, packaging, release, ordinary
consumer workflow, real-data access, broad test discovery or additional suite
is authorized. Do not resolve editor buffers with Keep/Undo/save/revert, edit
earlier reports, or use installed VS Code 1.136.1 as a substitute.

This is one measured run, not an automatic fix-and-rerun loop. Its success does
not grant release acceptance or prove every B3 failure branch at runtime.

2. Repository and completed preparation

ACTIVE_WORKTREE:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

LINKED_PRIMARY (read-only):
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch: fix/workspace-write-completion-0.3.148
Expected HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
Expected staging: empty.

Expected source dirty inventory:

```text
 M .github/templates/request.md
 M src/core/sttm/SttmUnderstandingReportRenderer.ts
 M src/extension.ts
 M src/test/runTest.ts
 M src/test/suite/index.ts
?? src/test/b3OutcomePolicy.ts
?? src/test/b3OutcomePolicy.unit.test.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts
```

PREP_ROOT locator from the received report (authenticate against disk):
C:\docs\ETL-0907-PINNED-HOST-MANIFEST-PREP01-20260908T020044626Z-57663a80-64c5-4b80-8e4a-02509b2fe2c2

Read its complete report.md, baseline/post-state, future-run-plan.json and
future-run-plan.md, manifest-route record, host identity, download/extraction
receipts, static entrypoint contract and preservation results. Resolve actual
filenames through the report/index when they differ from these descriptions.
Use the executable path in the measured plan, not a path reconstructed from
the screenshot’s wrapped lines.

Resolve BUILD_ROOT from those authenticated records and read the completed
build report, source/output identities, required runtime provenance and
protected-manifest candidate/schema mapping used by this planned invocation.
Read applicable repository instructions and C:\docs\ETL_QUALIFICATION_GLOSSARY.md.
Follow referenced corrected machine identities as needed. Do not repeat all
older reviews or require recovery of the unavailable historical baseline.

If the literal PREP_ROOT locator is wrong or absent, bounded discovery of
direct C:\docs children with the exact preparation task prefix is allowed,
including one timestamp child where necessary. Select by TASK_ID, content,
build references and identities, not merely newest timestamp. Do not search
debug logs, Local History, drives or unrelated profiles for replacement anchors.

Received report cross-checks, not independently measured pins:

• Result: PREPARATION_COMPLETE_AWAITING_FOCUSED_HOST_AUTHORIZATION.
• VS Code 1.135.0 / Windows x64; valid Microsoft Authenticode signature.
• Official archive downloaded on attempt 2, 335078002 bytes.
• 2441 archive file entries matched 2441 extracted files by reported entry/size
checks. Do not describe size matching alone as per-file cryptographic proof.
• Pinned entrypoint contract VERIFIED_STATICALLY.
• Manifest route B_PRELAUNCH_GATE_PROVEN_STATICALLY; canonical acceptance
NOT_EXECUTED.
• Build/source identity matches reported; current out/** has 2020 files.
• Preparation made zero repository writes and ran no Host/tests.
• Missing run input: an absolute ETL_F5_QA_WORKSPACE_ROOT containing
sttm/synthetic_workbook.xlsx, expected size 13201 bytes and an expected SHA-256.

Read full expected hashes, commit, fixture identity and paths programmatically
from original machine evidence and the current authenticated contract. Never
type hashes from photos into scripts. Reject malformed hash fields, and
distinguish an authenticated expected value from a new self-measurement.

3. Read-only preflight and preservation baseline

Create the fresh evidence root using section 5 before persisting baseline
records or fixture copies. The sections specify dependencies, not permission
to write to an uncreated or pre-existing task directory.

Use git –no-optional-locks for reads. Verify exact repository/common-Git
identity, branch, HEAD, staging and dirty inventory. Inspect relevant locks
and process arguments for another writer, watcher, compiler, test Host or
launcher. Do not terminate unrelated processes or remove locks. An ordinary
editor/language server is not by itself a prohibited Host.

Read disk bytes, not potentially stale editor views. Reconcile source and
compiled runtime dependencies with the authenticated build and preparation
POST states. Current source cross-checks are runTest.ts 131240 bytes / 2970
bare LF; b3OutcomePolicy.ts 35970 bytes / 809 CRLF; its unit test 36595 bytes /
758 CRLF; suite/index.ts 10408 bytes / 246 CRLF. Full hashes govern acceptance.

Authenticate the exact prepared Code.exe, product/package version and commit,
and the application files relevant to the pinned contract using retained
inventories. Confirm archive identity and provenance receipts. If the prior
inventory supplies only sizes for relevant files, establish their correspondence
to entries in the retained authenticated archive without replacing the host
distribution. Do not download or re-extract a new distribution for this run.

Capture before-run hashes for the complete out/** inventory, source/policy,
configuration/dependencies used by the run, build-info, consumed prior evidence,
fixture source and prepared Host application files. Compare against the
completed 2020-file output state, not the older 2016-file baseline. Do not
rebuild stale artifacts or bless changed ones with a fresh manifest.

Unexplained drift, missing protected/runtime artifacts, pin mismatch or an
actual concurrent relevant writer prevents invocation. Preserve a precise
finding and complete the report rather than normalizing the discrepancy.

4. Resolve the existing synthetic fixture without fabrication

Read ETL_F5_QA_WORKSPACE_ROOT handling and fixture checks in the existing
runner/focused suite, plus the preparation plan. Recover the expected full
workbook hash and any required companion files from authenticated records/code.
The workbook must be the existing exact 13201-byte fixture, not a newly authored
spreadsheet that merely looks equivalent.

Bounded lookup is authorized in this order:

1. Any absolute QA workspace supplied by the owner or the saved plan/evidence.
2. The current value of the specifically named ETL_F5_QA_WORKSPACE_ROOT, if set.
3. Repository fixture locations and named QA/evidence roots referenced by the
existing suite, runner, governing instructions or prior reports. Filename
searches for synthetic_workbook.xlsx inside those identified roots are allowed.

Do not scan all drives, arbitrary consumer workspaces or user documents.
Distinguish missing, inaccessible and wrong-hash candidates. Read original
fixture bytes as data and record each candidate’s absolute path, size/hash and
comparison. Do not open/resave it in Excel, regenerate it, change expected
hashes, or download a replacement.

Once authenticated, create an isolated QA workspace under TASK_ROOT using
exact verified copies of that fixture and only the existing synthetic companion
files the focused contract requires. Preserve original source paths read-only.
Use the actual required relative path sttm/synthetic_workbook.xlsx. Record
source/copy hashes and any required workspace/template identity. Do not invent
an ETL workspace layout, fabricate a consumer configuration, or copy profiles,
credentials, real datasets or unrelated repositories.

Set ETL_F5_QA_WORKSPACE_ROOT for the future child to this actual absolute isolated
workspace path, provided the contract permits a verified copy there. If the
contract requires a different test-only placement, resolve it within the fresh
task scope before launch; do not bypass a path/root check.

If no exact fixture is found, finish all independent preparation and report
BLOCKED_FIXTURE_UNRESOLVED with searched roots and mismatches. Ask only for the
absolute location of the existing authenticated QA workspace/workbook. Do not
launch the runner to discover that the fixture is missing.

5. Fresh task/run directories and concrete invocation plan

Validate the existing C:\docs parent and containment outside both worktrees,
old evidence/snapshots, everyday profiles and consumer workspaces. Create one
exclusive new flat task leaf:

C:\docs\ETL-0908-FOCUSED-HOST-RUN01-<UTC>-<GUID>\

Use fs.mkdirSync(leaf, { recursive: false }) and a creation receipt written with
exclusive new-file semantics. Record actual completion; check-then-create alone
does not prove exclusive creation. Do not reuse the preparation root or a
directory merely named in an earlier plan.

Allocate runtime paths according to the real freshness contract. TASK_ROOT holds
supervisory evidence and fixture copies; RUN_ROOT is a separate, initially
absent child reserved for the runner when the runner requires exclusive creation.
Do not populate its required-empty directories, completion markers or per-run
authorization flags beforehand. If the contract requires sibling roots instead,
document their safe common new parent and exact creation ownership before use.

Before invocation, freeze execution-plan.json from the saved future plan and
current code. Record the actual executable/Node paths, working directory,
compiled runner, producer and single focused-suite entrypoints, environment,
arguments, fixture hashes, manifest input strategy, expected test count and
all permitted runtime write roots.

Required properties:

• ETL_TEST_VSCODE_EXECUTABLE_PATH resolves to the authenticated 1.135.0 Code.exe;
show the actual code path bypassing automatic download. Do not change the pin.
• Use the existing compiled runner’s supported focused selector; no standalone
Mocha substitute, direct producer call, glob expansion or broad discovery.
• Derive all other environment names and selectors from the current code/plan.
Do not guess them. Record how they reach the Host/producer.
• Isolated user-data, extensions, logs, caches, TEMP/TMP, QA and evidence paths
are supplied through the established contract and child-specific environment.
Do not persist global environment/settings or copy everyday editor state.
• No portable data-folder or inherited profile/IPC setting may redirect the
test into the everyday editor/profile. Apply only established compatible
child-local isolation controls; do not change security/trust policy to force a run.
• Product access is limited to this synthetic suite. No Databricks, SQL Server,
consumer jobs, credentials or deliberate network calls are part of this run.
• Use existing supported update/telemetry/network suppression and document
effective settings. Do not claim an OS network sandbox merely from flags.
If the suite requires external services or real data, stop before launching.
• Establish a finite timeout from the saved plan/current test contract and a
documented small shutdown allowance. Record the numeric deadline before run;
do not extend it simply because the run is stuck.

Inspect planned writes in the runner, producer and selected test before launch.
Read the complete selected suite and inspect its runtime dependency closure
for top-level effects, fixture access and writes, not only its test names.
Harness-owned creation/modification of synthetic test outputs and runtime
profiles inside the new roots is authorized. Source, out/, the prepared Host
application and old evidence remain immutable. If the current code requires
writes outside this boundary, identify the actual coupling before invocation.

6. Canonical validation is the first real gate of the single run

Read the proven route B from manifest-route and the actual compiled call path.
Reconfirm that the existing readProtectedHashManifest validation completes
successfully before any launcher/Host invocation, and that its failure stops
that path. This must be true for the selected focused invocation, including
error branches and top-level initialization.

Use exactly the manifest mechanism documented by that route: supply the
authenticated candidate if accepted by the real schema, derive a documented
payload if needed, or let the existing runner create its legitimate run-bound
manifest. Keep prior candidates immutable. Derive policy membership/order,
source-artifact relations and digests from the established canonical policy.
The reported 12 members / 11 relations are cross-checks, not replacement lists.

Do not manufacture successful validation, run authorization, result delivery,
freshness timestamps or completion markers. Let the real run generate its own
nonce and other run-bound values using the supported mechanism.

Identify BEFORE invocation which existing evidence/control-flow observations
can establish that the canonical reader executed and accepted the input. Use
actual emitted evidence and authenticated control flow; do not require adding
new logs merely to obtain a particular wording. If acceptance is inferred from
a downstream observation that is reachable only after validation, label it
INFERRED_FROM_AUTHENTICATED_CONTROL_FLOW and retain that proof. Do not equate
a data-only checker, source inspection or a generic exit 0 with reader execution.

Do not import the runner for exploratory checks: its unconditional main() is
the execution. Do not strip main(), monkey-patch launch/process APIs, evaluate
an extracted reader or execute a modified copy. If the actual prelaunch gate
cannot be established, report BLOCKED_CANONICAL_PRELAUNCH_GATE and do not launch.

Canonical validation and the permitted Host are parts of the SAME single
runner invocation. A separate runner ‘probe’ would consume the one invocation.
If canonical validation rejects, preserve the failure and report Host NOT_RUN;
do not patch the manifest/policy and try again in this task.

7. Execute once, supervise and preserve the real outcome

After all prerequisites pass, launch the existing compiled runner once using
the frozen plan. No extra approval is needed. Capture the exact command/argument
array, necessary nonsecret child environment, working directory, UTC start/end,
stdout/stderr, actual tool/process completion, parent/child PIDs and exit status.
Use the existing installed Node; no npm/npx scripts, compiler or package install.

The single invocation may start its one supported focused Host and producer.
Do not perform separate smoke launches, Code –version probes, unit reruns or
an extra attempt after a failed run. Preparation helpers may be corrected before
invocation with separate retained artifacts, without changing repository code.

Supervise the finite deadline. A task-owned supervisor may stop only the runner
and descendant Host processes created by this invocation on timeout or a
detected boundary breach. Establish process ownership/start identity before
termination; never kill all node.exe/Code.exe processes or target the everyday
editor by name. Record the reason, actual PIDs and termination results. A timeout
is a measured incomplete/blocked outcome, never a passing test. Preserve logs
and partial runtime directories; do not clean up or restore files automatically.
Keep the owner informed during the run with a brief update at least once per
minute; poll the actual running process rather than starting another invocation.

Record whether the intended Host actually started and its observed version,
whether the focused producer ran, whether a result was delivered, and whether
finalization/post-exit verification completed. Do not assume that runner start
means Host execution or that a Host process alone means the suite completed.

After a failure, read-only diagnosis from this attempt is authorized. Source
repair, assertion weakening, expectation changes and a second invocation are
not. Provide a bounded next repair proposal if the evidence identifies a defect.

8. Interpret the current result and verify preservation

Read the real current-run ledger, producer result, runner evidence and final
verdict using their actual schema. Verify, as applicable:

• Run identity/nonce, focused-suite identity, delivery protocol and completion
correlate to this invocation and its fixture; no stale result is accepted.
• Expected test count and tests/passes/failures/pending consistency follow the
existing validator. Zero executed tests is not a successful focused run.
• Counted product failures with trustworthy completed delivery remain FAIL
when no independent infrastructure cause exists.
• Independent launcher/Host/infrastructure failures remain retained and affect
the verdict according to the current policy; do not relabel them as product
failures merely because a result file also contains failures.
• Missing/foreign/unusable evidence cannot establish PASS or product FAIL.
• Evidence writes, reduced-evidence fallback, finalization and post-exit checks
are reported exactly as observed, including any paired failures.

Do not inject failures or run negative cases in this task. Report unexercised
branches as NOT_EXERCISED, even if earlier isolated unit tests covered them.
Keep runner verdict/exit status separate from your assessment of whether this
attempt supplied trustworthy evidence. Exit 0 alone is not sufficient, and a
trustworthy FAIL can be a valid executed test result without being a passing gate.

Compare after-state against the intake inventories: source, out/**, configuration,
dependencies, build-info, prepared Host application, original fixture and prior
evidence consumed. Report exact differences. Expected task writes are confined
to the declared new test/runtime/evidence roots. Do not claim that unrelated
background OS/editor activity was exhaustively observed or caused by this task.
Verify HEAD, branch, empty staging and source dirty inventory remain unchanged.
Record remaining owned processes and whether the intended shutdown completed.

Any unexplained protected/source/output change invalidates a clean acceptance
claim even if the tests printed success. Preserve the changed bytes/evidence
without repairing or reverting them. Classify only what the evidence supports.

9. Deliverables and final result

Keep under TASK_ROOT: report.md; creation receipt; baseline/post-state;
fixture-resolution and source/copy identity records; frozen execution plan;
supervisor/helper source; raw command logs/status; references to untouched
runner/Host evidence; canonical-validation proof; result assessment; and
preservation/process checks. Serialize new JSON from measured objects and
strictly re-parse it. Retain failed/intermediate artifacts and explicitly link
separately named corrections. Do not hand-transcribe measured hashes.

Choose one result:

```text
TASK_ID: ETL-0908-FOCUSED-HOST-RUN01
RESULT: FOCUSED_RUN_PASSED_AWAITING_INDEPENDENT_REVIEW |
        FOCUSED_RUN_COMPLETED_WITH_PRODUCT_FAILURES |
        FOCUSED_RUN_BLOCKED_OR_INCOMPLETE |
        BLOCKED_BEFORE_INVOCATION_<REASON> |
        INVALIDATED_BY_BOUNDARY_OR_PRESERVATION_FAILURE
PREP_ROOT: <authenticated path>
BUILD_ROOT: <authenticated path>
QA_WORKSPACE_AND_FIXTURE: <absolute paths, measured/expected identities>
PINNED_HOST: <actual executable path, version, architecture, commit and hash>
CANONICAL_READER: ACCEPTED | REJECTED | NOT_REACHED | UNPROVEN
CANONICAL_READER_PROOF: <direct evidence or explicitly identified inference>
RUNNER_INVOCATIONS: <0 or 1; report any actual deviation>
HOST_EXECUTION_AND_VERSION: <actual observation or NOT_RUN>
RUN_IDENTITY_AND_RESULT_CORRELATION: <actual result>
TESTS_PASSES_FAILURES_PENDING: <measured counts, or NOT_AVAILABLE>
RUNNER_VERDICT_AND_EXIT: <actual values, or NOT_AVAILABLE>
INDEPENDENT_CAUSES_RETAINED: <observed evidence; unexercised cases identified>
FINALIZATION_AND_POST_EXIT: <actual outcome>
PRESERVATION: <measured result and discrepancies>
TIMEOUT_OR_OWNED_PROCESS_TERMINATION: <actual outcome>
HISTORICAL_REVIEWED_BASELINE_PRESERVATION: NOT_VERIFIED
FULL_B3_OR_RELEASE_ACCEPTANCE_GRANTED: NO
REPORT_PATH: <exact absolute path>
REMAINING_BLOCKERS: <specific findings or NONE_FOR_THIS_RUN>
```

The passing result requires accepted canonical validation, the correct pinned
Host and authenticated fixture, the intended completed focused suite with
passing results under its existing count rules, consistent run-bound evidence,
completed required finalization, correct verdict/exit and preserved boundaries.
It does not establish independent acceptance or qualification of unexercised
failure branches. Keep the historical baseline limitation separate from the
current-run evidence; do not silently claim it was closed.

Finish with a short chat summary containing the exact report path, whether the
Host ran, actual test counts/verdict/exit, manifest acceptance, preservation
result and remaining blockers. Stop. Do not self-perform the independent review,
repair/rebuild/rerun, expand the suite or package/release the extension.
