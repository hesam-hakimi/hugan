"""Bounded, in-memory cumulative source handoff; no execution or Git authority.

A trusted host must attest the origin and qualification evidence. Opaque hashes in
this contract bind that evidence; they do not authenticate it or prove a PASS.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
from dataclasses import asdict, dataclass, fields


class ProgramSourceError(ValueError):
    """A source transition failed its immutable identity or bounded scope contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProgramSourceError(message)


def _digest(value: object) -> None:
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
             "invalid SHA-256 identity")


def _identifier(value: object) -> None:
    _require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,127}",
                                                  value) is not None,
             "invalid execution identity")


def _path(value: object) -> None:
    _require(isinstance(value, str) and 0 < len(value) <= 1024, "invalid source path")
    parts = value.split("/")
    _require(len(parts) <= 64, "source path depth exceeded")
    devices = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(10)),
               *(f"lpt{i}" for i in range(10))}
    for part in parts:
        _require(re.fullmatch(r"[A-Za-z0-9_.-]{1,255}", part) is not None
                 and part not in {".", ".."} and not part.endswith(".")
                 and part.lower() != ".git" and part.split(".")[0].lower() not in devices,
                 "unsafe or unsupported portable source path")


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True, slots=True)
class ProgramSourcePolicy:
    max_files: int = 20_000
    max_changes: int = 1_000
    max_file_bytes: int = 1_000_000
    max_total_bytes: int = 16_000_000
    max_artifact_bytes: int = 24_000_000

    def __post_init__(self) -> None:
        for value in asdict(self).values():
            _require(type(value) is int and 0 < value <= 64_000_000,
                     "source policy bounds must be positive bounded integers")

    def canonical_hash(self) -> str:
        return _hash(_canonical({"schema": "uca-source-policy-1", **asdict(self)}))


@dataclass(frozen=True, slots=True)
class ProgramSourceIdentity:
    program_id: str
    repository_sha256: str
    requirement_sha256: str
    plan_sha256: str
    origin_base_sha: str
    origin_tree_sha: str

    def __post_init__(self) -> None:
        _identifier(self.program_id)
        for value in (self.repository_sha256, self.requirement_sha256, self.plan_sha256):
            _digest(value)
        for value in (self.origin_base_sha, self.origin_tree_sha):
            _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}",
                                                          value) is not None,
                     "invalid immutable Git origin")
        _require(len(self.origin_base_sha) == len(self.origin_tree_sha),
                 "origin Git object formats differ")


@dataclass(frozen=True, slots=True)
class ProgramSourceFile:
    path: str
    content: bytes
    mode: str = "100644"

    def __post_init__(self) -> None:
        _path(self.path)
        _require(type(self.content) is bytes, "source content must be immutable bytes")
        _require(self.mode in ("100644", "100755"), "unsupported source mode")

    def fingerprint(self) -> str:
        return _hash(self.mode.encode("ascii") + b"\0" + self.content)


def _ordered(values: object) -> None:
    _require(type(values) is tuple and all(isinstance(value, str) for value in values),
             "expected an immutable string sequence")
    _require(values == tuple(sorted(set(values))), "sequence must be unique and sorted")


@dataclass(frozen=True, slots=True)
class ProgramSourceSnapshot:
    identity: ProgramSourceIdentity
    files: tuple[ProgramSourceFile, ...]
    generation: int = 0
    predecessor_sha256: str | None = None

    def __post_init__(self) -> None:
        _require(type(self.identity) is ProgramSourceIdentity, "invalid source identity")
        _require(type(self.files) is tuple
                 and all(type(item) is ProgramSourceFile for item in self.files),
                 "source files must be an immutable typed sequence")
        _ordered(tuple(item.path for item in self.files))
        _require(type(self.generation) is int and 0 <= self.generation <= 10_000,
                 "invalid source generation")
        if self.generation == 0:
            _require(self.predecessor_sha256 is None, "initial source has a predecessor")
        else:
            _digest(self.predecessor_sha256)


@dataclass(frozen=True, slots=True)
class ProgramSourceEdit:
    path: str
    expected_fingerprint: str | None
    replacement: ProgramSourceFile | None

    def __post_init__(self) -> None:
        _path(self.path)
        _require(self.expected_fingerprint is not None or self.replacement is not None,
                 "empty source edit")
        if self.expected_fingerprint is not None:
            _digest(self.expected_fingerprint)
        if self.replacement is not None:
            _require(type(self.replacement) is ProgramSourceFile
                     and self.replacement.path == self.path, "replacement path differs")


