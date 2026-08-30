TASK: HF1_V2_FIX_PUBLIC_STTM_STRUCTURED_OUTPUT_0_3_148

Work only in:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Current state:
- The recovery product branch is locally committed and clean.
- VSIX 0.3.147 was successfully built, installed locally, and activated.
- Installed identity:
  td-etl.databricks-etl-copilot @ 0.3.147
- All 16 contributed ETL tools were available.
- Runtime QA used an isolated consumer workspace with no source repository.
- Preview remained read-only and created or modified no files.
- Runtime QA stopped with:
  BLOCKED_PREVIEW_RUNTIME_FAILURE

Observed product defect:
- The public STTM workflow result exposes the Markdown diagnostic projection.
- The required structured STTM diagnostic payload is not exposed through the
  consumer-visible VS Code tool-result boundary.
- Therefore diagnostic-code parity and affected-row identity parity cannot be verified.
- Internal-only structured data does not satisfy this requirement.

Primary objective:
Trace and minimally repair the public result path from the STTM interpreter through
the workflow/tool handler to the VS Code Language Model tool result, so both:
1. the existing Markdown projection, and
2. the structured STTM diagnostic payload
are available to the real consumer.

Do not treat this as a governance, packaging, or QA-agent problem.

Branch handling:
1. Confirm the current worktree is clean.
2. Preserve the existing 0.3.147 commit unchanged.
3. Create a new branch from the current commit:
   fix/runtime-sttm-structured-output-0.3.148
4. Do not operate on the original dirty worktree.

Implementation requirements:
1. Trace the exact production path:
   public workflow command
   → registered LM tool handler
   → STTM interpreter/parser
   → public LanguageModelToolResult
2. Identify the exact point where structured `data` is dropped.
3. Use the repository's existing public-result envelope or serialization convention.
4. Do not invent a second incompatible STTM protocol.
5. Preserve existing Markdown output and backward compatibility.
6. Preserve valid mapping IDs and order.
7. Preserve preview-only containment: no workspace write, settings change, job
   submission, execution, publishing, or managed-asset recording.
8. Missing or malformed structured results must fail closed.

Focused tests required:
1. Test the actual public tool/workflow boundary, not only `interpretSttm` internally.
2. Assert that the consumer-visible result contains both Markdown and structured data.
3. Assert exact parity between both projections for:
   - diagnostic codes
   - affected-row identities
   - ordering
4. Cover:
   - valid active mappings
   - inactive mappings
   - conflicting mappings
   - unresolved references
   - malformed short rows
   - malformed oversized rows
5. Confirm malformed rows never receive active authority.
6. Confirm preview produces zero filesystem or configuration writes.
7. Include a regression test that fails against the 0.3.147 behavior.

Strict scope:
Allowed:
- Minimum production runtime files on the STTM public-result path
- Focused tests and test fixtures
- package.json version bump to exactly 0.3.148
- Minimum package metadata required for the version bump

Forbidden:
- .github/**
- .claude/**
- scripts/agent-governance/**
- governance manifests, schemas, agents, prompts, or checkpoints
- Phase H reports
- portfolio or roadmap documents
- unrelated refactors or cleanup
- weakening existing assertions
- dependency or devDependency changes
- package-lock.json creation
- commit, push, merge, install, or Runtime QA

Verification:
Run in this order:
1. New focused regression tests
2. Existing STTM/runtime focused suites
3. npm run compile
4. npm run lint
5. npm run product:verify or the existing product-verification command
6. Canonical full unit suite once

The full unit suite may retain only the exact already-known F1/F3 failures.
No new failing or pending test identity is acceptable.

Packaging:
- Version must be exactly 0.3.148.
- Build one temporary VSIX with an explicit filename.
- Do not overwrite or delete the 0.3.147 artifact.
- Do not install the VSIX yet.
- Verify required entries, forbidden entries, archive roots, extension ID, version,
  entry count, size, and SHA-256.

Stop before commit and report:
- root cause
- exact producer-to-consumer path
- changed paths grouped as runtime / tests / package metadata
- focused-test results
- compile/lint/full-unit results
- package verification result
- VSIX temporary path, SHA-256, size, and entry count
- confirmation of zero governance changes
- confirmation that the original worktree and 0.3.147 artifact remain untouched

Final verdict must be exactly one of:
PASS_READY_FOR_OWNER_PRODUCT_REVIEW
BLOCKED_<SPECIFIC_PRODUCT_REASON>
