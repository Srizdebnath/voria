"""Modal Z.ai GLM-5.1 LLM Provider Integration

Modal Research provides the Z.ai GLM-5.1-FP8 model via their API.
Docs: https://modal.com
Model: zai-org/GLM-5.1-FP8 (745B parameters)
"""

import logging
from typing import List, Dict, Any, Optional
import httpx
import asyncio

from .base import BaseLLMProvider, Message, LLMResponse

logger = logging.getLogger(__name__)


class ModalProvider(BaseLLMProvider):
    """Modal Z.ai GLM-5.1 LLM Provider"""

    API_ENDPOINT = "https://api.us-west-2.modal.direct/v1/chat/completions"
    DEFAULT_MODEL = "zai-org/GLM-5.1-FP8"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        """
        Initialize Modal provider

        Args:
            api_key: Modal API token
            model: Model identifier (default: GLM-5.1-FP8)
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
        """
        Generate response using Modal Z.ai

        Args:
            messages: Chat messages
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            LLMResponse with content and token info
        """
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": msg.role, "content": msg.content} for msg in messages
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            logger.debug(f"Calling Modal API with {len(messages)} messages")

            response = await self.client.post(self.API_ENDPOINT, json=payload)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)

            logger.info(f"Modal API response: {tokens_used} tokens used")

            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                model=self.model,
                provider="Modal",
            )

        except httpx.HTTPError as e:
            logger.error(f"Modal API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating with Modal: {e}")
            raise

    async def plan(self, issue_description: str) -> str:
        """
        Generate implementation plan from issue

        Args:
            issue_description: GitHub issue text

        Returns:
            Implementation plan
        """
        system_message = Message(
            role="system",
            content="""You are an expert software architect analyzing GitHub issues.
Your task is to create a detailed implementation plan for fixing the issue.

Include:
1. Problem analysis
2. Root cause identification
3. Solution approach
4. Files to modify
5. Testing strategy

Be concise but thorough.""",
        )

        user_message = Message(
            role="user", content=f"GitHub Issue:\n{issue_description}"
        )

        response = await self.generate(
            [system_message, user_message], max_tokens=2000, temperature=0.7
        )

        return response.content

    async def generate_patch(
        self,
        issue_description: str,
        context_files: Dict[str, str],
        previous_errors: Optional[str] = None,
    ) -> str:
        """
        Generate code patch

        Args:
            issue_description: Issue description
            context_files: Dict of filename -> file content
            previous_errors: Errors from previous attempt

        Returns:
            Unified diff format patch
        """
        system_message = Message(
            role="system",
            content="""You are an expert code generator.
Generate a unified diff format patch to fix the issue.

Format:
--- a/path/to/file
+++ b/path/to/file
@@ -line,count +line,count @@
 unchanged line
-removed line
+added line

Generate complete, working patches.""",
        )

        context = f"Issue:\n{issue_description}\n\n"
        context += "Current Code:\n"
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
        """
        Analyze test failure and suggest fix

        Args:
            test_output: Test output/error logs
            code_context: Relevant code snippet

        Returns:
            Analysis dict with suggestions
        """
        system_message = Message(
            role="system",
            content="""Analyze the test failure and provide:
1. Root cause
2. Why the fix didn't work
3. Suggested improvements
4. Next approach

Be technical and specific.""",
        )

        user_message = Message(
            role="user",
            content=f"""Test Output:
{test_output}

Code Context:
{code_context}""",
        )

        response = await self.generate(
            [system_message, user_message], max_tokens=1500, temperature=0.7
        )

        return {
            "analysis": response.content,
            "provider": "Modal",
            "tokens_used": response.tokens_used,
        }

    async def stream_generate(
        self, messages: List[Message], max_tokens: int = 2000, temperature: float = 0.7
    ):
        """Stream response tokens from Modal"""
        import json as _json

        try:
            payload = {
                "model": self.model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            }
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
                            data = _json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except Exception:
                            continue
        except Exception as e:
            logger.error(f"Modal stream error: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def __del__(self):
        """Cleanup on deletion"""
        try:
            # Don't try to run async cleanup in __del__ as it may cause issues
            # The context manager or explicit close() should handle cleanup
            return
        except:
            pass
