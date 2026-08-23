TASK: HF1 V2 QA VALIDATION — VERSION 0.3.140

We now have the approved QA candidate:

databricks-etl-copilot-0.3.140-hf1-v2-qa-clean.vsix

This task is QA validation only.

Do NOT modify source code.
Do NOT modify framework source.
Do NOT modify .github/**.
Do NOT modify AGENT.md / AGENTS.md.
Do NOT regenerate Phase-H baselines.
Do NOT commit or push anything.
Do NOT install or download dependencies.
Do NOT use any older VSIX artifact.

==================================================
1. PRE-QA ENVIRONMENT CHECK
==================================================

Before testing:

1. Inspect the currently installed Databricks ETL Copilot extension version.
2. If version 0.3.139 or any older/stale HF1 build is installed:
   - uninstall it first.
3. Confirm no other Databricks ETL Copilot version remains active.
4. Install ONLY:

   databricks-etl-copilot-0.3.140-hf1-v2-qa-clean.vsix

5. Restart/reload VS Code if required.
6. Confirm the installed extension reports version:

   0.3.140

Do not rename or substitute another VSIX.

==================================================
2. TEST WORKSPACE RULES
==================================================

Use a fresh QA/test consumer workspace.

Do NOT add etl-framework-adb or framework source as another workspace folder.

The tester/end-user workspace must represent the normal packaged-extension experience.

The extension must operate using packaged resources and the consumer workspace only.

Do not intentionally modify unrelated files.

==================================================
3. CORE QA SCENARIO — FRESH CONSUMER
==================================================

Run the normal end-user ETL flow on a fresh consumer workspace.

Exercise the normal entry point, including:

/workflow

or the currently supported equivalent ETL workflow command.

Validate that the extension can:

1. recognize the consumer workspace correctly;
2. distinguish a fresh consumer from:
   - extension source
   - framework/reference roots
   - sample_repo
   - unrelated workspace folders;
3. resolve the intended consumer root without using a first-folder fallback;
4. locate or request required ETL inputs such as STTM;
5. inspect the existing workspace;
6. build the preview/plan;
7. present intended artifact changes before writing;
8. require explicit approval before filesystem mutation;
9. write only after approval;
10. write only beneath the authorized consumer root.

Capture the exact user-visible result at each important stage.

==================================================
4. WRITE-SAFETY QA
==================================================

Specifically validate the HF1 fixes.

Test that:

- preview performs zero writes;
- declining/cancelling approval performs zero writes;
- approval allows exactly the intended write;
- replaying the same consumed approval does not produce another write;
- changing the target/path/content after preview cannot reuse the previous approval;
- prohibited/reference roots are blocked;
- sample_repo is blocked;
- extension/framework roots are blocked;
- zero-folder and ambiguous multi-root conditions fail closed rather than selecting workspaceFolders[0].

Do NOT construct dangerous external filesystem links outside a controlled QA/temp fixture unless the environment explicitly supports such testing safely.

==================================================
5. GENERATED ARTIFACT VALIDATION
==================================================

For the successful fresh-consumer flow, inspect generated ETL artifacts.

Confirm:

- paths shown during Preview are the same paths later written;
- no path is silently recomputed to another root;
- expected job config is created;
- environment/config reuse behavior matches the current product contract;
- include paths are valid;
- no unrelated .github/** files are generated;
- no maintainer/control-plane files are copied into the consumer workspace;
- no framework source directory is required by the consumer.

If the workflow produces multiple ETL artifacts, record every generated path.

==================================================
6. PROVIDER / OUTPUT BEHAVIOR
==================================================

Do not assume Oracle is the product architecture.

Oracle validation was part of this hotfix regression surface only.

The extension remains a general ETL extension and may support multiple framework output/provider patterns such as Databricks/data-lake/database/TIBCO/Synapse-style integrations according to available framework contracts.

For this QA run, validate only the provider/output path exercised by the supplied test case.

Do not redesign provider behavior.

==================================================
7. NEGATIVE QA
==================================================

Perform at least these negative checks where practical:

A. protected/reference workspace as sole folder
Expected: BLOCKED.

B. more than one eligible workspace root without explicit safe resolution
Expected: BLOCKED / ambiguous.

C. user rejects write approval
Expected: zero filesystem mutation.

D. stale/replayed approval
Expected: rejected.

E. artifact/path changes between preview and approval
Expected: rejected or fresh preview required.

Do not weaken validation to make tests pass.

==================================================
8. PACKAGE / VERSION CONFIRMATION
==================================================

Confirm during QA that the actually installed extension is 0.3.140.

Record:

- extension version
- VSIX filename
- consumer workspace used
- VS Code version
- operating system
- test start/end time

Do not rely only on the VSIX filename. Verify the installed extension metadata.

==================================================
9. RESULT CLASSIFICATION
==================================================

Classify every issue as one of:

- NEW_FUNCTIONAL_REGRESSION
- HF1_SECURITY_REGRESSION
- QA_ENVIRONMENT_ISSUE
- TEST_DATA_ISSUE
- PRE_EXISTING_KNOWN_FAILURE
- NON_BLOCKING_UX_DEBT
- PASS

Do not classify a real new issue as historical simply because the full test suite already has known failures.

==================================================
10. FINAL REPORT
==================================================

Return a concise but evidence-based report with:

1. Installed version
2. VSIX tested
3. Workspace/test scenario
4. Fresh-consumer workflow result
5. Preview result
6. Approval/write result
7. Generated artifact paths
8. Root-selection result
9. Protected-root blocking result
10. Replay/stale approval result
11. Any unexpected writes
12. Any new regression
13. Screenshots/log evidence available
14. QA verdict

End with exactly these markers:

QA_VSIX_VERSION_0_3_140_CONFIRMED: YES/NO
FRESH_CONSUMER_WORKFLOW_PASS: YES/NO
PREVIEW_WRITES_ZERO_FILES: YES/NO
EXPLICIT_APPROVAL_REQUIRED: YES/NO
APPROVED_WRITE_SUCCEEDS: YES/NO
WRITE_PATH_MATCHES_PREVIEW: YES/NO
PROTECTED_ROOTS_BLOCKED: YES/NO
MULTI_ROOT_FAILS_CLOSED: YES/NO
APPROVAL_REPLAY_BLOCKED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: YES/NO
HF1_SECURITY_REGRESSIONS: YES/NO
SAFE_TO_PROCEED_TO_PRE_MERGE_CHORES: YES/NO
QA_RESULT: PASS/FAIL

If any release-critical behavior fails, set QA_RESULT: FAIL and stop. Do not repair code during this QA task.
