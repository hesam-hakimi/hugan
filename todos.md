Run a bounded SharePoint authentication feasibility probe in the local Windows VS Code environment.

Objective

Determine whether a VS Code extension can use the built-in Microsoft authentication provider, with its DEFAULT client registration, to access an owner-selected SharePoint Online site and read one harmless test file.

We have no dedicated Microsoft Entra App Registration or Client ID for this extension. External MCP servers are unavailable. This task evaluates the existing VS Code authentication route; it does not implement the full SharePoint connector.

All communication, code, comments, and reports must be in English.

1. Preserve the current environment

* Read applicable AGENTS.md instructions.
* Inspect the installed VS Code version, extension host location, and availability of the built-in Microsoft authentication provider.
* Work in a separate local probe folder outside the active product checkout. Preserve ongoing ETL Copilot work and uncommitted changes.
* Do not replace the installed product VSIX, change shared authentication settings, clear existing sessions, or modify production extension code.
* Use text, filesystem, DOM, accessibility, and structured logs. No screenshots, video, OCR, or vision.
* Run authentication in the local Windows VS Code extension host, not GitHub Actions, a remote agent, WSL, or a container.

2. Keep the authentication experiment exact

Use the supported VS Code API:

vscode.authentication.getSession(‘microsoft’, requestedScopes, options)

Use the provider’s default client registration.

Do not:

* Set a VSCODE_CLIENT_ID override.
* Register an Entra application or create credentials.
* Substitute an Azure CLI, Graph Explorer, Office, or another application’s Client ID.
* Use external MCP services, application permissions, or a service account.
* Extract browser cookies, reuse another application’s token cache, or request manually pasted tokens/passwords.
* Change tenant consent, Conditional Access, proxy, TLS, or device compliance policies.

The user must choose the intended organizational account. Keep subsequent stages bound to that account. Do not silently switch accounts or tenants.

Use the provider’s normal interactive sign-in experience when necessary. The owner completes sign-in and MFA. Reuse an existing suitable session through the supported API when possible.

3. Prepare a minimal executable probe

Create a small local extension with a command named:

SharePoint Auth Probe: Run

Use an Extension Development Host with the installed VS Code version and applicable organizational policies. Prefer existing tools and dependencies.

The command must perform the stages below and produce a sanitized report. Keep tokens inside the running extension. Do not expose credentials through a language-model tool.

Compile/load the probe and execute everything your available tools support. If invoking the command or completing sign-in requires the owner, finish the harness first, then provide the exact launch or Command Palette action needed.

Do not claim a live test succeeded based on compilation, mocks, or source inspection.

4. Identify one bounded target

Ask once for:

* The SharePoint site URL.
* The document library and path of one existing, non-sensitive, small text file the owner can already read.

Collect these through local input or an explicitly supplied test configuration. Do not search unrelated folders, browser history, or the tenant for a target.

Confirm whether the target is SharePoint Online. If it is SharePoint Server on premises, mark this Graph-specific probe NOT_APPLICABLE and report that the authentication design needs to match that server.

Do not create/upload a SharePoint file or redeem a sharing link to acquire access. Missing target information must be recorded as pending, not guessed.

5. Execute and report each stage separately

Stage A — Basic Microsoft authentication control

* Request the delegated scope https://graph.microsoft.com/User.Read through the default provider.
* Call GET https://graph.microsoft.com/v1.0/me?$select=id.
* Report only whether the call succeeded and whether the expected account was selected.
* This stage proves basic Microsoft Graph access, not SharePoint access.

Stage B — SharePoint permission acquisition

* For the site-by-path test, request https://graph.microsoft.com/Sites.Read.All through the SAME default provider and selected account.
* Explain that this is a delegated read scope that can cover sites the user can access; the probe itself will only access the selected test target.
* Do not request write scopes or bundle unrelated permissions.
* If Entra requires administrator consent, blocks the application, or rejects first-party preauthorization, record the result and stop dependent stages.
* An error such as AADSTS65002 is evidence about the default client authorization route. Do not repeatedly retry it or switch Client IDs.

