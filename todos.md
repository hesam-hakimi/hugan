Repair A — Canonical runtime-artifact contract and public discovery parity

Execution environment

Run this task only in the normal writable VS Code source-repository Agent/Claude session opened at:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Do not run it in:

* the Extension Development Host;
* the isolated F5 QA workspace;
* a consumer workspace;
* the ETL Orchestrator chat;
* an ETL Verifier or other read-only agent;
* the previous Repair B conversation.

This is Repair A only.

Ignore the earlier Repair B prompt. No REPAIR_A_FULL_SHA placeholder applies to this task.

Mandatory capability gate

Before running tests or editing files, confirm that this session provides:

* repository-scoped file reading;
* Write or Edit file-authoring capability;
* terminal execution.

If Write/Edit is unavailable:

* do not attempt terminal redirection, PowerShell file writes, scripts, patches, or another editing fallback;
* do not modify anything;
* report WRITE_EDIT_UNAVAILABLE;
* finish with:

REPAIR_A_CONTRACT_DISCOVERY_BLOCKED

PowerShell PATHEXT requirement

This environment has a known process-local PATHEXT problem. Each new PowerShell tool invocation may inherit only .CPL.

At the beginning of every independent PowerShell terminal invocation that calls git, node, npm, npx, or cmd, set this in the same invocation:

$env:PATHEXT = '.COM;.EXE;.BAT;.CMD';

Shell state does not persist between tool calls, so repeat it for every independent PowerShell invocation.

Do not use setx.

Do not modify Windows user/system environment variables, the registry, PowerShell profiles, VS Code settings, or repository files to persist this workaround.

Pinned source identity

The only permitted starting state is:

* repository:
    C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
* branch:
    fix/workspace-write-completion-0.3.148
* baseline HEAD:
    a7ec7284906897321b2af5f7bf99de99211f7b70
* baseline HEAD subject:
    test: refresh Phase H evaluation baseline
* sole parent/W1 commit:
    cb972b7bee10ee43690097a40b6b29b474b18276
* baseline grandparent/Repair13:
    64706129e0d1054ea615e150b28dd623fb3c629e

These are full SHAs. Do not substitute a short SHA or infer a nearby commit.

Objective

Implement one bounded producer-side repair so the registered read-only ETL discovery tools expose the repository-owned canonical executable job-config contract consistently in both:

* source/F5 layout;
* packaged-VSIX layout.

This task does not repair validator consumers. Repair B must not begin in this run.

Evidence classification:

QA-proven blockers

* Public discovery did not expose enough executable-envelope information for authoritative artifact construction.
* Permitted job-config extensions were not discoverable through the public contract/tools.

Independently source-audit-proven defects

* Development and packaged module-reference precedence differs.
* The authoritative contract does not publish the job-config extension rule.

Separate blocker — report only

* The current QA workspace has no deterministic physical source, target, and environment fixture.

Do not describe this as a W1/write failure. The Orchestrator stopped before render, validation, preview, confirmation, or write.

Do not claim that Repair A alone fixes end-to-end F5 QA.

Phase 0 — Fail-closed repository preflight

Before editing anything, report:

* resolved repository root;
* current branch;
* exact HEAD SHA and subject;
* exact HEAD parent SHA;
* exact HEAD grandparent SHA;
* git rev-list --parents -n 1 HEAD;
* concise commit graph around HEAD;
* git status --short --untracked-files=all;
* staged-path inventory;
* untracked-path inventory.

Verify all of the following:

1. Repository root is exact.
2. Branch is exact.
3. HEAD exactly equals:
    a7ec7284906897321b2af5f7bf99de99211f7b70
4. HEAD subject exactly equals:
    test: refresh Phase H evaluation baseline
5. git rev-list --parents -n 1 HEAD shows exactly one parent.
6. The sole parent exactly equals:
    cb972b7bee10ee43690097a40b6b29b474b18276
7. HEAD^^ exactly equals:
    64706129e0d1054ea615e150b28dd623fb3c629e
8. Index is clean.
9. Working tree is clean.
10. Untracked-path count is zero.

Stop immediately if any check differs.

Do not fetch, pull, merge, rebase, reset, checkout, stash, clean, amend, cherry-pick, or repair repository state.

Phase 0A — Protected-file baseline

Obtain the changed-path inventories from:

