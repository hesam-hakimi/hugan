# Repair reused\-env authority and expiry during write approval

STATUS: OWNER\_AUTHORIZED\_FOR\_SUBMISSION; not executed by ChatGPT\.
TASK\_ID: ETL\-0914\-ENV\-REUSE\-AND\-APPROVAL\-EXPIRY\-REPAIR01\.
PREDECESSOR: ETL\-0914\-INSTALLED\-0154\-ORCHESTRATOR\-APPROVED\-WRITE01, closed with approval spent and no write\.
SCOPE: Two bounded product\-source corrections, affected permanent tests and focused independent review\.
PRODUCT\_WRITE\_AUTHORIZATION\_BUDGET: 0\. The predecessor’s single approval remains spent and non\-retryable\.

Continue in the Windows engineering workspace; this prompt is self\-contained for a fresh Copilot chat if needed\. All engineering replies, prompts, code, tests and documents must be English\. Use text, DOM, files and existing diagnostics only; no screenshots, video, OCR or vision\. Complete this authorized source task without repeated routine permission requests\.

## 1\. Restore the actual failure and preserve its evidence

Resolve the predecessor’s claim/evidence directory under C:\\docs using its exact task\-ID prefix\. Read its final report\.md, result\.json, pins\.json, reviewer/review\.md, approval ledger and directly referenced observations\. Follow references to the final \.154 source/installation identities and the trusted\-write\-evidence source repair\. Read applicable repository instructions\. Search within those identified roots and relevant source paths, not all historical campaigns\.

Authenticate the findings before editing:

- Installed 0\.3\.154 reached a genuine trusted preview through the natural\-language consumer ETL Orchestrator\. It proposed one CREATE under job\_conf/conf/ERUS9/ plus an UNCHANGED env reference\. Writer internal validation reported zero errors / three warnings / seven stages\.
- The one Approve write action was dispatched and the dialog accepted the answer\. The store then refused to record approval\. The roughly ten\-minute preview lifetime had elapsed while the modal was pending\. The product returned a combined already\-used/concurrently\-approved/expired message without identifying the actual reason\.
- requestWriteAuthorization checks expiry before opening the dialog and calls store\.approve afterward\. Confirm the actual expiry anchor, comparison and store/consume behavior from source\. Preserve the report’s timing range; do not manufacture a more precise historical timestamp or stronger click/fsync proof\.
- Reused env content supplied by the model differed from the actual file: outer HOCON braces were removed and a destination\.storage\.account value changed\. This is a semantic divergence as well as a byte difference\. The env file itself stayed unchanged because the reused reference was skipped by RepoWriter\.writeArtifacts, but validation used the divergent input\.
- The consumer remained at 21 files, target absent, with no partial/temp outputs\. The prior budget is spent\. Preserve the consumer and all original records exactly as left; no retry, rollback, cleanup or compensating write\.

Acquire the normal source claim after verifying ownership release\. If this task is already active, resume its existing claim\. Preserve full current preimages/hashes for every touched tracked or untracked file and all unrelated dirty state\. Installed \.153/\.154, profiles, VSIX files, historical tests and reports remain unchanged\.

## 2\. Make the existing env file authoritative for reuse

Trace the existing reuse flow through EtlActionToolService, its validator, manifest builder, trusted preview/store and final writer\. Use those existing seams; do not add a second configuration resolver or approval pipeline\.

Implement this rule when the request declares an existing env is being reused:

- Resolve the declared env path using the existing explicit\-workspace and containment rules\. Read the actual workspace file and use that snapshot as the env input to validation and planning of the guarded write\. Missing/unreadable/out\-of\-scope files must fail clearly before approval; never fall back to model\-supplied env text\.
- Model\-supplied env text is non\-authoritative in this mode\. If supplied text differs, emit an explicit bounded diagnostic that the existing file is being reused and supplied changes were not applied\. Do not merge the model’s storage account or other values into the effective config\. Do not rewrite the file to fit the model\. Preserve the semantics of genuinely new or separately authorized env\-write modes\.
- Preserve original disk bytes and the exact text actually given to the validator\. Do not add trim/newline normalization as a shortcut\. If existing decoding/parsing transforms representation, identify those stages honestly rather than equating their hashes\.
- Bind the reused env dependency’s canonical path and actual content fingerprint to the trusted preview\. Carry that snapshot through the existing store/manifest contract using authoritative product state, never a caller\-provided hash\.
- Recheck the bound dependency on the preview\-bearing continuation and at the existing last safe check before writing, including after the user answers the modal\. A changed, replaced, removed or unreadable env must prevent writing and require a fresh preview/validation/explicit approval\. Do not silently rebase the old approval onto a new env\. Document the actual check/atomicity boundary without claiming filesystem guarantees the implementation does not provide\.

Extend the existing versioned evidence/result contract compatibly to identify that validation used an existing workspace env snapshot and to expose its actual identities and drift outcome\. Keep disk\-content, validation\-input and path\-only hashes distinct\. Do not relabel an old destination\_path\_identity or reference\_input\_content value as a disk\-content hash\. Preserve existing human\-readable preview behavior and keep diagnostics concise; no whole\-file/credential dumps or background logging service\.

## 3\. Handle preview expiry across the real approval lifecycle

Preserve the existing absolute lifetime and security behavior\. Expired approval must still fail closed\. Do not solve this by increasing the TTL, pausing its clock while a dialog is open, refreshing expiresAt on access, treating a stale affirmative answer as valid, or carrying that answer into another preview\.

Implement the smallest correction through requestWriteAuthorization and the actual trusted store/consume path:

- Expose the authoritative preview expiry and timestamp basis in the real preview evidence\. At the point the dialog is about to open, re\-evaluate expiry after any validation or other time\-consuming work\. Do not show an actionable approval for a record already expired\.
- Give the user a concise, accurate expiry notice in the existing approval flow, including the deadline or remaining time as measured when displayed\. If the existing supported dialog API can update, disable or close an expired pending modal without unrelated UI changes, use it\. Do not promise live countdown/automatic closure if that API cannot provide it; document that limitation and implement correct result handling regardless\.
- On an affirmative response, use the existing atomic store operation and current time to determine whether approval can still be recorded\. Preserve the checks again at consumption/write boundaries\. Distinguish expiration from already\-consumed/concurrent approval and other actual rejection reasons; avoid a separate check\-then\-approve race\.
- If expiration occurred while waiting, return a specific structured expiry outcome plus a clear user message that no write occurred and a fresh preview and explicit approval are required\. Do not replay the affirmative answer or automatically dispatch a new write\. Retain the old preview/attempt as history\.
- A subsequent normal user\-requested renewal must create a new product preview identity, rerun the necessary current validation/dependency checks and require its own explicit final approval\. It must not reuse a spent approval or expired record\.

Use supported existing interfaces and narrow type changes\. Preserve containment, destination shape, content checksums, env dependency checks, expiry/consumption and the genuine final Approve write / Cancel boundary\. No generic UI auto\-approval, custom replacement writer, alternate permission channel or state injection\.

## 4\. Permanent behavioral tests without real\-time waits

Use the existing test framework and controlled clock/fake\-timer facilities; add no dependency and do not wait ten real minutes\. Exercise actual service/store/result paths, not only formatting or source\-string assertions\. Use isolated filesystem fixtures and writer spies\. Offline test fixture writes are allowed; live product writes are not\.

Env cases:

1. Reused env supplied with the observed storage\-account mutation: validation receives the real file’s content, the supplied difference is disclosed, and the file is not changed\. Exercise braced/unbraced HOCON and the trailing\-LF difference without hiding semantic or byte differences\.
2. Missing/unreadable env and a path outside the allowed workspace: no fallback to caller text, no preview/approval/write\.
3. Env changes between preview and continuation, and while the approval modal is pending: stale approval cannot write; the diagnostic and required next action are accurate\. Cover replacement/deletion as appropriate at the same seam\.
4. Unchanged reused env: current file snapshot, actual validator input and trusted evidence agree according to their declared representation; the valid path still works\. Preserve the existing new\-env behavior in its affected regression suite\.

