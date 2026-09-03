READ-ONLY INVESTIGATION. No edits, no compile, no test execution.

Quote the exact current text, with line numbers, of each of these and
explain in one sentence what each one asserts about source/target
string composition:
1. SttmResolvedEvidence.ts, the canonical source-composition logic
   (reported near line 630) including every fallback branch.
2. SttmUnderstandingReportRenderer.ts, the Markdown Active Mappings
   source rendering (reported near line 218).
3. The public tool-result adapter (reported at index.ts:181) — show
   exactly what it adds to and what it copies verbatim from the internal
   service response.
4. package.json, the description or contract string reported at line 574
   containing wording about values being carried identically.
5. sttmPublicToolResultEnvelope.test.ts around line 346, and
   etl-verifier.agent.md around line 35.

Then state, as an observation and not a decision: which artifacts define
parity by mapping ID/order/count, and which artifacts could be read as
requiring byte-identical display strings.
