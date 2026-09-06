TASK\_ID: ETL\-0906\-B3\-REPAIR\-TEST01
TYPE: BOUNDED B3 REPAIR WITH LOCAL UNIT TESTS — NO RUNNER OR HOST
STATUS: EXECUTION BRIEF; IMPLEMENTATION AND EXECUTION HAVE NOT STARTED

Run in a normal LOCAL VS Code Agent chat on Windows, in the active worktree
below\. Do not use the ETL Orchestrator\. This is implementation, not independent
review\. The implementer may continue within this task; the eventual reviewer
must be independent\. Do not launch a second writer\.

## 1\. Owner\-approved change to the working method

The owner approved package 1: close the five independently reported B3 defects,
with early local tests and, if needed, a small side\-effect\-free extraction\.
This brief supersedes the older SOURCE\-ONLY / ONE\-FILE / NO\-TEMP\-COPY rules
ONLY for the operations explicitly allowed here\. It does not authorize the
other architectural proposals, global documentation updates, or later gates\.
Known differences in those older permissions are intentional, not a blocker\.
Unresolved differences in baseline identity or behavioral requirements ARE blockers\.

Required context: read this entire brief and the verified external glossary
at C:\\docs\\ETL\_QUALIFICATION\_GLOSSARY\.md\. Use its stable definitions, not its
superseded next\-task/execution restrictions\. The five findings and reviewed
baseline below are carried forward from
ETL\_DELTA\_2026\-09\-05\_B3\_REMAINDER\_INDEPENDENT\_REVIEW\.md
&#40;review ETL\-0904\-REVIEW\-B3\-REMAINDER, NOT\_ACCEPTABLE, 2026\-09\-05&#41;\.
Read the full report if locally available; its absence is not permission to
invent details and need not force Library access from the local Agent\.
Do not require reconstruction of every historical handoff\.

Before editing, read the entire live runTest\.ts, the actual result producer in
src/test/suite/index\.ts, its focused\-suite constants, the Mocha guard located by
symbol search, and the relevant existing local test/compiler configuration\.
Read producer/guard sources as evidence; do not modify them\.

## 2\. Exact authorization

|Area            |Allowed                                                                                                                                                     |
|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Existing source |Surgical edits to src/test/runTest.ts, B3 seams only                                                                                                        |
|Small extraction|Create src/test/b3OutcomePolicy.ts: only pure B3 functions/types consumed by runTest.ts                                                                     |
|Tests           |Create src/test/b3OutcomePolicy.unit.test.ts: tests of those actual functions, not a copied implementation                                                  |
|Diagnostics     |Read-only identity/status/hash/diff/process/source/configuration inspection                                                                                 |
|Type analysis   |Direct use of the already-installed local compiler for no-emit integration checks, with all persistent caches/build-info writes disabled                    |
|Test-only emit  |Compile only the pure helper, its test and necessary side-effect-free dependencies into the fresh external task root                                        |
|Execution       |Run only that explicitly selected local unit-test entrypoint using already-installed tooling                                                                |
|Evidence        |Create pre-edit copy, machine baseline, test configuration/fixtures, build output, per-attempt logs, diff and report ONLY under the fresh external task root|

Use the two exact new source paths above; verify they do not already exist,
including ignored/untracked files\. No package\.json, lockfile, tsconfig, suite
registration, barrel export, existing test, dependency or tool installation
change is authorized\. If the extraction cannot fit these boundaries, stop\.
Do not extract unrelated runner code or build a new testing framework\.
Preserve the existing encoding and line endings; no whole\-file normalization\.

NEVER execute/import/evaluate runTest\.ts or emitted runTest\.js\. Compiler
analysis of that source is allowed; module execution is not\. Inspect the test’s
transitive runtime imports before execution: no vscode, Extension Host,
@vscode/test\-electron, extension activation, network, credentials or consumer
data\. Test/helper code must not launch child processes\. Tool\-managed unit\-test
workers may execute only the same selected pure test closure; record their
entrypoint/arguments\. No import trick, VM evaluation or text\-extracted
copy of the runner may substitute for a testable production\-consumed helper\.

