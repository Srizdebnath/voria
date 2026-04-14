"""LLM Provider Integration Module

Supports multiple LLM providers with dynamic model discovery:
- Modal Z.ai GLM-5.1 (745B parameters)
- OpenAI GPT-4 / GPT-3.5-turbo
- Google Gemini Pro
- Anthropic Claude 3
- DeepSeek
- SiliconFlow
- Kimi (Moonshot AI)
- MiniMax

Dynamic Model Discovery:
    from voria.core.llm import LLMProviderFactory

    # Discover available models
    models = await LLMProviderFactory.discover_models(
        provider_name="openai",
        api_key="sk-..."
    )

    # User chooses from models list
    chosen_model = models[0]

    # Create provider with chosen model
    provider = LLMProviderFactory.create(
        provider_name="openai",
        api_key="sk-...",
        model=chosen_model.name
    )

    response = await provider.generate(messages)
"""

from .base import BaseLLMProvider, Message, LLMResponse, LLMProviderFactory
from .model_discovery import ModelDiscovery, ModelInfo
from .modal_provider import ModalProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .claude_provider import ClaudeProvider
from .minimax_provider import MiniMaxProvider
from .deepseek_provider import DeepSeekProvider
from .siliconflow_provider import SiliconFlowProvider
from .kimi_provider import KimiProvider

# Register all providers
LLMProviderFactory.register("modal", ModalProvider)
LLMProviderFactory.register("openai", OpenAIProvider)
LLMProviderFactory.register("gemini", GeminiProvider)
LLMProviderFactory.register("claude", ClaudeProvider)
LLMProviderFactory.register("minimax", MiniMaxProvider)
LLMProviderFactory.register("deepseek", DeepSeekProvider)
LLMProviderFactory.register("siliconflow", SiliconFlowProvider)
LLMProviderFactory.register("kimi", KimiProvider)

__all__ = [
    "BaseLLMProvider",
    "Message",
    "LLMResponse",
    "LLMProviderFactory",
    "ModelDiscovery",
    "ModelInfo",
    "ModalProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "ClaudeProvider",
    "MiniMaxProvider",
    "DeepSeekProvider",
    "SiliconFlowProvider",
    "KimiProvider",
]
