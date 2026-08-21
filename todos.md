Product Portfolio Poster – Repository Analysis

I am preparing a product portfolio poster to present the tools/products we have built.

Your task is to inspect the available Git repositories/workspace and create a clear, concise, business-friendly summary for each real product or tool you can identify.

Important Rules

* Do not modify any code or configuration.
* Do not create commits, branches, or PRs.
* Analyze the implementation, not only README files.
* Use evidence from:
    * source code
    * README/documentation
    * configuration files
    * architecture files
    * tests
    * workflows
    * APIs
    * UI code
    * integrations
    * deployment configuration
* Do not invent capabilities.
* If something cannot be confirmed from the repository, write:
    Needs confirmation
* Do not expose:
    * secrets
    * credentials
    * tokens
    * private URLs
    * connection strings
    * sensitive infrastructure information
* Write the final content in simple professional English suitable for a poster and for both technical and non-technical audiences.

⸻

Step 1 – Identify the Products

First inspect the repositories/workspace and identify the distinct products, tools, extensions, frameworks, applications, or major reusable solutions we have built.

Do not treat every library or module as a separate product.

For each detected product, explain briefly why you consider it a separate product.

Create an initial table:

Product	Repository / Location	Product Type	Main Purpose

Examples of Product Type:

* Web Application
* AI Application
* VS Code Extension
* Data Engineering Framework
* Developer Tool
* Evaluation Tool
* Automation Tool
* API / Service
* Data Platform Component

⸻

Step 2 – Deeply Analyze Each Product

For each identified product, inspect enough of the implementation to understand:

1. What problem it solves
2. What the tool actually does
3. Who would use it
4. Its major features
5. Main architectural components
6. Whether and how AI/LLM is used
7. Important integrations
8. What makes the solution useful or different
9. Business and engineering benefits
10. Current implementation evidence

Do not simply copy repository descriptions.

⸻

Step 3 – Create Poster-Ready Content

For every product use exactly this structure.

[Product Name]

Tagline

One short sentence, preferably 10–18 words, describing the value of the product.

What Does This Tool Do?

Write one or two short paragraphs.

Explain:

* the problem
* what the product does
* how it helps the user

Keep this approximately 60–100 words.

Avoid deep implementation details here.

Key Features

Provide 4–7 short bullets.

Each bullet should describe a meaningful capability, for example:

* Natural-language data querying
* Automated ETL generation
* Metadata-driven processing
* Validation before deployment
* Multi-platform data access

Do not use generic statements such as “easy to use” unless supported by the implementation.

How It Works

Describe the main workflow in 3–6 simple steps.

Example format:

User Request → Analysis → Validation → Execution → Result

Then add one sentence explaining the workflow.

Main Components

Use a compact table:

Component	Purpose
Web UI	User interaction
Backend API	Application orchestration
LLM	AI reasoning/generation
Database	Data or metadata storage

Only include components that actually exist.

AI / LLM Enabled

Write:

Yes / No / Partial

If Yes or Partial, briefly describe what AI does.

Examples:

* understands user questions
* generates SQL
* analyzes metadata
* generates ETL artifacts
* evaluates results
* provides recommendations

Do not state the exact model unless it can be confirmed.

Key Technologies

Provide only the important technologies.

For example:

React · Python · FastAPI · Databricks · Azure OpenAI · SQL · VS Code

Avoid listing every package or dependency.

Integrations

List significant platforms or systems the product integrates with.

Target Users

List the primary user groups in one short line.

For example:

Data Engineers · Analysts · Developers · Business Users

Benefits

Provide 3–5 concise business-oriented benefits.

Focus on outcomes such as:

* Reduces manual engineering effort
* Speeds up delivery
* Improves consistency
* Reduces implementation errors
* Makes governed data easier to access
* Standardizes development workflows
* Improves traceability
* Enables self-service capabilities

Only claim benefits that reasonably follow from confirmed functionality.

Key Differentiator

Write 1–2 sentences describing what makes this product particularly useful or different.

Product Status

Use one of:

* Production
* Pilot
* POC
* Active Development
* Prototype
* Unknown / Needs confirmation

Only select a status when repository evidence supports it.

⸻

Step 4 – Create a Very Short Poster Version

After the detailed analysis, create a second condensed version for each product.

Use this format:

[Product Name] – Poster Card

Tagline:
Maximum 15 words.

What it does:
Maximum 50 words.

Features:

* Maximum 5 bullets
* Maximum 8 words per bullet

Components:
Maximum 6 major components.

AI Enabled:
Yes / No / Partial

Benefits:

* Maximum 4 bullets
* Maximum 8 words per bullet

This section must be optimized for putting directly onto a visual poster.

⸻

Step 5 – Portfolio Summary

After analyzing all products, create this comparison table:

Product	Category	Primary User	Main Problem Solved	AI Enabled	Main Value

Then add:

Portfolio Story

Write a short 100–150 word executive summary explaining how these products collectively demonstrate our capabilities.

Focus on themes such as:

* AI-enabled engineering
* automation
* data engineering
* developer productivity
* governed analytics
* reusable frameworks
* enterprise integration

Only include themes supported by the products found.

⸻

Step 6 – Evidence / Verification Appendix

The poster itself should remain clean, but I also need to know where the information came from.

For every important claim, provide supporting repository evidence in a separate appendix.

Use:

Product	Claim	Evidence File	Relevant Code/Section

Example:

| AskTD | Natural-language querying | backend/... | Query orchestration implementation |

This appendix is for verification and should not be mixed with poster content.

⸻

Final Deliverable

Create a Markdown file named:

PRODUCT_PORTFOLIO_POSTER_CONTENT.md

Organize it as:

1. Product Inventory
2. Detailed Product Profiles
3. Poster Cards
4. Portfolio Comparison
5. Portfolio Story
6. Evidence / Verification Appendix
7. Open Items / Needs Confirmation

Before finishing, perform a final consistency check:

* Every feature must have implementation evidence.
* Remove duplicate products.
* Remove low-level technical details unsuitable for a poster.
* Keep wording simple and concise.
* Do not overstate maturity or capabilities.
* Clearly mark anything that requires human confirmation.

Do not make any code changes. This task is analysis and documentation only.
