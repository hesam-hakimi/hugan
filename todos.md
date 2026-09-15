The basic Microsoft session succeeded, but the SharePoint scope request returned no session. The report does not identify why.

Inspect only the existing authentication and Extension Host logs for that attempt. Also inspect the probe’s error handler to determine whether it discarded or replaced the original error.

Return:

* The sanitized original error code and a brief explanation, if recoverable.
* Whether the evidence identifies user cancellation, a consent/client restriction, or another failure.
* If the cause cannot be recovered, explicitly say “Cause unknown.”

Do not rerun authentication, modify code, change Client IDs, or start extension development. Do not output tokens, cookies, complete session objects, account details, or raw authentication URLs.

Keep the response in English and under 150 words. Stop after reporting.
