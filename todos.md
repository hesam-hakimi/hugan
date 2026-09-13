# Expose trusted preview and writer\-validation evidence

STATUS: PREPARED\_FOR\_OWNER\_SUBMISSION; not executed by ChatGPT\.
TASK\_ID: ETL\-0913\-TRUSTED\-WRITE\-EVIDENCE\-REPAIR01\.
PREDECESSOR: ETL\-0913\-0153\-ORCHESTRATOR\-EVIDENCE\-BINDING01, closed with item B satisfied and item E partial\.
TYPE: Bounded product\-source observability repair, permanent affected tests and independent review\.
PRODUCT\_WRITE\_AUTHORIZATION\_BUDGET: 0\.

Continue in the Windows engineering workspace\. This prompt is self\-contained for a new GitHub Copilot chat if needed\. Keep all engineering replies, code, tests and documents English\. Use text, DOM, files and existing diagnostics only; no screenshots, video, OCR or vision\. This is a new source\-repair task, not a replay of the completed installed qualification\.

## 1\. Authenticate the exact starting point

Resolve the predecessor’s existing claim and evidence directory under C:\\docs by its exact task\-ID prefix above\. Read its final report, result, named Verifier verdict and referenced evidence inventory\. Read applicable repository instructions\. Resolve the worktree and current full source hashes from those records; do not assume HEAD describes dirty or untracked inputs\. Search only the identified task roots and relevant source paths, not all historical campaigns\.

Also retain the parent qualification at:
`C:\docs\ETL-0913-JOBCONFIG-INSTALLED-ORCHESTRATOR-QUALIFY01`\.

Authenticate these reported facts before editing:

- Private 0\.3\.153 remains installed and preserved\. The source worktree package\.json remains 0\.3\.147\. No new version or installation is required for this source task\.
- The predecessor recovered the SAME run’s actual tool arguments/results from the isolated profile’s chatSessions JSON and GitHub\.copilot\-chat/transcripts JSONL\. No additional model request or live run was needed\. Reuse its collector at the recorded `helpers/chat-evidence-collector.js` path\.
- Item B is satisfied: the first writer invocation actually omitted previewId; the product result returned its preview record; the second call supplied that exact previewId with identical content; the product returned that explicit approval was declined\. Preserve this finding and its historical reporting correction\.
- Preview\-to\-continuation binding is enforced by the existing manifest\-checksum guard\. Item E remains partial because standalone validation received 1,145 bytes while the writer received 1,144 bytes, differing by exactly one trailing LF\. Do not erase or relabel this difference\.
- The writer’s internal revalidation diagnostics and the computed manifest/per\-file hashes were not published\. That is the observability gap for this repair; a runtime behavior defect has not been established\.
- Consumer preservation remains 21 unchanged files, job\_conf absent, zero product writes\. Prior source regression results reported 584 passing / 5 failing, all five reproduced in the pre\-fix baseline\. Carry their identities without calling the baseline all\-green\.

Verify ownership release and acquire the normal bounded source claim\. Preserve full preimages/hashes of every touched tracked or untracked file\. Keep unrelated dirty files, earlier reports, consumers, profiles, installed candidates and VSIX files unchanged\. Do not manufacture a missing historical preimage\.

## 2\. Implement the smallest additive evidence contract

Inspect the actual seams named by the predecessor; line numbers are hints, not authority:

- WriteAuthorization\.ts: buildPreviewStoreMarkdown, around line 309\.
- TrustedWriteApprovalStore\.ts: computeManifestChecksum, around line 134, and the stored preview record\.
- EtlActionToolService\.ts: writer internal validation, around line 584, and existing tool\-result serialization\.

Trace their real callers and result types, then extend the existing product result path\. Do not introduce another writer, approval store, planner, MCP tool, validation pipeline or background logging service\.

Expose a small versioned machine\-readable evidence section associated with the real product preview result\. Follow existing result conventions; if the transport is text\-only, use an unambiguous bounded serialized section inside the actual tool result\. Do not rely on model narration to produce or repeat it\. Preserve existing human\-readable markers, previewId return behavior and compatible consumers\. Keep routine user\-facing preview text concise; place technical detail in the existing structured/diagnostic result surface\.

The evidence must identify:

1. The product\-issued previewId and manifest checksum from the trusted record, with the actual algorithm/representation identified\.
2. The manifest’s workspace/destinations and per\-file dispositions, exact proposed byte lengths and content SHA\-256 values\. Reuse the trusted calculation or its shared implementation; do not build a parallel definition of the manifest\. Distinguish proposed bytes from existing\-file state hashes and identify hash encoding\. Do not assert a content hash for a disposition that has no content\.
3. The writer’s ACTUAL internal pre\-write validation outcome, including available errors/warnings and input\-content identities\. Bind the outcome to the files it really validated and the resulting preview\. Mark any file not covered by that validator accurately\. Do not export a fabricated pass or a model summary\.

Use the already\-computed validation result; do not run another validation just to generate evidence\. If safe propagation through existing types is needed, carry the result and input identities through the existing call path\. The metadata must describe the same snapshot used by the trusted record and approval check, without a separate stale cache or an extra product file write\.

Document the two different comparisons explicitly: historical standalone validation \-\> writer input, and writer internal revalidation \-\> trusted preview\. Publishing the latter does not retroactively prove the former\. The old 1,145/1,144\-byte record and partial E verdict remain intact\.

