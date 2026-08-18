ETL Extension — Remaining Work and Priorities

Prepared: 2026-08-18
Purpose: A simple prioritized view of the important work that remains before the ETL Extension is ready for broader release and continued roadmap development.

Priority definitions

• P0 — Release blocker: Must be completed before the affected capability can be released.
• P1 — Core next capability: Important architecture or product work that should follow the immediate release blockers.
• P2 — Later hardening: Valuable product maturity work that can follow the core workflow.

Remaining work

|Order|Priority               |Work item / phase                              |In simple terms                                                                                             |Problem fixed or feature added                                                                                                                                |
|----:|:---------------------:|-----------------------------------------------|------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
|1    |P0                     |**HF1 independent code audit**                 |Review the complete 27-file hotfix without changing it.                                                     |Confirms that framework discovery, Oracle validation, and write authorization are secure and do not introduce bypasses.                                       |
|2    |P0                     |**HF1 real-consumer test**                     |Install the sanitized VSIX in an isolated VS Code profile and rerun the reporter’s original Oracle workflow.|Confirms that `db_data_out` and `db_ctrl_out` work in a fresh consumer repository. Current status: `NOT EXECUTED — SAMPLE UNAVAILABLE`.                       |
|3    |P0                     |**Permanent VSIX packaging fix**               |Update the packaging configuration so test files are excluded automatically.                                |Removes `.tsbuildinfo.test` and `tsconfig.test.json` without manually editing the VSIX after every build.                                                     |
|4    |P0                     |**Resolve six baseline unit-test failures**    |Repair or formally regenerate the stale Phase-H, package, and customization baselines.                      |Produces a completely green full-unit test run. The six current failures are pre-existing, but they still prevent a clean release claim.                      |
|5    |P0                     |**HF1 PR and CI validation**                   |Review the diff, commit the 27 authorized files, push the hotfix branch, and run CI.                        |Converts the local hotfix into a traceable and reviewable change based on `feature/v3-agentic-redesign`.                                                      |
|6    |P1                     |**S-B secure resolved agent context**          |Rebuild the rejected S-B candidate as a small, immutable, and deterministic context object.                 |Fixes schema-version typing, unsafe getters/proxies/iterators, provenance correlation, public API bypasses, and canonical-digest safety.                      |
|7    |P1                     |**S-A hardening follow-up**                    |Correct remaining weaknesses in settings inventory and provenance handling.                                 |Adds bounded recursion, own-property safety, element validation for `languageIds`, and clearer precedence/default-value behavior.                             |
|8    |P1                     |**S-C trusted planning evidence**              |Convert the safe S-B context into evidence that the planner can trust.                                      |Adds completeness and ambiguity decisions and explicit workspace/resource selection. The overlap with `TrustedPlanningEvidenceService` must be resolved first.|
|9    |P1                     |**S-D production consumer and result envelope**|Connect the trusted context to the first real planning/execution consumer.                                  |Adds the first production consumer, result envelope, and child-operation propagation; it also closes the uncovered `EtlSettingsVsCodeBindings.ts` gap.        |
|10   |P1                     |**S-E drift and staleness protection**         |Compare the current context with the context used during planning.                                          |Uses `contextDigest` to block execution when settings, evidence, or framework definitions changed after preview.                                              |
|11   |P2                     |**S-F user-facing explanations**               |Translate machine-only diagnostic codes into clear English guidance.                                        |Gives users understandable errors without exposing raw values, secrets, or unsafe diagnostic text.                                                            |
|12   |P2                     |**S-G / S-H lifecycle controls**               |Add controlled persistence, overrides, and bootstrap/result lifecycle handling.                             |Allows approved work to resume safely while preventing stale, untrusted, or silently overridden state.                                                        |
|13   |P2                     |**S-I / S-J / S-K delivery identity**          |Bind generated work to registry, deployment destination, and publisher identity.                            |Prevents artifacts from being deployed or published under the wrong target, registry, or owner.                                                               |
|14   |P0 before final release|**Final package and smoke validation**         |Build a clean VSIX, inspect its contents, install it in a fresh profile, and run the supported workflows.   |Confirms installation, activation, Preview → Approval → Write, Oracle validation, no unauthorized files, and no regression before publishing.                 |

Recommended execution order

```text
HF1 independent audit
→ HF1 real-consumer test
→ Permanent packaging fix
→ Baseline-test repair
→ HF1 PR and CI
→ S-B
→ S-A hardening
→ S-C
→ S-D
→ S-E
→ S-F
→ S-G / S-H
→ S-I / S-J / S-K
→ Final release validation
```

Current status note

The current sanitized HF1 VSIX is suitable only for isolated internal testing. It is not yet the final release package. No real-consumer end-to-end test, final independent audit, commit, push, merge, marketplace publication, or production deployment has been completed yet.
