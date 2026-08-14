LOCAL_SA_KEEP_GATE — Bounded Keep of the Independently Accepted S-A Candidate

The fresh independent A1H re-audit completed with:

SAFE_TO_KEEP_SA: YES
SAFE_TO_PROCEED_TO_S_B: NO
LOCAL_PHASE_A1H_SA_REAUDIT_PASS

This step authorizes only the bounded retention/Keep decision for the existing four-file S-A candidate. It does not authorize any implementation, repair, cleanup, Git action, package action, or later slice.

Authorized S-A files only:

* src/core/settings/EtlSettingsInventory.ts
* src/core/settings/EtlSettingsProvenance.ts
* src/core/settings/EtlSettingsVsCodeBindings.ts
* src/test/suite/settingsInventoryProvenance.test.ts

Strict rules:

* Do not edit, save, format, create, delete, rename, restore, revert, discard, clean, stage, commit, push, build, package, install, or run CI.
* Do not modify the four S-A files.
* Do not modify package.json, package-lock.json, testPatterns.ts, protected paths, pre-existing pending files, or any unrelated file.
* Do not implement the A1H Medium or Low advisory findings in this step.
* Do not start S-B or any later slice.
* Do not treat Keep as Git acceptance, commit, PR approval, CI approval, or release approval.

Before authorizing the UI action, verify read-only:

1. Repository root, origin, branch, and HEAD still match the A1H target.
2. Staged count remains zero.
3. The Copilot review card/change set to be Kept contains exactly the four authorized S-A files above and no other path.
4. No additional S-A file or later-slice artifact exists.
5. All other pending or dirty paths remain user-owned/pre-existing and outside this Keep decision.
6. A1H’s Medium and Low findings are retained as follow-up debt and are not silently classified as fixed.
7. S-B remains explicitly unauthorized.

If the review card contains any additional file, any repository identity differs, staged count is nonzero, or current state is ambiguous, do not authorize Keep.

Return exactly:

KEEP_SCOPE_EXACT: YES|NO
STAGED_COUNT: 
S_B_AUTHORIZED: NO
SAFE_TO_CLICK_KEEP_SA_CARD: YES|NO
LOCAL_SA_KEEP_GATE_READY

or:

KEEP_SCOPE_EXACT: YES|NO
STAGED_COUNT: 
S_B_AUTHORIZED: NO
SAFE_TO_CLICK_KEEP_SA_CARD: NO
LOCAL_SA_KEEP_GATE_BLOCKED
