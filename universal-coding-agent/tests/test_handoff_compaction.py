from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from universal_coding_agent.product.handoff_compaction import (
    HandoffCompactionError,
    PhaseHandoffCompactor,
)
from universal_coding_agent.product.models import (
    AcceptedPhaseEvidence,
    AcceptedPhaseEvidenceBundle,
    AcceptedSafeExecutionEvidence,
)
from universal_coding_agent.storage.artifacts import ArtifactStore


def _execution() -> AcceptedSafeExecutionEvidence:
    return AcceptedSafeExecutionEvidence(
        task_id="task-phase-one",
        slice_id="slice-one",
        source_base_sha="a" * 40,
        result_ref="artifact://safe/task-phase-one/result.json",
        result_sha256="b" * 64,
        tests_ref="artifact://safe/task-phase-one/tests.json",
        review_ref="artifact://safe/task-phase-one/review.json",
        final_report_ref="artifact://safe/task-phase-one/final.json",
        reviewer_verdict="PASS",
    )


def _bundle(*, verbose: bool) -> AcceptedPhaseEvidenceBundle:
    decisions = (
        tuple(f"decision-{index}:" + "d" * 2_000 for index in range(20))
        if verbose
        else ("Use the accepted contract.",)
    )
    risks = (
        tuple(f"risk-{index}:" + "r" * 2_000 for index in range(20))
        if verbose
        else ("No known material risk.",)
    )
    phase = AcceptedPhaseEvidence(
        phase_id="phase-one",
        result_ref="artifact://programs/demo/phase-one/result.json",
        result_sha256="c" * 64,
        summary_ref="artifact://programs/demo/phase-one/summary.json",
        summary_sha256="d" * 64,
        phase_report_ref="artifact://programs/demo/phase-one/report.json",
        phase_report_sha256="e" * 64,
        summary="Completed the accepted phase. " + ("s" * 7_500 if verbose else ""),
        changed_paths=tuple(f"src/module_{index}.py" for index in range(20)),
        decisions=decisions,
        tests=tuple(f"test-profile-{index}: PASS" for index in range(20)),
        reviewer_verdict="PASS",
        known_risks=risks,
        executions=(_execution(),),
    )
    return AcceptedPhaseEvidenceBundle(
        program_id="program-demo",
        target_phase_id="phase-two",
        requirement_hash="f" * 64,
        source_base_sha="a" * 40,
        dependency_phase_ids=("phase-one",),
        phases=(phase,),
    )


def test_small_bundle_preserves_existing_accepted_phase_evidence(tmp_path: Path) -> None:
    artifacts = ArtifactStore(tmp_path / "artifacts")
    bundle = _bundle(verbose=False)

    evidence = PhaseHandoffCompactor(artifacts).compile(bundle)

    assert evidence.context_type == "accepted_phase_evidence"
    assert evidence.sha256 == bundle.canonical_hash()
    assert evidence.source_ref.endswith(f"{bundle.canonical_hash()}.json")
    assert json.loads(evidence.content)["phases"][0]["decisions"] == [
        "Use the accepted contract."
    ]


def test_large_bundle_compacts_deterministically_with_source_provenance(
    tmp_path: Path,
) -> None:
    artifacts = ArtifactStore(tmp_path / "artifacts")
    bundle = _bundle(verbose=True)
    compactor = PhaseHandoffCompactor(artifacts)

    first = compactor.compile(bundle)
    second = compactor.compile(bundle)

    assert first == second
    assert first.context_type == "accepted_phase_handoff"
    assert len(first.content.encode("utf-8")) <= 48_000
    payload = json.loads(first.content)
    assert payload["source_bundle_sha256"] == bundle.canonical_hash()
    assert payload["source_bundle_ref"].endswith(
        f"accepted-prior-phase-evidence-{bundle.canonical_hash()}.json"
    )
    phase = payload["phases"][0]
    source_phase = bundle.phases[0]
    source_phase_content = json.dumps(
        source_phase.model_dump(mode="json"),
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    assert phase["phase_evidence_sha256"] == hashlib.sha256(
        source_phase_content
    ).hexdigest()
    assert phase["decisions"]["item_count"] == len(source_phase.decisions)
    decisions_content = json.dumps(
        list(source_phase.decisions),
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    assert phase["decisions"]["items_sha256"] == hashlib.sha256(
        decisions_content
    ).hexdigest()
    assert len(phase["decisions"]["items"]) < len(source_phase.decisions)
    source_content = artifacts.read_text_bounded_verified(
        payload["source_bundle_ref"],
        expected_sha256=payload["source_bundle_sha256"],
        max_bytes=512_000,
    )
    assert json.loads(source_content)["phases"][0]["decisions"] == list(
        source_phase.decisions
    )


def test_source_bundle_and_minimal_handoff_limits_fail_closed(tmp_path: Path) -> None:
    artifacts = ArtifactStore(tmp_path / "artifacts")
    bundle = _bundle(verbose=True)

    with pytest.raises(HandoffCompactionError, match="source bundle"):
        PhaseHandoffCompactor(
            artifacts,
            context_max_bytes=1_000,
            source_bundle_max_bytes=2_000,
        ).compile(bundle)

    with pytest.raises(HandoffCompactionError, match="metadata"):
        PhaseHandoffCompactor(
            artifacts,
            context_max_bytes=100,
            source_bundle_max_bytes=512_000,
        ).compile(bundle)
