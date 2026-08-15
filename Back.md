LOCAL_PHASE_SB2R — EXACT REVERSIBLE RECOVERY OF THE AUDIT-CREATED DIRECTORY

Your SB2 audit correctly returned FAIL, but its malformed cached-host command accidentally created this directory at the canonical repository root:

C:\repos\etl-extension\etl_fw2\etl_framework_extension\System.Management.Automation.Internal.Host.InternalHost

Your report states that:

* the directory did not exist at audit start;
* it was created solely by the malformed SB2 audit command;
* it contains 96 files totaling 21,257,633 bytes;
* it contributes exactly 72 new pending entries;
* expanded pending count increased from 23 to 95;
* eight associated Code processes were stopped;
* no original protected, S-A, or S-B candidate byte changed;
* the directory was not deleted.

This task authorizes only a reversible quarantine move of that exact directory outside every Git worktree and workspace folder.

It does not authorize deletion, repair, testing, process management, Keep, Undo, S-C, Git, package, VSIX, PR, CI, or any other mutation.

1. Absolute restrictions

Do not:

* edit any source, test, package, configuration, documentation, or evaluation file;
* modify any of the three S-B candidate files;
* modify any S-A or pre-existing pending file;
* delete the accidental directory;
* use Remove-Item, rm, rmdir, del, git clean, or any equivalent deletion command;
* move, delete, or alter .vscode-test;
* restart, stop, kill, or otherwise manage any process;
* click Keep or Undo;
* stage, commit, push, stash, reset, checkout, merge, or alter a worktree;
* compile, lint, test, build, package, install, download, or use network access;
* create a quarantine directory inside any Git worktree or selected workspace folder;
* use a wildcard, unresolved relative path, broad repository-root operation, or recursive operation against any parent directory.

If any verification is ambiguous, stop without moving anything.

2. Reverify repository state before recovery

Verify read-only:

* Root:
    C:\repos\etl-extension\etl_fw2\etl_framework_extension
* Origin:
    https://github.com/TD-Universe/agentic_etl.git
* Branch:
    feature/v3-agentic-redesign
* HEAD:
    b2e44c3a1a051aa7fa6008831d225bc06d22e847
* Worktree count: 3
* Staged count: 0
* Expanded pending count: 95

Confirm that exactly:

* 20 paths are the original pre-S-B pending paths;
* 3 paths are the S-B candidate;
* 72 additional pending entries are beneath only:
    System.Management.Automation.Internal.Host.InternalHost\

If any additional unexplained pending path exists, stop.

3. Reverify protected and candidate bytes

Recompute the four authoritative S-A hashes:

* EtlSettingsInventory.ts
    6B99E6EB1851AB45050AE69225D06A59CE6AE0CE85871BF7A9C1DEAD0FBADD84
* EtlSettingsProvenance.ts
    09CD4A53A92D845D6C7F34279CBD2B2495F6C2EAE03D14567CBBC8474D553AC8
* EtlSettingsVsCodeBindings.ts
    0A010841E9806F6FDB51C35559EE20CB4A39A246F29001CA6A9DD749A3CD15D1
* settingsInventoryProvenance.test.ts
    64A4682CB2428B70F1E4B99B706A3050542502E14A57CC4BF7336D5711AB8AE2

Recompute the S-B candidate hashes and compare them with the SB2 start/end values:

* EtlAgentContextCanonicalForm.ts
    428327984682B2F473CD9AD481792C0D6029D78C1FFB655FB3435FF8D893C192
* ResolvedEtlAgentContext.ts
    DFC19D693C96DC0180CBBA92AA66F620582344FFD89ADA6100DACC3240D678CD
* resolvedEtlAgentContext.test.ts
    E35BFE5DE246A6956533B2B1BCE761F35225264B29A51B770557C26010F988C5

Compare all 16 original pending-path hashes and the complete SB2 protected manifest with your captured audit-start values.

If any protected or candidate hash differs, stop.

4. Prove the accidental-directory identity

Resolve the exact source with a literal absolute path.

Before moving it, prove:

1. The resolved path equals exactly:
    C:\repos\etl-extension\etl_fw2\etl_framework_extension\System.Management.Automation.Internal.Host.InternalHost
2. It is a directory, not a file.
3. It was absent from the SB2 audit-start inventory.
4. It contains no Git-tracked or staged path.
5. All 72 additional pending entries are descendants of this directory.
6. No original 23 pending path is inside it.
7. It contains 96 files totaling 21,257,633 bytes, or explain any discrepancy before proceeding.
8. Neither the directory nor any descendant is a:
    * symbolic link;
    * junction;
    * mount point;
    * reparse point.
9. No descendant resolves outside the exact source directory.
10. No file timestamp predates the audit-created directory in a way that contradicts the recorded accident chronology.

Create an in-memory, deterministically sorted source manifest containing for every file:

* relative path;
* length;
* SHA-256.

Compute a single manifest digest from that sorted manifest.

