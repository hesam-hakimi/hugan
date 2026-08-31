The first real-host F5 run reached the exact BP1 anchor at
src/extension.ts:144, proving activation and breakpoint binding.

However, the runbook bootstrap failed twice:

globalThis.__etlQA =
  require(process.env.TEMP + '\\qa-harness.js')(vscode, require)

Both at BP1 and after exactly one F10 step, the Debug Console returned:

ReferenceError: require is not defined

The Debug Console therefore does not expose lexical require in this real
Extension Host frame. The current F5 run has been stopped and must not be
reported as Runtime PASS.

Additionally, activation emitted repeated warnings:

Trying to add a disposable to a DisposableStore that has already been
disposed of. The added object will be leaked!

TASK: REPAIR_EXTERNAL_F5_BOOTSTRAP_AND_RECONCILE_ACTIVATION_WARNINGS

Constraints:

- Do not modify any repository file.
- Preserve package version 0.3.147 and exactly the existing four-file diff.
- Do not commit, compile, test product code, package, install, build VSIX,
  write to the QA workspace, run jobs, deploy, or execute another F5 session.
- Modify only the external %TEMP% harness, runbook, self-test, and manifest.
- Do not use an ad-hoc command that depends on lexical `require`.
- Do not weaken any existing harness checks.

1. Record the failed run as:
   BP1_ACTIVATION=PASS
   HARNESS_LOAD=FAIL_REQUIRE_UNAVAILABLE
   REAL_HOST_F5_EXECUTED=YES_INCOMPLETE
   STRUCTURED_OUTPUT_RUNTIME_GATE=BLOCKED_HARNESS_BOOTSTRAP

2. Replace the Debug Console bootstrap with a deterministic loader that works
   when lexical `require` is absent. It must obtain a module loader through a
   capability-checked supported runtime path, bind it to the harness file, and
   pass that same loader into qa-harness.js. If the required runtime capability
   is unavailable, fail closed with an explicit error.

3. Add a self-test that explicitly executes the bootstrap with lexical
   `require` unavailable. The previous 310/310 result was insufficient because
   it did not model the actual Debug Console environment.

4. Ensure bootstrap can be executed only once per fresh Extension Host and
   refuses stale globalThis.__etlQA state or a reused RUN_ID.

5. Reconcile the DisposableStore warnings read-only:
   - identify whether they came from product activation, host shutdown/reuse,
     or harness activity;
   - provide exact timestamps/call-path evidence;
   - do not classify them as harmless without evidence;
   - require a clean-host rerun to determine reproducibility.

6. Regenerate and self-test the external assets, then produce a new manifest
   and SHA-256. The previous manifest hash is stale and must not be reused.

7. Provide the exact corrected single-line Debug Console bootstrap plus fresh
   P0-P4 preflight instructions. Do not execute F5.

Required report:

REPOSITORY_DIFF_UNCHANGED: YES|NO
PACKAGE_VERSION: 0.3.147|OTHER
FAILED_RUN_RECORDED: YES|NO
LEXICAL_REQUIRE_DEPENDENCY_REMOVED: YES|NO
REQUIRE_ABSENT_SELF_TEST: PASS|FAIL
HARNESS_SELFTEST: PASS (<count>/<count>)|FAIL
STALE_GLOBAL_OR_RUN_ID_FAILS_CLOSED: YES|NO
DISPOSABLESTORE_WARNING_CLASSIFICATION: <evidence>|UNRESOLVED
NEW_MANIFEST_SHA256: <64 lowercase hex>
REAL_HOST_F5_EXECUTED_AGAIN: NO
NEXT_OWNER_ACTION: VERIFY_NEW_MANIFEST_AND_REPEAT_PREFLIGHT
