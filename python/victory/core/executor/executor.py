"""
Test Executor Module - Run tests and parse results

Supports multiple test frameworks:
- pytest (Python)
- jest (JavaScript/TypeScript)
- go test (Go)
- Custom frameworks
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    """Single test result"""
    name: str
    status: TestStatus
    duration: float = 0.0
    message: str = ""
    error_type: Optional[str] = None
    stacktrace: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Complete test suite result"""
    framework: str
    total: int
    passed: int
    failed: int
    skipped: int
    duration: float
    results: List[TestResult]
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0


class PytestParser:
    """Parse pytest output"""
    
    @staticmethod
    async def run(
        test_dir: str = "tests/",
        repo_path: str = "."
    ) -> TestSuiteResult:
        """Run pytest and parse results"""
        
        import subprocess
        
        repo = Path(repo_path)
        test_path = repo / test_dir
        
        if not test_path.exists():
            logger.warning(f"Test directory not found: {test_path}")
            return TestSuiteResult(
                framework="pytest",
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=0,
                results=[],
                stderr=f"Test directory not found: {test_dir}",
                returncode=-1
            )
        
        try:
            # Run pytest with JSON output
            cmd = [
                "python3", "-m", "pytest",
                str(test_path),
                "-v", "--tb=short",
                "--json-report", "--json-report-file=/tmp/pytest-report.json"
            ]
            
            result = await asyncio.create_subprocess_shell(
                " ".join(cmd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(repo)
            )
            
            stdout, stderr = await result.communicate()
            stdout_str = stdout.decode()
            stderr_str = stderr.decode()
            
            return PytestParser.parse_output(
                stdout_str,
                stderr_str,
                result.returncode
            )
        
        except Exception as e:
            logger.error(f"Pytest execution failed: {e}")
            return TestSuiteResult(
                framework="pytest",
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=0,
                results=[],
                stderr=str(e),
                returncode=-1
            )
    
    @staticmethod
    def parse_output(
        stdout: str,
        stderr: str,
        returncode: int
    ) -> TestSuiteResult:
        """Parse pytest output"""
        
        results = []
        
        # Match pytest summary line: "passed 10 failed 2 skipped 1 in 0.5s"
        summary_match = re.search(
            r"(\d+)\s+passed(?:\s+(\d+)\s+failed)?(?:\s+(\d+)\s+skipped)?(?:\s+in\s+([\d.]+)s)?",
            stdout
        )
        
        passed = int(summary_match.group(1)) if summary_match else 0
        failed = int(summary_match.group(2)) if summary_match and summary_match.group(2) else 0
        skipped = int(summary_match.group(3)) if summary_match and summary_match.group(3) else 0
        duration = float(summary_match.group(4)) if summary_match and summary_match.group(4) else 0.0
        
        # Parse individual test results
        # Match: "test_file.py::test_name PASSED"
        for match in re.finditer(
            r"(\S+::\S+)\s+(PASSED|FAILED|SKIPPED|ERROR)",
            stdout
        ):
            test_name = match.group(1)
            status_str = match.group(2)
            
            status_map = {
                "PASSED": TestStatus.PASSED,
                "FAILED": TestStatus.FAILED,
                "SKIPPED": TestStatus.SKIPPED,
                "ERROR": TestStatus.ERROR
            }
            
            results.append(TestResult(
                name=test_name,
                status=status_map.get(status_str, TestStatus.ERROR)
            ))
        
        return TestSuiteResult(
            framework="pytest",
            total=passed + failed + skipped,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            results=results,
            stdout=stdout,
            stderr=stderr,
            returncode=returncode
        )


class JestParser:
    """Parse jest output"""
    
    @staticmethod
    async def run(
        test_dir: str = "tests/",
        repo_path: str = "."
    ) -> TestSuiteResult:
        """Run jest and parse results"""
        
        import subprocess
        
        repo = Path(repo_path)
        test_path = repo / test_dir
        
        if not test_path.exists():
            logger.warning(f"Test directory not found: {test_path}")
            return TestSuiteResult(
                framework="jest",
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=0,
                results=[],
                stderr=f"Test directory not found: {test_dir}",
                returncode=-1
            )
        
        try:
            # Run jest with JSON output
            cmd = [
                "npx", "jest",
                str(test_path),
                "--json", "--verbose"
            ]
            
            result = await asyncio.create_subprocess_shell(
                " ".join(cmd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(repo)
            )
            
            stdout, stderr = await result.communicate()
            stdout_str = stdout.decode()
            stderr_str = stderr.decode()
            
            return JestParser.parse_output(
                stdout_str,
                stderr_str,
                result.returncode
            )
        
        except Exception as e:
            logger.error(f"Jest execution failed: {e}")
            return TestSuiteResult(
                framework="jest",
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=0,
                results=[],
                stderr=str(e),
                returncode=-1
            )
    
    @staticmethod
    def parse_output(
        stdout: str,
        stderr: str,
        returncode: int
    ) -> TestSuiteResult:
        """Parse jest JSON output"""
        
        results = []
        
        try:
            # Jest outputs JSON
            data = json.loads(stdout)
            
            passed = data.get("numPassedTests", 0)
            failed = data.get("numFailedTests", 0)
            skipped = data.get("numPendingTests", 0)
            duration = data.get("testResults", [{}])[0].get("perfStats", {}).get("end", 0) / 1000.0
            
            # Parse test results
            for test_result in data.get("testResults", []):
                for assertion in test_result.get("assertionResults", []):
                    status_map = {
                        "pass": TestStatus.PASSED,
                        "fail": TestStatus.FAILED,
                        "skip": TestStatus.SKIPPED,
                        "todo": TestStatus.SKIPPED
                    }
                    
                    results.append(TestResult(
                        name=assertion.get("fullName", "unknown"),
                        status=status_map.get(assertion.get("status", "error"), TestStatus.ERROR),
                        duration=assertion.get("duration", 0) / 1000.0,
                        message=assertion.get("failureMessages", [""])[0] if assertion.get("failureMessages") else ""
                    ))
            
        except json.JSONDecodeError:
            # Fallback: parse text output
            passed = len(re.findall(r"✓", stdout))
            failed = len(re.findall(r"✕", stdout))
        
        return TestSuiteResult(
            framework="jest",
            total=passed + failed + skipped,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            results=results,
            stdout=stdout,
            stderr=stderr,
            returncode=returncode
        )


class TestExecutor:
    """Execute tests and parse results"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
    
    async def detect_framework(self) -> Optional[str]:
        """Detect test framework from files"""
        
        repo = self.repo_path
        
        # Check for pytest
        if (repo / "setup.py").exists() or (repo / "pyproject.toml").exists():
            if (repo / "tests").exists() or any(repo.glob("test_*.py")):
                return "pytest"
        
        # Check for jest
        if (repo / "package.json").exists():
            if (repo / "tests").exists() or (repo / "__tests__").exists():
                package_data = json.loads((repo / "package.json").read_text())
                if "jest" in package_data.get("devDependencies", {}):
                    return "jest"
        
        # Check for go tests
        if any(repo.glob("*_test.go")):
            return "go"
        
        return None
    
    async def run_tests(
        self,
        framework: Optional[str] = None,
        test_dir: str = "tests/",
        language: Optional[str] = None
    ) -> TestSuiteResult:
        """
        Run tests with specified framework
        
        Args:
            framework: Test framework (pytest, jest, go, or auto-detect)
            test_dir: Directory containing tests
            language: Programming language (python, javascript, go)
            
        Returns:
            TestSuiteResult with all test results
        """
        
        # Auto-detect if not specified
        if not framework:
            framework = await self.detect_framework()
            logger.info(f"Detected framework: {framework}")
        
        if not framework:
            return TestSuiteResult(
                framework="unknown",
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=0,
                results=[],
                stderr="Could not detect test framework",
                returncode=-1
            )
        
        framework = framework.lower()
        
        if framework == "pytest":
            return await PytestParser.run(test_dir, str(self.repo_path))
        elif framework == "jest":
            return await JestParser.run(test_dir, str(self.repo_path))
        else:
            return TestSuiteResult(
                framework=framework,
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=0,
                results=[],
                stderr=f"Unsupported framework: {framework}",
                returncode=-1
            )
    
    def format_results(self, result: TestSuiteResult) -> str:
        """Format test results as string"""
        
        status_emoji = "✅" if result.failed == 0 else "❌"
        
        summary = f"""{status_emoji} {result.framework} Results:
  Total: {result.total}
  Passed: {result.passed}
  Failed: {result.failed}
  Skipped: {result.skipped}
  Duration: {result.duration:.2f}s
"""
        
        if result.failed > 0:
            summary += f"\nFailed Tests:\n"
            for test in result.results:
                if test.status == TestStatus.FAILED:
                    summary += f"  ❌ {test.name}\n"
                    if test.message:
                        summary += f"     {test.message[:100]}\n"
        
        return summary


async def test_executor():
    """Test the test executor"""
    
    executor = TestExecutor("/home/ansh/victory")
    
    # Detect framework
    framework = await executor.detect_framework()
    print(f"Detected framework: {framework}")
    
    # Run tests (this would fail without pytest installed, but shows the flow)
    if framework == "pytest":
        result = await executor.run_tests(framework="pytest")
        print(executor.format_results(result))


if __name__ == "__main__":
    asyncio.run(test_executor())
