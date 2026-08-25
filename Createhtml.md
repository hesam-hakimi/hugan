You are a senior enterprise solution architect, information designer,
and front-end engineer.

I need you to create a professional, print-ready architecture diagram
for a governed conversational analytics platform named AskAlpha.

IMPORTANT:

Do NOT create a VSIX package.
Do NOT create a Visual Studio or VS Code extension.
Do NOT create a plugin.
Do NOT create a React project or any application requiring installation.
Do NOT use Mermaid.
Do NOT require npm, a build process, a web server, or internet access.

Create one standalone HTML file that can be opened directly in a browser,
viewed as an architecture poster, and printed or saved as PDF.

==================================================
1. INPUT AND SOURCE OF TRUTH
==================================================

If the following Excel workbook is attached, read it first:

AskAlpha_Visio_Compact_Architecture_V3_2026-08-24.xlsx

Use these worksheets as supporting input:

- 13.1_Compact_Architecture_V3
- 13.1_Flow_Details_V3
- 13.1_Visio_Notes_V3
- Meeting_Update_2026-08-24

If the workbook is not available, use the architecture specification in
this prompt as the source of truth.

All visible labels must use:

AskAlpha

Do not use AskTD anywhere in the visible diagram.

==================================================
2. REQUIRED OUTPUT
==================================================

Create this file in the current workspace:

AskAlpha_Architecture_Poster.html

The file must be completely self-contained and include:

- HTML;
- inline CSS;
- inline JavaScript only if needed;
- inline SVG for connectors and simple icons;
- no external images;
- no external fonts;
- no CDN references;
- no third-party JavaScript or CSS libraries.

The HTML must work offline by double-clicking the file.

If you cannot write files in the current environment, return the complete
HTML source without abbreviating or omitting any section.

==================================================
3. PRINTING REQUIREMENTS
==================================================

Design the output as a single-page enterprise architecture poster.

Print format:

- A3 landscape;
- approximately 420 mm × 297 mm;
- printable on one page;
- 8–10 mm page margins;
- no content clipping;
- no horizontal or vertical overflow in print mode;
- preserve all colors when printing;
- use vector-quality SVG connectors and icons;
- do not rasterize the architecture diagram.

Include CSS similar to:

@page {
  size: A3 landscape;
  margin: 8mm;
}

@media print {
  .screen-only {
    display: none !important;
  }

  body {
    margin: 0;
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }
}

Create a screen-only toolbar with:

- Print / Save as PDF button;
- Reset Zoom button;
- optional Fit to Screen button.

Hide this toolbar during printing.

Use Segoe UI, Arial, or another standard local system font.

==================================================
4. VISUAL STYLE
==================================================

Use a clean enterprise architecture style.

The diagram should look similar to a professional Visio architecture
poster rather than a web dashboard.

Use:

- a white background;
- subtle container fills;
- dark-blue headings;
- rectangular architecture components;
- rounded corners;
- thin professional borders;
- right-angle connectors;
- clear arrowheads;
- status badges;
- concise but readable text;
- consistent spacing;
- no decorative gradients;
- no excessive shadows;
- no cartoon-style graphics.

Use these status styles:

Current / Supported
- solid blue border;
- pale blue or pale green fill.

Core / Working Decision
- solid green border;
- pale green fill.

Planned / Open
- dashed orange border;
- pale orange fill.

Conditional / PIA-Dependent
- dashed purple border;
- pale purple fill.

Future / Evaluation
- dashed grey border;
- pale grey fill.

Include a legend explaining these status styles.

==================================================
5. PAGE STRUCTURE
==================================================

The poster must contain:

1. A title area.
2. A main cross-functional architecture diagram.
3. Four horizontal cross-cutting control bands.
4. A status legend.
5. A small Open Decisions / Architecture Notes panel.
6. A footer containing the architecture disclaimer.

Use this title:

AskAlpha Governed Conversational Analytics
Data Architecture and Processing Flow

Use this subtitle:

