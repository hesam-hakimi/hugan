from __future__ import annotations

import os
import sqlite3
import stat
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
from test_repository_coverage_evidence import (
    PROJECT_ID,
    _build_upstreams,
    _commit,
    _policy,
    _record,
    _repository,
    _services,
    _write_run,
)
from test_repository_coverage_selection import (
    _eligibility_for_selector,
    _run_for_every_profile,
    _select_target,
    _SelectionContext,
)

from universal_coding_agent.core.cancellation import (
    CancellationRequested,
    PauseRequested,
)
from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.product.coverage_execution import (
    CoverageExecutionFallbackReason,
    CoverageTestExecutionFailureCode,
    CoverageTestExecutionMode,
    CoverageTestExecutionOutcome,
    CoverageTestExecutionPolicy,
    RepositoryCoverageTestExecutionError,
    RepositoryCoverageTestExecutionService,
)
from universal_coding_agent.product.coverage_selection import (
    CoverageTestSelectionDisposition,
    RepositoryCoverageSelectionService,
)
from universal_coding_agent.safe.testing import SafeTestRunner
from universal_coding_agent.sandbox.git import GitSandboxManager

PASS_SCRIPT = (
    "from pathlib import Path; import sys; "
    "Path('profile-runs.log').open('a', encoding='utf-8').write('run\\n'); "
    "print('ARGS=' + '|'.join(sys.argv[1:]))"
)
MUTATE_SOURCE_SCRIPT = (
    "from pathlib import Path; "
    "Path('src/pkg/core.py').write_text('mutated\\n', encoding='utf-8'); "
    "print('mutated tracked source')"
)
FAIL_SCRIPT = "import sys; print('profile failed'); sys.exit(7)"
TARGET_SOURCE = (
    "def leaf(value: int):\n"
    "    # A supported source-only change keeps behavior stable.\n"
    "    return value + 1\n"
    "\n"
    "class Worker:\n"
    "    def run(self):\n"
    "        return leaf(1)\n"
)


@dataclass
class _ExecutionContext:
    root: Path
    services: object
    policy: SafeModePolicy
    selection: object
    selector: RepositoryCoverageSelectionService
    sandbox_manager: GitSandboxManager
    executor: RepositoryCoverageTestExecutionService
    database_path: Path


class _RaisingRunner:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def run_selected_profiles(self, *args, **kwargs):
        raise self.error

    def run_profiles(self, *args, **kwargs):
        raise self.error


def _execution_policy(*profile_ids: str) -> CoverageTestExecutionPolicy:
    return CoverageTestExecutionPolicy(
        selected_test_profile_ids=tuple(sorted(profile_ids))
    )


def _trusted_policy(script: str) -> SafeModePolicy:
    return SafeModePolicy(
        profiles=tuple(
            TestProfile(
                profile_id=profile_id,
                argv=(sys.executable, "-c", script),
                timeout_seconds=30,
                output_limit=10_000,
            )
            for profile_id in ("focused", "integration")
        )
    )


