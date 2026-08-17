2. “Should AskTD use Managed Identity or a Service Principal to connect to Databricks SQL?”
3. “Databricks will see the AskTD application identity. How should we enforce the permissions of the signed-in user?”
4. “Can the user’s Entra identity or group membership be passed to Databricks, or must AskTD enforce authorization itself?”
5. “How will row-level security be enforced? The Trusted, Confidential, and De-risked views mainly address column masking.”
6. “How do we meet least privilege if a user needs only three unmasked columns rather than the complete standardized view?”
7. “What is the source of truth for access: Entra groups, AZ groups, Unity Catalog grants, or an AskTD entitlement mapping?”
8. “Can AskTD read Unity Catalog metadata only for datasets that the user is authorized to access?”
9. “Who creates and maintains the secondary views, and how are schema changes handled?”
10. “Is zero-copy approved for this architecture, and has the performance and concurrency been tested?”
11. “What network configuration is required between App Service or SpruceX and Databricks SQL?”
12. “How will audit logs show which end user asked the question and which tables, columns, and rows were accessed?”
