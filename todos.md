As discussed, I wanted to provide some context on why the current unavailability of Azure AI Search and MRA in SpruceX is becoming a blocker for our AskAlpha validation.

Azure AI Search is part of our current application architecture and is used for the RAG/semantic retrieval layer. It allows AskAlpha to retrieve the relevant business definitions, metadata, examples, and semantic context before sending the required context to the LLM for planning and response generation.

Without Azure AI Search in SpruceX, we cannot properly validate the same end-to-end flow that we intend to use for the application. We could temporarily replace or bypass it, but that would mean testing a different architecture and would require additional development and rework later.

For MRA, we also need to validate the architecture components that depend on it in the target environment. If MRA is not planned to be available in SpruceX, we would need to understand the approved alternative before implementing an environment-specific workaround.

Could you please help us confirm:

* Whether Azure AI Search and MRA are planned to be available in SpruceX.
* If yes, the expected timeline.
* If not, what approved services/patterns should be used instead.

This will help us avoid building temporary solutions that may not align with the supported SpruceX architecture.

Thanks,
Hesam
