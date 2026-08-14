TASK: LOCAL PHASE A1E — ETL ORCHESTRATOR CONFIGURATION UX AND RESOLVED AGENT CONTEXT CONTRACT

Continue from the completed A1D ratification packet in this same chat.

A1D ended with:

LOCAL_PHASE_A1D_OWNER_DECISIONS_PARTIAL

Preserve its authority state exactly:

* Three principles were ratified only at principle/design level.
* Every R1–R20 detail decision remains unresolved unless independently shown otherwise.
* No ADR write or implementation was authorized.
* Slice 2 and S1/S2/S3 implementation remain NOT AUTHORIZED.
* Existing pending/Keep changes and all previous sessions must remain untouched.
* The ordinary Extension consumer must never be asked to choose a Framework structural convention.

1. Execution mode

Perform a strictly read-only architecture and UX audit.

Permitted:

* Read the live extension repository, package metadata, VS Code configuration contributions, orchestrator code, agent-spawn code, relevant tests and the explicitly selected consumer workspace.
* Run non-mutating inspection commands such as Git identity/status/diff and text searches.

Forbidden:

* No file create, edit, save, format, rename or delete.
* No Keep, Undo, Revert, Discard, Clean, Restore, Checkout, Reset or Stash.
* No stage, commit, push, merge, rebase or branch/worktree mutation.
* No build, test, package, install, uninstall or VSIX replacement.
* No ADR write.
* No Databricks, ADF, DBFS, MSSQL, Jira or Confluence write.
* No implementation or scaffolding.

Capture repository identity, HEAD, staged state and the exact pending-file/hash inventory before inspection. Recheck them at the end.

2. Objective

Design, but do not implement, a configuration and conversational-help contract in which:

1. A user can ask the primary ETL Orchestrator about current ETL settings.
2. The Orchestrator can explain exactly how an adjustable setting may be changed in VS Code.
3. A user can request a preview of a settings change through chat.
4. The Orchestrator distinguishes adjustable operational settings from structural product policy.
5. Every child agent spawned by the ETL Orchestrator receives the same immutable, validated effective configuration.
6. No child agent independently guesses configuration from cwd, filenames, prevalence, neighbouring workspace folders, stale chat history or ambient process state.

Example user intents include:

* “What ETL environment is currently active?”
* “How can I change the default environment?”
* “Preview changing the target environment to sit.”
* “Use this environment only for the current task.”
* “Save this setting for this workspace folder.”
* “Show which value came from User, Workspace, Workspace Folder, policy registry or task override.”
* “Why can’t I select prod/prd/prod_c2?”
* “Which deployment profile and root will be used?”
* “What configuration will the agents spawned for this task receive?”

The chat UX must also support equivalent Persian questions.

3. Do not treat all decisions as user settings

Define and keep separate at least these classes:

A. User-adjustable operational selections

Candidate examples, subject to live-code verification:

* Explicitly selected workspace folder.
* Target environment selected from a ratified vocabulary.
* Task-only environment override.
* Evidence scope selected from a ratified set.
* Approved layout/profile identifier.
* Deployment profile identifier.
* Preview/confirmation preferences.
* Read-only diagnostic verbosity.

A user may choose only values already allowed by a ratified, versioned registry. A settings field must never manufacture authority for a new grammar, alias or structural convention.

B. Maintainer-owned structural policy

Not ordinary consumer settings:

* Job and Environment CREATE grammars.
* Canonical sanitizer and filename grammar.
* Include-resolution contract.
* Family topology.
* Split EXTRACT/LOAD grammar.
* Profile-registry contents and versions.
* Fallback behavior when evidence is empty, incomplete or ambiguous.
* Standalone SQL lifecycle policy.
* Shared/common configuration lifecycle policy.
* Onboarding artifact family.
* Mixed-convention behavior.
* Migration and managed-ownership policy.

These remain governed by the unresolved R decisions and must fail closed where A1D requires it.

C. External CD/platform-owner configuration

Examples:

* Typed deployment-root components.
* Provider URI/canonicalization scheme.
* Environment vocabulary and alias/casing authority.
* Conditional version-segment semantics.
* Publisher receipt contract.
* Partial-publish behavior.
* Registration-path serialization.

The Orchestrator may display these settings and identify their owner, but must not invent values.

D. Secrets

Secrets, tokens and credentials must never be stored directly in VS Code settings, prompts, logs, child-agent context or generated manifests.

Design only opaque references backed by an approved secret store or credential provider.

E. Computed/read-only facts

Examples:

* Projected deployed path.
* Actual deployed path from a successful publisher receipt.
* Registration path derived from the actual receipt.
* Resolved include closure.
* Manifest digest/version.
* Configuration provenance.
* Discovery-completeness state.

These must not be independently editable settings.

4. ETL Orchestrator as the sole configuration resolver

Design the primary ETL Orchestrator as the single owner of effective configuration resolution.

It must:

