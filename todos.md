SpruceX Governance and Security Playbook

> **DRAFT FOR REVIEW — NOT AN APPROVAL OR A LIVE-CONTROL ATTESTATION**
> 
> This project-level playbook supports the askAlpha PIA and control assessment. It does not replace the SpruceX foundational controls, required data-access approvals, or Privacy, Security and AI Governance decisions. Proposed responsibilities and review frequencies require acceptance by the relevant TD owners.

|Document control                                       |Value                                                                                                     |
|-------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
|Version / prepared date                                |0.1 / 9 September 2026                                                                                    |
|Initiative                                             |askAlpha, previously referenced as AskTD / KMAI                                                           |
|Environment                                            |SpruceX — pre-production validation with governed access to real / production-origin data                 |
|Business scope                                         |Proposed TD US Data activity; sponsoring business, legal entity and impacted jurisdictions to be confirmed|
|Document custodian                                     |askAlpha project team; named accountable owner to be confirmed                                            |
|Business / Risk Owner                                  |To be confirmed                                                                                           |
|SpruceX owner / assigned BISO or BSO                   |To be confirmed                                                                                           |
|Privacy Designate / AI Governance contact              |To be confirmed                                                                                           |
|PIA, foundational assessment and data-access references|To be linked by their owners                                                                              |
|Next review                                            |Before use as an approved control record or expansion of the pilot; exact date to be agreed               |

## 1\. Background

askAlpha is a conversational analytics application intended to help authorized TD users obtain governed, read\-only answers from organizational data\. Its design combines authenticated access, explicit permissions, a versioned Semantic Registry, validated analytical plans and bounded queries\. Reports, summaries and richer presentation are governed capabilities to be enabled only within their accepted delivery and data\-use scope\.

This playbook describes the project’s permitted\-use boundaries, data handling, responsibilities, change triggers, oversight and supporting evidence\. It adapts the structure of the supplied **Analytic Zone Playbooks** screenshots to a single application; it does not establish askAlpha as the owner of an enterprise Analytics Zone\. &#91;R1&#93;

Two separate boundaries apply:

- **SpruceX access:** the environment can provide governed access to approved production\-origin data\. It must not be described as synthetic\-data\-only\. &#91;R2&#93;
- **Application and AI use:** environment access does not authorize every askAlpha user, query, model payload, retained copy or export\. Each requires the relevant purpose, permissions, controls and approval\. &#91;R2–R3&#93;

### Evidence status

|Label                |Meaning                                                                                                   |
|---------------------|----------------------------------------------------------------------------------------------------------|
|Documented baseline  |Described in the reviewed project records; not freshly verified against the deployed SpruceX configuration|
|Required control     |A condition of the proposed design; implementation and test evidence are still required                   |
|Planned / conditional|A future or approval-dependent route; not represented as enabled                                          |
|Open                 |Missing evidence, owner, decision or configuration; no approval is inferred                               |

The latest reviewed executive update documents a foundation through Phase 2E, with **one governed dataset, one approved recipe and 199 governed fields**\. This is engineering pilot evidence, not approval for production\-origin PI/PII or the wider business\-data inventory\. The documented permission foundation is entity\-level; comprehensive user\-specific row/column enforcement must not be claimed from that alone\. New template, cache and provider capabilities remain planned, and AI result formatting remains disabled until approved\. &#91;R4–R5&#93;

No live source\-code, Azure configuration or current approval\-record audit was performed for this draft\.

## 2\. Scope and Use Boundaries

### In scope for this playbook

