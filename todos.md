Task: LOCAL-PHASE-A1B-SLICE1-BOUNDED-REPAIR-20260813-01

Mode: bounded local source-and-test repair.

Goal: repair the defects found by the independent Slice-1 audit. Do not start Slice 2, integrate the new layout modules into existing producers, or resolve the disputed ETL path contracts.

Non-negotiable controls

* Do not click Keep or Undo.
* Do not stage, commit, push, merge, rebase, switch branches, edit a PR, or invoke CI.
* Do not build/package/install/uninstall a VSIX.
* Do not modify any Consumer workspace or external system.
* Do not modify .github/**, workflow/**, AGENTS.md, COPY_ORDER.md, the four protected user-owned dirty files, or any existing ETL path producer.
* Preserve the nine-file A0R overlay except for the explicitly authorized single test-registration line in testPatterns.ts.
* All executable validation must run in isolated temporary snapshots created from git archive HEAD plus the exact authorized overlay.
* If any required repair needs another production file, stop and report the exact scope expansion. Do not improvise.

Step 1 — Revalidate identity and pending scope

Before editing, report:

* repository root and origin;
* branch feature/v3-agentic-redesign;
* HEAD b2e44c3a1a051aa7fa6008831d225bc06d22e847;
* staged count;
* exact current pending-path manifest;
* hashes of the nine A0R files;
* hashes of the four protected dirty files;
* hashes of the three Slice-1 files;
* hash of TrustedCreatePreviewService.ts;
* candidate VSIX path/hash and installed version.

Confirm the review card, Git state, protected files, VSIX and Consumer workspaces are unchanged.

Authorized mutation scope

Production:

1. src/core/artifacts/layout/EtlArtifactLayout.ts
2. src/core/artifacts/layout/ArtifactPathNormalizer.ts

Tests:

3. src/test/suite/etlArtifactLayoutParity.test.ts
4. The unique canonical testPatterns.ts, only to add the exact pure-unit registration entry:
    **/etlArtifactLayoutParity.test.js

Phase-H baseline:

5. The unique generated Phase-H tracked-input baseline artifact may be regenerated only if all of the following are proven:
    * the change is deterministic;
    * it records only the addition/change of the Slice-1 tracked production inputs;
    * no evaluator logic, tracking pattern, threshold or expected product behavior is changed;
    * no unrelated existing failure is hidden or waived;
    * the exact before/after baseline delta is reported.

If Phase-H repair requires changing EvalGovernance.ts, evaluation logic, a protected control-plane file, or an unidentified additional file, stop with SCOPE_EXPANSION_REQUIRED.

No other file is authorized.

Required repairs

D1 — Mutable registry escape

Repair the runtime immutability defect in EtlArtifactLayout.ts.

The exported registries and every nested entry must be deeply immutable at runtime, not merely typed readonly or shallow-frozen.

Requirements:

* callers cannot mutate registry entries, nested arrays or nested objects;
* formulasForFamily, formulasForIds, conflict lookup and unresolved-result functions must not expose shared mutable state;
* modifying or attempting to modify one returned value must never change a later call;
* prefer deep runtime freezing and/or deep defensive copies;
* preserve deterministic ordering;
* do not introduce mutable global caches.

Add executable tests proving:

* registry array frozen;
* each entry and nested value frozen or defensively isolated;
* mutation attempts cannot alter module state;
* a second and later call remains byte/deep-equal to the original result.

D2 — Result immutability

Ensure results from normalizeRelativeArtifactPath and other new public Slice-1 APIs are runtime immutable or defensively copied, including nested segments, observed formulas, conflicts and unresolved metadata.

Add explicit mutation-leak regression tests.

D3 — Windows-safe normalization and collision identity

Repair the Windows filename-alias security defect without weakening POSIX behavior.

Use explicit platform semantics. Do not rely on process.platform, process.cwd, active editor or ambient workspace state.

For win32:

* reject or safely canonicalize trailing-dot aliases;
* reject or safely canonicalize trailing-space aliases;
* reject Windows reserved device names case-insensitively, including names with extensions such as CON.txt;
* reject NTFS alternate data stream syntax;
* reject drive-relative, drive-absolute, UNC, extended/device and absolute inputs where a relative artifact path is required;
* prevent prefix confusion;
* case-fold collision keys consistently;
* preserve drive/share boundaries for containment checks.

For posix:

* do not unconditionally case-fold;
* A.json and a.json must remain distinct;
* do not apply Windows reserved-name or trailing-dot rules as though POSIX were Windows.

Percent-encoded strings are filesystem path text, not URLs. Do not decode them implicitly; document and test this behavior.

Keep lexical containment explicitly separate from realpath/symlink/junction containment. Do not claim lexical checks prove filesystem containment.

Add adversarial executable tests for every case above, including duplicate detection.

D4 — Provenance correctness

