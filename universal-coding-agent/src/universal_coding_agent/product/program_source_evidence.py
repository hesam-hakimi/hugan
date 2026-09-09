"""Admission of actual checkpoint-bound Safe evidence; never execute another task."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from universal_coding_agent.core.safe_models import (
    PatchProposal,
    PatchValidationResult,
    SafeModePolicy,
    SafeReviewResult,
    SafeTaskRequest,
    StructuredEditProposal,
    TestExecutionResult,
)
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService,
)
from universal_coding_agent.product.program_source_patch import verified_patch_edits
from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceEdit,
    ProgramSourceSnapshot,
    _canonical,
    _hash,
    _require,
)
from universal_coding_agent.storage.artifacts import ArtifactStore

MAX_EVIDENCE_BYTES = 16_000_000


def strict_json(raw: bytes) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, "duplicate evidence JSON key")
            result[key] = value
        return result

    def constant(_value):
        raise ValueError("non-finite evidence JSON value")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


@dataclass(frozen=True)
class SafeSourceEvidence:
    payload: bytes
    edits: tuple[ProgramSourceEdit, ...]
    allowed_paths: tuple[str, ...]


def capture_safe_source_evidence(
    *, state: dict, before: ProgramSourceSnapshot, artifacts: ArtifactStore,
    repository_url: str, policy: SafeModePolicy,
    attestor: ProgramGitSourceAttestationService,
) -> SafeSourceEvidence:
    """Only call with values deserialized from the host's real completed checkpoint."""
    task = SafeTaskRequest.model_validate(state["task"])
    _require(task.repository.url == repository_url and task.policy == policy,
             "Safe request repository or trusted policy differs")
    _require(bool(policy.profiles)
             and set(task.manifest.test_profiles) == set(policy.profile_map()),
             "source acceptance requires every host policy profile")
    _require(state.get("status") == "completed" and not state.get("safe_errors")
             and state.get("rolled_back") is False and not state.get("rollback_ref")
             and state.get("scope_approved") is True and state.get("patch_applied") is True
             and state.get("reviewer_verdict") == "PASS", "Safe checkpoint is not qualified")
    _require(not task.require_publish_approval or state.get("publish_approved") is True,
             "required publication decision is missing or rejected")
    _require(state.get("base_sha") == task.manifest.base_sha
             and state.get("scope_hash") == task.manifest.canonical_hash()
             and state.get("sandbox_id") == task.task_id, "Safe source binding differs")
    sandbox = artifacts.root.parent / "sandboxes" / task.task_id / "repo"
    _require(Path(state["sandbox_path"]) == sandbox and sandbox.resolve() == sandbox,
             "Safe sandbox is not the exact host-owned task directory")
    return _capture_at_owned_destination(
        state=state, before=before, artifacts=artifacts, repository_url=repository_url,
        policy=policy, attestor=attestor, sandbox=sandbox)


