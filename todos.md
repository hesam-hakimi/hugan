TASK_ID: ETL-0909-WORKFLOW-EMPTY-PROJECT-INDEPENDENT-REVIEW01
TYPE: BOUNDED INDEPENDENT BOUNDARY REVIEW
REVIEWED_TASK: ETL-0909-WORKFLOW-EMPTY-PROJECT-BOOTSTRAP01

Use English for all communication, reports, and artifacts.

GOAL
Independently review the completed empty-project workflow bootstrap
change and its retained evidence. Determine whether its local source
boundary is acceptable.

This is a review task. Do not implement fixes or rerun the project.

OWNER REQUIREMENT
A user must be able to initialize the packaged ETL Copilot workflow
in an explicitly selected new/empty consumer project without first
creating ETL marker folders.

The intended flow is:
select consumer root -> preview workflow assets -> approve -> create
the approved assets in that same root.

This does not make every unknown folder a verified ETL workspace,
remove protected-root exclusions, or authorize unrelated write routes.

REPORTED STATE — VERIFY FROM MACHINE RECORDS
BOOTSTRAP01 reports:
- LOCAL_CHECKED_AWAITING_INDEPENDENT_BOUNDARY_REVIEW.
- 13 new tests passed.
- A separate regression probe failed against pre-edit sources and
  passed against post-edit sources.
- 143 adjacent tests passed in the named passing suites.
- The customization suite retained three documented pre-existing
  failures; it was not fully green.
- No real VS Code Host or installed-extension qualification.
- Repository output and maintainer .github content were preserved.

Treat these as claims to inspect, not conclusions to copy.

INPUTS AND BASELINE
1. Resolve the existing BOOTSTRAP01 evidence bundle using bounded
   direct-child discovery under C:\docs and its machine-recorded task ID.
   Do not select a bundle solely because it has the newest timestamp.

2. Read its full report, result, governing task brief, exact task diff,
   baseline/precopy records, preservation records, and relevant test
   outputs. Follow explicit artifact links within that evidence chain.

3. Obtain expected worktree, branch, HEAD, changed paths, hashes, and
   byte counts from those records. Never transcribe a hash from a photo.

4. Verify that the live five-file post-state matches the reviewed
   evidence. src/test/testPatterns.ts was already dirty before this
   task: compare its actual pre-task copy, not HEAD.

5. Confirm no writer or relevant Host is currently using the worktree.
   If one is active, return WAITING_FOR_ACTIVE_TASK. Do not start another.

If task identity, baseline, or required evidence is missing or conflicting,
report the precise blocker. Do not repair, reset, normalize, or re-pin it.
Do not reconstruct missing contract text.

REVIEWED DELTA
- src/customization/WorkflowTargetResolver.ts
- src/customization/CopilotWorkflowInitializer.ts
- src/customization/CopilotWorkflowCommands.ts
- src/test/testPatterns.ts
- src/test/suite/workflowEmptyProjectBootstrap.test.ts

Read directly required callers and helpers to establish behavior.
Do not broaden into unrelated project cleanup or historical audits.

REVIEW QUESTIONS

A. Bootstrap eligibility and root selection
- Does setup work for a genuinely empty selected consumer directory?
- Is bootstrap opt-in limited to the intended workflow operations?
- Does default classification remain unchanged?
- Does multi-root selection require an explicit choice?
- Determine how populated but unmarked directories are treated.
  Assess that behavior against explicit consumer designation and the
  governing brief; do not assume "unknown" alone proves either safety
  or a defect.
- Verify protected extension/framework/reference roots, filesystem
  roots, and home exclusions. Check actual identity and containment
  behavior, including aliases and junctions where relevant.
  Basename-list parity alone is not proof of protected-root identity.

B. Preview, approval, and actual writes
- Trace the selected root through preview, confirmation, approved plan,
  revalidation, and filesystem write.
- Verify that approval binds the actual destination and written assets,
  including relevant content/profile changes.
