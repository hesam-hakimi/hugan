from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    FileEdit,
    SafeModePolicy,
    SafeTaskRequest,
    StructuredEditProposal,
    TestProfile,
    TextReplacement,
)
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.source_control.base import (
    ExactPublicationRequest,
    PublicationAction,
    SourceControlAdapter,
    SourceControlCapabilities,
    SourceControlPublicationError,
    SourceControlPublicationResult,
    validate_base_branch,
    validate_head_branch,
)
from universal_coding_agent.source_control.github import (
    GITHUB_REPOSITORY_ENV,
    GITHUB_TOKEN_ENV,
    GitHubDraftPullRequestError,
    create_adapter,
)
from universal_coding_agent.source_control.publication import (
    ExactPatchPublicationError,
    ExactPatchPublicationService,
)

_TASK_ID = "pretransfer-github-publication-live"
_SUMMARY_NAME = "github-publication-live-summary.json"
_FIXTURE_PATH = "universal-coding-agent/qualification/github-live-fixture.txt"
_FIXTURE_BEFORE = "UCA_GITHUB_LIVE_QUALIFICATION_FIXTURE=v1\n"
_FIXTURE_AFTER = "UCA_GITHUB_LIVE_QUALIFICATION_FIXTURE=v2\n"
_HEAD_PREFIX = "uca/github-live-qualification-"
_SHA = re.compile(r"^[0-9a-f]{40}$")
_GITHUB_SSH_URL = re.compile(
    r"^git@github\.com:(?P<owner>[A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/"
    r"(?P<repo>[A-Za-z0-9_.-]{1,100})\.git$"
)

AdapterFactory = Callable[[], SourceControlAdapter]


@dataclass(frozen=True)
class GitHubPublicationLiveConfig:
    state_root: Path
    source_root: Path
    repository_url: str
    base_branch: str
    base_sha: str
    head_branch: str


@dataclass
class _RecordingAdapter:
    delegate: SourceControlAdapter
    calls: list[ExactPublicationRequest] = field(default_factory=list)

    def capabilities(self) -> SourceControlCapabilities:
        return self.delegate.capabilities()

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        self.calls.append(request)
        return self.delegate.publish_exact(request)


