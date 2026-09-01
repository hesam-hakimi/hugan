Step 0.1 — Close the Phase H Tracked-Input Coverage Gap

Objective

Implement one bounded, tracking-only repair that:

1. Adds the five confirmed behavior-critical surfaces to Phase H freshness tracking.
2. Adds focused regression coverage using the real Phase H input collector.
3. Proves the expanded baseline becomes stale before refresh.
4. Runs npm run eval:golden exactly once.
5. Reconciles the full test suite against the exact known baseline.
6. Creates one atomic local commit.

Do not begin F5, QA workspace, STTM, fixture, render, validation, preview, approval, or write work in this task.

Execution environment

Run in the normal writable VS Code source-repository window:

Repository root:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
Required branch:
fix/workspace-write-completion-0.3.148
Required starting HEAD:
edeaaa74fa84df715fedb7b2d9f50f2418018770
Required starting subject:
test: refresh Phase H evaluation baseline

This path is a linked Git worktree. Operate only in this exact worktree root, not its parent clone.

If PowerShell cannot resolve git, node, npm, or npx because PATHEXT is malformed, prefix only the affected invocation with:

$env:PATHEXT = '.COM;.EXE;.BAT;.CMD'

Do not persist that workaround.

Preflight gate

Before editing, verify and record:

1. Canonical repository root.
2. Branch.
3. Full HEAD SHA and subject.
4. Sole parent and parent count.
5. Linear topology through Repair A, Repair B, and Eval Refresh.
6. git status --short --untracked-files=all is empty.
7. Index has no staged paths.
8. Stash is empty.
9. All required Git objects exist.
10. Current Phase H report contains 257 tracked paths and does not include the five critical paths listed below.

Stop immediately if any identity or cleanliness check differs.

Do not fetch, pull, merge, rebase, reset, checkout, stash, clean, amend, cherry-pick, or push.

Exact edit allowlist

Only these four tracked files may change:

src/test/eval/EvalGovernance.ts
src/test/suite/evalGating.test.ts
docs/eval/phase_h_latest_report.json
docs/eval/phase_h_latest_report.md

The two report files may change only through the single authorized Golden generation.

Do not modify:

* production source;
* Repair A or Repair B implementation;
* canonical contract contents;
* package.json;
* package version;
* dependencies or lockfiles;
* .vscode;
* .vscodeignore;
* launch configuration;
* build scripts;
* fixture or QA workspace files;
* Eval generator behavior.

If an additional tracked or untracked path changes, stop and report it.

Phase 1 — Extend the authoritative tracking patterns

In:

src/test/eval/EvalGovernance.ts

extend PHASE_H_TRACKED_INPUT_PATTERNS with exactly these category patterns:

'package.json',
'resources/copilot/context/**/*.md',
'resources/framework/**/*.json',
'src/tools/**/*.ts',

Preserve all existing patterns and existing behavior.

Do not replace the list with a broad src/**/*.ts or resources/**/* pattern.

Before Golden refresh, enumerate every repository path newly matched by these four patterns. At minimum, the resulting tracked set must include:

src/tools/EtlReadOnlyToolService.ts
src/tools/EtlActionToolService.ts
resources/framework/contracts/job-config-envelope.v1.json
resources/copilot/context/etl-module-reference.md
package.json

The expected src/tools/**/*.ts expansion currently includes five runtime tool-boundary files:

src/tools/EtlReadOnlyToolService.ts
src/tools/EtlActionToolService.ts
src/tools/index.ts
src/tools/TrustedWriteApprovalStore.ts
src/tools/WriteApprovalContext.ts

Verify this from the live repository rather than relying only on this prompt.

Phase 2 — Add focused regression coverage

Update only:

src/test/suite/evalGating.test.ts

Add focused regression tests that exercise the real Phase H tracked-input collector and prove:

