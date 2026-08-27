TASK: HF1_V2_REPAIR_13_AUTHORITATIVE_ACTIVE_MAPPING_PARITY

Implement Repair 13 using the stabilized native Claude Agent/Governance
Framework.

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Execution context:

* VS Code option 4: Claude harness;
* fresh Chat;
* selected native Agent: etl-hotfix-implementer;
* Claude Opus 5 with Max reasoning;
* Current Folder, not Worktree;
* exactly one effective repository target;
* Local execution only;
* Bypass Permissions may remain enabled, but it grants no authority beyond this
    prompt.

Follow the active native lifecycle Skill referenced by the selected Agent:

.claude/skills/etl-hotfix-lifecycle/SKILL.md

The native governance framework passed independent review with:

NATIVE_CLAUDE_GOVERNANCE_INDEPENDENT_REVIEW_RESULT:
PASS_REPAIR_13_MAY_START_IN_FRESH_CLAUDE_SESSION

This authorizes only the bounded local implementation and validation of
Repair 13.

It does not authorize:

* independent certification by this implementation session;
* version bump;
* packaging;
* VSIX creation or replacement;
* extension installation or uninstallation;
* Runtime QA;
* Preview against a consumer workspace;
* write execution against a consumer workspace;
* commit, push, merge, tag, reset, clean, restore, or stash;
* Cloud rollout;
* governance-framework hardening.

==================================================

1. REPAIR 13 OBJECTIVE
    ==================================================

Repair the divergence between the structured Active Mappings output and the
Markdown Active Mappings output.

The current implementation is suspected to select or project mappings
independently for different output channels, allowing:

* structured and Markdown mapping counts to differ;
* mapping IDs to differ;
* mapping order to differ;
* conflicting mappings to disappear silently from one channel;
* unresolved mappings to retain or acquire machine authority;
* inactive or negative states to be interpreted inconsistently;
* public output or public tool behavior to diverge from internal helpers.

Implement one shared authoritative Active Mapping selector and one shared ordered
projection consumed by every output channel.

Required outcome:

1. structured and Markdown Active Mappings contain exactly the same mapping IDs;
2. IDs appear in exactly the same deterministic order;
3. both channels are derived from one authoritative selected collection;
4. conflicting mappings are excluded from active authority and disclosed
    deterministically;
5. unresolved mappings are excluded and fail closed;
6. inactive mappings do not create blockers merely because they are inactive;
7. no negative-state predicate grants authority;
8. no public machine-authority surface is broadened;
9. all source-declared mapping states are covered explicitly;
10. Repair 12 behavior and the canonical QA STTM remain unchanged.

==================================================
2. REQUIRED IDENTITY

Verify before any edit:

REPOSITORY_ROOT:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

ORIGIN:
https://github.com/TD-Universe/agentic_etl.git

BRANCH:
hotfix/hf1-oracle-fresh-consumer-v2

HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

SOURCE_VERSION:
0.3.144

Required:

* exactly one effective Current Folder repository target;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* Repair 13 has not already started;
* no concurrent Agent is modifying the repository;
* native governance Agents and Skills are present;
* existing protected VSIX artifacts remain unchanged.

Prove executable identity, visible output, and real exit codes for:

* cmd.exe;
* git.exe;
* node.exe;
* npm.cmd or its exact underlying Node command.

The environment has a known process-capture defect:

* child processes may receive a stripped PATH;
* ComSpec may be empty;
* inline stdout capture may incorrectly return no output;
* a harness notification may disagree with the real process exit code.

If encountered, use task-owned helpers only under a unique operating-system
temporary directory and capture stdout, stderr, duration, executable identity,
and real exit code through file redirection.

Do not modify the repository to recover command execution.

Stop without edits on identity mismatch, staged files, ambiguous workspace,
concurrent mutation, or unproven process execution.

Required terminal results include:

