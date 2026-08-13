Task: LOCAL-PHASE-A0R-AB-VALIDATION-20260813-01
Mode: isolated differential validation only
Target: extension-source
Delivery: report-only
Mutation authorization: NONE

Purpose

Phase A0R currently reports:

* TypeScript test compilation: PASS
* focused suites: 32 passing, 0 failing
* registered A0 run: 6 passing, 0 failing
* all original eight failures resolved
* real worktree and protected files unchanged

However, the broader pure-unit run reported nine failures and classified them as unrelated without showing results from clean HEAD under the identical dependency tree and test command.

Do not accept that classification based on filenames, suite names, historical knowledge, or intuition. Prove it through an isolated A/B comparison.

Hard boundaries

1. Do not click Keep or Undo. Leave the nine-file review card pending.
2. Do not start, plan, or implement Phase A1.
3. Do not modify any source, test, configuration, documentation, package, generated output, or workspace file.
4. This task is validation-only. If a regression or coverage gap is found, report it and stop.
5. Do not stage, commit, push, merge, rebase, switch branches, edit PR #7, invoke CI, or make any Git/PR/CI mutation.
6. Do not package, rebuild, install, uninstall, or replace a VSIX.
7. Do not install dependencies or run compilation/tests in the real repository.
8. Do not touch any real Consumer workspace or external Databricks, ADF, SQL Server, or storage system.
9. Do not alter:
    * .tsbuildinfo.test
    * package.json
    * CopilotAssetCatalog.ts
    * EtlActionToolService.ts
10. Do not repair failures during this task.

Expected identity

Verify read-only:

* origin: https://github.com/TD-Universe/agentic_etl.git
* branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* HEAD package.json version: 0.3.139
* protected dirty package.json version: 0.3.128
* staged changes: none
* candidate and installed VSIX: 0.3.139, both PRE-A0R

Capture before-state:

* exact git status --porcelain;
* registered worktrees;
* SHA-256 of all nine pending A0R files;
* SHA-256 of all four protected dirty files;
* candidate VSIX SHA-256;
* protected control-plane hashes.

If identity or scope differs, stop with:

LOCAL_PHASE_A0R_AB_BLOCKED_IDENTITY_OR_SCOPE

Exact B overlay

Resolve the canonical repository paths for exactly these nine pending files:

1. TrustedPlanningEvidenceService.ts
2. EtlAgent.ts
3. AgentMessageRouter.ts
4. AgentActionExecutor.ts
5. ResponseComposer.ts
6. index.ts
7. trustedPlanningEvidenceService.test.ts
8. testPatterns.ts
9. phase5AgentRouter.test.ts

Prove before testing that:

