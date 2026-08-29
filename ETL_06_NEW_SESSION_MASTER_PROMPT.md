# New Session Master Prompt — ETL Extension Governance Repair

## Environment

Use this prompt in a **fresh generic local coding Agent session** opened at the Extension source repository. Use the strongest available reasoning model. Do not use the consumer `ETL Orchestrator` or any consumer Agent for this maintainer governance task. The implementation and independent review must be separate sessions.

Copy everything below into the new session.

---

```text
TASK: HF1_V2_REPAIR_PACKAGE_LIFECYCLE_GOVERNANCE_OWNER_DECISIONS_V3

ROLE
You are a fresh generic maintainer-side implementation Agent. You are not a
consumer ETL Agent and you are not the later independent reviewer. Work only in
the Extension source repository and do not claim PASS without executable evidence.

OWNER COMMUNICATION
- Explain progress and decisions to the owner in Persian.
- Keep repository/product text, code, tests, identifiers, and reports in English.
- Work one bounded step at a time.

EXPECTED REPOSITORY IDENTITY — VERIFY, DO NOT ASSUME
Repository root:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1_v2

Origin:
https://github.com/TD-Universe/agentic_etl.git

Branch:
hotfix/hf1-oracle-fresh-consumer-v2

Last reported HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

Latest reported source/package version:
0.3.146

Latest reported artifact:
databricks-etl-copilot-0.3.146.vsix

CURRENT FACTS TO RE-VERIFY
1. Repair 13 structured diagnostics, Phase-H refresh, and independent review passed.
2. The 0.3.146 archive passed exact package verification.
3. Package lifecycle governance still blocks the artifact because **/*.vsix has
   no safe VERSION_AND_PACKAGE create-only exception.
4. Certification provenance has a producer/reviewer ambiguity and can fail open
   when producer identity is missing or display-name aliases hide sameness.
5. The last repair attempt made zero edits and stopped because five authorized
   paths were insufficient for Decision B.

AUTHORIZED PATHS — EXACTLY THESE EIGHT
1. .github/agent-governance/process-manifest.json
2. .github/agent-governance/schemas/process-manifest.schema.json
3. scripts/agent-governance/verify-change-boundary.mjs
4. scripts/agent-governance/tests/change-boundary-adversarial.test.mjs
5. scripts/agent-governance/tests/manifest-registry.test.mjs
6. scripts/agent-governance/emit-checkpoint.mjs
7. scripts/agent-governance/tests/checkpoint-fidelity.test.mjs
8. scripts/agent-governance/validate-customizations.mjs

No other repository path is authorized. Do not modify package.json, any VSIX,
src/**, resources/copilot/**, test registration, prompts, consumer workspaces,
or installed Extension state. Do not commit, push, tag, stash, install, activate,
or start Runtime QA.

BEFORE THE FIRST EDIT
1. Verify root, origin, branch, HEAD, version, staged count, stash count, and
   concurrent-Agent state.
2. Capture an independent full-tree baseline and a protected-path baseline using
   the repository's canonical tools. Include ignored/protected VSIX paths; do not
   rely only on git ls-files.
3. Read all applicable AGENTS.md/agent instructions and governance manifests.
4. Inspect the exact current implementations and tests for:
   - protected-path exception lookup;
   - change-kind calculation;
   - artifact count/identity derivation;
   - checkpoint provenance and checkIndependence;
   - actor/reviewer identity resolution;
   - manifest/static customization validation.
5. Report any contradiction and stop if the eight paths are still insufficient.

DECISION A — SAFE CREATE-ONLY VSIX EXCEPTION
Implement one narrow VERSION_AND_PACKAGE exception that is machine-enforced.

Required semantics:
- allowed change kind: CREATED only;
- exactly one new VSIX for the intended stage;
- zero modification, replacement, rename, or deletion of existing VSIX files;
- exact filename derived from current package name/version;
- archive Extension ID and version agree with package.json;
- declared separate authorization token is enforced;
- no other stage receives this exception;
- generic **/*.vsix protection remains fail closed.

Do not merely add prose fields. The verifier must read and enforce every field.
Do not use mtime or an unconstrained glob as artifact identity.

Required adversarial tests:
- correct single newly created artifact passes with the exact token;
- no exception blocks;
- wrong stage blocks;
- missing/wrong token blocks;
- wrong filename/version/Extension ID blocks;
- two new artifacts block;
- existing artifact content change blocks;
- existing artifact replace/rename/delete blocks;
- non-VSIX protected-path negative control remains blocked.

DECISION B — FAIL-CLOSED PRODUCER/REVIEWER INDEPENDENCE
Use the existing checkpoint/governance enforcement path; do not create a parallel
policy system.

Required semantics:
- missing producer identity blocks a certifying PASS;
- malformed or wrong-typed provenance blocks;
- producer and reviewer resolve to canonical machine actor identities;
- aliases/display-name variants cannot hide that they are the same actor;
- producer and certifier must be distinct when independent certification is
  required;
- distinct required session IDs remain enforced;
- a reviewer cannot certify its own implementation/package output;
- static manifest validation detects an ownership topology that makes the
  required independence impossible;
- no new Agent and no authority broadening;
- existing valid independent-review/package-verification routes remain valid.

Do not encode trust solely in a user-facing actor name. Do not make
etl-release-verifier both the producer and the certifier of the same artifact.

TEST AND VALIDATION REQUIREMENTS
Run repository-canonical commands and record exact command, exit code, and
result. At minimum:
1. manifest schema/registry validation;
2. change-boundary adversarial suite;
3. checkpoint-fidelity suite with negative/mutation controls;
4. customization/governance validation;
5. governance registration and package-asset byte-lock checks;
6. compile, compile-test, and lint when canonical for these changes;
7. Repair 11, Repair 12, Repair 13, and Runtime QA support fixture regressions;
8. full unit suite with passing/pending/failing counts reconciled by exact test
   identity;
9. independent OS/protected-path post-edit comparison against the pre-edit
   baseline.

Known prior unit state was 2298 passing / 1 pending / 2 failing, with unchanged
F1/F3 protected customization failures. Re-derive the live result. Do not edit
those failures or weaken assertions in this task.

REQUIRED FINAL REPORT
Report:
- identity gate;
- exact baseline method and coverage;
- authorized changed paths;
- unauthorized changed paths;
- Decision A field-by-field implementation and test matrix;
- Decision B field-by-field implementation and test matrix;
- negative-control evidence;
- compile/lint/focused/governance/full-suite results;
- F1/F3 exact identities and unchanged/new classification;
- package version/VSIX/install/runtime/Git non-mutation proof;
- remaining findings and honest readiness markers.

Required terminal markers:
IDENTITY_GATE: PASS|BLOCKED
INDEPENDENT_BASELINE_CAPTURED: YES|NO
CREATE_ONLY_VSIX_EXCEPTION_IMPLEMENTED: YES|NO
CREATE_ONLY_VSIX_NEGATIVE_MATRIX_PASS: YES|NO
MISSING_PRODUCER_FAILS_CLOSED: YES|NO
CANONICAL_ACTOR_ALIAS_SELF_CERTIFICATION_BLOCKED: YES|NO
STATIC_CERTIFICATION_TOPOLOGY_VALIDATED: YES|NO
AGENT_AUTHORITY_BROADENED: NO
UNAUTHORIZED_CHANGED_PATHS: NONE|<list>
EXISTING_VSIX_CHANGED: NO
NEW_VSIX_CREATED: NO
PACKAGE_VERSION_CHANGED: NO
EXTENSION_INSTALLED_OR_UNINSTALLED: NO
RUNTIME_QA_STARTED: NO
COMMIT_CREATED: NO
PUSH_EXECUTED: NO
READY_FOR_FRESH_INDEPENDENT_GOVERNANCE_REVIEW: YES|NO

SUCCESS RESULT:
PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
PASS_READY_FOR_FRESH_INDEPENDENT_GOVERNANCE_REVIEW

BLOCKED RESULT:
PACKAGE_LIFECYCLE_GOVERNANCE_REPAIR_RESULT:
BLOCKED_<EXACT_REASON>

STOP RULES
- Stop before editing if identity, authority, or boundary is wrong.
- Stop before partial implementation if a correct result still needs another path.
- Never downgrade a truthful blocker to obtain PASS.
- Never install or run the Extension in this task.
- The next session after a successful implementation must be a genuinely fresh
  independent governance review, not self-review.
```

---

## Expected next session after PASS

If and only if the implementation session ends with the success marker, open a new session with a different source-governance reviewer. The reviewer must be read-only, re-derive identity and baselines independently, run the adversarial and checkpoint suites, inspect all eight diffs, and refuse to certify any implementation/session it cannot distinguish from its own authority.

