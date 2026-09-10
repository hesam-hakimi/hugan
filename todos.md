TASK_ID: ETL-0910-VSIX-CANDIDATE-PREP01
TYPE: BOUNDED PRIVATE VSIX BUILD AND CONTENT VERIFICATION

Use English for all communication, reports, and artifacts.

GOAL
Produce one private VSIX candidate containing the accepted source,
including empty-project workflow bootstrap and the accepted Initialize
.gitignore disclosure fix.

Candidate version: 0.3.148.
This version identifies a private test candidate, not an accepted release.

ENVIRONMENT
Local Windows Agent.
Expected source worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

INPUTS
Read the complete report.md and result.json for:
ETL-0910-WORKFLOW-GITIGNORE-DISCLOSURE-REVIEW01

Follow its machine-recorded links to FIX01 and the accepted bootstrap
and prior Host evidence where needed.

Carry forward:
- ACCEPTED_WITH_LIMITATIONS.
- F-1 accepted for Initialize only.
- The previous Host PASS exercised sources before the disclosure fix.
- Repair/Upgrade disclosure omissions and F-2 through F-5, U-1/U-2
  remain open.
- Original job/env write-fix and installed/release qualification are
  not established by this workflow evidence.

BASELINE
Resolve evidence by task identity, not newest timestamp.
Authenticate the current source against the accepted evidence chain.
Use actual machine hashes; never transcribe hashes from photos.

Check for a concurrent writer or conflicting build.
Preserve existing dirty changes and pending editor changes.
Do not build from HEAD alone: accepted changes exist in the worktree.

If source identity materially conflicts with the reviewed state,
report the exact mismatch without repairing the baseline.

AUTHORIZED WORK
1. Inspect existing package.json, build/package scripts, packaging
   rules, runtime resources, and available local tooling.

2. Prepare an isolated build/package staging directory outside the
   repository using the authenticated current working-tree content.

3. Set version 0.3.148 only in staged package metadata. Record this
   packaging-only change explicitly. Preserve extension identity and
   all unrelated metadata; do not modify repository version files.

4. Compile the accepted source once using existing local dependencies
   and the project's applicable build configuration.
   Retained FIX01 compiled trees were disposable and removed.
   Do not reuse stale repository out/ or the older bootstrap build as
   though either included the disclosure fix.

5. Package one uniquely named private VSIX using existing local
   packaging tooling. Inspect lifecycle scripts before invoking them.
   Do not silently bypass required project gates or omit dependencies
   merely to make packaging succeed.

6. Inspect the actual VSIX archive and verify:
   - expected extension ID and candidate version;
   - valid entrypoint and required runtime dependencies;
   - compiled bootstrap and disclosure code match this build;
   - packaged catalog/resources/media are present and consistent;
   - no dependency points back to the development workspace;
   - no evidence bundles, temporary fixtures, credentials, or
     maintainer-only control-plane files are accidentally included.

Use existing packaging rules. If they require a source/config repair
or an unavailable tool, report the concrete blocker and smallest
necessary follow-up instead of expanding this task.

EFFICIENCY
Reuse existing build/package commands and tools.
Do not create another testing framework or a collection of JS helpers
under C:\docs.

Do not rerun historical red/green, broad suites, or Host scenarios.
Run only checks required to build and inspect this candidate.

BOUNDARIES
No product-source edits, repository out/ promotion, dependency
installation, Git mutation, reference updates, VSIX installation,
Host launch, real consumer writes, publishing, or release.

Staging, compiler output, the VSIX, and this task's evidence may be
written outside the repository.

DELIVERY
Retain the VSIX and a compact evidence bundle containing:
- report.md and result.json;
- source/build/package identity and the staging metadata delta;
- actual commands, exit codes, and relevant output;
- archive inventory and content-verification results;
- repository preservation results.

Record the VSIX's exact path, SHA-256, size, extension ID, and version.
Do not call the package runtime-tested or ready for release.

End with:
TASK_ID:
STATUS: CANDIDATE_BUILT_AND_CONTENT_VERIFIED / BLOCKED
SOURCE_IDENTITY:
STAGING_METADATA_CHANGE:
BUILD_RESULT:
PACKAGE_CONTENT_VERIFICATION:
VSIX_PATH:
VSIX_SHA256:
VSIX_SIZE:
EXTENSION_ID:
CANDIDATE_VERSION:
REPOSITORY_CHANGED: NO
CANDIDATE_INSTALLED: NO
HOST_EXECUTED: NO
INSTALLED_OR_RELEASE_ACCEPTANCE: NOT_GRANTED
RETAINED_LIMITATIONS:
EVIDENCE_ROOT:
NEXT_CONDITIONAL_GATE: BOUNDED_INSTALL_AND_INSTALLED_WORKFLOW_SMOKE

Stop after delivering the candidate and report.
