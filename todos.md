Refresh only the committed EvalGating baseline evidence after the accepted and committed W1 workspace-write collision repair.

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required branch:

fix/workspace-write-completion-0.3.148

Product decision carried forward

The following items are intentionally deferred and are not release blockers for this hotfix:

Batch atomicity is intentionally deferred.
Durable managed-file ownership is intentionally deferred.
Partial apply is accepted product behavior.
The tool must accurately report created, overwritten, unchanged, failed, blocked, and skipped files.
Users may review or revert workspace changes through VS Code Source Control.

Do not implement or document these items in repository files during this task. Include them only in the final report so they can later be copied into the pull-request description.

Preflight

Confirm:

* The repository path and branch match.
* The working tree and index are clean.
* The current HEAD subject is:

fix: enforce trusted workspace write collision checks

* The current HEAD has exactly one parent.
* Its parent is:

64706129e0d1054ea615e150b28dd623fb3c629e

* The branch contains exactly one commit above that parent.
* Nothing has been pushed.

Record the current full HEAD SHA.

If any condition differs, stop without editing and return:

EVAL_REFRESH_PREFLIGHT_BLOCKED

Discover the authoritative refresh process

Locate the source for these two failing tests:

EvalGating > passes against the committed Phase H baseline report
EvalGating > allows deterministic v3 baseline reports without prompt telemetry

Use repository search to identify:

* the committed Phase H baseline report;
* the authoritative generator or refresh command;
* the tracked behavior-input list;
* every output file that the refresh command is expected to modify.

Do not infer or invent a refresh process.

Do not manually edit hashes, timestamps, tracked-input lists, or report content.

Before running anything, confirm that the authoritative refresh:

* is deterministic;
* runs locally;
* requires no production-source modification;
* will not modify prompts, workflows, package files, versions, tests, or Copilot customization assets;
* will update only the intended committed evaluation evidence.

If no authoritative deterministic refresh command exists, or if it would modify files outside evaluation evidence, stop and return:

EVAL_REFRESH_PROCESS_BLOCKED

Report the exact reason and make no changes.

Verify the intended tracked-input drift

Before refreshing, confirm that the two EvalGating failures are caused only by the already accepted W1 production changes.

The previously reported tracked files were:

src/chat/DeployCoordinator.ts
src/chat/WriteCoordinator.ts
src/core/artifacts/ArtifactDestinationInventory.ts
src/core/artifacts/WorkspaceDestinationProbe.ts
src/core/trusted/WriteAuthorization.ts

If the actual tracked drift contains an unexpected production file, prompt, workflow, package file, test file, or documentation file, stop without refreshing and report:

EVAL_REFRESH_UNEXPECTED_DRIFT

Refresh

Run the repository’s authoritative deterministic baseline-refresh command exactly as designed.

Do not modify the generated result manually afterward.

After generation, run:

git status --short
git diff --check
git diff --stat

Inspect the complete generated diff.

The diff must:

* modify only committed evaluation baseline evidence;
* represent the accepted W1 behavior changes;
* contain no production-source changes;
* contain no test weakening;
* contain no package or version changes;
* contain no prompt, workflow, CI, or Copilot customization changes;
* contain no unrelated formatting churn;
* contain no machine-specific absolute paths;
* contain no nondeterministic timestamps or temporary values unless the repository’s established format explicitly requires them.

If the generated diff violates these requirements, preserve the generated files for inspection, do not stage or commit, and return:

EVAL_REFRESH_OUTPUT_BLOCKED

Validation

Run the narrowest supported EvalGating test first.

It must make both EvalGating tests pass.

Then run exactly once:

npm run compile
npm run test:unit

Expected full unit-test result:

2332 passing
5 pending
3 failing
exit code 1

The only permitted remaining failures are the same three pre-existing Copilot customization failures:

1. Missing deploy-v3 agent tool-context prompt.
2. Missing frontmatter name in the business-context instructions file.
3. Residual module-level AGENT.md files.

Acceptance requires:

* both EvalGating tests pass;
* no workspace-write test fails;
* no new failure appears;
* compilation exits 0;
* the total result is exactly 2332 passing, 5 pending, and 3 failing;
* current HEAD remains unchanged;
* only evaluation evidence files remain modified;
* nothing is staged.

Do not fix or suppress the three permitted failures.

Final report

Report:

* starting and ending HEAD;
* authoritative refresh command;
* exact files generated or modified;
* tracked W1 input files represented in the baseline;
* focused EvalGating test result;
* compile result;
* full unit-test totals;
* complete names of the three remaining failures;
* git diff --check result;
* final git status --short;
* confirmation that no production source was edited;
* confirmation that nothing was staged, committed, or pushed.

Include this release-scope note verbatim in the report:

Accepted release limitation:
Batch atomicity and durable managed-file ownership are deferred.
Partial apply remains supported and must be reported accurately per file.
Workspace changes remain reviewable and revertible through VS Code Source Control.

Return exactly one verdict:

EVAL_BASELINE_REFRESH_READY_FOR_REVIEW

or one of the blocking verdicts defined above.

Restrictions

Do not:

* stage or commit;
* push or create a pull request;
* change production source;
* change tests;
* change prompts or Copilot customization assets;
* change package or version files;
* implement atomic apply;
* implement managed ownership;
* run F5, package, install, or external QA;
* merge, rebase, reset, clean, or stash.

Stop after reporting.
