from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider


def test_product_workspace_discovered_safe_shares_task_control(tmp_path):
    workspace = ProductWorkspace.create(tmp_path / "workspace", FakeModelProvider())
    try:
        discovered = workspace.discovered_safe(
            state_root=tmp_path / "safe-state",
            allow_local_sources=True,
        )
        assert discovered.control is workspace.control
    finally:
        workspace.close()
