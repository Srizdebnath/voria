"""LLM Provider Interfaces and Base Classes"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """LLM message in chat format"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Standard response from LLM providers"""
    content: str
    tokens_used: int
    model: str
    provider: str


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize LLM provider
        
        Args:
            api_key: Provider-specific API key
            model: Model identifier
        """
        self.api_key = api_key
        self.model = model
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        Generate response from LLM
        
        Args:
            messages: List of messages in conversation
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            
        Returns:
            LLMResponse with content and token info
        """
        pass
    
    @abstractmethod
    async def plan(self, issue_description: str) -> str:
        """Generate implementation plan from issue"""
        pass
    
    @abstractmethod
    async def generate_patch(
        self,
        issue_description: str,
        context_files: Dict[str, str],
        previous_errors: Optional[str] = None
    ) -> str:
        """Generate code patch"""
        pass
    
    @abstractmethod
    async def analyze_test_failure(
        self,
        test_output: str,
        code_context: str
    ) -> Dict[str, Any]:
        """Analyze test failure and suggest fix"""
        pass


class LLMProviderFactory:
    """Factory for creating LLM provider instances"""
    
    _providers = {}
    
    @classmethod
    def register(cls, name: str, provider_class):
        """Register a new LLM provider"""
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered LLM provider: {name}")
    
    @classmethod
    def create(cls, provider_name: str, api_key: str, model: str):
        """
        Create an LLM provider instance
        
        Args:
            provider_name: Name of provider (modal, openai, gemini, claude)
            api_key: Provider API key
            model: Model identifier
            
        Returns:
            Configured LLM provider instance
            
        Raises:
            ValueError: If provider not found
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown LLM provider: {provider_name}. "
                f"Available: {available}"
            )
        
        logger.info(f"Creating {provider_name} provider with model {model}")
        return provider_class(api_key=api_key, model=model)
    
    @classmethod
    async def discover_models(cls, provider_name: str, api_key: str):
        """
        Discover available models for a provider
        
        Args:
            provider_name: Name of provider (modal, openai, gemini, claude)
            api_key: Provider API key for authentication
            
        Returns:
            List of ModelInfo objects with available models
            
        Raises:
            ValueError: If provider not found
        """
        # Import here to avoid circular dependency
        from .model_discovery import ModelDiscovery
        
        if provider_name.lower() not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown LLM provider: {provider_name}. "
                f"Available: {available}"
            )
        
        logger.info(f"Discovering models for {provider_name}")
        return await ModelDiscovery.discover_all(provider_name, api_key)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """List all registered providers"""
        return list(cls._providers.keys())
