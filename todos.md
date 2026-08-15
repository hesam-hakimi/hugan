LOCAL_PHASE_SB3 — BOUNDED THREE-FILE S-B REPAIR AFTER INDEPENDENT AUDIT FAILURE

FINAL CONSOLIDATED IMPLEMENTATION PROMPT

Execute this prompt only in the original Copilot chat that performed:

LOCAL_PHASE_SB1 — BOUNDED S-B IMPLEMENTATION

This is the chat whose current review card shows exactly:

3 files changed +2494 -3

Do not execute this prompt in the independent S-B correctness and security audit chat.

This task repairs the existing three-file S-B candidate. It is not a new implementation, not another recovery attempt, not an independent audit, not a Keep decision, and not authorization for S-C.

All explanations, code comments, test names, and final reporting must be in English.

MUST, ONLY, EXACTLY, NEVER, and DO NOT are hard constraints.

⸻

0. AUTHORITATIVE INTERPRETATION OF THE PRECEDING SB2R REPORT

The immediately preceding SB2R rerun in this chat was read-only and found that the recovery had already been completed by an earlier session.

Its markers:

SAFE_TO_REPAIR_S_B: NO
REVERSIBLE_MOVE_SUCCEEDED: NO
LOCAL_PHASE_SB2R_RECOVERY_BLOCKED

apply only to authorization to repeat the already-completed recovery move.

They are not an SB3 eligibility decision.

The following recovered live state is expected:

* the accidental repository source path is absent;
* expanded pending count is exactly 23;
* the original 20 pre-S-B pending paths are present and byte-identical;
* the three S-B candidate paths are present and match their authoritative pre-repair hashes;
* staged count is 0;
* S-A hashes match A1H;
* protected-path drift is zero;
* repository identity, branch, HEAD, and worktrees are unchanged.

The source-to-quarantine manifest comparison is permanently UNKNOWN because the original source no longer exists and the earlier VS Code test host continued writing 15,492 bytes after the move.

This quarantine discrepancy is not an SB3 preflight blocker.

Do not:

* repeat the recovery;
* recreate the accidental source;
* inspect or manage processes;
* inspect, modify, move, copy, merge, or delete the quarantine;
* require source-to-quarantine byte equivalence as an SB3 gate.

Determine SB3 eligibility only from the live repository preflight requirements in this prompt.

The independent SB2 audit transcript is not present in this implementation chat. The audit findings stated in this prompt are nevertheless authoritative repair requirements. Verify them against the current three candidate files; do not reject the task merely because the SB2 transcript is absent from this chat.

⸻

1. CONSOLIDATED ONE-TIME AUTHORIZATION GATE — HIGHEST PRIORITY

This section takes precedence over every later instruction concerning preflight, editing, command execution, temporary files, and permission requests.

Phase A — ask once and stop

Before the first tool call, filesystem read, repository inspection, file edit, command, or temporary-directory operation:

1. Execute nothing.
2. Display the exact authorization request below.
3. Stop and wait for the exact approval token:

APPROVE_LOCAL_PHASE_SB3_BATCH

Display exactly:

