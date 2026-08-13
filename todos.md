TASK: LOCAL-PHASE-A1B-CONTRACT-EXTRACTION-AUDIT-20260813-01

Mode: strictly read-only authoritative contract extraction.
Use the current shared workspace, but approach the task as a fresh independent agent.

Current checkpoint:
- Slice 1 repair independently passed.
- Test registration independently passed.
- The combined review card is NOT safe to Keep because it still contains the unaccepted nine-file A0R overlay.
- Phase-H baseline staleness is a separate pre-existing governance blocker.
- Slice 2 has not started.

NON-NEGOTIABLE SAFETY RULES

1. Before analysis, revalidate:
   - repository root and origin;
   - branch and HEAD;
   - registered worktrees;
   - staged state;
   - exact dirty/untracked path manifest;
   - current Slice-1 files;
   - protected user-owned files;
   - candidate and installed VSIX identity.

2. Do not:
   - edit, create, delete, rename, or format any file;
   - click Keep or Undo;
   - stage, commit, push, merge, rebase, switch branches, stash, or modify PR/CI;
   - build, package, install, or modify a VSIX;
   - regenerate Phase-H/evaluation baselines;
   - touch any Consumer workspace or external system;
   - start or implement Slice 2.

3. Do not resolve contracts using:
   - majority or frequency of current implementations;
   - whichever producer is easiest to reuse;
   - examples, fixtures, sample repositories, test data, OCR text, or documentation examples;
   - customer-specific names or conventions.

4. Do not infer:
   - credentials;
   - physical storage values;
   - environment values;
   - write mode;
   - merge keys;
   - onboarding IDs;
   - deployment or business decisions.

OBJECTIVE

Extract the authoritative structural ETL Framework contracts required before Slice 2 can delegate existing path producers to the canonical layout owner.

STTM remains the functional source of truth, but do not assume that STTM defines repository directory and filename conventions unless explicit evidence proves it.

CONTRACT AREAS TO EXTRACT

A. PRIMARY JOB CONFIG

Determine the authoritative path and naming grammar, including the current conflict between conventions such as:

- conf/jobs/..._config.json
- job_conf/...json

Determine whether these represent:

- competing contracts;
- CREATE versus UPDATE behavior;
- legacy versus current behavior;
- different artifact families;
- or an implementation defect.

For UPDATE, explicitly determine whether an existing managed path must be preserved unless a separately approved migration is requested.

B. ENVIRONMENT CONFIG

Extract the authoritative contract for:

- directory;
- filename;
- environment segment;
- process/job identifier;
- `.yaml` versus `.yml`;
- CREATE, UPDATE, reuse, shared, and environment-specific behavior.

The three existing producer conventions must be evaluated independently. Do not select one based on prevalence.

C. TRANSFORMATION ARTIFACTS

Determine whether the following are truly competing representations or distinct artifact kinds:

- executable transformation `.sql`;
- HOCON/YAML include or module configuration;
- transformation SQL suggestion paths.

For every proven artifact kind, extract:

- responsibility;
- path grammar;
- filename grammar;
- required inputs;
- lifecycle applicability;
- relationship to job/module configuration.

Do not collapse SQL and include configuration into one artifact merely because both concern transformation.

D. FAMILIES WITHOUT A CURRENT AUTHORITATIVE PRODUCER

Investigate:

- common/shared configuration;
- declared tabular output;
- managed-ownership marker.

For each, determine whether it is:

- mandatory;
- optional;
- externally owned;
- derived in a later phase;
- represented through another artifact;
- intentionally absent;
- or genuinely missing from the contract.

Do not invent a path for any family lacking authority.

EVIDENCE SOURCES

Inspect read-only:

- current Consumer ETL Framework contracts and schemas;
- production Framework source;
- Framework tests that assert external contracts;
- generic packaged templates and assets;
- Extension contracts, production source, and tests;
- onboarding, environment, include, SQL, writer, and output schemas;
- neutral real-consumer evidence, if available and safe to inspect read-only.