REPAIR_13_RESULT: BLOCKED_IDENTITY_MISMATCH
REPAIR_13_RESULT: BLOCKED_STAGED_CHANGES
REPAIR_13_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

==================================================
3. DEFERRED GOVERNANCE FINDINGS

The independent review reported:

G1. .claude/** and CLAUDE.md currently lack Git durability because of existing
ignore behavior.

G2. governance enforcement assets remain untracked.

G3. governance CI has not yet run remotely.

These findings are acknowledged but are outside Repair 13.

Do not fix, stage, commit, delete, move, regenerate, or reconfigure governance
assets in this task.

Do not modify:

* .gitignore;
* .claude/**;
* CLAUDE.md;
* .github/agent-governance/**;
* .github/workflows/validate-agent-governance.yml;
* scripts/agent-governance/**;
* .github/agents/**;
* .github/skills/**;
* .github/prompts/**.

Do not run git clean, git reset, git restore, or any cleanup operation.
Those operations could destroy the untracked governance framework.

The governance findings must be addressed separately after Repair 13’s
independent review and before commit, push, or Cloud rollout.

PROCESS_HARDENING_STARTED must remain NO.

==================================================
4. INDEPENDENT PRE-EDIT BASELINE

The repository contains a large pre-existing dirty and untracked overlay.

Before invoking any task or governance tool, create an independent baseline using
Git plus OS-level file hashing.

Capture:

* git status --porcelain=v2 --untracked-files=all;
* tracked modified, added, deleted, and staged paths;
* all non-ignored untracked paths;
* byte size and SHA-256 for every current working-tree path;
* package.json;
* src/test/testPatterns.ts;
* tsconfig.json;
* all Repair 12 production and test paths;
* all native governance files;
* all eleven src/**/AGENT.md files;
* every .github/prompts/*.prompt.md;
* every existing VSIX;
* the exact Repair 13 candidate source and test paths discovered in Section 5.

Store snapshots, logs, scripts, mirrors, and fixtures only under a unique
operating-system temporary directory.

Do not rely solely on Git because material framework content is untracked.

After the independent baseline exists, the governance capture/checkpoint tools may
also be used for lifecycle enforcement. They do not replace the independent
snapshot.

==================================================
5. DISCOVER THE EXACT LIVE REPAIR SURFACE

Before editing, inspect live source using rg and the repository’s import graph.

Locate every implementation and test path related to:

* Active Mappings;
* structured mapping projection;
* Markdown mapping rendering;
* mapping state or status;
* mapping conflict detection;
* unresolved mapping diagnostics;
* mapping authority or eligibility;
* the public tool/API seam returning the structured result;
* the canonical QA STTM fixture or snapshot;
* Repair 12 mapping fields and behavior;
* canonical test registration.

Search both display strings and identifiers, including reasonable variants of:

* Active Mappings;
* activeMappings;
* mappingState;
* mappingStatus;
* conflict;
* unresolved;
* structured output;
* Markdown output;
* mapping ID ordering.

Construct a pre-edit source-of-truth map:

Concern	Exact source path	Exact symbol	Current consumers
state declaration	value	value	complete list
structured selection	value	value	complete list
Markdown selection	value	value	complete list
ordering	value	value	complete list
conflict diagnostic	value	value	complete list
unresolved diagnostic	value	value	complete list
public seam	value	value	complete list
QA STTM fixture	value	value	complete list
test registry	value	value	complete list

Do not infer file names from this prompt.

Derive them from the live source and import graph.

Before editing, enumerate:

PROPOSED_REPAIR_13_SOURCE_PATHS
PROPOSED_REPAIR_13_TEST_PATHS
PROPOSED_TEST_REGISTRATION_PATH
PROPOSED_QA_REFERENCE_PATHS

The authorized product change boundary is then limited to:

* the smallest existing source files proven to implement the structured and
    Markdown mapping projections;
* at most one existing shared selector/projection module when extracting shared
    logic is necessary;
* the smallest focused test files required to reproduce and validate Repair 13;
* src/test/testPatterns.ts only for one exact, narrow, non-overlapping Repair 13
    test-registration entry.

Do not modify any QA STTM or QA reference input.

Do not modify unrelated product source.

Do not create a general-purpose framework, new public tool, new Agent, new Skill,
new Prompt, new Rule, or new workflow.

If the repair requires a path outside this derived minimal product/test boundary,
stop before editing:

REPAIR_13_RESULT: BLOCKED_CHANGE_BOUNDARY_EXPANSION

If more than one materially different source-of-truth interpretation remains
possible, stop before editing:

REPAIR_13_RESULT: BLOCKED_CONTRACT_AMBIGUITY

==================================================
6. READ AND ENUMERATE THE DECLARED STATE MODEL

Read the actual source declaration of every mapping state.

Return the exact list and ordering before editing.

Do not invent, rename, merge, or remove states merely to simplify the repair.

Build a complete state-projection matrix containing, for every declared state:

* state name;
* whether it may enter Active Mappings;
* whether it appears in structured Active Mappings;
* whether it appears in Markdown Active Mappings;
* whether it emits a finding;
* whether it emits a blocker;
* diagnostic code;
* disclosure channels;
* machine-authority consequence.

Required principles:

* active authority must be granted only by an explicit positive state and all
    required resolution/validity conditions;
* authority must never be inferred from state !== inactive,
    state !== conflict, !invalid, or another negative predicate;
* inactive mappings do not cause blockers solely because they are inactive;
* conflicting mappings never remain active;
* unresolved mappings never remain active;
* unresolved mappings fail closed;
* conflicting or unresolved mappings cannot disappear silently;
* all declared states must be covered explicitly.

If a source-declared state cannot be mapped unambiguously to the required
contract, stop before editing:

REPAIR_13_RESULT: BLOCKED_STATE_MODEL_MISMATCH

==================================================
7. DYNAMIC PRE-FIX REPRODUCTION

Before fixing, reproduce the defect dynamically through the real public seam.

Do not prove it only by calling a private helper.

Create task-owned temporary fixtures covering at minimum:

1. zero mappings;
2. one valid active mapping;
3. multiple valid active mappings;
4. one inactive mapping;
5. mixed active and inactive mappings;
6. one conflicting mapping;
7. duplicate source identity;
8. duplicate target identity;
9. one unresolved mapping;
10. mixed active, conflicting, unresolved, and inactive mappings;
11. input ordering different from canonical output ordering;
12. the canonical QA STTM mapping shape.

Capture independently from the same public invocation:

* structured mapping IDs and order;
* Markdown Active Mappings IDs and order;
* diagnostics;
* status;
* stop code;
* process exit code;
* evidence packet when applicable.

Record:

PRE_FIX_STRUCTURED_MAPPING_COUNT
PRE_FIX_MARKDOWN_MAPPING_COUNT
PRE_FIX_IDS_ONLY_IN_STRUCTURED
PRE_FIX_IDS_ONLY_IN_MARKDOWN
PRE_FIX_CHANNEL_DIVERGENCE_REPRODUCED

A valid reproduction must show the actual defect through the public product seam.

If the channels already agree for all relevant fixtures and the reported defect
cannot be reproduced, do not make a speculative change. Stop:

REPAIR_13_RESULT: BLOCKED_REPRODUCTION_MISMATCH

==================================================
8. IMPLEMENT ONE AUTHORITATIVE SELECTOR

Implement one shared authoritative selector for Active Mappings.

The selector must:

* accept the canonical mapping model;
* evaluate every source-declared state explicitly;
* positively identify mappings eligible for active machine authority;
* reject conflicting mappings from active authority;
* reject unresolved mappings from active authority;
* preserve inactive mappings as non-authoritative without turning inactivity
    alone into a blocker;
* produce deterministic results;
* return or expose the exact ordered selected collection needed by all output
    channels;
* preserve existing valid IDs and data fields;
* avoid mutating the caller’s mappings;
* avoid hidden global state;
* avoid channel-specific re-selection.

Both consumers must use the same selected collection:

1. structured Active Mappings;
2. Markdown Active Mappings.

Neither consumer may independently filter, reclassify, deduplicate, or reorder
the collection.

Required:

POST_FIX_STRUCTURED_MAPPING_COUNT ==
POST_FIX_MARKDOWN_MAPPING_COUNT

POST_FIX_IDS_ONLY_IN_STRUCTURED: NONE
POST_FIX_IDS_ONLY_IN_MARKDOWN: NONE
POST_FIX_CHANNELS_AGREE: YES
POST_FIX_IDS_ORDERED_EQUAL: YES

Do not fix parity by hiding mappings from both channels without preserving the
required diagnostics and state disclosure.

SILENT_CONFLICTING_MAPPING_LOSS must be NO.

==================================================
9. DETERMINISTIC CONFLICT AND UNRESOLVED BEHAVIOR

Conflicting mappings must:

* be excluded from Active Mappings;
* retain sufficient identity for diagnosis;
* emit one deterministic diagnostic through every required disclosure channel;
* never acquire public machine authority;
* never disappear silently.

Unresolved mappings must:

* be excluded from Active Mappings;
* emit a deterministic unresolved-mapping diagnostic;
* fail closed;
* prevent an unsafe successful outcome;
* use the canonical status/stop-code model;
* never be treated as active because a negative predicate happens to pass.

Determine the existing canonical conflict and unresolved diagnostic codes from
the source or established tests.

Reuse existing codes when authoritative.

If no canonical code exists, introduce the narrowest deterministic code required
inside the authorized Repair 13 source boundary and test it completely.

Do not broaden public authority or invent new public operations.

Return:

CONFLICT_DIAGNOSTIC_CODE
CONFLICT_DISCLOSURE_CHANNELS
UNRESOLVED_MAPPING_DIAGNOSTIC_PRESENT
UNRESOLVED_MAPPING_FAILS_CLOSED
INACTIVE_MAPPING_CAUSES_BLOCKER
SILENT_CONFLICTING_MAPPING_LOSS
PUBLIC_MACHINE_AUTHORITY_BROADENED

Expected:

UNRESOLVED_MAPPING_DIAGNOSTIC_PRESENT: YES
UNRESOLVED_MAPPING_FAILS_CLOSED: YES
INACTIVE_MAPPING_CAUSES_BLOCKER: NO
SILENT_CONFLICTING_MAPPING_LOSS: NO
PUBLIC_MACHINE_AUTHORITY_BROADENED: NO

==================================================
10. PUBLIC SEAM AND AUTHORITY CONTAINMENT

Exercise the complete public product seam used by real callers.

Do not validate only:

* an extracted selector;
* a private renderer;
* a private formatter;
* a test-only adapter.

The focused Repair 13 suite must prove that the public seam produces:

* the structured result;
* the Markdown result;
* matching Active Mapping IDs;
* matching deterministic ordering;
* deterministic diagnostics;
* consistent status;
* consistent stop code;
* consistent exit code or tool outcome;
* no authority for conflicting or unresolved mappings.

Do not:

* export a private predicate merely to make testing easier;
* create a new public endpoint or command;
* broaden tool registration;
* add a public setter or bypass;
* convert consumer/display context into machine authority.

Required:

FULL_PUBLIC_SEAM_TESTED: YES
PUBLIC_MACHINE_AUTHORITY_BROADENED: NO

==================================================
11. REPAIR 13 TEST REGISTRATION

Create or update the smallest focused Repair 13 test suite.

The suite must cover every declared state and the full public seam.

Register it through the canonical test registry exactly once.

If a registry change is needed, src/test/testPatterns.ts may receive only one
narrow additive entry that:

* targets the exact freshly compiled Repair 13 suite;
* matches exactly one compiled test file;
* does not overlap any existing pattern;
* does not broaden discovery;
* executes exactly once;
* uses the canonical VS Code test bootstrap.

Do not use ad-hoc Mocha without the repository bootstrap.

Do not add a broad src/test/unit/** pattern.

Required:

REPAIR_13_PATTERN_REGISTERED: YES
REPAIR_13_PATTERN_MATCH_COUNT: 1
REPAIR_13_DUPLICATE_EXECUTION: NO
ALL_DECLARED_STATES_COVERED: YES
FULL_PUBLIC_SEAM_TESTED: YES

If exact single registration cannot be proven, stop:

REPAIR_13_RESULT: FAIL_VALIDATION

==================================================
12. REPAIR 12 PRESERVATION

Repair 13 must not change the established Repair 12 contract.

Identify and snapshot all Repair 12 production and test paths before editing.

Required:

* Repair 12 canonical suite remains 21/21 passing;
* Repair 12 source and expected behavior remain unchanged;
* no Repair 12 test is weakened, skipped, renamed, deleted, or reclassified;
* no Repair 12 output field is silently changed;
* no historical fixture is regenerated.

Return:

REPAIR_12_REGRESSION_PASS: YES
REPAIR_12_CONTENT_CHANGED: NO

==================================================
13. QA STTM PRESERVATION

Locate the canonical repository-side QA STTM reference or fixture used by the
existing tests.

Do not open, modify, or write to the external Development Test Workspace.

Before editing, record from the canonical repository-side reference:

* mapping count;
* exact source literals;
* exact target literals;
* exact filters;
* exact notes;
* byte size;
* SHA-256.

After implementation, prove these values are unchanged.

Return:

QA_STTM_MAPPING_COUNT
QA_STTM_SOURCE_LITERAL_MATCH
QA_STTM_TARGET_LITERAL_MATCH
QA_STTM_FILTERS_EXACT
QA_STTM_NOTES_EXACT
QA_STTM_UNCHANGED

Required:

QA_STTM_SOURCE_LITERAL_MATCH: YES
QA_STTM_TARGET_LITERAL_MATCH: YES
QA_STTM_FILTERS_EXACT: YES
QA_STTM_NOTES_EXACT: YES
QA_STTM_UNCHANGED: YES
QA_WORKSPACE_TOUCHED: NO

If the canonical QA input cannot be identified uniquely, or the observed input
does not match the test contract, stop before editing:

REPAIR_13_RESULT: BLOCKED_QA_INPUT_MISMATCH

==================================================
14. CHANGE BOUNDARY

After the Repair 13 source graph is proven, write the exact authorized path list
before editing.

Only the following categories may appear:

* minimal existing Repair 13 product source paths;
* at most one minimal shared selector/projection module;
* focused Repair 13 test paths;
* src/test/testPatterns.ts only for one exact registration entry.

Everything else is unauthorized.

Explicitly protected:

* .gitignore;
* .claude/**;
* CLAUDE.md;
* .github/**;
* scripts/agent-governance/**;
* package.json;
* package-lock.json;
* tsconfig.json;
* all Repair 12 paths;
* QA STTM/reference content;
* all eleven src/**/AGENT.md files;
* all existing VSIX files;
* unrelated product source;
* Development Test Workspace.

