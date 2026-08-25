## Product Goal

askAlpha turns a business question into a safe, governed, and repeatable answer\. The long\-term goal is to provide trusted answers, tables, charts, and reports across approved enterprise data platforms—not just generate SQL\.

## What We Have Designed and Added

|Phase                                       |Capability Added                                                                                                                    |Simple Business Value                                                                                                         |Current Position                                          |
|--------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
|**Phase 1 — Secure Foundation**             |Enterprise sign-in, access checks, read-only data access, safe query controls, and answers in table/chart form.                     |Users can ask questions without bypassing security or changing source data.                                                   |**Delivered foundation**                                  |
|**Phase 2A — Governed Metadata**            |A common structure for describing Product Groups, Schemas, Datasets, and Fields.                                                    |The product understands approved data through consistent definitions instead of guesses.                                      |**Completed and accepted**                                |
|**Phase 2B — Versioned Registry**           |A service that stores and retrieves current and previous metadata versions, with a small safe cache.                                |Answers can be traced to the exact data definition used at that time.                                                         |**Completed and accepted**                                |
|**Phase 2C — Governed Semantic Plan**       |A validated plan is created before any query runs, including the selected data, fields, relationships, filters, and expected output.|The system checks that a question is mapped to the right governed data before execution.                                      |**Completed and accepted**                                |
|**Phase 2C.5 — Provider-Neutral Foundation**|The core product was separated from one specific database implementation.                                                           |askAlpha can support SQL today and add Databricks or another approved platform later without redesigning the core.            |**Completed and merged**                                  |
|**Phase 2D — Approved Recipe Pilot**        |A repeatable business calculation can be stored as a governed, versioned recipe with approved parameters and validation rules.      |Important answers no longer depend on the AI improvising the calculation each time.                                           |**Implemented; review/merge workflow in progress**        |
|**Phase 2E — Field-Level Change Protection**|Recipes identify the exact governed fields they depend on and detect relevant changes.                                              |If a required field is removed, renamed, or materially changed, the answer stops instead of silently returning a wrong result.|**Implemented; stacked review/merge workflow in progress**|
|**Phase 2F — Recipe Approval and Lifecycle**|Proposed states such as **Valid**, **Review Required**, **Broken**, and **Not Approved**, supported by explicit approval evidence.  |The business can clearly see whether a trusted answer is still safe to run after a change.                                    |**Discovery complete; owner decisions pending**           |

## What We Plan to Do Next

1. **Finish the current merge sequence** — complete review and merge of the Phase 2D and Phase 2E changes\.
2. **Implement Phase 2F** — finalize approval ownership and add controlled recipe lifecycle and reapproval rules\.
3. **Add certified business meaning** — governed KPIs, glossary terms, business rules, ownership, and reusable report templates\.
4. **Support governed relationships** — approved joins and multi\-dataset reasoning without allowing the AI to invent relationships\.
5. **Expand data\-platform support** — introduce Databricks and other providers through the provider\-neutral foundation, and define the coexistence boundary with Databricks Genie\.
6. **Strengthen data safety** — improve join, grain, duplicate\-counting, row, and column controls\.
7. **Measure quality and operations** — add audit evidence, traceability, answer\-quality evaluation, and regression monitoring\.
8. **Improve scale and cost** — benchmark first, then add scope\-aware caching or Redis only if evidence shows it is needed\.
9. **Enable governed self\-service** — allow approved teams to onboard metadata and recipes through a controlled review and publishing process\.
10. **Improve the presentation experience** — richer charts, polished reports, downloads, exports, and approved integrations\.

## Management Takeaway

The project has progressed from a secure question\-and\-answer application to the foundation of a governed analytics platform\. The current focus is making business answers **repeatable, explainable, change\-aware, and safe** before expanding to more data platforms, more datasets, and broader self\-service\.
