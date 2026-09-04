from universal_coding_agent.providers.fake import FakeModelProvider


def test_product_workspace_discovered_safe_shares_task_control(tmp_path):
    from universal_coding_agent.product.workspace import ProductWorkspace

    workspace = ProductWorkspace.create(tmp_path / "workspace", FakeModelProvider())
    try:
        discovered = workspace.discovered_safe(
            state_root=tmp_path / "safe-state",
            allow_local_sources=True,
        )
        assert discovered.control is workspace.control
        assert workspace.coverage_selection.artifacts is workspace.artifacts
        assert (
            workspace.coverage_selection.coverage_evidence
            is workspace.coverage_evidence
        )
        assert (
            workspace.coverage_selection.dispatch_evidence
            is workspace.dispatch_evidence
        )
    finally:
        workspace.close()


def test_product_public_exports_are_cycle_safe_after_safe_service_import():
    from universal_coding_agent.product import (
        ProductWorkspace,
        RepositoryCoverageEvidenceService,
        RepositoryCoverageSelectionService,
        TaskControlService,
    )
    from universal_coding_agent.safe_service import SafeAgentService

    assert SafeAgentService is not None
    assert ProductWorkspace.__name__ == "ProductWorkspace"
    assert RepositoryCoverageEvidenceService.__name__ == (
        "RepositoryCoverageEvidenceService"
    )
    assert RepositoryCoverageSelectionService.__name__ == (
        "RepositoryCoverageSelectionService"
    )
    assert TaskControlService.__name__ == "TaskControlService"
