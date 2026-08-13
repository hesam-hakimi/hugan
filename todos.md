Task: LOCAL-PHASE-A1B-SLICE1-INDEPENDENT-AUDIT-20260813-01

Mode: independent read-only audit
Delivery: report-only
Mutation authorization: NONE
Slice 2: PROHIBITED

Independently audit Slice 1 before it is accepted.

Expected Slice 1 scope

The pre-existing nine-file A0R review-card overlay must remain byte-identical.

Exactly these three files were reportedly added:

1. src/core/artifacts/layout/EtlArtifactLayout.ts
2. src/core/artifacts/layout/ArtifactPathNormalizer.ts
3. src/test/suite/etlArtifactLayoutParity.test.ts

Do not trust these claims without verification.

Hard boundaries

* Do not click Keep or Undo.
* Do not edit any real file, including testPatterns.ts.
* Do not begin or design Slice 2.
* Do not resolve disputed canonical path formulas.
* Do not change tests or expectations.
* Do not perform Git, PR, CI, package, VSIX, installation, Consumer-workspace, or external actions.
* Any compilation or test must run only in disposable snapshots created from git archive HEAD.

1. Identity and exact scope

Verify repository, origin, branch, exact HEAD, worktrees, staged state, package versions, VSIX identity and all protected hashes.

Reconcile:

* the UI statement suggesting “Created 4 files”;
* the reported three-file Slice 1 table;
* actual filesystem and git status evidence.

Confirm there is no hidden fourth file or modification to an existing production file.

2. Layout-contract audit

Audit every export in EtlArtifactLayout.ts.

For each path formula, trace the real current producer and prove exact parity with:

* RepoWriter.generatePaths
* ArtifactPatchPlanner
* ArtifactGenerationPipeline
* EnvConfigRenderer
* BlueprintBuilder
* IncludeFileRenderer
* onboarding generation

Verify directory, filename, sanitizer, lowercasing, suffix, environment segment and .yaml versus .yml.

Confirm disputed formulas remain fail-closed:

* primary_job_config
* environment_config_create
* transformation_sql_suggestion

They must return explicit unresolved results unless an exact formula ID is supplied.

Confirm no formula is invented for:

* common_shared_config
* declared_tabular_output
* managed_ownership_marker

3. Path-normalizer security audit

Audit and execute tests for:

* POSIX, Windows and mixed separators;
* empty and NUL paths;
* . and ..;
* absolute and drive-relative paths;
* drive mismatch;
* UNC and extended Windows paths;
* case aliases;
* trailing dot/space aliases and Windows reserved names;
* C:\foo versus C:\foobar;
* duplicate destinations;
* symlink/junction escape using the injected realpath resolver.

Confirm lexical normalization is not presented as proof of filesystem or symlink containment.

4. Purity and dependency audit

Prove both production modules are deterministic leaf components with:

* no filesystem write or directory creation;
* no RepoWriter, renderer mutation or preview dependency;
* no process.cwd() or ambient workspace;
* no AI/model, time, randomness, network or global mutable state;
* no import, runtime or semantic cycle;
* immutable or defensively copied outputs.

5. Test-quality audit

Inspect etlArtifactLayoutParity.test.ts.

Map every production path formula and every security case to an exact test title.

Reject circular assertions where expected values come from the same new registry/helper being tested.

Classify each required behavior as:

* COVERED
* PARTIAL
* GAP
* INVALID_ASSERTION

6. Test registration decision

Determine whether the registered runner uses PURE_UNIT_TEST_PATTERNS and whether the new test is currently omitted.

Evaluate this exact proposed entry without applying it:

**/etlArtifactLayoutParity.test.js

Prove whether it:

* selects exactly one compiled suite;
* works on Windows and POSIX;
* causes no duplicate execution;
* changes test discovery only.

Return one decision:

* APPROVE_EXACT_TEST_REGISTRATION_SCOPE_EXPANSION
* REGISTRATION_ALREADY_EFFECTIVE_NO_CHANGE_REQUIRED
* REJECT_PROPOSED_REGISTRATION_PATTERN
* REGISTRATION_DECISION_INCONCLUSIVE

7. Isolated verification

Using one identical temporary dependency seed, create:

* B0: HEAD plus exactly the nine pre-Slice-1 A0R files;
* B1: B0 plus exactly the three Slice 1 files;
* B1R: B1 plus a temporary hypothetical one-line registration change.

Do not include the four protected user-owned dirty files.

Run:

* TypeScript test compilation;
* focused Slice 1 suite;
* registered canonical runner;
* test-discovery enumeration;
* directly affected suites;
* git diff --check.

Compare full test titles, error types, messages and first meaningful stack frames—not only counts.

Acceptance requires:

* B0 and B1 have identical broader failure signatures;
* focused Slice 1 tests pass;
* B1R registers the new suite exactly once;
* B1R introduces no new failure;
* no expectation is weakened.

Final report

Report:

1. exact scope and hashes;
2. “four created” versus three-file reconciliation;
3. formula/producer parity table;
4. unresolved-conflict table;
5. normalizer security matrix;
6. purity/dependency result;
7. test-quality matrix;
8. B0/B1/B1R results;
9. exact registration decision;
10. any defect with file and symbol evidence;
11. proof that the real worktree and review card remained unchanged.

End with exactly one token:

* LOCAL_PHASE_A1B_SLICE1_AUDIT_PASS_REGISTRATION_APPROVED
* LOCAL_PHASE_A1B_SLICE1_AUDIT_PASS_NO_REGISTRATION_CHANGE
* LOCAL_PHASE_A1B_SLICE1_AUDIT_FAIL
* LOCAL_PHASE_A1B_SLICE1_AUDIT_INCONCLUSIVE
* LOCAL_PHASE_A1B_SLICE1_AUDIT_BLOCKED
