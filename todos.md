Task: LOCAL-PHASE-A0R-20260813-01
Mode: bounded Phase A0 repair and isolated executable verification
Target: extension-source
Delivery: source-only
Phase A1: PROHIBITED

Current evidence:

* Repository: TD-Universe/agentic_etl
* Branch: feature/v3-agentic-redesign
* Expected HEAD: b2e44c3a1a051aa7fa6008831d225bc06d22e847
* Committed package version: 0.3.139
* Protected dirty worktree package.json: 0.3.128
* Candidate and installed VSIX: 0.3.139, both PRE-A0 and unchanged
* Current Agent review card contains 8 pending Phase A0 files.
* Isolated validation results:
    * test TypeScript compilation: PASS
    * focused suites: 24 passing, 8 failing
    * registered grep run: 5 passing, 1 failing
* Phase A1 was not started.

Do not click Keep or Undo. Leave the current review card pending throughout this task.

Hard prohibitions

1. Do not start or implement Phase A1.
2. Do not stage, commit, push, merge, rebase, switch branches, edit PR #7, invoke CI, or perform any Git/PR/CI mutation.
3. Do not package, rebuild, install, uninstall, or replace any VSIX.
4. Do not install dependencies, build, test, or generate output inside the real repository.
5. Do not modify any Consumer workspace, Databricks/ADF/SQL resource, external system, workflow control plane, or packaged Copilot asset.
6. Do not modify these protected user-owned files:
    * .tsbuildinfo.test
    * package.json
    * CopilotAssetCatalog.ts
    * EtlActionToolService.ts
7. Do not restore RepoWriter-based workspace fallback.
8. Do not weaken the trusted-evidence gate or allow preview with incomplete evidence.
9. The direct /create planning route must not invoke:
    * RepoWriter
    * NewArtifactWriter
    * writeArtifacts
    * resolveWorkspacePath
    * process.cwd()
    * any filesystem write API
10. Do not delete, skip, quarantine, or weaken failing tests merely to obtain green output.

Preflight

Before editing, verify read-only:

* repository origin and resolved root;
* branch and exact HEAD;
* staged state and worktrees;
* complete current status;
* committed package version;
* current pending A0 diff and exact changed-file list;
* candidate VSIX version and SHA-256.

Capture before-state SHA-256 hashes for:

* all current pending A0 files;
* all four protected dirty files;
* candidate VSIX;
* protected control-plane paths;
* any observable real Consumer workspace roots.

If repository, branch, HEAD, workspace, or scope differs materially, stop with:

LOCAL_PHASE_A0R_BLOCKED_IDENTITY_MISMATCH

Authorized scope

Current eight-file A0 overlay:

1. TrustedPlanningEvidenceService.ts
2. EtlAgent.ts
3. AgentMessageRouter.ts
4. AgentActionExecutor.ts
5. ResponseComposer.ts
6. index.ts
7. trustedPlanningEvidenceService.test.ts
8. testPatterns.ts

One additional test-only file is explicitly authorized because seven observed failures reside there:

9. phase5AgentRouter.test.ts

No other file may change, except under the conditional SolutionMemoryStore.ts rule below.

Part A — adjudicate incoming is not iterable

First trace read-only:

* authoritative SolutionPlan and evidence types;
* canonical constructors/factories;
* SolutionMemoryStore.mergeEvidence;
* every production and test caller supplying the incoming value;
* the exact synthetic fixture reaching AgentActionExecutor.

Then choose exactly one evidence-backed classification.

Case 1 — invalid synthetic fixture

If the authoritative type and every legitimate runtime caller require an evidence array:

* repair only the test fixture/helper;
* construct the plan through its canonical factory where available;
* otherwise provide a structurally valid explicit empty evidence collection;
* do not alter production SolutionMemoryStore behavior.

The repaired test must reach and assert the trusted-evidence gate. It must not crash before the assertion.

Case 2 — legitimately optional runtime evidence

Only if authoritative types or reachable production callers prove that omitted evidence is valid, a minimal edit to SolutionMemoryStore.ts may be made.

Before editing it, report the exact type and caller evidence justifying this scope expansion.

If justified:

* normalize only legitimate absence to an empty collection;
* reject a present malformed/non-array value with a structured fail-closed result;
* do not use blanket incoming ?? [];
* do not catch and suppress the TypeError without validating the input;
* add executable cases for valid empty, valid populated, legitimately absent, and malformed evidence.

If neither case is proven, stop with:

LOCAL_PHASE_A0R_BLOCKED_SOLUTION_PLAN_CONTRACT

Part B — reconcile the seven router regressions

Inventory each failing test in phase5AgentRouter.test.ts.

For every test, report:

* test title;
* former expectation;
* original behavior it protected;
* why the expectation conflicts with the authorized A0 contract;
* replacement executable assertion.

Apply these rules:

* Never restore default RepoWriter workspace resolution.
* Never let incomplete evidence reach trusted preview.
* Preserve the original safety purpose of each test.
* Do not rewrite unrelated expectations.
* Do not fabricate workspace identity, STTM identity, job candidates, ownership, or collision evidence merely to make a complete fixture.
* Do not delete or blanket-skip any failure.

