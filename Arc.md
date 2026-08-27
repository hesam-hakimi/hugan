TASK: HF1_V2_MIGRATE_AGENT_GOVERNANCE_TO_NATIVE_CLAUDE_HARNESS

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Execution context:

* local VS Code environment;
* Session Target: Claude, the fourth harness option;
* built-in claude agent;
* Claude Opus 5 with Max reasoning;
* current workspace Folder, not a new Git worktree;
* exactly one open workspace root;
* Bypass Permissions may be enabled, but it grants authority only within this
    prompt.

The Agent/Governance Framework was implemented primarily under .github/**.
After VS Code reload, the Claude Agent picker still showed only:

* claude;
* claude-code-guide;
* Explore;
* Plan.

It did not show:

* etl-hotfix-implementer;
* etl-independent-reviewer;
* etl-release-verifier.

Therefore actual Claude Harness activation has failed.

The reported REGISTRY_ACTIVE_AGENT_COUNT: 3 proves only registration in the
custom process manifest. It does not prove discovery by the Claude Agent SDK.

This task must migrate the active Framework customizations to their native Claude
locations, update every authoritative reference, and validate the migrated static
state.

Do not start Repair 13.

Do not certify this migration as runtime-active from the implementation session.
A VS Code reload and a fresh Claude activation check will be required afterward.

==================================================

1. EXPECTED IDENTITY
    ==================================================

Required:

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

Also require:

* exactly one workspace root;
* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* existing 0.3.144 VSIX preserved;
* no concurrent Agent mutation;
* Repair 13 not started.

Prove real execution for cmd.exe, git.exe, node.exe, and npm.cmd or its exact
underlying command.

If inline process capture is defective, use a task-owned helper under the
operating-system temporary directory. Do not modify the repository to repair
execution.

Stop without changes on any mismatch:

CLAUDE_NATIVE_MIGRATION_RESULT: BLOCKED_IDENTITY

or:

CLAUDE_NATIVE_MIGRATION_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

==================================================
2. INDEPENDENT PRE-MIGRATION SNAPSHOT

The repository has a large pre-existing dirty and untracked overlay.

Before editing, capture an independent OS-level and Git snapshot of:

* every tracked-modified path and hash;
* every tracked-deleted path;
* every non-ignored untracked path and hash;
* staged and stash state;
* .github/agents/**;
* .github/skills/**;
* .github/instructions/**;
* .github/prompts/**;
* .github/templates/**;
* .github/agent-governance/**;
* .github/workflows/validate-agent-governance.yml;
* .claude/**, if currently present;
* root CLAUDE.md;
* root AGENTS.md, if present;
* .github/copilot-instructions.md;
* scripts/agent-governance/**;
* package.json;
* src/test/testPatterns.ts;
* all Repair 12 production/test paths;
* all eleven src/**/AGENT.md files;
* protected 0.3.144 VSIX files.

Store all task helpers, snapshots, logs, and backups only in a unique operating-
system temporary directory.

Because the source files may be untracked, preserve their complete pre-migration
bytes in that temporary backup before moving or deleting them.

Do not use the Governance Framework’s own baseline tool as the sole baseline
authority.

==================================================
3. READ AND CLASSIFY BEFORE MOVING

Read completely:

* root CLAUDE.md;
* .github/copilot-instructions.md;
* every .github/agents/*.agent.md;
* every .github/skills/*/SKILL.md and all referenced resources;
* every .github/instructions/**/*.instructions.md;
* every relevant .github/prompts/*.prompt.md;
* every relevant .github/templates/** file;
* .github/agent-governance/process-manifest.json;
* all schemas under .github/agent-governance/schemas/**;
* Governance README and templates;
* all scripts/agent-governance/** implementation and tests.

Use the live process manifest to distinguish:

1. active Governance Agents;
2. active Governance Skills;
3. inactive or legacy assets;
4. prompts and templates that are convenience inputs;
5. machine-authoritative schemas, manifests, and scripts.

Expected active Governance Agents:

* etl-hotfix-implementer;
* etl-independent-reviewer;
* etl-release-verifier.

Expected active Governance Skills:

* etl-hotfix-lifecycle;
* etl-independent-review;
* etl-package-delivery;
* etl-runtime-qa;
* etl-execution-recovery.

If the live manifest does not identify exactly those three active Agents and five
active Skills, stop without migration:

CLAUDE_NATIVE_MIGRATION_RESULT: BLOCKED_ACTIVE_ASSET_AMBIGUITY

Do not activate or migrate legacy Agents merely because they exist, including:

* developer;
* evidence-researcher;
* orchestrator;
* planner;
* verifier;

unless the live manifest independently identifies one as active. Preserve inactive
assets unchanged and retain their explicit inactive classification.

Do not broaden any Agent’s authority.

==================================================
4. REQUIRED NATIVE CLAUDE STRUCTURE

Create the native Claude project structure:

.claude/
agents/
etl-hotfix-implementer.md
etl-independent-reviewer.md
etl-release-verifier.md
skills/
etl-hotfix-lifecycle/
SKILL.md
…
etl-independent-review/
SKILL.md
…
etl-package-delivery/
SKILL.md
…
etl-runtime-qa/
SKILL.md
…
etl-execution-recovery/
SKILL.md
…
rules/
agent-governance.md

Use native Claude conventions:

* Agent files use plain .md, not .agent.md.
* Agent files use Claude-compatible YAML frontmatter.
* Skill directory name exactly matches its name.
* Every SKILL.md has valid Claude-compatible frontmatter.
* All relative references resolve from their new location.
* No absolute developer-machine paths are embedded.
* No source, test, package, QA, Preview, or VSIX authority is broadened.
* No Agent may grant itself approval.
* No Agent may certify work it implemented.
* Independent review must require a separate session.
* Human approval stages remain human-owned.

Do not merely rename files. Translate tool names, frontmatter fields, hooks,
permission modes, skill references, and relative paths into the native Claude
format while preserving the exact intended responsibilities and restrictions.

==================================================
5. MIGRATE THE THREE ACTIVE AGENTS

For each active Agent:

1. Read the complete source .github/agents/*.agent.md.
2. Create its Claude-native equivalent under .claude/agents/*.md.
3. Preserve its:
    * name;
    * description;
    * responsibilities;
    * allowed and disallowed operations;
    * owned lifecycle stages;
    * stop conditions;
    * approval boundaries;
    * mayNotCertify restrictions;
    * required Skills;
    * evidence requirements.
4. Convert VS Code/Copilot tool identifiers to supported Claude tool identifiers.
5. Reject any unknown or silently ignored frontmatter field.
6. Ensure the independent reviewer remains strictly read-only.
7. Ensure the implementer cannot independently certify its own changes.
8. Ensure the release verifier cannot authorize implementation or owner approval.
9. Verify that the three Agents appear as distinct Native Claude definitions.

Expected target paths:

* .claude/agents/etl-hotfix-implementer.md
* .claude/agents/etl-independent-reviewer.md
* .claude/agents/etl-release-verifier.md

Only after semantic parity and target validation succeed may these exact active
source files be removed:

* .github/agents/etl-hotfix-implementer.agent.md
* .github/agents/etl-independent-reviewer.agent.md
* .github/agents/etl-release-verifier.agent.md

Do not remove or modify any other .github/agents file.

If safe source removal cannot be proven, preserve the source and report a duplicate
compatibility blocker. Do not silently maintain two active authorities.

==================================================
6. MIGRATE THE FIVE ACTIVE SKILLS

For each active Governance Skill:

1. Copy the complete Skill directory, including scripts, examples, references,
    templates, and assets, to .claude/skills/<skill-name>/.
2. Validate the target SKILL.md against Claude Agent Skills requirements.
3. Ensure the frontmatter name exactly matches the parent directory.
4. Preserve descriptions and invocation semantics.
5. Convert or remove only fields proven incompatible with Claude.
6. Update every relative link and referenced path.
7. Verify referenced files exist and remain inside the intended repository
    boundary.
8. Confirm the Skill does not silently grant broader tool permission.
9. Confirm all five Skills have unique names and no command collision.

Only after full content, reference, and semantic parity succeeds may the exact
active source Skill directories under .github/skills/ be removed.

Do not move, delete, or activate unrelated inactive Skills.

Do not maintain two independently editable active copies.

==================================================
7. CLAUDE.MD AND NATIVE RULES

Preserve all valid unrelated content in root CLAUDE.md.

Update it minimally so a fresh Claude Harness session receives the required
project-wide Governance entry point.

Use Claude-supported @relative/path imports where they prevent policy
duplication.

The root CLAUDE.md must make these facts explicit:

* the process manifest remains the machine authority;
* Native Claude Agents are under .claude/agents/;
* Native Claude Skills are under .claude/skills/;
* reusable Governance scripts remain under scripts/agent-governance/;
* GitHub Actions workflows remain under .github/workflows/;
* implementation, independent review, release verification, approval, packaging,
    installation, and Runtime QA are separate stages;
* self-certification is forbidden;
* Bypass Permissions does not expand authorized scope;
* all writes require a task-specific boundary and baseline;
* Repair 13 is not authorized by this migration.

Create one concise .claude/rules/agent-governance.md only if required to express
Claude-native always-on rules.

Do not duplicate the entire manifest or long procedures into CLAUDE.md or the rule.
Reference canonical files instead.

Do not move GitHub Actions workflows, schemas, machine manifests, test fixtures,
or shared templates into .claude/. They already belong in their current
functional locations.

==================================================
8. MANIFEST, SCHEMA, AND VALIDATOR PARITY

Update the process manifest so active asset paths point to:

* .claude/agents/**;
* .claude/skills/**.

Update its schema only where required to allow and validate the new canonical
paths.

Update Governance validators and tests so they:

* discover Native Claude Agents;
* discover Native Claude Skills;
* validate Claude frontmatter accurately;
* identify unsupported or silently ignored fields;
* reject duplicate active authority across .github/** and .claude/**;
* keep inactive legacy assets visible with exact reasons;
* verify all Agent-to-Skill references;
* verify stage ownership;
* verify mayNotCertify restrictions;
* verify no Agent declaration exceeds manifest authority;
* verify no Prompt is treated as machine authority;
* verify missing Native Claude assets fail closed.

Do not change the PASS/FINDINGS/BLOCKED model:

* PASS: exit 0;
* FINDINGS: exit 1;
* BLOCKED: exit 2.

Do not weaken checkpoint, baseline, protected-path, registration, self-review, or
CI enforcement implemented in R-A through R-J.

==================================================
9. PROMPTS, TEMPLATES, AND GITHUB-SPECIFIC FILES

Do not blindly move all .github/** content.

Correct placement is based on function:

* .github/workflows/** stays under .github/workflows/**;
* .github/agent-governance/** remains the machine Governance location;
* .github/templates/** remains shared template content;
* .github/prompts/** remains Copilot convenience content unless an exact active
    workflow requires conversion;
* .github/copilot-instructions.md remains the Copilot instruction surface;
* inactive legacy .github/agents/** remain preserved and classified;
* only the three active Governance Agents move to .claude/agents/**;
* only the five active Governance Skills move to .claude/skills/**;
* Claude-specific always-on rules belong in CLAUDE.md or .claude/rules/**.

If a prompt contains unique active Governance rules not present in the manifest,
Skill, CLAUDE.md, or native rule:

* do not copy it blindly;
* move the reusable procedure into the appropriate active Skill;
* keep machine authority in the manifest;
* record exact semantic migration evidence.

No Cloud-critical or Claude-critical rule may remain only in a prompt.

==================================================
10. AUTHORIZED CHANGE BOUNDARY

Authorized additions or modifications:

* .claude/agents/**
* .claude/skills/**
* .claude/rules/**
* root CLAUDE.md
* .github/agent-governance/**
* scripts/agent-governance/**
* .github/workflows/validate-agent-governance.yml
* .github/copilot-instructions.md only for minimal corrected references

Conditionally authorized removals after proven target parity:

* .github/agents/etl-hotfix-implementer.agent.md
* .github/agents/etl-independent-reviewer.agent.md
* .github/agents/etl-release-verifier.agent.md
* only the five exact active Governance Skill directories under .github/skills/

No other path is authorized.

Explicitly prohibited:

* product/runtime source changes;
* Repair 12 content changes;
* Repair 13 implementation;
* src/test/testPatterns.ts changes;
* tsconfig changes;
* package.json or version changes;
* dependency changes;
* package-lock.json creation;
* VSIX build, replacement, installation, or removal;
* QA workspace access;
* Preview or Write execution;
* commit, push, merge, tag, stash, reset, restore, or clean;
* deletion or migration of the eleven src/**/AGENT.md files;
* activation of legacy Agents;
* creation of additional roles beyond the three active Governance Agents.

