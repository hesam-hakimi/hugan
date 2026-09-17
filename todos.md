Continue from the current CLUE branch and working tree. Preserve the completed implementation and the reported 56 passing offline tests.

The exposed Tungsten keys have not yet been confirmed rotated. Keep live submission disabled with those credentials. Continue all independent work now.

1. Clean the active credential-bearing artifacts

A sanitized companion template is not sufficient while the active tracked Postman collection and scripts still contain embedded credentials.

Replace embedded secret values in the active working-tree artifacts with configuration references, preserving their request semantics. Inspect and sanitize locally; report filenames and findings only, never secret values, fingerprints, raw file contents or secret-bearing diffs. Do not rewrite shared history or force-push.

2. Finish deterministic configuration

Continue using C:\repos\FCRM.env through –env-file. Moving the file is not required.

Support or document the existing PrimaryKey and SecondaryKey names through explicit aliases. Report configuration sources and presence only. Resolve the actual process Config and sessionId requirements from native artifacts, including session acquisition or expiry behavior where documented. Do not substitute the APIM key for either value.

Keep unknown values explicit and identify the exact missing information for the API owner.

3. Verify integration with the durable core

Demonstrate that the src/clue/ orchestration actually invokes the new Tungsten adapter and persists its outcomes. A separate component CLI alone does not establish that integration.

Use injected fake transport to verify successful extraction handling, interrupted execution, persisted-image reuse, ambiguous submission outcomes and source/document/page association. Preserve the rule against blind resubmission after a timeout.

Keep the OUTPUT_JSON parser explicitly provisional until a real response validates its location and structure. Do not count a fixture built from that assumption as native-contract verification.

4. Prepare the first bounded DEV call without a circular dependency

A previously saved success response is helpful but is not itself required to make the first authorized component request.

Once credential replacement is confirmed, valid DEV process/session configuration is available and a permitted test image is supplied, the first bounded call may establish the response structure. Capture the result in protected local storage and expose only a sanitized structural summary. Distinguish HTTP success, job creation, processing completion and verified extraction.

Do not set –confirm-credentials-rotated while replacement remains unconfirmed. Do not make live Symcor or ADIDO calls.

5. Correct the evidence and continue independent work

Describe two submissions for a two-sided cheque as the current profile’s behavior, not a proven provider-wide limit or a twofold increase in total runtime.

Keep the Symcor TLS root cause unresolved. Continue reading the available native Symcor specifications and mapping supported findings to open contract questions without live calls.

Run targeted tests for changed behavior, followed by the appropriate existing regression check. Record the current commit and working-tree status, implemented changes, observed results and exact remaining external dependencies.

All engineering output must remain in English. Use text and filesystem tools only. Continue without another routine planning or approval checkpoint.
