TASK: HF1_V2_FINAL_EXTERNAL_F5_RUNBOOK_CORRECTION

Accept the current BLOCKED_NOT_EXECUTED result.

Do not run F5 yet. The architecture and acceptance scope are now correct, but
the external runbook still contains execution and false-PASS risks.

HARD CONSTRAINTS

- Keep the existing four product paths unchanged.
- Keep package version 0.3.147.
- Do not edit product source/tests/package/governance.
- Do not commit, push, package, install, build VSIX, bump version, run jobs,
  approve writes, or deploy.
- Modify only external %TEMP% harness/runbook assets.
- F1 and F3 remain the only approved quarantines.
- Failure 2 remains an open unregistered blocker.
- Do not execute F5 or claim Runtime PASS in this task.

1. FIX PREFLIGHT

Add P0:

- The owner must open the VS Code Problems panel and classify all currently
  visible 15 problems.
- Any repository TypeScript, JavaScript, JSON, launch, source-map, compile, or
  test error blocks F5.
- Only explicitly identified unrelated Markdown/spelling/editor warnings may be
  recorded as non-blocking.
- Do not assume the count is cosmetic.

Correct P1:

- If compiled output is absent, stale, mismatched, or its source maps do not
  match, STOP_STALE_COMPILED_OUTPUT.
- Do not run npm run compile during this frozen acceptance run.
- Compilation and re-baselining require a separate preparation task.
- Pin SHA-256 for the exact compiled extension JS, out/tools/index.js, and
  required source maps.

Strengthen P2 before and after:

- full HEAD;
- version;
- exact path/mode list;
- canonical tracked-diff hash;
- all four per-file hashes, including the untracked test;
- compiled JS and source-map hashes.

2. REVIEW AND PIN ALL EXTERNAL ASSETS

Before the owner trusts the workspace or executes require(...), record SHA-256
for:

- etl-f5-harness.code-workspace;
- qa-harness.js;
- repair13-harness-selftest.js;
- qa-inventory.ps1;
- etl-f5-runbook.md;
- every Markdown fixture;
- synthetic_workbook.xlsx.

Verify mechanically:

- no preLaunchTask;
- no network access;
- no package/install/version operation;
- no deletion;
- no unrestricted shell execution;
- any git subprocess is allowlisted to read-only identity commands;
- writes are limited to the documented %TEMP% case/evidence directories;
- no repository write occurs.

Repeat these hashes after the run.

3. FIX LAZY ACTIVATION

F5 alone must not be assumed to hit BP1.

The numbered flow must be:

- set all breakpoints;
- press F5 and wait for the Extension Development Host;
- in the child host perform one benign, read-only activation action such as
  `@etl hello`;
- only then expect BP1;
- after BP1 loads the harness, establish/reset the evidence baseline so the
  activation action is not mixed with the acceptance cases.

If activation does not reach the exact BP1 anchor, stop.

4. REQUIRE VERIFIED BREAKPOINTS

After the debug session starts:

- BP1, BP2, and BP3 must all be solid/bound, not hollow or relocated;
- compiled and TypeScript anchors must match;
- required locals must be in scope;
- any conditional-expression error is a blocker.

BP2 must use exact request correlation:

  globalThis.__etlQA &&
  globalThis.__etlQA.inject(title, options.input, response)

Do not use inject(title, response).

If options.input is unavailable at BP2, stop and redesign the external
observation; do not fall back to a global/FIFO assumption.

Before Seam B, explicitly disable BP2 so Copilot Agent’s natural workbook
invocation can never receive fault injection.

5. REPLACE THE FRAGILE ASYNC DEBUG-CONSOLE FLOW

Do not rely on:

  await __etlQA.run()

being evaluated after Continue, and do not await it while the Extension Host is
paused.

Implement an external-harness scheduled-run mechanism:

- while safely paused at BP1, load the reviewed/hash-pinned harness;
- schedule the run to start only after Continue;
- return a RUN_ID immediately;
- execute cases only after activation completes;
- persist RUNNING, COMPLETED, or FAILED status;
- atomically write a terminal completion/evidence file under %TEMP%;
- include rejection/timeout details;
- never treat a printed Promise or missing output as completion.

The operator must judge only the terminal COMPLETED evidence artifact.

6. FIX THE POSITIVE/NEGATIVE ASSERTION CONTRADICTION

Split assertions mechanically:

Positive cases A1–A3:

- TextPart count >= 1;
- DataPart count == 1;
- MIME application/json;
- decoded non-null, non-array object;
- expected schema and parity.

Injected invalid-output cases N1–N4:

