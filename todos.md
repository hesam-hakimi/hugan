# Make the investigated writeFlow filesystem precondition permanent

TASK\_ID: ETL\-0915\-WRITEFLOW\-FILESYSTEM\-PRECONDITION\-REPAIR01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
PREDECESSOR: ETL\-0915\-WRITEFLOW\-NINE\-FAILURES\-INVESTIGATE01\.
SCOPE: Implement the reviewed recommendation’s steps 1\-2 only: an opt\-in real\-filesystem binding for the existing headless stub, activated and restored by writeFlow’s test lifecycle\.
REGISTRATION\_DECISION: Preserve existing GUI/integration membership\. Do not add writeFlow to PURE\_UNIT\_TEST\_PATTERNS or change runner selection\.
PRODUCT\_WRITE\_AUTHORIZATION\_BUDGET: 0\.
PRODUCT\_MODEL\_REQUESTS: 0\. ADDITIONAL\_VSCODE\_HOST\_LAUNCHES: 0\.

Execute on owner submission, preferably in the same engineering session as the completed investigation\. Submission authorizes the bounded test\-only edits, isolated compilation/checks, task\-local diagnostics and independent review in this brief\. It does not authorize product\-source changes, shared\-helper adoption, a GUI run, installation or consumer writes\. Use English for every response, code comment, test and document\. Use text/filesystem evidence only; no screenshots, video, OCR or vision\.

## 1\. Recover and reuse the completed investigation

Read the predecessor’s actual final report\.md, result\.json, both complete reviewer returns, exact nine\-case mapping, successful contained filesystem\-binding probe and its raw pre/post records\. The owner received pass 1 CHANGES\_REQUIRED followed by pass 2 VERIFIED after corrections\. Resolve its root under C:\\docs by the actual task ID; do not reconstruct paths, hashes or code from the photograph\.

The demonstrated cause was the headless environment:

- RepoWriter uses vscode\.workspace\.fs, while writeFlow checks the physical filesystem with Node fs\.
- The default headless stub’s writeFile/createDirectory are no\-ops, causing eight cases to observe absent output\. Its always\-successful stat causes the WF\-04 overwrite check to report an existing destination\.
- Holding the compiled suite, product build, runner, flags and cwd constant while replacing only the filesystem binding changed 17 passing / 9 failing to 26 passing / 0 failing\. This establishes the measured cause; it is not nine product defects\.
- The suite is registered for the GUI/integration runner, which uses an Extension Host\. No GUI run was performed, so passing there remains unobserved\.
- The predecessor did not implement its recommended permanent repair\. Its suggested third step would alter runner membership because the GUI exclusion list is derived from pure\-unit patterns\. That optional trade\-off is declined in this task\.

Reuse these results where the inputs match; do not repeat the investigation or reinterpret successful Created log lines as proof of physical writes\. Both predecessor runs emitted such lines\. Physical readback is the relevant evidence for disk effects\.

Read applicable repository instructions and the effective 09 repair/verification contract\. Authenticate the actual current source and test paths using retained records and bounded inspection\. Do not use clean \.147 HEAD as a substitute for the later accepted dirty source; installed \.160 and worktree package\.json \.147 remain distinct\.

## 2\. Establish the narrow edit boundary

Resolve the actual files named registerVscodeStub\.ts and writeFlow\.test\.ts\. These are the two primary editable surfaces\. One existing adjacent test\-only file may be extended, or one focused test\-only file added, only if required to check binding restoration or the exercised filesystem contract\. Record the exact paths before editing\. No other source/helper/configuration changes are included\.

Confirm the investigation is closed and acquire ownership of these exact test surfaces\. Check any active claims, including ETL\-0915\-OVERNIGHT\-REVIEW\-CLOSEOUT01\. A read\-only closeout using frozen evidence need not block this task, but do not edit a surface owned by another task\. If a real conflict exists, prepare the patch and checks in an isolated copy and identify the integration dependency; do not stop or redirect the other agent\.

Create a new task\-owned evidence root with relevant preimages and hashes\. Preserve unrelated dirty work, HEAD, package version, shared out, \.tsbuildinfo\.test, installed \.160, maintainer \.github files, closed evidence, profiles and consumers\. Do not claim historical preservation from current hashes or mtimes alone\.

Inspect the actual packaging boundary and import consumers once\. The investigation reported the test/stub source excluded from shipping; verify that these edits stay test\-only and cannot enter the product bundle or alter package inputs\. Do not launch a build/package/install merely to rediscover a boundary already supported by matching evidence\. If the assumption is false, stop expansion and report the exact coupling\.

## 3\. Implement opt\-in filesystem behavior and suite ownership

Reuse the successful probe’s tested behavior as evidence, adapting it into the existing test mechanism rather than creating a second harness or copying an unreviewed probe wholesale\.

