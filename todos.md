TASK: HF1 V2 CREATE DISPOSABLE QA WORKSPACE AND RUN RUNTIME QA — VERSION 0.3.140

We have now confirmed in this VS Code host:

ACTIVE_EXTENSION_IS_0_3_140 = PASS
OLD_0_3_139_NOT_ACTIVE = PASS

The previous QA attempt was correctly blocked only because the open workspace
(etl-acz0004-cd-renewal) is a real established consumer repository.

Do NOT run QA against that repository.

GOAL

Create a completely disposable fresh consumer QA workspace outside the real
consumer repository, switch/open that disposable workspace as the sole workspace
root, and then execute the complete HF1 V2 runtime QA matrix using the installed
Databricks ETL Copilot 0.3.140.

IMPORTANT SAFETY RULES

Do NOT modify:
- etl-acz0004-cd-renewal
- any real consumer repository
- etl-framework-adb
- extension source
- .github/**
- AGENT.md / AGENTS.md
- framework contracts
- production deployment configuration

Do NOT commit or push anything.

The disposable workspace may be freely created, modified, and deleted.

--------------------------------------------------
PHASE 1 — CREATE DISPOSABLE CONSUMER
--------------------------------------------------

Create a new temporary directory outside all repositories.

Suggested name:

hf1-v2-qa-consumer-03140

It must initially contain:

- no .git
- no .github
- no real deployment metadata
- no existing ETL project assets
- no framework source
- no etl-framework-adb
- no extension source

Create only the minimum fixture/input necessary for the normal installed
extension workflow to recognize it as a fresh consumer workspace.

Do NOT copy an existing consumer repository.

Report its absolute path.

--------------------------------------------------
PHASE 2 — WORKSPACE ISOLATION
--------------------------------------------------

The disposable directory must become the ONLY VS Code workspace root.

Do not treat the currently open real consumer repository as a second root.

Before any workflow execution prove:

WORKSPACE_IS_DISPOSABLE = YES
WORKSPACE_IS_SINGLE_ROOT = YES
REAL_CONSUMER_REPOSITORY_NOT_TARGETED = YES
FRAMEWORK_SOURCE_NOT_PRESENT = YES
ETL_FRAMEWORK_ADB_NOT_PRESENT = YES

If the agent cannot programmatically change/open the VS Code workspace,
STOP before runtime testing and tell me exactly:

1. the disposable directory created,
2. how to open it as the sole VS Code workspace,
3. what prompt I should send after reopening it.

Do NOT classify that situation as a product defect.

--------------------------------------------------
PHASE 3 — RUNTIME IDENTITY
--------------------------------------------------

In the disposable workspace verify again from live runtime evidence:

ACTIVE_EXTENSION_IS_0_3_140 = PASS
OLD_0_3_139_NOT_ACTIVE = PASS

Installed-package metadata alone is insufficient.

Confirm the ETL Copilot runtime tools / participant / workflow entry point are
actually available in this extension host.

--------------------------------------------------
PHASE 4 — NORMAL FRESH-CONSUMER WORKFLOW
--------------------------------------------------

Exercise the installed extension exactly as an end user would.

Do not invoke extension source directly.

Run the normal fresh-consumer workflow.

Validate:

1. Fresh consumer recognition.
2. Preview produces ZERO filesystem writes.
3. Preview identifies the exact proposed artifact paths.
4. Explicit approval is required before mutation.
5. Reject/cancel produces ZERO writes.
6. Approved write succeeds.
7. Actual written paths exactly equal approved preview paths.
8. Actual written bytes/content correspond to the approved manifest.
9. Approval cannot be replayed.
10. Changing preview/path/content requires a NEW approval.
11. Zero-folder condition fails closed.
12. Multi-root ambiguity fails closed.
13. Protected/reference/framework roots cannot become consumer write roots.
14. There is NO first-folder write fallback.
15. Physical containment is enforced immediately before mutation.
16. Junction/symlink/reparse-point escape cannot write outside consumer root.
17. No filesystem mutation occurs outside the disposable consumer root.
18. Runtime works without access to etl-framework-adb or extension source.

--------------------------------------------------
PHASE 5 — HF1 SECURITY REGRESSION
--------------------------------------------------

Explicitly exercise the HF1 attack cases against the disposable workspace:

- ../ traversal
- absolute path
- sibling-root destination
- junction/reparse-point escape
- symlink escape where supported
- dangling link
- linked ancestor
- hard-link case where supported
- POSIX case-sensitive containment where applicable
- Windows case-insensitive equivalent
- TOCTOU: destination changed after preview/approval but before write

All unsafe cases must fail closed.

Do not weaken or bypass the security checks to make QA pass.

--------------------------------------------------
PHASE 6 — ARTIFACT VALIDATION
--------------------------------------------------

After successful approved generation verify:

- expected artifact paths exist
- no unexpected artifacts exist
- generated configuration is internally consistent
- no writes occurred outside the disposable root
- no framework-source dependency was introduced

Do not judge correctness based on one destination technology such as TIBCO.

The ETL framework supports multiple destination/output strategies.
HF1 QA is testing workflow/write safety and must remain destination-agnostic
unless a specific fixture intentionally exercises a provider.

--------------------------------------------------
PHASE 7 — FINAL REPORT
--------------------------------------------------

Return PASS / FAIL / BLOCKED for:

ACTIVE_EXTENSION_IS_0_3_140
FRESH_CONSUMER_WORKFLOW
PREVIEW_ZERO_WRITES
EXPLICIT_APPROVAL_REQUIRED
REJECTED_APPROVAL_ZERO_WRITES
APPROVED_WRITE_SUCCESS
WRITE_PATH_EQUALS_PREVIEW
WRITE_CONTENT_EQUALS_APPROVED_MANIFEST
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

PASS only if every release-critical runtime assertion was actually executed
and passed.

Do not convert static/source/package evidence into runtime PASS.

If an environment limitation prevents execution, use BLOCKED and identify
the exact prerequisite rather than modifying product code.

Do not repair source code during this task.
