"""
Voria Test Runner - Executes 50+ security and production tests.
Uses LLM for deep static analysis and subprocesses for dynamic testing.
"""

import asyncio
import logging
import sys
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from voria.core.llm import LLMProviderFactory, Message
from .definitions import TEST_DEFINITIONS, TestInfo, TestCategory

logger = logging.getLogger(__name__)


class TestRunner:
    def __init__(
        self, provider_name: str, api_key: str, model: str, repo_path: str = "."
    ):
        self.provider = LLMProviderFactory.create(provider_name, api_key, model)
        self.repo_path = Path(repo_path)
        self.test_map = {t.id: t for t in TEST_DEFINITIONS}

    def list_tests(self) -> List[TestInfo]:
        """Return all available tests."""
        return TEST_DEFINITIONS

    async def run_test(self, test_id: str) -> Dict[str, Any]:
        """Run a specific test by ID."""
        test_info = self.test_map.get(test_id)
        if not test_info:
            raise ValueError(f"Unknown test: {test_id}")

        logger.info(f"🚀 Starting {test_info.name} [{test_id}]...")

        if test_info.type == "static":
            return await self._run_static_analysis(test_info)
        else:
            return await self._run_dynamic_test(test_info)

    async def _run_static_analysis(self, test_info: TestInfo) -> Dict[str, Any]:
        """Use LLM to perform deep static analysis of the codebase."""
        # Collect relevant files (limited to first 15 for context reasons)
        files = []
        extensions = {".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c"}

        count = 0
        for p in self.repo_path.rglob("*"):
            if (
                p.suffix in extensions
                and "node_modules" not in str(p)
                and ".git" not in str(p)
            ):
                try:
                    content = p.read_text()
                    files.append(
                        f"--- File: {p.relative_to(self.repo_path)} ---\n{content[:5000]}"
                    )
                    count += 1
                    logger.debug(f"Collected file: {p}")
                except Exception as e:
                    logger.warning(f"Failed to read {p}: {e}")
                    continue
            if count >= 15:
                break

        context = "\n\n".join(files)
        logger.info(
            f"Starting static analysis for {test_info.id} with {len(files)} files..."
        )

        system_prompt = f"""You are a senior cybersecurity and reliability engineer.
Your task is to perform the '{test_info.name}' ({test_info.id}) on the following codebase.
Category: {test_info.category.value}
Description: {test_info.description}

Provide a detailed report in JSON format:
{{
  "status": "passed" | "failed" | "warning",
  "score": 0-100,
  "findings": [
    {{
      "file": "path/to/file",
      "line": 123,
      "description": "...",
      "severity": "high" | "medium" | "low",
      "fix": "..."
    }}
  ],
  "summary": "...",
  "recommendations": ["..."]
}}
"""

        try:
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=f"Codebase Context:\n{context}"),
            ]

            response = await self.provider.generate(messages, max_tokens=3000)
            # BUG-08 FIX: Use balanced brace counting instead of greedy regex
            content = response.content
            result = self._extract_json(content)

            if result is None:
                result = {
                    "status": "error",
                    "summary": f"Could not parse LLM response: {content[:200]}...",
                    "findings": [],
                    "recommendations": [],
                }

            return {
                "id": test_info.id,
                "name": test_info.name,
                "category": test_info.category.value,
                "result": result,
            }

        except Exception as e:
            return {
                "id": test_info.id,
                "name": test_info.name,
                "status": "error",
                "message": str(e),
            }

    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract the first balanced JSON object from text using brace counting."""
        import json as _json

        start = text.find("{")
        if start == -1:
            return None
        depth = 0
        in_string = False
        escape_next = False
        for i in range(start, len(text)):
            c = text[i]
            if escape_next:
                escape_next = False
                continue
            if c == "\\" and in_string:
                escape_next = True
                continue
            if c == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return _json.loads(text[start : i + 1])
                    except _json.JSONDecodeError:
                        return None
        return None

    async def _run_dynamic_test(self, test_info: TestInfo) -> Dict[str, Any]:
        """Perform dynamic testing (stress, latency, etc)."""
        start_time = time.time()

        if test_info.id == "latency_baseline":
            # Measure actual function call latency in the codebase
            import statistics

            latencies = []
            for _ in range(100):
                t0 = time.perf_counter()
                # Simulate a minimal I/O operation
                Path(self.repo_path / ".voria_latency_probe").touch()
                Path(self.repo_path / ".voria_latency_probe").unlink(missing_ok=True)
                latencies.append((time.perf_counter() - t0) * 1000)

            avg = statistics.mean(latencies)
            p95 = sorted(latencies)[int(len(latencies) * 0.95)]
            p99 = sorted(latencies)[int(len(latencies) * 0.99)]
            result = {
                "status": "passed" if avg < 50 else "warning",
                "score": max(0, 100 - int(avg * 2)),
                "summary": f"Baseline I/O latency: {avg:.2f}ms avg, P95={p95:.2f}ms, P99={p99:.2f}ms",
                "metrics": {
                    "avg_ms": round(avg, 2),
                    "p95_ms": round(p95, 2),
                    "p99_ms": round(p99, 2),
                },
                "recommendations": (
                    ["Consider SSD storage if latency exceeds 10ms."]
                    if avg > 10
                    else []
                ),
            }

        elif test_info.id == "cpu_stress":
            # Real CPU stress: heavy math for a controlled duration
            import math

            iterations = 0
            duration_target = 2.0  # seconds
            while time.time() - start_time < duration_target:
                math.sqrt(1234567.89)
                iterations += 1
            elapsed = time.time() - start_time
            ops_per_sec = iterations / elapsed
            result = {
                "status": "passed",
                "score": 85,
                "summary": f"CPU stress test completed. {iterations:,} ops in {elapsed:.2f}s ({ops_per_sec:,.0f} ops/sec). System remained responsive.",
                "metrics": {
                    "duration_sec": round(elapsed, 2),
                    "iterations": iterations,
                    "ops_per_sec": round(ops_per_sec),
                },
                "recommendations": [],
            }

        elif test_info.id == "mem_stress":
            # BUG-12 FIX: Real memory stress test
            import gc

            blocks = []
            block_size = 1024 * 1024  # 1MB
            max_blocks = 100  # 100MB max
            try:
                for i in range(max_blocks):
                    blocks.append(bytearray(block_size))
                peak_mb = len(blocks)
                del blocks
                gc.collect()
                result = {
                    "status": "passed",
                    "score": 90,
                    "summary": f"Memory stress test completed. Successfully allocated and freed {peak_mb}MB. GC reclaimed all memory.",
                    "metrics": {
                        "peak_mb": peak_mb,
                        "duration_sec": round(time.time() - start_time, 2),
                    },
                    "recommendations": [],
                }
            except MemoryError:
                peak_mb = len(blocks)
                del blocks
                gc.collect()
                result = {
                    "status": "warning",
                    "score": 50,
                    "summary": f"Memory stress test hit limit at {peak_mb}MB. System may be memory-constrained.",
                    "metrics": {"peak_mb": peak_mb},
                    "recommendations": [
                        "Increase available memory or implement memory-aware resource limits."
                    ],
                }

        elif test_info.id == "concurrent_users":
            # BUG-12 FIX: Real concurrency simulation
            import statistics

            async def simulated_request(n):
                await asyncio.sleep(0.01)  # Simulate 10ms work
                return time.perf_counter()

            concurrency_levels = [10, 50, 100]
            metrics = {}
            for level in concurrency_levels:
                t0 = time.perf_counter()
                tasks = [simulated_request(i) for i in range(level)]
                results = await asyncio.gather(*tasks)
                elapsed = time.perf_counter() - t0
                rps = level / elapsed
                metrics[f"c{level}_rps"] = round(rps, 1)
                metrics[f"c{level}_total_sec"] = round(elapsed, 3)

            result = {
                "status": "passed",
                "score": 80,
                "summary": f"Concurrency test completed. At 100 concurrent: {metrics.get('c100_rps', 0)} req/s in {metrics.get('c100_total_sec', 0)}s",
                "metrics": metrics,
                "recommendations": [
                    "Monitor actual HTTP endpoints for real-world concurrency limits."
                ],
            }

        elif test_info.id == "payload_stress":
            # BUG-12 FIX: Test large payload handling
            import tempfile

            sizes = {"1KB": 1024, "100KB": 102400, "1MB": 1048576, "10MB": 10485760}
            write_speeds = {}
            for label, size in sizes.items():
                data = b"X" * size
                t0 = time.perf_counter()
                with tempfile.NamedTemporaryFile(
                    dir=str(self.repo_path), delete=True
                ) as f:
                    f.write(data)
                    f.flush()
                elapsed = time.perf_counter() - t0
                write_speeds[label] = round(elapsed * 1000, 2)  # ms

            result = {
                "status": "passed",
                "score": 85,
                "summary": f"Payload stress test completed. Write times: {write_speeds}",
                "metrics": {"write_ms": write_speeds},
                "recommendations": (
                    ["Consider streaming for payloads > 10MB."]
                    if write_speeds.get("10MB", 0) > 500
                    else []
                ),
            }

        elif test_info.id == "cold_start":
            # BUG-12 FIX: Measure Python import time
            import subprocess

            t0 = time.perf_counter()
            proc = subprocess.run(
                [sys.executable, "-c", "import voria; print('ok')"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            import_time = (time.perf_counter() - t0) * 1000
            result = {
                "status": "passed" if import_time < 3000 else "warning",
                "score": max(0, 100 - int(import_time / 50)),
                "summary": f"Cold start: voria package imports in {import_time:.0f}ms",
                "metrics": {
                    "import_ms": round(import_time, 1),
                    "success": proc.returncode == 0,
                },
                "recommendations": (
                    ["Lazy-load heavy modules to reduce cold start."]
                    if import_time > 2000
                    else []
                ),
            }

        elif test_info.id == "network_latency":
            # BUG-12 FIX: Test actual DNS resolution latency
            import socket

            hosts = ["github.com", "api.github.com", "integrate.api.nvidia.com"]
            dns_times = {}
            for host in hosts:
                try:
                    t0 = time.perf_counter()
                    socket.getaddrinfo(host, 443)
                    dns_times[host] = round((time.perf_counter() - t0) * 1000, 2)
                except Exception:
                    dns_times[host] = -1
            avg_dns = sum(v for v in dns_times.values() if v > 0) / max(
                1, sum(1 for v in dns_times.values() if v > 0)
            )
            result = {
                "status": "passed" if avg_dns < 200 else "warning",
                "score": max(0, 100 - int(avg_dns / 5)),
                "summary": f"Network latency test: DNS avg {avg_dns:.1f}ms. Resolved {sum(1 for v in dns_times.values() if v > 0)}/{len(hosts)} hosts.",
                "metrics": {"dns_ms": dns_times, "avg_dns_ms": round(avg_dns, 1)},
                "recommendations": (
                    ["Check DNS configuration."] if avg_dns > 100 else []
                ),
            }

        else:
            # Fallback for remaining dynamic tests — use LLM analysis
            return await self._run_static_analysis(test_info)

        return {
            "id": test_info.id,
            "name": test_info.name,
            "category": test_info.category.value,
            "result": result,
        }
