TASK_ID: ETL-0907-BUILD-PROVENANCE-PIN01
TYPE: BOUNDED BUILD, SOURCE-ARTIFACT PROVENANCE AND PINNED-HOST PREPARATION

Run this complete prompt in an ordinary LOCAL Windows VS Code Agent chat in
the active recovery worktree below. Use one Agent and one writer. Do not use
the ETL Orchestrator. Keep code, comments and engineering evidence in English.
Echo TASK_ID as the first line of the final report.

1. Owner authorization and completion boundary

The owner has approved the next bounded step following the independent
POLICY-COVERAGE review: build the reviewed source, establish the origin and
integrity of the required compiled outputs/protected manifest, and inspect the
locally available pinned VS Code 1.135.0 launcher/entrypoint contract.

This task explicitly authorizes compilation and the limited generated-output
writes described below. The previous source-only tasks’ no-emit restrictions
do not prohibit this newly authorized build. Their source-edit permissions
are not carried forward.

Allowed work:

1. Read-only identity, source, configuration, dependency, process, path and
evidence inspection; raw-byte copying/hashing and strict JSON parsing.
2. Run the existing installed TypeScript compiler for a checked build. Use
task-owned scripts and staging/evidence under one fresh external task root.
3. Create or update only the necessary compiler-generated files under the
active worktree’s out/ directory, through the recorded promotion set in
section 5. Keep all source and repository configuration unchanged.
4. Generate build-provenance evidence and a protected-manifest artifact using
the bounded routes in section 7. Those routes do not authorize a test run.
5. Inspect actual local VS Code 1.135.0 artifacts and launcher code read-only.

Not authorized:

• Source, test, policy, dependency, configuration, package/lock-file or version
edits; Git mutations; modifying earlier evidence or reference documents.
• Saving/reverting/reloading pending editor buffers, Keep/Undo, changing
autosave, restoring historical source, terminating processes or deleting locks.
• Executing tests, the ordinary test runner, producer, launcher, Extension
Host, extension activation, product parser/workflow or real consumer jobs.
• npm/npx lifecycle scripts, installs, upgrades, downloads, VSIX packaging,
extension installation, publication or release; network/credential access.
• Deleting/cleaning out/, emitting into the linked primary, modifying build
caches/build-info, copying arbitrary old JavaScript or patching emitted code.

Compilation may read project modules as compiler input. It must not import
or execute their runtime code. The sole narrowly conditional project-code
execution exception is an existing manifest-only entrypoint under section 7.

Carry all authorized work through to measured results. A missing pinned Host
does not prevent the independent compilation/provenance work. Preserve any
partial result and identify remaining blockers; do not claim Host readiness
or automatically launch the next phase.

2. Exact workspace and governing evidence

ACTIVE_WORKTREE:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

LINKED_PRIMARY (identity/read-only boundary):
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch: fix/workspace-write-completion-0.3.148
Expected HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
Expected staging: empty.

POLICY_REPAIR_ROOT (one literal flat directory name):
C:\docs\ETL-0907-POLICY-COVERAGE-REPAIR01-20260907T183624221Z-9f1d6a42-6614-4025-a029-2590da4a0b5f

CONTRACT_REVIEW_ROOT:
C:\docs\ETL-0907-F5-CONTRACT-INDEPENDENT-REVIEW01\20260907T175437Z-73509E6F-9589-44BB-8A8F-150986769864

CONTRACT_REPAIR_ROOT:
C:\docs\ETL-0907-F5-CONTRACT-REPAIR01\20260907T112539Z-559ABD3C-A873-4D54-8EF0-BC72D38F2403

CURRENT_POLICY_REVIEW_TASK:
ETL-0907-POLICY-COVERAGE-INDEPENDENT-REVIEW01

Resolve the actual completed policy-review root from the supplied review.md
location. If no absolute location is supplied, bounded discovery of direct
C:\docs children named ETL-0907-POLICY-COVERAGE-INDEPENDENT-REVIEW01* is
authorized, including one timestamp child if the named task container exists.
Validate report contents, TASK_ID, reviewed POLICY_REPAIR_ROOT, final source
identity, decision and correction/supersession links. Do not invent a GUID,
select a directory merely by newest timestamp, or substitute the older
CONTRACT review for the policy review. If matching reports disagree or the
authoritative completed result cannot be established, report the exact gap.

