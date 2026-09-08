"""Safe and discovery execution adapter resolved exclusively from stored v2 admission."""

from __future__ import annotations

import os
import secrets
import time
from dataclasses import replace
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec, SandboxInfo
from universal_coding_agent.core.safe_models import (
    SafeContextEvidence,
    SafeTaskRequest,
    StructuredEditProposal,
)
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService,
    _GitBudget,
)
from universal_coding_agent.product.program_source_patch import verified_patch_edits
from universal_coding_agent.product.program_source_transitions import _canonical, _hash, _require
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.sandbox.owned_source import _stamp


class AdmittedSafeExecution:
    """Trusted host adapter. Every destination is reloaded from the durable admission."""

    def __init__(self, dispatch, operation_id, owner_token):
        self.dispatch, self.operation_id, self.owner_token = dispatch, operation_id, owner_token
        self.store = dispatch.store
        self.services = None
        self._ticket = None
        self._active_kind = None
        self._applying_paths = None

    def _authorize(self, kind):
        """Called only by the explicit transition while its authority transaction is held.

        Persist only a digest. A reconstructed adapter cannot recover this process-local
        capability, even if the durable intent has not reached its invocation claim yet.
        """
        _require(self.store.connection.in_transaction, "handoff requires its authority transaction")
        self._ticket = secrets.token_bytes(32)
        self._active_kind = None
        self.store.connection.execute(
            """UPDATE program_source_dispatches SET invocation_sha256 = ?,
            invocation_kind = ?, invocation_state = 'armed' WHERE operation_id = ?""",
            (_hash(self._ticket), kind, self.operation_id),
        )

    def _claim(self, row, kind):
        _require(
            self._ticket is not None
            and row["invocation_sha256"] == _hash(self._ticket)
            and row["invocation_kind"] == kind
            and row["invocation_state"] == "armed"
            and self._active_kind is None,
            "explicit invocation capability is missing or already consumed",
        )
        changed = self.store.connection.execute(
            """UPDATE program_source_dispatches SET invocation_state = 'claimed'
            WHERE operation_id = ? AND invocation_sha256 = ? AND invocation_state = 'armed'""",
            (self.operation_id, _hash(self._ticket)),
        ).rowcount
        _require(changed == 1, "explicit invocation claim CAS changed")
        self._active_kind = kind

    def _active(self, row, kind):
        _require(
            self._ticket is not None
            and self._active_kind == kind
            and row["invocation_kind"] == kind
            and row["invocation_state"] == "claimed"
            and row["invocation_sha256"] == _hash(self._ticket),
            "operation has no live consumed invocation capability",
        )

    def _load(self, **kwargs):
        return self.dispatch._load(self.operation_id, self.owner_token, **kwargs)

    def _path(self):
        row, admission, _ = self._load()
        self.dispatch._verify_files(row, admission)
        return (
            self.dispatch.preparation.filesystem.root / ("execution-" + self.operation_id) / "repo"
        )

    def task(self):
        return SafeTaskRequest.model_validate(
            self.dispatch._json(self.dispatch._row(self.operation_id)["task_sha256"])
        )

    def discovery_request(self, service):
        with self.store._transaction():
            row, admission, before = self._load()
            _require(
                row["state"] == "discovery_started"
                and service.state_root == self.store.safe.artifacts.root.parent
                and service.control is self.store.safe.control
                and service.remote_operations is self.store.safe.remote_operations,
                "discovery service host or handoff differs",
            )
            self.dispatch._verify_files(row, admission)
            self._claim(row, "discovery")
            phase = self.store._plan(before.identity).phases[before.generation]
            context = self.store._get(admission["dependency_sha256"]).decode()
            _require(
                self.store.programs.artifacts.read_text_bounded_verified(
                    admission["dependency_ref"],
                    expected_sha256=admission["dependency_sha256"],
                    max_bytes=48_000,
                )
                == context,
                "source dependency context changed",
            )
            return {
                "task_id": admission["task_id"],
                "thread_id": admission["thread_id"],
                "title": phase.title,
                "objective": phase.objective,
                "repository": RepositorySpec(
                    url=admission["origin_repository_url"], base_ref=admission["origin_base_sha"]
                ),
                "policy": self.store.trusted_policy,
                "test_profiles": tuple(self.store.trusted_policy.profile_map()),
                "acceptance_criteria": phase.acceptance_criteria,
                "expected_base_sha": admission["derived_git_commit_sha"],
                "accepted_evidence": (
                    SafeContextEvidence(
                        context_type="accepted_source_lineage_v2",
                        source_ref=admission["dependency_ref"],
                        sha256=admission["dependency_sha256"],
                        content=context,
                    ),
                ),
            }

    def prepare(self, task_id, repository):
        with self.store._transaction():
            row, admission, _ = self._load()
            _require(
                task_id == admission["task_id"]
                and repository.url == admission["origin_repository_url"]
                and repository.base_ref == admission["origin_base_sha"],
                "sandbox request does not match stored admission",
            )
            path = self._path()
            return SandboxInfo(
                sandbox_id=task_id,
                repository_url=repository.url,
                base_ref=repository.base_ref,
                base_sha=admission["derived_git_commit_sha"],
                path=str(path),
                clean=True,
            )

    def read_only_git_checks(self, path):
        with self.store._transaction():
            _require(path == self._path(), "discovery destination differs")
        return [{"name": "admitted_complete_source_and_git", "passed": True}]

    def discovery_completed(self, task):
        with self.store._transaction():
            row, admission, before = self._load()
            self._active(row, "discovery")
            _require(row["state"] == "discovery_started", "discovery completion CAS changed")
            self.dispatch._verify_files(row, admission)
            phase = self.store._plan(before.identity).phases[before.generation]
            _require(
                task.task_id == admission["task_id"]
                and task.thread_id == admission["thread_id"]
                and task.objective == phase.objective
                and task.manifest.acceptance_criteria == phase.acceptance_criteria
                and task.manifest.base_sha == admission["derived_git_commit_sha"]
                and set(task.manifest.test_profiles) == set(self.store.trusted_policy.profile_map())
                and task.policy == self.store.trusted_policy
                and task.repository.url == admission["origin_repository_url"]
                and not task.require_publish_approval,
                "actual discovered task differs from execution admission",
            )
            _require(
                all(item.operation.value == "modify" for item in task.manifest.allowed_changes),
                "bounded v2 discovery permits existing-file modifications only",
            )
            captured = []
            for name in (
                "solution-discovery-snapshot.json",
                "solution-impact-plan.json",
                "solution-discovery-model-validation.json",
                "solution-discovery-read-only-checks.json",
                "discovered-change-manifest.json",
                "solution-discovery-provenance.json",
            ):
                ref = f"artifact://tasks/{task.task_id}/{name}"
                raw = self.store.safe.artifacts._read_bytes_bounded(ref, max_bytes=2_000_000)
                captured.append({"ref": ref, "sha256": self.store._put(raw)})
            self.dispatch._state(
                self.operation_id,
                row["state"],
                "discovered",
                task_sha256=self.store._put(_canonical(task.model_dump(mode="json"))),
                discovery_sha256=self.store._put(_canonical(captured)),
            )

    def start_safe(self):
        with self.store._transaction():
            row, admission, _ = self._load()
            _require(row["state"] == "discovered", "Safe initialization was already started")
            if self._active_kind == "discovery":
                self._active(row, "discovery")
            else:
                self._claim(row, "safe_prepare")
            self.dispatch._verify_files(row, admission)
            _require(
                not self.store.connection.execute(
                    "SELECT 1 FROM safe.checkpoints WHERE thread_id = ? LIMIT 1",
                    (admission["thread_id"],),
                ).fetchone(),
                "Safe thread already exists before handoff",
            )
            self.dispatch._state(self.operation_id, "discovered", "safe_started")
            self._authorize("safe")

    def entry(self, thread_id, task_id):
        with self.store._transaction():
            row, admission, _ = self._load()
            _require(
                thread_id == admission["thread_id"]
                and (task_id is None or task_id == admission["task_id"])
                and row["state"] == ("safe_started" if task_id else "resume_started"),
                "Safe invocation is not the admitted explicit handoff",
            )
            self.dispatch._verify_files(row, admission)
            self._claim(row, "safe" if task_id else "resume")

    def safe_service(self):
        from contextlib import contextmanager

        @contextmanager
        def opened():
            safe = SafeAgentService.create(
                self.store.safe.artifacts.root.parent,
                self.dispatch.provider,
                control=self.store.safe.control,
                remote_operations=self.store.safe.remote_operations,
                execution_adapter=self,
            )
            try:
                yield safe
            finally:
                safe.close()

        return opened()

    def bind_services(self, services, state_root, protocol):
        _require(state_root == self.store.safe.artifacts.root.parent, "Safe adapter host differs")

        # Bind read-only Git to the isolated bounded runner, including optional-lock suppression.
        # These are fresh v2 service instances; legacy engines and helpers are not modified.
        def git(root, arguments, *, check=True):
            attestor = self._attestor(root)
            budget = _GitBudget(
                time.monotonic() + attestor.policy.operation_timeout_seconds,
                attestor.policy.max_git_output_bytes,
            )
            result = attestor._run_result(
                tuple(arguments), b"", budget,
                expected_returncodes=(0,) if check else tuple(range(256)),
            )
            result.stdout = result.stdout.decode("utf-8")
            result.stderr = result.stderr.decode("utf-8")
            return result

        apply = services.edit_engine.apply

        def apply_owned(sandbox, manifest, proposal):
            self._applying_paths = tuple(proposal.changed_paths)
            try:
                return apply(sandbox, manifest, proposal)
            finally:
                self._applying_paths = None

        services.edit_engine._git = git
        services.edit_engine.apply = apply_owned
        services.edit_engine.restore = self._restore
        services.patch_engine._git = git
        services.indexer._git = lambda root, *args: git(root, args).stdout.encode("utf-8")
        self.services = replace(services, sandbox=self, execution_boundary=self)
        return self.services

    def _restore(self, sandbox, manifest, changed_paths):
        """Restore exact approved Base bytes without Git's index/lock side effects."""
        from contextlib import ExitStack

        with self.store._transaction():
            row, admission, before = self._load()
            self._active(row, "safe" if row["state"] == "safe_started" else "resume")
            destination = (
                self.dispatch.preparation.filesystem.root
                / ("execution-" + self.operation_id) / "repo"
            )
            _require(
                Path(sandbox) == destination
                and manifest == self.task().manifest
                and set(changed_paths).issubset(manifest.allowed_path_map()),
                "rollback must target this admitted execution scope",
            )
            fs = self.dispatch.preparation.filesystem
            base_row = self.dispatch.preparation._row(self.operation_id)
            intent = self.dispatch._json(base_row["intent_sha256"])
            allocation = self.dispatch._json(base_row["allocation_sha256"])
            files = {item.path: item for item in before.files}
            deadline = fs.deadline()
            with fs.root_handle(intent["root_chain"]) as (root, _), ExitStack() as stack:
                operation = stack.enter_context(
                    fs.directory(root, "execution-" + self.operation_id, allocation["operation"])
                )
                repo = stack.enter_context(fs.directory(operation, "repo", allocation["source"]))
                if self._applying_paths is not None:
                    _require(
                        tuple(changed_paths) == self._applying_paths,
                        "in-flight rollback differs from the live edit attempt",
                    )
                    # Only a live edit failure can inspect these potentially partial bytes.
                    # Every other byte, Git entry and filesystem identity is still verified
                    # against the retained proof before any restoration writes occur.
                    observed = dict(files)
                    for path in changed_paths:
                        with ExitStack() as parents:
                            parent = repo
                            parts = path.split("/")
                            for part in parts[:-1]:
                                parent = parents.enter_context(fs.directory(parent, part))
                            fd = os.open(
                                parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                                dir_fd=parent,
                            )
                            try:
                                info = os.fstat(fd)
                                expected = self.dispatch._json(row["filesystem_sha256"])[
                                    "entries"
                                ][path]
                                _require(
                                    _stamp(info)[:5] == expected[:5] and info.st_nlink == 1,
                                    "in-flight rollback file identity changed",
                                )
                                chunks, size = [], 0
                                while True:
                                    fs.check_time(deadline)
                                    chunk = os.read(fd, 65_536)
                                    if not chunk:
                                        break
                                    size += len(chunk)
                                    _require(
                                        size <= self.store.source.policy.max_file_bytes,
                                        "in-flight rollback source exceeds file bound",
                                    )
                                    chunks.append(chunk)
                                _require(
                                    _stamp(info) == _stamp(os.fstat(fd)) == _stamp(
                                        os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
                                    ),
                                    "in-flight rollback source changed during read",
                                )
                                observed[path] = replace(files[path], content=b"".join(chunks))
                            finally:
                                os.close(fd)
                    current = replace(before, files=tuple(observed[p] for p in sorted(observed)))
                    self.dispatch._verify_files(
                        row, admission, retained=current, mutable=tuple(changed_paths)
                    )
                else:
                    self.dispatch._verify_files(row, admission)
                for path in changed_paths:
                    _require(path in files, "rollback Base file is missing")
                    with ExitStack() as parents:
                        parent = repo
                        parts = path.split("/")
                        for part in parts[:-1]:
                            parent = parents.enter_context(fs.directory(parent, part))
                        fd = os.open(parts[-1], os.O_WRONLY | os.O_NOFOLLOW, dir_fd=parent)
                        try:
                            expected = self.dispatch._json(row["filesystem_sha256"])["entries"][
                                path
                            ]
                            info = os.fstat(fd)
                            _require(
                                _stamp(info)[:5] == expected[:5]
                                and info.st_nlink == 1,
                                "rollback destination changed",
                            )
                            os.ftruncate(fd, 0)
                            content = files[path].content
                            offset = 0
                            while offset < len(content):
                                fs.check_time(deadline)
                                count = os.write(fd, content[offset : offset + 65_536])
                                _require(count > 0, "rollback made no write progress")
                                offset += count
                            os.fsync(fd)
                        finally:
                            os.close(fd)
                fs.anchor(intent["root_chain"])
            proof = self.dispatch._verify_files(
                row, admission, retained=before, mutable=tuple(changed_paths)
            )
            self.store.connection.execute(
                """UPDATE program_source_dispatches SET filesystem_sha256 = ?,
                retained_sha256 = ? WHERE operation_id = ?""",
                (self.store._put(proof), self.store._put(self.store.source.snapshot_bytes(before)),
                 self.operation_id),
            )
            return True

    def discovery_indexer(self):
        from universal_coding_agent.repository.indexer import RepositoryIndexer

        indexer = RepositoryIndexer()

        def git(root, *args):
            attestor = self._attestor(root)
            return attestor._run(
                tuple(args),
                b"",
                _GitBudget(
                    time.monotonic() + attestor.policy.operation_timeout_seconds,
                    attestor.policy.max_git_output_bytes,
                ),
            )

        indexer._git = git
        return indexer

    def _attestor(self, path):
        inherited = self.store.attestor
        return ProgramGitSourceAttestationService(
            path,
            inherited.repository_sha256,
            source_policy=inherited.source.policy,
            git_policy=inherited.policy,
        )

    def node(self, name, state, action):
        from langgraph.errors import GraphInterrupt

        with self.store._transaction():
            row, admission, before = self._load()
            self._active(row, "safe" if row["state"] == "safe_started" else "resume")
            _require(
                state.get("task") == self.dispatch._json(row["task_sha256"]),
                "Safe node task is not the stored discovered task",
            )
            _require(
                row["state"] in {"safe_started", "resume_started"},
                "Safe node has no active explicit invocation",
            )
            if row["state"] == "safe_started":
                _require(
                    name in {"validate", "sandbox", "index", "scope_approval"},
                    "Safe editing requires a new exact scope decision",
                )
            if state.get("sandbox_path"):
                _require(
                    state["sandbox_path"] == str(self._path()), "Safe node destination differs"
                )
            self.dispatch._verify_files(row, admission)
            input_authority = row["authority_sha256"]
        try:
            result = action(state)
        except GraphInterrupt:
            # The first real scope interrupt has no provider or edit side effects.
            with self.store._transaction():
                row, admission, _ = self._load()
                self.dispatch._verify_files(row, admission)
            raise
        with self.store._transaction():
            completes = name == "finalize" and result.get("status") == "completed"
            row, admission, _ = self._load(after_finalize=completes)
            _require(
                row["authority_sha256"] == input_authority, "concurrent Safe invocation changed"
            )
            merged = {**state, **result}
            task = self.task()
            if name == "scope_approval":
                decision = self.dispatch._json(row["approval_sha256"])
                _require(
                    result.get("scope_approved") is decision["approved"],
                    "Safe scope decision differs from exact approval",
                )
            current = None
            mutable = ()
            if name == "apply_edits" and result.get("patch_applied"):
                proposal = StructuredEditProposal.model_validate(
                    self.store.safe.artifacts.read_json(merged["edit_proposal_ref"])
                )
                path = (
                    self.dispatch.preparation.filesystem.root
                    / ("execution-" + self.operation_id)
                    / "repo"
                )
                patch = self.services.patch_engine.capture_worktree_proposal(
                    path, task.manifest, proposal
                ).unified_diff.encode()
                edits = verified_patch_edits(before, patch, task.manifest, self.store.source.policy)
                retained = {item.path: item for item in before.files}
                retained.update((edit.path, edit.replacement) for edit in edits)
                current = replace(before, files=tuple(retained[path] for path in sorted(retained)))
                mutable = tuple(edit.path for edit in edits)
            elif name == "finalize" and result.get("rolled_back"):
                current = before
                mutable = tuple(task.manifest.allowed_path_map())
            proof = self.dispatch._verify_files(row, admission, retained=current, mutable=mutable)
            if current is not None:
                self.store.connection.execute(
                    """UPDATE program_source_dispatches
                    SET filesystem_sha256 = ?, retained_sha256 = ? WHERE operation_id = ?""",
                    (
                        self.store._put(proof),
                        self.store._put(self.store.source.snapshot_bytes(current)),
                        self.operation_id,
                    ),
                )
            if completes:
                authority, _ = self.dispatch._authority(admission, self.owner_token)
                self.store.connection.execute(
                    "UPDATE program_source_dispatches "
                    "SET authority_sha256 = ? WHERE operation_id = ?",
                    (self.store._put(_canonical(authority)), self.operation_id),
                )
        return result
