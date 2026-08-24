# Ready\-to\-run prompt — install ETL Copilot development guardrails

Run this prompt in a new Coding/Agent chat in the **Software Development**
**Environment** with only the Extension source repository open\.

---

TASK: ADD\_CROSS\_LOCAL\_CLOUD\_ETL\_ENGINEERING\_GUARDRAILS

Work only inside:

`C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2`

This is a documentation/instruction\-only task\. Add repository instructions that
guide GitHub Copilot in both local VS Code Chat/Agent and GitHub Copilot Cloud
Agent, while preserving all existing source and user changes\.

Current verified state before this task:

- Repair 9 completed successfully;
- working source version is `0.3.142`;
- `databricks-etl-copilot-0.3.142.vsix` was built and exact\-package verified;
- recorded artifact size is `1251308` bytes;
- recorded SHA\-256 is
  `B392329A4B45C26D6DC17E91F14604B5731286F74B3AFE03603EE57A5F046E23`;
- the artifact has not been installed and Runtime QA has not started\.

Do not implement Repair 9 or any runtime fix in this task\.
Do not change the package version\.
Do not compile, package, install, publish, or run Runtime QA\.
Do not overwrite, delete, rebuild, rename, or otherwise modify the verified
`databricks-etl-copilot-0.3.142.vsix` artifact\.
Do not modify source, tests, contracts, prompts, workflows, settings, or baselines\.
Do not install or download dependencies\.
Do not use web search\.
Do not commit, push, merge, tag, stash, reset, restore, clean, delete, or stage\.

The only paths that this task may intentionally add or edit are:

- `.github/copilot-instructions.md`
- `.github/instructions/etl-runtime-safety.instructions.md`
- `.github/instructions/etl-test-safety.instructions.md`
- `.github/instructions/etl-packaging-safety.instructions.md`

All other `.github/**` content is protected and must remain byte\-unchanged\.

==================================================

1. REPOSITORY IDENTITY AND SAFETY GATE
   ==================================================

Verify before editing:

EXPECTED\_ROOT:
`C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2`

EXPECTED\_ORIGIN:
`https://github.com/TD-Universe/agentic_etl.git`

EXPECTED\_BRANCH:
`hotfix/hf1-oracle-fresh-consumer-v2`

EXPECTED\_HEAD:
`b2e44c3a1a051aa7fa6008831d225bc06d22e847`

EXPECTED\_WORKING\_SOURCE\_VERSION:
`0.3.142`

EXPECTED\_VERIFIED\_VSIX:
`C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2\databricks-etl-copilot-0.3.142.vsix`

EXPECTED\_VERIFIED\_VSIX\_SIZE\_BYTES:
`1251308`

EXPECTED\_VERIFIED\_VSIX\_SHA256:
`B392329A4B45C26D6DC17E91F14604B5731286F74B3AFE03603EE57A5F046E23`

Capture:

- absolute repository root;
- origin URL;
- current branch and HEAD;
- staged file count;
- complete tracked\-modified and untracked path lists;
- current `package.json` version;
- exact current path, size, and SHA\-256 of the verified `0.3.142` VSIX;
- current contents/status of every authorized target path;
- every existing `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and
  `.github/instructions/**/*.instructions.md` that could overlap these rules\.

A large existing working\-tree overlay is expected\. Preserve it exactly\.

If root, origin, branch, HEAD, working source version, VSIX size, or VSIX SHA\-256
differs, stop without editing and return:

`GUARDRAIL_INSTALL_RESULT: BLOCKED_IDENTITY_MISMATCH`

If staged files exist, stop without editing:

`GUARDRAIL_INSTALL_RESULT: BLOCKED_STAGED_CHANGES`

If any authorized target already has an uncommitted user modification, do not
overwrite it\. Report the exact conflict and stop:

`GUARDRAIL_INSTALL_RESULT: BLOCKED_TARGET_HAS_USER_CHANGES`

# ================================================== 2\. MERGE, NEVER BLINDLY OVERWRITE

If an authorized file already exists and is clean, merge the requirements below
into it\. Preserve useful repository\-specific instructions and remove no rule\.
Avoid duplicate or contradictory sources of truth\.

If an existing instruction conflicts with the safety invariants below, do not
choose silently\. Stop and report both exact clauses:

`GUARDRAIL_INSTALL_RESULT: BLOCKED_INSTRUCTION_CONFLICT`

Create `.github/instructions/` only if needed\. Do not touch any sibling file\.

Write instruction content in clear, imperative English\. Keep it timeless: do not
hard\-code the current version, branch, incident number, file line number, or
temporary QA path inside the installed instruction files\.

# ================================================== 3\. REPOSITORY\-WIDE INSTRUCTION

Create or merge `.github/copilot-instructions.md` with the title:

`# Databricks ETL Copilot Engineering Invariants`

