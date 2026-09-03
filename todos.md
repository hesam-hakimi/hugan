READ-ONLY INVESTIGATION. No edits, no compile, no test execution.

In src/**, answer with exact quoted code and line numbers:
1. In SttmMarkdownBundleParser.ts, show the header-recognition table or
   alias map that maps STTM column headings to parsed fields. List every
   heading it recognizes for SOURCE components and every heading it
   recognizes for TARGET components, side by side.
2. Show lines 960-1000 and state precisely whether any branch assigns a
   targetEntity from a 'Target Table Name' column, and if not, what the
   target projection is composed of instead.
3. Do the same for the Excel path in SttmExcelWorkbookParser.ts. State
   whether the two parsers agree on target-component recognition.
4. In generateSyntheticWorkbook.ts, quote the authored target columns.
5. Search the whole repository for any test, fixture, or documentation
   string containing a three-component target of the form
   <db>.<entity>.<field>, and report whether any existing committed test
   asserts a three-component target.

Report findings only. Do not propose or apply a fix, and do not decide
whether this is intended behaviour — that is an owner decision.