@pytest.fixture
def execution_factory(tmp_path: Path):
    contexts: list[_ExecutionContext] = []

    def build(
        *,
        script: str = PASS_SCRIPT,
        changed_path: str = "src/pkg/core.py",
        changed_content: str = TARGET_SOURCE,
    ) -> _ExecutionContext:
        suffix = len(contexts)
        root, base_sha = _repository(tmp_path, name=f"source-{suffix}")
        state_root = tmp_path / f"analysis-state-{suffix}"
        services = _services(state_root)
        policy = _trusted_policy(script)
        upstreams = _build_upstreams(
            root,
            base_sha,
            services,
            repository_url=str(root.resolve()),
        )
        run = _run_for_every_profile(root, upstreams, policy).model_copy(
            update={"repository_url": str(root.resolve())}
        )
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        recorded = _record(
            services,
            root,
            upstreams,
            policy,
            run_ref,
            run_sha256,
        )
        selection_context = _SelectionContext(
            root=root,
            state_root=state_root,
            base_sha=base_sha,
            services=services,
            policy=policy,
            run=run,
            recorded=recorded,
            upstreams=upstreams,
        )
        eligibility = _eligibility_for_selector(selection_context)
        target = root / changed_path
        target.write_text(changed_content, encoding="utf-8")
        target_base_sha = _commit(root, "advance execution target")
        target_upstreams = _build_upstreams(
            root,
            target_base_sha,
            services,
            repository_url=str(root.resolve()),
            previous=upstreams,
        )
        selection = _select_target(
            selection_context,
            eligibility,
            target_base_sha,
            target_upstreams,
        )
        selector = RepositoryCoverageSelectionService(
            services.artifacts,
            services.coverage,
            services.dispatch,
        )
        execution_root = tmp_path / f"execution-state-{suffix}"
        sandbox_manager = GitSandboxManager(
            execution_root,
            allow_local_sources=True,
        )
        database_path = execution_root / "coverage-test-executions.sqlite"
        executor = RepositoryCoverageTestExecutionService(
            database_path,
            services.artifacts,
            selector,
            sandbox_manager,
            test_runner=SafeTestRunner(),
        )
        context = _ExecutionContext(
            root=root,
            services=services,
            policy=policy,
            selection=selection,
            selector=selector,
            sandbox_manager=sandbox_manager,
            executor=executor,
            database_path=database_path,
        )
        contexts.append(context)
        return context

    yield build

    for context in contexts:
        try:
            context.executor.close()
        except sqlite3.ProgrammingError:
            pass
        context.services.search.close()


def _prepare(
    context: _ExecutionContext,
    *,
    execution_id: str = "execution-001",
    execution_policy: CoverageTestExecutionPolicy | None = None,
):
    return context.executor.prepare_execution(
        execution_id=execution_id,
        project_id=PROJECT_ID,
        repository=RepositorySpec(url=str(context.root.resolve()), base_ref="main"),
        trusted_test_policy=context.policy,
        execution_policy=execution_policy
        or _execution_policy("focused", "integration"),
        selection_ref=context.selection.selection_ref,
        selection_sha256=context.selection.selection_sha256,
    )


def _approve(context: _ExecutionContext, plan):
    return context.executor.approve_execution(
        execution_id=plan.plan.execution_id,
        expected_plan_ref=plan.plan_ref,
        expected_plan_sha256=plan.plan_sha256,
        confirmed_plan_sha256=plan.plan_sha256,
        confirmed=True,
    )


def _execute(
    context: _ExecutionContext,
    plan,
    approval,
    *,
    policy: SafeModePolicy | None = None,
    execution_policy: CoverageTestExecutionPolicy | None = None,
):
    return context.executor.execute_approved(
        execution_id=plan.plan.execution_id,
        expected_plan_ref=plan.plan_ref,
        expected_plan_sha256=plan.plan_sha256,
        expected_approval_ref=approval.approval_ref,
        expected_approval_sha256=approval.approval_sha256,
        trusted_test_policy=policy or context.policy,
        execution_policy=execution_policy
        or _execution_policy("focused", "integration"),
    )