1. Require an explicit selected workspace-folder URI in a multi-root workspace.
2. Read configuration at the correct VS Code resource scope.
3. Resolve and preserve the provenance of each value from:
    * extension defaults;
    * User settings;
    * Workspace settings;
    * Workspace Folder settings;
    * a versioned recognized-profile/policy registry;
    * explicit task-only overrides;
    * external CD/platform configuration;
    * secret references.
4. Reject ambiguity instead of silently selecting by precedence when two values belong to different authority domains.
5. Validate values against the ratified registry and policy version.
6. Create an immutable task-specific configuration snapshot.
7. Freeze that snapshot before planning or spawning agents.
8. Keep a running task pinned to its snapshot even if VS Code settings later change.
9. Require a new resolve/validate/replan cycle for later tasks after a settings change.
10. Never treat another workspace folder, the extension source repository, examples, fixtures, generated previews or editor-dirty review artifacts as consumer configuration evidence.

Do not assume that VS Code’s generic settings precedence alone resolves authority conflicts. Report the difference between technical configuration precedence and product-policy authority.

5. Required child-agent context contract

Propose a typed immutable contract named provisionally:

ResolvedEtlAgentContext

The final name may be corrected after inspecting current naming conventions.

At minimum it must contain:

* schemaVersion
* taskId
* contextId
* contextDigest
* createdAt
* explicit selected workspaceFolderUri
* consumer/evidence scope
* effective operational settings
* provenance and scope of every setting
* recognized profile-registry ID and version
* policy/ADR version
* artifact-family-specific profile IDs
* canonical environment token, when ratified
* task-only overrides
* deployment profile/root references, never guessed values
* discovery-completeness attestation
* applicable capability and prohibition set
* unresolved/blocking decision codes
* redacted secret-reference metadata only
* manifest ID/version/digest
* parent Orchestrator identity/version

Specify the child-agent bootstrap protocol:

1. The Orchestrator resolves and validates the context.
2. It freezes the snapshot and computes a digest.
3. Each child receives a small bootstrap envelope containing the task ID, context ID, schema version and digest.
4. The child obtains the full context through a read-only context provider/tool, or receives the complete immutable snapshot if the provider is unavailable.
5. Before any action, the child validates the schema version and digest.
6. The child must fail closed when context is missing, stale, incomplete, belongs to a different workspace folder, or cannot be authenticated against the parent snapshot.
7. Every child result reports the context ID, schema version and digest it actually consumed.
8. The Orchestrator rejects results produced under a different context.
9. Children may not reread VS Code settings and produce their own effective configuration.
10. Children may request clarification from the Orchestrator but may not fill missing structural values themselves.

Also explain how nested agents inherit the same snapshot without relying on chat history.

6. Conversational configuration-help contract

Design an ETL Orchestrator chat flow that can teach the user how configuration works.

For every configuration question, the Orchestrator should report:

* Human-readable setting name.
* Proposed or existing VS Code key.
* Current effective value.
* Whether the key is actually implemented in the installed extension or only proposed.
* Value source and scope: Default, User, Workspace, Workspace Folder, task override, registry or external owner.
* Allowed values and the registry/version defining them.
* Whether the user is permitted to edit it.
* Exact VS Code UI route and settings-search phrase.
* Exact settings.json scope and example when appropriate.
* Chat-based preview syntax.
* Expected impact on future tasks.
* Whether a new plan, agent respawn or reload is needed.
* Any blocker or unresolved authority decision.
* Secret/redaction behavior.

Never claim that a proposed setting already exists.

If the current extension has no setting contribution for an item, say explicitly:

NOT_IMPLEMENTED_IN_INSTALLED_VERSION

and provide only a proposed design.

7. Chat change lifecycle

Design this fail-closed transaction:

inspect → explain → choose scope → validate → preview → confirm → apply in a separately authorized phase → re-resolve → freeze new context → replan

The current A1E phase stops at design and preview; it must not apply anything.

The Orchestrator must not silently change configuration merely because the user asks a general question.

For a future authorized mutation:

* “How do I change the environment?” provides guidance only.
* “Preview changing the environment to sit for this workspace folder” produces a non-mutating diff and impact report.
* “Apply the preview” still requires an exact confirmation showing key, old value, new value, target scope and affected future tasks.
* Structural policy settings cannot be changed through an ordinary consumer confirmation.
* External-owner settings require the appropriate owner evidence or approval.
* Existing running tasks remain pinned to their old context.

8. Environment example that must be fully designed

Provide both Persian and English dialogue examples for:

1. Showing the active environment.
2. Explaining where it came from.
3. Showing the permitted environment vocabulary.
4. Previewing a task-only change.
5. Previewing a Workspace Folder change.
6. Explaining the difference between dev, sit, pat, prd, prod and prod_c2.
7. Refusing to guess an unresolved alias.
8. Explaining how a maintainer or external owner must ratify a missing token.
9. Showing what the next spawned agent will receive.
10. Explaining that an already-running task will not change.