def run_github_publication_live(
    config: GitHubPublicationLiveConfig,
    *,
    adapter_factory: AdapterFactory = create_adapter,
    allow_local_sources: bool = False,
    secret_values: Iterable[str] = (),
) -> dict[str, Any]:
    """Qualify exact GitHub feature-ref push and Draft-PR publication.

    The qualification intentionally leaves the isolated feature ref and Draft PR in place as
    durable evidence. It has no merge, deployment, tag, base-update, history-rewrite, or ref-
    deletion authority.
    """

    state_root = config.state_root.expanduser().resolve()
    secrets = tuple(value for value in secret_values if value)
    try:
        normalized = _validate_config(config, allow_local_sources=allow_local_sources)
        state_root.mkdir(parents=True, exist_ok=True)
        initial_entries = list(state_root.iterdir())
        if any(
            entry.name != "console.log"
            or not entry.is_file()
            or entry.is_symlink()
            or entry.stat().st_size != 0
            for entry in initial_entries
        ):
            raise RuntimeError("qualification state root must be empty")

        source_before = _source_snapshot(normalized.source_root)
        if source_before["status"]:
            raise RuntimeError("qualification source checkout must be clean")
        if source_before["head_sha"] != normalized.base_sha:
            raise RuntimeError("qualification source HEAD does not match the approved base SHA")

        refs_before = _remote_refs(
            normalized.repository_url,
            allow_local=allow_local_sources,
        )
        base_ref = f"refs/heads/{normalized.base_branch}"
        head_ref = f"refs/heads/{normalized.head_branch}"
        if refs_before.get(base_ref) != normalized.base_sha:
            raise RuntimeError("remote base ref does not match the approved base SHA")
        if head_ref in refs_before:
            raise RuntimeError("qualification head ref already exists")

        approval_sha256, patch_sha256 = _prepare_exact_approval(
            normalized,
            allow_local_sources=allow_local_sources,
        )
        first_adapter = _RecordingAdapter(adapter_factory())
        publisher = ExactPatchPublicationService(state_root, first_adapter)
        try:
            first_receipt = publisher.publish_exact(
                _TASK_ID,
                approval_sha256=approval_sha256,
                patch_sha256=patch_sha256,
                action=PublicationAction.DRAFT_PR,
                head_branch=normalized.head_branch,
            )
        finally:
            publisher.close()
        if len(first_adapter.calls) != 1:
            raise RuntimeError("first publication did not invoke exactly one adapter")
        exact_request = first_adapter.calls[0]
        first_result = _qualified_first_result(first_receipt, normalized)

        direct_replay = adapter_factory().publish_exact(exact_request)

        restart_adapter = _RecordingAdapter(adapter_factory())
        restarted = ExactPatchPublicationService(state_root, restart_adapter)
        try:
            durable_replay = restarted.publish_exact(
                _TASK_ID,
                approval_sha256=approval_sha256,
                patch_sha256=patch_sha256,
                action=PublicationAction.DRAFT_PR,
                head_branch=normalized.head_branch,
            )
        finally:
            restarted.close()

        refs_after = _remote_refs(
            normalized.repository_url,
            allow_local=allow_local_sources,
        )
        source_after = _source_snapshot(normalized.source_root)
        _require_direct_replay(direct_replay, first_result, normalized)
        _require_durable_replay(
            durable_replay,
            first_receipt,
            restart_adapter,
        )
        ref_evidence = _require_isolated_remote_delta(
            refs_before,
            refs_after,
            base_ref=base_ref,
            base_sha=normalized.base_sha,
            head_ref=head_ref,
            head_sha=first_result["commit_sha"],
        )
        commit_evidence = _commit_evidence(exact_request, first_result)
        source_preserved = source_before == source_after and not source_after["status"]
        if not source_preserved:
            raise RuntimeError("qualification source checkout changed")
        if _state_contains_secret(state_root, secrets):
            raise RuntimeError("credential material was persisted in qualification state")

        summary = {
            "transport": "github_exact_draft_pr",
            "qualified": True,
            "repository": _repository_label(normalized.repository_url),
            "base_branch": normalized.base_branch,
            "base_sha": normalized.base_sha,
            "head_branch": normalized.head_branch,
            "head_sha": first_result["commit_sha"],
            "first_publication": _receipt_evidence(first_receipt),
            "adapter_replay": _result_evidence(direct_replay),
            "durable_restart_replay": _receipt_evidence(durable_replay),
            "commit": commit_evidence,
            "remote_refs": ref_evidence,
            "source": {
                "head_sha": source_after["head_sha"],
                "tree_sha": source_after["tree_sha"],
                "source_preserved": source_preserved,
            },
            "credential_redaction": {
                "state_files_scanned": True,
                "credential_material_absent": True,
            },
            "forbidden_effects": {
                "merge_performed": False,
                "deployment_performed": False,
                "base_branch_updated": False,
                "history_rewritten": False,
                "ref_deleted": False,
                "tag_created": False,
            },
        }
        _write_summary(state_root, summary)
        if _state_contains_secret(state_root, secrets):
            raise RuntimeError("credential material was persisted in qualification summary")
        return summary
    except Exception as exc:
        failure_root_is_safe = _paths_do_not_overlap(
            state_root,
            config.source_root.expanduser().resolve(),
        )
        summary = {
            "transport": "github_exact_draft_pr",
            "qualified": False,
            "failure": _redacted_failure(exc),
            "credential_redaction": {
                "state_files_scanned": state_root.exists() and failure_root_is_safe,
                "credential_material_absent": (
                    not _state_contains_secret(state_root, secrets)
                    if state_root.exists() and failure_root_is_safe
                    else True
                ),
            },
            "forbidden_effects_claimed": False,
        }
        if failure_root_is_safe:
            state_root.mkdir(parents=True, exist_ok=True)
            _write_summary(state_root, summary)
        return summary


