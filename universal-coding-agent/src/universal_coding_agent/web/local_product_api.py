"""Loopback-only typed local Product API; synchronous effects and pure reads."""

from __future__ import annotations

import ipaddress
import re

from fastapi import APIRouter, Request
from starlette.concurrency import run_in_threadpool
from starlette.responses import Response

from universal_coding_agent.product.local_product_binding import (
    COMMANDS,
    MAX_BODY,
    LocalProductError,
    check,
    command_payload,
    digest,
    identifier,
    local_authority,
)
from universal_coding_agent.product.program_continuation_execution_store import canonical

PREFIX = "/api/local-product/v1/projects/{project_id}"
PROGRAM = PREFIX + "/programs/{program_id}"


def response(status, raw):
    return Response(
        raw,
        status_code=status,
        media_type="application/json",
        headers={"Cache-Control": "no-store"},
    )


def boundary(request, origin):
    headers = request.scope.get("headers", [])

    def values(key):
        return [value.decode("latin-1") for name, value in headers if name.lower() == key]

    peer = request.scope.get("client")
    try:
        local = peer is not None and ipaddress.ip_address(peer[0]).is_loopback
    except ValueError:
        local = False
    check(local and values(b"host") == [local_authority(origin)], "local_boundary_denied")
    origins = values(b"origin")
    check(not origins or origins == [origin], "local_boundary_denied")
    if request.method == "POST":
        check(
            values(b"x-uca-command") == ["1"] and values(b"content-type") == ["application/json"],
            "local_boundary_denied",
        )


async def body(request):
    raw = bytearray()
    for value in request.headers.getlist("content-length"):
        check(re.fullmatch(r"[0-9]{1,10}", value) is not None, "invalid_command")
        check(int(value) <= MAX_BODY, "request_too_large")
    async for chunk in request.stream():
        check(len(raw) + len(chunk) <= MAX_BODY, "request_too_large")
        raw.extend(chunk)
    return bytes(raw)


def install(app, runtime, binding=None, *, enabled=False):
    from universal_coding_agent.product.local_product_status import (
        evidence,
        project_result,
        recorded_request,
        status,
    )

    router = APIRouter()
    host = runtime.local_product_host
    configured = binding is not None
    origin = binding.value["local_origin"] if configured else None
    path = runtime.workspace.programs.database_path

    async def handle(request, mode, action=None):
        project = program = request_id = None
        try:
            if not configured:
                raise LocalProductError("local_commands_disabled")
            boundary(request, origin)
            project = identifier(request.path_params["project_id"])
            if "program_id" in request.path_params:
                program = identifier(request.path_params["program_id"])
            raw = await body(request)
            if mode == "command":
                check(enabled and host is not None, "local_commands_disabled")
                check(not request.query_params, "invalid_command")
                target = request.path_params.get("target_request_id")
                payload = command_payload(raw, project, program, action, target)
                request_id = payload["request_id"]
                code, result = await run_in_threadpool(host.execute, payload)
                return response(code, result)
            check(not raw, "invalid_command")
            allowed = {
                "status": {"after_sequence", "limit"},
                "operation": {"after_sequence", "limit"},
                "evidence": {"after_chunk", "limit"},
            }.get(mode, set())
            items = request.query_params.multi_items()
            check(
                len(items) == len({k for k, _ in items}) and set(request.query_params) <= allowed,
                "invalid_command",
            )
            query = {}
            for key, value in items:
                check(re.fullmatch(r"0|[1-9][0-9]{0,15}", value) is not None, "invalid_command")
                query[key] = int(value)
                check(query[key] <= 2**53 - 1, "invalid_command")
            if "limit" in query:
                check(1 <= query["limit"] <= (16 if mode == "evidence" else 100), "invalid_command")
            if mode == "project":
                value = await run_in_threadpool(project_result, path, project, enabled=enabled)
            elif mode == "request":
                request_id = identifier(request.path_params["request_id"])
                code, result = await run_in_threadpool(
                    recorded_request, path, project, program, request_id
                )
                return response(code, result)
            elif mode == "evidence":
                view = digest(request.path_params["evidence_view_sha256"])
                value = await run_in_threadpool(evidence, path, project, program, view, **query)
            else:
                operation = request.path_params.get("operation_id")
                if operation:
                    check(re.fullmatch(r"[0-9a-f]{32}", operation) is not None, "invalid_command")
                value = await run_in_threadpool(
                    status, path, project, program, operation=operation, **query
                )
            return response(200, canonical(value))
        except LocalProductError as exc:
            return response(exc.status, canonical(exc.envelope(project, program, request_id)))
        except Exception:
            error = LocalProductError("recorded_evidence_invalid")
            return response(error.status, canonical(error.envelope(project, program, request_id)))

    for suffix, (action, _) in COMMANDS.items():
        route = PROGRAM + (
            "/requests/{target_request_id}/reconcile" if suffix == "reconcile" else "/" + suffix
        )

        def make_command(action):
            async def command(request: Request):
                return await handle(request, "command", action)

            return command

        router.add_api_route(route, make_command(action), methods=["POST"], name="local_" + action)
    for route, mode in (
        (PREFIX, "project"),
        (PROGRAM, "status"),
        (PROGRAM + "/operations/{operation_id}", "operation"),
        (PROGRAM + "/requests/{request_id}", "request"),
        (PROGRAM + "/evidence/{evidence_view_sha256}", "evidence"),
    ):

        def make_read(mode):
            async def read(request: Request):
                return await handle(request, mode)

            return read

        router.add_api_route(route, make_read(mode), methods=["GET"], name="local_" + mode)
    app.include_router(router)

    @app.middleware("http")
    async def local_response_boundary(request, call_next):
        if not request.url.path.startswith("/api/local-product/"):
            return await call_next(request)
        try:
            check(configured, "local_commands_disabled")
            boundary(request, origin)
            check(request.method in {"GET", "POST"}, "invalid_command")
            result = await call_next(request)
            check(
                result.status_code != 405
                and (
                    result.status_code != 404 or result.headers.get("Cache-Control") == "no-store"
                ),
                "invalid_command",
            )
            result.headers["Cache-Control"] = "no-store"
            return result
        except LocalProductError as exc:
            return response(exc.status, canonical(exc.envelope()))
        except Exception:
            error = LocalProductError("recorded_evidence_invalid")
            return response(error.status, canonical(error.envelope()))

    if enabled:

        @app.middleware("http")
        async def legacy_boundary(request, call_next):
            if request.method == "POST" and not request.url.path.startswith("/api/local-product/"):
                try:
                    boundary(request, origin)
                except LocalProductError as exc:
                    return response(exc.status, canonical(exc.envelope()))
            return await call_next(request)
