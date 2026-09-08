TASK\_ID: ETL\-0908\-B1\-TARGET\-ENTITY\-REPAIR01
TYPE: BOUNDED B1 REPAIR, REGRESSION VERIFICATION AND ONE FOCUSED HOST RUN

Run this complete prompt in a fresh ordinary LOCAL Windows VS Code Agent chat
on the active recovery worktree below\. Use one Agent and one writer, not the
ETL Orchestrator\. Keep code, tests and engineering evidence in English\. Echo
TASK\_ID as the first line of the report\.

## 1\. Owner authorization and intended outcome

The owner authorizes the next bounded B1 task following independent review
ETL\-0908\-FOCUSED\-HOST\-INDEPENDENT\-REVIEW01:

1. Verify the reviewed target\-entity alias defect against current disk bytes\.
2. Add the missing `target table name` alias while preserving existing aliases
   and their relative order\.
3. Verify the real parser through focused unit regression cases\.
4. Produce a checked staging build and promote only the necessary compiler
   artifacts corresponding to the repaired parser\.
5. After the prerequisites below pass, invoke the existing focused runner at
   most once, using the already prepared VS Code 1\.135\.0 and synthetic fixture\.
6. Preserve evidence and report B1 results separately from remaining C1/R3/R4
   failures\. Independent acceptance remains a later task\.

This prompt supplies the bounded source, test, compiler, output\-promotion and
single\-run authorization\. Historical no\-edit/no\-run restrictions described
what those earlier tasks could do; they do not prohibit these explicitly
authorized operations\. Do not ask for the same permission again once the
prerequisites pass\. Complete useful independent work if a concrete prerequisite
blocks the Host, and report exactly what remains unexecuted\.

This is not an omnibus repair or a fix\-and\-rerun loop\. No C1 instrumentation,
runner/policy repair, assertion weakening, version change, dependency change,
package/configuration edit, broad test discovery, Git mutation, download,
installation, packaging, release or ordinary consumer workflow is authorized\.

## 2\. Workspace and evidence to read

ACTIVE\_WORKTREE:
C:\\repos\\etl\-extension\\etl\_fw2\\recovery\-extension\-product\-0\.3\.147

LINKED\_PRIMARY &#40;read\-only identity boundary&#41;:
C:\\repos\\etl\-extension\\etl\_fw2\\etl\_framework\_extension\_hf1\_v2

Expected branch: fix/workspace\-write\-completion\-0\.3\.148
Expected HEAD: 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19
Expected staging: empty\.

Expected intake dirty inventory:

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

Resolve the completed review by TASK\_ID
`ETL-0908-FOCUSED-HOST-INDEPENDENT-REVIEW01`\. Bounded discovery of direct
`C:\docs` children with that exact task prefix is authorized, including one
timestamp child if necessary\. Select using report contents and referenced
RUN01 identities, not simply the newest directory name\.

Read its complete report\.md, review\-result\.json, comparison\-cause\-map\.json,
evidence/copy inventories, manifest\-revalidation\.json, pinned distribution
comparison and preservation results\. Resolve actual filenames through the
report when needed\. In particular, read the B1 trace, C1 limitations, R3/R4,
R5, and the proposed next scope\. The expected review decision is
ACCEPTABLE\_WITH\_MATERIAL\_LIMITATIONS; verify the actual record\.

Resolve RUN\_TASK\_ROOT, RUN\_ROOT, PREP\_ROOT and BUILD\_ROOT from those original
machine records and their referenced reports\. The earlier review prompt had
a mistyped BUILD\_ROOT GUID\. Do not reuse that literal, transcribe another
GUID/hash from screenshots, or substitute a newly measured file for an expected
identity\. Record actual resolved paths and how they were authenticated\.

Read RUN01’s complete report, frozen execution\-plan\.json, fixture\-resolution,
baseline/post\-state, supervisor source/status, raw stdout/stderr and the four
raw result/manifest files\. Read the preparation’s measured host/future plan and
the build’s actual compiler, input/output and promotion provenance\. Reuse the
review’s preserved copies when original transient evidence is unavailable,
only when its recorded original/copy hashes establish the correspondence\.
Do not rerun a helper from an old task directory merely because it exists\.

