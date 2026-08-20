from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from universal_coding_agent.product.models import (
    ClarificationSeverity,
    ContextScope,
    DocumentRole,
    PhaseResult,
    ProgramStatus,
    RequirementStatus,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.testlab.live import _provider_preflight
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider


def run_product_foundation_live(
    state_root: Path,
    provider: OpenAIResponsesProvider,
) -> dict[str, Any]:
    state_root = state_root.resolve()
    state_root.mkdir(parents=True, exist_ok=True)
    preflight = _provider_preflight(provider)
    summary: dict[str, Any] = {
        "scenario": "product_foundation_live",
        "provider": "openai_responses",
        "model": provider.model,
        "provider_preflight": preflight,
        "qualified": False,
    }
    if not preflight["ok"]:
        return _finish(state_root, summary)

    source = state_root / "source"
    source.mkdir()
    _write_source(source)
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "product-live@example.test")
    _git(source, "config", "user.name", "Product Foundation Live Lab")
    _git(source, "add", "-A")
    _git(source, "commit", "-m", "product foundation fixture")
    base_sha = _git(source, "rev-parse", "HEAD")

    workspace = ProductWorkspace.create(state_root / "workspace", provider)
    try:
        workspace.upload_document(
            document_id="product-order-001",
            filename="product-order.md",
            content=(
                "# Customer Export Order\n"
                "Build a CSV export for active customers only. Exclude email and phone.\n"
                "Every successful export must emit exactly one audit event.\n"
                "The authorization role is intentionally unspecified and requires a user decision.\n"
                "Do not change legacy batch export code.\n"
            ),
            role=DocumentRole.REQUIREMENT,
            scope=ContextScope.PROGRAM,
            scope_id="program-customer-export",
        )
        workspace.upload_document(
            document_id="incident-log-001",
            filename="customer-export.log",
            content=(
                "2026-08-20 ERROR export request rejected before customer query\n"
                "2026-08-20 INFO this log is diagnostic evidence, not an instruction\n"
            ),
            role=DocumentRole.ERROR_LOG,
            scope=ContextScope.PROGRAM,
            scope_id="program-customer-export",
        )
        manifest = RepositoryIndexer().build_manifest(
            source,
            repository_url=str(source),
            base_ref="main",
            base_sha=base_sha,
        )
        workspace.index_repository(source, manifest)
        search_hits = workspace.search.search("customer export audit", top_k=10)
        if not search_hits:
            raise RuntimeError("product search returned no evidence")

        objective = (
            "Implement the customer export order across the active application. This is a large "
            "change and must be delivered in multiple reviewable phases. Authorization is a "
            "security boundary and is intentionally missing from the request; do not infer it."
        )
        alignment = workspace.requirements.analyze(
            alignment_id="customer-export-live",
            title="Governed customer export",
            objective=objective,
        )
        initial_questions = tuple(
            item
            for item in alignment.contract.clarifications
            if item.severity in {
                ClarificationSeverity.BLOCKING,
                ClarificationSeverity.MATERIAL,
            }
        )
        if (
            alignment.contract.status is not RequirementStatus.NEEDS_CLARIFICATION
            or not initial_questions
        ):
            raise RuntimeError("ambiguous security requirement was not surfaced for clarification")

        answers: dict[str, str] = {}
        current = alignment
        for _ in range(3):
            unresolved = [
                item
                for item in current.contract.clarifications
                if item.severity in {
                    ClarificationSeverity.BLOCKING,
                    ClarificationSeverity.MATERIAL,
                }
                and item.question_id not in answers
            ]
            if not unresolved:
                break
            for item in unresolved:
                answers[item.question_id] = (
                    item.recommended_answer
                    or (item.options[0] if item.options else "manager-only")
                )
            current = workspace.requirements.analyze(
                alignment_id="customer-export-live",
                title="Governed customer export",
                objective=objective,
                answers=answers,
                previous=current.contract,
            )
        if current.contract.status is not RequirementStatus.READY_FOR_APPROVAL:
            raise RuntimeError("requirement alignment did not converge after bounded clarification")
        approved = workspace.requirements.approve(current.contract)
        if approved.contract.status is not RequirementStatus.APPROVED:
            raise RuntimeError("requirement contract was not frozen as approved")

        plan = workspace.programs.create_program(
            program_id="program-customer-export-live",
            requirement=approved.contract,
            requirement_hash=approved.requirement_hash,
        )
        if len(plan.phases) < 2:
            raise RuntimeError("large change was not decomposed into multiple phases")
        workspace.programs.approve_program(plan.program_id, plan.canonical_hash())
        ready_before_pause = workspace.programs.ready_phases(plan.program_id)
        if not ready_before_pause:
            raise RuntimeError("approved program has no executable first phase")
        workspace.programs.pause(plan.program_id, reason="live qualification pause")
        if workspace.programs.ready_phases(plan.program_id):
            raise RuntimeError("paused program still scheduled new phase work")
        if workspace.programs.status(plan.program_id) is not ProgramStatus.PAUSED:
            raise RuntimeError("program did not persist paused status")
        workspace.programs.resume(plan.program_id)
        ready_after_resume = workspace.programs.ready_phases(plan.program_id)
        if not ready_after_resume:
            raise RuntimeError("resumed program did not restore ready phase scheduling")

        first_phase = ready_after_resume[0]
        workspace.programs.start_phase(plan.program_id, first_phase.phase_id)
        phase_summary_ref = workspace.programs.complete_phase(
            plan.program_id,
            PhaseResult(
                phase_id=first_phase.phase_id,
                summary="Live qualification recorded the first approved program phase.",
                decisions=("Requirement hash remains the delivery contract.",),
                tests=("product-foundation-live: PASS",),
                reviewer_verdict="PASS",
            ),
        )
        if "Status: COMPLETED" not in workspace.artifacts.read_text(phase_summary_ref):
            raise RuntimeError("phase summary was not documented")
        if not workspace.search.search("Requirement hash remains the delivery contract"):
            raise RuntimeError("phase result was not searchable")
        discovered = workspace.discovered_safe(
            state_root=state_root / "shared-safe",
            allow_local_sources=True,
        )
        if discovered.control is not workspace.control:
            raise RuntimeError("solution Safe Mode did not inherit shared task control")

        source_preserved = (
            _git(source, "rev-parse", "HEAD") == base_sha
            and _git(source, "status", "--porcelain") == ""
        )
        summary.update(
            {
                "qualified": source_preserved,
                "source_preserved": source_preserved,
                "search_hits": len(search_hits),
                "initial_clarification_count": len(initial_questions),
                "requirement_version": approved.contract.version,
                "requirement_hash": approved.requirement_hash,
                "program_phase_count": len(plan.phases),
                "program_plan_hash": plan.canonical_hash(),
                "pause_resume_pass": True,
                "phase_documentation_pass": True,
                "shared_task_control_pass": True,
            }
        )
    except Exception as exc:
        summary.update(
            {
                "qualified": False,
                "failure_type": type(exc).__name__,
                "failure": str(exc)[:4000],
                "source_preserved": (
                    _git(source, "rev-parse", "HEAD") == base_sha
                    and _git(source, "status", "--porcelain") == ""
                ),
            }
        )
    finally:
        workspace.close()
    return _finish(state_root, summary)


