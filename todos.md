# ETL\-0910\-REPORT\-CORRECTION\-VSIX\-PREP01

TYPE: REPORT CORRECTION ADDENDUM \+ BOUNDED VSIX PREPARATION
ENVIRONMENT: Windows, normal local VS Code development Agent, existing ETL
Extension development worktree\. Do not use the ETL Orchestrator or a consumer
ETL workspace\. This task concerns ETL Extension, not Universal Coding Agent\.

Echo `TASK_ID: ETL-0910-REPORT-CORRECTION-VSIX-PREP01` as the first line of your
report\. Speak Persian with Hesam; write technical artifacts in English\.

## 1\. Owner authorization and required outcome

The owner authorizes this bounded next step:

1. Reconcile R1 and R2 from `ETL-0910-WORKFLOW-GITIGNORE-DISCLOSURE-REVIEW01`
   in a new evidence\-backed addendum, preserving all original reports and logs\.
2. Verify the exact current extension identity and package inputs\.
3. If the prerequisites below pass, run the existing supported build/package
   procedure and produce one traceable private VSIX candidate\.
4. Inspect that VSIX’s identity and contents and report preparation status\.

Complete all authorized work without asking again for routine confirmation\.
This is preparation for later installed\-product testing\. It authorizes no
installation, activation, Extension Development Host launch, live smoke, consumer
workflow execution, publishing, release, commit, push or merge\. A prepared package
is not installed\-product or release acceptance\.

Do not repair product/test source in this task\. If a prerequisite fails, preserve
the evidence, report the concrete blocker and identify the smallest follow\-up;
do not change source, weaken a gate or describe an unbuilt candidate as prepared\.

## 2\. Read actual records and pin the worktree

Read the applicable AGENTS\.md/instructions, current local ETL orientation/state
and approved build/package guidance\. Find the following existing evidence bundles
through the current workspace references and the recorded `C:\docs` evidence
locations, without a whole\-machine search:

- `ETL-0910-WORKFLOW-GITIGNORE-DISCLOSURE-REVIEW01`\.
- Its reviewed `ETL-0910-WORKFLOW-GITIGNORE-DISCLOSURE-FIX01` bundle\.
- The exact BOOTSTRAP01 post\-state and `ETL-0909-REVIEW01` records referenced by
  those bundles, as needed to verify their claims\.

Read complete `report.md`, `result.json`, manifests, `task-diff.patch`, pre\-copies
and the relevant retained red/green logs where present\. Resolve bundle names to
their exact recorded paths; do not pick a bundle merely because it is newest\.
Screenshots and this prompt are navigation, not substitutes for machine records\.

The submitted review reports these observations, which you must recheck from disk:

- Branch: `fix/workspace-write-completion-0.3.148`\.
- HEAD begins `45c945b4`; obtain the full SHA from the actual records and Git\.
- Zero staged paths and 23 dirty paths: 16 modified and 7 untracked\.
- The pre\-existing `.github/templates/request.md` change is unresolved\.
- The existing `out/` inventory was reported as 2020 files\.
- The reviewed fix changed only:
  `src/customization/CopilotWorkflowCommands.ts` &#40;\+4/\-1&#41; and
  `src/test/suite/workflowEmptyProjectBootstrap.test.ts` &#40;\+47/\-3&#41;\.

Both fix files were already dirty before FIX01\. Verify their pre\-copy \-\>
BOOTSTRAP01 \-\> FIX01 \-\> current\-byte chain against recorded hashes\. Do not use
HEAD as their pre\-edit baseline or infer equivalence from line counts alone\.
Record actual repository root, branch, full HEAD, status, relevant hashes and
package\-input inventory before any generated output is written\.

Reconcile any actual advancement against its approved records\. Do not reset,
checkout over, stash, clean, delete, normalize or silently absorb unexplained
changes\. If the reviewed source or other relevant package inputs have unexplained
drift, finish the factual addendum where possible and block build/package until
the actual baseline is resolved\. Do not claim concurrent writers were excluded
solely because two hashes match; report the observation method and its limits\.

## 3\. Correct R1 and R2 without rewriting history

Create a new uniquely named evidence directory using CreateNew semantics outside
both development and consumer worktrees, under the established `C:\docs` evidence
root if that is the verified location\. Include this TASK\_ID and the actual UTC
timestamp\. Keep original FIX01/REVIEW01 reports, logs and result files unchanged\.