Read applicable repository instructions and
`C:\docs\ETL_QUALIFICATION_GLOSSARY.md`\. Read the complete relevant parser,
its Excel adapter and the selected unit entrypoint’s runtime dependencies\.
For Host execution, read the complete existing focused suite, producer and
relevant runner/policy branches\. Read configuration/build scripts as data\.

Existing exact QA locator, subject to recorded identity verification:
C:\\Users\\tag5916\\AppData\\Local\\Temp\\etl\-w1\-qa\-20260901\-054832\-c5e982

The established fixture is `sttm/synthetic_workbook.xlsx`, 13201 bytes, in the
23\-file synthetic QA workspace\. Read the full expected hash and companion\-file
contract programmatically from authenticated evidence/current constants\.
The verified RUN01 QA copy is an allowed alternative byte source if its
original/copy identity is established\. Do not repeat broad fixture searches\.

If evidence needed for a particular action is missing or inconsistent, finish
the checks that remain possible and report that precise limitation\. Do not
repair old reports, invent missing measurements or reconstruct unrelated
historical baselines to keep this task going\.

## 3\. Exact mutation and execution boundary

Only these repository source files may be changed by this task:

|Path                                       |Permitted change                                                                                 |
|-------------------------------------------|-------------------------------------------------------------------------------------------------|
|src/core/sttm/SttmMarkdownBundleParser.ts  |Add one alias to the existing targetEntity alias list; no other production change.               |
|src/test/sttmTargetEntityAlias.unit.test.ts|One dedicated unit regression file for this B1 contract, selected explicitly for local execution.|

The unit path is intended to be new\. Check tracked, untracked and ignored state
before creating it\. Do not overwrite an unexpected existing file or bypass an
ignore rule\. This test must remain outside the focused `suite/` discovery set;
verify the real test patterns without changing registration/configuration\.

Preserve all eight pre\-existing dirty paths byte\-for\-byte, including the
renderer, extension\.ts, runTest\.ts, b3OutcomePolicy\.ts, its unit tests, suite
index and the focused Host test\. Do not edit SttmResolvedEvidence, the Excel
adapter, reference resolver, consumers, fixture, expectations or comparison
classification\. Do not add an export or refactor columnAt to make testing easy\.

Other allowed writes:

- One new external TASK\_ROOT under C:\\docs, for evidence, immutable pre\-copies,
  compiler staging, explicit unit\-case data and a verified synthetic QA copy\.
- Compiler\-generated companions for the one repaired parser under the active
  worktree’s out/, after the frozen promotion gate in section 7\. No other
  runtime artifacts may be replaced\. Identical companions are not rewritten\.
- One new RUN\_ROOT below the actual system temporary directory, as required
  by the existing runner, for the single focused Host’s state and evidence\.

Unit execution may load the real parser and its inspected pure/data\-processing
dependencies and read the authenticated synthetic workbook\. It may not start
VS Code, a launcher, child workloads, the extension, producer, runner, network
or consumer jobs\. The separate one Host invocation permits the product
activation/parsing already required by the unchanged focused suite only\.

Do not execute npm/npx lifecycle scripts, a formatter/linter/watcher, install
anything, edit generated JavaScript, clean out/, change build\-info, write to
the linked primary, modify the prepared Host or overwrite earlier evidence\.
Do not resolve editor buffers with Keep/Undo/save/revert\. Read disk bytes; an
editor view served stale code in earlier work\.

## 4\. Preflight, root creation and frozen baseline

Use `git --no-optional-locks` for reads\. Verify actual worktree/common\-Git
identity, HEAD, branch, staging and the complete dirty inventory\. Inspect
relevant locks and process arguments for an actual concurrent writer/compiler/
watcher/test Host; an ordinary editor/language server alone is not a blocker\.
Do not remove locks or terminate unrelated processes\.

Authenticate parser source and output against available reviewed/build input
records\. Capture a new task baseline before any task edit; do not confuse this
intake capture with authentication of an earlier baseline\. Unexplained drift
must be reconciled before editing, promotion or launch; do not normalize it\.

