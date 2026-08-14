LOCAL_PHASE_A1F — Implement S-A: Read-Only Settings Inventory and Inspect-Based Provenance

You are starting a new implementation phase in the existing multi-root VS Code workspace. Explicitly select the etl_framework_extension repository before doing anything.

This prompt grants implementation authorization for S-A only. It does not authorize S-B or any later slice.

Authoritative handoff

The preceding read-only design phase completed with:

LOCAL_PHASE_A1E_CONFIG_CONTEXT_CHAT_CONTRACT_PASS_WITH_RESIDUALS

That phase established the following accepted constraints:

* The product and every user-facing string are English-only.
* The ETL Orchestrator will eventually resolve and freeze configuration at the planning boundary.
* Child agents must eventually receive a frozen, digest-validated context and must not reread ambient VS Code configuration.
* Settings provenance must come from WorkspaceConfiguration.inspect().
* Explicit workspace-folder selection is required in multi-root workspaces; never silently use workspaceFolders[0].
* Maintainer-owned structural policy, external platform contracts, secrets, and computed paths must never be exposed as ordinary user settings.
* Existing Pending/Keep changes are user-owned and must remain untouched.
* No environment vocabulary, aliases, grammar, layout profile, deployment profile, or synthetic default has been ratified.
* The live repository is the primary implementation evidence. Earlier chats are contextual handoff, not independent authority.

Objective

Implement the smallest production-quality, runtime-read-only settings inventory and provenance API.

It must:

1. Discover this extension’s declared settings from the local package manifest.
2. Report exact setting metadata.
3. Resolve the effective value for an explicitly selected resource URI.
4. report every contributing VS Code scope and the winning scope using inspect().
5. Perform no configuration writes and introduce no behavioral change.

Strict scope

Permitted:

* Add the minimal clean production source needed for the read-only inventory/provenance API.
* Add focused unit tests for that API.
* Run only the narrow tests and type checks required for this slice.

Prohibited:

* Do not modify package.json.
* Do not add, remove, rename, rescope, or change the default of any setting.
* Do not implement the proposed targetEnvironment.default key.
* Do not implement an environment/profile registry.
* Do not add commands, chat handlers, orchestrator wiring, context freezing, agent envelopes, configuration-change listeners, or persistent setting writes.
* Do not call WorkspaceConfiguration.update().
* Do not use ConfigurationTarget.
* Do not register onDidChangeConfiguration.
* Do not read secrets, credentials, process.env, consumer infrastructure, or external systems.
* Do not log or persist effective setting values.
* Do not run package installation, VSIX packaging, deployment, publishing, or a full repository build.
* Do not stage, commit, push, merge, rebase, reset, stash, clean, checkout, or switch branches.
* Do not click Keep, Undo, Revert, Discard, or similar controls.
* Do not modify any file that was already modified or untracked at task start.

If a required existing file is already dirty, do not edit it. Prefer isolated new files only when that fits the repository architecture; otherwise stop and report the exact overlap.

Required implementation contract

A. Manifest inventory

* Read contributes.configuration from the local extension manifest.
* Support both object and array forms.
* Discover settings dynamically; do not hard-code the observed count or key list.
* Include only keys in the exact databricks-etl-copilot namespace.
* Preserve deterministic lexical ordering.
* For every setting report:
    * exact full key;
    * relative key;
    * type;
    * manifest default, including the distinction between missing and explicit falsy values;
    * English title and description;
    * explicitly declared scope, if any;
    * effective VS Code scope semantics.
* If scope is omitted, represent that fact explicitly and apply VS Code’s actual default scope semantics. Do not pretend the manifest declared a scope.

B. Effective value and provenance

For an explicitly supplied resource URI, use the equivalent of:

vscode.workspace.getConfiguration('databricks-etl-copilot', resourceUri)

* Obtain the effective value through get(relativeKey).
* Obtain provenance through inspect(relativeKey).
* Model all values exposed by the installed VS Code API, including applicable:
    * default;
    * global/user;
    * remote;
    * workspace;
    * workspace-folder;
    * default-language;
    * global-language;
    * workspace-language;
    * workspace-folder-language.
* Derive the winning scope from VS Code precedence and presence metadata, never by comparing values.
* Report all contributing scopes separately from the winning scope.
* Preserve undefined, false, 0, "", empty arrays, and empty objects as distinct states.
* Do not claim that inspect() identifies which extension declared a key. Manifest discovery establishes ownership; inspect() establishes effective scope provenance.

C. Multi-root behavior

* Resource-aware inspection must receive an explicit selected workspace-folder/resource URI.
* With multiple workspace folders and no explicit selection, return a typed ambiguity result.
* Never select the first folder implicitly.
* Never read sibling workspace folders to supplement the selected folder.

D. Read-only and trust boundary

* The implementation must have no mutation path.
* Do not cache values beyond the lifetime of the inspection call.
* Do not serialize values to disk, logs, telemetry, prompts, or generated assets.
* S-A handles user-editable Class A setting metadata only.
* Do not classify or propagate maintainer-owned Class B, platform-owned Class C, secret Class D, or computed Class E values as editable settings.
* All newly added user-facing text and test fixtures must be English.

E. Future compatibility without implementation

Design the return types so a future ResolvedEtlAgentContext builder can consume them, but do not implement that context, its digest, orchestrator propagation, child-agent behavior, or any setting write in this slice.

Required tests

Add focused tests proving:

1. Configuration contribution object and array forms are both handled.
2. Inventory is dynamically derived and deterministically ordered.
3. Metadata preserves missing versus falsy defaults.
4. Omitted scope is reported explicitly.
5. Effective value comes from get().
6. Winning and contributing scopes come from inspect() precedence.
7. Language-overridable inspection values are represented when supported.
8. A resource URI is used for resource-scoped resolution.
9. Multiple folders without an explicit selection fail closed and never use index zero.
10. false, 0, "", and undefined remain distinct.
11. The API performs no update, listener registration, persistence, logging, or secret/environment read.
12. Existing Pending/Keep files remain byte-identical.

Execution procedure

Before editing:

* Establish and report repository root, origin, branch, HEAD, worktrees, staged state, and full porcelain status.
* Record the exact set and SHA-256 hashes of all pre-existing modified and untracked files.
* Identify clean candidate files for S-A.

Then implement only S-A.

Verification:

* Run the smallest relevant test set.
* Run a targeted type check if available without installation or generated-output changes.
* Recheck all pre-existing pending-file hashes.
* Report every created or edited file and why it was needed.
* Clearly separate pre-existing changes from this phase’s changes.
* Do not commit or stage anything.

Completion marker

If the implementation and focused verification pass, end with:

LOCAL_PHASE_A1F_SA_SETTINGS_INVENTORY_PROVENANCE_IMPLEMENTED

If blocked by dirty-file overlap, missing test infrastructure, or an architectural dependency, make no speculative workaround and end with:

LOCAL_PHASE_A1F_SA_SETTINGS_INVENTORY_PROVENANCE_BLOCKED

Include the exact blocker and the smallest next decision required.
