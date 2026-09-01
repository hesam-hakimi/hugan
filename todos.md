Step 0 — Phase H Coverage and F5 Launch-Provenance Audit

Objective

Perform a strictly read-only audit of:

1. Phase H tracked-input coverage for Repair A and Repair B.
2. The repository-defined compile/F5 launch path needed to prove that a future Extension Development Host loads the repaired source code.

Do not implement fixes, compile, launch F5, regenerate Eval Golden, run tests, or modify any file.

Execution environment

Run only in the normal VS Code source-repository window:

Repository root:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147
Required branch:
fix/workspace-write-completion-0.3.148
Required HEAD:
edeaaa74fa84df715fedb7b2d9f50f2418018770
Required HEAD subject:
test: refresh Phase H evaluation baseline

This is not:

* the Extension Development Host;
* the QA workspace;
* a consumer workspace;
* an installed VSIX session.

If PowerShell cannot resolve bare git, node, npm, or npx commands because PATHEXT is malformed, prefix only the affected invocation with:

$env:PATHEXT = '.COM;.EXE;.BAT;.CMD'

Do not persist that workaround in the registry, profile, VS Code settings, repository, or operating-system environment.

Hard safety restrictions

This entire task is read-only.

Do not:

* edit, create, delete, rename, restore, stage, or commit files;
* run npm run eval:golden;
* run compile or test commands;
* launch or reload F5;
* access or modify the QA workspace;
* inspect broad external directories or VS Code workspaceStorage;
* fetch, pull, merge, rebase, reset, checkout, stash, clean, amend, cherry-pick, push, or publish;
* build, install, package, or inspect a VSIX;
* alter Git refs, index, configuration, environment profiles, or settings;
* treat a version string such as 0.3.147 as proof that repaired runtime code is loaded.

If any required preflight identity differs, stop immediately and report the exact mismatch.

Phase 0 — Repository preflight

Record exact evidence for:

1. Canonical repository root.
2. Current branch.
3. Full HEAD SHA.
4. HEAD subject.
5. Sole parent SHA and parent count.
6. git status --short --untracked-files=all.
7. Staged-path inventory.
8. Stash inventory.
9. Confirmation that these commits are present in this exact linear order:

46f6930e8474f6ac07d157cc85d21687a08869f3
fix: expose canonical runtime artifact contract
6107aa0b0e0d5bb26a998db62ee26712a728139a
fix: align artifact validation with canonical contract
edeaaa74fa84df715fedb7b2d9f50f2418018770
test: refresh Phase H evaluation baseline

Validate every SHA using Git object inspection. Do not rely on abbreviated SHAs or commit subjects alone.

The worktree, index, untracked inventory, and stash must all be empty.

Phase 1 — Establish the authoritative Repair A/B path inventories

Using Git history only, enumerate every path changed by:

Repair A:
46f6930e8474f6ac07d157cc85d21687a08869f3
Repair B:
6107aa0b0e0d5bb26a998db62ee26712a728139a

Classify each changed path as one of:

* production behavior;
* canonical contract;
* public tool boundary;
* packaged runtime documentation/context;
* package/tool description;
* test;
* generated or non-behavioral.

Do not infer the list from previous reports. Resolve it directly from Git.

At minimum, explicitly determine the status of:

resources/framework/contracts/job-config-envelope.v1.json
src/core/framework/TrustedJobConfigEnvelopeResolver.ts
src/tools/EtlReadOnlyToolService.ts
src/core/validation/DataSourcingConfigValidator.ts
src/tools/EtlActionToolService.ts
resources/copilot/context/etl-module-reference.md
package.json

Also include every other Repair A/B path discovered from Git.

Phase 2 — Audit Phase H tracked-input coverage

Locate the authoritative definition and all consumers of:

PHASE_H_TRACKED_INPUT_PATTERNS

Read the relevant implementation, tests, report-generation logic, and current committed Phase H JSON/Markdown reports sufficiently to prove:

