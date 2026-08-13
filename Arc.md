flowchart TB
    USER["Employee"] -->|"Login and question"| UI["AskTD UI / Application Server"]
    UI <-->|"JWT and AD-group claims"| ENTRA["Microsoft Entra ID"]
    UI -->|"Validated request and user context"| AGENT["User-triggered Agent Engine"]

    AGENT <-->|"Authorized metadata"| SEARCH[("Azure AI Search")]
    AGENT <-->|"Versioned semantics"| REGISTRY[("AskTD Semantic Registry")]

    AGENT <-->|"Minimized approved context"| PRIVACY["PII/PCI and Prompt Controls"]
    PRIVACY <-->|"Prompt and response"| GATEWAY["Enterprise LLM Gateway"]
    GATEWAY <-->|"Approved model"| AOAI["Azure OpenAI"]

    AGENT -->|"Read-only semantic plan / SQL"| POLICY["Authorization and Query Guard"]
    POLICY --> AUTH["TBD: End-user authorization propagation"]
    AUTH -->|"JDBC / approved mechanism"| UC["Databricks SQL and Unity Catalog"]
    DELTA[("Rahona ADLS Curated Delta Data")] --> UC
    UC -->|"Authorized and masked result"| POLICY
    POLICY --> AGENT

    AGENT -->|"Answer and progress"| UI
    UI --> USER

    AGENT <-.->|"Temporary session/job state"| REDIS[("Optional Azure Managed Redis")]
    AGENT -->|"Redacted AI traces"| OBS["Enterprise AI Observability / LangSmith"]
    POLICY -->|"Security and data-access events"| AUDIT["TBD: Authoritative Audit Store"]
