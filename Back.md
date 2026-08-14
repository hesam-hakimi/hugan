LOCAL_PHASE_SB0 — POST-KEEP READ-ONLY S-B READINESS AND CONTRACT EXTRACTION

You are performing a fresh, independent, strictly read-only verification and planning task.

This task does NOT authorize implementation of S-B. Do not create or modify any file.

1. Authoritative current boundary

The established chronology is:

S-A implementation created
→ independent A1G audit failed
→ bounded S-A repair completed
→ independent A1H re-audit passed
→ exact A1H hashes reconciled against the current bytes
→ the user clicked Keep for exactly the four S-A files
→ S-B implementation has not yet been authorized

The independent decisions were:

SAFE_TO_KEEP_SA: YES
SAFE_TO_PROCEED_TO_S_B: NO
LOCAL_PHASE_A1H_SA_REAUDIT_PASS

The subsequent reconciliation established:

A1H_ORIGINAL_HASH_EVIDENCE_AVAILABLE: YES
CURRENT_BYTES_MATCH_A1H_PASS: YES
A1H_VERDICT_APPLIES_TO_CURRENT_BYTES: YES
KEEP_ACTION_AUTHORIZED_BY_THIS_RECONCILIATION: NO
SAFE_TO_PROCEED_TO_S_B: NO
LOCAL_PHASE_A1H_HASH_RECONCILIATION_MATCH

ChatGPT separately reviewed that evidence and authorized Keep of only the four S-A files. The user reports that Keep has now been clicked.

Treat UI Keep as a user-reported review decision, not as a Git operation. Verify the live repository state independently.

2. Expected repository identity — reverify, never assume

Expected canonical repository:

* Root: C:\repos\etl-extension\etl_fw2\etl_framework_extension
* Origin: https://github.com/TD-Universe/agentic_etl.git
* Branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* Three worktrees total: the main worktree plus two known detached c7 worktrees
* Staged count: zero
* Work remains local-only
* Draft PR #7 remains untouched
* No S-B or later-slice implementation should exist

Operate only in the canonical main worktree. Do not inspect or alter another worktree except for the read-only git worktree list identity check.

3. Exact kept S-A surface

The only S-A files are:

* src/core/settings/EtlSettingsInventory.ts
* src/core/settings/EtlSettingsProvenance.ts
* src/core/settings/EtlSettingsVsCodeBindings.ts
* src/test/suite/settingsInventoryProvenance.test.ts

Recompute full SHA-256 values and compare them with these authoritative A1H values:

* EtlSettingsInventory.ts
    6B99E6EB1851AB45050AE69225D06A59CE6AE0CE85871BF7A9C1DEAD0FBADD84
* EtlSettingsProvenance.ts
    09CD4A53A92D845D6C7F34279CBD2B2495F6C2EAE03D14567CBBC8474D553AC8
* EtlSettingsVsCodeBindings.ts
    0A010841E9806F6FDB51C35559EE20CB4A39A246F29001CA6A9DD749A3CD15D1
* settingsInventoryProvenance.test.ts
    64A4682CB2428B70F1E4B99B706A3050542502E14A57CC4BF7336D5711AB8AE2

Use the complete hashes. Do not rely on abbreviated prefixes or the previously identified transposed-prefix typo.

4. Strict read-only restrictions

Do not:

* edit, save, format, create, rename, move, or delete files;
* click Keep, Undo, Revert, Discard, Restore, or Clean;
* stage, commit, push, stash, reset, checkout, merge, or alter a worktree;
* update Draft PR #7 or invoke CI;
* install dependencies or run lifecycle scripts;
* build, package, install, or smoke-test a VSIX;
* modify package.json, package-lock.json, src/test/testPatterns.ts, control-plane files, documentation, or any pending/protected file;
* implement S-B, S-C, or any later slice;
* treat the S-A implementation chat’s self-reports as independent evidence.

Use only read-only inspection commands. Capture repository identity, porcelain status with untracked files expanded, staged count, worktree list, and relevant hashes at both the start and end.

All pending or dirty files outside the four kept S-A paths are user-owned or pre-existing unless live evidence proves otherwise.

5. Preserve the independent A1H findings

A1H reported no Critical or High findings, but the following remain open and must not be silently described as fixed:

* MEDIUM-1: the S-A suite is currently reachable only through the Electron integration route; the test contains a negative assertion preventing pure-unit discovery.
* MEDIUM-2: EtlSettingsVsCodeBindings.ts has no executable test coverage and currently has no production consumer; its behavior is asserted primarily through source-text checks.
* LOW-1: a precedence assertion is partially self-referential.
* LOW-2: policy-enforced values may appear through VS Code as defaultValue; the limitation needs accurate documentation.
* LOW-3: unbounded recursion depth in deep clone/freeze.
* LOW-4: present and defined may disagree for hostile prototype-chain inputs.
* LOW-5: languageIds is spread without an explicit array guard.
* LOW-6: an own contributes.configuration: undefined edge case lacks coverage and is classified as malformed rather than absent.
* INFO: winningScope is not necessarily the sole source for object-valued settings because VS Code merges objects across scopes.

Determine, using live source evidence, whether any of these findings blocks S-B implementation. Do not repair them in this task. If resolving one requires modifying a protected or pre-existing file, report that exact dependency and stop at planning.

6. S-B intended architectural outcome

S-B is limited to:

* a deeply immutable/frozen ResolvedEtlAgentContext;
* deterministic canonical serialization;
* a deterministic versioned digest over the permitted canonical representation.

S-B must establish a pure trust boundary before any planner or agent consumes the context.

It must not absorb later-slice responsibilities:

