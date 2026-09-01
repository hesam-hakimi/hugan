from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import Field, ValidationError, field_validator, model_validator

from universal_coding_agent.core.models import FrozenModel
from universal_coding_agent.product.models import SearchHit, SearchSourceType
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.storage.artifacts import ArtifactStore

DEFAULT_DECISION_MAX_BYTES = 64_000


class ProjectDecisionValidationError(ValueError):
    """A project decision cannot satisfy its accepted-memory contract."""


class ProjectDecisionStatus(StrEnum):
    DRAFT = "draft"
    ACCEPTED = "accepted"


class ProjectDecisionManifest(FrozenModel):
    schema_version: str = Field(default="1", pattern=r"^1$")
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    decision_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    version: int = Field(ge=1)
    supersedes_version: int | None = Field(default=None, ge=1)
    title: str = Field(min_length=1, max_length=200)
    context: str = Field(min_length=1, max_length=8_000)
    decision: str = Field(min_length=1, max_length=8_000)
    rationale: str = Field(min_length=1, max_length=8_000)
    alternatives: tuple[str, ...] = Field(default=(), max_length=32)
    consequences: tuple[str, ...] = Field(default=(), max_length=32)

    @field_validator("title", "context", "decision", "rationale")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("project-decision text must not be blank")
        return value

    @field_validator("alternatives", "consequences")
    @classmethod
    def validate_sequence_text(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item.strip() or len(item) > 2_000 for item in values):
            raise ValueError(
                "project-decision sequence items must be non-blank and at most 2000 characters"
            )
        return values

    @model_validator(mode="after")
    def validate_supersession(self) -> ProjectDecisionManifest:
        if self.version == 1 and self.supersedes_version is not None:
            raise ValueError("project-decision version 1 cannot supersede another version")
        if self.version > 1 and self.supersedes_version != self.version - 1:
            raise ValueError(
                "project-decision versions must supersede the immediately prior version"
            )
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class ProjectDecisionRecord(FrozenModel):
    manifest: ProjectDecisionManifest
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    manifest_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    status: ProjectDecisionStatus
    acceptance_ref: str = Field(
        default="",
        pattern=r"^$|^artifact://[a-zA-Z0-9._/-]+$",
    )
    acceptance_sha256: str = Field(default="", pattern=r"^$|^[0-9a-f]{64}$")
    indexed: bool = False

    @model_validator(mode="after")
    def validate_acceptance_evidence(self) -> ProjectDecisionRecord:
        has_ref = bool(self.acceptance_ref)
        has_hash = bool(self.acceptance_sha256)
        if has_ref != has_hash:
            raise ValueError("project-decision acceptance reference and hash must coexist")
        if self.status is ProjectDecisionStatus.ACCEPTED and not has_ref:
            raise ValueError("accepted project decision requires acceptance evidence")
        if self.status is ProjectDecisionStatus.DRAFT and has_ref:
            raise ValueError("draft project decision cannot contain acceptance evidence")
        return self