No runner, Host, parser/product execution, VSIX build/package/install, lint,
formatter, dependency download, npm/npx lifecycle script, Git mutation, commit,
push, merge, release, permission bypass, or pending\-editor\-edit resolution\.
Use git –no\-optional\-locks for Git reads\. Read\-only Git configuration queries
are permitted; never change configuration or hooks\.

Preserve M2 paths/containment/CreateNew/write ordering/dual\-error handling;
M3 freshness/dedication/authorization and all eight accepted stage assignments;
finalization\-stage schema; non\-B3 finalization flow; post\-exit count/order;
full/reduced non\-B3 schema; B4/M1/M4/M5/C1/C2/B1 and protected\-set policy\.
B3\-only classifier, validator, ledger and verdict wiring inside the existing
finalization seam may change\. Do not reorder its non\-B3 operations, fix R14/R16,
or broaden output schemas\. An internal immutable B3 observation may replace
B3 re\-evaluation; this does not authorize rewriting unrelated finalizer reads\.

## 3\. Preflight and machine\-anchored baseline

Active worktree:
C:\\repos\\etl\-extension\\etl\_fw2\\recovery\-extension\-product\-0\.3\.147
Linked primary:
C:\\repos\\etl\-extension\\etl\_fw2\\etl\_framework\_extension\_hf1\_v2
Branch: fix/workspace\-write\-completion\-0\.3\.148

Expected porcelain status &#40;leading space means unstaged modification&#41;:

```text
 M .github/templates/request.md
 M src/core/sttm/SttmUnderstandingReportRenderer.ts
 M src/extension.ts
 M src/test/runTest.ts
 M src/test/suite/index.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts
```

The following pins were extracted from retained text records, not transcribed
from screenshots\. Verify live bytes; never replace expected values with live
hashes merely to pass preflight\.

```json
{
  "glossary_bare_cr": 0,
  "glossary_bare_lf": 587,
  "glossary_bytes": 25565,
  "glossary_crlf": 0,
  "glossary_sha256": "537F32326590454D1070CE6AB32315240ABCCE4CE8C604F0C8AEC65AD4AB749E",
  "head": "45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19",
  "reviewed_runTest_bare_cr": 0,
  "reviewed_runTest_bare_lf": 2903,
  "reviewed_runTest_bytes": 126214,
  "reviewed_runTest_crlf": 0,
  "reviewed_runTest_sha256": "9F865D703AB8C0FEAB453D62C2E26491DC6639F95423F2470473722808740089",
  "snapshot01_manifest_sha256": "78324A99A5D700053214B15F680E2DCBE3A2099A0801C43B6D02E512D43004DF"
}
```

Snapshot01 root:
C:\\Users\\tag5916\\ETL\-SNAPSHOT\-ETL\-0904\-SNAPSHOT01\-20260904T210831Z
Manifest: manifest\.json under that root\.
Cumulative baseline: payload\\worktree\\src\\test\\runTest\.ts under that root\.

Before any source/evidence write:

- Verify active/linked worktree identity, branch, HEAD, exact six\-path inventory,
  empty staging, and no index\.lock in worktree/common Git metadata\.
- Verify no actual active test/development Host invocation\. Exclude ordinary
  editors, inspection commands, prompt text and ordinary source\-path matches\.
- Verify the manifest hash, valid JSON, task identity ETL\-0904\-SNAPSHOT01,
  COMPLETE status and unchanged source\-history value YES\. Read the actual
  property paths; do not require an uppercase display label to be a JSON key\.
- Verify the Snapshot01 payload hash/size against its manifest\. Compare the
  five out\-of\-scope dirty files to their manifest hashes/sizes\.
- Verify current runTest\.ts against the REVIEWED pin above, NOT Snapshot01\.
  It is expected to differ from Snapshot01\. The reported cumulative numstat
  is \+280/\-103; measure it and explain any discrepancy without changing bytes\.
