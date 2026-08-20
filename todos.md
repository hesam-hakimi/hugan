LOCAL_HOTFIX_HF1_REPAIR_2 — REMOVE RUNTIME FRAMEWORK-SOURCE DEPENDENCY FOR QA

Purpose

Repair the existing HF1 candidate so that a normal QA tester or end user can install the VSIX and validate Oracle db_data_out / db_ctrl_out artifacts without having access to the etl-framework-adb source repository and without adding that repository to the VS Code workspace.

This task is performed on the isolated HF1 branch:

Repository:
C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1
Branch:
hotfix/hf1-oracle-fresh-consumer
Base HEAD:
b2e44c3a1a051aa7fa6008831d225bc06d22e847

The current HF1 candidate already has 27 authorized changed files.

Current validated state before Repair 2:

Changed files: exactly 27
Staged files: 0
Compile: PASS
Lint: PASS
Focused HF1 tests: 80 passing
Full unit suite: exactly the same 6 pre-existing baseline failures
No seventh failure
External marker:
HF1_EXTERNAL_VALIDATION_PASS

Real affected consumer end-to-end verification remains:

NOT EXECUTED — SAMPLE UNAVAILABLE

The current HF1 candidate must not be discarded or restarted.

⸻

0. ONE CONSOLIDATED AUTHORIZATION REQUEST

Before executing any command or editing a file, request exactly one consolidated authorization covering:

* read-only inspection of the HF1 repository;
* read-only inspection of etl-framework-adb solely to extract a minimal non-sensitive contract;
* modification of only the bounded Repair-2 files described below;
* creation of at most one new versioned machine-readable contract resource under the HF1 Extension repository;
* local compile, lint, and focused tests using already-installed dependencies;
* no installation, download, Git mutation, VSIX publish, or consumer write.

Ask for exactly this token:

APPLY_LOCAL_HOTFIX_HF1_REPAIR_2

After receiving it, do not ask the user for repeated conversational approval for operations already inside this bounded scope.

Host-enforced permission dialogs may still appear and must not be bypassed.

⸻

1. THE ARCHITECTURAL DEFECT

HF1 currently allows Oracle delivery validation through a trusted live framework source.

That is useful for Extension maintainers but is not a valid runtime requirement for QA or normal users.

QA must NOT require:

etl-framework-adb

in their workspace.

QA must NOT require:

databricks-etl-copilot.frameworkRepositoryPath

to point at framework source.

QA must NOT receive framework source code.

The final runtime experience must be:

Install VSIX
→ Open consumer workspace
→ Read STTM
→ Preview
→ Validate
→ Explicit approval
→ Write

and NOT:

Install VSIX
→ Obtain framework source
→ Add etl-framework-adb
→ Configure source path
→ Validate

⸻

2. TARGET ARCHITECTURE

Implement a two-mode framework trust model.

Mode A — normal QA / end-user runtime

Use a versioned packaged trusted framework contract shipped inside the Extension.

No external framework source is required.

Mode B — maintainer/development override

A maintainer may optionally use:

1. a valid explicitly configured framework source root; or
2. a valid explicitly present multi-root etl-framework-adb.

This mode exists only for maintainers/development and live framework compatibility verification.

The resolution precedence must be:

1. non-empty explicitly configured framework root
   → validate
   → if invalid: FAIL CLOSED, do not silently fall back
2. explicitly present multi-root etl-framework-adb
   → validate
   → if invalid: FAIL CLOSED, do not silently fall back
3. packaged trusted framework contract
   → validate packaged contract integrity
   → use for normal QA/end-user validation
4. unavailable

The packaged contract is therefore the default normal-user authority.

Do not scan arbitrary directories.

Do not search the machine for framework repositories.

Do not infer framework source from neighboring folders.

⸻

3. DISTINGUISH THE NEW CONTRACT FROM THE OLD PACKAGED REFERENCE

The existing packaged reference/documentation remains guidance-only.

