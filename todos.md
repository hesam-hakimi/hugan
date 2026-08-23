TASK: HF1 V2 FINAL RUNTIME QA — VERSION 0.3.140

This is a continuation of the previously blocked QA run.

The previous QA established:

- The approved VSIX is:
  databricks-etl-copilot-0.3.140-hf1-v2-qa-clean.vsix
- VSIX identity/provenance was verified at byte level.
- Installed extension version 0.3.140 matched the approved package.
- The previous runtime QA was NOT executed because the old VS Code window's extension host was still bound to 0.3.139.
- That was classified as QA_ENVIRONMENT_ISSUE, not a product failure.
- Static verification found no new HF1 functional or security regression.
- ETLChatParticipant.resolveWorkspaceRoot() retains a legacy first-folder/name heuristic, but downstream canonical write resolution and physical containment remain in place. Treat this only as previously identified NON_BLOCKING_UX_DEBT unless runtime evidence proves otherwise.

This VS Code window has now been fully restarted.

Do NOT trust the previous runtime state.
Re-establish all runtime facts from this new VS Code session.

PRECONDITIONS

1. Confirm that 0.3.140 is the active loaded Databricks ETL Copilot extension.
2. Confirm that 0.3.139 is not active in this extension host.
3. Confirm the current workspace is a disposable fresh consumer QA workspace.
4. Do NOT use or modify any real consumer repository.
5. Do NOT modify:
   - .github/**
   - AGENT.md / AGENTS.md
   - framework source
   - protected historical baselines
   - unrelated files
6. Do NOT repair code during this QA.
7. Do NOT commit or push.
8. Do NOT download/install dependencies.

If any prerequisite is missing, return QA_ENVIRONMENT_BLOCKED rather than FAIL.

RUNTIME QA

Exercise the real installed 0.3.140 extension and the real user-facing workflow.

Validate:

A. Fresh consumer
- Invoke the normal /workflow path.
- Fresh consumer workspace is recognized correctly.

B. Preview safety
- Generate a preview.
- Confirm preview writes ZERO files.

C. Approval
- Confirm explicit user approval is required.
- Reject/cancel once and prove zero writes.
- Preview again and approve.

D. Approved write
- Confirm exactly the approved artifacts are written.
- Confirm actual artifact paths exactly match the preview.
- Confirm no unrelated file is written.

E. Replay/staleness
- Attempt to reuse the consumed approval.
- It must fail closed.
- Change path/content after preview and prove the old approval cannot authorize it.

F. Protected roots
Prove writes are blocked for:
- sample_repo
- framework/source repo
- extension repo
- etl-framework-adb
- other protected/reference roots

G. Workspace topology
- zero folders → blocked
- ambiguous multi-root → blocked
- no implicit first-folder write
- explicit legitimate fresh consumer → allowed

H. Physical containment
Exercise or reuse the runtime HF1 adversarial coverage proving:
- ../ traversal rejected
- absolute escape rejected
- sibling-root escape rejected
- junction/symlink/reparse escape rejected
- dangling link escape rejected
- POSIX case-sensitive escape rejected where applicable
- no physical mutation occurs outside consumerRoot

I. Package independence
Confirm normal QA does not require:
- etl-framework-adb
- framework source workspace
- second workspace folder

Do NOT make Oracle the architectural assumption.
The ETL system may target multiple output/provider types.

FINAL CLASSIFICATION

Report each item as PASS / FAIL / BLOCKED / NOT_APPLICABLE:

ACTIVE_EXTENSION_IS_0_3_140
OLD_0_3_139_NOT_ACTIVE
FRESH_CONSUMER_WORKFLOW
PREVIEW_ZERO_WRITES
EXPLICIT_APPROVAL_REQUIRED
REJECTED_APPROVAL_ZERO_WRITES
APPROVED_WRITE_SUCCESS
WRITE_PATH_EQUALS_PREVIEW
APPROVAL_REPLAY_BLOCKED
CHANGED_PREVIEW_REQUIRES_NEW_APPROVAL
PROTECTED_ROOTS_BLOCKED
ZERO_FOLDER_FAILS_CLOSED
MULTI_ROOT_FAILS_CLOSED
NO_FIRST_FOLDER_WRITE_FALLBACK
PHYSICAL_CONTAINMENT_RUNTIME_SAFE
NO_WRITE_OUTSIDE_CONSUMER_ROOT
PACKAGED_RUNTIME_INDEPENDENT_OF_FRAMEWORK_SOURCE
NEW_FUNCTIONAL_REGRESSIONS
HF1_SECURITY_REGRESSIONS

Then conclude exactly one:

QA_RESULT: PASS
QA_RESULT: FAIL
QA_RESULT: BLOCKED

PASS requires every release-critical runtime behavior above to have actually executed successfully.
Do not convert static inspection into a runtime PASS.
Do not classify missing environment capability as product FAIL.
Do not modify source code during this task.