- Verify the glossary pin and its canonical location outside both worktrees\.
- Capture SHA\-256, bytes, CRLF/bare\-LF/bare\-CR for all six dirty files\.
  Record hashes/inventory for package/config/lock files and existing configured
  build/test output roots, including out/\*\*, for post\-task comparison\.
- Verify both new source paths are absent\. Inspect package scripts, compiler
  options, test discovery and runtime import closure before selecting commands\.

Stop on identity, staging, dirty\-set or source\-baseline mismatch:
BLOCKED\_BASELINE\_DRIFT: <expected> <observed>
Stop on absent/invalid baseline or glossary:
BLOCKED\_REFERENCE\_NOT\_VERIFIED: <path> <reason>
Stop on actual Host/lock/concurrent source change:
BLOCKED\_ACTIVE\_PROCESS\_OR\_CONCURRENT\_CHANGE: <evidence>
Do not repair/rebase a baseline, clear a lock, stop somebody else’s process,
resolve an editor change, or infer permission from a matching diffstat\.

After all preflight checks pass, create ONE fresh unique task root:
C:\\docs\\ETL\-0906\-B3\-REPAIR\-TEST01<UTC\-timestamp\>\-<GUID>
First prove its existing parent resolves outside both worktrees, Snapshot01,
and consumer/protected roots\. Reject redirected/unsafe destinations; do not
choose another location silently\. Create new task\-owned directories only\.

Create a byte\-for\-byte pre\\runTest\.ts copy with CreateNew semantics\. Hash it
and the live source again; both must match the reviewed pin\. Write baseline\.json
with the verified paths, anchor provenance, six\-file measurements and identity\.
This preserves a verified present baseline; it is NOT a replacement historical
snapshot\. Local History hunting is unnecessary\. Keep all failed\-attempt logs
in separate new subdirectories; no overwrites or cleanup of previous evidence\.
Recheck baseline immediately before the first source edit\.

## 4\. Five repairs and the preserved outcome contract

B3 is the canonical verdict, classification, precedence, accumulation,
cause\-based deduplication and verdict\-to\-exit policy\. M2 is evidence persistence;
M3 is authorization plus last\-completed\-stage behavior\. A3 owns adjacent
finalization/schema/post\-exit work and is NOT authorized here\.

|Finding  |Required closure                                                                                                                                                                                                                                                                    |
|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|F1 / B3-4|Remove global-ledger-emptiness eligibility. Product failure plus an independent runner mismatch retains both, gives infrastructure priority, BLOCKED and nonzero exit.                                                                                                              |
|F2 / B3-3|Prove focusedMode === true, authorized focusedSuiteFile, exact expected suiteTitles and loadedFiles, rejecting missing/foreign/duplicate/additional identities under the producer’s actual normalization semantics. Expectations must not come from the untrusted result itself.    |
|F3 / B3-2|Preserve class precedence and define a total deterministic primary-row order over immutable data. The same cause multiset gives identical primary class/stage/message for every arrival permutation. Resolve repeated observations deterministically too.                           |
|F4 / B3-3|Derive count equations and array/count relationships from the actual producer. Reject incoherent counts; do not assume a generic Mocha formula when the producer’s behavior differs.                                                                                                |
|F5 / B3-5|Retain one immutable B3 result observation, or prove equivalent observation identity and non-divergence. Keys must identify causes, not call sites, stage-only buckets or first-arrival order. Distinct same-stage causes coexist; repeated observations of one event collapse once.|

Preserve infrastructure \> product \> none\. Infrastructure implies BLOCKED;
trustworthy product failure with no infrastructure implies FAIL; PASS requires
the authorized, coherent focused result and no other failure\. A nonzero Host
or runner exit alone never creates product classification\. Preserve verdict
values and the existing verdict\-derived exit mapping, full/reduced B3
persistence, M2/M3 acceptance, and every distinct cause in failure\.all\.

