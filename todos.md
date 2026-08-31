Create a draft pull request for Repair 13 in:

TD-Universe/agentic_etl

Use GitHub server data rather than the incomplete local remote-tracking references.

Preflight:

1. Confirm no pull request already exists for:
    fix/runtime-sttm-structured-output-0.3.148
2. Confirm this intended base branch exists on GitHub:
    feature/v3-agentic-redesign
3. Use GitHub’s comparison data to confirm that the pull request would contain:

* Exactly one new commit:
    64706129e0d1054ea615e150b28dd623fb3c629e
* Exactly these four changed files:
    * src/tools/index.ts
    * src/test/helpers/registerVscodeStub.ts
    * src/test/testPatterns.ts
    * src/test/suite/sttmPublicToolResultEnvelope.test.ts

If the base is missing, the comparison contains unexpected commits/files, or an existing pull request is found, stop and report without creating anything.

If all checks pass, create a draft pull request with:

Base:

feature/v3-agentic-redesign

Head:

fix/runtime-sttm-structured-output-0.3.148

Title:

fix: return structured STTM public tool results

Body:

Summary

* Return the complete Markdown result from the public STTM tool boundary.
* Attach the same response data as a structured JSON data part when supported by the host.
* Preserve the existing failure envelope for missing or malformed response data.
* Add public-boundary regression coverage and the required VS Code test stub support.

Validation

* Focused regression tests passed.
* Full suite result: 2311 passing, 5 pending, and 3 failures identical to the clean baseline.
* Real VS Code Extension Development Host execution passed.
* The live etl_interpret_sttm invocation returned exactly two result parts:
    * Markdown text part
    * Structured JSON data part
* Structured result MIME type was application/json.
* Structured bytes decoded successfully to a JSON object.
* Copilot consumed the tool result and rendered the STTM mappings and transformation logic.

Scope

* Exactly four source/test files are included.
* Package version remains unchanged at this stage.
* VSIX packaging and installed-QA acceptance are deferred until CI review.
* Unrelated diagnostics, governance findings, and DisposableStore warnings are outside this repair.

After creation:

1. Report the pull-request number and URL.
2. Report whether CI checks were triggered for commit:
    64706129e0d1054ea615e150b28dd623fb3c629e
3. Report their initial status without waiting for completion.

Restrictions:

* Keep the pull request in draft state.
* Do not edit files or create commits.
* Do not change the package version.
* Do not modify the local fetch refspec.
* Do not push, merge, rebase, pull, tag, or force push.
* Do not assign reviewers or labels.
* Stop after reporting the pull request and initial CI status.