Read the complete current review.md, its decision, incident/recovery findings,
identity and preservation records, and its machine-generated corrections.
Read POLICY_REPAIR_ROOT/report.md, baseline/post-state, exact diff, relevant
pre/post copies and policy-coverage records. The screenshot summary reports
no blockers for the source-policy gate and verified incident recovery; verify
that against the actual completed report before building.

The reviewer disclosed corrupt manual transcriptions of FIVE hashes in its
own first-pass evidence (late finding F-9). Resolve the TWO actual superseding
machine-measured files from its report/index/correction links; do not guess
their names. Preserve the first-pass files as history. Programmatically read
the corrected full hashes and cross-check originals/live bytes. A new
measurement by itself is not an authenticated expected baseline, and a later
correction that merely repeats a claim is insufficient.

Read applicable repository instructions and the complete governing glossary:
C:\docs\ETL_QUALIFICATION_GLOSSARY.md
Record actual paths and hashes. Read any supplied current navigation/state
files; if unavailable, leave broader state completeness UNKNOWN. This brief
supplies the bounded build authorization, not missing release acceptance.
Do not search Local History, debug logs, unrelated folders or network storage.

3. Preflight and immutable input capture

Use git –no-optional-locks for reads. Verify worktree/common-Git identity,
branch, HEAD, empty staging and this complete existing dirty inventory:

```text
 M .github/templates/request.md
 M src/core/sttm/SttmUnderstandingReportRenderer.ts
 M src/extension.ts
 M src/test/runTest.ts
 M src/test/suite/index.ts
?? src/test/b3OutcomePolicy.ts
?? src/test/b3OutcomePolicy.unit.test.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts
```

Inspect applicable locks and actual process arguments for a concurrent writer,
compiler/watcher, test/development Host or launcher. Ordinary editor/language
server processes alone are not prohibited Hosts. Do not stop or reconfigure
anything. An actual concurrent writer or unexplained source drift blocks
repository output promotion; do not normalize it away.

These are cross-check counts, not substitute hash pins:

|Current source                       |Bytes |CRLF|Bare LF|Bare CR|
|-------------------------------------|-----:|---:|------:|------:|
|src/test/runTest.ts                  |131240|0   |2970   |0      |
|src/test/b3OutcomePolicy.ts          |35970 |809 |0      |0      |
|src/test/b3OutcomePolicy.unit.test.ts|36595 |758 |0      |0      |
|src/test/suite/index.ts              |10408 |246 |0      |0      |

Authenticate runTest.ts against the completed policy review, repaired
post-state and independent baseline-plus-insertion proof where needed. The
131123-byte source is the preceding baseline; 131713/136657-byte sources and
Snapshot01 are not current build inputs. The unavailable 126214-byte reviewed
source remains a historical limitation, not a prerequisite to reconstruct.

Validate every SHA-256 field as 64 hexadecimal characters before comparison.
Extract expected values programmatically from original machine records/full
saved tables. Do not type hash constants into helpers or transcribe photos.
Record raw hash, size and parse status of consumed evidence. Preserve malformed
older JSON; use the explicitly documented original source copies and complete
identity tables as alternative anchors when corroborated. Never silently
repair original evidence or attribute new drift to the old editor incident.

After creating the external task root, capture and verify immutable copies of
all first-party compiler inputs, resolved configuration, runtime assets needed
by this build, and preservation inputs. Retain hashes for actual compiler/
toolchain modules and external type/dependency inputs used by the build. A
complete compiler read-set inventory is preferable to guessing dependencies.

Record versions/paths from the installed tools; prior observations were Node
20.19.5 and TypeScript 5.9.3. Establish their current identities from local
artifacts and prior records; do not install a replacement. Unexpected changes
must be reconciled before trusting the build.