CONSOLIDATED_APPROVAL_REQUEST — LOCAL_PHASE_SB3
Authorize one bounded local batch covering:
A. READ-ONLY INSPECTION
- Verify repository root, origin, branch, HEAD, worktrees, staged count, pending paths, candidate hashes, S-A hashes, and protected-path hashes.
- Read/search only the files necessary to implement and validate the SB3 repair.
- Run read-only Git, path, text-search, line-count, and SHA-256 commands.
B. EXACTLY THREE AUTHORIZED FILE EDITS
1. src/core/agentContext/ResolvedEtlAgentContext.ts
2. src/core/agentContext/EtlAgentContextCanonicalForm.ts
3. src/test/suite/resolvedEtlAgentContext.test.ts
No other repository file may be created, modified, deleted, renamed, moved, restored, staged, or generated.
C. AUTHORIZED LOCAL VALIDATION
- Use only already-installed local Node.js, TypeScript, ESLint, and Mocha binaries.
- Run TypeScript no-emit validation.
- Perform an isolated TypeScript compilation whose config and emitted output remain entirely inside one authorized OS temporary directory.
- Run direct focused S-B Mocha tests.
- Run the direct S-A regression filter.
- Run ESLint only against the three authorized files with caching disabled.
- Perform final status, diff, path-inventory, and SHA-256 reconciliation.
D. ONE UNIQUE OS TEMPORARY DIRECTORY
- Create one uniquely named OS temporary directory outside every repository, worktree, selected workspace folder, .vscode-test, and retained quarantine.
- Use it only for isolated compilation and test artifacts.
- Record and validate its exact canonical path.
- Delete only that exact directory after validation, provided this phase created it and it did not previously exist.
- Never use a wildcard, unresolved variable, repository path, workspace root, HOME directory, parent directory, or broad recursive deletion target.
E. FINAL VERIFICATION
- Confirm exactly the three authorized files changed.
- Confirm staged count remains zero.
- Confirm all S-A, non-candidate pending, package, protected, control-plane, evaluation, and workflow files remain byte-identical.
- Report commands, exit codes, test counts, resulting hashes, unrelated failures, deviations, and limitations.
EXPLICITLY NOT AUTHORIZED:
- Any fourth repository file
- Network access or downloads
- npm install, npm update, dependency changes, or download-capable npx execution
- downloadAndUnzipVSCode or any VS Code/Electron test-download wrapper
- Modification or deletion of .vscode-test
- Modification, deletion, movement, or further inspection of the SB2 quarantine
- Git add, commit, checkout, restore, reset, clean, stash, merge, rebase, branch, tag, push, or pull
- Package, VSIX, release, PR, CI, deployment, or publishing work
- Keep or Undo
- S-C or any later phase
- Evaluation-baseline regeneration or docs/eval writes
- Process-management actions
- Any operation not explicitly listed above
This approval does not authorize accepting or keeping the repaired candidate. A new independent audit remains mandatory.
Reply exactly:
APPROVE_LOCAL_PHASE_SB3_BATCH

Phase B — autonomous execution after approval

After receiving the exact approval token:

1. Treat it as one conversational authorization for all operations explicitly listed above.
2. Begin preflight immediately.
3. Do not ask another conversational permission question for an already-authorized read, edit, command, validation, or exact temporary-directory cleanup.
4. Group logically related safe operations into the minimum practical number of tool calls.
5. Do not combine commands in a way that hides their effects or makes target paths ambiguous.
6. Do not broaden scope to make compilation or tests pass.
7. If an unlisted operation becomes necessary, stop before performing it and request one new narrowly scoped authorization.
8. If repository identity, hashes, pending inventory, or protected state fails preflight, perform no edit and report:

LOCAL_PHASE_SB3_PREFLIGHT_BLOCKED

Host permission boundary

The approval token is conversational authorization. It does not override VS Code, Copilot, operating-system, sandbox, or host security controls.

If the host still shows a mandatory Allow, Run tool, or equivalent dialog:

* minimize dialogs by batching already-authorized operations;
* do not repeat the permission question in chat;
* do not request broad access or Always Allow;
* do not modify permission settings;
* do not use alternate commands or shell tricks to bypass the host;
* resume immediately after host authorization.

⸻

2. AUTHORITATIVE REPOSITORY START STATE

Identity

Repository root:
C:\repos\etl-extension\etl_fw2\etl_framework_extension
Origin:
https://github.com/TD-Universe/agentic_etl.git
Branch:
feature/v3-agentic-redesign
HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847
Worktree count:
3
Staged count:
0
Expanded pending count:
23

Pending classification:

Original pre-S-B pending paths: 20
S-B candidate paths: 3
Accidental-directory entries: 0
Unexplained additional paths: 0

