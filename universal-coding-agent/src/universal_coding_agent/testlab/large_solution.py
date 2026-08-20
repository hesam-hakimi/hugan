from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from typing import Any

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    SafeModePolicy,
    SafeTaskRequest,
    TestProfile,
)
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.solution_discovery import SolutionDiscoveryService
from universal_coding_agent.testlab.live import _provider_preflight
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider

EXPECTED_SCOPE = {
    "audit/activity_log.py",
    "domain/risk_rules.py",
    "repositories/customer_state.py",
    "security/entitlements.py",
    "services/customer_account_service.py",
}

OBJECTIVE = (
    "Add temporary customer credit-limit overrides to the active customer API flow. Only actors "
    "with the manager role may create an override. A successful override stores customer_id, "
    "amount, and expires_at; appends exactly one audit event with event_type "
    "credit_limit_override_created and those same fields; and becomes the effective credit limit "
    "only while as_of is strictly earlier than expires_at. At the expiration boundary and after, "
    "the base credit limit applies. Reject non-positive amounts before any state or audit mutation. "
    "Unauthorized attempts must raise PermissionError and must not mutate state or audit. Preserve "
    "caller-owned role collections. Use the active runtime architecture and existing abstractions; "
    "do not route through legacy, batch, analytics, example, or migration implementations."
)


def active_files() -> dict[str, str]:
    return {
        "apps/api/customer_limits.py": dedent(
            '''\
            from __future__ import annotations

            from services.customer_account_service import CustomerAccountService


            def create_credit_limit_override(
                service: CustomerAccountService,
                actor_roles: list[str],
                customer_id: str,
                amount: int,
                expires_at: str,
            ):
                return service.create_credit_limit_override(
                    actor_roles,
                    customer_id,
                    amount,
                    expires_at,
                )


            def effective_credit_limit(
                service: CustomerAccountService,
                customer_id: str,
                as_of: str,
            ) -> int:
                return service.effective_credit_limit(customer_id, as_of)
            '''
        ),
        "services/customer_account_service.py": dedent(
            '''\
            from __future__ import annotations

            from audit.activity_log import record_credit_limit_override
            from domain.risk_rules import validate_credit_limit_override
            from repositories.customer_state import CustomerStateRepository
            from security.entitlements import require_manager_override_permission


            class CustomerAccountService:
                def __init__(
                    self,
                    repository: CustomerStateRepository,
                    audit_events: list[dict[str, object]],
                ) -> None:
                    self.repository = repository
                    self.audit_events = audit_events

                def create_credit_limit_override(
                    self,
                    actor_roles: list[str],
                    customer_id: str,
                    amount: int,
                    expires_at: str,
                ) -> dict[str, object]:
                    raise NotImplementedError

                def effective_credit_limit(self, customer_id: str, as_of: str) -> int:
                    return self.repository.get_base_limit(customer_id)
            '''
        ),
        "domain/risk_rules.py": dedent(
            '''\
            from __future__ import annotations


            def validate_credit_limit_override(amount: int, expires_at: str) -> None:
                return None
            '''
        ),
        "security/entitlements.py": dedent(
            '''\
            from __future__ import annotations


            def require_manager_override_permission(actor_roles: list[str]) -> None:
                return None
            '''
        ),
        "audit/activity_log.py": dedent(
            '''\
            from __future__ import annotations


            def record_credit_limit_override(
                events: list[dict[str, object]],
                customer_id: str,
                amount: int,
                expires_at: str,
            ) -> None:
                return None
            '''
        ),
        "repositories/customer_state.py": dedent(
            '''\
            from __future__ import annotations


            class CustomerStateRepository:
                def __init__(self, base_limits: dict[str, int]) -> None:
                    self._base_limits = dict(base_limits)
                    self._overrides: dict[str, dict[str, object]] = {}

                def get_base_limit(self, customer_id: str) -> int:
                    return self._base_limits[customer_id]

                def save_credit_limit_override(
                    self,
                    customer_id: str,
                    amount: int,
                    expires_at: str,
                ) -> dict[str, object]:
                    raise NotImplementedError

                def get_credit_limit_override(
                    self,
                    customer_id: str,
                ) -> dict[str, object] | None:
                    return None
            '''
        ),
        "docs/architecture.md": dedent(
            '''\
            # Runtime architecture

            User-facing HTTP handlers live under apps/api and delegate to services.
            Services coordinate domain rules, security entitlements, audit, and repositories.
            Legacy, batch, analytics, examples, and migration utilities are not runtime request paths.
            '''
        ),
    }


