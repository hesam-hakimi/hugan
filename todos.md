LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_DISCOVERY — READ ONLY

The post-Repair-4 independent re-audit returned FAIL.

Do NOT implement anything yet.

Perform a narrowly bounded, exhaustive, read-only discovery to freeze the exact Repair-5 scope.

No file may be created, edited, deleted, formatted, staged, committed, packaged, installed, or otherwise mutated.

==================================================
1. CURRENT CONFIRMED STATE
==================================================

Repair 4 is considered successfully implemented and validated.

The independent re-audit confirmed the following previous blockers are closed:

- sample_repo is BLOCKED as a consumerRoot.
- UnitTestCoordinator direct write is eliminated.
- UnitTestCoordinator containment is enforced.
- preview identity persistence is opaque-only.
- shared RepoWriter/write infrastructure is reused.
- normal QA single-folder topology is safe for the repaired RepoWriter path.
- packaged framework contract is trusted.
- installed-extension resource resolution works.
- Oracle validation fails closed.
- WriteAuthorization rejects forgery/replay on routes that use it.
- package hygiene is clean.
- historical five failures remain unrelated.

Do NOT reopen or redesign these areas unless one of the newly discovered routes directly requires reuse of their existing APIs.

The independent re-audit ended with:

ALL_WRITE_ROUTES_GATED: NO
SAFE_TO_BUILD_QA_VSIX: NO
LOCAL_HOTFIX_HF1_V2_FINAL_REAUDIT_FAIL

==================================================
2. NEW HIGH FINDING A — ExplainCoordinator
==================================================

The audit identified a live reachable consumer-write route:

ExplainCoordinator.handleSaveExplain()

The audit observed that this route:

- writes generated explain output;
- derives a workspace root through an equivalent of workspaceFolders[0];
- does not use RepoWriter.resolveWorkspacePath();
- does not apply the HF1-V2 source/reference-root exclusion policy;
- does not use the trusted preview → approval → WriteAuthorization lifecycle.

Trace this route completely from the user/chat action to the filesystem mutation.

Determine:

A. Exact production files and functions involved.

B. Exact current root-selection logic.

C. Whether the output is a consumer workspace artifact.

D. Whether any existing confirmation/approval mechanism exists.

E. Whether that mechanism is equivalent to the trusted HF1-V2 write gate or is weaker.

F. The smallest way to reuse the existing:
   - canonical consumerRoot resolution;
   - path containment;
   - preview manifest;
   - TrustedWriteApprovalStore;
   - WriteAuthorization;
   - one-time consumption.

G. Whether a preview ID must persist across turns, and if so which existing state object should carry only the opaque identifier.

H. Exact current test files exercising:
   - save explain;
   - cancel;
   - overwrite;
   - workspace selection;
   - filesystem writes.

Do not propose direct first-folder selection as acceptable.

==================================================
3. NEW HIGH FINDING B — Artifact Reuse write chain
==================================================

The audit identified another live write chain:

ArtifactReuseConversationCoordinator
→ ArtifactActionCoordinator
→ NewArtifactWriter / ArtifactPatchApplier

The audit reported that:

- ETLChatParticipant passes a workspaceRoot derived from an equivalent of workspaceFolders[0];
- that root is threaded into ArtifactActionInput/session state;
- NewArtifactWriter and ArtifactPatchApplier perform real writes;
- PathValidator provides relative/traversal protection;
- but the root itself is not classified through RepoWriter's consumer-root exclusion rules;
- sample_repo or another reference/source root can therefore be selected by first-folder fallback;
- the conversational preview/apply flow is not independently proven equivalent to the HF1-V2 trusted WriteAuthorization gate.

Trace the complete runtime route.

Determine:

A. Exact production files and functions.

B. Exact point where workspaceRoot is first chosen.

C. Every place the root is persisted or propagated.

D. Every real filesystem write performed by:
   - NewArtifactWriter;
   - ArtifactPatchApplier;
   - any sibling writer in the same flow.

E. Existing preview/apply/confirmation semantics.

F. Whether the current preview identity is cryptographically/immutably bound to:
   - consumerRoot;
   - relative artifact path;
   - artifact bytes/hash;
   - target/operation;
   - one-time consumption.

G. Whether the flow can reuse the existing trusted HF1-V2 approval primitives instead of maintaining a parallel authorization mechanism.

H. Exact test files covering:
   - new artifact write;
   - patch/apply;
   - preview;
   - cancel/reject;
   - replay;
   - multi-root workspace;
   - path traversal;
   - root selection.

==================================================
4. EXHAUSTIVE WRITE-ROUTE SWEEP
==================================================

Before freezing Repair 5, perform a repo-wide read-only inventory of every production filesystem mutation capable of writing into a workspace.

Search for and trace equivalent usages of:

workspace.fs.writeFile
workspace.fs.createDirectory
fs.writeFile
fs.writeFileSync
fs.mkdir
fs.mkdirSync
rename/copy operations that create consumer files
writer/helper abstractions that ultimately call these functions

For each route return:

- entry point;
- final mutation function;
- what it writes;
- whether it writes consumer artifacts;
- how consumerRoot is selected;
- whether root exclusion is applied;
- whether containment is applied;
- whether trusted preview/approval/WriteAuthorization is applied;
- whether the route is reachable from normal user/QA behavior;
- verdict.

Classify each exactly as:

TRUSTED_CONSUMER_WRITE
INTERNAL_NON_CONSUMER_WRITE
TEST_ONLY
DEAD_OR_UNREACHABLE
REPAIR_5_REQUIRED
AMBIGUOUS

