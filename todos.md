# Repair include authority and bind the effective dependencies to approval

STATUS: OWNER\_AUTHORIZED\_FOR\_SUBMISSION; not executed by ChatGPT\.
TASK\_ID: ETL\-0914\-INCLUDE\-AUTHORITY\-AND\-BINDING\-REPAIR01\.
PREDECESSOR: ETL\-0914\-ENV\-REUSE\-AND\-APPROVAL\-EXPIRY\-REPAIR01, completed with source repairs verified and HIGH finding F1 open\.
SCOPE: Bounded source repair of F1, necessary resolver/manifest/approval/evidence integration, affected permanent tests, and focused independent review\.
PRODUCT\_WRITE\_AUTHORIZATION\_BUDGET: 0\. The earlier installed \.154 trial’s single approval remains spent and non\-transferable\.

Execute this task in the Windows engineering workspace\. This prompt is self\-contained for a new GitHub Copilot engineering chat\. All engineering replies, code, tests, prompts and documents must be English\. Use text, files and existing diagnostics; no screenshots, video, OCR or vision\. Source edits and writes to disposable automated\-test fixtures are authorized; installed\-product writes and live qualification are not\.

## Restore only the relevant context

Resolve the predecessor’s exact evidence root under C:\\docs from its task ID\. Read its final report\.md, result\.json, pins\.json, reviewer/ and reviewer/delta/ verdicts, particularly the retained F1 evidence and proposed repair\. Follow only directly relevant references\. Read applicable repository instructions and authenticate the current source against the predecessor’s changed\-file pins\. Use its recorded worktree; the last known location is C:\\repos\\etl\-extension\\etl\_fw2\\recovery\-extension\-product\-0\.3\.147\. Verify rather than infer the current location\.

The predecessor reports that IncludeResolver allows caller\-supplied include content to shadow workspace files\. Include files can also be legitimate proposed write destinations, and reused\-env includes currently have path\-based identity in the manifest\. Therefore a universal disk\-precedence rule would be insufficient\. Reproduce F1 at the actual resolver entry point, trace affected callers, and distinguish faulty reuse from legitimate proposed content before changing behavior\. This is separate from the historical INCLUDE\-SQL\-KEY\-EXTRACTION\-001 finding unless a demonstrated code dependency connects them\.

Preserve these completed behaviors: reused env comes from the contained workspace file; missing reuse paths fail closed; disk and validator\-input identities remain distinct; expiry is checked before the modal; approveWithOutcome is the atomic authority; expired\_while\_pending differs from already\_consumed; dependency drift is checked before the prompt, after the answer and before writing\. TTL is never extended or refreshed\. The deadline notice is static, and no filesystem lock is claimed\.

Acquire the normal source claim after checking ownership\. Resume this task’s existing claim if present; if it is already completed with unchanged inputs, authenticate and reuse the result\. Save full current preimages of touched tracked and untracked files\. The predecessor reported its old host still running: leave that host, chat, profile, consumer and spent approval untouched\. This task needs no runtime ownership\.

## Establish one explicit authority for each include

Implement the smallest correction through the existing resolver, validation and guarded\-write pipeline\. Necessary changes to manifest/checksum construction, approval records and evidence are authorized within this scope\. Do not stop merely because F1 crosses those seams\.

Determine each include’s role using the product’s actual operation and artifact policy\. Supplied text alone must not silently turn a reused dependency into a proposed modification\.

|Include role                                                        |Required behavior                                                                                                                                                                                                                                                                          |
|--------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Existing include reused without a planned write                     |Resolve through existing workspace/containment rules and read the workspace snapshot. Use that effective content in validation. Supplied content cannot override or become a fallback; disclose a mismatch without echoing configuration contents.                                         |
|Explicit proposed creation or modification permitted by the product |Preserve the proposed content path. The effective proposed bytes must undergo the required validation and appear as the corresponding CREATE/MODIFY artifact in the trusted preview and approved manifest. An existing disk file does not automatically override an explicit proposed edit.|
|Missing/unreadable/out-of-scope reused dependency                   |Refuse before preview with an actionable diagnostic. Caller text cannot rescue a missing reused file. An absent file is valid only through a supported explicit creation plan.                                                                                                             |
|Conflicting roles or competing contents for one resolved destination|Establish one consistent plan under existing policy or refuse the ambiguity. Do not select authority by argument ordering or silently accept two meanings for the same path.                                                                                                               |

Apply this distinction to the include types and nested dependencies actually reached by the affected flow, including reuse declared through an env file\. Use existing resolution roots, containment and recursion limits\. Do not broaden supported include formats, introduce network resolution, or replace the parser\. Preserve unrelated standalone/proposal workflows; any new context requirement must be handled explicitly by their callers\.

## Bind what validation actually used

Create a coherent snapshot of the effective include graph\. Keep proposed write artifacts distinct from reused read dependencies\. Every workspace dependency whose contents affect validation must have a measured content identity bound to the trusted preview and checked on continuation, including dependencies reached transitively\. Read dependencies must not become write destinations merely to make them hashable\.

