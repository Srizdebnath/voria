"""Google Gemini LLM Provider"""

import logging
from typing import List, Dict, Any, Optional
import httpx

from .base import BaseLLMProvider, Message, LLMResponse

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Pro LLM Provider"""

    API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"
    DEFAULT_MODEL = "gemini-pro"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        """
        Initialize Gemini provider

        Args:
            api_key: Google API key
            model: Model (gemini-pro, gemini-pro-vision, etc)
        """
        super().__init__(api_key, model)
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate(
        self, messages: List[Message], max_tokens: int = 2000, temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response using Gemini"""
        try:
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                contents.append(
                    {
                        "role": "user" if msg.role == "user" else "model",
                        "parts": [{"text": msg.content}],
                    }
                )

            payload = {
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature,
                },
            }

            url = f"{self.API_ENDPOINT}/{self.model}:generateContent?key={self.api_key}"

            logger.debug(f"Calling Gemini API with {len(messages)} messages")

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]

            # Estimate tokens (Gemini doesn't always return token count)
            tokens_used = len(content.split()) * 1.3  # Rough estimate

            logger.info(f"Gemini API response: ~{int(tokens_used)} tokens")

            return LLMResponse(
                content=content,
                tokens_used=int(tokens_used),
                model=self.model,
                provider="Gemini",
            )

        except httpx.HTTPError as e:
            logger.error(f"Gemini API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating with Gemini: {e}")
            raise

    async def plan(self, issue_description: str) -> str:
        """Generate implementation plan"""
        system_message = Message(
            role="system",
            content="""You are an expert software architect.
Create a detailed implementation plan for fixing this GitHub issue.""",
        )

        user_message = Message(role="user", content=f"Issue:\n{issue_description}")

        response = await self.generate([system_message, user_message], max_tokens=2000)

        return response.content

    async def generate_patch(
        self,
        issue_description: str,
        context_files: Dict[str, str],
        previous_errors: Optional[str] = None,
    ) -> str:
        """Generate code patch"""
        system_message = Message(
            role="system", content="""Generate a unified diff format patch."""
        )

        context = f"Issue:\n{issue_description}\n\n"
        for filename, content in context_files.items():
            context += f"\n--- {filename} ---\n{content}\n"

        if previous_errors:
            context += f"\nPrevious Errors:\n{previous_errors}"

        user_message = Message(role="user", content=context)

        response = await self.generate(
            [system_message, user_message], max_tokens=3000, temperature=0.5
        )

        return response.content

    async def analyze_test_failure(
        self, test_output: str, code_context: str
    ) -> Dict[str, Any]:
        """Analyze test failure"""
        system_message = Message(
            role="system", content="Analyze the test failure and suggest fixes."
        )

        user_message = Message(
            role="user",
            content=f"""Test Output:
{test_output}

Code:
{code_context}""",
        )

        response = await self.generate([system_message, user_message], max_tokens=1500)

        return {
            "analysis": response.content,
            "provider": "Gemini",
            "tokens_used": response.tokens_used,
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