It must NEVER satisfy validation.

Repair 2 introduces a different artifact:

TRUSTED PACKAGED FRAMEWORK CONTRACT

This is an explicitly curated, machine-readable compatibility interface.

It is allowed to be authoritative because:

* it contains no framework source;
* it contains no executable business code;
* it contains no credentials;
* it contains no environment-specific data;
* it contains only the minimum semantics required by deterministic Extension validation;
* it is versioned and integrity-checked;
* it is shipped as part of the tested Extension.

Do not reuse a documentation file as this contract.

⸻

4. PACKAGED CONTRACT CONTENT

Create one versioned resource, preferably:

resources/framework/contracts/oracle-delivery-controls.v1.json

If current repository/package conventions require a different path, first prove that convention and use the nearest equivalent path.

Do not create multiple contract files.

The contract must contain only minimal, non-sensitive machine metadata required to validate the supported Oracle delivery behavior.

At minimum it must describe, using exact evidence from the read-only framework source:

* schema version;
* stable contract ID;
* contract format version;
* supported framework module type;
* support for db_data_out;
* support for db_ctrl_out;
* exact safe option/control semantics required by Extension validation;
* whether the executable process behavior is required;
* deterministic contract fingerprint/integrity data.

Do NOT place any of the following in the packaged contract:

* source code;
* Python code;
* HOCON source;
* SQL;
* internal comments;
* documentation paragraphs;
* developer usernames;
* machine paths;
* framework repository paths;
* Git URLs;
* credentials;
* connection strings;
* hostnames;
* schemas/tables from real consumers;
* environment names;
* business data;
* framework source filenames unless technically indispensable to runtime validation.

Prefer semantic identifiers over source-file paths.

Do not copy prose from the technical guide into the contract.

⸻

5. CONTRACT EXTRACTION RULE

Use etl-framework-adb only during this maintainer Repair-2 session as read-only evidence.

Independently derive the minimum contract from the same executable/structured evidence already used by HF1.

Documentation may corroborate the interpretation but must not be the only evidence.

Before writing the packaged contract, report internally which source evidence proves each semantic field.

Do not write anything to etl-framework-adb.

Do not generate any artifact inside it.

⸻

6. PACKAGED CONTRACT VALIDATION

Runtime must never trust arbitrary JSON merely because it exists.

Implement deterministic validation of:

* exact schema version;
* exact contract ID;
* closed allowed field set;
* expected module/control identifiers;
* expected value types;
* no unknown executable payload;
* no raw path or environment payload;
* deterministic canonical representation;
* deterministic SHA-256 fingerprint.

If a checked-in expected digest is used, changing the packaged contract must require an intentional code/test update.

Do not use:

JSON.parse → trust

without schema validation.

A missing, malformed, unsupported, or integrity-invalid packaged contract must fail closed.

⸻

7. FRAMEWORK SOURCE KIND

Extend the existing framework provenance/source-kind model to explicitly distinguish at least:

configured_source
workspace_source
packaged_contract

Use existing naming conventions where possible.

When QA uses no framework source:

sourceKind = packaged_contract

The approval manifest must still bind:

* framework source kind;
* contract/framework identity;
* deterministic fingerprint.

Therefore a preview created using one framework authority cannot silently be replayed using another.

⸻

8. BLOCKER SEMANTICS

Preserve existing distinct blockers.

Use:

FRAMEWORK_DEFINITION_UNAVAILABLE

when no valid source or packaged contract exists.

Use:

ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING

when an authority exists but does not prove the required Oracle delivery semantics.

Normal QA installation containing a valid packaged contract must NOT produce either blocker solely because etl-framework-adb is absent.

⸻

9. OPTIONAL SOURCE SETTING

The existing setting:

databricks-etl-copilot.frameworkRepositoryPath

must no longer be required for QA.

If retained, its description must clearly describe it as an optional:

Maintainer/development framework-source override

Normal users should leave it empty.

An empty value means:

try explicit workspace framework source if present
→ otherwise use packaged trusted contract

A non-empty but invalid explicit value must fail closed and must NOT silently use the packaged contract.

This prevents a maintainer configuration mistake from being hidden.

⸻

10. NO QA ACCESS TO FRAMEWORK SOURCE

Add an explicit deterministic test for the real QA topology:

configured framework root: absent
etl-framework-adb workspace folder: absent
consumer workspace: present
packaged contract: present

Expected result:

framework source kind = packaged_contract
Oracle delivery controls = verified
no framework-source blocker

The test must prove that no framework repository filesystem access is required.

Where practical, make any attempted external framework source read fail the test.

⸻

11. PRESERVE HF1 WRITE SECURITY

Repair 2 must not weaken any previous HF1 protection.

All production write routes must still enforce:

validation
→ immutable preview/path manifest
→ explicit approval
→ one-time WriteAuthorization
→ runtime re-verification
→ exactly one write

Preserve protections against:

* missing preview;
* stale preview;
* consumed approval;
* forged authorization;
* wrong workspace;
* changed target;
* changed targetDecision;
* changed artifact type;
* changed path;
* changed artifact bytes;
* changed framework identity;
* changed framework fingerprint.

A change between:

packaged_contract
configured_source
workspace_source

must invalidate the previous approval.

⸻

12. PRESERVE FRESH-CONSUMER BEHAVIOR

Keep:

CREATE_NEW_JOB
UPDATE_EXISTING_REPO
BLOCKED

semantics unchanged.

A valid explicitly selected fresh consumer:

* does not need job_conf/;
* does not need env_conf/;
* does not need a marker before preview;
* does not need etl-framework-adb.

No files may be created before approved write.

⸻

13. PRESERVE CONSUMER ARTIFACT CONTRACT

The existing consumer preview contract must remain unchanged.

The current HF1 tests establish:

12 consumer artifacts

Repair 2 must preserve:

* same artifact set;
* same paths;
* same ordering;
* same bytes.

The packaged framework contract is an Extension resource, NOT a consumer artifact.

It must never:

* become artifact 13;
* be copied into a consumer repository;
* alter a renderer;
* alter a template;
* alter a path builder;
* appear in generated consumer configuration;
* create a marker file.

⸻

14. PACKAGE BOUNDARY

The packaged trusted contract must be included in the resulting VSIX.

The Extension must load it from its own installed package, not from:

* current working directory;
* consumer workspace;
* adjacent repository;
* developer machine path.

Use a path resolution mechanism appropriate for installed VS Code extensions and compatible with the repository minimum VS Code/runtime requirements.

Do not embed an absolute development path.

⸻

15. BOUNDED REPAIR-2 CHANGE ALLOW-LIST

Start with read-only inspection.

Repair 2 may modify only the minimum necessary subset of:

src/core/framework/TrustedFrameworkDefinitionResolver.ts
src/core/framework/FrameworkDiscoveryService.ts
src/core/readiness/JobKnowledgeContract.ts
src/validation/PreWriteValidationPipeline.ts
src/tools/TrustedWriteApprovalStore.ts
src/tools/EtlActionToolService.ts
package.json
src/test/suite/trustedFrameworkDefinitionResolver.test.ts
src/test/suite/hf1OracleFreshConsumer.test.ts
src/test/suite/onboardingWriteApproval.test.ts
src/test/suite/createPreviewFlow.test.ts

and may create only:

resources/framework/contracts/oracle-delivery-controls.v1.json

Do not edit every allow-listed file automatically.

Touch only files proved necessary.

No other source, test, package, workflow, documentation, S-A, S-B, consumer, framework, or control-plane file is authorized.

If another repository file is genuinely required, stop before editing it and report:

LOCAL_HOTFIX_HF1_REPAIR_2_SCOPE_AMENDMENT_REQUIRED

with the exact file and reason.

⸻

16. REQUIRED TESTS

Add executable tests covering at least:

