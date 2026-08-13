Task: LOCAL-PHASE-A1A-20260813-01-RESUME-01

Resume the blocked LOCAL-PHASE-A1A-20260813-01 task from its current checkpoint.

All prior constraints, protected paths, lifecycle requirements, 19-item executable coverage matrix, isolated A/B validation requirements, and prohibitions remain in force.

Do not click Keep or Undo. Do not start Phase A1B.

Exact scope expansion

Authorize exactly one additional production file:

TrustedCreatePreviewService.ts

Resolve and report its unique canonical path under src/** before editing.

This is the sixth and final additional A1A production file. No seventh production file is authorized. The previously authorized test-file budget is unchanged.

If this file is absent or ambiguous, or another production/helper file is required, stop with:

LOCAL_PHASE_A1A_BLOCKED

Mandatory pre-edit proof

Before making any edit:

1. Revalidate repository, origin, branch, HEAD, worktrees, staged state, package versions, candidate VSIX hash, protected-file hashes, and the current pending changed-file manifest.
2. Prove that TrustedCreatePreviewService is the canonical owner of environment selection and intended artifact-path derivation.
3. Print the proposed preflight method signature and its exact callers.
4. Show the dependency/import graph remains acyclic.
5. If the implementation would introduce a circular dependency, dynamic-import workaround, service locator, or duplicated path logic, stop and request explicit scope expansion.
6. Confirm no unexpected file has changed.

Authorized implementation

Refactor TrustedCreatePreviewService.ts only enough to expose a pure, deterministic, side-effect-free preflight descriptor API.

The descriptor must be derived from explicit immutable inputs, including:

* trusted selected workspace and provenance;
* current session/workspace binding;
* canonical STTM identity and SHA-256;
* repository/environment discovery snapshot identity;
* provisional lifecycle route and stable job identity, when available;
* explicit environment selection or grounded environment candidates.

The descriptor must contain:

* descriptorComplete;
* normalized workspace-relative artifact paths;
* artifact kinds;
* canonical contained paths;
* deterministic sorted intended-path-set hash;
* environment-selection outcome;
* environment-candidate-set hash when applicable;
* workspace, STTM, and discovery bindings;
* typed unresolved codes and safety blockers.

It must not contain generated artifact content, preview-validation success, ownership claims, approval state, planningEligible, or applyEligible.

Correct lifecycle order

Avoid a circular routing contract. Use this order:

trusted workspace/STTM/session evidence
→ complete read-only job/environment discovery
→ provisional lifecycle classification
→ pure preflight descriptor
→ collision/ownership inventory over exactly those paths
→ final lifecycle decision
→ derive planningEligible
→ full in-memory preview and validation

Required provisional outcomes remain:

* one stable managed match → update candidate;
* no match in an existing confirmed repository → create candidate;
* explicitly selected empty repository → initialize candidate;
* multiple matches → request explicit job selection;
* unsafe or unknown target → block.

Unmanaged collision is classified after the exact descriptor path set is known and must block before preview.

Purity and safety

The preflight operation must:

* use no process.cwd(), active-editor inference, ambient workspace state, or sample/customer defaults;
* call no RepoWriter, NewArtifactWriter, writeArtifacts, resolveWorkspacePath, writer, or external system;
* perform no filesystem write, directory creation, preview validation, or approval/apply action;
* receive read-only observations as explicit inputs instead of recollecting mutable ambient state;
* never invent paths, environment values, credentials, storage values, write modes, merge keys, onboarding IDs, or business decisions;
* return descriptorComplete: false when any safety-critical path or environment choice is unresolved;
* reject outside-root, extension/install-root, different-drive, UNC escape, .., mixed-separator escape, symlink/junction escape, duplicate-path, and unsafe case-alias outcomes.

A descriptor is only a planning observation. It is not managed-ownership evidence.

applyEligible must remain unconditionally false.

Single path truth and drift protection

There must be one canonical implementation of environment/path derivation.

Prefer that both preflight and full preview call the same internal pure path planner inside TrustedCreatePreviewService.ts. Do not copy the rules into another service.

Before accepting a full preview, verify exact parity for:

* artifact paths and kinds;
* environment-selection outcome;
* environment-candidate-set hash;
* intended-path-set hash;
* workspace binding;
* STTM hash;
* discovery snapshot hash.

Any missing, added, renamed, differently normalized, or differently typed artifact must fail closed with a typed result such as:

BLOCK_PREVIEW_DESCRIPTOR_DRIFT

Collision inspection must receive exactly the descriptor’s canonical path set. No later path may be added silently.

Eligibility boundary

planningEligible: true may be derived only when:

* workspace/session/STTM evidence is trusted and current;
* job and environment discovery are complete;
* the provisional lifecycle route permits planning;
* the descriptor is complete;
* every safety-critical environment choice is resolved;
* collision/ownership inventory covers the exact descriptor path set;
* no unsafe collision or stale evidence exists.

After eligibility, the full preview may render content in memory and validate it, but must remain completely write-free. Descriptor parity must be checked before returning trusted_preview_validated.

Unresolved deployment/business values that do not affect paths or collision safety may remain visible in preview, but must not be invented and must keep apply blocked.

Mandatory executable tests

Within the existing test budget, prove:

1. Complete trusted direct /create evidence reaches trusted_preview_validated.
2. Incomplete, ambiguous, stale, external, or unsafe evidence blocks before full preview.
3. Phase 6 valid direct-create behavior is restored.
4. Golden Corpus acceptance returns to 1.
5. Canonical ABFSS aiFirst.acceptance === true.
6. Existing Phase 6 and Golden expectations are not weakened.
7. Test fixtures use genuine temporary trusted workspaces—not an arbitrary bare C:\workspace.
8. Preflight/full-preview paths and environment outcomes have exact parity.
9. Added, removed, renamed, renormalized, or differently typed paths trigger descriptor-drift blocking.
10. Environment-selection and candidate-set drift are rejected.
11. Collision inspection receives the exact descriptor path set.
12. Unique-environment reuse, deterministic generic scaffold, multiple selection, stale selection, and incomplete discovery are all covered.
13. Repeated/permuted equivalent input produces an identical immutable descriptor and hash.
14. All writer and filesystem-write APIs have executable zero-call assertions.
15. No preview validation occurs when evidence is incomplete.
16. The same immutable evidence identity reaches the executor.
17. Extension/install, mixed separators, UNC, different drive, case alias, symlink, and junction cases are covered.
18. /workflow create remains unchanged and separate.
19. applyEligible === false in every scenario.

Validation

Use only isolated temporary snapshots created from exact git archive HEAD with committed package.json 0.3.139.

Record:

* UNPINNED_TEMP_DEPENDENCY_RESOLUTION;
* Node/npm versions;
* temporary lock hash;
* exact dependency identity;
* A1 → B1 → B2 → A2 results;
* compile/typecheck;
* focused suites;
* broader pure-unit runner;
* Phase 6 and Golden suites;
* all 19 coverage items;
* lifecycle and environment matrices;
* git diff --check;
* independent verifier result.

Both B runs must eliminate the exact three source regressions and introduce no new or changed failure identity relative to both A runs.

Do not modify package/VSIX/install, Git/PR/CI state, real Consumer workspaces, protected dirty files, writers, apply/approval code, packaged assets, or control-plane paths.

Do not click Keep even after success; report whether the pending review card is safe for the user to keep.

Use the original final token set:

* LOCAL_PHASE_A1A_IMPLEMENTED_AND_AB_VERIFIED
* LOCAL_PHASE_A1A_OVERLAY_REGRESSION
* LOCAL_PHASE_A1A_COVERAGE_GAP
* LOCAL_PHASE_A1A_INCONCLUSIVE
* LOCAL_PHASE_A1A_BLOCKED
