LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_DISCOVERY — READ ONLY

The post-Repair-4 independent re-audit returned FAIL.

Do NOT implement anything yet.

Perform a narrowly bounded, exhaustive, read-only discovery to freeze the exact Repair-5 scope.

No file may be created, edited, deleted, formatted, staged, committed, packaged, installed, or otherwise mutated.

⸻

1. CURRENT CONFIRMED STATE

Repair 4 is considered successfully implemented and validated.

The independent re-audit confirmed the following previous blockers are closed:

* sample_repo is BLOCKED as a consumerRoot.
* UnitTestCoordinator direct write is eliminated.
* UnitTestCoordinator containment is enforced.
* preview identity persistence is opaque-only.
* shared RepoWriter/write infrastructure is reused.
* normal QA single-folder topology is safe for the repaired RepoWriter path.
* packaged framework contract is trusted.
* installed-extension resource resolution works.
* Oracle validation fails closed.
* WriteAuthorization rejects forgery/replay on routes that use it.
* package hygiene is clean.
* historical five failures remain unrelated.

Do NOT reopen or redesign these areas unless one of the newly discovered routes directly requires reuse of their existing APIs.

The independent re-audit ended with:

ALL_WRITE_ROUTES_ENUMERATED_AND_GATED: NO
SAFE_TO_BUILD_QA_VSIX: NO
SAFE_TO_COMMIT_HF1_V2: NO
LOCAL_HOTFIX_HF1_V2_FINAL_REAUDIT_FAIL

⸻

2. NEW HIGH FINDING A — ExplainCoordinator

The audit identified a live reachable consumer-write route:

ExplainCoordinator.handleSaveExplain()

The audit observed that this route:

* writes generated explain output;
* derives a workspace root through an equivalent of workspaceFolders[0];
* does not use RepoWriter.resolveWorkspacePath();
* does not apply the HF1-V2 source/reference-root exclusion policy;
* does not use the trusted Preview → Approval → WriteAuthorization lifecycle.

Trace this route completely from the user/chat action to the filesystem mutation.

Determine:

A. Exact production files and functions involved.

B. Exact current root-selection logic.

C. Whether the output is a consumer workspace artifact.

D. Whether any existing confirmation/approval mechanism exists.

E. Whether that mechanism is equivalent to the trusted HF1-V2 write gate or is weaker.

F. The smallest way to reuse the existing:

* canonical consumerRoot resolution;
* path containment;
* preview manifest;
* TrustedWriteApprovalStore;
* WriteAuthorization;
* one-time consumption.

G. Whether a preview ID must persist across turns, and if so which existing state object should carry only the opaque identifier.

H. Exact current test files exercising:

* save explain;
* cancel;
* overwrite;
* workspace selection;
* filesystem writes.

Do not propose direct first-folder selection as acceptable.

⸻

3. NEW FINDING B — Artifact Reuse write chain

The audit identified another live write chain:

ArtifactReuseConversationCoordinator
→ ArtifactActionCoordinator
→ NewArtifactWriter / ArtifactPatchApplier

The audit reported that:

* ETLChatParticipant passes a workspaceRoot derived from an equivalent of workspaceFolders[0];
* that root is threaded into ArtifactActionInput / session state;
* NewArtifactWriter and ArtifactPatchApplier perform real writes;
* PathValidator provides relative/traversal protection;
* but the root itself is not classified through RepoWriter’s consumer-root exclusion rules;
* sample_repo or another reference/source root can therefore be selected by first-folder fallback;
* the conversational preview/apply flow is not independently proven equivalent to the HF1-V2 trusted WriteAuthorization gate.

Trace the complete runtime route.

Determine:

A. Exact production files and functions.

B. Exact point where workspaceRoot is first chosen.

C. Every place the root is persisted or propagated.

D. Every real filesystem write performed by:

* NewArtifactWriter;
* ArtifactPatchApplier;
* any sibling writer in the same flow.

E. Existing preview/apply/confirmation semantics.

F. Whether the current preview identity is immutably bound to:

* consumerRoot;
* relative artifact path;
* artifact bytes/hash;
* target/operation;
* one-time consumption.

G. Whether the flow can reuse the existing trusted HF1-V2 approval primitives instead of maintaining a parallel authorization mechanism.

H. Exact test files covering:

* new artifact write;
* patch/apply;
* preview;
* cancel/reject;
* replay;
* multi-root workspace;
* path traversal;
* root selection.

⸻

4. EXHAUSTIVE WRITE-ROUTE SWEEP

Before freezing Repair 5, perform a repo-wide read-only inventory of every production filesystem mutation capable of writing into a workspace.

Search for and trace equivalent usages of:

workspace.fs.writeFile
workspace.fs.createDirectory
fs.writeFile
fs.writeFileSync
fs.mkdir
fs.mkdirSync
copy / rename operations that create or mutate consumer files
writer/helper abstractions that ultimately call these functions

Do not stop at the two routes already discovered.

For each route return:

* entry point;
* final mutation function;
* what it writes;
* whether it writes consumer artifacts;
* how consumerRoot is selected;
* whether root exclusion is applied;
* whether containment is applied;
* whether trusted Preview/Approval/WriteAuthorization is applied;
* whether the route is reachable from normal QA/user behavior;
* exact production files involved;
* verdict.

Classify each route exactly as one of:

TRUSTED_CONSUMER_WRITE
INTERNAL_NON_CONSUMER_WRITE
TEST_ONLY
DEAD_OR_UNREACHABLE
REPAIR_5_REQUIRED
AMBIGUOUS

The purpose of this sweep is to ensure the next independent audit does not discover yet another live consumer-write path.

Do not assume the previously known route count is complete.

⸻

5. REQUIRED TARGET ARCHITECTURE

For every real consumer-workspace write, the required contract remains:

resolve canonical consumerRoot
→ reject prohibited/reference/source roots
→ validate contained relative artifact path
→ immutable preview
→ explicit approval
→ trusted one-time authorization
→ immediate containment re-check
→ exactly one filesystem mutation

No production consumer-write route may depend on:

workspaceFolders[0]

or on an inference equivalent to:

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

⸻

6. SHARED INFRASTRUCTURE REUSE

Determine the smallest way for all Repair-5-required write flows to reuse existing HF1-V2 infrastructure.

Prefer reuse of existing:

RepoWriter
RepoWriter.resolveWorkspacePath / canonical root classification
PathValidator
TrustedWriteApprovalStore
requestWriteAuthorization / equivalent trusted approval API
WriteAuthorization
manifest/checksum primitives

Do not propose:

* another approval store;
* another root classifier;
* another WriteAuthorization implementation;
* direct workspace.fs.writeFile before trusted authorization;
* automatic approval;
* feature-flag bypass;
* test-only production escape.

If a route has a genuinely different artifact/operation shape, identify the smallest adapter required to map it into the existing trusted write contract.

⸻

7. EXPLAIN SAVE — REQUIRED TEST PLAN

Identify the exact existing test file(s) where behavioral coverage belongs.

The future Repair 5 must prove:

1. first save request → preview only, zero writes;
2. approved second request → exactly one write;
3. consumed/replayed approval → zero additional writes;
4. cancel/reject → zero writes;
5. sole sample_repo/reference root → BLOCKED;
6. sole framework/source/install root → BLOCKED;
7. multi-root without explicit selection → BLOCKED;
8. no first-folder fallback;
9. absolute path rejected;
10. traversal rejected;
11. sibling-root escape rejected;
12. every actual write is contained within canonical consumerRoot.

Tests must exercise real production behavior.

Do not use source-text assertions as primary evidence.

⸻

8. ARTIFACT REUSE — REQUIRED TEST PLAN

Identify the exact existing test file(s) where behavioral coverage belongs.

The future Repair 5 must prove:

13. preview produces zero writes;
14. approved new-artifact apply → exactly one contained write;
15. approved patch apply → exactly the intended contained mutation;
16. replay cannot apply again;
17. cancel performs zero mutations;
18. sole sample_repo/reference root → BLOCKED;
19. framework/source/install root → BLOCKED;
20. multi-root ambiguity → BLOCKED;
21. first-folder fallback is impossible;
22. consumerRoot drift after preview invalidates apply;
23. relative path drift invalidates apply;
24. content/patch drift invalidates apply;
25. absolute/traversal/sibling escape is rejected;
26. no mutation can occur outside canonical consumerRoot.

Tests must exercise the real production coordinator/writer path.

⸻

9. OTHER WRITE ROUTES FOUND BY THE SWEEP

For every additional route classified:

REPAIR_5_REQUIRED

provide:

* exact production path;
* exact root cause;
* whether it can reuse the same trusted infrastructure;
* exact behavioral test file;
* exact test scenarios required.

Do not silently exclude a route merely because it is pre-existing.

If it is a reachable consumer-workspace write, it is relevant to the final QA safety gate.

⸻

10. ROOT-SELECTION CONSISTENCY

For every consumer-write route, determine whether the root ultimately comes from the same canonical resolver semantics used by HF1 V2.

Report any occurrence of:

workspaceFolders[0]
workspaceFolders?.[0]
active editor inferred root
process.cwd() as consumer root
parent/sibling repo guessing
hard-coded sample/reference repo selection

For each occurrence classify whether it is:

* harmless/internal;
* unreachable;
* test-only;
* or a Repair-5 blocker.

⸻

11. APPROVAL MODEL CONSISTENCY

For each consumer-write route determine:

* preview object/state used;
* approval mechanism used;
* whether approval is explicit;
* whether it binds root/path/content;
* whether it is one-time;
* whether replay is rejected;
* whether drift invalidates apply;
* whether actual write occurs only after approval.

Identify parallel weaker approval mechanisms that should be replaced by or adapted to the shared trusted write contract.

⸻