Validate C:\\docs and create one flat, exclusive new leaf:
`C:\docs\ETL-0908-B1-TARGET-ENTITY-REPAIR01-<UTC>-<GUID>`\.
Use `fs.mkdirSync(leaf, { recursive: false })` or an equally exclusive creation,
not check\-then\-Directory\.CreateDirectory alone\. Verify parents/reparse points
and containment outside worktrees, previous evidence, QA and editor profiles\.
Write a creation receipt with exclusive new\-file semantics\. Preserve a partial
failure rather than reusing another task root\.

Inventory raw hashes, sizes and line endings for edited/read source inputs,
all existing dirty files, used configuration/dependencies, the complete out/
tree, build\-info, consumed prior evidence, original QA and prepared Host files
relevant to the run\. Reuse authenticated recorded expectations; current hashes
are observations\. Existing output count was 2020, but per\-file identities govern\.

Save and verify byte\-exact pre\-copies of the production edit target and any
output that might be replaced\. Keep the source baseline, new test, helpers,
compile/test attempts, diagnostics and journals distinguishable\. New task JSON
must be strict BOM\-free UTF\-8; do not alter original artifact encodings\.

## 5\. Establish the B1 boundary and write a behavioral regression

The review’s static trace identifies the targetEntity column lookup in
SttmMarkdownBundleParser\.ts &#40;reported near line 985&#41;\. Locate the symbol and
actual code; line numbers are navigation hints, not edit coordinates\.

Verify that the source lookup includes `source table name`, while targetEntity
currently accepts `target table or filename` and `target table file name` but
omits `target table name`\. Verify normalization and columnAt’s exact/fallback
ordering\. The fixture’s actual `Target Table Name` value is `tgt_customers`\.
Do not infer the fixture contract from a test assertion alone\.

Use the existing public parser API\. Trace the Excel\-to\-bundle delegation and
result shape, and write one isolated unit entrypoint that exercises real
observable parser results\. Do not copy the alias algorithm into a helper or
test a separately reconstructed parser\. Do not mock the mapping result\.

Minimum cases:

1. Parse the authenticated, unchanged 13201\-byte workbook using the actual
   Excel adapter/delegated parser path\. For `FM_F01417B0_0002`, require
   `targetEntity === 'tgt_customers'`; also preserve the fixture’s source and
   target database/field identities as defined by the real result schema\.
2. Verify the existing `target table or filename` header still binds\.
3. Verify the existing `target table file name` header still binds\.
4. Verify existing alias precedence when old/new candidate columns coexist,
   using distinct values so a changed winner is observable\. Derive expectations
   from the existing ordered behavior; do not rewrite columnAt semantics\.
5. Verify that a genuinely absent target\-entity column retains the existing
   missing\-value behavior, rather than borrowing the source entity or inventing
   a table name\.

Cases 2–5 may use minimal in\-memory bundle/Markdown inputs through the real
public bundle\-parser API, or clearly labeled task\-local derived unit fixtures
when that API requires files\. Those variants are unit data only\. Never alter
the authenticated workbook, the 23\-file QA source, Host fixture hash/pins or
the Host workspace to accommodate the fix\. Do not broaden into unrelated
parser functionality\.

Pass the absolute authenticated workbook location to the explicit unit process
using a task\-local parameter/environment value recorded in its plan\. Do not
hard\-code a user’s temporary absolute path into the reusable repository test\.
Keep the test from requiring the runner, producer or extension entrypoints\.
If a real runtime dependency prevents a pure parser unit run, report that
specific dependency; do not simulate a fake Host or silently run integration
tests as a substitute\.

## 6\. Red/green verification and the one\-line production fix

Use the existing installed Node, TypeScript and Mocha, resolved by exact paths
inside the current environment/repository\. Do not install or select global
replacement tools\. Inspect the new test’s transitive runtime closure before
execution and record exact entrypoint/dependency resolution\.

Compile the pre\-fix source with the new regression test into external staging\.
Keep source/configuration logical paths and compiler semantics intact; section
7 defines checked emission\. Run exactly the compiled new unit entrypoint using
the installed Mocha with config/package/implicit discovery disabled\. Explicit
child\-local dependency resolution to existing node\_modules is allowed when
staging is outside the repository\. Do not discover directories or load old
compiled repository tests by accident\.

