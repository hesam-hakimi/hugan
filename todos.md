# AskAlpha 13\.3 Logical\-to\-Physical Model Mapping

## Diagram Text and Microsoft Visio Build Instructions

This document provides:

- copy/paste\-ready English text for every major shape;
- connector labels;
- layout guidance;
- styling guidance;
- ABP\-ready wording for Section 13\.3;
- step\-by\-step instructions for recreating the diagram in Microsoft Visio\.

> **Important architecture wording**
> 
> - Use **single source of truth**, not “single version of truth.”
> - Do not present Unity Catalog as universally available. Use:  
>   **Unity Catalog when available and approved**.
> - Databricks is a **planned integration option**, not a required current dependency.
> - AskAlpha owns the governed logical/semantic model. Authoritative source platforms own their physical models.

---

# 1\. Diagram Title

```text
13.3 Logical-to-Physical Model Mapping — AskAlpha
```

---

# 2\. Layer Labels

Place these labels on the left side of the diagram:

```text
1. Logical / Semantic Layer
```

```text
2. Provider Mapping Layer
```

```text
3. Physical Layer (Sources)
```

---

# 3\. Logical / Semantic Layer

## Container Title

```text
AskAlpha Governed Logical / Semantic Model
```

## Product Group

```text
Product Group

Logical entity representing
a collection of related products.
```

## Schema

```text
Schema

Logical grouping of datasets
within a product group.
```

## Dataset

```text
Dataset

Business dataset defined
at the logical level.
```

## Field / Column

```text
Field / Column

Logical data element
with business meaning.
```

## Business Term

```text
Business Term

Business concepts and definitions
used across domains.
```

## KPI / Metric

```text
KPI / Metric

Business metrics and calculations
based on logical data.
```

---

# 4\. AskAlpha Registry Provider

```text
AskAlpha Registry Provider

Canonical metadata
and business glossary
(source of truth).
```

Suggested status label:

```text
Current / Core
```

Suggested border:

```text
Dashed border
```

Suggested connector type:

```text
Metadata / governance flow
```

---

# 5\. Provider Mapping Layer

## Container Title

```text
Provider Mapping Layer
```

## DataGovernanceProvider

```text
DataGovernanceProvider
(Authoritative Metadata)

• AskAlpha Registry
• Unity Catalog (Databricks)
• Collibra (Metadata / Glossary)
• HopeX (Enterprise Model Reference)
• Future Governance Provider
• Authorization & Policy Metadata
```

## DataSourceAdapter

```text
DataSourceAdapter
(Physical Object Mapping)

• Maps logical objects to physical objects
• Manages source-specific naming
• Maintains mapping rules and lineage
• Supports schema evolution
• Applies source-specific query capabilities
• Supports read-only execution controls
```

## Connector Label Between the Two Provider Components

Preferred label:

```text
metadata alignment
```

Alternative shorter label:

```text
governed mapping
```

Suggested connector:

```text
Two-way connector
```

---

# 6\. Physical Layer

## SQL Server / Azure SQL Physical Model

```text
SQL Server / Azure SQL
Physical Model

• Databases
• Schemas
• Tables
• Views
• Columns
• Keys / Relationships
• Stored Procedures
• Functions
• Indexes
• Security Policies / RLS
```

Suggested identifier format:

```text
Database.Schema.Table.Column
```

Suggested status:

```text
Current / Supported
```

Ownership statement:

```text
Owned by the authoritative SQL source platform
and the relevant data owner.
```

---

## Databricks Physical Model

```text
Databricks Physical Model
Unity Catalog when available and approved

• Catalogs
• Schemas
• Delta Tables
• Views
• Columns
• Governed Delta Data
• Row Filters / Column Masks
• Notebooks / Jobs
• Volumes
• Lineage References
```

Suggested identifier format:

```text
Catalog.Schema.Table.Column
```

Suggested status:

```text
Planned / Integration Option
```

