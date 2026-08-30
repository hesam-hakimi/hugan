from pathlib import Path

import pytest
from pydantic import ValidationError

from universal_coding_agent.context.compiler import ContextCompiler
from universal_coding_agent.core.models import (
    PhasePlan,
    ProjectFile,
    ProjectManifest,
    RepositorySpec,
    SlicePlan,
    TaskMode,
    TaskRequest,
)
from universal_coding_agent.safety.sanitizer import sanitize_text
from universal_coding_agent.storage.artifacts import (
    ArtifactSizeLimitExceeded,
    ArtifactStore,
)


def test_task_is_observe_only() -> None:
    with pytest.raises(ValidationError):
        TaskRequest(
            task_id="task-123",
            thread_id="thread-123",
            title="unsafe",
            objective="write code",
            repository=RepositorySpec(
                url="https://example.test/repo.git",
                base_ref="main",
            ),
            mode=TaskMode.SAFE,
        )


def test_phase_plan_rejects_unknown_internal_dependency() -> None:
    with pytest.raises(ValidationError):
        PhasePlan(
            phase_id="P1",
            title="phase",
            objective="objective",
            slices=(
                SlicePlan(
                    slice_id="S1",
                    title="one",
                    objective="one",
                    dependencies=("missing",),
                ),
            ),
        )


def test_phase_plan_accepts_explicit_external_dependency() -> None:
    plan = PhasePlan(
        phase_id="P2C",
        title="phase",
        objective="objective",
        slices=(
            SlicePlan(
                slice_id="S1",
                title="one",
                objective="one",
                external_dependencies=("Phase 2B canonical schema specification",),
            ),
        ),
    )
    assert plan.slices[0].dependencies == ()
    assert plan.slices[0].external_dependencies == (
        "Phase 2B canonical schema specification",
    )


def test_artifact_store_is_atomic_and_contained(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    reference = store.write_json("tasks/t1/result.json", {"ok": True})
    assert store.read_json(reference) == {"ok": True}
    with pytest.raises(ValueError):
        store.write_text("../escape.txt", "no")


def test_artifact_store_bounded_json_read_stops_before_oversized_payload(
    tmp_path: Path,
) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    payload = {"value": "x" * 1024}
    reference = store.write_json("tasks/t1/bounded.json", payload)

    assert store.read_json_bounded(reference, max_bytes=reference.size) == payload
    with pytest.raises(
        ArtifactSizeLimitExceeded,
        match="configured byte read limit",
    ):
        store.read_json_bounded(reference, max_bytes=reference.size - 1)
    with pytest.raises(ValueError, match="read limit must be positive"):
        store.read_json_bounded(reference, max_bytes=0)


def test_context_compiler_is_bounded(tmp_path: Path) -> None:
    source = tmp_path / "main.py"
    source.write_text("def relevant_symbol():\n    return 1\n" * 100, encoding="utf-8")
    manifest = ProjectManifest(
        repository_url="https://example.test/repo.git",
        base_ref="main",
        base_sha="a" * 40,
        files=(
            ProjectFile(
                path="main.py",
                size=source.stat().st_size,
                sha256="b" * 64,
                language="python",
                symbols=("FunctionDef:relevant_symbol:1",),
            ),
        ),
    )
    task = TaskRequest(
        task_id="task-123",
        thread_id="thread-123",
        title="inspect",
        objective="inspect relevant_symbol",
        repository=RepositorySpec(url=manifest.repository_url, base_ref="main"),
    )
    compiler = ContextCompiler(planner_char_budget=500, max_chars_per_file=300)
    context = compiler.compile_planner(tmp_path, task, manifest)
    assert len(context) <= 500
    assert "relevant_symbol" in context


def test_phase_plan_rejects_dependency_cycle() -> None:
    with pytest.raises(ValidationError):
        PhasePlan(
            phase_id="P1",
            title="phase",
            objective="objective",
            slices=(
                SlicePlan(slice_id="A", title="A", objective="A", dependencies=("B",)),
                SlicePlan(slice_id="B", title="B", objective="B", dependencies=("A",)),
            ),
        )


def test_sanitizer_redacts_common_secret_shapes() -> None:
    value = (
        "Authorization: Bearer abc.def.ghi\n"
        "api_key=super-secret\n"
        "ghp_123456789012345678901234"
    )
    sanitized = sanitize_text(value)
    assert "abc.def.ghi" not in sanitized
    assert "super-secret" not in sanitized
    assert "ghp_" not in sanitized
