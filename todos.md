READ-ONLY INVESTIGATION. No edits, no compile, no test execution.

Confirm or refute each of the following purely by reading the current
files. For each, quote the relevant lines and answer CONFIRMED,
REFUTED, or CANNOT_DETERMINE_STATICALLY:

1. In sttmRealHostStructuredResult.test.ts, the parser export is
   replaced before the restorer is returned, leaving a window in which a
   setup failure can leave the wrapper installed. Show the exact
   assignment, the return, and where the caller's try/finally begins.
2. In src/test/suite/index.ts, the loader globs all integration test
   files and relies on Mocha grep rather than exclusive module loading.
3. Host evidence is written only in suiteTeardown, after assertions can
   fail, so early validation failures produce no retained evidence.
4. A failed evidence write yields exit code 1 with no machine-readable
   infrastructure-versus-product classification, and no parent
   post-exit check is implemented.
5. runTest.ts enforces an exactly-eight-file manifest.

Also report: does the DataPart payload construction guarantee ASCII-only
content? The retained observation records 24,186 bytes decoding to
24,186 characters. Identify any field in the serialized structure that
could contain non-ASCII text and would break a byte-length-equals-
character-length assumption in a future oracle.