Any required change outside this boundary is a blocker.

==================================================
11. VALIDATION

Run generated-output validations only in a task-owned temporary mirror.

Required static and dynamic checks:

1. Native Claude Agent frontmatter validation.
2. Native Claude Skill frontmatter validation.
3. Native Agent discovery test.
4. Native Skill discovery test.
5. Manifest and schema validation.
6. Agent/manifest authority parity.
7. Agent-to-Skill reference resolution.
8. Duplicate active-authority rejection.
9. Missing Native Agent fail-closed test.
10. Missing Native Skill fail-closed test.
11. Self-certification negative tests.
12. Checkpoint fidelity tests.
13. Shared baseline contract tests.
14. Three-state result tests.
15. Protected-path and change-boundary tests.
16. Test-registration validator.
17. Governance workflow validation.
18. All Governance unit tests.
19. compile.
20. compile:test.
21. lint.
22. Repair 12 canonical suite, expected 21/21.
23. Canonical full unit suite through the VS Code bootstrap.

Inspect failure identities and fingerprints, not just aggregate counts.

Known F1 and F3 may remain only if their exact fingerprints are unchanged:

* F1: deferred missing Agent/Prompt contract;
* F3: assertion concerning eleven legacy src/**/AGENT.md files.

F2 must continue to pass without weakening its assertion.