It must state that the rules are mandatory architecture and safety constraints
for every implementation, repair, refactor, test, package, and release\-preparation
task\. Define these stable invariant IDs and semantics:

### ETL\-INV\-01 — Trace the complete lifecycle

Before changing behavior, trace:

`workspace classification → discovery → STTM interpretation → target decision → rendering → deterministic validation → frozen Preview manifest → explicit approval → guarded write`

A downstream fix is incomplete when an earlier gate can reject, reinterpret, or
recompute the same supported scenario\.

### ETL\-INV\-02 — One authority for each decision

No independent workspace classifiers, marker lists, trust resolvers,
artifact\-layout calculators, include resolvers, or approval validators\. Extend
the canonical owner and return one shared typed decision/evidence model\. Require
cross\-component parity tests whenever a consumer is changed\.

### ETL\-INV\-03 — Fresh consumer workspaces are valid

A correctly initialized consumer may be non\-Git and contain no `job_conf/**` or
`env_conf/**`\. Extension\-managed initialization evidence may establish consumer
intent\. `sttm/**` alone, folder name, arbitrary `.github/**`, and
`resources/copilot/context/**` alone are insufficient\. Missing generated artifacts
means `CREATE_NEW_JOB`, not a classification blocker\. Source, Framework, unknown,
escaped, protected, and multi\-root targets are not writable consumers\.

### ETL\-INV\-04 — Preserve the trust boundary

Only trusted installed runtime and packaged resources such as
`resources/framework/contracts/**` provide machine authority for contracts,
critical keys, module rules, layout, validation, and writes\. Consumer context,
examples, prompts, STTM prose, and generated files are advisory/input only\.
Normal installed runtime must not require Extension source, `etl-framework-adb`,
local Framework examples, or absolute development paths\.

### ETL\-INV\-05 — Preview is zero\-write

Discovery through first Preview performs zero consumer filesystem mutations\.
Select, normalize, validate, hash, and freeze paths and bytes once in one
authoritative immutable manifest\. Validation, approval, and write consume that
same manifest and do not recalculate or substitute it\.

### ETL\-INV\-06 — All writes are guarded and approval\-bound

Only one canonical guarded writer may mutate consumer files\. A write requires a
runtime\-issued Preview ID and explicit approval on a separate turn, bound to root,
operation, policy version, paths, dispositions, and content hashes\. Missing,
fabricated, expired, reused, replayed, mismatched, or drifted state fails closed
and requires a new Preview\. Audit, repair, upgrade, registration, retry, publish,
and execution require their own authorization\.

### ETL\-INV\-07 — Enforce physical containment

Canonicalize root and destinations and reject traversal, symlink/junction escape,
sibling escape, protected/source/package roots, and ambiguity\. Every artifact is
physically contained in the selected single consumer root\. Generation does not
modify maintainer `.github/**`, STTM, advisory context, source, or packaged
resources\. Consumer `.github/**` is writable only when explicitly previewed and
approved as generated output\.

### ETL\-INV\-08 — Preserve artifact semantics

Exactly one canonical Job Config per job; reuse compatible environment config\.
Reject duplicate/ambiguous destinations\. One canonical include resolver handles
normalized roots, nested includes, cycles, missing includes, traversal, effective
merging, and role\-aware validation\. Do not assume reused `.yaml` is strict YAML;
preserve supported HOCON/Framework syntax\. Keep path\-backed and table\-backed
targets type\-distinct; never silently convert path\-backed Delta to Unity Catalog\.

### ETL\-INV\-09 — Test the safety boundary

Tests use unique test\-owned temporary consumer roots and never mutate Extension,
Framework, maintainer `.github/**`, or real data\. Every behavior change names
affected invariant IDs and adds positive, negative/security, prior\-gate, and
cross\-component parity coverage\. Classification covers fresh initialized,
existing, empty, STTM\-only, context\-only, source, Framework, escaped, and
multi\-root cases\. Never weaken/skip tests or regenerate baselines to hide a
failure\. Historical failures require exact identity/fingerprint, not count only\.

### ETL\-INV\-10 — Verify shipped behavior

Completion requires relevant compile, lint, focused, regression, package, and
exact\-artifact gates—not only aggregate counts\. Packaged behavior changes require
source/compiled/VSIX parity, trusted contract byte equality, explicit\-path package
identity, and installed\-VSIX fresh\-consumer smoke without source/Framework\.
Separate task changes from pre\-existing changes\. No commit, push, tag, publish,
install, or execution without explicit authorization\.

