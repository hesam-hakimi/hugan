from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock


class PublicationIntentConflict(RuntimeError):
    """Raised when one approval is reused with a different publication intent."""


@dataclass(frozen=True)
class PublicationRecord:
    publication_id: str
    task_id: str
    approval_sha256: str
    intent_sha256: str
    status: str
    request: dict[str, object]
    receipt: dict[str, object] | None
    attempts: int
    created_at: str
    updated_at: str


class SourceControlPublicationStore:
    """Durable, single-intent reservation for exact source-control publication.

    The database is deliberately separate from LangGraph checkpoints. A process crash may leave
    a record in ``planned`` state; failed attempts retain per-attempt receipts while the same exact
    retry can ask the adapter to reconcile its fixed local/remote targets. A conflicting retry never
    reaches the adapter, and only a completed receipt is terminal.
    """

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self.connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
            timeout=30.0,
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS source_control_publications (
                publication_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL UNIQUE,
                approval_sha256 TEXT NOT NULL UNIQUE,
                intent_sha256 TEXT NOT NULL,
                status TEXT NOT NULL,
                request_json TEXT NOT NULL,
                receipt_json TEXT,
                attempts INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                CHECK(status IN ('planned', 'completed', 'failed'))
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS source_control_publication_attempts (
                publication_id TEXT NOT NULL,
                attempt INTEGER NOT NULL,
                outcome TEXT NOT NULL,
                receipt_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (publication_id, attempt),
                CHECK(outcome IN ('completed', 'failed')),
                FOREIGN KEY(publication_id)
                    REFERENCES source_control_publications(publication_id)
            )
            """
        )
        self.connection.commit()

    def close(self) -> None:
        with self._lock:
            self.connection.close()

    def reserve(
        self,
        *,
        publication_id: str,
        task_id: str,
        approval_sha256: str,
        intent_sha256: str,
        request: dict[str, object],
    ) -> PublicationRecord:
        request_json = json.dumps(
            request,
            separators=(",", ":"),
            sort_keys=True,
            ensure_ascii=False,
        )
        now = datetime.now(UTC).isoformat()
        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                row = self.connection.execute(
                    """
                    SELECT publication_id, task_id, approval_sha256, intent_sha256,
                           status, request_json, receipt_json, attempts,
                           created_at, updated_at
                    FROM source_control_publications
                    WHERE task_id = ? OR approval_sha256 = ? OR publication_id = ?
                    """,
                    (task_id, approval_sha256, publication_id),
                ).fetchone()
                if row is not None:
                    existing = self._record(row)
                    if (
                        existing.publication_id != publication_id
                        or existing.task_id != task_id
                        or existing.approval_sha256 != approval_sha256
                        or existing.intent_sha256 != intent_sha256
                        or self._canonical(existing.request) != request_json
                    ):
                        raise PublicationIntentConflict(
                            "publish approval already has a different immutable intent"
                        )
                    if existing.status == "completed":
                        self.connection.commit()
                        return existing
                    if existing.status == "failed" and existing.receipt is not None:
                        self._insert_attempt(
                            existing.publication_id,
                            existing.attempts,
                            "failed",
                            existing.receipt,
                            existing.updated_at,
                        )
                    elif (
                        existing.status == "planned"
                        and self.get_attempt(existing.publication_id, existing.attempts)
                        is None
                    ):
                        self._insert_attempt(
                            existing.publication_id,
                            existing.attempts,
                            "failed",
                            self._interrupted_receipt(existing),
                            now,
                        )
                    self.connection.execute(
                        """
                        UPDATE source_control_publications
                        SET status = 'planned', attempts = attempts + 1, updated_at = ?
                        WHERE publication_id = ?
                        """,
                        (now, publication_id),
                    )
                    self.connection.commit()
                    return self.get_required(publication_id)

                self.connection.execute(
                    """
                    INSERT INTO source_control_publications(
                        publication_id, task_id, approval_sha256, intent_sha256,
                        status, request_json, receipt_json, attempts,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 'planned', ?, NULL, 1, ?, ?)
                    """,
                    (
                        publication_id,
                        task_id,
                        approval_sha256,
                        intent_sha256,
                        request_json,
                        now,
                        now,
                    ),
                )
                self.connection.commit()
                return self.get_required(publication_id)
            except BaseException:
                if self.connection.in_transaction:
                    self.connection.rollback()
                raise

    def complete(
        self,
        publication_id: str,
        receipt: dict[str, object],
    ) -> PublicationRecord:
        return self._finish(publication_id, "completed", receipt)

    def record_retryable_failure(
        self,
        publication_id: str,
        receipt: dict[str, object],
    ) -> PublicationRecord:
        receipt_json = self._canonical(receipt)
        now = datetime.now(UTC).isoformat()
        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                current = self.get_required(publication_id)
                if current.status != "planned":
                    raise PublicationIntentConflict(
                        "only a planned publication can record a retryable failure"
                    )
                self._insert_attempt(
                    publication_id,
                    current.attempts,
                    "failed",
                    receipt,
                    now,
                )
                self.connection.execute(
                    """
                    UPDATE source_control_publications
                    SET receipt_json = ?, updated_at = ?
                    WHERE publication_id = ? AND status = 'planned'
                    """,
                    (receipt_json, now, publication_id),
                )
                self.connection.commit()
                return self.get_required(publication_id)
            except BaseException:
                if self.connection.in_transaction:
                    self.connection.rollback()
                raise

    def attempt_receipts(
        self,
        publication_id: str,
    ) -> tuple[dict[str, object], ...]:
        with self._lock:
            rows = self.connection.execute(
                """
                SELECT receipt_json
                FROM source_control_publication_attempts
                WHERE publication_id = ?
                ORDER BY attempt
                """,
                (publication_id,),
            ).fetchall()
            return tuple(json.loads(row[0]) for row in rows)

    def get_attempt(
        self,
        publication_id: str,
        attempt: int,
    ) -> tuple[str, dict[str, object]] | None:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT outcome, receipt_json
                FROM source_control_publication_attempts
                WHERE publication_id = ? AND attempt = ?
                """,
                (publication_id, attempt),
            ).fetchone()
            if row is None:
                return None
            return str(row[0]), json.loads(row[1])

    def get(self, publication_id: str) -> PublicationRecord | None:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT publication_id, task_id, approval_sha256, intent_sha256,
                       status, request_json, receipt_json, attempts,
                       created_at, updated_at
                FROM source_control_publications WHERE publication_id = ?
                """,
                (publication_id,),
            ).fetchone()
            return self._record(row) if row is not None else None

    def get_for_authority(
        self,
        *,
        task_id: str,
        approval_sha256: str,
    ) -> PublicationRecord | None:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT publication_id, task_id, approval_sha256, intent_sha256,
                       status, request_json, receipt_json, attempts,
                       created_at, updated_at
                FROM source_control_publications
                WHERE task_id = ? OR approval_sha256 = ?
                """,
                (task_id, approval_sha256),
            ).fetchone()
            return self._record(row) if row is not None else None

    def get_required(self, publication_id: str) -> PublicationRecord:
        record = self.get(publication_id)
        if record is None:
            raise KeyError(publication_id)
        return record

    def _finish(
        self,
        publication_id: str,
        status: str,
        receipt: dict[str, object],
    ) -> PublicationRecord:
        receipt_json = self._canonical(receipt)
        now = datetime.now(UTC).isoformat()
        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                current = self.get_required(publication_id)
                if current.status in {"completed", "failed"}:
                    if (
                        current.status != status
                        or self._canonical(current.receipt or {}) != receipt_json
                    ):
                        raise PublicationIntentConflict(
                            "source-control publication receipt is immutable"
                        )
                    self.connection.commit()
                    return current
                self.connection.execute(
                    """
                    UPDATE source_control_publications
                    SET status = ?, receipt_json = ?, updated_at = ?
                    WHERE publication_id = ? AND status = 'planned'
                    """,
                    (status, receipt_json, now, publication_id),
                )
                self._insert_attempt(
                    publication_id,
                    current.attempts,
                    status,
                    receipt,
                    now,
                )
                self.connection.commit()
                return self.get_required(publication_id)
            except BaseException:
                if self.connection.in_transaction:
                    self.connection.rollback()
                raise

    @staticmethod
    def _record(row) -> PublicationRecord:
        receipt = json.loads(row[6]) if row[6] is not None else None
        return PublicationRecord(
            publication_id=row[0],
            task_id=row[1],
            approval_sha256=row[2],
            intent_sha256=row[3],
            status=row[4],
            request=json.loads(row[5]),
            receipt=receipt,
            attempts=int(row[7]),
            created_at=row[8],
            updated_at=row[9],
        )

    @staticmethod
    def _canonical(value: dict[str, object]) -> str:
        return json.dumps(
            value,
            separators=(",", ":"),
            sort_keys=True,
            ensure_ascii=False,
        )

    def _insert_attempt(
        self,
        publication_id: str,
        attempt: int,
        outcome: str,
        receipt: dict[str, object],
        created_at: str,
    ) -> None:
        receipt_json = self._canonical(receipt)
        existing = self.connection.execute(
            """
            SELECT outcome, receipt_json
            FROM source_control_publication_attempts
            WHERE publication_id = ? AND attempt = ?
            """,
            (publication_id, attempt),
        ).fetchone()
        if existing is not None:
            if existing[0] != outcome or existing[1] != receipt_json:
                raise PublicationIntentConflict(
                    "source-control publication attempt receipt is immutable"
                )
            return
        self.connection.execute(
            """
            INSERT INTO source_control_publication_attempts(
                publication_id, attempt, outcome, receipt_json, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                publication_id,
                attempt,
                outcome,
                receipt_json,
                created_at,
            ),
        )

    @staticmethod
    def _interrupted_receipt(record: PublicationRecord) -> dict[str, object]:
        return {
            "schema_version": "1",
            "status": "interrupted",
            "qualified": False,
            "attempt": record.attempts,
            **record.request,
            "adapter": record.request.get("adapter_identity", "unknown"),
            "error": {
                "code": "previous_attempt_interrupted",
                "stage": "unknown",
                "cause_type": "ProcessInterruption",
            },
            "partial_effects": {
                "commit_created": False,
                "commit_sha": "",
                "local_ref_attempted": False,
                "local_ref_verified": False,
                "local_ref_created": False,
                "local_ref_updated": False,
                "local_ref": "",
                "push_attempted": False,
                "push_verified": False,
                "remote_sha": "",
                "draft_pr_attempted": False,
                "draft_pr_created": False,
                "draft_pr_url": "",
            },
            "source_repository_modified": None,
            "merge_performed": False,
            "deployment_performed": False,
            "side_effects_indeterminate": True,
            "effect_attribution_indeterminate": True,
            "retryable": True,
            "reconciliation_required": True,
        }
