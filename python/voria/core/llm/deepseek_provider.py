"""DeepSeek LLM Provider

DeepSeek provides powerful code-focused models via OpenAI-compatible API.
"""

import json
import logging
from typing import List, Dict, Any, Optional
import httpx

from .base import BaseLLMProvider, Message, LLMResponse

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek LLM Provider (OpenAI-compatible API)"""

    API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
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
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": msg.role, "content": msg.content} for msg in messages
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            response = await self.client.post(self.API_ENDPOINT, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            return LLMResponse(content=content, tokens_used=tokens_used, model=self.model, provider="DeepSeek")
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise

    async def stream_generate(
        self, messages: List[Message], max_tokens: int = 2000, temperature: float = 0.7
    ):
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            }
            async with self.client.stream("POST", self.API_ENDPOINT, json=payload) as response:
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
                        except Exception:
                            continue
        except Exception as e:
            logger.error(f"DeepSeek stream error: {e}")
            raise

    async def plan(self, issue_description: str) -> str:
        system_message = Message(role="system", content="You are an expert software architect. Create a detailed implementation plan.")
        user_message = Message(role="user", content=f"Issue:\n{issue_description}")
        response = await self.generate([system_message, user_message], max_tokens=2000)
        return response.content

    async def generate_patch(self, issue_description: str, context_files: Dict[str, str], previous_errors: Optional[str] = None) -> str:
        system_message = Message(role="system", content="Generate a unified diff format patch.")
        context = f"Issue:\n{issue_description}\n\n"
        for filename, content in context_files.items():
            context += f"\n--- {filename} ---\n{content}\n"
        if previous_errors:
            context += f"\nPrevious Errors:\n{previous_errors}"
        user_message = Message(role="user", content=context)
        response = await self.generate([system_message, user_message], max_tokens=3000, temperature=0.5)
        return response.content

    async def analyze_test_failure(self, test_output: str, code_context: str) -> Dict[str, Any]:
        system_message = Message(role="system", content="Analyze the test failure and suggest fixes.")
        user_message = Message(role="user", content=f"Test Output:\n{test_output}\n\nCode:\n{code_context}")
        response = await self.generate([system_message, user_message], max_tokens=1500)
        return {"analysis": response.content, "provider": "DeepSeek", "tokens_used": response.tokens_used}

    async def close(self):
        await self.client.aclose()
