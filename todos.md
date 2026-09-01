Hi Neha,

Sean asked us to document how information is secured across the three data states:

1. Data at rest

Production-origin data remains within the governed SpruceX data environment. askAlpha is designed to have read-only access only to approved DAC-treated/AZ views and not to the underlying raw or base tables.

Any information persisted by the supporting Azure services is protected using Azure encryption-at-rest capabilities. The Azure OpenAI model itself is stateless and does not store prompts or completions in the model. However, we still need the platform owner to confirm the actual encryption-key configuration, Azure region and deployment type, backup protection, application-log and cache retention, and whether Azure OpenAI abuse-monitoring storage or any stateful features are enabled.

Sensitive source values must not be written to application logs, traces, caches, diagnostic records, or exported files unless explicitly approved. Audit records should contain non-sensitive references such as request IDs, dataset IDs, policy versions, row counts, and query hashes.

2. Data in transit

The user-to-application and application-to-Azure-service communication paths use HTTPS/TLS. Users authenticate through Microsoft Entra ID, while the backend uses Managed Identity for supported Azure service-to-service access, avoiding stored service credentials.

The intended SpruceX network design should use private endpoints, approved VNet routing, firewall controls, private DNS, and restricted egress, with public network access disabled where applicable. We still need the SpruceX/platform team to provide configuration evidence confirming the deployed private endpoints, TLS settings, firewall rules, DNS path, and public-network-access status.

3. Data in use / processing

Before any data is retrieved or processed, the initiating user is authenticated through Entra ID and their effective authorization scope is resolved from approved group and entitlement information. Authorization must be enforced before metadata discovery, querying, aggregation, Azure OpenAI processing, caching, visualization, reporting, download, or export. If entitlement cannot be resolved, access must fail closed.

askAlpha performs bounded, read-only queries against approved governed views. DAC treatment and row/column authorization must be applied before data reaches the application. Deterministic application controls—not the AI model—must enforce SQL restrictions, redaction, treatment, and minimum-necessary selection.

Azure OpenAI receives only the minimum necessary, request-specific and approved prompt context, treated rows, columns, aggregates, or derived measures. It must not receive unrestricted datasets, raw/base-table data, or fields outside the approved payload. The generated output is validated before being returned to the authorized user.

We are collecting the remaining SpruceX, DAC, networking, logging, retention, and Azure OpenAI configuration evidence from the platform owner/BISO. These technical controls do not replace the separate TD Privacy, AI Governance, TPRM, and contractual confirmation that production PI/PII is permitted to be processed by Azure OpenAI; that confirmation remains an approval dependency.
