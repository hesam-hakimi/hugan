TASK_ID: ETL-0907-POLICY-COVERAGE-REPAIR01
TYPE: BOUNDED SOURCE-ONLY POLICY REPAIR AND EVIDENCE-PATH RECONCILIATION

Run this complete prompt in an ordinary LOCAL Windows VS Code Agent chat,
in the active recovery worktree identified below. Do not use the ETL
Orchestrator. Use one implementation Agent and one writer. A later independent
review must be performed by a different Agent. Keep code, comments and all
engineering evidence in English.

Echo the TASK_ID as the first line of the final report.

1. Owner authorization and intended result

The owner authorizes this next bounded task:

1. Correct the protected-policy coverage of the b3OutcomePolicy runtime
dependency, including its canonical source/artifact relationship.
2. Reconcile the exact evidence paths that the last review reported absent.
3. Use a genuinely exclusive new evidence destination and retain its creation
result. Preserve all previous reports and evidence unchanged.

The only repository file authorized for editing is:
src/test/runTest.ts

Edits are limited to PROTECTED_POLICY_PATHS, the existing canonical
source/artifact relation data and any directly associated declarative expected
path/count data in that same file that must change for this one dependency.
Locate these declarations and all their consumers before editing. Do not
duplicate canonical declarations or introduce a second policy authority.

If the necessary canonical owner or a mandatory coupled change is outside
src/test/runTest.ts, report BLOCKED_POLICY_COUPLING with its exact path, symbol,
reason and minimum proposed expansion. Do not edit another file or leave an
inconsistent partial policy change merely to satisfy the one-file boundary.

The task may perform read-only identity/status/hash/diff/source inspection and
write new task evidence under the destination in section 4. Existing local
PowerShell/Node may be used for these operations and for small data-only
inspection scripts. This does not authorize execution of project modules.

No type-check, compiler, transpiler, test, runner, producer, launcher,
Extension Host, parser, integration suite, formatter, linter, watcher,
package script, install, download, packaging or release is authorized.
No repository build output, dependency/configuration change, new repository
file, Git mutation command, process termination or lock deletion is authorized.
Do not use Keep/Undo/save/revert to resolve pre-existing pending editor changes.

This is a source-level policy repair. Generating the actual compiled artifact,
proving its build provenance and qualifying the pinned Host remain later gates.
The recommendation to regenerate a manifest/compiled artifact in the review
does not grant those operations in this task.

2. Governing inputs and exact locations

Active worktree:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Linked primary, identity only:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Expected branch: fix/workspace-write-completion-0.3.148
Expected HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
Expected staging: empty.

Read this brief completely, then the complete governing glossary at
C:\docs\ETL_QUALIFICATION_GLOSSARY.md or its actual governing repository copy
docs/glossary/ETL_QUALIFICATION_GLOSSARY.md. Record the real path and raw hash.
Read the following original reports and relevant supporting files completely;
screenshots are navigation aids, not source or hash substitutes.

LATEST_REVIEW_ROOT:
C:\docs\ETL-0907-F5-CONTRACT-INDEPENDENT-REVIEW01\20260907T175437Z-73509E6F-9589-44BB-8A8F-150986769864

Read review.md, review-result.json, review-identities.json,
review-input-hashes.json, source-stability.json and the requirement/evidence
matrix, plus the authenticated diff and other records needed for this scope.
Use bounded enumeration inside the exact root to locate actual filenames.

CURRENT_IMPLEMENTATION_ROOT:
C:\docs\ETL-0907-F5-CONTRACT-REPAIR01\20260907T112539Z-559ABD3C-A873-4D54-8EF0-BC72D38F2403

Read report.md, baseline.json, post-state.json, task.diff and relevant
post-source/pre copies and preservation inventories. Read prior complete task
briefs if retained/supplied to assess their claims; their former execution
permissions do not apply to this task.

CORRECT_EARLIER_REVIEW_ROOT:
C:\docs\ETL-0906-F5-INDEPENDENT-REVIEW02\20260907T101629Z-0318A671-32C9-41EC-AA32-B4EF0BF16505

CORRECT_OLDER_IMPLEMENTATION_ROOT:
C:\docs\ETL-0906-F5-REPAIR-TEST02-20260906T193742Z-11E99B37-E240-4D33-931A-3793C1E97409

These are literal paths. The older implementation root is one directory name
containing ‘-TEST02-20260906…’; do not replace that hyphen with a directory
separator. The earlier review root ends in ‘INDEPENDENT-REVIEW02’; do not drop
‘02’. Do not derive one evidence path by applying another task’s layout.