Ownership statement:

```text
Owned by the authoritative Databricks / Rahona platform
and the relevant data-product owner.
```

Important note:

```text
Do not assume Unity Catalog, a SQL Warehouse,
or a specific Databricks access pattern is available
in every environment without architecture confirmation.
```

---

## Future Approved Provider Physical Model

```text
Future Approved Provider
Physical Model

• Provider-Specific Database / Catalog
• Schemas / Datasets
• Tables / Views / Objects
• Fields / Attributes
• Files / Containers
• APIs / Endpoints
• Streaming Sources
• Provider-Specific Security Controls
```

Suggested status:

```text
Future / Optional
```

---

# 7\. Example: Logical\-to\-Physical Mapping

## Example Box Title

```text
Example: Logical-to-Physical Mapping
(Lending Domain)
```

## Copy/Paste Content

```text
Logical (AskAlpha)                    Physical (Example)

Product Group: Lending      →         Catalog / Database: lending
Schema: Consumer            →         Schema: consumer
Dataset: Loan               →         Table / View: loan
Field: Current Balance      →         Column: current_balance
```

## SQL Server Example

```text
SQL Server Mapping

Database: LendingDB
Schema: Consumer
Table: Loan
Column: CurrentBalance

Identifier:
LendingDB.Consumer.Loan.CurrentBalance
```

## Databricks Example

```text
Databricks Mapping

Catalog: lending
Schema: consumer
Table: loan
Column: current_balance

Identifier:
lending.consumer.loan.current_balance
```

Suggested connector label:

```text
metadata mapping
```

Architecture note:

```text
The governed business meaning remains stable
even when the authoritative physical source changes.
```

---

# 8\. Legend

```text
Legend

────────  Data / mapping flow

- - - -   Metadata / governance flow

Solid border   Current / supported

Dashed border  Planned / optional / future
```

---

# 9\. Key Principles

```text
Key Principles

• The AskAlpha logical model is technology-agnostic and governed.

• AskAlpha owns the business definitions, semantic relationships,
  KPI definitions, and mapping contracts.

• The Provider Mapping Layer ensures consistent mapping,
  metadata alignment, and traceability.

• Physical models are optimized and governed by each
  authoritative source platform.

• Governance metadata flows through provider contracts
  into the canonical AskAlpha model.

• Changing a physical provider should not require redesign
  of business terms, KPIs, recipes, or the semantic plan.
```

---

# 10\. Notes

```text
Notes

• The logical model in AskAlpha is the single source of truth
  for business definitions and semantic meaning.

• Physical implementations may vary by source system
  and are managed through the provider-mapping layer.

• Mappings support lineage, impact analysis,
  reproducibility, and controlled source replacement.

• AskAlpha does not create an uncontrolled duplicate
  of each provider's physical metadata catalog.
```

---

# 11\. Future Provider Examples

```text
Future Providers (Examples)

• Snowflake
• Microsoft Fabric
• SAP / S4HANA
• Oracle
• REST / GraphQL APIs
• File / Object Storage
• Streaming Platforms
```

---

# 12\. Ownership Statement

```text
AskAlpha owns the governed logical and semantic model.

Authoritative source platforms own their physical data models.

Provider contracts map the AskAlpha logical model
to each approved physical implementation.
```

---

# 13\. Recommended Visio Layout

Use this three\-layer arrangement:

```text
┌──────────────────────────────────────────────────────────────┐
│       AskAlpha Governed Logical / Semantic Model             │
│                                                              │
│ Product Group | Schema | Dataset | Field | Term | KPI        │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
          ┌─────────────────────────────────────────┐
          │         Provider Mapping Layer          │
          │                                         │
          │ DataGovernanceProvider ↔ DataSourceAdapter
          └────────────────────┬────────────────────┘
                               │
                   ┌───────────┼───────────┐
                   ▼           ▼           ▼
             SQL Server    Databricks    Future
             Physical      Physical      Physical
             Model         Model         Model
```

