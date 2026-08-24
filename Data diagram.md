1. Core Structural Entities

Product Group

```text
Product Group
────────────────────────
Product Group ID (PK)
Name
Description
```

Schema

```text
Schema
────────────────────────
Schema ID (PK)
Product Group ID (FK)
Name
Description
```

Dataset

```text
Dataset
────────────────────────
Dataset ID (PK)
Schema ID (FK)
Data Source ID (FK)
Name
Description
Grain
Dataset Type
```

Field / Column

```text
Field / Column
────────────────────────
Field ID (PK)
Dataset ID (FK)
Name
Data Type
Description
Is Key (Y/N)
```

Relationship

```text
Relationship
────────────────────────
Relationship ID (PK)
From Dataset ID (FK)
To Dataset ID (FK)
Relationship Type
Cardinality
Description
```

────────

2. Business Semantic Entities

Business Term

```text
Business Term
────────────────────────
Business Term ID (PK)
Name
Definition
Business Glossary Reference
Synonyms
```

KPI / Metric

```text
KPI / Metric
────────────────────────
KPI ID (PK)
Name
Definition
Calculation Logic
Unit
Owner
```

Recipe / Calculation

```text
Recipe / Calculation
────────────────────────
Recipe ID (PK)
Name
Description
Logic / Formula
Version
Status
```

────────

3. Governance Entities

Governance Metadata

```text
Governance Metadata
────────────────────────
Metadata ID (PK)
Dataset / Field Reference
Classification
Sensitivity Level
PII (Y/N)
PCI (Y/N)
Retention Policy
Data Owner
Steward
Freshness
Lifecycle
```

Authorization Scope

```text
Authorization Scope
────────────────────────
Scope ID (PK)
Entity / Dataset Reference
Role / Group
Permission Type
Access Level
Description
```

MVP note:

```text
Current MVP:
- Entity-level authorization

Future:
- Dataset-level authorization
- Column-level authorization
- Row-level scope
```

Registry Version

```text
Registry Version
────────────────────────
Registry Version ID (PK)
Version Number
Status
Effective From
Effective To
Change Summary
```

Conceptual meaning:

```text
Registry Version represents an immutable
governed semantic snapshot covering:

- Product Groups
- Schemas
- Datasets
- Fields
- Relationships
- Business Terms
- KPIs
- Recipes
- Governance Metadata
```

────────

4. Source Mapping

Data Source

```text
Data Source
────────────────────────
Data Source ID (PK)
Name
Source Type
Platform / System
Environment
Owner
```

SQL Server / Azure SQL

```text
SQL Server / Azure SQL
────────────────────────
Relational Source
Database
Schema
Tables / Views
```

Status:

```text
Current / Supported
```

Databricks

```text
Databricks
────────────────────────
Analytical Source
Catalog (when available)
Schema
Tables / Views
Governed Delta Data
```

Status:

```text
Planned / Integration Option
```

Future Approved Source

```text
Future Approved Source
────────────────────────
Provider-Specific Source
Provider-Specific Metadata
Provider-Specific Physical Model
```

Status:

```text
Future / Optional
```

────────

5. Relationships to Draw in Visio

Use these relationships as the main diagram connections.

────────

From              Relationship      To                Cardinality / Note

────────

Product Group     contains          Schema            1-to-many

Schema            contains          Dataset           1-to-many

Dataset           contains          Field / Column    1-to-many

Dataset           participates in   Relationship      1-to-many

Relationship      connects          Dataset           Dataset-to-Dataset
governed
relationship

Business Term     describes         Dataset           many-to-many
conceptually

Business Term     describes         Field / Column    many-to-many
conceptually

KPI / Metric      uses              Dataset           many-to-many
conceptually

KPI / Metric      uses              Field / Column    many-to-many
conceptually

KPI / Metric      implemented by    Recipe /          1-to-many or
Calculation       governed association

Recipe /          uses              Dataset           many-to-many
Calculation                                           conceptually

Recipe /          uses              Field / Column    many-to-many
Calculation                                           conceptually

Recipe /          uses              Relationship      governed association
Calculation

Governance        classifies /      Dataset           1-to-many
Metadata          governs                             conceptually

Governance        classifies /      Field / Column    1-to-many
Metadata          governs                             conceptually

Authorization     permits access to Entity / Dataset  MVP is entity-level
Scope

Registry Version  versions          Governed Semantic snapshot-level
Model             relationship

Dataset           maps to           Data Source       many datasets to one
source

Data Source       implemented by    SQL Server /      provider option
Azure SQL

Data Source       implemented by    Databricks        provider option

Data Source       implemented by    Future Approved   provider option Source

────────

6. Recommended Visio Layout

Arrange the main structural hierarchy horizontally at the top:

```text
Product Group
     │
     │ 1-to-many
     ▼
Schema
     │
     │ 1-to-many
     ▼
Dataset
     │
     │ 1-to-many
     ▼
Field / Column
```

In the actual Visio page, rotate this into a horizontal presentation if
desired:

```text
Product Group  →  Schema  →  Dataset  →  Field / Column
```

Place the semantic/business entities to the right of Dataset / Field:

```text
                         ┌─ Relationship
                         │
Dataset / Field ─────────┼─ Business Term
                         │
                         ├─ KPI / Metric
                         │      │
                         │      ▼
                         └─ Recipe / Calculation
```

Place governance entities below Dataset:

```text
                  Dataset
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
Authorization   Registry       Governance
Scope           Version        Metadata
```

Place source mapping below the structural model:

```text
Dataset
   │
   ▼
Data Source
   │
   ├───────────────┬────────────────┐
   ▼               ▼                ▼
SQL Server      Databricks       Future
/ Azure SQL                       Source
```

────────

7. Suggested Visual Groups / Containers

Create four Visio containers:

```text
CORE DATA STRUCTURE
Product Group
Schema
Dataset
Field / Column
Relationship
```

```text
BUSINESS SEMANTICS
Business Term
KPI / Metric
Recipe / Calculation
```

```text
GOVERNANCE & METADATA
Governance Metadata
Authorization Scope
Registry Version
```

```text
SOURCE SYSTEMS
Data Source
SQL Server / Azure SQL
Databricks
Future Approved Source
```

Suggested visual distinction:

• Core Data Structure: blue
• Business Semantics: green
• Governance & Metadata: purple
• Source Systems: light teal

────────

8. Important Architecture Notes for the Diagram

Add these as small notes at the bottom of the Visio page:

```text
1. This is a conceptual data model, not a physical database schema.

2. Metadata existence does not grant authorization.

3. AskAlpha maintains a provider-independent governed semantic model.

4. Physical data remains owned by the authoritative source platforms.

5. SQL Server / Azure SQL is currently supported.

6. Databricks is a planned/integration option and must not be shown
   as a mandatory current dependency.

7. Registry Version identifies the governed semantic snapshot used
   for reproducibility and audit.

8. Authorization is entity-level for MVP and is designed to support
   finer dataset, column, and row scope in future phases.
```

────────

9. Minimal Version — If the Diagram Becomes Too Busy

If the full diagram is too crowded, use only these entities:

```text
Product Group
Schema
Dataset
Field / Column
Relationship
Business Term
KPI / Metric
Recipe / Calculation
Governance Metadata
Authorization Scope
Registry Version
Data Source
SQL Server / Azure SQL
Databricks
Future Approved Source
```

Do not add additional technical implementation objects such as:

```text
Azure OpenAI
Azure AI Search
FastAPI
React
App Service
SQL Warehouse
Event Hubs
Redis
Genie
```

Those belong to architecture/runtime diagrams, not the 13.2 Conceptual
Data Model.
