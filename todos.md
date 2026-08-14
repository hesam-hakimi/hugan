TASK: LOCAL_PHASE_A1E — ENGLISH-FIRST VS CODE CONFIGURATION, FROZEN ORCHESTRATOR CONTEXT, AND CHAT-GUIDANCE CONTRACT

MODE: STRICTLY READ-ONLY, DESIGN-ONLY

1. Product-language invariant

This product is being built for English-speaking users.

All product-facing material must be English, including:

* VS Code setting titles and descriptions
* command names and descriptions
* ETL Orchestrator responses
* child-agent instructions and outputs
* validation and error messages
* documentation and examples
* tests and fixtures
* code identifiers and comments

Do not infer product language from the language used by the operator who submitted this task.

Do not add Persian, bilingual output, locale switching, or a configurable product-language setting. Localization is outside this task and would require separate explicit authorization.

2. Authoritative starting state

The immediately preceding phase ended with:

LOCAL_PHASE_A1D_OWNER_DECISIONS_PARTIAL

The following scope-limited principles were ratified only for design articulation:

1. Semantically different path fields must remain separate; they must not be collapsed into one ambiguous path.
2. The deployment-projection interface may accept an externally supplied, typed deployment root. The root must not be guessed.
3. An evidence classifier may be expressed as a generic injected-registry design, together with a typed result/error/provenance algebra.

These ratifications:

* do not ratify any concrete Job Config grammar;
* do not ratify any Environment Config grammar;
* do not ratify an environment vocabulary, alias table, filename sanitizer, extension, deployment-root representation, projection version, or registry contents;
* do not prohibit behavior merely because no authoritative producer was found;
* do not authorize removing existing standalone .sql behavior;
* do not make existing include resolvers authoritative;
* do not authorize an ADR write;
* do not authorize Slice 2, S1, S2, S3, scaffolding, production edits, or implementation.

Every detail decision R1–R20 remains unresolved unless live authoritative evidence proves that it is not actually a product decision.

Configuration must not be used to silently ratify any unresolved structural convention.

3. Change-surface restrictions

Operate read-only.

Allowed:

* inspect repository and workspace files;
* use read-only search and Git inspection commands;
* inspect package.json, extension manifests, configuration declarations, source, tests, and documentation;
* inspect the live pending diff without accepting or modifying it;
* report findings in chat.

Forbidden:

* creating, editing, deleting, renaming, formatting, or saving files;
* writing an ADR;
* staging, committing, pushing, rebasing, resetting, checking out, stashing, cleaning, or switching branches/worktrees;
* clicking Keep, Undo, Revert, Discard, Delete, Clean, Restore, or equivalent actions;
* building, testing, packaging, installing, uninstalling, or replacing the VSIX;
* writing to consumer workspaces or external systems;
* implementing or scaffolding any slice.

All pending/Keep changes and all dirty or untracked files are user-owned and must remain untouched.

Capture start and end repository identity, status, pending-file inventory, and protected hashes. Reconcile the known 15-entry / 16-file / 17-hash distinction rather than describing them as one count.

4. Objective

Design—without implementing—the contract by which:

1. appropriate operational defaults can be configured through VS Code settings;
2. users can override appropriate values at User, Remote, Workspace, Workspace Folder, or task/session scope;
3. the ETL Orchestrator resolves and validates the effective configuration;
4. every spawned or nested agent receives the same frozen, readable context;
5. agents do not independently infer or reread mutable configuration;
6. users can ask the ETL Orchestrator, in English, how to inspect or change an operational setting such as the target environment;
7. structural Framework decisions, external platform contracts, secrets, and computed values are not misrepresented as ordinary user settings.

This phase must decide only the configuration/context/chat architecture. It must not select unresolved ETL layout grammars or platform values.

5. Mandatory live inventory

Inspect and cite the live repository implementation for:

* the existing VS Code configuration namespace;
* contributes.configuration declarations;
* commands and command-palette surfaces;
* every call to workspace.getConfiguration, inspect, get, or update;
* User, Remote, Workspace, and Workspace Folder handling;
* multi-root workspace selection;
* ETL Orchestrator bootstrap and task planning;
* agent creation, child-agent creation, and prompt/context construction;
* environment-selection code;
* deployment settings and package metadata;
* profile/layout/config readers;
* secret and credential handling;
* generated context resources available to agents;
* user help, errors, and chat guidance;
* relevant tests and documentation.

Do not invent a permanent setting namespace or key before inspecting the existing namespace and conventions.

For every existing or proposed setting, report its current status as one of:

* EXISTING_AND_ENFORCED
* EXISTING_BUT_PARTIAL
* EXISTING_BUT_UNUSED
* PROPOSED_PENDING_RATIFICATION
* NOT_APPROPRIATE_AS_A_SETTING

