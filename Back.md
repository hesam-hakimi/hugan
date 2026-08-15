LOCAL_PHASE_SB2 — FRESH INDEPENDENT S-B CORRECTNESS, SECURITY, AND SCOPE AUDIT

You are a fresh independent auditor. You did not implement S-A or S-B and must not trust the implementation chat’s conclusions, tests, classifications, hashes, or PASS footer.

This is a repository-read-only audit. It does not authorize repair, Keep, S-C, Git actions, package work, or release work.

1. Established chronology

The current chronology is:

* S-A was independently audited, repaired, re-audited, hash-reconciled, and Kept.
* SB0 independently established a bounded S-B contract.
* ChatGPT authorized SB1 to create exactly three new S-B files.
* SB1 reports implementation complete, but no independent S-B audit has occurred.
* Keep and Undo have not been clicked.
* S-C remains unauthorized.

The only S-B candidate files are:

* src/core/agentContext/ResolvedEtlAgentContext.ts
* src/core/agentContext/EtlAgentContextCanonicalForm.ts
* src/test/suite/resolvedEtlAgentContext.test.ts

Expected self-reported sizes, to verify rather than assume:

* canonical-form module: approximately 639 lines;
* context/builder module: approximately 642 lines;
* test module: approximately 1210 lines;
* review card: three files, approximately +2494 -3.

Reconcile why a three-new-file card displays three deletions and prove the final on-disk candidate does not modify an existing file.

2. Known SB1 claims requiring independent verification

SB1 claimed:

* repository identity matched;
* staged count remained zero;
* pending paths changed from 20 to exactly 23;
* all four S-A files remained byte-identical to A1H;
* all 16 prior pending paths remained byte-identical;
* 38 focused S-B tests passed;
* 59 focused S-A tests passed;
* three new files linted successfully;
* full TypeScript checking returned the same 15 pre-existing errors, all in onboardingWriteApproval.test.ts, with zero S-B diagnostics;
* no S-C or later behavior was added.

Do not accept any claim without fresh evidence.

SB1 also disclosed:

1. The authorized integration wrapper invoked unpinned downloadAndUnzipVSCode, resolved stable VS Code 1.133.0, and downloaded approximately 325.93 MB into .vscode-test.
2. This download violated the explicit no-download restriction, even though .vscode-test was reported as Git-ignored with no pending entries.
3. The full integration suite was not run. Only grep-filtered S-B and S-A tests were executed.
4. npm run test:unit was not run.
5. The public ResolvedEtlAgentContext.schemaVersion type was declared as number, while runtime serialization enforced the value 1.
6. isPlainRecord, hasOwn, and ownValue were exported because the builder consumes them.
7. The canonical module exposes approximately 64 machine-only failure codes and several domain constants.

Independently determine the correctness, severity, and Keep impact of every item.

3. Expected repository identity

Reverify:

* Root: C:\repos\etl-extension\etl_fw2\etl_framework_extension
* Origin: https://github.com/TD-Universe/agentic_etl.git
* Branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* Three worktrees total
* Canonical main worktree only
* Staged count: 0
* Expanded pending count: 23

The four authoritative S-A hashes are:

* EtlSettingsInventory.ts
    6B99E6EB1851AB45050AE69225D06A59CE6AE0CE85871BF7A9C1DEAD0FBADD84
* EtlSettingsProvenance.ts
    09CD4A53A92D845D6C7F34279CBD2B2495F6C2EAE03D14567CBBC8474D553AC8
* EtlSettingsVsCodeBindings.ts
    0A010841E9806F6FDB51C35559EE20CB4A39A246F29001CA6A9DD749A3CD15D1
* settingsInventoryProvenance.test.ts
    64A4682CB2428B70F1E4B99B706A3050542502E14A57CC4BF7336D5711AB8AE2

If identity differs, staged count is nonzero, an S-A hash differs, the pending inventory is not exactly the original 20 plus the three S-B files, or another S-B/later-slice artifact exists, stop and return FAIL.

4. Strict prohibitions

Do not:

* edit, format, save, repair, rename, move, create, or delete any repository file;
* click Keep or Undo;
* stage, commit, push, stash, reset, checkout, merge, or change a worktree;
* modify package files, test registries, evaluation evidence, generated artifacts, or protected pending files;
* run npm install, npm ci, package, VSIX, smoke, PR, CI, or evaluation-regeneration commands;
* run npm run eval:golden;
* update, delete, clean, or redownload .vscode-test;
* use network access or invoke a command capable of downloading VS Code or other tooling;
* invoke the unpinned downloadAndUnzipVSCode wrapper;
* run node ./out/test/runTest.js if it can reach that downloader;
* repair the known type/API concerns;
* start S-C or add a consumer.

