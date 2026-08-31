Implement only Workspace Write Completion step W1: collision detection and explicit overwrite approval.

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Required starting branch:

fix/runtime-sttm-structured-output-0.3.148

Required starting HEAD:

64706129e0d1054ea615e150b28dd623fb3c629e

Preflight:

1. Confirm the branch and HEAD.
2. Confirm `git status --short` is empty.
3. If either differs, stop.

Create a new local branch:

fix/workspace-write-completion-0.3.148

Do not push it.

Implementation scope — W1 only:

1. Create one canonical artifact-destination inventory used by both:

* Overwrite/collision detection
* The actual artifact-writing path

Do not maintain separate manually duplicated destination lists.

2. The inventory must include every artifact category that `RepoWriter.writeArtifacts` can write, including:

* Primary job configuration
* Environment configurations
* Include files
* Every `additionalJobConfigs` entry
* Any other currently writable artifact category discovered in the implementation

3. Normalize and deduplicate destinations deterministically.

If two artifacts resolve to the same destination with conflicting content or metadata, fail closed before approval and before writing.

4. Correct the existing defect where `additionalJobConfigs` can be written but is omitted from `checkOverwrites`.

5. The approval confirmation must clearly and separately display:

* CREATE
* OVERWRITE
* UNCHANGED

An existing destination must never be shown as CREATE.

6. Immediately before writing, revalidate the destination existence state against the approved preview.

If a destination changed between preview/approval and apply, reject the operation before writing any file.

7. Continue using the existing trusted approval store and manifest checksum. Do not create a second approval mechanism.

Required headless tests:

* A missing additional job configuration is classified as CREATE.
* An existing additional job configuration is classified as OVERWRITE.
* An unchanged destination is classified as UNCHANGED.
* The approval text places every path in the correct section.
* A destination-state change after approval is rejected before any write.
* Conflicting duplicate destinations fail closed.
* The canonical inventory contains every artifact category written by `writeArtifacts`.
* Existing approval, containment, and exact-byte tests continue to pass.

Testing constraints:

1. Add the new coverage to an existing headless unit suite or a new headless suite.
2. Do not add the GUI-dependent `writeFlow.test.ts` to `PURE_UNIT_TEST_PATTERNS`.
3. Run at most:

* One smallest supported focused test command for the affected suite.
* One execution of `npm run test:unit`.

The unit command may still return the same three known failures in `copilotWorkflowCustomization.test.js`. Do not fix them in this task. No new failure may appear in a workspace-write suite.

Explicit exclusions:

* Do not implement atomic multi-file apply yet.
* Do not implement managed-file ownership yet.
* Do not modify Repair 13 structured-output behavior.
* Do not change the package version.
* Do not run F5, the external harness, packaging, or installed QA.
* Do not commit, push, create a pull request, merge, rebase, reset, clean, or tag.
* Do not rewrite unrelated files or line endings.

Final report:

* New local branch
* Files changed
* Exact behavior corrected
* Tests added
* Commands and results
* Confirmation that the three known baseline failures are unchanged
* Final `git status --short`
* Stop without committing.
