APPLY_LOCAL_HOTFIX_HF1

AUTHORIZATION DECISIONS AND EXECUTION CONDITIONS

1. Bypass decision

Close all three identified production write bypasses.

Do not use “route 1 only”.

After this hotfix, every production write route, including:

* EtlActionToolService.writeToWorkspace
* WriteCoordinator.writeArtifactsWithSummary
* DeployCoordinator local-write step 1

must follow:

validation → immutable preview/path manifest → explicit approval → one-time authorized write

The resulting two-step Preview → Confirm behavior for @etl /write and the local-write portion of @etl /deploy is explicitly authorized.

2. Frozen source scope

Implement only the frozen inventory:

* exactly 5 new files
* exactly 21 modified files
* exactly 26 files total

Do not modify any unlisted file.

If compilation or implementation exposes a required call site outside the frozen inventory, stop immediately without editing that file and report:

LOCAL_HOTFIX_HF1_SCOPE_AMENDMENT_REQUIRED

3. Start-state protection

Before editing, perform a final read-only Git status check.

The copied node_modules and generated ignored output are allowed, but there must be no tracked or non-ignored source change in the HF1 clone.

If source drift exists before implementation, stop with:

LOCAL_HOTFIX_HF1_START_STATE_DIRTY

Do not modify:

* the original etl_framework_extension worktree
* etl-framework-adb
* any consumer repository
* any S-A/S-B file
* .github/**
* resources/prompts/**
* docs/eval/**
* .vscodeignore
* AGENT.md or AGENTS.md files
* Phase-H baseline reports
* package-lock.json
* any file associated only with the six known baseline failures

4. Known pre-existing baseline

Before HF1 implementation, the clean committed HEAD produced:

* 1791 passing
* 5 pending
* 6 failing

The six pre-existing failures are:

1. EvalGating — passes against the committed Phase H baseline report
2. EvalGating — allows deterministic v3 baseline reports without prompt telemetry
3. Package asset manifest — excludes dev logs, eval outputs, generated packages, and test artifacts from VSIX candidate
4. Copilot workflow customization — maintainer delivery prompt references real repo-local agents
5. Copilot workflow customization — repo customization assets use valid frontmatter and agent file naming
6. Copilot workflow customization — source tree uses standard AGENTS.md guidance instead of module AGENT.md files

Do not repair, suppress, skip, rebaseline, regenerate, or otherwise alter these failures in HF1.

After implementation, the full unit suite may still contain these exact six failures. No seventh failure and no changed failure identity is acceptable.

5. Oracle trust authority

Executable or structured framework behavior is authoritative.

Documentation may be used only as corroborating evidence; documentation text alone must never make Oracle delivery validation pass.

The resolver must verify the executable dataframe_writer implementation and its relevant database-delivery option semantics. Missing executable semantics must fail closed with:

ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING

The packaged extension reference remains guidance-only and can never satisfy trusted framework resolution.

6. Authorization-token security

WriteAuthorization must be checked at runtime as well as at compile time.

A TypeScript cast, structurally similar plain object, stale authorization, already-consumed authorization, authorization for another workspace, changed framework fingerprint, changed artifact path, changed artifact bytes, changed target type, or changed targetDecision must all be rejected.

Add coverage inside the already-authorized test files. Do not add another file.

7. Dependency and command boundary

The human-operated terminal has restored local node_modules without downloading or installing anything.

Do not run:

* npm install
* npm ci
* dependency copy/link commands
* downloads
* network commands
* VS Code archive download
* VSIX packaging/install/deploy
* Git mutation commands

You may use the existing local toolchain to attempt compile, lint, and tests.

If this Chat still cannot launch native Node processes, do not treat that as an implementation failure and do not fabricate results. Report the exact commands for human execution.

8. Required validation interpretation

Required green checks:

* npm run compile
* npm run lint
* focused HF1 unit tests
* every new HF1 test

Required full-suite comparison:

* the same six named baseline failures may remain
* no new failure
* no missing or renamed baseline failure caused by HF1
* existing unrelated passing tests must not regress

Real-consumer end-to-end verification remains:

NOT EXECUTED — SAMPLE UNAVAILABLE

Synthetic fixtures must not be described as production-consumer validation.

9. Consumer artifact contract

The consumer artifact set, paths, order, and bytes must remain unchanged.

Framework identity and fingerprint belong only to internal validation/approval state. They must not:

* create a thirteenth artifact
* alter generated consumer bytes
* alter a renderer, template, or path builder
* write a marker
* create job_conf/ or env_conf/ before approved write

10. Completion report

Report:

* exact files created and modified
* diff statistics
* mapping of each defect to implementation and tests
* all attempted commands and exit codes
* focused-test results
* full-suite comparison against the six-failure baseline
* confirmation that all no-touch paths remained unchanged
* confirmation that no package, install, deployment, Git mutation, or consumer write occurred

Finish with exactly one applicable marker:

LOCAL_HOTFIX_HF1_COMPLETE

only if compile, lint, and focused HF1 tests were actually executed and passed, with no new full-suite failure;

or:

LOCAL_HOTFIX_HF1_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

if implementation completed but this Chat could not execute the native validation commands;

or:

LOCAL_HOTFIX_HF1_BLOCKED

if implementation could not be completed within the frozen scope.
