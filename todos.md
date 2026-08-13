STRICT READ-ONLY PRODUCTION BEHAVIOR AND HARD-CODE AUDIT.

Audit the ETL Copilot Extension source, packaged product resources, compiled runtime,
and VSIX candidate.

This is an inspection-only task.

Do not modify source files, tests, prompts, packaged resources, build output,
package files, Git state, PRs, CI, or the installed extension.
Do not compile, package, install, publish, commit, push, or run CI.

PURPOSE

Determine whether production behavior is incorrectly tied to a specific sample job,
repository, STTM workbook, target table, or use case.

1. HARD-CODE SEARCH

Search for all variants of:

- etl-acz0004-cd-renewal
- CD Renewal
- cd_renewal
- CD-Renewal_DataMapping
- cz_acz0004_retail
- etl-acz0001-aczdg
- customer_interactions

Search at minimum:

- src/**
- resources/copilot/**
- package.json
- out/extension.js
- out/sttm-runtime.js
- scripts/**
- packaged VSIX contents
- tests, fixtures, documentation, and examples

For every occurrence report:

- exact file,
- line or symbol,
- surrounding purpose,
- whether it is runtime reachable,
- whether it is shipped in the VSIX,
- classification:
  - RUNTIME_HARDCODE
  - PACKAGED_PRODUCT_INSTRUCTION
  - GENERIC_EXAMPLE_ONLY
  - TEST_FIXTURE_ONLY
  - DOCUMENTATION_ONLY
  - GENERATED_OUTPUT_ONLY

An occurrence in tests or documentation is acceptable only if it cannot affect runtime
routing, prompting, fallback selection, templates, or generated output.

2. ROUTING LOGIC AUDIT

Trace the actual production path from:

@etl /workflow

through:

- target workspace selection,
- workspace classification,
- STTM resolution,
- existing-job matching,
- create-versus-update routing,
- environment resolution,
- preview manifest generation,
- approval,
- guarded apply.

Determine the actual behavior for each scenario:

A. Matching managed job exists:
   expected route = UPDATE_EXISTING_JOB

B. Valid selected Consumer ETL repository, but no matching job exists:
   expected route = CREATE_NEW_JOB
   Absence of a matching job must not itself be a blocker.

C. Explicitly selected empty or temporary workspace:
   expected route = INITIALIZE_NEW_CONSUMER_REPO
   The complete structure must come from generic packaged templates and STTM evidence.

D. Multiple matching jobs:
   expected route = REQUEST_JOB_SELECTION

E. Existing unmanaged path collision:
   expected route = BLOCK_UNSAFE_OVERWRITE

F. Extension source, installation directory, external path, or unknown target:
   expected route = BLOCK_UNSAFE_TARGET

G. Missing deployment-specific value:
   expected route = PREVIEW_WITH_UNRESOLVED_DECISION
   Do not copy values from unrelated jobs or environments.

3. EMPTY-REPOSITORY CAPABILITY

Verify whether the packaged product contains generic, use-case-independent contracts
or templates sufficient to preview creation of:

- required directory structure,
- job configuration,
- transformation SQL,
- environment configuration,
- shared/include configuration,
- onboarding metadata,
- generated consumer Copilot assets where required.

Verify that empty-repository scaffolding does not depend on:

- a sample repository,
- a sample STTM,
- CD Renewal,
- customer interactions,
- stale session paths,
- process.cwd(),
- an Extension source path,
- or an installed-extension path.

4. MATCHING RULES

Verify that existing-job matching uses deterministic evidence such as:

- stable job ID,
- onboarding identity,
- declared source/target identity,
- managed-asset metadata,
- or explicit user selection.

It must not rely only on repository name, filename similarity, workbook name,
or a previously processed example.

5. CURRENT BLOCKER CLASSIFICATION

Determine whether the observed
TARGET_WORKSPACE_IDENTITY_REQUIRES_USER_CONFIRMATION result was caused by:

- production runtime hard-coding,
- a packaged prompt/skill/instruction,
- missing CREATE_NEW_JOB routing,
- missing empty-repository scaffold support,
- a generic safety guardrail,
- or only the special read-only identity-check prompt used during diagnosis.

Do not infer the cause. Trace it to exact files and functions.

6. TEST COVERAGE AUDIT

Report whether tests already cover:

- create in an existing Consumer repository with no matching job,
- update an existing managed job,
- scaffold an explicitly selected empty workspace,
- renamed repositories and completely novel use cases,
- ambiguous matches,
- unmanaged collisions,
- no mutation before approval,
- idempotent rerun after creation,
- atomic apply failure,
- containment and cross-workspace rejection.

Do not add or change tests in this task. Report coverage gaps only.

OUTPUT

Provide:

1. Executive verdict.
2. Hard-coded occurrence table.
3. Runtime decision-flow table.
4. Empty-repository capability assessment.
5. Exact cause of the current behavior.
6. Missing implementation capabilities.
7. Missing tests.
8. Exact files that would require changes in a later implementation task.
9. Confirmation that zero files were changed.

Finish with one of:

READ_ONLY_AUDIT_RUNTIME_HARDCODE_FOUND

READ_ONLY_AUDIT_GENERIC_ROUTING_OR_SCAFFOLD_DEFECT_FOUND

READ_ONLY_AUDIT_CURRENT_RESULT_DIAGNOSTIC_PROMPT_ONLY

READ_ONLY_AUDIT_NO_RELEVANT_DEFECT_FOUND

READ_ONLY_AUDIT_INSUFFICIENT_EVIDENCE
