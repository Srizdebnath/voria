"""
Interactive setup CLI for configuring LLM providers.
Guides users through choosing provider, API key, and model selection.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Optional
import json
import logging

from victory.core.llm import LLMProviderFactory

logger = logging.getLogger(__name__)


class ProviderSetup:
    """Interactive provider configuration setup"""

    CONFIG_DIR = Path.home() / ".victory"
    CONFIG_FILE = CONFIG_DIR / "providers.json"

    def __init__(self):
        """Initialize setup helper"""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.providers = {}
        self._load_config()

    def _load_config(self):
        """Load saved provider configurations"""
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, "r") as f:
                self.providers = json.load(f)

    def _save_config(self):
        """Save provider configurations"""
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.providers, f, indent=2)
        os.chmod(self.CONFIG_FILE, 0o600)  # Restrict permissions

    async def setup_provider(
        self,
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Interactive setup for a provider

        Args:
            provider_name: Provider to setup (optional, will prompt if None)
            api_key: API key (optional, will prompt if None)

        Returns:
            Dict with provider_name, api_key, and selected model
        """
        # Step 1: Choose provider
        if not provider_name:
            provider_name = await self._choose_provider()
        provider_name = provider_name.lower()

        # Step 2: Get API key
        if not api_key:
            api_key = await self._get_api_key(provider_name)

        # Step 3: Discover models
        print(f"\n🔍 Fetching available {provider_name} models...")
        try:
            models = await LLMProviderFactory.discover_models(provider_name, api_key)
        except Exception as e:
            print(f"❌ Failed to fetch models: {e}")
            print("Using fallback models...")
            from victory.core.llm import ModelDiscovery

            if provider_name == "modal":
                models = await ModelDiscovery._get_modal_fallback()
            elif provider_name == "openai":
                models = await ModelDiscovery._get_openai_fallback()
            elif provider_name == "gemini":
                models = await ModelDiscovery._get_gemini_fallback()
            elif provider_name == "claude":
                models = await ModelDiscovery._get_claude_fallback()

        # Step 4: Choose model
        chosen_model = await self._choose_model(models)

        # Step 5: Save configuration
        print(f"\n💾 Saving configuration...")
        self.providers[provider_name] = {
            "api_key": api_key,
            "model": chosen_model.name,
            "model_name": chosen_model.display_name,
        }
        self._save_config()

        print(f"✅ {provider_name} configured successfully!")
        print(f"   Model: {chosen_model.display_name}")
        print(f"   Config saved to: {self.CONFIG_FILE}")

        return {
            "provider": provider_name,
            "api_key": api_key,
            "model": chosen_model.name,
            "model_name": chosen_model.display_name,
        }

    async def _choose_provider(self) -> str:
        """Interactive provider selection"""
        providers = LLMProviderFactory.list_providers()

        print("\n🤖 Select LLM Provider:")
        for i, provider in enumerate(providers, 1):
            status = (
                "✅ Configured" if provider in self.providers else "❌ Not configured"
            )
            print(f"  {i}. {provider.upper()} {status}")

        while True:
            try:
                choice = input("\nEnter number (1-4): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(providers):
                    return providers[idx]
                print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a valid number.")

    async def _get_api_key(self, provider_name: str) -> str:
        """Get API key from user or environment"""
        # Check environment variables
        env_vars = {
            "modal": ["MODAL_API_KEY"],
            "openai": ["OPENAI_API_KEY"],
            "gemini": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
            "claude": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
        }

        for env_var in env_vars.get(provider_name, []):
            if env_var in os.environ:
                print(f"✅ Using API key from ${env_var}")
                return os.environ[env_var]

        # Prompt user
        while True:
            api_key = input(f"\n🔑 Enter {provider_name.upper()} API key: ").strip()
            if api_key:
                # Ask to save to environment
                save = input("Save to environment variable? (y/n): ").lower().strip()
                if save == "y":
                    env_var = env_vars[provider_name][0]
                    print(f"Add to ~/.bashrc or ~/.zshrc:")
                    print(f"export {env_var}='{api_key}'")
                return api_key
            print("API key cannot be empty.")

    async def _choose_model(self, models: list) -> object:
        """Interactive model selection from discovered models"""
        print("\n📦 Available Models:")
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model.display_name}")
            if model.description:
                print(f"     {model.description}")

        while True:
            try:
                choice = input("\nSelect model number: ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    return models[idx]
                print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a valid number.")

    def get_provider_config(self, provider_name: str) -> Optional[Dict]:
        """Get saved configuration for a provider"""
        return self.providers.get(provider_name.lower())

    def list_configured(self) -> Dict:
        """List all configured providers"""
        return self.providers.copy()


async def interactive_setup():
    """Run interactive setup for first-time users"""
    setup = ProviderSetup()

    print("\n" + "=" * 50)
    print("🚀 Victory LLM Provider Setup")
    print("=" * 50)

    config = await setup.setup_provider()

    print("\n" + "=" * 50)
    print("✅ Setup Complete!")
    print("=" * 50)

    return config


if __name__ == "__main__":
    asyncio.run(interactive_setup())