def _validate_config(
    config: GitHubPublicationLiveConfig,
    *,
    allow_local_sources: bool,
) -> GitHubPublicationLiveConfig:
    state_root = config.state_root.expanduser().resolve()
    source_root = config.source_root.expanduser().resolve()
    if not source_root.is_dir():
        raise ValueError("qualification source root is unavailable")
    if not _paths_do_not_overlap(state_root, source_root):
        raise ValueError("qualification state root must be outside the source checkout")
    base_branch = validate_base_branch(config.base_branch)
    head_branch = validate_head_branch(config.head_branch)
    base_sha = config.base_sha.strip().lower()
    if _SHA.fullmatch(base_sha) is None:
        raise ValueError("GitHub live qualification requires an exact 40-character SHA")
    if head_branch == base_branch or not head_branch.startswith(_HEAD_PREFIX):
        raise ValueError("qualification head branch must use the isolated live prefix")

    repository_url = config.repository_url.strip()
    if allow_local_sources:
        local_repository = Path(repository_url).expanduser().resolve()
        if not local_repository.exists():
            raise ValueError("local qualification repository is unavailable")
        repository_url = str(local_repository)
    else:
        match = _GITHUB_SSH_URL.fullmatch(repository_url)
        if match is None:
            raise ValueError("live qualification requires a credential-free GitHub SSH URL")
        expected_repository = os.getenv(GITHUB_REPOSITORY_ENV, "").strip().casefold()
        actual_repository = f"{match.group('owner')}/{match.group('repo')}".casefold()
        if not expected_repository or actual_repository != expected_repository:
            raise ValueError("GitHub repository identity does not match the SSH URL")
        if not os.getenv("SSH_AUTH_SOCK", "").strip():
            raise ValueError("live qualification requires a host-owned SSH agent")

    return GitHubPublicationLiveConfig(
        state_root=state_root,
        source_root=source_root,
        repository_url=repository_url,
        base_branch=base_branch,
        base_sha=base_sha,
        head_branch=head_branch,
    )


def _prepare_exact_approval(
    config: GitHubPublicationLiveConfig,
    *,
    allow_local_sources: bool,
) -> tuple[str, str]:
    def implementer(_request) -> dict[str, Any]:
        return StructuredEditProposal(
            summary="Advance only the dedicated GitHub live-qualification fixture.",
            edits=(
                FileEdit(
                    path=_FIXTURE_PATH,
                    operation=ChangeOperation.MODIFY,
                    replacements=(
                        TextReplacement(
                            old_text=_FIXTURE_BEFORE,
                            new_text=_FIXTURE_AFTER,
                        ),
                    ),
                ),
            ),
            requested_test_profiles=("github-live-fixture-check",),
        ).model_dump(mode="json")

    manifest = ApprovedChangeManifest(
        base_sha=config.base_sha,
        plan_hash="c" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path=_FIXTURE_PATH,
                operation=ChangeOperation.MODIFY,
                purpose="Create a harmless, isolated hosted-publication qualification commit.",
            ),
        ),
        test_profiles=("github-live-fixture-check",),
        acceptance_criteria=("The dedicated qualification fixture advances exactly to v2.",),
        max_changed_files=1,
    )
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="github-live-fixture-check",
                argv=(
                    sys.executable,
                    "-c",
                    (
                        "from pathlib import Path; "
                        f"assert Path({_FIXTURE_PATH!r}).read_text() == {_FIXTURE_AFTER!r}"
                    ),
                ),
                timeout_seconds=30,
            ),
        )
    )
    task = SafeTaskRequest(
        task_id=_TASK_ID,
        thread_id=_TASK_ID,
        title="Live GitHub exact Draft-PR qualification",
        objective="Publish only the approved qualification fixture change as a Draft PR.",
        repository=RepositorySpec(
            url=config.repository_url,
            base_ref=config.base_branch,
        ),
        manifest=manifest,
        policy=policy,
        require_publish_approval=True,
    )
    service = SafeAgentService.create(
        config.state_root,
        FakeModelProvider(handlers={"implementer": implementer}),
        allow_local_sources=allow_local_sources,
    )
    try:
        service.run(task)
        pending = service.resume(task.thread_id, True)
        validation = service.artifacts.read_json(pending["patch_validation_ref"])
        patch_sha256 = str(validation["patch_sha256"])
        final = service.resume_publish(
            task.thread_id,
            approved=True,
            patch_sha256=patch_sha256,
        )
        report = service.artifacts.read_json(final["final_report_ref"])
        if final.get("status") != "completed" or report.get("publish_approved") is not True:
            raise RuntimeError("safe qualification change did not reach publish approval")
        return str(report["publish_approval_sha256"]), patch_sha256
    finally:
        service.close()