ETL_LATEST.md and ETL_STATE_REV3.md were reported unavailable. For this exact
policy repair and path reconciliation, that reported absence is not a new
permission to infer their contents or reconstruct project state. Read them if
supplied/found by bounded named-file discovery; otherwise record broader
state completeness UNKNOWN. This explicit brief supplies the narrow new scope.
Stop and report any actual governing conflict beyond the authorized coverage
expansion. A missing complete glossary or ambiguous policy requirement must
be reported rather than replaced with memory.

3. Preflight, path reconciliation and immediate baseline

Use git –no-optional-locks for reads. Re-derive worktree/common-Git identity,
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
an active test/development Host or concurrent writer. An ordinary editor and
language server are not automatically prohibited Hosts. Do not stop processes,
remove locks or change pending editor state to make preflight pass.

Compare the literal correct evidence paths above with those actually retained
in the last review. Check both exact spellings where they differ; record the
requested string, observed result and resolved path. If a correct historical
root exists, inspect the relevant original records there and explain exactly
which earlier absence/preservation claims can now be corrected. If it does
not exist, report absence only at that exact path. Do not search Local History,
debug logs, unrelated directories or network storage for replacement evidence.

Do not overwrite the review’s files. Prepare path-reconciliation.md in the
new task root, retaining the earlier claims as history. Finding an old folder
does not by itself authenticate its contents or resolve the unavailable
126214-byte historical source. Missing historical folders alone need not stop
this repair if the immediate reviewed baseline is authenticated independently.

Read full expected source SHA-256 values from the original latest review’s
source records/full table, cross-check the current implementation post-state
and post-source copies, then compare live bytes. These counts are cross-checks:

|File                                 |Bytes |CRLF|Bare LF|Bare CR|
|-------------------------------------|-----:|---:|------:|------:|
|src/test/runTest.ts                  |131123|0   |2968   |0      |
|src/test/b3OutcomePolicy.ts          |35970 |809 |0      |0      |
|src/test/b3OutcomePolicy.unit.test.ts|36595 |758 |0      |0      |
|src/test/suite/index.ts              |10408 |246 |0      |0      |

Authenticate preservation inputs too: the guard, discovery constants, focused
suite, out-of-scope dirty files and configuration. Do not transcribe hashes
from photographs or promote newly observed hashes to expected pins.

If a previously photographed JSON file is malformed, record its parse failure
and leave it untouched. For this task, complete explicit hashes in the saved
review.md plus matching original post-source bytes and another retained
source-identity record are allowed alternative anchors. This permits a
documented current baseline, not silent lenient parsing or retrospective
repair of old evidence. Stop if anchors disagree or exact identity is not
established. Do not stop solely because display edits made one old JSON
unparseable when the required identities are established through this rule.

After section 4 establishes the fresh task root, and before any source edit,
capture an exact immutable pre\ copy of runTest.ts and byte copies of
preservation inputs, verify source/copy equality and retain full identities.
Recheck the target immediately before editing. Use this
131123-byte reviewed source as the immediate baseline, not HEAD, Snapshot01,
the earlier 131713/136657-byte sources or the unavailable 126214-byte source.

4. Exclusive new evidence destination

First validate C:\docs and the planned destination against both worktrees,
prior evidence/snapshots, profiles and consumer/protected paths. Reject unsafe
redirection/reparse points. C:\docs must already be a safe accessible parent.

Create exactly one fresh leaf with this literal layout:
C:\docs\ETL-0907-POLICY-COVERAGE-REPAIR01-<UTC-timestamp>-<GUID>\

Use a create operation that fails if the leaf exists. A preliminary existence
check followed by Directory.CreateDirectory is not sufficient. Do not use
recursive directory creation for the final leaf or accept an existing empty
leaf. On a conflict/failure, stop without choosing an alternate destination.

The following Node core operations are explicitly allowed after parent and
containment validation. Use the installed Node and invoke only a task-owned
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

Pass the JavaScript as literal input, for example through a single-quoted
PowerShell here-string to Node stdin. Preserve JavaScript backticks and dollar
signs; do not embed it in an interpolating shell string.

Retain the exact invocation, returned output and actual execution-tool status.
Do not hard-code a successful tool exit into a later report. If creation
succeeds but receipt writing fails, preserve the partial directory and stop.
Use CreateNew / ‘wx’ semantics for all new evidence files and exclusive copy
semantics for baseline copies. Write final artifacts once; use distinct names
for intermediate captures rather than overwriting them.

API reference: Node.js filesystem directory creation.
The helper illustrates leaf creation only; it does not replace the required
parent, containment or redirection checks.

This fresh receipt proves only this task’s operation. Do not relabel earlier
nonexclusive creation as exclusive or claim that earlier evidence was corrupt
merely because its exclusivity was unsupported.

5. Exact repair requirements

Read all of runTest.ts, the policy module and producer, plus every canonical
policy/relation declaration and relevant consumer. Resolve both runtime import
paths to the actual module using the existing compiler layout; do not copy a
report’s shorthand import spelling into code.