The goal is to avoid another later audit discovering yet another live consumer-write route.

Do NOT edit anything.

==================================================
5. REQUIRED TARGET ARCHITECTURE
==================================================

For every real consumer-workspace write, the desired contract remains:

resolve canonical consumerRoot
→ reject prohibited/reference/source roots
→ validate contained relative artifact path
→ immutable preview
→ explicit approval
→ trusted one-time authorization
→ immediate containment re-check
→ exactly one filesystem write

No production consumer-write route may depend on:

workspaceFolders[0]

or:

"the folder that is not extension/framework must be the consumer"

Normal QA topology remains:

exactly one legitimate consumer folder
→ consumerRoot

zero folders
→ BLOCKED

one prohibited/reference/source root
→ BLOCKED

multiple folders without explicit safe selection
→ ambiguous / BLOCKED

==================================================
6. SHARED INFRASTRUCTURE REUSE
==================================================

Determine the smallest way for both newly identified write flows to reuse existing HF1-V2 infrastructure.

Prefer reuse of existing:

RepoWriter
RepoWriter.resolveWorkspacePath / canonical root classification
PathValidator
TrustedWriteApprovalStore
requestWriteAuthorization / equivalent trusted approval API
WriteAuthorization
manifest/checksum primitives

Do not propose:

- another approval store;
- another root classifier;
- another WriteAuthorization implementation;
- direct workspace.fs.writeFile before authorization;
- auto-approval;
- feature-flag bypass;
- a test-only production escape.

If a different trusted API is required because these artifacts have a genuinely different manifest shape, identify the minimum adapter needed and why.

==================================================
7. REQUIRED BEHAVIORAL TEST PLAN
==================================================

For Explain save, identify exact tests proving:

1. first request → preview only, zero writes;
2. approved second request → exactly one write;
3. replay → zero additional writes;
4. cancel/reject → zero writes;
5. sole sample_repo/reference root → BLOCKED;
6. multi-root without explicit selection → BLOCKED;
7. no first-folder fallback;
8. absolute path rejected;
9. traversal rejected;
10. sibling-root escape rejected;
11. every actual write stays inside canonical consumerRoot.

For Artifact Reuse, identify exact tests proving:

12. preview produces zero writes;
13. approved new-artifact apply → exactly one contained write;
14. approved patch apply → exactly intended contained mutation;
15. replay cannot apply again;
16. cancel performs zero mutations;
17. sample_repo/reference root is blocked;
18. multi-root ambiguity is blocked;
19. first-folder fallback is impossible;
20. root drift after preview invalidates apply;
21. relative path drift invalidates apply;
22. content/patch drift invalidates apply;
23. write cannot escape consumerRoot.

Tests must exercise real production behavior, not primary source-text assertions.

==================================================
8. FRAMEWORK-BINDING LOW DEBT
==================================================

Do not modify framework-binding behavior in Repair 5 unless one of the two newly identified routes directly depends on it.

The previous audit accepted it as LOW/INFO follow-up debt because gated writes revalidate authority before write.

Return:

FRAMEWORK_BINDING_CHANGE_NEEDED_FOR_REPAIR_5: YES|NO

with evidence.

==================================================
9. FIVE HISTORICAL FAILURES
==================================================

Do not touch:

- the two EvalGating failures;
- the three Copilot workflow customization failures;
- Phase-H baselines;
- customization assets.

They remain unrelated historical failures.

==================================================
10. EXACT SCOPE DISCOVERY
==================================================

Return an exact production file inventory.

For every production file list:

- exact path;
- route/finding;
- exact function/class to change;
- exact reason the edit is necessary.

Return an exact test file inventory.

For every test file list:

- exact path;
- behavior(s) covered;
- whether existing test is modified or new test added inside the existing file.

Return any state/type file required to persist only opaque preview identity between turns.

No approximate filenames are allowed.

==================================================
11. SCOPE MINIMIZATION
==================================================

Do not automatically include ETLChatParticipant or shared infrastructure merely because they are upstream.

Include a file only if live call-path evidence proves it must change.

If both write routes can be repaired through one shared root/gate integration point, prefer the smaller common repair.

Do not redesign unrelated coordinators.

==================================================
12. REQUIRED RESPONSE
==================================================

Return:

A. Complete production write-route inventory.

B. The exact two newly blocking routes and their root causes.

C. Exact Repair-5 production file list.

D. Exact Repair-5 test file list.

E. Exact state/type files if required.

F. Whether any new file is required.

G. Whether both flows can reuse existing trusted infrastructure.

H. Whether any other live ungated consumer write exists after the exhaustive sweep.

I. Framework-binding change verdict.

J. Scope totals:

Production files to modify: <count>
Test files to modify: <count>
State/type files to modify: <count>
New files required: <count>

Do not implement.

Finish exactly:

ALL_LIVE_CONSUMER_WRITE_ROUTES_ENUMERATED: YES|NO
ADDITIONAL_UNGATED_WRITE_ROUTE_BEYOND_AUDIT_TWO: YES|NO
EXPLAIN_WRITE_REPAIR_REQUIRED: YES|NO
ARTIFACT_REUSE_WRITE_REPAIR_REQUIRED: YES|NO
FRAMEWORK_BINDING_CHANGE_NEEDED_FOR_REPAIR_5: YES|NO
REPAIR_5_SCOPE_FROZEN: YES|NO
LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_DISCOVERY_COMPLETE
