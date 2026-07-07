from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Optional

from openai import AzureOpenAI, OpenAI

from .interfaces import LLMClient

try:
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
except Exception:  # pragma: no cover - optional dependency
    DefaultAzureCredential = None
    get_bearer_token_provider = None


@dataclass(frozen=True)
class LLMConnectionSettings:
    provider: str
    model: str
    timeout_seconds: float = 20.0
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    azure_api_version: Optional[str] = None
    azure_deployment: Optional[str] = None
    azure_use_entra_id: bool = False


class OpenAICompatibleLLMClient(LLMClient):
    """Thin adapter around the official OpenAI/Azure OpenAI Python SDK.

    This class preserves the existing ``LLMClient`` interface used by the
    pipeline while delegating all transport/authentication to the official SDK.
    """

    def __init__(
        self,
        *,
        provider: str,
        model: str,
        timeout_seconds: float = 20.0,
        api_key: Optional[str] = None,
        api_base_url: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        azure_use_entra_id: bool = False,
    ) -> None:
        self.provider = provider
        self.model = model
        self.timeout_seconds = timeout_seconds
        if provider == "azure-openai":
            if not azure_deployment:
                raise ValueError("Azure OpenAI requires explicit deployment name")
            self.azure_deployment = azure_deployment
        else:
            self.azure_deployment = None

        if provider == "azure-openai":
            if not api_base_url:
                raise ValueError("Azure OpenAI requires AZURE_OPENAI_ENDPOINT or LLM_API_BASE_URL.")

            if azure_use_entra_id:
                if DefaultAzureCredential is None or get_bearer_token_provider is None:
                    raise RuntimeError(
                        "azure-identity is required for Azure Entra ID authentication. "
                        "Install with: pip install azure-identity"
                    )
                token_provider = get_bearer_token_provider(
                    DefaultAzureCredential(),
                    "https://cognitiveservices.azure.com/.default",
                )
                self.client = AzureOpenAI(
                    azure_endpoint=api_base_url.rstrip("/"),
                    api_version=azure_api_version or "2026-01-01-preview",
                    azure_ad_token_provider=token_provider,
                    timeout=timeout_seconds,
                )
            else:
                if not api_key:
                    raise ValueError("Azure OpenAI requires AZURE_OPENAI_API_KEY (or enable Entra ID).")
                self.client = AzureOpenAI(
                    azure_endpoint=api_base_url.rstrip("/"),
                    api_key=api_key,
                    api_version=azure_api_version or "2026-01-01-preview",
                    timeout=timeout_seconds,
                )
        else:
            if not api_key:
                raise ValueError("OpenAI requires OPENAI_API_KEY or LLM_API_KEY.")
            kwargs = {"api_key": api_key, "timeout": timeout_seconds}
            if api_base_url:
                kwargs["base_url"] = api_base_url.rstrip("/")
            self.client = OpenAI(**kwargs)

    def complete_json(self, system_prompt: str, user_prompt: str, schema_hint: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.azure_deployment if self.provider == "azure-openai" else self.model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt + "\nReturn strictly valid JSON that follows this schema hint:\n" + schema_hint,
                },
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return self._parse_json(content)

    def _parse_json(self, content: str) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", content)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Model response is not valid JSON: {content[:500]}")


def load_llm_settings_from_env() -> Optional[LLMConnectionSettings]:
    timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "20.0"))

    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_use_entra_id = os.getenv("AZURE_OPENAI_USE_ENTRA_ID", "false").lower() in {"1", "true", "yes"}

    if azure_endpoint and (azure_api_key or azure_use_entra_id or azure_deployment):
        return LLMConnectionSettings(
            provider="azure-openai",
            api_base_url=azure_endpoint,
            api_key=azure_api_key,
            model=os.getenv("LLM_MODEL", azure_deployment or ""),
            timeout_seconds=timeout_seconds,
            azure_api_version=azure_api_version,
            azure_deployment=azure_deployment,
            azure_use_entra_id=azure_use_entra_id,
        )

    openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_API_BASE_URL")
    openai_model = os.getenv("OPENAI_MODEL") or os.getenv("LLM_MODEL")

    if openai_api_key and openai_model:
        return LLMConnectionSettings(
            provider="openai",
            api_base_url=openai_base_url,
            api_key=openai_api_key,
            model=openai_model,
            timeout_seconds=timeout_seconds,
        )

    return None


def build_llm_client_from_env() -> Optional[LLMClient]:
    settings = load_llm_settings_from_env()
    if settings is None:
        return None
    return OpenAICompatibleLLMClient(
        provider=settings.provider,
        model=settings.model,
        timeout_seconds=settings.timeout_seconds,
        api_key=settings.api_key,
        api_base_url=settings.api_base_url,
        azure_api_version=settings.azure_api_version,
        azure_deployment=settings.azure_deployment,
        azure_use_entra_id=settings.azure_use_entra_id,
    )
