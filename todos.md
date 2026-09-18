Make Tungsten TLS verification configurable and complete the DEV smoke test

Continue the active CLUE Python project in the current development workspace. All responses, code, tests and handoff updates must be in English. Use text, filesystem and structured logs; no screenshots, OCR or vision. This brief authorizes the bounded implementation and local DEV test below. Do not restart the project or reopen unrelated architecture work.

Context and authority

The owner reports that the development server has the required certificate, while the laptop does not. The same Postman request returned an application response after SSL certificate verification was disabled. The visible response included JobIdentity and DocumentId, with empty OCR-related arrays in the visible section. This supports a laptop/Postman TLS-verification issue, not proof of successful field extraction or the precise certificate-chain cause.

The owner explicitly authorizes temporarily disabling server-certificate verification for the laptop’s Tungsten DEV smoke test. Preserve verification by default and on the development server. This changes certificate verification, not HTTPS encryption, API authentication or client-certificate requirements.

Implement the smallest coherent change

Read the current handoff and actual configuration loader, Tungsten HTTP client and smoke entrypoint. Use the active checkout and its existing HTTP library. Preserve unrelated changes. Reuse an equivalent existing configuration setting if present; otherwise introduce:

```dotenv
CLUE_TUNGSTEN_TLS_VERIFY=true
CLUE_TUNGSTEN_CA_BUNDLE=
```

• TLS verification defaults to true when unset. Parse explicit true/false values correctly; do not use bool(“false”). Reject invalid values with a clear configuration error.
• With verification enabled and no explicit CA bundle, preserve the existing verified transport and trust configuration, including relevant environment/proxy handling.
• With verification enabled and a CA bundle configured, verify using that real PEM file. Validate the path and report an actionable error for missing/invalid bundles. Never silently fall back to unverified transport.
• With verification explicitly false, disable verification only for Tungsten’s local DEV smoke connection to the already configured DEV endpoint. Use existing environment/endpoint checks; reject this option for production. Do not introduce an unrelated configuration framework.
• Scope the setting to the Tungsten client. Do not disable TLS verification globally or affect Symcor, other clients or system settings. Do not automatically retry a certificate failure with verification disabled.
• If a CA bundle is also configured while verification is false, clearly report that it is not being used. Emit a concise warning that the test is unverified TLS; do not suppress warnings globally.
• Keep timeouts, proxy settings, authentication, payload semantics and existing client-certificate settings intact. For Requests, map to its verify argument; for another library use its equivalent supported client configuration. Do not change libraries just for this option.

Update the actual local, untracked .env used by the laptop test to:

```dotenv
CLUE_TUNGSTEN_TLS_VERIFY=false
CLUE_TUNGSTEN_CA_BUNDLE=
```

Preserve all existing keys and settings without printing their values. Do not create or modify a guessed .env path. Keep shared examples/defaults at true and leave server configuration unchanged. Document that the server’s Python process must actually trust the installed CA; certificate presence on the machine alone does not establish that. Document the optional CA-bundle path for the server without inventing one.

Validate and execute

Use focused existing tests to check default verification, explicit false, explicit CA-bundle use, invalid boolean handling and rejection of production bypass. Assert the effective transport options, not just parsed strings. Run relevant repository-required checks; no unrelated full regression or architecture audit.

Recover the successful Postman request from available collection/export/source files. Compare the resolved endpoint, headers, Config, sessionId and image payload with the Python client. Do not assume the earlier placeholder values are the values that worked. Do not invent configuration values or weaken missing-input validation to force a request through. Preserve the owner’s previously recorded credential-rotation deferral; do not claim credentials were rotated.

Once the actual required values are available, run one controlled live Tungsten DEV smoke request using the existing sample image and normal client, with this explicit local TLS setting. Reuse the existing command and response parser. Disable automatic retries for this job-creating POST if they could duplicate submission. On an uncertain timeout, retain the evidence and determine the submission outcome before any repeat. Do not send a batch or call Symcor as part of this task.

Save the actual HTTP status and complete response through the project’s existing local evidence mechanism, protecting credentials and image/customer data from console output and shared reports. Distinguish transport success, application acceptance, job/document creation and actual OCR field extraction. Empty extraction arrays are not a completed OCR success. If an Excel output is produced, accurately label missing fields and extraction status rather than inventing values.

If essential Config/sessionId values remain unavailable, complete the implementation and focused checks, then identify the exact missing input and ready-to-run command. Do not ask again for files or information already present locally.

Handoff

Update the current handoff with changed files, tests, effective TLS mode, actual smoke result, output paths and the exact command used. State that the laptop result with verification disabled does not qualify verified TLS on the development server. Explain restoration: set CLUE_TUNGSTEN_TLS_VERIFY=true and configure the correct CA bundle if required.

Do not expose or commit .env secrets, replace system certificates, change server configuration, rotate credentials, deploy or publish. Keep the task limited to this configuration feature and one DEV smoke result. Rebuild only if the actual changed code requires it.

Reference for Requests TLS verification and CA bundles:
https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification
