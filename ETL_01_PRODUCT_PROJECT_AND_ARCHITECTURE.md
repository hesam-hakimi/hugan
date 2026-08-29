# ETL Framework Extension — Product, Project, and Architecture

## 1. What “ETL FW” means

The **Consumer ETL Framework** is a configuration-driven Databricks execution framework. It turns governed consumer artifacts into an executable ETL pipeline. Its inputs and contracts include:

- STTM mappings and metadata;
- job configuration;
- environment/shared configuration;
- nested includes and substitutions;
- transformation SQL or module settings;
- source, transformation, load/enrichment, and writer modules;
- onboarding/registration metadata;
- runtime parameters;
- provider-specific destination behavior.

A typical logical flow is:

```text
source/sourcing
→ transformation
→ load or enrichment
→ writer/output
```

The Framework is not the chat UI and it is not the VS Code extension. It owns the executable ETL grammar and runtime behavior.

## 2. What this project is

The project is the **Databricks ETL Copilot Extension**, distributed as a VSIX with Extension ID:

```text
td-etl.databricks-etl-copilot
```

It integrates VS Code and GitHub Copilot Agent Mode through `@etl`, `/workflow`, installed ETL tools, trusted packaged contracts, and consumer-local Agents. It is the control plane around the Framework.

The Extension owns:

- selected-workspace resolution;
- consumer/repository classification;
- STTM interpretation;
- evidence gathering;
- machine-authoritative contract resolution;
- target decision: create, update, initialize/scaffold, ask, or block;
- in-memory artifact rendering;
- deterministic validation;
- exact zero-write Preview;
- trusted explicit approval;
- guarded filesystem writes;
- managed ownership and audit records;
- repair, upgrade, package verification, and Runtime QA support.

Normal consumer operation must not require an `etl-framework-adb` source checkout. The trusted Framework contracts and required examples must resolve from the installed VSIX/package.

## 3. Product boundary model

| Scope | Canonical location | Authority |
|---|---|---|
| Maintainer control plane | Extension source `.github/**`, `AGENTS.md`, governance files | Maintainer-only and protected unless explicitly authorized |
| Packaged product guidance | `resources/copilot/**` | Generated Agents, prompts, skills, instructions, and advisory context |
| Machine Framework contracts | `resources/framework/contracts/**` | Integrity-validated runtime authority |
| Runtime implementation | `src/**` | Deterministic target, validation, Preview, approval, write, and provider behavior |
| Consumer workspace | Explicit selected root | Consumer inputs and approved generated artifacts |
| Consumer workflow assets | Consumer `.github/**` and context assets | Generated/customized product assets; advisory unless trusted runtime says otherwise |
| Automated write-test roots | Unique disposable OS temp roots | The only test write surface |

Relative paths and folder names do not establish authority. Every read/write decision must be bound to an exact canonical root.

## 4. Environment terminology

| Term | Meaning |
|---|---|
| Software Development Environment | The Extension source checkout where TypeScript, resources, tests, package policy, and VSIX packaging are developed |
| Development Test Workspace | A disposable or copied consumer-shaped workspace used for product tests; it is not SIT or production |
| SIT | A later controlled integration environment; not reached in this workstream |
| Production | Live workload/data environment; not authorized |
| `0.3.xxx` | Internal development/test candidate versions |
| `1.x` | Intended public/general-release family |

A copy of a real consumer repository remains a Development Test Workspace when isolated and not merged or deployed.

## 5. Consumer artifact model

The Extension may propose or manage:

- `job_conf/**` job configuration;
- `env_conf/**` environment configuration;
- referenced include files;
- transformation SQL;
- onboarding/registration assets;
- generated consumer Agents, skills, prompts, and instructions;
- advisory context needed by the consumer workflow.

For a fresh create flow:

- default environment is `dev` unless explicitly changed;
- ask whether an environment config already exists;
- reuse a supplied existing env config;
- create one only when the user says it does not exist or the trusted route proves it is required;
- validate job parsing and substitution resolution with the Framework-compatible contract;
- generate every deterministically referenced include/transformation artifact;
- keep Bitbucket/repository-first promotion semantics for higher environments;
- do not update an SQL configuration table in the MVP path;
- do not upload to development DBFS until separately approved.

The early V1 target covered bronze/source ingestion, transformation, Delta silver/gold, and Synapse-related output patterns. The broader provider strategy catalog now includes:

```text
curated_load_enrich
generic_dataframe_write
database_out
tibco_out
bulk_delta_copy
```

Each provider still needs its own authoritative field contract and runtime proof. Local workspace write safety must not be confused with data-plane provider support.

## 6. Canonical job configuration

The machine-authoritative job envelope is stage-keyed HOCON:

```hocon
modules {
  source_stage {
    ...
    options {
      module = data_sourcing_process
      method = process
    }
  }

  writer_stage {
    ...
    options {
      module = dataframe_writer
      method = process
    }
  }
}
```

Key invariants:

- `modules` is an object, not an array;
- entries are keyed by stage name;
- module type is `options.module`;
- method is `options.method`;
- unsupported envelopes fail before Preview;
- consumer-editable context cannot redefine this grammar.

The currently proven positive writer scenario is path-backed Delta with append. A direct Unity Catalog target such as `catalog.schema.table` is not supported by the current Framework version and must produce:

```text
UNSUPPORTED_UNITY_CATALOG_TARGET
```

## 7. Target decision rules

| Observed state | Required decision |
|---|---|
| Exactly one managed matching job | `UPDATE_EXISTING_JOB` or managed update route |
| No match in a confirmed consumer repo | `CREATE_NEW_JOB` |
| Valid empty consumer repo | `INITIALIZE_NEW_CONSUMER_REPO`, then create |
| Zero roots | Block: `no_workspace` |
| Multiple roots without explicit trusted selection | Block: `ambiguous` |
| Invalid explicit root | Block: `explicit_invalid` |
| Extension/Framework/reference/sample root | Block |
| Unmanaged collision or unknown authority | Ask or fail closed |

“No matching job” is never evidence that the Framework source repository is required.

