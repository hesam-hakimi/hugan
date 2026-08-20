LOCAL_HOTFIX_HF1_V2_REPAIR_2

We have completed external validation after Repair 1.

Current verified state:
- npm run compile: PASS, exit 0
- npm run lint: PASS, exit 0
- Focused HF1 V2 tests: 85 passing, 1 failing
- Production code must NOT be changed in this repair.

The single failing test is:

Trusted framework definition resolver
Framework contract resolution
"packaged contract unreachable anywhere on disk and no source configured yields FRAMEWORK_DEFINITION_UNAVAILABLE"

Observed runtime failure:

TypeError: Cannot set property existsSync of #<Object> which has only a getter

The failure originates from the test helper:
withContractFileHidden(...)
inside:
src/test/suite/trustedFrameworkDefinitionResolver.test.ts

This is a TEST HARNESS problem, not a production resolver defect.

TASK

Repair only the failing test/helper so it can simulate the packaged contract being unavailable without mutating a read-only ES/CommonJS namespace export.

STRICT SCOPE

You MAY modify only:

src/test/suite/trustedFrameworkDefinitionResolver.test.ts

Do NOT modify:
- TrustedFrameworkDefinitionResolver.ts
- FrameworkDiscoveryService.ts
- package.json
- packaged framework contract JSON
- production resolver logic
- any other source or test file

REQUIREMENTS

1. Inspect the actual import style and implementation of withContractFileHidden(...).

2. Do not assign directly to:
   fs.existsSync
or any other getter-only module namespace property.

3. Use the smallest existing repo-compatible mocking/stubbing technique available.

Preferred order:
   a. dependency/function injection already supported by the resolver/test
   b. sinon.stub(...) on a mutable object if already used in this repo
   c. require("fs") mutable CommonJS object only if compatible with the current module/runtime
   d. a test-local wrapper/injected filesystem adapter

Do NOT introduce a production seam merely for this test unless absolutely necessary.

4. Preserve the semantic intent of the test exactly:
   - no configured framework source
   - packaged contract appears unavailable
   - resolver returns FRAMEWORK_DEFINITION_UNAVAILABLE
   - no fallback to unrelated workspace folders
   - no filesystem write or mutation

5. The mock must always be restored in finally/afterEach so later tests cannot inherit modified filesystem behavior.

6. Do not weaken, skip, remove, or change the assertion.

7. Do not use:
   - as any
   - as never
   - @ts-ignore
   - @ts-expect-error
   - Object.defineProperty on Node's fs module namespace
   - global permanent monkey-patching

8. After the repair, run:

npm run compile
npm run lint

Then run the same focused HF1 V2 test command used in the previous external validation.

Expected result:

Focused HF1 V2 tests:
86 passing
0 failing

If compile/lint/focused tests pass, STOP.

Do NOT run the full-unit suite yet.
Do NOT package or install a VSIX.
Do NOT commit, push, merge, or perform any Git mutation.

Report:
- exact root cause
- exact lines changed
- mocking/stubbing mechanism used
- proof cleanup/restoration occurs
- compile result
- lint result
- focused-test result

Finish with exactly:

LOCAL_HOTFIX_HF1_V2_REPAIR_2_VALIDATED

or, if anything remains failing:

LOCAL_HOTFIX_HF1_V2_REPAIR_2_BLOCKED