Implement the minimum pure policy boundary needed for these five findings\.
Tests must exercise the actual eligibility/validation/reduction decisions used
by runTest\.ts, not an unused helper that leaves old gates at the call sites\.
Do not add serialized fields just for sorting/deduplication\. Do not invent
producer fields, change the focused suite’s eight\-test identity, or redesign
all producer/consumer schemas\. Stop if correct closure needs forbidden scope\.

## 5\. Local feedback loop — explicitly limited execution

After preflight, print a short non\-blocking execution plan: exact edit paths,
helper exports, selected compiler/test commands, input files and output paths\.
The owner has authorized this bounded lane; no additional approval round is
needed if it fits\. Permission failures or a need for wider access remain stops\.

Use existing local tooling directly, not package lifecycle scripts\. Disable
incremental/watch/cache writes; no emit into out/\*\* or elsewhere in the repo\.
A task\-specific compiler/test configuration may be CREATED inside the external
task root only\. Verify its input closure and output paths before invoking it\.
Compiler diagnostics for runTest\.ts are not execution of the runner\.
Before source edits, retain baseline no\-emit integration diagnostics under the
task root\. Use the same options after editing so pre\-existing errors can be
distinguished from regressions; do not treat an unavailable check as a pass\.

Prefer a behavior\-preserving extraction first, then demonstrate the known
failures with tests, then repair\. Record genuine pre\-fix red results when
available; do not claim red/green if only post\-fix tests ran\. A negative fixture
correctly rejected by a passing test is not a pre\-fix red result\.

Freeze expected outcomes from the producer and approved contract independently
of the implementation\. Do not generate expected results using the function
under test\. Add a deliberate invalid\-result/control case that would expose a
validator wired open\. Never weaken expectations to obtain green\.

Required local matrix &#40;use parameterized cases, not a new framework&#41;:

1. Valid authorized coherent zero/positive failures: PASS/zero and FAIL/nonzero
   respectively, absent infrastructure, according to producer semantics\.
2. Product \+ independent runner mismatch; product \+ supplied surviving\-PID
   observation; parent\-post\-exit \+ host\-evidence observations: retain causes
   and select BLOCKED/nonzero\. These are policy fixtures, NOT real PID tests\.
3. Each hostile focused\-mode/file/title/loaded\-file case, including duplicates
   and extra entries: infrastructure; no manufactured product attribution\.
4. Negative/noninteger/missing counts and producer\-specific cross\-count/
   array\-count contradictions, including tests=8, passes=8, failures=3,
   pending=0: reject\. Include coherent pending/hook cases if producer permits\.
5. Multiple same\-class causes in all permutations of a small fixed set:
   identical primary class/stage/message; no lossy accumulation\.
6. Same event observed twice: one cause; distinct events sharing stage AND
   message: both retained; duplicate observations with differing metadata:
   deterministic retained primary data\.
7. Mutation of the supplied source object or a simulated second observation
   cannot rewrite the retained B3 observation or create two cause identities\.
   Prove actual runner wiring uses that retained observation statically\.
8. Empty, missing, foreign or invalid evidence cannot yield a manufactured
   product PASS/FAIL\. Exit mapping agrees with each canonical policy verdict\.

Report individual cases, commands, exit codes and logs\. Iterate within scope,
retaining each attempt\. Missing local dependencies do not authorize installs\.
Run a no\-emit integration check using the existing project configuration with
persistent writes disabled\. Compare pre/post diagnostics where unrelated
baseline errors exist; do not fix them or report a failed check as passing\.
Unexplained new diagnostics or unresolved local test failures block success\.

## 6\. Preservation, attribution and stopping

Re\-read each changed hunk and enclosing flow\. Map all five findings to source
AND executable local cases\. Enumerate classification sites and demonstrate:
no remaining global\-empty\-ledger gate, first\-inserted primary, ambiguous cause
bucket, untrusted identity expectation or unvalidated count relationship\.
Show that helper imports are actually wired into all relevant runner seams\.

