LOCAL_HOTFIX_HF1 — TRUSTED FRAMEWORK RESOLUTION AND FRESH-CONSUMER WRITE GATE

This task fixes a production Extension defect that blocks both:

* etl_validate_artifacts
* etl_write_to_workspace

for a valid, explicitly selected fresh consumer ETL workspace using Oracle delivery controls.

This is an Extension-source hotfix. Do not run it in the S-A/S-B implementation worktree or any chat with an unaccepted S-B review card.

Problem statement

The current Extension conflates two different states:

1. The selected consumer workspace is valid but has no existing job_conf/ or env_conf/ because the requested operation is CREATE_NEW_JOB.
2. The local validator lacks the trusted Oracle framework definitions for db_data_out and db_ctrl_out.

The current generic blocker, “Confirm destination schema/table or database delivery controls,” is insufficient because it does not distinguish those states.

A packaged reference is documentation and read-only guidance only. It must never be treated as an authoritative framework definition source or cause Oracle validation to pass.

Read-only discovery first

This request authorizes read-only inspection only.

Before editing any file or running a mutating command:

1. Map the actual implementation of:
    * consumer workspace selection and classification;
    * fresh-repository capability checks;
    * framework repository resolution;
    * packaged-reference fallback;
    * destination-delivery-control validation;
    * preview manifest creation;
    * guarded write and pre-write revalidation;
    * relevant unit/integration tests.
2. Identify the smallest exact source and test file set required.
3. Identify the existing configuration naming convention for a user-configured framework-root setting, if one exists.
4. Return a concise implementation plan with:
    * exact files to change;
    * exact files not to change;
    * validation commands;
    * expected test coverage;
    * whether a trusted framework identity/version/manifest can already be captured.
5. Do not edit, create, delete, package, install, download, or run a write-capable command yet.

Then request exactly this approval token and stop:

APPLY_LOCAL_HOTFIX_HF1

Required hotfix behavior after approval

After receiving APPLY_LOCAL_HOTFIX_HF1, implement only the approved minimal change set.

A. Trusted framework-definition resolver

Add or repair a deterministic resolver with this precedence:

1. An explicitly configured and validated framework root, if the Extension already supports a setting for it or adds one using the established configuration convention.
2. An explicitly present and validated etl-framework-adb folder in the current VS Code multi-root workspace.
3. No authoritative framework source.

Requirements:

* Never scan arbitrary folders to guess a framework.
* Never use an unselected workspace folder.
* Never use the Extension source, installation directory, consumer workspace, or an external path as an implicit fallback.
* Resolve and canonicalize the framework root before use.
* Read the framework only; never modify it.
* Verify the expected framework identity and required Oracle module definitions.
* Record framework source identity, source kind, canonical root, and a deterministic version or manifest fingerprint in the validation/preview state.
* If the framework source or its required module definitions change after preview, pre-write revalidation must block and require a new preview.
* If the framework is absent, return one actionable machine-readable blocker such as FRAMEWORK_DEFINITION_UNAVAILABLE.
* If the framework exists but Oracle definitions are missing, return a distinct blocker such as ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING.
* The packaged reference may explain how to fix the issue, but may never validate Oracle controls or turn a block into a pass.

B. Fresh consumer workspace classification

A selected, contained, valid consumer repository with no matching job_conf/ or env_conf/ must be eligible for:

CREATE_NEW_JOB

It must not be classified as unknown merely because the requested job does not exist yet.

Requirements:

* Keep explicit workspace selection mandatory.
* Keep path containment and target classification fail-closed.
* Extension source, installation directory, unselected roots, external paths, and unknown targets remain blocked.
* Do not create etl-workspace.json automatically merely to pass capability checks.
* Do not require a user to manually create job_conf/ or env_conf/.
* If an official consumer marker is part of the existing contract, it may be included only as an exact previewed artifact and written only through the normal approved manifest flow.
* Missing business/environment values remain explicit unresolved decisions; do not invent them.

C. Preserve the guarded-write contract

The sequence remains:

select consumer workspace
→ classify target
→ resolve trusted framework definitions
→ resolve/canonicalize inputs
→ validate
→ build immutable artifact manifest
→ preview
→ explicit approval
→ one-time guarded write

Requirements:

* Activation and preview write no consumer files.
* Validation, preview, approval, and write must consume the same immutable artifact-path manifest.
* Do not recompute output paths independently at write time.
* Preview must bind workspace identity, framework fingerprint, artifact paths, artifact bytes/hashes, dispositions, approval expiry, and one-time consumption.
* Any drift in workspace identity, framework identity, framework fingerprint, input files, target paths, or artifact hashes requires a new preview.
* Do not bypass destination validation.
* Do not allow Oracle output merely because a user manually copied rendered files.
* Do not weaken collision protection or overwrite handling.

D. Required tests

Add or update executable tests proving:

1. A fresh, explicitly selected valid consumer workspace with no job configuration reaches CREATE_NEW_JOB.
2. An unselected, external, installation, or Extension-source root remains blocked.
3. A multi-root workspace containing validated etl-framework-adb resolves authoritative Oracle definitions.
4. An explicitly configured valid framework root resolves authoritative Oracle definitions.
5. A missing framework root produces FRAMEWORK_DEFINITION_UNAVAILABLE and no write.
6. A framework missing Oracle delivery modules produces ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING and no write.
7. Packaged reference fallback remains guidance-only and cannot validate Oracle controls.
8. A valid Oracle framework source permits deterministic validation of db_data_out and db_ctrl_out.
9. Framework-source drift after preview blocks write and requires a new preview.
10. The same immutable path manifest is used by validation, preview, approval, and write.
11. Preview remains write-free.
12. The exact existing 12-artifact preview remains unchanged except where the hotfix deliberately adds required framework provenance to internal state, not consumer artifact content.

E. Strict scope exclusions

Do not:

* modify the consumer repository;
* manually create consumer job_conf/ or env_conf/;
* manually copy rendered configuration files;
* add a hand-written workspace marker outside the approved manifest flow;
* modify the ETL framework repository;
* modify S-A or S-B files;
* run Git mutations;
* install dependencies;
* download VS Code, Databricks tooling, or packages;
* package or publish a VSIX;
* run network-dependent integration;
* weaken or bypass validation;
* alter unrelated settings behavior.

Use local tests and local dependencies only.

Final report

Report:

1. Root cause, separated into framework-resolution and fresh-consumer classification defects.
2. Exact files changed and why.
3. Framework resolver precedence and trust boundary.
4. How Oracle validation behaves for every source state.
5. How a fresh consumer is classified.
6. Preview/write manifest binding evidence.
7. Tests and exit codes.
8. Any unrelated failures, separately.
9. Whether a patch package/build is ready for a separate authorized phase.

Finish with exactly one marker:

LOCAL_HOTFIX_HF1_COMPLETE

or:

LOCAL_HOTFIX_HF1_BLOCKED

Do not package, install, deploy, or test a VSIX in this task.
