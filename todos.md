Create a minimal browser-extension probe to test SharePoint access through the user’s existing signed-in browser session.

This is a small feasibility test, not product development.

Context:

* The site-title API already works when opened directly in the user’s browser.
* PowerShell with Windows default credentials returned 401.
* VS Code’s default Microsoft client failed to obtain Sites.Read.All with AADSTS65002.
* Do not repeat those authentication tests.

Create a separate folder named sharepoint-browser-probe beside the existing probe. Preserve all existing projects and results. Use a few small files, plain JavaScript, and Manifest V3 for Chrome/Edge. No dependencies or build framework.

Implement one popup button: “Test SharePoint access”.

Use only the activeTab and scripting permissions. On a user click:

1. Verify that the active tab is on https://myteam.td.com and belongs to /sites/tr-usts-arc or a path beneath it. Otherwise show an instruction to open the correct site and send no request.
2. Use chrome.scripting.executeScript in the top frame’s isolated content-script world. Execute the fetch inside that tab, not from the popup or background service worker.
3. Make exactly one GET to:
    https://myteam.td.com/sites/tr-usts-arc/_api/web/title
    Use credentials: “same-origin”, mode: “same-origin”, redirect: “error”, cache: “no-store”, and a 15-second timeout. Request JSON and cap response reading at 64 KiB.
    Let the browser attach its existing session cookies automatically. Do not read, extract, copy, or manually set cookies or Authorization headers.
4. Parse the response and check for actual nonempty SharePoint site-title metadata. HTTP 200 with a login page is not success. Do not substitute document.title or previously displayed page text for the API response.
5. Return only a small result object to the popup:
    * HTTP status, when available
    * Content type
    * Valid site-title metadata: yes/no
    * A brief safe failure reason, if needed

Do not display or retain the actual site title, response body, tokens, cookies, or authentication URLs.

Keep the test bounded:

* No Microsoft Graph, App Registration, external MCP, native messaging, localhost server, or VS Code integration yet.
* No file downloads, searches, broad site permissions, automatic retries, or new test framework.
* Use text/filesystem/accessibility tools only. Keep all code, instructions, and responses in English.

Prepare the files and perform a lightweight manifest/JavaScript syntax check. Load and run once using the normal permitted browser extension UI if available. If manual installation is necessary, give me the exact folder path and short Load unpacked → open SharePoint → click test instructions.

Do not bypass organization restrictions. If loading unpacked extensions is blocked, report that specific blocker and preserve the ready-to-test files. Do not claim the live test ran.

Finish with a short result or the exact remaining manual action. Success establishes browser-extension access to this metadata endpoint only; connection to VS Code remains untested.
