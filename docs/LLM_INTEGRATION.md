# LLM Integration Guide

How to add support for new LLM providers in voria.

##  Adding a New LLM Provider

voria supports multiple LLM providers. Here's how to add a new one like Kimi, MiniMax, or custom APIs.

##  Step 1: Choose an LLM

**Current Providers** (supported out of box):
- **Modal** - Free 745B GLM model (until Apr 30)
- **OpenAI** - GPT-5.4 series (frontier models)
- **Google Gemini** - Gemini 3.x (fast & cheap)
- **Anthropic Claude** - Claude 4.6 (highest quality)

**Candidates to Add**:
- **Kimi (Moon)** - Chinese LLM
- **MiniMax** - Cost-effective option
- **Aleph Alpha** - Private deployment option
- **Together** - Distributed inference
- **LocalAI** - Self-hosted option
- **Ollama** - Local models

##  Implementation (Example: Kimi)

### Step 1: Create Provider Class

Create `python/voria/core/llm/providers/kimi.py`:

```python
from .base import BaseLLMProvider, LLMResponse
import httpx
from dataclasses import dataclass
from typing import Optional

@dataclass
class KimiModelInfo:
    """Kimi model information"""
    name: str
    display_name: str
    max_tokens: int = 4096

class KimiProvider(BaseLLMProvider):
    """Kimi (Moonshot) LLM provider"""
    
    BASE_URL = "https://api.moonshot.cn/v1"
    
    def __init__(self, api_key: str, model: str = "moonshot-v1-32k"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def plan(self, issue_description: str) -> str:
        """Generate a fix plan for the issue"""
        prompt = f"""Analyze this GitHub issue and create a detailed fix plan:

{issue_description}

Provide:
1. Root cause analysis
2. Files that need changes
3. Changes needed (point form)
4. Potential edge cases
5. Testing strategy"""
        
        response = await self._call_api(prompt, "planning")
        return response.content
    
    async def generate_patch(self, issue_context: dict, plan: str) -> str:
        """Generate a unified diff based on the plan"""
        prompt = f"""Based on this plan, generate a unified diff:

Plan:
{plan}

Context:
{issue_context}

Generate a valid unified diff starting with:
--- a/filename
+++ b/filename
@@..."""
        
        response = await self._call_api(prompt, "patching")
        return response.content
    
    async def analyze_test_failure(self, test_output: str, code: str) -> str:
        """Analyze test failures and suggest fixes"""
        prompt = f"""The code changes failed tests:

Test Output:
{test_output}

Modified Code:
{code}

Analyze why tests failed and suggest fixes. Be specific about what changed."""
        
        response = await self._call_api(prompt, "analysis")
        return response.content
    
    async def _call_api(self, prompt: str, task_type: str = "default") -> LLMResponse:
        """Call Kimi API"""
        
        # System prompt based on task
        system_prompts = {
            "planning": "You are an expert code analyzer. Provide detailed, actionable plans.",
            "patching": "You are an expert code generator. Generate valid, working code patches.",
            "analysis": "You are an expert debugger. Analyze failures and suggest fixes."
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompts.get(task_type, "")},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 4096
        }
        
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        tokens_used = data.get("usage", {}).get("total_tokens", 0)
        
        return LLMResponse(
            content=content,
            tokens_used=tokens_used,
            finish_reason=data["choices"][0].get("finish_reason", "stop")
        )
    
    @staticmethod
    async def discover_models(api_key: str) -> List[ModelInfo]:
        """Discover available models from Kimi"""
        try:
            client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {api_key}"}
            )
            resp = await client.get("https://api.moonshot.cn/v1/models")
            data = resp.json()
            
            models = []
            for model in data.get("data", []):
                models.append(ModelInfo(
                    name=model["id"],
                    display_name=f"Kimi - {model['id']}",
                    tokens_per_hour=unlimited,
                    max_tokens=model.get("context_window", 4096),
                    description="Moonshot Kimi model"
                ))
            return models
        except:
            # Fallback to known models
            return [
                ModelInfo(
                    name="moonshot-v1-32k",
                    display_name="Kimi (32K Context)",
                    max_tokens=32768,
                    description="Moonshot Kimi with 32K context"
                ),
                ModelInfo(
                    name="moonshot-v1-128k",
                    display_name="Kimi (128K Context)",
                    max_tokens=131072,
                    description="Moonshot Kimi with 128K context"
                )
            ]
```

### Step 2: Register Provider

Edit `python/voria/core/llm/__init__.py`:

```python
from .providers.kimi import KimiProvider

class LLMProviderFactory:
    PROVIDERS = {
        "modal": ModalProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "kimi": KimiProvider,  # ← Add this
    }
    
    @classmethod
    async def discover_models(cls, provider_name: str, api_key: str):
        """Discover available models"""
        provider_class = cls.PROVIDERS.get(provider_name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        return await provider_class.discover_models(api_key)
```

### Step 3: Add to Setup

Edit `python/voria/core/setup.py`:

```python
class ProviderSetup:
    KNOWN_PROVIDERS = {
        "modal": {
            "name": "Modal Z.ai",
            "env_key": "MODAL_API_KEY",
            "url": "https://modal.com"
        },
        "openai": {
            "name": "OpenAI",
            "env_key": "OPENAI_API_KEY",
            "url": "https://platform.openai.com"
        },
        "gemini": {
            "name": "Google Gemini",
            "env_key": "GOOGLE_API_KEY",
            "url": "https://makersuite.google.com"
        },
        "claude": {
            "name": "Anthropic Claude",
            "env_key": "ANTHROPIC_API_KEY",
            "url": "https://console.anthropic.com"
        },
        "kimi": {  # ← Add this
            "name": "Kimi (Moonshot)",
            "env_key": "KIMI_API_KEY",
            "url": "https://platform.moonshot.cn"
        },
    }
```

### Step 4: Add Token Pricing

Edit `python/voria/core/token_manager/pricing.py`:

```python
PROVIDER_PRICING = {
    "modal": {
        "input_price": 0.00,     # Free until Apr 30
        "output_price": 0.00,
        "currency": "USD"
    },
    "openai": {
        "input_price": 0.0.35,   # Per 1K tokens
        "output_price": 0.010,
        "currency": "USD"
    },
    "gemini": {
        "input_price": 0.000075,
        "output_price": 0.00030,
        "currency": "USD"
    },
    "claude": {
        "input_price": 0.003,
        "output_price": 0.015,
        "currency": "USD"
    },
    "kimi": {  # ← Add this
        "input_price": 0.0006,   # Per 1K tokens
        "output_price": 0.0.38,
        "currency": "Yuan (CNY)"
    },
}
```

### Step 5: Test

Create `tests/test_kimi.py`:

```python
import pytest
from voria.core.llm import LLMProviderFactory

@pytest.mark.asyncio
async def test_kimi_provider_creation():
    """Test creating Kimi provider"""
    provider = LLMProviderFactory.create(
        "kimi",
        "fake-key-for-testing",
        "moonshot-v1-32k"
    )
    assert provider is not None
    assert provider.model == "moonshot-v1-32k"

@pytest.mark.asyncio
async def test_kimi_model_discovery():
    """Test discovering Kimi models"""
    models = await LLMProviderFactory.discover_models("kimi", "fake-key")
    assert len(models) > 0
    assert any("Kimi" in m.display_name for m in models)

@pytest.mark.asyncio
async def test_kimi_api_call():
    """Test actual API call (skipped if no real key)"""
    import os
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        pytest.skip("KIMI_API_KEY not set")
    
    provider = LLMProviderFactory.create("kimi", api_key)
    response = await provider.plan("Fix a bug")
    assert response  # Should return something
```

### Step 6: Update Documentation

Add to relevant docs:
- [USER_GUIDE.md](USER_GUIDE.md) - Usage with Kimi
- [EXAMPLES.md](EXAMPLES.md) - Example with Kimi
- Add pricing to comparison table

##  API Key Configuration

Users can configure new provider via:

**Option 1: Interactive Setup**
```bash
python3 -m voria.core.setup
# Choose: kimi
# Enter API key: xxx
```

**Option 2: Environment Variable**
```bash
export KIMI_API_KEY="xxx"
```

**Option 3: Manual Config**
```json
{
  "providers": {
    "kimi": {
      "api_key": "xxx",
      "model": "moonshot-v1-32k"
    }
  }
}
```

##  Checklist for New Provider

- [ ] Create provider class inheriting from `BaseLLMProvider`
- [ ] Implement `plan()`, `generate_patch()`, `analyze_test_failure()`
- [ ] Implement `discover_models()` static method
- [ ] Add to `LLMProviderFactory.PROVIDERS` dict
- [ ] Add to `ProviderSetup.KNOWN_PROVIDERS`
- [ ] Add pricing to `token_manager`
- [ ] Write unit tests
- [ ] Test with real API key (if available)
- [ ] Update documentation with examples
- [ ] Submit PR or document for users

##  Provider Comparison

| Provider | Cost | Speed | Quality | Notes |
|----------|------|-------|---------|-------|
| Modal | FREE | Fast | Good | Limited to GLM-5.1FP8 |
| OpenAI | $5/hr | 2-3min | Excellent | GPT-5.4 |
| Gemini | $1/hr | 1-2min | Good | Cost-effective |
| Claude | $3/hr | 3-4min | Excellent | Takes longer |
| Kimi | $$/hr | Fast | Good | Chinese LLM |

##  Security Notes

When implementing new providers:
- Never log API keys
- Use environment variables for local testing
- Validate API responses
- Handle rate limiting
- Implement exponential backoff
- Use secure HTTPS connections

##  Example: Local Model (Ollama)

```python
class OllamaProvider(BaseLLMProvider):
    """Local Ollama model provider"""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    async def _call_api(self, prompt: str, **kwargs) -> LLMResponse:
        """Call local Ollama server"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            data = response.json()
            return LLMResponse(
                content=data["response"],
                tokens_used=data.get("tokens", 0),
                finish_reason="stop"
            )
```

---

**See Also:**
- [MODULES.md](MODULES.md) - `llm/` module documentation
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup
- [PLUGINS.md](PLUGINS.md) - Plugin development (for test executors, etc)

---

**Join our WhatsApp Support Group:** [Click Here](https://chat.whatsapp.com/IWude2099NAJmLTs8kgEuE?mode=gi_t)
