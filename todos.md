LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6_SCOPE_DISCOVERY — READ ONLY

The final independent post-Repair-5 audit completed with:

SAFE_TO_KEEP_REPAIR_5: YES
SAFE_TO_BUILD_QA_VSIX: NO
SAFE_TO_COMMIT_HF1_V2: NO
LOCAL_HOTFIX_HF1_V2_FINAL_POST_REPAIR5_REAUDIT_FAIL

Repair 5 itself has passed its independent gate and must be treated as accepted current candidate behavior.

Do NOT reopen, redesign, or undo Repair 5.

This task is a NEW release-gate discovery phase.

Do NOT implement anything.

Perform exhaustive, adversarial, strictly read-only investigation of the remaining release findings and freeze the exact smallest Repair-6 scope.

No file may be created, edited, deleted, formatted, staged, committed, packaged, installed, or otherwise mutated.

⸻

1. CURRENT ACCEPTED HF1 V2 STATE

The independent audit already confirmed the following as PASS:

* repository identity correct;
* candidate bytes stable during audit;
* all live consumer-write routes enumerated;
* normal QA single-folder model safe;
* QA requires no framework source;
* dangling-link handling in resolveContainedWorkspacePath() correct;
* POSIX case-sensitive containment logic inside that helper correct;
* Explain trusted write safe;
* Artifact Reuse trusted write safe;
* RepoContext trusted write safe;
* UnitTestCoordinator trusted write safe;
* WriteAuthorization runtime safe;
* packaged Oracle framework contract safe;
* Oracle validation safe;
* installed-extension resource loading safe;
* consumer artifact contract preserved;
* five historical failures unrelated;
* Repair 5 safe to Keep.

Do not re-litigate those conclusions unless live evidence shows a direct contradiction relevant to the findings below.

⸻

2. AUDIT FINDINGS TO INVESTIGATE

The final independent audit reported:

HIGH H1 — physical containment is not applied to the primary RepoWriter write route

Audit claim:

RepoWriter.writeArtifacts(...)

validates artifact paths lexically with PathValidator.validateArtifactPath(...), but does NOT invoke the already-hardened physical containment function:

resolveContainedWorkspacePath(...)

before the real filesystem write.

The audit reported that the primary routes using RepoWriter.writeArtifacts() include at least:

* EtlActionToolService
* WriteCoordinator
* DeployCoordinator

Potential consequence:

A symlink/junction inside an approved consumerRoot could redirect an otherwise approved relative path physically outside consumerRoot.

The trusted preview may still display only the apparently safe relative path.

Classification from audit:

HIGH

⸻

HIGH H2 — package hygiene is insufficient for a safe QA VSIX

The audit reported:

* .tmp/** is not excluded;
* .tmp currently contains a large unrelated tree, including cloned/private repository content;
* .tsbuildinfo.test is not matched by the current .vscodeignore rule;
* a clean QA VSIX build may therefore package unrelated/private/test content;
* manual ZIP surgery would otherwise be required.

Audit observed approximately:

.tmp:
~1895 files
~257 MB

Do NOT rely on those numbers as current truth; verify them read-only.

Classification from audit:

HIGH

⸻

3. MEDIUM FINDINGS TO CLASSIFY BEFORE ANY REPAIR

The independent audit also reported four MEDIUM findings.

Do NOT automatically include them in Repair 6.

For each, determine whether it is:

RELEASE_BLOCKING_SECURITY_DEFECT
RELEASE_BLOCKING_CORRECTNESS_DEFECT
BOUNDED_NON_BLOCKING_DEBT
FALSE_POSITIVE
DEAD_OR_UNREACHABLE
OUT_OF_SCOPE_LEGACY_BEHAVIOR
AMBIGUOUS

⸻

M1 — additional lexical-only containment paths

Audit reported that:

UnitTestCoordinator.isInsideRoot(...)
WorkflowTargetResolver.assertWithinWorkspace(...)

use lexical path.relative(...)-style containment without physical realpath containment.

Determine independently:

A. Are these functions reachable on real consumer filesystem mutation paths?

B. Does UnitTestCoordinator already perform an independent physical containment check elsewhere that makes this helper defense-in-depth only?

C. Does WorkflowTargetResolver guard an actual consumer write or only planning/read behavior?

D. Can either route physically escape consumerRoot through a symlink/junction?

E. Would fixing them require a shared primitive outside the currently accepted Repair-5 architecture?

Do not classify M1 as a blocker merely because the helper is lexical.

Prove reachability and exploitability.

⸻

M2 — .tsbuildinfo.test package exclusion

Audit reported that:

.tsbuildinfo.test

is not excluded by the current .vscodeignore.

Determine whether this is already fully subsumed by H2.

Prefer ONE package-hygiene repair rather than treating H2 and M2 as separate implementations if they share the same configuration fix.

⸻

M3 — manifest disposition mismatch

Audit claim:

EtlActionToolService.collectManifestFiles(...) may mark the job config as:

disposition: unchanged

while:

RepoWriter.writeArtifacts(...)

still rewrites artifacts.jobConfig.

Determine:

A. Is the same byte content rewritten?

B. Does Preview tell the user that this file is unchanged?

C. Is an actual filesystem write performed anyway?

D. Could this break timestamp-sensitive behavior, downstream automation, audit semantics, or user expectations?

E. Is this only a semantic/reporting inconsistency or a true unsafe write?

F. Is it pre-existing?

G. Does it affect the fresh-consumer QA use case?

Do not fix it unless it is materially release-blocking or the smallest safe repair is clearly bounded.

⸻

M4 — legacy Copilot workflow customization writes

Audit reported legacy paths involving equivalents of:

CopilotWorkflowInitializer
Repairer
Upgrader
Deleter
ConsumerRepoOverlayService

which may authorize consumer .github/** mutations using a plain:

{ approved: true }

plus a modal, rather than the HF1 V2 immutable manifest / checksum / one-time WriteAuthorization model.

Important historical boundary:

The repository already has three protected historical Copilot workflow customization failures.

Repair 5 intentionally did NOT redesign that historical customization family.

Determine:

A. Are these routes part of the normal QA/end-user ETL flow being released?

B. Are they reachable from the packaged extension?

C. Do they mutate the same consumer workspace?

D. Are they explicitly user-triggered maintainer/customization operations?

E. Could they bypass HF1 V2 consumer-write guarantees in normal QA use?

F. Would repairing them require touching the historical customization family / protected baseline?

G. Is this a separate future security-hardening project rather than a blocker for this QA VSIX?

Do NOT silently broaden Repair 6 into a rewrite of the Copilot workflow customization subsystem.

⸻

4. HIGH H1 — TRACE THE PRIMARY WRITE ROUTE COMPLETELY

Trace:

EtlActionToolService
WriteCoordinator
DeployCoordinator
→ RepoWriter.writeArtifacts(...)
→ final filesystem mutations

For every call site determine:

* canonical consumerRoot source;
* preview manifest identity;
* approval state;
* WriteAuthorization state;
* artifact relative path;
* current lexical validation;
* current physical validation;
* exact final write target construction.

Answer explicitly:

H1-A

Is resolveContainedWorkspacePath() already called earlier or later in the route for every artifact?

H1-B

If not, can a symlink/junction under:

job_conf/
env_conf/
conf/
sql/

or another generated artifact directory redirect the final write physically outside consumerRoot?

H1-C

Can this occur after Preview/Approval without changing:

* relative artifact path;
* artifact bytes;
* manifest checksum?

H1-D

What is the smallest correct integration point?

Prefer, if architecture supports it:

RepoWriter.writeArtifacts()

as the single physical-containment choke point immediately before every real file/directory mutation.

Do NOT duplicate physical containment into every caller if one central fix is sufficient.

H1-E

Enumerate every file-writing helper inside RepoWriter that would need to use the resolved physical target.

H1-F

Determine whether:

backupExisting(...)
ensureDirectoryStructure(...)

or other internal helpers can create/mutate paths before the proposed physical validation.

⸻

5. H1 REQUIRED TEST PLAN

Identify exact existing test file(s) for RepoWriter real filesystem writing.

Future Repair 6 must behaviorally prove at least:

1. normal approved in-root job write succeeds;
2. approved relative path redirected by symlink to outside existing file is rejected;
3. dangling symlink to outside missing file is rejected;
4. escaping linked ancestor is rejected;
5. sibling-root junction/reparse escape rejected where applicable;
6. physical escape created AFTER Preview but BEFORE Write is rejected;
7. no outside bytes are modified;
8. normal valid in-root symlink behavior remains as defined by current contract;
9. /write, WriteCoordinator, and local /deploy cannot bypass the central check;
10. approval is failed/consumed correctly when the physical destination becomes unsafe.

Tests must exercise real production write behavior.

Do not accept source-text-only assertions.

⸻

6. H2 — PACKAGE HYGIENE AUDIT

Inspect:

.vscodeignore
package.json
VSIX packaging scripts/configuration

and the current repository filesystem.

Determine exactly which candidate files/directories would be included by the VSIX packager.

Do NOT actually package a VSIX in this discovery.

Verify handling of at least:

.tmp/**
.tsbuildinfo.test
*.tsbuildinfo
*.tsbuildinfo.*
tsconfig.test.json
src/test/**
out/test/**
docs/eval/**
.vscode-test/**
*.log
*.vsix
node_modules/**

Also verify required runtime content remains included:

package.json
out/extension.js
out/sttm-runtime.js
resources/copilot/**
resources/framework/contracts/**
required media/runtime assets

⸻

7. H2 — .tmp INVESTIGATION

Inspect .tmp read-only.

Return:

* total files;
* total bytes;
* top-level entries;
* whether Git repositories/checkouts exist underneath;
* whether private/internal source content could be packaged;
* whether .tmp is intended runtime content;
* whether any production code expects .tmp to ship in VSIX.

If .tmp is purely local/test/temporary state, state whether excluding:

.tmp/**

is sufficient.

Do not delete .tmp.

⸻

8. H2 — .tsbuildinfo RULE

Determine why current .vscodeignore matches some .tsbuildinfo forms but not:

.tsbuildinfo.test

Identify the smallest robust pattern that excludes:

.tsbuildinfo
.tsbuildinfo.test
foo.tsbuildinfo
foo.tsbuildinfo.test
other equivalent build-info variants

without excluding legitimate runtime assets.

Do not edit yet.

⸻

9. PACKAGE CONTENT PROOF STRATEGY

Define how Repair 6 should later prove package safety WITHOUT manual ZIP surgery.

Preferred future validation:

1. clean build;
2. local VSIX package;
3. vsce ls and/or archive-content inspection;
4. assert required runtime files present;
5. assert forbidden patterns absent;
6. verify source repository bytes unchanged except authorized build outputs if expected.

For this discovery only, specify commands but do not execute packaging.

⸻

10. RE-AUDIT ALL CURRENT WRITE ROUTES FOR H1 CLASS

Because H1 revealed that authorization correctness and physical containment were separated, perform a narrow read-only sweep of every current TRUSTED_CONSUMER_WRITE route.

For each route answer:

Trusted authorization? YES/NO
Canonical logical root? YES/NO
Physical target containment immediately before mutation? YES/NO

Routes must include at least:

* RepoWriter / /write
* WriteCoordinator
* DeployCoordinator
* ExplainCoordinator
* UnitTestCoordinator
* Artifact Reuse create
* Artifact Reuse patch
* RepoContextInitializer
* legacy customization routes identified in M4

The goal is not to redesign everything.

The goal is to identify whether H1’s physical-containment omission exists anywhere else that is release-relevant.

⸻

11. DEAD/UNREACHABLE PUBLIC WRITE HELPERS

Audit reported LOW findings around:

RepoWriter.backupExisting(...)
RepoWriter.ensureDirectoryStructure(...)

being public but apparently unreachable from production.

Verify:

* production caller count;
* whether they are truly unreachable/dead;
* whether they can be invoked indirectly;
* whether they need Repair 6 modification if RepoWriter.writeArtifacts becomes the central safe choke point.

If dead/unreachable, keep them out of scope unless they undermine the safety proof.

⸻

12. ROOT NAME HEURISTIC LOW DEBT

Audit reported RepoWriter root exclusions still rely partly on folder names.

Do not automatically fix this.

Determine whether a renamed extension/framework checkout can realistically become a consumer root in normal QA use despite:

* single-folder topology;
* explicit user selection;
* packaged contract;
* existing source/reference-root classifiers.

Classify as:

RELEASE_BLOCKER
NON_BLOCKING_DEBT
FALSE_POSITIVE

Do not widen Repair 6 unless necessary.

⸻

13. OUTPUT REQUIRED — COMPLETE REPAIR-6 DECISION MATRIX

Return a table with rows:

H1 Primary RepoWriter physical containment
H2 .tmp package exclusion
M1 Other lexical-only containment
M2 .tsbuildinfo.test exclusion
M3 disposition unchanged but rewritten
M4 legacy customization authorization
L1 workspaceFolders[0] read-root heuristic
L3 folder-name root exclusions
L4 PathValidator lowercase behavior
L5 unreachable RepoWriter public helpers

Columns:

Severity from audit
Independent classification
Reachable?
Normal QA impact?
Security impact?
Release blocking?
Exact production file(s) required
Exact test/config file(s) required
Already candidate-modified?
Repair 6 required?

⸻

14. EXACT REPAIR-6 SCOPE

Return the smallest exact file list required to reach:

SAFE_TO_BUILD_QA_VSIX: YES

Separate:

PRODUCTION_FILES_TO_MODIFY
TEST_FILES_TO_MODIFY
PACKAGE_CONFIG_FILES_TO_MODIFY
NEW_FILES_REQUIRED

Do not include speculative files.

For every file explain the exact reason.

⸻

15. SCOPE MINIMIZATION

Strong preference:

* one central physical-containment integration;
* one package-ignore/config fix;
* targeted behavioral regressions;
* no unrelated routing redesign;
* no historical customization repair unless proven release-blocking.

Do not convert every LOW/MEDIUM audit note into Repair 6 work.

⸻

16. NO-TOUCH BOUNDARY

Do not modify or propose incidental cleanup to:

etl-framework-adb
real consumer repositories
S-A/S-B work
Phase-H baselines
resources/prompts/**
.github/**
AGENT.md / AGENTS.md
package-lock.json
historical customization assets

unless a finding is explicitly proven release-blocking and scope amendment is requested separately.

⸻

17. REQUIRED END MARKERS

Return:

CURRENT_HF1_V2_BYTES_PRESERVED: YES|NO
H1_PRIMARY_WRITE_PHYSICAL_CONTAINMENT_REPAIR_REQUIRED: YES|NO
H2_TMP_PACKAGE_EXCLUSION_REPAIR_REQUIRED: YES|NO
M1_ADDITIONAL_PHYSICAL_CONTAINMENT_REPAIR_REQUIRED: YES|NO
M2_TSBUILDINFO_PACKAGE_REPAIR_REQUIRED: YES|NO
M3_DISPOSITION_REPAIR_REQUIRED_FOR_QA: YES|NO
M4_LEGACY_CUSTOMIZATION_REPAIR_REQUIRED_FOR_QA: YES|NO
ADDITIONAL_RELEASE_BLOCKER_DISCOVERED: YES|NO
ALL_RELEASE_RELEVANT_WRITE_ROUTES_PHYSICALLY_AUDITED: YES|NO
REPAIR_6_SCOPE_FROZEN: YES|NO

Finish exactly:

LOCAL_HOTFIX_HF1_V2_RELEASE_GATE_REPAIR_6_SCOPE_DISCOVERY_COMPLETE

No implementation.

Do not Keep.
Do not commit.
Do not package.
Do not install a VSIX.
