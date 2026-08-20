from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from universal_coding_agent.core.models import ProjectManifest
from universal_coding_agent.discovered_safe_service import DiscoveredSafeAgentService
from universal_coding_agent.product.context_documents import ContextDocumentService
from universal_coding_agent.product.models import ContextDocument, ContextScope, DocumentRole
from universal_coding_agent.product.program_orchestrator import ProgramOrchestrator
from universal_coding_agent.product.requirement_alignment import RequirementAlignmentService
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.base import ModelProvider
from universal_coding_agent.storage.artifacts import ArtifactStore


@dataclass
class ProductWorkspace:
    root: Path
    provider: ModelProvider
    artifacts: ArtifactStore
    documents: ContextDocumentService
    search: SearchService
    requirements: RequirementAlignmentService
    programs: ProgramOrchestrator
    control: TaskControlService

    @classmethod
    def create(cls, root: Path, provider: ModelProvider) -> ProductWorkspace:
        root = root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        artifacts = ArtifactStore(root / "artifacts")
        search = SearchService(root / "knowledge.sqlite")
        control = TaskControlService(root / "control.sqlite")
        documents = ContextDocumentService(root / "documents.sqlite", artifacts)
        requirements = RequirementAlignmentService(artifacts, provider, search)
        programs = ProgramOrchestrator(
            root / "programs.sqlite",
            artifacts,
            provider,
            search,
            control,
        )
        return cls(
            root=root,
            provider=provider,
            artifacts=artifacts,
            documents=documents,
            search=search,
            requirements=requirements,
            programs=programs,
            control=control,
        )

    def close(self) -> None:
        self.programs.close()
        self.documents.close()
        self.search.close()
        self.control.close()

    def upload_document(
        self,
        *,
        document_id: str,
        filename: str,
        content: bytes | str,
        role: DocumentRole,
        scope: ContextScope,
        scope_id: str,
    ) -> ContextDocument:
        document = self.documents.ingest(
            document_id=document_id,
            filename=filename,
            content=content,
            role=role,
            scope=scope,
            scope_id=scope_id,
        )
        self.search.index_document(document, self.artifacts)
        return document

    def index_repository(
        self,
        root: Path,
        manifest: ProjectManifest,
        *,
        namespace: str = "repository",
    ) -> int:
        return self.search.index_repository(root, manifest, namespace=namespace)

    def discovered_safe(
        self,
        *,
        state_root: Path | None = None,
        allow_local_sources: bool = False,
    ) -> DiscoveredSafeAgentService:
        return DiscoveredSafeAgentService.create(
            state_root or (self.root / "safe"),
            self.provider,
            allow_local_sources=allow_local_sources,
            control=self.control,
        )
