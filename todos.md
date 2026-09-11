# Finish the related /create parser corrections and independent review

TASK\_ID: ETL\-0911\-CREATE\-ENV\-ROLE\-BINDING\-REPAIR01
ACTION\_ID: PARSER\-CORRECTIONS\-AND\-REVIEW01
STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not launched by ChatGPT
TYPE: Same\-source\-task continuation; narrowly expanded parser defect scope

Continue in the current Windows session\. English only for all coordinator/subagent communication, code, tests and reports\. No screenshots, video, image inspection, OCR or vision\.

## Current result and precise expansion

Read the retained final source result, actual review findings, post\-review diff and test commands\. The owner reports:

- GoalInterpreter\.extractFolders harvested slash\-containing tokens with only a \.md exclusion, allowing the explicitly reused environment config into references\.folders and the workload plan\.
- The correction now uses isSuppliedEnvironmentConfigReference at three candidate\-producing branches, including inline\-backtick extraction and the folders\-section branch corrected after review\.
- 74 affected checks pass and typecheck exits 0\. Only GoalInterpreter\.ts and phase4ConversationalPlanner\.test\.ts changed\.
- The reviewer correctly returned CHANGES\_REQUIRED for a bypass\. The author corrected it, but the corrective delta has NOT received independent re\-review\.
- CREATE\-PHRASING\-WORKLOAD\-COLLAPSE\-001 is independently reproduced: ‘Create an ETL job from folders raw/customer\_orders into ADLS curated\.’ becomes table ADLS and source folders without any env clause\.

Owner submission now explicitly includes the smallest fix for CREATE\-PHRASING\-WORKLOAD\-COLLAPSE\-001 alongside closure of the environment\-role review findings\. Its previous out\-of\-scope classification was correct for the previous brief; preserve that history rather than claiming it was always authorized\. This is not authority for a general natural\-language parser rewrite\.

Complete both concrete source corrections and their focused independent review in this continuation\. Do not end merely after applying a reviewer correction without having its changed portion re\-checked\.

## Authority and preservation

Authorized: targeted source/test edits for these two defects, isolated affected test compilation/execution using existing tooling, and a bounded independent re\-check\. No runtime Chat/model request, product command, consumer write, build/package/install, dependency download/update, version change, Git mutation, job, deployment or publication\.

Use the existing task/claim/root, check actual action disposition and source ownership, and preserve newer evidence\. Do not duplicate running/completed work or infer inactivity from missing output\. Append identifiable continuation records without altering old reviews/evidence\.

Source: C:\\repos\\etl\-extension\\etl\_fw2\\recovery\-extension\-product\-0\.3\.147
Protected linked primary: C:\\repos\\etl\-extension\\etl\_fw2\\etl\_framework\_extension\_hf1\_v2

Pin relevant preimages and preserve existing dirty/untracked work, shared out/, \.tsbuildinfo\.test, installed environments and the signed\-in env151 profile\. Do not repeat fixture setup, sign\-in, host diagnosis or prior runtime cases\. No broad C:\\docs/session\-store scan or historical reconciliation campaign\.

## Trace and fix only the concrete parser failures

1. Reproduce the exact CREATE\-PHRASING\-WORKLOAD\-COLLAPSE\-001 input offline against current code before editing\. Trace actual branch precedence/capture groups and downstream role assignment\. Do not assume the regex/mechanism before inspecting it\.
2. Parse the explicitly supplied folder raw/customer\_orders as the workload input and ADLS curated as destination context under the existing contract\. Structural words in that sentence must not silently become a workload table/source\. Derive literal expected normalized roles/paths from the established valid\-folder contract, not from the parser under test\.
3. Preserve valid ‘Migrate folders …’ behavior and legitimate explicit workload names\. Do not blanket\-ban the words ADLS/folders/env or YAML/JSON/file inputs; correct roles and precedence in the affected sentence forms\.
4. Preserve the env\-reuse correction across all actual candidate\-producing paths: bare paths, quoted/backtick tokens and the folders\-section branch\. An env\-only request must clarify genuine missing workload inputs, not invent a table/target/write mode\.
5. The current environment\-context check is a bounded lexical heuristic &#40;reported preceding window <=120 characters with sentence boundaries&#41;\. Do not describe it as a complete semantic understanding guarantee\. Have the reviewer inspect its actual bounds and verify that the supplied role language is not applied to an unrelated neighboring workload\. Fix concrete in\-scope regressions; record unsupported language variants honestly rather than expanding to arbitrary natural\-language coverage\.
6. Do not merely replace the failing live test request with a friendlier phrase or weaken its expectations\. No changes to writers, approval gates, workflow migration, packaged assets, file\-extension policy, diagnostic F\-1 or OUTCOME\-DISCLOSURE\-001\.

