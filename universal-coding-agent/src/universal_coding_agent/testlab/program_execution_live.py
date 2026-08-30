from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from universal_coding_agent.core.models import (
    ModelCapabilities,
    ModelRequest,
    ModelResponse,
)
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.product.models import (
    AcceptanceCriterion,
    RequirementContract,
    RequirementItem,
    RequirementStatus,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safety.sanitizer import sanitize_text
from universal_coding_agent.solution_discovery import (
    ImpactChange,
    ImpactConfidence,
    SolutionImpactPlan,
)
from universal_coding_agent.testlab.live import _provider_preflight
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider
from universal_coding_agent.web.app import ProductWebRuntime, create_product_app


class ProgramExecutionQualificationProvider:
    """Use deterministic scope selection while qualifying live Safe edit and review roles."""

    def __init__(self, live: OpenAIResponsesProvider) -> None:
        self.live = live
        self.model = live.model
        self.records: list[dict[str, Any]] = []

    def probe(self) -> bool:
        return self.live.probe()

    def capabilities(self) -> ModelCapabilities:
        return self.live.capabilities()

    def invoke(self, request: ModelRequest) -> ModelResponse:
        accepted_evidence_context = (
            "# Accepted prior-phase evidence (READ ONLY)" in request.user_prompt
        )
        if request.role == "solution_discovery":
            target_path = self._target_path(request.user_prompt)
            payload = SolutionImpactPlan(
                summary=f"Change only the qualified feature contract in {target_path}.",
                components=("features",),
                changes=(
                    ImpactChange(
                        path=target_path,
                        component="features",
                        confidence=ImpactConfidence.HIGH,
                        rationale=(
                            "The approved phase objective names this existing feature contract "
                            "as its only change target."
                        ),
                    ),
                ),
                rejected_candidates=tuple(
                    path
                    for path in ("features/alpha.py", "features/beta.py")
                    if path != target_path
                ),
            ).model_dump(mode="json")
            self.records.append(
                {
                    "role": request.role,
                    "provider": "deterministic_qualification_scope",
                    "target_path": target_path,
                    "accepted_evidence_context": accepted_evidence_context,
                    "status": "completed",
                }
            )
            return ModelResponse(
                content=json.dumps(payload, separators=(",", ":")),
                structured=payload,
                actual_model="deterministic-qualification-scope",
                finish_reason="stop",
                safe_diagnostics={"provider": "deterministic_qualification_scope"},
            )

        record: dict[str, Any] = {
            "role": request.role,
            "provider": "openai_responses",
            "task_id": str(request.metadata.get("task_id", "")),
            "target_path": str(request.metadata.get("target_path", "")),
            "accepted_evidence_context": accepted_evidence_context,
            "status": "started",
        }
        try:
            response = self.live.invoke(request)
        except Exception as exc:
            record.update(
                {
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "error_code": str(getattr(exc, "code", "")),
                    "error": sanitize_text(str(exc))[:2000],
                }
            )
            self.records.append(record)
            raise
        record.update(
            {
                "status": "completed",
                "actual_model": response.actual_model,
                "finish_reason": response.finish_reason,
                "completion_tokens": response.completion_tokens,
                "reasoning_tokens": response.reasoning_tokens,
                "response_ref": str(response.safe_diagnostics.get("response_ref", "")),
                "stored_by_provider": bool(response.safe_diagnostics.get("store", False)),
            }
        )
        self.records.append(record)
        return response

    @staticmethod
    def _target_path(prompt: str) -> str:
        requirement_section = prompt.split("# Repository summary", 1)[0]
        matches = [
            path
            for path in ("features/alpha.py", "features/beta.py")
            if path in requirement_section
        ]
        if len(matches) != 1:
            raise ModelProviderError(
                "program_qualification_scope_unknown",
                "Program qualification objective must name exactly one fixture target path",
            )
        return matches[0]


def run_program_execution_live(
    state_root: Path,
    live_provider: OpenAIResponsesProvider,
) -> dict[str, Any]:
    state_root = state_root.resolve()
    state_root.mkdir(parents=True, exist_ok=True)
    provider = ProgramExecutionQualificationProvider(live_provider)
    preflight = _provider_preflight(provider)
    summary: dict[str, Any] = {
        "scenario": "program_execution_live",
        "provider": "openai_responses",
        "model": provider.model,
        "provider_preflight": preflight,
        "program_plan_source": "deterministic_qualification_fixture",
        "solution_scope_source": "deterministic_qualification_fixture",
        "safe_implementation_and_review_provider": "openai_responses",
        "program_automatic_execution": False,
        "cross_phase_source_handoff": False,
        "cross_phase_evidence_compilation": False,
        "hard_process_termination": False,
        "qualified": False,
    }
    if not preflight["ok"]:
        summary["provider_records"] = provider.records
        return _finish(state_root, summary)

    source = state_root / "source"
    base_sha = ""
    initial_status = ""
    previous_protocol = os.environ.get("UCA_SAFE_EDIT_PROTOCOL")
    os.environ["UCA_SAFE_EDIT_PROTOCOL"] = "v2-line-addressed"
    try:
        source.mkdir()
        _write_source(source)
        _git(source, "init", "-b", "main")
        _git(source, "config", "user.email", "program-live@example.test")
        _git(source, "config", "user.name", "Program Execution Live Lab")
        _git(source, "add", "-A")
        _git(source, "commit", "-m", "program execution live fixture")
        base_sha = _git(source, "rev-parse", "HEAD")
        initial_status = _git(source, "status", "--porcelain")

        alpha_checker = state_root / "alpha_contract_check.py"
        beta_checker = state_root / "beta_contract_check.py"
        _write_checkers(alpha_checker, beta_checker)

        product_root = state_root / "workspace"
        runtime_root = state_root / "runtime"
        program_id = "program-execution-live"
        drift_program_id = "program-execution-drift-live"
        first_workspace = ProductWorkspace.create(product_root, provider)
        first_workspace.programs.provider = _program_planner_provider()
        requirement_hash = _create_approved_program(first_workspace, program_id)
        drift_requirement_hash = _create_approved_program(
            first_workspace,
            drift_program_id,
        )
        first_workspace.programs.provider = provider
        first_runtime = ProductWebRuntime(
            workspace=first_workspace,
            state_root=runtime_root,
            allow_local_sources=True,
        )
        first_client = TestClient(create_product_app(first_runtime))
        try:
            start = first_client.post(
                f"/api/programs/{program_id}/executions/start-next",
                json=_execution_request(
                    requirement_hash,
                    source,
                    "alpha-contract",
                    alpha_checker,
                ),
            )
            _require_status(start.status_code, 202, "start phase alpha")
            awaiting = _wait_for_binding(
                first_client,
                program_id,
                binding_count=1,
                expected_status="awaiting_scope_approval",
            )
            first_binding = awaiting["bindings"][0]
            if first_binding["phase_id"] != "phase-alpha":
                raise RuntimeError("program did not schedule phase alpha first")
            if first_binding["slice_id"] != "slice-alpha":
                raise RuntimeError("program did not schedule the alpha slice first")
            provider_records_at_checkpoint = len(provider.records)
        finally:
            first_client.close()
            first_runtime.close()

        reopened = ProductWorkspace.create(product_root, provider)
        recovered_runtime = ProductWebRuntime(
            workspace=reopened,
            state_root=runtime_root,
            allow_local_sources=True,
        )
        recovered_client = TestClient(create_product_app(recovered_runtime))
        try:
            recovered_response = recovered_client.get(
                f"/api/programs/{program_id}/executions"
            )
            _require_status(recovered_response.status_code, 200, "recover program status")
            recovered = recovered_response.json()
            restart_no_provider_work = (
                recovered["runtime"]["recovered_pending"] is True
                and recovered["runtime"]["requires_explicit_action"] is True
                and len(provider.records) == provider_records_at_checkpoint
            )
            if not restart_no_provider_work:
                raise RuntimeError("restart recovery triggered work or lost the checkpoint")

            _continue(
                recovered_client,
                program_id,
                first_binding["task_id"],
                requirement_hash,
            )
            after_alpha = _wait_for_binding(
                recovered_client,
                program_id,
                binding_count=1,
                expected_status="completed",
            )
            if after_alpha["program_status"] != "running":
                raise RuntimeError("dependent phase was not left pending after phase alpha")

            beta_start = recovered_client.post(
                f"/api/programs/{program_id}/executions/start-next",
                json=_execution_request(
                    requirement_hash,
                    source,
                    "beta-contract",
                    beta_checker,
                ),
            )
            _require_status(beta_start.status_code, 202, "start phase beta")
            awaiting_beta = _wait_for_binding(
                recovered_client,
                program_id,
                binding_count=2,
                expected_status="awaiting_scope_approval",
            )
            beta_binding = awaiting_beta["bindings"][-1]
            if beta_binding["phase_id"] != "phase-beta":
                raise RuntimeError("program did not schedule dependent phase beta second")
            if beta_binding["slice_id"] != "slice-beta":
                raise RuntimeError("program did not schedule the beta slice second")

            _continue(
                recovered_client,
                program_id,
                beta_binding["task_id"],
                requirement_hash,
            )
            completed = _wait_for_binding(
                recovered_client,
                program_id,
                binding_count=2,
                expected_status="completed",
            )
            if completed["program_status"] != "completed":
                raise RuntimeError("multi-phase Program did not complete")

            records_before_drift = len(provider.records)
            drift_hash = "f" * 64
            if drift_hash == drift_requirement_hash:
                raise RuntimeError("qualification drift hash unexpectedly matched")
            drift_start = recovered_client.post(
                f"/api/programs/{drift_program_id}/executions/start-next",
                json=_execution_request(
                    drift_hash,
                    source,
                    "alpha-contract",
                    alpha_checker,
                ),
            )
            _require_status(drift_start.status_code, 202, "start drift qualification")
            drift_status = _wait_for_runtime_failure(
                recovered_client,
                drift_program_id,
            )
            drift_stop_pass = (
                drift_status["program_status"] == "realignment_required"
                and drift_status["bindings"] == []
                and drift_status["runtime"]["error_type"] == "ProgramExecutionError"
                and len(provider.records) == records_before_drift
            )
            if not drift_stop_pass:
                raise RuntimeError("requirement drift did not stop before provider work")

            bindings = completed["bindings"]
            phase_order = [item["phase_id"] for item in bindings]
            slice_order = [item["slice_id"] for item in bindings]
            phase_order_pass = phase_order == ["phase-alpha", "phase-beta"]
            slice_order_pass = slice_order == ["slice-alpha", "slice-beta"]
            phase_report_refs = {
                item["phase_id"]: item["phase_report_ref"] for item in bindings
            }
            phase_reports = {
                phase_id: reopened.artifacts.read_json(reference)
                for phase_id, reference in phase_report_refs.items()
            }
            phase_reports_pass = (
                len(phase_report_refs) == 2
                and len(set(phase_report_refs.values())) == 2
                and all(
                    report.get("phase_status") == "completed"
                    and len(report.get("bindings", [])) == 1
                    for report in phase_reports.values()
                )
            )
            evidence_ref = str(beta_binding.get("accepted_evidence_ref", ""))
            evidence_content = reopened.artifacts.read_text(evidence_ref)
            evidence_bundle = json.loads(evidence_content)
            evidence_hash = hashlib.sha256(evidence_content.encode("utf-8")).hexdigest()
            evidence_provenance_pass = (
                first_binding.get("accepted_evidence_ref", "") == ""
                and beta_binding.get("expected_base_sha") == base_sha
                and beta_binding.get("accepted_evidence_hash") == evidence_hash
                and evidence_bundle.get("target_phase_id") == "phase-beta"
                and evidence_bundle.get("requirement_hash") == requirement_hash
                and evidence_bundle.get("source_base_sha") == base_sha
                and evidence_bundle.get("dependency_phase_ids") == ["phase-alpha"]
                and len(evidence_bundle.get("phases", [])) == 1
                and evidence_bundle["phases"][0].get("reviewer_verdict") == "PASS"
                and len(evidence_bundle["phases"][0].get("tests", [])) == 1
                and len(evidence_bundle["phases"][0].get("executions", [])) == 1
            )
        finally:
            recovered_client.close()
            recovered_runtime.close()

        task_ids = [item["task_id"] for item in bindings]
        safe_reports: dict[str, dict[str, Any]] = {}
        safe_report_refs: dict[str, str] = {}
        for task_id in task_ids:
            path = (
                runtime_root
                / "safe"
                / "artifacts"
                / "tasks"
                / task_id
                / "safe-final-report.json"
            )
            safe_reports[task_id] = _read_json(path)
            safe_report_refs[task_id] = str(path.relative_to(state_root))
        safe_reports_pass = all(
            report.get("status") == "completed"
            and report.get("reviewer_verdict") == "PASS"
            and report.get("safe_errors") == []
            and report.get("source_repository_modified") is False
            and report.get("sandbox_patch_retained") is True
            for report in safe_reports.values()
        )
        live_role_coverage = {
            task_id: sorted(
                {
                    str(record["role"])
                    for record in provider.records
                    if record.get("provider") == "openai_responses"
                    and record.get("task_id") == task_id
                    and record.get("status") == "completed"
                }
            )
            for task_id in task_ids
        }
        live_role_coverage_pass = all(
            {"implementer", "reviewer"}.issubset(roles)
            for roles in (set(items) for items in live_role_coverage.values())
        )
        beta_task_id = task_ids[1]
        beta_live_evidence_roles = {
            str(record["role"])
            for record in provider.records
            if record.get("provider") == "openai_responses"
            and record.get("task_id") == beta_task_id
            and record.get("accepted_evidence_context") is True
            and record.get("status") == "completed"
        }
        beta_discovery_evidence = any(
            record.get("role") == "solution_discovery"
            and record.get("target_path") == "features/beta.py"
            and record.get("accepted_evidence_context") is True
            for record in provider.records
        )
        evidence_context_pass = (
            beta_discovery_evidence
            and {"implementer", "reviewer"}.issubset(beta_live_evidence_roles)
        )
        source_preserved = _source_preserved(source, base_sha, initial_status)
        qualified = all(
            (
                restart_no_provider_work,
                drift_stop_pass,
                phase_order_pass,
                slice_order_pass,
                phase_reports_pass,
                evidence_provenance_pass,
                evidence_context_pass,
                safe_reports_pass,
                live_role_coverage_pass,
                source_preserved,
            )
        )
        summary.update(
            {
                "qualified": qualified,
                "source_preserved": source_preserved,
                "source_base_sha": base_sha,
                "restart_checkpoint": "awaiting_scope_approval",
                "restart_no_provider_work": restart_no_provider_work,
                "explicit_start_next_and_continue_only": True,
                "dependency_order_pass": phase_order_pass and slice_order_pass,
                "phase_order": phase_order,
                "slice_order": slice_order,
                "phase_report_count": len(phase_report_refs),
                "phase_report_refs": phase_report_refs,
                "phase_reports_pass": phase_reports_pass,
                "cross_phase_evidence_compilation": True,
                "accepted_evidence_ref": evidence_ref,
                "accepted_evidence_hash": evidence_hash,
                "accepted_evidence_provenance_pass": evidence_provenance_pass,
                "accepted_evidence_context_roles": sorted(beta_live_evidence_roles),
                "accepted_evidence_discovery_context": beta_discovery_evidence,
                "accepted_evidence_context_pass": evidence_context_pass,
                "safe_report_refs": safe_report_refs,
                "safe_reports_pass": safe_reports_pass,
                "live_role_coverage": live_role_coverage,
                "live_role_coverage_pass": live_role_coverage_pass,
                "requirement_drift_stop_pass": drift_stop_pass,
                "bindings": bindings,
            }
        )
    except Exception as exc:
        source_preserved = (
            bool(base_sha)
            and source.is_dir()
            and _source_preserved(source, base_sha, initial_status)
        )
        summary.update(
            {
                "qualified": False,
                "source_preserved": source_preserved,
                "source_base_sha": base_sha,
                "failure_type": type(exc).__name__,
                "failure_code": str(getattr(exc, "code", "")),
                "failure": sanitize_text(str(exc))[:4000],
            }
        )
    finally:
        if previous_protocol is None:
            os.environ.pop("UCA_SAFE_EDIT_PROTOCOL", None)
        else:
            os.environ["UCA_SAFE_EDIT_PROTOCOL"] = previous_protocol
    summary["provider_records"] = provider.records
    return _finish(state_root, summary)


def _program_planner_provider() -> FakeModelProvider:
    def program_planner(_request):
        return {
            "title": "Live multi-phase Program qualification",
            "objective": "Qualify explicit dependency-ordered Safe execution.",
            "phases": [
                {
                    "phase_id": "phase-alpha",
                    "title": "Alpha contract",
                    "objective": "Deliver the isolated alpha feature contract.",
                    "dependencies": [],
                    "slices": [
                        {
                            "slice_id": "slice-alpha",
                            "title": "Alpha feature",
                            "objective": (
                                "In existing features/alpha.py, change only alpha_status so it "
                                "returns the exact string ready-alpha instead of pending-alpha. "
                                "Do not modify any other file or behavior."
                            ),
                            "dependencies": [],
                            "acceptance_criteria": [
                                "alpha_status returns ready-alpha.",
                                "features/beta.py remains unchanged.",
                            ],
                        }
                    ],
                    "acceptance_criteria": ["The trusted alpha contract passes."],
                },
                {
                    "phase_id": "phase-beta",
                    "title": "Beta contract",
                    "objective": "Deliver the dependent isolated beta feature contract.",
                    "dependencies": ["phase-alpha"],
                    "slices": [
                        {
                            "slice_id": "slice-beta",
                            "title": "Beta feature",
                            "objective": (
                                "In existing features/beta.py, change only beta_status so it "
                                "returns the exact string ready-beta instead of pending-beta. "
                                "Do not modify any other file or behavior. This independent Safe "
                                "sandbox must not assume unpublished phase-alpha source changes."
                            ),
                            "dependencies": [],
                            "external_dependencies": [
                                "The durable phase-alpha execution report records PASS."
                            ],
                            "acceptance_criteria": [
                                "beta_status returns ready-beta.",
                                "features/alpha.py remains at its immutable source baseline.",
                            ],
                        }
                    ],
                    "acceptance_criteria": ["The trusted beta contract passes."],
                },
            ],
            "definition_of_done": [
                "Both phase reports are durable and the source repository is preserved."
            ],
        }

    return FakeModelProvider(handlers={"program_planner": program_planner})


def _create_approved_program(workspace: ProductWorkspace, program_id: str) -> str:
    requirement = RequirementContract(
        alignment_id=f"{program_id}-requirement",
        version=1,
        title="Live Program execution qualification",
        objective="Execute two isolated feature contracts through explicit Safe checkpoints.",
        requirements=(
            RequirementItem(
                requirement_id="R-001",
                statement="Phase alpha completes before dependent phase beta starts.",
                category="delivery",
            ),
            RequirementItem(
                requirement_id="R-002",
                statement="Every unit requires explicit scope approval and preserves source.",
                category="safety",
            ),
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                criterion_id="AC-001",
                statement="Both trusted isolated feature contracts pass.",
                requirement_ids=("R-001", "R-002"),
            ),
        ),
        status=RequirementStatus.APPROVED,
    )
    requirement_hash = requirement.canonical_hash()
    plan = workspace.programs.create_program(
        program_id=program_id,
        requirement=requirement,
        requirement_hash=requirement_hash,
    )
    workspace.programs.approve_program(program_id, plan.canonical_hash())
    return requirement_hash