|Area                            |Proposed scope and restriction                                                                                                                                                                                                                    |
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Business use                    |Controlled development, testing and validation of read-only analytical questions; business sponsor to approve the exact use-case list                                                                                                             |
|Users                           |Authorized TD users within approved application groups and effective data permissions; approved endpoint / VDI conditions to be evidenced                                                                                                         |
|Data                            |Only datasets, fields and representations explicitly approved for the activity; governed production-origin access is possible in SpruceX                                                                                                          |
|Historical business-data request|Sales Associate Master, Sales Associate Goals and Loan Application Pipeline information, including employee and borrower/loan information, subject to final inventory and approval; this is not the same as the narrower engineering pilot [R3–R4]|
|Classification                  |Applicable Internal, Confidential and Restricted fields must be identified and treated; classification does not grant access                                                                                                                      |
|Source access                   |SQL Server / Azure SQL is the documented concrete execution path. The production-origin SpruceX path, including any DAC/AZ views, requires exact object mapping and runtime verification [R3, R5]                                                 |
|AI service                      |Microsoft Azure OpenAI; only approved per-call content and purposes. PI/PII processing permission remains unconfirmed in the reviewed evidence                                                                                                    |
|Outputs                         |Pilot answers and any enabled tables, summaries, charts or reports; not certified BAU, regulatory or operational reports                                                                                                                          |
|Supporting data                 |Questions, metadata, SQL, intermediate results, model inputs/outputs, histories, logs, traces, caches, diagnostics, backups and exports, wherever present                                                                                         |

### Out of scope unless separately assessed and approved

- Source\-record inserts, updates or deletes, ingestion jobs and ETL changes\.
- Automated lending, credit, employment or other customer/operational decisions\.
- Unrestricted raw/base\-table or raw\-storage access; unrestricted model payloads\.
- PCI\-DSS data\. Final field inventory and technical exclusion evidence are still required; a zone’s broader capability does not expand this project scope\.
- Public ChatGPT, the public OpenAI API, unapproved external tools, or model training/fine\-tuning with project data\.
- Unapproved downloads, scheduled distribution, email delivery or movement outside the permitted boundary\.
- Additional sources, businesses or jurisdictions without reassessment\.
- Databricks/Genie, on\-premises expansion and Collibra integration as already approved/live capabilities\. Their roadmap consideration grants no data\-access or deployment authority\.
- The separate Power BI POC and other applications using SpruceX\.

## 3\. Data Access, Processing and Movement

The following describes **required control boundaries**, not an attestation that all routes are deployed\.

|Boundary                        |Required handling                                                                                                     |Evidence needed                                                                                   |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
|User to askAlpha                |Authenticate with Entra ID; validate tokens and resolve effective permissions before protected discovery or processing|Identity configuration, group object IDs, entitlement mapping and deny tests                      |
|askAlpha to governed metadata   |Use the canonical registry and only authorized discovery scope; metadata never grants access                          |Registry version, permission checks and negative discovery tests                                  |
|askAlpha to source              |Validate plans and bounded read-only SQL; constrain execution to approved objects and user scope                      |Actual adapter/objects, identity grants, SQL validation and scope tests                           |
|Rahona / DAC / AZ route         |Confirm whether access uses governed queries or a data copy; prove treatment and deny bypass access                   |Source-to-view mapping, transfer approval where applicable, effective grants and raw-access denial|
|Any call to Azure OpenAI        |Apply an approved data contract before sending the question, metadata, SQL, results or conversation context           |Per-call payload inventory, minimization/redaction tests and applicable approval                  |
|Results to user or stored output|Preserve authorization, treatment, classification and approved destination restrictions                               |Cross-user tests, renderer/export checks and retention evidence                                   |

**Source mapping matters:** an AZ/secondary view must not be assumed to be DAC\-treated simply because it is a view\. Confirm the actual treatment policy, enforcement location and returned values\. A `Redact` label is a requirement, not proof of runtime redaction\. `Strong with Referential Integrity` needs an approved technical definition; `PI = Yes / Treatment = None` remains PI\. &#91;R3&#93;

**User and service identities are distinct:** Managed Identity authenticates the backend to services\. It does not, by itself, enforce the initiating user’s record\-level rights\. Where a dataset requires row/column restrictions beyond the proven entity\-level foundation, the route must remain unavailable until those restrictions are implemented and tested\.

## 4\. Information Security Across the Three Data States

This section addresses Sean’s request to explain protection **at rest, in transit and in use**, with deployment evidence for each state\.

### 4\.1 Data at rest — stored information

Coverage includes source databases/storage, metadata indexes, application histories, temporary files, persisted results, logs/traces, caches, provider\-held content, backups and exports where those stores exist\.

Required controls:

