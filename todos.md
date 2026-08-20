LOCAL_HOTFIX_HF1_V2_ARCHITECTURE_AMENDMENT_1 — SINGLE-FOLDER QA/USER PATH MODEL

This amendment is authoritative and must be incorporated into the currently executing LOCAL_HOTFIX_HF1_V2 implementation before continuing.

Do not restart the implementation and do not discard the already-created in-scope resolver/package changes.

The previous V2 requirements remain valid except where this amendment explicitly refines the runtime path model.

IMPORTANT PRODUCT CONSTRAINT

Normal QA testers and end users will have exactly ONE consumer workspace folder open.

They will NOT have:

- etl-framework-adb
- extension source
- framework source
- neighboring development repositories
- frameworkRepositoryPath configured

The normal production runtime must therefore be designed around a single consumer workspace root plus packaged Extension resources.

==================================================
1. THREE ROOT TYPES — NEVER MIX THEM
==================================================

Model these concepts separately:

A. consumerRoot

The only filesystem root under which generated consumer ETL artifacts may be read/written.

For normal QA/user operation:

workspaceFolders.length === 1
→ canonicalize that exact selected workspace folder
→ validate/classify it
→ consumerRoot

B. extensionResourceRoot

The installed Extension package root.

This owns:

resources/framework/contracts/oracle-delivery-controls.v1.json

and other packaged runtime resources.

It is NEVER a consumer write target.

C. maintainerFrameworkRoot

Optional maintainer/development source evidence only.

It may originate from:

- explicitly configured frameworkRepositoryPath; or
- explicitly opened etl-framework-adb in a maintainer multi-root workspace.

It must never be required in normal QA/user mode.

Do not use one root as a fallback for another.

==================================================
2. NORMAL QA/USER WORKSPACE MODEL
==================================================

The primary production path is:

exactly one workspace folder
→ canonicalize
→ validate as consumer root
→ consumerRoot

Normal QA/user logic must NOT:

- scan workspace folders looking for etl-framework-adb;
- scan sibling folders;
- scan parent directories;
- infer framework repositories;
- use process.cwd();
- use Extension source as a consumer root;
- select workspaceFolders[0] without first enforcing the single-folder contract;
- require a second workspace folder.

If:

workspaceFolders.length === 0

return a typed blocked/missing-workspace result.

If:

workspaceFolders.length > 1

normal user mode must fail closed as an ambiguous consumer selection unless there is already an explicit consumer-resource selection mechanism proven by the repository contract.

Do NOT silently choose the first folder.

Maintainer multi-root behavior is separate and must not alter this production rule.

==================================================
3. FRAMEWORK AUTHORITY IS NOT PART OF CONSUMER PATH RESOLUTION
==================================================

In normal QA/user mode:

consumerRoot
and
framework authority

must be resolved independently.

Expected normal topology:

workspace:
    consumerRoot only

installed extension:
    extensionResourceRoot
        → packaged trusted framework contract

Therefore:

consumerRoot resolution must succeed even when no etl-framework-adb exists anywhere in the workspace.

Oracle validation then uses:

packaged_contract

from extensionResourceRoot.

Do not make consumer classification dependent on framework source discovery.

==================================================
4. FRESH CONSUMER MODEL
==================================================

A single explicitly opened consumer folder may be a valid fresh target even when none of these exist:

job_conf/
env_conf/
workspace marker

Classification must be:

single canonical workspace folder
+ contained and valid consumer target
+ not Extension installation/source
+ not maintainer framework source
+ not prohibited/external root
+ no existing ETL job layout
=
CREATE_NEW_JOB

Do not create job_conf/, env_conf/, markers, or any other consumer file during classification, validation, or preview.

Only the approved write may create the previewed directories/files.

==================================================
5. ARTIFACT PATH MODEL
==================================================

The immutable manifest must store consumer artifact paths as canonical relative paths rooted at consumerRoot.

Example:

job_conf/imsbf/job-name.conf

Do not persist developer-machine absolute paths as artifact identity.

For every artifact:

relativePath
→ normalize
→ reject absolute paths
→ reject drive-qualified paths
→ reject traversal (`..`)
→ reject paths escaping consumerRoot
→ resolve against the exact canonical consumerRoot
→ verify containment

At write time:

the same manifest relative path
+ the same canonical consumerRoot

