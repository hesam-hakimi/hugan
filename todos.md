READ-ONLY INVESTIGATION. No edits, no compile, no test execution, no
Extension Host launch.

In src/extension.ts and its activation call graph, produce an ordered
comparison of two activation routes:

Route A: opted-in ExtensionMode.Test read-only-tool-only activation
         (ETL_TEST_READ_ONLY_TOOL_ONLY=1)
Route B: normal installed-VSIX activation used by @etl /workflow

For each route, list in execution order every initialization step, and
mark each step as PRESENT_IN_A, PRESENT_IN_B, or BOTH. Explicitly
identify:
1. Where etl_interpret_sttm is registered in each route, and whether the
   same handler implementation is used in both.
2. Every code path between the tool handler and the constructed
   LanguageModelToolResult, and whether any of those paths differ
   between the two routes.
3. Every place a LanguageModelDataPart is constructed or appended, and
   any conditional that could omit it — including any dependency on
   chat participant state, model availability, authentication, or
   configuration that exists in Route B but not Route A.

Report the diff as findings. Do not conclude that the installed defect
is explained or closed.