Write `report-correction-addendum.md` with references to the exact original claims
and the source/log evidence supporting each correction:

### R1 — red\-run assertion coverage

FIX01 section 4\.1 claims the root, catalog\-path and `filesAtPrompt` assertions all
preceded the disclosure assertion and passed in the red run\. The review found
`filesAtPrompt` after the failing disclosure assertion; Mocha therefore never
reached it in that run\. Verify the actual ordering and correct the claim\.

The retained red result is 12 passing / 1 failing, with the new disclosure case
failing\. The retained green result is 13 passing / 0 failing\. The passing green
case supports the later assertion; it does not retroactively establish that
assertion was executed in the red run\. Preserve the valid earlier root/catalog
observations with their proper scope\. Do not rerun tests to replace old evidence\.

### R2 — adjacent\-suite failure classification

The retained adjacent\-suite results show 50 passing / 4 failing in both runs\.
Inspect each failure’s actual detail\. The review identifies items 1, 2 and 4 as
external\-build\-lane `repoRoot` resolution failures &#40;`ENOENT`&#41;; item 3 is a plain
assertion failure\. Correct the unsupported “three historical failures plus one
lane artifact” characterization\.

The earlier 51 passing / 3 failing baseline was declared without retained output
&#40;U\-1&#41;\. Do not authenticate its historical attribution from equal totals, titles,
or later results\. The adjacent suite remains NOT GREEN\. Cases failing on path
resolution before product behavior provide no product regression signal\. State
the narrower evidence from relevant passing Initialize cases and the reviewed
small product diff; do not generalize it into full regression qualification\.

Keep both corrections as reporting corrections, not new source defects\. Retain
`ACCEPTED_WITH_LIMITATIONS` for the bounded reviewed delta\. Historical exit codes
remain unauthenticated where no record was retained; empty stdout/stderr does
not prove success\. Do not reconstruct deleted red/green build trees\.

## 4\. Resolve extension identity and the supported package recipe

Read the actual `package.json`, lockfile, VSIX packaging configuration, applicable
scripts, compiler/bundler configuration and existing delivery instructions\.
Record publisher, extension name/ID, version, engine constraints, entrypoint,
Node/package\-manager/compiler/packager versions and the chosen exact commands\.

Do not assume version `0.3.148` from the branch name\. Do not change version,
publisher, extension ID, manifest, lockfile, scripts or package exclusions\. If the
repository has a documented version consistency rule, verify it as written; do
not invent one requiring every dependency’s version to equal the extension’s\.
The established expected extension ID has been `td-etl.databricks-etl-copilot`;
resolve its current value against accepted local records and report any mismatch\.

Inspect lifecycle/prepublish hooks before execution\. Use the installed approved
toolchain and existing dependencies\. No dependency installation/update, network
tool download, unpinned `npx`, environment creation, custom packaging replacement
or bypass flag is authorized\. If required tooling or a mandatory gate is missing,
record that blocker rather than modifying policy or masking a failure\.

Prepare a manifest of actual package inputs, including relevant dirty/untracked
source and resource files\. A VSIX built from a dirty worktree is identified by
these actual inputs plus HEAD; HEAD alone does not describe its bytes\. The narrow
Initialize review does not independently accept all other included worktree
changes\. Carry their approval/evidence scope and unknowns explicitly\.

## 5\. Build and package once under the existing recipe

Use the verified repository root as the working directory for its existing
commands\. Do not invent an external test/build lane with different `repoRoot`
semantics\. Execute only the required supported build/typecheck/package steps
whose effects fit this task\. Inspect transitive hooks as well as top\-level scripts\.

Allowed writes:

- New reports, manifests, command logs and one candidate VSIX in the new task
  evidence directory outside repository and consumer roots\.
- Documented generated compiler/bundler outputs required by the approved recipe,
  such as the actual configured `out/` paths, after preserving their affected
  before\-images and inventory\. These are build outputs, not permission for source
  edits or broad output\-directory cleanup\.

Preserve existing generated outputs that the build would overwrite before
running it\. Do not remove the existing `out/` tree, reconstruct deleted historical
trees, or overwrite a previous VSIX/evidence bundle\. Use an explicit unique VSIX
destination when the supported packager permits it\. If the recipe cannot operate
within these boundaries, report the exact blocker; do not silently improvise\.

