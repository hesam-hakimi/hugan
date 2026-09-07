TASK\_ID: ETL\-0907\-POLICY\-COVERAGE\-INDEPENDENT\-REVIEW01
TYPE: INDEPENDENT SOURCE\-ONLY REVIEW OF POLICY COVERAGE, INCIDENT RECOVERY AND EVIDENCE

Run this complete prompt in a fresh ordinary LOCAL Windows VS Code Agent chat,
with a reviewer independent of the Agent that implemented POLICY\-COVERAGE\-REPAIR01\.
Use one reviewer and one evidence writer\. Do not use the ETL Orchestrator\.
Keep engineering reports and evidence in English\. Echo TASK\_ID as the first
line of the final report\.

## 1\. Authorization and review boundary

The owner authorizes this independent review of the completed bounded repair\.
Assess its current source correctness, immediate\-baseline preservation, the
disclosed stale\-editor\-buffer incident and recovery, path reconciliation, and
the reliability of the supporting evidence\. Produce a concrete acceptance or
blocking decision for this source\-policy gate only\.

No repository edit or repair is authorized\. All existing source, compiled
output, configuration, prior evidence, editor buffers and Git state are
read\-only\. The only permitted writes are new review evidence under the fresh
exclusive review root specified in section 4\.

Allowed: read\-only source/status/process\-argument/path inspection, raw\-byte
hashing and comparison, strict JSON parsing, and task\-owned data\-only analysis
using the already installed PowerShell/Node tools\. Read TypeScript as text or
data; do not import, evaluate or execute project modules to obtain policy data\.

Not authorized: source fixes, evidence repairs, restoring any pre/post copy
over live source, applying task\.diff, running the supplied recovery or capture
scripts, Keep/Undo/save/revert/reload actions, resolving pending editor changes,
changing autosave settings, process termination, lock deletion, Git mutation,
type\-checking, compilation, transpilation, tests, runner/producer/launcher or
Extension Host execution, lint/format/watch, package scripts, installations,
downloads, packaging or release\. Do not perform a build or manifest generation\.

The repair brief is reproduced verbatim in Appendix A as the contract being
reviewed\. Its old implementation permissions are historical, not permissions
for this review\. Sections 1\-10 of this prompt govern current execution\.

## 2\. Exact inputs and current claims

Active worktree:
C:\\repos\\etl\-extension\\etl\_fw2\\recovery\-extension\-product\-0\.3\.147

Linked primary, identity only:
C:\\repos\\etl\-extension\\etl\_fw2\\etl\_framework\_extension\_hf1\_v2

Expected branch: fix/workspace\-write\-completion\-0\.3\.148
Expected HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
Expected staging: empty\.

REPAIR\_ROOT &#40;one literal flat directory name&#41;:
C:\\docs\\ETL\-0907\-POLICY\-COVERAGE\-REPAIR01\-20260907T183624221Z\-9f1d6a42\-6614\-4025\-a029\-2590da4a0b5f

PREVIOUS\_REVIEW\_ROOT:
C:\\docs\\ETL\-0907\-F5\-CONTRACT\-INDEPENDENT\-REVIEW01\\20260907T175437Z\-73509E6F\-9589\-44BB\-8A8F\-150986769864

CONTRACT\_REPAIR\_ROOT:
C:\\docs\\ETL\-0907\-F5\-CONTRACT\-REPAIR01\\20260907T112539Z\-559ABD3C\-A873\-4D54\-8EF0\-BC72D38F2403

EARLIER\_REVIEW\_ROOT:
C:\\docs\\ETL\-0906\-F5\-INDEPENDENT\-REVIEW02\\20260907T101629Z\-0318A671\-32C9\-41EC\-AA32\-B4EF0BF16505

OLDER\_IMPLEMENTATION\_ROOT &#40;one literal flat directory name&#41;:
C:\\docs\\ETL\-0906\-F5\-REPAIR\-TEST02\-20260906T193742Z\-11E99B37\-E240\-4D33\-931A\-3793C1E97409

Read this complete prompt and the governing glossary at
C:\\docs\\ETL\_QUALIFICATION\_GLOSSARY\.md, or an actually governing supplied copy\.
Record its actual location and raw hash\. Do not invent missing instructions\.
If a required glossary is unavailable or an actual governing conflict exists,
report that limitation and its effect on this narrow decision\.

Read REPAIR\_ROOT/report\.md, baseline\.json, post\-state\.json, task\.diff,
creation\-receipt\.json, policy\-coverage\.json, path\-reconciliation\.md,
incident/incident\.json and the supporting records indexed by the report\.
Read policy\-coverage\.js, capture\-state\.js and repair\-policy\.js as source text
only\. Enumerate the exact root to discover actual filenames; do not invent a
missing filename or execute a retained script to regenerate its evidence\.

Read the previous independent review’s complete review\.md and relevant
identity, stability and requirement/evidence records\. Inspect the original
CONTRACT\_REPAIR\_ROOT post\-source copies and the previous review’s retained
snapshots needed to authenticate the immediate baseline\. Earlier reports are
evidence and claims to assess; they cannot change this review’s permissions\.

The implementation reports:

- Final repository delta: runTest\.ts only; one comment and one array member,
  \+117 bytes, \+2 lines / 0 removed; LF preserved\.
- PROTECTED\_POLICY\_PATHS: 11 \-\> 12 members, adding exactly
  out/test/b3OutcomePolicy\.js; derived source/artifact relations: 10 \-\> 11\.
- No count/manifest/digest algorithm change because all consumers derive from
  the same canonical declarations\. The report enumerates 44 consumer sites\.
