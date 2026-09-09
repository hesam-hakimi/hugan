TASK_ID: ETL-0909-WORKFLOW-EMPTY-PROJECT-BOOTSTRAP01
TYPE: BOUNDED WORKFLOW BOOTSTRAP REPAIR
LANGUAGE: English only for Agent conversation, code and artifacts.

OWNER PRODUCT REQUIREMENT
A user must be able to initialize the ETL Copilot workflow in a new,
empty project folder. Existing ETL artifacts or workflow files must not
be prerequisites for creating the initial workflow.

The required user flow is:
select project root -> preview workflow files -> explicit approval ->
create the workflow files inside that same root.

This supersedes any assumption that absence of ETL workspace markers
alone must prohibit first-time workflow setup.

It does not authorize arbitrary unknown folders as ETL write targets,
remove protected-root exclusions, or bypass preview and approval.

CURRENT CONTEXT
The screenshot shows version 0.3.147 and:
@etl /workflow create
-> workflow manager setup
-> target type unknown
-> blocked because no ETL workspace markers were found.

The screenshot establishes that blocker, not that its folder was empty.
Build the new regression using an actually empty temporary project.

ETL-0909-CONSUMER-WRITE-SMOKE01 now reports GUARDED_WRITE_VERIFIED:
two approved job/env files were written and read back through the local
Node filesystem adapter. Preserve that result at its reported boundary.
It does not establish workflow bootstrap or installed-extension behavior.
Do not repeat that write.

1. ESTABLISH THE ACTUAL IMPLEMENTATION

Worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:
fix/workspace-write-completion-0.3.148

Read the latest SMOKE01 continuation report/result and the accepted
preview-containment review through their original machine references.
Verify the current baseline and absence of a concurrent writer.
Do not repair unexplained drift or resolve pending editor changes.

Trace the actual @etl /workflow create registration, setup handler,
[CopilotWorkflow] target resolution, preview and provisioning consumers.

Search the relevant src/, resources/copilot/ and package command
registrations. Read complete relevant implementations and local rules.
Do not guess filenames or invent a replacement workflow architecture.

Identify precisely where absence of existing ETL markers blocks setup.

2. IMPLEMENT THE SMALLEST COHERENT CORRECTION

Permitted mutation boundary:
- Workflow setup target eligibility and explicit target confirmation.
- Its direct preview/provisioning consumers where required.
- Relevant user-facing outcome reporting.
- Targeted regression tests.

Record exact affected paths before editing.

Required behavior:
A. A new empty project can enter workflow setup without pre-existing
   job_conf/, env_conf/, sttm/ or generated workflow files.
B. The destination root is explicitly selected or confirmed by the user.
   Multi-root workspaces must never silently select the first folder.
C. Keep this bootstrap eligibility specific to workflow initialization.
   Do not globally classify every unknown folder as a verified ETL project.
D. Known extension/source/reference roots remain prohibited targets.
   Preserve canonical-path and symlink/junction protections.
E. Derive the workflow file set from the existing packaged assets and
   provisioning contract. Do not copy maintainer control-plane files or
   create dummy ETL markers merely to satisfy the old classifier.
F. Preview the exact files and bind approval and provisioning to the same
   root, file set and contents. Cancellation must cause no writes.
G. Create only approved workflow assets inside the selected project.
   Preserve existing user files and the established conflict policy.
H. Repeated setup must be safe and idempotent. Do not silently overwrite
   user-modified workflow assets.
I. Report created/unchanged/conflicted/blocked/cancelled outcomes clearly.
   Returning from the command is not proof that files were created.

Do not require the user to manually create ETL folders as a workaround.
Do not weaken the separate job/env write validation or its accepted
containment implementation.

3. VERIFY WITH TARGETED LOCAL TESTS

Submitting this prompt authorizes this bounded source repair, relevant
compiler checks, and local tests confined to fresh task-owned fixtures.
Any test-generated workflow files must remain inside those fixtures;
simulated user selections/approvals must be explicitly labeled.

Cover:
- First setup in an actually empty project.
- Explicit selection among multiple workspace folders.
- Rejection of protected roots and escaping destinations.
- Cancellation before provisioning.
- Repeated setup and preservation of a user-modified existing file.
- Existing recognized consumer workspace behavior.

Exercise the real setup/provisioning decisions and packaged asset plan,
not a parallel implementation of their logic.

Use existing installed tools and the minimum necessary compilation.
Place generated test/build output outside repository out/.
Reuse unaffected accepted evidence; do not rerun the STTM/protocol-3
campaign or the completed consumer write smoke.

Retain genuine failing regression evidence where feasible. Correct
routine in-scope implementation/test failures within this same task.

4. LIMITS

No real consumer-project writes, Extension Host run, installation,
packaging, release, cloud operation, Git mutation or repository out/
promotion is authorized.

Do not change test-mode activation to enable unrelated write tools.
Do not update canonical references or rewrite historical reports.
Do not claim an installed-product fix from local tests.

5. HANDOFF

Return report.md, result.json, task.diff, authenticated pre/post identities
and the relevant original test output.

Explain:
- The actual cause of the empty-project bootstrap block.
- The exact workflow-specific eligibility change.
- The packaged workflow files selected by the existing implementation.
- Root/preview/approval/provisioning consistency.
- Measured tests and their execution level.
- Remaining runtime or installed-product gaps.

Successful local completion:
STATUS: LOCAL_CHECKED_AWAITING_INDEPENDENT_BOUNDARY_REVIEW
EMPTY_PROJECT_WORKFLOW_LOCAL_RESULT: PASS
EMPTY_PROJECT_WORKFLOW_INSTALLED_VERIFIED: NO
INSTALLED_OR_RELEASE_ACCEPTANCE: NOT_GRANTED

The next gate is independent review of this exact bootstrap delta,
followed by the appropriately bounded real VS Code workflow scenario.
Do not restart accepted unrelated work.

Stop after delivering the reviewable result.
