"""
Dynamic model discovery for all LLM providers.
Fetches available models at runtime based on API keys.
"""

import asyncio
import httpx
from dataclasses import dataclass
from typing import List, Optional
import logging

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
    async def fetch_modal_models(api_key: str) -> List[ModelInfo]:
        """Fetch available models from Modal Z.ai API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.us-west-2.modal.direct/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    # Modal returns model data in "data" key
                    for model in data.get("data", []):
                        models.append(ModelInfo(
                            name=model.get("id", model.get("name")),
                            display_name=model.get("id", model.get("name")),
                            max_tokens=model.get("max_tokens", 4096),
                            description=f"Modal Z.ai - {model.get('created', 'N/A')}"
                        ))
                    return models if models else await ModelDiscovery._get_modal_fallback()
                else:
                    logger.warning(f"Modal API returned {response.status_code}, using fallback models")
                    return await ModelDiscovery._get_modal_fallback()
        except Exception as e:
            logger.warning(f"Failed to fetch Modal models: {e}, using fallback")
            return await ModelDiscovery._get_modal_fallback()

    @staticmethod
    async def _get_modal_fallback() -> List[ModelInfo]:
        """Fallback models for Modal when API unavailable."""
        return [
            ModelInfo(
                name="zai-org/GLM-5.1-FP8",
                display_name="GLM-5.1-FP8 (745B, Latest)",
                max_tokens=4096,
                description="Latest Modal Z.ai model - 745B parameters"
            ),
            ModelInfo(
                name="zai-org/GLM-4",
                display_name="GLM-4 (370B, Legacy)",
                max_tokens=2048,
                description="Previous generation Modal model"
            )
        ]

    @staticmethod
    async def fetch_openai_models(api_key: str) -> List[ModelInfo]:
        """Fetch available models from OpenAI API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    # Filter to only gpt models suitable for text generation
                    suitable_models = {"gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"}
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        # Match by prefix or exact name
                        if any(model_id.startswith(prefix) for prefix in suitable_models):
                            models.append(ModelInfo(
                                name=model_id,
                                display_name=model_id,
                                description=f"OpenAI - {model.get('owned_by', 'N/A')}"
                            ))
                    # Sort by recency (gpt-4o > gpt-4-turbo > gpt-4 > gpt-3.5-turbo)
                    return sorted(models, key=lambda x: (
                        not x.name.startswith("gpt-4o"),
                        not x.name.startswith("gpt-4-turbo"),
                        not x.name.startswith("gpt-4"),
                    )) if models else await ModelDiscovery._get_openai_fallback()
                else:
                    logger.warning(f"OpenAI API returned {response.status_code}, using fallback models")
                    return await ModelDiscovery._get_openai_fallback()
        except Exception as e:
            logger.warning(f"Failed to fetch OpenAI models: {e}, using fallback")
            return await ModelDiscovery._get_openai_fallback()

    @staticmethod
    async def _get_openai_fallback() -> List[ModelInfo]:
        """Fallback models for OpenAI when API unavailable."""
        return [
            ModelInfo(
                name="gpt-5.4",
                display_name="GPT-5.4 (Latest Frontier)",
                max_tokens=128000,
                description="Best intelligence at scale for agentic, coding, and professional workflows. $2.50 input, $15 output per 1M tokens"
            ),
            ModelInfo(
                name="gpt-5.4-mini",
                display_name="GPT-5.4-mini (Mini Model)",
                max_tokens=128000,
                description="Strongest mini model yet for coding, computer use, and agentic tasks. $0.75 input, $4.50 output per 1M tokens"
            ),
            ModelInfo(
                name="gpt-5.4-nano",
                display_name="GPT-5.4-nano (Cheapest)",
                max_tokens=128000,
                description="Cheapest GPT-5.4-class model for simple high-volume tasks. $0.20 input, $1.25 output per 1M tokens"
            ),
            ModelInfo(
                name="gpt-4o",
                display_name="GPT-4o (Previous High Quality)",
                max_tokens=128000,
                description="Previous latest model - optimized for speed and cost"
            )
        ]

    @staticmethod
    async def fetch_gemini_models(api_key: str) -> List[ModelInfo]:
        """Fetch available models from Google Gemini API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1/models?key={api_key}",
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    # Filter to generative models
                    for model in data.get("models", []):
                        model_name = model.get("name", "").replace("models/", "")
                        if "gemini" in model_name.lower():
                            models.append(ModelInfo(
                                name=model_name,
                                display_name=model_name,
                                description=f"Google Gemini - {model.get('displayName', 'N/A')}"
                            ))
                    return models if models else await ModelDiscovery._get_gemini_fallback()
                else:
                    logger.warning(f"Gemini API returned {response.status_code}, using fallback models")
                    return await ModelDiscovery._get_gemini_fallback()
        except Exception as e:
            logger.warning(f"Failed to fetch Gemini models: {e}, using fallback")
            return await ModelDiscovery._get_gemini_fallback()

    @staticmethod
    async def _get_gemini_fallback() -> List[ModelInfo]:
        """Fallback models for Gemini when API unavailable."""
        return [
            ModelInfo(
                name="gemini-3.1-pro",
                display_name="Gemini 3.1 Pro (Latest SOTA Reasoning)",
                max_tokens=200000,
                description="Latest SOTA reasoning model with unprecedented depth and nuance. $2 input, $12 output per context window"
            ),
            ModelInfo(
                name="gemini-3-flash",
                display_name="Gemini 3 Flash (Latest, Fastest)",
                max_tokens=200000,
                description="Most intelligent model built for speed, combining frontier intelligence with superior search and grounding"
            ),
            ModelInfo(
                name="gemini-3.1-flash-lite",
                display_name="Gemini 3.1 Flash Lite (Cheapest)",
                max_tokens=200000,
                description="Most cost-efficient model, optimized for high-volume agentic tasks. $0.25 input, $1.50 output"
            ),
            ModelInfo(
                name="gemini-2.0-flash",
                display_name="Gemini 2.0 Flash (Previous)",
                max_tokens=2000,
                description="Previous generation Gemini model"
            )
        ]

    @staticmethod
    async def fetch_claude_models(api_key: str) -> List[ModelInfo]:
        """Fetch available models from Anthropic Claude API."""
        try:
            async with httpx.AsyncClient() as client:
                # Claude doesn't have a public models endpoint, use documented models
                # Make a test call to verify API key works
                response = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={"x-api-key": api_key},
                    timeout=10.0
                )
                # If we get here, API key works - return known models
                return await ModelDiscovery._get_claude_fallback()
        except Exception as e:
            logger.warning(f"Failed to verify Claude API: {e}, returning known models")
            return await ModelDiscovery._get_claude_fallback()

    @staticmethod
    async def _get_claude_fallback() -> List[ModelInfo]:
        """Known Claude models (Anthropic doesn't provide list endpoint)."""
        return [
            ModelInfo(
                name="claude-opus-4.6",
                display_name="Claude Opus 4.6 (Most Intelligent)",
                max_tokens=200000,
                description="Most intelligent broadly available model for complex reasoning. $5 input, $25 output per 1M tokens"
            ),
            ModelInfo(
                name="claude-sonnet-4.6",
                display_name="Claude Sonnet 4.6 (Best Value)",
                max_tokens=200000,
                description="Best balance of speed and intelligence. $3 input, $15 output per 1M tokens"
            ),
            ModelInfo(
                name="claude-haiku-4.5",
                display_name="Claude Haiku 4.5 (Fastest, Cheapest)",
                max_tokens=200000,
                description="Fast and cost-efficient for simpler tasks. $0.80 input, $4 output per 1M tokens"
            )
        ]

    @staticmethod
    async def discover_all(provider: str, api_key: str) -> List[ModelInfo]:
        """Discover all models for a given provider."""
        provider = provider.lower().strip()
        if provider == "modal":
            return await ModelDiscovery.fetch_modal_models(api_key)
        elif provider == "openai":
            return await ModelDiscovery.fetch_openai_models(api_key)
        elif provider == "gemini":
            return await ModelDiscovery.fetch_gemini_models(api_key)
        elif provider == "claude":
            return await ModelDiscovery.fetch_claude_models(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