def _qualified_first_result(
    receipt: Mapping[str, Any],
    config: GitHubPublicationLiveConfig,
) -> dict[str, Any]:
    result = receipt.get("result")
    draft = result.get("draft_pr") if isinstance(result, dict) else None
    exact = bool(
        receipt.get("status") == "completed"
        and receipt.get("qualified") is True
        and receipt.get("replayed_receipt") is False
        and receipt.get("action") == PublicationAction.DRAFT_PR.value
        and receipt.get("merge_performed") is False
        and receipt.get("deployment_performed") is False
        and isinstance(result, dict)
        and result.get("commit_created") is True
        and result.get("local_ref_created") is True
        and result.get("pushed") is True
        and result.get("push_performed") is True
        and result.get("reused") is False
        and isinstance(draft, dict)
        and draft.get("draft") is True
        and draft.get("created") is True
        and draft.get("base_branch") == config.base_branch
        and draft.get("base_sha") == config.base_sha
        and draft.get("head_branch") == config.head_branch
        and draft.get("head_sha") == result.get("commit_sha")
    )
    if not exact:
        raise RuntimeError("first hosted publication did not produce the exact Draft PR")
    return result


def _require_direct_replay(
    replay: SourceControlPublicationResult,
    first_result: Mapping[str, Any],
    config: GitHubPublicationLiveConfig,
) -> None:
    draft = replay.draft_pr
    if not (
        replay.commit_sha == first_result.get("commit_sha")
        and replay.tree_sha == first_result.get("tree_sha")
        and replay.commit_created is False
        and replay.local_ref_created is False
        and replay.local_ref_updated is False
        and replay.pushed is True
        and replay.push_performed is False
        and replay.remote_before_sha == replay.commit_sha
        and replay.remote_after_sha == replay.commit_sha
        and replay.reused is True
        and draft is not None
        and draft.draft is True
        and draft.created is False
        and draft.base_branch == config.base_branch
        and draft.base_sha == config.base_sha
        and draft.head_branch == config.head_branch
        and draft.head_sha == replay.commit_sha
    ):
        raise RuntimeError("provider-level hosted publication replay was not idempotent")


def _require_durable_replay(
    replay: Mapping[str, Any],
    first: Mapping[str, Any],
    adapter: _RecordingAdapter,
) -> None:
    if not (
        replay.get("status") == "completed"
        and replay.get("qualified") is True
        and replay.get("replayed_receipt") is True
        and replay.get("publication_receipt_sha256")
        == first.get("publication_receipt_sha256")
        and replay.get("result") == first.get("result")
        and not adapter.calls
    ):
        raise RuntimeError("durable hosted publication replay was not exact")