If an unauthorized path changes, stop:

REPAIR_13_RESULT: FAIL_UNAUTHORIZED_CHANGE

Do not normalize, format, or mechanically rewrite unrelated files.

==================================================
15. VALIDATION ENVIRONMENT

Make authorized source edits only in the live repository.

Run compilation, generated-output commands, mutation fixtures, and destructive
negative tests only in a byte-faithful task-owned temporary mirror outside the
repository.

Reuse existing dependencies read-only.

Do not download or install anything.

Do not run:

* npm install;
* npm ci;
* npm version;
* package preparation;
* VSIX build;
* VSIX verification that rewrites artifacts;
* npm test if it downloads VS Code;
* eval or report generators against the live repository;
* Preview against a consumer workspace;
* Runtime QA;
* any real write path.

Require fresh compilation in the temporary mirror; do not trust stale out/**.

==================================================
16. REQUIRED VALIDATION

Run and report exact command, route, duration, stdout/stderr capture method, and
real exit code for:

1. focused pre-fix Repair 13 reproduction;
2. focused post-fix selector tests;
3. all declared-state projection tests;
4. conflict diagnostic tests;
5. unresolved fail-closed tests;
6. inactive-state non-blocking tests;
7. structured/Markdown ID parity tests;
8. structured/Markdown ordered-parity tests;
9. full public seam tests;
10. Repair 13 registration match test;
11. Repair 13 duplicate-execution test;
12. governance tests;
13. customization validator;
14. test-registration validator;
15. manifest/schema validator;
16. compile;
17. compile:test;
18. lint;
19. Repair 13 focused suite through the canonical harness;
20. Repair 12 canonical suite;
21. STTM regression suite;
22. public-tool regression suite;
23. golden-path suite;
24. containment/security suite;
25. trusted-envelope suite;
26. canonical full unit suite using the VS Code bootstrap;
27. independent snapshot → action → compare lifecycle.

Required:

COMPILE_PASS: YES
COMPILE_TEST_PASS: YES
LINT_PASS: YES
REPAIR_13_FOCUSED_PASS: YES
REPAIR_12_REGRESSION_PASS: YES
STTM_REGRESSION_PASS: YES
PUBLIC_TOOL_REGRESSION_PASS: YES
GOLDEN_PATH_PASS: YES
CONTAINMENT_SECURITY_PASS: YES
TRUSTED_ENVELOPE_PASS: YES
SOURCE_COMPILED_PARITY: YES

Governance baseline expected from the completed independent review:

* governance tests: 224 passing, 0 failing;
* customization: blocker 0, major 0, minor 0, informational 8;
* registration enforcing findings: 0;
* Repair 12: 21/21 passing;
* compile, compile:test, lint: exit 0;
* full unit:
    * 2246 passing;
    * 1 pending;
    * 2 failing.

The two known full-suite failures are:

F1:

* pre-existing missing maintainer-delivery Prompt contract;
* expected missing path includes:
    .github/prompts/deploy-v3-agent-tool-context-gap.prompt.md;
* do not create a Prompt or Agent to make it pass;
* fingerprint must remain unchanged.

F3:

* pre-existing assertion concerning eleven src/**/AGENT.md files;
* do not delete, rename, migrate, or rewrite them;
* fingerprint must remain unchanged.

