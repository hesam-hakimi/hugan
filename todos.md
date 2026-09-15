Reconcile Phase H discrepancies and propose the first release scope

TASK_ID: ETL-0915-PHASE-H-AND-FIRST-RELEASE-SCOPE01
STATUS: PREPARED_FOR_OWNER_SUBMISSION; not executed by ChatGPT.
MODE: Contract reconciliation, focused evidence checks, and a concrete release-scope proposal.

Execute this brief in a new session in the existing development workspace. Here, the owner’s “H1” means resolving Phase H discrepancies and defining the first release scope. Recover the actual Phase H definitions from project records; do not substitute another historical finding with a similar label.

1. Outcome and authority

Determine which disputed expectations require a code repair, a test correction, an environment correction, or an owner decision. Recommend a useful first release scope with explicit acceptance criteria and an ordered implementation plan.

Complete the evidence work and prepare concrete recommendations before asking the owner to decide anything. An unresolved row must not block work on independent rows. This task authorizes reading project evidence, task-owned analysis files, and narrowly justified offline checks. Prepare an unapplied candidate diff only where it materially clarifies an unambiguous repair. Implementation and acceptance-policy changes are follow-up work; do not silently change code, tests, contracts, or release gates to make discrepancies disappear.

Use English for all execution, code, reports, and questions. Use text, filesystem, and DOM/accessibility interfaces only; no screenshots, video, OCR, or vision.

2. Recover the relevant state once

Expected checkout:
C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Authenticate the actual checkout and applicable local instructions. Resolve current task claims from published metadata and establish one task-owned evidence root under C:\docs. Resume only your own authenticated claim; do not acquire a live session’s claim or modify its files. Concurrent unrelated work is not itself a blocker.

Read the accepted repair/verification contract at:
C:\docs\ETL_Team_Test_Prep\references\09_AGILE_REPAIR_AND_VERIFICATION_CONTRACT.md

Expected v1.2: 23,684 bytes; SHA-256:
5387aa5c42940eceb2ffcd4d68d732ad3d57f1c69c2288c66bd0f32455e6f75b

Authenticate the file and record its version. Resolve other accepted contracts and references from the established staging/index. If an expected reference differs or is missing, record that fact and continue unaffected work; do not reconstruct its contents from memory. The old ETL_Team_Test_Prep\PROMPT.md is a completed task and must not be executed again.

Start with the actual N-2/N-3, Phase H, and G1 records from:

• ETL-0915-OVERNIGHT-READINESS-AND-LOCAL-RELIABILITY01, revision 2.
• ETL-0915-OVERNIGHT-REVIEW-CLOSEOUT01, including its final independent acceptance.
• The original Phase H contracts, assertions, source, fixtures, and accepted change history those records cite.

Resolve full task paths through published metadata. Inspect supporting files, not merely report summaries. Expand retrieval only for a disputed requirement or evidence dependency; do not re-audit every historical task.

Use this later handoff to avoid reopening completed work, then confirm only relevant identities from retained records:

• The two-file writeFlow filesystem precondition repair is APPLIED. Retained baseline/red: 17 passing/9 failing; repaired: 31 passing/0 failing, including all 26 original cases. It remains outside PURE_UNIT_TEST_PATTERNS; GUI/Extension Host execution was not demonstrated.
• The Developer header repair is APPLIED. The subsequent workflow-validator coverage repair is APPLIED: six regression cases pass; discovered agent files are validated when present. Whether Developer must exist remains the separate AP-1 policy question.
• The internal 0.3.160 kit has already been shared. Recorded-input installed preview/rejection and one scoped two-file write/readback have evidence. Fresh natural-language generation, read-only SQL-include reuse, and Databricks/DBFS execution are not established by that evidence.
• Last reported checkout state: HEAD 45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19, source version 0.3.147, dirty count 81; installed candidate 0.3.160. Shared out has 2,041 files; .tsbuildinfo.test is 158,611 bytes. These are context, not a substitute for current identity checks or a reason to reset drift.

3. Reconcile each discrepancy against accepted intent

Recover the exact Phase H population first. For every disputed row, record:

• Stable ID, affected behavior, test/assertion and source locations.
• Old expected behavior, current observed behavior, and evidence level/date.
• Applicable accepted contract clause, version, acceptance provenance, and any accepted superseding decision.
• Classification, confidence, recommended action, and impact on the proposed release.

Use these classifications with explicit supporting evidence:

|Classification              |Required basis                                                                                            |
|----------------------------|----------------------------------------------------------------------------------------------------------|
|CODE_DEFECT                 |Current behavior contradicts an applicable accepted requirement.                                          |
|STALE_TEST_EXPECTATION      |An accepted behavior change superseded the assertion; the replacement expectation follows that acceptance.|
|ENVIRONMENT_OR_INPUT        |A demonstrated setup/input difference explains the failure.                                               |
|ACCEPTANCE_DECISION_REQUIRED|Applicable requirements conflict or leave the behavior undecided.                                         |
|KNOWN_LIMITATION            |The behavior and its accepted scope limitation are both established.                                      |
|INSUFFICIENT_EVIDENCE       |Available evidence cannot settle the row; name the smallest missing observation.                          |

Current code, HEAD, a historical snapshot, and a passing test are observations, not automatic authorities. Trace which requirement applies and who accepted any change. In particular, G1 was accepted as a confirmed repository-state divergence; that acceptance did not decide which side is wrong.

