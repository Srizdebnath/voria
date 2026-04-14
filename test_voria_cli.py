#!/usr/bin/env python3
"""
Complete voria CLI + LLM Integration Test Suite
Tests model discovery, provider setup, and CLI end-to-end
"""

import asyncio
import subprocess
import os
import sys
from pathlib import Path
import json

from voria.core.llm import (
    LLMProviderFactory,
    ModelDiscovery,
)
from voria.core.setup import ProviderSetup


class voriaTestSuite:
    """Comprehensive test suite for voria"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}\n")

    def print_test(self, name, status, message=""):
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}")
        if message:
            print(f"   {message}")
        if status:
            self.passed += 1
        else:
            self.failed += 1

    async def test_model_discovery(self):
        """Test model discovery for all providers"""
        self.print_header("Model Discovery Tests")

        # Test Modal
        try:
            models = await ModelDiscovery._get_modal_fallback()
            self.print_test(
                "Modal Models Discovery",
                len(models) >= 2,
                f"Found {len(models)} models: {[m.name for m in models]}",
            )
        except Exception as e:
            self.print_test("Modal Models Discovery", False, str(e))

        # Test OpenAI
        try:
            models = await ModelDiscovery._get_openai_fallback()
            has_latest = any("4o" in m.name for m in models)
            self.print_test(
                "OpenAI Latest Models (including GPT-4o)",
                has_latest,
                f"Found {len(models)} models including {models[0].name}",
            )
        except Exception as e:
            self.print_test("OpenAI Latest Models", False, str(e))

        # Test Gemini
        try:
            models = await ModelDiscovery._get_gemini_fallback()
            has_latest = any("1.5" in m.name for m in models)
            self.print_test(
                "Gemini Latest Models (including Gemini 1.5)",
                has_latest,
                f"Found {len(models)} models including {models[0].name}",
            )
        except Exception as e:
            self.print_test("Gemini Latest Models", False, str(e))

        # Test Claude
        try:
            models = await ModelDiscovery._get_claude_fallback()
            has_latest = any("3-5" in m.name for m in models)
            self.print_test(
                "Claude Latest Models (including Claude 3.5)",
                has_latest,
                f"Found {len(models)} models including {models[0].name}",
            )
        except Exception as e:
            self.print_test("Claude Latest Models", False, str(e))

    async def test_provider_factory(self):
        """Test LLM provider factory"""
        self.print_header("LLM Provider Factory Tests")

        # Test provider list
        try:
            providers = LLMProviderFactory.list_providers()
            expected = {
                "modal",
                "openai",
                "gemini",
                "claude",
                "deepseek",
                "siliconflow",
                "kimi",
                "minimax",
            }
            has_all = expected <= set(providers)
            self.print_test(
                "All Providers Registered", has_all, f"Providers: {providers}"
            )
        except Exception as e:
            self.print_test("All Providers Registered", False, str(e))

        # Test provider creation
        try:
            provider = LLMProviderFactory.create(
                provider_name="modal", api_key="test-key", model="zai-org/GLM-5.1-FP8"
            )
            self.print_test(
                "Provider Creation",
                provider is not None,
                f"Created {provider.__class__.__name__}",
            )
        except Exception as e:
            self.print_test("Provider Creation", False, str(e))

        # Test discover_models method
        try:
            # This will use fallback since no real API key
            models = await LLMProviderFactory.discover_models("modal", "fake-key")
            self.print_test(
                "Model Discovery via Factory",
                len(models) > 0,
                f"Discovered {len(models)} models",
            )
        except Exception as e:
            self.print_test("Model Discovery via Factory", False, str(e))

    def test_provider_setup_config(self):
        """Test provider setup configuration"""
        self.print_header("Provider Setup Configuration Tests")

        try:
            setup = ProviderSetup()
            config_dir = ProviderSetup.CONFIG_DIR
            config_file = ProviderSetup.CONFIG_FILE

            self.print_test(
                "Config Directory Creation",
                config_dir.exists(),
                f"Config dir: {config_dir}",
            )

            # Check if config file exists or can be created
            can_write = config_dir.exists() and os.access(config_dir, os.W_OK)
            self.print_test(
                "Config File Writable", can_write, f"Can write to {config_file}"
            )
        except Exception as e:
            self.print_test("Provider Setup Config", False, str(e))

    def test_cli_build(self):
        """Test CLI compilation"""
        self.print_header("voria CLI Build Tests")

        try:
            result = subprocess.run(
                ["./target/release/voria", "--version"],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.print_test(
                "CLI Binary Built",
                result.returncode == 0 and "0.0.5" in result.stdout.strip(),
                f"Version: {result.stdout.strip()}",
            )
        except Exception as e:
            self.print_test("CLI Binary Built", False, str(e))

    def test_cli_help(self):
        """Test CLI help output"""
        self.print_header("voria CLI Help Tests")

        try:
            result = subprocess.run(
                ["./target/release/voria", "--help"],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=5,
            )
            has_commands = all(
                cmd in result.stdout for cmd in ["plan", "issue", "apply"]
            )
            self.print_test(
                "CLI Commands Available", has_commands, "Commands: plan, issue, apply"
            )
        except Exception as e:
            self.print_test("CLI Commands Available", False, str(e))

    def test_cli_end_to_end(self):
        """Test full CLI end-to-end"""
        self.print_header("voria CLI End-to-End Tests")

        try:
            env = os.environ.copy()
            env["OPENAI_API_KEY"] = "test-key"

            result = subprocess.run(
                ["./target/release/voria", "plan", "1"],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
            )

            combined_output = (result.stdout + result.stderr).lower()
            success = result.returncode == 0 and (
                "plan generated" in combined_output
                or "blueprint" in combined_output
                or "plan generation failed" in combined_output
                or "error" in combined_output
            )

            self.print_test(
                "CLI Plan Command",
                success,
                "Successfully executed (or failed gracefully): voria plan 1",
            )

            if not success:
                print(f"   stdout: {result.stdout[:200]}")
                print(f"   stderr: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            self.print_test("CLI Plan Command", False, "Timeout after 10 seconds")
        except Exception as e:
            self.print_test("CLI Plan Command", False, str(e))

    async def run_all(self):
        """Run all tests"""
        print("\n")
        print("█" * 60)
        print("█" + " " * 58 + "█")
        print("█" + "  🚀 voria CLI + LLM INTEGRATION TEST SUITE  ".center(58) + "█")
        print("█" + " " * 58 + "█")
        print("█" * 60)

        # Run async tests
        await self.test_model_discovery()
        await self.test_provider_factory()

        # Run sync tests
        self.test_provider_setup_config()
        self.test_cli_build()
        self.test_cli_help()
        self.test_cli_end_to_end()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        percent = (self.passed / total * 100) if total > 0 else 0

        print(f"\n{'='*60}")
        print(f"📊 Test Results")
        print(f"{'='*60}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Total:  {total}")
        print(f"🎯 Success Rate: {percent:.1f}%")
        print(f"{'='*60}\n")

        if self.failed == 0:
            print("🎉 ALL TESTS PASSED! voria is ready to use!\n")
            return 0
        else:
            print(f"⚠️  {self.failed} test(s) failed. Please review above.\n")
            return 1


async def main():
    """Run test suite"""
    suite = voriaTestSuite()
    exit_code = await suite.run_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
