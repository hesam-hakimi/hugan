ETL-0904-IMPL04 — Phase W Review Repairs and Markdown Projection Fix

Paste this prompt into a fresh, high-reasoning local VS Code Agent chat on Windows. Use the normal local engineering Agent, not the ETL Orchestrator. This prompt supersedes ETL-0904-IMPL01, ETL-0904-IMPL02, and ETL-0904-IMPL03 for the work defined here. It does not authorize any execution beyond bounded read-only inspection and edits to the explicitly authorized files.

1. Owner authorization and task boundary

The owner authorizes one source-only repair task: close all four BLOCKER and all five MAJOR findings from independent ETL-0904-REVIEW01, while preserving the owner-ratified channel contract below.

You may:

• run read-only identity, status, hash, diff, file-search, and source-inspection commands needed for preflight and proof;
• edit only the three authorized files listed in §4;
• report newly discovered out-of-scope work as backlog candidates.

You may not:

• run type-check, compile, lint, unit/integration tests, the compiled runner, Extension Host, parser execution, package preparation, VSIX build/inspection, installation, activation, or any runtime command;
• run Git commands that mutate index, worktree, refs, stash, branch, or history;
• commit, push, merge, tag, publish, install, copy an extension, seed a profile, access real data, submit a job, or write to a consumer workspace;
• edit out/**, build-info, evidence, QA, installed-extension, profile, consumer-workspace, or Library files;
• accept, reject, Keep, Undo, discard, resolve, or otherwise manipulate pending VS Code chat edits;
• normalize line endings, format whole files, or repair unrelated findings;
• treat this implementation as qualification or certify your own work.

If a required fix needs another source file, stop before editing it and return BLOCKED_SCOPE_EXPANSION_REQUIRED with the exact path, symbol, reason, and minimum proposed change.

2. Required preflight — re-derive before editing

Verify all fields live. Do not infer them from this prompt.

```text
Active worktree:
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Linked primary worktree:
  C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Branch:
  fix/workspace-write-completion-0.3.148

HEAD:
  45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19

Manifest version:
  0.3.147

Extension identifier:
  td-etl.databricks-etl-copilot
```

Expected pre-task dirty inventory:

```text
 M .github/templates/request.md
 M src/extension.ts
 M src/test/runTest.ts
 M src/test/suite/index.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts
```

Also verify:

• staging area is empty;
• no index.lock exists in the linked-worktree Git metadata;
• src/core/sttm/SttmUnderstandingReportRenderer.ts is clean before this task;
• src/test/suite/index.ts still contains the exclusive focused loader implemented by ETL-0904-IMPL01 and is not edited here;
• the canonical policy contains exactly the 11 repository-defined paths in §3, with entry 4 exactly out/test/harness/mochaResultGuard.js;
• no type-check, compile, test, runner, or Host process is active;
• capture immediate pre-edit SHA-256 values, byte counts, line-ending counts, and status for every dirty path plus the renderer. Historical document hashes are not baselines.

If identity, HEAD, manifest, extension identifier, dirty path set, status code, staging state, or authorized-file cleanliness differs, stop with BLOCKED_BASELINE_DRIFT. Do not “repair” the baseline.

3. Contracts that govern this task

3.1 Owner-ratified source and target projections

```text
Structured source:  source_db.customers.cust_name
Markdown source:    customers.cust_name

Structured target:  target_db.tgt_customers.customer_name
Markdown target:    tgt_customers.customer_name
```

The independent reviewer proposed making the Markdown target fully qualified. That proposal is explicitly rejected. The owner instruction above wins: the product Markdown renderer must emit the short human projection; the structured channel retains the full machine identity. Do not weaken or change the oracle to match the current renderer.

Channel parity means identical mapping IDs, order, count, exclusions, and diagnostics. Display strings are related projections, not byte-identical strings. The test must assert the projection relation executably rather than store two unrelated literals. It must still derive the oracle independently of the product renderer/helper under test.

3.2 Formal verdict contract

• PASS: the intended public boundary is reached; exactly 8 focused tests are authored and evaluated; every required comparison passes; evidence is complete, valid, and durable; parent post-exit verification completes and passes; no infrastructure or evidence-write failure exists.
• FAIL: the intended public boundary is reached and a valid, independently derived product oracle observes a product-value mismatch, with complete valid evidence and no higher-priority infrastructure/evidence failure.
• BLOCKED: any pre-boundary, infrastructure, containment, provenance, incomplete-evidence, evidence-write, malformed-evidence, or post-exit-verification problem.

Infrastructure and evidence failures outrank product mismatch. Preserve multiple failures. Exit code 1 alone never classifies a product defect.

3.3 Canonical protected policy

The policy is one strictly ordinal-sorted repository-defined list:

```text
out/core/solution/FileSystemSttmDocumentReader.js
out/core/sttm/SttmExcelWorkbookParser.js
out/extension.js
out/test/harness/mochaResultGuard.js
out/test/runTest.js
out/test/suite/index.js
out/test/suite/sttmRealHostStructuredResult.test.js
out/test/testPatterns.js
out/tools/EtlReadOnlyToolService.js
out/tools/index.js
package.json
```

All protected counts derive from PROTECTED_POLICY_PATHS.length. No literal 8, 11, or 39 may independently define cardinality. The focused-suite expectation remains exactly 8 tests and is a separate invariant.

4. Authorized files

You may modify only:

1. src/core/sttm/SttmUnderstandingReportRenderer.ts
2. src/test/runTest.ts
3. src/test/suite/sttmRealHostStructuredResult.test.ts

Read-only comparison is allowed elsewhere. In particular, do not modify:

• .github/templates/request.md
• src/extension.ts
• src/test/suite/index.ts
• src/core/sttm/SttmMarkdownBundleParser.ts
• package.json
• tsconfig*.json
• out/**

Preserve each authorized file’s existing line-ending style. Make surgical edits only; no whole-file formatting or mechanical rewrite.

5. Required repairs

Repair B1 — owner-required Markdown target projection

In SttmUnderstandingReportRenderer.ts, change the Markdown mapping target from the fully qualified machine identity to the owner-required short human projection:

```text
tgt_customers.customer_name
```

Requirements:

• do not remove targetDb from the structured model or public structured result;
• keep Structured target target_db.tgt_customers.customer_name;
• make missing components explicit instead of silently collapsing via filter(Boolean).join('.') at the changed seam;
• keep legitimate human-contract entity absence distinguishable from an accidental missing entity;
• add no parser behavior in this task; if the renderer cannot satisfy the contract without a parser change, stop with BLOCKED_SCOPE_EXPANSION_REQUIRED naming src/core/sttm/SttmMarkdownBundleParser.ts and the precise missing input;
• in the test, derive the short Markdown target from independently parsed expected components, not from the production renderer or a second unrelated string literal.

Repair B2 — activation and parser-observer timing

The current etlWasActiveAtParserObserverInstallation observation is sampled before activation and contradicts later runner comparisons.

• retain a separately named pre-activation observation if useful;
• sample “active at parser observer installation” immediately before installation, after the tool invocation path has made activation necessary;
• make both fields semantically exact and machine-readable;
• never reinterpret a pre-activation false as an installation-time observation.

Repair B3 — failure precedence and classification

Refactor classification so that:

• infrastructure, containment, provenance, evidence-write, incomplete-evidence, and failed parent verification produce BLOCKED and outrank product mismatch;
• product FAIL promotion occurs only after the boundary and only with a valid independent oracle plus complete evidence;
• all failures are accumulated; the first product mismatch cannot mask target assertions or later infrastructure failures;
• machine-readable failureClassification supports at least none | product | infrastructure | evidence-write and may add a more specific non-breaking blocked subtype;
• runner exit status and recorded aggregate verdict are derived from the same final classification.

Repair B4 — enable the intended Test-mode registration gate

src/extension.ts reads ETL_TEST_READ_ONLY_TOOL_ONLY, but the runner did not set it.

• set ETL_TEST_READ_ONLY_TOOL_ONLY: "1" only in the focused Test-mode extensionTestsEnv;
• assert its exact value during the earliest evidence bootstrap that can still persist a failure;
• prove from captured real API evidence that etl_interpret_sttm is the intended visible tool;
• do not edit src/extension.ts or broaden production activation.

Repair M1 — non-vacuous Host PID observation

The Host-start PID regex cannot match the retained real log spelling, so liveness can pass vacuously.

• derive the two actual log spellings from retained captured logs; do not invent a pattern;
• encode them as separate anchored patterns with explicit capture groups;
• fail closed if no valid Host-start PID is observed;
• an empty PID list can never satisfy extensionHostsAliveAfterRunTests;
• preserve raw matched log lines and parsed PID evidence;
• report ambiguous/multiple identities as infrastructure-blocked unless the evidence contract explicitly permits and explains them.

Do not attempt the broader EPERM/PID-reuse redesign here; report it under NEW_BACKLOG_CANDIDATES only if additional detail is found.

Repair M2 — evidence assembly must not erase the original result

• establish evidence destination and authorization as early as safely possible;
• run the parent post-exit verification before final evidence assembly is declared complete;
• isolate capture, hashing, comparison assembly, and persistence failures;
• if full assembly fails, write one reduced, non-overwriting, machine-readable evidence record that preserves the original failure and identifies the secondary evidence failure;
• never let a later evidence exception erase or relabel the primary error;
• never overwrite a prior evidence file.

Repair M3 — evidence on every early focused-run failure

Move runnerEvidencePath establishment and focused evidence-write authorization immediately after the canonical evidenceRoot is known, before result-file, distinctness, preexistence, manifest, freshness, digest, and QA-root gates.

Requirements:

• every recoverable early failure after root establishment leaves evidence;
• QA-root resolution failure leaves evidence;
• an unrecoverable destination failure is explicit on stderr, uses nonzero exit, and is classified evidence-write/BLOCKED;
• stage tracking identifies the last completed gate;
• evidence uses exclusive creation and never falls back into repository, QA, consumer, or installed-extension locations.

Repair M4 — compiled-artifact provenance and unbundled Test-mode proof

Add future-run preconditions/evidence that can prove, without trusting timestamps alone:

• each protected out/** artifact corresponds to the reviewed source/configuration state;
• no protected artifact predates its source counterpart;
• the focused Host uses unbundled tsc output rather than a package-preparation bundle;
• out/extension.js still resolves the parser as the external module instance wrapped by the observer;
• package preparation would be detected as a different artifact shape;
• the result is labelled Test-mode-only and never promoted to installed/packaged VSIX proof.

Do not compile, bundle, or inspect a newly built artifact in this task. Implement only the fail-closed future checks and evidence schema.

Validate manifest provenance fields including canonical repositoryRoot, schema version, sort rule, generation time, manifest digest, exact path membership/order, and source/artifact relationship. A manifest supplied by an operator is not authoritative merely because its count matches.

Repair M5 — registration evidence comes from the API

• make etlToolsVisibleToRealApi the authoritative registration observation;
• assert exact expected visibility for the focused Test mode;
• keep Output-channel log matching advisory only;
• a log line can corroborate, but can never replace, missing API evidence.

Coupled repair C1 — total parser restoration and primary-error preservation

Close the reviewer’s coupled wrapper findings while already editing the same seam:

• enter the owning try before any statement that can throw after wrapper installation;
• make restoration unconditional in finally for fulfillment, rejection, assertion failure, observation failure, and timeout cleanup paths under the suite’s control;
• move/guard record() calls so none creates an uncovered leak window;
• verify module/export identity on installation and restoration;
• capture restorationError without masking the primary failure;
• surface restoration failure as an additional infrastructure comparison and classification;
• keep vscode.lm.invokeTool cardinality and parser invocation cardinality as separate direct observations.

Coupled repair C2 — independently falsifiable channel assertions

• capture source and target values for both channels before assertions;
• evaluate every source and target comparison independently so one mismatch cannot mask another;
• derive expected structured and Markdown projections from independent fixture components;
• assert the executable relation “Markdown = entity.field projection of Structured = db.entity.field” for source and target;
• do not import or call the product renderer/helper to generate the expected value;
• keep all comparison identities stable, unique, and machine-readable; update the expected comparison-ID list only when required and prove exact order/cardinality from source.

6. Required non-changes and deferred items

Do not fix these in this task:

• LF/CRLF normalization;
• generalized Host/runner path canonicalization;
• repository ↔ QA-root disjointness implementation;
• EPERM/PID-reuse hardening beyond the non-vacuous PID fix above;
• .github/templates/request.md corruption/disposition;
• pending chat-edit sessions;
• tracked build-info policy;
• vestigial compiler exclusions;
• F1/F3 quarantine;
• target-parser banner-row/heading repair in SttmMarkdownBundleParser.ts;
• ten action tools’ lack of a structured channel;
• package, installed-runtime, or /workflow qualification.

List any new information about these under DEFERRED_BACKLOG_UPDATES; do not edit them.

7. Static verification required before stopping

Without running TypeScript, tests, parser, runner, or Host:

1. re-read every changed hunk and its enclosing control flow;
2. prove each of B1–B4, M1–M5, C1–C2 against source with exact file/symbol references;
3. search for stale literals/fields that would contradict the new schema or precedence;
4. confirm src/test/suite/index.ts was not modified and its focused-loader contract is still consumed correctly;
5. confirm the 11 protected paths are strictly sorted and all protected cardinalities derive from the one list;
6. confirm the focused 8-test expectation remains separate;
7. compare immediate pre/post SHA-256 for every pre-existing dirty path and prove unauthorized paths are byte-identical;
8. report exact final Git status and diffstat;
9. run no formatter or command that writes generated output.

If static reasoning cannot establish a requirement, report UNVERIFIED_UNTIL_AUTHORIZED_<TYPECHECK|COMPILE|HOST>; do not claim it passed.

8. Required report

Return a concise but complete report with:

1. re-derived identity and exact pre-edit status;
2. immediate pre-edit hashes/baseline identity;
3. files and symbols changed;
4. a B1–B4, M1–M5, C1–C2 closure table with source references;
5. the exact structured/Markdown source and target contract as implemented;
6. failure-precedence state diagram or equivalent ordered description;
7. evidence-bootstrap, reduced-evidence, and parent-post-exit flow;
8. proof of unconditional parser restoration;
9. proof that API evidence, not logs, governs tool registration;
10. proof of 11-path policy and separate 8-test cardinality;
11. unresolved/static-only claims requiring future authorized execution;
12. deferred backlog updates;
13. exact final diffstat, status, and authorized/unauthorized path comparison.

End with exactly one result token:

```text
ETL_0904_IMPL04_RESULT: IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW
```

or one precise blocker token:

```text
ETL_0904_IMPL04_RESULT: BLOCKED_<REASON>
```

Then include exactly:

```text
AUTHORIZED_FILES_CHANGED: <comma-separated paths or NONE>
UNAUTHORIZED_FILES_CHANGED: <count>
TYPECHECK_OR_COMPILE_EXECUTED: NO
TEST_RUNNER_OR_HOST_EXECUTED: NO
PACKAGE_INSTALL_OR_CONSUMER_WRITE_EXECUTED: NO
COMMIT_PUSH_MERGE_OR_RELEASE_EXECUTED: NO
NEXT_REQUIRED_GATE: INDEPENDENT_SOURCE_REVIEW
```

Do not propose or execute the review, type-check, compile, Host run, package, install, commit, merge, or release inside this task.
