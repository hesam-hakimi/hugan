READ-ONLY INVESTIGATION. Do not compile, run tests, launch a runner or
Extension Host, install anything, or edit any file. Report only.

Repository: C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Report, each as a separate labelled block:
1. git rev-parse --abbrev-ref HEAD, git rev-parse HEAD, and the exact
   porcelain status, with a literal count of status paths.
2. Whether the staging area is empty and whether .git/index.lock exists.
3. The full repository-relative path of every file named index.ts under
   src/**, so the three ambiguous manifest entries can be disambiguated.
4. The exact current text of runTest.ts lines 340-370, and state
   whether the manifest cardinality is hard-coded, derived, or
   configurable.
5. The SHA-256 of src/test/runTest.ts, src/test/suite/index.ts, and
   src/test/suite/sttmRealHostStructuredResult.test.ts as they exist
   now on disk.

Do not compare against any hash I have not given you. Do not conclude
PASS, FAIL, or BLOCKED. Just report observed values.