Preserve existing path identity semantics\. Add the necessary dependency/content binding through the established manifest/store contract; document the exact representation and ordering that the checksum covers\. Do not relabel a path hash as file\-content proof\. Preserve raw disk\-byte identities separately from decoded or transformed validator\-input identities and expose transformations honestly\. If validation repairs proposed content, bind the actual resulting candidate and retain the input/output distinction\.

The continuation must verify the preview’s complete bound plan and effective dependencies\. A dependency changed, removed or redirected after preview must not permit writing against the old validation\. Reuse the predecessor’s checks before the modal, after the answer and at the last safe point before the first write\. Preserve its record\-spending and expiry precedence: drift before prompting does not spend the record; drift after successful approval is reported with the actual consumed state\. No stale answer may be replayed against a replacement preview\. Describe the remaining check\-to\-write race accurately; do not claim locking or transactional atomicity that does not exist\.

If the strengthened contract changes approval compatibility, make that explicit and reject insufficiently bound records on the affected path\. Do not manufacture missing hashes for old records or migrate historical approvals into new authority\. Use one established approval pipeline, without TTL changes or bypasses\.

Extend the real transported evidence only as needed to show include roles, effective provenance, content/dependency identities, and the comparison actually enforced\. Action\-tool consumers receive serialized markdown, so an in\-process data field alone is insufficient\. Preserve the existing evidence meanings and collector compatibility where possible; document any unavoidable contract version change\. Avoid raw configuration/secret contents in new diagnostics\. Reused dependencies are not reported as written artifacts\. Historical standalone\-validator/writer byte differences remain historical limitations, not retroactively closed by this repair\.

## Prove the behavior with affected tests

Use permanent behavioral tests through the real affected resolver and authorization seams, with temporary workspaces and controlled clocks\. Mock dialogs and external effects where necessary; do not stub away the authority decision, checksum binding or freshness check being tested\. Extend existing suites/helpers instead of constructing another qualification harness\.

Cover the concrete risks:

- Reused include: divergent caller text cannot affect the effective validation input; absent/unreadable files fail without fallback; reference files remain unwritten\.
- Proposed includes: supported new and changed includes retain their intended content through validation, preview, continuation and the test writer\. Supplied content outside the approved write plan cannot substitute for a reused dependency\.
- Mixed/nested graphs: actual dependencies are included in the binding, duplicate/conflicting resolved paths cannot create silent precedence, and existing containment failures remain failures\.
- Freshness and record lifecycle: change a reused dependency between preview and continuation, while the modal waits, and at the final pre\-write check\. Assert the outcome, correct spent/unspent state and no write for refused cases\. Use existing injection seams or narrow test hooks rather than real\-time waiting\.
- Identity/evidence: content changes invalidate the appropriate binding; an old insufficiently bound preview cannot authorize the affected operation; transported evidence describes the identities actually used\. Preserve env\-reuse, expiry and genuine proposed\-write positive cases\.

Confirm each negative test reaches the intended guard\. Do not allow an unrelated earlier render/parser failure to create a false pass\. Run the compiler and affected regression suites in an isolated output lane\. Compare failures against the authenticated current pre\-edit baseline, not a clean HEAD that omits earlier repairs\. Fix regressions introduced here and report exact failure identities\. Baseline reproduction does not waive a mandatory gate; the exception that expired after 2026\-09\-13 UTC is not renewed\.

## Review, preserve and finish

Use one independent read\-only reviewer for the final changed source, F1 reproduction, role rules, checksum/freshness integration and behavioral tests\. Preserve the initial verdict and review corrective deltas if needed\. State reviewer provenance accurately\. Resolve findings caused by this task; record genuinely unrelated findings without expanding into another general audit\.

Preserve unrelated dirty state, maintainer assets, shared out and \.tsbuildinfo\.test, installed \.153/\.154 and their packages, all historical consumers/evidence, authentication and approval ledgers\. Do not mutate Git, install dependencies, clean shared caches/Temp, change profile/trust settings, build/package/install a candidate, start a live model run, publish to DBFS or run external jobs\. Isolated compilation and test outputs are allowed\. Check available disk space before substantial local output and reuse existing helpers\.

Deliver report\.md, result\.json, changed\-file pins and the reviewer verdict under this task’s evidence root\. State whether F1 is fixed, the enforced role/binding rules, meaningful test results, compatibility implications and precise residual limits\. Claim verified source repair only when supported\. Preserve predecessor env/TTL findings and the failed \.154 trial unchanged\.

Prepare one concise follow\-up brief for a distinguishable candidate and installed natural\-language ETL Orchestrator qualification\. Do not execute it or assume the next unused version\. That future consumer test must use the selected ETL Orchestrator through natural language, with no manual slash commands or direct tool substitution\. A real approved\-write test needs a fresh explicit bounded budget; this task grants none\. No release, runtime/DBFS readiness or demo\-delivery claim follows from source verification\.

Complete the authorized work without repeated routine permission requests\. If a concrete access constraint or unrelated architectural change prevents completion, checkpoint the verified work and report the exact blocker and smallest reviewable next action\. Release source ownership with final pins and a concise outcome\.
