from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "RepositoryCallGraphService": (
        "universal_coding_agent.product.call_graphs",
        "RepositoryCallGraphService",
    ),
    "RepositoryDispatchEvidenceService": (
        "universal_coding_agent.product.dispatch_evidence",
        "RepositoryDispatchEvidenceService",
    ),
    "RepositoryCoverageEvidenceService": (
        "universal_coding_agent.product.coverage_evidence",
        "RepositoryCoverageEvidenceService",
    ),
    "RepositoryCoverageSelectionService": (
        "universal_coding_agent.product.coverage_selection",
        "RepositoryCoverageSelectionService",
    ),
    "RepositoryCoverageTestExecutionService": (
        "universal_coding_agent.product.coverage_execution",
        "RepositoryCoverageTestExecutionService",
    ),
    "ContextDocumentService": (
        "universal_coding_agent.product.context_documents",
        "ContextDocumentService",
    ),
    "DurableLifecycleReservationStore": (
        "universal_coding_agent.product.lifecycle_reservations",
        "DurableLifecycleReservationStore",
    ),
    "ProjectKnowledgePackService": (
        "universal_coding_agent.product.knowledge_packs",
        "ProjectKnowledgePackService",
    ),
    "ProjectDecisionService": (
        "universal_coding_agent.product.project_decisions",
        "ProjectDecisionService",
    ),
    "RepositoryIndexService": (
        "universal_coding_agent.product.repository_indexes",
        "RepositoryIndexService",
    ),
    "RepositoryDependencyService": (
        "universal_coding_agent.product.dependency_graphs",
        "RepositoryDependencyService",
    ),
    "ProgramOrchestrator": (
        "universal_coding_agent.product.program_orchestrator",
        "ProgramOrchestrator",
    ),
    "ProductWorkspace": (
        "universal_coding_agent.product.workspace",
        "ProductWorkspace",
    ),
    "RequirementAlignmentService": (
        "universal_coding_agent.product.requirement_alignment",
        "RequirementAlignmentService",
    ),
    "SearchService": (
        "universal_coding_agent.product.search_service",
        "SearchService",
    ),
    "SqliteRemoteOperationLeaseStore": (
        "universal_coding_agent.product.remote_operations",
        "SqliteRemoteOperationLeaseStore",
    ),
    "TaskControlService": (
        "universal_coding_agent.product.task_control",
        "TaskControlService",
    ),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = target
    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value