6. Configuration classification

Classify every candidate value into exactly one authority class:

A. User-adjustable operational input

A user may configure or override it without choosing a Framework structural convention.

Potential examples to evaluate, not automatically approve:

* default target environment for future tasks;
* explicit target environment for the current task;
* selected consumer workspace root;
* selected evidence scope;
* an already-ratified layout/deployment profile ID;
* preview or confirmation preferences that do not weaken safety.

B. Maintainer-owned structural policy

Examples include:

* Job and Environment Config grammars;
* filename sanitizers;
* profile definitions;
* include topology;
* fallback grammar;
* artifact-family rules;
* evidence precedence;
* migration behavior.

These must not become ordinary user-editable settings merely to avoid a maintainer decision.

C. External CD/platform-owner contract

Examples include:

* deployment-root components;
* environment vocabulary and casing;
* version-segment semantics;
* canonical DBFS/URI representation;
* publisher receipt and partial-failure semantics.

Expose these only through a ratified external profile/contract. Do not ask an ordinary extension consumer to invent them.

D. Secret or credential

Never store or echo secret values in ordinary VS Code settings, prompts, logs, provenance, or child-agent context. Pass only references to an approved secret provider.

E. Computed/read-only state

Examples include:

* repository-relative paths;
* resolved include targets;
* projected or actual deployed paths;
* registration paths;
* discovery results;
* context digests and provenance.

These may be displayed but must not be editable as ordinary settings.

Produce a classification matrix with authority, owner, scope, sensitivity, mutability, and rationale.

7. Target-environment configuration contract

Explicitly design how a user can configure a default target environment in VS Code and override it for a task, while preserving these constraints:

* Do not hard-code or invent dev, sit, pat, prd, prod, prod_c2, aliases, casing, or a default environment.
* Allowed environment IDs must come from a versioned recognized-profile registry or an authoritative external platform contract.
* A configured value not present in the applicable registry must fail closed with an English diagnostic.
* Distinguish a persistent VS Code default from an explicit task/session override.
* A session override must not silently persist.
* A persistent update must require explicit user confirmation and must target the intended VS Code scope.
* A setting change during an active task must not mutate that task’s frozen context. It applies to a new plan or an explicitly confirmed re-plan.
* In a multi-root workspace, the selected Workspace Folder and evidence scope must be explicit.

Derive the real precedence and provenance behavior from the VS Code configuration APIs and the live extension. Do not assume precedence without checking it.

8. Proposed settings contract

After inventorying the existing namespace, propose exact candidate setting keys in English.

For each proposed key specify:

* key;
* English title and description;
* type;
* authority class;
* valid scopes;
* default source;
* allowed-values source;
* validation;
* sensitivity;
* whether agents may receive it;
* whether it is persisted or task-local;
* effect of changing it;
* whether restart, re-plan, or neither is required;
* error code when missing or invalid;
* associated unresolved R1–R20 decision, if any.

Do not give unresolved structural settings a synthetic default.

When no value is authoritative, use a typed blocked state rather than guessing.

9. Frozen orchestrator context

Design a serializable ResolvedEtlAgentContext or equivalently named contract containing at least:

* contextSchemaVersion
* policyVersion
* profileRegistryVersion
* productLanguage: "en"
* task/session identity
* explicitly selected workspace-folder URI
* realpath-resolved evidence scope
* artifact family
* applicable layout-profile identity, if ratified
* applicable deployment-profile identity, if ratified
* effective non-secret operational settings
* value provenance and VS Code scope for every effective setting
* target-environment selection and vocabulary/profile version
* secret references without secret values
* discovery-completeness attestation
* unresolved decisions and blockers
* selected projection version, when authorized
* canonical context digest

A single global layoutProfileId must not be assumed sufficient. Evaluate profile identity scoped by at least (artifactFamily, evidenceScope) plus a cross-family topology-consistency result.

Git status must not determine whether valid consumer evidence qualifies. A valid file may be committed, modified, untracked, ignored, or in a non-Git consumer workspace, subject to explicit scope, parsing, exclusion, and completeness rules.

10. Orchestrator and child-agent protocol

Design the following protocol:

1. The ETL Orchestrator is the sole resolver of effective configuration for a task.
2. It reads the selected VS Code configuration scopes at the planning boundary.
3. It validates authority, registry version, allowed values, scope, and completeness.
4. It fails closed before spawning agents if required values are invalid or unresolved.
5. It canonicalizes and freezes the resolved context.
6. It computes a digest over a specified canonical serialization.
7. It sends the complete non-secret AgentBootstrapEnvelope to every child agent.
8. Every child validates the schema version, policy/profile versions, and digest before doing work.
9. Every nested child inherits the exact same frozen context and digest.
10. Children must not reread VS Code settings, CWD, ambient workspace folders, process environment, examples, fixtures, or another agent’s output to reconstruct configuration.
11. Children return the context digest in their result envelope.
12. A changed setting requires a new context version and explicit re-plan; it never mutates an active task invisibly.
13. The ETL Orchestrator remains aware of every effective value, source, override, unresolved blocker, and child acknowledgement.
14. No child relies on inaccessible parent-chat history for required instructions.

