The 401 result is useful, but the SharePoint Online classification is not established. Error 917656 is not exclusive to SharePoint Online.

Repeat the same PowerShell GET once, adding:
X-FORMS_BASED_AUTH_ACCEPTED: f

Keep the same URL, current Windows default credentials, disabled redirects, normal TLS validation, 15-second timeout, and response-size limit.

Report only:
- HTTP status.
- Whether valid site-title metadata was returned, without printing its value.
- Authentication scheme names, if supplied.
- Any redirect hostname/path, excluding query strings.

Do not log credentials, cookies, or authentication challenge values. Do not infer the hosting platform from this error. No extension work, additional tests, or framework changes. Stop after reporting.