@dataclass(frozen=True, slots=True)
class ProgramSourceTransition:
    before_sha256: str
    after_sha256: str
    policy_sha256: str
    phase_id: str
    task_id: str
    slice_id: str | None
    allowed_paths: tuple[str, ...]
    evidence_sha256: tuple[str, ...]
    edits: tuple[ProgramSourceEdit, ...]

    def __post_init__(self) -> None:
        for value in (self.before_sha256, self.after_sha256, self.policy_sha256):
            _digest(value)
        for value in (self.phase_id, self.task_id):
            _identifier(value)
        if self.slice_id is not None:
            _identifier(self.slice_id)
        _ordered(self.allowed_paths)
        for path in self.allowed_paths:
            _path(path)
        _ordered(self.evidence_sha256)
        _require(0 < len(self.evidence_sha256) <= 32, "missing or oversized evidence bindings")
        for value in self.evidence_sha256:
            _digest(value)
        _require(type(self.edits) is tuple and self.edits
                 and all(type(item) is ProgramSourceEdit for item in self.edits),
                 "edits must be a nonempty immutable typed sequence")
        _ordered(tuple(item.path for item in self.edits))
        _require({item.path for item in self.edits}.issubset(self.allowed_paths),
                 "source edit is outside exact approved scope")


def _file_payload(item: ProgramSourceFile) -> dict[str, str]:
    return {"path": item.path, "mode": item.mode,
            "content": base64.b64encode(item.content).decode("ascii")}


def _snapshot_payload(snapshot: ProgramSourceSnapshot) -> dict[str, object]:
    return {"schema": "uca-source-snapshot-1", "identity": asdict(snapshot.identity),
            "generation": snapshot.generation, "predecessor_sha256": snapshot.predecessor_sha256,
            "files": [_file_payload(item) for item in snapshot.files]}


def _transition_payload(transition: ProgramSourceTransition) -> dict[str, object]:
    payload = asdict(transition)
    payload["schema"] = "uca-source-transition-1"
    payload["edits"] = [
        {"path": edit.path, "expected_fingerprint": edit.expected_fingerprint,
         "replacement": _file_payload(edit.replacement) if edit.replacement else None}
        for edit in transition.edits
    ]
    return payload


