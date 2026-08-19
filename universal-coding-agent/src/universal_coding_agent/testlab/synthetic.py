from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from universal_coding_agent.core.models import RepositorySpec, ReviewVerdict
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    FileEdit,
    SafeModePolicy,
    SafeReviewResult,
    SafeTaskRequest,
    StructuredEditProposal,
    TestProfile,
    TextReplacement,
)
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe_service import SafeAgentService

Position = Literal["replace", "before", "after"]


@dataclass(frozen=True)
class SyntheticChange:
    path: str
    operation: ChangeOperation
    new_text: str
    line_number: int | None = None
    position: Position = "replace"
    invalid_initial_address: bool = False
    invalid_correction_address: bool = False
    wrong_path: str | None = None


@dataclass(frozen=True)
class SyntheticScenario:
    scenario_id: str
    title: str
    initial_files: dict[str, str]
    changes: tuple[SyntheticChange, ...]
    expected_status: str = "completed"
    expected_safe_error: str | None = None
    force_test_failure: bool = False
    reviewer_verdict: ReviewVerdict = ReviewVerdict.PASS


@dataclass(frozen=True)
class SyntheticRunResult:
    report: dict
    source: Path
    sandbox: Path
    expected_files: dict[str, str]
    source_head_before: str
    source_head_after: str
    source_status_after: str
    phases: tuple[tuple[str, str], ...]


class ScenarioProvider(FakeModelProvider):
    def __init__(self, scenario: SyntheticScenario) -> None:
        self.scenario = scenario
        self.phases: list[tuple[str, str]] = []
        super().__init__(
            handlers={
                "implementer": self._implementer,
                "reviewer": self._reviewer,
            }
        )

    def _implementer(self, request):
        target = str(request.metadata.get("target_path"))
        phase = str(request.metadata.get("shard_phase"))
        self.phases.append((target, phase))
        change = next(item for item in self.scenario.changes if item.path == target)

        edit_path = change.wrong_path or change.path
        if change.operation is ChangeOperation.CREATE:
            edit = FileEdit(
                path=edit_path,
                operation=ChangeOperation.CREATE,
                content=change.new_text,
            )
        else:
            if change.line_number is None:
                raise AssertionError(f"modify scenario is missing line_number: {change.path}")
            invalid = (
                change.invalid_initial_address
                if phase == "initial"
                else change.invalid_correction_address
            )
            token = self._token(change, invalid=invalid)
            edit = FileEdit(
                path=edit_path,
                operation=ChangeOperation.MODIFY,
                replacements=(
                    TextReplacement(
                        old_text=token,
                        new_text=change.new_text,
                    ),
                ),
            )

        return StructuredEditProposal(
            summary=f"Synthetic pre-transfer edit for {target}.",
            edits=(edit,),
            requested_test_profiles=("synthetic-check",),
        ).model_dump(mode="json")

    def _reviewer(self, _request):
        actions = (
            ("Synthetic reviewer intentionally rejected the change.",)
            if self.scenario.reviewer_verdict is ReviewVerdict.FAIL
            else ()
        )
        return SafeReviewResult(
            verdict=self.scenario.reviewer_verdict,
            requirement_findings=("Synthetic acceptance evidence reviewed.",),
            required_actions=actions,
            confidence="high",
        ).model_dump(mode="json")

    @staticmethod
    def _token(change: SyntheticChange, *, invalid: bool) -> str:
        if invalid:
            anchor = "A999999"
        else:
            assert change.line_number is not None
            anchor = f"A{change.line_number:06d}"
        if change.position == "before":
            return f"@before:{anchor}"
        if change.position == "after":
            return f"@after:{anchor}"
        return f"@range:{anchor}..{anchor}"


