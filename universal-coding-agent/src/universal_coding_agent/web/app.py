from __future__ import annotations

import ipaddress
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import SafeModePolicy
from universal_coding_agent.product.context_documents import DocumentValidationError
from universal_coding_agent.product.models import ContextScope, DocumentRole, RequirementContract
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.safety.sanitizer import sanitize_text


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=20, ge=1, le=100)


class DocumentUploadRequest(BaseModel):
    document_id: str
    filename: str
    content: str
    role: DocumentRole
    scope: ContextScope
    scope_id: str


class RequirementAnalyzeRequest(BaseModel):
    alignment_id: str
    title: str
    objective: str
    answers: dict[str, str] = Field(default_factory=dict)
    previous: RequirementContract | None = None


class RequirementApproveRequest(BaseModel):
    contract: RequirementContract


class ProgramCreateRequest(BaseModel):
    program_id: str
    requirement: RequirementContract
    requirement_hash: str


class ProgramApproveRequest(BaseModel):
    plan_hash: str


class ControlRequest(BaseModel):
    reason: str = ""


class ScopeDecisionRequest(BaseModel):
    approved: bool


class SafeTaskStartRequest(BaseModel):
    task_id: str | None = None
    thread_id: str | None = None
    title: str = "Safe task"
    objective: str = Field(min_length=1, max_length=20_000)
    repository: str
    ref: str
    policy: SafeModePolicy
    test_profiles: tuple[str, ...]
    acceptance_criteria: tuple[str, ...] = ()


