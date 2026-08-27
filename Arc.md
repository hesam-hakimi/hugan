@etl /workflow

TASK: HF1_V2_RUNTIME_QA_REPAIR_13_PREVIEW_ONLY_VERSION_0_3_145

This is a strictly bounded, preview-only Runtime QA of the installed ETL extension.

Expected installed extension:

EXTENSION_ID: td-etl.databricks-etl-copilot
VERSION: 0.3.145

Work only inside the currently open Development Test Workspace.

This workspace is a synthetic QA workspace. It is not the extension source
repository, SIT, production, or a real consumer repository.

Do not access:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Do not modify or repair the installed extension or its source.

==================================================
1. STRICT PREVIEW-ONLY BOUNDARY
==================================================

This task authorizes:

- extension activation;
- read-only workspace discovery;
- reading the existing synthetic QA STTM;
- STTM interpretation;
- structured and Markdown result generation;
- Preview generation in memory;
- read-only diagnostics and reporting.

This task does not authorize:

- approving the Preview;
- executing Write;
- creating or modifying job, environment, SQL, configuration or source files;
- creating consumer `.github/**` content;
- creating a managed-asset record;
- modifying the STTM;
- installing or changing extensions;
- accessing real data or external environments;
- commit, push, stage, stash, reset, clean or restore.

Before activation, capture an independent workspace snapshot containing path,
size and SHA-256 for every non-ignored workspace file.

Repeat the snapshot after QA. Any workspace mutation is a failure.

==================================================
2. INPUT SELECTION
==================================================

Locate the existing synthetic QA STTM inside the Development Test Workspace.

Prefer the existing QA file previously designated for Repair 11, Repair 12 and
Repair 13 validation, including `synthetic_sectioned_sttm.md` if present.

Do not create or edit an STTM.

If exactly one authoritative synthetic QA STTM cannot be determined, stop and
list the candidates without selecting one arbitrarily.

Report the selected STTM’s:

- workspace-relative path;
- byte size;
- SHA-256;
- source and target mapping count.

==================================================
3. ACTIVATION AND WORKSPACE CLASSIFICATION
==================================================

Prove that the installed 0.3.145 extension activates in this reloaded Extension
Host.

Report:

- active extension ID;
- active runtime version;
- workspace root count;
- selected workspace root;
- workspace classification;
- loaded @etl command/workflow;
- activation or runtime errors.

Fail if the runtime version is not exactly 0.3.145.

==================================================
4. REPAIR 13 LIVE RUNTIME VALIDATION
==================================================

Execute the public installed-extension workflow against the selected synthetic
STTM through the real consumer-facing seam.

Do not validate only an internal model.

Verify:

1. Structured and Markdown Active Mappings contain exactly the same mapping IDs.
2. Mapping IDs appear in exactly the same deterministic order.
3. Both channels derive their selected mappings from one authoritative result.
4. Only mappings with positive active authority are included.
5. Conflicting mappings are excluded from active authority.
6. Conflicting mappings are deterministically disclosed in both channels.
7. Historical, inactive and unknown states do not gain active authority.
8. An inactive mapping does not create a blocker merely because it is inactive.
9. Undeclared state values fail closed.
10. Unresolved references remain visibly disclosed and non-authoritative.
11. No negative-state predicate grants authority.
12. Active mapping count agrees across structured output, Markdown and Preview.
13. Repair 12 STTM fields and mapping behavior remain unchanged.
14. No public Write, approval, Preview-approval or machine-authority surface is
    broadened.

Return the complete ordered Active Mapping ID list from both channels and their
equality result.

Return the excluded mapping list with state, reason and diagnostic code.

==================================================
5. PREVIEW VALIDATION
==================================================

Generate the normal Preview result in memory only.

Verify:

- Preview is produced successfully;
- no approval is inferred;
- no write is performed;
- CREATE, MODIFY, UNCHANGED, CONFLICT and BLOCKED classifications remain
  deterministic;
- conflicting or unresolved mappings cannot authorize generated output;
- no job or environment duplication is proposed;
- existing environment reuse rules remain intact;
- transformation inputs reference valid sourced aliases/views;
- output strategy is based only on STTM and workspace evidence.

Do not proceed beyond the Preview boundary.

==================================================
6. FINAL NON-MUTATION PROOF
==================================================

Compare the final workspace snapshot with the pre-QA snapshot.

Required:

WORKSPACE_CHANGED_PATHS: NONE
STTM_CHANGED: NO
JOB_FILES_CREATED_OR_CHANGED: NO
ENV_FILES_CREATED_OR_CHANGED: NO
SQL_FILES_CREATED_OR_CHANGED: NO
GITHUB_FILES_CREATED_OR_CHANGED: NO
MANAGED_ASSET_RECORD_CREATED: NO
PREVIEW_APPROVED: NO
WRITE_EXECUTED: NO
GIT_STATE_CHANGED: NO

==================================================
7. FINAL REPORT
==================================================

Return:

EXTENSION_ID: <value>
INSTALLED_RUNTIME_VERSION: <value>
EXTENSION_ACTIVATED: YES/NO
WORKSPACE_ROOT: <value>
WORKSPACE_CLASSIFICATION: <value>
SELECTED_STTM_PATH: <value>
SELECTED_STTM_SHA256: <value>

STRUCTURED_ACTIVE_MAPPING_IDS: <complete ordered list>
MARKDOWN_ACTIVE_MAPPING_IDS: <complete ordered list>
ACTIVE_MAPPING_IDS_EQUAL: YES/NO
ACTIVE_MAPPING_ORDER_EQUAL: YES/NO
ACTIVE_MAPPING_COUNT_EQUAL: YES/NO

EXCLUDED_MAPPINGS: <complete list>
CONFLICTING_MAPPINGS_EXCLUDED: YES/NO
CONFLICT_DIAGNOSTICS_PRESENT_IN_BOTH_CHANNELS: YES/NO
UNRESOLVED_MAPPINGS_NON_AUTHORITATIVE: YES/NO
UNDECLARED_STATES_FAIL_CLOSED: YES/NO
INACTIVE_MAPPING_CAUSES_BLOCKER: YES/NO
PUBLIC_MACHINE_AUTHORITY_BROADENED: YES/NO

PREVIEW_CREATED_IN_MEMORY: YES/NO
PREVIEW_APPROVED: NO
WRITE_EXECUTED: NO
WORKSPACE_CHANGED_PATHS: <complete list or NONE>
NEW_RUNTIME_ERRORS: <complete list or NONE>
NEW_SECURITY_FINDINGS: <complete list or NONE>

READY_FOR_EXPLICIT_APPROVAL_AND_WRITE_QA: YES/NO

End exactly with one:

RUNTIME_QA_RESULT:
PASS_PREVIEW_ONLY_READY_FOR_EXPLICIT_WRITE_QA

RUNTIME_QA_RESULT:
FAIL_EXTENSION_ACTIVATION

RUNTIME_QA_RESULT:
FAIL_REPAIR_13_RUNTIME_BEHAVIOR

RUNTIME_QA_RESULT:
FAIL_WORKSPACE_MUTATION

RUNTIME_QA_RESULT:
BLOCKED_QA_INPUT_AMBIGUITY
