"""Exact v3 adapter with a process-local one-shot outer invocation and revoked contexts.

The frozen c2 file/rollback proof is separately reproduced here for v3. Its source
and exact-owner behavior are unchanged; no c2 object or metadata becomes v3 authority.
"""

from __future__ import annotations

import os
import secrets
import time
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from threading import RLock

from universal_coding_agent.core.cancellation import OwnedOperationKind
from universal_coding_agent.core.models import RepositorySpec, SandboxInfo
from universal_coding_agent.core.safe_models import (
    SafeContextEvidence,
    SafeTaskRequest,
    StructuredEditProposal,
)
from universal_coding_agent.product.program_continuation_execution_store import HEADS, locked
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService,
    _GitBudget,
)
from universal_coding_agent.product.program_source_patch import verified_patch_edits
from universal_coding_agent.product.program_source_transitions import _canonical, _hash, _require
from universal_coding_agent.providers.base import CancellableModelProvider
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.sandbox.owned_source import _stamp


class _BoundProvider:
    def __init__(self, execution):
        self.execution = execution

    def capabilities(self):
        return self.execution.dispatch.provider.capabilities()

    def probe(self):
        with self.execution._callback():
            return self.execution.dispatch.provider.probe()

    def invoke(self, request):
        execution = self.execution
        with execution._callback(), execution._registered():
            signal = execution.store.safe.control.cancellation.signal(execution._context.task_id)
            with signal.operation(OwnedOperationKind.PROVIDER):
                provider = execution.dispatch.provider
                if isinstance(provider, CancellableModelProvider):
                    return provider.invoke_cancellable(request, signal)
                return provider.invoke(request)

    def invoke_cancellable(self, request, cancellation):
        _require(
            cancellation._coordinator is self.execution.store.safe.control.cancellation
            and cancellation.task_id == self.execution._context.task_id,
            "v3 provider cancellation context differs",
        )
        return self.invoke(request)


