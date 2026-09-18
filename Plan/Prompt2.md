After the current implementation step finishes, inspect the active code and report the exact retry and recovery behavior for Symcor and Tungsten. This is a focused read-only verification.

For each API operation, report:

* Whether retries are actually wired into the execution path.
* Which errors are retryable, terminal, or treated as UNKNOWN_OUTCOME.
* Maximum attempts, clearly distinguishing total attempts from additional retries.
* Delay/backoff, timeout, and the configuration names controlling them.
* Which committed checkpoint is reused when execution resumes.
* Whether a persisted FAILED item is retried on a normal rerun. If not, provide the existing recovery command or identify the missing capability.
* How an ambiguous Tungsten submission is resolved without blindly submitting another job.

Cite the relevant code paths and existing test evidence. Report gaps as gaps; do not infer behavior from a helper function that is not called.

Also state whether the owner’s latest requirement—keeping an output row for every returned cheque, including failed items—has now been implemented.

Do not modify code, call either provider, or run the full test suite for this inspection. Keep the response in English.
