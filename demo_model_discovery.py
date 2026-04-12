#!/usr/bin/env python3
"""
Quick demo of voria's dynamic model discovery
Shows how to select models from latest available options
"""

import asyncio
from voria.core.llm import LLMProviderFactory


async def demo():
    print("\n" + "=" * 70)
    print("🚀 voria DYNAMIC MODEL DISCOVERY DEMO")
    print("=" * 70 + "\n")

    # Demo: Discover OpenAI models (includes latest GPT-5.4)
    print("1️⃣  Discovering OpenAI Models (Latest GPT-5.4 Series):\n")

    models = await LLMProviderFactory.discover_models(
        provider_name="openai", api_key="sk-fake"  # Using fallback since no real key
    )

    for i, model in enumerate(models, 1):
        print(f"   Option {i}: {model.display_name}")
        print(f"             {model.description}\n")

    # Demo: Select and create provider
    print("2️⃣  Selecting Model & Creating Provider (Option 1 - GPT-5.4):\n")

    selected = models[0]
    print(f"   Selected: {selected.display_name}")
    print(f"   Model ID: {selected.name}\n")

    provider = LLMProviderFactory.create(
        provider_name="openai", api_key="sk-test-fake", model=selected.name
    )

    print(f"   ✅ Provider created: {provider.__class__.__name__}")
    print(f"   ✅ Model: {provider.model}")
    print(f"   ✅ Ready for use!\n")

    # Demo: Show all provider options
    print("3️⃣  Available Providers in voria:\n")

    providers = LLMProviderFactory.list_providers()
    for provider in providers:
        print(f"     • {provider.upper()}")

    print("\n4️⃣  Interactive Setup (from CLI):\n")
    print("     $ python3 -m voria.core.setup")
    print("     🤖 Select LLM Provider:")
    print("        1. modal ❌ Not configured")
    print("        2. openai ❌ Not configured")
    print("        3. gemini ❌ Not configured")
    print("        4. claude ❌ Not configured")
    print("     Enter number (1-4): 2")
    print("     🔑 Enter OPENAI API key: sk-...")
    print("     🔍 Fetching available openai models...")
    print("     📦 Available Models:")
    print("        1. GPT-5.4 (Latest Frontier)")
    print("        2. GPT-5.4-mini (Mini Model)")
    print("        3. GPT-5.4-nano (Cheapest)")
    print("        4. GPT-4o (Previous High Quality)")
    print("     Select model number: 1")
    print("     💾 Saving configuration...")
    print("     ✅ openai configured successfully!")
    print("        Model: GPT-5.4 (Latest Frontier)")
    print("        Config saved to: /home/user/.voria/providers.json\n")

    print("=" * 70)
    print("✅ voria supports latest models with dynamic discovery!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(demo())