1. All five confirmed critical paths are included.
2. Windows and repository-relative path normalization does not invalidate the assertions.
3. Representative src/test/** files remain excluded.
4. docs/reference/ETL_MODULE_REFERENCE.md remains excluded.
5. The test does not depend on a brittle total tracked-file count.
6. The assertions validate actual collector output, not merely the presence of string literals in the source array.

Let N be the exact number of new passing test cases added. Record N for final full-suite arithmetic.

Do not modify tests to weaken any existing Eval gate.

Phase 3 — Expected stale-baseline proof

Compile using the repository-owned compile script as needed for the edited TypeScript:

npm run compile

Then run the narrow focused Eval tests using the repository’s existing supported test command.

Before regenerating Golden, run:

npm run eval:check

This command is expected to fail only because:

baselineStatus: stale

The stale evidence must be limited to the paths newly admitted by the four added patterns.

Before continuing, record:

* old tracked-file count;
* new collector file count;
* every newly admitted relative path;
* old tracked-input digest;
* current digest;
* exact stale-path inventory.

Stop if:

* eval:check unexpectedly passes;
* an existing tracked path has an unexplained content change;
* any required scenario fails;
* schema, corpus, or scenario semantics change;
* the stale set contains an unexpected path;
* any failure is unrelated to expanded tracked-input coverage.

Do not fix or bypass unexpected results.

Phase 4 — Single Golden refresh

Only after the expected stale state is proven, run exactly once:

npm run eval:golden

Do not run this command a second time.

If the command fails or produces unexpected output, stop. Do not retry or overwrite the first-run evidence.

After the single run, inspect both generated reports and prove:

scenarioCount = 9
coverage.missingRequiredScenarios = empty
acceptanceRate = 1
parityRate = 1
validationSuccessRate = 1
correctionRate = 0
schema version = 1
corpusVersion = phase-h-v1
all 9 scenario rows = PASS / PASS
overall gate = PASS

Expected changes:

* expanded tracked path list;
* hashes for newly admitted files;
* tracked-input digest;
* changed-input evidence;
* generatedAt;
* per-scenario and aggregate latency values.

Timestamps and latency are wall-clock fields and need not be byte-identical.

No scenario meaning, prompt sample, Markdown answer, JSON answer, schema, acceptance result, parity result, validation result, or required-scenario inventory may change.

The reports must show all five critical paths in the tracked-input inventory.

Phase 5 — Post-refresh validation

Run:

npm run eval:check

Require:

baselineStatus: current
Phase H gate: PASS

Then run:

1. The focused Eval gating suite.
2. git diff --check.
3. The sanctioned full unit suite exactly once:

npm run test:unit

Do not run workflow.test.js headlessly. It requires its supported VS Code/Extension Host harness and is outside this task.

Full-suite reconciliation

The pre-change sanctioned baseline was:

2358 passing
5 pending
3 failing

With N newly added passing regression tests, the expected final shape is:

2358 + N passing
5 pending
3 failing

The two former Eval freshness failures must pass and must not appear in the failure list.

Only these three exact failures may remain:

1. Exact test:

Copilot workflow customization > maintainer delivery prompt references real repo-local agents

Essential signature:

ENOENT
.github/prompts/deploy-v3-agent-tool-context-gap.prompt.md

2. Exact test:

Copilot workflow customization > repo customization assets use valid frontmatter and agent file naming

Essential signature:

.github/instructions/business-context.instructions.md
frontmatter must declare a name

3. Exact test:

Copilot workflow customization > source tree uses standard AGENTS.md guidance instead of module AGENT.md files

Essential signature:

11 tracked src/**/AGENT.md files versus expected []

If these three identities and signatures match exactly:

* record them as known baseline failures;
* do not rerun them individually;
* do not reinvestigate them;
* do not modify unrelated files to silence them.

Any additional failure, missing failure, changed signature, timeout, crash, infrastructure error, or Eval freshness failure blocks the commit.

Enumerate all five pending test identities and their source locations. Confirm none covers:

* Phase H freshness;
* public ETL discovery;
* public validation;
* ETL Orchestrator;
* Extension Development Host;
* preview, approval, or write behavior.

Do not attempt to fix pending tests in this task.

Generated cache handling

out/ is ignored and may be regenerated by the authorized compile/Golden commands. It must not be staged or committed.

If and only if .tsbuildinfo.test becomes modified solely by the sanctioned compile/test commands:

1. Record its diff and pre-run HEAD identity.
2. Restore only that exact file from the pinned starting HEAD.
3. Verify it is byte-identical to the starting HEAD.

This is the only authorized restoration. Do not restore, reset, or checkout any other path.

Phase 6 — Commit gate

Before staging, require:

git diff --check

and prove the changed tracked-path inventory is exactly:

src/test/eval/EvalGovernance.ts
src/test/suite/evalGating.test.ts
docs/eval/phase_h_latest_report.json
docs/eval/phase_h_latest_report.md

No other tracked or untracked path may exist.

Verify all Repair A/B production, contract, packaged-documentation, package, W1-protected, and Eval implementation files outside this four-path allowlist remain byte-identical to the starting HEAD.

Stage the four paths explicitly. Do not use:

git add .
git add -A

Create exactly one local commit with subject:

test: close Phase H tracked-input coverage gap

Do not amend or squash any prior commit.

Post-commit verification

Prove:

1. The new commit has exactly one parent.
2. Its sole parent is:

edeaaa74fa84df715fedb7b2d9f50f2418018770

3. The commit contains exactly the four authorized paths.
4. Branch remains:

fix/workspace-write-completion-0.3.148

5. Worktree, index, untracked inventory, and stash are empty.
6. Package version remains 0.3.147.
7. No dependency or lockfile changed.
8. No F5 launch, VSIX operation, QA workspace access, fixture authoring, external service call, approval, write, or push occurred.

Required English report

Return:

1. Preflight evidence.
2. Old and new pattern lists.
3. Exact newly matched path inventory.
4. Regression tests added and value of N.
5. Expected pre-Golden stale evidence.
6. Confirmation Golden ran exactly once.
7. Post-Golden semantic report comparison.
8. Focused test results.
9. Full-suite totals.
10. Exact three known failure identities/signatures.
11. Exact five pending identities and source locations.
12. git diff --check result.
13. Final changed-path inventory.
14. New full commit SHA, subject, and sole parent.
15. Final clean-state evidence.

Finish with exactly one of:

PHASE_H_TRACKING_REPAIR_COMMITTED

or, if any gate cannot be satisfied:

PHASE_H_TRACKING_REPAIR_BLOCKED
