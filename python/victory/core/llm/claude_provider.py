"""Anthropic Claude LLM Provider"""

import logging
from typing import List, Dict, Any, Optional
import httpx

from .base import BaseLLMProvider, Message, LLMResponse

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude LLM Provider"""
    
    API_ENDPOINT = "https://api.anthropic.com/v1/messages"
    DEFAULT_MODEL = "claude-3-opus-20240229"
    
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        """
        Initialize Claude provider
        
        Args:
            api_key: Anthropic API key
            model: Model (claude-3-opus, claude-3-sonnet, claude-3-haiku)
        """
        super().__init__(api_key, model)
        self.client = httpx.AsyncClient(
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            timeout=300.0
        )
    
    async def generate(
        self,
        messages: List[Message],
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response using Claude"""
        try:
            # Separate system message from user messages
            system_content = ""
            user_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_content = msg.content
                else:
                    user_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": user_messages,
                "temperature": temperature
            }
            
            if system_content:
                payload["system"] = system_content
            
            logger.debug(f"Calling Claude API with {len(user_messages)} messages")
            
            response = await self.client.post(
                self.API_ENDPOINT,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["content"][0]["text"]
            
            # Claude returns token usage directly
            tokens_used = data.get("usage", {}).get("output_tokens", 0)
            input_tokens = data.get("usage", {}).get("input_tokens", 0)
            total_tokens = input_tokens + tokens_used
            
            logger.info(
                f"Claude API response: {tokens_used} output tokens "
                f"({input_tokens} input, {total_tokens} total)"
            )
            
            return LLMResponse(
                content=content,
                tokens_used=total_tokens,
                model=self.model,
                provider="Claude"
            )
        
        except httpx.HTTPError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating with Claude: {e}")
            raise
    
    async def plan(self, issue_description: str) -> str:
        """Generate implementation plan"""
        system_message = Message(
            role="system",
            content="""You are an expert software architect with decades of experience.
Create a detailed, step-by-step implementation plan for fixing this GitHub issue.
Include analysis, approach, and testing strategy."""
        )
        
        user_message = Message(
            role="user",
            content=f"GitHub Issue:\n{issue_description}"
        )
        
        response = await self.generate(
            [system_message, user_message],
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.content
    
    async def generate_patch(
        self,
        issue_description: str,
        context_files: Dict[str, str],
        previous_errors: Optional[str] = None
    ) -> str:
        """Generate code patch in unified diff format"""
        system_message = Message(
            role="system",
            content="""You are an expert code generator and software engineer.
Generate a unified diff format patch to fix the issue.

Use this format exactly:
--- a/path/to/file
+++ b/path/to/file
@@ -line,count +line,count @@
 context line
-removed line
+added line

Generate complete, working patches that will fix the issue."""
        )
        
        context = f"Issue:\n{issue_description}\n\n"
        context += "Current Code:\n"
        for filename, content in context_files.items():
            context += f"\n--- {filename} ---\n{content}\n"
        
        if previous_errors:
            context += f"\nPrevious Attempt Errors:\n{previous_errors}"
        
        user_message = Message(role="user", content=context)
        
        response = await self.generate(
            [system_message, user_message],
            max_tokens=3000,
            temperature=0.5
        )
        
        return response.content
    
    async def analyze_test_failure(
        self,
        test_output: str,
        code_context: str
    ) -> Dict[str, Any]:
        """Analyze test failure and suggest improvements"""
        system_message = Message(
            role="system",
            content="""Analyze the test failure in detail.
Provide:
1. Root cause analysis
2. Why the fix didn't work
3. Specific suggestions for improvement
4. Next approach to try

Be technical and precise."""
        )
        
        user_message = Message(
            role="user",
            content=f"""Test Output:
{test_output}

Code Context:
{code_context}"""
        )
        
        response = await self.generate(
            [system_message, user_message],
            max_tokens=1500,
            temperature=0.7
        )
        
        return {
            "analysis": response.content,
            "provider": "Claude",
            "tokens_used": response.tokens_used
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
