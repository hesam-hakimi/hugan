from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from universal_coding_agent.core.safe_models import SafeContextEvidence
from universal_coding_agent.product.models import (
    AcceptedPhaseEvidence,
    AcceptedPhaseEvidenceBundle,
    AcceptedPhaseHandoff,
    CompactedEvidenceSequence,
    CompactedPhaseHandoff,
)
from universal_coding_agent.storage.artifacts import ArtifactStore

DEFAULT_CONTEXT_MAX_BYTES = 48_000
DEFAULT_SOURCE_BUNDLE_MAX_BYTES = 512_000


class HandoffCompactionError(ValueError):
    """Accepted phase evidence cannot be transferred inside its bounded contract."""


@dataclass(frozen=True)
class _CompactionProfile:
    summary_chars: int
    item_limit: int
    item_chars: int


_COMPACTION_PROFILES = (
    _CompactionProfile(2_000, 16, 512),
    _CompactionProfile(1_000, 8, 256),
    _CompactionProfile(500, 4, 160),
    _CompactionProfile(256, 2, 128),
    _CompactionProfile(128, 1, 96),
    _CompactionProfile(0, 0, 0),
)


class PhaseHandoffCompactor:
    """Create a deterministic, provenance-bound Safe context from accepted phases."""

    def __init__(
        self,
        artifacts: ArtifactStore,
        *,
        context_max_bytes: int = DEFAULT_CONTEXT_MAX_BYTES,
        source_bundle_max_bytes: int = DEFAULT_SOURCE_BUNDLE_MAX_BYTES,
    ) -> None:
        if context_max_bytes < 1 or source_bundle_max_bytes < context_max_bytes:
            raise ValueError("handoff byte limits are invalid")
        self.artifacts = artifacts
        self.context_max_bytes = context_max_bytes
        self.source_bundle_max_bytes = source_bundle_max_bytes

    def compile(self, bundle: AcceptedPhaseEvidenceBundle) -> SafeContextEvidence:
        source_content = _canonical_json(bundle.model_dump(mode="json"))
        source_size = len(source_content.encode("utf-8"))
        if source_size > self.source_bundle_max_bytes:
            raise HandoffCompactionError(
                "accepted prior-phase source bundle exceeds its byte limit"
            )

        source_hash = bundle.canonical_hash()
        source_ref = self.artifacts.write_text(
            (
                f"programs/{bundle.program_id}/phases/{bundle.target_phase_id}/"
                f"accepted-prior-phase-evidence-{source_hash}.json"
            ),
            source_content,
            "application/json",
        )
        if source_ref.sha256 != source_hash:
            raise HandoffCompactionError("accepted source bundle artifact hash mismatch")
        self.artifacts.read_text_bounded_verified(
            source_ref,
            expected_sha256=source_hash,
            max_bytes=self.source_bundle_max_bytes,
        )

        if source_size <= self.context_max_bytes:
            return SafeContextEvidence(
                source_ref=source_ref.uri,
                sha256=source_hash,
                content=source_content,
            )

        for profile in _COMPACTION_PROFILES:
            handoff = self._handoff(
                bundle,
                source_ref=source_ref.uri,
                source_hash=source_hash,
                profile=profile,
            )
            content = _canonical_json(handoff.model_dump(mode="json"))
            if len(content.encode("utf-8")) > self.context_max_bytes:
                continue
            handoff_hash = handoff.canonical_hash()
            reference = self.artifacts.write_text(
                (
                    f"programs/{bundle.program_id}/phases/{bundle.target_phase_id}/"
                    f"accepted-phase-handoff-{handoff_hash}.json"
                ),
                content,
                "application/json",
            )
            if reference.sha256 != handoff_hash:
                raise HandoffCompactionError("accepted phase handoff artifact hash mismatch")
            verified = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=handoff_hash,
                max_bytes=self.context_max_bytes,
            )
            return SafeContextEvidence(
                context_type="accepted_phase_handoff",
                source_ref=reference.uri,
                sha256=handoff_hash,
                content=verified,
            )

        raise HandoffCompactionError(
            "accepted phase handoff metadata exceeds the bounded Safe context budget"
        )

    @staticmethod
    def _handoff(
        bundle: AcceptedPhaseEvidenceBundle,
        *,
        source_ref: str,
        source_hash: str,
        profile: _CompactionProfile,
    ) -> AcceptedPhaseHandoff:
        return AcceptedPhaseHandoff(
            program_id=bundle.program_id,
            target_phase_id=bundle.target_phase_id,
            requirement_hash=bundle.requirement_hash,
            source_base_sha=bundle.source_base_sha,
            source_bundle_ref=source_ref,
            source_bundle_sha256=source_hash,
            dependency_phase_ids=bundle.dependency_phase_ids,
            phases=tuple(
                _compact_phase(phase, profile=profile) for phase in bundle.phases
            ),
        )


def _compact_phase(
    phase: AcceptedPhaseEvidence,
    *,
    profile: _CompactionProfile,
) -> CompactedPhaseHandoff:
    phase_payload = _canonical_json(phase.model_dump(mode="json")).encode("utf-8")
    return CompactedPhaseHandoff(
        phase_id=phase.phase_id,
        phase_evidence_sha256=hashlib.sha256(phase_payload).hexdigest(),
        summary_chars=len(phase.summary),
        summary_excerpt=phase.summary[: profile.summary_chars],
        changed_paths=_compact_sequence(
            phase.changed_paths,
            item_limit=profile.item_limit,
            item_chars=profile.item_chars,
        ),
        decisions=_compact_sequence(
            phase.decisions,
            item_limit=profile.item_limit,
            item_chars=profile.item_chars,
        ),
        tests=_compact_sequence(
            phase.tests,
            item_limit=profile.item_limit,
            item_chars=profile.item_chars,
        ),
        reviewer_verdict=phase.reviewer_verdict,
        known_risks=_compact_sequence(
            phase.known_risks,
            item_limit=profile.item_limit,
            item_chars=profile.item_chars,
        ),
        execution_count=len(phase.executions),
    )


def _compact_sequence(
    values: tuple[str, ...],
    *,
    item_limit: int,
    item_chars: int,
) -> CompactedEvidenceSequence:
    content = _canonical_json(list(values)).encode("utf-8")
    return CompactedEvidenceSequence(
        item_count=len(values),
        items_sha256=hashlib.sha256(content).hexdigest(),
        items=tuple(item[:item_chars] for item in values[:item_limit]),
    )


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    )
