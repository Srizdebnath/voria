"""
Dynamic model discovery for all LLM providers.
Fetches available models at runtime based on API keys.
"""

import asyncio
import httpx
from dataclasses import dataclass, asdict
from typing import List, Optional
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about an available model."""

    name: str
    display_name: str
    tokens_per_hour: Optional[int] = None
    max_tokens: Optional[int] = None
    description: str = ""


class ModelDiscovery:
    """Fetch available models from LLM providers."""

    @staticmethod
    async def fetch_generic_openai_compatible(
        api_key: str, base_url: str, provider_name: str
    ) -> List[ModelInfo]:
        """Fetch models from an OpenAI-compatible API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url.rstrip('/')}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        models.append(
                            ModelInfo(
                                name=model_id,
                                display_name=model_id,
                                description=f"{provider_name} Model",
                            )
                        )
                    return models
                else:
                    logger.warning(
                        f"{provider_name} API returned {response.status_code}"
                    )
                    return []
        except Exception as e:
            logger.warning(f"Failed to fetch {provider_name} models: {e}")
            return []

    @staticmethod
    async def fetch_modal_models(api_key: str) -> List[ModelInfo]:
        """Fetch available models from Modal Z.ai API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.us-west-2.modal.direct/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model in data.get("data", []):
                        models.append(
                            ModelInfo(
                                name=model.get("id", model.get("name")),
                                display_name=model.get("id", model.get("name")),
                                max_tokens=model.get("max_tokens", 4096),
                                description=f"Modal Z.ai - {model.get('created', 'N/A')}",
                            )
                        )
                    return (
                        models if models else await ModelDiscovery._get_modal_fallback()
                    )
                return await ModelDiscovery._get_modal_fallback()
        except Exception:
            return await ModelDiscovery._get_modal_fallback()

    @staticmethod
    async def _get_modal_fallback() -> List[ModelInfo]:
        return [
            ModelInfo(name="zai-org/GLM-5.1-FP8", display_name="GLM-5.1-FP8 (Latest)"),
            ModelInfo(name="zai-org/GLM-4", display_name="GLM-4 (Legacy)"),
        ]

    @staticmethod
    async def fetch_openai_models(api_key: str) -> List[ModelInfo]:
        """Fetch available models from OpenAI API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    suitable_prefixes = {"gpt-4", "gpt-3.5", "o1-"}
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        if any(model_id.startswith(p) for p in suitable_prefixes):
                            models.append(
                                ModelInfo(name=model_id, display_name=model_id)
                            )
                    return (
                        models
                        if models
                        else await ModelDiscovery._get_openai_fallback()
                    )
                return await ModelDiscovery._get_openai_fallback()
        except Exception:
            return await ModelDiscovery._get_openai_fallback()

    @staticmethod
    async def _get_openai_fallback() -> List[ModelInfo]:
        return [
            ModelInfo(name="gpt-4o", display_name="GPT-4o"),
            ModelInfo(name="gpt-4o-mini", display_name="GPT-4o-mini"),
            ModelInfo(name="o1-preview", display_name="o1-preview"),
        ]

    @staticmethod
    async def fetch_gemini_models(api_key: str) -> List[ModelInfo]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1/models?key={api_key}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model in data.get("models", []):
                        name = model.get("name", "").replace("models/", "")
                        if "gemini" in name.lower():
                            models.append(ModelInfo(name=name, display_name=name))
                    return (
                        models
                        if models
                        else await ModelDiscovery._get_gemini_fallback()
                    )
                return await ModelDiscovery._get_gemini_fallback()
        except Exception:
            return await ModelDiscovery._get_gemini_fallback()

    @staticmethod
    async def _get_gemini_fallback() -> List[ModelInfo]:
        return [
            ModelInfo(name="gemini-1.5-pro", display_name="Gemini 1.5 Pro"),
            ModelInfo(name="gemini-1.5-flash", display_name="Gemini 1.5 Flash"),
        ]

    @staticmethod
    async def fetch_claude_models(api_key: str) -> List[ModelInfo]:
        # Anthropic doesn't have a models endpoint, just return hardcoded
        return [
            ModelInfo(
                name="claude-3-5-sonnet-20240620", display_name="Claude 3.5 Sonnet"
            ),
            ModelInfo(name="claude-3-opus-20240229", display_name="Claude 3 Opus"),
            ModelInfo(name="claude-3-haiku-20240307", display_name="Claude 3 Haiku"),
        ]

    @staticmethod
    async def discover_all(provider: str, api_key: str) -> List[ModelInfo]:
        provider = provider.lower().strip()
        if provider == "modal":
            return await ModelDiscovery.fetch_modal_models(api_key)
        elif provider == "openai":
            return await ModelDiscovery.fetch_openai_models(api_key)
        elif provider == "gemini":
            return await ModelDiscovery.fetch_gemini_models(api_key)
        elif provider == "claude":
            return await ModelDiscovery.fetch_claude_models(api_key)
        elif provider == "deepseek":
            return await ModelDiscovery.fetch_generic_openai_compatible(
                api_key, "https://api.deepseek.com/v1", "DeepSeek"
            )
        elif provider == "kimi":
            return await ModelDiscovery.fetch_generic_openai_compatible(
                api_key, "https://api.moonshot.cn/v1", "Kimi"
            )
        elif provider == "minimax":
            return await ModelDiscovery.fetch_generic_openai_compatible(
                api_key, "https://api.minimax.chat/v1", "Minimax"
            )
        elif provider == "siliconflow":
            return await ModelDiscovery.fetch_generic_openai_compatible(
                api_key, "https://api.siliconflow.cn/v1", "SiliconFlow"
            )
        else:
            return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print(json.dumps([]))
        sys.exit(0)

    provider = sys.argv[1]
    api_key = sys.argv[2]

    async def main():
        models = await ModelDiscovery.discover_all(provider, api_key)
        print(json.dumps([asdict(m) for m in models]))

    asyncio.run(main())
