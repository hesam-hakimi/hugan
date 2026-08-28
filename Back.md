Thanks for raising this point.

For the authorization part, I do not think we should synchronize AskTD user permissions with SQL Server or Unity Catalog permissions.

In the current MVP design, AskTD is the source of truth for end-user authorization at the entity level. AskTD checks the signed-in user’s access before metadata retrieval or query execution.

AskTD then connects to the data source using Managed Identity (MSI). The data source only needs to verify that the AskTD application identity has access to the approved schemas, views, or datasets.

So the flow should be:

User signs in
→ AskTD checks entity access
→ If unauthorized, AskTD returns an appropriate access-denied message
→ If authorized, AskTD connects to the source using MSI
→ The source validates the AskTD MSI


If the user is authorized in AskTD but the MSI cannot access the source, the application should fail closed and return a safe service-access message with a correlation ID. That would be treated as a platform or configuration issue, not a user-permission issue.

A continuous synchronization or reconciliation process between AskTD permissions and every provider’s ACLs would introduce significant complexity and maintenance overhead. I would not add that unless we later decide to pass the actual end-user identity to the data platform and use provider-native user-level authorization
