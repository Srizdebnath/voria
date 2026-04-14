"""MiniMax LLM Provider via NVIDIA Integrate API"""

import logging
from typing import List, Dict, Any, Optional
import httpx

from .base import BaseLLMProvider, Message, LLMResponse

logger = logging.getLogger(__name__)


class MiniMaxProvider(BaseLLMProvider):
    """MiniMax LLM Provider using NVIDIA's OpenAI-compatible API"""

    API_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
    DEFAULT_MODEL = "minimaxai/minimax-m2.7"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        """
        Initialize MiniMax provider

        Args:
            api_key: NVIDIA API key
            model: Model (minimaxai/minimax-m2.7, etc)
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
        """Generate response using MiniMax"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": msg.role, "content": msg.content} for msg in messages
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.95,
                "stream": False,
            }

            logger.debug(f"Calling MiniMax API with {len(messages)} messages")
            logger.info(f"Sending generation request to MiniMax model {self.model}...")

            response = await self.client.post(self.API_ENDPOINT, json=payload)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)

            logger.info(f"MiniMax API response: {tokens_used} tokens used")

            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                model=self.model,
                provider="MiniMax",
            )

        except httpx.HTTPError as e:
            logger.error(f"MiniMax API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating with MiniMax: {e}")
            raise

    async def stream_generate(
        self, messages: List[Message], max_tokens: int = 2000, temperature: float = 0.7
    ):
        """Stream generation from MiniMax"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": msg.role, "content": msg.content} for msg in messages
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.95,
                "stream": True,
            }

            import json

            async with self.client.stream(
                "POST", self.API_ENDPOINT, json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except Exception as e:
                            logger.error(f"Error parsing stream chunk: {e}")
                            continue

        except Exception as e:
            logger.error(f"Error in MiniMax stream: {e}")
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
            "provider": "MiniMax",
            "tokens_used": response.tokens_used,
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