1. QA topology: no configured root + no framework workspace → packaged contract succeeds.
2. QA topology performs no framework-source repository read.
3. Configured valid framework source overrides packaged contract.
4. Configured invalid framework source fails closed and does not fall back.
5. Valid workspace framework source overrides packaged contract.
6. Invalid explicit workspace framework source fails closed.
7. Missing packaged contract with no source returns FRAMEWORK_DEFINITION_UNAVAILABLE.
8. Malformed packaged contract fails closed.
9. Wrong schema version fails closed.
10. Unknown packaged-contract field fails closed if contract schema is closed.
11. Integrity/fingerprint mismatch fails closed.
12. Packaged contract lacking Oracle semantics returns ORACLE_DELIVERY_CONTROL_DEFINITION_MISSING.
13. Valid packaged contract permits db_data_out.
14. Valid packaged contract permits db_ctrl_out.
15. Framework source-kind change after preview invalidates approval.
16. Packaged-contract fingerprint change invalidates approval.
17. Consumer artifact set remains exactly 12.
18. Consumer artifact paths/order/bytes remain unchanged.
19. Packaged contract never becomes a consumer artifact.
20. Fresh consumer reaches CREATE_NEW_JOB without framework source.
21. No write occurs before approval.
22. Exactly one write occurs after valid approval.
23. Existing HF1 bypass protections remain intact.

Do not weaken or delete existing tests.

⸻

17. VALIDATION EXPECTATIONS

The previous external baseline is:

Compile: PASS
Lint: PASS
Focused HF1 tests: 80 passing
Full unit suite:
exactly 6 known pre-existing failures
no seventh failure

Repair 2 must not change the identity of those six failures.

If native execution is unavailable in this Copilot session:

* do not fabricate validation;
* provide exact PowerShell commands for human execution;
* report implementation as awaiting external validation.

Do not install dependencies.

Do not download tooling.

Do not package or install VSIX during this Repair-2 implementation task.

⸻

18. PACKAGE VERIFICATION REQUIREMENT FOR THE NEXT STEP

After Repair 2 is externally validated, a new QA VSIX will be produced.

That package must prove:

* packaged contract exists inside the VSIX;
* no etl-framework-adb source exists inside the VSIX;
* no framework source code is included;
* .tsbuildinfo.test absent;
* tsconfig.test.json absent;
* src/test/** absent;
* out/test/** absent;
* docs/eval/** absent;
* required runtime bundles present;
* packaged Copilot resources present.

Do not perform that packaging inside this task.

⸻

19. REQUIRED FINAL REPORT

Return:

1. Exact files changed in Repair 2.
2. Exact new contract resource.
3. Exact packaged-contract schema.
4. Evidence-to-contract mapping showing that every contract field came from executable/structured framework evidence.
5. Confirmation that no source code or sensitive value entered the contract.
6. Final resolver precedence.
7. QA runtime flow with zero framework-source access.
8. Maintainer override flow.
9. Failure/blocker matrix.
10. Approval drift behavior.
11. Test additions and updates.
12. Attempted validation commands and actual results.
13. Any remaining limitation.
14. Confirmation that etl-framework-adb was read-only.
15. Confirmation that no consumer repository was written.
16. Confirmation that the existing 12-artifact contract remains unchanged.

The implementation chat may not authorize Keep.

Finish with exactly one marker:

LOCAL_HOTFIX_HF1_REPAIR_2_COMPLETE

if implementation and available validation succeeded;

or:

LOCAL_HOTFIX_HF1_REPAIR_2_IMPLEMENTED_AWAITING_EXTERNAL_VALIDATION

if code/tests are complete but native validation must be run externally;

or:

LOCAL_HOTFIX_HF1_REPAIR_2_BLOCKED

if the repair cannot be completed within the authorized scope.

Do not Keep.
Do not commit.
Do not push.
Do not package.
Do not install a VSIX.
Do not start an independent audit.
Stop after the Repair-2 report.