* S-C: explicit workspace/resource selection and evidence completeness/ambiguity;
* S-D: bootstrap/result envelopes and child/nested-agent propagation;
* S-E: drift detection, stale-context rejection, and re-plan behavior;
* S-F: user-facing English settings guidance;
* S-G: temporary task overrides;
* S-H: persistent VS Code configuration writes;
* S-I/S-J/S-K: owner/platform-dependent registry, deployment-path, and publisher-recovery contracts.

S-B must not expose, log, serialize, or digest raw secret-like, credential-like, tenant-specific, or physical-storage values. Do not assume raw configuration values are permitted merely because they exist in VS Code. If live contracts do not support a safe representation, identify that as a blocker rather than expanding the trust boundary.

7. Required live-source investigation

Inspect and cite exact file paths and line ranges for:

1. The public types and functions exposed by the four S-A files.
2. Existing repository conventions for immutable domain objects.
3. Existing deterministic serialization, stable-key ordering, hashing, schema-versioning, or digest utilities.
4. Existing context, planning, evidence, bootstrap, envelope, or routing types that might conflict with or constrain ResolvedEtlAgentContext.
5. Existing exports/barrel files and test naming/discovery conventions.
6. Current Node/TypeScript facilities already available without adding a dependency.
7. Any existing type or artifact already named similarly to ResolvedEtlAgentContext.
8. Any current consumer of the S-A modules.
9. Any forbidden early implementation of S-C or later behavior.
10. The smallest exact S-B candidate change surface, distinguishing:

* new S-B files;
* any existing file that would require modification;
* protected/pre-existing files that must remain untouched.

Do not select file paths merely by preference. Ground every proposed path in current repository conventions.

8. Required S-B contract proposal

Produce a concrete, evidence-backed proposal covering:

A. Context schema

For every proposed field, report:

* exact field name and type;
* source/evidence owner;
* whether it is required or optional;
* why it belongs in S-B rather than S-C or later;
* sensitivity classification;
* whether it enters canonical serialization and the digest.

Do not invent environment, workspace, deployment, business, job, or provider values.

B. Immutability contract

Define:

* defensive-copy requirements;
* recursive freezing behavior;
* treatment of arrays and objects;
* prototype and own-property handling;
* cycles and excessive nesting;
* mutation-isolation expectations;
* repeated-construction determinism.

C. Canonical serialization contract

Define explicitly:

* schema/version marker;
* object-key ordering;
* array ordering;
* omitted versus undefined;
* null, booleans, strings, and numbers;
* non-finite numbers;
* unsupported values and prototypes;
* duplicate or ambiguous inputs;
* Unicode/string behavior if relevant;
* fail-closed error outcomes.

D. Digest contract

Determine from existing repository/runtime evidence:

* algorithm;
* encoding;
* version/domain-separation strategy;
* exact bytes being digested;
* whether the digest is recomputed or stored;
* how accidental raw-value or secret inclusion is prevented.

Do not add dependencies.

E. Integration boundary

Explain exactly how S-B may consume safe S-A results without:

* importing VS Code into the pure context module;
* reading configuration again;
* choosing an implicit workspace folder;
* carrying mutable S-A objects;
* implementing S-C selection/completeness;
* implementing S-D propagation or S-E drift handling.

F. Test plan

Provide the smallest focused test matrix that would discriminate:

* stable output across different object insertion orders;
* meaningful array-order preservation;
* deep immutability and mutation isolation;
* canonical serialization determinism;
* digest determinism and domain/version separation;
* unsupported or unsafe input rejection;
* absence of raw-value/secret propagation;
* no VS Code import in the pure S-B module;
* strict boundary against S-C and later slices;
* actual discovery through an existing unmodified test route.

Account explicitly for A1H MEDIUM-1 and MEDIUM-2. Do not modify src/test/testPatterns.ts during this task.

9. Required report

Return:

1. Repository identity and start/end immutability proof.
2. Full current SHA-256 table for all four S-A files.
3. Complete porcelain classification:
    * four kept S-A files;
    * pre-existing/user-owned pending paths;
    * any unexpected path.
4. Confirmation whether an S-B or later artifact already exists.
5. Live-source evidence table with path and line references.
6. Open A1H finding impact table: blocker, non-blocker, or requires separate decision.
7. Proposed S-B schema and trust-boundary table.
8. Canonical serialization and digest specification.
9. Exact proposed implementation file surface.
10. Focused test matrix and unmodified discovery route.
11. All blockers, ambiguities, or user/owner decisions still required.
12. The smallest bounded S-B implementation plan—but no implementation.

If repository identity differs, staged count is nonzero, any S-A full hash differs, an unexpected new artifact exists, protected files drift during inspection, the S-B trust boundary cannot be made explicit, or the exact change surface cannot be bounded, return FAIL.

Finish with exactly one of these outcomes:

POST_KEEP_SA_BYTES_MATCH_A1H: YES|NO
PRE_EXISTING_OR_PROTECTED_DRIFT_DETECTED: YES|NO
S_A_OPEN_FINDINGS_PRESERVED: YES|NO
S_B_SCOPE_CONTRACT_COMPLETE: YES|NO
S_B_READY_FOR_BOUNDED_IMPLEMENTATION: YES|NO
S_B_IMPLEMENTATION_AUTHORIZED: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB0_READINESS_PASS

or:

POST_KEEP_SA_BYTES_MATCH_A1H: YES|NO
PRE_EXISTING_OR_PROTECTED_DRIFT_DETECTED: YES|NO
S_A_OPEN_FINDINGS_PRESERVED: YES|NO
S_B_SCOPE_CONTRACT_COMPLETE: YES|NO
S_B_READY_FOR_BOUNDED_IMPLEMENTATION: YES|NO
S_B_IMPLEMENTATION_AUTHORIZED: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB0_READINESS_FAIL
