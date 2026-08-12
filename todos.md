@etl /workflow

LOCAL INSTALLED-EXTENSION SMOKE TEST ONLY.

This is a read-only activation and workflow-resolution test of the installed VSIX.

Do not create, modify, rename, move, or delete any file.
Do not install dependencies.
Do not stage, commit, push, or interact with CI.
Do not approve or execute any generated change.
Do not write .github/**, job configuration, environment configuration, SQL, onboarding, or managed-asset records.

1. Confirm that the installed @etl participant activated and accepted /workflow.
2. Report the exact selected workspace root.
3. Classify the workspace as one of:
    * consumer-etl-workspace
    * temporary-test-workspace
    * extension-source
    * installation-directory
    * unknown
4. If the workspace is extension-source, installation-directory, or unknown, fail closed without writing.
5. Resolve the packaged Copilot asset catalog and report:
    * available agents;
    * prompts;
    * skills;
    * instructions;
    * knowledge assets;
    * any missing or unreadable packaged asset.
6. If this is an allowed consumer or temporary-test workspace:
    * locate STTM candidates;
    * locate existing job, environment, shared configuration, SQL, and onboarding candidates;
    * perform analysis and validation only;
    * produce at most a proposed preview manifest;
    * stop before approval or execution.
7. Do not invent missing paths or configuration.
8. Recheck that the workspace has no new, modified, staged, or deleted files.

Report any activation or packaged-asset error exactly.

Finish with one of:

LOCAL_INSTALLED_EXTENSION_SMOKE_PASS

LOCAL_INSTALLED_EXTENSION_SMOKE_BLOCKED_<EXACT_REASON>