- A stale editor buffer briefly replaced the current runner with an older
  131713\-byte runner plus the insertion\. Recovery restored the authenticated
  131123\-byte immediate baseline, then applied the insertion at byte level\.
- The compiled policy artifact remains absent; no project execution occurred\.
- A BOM\-bearing correction JSON and an invalid 62\-character expected hash in
  an evidence helper were disclosed, with a distinct strict correction record\.

These are claims to verify, not acceptance premises\. Photographs and numbers
in this prompt are navigation/cross\-check aids, not authoritative hash pins\.

## 3\. Read\-only preflight and identity

Use git –no\-optional\-locks for Git reads\. Re\-derive active worktree, common
Git directory, branch, HEAD and staging\. Expected complete dirty inventory:

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

Check applicable worktree/common index locks and actual process arguments for
a concurrent writer, build/test process or development/test Host\. Ordinary
editor/language\-server processes alone do not prove prohibited execution\.
Do not terminate or reconfigure anything to make the check pass\.

If repository identity is wrong, stop substantive target review\. If a writer,
lock, unexpected inventory or input drift prevents a stable assessment,
preserve the observations and report the concrete blocker\. Do not repair it,
switch worktrees, rebase expected identities or consume an arbitrary newer
file as the intended review target\.

Authenticate these separate versions explicitly:

|Role                         |File                                 |Reported bytes|CRLF|Bare LF|Bare CR|
|-----------------------------|-------------------------------------|-------------:|---:|------:|------:|
|Immediate pre-repair baseline|src/test/runTest.ts                  |131123        |0   |2968   |0      |
|Intended final review target |src/test/runTest.ts                  |131240        |0   |2970   |0      |
|Unchanged dependency         |src/test/b3OutcomePolicy.ts          |35970         |809 |0      |0      |
|Unchanged unit tests         |src/test/b3OutcomePolicy.unit.test.ts|36595         |758 |0      |0      |
|Unchanged producer           |src/test/suite/index.ts              |10408         |246 |0      |0      |

Read full expected SHA\-256 values from the actual original saved records\.
Validate hash syntax/length before comparison; never transcribe a hash from a
photograph, truncate it, or silently substitute the newly measured live hash\.

Authenticate the 131123\-byte baseline against the previous review’s full
explicit identity table, CONTRACT\_REPAIR\_ROOT/post\-source source bytes, the
previous review’s snapshots/live and snapshots/post\-source copies, and this
repair’s immutable pre copy\. Cross\-check all available independent anchors\.
The old 131713\-byte source is an incident comparator, not this repair baseline\.
HEAD, Snapshot01, the 136657\-byte predecessor and the unavailable 126214\-byte
historical source are not substitutes\.

Establish the intended final identity from the repair’s retained post\-state
and any actual post\-source copy, then verify live bytes\. Independently derive
the expected final byte sequence in memory from the authenticated immediate
baseline and the exact approved insertion\. Compare it to live and retained
post bytes\. Do not write this reconstruction into the repository\.

Capture target/input identities at review intake and again after the review\.
Two matching observations establish observed stability at those checkpoints,
not continuous monitoring or proof that a dirty editor buffer cannot later
overwrite the file\. Inspect buffer identity/dirty state only if already
exposed by a genuinely read\-only capability; otherwise record it UNKNOWN\.
Do not use save/reload/Keep/Undo or open\-and\-save to obtain this information\.

Any new hash drift is an unexplained observation until evidence establishes
its cause\. The report’s instruction to treat every different future hash as
a recurrence of the editor hazard is not an acceptable diagnostic rule\.

## 4\. Exclusive review evidence destination

Validate the existing C:\\docs parent, containment and reparse/redirection
properties\. Keep the new root outside both worktrees, all prior evidence and
snapshots, user profiles and consumer/protected paths\.

Create exactly one new flat leaf:
C:\\docs\\ETL\-0907\-POLICY\-COVERAGE\-INDEPENDENT\-REVIEW01\-<UTC-timestamp>\-<GUID>\\

The final leaf must be created by an operation that fails if it already
exists\. Do not replace this with check\-then\-Directory\.CreateDirectory, accept
an existing empty leaf, or choose another destination after a failure\.

After validating the parent, this task\-owned Node core helper is allowed:

```js
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const taskId = 'ETL-0907-POLICY-COVERAGE-INDEPENDENT-REVIEW01';
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

Pass JavaScript literally, e\.g\. through a single\-quoted PowerShell here\-string
to Node stdin\. Preserve backticks/dollar signs without shell interpolation\.
Retain the exact invocation, output and actual execution\-tool completion
status\. A later script’s hard\-coded success field is not the tool result\.
If creation succeeds but the receipt fails, preserve the partial root and stop\.

Use exclusive new\-file/copy semantics for evidence\. Write each final artifact
once; use distinct filenames for intermediate observations\. Serialize new
JSON as BOM\-free UTF\-8, parse it strictly, and preserve any failed artifact
with a separately named correction\. Do not rewrite old evidence or conceal a
failed attempt\. This review’s receipt does not retroactively prove any older
root was created exclusively\.

## 5\. Verify the exact source\-policy repair

Read all of current runTest\.ts and the relevant dependency/producer imports,
compiler\-layout declarations and policy consumers\. Produce an independent
task\-only diff against the authenticated 131123\-byte pre copy\. Include normal,
whitespace\-ignored and CR\-at\-EOL\-ignored numstats; a read\-only no\-index diff
exit code indicating differences is not itself a command failure\.

Verify the claimed insertion is exactly the following two lines in the
canonical PROTECTED\_POLICY\_PATHS array, with existing indentation and LF:

```ts
  // Loaded at runtime by both `out/test/runTest.js` and `out/test/suite/index.js`.
  'out/test/b3OutcomePolicy.js',