* W1 commit:
    cb972b7bee10ee43690097a40b6b29b474b18276
* Eval-refresh commit:
    a7ec7284906897321b2af5f7bf99de99211f7b70

Use Git-native inspection such as git diff-tree --no-commit-id --name-status -r.

For every inventoried path, record its baseline state as it exists at baseline HEAD:

* path;
* present or absent;
* Git blob OID when present.

Keep this manifest in the task report/in-memory evidence only. Do not create a repository manifest file.

Before editing, compare the intended Repair A production and test paths against both protected inventories.

If any intended changed path overlaps a W1 or Eval-refresh protected path, protection wins:

* do not edit the overlapping path;
* stop and report the overlap;
* finish blocked.

Use Git diff/blob identity rather than OS-level hashes where possible to avoid CRLF ambiguity.

Phase 0B — Grounded test baseline

Before adding characterization tests or changing production code:

1. Read applicable repository-local contributor and agent instructions completely.
2. Inspect existing package scripts and test conventions.
3. Run the existing compile/typecheck command.
4. Run the full unit suite once.
5. Record:
    * exact command;
    * total tests;
    * passed tests;
    * failed tests;
    * skipped tests;
    * exact failing test names;
    * exact failure signatures and root causes.

A failure count alone is not a valid baseline.

Stop if the pre-change suite contains an unexplained failure.

Phase 1 — Characterization tests before production edits

Add focused characterization tests before changing production code.

Run them against unchanged production code and record the expected red results.

The tests must exercise both direct service methods and the real registered public-tool boundary.

A. Direct service layer

Exercise the real service implementations corresponding to:

* EtlReadOnlyToolService.getFrameworkRules;
* EtlReadOnlyToolService.describeModule('data_sourcing_process').

Do not fabricate a replacement service object.

B. Registered public-tool boundary

Invoke the registered tools through their real BaseReadOnlyTool.invoke path:

* etl_get_framework_rules;
* etl_describe_module.

Inspect the actual public structured application/json payload.

Do not test only a private helper.

Where the tools currently return Markdown or textual content, verify that channel as well so backward compatibility remains protected.

C. Source/package layout parity

Characterize both layouts:

1. Development/source layout where:
    docs/reference/ETL_MODULE_REFERENCE.md
    is present.
2. Packaged-only layout where the development document is absent and:
    resources/copilot/context/etl-module-reference.md
    is available.

Prove whether the two layouts currently expose equivalent authoritative executable-envelope semantics.

Ephemeral test-only temporary directories and inline test data are allowed for layout simulation.

Do not add a tracked deterministic F5/STTM/physical source/target/environment fixture.

D. Contract discoverability

Characterize whether the public service and registered-tool payloads currently expose:

* authoritative modules root semantics;
* stage-keyed module entries;
* module dispatch field;
* method dispatch field;
* default method;
* accepted object-opening separators;
* module/stage order;
* required module keys;
* required option keys;
* permitted job-config extensions.

Characterize that .conf and .json are not currently discoverable from the authoritative public contract/tool payloads.

Each characterization failure must arise from the audited product defect—not broken registration, incorrect mocks, path mistakes, or malformed tests.

If a claimed defect does not reproduce:

* do not edit production code;
* remove only the characterization-test changes created during this task using the available file-authoring tools;
* verify the repository returns to its clean baseline;
* report the discrepancy;
* finish blocked.

Do not commit a red-test-only checkpoint.

Allowed production scope

Production edits are limited to the smallest necessary hunks in:

1. resources/framework/contracts/job-config-envelope.v1.json
2. src/core/framework/TrustedJobConfigEnvelopeResolver.ts
3. src/tools/EtlReadOnlyToolService.ts
4. resources/copilot/context/etl-module-reference.md
5. docs/reference/ETL_MODULE_REFERENCE.md
6. package.json — only the existing jobConfigPath or directly related tool-description text

