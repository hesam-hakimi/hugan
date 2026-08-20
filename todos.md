LOCAL_HOTFIX_HF1_V2_EXTERNAL_VALIDATION_REPAIR_1 — TEST-STUB SIGNATURE FIX

External validation stopped at compile with exactly two TypeScript diagnostics, both in the already-authorized test file:

src/test/suite/hf1OracleFreshConsumer.test.ts:215:7
TS2322
src/test/suite/hf1OracleFreshConsumer.test.ts:218:7
TS2322

The assignments to:

vscodeTestStub.workspace.fs.createDirectory
vscodeTestStub.workspace.fs.writeFile

use function signatures that are incompatible with the existing VS Code test-stub contract.

Scope

Modify ONLY:

src/test/suite/hf1OracleFreshConsumer.test.ts

This file is already inside the authorized HF1-V2 edit universe.

Do not modify production code.

Do not modify the shared VS Code stub unless read-only inspection proves the test cannot be corrected locally. If another file is truly required, STOP before editing and report:

LOCAL_HOTFIX_HF1_V2_SCOPE_AMENDMENT_REQUIRED

Required repair

1. Inspect the exact declared types of:

vscodeTestStub.workspace.fs.createDirectory
vscodeTestStub.workspace.fs.writeFile

and the repository’s existing tests that override these methods.

2. Align the two HF1 test overrides with the established stub convention.
3. Preserve the purpose of the tests:
    * detect whether an unexpected filesystem write is attempted;
    * capture/inspect the requested URI/path where required;
    * prove fresh-consumer classification/preview performs zero writes;
    * do not make the assertion vacuous.
4. Do NOT solve the error with:
    * as any;
    * as unknown as ...;
    * non-null assertions;
    * disabling TypeScript;
    * @ts-ignore;
    * @ts-expect-error;
    * weakening production interfaces;
    * removing the write-detection assertions.
5. If the existing stub type intentionally exposes parameterless functions, use a locally type-compatible strategy such as optional/rest arguments only if that matches existing repository test conventions and still observes the real arguments passed at runtime.

Do not guess the signature; derive it from live source evidence.

6. Review both tests after the repair and prove they would fail if production attempted the forbidden filesystem operation.
7. Do not run package, Git, VSIX, install, network, or consumer-write actions.
8. Native compile/tests do not need to be run from this Copilot session if process execution remains unavailable. Do not fabricate results.

Return:

* exact root cause;
* existing stub signature;
* before/after test override;
* why the assertion remains discriminating;
* exact file changed;
* confirmation that no production file changed.

Finish with:

LOCAL_HOTFIX_HF1_V2_REPAIR_1_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION
