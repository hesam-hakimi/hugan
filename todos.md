Continue the current CLUE delivery candidate and incorporate the queue/scheduler requirements from the latest meeting. Preserve the existing implementation, packaging, and any in-progress image, fault-policy, and acceptance refinements.

Keep all engineering work in English. Use the actual batch entry point and existing durable state, ownership controls, fixtures, and tests.

First trace the executable path and report which of these behaviors already exist:

* Durable pending-work selection and registration of files arriving during a run.
* Exclusive ownership, overlapping invocations, and recovery of abandoned work.
* Independent Symcor and Tungsten dispatch/concurrency controls.
* Request-rate limits, persisted retry timing, and backlog/storage limits.

Then complete only the missing behavior needed for the current single-host release.

Select and document one clear application ownership model. A second invocation must not process an already-owned delivery or multiply the effective provider limits. Keep complete incoming files durably pending until capacity is available.

Define application exit outcomes and distinguish intake acceptance, active processing, batch completion, partial completion, and failure. Record the actual AutoSys trigger/overlap configuration as an external confirmation item; do not assume a 15-minute schedule requires processing to finish within 15 minutes.

Use independently configurable limits for each provider. Distinguish in-flight requests, requests per second, and records per API request. Do not configure any of them to 100 solely from the meeting discussion.

Feed committed Symcor image results into Tungsten as capacity becomes available. Preserve page-level checkpoints, held unknown outcomes, source associations, and per-file output rules. Limit upstream work when the downstream backlog or disk threshold is reached.

Demonstrate through the actual orchestration path with injected offline providers:

1. Two overlapping application invocations.
2. Additional complete files arriving during an active batch.
3. A process interruption followed by restart and ownership recovery.
4. Enforced provider limits and restart-safe retry waiting.
5. A slow Tungsten stage causing controlled upstream backpressure.

Extend the existing acceptance data to a few hundred varied records across multiple files. Use bounded fake delays or controlled clocks where appropriate. Report observed maximum concurrent calls, processed/pending/held counts, duplicate effects, and input/output reconciliation. Label timings as offline measurements.

The latest meeting leaves the final debit/credit query strategy open pending native samples. Preserve all returned associations and expose unexpected multiplicity; do not impose an unconfirmed cardinality rule.

Reuse existing tests, add only missing behavioral coverage, and rebuild the release if code changes. Finish with the demonstrated queue behavior, remaining AutoSys configuration questions, tested commit, and artifact paths. Continue independent delivery work while external answers are pending.