@dataclass
class ProductWebRuntime:
    workspace: ProductWorkspace
    state_root: Path
    allow_local_sources: bool = False
    executor: ThreadPoolExecutor = field(
        default_factory=lambda: ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="uca-web",
        )
    )
    _runs: dict[str, dict[str, Any]] = field(default_factory=dict)
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def close(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.workspace.close()

    def start_safe_task(self, request: SafeTaskStartRequest) -> dict[str, Any]:
        task_id = request.task_id or f"safe-ui-{uuid.uuid4().hex[:16]}"
        thread_id = request.thread_id or task_id
        with self._lock:
            if task_id in self._runs:
                raise ValueError(f"task already exists: {task_id}")
            self.workspace.control.ensure_task(task_id)
            self._runs[task_id] = {
                "task_id": task_id,
                "thread_id": thread_id,
                "title": request.title,
                "status": "queued",
                "busy": True,
            }
        self.executor.submit(self._start_safe_worker, task_id, thread_id, request)
        return self.task_status(task_id)

    def task_status(self, task_id: str) -> dict[str, Any]:
        with self._lock:
            record = dict(self._runs.get(task_id, {}))
        control = self.workspace.control.get_task(task_id)
        if not record and control is None:
            raise KeyError(task_id)
        if control is not None:
            record["control"] = control.model_dump(mode="json")
        return record

    def scope_decision(self, task_id: str, approved: bool) -> dict[str, Any]:
        with self._lock:
            record = self._runs.get(task_id)
            if record is None:
                raise KeyError(task_id)
            if record.get("busy"):
                raise ValueError("task is currently executing")
            thread_id = str(record["thread_id"])
            record["busy"] = True
            record["status"] = "scope_approved" if approved else "scope_rejected"
        self.executor.submit(self._resume_safe_worker, task_id, thread_id, approved)
        return self.task_status(task_id)

    def pause_task(self, task_id: str, reason: str = "") -> dict[str, Any]:
        self._require_run(task_id)
        self.workspace.control.pause_task(task_id, reason=reason)
        return self.task_status(task_id)

    def resume_task(self, task_id: str) -> dict[str, Any]:
        self._require_run(task_id)
        self.workspace.control.resume_task(task_id)
        return self.task_status(task_id)

    def cancel_task(self, task_id: str, reason: str = "") -> dict[str, Any]:
        self._require_run(task_id)
        self.workspace.control.cancel_task(task_id, reason=reason)
        return self.task_status(task_id)

    def _require_run(self, task_id: str) -> None:
        with self._lock:
            if task_id not in self._runs:
                raise KeyError(task_id)

    def _start_safe_worker(
        self,
        task_id: str,
        thread_id: str,
        request: SafeTaskStartRequest,
    ) -> None:
        try:
            control = self.workspace.control.task_action(task_id)
            if control.value == "cancel":
                self._set_run(task_id, status="cancelled", busy=False)
                return
            if control.value == "pause":
                self._set_run(task_id, status="paused", busy=False)
                return
            service = self.workspace.discovered_safe(
                state_root=self.state_root / "safe",
                allow_local_sources=self.allow_local_sources,
            )
            result = service.start(
                task_id=task_id,
                thread_id=thread_id,
                title=request.title,
                objective=request.objective,
                repository=RepositorySpec(
                    url=request.repository,
                    base_ref=request.ref,
                ),
                policy=request.policy,
                test_profiles=request.test_profiles,
                acceptance_criteria=request.acceptance_criteria,
            )
            state = result.get("state", {})
            self._set_run(
                task_id,
                status=str(state.get("status", "awaiting_scope_approval")),
                busy=False,
                result=result,
            )
        except Exception as exc:  # execution errors become bounded task state
            self._set_run(
                task_id,
                status="failed",
                busy=False,
                error_type=type(exc).__name__,
                error=sanitize_text(str(exc))[:2000],
            )

    def _resume_safe_worker(self, task_id: str, thread_id: str, approved: bool) -> None:
        try:
            service = self.workspace.discovered_safe(
                state_root=self.state_root / "safe",
                allow_local_sources=self.allow_local_sources,
            )
            result = service.resume(thread_id, approved)
            self._set_run(
                task_id,
                status=str(result.get("status", "completed")),
                busy=False,
                result=result,
            )
        except Exception as exc:
            self._set_run(
                task_id,
                status="failed",
                busy=False,
                error_type=type(exc).__name__,
                error=sanitize_text(str(exc))[:2000],
            )

    def _set_run(self, task_id: str, **changes: Any) -> None:
        with self._lock:
            record = self._runs.setdefault(task_id, {"task_id": task_id})
            record.update(changes)


def create_product_app(
    runtime: ProductWebRuntime,
    *,
    ui_dist: Path | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        runtime.close()

    app = FastAPI(
        title="Universal Coding Agent Control API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.exception_handler(DocumentValidationError)
    async def document_error(_request: Request, exc: DocumentValidationError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(KeyError)
    async def key_error(_request: Request, exc: KeyError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc.args[0])},
        )

    @app.exception_handler(ValueError)
    async def value_error(_request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"detail": sanitize_text(str(exc))[:2000]},
        )

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "api": "uca-product-control",
            "browser_credentials": False,
            "allow_local_sources": runtime.allow_local_sources,
        }

    @app.post("/api/search")
    def search(request: SearchRequest) -> dict[str, Any]:
        hits = runtime.workspace.search.search(request.query, top_k=request.top_k)
        return {"hits": [item.model_dump(mode="json") for item in hits]}

    @app.get("/api/documents")
    def list_documents(scope_id: str | None = None) -> dict[str, Any]:
        documents = runtime.workspace.documents.list(scope_id=scope_id)
        return {
            "documents": [
                item.model_dump(mode="json")
                for item in documents
            ]
        }

    @app.post("/api/documents", status_code=201)
    def upload_document(request: DocumentUploadRequest) -> dict[str, Any]:
        document = runtime.workspace.upload_document(
            document_id=request.document_id,
            filename=request.filename,
            content=request.content,
            role=request.role,
            scope=request.scope,
            scope_id=request.scope_id,
        )
        return document.model_dump(mode="json")

    @app.post("/api/requirements/analyze")
    def analyze_requirement(request: RequirementAnalyzeRequest) -> dict[str, Any]:
        result = runtime.workspace.requirements.analyze(
            alignment_id=request.alignment_id,
            title=request.title,
            objective=request.objective,
            answers=request.answers,
            previous=request.previous,
        )
        return result.model_dump(mode="json")

    @app.post("/api/requirements/approve")
    def approve_requirement(request: RequirementApproveRequest) -> dict[str, Any]:
        result = runtime.workspace.requirements.approve(request.contract)
        return result.model_dump(mode="json")

    @app.post("/api/programs", status_code=201)
    def create_program(request: ProgramCreateRequest) -> dict[str, Any]:
        plan = runtime.workspace.programs.create_program(
            program_id=request.program_id,
            requirement=request.requirement,
            requirement_hash=request.requirement_hash,
        )
        return _program_snapshot(runtime.workspace, plan.program_id)

    @app.get("/api/programs/{program_id}")
    def program_status(program_id: str) -> dict[str, Any]:
        return _program_snapshot(runtime.workspace, program_id)

    @app.post("/api/programs/{program_id}/approve")
    def approve_program(
        program_id: str,
        request: ProgramApproveRequest,
    ) -> dict[str, Any]:
        runtime.workspace.programs.approve_program(program_id, request.plan_hash)
        return _program_snapshot(runtime.workspace, program_id)

    @app.post("/api/programs/{program_id}/pause")
    def pause_program(
        program_id: str,
        request: ControlRequest,
    ) -> dict[str, Any]:
        runtime.workspace.programs.pause(program_id, reason=request.reason)
        runtime.workspace.programs.ready_phases(program_id)
        return _program_snapshot(runtime.workspace, program_id)

    @app.post("/api/programs/{program_id}/resume")
    def resume_program(program_id: str) -> dict[str, Any]:
        runtime.workspace.programs.resume(program_id)
        return _program_snapshot(runtime.workspace, program_id)

    @app.post("/api/programs/{program_id}/cancel")
    def cancel_program(
        program_id: str,
        request: ControlRequest,
    ) -> dict[str, Any]:
        runtime.workspace.programs.cancel(program_id, reason=request.reason)
        return _program_snapshot(runtime.workspace, program_id)

    @app.post("/api/tasks/safe", status_code=202)
    def start_safe_task(request: SafeTaskStartRequest) -> dict[str, Any]:
        if not request.test_profiles:
            raise HTTPException(
                status_code=422,
                detail="at least one trusted test profile is required",
            )
        return runtime.start_safe_task(request)

    @app.get("/api/tasks/{task_id}")
    def task_status(task_id: str) -> dict[str, Any]:
        return runtime.task_status(task_id)

    @app.post("/api/tasks/{task_id}/scope-decision", status_code=202)
    def scope_decision(
        task_id: str,
        request: ScopeDecisionRequest,
    ) -> dict[str, Any]:
        return runtime.scope_decision(task_id, request.approved)

    @app.post("/api/tasks/{task_id}/pause")
    def pause_task(task_id: str, request: ControlRequest) -> dict[str, Any]:
        return runtime.pause_task(task_id, request.reason)

    @app.post("/api/tasks/{task_id}/resume")
    def resume_task(task_id: str) -> dict[str, Any]:
        return runtime.resume_task(task_id)

    @app.post("/api/tasks/{task_id}/cancel")
    def cancel_task(task_id: str, request: ControlRequest) -> dict[str, Any]:
        return runtime.cancel_task(task_id, request.reason)

    resolved_ui = ui_dist.resolve() if ui_dist is not None else None
    if resolved_ui is not None and resolved_ui.is_dir():
        app.mount(
            "/",
            StaticFiles(directory=resolved_ui, html=True),
            name="ui",
        )
    else:

        @app.get("/")
        def api_root() -> dict[str, str]:
            return {
                "service": "Universal Coding Agent Control API",
                "ui": "not-built",
                "hint": "build web/ and restart with --ui-dist web/dist",
            }

    return app


def is_loopback_host(host: str) -> bool:
    if host.strip().lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _program_snapshot(
    workspace: ProductWorkspace,
    program_id: str,
) -> dict[str, Any]:
    plan = workspace.programs.plan(program_id)
    return {
        "program_id": program_id,
        "status": workspace.programs.status(program_id).value,
        "plan_hash": plan.canonical_hash(),
        "plan": plan.model_dump(mode="json"),
        "phases": [
            {
                "phase_id": phase.phase_id,
                "title": phase.title,
                "status": workspace.programs.phase_status(
                    program_id,
                    phase.phase_id,
                ).value,
                "dependencies": list(phase.dependencies),
            }
            for phase in plan.phases
        ],
    }
