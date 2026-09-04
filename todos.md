
ETL-0904-SNAPSHOT01 — Evidence Preservation Prompt

```text
TASK_ID: ETL-0904-SNAPSHOT01
TYPE: AUTHORISED EVIDENCE SNAPSHOT — COPY ONLY, OUTSIDE BOTH WORKTREES

Run this in a fresh, normal local VS Code Agent chat on Windows. Do not
use the Agent that implemented or self-reviewed IMPL04, and do not use the
ETL Orchestrator.

Echo TASK_ID: ETL-0904-SNAPSHOT01 as the first line of your report.

=========================================================
AUTHORISATION AND ITS EXACT LIMITS
=========================================================

The owner authorises exactly one bounded class of write:

- create one new destination root outside both worktrees; and
- create only the necessary child directories and new snapshot files
  beneath that destination root.

Everything else remains forbidden:

- Do not modify, move, rename, or delete anything inside either worktree
  or anywhere under %APPDATA%\Code\User\History.
- Do not accept, discard, Keep, Undo, or otherwise resolve any pending
  VS Code chat edit. Leave every pending edit exactly as it is.
- No type-check, compile, lint, emit, test, parser execution, runner,
  Extension Host, package, install, activation, or consumer write.
- No git command that mutates the index, worktree, refs, stash, branch,
  tags, or history. No add, commit, stash, checkout, restore, reset,
  clean, merge, rebase, cherry-pick, tag, or worktree add/remove.
- Use read-only git commands with `git --no-optional-locks` wherever git
  is needed.
- Do not create a helper script, temporary file, transcript, archive, or
  intermediate report anywhere. Keep the pre-write baseline in memory.
- Do not compress, archive, encrypt, normalise, re-encode, or otherwise
  transform payload files. Copy their bytes unchanged.
- Every destination file write must use fail-if-exists / CreateNew
  semantics. Do not use Copy-Item's default overwrite behaviour. For
  payload copies use [System.IO.File]::Copy(source, destination, $false)
  or an equivalent operation that cannot overwrite. For manifest.json,
  use FileMode.CreateNew or an equivalent atomic fail-if-exists method.

If any destination file already exists or any write would overwrite a
file, stop immediately. Do not delete or reuse the directory. Report:

  BLOCKED_DESTINATION_CONFLICT

Report what you find and copy only what this prompt authorises. Fix,
clean up, stage, or propose nothing.

=========================================================
WHY THIS EXISTS
=========================================================

Most of the current worktree state exists in no commit and no stash.
VS Code Local History is a bounded evidence source; at least one relevant
history folder has reached 50 entries, and one relevant file already has
no surviving snapshot preceding a window that matters. Further editor
writes can evict the remaining baselines.

This task preserves the current dirty working set and all surviving Local
History associated with it. It is evidence insurance, not cleanup,
qualification, acceptance, or a substitute for independent review.

=========================================================
REPOSITORY
=========================================================

Active worktree:
  C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Linked primary worktree:
  C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

The active worktree is a linked Git worktree of the primary. Its Git
administrative directory and common directory may differ. Do not enter
or modify the primary worktree. Read-only inspection of Git-reported
identity is permitted.

Use the listed paths only for navigation and scope. Independently
re-derive every repository identity, path, hash, count, and timestamp.
If the active worktree or linked-worktree identity does not match the
live evidence, stop before writing and report:

  BLOCKED_REPOSITORY_IDENTITY_MISMATCH

=========================================================
DESTINATION SELECTION AND SAFETY
=========================================================

Complete this preflight before any write:

1. Resolve the canonical paths of the active worktree, the linked primary
   worktree, their parent repository tree, %APPDATA%\Code\User\History,
   known VS Code profile roots, installed-extension roots, QA roots, and
   consumer-workspace roots. Resolve reparse points rather than comparing
   unnormalised strings.
2. Choose an existing, writable parent under %USERPROFILE% that is outside
   every excluded root above. The snapshot destination itself must be a
   new direct child of that safe parent. If disjointness cannot be proved,
   stop and report BLOCKED_DESTINATION_SAFETY_UNKNOWN.
3. Name the new destination root exactly in this form, using the actual
   current UTC time and Windows-safe characters:

     ETL-SNAPSHOT-ETL-0904-SNAPSHOT01-<UTC>

   Example timestamp format only: 20260904T190000Z
4. Canonicalise the existing parent and validate the planned full child
   path before creation. Reject path traversal, reparse-point redirection,
   or containment within any excluded root.
5. Confirm the destination root does not exist. Print its exact absolute
   path in the chat before the first write. If it exists, stop and report:

     BLOCKED_DESTINATION_EXISTS

Do not create the destination until S4 has been captured in memory.

=========================================================
COMPLETION MODEL AND MANDATORY ORDER
=========================================================

A valid manifest.json, written as the final destination file, is the only
completion marker. A directory with no manifest.json, or with an invalid
manifest.json, is not a complete snapshot.

Perform the work in exactly this order:

1. Complete all read-only identity, scope, and destination preflight.
2. Perform S1 through S4 and hold the full S4 baseline in memory. No file
   or directory may have been created yet.
3. Create the new destination root and its necessary child directories.
4. Copy the S1 and S2 payload files using fail-if-exists semantics.
5. Perform S5 and verify every payload copy against its S4 source hash.
6. Perform S6 immediately before manifest creation and compare all source
   state against S4.
7. Only if S5 passes completely and both S6 source-state verdicts are YES,
   write manifest.json using CreateNew as the final destination write.
8. After writing manifest.json, perform read-only parse validation, obtain
   its byte size, and compute its SHA-256 for the report. Do not alter it.

If any exception, mismatch, unsafe condition, source-state change, or
incomplete verification occurs after destination creation:

- stop;
- leave the partial directory exactly as it is;
- do not delete, rename, repair, resume, or reuse it;
- do not write manifest.json; and
- report SNAPSHOT_STATUS: INCOMPLETE and the last completed step.

If blocked before destination creation, report SNAPSHOT_STATUS: BLOCKED.

=========================================================
WHAT TO CAPTURE
=========================================================

S1 — THE DIRTY WORKING SET

Derive the complete current dirty set from:

  git --no-optional-locks status --porcelain=v1 --untracked-files=all

Do not assume a count or reuse a prior inventory. Preserve the raw output
verbatim. Determine separately whether anything is staged.

Copy every dirty repository file, tracked or untracked, preserving its
repository-relative path beneath:

  payload/worktree/

Fail closed if a dirty item is missing, changes type during collection,
or is a directory, symlink, junction, reparse point, or other non-regular
file whose exact byte-copy semantics are not established. Report the item
and do not improvise.

S2 — COMPLETE LOCAL HISTORY FOR EACH DIRTY PATH

For each dirty repository path, locate its matching folder under:

  %APPDATA%\Code\User\History

Match by reading candidate entries.json files and comparing their decoded
resource URIs to the canonical source path. Do not infer a match from a
folder name or filename alone. If zero matches exist, record
NO_HISTORY_FOUND. If more than one distinct folder claims the same resource,
record every match and report the ambiguity; do not silently choose one.

For every matched history folder, copy without filtering:

- the complete entries.json; and
- every other regular file in that folder, including every snapshot.

Preserve each history folder as a distinct directory beneath:

  payload/local-history/

Use a collision-proof destination name that includes the original history
folder identifier. Record the source-to-destination mapping in the manifest.

NO_HISTORY_FOUND is a finding, not a snapshot failure. Do not convert it to
"unchanged", zero history, or proof that no prior modification occurred.

S3 — TASK-WINDOW ANNOTATION

From the chat-request labels and timestamps actually stored in each copied
entries.json, identify entries associated with:

- IMPL03;
- IMPL04; and
- the implementing Agent's self-review after IMPL04.

Record each supported mapping in the manifest with dirty repository path,
history-folder identifier, entry ID, snapshot filename, timestamp, and exact
chat-request label. If a mapping is absent or ambiguous, record
NOT_IDENTIFIED or AMBIGUOUS with the evidence. Do not guess.

These annotations do not select the payload: all history files are already
captured by S2.

S4 — PRE-WRITE STATE BASELINE, HELD IN MEMORY ONLY

Before creating the destination or any child directory, capture in memory:

Repository identity and state:

- `git --no-optional-locks rev-parse --git-dir`;
- `git --no-optional-locks rev-parse --git-common-dir`;
- `git --no-optional-locks rev-parse --show-toplevel`;
- branch;
- HEAD;
- raw porcelain status;
- staged-path inventory; and
- active and primary worktree records needed to prove linked identity.

For every dirty repository file:

- canonical absolute source path;
- repository-relative path;
- SHA-256;
- byte size;
- source mtime in UTC;
- line count; and
- counts of CRLF, bare LF, and bare CR line endings, computed from bytes.

For every matched Local History folder:

- canonical folder path and folder identifier;
- decoded resource URI;
- a complete, ordinal filename inventory;
- for every regular file, SHA-256, byte size, and source mtime in UTC;
- SHA-256 and byte size of entries.json specifically;
- total entry count; and
- earliest and latest entry timestamps and entry IDs as recorded in
  entries.json.

Also retain the S3 annotation mapping and every NO_HISTORY_FOUND or ambiguous
history result. Do not write S4 to a temporary file.

S5 — VERIFY EVERY PAYLOAD COPY

After all payload files have been copied and before manifest creation:

- enumerate every destination payload file;
- prove that the destination relative-path inventory exactly matches the
  planned S1/S2 payload inventory from S4;
- recompute SHA-256 and byte size for every destination payload file; and
- compare each destination value to the corresponding S4 source value.

Report the exact comparison count and every missing, extra, or mismatching
path. Compare against S4, not against a newly sampled source hash.

If any payload file is missing, extra, or not byte-identical, S5 fails. Do
not write manifest.json. Report SNAPSHOT_STATUS: INCOMPLETE.

S6 — PROVE THE SOURCES REMAIN UNCHANGED

After S5 passes and immediately before manifest.json is written, re-derive
the source state and compare it to S4.

For the repository, compare:

- branch and HEAD;
- raw porcelain status and staged-path inventory;
- canonical dirty-path inventory; and
- SHA-256 and byte size of every S4 dirty repository file.

For every S4 Local History folder, compare:

- complete ordinal filename inventory;
- SHA-256 and byte size of every file;
- SHA-256 and byte size of entries.json;
- total entry count; and
- earliest and latest entry timestamps and entry IDs.

Report source mtime changes separately as observations; never infer their
cause. Content and inventory comparisons must not rely on mtime alone.

Produce two independent verdicts:

  SOURCE_REPOSITORY_STATE_UNCHANGED: YES / NO
  SOURCE_HISTORY_STATE_UNCHANGED: YES / NO

If either verdict is NO, name every observed delta, do not attribute its
cause without evidence, do not write manifest.json, and report
SNAPSHOT_STATUS: INCOMPLETE.

S7 — WRITE, READ BACK, AND REPORT THE MANIFEST

Only after S5 passes and both S6 verdicts are YES, construct one
machine-readable JSON object in memory and write it to:

  manifest.json

Use UTF-8 and FileMode.CreateNew or equivalent fail-if-exists semantics.
This must be the final file created in the destination. Do not write a
temporary manifest and do not rename or replace a file.

The manifest must contain at least:

- `manifestSchemaVersion`;
- task ID;
- `snapshotStatus` equal to `COMPLETE`;
- UTC generation time;
- exact absolute destination path;
- canonical excluded-root and destination-safety results;
- Git identity: git-dir, git-common-dir, show-toplevel, linked-worktree
  evidence, branch, HEAD, raw porcelain status, and staged inventory;
- for every dirty repository file, all S4 metadata and its destination
  relative path;
- for every copied Local History file, source absolute path, destination
  relative path, SHA-256, byte size, and source mtime in UTC;
- for every history folder, resource URI, complete filename inventory,
  total entry count, earliest/latest timestamps, and entry IDs;
- all S3 annotations, including NOT_IDENTIFIED or AMBIGUOUS results;
- all NO_HISTORY_FOUND paths;
- S5 planned count, verified count, and mismatch/extra/missing arrays;
- both S6 verdicts and their delta arrays; and
- a declaration that manifest.json itself is not part of the payload-copy
  verification count.

Do not place manifest.json's own SHA-256 inside manifest.json. A file cannot
contain a stable digest of its final bytes without changing those bytes.

After the CreateNew write completes, perform only read-only operations on
manifest.json:

1. read it back from disk;
2. parse it as JSON;
3. verify required top-level fields and `snapshotStatus: COMPLETE`;
4. compute its byte size; and
5. compute its SHA-256.

Report the manifest byte size and SHA-256 outside the manifest. If read-back
or JSON validation fails, do not edit or delete it. Report
SNAPSHOT_STATUS: INCOMPLETE and MANIFEST_JSON_VALID: NO.

=========================================================
EPISTEMIC RULES
=========================================================

1. Absence of Local History is not evidence of absence of change. Report
   UNKNOWN where history cannot support a conclusion.
2. A current clean or unchanged file cannot exclude a transient edit that
   was later reverted. State that limitation where relevant.
3. An mtime is an observation, not proof of the operation that produced it.
4. A byte-identical snapshot preserves evidence; it does not establish that
   the source is correct, reviewed, compiled, tested, or qualified.
5. The snapshot does not approve the 11-path protected policy, B1, A2, or
   any other implementation or test-oracle decision.
6. If evidence is missing or ambiguous, preserve and report the ambiguity.
   Do not resolve it by assumption.

=========================================================
REPORT
=========================================================

1. Begin with the required TASK_ID line.
2. Report the proposed destination and all canonical-path safety checks
   before reporting any write.
3. Report S1 through S7 in order, with raw command output where requested.
4. Report total payload files copied and total payload bytes. Keep payload
   counts separate from manifest.json.
5. If manifest.json was written, report its read-back validation, SHA-256,
   and byte size separately.
6. List every command executed in exact order. For each write command,
   identify the newly created destination path. Confirm that every write
   was confined beneath the new destination and used fail-if-exists
   semantics.
7. Confirm HEAD was never moved in either worktree and no Git mutation was
   executed.
8. Report anything material that this prompt did not ask about, but do not
   change it or propose a repair.
9. Replace every angle-bracket placeholder below with one permitted concrete
   value. Do not print choice lists literally.
10. Close with exactly these lines and then stop:

TASK_ID: ETL-0904-SNAPSHOT01
SNAPSHOT_STATUS: <COMPLETE | INCOMPLETE | BLOCKED>
DESTINATION: <absolute path | NOT_CREATED>
DIRTY_PATHS_CAPTURED: <n | NOT_COMPLETED>
HISTORY_FOLDERS_CAPTURED: <n | NOT_COMPLETED>
HISTORY_SNAPSHOTS_CAPTURED: <n | NOT_COMPLETED>
PATHS_WITH_NO_LOCAL_HISTORY: <n | NOT_COMPLETED>
COPIED_PAYLOAD_FILES_VERIFIED_BYTE_IDENTICAL: <n of n | NOT_COMPLETED>
MANIFEST_SHA256: <sha256 | NONE>
MANIFEST_BYTES: <n | NONE>
MANIFEST_JSON_VALID: <YES | NO | NOT_WRITTEN>
SOURCE_REPOSITORY_STATE_UNCHANGED: <YES | NO | NOT_COMPLETED>
SOURCE_HISTORY_STATE_UNCHANGED: <YES | NO | NOT_COMPLETED>
FILES_CREATED_OUTSIDE_DESTINATION: NONE
FILES_MODIFIED_IN_WORKTREES_BY_THIS_TASK: NONE
LOCAL_HISTORY_MODIFIED_BY_THIS_TASK: NONE
PENDING_EDITOR_CHANGES_RESOLVED: NONE
GIT_MUTATION_EXECUTED: NO
COMPILE_OR_TEST_EXECUTED: NO
```
