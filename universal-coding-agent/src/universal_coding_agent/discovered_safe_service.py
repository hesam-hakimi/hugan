from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeScopeEntry,
    SafeContextEvidence,
    SafeModePolicy,
    SafeTaskRequest,
    safe_json,
)
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.base import ModelProvider
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.safety.sanitizer import sanitize_text
from universal_coding_agent.sandbox.git import GitSandboxManager
from universal_coding_agent.solution_discovery import (
    SolutionDiscoveryError,
    SolutionDiscoveryService,
)
from universal_coding_agent.storage.artifacts import ArtifactStore


class DiscoveredSafeStartError(RuntimeError):
    pass


@dataclass(frozen=True)
class DiscoveredSafeAgentService:
    """Discover a bounded change scope before entering the existing Safe approval gate.

    Discovery runs in its own isolated clone and never receives write authority. The resulting
    impact plan is converted into a frozen ApprovedChangeManifest whose Base SHA is the exact
    discovery checkout. Safe Mode then clones again and fails closed if the requested ref moved.
    A shared TaskControlService may be supplied so UI/program controls operate on this exact task.
    """

    state_root: Path
    provider: ModelProvider
    allow_local_sources: bool = False
    control: TaskControlService | None = None
    remote_operations: SqliteRemoteOperationLeaseStore | None = None

    @classmethod
    def create(
        cls,
        state_root: Path,
        provider: ModelProvider,
        *,
        allow_local_sources: bool = False,
        control: TaskControlService | None = None,
        remote_operations: SqliteRemoteOperationLeaseStore | None = None,
    ) -> DiscoveredSafeAgentService:
        return cls(
            state_root=state_root.resolve(),
            provider=provider,
            allow_local_sources=allow_local_sources,
            control=control,
            remote_operations=remote_operations,
        )

    def start(
        self,
        *,
        task_id: str,
        thread_id: str,
        title: str,
        objective: str,
        repository: RepositorySpec,
        policy: SafeModePolicy,
        test_profiles: tuple[str, ...],
        acceptance_criteria: tuple[str, ...] = (),
        accepted_evidence: tuple[SafeContextEvidence, ...] = (),
        expected_base_sha: str = "",
        require_publish_approval: bool = False,
    ) -> dict[str, Any]:
        requested_profiles = self._validate_test_profiles(policy, test_profiles)
        criteria = acceptance_criteria or (objective,)
        self.state_root.mkdir(parents=True, exist_ok=True)
        artifacts = ArtifactStore(self.state_root / "artifacts")
        sandbox_manager = GitSandboxManager(
            self.state_root,
            allow_local_sources=self.allow_local_sources,
        )
        discovery_sandbox_id = f"{task_id}-discovery"
        task_root = f"tasks/{task_id}"
        try:
            sandbox = sandbox_manager.prepare(discovery_sandbox_id, repository)
        except (OSError, ValueError, RuntimeError) as exc:
            raise DiscoveredSafeStartError(
                f"discovery sandbox failed safely: {type(exc).__name__}"
            ) from exc

        if expected_base_sha and sandbox.base_sha != expected_base_sha:
            drift_ref = artifacts.write_json(
                f"{task_root}/accepted-evidence-base-drift.json",
                {
                    "expected_base_sha": expected_base_sha,
                    "actual_base_sha": sandbox.base_sha,
                    "accepted_evidence_refs": [
                        item.source_ref for item in accepted_evidence
                    ],
                    "provider_work_started": False,
                },
            )
            raise DiscoveredSafeStartError(
                "accepted prior-phase evidence base SHA does not match the current "
                f"discovery checkout; diagnostic: {drift_ref.uri}"
            )

        try:
            discovery = SolutionDiscoveryService(self.provider).discover(
                Path(sandbox.path),
                repository,
                base_sha=sandbox.base_sha,
                objective=objective,
                accepted_evidence=accepted_evidence,
            )
        except SolutionDiscoveryError as exc:
            checks = sandbox_manager.read_only_git_checks(Path(sandbox.path))
            failure_ref = artifacts.write_json(
                f"{task_root}/solution-discovery-failure.json",
                {
                    "code": exc.code,
                    "message": sanitize_text(str(exc))[:4000],
                    "diagnostics": exc.diagnostics,
                    "base_sha": sandbox.base_sha,
                    "discovery_sandbox_id": discovery_sandbox_id,
                    "discovery_sandbox_path": sandbox.path,
                    "read_only_checks": checks,
                    "edit_authority_granted": False,
                },
            )
            exc.diagnostics["failure_ref"] = failure_ref.uri
            if not all(bool(item.get("passed")) for item in checks):
                raise DiscoveredSafeStartError(
                    "discovery failed and invalidated its read-only sandbox"
                ) from exc
            raise

        checks = sandbox_manager.read_only_git_checks(Path(sandbox.path))
        if not all(bool(item.get("passed")) for item in checks):
            raise DiscoveredSafeStartError("discovery changed or invalidated its read-only sandbox")

        snapshot_ref = artifacts.write_json(
            f"{task_root}/solution-discovery-snapshot.json",
            discovery.snapshot.model_dump(mode="json"),
        )
        plan_ref = artifacts.write_json(
            f"{task_root}/solution-impact-plan.json",
            discovery.plan.model_dump(mode="json"),
        )
        diagnostics_ref = artifacts.write_json(
            f"{task_root}/solution-discovery-model-validation.json",
            discovery.diagnostics,
        )
        checks_ref = artifacts.write_json(
            f"{task_root}/solution-discovery-read-only-checks.json",
            {"checks": checks},
        )

        plan_hash = hashlib.sha256(
            safe_json(discovery.plan.model_dump(mode="json")).encode("utf-8")
        ).hexdigest()
        manifest = ApprovedChangeManifest(
            base_sha=sandbox.base_sha,
            plan_hash=plan_hash,
            allowed_changes=tuple(
                ChangeScopeEntry(
                    path=change.path,
                    operation=change.operation,
                    purpose=change.rationale,
                )
                for change in discovery.plan.changes
            ),
            test_profiles=requested_profiles,
            acceptance_criteria=criteria,
            max_changed_files=len(discovery.plan.changes),
        )
        proposed_scope_ref = artifacts.write_json(
            f"{task_root}/discovered-change-manifest.json",
            manifest.model_dump(mode="json"),
        )
        provenance_ref = artifacts.write_json(
            f"{task_root}/solution-discovery-provenance.json",
            {
                "base_sha": sandbox.base_sha,
                "plan_hash": plan_hash,
                "scope_hash": manifest.canonical_hash(),
                "discovery_sandbox_id": discovery_sandbox_id,
                "discovery_sandbox_path": sandbox.path,
                "snapshot_ref": snapshot_ref.uri,
                "plan_ref": plan_ref.uri,
                "diagnostics_ref": diagnostics_ref.uri,
                "read_only_checks_ref": checks_ref.uri,
                "proposed_scope_ref": proposed_scope_ref.uri,
                "test_profiles": list(requested_profiles),
                "edit_authority_granted": False,
            },
        )

        task = SafeTaskRequest(
            task_id=task_id,
            thread_id=thread_id,
            title=title,
            objective=objective,
            repository=repository,
            manifest=manifest,
            policy=policy,
            require_publish_approval=require_publish_approval,
            context_evidence=accepted_evidence,
            metadata={
                "scope_source": "solution_discovery",
                "solution_discovery_plan_ref": plan_ref.uri,
                "solution_discovery_provenance_ref": provenance_ref.uri,
            },
        )
        safe = self._safe_service()
        try:
            state = safe.run(task)
        finally:
            safe.close()

        return {
            "state": state,
            "base_sha": sandbox.base_sha,
            "plan_hash": plan_hash,
            "scope_hash": manifest.canonical_hash(),
            "snapshot_ref": snapshot_ref.uri,
            "plan_ref": plan_ref.uri,
            "diagnostics_ref": diagnostics_ref.uri,
            "read_only_checks_ref": checks_ref.uri,
            "proposed_scope_ref": proposed_scope_ref.uri,
            "provenance_ref": provenance_ref.uri,
        }

    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]:
        safe = self._safe_service()
        try:
            return safe.resume(thread_id, approved)
        finally:
            safe.close()

    def resume_publish(
        self,
        thread_id: str,
        *,
        approved: bool,
        patch_sha256: str,
    ) -> dict[str, Any]:
        safe = self._safe_service()
        try:
            return safe.resume_publish(
                thread_id,
                approved=approved,
                patch_sha256=patch_sha256,
            )
        finally:
            safe.close()

    def pause(self, thread_id: str, *, reason: str = "") -> dict[str, Any]:
        safe = self._safe_service()
        try:
            return safe.pause(thread_id, reason=reason)
        finally:
            safe.close()

    def cancel(self, thread_id: str, *, reason: str = "") -> dict[str, Any]:
        safe = self._safe_service()
        try:
            return safe.cancel(thread_id, reason=reason)
        finally:
            safe.close()

    def resume_control(self, thread_id: str, *, action: str = "resume") -> dict[str, Any]:
        safe = self._safe_service()
        try:
            return safe.resume_control(thread_id, action=action)
        finally:
            safe.close()

    def state(self, thread_id: str) -> dict[str, Any]:
        safe = self._safe_service()
        try:
            return safe.state(thread_id)
        finally:
            safe.close()

    def _safe_service(self) -> SafeAgentService:
        return SafeAgentService.create(
            self.state_root,
            self.provider,
            allow_local_sources=self.allow_local_sources,
            control=self.control,
            remote_operations=self.remote_operations,
        )

    @staticmethod
    def _validate_test_profiles(
        policy: SafeModePolicy,
        requested: tuple[str, ...],
    ) -> tuple[str, ...]:
        if not requested:
            raise DiscoveredSafeStartError(
                "discovered Safe Mode requires at least one explicit trusted test profile"
            )
        if len(requested) != len(set(requested)):
            raise DiscoveredSafeStartError("requested test profiles must be unique")
        available = policy.profile_map()
        unknown = [profile_id for profile_id in requested if profile_id not in available]
        if unknown:
            raise DiscoveredSafeStartError(
                "requested test profiles are not present in trusted policy: "
                + ", ".join(unknown)
            )
        return requested
