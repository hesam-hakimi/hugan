CLUE — Open Questions for the Delivery Meeting

Purpose: Close the decisions needed for connected testing, accepted batch outputs and VMC2 delivery.

|Meeting details               |Fill in             |
|------------------------------|--------------------|
|Prepared                      |2026-09-17          |
|Meeting date / time / timezone|____________________|
|Facilitator / note-taker      |____________________|
|Shared tracker or minutes link|____________________|

Opening statement

> I would like us to confirm the remaining interface and delivery decisions so we can keep the implementation moving. For each open item, can we agree the answer, any evidence still needed, and who will follow up by when?

Priority agenda

• P0 — Discuss first: needed for the affected connected component test, full file exchange or business output acceptance.
• P1 — Resolve before the affected load setting or operational release: capacity, runtime and operating decisions.
• Respondent roles below are suggested participants. Record the actual accountable owner in the decision register.
• An unresolved item constrains its affected capability; continue unrelated implementation and packaging.

|ID                                                               |Topic                                                |Priority|Suggested respondent                                                         |
|-----------------------------------------------------------------|-----------------------------------------------------|--------|-----------------------------------------------------------------------------|
|[Q01](#q01-transfer-route)                                       |Transfer route                                       |P0      |ADIDO owner; TIBCO/MFT owner; VMC2 architect                                 |
|[Q02](#q02-tungsten-dev-request-configuration)                   |Tungsten DEV request configuration                   |P0      |Tungsten API/process owner                                                   |
|[Q03](#q03-complete-symcor-sample-and-remaining-contract-details)|Complete Symcor sample and remaining contract details|P0      |Team that supplied the Java sample; Symcor interface owner for remaining gaps|
|[Q04](#q04-input-contract-and-complete-file-signal)              |Input contract and complete-file signal              |P0      |Rahona producer; business data owner; transfer owner                         |
|[Q05](#q05-output-examples-and-partial-results)                  |Output examples and partial results                  |P0      |Business/investigator representative; Rahona output consumer                 |
|[Q06](#q06-tungsten-response-and-metadata-mapping)               |Tungsten response and metadata mapping               |P0      |Tungsten process owner; business metadata owner                              |
|[Q07](#q07-api-capacity-and-retry-behavior)                      |API capacity and retry behavior                      |P1      |Symcor and Tungsten service owners, separately                               |
|[Q08](#q08-workload-and-completion-target)                       |Workload and completion target                       |P1      |Business workload owner; delivery lead                                       |
|[Q09](#q09-vmc2-runtime-and-mvp-recovery-scope)                  |VMC2 runtime and MVP recovery scope                  |P1      |Solution architect; PDL/VMC2 owner; release/delivery owner                   |
|[Q10](#q10-calendar-archive-retention-and-output-receipt)        |Calendar, archive, retention and output receipt      |P1      |Business operations; transfer operations; VMC2/storage owner                 |
|[Q11](#q11-dynatrace-delivery-configuration)                     |Dynatrace delivery configuration                     |P1      |Monitoring/Dynatrace team; application/platform owner                        |

Use the quoted question to open each topic. Use the follow-ups only where the main answer leaves a gap. Capture the result in the register at the end.

Q01. Transfer route

Priority: P0 · Unblocks: Transfer setup and full batch delivery

Ask: ADIDO owner; TIBCO/MFT owner; VMC2 architect.

Context: The route to the application folder on VMC2 is still unconfirmed. Earlier guidance said TIBCO could not pull from ADIDO; the meeting also referred to a pickup location.

> Can we confirm how a file will move from ADIDO into the CLUE landing folder on VMC2, and how the processed output will get back?

Follow up if needed:

• Which service initiates each transfer, using which protocol, endpoint and directory? Who owns each step and its service identity?
• Does TIBCO have a supported pickup location, require an ADIDO-side push, or need another handoff? Does its delivery reach the application folder on VMC2?
• What remains to complete the intake, and what is the provisioning ETA? If a similar production route exists, which implementation or team can we refer to?

Evidence or decision requested: A confirmed route diagram/table, handoff paths, ownership and intake/ETA details.

Q02. Tungsten DEV request configuration

Priority: P0 · Unblocks: First connected Tungsten component test

Ask: Tungsten API/process owner.

Context: The endpoint and request shape are available. The meaning and valid values of Config and sessionId remain unresolved.

> What process configuration and session setup do we need to run one valid Tungsten DEV request?

Follow up if needed:

• What belongs in InputVariables[Config], and which process/profile settings apply to CLUE?
• Is sessionId static, acquired through an operation, or optional for this operation? If acquired, how is it created, reused and renewed after expiry?
• Which permitted test image and document/ISN identifiers can we use, and what result should that sample produce?

Evidence or decision requested: A valid request/configuration example and permitted test inputs. Keep secret values out of the meeting notes.

Q03. Complete Symcor sample and remaining contract details

Priority: P0 · Unblocks: Native Symcor adapter completion and connected testing

Ask: Team that supplied the Java sample; Symcor interface owner for remaining gaps.

Context: The Java excerpts demonstrate an MTOM-capable client. Request construction, attachment mapping and HTTPS setup are delegated to code not visible in the excerpts.

> Can you share the complete Symcor sample, including the request builder, response transformer and HTTPS helper, together with a sanitized successful request and response?

Follow up if needed:

• Locate the AwsSearchRequest construction, transformedCisResponse implementation, HTTPS sender helper and matching WSDL/XSD. Include MIME headers and attachment references in the response sample.
• After reviewing those files, resolve any remaining request gaps: timeStamp semantics, supported Account search versus required TransitBankAcct composition, and docsFetchLimit versus documentFetchLimit naming.
• Confirm the intended endpoint/environment, authentication and certificate requirements, timeout settings and the owner of the outstanding TLS diagnosis.

Evidence or decision requested: Native source dependencies, connection configuration and a successful wire example for the applicable interface. Ask externally only for facts still unresolved after source review.

Q04. Input contract and complete-file signal

Priority: P0 · Unblocks: Reliable file intake and input acceptance

Ask: Rahona producer; business data owner; transfer owner.

Context: Multiple daily files and timestamped filenames are expected. Detailed reconciliation was parked, while the completion-signal discussion remained open.

> Can we agree the exact input file contract and how CLUE will know that each delivery has arrived completely?

Follow up if needed:

• Confirm the file format/schema, delivery and source-row identifiers, filename convention including timezone/collision handling, and the meaning of a replayed delivery.
• Confirm cheque/debit/credit identification rules, eligible transaction/channel codes and the account, processing-date and ISN mappings.
• Will the sender provide a .done marker, manifest or equivalent transfer-completion event? Who publishes it, when, and how is it linked to the data file?

Evidence or decision requested: A versioned input contract, representative input files and an explicit completion/replay agreement.

Q05. Output examples and partial results

Priority: P0 · Unblocks: Business acceptance of the returned output

Ask: Business/investigator representative; Rahona output consumer.

Context: One logical output per input file, returned after that batch completes, is understood. The physical layout and exceptional-case behavior remain open.

> Can we approve output examples for a debit with one cheque, a credit with several cheques, and cases with missing or partial results?

Follow up if needed:

• How are multiple cheques linked to the original row and request? Confirm the output format, preserved columns, metadata placement and image embedding or references.
• Which cases may be delivered partially, and which must remain pending? Distinguish no matching document, unreadable/missing fields, missing pages, failed calls and unknown provider outcomes.
• Where will those outcomes be represented: the agreed business file, a companion status file, or another agreed mechanism?

Evidence or decision requested: Approved examples for the three scenarios and a clear partial-result/exception policy.

Q06. Tungsten response and metadata mapping

Priority: P0 · Unblocks: Validated extraction and field mapping

Ask: Tungsten process owner; business metadata owner.

Context: An eight-field business sample exists. The response parser is provisional, and front/back precedence is not an approved business rule.

> Can we confirm how the actual Tungsten response maps to our existing eight metadata fields and their confidence values?

Follow up if needed:

• Provide the native response paths and types, including where OUTPUT_JSON appears. Use an existing complete response if available; otherwise capture the first permitted DEV call.
• Is confidence per field, page or document, and what scale and missing-value rules apply?
• How should conflicting front/back values be handled? Confirm page attribution and any field-specific precedence.

Evidence or decision requested: A complete response example and a mapping table covering field path, type, confidence and page/conflict rules. A saved response is not a prerequisite to making the first permitted call.

Q07. API capacity and retry behavior

Priority: P1 · Unblocks: Controlled parallel processing and load settings

Ask: Symcor and Tungsten service owners, separately.

Context: The meeting’s 100 TPS figure is unconfirmed. The Java sample’s actualSize <= 100 check is a result-count threshold in that consumer.

> What rate, concurrency and request-size limits apply to our client in each environment, and how should we handle throttling or an uncertain response?

Follow up if needed:

• Request limits per operation, client and environment: requests per second, concurrent requests, payload/response size, and recommended timeout or latency expectations.
• Which faults are retryable, what backoff or Retry-After behavior applies, and what happens if we retry after the provider may already have processed the request?
• Is status lookup, reconciliation or idempotency available for the relevant operation? Confirm any retrieval/result limits needed by the selected Symcor profile.

Evidence or decision requested: Written limits and error/retry/status guidance for each provider. Keep these discussions provider-specific.

Q08. Workload and completion target

Priority: P1 · Unblocks: Capacity assessment and a realistic completion target

Ask: Business workload owner; delivery lead.

Context: 250,000 per month is a planning estimate with an unresolved unit. A 10,000-row file was discussed as a scenario.

> What does the monthly volume count, and how quickly does the business need each batch returned?

Follow up if needed:

• Does 250,000 mean investigator requests, input records or cheques? Reconcile it with earlier daily estimates using the same units.
• What are the largest file, peak arrival pattern, average/peak cheques per credit record and representative image sizes?
• What turnaround and backlog are acceptable, including peak days? Which workload should be used for acceptance?

Evidence or decision requested: A representative workload profile and an explicit turnaround/backlog target.

Q09. VMC2 runtime and MVP recovery scope

Priority: P1 · Unblocks: Target-environment setup and MVP release scope

Ask: Solution architect; PDL/VMC2 owner; release/delivery owner.

Context: The local implementation reportedly includes SQLite state and recovery. The meeting discussed deferring database infrastructure and resume to a later version.

> Can we confirm whether the existing local SQLite state store and recovery capabilities are acceptable for the target MVP on VMC2?

Follow up if needed:

• Did the database deferral concern provisioning a new database service, or does it also exclude embedded local storage? Record the accepted MVP capability scope.
• Confirm the durable local filesystem/path, execution identity and permissions, supported runtime and package installation approach.
• Confirm which restart/recovery behavior operations will support, including held outcomes and legitimate replay.

Evidence or decision requested: An explicit scope decision and VMC2 runtime/storage configuration. Preserve existing implementation while this deployment decision is resolved.

Q10. Calendar, archive, retention and output receipt

Priority: P1 · Unblocks: Operational handover

Ask: Business operations; transfer operations; VMC2/storage owner.

Context: 500 GB was a production planning figure. One-week/month retention examples and day-boundary archive movement were not final operating rules.

> What operating rules should we use for the business calendar, archiving, retention and confirmation that each output was received?

Follow up if needed:

• Should arrivals run on weekends/holidays or wait for the next business day? What happens to unfinished or undelivered work when the date changes?
• What capacity is actually provisioned and usable? Confirm retention by artifact type, cleanup ownership and the archive location.
• What acknowledges output receipt or acceptance, which team supplies it, and how is it correlated to the original delivery?

Evidence or decision requested: An operating schedule, retention/storage settings and an output-acknowledgement agreement with owners.

Q11. Dynatrace delivery configuration

Priority: P1 · Unblocks: Central logging verification and operational support

Ask: Monitoring/Dynatrace team; application/platform owner.

Context: Local logging and a forwarding integration have been reported. Successful delivery to the CLUE Dynatrace destination has not been demonstrated.

> Which supported Dynatrace collection setup applies to CLUE, and who can confirm receipt of a test log event?

Follow up if needed:

• Confirm the collection path, supported package/version and installation source, destination, and application/environment attribution such as MALCODE and application name.
• Confirm how runtime configuration is supplied and who verifies a test event using its correlation ID. Keep secret values outside the notes.

Evidence or decision requested: The CLUE logging configuration and a successful correlated ingestion check with the monitoring owner.

Decision and follow-up register

Update this register during the meeting. Use Open, In progress, Closed or Parked. Mark an item Closed when its answer/decision and the evidence needed for that item are recorded. A promise to investigate remains a follow-up.

|ID |Answer / decision and affected scope or version|Status|Accountable owner / team|Due date|Evidence / next action|
|---|-----------------------------------------------|------|------------------------|--------|----------------------|
|Q01|—                                              |Open  |—                       |—       |—                     |
|Q02|—                                              |Open  |—                       |—       |—                     |
|Q03|—                                              |Open  |—                       |—       |—                     |
|Q04|—                                              |Open  |—                       |—       |—                     |
|Q05|—                                              |Open  |—                       |—       |—                     |
|Q06|—                                              |Open  |—                       |—       |—                     |
|Q07|—                                              |Open  |—                       |—       |—                     |
|Q08|—                                              |Open  |—                       |—       |—                     |
|Q09|—                                              |Open  |—                       |—       |—                     |
|Q10|—                                              |Open  |—                       |—       |—                     |
|Q11|—                                              |Open  |—                       |—       |—                     |

Meeting close

☐ Read back the agreed decisions and the scope/version they apply to.
☐ Confirm one accountable owner and an explicit due date for each follow-up.
☐ Record why each parked item is parked and when it will be revisited.
☐ Link the supporting samples, configuration or decisions in the shared tracker.
☐ Confirm the next connected test or delivery step that can proceed.

Context to preserve

• Multiple timestamped input files may arrive in a day. A corresponding logical output is expected for each input, returned after its batch completes.
• Debit search is expected to use account, processing date and ISN; credit search may return multiple cheques. Exceptional cardinalities still need defined handling.
• The current profile plans a front and back Tungsten submission per cheque. This is not a demonstrated provider-wide limit.
• The Java sample supports SOAP/MTOM attachments. Its complete helper code and the applicable endpoint response are needed for exact image mapping.
• The sample’s local timing calls do not establish the format of the outgoing SOAP timeStamp field.
• Existing metadata names, operator mappings, segment interpretation and recovery work should be reused. Validate only the remaining gaps.

Basis: The supplied CLUE meeting transcript (00:00–38:09), the latest reported implementation checkpoint, and the supplied SymcorSoapClient.java excerpts. The transcript’s meeting date was not supplied; the prepared date above is the document date. No new live connectivity or business acceptance is claimed by this guide.