Define failure behavior for missing, stale, mismatched, or tampered context.

11. ETL Orchestrator chat-guidance contract

Design an English-only user-help capability for intents including:

* “Show my effective ETL settings.”
* “Why is this value being used?”
* “What can I change?”
* “How do I change the target environment?”
* “Change the environment for this task only.”
* “How do I persist this environment for this workspace?”
* “Which setting scope currently wins?”
* “Will this change affect the running task?”
* “Why is this operation blocked?”

For an editable setting, the response must state:

1. current effective value;
2. source and scope;
3. allowed values and their authoritative source;
4. exact setting key;
5. the correct VS Code UI route;
6. a valid settings.json example;
7. whether the change is task-local or persistent;
8. validation and safety impact;
9. whether a re-plan or restart is required;
10. how to verify the resulting effective value.

For a non-editable value, it must say why it is:

* maintainer-owned;
* externally owned;
* secret;
* computed/read-only; or
* blocked pending ratification.

It must not invent a setting key or advise the user to edit raw generated files.

A chat request may create a task-local override only after explicit confirmation. Persistent settings must not be changed silently.

Provide complete English examples for:

* inspecting the current environment;
* changing it for one task;
* changing the Workspace Folder default;
* entering an invalid environment;
* requesting a structural grammar change;
* requesting a secret value;
* changing a setting while agents are running.

12. Existing technical constraints to verify

Independently verify these against live code and authoritative dependencies. Treat them as audit hypotheses, not automatic truth:

* nested HOCON includes use parent-relative resolution;
* Job and Environment layouts are jointly constrained by include topology;
* current include resolvers may be base-blind or family-blind;
* planned deployment paths differ from actual publisher-receipt paths;
* registration must be derived from successful actual deployment;
* partial publish must not produce registration;
* provider URI/DBFS canonicalization differs from host filesystem normalization;
* discovery completeness must be an explicit attested input;
* sibling roots in a multi-root workspace must not contaminate evidence;
* onboarding may require a separate artifact family;
* absence of a producer is not automatically a prohibition;
* current standalone .sql creation must not be silently removed;
* existing projection code may already mirror repository-relative paths in some flows.

Cite exact live files and lines for every confirmed or rejected hypothesis.

13. Acceptance invariants

Define testable, implementation-independent invariants covering:

* deterministic effective-setting resolution;
* correct VS Code scope provenance;
* multi-root isolation;
* explicit Workspace Folder selection;
* invalid environment fail-closed behavior;
* no invented aliases or defaults;
* versioned profile-registry mismatch;
* explicit discovery-completeness attestation;
* identical parent/child/nested-child context digest;
* no child settings reread;
* active-task context immutability;
* explicit re-plan after a setting change;
* secret non-exposure;
* English-only product output;
* chat guidance for editable settings;
* refusal to expose structural policy as an ordinary setting;
* provider-specific path canonicalization;
* projected-versus-actual deployment separation;
* no registration after partial publish;
* preservation of pending/Keep changes.

14. Required report

Return a single, self-contained report in chat with:

1. repository identity and immutability proof;
2. live configuration and orchestration inventory;
3. authority-classification matrix;
4. existing/proposed settings contract;
5. exact ResolvedEtlAgentContext schema;
6. exact AgentBootstrapEnvelope and result-envelope design;
7. context-resolution and propagation sequence;
8. ETL Orchestrator chat-guidance contract;
9. complete English chat examples;
10. multi-root, secret, and trust-boundary analysis;
11. acceptance-invariant matrix;
12. mapping to unresolved R1–R20 decisions;
13. smallest dependency-ordered future implementation slices, each marked NOT_AUTHORIZED;
14. a final verdict distinguishing:

* designable now;
* requires maintainer ratification;
* requires external CD/platform-owner evidence;
* blocked;
* implementation not authorized.

Do not convert this report into an ADR and do not implement it.

End with exactly one status token:

* LOCAL_PHASE_A1E_CONFIG_CONTEXT_CHAT_CONTRACT_PASS
* LOCAL_PHASE_A1E_CONFIG_CONTEXT_CHAT_CONTRACT_PASS_WITH_RESIDUALS
* LOCAL_PHASE_A1E_CONFIG_CONTEXT_CHAT_CONTRACT_BLOCKED
