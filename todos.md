TASK_ID: ETL-0909-PREVIEW-CONTAINMENT-REPAIR01
TYPE: BOUNDED PREVIEW/APPROVAL BOUNDARY REPAIR
LANGUAGE: English only for Agent conversation, code and artifacts.

OWNER-CONFIRMED OBJECTIVE
Generated files must target the explicitly selected consumer project
at the correct relative paths. Extension/reference roots and destinations
escaping the consumer root must never become approved write targets.

The historical wrong-root scenario is already confirmed by the owner.
Do not ask for scenario confirmation again.

CURRENT EVIDENCE
ETL-0909-PRODUCT-WRITE-REPRO01 reports:
- PREWRITE_ROUTING_CONFIRMED using compiled product modules and the real
  tool route with SIMULATED_WORKSPACE_ADAPTER.
- No Extension Host invocation and no actual product file writes.
- The historical selection defect did not reproduce at that boundary.
- Finding F-1: an escaping destination enters the trusted preview as an
  approvable CREATE, although the independent write-time guard rejects it.
- Historical artifact bytes fail current pre-routing validation; the
  successful routing input is explicitly a derived fixture.

Preserve these distinctions. Do not claim installed behavior, actual
writing, or historical-version runtime reproduction.

TASK
Fix F-1 so preview/approval excludes destinations that the existing
containment guard rejects. Keep the write-time containment check intact.

Submitting this prompt authorizes the bounded source correction,
targeted local tests and necessary local compiler checks described below.
It does not authorize a Host, product output writes or release.

1. RESOLVE ACTUAL INPUTS

Worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Expected branch:
fix/workspace-write-completion-0.3.148

Resolve the completed REPRO01 evidence directory through bounded
direct-child task-prefix discovery under C:\docs.
Authenticate its task identity and read:
- report.md and result.json;
- measurements/d1-routing-preview.json;
- measurements/d6-converged-full-route-preview.json;
- the diagnostic driver and fixture records needed for F-1.

Follow actual machine references for expected identities.
Do not transcribe hashes, preview IDs or temporary-root names from photos.

Verify current baseline against the applicable machine records, including
branch, HEAD, staging, dirty paths and affected source identities.
Do not repair unexplained drift or duplicate a running writer.

Reuse existing reference context and accepted evidence.
Read complete relevant source files and applicable local instructions.
Do not reconstruct absent reference documents or reread unrelated archives.

2. BOUNDED IMPLEMENTATION

Start with:
src/core/trusted/WriteAuthorization.ts
src/core/artifacts/ArtifactDestinationInventory.ts

Trace their direct callers and the existing containment implementation,
including RepoWriter.resolveContainedWorkspacePath and its consumers.

Permitted changes:
- Manifest destination validation.
- Direct caller changes strictly needed to propagate its blocked result.
- Minimal reuse/export or pure shared extraction of the existing
  containment routine, if necessary.
- The nearest relevant regression tests, or one dedicated test file.

Record the exact selected file list and purpose before editing.
Keep the change within this semantic boundary.

Do not change root-selection policy, approval semantics, file content
generation, write-time validation, STTM behavior, outcome classification,
extension activation or test-mode registration.

Do not duplicate a weaker path-validation algorithm.
Do not use a string-prefix check as proof of containment.

Required behavior:
- Validate destinations against the selected canonical consumer root
  before they can enter an approvable manifest.
- Reject traversal, disallowed rooted destinations and link/junction
  escapes using the existing containment policy.
- If containment cannot be established, fail closed with the existing
  structured blocker mechanism.
- An invalid destination must not be stored or displayed as an approvable
  CREATE/MODIFY or become eligible for an approval token.
- Valid in-root destinations retain their intended relative paths,
  content and existing preview behavior.
- Preserve independent containment validation immediately before writing.
  Preview validation does not replace that protection.

Use the smallest compatible correction. Do not introduce a new approval
protocol or redesign the manifest architecture.

3. TARGETED VERIFICATION

Use existing installed compiler/test tooling.
Emit only the required test/dependency output into this task's external
evidence directory. Do not promote into repository out/ or hand-edit
compiled product JavaScript.

Use the real manifest/authorization implementation in the regression.
Label any simulated VS Code adapter explicitly.

Required cases:
A. Reproduce F-1 on authenticated pre-edit code: the escaping destination
   is incorrectly offered for approval.
B. The identical regression passes after correction because that
   destination is blocked before becoming approvable.
C. Both valid consumer destinations from REPRO01 still preview correctly.
D. Disallowed rooted destinations and a Windows junction escape are
   rejected at the preview boundary.
E. A mixed valid/invalid set cannot authorize the invalid member.
F. No approval prompt or product write is invoked during these checks.

Create filesystem fixtures only inside fresh task-owned temporary roots.
Preserve original evidence and historical consumer artifacts.

A compiler/import failure is not behavioral red.
Retain genuine failed attempts and their corrections.
Resolve routine in-scope implementation or test defects in this task;
do not stop merely because the first attempt fails.

Reuse accepted unchanged checks. Do not rerun the protocol-3/STTM Host
suite or generate another full qualification bundle for this correction.

4. AUTHORITY LIMITS

No Extension Host, installed-extension smoke, actual product write,
approval token creation, dependency installation, output promotion,
packaging, cloud operation, publishing or Git mutation.

Do not resolve pending editor changes.
Do not modify canonical references, prior reports or evidence bundles.
Do not investigate incidental historical files unrelated to F-1.

The REPRO01 preview ID is stale. This repair grants no approval to reuse
it or to write into its retained temporary workspace.

5. HANDOFF

Return:
- report.md: concise behavior change, affected files, measured checks,
  remaining limitations and next gate.
- result.json: machine baseline/post-state identities, actual commands,
  exits/results, evidence references and mutation boundaries.
- task.diff, recoverable pre-edit bytes or authenticated immutable
  references, and relevant original test output.

Distinguish:
PREVIEW_CONTAINMENT_LOCAL_RESULT
INDEPENDENT_BOUNDARY_REVIEW
REAL_VSCODE_FILESYSTEM_WRITE_VERIFIED
ORIGINAL_PRODUCT_WRITE_FIX_VERIFIED

After successful local checks, use:
STATUS: LOCAL_CHECKED_AWAITING_INDEPENDENT_BOUNDARY_REVIEW
REAL_VSCODE_FILESYSTEM_WRITE_VERIFIED: NO
ORIGINAL_PRODUCT_WRITE_FIX_VERIFIED: NO

Next gate is an independent review of this exact delta and affected
interfaces. Successful review then permits planning a separately bounded
guarded-write smoke with a fresh preview, an exact temporary consumer
root/write set, and a genuine filesystem route.

Do not solve the test-mode activation limitation by silently enabling
write tools or replacing a no-op stub and calling that installed evidence.

Stop after delivering the reviewable result.
