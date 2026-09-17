Continue the current CLUE implementation in C:\repos\fcrm_clue on feature/clue-durable-core.

Use the reported checkpoint 0009609 and 66 passing offline tests as context. Inspect the actual current HEAD and working tree, preserve subsequent changes, and continue from the existing implementation. Keep all responses, code, tests, and documentation in English. Use text and filesystem tools only.

Complete this focused follow-up within the existing local-work scope.

1. Verify recovery between the two page submissions

Inspect existing tests before adding coverage. Verify this sequence through the durable application and real adapter with an injected fake transport:

* The front-page response is received and durably committed.
* The back-page request fails before submission, or execution stops before it is sent.
* A fresh application instance resumes only the back page and reuses the committed front-page result.

Also verify an ambiguous back-page outcome: retain the front-page result, hold the unresolved back-page attempt, and do not blindly resubmit either page. Preserve document/page identity and provider references. Extend existing fixtures only where this behavior is not already covered.

2. Enforce the boundary between synthetic identifiers and live requests

The provisional internal locator used for ITEMSEQUENCENUM must remain confined to synthetic execution. A provenance label alone is insufficient.

Verify that live core execution refuses before sending when the required ISN mapping is unresolved. An isolated DEV component smoke may use an explicitly supplied, provider-accepted test identifier independently of the unresolved Symcor mapping.

Keep provisional parsing results clearly identified in test artifacts. They must not be published as validated business extraction.

3. Tighten the evidence and capture handling

Describe the credential scan as finding no matches for the known exposed keys in the scanned current files. Treat any unidentified token as unclassified; do not print its value or infer that it is non-sensitive from a different fingerprint.

Before saving a real response on Windows, verify the capture directory’s actual access permissions and that it is outside synced/shared locations. Do not treat chmod 0600 or gitignore as proof of access control.

Treat the first successful response as an observed response sample, not verification of every success and error variant.

4. Continue only the remaining targeted Symcor document review

Check the existing native sources for operator-code mappings and AvailableSegments/docsFetchLimit behavior. Record exact source references and unresolved contradictions. If the required information is absent, report that finding and preserve the unresolved configuration rather than guessing or repeatedly searching the same material.

Preserve the corrected findings about Amount and the conflicting timeStamp specification/examples.

5. Prepare the isolated Tungsten DEV smoke

Keep C:\repos\FCRM.env supported through the explicit –env-file option and existing aliases.

Credential rotation remains unconfirmed. Continue the offline work now. Once the owner confirms rotation and supplies valid process/session settings and an approved test image with permitted identifiers, use the existing CLI for one bounded single-page DEV request within the previously authorized scope.

Report transport, provider/job outcome, and extraction interpretation separately. Keep response values and credentials out of chat and general logs. A missing saved response is not itself a prerequisite to this first call.

Run the relevant checks and the existing regression suite once after changes. Finish with the actual commit/tree status, evidence for the two recovery/identifier checks, and the precise external inputs still missing. Continue routine authorized local work without asking for repeated approval.