F2 must remain genuinely passing and must not be weakened, skipped, deleted, or
reclassified.

The single pending suite is:

KnowledgeAdvisor Integration Tests

Compare full-suite failures by exact identity and fingerprint, not only aggregate
counts.

Required:

FULL_UNIT_FAILURE_IDENTITIES_UNCHANGED: YES
NEW_FUNCTIONAL_REGRESSIONS: 0
NEW_SECURITY_REGRESSIONS: 0

==================================================
17. FINAL INDEPENDENT CHANGE COMPARISON

Use the independent OS-hash baseline—not only Git and not only the governance
tools—to compare final live state.

Report:

* every task-attributable changed path;
* every preserved pre-existing dirty path;
* every unauthorized changed path;
* staged paths;
* stash state;
* package.json hash before/after;
* package version before/after;
* package-lock.json presence;
* src/test/testPatterns.ts exact delta or unchanged reason;
* tsconfig.json hash before/after;
* all Repair 12 hashes before/after;
* QA reference hashes before/after;
* all eleven legacy AGENT.md hashes before/after;
* all governance hashes before/after;
* every protected VSIX size and SHA-256 before/after;
* QA workspace access/write count;
* HEAD before/after.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
STAGED_FILES: 0
PACKAGE_JSON_CHANGED_FIELDS: NONE
PACKAGE_VERSION_CHANGED: NO
DEPENDENCIES_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
EXISTING_0_3_144_VSIX_MODIFIED: NO
GITHUB_CUSTOMIZATION_MODIFIED: NO
REVIEW_INDUCED_BASELINE_FILES_PRESERVED: YES
QA_WORKSPACE_TOUCHED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
PROCESS_HARDENING_STARTED: NO