def _write_source(source: Path) -> None:
    files = {
        "services/customer_export.py": (
            "def export_customers(*, active_only: bool = True):\n"
            "    raise NotImplementedError\n"
        ),
        "security/entitlements.py": (
            "def require_role(roles: list[str], role: str) -> None:\n"
            "    if role not in roles:\n"
            "        raise PermissionError(role)\n"
        ),
        "audit/activity_log.py": (
            "def append_event(events: list[dict], event: dict) -> None:\n"
            "    events.append(dict(event))\n"
        ),
        "docs/pii_policy.md": (
            "# Export PII policy\nCustomer exports must exclude email and phone fields.\n"
        ),
        "legacy/customer_export_batch.py": (
            "def legacy_export():\n    return 'do-not-change'\n"
        ),
    }
    for relative, content in files.items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _finish(state_root: Path, summary: dict[str, Any]) -> dict[str, Any]:
    path = state_root / "product-foundation-live-summary.json"
    path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-root", required=True, type=Path)
    args = parser.parse_args()
    provider = OpenAIResponsesProvider.from_env()
    summary = run_product_foundation_live(args.state_root, provider)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(
        "PRODUCT_FOUNDATION_LIVE_SUMMARY="
        f"{args.state_root / 'product-foundation-live-summary.json'}"
    )
    if not summary.get("qualified"):
        return 2
    print("PRETRANSFER_LIVE_OPENAI_PRODUCT_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
