# Phase 1B.3G-C1 — Corrected Hash Gate and Resume One-Shot Host Run

The previous BLOCKED result was caused solely by an incorrect expected hash
supplied in the prompt.

No runner was invoked.
No Extension Host was launched.
No focused test was evaluated.
No isolation/evidence directory was created.
No repository, QA, or environment state was changed.

Therefore, this is not a Host retry and the one-shot launch budget remains
completely unused.

## Authoritative correction

The correct SHA-256 for:

out/test/suite/index.js

is:

D6151E50E5996F048E3E60129B10AB75205A7300988847748A75DDD3BF9222CC

The previously supplied value containing:

A75D0D3

was a transcription error. The authoritative compiled artifact contains:

A75DDD3

All other fixed values, hashes, guardrails, evidence requirements and
PASS/FAIL/BLOCKED definitions from Phase 1B.3G remain unchanged.

## Corrected resume gate

1. Verify the corrected suite/index.js hash directly from disk.
2. Reconfirm that:

   - repository path, branch and HEAD remain unchanged;
   - Git status remains exactly the same three lines;
   - the other four compiled hashes still match;
   - request.md and focused-test hashes still match;
   - the current runTest.ts hash matches the immediately preceding
     sanitization PASS state;
   - the QA inventory still contains exactly 23 byte-identical files;
   - the workbook size and SHA-256 still match;
   - runner invocations remain 0;
   - Host launches remain 0;
   - focused tests evaluated remain 0;
   - no isolation/evidence directory was created by the blocked preflight.

Do not compile, edit, repair, or create a new expected hash.

If this corrected gate passes, resume the previously authorized Phase 1B.3G
at Step 2.

## One authorized Host invocation

Create one unique Temp isolation/evidence directory and set only the
environment-variable contracts already verified in the current source.

Then, from the repository root, invoke exactly once:

& 'C:\Program Files\nodejs\node.exe' '.\out\test\runTest.js'

Do not use npm, F5, Code.exe directly, Start-Process, a wrapper, sidecar,
Cloud, ETL Orchestrator, or another launcher.

Do not retry.

Apply all structured-result requirements and classification rules from the
original Phase 1B.3G prompt.

After completion, verify repository, compiled artifacts and QA integrity and
retain the isolation/evidence directory.

End with exactly one marker:

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_PASS

or

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_FAIL

or

F5_LOCAL_REAL_HOST_STRUCTURED_RESULT_BLOCKED
