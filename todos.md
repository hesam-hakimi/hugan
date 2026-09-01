Perform a strictly read-only source audit of the runtime artifact-contract mismatch exposed by F5 Phase 1. Do not implement a fix in this turn.

Repository:

C:\repos\etl-extension\etl_fw2\recovery-extension-product-0.3.147

Preflight

Verify:

* branch is fix/workspace-write-completion-0.3.148;
* current full HEAD and subject;
* index and working tree are clean.

Stop if dirty. Do not edit, format, stage, commit, fetch, reset, stash, clean, build, test, package, push, or create a branch.

Observed runtime evidence

The Extension Development Host successfully interpreted the Excel STTM, rendered artifacts, and contained both destinations inside the isolated QA workspace. Validation then reported:

* HOCON job configuration must use .conf or .json, not .yaml;
* data_sourcing_process options.module/method missing or incorrect;
* sourceList missing or empty;
* output strategy undetermined.

Read-only discovery then found an apparent mismatch:

* render guard expects stage-local options.module and options.method;
* packaged data_sourcing_process example omits options;
* packaged example shows stage-local sourceList;
* writer metadata exposes strategy: generic_dataframe_write, but it is unclear whether this is executable content or search metadata;
* no complete canonical executable job envelope was exposed.

Audit

Use rg, git grep, git show, and read-only file inspection to locate and inspect the exact implementation and packaged evidence. Start with these symbols/messages, resolving actual paths dynamically:

* renderJobConfig
* validateArtifacts
* PreWriteValidationPipeline
* etl_get_framework_rules
* etl_describe_module
* etl_search_examples
* job-config-envelope.v1
* data_sourcing_process
* dataframe_writer
* sourceList
* options.module
* options.method
* generic_dataframe_write
* HOCON config must use .json or .conf
* Output strategy could not be determined

Inspect, where present:

* src/tools/EtlActionToolService.ts
* tool registration and handlers under src/tools/**
* validation code under src/**
* packaged rules, module contracts, schemas, and examples under resources/**, src/context_files/**, or equivalent;
* package.json, .vscodeignore, and packaging-copy logic governing which contracts and examples reach the Extension Host.

If the extension loader explicitly references the sibling etl-framework-gen-utils checkout, inspect only the referenced files there and clearly distinguish upstream source from packaged extension content.

Required findings

Produce exact file-and-line evidence for:

1. The authoritative executable job envelope.
2. Permitted job-config extensions and which component chooses or validates the destination.
3. Exact modules.<stage> structure.
4. Exact placement and allowed values of options.module and options.method.
5. Exact sourceList type, placement, and relationship to named source blocks.
6. Exact executable representation of generic_dataframe_write.
7. Whether inline SQL is valid or an include artifact is required.
8. What each runtime discovery tool actually exposes to Copilot.
9. Whether packaged assets differ from their source or are omitted during packaging.
10. Whether the invalid .yaml extension causes the semantic errors to cascade or whether they are independent defects.

Classify the result as exactly one:

* CALLER_INPUT_ONLY
* VALIDATION_CASCADE
* DISCOVERY_CONTRACT_INCOMPLETE
* RENDER_VALIDATOR_CONTRADICTION
* PACKAGING_DRIFT
* MULTIPLE_DEFECTS
* INDETERMINATE

Do not assume the screenshots represent four independent defects.

Minimal-fix recommendation

Without editing, propose the smallest correction with:

* exact files and symbols;
* behavior changed;
* behavior intentionally unchanged;
* whether the authoritative source belongs in this repository or upstream;
* whether generated or packaged copies must be synchronized.

Recommend branch placement:

* If current packaged discovery or renderer/validator parity blocks the accepted W1 runtime gate, recommend a separate narrow commit on the current fix/workspace-write-completion-0.3.148 branch before push.
* If the defect is owned upstream and cannot be correctly fixed here, recommend a dedicated upstream branch and identify the required downstream synchronization.
* Do not create either branch.

Acceptance-test proposal

Specify the narrowest automated tests that would prove:

1. a complete canonical minimal .conf or .json job is discoverable through the public ETL tools;
2. its rendered bytes pass the same validator used by etl_validate_artifacts;
3. data_sourcing_process, non-empty sourceList, and generic_dataframe_write are recognized;
4. invalid .yaml input fails at the correct boundary without misleading downstream semantic errors;
5. existing W1 collision and approval tests remain unchanged.

Also specify the final manual F5 rerun required after implementation.

Return:

* preflight;
* source-of-truth table;
* producer-to-validator trace;
* root cause and classification;
* minimal fix plan;
* proposed tests;
* branch recommendation;
* final clean git status --short.

End with exactly:

RUNTIME_ARTIFACT_CONTRACT_AUDIT_COMPLETE

or:

RUNTIME_ARTIFACT_CONTRACT_AUDIT_BLOCKED