Provider-Agnostic • Governed • Read-Only • Versioned • Auditable

==================================================
6. MAIN DIAGRAM LAYOUT
==================================================

Create a structured matrix with four horizontal lifecycle phases and five
vertical responsibility lanes.

Lifecycle phases from left to right:

1. Access & Understand
2. Plan & Govern
3. Execute & Validate
4. Format & Respond

Responsibility lanes from top to bottom:

1. Users & Identity
2. AskAlpha Application
3. Semantic, AI & Acceleration
4. Data Access & Platforms
5. Business Outputs

Use visible phase headers and lane labels.

Use inline SVG or an SVG overlay for connectors.

All connectors must:

- use right-angle routing where practical;
- avoid crossing through text;
- use arrowheads;
- remain aligned when printing;
- use solid lines for request/data flows;
- use dashed lines for metadata, governance, offline refresh, optional,
  or future flows.

==================================================
7. MAIN REQUEST FLOW
==================================================

Represent this primary flow:

Business User
→ AskAlpha Web UI + Microsoft Entra ID
→ Authentication + Entity-Level Authorization
→ Intent Understanding
→ Predefined Question / Template Match
→ Semantic Planning
→ Query Orchestration + Query Safety
→ Scope-Aware Cache Lookup

From Scope-Aware Cache Lookup create two paths:

Cache Hit
→ Response Formatting / Template Selection

Cache Miss
→ DataSourceAdapter / ExecutionProvider
→ Governed Data Source
→ Result Validation
→ Cache Store / Refresh
→ Response Formatting / Template Selection

From Response Formatting / Template Selection create two paths:

Preferred deterministic path:
→ Deterministic Template Formatter
→ Business Outputs

Conditional AI-assisted path:
→ Azure OpenAI — Response Formatting
→ Business Outputs

Business Outputs must include:

- Direct Answer
- Table
- Chart
- Report
- Executive Summary

==================================================
8. USERS & IDENTITY LANE
==================================================

Add these components:

Business User

AskAlpha Web UI + Microsoft Entra ID

Use these connector labels where appropriate:

- HTTPS / TLS
- Authentication
- JWT / Group Claims

Authentication / authorization principles:

- Microsoft Entra ID / SSO;
- entity-level authorization for MVP;
- fail closed;
- authorization before metadata retrieval, query execution, aggregation,
  caching, formatting, and output.

==================================================
9. ASKALPHA APPLICATION LANE
==================================================

Add these components:

Authentication + Entity-Level Authorization

Intent Understanding

Semantic Planning

Query Orchestration + Query Safety

Result Validation

Response Formatting / Template Selection

Deterministic Template Formatter

Use concise descriptions inside or below each component.

Authentication + Entity-Level Authorization:

- Validate authenticated user;
- resolve allowed entities;
- restrict downstream discovery and execution.

Semantic Planning:

- create a governed semantic plan;
- bind the plan to metadata and registry versions;
- do not treat model output as executable authority.

Query Orchestration + Query Safety:

- read-only;
- bounded;
- validated;
- allow-listed objects;
- timeout and row limits.

Result Validation:

- verify schema and expected output;
- apply masking/redaction;
- validate authorization;
- validate result size and shape.

Deterministic Template Formatter:

- approved repeatable output formats;
- preferred for common and high-risk questions;
- no model call required.

==================================================
10. PREDEFINED QUESTIONS AND TEMPLATE LIBRARY
==================================================

Add this supporting component:

Predefined Question / Template Library

Description:

- versioned JSON patterns;
- approved question patterns;
- approved response templates;
- approved output structures;
- controlled business definitions.

Add this offline supporting component:

Usage Analytics + Curated Monthly Refresh

Connect it to the Predefined Question / Template Library using a dashed
arrow labelled:

Monthly Governed Standard Release

Add this note:

Popular query patterns are analyzed offline.
Selected patterns and JSON/template definitions are reviewed and refreshed
through a controlled monthly or approved standard release.
The library is not rewritten autonomously every day.