You may create a uniquely named audit directory under the operating-system temporary directory only for independently compiled test output or mutation probes. Do not create audit files inside the repository. You may remove only the temporary directory you created.

Capture start and end hashes for:

* all three S-B files;
* all four S-A files;
* all 16 pre-existing pending paths;
* package.json;
* package-lock.json;
* .tsbuildinfo.test;
* src/test/testPatterns.ts;
* relevant TypeScript configs;
* all four docs/eval/** evidence files;
* every additional protected path discovered at start.

5. Download-policy and cache assessment

Independently inspect .vscode-test without altering it.

Report:

* whether it exists;
* Git ignore rule and tracked/pending status;
* archive/extracted version;
* total size;
* relevant timestamps where reliably available;
* whether it contains any source or pending repository path;
* whether the download changed any tracked, staged, pending, package, S-A, or S-B byte;
* whether version 1.133.0 is being incorrectly used as evidence of compatibility with the repository minimum VS Code version.

The implementation’s admitted download is a process violation. Assess it separately from candidate source correctness. Do not silently excuse it and do not delete the cache.

No audit command may perform another download or network lookup.

6. Exact S-B contract audit

Independently verify that the context contains exactly six top-level fields:

* schemaVersion
* namespace
* contributionForm
* settings
* diagnostics
* contextDigest

Verify the permitted setting-entry and diagnostic fields against the ratified SB0 contract.

Prove that the public type is exactly:

* schemaVersion: 1

A public declaration of schemaVersion: number is not equivalent merely because runtime serialization rejects values other than 1. Treat that as a contract/type-soundness defect unless exact repository evidence proves otherwise.

Verify that all fields and arrays are deeply readonly at the public TypeScript boundary and immutable at runtime.

7. Public API and complexity audit

Inventory every export from both production S-B modules.

For every exported value, type, constant, helper, or error code, report:

* whether it was required by SB0;
* whether it is needed by a production cross-module call;
* whether it unnecessarily expands the public trust surface;
* whether it can be made module-private without adding a file;
* whether it exposes an unsafe generic primitive;
* whether downstream code could bypass the validated builder.

Pay particular attention to:

* isPlainRecord;
* hasOwn;
* ownValue;
* admitEtlAgentContextValue;
* canonicalization and digest functions;
* the six domain constants;
* the approximately 64 failure codes;
* TrustedEtlAgentContextInput;
* any exported payload type that permits constructing an invalid context.

Direct use by the sibling module is not, by itself, proof that an exported helper belongs in the intended public API.

Determine whether the implementation is materially over-engineered relative to the bounded S-B contract and whether complexity creates unreachable, contradictory, or untested failure outcomes.

8. S-A-to-S-B projection correctness

Using the actual S-A public unions and runtime shapes, verify that S-B correctly handles every applicable:

* manifest contribution form;
* descriptor shape;
* declared scope;
* omitted and explicit defaults;
* falsy or empty metadata;
* resolved provenance outcome;
* negative provenance outcome;
* duplicate declaration;
* malformed declaration;
* malformed configuration block;
* unavailable provenance;
* ambiguous resource selection;
* language-specific result.

Verify that:

* known-but-excluded S-A fields are safely dropped;
* legitimate S-A results are not rejected merely because they contain an expected outcome-specific field;
* unknown extra fields fail closed;
* duplicate, missing, mismatched, or conflicting setting/provenance correlations fail closed;
* winningScope is carried verbatim and never represented as the sole source of an object-valued setting;
* no configuration is reread;
* no VS Code binding is consumed;
* no S-A object or array is retained by reference.

9. Raw-value trust-boundary audit

Inspect the complete public result graph, failure graph, canonical form, and digest input.

Prove that none can expose, serialize, hash, log, or propagate:

* raw manifest defaults;
* raw effective values;
* raw per-scope values;
* title, description, markdownDescription, or category title;
* diagnostic/reason prose;
* resource URIs, fsPath, workspace folders, or physical paths;
* environment, deployment, job, provider, writer, merge-key, or onboarding values;
* credentials, secrets, tenant identifiers, or arbitrary unknown content.

Test with unique canary strings in every excluded input position and prove absence from:

* success results;
* failure results;
* thrown errors;
* canonical strings;
* digests and diagnostic metadata.

Do not use a redaction classifier as a substitute for structural exclusion.

10. Hostile-input and prototype safety

Independently inspect and probe:

* inherited properties;
* an own __proto__ data property;
* constructor and prototype keys;
* own accessor/getter/setter properties;
* throwing getters;
* symbol keys;
* non-enumerable keys;
* sparse arrays;
* arrays with extra string or symbol properties;
* class instances;
* null-prototype objects;
* proxies where safely testable;
* repeated shared references;
* true cycles;
* mutation during traversal;
* Date, Map, Set, RegExp, typed arrays, functions, symbols, and BigInt;
* NaN, infinities, -0, non-integers, and unsafe integers.

Determine whether any validation operation invokes attacker-controlled getters or proxy traps before failing closed. Missing required protection is a material trust-boundary finding.

Verify depth semantics precisely:

* root depth 0;
* depths through 32 accepted when otherwise valid;
* attempted descent to 33 rejected;
* no off-by-one behavior;
* no partial result;
* bounded stack usage.

11. Immutability and determinism

Verify:

* complete defensive copying;
* no caller-owned reference retained;
* recursive freezing of every returned object and array;
* absent optional properties are truly omitted;
* defined false and empty arrays are preserved;
* mutation of source after construction has no effect;
* mutation of returned context throws or cannot change state;
* repeated equal constructions have different identities but equal structures and digests;
* no mutable cache or global task state;
* stable ordering across repeated processes.

Check whether a traversal-local WeakSet incorrectly conflates harmless shared references with cycles and whether that behavior is deterministic and contract-compatible.

12. Canonical serialization and digest

Independently verify:

* exact prefix etl.agent.context.v1\n;
* canonical JSON follows the prefix with no ambiguous separator;
* ascending UTF-16 code-unit object-key ordering;
* no localeCompare;
* semantically meaningful array order preserved;
* sparse arrays rejected;
* strings preserved without normalization or case folding;
* correct escaping of quotes, backslashes, controls, and Unicode;
* absent/undefined optional properties omitted;
* null rejected;
* only finite safe integers admitted;
* invalid numbers and unsupported values rejected;
* duplicate semantic setting keys rejected;
* unknown fields rejected;
* no generic raw-input JSON.stringify path;
* contextDigest excluded from its own input;
* SHA-256 computed over exact UTF-8 canonical bytes;
* lowercase 64-character hexadecimal digest;
* version/domain separation effective;
* independent recomputation produces the stored digest.

Produce at least one complete independently calculated canonical-string and digest fixture that does not reuse production serializer logic.

13. Test-quality and executable evidence

Inspect all 38 candidate tests.

Determine:

* which requirements are only source-text assertions;
* whether expected values are independently authored;
* whether tests mirror implementation tables/constants;
* whether compile-time literal typing of schemaVersion is actually tested;
* whether all 64 failure codes are reachable or meaningfully covered;
* whether hostile getters, symbols, sparse arrays, unknown keys, duplicates, mismatches, raw-value canaries, and prototype cases are covered;
* whether the test can pass while material behavior is broken.

Run an independent no-network validation using only already-installed tooling.

Preferred approach:

1. Run the existing local TypeScript compiler with --noEmit.
2. Separate the known 15 pre-existing diagnostics from any S-B diagnostic.
3. Compile the necessary S-B sources/tests into the authorized OS temporary audit directory using existing local tooling and no dependency download.
4. Execute focused tests or independent probes from that temporary output.
5. Prove the repository test glob would discover the S-B test without modifying testPatterns.ts.

Do not use the downloading test wrapper.

If an already-cached VS Code executable can be invoked directly and offline without modifying .vscode-test, use a separate temporary user-data/extensions directory and report the exact command. Otherwise do not invoke Electron.

Perform bounded mutation tests in the temporary copy for critical rules such as:

* disable key sorting;
* include manifestDefault;
* skip deep freezing;
* include contextDigest in digest input;
* accept depth 33;
* accept an unknown raw field.

Each mutant should cause an appropriate existing test to fail. Do not mutate repository files.

Report exact commands, exit codes, passing/failing/pending/total counts, and proof that the intended test file executed.

If independent executable evidence cannot be obtained without a new download or repository mutation, report missing evidence and do not pass the audit.

14. Minimum-runtime compatibility

Do not treat the downloaded VS Code 1.133.0 test execution as minimum-version evidence.

Verify the production S-B source against:

* repository engines.vscode;
* repository TypeScript version and target;
* repository Node/runtime assumptions;
* APIs actually available to the extension’s minimum supported runtime.

Prove both production files import no vscode and use no newer unsupported runtime feature.

15. Unrelated-failure separation

Independently reproduce or inspect the 15 TypeScript diagnostics.

For each unique diagnostic:

* identify exact file and symbol;
* prove whether it references either S-B production file or S-B test;
* show the dependency route through the pre-existing EtlActionToolService.ts modification where applicable;
* do not repair it.

Inspect the stale Phase-H baseline separately.

Do not regenerate it. Prove whether its stale tracked-input set predated S-B and distinguish the two newly added src/core/** S-B paths from the pre-existing differences.

A globally red compile is not a candidate pass unless zero S-B diagnostics are independently demonstrated.

16. Scope closure and end integrity

Prove:

* only the three named files implement S-B;
* no existing file was changed by SB1;
* no S-C or later behavior exists;
* no runtime consumer exists;
* no barrel or registration file was added;
* no configuration-writing behavior exists;
* no package, Git, PR, CI, or VSIX action occurred;
* all 20 prior pending paths remain outside the S-B Keep decision;
* all protected files are byte-identical start-to-end;
* all three S-B files are byte-identical start-to-end;
* staged count remains zero.

Return full start and end SHA-256 values for every S-B file.

17. Required findings and verdict

Return:

1. Audit identity and repository verification.
2. Start-state inventory and hashes.
3. Severity-ranked findings with exact file:line citations.
4. Download/cache process-compliance assessment.
5. Type and public-API assessment.
6. S-A projection assessment.
7. Raw-value and hostile-input assessment.
8. Immutability/determinism assessment.
9. Canonicalization/digest assessment.
10. Test-quality, discovery, mutation, and executable evidence.
11. Runtime compatibility assessment.
12. Unrelated-failure separation.
13. Scope-closure proof.
14. End-state inventory and hash comparison.
15. Smallest three-file-only repair plan if any defect remains.
16. Final verdict.

A public schemaVersion: number where the ratified contract requires literal 1 is not a pass.

Missing independent executable evidence is not a pass.

A material correctness, security, determinism, immutability, type-soundness, public-boundary, compatibility, or scope defect is not a pass.

The download-policy violation must be recorded even if it caused no candidate/source drift.

This audit never authorizes Keep itself. S-C must always remain unauthorized.

Finish with exactly one block and no text after it.

PASS:

S_B_CANDIDATE_BYTES_STABLE: YES
S_B_SCOPE_EXACT: YES
SCHEMA_VERSION_LITERAL_CONTRACT_MET: YES
PUBLIC_API_BOUNDARY_ACCEPTABLE: YES
RAW_VALUE_TRUST_BOUNDARY_SAFE: YES
CANONICAL_DIGEST_CONTRACT_SAFE: YES
IMMUTABILITY_AND_DETERMINISM_SAFE: YES
INDEPENDENT_FOCUSED_TESTS_PASS: YES
SB1_DOWNLOAD_POLICY_VIOLATION_CONFIRMED: YES
DOWNLOAD_CAUSED_TRACKED_OR_PENDING_DRIFT: NO
SAFE_TO_KEEP_SB_CANDIDATE: YES
KEEP_ACTION_AUTHORIZED_BY_THIS_AUDIT: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB2_INDEPENDENT_AUDIT_PASS

FAIL:

S_B_CANDIDATE_BYTES_STABLE: YES|NO
S_B_SCOPE_EXACT: YES|NO
SCHEMA_VERSION_LITERAL_CONTRACT_MET: YES|NO
PUBLIC_API_BOUNDARY_ACCEPTABLE: YES|NO
RAW_VALUE_TRUST_BOUNDARY_SAFE: YES|NO
CANONICAL_DIGEST_CONTRACT_SAFE: YES|NO
IMMUTABILITY_AND_DETERMINISM_SAFE: YES|NO
INDEPENDENT_FOCUSED_TESTS_PASS: YES|NO
SB1_DOWNLOAD_POLICY_VIOLATION_CONFIRMED: YES|NO
DOWNLOAD_CAUSED_TRACKED_OR_PENDING_DRIFT: YES|NO
SAFE_TO_KEEP_SB_CANDIDATE: NO
KEEP_ACTION_AUTHORIZED_BY_THIS_AUDIT: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB2_INDEPENDENT_AUDIT_FAIL
