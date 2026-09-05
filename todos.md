
# ETL\-0904\-SNAPSHOT02 — Supplemental Evidence Snapshot Prompt

```text
TASK_ID: ETL-0904-SNAPSHOT02
TYPE: SUPPLEMENTAL EVIDENCE SNAPSHOT — TWO IDENTIFIED HISTORY FOLDERS ONLY

Run this in a fresh, normal local VS Code Agent chat on Windows. Do not
use the Agent that implemented or self-reviewed IMPL04, and do not use
the ETL Orchestrator.

Echo TASK_ID: ETL-0904-SNAPSHOT02 as the first line of your report.

=========================================================
THIS IS A SUPPLEMENT, NOT A REPEAT
=========================================================

ETL-0904-SNAPSHOT01 captured the six dirty repository paths and their
matched Local History. Do not modify, extend, copy, or re-verify its
payload. This task performs only a read-only identity check of
SNAPSHOT01's manifest, then captures two identified Local History
folders that SNAPSHOT01 did not capture.

The eleven unattributed Local History folders remain outside the payload
by owner decision. This task records their current inventory only and
does not claim that any orphan belongs to a repository file.

=========================================================
SNAPSHOT01 IDENTITY — MANIFEST CHECK ONLY
=========================================================

Expected values:

  Snapshot root:
    C:\Users\tag5916\ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-20260904T210831Z

  Manifest SHA-256:
    78324A99A5D700053214B15F680E2DCBE3A2099A0801C43B6D02E512D43004DF

Before any write:

1. Confirm the exact snapshot root and manifest.json exist.
2. Compute manifest.json's SHA-256 and compare it with the expected
   digest above. Hexadecimal case is not significant; every byte is.
3. Parse manifest.json as JSON.
4. Inspect the actual JSON schema and locate the unique semantic values
   for:
     - task identity, which must equal ETL-0904-SNAPSHOT01;
     - snapshot completion, which must equal COMPLETE;
     - source-history unchanged, which must be true or YES.
5. Report the exact JSON path, value, and value type used for each check.
   Do not assume invented property names such as TASK_ID or
   SOURCE_HISTORY_STATE_UNCHANGED if the manifest uses a different or
   nested schema. If conflicting values exist, identity is not proven.
6. Record the exact Local History folder identifiers SNAPSHOT01 reports
   as captured.
7. Record the orphan-folder identifiers stored in SNAPSHOT01, if the
   manifest contains them. Do not inspect SNAPSHOT01's payload.

If the root or manifest is absent, the digest differs, JSON parsing
fails, any semantic value is missing or conflicting, or a required
semantic value is not the expected value, stop and report:

  BLOCKED_SNAPSHOT01_IDENTITY_MISMATCH: <specific reason>

=========================================================
TARGET FOLDER IDENTIFICATION
=========================================================

The only payload sources authorised by this task are:

  Folder A:
    History folder identifier: -3a438db7
    Expected canonical resource path:
      C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147\test.txt

  Folder B:
    History folder identifier: -545fead2
    Expected canonical resource path:
      C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147\.github\agents\test.agent.md

For each folder, before any write:

1. Locate the exact identifier beneath %APPDATA%\Code\User\History.
2. Confirm it is a real directory and not a symlink, junction, or other
   reparse point.
3. Read entries.json. Its absence is not recoverable for either target.
4. Decode the resource URI, normalise separators, and canonicalise the
   resulting Windows path.
5. Compare the complete canonical path with the expected path above
   using Windows case-insensitive path semantics. A basename, suffix,
   prefix, or textual-substring match is insufficient.
6. Confirm the identifier is absent from SNAPSHOT01's captured-folder
   list.

If the folder or entries.json is absent, the folder is a reparse point,
the decoded resource differs, identity is ambiguous, or the identifier
was already captured by SNAPSHOT01, stop and report:

  BLOCKED_TARGET_HISTORY_IDENTITY_LOST: <folder identifier>: <reason>

=========================================================
AUTHORISATION AND ITS EXACT LIMITS
=========================================================

The owner authorises exactly:

- read-only verification of SNAPSHOT01's manifest identity;
- read-only identification and inventory of the two target folders;
- read-only inventory of the orphan identifiers recorded by SNAPSHOT01;
- read-only Git identity and state checks from the active worktree;
- creation of one new destination root that is a sibling of SNAPSHOT01;
- creation of necessary child directories beneath that destination;
- byte-for-byte copying of the two target folders' regular files; and
- creation of one manifest.json as the final destination file.

Everything else is forbidden:

- Do not modify, move, rename, delete, extend, or add anything beneath
  SNAPSHOT01's root.
- Do not modify, move, rename, or delete anything in either Git worktree
  or anywhere beneath %APPDATA%\Code\User\History.
- Do not accept, discard, Keep, Undo, or otherwise resolve any pending
  VS Code chat edit. Leave every pending edit exactly as it is.
- No type-check, compile, lint, emit, test, parser execution, runner,
  Extension Host, package, install, activation, or consumer write.
- No Git command that mutates an index, worktree, ref, stash, branch,
  tag, or history. Use git --no-optional-locks for every Git read.
- Do not enter or modify the linked primary worktree. Its recorded
  identity may be read from the active linked worktree.
- Do not create helper scripts, temporary files, transcripts, archives,
  intermediate reports, or scratch output anywhere, including beneath
  the destination.
- Do not compress, encrypt, normalise, re-encode, or otherwise transform
  payload files. Copy bytes unchanged.
- Every destination file write must use fail-if-exists / CreateNew
  semantics. Use [System.IO.File]::Copy(source, destination, $false) for
  payload files and FileMode.CreateNew for manifest.json.

If any destination file already exists or any operation would overwrite
a file, stop immediately and report:

  BLOCKED_DESTINATION_CONFLICT

=========================================================
MANDATORY EXECUTION ORDER
=========================================================

The first authorised write is step 6. No write may occur before step 6.
Perform the task in exactly this order:

1. Verify SNAPSHOT01 manifest identity — Section 1, read-only.
2. Identify both target folders — Section 2, read-only.
3. Record the orphan inventory — Section 3, read-only.
4. Capture the complete pre-write baseline in memory — Section 4,
   read-only.
5. Select and validate the destination and print it — Section 5,
   read-only.
6. Create the destination and copy payload files — Section 6, writes.
7. Verify every destination payload file against Section 4 — Section 7,
   read-only.
8. Re-derive source and control state and compare with Section 4 —
   Section 8, read-only.
9. Only if Section 7 passes completely and every blocking Section 8
   verdict is YES, write manifest.json as the final destination file —
   Section 9.
10. Read back, parse, validate, size, and hash manifest.json — read-only.

If a blocker occurs before step 6, create nothing and report:

  SNAPSHOT_STATUS: BLOCKED

If any failure occurs after step 6, leave the partial destination exactly
as it is. Do not delete, rename, repair, resume, or reuse it. Do not write
manifest.json unless Sections 7 and 8 passed. Report:

  SNAPSHOT_STATUS: INCOMPLETE

and identify the last completed step.

=========================================================
SECTION 1 — VERIFY SNAPSHOT01 MANIFEST IDENTITY
=========================================================

Perform only the manifest checks defined above. Retain in memory:

- canonical SNAPSHOT01 root;
- manifest SHA-256 and byte size;
- the three semantic values and their actual JSON paths/types;
- captured Local History folder identifiers; and
- recorded orphan identifiers, if present.

Do not enumerate, hash, or compare SNAPSHOT01 payload files.

=========================================================
SECTION 2 — IDENTIFY THE TWO TARGET FOLDERS
=========================================================

Perform every check under TARGET FOLDER IDENTIFICATION. For each target,
retain the folder identifier, canonical folder path, decoded resource URI,
canonical resource path, and proof that SNAPSHOT01 did not capture it.

=========================================================
SECTION 3 — ORPHAN INVENTORY, NO COPY
=========================================================

Use SNAPSHOT01's manifest as the authoritative prior orphan list. Do not
infer attribution from extensions, contents, timestamps, or similarity.

For every identifier in that prior list, report one of:

- PRESENT: current folder name, regular-file count, total bytes, earliest
  file mtime UTC, and latest file mtime UTC; or
- CURRENTLY_ABSENT.

If SNAPSHOT01's manifest contains no machine-readable orphan list, report:

  ORPHAN_INVENTORY_STATUS: NOT_AVAILABLE_IN_SNAPSHOT01_MANIFEST

and continue. Do not scan all unrelated Local History folders to invent a
replacement prior list.

If the prior list exists but its size is not eleven, preserve the actual
manifest value, report the discrepancy, and continue. A changed or absent
orphan is not a blocker because orphan bytes are not payload in this task.

Record the observation time in UTC. Do not copy or hash orphan contents.

=========================================================
SECTION 4 — PRE-WRITE BASELINE, MEMORY ONLY
=========================================================

Before selecting or creating the destination, capture in memory:

For each target Local History folder:

- canonical folder path and identifier;
- decoded resource URI and canonical resource path;
- complete ordinal inventory of every item;
- for every regular file: filename, SHA-256, byte size, and mtime UTC;
- entries.json SHA-256 and byte size specifically;
- total entries.json entry count; and
- earliest and latest entry timestamps and entry IDs.

Fail before writing if either target contains a child directory, symlink,
junction, reparse point, or non-regular item. Report:

  BLOCKED_UNEXPECTED_HISTORY_ENTRY_TYPE: <path>

For control-state evidence, derive from the active linked worktree without
entering the primary worktree:

- git-dir, git-common-dir, and show-toplevel;
- branch and active HEAD;
- complete `git --no-optional-locks worktree list --porcelain` output and
  the primary worktree HEAD recorded there;
- raw `git --no-optional-locks status --porcelain=v1
  --untracked-files=all`; and
- staged-path inventory.

Also retain the current SNAPSHOT01 manifest SHA-256. Keep every Section 4
value in memory. Do not create any file or directory.

=========================================================
SECTION 5 — DESTINATION SELECTION AND SAFETY
=========================================================

The new destination must be a sibling of SNAPSHOT01, never a child or
parent of it:

1. Resolve SNAPSHOT01's canonical parent directory and verify it is not a
   reparse point.
2. Use that exact canonical parent as the destination parent.
3. Name the new root with the actual current UTC time in Windows-safe
   format:

     ETL-SNAPSHOT-ETL-0904-SNAPSHOT02-<YYYYMMDDTHHMMSSZ>

   Example format only: 20260905T120000Z
4. Canonicalise the planned path from its existing parent. Reject path
   traversal or reparse-point redirection.
5. Prove that the planned root is disjoint from and neither contains nor
   is contained by:
     - SNAPSHOT01;
     - both worktrees and their parent repository tree;
     - %APPDATA%\Code\User\History;
     - VS Code profile roots;
     - installed-extension roots;
     - QA roots; and
     - consumer-workspace roots.
6. Confirm the destination does not exist.
7. Print the exact planned absolute path in chat before the first write.

If disjointness cannot be proved, report:

  BLOCKED_DESTINATION_SAFETY_UNKNOWN

If the planned destination exists, report:

  BLOCKED_DESTINATION_EXISTS

=========================================================
SECTION 6 — CREATE DESTINATION AND COPY TARGET PAYLOAD
=========================================================

Create the destination root and the necessary child directories. Beneath:

  payload/local-history/

create one collision-proof directory per target whose name includes the
exact original folder identifier.

Copy entries.json and every other regular file from each target folder.
Use fail-if-exists semantics for every destination file. Do not copy any
orphan folder or SNAPSHOT01 payload file.

Record:

- total payload file count;
- total payload bytes; and
- history snapshot count, defined as copied regular payload files other
  than the two entries.json files.

=========================================================
SECTION 7 — VERIFY DESTINATION PAYLOAD
=========================================================

Before manifest creation:

1. Enumerate every destination payload file.
2. Prove its relative-path inventory exactly equals the Section 4 planned
   inventory.
3. Recompute SHA-256 and byte size for every destination payload file.
4. Compare each value with its corresponding Section 4 value, not with a
   newly sampled source value.
5. Report planned, present, compared, byte-identical, missing, extra, and
   mismatching counts, plus every exceptional path.

Any missing, extra, or mismatching payload makes the snapshot incomplete.
Do not write manifest.json.

=========================================================
SECTION 8 — PROVE SOURCES AND CONTROL STATE UNCHANGED
=========================================================

Immediately before manifest creation, re-derive and compare with Section 4:

For each target Local History folder:

- complete ordinal item inventory;
- SHA-256 and byte size of every regular file;
- entries.json SHA-256 and byte size;
- total entry count; and
- earliest/latest entry timestamps and entry IDs.

For repository control state:

- active branch and HEAD;
- the active and primary worktree HEADs from `git --no-optional-locks
  worktree list --porcelain`;
- raw porcelain status; and
- staged-path inventory.

For SNAPSHOT01:

- recompute manifest.json SHA-256 only; do not inspect its payload.

Produce these blocking verdicts:

  FOLDER_A_STATE_UNCHANGED: YES / NO
  FOLDER_B_STATE_UNCHANGED: YES / NO
  ACTIVE_AND_PRIMARY_HEADS_UNCHANGED: YES / NO
  WORKTREE_STATUS_UNCHANGED: YES / NO
  SNAPSHOT01_MANIFEST_UNCHANGED: YES / NO

Report mtime-only changes separately as observations and do not infer their
cause. Hash and inventory comparisons must not rely on mtime.

Re-observe the Section 3 orphan identifiers and record any inventory delta
as a non-blocking observation. Do not copy them. Orphan changes do not alter
the five blocking verdicts above.

If any blocking verdict is NO, name every delta, do not attribute cause
without evidence, do not write manifest.json, and report
SNAPSHOT_STATUS: INCOMPLETE.

=========================================================
SECTION 9 — WRITE AND VALIDATE MANIFEST
=========================================================

Only after Section 7 passes completely and all five Section 8 verdicts are
YES, construct one JSON object in memory and write it to manifest.json with
UTF-8 and FileMode.CreateNew. It must be the final destination write. Do
not write a temporary manifest and do not rename or replace a file.

The manifest must contain at least:

- manifestSchemaVersion;
- task ID and snapshotStatus equal to COMPLETE;
- UTC generation time and absolute destination path;
- SNAPSHOT01 root, verified manifest digest and byte size, plus the actual
  JSON paths/types/values used for its three semantic checks;
- initial and final SNAPSHOT01 manifest digests;
- initial and final repository control-state records and verdicts;
- each target's identifier, canonical folder path, resource URI and
  canonical resource path;
- each target's full Section 4 source inventory and Section 8 comparison;
- every copied payload file's source path, destination relative path,
  SHA-256, byte size, and source mtime UTC;
- Section 3 prior/current orphan inventory, observation timestamps, status,
  and any non-blocking deltas;
- Section 7 counts and exceptional-path arrays;
- all five Section 8 verdicts and delta arrays;
- total payload file count and bytes;
- history snapshot count, excluding entries.json; and
- an explicit declaration that manifest.json is excluded from payload
  verification counts.

Do not place manifest.json's own SHA-256 inside itself.

After the CreateNew write completes, perform read-only operations only:

1. read manifest.json back from disk;
2. parse it as JSON;
3. verify its required fields and snapshotStatus;
4. compute its byte size; and
5. compute its SHA-256 for the report.

If read-back or validation fails, do not edit or delete the manifest or
destination. Report SNAPSHOT_STATUS: INCOMPLETE and
MANIFEST_JSON_VALID: NO.

=========================================================
EPISTEMIC RULES
=========================================================

1. Missing entries.json for either target is a blocker, not a recoverable
   absence.
2. Do not use an orphan as a baseline or attribute it to a file.
3. A changed orphan inventory is reportable but is not a payload failure.
4. A byte-identical copy preserves evidence. It does not establish that
   source code is correct, independently reviewed, compiled, tested, or
   qualified.
5. An mtime is an observation, not proof of the operation that produced it.
6. A command log can prove what this task executed; it cannot exclude an
   unrelated concurrent external action. Attribute cause only when evidence
   supports it.
7. This snapshot does not approve the 11-path protected policy, B1, A2, or
   any implementation, oracle, review, qualification, version, merge, or
   release decision.

=========================================================
REPORT
=========================================================

1. Begin with the required TASK_ID line.
2. Report Sections 1 through 9 in execution order.
3. Include the SNAPSHOT01 semantic JSON paths/types/values actually used.
4. Include target-folder identity evidence and exact canonical resources.
5. Include destination safety results and the printed pre-write path.
6. Include exact payload counts and bytes, excluding manifest.json.
7. Include manifest read-back validation, SHA-256, and byte size.
8. List every command executed in exact order. For every write, identify
   the new destination path. Confirm each direct write was confined beneath
   the destination and used fail-if-exists semantics.
9. Report platform-generated cache artifacts separately from direct Agent
   file-write commands; do not silently equate the two.
10. Confirm no Git mutation command was executed. Report observed control
    state using the Section 8 comparisons rather than claiming more than
    the evidence proves.
11. Report anything material not requested, but change and propose nothing.
12. Replace every angle-bracket placeholder below with one permitted
    concrete value. Do not print the alternatives literally.
13. Close with exactly these lines and then stop:

TASK_ID: ETL-0904-SNAPSHOT02
SNAPSHOT_STATUS: <COMPLETE | INCOMPLETE | BLOCKED>
DESTINATION: <absolute path | NOT_CREATED>
SNAPSHOT01_IDENTITY_VERIFIED: <YES | NO>
SNAPSHOT01_MANIFEST_UNCHANGED: <YES | NO | NOT_COMPLETED>
FOLDER_A_CAPTURED: <YES | PARTIAL | NOT_ATTEMPTED>
FOLDER_B_CAPTURED: <YES | PARTIAL | NOT_ATTEMPTED>
ORPHAN_INVENTORY_STATUS: <COMPLETE | PARTIAL | NOT_AVAILABLE_IN_SNAPSHOT01_MANIFEST | NOT_COMPLETED>
ORPHAN_FOLDERS_INVENTORIED: <n | NOT_COMPLETED>
HISTORY_SNAPSHOTS_CAPTURED: <n | NOT_COMPLETED>
PAYLOAD_FILES_CAPTURED: <n | NOT_COMPLETED>
PAYLOAD_BYTES_CAPTURED: <n | NOT_COMPLETED>
COPIED_FILES_VERIFIED_BYTE_IDENTICAL: <n of n | NOT_COMPLETED>
MANIFEST_SHA256: <sha256 | NONE>
MANIFEST_BYTES: <n | NONE>
MANIFEST_JSON_VALID: <YES | NO | NOT_WRITTEN>
FOLDER_A_STATE_UNCHANGED: <YES | NO | NOT_COMPLETED>
FOLDER_B_STATE_UNCHANGED: <YES | NO | NOT_COMPLETED>
ACTIVE_AND_PRIMARY_HEADS_UNCHANGED: <YES | NO | NOT_COMPLETED>
WORKTREE_STATUS_UNCHANGED: <YES | NO | NOT_COMPLETED>
SNAPSHOT01_MODIFIED_BY_THIS_TASK: NO
FILES_CREATED_OUTSIDE_DESTINATION_BY_AGENT_COMMANDS: NONE
FILES_MODIFIED_IN_WORKTREES_BY_THIS_TASK: NONE
LOCAL_HISTORY_MODIFIED_BY_THIS_TASK: NONE
PENDING_EDITOR_CHANGES_RESOLVED: NONE
GIT_MUTATION_EXECUTED: NO
COMPILE_OR_TEST_EXECUTED: NO
```