- Inventory every actual store, its content classification, location, owner and approved retention purpose\.
- Evidence service\-appropriate encryption, key ownership, key\-access permissions and backup protection\. Do not assert customer\-managed keys or a particular algorithm across all services without configuration evidence\.
- Apply least\-privilege data and administration access; document privileged/support access and access review\.
- Minimize persisted content\. Sensitive values must not enter logs, traces or diagnostic bundles by default; use approved non\-sensitive audit references where sufficient\.
- Define retention, deletion, legal\-hold handling where applicable and end\-of\-pilot disposal for each store\. Source retention does not automatically govern application copies\.
- If result caching is introduced, bind it to effective authorization and relevant policy/data versions, with bounded retention, invalidation and revocation tests\. A metadata cache is not proof of a secure result cache\.

**Open evidence:** store inventory; encryption/key settings; access grants; backup/export controls; approved retention/deletion matrix; tests for sensitive logging; any provider persistence configuration\. Accountable functions: Platform, Data Owners, Engineering, Privacy and the assigned BISO/BSO\.

### 4\.2 Data in transit — information moving between components

Coverage includes the user/browser\-to\-application path, backend\-to\-source/metadata services, every Azure OpenAI request/response, telemetry transport and any approved data movement or download\.

Required controls:

- Use HTTPS/TLS on applicable connections, validate certificates and document the permitted protocol configuration at every hop, including any intermediary termination\.
- Authenticate users and services independently; validate service audiences and restrict backend permissions\.
- Evidence the actual ingress/egress topology, firewall rules, DNS resolution and endpoint restrictions\. Document private endpoints and public\-access settings where required by the approved platform design\.
- Restrict destinations and transmitted content; a private connection does not authorize a PI/PII payload or establish processing residency\.
- Review any new outbound connector or export as a new data movement boundary before enablement\.

Microsoft provides a private\-endpoint configuration pattern for Azure OpenAI that also requires appropriate public\-network and DNS settings\. Availability of that pattern is not evidence that SpruceX uses it\. &#91;R7&#93;

**Open evidence:** current data\-flow/network diagram; HTTPS/TLS settings; certificate\-validation tests; private endpoint and DNS evidence; public\-access status; firewall/egress rules; actual source and telemetry routes\. Accountable functions: Platform/Network, Engineering and the assigned BISO/BSO\.

### 4\.3 Data in use — information being queried or processed

Coverage includes SQL execution, application memory, aggregation, prompt construction, AI inference, output generation and session/cache reuse\.

Required controls:

- Resolve authorization before protected retrieval, planning, query execution, aggregation, model calls, cache reuse, rendering and export\. Deny unresolved or unauthorized scope\.
- Enforce source treatment and user restrictions through deterministic application/platform controls; never delegate mandatory authorization or redaction to the LLM\.
- Use only approved objects and minimum\-necessary rows, columns and derived measures\. If an approved treatment prevents a calculation, use an explicitly approved aggregate route or declare the question unsupported; never bypass treatment\.
- Validate every model\-call payload, including free\-text questions, history, metadata, SQL literals and results\. Aggregation alone does not prove anonymization or permission for AI use\.
- Keep result\-assisted AI formatting unavailable until its permitted payload and Privacy conditions are approved\. Earlier interpretation/planning calls also require their own data contracts\.
- Treat retrieved text and model output as untrusted; they cannot change permissions, security policies or allowed tool/query actions\.
- Test unauthorized\-user access, row/column separation where required, cross\-user/session/cache leakage, malicious instructions, sensitive logs and unauthorized output/export paths\.

**Important distinction:** encryption at rest and TLS do not prove that data remains encrypted while the application or model uses it\. No confidential\-computing, enclave, encrypted\-inference or zero\-human\-access guarantee is asserted for this deployment\.

**Open evidence:** effective permission model; row/column enforcement where required; view grants and treatment tests; per\-call payloads; output/cache/logging tests; privileged/support\-access controls\. Accountable functions: Engineering/QA, IAM, DAC/Data Owners, Platform, Privacy and AI Governance\.

## 5\. Azure OpenAI and Third\-Party Processing