Stage C — Actual SharePoint site access

* Use the acquired SharePoint session to resolve only the supplied site:
    GET /v1.0/sites/{hostname}:/{server-relative-site-path}
* Use correct URL encoding and minimal selected response fields.
* Resolve the specified library/file within that site using documented Graph endpoints. Keep metadata enumeration small and bounded.
* Do not enumerate all tenant sites or unrelated content.

Stage D — Actual file read

* Retrieve metadata and content for the selected existing test file.
* Read at most 64 KiB and stop reading at the limit, even if a server ignores a Range request.
* Report status, bytes read, and optional matching of an owner-supplied harmless marker. Do not include the document’s text in chat or reports.
* Handle Graph’s preauthenticated download redirect correctly: never forward the Graph bearer token to another host and never log the signed download URL.
* Respect organizational network restrictions.

Stage E — Bounded search

* If the preceding stages succeed, perform one Microsoft Graph search for the selected test file, restricted to its site or folder, with at most five results.
* POST /v1.0/search/query is allowed solely for this read-only search.
* Escape the query correctly and retain the fixed target restriction.
* Report API success separately from finding the expected file. Empty results do not prove an authentication failure or successful content discovery.

Stage F — Session reuse

* Reacquire the same SharePoint session silently through the supported VS Code API and repeat one small metadata request.
* Report whether another interactive sign-in was required.
* Do not force expiry or sign out the owner’s account. This stage does not prove refresh-token or revocation behavior.

An access-denied check is optional only if the owner explicitly supplies a known inaccessible test resource. Do not guess private resources. A random 404 is not proof of authorization enforcement.

6. Keep evidence safe and conclusions precise

* Never print/store access tokens, refresh tokens, authorization codes, cookies, Authorization headers, signed URLs, complete session objects, or raw document content.
* Do not decode Graph access tokens to infer permissions. API outcomes are the evidence.
* Record requested scopes and provider-reported session scopes separately; do not label either as independently verified token permissions.
* Record stage, UTC time, outcome, HTTP status, sanitized Graph/AADSTS error code, and correlation/request ID when available.
* Redact account identifiers and sensitive target details in the shareable report.
* Distinguish observed errors from inferred causes. A 403 alone does not establish whether the cause is consent, user access, or policy.
* Stop repeat attempts for persistent authentication/authorization errors. Do not run the full ETL regression suite or rebuild unrelated packages.

7. Deliver the result

Create these files in the isolated probe folder:

* README.md with exact run instructions.
* AUTH_PROBE_RESULT.md.
* AUTH_PROBE_RESULT.json.
* The minimal probe source.

Return:

* Probe folder and VS Code version.
* Whether live execution occurred.
* Confirmation that the default Microsoft provider registration was used without a Client ID override.
* A compact stage table: PASS, FAIL, BLOCKED, NOT_RUN, or NOT_APPLICABLE.
* Sanitized evidence for any blocker.
* One verdict:
    PASS — The default identity route read the selected SharePoint file.
    PARTIAL — Some stages succeeded, but the end-to-end file read was not proven.
    BLOCKED — An observed authentication, authorization, policy, or network blocker prevented progress.
    NOT_RUN — Live execution still requires an identified owner action.
    NOT_APPLICABLE — The target is not SharePoint Online.

Report search and session-reuse results separately from the main verdict. A PASS establishes feasibility only for this tested account, target, environment, and time.

Finish with one evidence-based next step. If blocked, identify the missing prerequisite without changing organizational controls. Do not claim that a SharePoint connector is implemented.

Official references:

* VS Code Authentication API
* Get SharePoint site by path
* List document libraries
* Download file content
* Microsoft Graph search

Proceed with preparation and all executable steps now. Request owner interaction only when sign-in, target selection, or an unavailable UI action actually requires it.
