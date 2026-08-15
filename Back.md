LOCAL_PHASE_SB1 — BOUNDED S-B IMPLEMENTATION

Continue in this same SB0 chat and use your immediately preceding read-only report as the authoritative live-source contract.

This follow-up supersedes the prior read-only restriction only for creating the exact three authorized S-B files below. Every other restriction remains in force.

1. Authorization boundary

S-B implementation is now authorized, limited to exactly these three new files:

* src/core/agentContext/ResolvedEtlAgentContext.ts
* src/core/agentContext/EtlAgentContextCanonicalForm.ts
* src/test/suite/resolvedEtlAgentContext.test.ts

No existing file may be edited.

Do not create an index.ts, barrel export, documentation file, snapshot, registry entry, fixture file, configuration file, or any fourth S-B file.

Do not click Keep or Undo when implementation finishes.

This authorization does not authorize:

* S-C or any later slice;
* a production/runtime consumer;
* changes to TrustedPlanningEvidenceService.ts;
* any repair of S-A or its open findings;
* changes to testPatterns.ts;
* regeneration of Phase-H evaluation evidence;
* package, VSIX, Git, PR, or CI actions.

2. Ratified ChatGPT decisions

The following decisions are now confirmed and are not open for reinterpretation:

1. Raw manifestDefault is excluded.
    * Carry only hasManifestDefault: boolean.
    * Never copy, expose, serialize, log, or digest the default value itself.
2. The S-B defensive traversal depth bound is 32.
    * Treat the root admitted input as depth 0.
    * Descending into an object or array increments the depth.
    * Depths through 32 are permitted.
    * Any attempted descent beyond 32 fails closed.
    * Return no partial context.
    * Do not reuse S-A’s unbounded recursive helper.
3. Use the already-existing integration discovery route:
    * src/test/suite/resolvedEtlAgentContext.test.ts
    * existing suite/**/*.test.js integration glob
    * zero edits to src/test/testPatterns.ts
    * no new test registration route.
4. Use direct relative imports. Do not add or edit a barrel file.
5. The stale phase_h_latest_report.json / evalGating.test.ts condition is pre-existing.
    * Do not repair or regenerate it.
    * Do not run npm run eval:golden.
    * If encountered, separate it from S-B results using exact path and dependency evidence.
6. TrustedPlanningEvidenceService.ts remains an S-C owner decision.
    * Do not import, modify, supersede, or integrate it in S-B.
7. The current package.json/installed-extension version difference is pre-existing and unrelated.
    * Do not reconcile or modify it.
8. S-B has no runtime consumer yet.
    * Do not wire it into bindings, planners, agents, routers, bootstrap, or action executors.
    * Runtime propagation remains S-D work.

3. Mandatory preflight

Before editing anything, reverify:

* Root: C:\repos\etl-extension\etl_fw2\etl_framework_extension
* Origin: https://github.com/TD-Universe/agentic_etl.git
* Branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* Canonical main worktree only
* Three worktrees total
* Staged count: 0
* Total pending paths with untracked files expanded: 20
* No S-B file already exists

Recompute the four complete S-A hashes:

* src/core/settings/EtlSettingsInventory.ts
    6B99E6EB1851AB45050AE69225D06A59CE6AE0CE85871BF7A9C1DEAD0FBADD84
* src/core/settings/EtlSettingsProvenance.ts
    09CD4A53A92D845D6C7F34279CBD2B2495F6C2EAE03D14567CBBC8474D553AC8
* src/core/settings/EtlSettingsVsCodeBindings.ts
    0A010841E9806F6FDB51C35559EE20CB4A39A246F29001CA6A9DD749A3CD15D1
* src/test/suite/settingsInventoryProvenance.test.ts
    64A4682CB2428B70F1E4B99B706A3050542502E14A57CC4BF7336D5711AB8AE2

Capture full SHA-256 hashes for all 16 pre-existing/user-owned pending paths and every other protected path identified in SB0, including:

* .tsbuildinfo.test
* package.json
* package-lock.json
* src/test/testPatterns.ts
* all prior A0R and c7 files
* all docs/eval/** evidence relevant to the stale Phase-H gate

If repository identity differs, staged count is nonzero, an S-A hash differs, the pending set differs unexpectedly, or an S-B artifact already exists, stop without editing and return BLOCKED.

4. Exact S-B contract

Implement the exact schema and trust-boundary table ratified in your SB0 report.

The context is a deeply immutable ResolvedEtlAgentContext containing only:

Top-level fields

* schemaVersion: 1
* namespace: string
* contributionForm
* settings: readonly ResolvedSettingContextEntry[]
* diagnostics: readonly ContextDiagnostic[]
* contextDigest: string

Permitted setting-entry fields

* key
* effectiveScope
* scopeDeclaration
* optional declaredTypes
* hasManifestDefault
* folderConfigurable
* languageOverridable
* provenanceOutcome
* optional effectiveValueDefined
* optional contributingScopes
* optional winningScope
* optional resourceProvided
* optional languageIds

Preserve defined falsy and empty values. An optional property whose source is absent must be omitted rather than created with an undefined value.

Treat winningScope only as the highest-precedence contributor. Do not describe it as the sole value source because VS Code can merge object-valued settings.

Permitted diagnostic fields

* code
* optional key
* optional categoryIndex
* optional declarationCount

Diagnostics must contain machine-safe metadata only.

Explicit exclusions

Do not carry:

* raw manifest defaults;
* raw effective or per-scope configuration values;
* title, description, markdownDescription, or category title;
* diagnostic or negative-outcome prose/reason strings;
* URIs, fsPath, workspace roots, folders, or resource objects;
* environment, deployment, business, job, provider, writer, merge-key, or onboarding values;
* credentials, secrets, tenant-specific values, or physical-storage values;
* bootstrap/result envelopes, drift state, overrides, persistence, registry, deployment path, or publisher identity.

5. Builder and immutability behavior

Implement a pure builder equivalent to:

buildResolvedEtlAgentContext(input): BuildContextResult

It must:

* accept already-computed S-A inventory and provenance results;
* never read VS Code configuration;
* never import or invoke EtlSettingsVsCodeBindings;
* perform zero configuration, filesystem, network, environment, or secret-storage reads;
* validate input shapes at runtime;
* use only own enumerable properties;
* never trust inherited members;
* reject unknown or unsupported own fields that could become a raw-value pass-through;
* safely handle an own __proto__ data key without prototype pollution;
* validate every languageIds and declaredTypes element;
* detect duplicate, missing, conflicting, or otherwise invalid correlations fail-closed;
* defensively copy every admitted value;
* retain no S-A object or array by reference;
* recursively freeze every returned object and array;
* detect cycles using a traversal-local WeakSet;
* enforce the confirmed depth limit of 32;
* return a discriminated success/failure result;
* return stable machine-only failure codes with no echoed input values;
* return no partial context on failure;
* use no mutable shared cache.

Two constructions from semantically equal inputs must produce:

* structurally equal contexts;
* different object/array identities;
* identical canonical strings;
* identical digests.

6. Canonical serialization

Implement the canonical serializer in:

src/core/agentContext/EtlAgentContextCanonicalForm.ts

The exact canonical form must:

* begin with etl.agent.context.v1\n;
* include canonical JSON for the closed S-B field allow-list;
* exclude contextDigest from its own digest input;
* sort object keys in ascending UTF-16 code-unit order;
* never use localeCompare;
* preserve semantically meaningful array order, including contributingScopes and languageIds;
* omit absent/undefined optional fields;
* reject null;
* preserve strings byte-for-byte with no Unicode normalization or case folding;
* JSON-escape admitted strings and booleans;
* admit only finite safe integers for numeric fields;
* reject NaN, Infinity, -Infinity, -0, non-integers, and unsafe integers;
* reject functions, symbols, BigInt, Date, Map, Set, RegExp, class instances, and unsupported prototypes;
* reject duplicate semantic setting keys and ambiguous inputs;
* fail closed with a machine code and no echoed raw content.

Do not use a generic pass-through JSON.stringify(input) design. Serialization must operate on the validated closed representation only.

7. Digest contract

Implement deterministic SHA-256 using the existing runtime facility:

createHash('sha256').update(canonicalString, 'utf8').digest('hex')

Requirements:

* import from node:crypto;
* add no dependency;
* digest the exact UTF-8 bytes of the complete version-prefixed canonical string;
* exclude contextDigest from those bytes;
* return lowercase 64-character hexadecimal output;
* store the digest in the frozen context;
* make it independently recomputable from that context;
* ensure the version/domain header participates in the digest.

Avoid a runtime circular dependency. Type-only imports must remain type-only.

8. Strict architectural boundary

The two S-B production files must not import vscode.

They must contain no:

* workspaceFolder;
* workspaceFolders[0];
* fsPath;
* getConfiguration;
* inspect;
* update;
* ConfigurationTarget;
* process.env;
* filesystem or network operation;
* logging or persistence;
* task-context cache;
* evidenceComplete;
* bootstrap/envelope/child-agent propagation;
* drift or stale-context comparison;
* S-C selection or completeness logic;
* S-F guidance;
* S-G override;
* S-H configuration write;
* S-I/S-J/S-K behavior.

9. Focused test requirements

Create only:

src/test/suite/resolvedEtlAgentContext.test.ts

Cover at minimum the complete 18-row SB0 matrix, including:

1. Different object insertion orders produce identical canonical strings and digests.
2. Reordering contributingScopes or languageIds changes the digest.
3. Mutating source inputs after construction cannot change context or digest.
4. Every nested returned object and array is frozen and rejects writes under strict mode.
5. Equal independent inputs produce equal values/digests but non-identical references.
6. Depth 32 is accepted and attempted depth 33 fails with no partial context.
7. Prototype-chain members are not read; own __proto__ cannot pollute.
8. Non-string languageIds or declaredTypes elements fail closed.
9. Unsupported values and invalid numbers fail closed.
10. Cyclic input fails closed.
11. Failure results never echo an attacker-controlled substring.
12. Version header/domain separation is verified.
13. Digest is independently recomputed with node:crypto.
14. No vscode import exists in either production S-B file.
15. Forbidden S-C/S-D/S-E/S-H tokens/behavior are absent.
16. Unknown raw-value fields are rejected.
17. winningScope and all contributors are preserved without re-derivation.
18. Existing integration discovery is proven without editing a registry.

Also add explicit assertions that:

* raw manifestDefault is absent from the context, canonical form, and digest input;
* only hasManifestDefault is retained;
* user-facing manifest text and reason strings are absent;
* defined false, empty arrays, and other permitted empty/falsy metadata remain distinguishable from absence;
* contextDigest does not digest itself;
* all output ordering is deterministic.

Tests must not become self-fulfilling mirrors of the implementation. Use independent expected strings or independent hashing where applicable.

Do not add coverage for or a consumer of EtlSettingsVsCodeBindings.ts; MEDIUM-2 remains open until S-D.

10. Permitted validation commands

First inspect the existing scripts and hooks read-only.

You may run only:

* the already-existing compile route identified in SB0; and
* the already-existing integration test route that discovers suite/**/*.test.js.

Do not run a command that installs or downloads tooling.

Do not run npm install, npm ci, package, VSIX, smoke, evaluation-regeneration, Git, PR, or CI commands.

If an existing compile/test script would mutate a protected pending file, do not run it. Use an already-installed, bounded no-install equivalent if one exists; otherwise report the missing validation evidence.

If a command exposes the pre-existing evalGating.test.ts:5-8 failure:

* report the exact command, exit code, dependency route, and affected paths;
* prove whether the new S-B test executed;
* report the S-B passing/failing/pending/total counts separately;
* do not repair or regenerate the stale baseline;
* do not classify the unrelated failure as an S-B regression.

An S-B-caused failure may be repaired only inside the same three authorized S-B files.

11. End-state integrity

At the end, reverify:

* root, origin, branch, HEAD, and worktree list unchanged;
* staged count remains 0;
* all four S-A hashes still exactly match A1H;
* all original 16 pending paths are byte-identical to preflight;
* every protected clean path remains unchanged;
* package.json, package-lock.json, testPatterns.ts, and Phase-H evidence remain unchanged;
* the only new source paths are the three authorized S-B files;
* expanded pending inventory is exactly the original 20 paths plus those three files;
* no S-C or later artifact was created;
* no Git, PR, CI, package, or VSIX state changed.

Compute and report full SHA-256 hashes for all three new files.

The Copilot review card must contain exactly three added files. Do not click Keep or Undo.

12. Required report

Return:

1. Repository identity and preflight result.
2. Start-state porcelain inventory and protected hash evidence.
3. Implementation summary with exact file:line citations.
4. Final public schema and exported API.
5. Immutability, canonicalization, digest, and trust-boundary evidence.
6. Exact commands, exit codes, test counts, and proof that the focused test executed.
7. Unrelated-failure separation.
8. End-state inventory and complete start/end comparison.
9. Full hashes of the three S-B files.
10. Confirmation that all A1H findings remain correctly classified.
11. Exact Copilot review-card scope.
12. Self-review findings, including any remaining defect or missing evidence.

A self-check is not an independent audit and must never authorize Keep.

Finish with exactly one of these blocks and no text after it.

SUCCESS:

REPOSITORY_IDENTITY_MATCH: YES
PRE_IMPLEMENTATION_SA_BYTES_MATCH_A1H: YES
S_B_SOURCE_SCOPE_EXACTLY_THREE_NEW_FILES: YES
EXISTING_OR_PROTECTED_FILE_BYTE_DRIFT: NO
POST_IMPLEMENTATION_SA_BYTES_MATCH_A1H: YES
STAGED_COUNT: 0
S_B_FOCUSED_TEST_EXECUTED: YES
S_B_FOCUSED_TESTS_PASS: YES
UNRELATED_FAILURES_SEPARATED: YES
S_B_IMPLEMENTATION_SELF_CHECK: PASS
SAFE_TO_CLICK_KEEP_SB_CARD: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB1_IMPLEMENTATION_COMPLETE

FAILURE OR MISSING EVIDENCE:

REPOSITORY_IDENTITY_MATCH: YES|NO
PRE_IMPLEMENTATION_SA_BYTES_MATCH_A1H: YES|NO
S_B_SOURCE_SCOPE_EXACTLY_THREE_NEW_FILES: YES|NO
EXISTING_OR_PROTECTED_FILE_BYTE_DRIFT: YES|NO
POST_IMPLEMENTATION_SA_BYTES_MATCH_A1H: YES|NO
STAGED_COUNT: 
S_B_FOCUSED_TEST_EXECUTED: YES|NO
S_B_FOCUSED_TESTS_PASS: YES|NO
UNRELATED_FAILURES_SEPARATED: YES|NO
S_B_IMPLEMENTATION_SELF_CHECK: FAIL
SAFE_TO_CLICK_KEEP_SB_CARD: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB1_IMPLEMENTATION_BLOCKED