def decoy_files() -> dict[str, str]:
    files = {
        "legacy/credit_limit_override.py": dedent(
            '''\
            def apply_credit_limit_override(customer_id, amount, manager=True):
                return {"legacy": True, "customer_id": customer_id, "amount": amount}
            '''
        ),
        "batch/credit_limit_override_job.py": dedent(
            '''\
            def run_credit_limit_override_job():
                return "offline batch only"
            '''
        ),
        "analytics/credit_limit_override_metrics.py": dedent(
            '''\
            def credit_limit_override_audit_metrics(rows):
                return len(rows)
            '''
        ),
        "examples/credit_limit_override_demo.py": dedent(
            '''\
            def manager_credit_limit_override_demo():
                return "example only"
            '''
        ),
        "migrations/credit_limit_override_backfill.py": dedent(
            '''\
            def backfill_credit_limit_override_history():
                return "migration only"
            '''
        ),
        "docs/legacy_credit_limit_override.md": (
            "# Legacy override\n\nThis document describes the retired lending override process.\n"
        ),
    }
    groups = (
        "analytics",
        "batch",
        "billing",
        "cards",
        "collections",
        "compliance",
        "examples",
        "fraud",
        "marketing",
        "notifications",
        "reporting",
        "treasury",
        "wealth",
    )
    for group in groups:
        for index in range(13):
            if index % 4 == 0:
                function_name = f"credit_limit_manager_audit_{index:02d}"
            elif index % 4 == 1:
                function_name = f"customer_override_report_{index:02d}"
            elif index % 4 == 2:
                function_name = f"manager_entitlement_snapshot_{index:02d}"
            else:
                function_name = f"account_limit_helper_{index:02d}"
            files[f"{group}/module_{index:02d}.py"] = (
                f"def {function_name}(value=None):\n"
                f"    return ({group!r}, {index}, value)\n"
            )
    return files


def hidden_integration_test() -> str:
    return dedent(
        '''\
        import copy
        import os
        import sys

        sys.path.insert(0, os.getcwd())

        from apps.api.customer_limits import (
            create_credit_limit_override,
            effective_credit_limit,
        )
        from repositories.customer_state import CustomerStateRepository
        from services.customer_account_service import CustomerAccountService

        repository = CustomerStateRepository({"C-100": 1000, "C-200": 700})
        audit_events = []
        service = CustomerAccountService(repository, audit_events)

        employee_roles = ["employee"]
        employee_roles_before = copy.deepcopy(employee_roles)
        try:
            create_credit_limit_override(
                service,
                employee_roles,
                "C-100",
                1600,
                "2026-09-01T00:00:00Z",
            )
        except PermissionError:
            pass
        else:
            raise AssertionError("non-manager override must be rejected")
        assert employee_roles == employee_roles_before
        assert repository.get_credit_limit_override("C-100") is None
        assert audit_events == []

        try:
            create_credit_limit_override(
                service,
                ["manager"],
                "C-100",
                0,
                "2026-09-01T00:00:00Z",
            )
        except ValueError:
            pass
        else:
            raise AssertionError("non-positive override amount must be rejected")
        assert repository.get_credit_limit_override("C-100") is None
        assert audit_events == []

        manager_roles = ["employee", "manager"]
        manager_roles_before = copy.deepcopy(manager_roles)
        record = create_credit_limit_override(
            service,
            manager_roles,
            "C-100",
            1600,
            "2026-09-01T00:00:00Z",
        )
        assert manager_roles == manager_roles_before
        assert record == {
            "customer_id": "C-100",
            "amount": 1600,
            "expires_at": "2026-09-01T00:00:00Z",
        }
        assert repository.get_credit_limit_override("C-100") == record
        assert audit_events == [
            {
                "event_type": "credit_limit_override_created",
                "customer_id": "C-100",
                "amount": 1600,
                "expires_at": "2026-09-01T00:00:00Z",
            }
        ]

        assert effective_credit_limit(
            service,
            "C-100",
            "2026-08-31T23:59:59Z",
        ) == 1600
        assert effective_credit_limit(
            service,
            "C-100",
            "2026-09-01T00:00:00Z",
        ) == 1000
        assert effective_credit_limit(
            service,
            "C-100",
            "2026-09-02T00:00:00Z",
        ) == 1000
        assert effective_credit_limit(
            service,
            "C-200",
            "2026-08-31T23:59:59Z",
        ) == 700
        '''
    ).strip()