Do not write the manifest inside the repository.

If any condition fails, do not move anything.

5. Select a safe quarantine destination

Resolve the operating-system temporary directory.

Create a unique quarantine parent named similarly to:

SB2_AUDIT_QUARANTINE_20260815_<unique-suffix>

The final destination must:

* be on the same volume as the source so the directory move can be atomic;
* be outside the canonical repository;
* be outside all three Git worktrees;
* be outside every selected multi-root workspace folder;
* not already exist;
* not be a descendant of the accidental source directory;
* not be .vscode-test;
* contain no pre-existing user file.

Report the fully resolved destination before moving.

If a same-volume safe destination cannot be established, stop. Do not fall back to copy-and-delete.

6. Perform exactly one reversible move

After every check passes, move only the literal source directory to the verified quarantine destination using an exact-path directory move.

Prefer a same-volume atomic directory move such as the platform equivalent of System.IO.Directory.Move.

Do not:

* recursively delete the source;
* copy selected files;
* merge into an existing destination;
* overwrite anything;
* operate on the repository root or source parent;
* perform any second filesystem mutation.

If the move fails, stop immediately. Do not retry with deletion, force, wildcard, or fallback logic.

7. Post-move verification

After the move, prove:

* the original source path no longer exists;
* the quarantine destination exists;
* the destination remains outside all worktrees/workspace folders;
* destination file count is exactly 96;
* destination total bytes are exactly 21,257,633;
* the destination’s sorted relative-path/length/SHA-256 manifest exactly matches the pre-move source manifest;
* repository expanded pending count returned from 95 to exactly 23;
* the 72 audit-created pending entries disappeared;
* the original 20 pending paths remain present and byte-identical;
* the three S-B files remain present and byte-identical;
* all four S-A hashes still match A1H;
* every protected hash is unchanged;
* staged count remains 0;
* root, origin, branch, HEAD, and three-worktree inventory are unchanged;
* .vscode-test is untouched;
* the Copilot S-B review card still contains exactly the same three files;
* no process state was changed by this recovery task.

Do not delete the quarantine destination after verification.

8. Required report

Return:

1. Repository identity.
2. Exact pre-move pending classification.
3. Source-directory identity and reparse/tracked-content checks.
4. Source count, bytes, and manifest digest.
5. Fully resolved quarantine destination.
6. Exact move operation and exit/result.
7. Destination count, bytes, and manifest comparison.
8. Post-move pending inventory.
9. Start/end hashes for all S-A and S-B files.
10. Start/end comparison for all protected paths.
11. Confirmation that no other operation occurred.
12. Exact quarantine path retained for later disposition.

This recovery does not authorize S-B repair or Keep.

Finish with exactly one block and no text after it.

SUCCESS:

ACCIDENT_PATH_EXACTLY_VERIFIED: YES
TRACKED_CONTENT_IN_ACCIDENT_PATH: NO
REPARSE_POINT_DETECTED: NO
QUARANTINE_DESTINATION_SAFE: YES
REVERSIBLE_MOVE_SUCCEEDED: YES
SOURCE_PATH_ABSENT_AFTER_MOVE: YES
QUARANTINE_MANIFEST_MATCHES_SOURCE: YES
PENDING_COUNT_RESTORED_TO_23: YES
ORIGINAL_20_PATHS_BYTE_IDENTICAL: YES
S_A_HASHES_MATCH_A1H: YES
S_B_CANDIDATE_HASHES_UNCHANGED: YES
PROTECTED_PATH_DRIFT: NO
STAGED_COUNT: 0
SAFE_TO_CLICK_KEEP: NO
SAFE_TO_REPAIR_S_B: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB2R_RECOVERY_COMPLETE

FAILURE:

ACCIDENT_PATH_EXACTLY_VERIFIED: YES|NO
TRACKED_CONTENT_IN_ACCIDENT_PATH: YES|NO|UNKNOWN
REPARSE_POINT_DETECTED: YES|NO|UNKNOWN
QUARANTINE_DESTINATION_SAFE: YES|NO
REVERSIBLE_MOVE_SUCCEEDED: YES|NO
SOURCE_PATH_ABSENT_AFTER_MOVE: YES|NO
QUARANTINE_MANIFEST_MATCHES_SOURCE: YES|NO|UNKNOWN
PENDING_COUNT_RESTORED_TO_23: YES|NO
ORIGINAL_20_PATHS_BYTE_IDENTICAL: YES|NO
S_A_HASHES_MATCH_A1H: YES|NO
S_B_CANDIDATE_HASHES_UNCHANGED: YES|NO
PROTECTED_PATH_DRIFT: YES|NO|UNKNOWN
STAGED_COUNT: 
SAFE_TO_CLICK_KEEP: NO
SAFE_TO_REPAIR_S_B: NO
SAFE_TO_PROCEED_TO_S_C: NO
LOCAL_PHASE_SB2R_RECOVERY_BLOCKED