Add an explicit opt\-in binding to the existing headless stub\. Preserve default stub behavior for unrelated suites\. Bind only the local\-file operations actually required by writeFlow, with the relevant vscode\.workspace\.fs argument/result semantics rather than blindly assigning incompatible Node functions\. Physical writes, directory creation and missing/existing stat behavior must agree with the assertions and real consumer calls being tested\.

Keep the binding scoped to the suite’s own temporary root&#40;s&#41;\. Do not follow fixture paths into a live worktree, historical consumer, profile, approval store or another task\. Preserve the actual byte contents and filesystem exceptions needed by these cases\. Do not manufacture success, pretend absent paths exist, suppress an unexpected error or weaken the writer/test assertions\. General equivalence to all VS Code providers, including remote/virtual filesystems, is not required and must not be claimed\.

Activate the binding through writeFlow’s setup only when the existing headless\-stub mechanism is actually in use\. Record the previous binding and restore it on teardown, including setup\-failure paths where registration has already occurred\. Avoid leaking real filesystem behavior to another suite\.

In an actual Extension Host, use its existing vscode\.workspace\.fs unchanged\. Do not import a module that auto\-registers the headless stub into the GUI host just to detect the environment\. Use the repository’s real environment/registration mechanism; do not infer a headless stub merely because a method with the same name exists\. If the environment cannot be established, expose that setup failure instead of silently skipping tests or replacing a real provider\.

Keep all 26 existing writeFlow assertions and their intended behavior\. Add only the focused protection necessary for this new test\-environment boundary, such as restoration and missing/existing\-file behavior that the nine historical failures depend on\. Do not refactor RepoWriter, introduce a product endpoint, change validation semantics, or edit testPatterns\.ts, PURE\_UNIT\_TEST\_PATTERNS, GUI ignore rules or runner defaults\.

## 4\. Verify the changed boundary with minimal execution

Reuse inspected isolated\-lane helpers, the focused runner and existing dependencies\. Compile only what the changed TypeScript requires into task\-owned output/build\-info locations\. Preserve source\-to\-executed\-JS identity; do not hand\-edit generated files or run tests from shared out\. Never execute naive compile/test:unit/pretest/compile:test in the recovery worktree\.

Show a behavioral red/green comparison for the permanent integration\. Prefer matching retained red evidence; if it no longer corresponds, run one focused type\-compatible red case that disables only the new opt\-in behavior in an isolated copy\. Do not use a compilation error from a missing new export as the negative control\. Then run the permanent writeFlow suite through the focused headless route without the predecessor’s external probe injecting its filesystem binding\.

Required observations:

- The original 26 writeFlow cases pass with the permanent suite setup and actual task\-local disk effects\.
- At least the affected write/readback and absent\-destination behavior are supported by physical filesystem evidence, not Created logs alone\.
- The opt\-in is inactive by default and restored after the suite; a focused control demonstrates no binding leakage to an unrelated test using the original stub behavior\. Retain the real\-host branch’s source/static or test\-control evidence separately from unexecuted GUI qualification\.
- Actual pattern\-array and derived\-ignore evaluation still places writeFlow in its existing GUI/integration selection and not the ordinary pure\-unit selection\. Do not advertise new default headless discovery: this task makes the focused headless execution valid while preserving existing registration\.

Reuse the corrected failure identity/encoding guard where relevant\. Record runner selection, test counts, raw exits/signals, input identities and actual timing\. Unknown is not zero\. Do not call the repository all\-green, subtract these nine from a different campaign’s 24 failures, or claim GUI success from the headless result\. The other seven of the historical 16 remain outside this task\.

A full suite campaign, fresh VSIX, installation, product model call or live host is not part of this test\-only repair\. Broaden a focused check only for a concrete changed dependency or failed acceptance above\. Preserve task\-caused failed attempts and fix them within scope; do not skip or waive failures\.

## 5\. Review, deliver and stop

Use one independent read\-only reviewer, with corrective passes as needed, for the actual final stub/suite delta, binding lifecycle, filesystem semantics exercised, runner membership and packaging boundary\. Reuse the investigation’s accepted diagnosis; do not review the entire history again\. Preserve complete returns; parent\-persisted output must be marked artifactAuthoredByReviewer: false\. Author corrections are not final independent acceptance without the reviewer’s disposition\.

Deliver report\.md, result\.json and the minimal task\.diff, with exact edited paths, applied versus staged status, pre/post source identities, original and added test counts, raw results, review status, unchanged registration evidence and preservation checks\. State separately: cause already established, permanent test repair implemented or staged, focused headless result, GUI run not performed, product \.160 unchanged\.

Release only this task’s ownership\. Do not adopt the overnight b1\-lane manifest, fix developer\.agent\.md, change Phase H acceptance, update canonical references, or start follow\-on backlog work\. Preserve the successful \.160 two\-file write/readback and its SPENT allowance; no new preview or approval is available here\. Carry item E, F\-ROOT\-1, historical ledger identity limits, the check\-to\-write race, runtime/DBFS limits, the separate overnight review disposition and expired quarantine forward\. No release, deployment or full\-readiness claim follows\.
