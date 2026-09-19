Investigate whether Symcor can be called successfully from this Windows laptop for the CLUE project.

All responses, scripts, reports and documentation must be in English. Use files, source code, command output and structured logs. Do not use screenshots, browser automation, OCR or vision.

This authorizes a focused local investigation and the minimum live DEV calls needed to verify authentication, search and image retrieval. Proceed within this scope without asking again for routine file reads, diagnostic commands or the stated DEV calls.

1. Establish the current workspace and execution environment

Application repository: C:\repos\fcrm_clue
Expected working branch: feature/clue-durable-core
Reference material: C:\repos\FCRM
Current handoff: C:\repos\fcrm_clue\docs\handoff\clue

Verify the actual checkout, revision and working-tree state. Preserve current work; do not reset, switch branches or interrupt an active mutation. Reuse the current handoff and inspect only relevant code and interface artifacts.

Confirm where commands actually execute: the user’s Windows laptop, WSL, a remote VS Code host, a container or another machine. Record the execution environment, interpreter and identity context without exposing sensitive identifiers. Results from a remote environment must not be described as laptop results. If Windows execution is available, run the diagnostic through the laptop’s intended runtime.

If the actual laptop is inaccessible, complete the artifact/configuration inspection available to you, prepare exact runnable commands for that laptop, and clearly identify which checks remain unexecuted.

2. Recover the actual Symcor connection contract

Inspect the existing Java sample, WSDL/XSD, Archive Web Service specification, current Python adapter, configuration loader and existing diagnostic commands.

Resolve the effective DEV endpoint, gateway/proxy path, authentication mechanism, certificate settings and request construction through the project’s existing configuration precedence. Locate the actual .env files used by that loader, including reference configuration if supported. Never assume a guessed .env path is active.

Determine:

* Which endpoint and native operations implement search and image retrieval.
* Whether authentication requires a token, session, credentials, client certificate or another documented mechanism.
* Which required settings are present or missing, without revealing values.
* Which configuration is actually consumed by the active client.

Historical documents mention PingFed ClientCredentials. Confirm its applicability from the current artifacts; do not assume provisioning or token acceptance.

Use existing local information before requesting missing inputs. Do not invent credentials, request fields or sample identifiers. A missing saved response does not prevent a first live test.

Historical context:

* Tungsten’s successful Postman call does not establish Symcor connectivity.
* Earlier SKIPPED_NO_URL results mean no configured live call occurred; they do not prove a network restriction.
* Earlier reports described unresolved Symcor TLS issues, but their status must be checked against current evidence.
* The documented retrieval path is search followed by getDocs using returned identifiers. Confirm the actual operation names and sequence from the native contract.

3. Diagnose the connection using the intended client path

Use the current Symcor client and its configured proxy/trust behavior. Establish evidence for endpoint resolution, network connectivity, TLS and authentication. A successful higher-level operation can establish earlier layers; avoid redundant probes.

For any failure, identify the earliest failed stage and report the actual sanitized error. Distinguish missing configuration, name resolution, connection timeout/refusal, proxy failure, certificate trust/hostname failure, client-authentication failure and API authorization failure where evidence permits.

Do not infer an unavailable API from a failed direct TCP probe when the configured client uses a proxy. Do not assume that browser access, ping or a token from another service establishes API access.

Keep certificate verification enabled. The earlier CLUE_TUNGSTEN_TLS_VERIFY setting is specific to Tungsten and must not be applied to Symcor. Do not change global TLS settings, import certificates into system stores, disable verification or alter server/network configuration.

If certificate validation fails, inspect the available trust configuration and error details. Explain whether the evidence supports a trust-chain issue, hostname issue, a documented client-certificate requirement or an unresolved cause. An installed certificate alone does not prove the Python or Java runtime trusts it; a generic certificate error does not establish mTLS.

4. Run the smallest useful live DEV retrieval

Once the required connection settings and a suitable existing DEV sample are available, execute one bounded search using the normal Symcor client. Use a known small test case and contract-supported limits. Do not send a batch or an unrestricted archive query.

Record the requested native operation, HTTP result, SOAP/application outcome, returned count and any limit/continuation indicators. Interpret empty hit lists according to the native contract; count-only or truncated responses must not be reported as genuine zero matches.

Confirm the response comes from the intended Symcor DEV operation; a proxy page, login page, redirect or unrelated HTTP 200 is insufficient. A SOAP fault alone does not establish a successful search. A valid zero-result response verifies search execution but leaves image retrieval unverified.

If search returns documents, use the exact returned identity, including required associated metadata, to retrieve one representative cheque through getDocs or the documented equivalent. If the contract returns images directly, inspect those bytes without making an unnecessary extra request.

Verify image retrieval programmatically using the response metadata, decoded byte count and actual image format. Record available front/back sides only where native metadata establishes them. Do not use OCR or make an image-to-account association from extracted names.

Preserve the sample’s search-to-document-to-image traceability. Do not invent or substitute a document ID to force the test to succeed. If no suitable result is available, report search success and the specific prerequisite for testing image retrieval.

Use finite timeouts and record actual attempts. Avoid uncontrolled retries. After an authentication or certificate failure, diagnose it before repeating the request. Any extra DEV call must resolve a concrete issue found in the preceding attempt.

5. Keep the investigation isolated and reusable

Reuse existing diagnostics and saved evidence. If no command can isolate Symcor, create only a small diagnostic runner in the project’s existing diagnostics area and use the existing adapter. Do not replace the integration with a newly invented client.

Do not modify application behavior or .env files to hide a failure. Report discovered implementation defects separately. Preserve active processing state and output files.

Keep credentials, tokens, private-key material, account numbers and cheque payloads out of chat and shared reports. Store necessary response captures through the existing protected local evidence mechanism and report their paths; use the smallest required data.

Do not call Tungsten or ADIDO/TIBCO, run the full pipeline or a broad regression suite, change VMC2/AutoSys/Dynatrace configuration, rotate credentials, push or deploy. This is a Symcor laptop diagnostic.

6. Deliver a concrete result

Produce a concise English report in the existing diagnostics/handoff location. Avoid concurrent edits to a handoff another session is modifying; use a separate dated report when necessary.

Lead with one of these evidence-based outcomes:

* Live search and image retrieval verified from the Windows laptop.
* Live search verified; image retrieval remains unverified.
* Live attempt failed at a specified stage.
* Live execution blocked by a specifically identified missing prerequisite.

Include:

* Actual execution environment, source revision, runtime and command used.
* Relevant code/configuration locations and effective TLS verification mode.
* A compact table for configuration, network path, TLS, authentication, search and image retrieval: result, evidence and remaining gap.
* Actual HTTP/SOAP outcomes, native operation names, attempt counts and exit codes where available.
* Retrieved document/image counts and evidence paths, with sensitive values excluded.
* Files created or changed.
* For each unresolved issue, the smallest concrete next action and the responsible role where known.

Distinguish live evidence, saved-response replay and static inspection. Do not claim VMC2-only access without supporting configuration or network-policy evidence.

Complete every independent check available in this session. Return the actual findings and exact commands, rather than another general investigation plan.
