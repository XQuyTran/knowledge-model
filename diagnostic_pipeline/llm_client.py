import os
from typing import Optional

from openai import OpenAI

try:
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
except Exception:  # pragma: no cover - optional dependency
    DefaultAzureCredential = None
    get_bearer_token_provider = None


def _normalize_azure_base_url(endpoint: str) -> str:
    endpoint = endpoint.rstrip("/")
    if endpoint.endswith("/openai/v1"):
        return endpoint + "/"
    return endpoint + "/openai/v1/"


def build_llm_client_from_env() -> Optional[OpenAI]:
    """Build a direct official OpenAI client.

    - OpenAI public API: OpenAI(api_key=..., base_url=optional)
    - Azure OpenAI v1 API: OpenAI(base_url='https://<resource>.openai.azure.com/openai/v1/', api_key=...)

    This function intentionally returns the official ``OpenAI`` client directly,
    without any project-specific wrapper class.
    """
    timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "20.0"))

    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_use_entra_id = os.getenv("AZURE_OPENAI_USE_ENTRA_ID", "false").lower() in {"1", "true", "yes"}

    if azure_endpoint:
        base_url = _normalize_azure_base_url(azure_endpoint)
        if azure_use_entra_id:
            if DefaultAzureCredential is None or get_bearer_token_provider is None:
                raise RuntimeError(
                    "azure-identity is required for Azure Entra ID authentication. "
                    "Install with: pip install azure-identity"
                )
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://ai.azure.com/.default",
            )
            return OpenAI(base_url=base_url, api_key=token_provider(), timeout=timeout_seconds)
        if not azure_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is required when AZURE_OPENAI_ENDPOINT is set.")
        return OpenAI(base_url=base_url, api_key=azure_api_key, timeout=timeout_seconds)

    openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_API_BASE_URL")
    if not openai_api_key:
        return None

    kwargs = {"api_key": openai_api_key, "timeout": timeout_seconds}
    if openai_base_url:
        kwargs["base_url"] = openai_base_url.rstrip("/")
    return OpenAI(**kwargs)
