TASK: HF1_V2_COMPLETE_NATIVE_CLAUDE_REFERENCE_MIGRATION

Work only inside:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Use the current folder in a generic Claude Agent session.

This is a narrowly bounded follow-up to:

TASK: HF1_V2_MIGRATE_AGENT_GOVERNANCE_TO_NATIVE_CLAUDE_HARNESS

The preceding migration correctly created and validated:

* 3 native Agents under .claude/agents/**;
* 5 native Skills under .claude/skills/**;
* .claude/rules/agent-governance.md;
* the CLAUDE.md import;
* native manifest and governance-validator support.

It stopped with:

BLOCKED_NATIVE_FORMAT_OR_REFERENCE_MISMATCH

The exact remaining defect is six dangling Skill references in five existing
.github/prompts/*.prompt.md files after the active Skills were migrated from
.github/skills/** to .claude/skills/**.

This task is authorized to repair only those six references and to validate the
completed migration.

Do not perform Repair 13.
Do not change product/runtime source.
Do not change package.json or its version.
Do not create package-lock.json.
Do not build, replace, install, or uninstall a VSIX.
Do not start Runtime QA.
Do not access the QA workspace.
Do not commit, push, merge, tag, stash, reset, clean, or restore.
Do not create additional Agents, Skills, Prompts, or Rules.
Do not reintroduce duplicate active authority under .github/agents/** or
.github/skills/**.

==================================================

1. IDENTITY AND CURRENT-STATE GATE
    ==================================================

Verify:

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

* staged files: 0;
* stash entries: 0;
* package-lock.json absent;
* exactly one effective current-folder repository target;
* the prior Claude-native migration content is still present;
* no concurrent Agent is modifying the repository.

Confirm the presence of exactly these native Agents:

* .claude/agents/etl-hotfix-implementer.md
* .claude/agents/etl-independent-reviewer.md
* .claude/agents/etl-release-verifier.md

Confirm the presence of exactly these active native Skills:

* .claude/skills/etl-hotfix-lifecycle/SKILL.md
* .claude/skills/etl-independent-review/SKILL.md
* .claude/skills/etl-package-delivery/SKILL.md
* .claude/skills/etl-runtime-qa/SKILL.md
* .claude/skills/etl-execution-recovery/SKILL.md

Confirm:

* .claude/rules/agent-governance.md exists;
* CLAUDE.md imports that Rule;
* the process manifest identifies the .claude/** assets as the active authority;
* the old three active .github/agents/** sources and old five active
    .github/skills/** sources are not simultaneously active.

Stop without edits if identity differs or the native migration is incomplete.

==================================================
2. INDEPENDENT PRE-EDIT SNAPSHOT

Before editing, record path, size, and SHA-256 for:

* all .claude/** files;
* all .github/prompts/*.prompt.md files;
* .github/copilot-instructions.md;
* .github/agent-governance/**;
* scripts/agent-governance/**;
* CLAUDE.md;
* package.json;
* src/test/testPatterns.ts;
* tsconfig.json;
* Repair 12 production and test paths;
* all eleven src/**/AGENT.md files;
* every existing VSIX.

Store temporary snapshots and logs outside the repository.

Do not use the repository’s own governance baseline as the sole authority.

==================================================
3. EXACT AUTHORIZED EDITS

Only these five files may be modified:

1. .github/prompts/build.prompt.md
2. .github/prompts/investigate.prompt.md
3. .github/prompts/plan-change.prompt.md
4. .github/prompts/verify-change.prompt.md
5. .github/prompts/verify-live-flow.prompt.md

Make only these semantic reference replacements:

File	Replace old active Skill reference with
.github/prompts/build.prompt.md	.claude/skills/etl-hotfix-lifecycle/SKILL.md
.github/prompts/investigate.prompt.md	.claude/skills/etl-execution-recovery/SKILL.md
.github/prompts/plan-change.prompt.md	.claude/skills/etl-hotfix-lifecycle/SKILL.md
.github/prompts/verify-change.prompt.md	.claude/skills/etl-independent-review/SKILL.md
.github/prompts/verify-live-flow.prompt.md	.claude/skills/etl-runtime-qa/SKILL.md and .claude/skills/etl-package-delivery/SKILL.md

