Repair A — Explicit expected-failure reconciliation and commit authorization

Continue in the same writable source-repository Agent/Claude session where the immediately preceding Repair A implementation and validation completed.

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Branch:

fix/workspace-write-completion-0.3.148

Pinned parent HEAD:

a7ec7284906897321b2af5f7bf99de99211f7b70

This follow-up authorizes reconciliation of the five exact failures already observed in the immediately preceding Repair A run.

It does not authorize new implementation changes.

PowerShell requirement

For every independent PowerShell terminal invocation, prefix the same invocation with:

$env:PATHEXT = '.COM;.EXE;.BAT;.CMD';

Do not persist this value through setx, registry, profile, VS Code settings, or repository changes.

Decision

Do not run npm run eval:golden.

Do not modify or regenerate:

* docs/eval/phase_h_latest_report.json
* docs/eval/phase_h_latest_report.md
* any other Eval report or baseline artifact

The Eval baseline will be refreshed once, in a separate commit, after Repair B is complete. Refreshing it now would create avoidable duplicate work.

The two newly observed EvalGating failures are authorized as temporary expected freshness failures caused directly by the scoped Repair A source change.

Expected Failure Manifest

Use the exact test identities and signatures captured in the immediately preceding Phase 0B and full-suite reports.

Do not rediscover or re-investigate an entry that matches this manifest exactly.

Known baseline failures — continue without investigation

The three pre-existing failures must match the exact identities and signatures recorded before Repair A.

Their grounded root causes are:

1. Missing:
    .github/prompts/deploy-v3-agent-tool-context-gap.prompt.md
2. business-context.instructions.md frontmatter declares applyTo but does not declare name.
3. Eleven tracked src/*/AGENT.md files exist where the test expects an empty inventory.

Classification:

KNOWN_BASELINE_FAILURE

Required behavior:

* confirm exact identity and signature match;
* record the match;
* do not investigate again;
* do not rerun the test individually;
* continue.

Authorized Eval freshness failures — continue without investigation

The following two exact tests are authorized:

1. EvalGating > passes against the committed Phase H baseline report
2. EvalGating > allows deterministic v3 baseline reports without prompt telemetry

Expected failure signature:

AssertionError: Tracked project or behavior inputs changed since the last baseline report: src/core/framework/TrustedJobConfigEnvelopeResolver.ts

Classification:

KNOWN_EVAL_FRESHNESS_FAILURE

Reason:

Repair A intentionally changed an input tracked by PHASE_H_TRACKED_INPUT_PATTERNS, while this task intentionally protects the previously committed Phase H report from modification.

Required behavior:

* confirm both test names match exactly;
* confirm the failure class and changed tracked path match exactly;
* record them as expected temporary Eval freshness failures;
* do not investigate again;
* do not rerun them individually;
* do not weaken EvalGovernance;
* do not modify tracked-input patterns;
* do not regenerate Eval reports;
* continue.

Fail-closed mismatch rules

Stop without committing if:

* any baseline failure has a different test identity;
* any baseline failure has a different signature or root cause;
* either EvalGating test name differs;
* the Eval failure identifies an unexpected changed path;
* another failure appears;
* a previously observed failure disappears for an unexplained reason;
* the suite totals differ from the immediately preceding report without a grounded explanation;
* the current diff differs from the immediately preceding validated Repair A diff.

A matching count alone is insufficient.

Expected validated evidence

The immediately preceding Repair A report recorded:

* pre-change suite:
    * 2332 passing
    * 5 pending
    * 3 failing
* characterization before repair:
    * 84 passing
    * 15 expected failing
* characterization after repair:
    * 99 passing
    * 0 failing
* compile:
    * exit 0
* package asset tests:
    * 34 passing
* post-change full suite:
    * 2340 passing
    * 5 pending
    * 5 failing
* failure composition:
    * 3 exact pre-existing baseline failures
    * 2 exact authorized EvalGating freshness failures
    * no other regression

Use this evidence only if the working-tree diff is byte-for-byte unchanged from the immediately preceding report.

Do not rerun the full unit suite when the diff and test evidence are unchanged.

Authorized changed paths

The working tree must contain exactly these nine changed paths and no others:

1. resources/framework/contracts/job-config-envelope.v1.json
2. src/core/framework/TrustedJobConfigEnvelopeResolver.ts
3. src/tools/EtlReadOnlyToolService.ts
4. resources/copilot/context/etl-module-reference.md
5. docs/reference/ETL_MODULE_REFERENCE.md
6. package.json
7. src/test/suite/EtlReadOnlyToolService.test.ts
8. src/test/suite/EtlReadOnlyTools.test.ts
9. src/test/suite/trustedJobConfigEnvelope.test.ts

Expected diff summary from the preceding report:

* 9 files changed
* 704 insertions
* 10 deletions

If the changed-path inventory or diff differs, stop and report the difference.

No additional edits

Do not make any new production, test, documentation, formatting, Eval, fixture, version, dependency, or lockfile edit.

Do not alter the current Repair A diff merely to silence the two EvalGating failures.

Do not begin Repair B.

Final pre-commit verification

Before staging:

1. Confirm branch is:
    fix/workspace-write-completion-0.3.148
2. Confirm HEAD is:
    a7ec7284906897321b2af5f7bf99de99211f7b70
3. Confirm the nine changed paths exactly match the authorized inventory.
4. Run:
    git diff --check
5. Confirm the diff is unchanged from the immediately preceding validated report.
6. Confirm all W1-protected paths remain unchanged.
7. Confirm both Eval-report files remain unchanged.
8. Confirm:
    * package version remains 0.3.147;
    * dependencies remain unchanged;
    * no lockfile was added or modified;
    * no fixture was added;
    * src/tools/EtlActionToolService.ts is unchanged;
    * DataSourcingConfigValidator is unchanged;
    * ModuleSequenceExtractor is unchanged;
    * no generated build or VSIX artifact exists.
9. Produce a five-entry reconciliation table containing:
    * exact test identity;
    * exact signature;
    * classification;
    * baseline SHA;
    * reason;
    * action taken.

The action for all five entries must be:

recorded and continued without reinvestigation

Commit authorization

If and only if every verification above passes, stage only the nine authorized paths explicitly.

Do not use git add -A.

Create exactly one commit with subject:

fix: expose canonical runtime artifact contract

The commit must:

* have sole parent:
    a7ec7284906897321b2af5f7bf99de99211f7b70
* contain exactly the nine authorized paths;
* contain no Eval-report modification;
* contain no W1 change;
* not amend or squash another commit;
* not be pushed.

Post-commit verification

After committing, verify:

* exactly one commit exists above the pinned parent;
* the new commit has exactly one parent;
* its parent is the pinned parent;
* its subject is exact;
* its changed-path inventory contains exactly the nine authorized paths;
* worktree and index are clean;
* untracked-path count is zero.

Final report

Report:

* branch;
* Repair A full commit SHA;
* parent SHA;
* exact changed paths;
* final five-entry Expected Failure Manifest;
* confirmation that the three baseline failures were not reinvestigated;
* confirmation that the two EvalGating failures were classified as expected temporary freshness failures;
* confirmation that eval:golden was not run;
* confirmation that Eval reports were unchanged;
* confirmation that W1 behavior was unchanged;
* confirmation that no Repair B, fixture, F5, VSIX, external service, push, or publication occurred;
* final git status --short --untracked-files=all.

End with exactly one marker:

REPAIR_A_CONTRACT_DISCOVERY_COMMITTED

or, if any identity or protection check fails:

REPAIR_A_CONTRACT_DISCOVERY_BLOCKED
