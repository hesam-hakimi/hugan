READ-ONLY TARGETED HARD-CODE TRACE.

Do not modify any file.
Do not replace or delete any occurrence.
Do not compile, test, package, install, commit, push, or use CI.

1. Inspect the exact `CD Renewal` occurrence in:

   src/core/sttm/SttmAuditor.ts

2. Report:

   - the complete enclosing function,
   - the condition that leads to this message,
   - every helper function used by that condition,
   - every caller of the enclosing function,
   - whether this code is reachable from `@etl /workflow`,
   - whether it is included in the packaged VSIX.

3. Determine whether `CD Renewal` is:

   - diagnostic text only,
   - a template/classifier identifier,
   - a workbook structural profile,
   - a fallback selection,
   - an acceptance/rejection condition,
   - or a source of generated values.

4. Search production-relevant locations, separately from tests:

   - src/**
   - resources/copilot/**
   - package.json
   - out/extension.js
   - out/sttm-runtime.js
   - packaged VSIX contents

   Search case-insensitively for:

   - CD Renewal
   - cd_renewal
   - cd-renewal
   - cdRenewal
   - acz0004
   - cz_acz0004_retail
   - renewal
   - sample_sttm

5. Do not count tests, fixtures, or documentation as runtime defects unless production
   code imports, copies, retrieves, or uses them as fallback inputs.

6. Trace the production routing when:

   - the selected workspace is an authorized Consumer ETL repository,
   - an STTM is supplied,
   - no matching job, environment, onboarding, or SQL file exists.

   Determine whether the actual route is:

   - CREATE_NEW_JOB,
   - PREVIEW_NEW_JOB_WITH_MISSING_DECISIONS,
   - REQUEST_TARGET_CONFIRMATION,
   - or BLOCK_NO_EXISTING_JOB.

7. Trace the production routing for an explicitly selected empty temporary workspace.
   Determine whether generic scaffolding exists and whether it depends on a sample job.

8. Provide a table containing:

   - exact file and line,
   - runtime reachability,
   - behavioral impact,
   - test-only versus production,
   - required correction.

9. Confirm that zero files were changed.

Finish with exactly one:

TARGETED_AUDIT_RUNTIME_USE_CASE_HARDCODE_CONFIRMED

TARGETED_AUDIT_MESSAGE_ONLY_NO_BEHAVIORAL_HARDCODE

TARGETED_AUDIT_NEW_JOB_ROUTING_DEFECT_CONFIRMED

TARGETED_AUDIT_MULTIPLE_DEFECTS_CONFIRMED

TARGETED_AUDIT_INSUFFICIENT_EVIDENCE