def test_prepare_binds_selected_tests_to_exact_clean_sandbox_without_execution(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()

    plan = _prepare(context)
    replayed = _prepare(context)
    sandbox = context.sandbox_manager.sandbox_path("execution-001")

    assert plan.plan.execution_mode is CoverageTestExecutionMode.SELECTED_TESTS
    assert plan.plan.authorizes_execution is False
    assert plan.plan.requires_explicit_human_approval is True
    assert plan.plan.shell_disabled is True
    assert all(item.test_ids for item in plan.plan.profiles)
    assert plan.plan.target_base_sha == _git(context.root, "rev-parse", "HEAD")
    assert plan.plan.source_tree_oid == _git(context.root, "rev-parse", "HEAD^{tree}")
    assert not sandbox.joinpath("profile-runs.log").exists()
    assert replayed.plan_ref == plan.plan_ref
    assert replayed.plan_sha256 == plan.plan_sha256
    assert replayed.replayed is True
    if os.name != "nt":
        assert stat.S_IMODE(context.database_path.stat().st_mode) == 0o600


def test_execution_requires_exact_explicit_human_confirmation(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)

    with pytest.raises(RepositoryCoverageTestExecutionError, match="confirmation"):
        context.executor.approve_execution(
            execution_id="execution-001",
            expected_plan_ref=plan.plan_ref,
            expected_plan_sha256=plan.plan_sha256,
            confirmed_plan_sha256=plan.plan_sha256,
            confirmed=False,
        )
    with pytest.raises(RepositoryCoverageTestExecutionError, match="does not match"):
        context.executor.approve_execution(
            execution_id="execution-001",
            expected_plan_ref=plan.plan_ref,
            expected_plan_sha256=plan.plan_sha256,
            confirmed_plan_sha256="a" * 64,
            confirmed=True,
        )
    assert not context.sandbox_manager.sandbox_path("execution-001").joinpath(
        "profile-runs.log"
    ).exists()


def test_exact_approval_replay_is_idempotent(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)

    first = _approve(context, plan)
    second = _approve(context, plan)

    assert second.approval_ref == first.approval_ref
    assert second.approval_sha256 == first.approval_sha256
    assert second.replayed is True


def test_approved_selected_execution_runs_exact_ids_once_and_replays_receipt(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)
    approval = _approve(context, plan)

    result = _execute(context, plan, approval)
    replayed = _execute(context, plan, approval)
    run_log = context.sandbox_manager.sandbox_path("execution-001") / "profile-runs.log"

    assert result.receipt.outcome is CoverageTestExecutionOutcome.PASSED
    assert result.receipt.execution_complete is True
    assert result.receipt.all_tests_passed is True
    assert result.receipt.source_preserved is True
    assert result.receipt.failure_codes == ()
    assert len(result.receipt.profile_results) == 2
    assert all(
        "tests/test_core.py::test_leaf" in item.output
        for item in result.receipt.profile_results
    )
    assert all(
        "tests/test_core.py::test_worker" in item.output
        for item in result.receipt.profile_results
    )
    assert run_log.read_text(encoding="utf-8").splitlines() == ["run", "run"]
    assert replayed.result_ref == result.result_ref
    assert replayed.result_sha256 == result.result_sha256
    assert replayed.replayed is True
    assert run_log.read_text(encoding="utf-8").splitlines() == ["run", "run"]
    assert context.executor.verified_result(
        result.result_ref, result.result_sha256
    ) == result.receipt


def test_unopted_profile_capability_runs_complete_full_profiles(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    execution_policy = _execution_policy()
    plan = _prepare(context, execution_policy=execution_policy)
    approval = _approve(context, plan)

    result = _execute(
        context,
        plan,
        approval,
        execution_policy=execution_policy,
    )

    assert context.selection.selection.disposition is CoverageTestSelectionDisposition.SELECTED
    assert plan.plan.execution_mode is CoverageTestExecutionMode.FULL_PROFILE
    assert plan.plan.fallback_reasons == (
        CoverageExecutionFallbackReason.PROFILE_NOT_SELECTION_CAPABLE,
    )
    assert all(item.test_ids == () for item in plan.plan.profiles)
    assert result.receipt.outcome is CoverageTestExecutionOutcome.PASSED
    assert all(item.output.strip() == "ARGS=" for item in result.receipt.profile_results)


def test_selector_fallback_runs_every_requested_full_profile(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory(
        changed_path="notes.txt",
        changed_content="unsupported non-Python target change\n",
    )
    plan = _prepare(context)
    approval = _approve(context, plan)

    result = _execute(context, plan, approval)

    assert context.selection.selection.disposition is (
        CoverageTestSelectionDisposition.FULL_PROFILE_FALLBACK
    )
    assert plan.plan.execution_mode is CoverageTestExecutionMode.FULL_PROFILE
    assert plan.plan.fallback_reasons == (
        CoverageExecutionFallbackReason.SELECTION_FULL_PROFILE_FALLBACK,
    )
    assert tuple(item.profile_id for item in result.receipt.profile_results) == (
        "focused",
        "integration",
    )
    assert all(item.output.strip() == "ARGS=" for item in result.receipt.profile_results)


def test_policy_or_capability_drift_rejects_before_any_process(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    execution_policy = _execution_policy("focused", "integration")
    plan = _prepare(context, execution_policy=execution_policy)
    approval = _approve(context, plan)
    profiles = list(context.policy.profiles)
    profiles[0] = profiles[0].model_copy(update={"argv": (sys.executable, "-c", "pass")})
    drifted_policy = context.policy.model_copy(update={"profiles": tuple(profiles)})

    with pytest.raises(RepositoryCoverageTestExecutionError, match="policy drifted"):
        _execute(
            context,
            plan,
            approval,
            policy=drifted_policy,
            execution_policy=execution_policy,
        )
    with pytest.raises(RepositoryCoverageTestExecutionError, match="policy drifted"):
        _execute(
            context,
            plan,
            approval,
            execution_policy=_execution_policy("focused"),
        )
    assert not context.sandbox_manager.sandbox_path("execution-001").joinpath(
        "profile-runs.log"
    ).exists()


def test_pre_execution_sandbox_drift_blocks_without_running_tests(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)
    approval = _approve(context, plan)
    sandbox = context.sandbox_manager.sandbox_path("execution-001")
    sandbox.joinpath("src/pkg/core.py").write_text("tampered\n", encoding="utf-8")

    result = _execute(context, plan, approval)

    assert result.receipt.outcome is CoverageTestExecutionOutcome.BLOCKED
    assert result.receipt.execution_complete is False
    assert result.receipt.source_preserved is False
    assert CoverageTestExecutionFailureCode.TRACKED_WORKTREE_DIRTY in (
        result.receipt.failure_codes
    )
    assert not sandbox.joinpath("profile-runs.log").exists()


def test_test_source_mutation_fails_receipt_and_rolls_back_tracked_checkout(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory(script=MUTATE_SOURCE_SCRIPT)
    source_before = context.root.joinpath("src/pkg/core.py").read_text(encoding="utf-8")
    plan = _prepare(context)
    approval = _approve(context, plan)

    result = _execute(context, plan, approval)
    sandbox_source = context.sandbox_manager.sandbox_path("execution-001").joinpath(
        "src/pkg/core.py"
    )

    assert result.receipt.outcome is CoverageTestExecutionOutcome.SOURCE_DRIFT
    assert result.receipt.execution_complete is False
    assert result.receipt.all_tests_passed is False
    assert len(result.receipt.profile_results) == 1
    assert result.receipt.source_preserved is False
    assert result.receipt.rollback_attempted is True
    assert result.receipt.rollback_succeeded is True
    assert CoverageTestExecutionFailureCode.SOURCE_CHANGED_DURING_EXECUTION in (
        result.receipt.failure_codes
    )
    assert sandbox_source.read_text(encoding="utf-8") == source_before
    assert context.root.joinpath("src/pkg/core.py").read_text(encoding="utf-8") == source_before


@pytest.mark.parametrize("index_flag", ("--assume-unchanged", "--skip-worktree"))
def test_hidden_index_flag_cannot_mask_source_mutation(
    execution_factory: Callable[..., _ExecutionContext],
    index_flag: str,
) -> None:
    script = (
        "from pathlib import Path; import subprocess; "
        f"subprocess.run(['git', 'update-index', '{index_flag}', "
        "'src/pkg/core.py'], check=True); "
        "Path('src/pkg/core.py').write_text('hidden mutation\\n', encoding='utf-8')"
    )
    context = execution_factory(script=script)
    source_before = context.root.joinpath("src/pkg/core.py").read_text(encoding="utf-8")
    plan = _prepare(context)
    approval = _approve(context, plan)

    result = _execute(context, plan, approval)

    assert result.receipt.outcome is CoverageTestExecutionOutcome.SOURCE_DRIFT
    assert result.receipt.source_preserved is False
    assert CoverageTestExecutionFailureCode.SANDBOX_VERIFICATION_FAILED in (
        result.receipt.failure_codes
    )
    assert context.root.joinpath("src/pkg/core.py").read_text(encoding="utf-8") == source_before


def test_nonzero_trusted_profiles_produce_bound_failure_receipt(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory(script=FAIL_SCRIPT)
    plan = _prepare(context)
    approval = _approve(context, plan)

    result = _execute(context, plan, approval)

    assert result.receipt.outcome is CoverageTestExecutionOutcome.TEST_FAILED
    assert result.receipt.execution_complete is True
    assert result.receipt.all_tests_passed is False
    assert result.receipt.source_preserved is True
    assert result.receipt.failure_codes == (
        CoverageTestExecutionFailureCode.TEST_PROFILE_FAILED,
    )
    assert [item.returncode for item in result.receipt.profile_results] == [7, 7]


def test_result_model_rejects_outcomes_that_conflict_with_bound_evidence(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)
    approval = _approve(context, plan)
    result = _execute(context, plan, approval)
    original = result.receipt.model_dump(mode="json")
    contradictions = (
        {
            "outcome": CoverageTestExecutionOutcome.BLOCKED.value,
            "failure_codes": [
                CoverageTestExecutionFailureCode.SANDBOX_VERIFICATION_FAILED.value
            ],
        },
        {
            "outcome": CoverageTestExecutionOutcome.TEST_FAILED.value,
            "all_tests_passed": False,
            "failure_codes": [
                CoverageTestExecutionFailureCode.TEST_PROFILE_FAILED.value
            ],
        },
    )

    for contradiction in contradictions:
        with pytest.raises(ValueError, match="conflicts"):
            type(result.receipt).model_validate(original | contradiction)


@pytest.mark.parametrize(
    ("error", "outcome", "failure_code"),
    (
        (
            CancellationRequested("cancelled"),
            CoverageTestExecutionOutcome.CANCELLED,
            CoverageTestExecutionFailureCode.TRUSTED_TEST_CANCELLED,
        ),
        (
            PauseRequested("paused"),
            CoverageTestExecutionOutcome.CANCELLED,
            CoverageTestExecutionFailureCode.TRUSTED_TEST_CONTROL_STOPPED,
        ),
        (
            subprocess.TimeoutExpired("trusted-profile", 1),
            CoverageTestExecutionOutcome.EXECUTION_ERROR,
            CoverageTestExecutionFailureCode.TRUSTED_TEST_TIMEOUT,
        ),
        (
            RuntimeError("adapter failed"),
            CoverageTestExecutionOutcome.EXECUTION_ERROR,
            CoverageTestExecutionFailureCode.TRUSTED_TEST_EXECUTION_ERROR,
        ),
    ),
)
def test_owned_runner_interruptions_produce_typed_failure_receipts(
    execution_factory: Callable[..., _ExecutionContext],
    error: Exception,
    outcome: CoverageTestExecutionOutcome,
    failure_code: CoverageTestExecutionFailureCode,
) -> None:
    context = execution_factory()
    context.executor.test_runner = _RaisingRunner(error)
    plan = _prepare(context)
    approval = _approve(context, plan)

    result = _execute(context, plan, approval)

    assert result.receipt.outcome is outcome
    assert result.receipt.failure_codes == (failure_code,)
    assert result.receipt.execution_complete is False
    assert result.receipt.source_preserved is True


def test_failed_source_rollback_remains_explicit_and_fail_closed(
    execution_factory: Callable[..., _ExecutionContext],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = execution_factory(script=MUTATE_SOURCE_SCRIPT)
    plan = _prepare(context)
    approval = _approve(context, plan)

    def fail_rollback(*args, **kwargs):
        raise RuntimeError("rollback unavailable")

    monkeypatch.setattr(
        context.sandbox_manager,
        "restore_tracked_checkout",
        fail_rollback,
    )
    result = _execute(context, plan, approval)

    assert result.receipt.outcome is CoverageTestExecutionOutcome.SOURCE_DRIFT
    assert result.receipt.rollback_attempted is True
    assert result.receipt.rollback_succeeded is False
    assert result.receipt.rollback_checkout is None
    assert CoverageTestExecutionFailureCode.ROLLBACK_FAILED in (
        result.receipt.failure_codes
    )


def test_approval_artifact_drift_fails_before_execution(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)
    approval = _approve(context, plan)
    approval_path = context.services.artifacts.root / approval.approval_ref.removeprefix(
        "artifact://"
    )
    approval_path.write_text("{}", encoding="utf-8")

    with pytest.raises(RepositoryCoverageTestExecutionError, match="integrity"):
        _execute(context, plan, approval)
    assert not context.sandbox_manager.sandbox_path("execution-001").joinpath(
        "profile-runs.log"
    ).exists()


def test_selection_or_plan_artifact_drift_fails_closed(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    selection_context = execution_factory()
    selection_path = (
        selection_context.services.artifacts.root
        / selection_context.selection.selection_ref.removeprefix("artifact://")
    )
    selection_path.write_text("{}", encoding="utf-8")
    with pytest.raises(RepositoryCoverageTestExecutionError, match="verification"):
        _prepare(selection_context)

    plan_context = execution_factory()
    plan = _prepare(plan_context)
    plan_path = plan_context.services.artifacts.root / plan.plan_ref.removeprefix(
        "artifact://"
    )
    plan_path.write_text("{}", encoding="utf-8")
    with pytest.raises(RepositoryCoverageTestExecutionError, match="integrity"):
        _approve(plan_context, plan)


def test_completed_result_artifact_drift_blocks_replay(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)
    approval = _approve(context, plan)
    result = _execute(context, plan, approval)
    result_path = context.services.artifacts.root / result.result_ref.removeprefix(
        "artifact://"
    )
    result_path.write_text("{}", encoding="utf-8")

    with pytest.raises(RepositoryCoverageTestExecutionError, match="integrity"):
        _execute(context, plan, approval)


def test_state_corruption_and_service_policy_drift_fail_closed(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)
    drifted_service = RepositoryCoverageTestExecutionService(
        context.database_path,
        context.services.artifacts,
        context.selector,
        context.sandbox_manager,
        test_runner=SafeTestRunner(),
        max_json_depth=15,
    )
    try:
        with pytest.raises(RepositoryCoverageTestExecutionError, match="policy"):
            drifted_service.verified_plan(plan.plan_ref, plan.plan_sha256)
    finally:
        drifted_service.close()

    context.executor.connection.execute(
        "UPDATE coverage_test_executions SET status = 'invalid' WHERE execution_id = ?",
        ("execution-001",),
    )
    with pytest.raises(RepositoryCoverageTestExecutionError, match="state"):
        _prepare(context)


def test_durable_state_scope_drift_rejects_before_approval(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)
    context.executor.connection.execute(
        "UPDATE coverage_test_executions SET project_id = ? WHERE execution_id = ?",
        ("other-project", "execution-001"),
    )

    with pytest.raises(RepositoryCoverageTestExecutionError, match="expected plan"):
        _approve(context, plan)
    assert not context.sandbox_manager.sandbox_path("execution-001").joinpath(
        "profile-runs.log"
    ).exists()


def test_prepared_state_cannot_contain_unconsumed_approval_artifacts(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    _prepare(context)
    context.executor.connection.execute(
        """
        UPDATE coverage_test_executions
        SET approval_ref = ?, approval_sha256 = ?
        WHERE execution_id = ?
        """,
        ("artifact://forged/approval.json", "a" * 64, "execution-001"),
    )

    with pytest.raises(RepositoryCoverageTestExecutionError, match="state"):
        _prepare(context)


def test_aggregate_output_bound_rejects_before_sandbox_creation(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    context.executor.close()
    context.executor = RepositoryCoverageTestExecutionService(
        context.database_path,
        context.services.artifacts,
        context.selector,
        context.sandbox_manager,
        test_runner=SafeTestRunner(),
        max_total_output_chars=19_999,
    )

    with pytest.raises(RepositoryCoverageTestExecutionError, match="aggregate"):
        _prepare(context)
    assert not context.sandbox_manager.sandbox_path("execution-001").exists()


def test_restart_executes_approved_plan_and_replays_completed_result(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)
    approval = _approve(context, plan)
    context.executor.close()
    context.executor = RepositoryCoverageTestExecutionService(
        context.database_path,
        context.services.artifacts,
        context.selector,
        context.sandbox_manager,
        test_runner=SafeTestRunner(),
    )

    result = _execute(context, plan, approval)
    context.executor.close()
    context.executor = RepositoryCoverageTestExecutionService(
        context.database_path,
        context.services.artifacts,
        context.selector,
        context.sandbox_manager,
        test_runner=SafeTestRunner(),
    )
    replayed = _execute(context, plan, approval)

    assert result.receipt.outcome is CoverageTestExecutionOutcome.PASSED
    assert replayed.replayed is True
    assert replayed.result_sha256 == result.result_sha256


def test_crash_left_running_state_blocks_automatic_reexecution(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    plan = _prepare(context)
    approval = _approve(context, plan)
    context.executor.connection.execute(
        "UPDATE coverage_test_executions SET status = 'running' WHERE execution_id = ?",
        ("execution-001",),
    )

    with pytest.raises(RepositoryCoverageTestExecutionError, match="explicit recovery"):
        _execute(context, plan, approval)
    assert not context.sandbox_manager.sandbox_path("execution-001").joinpath(
        "profile-runs.log"
    ).exists()


def test_target_ref_drift_fails_preparation_without_test_execution(
    execution_factory: Callable[..., _ExecutionContext],
) -> None:
    context = execution_factory()
    context.root.joinpath("notes.txt").write_text("moved after selection\n", encoding="utf-8")
    _commit(context.root, "move target ref after selection")

    with pytest.raises(RepositoryCoverageTestExecutionError, match="selected exact Base"):
        _prepare(context)


@pytest.mark.parametrize(
    "test_ids",
    (
        ("-k",),
        ("@selected-tests.py",),
        ("../tests/test_core.py::test_leaf",),
        ("tests/test_core.txt::test_leaf",),
        ("tests/test_core.py::test_leaf", "tests/test_core.py::test_leaf"),
    ),
)
def test_safe_runner_rejects_noncanonical_selected_test_arguments(
    tmp_path: Path,
    test_ids: tuple[str, ...],
) -> None:
    policy = _policy("focused")

    with pytest.raises(ValueError):
        SafeTestRunner().run_selected_profiles(
            tmp_path,
            policy,
            ("focused",),
            {"focused": test_ids},
        )


def test_safe_runner_appends_valid_test_ids_as_separate_positional_arguments(
    tmp_path: Path,
) -> None:
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="focused",
                argv=(sys.executable, "-c", "import sys; print(repr(sys.argv[1:]))"),
            ),
        )
    )
    test_ids = (
        "tests/test_core.py::test_leaf",
        "tests/test_core.py::test_worker[param]",
    )

    result = SafeTestRunner().run_selected_profiles(
        tmp_path,
        policy,
        ("focused",),
        {"focused": test_ids},
    )

    assert result[0].passed is True
    assert "tests/test_core.py::test_leaf" in result[0].output
    assert "tests/test_core.py::test_worker[param]" in result[0].output


def test_safe_runner_requires_exact_selected_profile_mapping(tmp_path: Path) -> None:
    policy = _policy("focused", "integration")

    with pytest.raises(ValueError, match="mapping"):
        SafeTestRunner().run_selected_profiles(
            tmp_path,
            policy,
            ("focused",),
            {"integration": ("tests/test_core.py::test_leaf",)},
        )


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
