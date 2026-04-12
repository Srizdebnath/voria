"""OpenAI GPT-4 and GPT-3.5 LLM Provider"""

import logging
from typing import List, Dict, Any, Optional
import httpx

from .base import BaseLLMProvider, Message, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4 and GPT-3.5-turbo Provider"""

    API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
    DEFAULT_MODEL = "gpt-4"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key
            model: Model (gpt-4, gpt-3.5-turbo, etc)
        """
        super().__init__(api_key, model)
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=300.0,
        )

    async def generate(
        self, messages: List[Message], max_tokens: int = 2000, temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response using OpenAI"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": msg.role, "content": msg.content} for msg in messages
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            logger.debug(f"Calling OpenAI API with {len(messages)} messages")

            response = await self.client.post(self.API_ENDPOINT, json=payload)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)

            logger.info(f"OpenAI API response: {tokens_used} tokens used")

            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                model=self.model,
                provider="OpenAI",
            )

        except httpx.HTTPError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating with OpenAI: {e}")
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
        """Generate code patch in unified diff format"""
        system_message = Message(
            role="system",
            content="""Generate a unified diff format patch.
Format:
--- a/path
+++ b/path
@@ -line,count +line,count @@""",
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
            "provider": "OpenAI",
            "tokens_used": response.tokens_used,
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
