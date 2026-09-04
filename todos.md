# ETL\-0904\-REVIEW02A — Independent Classification and Evidence Review

Run this prompt in a fresh local VS Code Agent chat with a reviewer that did not implement `ETL-0904-IMPL04` and did not perform its same\-session self\-review\. Use a strong review model in the normal local engineering environment\. You are not the ETL Orchestrator\.

## 1\. Task and authorization boundary

Perform an independent, read\-only source review of the already\-existing combined `ETL-0904-IMPL04` diff, limited to:

- `B3` — failure classification, accumulation, and precedence;
- `M2` — post\-exit verification and evidence\-write failure behavior; and
- `M3` — evidence\-path authorization timing and containment\.

This review authorizes only read\-only identity, status, source, diff, local\-history, and immutable\-artifact inspection needed to review those three requirements\.

Do not:

- edit, format, save, stage, reset, restore, checkout, commit, push, merge, or otherwise mutate any file or Git state;
- press or invoke `Keep`, `Undo`, or any pending\-chat edit action;
- run type\-check, compile, test, parser, runner, Extension Host, package, install, activation, or consumer\-workspace commands;
- review or certify `B1`, `B2`, `B4`, `M1`, `M4`, `M5`, `C1`, `C2`, the 11\-path policy list, or release readiness;
- treat the implementing Agent’s self\-review, screenshots, or report as independent evidence; or
- repair anything you find\.

If you implemented or self\-reviewed `ETL-0904-IMPL04`, stop with:

`ETL_0904_REVIEW02A_RESULT: BLOCKED_REVIEWER_NOT_INDEPENDENT`

## 2\. Re\-derive identity before review

Independently confirm all of the following before inspecting conclusions:

- Active worktree: `C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147`
- Linked primary worktree: `C:\repos\etl-extension\etl_framework_extension_hf1_v2`
- Branch: `fix/workspace-write-completion-0.3.148`
- HEAD: `45c945b4a7d2866fa79e67f0bcf3ac3ae32b9c19`
- Manifest version: `0.3.147`
- Extension identifier: `td-etl.databricks-etl-copilot`

The expected logical working\-tree inventory after the already\-executed combined task is:

```text
 M .github/templates/request.md
 M src/core/sttm/SttmUnderstandingReportRenderer.ts
 M src/extension.ts
 M src/test/runTest.ts
 M src/test/suite/index.ts
?? src/test/suite/sttmRealHostStructuredResult.test.ts
```

Re\-derive this inventory; do not accept it as proof\. Also confirm that the staging index is empty and that no `index.lock` or equivalent active mutation indicator exists\.

If identity or inventory differs materially, stop with:

`ETL_0904_REVIEW02A_RESULT: BLOCKED_BASELINE_DRIFT`

Report the exact observed difference\. Do not repair it\.

## 3\. Recover the exact pre\-`IMPL04` baseline

The review must compare the current `src/test/runTest.ts` against the exact state immediately before `ETL-0904-IMPL04`, not merely against `HEAD`\.

Recover that baseline from VS Code local history, a retained immutable snapshot, or another provenance\-bearing artifact that can be tied to the pre\-task state\. Record the artifact identity, timestamp/version, path, and cryptographic digest if available\.

Do not assume `HEAD` is the baseline: `src/test/runTest.ts` was already dirty before `IMPL04`\.

If the exact pre\-task baseline cannot be recovered, stop with:

`ETL_0904_REVIEW02A_RESULT: BLOCKED_BASELINE_UNRECOVERABLE`

Do not infer the diff from screenshots or the implementing Agent’s narrative\.

## 4\. Evidence discipline

Treat the following as `REPORTED`, not verified facts:

- the reported `+416/-113` across three files;
- the implementing Agent’s eight self\-found defects and claimed corrections;
- its claims of zero unauthorized edits, preserved hashes, empty staging, and clean whitespace;
- its claim that `B3`, `M2`, and `M3` are closed; and
- any screenshot text calling the same\-session review “independent\.”

For every finding, cite the current file path and exact line/symbol, plus the matching pre\-`IMPL04` baseline location\. Distinguish direct source evidence from Agent claims\.

## 5\. Review `B3` — classification, accumulation, and precedence

Establish whether the current implementation makes all of these properties explicit and falsifiable:

