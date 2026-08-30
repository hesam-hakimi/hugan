TASK: HF1_V2_RECONCILE_AND_F5_PUBLIC_STTM_OUTPUT

The focused public-STTM structured-output fix is complete, but the new
engineering process was adopted while the previous task was running.

Current status:
- focused fix/tests passed;
- five repository paths are changed;
- package.json was prematurely bumped to 0.3.148;
- a temporary VSIX was built outside the repository;
- nothing was committed, installed, pushed, merged, or Runtime-QA tested;
- full suite reported 2311 passing / 5 pending / 3 failing.

Do not add another product feature.
Do not commit, push, install, package, release, or invoke etl-release-verifier.

1. Mark the temporary 0.3.148 VSIX as DEV_ONLY_NON_CANONICAL.
   Never use it for installation, QA, or release.

2. Revert only package.json version from 0.3.148 to 0.3.147.
   Do not build another VSIX.

3. Preserve and review these four functional/test changes:
   - src/tools/index.ts
   - src/test/suite/sttmPublicToolResultEnvelope.test.ts
   - src/test/helpers/registerVscodeStub.ts
   - src/test/testPatterns.ts

4. Prove that the stub/helper changes do not weaken existing assertions or
   merely make the production fix self-confirming.

5. In a separate clean 0.3.147 baseline worktree, run the same canonical full
   suite once and capture the exact fully qualified identities of all failures
   and pending tests.

6. Compare baseline and candidate results:
   - map only exact approved identities to F1 and F3;
   - F1 ticket: ETL-TEST-DEBT-001
   - F3 ticket: ETL-TEST-DEBT-002
   - owner: ETL Repository Maintainer
   - expiry: 2026-09-13
   - do not create or broaden quarantine in this product branch;
   - any third/unregistered failure remains a blocker.

7. Run the configured Extension Development Host/F5 against the isolated
   consumer QA workspace.

8. Through the real contributed LM-tool/public-result path, verify with one
   valid fixture and one negative/malformed fixture:
   - the structured part has MIME application/json;
   - the consumer extracts an object, not an opaque string;
   - Markdown and structured diagnostics are both present;
   - diagnostic codes match;
   - affected-row identities and mapping order match;
   - missing/null/primitive/malformed data fails closed;
   - Preview creates or modifies no files or settings;
   - no job, approval, write, deployment, or source-repository access occurs.

9. If VS Code UI interaction cannot be executed by the Agent, provide the exact
   minimal F5 steps and expected observations, then wait. Do not claim PASS.

Stop after reporting:

FOCUSED_FIX_PRESERVED: YES|NO
TEMP_VSIX_CANONICAL: NO
PACKAGE_VERSION_RESTORED_TO_0_3_147: YES|NO
BASELINE_FAILURE_IDENTITIES_CAPTURED: YES|NO
F1_F3_EXACTLY_MATCHED: YES|NO
UNREGISTERED_FAILURES: NONE|<list>
REAL_HOST_F5_EXECUTED: YES|NO
PUBLIC_STRUCTURED_OBJECT_VISIBLE: YES|NO
MARKDOWN_STRUCTURED_PARITY: PASS|FAIL|NOT_TESTED
PREVIEW_WORKSPACE_MUTATION: NO|YES|NOT_TESTED
SOURCE_REPOSITORY_ACCESSED: NO|YES|NOT_TESTED

Success:
PUBLIC_STTM_OUTPUT_DEVELOPMENT_RESULT:
PASS_READY_FOR_TASK_PR_GATE

Otherwise:
PUBLIC_STTM_OUTPUT_DEVELOPMENT_RESULT:
BLOCKED_<EXACT_REASON>
