# askAlpha / SpruceX — PIA Third-Party Section Draft

**Version:** 2 (scope correction)  
**Date:** 2026-08-17  
**Status:** Draft for PIA completion; not evidence of final Privacy, TPRM, Security, AI Governance, DAC, or contractual approval.

## Scope correction

SpruceX is a pre-production Azure environment that provides **governed, role-based access to approved real / production-origin data**. Therefore, this PIA must not describe the environment as synthetic-data-only.

That environment-level access is distinct from the content sent to Azure OpenAI. The application must retrieve only authorized data through the approved governed path (for example, DAC-treated views), apply user and runtime-identity authorization before retrieval, and send Azure OpenAI only the **minimum necessary approved rows, columns, derived measures, and prompt context** for a request. Access to real data does not authorize unrestricted prompt payloads or raw/base-table access.

For this initiative, Microsoft Azure OpenAI is the third-party service provider. The solution does not use ChatGPT or the public OpenAI API.

> **Project data classification note:** SpruceX can support governed access to Confidential and Restricted data. That environment capability does not expand the askAlpha scope. PCI-DSS data remains outside the intended Phase 1 scope, subject to final approved field-level inventory confirmation.

## Evidence still required before final submission

| Required fact | Why it is required | Obtain from |
|---|---|---|
| Microsoft/Azure vendor relationship owner and start date | Required by Question 1 | Foundational PIA owner, TD Azure service owner, Vendor Management, or AI Governance |
| TPRM E# and risk rating | Required by Questions 3 and 4 | TPRM / Vendor Management / Foundational PIA |
| Azure OpenAI resource geography and deployment type (`Standard`, `Data Zone`, or `Global`) | Required by Question 2 and storage/residency answers | Azure service owner / solution architecture |
| Abuse-monitoring configuration and retention period | Required by Questions 16 and 17 | Azure service owner, TPRM evidence, and Foundational PIA |
| Proof of approved payload controls and runtime access | Required to distinguish SpruceX data access from Azure OpenAI disclosure | DAC, Security, Privacy, AI Governance, and technical test evidence |

---

## 1. Third-party name, service, existing-vendor status, and TD relationship owner

**Form question**

> Please provide the third Party name; the service they will provide; whether they are an existing vendor (and since when); and who in TD owns the relationship with the vendor.

**Proposed response**

Microsoft Corporation — Azure OpenAI Service.

Microsoft provides a managed cloud AI service that processes application prompts, approved retrieved context, and generated outputs for model inference, together with applicable service-level safety and abuse-monitoring functions.

Microsoft is an existing TD enterprise cloud vendor. The Azure OpenAI service onboarding/contract effective date and the TD owner of the enterprise Microsoft relationship are **TBD** and must be confirmed from the Foundational PIA, applicable TPRM engagement, or the TD Azure/AI Governance service owner.

The askAlpha project team must not be recorded as the vendor relationship owner unless that ownership is formally confirmed.

---

## 2. Jurisdiction(s) where the third party processes Personal Information

**Form question**

> Which jurisdiction(s) is the personal information being processed in by the Third party?

**Current response status: `TBD — do not finalize the country table yet.`**

The answer must be based on the Azure OpenAI resource's actual region and deployment type, not solely on the fact that the source data is TD US Data or that SpruceX provides access to real data.

**Table-selection guidance after configuration is confirmed**

| Azure OpenAI configuration | Form treatment |
|---|---|
| Standard deployment in a United States Azure region | Select `United States` for **Use**. Select **Storing** only where the confirmed service configuration stores data; select **Access** only where the documented configuration confirms it. Do not select **Collection** or **Sharing** for Microsoft in this table. |
| Data Zone deployment | Record the applicable data-zone geography exactly as documented; do not assume a single U.S. region. |
| Global deployment | Do not state that processing is U.S.-only; document the Global deployment geography and obtain Privacy/TPRM confirmation. |

**Interim wording for the form, if text is required**

> Pending confirmation of the Azure OpenAI resource region, deployment type, and abuse-monitoring configuration. The project will document all processing jurisdictions from the approved Azure service configuration and Foundational PIA before final submission.

---

