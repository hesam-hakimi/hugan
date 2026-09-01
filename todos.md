Validate and regenerate the existing uncommitted Phase H EvalGating baseline evidence.

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required branch:

fix/workspace-write-completion-0.3.148

Authorized starting state

The working tree is intentionally expected to contain exactly these two unstaged modified files:

docs/eval/phase_h_latest_report.json
docs/eval/phase_h_latest_report.md

Nothing else may be modified, staged, untracked, or deleted.

These files appear to contain an earlier uncommitted baseline refresh, but their provenance has not yet been established.

This task explicitly authorizes replacing only these two existing dirty files by running the repository’s authoritative baseline generator once.

Do not discard, reset, stash, or manually edit them.

Preflight

Confirm:

* Repository and branch match.
* The index is clean.
* The working tree contains exactly the two authorized modified files.
* The current HEAD subject is:

fix: enforce trusted workspace write collision checks

* The current HEAD has exactly one parent.
* Its parent is:

64706129e0d1054ea615e150b28dd623fb3c629e

Record:

* full HEAD SHA;
* SHA-256 hash of each current report file;
* current diff of both files;
* current generatedAt;
* current trackedInputs.digest;
* tracked input paths;
* scenario identities, statuses, and counts;
* all latency and timing fields.

If any additional dirty or staged path exists, stop and return:

EVAL_REGEN_PREFLIGHT_BLOCKED

Discover the authoritative generator

Locate the source for:

EvalGating > passes against the committed Phase H baseline report
EvalGating > allows deterministic v3 baseline reports without prompt telemetry

Identify:

* the authoritative generator;
* the exact supported refresh command;
* the expected output paths;
* stable behavioral evidence fields;
* observational or nondeterministic fields;
* fields included in trackedInputs.digest;
* fields intentionally excluded from behavioral identity.

Do not infer the command from filenames alone.

Do not manually modify report content, hashes, tracked inputs, timestamps, scenarios, or latency values.

If no authoritative local generator exists, stop and return:

EVAL_REGEN_PROCESS_BLOCKED

Determinism interpretation

Do not require the complete report files to be byte-identical between executions if the established generator intentionally includes:

* generatedAt;
* wall-clock duration;
* measured latency;
* environment-specific timing observations.

These fields may change only if the official generator and schema explicitly define them as observational.

The following must remain semantically stable:

* tracked input paths;
* tracked input content hashes;
* trackedInputs.digest;
* scenario identities;
* scenario order where defined;
* scenario outcome/status;
* pass/fail classification;
* absence of prompt telemetry;
* report schema and version;
* product-behavior conclusions.

A latency-only difference is not a blocker when latency is explicitly observational and excluded from behavioral identity.

Preserve the current evidence before regeneration

Copy the two existing report files byte-for-byte to a unique temporary directory outside the repository.

Record their SHA-256 hashes.

The temporary copies are evidence only. Do not add them to Git or place them inside the repository.

Regenerate once

Run the authoritative refresh command exactly once in the repository.

It may replace only:

docs/eval/phase_h_latest_report.json
docs/eval/phase_h_latest_report.md

Do not run the generator a second time.

After generation, record:

* SHA-256 of both newly generated files;
* exact files changed;
* diff against HEAD;
* semantic differences from the preserved pre-existing reports;
* differences limited to generated time or latency;
* stable tracked-input and scenario comparison.

If the generator modifies or creates any additional repository path, stop without staging or committing and return:

EVAL_REGEN_OUTPUT_BLOCKED

Do not delete or conceal unexpected output.

Validate the refreshed evidence

Confirm that the refreshed report represents exactly these accepted W1 tracked inputs:

src/chat/DeployCoordinator.ts
src/chat/WriteCoordinator.ts
src/core/artifacts/ArtifactDestinationInventory.ts
src/core/artifacts/WorkspaceDestinationProbe.ts
src/core/trusted/WriteAuthorization.ts

Confirm:

* no unexpected tracked input appears;
* every expected tracked input hash matches the current committed HEAD;
* the digest is computed by the official generator;
* no prompt telemetry is present;
* no production source, tests, prompts, workflows, packages, versions, or Copilot customization assets were modified.

Run:

git diff --check

Then run the narrowest supported EvalGating test.

Both EvalGating tests must pass.

After the focused test passes, run exactly once:

npm run compile
npm run test:unit

Expected full unit result:

2332 passing
5 pending
3 failing
exit code 1

The only permitted failures are:

1. Missing deploy-v3 agent tool-context prompt.
2. Missing frontmatter name in the business-context instructions file.
3. Residual module-level AGENT.md files.

No workspace-write test may fail.

Final state

At completion:

* HEAD must be unchanged.
* Nothing may be staged.
* Exactly the two evaluation report files may remain modified.
* No other repository path may be changed.
* Do not restore the earlier report copies over the officially regenerated output.
* Keep the temporary evidence copies only until the report is complete, then remove that temporary directory.

Final report

Report:

* starting and ending HEAD;
* authoritative generator and exact command;
* hashes of the pre-existing reports;
* hashes of the officially regenerated reports;
* semantic comparison between them;
* explicitly sanctioned nondeterministic fields;
* stable tracked-input digest and scenario comparison;
* exact modified files;
* focused EvalGating results;
* compilation result;
* full unit-test totals;
* complete names of the three remaining failures;
* final git status --short;
* confirmation that nothing was staged, committed, or pushed.

Include:

Accepted release limitation:
Batch atomicity and durable managed-file ownership are deferred.
Partial apply remains supported and must be reported accurately per file.
Workspace changes remain reviewable and revertible through VS Code Source Control.

Return exactly one verdict:

EVAL_BASELINE_REGENERATED_READY_FOR_COMMIT

or one of the blocking verdicts defined above.

Restrictions

Do not:

* manually edit either report;
* modify production source or tests;
* stage or commit;
* push or create a pull request;
* change package or version files;
* change prompts, workflows, CI, or Copilot customization assets;
* implement atomic apply or managed ownership;
* run F5, package, install, or external QA;
* merge, rebase, reset, clean, or stash.

Stop after reporting.
