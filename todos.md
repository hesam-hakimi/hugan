LOCAL_PHASE_SB3 — BOUNDED THREE-FILE S-B REPAIR AFTER INDEPENDENT AUDIT FAILURE

FINAL COMBINED PROMPT WITH CONSOLIDATED ONE-TIME AUTHORIZATION

Run this task in the original chat that performed LOCAL_PHASE_SB1.

This is a bounded repair of the existing S-B candidate after the independent LOCAL_PHASE_SB2 audit failure and the completed LOCAL_PHASE_SB2R recovery.

This is:

* not a fresh S-B implementation;
* not an independent audit;
* not a Keep authorization;
* not S-C or any later slice;
* not authorization to modify repository infrastructure, protected files, evaluation evidence, package files, Git state, or existing user-owned work.

All explanations, code comments, test names, command output summaries, and final reporting must be in English.

The words MUST, ONLY, EXACTLY, NEVER, and DO NOT are hard constraints.

⸻

0. CONSOLIDATED ONE-TIME AUTHORIZATION GATE — HIGHEST PRIORITY

This section takes precedence over every later instruction concerning preflight, execution, editing, commands, temporary files, and permission requests.

Phase A — ask exactly once

Before performing the first tool call, filesystem read, repository inspection, file edit, shell command, or temporary-directory operation:

1. Do not execute anything.
2. Display the exact authorization request below.
3. Stop.
4. Wait for the user to reply with the exact approval token:

APPROVE_LOCAL_PHASE_SB3_BATCH

Display exactly:

CONSOLIDATED_APPROVAL_REQUEST — LOCAL_PHASE_SB3
Authorize one bounded local batch covering all of the following:
A. READ-ONLY INSPECTION
- Verify repository root, origin, branch, HEAD, worktrees, staged count, pending-path inventory, candidate hashes, S-A hashes, and protected-path hashes.
- Read and search repository files needed to repair and validate the existing S-B candidate.
- Run read-only Git operations such as rev-parse, remote inspection, branch inspection, worktree list, status, diff, diff --no-index where safe, ls-files, show, and hash-object.
- Run local path, file-size, line-count, text-search, and SHA-256 commands.
B. EXACTLY THREE AUTHORIZED FILE EDITS
1. src/core/agentContext/ResolvedEtlAgentContext.ts
2. src/core/agentContext/EtlAgentContextCanonicalForm.ts
3. src/test/suite/resolvedEtlAgentContext.test.ts
No other repository file may be created, modified, deleted, renamed, moved, restored, staged, or generated.
C. AUTHORIZED LOCAL VALIDATION
- Invoke only already-installed local Node.js, TypeScript, ESLint, and Mocha binaries.
- Run TypeScript no-emit validation.
- Perform an isolated TypeScript compilation whose config and emitted output remain entirely inside one authorized OS temporary directory.
- Run direct focused Mocha tests for S-B.
- Run the required direct S-A regression filter.
- Run ESLint only against the three authorized files, with caching disabled.
- Perform final status, diff, path-inventory, and SHA-256 reconciliation.
- Do not install, update, or download any dependency.
D. ONE UNIQUE OS TEMPORARY DIRECTORY
- Create one uniquely named operating-system temporary directory outside the repository, all Git worktrees, all selected workspace folders, .vscode-test, and the retained SB2 quarantine.
- Use it only for isolated compilation and test artifacts.
- Record and validate its exact canonical path before use.
- At completion, delete only that exact directory, provided it was created by this phase and did not exist before this phase.
- Never use a wildcard, unresolved variable, repository path, workspace root, HOME directory, parent directory, or broad recursive target for cleanup.
E. FINAL VERIFICATION
- Confirm that exactly the three authorized files changed during SB3.
- Confirm staged count remains zero.
- Confirm all non-candidate pending, protected, package, control-plane, evaluation, workflow, and S-A files remain byte-identical.
- Report every validation command, exit code, test count, resulting candidate hash, unrelated failure, deviation, and remaining limitation.
EXPLICITLY NOT AUTHORIZED:
- Any fourth repository file
- Network access or downloads
- npm install, npm update, dependency mutation, or download-capable npx execution
- downloadAndUnzipVSCode or any VS Code/Electron test-download wrapper
- Modification, deletion, refresh, or cleanup of .vscode-test
- Modification, deletion, or inspection-driven mutation of the retained SB2 quarantine
- Package, VSIX, release, deployment, PR, CI, or publishing work
- Git add, commit, checkout, restore, reset, clean, stash, merge, rebase, branch creation, tag, push, or pull
- Keep or Undo
- S-C or any later phase
- Evaluation-baseline regeneration or docs/eval writes
- Process-management actions
- Any operation not explicitly listed above
This approval does not authorize accepting or keeping the repaired candidate. A new independent audit is still required.
Reply exactly:
APPROVE_LOCAL_PHASE_SB3_BATCH