There must be exactly six repaired references across those five files.

Preserve:

* Prompt frontmatter;
* Prompt names and descriptions;
* all behavioral instructions;
* workflow semantics;
* review and approval boundaries;
* no-self-certification rules;
* packaging, installation, Runtime QA, Preview, and write gates;
* all unrelated whitespace and content where practical.

Do not make these Prompts a second policy authority. They remain convenience
entry points referencing the canonical native Skills.

Do not add fallback references to the removed .github/skills/** sources.

==================================================
4. REFERENCE-INTEGRITY VALIDATION

After editing, scan all repository governance and customization assets for
references to the removed active sources.

At minimum inspect:

* .github/**/*.md;
* .github/**/*.json;
* .github/**/*.yml;
* .github/**/*.yaml;
* .claude/**/*.md;
* CLAUDE.md;
* scripts/agent-governance/**.

Required:

* dangling references to removed active .github/skills/etl-*: 0;
* dangling references to removed active .github/agents/etl-*: 0;
* references to active native Agents resolve: 3/3;
* references to active native Skills resolve: 5/5;
* the six repaired Prompt references resolve: 6/6;
* duplicate active authority: 0;
* unclassified active assets: 0;
* missing referenced files: 0.

Historical prose that intentionally documents the prior location may remain only
when explicitly marked as historical and when no loader or validator interprets
it as an active reference.

Do not suppress or weaken reference validation.

==================================================
5. VALIDATION

Run all write-producing validation in a task-owned temporary mirror when
necessary.

Run:

1. native Agent frontmatter validation;
2. native Skill frontmatter validation;
3. native Agent discovery tests;
4. native Skill discovery tests;
5. Agent-to-Skill resolution tests;
6. manifest/schema validation;
7. Agent/manifest authority parity validation;
8. duplicate-authority validation;
9. missing-Agent and missing-Skill fail-closed tests;
10. self-certification negative tests;
11. checkpoint-fidelity tests;
12. baseline-contract tests;
13. change-boundary adversarial tests;
14. test-registration validation;
15. workflow validation;
16. complete governance test suite;
17. customization validation;
18. compile;
19. compile:test;
20. lint;
21. Repair 12 canonical suite;
22. canonical full unit suite.

Expected minimum results based on the preceding run:

* Governance tests: at least 224 passing, 0 failing;
* customization blocker findings: 0;
* customization major findings caused by dangling references: 0;
* inactive informational asset records may remain: 8;
* registration enforcement findings: 0;
* Repair 12: 21/21 passing;
* compile: exit 0;
* compile:test: exit 0;
* lint: exit 0;
* no new functional regression;
* no new security regression.

Reconcile full-suite failures by exact identity.

The known deferred failures may remain only if unchanged:

* F1: missing/stale maintainer-delivery Prompt contract;
* F3: assertion concerning the eleven existing src/**/AGENT.md files.

F2 must remain genuinely passing without weakening, skipping, or deleting its
assertion.

Do not create missing Agents or Prompts merely to make F1 pass.
Do not change or delete the eleven legacy AGENT.md files to make F3 pass.

==================================================
6. NON-MUTATION AND CHANGE-BOUNDARY PROOF

Compare the final live repository with the independent pre-edit snapshot.

Required task-attributable changes:

* exactly five modified Prompt files;
* exactly six reference replacements;
* no other task-attributable change.

Required:

UNAUTHORIZED_CHANGED_PATHS: NONE
PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
TEST_PATTERNS_CHANGED: NO
TSCONFIG_CHANGED: NO
REPAIR_12_CONTENT_CHANGED: NO
LEGACY_AGENT_MD_CHANGED: NO
NATIVE_AGENT_CONTENT_CHANGED: NO
NATIVE_SKILL_CONTENT_CHANGED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
REPAIR_13_STARTED: NO
STAGED_FILES: 0
COMMIT_CREATED: NO
PUSH_EXECUTED: NO