For incomplete evidence, assert:

* preview and validation receive zero calls;
* all writer APIs receive zero calls;
* applyEligible === false;
* exact unresolved-evidence codes are returned;
* the response is deterministic and fail-closed.

Where explicit selected-workspace evidence is legitimately present, assert its provenance and containment.

Candidate/job-discovery and collision ownership are deferred to A1. In A0 they must be represented explicitly as unresolved—not silently empty, absent, safe, or complete.

Rename stale test titles where necessary so they describe the new safety contract.

Part C — close A0 executable-coverage gaps

Add focused executable tests for:

1. Direct /create evidence propagation:
    * evidence is collected in AgentMessageRouter before AgentActionExecutor;
    * executor receives the same immutable evidence identity/content;
    * incomplete evidence blocks before preview;
    * unresolved codes reach ResponseComposer.
2. Zero side effects:
    * use executable spies/fakes for every reachable writer and preview writer boundary;
    * assert zero calls;
    * text search alone is insufficient.
3. Workspace/root behavior:
    * no process.cwd() fallback;
    * no default or ambient workspace inference;
    * ambiguous multi-root remains fail-closed;
    * explicit selected-root provenance is preserved;
    * a confirmed empty repository can express initialization intent without pretending candidate/collision discovery is complete.
4. Extension-source classification:
    * extension installation/source roots cannot become Consumer targets;
    * classification must use trusted path evidence, not repository names or sample strings.
5. Containment:
    * POSIX outside-root escape;
    * Windows drive escape;
    * UNC escape;
    * mixed separators;
    * symlink/junction escape where the host permits it;
    * stale or external STTM rejection.

A narrowly justified platform-specific conditional test is acceptable only where the host cannot create the relevant filesystem object. Do not silently skip an entire safety category.

6. Candidate/collision evidence:
    * absent adapters produce explicit unresolved observations;
    * absence must not mean “no candidates” or “no collision”;
    * applyEligible remains false.

Do not implement A1 job-discovery or collision-inventory adapters during A0R.

Part D — isolated executable verification

After the bounded repair, validate only in a fresh unique OS temporary directory.

1. Create a clean snapshot using git archive HEAD.
2. Overlay only the final authorized pending A0R files.
3. Do not copy:
    * dirty protected files;
    * real out/**;
    * node_modules;
    * caches;
    * VSIX files;
    * Consumer workspace content.
4. Confirm snapshot package.json is committed version 0.3.139.
5. The committed tree has no lockfile. Therefore:
    * dependency resolution is allowed only inside the temporary snapshot;
    * use the least-mutating no-audit/no-fund command supported by the repository;
    * record Node and npm versions;
    * record resolved top-level dependency versions;
    * record SHA-256 of the temporary generated lockfile;
    * label the result UNPINNED_TEMP_DEPENDENCY_RESOLUTION;
    * never copy the lockfile or generated artifacts into the real repository.
6. Run test TypeScript compilation.
7. Run at minimum:
    * TrustedPlanningEvidenceService tests;
    * phase5AgentRouter tests;
    * workspaceInputContainment tests;
    * focused AgentActionExecutor evidence-gate tests;
    * direct /create propagation tests;
    * zero-writer-call tests;
    * the repository-registered focused unit runner.
8. Run the broader directly affected unit suite if available without modifying tracked/generated real-repository content.
9. Every original failure must be resolved and no new failure introduced.
10. Delete only the exact temporary snapshot after validation.

Final immutability verification

Prove that:

* real git status --porcelain is byte-for-byte identical before and after;
* hashes of all protected dirty files are unchanged;
* candidate VSIX hash is unchanged;
* protected control-plane paths are unchanged;
* real Consumer roots are unchanged;
* no package, VSIX, installation, Git, PR, CI, workflow, external-system, or control-plane action occurred;
* only explicitly authorized pending A0R files changed relative to the pre-repair pending overlay.

Required final report

Provide:

1. Repository/workspace identity evidence.
2. Exact final changed-file list.
3. A table mapping all original eight failures to:
    * root cause;
    * repair;
    * executable assertion;
    * result.
4. SolutionMemoryStore decision with exact type/caller evidence.
5. Coverage matrix for every A0R requirement.
6. Exact test commands, exit codes, and passing/failing/pending counts.
7. Node/npm versions, dependency-resolution label, resolved dependency inventory, and temporary lock hash.
8. Before/after hashes and immutability evidence.
9. Explicit confirmation that A1 did not start.
10. Explicit confirmation that Keep/Undo remains untouched.
11. Explicit statement that candidate/installed VSIX remains PRE-A0 runtime and does not yet contain the pending source changes.

Pass only if:

* compilation passes;
* all focused A0 suites have zero failures;
* all eight original failures are resolved;
* required executable assertions pass;
* writer/preview-writer call counts are zero where evidence is incomplete;
* no safety contract was weakened;
* real-worktree immutability is proven.

End with exactly one token:

LOCAL_PHASE_A0R_ISOLATED_EXECUTABLE_TESTS_PASS
LOCAL_PHASE_A0R_ISOLATED_EXECUTABLE_TESTS_FAIL
LOCAL_PHASE_A0R_BLOCKED