class ContinuationSafeExecution:
    def __init__(self, dispatch, operation_id, owner_token, payload):
        self.dispatch, self.store = dispatch, dispatch.store
        self.operation_id, self.owner_token, self.payload = operation_id, owner_token, payload
        self._lock, self._secret = RLock(), None
        self._context = None
        self._running, self._returned, self._revoked = False, False, False
        self._callbacks, self._safe_entered = 0, False
        self._result, self._stage = None, "unarmed"
        self._applying_paths, self.services = None, None
        self._node_name, self._rollback_authority = None, None
        self.provider = _BoundProvider(self)

    def __repr__(self):
        return "ContinuationSafeExecution(private live authority)"

    def _arm(self):
        _require(
            self.store.connection.in_transaction and self._secret is None, "v3 arm is not explicit"
        )
        row = self.dispatch._row(self.operation_id)
        _require(row["invocation_state"] in {None, "revoked"}, "prior v3 ticket was not revoked")
        self._secret = secrets.token_bytes(32)
        self._epoch = row["epoch"]
        self._context = self.store.safe.control.cancellation._new_invocation(row["task_id"])
        self._stage = "discovery" if self.payload["action"] == "dispatch" else "resume"
        changed = self.store.connection.execute(
            f"UPDATE {HEADS} SET invocation_sha256=?,"
            "invocation_state='armed' WHERE operation_id=? AND epoch=?",
            (_hash(self._secret), self.operation_id, self._epoch),
        ).rowcount
        _require(changed == 1, "v3 arm CAS differs")
        self.dispatch.db.boundary("after_arm")

    def _load(self, **kwargs):
        return self.dispatch._load(self.operation_id, self.owner_token, **kwargs)

    def _discard(self):
        """Revoke local registration state after a failed grant; never release a worker."""
        self._revoked = True
        if self._context is not None:
            self.store.safe.control.cancellation._revoke_invocation(self._context)

    def _active(self, row, kind=None):
        _require(
            self._secret is not None
            and self._running
            and not self._revoked
            and row["invocation_sha256"] == _hash(self._secret)
            and row["epoch"] == self._epoch
            and row["invocation_state"] == "claimed"
            and row["invocation_action"] == self.payload["action"]
            and row["request_id"] == self.payload["request_id"],
            "v3 live invocation is unavailable",
        )
        if kind == "discovery":
            _require(self._stage == "discovery", "v3 discovery callback is late")

    @contextmanager
    def _callback(self):
        with locked(self._lock):
            _require(
                self._running and not self._revoked, "v3 callback belongs to a revoked invocation"
            )
            self._callbacks += 1
        try:
            yield
        finally:
            with locked(self._lock):
                self._callbacks -= 1

    def _registered(self):
        return self.store.safe.control.cancellation._invocation_context(self._context)

    def _drive(self):
        with locked(self._lock):
            _require(
                not self._running
                and not self._returned
                and not self._revoked
                and self._secret is not None,
                "v3 invocation cannot be reconstructed or replayed",
            )
            self._running = True
        try:
            with self.dispatch.db.transaction():
                row, admission, _ = self._load()
                _require(
                    row["invocation_sha256"] == _hash(self._secret)
                    and row["invocation_state"] == "armed",
                    "v3 claim requires its live ticket",
                )
                self.dispatch._verify_files(row, admission)
                count = self.store.connection.execute(
                    f"UPDATE {HEADS} SET invocation_state='claimed' "
                    "WHERE operation_id=? AND epoch=? AND invocation_sha256=? "
                    "AND invocation_state='armed'",
                    (self.operation_id, self._epoch, _hash(self._secret)),
                ).rowcount
                _require(count == 1, "v3 invocation claim CAS differs")
                self.dispatch.db.boundary("after_claim")
            with self._registered():
                if self.payload["action"] == "dispatch":
                    from universal_coding_agent.discovered_safe_service import (
                        DiscoveredSafeAgentService,
                    )

                    service = DiscoveredSafeAgentService.create(
                        self.store.safe.artifacts.root.parent,
                        self.provider,
                        control=self.store.safe.control,
                        remote_operations=self.store.safe.remote_operations,
                    )
                    result = service.start_admitted(self)
                else:
                    with self.safe_service() as safe:
                        result = safe.resume(admission["thread_id"], self.payload["approved"])
            # Only this code observes the real outer return. A caller cannot supply
            # a checkpoint, elapsed interval or boolean to manufacture this fact.
            with locked(self._lock):
                self._result, self._returned = result, True
                self._stage = "returned"
            self.dispatch.db.boundary("after_outer_return")
        finally:
            with locked(self._lock):
                self._running, self._revoked = False, True
            if self._context is not None:
                self.store.safe.control.cancellation._revoke_invocation(self._context)
        return self.dispatch._seal(self)

    def _returned_proof(self):
        with locked(self._lock):
            _require(
                self._returned
                and self._revoked
                and not self._running
                and self._callbacks == 0
                and self._stage == "returned"
                and self._context is not None
                and self._context.revoked,
                "v3 live call has not positively settled",
            )

    def _settling(self, row):
        self._returned_proof()
        _require(
            row["invocation_sha256"] == _hash(self._secret)
            and row["epoch"] == self._epoch
            and row["invocation_state"] == "claimed"
            and row["request_id"] == self.payload["request_id"],
            "v3 settlement ticket differs",
        )

    def _result_state(self):
        self._returned_proof()
        result = self._result["state"] if self.payload["action"] == "dispatch" else self._result
        return {k: v for k, v in result.items() if k != "__interrupt__"}

    def discovery_request(self, service):
        with self.dispatch.db.transaction():
            row, admission, before = self._load()
            self._active(row, "discovery")
            _require(
                service.state_root == self.store.safe.artifacts.root.parent
                and service.control is self.store.safe.control
                and service.remote_operations is self.store.safe.remote_operations
                and service.provider is self.provider,
                "v3 discovery service host differs",
            )
            self.dispatch._verify_files(row, admission)
            phase = self.store._plan(before.identity).phases[before.generation]
            context = self.store._get(admission["dependency_sha256"]).decode()
            _require(
                self.store.programs.artifacts.read_text_bounded_verified(
                    admission["dependency_ref"],
                    expected_sha256=admission["dependency_sha256"],
                    max_bytes=48_000,
                )
                == context,
                "v3 dependency artifact changed",
            )
            return {
                "task_id": row["task_id"],
                "thread_id": row["thread_id"],
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

    def start_safe(self):
        with self.dispatch.db.transaction():
            row, admission, _ = self._load()
            self._active(row)
            _require(
                row["state"] == "discovered" and self._stage == "discovered",
                "v3 Safe initialization cannot be repeated",
            )
            self.dispatch._verify_files(row, admission)
            _require(
                self.store.connection.execute(
                    "SELECT 1 FROM safe.checkpoints WHERE thread_id=? LIMIT 1",
                    (admission["thread_id"],),
                ).fetchone()
                is None,
                "v3 Safe thread already exists",
            )
            self.dispatch._state(
                self.operation_id, "discovered", "safe_started", owner_token=self.owner_token
            )
            self._stage = "safe"

    def entry(self, thread_id, task_id, action):
        with self.dispatch.db.transaction():
            row, admission, _ = self._load()
            self._active(row)
            _require(
                not self._safe_entered
                and thread_id == row["thread_id"]
                and (
                    (
                        action == "run"
                        and task_id == row["task_id"]
                        and self._stage == "safe"
                        and self.payload["action"] == "dispatch"
                        and row["state"] == "safe_started"
                    )
                    or (
                        action == "resume"
                        and task_id is None
                        and self._stage == "resume"
                        and self.payload["action"] == "approve_scope"
                        and row["state"] == "resume_started"
                    )
                ),
                "v3 Safe entry is not its exact explicit action",
            )
            self.dispatch._verify_files(row, admission)
            self._safe_entered = True

    def node(self, name, state, action):
        with self._callback(), self._registered():
            with locked(self._lock):
                _require(self._node_name is None, "v3 node callback overlaps another node")
                self._node_name, self._rollback_authority = name, None
            try:
                result = self._node(name, state, action)
                self.dispatch.db.boundary("after_node_" + name)
                return result
            finally:
                with locked(self._lock):
                    self._node_name, self._rollback_authority = None, None

    def _path(self):
        row, admission, _ = self._load()
        self._active(row)
        self.dispatch._verify_files(row, admission)
        return (
            self.dispatch.preparation.filesystem.root / ("execution-" + self.operation_id) / "repo"
        )

    def task(self):
        return SafeTaskRequest.model_validate(
            self.dispatch._json(self.dispatch._row(self.operation_id)["task_sha256"])
        )

    def prepare(self, task_id, repository):
        with self._callback(), self.dispatch.db.transaction():
            row, admission, _ = self._load()
            self._active(row)
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
        with self._callback(), self.dispatch.db.transaction():
            _require(path == self._path(), "discovery destination differs")
        return [{"name": "admitted_complete_source_and_git", "passed": True}]

    def discovery_completed(self, task):
        with self.dispatch.db.transaction():
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
                "bounded v3 discovery permits existing-file modifications only",
            )
            task = task.model_copy(
                update={
                    "metadata": {
                        **task.metadata,
                        "execution_schema": "uca-program-source-dispatch-3",
                        "admission_sha256": row["admission_sha256"],
                    }
                }
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
                owner_token=self.owner_token,
                task_sha256=self.store._put(_canonical(task.model_dump(mode="json"))),
                discovery_sha256=self.store._put(_canonical(captured)),
            )

            self._stage = "discovered"
            self.dispatch.db.boundary("after_discovery")
            return task

    def safe_service(self):
        from contextlib import contextmanager

        @contextmanager
        def opened():
            safe = SafeAgentService.create(
                self.store.safe.artifacts.root.parent,
                self.provider,
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
        with self.dispatch.db.transaction():
            row, _, _ = self._load()
            self._active(row)
        _require(state_root == self.store.safe.artifacts.root.parent, "Safe adapter host differs")

        # Bind read-only Git to the isolated bounded runner, including optional-lock suppression.
        # These are fresh v3 service instances; legacy engines and helpers are not modified.
        def git(root, arguments, *, check=True):
            attestor = self._attestor(root)
            budget = _GitBudget(
                time.monotonic() + attestor.policy.operation_timeout_seconds,
                attestor.policy.max_git_output_bytes,
            )
            with self._callback():
                result = attestor._run_result(
                    tuple(arguments),
                    b"",
                    budget,
                    expected_returncodes=(0,) if check else tuple(range(256)),
                )
            result.stdout = result.stdout.decode("utf-8")
            result.stderr = result.stderr.decode("utf-8")
            return result

        apply = services.edit_engine.apply

        def apply_owned(sandbox, manifest, proposal):
            _require(
                self._running and not self._revoked and self._node_name == "apply_edits",
                "v3 edit callback has no live apply node",
            )
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
        _require(
            self._stage in {"safe", "resume"} and not self._revoked,
            "v3 service requires its live stage",
        )
        self.services = replace(services, sandbox=self, execution_boundary=self)
        return self.services

    def _restore(self, sandbox, manifest, changed_paths):
        """Restore exact approved Base bytes without Git's index/lock side effects."""
        from contextlib import ExitStack

        with self.dispatch.db.transaction():
            _require(self._node_name in {"apply_edits", "finalize"}, "v3 rollback has no live node")
            row, admission, before = self._load()
            self._active(row, "safe" if row["state"] == "safe_started" else "resume")
            destination = (
                self.dispatch.preparation.filesystem.root
                / ("execution-" + self.operation_id)
                / "repo"
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
                                parts[-1],
                                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                                dir_fd=parent,
                            )
                            try:
                                info = os.fstat(fd)
                                expected = self.dispatch._json(row["filesystem_sha256"])["entries"][
                                    path
                                ]
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
                                    _stamp(info)
                                    == _stamp(os.fstat(fd))
                                    == _stamp(
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
                                _stamp(info)[:5] == expected[:5] and info.st_nlink == 1,
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
                """UPDATE program_source_continuation_heads_v3 SET filesystem_sha256 = ?,
                retained_sha256 = ? WHERE operation_id = ?""",
                (
                    self.store._put(proof),
                    self.store._put(self.store.source.snapshot_bytes(before)),
                    self.operation_id,
                ),
            )
            self.dispatch._refresh_authority(self.operation_id, self.owner_token)
            self._rollback_authority = self.dispatch._row(self.operation_id)["authority_sha256"]
            return True

    def discovery_indexer(self):
        from universal_coding_agent.repository.indexer import RepositoryIndexer

        with self.dispatch.db.transaction():
            row, _, _ = self._load()
            self._active(row, "discovery")
        indexer = RepositoryIndexer()

        def git(root, *args):
            attestor = self._attestor(root)
            with self._callback():
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

    def _node(self, name, state, action):
        from langgraph.errors import GraphInterrupt

        with self.dispatch.db.transaction():
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
            with self.dispatch.db.transaction():
                row, admission, _ = self._load()
                self.dispatch._verify_files(row, admission)
            raise
        with self.dispatch.db.transaction():
            completes = name == "finalize" and result.get("status") == "completed"
            row, admission, _ = self._load(after_finalize=completes)
            _require(
                row["authority_sha256"] in {input_authority, self._rollback_authority},
                "concurrent Safe invocation changed",
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
                    """UPDATE program_source_continuation_heads_v3
                    SET filesystem_sha256 = ?, retained_sha256 = ? WHERE operation_id = ?""",
                    (
                        self.store._put(proof),
                        self.store._put(self.store.source.snapshot_bytes(current)),
                        self.operation_id,
                    ),
                )
            if current is not None or completes:
                self.dispatch._refresh_authority(self.operation_id, self.owner_token)
        return result
