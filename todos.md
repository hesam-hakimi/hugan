 I reviewed the folder structure. It covers the main areas well. I would add explicit ownership for processing control and durable state, for example processing_control/ and adapters/state/, alongside the existing pipeline and observability modules.

Along with AutoSys, I suggest we cover these points in the design:

1. Logging: structured logs with run/file/request IDs, processing stage, timing and safe error codes, forwarded to Dynatrace. We should confirm log collection, retention and alerts with the infrastructure team.
2. File recovery: track both file-level and record/document-level progress, so a failure halfway through a file resumes from committed checkpoints. Reading the file should not mark it as completed.
3. Duplicate prevention: use a stable source delivery ID, content verification and an atomic claim in the state store. Completed work should be reused, while interrupted work should resume. We also need to preserve legitimate requests for the same cheque from different cases.
4. API recovery: once Symcor images and document IDs are safely stored, a Tungsten failure should resume from the Tungsten stage. A timeout after submission needs a status/idempotency strategy because the provider may already have accepted the request.
5. Output and scheduling: define partial-success handling, reconciliation, output acknowledgement and AutoSys return-code/restart behavior. A rerun should use the same controlled recovery path.
6. Capacity: the indicative 500–1,000 requests/day is a starting point. We need average and peak cheques per request, image sizes, API latency/rate limits and the expected completion window before confirming capacity. Bounded parallelism and chunked processing should be part of the design.

These responsibilities fit the proposed structure. I suggest we agree the state-store option with the VMC2/PDL team, document the recovery contracts, and include crash/restart and duplicate-delivery scenarios in the tests. We should also confirm the Python/package requirements with PDL.
