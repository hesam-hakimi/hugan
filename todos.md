Continue the current CLUE implementation in C:\repos\fcrm_clue. Preserve the current branch, commits, user changes and completed synthetic tests. The first-run report identified feature/clue-durable-core and commit 48b5d67; inspect the current state without resetting to that commit.

Next objective: implement and verify the real Tungsten DEV component adapter, then connect it to the new src/clue/ core.

Important owner update: the primary and secondary keys currently copied into .env are the SAME keys that your first-run report identified in the committed Postman collection. They have not been confirmed rotated. Do not use either current key for a live request.

Proceed now with all independent local work below. Do not stop at another plan.

1. Credential handling and configuration

Ensure the local .env is ignored and untracked while preserving the local file. Keep only placeholder configuration in tracked examples.

Inspect configuration through local code that reports variable names and presence only. Do not print .env contents, secret values, authorization headers or secret-bearing diffs into the conversation or subagent reports.

Prepare sanitized Postman templates using variable references in place of embedded keys. Preserve useful request structure. Do not rewrite shared Git history, force-push or rotate shared credentials yourself.

Record credential rotation as an external dependency. The API owner must invalidate both exposed keys and provide replacement credentials. Continue adapter implementation and offline verification while this is pending.

2. Establish the exact DEV request

Locate the native Postman collection, endpoint configuration and the successful DEV request referenced by the existing design/review documents. Process potentially sensitive files locally and expose only sanitized structural information.

The supplied screenshot shows a POST operation named createjobsyncwithdocuments, a jobWithDocsInitialization envelope and InputVariables, with an HTTP 200 response. Use this as corroborating evidence; obtain the complete request and response from native artifacts.

Verify the exact DEV URL, HTTP method, authentication header, content type, required input variables, document encoding, image-side values and response structure. Do not assume a body subscription/configuration identifier is the API key.

Select one key through explicit configuration. Do not send both keys, reuse Symcor authentication or automatically switch credentials after a timeout.

If essential native details are unavailable, identify precisely what is missing and continue independent implementation rather than inventing the contract.

3. Build the component adapter and test runner

Inspect the new src/clue/ interfaces and extend that core. Do not run the untouched legacy full pipeline as the next test.

Provide a reusable Tungsten component command that can validate configuration and exercise a documented request independently of the unresolved DAT input, Symcor and ADIDO integration.

Make .env loading explicit and deterministic. Keep secrets out of command arguments. Retain TLS verification and use the approved trust configuration.

Add fake-transport tests for request construction, selected-key injection, configuration loading, redaction, response parsing, authentication rejection, malformed responses and ambiguous submission outcomes. Offline tests must not contact real endpoints.

4. Execute the DEV smoke test after credential replacement

Once the API owner’s rotation is confirmed and replacement credentials are configured, perform one bounded DEV component test using an explicitly approved test image with known expected content. If rotation or the permitted sample is still missing, keep this live step pending and complete the local work.

Validate both the HTTP result and the provider’s application result. Report separately whether authentication/transport succeeded, a job was created, processing completed and expected extraction fields were returned.

A timeout after submission may leave an unknown outcome. Do not blindly resubmit or switch keys. Use status lookup only when the provider contract documents it.

Record the actual execution machine/environment, application version, test-fixture reference, duration, HTTP status, safe correlation/job references and sanitized outcome. Do not claim VMC2 readiness from a workstation test.

5. Logging in parallel

Review the existing CLUE logging implementation and the documented TD-Enterprise/td-dytp-log-python package. Preserve structured, redacted application events and avoid duplicate handler registration.

Tungsten credentials and Dynatrace credentials are separate. If the existing DEV logging destination is configured and authorized, emit one harmless correlation marker and verify it is searchable in Dynatrace. Otherwise finish local integration and report central delivery as unverified.

Keep Symcor connectivity separate: the supplied PAT test shows TCP connectivity followed by a TLS handshake/reset failure. Do not treat it as successful API connectivity or disable certificate verification.

6. Completion and continuation

Use subagents for independent contract analysis, logging integration and test review with clear file ownership. Keep secret-bearing artifacts out of their context.

Run targeted tests and the appropriate existing regression suite. Report the final branch/commit, changed behavior, exact commands/results, and the remaining concrete dependencies.

Keep these states distinct: local tests passed, credentials replaced, Tungsten DEV transport verified, extraction verified, and Dynatrace delivery verified. Do not mark the full pipeline or VMC2 integration complete.

All engineering responses, code, tests and documents must be in English. Use text and filesystem tools only; no screenshots, OCR or vision. Continue all unblocked work without repeated routine approval requests.