```

Check the actual source, not just task\.diff\. Verify the added member occurs
once, no member was removed, all prior relative order is retained, and the
canonical ordering requirement is satisfied\. The reported position is after
out/extension\.js and before out/test/harness/mochaResultGuard\.js; derive the
ordering rule from assertProtectedPolicyIsCanonical itself\.

Independently enumerate old/new membership and source/artifact relations from
source literals and the existing rule\. Verify the compiled dependency binds
to src/test/b3OutcomePolicy\.ts exactly once\. Preserve the representation’s
actual orientation &#40;reported as artifact \-\> source in buildSourceArtifactRelations&#41;\.
Do not demand a duplicate hand\-maintained relation if the existing rule
already derives it, or an extra TypeScript membership entry that this model
does not require\. The unit\-test artifact must not be added as a runtime member\.

Verify both imports against actual tsconfig rootDir/outDir layout:

- src/test/runTest\.ts \-\> \./b3OutcomePolicy
- src/test/suite/index\.ts \-\> \.\./b3OutcomePolicy

Trace canonical data into the existing manifest generation/validation,
source/artifact relations, path/count checks, digest construction and runner
evidence comparisons\. At minimum inspect PROTECTED\_POLICY\_PATHS,
buildProtectedRecordsFromPolicy, generateProtectedHashManifest,
readProtectedHashManifest, canonicalProtectedFilesDigest,
buildSourceArtifactRelations and assertProtectedPolicyIsCanonical, plus their
relevant count/evidence consumers\. Check the report’s 44\-site enumeration
against source; site count alone is not proof of completeness\.

Show the exact member/relation deltas, preserved entries, counts and source
locations\. Separate static declaration/derivation evidence from a generated
runtime manifest\. Do not execute those functions or manufacture a compiled
file hash when the artifact is absent\.

Confirm the final diff changes no focused\-result protocol/nonce/eligibility,
observation, abort attribution, cause merge, verdict, exit, M2 writer/path,
M3 authorization/stage, A3 schema/order, B4 environment handling or Host pin\.
Use the exact diff plus unchanged input hashes to support preservation; do
not reopen all prior F1\-F5 behavior reviews or rerun the 15 local cases\.

Read\-only check out/test/b3OutcomePolicy\.js\. Report presence, absence or access
failure distinctly\. Its absence is an expected build/provenance blocker for
a later gate, not grounds to delete the new member or reject a correct source
declaration merely because this source\-only task prohibited emission\. Do not
claim runtime qualification from this source review\.

## 6\. Independently assess the editor incident and recovery

Treat this as a material incident, even if the final source is correct\.
Assess final correctness and implementation\-process compliance separately\.
Neither disclosure alone nor the small final diff proves recovery, limited
blast radius, or absence of intermediate effects\.

Inspect the retained incident blob, incident\.json, exact recovery helper,
available step\-by\-step measurements and original invocation/tool records\.
Read helpers as data; never execute a helper that restores or edits source\.

Build an evidence\-backed sequence for the reported transitions:

|State                           |Reported runTest.ts bytes|Meaning                                                         |
|--------------------------------|------------------------:|----------------------------------------------------------------|
|Authenticated immediate baseline|131123                   |Current contract repair before policy insertion                 |
|Older comparator                |131713                   |CONTRACT_REPAIR_ROOT pre source, reportedly held by stale buffer|
|Preserved damaged file          |131830                   |Older comparator plus the 117-byte insertion                    |
|Intended final source           |131240                   |Authenticated immediate baseline plus the same insertion        |

1. Verify incident/runTest\.after\-buffer\-flush\.ts against the incident record\.
   Remove only the exact insertion in memory and compare the remaining bytes
   with the actual older CONTRACT\_REPAIR\_ROOT pre copy\. This establishes byte
   correspondence; it does not by itself prove which editor/tool wrote them\.
2. Inspect available original edit/save observations and tool results for the
   claimed stale\-buffer mechanism and timing\. Distinguish direct observations,
   retained records, implementer narrative and inference\. Do not reconstruct
   unrecorded execution from a script merely because it could perform it\.
3. Authenticate the recovery pre copy independently\. Verify the recovery
   helper’s checks, exact insertion\-anchor cardinality and read\-back records\.
   Confirm restoration did not use the older incident comparator or HEAD\.
4. Verify the final source equals authenticated baseline plus the permitted
   insertion and that earlier CONTRACT\_REPAIR01 changes are preserved\.
5. Cross\-check preservation inputs at available incident/recovery checkpoints\.
   State what supports the claimed one\-file blast radius and what is unknown\.
   Endpoint equality alone does not prove a file was never temporarily changed\.
6. Assess the evidence for no compiler/test/runner/Host execution during the
   incident\. Do not promote absence of a later process to proof of an earlier
   process history\. Lack of exhaustive historical telemetry is a stated limit,
   not permission to invent either prohibited execution or its absence\.
7. Assess the original brief’s narrow edit and pending\-editor\-state constraints
   against actual actions, including whether task\-owned byte recovery is
   evidenced and any workflow deviation remains\. Do not retroactively grant
   permissions or describe the entire execution as mutation\-free\.
8. Recheck live source at completion\. Record buffer state only to the extent
   observable read\-only; do not resolve the editor condition in this review\.

A verified final recovery can support source\-policy acceptance with a
disclosed recovered incident\. It does not erase a process deviation or prove
future editor safety\. If recovery, input identity, required preservation or
observed stability is unresolved, explain the precise blocking gap\. Do not
auto\-reject merely because a recovered incident occurred, and do not auto\-pass
because report\.md says it was recovered\.

## 7\. Evidence reliability and path reconciliation

Verify the repair root’s creation mechanism using its actual receipt and
retained invocation/output/tool status\. Separate evidence of a successful
exclusive leaf creation from self\-authored success prose\. Assess the old
nonexclusive\-root finding as historical; a new receipt cannot cure its method\.

For every consumed original JSON record, record raw hash/bytes and strict
parse status\. Keep BOMs, raw control characters and any invalid strings in
the source file untouched\. The owner previously explained that literal
newlines were temporarily inserted in some evidence for photographs\. Do not
infer who caused a legacy parse failure or that it represents a source defect\.

The same alternative identity anchors authorized by Appendix A remain allowed
for this review: complete explicit hashes in the original saved review\.md,
matching original post\-source bytes and corroborating retained source\-identity
records/snapshots\. Record exactly which alternatives establish each identity\.
Do not silently repair JSON, leniently parse it as though it were strict, or
block solely on a legacy display edit when these anchors agree completely\.

Specifically verify the newly disclosed exceptions:

- prior\-evidence\-integrity\.json reportedly flags unchanged:false for
  requirement\-evidence\-matrix\.md because a helper used a 62\-character expected
  hash\. Validate the invalid value, locate the earliest retained measured
  identity and compare the actual matrix bytes/hash to that independent
  observation and any original retained copy\. A matching value in a later
  correction alone is circular and insufficient proof of preservation\.
- Preserve and hash prior\-evidence\-integrity\-anchor\-correction\.json, the
  reportedly BOM\-bearing original, and its separately named
  prior\-evidence\-integrity\-anchor\-correction\.strict\.json\. Verify the latter
  parses strictly and accurately describes the former comparison error\.
  Report whether its claims are corroborated, contradicted or unresolved\.
- Check for missing/broken artifact references by bounded enumeration\. A
  differently named actual inventory may be used when its contents and identity
  are verified; do not pretend that the report’s missing filename exists\.

Recheck the exact path reconciliation without overwriting prior reports:

- OLDER\_IMPLEMENTATION\_ROOT is the flat name containing
  \-TEST02\-20260906…, not a TEST02 directory containing a timestamp child\.
  It is reported present with 27 files\. Verify the corrected absence claim
  using the saved original spelling and actual files\.
- EARLIER\_REVIEW\_ROOT includes REVIEW02 and is reported present with six files\.
  The previous review did not claim this root absent\. Verify those originals
  against the six mapped retained copies; do not fabricate a second corrected
  absence claim merely because a REVIEW\-without\-02 control path is absent\.
- The earlier 126214\-byte reviewed source remains unavailable unless actual
  authenticated matching bytes are supplied\. A recovered 136657\-byte pre copy
  is not that source and cannot close historical preservation\.

Read bounded prior records relevant to these claims; do not search Local
History, debug logs, unrelated locations or network storage\. Navigation files
ETL\_LATEST\.md and ETL\_STATE\_REV3\.md remain UNKNOWN beyond their exact probed
locations if unavailable\. Their absence does not expand this task or replace
the explicit scope with guessed project state\.

## 8\. Preservation and review evidence

Compare actual final source/output/configuration/preservation inputs with the
repair’s independently authenticated pre records and originals\. Then capture
review\-intake and completion identities for the relevant repository inputs
and every prior evidence file consumed\. Use per\-file raw hashes for out/\*\*
and existing configured build\-output/build\-info paths, not only aggregate
file counts, total bytes or newest timestamps\. Preserve absent vs inaccessible\.

An unchanged Git status alone cannot establish unchanged dirty or untracked
file contents\. Verify the guard, discovery constants, focused suite, helper,
helper tests, producer, other pre\-existing dirty files, configuration and old
evidence\. Separate preservation across the implementation from preservation
during this review\. Do not claim continuous no\-write history from equal hashes\.

Write a compact, auditable new evidence set containing:

- creation\-receipt\.json and exact command/tool completion records;
- review\-identities\.json with original expected anchors and measured identities;
- review\-policy\-delta\.json and the independently derived task\-only diff;
- review\-incident\.json with state correspondence, mechanism/recovery evidence,
  scope assessment, buffer/stability observations and limitations;
- review\-evidence\-assessment\.json covering parse/correction/creation/path claims;
- review\-preservation\.json with per\-file comparisons and endpoint stability;
- review\-result\.json and review\.md with findings, decision and next boundary\.

Use additional immutable capture files only where needed for auditable raw
observations\. Hash helpers and retained copies used in analysis\. Cite actual
paths, symbols/locations and supporting evidence for conclusions\. Label a
claim retained from the implementer distinctly from an independent observation\.
Do not claim the entire historical evidence chain is authenticated merely
because the files agree with their own embedded hashes\.

## 9\. Decision and acceptance criteria

Choose one actual overall result:

- ACCEPTABLE\_FOR\_SOURCE\_POLICY\_GATE
- ACCEPTABLE\_FOR\_SOURCE\_POLICY\_GATE\_WITH\_DISCLOSED\_RECOVERED\_INCIDENT
- NOT\_ACCEPTABLE
- BLOCKED\_<CONCRETE\_REASON\>

Source\-policy acceptance requires all of the following to be established:
authenticated immediate baseline and intended target; exact authorized final
policy/relation change; consistent canonical static consumption; preservation
of adjacent source behavior and required inputs; verified recovery of the
disclosed rollback; no unresolved live\-source drift; sufficiently reliable
current evidence and supported path corrections\.

Because an incident is reported, use the disclosed\-incident result if it is
verified recovered and no blocking gap remains\. Keep process deviations and
evidence defects visible even when they do not defeat final\-source correctness\.
Do not assert clean process compliance when the evidence contradicts it\.

For each finding state severity, exact evidence, practical consequence, whether
it blocks THIS source\-policy gate or a later build/Host gate, and the smallest
needed follow\-up\. Do not let a hypothetical later risk become an invented
current defect\. Conversely, do not waive an unresolved incident or identity
problem to advance the schedule\.

Expected later limitations, without upgrades by this review:

- The compiled policy artifact is absent/unproven until an authorized build\.
- The pinned VS Code 1\.135\.0 contract remains unverified; do not switch to
  1\.136\.1 to bypass it\.
- Historical reviewed\-baseline preservation remains NOT\_VERIFIED\.
- This review does not rerun the earlier 15 unit cases or establish runner,
  Host, product, full B3 acceptance or runtime qualification\.

## 10\. Final report and stop

Include these fields with actual evidence\-based values:

```text
TASK_ID: ETL-0907-POLICY-COVERAGE-INDEPENDENT-REVIEW01
RESULT: <one result from section 9>
REVIEWED_IMPLEMENTATION: ETL-0907-POLICY-COVERAGE-REPAIR01
REVIEWED_ROOT: <literal repair root>
IMMEDIATE_BASELINE_IDENTITY: <original anchors, raw SHA-256, bytes, EOL>
FINAL_SOURCE_IDENTITY: <expected anchors and measured SHA-256, bytes, EOL>
POLICY_DEPENDENCY_FINDING: CLOSED_STATICALLY | OPEN | UNRESOLVED
CANONICAL_RELATION_AND_CONSUMERS: <independent static evidence>
FINAL_TASK_ONLY_DIFF: <exact paths, bytes and numstats>
INCIDENT_RECOVERY: VERIFIED | CONTRADICTED | UNRESOLVED
INCIDENT_MECHANISM_EVIDENCE: <observed, retained, inferred and unknown>
IMPLEMENTATION_PROCESS_COMPLIANCE: <specific assessment, including deviations>
LIVE_SOURCE_STABILITY: <checkpoint results and limits>
EDITOR_BUFFER_STATE: <read-only observation or UNKNOWN>
EVIDENCE_CORRECTIONS: <independent assessment and remaining gaps>
PATH_RECONCILIATION: <corroborated/corrected/unresolved claims>
REPAIR_ROOT_EXCLUSIVITY: <supported/unsupported and evidence>
REVIEW_ROOT_EXCLUSIVITY: <mechanism and actual tool completion evidence>
IMPLEMENTATION_PRESERVATION: <verified scope and limitations>
REPOSITORY_OR_PRIOR_EVIDENCE_CHANGED_BY_REVIEW: NO
TYPECHECK_COMPILE_TEST_RUNNER_PRODUCER_OR_HOST_EXECUTED_BY_REVIEW: NO
COMPILED_POLICY_ARTIFACT: <actual presence; provenance status>
PINNED_VSCODE_1_135_0_CONTRACT: UNVERIFIED_IN_THIS_REVIEW
HISTORICAL_REVIEWED_BASELINE_PRESERVATION: NOT_VERIFIED
FULL_B3_OR_RUNTIME_QUALIFICATION_GRANTED: NO
BLOCKING_FINDINGS_FOR_THIS_GATE: <exact IDs or NONE>
LATER_GATE_BLOCKERS: <separately listed>
NEXT_STEP_PROPOSED_ONLY: <minimum bounded next task; no execution permission>
REPORT_PATH: <exact new review.md path>
```

If a prohibited action or unintended mutation actually occurs, report it
truthfully instead of copying a NO field\. Preserve the observations and stop
that operation; do not attempt a repository recovery in this read\-only task\.

After completing the review, stop\. If accepted, describe the minimum next
build/provenance and pinned\-Host preparation scope for separate authorization\.
Do not build, execute the Host, repair findings, self\-authorize the next gate,
or update any previous implementation/review/navigation document\.

Give a short chat summary with the exact report path, decision, incident
recovery assessment and remaining blockers\. No new test execution is expected
or permitted in this source\-only review\.

---

## Appendix A — Original repair contract, historical reference only

The text below is the complete previously issued repair brief\. Review the
implementation against it; do not execute its source\-editing instructions\.
Current permissions are exclusively those in sections 1\-10 above\.

<!-- BEGIN VERBATIM ORIGINAL REPAIR BRIEF -->

TASK\_ID: ETL\-0907\-POLICY\-COVERAGE\-REPAIR01
TYPE: BOUNDED SOURCE\-ONLY POLICY REPAIR AND EVIDENCE\-PATH RECONCILIATION

Run this complete prompt in an ordinary LOCAL Windows VS Code Agent chat,
in the active recovery worktree identified below\. Do not use the ETL
Orchestrator\. Use one implementation Agent and one writer\. A later independent
review must be performed by a different Agent\. Keep code, comments and all
engineering evidence in English\.

Echo the TASK\_ID as the first line of the final report\.

## 1\. Owner authorization and intended result

The owner authorizes this next bounded task:

1. Correct the protected\-policy coverage of the b3OutcomePolicy runtime
   dependency, including its canonical source/artifact relationship\.
2. Reconcile the exact evidence paths that the last review reported absent\.
3. Use a genuinely exclusive new evidence destination and retain its creation
   result\. Preserve all previous reports and evidence unchanged\.

The only repository file authorized for editing is:
src/test/runTest\.ts

Edits are limited to PROTECTED\_POLICY\_PATHS, the existing canonical
source/artifact relation data and any directly associated declarative expected
path/count data in that same file that must change for this one dependency\.
Locate these declarations and all their consumers before editing\. Do not
duplicate canonical declarations or introduce a second policy authority\.

If the necessary canonical owner or a mandatory coupled change is outside
src/test/runTest\.ts, report BLOCKED\_POLICY\_COUPLING with its exact path, symbol,
reason and minimum proposed expansion\. Do not edit another file or leave an
inconsistent partial policy change merely to satisfy the one\-file boundary\.

The task may perform read\-only identity/status/hash/diff/source inspection and
write new task evidence under the destination in section 4\. Existing local
PowerShell/Node may be used for these operations and for small data\-only
inspection scripts\. This does not authorize execution of project modules\.

No type\-check, compiler, transpiler, test, runner, producer, launcher,
Extension Host, parser, integration suite, formatter, linter, watcher,
package script, install, download, packaging or release is authorized\.
No repository build output, dependency/configuration change, new repository
file, Git mutation command, process termination or lock deletion is authorized\.
Do not use Keep/Undo/save/revert to resolve pre\-existing pending editor changes\.

This is a source\-level policy repair\. Generating the actual compiled artifact,
proving its build provenance and qualifying the pinned Host remain later gates\.
The recommendation to regenerate a manifest/compiled artifact in the review
does not grant those operations in this task\.

## 2\. Governing inputs and exact locations

Active worktree:
C:\\repos\\etl\-extension\\etl\_fw2\\recovery\-extension\-product\-0\.3\.147

Linked primary, identity only:
C:\\repos\\etl\-extension\\etl\_fw2\\etl\_framework\_extension\_hf1\_v2

Expected branch: fix/workspace\-write\-completion\-0\.3\.148
Expected HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
Expected staging: empty\.

Read this brief completely, then the complete governing glossary at
C:\\docs\\ETL\_QUALIFICATION\_GLOSSARY\.md or its actual governing repository copy
docs/glossary/ETL\_QUALIFICATION\_GLOSSARY\.md\. Record the real path and raw hash\.
Read the following original reports and relevant supporting files completely;
screenshots are navigation aids, not source or hash substitutes\.

LATEST\_REVIEW\_ROOT:
C:\\docs\\ETL\-0907\-F5\-CONTRACT\-INDEPENDENT\-REVIEW01\\20260907T175437Z\-73509E6F\-9589\-44BB\-8A8F\-150986769864

Read review\.md, review\-result\.json, review\-identities\.json,
review\-input\-hashes\.json, source\-stability\.json and the requirement/evidence
matrix, plus the authenticated diff and other records needed for this scope\.
Use bounded enumeration inside the exact root to locate actual filenames\.

CURRENT\_IMPLEMENTATION\_ROOT:
C:\\docs\\ETL\-0907\-F5\-CONTRACT\-REPAIR01\\20260907T112539Z\-559ABD3C\-A873\-4D54\-8EF0\-BC72D38F2403

Read report\.md, baseline\.json, post\-state\.json, task\.diff and relevant
post\-source/pre copies and preservation inventories\. Read prior complete task
briefs if retained/supplied to assess their claims; their former execution
permissions do not apply to this task\.

CORRECT\_EARLIER\_REVIEW\_ROOT:
C:\\docs\\ETL\-0906\-F5\-INDEPENDENT\-REVIEW02\\20260907T101629Z\-0318A671\-32C9\-41EC\-AA32\-B4EF0BF16505

CORRECT\_OLDER\_IMPLEMENTATION\_ROOT:
C:\\docs\\ETL\-0906\-F5\-REPAIR\-TEST02\-20260906T193742Z\-11E99B37\-E240\-4D33\-931A\-3793C1E97409

These are literal paths\. The older implementation root is one directory name
containing ‘\-TEST02\-20260906…’; do not replace that hyphen with a directory
separator\. The earlier review root ends in ‘INDEPENDENT\-REVIEW02’; do not drop
‘02’\. Do not derive one evidence path by applying another task’s layout\.

ETL\_LATEST\.md and ETL\_STATE\_REV3\.md were reported unavailable\. For this exact
policy repair and path reconciliation, that reported absence is not a new
permission to infer their contents or reconstruct project state\. Read them if
supplied/found by bounded named\-file discovery; otherwise record broader
state completeness UNKNOWN\. This explicit brief supplies the narrow new scope\.
Stop and report any actual governing conflict beyond the authorized coverage
expansion\. A missing complete glossary or ambiguous policy requirement must
be reported rather than replaced with memory\.

## 3\. Preflight, path reconciliation and immediate baseline

Use git –no\-optional\-locks for reads\. Re\-derive worktree/common\-Git identity,
branch, HEAD, empty staging and this exact complete dirty inventory:

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

Check applicable common/worktree index locks and actual process arguments for
an active test/development Host or concurrent writer\. An ordinary editor and
language server are not automatically prohibited Hosts\. Do not stop processes,
remove locks or change pending editor state to make preflight pass\.

Compare the literal correct evidence paths above with those actually retained
in the last review\. Check both exact spellings where they differ; record the
requested string, observed result and resolved path\. If a correct historical
root exists, inspect the relevant original records there and explain exactly
which earlier absence/preservation claims can now be corrected\. If it does
not exist, report absence only at that exact path\. Do not search Local History,
debug logs, unrelated directories or network storage for replacement evidence\.

Do not overwrite the review’s files\. Prepare path\-reconciliation\.md in the
new task root, retaining the earlier claims as history\. Finding an old folder
does not by itself authenticate its contents or resolve the unavailable
126214\-byte historical source\. Missing historical folders alone need not stop
this repair if the immediate reviewed baseline is authenticated independently\.

Read full expected source SHA\-256 values from the original latest review’s
source records/full table, cross\-check the current implementation post\-state
and post\-source copies, then compare live bytes\. These counts are cross\-checks:

|File                                 |Bytes |CRLF|Bare LF|Bare CR|
|-------------------------------------|-----:|---:|------:|------:|
|src/test/runTest.ts                  |131123|0   |2968   |0      |
|src/test/b3OutcomePolicy.ts          |35970 |809 |0      |0      |
|src/test/b3OutcomePolicy.unit.test.ts|36595 |758 |0      |0      |
|src/test/suite/index.ts              |10408 |246 |0      |0      |

Authenticate preservation inputs too: the guard, discovery constants, focused
suite, out\-of\-scope dirty files and configuration\. Do not transcribe hashes
from photographs or promote newly observed hashes to expected pins\.

If a previously photographed JSON file is malformed, record its parse failure
and leave it untouched\. For this task, complete explicit hashes in the saved
review\.md plus matching original post\-source bytes and another retained
source\-identity record are allowed alternative anchors\. This permits a
documented current baseline, not silent lenient parsing or retrospective
repair of old evidence\. Stop if anchors disagree or exact identity is not
established\. Do not stop solely because display edits made one old JSON
unparseable when the required identities are established through this rule\.

After section 4 establishes the fresh task root, and before any source edit,
capture an exact immutable pre\\ copy of runTest\.ts and byte copies of
preservation inputs, verify source/copy equality and retain full identities\.
Recheck the target immediately before editing\. Use this
131123\-byte reviewed source as the immediate baseline, not HEAD, Snapshot01,
the earlier 131713/136657\-byte sources or the unavailable 126214\-byte source\.

## 4\. Exclusive new evidence destination

First validate C:\\docs and the planned destination against both worktrees,
prior evidence/snapshots, profiles and consumer/protected paths\. Reject unsafe
redirection/reparse points\. C:\\docs must already be a safe accessible parent\.

Create exactly one fresh leaf with this literal layout:
C:\\docs\\ETL\-0907\-POLICY\-COVERAGE\-REPAIR01\-<UTC-timestamp>\-<GUID>\\

Use a create operation that fails if the leaf exists\. A preliminary existence
check followed by Directory\.CreateDirectory is not sufficient\. Do not use
recursive directory creation for the final leaf or accept an existing empty
leaf\. On a conflict/failure, stop without choosing an alternate destination\.

The following Node core operations are explicitly allowed after parent and
containment validation\. Use the installed Node and invoke only a task\-owned
inline helper; do not import or evaluate project code:

```js
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const taskId = 'ETL-0907-POLICY-COVERAGE-REPAIR01';
const utc = new Date().toISOString().replace(/[-:.]/g, '');
const root = path.join('C:\\docs', `${taskId}-${utc}-${crypto.randomUUID()}`);
fs.mkdirSync(root, { recursive: false }); // Existing leaf is an error.
const receipt = {
  taskId, root, createdAtUtc: new Date().toISOString(),
  mechanism: 'fs.mkdirSync', recursive: false,
  result: 'CREATED_BY_SUCCESSFUL_MKDIR', pid: process.pid
};
fs.writeFileSync(path.join(root, 'creation-receipt.json'),
  JSON.stringify(receipt, null, 2) + '\n', { encoding: 'utf8', flag: 'wx' });