The repaired canonical policy must cover:
out/test/b3OutcomePolicy.js

Its source/artifact relationship must bind:
src/test/b3OutcomePolicy.ts -> out/test/b3OutcomePolicy.js

Use the existing representation and ownership model. Add the compiled path
exactly once. Add or correct its relation exactly once. If the established
model also requires explicit protection of the matching TypeScript source,
the corresponding src/test/b3OutcomePolicy.ts entry is authorized within the
same declarations. Make no other membership expansion.

Preserve all existing protected entries and relations, their relative order
and the canonical normalization convention. Do not add a broad glob, protect
an entire directory, remove another entry, add an exception, or weaken a
missing-file/hash check. Do not protect the unit-test artifact merely because
it shares a basename prefix.

Trace how the protected manifest, counts, digest and final comparisons derive
from the canonical policy. Their future runtime values must include the new
member consistently. If values are derived, preserve that derivation. If
declarative expected membership/count data must change, change only the
necessary data within runTest.ts and explain the dependency. Do not insert a
fabricated hash, special-case a comparison to pass, or rewrite algorithmic
behavior to accommodate an absent artifact.

The compiled module is currently reported absent because repository emit was
not authorized. Verify that state read-only. Keep the policy entry even while
it is absent: a later authorized build/provenance gate must establish the
artifact before a qualified run. Do not create a placeholder, compile just
that file, copy previously emitted unit-test JavaScript into out/, exclude it
from the policy, or record missing as verified.

Do not change:

• Focused delivery, protocol version/nonce, eligibility, retained observation,
abnormal-exit attribution, cause keys/merge, verdict or exit logic.
• src/test/b3OutcomePolicy.ts, its unit tests, src/test/suite/index.ts,
the focused suite, guard or discovery patterns.
• M2 writers/destinations/reduced filename/dual-error handling; M3 authorization
or stages; A3 schemas/post-exit ordering; B4 environment handling.
• EXPECTED_VSCODE_VERSION, package/configuration/dependency files, build outputs,
historical evidence, navigation/reference documents or product code.

Preserve LF in runTest.ts; no whole-file formatting or line-ending changes.
If the required policy correction cannot preserve these boundaries, stop with
the concrete coupling rather than modifying adjacent accepted behavior.

6. Static verification and evidence

Perform data-only/static checks appropriate to this declaration change:

• Exact old/new membership set difference and duplicate check.
• Exact old/new source/artifact relation difference and coverage of both
runner and producer imports.
• Existing path/relation preservation and canonical path form.
• Every count/manifest/digest consumer’s source-level dependency on the updated
canonical data, without executing that consumer.
• Task-only diff against the new pre\ copy, including normal,
whitespace-ignored and CR-at-EOL-ignored numstats.

Read TypeScript literals as data only; never evaluate runTest.ts, its emitted
JavaScript, the policy module or the producer to obtain the lists. If a
data-only extraction cannot resolve an expression safely, inspect its source
or report the limitation. Do not introduce a test-only policy implementation.
No new test is required for this declaration-only task and none is authorized.

Capture per-file hashes for out/** and any existing configured output roots
and build-info before/after, along with configuration, preservation inputs
and prior evidence actually read. Prove that only runTest.ts changed in the
repository and that all old evidence consumed by this task stayed unchanged.
Record absent paths distinctly from empty directories and inaccessible paths.

Create policy-coverage.json containing observed before/after declaration data,
the one dependency’s source/artifact mapping, the exact set/count deltas and
source locations. Label any planned manifest or count as STATIC_DECLARATION_DATA.
This artifact is not the runner’s generated runtime protected manifest.
Do not manufacture a file-content digest when the compiled artifact is absent.

Save baseline.json, post-state.json, task.diff, path-reconciliation.md,
policy-coverage.json, creation-receipt.json, supporting measurement records
and report.md under the new task root. Serialize strict valid UTF-8 JSON.
Use display wrapping for screenshots; do not insert literal newlines into
JSON strings. Preserve failed/partial evidence without cleanup or replacement.

7. Completion and next gate

Success requires authenticated immediate source identity, the exact policy and
relation correction, consistent static consumption, preserved scope, reconciled
path observations and retained exclusive-creation evidence. It does not require
recovering missing historical folders, building the module or running tests.

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

The next independent reviewer must assess this exact small policy diff,
path reconciliation and new evidence-creation proof. Do not self-accept or
perform that independent review in this task. After its acceptance, a separately
authorized gate must build and prove the exact compiled dependency/manifest
and establish the pinned VS Code 1.135.0 contract before Host qualification.
Do not change the pin to 1.136.1 as a shortcut.

Give a concise chat summary with the exact report path and any blocker, then
stop. Leave source and evidence intact for the independent reviewer.