def _execution_request(
    requirement_hash: str,
    source: Path,
    profile_id: str,
    checker: Path,
) -> dict[str, Any]:
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id=profile_id,
                argv=(sys.executable, str(checker)),
                timeout_seconds=120,
                output_limit=20_000,
            ),
        )
    )
    return {
        "current_requirement_hash": requirement_hash,
        "repository": str(source),
        "ref": "main",
        "policy": policy.model_dump(mode="json"),
        "test_profiles": [profile_id],
    }


def _continue(
    client: TestClient,
    program_id: str,
    task_id: str,
    requirement_hash: str,
) -> None:
    response = client.post(
        f"/api/programs/{program_id}/executions/{task_id}/continue",
        json={
            "current_requirement_hash": requirement_hash,
            "approved": True,
        },
    )
    _require_status(response.status_code, 202, f"continue {task_id}")


def _wait_for_binding(
    client: TestClient,
    program_id: str,
    *,
    binding_count: int,
    expected_status: str,
    timeout_seconds: int = 900,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        response = client.get(f"/api/programs/{program_id}/executions")
        _require_status(response.status_code, 200, "read program execution")
        last = response.json()
        bindings = last["bindings"]
        if (
            len(bindings) == binding_count
            and bindings[-1]["status"] == expected_status
            and not last["runtime"]["busy"]
        ):
            return last
        if not last["runtime"]["busy"]:
            runtime_status = last["runtime"]["status"]
            binding_status = bindings[-1]["status"] if bindings else "missing"
            if runtime_status == "failed" or binding_status in {"failed", "cancelled"}:
                raise RuntimeError(
                    "program execution stopped before expected checkpoint: "
                    f"runtime={runtime_status}, binding={binding_status}, "
                    f"error={last['runtime'].get('error', '')}"
                )
        time.sleep(0.5)
    raise TimeoutError(
        f"program execution did not reach {expected_status}: "
        f"{sanitize_text(json.dumps(last, ensure_ascii=False))[:2000]}"
    )


def _wait_for_runtime_failure(
    client: TestClient,
    program_id: str,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        response = client.get(f"/api/programs/{program_id}/executions")
        _require_status(response.status_code, 200, "read drift execution")
        last = response.json()
        if last["runtime"]["status"] == "failed" and not last["runtime"]["busy"]:
            return last
        time.sleep(0.1)
    raise TimeoutError(
        "requirement drift did not reach a failed runtime boundary: "
        f"{sanitize_text(json.dumps(last, ensure_ascii=False))[:2000]}"
    )


def _write_source(source: Path) -> None:
    files = {
        "features/alpha.py": (
            "def alpha_status() -> str:\n"
            "    return \"pending-alpha\"\n"
        ),
        "features/beta.py": (
            "def beta_status() -> str:\n"
            "    return \"pending-beta\"\n"
        ),
        "README.md": (
            "# Program execution qualification fixture\n\n"
            "Alpha and beta are independent feature contracts.\n"
        ),
    }
    for relative, content in files.items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _write_checkers(alpha: Path, beta: Path) -> None:
    prefix = (
        "import os\n"
        "import sys\n\n"
        "sys.path.insert(0, os.getcwd())\n\n"
        "from features.alpha import alpha_status\n"
        "from features.beta import beta_status\n\n"
    )
    alpha.write_text(
        prefix
        + "assert alpha_status() == 'ready-alpha'\n"
        + "assert beta_status() == 'pending-beta'\n",
        encoding="utf-8",
    )
    beta.write_text(
        prefix
        + "assert alpha_status() == 'pending-alpha'\n"
        + "assert beta_status() == 'ready-beta'\n",
        encoding="utf-8",
    )


def _source_preserved(source: Path, base_sha: str, initial_status: str) -> bool:
    try:
        return (
            _git(source, "rev-parse", "HEAD") == base_sha
            and _git(source, "status", "--porcelain") == initial_status == ""
        )
    except (OSError, subprocess.SubprocessError):
        return False


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _require_status(actual: int, expected: int, action: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{action} returned HTTP {actual}, expected {expected}")


def _finish(state_root: Path, summary: dict[str, Any]) -> dict[str, Any]:
    path = state_root / "program-execution-live-summary.json"
    path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-root", required=True, type=Path)
    args = parser.parse_args()
    provider = OpenAIResponsesProvider.from_env()
    summary = run_program_execution_live(args.state_root, provider)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(
        "PROGRAM_EXECUTION_LIVE_SUMMARY="
        f"{args.state_root / 'program-execution-live-summary.json'}"
    )
    if summary.get("source_preserved") is False and summary.get("source_base_sha"):
        return 3
    if not summary.get("qualified"):
        return 2
    print("PRETRANSFER_LIVE_OPENAI_PROGRAM_EXECUTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