For a proposed test correction, specify the replacement assertion and the regression it must still detect. For a code correction, specify expected behavior, the smallest affected surface, and a meaningful failing/passing control. Do not delete, skip, normalize away, or weaken assertions merely to obtain green results.

Keep populations distinct. Overnight accounting was 17 cleared + 5 surviving selected + 2 outside selection = 24 historical failures; the 17 included two hooks that blocked 19 cases. The later header check’s 12-to-11 assertion population, the historical 16 containing nine writeFlow failures, and the validator’s six regression cases are different sets. Map exact identities before combining results. The other seven historical failures are unknown until inspected, not automatically Phase H or zero.

4. Propose a release the owner can decide on

Read actual product goals and accepted consumer behavior. The overnight report found an unfilled business-context.md; do not invent business requirements to complete that template. Propose a coherent, minimal useful scope and mark assumptions explicitly. Do not assume a production audience, date, version number, or that every existing feature must be included.

For each candidate scenario, record: recommended inclusion/deferment, intended user outcome, supported inputs/environment, observable acceptance criteria, evidence already available, missing qualification, relevant blockers, and a reason for the recommendation.

Assess the project’s applicable job/env/include handling, creation in an empty consumer, reuse in an existing consumer, generation, validation, preview, approval, write, and readback flows. Derive supported formats and behavior from accepted contracts. Do not limit the proposal to the one successful recorded fixture or assume every listed flow is mandatory. Separate maintainer workflow requirements from the extension’s consumer scenarios.

Distinguish source checks, offline replay, packaged identity, installed execution, fresh natural-language generation, and Databricks/DBFS runtime evidence. Evidence at one level does not silently satisfy another. Relate item E, F-ROOT-1, identity/race limitations, and remaining failures to the proposed scenarios instead of calling every historical issue a release blocker.

Treat the already shared internal test kit and the proposed target release separately. Team members may explore diverse scenarios in their own projects; copying the owner’s project and limiting every test to preview/Cancel are not universal prerequisites. No team-test success should be inferred without results.

Finish with a small set of concrete owner decisions only where needed. For each, give the recommended option, an alternative, and the effect on behavior, work, and acceptance. Recommendations remain proposals until accepted. Assess AP-1 only if it affects the proposed scope; do not make it mandatory by assumption.

5. Reuse evidence and run only discriminating checks

Reuse matching retained evidence and existing helpers after checking their inputs, source identity, and limitations. Copy forward the authenticated b1-lane.corrected.js into this task only if its declared inputs apply. Reuse existing timing and encoding-aware failure-identity helpers when needed. There is no established shared C:\docs\helpers repository to adopt into.

Create small task-specific glue only for a demonstrated gap; briefly record the reason and reused origin. No helper framework, catalog project, or script per assertion is required.

Run a focused offline check only when it resolves a specific disputed row or necessary acceptance criterion that retained evidence cannot settle. State that question before running it. Use task-owned fixtures and isolated output; preserve raw exit status, counts, and failure identities. Incomplete or ambiguous comparisons remain UNKNOWN, never an empty “no regressions” list. Stop optional testing once the concrete uncertainty is resolved.

6. Preserve the working state

Keep checkout source, tests, maintainer files, canonical references, closed task records, installed extensions, consumers, shared output, and buildinfo unchanged. Do not reset, clean, stage, commit, change branches, install dependencies, or run ordinary commands that rebuild shared output. No packaging, installation, host launch, sign-in, model request, external runtime call, publication, or teammate messaging is part of this task.

Product write allowance is zero. Historical .154/.155/.160 allowances remain SPENT; expired quarantine and consumed/cancelled previews are not renewed. If a necessary conclusion needs an unavailable capability, document the exact follow-up experiment and continue the rest of the reconciliation.

7. Review and deliver one decision package

Apply the contract’s proportional BOUNDARY review to the interpretation of requirements and release acceptance. Obtain an independent read-only review of the final classifications, evidence links, and scope proposal. Use the named reviewer if available; disclose any fallback and the actual provenance of its response. Reviewer acceptance of the analysis does not accept a new product requirement or authorize release.

Correct relevant findings and obtain the disposition required by the contract. Keep the final review verdict separate from frozen reviewed material; do not edit reviewed files to insert their own verdict. Preserve prior revisions without manufacturing a large evidence tree.

Deliver report.md and result.json, with necessary supporting evidence only. The report must contain:

1. The Phase H disposition table and remaining uncertainties.
2. The recommended first-release scenario/acceptance table.
3. An ordered repair backlog, distinguishing proposed release blockers from deferred work.
4. Concrete owner decisions, each with a recommendation and consequence.
5. One ready-to-run next implementation brief for the highest-priority unambiguous repair, or the exact decision that must precede it. Do not execute that next task automatically.

Keep structured rows and provenance in result.json; reference long logs instead of copying them into prose. Include actual preservation and review results. Use RECONCILED or RECONCILED_WITH_OPEN_DECISIONS only as supported; distinguish incomplete investigation from an owner decision. Do not report APPLIED or RELEASE_READY for this analysis task.

Complete all available work, persist the package, release only this task’s ownership, and stop. The final response should lead with what should be fixed first, the recommended release scope, and any concrete choice still needed from the owner.