def _capture_at_owned_destination(
    *, state, before, artifacts, repository_url, policy, attestor, sandbox,
):
    """Private common evidence verifier; callers must prove destination authority."""
    task = SafeTaskRequest.model_validate(state["task"])
    _require(task.repository.url == repository_url and task.policy == policy,
             "Safe request repository or trusted policy differs")
    _require(bool(policy.profiles)
             and set(task.manifest.test_profiles) == set(policy.profile_map()),
             "source acceptance requires every host policy profile")
    _require(state.get("status") == "completed" and not state.get("safe_errors")
             and state.get("rolled_back") is False and not state.get("rollback_ref")
             and state.get("scope_approved") is True and state.get("patch_applied") is True
             and state.get("reviewer_verdict") == "PASS", "Safe checkpoint is not qualified")
    _require(not task.require_publish_approval or state.get("publish_approved") is True,
             "required publication decision is missing or rejected")
    _require(state.get("base_sha") == task.manifest.base_sha
             and state.get("scope_hash") == task.manifest.canonical_hash()
             and state.get("sandbox_id") == task.task_id, "Safe source binding differs")
    captured: list[dict] = []
    size = 0

    def read(key: str, filename: str, digest: str | None = None, *, binary=False):
        nonlocal size
        uri = f"artifact://tasks/{task.task_id}/{filename}"
        _require(state.get(key) == uri, "evidence is not owned by the exact Safe task")
        raw = artifacts._read_bytes_bounded(uri, max_bytes=MAX_EVIDENCE_BYTES - size)
        size += len(raw)
        sha = _hash(raw)
        _require(digest is None or sha == digest, "checkpoint-bound evidence hash differs")
        captured.append({"ref": uri, "sha256": sha,
                         "content_base64": base64.b64encode(raw).decode("ascii")})
        return raw if binary else strict_json(raw)

    scope = read("scope_ref", "approved-change-manifest.json")
    _require(scope == task.manifest.model_dump(mode="json"), "approved scope differs")
    approval = read("scope_approval_ref", "scope-approval.json")
    _require(approval == {"approved": True, "scope_hash": state["scope_hash"],
                          "base_sha": state["base_sha"], "plan_hash": task.manifest.plan_hash},
             "scope approval binding differs")
    tests = read("tests_ref", "test-results.json", state.get("tests_sha256", ""))
    patch = read("patch_ref", "proposed.patch", tests.get("patch_sha256", ""), binary=True)
    proposal = PatchProposal.model_validate(read("patch_proposal_ref", "patch-proposal.json"))
    validation = PatchValidationResult.model_validate(
        read("patch_validation_ref", "patch-validation.json"))
    _require(proposal.unified_diff.encode("utf-8") == patch and validation.valid
             and not validation.errors and validation.patch_sha256 == _hash(patch)
             and set(validation.changed_paths) == set(proposal.changed_paths),
             "canonical patch validation differs")
    _require(tests.get("scope_intact") is True
             and tests.get("policy_sha256") == _hash(policy.model_dump_json().encode())
             and set(tests.get("actual_changed_paths", [])) == set(proposal.changed_paths),
             "trusted test source/policy binding differs")
    outcomes = tuple(TestExecutionResult.model_validate(item) for item in tests["results"])
    _require(tuple(item.profile_id for item in outcomes) == task.manifest.test_profiles
             and all(item.passed and item.returncode == 0 for item in outcomes),
             "required trusted profiles did not all pass")
    review = SafeReviewResult.model_validate(
        read("review_ref", "safe-review.json", state.get("review_sha256", "")))
    _require(review.verdict.value == "PASS" and not review.required_actions,
             "independent Safe review has unresolved findings")
    provenance = read("review_provenance_ref", "safe-review-provenance.json",
                      state.get("review_provenance_sha256", ""))
    expected = {"schema_version": "1", "task_id": task.task_id, "thread_id": task.thread_id,
                "base_sha": task.manifest.base_sha, "scope_hash": state["scope_hash"],
                "patch_sha256": _hash(patch), "tests_sha256": state["tests_sha256"],
                "review_sha256": state["review_sha256"], "reviewer_role": "reviewer",
                "independent_context": True,
                "reviewer_context_ref": state.get("reviewer_context_ref"),
                "reviewer_validation_ref": state.get("reviewer_validation_ref")}
    _require(all(provenance.get(key) == value for key, value in expected.items()),
             "separate reviewer provenance differs")
    context = read("reviewer_context_ref", "safe-reviewer-context.md",
                   provenance.get("reviewer_context_sha256", ""), binary=True)
    _require(bool(context.strip()), "independent reviewer context is missing")
    diagnostics = read("reviewer_validation_ref", "safe-reviewer-model-validation.json",
                       provenance.get("reviewer_validation_sha256", ""))
    _require(diagnostics.get("role") == "reviewer" and diagnostics.get("attempts")
             and diagnostics["attempts"][-1].get("schema_valid") is True,
             "independent reviewer did not produce validated output")
    report = read("final_report_ref", "safe-final-report.json")
    report_expected = {"task_id": task.task_id, "thread_id": task.thread_id,
                       "repository": task.repository.model_dump(mode="json"),
                       "plan_hash": task.manifest.plan_hash, "status": "completed",
                       "sandbox_patch_retained": True, "rolled_back": False,
                       "rollback_ref": None, "safe_errors": [], "scope_approved": True,
                       "source_repository_modified": False,
                       "stage_commit_push_pr_merge_deploy": False,
                       "model_authored_patch": False, "canonical_patch_generated_by": "git",
                       "approved_changed_paths": tests["actual_changed_paths"],
                       "publish_approval_required": task.require_publish_approval}
    for key in ("base_sha", "scope_hash", "sandbox_id", "scope_ref", "scope_approval_ref",
                "edit_proposal_ref",
                "patch_ref", "patch_proposal_ref", "patch_validation_ref", "tests_ref",
                "tests_sha256", "review_ref", "review_sha256", "review_provenance_ref",
                "review_provenance_sha256", "reviewer_context_ref", "reviewer_validation_ref",
                "reviewer_verdict", "publish_approved"):
        report_expected[key] = state.get(key)
    _require(all(key in report and report[key] == value
                 for key, value in report_expected.items()), "Safe final report differs")

    # These are read-only checks of the already owned Safe execution; they never stage source.
    edit_name = ("edit-proposal-repaired.json" if state.get("edit_repair_used")
                 else "edit-proposal.json")
    edits = StructuredEditProposal.model_validate(read("edit_proposal_ref", edit_name))
    execution_attestor = ProgramGitSourceAttestationService(
        sandbox, attestor.repository_sha256, source_policy=attestor.source.policy,
        git_policy=attestor.policy)
    execution_attestor.verify_retained_patch(task.manifest, edits, patch)
    execution = execution_attestor.attest_execution_base(before.identity, task.manifest.base_sha)
    _require(execution.snapshot.files == before.files,
             "Safe execution Base is not the complete current cumulative source")
    replacements = verified_patch_edits(before, patch, task.manifest, attestor.source.policy)
    retained = {item.path: item for item in before.files}
    retained.update((edit.path, edit.replacement) for edit in replacements)
    execution_attestor.verify_retained_files(tuple(retained[path] for path in sorted(retained)))
    payload = _canonical({"schema": "uca-safe-source-evidence-1",
                          "task": task.model_dump(mode="json"),
                          "execution_base": strict_json(execution.receipt_bytes()),
                          "artifacts": captured})
    _require(len(payload) <= attestor.source.policy.max_artifact_bytes,
             "source evidence exceeds immutable artifact policy")
    return SafeSourceEvidence(payload, replacements,
                              tuple(sorted(task.manifest.allowed_path_map())))
