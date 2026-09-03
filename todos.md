READ-ONLY INVESTIGATION. Do not compile, run tests, launch a runner or
Extension Host, install anything, package anything, or edit any file.
Report findings only. Do not assert PASS, FAIL, or BLOCKED, and do not
propose or apply a fix.

Compare two activation routes of this extension:

  Route A: the opted-in ExtensionMode.Test read-only tool-only route
           (ETL_TEST_READ_ONLY_TOOL_ONLY=1)
  Route B: normal installed-VSIX activation used by @etl /workflow

PART 1 — activation diff
Starting at src/extension.ts activate(), produce an ordered list of every
initialization step in each route. Mark each step PRESENT_IN_A,
PRESENT_IN_B, or BOTH. Quote the exact conditionals that cause any
divergence, with file:line.

PART 2 — tool registration
For etl_interpret_sttm specifically:
  a. Where is it registered in each route? Quote both call sites.
  b. Is the same handler implementation used in both? Answer YES or NO
     and show the evidence.
  c. Does anything about registration order, timing, or the set of other
     registered tools differ between the routes?

PART 3 — the structured DataPart, end to end
Trace every code path from the tool handler entry to the constructed
LanguageModelToolResult.
  a. Enumerate every place a LanguageModelDataPart is constructed or
     appended, with file:line.
  b. For each, list every condition that could cause it to be skipped,
     omitted, or replaced by a text-only result. Quote each guard.
  c. For each such condition, state whether it can be satisfied in
     Route A, Route B, both, or neither — and why.
  d. Report specifically whether any of these depend on: the host API
     surface actually present at runtime, chat participant state, model
     availability, authentication, workspace trust, configuration
     values, or activation events. Quote the relevant checks.

PART 4 — packaging
Is anything on the DataPart construction path affected by how the
extension is packaged rather than how it is run — bundling, tree
shaking, .vscodeignore exclusions, dependency externalization, activation
events declared in package.json, or engine/API version constraints?
Quote package.json and any bundler configuration present.

PART 5 — bounds
State plainly which parts of the Route B behaviour are NOT determinable
from source alone and would require runtime observation. Be explicit
about what static reading cannot settle here.
