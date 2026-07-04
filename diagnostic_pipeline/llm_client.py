from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

from .interfaces import LLMClient


@dataclass(frozen=True)
class LLMConnectionSettings:
    provider: str
    api_base_url: str
    api_key: str
    model: str
    timeout_seconds: float = 20.0
    azure_api_version: Optional[str] = None
    azure_deployment: Optional[str] = None


class OpenAICompatibleLLMClient(LLMClient):
    """HTTP client for OpenAI-compatible chat completion APIs.

    Supported environment-variable modes:

    1. Generic OpenAI-compatible endpoint
       - LLM_API_BASE_URL
       - LLM_API_KEY
       - LLM_MODEL
       - LLM_TIMEOUT_SECONDS (optional)

    2. Azure OpenAI endpoint
       - AZURE_OPENAI_ENDPOINT
       - AZURE_OPENAI_API_KEY
       - AZURE_OPENAI_DEPLOYMENT
       - AZURE_OPENAI_API_VERSION (optional, default: 2026-01-01-preview)
       - LLM_MODEL (optional display name only)
       - LLM_TIMEOUT_SECONDS (optional)
    """

    def __init__(self, api_base_url: str, api_key: str, model: str, timeout_seconds: float = 20.0):
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_env(cls) -> LLMClient:
        client = build_llm_client_from_env()
        if client is None:
            raise RuntimeError(
                "LLM environment variables are not configured. "
                "Set either LLM_API_BASE_URL/LLM_API_KEY/LLM_MODEL or "
                "AZURE_OPENAI_ENDPOINT/AZURE_OPENAI_API_KEY/AZURE_OPENAI_DEPLOYMENT."
            )
        return client

    def _build_url(self) -> str:
        return f'{self.api_base_url}/chat/completions'

    def _build_headers(self) -> dict:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

    def _build_payload(self, system_prompt: str, user_prompt: str, schema_hint: str) -> dict:
        return {
            'model': self.model,
            'temperature': 0.1,
            'response_format': {'type': 'json_object'},
            'messages': [{'role': 'system', 'content': system_prompt + 'Return valid JSON only. Schema hint:' + schema_hint},
                {'role': 'user', 'content': user_prompt},
            ],
        }

    def complete_json(self, system_prompt: str, user_prompt: str, schema_hint: str) -> dict:
        payload = self._build_payload(system_prompt, user_prompt, schema_hint)
        req = urllib.request.Request(
            url=self._build_url(),
            data=json.dumps(payload).encode('utf-8'),
            headers=self._build_headers(),
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            body = json.loads(response.read().decode('utf-8'))
        content = body['choices'][0]['message']['content']
        return json.loads(content)


class AzureOpenAIClient(OpenAICompatibleLLMClient):
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str,
        model: str | None = None,
        timeout_seconds: float = 20.0,
    ):
        self.endpoint = endpoint.rstrip('/')
        self.deployment = deployment
        self.api_version = api_version
        super().__init__(api_base_url=self.endpoint, api_key=api_key, model=model or deployment, timeout_seconds=timeout_seconds)

    def _build_url(self) -> str:
        base = f'{self.endpoint}/openai/deployments/{self.deployment}/chat/completions'
        query = urllib.parse.urlencode({'api-version': self.api_version})
        return f'{base}?{query}'

    def _build_headers(self) -> dict:
        return {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
        }

    def _build_payload(self, system_prompt: str, user_prompt: str, schema_hint: str) -> dict:
        # Azure uses deployment in URL, not model in payload.
        return {
            'temperature': 0.1,
            'response_format': {'type': 'json_object'},
            'messages': [
                {'role': 'system', 'content': system_prompt + 'Return valid JSON only. Schema hint: ' + schema_hint},
                {'role': 'user', 'content': user_prompt},
            ],
        }


def load_llm_settings_from_env() -> Optional[LLMConnectionSettings]:
    timeout_seconds = float(os.getenv('LLM_TIMEOUT_SECONDS', '20.0'))

    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
    azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
    azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2026-01-01-preview')

    if azure_endpoint and azure_api_key and azure_deployment:
        return LLMConnectionSettings(
            provider='azure-openai',
            api_base_url=azure_endpoint.rstrip('/'),
            api_key=azure_api_key,
            model=os.getenv('LLM_MODEL', azure_deployment),
            timeout_seconds=timeout_seconds,
            azure_api_version=azure_api_version,
            azure_deployment=azure_deployment,
        )

    api_base_url = os.getenv('LLM_API_BASE_URL')
    api_key = os.getenv('LLM_API_KEY')
    model = os.getenv('LLM_MODEL')
    if api_base_url and api_key and model:
        return LLMConnectionSettings(
            provider='openai-compatible',
            api_base_url=api_base_url.rstrip('/'),
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
        )
    return None


def build_llm_client_from_env() -> Optional[LLMClient]:
    settings = load_llm_settings_from_env()
    if settings is None:
        return None
    if settings.provider == 'azure-openai':
        return AzureOpenAIClient(
            endpoint=settings.api_base_url,
            api_key=settings.api_key,
            deployment=settings.azure_deployment or settings.model,
            api_version=settings.azure_api_version or '2026-01-01-preview',
            model=settings.model,
            timeout_seconds=settings.timeout_seconds,
        )
    return OpenAICompatibleLLMClient(
        api_base_url=settings.api_base_url,
        api_key=settings.api_key,
        model=settings.model,
        timeout_seconds=settings.timeout_seconds,
    )
