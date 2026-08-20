LOCAL_HOTFIX_HF1_V2_REPAIR_4_SCOPE_DISCOVERY — READ ONLY

The final independent HF1 V2 audit returned FAIL.

Do NOT repair anything yet.

Perform a narrowly bounded read-only discovery to freeze the exact Repair-4 implementation and test surface.

No file may be created, edited, deleted, formatted, staged, committed, packaged, installed, or otherwise mutated.

Confirmed blocking findings

Finding A — CRITICAL

A workspace folder named/reference-classified as:

sample_repo

can currently resolve as UPDATE_EXISTING_REPO instead of BLOCKED.

The independent audit identified the likely production location as:

src/writers/RepoWriter.ts

and specifically recommended adding sample_repo to the protected/reference/source-root classification rather than weakening the single-folder consumer model.

Finding B — HIGH

A fourth production write route exists:

UnitTestCoordinator.handleWrite()

The audit found that this route:

* bypasses the trusted preview/approval/WriteAuthorization gate;
* is not bound to an immutable approved manifest;
* does not enforce consumerRoot containment using the same authoritative path contract;
* uses a narrower filename check instead;
* contains or reaches a workspaceFolders[0]-style write-root fallback.

Likely production file:

src/chat/UnitTestCoordinator.ts

The other three production write routes are already correctly gated and must not be redesigned.

Finding C — MEDIUM contract gap

The audit reported that the approval manifest binds:

* consumer root / destination identity;
* target;
* targetDecision;
* artifact types;
* paths;
* content hashes;

but does not explicitly bind:

* framework authority source kind;
* framework contract/framework identity;
* framework fingerprint.

Determine whether this finding is accurate in the live source and identify the exact smallest file set required to close it.

Do not assume a change is required until source evidence confirms the gap.

Required discovery

1. sample_repo

Locate:

* exact root-classification implementation;
* exact list/set of protected framework/reference/source root names;
* all direct consumers of that classification;
* existing tests covering extension/reference/framework roots;
* exact existing test file where a sample_repo BLOCKED assertion belongs.

Determine whether adding sample_repo is sufficient or whether a broader semantic classifier already exists and should be used instead.

Do not broaden the production design unnecessarily.

2. UnitTestCoordinator write path

Trace end to end:

UnitTestCoordinator.handleWrite()
→ workspace-root resolution
→ artifact/path construction
→ overwrite checks
→ filesystem write

Identify:

* every production function/file in this route;
* whether it can reuse the existing trusted preview/approval APIs without creating another authorization implementation;
* the exact existing function that should replace its current root-selection fallback;
* the exact existing containment/path validator that should be reused;
* every existing test file exercising UnitTestCoordinator writes;
* the exact tests required for:
    * preview only / zero write;
    * explicit approval;
    * exactly one write;
    * consumed approval rejection;
    * ambiguous multi-root rejection;
    * no workspaceFolders[0] fallback;
    * consumerRoot escape rejection.

Do not invent a second write-authorization mechanism.

3. Framework authority binding

Inspect the current definitions and flow for:

* preview manifest;
* TrustedWriteApprovalStore;
* WriteAuthorization;
* manifest checksum/canonicalization;
* framework source kind;
* framework identity;
* framework fingerprint.

Answer exactly:

A. Are source kind, identity, and fingerprint already indirectly or directly included in the immutable checksum?

B. Are they reverified immediately before the write?

C. Could the framework authority change while artifact bytes remain identical and the old approval still be accepted?

D. If repair is required, list the exact files and tests needed.

E. If the audit finding is not materially exploitable because equivalent values are already cryptographically bound elsewhere, show the exact evidence and recommend whether to leave it as documented LOW debt or repair it.

Test-quality requirements

For each blocking finding, identify behavioral tests that would have failed before the repair.

Do not propose source-text-only tests as the primary proof.

The Repair-4 test plan must prove:

1. sample_repo is BLOCKED as the sole open folder.
2. A legitimate fresh single-folder consumer still reaches CREATE_NEW_JOB.
3. UnitTestCoordinator first call produces preview and zero writes.
4. Approved second call performs exactly one write.
5. Approval replay fails.
6. Multi-root ambiguity fails closed.
7. No first-folder fallback.
8. Absolute/traversal/sibling-root escape is rejected.
9. UnitTestCoordinator cannot write outside consumerRoot.
10. Framework source-kind/fingerprint drift invalidates approval, if Finding C is confirmed as a real gap.

No-touch requirements

Do not modify anything during this discovery.

Do not inspect or change:

* historical Phase-H failures beyond confirming they are unrelated;
* etl-framework-adb except if absolutely necessary for read-only contract context;
* consumer repositories;
* original etl_framework_extension;
* S-A/S-B work;
* package/VSIX artifacts.

Required response

Return:

A. Exact production repair inventory

For each file:

* exact path;
* finding addressed;
* exact function/type affected;
* why modification is necessary.

B. Exact test repair inventory

List every exact test path required.

Do not use approximate names.

C. Framework-binding verdict

Exactly one:

FRAMEWORK_BINDING_REPAIR_REQUIRED

or:

FRAMEWORK_BINDING_REPAIR_NOT_REQUIRED

with evidence.

D. Scope totals

Return:

* production files to modify: <count>
* test files to modify: <count>
* new files required: <count>

No implementation is authorized.

Finish exactly:

REPAIR_4_SCOPE_FROZEN: YES|NO
LOCAL_HOTFIX_HF1_V2_REPAIR_4_SCOPE_DISCOVERY_COMPLETE
