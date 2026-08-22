TASK: LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_7

Implement ONLY the minimum release-blocking remediation identified by
LOCAL_HOTFIX_HF1_V2_FINAL_RELEASE_REAUDIT.

Do not reopen Repair 5 or Repair 6.
Do not redesign the ETL architecture.
Do not modify framework/Oracle behavior.
Do not broaden into unrelated technical debt.

The final re-audit established one remaining release-blocking class:

Six production-reachable Copilot Workflow Customization consumer-write routes
can reach the filesystem using lexical containment only.

The audit also established that the hardened physical-containment algorithm
already works correctly in the Repair-6 path.

GOAL:

Reuse/extract the already-proven physical-containment algorithm as a shared
primitive and apply it to the six identified customization write routes
immediately before filesystem mutation.

Do NOT duplicate the algorithm.

==================================================
1. SHARED PHYSICAL-CONTAINMENT PRIMITIVE
==================================================

Inspect:

- RepoWriter.resolveContainedWorkspacePath(...)
- WorkflowTargetResolver.assertWithinWorkspace(...)

Extract/reuse the physical canonicalization core required for:

- nearest-existing-ancestor lstat walk
- realpath/native canonicalization
- dangling-link detection
- symlink/junction/reparse-point detection
- canonical descendant validation
- platform-aware case semantics
- hard-link protections where applicable
- fail-closed behavior

The shared primitive must NOT contain RepoWriter-specific policy such as
rejecting .github/**.

Physical containment and artifact-policy validation must remain separate
concerns.

Do not weaken the existing RepoWriter implementation.

==================================================
2. SIX LEGACY CUSTOMIZATION WRITE ROUTES
==================================================

Apply physical containment immediately before mutation to every route identified
by the final re-audit, including the Copilot workflow customization writers
reachable through:

- CopilotWorkflowInitializer
- CopilotWorkflowUpgrader
- CopilotWorkflowRepairer
- CopilotWorkflowDeleter
- GeneratedAssetGitignoreManager
- ConsumerRepoOverlayService / delegated writer path

Use the exact live-source inventory from the final re-audit as authority.

Do not assume this list is complete merely from these names:
before editing, reconcile it against the six failing routes enumerated by the
audit.

For each route prove:

logical workspace root
→ policy validation
→ physical canonical containment
→ ONLY THEN filesystem mutation

No mkdir/write/delete/rename/copy operation may happen before physical
containment succeeds.

==================================================
3. DO NOT REWRITE AUTHORIZATION ARCHITECTURE
==================================================

This Repair is specifically physical containment.

Do NOT redesign the legacy customization approval model unless required to
close the demonstrated physical escape.

Do not migrate unrelated legacy flows into WriteAuthorization in this repair.

Record legacy authorization modernization separately as deferred debt.

==================================================
4. ADVERSARIAL TESTS
==================================================

Extend the existing physical containment test coverage.

For EACH affected route/class, prove failure for relevant cases:

- ../ traversal
- absolute escape
- sibling-root escape
- symlink escape
- junction/reparse escape
- dangling link
- linked ancestor escape
- POSIX case-distinct sibling
- post-validation / pre-write path substitution where applicable

Also retain positive tests proving legitimate in-workspace customization writes
still succeed.

Most importantly, reproduce the exact PoC from the final re-audit:

lexically valid consumer target
→ junction inside consumer workspace
→ physical destination outside canonical consumer root

Before repair this is writable.
After repair it MUST fail closed and outside bytes MUST remain unchanged.

==================================================
5. TEST REGISTRY GAP
==================================================

The final audit reported that:

src/test/testPatterns.ts PURE_UNIT_TEST_PATTERNS

does not include:

physicalWriteContainment.test

and other relevant integration suites.

Correct the registry so release-critical containment tests cannot silently be
excluded from the standard test command.

Do not broadly reorganize test infrastructure.

==================================================
6. PACKAGE-HYGIENE SECONDARY ITEMS
==================================================

Do NOT mix non-blocking package cleanup into the security repair unless needed
for release verification.

After the security repair, verify and report separately the audit observations
about:

- .code-workspace
- scripts/**
- workflow/**
- resources negation behavior

Classify each as BLOCKING or NON-BLOCKING from actual packaged content.

Do not modify them unless independently proven release-blocking.

==================================================
7. VALIDATION
==================================================

Using already-installed dependencies only, run:

- compile
- lint
- focused physical-containment tests
- all six customization-route regression tests
- existing Repair 5 tests
- existing Repair 6 tests
- WriteAuthorization tests
- full unit suite
- package verification if available

Do not install/download dependencies.

Do not regenerate historical baselines.

The known historical five failures must remain exactly the historical five and
must not increase.

==================================================
8. SCOPE CONTROL
==================================================

Before mutation:

1. inspect the exact files required;
2. produce the minimum file inventory;
3. request ONE consolidated authorization for that bounded set.

Do not modify:

- consumer repositories
- etl-framework-adb
- resources/prompts/**
- .github/**
- AGENT.md / AGENTS.md
- package-lock.json
- historical Phase-H baselines
- Oracle/framework contracts

unless the task explicitly proves one is indispensable and stops for scope
amendment first.

No commit.
No push.
No Keep.
No VSIX installation.

==================================================
9. FINAL REPORT
==================================================

Report:

A. exact files changed
B. shared containment primitive created/reused
C. exact six routes repaired
D. proof each route checks physical containment immediately before mutation
E. adversarial PoC result
F. positive legitimate-write result
G. test-registry correction
H. compile result
I. lint result
J. focused-test result
K. full-unit result
L. historical-five status
M. package verification result
N. remaining blocking findings

Then print:

ALL_CUSTOMIZATION_WRITE_ROUTES_PHYSICALLY_CONTAINED: YES/NO
PHYSICAL_CONTAINMENT_TESTS_STANDARD_SUITE_INCLUDED: YES/NO
NEW_REGRESSIONS: YES/NO
HISTORICAL_FIVE_UNCHANGED: YES/NO
SAFE_FOR_FINAL_RELEASE_REAUDIT: YES/NO

If SAFE_FOR_FINAL_RELEASE_REAUDIT is NO, STOP.
Do not begin another repair automatically.

Final marker:

LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_7_COMPLETE