Focused test changes are allowed only under src/test/** and only for:

* trusted contract resolution/fingerprint behavior;
* direct read-only discovery;
* registered public-tool invocation;
* structured application/json payloads;
* source/package reference parity;
* directly related backward-compatibility regression coverage.

Before editing, list the exact proposed test paths.

No other production or test path is authorized.

If implementation requires another production path, generated copy, manifest, lockfile, helper, fixture, or test category, stop and report the required scope expansion before touching it.

Production hunk boundaries

Contract JSON

Changes are limited to:

* the authoritative job-config extension field;
* authoritative executable-envelope semantic fields proven missing from public projection;
* the contract fingerprint required by the repository’s existing canonicalization process.

Do not redesign unrelated contract sections.

TrustedJobConfigEnvelopeResolver

Changes are limited to:

* validation/resolution of newly published authoritative contract fields;
* deterministic shared projection of contract data;
* existing canonical fingerprint computation and verification.

Do not loosen or bypass fail-closed validation.

EtlReadOnlyToolService

Changes are limited to:

* obtaining the contract through TrustedJobConfigEnvelopeResolver;
* one shared deterministic contract projection;
* getFrameworkRules;
* describeModule;
* necessary reference-source ordering/import changes.

Both public tools must consume the same shared authoritative projection.

Do not place independently maintained copies of the contract in each tool.

Do not change:

* etl_search_examples root selection;
* local-workspace example precedence;
* snippet sizing;
* snippet whitespace behavior;
* search ranking;
* unrelated tool output;
* global formatting.

package.json

Only the existing job-config-path/tool description may change.

Do not change:

* package version;
* dependencies;
* devDependencies;
* scripts;
* activation events;
* commands;
* contributed tool schemas unrelated to the job-config description.

Reference documents

Changes are limited to making the development and packaged references agree with the trusted executable-envelope contract.

Do not add unrelated documentation.

No broad formatting or cleanup is allowed in any production file.

Required implementation behavior

Treat:

resources/framework/contracts/job-config-envelope.v1.json

resolved by TrustedJobConfigEnvelopeResolver, as the single source of authority.

Do not duplicate an independently maintained job envelope in tool/service code.

Publish through both read-only tools, using existing response conventions, the authoritative structural semantics required to create structurally valid job-config bytes when mapping and physical fixture values are available.

The shared public projection must include, using repository-owned field names:

* modules as the root object;
* stage-keyed module entries;
* options.module as module dispatch;
* options.method as method dispatch;
* default method process;
* accepted separators:
    * colon;
    * equals;
    * omitted-before-open-brace;
* stage/module ordering;
* per-module required module keys;
* per-module required option keys;
* permitted job-config extensions exactly:
    * .conf
    * .json

Do not advertise or permit .yaml or .yml for job configs.

Do not change environment-config extension behavior.

Preserve:

* existing public fields;
* existing Markdown/text output;
* existing MIME/result-envelope behavior;
* deterministic ordering where required;
* backward compatibility for existing consumers.

Source/F5 and packaged-VSIX convergence

Ensure:

* the packaged canonical reference is not shadowed by the development-only non-executable reference;
* the development reference’s executable example agrees with the trusted contract;
* packaged resources remain usable when docs/** is absent;
* source/F5 and packaged-only layouts return equivalent authoritative contract semantics.

Do not modify .vscodeignore.

Do not change etl_search_examples behavior or local-workspace precedence.

Contract fingerprint

Recompute the trusted-contract fingerprint only through the repository’s existing canonicalization implementation.

Report:

* previous fingerprint;
* new fingerprint;
* the exact existing repository mechanism used to recompute it.

Do not:

* guess the fingerprint;
* add a second canonicalization implementation;
* disable verification;
* bypass mismatch detection;
* loosen fail-closed behavior.

If the correct fingerprint update requires changing another tracked path outside the allowlist, stop for scope review.

Explicit non-goals and protected boundaries

Do not modify:

* src/tools/EtlActionToolService.ts;
* DataSourcingConfigValidator;
* ModuleSequenceExtractor;
* any validator consumer;
* any W1-owned file or hunk;
* any Eval-refresh/report file;
* STTM workbooks;
* job configs;
* environment configs;
* deterministic QA fixtures;
* package version;
* dependencies or lockfiles;
* release notes;
* generated build or VSIX artifacts;
* sibling etl-framework-gen-utils;
* external repositories.

Do not change or invoke:

* writeToWorkspace;
* performWrite;
* preview;
* approval;
* confirmation;
* consent;
* probing;
* authorization;
* manifest construction;
* collision handling;
* checksum handling;
* drift handling;
* filesystem write behavior;
* write-result construction;
* renderer/scaffolding architecture.

Do not:

* run F5;
* build, install, or package a VSIX;
* access external services;
* create another branch;
* push;
* publish;
* rewrite Git history.

Phase 2 — Required validation after implementation

After production changes, run in this order:

1. git diff --check
2. repository compile/typecheck
3. focused contract-schema tests
4. focused contract-fingerprint tests
5. focused direct-service discovery tests
6. focused registered public-tool tests inspecting real structured application/json
7. Markdown/backward-field compatibility tests
8. source-present versus packaged-only reference-parity tests
9. focused W1 regression tests without modifying W1 tests
10. full unit suite once

The focused tests must prove:

* characterization tests were red before production edits and green afterward;
* both read-only tools expose the same shared authoritative contract semantics;
* the registered public-tool result contains structured JSON—not merely a textual summary;
* .conf and .json are discoverable;
* .yaml and .yml are not advertised for job configs;
* source/F5 and packaged-only layouts return equivalent contract semantics;
* the corrected development example parses as the trusted modules { ... } envelope;
* existing public fields and Markdown remain available;
* local consumer-example precedence is unchanged;
* tampered trusted contract content still fails closed during fingerprint verification.

Full-suite reconciliation gate

Do not authorize a commit because a total failure count matches an expected number.

A remaining full-suite failure is permitted only when:

1. its exact test identity and failure signature match the grounded pre-change baseline; or
2. it is an exact EvalGating freshness failure caused solely by intentionally leaving the separately owned evaluation snapshot unchanged; and
3. repository evidence proves the failure is unaffected by the Repair A diff.

Record a before/after table containing:

* exact test identity;
* pre-change signature;
* post-change signature;
* classification;
* reason it is unaffected.

Any new, missing, renamed, similar-looking, unexplained, or differently rooted failure blocks the commit.

Do not refresh Eval artifacts in this task.

The exact reconciled baseline failure identities and signatures must be included in the final report for use by Repair B.

Pre-commit protection gate

Before committing:

1. Show git diff --check.
2. Show git diff --stat.
3. Show git diff --name-status relative to:
    a7ec7284906897321b2af5f7bf99de99211f7b70
4. Show the complete production and test diff.
5. Prove every changed path and hunk is within the allowlist.
6. Compare the final protected presence/blob manifest with the Phase 0A baseline.
7. Prove every W1-protected path is unchanged.
8. Prove every Eval-refresh-protected path is unchanged.
9. Prove src/tools/EtlActionToolService.ts is unchanged.
10. Prove validator consumers are unchanged.
11. Prove etl_search_examples behavior is unchanged.
12. Prove package.json changed only in the permitted description hunk.
13. Prove package version, dependencies, and lockfiles are unchanged.
14. Prove no deterministic fixture or generated artifact was added.
15. Confirm all focused tests pass.
16. Reconcile every full-suite failure by exact identity.

If any gate fails, do not commit.

Commit gate

Only if every gate passes, create exactly one commit with subject:

fix: expose canonical runtime artifact contract

The commit must:

* have sole parent:
    a7ec7284906897321b2af5f7bf99de99211f7b70
* contain only Repair A changes;
* not amend or squash existing commits;
* not create another branch;
* not be pushed.

After committing, verify:

* exactly one new commit exists above the pinned baseline;
* the new commit has exactly one parent;
* its parent is the pinned baseline;
* its subject is exact;
* worktree and index are clean;
* untracked-path count is zero.

Final report

Report:

* repository root;
* branch;
* pinned baseline HEAD;
* baseline parent and grandparent;
* new Repair A full commit SHA;
* new commit parent SHA;
* exact changed paths;
* production hunk summary;
* pre-fix characterization results;
* post-fix focused-test results;
* old/new trusted-contract fingerprint;
* before/after full-suite failure table with exact identities and signatures;
* protected W1/Eval presence/blob comparison;
* package version/dependency/lockfile protection results;
* confirmation that no validator, W1 write behavior, fixture, F5, VSIX, external service, push, or publication occurred;
* final git status --short --untracked-files=all.

Do not claim end-to-end F5 QA is fixed.

Do not begin Repair B.

End with exactly one marker:

REPAIR_A_CONTRACT_DISCOVERY_COMMITTED

or, if any gate blocks completion:

REPAIR_A_CONTRACT_DISCOVERY_BLOCKED