The original\-workbook assertion must fail for the observed missing targetEntity
reason, with a successful compile and the legacy behavior cases passing\. Record
the actual results; do not prescribe an artificial failing count\. A compiler,
loader or fixture error is not behavioral red\. If the regression already passes
on authenticated pre\-fix source, investigate the premise read\-only before any
production edit; do not force a red result\.

Apply only the reviewed production edit: append `target table name` to the
existing targetEntity alias list\. Preserve the exact two previous aliases and
their relative order, so the new alias is a fallback behind existing matches\.
Keep the file’s encoding and line endings\. No file\-wide rewrite/formatting,
source\-side change, projection workaround or mapping\-ID special case\.

Compile post\-fix source into a separate staging attempt and run the same unit
test source and cases\. Require all B1 unit cases to pass\. Preserve pre/post
source/test hashes, exact diff, compiled input/output provenance, actual
commands, exits and raw logs\. Do not weaken tests between red and green\.

Correct a concrete new\-test/helper defect if needed, retain the failed attempt
and rerun only affected verification\. If the test changed after the red run,
re\-establish red with the final identical test against the immutable pre\-fix
parser using external staging, without restoring old source over the repository\.
Do not repeat successful tests merely to accumulate evidence\. If a one\-alias
repair does not satisfy the real contract, preserve the result and propose the
smallest separate scope; do not widen production changes\.

## 7\. Checked build and minimal output promotion

Use the installed TypeScript Compiler API with the actual resolved tsconfig\.json
&#40;including extends/references&#41;\. Read package scripts but do not run them; the
previous compile script deleted out/\. Use a normal checked Program, collect
configuration/syntactic/global/semantic/emit diagnostics, and require no errors
and a successful emit\. Do not use transpileModule as build qualification\.

Resolve the compiler by absolute path within ACTIVE\_WORKTREE/node\_modules\.
Use noEmitOnError=true and prevent incremental/build\-info persistence in the
task invocation without changing repository configuration\. Preserve existing
target/module/module\-resolution/rootDir/outDir semantics and logical source\-map
layout\. If project references require an incompatible write mechanism, report
the coupling rather than silently changing the build model\.

Intercept every physical compiler write into a separate TASK\_ROOT staging tree\.
Do not allow default repository writes\. Capture the actual compiler input bytes
consistently, configuration/tool identities, source/output associations and
staged hashes\. Respect emitted BOM/source\-map bytes exactly\. Staging the whole
configured program for a checked build is permitted; promoting all of it is not\.

The successful post\-fix staging build used for green unit verification may also
supply the runtime output; no duplicate successful build is needed if its inputs
and artifacts remain unchanged\.

Freeze promotion\-plan\.json before any repository output write\. Its permitted
destinations are only the compiler’s artifacts for
`src/core/sttm/SttmMarkdownBundleParser.ts` under the active out/ tree, including
source\-map/declaration companions when actually emitted\. Establish association
from compiler outputs/source maps, not a hand\-written naming rule\. The new unit
test and its staged dependencies stay outside repository out/\.

Verify the repaired parser’s runtime dependency path and the existing runner,
producer, focused suite, extension and canonical protected artifacts\. Their
source/output state must agree with the authenticated accepted build except
for the explicitly repaired parser\. A staged difference in an unrelated required
runtime artifact is a concrete discrepancy to reconcile, not permission to
replace it\. Unrelated staged outputs do not authorize unrelated promotion\.

Before promotion, recheck inputs, repository identity, process/lock state and
destination pre\-hashes\. Preserve exact pre\-output copies, skip byte\-identical
files, write only the frozen necessary set, and verify every promoted file by
read\-back hash\. Retain an ordered journal\. On an unexpected write/drift/failure,
stop further promotion, preserve partial state, and do not launch the Host or
perform an automatic restore/cleanup\.

