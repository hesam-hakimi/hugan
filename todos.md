Prepare a complete CLUE development handoff for a new GitHub Copilot session.

The purpose is to preserve the effective instructions, project knowledge, implementation status, evidence and unfinished work from this session so that a new session can continue productively without access to this conversation.

This task produces handoff documents and a ready-to-paste startup prompt. Preserve the current development work and capture the state at a clear checkpoint without interrupting active operations.

All responses, documents and prompts must be in English.

1. Reconstruct the actual current state

Inspect the active workspace and reconcile it with this conversation, the initial instructions, repository guidance and existing project references.

Previously used locations include:

* Application repository: C:\repos\fcrm_clue
* Project references: C:\repos\FCRM
* Existing local configuration: C:\repos\FCRM.env
* Previously reported branch: feature/clue-durable-core

Verify the actual paths and branch. Record:

* Repository root, branch, HEAD and checkpoint timestamp.
* Relevant uncommitted changes and any active development or test operations.
* Actual application entry points, important modules, configuration locations and execution commands.
* Current package/artifact locations and their relationship to the tested source.

Treat earlier version numbers and test counts as historical until reconciled with the current checkout. Distinguish inspected implementation, executed tests, previous reports and proposed work.

2. Create a small, self-contained handoff package

Reuse an existing maintained handoff location if one exists. Otherwise create:

docs/handoff/clue/CLUE_HANDOFF.md
docs/handoff/clue/START_NEW_SESSION.txt

Include essential supporting reference documents under:

docs/handoff/clue/references/

The handoff must contain the information needed to continue even when the new session cannot read this conversation.

For references outside the application repository, include the necessary non-secret documents or consolidate their relevant content with clear source attribution. Preserve relative links and document provenance.

List the important files with their purpose, actual location and reading order. Distinguish reference material from executable source and generated artifacts.

Do not copy configuration secrets, private keys, customer data or raw API payloads into the handoff. Record configuration variable names and retrieval locations without recording their values.

3. Capture the complete project context

Document the current understanding of:

* The business objective and the Rahona → ADIDO/TIBCO → on-prem VMC2 → Symcor → Tungsten → correlated output flow.
* Input and output contracts, source-record identity, multiple deliveries, debit/credit handling, document associations and partial results.
* Symcor request construction, SOAP/XML and attachment handling, native sample availability, image formats and any remaining conversion work.
* Tungsten configuration, front/back processing, metadata mapping, confidence handling and actual DEV integration evidence.
* Durable state, ownership, checkpoints, duplicate prevention, retry waiting, held outcomes and restart behavior.
* Scheduling and queue behavior, including AutoSys integration, overlapping invocations, provider concurrency, rate limits and downstream backlog control.
* Local logging, the TD Dynatrace integration, offline logging tests, DEV ingestion verification and the checks still required on VMC2.
* Deployment/runtime assumptions, packaging, filesystem requirements, retention, output acknowledgement and operational dependencies.

Mark each important point as implemented, tested, agreed, proposed or unresolved, as appropriate.

Preserve unresolved questions accurately. For example, concurrency, requests per second and records per request are different quantities; a reported 15-minute schedule is not automatically a 15-minute completion requirement.

Record any difference between the local implementation and the infrastructure available or approved on VMC2.

4. Reconcile all recent workstreams

Explicitly reconcile the recent instructions concerning:

* Queue, ownership, scheduling, retry waiting and backpressure.
* Logging validation and Windows-to-DEV Dynatrace testing.
* Image conversion, SOAP fault handling and acceptance-test refinements.
* Provider integration, packaging and delivery preparation.

For each workstream, record:

* Current status: completed, running, pending, externally blocked or result unavailable.
* Relevant files and existing helpers/tests.
* What was actually verified.
* What remains to be done.
* The next concrete action and its completion evidence.

An issued prompt is not proof that the task ran. Missing results are not proof that it never started. Use the actual workspace and active-session state to resolve this where possible.

5. Preserve evidence and working rules

Include an evidence table covering:

* Offline tests.
* Packaged acceptance runs.
* Live Symcor DEV calls.
* Live Tungsten DEV calls.
* Dynatrace ingestion and verified destination visibility.
* VMC2/RHEL and AutoSys execution.

For each available result, record the command, source revision or working-tree state, outcome and artifact location. Keep fixture-based behavior separate from real provider behavior.

Preserve the effective user preferences:

* English throughout the development environment.
* Inspect source and documents through text/filesystem access.
* Reuse existing helpers, fixtures and meaningful tests.
* Continue within previously granted authority without repeatedly requesting routine approval.
* Preserve user changes and focus on delivery.
* Credential replacement was deferred by the owner. Record that decision accurately without treating it as a renewed global blocker or claiming replacement occurred.

Older documentation that says implementation is paused must be identified as historical if superseded by the current development instructions.

6. Define the new session’s ownership

State whether the current session is handing over responsibility or continuing in parallel.

If work remains active:

* Record the current session’s scope and files or resources being changed.
* Give the new session a bounded task that can proceed independently.
* Identify shared modules, test workspaces, databases, outputs and packaging operations that could conflict.
* Specify the integration owner and the evidence required before combining changes.

Use isolated workspaces or processing directories where needed. Shared source changes require a clear ownership boundary. Do not assign the same active edits to both sessions.

If active ownership cannot be established, give the new session useful inspection or planning work on the affected area until that boundary is resolved, while allowing independent work to continue.

7. Write the complete new-session startup prompt

START_NEW_SESSION.txt must be ready to paste directly into a new GitHub Copilot chat.

It must instruct the new agent to:

* Locate the actual repository and handoff package.
* Read CLUE_HANDOFF.md completely, then the listed essential references and source files for its assigned task.
* Verify the current checkout against the recorded checkpoint and reconcile newer changes without resetting existing work.
* Briefly report which files it actually read, the current implementation status and its assigned next task.
* Preserve the effective instructions, existing authority and active-session ownership boundaries.
* Continue the assigned development task through implementation and appropriate verification when its prerequisites are available.

The startup prompt must use real workspace paths and repository-relative references. It must not depend on ChatGPT sandbox links, conversation IDs, screenshots or access to this chat.

If the new session runs in another workspace or on another machine, explicitly identify the source checkout, uncommitted work and reference files that must be transferred or otherwise made available. A handoff document alone does not provide source-code access.

8. Validate and deliver

Check that the handoff is internally consistent, its local paths and links resolve, its status claims match the evidence, and its startup prompt is usable without this conversation.

Use focused document validation. Existing valid test reports can be referenced without repeating the full test suite solely to prepare the handoff.

Return:

* The actual handoff file paths.
* A short description of the assigned next task.
* Any specific missing information that the handoff could not reconstruct.
* The complete contents of START_NEW_SESSION.txt so I can copy it directly into the new session.

Complete the files and the startup text in this task; do not stop at proposing a handoff outline.