class ProjectDecisionService:
    """Durable, explicitly accepted, project-scoped decision and ADR memory."""

    def __init__(
        self,
        database_path: Path,
        artifacts: ArtifactStore,
        search: SearchService,
        *,
        max_decision_bytes: int = DEFAULT_DECISION_MAX_BYTES,
    ) -> None:
        if max_decision_bytes < 1:
            raise ValueError("project-decision byte limit must be positive")
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts = artifacts
        self.search = search
        self.max_decision_bytes = max_decision_bytes
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS project_decisions (
                project_id TEXT NOT NULL,
                decision_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                manifest_json TEXT NOT NULL,
                manifest_sha256 TEXT NOT NULL,
                manifest_ref TEXT NOT NULL,
                status TEXT NOT NULL,
                acceptance_ref TEXT NOT NULL,
                acceptance_sha256 TEXT NOT NULL,
                indexed INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (project_id, decision_id, version)
            )
            """
        )
        self.connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_project_decisions_status
            ON project_decisions(project_id, status, decision_id, version)
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def create_draft(
        self,
        *,
        project_id: str,
        decision_id: str,
        version: int,
        title: str,
        context: str,
        decision: str,
        rationale: str,
        alternatives: tuple[str, ...] = (),
        consequences: tuple[str, ...] = (),
        supersedes_version: int | None = None,
    ) -> ProjectDecisionRecord:
        try:
            manifest = ProjectDecisionManifest(
                project_id=project_id,
                decision_id=decision_id,
                version=version,
                supersedes_version=supersedes_version,
                title=title,
                context=context,
                decision=decision,
                rationale=rationale,
                alternatives=alternatives,
                consequences=consequences,
            )
        except ValidationError as exc:
            raise ProjectDecisionValidationError("invalid project-decision manifest") from exc
        content = manifest.canonical_content()
        if len(content.encode("utf-8")) > self.max_decision_bytes:
            raise ProjectDecisionValidationError("project-decision manifest exceeds its byte limit")
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            if self._get_row(project_id, decision_id, version) is not None:
                raise ProjectDecisionValidationError("project-decision version already exists")
            previous = self.connection.execute(
                """
                SELECT version, status FROM project_decisions
                WHERE project_id = ? AND decision_id = ?
                ORDER BY version DESC LIMIT 1
                """,
                (project_id, decision_id),
            ).fetchone()
            if version == 1:
                if previous is not None:
                    raise ProjectDecisionValidationError(
                        "project-decision version 1 requires a new project decision"
                    )
            elif (
                previous is None
                or int(previous[0]) != version - 1
                or previous[1] != ProjectDecisionStatus.ACCEPTED.value
                or supersedes_version != int(previous[0])
            ):
                raise ProjectDecisionValidationError(
                    "new project-decision version must supersede the latest accepted version"
                )
            manifest_sha256 = manifest.canonical_hash()
            manifest_ref = self.artifacts.write_text(
                self._manifest_path(manifest),
                content,
                "application/json",
            )
            if not hmac.compare_digest(manifest_ref.sha256, manifest_sha256):
                raise ProjectDecisionValidationError(
                    "project-decision manifest artifact hash mismatch"
                )
            self.connection.execute(
                """
                INSERT INTO project_decisions (
                    project_id, decision_id, version, manifest_json, manifest_sha256,
                    manifest_ref, status, acceptance_ref, acceptance_sha256, indexed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, '', '', 0)
                """,
                (
                    project_id,
                    decision_id,
                    version,
                    content,
                    manifest_sha256,
                    manifest_ref.uri,
                    ProjectDecisionStatus.DRAFT.value,
                ),
            )
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise
        return self.get(project_id, decision_id, version)

    def accept(
        self,
        *,
        project_id: str,
        decision_id: str,
        version: int,
        expected_manifest_sha256: str,
        confirmed: bool,
    ) -> ProjectDecisionRecord:
        if not confirmed:
            raise ProjectDecisionValidationError("explicit project-decision acceptance is required")
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            record = self._record(project_id, decision_id, version)
            if not hmac.compare_digest(record.manifest_sha256, expected_manifest_sha256):
                raise ProjectDecisionValidationError("project-decision manifest hash mismatch")
            self._verify_manifest(record)
            if record.status is ProjectDecisionStatus.ACCEPTED:
                self._verify_acceptance(record)
                self.connection.commit()
                return record
            acceptance_content = _canonical_json(self._acceptance_payload(record))
            acceptance_ref = self.artifacts.write_text(
                self._acceptance_path(record.manifest),
                acceptance_content,
                "application/json",
            )
            self.connection.execute(
                """
                UPDATE project_decisions
                SET status = ?, acceptance_ref = ?, acceptance_sha256 = ?
                WHERE project_id = ? AND decision_id = ? AND version = ? AND status = ?
                """,
                (
                    ProjectDecisionStatus.ACCEPTED.value,
                    acceptance_ref.uri,
                    acceptance_ref.sha256,
                    project_id,
                    decision_id,
                    version,
                    ProjectDecisionStatus.DRAFT.value,
                ),
            )
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise
        return self.accepted(project_id, decision_id, version)

    def get(
        self,
        project_id: str,
        decision_id: str,
        version: int,
    ) -> ProjectDecisionRecord:
        record = self._record(project_id, decision_id, version)
        self._verify_manifest(record)
        if record.status is ProjectDecisionStatus.ACCEPTED:
            self._verify_acceptance(record)
        return record

    def accepted(
        self,
        project_id: str,
        decision_id: str,
        version: int,
    ) -> ProjectDecisionRecord:
        record = self._record(project_id, decision_id, version)
        if record.status is not ProjectDecisionStatus.ACCEPTED:
            raise ProjectDecisionValidationError("project-decision version is not accepted")
        self._verify_manifest(record)
        self._verify_acceptance(record)
        return record

    def index_accepted(
        self,
        *,
        project_id: str,
        decision_id: str,
        version: int,
        expected_manifest_sha256: str,
    ) -> int:
        selected = self.accepted(project_id, decision_id, version)
        if not hmac.compare_digest(selected.manifest_sha256, expected_manifest_sha256):
            raise ProjectDecisionValidationError("project-decision manifest hash mismatch")
        records = self._latest_accepted(project_id)
        latest = next(
            (record for record in records if record.manifest.decision_id == decision_id),
            None,
        )
        if latest is None or latest.manifest.version != version:
            raise ProjectDecisionValidationError(
                "only the latest accepted project-decision version can rebuild the index"
            )
        rendered = tuple((record, self._search_text(record.manifest)) for record in records)
        namespace = self._namespace(project_id)
        self.search.clear_namespace(namespace)
        count = 0
        for record, text in rendered:
            manifest = record.manifest
            count += self.search.index_text(
                namespace=namespace,
                source_type=SearchSourceType.DECISION,
                source_id=manifest.decision_id,
                path=(f"project:{project_id}:decision:{manifest.decision_id}:v{manifest.version}"),
                text=text,
                metadata={
                    "project_id": project_id,
                    "decision_id": manifest.decision_id,
                    "version": manifest.version,
                    "manifest_sha256": record.manifest_sha256,
                    "status": record.status.value,
                },
            )
        self.connection.execute(
            "UPDATE project_decisions SET indexed = 0 WHERE project_id = ?",
            (project_id,),
        )
        self.connection.executemany(
            """
            UPDATE project_decisions SET indexed = 1
            WHERE project_id = ? AND decision_id = ? AND version = ? AND status = ?
            """,
            (
                (
                    project_id,
                    record.manifest.decision_id,
                    record.manifest.version,
                    ProjectDecisionStatus.ACCEPTED.value,
                )
                for record in records
            ),
        )
        self.connection.commit()
        return count

    def search_accepted(
        self,
        *,
        project_id: str,
        query: str,
        top_k: int = 20,
    ) -> tuple[SearchHit, ...]:
        return self.search.search(
            query,
            top_k=top_k,
            namespaces=(self._namespace(project_id),),
            source_types=(SearchSourceType.DECISION,),
        )

    def list(
        self,
        *,
        project_id: str,
        accepted_only: bool = False,
    ) -> tuple[ProjectDecisionRecord, ...]:
        clauses = ["project_id = ?"]
        parameters: list[Any] = [project_id]
        if accepted_only:
            clauses.append("status = ?")
            parameters.append(ProjectDecisionStatus.ACCEPTED.value)
        rows = self.connection.execute(
            "SELECT decision_id, version FROM project_decisions WHERE "
            + " AND ".join(clauses)
            + " ORDER BY decision_id, version",
            parameters,
        ).fetchall()
        return tuple(self.get(project_id, str(row[0]), int(row[1])) for row in rows)

    def _latest_accepted(self, project_id: str) -> tuple[ProjectDecisionRecord, ...]:
        rows = self.connection.execute(
            """
            SELECT current.decision_id, current.version
            FROM project_decisions AS current
            WHERE current.project_id = ? AND current.status = ?
              AND current.version = (
                  SELECT MAX(candidate.version)
                  FROM project_decisions AS candidate
                  WHERE candidate.project_id = current.project_id
                    AND candidate.decision_id = current.decision_id
                    AND candidate.status = ?
              )
            ORDER BY current.decision_id
            """,
            (
                project_id,
                ProjectDecisionStatus.ACCEPTED.value,
                ProjectDecisionStatus.ACCEPTED.value,
            ),
        ).fetchall()
        return tuple(self.accepted(project_id, str(row[0]), int(row[1])) for row in rows)

    def _verify_manifest(self, record: ProjectDecisionRecord) -> None:
        try:
            content = self.artifacts.read_text_bounded_verified(
                record.manifest_ref,
                expected_sha256=record.manifest_sha256,
                max_bytes=self.max_decision_bytes,
            )
            manifest = ProjectDecisionManifest.model_validate_json(content)
        except (OSError, UnicodeError, ValueError, ValidationError) as exc:
            raise ProjectDecisionValidationError(
                "project-decision manifest failed bounded integrity verification"
            ) from exc
        if manifest != record.manifest or content != record.manifest.canonical_content():
            raise ProjectDecisionValidationError(
                "project-decision manifest no longer matches durable metadata"
            )

    def _verify_acceptance(self, record: ProjectDecisionRecord) -> None:
        if not record.acceptance_ref or not record.acceptance_sha256:
            raise ProjectDecisionValidationError(
                "accepted project decision is missing acceptance evidence"
            )
        try:
            content = self.artifacts.read_text_bounded_verified(
                record.acceptance_ref,
                expected_sha256=record.acceptance_sha256,
                max_bytes=self.max_decision_bytes,
            )
            payload = json.loads(content)
        except (OSError, UnicodeError, ValueError) as exc:
            raise ProjectDecisionValidationError(
                "project-decision acceptance failed bounded integrity verification"
            ) from exc
        expected = self._acceptance_payload(record)
        if payload != expected or content != _canonical_json(expected):
            raise ProjectDecisionValidationError(
                "project-decision acceptance no longer matches durable metadata"
            )

    def _record(
        self,
        project_id: str,
        decision_id: str,
        version: int,
    ) -> ProjectDecisionRecord:
        row = self._get_row(project_id, decision_id, version)
        if row is None:
            raise KeyError(f"{project_id}:{decision_id}:v{version}")
        try:
            manifest = ProjectDecisionManifest.model_validate_json(row[0])
            record = ProjectDecisionRecord(
                manifest=manifest,
                manifest_sha256=row[1],
                manifest_ref=row[2],
                status=ProjectDecisionStatus(row[3]),
                acceptance_ref=row[4],
                acceptance_sha256=row[5],
                indexed=bool(row[6]),
            )
        except (ValueError, ValidationError) as exc:
            raise ProjectDecisionValidationError(
                "project-decision durable metadata is invalid"
            ) from exc
        if (
            manifest.project_id != project_id
            or manifest.decision_id != decision_id
            or manifest.version != version
            or not hmac.compare_digest(manifest.canonical_hash(), record.manifest_sha256)
        ):
            raise ProjectDecisionValidationError(
                "project-decision durable metadata failed provenance validation"
            )
        return record

    def _get_row(self, project_id: str, decision_id: str, version: int):
        return self.connection.execute(
            """
            SELECT manifest_json, manifest_sha256, manifest_ref, status,
                   acceptance_ref, acceptance_sha256, indexed
            FROM project_decisions
            WHERE project_id = ? AND decision_id = ? AND version = ?
            """,
            (project_id, decision_id, version),
        ).fetchone()

    @staticmethod
    def _acceptance_payload(record: ProjectDecisionRecord) -> dict[str, Any]:
        manifest = record.manifest
        return {
            "confirmed": True,
            "decision_id": manifest.decision_id,
            "manifest_sha256": record.manifest_sha256,
            "project_id": manifest.project_id,
            "schema_version": "1",
            "version": manifest.version,
        }

    @staticmethod
    def _search_text(manifest: ProjectDecisionManifest) -> str:
        lines = [
            f"# {manifest.title}",
            "",
            "## Context",
            manifest.context,
            "",
            "## Decision",
            manifest.decision,
            "",
            "## Rationale",
            manifest.rationale,
        ]
        if manifest.alternatives:
            lines.extend(["", "## Alternatives"])
            lines.extend(f"- {item}" for item in manifest.alternatives)
        if manifest.consequences:
            lines.extend(["", "## Consequences"])
            lines.extend(f"- {item}" for item in manifest.consequences)
        return "\n".join(lines) + "\n"

    @staticmethod
    def _manifest_path(manifest: ProjectDecisionManifest) -> str:
        return (
            f"project-decisions/{manifest.project_id}/{manifest.decision_id}/"
            f"v{manifest.version}/manifest.json"
        )

    @staticmethod
    def _acceptance_path(manifest: ProjectDecisionManifest) -> str:
        return (
            f"project-decisions/{manifest.project_id}/{manifest.decision_id}/"
            f"v{manifest.version}/acceptance.json"
        )

    @staticmethod
    def _namespace(project_id: str) -> str:
        return f"explicit:project-decisions:{project_id}"


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