Prove that the promoted parser came from this repaired source\. Preserve all
existing out/ files not in the promotion plan; no deletions\. Canonical protected
membership/order and source\-artifact rules remain unchanged\. If this parser is
outside that policy, supply its additional build provenance without expanding
the policy or claiming the canonical digest alone authenticates the repair\.

## 8\. Prepare the one controlled focused run

Proceed when B1 red/green evidence, checked emit/promotion, source/output
stability and the existing focused\-run prerequisites are satisfied\. C1/R3/R4
being unresolved is expected and does not by itself block this B1 measurement\.
Do not hide a new unrelated defect under those known labels\.

Use the measured RUN01 plan and actual current runner contract\. Produce a new
execution\-plan\.json with resolved absolute paths, argument arrays, nonsecret
environment, expected suite/fixture identity, manifest strategy and process
supervision limits\. Inspect/reuse the logic of prior helpers as source; create
new task\-owned helpers rather than executing scripts that write into old roots\.

Use the already verified VS Code 1\.135\.0 Windows x64 distribution from PREP\_ROOT\.
Read its executable path/version/commit/hashes from original records, accounting
for its commit\-prefixed application directory\. Verify against the independent
archive\-to\-disk inventory and current bytes\. Do not use the everyday 1\.136\.1,
download fallback, Code –version smoke launch or a replacement installation\.
Reuse the completed archive comparison evidence where identities still match;
do not repeat expensive archive reconstruction without a concrete discrepancy\.

Copy the exact authenticated 23\-file synthetic QA set into
`TASK_ROOT\qa-workspace` and verify source/copy identities\. Set
ETL\_F5\_QA\_WORKSPACE\_ROOT to that absolute path\. Unit variants must never enter
this Host workspace\. Preserve the original QA and all old run/evidence roots\.

Resolve actual os\.tmpdir&#40;&#41; in the runner’s child environment\. The reviewed
contract requires an already existing, empty isolation root below that directory
and uses allowRootCreation=false\. Create one new exclusive empty RUN\_ROOT there
with the required current naming/path properties, separate from TASK\_ROOT and
QA\. This task explicitly authorizes that disjoint root arrangement\. Record
creation ownership and receipt outside the required\-empty RUN\_ROOT\. Do not
create completion/authorization markers or pre\-populate its runtime evidence\.

Keep TEMP/TMP consistent with that authenticated contract; do not redirect them
in a way that changes os\.tmpdir&#40;&#41; and invalidates containment\. Configure supported
child\-local user\-data/extensions/log locations inside RUN\_ROOT\. Do not claim
exhaustive operating\-system filesystem isolation from these paths or flags\.

Re\-derive these parent settings from the current supported contract, then freeze
them for the child &#40;names below identify the established inputs&#41;:

- ETL\_TEST\_VSCODE\_EXECUTABLE\_PATH: the authenticated pinned Code\.exe\.
- ETL\_TEST\_VSCODE\_ISOLATION\_ROOT: the new empty RUN\_ROOT\.
- ETL\_TEST\_PROTECTED\_HASH\_MANIFEST: the supported fresh manifest path in RUN\_ROOT\.
- MOCHA\_RESULT\_FILE: the fresh supported result path in RUN\_ROOT\.
- MOCHA\_GREP: the unchanged focused characterization selector\.
- ETL\_F5\_QA\_WORKSPACE\_ROOT: the verified new QA copy\.
- ETL\_TEST\_ENABLE\_ISOLATED\_DEPENDENCIES and ETL\_TEST\_COPILOT\_EXTENSION\_PATH:
  the established isolated dependency activation and the pinned distribution’s
  bundled dependency, with the unchanged ordered development paths\.

Remove conflicting inherited test/fixture/selector values for this child only\.
Do not dump all environment variables\. Do not pre\-set runner\-owned nonce,
delivery, focused\-suite or other generated child\-only authorization fields\.
Do not change global environment/settings, everyday profiles or plugin installs\.
Read R5’s inherited MCP\-identity finding\. Use only existing supported child\-local
isolation controls; record residual metadata/log limitations honestly instead
of promising no inherited metadata or absolute offline operation\. No deliberate
external\-service, credential, real\-data or consumer workflow access is allowed\.