12. STATE / PREVIEW IDENTITY

For each multi-turn route determine whether an opaque preview/approval identifier must persist between turns.

If required, identify:

* exact existing state/type;
* exact field to add;
* whether it is optional;
* why old persisted state remains compatible.

Never propose storing:

WriteAuthorization
privileged capability objects
mutable writer instances
raw approval-store records

Persist only opaque identity/state needed to resume the trusted lifecycle.

⸻

13. FRAMEWORK-BINDING LOW DEBT

Do not modify framework-binding behavior in Repair 5 unless one of the newly identified routes directly depends on it.

The previous audit accepted the existing framework-binding limitation as LOW/INFO because the gated write path revalidates authority before write.

Return exactly:

FRAMEWORK_BINDING_CHANGE_NEEDED_FOR_REPAIR_5: YES|NO

with live-source evidence.

⸻

14. CONSUMER ARTIFACT CONTRACT

Determine whether Explain output and Artifact Reuse outputs are:

A. members of the existing governed consumer artifact manifest;

B. separately generated but still consumer-workspace artifacts;

or

C. genuinely internal/non-consumer files.

For each, explain whether integrating the trusted write gate would alter:

* artifact paths;
* bytes;
* ordering;
* existing user-visible behavior.

Do not silently add anything to the existing 12-artifact contract unless the existing architecture already treats it as part of that set.

⸻

15. FIVE HISTORICAL FAILURES

Do not touch:

* two EvalGating failures;
* three Copilot workflow customization failures;
* Phase-H baseline;
* customization assets.

They remain unrelated historical failures.

⸻

16. NO-TOUCH REQUIREMENTS

This is read-only discovery.

Do not modify:

original etl_framework_extension repository
etl-framework-adb
consumer repositories
S-A / S-B files
Phase-H baseline reports
resources/prompts/**
.github/**
AGENT.md / AGENTS.md
package-lock.json

Do not:

* install dependencies;
* download anything;
* package a VSIX;
* run Git mutation;
* stage;
* commit;
* push;
* regenerate baselines.

⸻

17. EXACT REPAIR-5 PRODUCTION INVENTORY

Return the exact minimal production file list required for Repair 5.

For every file provide:

Exact path
Route/finding
Exact class/function/type affected
Why modification is required
Whether it is root-selection, approval, state, containment, or write integration

Do not use approximate paths.

⸻

18. EXACT REPAIR-5 TEST INVENTORY

Return the exact minimal test file list required.

For every test file provide:

Exact path
Route covered
Existing test to modify vs new test inside existing file
Exact behavioral assertions to add

Do not create a new test file if an appropriate existing suite already exists.

⸻

19. NEW FILES

Determine whether Repair 5 requires any new production or test file.

Strong preference:

NEW FILES REQUIRED: 0

If a new file is genuinely required, explain exactly why no existing trusted abstraction can host the change.

⸻

20. SCOPE MINIMIZATION

Do not include a file simply because it is upstream/downstream.

Include it only if live call-path evidence proves it must change.

If both newly discovered routes can be corrected through one shared integration point, prefer that smaller common repair.

Do not redesign unrelated coordinators.

⸻

21. REQUIRED FINAL RESPONSE

Return the following sections.

A. Complete production write-route inventory

A table containing every discovered production mutation route and its classification.

B. ExplainCoordinator root cause

Exact live path and required repair.

C. Artifact Reuse root cause

Exact live path and required repair.

D. Any additional Repair-5-required route

Exact path and reason.

E. Exact production repair inventory

No approximate paths.

F. Exact test repair inventory

No approximate paths.

G. State/type changes

Exact paths and fields, if required.

H. Existing trusted infrastructure reuse plan

Show exactly what will be reused.

I. Framework-binding verdict

Exactly:

FRAMEWORK_BINDING_CHANGE_NEEDED_FOR_REPAIR_5: YES|NO

J. Scope totals

Return exactly:

PRODUCTION_FILES_TO_MODIFY: <count>
TEST_FILES_TO_MODIFY: <count>
STATE_TYPE_FILES_TO_MODIFY: <count>
NEW_FILES_REQUIRED: <count>

No implementation is authorized in this task.

Finish with exactly:

ALL_LIVE_CONSUMER_WRITE_ROUTES_ENUMERATED: YES|NO
ADDITIONAL_UNGATED_WRITE_ROUTE_BEYOND_AUDIT_TWO: YES|NO
EXPLAIN_WRITE_REPAIR_REQUIRED: YES|NO
ARTIFACT_REUSE_WRITE_REPAIR_REQUIRED: YES|NO
FRAMEWORK_BINDING_CHANGE_NEEDED_FOR_REPAIR_5: YES|NO
REPAIR_5_SCOPE_FROZEN: YES|NO
LOCAL_HOTFIX_HF1_V2_REPAIR_5_SCOPE_DISCOVERY_COMPLETE

Do not implement.
Do not Keep.
Do not commit.
Do not push.
Do not package.