- TextPart count >= 1;
- DataPart count == 0;
- exact fail-closed code/message;
- evidenceClass: DIAGNOSTIC_FAULT_INJECTION.

The evidence checklist must never require DataPart for N1–N4.

7. ALIGN THE NEGATIVE CLASSES

Name the cases explicitly:

- N1: missing/undefined structured payload;
- N2: null structured payload;
- N3: primitive structured payload;
- N4: malformed non-object structured shape, currently an array if that is the
  intended malformed class.

State explicitly that malformed.md is an input/document parsing case returning
an actionable diagnostic. It is not malformed structured output and does not
replace N4.

Conditional-breakpoint injection remains diagnostic corroboration only. It does
not create release PASS and does not replace natural unit regression tests.

8. STRENGTHEN THE XLSX ORACLE AND PROVENANCE

For the direct XLSX case and Copilot Agent case:

- pin the workbook SHA-256;
- include unique expected mapping identities and values in the workbook;
- require those values in both Markdown and structured JSON;
- record the canonical resolved parser-entry workbook path.

Do not overclaim provenance.

Unless the actual parser input/I/O path is observed sufficiently, report:

  QA_WORKBOOK_PROVENANCE: INCONCLUSIVE
  REPO_LOCAL_SAMPLE_STTM_READ: NOT_PROVEN

An empty tracer hit list means only:

  NONE_OBSERVED_IN_INSTRUMENTED_SCOPE

It must not be converted to a global NO.

9. SCOPE MUTATION EVIDENCE

Define the exact inventory scope:

- consumer QA workspace files and directories;
- workspace settings;
- repository identity/diff;
- any other paths actually observed.

Separate harness-created case/evidence files from product mutations.

Report:

  NONE_OBSERVED_IN_MEASURED_SCOPE

unless every claimed scope was actually measured. Never use a global
NONE_DETECTED for unmeasured locations.

10. MAKE SEAM B DETERMINISTIC AND LIMITED

- Disable BP2 before Seam B.
- Auto Approve and Bypass must be off.
- Use the VS Code tool picker/autocomplete and confirm that
  `#etl_interpret_sttm` becomes a real tool token/chip before sending.
- Do not rely on an unverified qualified fallback string.
- Any observed Seam B result proves only:
  COPILOT_AGENT_TOOL_INVOCATION.
- It does not prove Copilot consumed or used the returned DataPart.

11. DEFINE A MECHANICAL PASS TRUTH TABLE

DIRECT_LM_TOOL_PUBLIC_CONTRACT may be PASS_ON_REAL_HOST only when all required
positive public-result fields pass.

STRUCTURED_OUTPUT_RUNTIME_GATE may be PASS only when every required runtime
field is conclusive and passing.

It must not be PASS if any required field is:

- PARTIAL;
- NOT_TESTED;
- NOT_MEASURED;
- INCONCLUSIVE;
- unresolved;
- wrong MIME;
- changed repository identity;
- missing direct XLSX evidence.

Diagnostic fault injection must not independently contribute to release PASS.
A diagnostic failure is still a blocker.

OVERALL_TASK_PR_GATE must remain BLOCKED_FAILURE_2 regardless of the F5 result.

12. REVALIDATE WITHOUT RUNNING F5

Update the external self-test to cover every correction above, including:

- positive-versus-negative DataPart counts;
- exact input-to-response correlation;
- concurrent host invocation isolation;
- scheduled-run completion and rejection;
- truth-table impossibility of false PASS;
- asset hash verification;
- no preLaunchTask;
- provenance and mutation qualification.

Stop after reporting:

EXTERNAL_ASSET_SAFETY_REVIEW: PASS|FAIL
EXTERNAL_ASSET_HASHES_PINNED: YES|NO
HARNESS_SELFTEST: PASS|FAIL
PROBLEMS_PANEL_CLASSIFICATION_REQUIRED: YES
COMPILED_OUTPUT_PINNED: YES|NO
LAZY_ACTIVATION_STEP_PRESENT: YES|NO
REQUEST_RESPONSE_CORRELATION: EXACT|UNRESOLVED
ASYNC_COMPLETION_MECHANISM: SCHEDULED_ATOMIC|UNSAFE
POSITIVE_NEGATIVE_ASSERTIONS_SPLIT: YES|NO
PROVENANCE_CLAIMS_QUALIFIED: YES|NO
MUTATION_SCOPE_DEFINED: YES|NO
PASS_TRUTH_TABLE_DEFINED: YES|NO
REAL_HOST_F5_EXECUTED: NO
STRUCTURED_OUTPUT_RUNTIME_GATE: BLOCKED_NOT_EXECUTED
OVERALL_TASK_PR_GATE: BLOCKED_FAILURE_2