Important: the current evidence shows divergent environment vocabularies, casing and two-axis CD semantics. Therefore, do not select or normalize prd, prod, prod_c2, sit, pat or aliases unless an authoritative registry/version is proven. Demonstrate the fail-closed chat response.

9. Proposed settings inventory

After inspecting the live extension’s actual contributes.configuration surface and naming conventions, produce a table with:

* Proposed/existing key.
* Display name.
* Description.
* Type.
* Allowed values or schema source.
* Default.
* Scope: application, machine, window/workspace, resource/workspace-folder, language, or task-only.
* User-editable: yes/no.
* Owning authority.
* Secret: yes/no/reference only.
* Restart/reload/replan behavior.
* Ratification state.
* Existing, proposed or prohibited.

Do not hard-code final key names before checking the installed extension namespace.

The design should prefer native VS Code resource-scoped configuration for ordinary operational defaults, while retaining the versioned registry and structural policy outside consumer-controlled settings.

10. Required architecture checks

Explicitly test and report:

* Whether the current Orchestrator or spawned agents read settings independently.
* Whether config is passed to agents today or inferred from ambient state.
* Whether multi-root workspace-folder identity is preserved.
* Whether any child can accidentally inspect another root.
* Whether existing defaults are hard-coded in renderers/planners.
* Whether environment values are duplicated in code, settings, docs or tests.
* Whether an agent can distinguish task override from persisted setting.
* Whether a settings change during execution could produce Preview/Write drift.
* Whether configuration provenance is currently observable.
* Whether current logging could expose secrets.
* Whether proposed settings conflict with unresolved R1–R20 decisions.
* Whether configuration is tied to the context/manifest digest.
* Whether the Orchestrator can tell a user that a requested setting is unsupported in the installed version.

Treat all previous claims, including the A1E input assumptions, as auditable rather than automatically true.

11. Required deliverables

Return, in this order:

1. Repository identity and read-only immutability proof.
2. Inventory of existing VS Code configuration surfaces.
3. Authority classification: user-adjustable, maintainer policy, external owner, secret or computed.
4. Proposed settings schema and scope table.
5. Effective-configuration precedence versus authority-resolution rules.
6. Complete ResolvedEtlAgentContext TypeScript-style interface and JSON example with redacted sample values.
7. Orchestrator-to-child bootstrap, digest and fail-closed protocol.
8. Nested-agent inheritance protocol.
9. Chat intent and response contract.
10. Persian and English environment-change conversations.
11. Preview/confirmation/replan transaction model.
12. Error/result codes, including at least:
    * WORKSPACE_FOLDER_NOT_SELECTED
    * CONFIG_CONTEXT_NOT_RESOLVED
    * CONFIG_CONTEXT_VERSION_UNSUPPORTED
    * CONFIG_CONTEXT_DIGEST_MISMATCH
    * SETTING_NOT_IMPLEMENTED
    * SETTING_NOT_USER_EDITABLE
    * SETTING_VALUE_NOT_RATIFIED
    * AMBIGUOUS_ENVIRONMENT_ALIAS
    * EXTERNAL_OWNER_REQUIRED
    * SECRET_REFERENCE_REQUIRED
    * DISCOVERY_COMPLETENESS_NOT_ATTESTED
    * RUNNING_TASK_CONTEXT_PINNED
    * REPLAN_REQUIRED
13. Acceptance-test matrix, including multi-root isolation, child/nested-agent context parity, settings provenance, unresolved aliases, mid-task setting changes, secrets and Persian help responses.
14. Exact residual product/maintainer/external-owner decisions.
15. A future dependency-ordered implementation plan, clearly labelled NOT AUTHORIZED.
16. End-state immutability proof.

12. Decision boundaries

You may conclude that some operational settings are suitable for VS Code defaults and user overrides.

You must not conclude that putting a value in VS Code settings makes it an authoritative structural contract.

In particular:

* A user may select an environment only from an authoritative versioned vocabulary.
* A user may not decide whether prod equals prd.
* A user may not select a Job/Env repository grammar.
* A user may not invent an include topology.
* A user may not guess a deployment root or provider URI scheme.
* A user may not directly set actual deployed or registration paths.
* A child agent may not override the Orchestrator’s frozen context.
* An ordinary consumer must never be asked to settle an R1–R20 product convention.

End with exactly one of:

* LOCAL_PHASE_A1E_CONFIG_UX_CONTRACT_READY_WITH_RESIDUALS
* LOCAL_PHASE_A1E_CONFIG_UX_CONTRACT_BLOCKED_BY_CONTRADICTION
* LOCAL_PHASE_A1E_CONFIG_UX_CONTRACT_BLOCKED_BY_MISSING_EVIDENCE

This task authorizes read-only inspection and design reporting only. It does not authorize a file, ADR, settings, registry or implementation change.
