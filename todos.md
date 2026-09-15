Run a small authentication-only test using VS Code’s built-in Microsoft authentication provider.

Goal: determine whether the default VS Code client can return an authentication session for our organizational account and then for the requested SharePoint read scope. Do not resume full extension development.

Use the existing sharepoint-auth-probe project. If necessary, add one minimal command named “SharePoint Auth Probe: Test Microsoft Sign-In” and run it in the real local Windows Extension Development Host. These APIs cannot be tested from standalone Node.js or PowerShell.

This command must run independently of the previous site-hostname filter and site/library/file input boxes. Preserve the previous probe results.

Perform only these two checks, sequentially:

1. Basic Microsoft session
    Call vscode.authentication.getSession with:
    * Provider: “microsoft”
    * Scopes: [“https://graph.microsoft.com/User.Read”]
    * Options: { createIfNone: true }
    Let me complete any account selection, sign-in, or consent through VS Code’s supported interface. An existing usable session is acceptable; do not force reauthentication just to open a browser.
2. SharePoint scope request
    Only if step 1 returns a session, call getSession again with:
    * Provider: “microsoft”
    * Scopes: [“https://graph.microsoft.com/User.Read”, “https://graph.microsoft.com/Sites.Read.All”]
    * Options: { createIfNone: true, account: basicSession.account }
    Check that the returned session belongs to the same account and record the provider-reported scopes. Do not print account identifiers.

Use the built-in default client registration. Do not set VSCODE_CLIENT_ID, inject a custom client-ID scope, borrow another application’s Client ID, or register an application. If an override already exists, report it without silently changing the environment.

Keep this simple:

* No external MCP, new dependencies, test framework, or unrelated test reruns.
* No Graph or SharePoint data requests, file selection, downloads, or cookie extraction.
* Never print or persist tokens, cookies, complete session objects, or credentials.
* Use text, terminal, and accessibility tools only. All code and responses must be English.
* If user interaction is pending, tell me the exact window/action required and keep that single attempt pending. Do not open duplicate attempts.
* If a step is rejected or cancelled, report it and stop. For errors, include only the sanitized error code and relevant explanation. Do not change organization policies or switch authentication methods.

Return a short table with the result of each check, any observed sign-in interaction, and any error code. Keep unexecuted or pending steps clearly identified.

A returned session confirms session acquisition for the reported scopes only. Access to our specific SharePoint site remains untested.