* no tenth file belongs to the A0R overlay;
* SolutionMemoryStore.ts is unchanged;
* none of the four protected dirty files is included;
* no out/**, node_modules, cache, VSIX, or Consumer content is included.

Isolated A/B environment

Create one unique OS temporary root outside the real repository and all Consumer workspaces.

Create a dependency seed from git archive HEAD:

1. Confirm its package.json is committed version 0.3.139.
2. Because HEAD has no committed lockfile, install dependencies only in this temporary seed.
3. Record:
    * Node version;
    * npm version;
    * exact install command and exit code;
    * generated temporary lockfile SHA-256;
    * npm ls --depth=0;
    * dependency-resolution timestamp.
4. Label the run:

UNPINNED_TEMP_DEPENDENCY_RESOLUTION

5. Never copy node_modules, lockfiles, outputs, or caches into the real repository.

From the same dependency seed, create:

* A1: clean committed HEAD
* B1: identical environment plus exactly the nine-file A0R overlay
* A2: a second fresh clean HEAD snapshot
* B2: a second fresh snapshot plus the identical nine-file overlay

All four must use byte-identical:

* package.json;
* generated temporary lockfile;
* dependency tree;
* Node/npm versions;
* environment variables;
* test commands and configuration.

Run in this order:

1. A1
2. B1
3. B2
4. A2

Do not reuse generated compilation/test output between runs.

Broader-suite comparison

Recover and report the exact command that produced the previously reported nine broader pure-unit failures.

Run that identical command in all four snapshots. Do not replace it with a narrower grep.

For every run, record:

* command;
* exit code;
* passing/failing/pending counts;
* full failing test titles;
* error class;
* normalized assertion/error message;
* first meaningful repository stack frame.

Normalize only temporary directory prefixes, timestamps, and durations. Do not normalize meaningful errors, assertion values, test titles, or stack frames.

Classify each failure:

BASELINE_FAILURE

The same full test title, error class, materially equivalent message, and meaningful stack origin occur in A1, A2, B1, and B2.

OVERLAY_FIXED_BASELINE_FAILURE

The failure occurs consistently in A1 and A2 but not in B1 or B2.

OVERLAY_REGRESSION

Any of the following:

* failure occurs in B1/B2 but not A1/A2;
* failure count is equal but identities or signatures differ;
* A compiles but B does not;
* an A0R focused gate fails in either B run.

FLAKY_OR_INCONCLUSIVE

A1 differs from A2, B1 differs from B2, or environment/dependency identity cannot be proven.

Do not call a failure “unrelated” unless it qualifies executably as BASELINE_FAILURE.

A0R coverage proof

In both B snapshots, run and report the focused suites again.

Provide a table mapping each requirement below to:

* exact test file;
* full test title;
* executable assertion;
* B1 result;
* B2 result.

Required coverage:

1. Explicit selected-workspace provenance.
2. Ambiguous multi-root fail-closed behavior.
3. No process.cwd() or ambient workspace fallback.
4. Empty-repository initialization intent.
5. STTM SHA-256 and selected-root containment.
6. External and stale STTM rejection.
7. Extension-source/installation-root rejection as a Consumer target.
8. Windows drive and mixed-separator containment.
9. UNC escape handling.
10. Symlink/junction escape handling or a precise platform limitation plus equivalent resolved-path assertion.
11. Candidate/job-discovery absence represented as explicitly unresolved.
12. Collision/ownership absence represented as explicitly unresolved.
13. Direct /create collects evidence before AgentActionExecutor.
14. Executor receives the same immutable evidence.
15. Incomplete evidence blocks preview.
16. Exact unresolved codes reach ResponseComposer.
17. Executable spies prove zero calls to:
    * RepoWriter
    * NewArtifactWriter
    * writeArtifacts
    * resolveWorkspacePath
    * preview writer/validator
    * filesystem write APIs
18. /workflow create remains on its separate unchanged workflow-manager path.
19. applyEligible === false throughout Phase A0.

Source-text searches are supplementary and cannot replace executable assertions.

If any required item has no executable test, do not add one during this validation task. Report:

LOCAL_PHASE_A0R_AB_COVERAGE_GAP

Additional B gates

For both B1 and B2, require:

* TypeScript test compilation succeeds;
* focused suites have zero failures;
* registered A0 runner has zero failures;
* git diff --check for the nine-file overlay passes;
* no writer or preview call occurs with incomplete evidence.

Acceptance

A/B validation passes only if:

* A1 and A2 are consistent;
* B1 and B2 are consistent;
* B introduces no new or changed broader-suite failure;
* all nine previously reported failures are proven baseline failures or are fixed by B;
* all 19 A0 coverage requirements map to passing executable assertions;
* all focused B tests have zero failures;
* no real state changes.

If the same nine failures exist in A and B with materially identical signatures, report them as pre-existing baseline failures—not as a fully green repository.

Cleanup and immutability

After evidence collection:

* delete only the exact temporary root;
* verify deletion;
* compare real git status --porcelain byte-for-byte before and after;
* verify all nine pending A0R hashes are unchanged;
* verify all protected dirty hashes are unchanged;
* verify candidate VSIX hash is unchanged;
* verify Consumer workspaces and control-plane paths are unchanged.

Required final report

Provide:

1. Identity and overlay evidence.
2. Exact nine paths and hashes.
3. Dependency seed and reproducibility disclosure.
4. A1/B1/B2/A2 command matrix.
5. Failure-equivalence table.
6. Adjudication of all nine broader failures.
7. Nineteen-item executable coverage matrix.
8. Focused B1/B2 results.
9. Any flakiness or platform limitation.
10. Before/after immutability evidence.
11. Explicit confirmation:
    * Keep/Undo untouched;
    * A1 not started;
    * no edits performed;
    * no Git/PR/CI/package/VSIX/install/external action occurred.

End with exactly one token:

LOCAL_PHASE_A0R_AB_BASELINE_CONFIRMED
LOCAL_PHASE_A0R_AB_OVERLAY_REGRESSION
LOCAL_PHASE_A0R_AB_COVERAGE_GAP
LOCAL_PHASE_A0R_AB_INCONCLUSIVE
LOCAL_PHASE_A0R_AB_BLOCKED
