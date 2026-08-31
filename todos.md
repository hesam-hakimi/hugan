Perform a strictly read-only GitHub branch and commit provenance investigation for:

TD-Universe/agentic_etl

Known commits:

Baseline recovery commit:

ca51faf652d85d5b44c1e4dd97baa704f634ec1c

Repair 13 commit:

64706129e0d1054ea615e150b28dd623fb3c629e

Current integration-base candidate:

feature/v3-agentic-redesign

Use authenticated GitHub server data, not incomplete local origin/* references.

Investigate:

1. For the baseline recovery commit, report:

* Full commit subject
* Parent SHA
* Associated open, closed, or merged pull requests
* Every remote branch containing this commit
* Every remote branch or tag pointing directly to it

2. For each plausible target branch found on GitHub, run a server-side comparison against the Repair 13 branch.

A valid Repair 13 base must produce exactly:

* One new commit
* Four changed files
* Only these paths:
    * src/tools/index.ts
    * src/test/helpers/registerVscodeStub.ts
    * src/test/testPatterns.ts
    * src/test/suite/sttmPublicToolResultEnvelope.test.ts

3. Classify the result as exactly one of:

* Baseline recovery is already merged into an integration branch.
* Baseline recovery belongs to an existing open pull request and Repair 13 can use its head branch as a stacked base.
* Baseline recovery has no approved pull request or integration branch and must be reviewed first.
* Another valid base exists; provide its exact branch and comparison result.

4. Recommend the narrowest safe integration path, but do not perform it.

Restrictions:

* Do not create any branch or pull request.
* Do not push anything.
* Do not edit files or create commits.
* Do not change the local fetch refspec.
* Do not fetch, merge, rebase, cherry-pick, reset, clean, tag, or force push.
* Do not change the package version.
* Stop after reporting the verified GitHub provenance and recommendation.
