LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_2 — IMPLEMENT FINAL CONTAINMENT HARDENING

Continue the SAME existing Repair-5 task.

Authoritative read-only discovery completed with:

CURRENT_REPAIR_5_BYTES_PRESERVED: YES
CURRENT_COMPILE_RESULT_RETAINED_AS_EXTERNAL_EVIDENCE: PASS
CURRENT_LINT_RESULT_RETAINED_AS_EXTERNAL_EVIDENCE: PASS
CURRENT_FULL_UNIT_BASELINE: 1890_PASSING_5_PENDING_5_HISTORICAL_FAILING
DANGLING_LINK_REPAIR_REQUIRED: YES
POSIX_CASE_CONTAINMENT_REPAIR_REQUIRED: YES
COMPETING_ROUTE_REPAIR_REQUIRED: NO
EXPLAIN_FIXTURE_REPAIR_REQUIRED: YES
ADDITIONAL_PRODUCTION_FILES_REQUIRED: 0
ADDITIONAL_TEST_FILES_REQUIRED: 0
SHARED_SECURITY_PRIMITIVE_SCOPE_REQUIRED: NO
REPAIR_5_AMENDMENT_2_SCOPE_FROZEN: YES
LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_2_DISCOVERY_COMPLETE

Do NOT restart Repair 5.

Do NOT undo, revert, discard, reconstruct, or replace already-valid Repair-5 work.

This amendment completes the remaining verified defects inside the already-authorized 11-file universe.

⸻

1. EXACT FILES AUTHORIZED FOR THIS AMENDMENT

Modify only these three already-authorized files:

src/writers/RepoWriter.ts
src/test/suite/repoWriterWorkspaceSelection.test.ts
src/test/suite/configExplain.test.ts

All other existing Repair-5 candidate files must remain byte-identical during this amendment.

No new files.

If any fourth file is required, STOP before editing and return:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

⸻

2. FINDING A — DANGLING LINK CONTAINMENT

The read-only discovery classified this as:

PRODUCTION_SECURITY_DEFECT

Current behavior:

* PathValidator provides lexical validation.
* RepoWriter’s physical containment resolution walks upward using existence checks.
* existsSync follows links.
* For a dangling symlink, existsSync returns false.
* The resolver may therefore skip the dangling filesystem object and canonicalize an ancestor instead.
* A path such as:
    consumerRoot/docs/file.md
    → symlink to
    outside/missing.md
    can potentially pass containment even though the subsequent filesystem write follows the link outside consumerRoot.

This can affect all repaired routes that depend on the shared RepoWriter physical containment behavior.

⸻

3. REQUIRED DANGLING-LINK REPAIR

Repair only the shared physical containment implementation already located in:

src/writers/RepoWriter.ts

Specifically harden the existing:

resolveContainedWorkspacePath(...)

or the exact current equivalent identified by live source.

Requirements:

1. The ancestor walk must detect filesystem objects themselves, including symbolic links/reparse entries, rather than treating a dangling link as nonexistent merely because its target cannot be resolved.
2. Use an lstat-aware existence/object check for the ancestor walk.
3. If the candidate path or an ancestor contains a symlink/reparse object whose resolved target cannot be safely canonicalized, FAIL CLOSED.
4. A dangling link must never be skipped in favor of canonicalizing its parent.
5. If realpath of the encountered link fails, the destination is invalid.
6. If a link resolves outside canonical consumerRoot, the destination is invalid.
7. Do not follow the unsafe path into the write.
8. Preserve valid in-root symlink behavior only when the resolved physical destination is still contained under the canonical consumerRoot.
9. Do not weaken the existing lexical/path-shape validation.
10. Do not modify PathValidator.ts.

⸻

4. DANGLING-LINK SECURITY INVARIANT

Immediately before a write is considered safe:

logical approved relative path
+
canonical consumerRoot
+
physical filesystem topology

must all resolve to a physical destination contained under the same consumerRoot.

A dangling link or unresolved reparse/symlink target must produce a blocked/fail-closed result.

Never interpret:

cannot realpath link

as:

ignore link and continue with parent

⸻

5. FINDING B — POSIX CASE-SENSITIVE CONTAINMENT

The read-only discovery classified this as:

PRODUCTION_SECURITY_DEFECT

Current behavior in RepoWriter’s physical containment comparison:

normalized paths are lowercased unconditionally