For every source, label it as one of:

- NORMATIVE_CONTRACT
- CURRENT_RUNTIME_BEHAVIOR
- LEGACY_COMPATIBILITY
- CORROBORATING_CONSUMER_EVIDENCE
- DOCUMENTATION_ONLY
- EXAMPLE_OR_FIXTURE

Examples, fixtures, sample names, and observed frequency cannot establish product truth.

Names including CD Renewal, cd_renewal, acz0004, cz_acz0004_retail, renewal, and sample_sttm must never become defaults or contract evidence.

CLASSIFICATION RULE

For every contract and sub-contract, return exactly one:

1. PROVEN
   - An authoritative rule is established.
   - State its exact grammar, required inputs, applicability, provenance, and competing evidence.
   - Explain why competing behavior is legacy, context-specific, or defective.

2. CONFLICTING_EVIDENCE
   - Multiple authoritative sources disagree.
   - Enumerate every conflict.
   - Do not select one.

3. NO_AUTHORITATIVE_EVIDENCE
   - Only implementation accidents, incomplete documentation, fixtures, or examples exist.
   - Do not invent a rule.

4. INCONCLUSIVE
   - Required authoritative material could not be inspected.
   - State the exact missing evidence and blocker.

IMPORTANT DISTINCTIONS

- Incomplete discovery is not equivalent to no match.
- Existing managed path preservation and new-repository path creation may have different contracts.
- A transformation SQL file and a transformation include file may be distinct artifact families.
- An observed runtime convention is not automatically a normative contract.
- Producer count, test count, or current prevalence is not authority.
- Do not silently combine conflicting sources.

WHO MAKES THE DECISION?

If a contract is PROVEN:
- record it;
- do not ask the user;
- do not implement it yet.

If it is CONFLICTING_EVIDENCE or NO_AUTHORITATIVE_EVIDENCE:
- do not guess;
- produce a MAINTAINER_DECISION_PACKET for the maintainer/product owner.

The packet must include:

1. exact unresolved question;
2. 2–3 viable options;
3. authoritative and non-authoritative evidence for each;
4. backward-compatibility impact;
5. migration impact for existing managed repositories;
6. CREATE/UPDATE/INITIALIZE consequences;
7. safety and collision implications;
8. recommended option only if evidence supports a recommendation;
9. the exact short question the maintainer must answer;
10. what remains blocked until that decision is made.

Do not ask an ordinary Extension consumer to choose structural Framework conventions.

A runtime consumer may later be asked only for genuinely workload-specific values explicitly required by an already-established contract.

REQUIRED OUTPUT

1. Repository identity and immutability report.
2. Authority hierarchy actually used.
3. Contract evidence matrix with exact file and symbol citations.
4. Separate classifications for every contract/sub-contract.
5. List of PROVEN contracts ready to become future Slice-2 inputs.
6. Minimal MAINTAINER_DECISION_PACKET containing only unresolved decisions.
7. Explicit statement whether Slice 2 is:
   - READY_AFTER_MAINTAINER_APPROVAL;
   - BLOCKED_BY_CONTRACT_DECISIONS;
   - or BLOCKED_BY_MISSING_EVIDENCE.
8. Confirmation that Keep/Undo, Git, PR, CI, VSIX, Phase-H, Consumer workspaces, and all files remained untouched.

Do not implement anything after reporting.

End with exactly one:

LOCAL_PHASE_A1B_CONTRACT_EXTRACTION_PROVEN
LOCAL_PHASE_A1B_CONTRACT_EXTRACTION_MAINTAINER_DECISION_REQUIRED
LOCAL_PHASE_A1B_CONTRACT_EXTRACTION_NO_AUTHORITY
LOCAL_PHASE_A1B_CONTRACT_EXTRACTION_INCONCLUSIVE
LOCAL_PHASE_A1B_CONTRACT_EXTRACTION_BLOCKED_IDENTITY_MISMATCH