def _require_isolated_remote_delta(
    before: Mapping[str, str],
    after: Mapping[str, str],
    *,
    base_ref: str,
    base_sha: str,
    head_ref: str,
    head_sha: str,
) -> dict[str, Any]:
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(ref for ref in set(before) & set(after) if before[ref] != after[ref])
    before_tags = {ref: sha for ref, sha in before.items() if ref.startswith("refs/tags/")}
    after_tags = {ref: sha for ref, sha in after.items() if ref.startswith("refs/tags/")}
    if not (
        added == [head_ref]
        and not removed
        and not changed
        and before.get(base_ref) == base_sha
        and after.get(base_ref) == base_sha
        and after.get(head_ref) == head_sha
        and before_tags == after_tags
    ):
        raise RuntimeError("hosted publication changed refs outside the isolated head")
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "base_preserved": True,
        "tags_preserved": True,
        "only_expected_head_added": True,
    }


def _commit_evidence(
    request: ExactPublicationRequest,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    sandbox = Path(request.sandbox_path)
    commit_sha = str(result["commit_sha"])
    tree_sha = str(result["tree_sha"])
    parent_row = _git_readonly(sandbox, "rev-list", "--parents", "-n", "1", commit_sha)
    actual_tree = _git_readonly(sandbox, "rev-parse", f"{commit_sha}^{{tree}}")
    changed_paths = tuple(
        _git_readonly(
            sandbox,
            "diff",
            "--name-only",
            request.manifest.base_sha,
            commit_sha,
        ).splitlines()
    )
    if not (
        parent_row == f"{commit_sha} {request.manifest.base_sha}"
        and actual_tree == tree_sha
        and changed_paths == (_FIXTURE_PATH,)
    ):
        raise RuntimeError("published commit evidence does not match the approved patch")
    return {
        "commit_sha": commit_sha,
        "tree_sha": tree_sha,
        "parent_sha": request.manifest.base_sha,
        "changed_paths": list(changed_paths),
        "patch_sha256": request.patch_sha256,
        "approval_sha256": request.approval_sha256,
        "exact_binding_verified": True,
    }


def _receipt_evidence(receipt: Mapping[str, Any]) -> dict[str, Any]:
    result = receipt.get("result")
    return {
        "status": receipt.get("status"),
        "qualified": receipt.get("qualified"),
        "replayed_receipt": receipt.get("replayed_receipt"),
        "attempts": receipt.get("attempts"),
        "publication_id": receipt.get("publication_id"),
        "publication_receipt_sha256": receipt.get("publication_receipt_sha256"),
        "result": _result_evidence(result) if isinstance(result, dict) else None,
    }


def _result_evidence(result: SourceControlPublicationResult | Mapping[str, Any]) -> dict[str, Any]:
    payload = (
        result.model_dump(mode="json")
        if isinstance(result, SourceControlPublicationResult)
        else dict(result)
    )
    draft = payload.get("draft_pr")
    return {
        "commit_sha": payload.get("commit_sha"),
        "tree_sha": payload.get("tree_sha"),
        "commit_created": payload.get("commit_created"),
        "local_ref_created": payload.get("local_ref_created"),
        "local_ref_updated": payload.get("local_ref_updated"),
        "pushed": payload.get("pushed"),
        "push_performed": payload.get("push_performed"),
        "reused": payload.get("reused"),
        "draft_pr": (
            {
                "pull_request_id": draft.get("pull_request_id"),
                "url": draft.get("url"),
                "draft": draft.get("draft"),
                "base_branch": draft.get("base_branch"),
                "base_sha": draft.get("base_sha"),
                "head_branch": draft.get("head_branch"),
                "head_sha": draft.get("head_sha"),
                "created": draft.get("created"),
            }
            if isinstance(draft, dict)
            else None
        ),
    }


def _source_snapshot(root: Path) -> dict[str, str]:
    return {
        "head_sha": _git_readonly(root, "rev-parse", "HEAD"),
        "tree_sha": _git_readonly(root, "rev-parse", "HEAD^{tree}"),
        "status": _git_readonly(root, "status", "--porcelain"),
    }


def _remote_refs(repository_url: str, *, allow_local: bool) -> dict[str, str]:
    if not allow_local and _GITHUB_SSH_URL.fullmatch(repository_url) is None:
        raise ValueError("remote snapshot requires the approved GitHub SSH URL")
    with tempfile.TemporaryDirectory(prefix="uca-github-live-refs-") as temporary:
        root = Path(temporary)
        _run_git_network(root, "init", "--bare", ".")
        output = _run_git_network(
            root,
            "ls-remote",
            "--refs",
            "--heads",
            "--tags",
            repository_url,
        )
    refs: dict[str, str] = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) != 2 or _SHA.fullmatch(fields[0]) is None:
            raise RuntimeError("remote ref snapshot response is invalid")
        if fields[1] in refs:
            raise RuntimeError("remote ref snapshot contains a duplicate")
        refs[fields[1]] = fields[0]
    return refs


