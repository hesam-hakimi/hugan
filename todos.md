AUTHORIZE_LOCAL_HOTFIX_HF1_SCOPE_AMENDMENT_M22

The frozen LOCAL_HOTFIX_HF1 inventory is amended by exactly one file:

src/test/suite/etlActionTools.test.ts

Updated authorized totals:

* 5 new files
* 22 modified files
* 27 files total

Continue from the current partial implementation. Preserve the eight already-created/modified in-scope files. Do not restart, roll back, or edit any no-touch file.

AMENDMENT PURPOSE

Modify only the tests in etlActionTools.test.ts whose successful-write or post-write-checkpoint expectations are directly affected by the newly authorized two-step contract:

validation → preview → explicit approval → authorized write

TEST-UPDATE REQUIREMENTS

1. Do not weaken, delete, skip, suppress, or mark any affected test pending.
2. Do not add:

* automatic approval
* approval when previewId is absent
* a test-only production bypass
* a feature flag bypass
* a forged WriteAuthorization
* direct access to a private store
* direct RepoWriter writes that evade the public workflow

3. For tests requiring a completed write, drive the real public workflow:

* first invocation produces the immutable preview and performs zero writes
* perform the real explicit approval transition
* second invocation supplies the approved preview identity
* exactly one authorized write occurs
* returned workspace path, artifact paths, manifest binding, and continuation checkpoint are asserted

4. Tests that use a real write only to seed an Autonomous Guarded checkpoint must seed it through the same approved two-step workflow before testing publish/run continuation behavior.
5. Preserve the original semantic assertions:

* usedWorkspacePath
* success state after approved write
* markdown/result contract
* checkpoint scope
* approval-token behavior
* publish/run continuation
* requested-path coverage
* rejection when the stored checkpoint does not cover the requested path
* no unintended publish, onboarding, or run side effects

6. Tests that fail earlier during validation or workspace selection and never reach the write boundary should remain unchanged unless compilation proves a minimal signature update is required.
7. A plain preview response must not be rewritten as a successful completed write. The tests must explicitly distinguish:

* preview generated / no write
* approval accepted
* write completed

8. Keep src/test/suite/etlActionTools.test.ts registered through its existing PURE_UNIT_TEST_PATTERNS entry. Do not modify registration merely for this amendment.

SCOPE ENFORCEMENT

No additional production file is authorized beyond the original 26-file inventory.

No additional test file is authorized beyond this amendment.

If any other unlisted file becomes necessary, stop and report:

LOCAL_HOTFIX_HF1_SCOPE_AMENDMENT_REQUIRED

Do not modify that file.

VALIDATION AND BASELINE

Continue to enforce:

* compile must pass
* lint must pass
* focused HF1 tests must pass
* all new HF1 tests must pass
* the full unit suite may retain only the exact six documented pre-existing baseline failures
* no seventh failure
* no changed failure identity

Do not repair or modify the six baseline failures.

If native execution remains unavailable in this Chat, report the exact external PowerShell commands without fabricating results and finish with:

LOCAL_HOTFIX_HF1_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

AUDIT CORRECTION

In the next report, avoid any statement equivalent to “no file was modified in this session,” because eight authorized files have already been changed.

State accurately:

* eight authorized files were changed before this amendment
* zero out-of-inventory files were changed
* zero no-touch files were changed
* no Git mutation, install, download, package, deployment, or consumer write occurred

Proceed with the amended 27-file frozen scope.