Place the following reference boxes on the right:

```text
AskAlpha Registry Provider
```

```text
Example: Logical-to-Physical Mapping
```

```text
Legend
```

```text
Key Principles
```

Place the following wide information band at the bottom:

```text
Notes | Future Providers
```

---

# 14\. Microsoft Visio Build Instructions

## Step 1 — Create a New Page

Do not use a Cross\-Functional Flowchart for 13\.3\.

1. Click the `+` icon at the bottom of Visio\.
2. Add a new blank page\.
3. Select:

```text
Design → Orientation → Landscape
```

4. For more space, use:

```text
Design → Size → A3
```

or another wide custom page size\.

---

## Step 2 — Open the Required Shape Libraries

Open:

```text
More Shapes → General → Basic Shapes
```

For layer grouping, use:

```text
Insert → Container
```

For platform icons, use:

```text
Insert → Icons
```

Search for:

```text
database
layers
cloud
metadata
registry
catalog
```

---

## Step 3 — Create the Logical / Semantic Layer

1. Insert one wide container at the top\.
2. Set its title to:

```text
AskAlpha Governed Logical / Semantic Model
```

3. Insert six equal\-size rectangles inside the container:
  - Product Group
  - Schema
  - Dataset
  - Field / Column
  - Business Term
  - KPI / Metric
4. Select all six rectangles\.
5. Use:

```text
Home → Position → Align Middle
```

6. Then use:

```text
Home → Position → Distribute Horizontally
```

Suggested visual style:

- dark\-blue border;
- very light\-blue fill;
- white title bar or dark\-blue title text;
- font size 9–11 pt\.

---

## Step 4 — Add the AskAlpha Registry Provider

1. Place a rectangle to the right of the logical\-model container\.
2. Paste:

```text
AskAlpha Registry Provider

Canonical metadata
and business glossary
(source of truth).
```

3. Apply a dashed border:

```text
Home → Line → Dashes
```

4. Connect the logical model to the registry provider with a dashed connector\.

---

## Step 5 — Create the Provider Mapping Layer

1. Insert a green container below the logical layer\.
2. Set the title:

```text
Provider Mapping Layer
```

3. Add two large rectangles:
  - DataGovernanceProvider
  - DataSourceAdapter
4. Connect them with a two\-way connector\.
5. Use:

```text
Design → Connectors → Right Angle
```

6. Add arrowheads to both ends\.
7. Label the connector:

```text
metadata alignment
```

Suggested visual style:

- green title;
- very light\-green fill;
- medium green border\.

---

## Step 6 — Create the Physical Models

Place three equal\-size rectangles at the bottom:

1. SQL Server / Azure SQL Physical Model
2. Databricks Physical Model
3. Future Approved Provider Physical Model

Select all three and use:

```text
Home → Position → Align Top
```

Then:

```text
Home → Position → Distribute Horizontally
```

Connect `DataSourceAdapter` to all three\.

Recommended line styles:

- SQL Server: solid line;
- Databricks: dashed line or solid line with status label;
- Future Provider: dashed line\.

Recommended status label for Databricks:

```text
Planned / Integration Option
```

---

## Step 7 — Add the Logical\-to\-Physical Example

1. Insert a light\-orange rectangle or container on the right\.
2. Paste the example content from Section 7\.
3. Connect it to `DataSourceAdapter` using a dashed connector\.
4. Label the connector:

```text
metadata mapping
```

---

## Step 8 — Add the Legend

Create a small rectangle titled:

```text
Legend
```

Inside it, draw:

- one solid connector;
- one dashed connector\.

Add these labels:

```text
Data / mapping flow
```

```text
Metadata / governance flow
```

---

## Step 9 — Add Key Principles

Create a small rectangle titled:

```text
Key Principles
```

Paste the content from Section 9\.

Use a smaller font such as 8–9 pt\.

---

## Step 10 — Add the Bottom Notes Band

