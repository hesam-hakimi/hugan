Continue the current CLUE delivery task and incorporate the newly supplied Symcor Java sample into the existing Python adapter work.

Preserve the current branch, implementation, tests, and delivery progress. Keep all engineering responses and artifacts in English and inspect source through text/filesystem tools.

Locate the original SymcorSoapClient.java in the available workspace/reference files. Read its response transformer, HTTPS sender helper, and the code that constructs AwsSearchRequest. Search by the actual referenced symbols, including transformedCisResponse and httpComponentsMessageSender. If a dependency is unavailable, identify its exact name once and continue the work supported by the available evidence.

The visible sample establishes these implementation leads:

* Jaxb2Marshaller has MTOM enabled.
* The response is accessed as a SOAPMessage and its attachments are retrieved.
* Attachments and the unmarshalled AwsSearchResponse are passed together to transformedCisResponse.
* HTTPS configuration is delegated to a helper.
* getActualSize() <= 100 is a result-count threshold in this consumer.
* SOAP faults distinguish system, invalid-request, and application exceptions.

Apply these findings to the existing Python adapter:

1. Support the demonstrated SOAP attachment path. Parse the response according to its Content-Type using the original response bytes and required MIME headers. Preserve supported inline-image handling.
2. Resolve SOAP/XOP image references against the appropriate attachment Content-ID. Preserve provider document identity and page role; do not assign front/back by attachment order.
3. Pass the extracted image bytes and provenance into the existing image-processing and durable Tungsten stages. Identify the actual image format before any required JPEG conversion.
4. Reuse the current documented hit-list interpretation and fault handling. Do not introduce a global limit of 100 or treat it as TPS. Map SOAP faults according to the available contract.
5. Inspect the actual request-construction code for unresolved request fields. The visible System.currentTimeMillis() calls measure local timing and do not establish the outgoing SOAP timeStamp format.

Verify the parser through a focused multipart response fixture with front/back attachments deliberately supplied in a different order from their SOAP references. Verify that a missing referenced attachment produces an explicit incomplete/error outcome and does not send the wrong image to Tungsten. Reuse existing fixtures where possible; label standards-based fixtures accurately when a native response sample is unavailable.

Integrate this through the existing application and continue the input-to-output acceptance run and release packaging already requested. Retain the owner’s decision to defer credential replacement. Finish with the implemented behavior, generated output artifacts, validation results, and only the specific external inputs still needed.