That is acceptable for the normal Windows path-identity model but incorrect on a case-sensitive POSIX filesystem.

Example:

/ConsumerRoot/file
/consumerroot/file

must not automatically be treated as the same physical root on Linux/macOS.

⸻

6. REQUIRED PLATFORM-SENSITIVE NORMALIZATION

Modify the existing RepoWriter path normalization/comparison logic only.

Required behavior:

Windows

Case-insensitive comparison remains supported.

Equivalent casing variations may normalize for comparison.

Non-Windows / POSIX

Preserve path case.

Do NOT lowercase canonical filesystem paths.

A case-distinct sibling must not be accepted as a descendant.

Use the runtime platform identity already available in Node, e.g. the established repo convention around:

process.platform === 'win32'

or the exact existing platform helper if one is already used in this file.

Do not introduce a second platform abstraction merely for this repair.

⸻

7. POSIX SECURITY INVARIANT

On a case-sensitive platform:

/consumerRoot

must NOT contain:

/ConsumerRoot/outside

merely because their lowercase strings match.

Physical containment must respect the filesystem’s path identity semantics.

⸻

8. REQUIRED REPOWRITER REGRESSION TESTS

Modify:

src/test/suite/repoWriterWorkspaceSelection.test.ts

Add behavioral regression coverage for both production security defects.

T1 — dangling in-root final-file link to outside missing target

Construct the equivalent topology:

consumerRoot/
  docs/
    file.md -> outsideRoot/missing.md

Attempt to resolve/write the logical consumer path.

Assert:

* destination is rejected;
* outside file is not created;
* resolver does not skip the dangling link and accept its parent;
* consumerRoot containment fails closed.

Exercise the real shared RepoWriter containment implementation.

Do not merely assert source text contains lstat.

T2 — dangling link ancestor

Also cover a dangling symlink/reparse entry in an ancestor directory position if the actual resolver permits such a path shape.

Assert fail closed.

T3 — valid physical path regression

A normal non-linked in-root destination remains accepted.

T4 — valid in-root link, if supported by current contract

If the product currently permits a symlink whose physical destination remains inside consumerRoot, verify it remains contained and safe.

Do not add this behavior if current contract intentionally rejects all links.

Follow live-source behavior.

T5 — POSIX case-distinct sibling

On a case-sensitive platform, prove that a case-distinct sibling/root cannot pass physical containment solely because lowercased strings match.

Do not weaken the test on Windows.

If a real cross-platform filesystem fixture cannot deterministically demonstrate POSIX semantics on the Windows developer machine, use the smallest existing injectable/platform-test seam that exercises the actual RepoWriter normalization/comparison function.

Do NOT alter production behavior merely to make the test injectable.

Do NOT silently skip the security assertion without an equivalent deterministic unit-level proof.

T6 — Windows regression

Confirm Windows case-insensitive behavior remains unchanged.

⸻

9. LINK TEST ENVIRONMENT DISCIPLINE

Symlink creation may have host-specific restrictions.

Tests must remain deterministic.

Preferred order:

1. Use actual filesystem symlinks where supported in the test environment.
2. Reuse an existing filesystem/test seam if the repository already has one.
3. If a host cannot create the required symlink due to permissions, use a narrowly scoped test double around filesystem metadata resolution that still exercises the real RepoWriter containment algorithm.

Do not:

* disable the test globally;
* mark the security test permanently pending;
* weaken it into a source-text assertion;
* require administrator privileges as the only test strategy.

Always restore any filesystem stub in finally / teardown.

⸻

10. FINDING C — COMPETING ROUTES

Discovery classified this as:

NON_BLOCKING_DEBT

No Repair-5 change is authorized for this item.

Do not modify routing precedence.

Do not modify ETLChatParticipant for this finding.

Record as follow-up debt only.

Reason established by discovery:

* only one route dispatches per request;
* route-owned approval IDs cannot be cross-consumed;
* WriteAuthorization rejects wrong/mismatched preview state;
* no approval bypass was found;
* issue is conversational precedence/stale-state UX, not unauthorized write capability.

⸻

11. FINDING D — EXPLAIN TEMP FIXTURE ISOLATION

Discovery classified this as:

TEST_HARNESS_DEFECT

Production impact:

NONE

Repair only:

src/test/suite/configExplain.test.ts

Current problem:

* tests use fixed paths under os.tmpdir();
* concurrent runs may collide;
* a crashed run may leave stale files/links;
* one test teardown may remove another run’s fixture;
* stale state can contaminate evidence.

⸻

12. REQUIRED EXPLAIN FIXTURE REPAIR

Replace fixed shared temp roots with unique per-test/per-run fixtures using an equivalent of:

fs.mkdtempSync(...)

under the platform temporary directory.

Requirements:

* each test gets a unique base directory;
* derive Explain consumer/output roots beneath that unique base;
* cleanup only that test’s own base;
* teardown must be resilient;
* no stale fixture is reused;
* no global/fixed temp root shared between parallel runs;
* no production code change.

Do not create a new test file.

⸻

13. PRESERVE CURRENT REPAIR-5 CONTRACT

Before completing this amendment, confirm the already-implemented Repair-5 behavior remains intact:

* Explain trusted preview → approval → write;
* Explain root/path/content drift rejection;
* Explain replay rejection;
* Artifact Reuse preview → approval → create/patch;
* Artifact Reuse replay rejection;
* RepoContext trusted inline authorization;
* RepoContext manifest hashes actual bytes written;
* canonical RepoWriter root classification;
* actual HF1 V2 extension checkout BLOCKED as consumer root;
* sample_repo BLOCKED;
* no first-folder write-root fallback in repaired consumer write routes;
* no remaining REPAIR_5_REQUIRED write route from the exhaustive sweep.

Do not redesign any of these.

⸻

14. EXACT SCOPE PROOF

This amendment should modify exactly:

src/writers/RepoWriter.ts
src/test/suite/repoWriterWorkspaceSelection.test.ts
src/test/suite/configExplain.test.ts

or fewer if one authorized test file proves unnecessary.

No other candidate byte may change.

At end report:

* files changed during Amendment 2;
* all other Repair-5 candidate hashes unchanged;
* new files = 0;
* staged count = 0.

⸻

15. VALIDATION

Using only existing local dependencies, run:

npm run compile
npm run lint

Run focused tests covering:

* RepoWriter workspace selection;
* dangling-link containment;
* POSIX case-sensitive containment;
* Explain;
* Repair 5;
* HF1;
* Artifact Reuse;
* RepoContext;
* UnitTestCoordinator;
* WriteAuthorization.

Then run the full unit suite.

Expected:

compile: PASS
lint: PASS
focused Repair-5/HF1 tests: PASS
full unit: exactly 5 historical failures
new HF1 V2 regressions: NONE

Do not regenerate baselines.

⸻

16. FINAL PHYSICAL-CONTAINMENT ADVERSARIAL CHECK

Before declaring Repair 5 complete, explicitly reason through and/or test:

1. normal in-root file;
2. .. traversal;
3. absolute path;
4. sibling-root path;
5. symlink from in-root file to outside existing file;
6. symlink from in-root file to outside missing/dangling target;
7. linked ancestor directory escaping root;
8. case-distinct sibling on POSIX;
9. case variation on Windows;
10. normal valid consumer destination after all hardening.

There must be no path where an approved logical artifact can physically write outside canonical consumerRoot.

⸻

17. FINAL WRITE-ROUTE SWEEP

Repeat the exhaustive read-only write-route sweep.

There must be:

REPAIR_5_REQUIRED routes: 0

Competing-route UX debt may remain NON_BLOCKING_DEBT.

Do not convert it into a blocker unless new evidence demonstrates an actual approval/root/write bypass.

⸻

18. FINAL REPORT

Return:

1. Dangling-link root cause and exact fix.
2. Why lstat-aware handling closes the dangling-link escape.
3. POSIX case root cause and exact platform-sensitive fix.
4. Windows behavior preservation.
5. Physical containment regression matrix.
6. Explain fixture isolation repair.
7. Confirmation competing routes remain non-blocking and untouched.
8. Current Repair-5 lifecycle preservation.
9. Compile result.
10. Lint result.
11. Focused test result.
12. Full-unit result.
13. Exhaustive write-route sweep result.
14. Exact changed-file scope.
15. Staged/new-file count.
16. Historical-five separation.

Finish exactly one:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_VALIDATED

or

LOCAL_HOTFIX_HF1_V2_REPAIR_5_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

or

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

or

LOCAL_HOTFIX_HF1_V2_REPAIR_5_BLOCKED

Do not Keep.
Do not commit.
Do not push.
Do not package.
Do not install a VSIX.
Stop after the final report.