## 3. TPRM engagement number

**Form question**

> What is the Third Party Risk Management (TPRM) engagement number (E#)?

**Proposed response**

> TBD — Microsoft/Azure is an existing enterprise vendor. The applicable TPRM E# must be obtained from the Foundational PIA owner, TD Azure service owner, AI Governance, or Vendor Management.

Do not invent an E#.

---

## 4. TPRM risk rating

**Form question**

> What is the Risk Rating of the TPRM engagement?

**Proposed response**

> TBD — select the rating only after the associated TPRM E# and official risk rating are confirmed.

Do not choose a risk rating based on the project team's assessment.

---

## 5. Is the third party collecting on behalf of TD and/or sharing Personal Information?

**Form question**

> Is the third party collecting on behalf of TD and/or sharing personal information?

**Selection:** `None of the above`

**Supporting explanation**

Azure OpenAI does not directly collect Personal Information from individuals on TD's behalf and is not engaged to share Personal Information with another party. Microsoft processes the limited inputs TD provides as a service provider. TD's provision of Personal Information to Microsoft, if approved, is addressed in Question 6.

---

## 6. Will TD be sharing/providing Personal Information to the third party to perform this activity?

**Form question**

> Will TD be sharing/providing personal information to the third party to perform this activity?

**Selection:** `Yes`

**Supporting explanation**

Yes. SpruceX provides governed access to approved real / production-origin data, and askAlpha may provide Microsoft Azure OpenAI with the minimum necessary authorized content in application prompts and retrieved context to generate a response.

Before a request is made, the solution must enforce applicable user authorization, runtime-identity permissions, DAC treatment, row/column restrictions, and payload minimization. Azure OpenAI must not receive unrestricted source data, raw/base-table data, or data outside the approved payload scope. Production-origin Personal Information processing through Azure OpenAI remains subject to applicable Privacy, Security, AI Governance, DAC/data-governance, TPRM, and contractual approvals.

---

## 16. Retention period at the third party

**Form question**

> How long will the personal information be retained by the third party? (time period)

**Proposed response**

> TBD — Azure OpenAI model inference is stateless and does not store prompts or completions in the model. However, service-level abuse monitoring or optional stateful Azure OpenAI features may retain applicable content under the approved Microsoft/TD service configuration. The exact retention period, whether modified abuse monitoring is enabled, and whether any stateful feature is in use must be confirmed from the Foundational PIA, TPRM evidence, and Azure OpenAI service configuration before final submission.

Do not enter `0 days`, `30 days`, or another fixed period unless the applicable TD-approved service documentation confirms it.

---

## 17. Rationale for the retention period

**Form question**

> What is the rationale for the retention period?

**Proposed response**

Any retention must be limited to the minimum period necessary for Microsoft to operate the Azure OpenAI service, including applicable safety and abuse-monitoring requirements under the approved service configuration.

There is no business requirement for askAlpha to retain Azure OpenAI prompt or completion content beyond approved operational logging and audit requirements. The final retention period must align with the applicable TD/Microsoft contractual terms, TPRM evidence, and Privacy-approved configuration.

---

## 18. Storage location

**Form question**

> Where will the personal information be stored?

**Selection:** `Cloud`

**Supporting explanation**

Microsoft Azure cloud — Azure OpenAI Service. Source data and DAC-treated views remain in SpruceX / TD-managed stores; Azure OpenAI receives request-scoped, minimum-necessary approved content. Any Azure-held content depends on the approved abuse-monitoring and stateful-feature configuration. The exact Azure region/geography, deployment type, and any service-level stored-data component must be confirmed before final PIA submission.

---

## Questions not yet captured

Questions **7–15** were not visible in the supplied screenshots. Add them to this document once screenshots or the form text are available; do not infer their wording or selections.

## Technical reference (not a TD approval)

Microsoft documents that Azure-hosted models process prompts and generated content; optional features and abuse monitoring can affect storage and processing location. This public documentation is technical context only and does **not** replace TD's Foundational PIA, TPRM evidence, contractual terms, or approval decisions.

- [Microsoft Learn — Data, privacy, and security for Models sold by Azure](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy)