Connect the Predefined Question / Template Library to the template-match
or semantic-planning step using a dashed metadata/control connector.

==================================================
11. SEMANTIC REGISTRY, AI SEARCH, AND AI REASONING
==================================================

Add this combined or closely grouped component:

AskAlpha Semantic Registry + Azure AI Search

Semantic Registry responsibilities:

- Product Group;
- Schema;
- Dataset;
- Field;
- Relationship;
- Business Term;
- KPI / Metric;
- Approved Recipe;
- Registry Version.

Azure AI Search responsibilities:

- semantic metadata retrieval;
- business-definition retrieval;
- candidate discovery.

Make clear that Azure AI Search is not the analytical query engine.

Add:

Azure OpenAI — Semantic Reasoning

Connect:

Semantic Planning
↔ Azure OpenAI — Semantic Reasoning

Use connector labels:

- Approved Prompt + Minimum Necessary Semantic Context
- Semantic Plan Proposal

Add this visible note:

Azure OpenAI does not connect directly to governed source data
during semantic planning.

==================================================
12. SCOPE-AWARE CACHE
==================================================

Add this component:

Scope-Aware Cache

Status:

Planned / Platform TBD

Do not label it Redis because the cache platform has not been approved.

Inside or beside the component add:

Cache key includes:

- authorization scope;
- semantic-plan hash;
- registry / metadata version;
- authorization-policy version;
- data-freshness version;
- output shape.

Show:

Cache Hit
→ Response Formatting / Template Selection

Cache Miss
→ DataSourceAdapter / ExecutionProvider

Show:

Result Validation
→ Cache Store / Refresh
→ Response Formatting / Template Selection

Add this security warning:

Never cache unrestricted data and filter it only in the UI.

Use a dashed border because the cache is planned and not a confirmed current
live dependency.

==================================================
13. DATA ACCESS AND EXECUTION
==================================================

Add:

DataSourceAdapter / ExecutionProvider

Responsibilities:

- provider routing;
- source-specific query compilation;
- read-only execution;
- timeout and cancellation;
- row and result limits;
- audit correlation.

Below it create a large container:

Governed Data Sources

Inside this container show:

SQL Server / Azure SQL
Status: Current / Supported

- Schemas
- Tables
- Views

DAC-Prepared Data in SpruceX
Status: Integration Option

AZ / Consumption Views
Status: Integration Option

Databricks SQL
Status: Planned / Integration Option

- Catalog when available and approved
- Schema
- Tables / Views
- Governed Delta Data

Future Approved Provider
Status: Future / Optional

Add a small dashed callout:

Future execution provider:
Databricks Genie — Evaluation Only

Do not present Genie as current, approved, or required.

Add this architecture note:

The final governed data-access path remains an architecture decision:
DAC-prepared data, AZ / Consumption Views, Databricks SQL / Unity Catalog,
or another approved provider path.

Do not assume a specific Databricks compute model.

==================================================
14. RESPONSE FORMATTING
==================================================

Add:

Response Formatting / Template Selection

This component receives:

- validated authorized result;
- requested output type;
- approved output template reference.

Create two branches.

Branch 1:

Deterministic Template Formatter

Label:

Preferred / Repeatable

Description:

- approved formatting logic;
- tables, charts, reports, and summaries;
- deterministic output structure;
- no Azure OpenAI call required.

Branch 2:

Azure OpenAI — Response Formatting

Status:

Conditional / PIA-Dependent

Use a dashed purple border and dashed connector.

Label the connector into Azure OpenAI:

Minimum Necessary Validated Result Context

Add this warning:

This interaction may contain governed query-result data,
not metadata only.

It must be:

- explicitly approved;
- minimized;
- masked / redacted;
- governed by PIA and model-use controls;
- excluded from use when deterministic formatting is sufficient.

==================================================
15. CROSS-CUTTING CONTROL BANDS
==================================================

At the bottom of the poster add four horizontal bands.

Band 1:

Security & Authorization

Include:

- Microsoft Entra ID / SSO
- Entity-Level Authorization — MVP
- Workload / Managed Identity
- Read-Only Access
- Fail Closed
- Authorization Before Cache and Aggregation

Band 2:

Metadata & Governance

Include:

- Semantic Registry
- Business Definitions
- Metadata Versioning
- Governed Relationships
- Approved Recipes
- Source Ownership

Band 3:

Privacy & Data Protection

Include:

- DAC Treatment
- Data Minimization
- Masking / Redaction
- Minimum Necessary Model Payload
- PIA Controls
- Retention / Deletion

Band 4:

Audit & Observability

Include:

- User / Request ID
- Registry Version
- Data Source Used
- Query Outcome
- Cache Hit / Miss
- Model Usage
- Formatting Path
- Audit / Telemetry

==================================================
16. OPEN DECISIONS PANEL
==================================================

Add a small panel titled:

Open Decisions / Architecture Confirmation

Include:

- final governed data-access pattern;
- cache platform and owner;
- cache TTL and invalidation policy;
- Databricks query-serving endpoint;
- enterprise metadata provider;
- production network / firewall path;
- allowed Azure OpenAI response-formatting payload;
- output retention and export policy;
- Genie future role.

==================================================
17. STATUS LEGEND
==================================================

Include:

Current / Supported

Core / Working Decision

Planned / Open

Conditional / PIA-Dependent

Future / Evaluation

Also include:

Solid arrow:
Primary request / data flow

Dashed arrow:
Metadata / control / offline refresh / optional flow

==================================================
18. FOOTER DISCLAIMER
==================================================

Add this footer:

This is a conceptual architecture view.

It does not assert that Databricks, Unity Catalog, SQL Warehouse,
a distributed cache, Genie, direct access, or zero-copy access
is currently deployed or approved.

AskAlpha remains provider-agnostic.
Planned and optional capabilities require architecture,
security, privacy, platform, and operational confirmation.

==================================================
19. TECHNICAL IMPLEMENTATION GUIDANCE
==================================================

Prefer one of these implementation approaches:

Option A — Recommended:

- absolutely positioned HTML component boxes;
- one inline SVG overlay for connectors;
- arrowhead markers defined inside SVG;
- all visible content stored as HTML text;
- CSS Grid or calculated coordinates for the lane/phase matrix.

Option B:

- one large inline SVG;
- use foreignObject for wrapped HTML text inside components.

Do not use a canvas because printed text should remain sharp and selectable.

Keep architecture content and coordinates in one editable JavaScript object,
for example:

const diagramData = {
  phases: [...],
  lanes: [...],
  nodes: [...],
  edges: [...]
};

Each node should include:

- id;
- title;
- description;
- lane;
- phase;
- status;
- x;
- y;
- width;
- height.

Each edge should include:

- from;
- to;
- label;
- type: primary | metadata | conditional | future.

==================================================
20. QUALITY REQUIREMENTS
==================================================

Before finishing, verify:

- every required node is visible;
- no text is clipped;
- no component overlaps another component;
- connectors do not cross through component text;
- phase and lane labels are readable;
- all planned/conditional/future items use dashed styling;
- SQL Server is identified as current/supported;
- Databricks is identified as planned/integration option;
- Genie is future/evaluation only;
- Azure OpenAI response formatting is clearly conditional and PIA-controlled;
- cache is shown as planned/platform TBD;
- predefined templates show a controlled monthly refresh;
- the complete poster fits on one A3 landscape print page;
- print preview preserves background colors;
- the file opens without internet access;
- there are no browser console errors.

==================================================
21. FINAL RESPONSE
==================================================

If file-writing is available:

1. Create `AskAlpha_Architecture_Poster.html`.
2. Confirm that the file was created.
3. Briefly explain how to open it and print it to PDF.
4. Do not paste the entire HTML into the chat unless asked.

If file-writing is not available:

Return the complete HTML document in one code block.
Do not truncate it.
Do not replace sections with placeholders.
Do not write “continue” or “remaining code omitted.”
