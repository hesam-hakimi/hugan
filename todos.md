Work only in this repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Perform one narrowly scoped Git staging operation.

1. Verify:

* Current branch: fix/runtime-sttm-structured-output-0.3.148
* Current HEAD: ca51faf652d85d5b44c1e4dd07baa704f634ec1c
* Git status contains exactly these four paths:
    * src/tools/index.ts
    * src/test/helpers/registerVscodeStub.ts
    * src/test/testPatterns.ts
    * src/test/suite/sttmPublicToolResultEnvelope.test.ts

2. If the branch, HEAD, or changed-file set differs, stop immediately and report the difference.
3. Otherwise, stage only those four files using explicit paths.
4. Run:

git diff –cached –name-status

git status –short

5. Confirm that the staged set contains exactly three modified files and one added test file.

Restrictions:

* Do not edit any file.
* Do not run tests or compilation.
* Do not change the package version.
* Do not commit or push.
* Do not reset, clean, delete, or stash anything.
* Stop after reporting the verification results.
