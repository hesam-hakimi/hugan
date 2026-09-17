Continue CLUE development using the handoff already created in the local workspace.

The immediate task for this session is logging validation and the existing TD Dynatrace integration. This message updates the assigned-task and ownership assumptions in START_NEW_SESSION.txt. Preserve the other effective project instructions.

All development responses, code, tests and documents must remain in English.

1. Restore the context

Locate and read completely:

* C:\repos\fcrm_clue\docs\handoff\clue\CLUE_HANDOFF.md
* C:\repos\fcrm_clue\docs\handoff\clue\START_NEW_SESSION.txt

Then read the referenced documents and actual source files relevant to logging, configuration, the batch entry point and existing tests.

Verify the current repository, branch, HEAD and working-tree changes. Reconcile changes made after the recorded checkpoint without resetting or discarding existing work.

Briefly report what you actually read and the current logging implementation you found. Continue with the work after that report.

2. Apply the current priority

Complete the independently testable logging work.

Treat the Symcor getCriterionRules task as a separate follow-up. Missing provider settings or answers to Q01–Q11 do not block local logging tests.

Use existing queue/recovery evidence where relevant. Add verification only where the logging changes or an actual unresolved issue justify it.

3. Establish bounded ownership

Treat the handoff’s statement that no other session is active as checkpoint information.

If the main checkout is still being developed by another session, use an isolated worktree and branch for logging changes, with a separate processing workspace. Identify how changes will be integrated and keep shared release packaging under one owner.

If this is the only active session, continue on the current checkout while preserving existing work.

A separate processing –workspace isolates state and outputs; it does not isolate edits to shared source files.

4. Validate the existing logging path

Inspect and reuse the current logger, forwarding adapter, configuration helpers and fixtures.

Exercise the actual application logging path with offline providers and an injected logging transport. Cover:

* Successful file processing and output completion.
* Pending work, retry waiting, held outcomes and interruption/resume.
* Correlation between execution IDs and stable delivery/item IDs.
* Structured fields, severity, timestamps and safe error details.
* Redaction using synthetic sensitive values, including exception paths.
* Repeated initialization without duplicate handlers.
* Transport timeouts, retry/buffering behavior and buffer exhaustion.

Verify that logging failures do not cause indefinite blocking or duplicate business processing. Keep durable processing state as the recovery authority.

Reuse existing coverage and fix demonstrated issues.

5. Validate DEV forwarding when its prerequisites are available

Inspect the supported TD logger package instructions. If its source or approved package is accessible, integrate or install it through the existing project environment.

Use existing configuration inspection helpers and report configuration names and presence only.

When the DEV destination, authorized configuration and network access are available, send one harmless uniquely identifiable event through the CLUE logging path. Verify the ingestion response and, where access permits, locate the exact event in the intended DEV destination.

Report ingestion acceptance and destination visibility separately. For the /api/v2/logs/ingest route, handle documented partial-ingestion responses.

If a prerequisite is missing, complete the offline work and identify that specific dependency.

6. Deliver a clear checkpoint

Run the relevant tests and rebuild the release if the implementation changes require it.

Update the handoff with:

* Source revision and changes made.
* Test commands and actual results.
* Local logging status.
* TD package integration status.
* DEV ingestion and destination-visibility status.
* Remaining VMC2/AutoSys verification.
* The next concrete task and any active-session ownership boundaries.

Preserve the distinction between offline fixtures, real DEV integration and VMC2 execution. Continue through implementation and appropriate verification.