## 3\. Preserve behavior and authority

This change reports existing decisions; it must not change artifact bytes, validation semantics or approval authority\.

- Do not trim, normalize line endings, strip an LF, rewrite serialization or change hash sensitivity merely to make evidence match\. If existing code performs a transformation, report its actual stages and identities without changing it in this task\.
- Preserve the two\-call preview protocol, preview expiry/consumption, workspace/destination/content binding, current\-state checks, containment, job\-config layout policy and final Approve write / Cancel gate\.
- Evidence fields are output metadata, never caller\-supplied authorization\. A supplied or copied checksum must not substitute for the trusted record or explicit approval\. Do not expose additional approval secrets or add self\-referential metadata to the artifact/manifest checksum input\.
- Blocking validation must still prevent preview/approval as required by the existing contract\. Preview and cancellation must not reach RepoWriter\. Unavailable runtime/DBFS compatibility must remain unavailable, not become a validation\-pass claim\.
- No whole\-chat dumps, credentials, new profile logging settings or automatic diagnostic files in the consumer\. Emit only the bounded artifact evidence needed by the existing operation\.

Owner submission authorizes this bounded source/type/result\-contract change, directly affected documentation/tests, task\-owned test outputs and fixes for relevant reviewer findings\. It does not authorize build/package/install, a version bump, a live model run, product Initialize/Upgrade/Repair, an approved consumer write, DBFS publish, deployment, dependency installation or Git mutation\.

## 4\. Add permanent behavioral verification

Use the existing test framework and affected suites\. Exercise the real service/result\-serialization path as well as the trusted store; a formatter test or source\-string grep alone is insufficient\.

Required coverage:

- A successful preview exports the product’s real previewId/checksum, per\-file content identities and the actual internal validation diagnostics\. Independently compute expected UTF\-8 hashes from the fixture bytes and parse the real returned tool result\.
- The exact trailing\-LF case: standalone bytes and writer bytes have distinct identities, while writer revalidation and its preview accurately identify the writer’s bytes\. Preserve both valid business content and the byte difference\.
- Identical continuation content retains the trusted binding\. Adding/removing the LF, changing another byte or changing a bound destination while reusing previewId is rejected by the existing guard\. Exported hashes never override that guard\.
- Blocking validation and missing diagnostics are represented honestly\. Test the actual diagnostics propagation, including nonblocking warnings, rather than inventing status from an empty list\.
- Preview and final Cancel leave the consumer unchanged and do not invoke RepoWriter; use measured inventories and a writer spy, not a hard\-coded zero\-write result\. Do not make every test inherit an always\-pass validator\.
- Existing workspace/expiry/consumption and destination\-state checks still pass in their affected suite\. An UNCHANGED/reused env entry is represented accurately, without suggesting a new write\.

Compile and run in an isolated task\-owned lane\. Reuse the established resources/layout and local dependencies; shared out and \.tsbuildinfo\.test must not be written\. Check free disk space first\. No cache, Temp, fixture or historical\-evidence cleanup is authorized\. Unit\-test fixture writes are permitted only in isolated test locations\.

Run affected suites and directly related regression gates\. Reuse unrelated authenticated results\. If an affected failure is alleged to predate this repair, compare with the preserved preimages in an isolated baseline lane; do not infer that from its name or waive a required gate\. Fix new regressions within scope without weakening tests to conceal them\.

## 5\. Review, close and prepare the installed follow\-up

Run one independent read\-only reviewer on the actual final diff, the additive result contract, byte provenance, unchanged authority and behavioral evidence\. Permit its own verdict file in task evidence\. Use a generic reviewer with honest provenance if the named Verifier is unavailable\. Resolve relevant findings and have the final corrective delta checked; do not promote an older verdict to cover later edits\.

Deliver one concise report/result with full changed\-file pins, test outcomes, reviewer verdict, remaining limits, and the exact way the existing collector can obtain the new evidence from real tool results\. A small read\-only extractor adaptation is allowed only if required by the additive output; keep it in the existing collector with a focused offline check, not another harness\.

Claim source repair verified only to the extent established\. Do not close historical installed item E or claim installed qualification from source tests\. Preserve 0\.3\.153 as historical evidence\. Because product bytes changed, prepare but do not execute the smallest next task to build one distinguishable candidate, qualify its package, and run the genuine consumer ETL Orchestrator through preview and final Cancel with the new evidence\. Select the next unused private version only when that build is authorized; do not assume \.154 is available\.

The future brief must state which validation stage is evidenced and retain any unresolved standalone\-validation byte requirement\. Keep the real user route as natural language through ETL Orchestrator, not manual /create or /write\. No approved\-write or release task is launched here\.

Release source ownership with final pins\. Carry existing runtime/DBFS, Windows case, Framework\-documentation, HOCON/STTM, historical preimage and acceptance limits\. The quarantine is valid only through 2026\-09\-13 inclusive UTC, with no automatic extension; identify any actual dependency on it using the current date\. No RELEASE\_ACCEPTANCE, FULL\_PRODUCT\_OR\_ASKTD\_READINESS or demo delivery claim\.

Complete this source task without repeated routine permission requests\. If the gap cannot be repaired within these existing seams without a material behavior/authority change, return the concrete design conflict and smallest reviewable alternative; do not silently expand scope\.