Required:

* new functional regressions: 0;
* new security regressions: 0;
* unauthorized changed paths: none;
* active Agents: exactly 3;
* active Skills: exactly 5;
* duplicate active authorities: 0;
* unclassified active assets: 0;
* unowned machine stages: 0;
* manifest/Agent authority parity: yes;
* Native Claude static readiness: yes.

==================================================
12. FINAL CHANGE AND NON-MUTATION PROOF

Compare the final repository against the independent pre-task snapshot.

Report:

* every task-attributable changed path;
* every source-to-target migration;
* every removed source path;
* every preserved legacy asset;
* every unauthorized changed path;
* package.json hash before/after;
* src/test/testPatterns.ts hash before/after;
* tsconfig hash before/after;
* Repair 12 hashes before/after;
* eleven src/**/AGENT.md hashes before/after;
* VSIX size and SHA-256 before/after;
* staged and stash state;
* QA workspace access/write count.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
TEST_PATTERNS_CHANGED: NO
TSCONFIG_CHANGED: NO
REPAIR_12_CONTENT_CHANGED: NO
LEGACY_AGENT_MD_CHANGED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
REPAIR_13_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

==================================================
13. RUNTIME ACTIVATION LIMIT

This implementation session must not claim that the Claude dropdown has already
reloaded the migrated files.

The implementation session may prove only:

* correct Native Claude filesystem placement;
* valid Native Claude formats;
* correct manifest and reference parity;
* passing static and isolated dynamic validation;
* readiness for VS Code reload.

Actual runtime activation requires:

1. Developer: Reload Window;
2. a fresh Claude Harness session;
3. /agents;
4. /skills;
5. /memory;
6. Agent Customizations diagnostics;
7. a separate read-only activation check.

Therefore success in this task means only:

READY_FOR_CLAUDE_RELOAD_AND_ACTIVATION_CHECK: YES

It does not mean:

CLAUDE_RUNTIME_ACTIVATION_PROVEN: YES

