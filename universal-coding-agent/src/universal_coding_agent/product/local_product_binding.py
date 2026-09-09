"""Strict local operator configuration and wire values; never execution authority.

Loading configuration performs no provider probe, Git command or store creation.
The immutable runtime descriptor is established separately at explicit startup.
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from universal_coding_agent.product.program_continuation_execution_store import canonical, sha

MAX_BODY = 65_536
MAX_RESPONSE = 1_048_576
SCHEMA = "uca-local-product-binding-1"
COMMAND = "uca-local-product-command-1"
AUTHORITY = dict.fromkeys(
    (
        "source_bytes_verified",
        "filesystem_verified",
        "current_authority_verified",
        "execution_authorized",
        "source_acceptance_authorized",
        "materialization_authorized",
        "automatic_execution",
        "ready_for_supervised_pilot",
        "real_project_pilot_validated",
    ),
    False,
)
COMMON = frozenset(
    (
        "schema request_id action expected_binding_sha256 expected_revision requirement_sha256 "
        "plan_sha256 program_control_revision task_control_revision"
    ).split()
)
COMMANDS = {
    "source/initialize": ("initialize_source", "origin_commit_sha origin_tree_sha"),
    "phases/first/start": ("start_first_phase", "before_sha256 generation"),
    "phases/first/scope-decisions": (
        "decide_first_scope",
        "task_id scope_proposal_sha256 scope_sha256 checkpoint_sha256 approval_id approved",
    ),
    "source/first/previews": (
        "preview_first_source",
        "task_id result_sha256 before_sha256 generation",
    ),
    "source/first/decisions": (
        "decide_first_source",
        "task_id quote_sha256 quote_revision "
        "core_sha256 transition_sha256 before_sha256 generation "
        "predecessor_receipt_sha256 evidence_view_sha256 approval_id "
        "approved",
    ),
    "continuation/start": (
        "start_continuation",
        "before_sha256 generation acceptance_receipt_sha256",
    ),
    "continuation/scope-decisions": (
        "decide_continuation_scope",
        "operation_id task_id "
        "admission_sha256 expected_epoch expected_receipt_sha256 "
        "proposal_sha256 scope_sha256 approval_id approved",
    ),
    "source/final/previews": (
        "preview_final_source",
        "operation_id task_id terminal_receipt_sha256 before_sha256 generation",
    ),
    "source/final/decisions": (
        "decide_final_source",
        "operation_id task_id "
        "terminal_receipt_sha256 before_sha256 generation "
        "candidate_sha256 revision core_sha256 transition_sha256 "
        "predecessor_receipt_sha256 evidence_view_sha256 approval_id "
        "approved",
    ),
    "reconcile": ("reconcile_outcome", "target_request_sha256 target_revision operation_id"),
}
ACTION_FIELDS = {a: COMMON | set(fields.split()) for a, fields in COMMANDS.values()}
RESULT_FIELDS = {
    "initialize_source": "generation source_sha256 initialization_receipt_sha256",
    "start_first_phase": "phase_id task_id thread_id execution_status scope_proposal_sha256 "
    "scope_sha256 checkpoint_sha256 result_sha256 tests_summary "
    "reviewer_verdict evidence_view_sha256",
    "preview_first_source": "task_id quote_sha256 quote_revision core_sha256 transition_sha256 "
    "before_sha256 after_sha256 generation predecessor_receipt_sha256 "
    "evidence_view_sha256",
    "decide_first_source": "task_id quote_sha256 approved source_receipt_sha256 generation "
    "source_sha256",
    "start_continuation": "operation_id phase_id task_id thread_id admission_sha256 epoch "
    "v3_receipt_sha256 proposal_sha256 scope_sha256 execution_status "
    "result_sha256 evidence_view_sha256",
    "preview_final_source": "operation_id task_id candidate_sha256 revision core_sha256 "
    "transition_sha256 before_sha256 after_sha256 generation "
    "predecessor_receipt_sha256 terminal_receipt_sha256 "
    "evidence_view_sha256",
    "decide_final_source": "operation_id task_id candidate_sha256 approved source_receipt_sha256 "
    "generation source_sha256",
    "reconcile_outcome": "target_request_id target_request_sha256 target_status "
    "target_response_sha256 disposition",
}
RESULT_FIELDS["decide_first_scope"] = RESULT_FIELDS["start_first_phase"]
RESULT_FIELDS["decide_continuation_scope"] = RESULT_FIELDS["start_continuation"]
ERROR_STATUS = {
    **dict.fromkeys(("invalid_command",), 422),
    "invalid_json": 400,
    "request_too_large": 413,
    "local_boundary_denied": 403,
    **dict.fromkeys(
        (
            "project_not_found",
            "program_not_bound",
            "request_not_found",
            "operation_not_found",
            "evidence_not_found",
        ),
        404,
    ),
    **dict.fromkeys(
        (
            "request_conflict",
            "revision_conflict",
            "program_busy",
            "binding_changed",
            "source_changed",
            "policy_changed",
            "proposal_changed",
            "unsupported_version",
            "recorded_evidence_invalid",
            "recovery_required",
            "evidence_view_unavailable",
            "unsupported_program",
            "source_decision_final",
        ),
        409,
    ),
    **dict.fromkeys(("local_commands_disabled", "unsupported_transport", "store_unavailable"), 503),
}


class LocalProductError(ValueError):
    """Only fixed public messages may cross the transport boundary."""

    def __init__(self, code):
        if code not in ERROR_STATUS:
            raise ValueError("unknown local Product error")
        self.code, self.status = code, ERROR_STATUS[code]
        super().__init__(code.replace("_", " ") + ".")

    def envelope(self, project=None, program=None, request=None):
        return {
            "schema": "uca-local-product-error-1",
            "code": self.code,
            "message": str(self),
            "project_id": project,
            "program_id": program,
            "request_id": request,
            "retry_effect": False,
        }


def check(ok, code="invalid_command"):
    if not ok:
        raise LocalProductError(code)


def identifier(value):
    check(type(value) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", value))
    return value


def digest(value):
    check(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value))
    return value


def integer(value):
    check(type(value) is int and 0 <= value <= 2**53 - 1)
    return value


def parse_json(raw, *, maximum=MAX_BODY, strings=4096, canonical_only=False):
    check(type(raw) is bytes and len(raw) <= maximum, "request_too_large")
    check(bool(raw), "invalid_json")
    depth, quoted, escaped = 0, False, False
    for byte in raw:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            check(depth <= 8)
        elif byte in (93, 125):
            depth -= 1
            check(depth >= 0, "invalid_json")

    def pairs(items):
        check(len(items) <= 64 and len({k for k, _ in items}) == len(items))
        check(all(len(k.encode()) <= 128 for k, _ in items))
        return dict(items)

    def invalid(_):
        raise LocalProductError("invalid_command")

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=pairs,
            parse_float=invalid,
            parse_constant=invalid,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise LocalProductError("invalid_json") from exc

    def validate(item):
        if type(item) is str:
            check(len(item.encode()) <= strings and "\x00" not in item)
        elif type(item) is int:
            check(-(2**63) <= item < 2**64)
        elif type(item) is list:
            check(len(item) <= 1024)
            for child in item:
                validate(child)
        elif type(item) is dict:
            for child in item.values():
                validate(child)
        else:
            check(item is None or type(item) is bool)

    try:
        validate(value)
    except UnicodeError as exc:
        raise LocalProductError("invalid_json") from exc
    check(not canonical_only or canonical(value) == raw)
    return value


def command_payload(raw, project, program, action, target=None):
    identifier(project)
    identifier(program)
    value = parse_json(raw)
    check(type(value) is dict and value.keys() == ACTION_FIELDS[action])
    check(value["schema"] == COMMAND and value["action"] == action)
    for key, item in value.items():
        if key.endswith("_sha256"):
            digest(item)
        elif key in {"request_id", "task_id", "approval_id"}:
            identifier(item)
        elif key == "operation_id":
            check(
                (action == "reconcile_outcome" and item is None)
                or type(item) is str
                and re.fullmatch(r"[0-9a-f]{32}", item)
            )
        elif key in {
            "expected_revision",
            "program_control_revision",
            "expected_epoch",
            "target_revision",
            "generation",
            "revision",
            "quote_revision",
        }:
            integer(item)
        elif key == "task_control_revision":
            if action in {"initialize_source", "start_first_phase"}:
                check(item is None)
            else:
                check(item is None and action == "reconcile_outcome" or type(item) is int)
                if item is not None:
                    integer(item)
        elif key == "approved":
            check(type(item) is bool)
        elif key in {"origin_commit_sha", "origin_tree_sha"}:
            check(type(item) is str and re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", item))
    if "generation" in value:
        check(value["generation"] == (0 if "first" in action else 1))
    for key in ("quote_revision", "revision"):
        if key in value:
            check(value[key] == 1)
    if target is not None:
        identifier(target)
        check(action == "reconcile_outcome" and value["request_id"] != target)
        value["target_request_id"] = target
    return {**value, "project_id": project, "program_id": program}


def nofollow_bytes(path, maximum=MAX_BODY):
    """Open the complete absolute parent chain without following links."""
    path = Path(path)
    check(path.is_absolute() and str(path) == os.path.normpath(str(path)), "binding_changed")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK
    parent = os.open("/", flags)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, flags, dir_fd=parent)
            os.close(parent)
            parent = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            check(
                stat.S_ISREG(before.st_mode)
                and before.st_nlink == 1
                and before.st_uid == os.geteuid()
                and 0 < before.st_size <= maximum,
                "binding_changed",
            )
            raw = os.read(fd, maximum + 1)
            after = os.stat(path.name, dir_fd=parent, follow_symlinks=False)

            def stamp(s):
                return (
                    s.st_dev,
                    s.st_ino,
                    s.st_size,
                    s.st_mtime_ns,
                    s.st_ctime_ns,
                    s.st_nlink,
                    s.st_mode,
                )

            check(
                len(raw) == before.st_size and stamp(before) == stamp(os.fstat(fd)) == stamp(after),
                "binding_changed",
            )
            return raw
        finally:
            os.close(fd)
    finally:
        os.close(parent)


def root_pin(path):
    path = Path(path)
    check(path.is_absolute() and str(path.resolve(strict=True)) == str(path), "binding_changed")
    info = path.stat(follow_symlinks=False)
    check(stat.S_ISDIR(info.st_mode), "binding_changed")
    return [str(path), info.st_dev, info.st_ino]


def local_authority(origin):
    check(type(origin) is str)
    parts = urlsplit(origin)
    check(
        parts.scheme == "http"
        and not parts.username
        and not parts.password
        and not parts.path
        and not parts.query
        and not parts.fragment
        and parts.port is not None
    )
    try:
        local = ipaddress.ip_address(parts.hostname).is_loopback
    except ValueError:
        local = parts.hostname == "localhost"
    check(local and 1 <= parts.port <= 65535)
    check(origin == "http://" + parts.netloc)
    return parts.netloc


@dataclass(frozen=True)
class LocalProductBinding:
    raw: bytes

    @classmethod
    def load(cls, path):
        binding = cls.from_bytes(nofollow_bytes(Path(path)))
        binding.preflight()
        return binding

    def preflight(self, program_database=None):
        """Check retained identities before any factory can recreate a store."""
        import sqlite3
        from contextlib import closing

        from universal_coding_agent.product.program_continuation_execution_store import identity

        locator = read_locator(Path(self.value["safe_state_root"]) / LOCATOR)
        if program_database is not None:
            path = Path(program_database)
            identity(path)
            other = read_locator(path.parent / LOCATOR)
            check(other == locator, "binding_changed")
            if locator is None:
                with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
                    check(
                        db.execute(
                            "SELECT 1 FROM sqlite_master WHERE name GLOB 'local_product_*' LIMIT 1"
                        ).fetchone()
                        is None,
                        "binding_changed",
                    )
        if locator is None:
            return
        from universal_coding_agent.product.local_product_status import read_session

        with read_session(locator["program_store"][0], binding_only=True) as reader:
            _, descriptor = reader.mapping(self.value["project_id"])
            check(descriptor["configuration"] == self.value, "binding_changed")
            for program in descriptor["programs"]:
                reader.namespaces(program["program_id"])
            for root in descriptor["roots"]:
                check(root_pin(root[0]) == root, "binding_changed")
            if program_database is not None:
                check(
                    list(identity(program_database)) == descriptor["stores"][0], "binding_changed"
                )

    @classmethod
    def from_bytes(cls, raw):
        from universal_coding_agent.core.safe_models import SafeModePolicy

        value = parse_json(raw)
        fields = (
            "schema project_id display_name source_root origin_repository_url "
            "origin_commit_sha origin_tree_sha object_format owned_execution_root "
            "safe_state_root transport_id edit_protocol policy programs local_origin"
        )
        check(
            type(value) is dict
            and value.keys() == set(fields.split())
            and value["schema"] == SCHEMA
        )
        identifier(value["project_id"])
        identifier(value["transport_id"])
        check(type(value["display_name"]) is str and 0 < len(value["display_name"]) <= 200)
        check(value["object_format"] in {"sha1", "sha256"})
        for key in ("origin_commit_sha", "origin_tree_sha"):
            check(
                type(value[key]) is str
                and re.fullmatch(
                    r"[0-9a-f]{" + str(40 if value["object_format"] == "sha1" else 64) + "}",
                    value[key],
                )
            )
        check(value["edit_protocol"] in {"v1", "v2-line-addressed"})
        local_authority(value["local_origin"])
        roots = [Path(value[k]) for k in ("source_root", "safe_state_root", "owned_execution_root")]
        check(len(set(roots)) == 3)
        for root in roots:
            check(root.is_absolute() and str(root.resolve()) == str(root), "binding_changed")
        for root in roots[1:]:
            check(
                not root.is_relative_to(roots[0]) and not roots[0].is_relative_to(root),
                "binding_changed",
            )
        # This is the existing materializer's one supported host-owned root.
        check(roots[2] == roots[1] / "sandboxes", "binding_changed")
        root_pin(roots[0])
        check(type(value["origin_repository_url"]) is str and value["origin_repository_url"])
        url = urlsplit(value["origin_repository_url"])
        check(not url.username and not url.password and not url.query and not url.fragment)
        policy = SafeModePolicy.model_validate_json(canonical(value["policy"]), strict=True)
        check(bool(policy.profiles))
        value["policy"] = policy.model_dump(mode="json")
        programs = value["programs"]
        check(type(programs) is list and 1 <= len(programs) <= 100)
        seen = set()
        for item in programs:
            check(
                type(item) is dict
                and item.keys() == {"program_id", "requirement_sha256", "plan_sha256"}
            )
            identifier(item["program_id"])
            digest(item["requirement_sha256"])
            digest(item["plan_sha256"])
            check(item["program_id"] not in seen)
            seen.add(item["program_id"])
        value["programs"] = sorted(programs, key=lambda p: p["program_id"])
        return cls(canonical(value))

    @property
    def value(self):
        return parse_json(self.raw)

    @property
    def sha256(self):
        return sha(self.raw)


LOCATOR = "local-product-root-v1.json"


def write_locator(path, value):
    """Publish once, fsync and independently read the exact saved bytes."""
    raw = canonical(value)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        check(nofollow_bytes(path) == raw, "binding_changed")
        return
    try:
        offset = 0
        while offset < len(raw):
            written = os.write(fd, raw[offset:])
            check(written > 0, "store_unavailable")
            offset += written
        os.fsync(fd)
    finally:
        os.close(fd)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    check(nofollow_bytes(path) == raw, "binding_changed")


def read_locator(path):
    try:
        value = parse_json(nofollow_bytes(path), canonical_only=True)
    except FileNotFoundError:
        return None
    check(
        type(value) is dict
        and value.keys() == {"schema", "program_store", "safe_root", "binding_sha256", "programs"}
        and value["schema"] == "uca-local-product-root-1",
        "binding_changed",
    )
    digest(value["binding_sha256"])
    return value


def local_program_route(database_path, program_id=None, task_id=None, thread_id=None):
    """Deny-only affinity, including copied IDs and surviving partial metadata."""
    import sqlite3
    from contextlib import closing

    from universal_coding_agent.product.local_product_command_store import PROGRAMS, schema
    from universal_coding_agent.product.program_continuation_execution_store import identity

    path = Path(database_path)
    locator = read_locator(path.parent / LOCATOR)
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0.5)) as db:
        db.execute("PRAGMA query_only=ON")
        db.set_progress_handler(lambda: 1, 2_000_000)
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE name GLOB 'local_product_*' LIMIT 100"
        ).fetchall()
        if not tables and locator is None:
            return False
        schema(db)
        check(
            locator is not None and list(identity(path)) == locator["program_store"],
            "binding_changed",
        )
        check(read_locator(Path(locator["safe_root"][0]) / LOCATOR) == locator, "binding_changed")
        matched = []
        for item in locator["programs"]:
            if (
                program_id == item["program_id"]
                or task_id in item["task_ids"]
                or thread_id in item["thread_ids"]
            ):
                matched.append(item["program_id"])
        for program in matched:
            row = db.execute(
                f"SELECT binding_sha256 FROM {PROGRAMS} WHERE program_id=?", (program,)
            ).fetchone()
            check(row is not None and row[0] == locator["binding_sha256"], "binding_changed")
        return bool(matched)


def local_safe_route(safe, thread_id, task_id, source_task):
    from universal_coding_agent.product.program_source_routing import checkpoint_has_source_marker

    locations = (safe.artifacts.root.parent / LOCATOR, safe.control.database_path.parent / LOCATOR)
    values = [read_locator(path) for path in locations]
    metadata = source_task.get("metadata", {}) if type(source_task) is dict else {}
    marked = any(str(key).startswith("local_product_") for key in metadata)
    if not any(values):
        # Stored affinity also survives removal of both namespace locators.
        if marked or checkpoint_has_source_marker(safe, thread_id, local_only=True):
            raise LocalProductError("binding_changed")
        return False
    check(values[0] is not None and values[0] == values[1], "binding_changed")
    locator = values[0]
    check(root_pin(safe.artifacts.root.parent) == locator["safe_root"], "binding_changed")
    return marked or local_program_route(
        Path(locator["program_store"][0]), task_id=task_id, thread_id=thread_id
    )