==================================================
18. INDEPENDENCE AND NEXT-LIFECYCLE GATE

This implementation session may:

* reproduce Repair 13;
* implement the bounded fix;
* run validations;
* emit an implementation checkpoint;
* report readiness for independent review.

It may not:

* act as the independent reviewer;
* certify its own source changes;
* authorize version 0.3.145;
* package or install the extension;
* start Runtime QA;
* approve Preview or Write;
* commit or push;
* fix G1, G2, or G3;
* claim Cloud readiness.

After implementation, an independent review must occur in a separate fresh
session using etl-independent-reviewer, provided that reviewer does not certify
changes to its own governance definition or authority.

Required:

IMPLEMENTATION_SESSION_INDEPENDENT_REVIEW_PERFORMED: NO
READY_FOR_GENUINELY_INDEPENDENT_REVIEW: YES
NEXT_VERSION_IF_INDEPENDENT_REVIEW_PASSES: 0.3.145
READY_TO_BUMP_VERSION: NO
READY_TO_PACKAGE: NO
READY_TO_INSTALL: NO

==================================================
19. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_PREFLIGHT: PASS/FAIL
INDEPENDENT_BASELINE_CAPTURED: YES/NO

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD_BEFORE: 
HEAD_AFTER: 
SOURCE_VERSION: 
WORKSPACE_TARGET_COUNT: 
STAGED_FILES: 
STASH_ENTRIES: 