def run_synthetic_scenario(root: Path, scenario: SyntheticScenario) -> SyntheticRunResult:
    source = root / "source"
    state_root = root / "state"
    source.mkdir(parents=True)
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "pretransfer@example.test")
    _git(source, "config", "user.name", "Pre-transfer Test Lab")
    for relative, content in scenario.initial_files.items():
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="")
    _git(source, "add", "-A")
    _git(source, "commit", "-m", "synthetic fixture")
    source_head_before = _git(source, "rev-parse", "HEAD")

    expected_files = _expected_files(scenario)
    manifest = ApprovedChangeManifest(
        base_sha=source_head_before,
        plan_hash=hashlib.sha256(scenario.scenario_id.encode("utf-8")).hexdigest(),
        allowed_changes=tuple(
            ChangeScopeEntry(
                path=change.path,
                operation=change.operation,
                purpose=f"Synthetic scenario change for {change.path}.",
            )
            for change in scenario.changes
        ),
        test_profiles=("synthetic-check",),
        acceptance_criteria=(f"Synthetic scenario {scenario.scenario_id} is satisfied.",),
        max_changed_files=max(1, len(scenario.changes)),
    )
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="synthetic-check",
                argv=(sys.executable, "-c", _test_script(scenario)),
            ),
        )
    )
    task = SafeTaskRequest(
        task_id=f"pretransfer-{scenario.scenario_id}-task",
        thread_id=f"pretransfer-{scenario.scenario_id}-thread",
        title=scenario.title,
        objective=f"Execute synthetic pre-transfer scenario {scenario.scenario_id}.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
        manifest=manifest,
        policy=policy,
    )
    provider = ScenarioProvider(scenario)

    previous_protocol = os.environ.get("UCA_SAFE_EDIT_PROTOCOL")
    os.environ["UCA_SAFE_EDIT_PROTOCOL"] = "v2-line-addressed"
    service = SafeAgentService.create(
        state_root,
        provider,
        allow_local_sources=True,
    )
    try:
        service.run(task)
        if service.state(task.thread_id)["next"] != ["scope_approval"]:
            raise AssertionError("synthetic scenario did not stop at the scope approval gate")
        final = service.resume(task.thread_id, True)
        report = service.artifacts.read_json(final["final_report_ref"])
    finally:
        service.close()
        if previous_protocol is None:
            os.environ.pop("UCA_SAFE_EDIT_PROTOCOL", None)
        else:
            os.environ["UCA_SAFE_EDIT_PROTOCOL"] = previous_protocol

    return SyntheticRunResult(
        report=report,
        source=source,
        sandbox=state_root / "sandboxes" / task.task_id / "repo",
        expected_files=expected_files,
        source_head_before=source_head_before,
        source_head_after=_git(source, "rev-parse", "HEAD"),
        source_status_after=_git(source, "status", "--porcelain"),
        phases=tuple(provider.phases),
    )


def success_scenarios() -> tuple[SyntheticScenario, ...]:
    large_lines = [f"row-{index:04d}\n" for index in range(1, 3001)]
    return (
        SyntheticScenario(
            scenario_id="python-basic",
            title="Python single-line replacement",
            initial_files={"app.py": "def answer():\n    return 42\n"},
            changes=(
                SyntheticChange(
                    path="app.py",
                    operation=ChangeOperation.MODIFY,
                    line_number=2,
                    new_text="    return 43\n",
                ),
            ),
        ),
        SyntheticScenario(
            scenario_id="markdown-insert",
            title="Markdown insertion",
            initial_files={"README.md": "# Title\nExisting text\n"},
            changes=(
                SyntheticChange(
                    path="README.md",
                    operation=ChangeOperation.MODIFY,
                    line_number=1,
                    position="after",
                    new_text="Generated note\n",
                ),
            ),
        ),
        SyntheticScenario(
            scenario_id="sql-replace",
            title="SQL replacement",
            initial_files={"sql/view.sql": "CREATE VIEW v AS\nSELECT 1 AS value;\n"},
            changes=(
                SyntheticChange(
                    path="sql/view.sql",
                    operation=ChangeOperation.MODIFY,
                    line_number=2,
                    new_text="SELECT 2 AS value;\n",
                ),
            ),
        ),
        SyntheticScenario(
            scenario_id="repeated-lines",
            title="Repeated line disambiguation",
            initial_files={"data.txt": "same\n" * 10},
            changes=(
                SyntheticChange(
                    path="data.txt",
                    operation=ChangeOperation.MODIFY,
                    line_number=7,
                    new_text="changed\n",
                ),
            ),
        ),
        SyntheticScenario(
            scenario_id="large-file",
            title="Large file near-tail replacement",
            initial_files={"large.txt": "".join(large_lines)},
            changes=(
                SyntheticChange(
                    path="large.txt",
                    operation=ChangeOperation.MODIFY,
                    line_number=2994,
                    new_text="row-2994-updated\n",
                ),
            ),
        ),
        SyntheticScenario(
            scenario_id="multi-file",
            title="Three file shards",
            initial_files={
                "app.py": "VALUE = 1\n",
                "README.md": "Status: old\n",
                "sql/query.sql": "SELECT 1;\n",
            },
            changes=(
                SyntheticChange(
                    path="app.py",
                    operation=ChangeOperation.MODIFY,
                    line_number=1,
                    new_text="VALUE = 2\n",
                ),
                SyntheticChange(
                    path="README.md",
                    operation=ChangeOperation.MODIFY,
                    line_number=1,
                    new_text="Status: new\n",
                ),
                SyntheticChange(
                    path="sql/query.sql",
                    operation=ChangeOperation.MODIFY,
                    line_number=1,
                    new_text="SELECT 2;\n",
                ),
            ),
        ),
        SyntheticScenario(
            scenario_id="create-file",
            title="Approved file creation",
            initial_files={"README.md": "# Fixture\n"},
            changes=(
                SyntheticChange(
                    path="generated/result.txt",
                    operation=ChangeOperation.CREATE,
                    new_text="created safely\n",
                ),
            ),
        ),
        SyntheticScenario(
            scenario_id="address-correction",
            title="One bounded address correction",
            initial_files={"app.py": "VALUE = 42\n"},
            changes=(
                SyntheticChange(
                    path="app.py",
                    operation=ChangeOperation.MODIFY,
                    line_number=1,
                    new_text="VALUE = 43\n",
                    invalid_initial_address=True,
                ),
            ),
        ),
    )