For this initiative, **Microsoft through Azure OpenAI is a third\-party service provider**\. Being hosted in Azure does not make the processing internal to TD\. The intended solution does not use public ChatGPT or the public OpenAI API\. &#91;R2&#93;

Microsoft’s technical documentation states that Azure\-hosted model inputs/outputs are not available to OpenAI or other customers, and foundation\-model training does not use them without permission or instruction\. Stateless inference does not mean zero service retention: optional stateful features and abuse\-monitoring processes can retain content and, under applicable conditions, involve authorized Microsoft human review\. Processing geography also depends on the deployment type\. These are service descriptions, not TD\-specific approval evidence\. &#91;R6&#93;

Before enabling production\-origin PI/PII processing, obtain:

|Required confirmation                                                                              |Proposed accountable function                               |
|---------------------------------------------------------------------------------------------------|------------------------------------------------------------|
|Applicable TD contractual coverage, processor/subprocessor roles and permitted data classifications|Vendor Management / Legal / AI Governance                   |
|TPRM engagement E#, risk rating and applicable foundational assessment                             |TPRM / enterprise Azure service owner                       |
|Resource, model/version, API/features, deployment type and processing/storage/support jurisdictions|Azure service owner / Architecture                          |
|Abuse-monitoring configuration, applicable human/support access, retention and deletion            |Azure service owner / Privacy / TPRM                        |
|Approved payload by invocation type, treatment/minimization controls and test evidence             |Engineering / Data Governance / Privacy                     |
|Written use-case-specific Privacy disposition, conditions and approval references                  |Assigned Privacy authority and required governance functions|

Do not enter an assumed retention period, risk rating, region or approval\. A foundational assessment supports the application review only to the extent that its exact services, data, features and conditions apply\. Sean’s outstanding approval dependency is not closed by this playbook or public Microsoft documentation\.

## 6\. Process Triggers to Update the Playbook

**Proposed project schedule — subject to owner approval\.** Material changes require assessment before enablement; an annual review is not permission to defer a privacy/security\-impacting change\.

|Trigger                                                                |Sections / records to update                                                                   |Proposed review timing                                  |
|-----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|--------------------------------------------------------|
|New use case, business, user population or jurisdiction                |Scope, PIA, data inventory and approval records                                                |Before enablement                                       |
|New dataset/field, changed classification, treatment or source object  |Scope, access mapping, registry/dependencies and tests                                         |Before exposure to users or AI                          |
|Users/groups added, removed or materially changed                      |Entitlement register, grants and access evidence; playbook only if scope/control design changes|At access change under the agreed revocation SLA        |
|New transfer, download/export or distribution destination              |Data-flow, retention and movement approval records                                             |Before movement is enabled                              |
|New model/vendor, deployment region/type, AI payload or service feature|Third-party section, PIA/TPRM, payload and retention records                                   |Before use                                              |
|Changed application, query, template, cache or dependency policy       |Implementation baseline, control tests and release evidence                                    |Before release; check affected approvals                |
|Changed network, identity, encryption or logging configuration         |Three-state controls and evidence                                                              |Before planned change; reassess after urgent containment|
|Incident, failed control, expired approval or owner change             |Issue register, affected scope, ownership and evidence                                         |Prompt triage through applicable TD process             |
|Periodic attestation                                                   |Entire playbook and evidence register                                                          |Proposed annual review, plus event-driven reviews       |

## 7\. Roles and Responsibilities

All assignments below are **proposed functions**\. Named individuals and delegated authority must be confirmed; participation in a meeting does not establish accountability\.

