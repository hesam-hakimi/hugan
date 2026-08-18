below are the highest-priority gaps/dependencies we have identified so far while progressing AskTD in SpruceX. This is not intended to be an exhaustive list, as we are still validating the end-to-end architecture.

* High – End-user authorization: AskTD can identify the signed-in user through Entra ID, but the authoritative enterprise mechanism to determine and enforce what data that user is permitted to access is still open. A service/API to retrieve user-level access was discussed, but it is not currently available and requires an owner and implementation path.
* High – Enterprise metadata integration: AskTD requires governed technical and business metadata for semantic planning. We need to confirm the authoritative sources (e.g., Collibra, Unity Catalog, or both) and the supported enterprise API/service for retrieving and keeping this metadata synchronized.
* High – Governed data-access pattern: SpruceX supports bringing approved Rahona data through DAC, while AZ/Consumption views and future direct-access patterns are also being discussed. We need Architecture/Data Platform confirmation of the approved interim and target patterns, including refresh/freshness, ownership, and scalability for large data products.
* High – Query serving performance / compute model: AskTD requires a low-latency query-serving path. The current AZ cluster model can introduce several minutes of startup delay after inactivity. We need Architecture/Data Platform to confirm the approved serving option, such as SQL Warehouse if supported, along with the expected latency/concurrency SLA and cost/ownership model.
* High – Runtime identity and connectivity: The supported workload identity, AD-group model, firewall/network paths, and connectivity from AskTD to the approved data and enterprise metadata services need to be validated end to end in SpruceX.

PIA, DAC, and production-data governance activities are already progressing in parallel with the appropriate teams.

We are working with the Architecture, Rahona/Unity Catalog, and SpruceX teams to identify owners and resolve the interim versus target architecture for the items above.

ث 