Retain the unchanged producer and exactly the existing focused suite:
`suite/sttmRealHostStructuredResult.test.js`, with the authored 8\-test identity
and its existing selector/validation\. Confirm this through actual constants,
compiled paths and discovery rules\. Do not add the new unit file to that suite\.

Let the actual canonical prelaunch path generate/read its legitimate fresh
run\-bound manifest, using the post\-repair output state and unchanged policy\.
Keep previous candidates/manifests immutable\. Reconfirm canonical reader
acceptance occurs before launcher execution and cannot be bypassed by an
intervening recovery branch\. Do not import the runner for a probe: its main&#40;&#41;
is unconditional\. A separate probe consumes the one permitted invocation\.

Define existing observations that prove reader acceptance, distinguishing direct
records, authenticated control\-flow inference and post\-hoc data validation\.
A hypothetical rejected\-manifest branch is STATIC\_COUNTERFACTUAL / NOT\_EXERCISED,
not an executed negative control\. No new negative run is authorized\.

## 9\. Execute once, supervise and assess the real B1 result

Launch the unchanged compiled runner exactly once with the frozen plan, using
the existing installed Node directly\. Canonical validation and its one focused
Host are parts of this same invocation\. No standalone producer/Mocha substitute,
extra Host smoke test, retry after rejection or automatic fix\-and\-rerun loop\.

Use the previously demonstrated 600\-second deadline and at most 30 seconds for
shutdown, validated against the current contract before launch\. Record command,
cwd, UTC times, stdout/stderr, tool completion, runner/Host process ownership
and actual exits\. Keep the owner informed at least once per minute during a
long run\. A supervisor may terminate only this invocation’s positively identified
process tree on deadline or a concrete boundary breach; never kill by generic
node\.exe/Code\.exe name or affect the everyday editor\.

If canonical validation rejects, preserve the actual failure and Host NOT\_RUN\.
Do not patch its manifest or launch again\. After any result, read\-only diagnosis
and preservation work remain authorized; another repair/rebuild/Host attempt
does not\.

Authenticate new\-run nonce, delivery completion, focused\-suite identity, fixture,
Host version and actual extension/worktree\. Verify finalization and parent
post\-exit checks\. Keep normal Host/launcher exit distinct from the parent runner
exit; do not infer PASS from a normal Host exit alone\.

B1 runtime evidence must show the original expected outputs from this run:

|Observable                                  |Required value                        |
|--------------------------------------------|--------------------------------------|
|Structured target for the pinned mapping    |target_db.tgt_customers.customer_name |
|Markdown first target                       |tgt_customers.customer_name           |
|Corresponding original B1 target comparisons|Match their unchanged expected values.|

Confirm source identity/other mapping fields remain consistent with the original
fixture contract\. Read actual raw Host/runner records and test identities;
do not print expected values as if they were observed\. Missing/unusable evidence
does not prove the repaired target behavior\.

Report actual tests/passes/failures/pending without prescribing a new count of
passing tests\. C1 parser\-observation assertions may still fail, and the unchanged
R3/R4 policy may still produce BLOCKED/exit 1\. Retain these outcomes verbatim\.
B1 can be supported by passing unit regressions and authenticated matching
runtime target evidence while the overall gate remains non\-green\. Conversely,
do not call B1 complete from a green build or an unrelated test pass alone\.

Do not set expected parser cardinality to zero, remove any existing assertion,
broaden comparison exclusions or relabel this historical run manually\. Shared
Host evidence provenance alone is not sufficient proof that all comparisons
are duplicate causes\. C1 diagnosis and R3/R4 causal\-policy repair remain separate\.

## 10\. Preservation, deliverables and stopping point

Re\-measure task input/output state after unit tests, after promotion and after
the Host as needed to attribute changes to the correct phase\. The repaired
source and promoted parser outputs must remain stable during Host execution\.
All pre\-existing dirty files, configuration/dependencies, build\-info, prepared
distribution, original fixture and consumed prior evidence remain unchanged\.

