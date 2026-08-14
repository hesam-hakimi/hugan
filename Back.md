Continue the current S-A implementation in this same chat from the independent audit failure.

The four S-A candidate files are still unkept. This message authorizes a bounded repair of S-A only. It does not authorize S-B or any later slice.

Independent audit result:

* LOCAL_PHASE_A1G_SA_AUDIT_FAIL
* SAFE_TO_KEEP_SA: NO
* SAFE_TO_PROCEED_TO_S_B: NO

Repository identity expected:

* Repository: etl_framework_extension
* Branch: feature/v3-agentic-redesign
* HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847

Authorized files only:

1. src/core/settings/EtlSettingsInventory.ts
2. src/core/settings/EtlSettingsProvenance.ts
3. src/core/settings/EtlSettingsVsCodeBindings.ts
4. src/test/suite/settingsInventoryProvenance.test.ts

Before editing, re-establish the live repository identity, staged state, porcelain inventory, and SHA-256 baseline for every pending/Keep file plus package.json and package-lock.json. If the repository identity or the four candidate files differ unexpectedly, stop and report the mismatch.

Required repairs

1. Fix real VS Code inspect() contribution semantics

The current implementation incorrectly uses own-property presence to determine whether a scope contributed.

VS Code 1.95 returns a dense inspect() result: scope fields exist even when their value is undefined.

A scope contributes if and only if its corresponding runtime value is not undefined.

Preserve all defined falsy values as real contributions, including:

* false
* 0
* ""
* null
* empty arrays
* empty objects

Derive the winning scope from the documented VS Code precedence order using defined values, not property presence or truthiness.

2. Handle duplicate manifest declarations safely

Do not silently retain the first duplicate declaration.

Implement one deterministic fail-closed representation:

* preserve every declaration and return an explicit ambiguous/duplicate result with sufficient metadata; or
* reject duplicate declarations with a typed diagnostic.

Conflicting defaults, types, scopes, titles, descriptions, and language variants must not be discarded.

Do not invent a precedence rule for duplicates.

3. Replace sparse fake inspection tests

Add regression tests using a dense VS Code 1.95-style inspection object in which all inspection fields exist and absent scopes contain undefined.

Cover at minimum:

* only Default defined;
* Default plus Global;
* Workspace and Workspace Folder precedence;
* language override precedence;
* identical values at several scopes;
* every supported falsy value;
* all fields present but only one field defined;
* multi-root resolution with no resource;
* explicit resource selection;
* no implicit workspaceFolders[0].

The regression must fail against the pre-repair implementation.

4. Fail closed on malformed manifest properties

A non-object or otherwise malformed configuration property entry must not become an empty valid descriptor.

Return a typed invalid-manifest diagnostic or reject inventory construction deterministically. Include the setting key and a safe English explanation, but do not expose arbitrary raw manifest content.

5. Prevent sensitive-value propagation

S-B sensitivity classification is not authorized.

The public S-A provenance result must expose scope presence/definedness, contributing scopes, winning scope, and provenance metadata without logging or serializing raw effective/contributing values.

If removing or changing raw-value exposure conflicts with an explicitly authorized S-A API contract, stop and report the precise conflict and the smallest decision required. Do not invent a sensitivity classifier and do not begin S-B.

6. Eliminate mutable aliasing

Returned inventory descriptors and manifest defaults must not alias mutable manifest objects.

Use deterministic defensive copying and/or freezing, and add mutation-isolation tests proving that modifying returned data cannot modify the source manifest or another result.

Preserve existing valid boundaries

Keep all of the following:

* narrow VS Code binding;
* the existing extension ID lookup;
* injected configuration host;
* multi-root fail-closed behavior;
* English-only user-facing strings;
* deterministic setting ordering;
* no setting writes;
* no ConfigurationTarget;
* no onDidChangeConfiguration;
* no process.env;
* no secrets, logging, persistence, filesystem access, network access, or cross-call cache;
* no ambient workspace-folder fallback;
* no S-B context serialization, envelopes, orchestrator freezing, chat guidance, or later-slice work.

Forbidden actions

Do not:

* edit package.json, package-lock.json, testPatterns.ts, or any other pre-existing pending/Keep file;
* run another package installation;
* borrow dependencies or typings from sibling repositories;
* run a repository build, package operation, or VSIX operation;
* stage, commit, push, merge, rebase, reset, checkout, stash, clean, or change worktrees;
* click or invoke Keep, Undo, Revert, Discard, Restore, or Clean;
* repair unrelated repository errors, including the existing OnboardingWriteApproval.test.ts:200 failure.

Dependencies have already been restored. Use only the installed local toolchain.

Verification required

Run and report:

1. a focused compile/type check covering only the four S-A files;
2. targeted ESLint for the four files, if available without changing configuration;
3. direct targeted Mocha execution for settingsInventoryProvenance.test.ts;
4. proof that its clean integration-test discovery route still works without modifying testPatterns.ts;
5. source scans proving the prohibited APIs and later-slice behavior remain absent;
6. start/end Git status and SHA-256 comparison for every pre-existing pending/Keep file, package.json, and package-lock.json.

Do not treat an unrelated full-repository failure as an S-A failure, but report it separately and prove it was pre-existing.

Final report

Return:

* exact files changed;
* each audit finding and its repair;
* exact verification commands and exit codes;
* targeted test count;
* remaining blockers or residual risks;
* end-state staged count and hash-integrity proof;
* SAFE_TO_KEEP_SA: YES or NO;
* SAFE_TO_PROCEED_TO_S_B: NO.

Even if the repair succeeds, do not proceed to S-B. Stop for a fresh independent audit.
