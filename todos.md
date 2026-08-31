Create one local commit from the currently staged Repair 13 files.

Before committing:

1. Confirm the staged set still contains exactly these four paths:

* src/tools/index.ts
* src/test/helpers/registerVscodeStub.ts
* src/test/testPatterns.ts
* src/test/suite/sttmPublicToolResultEnvelope.test.ts

2. Run:

git diff –cached –check

If it reports a real whitespace error, stop and report it. A line-ending conversion warning by itself is non-blocking; do not rewrite any file to address it.

3. If the check passes, create exactly one local commit with this message:

fix: return structured STTM public tool results

4. After the commit, report:

* New commit SHA
* Commit subject
* Committed file names and statuses
* Output of git status --short

Expected final status: clean.

Restrictions:

* Do not edit any file.
* Do not change the package version.
* Do not run tests, compilation, or packaging.
* Do not push, tag, amend, reset, clean, delete, or stash.
* Stop immediately after reporting the local commit verification.