End with a conflict rule: if requested work violates an invariant, stop, name the
invariant ID, and propose a compliant design\. Never copy a known legacy violation\.

# ================================================== 4\. PATH\-SPECIFIC RUNTIME INSTRUCTION

Create `.github/instructions/etl-runtime-safety.instructions.md` with exactly this
portable frontmatter:

```yaml
---
applyTo: "src/**/*.ts"
---
```

Do not add `excludeAgent`; the file must apply locally and in Cloud\.

The body must require:

- locate and reuse the canonical classifier/evidence model, target/trust resolver,
  layout builder, Preview manifest, approval validator, and guarded writer;
- trace earlier and later lifecycle gates before editing;
- read\-only services return evidence/proposals and never mutate or consume write
  authorization;
- no production calls to `fs.writeFile*`, `fs.appendFile*`, `fs.rename*`,
  `fs.rm*`, `fs.unlink*`, `fs.mkdir*`, `workspace.fs.writeFile`, shell redirection,
  or equivalent mutation outside the canonical guarded writer;
- initialization evidence remains separate from contract authority, example
  discovery, and approval;
- every runtime entry point consumes one shared classification result;
- fresh initialized non\-Git consumer is distinct from empty, STTM\-only,
  context\-only, source, Framework, unknown, and multi\-root cases;
- managed marker lists are centralized, never copied;
- no source checkout, `etl-framework-adb`, or absolute development dependency;
- render/normalize/validate/freeze one manifest before Preview;
- Preview creates no proposed consumer files;
- approval/write consume the exact frozen manifest and verify root, hashes, policy,
  expiry/replay, containment, and preconditions immediately before mutation;
- mismatch/drift fails closed and requires a new Preview;
- one Job Config per job, compatible env reuse, canonical includes, HOCON\-safe
  reuse, and explicit path\-vs\-table target types;
- completion evidence includes classifier parity, zero\-write Preview,
  approval\-negative tests, containment tests, and exact VSIX parity when packaged\.

# ================================================== 5\. PATH\-SPECIFIC TEST INSTRUCTION

Create `.github/instructions/etl-test-safety.instructions.md` with exactly:

```yaml
---
applyTo: "src/test/**/*.ts,src/**/__tests__/**/*.ts,test/**/*.ts,tests/**/*.ts"
---
```

The body must require:

- unique test\-owned temporary consumer root per test;
- never use Extension, Framework, home, real consumer, or maintainer `.github/**`
  as a test write target;
- no installed\-user\-extension, personal\-settings, network, source\-checkout, or
  real\-data dependency;
- mandatory classification matrix for fresh initialized non\-Git consumer,
  existing consumer, empty folder, STTM\-only, context\-only, Extension source,
  Framework source, multi\-root, escape attempts, and missing root;
- equivalent typed decisions across all classifier/resolver entry points;
- zero writes during discovery/render/validation/Preview;
- exact Preview/write manifest equality;
- exact approved write succeeds once;
- missing/fake/expired/replayed/cross\-root/path/content/policy/precondition drift is
  rejected;
- write approval does not authorize other operations;
- Job Config uniqueness, env reuse, nested/cycle/missing/traversal include tests,
  unresolved variables, role\-aware fragments, HOCON\-in\-`.yaml`, and path\-backed
  Delta preservation;
- no assertion weakening, skip/quarantine, discovery change, snapshot/baseline
  regeneration, or aggregate\-count\-only historical comparison;
- explicit VSIX verifier and installed fresh\-consumer smoke for packaged behavior\.

# ================================================== 6\. PATH\-SPECIFIC PACKAGE INSTRUCTION

Create `.github/instructions/etl-packaging-safety.instructions.md` with exactly:

```yaml
---
applyTo: "package.json,scripts/**/*.js,scripts/**/*.ts,src/test/verifyVsixContents.ts,resources/framework/contracts/**/*"
---
```

The body must require:

- exact VSIX path as verifier input; never newest\-mtime selection;
- archive, identity, entry\-count/size, and forbidden\-entry verification;
- required trusted contracts present and byte\-equal to source;
- installed\-layout resolution without source, Framework, local examples, or
  absolute development paths;
- consumer context, source tests, temp content, nested Git, and build\-info excluded
  unless explicitly required by package policy;
- normalized entry\-name and decompressed\-byte comparisons, ignoring ZIP timestamps;
- version\-only package has unchanged non\-version bytes;
- packaging never implies permission to install/publish/tag/commit/run QA;
- no modification of tests, contracts, policy, or protected `.github/**` to make a
  package gate pass\.

# ================================================== 7\. VALIDATE THE INSTRUCTION SET

Perform read\-only validation after edits:

1. Confirm all four authorized files exist and are UTF\-8 text\.
2. Confirm both path\-specific files and the package file have valid YAML
   frontmatter and exact `applyTo` values above\.
3. Confirm no `excludeAgent` is present\.
4. Confirm all ten `ETL-INV-01` through `ETL-INV-10` IDs exist exactly once in the
   repository\-wide file\.
5. Search all active instruction sources for direct semantic conflicts concerning:
   workspace classification, consumer authority, Preview mutation, approval,
   destination containment, protected `.github/**`, Framework dependency, and
   test isolation\.
6. Confirm no instruction claims that model guidance alone enforces security\.
7. Confirm the path\-specific files contain details but do not contradict the
   repository\-wide invariants\.
8. Confirm Git diff contains no task\-attributable change outside the four
   authorized paths\.
9. Confirm `package.json`, all `src/**`, all tests, all contracts, workflows,
   settings, and every other `.github/**` path are byte\-unchanged from the initial
   baseline\.
10. Recalculate the `0.3.142` VSIX size and SHA\-256 and confirm that the verified
    artifact remains byte\-unchanged\.
11. Confirm staged file count remains zero\.

Do not run compile or unit tests: no executable source is authorized to change\.

# ================================================== 8\. FINAL REPORT

Return:

REPOSITORY\_ROOT: <value>
ORIGIN: <value>
BRANCH: <value>
HEAD: <value>
SOURCE\_VERSION: <value>
VERIFIED\_VSIX\_PATH: <value>
VERIFIED\_VSIX\_SIZE\_BYTES\_BEFORE: <value>
VERIFIED\_VSIX\_SIZE\_BYTES\_AFTER: <value>
VERIFIED\_VSIX\_SHA256\_BEFORE: <value>
VERIFIED\_VSIX\_SHA256\_AFTER: <value>
VERIFIED\_VSIX\_MODIFIED: YES/NO
STAGED\_FILES\_BEFORE: <number>
STAGED\_FILES\_AFTER: <number>
PRE\_EXISTING\_CHANGED\_PATHS: <complete list>
AUTHORIZED\_GUARDRAIL\_CHANGED\_PATHS: <complete list>
UNAUTHORIZED\_CHANGED\_PATHS: <complete list>
REPOSITORY\_WIDE\_INSTRUCTION\_PRESENT: YES/NO
PATH\_SPECIFIC\_RUNTIME\_INSTRUCTION\_PRESENT: YES/NO
PATH\_SPECIFIC\_TEST\_INSTRUCTION\_PRESENT: YES/NO
PATH\_SPECIFIC\_PACKAGE\_INSTRUCTION\_PRESENT: YES/NO
INVARIANT\_ID\_COUNT: <number>
FRONTMATTER\_VALID: YES/NO
LOCAL\_CLOUD\_PORTABLE\_APPLY\_TO: YES/NO
EXCLUDE\_AGENT\_PRESENT: YES/NO
INSTRUCTION\_CONFLICTS\_FOUND: <number>
INSTRUCTION\_CONFLICTS: <complete list or NONE>
PROTECTED\_GITHUB\_PATHS\_MODIFIED: <list or NONE>
SOURCE\_OR\_TEST\_MODIFIED: YES/NO
PACKAGE\_VERSION\_CHANGED: YES/NO
COMPILE\_EXECUTED: NO
VSIX\_BUILT: NO
EXTENSION\_INSTALLED: NO
RUNTIME\_QA\_STARTED: NO
COMMIT\_CREATED: NO
PUSH\_EXECUTED: NO
READY\_FOR\_GUARDRAIL\_REVIEW: YES/NO
READY\_FOR\_REPAIR\_9\_IMPLEMENTATION: YES/NO

PASS requires:

- correct repository identity and zero staged files;
- exactly the four authorized guardrail paths added/merged;
- all ten invariant IDs present;
- valid portable path\-specific frontmatter without exclusions;
- no unresolved instruction conflicts;
- no changes outside the authorized paths;
- verified `0.3.142` VSIX identity remains unchanged;
- no source/test/version/build/install/QA/commit/push action\.

End exactly with one:

`GUARDRAIL_INSTALL_RESULT: PASS`

`GUARDRAIL_INSTALL_RESULT: BLOCKED_IDENTITY_MISMATCH`

`GUARDRAIL_INSTALL_RESULT: BLOCKED_STAGED_CHANGES`

`GUARDRAIL_INSTALL_RESULT: BLOCKED_TARGET_HAS_USER_CHANGES`

`GUARDRAIL_INSTALL_RESULT: BLOCKED_INSTRUCTION_CONFLICT`

`GUARDRAIL_INSTALL_RESULT: FAIL_UNAUTHORIZED_CHANGE`
