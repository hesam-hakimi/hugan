Implement one surgical W1 follow-up: close only the canonical destination-path alias gap found by the final acceptance review.

Context

normalizeRelPath in src/tools/TrustedWriteApprovalStore.ts supplies identity normalization for inventory deduplication, approval checksums/storage, and drift comparison.

It currently leaves interior . components and repeated separators intact. Consequently:

* sql/x.yaml
* sql/./x.yaml
* sql//x.yaml

can become distinct inventory keys even though filesystem resolution targets the same file.

With conflicting content, this permits ambiguous last-write-wins behavior within one approved operation. This contradicts the W1 collision-protection acceptance criteria.

Preserve the current dirty worktree. Do not discard or recreate any existing W1 change.

Required change

Make those valid relative-path spellings share one canonical identity.

* Extend only the existing normalizeRelPath implementation, or an immediately adjacent private helper if strictly necessary.
* Remove path components that are exactly . at any depth.
* Collapse repeated separators between relative-path components.
* Preserve existing case folding, backslash handling, and leading-./ behavior.
* Preserve valid dotted names such as:
    * .env
    * x..yaml
    * a.b
* Keep one shared normalization path.
* Do not add call-site-specific normalization.

Security invariants

* Do not use path.resolve, path.normalize, or another operation that consumes ...
* Do not turn absolute, UNC, device, or drive-letter paths into relative paths by stripping root markers.
* .., absolute paths, UNC paths, device paths, and drive-letter paths must remain hard-rejected.
* Detect invalid rooted forms before removing empty or dot components.
* Do not modify physical-containment behavior.
* Do not modify PathValidator, PhysicalPathContainment, WorkspaceDestinationProbe, or RepoWriter.

Required tests

Add focused regressions only in:

src/test/suite/workspaceWriteCollision.test.ts

Use existing helpers and real temporary filesystem behavior where appropriate.

Test 1 — identical aliases

Prove that these paths with identical bytes and matching metadata collapse into one canonical inventory destination and cause one physical write:

* sql/x.yaml
* sql/./x.yaml
* sql//x.yaml
* an equivalent backslash or case variant

Test 2 — conflicting aliases

Cover both interior-dot and repeated-separator aliases with different bytes.

They must:

* be recognized as one physical destination;
* trigger the existing conflict error;
* fail before preview or confirmation;
* fail before approval;
* produce zero filesystem writes.

Test 3 — dotted filenames

Prove that only components exactly equal to . are removed.

These names must remain valid and distinct:

* .env
* x..yaml
* a.b

Test 4 — invalid rooted paths remain rejected

Confirm that this change does not make any of these acceptable:

* ..
* absolute paths
* UNC paths
* device paths
* drive-letter paths

Reuse existing coverage where possible and add only the smallest missing assertion.

Testing integrity

* Test through the public inventory or write flow.
* Do not export a production-private function only for testing.
* Do not derive both expected and actual results from the same normalization helper.
* Do not add skipped, exclusive, or tautological tests.
* Do not weaken existing assertions.

Strict edit boundary

Only these files may be modified:

* src/tools/TrustedWriteApprovalStore.ts
* src/test/suite/workspaceWriteCollision.test.ts

Do not modify src/core/artifacts/ArtifactDestinationInventory.ts; it already consumes the shared identity helper.

If another production file is genuinely required, stop without editing it and explain why.

Prohibited scope

Do not:

* refactor unrelated code;
* reformat unrelated regions;
* add dependencies;
* change packages or versions;
* alter approval UI or checksum design beyond the required alias equivalence;
* refresh evaluation baselines;
* change CI, workflows, prompts, or documentation;
* implement atomic multi-file apply;
* implement rollback or managed ownership;
* address broader TOCTOU concerns;
* stage, commit, or push.

Verification

Run these commands:

git diff --check
npm run compile

Then run the narrowest supported command for:

workspaceWriteCollision.test.ts

Finally, run exactly once:

npm run test:unit

Requirements:

* Compilation passes.
* Every existing and new workspace-write collision test passes.
* No workspace-write test fails.
* Report the known EvalGating freshness failures separately.
* Report the three existing Copilot customization failures separately.
* Do not fix or suppress those known failures.

Final report

Report:

* exact files changed;
* exact normalization behavior added;
* new test names and results;
* each command and exit code;
* full unit-test totals;
* complete names of remaining failures;
* git diff --check result;
* final git status --short;
* confirmation that nothing was staged, committed, pushed, or baseline-refreshed.

Return exactly one verdict:

W1_ALIAS_FIX_READY_FOR_FINAL_GATE

or:

W1_ALIAS_FIX_BLOCKED

Stop after reporting.
