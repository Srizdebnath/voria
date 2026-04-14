"""
Definitions for 50+ different types of testing supported by voria.
Combines security (pentesting) and production/reliability tests.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional

class TestCategory(Enum):
    SECURITY = "Security (Pentesting)"
    PRODUCTION = "Production & Reliability"
    PERFORMANCE = "Performance & Latency"
    STRESS = "Stress Testing"
    QUALITY = "Code Quality & Compliance"

@dataclass
class TestInfo:
    id: str
    name: str
    category: TestCategory
    description: str
    impact: str  # High, Medium, Low
    type: str  # "static" (code analysis) or "dynamic" (runtime)

# The master list of all 52 tests
TEST_DEFINITIONS: List[TestInfo] = [
    # --- SECURITY (25 tests) ---
    TestInfo("sql_injection", "SQL Injection Scan", TestCategory.SECURITY, "Checks for improper sanitization of database queries.", "Critical", "static"),
    TestInfo("xss", "Cross-Site Scripting (XSS)", TestCategory.SECURITY, "Checks for reflected or stored XSS vulnerabilities in web code.", "High", "static"),
    TestInfo("csrf", "CSRF Protection Audit", TestCategory.SECURITY, "Verifies presence of CSRF tokens in state-changing requests.", "High", "static"),
    TestInfo("path_traversal", "Path Traversal Probe", TestCategory.SECURITY, "Detects insecure file path handling that could allow unauthorized access.", "High", "static"),
    TestInfo("insecure_deserialization", "Insecure Deserialization", TestCategory.SECURITY, "Identifies unsafe decoding of serialized data.", "Critical", "static"),
    TestInfo("hardcoded_secrets", "Hardcoded Secret Detection", TestCategory.SECURITY, "Scans codebase for API keys, passwords, and private certificates.", "Critical", "static"),
    TestInfo("insecure_jwt", "Insecure JWT Handling", TestCategory.SECURITY, "Checks for weak JWT algorithms or lack of signature verification.", "High", "static"),
    TestInfo("broken_access_control", "Broken Access Control", TestCategory.SECURITY, "Analyzes authorization logic for potential bypasses.", "High", "static"),
    TestInfo("open_redirect", "Open Redirect Audit", TestCategory.SECURITY, "Checks for unsafe user-controlled redirection URLs.", "Medium", "static"),
    TestInfo("security_headers", "Security Headers Audit", TestCategory.SECURITY, "Verifies presence of CSP, HSTS, and X-Content-Type headers.", "Medium", "static"),
    TestInfo("clickjacking", "Clickjacking Vulnerability", TestCategory.SECURITY, "Checks for X-Frame-Options or suitable CSP directives.", "Low", "static"),
    TestInfo("bruteforce_protection", "Bruteforce Protection", TestCategory.SECURITY, "Identifies lack of rate limiting or account lockout logic.", "Medium", "static"),
    TestInfo("weak_crypto", "Weak Cryptography", TestCategory.SECURITY, "Detects use of MD5, SHA1, or other deprecated algorithms.", "High", "static"),
    TestInfo("sensitive_data_exposure", "Sensitive Data Exposure", TestCategory.SECURITY, "Checks for PII or sensitive info leaked in logs or error messages.", "High", "static"),
    TestInfo("xxe", "XML External Entity (XXE)", TestCategory.SECURITY, "Checks for insecure XML parsers allowed to resolve external entities.", "High", "static"),
    TestInfo("insecure_upload", "Insecure File Upload", TestCategory.SECURITY, "Analyzes file upload handling for potential malicious file execution.", "High", "static"),
    TestInfo("command_injection", "Command Injection Scan", TestCategory.SECURITY, "Checks for shell commands built using untrusted user input.", "Critical", "static"),
    TestInfo("directory_listing", "Directory Listing Probe", TestCategory.SECURITY, "Checks web config for inadvertent directory listing enablement.", "Medium", "static"),
    TestInfo("ssrf", "Server-Side Request Forgery", TestCategory.SECURITY, "Detects code that makes requests to user-controlled internal URLs.", "High", "static"),
    TestInfo("session_management", "Improper Session Management", TestCategory.SECURITY, "Analyzes session lifecycle, fixation, and timeout logic.", "Medium", "static"),
    TestInfo("rate_limiting", "Lack of Rate Limiting", TestCategory.SECURITY, "Checks for API endpoints vulnerable to abuse without throttling.", "Medium", "static"),
    TestInfo("info_leakage", "Information Leakage Scan", TestCategory.SECURITY, "Detects server versions or stack traces exposed to end users.", "Low", "static"),
    TestInfo("vulnerable_components", "Known Vulnerable Components", TestCategory.SECURITY, "Audit dependencies against known vulnerability databases.", "High", "static"),
    TestInfo("integrity_checks", "Lack of Integrity Checks", TestCategory.SECURITY, "Checks if downloaded assets or code lack checksum verification.", "Medium", "static"),
    TestInfo("error_handling_leak", "Error Handling Leakage", TestCategory.SECURITY, "Verifies that catch blocks don't expose system internals.", "Low", "static"),

    # --- PRODUCTION & RELIABILITY (10 tests) ---
    TestInfo("latency_baseline", "Latency Baseline Audit", TestCategory.PRODUCTION, "Establishes baseline response times for core functions.", "Medium", "dynamic"),
    TestInfo("deadlock_detection", "Potential Deadlock Scan", TestCategory.PRODUCTION, "Analyzes lock acquisition order for potential circular dependencies.", "High", "static"),
    TestInfo("race_condition", "Race Condition Check", TestCategory.PRODUCTION, "Identifies non-atomic operations on shared state.", "High", "static"),
    TestInfo("unhandled_exceptions", "Unhandled Exception Scan", TestCategory.PRODUCTION, "Checks for paths where exceptions could crash the process.", "High", "static"),
    TestInfo("memory_leak_static", "Memory Leak static Scan", TestCategory.PRODUCTION, "Identifies patterns like growing collections or unclosed resources.", "Medium", "static"),
    TestInfo("connection_exhaustion", "Conn Pool Exhaustion Probe", TestCategory.PRODUCTION, "Analyzes resource cleanup to prevent pool starvation.", "High", "static"),
    TestInfo("slow_query", "Slow Query Detection", TestCategory.PRODUCTION, "Scans for unoptimized DB queries without indices.", "Medium", "static"),
    TestInfo("cache_consistency", "Cache Inconsistency Scan", TestCategory.PRODUCTION, "Checks for missing cache invalidation after updates.", "Medium", "static"),
    TestInfo("timeout_handling", "Missing Timeout Logic", TestCategory.PRODUCTION, "Detects blocking calls without explicit timeouts.", "Medium", "static"),
    TestInfo("circular_dep", "Circular Dependency Audit", TestCategory.PRODUCTION, "Maps module imports for circularities that impair startup.", "Low", "static"),

    # --- PERFORMANCE & STRESS (10 tests) ---
    TestInfo("cpu_stress", "CPU Stress Resilience", TestCategory.STRESS, "Simulates heavy computational load to test stability.", "Medium", "dynamic"),
    TestInfo("mem_stress", "Memory Stress Resilience", TestCategory.STRESS, "Simulates high memory allocation to test GC and OOM handling.", "Medium", "dynamic"),
    TestInfo("concurrent_users", "High Concurrency Simulation", TestCategory.STRESS, "Simulates massive parallel user requests.", "High", "dynamic"),
    TestInfo("payload_stress", "Large Payload Resilience", TestCategory.STRESS, "Tests handling of extremely large input data.", "Medium", "dynamic"),
    TestInfo("network_latency", "Network Latency Simulation", TestCategory.PERFORMANCE, "Simulates slow network conditions (jitter/latency).", "Low", "dynamic"),
    TestInfo("p99_latency", "P99 Latency Audit", TestCategory.PERFORMANCE, "Measures tail latency under normal load.", "Medium", "dynamic"),
    TestInfo("throughput_max", "Max Throughput Benchmark", TestCategory.PERFORMANCE, "Determines the saturation point of the service.", "Medium", "dynamic"),
    TestInfo("bundle_size", "Asset Bundle Size Audit", TestCategory.PERFORMANCE, "Analyzes production assets for excessive size.", "Low", "static"),
    TestInfo("cold_start", "Cold Start Analysis", TestCategory.PERFORMANCE, "Measures startup time and initialization performance.", "Low", "dynamic"),
    TestInfo("db_index_audit", "DB Index Optimization", TestCategory.PERFORMANCE, "Suggests missing indices based on query patterns.", "Medium", "static"),

    # --- QUALITY & COMPLIANCE (7 tests) ---
    TestInfo("license_compliance", "License Compliance Audit", TestCategory.QUALITY, "Checks dependencies for copyleft or restrictive licenses.", "Medium", "static"),
    TestInfo("dep_graph", "Dependency Health Audit", TestCategory.QUALITY, "Analyzes depth and variety of project dependencies.", "Low", "static"),
    TestInfo("doc_completeness", "Documentation Completeness", TestCategory.QUALITY, "Checks for missing docstrings or exported API docs.", "Low", "static"),
    TestInfo("coverage_gap", "Test Coverage Gap Analysis", TestCategory.QUALITY, "Identifies critical paths missing automated tests.", "Medium", "static"),
    TestInfo("lint_security", "Security-focused Linting", TestCategory.QUALITY, "Runs specialized security linter rules.", "Medium", "static"),
    TestInfo("complexity_drift", "Complexity Drift Scan", TestCategory.QUALITY, "Detects increasing cyclomatic complexity over time.", "Low", "static"),
    TestInfo("redundant_calls", "Redundant API Call Detection", TestCategory.QUALITY, "Identifies duplicate data fetching patterns.", "Low", "static"),
]