|Role                                            |Project responsibilities                                                                                                                                                            |
|------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Business / Risk Owner                           |Own purpose and permitted use; approve pilot population and success criteria; ensure required approvals and remediation are obtained                                                |
|Product Owner / document custodian              |Maintain this page, scope/use-case register, dependencies, change log and evidence references; coordinate reviews without granting themselves Privacy approval                      |
|SpruceX / Zone Owner                            |Confirm zone identity, restrictions, foundational assessments, environment/user access, platform ownership and applicable disposal/attestation obligations                          |
|Data Owner / DAC / Data Steward                 |Approve datasets and use; maintain classification and treatment; validate source/view mappings, permitted combinations, grants and retention; resolve data-quality/definition issues|
|Engineering / Architecture                      |Implement and document application controls, model boundaries and actual data flows; keep delivered, planned and disabled routes distinct                                           |
|IAM / Platform / Network                        |Provide identity, network, storage, encryption, key, privileged-access and operational configuration evidence                                                                       |
|QA / control reviewer                           |Verify representative positive and negative tests, cross-user isolation and regression evidence; record failures and retest remediation                                             |
|Assigned BISO / BSO                             |Review technology/security risk and three-state evidence; confirm which platform/destination risk assessments apply and their owners                                                |
|Privacy Designate / Privacy authority           |Review PIA completeness, PI/PII processing, provider disclosure and conditions; record/escalate decisions through the applicable approval process                                   |
|AI Governance / TPRM / Legal / Vendor Management|Confirm service/model acceptability, contractual coverage, vendor engagement and configuration-dependent conditions                                                                 |
|Designated controls / operations function       |Perform accepted recurring reviews, maintain findings and access/retention evidence; coordinate incident handling                                                                   |
|Authorized users                                |Use approved endpoints and purposes; protect outputs; avoid prohibited prompts, sharing and exports; report suspected exposure or incorrect access                                  |

## 8\. Key Monitoring and Oversight Review Tasks

Frequencies and role assignments are proposals for this application, not copied TD policy\. Owners must ratify them against existing controls; stricter applicable requirements take precedence\. No automation is claimed merely because a task appears below\.

|Task                                        |Review and retained evidence                                                                                                    |Proposed frequency                               |Proposed responsible function          |
|--------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|---------------------------------------|
|User and privileged access                  |Reconcile approved users/groups, service grants, leavers and privilege changes; record removals and reviewer sign-off           |At access changes; quarterly attestation         |IAM + application/zone owner           |
|Data access and permitted use               |Check actual datasets/views, user scope and sampled activity against approved use cases                                         |At scope changes; quarterly                      |Data Owner + controls function         |
|Undesired data combinations                 |Review joins, linkage and small-group/repeated-query inference risks; metadata validity alone is insufficient                   |Before new combinations; quarterly               |Data Steward + Privacy                 |
|AI payload and provider configuration       |Review actual enabled routes, approved content, model/features, geography and monitoring/retention configuration                |Before change; each pilot release                |Engineering + AI Governance + Platform |
|Authorization and disclosure regressions    |Test fail-closed behavior, relevant row/column restrictions, cross-user sessions/caches, raw denial and sensitive output/logging|Before relevant release                          |QA + Engineering                       |
|Data disposition                            |Compare retained content with its approved schedule; verify deletion, backup/hold exceptions and end-of-pilot disposal          |Proposed monthly; at pilot closure               |Store owners + Privacy/Records function|
|Security configuration                      |Check encryption, keys, TLS, network exposure, support access and relevant vulnerabilities                                      |Before pilot; after material change; quarterly   |Platform + BISO/BSO                    |
|Endpoint exceptions and user acknowledgement|Review approved device/VDI conditions and exceptions; confirm training/acceptable-use acknowledgement                           |At onboarding/change; annual attestation         |Zone Owner + IAM/controls function     |
|Answer integrity / governed definitions     |Check recipe evidence, field changes, calculation accuracy, warnings and agreed change-policy decisions                         |On dependency change; before release             |Data Governance + QA                   |
|Reliability and cost                        |Review failures, latency, volume and usage/cost anomalies using privacy-safe telemetry; thresholds to be agreed                 |Proposed weekly during pilot                     |Operations + Engineering               |
|PIA and approval currency                   |Check conditions, expiry, evidence completeness and affected-scope reapproval                                                   |Before expansion; at expiry/change; annual review|Privacy Designate + Business Owner     |

Each completed review should record: scope, period, configuration/version, reviewer, evidence link, result, exceptions, remediation owner, due date and closure evidence\.

## 9\. Tools and Evidence Sources