process.stdout.write(JSON.stringify(receipt) + '\n');
```

Pass the JavaScript as literal input, for example through a single\-quoted
PowerShell here\-string to Node stdin\. Preserve JavaScript backticks and dollar
signs; do not embed it in an interpolating shell string\.

Retain the exact invocation, returned output and actual execution\-tool status\.
Do not hard\-code a successful tool exit into a later report\. If creation
succeeds but receipt writing fails, preserve the partial directory and stop\.
Use CreateNew / ‘wx’ semantics for all new evidence files and exclusive copy
semantics for baseline copies\. Write final artifacts once; use distinct names
for intermediate captures rather than overwriting them\.

API reference: [Node\.js filesystem directory creation](https://nodejs.org/docs/latest-v20.x/api/fs.html#fsmkdirpath-options-callback)\.
The helper illustrates leaf creation only; it does not replace the required
parent, containment or redirection checks\.

This fresh receipt proves only this task’s operation\. Do not relabel earlier
nonexclusive creation as exclusive or claim that earlier evidence was corrupt
merely because its exclusivity was unsupported\.

## 5\. Exact repair requirements

Read all of runTest\.ts, the policy module and producer, plus every canonical
policy/relation declaration and relevant consumer\. Resolve both runtime import
paths to the actual module using the existing compiler layout; do not copy a
report’s shorthand import spelling into code\.

The repaired canonical policy must cover:
out/test/b3OutcomePolicy\.js

Its source/artifact relationship must bind:
src/test/b3OutcomePolicy\.ts \-\> out/test/b3OutcomePolicy\.js

Use the existing representation and ownership model\. Add the compiled path
exactly once\. Add or correct its relation exactly once\. If the established
model also requires explicit protection of the matching TypeScript source,
the corresponding src/test/b3OutcomePolicy\.ts entry is authorized within the
same declarations\. Make no other membership expansion\.

Preserve all existing protected entries and relations, their relative order
and the canonical normalization convention\. Do not add a broad glob, protect
an entire directory, remove another entry, add an exception, or weaken a
missing\-file/hash check\. Do not protect the unit\-test artifact merely because
it shares a basename prefix\.

Trace how the protected manifest, counts, digest and final comparisons derive
from the canonical policy\. Their future runtime values must include the new
member consistently\. If values are derived, preserve that derivation\. If
declarative expected membership/count data must change, change only the
necessary data within runTest\.ts and explain the dependency\. Do not insert a
fabricated hash, special\-case a comparison to pass, or rewrite algorithmic
behavior to accommodate an absent artifact\.

The compiled module is currently reported absent because repository emit was
not authorized\. Verify that state read\-only\. Keep the policy entry even while
it is absent: a later authorized build/provenance gate must establish the
artifact before a qualified run\. Do not create a placeholder, compile just
that file, copy previously emitted unit\-test JavaScript into out/, exclude it
from the policy, or record missing as verified\.

Do not change:

- Focused delivery, protocol version/nonce, eligibility, retained observation,
  abnormal\-exit attribution, cause keys/merge, verdict or exit logic\.
- src/test/b3OutcomePolicy\.ts, its unit tests, src/test/suite/index\.ts,
  the focused suite, guard or discovery patterns\.
- M2 writers/destinations/reduced filename/dual\-error handling; M3 authorization
  or stages; A3 schemas/post\-exit ordering; B4 environment handling\.
- EXPECTED\_VSCODE\_VERSION, package/configuration/dependency files, build outputs,
  historical evidence, navigation/reference documents or product code\.

Preserve LF in runTest\.ts; no whole\-file formatting or line\-ending changes\.
If the required policy correction cannot preserve these boundaries, stop with
the concrete coupling rather than modifying adjacent accepted behavior\.

## 6\. Static verification and evidence

Perform data\-only/static checks appropriate to this declaration change:

- Exact old/new membership set difference and duplicate check\.
- Exact old/new source/artifact relation difference and coverage of both
  runner and producer imports\.
- Existing path/relation preservation and canonical path form\.
- Every count/manifest/digest consumer’s source\-level dependency on the updated
  canonical data, without executing that consumer\.
- Task\-only diff against the new pre\\ copy, including normal,
  whitespace\-ignored and CR\-at\-EOL\-ignored numstats\.

Read TypeScript literals as data only; never evaluate runTest\.ts, its emitted
JavaScript, the policy module or the producer to obtain the lists\. If a
data\-only extraction cannot resolve an expression safely, inspect its source
or report the limitation\. Do not introduce a test\-only policy implementation\.
No new test is required for this declaration\-only task and none is authorized\.

Capture per\-file hashes for out/\*\* and any existing configured output roots
and build\-info before/after, along with configuration, preservation inputs
and prior evidence actually read\. Prove that only runTest\.ts changed in the
repository and that all old evidence consumed by this task stayed unchanged\.
Record absent paths distinctly from empty directories and inaccessible paths\.

Create policy\-coverage\.json containing observed before/after declaration data,
the one dependency’s source/artifact mapping, the exact set/count deltas and
source locations\. Label any planned manifest or count as STATIC\_DECLARATION\_DATA\.
This artifact is not the runner’s generated runtime protected manifest\.
Do not manufacture a file\-content digest when the compiled artifact is absent\.

Save baseline\.json, post\-state\.json, task\.diff, path\-reconciliation\.md,
policy\-coverage\.json, creation\-receipt\.json, supporting measurement records
and report\.md under the new task root\. Serialize strict valid UTF\-8 JSON\.
Use display wrapping for screenshots; do not insert literal newlines into
JSON strings\. Preserve failed/partial evidence without cleanup or replacement\.

## 7\. Completion and next gate

Success requires authenticated immediate source identity, the exact policy and
relation correction, consistent static consumption, preserved scope, reconciled
path observations and retained exclusive\-creation evidence\. It does not require
recovering missing historical folders, building the module or running tests\.

Use the following final report fields, choosing one actual result:

```text
TASK_ID: ETL-0907-POLICY-COVERAGE-REPAIR01
RESULT: IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW | BLOCKED_<REASON>
FILES_CHANGED_BY_TASK: <exact repository paths>
IMMEDIATE_BASELINE: <raw hash, bytes, EOL profile and original anchors>
PROTECTED_POLICY_DELTA: <exact membership difference>
SOURCE_ARTIFACT_RELATION: <exact mapping and canonical owner>
COUNT_MANIFEST_DIGEST_CONSUMPTION: <static proof or coupling>
COMPILED_POLICY_ARTIFACT: <observed presence; provenance remains unverified>
CORRECT_EARLIER_REVIEW_PATH: <literal path and observed result>
CORRECT_OLDER_IMPLEMENTATION_PATH: <literal path and observed result>
PRIOR_REVIEW_PATH_CLAIMS: <corroborated/corrected/unknown with evidence>
CURRENT_EVIDENCE_ROOT_CREATION: <mechanism and retained actual result>
PRIOR_EVIDENCE_CHANGED: NO
PRESERVATION: <exact byte/static proofs and limitations>
TYPECHECK_COMPILE_TEST_RUNNER_PRODUCER_OR_HOST_EXECUTED: NO
REPOSITORY_COMPILED_OUTPUT_CHANGED: NO
GIT_MUTATION_INSTALL_PACKAGE_OR_RELEASE_EXECUTED: NO
HISTORICAL_REVIEWED_BASELINE_PRESERVATION: NOT_VERIFIED
PINNED_VSCODE_1_135_0_CONTRACT: UNVERIFIED_IN_THIS_TASK
FULL_B3_OR_RUNTIME_QUALIFICATION_GRANTED: NO
NEXT_GATE: ETL-0907-POLICY-COVERAGE-INDEPENDENT-REVIEW01
EVIDENCE_ROOT: <exact path or NOT_CREATED>
```

The next independent reviewer must assess 
