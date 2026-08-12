@etl /workflow

LOCAL END-TO-END STTM PREVIEW TEST ONLY.

Use the installed extension. Do not create, modify, rename, move, or delete any file.

1. Confirm the selected workspace is an allowed consumer ETL workspace.
2. Find supported STTM files only inside the selected workspace.
3. If none are found, stop with:
    LOCAL_STTM_PREVIEW_BLOCKED_NO_STTM
4. If multiple candidates exist, list them and request explicit selection without guessing.
5. If exactly one STTM exists:
    * parse it using the native STTM parser;
    * analyze existing job, environment, shared configuration, SQL, and onboarding assets;
    * reuse an existing compatible environment;
    * resolve nested includes;
    * validate sourcing → transformation → writer sequencing;
    * select an output strategy only from explicit evidence;
    * produce a preview manifest using:
        CREATE, MODIFY, UNCHANGED, CONFLICT, or BLOCKED.
6. Do not execute the manifest.
7. Do not request or assume approval.
8. Do not write managed-asset records.
9. Do not install dependencies or interact with Git or CI.

Report the exact STTM path, resolved target files, evidence, conflicts, and preview manifest.

Finish with:

LOCAL_STTM_END_TO_END_PREVIEW_PASS

or

LOCAL_STTM_PREVIEW_BLOCKED_<EXACT_REASON>
