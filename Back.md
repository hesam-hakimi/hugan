LOCAL_PHASE_A1H — Independent Read-Only Re-Audit of the Repaired S-A Settings Inventory and Provenance

You are an independent adversarial auditor. This is a fresh audit chat. Do not trust or repeat the implementation chat’s conclusions. Inspect the live candidate overlay and independently derive every verdict from repository evidence and the real VS Code API behavior.

EXPECTED TARGET — verify, never assume:

Repository root:
C:\repos\etl-extension\etl_fw2\etl_framework_extension

Origin:
https://github.com/TD-Universe/agentic_etl.git

Branch:
feature/v3-agentic-redesign

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

Candidate S-A files:

- src/core/settings/EtlSettingsInventory.ts
- src/core/settings/EtlSettingsProvenance.ts
- src/core/settings/EtlSettingsVsCodeBindings.ts
- src/test/suite/settingsInventoryProvenance.test.ts

If the target identity differs, stop with TARGET_MISMATCH.

MODE AND IMMUTABILITY

This phase is strictly read-only.

Do not:

- create, edit, delete, rename, format, save, stage, commit, restore, revert, clean, reset, stash, checkout, or otherwise mutate any file;
- click Keep, Undo, Revert, Discard, Restore, or Clean;
- install, update, or remove dependencies;
- run lifecycle scripts;
- build, package, install, uninstall, or replace the VSIX;
- modify package.json, package-lock.json, testPatterns.ts, control-plane files, protected files, or any pre-existing Pending/Keep file;
- start S-B or any later slice;
- borrow typings, dependencies, or code from sibling repositories.

You may run already-available read-only inspections, no-emit type checks, lint checks, and focused tests only when they require no download, installation, or repository mutation.

Capture repository identity, porcelain status, staged state, worktree list, candidate hashes, package.json hash, package-lock.json hash, and all pre-existing Pending/Keep hashes at the start. Recheck them at the end.

AUDIT SCOPE

Audit S-A only: read-only settings inventory, manifest-declaration diagnostics, effective-setting provenance, multi-root fail-closed behavior, and the narrow VS Code binding.

Re-derive and verify all of the following.

1. REAL VS CODE inspect() SEMANTICS

Ground the implementation against the actual WorkspaceConfiguration.inspect() contract supported by this repository’s VS Code version.

Verify that:

- runtime inspect results may contain all supported fields as own properties;
- a scope contributes only when its runtime value is not undefined;
- property presence alone never means contribution;
- truthiness and value equality are never used to determine contribution;
- false, 0, "", null, empty arrays, and empty objects remain defined contributions;
- winningScope is the highest-precedence defined contribution according to the documented VS Code order;
- language-override fields are handled explicitly and correctly.

2. DENSE INSPECT REGRESSION COVERAGE

Tests must use a realistic dense VS Code-style inspect object in which absent scopes are present with undefined values.

Prove that the repaired tests fail against the pre-repair hasOwnProperty-based rule and pass against the repaired implementation.

Cover at minimum:

- only Default defined;
- Default plus Global;
- Workspace versus Workspace Folder;
- complete language-override precedence;
- language override above workspace-folder;
- identical values at multiple scopes;
- every falsy defined value;
- no defined value;
- multi-root with and without an explicit resource.

Do not accept sparse fake inspect objects as the primary proof.

3. DUPLICATE MANIFEST DECLARATIONS

Verify that duplicate declarations:

- are not silently collapsed;
- preserve every declaration and its relevant metadata;
- retain conflicting defaults, types, scopes, titles, descriptions, markdown descriptions, categories, and source positions where available;
- produce an explicit fail-closed ambiguous outcome;
- trigger zero configuration reads while ambiguous;
- never invent a precedence rule.

4. MALFORMED MANIFEST ENTRIES

Verify that malformed property declarations:

- do not become ordinary empty descriptors;
- return a typed fail-closed diagnostic;
- do not echo raw malformed data in user-facing text;
- do not cause configuration reads.

5. TRUST AND VALUE-EXPOSURE BOUNDARY

Verify that the public S-A result does not expose raw effective values or per-scope values that may contain tenant-specific or sensitive data.

It may expose only the metadata required by S-A, such as:

- whether an effective value is defined;
- contributing scopes;
- winning scope;
- scope provenance;
- language IDs;
- manifest declaration metadata and diagnostics.

If the original S-A contract genuinely requires returning a raw effective value, report the exact contract conflict instead of silently adding redaction policy or inventing a sensitivity classifier.

6. IMMUTABILITY AND ALIASING

Verify that:

- manifest defaults and declaration objects are not returned by mutable reference;
- inventory, descriptors, declaration arrays, diagnostics, scope-state arrays, and provenance results cannot mutate the source manifest or another result;
- repeated construction is deterministic and independent;
- required result surfaces are deeply cloned/frozen or equivalently protected.

7. MULTI-ROOT AND RESOURCE SELECTION

Verify fail-closed behavior:

- with two or more workspace folders and no explicit resource, return the typed ambiguous-resource outcome;
- do not inspect workspaceFolders[0];
- do not use an ambient or sibling folder fallback;
- with an explicit resource, only that resource’s configuration participates.

8. VS CODE BINDING AND PROHIBITED SURFACES

Verify that the VS Code binding is narrow and that pure modules do not import VS Code.

Confirm there are no setting writes and no use of:

- update()
- ConfigurationTarget
- onDidChangeConfiguration
- process.env
- secret values or SecretStorage
- filesystem writes
- network calls
- logging of values
- persistence
- mutable caches
- ambient workspace-folder fallback

A documentation occurrence of a prohibited word is not itself a behavior violation; distinguish comments from reachable calls.

9. MANIFEST INVENTORY CONTRACT

Verify deterministic namespace discovery, object/array/absent contributes.configuration handling, declared-type extraction, manifest-default distinctions, scope classification, language-overridable metadata, deterministic sorting, and declaration diagnostics.

Specifically verify markdownDescription and language-related manifest metadata are either preserved according to the contract or explicitly reported as unsupported; they must not be silently discarded.

10. TEST ROUTE

Verify the S-A test is discovered through an already-existing clean route without editing the pre-existing dirty testPatterns.ts.

Run the smallest relevant existing checks. Do not download VS Code, Test Electron, or any additional tool. If a required test would cause a download or installation, stop and report TOOLING_REQUIRED.

Separate unrelated pre-existing failures from S-A failures using concrete evidence.

11. CHANGE-SURFACE INTEGRITY

At the end prove:

- repository root, origin, branch, HEAD, and worktree list are unchanged;
- staged count remains zero;
- package.json and package-lock.json are byte-identical;
- every pre-existing Pending/Keep/protected file is byte-identical;
- only the four S-A candidate files belong to this candidate overlay;
- no S-B or later-slice implementation exists.

REQUIRED OUTPUT

Return:

1. Repository identity and start/end immutability proof.
2. Severity-ranked findings with exact file:line citations.
3. A contract matrix for:
   - manifest inventory;
   - dense inspect semantics;
   - precedence and language overrides;
   - duplicate handling;
   - malformed-entry handling;
   - trust/value-exposure boundary;
   - immutability;
   - multi-root behavior;
   - VS Code binding;
   - test discovery.
4. Exact commands and exit codes.
5. Test counts and evidence that the regression would fail pre-repair.
6. Any unrelated pre-existing failures, clearly separated.
7. End-state hashes and change-surface proof.
8. The smallest repair plan if any defect remains.

FINAL DECISION RULE

Return SAFE_TO_KEEP_SA: YES only if:

- no Critical or High S-A finding remains;
- real dense inspect semantics are correctly modeled;
- the regression demonstrably catches the pre-repair defect;
- duplicates and malformed declarations fail closed;
- no unsafe raw-value propagation remains;
- multi-root isolation and immutability hold;
- all relevant focused checks pass;
- all non-S-A files remain unchanged.

Otherwise return SAFE_TO_KEEP_SA: NO.

Always return:

SAFE_TO_PROCEED_TO_S_B: NO

S-B requires a separate authorization after S-A is kept and independently closed.

Finish with exactly one marker:

LOCAL_PHASE_A1H_SA_REAUDIT_PASS

or

LOCAL_PHASE_A1H_SA_REAUDIT_FAIL
