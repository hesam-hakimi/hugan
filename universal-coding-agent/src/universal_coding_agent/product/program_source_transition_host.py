"""Explicit one-action host composition for the bounded two-phase journey.

Host construction supplies trusted existing adapters. No public action accepts a
path, provider, checkpoint, PASS result or worker token. Returned proposals never
trigger another action. Private legacy/c1 owner episodes cannot survive restart.
"""

from __future__ import annotations

from universal_coding_agent.product.program_continuation_execution_store import (
    canonical,
    require,
    sha,
)
from universal_coding_agent.product.program_source_acceptance_v2 import (
    ProgramSourceAcceptanceV2Service,
)
from universal_coding_agent.product.program_source_evidence import strict_json


class ProgramSourceTransitionHost:
    def __init__(self, continuation, *, first_phase_executor, repository):
        self.continuation = continuation
        self.store = continuation.store
        self.first_phase_executor, self.repository = first_phase_executor, repository
        self._first = {}
        self._prepared = {}
        self._acceptance = None

    def _final(self):
        if self._acceptance is None:
            self._acceptance = ProgramSourceAcceptanceV2Service(self.continuation)
        return self._acceptance

    def start_first_phase(self, program_id):
        source = self.store.current(program_id)
        plan = self.store._plan(source.identity)
        require(
            source.generation == 0
            and len(plan.phases) == 2
            and all(not phase.slices for phase in plan.phases),
            "unsupported first-phase Program",
        )
        require(program_id not in self._first, "first-phase episode already exists")
        owner = self.continuation.lifecycle.reserve_program_worker(program_id)
        self._first[program_id] = owner
        return self.store.programs.start_next_execution(
            program_id=program_id,
            current_requirement_hash=source.identity.requirement_sha256,
            repository=self.repository,
            policy=self.store.trusted_policy,
            test_profiles=tuple(self.store.trusted_policy.profile_map()),
            executor=self.first_phase_executor,
        )

    def decide_first_phase_scope(self, program_id, task_id, *, approved):
        require(
            program_id in self._first and type(approved) is bool,
            "first-phase decision needs its original live episode",
        )
        source = self.store.current(program_id)
        require(source.generation == 0, "first phase is already accepted")
        return self.store.programs.continue_execution(
            program_id=program_id,
            task_id=task_id,
            current_requirement_hash=source.identity.requirement_sha256,
            executor=self.first_phase_executor,
            approved=approved,
        )

    def preview_first_phase_source(self, program_id, task_id, *, before_sha256, generation):
        require(
            program_id in self._first and generation == 0,
            "first-phase preview needs its original live episode",
        )
        return self.store.prepare(
            program_id,
            task_id=task_id,
            expected_source_sha256=before_sha256,
            expected_generation=generation,
            owner_token=self._first[program_id],
        )

    def accept_first_phase_source(
        self, program_id, *, candidate_sha256, transition_sha256, approval_id
    ):
        require(program_id in self._first, "first-phase acceptance needs its original live episode")
        owner = self._first[program_id]
        candidate = strict_json(self.store._get(candidate_sha256))
        require(
            candidate["schema"] == "uca-source-candidate-1"
            and candidate["program_id"] == program_id
            and candidate["generation"] == 0,
            "first-phase candidate identity differs",
        )
        # Legacy service still recaptures the complete same-owner candidate.
        result = self.store.accept(
            candidate_sha256,
            approved_transition_sha256=transition_sha256,
            approval_id=approval_id,
            owner_token=owner,
        )
        require(
            result["program_id"] == program_id and result["generation"] == 1,
            "first-phase receipt differs",
        )
        self.continuation.lifecycle.release_program_worker(program_id, owner)
        del self._first[program_id]
        return result

    def prepare_continuation(self, program_id, *, acceptance_receipt_sha256, request_id):
        require(
            self.store.current(program_id).generation == 1 and program_id not in self._prepared,
            "continuation preparation requires the first accepted source",
        )
        owner = self.continuation.lifecycle.reserve_program_worker(program_id)
        self._prepared[program_id] = owner
        material = self.continuation.preparation.materialization
        begun = material.begin(
            program_id, acceptance_receipt_sha256=acceptance_receipt_sha256, owner_token=owner
        )
        material.reconcile(begun["operation_id"], owner_token=owner)
        base = self.continuation.preparation.begin(begun["operation_id"], owner_token=owner)
        completed = self.continuation.preparation.reconcile(base["operation_id"], owner_token=owner)
        return self.continuation.admit(
            program_id,
            base["operation_id"],
            request_id=request_id,
            preparation_receipt_sha256=sha(canonical(completed)),
            owner_token=owner,
        )

    def dispatch_continuation(
        self,
        program_id,
        operation_id,
        *,
        request_id,
        admission_sha256,
        expected_epoch,
        expected_receipt_sha256,
    ):
        require(program_id in self._prepared, "c1 dispatch needs its original live owner episode")
        result = self.continuation.dispatch(
            program_id,
            operation_id,
            request_id=request_id,
            admission_sha256=admission_sha256,
            expected_epoch=expected_epoch,
            expected_receipt_sha256=expected_receipt_sha256,
            owner_token=self._prepared[program_id],
        )
        require(result["state"] == "parked_scope", "continuation did not settle at scope")
        del self._prepared[program_id]
        return result

    def decide_continuation_scope(
        self,
        program_id,
        operation_id,
        *,
        request_id,
        admission_sha256,
        expected_epoch,
        expected_receipt_sha256,
        proposal_sha256,
        scope_sha256,
        approval_id,
        approved,
    ):
        return self.continuation.approve_scope(
            program_id,
            operation_id,
            request_id=request_id,
            admission_sha256=admission_sha256,
            expected_epoch=expected_epoch,
            expected_receipt_sha256=expected_receipt_sha256,
            proposal_sha256=proposal_sha256,
            scope_sha256=scope_sha256,
            approval_id=approval_id,
            approved=approved,
        )

    def preview_source_transition(
        self,
        program_id,
        operation_id,
        *,
        request_id,
        terminal_receipt_sha256,
        before_sha256,
        generation,
    ):
        return self._final().preview_source_transition(
            program_id,
            operation_id,
            request_id=request_id,
            terminal_receipt_sha256=terminal_receipt_sha256,
            before_sha256=before_sha256,
            generation=generation,
        )

    def decide_source_transition(
        self,
        program_id,
        operation_id,
        *,
        request_id,
        approval_id,
        approved,
        candidate_sha256,
        revision,
        core_sha256,
        transition_sha256,
        before_sha256,
        generation,
        predecessor_receipt_sha256,
        terminal_receipt_sha256,
    ):
        return self._final().decide_source_transition(
            program_id,
            operation_id,
            request_id=request_id,
            approval_id=approval_id,
            approved=approved,
            candidate_sha256=candidate_sha256,
            revision=revision,
            core_sha256=core_sha256,
            transition_sha256=transition_sha256,
            before_sha256=before_sha256,
            generation=generation,
            predecessor_receipt_sha256=predecessor_receipt_sha256,
            terminal_receipt_sha256=terminal_receipt_sha256,
        )