1. The exact tracked patterns.
2. How patterns are expanded.
3. Whether directories are recursive.
4. Whether contract JSON, public tool adapters, packaged documentation, and package descriptions are included.
5. Whether the tracked-input digest covers file contents, paths, or both.
6. Whether missing/new files affect the digest.
7. Which Repair A/B changed paths contributed to the latest refreshed report.
8. Why the current report lists the changed tracked inputs it lists.

Build an exact coverage matrix with these columns:

Repair	Path	Behavior role	Matching Phase H pattern	Covered?	Evidence

Use only these classifications:

TRACKED
UNTRACKED_BEHAVIOR_CRITICAL
NOT_BEHAVIOR_INPUT_WITH_EVIDENCE
UNRESOLVED

Do not dismiss a path merely because focused tests cover it. This phase is specifically auditing the completeness of Phase H freshness tracking.

Pay special attention to whether the latest Golden refresh tracked only:

src/core/framework/TrustedJobConfigEnvelopeResolver.ts
src/core/validation/DataSourcingConfigValidator.ts

Verify this from the committed report and implementation rather than assuming it.

Phase 3 — Assess the current Eval Golden claim

Determine which statement is supported:

A. PHASE_H_TRACKING_COMPLETE
B. PHASE_H_TRACKING_GAP
C. PHASE_H_TRACKING_UNRESOLVED

Use PHASE_H_TRACKING_GAP if any behavior-critical Repair A/B contract, public handler, packaged runtime context, or behavior-facing package declaration is absent from the tracked-input set.

If a gap exists:

* identify the exact missing paths;
* identify the narrowest authoritative pattern change that would cover them;
* state whether another single Eval Golden refresh would then be required;
* do not implement the change;
* do not run the generator.

The current Golden report contains timestamps and latency values. Do not require full byte-for-byte reproducibility of generated reports. Assess deterministic semantic fields, tracked-input digest, schema, scenario rows, and gate metrics separately from wall-clock fields.

Phase 4 — Read-only F5 launch-provenance plan

Inspect only repository-owned launch/build configuration needed for the next phase, including as applicable:

package.json
.vscode/launch.json
.vscode/tasks.json
tsconfig files
the configured extension entry point
relevant repository instructions

Do not compile or launch anything.

Report:

1. Extension ID derived from repository metadata.
2. package.json entry point used by VS Code.
3. Exact compile/prelaunch task required by the intended F5 configuration.
4. Exact F5 launch configuration name.
5. How extensionDevelopmentPath is established.
6. How the QA workspace should be opened in the new Extension Development Host.
7. Whether ignored generated output such as out/ can remain stale.
8. Which evidence can prove that the active extension comes from this source repository rather than an installed extension.
9. How to prove exactly one active extension instance.
10. How to ensure the Extension Development Host has exactly one workspace root.
11. How to open a fresh ETL Orchestrator chat after the host launches.
12. Which registered public discovery calls can behaviorally prove Repair A is active.
13. How the later public etl_validate_artifacts call will behaviorally prove Repair B is active.

Version 0.3.147 alone must explicitly be classified as insufficient provenance.

Do not inspect installed-extension directories or launch F5 during this audit.

Required final report

Return a concise but complete English report containing:

1. Preflight evidence table.
2. Repair A changed-path inventory.
3. Repair B changed-path inventory.
4. Phase H coverage matrix.
5. Exact Phase H verdict.
6. Missing critical tracked inputs, if any.
7. Minimal recommended tracking correction, without implementing it.
8. Whether a new Golden refresh would be required after that correction.
9. F5 compile/launch configuration facts.
10. Runtime-provenance evidence required in the next phase.
11. Exact statement that no file, index entry, ref, stash, setting, build output, Eval artifact, or workspace content was modified.

Finish with exactly one of:

SOURCE_COVERAGE_PROVENANCE_AUDIT_COMPLETE

or, if the audit cannot be completed safely:

SOURCE_COVERAGE_PROVENANCE_AUDIT_BLOCKED

Do not claim that fixture authoring or F5 QA is ready. The only permitted outcome is an evidence-backed coverage and launch-provenance assessment.
