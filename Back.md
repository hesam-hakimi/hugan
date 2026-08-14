TASK: LOCAL_PHASE_A1G — INDEPENDENT READ-ONLY AUDIT OF S-A SETTINGS INVENTORY AND PROVENANCE

Act as an independent adversarial auditor. You did not implement this change. Treat the implementation report and all previous-chat conclusions as untrusted claims that must be re-derived from the live workspace.

TARGET

* Repository: etl_framework_extension
* Use the currently selected repository root in this existing multi-root VS Code workspace.
* The candidate changes are still pending behind Keep/Undo.
* Do not click Keep, Undo, Revert, Discard, Clean, Restore, or any equivalent action.
* If the four candidate files are not visible to this chat, stop with CANDIDATE_OVERLAY_NOT_VISIBLE. Do not ask the user to Keep them merely to make them visible.

CANDIDATE S-A FILES

1. src/core/settings/EtlSettingsInventory.ts
2. src/core/settings/EtlSettingsProvenance.ts
3. src/core/settings/EtlSettingsVsCodeBindings.ts
4. src/test/suite/settingsInventoryProvenance.test.ts

Reported but untrusted claims:

* All four files are new.
* No pre-existing source or control-plane file was edited.
* npm ci was previously authorized and completed; dependencies now exist.
* package.json and package-lock.json remained byte-identical.
* Targeted TypeScript checks passed.
* Direct Mocha execution reported 22 passing tests.
* S-B and later slices were not implemented.

MODE AND IMMUTABILITY

This phase is strictly read-only and audit-only.

* Do not edit, create, delete, rename, format, save, stage, commit, or generate repository files.
* Do not click Keep or Undo.
* Do not run npm ci, npm install, package updates, build, packaging, VSIX, baseline regeneration, or snapshot updates.
* Use only already-installed local dependencies.
* Do not use npx if it could download anything.
* Targeted no-emit type checks and targeted tests are permitted.
* Do not write into the repository’s out, dist, coverage, snapshot, or cache directories.
* If temporary compilation is indispensable, use a fresh OS temporary directory outside the repository and remove only that directory afterward.
* Do not clean existing node_modules, ignored output, or user-owned pending files.
* Do not touch sibling worktrees or consumer workspaces.
* Do not begin S-B or propose fixes as edits. Report a minimal repair plan only.

ESTABLISH THE BASELINE FIRST

Capture and report:

* exact repository root, origin, branch, HEAD;
* all worktrees;
* staged state;
* porcelain status with untracked files expanded;
* hashes of every pre-existing pending/protected file;
* hashes of the four S-A candidate files;
* hashes of package.json and package-lock.json.

Recheck the same state at the end.

INTENDED S-A BOUNDARY

S-A is source-only infrastructure. It must provide:

A. A pure manifest settings inventory that does not import or call VS Code.

B. A provenance resolver over an injected configuration host that models only values actually exposed by the supported VS Code API.

C. A narrow VS Code binding responsible only for reading the installed extension manifest and adapting WorkspaceConfiguration.

D. Deterministic, English-only, read-only results.

E. Focused tests demonstrating the above.

S-A must not:

* write configuration;
* call update;
* select a ConfigurationTarget;
* register onDidChangeConfiguration;
* freeze task context;
* implement S-B context serialization or hashing;
* spawn agents;
* persist state;
* read environment variables;
* access secrets;
* log setting values;
* choose a workspace folder implicitly;
* define Job/Environment grammar, deployment profiles, or any structural policy.

MANDATORY AUDIT QUESTIONS

1. VS CODE VERSION COMPATIBILITY

The repository reportedly declares engines.vscode: ^1.95.0, while installed typings may be @types/vscode@1.109.0.

* Enumerate every WorkspaceConfiguration.inspect() field and VS Code API used by the candidate.
* Prove each field exists at the repository’s minimum supported VS Code version.
* Newer installed typings alone are not proof of minimum-version compatibility.
* Do not invent fields such as remoteValue.
* If minimum-version compatibility cannot be established from available authoritative evidence, record a compatibility blocker rather than assuming it.

2. PRECEDENCE AND PRESENCE SEMANTICS

Verify the resolver exactly matches real VS Code behavior:

* effective-value precedence;
* normal versus language-specific override fields;
* globalValue, workspaceValue, and workspaceFolderValue;
* default and language-default handling;
* winning scope versus all contributing scopes;
* property presence versus value equality;
* preservation of false, 0, "", and null;
* distinction between an omitted default and an explicitly declared default.

A test in which multiple scopes contain identical values must still identify the correct winning scope.

3. MANIFEST INVENTORY

Audit contributes.configuration handling for:

* object form;
* array form;
* absent configuration;
* malformed entries;
* duplicate keys across sections;
* properties without type;
* string versus array type declarations;
* omitted versus declared scope;
* title/category metadata;
* deterministic ordering;
* correct namespace and relative-key handling;
* no accidental interpretation of arbitrary manifest data as a setting.

