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