Repair the planTransformationIncludePath provenance mismatch for the sql/ascend2/** branch.

The returned provenance must agree exactly with the registered formula provenance. Add a test that asserts the provenance field, not only the path.

Do not introduce fixture/sample/customer-specific provenance.

D5 — PatchPlanner environment parity

The current producer applies its observed catalog ?? "common" behavior, while the Slice-1 formula requires input and the test manually supplies "common".

For the specific observed PatchPlanner formula:

* reproduce the existing producer behavior exactly;
* test the omitted-catalog case directly against the producer;
* keep the broader environment_config_create family conflict unresolved;
* do not select this producer as the canonical product contract;
* do not turn "common" into a general runtime default outside this formula-specific parity representation.

D7 — Parity coverage gaps

Extend the focused suite with direct, non-circular parity coverage for:

* BlueprintBuilder.resolveIncludePath;
* resolved ArtifactPatchPlanner.suggestSqlPath;
* split EXTRACT/LOAD behavior from ArtifactGenerationPipeline;
* onboarding default, naming override and entity fallback from the real producer;
* exact artifact/formula IDs, provenance and unresolved codes.

Use isolated fakes where required. Do not invoke AI, writers, filesystem writes or external services.

Expected values must not be computed by the same new helper being tested.

Test registration

Add exactly one entry to PURE_UNIT_TEST_PATTERNS:

**/etlArtifactLayoutParity.test.js

Prove that:

* exactly one compiled suite is selected;
* the suite moves from integration discovery to pure-unit discovery;
* it is not executed twice;
* Windows/POSIX glob behavior is valid;
* no other suite registration changes.

Phase-H tracked-input baseline

Identify the exact deterministic baseline affected by the two new production files.

Regenerate only the legitimate Slice-1 tracked-input delta. Report:

* old and new tracked files/count;
* old and new digest;
* exact added/changed paths;
* proof no path was removed unexpectedly;
* proof evaluator logic and thresholds are unchanged.

If this cannot be done without masking an unrelated baseline failure, leave it unchanged and return SCOPE_EXPANSION_REQUIRED.

Preserve fail-closed behavior

Do not resolve or choose among:

* the two primary_job_config formulas;
* the three environment_config_create formulas;
* .sql versus .yaml transformation suggestion;
* families with no authoritative producer.

They must continue returning stable explicit unresolved codes such as:

* CONTRACT_DECISION_REQUIRED
* NO_AUTHORITATIVE_PRODUCER
* FORMULA_NOT_APPLICABLE
* MISSING_REQUIRED_INPUT

No implicit formula, sample convention, customer name or runtime default may be selected.

The Slice-1 modules must remain additive leaf components:

* no imports from RepoWriter, renderer, preview, router, executor or Copilot runtime;
* no filesystem write;
* no AI/model/prompt/network;
* no clock/random/global mutable state;
* no dependency cycle.

Isolated validation

Use one identical temporary dependency seed for all comparison snapshots.

Run:

1. clean HEAD baseline twice;
2. nine-file A0R overlay baseline;
3. repaired A0R + Slice-1 overlay;
4. repaired overlay with canonical test registration and permitted Phase-H baseline update.

For the repaired overlay run:

* TypeScript compile;
* lint;
* directly focused Slice-1 suite;
* canonical registered pure-unit runner;
* directly affected producer suites;
* adversarial normalizer/security suite;
* deterministic repeated/permuted-input tests;
* git diff --check;
* static and executable zero-I/O/zero-writer/zero-AI checks.

Compare full failure identities:

* full test title;
* error class and message;
* first meaningful stack frame.

Acceptance requires:

* all repaired Slice-1 tests pass;
* canonical runner executes the new suite exactly once;
* D1 and D3 probes no longer reproduce;
* no new failure identity relative to the corresponding baseline;
* the known A0R Phase6/Golden failures are neither hidden nor “fixed” by weakened expectations;
* no existing test expectation is weakened;
* no mutation outside the authorized files;
* real worktree, review card, protected hashes, Git/PR/CI, VSIX and Consumer workspaces remain unchanged except for the authorized pending source/test edits.

Final report

Report:

* exact files changed and hashes;
* defect-by-defect repair evidence;
* registration proof;
* Phase-H baseline disposition;
* focused and canonical test results;
* baseline/overlay failure-signature comparison;
* remaining gaps;
* independent-verification recommendation.

Do not click Keep after success. A fresh independent read-only re-audit is still required before acceptance.

End with exactly one:

* LOCAL_PHASE_A1B_SLICE1_REPAIR_READY_FOR_INDEPENDENT_REAUDIT
* LOCAL_PHASE_A1B_SLICE1_REPAIR_SCOPE_EXPANSION_REQUIRED
* LOCAL_PHASE_A1B_SLICE1_REPAIR_FAILED
* LOCAL_PHASE_A1B_SLICE1_REPAIR_BLOCKED
