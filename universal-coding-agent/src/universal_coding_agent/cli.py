from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec, TaskMode, TaskRequest
from universal_coding_agent.providers.external import load_provider
from universal_coding_agent.service import AgentService


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="uca", description="Universal Coding Agent")
    root.add_argument("--state-root", type=Path, default=Path(".uca-state"))
    root.add_argument("--provider-factory")
    root.add_argument(
        "--allow-local-sources",
        action="store_true",
        help="allow local repository paths explicitly; intended for controlled smoke tests",
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


if __name__ == "__main__":
    raise SystemExit(main())