def _run_git_network(cwd: Path, *arguments: str) -> str:
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
        "http.extraHeader=",
        *arguments,
    ]
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if completed.returncode != 0:
        raise RuntimeError("credential-isolated Git remote inspection failed")
    return completed.stdout.strip()


def _git_readonly(cwd: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if completed.returncode != 0:
        raise RuntimeError("read-only Git qualification check failed")
    return completed.stdout.strip()


def _state_contains_secret(root: Path, secrets: tuple[str, ...]) -> bool:
    encoded = tuple(secret.encode("utf-8") for secret in secrets if secret)
    if not encoded or not root.exists():
        return False
    overlap_length = max(len(secret) for secret in encoded) - 1
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        with path.open("rb") as handle:
            overlap = b""
            while chunk := handle.read(64 * 1024):
                window = overlap + chunk
                if any(secret in window for secret in encoded):
                    return True
                overlap = window[-overlap_length:] if overlap_length else b""
    return False


def _paths_do_not_overlap(first: Path, second: Path) -> bool:
    first = first.resolve()
    second = second.resolve()
    return bool(
        first != second
        and first not in second.parents
        and second not in first.parents
    )


def _repository_label(repository_url: str) -> str:
    match = _GITHUB_SSH_URL.fullmatch(repository_url)
    if match is not None:
        return f"{match.group('owner')}/{match.group('repo')}"
    return "local-qualification-repository"


def _redacted_failure(exc: Exception) -> dict[str, str]:
    failure = {"type": type(exc).__name__}
    if isinstance(exc, (ExactPatchPublicationError, SourceControlPublicationError)):
        failure["code"] = exc.code
    if isinstance(exc, (GitHubDraftPullRequestError, SourceControlPublicationError)):
        failure["stage"] = exc.stage
    if isinstance(exc, SourceControlPublicationError) and exc.cause_type:
        failure["cause_type"] = exc.cause_type
    return failure


def _write_summary(state_root: Path, summary: Mapping[str, Any]) -> None:
    (state_root / _SUMMARY_NAME).write_text(
        json.dumps(dict(summary), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--repository-url", required=True)
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-branch", required=True)
    arguments = parser.parse_args()

    token = os.getenv(GITHUB_TOKEN_ENV, "")
    config = GitHubPublicationLiveConfig(
        state_root=arguments.state_root,
        source_root=arguments.source_root,
        repository_url=arguments.repository_url,
        base_branch=arguments.base_branch,
        base_sha=arguments.base_sha,
        head_branch=arguments.head_branch,
    )
    summary = run_github_publication_live(
        config,
        secret_values=(token,),
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))
    if not summary["qualified"]:
        raise SystemExit("GITHUB_PUBLICATION_LIVE_FAILED")
    print("GITHUB_PUBLICATION_LIVE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
