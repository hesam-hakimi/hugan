from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from universal_coding_agent.core.models import ProjectManifest, RepositorySpec
from universal_coding_agent.core.safe_models import SafeModePolicy
from universal_coding_agent.discovered_safe_service import DiscoveredSafeAgentService
from universal_coding_agent.product.call_graphs import RepositoryCallGraphService
from universal_coding_agent.product.context_documents import ContextDocumentService
from universal_coding_agent.product.coverage_evidence import RepositoryCoverageEvidenceService
from universal_coding_agent.product.coverage_selection import (
    RepositoryCoverageSelectionService,
)
from universal_coding_agent.product.dependency_graphs import RepositoryDependencyService
from universal_coding_agent.product.dispatch_evidence import RepositoryDispatchEvidenceService
from universal_coding_agent.product.knowledge_packs import ProjectKnowledgePackService
from universal_coding_agent.product.lifecycle_reservations import (
    DurableLifecycleReservationStore,
)
from universal_coding_agent.product.models import (
    ContextDocument,
    ContextScope,
    DocumentRole,
    ProgramExecutionBinding,
)
from universal_coding_agent.product.program_orchestrator import ProgramOrchestrator
from universal_coding_agent.product.project_decisions import ProjectDecisionService
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.product.repository_indexes import RepositoryIndexService
from universal_coding_agent.product.requirement_alignment import RequirementAlignmentService
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.base import (
    ModelProvider,
    RemoteOperationLeaseAwareProvider,
)
from universal_coding_agent.storage.artifacts import ArtifactStore


@dataclass
class ProductWorkspace:
    root: Path
    provider: ModelProvider
    artifacts: ArtifactStore
    documents: ContextDocumentService
    knowledge_packs: ProjectKnowledgePackService
    project_decisions: ProjectDecisionService
    repository_indexes: RepositoryIndexService
    dependency_graphs: RepositoryDependencyService
    call_graphs: RepositoryCallGraphService
    dispatch_evidence: RepositoryDispatchEvidenceService
    coverage_evidence: RepositoryCoverageEvidenceService
    coverage_selection: RepositoryCoverageSelectionService
    search: SearchService
    requirements: RequirementAlignmentService
    programs: ProgramOrchestrator
    control: TaskControlService
    remote_operations: SqliteRemoteOperationLeaseStore
    lifecycle_reservations: DurableLifecycleReservationStore

    @classmethod
    def create(cls, root: Path, provider: ModelProvider) -> ProductWorkspace:
        root = root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        artifacts = ArtifactStore(root / "artifacts")
        search = SearchService(root / "knowledge.sqlite")
        control = TaskControlService(root / "control.sqlite")
        remote_operations = SqliteRemoteOperationLeaseStore(
            root / "private-remote-operations.sqlite"
        )
        lifecycle_reservations = DurableLifecycleReservationStore(
            root / "lifecycle-reservations.sqlite"
        )
        if isinstance(provider, RemoteOperationLeaseAwareProvider):
            provider.bind_remote_operation_store(remote_operations.provider_store())
        documents = ContextDocumentService(root / "documents.sqlite", artifacts)
        knowledge_packs = ProjectKnowledgePackService(
            root / "knowledge-packs.sqlite",
            artifacts,
            documents,
            search,
        )
        project_decisions = ProjectDecisionService(
            root / "project-decisions.sqlite",
            artifacts,
            search,
        )
        repository_indexes = RepositoryIndexService(artifacts, search)
        dependency_graphs = RepositoryDependencyService(
            artifacts,
            search,
            repository_indexes,
        )
        call_graphs = RepositoryCallGraphService(
            artifacts,
            search,
            dependency_graphs,
        )
        dispatch_evidence = RepositoryDispatchEvidenceService(
            artifacts,
            search,
            call_graphs,
        )
        coverage_evidence = RepositoryCoverageEvidenceService(
            artifacts,
            search,
            dispatch_evidence,
        )
        coverage_selection = RepositoryCoverageSelectionService(
            artifacts,
            coverage_evidence,
        )
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
            knowledge_packs=knowledge_packs,
            project_decisions=project_decisions,
            repository_indexes=repository_indexes,
            dependency_graphs=dependency_graphs,
            call_graphs=call_graphs,
            dispatch_evidence=dispatch_evidence,
            coverage_evidence=coverage_evidence,
            coverage_selection=coverage_selection,
            search=search,
            requirements=requirements,
            programs=programs,
            control=control,
            remote_operations=remote_operations,
            lifecycle_reservations=lifecycle_reservations,
        )

    def close(self) -> None:
        self.programs.close()
        self.project_decisions.close()
        self.knowledge_packs.close()
        self.documents.close()
        self.search.close()
        self.control.close()
        self.remote_operations.close()
        self.lifecycle_reservations.close()

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
            remote_operations=self.remote_operations,
        )

    def start_next_program_execution(
        self,
        *,
        program_id: str,
        current_requirement_hash: str,
        repository: RepositorySpec,
        policy: SafeModePolicy,
        test_profiles: tuple[str, ...],
        state_root: Path | None = None,
        allow_local_sources: bool = False,
    ) -> ProgramExecutionBinding:
        executor = self.discovered_safe(
            state_root=state_root,
            allow_local_sources=allow_local_sources,
        )
        return self.programs.start_next_execution(
            program_id=program_id,
            current_requirement_hash=current_requirement_hash,
            repository=repository,
            policy=policy,
            test_profiles=test_profiles,
            executor=executor,
        )

    def continue_program_execution(
        self,
        *,
        program_id: str,
        task_id: str,
        current_requirement_hash: str,
        approved: bool,
        state_root: Path | None = None,
        allow_local_sources: bool = False,
    ) -> ProgramExecutionBinding:
        executor = self.discovered_safe(
            state_root=state_root,
            allow_local_sources=allow_local_sources,
        )
        return self.programs.continue_execution(
            program_id=program_id,
            task_id=task_id,
            current_requirement_hash=current_requirement_hash,
            executor=executor,
            approved=approved,
        )