Retain each command’s exact working directory, arguments, UTC start/end, stdout,
stderr and captured exit code\. A failed required build prevents packaging; a
failed package attempt is retained as failed\. Do not take an older build or VSIX
as the result of this task\. No repeated run or repair loop to manufacture a pass\.

Do not rerun BOOTSTRAP01, historical red/green tests or the known adjacent suite
in this task\. Do not launch VS Code/Extension Host or execute generated consumer
workflows\. If a mandatory repository package gate requires an excluded action,
record it as an unresolved prerequisite instead of skipping or disabling it\.

## 6\. Inspect the produced VSIX as an archive

Without installing or activating it, verify:

- The artifact exists, is readable, and has a recorded absolute path, byte size
  and SHA\-256\.
- `extension.vsixmanifest` and the packaged `extension/package.json` identify the
  same expected publisher/name/version as the verified package inputs\.
- The declared entrypoint exists; the packaged compiled command module matches
  the fresh build output by hash and includes the Initialize disclosure change\.
  A string search alone is not proof of correct build provenance\.
- Required workflow/catalog assets and runtime resources are included at their
  expected paths and match the intended inputs\. Preserve the reviewed Base
  profile’s eight\-asset catalog; do not describe managed `.gitignore` as a ninth
  catalog asset\.
- The package obeys the actual approved inclusion/exclusion configuration and
  contains no accidentally included task evidence, local state, consumer outputs,
  repository history or credential files\. Inspect by names/hashes; do not expose
  credential contents in logs\.
- Source/test/manifests/lockfile/control\-plane bytes remain unchanged after the
  build\. Explain each changed generated\-output path against the approved recipe\.

Use existing archive and inspection tools\. Do not put new JavaScript test or
product\-helper files under `docs`\. The permanent regression test remains in
`src/test/suite/workflowEmptyProjectBootstrap.test.ts` and is not replaced with an
ad hoc evidence script\. Reports and raw evidence may live in the task directory\.

## 7\. Retain limitations and report separate evidence states

Carry these limitations forward without closing them in this task:

- F\-1 is closed for Initialize only\. Repair and Upgrade still have the reported
  disclosure gaps; do not modify or qualify them here\.
- F\-2 through F\-5, U\-1 and U\-2 remain open as defined by their original records\.
- The 2026\-09\-09 Host PASS used pre\-fix sources and does not cover this delta\.
- The post\-fix modal has not been observed rendered; its layout/scroll visibility
  and installed behavior are unverified\.
- Base profile / single\-root evidence does not establish other profiles or
  multi\-root readiness\.
- The pre\-existing `.github/templates/request.md` editor change remains unresolved\.

Write `report.md`, `result.json`, input/output manifests and raw logs in the new
evidence directory\. In the final report, distinguish these fields:

|Field                       |Required meaning                                                   |
|----------------------------|-------------------------------------------------------------------|
|REPORT_CORRECTIONS          |R1/R2 corrected with traceable evidence, or exact unresolved reason|
|SOURCE_BASELINE             |Actual root/branch/HEAD plus relevant dirty-source hashes          |
|VERSION_IDENTITY            |Observed extension publisher/name/version and consistency verdict  |
|BUILD                       |Actual command and captured exit code, or NOT_EXECUTED             |
|VSIX_PACKAGE                |Actual artifact path/bytes/SHA-256, or NOT_PRODUCED                |
|PACKAGE_CONTENT_VERIFICATION|Verified members/hashes and result, or NOT_EXECUTED                |
|RETAINED_TEST_EVIDENCE      |Historical 13/0 focused result; adjacent 50/4 remains NOT GREEN    |
|INSTALLATION                |NOT_EXECUTED                                                       |
|ACTIVATION                  |NOT_EXECUTED                                                       |
|POST_FIX_HOST_SMOKE         |NOT_EXECUTED                                                       |
|RELEASE_ACCEPTANCE          |NOT_GRANTED                                                        |

Use `VSIX_PREPARED_WITH_LIMITATIONS` only if identity, required build, packaging,
content inspection and source\-preservation checks actually pass\. Otherwise use
`BLOCKED` with the exact failed/unexecuted stage\. Never label the whole product
GREEN based on preparation or the narrow disclosure review\.

Return a concise Persian explanation plus the exact evidence/artifact paths\.
The next conditional gate is a separately bounded installation/activation and
Initialize\-only post\-fix smoke using this exact VSIX; it has not been executed or
qualified by this task\. Do not perform it automatically\.