DECLARED_MAPPING_STATES: 
STRUCTURED_SELECTION_SOURCE_BEFORE: 
MARKDOWN_SELECTION_SOURCE_BEFORE: 
SHARED_SELECTION_SOURCE_AFTER: 
STRUCTURED_SELECTION_SOURCE_AFTER: 
MARKDOWN_SELECTION_SOURCE_AFTER: 

PRE_FIX_STRUCTURED_MAPPING_COUNT: 
PRE_FIX_MARKDOWN_MAPPING_COUNT: 
PRE_FIX_IDS_ONLY_IN_STRUCTURED: 
PRE_FIX_IDS_ONLY_IN_MARKDOWN: 
PRE_FIX_CHANNEL_DIVERGENCE_REPRODUCED: YES/NO

POST_FIX_STRUCTURED_MAPPING_COUNT: 
POST_FIX_MARKDOWN_MAPPING_COUNT: 
POST_FIX_IDS_ONLY_IN_STRUCTURED: 
POST_FIX_IDS_ONLY_IN_MARKDOWN: 
POST_FIX_CHANNELS_AGREE: YES/NO
POST_FIX_IDS_ORDERED_EQUAL: YES/NO

STATE_PROJECTION_MATRIX: 
CONFLICT_DIAGNOSTIC_CODE: 
CONFLICT_DISCLOSURE_CHANNELS: 
UNRESOLVED_MAPPING_DIAGNOSTIC_PRESENT: YES/NO
UNRESOLVED_MAPPING_FAILS_CLOSED: YES/NO
INACTIVE_MAPPING_CAUSES_BLOCKER: YES/NO
SILENT_CONFLICTING_MAPPING_LOSS: YES/NO
PUBLIC_MACHINE_AUTHORITY_BROADENED: YES/NO

REPAIR_13_PATTERN_REGISTERED: YES/NO
REPAIR_13_PATTERN_MATCH_COUNT: 
REPAIR_13_DUPLICATE_EXECUTION: YES/NO
ALL_DECLARED_STATES_COVERED: YES/NO
FULL_PUBLIC_SEAM_TESTED: YES/NO

QA_STTM_MAPPING_COUNT: 
QA_STTM_SOURCE_LITERAL_MATCH: YES/NO
QA_STTM_TARGET_LITERAL_MATCH: YES/NO
QA_STTM_FILTERS_EXACT: YES/NO
QA_STTM_NOTES_EXACT: YES/NO
QA_STTM_UNCHANGED: YES/NO

AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
PACKAGE_JSON_CHANGED_FIELDS: 
PACKAGE_VERSION_CHANGED: NO
DEPENDENCIES_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
EXISTING_0_3_144_VSIX_MODIFIED: NO
GITHUB_CUSTOMIZATION_MODIFIED: NO
REVIEW_INDUCED_BASELINE_FILES_PRESERVED: YES/NO

COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_13_FOCUSED_PASS: YES/NO
REPAIR_12_REGRESSION_PASS: YES/NO
STTM_REGRESSION_PASS: YES/NO
PUBLIC_TOOL_REGRESSION_PASS: YES/NO
GOLDEN_PATH_PASS: YES/NO
CONTAINMENT_SECURITY_PASS: YES/NO
TRUSTED_ENVELOPE_PASS: YES/NO
SOURCE_COMPILED_PARITY: YES/NO