==================================================
14. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
PROCESS_EXECUTION_GATE: PASS/FAIL
INDEPENDENT_BASELINE_CAPTURED: YES/NO

ACTIVE_AGENT_SOURCE_COUNT: 
ACTIVE_SKILL_SOURCE_COUNT: 
INACTIVE_LEGACY_ASSETS_PRESERVED: 

NATIVE_CLAUDE_AGENT_COUNT: 
NATIVE_CLAUDE_AGENT_PATHS: 
NATIVE_CLAUDE_SKILL_COUNT: 
NATIVE_CLAUDE_SKILL_PATHS: 
NATIVE_CLAUDE_RULE_PATHS: 

AGENT_SOURCE_TARGET_MAPPING: 
SKILL_SOURCE_TARGET_MAPPING: 
SOURCE_ACTIVE_AGENT_FILES_REMOVED: 
SOURCE_ACTIVE_SKILL_DIRECTORIES_REMOVED: 
SEMANTIC_PARITY_PROVEN: YES/NO
RELATIVE_REFERENCES_VALID: YES/NO
CLAUDE_FRONTMATTER_VALID: YES/NO
CLAUDE_MD_IMPORTS_VALID: YES/NO

MANIFEST_SCHEMA_VALID: YES/NO
MANIFEST_USES_NATIVE_CLAUDE_PATHS: YES/NO
ACTIVE_AGENT_COUNT: 
ACTIVE_SKILL_COUNT: 
DUPLICATE_ACTIVE_AUTHORITY_COUNT: 
UNCLASSIFIED_ACTIVE_ASSET_COUNT: 
UNOWNED_MACHINE_STAGE_COUNT: 
AGENT_MANIFEST_AUTHORITY_PARITY: YES/NO
SELF_CERTIFICATION_PROHIBITION_PRESERVED: YES/NO

GOVERNANCE_TESTS_PASSING: 
GOVERNANCE_TESTS_FAILING: 
COMPILE_PASS: YES/NO
COMPILE_TEST_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_12_CANONICAL_PASS: YES/NO

FULL_UNIT_PASSING: 
FULL_UNIT_PENDING: 
FULL_UNIT_FAILING: 
FULL_UNIT_FAILURES: 
F1_FINGERPRINT_CHANGED: NO
F2_GENUINELY_PASSING: YES/NO
F3_FINGERPRINT_CHANGED: NO
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 

AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
TEST_PATTERNS_CHANGED: NO
TSCONFIG_CHANGED: NO
REPAIR_12_CONTENT_CHANGED: NO
LEGACY_AGENT_MD_CHANGED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
REPAIR_13_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

NATIVE_CLAUDE_STATIC_READINESS: YES/NO
CLAUDE_RUNTIME_ACTIVATION_PROVEN: NO
READY_FOR_CLAUDE_RELOAD_AND_ACTIVATION_CHECK: YES/NO
READY_FOR_REPAIR_13: NO
READY_TO_BUMP_VERSION: NO
READY_TO_PACKAGE_OR_INSTALL: NO
READY_FOR_RUNTIME_QA: NO
READY_FOR_CLOUD_ROLLOUT: NO

Do not perform the post-reload independent activation check in this session.

End exactly with one:

CLAUDE_NATIVE_MIGRATION_RESULT:
PASS_READY_FOR_RELOAD_AND_FRESH_CLAUDE_ACTIVATION_CHECK

CLAUDE_NATIVE_MIGRATION_RESULT:
FAIL_VALIDATION

CLAUDE_NATIVE_MIGRATION_RESULT:
FAIL_UNAUTHORIZED_CHANGE

CLAUDE_NATIVE_MIGRATION_RESULT:
BLOCKED_IDENTITY

CLAUDE_NATIVE_MIGRATION_RESULT:
BLOCKED_EXECUTION_ENVIRONMENT

CLAUDE_NATIVE_MIGRATION_RESULT:
BLOCKED_ACTIVE_ASSET_AMBIGUITY

CLAUDE_NATIVE_MIGRATION_RESULT:
BLOCKED_NATIVE_FORMAT_OR_REFERENCE_MISMATCH
