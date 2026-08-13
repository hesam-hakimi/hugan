Continue development of the existing local .kmai-dev-agent Codex-like engineering agent.

This is NOT a redesign and NOT a request to add unrelated features.

The existing implementation already includes, at minimum:

* local .kmai-dev-agent control plane;
* repository indexing and bounded repository search/read tools;
* planner / implementer / reviewer separation;
* autonomy modes such as probe / plan / audit / implement / verify;
* approval and patch-safety controls;
* model profiles and role-to-model mapping;
* reuse of the existing KMAI authentication/model-access mechanism;
* GPT-5.5 selectable model profile;
* actual-model evidence/reporting behavior;
* automated test / repair concepts;
* clean-worktree safety boundaries.

The last validation did NOT fully pass.

Known blocker:

/bin/bash terminated with exit code 127.

The final GPT-5.5 configuration / end-to-end diagnostic therefore ended in FAIL.

Our immediate goal is:

Diagnose and fix the runtime failure, then obtain a clean, repeatable, evidence-backed end-to-end PASS for the existing KMAI Dev Agent.

Do not begin a new feature milestone until this is complete.

⸻

1. Read-only preflight

Before modifying anything:

1. Locate .kmai-dev-agent.
2. Read its README, configuration, model-policy, UI, orchestration, testing, and validation files.
3. Identify the most recent GPT-5.5 validation/probe scripts and evidence.
4. Inspect the command or process that produced /bin/bash exit code 127.
5. Determine the exact failing command.

Report:

* repository root;
* current branch;
* worktree status;
* relevant .kmai-dev-agent files;
* exact failing command;
* exact meaning of exit 127 in this specific execution;
* whether the failure comes from:
    * missing executable;
    * incorrect PATH;
    * shell assumption;
    * incorrect command construction;
    * working-directory issue;
    * quoting/escaping;
    * environment activation;
    * or another evidenced root cause.

Do not guess.

⸻

2. Preserve repository safety

The KMAI Dev Agent must remain a local engineering control plane.

Do not:

* auto-commit;
* auto-push;
* merge;
* deploy;
* alter remote branches;
* modify unrelated application code;
* weaken approval gates;
* weaken path-containment rules;
* expose credentials or tokens;
* introduce a new authentication mechanism if the existing KMAI mechanism works.

Prefer changes only inside .kmai-dev-agent/ unless there is direct evidence that another local configuration file must change.

If the host repository contains unrelated dirty files, leave them untouched.

⸻

3. Fix the runtime failure minimally

Reproduce the exit-127 failure first.

Then implement the smallest robust fix.

The fix must work in the actual target environment and must not simply hide or ignore command failures.

Requirements:

* no hardcoded developer-specific absolute paths;
* no assumption that an executable exists without probing it;
* clear error if a required dependency is genuinely unavailable;
* safe subprocess invocation;
* correct working directory;
* correct environment propagation;
* useful stdout/stderr capture;
* timeout handling;
* deterministic exit-code handling.

If the tool supports more than one shell/environment, use explicit capability detection rather than implicit assumptions.

⸻

4. Validate GPT-5.5 model-profile behavior

Verify the complete path:

UI / CLI selection
→ model profile
→ role-to-model policy
→ authentication reuse
→ actual provider/model invocation
→ observed-model evidence
→ final report

Specifically verify:

* GPT-5.5 can be selected through the intended interface;
* the selection reaches the actual runtime;
* Planner receives the intended model policy;
* Implementer receives the intended model policy;
* Reviewer receives the intended model policy;
* agents cannot silently override centralized model policy;
* authentication uses the already-approved/reused mechanism;
* no API key or credential is written into source or logs;
* requested model and actual observed model are distinguishable;
* failure to observe the actual model is reported explicitly rather than fabricated.

Do not consider UI selection alone proof that GPT-5.5 was actually used.

⸻

5. Run all existing self-tests

Run the complete existing .kmai-dev-agent self-test suite.

Do not delete, skip, loosen, or rewrite tests merely to obtain a green result.

Verify especially:

* repository search;
* bounded file reads;
* symbol/text navigation;
* path containment;
* forbidden-path handling;
* dirty-worktree protection;
* planning;
* implementation;
* reviewer independence;
* patch safety;
* approval gates;
* test execution;
* repair loop;
* checkpoint / rollback behavior;
* model-policy selection;
* authentication reuse;
* actual-model evidence;
* subprocess/runtime behavior.

Return exact:

* test command;
* passed count;
* failed count;
* skipped count.

⸻

6. Fake-repository end-to-end test

Create or reuse the existing disposable fake repository test.

Give the agent a small realistic engineering request requiring it to:

1. inspect repository context;
2. search for the relevant code;
3. create a plan;
4. implement a bounded change;
5. run tests;
6. independently review the implementation;
7. repair an issue if verification finds one;
8. rerun validation;
9. produce a final evidence report.

Verify that the workflow follows:

Task
→ Repository Discovery
→ Plan
→ Implementation
→ Tests
→ Independent Review
→ Repair if required
→ Final Verification
→ Final Report

The test must prove that the agent does not modify files outside the allowed workspace.

⸻

7. Real-worktree smoke test

After the disposable E2E test passes, perform one bounded smoke test against a clean isolated worktree of the real repository.

Use a harmless task that exercises discovery and planning without making broad product changes.

The smoke test must demonstrate:

* correct repository classification;
* search and bounded reads;
* planning;
* safe patch generation if implementation mode is exercised;
* test invocation;
* reviewer pass;
* no modification of unrelated files;
* no commit;
* no push;
* no merge;
* no deployment.

If a clean isolated worktree cannot be established safely, stop rather than using a dirty checkout.

⸻

8. Failure and repair loop

If any validation step fails:

1. capture the exact failure;
2. classify whether it is:
    * environment;
    * orchestration;
    * model policy;
    * authentication;
    * search/index;
    * implementation;
    * review;
    * test harness;
    * subprocess;
    * safety control;
3. make the smallest justified repair;
4. rerun the failed test;
5. rerun the relevant regression suite.

Continue only within a bounded repair loop.

Do not declare PASS while a required gate is failing.

⸻

9. Final hygiene verification

Before concluding, verify:

* host repository unrelated files are untouched;
* .kmai-dev-agent contains no credentials;
* no tokens are present in logs or evidence;
* no temporary test artifact escaped its allowed location;
* no remote branch changed;
* no commit/push/merge/deployment occurred;
* git diff is fully explained;
* all required tests are green.

⸻

10. Produce a final evidence report

Create a local Markdown report under the .kmai-dev-agent evidence/report area following its existing convention.

The report must contain:

1. Overall verdict: PASS or FAIL
2. Original exit-127 root cause
3. Exact fix
4. Files changed
5. GPT-5.5 selection and actual-model evidence
6. Authentication verification
7. Self-test results
8. Fake-repository E2E result
9. Real-worktree smoke-test result
10. Safety-boundary verification
11. Remaining limitations
12. Recommended next engineering milestone
13. Confirmation that no commit, push, merge, or deployment occurred

The overall result may be PASS only if:

* the exit-127 issue is resolved;
* all required self-tests pass;
* GPT-5.5 runtime behavior is evidenced;
* fake-repository E2E passes;
* real-worktree smoke test passes;
* safety boundaries remain intact.

At the end, stop.

Do NOT begin the next feature milestone.

Return the final report path and a concise summary of the evidence.