Determine whether duplicate declarations fail closed, are represented explicitly, or are silently overwritten.

4. MULTI-ROOT SAFETY

Prove that:

* with two or more workspace folders and no explicit resource, resolution fails closed;
* workspace.workspaceFolders?.[0] is never selected;
* sibling-folder settings never contaminate the selected folder;
* the resource supplied to getConfiguration and inspect is handled consistently;
* single-folder behavior does not weaken the multi-root contract.

5. PURITY AND SIDE EFFECTS

Search the candidate files for direct or indirect use of:

* configuration writes or update;
* ConfigurationTarget;
* onDidChangeConfiguration;
* filesystem or network writes;
* logging;
* environment variables;
* secret storage;
* caching that can become stale;
* ambient workspace-folder discovery in the pure modules.

Confirm that only the binding file imports vscode.

6. DATA MINIMIZATION AND SECURITY

Determine whether inventory or provenance results can expose credential-like or tenant-specific values unnecessarily.

* No secret value may be returned, logged, hashed into diagnostics, or included in errors.
* Manifest metadata and manifest defaults must remain distinguishable from effective user configuration.
* Flag any API that makes unsafe value propagation likely for S-B.

7. API AND TYPE QUALITY

Review the exported and internal types for:

* discriminated-union exhaustiveness;
* serializability;
* absence of any-driven ambiguity;
* deterministic output;
* stable English error codes and messages;
* minimal public surface;
* compatibility with a future S-B context layer without prematurely implementing or freezing S-B semantics.

Check whether the implementation is unnecessarily large, duplicated, or internally contradictory. File size alone is not a defect; identify concrete maintainability or correctness consequences.

8. BINDING CORRECTNESS

Verify that the VS Code binding:

* resolves the intended extension ID;
* reads the installed extension manifest, not an unrelated workspace manifest;
* handles unavailable extensions and malformed manifests safely;
* does not silently mix source version, installed version, or sibling-extension state;
* does not make production configuration calls during inventory construction.

9. TEST ROUTE AND COVERAGE

Independently prove whether src/test/suite/settingsInventoryProvenance.test.ts is discovered by the actual repository test runner.

Do not rely only on the test’s own assertions or the previous report.

Audit coverage for at least:

* object and array configuration forms;
* missing and malformed manifests;
* duplicate declarations;
* missing versus explicit defaults;
* false/zero/empty/null defaults;
* scope omitted versus declared;
* normal and language-specific overrides;
* identical values at multiple scopes;
* unknown setting;
* unavailable inspect;
* unavailable get;
* multi-root ambiguity;
* explicit resource selection;
* deterministic sorting;
* English-only strings;
* absence of mutation and configuration-write APIs.

Identify self-fulfilling tests, source-text-only assertions that do not prove runtime behavior, and important mutation survivors.

10. CHANGE-SURFACE INTEGRITY

Prove that:

* only the four candidate files belong to S-A;
* no pre-existing pending/Keep file changed;
* package.json, package-lock.json, control-plane files, test registries, and protected Slice-1 files remain unchanged;
* no S-B functionality or unrelated production wiring was added;
* existing ignored outputs were not mistaken for product changes.

ALLOWED VERIFICATION

Use the smallest relevant set only:

* source inspection and searches;
* existing local TypeScript compiler in no-emit mode;
* the exact targeted S-A test;
* inspection of actual test-runner globs/configuration;
* VS Code diagnostics;
* read-only Git/status/hash commands.

Record every command and exact exit status. A passing test is not sufficient if the test is not genuinely registered or does not test the claimed contract.

REQUIRED REPORT

Write the report in English and include:

1. Repository identity and start-state proof.
2. Findings ordered Critical, High, Medium, Low, with exact file and line citations.
3. Contract matrix for inventory, provenance resolver, VS Code binding, and tests.
4. VS Code minimum-version compatibility verdict.
5. Manifest parsing and duplicate-key verdict.
6. Precedence/language-override verdict.
7. Multi-root and trust-boundary verdict.
8. Test-discovery and coverage verdict.
9. Exact commands and results.
10. Start/end status and SHA-256 immutability proof.
11. Minimal repair plan for every blocking issue, without editing anything.
12. Explicit answers:

* SAFE_TO_KEEP_SA: YES or NO
* SAFE_TO_PROCEED_TO_S_B: YES or NO

End with exactly one marker:

* LOCAL_PHASE_A1G_SA_AUDIT_PASS
* LOCAL_PHASE_A1G_SA_AUDIT_PASS_WITH_CORRECTIONS
* LOCAL_PHASE_A1G_SA_AUDIT_FAIL

A PASS requires no unresolved correctness, compatibility, test-registration, isolation, security, or immutability issue. Cosmetic observations alone may produce PASS_WITH_CORRECTIONS, but any behaviorally material uncertainty requires FAIL.

Do not implement repairs. Do not start S-B.