- Inspect the optional approvedPlan parameter and every production
  caller. Determine whether bootstrap can bypass the required
  preview/approval binding through another entrypoint.
- Examine changes between preview and write: root, file set, content,
  and existing destination state.
- Check managed .gitignore changes explicitly: are these side effects
  adequately disclosed and authorized, contained to the selected root,
  and protective of existing user content?
- Cancellation must cause no provisioning writes. Blockers or drift
  must not authorize unapproved side effects.
- Verify physical containment is enforced at the actual write boundary.

C. Preservation and user-visible results
- Existing user-modified files must not be silently overwritten.
- Repeat initialization must preserve the documented idempotent behavior.
- Assets must come from the packaged catalog; no maintainer control-plane
  files or artificial ETL markers may be introduced.
- Creation, unchanged files, conflicts, blockers, cancellation, and
  managed .gitignore changes must be reported accurately.
- A blocked or empty result must not be presented as successful creation.
- Job/env writing and other non-bootstrap operations must retain their
  existing authorization and root-selection boundaries.

D. Evidence quality
- Authenticate the exact diff and pre/post identities.
- Verify that the regression probe exercises the relevant real code and
  that its red result is the intended assertion failure.
- Verify the retained compiler and test outputs, source-to-output
  relationship, and the reported test counts.
- Check the evidence supporting the three pre-existing customization
  failures. Do not describe that suite as fully passing.
- Distinguish external compilation, headless tests with simulated user
  interaction, real temporary filesystem writes, real VS Code Host
  behavior, and installed-extension qualification.
- Verify relevant preservation claims using retained machine records.

AUTHORITY AND EFFICIENCY
Allowed:
- Read-only inspection and hashing.
- Read-only helper scripts that do not import or execute project code.
- Creation of this review's report and result in one fresh evidence
  directory outside the repository.

Not allowed:
- Source, reference, existing-evidence, or editor-change mutation.
- Compiler, tests, runner, Host, or product execution.
- Dependency installation, output promotion, packaging, installation,
  Git mutation, publishing, or release.
- Real consumer workspace writes.

Reuse unchanged accepted evidence. Do not rerun the earlier consumer-write
smoke or reopen accepted protocol/STTM work. Missing installed evidence is
a stated qualification limit, not automatically a local source defect.

DELIVERABLE
Produce one concise report.md and result.json.

For each material finding include:
- exact file and location;
- reachable path or concrete evidence;
- violated requirement and practical consequence;
- smallest necessary correction.

Separate demonstrated defects, unresolved evidence questions, and
non-blocking limitations. Do not invent a defect to fill a checklist.

End with:
TASK_ID:
REVIEWED_TASK:
REVIEW_RESULT: ACCEPTED / ACCEPTED_WITH_LIMITATIONS / CHANGES_REQUIRED / BLOCKED / WAITING_FOR_ACTIVE_TASK
REVIEWED_SOURCE_IDENTITY:
BASELINE_AND_DIFF_VERIFIED:
BOOTSTRAP_ROOT_SELECTION:
PREVIEW_APPROVAL_WRITE_BINDING:
GITIGNORE_AUTHORIZATION_AND_PRESERVATION:
PROTECTED_ROOT_AND_CONTAINMENT:
LOCAL_TEST_EVIDENCE:
MATERIAL_FINDINGS:
RETAINED_LIMITATIONS:
REPOSITORY_CHANGED_BY_REVIEWER: NO
PROJECT_COMPILER_TEST_RUNNER_OR_HOST_EXECUTED_BY_REVIEWER: NO
EMPTY_PROJECT_WORKFLOW_INSTALLED_VERIFIED: NO
INSTALLED_OR_RELEASE_ACCEPTANCE: NOT_GRANTED
EVIDENCE_ROOT:
REPORT_PATH:
RESULT_PATH:
NEXT_CONDITIONAL_GATE:

If accepted, identify the smallest separately bounded real VS Code
workflow verification needed next. If changes are required, identify
only the necessary correction scope. Execute neither.

Stop after delivering the review.
