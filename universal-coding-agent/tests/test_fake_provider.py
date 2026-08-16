from universal_coding_agent.providers.fake import FakeModelProvider, create_provider


def test_builtin_fake_provider_factory() -> None:
    provider = create_provider()
    assert isinstance(provider, FakeModelProvider)
    assert provider.probe() is True
    assert provider.capabilities().structured_output is True
