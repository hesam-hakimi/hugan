READ-ONLY INVESTIGATION. Do not compile, run tests, launch a runner or
Extension Host, install anything, or edit any file. Report only.

PART A — confirm or refute each item purely by reading current files.
For each, quote the relevant lines and answer CONFIRMED, REFUTED, or
CANNOT_DETERMINE_STATICALLY:

1. In src/test/suite/sttmRealHostStructuredResult.test.ts, the parser
   export is replaced before the restore function is returned, leaving a
   window in which a setup failure can leave the wrapper installed. Show
   the assignment, the return, and where the caller's try/finally begins.
2. In src/test/suite/index.ts, the loader globs all integration test
   files and relies on Mocha grep rather than exclusive module loading.
3. Host evidence is written only in suiteTeardown, after assertions can
   fail, so an early validation failure produces no retained evidence.
4. A failed evidence write yields exit code 1 with no machine-readable
   distinction between an infrastructure failure and a product failure,
   and no parent post-exit check exists.
5. src/test/runTest.ts enforces an exactly-eight-record manifest.

PART B — assertion-strength inventory.
Across src/test/**, list every assertion that inspects a composed source
or target label string. For each, give file:line, the assertion, and
classify its strength as one of:
  EXACT_EQUALITY | SUFFIX_ONLY | PREFIX_ONLY | SUBSTRING_ONLY | OTHER
Then state which of these are structurally incapable of detecting a
missing middle component in a dot-joined label.

PART C — encoding.
Identify where the structured payload is serialized, and report whether
any field in it can carry non-ASCII text. State whether a
byte-length-equals-character-length assumption is safe for a future
oracle.

Report findings only. Do not propose or apply fixes, and do not assert
any PASS, FAIL, or BLOCKED judgment.
