from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
import urllib.parse
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, BinaryIO

if os.name == "nt":
    import msvcrt
else:
    import fcntl

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    PatchProposal,
    SafeReviewResult,
    StructuredEditProposal,
    TestExecutionResult,
)
from universal_coding_agent.product.models import ControlState
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.safe.patching import SafePatchEngine
from universal_coding_agent.source_control.base import (
    ExactPublicationRequest,
    PublicationAction,
    PublicationPartialEffects,
    SourceControlAdapter,
    SourceControlCapabilities,
    SourceControlPublicationError,
    SourceControlPublicationResult,
    normalize_base_branch,
    publication_intent_sha256,
    validate_base_branch,
    validate_head_branch,
)
from universal_coding_agent.source_control.git_metadata import (
    git_metadata_paths_are_safe,
)
from universal_coding_agent.storage.artifacts import ArtifactStore
from universal_coding_agent.storage.source_control import (
    PublicationIntentConflict,
    PublicationRecord,
    SourceControlPublicationStore,
)

_HASH = re.compile(r"^[0-9a-f]{64}$")
_TASK_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")


@contextmanager
def _exclusive_file_lock(handle: BinaryIO) -> Iterator[None]:
    if os.name == "nt":
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        try:
            yield
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return

    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    try:
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class ExactPatchPublicationError(RuntimeError):
    """Stable fail-closed error for exact publication preflight or verification."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"exact patch publication failed safely: {code}")


class ExactPatchPublicationService:
    """Consume one durable exact-patch approval through a trusted adapter.

    Publication is intentionally outside LangGraph so an irreversible network effect is never
    replayed merely because a graph checkpoint was not committed. The durable intent store and
    exact adapter request support reconciliation of a crash-left ``planned`` publication.
    """

    def __init__(
        self,
        state_root: Path,
        adapter: SourceControlAdapter,
    ) -> None:
        if not isinstance(adapter, SourceControlAdapter):
            raise TypeError("source-control adapter is incompatible")
        self.state_root = state_root.resolve()
        self.artifacts = ArtifactStore(self.state_root / "artifacts")
        self.store = SourceControlPublicationStore(
            self.state_root / "source-control-publications.sqlite"
        )
        self.adapter = adapter
        self.patch_engine = SafePatchEngine()
        self.locks_root = self.state_root / "source-control-locks"
        self.locks_root.mkdir(parents=True, exist_ok=True)

    def close(self) -> None:
        self.store.close()

    def publish_exact(
        self,
        task_id: str,
        *,
        approval_sha256: str,
        patch_sha256: str,
        action: PublicationAction | str,
        head_branch: str,
    ) -> dict[str, Any]:
        normalized_task_id = task_id.strip()
        normalized_approval_hash = approval_sha256.strip().lower()
        normalized_patch_hash = patch_sha256.strip().lower()
        if _TASK_ID.fullmatch(normalized_task_id) is None:
            raise ExactPatchPublicationError("invalid_task_id")
        if _HASH.fullmatch(normalized_approval_hash) is None:
            raise ExactPatchPublicationError("invalid_approval_sha256")
        if _HASH.fullmatch(normalized_patch_hash) is None:
            raise ExactPatchPublicationError("invalid_patch_sha256")
        try:
            requested_action = PublicationAction(action)
        except ValueError as exc:
            raise ExactPatchPublicationError("invalid_publication_action") from exc
        try:
            normalized_head_branch = validate_head_branch(head_branch)
        except ValueError as exc:
            raise ExactPatchPublicationError("invalid_head_branch") from exc

        lock_path = self.locks_root / f"{normalized_task_id}.lock"
        with lock_path.open("a+b") as lock_handle:
            with _exclusive_file_lock(lock_handle):
                existing = self.store.get_for_authority(
                    task_id=normalized_task_id,
                    approval_sha256=normalized_approval_hash,
                )
                if existing is not None:
                    self._require_same_requested_authority(
                        existing.request,
                        task_id=normalized_task_id,
                        approval_sha256=normalized_approval_hash,
                        patch_sha256=normalized_patch_hash,
                        action=requested_action,
                        head_branch=normalized_head_branch,
                    )
                    if existing.status == "completed":
                        receipt = self._validated_completed_receipt(existing)
                        self._sync_attempt_artifacts(
                            normalized_task_id,
                            existing.publication_id,
                            through_attempt=existing.attempts,
                        )
                        return self._persist_receipt(
                            normalized_task_id,
                            receipt,
                            replayed=True,
                            attempts=existing.attempts,
                        )
                    self._require_same_adapter_identity(existing.request)
                request = self._prepare_request(
                    normalized_task_id,
                    approval_sha256=normalized_approval_hash,
                    patch_sha256=normalized_patch_hash,
                    action=requested_action,
                    head_branch=normalized_head_branch,
                )
                return self._publish_reserved(request)

    @staticmethod
    def _require_same_requested_authority(
        stored: dict[str, object],
        *,
        task_id: str,
        approval_sha256: str,
        patch_sha256: str,
        action: PublicationAction,
        head_branch: str,
    ) -> None:
        if not (
            stored.get("task_id") == task_id
            and stored.get("approval_sha256") == approval_sha256
            and stored.get("patch_sha256") == patch_sha256
            and stored.get("action") == action.value
            and stored.get("head_branch") == head_branch
        ):
            raise ExactPatchPublicationError("publication_intent_conflict")

    def _validated_completed_receipt(
        self,
        record: PublicationRecord,
    ) -> dict[str, object]:
        receipt = record.receipt
        if not isinstance(receipt, dict):
            raise ExactPatchPublicationError("publication_receipt_invalid")
        request = record.request
        stored_attempt = self.store.get_attempt(record.publication_id, record.attempts)
        if stored_attempt is None:
            raise ExactPatchPublicationError("publication_receipt_invalid")
        attempt_outcome, attempt_receipt = stored_attempt
        try:
            result = SourceControlPublicationResult.model_validate(receipt.get("result"))
            action = PublicationAction(request.get("action"))
            head_branch = validate_head_branch(str(request.get("head_branch", "")))
            base_branch = validate_base_branch(str(request.get("base_ref", "")))
        except (TypeError, ValueError) as exc:
            raise ExactPatchPublicationError("publication_receipt_invalid") from exc
        expected_local_ref = f"refs/heads/{head_branch}"
        draft = result.draft_pr
        reconciled_existing_effects = bool(
            record.attempts > 1
            and (
                not result.commit_created
                or (
                    action in {PublicationAction.PUSH, PublicationAction.DRAFT_PR}
                    and not result.push_performed
                )
                or (
                    action is PublicationAction.DRAFT_PR
                    and draft is not None
                    and not draft.created
                )
            )
        )
        (
            effect_attribution_indeterminate,
            expected_source_repository_modified,
        ) = self._completed_remote_effect_attribution(
            record.publication_id,
            action,
            result,
        )
        result_binding_valid = (
            result.publication_id == record.publication_id
            and result.action is action
            and result.local_ref == expected_local_ref
            and receipt.get("commit_created") == result.commit_created
            and receipt.get("local_ref_created") == result.local_ref_created
            and receipt.get("local_ref_updated") == result.local_ref_updated
            and receipt.get("push_performed") == result.push_performed
            and receipt.get("push_verified") == result.pushed
            and receipt.get("draft_pr_created")
            == (draft.created if draft is not None else False)
            and receipt.get("reconciled_existing_effects")
            is reconciled_existing_effects
            and receipt.get("effect_attribution_indeterminate")
            is effect_attribution_indeterminate
            and receipt.get("source_repository_modified")
            == expected_source_repository_modified
        )
        if action is PublicationAction.COMMIT:
            result_binding_valid = result_binding_valid and not (
                result.pushed
                or result.push_performed
                or result.remote_before_sha
                or result.remote_after_sha
                or draft is not None
            )
        elif action is PublicationAction.PUSH:
            result_binding_valid = result_binding_valid and (
                result.pushed
                and result.remote_after_sha == result.commit_sha
                and result.remote_before_sha
                in {"", result.commit_sha}
                and result.push_performed
                == (result.remote_before_sha != result.commit_sha)
                and draft is None
            )
        else:
            result_binding_valid = result_binding_valid and (
                result.pushed
                and result.remote_after_sha == result.commit_sha
                and result.remote_before_sha
                in {"", result.commit_sha}
                and result.push_performed
                == (result.remote_before_sha != result.commit_sha)
                and draft is not None
                and draft.draft is True
                and draft.base_branch == base_branch
                and draft.head_branch == head_branch
                and draft.head_sha == result.commit_sha
            )
        if not (
            receipt.get("status") == "completed"
            and receipt.get("schema_version") == "1"
            and receipt.get("qualified") is True
            and receipt.get("commit_verified") is True
            and receipt.get("side_effects_indeterminate") is False
            and receipt.get("reconciliation_required") is False
            and receipt.get("merge_performed") is False
            and receipt.get("deployment_performed") is False
            and receipt.get("attempt") == record.attempts
            and attempt_outcome == "completed"
            and attempt_receipt == receipt
            and result_binding_valid
            and all(receipt.get(field) == value for field, value in request.items())
            and receipt.get("publication_id") == record.publication_id
            and receipt.get("task_id") == record.task_id
            and receipt.get("approval_sha256") == record.approval_sha256
            and receipt.get("intent_sha256") == record.intent_sha256
        ):
            raise ExactPatchPublicationError("publication_receipt_invalid")
        return receipt

    def _require_same_adapter_identity(self, stored: dict[str, object]) -> None:
        try:
            capabilities = SourceControlCapabilities.model_validate(
                self.adapter.capabilities()
            )
        except Exception as exc:
            raise ExactPatchPublicationError("adapter_capabilities_invalid") from exc
        expected_draft_identity = (
            capabilities.draft_pr_identity
            if stored.get("action") == PublicationAction.DRAFT_PR.value
            else ""
        )
        if (
            stored.get("adapter_identity") != capabilities.adapter_identity
            or stored.get("draft_pr_identity") != expected_draft_identity
        ):
            raise ExactPatchPublicationError("publication_intent_conflict")

    def _prepare_request(
        self,
        task_id: str,
        *,
        approval_sha256: str,
        patch_sha256: str,
        action: PublicationAction,
        head_branch: str,
    ) -> ExactPublicationRequest:
        approval_ref = f"artifact://tasks/{task_id}/publish-approval.json"
        try:
            approval = self.artifacts.read_json_bounded_verified(
                approval_ref,
                expected_sha256=approval_sha256,
                max_bytes=256_000,
            )
        except (OSError, ValueError, TypeError) as exc:
            raise ExactPatchPublicationError("approval_integrity_invalid") from exc
        if not isinstance(approval, dict):
            raise ExactPatchPublicationError("approval_payload_invalid")

        self._validate_approval(
            task_id,
            approval,
            approval_ref=approval_ref,
            patch_sha256=patch_sha256,
        )
        thread_id = str(approval["thread_id"])
        try:
            repository = RepositorySpec.model_validate(approval["repository"])
        except (TypeError, ValueError) as exc:
            raise ExactPatchPublicationError("approval_repository_invalid") from exc
        parsed_repository = urllib.parse.urlsplit(repository.url)
        if (
            parsed_repository.username
            or parsed_repository.password
            or parsed_repository.query
            or parsed_repository.fragment
        ):
            raise ExactPatchPublicationError("approval_repository_credentials_forbidden")
        if (
            "://" not in repository.url
            and not repository.url.startswith("git@")
            and not Path(repository.url).is_absolute()
        ):
            raise ExactPatchPublicationError("approval_relative_repository_forbidden")
        try:
            base_branch = validate_base_branch(repository.base_ref)
        except ValueError as exc:
            raise ExactPatchPublicationError("approval_base_branch_invalid") from exc
        scope_ref = str(approval["scope_ref"])
        edit_proposal_ref = str(approval["edit_proposal_ref"])
        patch_proposal_ref = str(approval["patch_proposal_ref"])
        patch_ref = str(approval["patch_ref"])

        try:
            manifest = ApprovedChangeManifest.model_validate(
                self.artifacts.read_json_bounded(scope_ref, max_bytes=512_000)
            )
            edit_proposal = StructuredEditProposal.model_validate(
                self.artifacts.read_json_bounded(
                    edit_proposal_ref,
                    max_bytes=2_500_000,
                )
            )
            patch_proposal = PatchProposal.model_validate(
                self.artifacts.read_json_bounded(
                    patch_proposal_ref,
                    max_bytes=4_500_000,
                )
            )
            patch_text = self.artifacts.read_text_bounded_verified(
                patch_ref,
                expected_sha256=patch_sha256,
                max_bytes=2_000_000,
            )
            tests_payload = self.artifacts.read_json_bounded_verified(
                str(approval["tests_ref"]),
                expected_sha256=str(approval["tests_sha256"]),
                max_bytes=2_000_000,
            )
            review_payload = self.artifacts.read_json_bounded_verified(
                str(approval["review_ref"]),
                expected_sha256=str(approval["review_sha256"]),
                max_bytes=1_000_000,
            )
        except (OSError, ValueError, TypeError) as exc:
            raise ExactPatchPublicationError("approved_evidence_invalid") from exc

        changed_paths = tuple(str(path) for path in approval["changed_paths"])
        if manifest.base_sha != approval["base_sha"]:
            raise ExactPatchPublicationError("approval_base_mismatch")
        if manifest.plan_hash != approval["plan_hash"]:
            raise ExactPatchPublicationError("approval_plan_mismatch")
        if manifest.canonical_hash() != approval["scope_hash"]:
            raise ExactPatchPublicationError("approval_scope_mismatch")
        if patch_proposal.unified_diff != patch_text:
            raise ExactPatchPublicationError("approved_patch_artifact_mismatch")
        if patch_proposal.changed_paths != changed_paths:
            raise ExactPatchPublicationError("approved_path_order_mismatch")
        if edit_proposal.changed_paths != changed_paths:
            raise ExactPatchPublicationError("approved_edit_path_mismatch")
        try:
            if not isinstance(tests_payload, dict):
                raise ValueError("test evidence must be an object")
            test_results = tuple(
                TestExecutionResult.model_validate(item)
                for item in tests_payload.get("results", [])
            )
            review_result = SafeReviewResult.model_validate(review_payload)
        except (TypeError, ValueError) as exc:
            raise ExactPatchPublicationError("approved_evidence_invalid") from exc
        if not self._quality_evidence_valid(
            tests_payload,
            test_results,
            changed_paths,
            manifest.test_profiles,
            review_result,
            str(approval["reviewer_verdict"]),
        ):
            raise ExactPatchPublicationError("approved_quality_evidence_invalid")

        self._validate_completed_task(
            task_id,
            thread_id=thread_id,
            approval_ref=approval_ref,
            approval_sha256=approval_sha256,
            patch_sha256=patch_sha256,
        )
        sandbox_id = str(approval["sandbox_id"])
        if sandbox_id != task_id:
            raise ExactPatchPublicationError("approval_sandbox_mismatch")
        sandboxes_root = (self.state_root / "sandboxes").resolve()
        sandbox_path = (sandboxes_root / sandbox_id / "repo").resolve()
        if sandboxes_root not in sandbox_path.parents or not sandbox_path.is_dir():
            raise ExactPatchPublicationError("sandbox_unavailable")
        self._require_safe_local_config(sandbox_path)
        if not self._base_branch_at_sha(sandbox_path, base_branch, manifest.base_sha):
            raise ExactPatchPublicationError("approval_base_branch_invalid")
        try:
            materialized = self.patch_engine.capture_worktree_proposal(
                sandbox_path,
                manifest,
                edit_proposal,
            )
            validation = self.patch_engine.validate_materialized(
                sandbox_path,
                manifest,
                patch_proposal,
            )
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            raise ExactPatchPublicationError("materialized_patch_invalid") from exc
        if (
            not validation.valid
            or validation.patch_sha256 != patch_sha256
            or materialized.unified_diff != patch_text
            or materialized.changed_paths != changed_paths
        ):
            raise ExactPatchPublicationError("materialized_patch_drift")
        if not self._index_is_clean(sandbox_path):
            raise ExactPatchPublicationError("sandbox_index_not_clean")

        try:
            capabilities = SourceControlCapabilities.model_validate(self.adapter.capabilities())
        except Exception as exc:
            raise ExactPatchPublicationError("adapter_capabilities_invalid") from exc
        self._require_capability(capabilities, action)
        effective_draft_pr_identity = (
            capabilities.draft_pr_identity
            if action is PublicationAction.DRAFT_PR
            else ""
        )

        commit_message = f"UCA: {task_id}"
        draft_pr_title = f"UCA: {task_id}" if action is PublicationAction.DRAFT_PR else ""
        draft_pr_body = (
            "Automated Draft PR for an exact Safe Mode patch.\n\n"
            f"Task: `{task_id}`\n"
            f"Base SHA: `{manifest.base_sha}`\n"
            f"Patch SHA-256: `{patch_sha256}`\n"
            f"Approval SHA-256: `{approval_sha256}`\n"
            if action is PublicationAction.DRAFT_PR
            else ""
        ).rstrip()
        intent_sha256 = publication_intent_sha256(
            approval_sha256=approval_sha256,
            patch_sha256=patch_sha256,
            repository=repository,
            manifest=manifest,
            changed_paths=changed_paths,
            head_branch=head_branch,
            action=action,
            commit_message=commit_message,
            draft_pr_title=draft_pr_title,
            draft_pr_body=draft_pr_body,
            adapter_identity=capabilities.adapter_identity,
            draft_pr_identity=effective_draft_pr_identity,
        )
        publication_id = hashlib.sha256(
            f"{approval_sha256}:{intent_sha256}".encode("ascii")
        ).hexdigest()
        try:
            return ExactPublicationRequest(
                publication_id=publication_id,
                approval_ref=approval_ref,
                approval_sha256=approval_sha256,
                patch_ref=patch_ref,
                patch_sha256=patch_sha256,
                intent_sha256=intent_sha256,
                task_id=task_id,
                thread_id=thread_id,
                repository=repository,
                sandbox_path=str(sandbox_path),
                sandboxes_root=str(sandboxes_root),
                manifest=manifest,
                edit_proposal=edit_proposal,
                patch_text=patch_text,
                changed_paths=changed_paths,
                head_branch=head_branch,
                action=action,
                adapter_identity=capabilities.adapter_identity,
                draft_pr_identity=effective_draft_pr_identity,
                commit_message=commit_message,
                draft_pr_title=draft_pr_title,
                draft_pr_body=draft_pr_body,
            )
        except ValueError as exc:
            raise ExactPatchPublicationError("publication_intent_invalid") from exc

    def _publish_reserved(self, request: ExactPublicationRequest) -> dict[str, Any]:
        intent_record = self._intent_record(request)
        try:
            reserved = self.store.reserve(
                publication_id=request.publication_id,
                task_id=request.task_id,
                approval_sha256=request.approval_sha256,
                intent_sha256=request.intent_sha256,
                request=intent_record,
            )
        except PublicationIntentConflict as exc:
            raise ExactPatchPublicationError("publication_intent_conflict") from exc

        if reserved.status == "completed":
            receipt = self._validated_completed_receipt(reserved)
            self._sync_attempt_artifacts(
                request.task_id,
                reserved.publication_id,
                through_attempt=reserved.attempts,
            )
            return self._persist_receipt(
                request.task_id,
                receipt,
                replayed=True,
                attempts=reserved.attempts,
            )

        self._sync_attempt_artifacts(
            request.task_id,
            reserved.publication_id,
            through_attempt=reserved.attempts - 1,
        )

        self.artifacts.write_json(
            f"tasks/{request.task_id}/source-control-publication-intent.json",
            {
                "schema_version": "1",
                **intent_record,
                "status": "planned",
                "attempts": reserved.attempts,
                "source_control_side_effects": False,
            },
        )
        result: SourceControlPublicationResult | None = None
        try:
            result = SourceControlPublicationResult.model_validate(
                self.adapter.publish_exact(request)
            )
            self._validate_result(request, result)
            self._verify_result_repository_state(request, result)
        except SourceControlPublicationError as exc:
            receipt = self._failure_receipt(
                request,
                exc.code,
                exc.stage,
                exc.cause_type,
                exc.partial_effects,
                side_effects_indeterminate=self._effects_indeterminate(exc.partial_effects),
                remote_effects_indeterminate=self._remote_effects_indeterminate(
                    request.action,
                    exc.partial_effects,
                ),
                partial_effects_attribution_trusted=True,
            )
            receipt["attempt"] = reserved.attempts
            record = self.store.record_retryable_failure(
                request.publication_id,
                receipt,
            )
            return self._persist_receipt(
                request.task_id,
                receipt,
                replayed=False,
                attempts=record.attempts,
            )
        except ExactPatchPublicationError as exc:
            receipt = self._failure_receipt(
                request,
                exc.code,
                "validate_result",
                type(exc).__name__,
                self._partial_effects_from_result(result),
                side_effects_indeterminate=True,
                remote_effects_indeterminate=(
                    request.action is not PublicationAction.COMMIT
                ),
                partial_effects_attribution_trusted=False,
            )
            receipt["attempt"] = reserved.attempts
            record = self.store.record_retryable_failure(
                request.publication_id,
                receipt,
            )
            return self._persist_receipt(
                request.task_id,
                receipt,
                replayed=False,
                attempts=record.attempts,
            )
        except Exception as exc:
            receipt = self._failure_receipt(
                request,
                "adapter_result_invalid" if result is None else "adapter_unexpected_failure",
                "validate_result" if result is None else "publish_exact",
                type(exc).__name__,
                self._partial_effects_from_result(result),
                side_effects_indeterminate=True,
                remote_effects_indeterminate=(
                    request.action is not PublicationAction.COMMIT
                ),
                partial_effects_attribution_trusted=False,
            )
            receipt["attempt"] = reserved.attempts
            record = self.store.record_retryable_failure(
                request.publication_id,
                receipt,
            )
            return self._persist_receipt(
                request.task_id,
                receipt,
                replayed=False,
                attempts=record.attempts,
            )

        draft_created = result.draft_pr.created if result.draft_pr is not None else False
        reconciled_existing_effects = bool(
            reserved.attempts > 1
            and (
                not result.commit_created
                or (
                    request.action in {PublicationAction.PUSH, PublicationAction.DRAFT_PR}
                    and not result.push_performed
                )
                or (
                    request.action is PublicationAction.DRAFT_PR
                    and result.draft_pr is not None
                    and not draft_created
                )
            )
        )
        (
            effect_attribution_indeterminate,
            source_repository_modified,
        ) = self._completed_remote_effect_attribution(
            request.publication_id,
            request.action,
            result,
        )
        receipt = {
            "schema_version": "1",
            "status": "completed",
            "qualified": True,
            "attempt": reserved.attempts,
            **self._intent_record(request),
            "adapter": type(self.adapter).__name__,
            "result": result.model_dump(mode="json"),
            "commit_verified": True,
            "commit_created": result.commit_created,
            "local_ref_created": result.local_ref_created,
            "local_ref_updated": result.local_ref_updated,
            "push_performed": result.push_performed,
            "push_verified": result.pushed,
            "draft_pr_created": draft_created,
            "reconciled_existing_effects": reconciled_existing_effects,
            "effect_attribution_indeterminate": effect_attribution_indeterminate,
            "source_repository_modified": source_repository_modified,
            "merge_performed": False,
            "deployment_performed": False,
            "side_effects_indeterminate": False,
            "reconciliation_required": False,
        }
        record = self.store.complete(request.publication_id, receipt)
        return self._persist_receipt(
            request.task_id,
            receipt,
            replayed=False,
            attempts=record.attempts,
        )

    @staticmethod
    def _validate_approval(
        task_id: str,
        approval: dict[str, Any],
        *,
        approval_ref: str,
        patch_sha256: str,
    ) -> None:
        required = {
            "schema_version",
            "task_id",
            "thread_id",
            "approved",
            "binding_valid",
            "decision_received",
            "decided_at",
            "repository",
            "sandbox_id",
            "base_sha",
            "plan_hash",
            "scope_hash",
            "scope_ref",
            "edit_proposal_ref",
            "patch_proposal_ref",
            "patch_ref",
            "patch_sha256",
            "confirmed_patch_sha256",
            "changed_paths",
            "tests_ref",
            "tests_sha256",
            "review_ref",
            "review_sha256",
            "reviewer_verdict",
            "source_control_side_effects",
        }
        if required - set(approval):
            raise ExactPatchPublicationError("approval_payload_incomplete")
        if approval["schema_version"] != "2" or approval["task_id"] != task_id:
            raise ExactPatchPublicationError("approval_identity_mismatch")
        if approval_ref != f"artifact://tasks/{task_id}/publish-approval.json":
            raise ExactPatchPublicationError("approval_reference_mismatch")
        if not (
            approval["approved"] is True
            and approval["binding_valid"] is True
            and approval["decision_received"] is True
        ):
            raise ExactPatchPublicationError("publication_not_approved")
        if not isinstance(approval["decided_at"], str) or not approval["decided_at"].strip():
            raise ExactPatchPublicationError("approval_decision_time_invalid")
        if (
            approval["patch_sha256"] != patch_sha256
            or approval["confirmed_patch_sha256"] != patch_sha256
        ):
            raise ExactPatchPublicationError("approval_patch_mismatch")
        if approval["reviewer_verdict"] != "PASS":
            raise ExactPatchPublicationError("approval_review_not_passed")
        if not approval["tests_ref"] or not approval["review_ref"]:
            raise ExactPatchPublicationError("approval_evidence_missing")
        if not (
            isinstance(approval["tests_sha256"], str)
            and _HASH.fullmatch(approval["tests_sha256"])
            and isinstance(approval["review_sha256"], str)
            and _HASH.fullmatch(approval["review_sha256"])
        ):
            raise ExactPatchPublicationError("approval_evidence_hash_invalid")
        if approval["source_control_side_effects"] is not False:
            raise ExactPatchPublicationError("approval_already_consumed")
        if not isinstance(approval["changed_paths"], list) or not approval["changed_paths"]:
            raise ExactPatchPublicationError("approval_paths_invalid")

    def _validate_completed_task(
        self,
        task_id: str,
        *,
        thread_id: str,
        approval_ref: str,
        approval_sha256: str,
        patch_sha256: str,
    ) -> None:
        try:
            report = self.artifacts.read_json_bounded(
                f"artifact://tasks/{task_id}/safe-final-report.json",
                max_bytes=1_000_000,
            )
        except (OSError, ValueError, TypeError) as exc:
            raise ExactPatchPublicationError("final_report_invalid") from exc
        if not isinstance(report, dict):
            raise ExactPatchPublicationError("final_report_invalid")
        expected = (
            report.get("task_id") == task_id
            and report.get("thread_id") == thread_id
            and report.get("status") == "completed"
            and report.get("publish_approved") is True
            and report.get("publish_approval_ref") == approval_ref
            and report.get("publish_approval_sha256") == approval_sha256
            and report.get("publish_patch_sha256") == patch_sha256
            and report.get("sandbox_patch_retained") is True
            and report.get("rolled_back") is False
        )
        if not expected:
            raise ExactPatchPublicationError("safe_task_not_publishable")

        control = TaskControlService(self.state_root / "task-control.sqlite")
        try:
            record = control.get_task(task_id)
            if record is None or record.state is not ControlState.COMPLETED:
                raise ExactPatchPublicationError("task_control_not_completed")
        finally:
            control.close()

    @staticmethod
    def _require_capability(
        capabilities: SourceControlCapabilities,
        action: PublicationAction,
    ) -> None:
        if not capabilities.commit:
            raise ExactPatchPublicationError("adapter_commit_unsupported")
        if action in {PublicationAction.PUSH, PublicationAction.DRAFT_PR} and not (
            capabilities.push
        ):
            raise ExactPatchPublicationError("adapter_push_unsupported")
        if action is PublicationAction.DRAFT_PR and not capabilities.draft_pr:
            raise ExactPatchPublicationError("adapter_draft_pr_unsupported")

    @staticmethod
    def _quality_evidence_valid(
        tests_payload: dict[str, object],
        test_results: tuple[TestExecutionResult, ...],
        changed_paths: tuple[str, ...],
        required_profiles: tuple[str, ...],
        review_result: SafeReviewResult,
        reviewer_verdict: str,
    ) -> bool:
        actual_paths = tuple(tests_payload.get("actual_changed_paths", ()))
        actual_profiles = tuple(result.profile_id for result in test_results)
        return bool(
            tests_payload.get("scope_intact") is True
            and len(actual_paths) == len(changed_paths)
            and set(actual_paths) == set(changed_paths)
            and len(actual_profiles) == len(required_profiles)
            and set(actual_profiles) == set(required_profiles)
            and all(result.passed and result.returncode == 0 for result in test_results)
            and review_result.verdict.value == "PASS"
            and reviewer_verdict == review_result.verdict.value
        )

    @staticmethod
    def _validate_result(
        request: ExactPublicationRequest,
        result: SourceControlPublicationResult,
    ) -> None:
        expected_ref = f"refs/heads/{request.head_branch}"
        if (
            result.publication_id != request.publication_id
            or result.action is not request.action
            or result.local_ref != expected_ref
        ):
            raise ExactPatchPublicationError("adapter_result_binding_mismatch")
        if request.action is PublicationAction.COMMIT:
            if (
                result.pushed
                or result.push_performed
                or result.remote_before_sha
                or result.remote_after_sha
                or result.draft_pr is not None
            ):
                raise ExactPatchPublicationError("adapter_result_exceeded_authority")
        elif request.action is PublicationAction.PUSH:
            if (
                not result.pushed
                or result.remote_after_sha != result.commit_sha
                or result.remote_before_sha
                not in {"", result.commit_sha}
                or result.push_performed != (result.remote_before_sha != result.commit_sha)
                or result.draft_pr is not None
            ):
                raise ExactPatchPublicationError("adapter_result_binding_mismatch")
        else:
            draft = result.draft_pr
            if (
                not result.pushed
                or result.remote_after_sha != result.commit_sha
                or result.remote_before_sha
                not in {"", result.commit_sha}
                or result.push_performed != (result.remote_before_sha != result.commit_sha)
                or draft is None
                or draft.draft is not True
                or draft.base_branch != normalize_base_branch(request.repository.base_ref)
                or draft.head_branch != request.head_branch
                or draft.head_sha != result.commit_sha
            ):
                raise ExactPatchPublicationError("adapter_draft_pr_binding_mismatch")

    @staticmethod
    def _partial_effects_from_result(
        result: SourceControlPublicationResult | None,
    ) -> PublicationPartialEffects:
        if result is None:
            return PublicationPartialEffects()
        return PublicationPartialEffects(
            commit_created=result.commit_created,
            commit_sha=result.commit_sha,
            local_ref_attempted=True,
            local_ref_verified=True,
            local_ref_created=result.local_ref_created,
            local_ref_updated=result.local_ref_updated,
            local_ref=result.local_ref,
            push_attempted=result.push_performed,
            push_verified=result.pushed,
            remote_sha=result.remote_after_sha,
            draft_pr_attempted=result.draft_pr is not None,
            draft_pr_created=(result.draft_pr.created if result.draft_pr is not None else False),
            draft_pr_url=(result.draft_pr.url if result.draft_pr is not None else ""),
        )

    def _verify_result_repository_state(
        self,
        request: ExactPublicationRequest,
        result: SourceControlPublicationResult,
    ) -> None:
        root = Path(request.sandbox_path)
        self._require_safe_local_config(root)
        if not git_metadata_paths_are_safe(root, local_ref=result.local_ref):
            raise ExactPatchPublicationError("sandbox_git_metadata_unsafe")
        try:
            local_symbolic = self._run_git(
                root,
                ["symbolic-ref", "-q", result.local_ref],
                check=False,
            )
            if local_symbolic.returncode == 0:
                raise ExactPatchPublicationError(
                    "adapter_result_symbolic_ref_forbidden"
                )
            local_sha = self._run_git(
                root,
                ["rev-parse", "--verify", f"{result.local_ref}^{{commit}}"],
            ).stdout.strip()
            raw_commit = self._run_git(
                root,
                ["cat-file", "commit", result.commit_sha],
            ).stdout
            header, separator, message = raw_commit.partition("\n\n")
            header_lines = header.splitlines()
            tree_headers = [
                line.removeprefix("tree ")
                for line in header_lines
                if line.startswith("tree ")
            ]
            parents = [
                line.removeprefix("parent ")
                for line in header_lines
                if line.startswith("parent ")
            ]
            changed_paths = tuple(
                line
                for line in self._run_git(
                    root,
                    [
                        "diff",
                        "--name-only",
                        request.manifest.base_sha,
                        result.commit_sha,
                    ],
                ).stdout.splitlines()
                if line
            )
            sections: list[str] = []
            for path in request.changed_paths:
                section = self._run_git(
                    root,
                    [
                        "diff",
                        "--no-ext-diff",
                        "--no-textconv",
                        "--no-color",
                        "--full-index",
                        request.manifest.base_sha,
                        result.commit_sha,
                        "--",
                        path,
                    ],
                ).stdout
                sections.append(section if section.endswith("\n") else section + "\n")
            committed_patch = "".join(sections)
            head_sha = self._run_git(root, ["rev-parse", "HEAD"]).stdout.strip()
            if request.action is not PublicationAction.COMMIT:
                remote_ref = f"refs/heads/{request.head_branch}"
                remote = self._run_remote_git(
                    [
                        "ls-remote",
                        "--symref",
                        "--exit-code",
                        "--heads",
                        "--end-of-options",
                        request.repository.url,
                        remote_ref,
                    ],
                ).stdout.split()
                remote_verified = remote == [result.commit_sha, remote_ref]
                remote_base_ref = (
                    f"refs/heads/{validate_base_branch(request.repository.base_ref)}"
                )
                remote_base = self._run_remote_git(
                    [
                        "ls-remote",
                        "--symref",
                        "--exit-code",
                        "--heads",
                        "--end-of-options",
                        request.repository.url,
                        remote_base_ref,
                    ],
                ).stdout.split()
                remote_base_verified = remote_base == [
                    request.manifest.base_sha,
                    remote_base_ref,
                ]
            else:
                remote_verified = True
                remote_base_verified = True
        except (OSError, subprocess.SubprocessError) as exc:
            raise ExactPatchPublicationError(
                "adapter_result_repository_verification_failed"
            ) from exc

        if not (
            local_sha == result.commit_sha
            and bool(separator)
            and parents == [request.manifest.base_sha]
            and tree_headers == [result.tree_sha]
            and message.rstrip("\n") == request.commit_message.rstrip("\n")
            and set(changed_paths) == set(request.changed_paths)
            and committed_patch == request.patch_text
            and head_sha == request.manifest.base_sha
            and self._index_is_clean(root)
            and remote_verified
            and remote_base_verified
        ):
            raise ExactPatchPublicationError("adapter_result_repository_mismatch")

    @staticmethod
    def _run_git(
        sandbox: Path,
        arguments: list[str],
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_SSH_COMMAND": "ssh -F /dev/null -oBatchMode=yes",
            "SSH_ASKPASS_REQUIRE": "never",
            "LC_ALL": "C",
        }
        if os.environ.get("SSH_AUTH_SOCK"):
            environment["SSH_AUTH_SOCK"] = os.environ["SSH_AUTH_SOCK"]
        command = [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "credential.helper=",
            "-c",
            "credential.interactive=never",
            "-c",
            "protocol.ext.allow=never",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "diff.external=",
            "-c",
            "http.extraHeader=",
            "-C",
            str(sandbox),
            *arguments,
        ]
        with ExitStack() as stack:
            git_directory = sandbox / ".git"
            if git_directory.exists() or git_directory.is_symlink():
                if not git_metadata_paths_are_safe(sandbox):
                    raise ExactPatchPublicationError(
                        "sandbox_git_metadata_unsafe"
                    )
                head_path = git_directory / "HEAD"
                index_path = git_directory / "index"
                if (
                    not git_directory.is_dir()
                    or git_directory.is_symlink()
                    or not head_path.is_file()
                    or head_path.is_symlink()
                    or not index_path.is_file()
                    or index_path.is_symlink()
                ):
                    raise ExactPatchPublicationError(
                        "sandbox_git_metadata_unsafe"
                    )
                proxy_root = Path(
                    stack.enter_context(
                        tempfile.TemporaryDirectory(
                            prefix="uca-publication-verifier-git-dir-"
                        )
                    )
                )
                common_path = str(git_directory)
                if "\n" in common_path:
                    raise ExactPatchPublicationError(
                        "sandbox_git_metadata_unsafe"
                    )
                (proxy_root / "commondir").write_text(
                    common_path + "\n",
                    encoding="utf-8",
                )
                (proxy_root / "HEAD").write_bytes(head_path.read_bytes())
                environment["GIT_DIR"] = str(proxy_root)
                environment["GIT_WORK_TREE"] = str(sandbox)
                environment["GIT_INDEX_FILE"] = str(index_path)
            return subprocess.run(
                command,
                check=check,
                capture_output=True,
                text=True,
                timeout=120,
                shell=False,
                env=environment,
            )

    @staticmethod
    def _run_remote_git(arguments: list[str]) -> subprocess.CompletedProcess[str]:
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_SSH_COMMAND": "ssh -F /dev/null -oBatchMode=yes",
            "SSH_ASKPASS_REQUIRE": "never",
            "LC_ALL": "C",
        }
        if os.environ.get("SSH_AUTH_SOCK"):
            environment["SSH_AUTH_SOCK"] = os.environ["SSH_AUTH_SOCK"]
        with tempfile.TemporaryDirectory(
            prefix="uca-publication-verifier-network-"
        ) as temporary_root:
            return subprocess.run(
                [
                    "git",
                    "-c",
                    "credential.helper=",
                    "-c",
                    "credential.interactive=never",
                    "-c",
                    "protocol.ext.allow=never",
                    "-c",
                    "http.extraHeader=",
                    "-C",
                    temporary_root,
                    *arguments,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
                shell=False,
                env=environment,
            )

    def _base_branch_at_sha(self, sandbox: Path, branch: str, base_sha: str) -> bool:
        for reference in (
            f"refs/heads/{branch}",
            f"refs/remotes/origin/{branch}",
        ):
            result = self._run_git(
                sandbox,
                ["rev-parse", "--verify", f"{reference}^{{commit}}"],
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip() == base_sha:
                return True
        return False

    def _require_safe_local_config(self, sandbox: Path) -> None:
        git_dir = sandbox / ".git"
        config_path = git_dir / "config"
        if not git_metadata_paths_are_safe(sandbox):
            raise ExactPatchPublicationError("sandbox_git_metadata_unsafe")
        if (
            not git_dir.is_dir()
            or git_dir.is_symlink()
            or (git_dir / "commondir").exists()
            or (git_dir / "commondir").is_symlink()
            or not config_path.is_file()
            or config_path.is_symlink()
        ):
            raise ExactPatchPublicationError("sandbox_git_config_unavailable")
        result = self._run_git(
            sandbox,
            [
                "config",
                "--file",
                str(config_path),
                "--null",
                "--name-only",
                "--list",
            ],
            check=False,
        )
        if result.returncode != 0:
            raise ExactPatchPublicationError("sandbox_git_config_invalid")
        safe_core = {
            "core.repositoryformatversion",
            "core.filemode",
            "core.bare",
            "core.logallrefupdates",
            "core.ignorecase",
            "core.precomposeunicode",
            "core.symlinks",
        }
        for raw_key in result.stdout.split("\0"):
            key = raw_key.strip().lower()
            if not key:
                continue
            remote_safe = bool(re.fullmatch(r"remote\.origin\.(url|fetch)", key))
            branch_safe = bool(re.fullmatch(r"branch\..+\.(remote|merge)", key))
            if key not in safe_core and not remote_safe and not branch_safe:
                raise ExactPatchPublicationError("sandbox_git_config_unsafe")
        for metadata_path in (git_dir / "info" / "grafts", git_dir / "shallow"):
            if metadata_path.is_symlink() or (
                metadata_path.is_file() and metadata_path.stat().st_size > 0
            ):
                raise ExactPatchPublicationError(
                    "sandbox_git_history_override_forbidden"
                )
        replacements = self._run_git(
            sandbox,
            ["for-each-ref", "--format=%(refname)", "refs/replace"],
            check=False,
        )
        if replacements.returncode != 0 or replacements.stdout.strip():
            raise ExactPatchPublicationError(
                "sandbox_git_history_override_forbidden"
            )

    @staticmethod
    def _effects_indeterminate(effects: PublicationPartialEffects) -> bool:
        return bool(
            (effects.local_ref_attempted and not effects.local_ref_verified)
            or (effects.push_attempted and not effects.push_verified)
            or (effects.draft_pr_attempted and not effects.draft_pr_created)
        )

    @staticmethod
    def _remote_effects_indeterminate(
        action: PublicationAction,
        effects: PublicationPartialEffects,
    ) -> bool:
        if action is PublicationAction.COMMIT:
            return False
        return bool(
            (effects.push_attempted and not effects.push_verified)
            or (
                action is PublicationAction.DRAFT_PR
                and effects.draft_pr_attempted
                and not effects.draft_pr_created
            )
        )

    def _completed_remote_effect_attribution(
        self,
        publication_id: str,
        action: PublicationAction,
        result: SourceControlPublicationResult,
    ) -> tuple[bool, bool | None]:
        """Resolve remote mutation evidence without conflating local-only reuse.

        A retried commit may reuse a local commit or feature ref after a fault that
        happened before any remote operation. That reconciliation is real, but it
        does not make remote effect attribution indeterminate. Only a prior
        unverified push or Draft-PR attempt (or an interruption with no durable
        operation boundary) carries remote uncertainty into the completed receipt.
        """

        if action is PublicationAction.COMMIT:
            return False, False

        prior_push_modified = False
        prior_push_indeterminate = False
        prior_draft_created = False
        prior_draft_indeterminate = False

        for receipt in self.store.attempt_receipts(publication_id):
            status = receipt.get("status")
            if status == "completed":
                continue
            if status == "interrupted":
                prior_push_indeterminate = True
                if action is PublicationAction.DRAFT_PR:
                    prior_draft_indeterminate = True
                continue

            try:
                effects = PublicationPartialEffects.model_validate(
                    receipt.get("partial_effects")
                )
            except (TypeError, ValueError):
                prior_push_indeterminate = True
                if action is PublicationAction.DRAFT_PR:
                    prior_draft_indeterminate = True
                continue

            attribution_trusted = (
                receipt.get("partial_effects_attribution_trusted") is True
            )
            prior_push_modified = prior_push_modified or bool(
                attribution_trusted
                and effects.push_attempted
                and effects.push_verified
            )
            prior_push_indeterminate = prior_push_indeterminate or bool(
                effects.push_attempted and not effects.push_verified
            )
            if action is PublicationAction.DRAFT_PR:
                prior_draft_created = prior_draft_created or bool(
                    attribution_trusted and effects.draft_pr_created
                )
                prior_draft_indeterminate = prior_draft_indeterminate or bool(
                    effects.draft_pr_attempted and not effects.draft_pr_created
                )

            # Result-validation and unexpected failures deliberately set the
            # receipt-level flag even when no typed operation boundary survived.
            # Preserve that fail-closed uncertainty. A sole unverified local-ref
            # CAS is the one encoded uncertainty that cannot have reached remote.
            if (
                receipt.get("effect_attribution_indeterminate") is True
                and not self._remote_effects_indeterminate(action, effects)
            ):
                prior_push_indeterminate = True
                if action is PublicationAction.DRAFT_PR:
                    prior_draft_indeterminate = True

        draft_created = result.draft_pr.created if result.draft_pr is not None else False
        source_repository_modified = bool(
            prior_push_modified
            or prior_draft_created
            or result.push_performed
            or draft_created
        )
        effect_attribution_indeterminate = bool(
            prior_push_indeterminate or prior_draft_indeterminate
        )
        return (
            effect_attribution_indeterminate,
            True
            if source_repository_modified
            else None
            if effect_attribution_indeterminate
            else False,
        )

    @staticmethod
    def _index_is_clean(sandbox: Path) -> bool:
        result = ExactPatchPublicationService._run_git(
            sandbox,
            ["diff", "--cached", "--quiet", "--exit-code"],
            check=False,
        )
        return result.returncode == 0

    @staticmethod
    def _intent_record(request: ExactPublicationRequest) -> dict[str, object]:
        return {
            "publication_id": request.publication_id,
            "task_id": request.task_id,
            "thread_id": request.thread_id,
            "approval_ref": request.approval_ref,
            "approval_sha256": request.approval_sha256,
            "patch_ref": request.patch_ref,
            "patch_sha256": request.patch_sha256,
            "intent_sha256": request.intent_sha256,
            "repository": request.repository.model_dump(mode="json"),
            "base_sha": request.manifest.base_sha,
            "base_ref": request.repository.base_ref,
            "changed_paths": list(request.changed_paths),
            "head_branch": request.head_branch,
            "action": request.action.value,
            "adapter_identity": request.adapter_identity,
            "draft_pr_identity": request.draft_pr_identity,
            "commit_message": request.commit_message,
            "draft_pr_title": request.draft_pr_title,
            "draft_pr_body": request.draft_pr_body,
        }

    def _failure_receipt(
        self,
        request: ExactPublicationRequest,
        code: str,
        stage: str,
        cause_type: str,
        partial_effects: PublicationPartialEffects,
        *,
        side_effects_indeterminate: bool = False,
        remote_effects_indeterminate: bool = False,
        partial_effects_attribution_trusted: bool,
    ) -> dict[str, object]:
        effects = partial_effects.model_dump(mode="json")
        source_repository_modified = bool(
            partial_effects_attribution_trusted
            and (
                (partial_effects.push_attempted and partial_effects.push_verified)
                or partial_effects.draft_pr_created
            )
        )
        return {
            "schema_version": "1",
            "status": "failed",
            "qualified": False,
            **self._intent_record(request),
            "adapter": type(self.adapter).__name__,
            "error": {
                "code": code,
                "stage": stage,
                "cause_type": cause_type[:128],
            },
            "partial_effects": effects,
            "partial_effects_attribution_trusted": (
                partial_effects_attribution_trusted
            ),
            "source_repository_modified": (
                True
                if source_repository_modified
                else None
                if remote_effects_indeterminate
                else False
            ),
            "merge_performed": False,
            "deployment_performed": False,
            "side_effects_indeterminate": side_effects_indeterminate,
            "effect_attribution_indeterminate": remote_effects_indeterminate,
            "retryable": True,
            "reconciliation_required": True,
        }

    def _persist_receipt(
        self,
        task_id: str,
        receipt: dict[str, object],
        *,
        replayed: bool,
        attempts: int,
    ) -> dict[str, Any]:
        attempt_reference = self.artifacts.write_json(
            (f"tasks/{task_id}/source-control-publication-attempt-{attempts:04d}.json"),
            receipt,
        )
        reference = self.artifacts.write_json(
            f"tasks/{task_id}/source-control-publication.json",
            receipt,
        )
        return {
            **receipt,
            "publication_receipt_ref": reference.uri,
            "publication_receipt_sha256": reference.sha256,
            "publication_attempt_ref": attempt_reference.uri,
            "publication_attempt_sha256": attempt_reference.sha256,
            "replayed_receipt": replayed,
            "attempts": attempts,
        }

    def _sync_attempt_artifacts(
        self,
        task_id: str,
        publication_id: str,
        *,
        through_attempt: int,
    ) -> None:
        if through_attempt < 1:
            return
        receipts = self.store.attempt_receipts(publication_id)
        if len(receipts) < through_attempt:
            raise ExactPatchPublicationError("publication_attempt_evidence_missing")
        for attempt, receipt in enumerate(receipts[:through_attempt], start=1):
            self.artifacts.write_json(
                f"tasks/{task_id}/source-control-publication-attempt-{attempt:04d}.json",
                receipt,
            )
