# ETL Framework Extension — Implemented Capabilities and Evidence

## 1. Evidence labels

| Label | Meaning |
|---|---|
| `IMPLEMENTED` | Source/resource exists |
| `SOURCE_VALIDATED` | Compile/lint/focused/regression evidence passed |
| `PACKAGE_VALIDATED` | Exact VSIX content/provenance checks passed |
| `RUNTIME_VALIDATED` | Active installed Extension behavior was exercised |
| `PARTIAL` | Some behavior is proven, not the full lifecycle |
| `BLOCKED` | Cannot proceed without a prerequisite or policy repair |
| `DEFERRED` | Intentionally left for another authorized task |

Never convert source or package validation into a runtime claim.

## 2. Repairs 3–8: core control-plane hardening

### Repair 3 — stale expectations without restoring unsafe behavior

- aligned stale tests after safer default v3 workspace behavior;
- preserved zero-write and trusted-approval semantics;
- did not restore direct non-onboarding writes.

### Repair 4 — protected roots and write bypass

- classified `sample_repo` and reference roots as non-consumer/protected;
- removed UnitTestCoordinator bypass of trusted Preview/Approval;
- preserved independent review of the fix.

### Repair 5 — additional consumer-write routes

- unified Explain save;
- unified Artifact Reuse apply/create;
- unified Repo Context initialization;
- bound writes to canonical root and one-time authorization;
- rejected path, preimage, and content drift.

### Repair 6 — physical containment and package hygiene

- hardened primary RepoWriter paths and other live mutation routes;
- added real-filesystem symlink/junction/TOCTOU evidence;
- excluded temp, nested Git, test-output, and build-noise artifacts;
- introduced package size/entry limits and exact archive verification.

### Repair 7 — shared policy-free containment

- created a shared `lstat`/`realpath` primitive;
- applied it across customization and legacy write sinks;
- used mutation controls to prove tests were not false-green.

### Repair 8 — machine-authoritative job-config contract

- added `job-config-envelope.v1.json` and trusted resolution;
- required canonical stage-keyed `modules { ... }` HOCON;
- packaged non-empty critical keys and fallback examples;
- removed Framework-source dependency from fresh consumers;
- added explicit `UNSUPPORTED_UNITY_CATALOG_TARGET` behavior;
- verified contract presence and byte identity inside the VSIX.

The 2026-08-24 package evidence for `0.3.141` remains historical proof of these repairs, not the current package identity.

## 3. Consumer-Agent provisioning and catalog

Implemented and verified properties include:

- six packaged consumer Agents;
- only `ETL Orchestrator` user-invocable;
- five internal specialists byte-locked to the canonical catalog;
- role-specific tool policy generated into consumer assets;
- package-asset byte-lock tests;
- no authority broadening for Verifier, Troubleshooter, Researcher, or Operator;
- consumer guidance that separates provisioning, Preview, verification, write, and runtime operation.

An installed snapshot reported all 16 ETL tools registered. Static catalog and tool registration do not prove every live connection or scenario.

## 4. Repairs 11–13 and Runtime QA support

### Repair 11 and Repair 12

Their focused suites remained green through the later Repair 13 work. Repair 12's trust boundary around projection diagnostics was explicitly rechecked after the structured-channel change.

### Repair 13 fixture coverage

A synthetic QA bundle was created to exercise:

- active and inactive mappings;
- conflicts;
- unresolved authority-critical references of types BR, TR, JC, and ER;
- malformed rows;
- oversized rows;
- declared and undeclared state behavior;
- dual-channel Markdown/structured parity.

Two scenarios remain deliberately deferred rather than falsely claimed:

- FT references are unreachable on the selected parser/bundle route;
- historical/unknown syntax is unsupported input syntax and must not be admitted as active authority.

### Structured diagnostic channel

The accepted task changed the public consumer seam so parser diagnostics are present in structured output as well as Markdown. The narrow implementation path involved:

- `src/core/sttm/SttmResolvedEvidence.ts`;
- `src/core/sttm/SttmMarkdownBundleParser.ts`;
- `src/tools/EtlReadOnlyToolService.ts`;
- focused Repair 13 tests;
- canonical Phase-H report regeneration.

Reported verification:

```text
PUBLIC_STRUCTURED_DIAGNOSTIC_CHANNEL: PRESENT
MALFORMED_ROWS_FAIL_CLOSED: YES
MALFORMED_ROWS_ACTIVE_AUTHORITY: NONE
MARKDOWN_STRUCTURED_DIAGNOSTIC_PARITY: YES
VALID_MAPPING_IDS_AND_ORDER_PRESERVED: YES
PUBLIC_SEAM_TESTED: YES
REPAIR_11_PASS: YES
REPAIR_12_PASS: YES
REPAIR_13_PASS: YES (44)
```

Negative controls removed the new structured channel and stripped parser row identity. The expected feature-dependent tests failed, demonstrating load-bearing coverage.

## 5. Phase-H baseline refresh

The Phase-H report baseline was regenerated canonically after the accepted tracked-input drift. Evidence reported:

- two isolated generations;
- semantic equality of substantive metrics and gates;
- latency-only volatile differences;
- identical tracked-input digest;
- negative stale-baseline test still detected injected drift;
- no threshold, scenario, generator, or assertion weakening;
- previously failing EvalGating tests passed against the refreshed baseline.

This refresh was not a hand edit and should not be regenerated again without a new tracked-input change and explicit authorization.

## 6. Final independent review before packaging

The independent review reported:

```text
RUNTIME_QA_SUPPORT_INDEPENDENT_REVIEW_RESULT:
PASS_READY_FOR_VERSION_0_3_146_AND_PACKAGE
```

Key reported checks:

- implementation and review used distinct sessions;
- repository was not mutated by the reviewer;
- structured diagnostic channel present at the consumer public seam;
- malformed rows failed closed;
- agent catalog/resource parity passed;
- package asset byte-lock passed;
- Agent tool sets and authority remained unchanged;
- Phase-H refresh was legitimate;
- compile, compile-test, lint, Repairs 11/12/13, fixture, and governance suites passed;
- no new functional or security regressions.

## 7. Version and package `0.3.146`

The version/package stage reported:

- `package.json` version changed from `0.3.145` to `0.3.146` and nothing else in that file;
- dependencies/devDependencies unchanged;
- no lockfile created;
- one new artifact: `databricks-etl-copilot-0.3.146.vsix`;
- ten pre-existing VSIX artifacts remained byte-identical;
- source repairs were unchanged during packaging;
- canonical validation result: `2298 passing / 1 pending / 2 failing`;
- both remaining failures were unchanged historical control-plane/customization failures;
- zero new functional and security regressions;
- package content identity, expected 66 entries, six consumer Agents, and provenance passed independent exact-path inspection.

The independent package verifier concluded:

```text
EXACT_PACKAGE_VERIFICATION_0_3_146_RESULT:
PASS_ARTIFACT_VALID_BLOCKED_GOVERNANCE_EXCEPTION
```

Therefore the archive is technically sound, but governance does not yet authorize the lifecycle that created it.

## 8. Known unchanged full-suite failures

Latest reported full-unit state:

```text
2298 passing
1 pending
2 failing
```

The two failures are unchanged and not attributed to the Repair 13 functional work:

- F1: missing `.github/prompts/deploy-v3-agent-tool-context-gap.prompt.md` in a protected maintainer-delivery test;
- F3: existing `src/**/AGENT.md` files where the customization test expects standard `AGENTS.md` guidance.

They still require a separate owner/governance decision before a clean merge/release. “Pre-existing” does not mean permanently acceptable.