1. The formal qualification verdict and the observation/failure ledger are separate data\.
2. Classification precedence is exactly `evidence-write` → `infrastructure` → `product`, with the formal run verdict rules applied consistently; explain any distinction between classification labels and verdict precedence\.
3. A `product` failure can be promoted only after the product\-observation boundary has actually been reached\.
4. Failures accumulate instead of being overwritten by later failures\.
5. The same failure cannot be promoted in both an outer catch and finalization\.
6. Process exit code and final verdict are derived from the same final state\.
7. Exit code `1` by itself is not converted into a valid product `FAIL` without the required product evidence\.
8. A retained product mismatch remains visible in the observation ledger even when a later infrastructure or evidence\-write condition makes the formal verdict `BLOCKED`\.

Look specifically for masking, duplicate entries, last\-write\-wins behavior, stage ambiguity, catch/finally races, and a path where a later failure consumes the original cause\.

## 6\. Review `M2` — post\-exit verification and evidence persistence

Establish whether:

1. Parent post\-exit verification is actually invoked on every relevant exit path rather than merely declared\.
2. Pre\-run, host\-run, post\-exit, and evidence\-write failures have distinct stages\.
3. The primary failure is preserved when full evidence cannot be written\.
4. The reduced record is explicitly incomplete and cannot be mistaken for complete or passing evidence\.
5. Reduced evidence is non\-overwriting and exclusive; it cannot overwrite a valid full record or another run’s evidence\.
6. A secondary persistence failure never masks the primary failure\.
7. Unrecoverable evidence\-destination loss produces explicit stderr, a nonzero exit, and an `evidence-write` classification when a record cannot be retained\.
8. The reported “`evidence-write` tier is a no\-op in the full\-write path” cannot cause a full\-write failure to escape classification or produce a misleading verdict\.

Do not accept the existence of declarations or schemas as proof that the post\-exit path executes\.

## 7\. Review `M3` — authorization timing and containment

Establish whether:

1. The isolation root is proven safe before any evidence destination is authorized\.
2. The evidence path is resolved and authorized immediately after the isolation root, early enough that every later gate can emit a reduced failure record\.
3. Authorization is limited to the exact evidence destination and does not broaden write authority\.
4. Every emitted stage accurately describes the point at which the failure occurred\.
5. Repository, installed\-extension, profile, consumer\-workspace, QA workbook, and unrelated temporary paths remain outside the write boundary\.
6. No fallback path silently relocates evidence into an unauthorized location\.

## 8\. Adjacent\-code rule

You may inspect adjacent code only when needed to prove or disprove `B3`, `M2`, or `M3`\. Do not certify adjacent requirements\. In particular:

- do not decide whether the owner\-required target renderer is correct &#40;`B1`&#41;;
- do not certify activation observations, PID parsing, tool\-list authority, parser wrapping, or channel projection &#40;`B2`, `B4`, `M1`, `M5`, `C1`, `C2`&#41;;
- do not ratify the current 11\-path list; the owner policy is to derive the set from every compiled artifact actually loaded by the focused Host run, plus `package.json`; and
- do not treat compile plausibility as a successful type\-check\.

## 9\. Required report

Return a compact but complete report with:

1. reviewer independence statement;
2. re\-derived identity and exact working\-tree inventory;
3. pre\-`IMPL04` baseline provenance;
4. a requirement matrix for `B3`, `M2`, and `M3`, each marked `ACCEPT`, `BLOCKER`, `MAJOR`, `MINOR`, or `UNKNOWN`;
5. exact source citations for every finding;
6. any interaction among the three reviewed requirements;
7. a list of claims left outside scope and explicitly not certified; and
8. one final verdict token\.

Use exactly one of:

```text
ETL_0904_REVIEW02A_RESULT: ACCEPTABLE
ETL_0904_REVIEW02A_RESULT: CHANGES_REQUIRED
ETL_0904_REVIEW02A_RESULT: BLOCKED_BASELINE_UNRECOVERABLE
ETL_0904_REVIEW02A_RESULT: BLOCKED_BASELINE_DRIFT
ETL_0904_REVIEW02A_RESULT: BLOCKED_REVIEWER_NOT_INDEPENDENT
```

Then end with exactly:

```text
FILES_CHANGED_BY_REVIEW: 0
TYPECHECK_COMPILE_OR_TEST_EXECUTED: NO
PARSER_RUNNER_OR_HOST_EXECUTED: NO
GIT_MUTATION_OR_PENDING_EDIT_ACTION: NO
PRODUCT_OR_OTHER_TRANCHE_CERTIFIED: NO
NEXT_GATE_IF_ACCEPTABLE: ETL-0904-REVIEW02B
```

Do not begin `REVIEW02B`, create a repair prompt, or perform any next action in this session\.