FULL_UNIT_PASSING_COUNT_BEFORE: 
FULL_UNIT_PASSING_COUNT_AFTER: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURES: 
FULL_UNIT_FAILURE_IDENTITIES_UNCHANGED: YES/NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

VSIX_BUILT: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO
PROCESS_HARDENING_STARTED: NO

IMPLEMENTATION_SESSION_INDEPENDENT_REVIEW_PERFORMED: NO
READY_FOR_GENUINELY_INDEPENDENT_REVIEW: YES/NO
NEXT_VERSION_IF_INDEPENDENT_REVIEW_PASSES: 0.3.145
READY_TO_BUMP_VERSION: NO
READY_TO_PACKAGE: NO
READY_TO_INSTALL: NO

PASS requires:

* exact identity and executable preflight;
* independent pre-edit baseline;
* dynamic pre-fix reproduction through the public seam;
* every source-declared state covered explicitly;
* one shared authoritative selector;
* exact structured/Markdown Active Mappings ID parity;
* exact structured/Markdown Active Mappings order parity;
* conflicting and unresolved mappings excluded from active authority;
* deterministic conflict and unresolved diagnostics;
* fail-closed unresolved behavior;
* inactive state not treated as a blocker merely for being inactive;
* no negative-state authority predicate;
* no public machine-authority broadening;
* full public seam exercised;
* Repair 12 behavior preserved;
* QA STTM preserved exactly;
* Repair 13 suite registered exactly once;
* zero new functional or security regressions;
* zero unauthorized path, package, version, VSIX, installation, QA, Git,
    Preview, process-hardening, or runtime-write mutation;
* implementation session does not self-certify.

End exactly with one:

REPAIR_13_RESULT: PASS_READY_FOR_GENUINELY_INDEPENDENT_REVIEW

REPAIR_13_RESULT: FAIL_VALIDATION

REPAIR_13_RESULT: FAIL_AUTHORITY_BROADENING

REPAIR_13_RESULT: FAIL_UNAUTHORIZED_CHANGE

REPAIR_13_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

REPAIR_13_RESULT: BLOCKED_IDENTITY_MISMATCH

REPAIR_13_RESULT: BLOCKED_STAGED_CHANGES

REPAIR_13_RESULT: BLOCKED_QA_INPUT_MISMATCH

REPAIR_13_RESULT: BLOCKED_STATE_MODEL_MISMATCH

REPAIR_13_RESULT: BLOCKED_CONTRACT_AMBIGUITY

REPAIR_13_RESULT: BLOCKED_REPRODUCTION_MISMATCH

REPAIR_13_RESULT: BLOCKED_CHANGE_BOUNDARY_EXPANSION