Phase B — execution after approval

After receiving the exact approval token:

1. Treat it as one conversational authorization for every operation explicitly listed above.
2. Begin preflight immediately and execute the complete SB3 workflow autonomously.
3. Do not ask another conversational permission question for an already-authorized read, edit, command, validation, or exact temporary-directory cleanup.
4. Group logically related safe checks into the minimum practical number of terminal or tool calls.
5. Do not combine commands in a way that hides effects, weakens error handling, or makes target paths ambiguous.
6. Do not expand scope merely to make a command, build, or test pass.
7. If an operation outside the approved manifest becomes necessary, stop before performing it and request one new narrowly scoped authorization.
8. If repository identity, hashes, path inventory, or protected state does not match the required preflight state, perform no edit and report LOCAL_PHASE_SB3_PREFLIGHT_BLOCKED.

Host-enforced permission boundary

The approval token is conversational authorization. It does not override VS Code, Copilot, operating-system, sandbox, or host security controls.

If the host still displays a mandatory Allow, Run tool, or equivalent dialog:

* minimize dialogs by batching only already-authorized operations;
* do not repeat the permission question in chat;
* do not request broad workspace access or Always Allow;
* do not change permission settings;
* do not use shell tricks or alternate tools to bypass the host control;
* resume the authorized workflow immediately after the host-level permission is granted.

⸻

1. AUTHORITATIVE START STATE

The following state is authoritative for this task.

Repository identity

* Repository root leaf: etl_framework_extension
* Origin: https://github.com/TD-Universe/agentic_etl.git
* Branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* Worktree count: 3
* Staged paths: 0
* Expanded pending paths after SB2R recovery: 23
    * original pre-S-B pending paths: 20
    * S-B candidate paths: 3
    * accidental audit-created entries remaining in the repository: 0

The three S-B files must still be absent from both HEAD and the index.

Current S-B candidate hashes

Full SHA-256 values must be compared without prefix abbreviation:

src/core/agentContext/EtlAgentContextCanonicalForm.ts
428327984682B2F473CD9AD481792C0D6029D78C1FFB655FB3435FF8D893C192
src/core/agentContext/ResolvedEtlAgentContext.ts
DFC19D693C96DC0180CBBA92AA66F620582344FFD89ADA6100DACC3240D678CD
src/test/suite/resolvedEtlAgentContext.test.ts
E35BFE5DE246A6956533B2B1BCE761F35225264B29A51B770557C26010F988C5

These are the authorized repair inputs. Their hashes are expected to change during SB3.

Authoritative S-A hashes

Resolve each path uniquely by its exact filename and verify its full SHA-256 value:

EtlSettingsInventory.ts
6B99E6EB1851AB45050AE69225D06A59CE6AE0CE85871BF7A9C1DEAD0FBADD84
EtlSettingsProvenance.ts
09CD4A53A92D845D6C7F34279CBD2B2495F6C2EAE03D14567CBBC8474D553AC8
EtlSettingsVsCodeBindings.ts
0A010841E9806F6FDB51C35559EE20CB4A39A246F29001CA6A9DD749A3CD15D1
settingsInventoryProvenance.test.ts
64A4682CB2428B70F1E4B99B706A3050542502E14A57CC4BF7336D5711AB8AE2

No S-A file may be modified.

SB2 recovery state

The audit-created repository directory named:

System.Management.Automation.Internal.Host.InternalHost

must be absent from the repository.

Its recovered quarantine leaf is:

SB2_AUDIT_QUARANTINE_20260815_5574a5974eab

It is outside all repositories and worktrees. Do not modify, move, delete, merge, copy, or enumerate its contents during SB3.

The existing .vscode-test cache is unrelated and protected. Do not modify or delete it.

Protected-state reconciliation

Use retained SB0, SB1, SB2, and SB2R evidence already present in this chat.