class ProgramSourceTransitionService:
    """Pure prepare/approve/materialize contract; never writes or executes source."""

    def __init__(self, policy: ProgramSourcePolicy | None = None) -> None:
        self.policy = policy if policy is not None else ProgramSourcePolicy()
        _require(type(self.policy) is ProgramSourcePolicy, "invalid source policy")

    def snapshot_bytes(self, snapshot: ProgramSourceSnapshot) -> bytes:
        _require(type(snapshot) is ProgramSourceSnapshot, "invalid source snapshot")
        self._check_files(snapshot.files)
        return self._bounded(_canonical(_snapshot_payload(snapshot)))

    def snapshot_hash(self, snapshot: ProgramSourceSnapshot) -> str:
        return _hash(self.snapshot_bytes(snapshot))

    def transition_bytes(self, transition: ProgramSourceTransition) -> bytes:
        _require(type(transition) is ProgramSourceTransition, "invalid source transition")
        _require(transition.policy_sha256 == self.policy.canonical_hash(), "source policy drift")
        _require(len(transition.edits) <= self.policy.max_changes
                 and len(transition.allowed_paths) <= self.policy.max_changes,
                 "source change or scope count exceeded")
        self._check_files(tuple(edit.replacement for edit in transition.edits
                               if edit.replacement is not None))
        return self._bounded(_canonical(_transition_payload(transition)))

    def transition_hash(self, transition: ProgramSourceTransition) -> str:
        return _hash(self.transition_bytes(transition))

    def prepare(
        self, before: ProgramSourceSnapshot, *, expected_source_sha256: str,
        phase_id: str, task_id: str, allowed_paths: tuple[str, ...],
        evidence_sha256: tuple[str, ...], edits: tuple[ProgramSourceEdit, ...],
        slice_id: str | None = None,
    ) -> ProgramSourceTransition:
        _digest(expected_source_sha256)
        _require(hmac.compare_digest(self.snapshot_hash(before), expected_source_sha256),
                 "source snapshot drift")
        candidate = ProgramSourceTransition(
            expected_source_sha256, "0" * 64, self.policy.canonical_hash(), phase_id,
            task_id, slice_id, allowed_paths, evidence_sha256, edits,
        )
        self.transition_bytes(candidate)
        after = self._apply(before, candidate)
        return ProgramSourceTransition(
            candidate.before_sha256, self.snapshot_hash(after), candidate.policy_sha256,
            phase_id, task_id, slice_id, allowed_paths, evidence_sha256, edits,
        )

    def materialize(
        self, before: ProgramSourceSnapshot, transition: ProgramSourceTransition, *,
        approved_transition_sha256: str,
    ) -> ProgramSourceSnapshot:
        """Return bytes in an immutable snapshot, not a filesystem or Git checkout.

        The approval digest must come from the trusted caller, never model output.
        No artifact, source, provider, test, or publication authority is implied.
        """
        _digest(approved_transition_sha256)
        _require(hmac.compare_digest(self.transition_hash(transition), approved_transition_sha256),
                 "source transition approval mismatch")
        _require(hmac.compare_digest(self.snapshot_hash(before), transition.before_sha256),
                 "source snapshot drift")
        after = self._apply(before, transition)
        _require(hmac.compare_digest(self.snapshot_hash(after), transition.after_sha256),
                 "source transition result mismatch")
        return after

    def load_snapshot(self, content: bytes, *, expected_sha256: str) -> ProgramSourceSnapshot:
        data = self._decode(content, expected_sha256, "uca-source-snapshot-1",
                            {"identity", "generation", "predecessor_sha256", "files"})
        identity = self._object(data["identity"], {field.name for field in fields(
            ProgramSourceIdentity)})
        raw_files = self._sequence(data["files"], self.policy.max_files)
        snapshot = ProgramSourceSnapshot(
            ProgramSourceIdentity(**identity), tuple(self._file(item) for item in raw_files),
            data["generation"], data["predecessor_sha256"],
        )
        _require(self.snapshot_bytes(snapshot) == content, "noncanonical source snapshot")
        return snapshot

    def load_transition(self, content: bytes, *, expected_sha256: str) -> ProgramSourceTransition:
        data = self._decode(content, expected_sha256, "uca-source-transition-1",
                            {field.name for field in fields(ProgramSourceTransition)})
        raw_edits = self._sequence(data["edits"], self.policy.max_changes)
        edits = []
        for raw in raw_edits:
            edit = self._object(raw, {"path", "expected_fingerprint", "replacement"})
            edits.append(ProgramSourceEdit(edit["path"], edit["expected_fingerprint"],
                         self._file(edit["replacement"]) if edit["replacement"] is not None
                         else None))
        data["edits"] = tuple(edits)
        data["allowed_paths"] = tuple(
            self._sequence(data["allowed_paths"], self.policy.max_changes)
        )
        data["evidence_sha256"] = tuple(self._sequence(data["evidence_sha256"], 32))
        transition = ProgramSourceTransition(**data)
        _require(self.transition_bytes(transition) == content, "noncanonical source transition")
        return transition

    def _apply(self, before: ProgramSourceSnapshot,
               transition: ProgramSourceTransition) -> ProgramSourceSnapshot:
        files_by_path = {item.path: item for item in before.files}
        for edit in transition.edits:
            old = files_by_path.get(edit.path)
            observed = old.fingerprint() if old is not None else None
            _require(observed == edit.expected_fingerprint, "source preimage mismatch")
            _require(old != edit.replacement, "source edit has no effect")
            if edit.replacement is None:
                del files_by_path[edit.path]
            else:
                files_by_path[edit.path] = edit.replacement
        after = ProgramSourceSnapshot(
            before.identity, tuple(files_by_path[path] for path in sorted(files_by_path)),
            before.generation + 1, transition.before_sha256,
        )
        self.snapshot_bytes(after)
        return after

    def _check_files(self, items: tuple[ProgramSourceFile, ...]) -> None:
        _require(len(items) <= self.policy.max_files, "source file count exceeded")
        total = 0
        names = set()
        directories = set()
        spelling = {}
        for item in items:
            _require(len(item.content) <= self.policy.max_file_bytes, "source file size exceeded")
            total += len(item.content)
            _require(total <= self.policy.max_total_bytes, "source total bytes exceeded")
            lower = item.path.lower()
            _require(lower not in names, "portable source path collision")
            names.add(lower)
            components = lower.split("/")
            directories.update("/".join(components[:index]) for index in range(1, len(components)))
            original_parts = item.path.split("/")
            for index in range(1, len(original_parts) + 1):
                prefix = "/".join(original_parts[:index])
                key = prefix.lower()
                _require(spelling.setdefault(key, prefix) == prefix,
                         "portable source directory spelling collision")
        _require(not names.intersection(directories), "source file/directory conflict")

    def _bounded(self, content: bytes) -> bytes:
        _require(type(content) is bytes and len(content) <= self.policy.max_artifact_bytes,
                 "source artifact bytes exceeded or invalid")
        return content

    def _decode(self, content: bytes, expected: str, schema: str,
                keys: set[str]) -> dict[str, object]:
        _digest(expected)
        self._bounded(content)
        _require(hmac.compare_digest(_hash(content), expected), "source artifact hash mismatch")
        try:
            data = json.loads(content, object_pairs_hook=_unique_object)
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise ProgramSourceError("invalid source artifact JSON") from exc
        data = self._object(data, keys | {"schema"})
        _require(data.pop("schema") == schema, "unsupported source artifact schema")
        return data

    @staticmethod
    def _object(value: object, keys: set[str]) -> dict[str, object]:
        _require(type(value) is dict and set(value) == keys, "invalid source object fields")
        return value

    @staticmethod
    def _sequence(value: object, limit: int) -> list:
        _require(type(value) is list and len(value) <= limit,
                 "invalid or oversized source sequence")
        return value

    def _file(self, value: object) -> ProgramSourceFile:
        data = self._object(value, {"path", "mode", "content"})
        encoded = data["content"]
        max_encoded = 4 * ((self.policy.max_file_bytes + 2) // 3)
        _require(type(encoded) is str and len(encoded) <= max_encoded,
                 "invalid or oversized source encoding")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (ValueError, UnicodeError) as exc:
            raise ProgramSourceError("invalid source base64") from exc
        _require(base64.b64encode(content).decode("ascii") == encoded, "noncanonical source base64")
        return ProgramSourceFile(data["path"], content, data["mode"])


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        _require(key not in result, "duplicate source artifact field")
        result[key] = value
    return result
