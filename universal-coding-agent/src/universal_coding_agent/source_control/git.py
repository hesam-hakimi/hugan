from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
import urllib.parse
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path

from universal_coding_agent.core.safe_models import PatchProposal
from universal_coding_agent.safe.patching import SafePatchEngine
from universal_coding_agent.source_control.base import (
    DraftPullRequestCreator,
    DraftPullRequestRequest,
    DraftPullRequestResult,
    ExactPublicationRequest,
    PublicationAction,
    PublicationPartialEffects,
    SourceControlCapabilities,
    SourceControlPublicationError,
    SourceControlPublicationResult,
    validate_base_branch,
)
from universal_coding_agent.source_control.git_metadata import (
    git_metadata_paths_are_safe,
)

_SHA = re.compile(r"^[0-9a-f]{40,64}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,255}$")


@dataclass(frozen=True)
class _CommandResult:
    returncode: int
    stdout: str
    stderr: str


class _GitCommandError(RuntimeError):
    pass


class GitSourceControlAdapter:
    """Publish one exact patch through a fixed, lease-guarded Git workflow."""

    def __init__(
        self,
        *,
        git_binary: str = "git",
        timeout_seconds: int = 300,
        allow_local_repositories: bool = False,
        draft_pr_creator: DraftPullRequestCreator | None = None,
        adapter_identity: str = "git-source-control-v1",
        draft_pr_identity: str = "",
        committer_name: str = "Universal Coding Agent",
        committer_email: str = "uca@localhost.invalid",
    ) -> None:
        if not git_binary or any(ord(character) < 32 for character in git_binary):
            raise ValueError("git binary is invalid")
        if timeout_seconds < 1 or timeout_seconds > 1800:
            raise ValueError("source-control timeout must be between 1 and 1800 seconds")
        if not committer_name.strip() or "\x00" in committer_name:
            raise ValueError("committer name is invalid")
        if not committer_email.strip() or "\x00" in committer_email:
            raise ValueError("committer email is invalid")
        if draft_pr_creator is not None and not isinstance(
            draft_pr_creator, DraftPullRequestCreator
        ):
            raise TypeError("draft PR creator is incompatible")
        if _IDENTITY.fullmatch(adapter_identity.strip()) is None:
            raise ValueError("adapter identity is invalid")
        if draft_pr_creator is not None and (
            _IDENTITY.fullmatch(draft_pr_identity.strip()) is None
        ):
            raise ValueError("Draft PR creator requires a stable identity")
        if draft_pr_creator is None and draft_pr_identity:
            raise ValueError("Draft PR identity requires a Draft PR creator")
        self.git_binary = git_binary
        self.timeout_seconds = timeout_seconds
        self.allow_local_repositories = allow_local_repositories
        self.draft_pr_creator = draft_pr_creator
        self.adapter_identity = adapter_identity.strip()
        self.draft_pr_identity = draft_pr_identity.strip()
        self.committer_name = committer_name.strip()
        self.committer_email = committer_email.strip()
        self.patch_engine = SafePatchEngine(
            git_binary=git_binary,
            timeout_seconds=timeout_seconds,
        )

    def capabilities(self) -> SourceControlCapabilities:
        return SourceControlCapabilities(
            adapter_identity=self.adapter_identity,
            draft_pr_identity=self.draft_pr_identity,
            commit=True,
            push=True,
            draft_pr=self.draft_pr_creator is not None,
        )

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        if not isinstance(request, ExactPublicationRequest):
            raise TypeError("publish_exact requires an ExactPublicationRequest")

        partial = PublicationPartialEffects()
        stage = "capability_preflight"
        base_sha = request.manifest.base_sha
        draft_pr_creator = self.draft_pr_creator
        try:
            if request.action is PublicationAction.DRAFT_PR and draft_pr_creator is None:
                self._fail("draft_pr_capability_unavailable", stage, partial)
            expected_draft_identity = (
                self.draft_pr_identity
                if request.action is PublicationAction.DRAFT_PR
                else ""
            )
            if (
                request.adapter_identity != self.adapter_identity
                or request.draft_pr_identity != expected_draft_identity
            ):
                self._fail("adapter_identity_mismatch", stage, partial)

            stage = "sandbox_preflight"
            root = self._contained_sandbox(request)
            repository_url = self._normalize_repository_url(request.repository.url)
            self._require_safe_local_config(root)
            self._require_git_repository(root)
            self._require_head(root, base_sha)
            self._require_clean_index(root)
            base_branch = validate_base_branch(request.repository.base_ref)
            self._require_base_branch(root, base_branch, base_sha)
            self._require_valid_head_ref(root, request.head_branch)
            if request.action is not PublicationAction.COMMIT:
                remote_base_ref = f"refs/heads/{base_branch}"
                if self._remote_ref_sha(root, repository_url, remote_base_ref) != base_sha:
                    self._fail("remote_base_ref_drift", stage, partial)
                remote_head_ref = f"refs/heads/{request.head_branch}"
                existing_local_head = self._local_ref_sha(root, remote_head_ref)
                remote_head_sha = self._remote_ref_sha(
                    root,
                    repository_url,
                    remote_head_ref,
                )
                allowed_remote_heads = {""}
                if existing_local_head and existing_local_head != base_sha:
                    allowed_remote_heads.add(existing_local_head)
                if remote_head_sha not in allowed_remote_heads:
                    self._fail("remote_ref_diverged", stage, partial)

            stage = "patch_preflight"
            self._require_exact_materialized_patch(root, request)

            stage = "stage_patch"
            with tempfile.TemporaryDirectory(
                prefix="uca-source-control-index-"
            ) as temporary_index_root:
                index_file = Path(temporary_index_root) / "index"
                self._run(
                    root,
                    ["read-tree", base_sha],
                    index_file=index_file,
                )
                self._run(
                    root,
                    [
                        "apply",
                        "--cached",
                        "--whitespace=error",
                        "--recount",
                        "-",
                    ],
                    stdin=request.patch_text,
                    index_file=index_file,
                )
                staged_patch = self._capture_staged_patch(
                    root,
                    request.changed_paths,
                    index_file=index_file,
                )
                if staged_patch != request.patch_text:
                    self._fail("staged_patch_mismatch", stage, partial)
                if hashlib.sha256(staged_patch.encode("utf-8")).hexdigest() != request.patch_sha256:
                    self._fail("staged_patch_hash_mismatch", stage, partial)
                staged_check = self._run(
                    root,
                    ["-c", "core.whitespace=cr-at-eol", "diff", "--cached", "--check"],
                    check=False,
                    index_file=index_file,
                )
                if staged_check.returncode != 0:
                    self._fail("staged_patch_whitespace_error", stage, partial)

                stage = "commit"
                tree_sha = self._require_sha(
                    self._run(
                        root,
                        ["write-tree"],
                        index_file=index_file,
                    ).stdout.strip(),
                    "unable_to_write_tree",
                    stage,
                    partial,
                )
            local_ref = f"refs/heads/{request.head_branch}"
            existing_local_sha = self._local_ref_sha(root, local_ref)
            local_ref_existed = bool(existing_local_sha)
            reused = False
            if existing_local_sha and existing_local_sha != base_sha:
                self._verify_exact_commit(
                    root,
                    request,
                    existing_local_sha,
                    expected_tree_sha=tree_sha,
                    partial=partial,
                )
                commit_sha = existing_local_sha
                partial = partial.model_copy(
                    update={
                        "commit_sha": commit_sha,
                        "local_ref_attempted": True,
                        "local_ref": local_ref,
                    }
                )
                self._run(
                    root,
                    [
                        "update-ref",
                        "--no-deref",
                        local_ref,
                        commit_sha,
                        commit_sha,
                    ],
                )
                if self._direct_local_ref_sha(root, local_ref) != commit_sha:
                    self._fail("local_ref_not_verified", stage, partial)
                partial = partial.model_copy(update={"local_ref_verified": True})
                reused = True
            else:
                commit_sha = self._require_sha(
                    self._run(
                        root,
                        ["commit-tree", tree_sha, "-p", base_sha, "-F", "-"],
                        stdin=request.commit_message + "\n",
                        identity=True,
                    ).stdout.strip(),
                    "commit_creation_failed",
                    stage,
                    partial,
                )
                partial = partial.model_copy(
                    update={"commit_created": True, "commit_sha": commit_sha}
                )
                self._verify_exact_commit(
                    root,
                    request,
                    commit_sha,
                    expected_tree_sha=tree_sha,
                    partial=partial,
                )
                expected_old = existing_local_sha or self._zero_object_id(root)
                partial = partial.model_copy(
                    update={
                        "local_ref_attempted": True,
                        "local_ref": local_ref,
                    }
                )
                self._run(
                    root,
                    ["update-ref", "--no-deref", local_ref, commit_sha, expected_old],
                )
                if self._direct_local_ref_sha(root, local_ref) != commit_sha:
                    self._fail("local_ref_not_verified", stage, partial)
                partial = partial.model_copy(
                    update={
                        "local_ref_verified": True,
                        "local_ref_created": not local_ref_existed,
                        "local_ref_updated": local_ref_existed,
                    }
                )

            self._require_clean_index(root, stage=stage, partial=partial)

            if request.action is PublicationAction.COMMIT:
                return SourceControlPublicationResult(
                    publication_id=request.publication_id,
                    action=request.action,
                    commit_sha=commit_sha,
                    tree_sha=tree_sha,
                    local_ref=local_ref,
                    commit_created=not reused,
                    local_ref_created=not reused and not local_ref_existed,
                    local_ref_updated=not reused and local_ref_existed,
                    reused=reused,
                )

            stage = "push"
            remote_ref = f"refs/heads/{request.head_branch}"
            remote_before = self._remote_ref_sha(root, repository_url, remote_ref)
            if remote_before not in {"", commit_sha}:
                self._fail("remote_ref_diverged", stage, partial)
            if remote_before != commit_sha:
                partial = partial.model_copy(update={"push_attempted": True})
                self._run_network(
                    root,
                    [
                        "push",
                        "--no-verify",
                        "--porcelain",
                        f"--force-with-lease={remote_ref}:{remote_before}",
                        repository_url,
                        f"{commit_sha}:{remote_ref}",
                    ],
                    with_objects=True,
                )
            remote_after = self._remote_ref_sha(root, repository_url, remote_ref)
            if remote_after != commit_sha:
                self._fail("remote_push_not_verified", stage, partial)
            partial = partial.model_copy(update={"push_verified": True, "remote_sha": remote_after})
            if self._remote_ref_sha(
                root,
                repository_url,
                f"refs/heads/{base_branch}",
            ) != base_sha:
                self._fail("remote_base_ref_drift", stage, partial)

            draft_result: DraftPullRequestResult | None = None
            if request.action is PublicationAction.DRAFT_PR:
                stage = "draft_pr"
                partial = partial.model_copy(update={"draft_pr_attempted": True})
                if draft_pr_creator is None:
                    self._fail("draft_pr_capability_unavailable", stage, partial)
                draft_request = DraftPullRequestRequest(
                    publication_id=request.publication_id,
                    repository=request.repository,
                    base_branch=request.repository.base_ref,
                    head_branch=request.head_branch,
                    head_sha=commit_sha,
                    title=request.draft_pr_title,
                    body=request.draft_pr_body,
                )
                draft_result = draft_pr_creator.ensure_draft(draft_request)
                if not isinstance(draft_result, DraftPullRequestResult):
                    self._fail("draft_pr_result_incompatible", stage, partial)
                partial = partial.model_copy(
                    update={
                        "draft_pr_created": draft_result.created,
                        "draft_pr_url": draft_result.url,
                    }
                )
                if (
                    draft_result.base_branch != draft_request.base_branch
                    or draft_result.head_branch != draft_request.head_branch
                    or draft_result.head_sha != commit_sha
                    or draft_result.draft is not True
                ):
                    self._fail("draft_pr_result_mismatch", stage, partial)

            return SourceControlPublicationResult(
                publication_id=request.publication_id,
                action=request.action,
                commit_sha=commit_sha,
                tree_sha=tree_sha,
                local_ref=local_ref,
                commit_created=not reused,
                local_ref_created=not reused and not local_ref_existed,
                local_ref_updated=not reused and local_ref_existed,
                pushed=True,
                push_performed=remote_before != commit_sha,
                remote_before_sha=remote_before,
                remote_after_sha=remote_after,
                draft_pr=draft_result,
                reused=(
                    reused
                    and remote_before == commit_sha
                    and (draft_result is None or not draft_result.created)
                ),
            )
        except SourceControlPublicationError:
            raise
        except Exception as exc:
            raise SourceControlPublicationError(
                "adapter_operation_failed",
                stage=stage,
                cause_type=type(exc).__name__,
                partial_effects=partial,
            ) from exc

    def _contained_sandbox(self, request: ExactPublicationRequest) -> Path:
        root = Path(request.sandbox_path).resolve()
        sandboxes_root = Path(request.sandboxes_root).resolve()
        if root == sandboxes_root or sandboxes_root not in root.parents:
            raise SourceControlPublicationError(
                "sandbox_path_not_contained",
                stage="sandbox_preflight",
            )
        return root

    def _normalize_repository_url(self, value: str) -> str:
        raw = value.strip()
        if raw.startswith("git@"):
            if any(ord(character) < 32 or ord(character) == 127 for character in raw):
                raise SourceControlPublicationError(
                    "repository_url_invalid",
                    stage="sandbox_preflight",
                )
            return raw
        if "://" in raw:
            parsed = urllib.parse.urlsplit(raw)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or not parsed.path
                or parsed.path == "/"
                or parsed.username
                or parsed.password
                or parsed.query
                or parsed.fragment
            ):
                raise SourceControlPublicationError(
                    "repository_url_invalid",
                    stage="sandbox_preflight",
                )
            return urllib.parse.urlunsplit(parsed)
        local = Path(raw)
        if not local.is_absolute():
            raise SourceControlPublicationError(
                "local_repository_not_absolute",
                stage="sandbox_preflight",
            )
        if local.exists():
            if not self.allow_local_repositories:
                raise SourceControlPublicationError(
                    "local_repository_not_allowed",
                    stage="sandbox_preflight",
                )
            return str(local.resolve())
        raise SourceControlPublicationError(
            "repository_url_invalid",
            stage="sandbox_preflight",
        )

    def _require_git_repository(self, root: Path) -> None:
        if not root.is_dir():
            raise SourceControlPublicationError(
                "sandbox_repository_missing",
                stage="sandbox_preflight",
            )
        result = self._run(root, ["rev-parse", "--is-inside-work-tree"], check=False)
        if result.returncode != 0 or result.stdout.strip() != "true":
            raise SourceControlPublicationError(
                "sandbox_repository_invalid",
                stage="sandbox_preflight",
            )

    def _require_head(self, root: Path, base_sha: str) -> None:
        head = self._run(root, ["rev-parse", "HEAD"]).stdout.strip()
        if head != base_sha:
            raise SourceControlPublicationError(
                "sandbox_head_mismatch",
                stage="sandbox_preflight",
            )

    def _require_clean_index(
        self,
        root: Path,
        *,
        stage: str = "sandbox_preflight",
        partial: PublicationPartialEffects | None = None,
    ) -> None:
        result = self._run(root, ["diff", "--cached", "--quiet", "--exit-code"], check=False)
        if result.returncode != 0:
            raise SourceControlPublicationError(
                "sandbox_index_not_clean",
                stage=stage,
                partial_effects=partial,
            )

    def _require_valid_head_ref(self, root: Path, branch: str) -> None:
        if not git_metadata_paths_are_safe(
            root,
            local_ref=f"refs/heads/{branch}",
        ):
            raise SourceControlPublicationError(
                "sandbox_git_metadata_unsafe",
                stage="sandbox_preflight",
            )
        result = self._run(
            root,
            ["check-ref-format", f"refs/heads/{branch}"],
            check=False,
        )
        if result.returncode != 0:
            raise SourceControlPublicationError(
                "head_branch_invalid",
                stage="sandbox_preflight",
            )
        symbolic = self._run(
            root,
            ["symbolic-ref", "-q", f"refs/heads/{branch}"],
            check=False,
        )
        if symbolic.returncode == 0:
            raise SourceControlPublicationError(
                "symbolic_head_branch_forbidden",
                stage="sandbox_preflight",
            )
        if symbolic.returncode not in {1, 128}:
            raise SourceControlPublicationError(
                "head_branch_ref_unreadable",
                stage="sandbox_preflight",
            )

    def _require_safe_local_config(self, root: Path) -> None:
        git_dir = root / ".git"
        config_path = git_dir / "config"
        if not git_metadata_paths_are_safe(root):
            raise SourceControlPublicationError(
                "sandbox_git_metadata_unsafe",
                stage="sandbox_preflight",
            )
        if (
            not git_dir.is_dir()
            or git_dir.is_symlink()
            or (git_dir / "commondir").exists()
            or (git_dir / "commondir").is_symlink()
            or not config_path.is_file()
            or config_path.is_symlink()
        ):
            raise SourceControlPublicationError(
                "sandbox_git_config_unavailable",
                stage="sandbox_preflight",
            )
        result = self._run(
            root,
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
            raise SourceControlPublicationError(
                "sandbox_git_config_invalid",
                stage="sandbox_preflight",
            )
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
            branch_safe = bool(
                re.fullmatch(r"branch\..+\.(remote|merge)", key)
            )
            if key not in safe_core and not remote_safe and not branch_safe:
                raise SourceControlPublicationError(
                    "sandbox_git_config_unsafe",
                    stage="sandbox_preflight",
                )
        for metadata_path in (git_dir / "info" / "grafts", git_dir / "shallow"):
            if metadata_path.is_symlink() or (
                metadata_path.is_file() and metadata_path.stat().st_size > 0
            ):
                raise SourceControlPublicationError(
                    "sandbox_git_history_override_forbidden",
                    stage="sandbox_preflight",
                )
        replacements = self._run(
            root,
            ["for-each-ref", "--format=%(refname)", "refs/replace"],
            check=False,
        )
        if replacements.returncode != 0 or replacements.stdout.strip():
            raise SourceControlPublicationError(
                "sandbox_git_history_override_forbidden",
                stage="sandbox_preflight",
            )

    def _require_base_branch(self, root: Path, branch: str, base_sha: str) -> None:
        candidates = (
            f"refs/heads/{branch}",
            f"refs/remotes/origin/{branch}",
        )
        for candidate in candidates:
            symbolic = self._run(
                root,
                ["symbolic-ref", "-q", candidate],
                check=False,
            )
            if symbolic.returncode == 0:
                continue
            if symbolic.returncode not in {1, 128}:
                raise SourceControlPublicationError(
                    "base_ref_not_canonical_branch",
                    stage="sandbox_preflight",
                )
            result = self._run(
                root,
                ["rev-parse", "--verify", f"{candidate}^{{commit}}"],
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip() == base_sha:
                return
        raise SourceControlPublicationError(
            "base_ref_not_canonical_branch",
            stage="sandbox_preflight",
        )

    def _require_exact_materialized_patch(
        self,
        root: Path,
        request: ExactPublicationRequest,
    ) -> None:
        proposal = PatchProposal(
            summary=request.edit_proposal.summary,
            unified_diff=request.patch_text,
            changed_paths=request.changed_paths,
            requested_test_profiles=request.edit_proposal.requested_test_profiles,
            assumptions=request.edit_proposal.assumptions,
        )
        captured = self.patch_engine.capture_worktree_proposal(
            root,
            request.manifest,
            request.edit_proposal,
        )
        validation = self.patch_engine.validate_materialized(
            root,
            request.manifest,
            proposal,
        )
        if (
            not validation.valid
            or validation.patch_sha256 != request.patch_sha256
            or validation.changed_paths != request.changed_paths
            or captured.unified_diff != request.patch_text
            or captured.changed_paths != request.changed_paths
        ):
            raise SourceControlPublicationError(
                "materialized_patch_mismatch",
                stage="patch_preflight",
            )

    def _capture_staged_patch(
        self,
        root: Path,
        paths: tuple[str, ...],
        *,
        index_file: Path,
    ) -> str:
        return self._capture_diff(
            root,
            paths,
            [
                "diff",
                "--cached",
                "--no-ext-diff",
                "--no-textconv",
                "--no-color",
                "--full-index",
            ],
            index_file=index_file,
        )

    def _capture_commit_patch(
        self,
        root: Path,
        base_sha: str,
        commit_sha: str,
        paths: tuple[str, ...],
    ) -> str:
        return self._capture_diff(
            root,
            paths,
            [
                "diff",
                "--no-ext-diff",
                "--no-textconv",
                "--no-color",
                "--full-index",
                base_sha,
                commit_sha,
            ],
        )

    def _capture_diff(
        self,
        root: Path,
        paths: tuple[str, ...],
        prefix: list[str],
        *,
        index_file: Path | None = None,
    ) -> str:
        sections: list[str] = []
        for path in paths:
            result = self._run(
                root,
                [*prefix, "--", path],
                index_file=index_file,
            )
            if not result.stdout:
                raise _GitCommandError("expected Git diff section is missing")
            sections.append(result.stdout if result.stdout.endswith("\n") else result.stdout + "\n")
        return "".join(sections)

    def _verify_exact_commit(
        self,
        root: Path,
        request: ExactPublicationRequest,
        commit_sha: str,
        *,
        expected_tree_sha: str,
        partial: PublicationPartialEffects,
    ) -> None:
        stage = "commit"
        commit_sha = self._require_sha(commit_sha, "commit_invalid", stage, partial)
        raw_commit = self._run(root, ["cat-file", "commit", commit_sha]).stdout
        header, separator, message = raw_commit.partition("\n\n")
        if not separator:
            self._fail("commit_invalid", stage, partial)
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
        if parents != [request.manifest.base_sha]:
            self._fail("commit_parent_mismatch", stage, partial)
        if tree_headers != [expected_tree_sha]:
            self._fail("commit_tree_mismatch", stage, partial)
        committed_patch = self._capture_commit_patch(
            root,
            request.manifest.base_sha,
            commit_sha,
            request.changed_paths,
        )
        if committed_patch != request.patch_text:
            self._fail("committed_patch_mismatch", stage, partial)
        committed_paths = tuple(
            item
            for item in self._run(
                root,
                [
                    "diff",
                    "--name-only",
                    request.manifest.base_sha,
                    commit_sha,
                ],
            ).stdout.splitlines()
            if item
        )
        if set(committed_paths) != set(request.changed_paths):
            self._fail("committed_paths_mismatch", stage, partial)
        if message.rstrip("\n") != request.commit_message.rstrip("\n"):
            self._fail("commit_message_mismatch", stage, partial)

    def _local_ref_sha(self, root: Path, reference: str) -> str:
        result = self._run(
            root,
            ["show-ref", "--verify", "--quiet", reference],
            check=False,
        )
        if result.returncode == 1:
            return ""
        if result.returncode != 0:
            raise _GitCommandError("unable to read local publication ref")
        value = self._run(root, ["rev-parse", "--verify", f"{reference}^{{commit}}"]).stdout.strip()
        if not _SHA.fullmatch(value):
            raise _GitCommandError("local publication ref did not resolve to a commit")
        return value

    def _direct_local_ref_sha(self, root: Path, reference: str) -> str:
        symbolic = self._run(
            root,
            ["symbolic-ref", "-q", reference],
            check=False,
        )
        if symbolic.returncode == 0:
            raise _GitCommandError("local publication ref became symbolic")
        if symbolic.returncode not in {1, 128}:
            raise _GitCommandError("unable to verify local publication ref type")
        return self._local_ref_sha(root, reference)

    def _remote_ref_sha(self, root: Path, repository: str, reference: str) -> str:
        result = self._run_network(
            root,
            [
                "ls-remote",
                "--symref",
                "--exit-code",
                "--heads",
                repository,
                reference,
            ],
            check=False,
        )
        if result.returncode == 2 and not result.stdout.strip():
            return ""
        if result.returncode != 0:
            raise _GitCommandError("unable to read remote publication ref")
        if any(line.startswith("ref:") for line in result.stdout.splitlines()):
            raise _GitCommandError("remote publication ref must not be symbolic")
        rows = [line.split() for line in result.stdout.splitlines() if line.strip()]
        if len(rows) != 1 or len(rows[0]) != 2 or rows[0][1] != reference:
            raise _GitCommandError("remote publication ref response is invalid")
        if not _SHA.fullmatch(rows[0][0]):
            raise _GitCommandError("remote publication ref did not resolve to a commit")
        return rows[0][0]

    def _run_network(
        self,
        source_root: Path,
        arguments: list[str],
        *,
        check: bool = True,
        with_objects: bool = False,
    ) -> _CommandResult:
        object_format = self._run(
            source_root,
            ["rev-parse", "--show-object-format"],
        ).stdout.strip()
        if object_format not in {"sha1", "sha256"}:
            raise _GitCommandError("unsupported Git object format")
        with tempfile.TemporaryDirectory(
            prefix="uca-source-control-network-"
        ) as temporary_root:
            temporary_path = Path(temporary_root)
            network_repository = temporary_path / "client.git"
            self._run(
                temporary_path,
                [
                    "init",
                    "--bare",
                    f"--object-format={object_format}",
                    str(network_repository),
                ],
            )
            alternate_objects: Path | None = None
            if with_objects:
                alternate_objects = source_root / ".git" / "objects"
                alternate_text = str(alternate_objects)
                if os.pathsep in alternate_text or "\n" in alternate_text:
                    raise _GitCommandError("sandbox object path is not safely representable")
            return self._run(
                network_repository,
                arguments,
                check=check,
                alternate_object_directory=alternate_objects,
            )

    def _zero_object_id(self, root: Path) -> str:
        object_format = self._run(root, ["rev-parse", "--show-object-format"]).stdout.strip()
        if object_format == "sha1":
            return "0" * 40
        if object_format == "sha256":
            return "0" * 64
        raise _GitCommandError("unsupported Git object format")

    def _require_sha(
        self,
        value: str,
        code: str,
        stage: str,
        partial: PublicationPartialEffects,
    ) -> str:
        if not _SHA.fullmatch(value):
            self._fail(code, stage, partial)
        return value

    @staticmethod
    def _fail(
        code: str,
        stage: str,
        partial: PublicationPartialEffects,
    ) -> None:
        raise SourceControlPublicationError(
            code,
            stage=stage,
            partial_effects=partial,
        )

    def _run(
        self,
        root: Path,
        arguments: list[str],
        *,
        check: bool = True,
        stdin: str | None = None,
        identity: bool = False,
        index_file: Path | None = None,
        alternate_object_directory: Path | None = None,
    ) -> _CommandResult:
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
        if index_file is not None:
            environment["GIT_INDEX_FILE"] = str(index_file)
        if alternate_object_directory is not None:
            environment["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = str(
                alternate_object_directory
            )
        if identity:
            environment.update(
                {
                    "GIT_AUTHOR_NAME": self.committer_name,
                    "GIT_AUTHOR_EMAIL": self.committer_email,
                    "GIT_COMMITTER_NAME": self.committer_name,
                    "GIT_COMMITTER_EMAIL": self.committer_email,
                }
            )
        command = [
            self.git_binary,
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "tag.gpgsign=false",
            "-c",
            "core.logAllRefUpdates=false",
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
            str(root),
            *arguments,
        ]
        with ExitStack() as stack:
            git_directory = root / ".git"
            if git_directory.exists() or git_directory.is_symlink():
                local_ref = ""
                if (
                    arguments[:2] == ["update-ref", "--no-deref"]
                    and len(arguments) > 2
                ):
                    local_ref = arguments[2]
                if not git_metadata_paths_are_safe(root, local_ref=local_ref):
                    raise _GitCommandError("sandbox Git metadata changed unsafely")
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
                    raise _GitCommandError("sandbox Git metadata changed unsafely")
                proxy_root = Path(
                    stack.enter_context(
                        tempfile.TemporaryDirectory(prefix="uca-git-dir-proxy-")
                    )
                )
                common_path = str(git_directory)
                if "\n" in common_path:
                    raise _GitCommandError("sandbox Git path is not safely representable")
                (proxy_root / "commondir").write_text(
                    common_path + "\n",
                    encoding="utf-8",
                )
                (proxy_root / "HEAD").write_bytes(head_path.read_bytes())
                environment["GIT_DIR"] = str(proxy_root)
                environment["GIT_WORK_TREE"] = str(root)
                environment.setdefault("GIT_INDEX_FILE", str(index_path))
            process = subprocess.run(
                command,
                input=stdin,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                shell=False,
                env=environment,
            )
        result = _CommandResult(process.returncode, process.stdout, process.stderr)
        if check and result.returncode != 0:
            raise _GitCommandError("fixed Git operation failed")
        return result
