TASK: HF1 V2 QA BLOCKER RESOLUTION — READ-ONLY CONTRACT DISCOVERY

We are continuing HF1 V2 runtime QA for Databricks ETL Copilot 0.3.140.

Phase 1 successfully reached real runtime preview planning in the isolated fresh consumer workspace, but deterministic validation blocked before Preview ID creation with exactly two unresolved contract questions:

1. What is the exact top-level module-list/envelope key and HOCON shape expected by the deployed ETL Framework job config?

2. Does dataframe_writer support writing directly to a Unity Catalog table by name (for example table.name = curated.qa_hf1v2_customer), or is it strictly path-based / ADLS-path-based?

This task is READ ONLY.

Do NOT:
- create or modify any workspace files
- execute approval
- execute write
- change STTM
- change package files
- modify .github/**
- access or modify a real consumer repository
- use etl-framework-adb
- guess syntax
- infer from prose if deterministic packaged/runtime evidence exists

Use only the installed 0.3.140 extension runtime, packaged framework contracts, packaged module references, deterministic ETL tools, and other read-only evidence available in this workspace.

First inspect:
- etl_get_framework_rules
- etl_describe_module for dataframe_writer and any required parent/module container
- packaged resources/framework/**
- packaged resources/copilot/**
- rendered HOCON schema or validation logic if exposed read-only
- any packaged canonical job_conf examples if they exist
- validator error definitions responsible for:
  "No modules detected in job config"
  "Confirm output path or table"

For question 1, return:
- exact root key name
- exact nesting shape
- exact minimal valid HOCON skeleton
- whether module entries are list/object/map based
- evidence source
- confidence: PROVEN / INFERRED / UNKNOWN

For question 2, return:
- supported dataframe_writer destination modes
- whether Unity Catalog table-name output is supported
- exact field name(s), if supported
- whether catalog.schema.table or table.name is expected
- whether path is mandatory
- evidence source
- confidence: PROVEN / INFERRED / UNKNOWN

Then classify whether Phase 1 can resume without any product/source-code change.

Return exactly these markers:

TOP_LEVEL_MODULE_ENVELOPE_PROVEN: YES/NO
TOP_LEVEL_MODULE_ENVELOPE_KEY: <value or UNKNOWN>
UNITY_CATALOG_TABLE_WRITE_SUPPORTED: YES/NO/UNKNOWN
UNITY_CATALOG_TARGET_FIELD: <value or UNKNOWN>
PATH_REQUIRED_FOR_DATAFRAME_WRITER: YES/NO/UNKNOWN
PRODUCT_DEFECT_FOUND: YES/NO
PACKAGE_CONTRACT_GAP_FOUND: YES/NO
QA_CAN_RESUME_WITHOUT_CODE_CHANGE: YES/NO

If both contract questions are PROVEN from packaged/runtime evidence, also provide the exact minimal corrected render inputs needed to resume Phase 1, but DO NOT execute rendering, preview, approval, or write.

End exactly with one of:

HF1_V2_QA_CONTRACT_DISCOVERY: PASS
HF1_V2_QA_CONTRACT_DISCOVERY: BLOCKED
HF1_V2_QA_CONTRACT_DISCOVERY: FAIL
