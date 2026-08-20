from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec, TaskMode, TaskRequest
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    SafeModePolicy,
    SafeTaskRequest,
)
from universal_coding_agent.discovered_safe_service import DiscoveredSafeAgentService
from universal_coding_agent.providers.external import load_provider
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.service import AgentService


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="uca", description="Universal Coding Agent")
    root.add_argument("--state-root", type=Path, default=Path(".uca-state"))
    root.add_argument("--provider-factory")
    root.add_argument(
        "--allow-local-sources",
        action="store_true",
        help="allow controlled local Git repository paths explicitly",
    )
    sub = root.add_subparsers(dest="command", required=True)

    sub.add_parser("probe")

    observe = sub.add_parser("observe")
    observe.add_argument("--repository", required=True)
    observe.add_argument("--ref", required=True)
    observe.add_argument("--task-file", type=Path, required=True)
    observe.add_argument("--title")
    observe.add_argument("--task-id")
    observe.add_argument("--thread-id")
    observe.add_argument("--require-plan-approval", action="store_true")

    resume = sub.add_parser("resume")
    resume.add_argument("--thread-id", required=True)
    resume.add_argument("--decision", choices=("approve", "reject"), required=True)

    status = sub.add_parser("status")
    status.add_argument("--thread-id", required=True)

    safe = sub.add_parser("safe")
    safe.add_argument("--repository", required=True)
    safe.add_argument("--ref", required=True)
    safe.add_argument("--task-file", type=Path, required=True)
    safe.add_argument("--scope-file", type=Path, required=True)
    safe.add_argument("--policy-file", type=Path, required=True)
    safe.add_argument("--title")
    safe.add_argument("--task-id")
    safe.add_argument("--thread-id")

    safe_auto = sub.add_parser("safe-auto")
    safe_auto.add_argument("--repository", required=True)
    safe_auto.add_argument("--ref", required=True)
    safe_auto.add_argument("--task-file", type=Path, required=True)
    safe_auto.add_argument("--policy-file", type=Path, required=True)
    safe_auto.add_argument(
        "--test-profile",
        action="append",
        required=True,
        dest="test_profiles",
        help="trusted policy test profile; repeat for multiple profiles",
    )
    safe_auto.add_argument(
        "--acceptance-file",
        type=Path,
        help="optional JSON array of human-provided acceptance criteria",
    )
    safe_auto.add_argument("--title")
    safe_auto.add_argument("--task-id")
    safe_auto.add_argument("--thread-id")

    safe_resume = sub.add_parser("safe-resume")
    safe_resume.add_argument("--thread-id", required=True)
    safe_resume.add_argument("--decision", choices=("approve", "reject"), required=True)

    safe_status = sub.add_parser("safe-status")
    safe_status.add_argument("--thread-id", required=True)

    serve = sub.add_parser("serve", help="run the local UCA Product Control API and UI")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--ui-dist", type=Path, default=Path("web/dist"))
    serve.add_argument(
        "--allow-remote-ui",
        action="store_true",
        help="explicitly allow binding the UI/API to a non-loopback address",
    )
    return root


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    provider = load_provider(arguments.provider_factory)
    if arguments.command == "probe":
        if not provider.probe():
            print("AGENT_MODEL_PROVIDER_FAIL", file=sys.stderr)
            return 1
        print("AGENT_MODEL_PROVIDER_OK")
        return 0

    if arguments.command == "serve":
        return _run_server(arguments, provider)
    if arguments.command in {"safe", "safe-auto", "safe-resume", "safe-status"}:
        return _run_safe(arguments, provider)
    return _run_observe(arguments, provider)


def _run_observe(arguments: argparse.Namespace, provider) -> int:
    service = AgentService.create(
        arguments.state_root,
        provider,
        allow_local_sources=arguments.allow_local_sources,
    )
    try:
        if arguments.command == "observe":
            objective = arguments.task_file.read_text(encoding="utf-8")
            task_id = arguments.task_id or f"task-{uuid.uuid4().hex[:16]}"
            thread_id = arguments.thread_id or task_id
            task = TaskRequest(
                task_id=task_id,
                thread_id=thread_id,
                title=arguments.title or arguments.task_file.stem,
                objective=objective,
                repository=RepositorySpec(url=arguments.repository, base_ref=arguments.ref),
                mode=TaskMode.OBSERVE,
                require_plan_approval=arguments.require_plan_approval,
            )
            result = service.run(task)
        elif arguments.command == "resume":
            result = service.resume(arguments.thread_id, arguments.decision == "approve")
        else:
            result = service.state(arguments.thread_id)
        print(json.dumps(result, indent=2, default=str))
        return 0
    finally:
        service.close()


