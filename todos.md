TASK: BUILD_PORTABLE_ETL_AGENT_PROCESS_FRAMEWORK_FOR_LOCAL_AND_GITHUB_CLOUD_V1

Run this task in a NEW CHAT after the current Repair 12 independent review has
finished.

Execution environment:

* VS Code desktop;
* Local Agent mode;
* Claude Opus 5;
* Extra High reasoning;
* Bypass Permissions may remain enabled;
* do NOT select Cloud for this bootstrap task.

Repository:

C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected identity:

ORIGIN: https://github.com/TD-Universe/agentic_etl.git
BRANCH: hotfix/hf1-oracle-fresh-consumer-v2
HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
SOURCE_VERSION: 0.3.144

Purpose:

Create and validate a portable, evidence-driven development process that works
with:

1. GitHub Copilot Agent in local VS Code;
2. GitHub Copilot Coding Agent / Cloud;
3. Claude models selected inside GitHub Copilot;
4. future hotfix implementation, independent review, packaging, and Runtime-QA
    sessions.

The framework must reduce user handoffs, detect known failure classes before a
hotfix is declared complete, and replace repeated giant prompts with portable
Instructions, Skills, Custom Agents, validators, evidence packets, and
machine-checkable gates.

This is a process-governance task. It is not authorized to modify ETL behavior.

==================================================

1. NON-NEGOTIABLE CHANGE BOUNDARY
    ==================================================

Do not:

* change Repairs 5–12 production behavior;
* change existing Repair 5–12 test meaning or expected results;
* modify src/test/testPatterns.ts;
* modify the QA STTM or Development Test Workspace;
* modify or rebuild an existing VSIX;
* change package version, dependencies, publisher, or Extension ID;
* create package-lock.json;
* install, uninstall, activate, or smoke-test an extension;
* execute Runtime QA, Preview, approval, write, or Databricks operations;
* access etl-framework-adb or real data;
* install or download dependencies;
* commit, push, merge, tag, stage, stash, reset, restore, clean, or delete files;
* add an Anthropic GitHub Action, GitHub App, API key, OAuth token, or secret;
* claim that uncommitted local customization files are visible to GitHub Cloud;
* replace existing .github/** drafts wholesale merely to simplify editing.

The current working tree is expected to be dirty and may contain:

* Repairs 5–12;
* modified .github/copilot-instructions.md;
* untracked .github/instructions/**, agents, skills, prompts, templates, and
    workflows.

Preserve all existing work.

For each existing process asset, record:

* relative path;
* tracked, modified, or untracked state;
* size;
* SHA-256;
* purpose;
* active surfaces;
* canonical or advisory status.

Use surgical patches. Preserve every non-conflicting rule.

If two existing rules conflict and repository evidence cannot resolve the
conflict, do not choose silently. Record:

OWNER_DECISION_REQUIRED

Continue with unrelated safe work.

==================================================
2. EXECUTION AND IDENTITY PREFLIGHT

Before editing, prove execution of real native processes:

* cmd.exe /c echo PROCESS_EXECUTION_OK
* git.exe –version
* node.exe –version
* the existing npm executable version

Capture stdout, stderr, exit code, signal, and executable path.

Do not classify the environment as blocked after one failed inline PowerShell
capture.

If inline capture returns empty output, retry using a task-owned helper under
the operating system temporary directory and direct process spawning or
Start-Process with separate stdout and stderr files.

Do not modify repository files during recovery.

If native execution still cannot be proven, stop with:

PROCESS_HARDENING_RESULT: BLOCKED_EXECUTION_ENVIRONMENT

Verify:

* absolute repository root;
* origin;
* branch;
* HEAD;
* package version;
* staged-file count;
* stash count;
* package-lock absence.

If identity differs, stop before editing:

PROCESS_HARDENING_RESULT: BLOCKED_IDENTITY_MISMATCH

If staged files exist, stop:

PROCESS_HARDENING_RESULT: BLOCKED_STAGED_CHANGES

Capture a NUL-safe baseline containing status, size, SHA-256, and mtime for:

* every tracked-modified path;
* every untracked path;
* all .github/** files;
* root CLAUDE.md and AGENTS.md files, if present;
* package.json;
* all Repair 12 implementation and test paths;
* src/test/testPatterns.ts;
* databricks-etl-copilot-0.3.144.vsix;
* the authorized QA STTM.

Run the current compile, lint, Repair 12 focused suite, and canonical full unit
suite using existing dependencies.

Record exact failure fingerprints rather than aggregate counts.

The expected pre-process full-suite evidence is approximately:

* 2243 passing;
* 1 pending;
* 5 failing.

Do not rely on those counts alone. Capture the exact five failure identities.

If compile, lint, or Repair 12 focused tests fail, stop before process edits:

PROCESS_HARDENING_RESULT: BLOCKED_UNSTABLE_SOURCE_BASELINE

==================================================
3. AUDIT LOCAL AND CLOUD CUSTOMIZATION SURFACES

Fully inventory and read:

* .github/copilot-instructions.md;
* .github/instructions/**/*.instructions.md;
* .github/prompts/**/*.prompt.md;
* .github/skills/**/SKILL.md;
* .github/agents/**/*.agent.md;
* .github/hooks/*.json;
* .github/templates/**;
* .github/workflows/**;
* root and nested AGENTS.md;
* root CLAUDE.md;
* existing customization validators and package scripts.

Do not assume that a file is active merely because it exists.

Produce a compatibility matrix containing:

* path;
* asset type;
* tracked state;
* local VS Code Agent support;
* GitHub Cloud support;
* GitHub code-review support;
* automatic or explicit loading;
* canonical, advisory, or convenience classification;
* validation status;
* required migration.

Use these platform constraints:

* .github/copilot-instructions.md is supported locally and in GitHub Cloud;
* .github/instructions/*.instructions.md is supported locally and in Cloud
    when frontmatter and applyTo are valid;
* .github/skills/<skill>/SKILL.md is supported locally and in Cloud;
* .github/agents/*.agent.md is supported locally and in Cloud;
* Custom Agent discovery and Cloud setup may require the asset to exist on the
    default branch;
* .github/prompts/*.prompt.md is a local VS Code convenience surface and must
    not be the only authority for a Cloud workflow;
* root CLAUDE.md may be used only as a thin compatibility bridge;
* local modified or untracked files are invisible to Cloud;
* GitHub Cloud cannot prove local VSIX installation, VS Code Extension Host
    activation, or the local Development Test Workspace;
* Cloud hooks execute in Linux and must not depend on PowerShell.

List every safety-critical rule or workflow that currently exists only in:

* a prompt file;
* an uncommitted local file;
* a screenshot or prior chat report.

Screenshots and chat history are evidence for this audit, not permanent machine
authority.

==================================================
4. DEFINE THE CANONICAL PROCESS

Create or update one canonical process manifest. Reuse an existing convention
if available; otherwise use:

.github/agent-governance/process-manifest.json

Do not embed:

* current version;
* current branch;
* current HEAD;
* absolute machine paths;
* username;
* machine name;
* VSIX SHA;
* current Preview ID.

Declare this lifecycle:

PREFLIGHT
→ BASELINE
→ REPRODUCE
→ BOUNDED_IMPLEMENTATION
→ SOURCE_VALIDATION
→ FULL_PUBLIC_SEAM_VALIDATION
→ INDEPENDENT_REVIEW
→ VERSION_AND_PACKAGE
→ EXACT_PACKAGE_VERIFICATION
→ LOCAL_INSTALL_AND_ACTIVATION
→ LIVE_RUNTIME_QA
→ PREVIEW_ONLY
→ EXPLICIT_APPROVAL
→ WRITE

Encode these distinctions:

* internal model success is not public-tool success;
* source success is not compiled success;
* compiled success is not packaged success;
* package verification is not installed-runtime activation;
* installation listing is not active Extension Host identity;
* activation is not Runtime QA;
* Preview is not approval;
* approval is not write;
* Cloud cannot perform local activation or local Runtime QA;
* an unavailable capability requires a typed handoff, not fabricated success;
* a changed source or package identity invalidates downstream evidence only,
    not already-grounded upstream evidence.

==================================================
5. CONSOLIDATE INSTRUCTIONS

Keep .github/copilot-instructions.md concise.

It may contain only:

* repository-wide invariants;
* lifecycle routing;
* canonical-source precedence;
* protected paths;
* fail-closed rules;
* capability boundaries;
* evidence and checkpoint requirements.

Do not copy full workflows into it.

Audit every path-specific instruction:

* validate YAML frontmatter;
* validate .instructions.md naming;
* validate applyTo patterns against actual repository paths;
* narrow rules that currently use applyTo "**" but govern only one path type;
* detect contradictory or duplicated rules;
* keep runtime, test, packaging, business, workflow-asset, and recovery rules in
    their proper scopes.

At minimum preserve the intent of:

* business-context instructions;
* change-safety instructions;
* ETL runtime safety;
* ETL test safety;
* ETL packaging safety;
* execution recovery;
* workflow asset boundaries;
* workflow coherence.

Create or update a short root CLAUDE.md compatibility bridge.

CLAUDE.md must:

* point to .github/copilot-instructions.md;
* point to the canonical lifecycle Skill;
* say that .github/prompts/** is not Cloud authority;
* require native-process preflight and evidence checkpoints;
* forbid claiming results beyond the current environment’s capabilities.

Do not duplicate the complete instruction corpus in CLAUDE.md.

==================================================
6. MIGRATE PROMPT-ONLY WORKFLOWS TO SKILLS

Audit every .github/prompts/*.prompt.md.

For every material hotfix, review, package, installation, Runtime-QA, Preview,
approval, or recovery workflow:

* migrate the canonical workflow into a Skill;
* retain the Prompt only as a thin local wrapper;
* ensure no critical safety rule remains solely in a Prompt File;
* place reusable checklists and examples under skill references;
* keep deterministic logic in scripts rather than Markdown.

Prefer a small coherent Skill set.

Create or update:

1. .github/skills/etl-hotfix-lifecycle/SKILL.md
    * preflight;
    * baseline;
    * dynamic reproduction;
    * bounded implementation;
    * source validation;
    * full public seam;
    * checkpoint.
2. .github/skills/etl-independent-review/SKILL.md
    * new-session independence disclosure;
    * read-only operation;
    * exact change-boundary review;
    * public seam and negative-path verification;
    * finding fingerprints;
    * no trust in the implementer’s conclusion.
3. .github/skills/etl-package-delivery/SKILL.md
    * version boundary;
    * exactly one build;
    * exact VSIX path;
    * no newest-file, mtime, or glob selection;
    * source/compiled/package parity;
    * computed artifact manifest;
    * local install handoff.
4. .github/skills/etl-runtime-qa/SKILL.md
    * local-only Extension Host identity;
    * exactly one authorized Development Test Workspace root;
    * actual public ETL tool invocation;
    * STTM evidence;
    * zero-write Preview;
    * approval pending;
    * no Cloud claim of local activation.
5. .github/skills/etl-execution-recovery/SKILL.md
    * distinguish missing executable from broken output capture;
    * typed blocker classification;
    * no blind retry;
    * resumable checkpoint;
    * exact next stage.

Every Skill must define:

* prerequisites;
* required capabilities;
* authorized mutations;
* forbidden mutations;
* protected paths;
* input evidence;
* success evidence;
* blocker outputs;
* checkpoint schema;
* next role or Agent.

==================================================
7. CREATE NARROW CUSTOM AGENTS

Validate the currently supported Custom Agent schema before editing.

Do not invent unsupported frontmatter or tool names.

Create or update only these Agents:

1. .github/agents/etl-hotfix-implementer.agent.md
    * may perform bounded source/test changes;
    * must use the hotfix lifecycle Skill;
    * cannot perform independent review, release, installation, or Runtime QA.
2. .github/agents/etl-independent-reviewer.agent.md
    * strictly read-only;
    * must run in a new Chat/session;
    * cannot modify tests or source;
    * must inspect the full public seam and negative cases.
3. .github/agents/etl-release-verifier.agent.md
    * version, package, exact-package verification, and evidence handoff only;
    * cannot change production behavior;
    * cannot claim local Runtime QA from Cloud.

Runtime QA remains a Skill usable in the authorized local QA window.

If a Cloud execution requests live Runtime QA, the Agent must return:

LOCAL_RUNTIME_REQUIRED

Every Agent must emit a machine-readable checkpoint with:

* completed stage;
* evidence digest;
* unresolved findings;
* invalidated downstream stages;
* exact next stage;
* exact next Agent or local environment.

Do not rely on UI-only handoff metadata unless verified as supported on both
required surfaces.

==================================================
8. ADD DETERMINISTIC GOVERNANCE TOOLS

Inspect existing scripts first. Reuse or extend them rather than creating
parallel implementations.

If no canonical implementation exists, create:

scripts/agent-governance/

Use Node built-ins only.

Do not modify dependencies or package.json.

Implement:

* preflight.mjs
* capture-baseline.mjs
* validate-customizations.mjs
* validate-test-registration.mjs
* verify-change-boundary.mjs
* validate-evidence-packet.mjs
* emit-checkpoint.mjs

Requirements:

* Windows and Linux compatible;
* direct child-process spawning;
* no shell command concatenation;
* capture stdout, stderr, exit code, signal, and executable;
* use process.execPath when invoking Node;
* platform-aware npm executable resolution;
* no PowerShell-only implementation;
* NUL-safe Git status parsing;
* SHA-256 hashing;
* exact failure fingerprints;
* no embedded local paths or current artifact identifiers;
* human-readable and JSON output;
* default evidence output under the OS temporary directory;
* never write into a consumer workspace;
* never change Git state;
* fail closed on missing or ambiguous evidence.

The customization validator must detect:

* invalid instruction frontmatter;
* invalid applyTo patterns;
* missing referenced Skills or Agents;
* duplicate globally applicable instruction rules;
* critical prompt-only workflows;
* claims that Cloud can prove local installed-runtime state;
* absolute machine paths in portable assets;
* hardcoded current version, HEAD, SHA, Preview ID, or username;
* invalid Custom Agent schema;
* stale or broken documentation links;
* setup or hooks that depend on unsupported Cloud execution.

The test-registration validator must prove that every intended canonical test
suite is discovered exactly once.

Do not select tests or VSIX files by newest modification time.

==================================================
9. ADD MACHINE-READABLE EVIDENCE CONTRACTS

Create:

* an evidence-packet JSON schema;
* a concise human-readable evidence template;
* a checkpoint schema.

Reuse existing template conventions if available.

The evidence packet must contain:

* task ID;
* lifecycle stage;
* environment and capability class;
* repository identity;
* baseline digest;
* authorized and protected paths;
* before/after hashes;
* commands and exit codes;
* failure fingerprints;
* public-seam assertions;
* source, compiled, package, installed, and runtime identities when applicable;
* artifact path, size, and computed SHA when applicable;
* Preview ID and frozen-manifest digest when applicable;
* approval and write state;
* blocker classification;
* unresolved owner decisions;
* exact next stage;
* nondeterministic audit metadata clearly separated from deterministic evidence.

Never compare audit timestamps as deterministic product evidence.

==================================================
10. PREVENT THE OBSERVED FAILURE CLASSES

Create validator tests or explicit contract tests for these real incidents:

A. Wrong workspace or multi-root execution:
preflight rejects before interpretation or mutation.

B. Installed version differs from active Extension Host version:
installed listing is insufficient; local runtime evidence is mandatory.

C. Native process output appears empty:
recovery distinguishes output-capture failure from missing executable.

D. Focused suite exists but canonical suite does not discover it:
registration validator fails.

E. Internal STTM model passes while public ETL output omits contract fields:
lifecycle requires an actual public-tool/full-seam test.

F. Single-file STTM accidentally enumerates siblings:
workflow requires explicit file-versus-bundle semantics and an IO-spy test.

G. Expected test literals differ from the authorized STTM:
classify as STALE_TEST_SPEC; never edit the STTM or fabricate values.

H. SHA or version is manually mistranscribed:
accept only computed artifact-manifest values.

I. Package verifier selects newest artifact:
explicit artifact path is mandatory.

J. Dirty overlay causes incorrect change ownership:
baseline hashes plus authorized-path allowlist and post-change verification.

K. Implementer reviews its own work:
independent reviewer must disclose session identity and remain read-only.

L. Critical safety logic exists only in local Prompt Files:
customization validation fails.

M. Internal-model Golden Path does not cross the public runtime seam:
completion evidence is rejected.

==================================================
11. HOOKS AND CLOUD SETUP — CONDITIONAL

Hooks must not be the only enforcement mechanism.

Create or update a conservative .github/hooks/*.json guard only if the
official schema and repository policy can be validated.

A hook may block only clearly dangerous operations such as:

* destructive Git reset or clean;
* forced push;
* broad recursive deletion;
* mutation outside an authorized root;
* mutation of protected consumer or release paths.

Do not make the hook responsible for semantic correctness.

Cloud-compatible hook commands must use Bash or a verified cross-platform
command. Do not depend on PowerShell.

Assess .github/workflows/copilot-setup-steps.yml.

Create it only if the repository already has a deterministic and authorized
bootstrap that:

* does not create or modify a lockfile;
* does not require a new secret;
* follows existing action-pinning policy;
* is Linux compatible;
* does not invent a new dependency-installation strategy.

Otherwise report:

CLOUD_SETUP_WORKFLOW: NOT_CREATED
CLOUD_SETUP_BLOCKER: 

A setup workflow is not active for Cloud merely because it exists locally. It
must later be committed and available on the required/default branch.

Create a narrow governance CI workflow only if existing workflow policy and
approved action references can be reused safely.

It may run only dependency-free governance validation. It must not publish,
install, release, or mutate consumer files.

Do not add Anthropic Claude Code Actions or secrets.

==================================================
12. VALIDATION

Add Node built-in tests under the governance script directory for:

* successful process capture;
* nonzero exit propagation;
* missing executable;
* stdout/stderr separation;
* Windows paths;
* NUL-safe Git status;
* dirty baseline preservation;
* frontmatter and applyTo validation;
* critical prompt-only detection;
* unsupported Cloud/local claims;
* exact change-boundary detection;
* evidence-packet validation;
* test-registration uniqueness.

Run:

* governance Node tests;
* customization validation;
* test-registration validation;
* compile;
* lint;
* Repair 12 focused suite;
* canonical full unit suite;
* any existing GitHub customization guard.

For each command report:

* exact command;
* environment;
* exit code;
* passing, pending, and failing counts;
* complete failure fingerprints.

The three existing customization failures may disappear only if the new
process assets directly and correctly resolve them.

The two EvalGating failures may remain only if their exact identities match the
pre-change baseline and no authorized process file caused them.

Do not regenerate a baseline or weaken a test to obtain a pass.

Required:

* compile passes;
* lint passes;
* Repair 12 focused suite passes;
* all governance tests pass;
* no new functional regression;
* no new security regression;
* no Repair 5–12 source or test byte changes;
* no QA STTM byte changes;
* no VSIX byte changes;
* zero staged files.

==================================================
13. POST-CHANGE BOUNDARY

Authorized paths:

* .github/copilot-instructions.md;
* .github/instructions/**;
* .github/prompts/** only as thin wrappers;
* .github/skills/**;
* .github/agents/**;
* .github/hooks/** when Section 11 passes;
* .github/templates/**;
* .github/agent-governance/**;
* .github/workflows/** only when Section 11 passes;
* root CLAUDE.md;
* scripts/agent-governance/**;
* stable process documentation under docs.

No other task-attributable path may change.

Prove unchanged:

* all Repairs 5–12 production files;
* all existing Repair 5–12 test files;
* src/test/testPatterns.ts;
* package.json;
* package version;
* dependencies;
* package-lock absence;
* existing 0.3.144 VSIX;
* QA STTM and QA workspace;
* branch and HEAD;
* Git index and staged count.

Do not commit, push, or stage.

==================================================
14. FINAL REPORT

Return:

REPOSITORY_ROOT: 
ORIGIN: 
BRANCH: 
HEAD: 
SOURCE_VERSION: 
PROCESS_EXECUTION_PREFLIGHT: PASS/FAIL
STAGED_FILES_AT_START: 
STAGED_FILES_AT_END: 
BASELINE_PATH_COUNT: 

CUSTOMIZATION_COMPATIBILITY_MATRIX: 
PREEXISTING_CUSTOMIZATION_PATHS: 
PREEXISTING_CUSTOMIZATIONS_OVERWRITTEN: NO
PROMPT_FILES_LOCAL_ONLY_COUNT: 
CRITICAL_PROMPT_ONLY_FLOWS_BEFORE: 
CRITICAL_PROMPT_ONLY_FLOWS_AFTER: <complete list; expected NONE>

GLOBAL_INSTRUCTIONS_VALID: YES/NO
PATH_INSTRUCTIONS_VALID: YES/NO
CLAUDE_MD_BRIDGE_VALID: YES/NO
SKILLS_CREATED_OR_UPDATED: 
CUSTOM_AGENTS_CREATED_OR_UPDATED: 
PROMPT_WRAPPERS_RETAINED: 
HOOK_STATUS: CREATED/UPDATED/NOT_CREATED
PROCESS_MANIFEST_PATH: 
EVIDENCE_PACKET_SCHEMA_PATH: 
CHECKPOINT_SCHEMA_PATH: 
GOVERNANCE_SCRIPT_PATHS: 
GOVERNANCE_TEST_PATHS: 

LOCAL_AGENT_SUPPORT: PASS/FAIL
GITHUB_CLOUD_ASSET_SUPPORT: PASS/FAIL
CLOUD_UNCOMMITTED_ASSETS_AVAILABLE: NO
CLOUD_SETUP_WORKFLOW: CREATED/UPDATED/NOT_CREATED
CLOUD_SETUP_BLOCKER: 
GOVERNANCE_CI_WORKFLOW: CREATED/UPDATED/NOT_CREATED
GOVERNANCE_CI_BLOCKER: 
LOCAL_RUNTIME_QA_FROM_CLOUD_ALLOWED: NO
ANTHROPIC_ACTION_OR_SECRET_ADDED: NO

COMPILE_PASS: YES/NO
LINT_PASS: YES/NO
REPAIR_12_FOCUSED_PASS: YES/NO
FULL_UNIT_PASSING_COUNT: 
FULL_UNIT_PENDING_COUNT: 
FULL_UNIT_FAILURE_COUNT: 
FULL_UNIT_FAILURE_FINGERPRINTS: 
FAILURES_RESOLVED_BY_AUTHORIZED_PROCESS_CHANGES: 
NEW_FUNCTIONAL_REGRESSIONS: 
NEW_SECURITY_REGRESSIONS: 
GOVERNANCE_VALIDATOR_PASS: YES/NO
GOVERNANCE_SCRIPT_TESTS_PASS: YES/NO
TEST_REGISTRATION_VALIDATOR_PASS: YES/NO

TASK_ATTRIBUTABLE_CHANGED_PATHS: 
UNAUTHORIZED_CHANGED_PATHS: 
REPAIR_12_PATHS_PRESERVED: YES/NO
QA_STTM_PRESERVED: YES/NO
VSIX_0_3_144_PRESERVED: YES/NO
PACKAGE_VERSION_CHANGED: NO
DEPENDENCIES_CHANGED: NO
PACKAGE_LOCK_CREATED: NO
VSIX_BUILT_OR_MODIFIED: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
PREVIEW_CREATED: NO
WRITE_EXECUTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
TAG_CREATED: NO

OWNER_DECISIONS_REQUIRED: 
READY_FOR_GENUINELY_INDEPENDENT_PROCESS_REVIEW: YES/NO
READY_TO_COMMIT_PROCESS_FRAMEWORK: NO
READY_TO_PUSH_PROCESS_FRAMEWORK: NO
CLOUD_AVAILABILITY_REQUIRES_COMMIT_PUSH_AND_DEFAULT_BRANCH_ROLLOUT: YES

PASS requires:

* native-process and repository preflight pass;
* reusable workflows are canonical Skills;
* no safety-critical workflow remains Prompt-only;
* Instructions are concise and correctly scoped;
* Custom Agents have explicit capability and mutation boundaries;
* validators use real process evidence and exact fingerprints;
* public-seam validation is mandatory in the lifecycle;
* evidence and checkpoint schemas validate;
* no new functional or security regression;
* no production, Repair, QA, VSIX, package, dependency, or Git-state mutation;
* all process changes remain unstaged for a separate independent review.

End exactly with one:

PROCESS_HARDENING_RESULT: PASS_READY_FOR_INDEPENDENT_REVIEW
PROCESS_HARDENING_RESULT: FAIL_UNAUTHORIZED_CHANGE
PROCESS_HARDENING_RESULT: FAIL_VALIDATION
PROCESS_HARDENING_RESULT: BLOCKED_EXECUTION_ENVIRONMENT
PROCESS_HARDENING_RESULT: BLOCKED_IDENTITY_MISMATCH
PROCESS_HARDENING_RESULT: BLOCKED_STAGED_CHANGES
PROCESS_HARDENING_RESULT: BLOCKED_UNSTABLE_SOURCE_BASELINE
PROCESS_HARDENING_RESULT: OWNER_DECISION_REQUIRED
