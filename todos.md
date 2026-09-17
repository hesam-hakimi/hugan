Continue from the committed TD logger integration with td-python-dytp-logger==1.0.2 and the reported 14 focused / 184 full-suite passing tests.

The next task is to resolve DEV configuration availability and perform one logging smoke test when ready.

1. Use the existing configuration inspection helpers to check the actual CLUE startup path and Python environment.

For these settings, report only PRESENT, MISSING or BLANK, plus their configuration source:
DYNATRACE_URL
DYNATRACE_API_KEY
TD_DT_LOG_SOURCE
WEBSITE_SITE_NAME
MALCODE
COMPUTERNAME

Check the explicit .env location, inherited process environment, intended precedence and whether configuration is loaded before the TD handler reads or caches it. Do not print secret values or dump the environment.

2. Inspect how the installed TD package uses these settings.

In particular, check whether COMPUTERNAME is available in the actual Windows process but missed by the current preflight. Determine how WEBSITE_SITE_NAME maps to application identity for this local/on-prem application.

Use verified project references for the DEV destination and application attribution. Do not substitute sample values or invent a MALCODE. If a real value is unavailable, identify the exact external input needed.

3. Investigate the visible PowerShell exit-code-1 notification using the corresponding command and sanitized error output. Retry only the affected step if appropriate. If the evidence is unavailable, record that uncertainty.
4. Once the real DEV configuration is available, send one harmless event with a unique marker through the integrated CLUE logger. Check ingestion acceptance and verify destination visibility separately.

Reuse existing test evidence. If configuration code needs fixing, run the relevant targeted tests. Update the handoff with the actual result and remaining dependencies.

Keep all development output in English.
