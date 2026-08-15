"""Example host adapter. Keep real authentication/configuration outside the public repository."""

from universal_coding_agent.core.models import (
    ModelCapabilities,
    ModelRequest,
    ModelResponse,
)


class ExistingClientAdapter:
    def __init__(self, client):
        self._client = client

    def probe(self) -> bool:
        # Replace with one minimal approved call through the existing client.
        return True

    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            structured_output=True,
            tool_calls=False,
            reasoning_tokens=True,
            actual_model_identity=True,
        )

    def invoke(self, request: ModelRequest) -> ModelResponse:
        # Translate the generic request into the host client's request shape.
        # Never expose a credential or raw authorization header.
        response = self._client.invoke(
            role=request.role,
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            response_schema=request.response_schema,
            max_output_tokens=request.max_output_tokens,
        )
        return ModelResponse(
            content=response.content,
            structured=getattr(response, "structured", None),
            actual_model=getattr(response, "actual_model", None),
            finish_reason=getattr(response, "finish_reason", None),
            completion_tokens=getattr(response, "completion_tokens", None),
            reasoning_tokens=getattr(response, "reasoning_tokens", None),
        )


def create_provider():
    # Import the host client factory here so the public core remains independent.
    # from site_specific_client import create_client
    # return ExistingClientAdapter(create_client())
    raise RuntimeError("configure this example in a private host adapter")
