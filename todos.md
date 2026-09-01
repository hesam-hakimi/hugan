Phase H — One-time Eval Golden refresh after Repair A and Repair B

Execute this task in the normal writable VS Code source-repository workspace:

Repository:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required branch:
fix/workspace-write-completion-0.3.148

Required starting HEAD — committed Repair B:
6107aa0b0e0d5bb26a998db62ee26712a728139a

Required HEAD subject:
fix: align artifact validation with canonical contract

Required sole parent — committed Repair A:
46f6930e8474f6ac07d157cc85d21687a08869f3

Speak with the user in Persian, but keep commands, paths, test identities, commit messages, technical evidence, and final markers in English.

This task performs exactly one deterministic Phase H Eval Golden refresh after Repair A and Repair B.

It is not a source repair, feature implementation, runtime QA run, fixture task, release task, or W1 change.

==================================================
0. ENVIRONMENT AND CAPABILITY GATE

Run only in the normal writable source repository.

Do not run in:

* Extension Development Host;
* F5 QA workspace;
* consumer ETL workspace;
* ETL Orchestrator chat;
* read-only agent mode.

The session must have repository-scoped Read, Write/Edit, and Terminal capabilities.

If report generation cannot write the authorized files, stop with:

PHASE_H_EVAL_GOLDEN_WRITE_BLOCKED

This PowerShell environment may inherit PATHEXT=.CPL.

Every terminal invocation using git, node, npm, npx, or cmd must set this in the same invocation:

$env:PATHEXT = ‘.COM;.EXE;.BAT;.CMD’;

Do not persist that workaround through setx, registry, profiles, VS Code settings, or repository files.

==================================================

1. STRICT PREFLIGHT
    ==================================================

Before running any generator, verify:

1. Repository root is exactly:
    C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
2. Current branch is exactly:
    fix/workspace-write-completion-0.3.148
3. HEAD is exactly:
    6107aa0b0e0d5bb26a998db62ee26712a728139a
4. HEAD subject is exactly:
    fix: align artifact validation with canonical contract
5. HEAD has exactly one parent:
    46f6930e8474f6ac07d157cc85d21687a08869f3
6. git status --short --untracked-files=all is empty.
7. No staged paths exist.
8. The topology is linear:
    Repair A → Repair B
9. Repair B contains exactly these four paths:
    * src/core/validation/DataSourcingConfigValidator.ts
    * src/tools/EtlActionToolService.ts
    * src/test/suite/dataSourcingConfigValidator.test.ts
    * src/test/suite/etlActionTools.test.ts
10. Repair A and Repair B commit objects are valid and reachable from HEAD.

If any check differs, do not repair, infer, search for a similar commit, fetch, merge, rebase, reset, checkout, stash, clean, amend, or continue.

Stop with:

PHASE_H_EVAL_GOLDEN_PREFLIGHT_BLOCKED

==================================================
2. AUTHORIZED SCOPE

The only authorized persistent modifications are the generator-produced changes to:

* docs/eval/phase_h_latest_report.json
* docs/eval/phase_h_latest_report.md

No manual content editing is authorized.

Do not modify any:

* TypeScript source;
* test source;
* contract;
* documentation outside the two Phase H reports;
* package.json;
* dependency;
* engine;
* lockfile;
* extension version;
* VSIX artifact;
* fixture;
* STTM workbook;
* job config;
* environment config;
* W1 file;
* prompt or agent file;
* EvalGating or EvalGovernance implementation;
* tracked-input patterns.

Do not weaken, bypass, suppress, or mock the Eval freshness gate.

==================================================
3. GENERATOR INSPECTION

Before executing it, inspect the existing eval:golden package script and the directly invoked repository-owned generator only far enough to confirm:

* the exact command;
* expected output paths;
* whether it reads the current committed HEAD;
* whether it is deterministic under the repository’s existing rules;
* that it does not publish, push, install, package a VSIX, call an external service, or modify production source.

Do not redesign or edit the generator.

If its declared persistent output is broader than the two authorized Phase H report files, stop and report the additional paths with:

PHASE_H_EVAL_GOLDEN_SCOPE_BLOCKED

==================================================
4. ONE-TIME GOLDEN REFRESH

Run exactly once:

npm run eval:golden

Do not rerun it merely to obtain different timestamps, formatting, ordering, or output.

If the command fails, stop and report the exact command, exit code, and first actionable error. Do not improvise a manual report.

After the command succeeds, verify that:

1. Only these files are modified:
    * docs/eval/phase_h_latest_report.json
    * docs/eval/phase_h_latest_report.md
2. The JSON is valid.
3. The Markdown and JSON describe the same refreshed Phase H baseline.
4. The report is based on current Repair B HEAD:
    6107aa0b0e0d5bb26a998db62ee26712a728139a
5. The refreshed tracked-input evidence incorporates the currently committed Repair A and Repair B source state.
6. The report does not claim that F5 QA, fixture creation, write preview, approval, confirmation, publication, or runtime write occurred.
7. No source or test file was modified.

If any unexpected path appears, stop without committing.

==================================================
5. VALIDATION

After generation, run validation in this order:

1. Validate the generated JSON syntax.
2. git diff --check
3. Run the focused EvalGating/EvalGovernance test suite that contains:
    * EvalGating > passes against the committed Phase H baseline report
    * EvalGating > allows deterministic v3 baseline reports without prompt telemetry
4. Run any directly related report-schema or deterministic-baseline tests.
5. Run the sanctioned full unit suite exactly once:
    npm run test:unit

The two previous KNOWN_EVAL_FRESHNESS_FAILURE tests must now pass.