must reproduce the target.

Do not independently recompute an alternate artifact path.

==================================================
6. APPROVAL PATH BINDING
==================================================

Bind the approval to:

- canonical consumerRoot identity;
- targetDecision;
- selected artifact types;
- exact normalized relative artifact paths;
- exact content hashes;
- framework source kind;
- framework/contract identity;
- framework fingerprint.

Before writing, recompute only the containment-safe absolute target from:

consumerRoot + approved relativePath

and compare all bound claims.

Any consumerRoot change must invalidate approval.

Any artifact relative-path change must invalidate approval.

==================================================
7. NEVER WRITE OUTSIDE consumerRoot
==================================================

RepoWriter / final write boundary must prove for every artifact:

target is a descendant of consumerRoot

after canonicalization.

Explicitly deny:

- extensionResourceRoot;
- Extension installation/source;
- maintainerFrameworkRoot;
- etl-framework-adb;
- sibling workspace roots;
- parent directories;
- arbitrary absolute paths;
- external paths.

No write must be possible to the packaged contract or framework source.

==================================================
8. MAINTAINER MODE
==================================================

Maintainer/development mode may still use a multi-root workspace containing:

- consumer test workspace
- etl-framework-adb

but framework-source discovery must not determine consumerRoot.

If multi-root is used for maintainer verification, the consumer target must be explicitly identified through an existing safe selection mechanism.

Never infer:

“the folder that is not etl-framework-adb must be the consumer.”

Normal QA/user behavior remains single-folder-first.

==================================================
9. REQUIRED TESTS FOR THIS AMENDMENT
==================================================

Add behavioral tests proving:

1. exactly one consumer workspace folder → selected consumerRoot;
2. zero workspace folders → blocked;
3. multiple folders without explicit consumer selection → blocked/ambiguous;
4. the first-folder fallback is never used;
5. a fresh single-folder consumer with no job_conf/env_conf → CREATE_NEW_JOB;
6. no marker/directory/file created during classification;
7. normal QA works with zero etl-framework-adb folders;
8. packaged framework contract resolves independently from consumerRoot;
9. artifact manifest stores relative paths, not machine-specific absolute paths;
10. absolute artifact path input is rejected;
11. `..` traversal is rejected;
12. sibling-root escape is rejected;
13. canonical containment is rechecked before write;
14. consumerRoot change after preview invalidates approval;
15. relative artifact-path change after preview invalidates approval;
16. extensionResourceRoot can never be a write root;
17. maintainerFrameworkRoot can never be a write root;
18. consumer artifacts remain the same 12 paths/bytes/order.

Use actual production path APIs rather than source-text-only assertions for these critical behaviors.

==================================================
10. REVIEW CURRENT IMPLEMENTATION BEFORE CONTINUING
==================================================

Before continuing edits:

- inspect all already-created/edited V2 changes;
- identify whether any current code assumes framework source is another workspace folder;
- identify whether any current code couples framework discovery to consumerRoot selection;
- correct that design within the existing authorized edit universe before proceeding.

Do not undo valid packaged-contract or maintainer-override work.

If this amendment requires an existing file outside the already-authorized HF1-V2 edit universe, STOP before editing it and report:

LOCAL_HOTFIX_HF1_V2_SCOPE_AMENDMENT_REQUIRED

with exact path and reason.

==================================================
11. REQUIRED ACKNOWLEDGEMENT
==================================================

Before resuming implementation, report briefly:

NORMAL_QA_WORKSPACE_MODEL: SINGLE_CONSUMER_FOLDER
CONSUMER_ROOT_SOURCE: EXPLICIT_SINGLE_WORKSPACE_FOLDER
PACKAGED_CONTRACT_SOURCE: EXTENSION_RESOURCE_ROOT
FRAMEWORK_SOURCE_REQUIRED_FOR_QA: NO
FIRST_FOLDER_FALLBACK_ALLOWED: NO
MULTI_ROOT_IMPLICIT_CONSUMER_SELECTION_ALLOWED: NO
ARTIFACT_IDENTITY: CONSUMER_RELATIVE_PATH
WRITE_OUTSIDE_CONSUMER_ROOT_ALLOWED: NO

Then continue the existing LOCAL_HOTFIX_HF1_V2 implementation under this amended architecture.

Do not Keep.
Do not commit.
Do not package.