|Tool / evidence source                                            |Intended use                                                                   |Applicability and limitation                                                                                                                                                           |
|------------------------------------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Controlled Confluence page and approved issue tracker             |Playbook, decisions, evidence links and remediation tracking                   |Page permissions, owners and canonical links to be assigned; avoid raw PI or credentials in tickets                                                                                    |
|Entra / IAM and source permission records                         |Users, groups, service identities, entitlements and effective grants           |Required evidence; group membership alone does not prove row-level isolation                                                                                                           |
|Semantic Registry and governed recipe evidence                    |Dataset definitions, versions, dependencies and accepted calculations          |Documented foundation; metadata is not an authorization grant [R4–R5]                                                                                                                  |
|Azure/platform configuration and diagnostic records               |Storage, keys, networking, model settings and privacy-safe operational evidence|Actual services, access and retention to be confirmed                                                                                                                                  |
|Repository tests and release evidence                             |Pin control behavior to a source revision, build and deployed configuration    |A passing code test does not prove SpruceX configuration or approval                                                                                                                   |
|AMoAR / Akora Monitoring and Access Report                        |Possible zone/user/data-access review evidence                                 |Present in the supplied example only; askAlpha/SpruceX coverage and access are unconfirmed. The example says it does not establish retention or undesirable-combination compliance [R1]|
|DataDog zone dashboards                                           |Possible infrastructure/zone-activity evidence                                 |Present in the example only; integration and permissions are unconfirmed. Do not assume alerts for data movement or problematic combinations [R1]                                      |
|Future result cache, audit pipeline, Genie or Collibra integration|Potential later delivery capabilities                                          |Not current controls or prerequisites simply because they appear on the roadmap                                                                                                        |

## 10\. Retention, Disposal and Output Handling

No retention value is approved by this draft\. Complete a record for **each actual store**, including location, owner, classification, purpose, duration, access roles, deletion mechanism, backup behavior and applicable hold/exception process\.

|Information class                             |Required disposition decision                                                                                                            |
|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
|Source data or copied pilot datasets          |Distinguish governed query access from copied data; apply the approved source/copy schedule and pilot-closure conditions                 |
|Prompts, SQL, results and conversation history|Confirm whether persisted anywhere; minimize content and approve any history/diagnostic purpose and duration                             |
|Audit, logs and traces                        |Retain only approved evidence; document redaction, access and retention separately from query results                                    |
|Metadata and result caches                    |Distinguish cache types; define TTL/invalidation and access-change handling; do not assume a live secure result cache                    |
|Azure OpenAI-held content                     |Confirm enabled API/features, abuse monitoring, applicable retention and deletion constraints                                            |
|Reports, downloads and backups                |Approve destinations, access/classification controls, copies and end-of-use disposal; include endpoint/browser persistence where relevant|

Controls over downloaded or copied outputs require their own evidence; an encrypted source database does not automatically protect a downloaded report\. No disabling of clipboard, printing, screenshots or exports is asserted without implementation evidence\.

## 11\. Open Evidence and Approval Register

Every item is **Open in this draft**\. This means no closing evidence was established here, not that the control necessarily does not exist\. Named owners, links and due dates must be assigned before the affected route is authorized\.

|ID |Evidence / decision needed                                                                                 |Proposed lead                             |Gate                                            |
|---|-----------------------------------------------------------------------------------------------------------|------------------------------------------|------------------------------------------------|
|E01|Named owners, zone/resource identifiers, canonical foundational assessment and application PIA references  |Business + Zone Owner                     |Before approved publication/attestation         |
|E02|Approved business use cases, exact pilot inventory, PI/PCI assessment and source/copy/view mapping         |Data Owner + DAC                          |Before affected real-data use                   |
|E03|Effective user/service grants, necessary row/column controls, treatment and raw-denial tests               |IAM + Engineering + DAC                   |Before affected data access                     |
|E04|Complete at-rest store/key/access/backup evidence and retention/deletion schedules                         |Platform + store owners                   |Before affected persistence/retention           |
|E05|Per-hop TLS and actual private/public network, DNS and egress evidence                                     |Platform/Network                          |Before affected connectivity                    |
|E06|Azure OpenAI contract/TPRM references and use-case-specific Privacy/AI disposition                         |Privacy + AI Governance + vendor functions|Before production-origin PI/PII model processing|
|E07|Per-call payload contracts, model/deployment/API configuration, geography and monitoring/retention evidence|Engineering + Azure service owner         |Before affected model route                     |
|E08|Output, session, cache, logging and disclosure-negative tests                                              |Engineering + QA                          |Before affected release                         |
|E09|Agreed review cadence, tool coverage, incident contacts and exception handling                             |Controls/Operations + BISO/BSO            |Before pilot operational handover               |
|E10|Pilot duration, measures, exit authority and disposal plan                                                 |Business Owner + Product + Privacy        |Before pilot authorization                      |