Use the smallest coherent edit set, preferably the same parser/test seam\. Any additional affected file must have a concrete dependency justification and protected preimage\.

## Tests through existing entrypoints

Retain the six environment\-role regressions and the existing positive case in which env\_conf/dev/customer is legitimately a workload\. Add minimal permanent coverage for:

- the exact observed ‘Create an ETL job from folders raw/customer\_orders into ADLS curated\.’ form;
- that same concrete workload plus an explicit unchanged\-env\-reuse clause: only the real workload enters the plan;
- existing valid folder phrasing remaining valid;
- the reviewer\-identified quoted/backtick and folders\-section bypasses staying closed\.

Use independent literal expected workload/source/target roles and assert that missing\-input outcomes cannot dispatch a writer\. No live model call, fixture consumer write or fake claim of installed behavior\. Record a behavioral pre\-fix failure where feasible; a compile/import failure is not a behavioral red\.

Run the relevant existing suites using the retained isolated lane\. Use already installed compiler/test binaries; do not allow npx to fetch missing tooling\. Output and incremental state remain task\-owned\. Verify the emitted tests correspond to the edited test/source identities, and do not run a command that removes protected out/\.

The previous report says createFlowScenarios\.test\.ts was not emitted by tsconfig\.test\.json and createPreviewFlow ran instead\. Inspect why and whether the omitted suite covers the changed entrypoint or an explicitly required gate\. If relevant, include that existing suite in a task\-owned test compilation configuration using existing dependencies; do not edit global configuration or invent another harness\. If it is not relevant or cannot run for a concrete dependency reason, state the exact coverage limit\. Do not count an unexecuted suite as passed or claim a similarly named suite is equivalent without evidence\.

Reuse unaffected results only when source/tests/fixtures/dependencies/settings/compiled outputs relevant to those results still match\. Do not rerun broad adjacent suites solely to increase totals; preserve the three historical unrelated failures without opportunistic fixes\.

## Independent re\-check must reach an actual recorded disposition

Use one read\-only reviewer, preferably the original instance if available, to inspect both the existing corrective delta and the newly authorized phrasing fix\. It may independently trace the reproducer while the sole coordinator edits; it must not modify source/tests, run a Host, send model requests or mutate consumers\.

If the original instance cannot resume, use one clearly identified replacement and preserve the original CHANGES\_REQUIRED as historical\. Capture the actual returned review verbatim with provenance at receipt, or have it write an artifact in its own evidence directory\. Do not leave the verdict only in an ephemeral message\.

Have it check the exact failures, three extraction branches, valid workload preservation, no\-write/missing\-input behavior and actual test execution\. Address concrete findings and have the changed portion re\-checked before closing\. A passing author suite is not an independent reviewer verdict\. If an unresolved requirement remains, report it precisely rather than promoting the result\.

## Close and prepare the installed successor without executing it

Return one concise report/result with confirmed causes, changed\-file/preimage identities, actual test commands/results, omitted\-suite disposition, real final reviewer verdict and limitations\. Record final reusable command/parameter locations; no new reporting framework or general reconciliation stage\.

If both defects are corrected and reviewed, record that each finding is closed at SOURCE scope only\. \.151 still contains the old parser\. Prepare the smallest distinguishable\-candidate follow\-up and expected Route B sequence: first prove the original env\-only input asks for the genuinely missing workload, then supply a concrete synthetic workload from the registered fixture contract, reach preview and decline the final write approval\. Do not inject participant session state or manufacture a candidate to bypass /create\. No candidate version is reserved or built by this task\.

Route A’s \.151 preview remains retained evidence; do not rerun it now\. For a future candidate, justify reuse from the actual affected dependency boundary rather than version alone\. Route B’s previous Escape was a clarification cancellation, not a product write\-approval cancellation\. Final Chat write approval remains unobserved in that task\.

Close with result pins and explicit source\-ownership release\. Preserve all prior scopes and open limits: spent write budgets; Base/Upgrade/B1/C1 acceptance; QA exception; R3/R4 uncertainty; document 10; OUTCOME\-DISCLOSURE\-001; diagnostic F\-1; historical CASE2 dispute; Windows case\-folding; three adjacent failures; trust/model/historical\-incident/toolchain/no\-lockfile/source/preservation limits\. Quarantine ends 2026\-09\-13 inclusive UTC with no automatic extension from September 14\. No RELEASE\_ACCEPTANCE or FULL\_PRODUCT\_OR\_ASKTD\_READINESS\. Demo remains deferred\.