def build_large_solution(root: Path) -> str:
    source = root / "source"
    source.mkdir(parents=True)
    files = {**active_files(), **decoy_files()}
    for relative, content in files.items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "large-solution@example.test")
    _git(source, "config", "user.name", "Large Solution Lab")
    _git(source, "add", "-A")
    _git(source, "commit", "-m", "large synthetic solution")
    return _git(source, "rev-parse", "HEAD")


def run_large_solution_suite(
    state_root: Path,
    provider: OpenAIResponsesProvider,
    *,
    runs: int,
    min_success_rate: float,
) -> dict[str, Any]:
    if runs < 1 or runs > 5:
        raise ValueError("runs must be between 1 and 5")
    if not 0.0 <= min_success_rate <= 1.0:
        raise ValueError("min_success_rate must be between 0 and 1")
    state_root.mkdir(parents=True, exist_ok=True)
    provider_preflight = _provider_preflight(provider)
    records: list[dict[str, Any]] = []
    if provider_preflight["ok"]:
        for index in range(1, runs + 1):
            records.append(_run_once(state_root / f"run-{index:02d}", provider, index))

    completed = sum(record.get("status") == "completed" for record in records)
    source_mutations = sum(not record.get("source_preserved", True) for record in records)
    discovery_correct = sum(record.get("discovery_scope_exact") is True for record in records)
    success_rate = completed / runs
    summary = {
        "scenario": "large_solution_discovery_and_implementation",
        "provider": "openai_responses",
        "model": provider.model,
        "runs": runs,
        "tracked_files_per_run": len(active_files()) + len(decoy_files()),
        "attempted_runs": len(records),
        "completed": completed,
        "discovery_scope_exact": discovery_correct,
        "source_mutations": source_mutations,
        "success_rate": success_rate,
        "min_success_rate": min_success_rate,
        "qualified": (
            provider_preflight["ok"]
            and len(records) == runs
            and discovery_correct == runs
            and source_mutations == 0
            and success_rate >= min_success_rate
        ),
        "provider_preflight": provider_preflight,
        "records": records,
    }
    (state_root / "large-solution-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def _run_once(
    root: Path,
    provider: OpenAIResponsesProvider,
    run_number: int,
) -> dict[str, Any]:
    base_sha = build_large_solution(root)
    source = root / "source"
    repository = RepositorySpec(url=str(source), base_ref="main")
    source_status_before = _git(source, "status", "--porcelain")

    discovery = SolutionDiscoveryService(provider).discover(
        source,
        repository,
        base_sha=base_sha,
        objective=OBJECTIVE,
    )
    discovered_scope = {change.path for change in discovery.plan.changes}
    discovery_scope_exact = discovered_scope == EXPECTED_SCOPE
    (root / "discovery-snapshot.json").write_text(
        discovery.snapshot.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    (root / "discovery-plan.json").write_text(
        discovery.plan.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )

    if not discovery_scope_exact:
        return {
            "run": run_number,
            "status": "blocked",
            "stage": "solution_discovery",
            "discovered_scope": sorted(discovered_scope),
            "expected_scope": sorted(EXPECTED_SCOPE),
            "discovery_scope_exact": False,
            "source_preserved": (
                _git(source, "rev-parse", "HEAD") == base_sha
                and _git(source, "status", "--porcelain") == source_status_before
            ),
        }

    checker_path = root / "large_solution_hidden_check.py"
    checker_path.write_text(hidden_integration_test() + "\n", encoding="utf-8")
    allowed_changes = tuple(
        ChangeScopeEntry(
            path=change.path,
            operation=ChangeOperation.MODIFY,
            purpose=change.rationale,
        )
        for change in discovery.plan.changes
    )
    plan_hash = hashlib.sha256(
        discovery.plan.model_dump_json().encode("utf-8")
    ).hexdigest()
    manifest = ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash=plan_hash,
        allowed_changes=allowed_changes,
        test_profiles=("large-solution-contract",),
        acceptance_criteria=(
            "Only manager-role actors may create an override.",
            "Unauthorized and invalid attempts do not mutate repository or audit state.",
            "Override amount must be positive.",
            "Successful override record contains customer_id, amount, and expires_at.",
            "Successful override emits exactly one credit_limit_override_created audit event.",
            "Effective limit uses the override only while as_of is strictly before expires_at.",
            "At and after expires_at the base credit limit applies.",
            "Caller-owned role collections are not mutated.",
            "Do not change legacy, batch, analytics, examples, migrations, or unrelated files.",
        ),
        max_changed_files=len(EXPECTED_SCOPE),
    )
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="large-solution-contract",
                argv=(sys.executable, str(checker_path)),
            ),
        )
    )
    task = SafeTaskRequest(
        task_id=f"large-solution-{run_number:02d}-task",
        thread_id=f"large-solution-{run_number:02d}-thread",
        title=f"Large solution discovery and implementation {run_number}",
        objective=OBJECTIVE,
        repository=repository,
        manifest=manifest,
        policy=policy,
    )

    previous_protocol = os.environ.get("UCA_SAFE_EDIT_PROTOCOL")
    os.environ["UCA_SAFE_EDIT_PROTOCOL"] = "v2-line-addressed"
    service = SafeAgentService.create(root / "safe-state", provider, allow_local_sources=True)
    try:
        service.run(task)
        if service.state(task.thread_id)["next"] != ["scope_approval"]:
            raise RuntimeError("large solution run did not reach scope approval")
        final = service.resume(task.thread_id, True)
        report = service.artifacts.read_json(final["final_report_ref"])
    finally:
        service.close()
        if previous_protocol is None:
            os.environ.pop("UCA_SAFE_EDIT_PROTOCOL", None)
        else:
            os.environ["UCA_SAFE_EDIT_PROTOCOL"] = previous_protocol

    source_preserved = (
        _git(source, "rev-parse", "HEAD") == base_sha
        and _git(source, "status", "--porcelain") == source_status_before
    )
    return {
        "run": run_number,
        "status": report.get("status"),
        "stage": "safe_implementation",
        "discovered_scope": sorted(discovered_scope),
        "expected_scope": sorted(EXPECTED_SCOPE),
        "discovery_scope_exact": True,
        "reviewer_verdict": report.get("reviewer_verdict"),
        "safe_errors": report.get("safe_errors", []),
        "source_preserved": source_preserved,
        "sandbox_patch_retained": report.get("sandbox_patch_retained", False),
        "final_report_ref": final["final_report_ref"],
    }


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
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument(
        "--runs",
        type=int,
        default=int(os.environ.get("UCA_LARGE_SOLUTION_RUNS", "1")),
    )
    parser.add_argument(
        "--min-success-rate",
        type=float,
        default=float(os.environ.get("UCA_LARGE_SOLUTION_MIN_SUCCESS_RATE", "1.0")),
    )
    args = parser.parse_args()

    provider = OpenAIResponsesProvider.from_env()
    summary = run_large_solution_suite(
        args.state_root,
        provider,
        runs=args.runs,
        min_success_rate=args.min_success_rate,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"LARGE_SOLUTION_SUMMARY={args.state_root / 'large-solution-summary.json'}")
    if summary["source_mutations"]:
        return 3
    if not summary["qualified"]:
        return 2
    print("PRETRANSFER_LIVE_OPENAI_LARGE_SOLUTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