Expiry cases:

5. Already expired at invocation, expiry during validation before modal display, expiry exactly at the documented boundary, and expiry while the modal is pending: no writer call; correct expiry outcome and user guidance\.
6. Approval before expiry followed by expiry before consumption, where reachable: the actual final guard remains effective\.
7. Timely valid approval succeeds through the real source path in an isolated test\. Cancel does not write\. Consumed/concurrent records cannot be approved twice and are not mislabeled as expired\.
8. Explicit renewal produces a new ID/current snapshot and still requires a fresh approval\. A stale dialog answer, supplied checksum or repeated call cannot transfer authority\.

Combined case: exercise env drift and expiry around the same pending approval, checking that the writer is never called and that the reported reason corresponds to the implemented ordering\. Do not weaken one protection to test the other\.

Compile in the established isolated task\-owned lane with required resources and local dependencies\. Shared out and \.tsbuildinfo\.test must remain untouched\. Run affected trusted\-write/env/approval/result suites and required related regression gates\. Reuse unrelated authenticated results\. For a claimed pre\-existing failure, use relevant preserved preimages/baseline evidence; baseline status alone cannot waive a mandatory gate\. Fix regressions introduced by this task within scope\.

## 5\. Update the reusable driver guidance, review and close

Make only a small necessary update to the existing qualification helper/brief: heavy identity/fixture/capture checks should happen before the preview is created\. Checks that depend on the actual new preview must still happen afterward\. Read the product’s authoritative expiresAt immediately before a future final click and enforce an explicit time reserve for that action\. If time is insufficient, obtain a fresh preview through the normal product flow before any approval is spent; never skip binding checks or rely on an estimated historical TTL anchor\.

The old approval ledger remains spent\. This source task creates no new live\-run or approval allowance\. Do not exercise the installed product, rebuild/package/install, bump a version, change sign\-in/trust/profile state, mutate Git, publish to DBFS, deploy or run external jobs\. No shared cache/Temp/evidence cleanup is authorized\. Check disk capacity before isolated compilation and checkpoint if it cannot complete\.

Use one independent read\-only reviewer for the final source diff, authoritative env behavior, expiry/concurrency ordering, result contract and tests\. Permit its verdict only in task evidence\. Resolve relevant findings and have corrective deltas checked\. State reviewer provenance accurately and preserve intermediate verdicts rather than promoting an older review over later edits\.

Deliver one concise report/result with changed\-file pins, behavioral test outcomes, final reviewer verdict, implemented lifecycle behavior and precise residual limits\. Claim verified source repair only where established; do not claim installed/runtime qualification, close the failed \.154 write retrospectively or call its absence of writes a successful write test\.

Prepare, but do not execute, the smallest follow\-up to build one distinguishable candidate and qualify the corrected consumer Orchestrator flow\. Select an unused private version only when that build is authorized\. Any later real write requires a fresh, explicit bounded approval budget; do not inherit or reset the predecessor’s one spent approval\. Preserve \.154 and the failed trial as historical evidence\.

Release source ownership with final pins\. Carry runtime/DBFS, historical standalone\-validation byte identity, Framework documentation, case\-normalization and other acceptance limits\. The quarantine ended after 2026\-09\-13 UTC and is not extended; identify any actual required\-gate dependency\. No RELEASE\_ACCEPTANCE, FULL\_PRODUCT\_OR\_ASKTD\_READINESS or demo\-delivery claim\.

If a material behavior/API change beyond these two repairs is required, return the exact conflict and smallest reviewable alternative\. Do not broaden the task into another audit or an open\-ended harness rebuild\.