Compare M2/M3, all eight stage assignments, finalization/schema/post\-exit and
other preservation boundaries to pre\\runTest\.ts\. Unchanged text does not by
itself prove unchanged behavior through modified B3 inputs; trace the seams\.

Re\-hash the five out\-of\-scope dirty paths and protected/configured output roots;
prove they are unchanged\. Final staging must be empty\. Git status may contain
only the original six paths plus the two explicitly authorized new files\.
Do not create generated repository files, even ignored ones\.

Use pre\\runTest\.ts for TASK\-ONLY normal, \-w and –ignore\-cr\-at\-eol numstats\.
Report new helper/test additions separately, including untracked\-file contents\.
Use Snapshot01 only for the separate cumulative runTest\.ts comparison:
git –no\-optional\-locks diff –no\-index –numstat – “<Snapshot01 payload path>” “src\\test\\runTest\.ts”
Exit 1 means differences\. Do not use HEAD or an editor panel as the task baseline\.
Store the full task diff with verified endpoints; do not repeat whole files
in chat or investigate unrelated historical panel comparisons\.

If forbidden scope is needed, stop before editing when foreseeable, otherwise
stop when discovered without reverting prior authorized work:
BLOCKED\_SCOPE\_COUPLING: <file> <symbol> <requirement> <minimum expansion>
Tool/permission/output\-containment failures also stop; no bypass or silent
fallback\. Do not disguise a blocker as success or delete evidence to hide it\.

## 7\. Handoff and evidence boundaries

Save report\.md, baseline\.json, task diff and test/diagnostic logs under the
external task root\. report\.md should contain a five\-finding closure matrix,
exact commands/results, producer equations and identity rules, primary tie\-break,
cause\-identity mapping, preservation proof, final status and remaining risks\.
Chat handoff should be short and name the complete external report path\.

Keep evidence classes explicit:

- Executed pure\-policy tests: LOCAL\_UNIT\_TEST\_VERIFIED, only for exercised cases\.
- Runner integration without execution: STATIC\_SOURCE\_SUPPORT\.
- Actual M2 filesystem success/failure, M3 gate fault injection, Host/PID/API,
  real evidence files/stderr/process exits, packaged provenance and consumer
  behavior: UNVERIFIED\_UNTIL\_AUTHORIZED\_TARGETED\_TEST\.

A simulated write failure or exit\-code mapping is not proof of a real write or
process exit\. Nothing here qualifies the Extension or closes R14/R16/A3\.

End report\.md with factual values, never a prefilled claim:

```text
ETL_B3_REPAIR_TEST01_RESULT: IMPLEMENTED_WITH_LOCAL_TESTS_AWAITING_INDEPENDENT_REVIEW | BLOCKED_<REASON>
FILES_CHANGED_BY_TASK: <exact paths or NONE>
UNAUTHORIZED_FILES_CHANGED_BY_TASK: <actual count>
LOCAL_UNIT_TESTS: <passed/failed/not reached, case counts>
PRE_FIX_RED_EVIDENCE: <observed/partial/not obtained, reasons>
NO_EMIT_INTEGRATION_CHECK: <passed/pre-existing failures/new failures/not reached>
PRESERVATION_BOUNDARIES: <each YES/NO/NOT_VERIFIED with evidence>
RUNNER_OR_HOST_EXECUTED: <YES/NO; NO required>
PACKAGE_INSTALL_GIT_MUTATION_OR_RELEASE_EXECUTED: <YES/NO; NO required>
PENDING_EDITOR_CHANGES_RESOLVED: <actual; NONE required>
HOST_AND_CONSUMER_QUALIFIED: NO
NEXT_REQUIRED_GATE: <INDEPENDENT_REVIEW_B3_REPAIR_TEST01 if successful; OWNER_SCOPE_DECISION if blocked>
```

Choose ONE result value\. Success requires all five closures, passing required
local cases, no unexplained new diagnostics and preserved scope\. Independent
review remains mandatory and is not performed by this task\. Stop after handoff\.