def _run_safe(arguments: argparse.Namespace, provider) -> int:
    if arguments.command == "safe-auto":
        return _run_discovered_safe(arguments, provider)

    service = SafeAgentService.create(
        arguments.state_root,
        provider,
        allow_local_sources=arguments.allow_local_sources,
    )
    try:
        if arguments.command == "safe":
            objective = arguments.task_file.read_text(encoding="utf-8")
            scope_payload = json.loads(arguments.scope_file.read_text(encoding="utf-8"))
            policy_payload = json.loads(arguments.policy_file.read_text(encoding="utf-8"))
            task_id = arguments.task_id or f"safe-{uuid.uuid4().hex[:16]}"
            thread_id = arguments.thread_id or task_id
            task = SafeTaskRequest(
                task_id=task_id,
                thread_id=thread_id,
                title=arguments.title or arguments.task_file.stem,
                objective=objective,
                repository=RepositorySpec(url=arguments.repository, base_ref=arguments.ref),
                manifest=ApprovedChangeManifest.model_validate(scope_payload),
                policy=SafeModePolicy.model_validate(policy_payload),
            )
            result = service.run(task)
        elif arguments.command == "safe-resume":
            result = service.resume(arguments.thread_id, arguments.decision == "approve")
        else:
            result = service.state(arguments.thread_id)
        print(json.dumps(result, indent=2, default=str))
        return 0
    finally:
        service.close()


def _run_discovered_safe(arguments: argparse.Namespace, provider) -> int:
    objective = arguments.task_file.read_text(encoding="utf-8")
    policy_payload = json.loads(arguments.policy_file.read_text(encoding="utf-8"))
    policy = SafeModePolicy.model_validate(policy_payload)
    criteria = _load_acceptance_criteria(arguments.acceptance_file, objective)
    task_id = arguments.task_id or f"safe-auto-{uuid.uuid4().hex[:16]}"
    thread_id = arguments.thread_id or task_id
    service = DiscoveredSafeAgentService.create(
        arguments.state_root,
        provider,
        allow_local_sources=arguments.allow_local_sources,
    )
    result = service.start(
        task_id=task_id,
        thread_id=thread_id,
        title=arguments.title or arguments.task_file.stem,
        objective=objective,
        repository=RepositorySpec(url=arguments.repository, base_ref=arguments.ref),
        policy=policy,
        test_profiles=tuple(arguments.test_profiles),
        acceptance_criteria=criteria,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0


def _run_server(arguments: argparse.Namespace, provider) -> int:
    import uvicorn

    from universal_coding_agent.product.workspace import ProductWorkspace
    from universal_coding_agent.web.app import ProductWebRuntime, create_product_app, is_loopback_host

    if not is_loopback_host(arguments.host) and not arguments.allow_remote_ui:
        raise ValueError(
            "refusing non-loopback UI bind; pass --allow-remote-ui only behind approved access controls"
        )
    if arguments.port < 1 or arguments.port > 65535:
        raise ValueError("port must be between 1 and 65535")

    state_root = arguments.state_root.resolve()
    workspace = ProductWorkspace.create(state_root / "product", provider)
    runtime = ProductWebRuntime(
        workspace=workspace,
        state_root=state_root / "web-runtime",
        allow_local_sources=arguments.allow_local_sources,
    )
    app = create_product_app(runtime, ui_dist=arguments.ui_dist)
    uvicorn.run(app, host=arguments.host, port=arguments.port, log_level="info")
    return 0


def _load_acceptance_criteria(path: Path | None, objective: str) -> tuple[str, ...]:
    if path is None:
        return (objective,)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("acceptance file must contain a non-empty JSON array")
    criteria: list[str] = []
    for item in payload:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("acceptance criteria must be non-empty strings")
        criteria.append(item.strip())
    return tuple(criteria)


if __name__ == "__main__":
    raise SystemExit(main())