If another change is required, stop and report it. Do not broaden the boundary.

==================================================
7. FINAL REPORT

Return:

IDENTITY_GATE: PASS/FAIL
NATIVE_MIGRATION_PRESENT: YES/NO
INDEPENDENT_BASELINE_CAPTURED: YES/NO

AUTHORIZED_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
PROMPT_FILES_MODIFIED_COUNT: 
SKILL_REFERENCES_REPAIRED_COUNT: 

BUILD_PROMPT_REFERENCE_VALID: YES/NO
INVESTIGATE_PROMPT_REFERENCE_VALID: YES/NO
PLAN_CHANGE_PROMPT_REFERENCE_VALID: YES/NO
VERIFY_CHANGE_PROMPT_REFERENCE_VALID: YES/NO
VERIFY_LIVE_FLOW_REFERENCES_VALID: YES/NO

DANGLING_REMOVED_SKILL_REFERENCES: 
DANGLING_REMOVED_AGENT_REFERENCES: 
ACTIVE_NATIVE_AGENT_COUNT: 
ACTIVE_NATIVE_SKILL_COUNT: 
DUPLICATE_ACTIVE_AUTHORITY_COUNT: 
UNCLASSIFIED_ACTIVE_ASSET_COUNT: 
MISSING_REFERENCED_PATH_COUNT: 

NATIVE_AGENT_FRONTMATTER_VALID: YES/NO
NATIVE_SKILL_FRONTMATTER_VALID: YES/NO
CLAUDE_MD_IMPORT_VALID: YES/NO
MANIFEST_SCHEMA_VALID: YES/NO
AGENT_MANIFEST_AUTHORITY_PARITY: YES/NO
SELF_CERTIFICATION_PROHIBITION_PRESERVED: YES/NO

GOVERNANCE_TESTS_PASSING: 
GOVERNANCE_TESTS_FAILING: 
CUSTOMIZATION_BLOCKERS: 
CUSTOMIZATION_MAJOR_FINDINGS: 
CUSTOMIZATION_MINOR_FINDINGS: 
CUSTOMIZATION_INFORMATIONAL_FINDINGS: 
REGISTRATION_ENFORCING_FINDINGS: 

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

PACKAGE_JSON_CHANGED: NO
PACKAGE_VERSION_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
TEST_PATTERNS_CHANGED: NO
TSCONFIG_CHANGED: NO
REPAIR_12_CONTENT_CHANGED: NO
LEGACY_AGENT_MD_CHANGED: NO
NATIVE_AGENT_CONTENT_CHANGED: NO
NATIVE_SKILL_CONTENT_CHANGED: NO
VSIX_CHANGED: NO
QA_WORKSPACE_TOUCHED: NO
REPAIR_13_STARTED: NO
STAGED_FILES: 
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

This implementation session must not claim that runtime discovery has been
proven. Runtime activation requires a VS Code reload followed by a fresh Claude
session.

End exactly with one:

CLAUDE_NATIVE_REFERENCE_REPAIR_RESULT:
PASS_READY_FOR_RELOAD_AND_FRESH_CLAUDE_ACTIVATION_CHECK

CLAUDE_NATIVE_REFERENCE_REPAIR_RESULT:
FAIL_VALIDATION

CLAUDE_NATIVE_REFERENCE_REPAIR_RESULT:
FAIL_UNAUTHORIZED_CHANGE

CLAUDE_NATIVE_REFERENCE_REPAIR_RESULT:
BLOCKED_IDENTITY_OR_WORKTREE_DRIFT

CLAUDE_NATIVE_REFERENCE_REPAIR_RESULT:
BLOCKED_ADDITIONAL_REFERENCE_SCOPE
