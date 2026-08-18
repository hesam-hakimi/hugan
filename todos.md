DO NOT IMPLEMENT YET. Revise and freeze the LOCAL_HOTFIX_HF1 plan using read-only inspection only.

Resolve all of the following before requesting authorization again:

1. Reconcile the exact edit inventory.

You stated “2 new + 3 modified” test files, but the coverage table also modifies createPreviewFlow.test.ts. List every new and modified file exactly once and provide correct totals. No unlisted file may be changed after authorization.

2. Make fresh-consumer classification explicit and machine-readable.

An explicitly selected, repository-contained, valid fresh consumer with no job_conf/ and no env_conf/ must produce an exact typed decision value:

CREATE_NEW_JOB

A free-form reason such as explicit_fresh_consumer is insufficient by itself. Show the exact type, field, and downstream branch that consume CREATE_NEW_JOB. Existing unselected, external, installation, extension-source, and unknown targets must remain blocked. No marker or configuration directory may be created automatically.

3. Close every write bypass.

Prove that every write entry point, including the current hasOnboarding === false path, follows exactly:

validation → immutable preview/path manifest → explicit approval → write

performWrite must not be directly reachable without a valid approval bound to:

* selected workspace identity
* target type
* selected artifact types
* exact artifact paths and content hashes
* trusted framework identity
* trusted framework fingerprint

Add negative tests for every previously bypassing route.

4. Avoid incorrect layering or circular dependencies.

TrustedFrameworkDefinitionResolver must not depend on the approval-store layer merely to obtain SHA-256 functionality if that creates reversed layering or a circular import. Use node:crypto directly or an already-existing lower-level utility. Do not add another source file unless it is explicitly disclosed in the revised edit inventory.

5. Define trusted Oracle verification precisely.

State the exact framework definition files and semantic evidence used to verify db_data_out and db_ctrl_out. Checking only a folder name, filename, module-name constant, or packaged fallback is insufficient.

The fingerprint must cover the complete verified definition set using deterministic sorted relative paths and content hashes.

Resolver precedence must remain:

explicit validated configuration → explicitly present validated multi-root etl-framework-adb → unavailable

No recursive machine scan, repository guessing, or packaged-reference trust is permitted.

6. Clarify the configuration contract.

Confirm that databricks-etl-copilot.frameworkRepositoryPath:

* defaults to an empty string
* is read using the selected workspace/resource scope
* is canonicalized using realpath
* must resolve to a validated framework root
* never causes writes to the framework repository
* cannot silently fall back after an invalid explicitly configured value

7. Preserve the consumer artifact contract exactly.

The existing set, paths, ordering, and bytes of all 12 consumer preview artifacts must remain unchanged. Framework provenance may be added only to the internal validation/approval manifest and must not become a thirteenth consumer artifact or alter generated consumer content.

8. Make validation commands Windows PowerShell-compatible.

Do not use POSIX syntax such as:

MOCHA_GREP=”…” npm run test:unit

Use PowerShell syntax and remove the temporary environment variable afterward, for example:

$env:MOCHA_GREP = ‘HF1|Trusted framework|RepoWriter workspace selection|Job development readiness’
npm run test:unit
$hf1TestExit = $LASTEXITCODE
Remove-Item Env:MOCHA_GREP -ErrorAction SilentlyContinue
if ($hf1TestExit -ne 0) { exit $hf1TestExit }

9. Perform a read-only dependency preflight now.

Report whether node_modules, TypeScript, ESLint, Mocha, and every required local test dependency are already available in etl_framework_extension_hf1.

Do not install, copy, link, or download dependencies. If the required local toolchain is unavailable, report:

HF1_VALIDATION_TOOLCHAIN_UNAVAILABLE

and identify the missing components before implementation authorization.

10. Keep the evidence limitation explicit.

Real-consumer verification remains:

NOT EXECUTED — SAMPLE UNAVAILABLE

Synthetic tests must not be described as production-consumer validation.

Return:

* corrected root-cause-to-change mapping
* exact final new-file list
* exact final modified-file list
* exact no-touch list
* exact PowerShell validation commands
* dependency-preflight result
* final test matrix
* confirmation that no mutation occurred

Then stop and request the same single authorization token:

APPLY_LOCAL_HOTFIX_HF1
