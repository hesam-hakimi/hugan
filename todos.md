Continue the current CLUE candidate and address the two local findings reported in:

docs/handoff/clue/CLUE_SOLUTION_REVIEW.md

This is a bounded correction task. Preserve the existing implementation, unrelated changes, active-session ownership and acceptance workflow. Keep live Dynatrace parked and preserve the effective owner decisions.

All development output must remain in English.

1. Reconcile the findings with the actual source

Read the complete findings and their evidence. Verify the reviewed revision against the current checkout and the previously reported 204-test release.

Trace delivery leases and workspace coordinator leases separately. Explain precisely why the earlier lease-renewal implementation did or did not cover coordinator ownership.

For each actual defect, establish a small reproducible regression before fixing it. If a finding is already resolved or relies on an unsupported contract assumption, correct its classification with evidence rather than manufacturing a code change.

2. Fix workspace coordinator renewal

Ensure a healthy coordinator retains exclusive ownership beyond its original lease duration, including during long provider waits.

Use the existing owner identity and fencing model. Preserve:

* Recovery after an owner crashes and renewal stops.
* Conditional release on a controlled stop.
* Rejection of stale owners and stale renewal attempts.
* Pending work when another invocation is already active.

If coordinator ownership is lost, prevent that invocation from dispatching new work and preserve unresolved in-flight outcomes through the existing handling.

Demonstrate this through the actual orchestration path: a healthy owner remains exclusive beyond its original TTL, a competing invocation cannot take over, and recovery becomes possible after renewal stops.

Use controlled time or bounded delays.

3. Fix completion-marker validation for the supported contract

Inspect the marker formats the application documents, generates and accepts.

Where the contract supplies size, hash or other required metadata, validate those declarations against the exact input bytes that will be processed, before business/API processing begins.

Handle malformed or mismatched inputs through the existing explicit rejection, hold or quarantine path. Ensure that validating one file version cannot lead to processing another.

Preserve a documented signal-only .done profile if it is intentionally supported. Do not invent mandatory metadata or claim checksum verification for a marker that does not provide a checksum.

Add focused coverage for applicable cases:

* Valid marker and matching file.
* Size mismatch.
* Same-size content alteration detected by the declared hash.
* Missing or malformed required metadata.
* Existing signal-only compatibility, if supported.

4. Verify and rebuild

After the final code changes, run the focused regressions and the existing full suite once.

Rebuild the release and reuse the documented isolated-extraction acceptance run. Confirm that duplicate delivery, interruption/resume and output correlation still work.

Avoid unrelated enhancements or another comprehensive review cycle.

5. Close the findings with evidence

Update the existing review and handoff with:

* The status of each finding.
* The cause and correction.
* Reproduction and regression evidence.
* Tested source revision.
* Updated release path and checksum.
* Remaining external integration dependencies.

Keep unavailable provider contracts, business acceptance and VMC2/AutoSys validation explicitly separate from these local fixes.

Complete the corrections, verification and updated delivery checkpoint. Report any finding that could not be resolved with its exact remaining reason.