For any finding, use a controlled record with a ticket, accountable owner, due date, affected scope, remediation and closure evidence\. Where policy permits an exception, also record authorized risk acceptance, compensating controls and expiry\. A ticket or project decision cannot substitute for required Privacy/contractual approval\.

## 12\. Incident and Review Closure

On suspected unauthorized access, raw\-data exposure, prohibited model transmission or output leakage, follow the applicable TD incident process\. The responsible operator should contain the affected route within their authority, notify the designated Security/Privacy contacts and preserve relevant protected evidence\. Do not copy exposed PI into ordinary tickets or broadly shared messages\. Re\-enablement requires remediation, verification and the applicable owner approval\.

This page may be circulated as a draft\. Before it is labelled approved or used to attest control sufficiency:

1. Assign the accountable owners and replace open references with verified evidence\.
2. Reconcile the narrow engineering pilot with the approved business\-data scope\.
3. Confirm each enabled control against the actual build, identity, services and configuration\.
4. Close the required three\-state evidence gaps and the separate Azure OpenAI PI/PII approval dependency\.
5. Obtain reviewer sign\-off and record the decision, conditions, scope, date and expiry/review trigger\.

## References and Change History

|Ref|Source reviewed                                                                                                                                                                |How it was used / boundary                                                                                                                                      |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
|R1 |**Analytic Zone Playbooks** — five screenshots supplied on 9 September 2026                                                                                                    |Structure, role categories, oversight tasks and tool limitations only; not a current-policy validation or askAlpha approval                                     |
|R2 |`askAlpha_SpruceX_PIA_Third_Party_Draft_2026-08-17.md`, version 2 scope correction                                                                                             |Real-data environment distinction, third-party disclosure and outstanding provider evidence                                                                     |
|R3 |`askAlpha_SpruceX_PIA_Questions_and_Answers_2026-08-12.md`                                                                                                                     |Proposed business-data scope and open treatment/access/data-state requirements; older synthetic-only and implied-approved-service wording is not carried forward|
|R4 |`askalpha_Executive_Update_for_Copilot.md`, September report, updated 9 September 2026                                                                                         |Documented engineering foundation/pilot; planned capabilities; AI-formatting approval boundary                                                                  |
|R5 |`AskTD_04_Assumption_Decision_Log_2026-08-23.md`, updated 26 August 2026                                                                                                       |Entity-level authorization baseline, SQL path, canonical registry and future-integration boundaries; not a live repository-state check                          |
|R6 |[Microsoft: Data, privacy and security for Models sold by Azure](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy), reviewed 9 September 2026|Provider technical context only; does not establish applicable TD contract or processing permission                                                             |
|R7 |[Microsoft: Configure Azure OpenAI networking](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/network), reviewed 9 September 2026                       |Private-endpoint configuration pattern only; not proof of deployed topology                                                                                     |
|R8 |Sean’s PIA discussion supplied in this conversation                                                                                                                            |Requirement for three-state security evidence and TD-specific assurance for PI/PII AI processing; no later approval inferred                                    |

|Version|Date            |Change                                                                                                     |Approval|
|-------|----------------|-----------------------------------------------------------------------------------------------------------|--------|
|0.1    |9 September 2026|Initial project-specific draft; separates baseline, required controls, proposed oversight and open evidence|Pending |

**Publication note:** Transfer this content into a controlled Confluence draft, add the native table\-of\-contents element if desired, and replace evidence references with approved internal links\. Do not mark the page or its controls approved solely because the page has been published\.