Reconcile the complete 57-path SB2R start manifest if available:

* exactly the three authorized S-B candidates may change;
* the other 54 paths must remain byte-identical.

If the complete retained manifest cannot be reconstructed from the chat, do not invent hashes. Capture a fresh read-only SB3 baseline for every non-authorized pending and protected path after all exact identity, pending-count, S-A, and candidate-hash checks have passed.

Any preflight mismatch is a hard stop.

⸻

2. EXACT AUTHORIZED REPAIR SURFACE

Modify in place only:

1. src/core/agentContext/ResolvedEtlAgentContext.ts
2. src/core/agentContext/EtlAgentContextCanonicalForm.ts
3. src/test/suite/resolvedEtlAgentContext.test.ts

Do not:

* create a barrel or index.ts;
* create helper, fixture, config, report, Markdown, JSON, snapshot, or generated file in the repository;
* modify package.json, package-lock.json, TypeScript configs, test registries, runner files, or scripts;
* modify testPatterns.ts;
* modify S-A;
* modify control-plane, workflow, docs/eval/**, or user-owned pending files;
* apply repository-wide formatting;
* add a dependency;
* move code into a fourth file.

All production repair code and all permanent tests must fit inside the same three files.

⸻

3. SB2 FINDINGS THAT MUST BE REPAIRED

3.1 HIGH — literal schema-version contract

The public schema currently exposes schemaVersion as number.

Repair it so that:

* the public context contract exposes readonly schemaVersion: 1;
* the exported schema-version constant retains literal type 1;
* every successfully built context contains runtime value 1;
* canonicalization validates the exact value;
* a version-2 context or payload is rejected;
* a compile-time probe proves that version 2 is not assignable;
* changing the domain/version header changes the digest.

Do not rely only on runtime comparison. The public TypeScript contract itself must be literal.

3.2 HIGH — hostile-input and reflective-boundary safety

The current candidate can invoke getters, custom array iterators, and proxy traps, and thrown attacker-controlled prose can escape.

Replace unsafe traversal with a bounded descriptor-snapshot boundary.

Required behavior:

* Never read untrusted object fields using ordinary property access before validation.
* Never invoke getters, setters, custom iterators, coercion hooks, toJSON, or attacker-provided callbacks.
* Inspect own property descriptors under guarded exception handling.
* Reject accessor descriptors without invoking them.
* Copy only validated own data descriptors.
* Wrap all reflection operations that may trigger Proxy traps.
* Convert reflection or Proxy failures to fixed machine-only failure codes.
* Never return, interpolate, log, or echo attacker-controlled exception text.
* Do not use array spread, slice, Array.from, map, for...of, or the iterator protocol on untrusted arrays.
* Validate array index descriptors directly.
* Reject sparse arrays.
* Reject augmented arrays containing extra string or symbol properties.
* Reject custom array prototypes.
* Reject symbol-keyed input.
* Reject unsupported non-enumerable input properties, except the intrinsic validated array length descriptor.
* Reject accessor-backed array elements or length anomalies.
* Reject non-plain object prototypes, while continuing to accept explicitly supported ordinary and null-prototype records.
* Handle an own data property named __proto__ without prototype pollution.
* Preserve harmless repeated/shared references.
* Reject true cycles.
* Permit the established maximum depth of exactly 32.
* Reject depth greater than 32 with a fixed machine code and no partial context.
* Reject null, functions, symbols, BigInt, class instances, Date, Map, Set, RegExp, typed or exotic objects, and other unsupported values.
* Reject NaN, positive or negative infinity, negative zero, non-integers, and unsafe integers.
* Snapshot validated data before later projection so subsequent caller mutation cannot alter the accepted context or digest.

A transparent Proxy cannot always be identified by JavaScript. Do not claim universal Proxy detection. The required guarantee is that accessors and iterators are not invoked, reflective failures are caught, observable hostile behavior fails closed, and attacker prose never escapes.

3.3 HIGH — complete S-A semantic correlation

The current key-only correlation accepts conflicting fabricated provenance and rejects legitimate S-A negative outcomes.

Derive the exact runtime contract from the unchanged, hash-verified S-A modules. Do not invent a new S-A interpretation.

Implement exhaustive outcome-aware validation for every actual S-A provenance discriminant, including the existing outcomes:

resolved
unknown_setting
ambiguous_declaration
malformed_declaration
ambiguous_resource_selection
provenance_unavailable

The hash-verified live S-A definitions remain authoritative.

Required behavior:

* Validate the exact discriminant.
* Validate every required, optional, and forbidden own field for that outcome.
* Validate field types and descriptor safety.
* Validate outcome-specific semantic combinations.
* Correlate provenance to the applicable inventory descriptor using all identity and semantic evidence required by the real S-A contract.
* Key-only correlation is forbidden.
* Reject duplicate or conflicting results for the same setting.
* Reject a forged same-key result whose descriptor metadata conflicts.
* Reject an outcome containing fields valid only for another outcome.
* Reject missing required resolved data.
* Reject missing required diagnostic data.
* Reject duplicate or contradictory diagnostics.
* Accept real S-A-produced examples of every legitimate negative outcome.
* Preserve S-A’s winningScope verbatim and never re-derive it.
* Preserve S-A’s contributionForm classification verbatim.
* Do not silently repair or reinterpret existing S-A findings.
* Do not import or call VS Code bindings.
* Do not reread configuration or the workspace.

3.4 HIGH — remove public validation bypasses

The current export surface allows callers to canonicalize or hash impossible raw payloads.

Reduce the public API to the smallest contract-facing surface necessary for S-B.

Contract-facing exports may include only what is genuinely needed for:

* the immutable context, entry, diagnostic, and domain types;
* the builder input and discriminated build result;
* the literal schema-version constant;
* buildResolvedEtlAgentContext;
* a safe digest-recomputation entry point if retained as part of the contract.

Implementation details must be private, relocated within the same two production files, or made safe through full runtime validation.

Review and remove or harden unnecessary public exports, including the existing categories:

* raw digest payload types;
* unused trusted-input aliases;
* raw-payload canonicalizers;
* raw-payload digest functions;
* generic admission helpers;
* plain-record helpers;
* own-property helpers;
* descriptor tables;
* domain lookup tables;
* internal result types;
* implementation-only header and depth constants;
* broad failure-code unions.

Requirements:

* No exported function may accept an unvalidated raw payload and produce a canonical string or digest.
* No caller may construct an impossible unknown_setting entry with resolved-only scope metadata and successfully canonicalize or hash it.
* A TypeScript brand alone is not runtime validation.
* Any retained exported recomputation function must validate the complete closed context schema and semantic combinations before computing a digest.
* No production consumer, barrel, registry, or fourth file may be created.
* Add an export-surface test that fails if an unintended runtime export returns.

3.5 MEDIUM — excessive and unreachable public complexity

The previous candidate exposed approximately 34 symbols and 54 failure codes. Eighteen codes lacked explicit assertions and DIAGNOSTIC_FIELD_INVALID was unreachable.

Repair this by:

* removing unreachable failure codes;
* consolidating redundant codes where semantics are identical;
* keeping machine codes stable and specific enough for callers;
* exporting only codes callers genuinely need;
* ensuring every retained externally observable failure code is reachable;
* adding an explicit behavioral test for every retained externally observable failure code;
* avoiding arbitrary target counts;
* never embedding attacker-controlled values or prose in an error result.

A failure must remain a discriminated machine-readable result such as:

{ ok: false, code: SOME_FIXED_CODE }

Do not return partial context on failure.

⸻

4. S-B CONTRACT THAT MUST REMAIN TRUE

4.1 Exact top-level context schema

A successful context contains exactly these six keys:

schemaVersion
namespace
contributionForm
settings
diagnostics
contextDigest

No extra key is admitted.

4.2 Setting-entry schema

A setting entry permits exactly these 13 keys.

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

Absence must remain absence. Do not replace omitted optional fields with undefined or null.

4.3 Diagnostic schema

A diagnostic permits exactly four keys:

Required:

code

Optional only when applicable:

key
categoryIndex
declarationCount

Diagnostic English prose and raw reason strings are excluded.

4.4 Raw-value and secret exclusion

The context, canonical string, digest input, diagnostics, and error results must never carry:

* raw manifestDefault;
* any effective, default, policy, or per-scope configuration value;
* title;
* description;
* markdownDescription;
* categoryTitle;
* negative-outcome reason prose;
* scopeStates;
* relativeKey;
* declaredScopeLiteral;
* SettingsResourceUri;
* fsPath;
* workspace root;
* folder count;
* environment or deployment data;
* registry, publisher, or physical-storage identity;
* bootstrap, envelope, evidence-completeness, drift, staleness, or persistence data;
* unknown caller-supplied keys.

Presence of a manifest default is represented only by hasManifestDefault.

Resource resolution is represented only by the already-resolved boolean resourceProvided.

4.5 Immutability

For successful inputs:

* defensively copy every admitted value;
* retain no caller-owned object or array reference;
* deeply freeze every returned object and array;
* preserve meaningful array order;
* mutation of any source input after construction must not change the context or digest;
* mutation of every returned nested object or array must fail under strict mode;
* two equal inputs must yield deeply equal values, distinct object identities, identical canonical strings, and identical digests.

4.6 Canonical serialization

Preserve the existing canonical contract:

* canonical bytes begin with the domain-separated header:
    etl.agent.context.v1\n
* object keys are ordered by ascending UTF-16 code-unit comparison;
* never use locale-sensitive ordering or localeCompare;
* meaningful array order is preserved verbatim;
* contributingScopes and languageIds are order-significant;
* undefined and omitted optional fields are absent from canonical output;
* null is rejected;
* strings and booleans are encoded deterministically;
* numbers are admitted only when finite safe integers are permitted by the closed schema;
* Unicode bytes are preserved without normalization or case folding;
* control, quote, slash, and backslash characters are escaped deterministically;
* duplicate or ambiguous normalized keys fail closed;
* unsupported values fail closed;
* no insertion-order-dependent object digest is permitted;
* do not use raw JSON.stringify(payload) as the canonical algorithm;
* if JSON.stringify is retained for scalar string escaping, it must never receive an unvalidated object or array.

4.7 Digest contract

* Algorithm: SHA-256.
* Encoding: UTF-8.
* Output: exactly 64 lowercase hexadecimal characters.
* The domain/version header is inside the digested bytes.
* contextDigest itself is excluded from its own digest input.
* The stored digest and an independent recomputation from the same validated frozen context must match.
* Changing the header or any admitted order-significant value must change the digest.
* Object insertion order alone must not change the digest.
* No new dependency is allowed; use only the existing local node:crypto facility.

4.8 Integration boundary

The production S-B modules:

* must not import vscode;
* must not call or reference downloadAndUnzipVSCode;
* must not read workspace folders;
* must not read configuration;
* must not select resources;
* must not read environment variables;
* must not create or update evidence envelopes;
* must not calculate completeness;
* must not compare drift or staleness;
* must not perform persistence;
* must not implement S-C, S-D, S-E, S-F, S-G, or S-H behavior.

S-B consumes already-computed, hash-verified S-A outputs and projects only the closed trusted context.

⸻

5. REQUIRED EXECUTABLE TEST REPAIR

Preserve all useful existing S-B tests. Do not weaken or delete a test merely to obtain green output.

Add executable coverage for every SB2 defect.

5.1 Literal schema typing

Test:

* successful context type exposes literal 1;
* a compile-time assignment to literal 1 succeeds;
* a version-2 assignment or payload is rejected at compile time;
* runtime version 2 is rejected;
* version/header separation affects the digest.

Do not substitute a source-text search for the compile-time contract.

5.2 Getter and accessor canaries

Use getter/setter fixtures that:

* increment a canary;
* throw attacker-controlled prose;
* attempt to mutate another field.

Assert:

* the accessor is never invoked;
* the input fails closed with a fixed code;
* no attacker prose appears in the result;
* no partial context is returned.

5.3 Proxy and reflection failures

Add throwing Proxy traps for relevant reflection operations.

Assert:

* no exception escapes the builder;
* no trap message is echoed;
* the result is a fixed machine code;
* no partial context or digest is produced.

Do not claim detection of fully transparent proxies.

5.4 Array-hostility cases

Add behavioral tests for:

* custom iterator canary;
* symbol-keyed array;
* non-enumerable extra property;
* enumerable augmented property;
* accessor-backed element;
* sparse array;
* custom array prototype;
* invalid length/index structure;
* non-string languageIds element;
* hostile contributingScopes;
* ordinary dense arrays that remain valid.

Assert that the custom iterator is never invoked.

5.5 Unsupported values and numbers

Cover:

* null;
* undefined where not permitted;
* function;
* symbol;
* BigInt;
* Date;
* Map;
* Set;
* RegExp;
* class instance;
* typed array or exotic object;
* NaN;
* Infinity;
* -Infinity;
* -0;
* non-integer;
* unsafe integer;
* true cycle;
* depth 32;
* depth 33;
* harmless shared reference.

5.6 Prototype safety

Cover:

* inherited-only properties;
* null-prototype records;
* own __proto__ data;
* polluted prototype chains;
* forbidden custom prototypes;
* prototype remains unchanged;
* no global pollution occurs.

5.7 Complete S-A outcome matrix

Construct cases using actual hash-verified S-A producers or faithful runtime-shaped outputs derived directly from those producers.

Cover every legitimate outcome:

resolved
unknown_setting
ambiguous_declaration
malformed_declaration
ambiguous_resource_selection
provenance_unavailable

For each outcome, test:

* valid minimum form;
* valid optional fields;
* missing required field;
* forbidden cross-outcome field;
* invalid field type;
* duplicate result;
* conflicting same-key descriptor;
* mismatched descriptor identity;
* contradictory diagnostic;
* missing required diagnostic where applicable.

Prove that legitimate S-A negative outcomes are accepted and forged correlations are rejected.

5.8 Public API boundary

Test the runtime export surface.

Prove that:

* unintended helpers are not exported;
* raw-payload canonicalization is unavailable or fully guarded;
* raw-payload digest bypass is unavailable or fully guarded;
* an impossible context cannot be hashed successfully;
* all retained exported functions reject malformed runtime input;
* every retained public failure code has a behavioral assertion.

5.9 Canonical and digest behavior

Retain or add executable assertions for:

* exact independently written canonical fixture;
* equal output for different object insertion orders;
* different digest when meaningful array order changes;
* exact UTF-16 key ordering;
* no localeCompare;
* Unicode preservation without normalization;
* deterministic escaping;
* digest independent recomputation;
* self-digest exclusion;
* 64-character lowercase hex output;
* domain/version separation.

5.10 Trust-boundary exclusions

Build a real S-A inventory using a manifest containing a distinctive secret default and user-facing metadata.

Assert that none of the following appears anywhere in the context, canonical string, digest-input representation, diagnostic, or error:

* secret default;
* title or description;
* raw reason prose;
* resource URI or path;
* scope-state payload;
* unknown extra field.

5.11 Immutability and determinism

Test:

* source mutation after construction;
* nested returned-object mutation;
* returned-array mutation;
* repeated construction;
* distinct references;
* deep equality;
* identical digests across repeated local processes where practical.

Security behavior must be tested by execution. Source-text assertions may supplement but must not replace hostile-input, correlation, schema-typing, and public-boundary behavioral tests.

⸻

6. SAFE COMMAND AND TEMPORARY-DIRECTORY RULES

Use only existing local tools.

Do not use npx.

Do not run any command capable of installing or downloading packages.

Do not run the VS Code/Electron test wrapper.

Do not run downloadAndUnzipVSCode.

Do not run npm run eval:golden.

Do not regenerate docs/eval/**.

Do not run a compile command that emits into the repository.

PowerShell safety

Because SB2 accidentally created a directory through a malformed host/cache command:

* never assign to or repurpose automatic variables such as $Host, $HOME, $PWD, $PID, $Error, $Args, or $Input;
* use task-specific variable names such as $sb3RepoRoot and $sb3TempRoot;
* resolve every destructive target to a literal canonical path first;
* verify the temporary directory was created by this phase;
* verify it is outside all repositories and worktrees;
* never use wildcard deletion;
* never delete a parent directory;
* never retry cleanup against a shortened or fallback path;
* if exact cleanup validation fails, leave the temporary directory in place and report it rather than risking a broad deletion.

The only authorized deletion is the exact unique OS temporary directory created by this SB3 run.

⸻

7. REQUIRED EXECUTION ORDER AFTER APPROVAL

Step 1 — read-only preflight

Capture before-state evidence:

* repository identity;
* all three worktrees;
* staged count;
* expanded pending inventory;
* candidate path/index/HEAD status;
* full candidate hashes;
* full S-A hashes;
* non-candidate pending and protected hashes;
* absence of the accidental audit directory;
* absence of any unexpected S-B or later-slice artifact.

If any required value differs, stop without editing.

Step 2 — inspect the three files and live S-A contracts

Read:

* the three authorized files;
* only the S-A types and implementation sections needed to derive exact discriminants and semantic relationships;
* existing test-runner configuration strictly read-only.

Do not modify anything during inspection.

Step 3 — design the minimal repair

Before editing, establish internally:

* final public export allow-list;
* final reachable failure-code set;
* exact S-A outcome matrix;
* descriptor-safe snapshot strategy;
* canonicalization trust boundary;
* tests mapped to every SB2 finding.

Do not create a plan file.

Step 4 — edit exactly the three authorized files

Implement the repair in the two production files and update the single S-B test file.

Avoid unrelated refactoring and formatting churn.

Step 5 — self-review before commands

Inspect the exact diff and confirm:

* only the three paths changed;
* no raw bypass remains;
* no unsafe property/array traversal remains;
* no getter or custom iterator is invoked;
* reflection exceptions map to fixed codes;
* semantic correlation is exhaustive;
* schema version is literal;
* no unnecessary runtime export remains;
* no S-C behavior was introduced.

Step 6 — isolated validation

Run, using local binaries only:

1. TypeScript no-emit validation that cannot write repository artifacts.
2. Isolated TypeScript compilation with config and output inside the unique OS temporary directory.
3. Direct Mocha focused on S-B tests.
4. Direct Mocha S-A regression filter.
5. ESLint with --no-cache against exactly the three authorized files.
6. Any necessary mutation/security probes inside the same OS temporary directory.

Expected evidence:

* isolated candidate compilation: exit 0;
* no TypeScript diagnostic in an S-B file;
* S-B tests: all pass, with a count not lower than the previous 38;
* S-A regression filter: all pass, preserving the prior 59/59 baseline unless the runner proves a legitimate deterministic count difference;
* ESLint for the three files: exit 0.

The repository-wide compiler previously reported 15 unrelated TS2353 diagnostics in onboardingWriteApproval.test.ts, caused by pre-existing changes to EtlActionToolService.ts.

If still present:

* report them separately;
* prove there are zero S-B diagnostics in the same compiler run;
* do not modify either unrelated file;
* do not claim the repository is globally green.

If the unrelated failure differs in path, code, or count, investigate read-only and report the exact difference. Do not repair it.

Step 7 — exact cleanup

Delete only the validated SB3 temporary directory.

Do not touch .vscode-test or the SB2 quarantine.

Step 8 — end-state proof

Recompute:

* repository identity;
* worktree count;
* staged count;
* pending inventory;
* full hashes of all three repaired S-B files;
* all four S-A hashes;
* every non-authorized start-state hash;
* control-plane and protected-path drift;
* accidental-directory absence;
* temporary-directory absence.

Required end state:

* repository identity unchanged;
* worktree count remains 3;
* staged count remains 0;
* pending count remains 23;
* pending-path names remain identical;
* exactly the three authorized S-B file bytes changed;
* all original 20 pre-S-B pending paths remain byte-identical;
* all four S-A files remain byte-identical;
* no new repository file or directory exists;
* no Git state mutation occurred;
* no quarantine or .vscode-test mutation occurred.

⸻

8. FINAL REPORT

Return one complete evidence report containing:

1. Approval token received.
2. Repository identity and preflight result.
3. Start/end pending inventory.
4. Start/end full SHA-256 hashes of the three S-B files.
5. Full S-A hash comparison.
6. Non-candidate protected-path drift comparison.
7. Exact changed-file list.
8. File-and-line citations for every substantive repair.
9. Before/after runtime export list.
10. Before/after externally observable failure-code list.
11. A disposition table for every SB2 finding.
12. Hostile-input safety evidence.
13. S-A semantic-correlation evidence.
14. Literal schema-version evidence.
15. Canonical-string and digest evidence.
16. Exact commands, exit codes, and test counts.
17. Unrelated failures, clearly separated.
18. Temporary-directory creation and verified removal.
19. Remaining limitations.
20. Confirmation that no Keep, Undo, S-C, Git, package, VSIX, network, download, or evaluation action occurred.

Do not claim independent assurance. This is a repair self-check and still requires a new independent audit.

Finish with exactly one of the following marker blocks.

Successful repair marker

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

Blocked or incomplete marker

SAFE_TO_REAUDIT_S_B: NO
SAFE_TO_CLICK_KEEP_S_B_CARD: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB3_REPAIR_INCOMPLETE

If blocked or incomplete, add the exact failed gate immediately before the marker.

Do not click Keep or Undo.
Do not begin an independent audit.
Stop after the final SB3 report.