Capture a per-file raw-hash inventory of existing out/**, configured build
outputs, build-info, relevant dependencies/configuration, all pre-existing
dirty files and every prior evidence file consumed. The previous out inventory
was 2016 files; the actual intake inventory governs this build after review
anchor reconciliation. Record absent, empty and inaccessible paths distinctly.

Read source bytes from disk through a controlled compiler host, not editor
buffers. Retain/hash the same input bytes actually supplied to the compiler;
cache each captured input for consistent repeated reads and reject any
observed conflicting version. Recheck source/configuration identities before
promotion and at task end.

4. Exclusive external task root

Validate C:\docs as an existing safe parent with no unsafe reparse/redirection.
The fresh root must be outside both worktrees, all old evidence/snapshots,
profiles and consumer/protected paths.

Create one flat leaf:
C:\docs\ETL-0907-BUILD-PROVENANCE-PIN01-<UTC-timestamp>-<GUID>\

Use creation that fails if the leaf exists. A check followed by
Directory.CreateDirectory is insufficient. After parent validation, the
following installed-Node helper is authorized:

```js
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const taskId = 'ETL-0907-BUILD-PROVENANCE-PIN01';
const utc = new Date().toISOString().replace(/[-:.]/g, '');
const root = path.join('C:\\docs', `${taskId}-${utc}-${crypto.randomUUID()}`);
fs.mkdirSync(root, { recursive: false });
const receipt = {
  taskId, root, createdAtUtc: new Date().toISOString(),
  mechanism: 'fs.mkdirSync', recursive: false,
  result: 'CREATED_BY_SUCCESSFUL_MKDIR', pid: process.pid
};
fs.writeFileSync(path.join(root, 'creation-receipt.json'),
  JSON.stringify(receipt, null, 2) + '\n', { encoding: 'utf8', flag: 'wx' });
process.stdout.write(JSON.stringify(receipt) + '\n');
```

Use literal shell input, such as a single-quoted PowerShell here-string to
Node stdin. Preserve backticks/dollar signs without interpolation. Retain
invocation, output and actual execution-tool completion status. On collision
or failed receipt, preserve partial evidence and stop; do not choose another root.

Use exclusive new-file/copy semantics for task evidence and staging. New JSON
must be strict, BOM-free UTF-8. Keep failed/intermediate artifacts under their
original names; write any correction separately with explicit supersession.
Never hand-transcribe a measured hash or fabricate a successful process exit.

5. Freeze the exact build and promotion plan

Before any compilation, read tsconfig.json and its complete resolved extends/
references, package build scripts as text, the current canonical protected
policy, source/artifact mapping, and runtime imports. Do not execute package
scripts or infer build settings from a standalone tsc invocation on one file.

Build from the repository’s established TypeScript configuration and installed
compiler. Do not change target/module/resolution options, add custom transforms,
suppress diagnostics, change the pin or weaken manifest checks to obtain success.

Derive the runtime build set from:

• Every JavaScript artifact in the authenticated PROTECTED_POLICY_PATHS.
• The runner, producer, focused suite and extension entrypoints used by the
existing focused-run contract, including out/test/runTest.js,
out/test/suite/index.js and out/extension.js.
• Their necessary first-party runtime dependencies and the exact focused
suite file selected by the existing constants, resolved from actual source.

Resolve imports and compiler-emitted runtime helpers without loading the
modules. Distinguish type-only dependencies from runtime files. For computed
loads, inspect the bounded focused selection and document its actual target;
do not execute broad test discovery. If a necessary runtime dependency cannot
be established, report it rather than silently declaring the closure complete.

The new out/test/b3OutcomePolicy.js must be built together with the current
runner and producer. Compiling only that helper while leaving stale runner or
producer JavaScript does not complete this task.

Freeze build-plan.json before emission and promotion-plan.json after staging
but before repository writes. Record exact source paths and identities,
resolved compiler options, logical destinations, required runtime assets,
dependency reasons, and proposed output actions.

Permitted repository output set:

• Compiler-emitted artifacts under ACTIVE_WORKTREE/out/ belonging to this
proven runtime set, with their compiler-generated source maps and declaration
companions when the unchanged configuration emits them.
• Necessary first-party JSON/data files under out/ only when required by this
runtime set and emitted/copied by the documented existing build contract;
record their original source and exact-byte provenance.

Compilation may stage the whole configured program under the external task
root to obtain a correct checked emit. This does not authorize promoting all
staged files. Other tests, unrelated outputs and packaging/resources outside
out/ stay unchanged. The unit-test artifact is not a runtime dependency merely
because its name starts with b3OutcomePolicy; do not promote it on that basis.

package.json is an existing protected input, not a generated output to edit.
The canonical protected membership is reported as 12 files and 11 derived
TypeScript relations; derive the exact list from current source, not a typed
replacement list. Do not expand/reduce that policy during the build.

No project-owned output outside out/, cache/build-info update or source/config
change is authorized. If the existing build needs one, identify the exact
coupling and smallest additional operation. Do not quietly substitute a
different build pipeline or partially promote an incomplete required set.

6. Checked staging build and bounded promotion

Use the installed TypeScript Compiler API in a task-owned helper with the
configuration resolved by TypeScript itself. Resolve the compiler by its
absolute path inside ACTIVE_WORKTREE/node_modules; do not fall back to a global
compiler or npx. Create a normal checked Program;
collect configuration, syntactic, global, semantic and emit diagnostics. Do
not substitute transpileModule for the checked runtime build.

Preserve the original logical rootDir/outDir and output paths. Redirect all
physical compiler writes through an explicit writeFile callback into the new
task staging tree. This retains the compiler’s logical source-map layout while
preventing premature repository writes. Verify each emitted logical path is
within the allowed configured output root and each staged physical path is
inside TASK_ROOT. Handle writeByteOrderMark as the compiler requests; the
BOM-free requirement applies to task JSON, not arbitrary alteration of compiler
output. Preserve every emitted byte without post-processing.

Use noEmitOnError=true. Disable incremental/build-info persistence in the
task-owned invocation where compatible with the actual configuration; do not
edit tsconfig.json. If composite/project references require a different build
mechanism or persistent writes that this boundary cannot preserve, report
the concrete coupling rather than changing semantics. Never fall back to
default filesystem writes when a redirected write is rejected.

Retain compiler/helper identity, resolved options, actual input read-set,
diagnostics, emitted-file inventory, stdout/stderr and real process status.
Error diagnostics, emitSkipped, failed writes or missing required outputs
prevent promotion. Empty logs alone are not proof of success. Preserve failed
attempts; repair only task-owned build helpers when necessary, never repository
source. No repeated successful build or extra test run is required.

Before promotion:

1. Verify the complete required staged set, its hashes and source associations.
2. Parse/check source-map references against the unchanged logical destinations;
do not relocate maps blindly or manually rewrite emitted code/maps.
3. Inspect staged JavaScript as data to confirm both runner/producer imports
resolve to the same required policy artifact and the compiled runner carries
the current canonical membership. Do not require/import these modules.
4. Recheck all build inputs against the captured compiler bytes, repository
identity, locks/process arguments and planned destination pre-hashes.
5. Record exact CREATE / REPLACE / IDENTICAL actions in promotion-plan.json.

Promote only the frozen necessary set, copying the unchanged staged bytes to
their exact logical destinations under ACTIVE_WORKTREE/out/. For each replaced
file preserve and verify its exact pre-copy first; for absent destinations use
exclusive creation. Validate containment/redirection for destination parents.
Skip writes for byte-identical destinations. Verify each write by raw read-back
hash and retain an ordered promotion journal.

Do not clean stale files, regenerate unrelated output or use Git to restore
anything. On source/destination drift, failed promotion or an unexpected write,
stop further promotion and preserve the partial state with an exact journal.
Do not label it complete or attempt an unrecorded cleanup/rollback.

7. Establish provenance and produce the protected manifest

For every required runtime output and every canonical protected artifact,
record its final raw hash/bytes, originating source hash, compiler/configuration
identity, staged hash and promoted hash or demonstrated byte-identical status.
Confirm all 11 TypeScript-to-artifact relations against actual compiler inputs
and outputs. Hash package.json as the unchanged direct protected input.

Report source-to-output provenance separately from the protected-files digest:
a digest over files that happen to exist does not prove those files were built
from the reviewed source. Do not bless stale artifacts by simply hashing them.
Include required runtime dependencies outside the protected policy in the
build provenance without silently adding them to the canonical policy.

Read the actual generateProtectedHashManifest, buildProtectedRecordsFromPolicy,
buildSourceArtifactRelations, readProtectedHashManifest, digest routine and
their call sites. Determine the real schema and whether a safe existing
manifest-only entrypoint is available. Do not invent a command-line flag or
environment variable based on a function name.

Route A — existing manifest-only entrypoint:
Execution of that existing route is authorized only after static inspection
establishes that all reachable top-level initialization/imports and the selected
branch remain within this task’s read/write boundaries, that the route returns
before the ordinary test/Host flow, and that it cannot launch/download a
Host or write old/consumer evidence. Retain the exact branch and invocation
proof before executing it. Direct its new manifest into TASK_ROOT using the
existing supported mechanism. Do not patch the entrypoint, mock out launch,
monkey-patch process/child_process, or rely on a hoped-for early error.

Validate the result through an equally bounded existing reader if available.
Check actual file hashes, current canonical membership/order, derived source
relations, counts and the existing digest algorithm. Record precisely which
canonical code executed. No other runner/producer/launcher execution is allowed.

Route B — no proven safe manifest-only entrypoint:
Complete build-provenance.json and generate protected-manifest.candidate.json
under TASK_ROOT from the canonical declarations/schema read as data and the
actual built-file hashes. A task-owned data-only serializer/checker may compute
the exact documented digest and relations; retain its source and source-symbol
mapping. Label this artifact BUILD_CANDIDATE, with canonical runtime-reader
acceptance NOT_EXECUTED. Do not claim it is runner-generated or runtime-validated.
If required run-bound fields cannot legitimately be established in a build
task, leave the candidate explicitly incomplete instead of fabricating them.

Route B is an authorized useful fallback, not a second repository policy
implementation and not closure of canonical manifest integration. Record the
smallest remaining manifest-validation requirement for the next task. Do not
execute the whole runner merely to avoid this limitation.

Neither route grants a future run freshness/authorization. Preserve any
existing per-run isolation, dedicated-directory, nonce and manifest rules.
The later Host task must create its own fresh run evidence and regenerate or
consume a manifest exactly as the established contract permits. Do not create
fake test results, success rows, authorization markers or run completion data.

8. Inspect the pinned VS Code 1.135.0 contract

Read EXPECTED_VSCODE_VERSION, executable resolution and installed
@vscode/test-electron launcher code, including the effective local path inputs.
Inspect only the named environment values used by that resolution; do not
dump the whole environment or access credentials.

Use bounded lookup of paths identified by the current code and retained
evidence, plus the repository’s existing test-binary cache if present. Do not
search all drives, download a distribution, install an extension or replace
the user’s ordinary VS Code. An installed 1.136.1 build is not a substitute.

For an actual local 1.135.0 candidate, record its canonical path, platform/
architecture, package/product metadata, executable and relevant entrypoint
hashes, and available local distribution provenance. A version label alone
does not establish binary origin. Do not execute Code.exe, code.cmd, its CLI,
test-electron, a launcher or an Extension Host in this task.

Inspect the actual pinned build’s extension-test entrypoint and installed
launcher’s settlement/exit handling. Verify the relevant static contract:

• Completed focused result delivery can settle normally even when counted
test failures exist; the parent still derives FAIL from trustworthy evidence.
• Launcher rejection/abnormal Host termination remains a distinct infrastructure
cause; the producer result does not suppress it.
• The future focused run can select the exact pinned executable without a
fallback to another installation or an automatic download.

Cite the exact local source/artifact and distinguish static inspection from
runtime proof. Do not generalize the 1.136.1 implementation to the pinned build.
If 1.135.0 is absent, inaccessible, uncorrelated or the contract cannot be
verified, record that outcome and finish any independently completable build
work. Do not change the version pin or relabel the result as ready for Host.

9. Final verification, evidence and result

Verify all source/configuration/dependency inputs and prior evidence consumed
remain unchanged. Compare the complete before/after out/ inventories: every
change must appear in the promotion journal; every non-promoted file must be
byte-identical; no deletions or unexplained files are allowed. Build-info and
other output roots remain unchanged. HEAD, branch, staging and existing source
dirty inventory must be preserved; report any actual unexpected difference.

Keep a compact complete evidence set, with additional raw captures only as
needed:

• report.md, baseline.json, post-state.json, creation-receipt.json;
• review-anchor-resolution.json and immutable measured input copies;
• build-plan.json, compiler helper, resolved options and input read-set;
• raw command/tool results, diagnostics, emitted-file inventory and staged bytes;
• promotion-plan.json, pre-output copies and ordered promotion journal;
• build-provenance.json, before/after per-file output inventories;
• protected manifest or explicitly labeled candidate and validation evidence;
• pinned-host-inspection.json and preservation checks.

All measured hashes, counts and status fields must be populated from actual
operations. Strictly parse new JSON after serialization. Preserve any failed
artifact and write a separately named correction with machine-derived values.
Do not manually transcribe hashes into summaries or hard-code process success.

Use these report fields, with one actual result:

```text
TASK_ID: ETL-0907-BUILD-PROVENANCE-PIN01
RESULT: BUILD_AND_PROVENANCE_COMPLETE_AWAITING_HOST_AUTHORIZATION |
        BUILD_COMPLETE_WITH_REMAINING_GATE_BLOCKERS |
        BLOCKED_<CONCRETE_REASON> | INCOMPLETE_PARTIAL_PROMOTION
SOURCE_POLICY_REVIEW: <actual report path, decision and corrected anchors>
SOURCE_IDENTITY: <machine-derived identities and stability>
COMPILER_AND_CONFIGURATION: <actual versions, hashes and options>
BUILD: <exit status, error/warning counts, emit result and raw logs>
REQUIRED_RUNTIME_SET: <exact list and closure evidence>
OUTPUT_PROMOTION: <created/replaced/identical counts and exact journal>
SOURCE_ARTIFACT_PROVENANCE: <verified relations and unresolved gaps>
PROTECTED_POLICY: <observed membership, relation count and actual digest>
PROTECTED_MANIFEST: <path, route A/B, schema/completeness/validation status>
PINNED_VSCODE_1_135_0: <actual path/identity or precise unavailable state>
PINNED_ENTRYPOINT_CONTRACT: VERIFIED_STATICALLY | UNRESOLVED | UNAVAILABLE
REPOSITORY_SOURCE_CONFIG_OR_DEPENDENCY_CHANGED: NO
PRIOR_EVIDENCE_CHANGED: NO
OUT_OF_PLAN_OUTPUT_CHANGED: NO
ORDINARY_RUNNER_FLOW_PRODUCER_LAUNCHER_OR_HOST_EXECUTED: NO
MANIFEST_ONLY_ENTRYPOINT_EXECUTED: <exact permitted route or NO>
TESTS_EXECUTED: 0
GIT_MUTATION_INSTALL_DOWNLOAD_PACKAGE_OR_RELEASE_EXECUTED: NO
HISTORICAL_REVIEWED_BASELINE_PRESERVATION: NOT_VERIFIED
FULL_B3_OR_RUNTIME_QUALIFICATION_GRANTED: NO
REMAINING_GATE_BLOCKERS: <specific unresolved items or NONE>
NEXT_STEP_PROPOSED_ONLY: <minimum remaining preparation or focused Host task>
REPORT_PATH: <absolute path under this task root>
```

The first result requires a checked successful build, complete required-output
provenance/promotion, canonical manifest generation/validation evidence, pinned
local identity/static contract, and preserved boundaries. A candidate-only
manifest or unavailable/unverified pin belongs in the second result when the
build itself is complete. Never conflate build success with successful tests.
If an unexpected action occurred, replace the corresponding NO with the truth.

Stop after delivering the result. The next separately authorized task must
verify these records before its focused Host run; this prompt does not launch
that run. Do not reopen accepted source repairs without a concrete new defect
or add another round of successful unit tests merely to accumulate evidence.

Give a short chat summary with the exact report path, build outcome, promoted
file counts, manifest status, pinned-version status and remaining blockers.

Technical references for the staging design

These references explain compiler capabilities; they are not permission to
install anything or override the project’s actual local compiler/configuration.

• TypeScript Compiler API: Program, CompilerHost and redirected writeFile
• TypeScript noEmitOnError
• TypeScript sourceMap
