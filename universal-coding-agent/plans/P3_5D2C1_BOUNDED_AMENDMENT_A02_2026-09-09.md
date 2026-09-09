# P3.5d-2c-1 bounded amendment A02 — retain the older-version requirement

Task: `UCA-20260908-P35D2C1-LOCAL-PRODUCT-COMMANDS`.
This supplements A01 and is recorded before the additional checker assertion.
The canonical task's recorded-amendment provision remains the authority; no
additional Product or pilot task is instantiated.

The first deterministic A01 run at staged tree
`77c60d0c692a62714d991d6211076faaf3841177` (HEAD
`a67d4ee4046aa484568c85ef31afbfd9e3e08060`) had five passes and one failure.
Its deliberately incorrect `candidate_version == stored_version` implementation
was not rejected by the existing checker. The existing mixed-event example has
an older delete, but an equal-version candidate wins for that key before apply.
It therefore cannot establish rejection of an older winning candidate. This
finding and the original failed log remain retained; no pass is fabricated.

The only additional permitted edit is in A01's already named
`src/universal_coding_agent/testlab/hard_reasoning.py`: add an explicit older
winning delete and older winning upsert, with no competing event, and require
the complete existing state to remain equal. These cases exercise the existing
strictly-newer requirement through `run_incremental`. No existing assertion is
removed or weakened; fixture/reference code, prompts, policies, workflows and
all qualification thresholds remain unchanged.

The A01 focused test consumer must then prove the known valid implementation
passes both documented vocabulary forms, required documentation is still
checked, and both equal-update and older-update mutants fail. This correction
strengthens verification of an existing contract; it implements no ETL feature
and publishes no generated source. It supersedes only A01's statement that the
functional checker statements would remain textually unchanged.

Required separate review and exact corrected-candidate CI/Live/Web, normal Ready,
and expected-head integration gates remain intact. Live199 stays failed history.
This document records the bounded change before its edit and does not certify
future results or its own publication. Pilot readiness and validation remain false.