def failure_scenarios() -> tuple[SyntheticScenario, ...]:
    return (
        SyntheticScenario(
            scenario_id="invalid-address",
            title="Invalid address fails closed",
            initial_files={"app.py": "VALUE = 42\n"},
            changes=(
                SyntheticChange(
                    path="app.py",
                    operation=ChangeOperation.MODIFY,
                    line_number=1,
                    new_text="VALUE = 43\n",
                    invalid_initial_address=True,
                    invalid_correction_address=True,
                ),
            ),
            expected_status="blocked",
            expected_safe_error="edit:shard_validation_failed",
        ),
        SyntheticScenario(
            scenario_id="wrong-path",
            title="Unapproved path fails closed",
            initial_files={"app.py": "VALUE = 42\n"},
            changes=(
                SyntheticChange(
                    path="app.py",
                    operation=ChangeOperation.MODIFY,
                    line_number=1,
                    new_text="VALUE = 43\n",
                    wrong_path="outside.py",
                ),
            ),
            expected_status="blocked",
            expected_safe_error="edit:shard_validation_failed",
        ),
        SyntheticScenario(
            scenario_id="test-failure",
            title="Focused test failure rolls back",
            initial_files={"app.py": "VALUE = 42\n"},
            changes=(
                SyntheticChange(
                    path="app.py",
                    operation=ChangeOperation.MODIFY,
                    line_number=1,
                    new_text="VALUE = 43\n",
                ),
            ),
            expected_status="blocked",
            expected_safe_error="tests:focused_profile_failed",
            force_test_failure=True,
        ),
        SyntheticScenario(
            scenario_id="reviewer-fail",
            title="Reviewer failure blocks safely",
            initial_files={"app.py": "VALUE = 42\n"},
            changes=(
                SyntheticChange(
                    path="app.py",
                    operation=ChangeOperation.MODIFY,
                    line_number=1,
                    new_text="VALUE = 43\n",
                ),
            ),
            expected_status="blocked",
            reviewer_verdict=ReviewVerdict.FAIL,
        ),
    )


def _expected_files(scenario: SyntheticScenario) -> dict[str, str]:
    result = dict(scenario.initial_files)
    for change in scenario.changes:
        if change.operation is ChangeOperation.CREATE:
            result[change.path] = change.new_text
            continue
        if change.line_number is None:
            raise AssertionError(f"modify scenario is missing line_number: {change.path}")
        lines = result[change.path].splitlines(keepends=True)
        index = change.line_number - 1
        if change.position == "before":
            lines[index:index] = [change.new_text]
        elif change.position == "after":
            lines[index + 1 : index + 1] = [change.new_text]
        else:
            lines[index : index + 1] = [change.new_text]
        result[change.path] = "".join(lines)
    return result


def _test_script(scenario: SyntheticScenario) -> str:
    statements = ["from pathlib import Path"]
    expected = _expected_files(scenario)
    for change in scenario.changes:
        path = change.path
        if change.operation is ChangeOperation.CREATE:
            statements.append(
                f"assert Path({path!r}).read_text(encoding='utf-8') == {expected[path]!r}"
            )
            continue
        if change.line_number is None:
            continue
        if change.position == "before":
            target_line = change.line_number
        elif change.position == "after":
            target_line = change.line_number + 1
        else:
            target_line = change.line_number
        statements.append(
            "assert Path("
            f"{path!r}).read_text(encoding='utf-8').splitlines(keepends=True)"
            f"[{target_line - 1}] == {change.new_text!r}"
        )
    if scenario.force_test_failure:
        statements.append("raise AssertionError('forced synthetic acceptance failure')")
    return "; ".join(statements)


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