Account for every out/ change in the promotion journal\. Expect the original
eight dirty source paths plus the permitted parser modification and new unit
file, assuming the authenticated intake confirmed both were previously clean/
absent\. Preserve actual HEAD/branch/empty staging\. Report deviations rather than
using Git to clean up\. Preservation claims cover measured sets only\.

Keep a compact complete evidence package under TASK\_ROOT:

- report\.md, creation receipts, baseline\.json, post\-state\.json;
- evidence\-locator\-resolution\.json and original/copy identity records;
- exact task\-only source/test diff and immutable pre\-source copies;
- unit plan, red/green staging, identical test identities, logs and real statuses;
- compiler input/configuration records, diagnostics and staged\-output inventory;
- promotion\-plan\.json, pre\-output copies, ordered journal and build\-provenance\.json;
- QA copy inventory, pinned\-host verification, frozen execution plan and supervisor;
- raw stdout/stderr, measured process status, B1/result assessment and preservation\.

After the Host has settled, preserve verified byte\-exact copies of its four raw
manifest/result JSON artifacts and relevant Host logs under TASK\_ROOT, with
original/copy/after hashes and original absolute paths\. Keep originals in RUN\_ROOT
unchanged\. Do not copy unrelated credential/profile storage\. Preserve failed
attempts and issue separately named corrections rather than rewriting history\.

Use these result axes:

```text
TASK_ID: ETL-0908-B1-TARGET-ENTITY-REPAIR01
RESULT: B1_VERIFIED_AWAITING_INDEPENDENT_REVIEW |
        B1_SOURCE_AND_UNIT_VERIFIED_RUNTIME_UNVERIFIED |
        B1_NOT_VERIFIED | BLOCKED_<CONCRETE_REASON> |
        INCOMPLETE_PARTIAL_PROMOTION | INVALIDATED_BY_UNEXPECTED_CHANGE
PRODUCTION_CHANGE: <exact path and alias-only diff>
UNIT_REGRESSION: <real pre/post counts, exits, identical test-source evidence>
LEGACY_ALIAS_BEHAVIOR: <actual regression results>
CHECKED_BUILD: <compiler identity, diagnostics, emit status>
OUTPUT_PROMOTION: <exact actions and provenance>
RUNNER_INVOCATIONS_AND_HOST_LAUNCHES: <actual counts, expected at most 1 each>
CANONICAL_READER: ACCEPTED | REJECTED | NOT_REACHED | UNPROVEN
NEW_RUN_IDENTITY: <actual nonce, fixture and suite correlation>
B1_STRUCTURED_TARGET: <actual value or NOT_OBSERVED>
B1_MARKDOWN_TARGET: <actual value or NOT_OBSERVED>
B1_RUNTIME_COMPARISONS: <actual relevant matches/mismatches>
TESTS_PASSES_FAILURES_PENDING: <actual counts or NOT_EXECUTED>
RUNNER_VERDICT_AND_EXIT: <actual values, unchanged policy>
C1_OBSERVATION: <actual residual evidence; do not infer unmeasured module identity>
R3_R4_STATUS: NOT_REPAIRED_IN_THIS_TASK
FINALIZATION_AND_POST_EXIT: <actual outcome>
PRESERVATION: <measured sets and exact differences>
HISTORICAL_REVIEWED_BASELINE_PRESERVATION: NOT_VERIFIED
INDEPENDENT_B1_ACCEPTANCE: NOT_YET_GRANTED
FULL_B3_OR_RELEASE_ACCEPTANCE: NOT_GRANTED
REPORT_PATH: <absolute path>
NEXT_BOUNDED_TASK: <independent B1 review or concrete blocker; C1 remains separate>
```

The first result requires the alias\-only repair, genuine red/green regression
evidence with preserved legacy behavior, checked promotion/provenance and valid
new\-run evidence of both corrected target outputs, with preserved boundaries\.
It does not require the known C1/R3/R4 gate to become green\. Do not assign that
result when Host evidence is absent, stale or invalid, even if unit tests pass\.

Finish with a short chat summary: exact report path, changed source/output
files, unit outcome, observed structured/Markdown targets, actual overall
verdict/exit and remaining blockers\. Stop without self\-performing independent
acceptance, adding C1 instrumentation, repairing policy or releasing anything\.
