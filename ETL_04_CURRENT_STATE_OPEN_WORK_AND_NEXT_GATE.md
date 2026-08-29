# ETL Framework Extension — Current State, Open Work, and Next Gate

## 1. Current state as of 2026-08-29

The functional Repair 13 work is complete enough for independent package review. The `0.3.146` VSIX was built and independently verified by explicit path. The current blocker is the **source-governance framework**, not the VSIX payload or the ETL parser behavior.

Two governance defects remain:

1. **Create-only VSIX exception cannot be expressed safely.** `**/*.vsix` is protected. `VERSION_AND_PACKAGE` is supposed to create exactly one new versioned artifact, but the manifest/verifier model only checks that an exception exists and does not enforce change kind, exact artifact count, or derived identity.
2. **Certification provenance can be missing or ambiguous.** `etl-release-verifier` participates in both production/version-package and exact package verification. Existing checkpoint enforcement can allow a PASS when producer provenance is missing, and raw display-name comparisons are insufficient to prevent alias-based self-certification.

## 2. Why the last repair stopped

The attempted governance repair was initially limited to five paths. Investigation proved:

- Decision A is implementable in those five paths;
- Decision B requires the checkpoint emitter/enforcer and its tests/static validation;
- project rules required stopping before partial edits because a correct atomic result crossed the authorized boundary.

The task changed zero repository files and preserved all VSIX artifacts byte-identically.

## 3. Required eight-file boundary for the next atomic repair

Authorize only these paths:

1. `.github/agent-governance/process-manifest.json`
2. `.github/agent-governance/schemas/process-manifest.schema.json`
3. `scripts/agent-governance/verify-change-boundary.mjs`
4. `scripts/agent-governance/tests/change-boundary-adversarial.test.mjs`
5. `scripts/agent-governance/tests/manifest-registry.test.mjs`
6. `scripts/agent-governance/emit-checkpoint.mjs`
7. `scripts/agent-governance/tests/checkpoint-fidelity.test.mjs`
8. `scripts/agent-governance/validate-customizations.mjs`

No package version, VSIX artifact, product source, consumer Agent file, test registration file, prompt, workspace, install state, Git commit, or push belongs in this task.

## 4. Decision A acceptance contract — safe create-only VSIX lifecycle

The manifest/schema/verifier must support and enforce a narrow stage exception whose semantics are machine-derived, not prose-only:

- allowed change kind is exactly `CREATED`;
- at most/exactly one new artifact as required by the stage;
- zero existing VSIX files may be content-changed, replaced, removed, or renamed;
- artifact filename is derived from current package identity/version;
- archive manifest identity and version agree with `package.json`;
- the new file must match the exact expected `databricks-etl-copilot-<version>.vsix` identity;
- a separate authorization token is required when declared;
- no other stage inherits the exception;
- the generic `**/*.vsix` protection remains fail-closed.

Required negative tests include:

- no exception;
- wrong stage;
- wrong/missing token;
- wrong filename;
- wrong version;
- wrong Extension ID;
- two new VSIX files;
- content change to an existing VSIX;
- replacement, removal, or rename of an existing VSIX;
- a non-VSIX protected-path regression control.

The control case must prove the change narrows a safe lifecycle and does not weaken the guard.

## 5. Decision B acceptance contract — producer/reviewer independence

Checkpoint and static governance must fail closed when:

- producer identity is absent;
- provenance is malformed or wrong-typed;
- producer and reviewer resolve to the same canonical actor;
- different display names or aliases resolve to the same actor;
- the verifier certifies an artifact it produced;
- session separation is absent or ambiguous where required;
- the configured ownership model makes independent certification impossible.

Trust must not depend only on a user-facing display string. Actor identity needs one canonical machine representation with aliases normalized before comparison.

The repair must preserve:

- distinct implementation/review sessions;
- no new Agent and no authority broadening;
- existing valid independent-review and package-verification routes;
- existing major/blocker findings unless a test proves the new model correctly replaces them;
- a single enforcement system rather than parallel contradictory policy logic.

## 6. Required validation order

1. Identity gate and concurrent-agent check.
2. Independent full-tree and protected-path baseline.
3. Focused manifest/schema validation.
4. Adversarial change-boundary tests.
5. Checkpoint fidelity tests, including mutation/negative controls.
6. Customization/static governance validation.
7. Governance suite and registration checks.
8. Compile, compile-test, and lint if the canonical scripts require them.
9. Repair 11/12/13 and package asset byte-lock regressions.
10. Full unit suite with failures reconciled by exact identity.
11. Independent post-edit boundary proof.
12. Separate independent review in a new session.

Do not rebuild, replace, or reinstall the VSIX in the governance-repair session unless a later owner-approved task explicitly authorizes it.

## 7. Gate sequence after governance repair

```text
Eight-file governance repair
→ independent governance review
→ exact package-lifecycle verification against the existing or freshly authorized artifact
→ owner decision on remaining F1/F3 protected customization failures
→ clean package candidate from exact reviewed state
→ separate local install and activation
→ consumer Runtime QA
→ negative runtime matrix
→ commit/push/PR decision
→ SIT decision
→ public 1.x readiness work
```

## 8. Runtime QA still outstanding

Even after governance becomes green, Runtime QA must separately prove:

- exact `0.3.146` Extension Host activation;
- consumer Agent discovery and dynamic delegation;
- Repair 13 Markdown/structured parity through the installed public seam;
- Preview/approval/write/replay lifecycle;
- wrong/expired/replayed Preview IDs;
- changed root/path/bytes/artifact set;
- zero/multi/protected workspace roots;
- symlink/junction/TOCTOU escape;
- unsupported direct Unity Catalog target;
- no external runtime side effects without Operator approval.

## 9. Other open and deferred work

### Release-critical or pre-merge

- resolve F1 and F3 through an explicit protected-path/governance decision;
- ensure all important focused suites are in canonical registration;
- harden VSIX selection to current source version/freshness;
- capture exact final changed-path inventory;
- cleanly separate unrelated working-tree content;
- run final Git/CI/package evidence from the exact commit candidate;
- no public release until the `1.x` contract, documentation, compatibility, and support matrix are complete.

### Product/security backlog

- fail closed at guard level when a trusted Framework contract is unavailable;
- redesign advisory context provenance and skill scoping;
- complete provider output contracts and runtime evidence;
- decide and implement direct Unity Catalog write support if desired;
- modernize remaining legacy authorization models;
- improve STTM heading aliases and diagnostics;
- clean stale VSIX artifacts under a separate authorized task.

## 10. Current terminal markers

```text
REPAIR_13_STRUCTURED_DIAGNOSTICS_COMPLETE: YES
PHASE_H_REFRESH_COMPLETE: YES
INDEPENDENT_REVIEW_COMPLETE: YES
VERSION_0_3_146_BUILT: YES
EXACT_PACKAGE_ARTIFACT_VALID: YES
PACKAGE_LIFECYCLE_GOVERNANCE_COMPLETE: NO
CERTIFICATION_PROVENANCE_COMPLETE: NO
LATEST_GOVERNANCE_REPAIR_CHANGED_FILES: 0
READY_FOR_LOCAL_INSTALL: NO
READY_FOR_RUNTIME_QA: NO
READY_TO_COMMIT_OR_PUSH: NO
READY_FOR_SIT: NO
READY_FOR_PUBLIC_RELEASE: NO
```

