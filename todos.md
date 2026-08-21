LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_2_DISCOVERY — READ ONLY

Repair 5 has reached a validated partial state but ended with:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_REQUIRED

Do NOT edit anything yet.

Preserve all current Repair-5 candidate bytes exactly as they are.

Do not Keep, Undo, Revert, Discard, Clean, stage, commit, package, install, download, or mutate any file.

The current externally relevant implementation evidence is:

- production compile: PASS
- lint: PASS
- focused Repair-5/HF1/Phase-6 matrix: 278 passing
- full unit: 1890 passing, 5 pending, exactly 5 failing
- the five failures are the protected historical failures
- staged files: 0
- new files: 0
- framework binding unchanged
- etl-framework-adb unchanged
- 10 files currently changed
- ArtifactActionCoordinator.ts was authorized but remained byte-identical

The verifier reported four remaining concerns:

1. dangling-link handling
2. POSIX case-sensitive containment
3. broader competing-route suppression
4. unique temporary Explain fixtures

Your task is ONLY to determine the exact nature and minimum scope of these four items.

==================================================
1. CLASSIFY EACH ITEM BEFORE REQUESTING ANY EDIT
==================================================

For each of the four findings classify it exactly as one of:

PRODUCTION_SECURITY_DEFECT
PRODUCTION_CORRECTNESS_DEFECT
TEST_HARNESS_DEFECT
TEST_COVERAGE_GAP
PORTABILITY_HARDENING
NON_BLOCKING_DEBT
FALSE_POSITIVE
AMBIGUOUS

Do not assume that a verifier-requested test implies a production defect.

For every item provide live-source evidence.

==================================================
2. DANGLING-LINK HANDLING
==================================================

Determine exactly what "dangling-link handling" refers to.

Trace:

- which repaired route encounters symlinks/junctions/reparse points;
- whether PathValidator / isInsideRoot / canonicalization currently resolves them;
- whether a dangling symbolic link could cause:
  - consumerRoot escape,
  - source/reference-root substitution,
  - unauthorized write,
  - write outside the approved relative path,
  - or merely a clean filesystem error.

Identify:

- exact production function;
- exact current behavior;
- actual security impact;
- exact test needed.

Do not propose a platform-specific workaround unless the live production behavior requires it.

==================================================
3. POSIX CASE-SENSITIVE CONTAINMENT
==================================================

Determine whether current containment logic incorrectly assumes Windows case-insensitivity on POSIX.

Inspect the exact implementation used by all Repair-5 write routes.

Answer:

A. Does Windows behavior remain correct?

B. On Linux/macOS, could:

/ConsumerRoot/file
and
/consumerroot/file

be incorrectly treated as the same root?

C. Could that cause a real root escape or false acceptance?

D. Is the bug in shared PathValidator/isInsideRoot infrastructure or only in Repair-5 test code?

E. Would fixing it require modifying an already-protected shared file outside the current scope?

Do not edit shared PathValidator or root utilities in this discovery.

==================================================
4. BROADER COMPETING-ROUTE SUPPRESSION
==================================================

Clarify exactly what "competing route" means.

Identify any scenario where more than one write-capable route could respond to the same user action or conversational state.

For every claimed competing route show:

- entry point;
- activation condition;
- whether both can be reachable in the same request;
- whether either can write;
- whether preview state from one route can be consumed by another;
- whether route confusion can bypass approval;
- whether the issue is merely UX/routing ambiguity.

Do not broaden Repair 5 into unrelated routing redesign.

If the concern is not capable of causing an unauthorized consumer mutation, classify it accordingly.

==================================================
5. UNIQUE TEMPORARY EXPLAIN FIXTURES
==================================================

Determine whether this is:

- a production problem,
- test isolation problem,
- parallel-test collision,
- stale temporary directory reuse,
- or simply a verifier-hardening request.

Inspect current Explain tests and temp-directory construction.

Prove whether two tests/runs can collide on the same path and contaminate one another.

If the issue is test-only, do not propose a production change.

Identify the exact existing test file that should be changed.

No new test file unless strictly necessary.

==================================================
6. RECHECK THE CURRENT REPAIR-5 CONTRACT
==================================================

Do a read-only confirmation that the current candidate already provides:

- Explain trusted preview/approval/write lifecycle;
- Explain root/path/content drift protection;
- Explain replay rejection;
- Artifact Reuse preview → approval → create/patch;
- Artifact Reuse replay rejection;
- RepoContext trusted inline authorization;
- RepoContext manifest hashes the actual bytes written;
- canonical RepoWriter root classification;
- current extension-source checkout blocked as a consumer root;
- no first-folder consumer-write fallback in repaired routes;
- no remaining REPAIR_5_REQUIRED write route from the previous exhaustive sweep.

If any of these is actually incomplete, report it separately as a regression from the just-completed implementation.

==================================================
7. EXACT SCOPE REQUEST
==================================================

For every item that truly requires a change, return:

- exact file path;
- production vs test;
- exact function/test affected;
- smallest change required;
- why the currently authorized 11-file universe cannot solve it;
- whether the file was already part of the previously protected/no-touch set.

Do not give approximate paths.

Do not request a file merely for convenience.

==================================================
8. SCOPE MINIMIZATION RULE
==================================================

Prefer:

0 additional files

if the remaining items can be addressed inside existing authorized files.

If an additional file is genuinely necessary, request only that exact file.

If a shared security primitive outside current scope must change, explicitly flag:

SHARED_SECURITY_PRIMITIVE_SCOPE_REQUIRED

and stop before implementation.

==================================================
9. REQUIRED FINAL REPORT
==================================================

Return a four-row matrix:

Finding
Classification
Production impact
Security impact
Exact file(s) required
Already authorized? YES|NO
Repair required? YES|NO
Release blocking? YES|NO

Then return:

CURRENT_REPAIR_5_BYTES_PRESERVED: YES|NO
CURRENT_COMPILE_RESULT_RETAINED_AS_EXTERNAL_EVIDENCE: PASS
CURRENT_LINT_RESULT_RETAINED_AS_EXTERNAL_EVIDENCE: PASS
CURRENT_FULL_UNIT_BASELINE: 1890_PASSING_5_PENDING_5_HISTORICAL_FAILING
DANGLING_LINK_REPAIR_REQUIRED: YES|NO
POSIX_CASE_CONTAINMENT_REPAIR_REQUIRED: YES|NO
COMPETING_ROUTE_REPAIR_REQUIRED: YES|NO
EXPLAIN_FIXTURE_REPAIR_REQUIRED: YES|NO
ADDITIONAL_PRODUCTION_FILES_REQUIRED: <count>
ADDITIONAL_TEST_FILES_REQUIRED: <count>
SHARED_SECURITY_PRIMITIVE_SCOPE_REQUIRED: YES|NO
REPAIR_5_AMENDMENT_2_SCOPE_FROZEN: YES|NO

Finish exactly:

LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_AMENDMENT_2_DISCOVERY_COMPLETE