Do not classify them as expected failures after the refresh.

==================================================
6. REMAINING EXPECTED FAILURE MANIFEST

After a successful golden refresh, only these three known baseline failures are permitted.

An exact test identity and essential signature match is required. Matching only the failure count is insufficient.

1. Test identity:

Copilot workflow customization > maintainer delivery prompt references real repo-local agents

Essential signature:

ENOENT opening:
.github/prompts/deploy-v3-agent-tool-context-gap.prompt.md

Classification:

KNOWN_BASELINE_FAILURE

Action:

Record and continue without reinvestigation or individual rerun.

2. Test identity:

Copilot workflow customization > repo customization assets use valid frontmatter and agent file naming

Essential signature:

business-context.instructions.md frontmatter declares applyTo but no name

Classification:

KNOWN_BASELINE_FAILURE

Action:

Record and continue without reinvestigation or individual rerun.

3. Test identity:

Copilot workflow customization > source tree uses standard AGENTS.md guidance instead of module AGENT.md files

Essential signature:

11 tracked src/*/AGENT.md files versus expected empty inventory

Classification:

KNOWN_BASELINE_FAILURE

Action:

Record and continue without reinvestigation or individual rerun.

Expected full-suite shape, subject to exact identity reconciliation:

* 2358 passing
* 5 pending
* 3 failing

If test totals differ only because deterministic test discovery adds or removes passing tests, report the arithmetic and continue only if:

* the only failures are the exact three manifest entries;
* both former EvalGating failures pass;
* no test disappeared unexpectedly.

Any additional failure, changed signature, Eval freshness failure, timeout, crash, or infrastructure error blocks the commit.

Do not rerun manifest-matching failures individually.

==================================================
7. GENERATED CACHE HANDLING

The sanctioned tests may dirty the tracked incremental compilation cache:

.tsbuildinfo.test

This file is not an authorized deliverable.

If and only if .tsbuildinfo.test is the sole non-report modification and its change was generated by the required test commands, restore it byte-for-byte from the pinned Repair B HEAD:

6107aa0b0e0d5bb26a998db62ee26712a728139a

The only authorized restore operation is:

git restore –source=6107aa0b0e0d5bb26a998db62ee26712a728139a – .tsbuildinfo.test

Then verify that it has zero diff.

Do not use checkout, reset, clean, stash, or broad restore commands.

Any other unexpected modified or untracked path is a blocker.

==================================================
8. PRE-COMMIT GATE

Before committing, report:

1. Branch.
2. HEAD before commit.
3. Sole parent and linear topology.
4. Exact generator command and exit code.
5. Exact changed-path inventory.
6. Diff summary.
7. JSON validation result.
8. git diff --check result.
9. Focused Eval test results.
10. Full-suite totals.
11. Proof that both former Eval freshness failures now pass.
12. Exact reconciliation of the three remaining known failures.
13. Proof that every production and test path is byte-identical to Repair B HEAD.
14. Proof that W1 files and behavior are unchanged.
15. Proof that package version remains 0.3.147.
16. Proof that dependencies, devDependencies, engines, and lockfile state are unchanged.
17. Proof that no fixture, STTM, job config, environment config, VSIX, generated build artifact, or unexpected file exists.

Commit only if:

* npm run eval:golden succeeded;
* focused Eval tests pass;
* both old Eval freshness failures are gone;
* the full suite has only the three exact manifest failures;
* only the two authorized report files remain modified;
* all protected boundaries remain unchanged.

Stage the two report paths explicitly:

* docs/eval/phase_h_latest_report.json
* docs/eval/phase_h_latest_report.md

Do not use:

git add -A

Do not use:

git add .

Create exactly one commit with subject:

test: refresh Phase H evaluation baseline

Do not amend Repair A or Repair B.

Do not push.

==================================================
9. POST-COMMIT VERIFICATION

After committing, verify:

1. The new commit has exactly one parent.
2. Its sole parent is:
    6107aa0b0e0d5bb26a998db62ee26712a728139a
3. Its subject is exactly:
    test: refresh Phase H evaluation baseline
4. It contains exactly:
    * docs/eval/phase_h_latest_report.json
    * docs/eval/phase_h_latest_report.md
5. Worktree, index, and untracked inventory are empty.
6. Repair B remains the immediate parent.
7. No source, test, W1, fixture, version, dependency, lockfile, or generated artifact was committed.
8. No push occurred.

==================================================
10. NON-GOALS

Do not:

* create the deterministic physical fixture;
* run F5 QA;
* run the ETL Orchestrator;
* render or validate a runtime STTM candidate;
* create a job or environment config;
* build, package, or install a VSIX;
* perform write preview, approval, confirmation, or write;
* call external services;
* publish or push;
* create a branch;
* modify Repair A or Repair B;
* claim end-to-end QA readiness.

The deterministic physical source/target/environment fixture remains the next separate task after this commit.

==================================================
11. FINAL RESPONSE

Return a concise evidence report containing:

* Eval refresh commit SHA;
* sole parent SHA;
* commit subject;
* exact changed paths;
* npm run eval:golden result;
* focused Eval test results;
* full-suite result;
* proof that the two freshness failures now pass;
* reconciliation of the three remaining known baseline failures;
* protected-file verification;
* final worktree state;
* explicit statement that no source code changed;
* explicit statement that no F5 QA or fixture work occurred;
* explicit statement that no push occurred.

End with exactly one marker:

PHASE_H_EVAL_GOLDEN_REFRESH_COMMITTED

or, if blocked:

PHASE_H_EVAL_GOLDEN_REFRESH_BLOCKED
