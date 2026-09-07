# Preserve the caller's objective through requirement alignment

## Diagnosed integration failure

Live 171, run `34113965693`, attempt 2 (job `101720016146`), ran after the owner
confirmed API credit replenishment. The exact checkout was GitHub merge preview
`b895bfba2fa8a9b7ed02660473a4bf23bea4bf8c`, tree
`d803c52af1bf7f261ec99ebb65c66c8454384316`, source-equivalent to PR20 head
`f932a98b70c983895076b5f70b73658852dd10a9`.

Billing was no longer the blocker. Five Live outcome groups passed; the Product
foundation scenario failed with `large change was not decomposed into multiple phases`.
The Product JSON reports `qualified: false` and `source_preserved: true`. The final
aggregator correctly failed. Product's intermediate step conclusion must not be used as
acceptance: `continue-on-error` allows other diagnostics to run, whereas its underlying
outcome remains `failure`.

The downloaded Product diagnostics artifact is `10016010446`. Its ZIP SHA-256 is
`0c3263b6f4ea71835cb5fe3f05b8a408f4720515ab505f24914c730c15511674`.
The initial alignment context contains the caller's exact instruction, "This is a
multi-phase change." The approved v2 contract instead contains a model-authored objective
without that instruction, and the planner context contains no `multi-phase` occurrence.
The resulting plan has one phase and one slice, explaining that implementation and
verification should be delivered atomically.

Source inspection confirms the propagation defect: `analyze()` passed the caller's
objective into the alignment prompt but `_contract_from_draft()` persisted
`draft.objective`. A structurally valid model summary could therefore silently discard
explicit delivery, scope, or stop constraints before approval and Program planning.
This is a confirmed loss of input, not proof that every single-phase model response has
this cause or that the new snapshot contract caused this pre-existing behavior.

## Bounded repair

For newly analyzed contracts, the existing `RequirementContract.objective` field now
retains the exact objective supplied to that `analyze()` call. The model may still propose
requirements, acceptance criteria, assumptions, clarifications, and other existing fields,
but it cannot replace the caller's objective with its summary. The normal model validation
and final contract validation remain in place, including the existing 1–8,000-character
objective bound. Invalid input is not silently truncated or normalized.

The preserved objective participates in the existing canonical requirement hash and is
persisted in the normal contract and approval artifacts. It is displayed in the approved
summary so an approver can review the input together with clarification decisions. The
existing planner receives it through the approved, hash-checked contract; no ad hoc extra
planner instruction or unbound side channel is added.

A subsequent explicit caller objective becomes the next version's objective. Existing
approved contracts and hashes are not retroactively rewritten. Clarification answers
remain explicit decisions; preserving a question in the original wording does not remove
its resolved answer or authorize unanswered security requirements.

The dedicated deterministic tests use the actual Product workspace, provider fixture,
artifact store, contract model, and planner path. They cover exact objective preservation,
spaces/Unicode/bounds, clarification and approval, immutable prior versions, isolated
objective hash binding, structural-repair behavior, and approved planner-context transport.
Their fake planner demonstrates transport, not real-model adherence to delivery semantics.
The unchanged Live scenario remains the behavioral integration gate.

## Scope and limitations

This repair changes the alignment service, adds dedicated regression tests and this note.
It does not change Program/Core schemas, force every Program to have multiple phases,
invent phases, relax the Live requirement for at least two phases, alter prompts or
workflow thresholds, repeat failed runs until green, or implement P3.5b. Preserving exact
input is necessary but not a general semantic proof that a model obeys every instruction.

Qualification of this source change must be recorded against its new head/tree. Earlier
880-test CI results and the five successful attempt-2 Live groups remain historical
evidence for their original source; they do not qualify the repaired source by themselves.
Independent review and all normal integration gates remain required.
