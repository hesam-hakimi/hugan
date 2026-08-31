Establish SHA-tied unit-test evidence for the inherited workspace-write hotfix.

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required HEAD:

64706129e0d1054ea615e150b28dd623fb3c629e

Preflight:

1. Confirm the current HEAD matches exactly.
2. Confirm `git status --short` is empty.
3. If either check fails, stop without running tests.

Run exactly once:

npm run test:unit

Do not add filters, retries, repairs, or additional commands that execute tests.

Capture and report:

* Exact command
* Starting and ending HEAD
* Exit code
* Elapsed time
* Total passing, pending, skipped, and failing tests
* Full names and error messages of every failure
* Whether each of these write-related suites was executed:

  * onboardingWriteApproval.test.ts
  * repoWriterWorkspaceSelection.test.ts
  * workspaceInputContainment.test.ts
  * hf1OracleFreshConsumer.test.ts
  * hf1v2GoldenPathPrePackage.test.ts
  * physicalWriteContainment.test.ts
* Confirm that `writeFlow.test.ts` was not included by this command.
* Final output of `git status --short`

Important interpretation:

* Passing tests do not close the already identified collision, atomic-apply, or managed-ownership gaps.
* This run establishes the current baseline only.
* If the command fails, report the evidence and stop. Do not diagnose or fix it in this turn.

Restrictions:

* Do not run `npm install`.
* Do not edit or format files.
* Do not run the full suite, F5, packaging, or a harness.
* Do not create commits, branches, tags, packages, or pull requests.
* Do not push, fetch, merge, rebase, reset, clean, or change the package version.
* Run the command only once and stop after reporting.