1. Add one wide rectangle at the bottom\.
2. Divide it visually into two sections:
  - Notes
  - Future Providers
3. Paste the text from Sections 10 and 11\.
4. Use:
  - very light fill;
  - thin border;
  - 8–9 pt font\.

---

## Step 11 — Clean Up the Diagram

Use right\-angle connectors:

```text
Design → Connectors → Right Angle
```

Align and distribute shapes:

```text
Home → Position → Align
```

```text
Home → Position → Distribute
```

Use automatic spacing carefully:

```text
Home → Position → Auto Align & Space
```

For containers:

```text
Home → Arrange → Send to Back
```

For labels and important boxes:

```text
Home → Arrange → Bring to Front
```

---

# 15\. Suggested Shape Sizes

|Diagram Element           |Suggested Width     |
|--------------------------|-------------------:|
|Logical Layer Container   |70–75% of page width|
|Each Logical Entity       |1.5–1.8 inches      |
|Provider Mapping Container|55–60% of page width|
|Each Provider Box         |3–3.5 inches        |
|Each Physical Model Box   |2.7–3 inches        |
|Example Mapping Box       |3.2–3.8 inches      |
|Right-Side Reference Box  |2.8–3.2 inches      |

---

# 16\. ABP\-Ready Text for Section 13\.3

```text
The AskAlpha logical model is represented by the governed semantic
registry, including Product Group, Schema, Dataset, Field,
Relationship, Business Term, KPI, Recipe, Governance Metadata,
Registry Version, and Authorization Scope.

AskAlpha is provider-agnostic and does not maintain an uncontrolled
duplicate of each source platform's physical data model.

Physical models remain owned by the authoritative source platforms.
For SQL Server / Azure SQL sources, the physical model is represented
by the approved database, schema, table/view, column, key, and security
definitions.

For Databricks-based sources, the physical model will reference the
approved catalog/schema/table/view/column model and governed
data-product documentation when that integration path is confirmed.

Provider contracts map the AskAlpha logical model to these
authoritative physical models.
```

---

# 17\. Link Placeholders for the ABP

Do not invent URLs\. Use these placeholders until the authoritative owners provide them\.

```text
AskAlpha Logical / Semantic Model:
[TBD — link to AskAlpha semantic registry or approved project documentation]
```

```text
SQL Server / Azure SQL Physical Model:
[TBD — link to the authoritative physical model in HopeX
or the approved source-system repository]
```

```text
Databricks / Rahona Physical Model:
[TBD — link to the authoritative data-product or catalog model
in HopeX, Unity Catalog, or approved architecture documentation]
```

```text
Enterprise Business Glossary / Governance Model:
[TBD — link to Collibra or the approved enterprise governance system]
```

---

# 18\. Explanation When a Single Physical Model Is Not Applicable

```text
A single application-owned physical data model is not applicable
because AskAlpha is designed to consume governed datasets from
multiple authoritative data platforms.

AskAlpha owns the logical / semantic model and maps it to
provider-specific physical models through governed adapter contracts.

Each source platform and data-product owner remains responsible
for its authoritative physical model.
```

---

# 19\. Minimal Version

If the full diagram becomes too busy, keep only these shapes:

```text
AskAlpha Governed Logical / Semantic Model

DataGovernanceProvider

DataSourceAdapter

SQL Server / Azure SQL Physical Model

Databricks Physical Model

Future Approved Provider Physical Model
```

Minimal layout:

```text
AskAlpha Logical / Semantic Model
                 │
                 ▼
      DataGovernanceProvider
                 ↕
         DataSourceAdapter
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
      SQL    Databricks   Future
```

Do not include these runtime components in 13\.3:

```text
Azure OpenAI
Azure AI Search
React
FastAPI
App Service
Event Hubs
Redis
Genie
SQL Warehouse
```

Those belong in runtime/application architecture diagrams, not in the logical\-to\-physical mapping\.