The three S-B paths must remain absent from both HEAD and the Git index.

Authoritative S-B pre-repair hashes

Compare all 64 characters without abbreviation:

src/core/agentContext/EtlAgentContextCanonicalForm.ts
428327984682B2F473CD9AD481792C0D6029D78C1FFB655FB3435FF8D893C192
src/core/agentContext/ResolvedEtlAgentContext.ts
DFC19D693C96DC0180CBBA92AA66F620582344FFD89ADA6100DACC3240D678CD
src/test/suite/resolvedEtlAgentContext.test.ts
E35BFE5DE246A6956533B2B1BCE761F35225264B29A51B770557C26010F988C5

These are the only files whose hashes may change during SB3.

Authoritative S-A hashes

Resolve each exact filename uniquely and verify its complete SHA-256 value:

EtlSettingsInventory.ts
6B99E6EB1851AB45050AE69225D06A59CE6AE0CE85871BF7A9C1DEAD0FBADD84
EtlSettingsProvenance.ts
09CD4A53A92D845D6C7F34279CBD2B2495F6C2EAE03D14567CBBC8474D553AC8
EtlSettingsVsCodeBindings.ts
0A010841E9806F6FDB51C35559EE20CB4A39A246F29001CA6A9DD749A3CD15D1
settingsInventoryProvenance.test.ts
64A4682CB2428B70F1E4B99B706A3050542502E14A57CC4BF7336D5711AB8AE2

No S-A file may change.

Recovery and quarantine state

The repository path named:

System.Management.Automation.Internal.Host.InternalHost

must be absent.

The retained quarantine is:

C:\Users\tag5916\AppData\Local\Temp\SB2_AUDIT_QUARANTINE_20260815_5574a5974eab

Do not inspect, modify, move, or delete it.

The existing .vscode-test cache is protected and unrelated. Do not modify or delete it.

Other protected paths

The protected set includes, but is not limited to:

.tsbuildinfo.test
package.json
package-lock.json
tsconfig.json
tsconfig.test.json
testPatterns.ts
src/customization/CopilotAssetCatalog.ts
src/tools/EtlActionToolService.ts
EvalGovernance.ts
evalGating.test.ts
docs/eval/**
.github/**
workflow/**
AGENTS.md
COPY_ORDER.md

Resolve actual paths read-only. Do not modify them.

If the historical complete protected manifest is unavailable in this chat, do not invent hashes. After all fixed identity, count, candidate-hash, and S-A-hash checks pass, capture a fresh SB3 start hash for every non-authorized pending/protected path and compare it at the end.

Any fixed preflight mismatch is a hard stop.

⸻

3. EXACT AUTHORIZED REPAIR SURFACE

Modify in place only:

src/core/agentContext/ResolvedEtlAgentContext.ts
src/core/agentContext/EtlAgentContextCanonicalForm.ts
src/test/suite/resolvedEtlAgentContext.test.ts

Do not:

* create a barrel or index.ts;
* create another source or test file;
* create repository-local fixtures, configs, reports, Markdown, JSON, snapshots, or generated output;
* modify package files or TypeScript configs;
* modify testPatterns.ts;
* modify S-A;
* modify control-plane, workflow, evaluation, or existing user-owned paths;
* apply repository-wide formatting;
* add a dependency;
* move implementation into a fourth file.

All permanent repair code and tests must remain inside the existing three candidate files.

⸻

4. MANDATORY SB2 REPAIRS

4.1 Literal schema-version contract

The current public interface exposes schemaVersion as number.

Repair it so that:

* the public contract declares readonly schemaVersion: 1;
* the schema-version constant retains literal type 1;
* a successful context always contains runtime value 1;
* canonicalization validates exact value 1;
* a version-2 payload fails closed;
* a compile-time probe proves 2 is not assignable;
* changing the domain/version header changes the digest.

A runtime equality test alone is insufficient. The exported TypeScript contract must itself use literal 1.

4.2 Hostile-input boundary

The current implementation may invoke getters, custom array iterators, or Proxy/reflection traps and may allow attacker-controlled exception prose to escape.

Replace unsafe traversal with a bounded descriptor-snapshot boundary.

Required behavior:

* do not read untrusted fields through ordinary property access before validation;
* never invoke getters or setters;
* never invoke custom iterators;
* never invoke coercion hooks, toJSON, or caller callbacks;
* inspect only own property descriptors under guarded exception handling;
* reject accessor descriptors without invoking them;
* copy only validated own data descriptors;
* catch exceptions from reflection and Proxy traps;
* convert caught failures to fixed machine-only codes;
* never echo, interpolate, log, or return attacker-controlled exception text;
* do not use spread, slice, Array.from, map, for...of, or iterator-based copying on untrusted arrays;
* validate array index descriptors directly;
* reject sparse arrays;
* reject augmented arrays;
* reject symbol-keyed array or record data;
* reject unsupported non-enumerable extras;
* permit only the intrinsic validated array length descriptor;
* reject custom array prototypes;
* reject accessor-backed array entries;
* reject invalid array length/index structures;
* reject non-plain record prototypes except explicitly supported ordinary and null-prototype records;
* safely handle an own data key named __proto__ without prototype pollution;
* preserve harmless shared references;
* reject true cycles;
* permit maximum depth exactly 32;
* reject depth greater than 32 with a fixed code and no partial context;
* reject null, function, symbol, BigInt, Date, Map, Set, RegExp, class instances, typed arrays, and other unsupported/exotic objects;
* reject NaN, infinities, negative zero, non-integers, and unsafe integers;
* snapshot validated data before projection so later mutation cannot change the accepted context or digest.

Do not claim that JavaScript can detect every transparent Proxy. The required guarantee is:

* getters and iterators are not invoked;
* reflective failures are caught;
* observable hostile behavior fails closed;
* attacker prose never escapes.

4.3 Complete S-A semantic correlation

The current key-only correlation can reject legitimate S-A negative results while accepting conflicting fabricated same-key results.

Derive the exact runtime contract from the unchanged, hash-verified S-A modules.

Do not invent or repair S-A semantics.

Implement exhaustive validation for the actual outcomes, including:

resolved
unknown_setting
ambiguous_declaration
malformed_declaration
ambiguous_resource_selection
provenance_unavailable

The live hash-verified S-A definitions remain authoritative.

For every outcome:

* validate its discriminant;
* validate required, optional, and forbidden own fields;
* validate descriptor safety and field types;
* validate outcome-specific semantic combinations;
* correlate provenance to the applicable inventory descriptor using all identity and semantic evidence required by S-A;
* never use key-only correlation;
* reject duplicate or conflicting results;
* reject fabricated same-key results with conflicting descriptor metadata;
* reject fields belonging to another outcome;
* reject missing resolved fields;
* reject missing required diagnostic evidence;
* reject duplicate or contradictory diagnostics;
* accept real S-A-produced examples of every legitimate negative outcome;
* preserve winningScope verbatim and never re-derive it;
* preserve contributionForm verbatim;
* do not reread VS Code configuration or workspace state.

4.4 Remove public validation bypasses

The current export surface permits impossible raw payloads to reach canonicalization or digest computation.

Reduce the API to the smallest contract-facing surface required for:

* immutable context, entry, diagnostic, and domain types;
* builder input and discriminated result types;
* literal schema-version constant;
* buildResolvedEtlAgentContext;
* a safe validated digest-recomputation function, if retained.

Remove, privatize, relocate within the same two production files, or fully guard implementation-only exports such as:

* raw digest payload types;
* unused trusted-input aliases;
* raw-payload canonicalizers;
* raw-payload digest functions;
* generic admission helpers;
* plain-record helpers;
* descriptor and domain tables;
* own-property helpers;
* internal result types;
* implementation-only constants;
* broad failure-code unions.

Requirements:

* no exported function may accept an unvalidated raw payload and return a canonical string or digest;
* an impossible unknown_setting entry carrying resolved-only fields must fail;
* TypeScript branding alone is not runtime validation;
* any public recomputation entry point must validate the complete closed context and outcome semantics;
* no new consumer, barrel, registry, or production file may be created;
* add an executable export-surface allow-list test.

4.5 Reduce unreachable or excessive failure codes

The independent audit found approximately 34 exports and 54 failure codes, including unasserted and unreachable cases such as DIAGNOSTIC_FIELD_INVALID.

Repair by:

* removing unreachable codes;
* consolidating redundant codes where the semantics are identical;
* keeping externally meaningful codes machine-readable and stable;
* ensuring every retained externally observable code is reachable;
* adding a behavioral assertion for every retained externally observable code;
* avoiding an arbitrary target count;
* never placing attacker-controlled values or prose in an error result.

Failures must remain discriminated and contain no partial context, for example:

{ ok: false, code: SOME_FIXED_CODE }

⸻

5. CONTRACT THAT MUST REMAIN TRUE

5.1 Top-level context

A successful context contains exactly six keys:

schemaVersion
namespace
contributionForm
settings
diagnostics
contextDigest

No extra key is admitted.

5.2 Setting entry

A setting entry permits exactly 13 keys.

Required:

key
effectiveScope
scopeDeclaration
hasManifestDefault
folderConfigurable
languageOverridable
provenanceOutcome

Optional only when semantically applicable:

declaredTypes
effectiveValueDefined
contributingScopes
winningScope
resourceProvided
languageIds

Omitted fields must remain absent, not undefined or null.

5.3 Diagnostic

A diagnostic permits exactly four keys.

Required:

code

Optional only when applicable:

key
categoryIndex
declarationCount

Do not include diagnostic English prose or raw reason strings.

5.4 Raw-value exclusion

The context, canonical representation, digest input, diagnostics, and error results must never include:

manifestDefault raw value
effective/default/policy/per-scope configuration values
title
description
markdownDescription
categoryTitle
reason prose
scopeStates
relativeKey
declaredScopeLiteral
SettingsResourceUri
fsPath
workspace root
folder count
environment or deployment data
registry or publisher identity
bootstrap/result envelopes
evidence completeness
drift or staleness state
persistence state
unknown caller-supplied keys

Only hasManifestDefault may represent default presence.

Only the already-resolved boolean resourceProvided may represent resource availability.

5.5 Immutability and determinism

For successful input:

* copy every admitted value defensively;
* retain no caller-owned object or array reference;
* deeply freeze every returned object and array;
* preserve meaningful array order;
* source mutation after construction must not change the context or digest;
* returned nested writes must fail in strict mode;
* equal inputs must produce deeply equal values;
* separate builds must return different object identities;
* equal inputs must produce identical canonical strings and digests.

5.6 Canonical serialization

Preserve:

* domain header: etl.agent.context.v1\n;
* ascending UTF-16 code-unit object-key ordering;
* no localeCompare;
* meaningful array order;
* contributingScopes and languageIds order significance;
* omission of absent optionals;
* rejection of null;
* deterministic string, boolean, and safe-integer encoding;
* Unicode byte preservation without normalization or case folding;
* deterministic control and quote escaping;
* failure on duplicate or ambiguous input;
* failure on unsupported values;
* insertion-order independence.

Do not use raw JSON.stringify(payload) as canonicalization.

If JSON.stringify is used only for scalar string escaping, it must never receive an unvalidated object or array.

5.7 Digest

Required:

Algorithm: SHA-256
Encoding: UTF-8
Output: 64 lowercase hex characters

The version header must be inside the digested bytes.

contextDigest must be excluded from its own input.

Stored digest and independent recomputation from the same validated frozen context must match.

No new dependency is permitted. Use only the existing node:crypto.

5.8 Slice boundary

The production S-B modules must not:

* import vscode;
* invoke a VS Code test/download wrapper;
* read workspace folders;
* read configuration;
* select a resource;
* read environment variables;
* create evidence envelopes;
* calculate evidence completeness;
* compare drift or staleness;
* perform persistence;
* implement S-C or any later slice.

⸻

6. REQUIRED EXECUTABLE TEST MATRIX

Preserve all useful existing tests. Do not weaken or delete a test merely to obtain green output.

Add executable coverage for the following.

6.1 Literal schema typing

Prove:

* successful context exposes literal 1;
* assignment to literal 1 succeeds;
* version 2 is rejected at compile time;
* runtime version 2 fails closed;
* header/version changes alter the digest.

A source-text search is not a substitute for compile-time evidence.

6.2 Getter/accessor safety

Use getters or setters that:

* increment a canary;
* throw attacker prose;
* attempt to mutate another field.

Assert:

* accessor invocation count remains zero;
* input fails with a fixed code;
* attacker prose is absent;
* no partial context is returned.

6.3 Proxy/reflection failures

Add throwing Proxy traps.

Assert:

* no exception escapes;
* trap text is not returned;
* a fixed machine code is returned;
* no context or digest is produced.

Do not claim detection of fully transparent proxies.

6.4 Hostile arrays

Cover:

* custom iterator canary;
* symbol-keyed array;
* non-enumerable extra property;
* enumerable augmented property;
* accessor-backed element;
* sparse array;
* custom prototype;
* invalid length/index shape;
* non-string languageIds;
* hostile contributingScopes;
* valid ordinary dense arrays.

Assert the custom iterator is never invoked.

6.5 Unsupported values

Cover:

null
invalid undefined
function
symbol
BigInt
Date
Map
Set
RegExp
class instance
typed or exotic object
NaN
Infinity
-Infinity
-0
non-integer
unsafe integer
true cycle
depth 32
depth 33
harmless shared reference

6.6 Prototype safety

Cover:

* inherited-only properties;
* null-prototype records;
* own __proto__ data;
* polluted prototype chains;
* forbidden custom prototypes;
* unchanged global/object prototypes.

6.7 Complete S-A outcomes

Use real S-A producers or faithful runtime-shaped values derived directly from the live S-A contract.

Cover all legitimate outcomes:

resolved
unknown_setting
ambiguous_declaration
malformed_declaration
ambiguous_resource_selection
provenance_unavailable

For every applicable outcome, cover:

* valid minimum form;
* valid optional form;
* missing required field;
* forbidden cross-outcome field;
* invalid field type;
* duplicate result;
* conflicting same-key descriptor;
* mismatched descriptor identity;
* contradictory diagnostic;
* missing required diagnostic.

Prove that legitimate negative results are accepted and fabricated correlations are rejected.

6.8 Public API

Test the runtime export surface and prove:

* unintended helpers are absent;
* raw canonicalization bypass is absent or fully guarded;
* raw digest bypass is absent or fully guarded;
* an impossible context cannot be hashed;
* every exported function validates runtime input;
* every retained externally observable failure code has behavioral coverage.

6.9 Canonical form and digest

Cover:

* independently written exact canonical fixture;
* insertion-order independence;
* meaningful array-order sensitivity;
* exact UTF-16 ordering;
* no locale-sensitive sorting;
* Unicode preservation;
* deterministic escaping;
* independent digest recomputation;
* self-digest exclusion;
* lowercase 64-hex result;
* domain/version separation.

6.10 Secret/raw-value exclusion

Build a real S-A inventory containing a distinctive secret default and user-facing metadata.

Prove the context and canonical representation contain none of:

* secret default;
* title or description;
* reason prose;
* resource URI/path;
* scope-state payload;
* unknown extra data.

6.11 Immutability

Test:

* mutation of source after construction;
* nested returned-object writes;
* returned-array writes;
* repeated construction;
* distinct references;
* deep equality;
* identical digests.

Security behavior must be executable. Source-text assertions may supplement but must not replace runtime hostile-input, outcome-correlation, schema-typing, and API-boundary tests.

⸻

7. COMMAND AND TEMP-DIRECTORY SAFETY

Use only existing local binaries.

Do not use npx.

Do not run an install/update command.

Do not run downloadAndUnzipVSCode.

Do not run the VS Code/Electron test wrapper.

Do not run npm run eval:golden.

Do not regenerate docs/eval/**.

Do not run a compiler command that emits into the repository.

PowerShell safety

The SB2 accident was caused by interpolation of PowerShell’s automatic $Host variable into a path.

Therefore:

* never assign to or repurpose $Host, $HOME, $PWD, $PID, $Error, $Args, or $Input;
* use task-specific variables such as $sb3RepoRoot and $sb3TempRoot;
* resolve every cleanup target to a literal canonical path;
* verify the temporary path is outside all repositories and worktrees;
* verify this task created it;
* never use wildcard deletion;
* never delete a parent directory;
* never retry against a shortened, empty, or fallback path;
* if cleanup validation fails, retain the temp directory and report it instead of risking an unsafe deletion.

The only authorized deletion is the exact temporary directory created by this SB3 execution.

⸻

8. EXECUTION ORDER AFTER APPROVAL

Step 1 — preflight

Capture:

* repository root, origin, branch, and HEAD;
* all three worktrees;
* staged count;
* expanded pending inventory;
* candidate HEAD/index absence;
* full S-B hashes;
* full S-A hashes;
* non-candidate protected hashes;
* accidental source-path absence;
* absence of unexpected S-B or later-slice artifacts.

The already-existing quarantine is not an unexpected artifact.

If any fixed required value differs, stop before editing.

Step 2 — inspect contracts

Read:

* the three authorized files;
* only the S-A definitions needed to derive exact discriminants and semantic relationships;
* test-runner details strictly read-only.

Do not edit during inspection.

Step 3 — establish minimal design

Before editing, determine internally:

* final public export allow-list;
* final reachable failure-code set;
* complete S-A outcome matrix;
* descriptor-safe snapshot strategy;
* canonical trust boundary;
* mapping from every SB2 finding to executable tests.

Do not create a plan file.

Step 4 — repair exactly three files

Implement the smallest complete repair in the two production files and the one S-B test file.

Avoid unrelated formatting or refactoring.

Step 5 — self-review

Inspect the exact diff and confirm:

* only three paths changed;
* schema version is literal;
* no raw public bypass remains;
* unsafe getters and iterators are not invoked;
* reflection failures map to fixed codes;
* attacker prose cannot escape;
* correlation is outcome-aware and exhaustive;
* all retained codes are reachable;
* no S-C behavior exists.

Step 6 — isolated validation

Using local binaries only, run:

1. TypeScript no-emit validation that writes no repository artifact.
2. Isolated TypeScript compilation with config/output entirely inside the authorized OS temp directory.
3. Direct Mocha S-B tests.
4. Direct Mocha S-A regression tests.
5. ESLint with caching disabled against exactly the three files.
6. Required security/mutation probes inside the same temporary directory.

Expected evidence:

* isolated candidate compilation: exit 0;
* zero TypeScript diagnostics in an S-B file;
* S-B tests: all pass, with count not lower than the previous 38;
* S-A regression filter: preserve the previous 59/59 result unless a legitimate deterministic discovery difference is proven;
* ESLint for the three files: exit 0.

The repository compiler previously produced 15 unrelated TS2353 diagnostics in onboardingWriteApproval.test.ts, caused by pre-existing changes involving EtlActionToolService.ts.

If those remain:

* report them separately;
* prove zero S-B diagnostics occurred;
* do not modify either unrelated file;
* do not claim the repository is globally green.

If the unrelated failure changes in file, code, or count, investigate read-only and report it. Do not repair it.

Step 7 — exact temp cleanup

Delete only the validated unique SB3 temporary directory.

Do not touch .vscode-test or the quarantine.

Step 8 — end-state proof

Recompute:

* identity and worktrees;
* staged count;
* pending path inventory;
* full hashes of all three repaired files;
* all four S-A hashes;
* all non-authorized start hashes;
* protected/control-plane drift;
* accidental-source absence;
* temp-directory absence.

Required end state:

Repository identity unchanged
Worktrees: 3
Staged count: 0
Pending count: 23
Pending path names unchanged
Exactly three S-B files changed
Original 20 paths byte-identical
All S-A files byte-identical
No new repository path
No Git mutation
No quarantine mutation
No .vscode-test mutation

⸻

9. FINAL REPORT

Return one complete evidence report containing:

1. Approval token received.
2. Repository identity and preflight result.
3. Start/end pending inventory.
4. Start/end full hashes for the three S-B files.
5. Full S-A hash comparison.
6. Protected non-candidate drift comparison.
7. Exact changed-file list.
8. File-and-line citations for every substantive repair.
9. Before/after runtime export lists.
10. Before/after externally observable failure-code lists.
11. Disposition of every SB2 finding.
12. Hostile-input evidence.
13. S-A outcome-correlation evidence.
14. Literal schema-version evidence.
15. Canonicalization and digest evidence.
16. Exact commands, exit codes, and test counts.
17. Unrelated failures, clearly separated.
18. Temporary-directory creation and removal evidence.
19. Remaining limitations.
20. Confirmation that no Keep, Undo, Git, package, VSIX, network, download, evaluation, or S-C action occurred.

This is an implementer self-check, not an independent audit.

Do not claim the candidate is safe to Keep.

Finish with exactly one of these blocks.

Successful repair

REPOSITORY_IDENTITY_MATCH: YES
CONSOLIDATED_BATCH_APPROVAL_RECEIVED: YES
PRE_REPAIR_S_B_HASHES_MATCH_SB2R: YES
S_B_SCOPE_EXACTLY_THREE_FILES: YES
UNAUTHORIZED_REPOSITORY_PATH_CREATED_OR_MODIFIED: NO
EXISTING_OR_PROTECTED_FILE_BYTE_DRIFT: NO
POST_REPAIR_S_A_HASHES_MATCH_A1H: YES
STAGED_COUNT: 0
PENDING_PATH_SET_UNCHANGED: YES
SCHEMA_VERSION_LITERAL_CONTRACT_MET: YES
PUBLIC_API_BOUNDARY_ACCEPTABLE: YES
RAW_VALUE_TRUST_BOUNDARY_SAFE: YES
CANONICAL_DIGEST_CONTRACT_SAFE: YES
IMMUTABILITY_AND_DETERMINISM_SAFE: YES
HOSTILE_INPUT_BOUNDARY_SAFE: YES
S_A_SEMANTIC_CORRELATION_COMPLETE: YES
RETAINED_FAILURE_CODES_REACHABLE_AND_TESTED: YES
S_B_FOCUSED_TESTS_EXECUTED: YES
S_B_FOCUSED_TESTS_PASS: YES
S_A_REGRESSION_TESTS_EXECUTED: YES
S_A_REGRESSION_TESTS_PASS: YES
UNRELATED_FAILURES_SEPARATED: YES
TEMP_DIRECTORY_REMOVED: YES
SAFE_TO_REAUDIT_S_B: YES
SAFE_TO_CLICK_KEEP_S_B_CARD: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB3_REPAIR_COMPLETE

Blocked or incomplete

SAFE_TO_REAUDIT_S_B: NO
SAFE_TO_CLICK_KEEP_S_B_CARD: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB3_REPAIR_INCOMPLETE

If incomplete, place the exact failed gate immediately before the marker.

Do not click Keep or Undo.

Do not begin the independent audit.

Stop after the final SB3 report.
